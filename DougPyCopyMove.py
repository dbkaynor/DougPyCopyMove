# https://docs.python.org/3/
#
# TODO
# Check source and destinations for permissions and ownership
# Color status indicator, does not do anything!
# Multiple files at once
#   select destination/operation for each file
#   Method to enable auto complete if dest and operation are the same for all sources
# Why does help not return correctly when called from command line
# Py2Exe
# Drag and drop into running program
#
# Project files save with bad extension
# Source file does not work
#
# Debug levels
# Priorities for source file?
#    SetDefaults()
#    ProjectLoad('default')
#    GetClipBoard()Main.clipboard_get()
#    ParseCommandLine()
#
#
import hashlib
import sys
import os
import platform
import pprint
import inspect

from send2trash import send2trash
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import shutil
import re
import __main__ as main
from ToolTip import ToolTip

from DougModules import SearchPath
from DougModules import MyMessageBox
from DougModules import StartFile
from DougModules import FileStats
from DougModules import DiskSpace
# from DougModules import SetUpLogger
from DougModules import RemoveAFile
from DougModules import ShowEditFile


Main = tkinter.Tk()
pp = pprint.PrettyPrinter(indent=4)
from PyCopyMoveVars import Vars
Vars.ProgramVersionNumber.set('1.0.1')

debugFile = "DougPyCopyMove.txt"
if os.path.exists(debugFile):
    os.remove(debugFile)


def line_info(message="nothing", show=False):
    f = inspect.currentframe()
    i = inspect.getframeinfo(f.f_back)
    tString = f"{os.path.basename(i.filename)}:{i.lineno}  called from {i.function}  {message}\n"
    file1 = open(debugFile, "a")
    file1.write(tString)
    file1.close()
    if show:
        print(tString)

# ------------------------------
# Parse the command line


def ParseCommandLine():
    if len(sys.argv) == 1:
        return

    del sys.argv[0]  # Don't want the script name

    y = []
    y = [x.upper() for x in sys.argv]

    if '-H' in y or '-HELP' in y:
        line_info('Help was found')
        Help()

    if '-A' in y or '-ABOUT' in y:
        line_info('About was found')
        About()

    if '-D' in y or '-DEBUG' in y:
        line_info('Debug was found')
        import pdb
        pdb.set_trace()

    if '-P' in y or '-PROJECT' in y:
        line_info('Project was found')
        ProjectLoad()

    for Src in sys.argv:
        if os.path.exists(Src):
            Vars.FileNameListVar.extend([Src])
            line_info(Src)

    FileSourceEntry.delete(0, tkinter.END)
    FileSourceEntry.insert(
        0, ' '.join([str(len(Vars.FileNameListVar)), 'source files detected']))
    Vars.StatusVar.set(''.join([str(len(Vars.FileNameListVar)),
                       ' source files detected']))
    line_info(' '.join(['Browse source file:', str(Vars.FileNameListVar)]))

# ------------------------------
# Set up defaults in case there is no project file
# Initialize the variables
# Written over by StartUpStuff and by ProjectLoad


def SetDefaults():
    # print(MyTrace(GFI(CF())), 'SetDefaults')
    Vars.KeepFlagsCheckVar.set(1)
    Vars.CheckSourceOnStartVar.set(1)
    Vars.ClearSourceOnStartVar.set(0)
    Vars.AskOnCopyVar.set(1)
    Vars.AskOnMoveVar.set(1)
    Vars.AskOnRecycleVar.set(1)
    Vars.AskOnDeleteVar.set(1)
    Vars.AskOnRenameVar.set(1)
    Vars.AskBeforeOverWriteDuringCopyVar.set(1)
    Vars.AskBeforeOverWriteDuringMoveVar.set(1)
    FileSourceEntry.delete(0, tkinter.END)
    Vars.DestinationCheck01Var.set(0)
    Vars.DestinationCheck02Var.set(0)
    Vars.DestinationCheck03Var.set(0)
    Vars.DestinationCheck04Var.set(0)
    Vars.DestinationCheck05Var.set(0)
    Vars.DestinationCheck06Var.set(0)
    Vars.DestinationCheck07Var.set(0)
    Vars.DestinationCheck08Var.set(0)
    Vars.DestinationCheck09Var.set(0)
    Vars.DestinationCheck10Var.set(0)
    Vars.DestinationCheck11Var.set(0)
    Vars.DestinationCheck12Var.set(0)
    Vars.SystemRenamerVar.set('')
    Vars.SystemEditorVar.set('')

# ------------------------------
# Initialize the program


def StartUpStuff():
    # -- Lots of startup stuff ------------------------------------
    # The following are defaults which will be over written by a project file
    if sys.platform.startswith('linux'):
        Vars.SystemEditorVar.set('gedit')
        Vars.SystemRenamerVar.set('pyrename')
        Vars.ProjectFileExtensionVar.set('prjl')
    elif sys.platform.startswith('win32'):
        Vars.SystemEditorVar.set('c:\\windows\\notepad.exe')
        Vars.SystemRenamerVar.set(
            'C:\\Program Files (x86)\\Ant Renamer\\Renamer.exe')
        Vars.ProjectFileExtensionVar.set('prjw')

    Vars.StartUpDirectoryVar.set(os.getcwd())
    Vars.AuxDirectoryVar.set(os.path.join(
        Vars.StartUpDirectoryVar.get(), 'auxfiles', '.'))
    Vars.HelpFileVar.set(os.path.join(
        Vars.AuxDirectoryVar.get(), 'PyCopyMoveTk.hlp'))
    Vars.LogFileNameVar.set(os.path.join(
        Vars.StartUpDirectoryVar.get(), 'PyCopyMoveTk.log'))
    #  SetUpLogger(Vars.LogFileNameVar.get())

    line_info(' '.join(['OS:', str(os.environ.get('OS'))]))
    line_info(' '.join(['Platform:', str(platform.uname())]))
    line_info(' '.join(['Number of argument(s):', str(len(sys.argv))]))
    line_info(' '.join(['Argument List:', str(sys.argv)]))

    ProjectLoad('default')
    GetClipBoard()
# ------------------------------
# Try to get source file from clipboard


def GetClipBoard():
    # print(MyTrace(GFI(CF())), 'GetClipBoard')
    try:
        temp = Main.clipboard_get()
        temp = temp.replace('"', '').strip()
        if os.path.isfile(temp):
            FileSourceEntry.delete(0, tkinter.END)
            FileSourceEntry.insert(0, temp)
            Vars.StatusVar.set(temp)
            line_info(' '.join(['From clipboard:', temp]))
        else:
            line_info(' '.join(['Invalid path from clipboard:', temp]))
    except Exception as e:
        line_info(' '.join(['No clipboard data', str(e)]))

# ------------------------------
# This class handles file rename for the file info menu


class FileRename:
    RenameEntry = None
    BeforeFilename = ''
    AfterFilename = ''
    Path = ''
    Basename = ''
