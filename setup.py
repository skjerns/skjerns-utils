from setuptools import setup

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
