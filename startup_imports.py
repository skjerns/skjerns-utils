# standard imports
try:
    import os
    import sys
    import numpy as np
    from importlib import reload
    import unittest
    import inspect
except Exception as e:
    print(e)

# lazy import of matplotlib
class Importplt(object):
    def __setattr__(self, name, value):
        global plt
        import matplotlib.pyplot as plt
        import sys
        setattr(sys, name, value)
    def __getattribute__(self, name):
        global plt
        import sys
        import matplotlib.pyplot as plt
        return getattr(sys, name)

    
# these libraries are maybe not present
try:
    from tqdm import tqdm
    import sdill as pickle
    plt = Importplt()
    dill = pickle
    from pysnooper import snoop
    import stimer
    from stimer import start, stop
except Exception as e:
    print(e)    

# check if run in console or in script
def is_in_script():
    print(get_ipython().__class__.__name__)
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