# ------------------------------

    def Swapcase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, tkinter.END)
        self.RenameEntry.insert(0, filename.swapcase())

    def Titlecase(self):
        filename = self.RenameEntry.get()

        def titlecase(s):
            return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                          lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(), s)
        self.RenameEntry.delete(0, tkinter.END)
        self.RenameEntry.insert(0, titlecase(filename))

    def Uppercase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, tkinter.END)
        self.RenameEntry.insert(0, filename.upper())
        self.RenameEntry.focus_set()

    def Lowercase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, tkinter.END)
        self.RenameEntry.insert(0, filename.lower())
        self.RenameEntry.focus_set()

    def Capitalize(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, tkinter.END)
        self.RenameEntry.insert(0, filename.capitalize())
        self.RenameEntry.focus_set()

    def Done(self):  # Filename will always be the same
        self.AfterFilename = os.path.join(self.Path, self.RenameEntry.get())
        line_info('Rename. Before: %s  After: %s' %
                  (self.BeforeFilename, self.AfterFilename))
        try:
            os.rename(self.BeforeFilename, self.AfterFilename)
        except OSError as e:
            line_info('Rename file error: %s' % e)
            tkinter.messagebox.showerror('Rename file error',
                                         os.linesep.join(['no can do',
                                                          ''.join(['Before filename:', self.BeforeFilename]),
                                                          ''.join(['After filename:', self.AfterFilename]),
                                                          'Return code: %s' % e]))
        Vars.FileRenameTopLevelVar.withdraw()

    def Cancel(self):
        Vars.FileRenameTopLevelVar.withdraw()

    def RenameAFile(self):
        Vars.FileRenameTopLevelVar = tkinter.Toplevel()
        Vars.FileRenameTopLevelVar.title('File rename')
        Vars.FileRenameTopLevelVar.resizable(0, 0)
        Vars.FileRenameTopLevelVar.option_add('*Font', 'courier 10')

        Main.update()
        FileRenameTopLevelSizeX = 400
        FileRenameTopLevelSizeY = 100
        Mainsize = Main.geometry().split('+')
        x = int(Mainsize[1]) + FileRenameTopLevelSizeX / 2
        y = int(Mainsize[2]) + FileRenameTopLevelSizeY / 2
        Vars.FileRenameTopLevelVar.geometry("%dx%d+%d+%d" %
                                            (FileRenameTopLevelSizeX, FileRenameTopLevelSizeY, x, y))
        Vars.FileRenameTopLevelVar.resizable(1, 0)

        FileRenameFrame1 = tkinter.Frame(
            Vars.FileRenameTopLevelVar, relief=tkinter.SUNKEN, bd=1)
        FileRenameFrame1.pack(side=tkinter.tkinter.TOP, fill=tkinter.x)
        FileRenameFrame2 = tkinter.Frame(
            Vars.FileRenameTopLevelVar, relief=tkinter.SUNKEN, bd=1)
        FileRenameFrame2.pack(side=tkinter.tkinter.TOP, fill=tkinter.x)
        FileRenameFrame3 = tkinter.Frame(
            Vars.FileRenameTopLevelVar, relief=tkinter.SUNKEN, bd=1)
        FileRenameFrame3.pack(side=tkinter.tkinter.TOP, fill=tkinter.x)

        # Start here
        self.BeforeFilename = FileSourceEntry.get()
        self.Basename = os.path.basename(self.BeforeFilename)
        self.Path = os.path.dirname(self.BeforeFilename)

        tkinter.Label(FileRenameFrame1, text=self.BeforeFilename).pack(fill=tkinter.x)
        self.RenameEntry = tkinter.Entry(FileRenameFrame1)
        self.RenameEntry.pack(fill=tkinter.x)
        self.RenameEntry.delete(0, tkinter.END)
        self.RenameEntry.insert(0, self.Basename)
        self.RenameEntry.focus_set()

        tkinter.Button(FileRenameFrame2,
                       text='Done',
                       width=8,
                       command=self.Done).pack(side=tkinter.LEFT)
        tkinter.Button(FileRenameFrame2,
                       text='Cancel',
                       width=8,
                       command=self.Cancel).pack(side=tkinter.LEFT)
        tkinter.Button(FileRenameFrame2,
                       text='Title',
                       width=8,
                       command=self.Titlecase).pack(side=tkinter.LEFT)

        tkinter.Button(FileRenameFrame3,
                       text='Upper',
                       width=8,
                       command=self.Uppercase).pack(side=tkinter.LEFT)
        tkinter.Button(FileRenameFrame3,
                       text='Lower',
                       width=8,
                       command=self.Lowercase).pack(side=tkinter.LEFT)
        tkinter.Button(FileRenameFrame3,
                       text='Swap',
                       width=8,
                       command=self.Swapcase).pack(side=tkinter.LEFT)
        tkinter.Button(FileRenameFrame3,
                       text='Capitalize',
                       width=10,
                       command=self.Capitalize).pack(side=tkinter.LEFT)

# ------------------------------
# Loads a project file
# Lines without a ~ in the line are ignored and may be used as comments
# Lines with # in position 0 may be used as comments


def ProjectLoad(LoadType='none'):  # noqa: C901
    # print(MyTrace(GFI(CF())),'ProjectLoad' , LoadType)
    if LoadType == 'default':
        Vars.ProjectFileNameVar.set(os.path.join(Vars.AuxDirectoryVar.get(),
                                                 ''.join(['PyCopyMoveTk.',
                                                          Vars.ProjectFileExtensionVar.get()])))
    else:
        Vars.ProjectFileNameVar.set(tkinter.filedialog.askopenfilename(
            defaultextensio=Vars.ProjectFileExtensionVar.get(),
            filetypes=[('Project file', ''.join(['PyCopyMove*.',
                        Vars.ProjectFileExtensionVar.get()])), ('All files', '*.*')],
            initialdir=Vars.AuxDirectoryVar.get(),
            initialfile=''.join(['PyCopyMoveTk.', Vars.ProjectFileExtensionVar.get()]),
            title='Load a PyCopyMoveTk project file',
            parent=Main))
    Vars.ProjectFileNameVar.set(
        os.path.normpath(Vars.ProjectFileNameVar.get()))

    line_info(' '.join(['Project Load', Vars.ProjectFileNameVar.get()]))

    ProjectEntry.delete(0, tkinter.END)
    ProjectEntry.insert(0, Vars.ProjectFileNameVar.get())

    tkinter.title = 'Select a file',
    try:
        f = open(Vars.ProjectFileNameVar.get(), 'r')
    except IOError:
        tkinter.messagebox.showerror('Project file error',
                                     os.linesep.join(['Requested file does not exist.',
                                                      Vars.ProjectFileNameVar.get()]))
        return

    lines = f.readlines()
    f.close()
    try:
        if not 'PyCopyMoveTk.py project file ' + sys.platform in lines[0]:
            tkinter.messagebox.showerror('Project file error',
                                         os.linesep.join(['Not a valid project file.',
                                                          'project file', lines[0]]))
            line_info(' '.join(['PyCopyMoveTk.py project file', lines[0].strip()]))
            return
    except IOError:
        tkinter.messagebox.showerror('Project file error',
                                     ' '.join(['Unable to read project file', Vars.ProjectFileNameVar.get()]))
        line_info('PyCopyMoveTk.py project file. Unable to read file')
        return

    # remove the first line so it won't be added to the comments list
    del lines[0]
    # Clear any widgets that need to be
    FileSourceListbox.delete(0, tkinter.END)
    Vars.CommentsListVar = []
    for line in lines:
        if '~' in line and line[0] != '#':
            t = line.split('~')
            if 'False' in t[1]:
                t[1] = 0
            elif 'True' in t[1]:
                t[1] = 1
            if 'DestinationEntry01~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry01.delete(0, tkinter.END)
                DestinationEntry01.insert(0, x)
            if 'DestinationEntry02~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry02.delete(0, tkinter.END)
                DestinationEntry02.insert(0, x)
            if 'DestinationEntry03~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry03.delete(0, tkinter.END)
                DestinationEntry03.insert(0, x)
            if 'DestinationEntry04~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry04.delete(0, tkinter.END)
                DestinationEntry04.insert(0, x)
            if 'DestinationEntry05~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry05.delete(0, tkinter.END)
                DestinationEntry05.insert(0, x)
            if 'DestinationEntry06~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry06.delete(0, tkinter.END)
                DestinationEntry06.insert(0, x)
            if 'DestinationEntry07~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry07.delete(0, tkinter.END)
                DestinationEntry07.insert(0, x)
            if 'DestinationEntry08~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry08.delete(0, tkinter.END)
                DestinationEntry08.insert(0, x)
            if 'DestinationEntry09~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry09.delete(0, tkinter.END)
                DestinationEntry09.insert(0, x)
            if 'DestinationEntry10~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry10.delete(0, tkinter.END)
                DestinationEntry10.insert(0, x)
            if 'DestinationEntry11~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry11.delete(0, tkinter.END)
                DestinationEntry11.insert(0, x)
            if 'DestinationEntry12~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry12.delete(0, tkinter.END)
                DestinationEntry12.insert(0, x)
            if 'KeepFlagsCheckVar~' in line:
                Vars.KeepFlagsCheckVar.set(int(t[1]))
            if 'CheckSourceOnStartVar~' in line:
                Vars.CheckSourceOnStartVar.set(int(t[1]))
            if 'ClearSourceOnStartVar~' in line:
                Vars.ClearSourceOnStartVar.set(int(t[1]))
            if 'AskOnCopyVar~' in line:
                Vars.AskOnCopyVar.set(int(t[1]))
            if 'AskOnMoveVar~' in line:
                Vars.AskOnMoveVar.set(int(t[1]))
            if 'AskOnRecycleVar~' in line:
                Vars.AskOnRecycleVar.set(int(t[1]))
            if 'AskOnDeleteVar~' in line:
                Vars.AskOnDeleteVar.set(int(t[1]))
            if 'AskOnRenameVar~' in line:
                Vars.AskOnRenameVar.set(int(t[1]))
            if 'AskBeforeOverWriteDuringCopyVar~' in line:
                Vars.AskBeforeOverWriteDuringCopyVar.set(int(t[1]))
            if 'AskBeforeOverWriteDuringMoveVar~' in line:
                Vars.AskBeforeOverWriteDuringMoveVar.set(int(t[1]))
            if 'DestinationCheck01Var~' in line:
                Vars.DestinationCheck01Var.set(int(t[1]))
            if 'DestinationCheck02Var~' in line:
                Vars.DestinationCheck02Var.set(int(t[1]))
            if 'DestinationCheck03Var~' in line:
                Vars.DestinationCheck03Var.set(int(t[1]))
            if 'DestinationCheck04Var~' in line:
                Vars.DestinationCheck04Var.set(int(t[1]))
            if 'DestinationCheck05Var~' in line:
                Vars.DestinationCheck05Var.set(int(t[1]))
            if 'DestinationCheck06Var~' in line:
                Vars.DestinationCheck06Var.set(int(t[1]))
            if 'DestinationCheck07Var~' in line:
                Vars.DestinationCheck07Var.set(int(t[1]))
            if 'DestinationCheck08Var~' in line:
                Vars.DestinationCheck08Var.set(int(t[1]))
            if 'DestinationCheck09Var~' in line:
                Vars.DestinationCheck09Var.set(int(t[1]))
            if 'DestinationCheck10Var~' in line:
                Vars.DestinationCheck10Var.set(int(t[1]))
            if 'DestinationCheck11Var~' in line:
                Vars.DestinationCheck11Var.set(int(t[1]))
            if 'DestinationCheck12Var~' in line:
                Vars.DestinationCheck12Var.set(int(t[1]))
            if 'SystemEditorVar~' in line and len(t[1]) > 1:
                x = os.path.normpath(t[1].strip())
                Vars.SystemEditorVar.set(x)
            if 'SystemRenamerVar~' in line and len(t[1]) > 1:
                x = os.path.normpath(t[1].strip())
                Vars.SystemRenamerVar.set(x)
            if 'FileSourceEntry~' in line:
                x = os.path.normpath(t[1].strip())
                if x == '.':
                    x = ''
                FileSourceEntry.delete(0, tkinter.END)
                FileSourceEntry.insert(0, x)
            if 'SourcesList~' in line:
                FileSourceListbox.insert(tkinter.END, t[1].strip())
        else:
            # All lines with # in the first column are comments
            # All line that do not contain ~ are comments
            Vars.CommentsListVar.append(line)

    line_info(str(Vars.ClearSourceOnStartVar.get()))
    if Vars.ClearSourceOnStartVar.get():
        FileSourceEntry.delete(0, tkinter.END)

    VerifyPaths('Load')
    line_info(' '.join(['Project opened:', Vars.ProjectFileNameVar.get()]))
