# standard imports
try:
    # Dummy exception. Just for correct linting in file.
    raise Exception()
    plt, get_ipython = None  # will not actually be executed
except:
    pass

try:
    import os
    import sys
    import unittest
    import inspect
    import shutil
    import tempfile
    import warnings
    import numpy as np
    from pprint import pformat, pprint
except Exception as e:
    print(f'[startup_imports] Error while loading builtin modules: {e}')    

    
# these libraries are maybe not present
__import_statements = """
from tqdm import tqdm
import sdill as pickle
import matplotlib.pyplot as plt
import seaborn as sns
dill = pickle
""".strip().split('\n')

try:
    import demandimport
    import stimer
except:
    pass
for __import_statement in __import_statements:
    try:
        exec(f'with demandimport.enabled():{__import_statement}')
    except Exception as e1:
        print(f'Cannot lazy import `{__import_statement}`:\n-->{e1}')
        try:
            exec(__import_statement)
        except Exception as e2:
            print(f'Error on import statement in startup_imports.py `{__import_statement}`:\n-->{e2}')

# check if run in console or in script
def is_in_script():
    try:
        return get_ipython().__class__.__name__=='EZMQInteractiveShell'
    except:
        return True

# this makes debugging unittests line by line much easier
class _DummyTestClass(unittest.TestCase):
    def __getattribute__(self, item):
        if not (item  in ['__class__', 'runTest','addTypeEqualityFunc', '_type_equality_funcs' ]) \
        and not (item in unittest.TestCase.__dict__):
            if is_in_script():
                print('this function should not be called within a script, only from command line\n' +
                                  'make sure all calls to cls/self are assigned. Tried read  {}'.format(item))
        return object.__getattribute__(self, item)
    def __setattr__(self, item, value):
        if not (item  in ['__class__', 'runTest','addTypeEqualityFunc', '_type_equality_funcs' ]) \
        and not (item in unittest.TestCase.__dict__) and not (item.startswith('_')):
            if is_in_script():
                print('this function should not be called within a script, only from command line\n' +
                                  'make sure all calls to cls/self are assigned. Tried set  {}'.format(item))
        return object.__setattr__(self, item, value)

self = _DummyTestClass()
cls = self

#######
# pass-through wrapper for line-profiler / kernprof
try:
    # Python 2
    import __builtin__ as builtins
except ImportError:
    # Python 3
    import builtins

try: # pass t
    builtins.profile
except AttributeError:
    # No line profiler, provide a pass-through version
    def profile(func):
        import traceback
        print(f'WARNING: @profile debugger active for {func}()')
        print(traceback.format_stack(limit=2)[0])
        return func
    builtins.profile = profile


####################
#### make matplotlib fullscreen on second screen automatically

def check_extended_display():
    """returns true if two monitors are detected and OS=win. Always false on Linux."""
    try:
        from win32api import GetSystemMetrics
        t_width, t_height = GetSystemMetrics(79), GetSystemMetrics(78)
        c_width, c_height = GetSystemMetrics(1), GetSystemMetrics(0)
        
        if t_width==c_width and c_height==t_height:
            return False
    except ModuleNotFoundError:
        return False
    return True


def _new_figure(num=None, figsize=None, dpi=None, maximize=None,
                second_monitor=None, **kwargs):
    """
    This convenience function creates figures 
    on the second screen automatically and maximizes
    """       
    if num is not None and num in plt.get_fignums():
        return plt._figure(num=num, figsize=figsize, dpi=dpi, **kwargs)
    
    fig = plt._figure(num=num, figsize=figsize, dpi=dpi, **kwargs)

    # check if we are actually running a window or are in an inline-plot
    is_windowed = hasattr(fig.canvas.manager, 'window')
    if not is_windowed: return fig
    
    if maximize is None and not 'figsize' in kwargs:
        maximize = plt.maximize
    second_monitor = second_monitor if second_monitor is not None else plt.second_monitor

    window = fig.canvas.manager.window
    if second_monitor and check_extended_display() and hasattr(window, 'move'):
        fig.canvas.manager.window.move(2100,400)
    if maximize:
        if hasattr(window, 'showMaximized'):
            fig.canvas.manager.window.showMaximized()
        else:
            print(f"Can't maximize figure for window: {window}. showMaximized() not found")
    return fig

def _pause_without_putting_figure_on_top(interval):
    figs = plt.get_fignums()
    
    if len(figs)==0:
        return plt._pause(interval)
        
    td = interval/len(figs)
    for fignum in figs:
        fig = plt.figure(fignum)
        fig.canvas.draw_idle()
        fig.canvas.start_event_loop(td)
        

        
        
plt._pause = plt.pause
plt.pause = _pause_without_putting_figure_on_top

plt._figure = plt.figure
plt.figure = _new_figure
plt.maximize = True
plt.second_monitor = True
plt.rcParams['svg.fonttype'] = 'none' #when saving svg, keep text as text

#%% Change the warnings module such that the source line is not printed
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line

# # overwrite print function with pprint
# def pprint_wrapper(*args, sep=' ', end='\n', file=sys.stdout, flush=False):
#     """
#     Wrapper for pretty-print. Forwards to print.
#     Prints the values to a stream, or to sys.stdout by default.

#     Optional keyword arguments:
#     file:  a file-like object (stream); defaults to the current sys.stdout.
#     sep:   string inserted between values, default a space.
#     end:   string appended after the last value, default a newline.
#     flush: whether to forcibly flush the stream.
#     """
#     if len(args)==1:
#         if not isinstance(args[0], str):
#             args = [pformat(args[0])]
#     __print(*args, sep=sep, end=end, file=file, flush=flush)
# __print = print

# print = pprint_wrapper
# builtins.print = pprint_wrapper

