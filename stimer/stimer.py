import time as t

def time(identifier = ''):
    """
    A timer with the identifier will be either started or stopped.
    Same as toggle()
    
    :param identifier: 
    """
    if identifier in starttime:
        return stop(identifier)
    else :
        return start(identifier)
    
def toggle(identifier=''):
    return time(identifier)

def start(identifier = ''):
    """
    Starts a timer with the given identifier
    """
    starttime[identifier] = t.time()
    
def stop(identifier = ''):
    """
    Stops a timer with the given identifier and prints the elapsed time
    """
    try:
        end = t.time()-starttime[identifier]
        if end > 7200:
            hours   = end//3600
            minutes = end//60 - hours*60
            print("Elapsed{}: {:.0f}:{:02.0f} hours".format(' '+str(identifier) if len(str(identifier))>0 else '',hours,minutes))
        elif end > 180:
            minutes = end//60
            seconds = end%60
            print("Elapsed{}: {:.0f}:{:02.0f} minutes".format(' '+str(identifier) if len(str(identifier))>0 else '', minutes , seconds ))
        else:
            print("Elapsed{}: {:02.3f} seconds".format(' '+str(identifier) if len(str(identifier))>0 else '',end))
        elapsed =  t.time()-starttime[identifier]
        del starttime[identifier]
        return elapsed
    
    except KeyError:
        print('[stimer] KeyError: Identifier {} not found'.format(identifier))
   
def sleep(seconds):
    t.sleep(seconds)
    
def _dummy_wrapper(obj):
    """a dummy wrapper that just passes through functions"""
    return obj
    
starttime = dict()
start('')