# ------------------------------
# Saves a project file


def ProjectSave():
    line_info(' '.join(['ProjectSave', Vars.ProjectFileNameVar.get()]))
    if VerifyPaths('Save') != 0:
        if tkinter.messagebox.askyesno('Bad paths detected', 'Do you want to continue?') is False:
            line_info('Project saved aborted. Bad path detected.')
            return

    line_info(Vars.ProjectFileNameVar.get())

    Vars.ProjectFileNameVar.set(
        tkinter.filedialog.asksaveasfilename(
            defaultextension=Vars.ProjectFileExtensionVar.get(),
            filetypes=[('Project file', ''.join(['PyCopyMove*.',
                                                 Vars.ProjectFileExtensionVar.get()]),
                        ('All files', '*.*'))],
            initialdir=Vars.AuxDirectoryVar.get(),
            initialfile=''.join(['PyCopyMoveTk', Vars.ProjectFileExtensionVar.get()],
                                title='Save a PyCopyMoveTk project file',
                                parent=Main)))

    line_info(Vars.ProjectFileNameVar.get())
    Vars.ProjectFileNameVar.set(
        os.path.normpath(Vars.ProjectFileNameVar.get()))
    ProjectEntry.delete(0, tkinter.END)
    ProjectEntry.insert(0, Vars.ProjectFileNameVar.get())

    try:
        f = open(Vars.ProjectFileNameVar.get(), 'w')
    except IOError:
        tkinter.messagebox.showerror('Project file error',
                                     os.linesep.join(['Unable to open requested file.>>',
                                                      Vars.ProjectFileNameVar.get(), '<<']))

    if not Vars.ProjectFileNameVar.get():
        return

    f.write(''.join(['PyCopyMoveTk.py project file ', sys.platform, os.linesep]))
    for item in Vars.CommentsListVar:
        f.write(item)
    f.write(''.join(['DestinationEntry01~', DestinationEntry01.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry02~', DestinationEntry02.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry03~', DestinationEntry03.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry04~', DestinationEntry04.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry05~', DestinationEntry05.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry06~', DestinationEntry06.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry07~', DestinationEntry07.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry08~', DestinationEntry08.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry09~', DestinationEntry09.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry10~', DestinationEntry10.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry11~', DestinationEntry11.get().strip(), os.linesep]))
    f.write(''.join(['DestinationEntry12~', DestinationEntry12.get().strip(), os.linesep]))
    f.write(''.join(['KeepFlagsCheckVar~', str(Vars.KeepFlagsCheckVar.get()), os.linesep]))
    f.write(''.join(['CheckSourceOnStartVar~', str(Vars.CheckSourceOnStartVar.get()), os.linesep]))
    f.write(''.join(['ClearSourceOnStartVar~', str(Vars.ClearSourceOnStartVar.get()), os.linesep]))
    f.write(''.join(['AskOnCopyVar~', str(Vars.AskOnCopyVar.get()), os.linesep]))
    f.write(''.join(['AskOnMoveVar~', str(Vars.AskOnMoveVar.get()), os.linesep]))
    f.write(''.join(['AskOnRecycleVar~', str(Vars.AskOnRecycleVar.get()), os.linesep]))
    f.write(''.join(['AskOnDeleteVar~', str(Vars.AskOnDeleteVar.get()), os.linesep]))
    f.write(''.join(['AskOnRenameVar~', str(Vars.AskOnRenameVar.get()), os.linesep]))
    f.write(''.join(['AskBeforeOverWriteDuringCopyVar~', str(Vars.AskBeforeOverWriteDuringCopyVar.get()), os.linesep]))
    f.write(''.join(['AskBeforeOverWriteDuringMoveVar~', str(Vars.AskBeforeOverWriteDuringMoveVar.get()), os.linesep]))
    f.write(''.join(['DestinationCheck01Var~', str(Vars.DestinationCheck01Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck02Var~', str(Vars.DestinationCheck02Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck03Var~',
            str(Vars.DestinationCheck03Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck04Var~',
            str(Vars.DestinationCheck04Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck05Var~',
            str(Vars.DestinationCheck05Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck06Var~',
            str(Vars.DestinationCheck06Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck07Var~',
            str(Vars.DestinationCheck07Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck08Var~',
            str(Vars.DestinationCheck08Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck09Var~',
            str(Vars.DestinationCheck09Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck10Var~',
                     str(Vars.DestinationCheck10Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck11Var~',
                     str(Vars.DestinationCheck11Var.get()), os.linesep]))
    f.write(''.join(['DestinationCheck12Var~',
                     str(Vars.DestinationCheck12Var.get()), os.linesep]))
    f.write(''.join(['SystemEditorVar~' + Vars.SystemEditorVar.get(), os.linesep]))
    f.write(''.join(['SystemRenamerVar~' + Vars.SystemRenamerVar.get(), os.linesep]))
    f.write(''.join(['FileSourceEntry~', FileSourceEntry.get().strip(), os.linesep]))
    for item in FileSourceListbox.get(0, tkinter.END):
        f.write(''.join(['SourcesList~', item]))
    f.close()
    line_info(' '.join(['Project saved:', Vars.ProjectFileNameVar.get()]))
# ------------------------------


def sha1file(filename):
    sha1 = hashlib.sha1()
    f = open(filename, 'rb')
    try:
        sha1.update(f.read())
    except shutil.Error as e:
        line_info(' '.join(['whoops ', str(e)]))
    finally:
        f.close()
    return sha1.hexdigest()
# ------------------------------


# Allow the user to browse for a file to use as the source file
def BrowseSourceFile():

    xx = FileSourceEntry.get()
    if not os.path.isdir(xx):
        xx = os.path.dirname(xx)
    Vars.FileNameListVar = []
    filenames = tkinter.filedialog.askopenfilenames(
        initialdir=xx,
        filetypes=[('All files', '*.*')],
        title='Select a file',
        parent=Main)

    for Src in filenames:
        if os.path.exists(Src):
            Vars.FileNameListVar.extend([Src])
    FileSourceEntry.delete(0, tkinter.END)
    if len(Vars.FileNameListVar) == 1:
        FileSourceEntry.insert(0, Src)
    else:
        FileSourceEntry.insert(
            0, str(len(Vars.FileNameListVar)) + ' source files detected')
    Vars.StatusVar.set(' '.join([str(len(Vars.FileNameListVar)),
                                 'source files detected']))
    line_info(' '.join(['Browse source file: ',
                        str(Vars.FileNameListVar)]))
# ------------------------------
# Allow the user to browse for a destination directory to use


def BrowseDestinationFile(Destination):  # noqa: C901
    temp = ''
    if Destination == '01':
        temp = DestinationEntry01.get()
    elif Destination == '02':
        temp = DestinationEntry02.get()
    elif Destination == '03':
        temp = DestinationEntry03.get()
    elif Destination == '04':
        temp = DestinationEntry04.get()
    elif Destination == '05':
        temp = DestinationEntry05.get()
    elif Destination == '06':
        temp = DestinationEntry06.get()
    elif Destination == '07':
        temp = DestinationEntry07.get()
    elif Destination == '08':
        temp = DestinationEntry08.get()
    elif Destination == '09':
        temp = DestinationEntry09.get()
    elif Destination == '10':
        temp = DestinationEntry10.get()
    elif Destination == '11':
        temp = DestinationEntry11.get()
    elif Destination == '12':
        temp = DestinationEntry12.get()
    if not os.path.isdir(temp):
        tkinter.messagebox.showerror('Destination error',
                                     os.linesep.join(['Destination directory does not exist',
                                                      temp]))
        line_info(os.linesep.join(['Destination error. Current destination directory does not exist.',
                                   temp]))

    DestinationName = tkinter.filedialog.askdirectory(
        initialdir=temp,
        parent=Main,
        title='Select a destination directory',
        mustexist=True)

    if len(DestinationName) < 1:
        return  # User choose cancel

    line_info(' '.join(['Browse destination file:',
                        Destination,
                        DestinationName]))
    if DestinationName:
        DestinationName = os.path.normpath(DestinationName)
        if Destination == '01':
            DestinationEntry01.delete(0, tkinter.END)
            DestinationEntry01.insert(0, DestinationName)
            Vars.DestinationCheck01Var.set(1)
        elif Destination == '02':
            DestinationEntry02.delete(0, tkinter.END)
            DestinationEntry02.insert(0, DestinationName)
            Vars.DestinationCheck02Var.set(1)
        elif Destination == '03':
            DestinationEntry03.delete(0, tkinter.END)
            DestinationEntry03.insert(0, DestinationName)
            Vars.DestinationCheck03Var.set(1)
        elif Destination == '04':
            DestinationEntry04.delete(0, tkinter.END)
            DestinationEntry04.insert(0, DestinationName)
            Vars.DestinationCheck04Var.set(1)
        elif Destination == '05':
            DestinationEntry05.delete(0, tkinter.END)
            DestinationEntry05.insert(0, DestinationName)
            Vars.DestinationCheck05Var.set(1)
        elif Destination == '06':
            DestinationEntry06.delete(0, tkinter.END)
            DestinationEntry06.insert(0, DestinationName)
            Vars.DestinationCheck06Var.set(1)
        elif Destination == '07':
            DestinationEntry07.delete(0, tkinter.END)
            DestinationEntry07.insert(0, DestinationName)
            Vars.DestinationCheck07Var.set(1)
        elif Destination == '08':
            DestinationEntry08.delete(0, tkinter.END)
            DestinationEntry08.insert(0, DestinationName)
            Vars.DestinationCheck08Var.set(1)
        elif Destination == '09':
            DestinationEntry09.delete(0, tkinter.tkinter.END)
            DestinationEntry09.insert(0, DestinationName)
            Vars.DestinationCheck09Var.set(1)
        elif Destination == '10':
            DestinationEntry10.delete(0, tkinter.END)
            DestinationEntry10.insert(0, DestinationName)
            Vars.DestinationCheck10Var.set(1)
        elif Destination == '11':
            DestinationEntry11.delete(0, tkinter.END)
            DestinationEntry11.insert(0, DestinationName)
            Vars.DestinationCheck11Var.set(1)
        elif Destination == '12':
            DestinationEntry12.delete(0, tkinter.END)
            DestinationEntry12.insert(0, DestinationName)
            Vars.DestinationCheck12Var.set(1)

# ------------------------------
# Does the copy or move of the source file to the destination location


def CopyOrMoveActions(Action, Src, Dest):  # noqa: C901
    # remove leading and trailing double quotes
    Src = Src.strip('\n').replace('\"', '')
    # remove leading and trailing double quotes
    Dest = Dest.strip('\n').replace('\"', '')
    if not os.path.isfile(Src):
        tkinter.messagebox.showerror('Source error',
                                     os.linesep.join(['Source is not a file or does not exist.',
                                                      Src]))
        line_info(' '.join([Action,
                            'Source is not a file or does not exist:',
                            Src]))
        return
    if not os.path.isdir(Dest):
        tkinter.messagebox.showerror('Destination error',
                                     ' '.join(['Destination is not a directory',
                                               Dest]))
        line_info(' '.join([Action,
                           'Destination error. Destination is not a directory:',
                            Dest]))
        return

    if Action == 'Copy':
        if Vars.AskOnCopyVar.get():
            if not tkinter.messagebox.askyesno('Proceed with copy?',
                                               os.linesep.join(['Proceed with copy?',
                                                                'Source: ', Src,
                                                                'Destination: ', Dest])):
                line_info(' '.join([Action,
                                    'aborted by user',
                                    Src,
                                    Dest]))
                return

        if Vars.AskBeforeOverWriteDuringCopyVar.get():
            if os.path.isfile(os.path.join(Dest, os.path.split(Src)[1])):
                # print(MyTrace(GFI(CF())),os.path.join(Dest))
                if not tkinter.messagebox.askyesno('Source file exists',
                                                   os.linesep.join([Dest,
                                                                    'Source file exists in destination.',
                                                                    'Overwrite?'])):
                    line_info(' '.join(['Copy overwrite aborted by user.', Src, Dest]))
                    return
        try:
            if Vars.KeepFlagsCheckVar.get():
                shutil.copy2(Src, Dest)  # Copy without flags
            else:
                shutil.copy(Src, Dest)  # Copy with flags
        except shutil.Error as e:
            line_info(' '.join([Action, 'error. Error: %s' % e]))
            tkinter.messagebox.showerror('Copy error', e)
        except OSError as e:
            line_info(' '.join([Action, 'error: %s' % e]))
            tkinter.messagebox.showerror('Copy error', e)

    if Action == 'Move':
        if Vars.AskOnMoveVar.get():
            if not tkinter.messagebox.askyesno('Move file',
                                               'Proceed with move?\nSource: ' + Src + '\nDestination: ' + Dest):
                line_info(os.linesep.join([Action,
                                           'aborted by user.',
                                           Src,
                                           Dest]))
                return

        DestFileName = os.path.join(Dest, os.path.split(Src)[1])
        if os.path.isfile(DestFileName):
            if Vars.AskBeforeOverWriteDuringMoveVar.get():
                if not tkinter.messagebox.askyesno('Move question',
                                                   os.linesep.join(['Source file exists in destination.',
                                                                    'Overwrite?',
                                                                    FileStats(DestFileName, Short=True)])):
                    line_info(' '.join(['Move overwrite aborted. ', Src, Dest]))
                    return
            line_info(os.linesep.join(['Move overwrite dest file removed.',
                                       Src,
                                       DestFileName]))
            RemoveAFile(os.path.join(Dest, os.path.split(Src)[1]), Trash=True)
            send2trash(os.path.join(Dest, os.path.split(Src)[1]))

        try:
            shutil.move(Src, Dest)
        except shutil.Error as e:
            line_info(os.linesep.join([Action,
                                       'error. Error: %s' % e]))
            tkinter.messagebox.showerror('Move error\n', e)
        except OSError as e:
            line_info(os.linesep.join([Action,
                                       'error: %s' % e]))
            tkinter.messagebox.showerror('Move error\n', e)
    line_info(os.linesep.join([' '.join([Action,
                                         'Source:',
                                         Src,
                                         'Destination:',
                                         Dest])]))
# ------------------------------
# Handles multiple source files


def NextSource():
    try:
        Src = Vars.FileNameListVar.pop()
    except Exception as e:
        line_info('Nothing in list')
        Vars.StatusVar.set(' '.join(['Nothing in list', str(e)]))
        FileSourceEntry.delete(0, tkinter.END)
        FileSourceEntry.insert(0, 'Nothing in list')
        return
    line_info(Src)
    if os.path.exists(Src):
        Vars.StatusVar.set(Src)
        FileSourceEntry.delete(0, tkinter.END)
        FileSourceEntry.insert(0, Src)
    else:
        line_info(' '.join([Src, 'is not a valid file']))

# ------------------------------
# Tests to see where to copy or move the source file to
# Multiple destinations are valid


def CopyOrMove(Action):  # noqa: C901
    count = 0
    Src = FileSourceEntry.get()
    if Vars.DestinationCheck01Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry01.get())
        count += 1
    if Vars.DestinationCheck02Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry02.get())
        count += 1
    if Vars.DestinationCheck03Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry03.get())
        count += 1
    if Vars.DestinationCheck04Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry04.get())
        count += 1
    if Vars.DestinationCheck05Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry05.get())
        count += 1
    if Vars.DestinationCheck06Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry06.get())
        count += 1
    if Vars.DestinationCheck07Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry07.get())
        count += 1
    if Vars.DestinationCheck08Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry08.get())
        count += 1
    if Vars.DestinationCheck09Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry09.get())
        count += 1
    if Vars.DestinationCheck10Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry10.get())
        count += 1
    if Vars.DestinationCheck11Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry11.get())
        count += 1
    if Vars.DestinationCheck12Var.get():
        CopyOrMoveActions(Action, Src, DestinationEntry12.get())
        count += 1
    if count == 0:
        line_info(' '.join(['Copy Or Move. No destinations specified', Src]))
        tkinter.messagebox.showinfo(
            'Copy Or Move', ' '.join(['No destinations specified', os.linesep, Src]))
