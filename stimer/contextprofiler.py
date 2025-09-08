# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:24:59 2025

@author: Simon.Kern
"""

import sys
import time
import inspect
import linecache
from collections import defaultdict

class _ProfilerImpl:
    """
    Internal implementation of the line profiler.

    This class contains the core logic for tracing, timing, and reporting.
    Users interact with the `ContextProfiler` instance created at the module level.
    """
    def __init__(self):
        self._reset()

    def _reset(self):
        """Resets the profiler's state to allow for multiple runs."""
        self._timings = defaultdict(float)
        self._lines = {}
        self._start_time = 0
        self._last_time = 0
        self._target_frame = None
        self._entry_lineno = -1  # Line number of the 'with' statement
        self._last_lineno = -1

    def __enter__(self):
        """Starts the profiling, gets the target frame, and sets the trace."""
        # Reset state for this run, crucial for the shared instance
        self._reset()

        # Get the frame of the code executing the 'with' statement
        self._target_frame = inspect.currentframe().f_back
        self._entry_lineno = self._target_frame.f_lineno

        self._start_time = time.perf_counter()
        self._last_time = self._start_time
        self._last_lineno = self._entry_lineno

        # Set the tracing function for the target frame
        self._target_frame.f_trace = self._trace_function
        sys.settrace(self._trace_function)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stops profiling, calculates final timing, and prints results."""
        # Unset tracing
        sys.settrace(None)
        if self._target_frame:
            self._target_frame.f_trace = None

        # Calculate time for the very last line executed in the block
        final_time = time.perf_counter()
        self._record_timing(self._last_lineno, final_time)

        self._print_results()

        # Clear references to frames to prevent circular references
        self._target_frame = None

        # Do not suppress exceptions
        return False

    def _trace_function(self, frame, event, arg):
        """
        The core tracing function called for each line of executed code.
        """
        # We only care about 'line' events in our target frame
        if event == 'line' and frame is self._target_frame:
            current_time = time.perf_counter()

            # The time elapsed since the last trace is the execution
            # time of the *previous* line.
            self._record_timing(self._last_lineno, current_time)

            # Update state for the next line
            self._last_time = current_time
            self._last_lineno = frame.f_lineno

        return self._trace_function

    def _record_timing(self, lineno, end_time):
        """Stores the execution time for a given line, ignoring the 'with' line."""
        # CRITICAL: Do not record any timing for the 'with' statement itself.
        if lineno == self._entry_lineno:
            return

        elapsed = end_time - self._last_time
        self._timings[lineno] += elapsed

        # Cache the line's source code if we haven't seen it before
        if lineno not in self._lines:
            filename = self._target_frame.f_code.co_filename
            self._lines[lineno] = linecache.getline(filename, lineno).strip()

    def _print_results(self):
        """Formats and prints the profiling results with aligned columns."""
        if not self._timings:
            print("No lines were profiled in the block.")
            return

        total_time = sum(self._timings.values())
        sorted_linenos = sorted(self._timings.keys())

        # Determine field widths
        max_lineno_width = len(str(max(sorted_linenos))) if sorted_linenos else 0
        max_time_width = 7  # fixed for "%.4f"
        max_pct_width = 5   # fixed for "%.1f"

        print("-" * 80)
        print("Line-by-Line Profile:")
        print("-" * 80)

        for lineno in sorted_linenos:
            line_time = self._timings[lineno]
            percentage = (line_time / total_time) * 100 if total_time > 0 else 0
            line_text = self._lines.get(lineno, "")

            # Format: %LINENUMBER %PERCENTAGE %TIME %LINECONTENT
            print(
                # f"{lineno:0{max_lineno_width}d}  "
                f"{percentage:04.1f}% "
                f"{line_time:07.4f}s | "
                f"{line_text}"
            )

        print("-" * 80)
        print(f"Total time: {total_time:.4f}s")
        print("-" * 80)

    def __call__(self):
        """
        Allows creating a new, independent profiler instance via `ContextProfiler()`.
        """
        return _ProfilerImpl()

# Create a single, callable instance that acts as the entry point for the module.
# This allows for both 'with ContextProfiler:' and 'with ContextProfiler():' syntax.
ContextProfiler = _ProfilerImpl()
