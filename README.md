# Timing Logs
One of a series of small debugging tools I have used in multiple projects, timing logs
creates a wrapper function that logs individual events inside a program and uses pickle
to log them.  Then, those logs can be retrieved and examined with CLI commands.  It was made
to be as unobtrusive as possible (just wrap pieces of code with the timing function) and to 
be more targetted than full stack traces for when you have specific hunches.

## Setup
Since I generally work with uv as my Python package manager, this setup will be for that environment.
If you use some other package manager or setup, install the package as you would any other package 
in it.

For installation directly from github:
```bash
uv add git+https://github.com/CoupDeGrace92/timing_logs
```

or for local development:
```bash
git clone https://github.com/CoupDeGrace92/timing_logs
cd timing_logs
uv sync
```

uv add will install the tools as a dependency into an existing uv-managed project allowing devs to use
its command line functionality.  If instead you would like to use it as a global command line tool:

```bash
uv tool install git+https://github.com/CoupDeGrace92/timing_logs
```

## Usage within Python code
To use the files within python code, at the top level of a file you want some sort of timing in:
```Python
from timing_logs.data_structures import event_log, timed
```

This will import the generic event log and the timed decorator.  Instead of using the generic global event log,
you could instead import the timed_events class itself and initialize your own local/global log:

```Python
from timing_logs.data_structures import timed_events, timed
```

This would allow you to create multiple log dumps if desired, dumping them to seperate pickle files.  To time an event:

```Python
with timed("NAME THE EVENT", event_log):
    foo(...)
```

replacing event_log with the name of your log if you instead chose to import the timed_events class and initialize your own.
Now, once desired events are timed, include a dump command for each log:
```Python
event_logs.dump_logs()
```

dump_logs takes an optional file path for the desired dump location.  The default is: ./cache/timing_logs.pkl
This can be updated to reflect the shape of your project.  For example:
```Python
event_logs.dump_logs("./logs/temp/timing.pkl")
```

If that is the case, remember to specify the --file option when running the CLI commands to point the script to the 
correct filepath.


Note that timing events, by design can be nested - since the event logs import should be global, each event will 
be appended and will have appropriate relationships on the timing log stack (i.e. nested events will be connected
to both parent and children events). 

**IMPORTANT NOTE:** The nesting structure of the timing logs only works when the program is not operating in parralel,
only sequential tasks can accurately use this nesting feature.  Thus any multi-threading should be careful when
using this timing log or consider using a different tool.

## Command Line Commands
Once the logs have been dumped, the command line tool has a couple of commands:

1. view
The view command allows users to view all timed events in the order they occured
```bash
uv run timing-logs view
```

The sort command allows users to view all timed events in order from longest running process to shortest.  Without
the --leaves option, it does not distinguish between events nested within each other.  Thus is process B was a process within
process A and process B took 5 seconds and A took 10, both would be reported even though 5 of those 10 seconds of process A
were specifically in process B, so the unique time would have been the other 5.  The --leaves command sorts the lowest level
logged nodes instead.
```bash
uv run timing-logs sort
```

The max command reports the timing event that took the longest.  --leaves restricts the timing event to the leave nodes only
(nodes that do not have children).
```bash
uv run timing-logs max
```

To direct the timing-logs commands at a non-default filepath, the --filepath option must be specified:
```bash
uv run timing-logs view --filepath "./logs/temp/timing.pkl"
```

where "./logs/temp/timing.pkl" can be replaced with your filepath.