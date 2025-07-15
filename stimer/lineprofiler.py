# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:24:59 2025

@author: Simon.Kern
"""

# line_profiler.py
import inspect
import linecache
import os
import sys
import time
from collections import OrderedDict, defaultdict
from typing import Callable, DefaultDict, Tuple


class LineProfiler:
    """
    Context-manager wall-clock line profiler.

        from line_profiler import LineProfiler

        with LineProfiler():          # or: with LineProfiler(skip_internal=False):
            ...
    """

    def __init__(
        self,
        *,
        stream=None,
        clock: Callable[[], float] = time.perf_counter,
        skip_internal: bool = True,
    ):
        self._clock = clock
        self._stream = stream or sys.stdout
        self._skip_internal = skip_internal

        self._timings: DefaultDict[Tuple[str, int], float] = defaultdict(float)
        self._order: "OrderedDict[Tuple[str, int], int]" = OrderedDict()
        self._last_key: Tuple[str, int] | None = None
        self._last_time: float | None = None

        # absolute, normalised path of this file so we can ignore our own lines
        self._profiler_file = os.path.normcase(__file__)

    # ───────────────────────────────── context manager ─────────────────────────
    def __enter__(self):
        # attach tracer to *current* and *all ancestor* frames
        frame = inspect.currentframe().f_back
        while frame:
            frame.f_trace = self._trace
            frame = frame.f_back

        sys.settrace(self._trace)          # future frames
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop_timing(self._clock())   # final slice
        sys.settrace(None)                 # stop tracing
        self._report()
        return False                       # propagate any exception

    # ─────────────────────────────────── tracer ────────────────────────────────
    def _trace(self, frame, event, arg):
        if event != "line":
            return self._trace

        filename = os.path.normcase(frame.f_code.co_filename)
        if self._skip_internal and filename == self._profiler_file:
            return self._trace

        now = self._clock()
        self._stop_timing(now)

        key = (filename, frame.f_lineno)
        if key not in self._order:                     # keep first-seen order
            self._order[key] = len(self._order) + 1

        self._last_key = key
        self._last_time = now
        return self._trace

    def _stop_timing(self, now: float):
        if self._last_key is not None:
            self._timings[self._last_key] += now - self._last_time

    # ─────────────────────────────────── report ────────────────────────────────
    def _report(self):
        total = sum(self._timings.values()) or 1e-12
        for (filename, lineno), idx in list(self._order.items())[:-1]:
            wall = self._timings[(filename, lineno)]
            pct = wall / total * 100
            code = linecache.getline(filename, lineno).rstrip()
            print(f"L{idx}: {code} - {wall:.3f} s ({pct:5.1f}%)", file=self._stream)


# keep the original import style
line_profiler = LineProfiler
