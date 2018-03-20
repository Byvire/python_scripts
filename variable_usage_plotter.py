#!/usr/bin/env python3
import argparse
from collections import OrderedDict, namedtuple
import enum
import re
import sys

_varname = r"\b[a-zA-Z_][\w_]*\b"
_assignment = re.compile(r"^\s*({varname})(\s*,\s*{varname})*\s*=[^=].*$"
                         .format(varname=_varname))

def vars_assigned_in_line(line):
    # Can be fooled by keyword argument passing
    m = _assignment.match(line)
    if m:
        name = m.group(1)
        if not m.group(2):
            return (name,)
        [*rest] = [var.strip() for var in m.group(2).split(",")]
        rest.append(name)
        return rest
        # return (name,) + tuple(rest)
    return ()

def assignments_by_line(lines):
    # TODO make this better by avoiding catching keyword arguments
    asgns_by_line = []
    parens_open = 0
    passing_kwargs = False
    for line in lines:
        if not passing_kwargs:
            asgns_by_line.append(vars_assigned_in_line(line))
        else:
            asgns_by_line.append(())
        line = line.strip()
        passing_kwargs = line.endswith(",") or line.endswith("(")
    return asgns_by_line

class VarStatus(enum.Enum):
    # in a given line, was the variable...
    undefined = 1
    assigned = 2
    unused = 3
    used = 4
    used_and_assigned = 5
    unused_forevermore = 6  # could split this into in-scope and out-of-scope, but whatever

VarEvent = namedtuple("VarEvent", ("line_num", "status"))

class WordFinder:
    def __init__(self):
        self.word_patterns = []

    def find_words(self, line):
        found = []
        for wp in self.word_patterns:
            m = wp.search(line)
            if m:
                found.append(m.group(0))
        return found

    def add_word(self, w):
        self.word_patterns.append(re.compile(f"\\b{w}\\b"))
        
def get_sparse_variable_events(lines):
    asgns = assignments_by_line(lines)
    events = OrderedDict()
    finder = WordFinder()
    for index, (asgned_vars, line) in enumerate(zip(asgns, lines)):
        if asgned_vars:
            # Let's not process the left-hand side again
            _, line = line.split("=", maxsplit=1)
        for var in finder.find_words(line):
            if var in asgned_vars:
                events[var].append(VarEvent(index, VarStatus.used_and_assigned))
            else:
                events[var].append(VarEvent(index, VarStatus.used))
        for var in asgned_vars:
            if var not in events:
                events[var] = []
                finder.add_word(var)
            if not events[var] or events[var][-1][0] is not index:
                events[var].append(VarEvent(index, VarStatus.assigned))
    return events

def make_dense_status_list(event_list, num_lines):
    event_list = event_list[::-1]  # so we can pop the earliest event
    all_events = []
    defined_yet = False
    for line_num in range(num_lines):
        if not event_list:
            all_events.append(VarStatus.unused_forevermore)
        elif not defined_yet and line_num < event_list[-1].line_num:
            all_events.append(VarStatus.undefined)
        elif line_num < event_list[-1].line_num:
            all_events.append(VarStatus.unused)
        else:  #if line_num == event_list[-1].line_num:
            all_events.append(event_list.pop().status)
            defined_yet = True
    return all_events

def dense_events_for_all(events, num_lines):
    return OrderedDict((name, make_dense_status_list(event_list, num_lines))
                       for name, event_list in events.items())

def print_events_vertical(events, event_to_char):
    # events is an OrderedDict of lists of statuses of events for var names
    num_lines = len(next(iter(events.values())))  # makes me cringe
    col_width = 3
    def print_col(c, width=col_width):
        print(c, end=" "*(width - len(c)))

    def print_event(event):
        print_col(event_to_char[event])

    left_margin_len = len(str(num_lines)) + 2

    # Label the columns, somewhat haphazardly
    for ix, varname in enumerate(events):
        print(" " * left_margin_len, end="")
        for _ in range(ix):
            print_col(":")
        print(varname)
    print("-" * (len(events) * col_width + left_margin_len))
    # now do the rows!
    for line_num in range(num_lines):
        print_col(str(line_num), width=left_margin_len)
        for _, event_list in events.items():  # this is why it's an OrderedDict
            print_event(event_list[line_num])
        print("")

def text_and_display_key_from_args():
    display_key = {
        VarStatus.undefined: "",
        VarStatus.assigned: "=",
        VarStatus.unused: ":",
        VarStatus.used: "#",
        VarStatus.used_and_assigned: "%",
        VarStatus.unused_forevermore: "",
    }
    parser = argparse.ArgumentParser(
        description="""
Track the use of variables assigned by the = operator in python files.""".strip(),
        epilog=("Each column tracks one variable.  The key (currently not user"
                + " defined) is " +
                "".join("\n    {} means {}".format(val, key.name)
                        for key, val in display_key.items())
                + """

This is most useful if you feed it an single, long function with lots of
variable assignments, because then it's easy to see the seams in the logic
where the function can be split up.  (But it's still just a toy.)"""),
                formatter_class=argparse.RawDescriptionHelpFormatter)
    


    parser.add_argument("infile", type=argparse.FileType("r"), help="Input file with code to analyze")
    args = parser.parse_args()
    return args.infile.read(), display_key

def main():
    text, display_key = text_and_display_key_from_args()
    lines = text.split("\n")
    events = get_sparse_variable_events(lines)
    if not events:
        print("Nothing to show!", file=sys.stderr)
        return 1
    print_events_vertical(dense_events_for_all(events, len(lines)),
                          display_key)

if __name__ == "__main__":
    main()
    
