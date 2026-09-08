import copy, time, pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self
from contextlib import contextmanager

#Helper to pin down performance problems
#NOTE: ANYTHING THAT OPERATES IN PARALLEL (e.g. multithreading) WILL REQUIRE EVENT LOGS PER THREAD THAT ARE MERGED WHEN ALL THREADS ARE DONE
#IN THIS CASE, once all threads are done, append the root timing events together either in a new log, or in one of the sub-logs

@dataclass
class TimingEvent:
    label: str
    start: float
    elapsed: float

    parent: "TimingEvent | None" = None
    children: list["TimingEvent"] = field(default_factory=list)

class timed_events:
    def __init__(self, events=[]):
        self.events: list[TimingEvent] = events
        self._stack: list[TimingEvent] = []

    def add_event(self: Self, event: TimingEvent):
        self.events.append(event)

    #Method flattens out the tree into a list of leaf nodes
    def all_leaves(self) -> list[TimingEvent]:
        leaves = []
        for root in self.events:
            leaves.extend(collect_leaves(root))
        return leaves

    def view_in_order(self):
        print("\nEVENT TIMES IN ORDER:")
        c = copy.deepcopy(self.events)
        c.sort(key=lambda t: t.start)
        for event in c:
            _print_event(event)

    def max_root(self):
        max = TimingEvent("No events present", 0, 0)
        for event in self.events:
            if event.elapsed > max.elapsed:
                max = event

        if max.start == 0:
            print("No timed events to compare")
        else:
            print("LONGEST TIMED EVENT:")
            _print_event(max)

    def sort_roots(self):
        print("\nSORTED EVENT TIMES:")
        c = copy.deepcopy(self.events)
        c.sort(key=lambda t: t.elapsed)

        #Alternatively if we want strict type hinting:
        '''
        def by_elapsed(t: TimingEvent) -> float:
            return t.elapsed

        c.sort(key=by_elapsed)
        '''
        for event in c:
            _print_event(event)

    def max_leaf(self):
        l_nodes = self.all_leaves()
        max = TimingEvent("No events present", 0, 0)
        for event in l_nodes:
            if event.elapsed > max.elapsed:
                max = event

        if max.start == 0:
            print("No timed events to compare")
        else:
            print(f"LONGEST TIMED EVENT:")
            _print_event(max)

    def sort_leaf_nodes(self):
        l_nodes = self.all_leaves()
        l_nodes.sort(key=lambda t: t.elapsed)
        for event in l_nodes:
            _print_event(event)


    def dump_logs(self, fp: str="./cache/timing_logs.pkl"):

        f = Path(fp)
        f.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(f, "wb") as file:
                pickle.dump(self.events, file)
        except Exception as e:
            print(f"Error writing to cache: {type(e).__name__} - {e}")

@contextmanager
def timed(label: str, tracker: timed_events):
    parent = tracker._stack[-1] if tracker._stack else None
    event = TimingEvent(label=label, start=time.perf_counter(), elapsed=0.0, parent=parent)

    if parent is not None:
        parent.children.append(event)
    else:
        tracker.events.append(event)

    tracker._stack.append(event)
    yield
    tracker._stack.pop()
    event.elapsed = time.perf_counter() - event.start
'''
USAGE:
with timed("load_movies", event_log):
    movies = load_movies(fp)

Use a with loop to wrap the portions of the function we want timed
Make sure the event log has been initialized
'''

def _print_event(event: TimingEvent, depth: int=0):
    indent = "  " * depth
    print(f"{indent}{event.label}: {event.elapsed: .4f}s")
    for child in event.children:
        _print_event(child, depth + 1)

def collect_leaves(event: TimingEvent) -> list[TimingEvent]:
    if not event.children:
        return [event]

    leaves = []
    for child in event.children:
        leaves.extend(collect_leaves(child))

    return leaves

#Create a global event log that can be used by all modules:
event_log = timed_events()