# ------------------------------
# Does the copy or move of the source file to the destination location


def DeleteRecycleRenameInfo(Action):  # noqa: C901
    Src = FileSourceEntry.get()
    # remove leading and trailing double quotes
    Src = Src.strip('\n').replace('\"', '')

    if not os.path.isfile(Src) and Action != 'Info':
        line_info(' '.join([Action, 'Source is not a file', Src]))
        tkinter.messagebox.showerror(
            'Source error', 'Source is not a file\n' + Src)
        return

    line_info(' '.join([Action, 'Source: ', Src]))

    if Action == 'Recycle':
        if Vars.AskOnRecycleVar.get():
            if not tkinter.messagebox.askyesno('Recycle',
                                               os.linesep.join(['Recycle may not work unless drive is local!',
                                                                'Proceed with recycle?',
                                                                'Source: ',
                                                                Src])):
                line_info(' '.join([Action,
                                    'file abort by user. ',
                                    Src]))
                return
        try:
            send2trash(Src)
            RemoveAFile(Src, Trash=True)
            line_info(' '.join([Action, 'Source:', Src]))
        except OSError as e:
            line_info(' '.join([Action, 'file error: %s' % e]))

    if Action == 'Delete':
        if Vars.AskOnDeleteVar.get():
            if not tkinter.messagebox.askyesno('Delete file',
                                               ' '.join(['Proceed with delete?\nSource:',
                                                         Src])):
                line_info(' '.join([Action,
                                   'file abort by user. ',
                                    Src]))
                return
        try:
            # os.remove(Src)
            RemoveAFile(Src, Trash=False)
            line_info(' '.join([Action, 'Source:', Src]))
        except OSError as e:
            line_info(' '.join([Action, 'file error: %s' % e]))

    if Action == 'Rename':
        FileRenameInstance = FileRename()
        FileRenameInstance.RenameAFile()

    if Action == 'Info':
        line_info(' '.join([Action, 'File information',
                            Src]))
        tkinter.messagebox.showinfo('File info',
                                    FileStats(FileSourceEntry.get()))
