## ospath
This package can be used instead of `os.path` and will unify all backslashes (windows) to unix slashes. This way we can e.g. use paths as keys in dictionaries across platforms. All functions from ospath are mirrored.


### Overview
usage:
```python
import ospath 
windowspath = '.\\images\\image1.jpg'
unified = os.path.join(windowspath)
print(unified) # './images/image1.jpg'
```

Other functions:

1. All backslashes '\\' will be replaced with '/' for windows-linux compatibility.
2. Leading \\ or / will be removed from the *paths to prevent problems, see also https://stackoverflow.com/questions/1945920/why-doesnt-os-path-join-work-in-this-case
3. All double backslashes and double slashes will be replaces with single slashes using os.path.normpath()
4. '~' will be converted to the specific USERDIR, only the first path argument will be expanded


### Misc. functions

```Python
# list all folders on a given path
list_folders(path, subfolders=False, add_parent=False)

# list all files in a given folder
list_files(path, exts=None, patterns=None, relative=False,...)

# open tkinter chooser dialoge for files and folder
choose_file(default_dir=None,exts='txt', title='Choose file')
choose_folder(default_dir=None,exts='txt', title='Choose file')
```
