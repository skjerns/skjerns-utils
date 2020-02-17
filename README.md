## skjerns-utils

This repository includes three packages: `sDill`, `sTimer` and `ospath`.

Additionally it has some custom files like `startup.py` for `iPython` or a bat file to create an icon for Spyder

## Installation
`pip install git+https://github.com/skjerns/skjerns-utils`

## Utils
### ospath
This package can be used instead of `os.path` and will unify all backslashes (windows) to unix slashes. This way we can e.g. use paths as keys in dictionaries across platforms.



usage:
``` python
import ospath
windowspath = '.\\images\\image1.jpg'
unified = os.path.join(windowspath)
print(unified) # './images/image1.jpg'
```

Details: [ospath](./ospath/)

### sDill

A simple wrapper to use picke/dill with strings instead of file-objects

usage:
```python
import sdill as pickle
pickle.load('picklefile.pkl')

```

Details: [sDill](./sdill/)

### sTimer

A simple stoptimer

usage:
```python
import stimer
stimer.start()
stimer.stop()
# elapsed: 0.00 seconds
```

Details: [sTimer](./stimer/)

### CopyAbsPythonPath
Starting this executable once will add an item to the context menu to copy the path of any file in a pythonic way, that means with all backslashes turned into slashes. If you don't trust this file, just delete it.
