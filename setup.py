from setuptools import setup
import os
import sys
import shutil
import subprocess

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception:
        print(f'Could not install {package}')
            
setup(name='skjerns-utils',
      version='1.12',
      description='A collection of tools and boiler plate functions',
      url='http://github.com/skjerns/skjerns-utils',
      author='skjerns',
      author_email='nomail',
      license='GNU 2.0',
      packages=['stimer', 'sdill', 'ospath'],
      zip_safe=False)

import sys, os, traceback, types

if __name__=='__main__':
    packages = ['demandimport', 'dill', 'dateparser', 'pyedflib', 'mat73', 'mss', 'lspopt', 'pytablewriter',
                'pybind11', 'bleak', 'scikit-learn', 'dill','coverage', 'imageio', 'keras', 'natsort', 'pyexcel', 'pyexcel-ods', 'pyexcel-ods3', 'mlxtend',
                'numba', 'tqdm', 'prettytable', 'pysnooper', 'mne', 'joblib', 'clipboard', 'dateparser', 'umap-learn',
                'opencv-python', 'pygame', 'python-pptx', 'dominate', 'pyglet', 'python-picard', 'seaborn']

    if sys.argv[1] == 'install':
          for package in packages:
              install(package)

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
