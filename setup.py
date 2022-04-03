from setuptools import setup
import os
import sys
import shutil
import subprocess

# setup(name='skjerns-utils',
#       version='1.12',
#       description='A collection of tools and boiler plate functions',
#       url='http://github.com/skjerns/skjerns-utils',
#       author='skjerns',
#       author_email='nomail',
#       license='GNU 2.0',
#       install_requires=['tqdm'],
#       packages=['stimer', 'sdill', 'ospath'],
#       zip_safe=False)

#%% Second part with optional install
def install(package):
    if isinstance(package, str):
        package = [package]
    with subprocess.Popen([sys.executable, "-m", "pip", "install", *package], stdout=subprocess.PIPE, bufsize=0) as p:
        char = p.stdout.read(1)
        while char != b'':
            print(char.decode('UTF-8'), end='', flush=True)
            char = p.stdout.read(1)

    if p.returncode: 
        print(f'\t!!! Could not install {package}\n', flush=True)


class Redirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget
        self._stderr = sys.stderr
        self._stdout = sys.stdout
        sys.stdout = self
        sys.stderr = self

    def write(self, *args, **kwargs):
        self.text_space.insert('end', ' '.join(args))
        self.text_space.see('end')     
        self._stdout.write(*args, **kwargs)
        self.text_space.parent.update_idletasks()
        self.text_space.parent.update()
        
    def flush(self, *args, **kwargs):
        self._stderr.flush(*args)
        self._stdout.flush(**kwargs)
     
    def restore(self):
        sys.stderr = self._stderr
        sys.stdout = self._stdout
        
        
        
class InstallPackagesGUI(object):
    
    def __init__(self, packages):
        self.stopped = False
        self.started = False
        self.packages = packages
        self.timeout = 15
        
        parent = Tk()
        # parent.overrideredirect(1)
        parent.configure(bg="black")
        parent.eval('tk::PlaceWindow . center')
        parent.title("Install optional dependencies?")
        parent.resizable(False, False)
        msg = """Do you want to 
        
    - copy the startup-imports.py to the ipython startup folder and
    - install the optional dependencies?
    
This may have unexpected side-effects.\n\nIf you dont know what this does, click "No".
"""

        self.parent = parent
        
        self.text_box = Text(self.parent, wrap='word', height = 20, width=120,
                             background='black', foreground='white', font=('Consolas', 10))
        self.text_box.grid(column=0, row=0, columnspan = 9, sticky='NSWE', padx=5, pady=5)
        self.text_box.parent = parent
        
        self.redirector = Redirector(self.text_box)
        print(msg)
        button1 = Button(self.parent, text="Yes, install\n(not recommended)", command=self.install,
                         width=20, height=2, fg='red')
        button1.grid(column=1, row=1)
        button2 = Button(self.parent, text="No", command=self.destroy, width=10, height=2)
        button2.grid(column=2, row=1, pady=10)
        parent.protocol("WM_DELETE_WINDOW", self.redirector.restore)
       
        progress= ttk.Progressbar(
                                parent,
                                orient='horizontal',
                                mode='determinate',
                                length=280,
                                maximum=len(self.packages)-1
                            )
        progress.grid(column=4, row=1, columnspan=5, padx=10, pady=20)
        
        self.button1 = button1
        self.button2 = button2
        self.progress = progress
        self.parent.after(1000, self.destroy_if_no_action)
        parent.mainloop()    
        
    def destroy_if_no_action(self):
        if self.timeout==0:
            self.destroy()
        elif not self.started:
            self.button1['text'] = f'Yes, install ({self.timeout})\n(not recommended)'
            self.timeout-=1
            self.parent.after(1000, self.destroy_if_no_action)
    
    def install(self):
        self.started = True
        
        self.button1['state'] = 'disable'
        self.button2['text'] = 'Stop'

        home = os.path.expanduser('~')
        ipython_path  = os.path.join(home, '.ipython', 'profile_default', 'startup')
        shutil.copy('./startup_imports.py', ipython_path)
        print('Copied startup-script to', ipython_path, '\n')
        
        print(f'installing packages: {self.packages}\n')

        for i, package in enumerate(self.packages):
            if not self.stopped:
                self.progress['value']=i
                install(package)
        self.destroy()           

    def destroy(self):
        self.stopped = True
        self.redirector.restore()
        self.parent.destroy()
        
        

if __name__=='__main__':
    packages = [['numpy', 'scipy', 'scikit-learn', 'joblib', 'numba', 'imageio', 'seaborn'], 
                ['pyexcel', 'pyexcel-ods', 'pyexcel-ods3', 'python-pptx'],
                ['mlxtend','umap-learn'], ['mne', 'python-picard'],
                'demandimport', 'dill', 'pyedflib', 'mat73', 'mss', 'lspopt', 
                'pytablewriter', 'pybind11', 'bleak', 'coverage', 'keras', 
                'natsort','prettytable', 'pysnooper', 'clipboard',
                'dateparser', 'opencv-python', 'pygame', 'dominate', 'pyglet', 
                'beautifulsoup4']
    if len(sys.argv)==1 or sys.argv[1] != 'egg_info':
          try:
              from tkinter import Tk, ttk
              from tkinter import Text, Button
              InstallPackagesGUI(packages)
          except:
              pass
