import time as t
from inspect import getframeinfo, stack
import os
import numpy as np



def timeit(func, *args, repetitions=1, **kwargs):
    """
    time a certain function call
    """
    
    mean_elapsed = []
    for repetition in range(repetitions):
        start('%%TIMEIT%%')
        result = func(*args, **kwargs)
        elapsed = stop('%%TIMEIT%%', verbose=False)
        mean_elapsed.append(elapsed)
    
    elapsed = np.array(elapsed)
    min_str = _print_time(elapsed.min())
    max_str = _print_time(elapsed.max())
    mean_str = _print_time(elapsed.mean())
    
    if repetitions==1:
        print(f'[{func.__name__}] {mean_str}')
    else:
        print(f'[{func.__name__}] {repetitions} runs: {mean_str} ({min_str} - {max_str})')
    return elapsed
    


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
    
def _dummy_wrapper(obj):
    """a dummy wrapper that just passes through functions"""
    return obj
    
starttime = dict({'%%COUND%%':0})
line_cache = set()
