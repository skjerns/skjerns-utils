import time as t
from inspect import getframeinfo, stack
import os
import numpy as np



def timeit(fn):
    """
    time a function call, use it as a wrapper:
    
    Example:
        @stimer.timeit
        def test():
            time.sleep(1)
        # 1 second

    Can be called repeatedly:
        @stimer.timeit(15)
        def test():
            time.sleep(1)
        # 15 seconds
    """
    def wrapper(func, iterations=1):
        def wrapped(*args, **kwargs):
            times = []
            for i in range(iterations):
                start(func.__name__)
                result = func(*args, **kwargs)
                elapsed = stop(func.__name__, verbose=False)
                times.append(elapsed)
            mean = _print_time(np.mean(times))
            std = ' +- ' +  _print_time(np.std(times)) if iterations>1 else ''
            repeats = f', {iterations} loops' if iterations>1 else ''
            print(f'{func.__name__}: runtime {mean}{std}{repeats}')
            return result
        return wrapped
    if callable(fn):
        return wrapper(fn, iterations=1)
    elif isinstance(fn, int):
        def wrapped_repeated(func):
            return wrapper(func, iterations=fn)
        return wrapped_repeated


def lapse(prefix='', verbose=True):
    """
    Will print the time from the previous invocation
    """
    identifier = '%%LAPSE%%'
    if not identifier in starttime:
        starttime[identifier] = t.perf_counter()
        elapsed = 0
    else:
        elapsed = t.perf_counter() - starttime[identifier]
        elapsed_str = _print_time(elapsed)
        caller = getframeinfo(stack()[1][0])
        count = starttime['%%COUND%%']
        line = '{}:{}():{}'.format(os.path.basename(caller.filename), caller.function,  caller.lineno)
        if line in line_cache: 
            line_cache.clear()
            line_cache.add(line)
            star='#'
        else:
            line_cache.add(line)
            star = ''
        if prefix != '': prefix = f' {prefix}'
        if verbose:
            print(f'[{count}{prefix}] {line} - {elapsed_str}\t{star}')
        starttime[identifier] = t.perf_counter()
    starttime['%%COUND%%']+=1
    return elapsed


def start(identifier = ''):
    """
    Starts a timer with the given identifier
    """
    starttime[identifier] = t.perf_counter()
   


def _print_time(seconds):    
    if seconds > 7200:
        hours   = seconds//3600
        minutes = seconds//60 - hours*60
        return "{:.0f}:{:02.0f} hours".format(hours, minutes)
    elif seconds > 180:
        minutes = seconds//60
        seconds = seconds%60
        return "{:.0f}:{:02.0f} min".format(minutes , seconds)
    elif seconds >= 1:
        return "{:02.1f} sec".format(seconds)
    elif seconds > 0.01:
        return "{} ms".format(int(seconds*1000))
    elif seconds > 0.001:
        return "{:.1f} ms".format(seconds*1000)
    elif seconds > 0.0001:
        return "{:.1f} μs".format(seconds*100000)
    else:
        return "{} nanoseconds".format(int(seconds*1e-9))
   
    
def stop(identifier = '', verbose=True):
    """
    Stops a timer with the given identifier and prints the elapsed time
    """
    try:
        elapsed = t.perf_counter() - starttime[identifier]
        if verbose: 
            print('Elapsed {}: {}'.format(identifier, _print_time(elapsed)))
        del starttime[identifier]
        return elapsed
    except KeyError:
        print('[stimer] KeyError: Identifier {} not found'.format(identifier))
   
def sleep(seconds):
    t.sleep(seconds)


starttime = dict({'%%COUND%%':0})
line_cache = set()
wrapper = timeit
