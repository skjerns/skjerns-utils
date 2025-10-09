# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:24:59 2025

@author: Simon.Kern
"""

import os
import sys
import time
import inspect
import linecache
from collections import defaultdict

RESET = "\033[0m"


def _supports_color():
    """Returns True if ANSI color is likely supported."""
    if os.environ.get("NO_COLOR"):
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def _white_to_red_rgb(pct):
    """Maps 0-100 pct to RGB from white to red."""
    t = max(0.0, min(1.0, pct / 100.0))
    r = 255
    g = int(round(255 * (1.0 - t)))
    b = int(round(255 * (1.0 - t)))
    return r, g, b


def _rgb_fg_ansi(r, g, b):
    """Returns ANSI escape for 24-bit RGB foreground."""
    return f"\033[38;2;{r};{g};{b}m"


class _ProfilerImpl:
    """
    Internal implementation of the line profiler.

    Traces a single frame entered via context manager and reports line timings.
    """
    def __init__(self):
        self._reset()
        self._use_color = _supports_color()

    def _reset(self):
        """Resets the profiler's state to allow for multiple runs."""
        self._timings = defaultdict(float)
        self._lines = {}
        self._start_time = 0
        self._last_time = 0
        self._target_frame = None
        self._entry_lineno = -1
        self._last_lineno = -1

    def __enter__(self):
        """Starts the profiling, gets the target frame, and sets the trace."""
        self._reset()
        self._target_frame = inspect.currentframe().f_back
        self._entry_lineno = self._target_frame.f_lineno
        self._start_time = time.perf_counter()
        self._last_time = self._start_time
        self._last_lineno = self._entry_lineno
        self._target_frame.f_trace = self._trace_function
        sys.settrace(self._trace_function)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stops profiling, finalizes timing, and prints results."""
        sys.settrace(None)
        if self._target_frame:
            self._target_frame.f_trace = None
        final_time = time.perf_counter()
        self._record_timing(self._last_lineno, final_time)
        self._print_results()
        self._target_frame = None
        return False

    def _trace_function(self, frame, event, arg):
        """Tracing callback for each executed line in the target frame."""
        if event == 'line' and frame is self._target_frame:
            current_time = time.perf_counter()
            self._record_timing(self._last_lineno, current_time)
            self._last_time = current_time
            self._last_lineno = frame.f_lineno
        return self._trace_function

    def _record_timing(self, lineno, end_time):
        """Stores execution time for a line, ignoring the 'with' line."""
        if lineno == self._entry_lineno:
            return
        elapsed = end_time - self._last_time
        self._timings[lineno] += elapsed
        if lineno not in self._lines:
            filename = self._target_frame.f_code.co_filename
            self._lines[lineno] = linecache.getline(filename, lineno).rstrip("\n")

    def _fmt_line(self, percentage, line_time, line_text):
        """Formats a single output line with optional color."""
        pct_str = f"{percentage:04.1f}%"
        time_str = f"{line_time:07.3f}s"
        line_text = line_text.replace('  ', ' ')
        base = f"{pct_str} {time_str} | {line_text.rstrip()}"
        if not self._use_color:
            return base
        r, g, b = _white_to_red_rgb(percentage)
        return f"{_rgb_fg_ansi(r, g, b)}{base}{RESET}"

    def _print_results(self):
        """Prints results sorted by descending percentage with color mapping."""
        if not self._timings:
            print("No lines were profiled in the block.")
            return

        total_time = sum(self._timings.values())
        rows = []
        for lineno, line_time in self._timings.items():
            pct = (line_time / total_time) * 100 if total_time > 0 else 0.0
            rows.append((pct, line_time, self._lines.get(lineno, "")))

        #rows.sort(key=lambda x: x[0], reverse=True)

        print("-" * 80)
        print("Line-by-Line Profile")
        print("-" * 80)
        for pct, line_time, text in rows:
            print(self._fmt_line(pct, line_time, text))
        print("-" * 80)
        print(f"Total time: {total_time:.4f}s")
        print("-" * 80)

    def __call__(self):
        """Returns a fresh independent profiler instance."""
        return _ProfilerImpl()


# Shared, callable instance for 'with ContextProfiler:' and 'with ContextProfiler():'
ContextProfiler = _ProfilerImpl()
