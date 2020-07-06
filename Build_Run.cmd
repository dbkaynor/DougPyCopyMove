cd C:\Users\dkaynor\DougPython\DougPyCopyMove
rmdir /s /q build
rem del /s /q C:\Users\dbkaynox\DougPython\DougPyCopyMove\build\*.*
del /s /q PyCopyMoveTk.log
del /s /q geany_run_script.bat
pause

python setup.py build
pause

C:\Users\dbkaynox\DougPython\DougPyCopyMove\build\exe.win32-3.4\PyCopyMoveTk.exe
pause
