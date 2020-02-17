choco install anaconda3 --force --params '"/AddToPath /D:%UserProfile%\"'
%UserProfile%\Anaconda3\scripts\pip.exe install pybind11 emlearn bleak scikit-learn dill coverage imageio keras natsort numba tqdm prettytable pysnooper mne joblib clipboard dateparser opencv-python==3.4.8.29 git+https://github.com/skjerns/skjerns-utils git+https://github.com/hbldh/lspopt.git#egg=lspopt pygame 
%UserProfile%\Anaconda3\scripts\pip.exe install pprint mss pyexcel pyexcel-ods pyexcel-ods3 mat73 pyedflib git+https://github.com/skjerns/pyRobotEyez

set SHIMGEN=C:\ProgramData\chocolatey\tools\shimgen.exe
set SCRIPTS=c:\anaconda3\scripts\
%SHIMGEN% -p %SCRIPTS%\spyder.exe -i %SCRIPTS%\spyder.ico -o %SCRIPTS%\spyder_icon.exe

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
