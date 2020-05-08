import time as t
from inspect import getframeinfo, stack
import os





def lapse():
    """
    Will print the time from the previous invocation
    """
    identifier = '%%LAPSE%%'
    if not identifier in starttime:
        starttime[identifier] = t.time()
    else:
        elapsed = _print_time(t.time() - starttime[identifier])
        caller = getframeinfo(stack()[1][0])
        count = starttime['%%COUND%%']
        line = '{}:{}():{}'.format(os.path.basename(caller.filename), caller.function,  caller.lineno)
        if line in line_cache: 
            line_cache.clear()
            star='*'
        else:
            line_cache.add(line)
            star = ''
        print('[{}] {} - {}\t{}'.format(count, line, elapsed, star))
        starttime[identifier] = t.time()
    starttime['%%COUND%%']+=1

def start(identifier = ''):
    """
    Starts a timer with the given identifier
    """
    starttime[identifier] = t.time()
   


def _print_time(seconds):
        if seconds > 7200:
            hours   = seconds//3600
            minutes = seconds//60 - hours*60
            return "{:.0f}:{:02.0f} hours".format(hours, minutes)
        elif seconds > 180:
            minutes = seconds//60
            seconds = seconds%60
            return "{:.0f}:{:02.0f} min".format(minutes , seconds)
        elif seconds > 1:
            return "{:02.1f} sec".format(seconds)
        elif seconds > 0.001:
            return "{} ms".format(int(seconds*1000))
        else:
            return "{} ms".format(seconds*1000)
   
    
def stop(identifier = ''):
    """
    Stops a timer with the given identifier and prints the elapsed time
    """
    try:
        elapsed = t.time()-starttime[identifier]
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
