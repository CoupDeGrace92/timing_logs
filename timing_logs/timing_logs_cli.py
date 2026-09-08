import argparse
import pickle
from pathlib import Path

from data_structures import timed_events


def load_tracker(path: str) -> timed_events:
    with open(path, "rb") as file:
        events = []
        try:
            events = pickle.load(file)
        except FileNotFoundError:
            print(f"File not found: {path}")
        except EOFError:
            print(f"Timing log at {path} is empty or corrupted")
        except Exception as e:
            print(f"Unexpected error occured: {type(e).__name__} - {e}")
    tracker = timed_events()
    tracker.events = events
    return tracker


def main():
    parser = argparse.ArgumentParser(description="Timing Logs CLI")
    subparser = parser.add_subparsers(dest="command")

    view_parser = subparser.add_parser("view", help="View events in the order they occured")
    sort_parser = subparser.add_parser("sort", help="View events sorted by elapsed time")
    max_parser = subparser.add_parser("max", help="Show the single slowest event")

    for p in (view_parser, sort_parser, max_parser):
        p.add_argument("--leaves", action="store_true", help="Operate on leaf events only")
        p.add_argument("--file", default="cache/timing_logs.pkl", help="Path to timing log pickle")

    args = parser.parse_args()

    match args.command:
        case "view":
            tracker = load_tracker(args.file)
            tracker.view_in_order()
        case "sort":
            tracker = load_tracker(args.file)
            if args.leaves == True:
                tracker.sort_leaf_nodes()
            else:
                tracker.sort_roots()
        case "max": 
            tracker = load_tracker(args.file)
            if args.leaves == True:
                tracker.max_leaf()
            else:
                tracker.max_root()
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()