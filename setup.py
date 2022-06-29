# http://web.archive.org/web/20120622213400/http://cx-freeze.sourceforge.net/cx_Freeze.html
from cx_Freeze import setup, Executable

includefiles = ['PyCopyMove.bat', 'auxfiles/']
includes = []
excludes = []
packages = []


setup(
    name="DougPyCopyMove",
    version="0.1",
    description="DougPyCopyMove.py cx_Freeze script",
    author="Douglas Kaynor",
    options={'build_exe': {'includes': includes,
                           'excludes': excludes,
                           'packages': packages,
                           'include_files': includefiles}},
    executables=[Executable("DougPyCopyMove.py",
                            copyDependentFiles=True,
                            appendScriptToExe=True)])
