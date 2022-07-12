import sys
import types
from .stimer import start, stop, sleep, lapse, timeit, wrapper

class CallableModule(types.ModuleType):

    def __init__(self):

        self.identifier = 'context'
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)

    def __enter__(self):
        start(self.identifier)
        return None

    def __exit__(self, exc_type, exc_val, traceback):
        stop(self.identifier)

    def __call__(self, identifier='context'):
        self.identifier = identifier
        return self


sys.modules[__name__] = CallableModule()


    
