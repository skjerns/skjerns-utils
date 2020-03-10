from setuptools import setup
import os
import shutil

setup(name='skjerns-utils',
      version='1.07',
      description='A collection of tools to speed up my development',
      url='http://github.com/skjerns/skjerns-utils',
      author='skjerns',
      author_email='nomail',
      license='GNU 2.0',
      packages=['stimer', 'sdill', 'ospath'],
      install_requires=['dill'],
      zip_safe=False)


try:
    home = os.path.expanduser('~')
    ipython_path  = os.path.join(home, '.ipython', 'profile_default', 'startup')
    shutil.copy('./startup_imports.py', ipython_path)
    print('Copied startup-script to', ipython_path)
except:
    print('Could not copy to', ipython_path, '\ncopy manually')
