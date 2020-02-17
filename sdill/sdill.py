from dill import load as sload
from dill import dump as sdump


def load(file):
    """
    This wrapper allows dill to be called with strings instead of open()
    
    :param file: a string or a file handler
    :returns: dill called with the parameters
    """
    if type(file) is str:
        with open(file, 'rb') as f:
            return sload(f)
    else:
        return sload(file)
            
def dump(obj, file, protocol=None, byref=None, fmode=None, recurse=None):
    """
    This wrapper allows dill to be called with strings instead of open()
    
    :param obj: object to pickle
    :param file: a string or a file handler
    :returns: dill called with the parameters
    """
    if type(file) is str:
        with open(file, 'wb') as f:
            return sdump(obj, f, protocol=None, byref=None, fmode=None, recurse=None)
    elif type(file):
        return sdump(obj, file, protocol=None, byref=None, fmode=None, recurse=None)
