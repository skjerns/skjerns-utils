from setuptools import setup
import os
import shutil


setup(name='skjerns-utils',
      version='1.10',
      description='A collection of tools and boiler plate functions',
      url='http://github.com/skjerns/skjerns-utils',
      author='skjerns',
      author_email='nomail',
      license='GNU 2.0',
      packages=['stimer', 'sdill', 'ospath'],
      install_requires=['dill', 'dateparser', 'pyedflib', 'mat73', 'mss', 'lspopt', 'pytablewriter',
      'pybind11', 'bleak', 'scikit-learn', 'dill','coverage', 'imageio', 'keras', 'natsort', 'pyexcel', 'pyexcel-ods', 'pyexcel-ods3', 'mlxtend',
      'numba', 'tqdm', 'prettytable', 'pysnooper', 'mne', 'joblib', 'clipboard', 'dateparser', 
      'opencv-python==3.4.8.29', 'pygame', 'python-pptx', 'dominate', 'pyglet', 'python-picard'],
      zip_safe=False)

import sys, os, traceback, types

if __name__=='__main__':
    try:
        from tkinter import Tk
        from tkinter import *
        from tkinter import messagebox as mb
        root = Tk()
        res = mb.askquestion('Copy startup script?', 'Do you want to copy the startup-imports.py to the ipython startup folder? This may have side-effects.\n\nIf you dont know what this does, click "No".')
        root.destroy()
        
        if res == 'yes':
            home = os.path.expanduser('~')
            ipython_path  = os.path.join(home, '.ipython', 'profile_default', 'startup')
            shutil.copy('./startup_imports.py', ipython_path)
            print('Copied startup-script to', ipython_path)
    except:
        print('Could not copy to', ipython_path, '\ncopy manually')
