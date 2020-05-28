choco install anaconda3 --force --params '"/AddToPath /D:%UserProfile%\"'
%UserProfile%\Anaconda3\scripts\pip.exe install pybind11 emlearn bleak scikit-learn dill coverage imageio keras natsort numba tqdm prettytable pysnooper mne joblib clipboard dateparser opencv-python==3.4.8.29 git+https://github.com/skjerns/skjerns-utils git+https://github.com/hbldh/lspopt.git#egg=lspopt pygame 
%UserProfile%\Anaconda3\scripts\pip.exe install pprint mss pyexcel pyexcel-ods pyexcel-ods3 mat73 pyedflib git+https://github.com/skjerns/pyRobotEyez

set SHIMGEN=C:\ProgramData\chocolatey\tools\shimgen.exe
set ANACONDA=%UserProfile%\anaconda3
%SHIMGEN% -p %ANACONDA%\pythonw.exe -o %ANACONDA%\spyder_icon.exe -c "%ANACONDA%\cwp.py %ANACONDA% %ANACONDA%\pythonw.exe %ANACONDA%\Scripts\spyder-script.py" -i %ANACONDA%\Scripts\spyder.ico

C:\Users\Simon\Anaconda3\pythonw.exe C:\Users\Simon\Anaconda3\cwp.py C:\Users\Simon\Anaconda3 C:\Users\Simon\Anaconda3\pythonw.exe C:\Users\Simon\Anaconda3\Scripts\spyder-script.py

type NUL > "%UserProfile%\vis.bat"
ECHO call activate visbrain >> "%UserProfile%\vis.bat"
ECHO call activate visbrain >> "%UserProfile%\vis.bat"
ECHO python -c "import sys;from visbrain.gui import Sleep;s=Sleep(data=sys.argv[1] if len(sys.argv)>1 else None, hypno=None).show()" %1 >> "%UserProfile%\vis.bat"
ECHO Pause >> "%UserProfile%\vis.bat"

conda create -n visbrain
activate visbrain
pip install visbrain
conda create -n py27 python=2.7
pause
