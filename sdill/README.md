## sDill
A wrapper for dill to enable calls with filestrings.

## Installation
`pip install git+https://github.com/skjerns/sDill`

## Usage
```Python 
import sdill

sdill.dump([1,2,3], 'filestr.pkl')

a = sdill.load('filestr.pkl')
print(a)
# [1, 2, 3]
```

or as an interface to dill or pickle

```Python 
import sdill as dill
import sdill as pickle

pickle.dump([1,2,3], 'filestr.pkl')

a = pickle.load('filestr.pkl')
print(a)
# [1, 2, 3]
```