# ------------------------------
# Fetch the current source file path from the file source list


def SourceListOperations(Operation):
    if not FileSourceListbox.curselection() and (Operation == 'Fetch' or Operation == 'Remove'):
        line_info('SourceListOperations: No item selected.')
        return

    if Operation == 'Fetch':
        FileSourceEntry.delete(0, tkinter.END)
        FileSourceEntry.insert(0, FileSourceListbox.get(
            FileSourceListbox.curselection()))
    elif Operation == 'Remove':
        FileSourceListbox.delete(FileSourceListbox.curselection())
    elif Operation == 'Add':
        if not os.path.isfile(FileSourceEntry.get()):  # verify the data is valid
            line_info(' '.join(['FileSourceEntry path is not valid.', FileSourceEntry.get()]))
            return
        FileSourceListbox.insert(tkinter.END, FileSourceEntry.get())

    # fetch the contents of FileSourceListbox
    temp_list = list(FileSourceListbox.get(0, tkinter.END))

    # remove duplicates
    temp_list = list(set(temp_list))

    # sort the listbox
    temp_list.sort(key=str.lower)

    # delete contents of present listbox
    FileSourceListbox.delete(0, tkinter.END)

    # load listbox with fixed up data
    for item in temp_list:
        FileSourceListbox.insert(tkinter.END, item)

    line_info(' '.join(['Source list operations', Operation]))
# ------------------------------
# Show any text file using the defined system editor


def ViewEditAnyFile():
    ViewEditName = tkinter.filedialog.askopenfilename(initialdir=Vars.AuxDirectoryVar.get(),
                                                      filetypes=[('All files', '*.*')],
                                                      title='Select a file',
                                                      parent=Main)

    if ViewEditName:
        line_info('View or Edit any file')
        StartFile(''.join([Vars.SystemEditorVar.get(),
                           'View or Edit any file',
                           os.path.normpath(ViewEditName)]))
