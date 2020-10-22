import sys
import types
from .stimer import start, stop, sleep, _dummy_wrapper, lapse

class CallAbleModule(types.ModuleType):
    def __init__(self):
        types.ModuleType.__init__(self, __name__)
        # or super().__init__(__name__) for Python 3
        self.__dict__.update(sys.modules[__name__].__dict__)
    def __call__(self):
        return 42

sys.modules[__name__] = CallAbleModule()