# -*- coding: utf-8 -*-
"""

Created on Wed Jan 10 17:13:01 2018

This file contains wrappers for calls to os.path. 

1. All backslashes '\\' will be replaced with '/' for windows-linux compatibility.
2. Leading \\ or / will be removed from the *paths to prevent problems 
          (see https://stackoverflow.com/questions/1945920/why-doesnt-os-path-join-work-in-this-case) 
3. All double backslashes and double slashes will be replaces with single slashes using os.path.normpath()
4. '~' will be converted to the specific USERDIR, only the first path argument will be expanded
5. there is a os.listfiles that can filter extensions and give a full path

@author: Simon Kern (@skjerns)
"""

try:
    from pathlib import Path
except Exception:
    print('[ospath] can\'t import Path from pathlib, need Python 3.5+')
from os import makedirs
from os.path import *
import os
import re
import fnmatch
from natsort import natsort_key


from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import simpledialog
from tkinter import  Tk


_invalid_chars = "<>:\"/\\|?*\n\r\t"



def join(path, *paths):
    """
    Wrapper of os.path.join that always returns linux slashes
    
    1. All backslashes '\\' will be replaced with '/' for windows-linux compatibility.
    2. Leading \\ or / will be removed from the *paths to prevent problems 
              (see https://stackoverflow.com/questions/1945920/why-doesnt-os-path-join-work-in-this-case) 
    3. All double backslashes and double slashes will be replaces with single slashes using os.path.normpath()
    4. '~' will be converted to the specific USERDIR, only the first path argument will be expanded
    
    @param path:             A path in all its variations
    @param *paths:           More paths
    @return: joined_path as described above
    """
    path = os.path.expanduser(path)
    path = os.path.normpath(path)
    paths = [os.path.normpath(path) for path in paths]
    paths = [path.replace('\\', '/') for path in paths]
    paths = [path[1:] if (path.startswith('/') or path.startswith('\\')) else path for path in paths]
    joined_path = os.path.join(path, *paths)
    joined_path = joined_path.replace('\\', '/')
    joined_path = joined_path.replace('//', '/').replace('//', '/')
    return joined_path.replace('\\', '/')


def splitext(p):
    p = join(p)
    return os.path.splitext(p)


def split(p):
    p = join(p)
    return os.path.split(p)


def splitdrive(p):
    p = join(p)
    return os.path.splitdrive(p)


def expanduser(p):
    p = os.path.expanduser(p)
    return join(p)


def abspath(path):
    path = os.path.abspath(path)
    return join(path)


def dirname(path):
    path = os.path.dirname(path)
    return join(path)


def relpath(path, start=None):
    path = os.path.relpath(path, start)
    return join(path)


def commonpath(paths):
    paths = os.path.commonpath(paths)
    return join(paths)


def list_folders(path, subfolders=False, add_parent=False, pattern='*'):
    """
    This function will list all folders or subfolders of a certain directory
    
    :param path: parent folder, will be in included in return list
    :param subfolders: include subfolders of folders
    :returns: A list of folders and optionally subfolders
    """
    path += '/'
    path = join(path)
    assert isdir(path), '{} is not a directory'.format(path)
    folders = []
    if add_parent: folders = [path]
    
    for foldername in next(os.walk(path))[1]:
        folder = join(path, foldername, '/')
        if fnmatch.fnmatch(foldername.lower(), pattern.lower()):
            folders.append(folder)
        if subfolders:
            folders.extend(list_folders(folder, subfolders=True,
                                        add_parent=False, pattern=pattern))
        
    return sorted(folders, key=natsort_key)

def list_files(path, exts=None, patterns=None, relative=False, 
               subfolders=False, return_strings=True, only_folders=False,
               max_results=None):
    """
    will make a list of all files with extention exts (list)
    found in the path and possibly all subfolders and return
    a list of all files matching this pattern
    
    :param path:  location to find the files
    :type  path:  str
    :param exts:  extension of the files (e.g. .jpg, .jpg or .png, png)
                  Will be turned into a pattern internally
    :type  exts:  list or str
    :param pattern: A pattern that is supported by pathlib.Path, 
                  e.g. '*.txt', '**\rfc_*.clf'
    :type:        str
    :param fullpath:  give the filenames with path
    :type  fullpath:  bool
    :param subfolders
    :param return_strings: return strings, else returns Path objects
    :return:      list of file names
    :type:        list of str
    """
    if isinstance(exts, str): exts = [exts]
    if isinstance(patterns, str): patterns = [patterns]
    assert isinstance(path, str), "path needs to be a str"
    assert os.path.exists(path), 'Path {} does not exist'.format(path)
    if patterns is None: patterns = []
    if exts is None: exts = []
    
    if patterns==[] and exts == []:
        patterns = ['*']
    
    for ext in exts:
        ext = ext.replace('*', '')
        pattern = '*' + ext
        patterns.append(pattern.lower())
    
    # if recursiveness is asked, prepend the double asterix to each pattern
    if subfolders: patterns = ['**/' + pattern for pattern in patterns]   
    
    # collect files for each pattern
    files = []
    fcount = 0
    for pattern in patterns:
        # pattern = 
        for filename in Path(path).glob(pattern):
            if filename.is_file() and filename not in files: 
                files.append(filename)
                fcount += 1
                if max_results is not None and max_results<=fcount:
                    break
    
    # turn path into relative or absolute paths
    files = [file.relative_to(path) if relative else file.absolute() for file in files]
        
    # by default: return strings instead of Path objects
    if return_strings: 
        files = [join(file) for file in files]
    
    return sorted(files, key=natsort_key)

def choose_file(default_dir=None,exts='txt', title='Choose file'):
    """
    Open a file chooser dialoge with tkinter.
    
    :param default_dir: Where to open the dir, if set to None, will start at wdir
    :param exts: A string or list of strings with extensions etc: 'txt' or ['txt','csv']
    :returns: the chosen file
    """
    root = Tk()
    root.iconify()
    root.update()
    if isinstance(exts, str): exts = [exts]
    name = askopenfilename(initialdir=None,
                           parent=root,
                           title = title,
                           filetypes =(*[("File", "*.{}".format(ext)) for ext in exts],
                                       ("All Files","*.*")))
    root.update()
    root.destroy()
    if not os.path.exists(name):
        print("No file chosen")
    else:
        return name

def choose_folder(default_dir=None,exts='txt', title='Choose file'):
    """
    Open a file chooser dialoge with tkinter.
    
    :param default_dir: Where to open the dir, if set to None, will start at wdir
    :param exts: A string or list of strings with extensions etc: 'txt' or ['txt','csv']
    :returns: the chosen file
    """
    root = Tk()
    root.iconify()
    root.update()
    if isinstance(exts, str): exts = [exts]
    name = askdirectory(initialdir=None,
                           parent=root,
                           title = title)
    root.update()
    root.destroy()
    if not os.path.exists(name):
        print("No folder chosen")
    else:
        return name


def valid_filename(string, replacement='_'):
    """
    replace all non-valid filename characters with an underscore
    """
    string = str(string)
    return ''.join([replacement if x in _invalid_chars else x for x in string])