# ------------------------------
# Toggle all destinations from selected to un-selected state


def ToggleDestinations():
    Vars.DestinationCheckToggleStateVar.set(
        not Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck01Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck02Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck03Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck04Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck05Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck06Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck07Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck08Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck09Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck10Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck11Var.set(Vars.DestinationCheckToggleStateVar.get())
    Vars.DestinationCheck12Var.set(Vars.DestinationCheckToggleStateVar.get())
    line_info(' '.join(['ToggleDestinations',
                        str(Vars.DestinationCheckToggleStateVar.get())]))
# ------------------------------


# Verify that destinations exist and are writeable
def VerifyPaths(Type=''):  # noqa: C901
    Results = ''

    if not SearchPath(Vars.SystemEditorVar.get()):
        Results = 'System editor' + os.linesep

    line_info(str(Vars.CheckSourceOnStartVar.get()))
    if Vars.CheckSourceOnStartVar.get():
        if len(FileSourceEntry.get()) > 0 and not os.path.isfile(FileSourceEntry.get()):
            Results += 'Source\n'

    if not os.path.isdir(DestinationEntry01.get()) or not os.access(DestinationEntry01.get(), os.W_OK):
        Results += 'Destination 1\n'
        DestinationEntry01.configure(fg="red")
    else:
        DestinationEntry01.configure(fg="green")

    if not os.path.isdir(DestinationEntry02.get()) or not os.access(DestinationEntry02.get(), os.W_OK):
        Results += 'Destination 2\n'
        DestinationEntry02.configure(fg="red")
    else:
        DestinationEntry02.configure(fg="green")
    if not os.path.isdir(DestinationEntry03.get()) or not os.access(DestinationEntry03.get(), os.W_OK):
        Results += 'Destination 3\n'
        DestinationEntry03.configure(fg="red")
    else:
        DestinationEntry03.configure(fg="green")
    if not os.path.isdir(DestinationEntry04.get()) or not os.access(DestinationEntry04.get(), os.W_OK):
        Results += 'Destination 4\n'
        DestinationEntry04.configure(fg="red")
    else:
        DestinationEntry04.configure(fg="green")
    if not os.path.isdir(DestinationEntry05.get()) or not os.access(DestinationEntry05.get(), os.W_OK):
        Results += 'Destination 5\n'
        DestinationEntry05.configure(fg="red")
    else:
        DestinationEntry05.configure(fg="green")
    if not os.path.isdir(DestinationEntry06.get()) or not os.access(DestinationEntry06.get(), os.W_OK):
        Results += 'Destination 6\n'
        DestinationEntry06.configure(fg="red")
    else:
        DestinationEntry06.configure(fg="green")
    if not os.path.isdir(DestinationEntry07.get()) or not os.access(DestinationEntry07.get(), os.W_OK):
        Results += 'Destination 7\n'
        DestinationEntry07.configure(fg="red")
    else:
        DestinationEntry07.configure(fg="green")
    if not os.path.isdir(DestinationEntry08.get()) or not os.access(DestinationEntry08.get(), os.W_OK):
        Results += 'Destination 8\n'
        DestinationEntry08.configure(fg="red")
    else:
        DestinationEntry08.configure(fg="green")
    if not os.path.isdir(DestinationEntry09.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 9\n'
        DestinationEntry09.configure(fg="red")
    else:
        DestinationEntry09.configure(fg="green")
    if not os.path.isdir(DestinationEntry10.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 10\n'
        DestinationEntry10.configure(fg="red")
    else:
        DestinationEntry10.configure(fg="green")
    if not os.path.isdir(DestinationEntry11.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 11\n'
        DestinationEntry11.configure(fg="red")
    else:
        DestinationEntry11.configure(fg="green")
    if not os.path.isdir(DestinationEntry12.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 12\n'
        DestinationEntry12.configure(fg="red")
    else:
        DestinationEntry12.configure(fg="green")
    # if len(Results) != 0:
    #    xx=tkinter.messagebox.showerror('Invalid path(s)', 'Invalid path(s):\n' + Results)
    # else:
    #    if (Type != 'Save' and Type != 'Load'):
    #        tkinter.messagebox.showinfo('All paths valid', 'All paths valid!')
    return(len(Results))  # 0 is No bad paths
# ------------------------------
# Some debug stuff


def About():
    line_info(main.Vars.StartUpDirectoryVar.get())
    tkinter.messagebox.showinfo('About',
                                os.linesep.join([main.Vars.StartUpDirectoryVar.get(),
                                                 Main.geometry(),
                                                 ''.join([str(Main.winfo_screenwidth()),
                                                          'x',
                                                          str(Main.winfo_screenheight())]),
                                                 ' '.join(['Python version:',
                                                           platform.python_version()]),
                                                 ' '.join(['Platform:',
                                                           platform.platform()]),
                                                 ' '.join(['PyCopyMoveTk version:',
                                                           Vars.ProgramVersionNumber.get()])
                                                 ]))

# ------------------------------
# The help file


def Help():
    line_info(main.Vars.StartUpDirectoryVar.get())
    Vars.StatusVar.set('Help')

    try:
        f = open(Vars.HelpFileVar.get(), 'r')
    except IOError:
        tkinter.messagebox.showerror('Help file error',
                                     'Requested file does not exist.\n>>' + Vars.HelpFileVar.get() + '<<')
        return
    data = f.read()
    f.close()

    MyMessageBox(Title='PyCopyMoveTk help',
                 TextMessage=data,
                 Buttons=['OK', 'Cancel'],
                 LabelText=['This is a test label'],
                 fgColor='pink',
                 bgColor='black',
                 Center=None,
                 Geometry='500x300+1300+20')

# ------------------------------
# These functions are used for the menu popup for the source entry


def MakePopupmenu(w):
    global Popupmenu
    Popupmenu = tkinter.Menu(w, tearoff=0)
    Popupmenu.add_command(label="Cut")
    Popupmenu.add_command(label="Copy")
    Popupmenu.add_command(label="Paste")
    Popupmenu.add_command(label="Clear")
    Popupmenu.add_command(label="Select")


def ShowPopupmenu(e):
    w = e.widget
    Popupmenu.entryconfigure(
        "Cut", command=lambda: w.event_generate("<<Cut>>"))
    Popupmenu.entryconfigure(
        "Copy", command=lambda: w.event_generate("<<Copy>>"))
    Popupmenu.entryconfigure(
        "Paste", command=lambda: w.event_generate("<<Paste>>"))
    Popupmenu.entryconfigure("Clear", command=lambda: w.delete(0, tkinter.tkinter.END))
    Popupmenu.entryconfigure(
        "Select", command=lambda: w.select_range(0, tkinter.tkinter.END))
    Popupmenu.tk.call("tk_popup", Popupmenu, e.x_root, e.y_root)

# ------------------------------


# Build all the gui and start the program
Vars.StatusVar.set('Starting')

menubar = tkinter.Menu(Main)
Main['menu'] = menubar
ProjectsMenu = tkinter.Menu(menubar)
SourceMenu = tkinter.Menu(menubar)
OtherMenu = tkinter.Menu(menubar)
OptionsMenu = tkinter.Menu(menubar)
HelpMenu = tkinter.Menu(menubar)

menubar.add_cascade(menu=ProjectsMenu,
                    label='Project')
ProjectsMenu.add_command(label='Load',
                         command=ProjectLoad)
ProjectsMenu.add_command(label='Save',
                         command=ProjectSave)
ProjectsMenu.add_command(label='Edit',
                         command=lambda: ShowEditFile(ProjectEntry.get()))

menubar.add_cascade(menu=SourceMenu, label='Source')
SourceMenu.add_command(label='Browse for source file(s)',
                       command=BrowseSourceFile)
SourceMenu.add_command(label='Add source to list',
                       command=lambda: SourceListOperations('Add'))
SourceMenu.add_command(label='Remove source from list',
                       command=lambda: SourceListOperations('Remove'))
SourceMenu.add_command(label='Fetch source from list',
                       command=lambda: SourceListOperations('Fetch'))

menubar.add_cascade(menu=OtherMenu, label='Other')
OtherMenu.add_command(label='Get Clipboard', command=GetClipBoard)
OtherMenu.add_command(label='View log',
                      command=lambda: StartFile(Vars.SystemEditorVar.get(), arg1=Vars.LogFileNameVar.get()))
OtherMenu.add_command(label='ViewEdit any file', command=ViewEditAnyFile)
OtherMenu.add_command(label='Verify paths', command=VerifyPaths)
OtherMenu.add_command(label='Show disk space', command=DiskSpace)

menubar.add_cascade(menu=OptionsMenu, label='Options')
OptionsMenu.add_checkbutton(
    label='Keep flags on copy and move', variable=Vars.KeepFlagsCheckVar)
OptionsMenu.add_checkbutton(
    label='Check source on startup', variable=Vars.CheckSourceOnStartVar)
OptionsMenu.add_checkbutton(
    label='Clear source on startup', variable=Vars.ClearSourceOnStartVar)
OptionsMenu.add_checkbutton(label='Ask on copy', variable=Vars.AskOnCopyVar)
OptionsMenu.add_checkbutton(label='Ask on move', variable=Vars.AskOnMoveVar)
OptionsMenu.add_checkbutton(label='Ask on recycle',
                            variable=Vars.AskOnRecycleVar)
OptionsMenu.add_checkbutton(label='Ask on delete',
                            variable=Vars.AskOnDeleteVar)
OptionsMenu.add_checkbutton(label='Ask on rename',
                            variable=Vars.AskOnRenameVar)
OptionsMenu.add_checkbutton(label='Ask before overwrite during copy',
                            variable=Vars.AskBeforeOverWriteDuringCopyVar)
OptionsMenu.add_checkbutton(label='Ask before overwrite during move',
                            variable=Vars.AskBeforeOverWriteDuringMoveVar)

menubar.add_cascade(menu=HelpMenu,
                    label='Help')
HelpMenu.add_command(label='About',
                     command=About)
HelpMenu.add_command(label='Help',
                     command=Help)

# ---------------
FileFrame1 = tkinter.Frame(Main,
                           relief=tkinter.SUNKEN,
                           bd=1)
FileFrame1.pack(fill=tkinter.X,
                side=tkinter.TOP)
tkinter.Label(FileFrame1,
              text='Source file',
              font=("Helvetica", 15)).pack(side=tkinter.tkinter.TOP,
                                           fill=tkinter.BOTH,
                                           expand=tkinter.YES)

BrowseSourceButton = tkinter.Button(FileFrame1,
                                    text='Browse',
                                    command=BrowseSourceFile, width=8)
BrowseSourceButton.pack(side=tkinter.LEFT)
ToolTip(BrowseSourceButton, 'Browse for one or more source file')
FileSourceEntry = tkinter.Entry(FileFrame1,
                                relief=tkinter.SUNKEN,
                                bd=2)
FileSourceEntry.pack(fill=tkinter.x)
ToolTip(FileSourceEntry, 'Path for the source file')

MakePopupmenu(Main)
FileSourceEntry.bind_class("Entry",
                           "<Button-3><ButtonRelease-3>",
                           ShowPopupmenu)

# ---------------
FileFrame2 = tkinter.Frame(Main,
                           relief=tkinter.SUNKEN,
                           bd=1)
FileFrame2.pack(side=tkinter.tkinter.TOP,
                fill=tkinter.BOTH,
                expand=tkinter.YES)

FileFrame3 = tkinter.Frame(FileFrame2,
                           relief=tkinter.SUNKEN,
                           bd=1,
                           width=10)
FileFrame3.pack(side=tkinter.LEFT)
ToolTip(FileFrame3, 'Operations to the source list')

tkinter.Button(FileFrame3,
               text='Add',
               width=8,
               command=lambda: SourceListOperations('Add')).pack(side=tkinter.tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES)
tkinter.Button(FileFrame3,
               text='Fetch',
               width=8,
               command=lambda: SourceListOperations('Fetch')).pack(side=tkinter.tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES)
tkinter.Button(FileFrame3,
               text='Remove',
               width=8,
               command=lambda: SourceListOperations('Remove')).pack(side=tkinter.tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES)

FileFrame4 = tkinter.Frame(FileFrame2,
                           relief=tkinter.SUNKEN,
                           bd=1)
FileFrame4.pack(side=tkinter.LEFT,
                fill=tkinter.X,
                expand=tkinter.YES)

yScroll = tkinter.Scrollbar(FileFrame4,
                            orient=tkinter.VERTICAL)
yScroll.pack(side=tkinter.RIGHT,
             fill=tkinter.Y)
xScroll = tkinter.Scrollbar(FileFrame4,
                            orient=tkinter.HORIZONTAL)
xScroll.pack(side=tkinter.BOTTOM,
             fill=tkinter.x)
FileSourceListbox = tkinter.Listbox(FileFrame4,
                                    height=6,
                                    yscrollcommand=yScroll.set,
                                    xscrollcommand=xScroll.set)
FileSourceListbox.pack(fill=tkinter.BOTH,
                       expand=tkinter.YES)

FileSourceListbox.bind('<Double-Button-1>',
                       lambda x: SourceListOperations('Fetch'))
ToolTip(FileSourceListbox, 'Saved list of source files. Double tkinter.LEFT click to fetch.')
yScroll.config(command=FileSourceListbox.yview)
xScroll.config(command=FileSourceListbox.xview)

OperationFrame = tkinter.Frame(Main,
                               relief=tkinter.SUNKEN, bd=1)
OperationFrame.pack(side=tkinter.tkinter.TOP,
                    fill=tkinter.X,
                    expand=tkinter.YES)
ToolTip(OperationFrame, 'Click a button to perform action')
tkinter.Label(OperationFrame,
              text='Operations',
              font=("Helvetica", 15)).pack(side=tkinter.tkinter.TOP,
                                           fill=tkinter.BOTH,
                                           expand=tkinter.YES)

tkinter.Button(OperationFrame,
               width=10,
               text='Copy',
               command=lambda: CopyOrMove('Copy')).pack(side=tkinter.LEFT)
tkinter.Button(OperationFrame,
               width=10,
               text='Move',
               command=lambda: CopyOrMove('Move')).pack(side=tkinter.LEFT)
tkinter.Button(OperationFrame,
               width=10,
               text='Recycle',
               command=lambda: DeleteRecycleRenameInfo('Recycle')).pack(side=tkinter.LEFT)
tkinter.Button(OperationFrame,
               width=10,
               text='Delete',
               command=lambda: DeleteRecycleRenameInfo('Delete')).pack(side=tkinter.LEFT)
tkinter.Button(OperationFrame,
               width=10,
               text='Rename',
               command=lambda: DeleteRecycleRenameInfo('Rename')).pack(side=tkinter.LEFT)
tkinter.Button(OperationFrame,
               width=10,
               text='Info',
               command=lambda: DeleteRecycleRenameInfo('Info')).pack(side=tkinter.LEFT)
tkinter.Button(OperationFrame,
               width=10,
               text='Next',
               command=lambda: NextSource()).pack(side=tkinter.LEFT)
# ------------------------------
DestinationFrame = tkinter.Frame(Main,
                                 relief=tkinter.SUNKEN,
                                 bd=1)
DestinationFrame.pack(fill=tkinter.x)
ToolTip(DestinationFrame, 'Chose/add a destination path')
tkinter.Label(DestinationFrame,
              text='Destination directories',
              font=("Helvetica", 15)).pack(side=tkinter.tkinter.TOP,
                                           fill=tkinter.BOTH,
                                           expand=tkinter.YES)

DestinationFrame00 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN,
                                   bd=1)
DestinationFrame00.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
ToggleAllButton = tkinter.Button(DestinationFrame00,
                                 width=15,
                                 text='Toggle all',
                                 command=ToggleDestinations)
ToggleAllButton.pack(padx=100,
                     pady=5,
                     side=tkinter.LEFT)
ToolTip(ToggleAllButton, 'Toggle all destination selects')

VerifyPathsButton = tkinter.Button(DestinationFrame00,
                                   width=15,
                                   text='Verify paths',
                                   command=VerifyPaths)
VerifyPathsButton.pack(padx=5,
                       pady=5,
                       side=tkinter.LEFT)
ToolTip(VerifyPathsButton, 'Verify all destination paths')

DestinationFrame01 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN, bd=1)
DestinationFrame01.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame01,
                    text='Dest01',
                    variable=Vars.DestinationCheck01Var).pack(side=tkinter.LEFT)
tkinter.Button(DestinationFrame01,
               text='Browse',
               command=lambda: BrowseDestinationFile('01')).pack(side=tkinter.LEFT)
DestinationEntry01 = tkinter.Entry(DestinationFrame01)
DestinationEntry01.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame02 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN,
                                   bd=1)
DestinationFrame02.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame02,
                    text='Dest02',
                    variable=Vars.DestinationCheck02Var).pack(side=tkinter.LEFT)
tkinter.Button(DestinationFrame02,
               text='Browse',
               command=lambda: BrowseDestinationFile('02')).pack(side=tkinter.LEFT)
DestinationEntry02 = tkinter.Entry(DestinationFrame02)
DestinationEntry02.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame03 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN,
                                   bd=1)
DestinationFrame03.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame03,
                    text='Dest03',
                    variable=Vars.DestinationCheck03Var).pack(side=tkinter.LEFT)
tkinter.Button(DestinationFrame03,
               text='Browse',
               command=lambda: BrowseDestinationFile('03')).pack(side=tkinter.LEFT)
DestinationEntry03 = tkinter.Entry(DestinationFrame03)
DestinationEntry03.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame04 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN, bd=1)
DestinationFrame04.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame04,
                    text='Dest04',
                    variable=Vars.DestinationCheck04Var).pack(side=tkinter.LEFT)
tkinter.Button(DestinationFrame04,
               text='Browse',
               command=lambda: BrowseDestinationFile('04')).pack(side=tkinter.LEFT)
DestinationEntry04 = tkinter.Entry(DestinationFrame04)
DestinationEntry04.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame05 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN, bd=1)
DestinationFrame05.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame05,
                    text='Dest05',
                    variable=Vars.DestinationCheck05Var).pack(side=tkinter.LEFT)
tkinter.Button(DestinationFrame05,
               text='Browse',
               command=lambda: BrowseDestinationFile('05')).pack(side=tkinter.LEFT)
DestinationEntry05 = tkinter.Entry(DestinationFrame05)
DestinationEntry05.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame06 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN,
                                   bd=1)
DestinationFrame06.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame06,
                    text='Dest06',
                    variable=Vars.DestinationCheck06Var).pack(side=tkinter.LEFT)
tkinter.Button(DestinationFrame06,
               text='Browse',
               command=lambda: BrowseDestinationFile('06')).pack(side=tkinter.LEFT)
DestinationEntry06 = tkinter.Entry(DestinationFrame06)
DestinationEntry06.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame07 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN, bd=1)
DestinationFrame07.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame07,
                    text='Dest07',
                    variable=Vars.DestinationCheck07Var).pack(side=tkinter.LEFT)
tkinter.Button(DestinationFrame07,
               text='Browse',
               command=lambda: BrowseDestinationFile('07')).pack(side=tkinter.LEFT)
DestinationEntry07 = tkinter.Entry(DestinationFrame07)
DestinationEntry07.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame08 = tkinter.Frame(DestinationFrame, relief=tkinter.SUNKEN, bd=1)
DestinationFrame08.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame08,
                    text='Dest08',
                    variable=Vars.DestinationCheck08Var).pack(side=tkinter.LEFT)
tkinter.tkinter.Button(DestinationFrame08,
                       text='Browse',
                       command=lambda: BrowseDestinationFile('08')).pack(side=tkinter.LEFT)
DestinationEntry08 = tkinter.Entry(DestinationFrame08)
DestinationEntry08.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame09 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN, bd=1)
DestinationFrame09.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame09,
                    text='Dest09',
                    variable=Vars.DestinationCheck09Var).pack(side=tkinter.LEFT)
tkinter.tkinter.Button(DestinationFrame09,
                       text='Browse',
                       command=lambda: BrowseDestinationFile('09')).pack(side=tkinter.LEFT)
DestinationEntry09 = tkinter.Entry(DestinationFrame09)
DestinationEntry09.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame10 = tkinter.Frame(DestinationFrame, relief=tkinter.SUNKEN, bd=1)
DestinationFrame10.pack(side=tkinter.tkinter.TOP, fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame10,
                    text='Dest10',
                    variable=Vars.DestinationCheck10Var).pack(side=tkinter.LEFT)
tkinter.tkinter.Button(DestinationFrame10,
                       text='Browse',
                       command=lambda: BrowseDestinationFile('10')).pack(side=tkinter.LEFT)
DestinationEntry10 = tkinter.Entry(DestinationFrame10)
DestinationEntry10.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame11 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN, bd=1)
DestinationFrame11.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.X)
tkinter.Checkbutton(DestinationFrame11,
                    text='Dest11',
                    variable=Vars.DestinationCheck11Var).pack(side=tkinter.LEFT)
tkinter.tkinter.Button(DestinationFrame11,
                       text='Browse',
                       command=lambda: BrowseDestinationFile('11')).pack(side=tkinter.LEFT)
DestinationEntry11 = tkinter.Entry(DestinationFrame11)
DestinationEntry11.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

DestinationFrame12 = tkinter.Frame(DestinationFrame,
                                   relief=tkinter.SUNKEN, bd=1)
DestinationFrame12.pack(side=tkinter.tkinter.TOP,
                        fill=tkinter.x)
tkinter.Checkbutton(DestinationFrame12,
                    text='Dest12',
                    variable=Vars.DestinationCheck12Var).pack(side=tkinter.LEFT)
tkinter.tkinter.Button(DestinationFrame12,
                       text='Browse',
                       command=lambda: BrowseDestinationFile('12')).pack(side=tkinter.LEFT)
DestinationEntry12 = tkinter.Entry(DestinationFrame12)
DestinationEntry12.pack(side=tkinter.LEFT,
                        fill=tkinter.X,
                        expand=tkinter.TRUE)

# ------------------------------
StatusFrame = tkinter.Frame(Main, relief=tkinter.SUNKEN, bd=1)
StatusFrame.pack(fill=tkinter.x)
tkinter.Label(StatusFrame, text='Status', font=("Helvetica", 15)).pack(
    side=tkinter.tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES)
Statuslabel = tkinter.Label(StatusFrame, textvariable=Vars.StatusVar, relief=tkinter.GROOVE)
Statuslabel.pack(side=tkinter.tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.x)
ToolTip(Statuslabel, 'Display status')
ProjectEntry = tkinter.Entry(StatusFrame)
ProjectEntry.pack(side=tkinter.tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.x)
ToolTip(ProjectEntry, 'Currently loaded project')
# ------------------------------

SetDefaults()  # Initialize the variables
StartUpStuff()
ParseCommandLine()
# ------------------------------
Vars.LogFileNameVar.set(os.path.join(
    Vars.StartUpDirectoryVar.get(), 'PyCopyMoveTk.log'))
# ------------------------------
Main.bind('<F1>', lambda e: Help())
Main.bind('<F2>', lambda e: About())
Main.bind('<F3>', lambda e: BrowseSourceFile())
Main.bind('<F4>', lambda e: ProjectLoad())
# Main.bind('<Configure>', lambda e:ShowResize(Main))

Main.minsize(400, 300)
Main.resizable(True, False)
Main.option_add('*Font', 'courier 10')
Main.title('PyCopyMoveTk')
Main.wm_iconname('PyCopyMoveTk')
Main.mainloop()
