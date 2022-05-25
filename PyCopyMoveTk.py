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
# http://www.shayanderson.com/linux/using-git-with-remote-repository.htm
#
import sys
import os
import time
import platform
import pprint

pp = pprint.PrettyPrinter(indent=4)

sys.path.append('.' + os.sep + 'auxfiles')
sys.path.append('.' + os.sep + 'DougModules')
sys.path.append('.' + os.sep + 'Send2Trash')
pp.pprint(sys.path)
from send2trash import send2trash
from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import argparse
import shutil
import re
import __main__ as main
#from inspect import currentframe, getframeinfo
from inspect import currentframe as CF
from inspect import getframeinfo as GFI

from ToolTip import ToolTip

from DougModules import SearchPath
from DougModules import MyTrace
from DougModules import MyMessageBox
from DougModules import Logger
from DougModules import StartFile
from DougModules import FileStats
from DougModules import DiskSpace
from DougModules import SetUpLogger
from DougModules import RemoveAFile
from DougModules import ShowResize

Main = tkinter.Tk()

from PyCopyMoveVars import Vars


#Debug
#import pdb
#pdb.set_trace()

Vars.ProgramVersionNumber.set('1.0.0')

#------------------------------
# Parse the command line

def ParseCommandLine():
    #print(MyTrace(GFI(CF())), 'ParseCommandLine')
    if len(sys.argv) == 1:
        return

    del sys.argv[0]  # Don't want the script name

    x = ''
    y = []
    y = [x.upper() for x in sys.argv]

    #print(MyTrace(GFI(CF())), y)

    if '-H' in y or '-HELP' in y:
        print(MyTrace(GFI(CF())), 'Help was found')
        Help()

    if '-A' in y or '-ABOUT' in y:
        print(MyTrace(GFI(CF())), 'About was found')
        About()

    if '-D' in y or '-DEBUG' in y:
        print(MyTrace(GFI(CF())), 'Debug was found')
        import pdb
        pdb.set_trace()

    if '-P' in y or '-PROJECT' in y:
        print(MyTrace(GFI(CF())), 'Project was found')
        ProjectLoad()

    for Src in sys.argv:
        if os.path.exists(Src):
            Vars.FileNameListVar.extend([Src])
            print(MyTrace(GFI(CF())), Src)

    FileSourceEntry.delete(0, END)
    FileSourceEntry.insert(
        0, str(len(Vars.FileNameListVar)) + ' source files detected')
    Vars.StatusVar.set(str(len(Vars.FileNameListVar)) +
                       ' source files detected')
    Logger(MyTrace(GFI(CF())), 'Browse source file: ' + str(Vars.FileNameListVar))

#------------------------------
# Set up defaults in case there is no project file
# Initialize the variables
# Written over by StartUpStuff and by ProjectLoad


def SetDefaults():
    #print(MyTrace(GFI(CF())), 'SetDefaults')
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
    FileSourceEntry.delete(0, END)
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

#------------------------------
# Initialize the program


def StartUpStuff():
    #-- Lots of startup stuff ------------------------------------
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
    SetUpLogger(Vars.LogFileNameVar.get())

    Logger(MyTrace(GFI(CF())), str(os.environ.get('OS')))
    Logger(MyTrace(GFI(CF())), str(platform.uname()))
    Logger(MyTrace(GFI(CF())), 'Number of argument(s): ' + str(len(sys.argv)))
    Logger(MyTrace(GFI(CF())), 'Argument List: ' + str(sys.argv))

    ProjectLoad('default')
    GetClipBoard()
#------------------------------
# Try to get source file from clipboard


def GetClipBoard():
    #print(MyTrace(GFI(CF())), 'GetClipBoard')
    try:
        temp = Main.clipboard_get()
        temp = temp.replace('"', '').strip()
        if os.path.isfile(temp):
            FileSourceEntry.delete(0, END)
            FileSourceEntry.insert(0, temp)
            Vars.StatusVar.set(temp)
            Logger(MyTrace(GFI(CF())), 'From clipboard: ' + temp)
        else:
            Logger(MyTrace(GFI(CF())), 'Invalid path from clipboard: ' + temp)
    except:
        Logger(MyTrace(GFI(CF())), 'No clipboard data')

#------------------------------
# This class handles file rename for the file info menu


class FileRename:
    RenameEntry = None
    BeforeFilename = ''
    AfterFilename = ''
    Path = ''
    Basename = ''
#------------------------------

    def Swapcase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, END)
        self.RenameEntry.insert(0, filename.swapcase())

    def Titlecase(self):
        filename = self.RenameEntry.get()

        def titlecase(s):
            return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                          lambda mo: mo.group(0)[0].upper() +
                          mo.group(0)[1:].lower(), s)
        self.RenameEntry.delete(0, END)
        self.RenameEntry.insert(0, titlecase(filename))

    def Uppercase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, END)
        self.RenameEntry.insert(0, filename.upper())
        self.RenameEntry.focus_set()

    def Lowercase(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, END)
        self.RenameEntry.insert(0, filename.lower())
        self.RenameEntry.focus_set()

    def Capitalize(self):
        filename = self.RenameEntry.get()
        self.RenameEntry.delete(0, END)
        self.RenameEntry.insert(0, filename.capitalize())
        self.RenameEntry.focus_set()

    def Done(self):  # Filename will always be the same
        self.AfterFilename = os.path.join(self.Path, self.RenameEntry.get())
        Logger(MyTrace(GFI(CF())), 'Rename. Before: %s  After: %s' %
               (self.BeforeFilename, self.AfterFilename))
        try:
            os.rename(self.BeforeFilename, self.AfterFilename)
        except OSError as e:
            Logger(MyTrace(GFI(CF())), 'Rename file error: %s' % e)
            tkinter.messagebox.showerror('Rename file error',
                                         'no can do' +
                                         '\nBefore filename:' + self.BeforeFilename +
                                         '\nAfter filename:' + self.AfterFilename +
                                         '\n\nReturn code: %s' % e)
        Vars.FileRenameTopLevelVar.withdraw()

    def Cancel(self):
        Vars.FileRenameTopLevelVar.withdraw()

    def RenameAFile(self):
        Vars.FileRenameTopLevelVar = Toplevel()
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

        FileRenameFrame1 = Frame(
            Vars.FileRenameTopLevelVar, relief=SUNKEN, bd=1)
        FileRenameFrame1.pack(side=TOP, fill=X)
        FileRenameFrame2 = Frame(
            Vars.FileRenameTopLevelVar, relief=SUNKEN, bd=1)
        FileRenameFrame2.pack(side=TOP, fill=X)
        FileRenameFrame3 = Frame(
            Vars.FileRenameTopLevelVar, relief=SUNKEN, bd=1)
        FileRenameFrame3.pack(side=TOP, fill=X)

        # Start here
        self.BeforeFilename = FileSourceEntry.get()
        self.Basename = os.path.basename(self.BeforeFilename)
        self.Path = os.path.dirname(self.BeforeFilename)

        Label(FileRenameFrame1, text=self.BeforeFilename).pack(fill=X)
        self.RenameEntry = Entry(FileRenameFrame1)
        self.RenameEntry.pack(fill=X)
        self.RenameEntry.delete(0, END)
        self.RenameEntry.insert(0, self.Basename)
        self.RenameEntry.focus_set()

        Button(FileRenameFrame2, text='Done', width=8,
               command=self.Done).pack(side=LEFT)
        Button(FileRenameFrame2, text='Cancel', width=8,
               command=self.Cancel).pack(side=LEFT)
        Button(FileRenameFrame2, text='Title', width=8,
               command=self.Titlecase).pack(side=LEFT)

        Button(FileRenameFrame3, text='Upper', width=8,
               command=self.Uppercase).pack(side=LEFT)
        Button(FileRenameFrame3, text='Lower', width=8,
               command=self.Lowercase).pack(side=LEFT)
        Button(FileRenameFrame3, text='Swap', width=8,
               command=self.Swapcase).pack(side=LEFT)
        Button(FileRenameFrame3, text='Capitalize', width=10,
               command=self.Capitalize).pack(side=LEFT)

#------------------------------
# Loads a project file
# Lines without a ~ in the line are ignored and may be used as comments
# Lines with # in position 0 may be used as comments


def ProjectLoad(LoadType='none'):
    #print(MyTrace(GFI(CF())),'ProjectLoad' , LoadType)
    if LoadType == 'default':
        Vars.ProjectFileNameVar.set(os.path.join(Vars.AuxDirectoryVar.get(),
                                                 'PyCopyMoveTk.' + Vars.ProjectFileExtensionVar.get()))
    else:
        Vars.ProjectFileNameVar.set(tkinter.filedialog.askopenfilename(
            defaultextension=Vars.ProjectFileExtensionVar.get(),
            filetypes=[('Project file', 'PyCopyMove*.' +
                        Vars.ProjectFileExtensionVar.get()), ('All files', '*.*')],
            initialdir=Vars.AuxDirectoryVar.get(),
            initialfile='PyCopyMoveTk.' + Vars.ProjectFileExtensionVar.get(),
            title='Load a PyCopyMoveTk project file',
            parent=Main))
    Vars.ProjectFileNameVar.set(
        os.path.normpath(Vars.ProjectFileNameVar.get()))

    Logger(MyTrace(GFI(CF())), 'Project Load ' + Vars.ProjectFileNameVar.get())

    ProjectEntry.delete(0, END)
    ProjectEntry.insert(0, Vars.ProjectFileNameVar.get())

    title = 'Select a file',
    try:
        f = open(Vars.ProjectFileNameVar.get(), 'r')
    except IOError:
        tkinter.messagebox.showerror('Project file error',
                                     'Requested file does not exist.\n>>' + Vars.ProjectFileNameVar.get() + '<<')
        return

    lines = f.readlines()
    f.close()
    try:
        if not 'PyCopyMoveTk.py project file ' + sys.platform in lines[0]:
            tkinter.messagebox.showerror('Project file error',
                                         'Not a valid project file.\nproject file' + '\n' + lines[0])
            Logger(MyTrace(GFI(CF())),
                   'PyCopyMoveTk.py project file ' + lines[0].strip())
            return
    except:
        tkinter.messagebox.showerror('Project file error',
                                     'Unable to read project file' + Vars.ProjectFileNameVar.get())
        Logger(MyTrace(GFI(CF())),
               'PyCopyMoveTk.py project file. Unable to read file')
        return

    # remove the first line so it won't be added to the comments list
    del lines[0]
    # Clear any widgets that need to be
    FileSourceListbox.delete(0, END)
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
                DestinationEntry01.delete(0, END)
                DestinationEntry01.insert(0, x)
            if 'DestinationEntry02~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry02.delete(0, END)
                DestinationEntry02.insert(0, x)
            if 'DestinationEntry03~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry03.delete(0, END)
                DestinationEntry03.insert(0, x)
            if 'DestinationEntry04~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry04.delete(0, END)
                DestinationEntry04.insert(0, x)
            if 'DestinationEntry05~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry05.delete(0, END)
                DestinationEntry05.insert(0, x)
            if 'DestinationEntry06~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry06.delete(0, END)
                DestinationEntry06.insert(0, x)
            if 'DestinationEntry07~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry07.delete(0, END)
                DestinationEntry07.insert(0, x)
            if 'DestinationEntry08~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry08.delete(0, END)
                DestinationEntry08.insert(0, x)
            if 'DestinationEntry09~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry09.delete(0, END)
                DestinationEntry09.insert(0, x)
            if 'DestinationEntry10~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry10.delete(0, END)
                DestinationEntry10.insert(0, x)
            if 'DestinationEntry11~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry11.delete(0, END)
                DestinationEntry11.insert(0, x)
            if 'DestinationEntry12~' in line:
                x = os.path.normpath(t[1].strip())
                DestinationEntry12.delete(0, END)
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
                FileSourceEntry.delete(0, END)
                FileSourceEntry.insert(0, x)
            if 'SourcesList~' in line:
                FileSourceListbox.insert(END, t[1].strip())
        else:
            # All lines with # in the first column are comments
            # All line that do not contain ~ are comments
            Vars.CommentsListVar.append(line)

    print(MyTrace(GFI(CF())) + "  " + str(Vars.ClearSourceOnStartVar.get()))
    if Vars.ClearSourceOnStartVar.get():
        FileSourceEntry.delete(0, END)

    VerifyPaths('Load')
    Logger(MyTrace(GFI(CF())), 'Project opened: ' +
           Vars.ProjectFileNameVar.get())
#------------------------------
# Saves a project file


def ProjectSave():
    Logger(MyTrace(GFI(CF())), 'ProjectSave ' + Vars.ProjectFileNameVar.get())

    import pdb

    if VerifyPaths('Save') != 0:
        if tkinter.messagebox.askyesno('Bad paths detected', 'Do you want to continue?') == False:
            Logger(MyTrace(GFI(CF())), 'Project saved aborted. Bad path detected.')
            return

    print(MyTrace(GFI(CF())), Vars.ProjectFileNameVar.get())
    # pdb.set_trace()

    Vars.ProjectFileNameVar.set(
        tkinter.filedialog.asksaveasfilename(
            defaultextension=Vars.ProjectFileExtensionVar.get(),
            filetypes=[('Project file', 'PyCopyMove*.' +
                        Vars.ProjectFileExtensionVar.get()), ('All files', '*.*')],
            initialdir=Vars.AuxDirectoryVar.get(),
            initialfile='PyCopyMoveTk' + Vars.ProjectFileExtensionVar.get(),
            title='Save a PyCopyMoveTk project file',
            parent=Main))

    print(MyTrace(GFI(CF())), Vars.ProjectFileNameVar.get())
    # pdb.set_trace()

    Vars.ProjectFileNameVar.set(
        os.path.normpath(Vars.ProjectFileNameVar.get()))
    ProjectEntry.delete(0, END)
    ProjectEntry.insert(0, Vars.ProjectFileNameVar.get())

    try:
        f = open(Vars.ProjectFileNameVar.get(), 'w')
    except IOError:
        tkinter.messagebox.showerror('Project file error',
                                     'Unable to open requested file.\n>>' + Vars.ProjectFileNameVar.get() + '<<')

    if not Vars.ProjectFileNameVar.get():
        return

    f.write('PyCopyMoveTk.py project file ' + sys.platform + '\n')
    for item in Vars.CommentsListVar:
        f.write(item)
    f.write('DestinationEntry01~' + DestinationEntry01.get().strip() + '\n')
    f.write('DestinationEntry02~' + DestinationEntry02.get().strip() + '\n')
    f.write('DestinationEntry03~' + DestinationEntry03.get().strip() + '\n')
    f.write('DestinationEntry04~' + DestinationEntry04.get().strip() + '\n')
    f.write('DestinationEntry05~' + DestinationEntry05.get().strip() + '\n')
    f.write('DestinationEntry06~' + DestinationEntry06.get().strip() + '\n')
    f.write('DestinationEntry07~' + DestinationEntry07.get().strip() + '\n')
    f.write('DestinationEntry08~' + DestinationEntry08.get().strip() + '\n')
    f.write('DestinationEntry09~' + DestinationEntry09.get().strip() + '\n')
    f.write('DestinationEntry10~' + DestinationEntry10.get().strip() + '\n')
    f.write('DestinationEntry11~' + DestinationEntry11.get().strip() + '\n')
    f.write('DestinationEntry12~' + DestinationEntry12.get().strip() + '\n')
    f.write('KeepFlagsCheckVar~' + str(Vars.KeepFlagsCheckVar.get()) + '\n')

    f.write('CheckSourceOnStartVar~' +
            str(Vars.CheckSourceOnStartVar.get()) + '\n')
    f.write('ClearSourceOnStartVar~' +
            str(Vars.ClearSourceOnStartVar.get()) + '\n')
    f.write('AskOnCopyVar~' + str(Vars.AskOnCopyVar.get()) + '\n')
    f.write('AskOnMoveVar~' + str(Vars.AskOnMoveVar.get()) + '\n')
    f.write('AskOnRecycleVar~' + str(Vars.AskOnRecycleVar.get()) + '\n')
    f.write('AskOnDeleteVar~' + str(Vars.AskOnDeleteVar.get()) + '\n')
    f.write('AskOnRenameVar~' + str(Vars.AskOnRenameVar.get()) + '\n')
    f.write('AskBeforeOverWriteDuringCopyVar~' +
            str(Vars.AskBeforeOverWriteDuringCopyVar.get()) + '\n')
    f.write('AskBeforeOverWriteDuringMoveVar~' +
            str(Vars.AskBeforeOverWriteDuringMoveVar.get()) + '\n')
    f.write('DestinationCheck01Var~' +
            str(Vars.DestinationCheck01Var.get()) + '\n')
    f.write('DestinationCheck02Var~' +
            str(Vars.DestinationCheck02Var.get()) + '\n')
    f.write('DestinationCheck03Var~' +
            str(Vars.DestinationCheck03Var.get()) + '\n')
    f.write('DestinationCheck04Var~' +
            str(Vars.DestinationCheck04Var.get()) + '\n')
    f.write('DestinationCheck05Var~' +
            str(Vars.DestinationCheck05Var.get()) + '\n')
    f.write('DestinationCheck06Var~' +
            str(Vars.DestinationCheck06Var.get()) + '\n')
    f.write('DestinationCheck07Var~' +
            str(Vars.DestinationCheck07Var.get()) + '\n')
    f.write('DestinationCheck08Var~' +
            str(Vars.DestinationCheck08Var.get()) + '\n')
    f.write('DestinationCheck09Var~' +
            str(Vars.DestinationCheck09Var.get()) + '\n')
    f.write('DestinationCheck10Var~' +
            str(Vars.DestinationCheck10Var.get()) + '\n')
    f.write('DestinationCheck11Var~' +
            str(Vars.DestinationCheck11Var.get()) + '\n')
    f.write('DestinationCheck12Var~' +
            str(Vars.DestinationCheck12Var.get()) + '\n')
    f.write('SystemEditorVar~' + Vars.SystemEditorVar.get() + '\n')
    f.write('SystemRenamerVar~' + Vars.SystemRenamerVar.get() + '\n')
    f.write('FileSourceEntry~' + FileSourceEntry.get().strip() + '\n')
    for item in FileSourceListbox.get(0, END):
        f.write('SourcesList~' + item + '\n')
    f.close()
    Logger(MyTrace(GFI(CF())), 'Project saved: ' +
           Vars.ProjectFileNameVar.get())
#------------------------------


def sha1file(filename):
    sha1 = hashlib.sha1()
    f = open(filename, 'rb')
    try:
        sha1.update(f.read())
    except:
        Logger(MyTrace(GFI(CF())), 'whoops ' + str(exception))
    finally:
        f.close()
    return sha1.hexdigest()
#------------------------------

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
    FileSourceEntry.delete(0, END)
    if len(Vars.FileNameListVar) == 1:
        FileSourceEntry.insert(0, Src)
    else:
        FileSourceEntry.insert(
            0, str(len(Vars.FileNameListVar)) + ' source files detected')
    Vars.StatusVar.set(str(len(Vars.FileNameListVar)) +
                       ' source files detected')
    Logger(MyTrace(GFI(CF())), 'Browse source file: ' + str(Vars.FileNameListVar))
#------------------------------
# Allow the user to browse for a destination directory to use

def BrowseDestinationFile(Destination):
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
                                     'Destination directory does not exist.\n' + temp)
        Logger(MyTrace(GFI(CF())), 'Destination error. Current destination directory does not exist. ' +
               temp)

    DestinationName = tkinter.filedialog.askdirectory(
        initialdir=temp,
        parent=Main,
        title='Select a destination directory',
        mustexist=True)

    if len(DestinationName) < 1:
        return  # User choose cancel

    Logger(MyTrace(GFI(CF())), 'Browse destination file: ' +
           Destination + '  ' + DestinationName)
    if DestinationName:
        DestinationName = os.path.normpath(DestinationName)
        if Destination == '01':
            DestinationEntry01.delete(0, END)
            DestinationEntry01.insert(0, DestinationName)
            Vars.DestinationCheck01Var.set(1)
        elif Destination == '02':
            DestinationEntry02.delete(0, END)
            DestinationEntry02.insert(0, DestinationName)
            Vars.DestinationCheck02Var.set(1)
        elif Destination == '03':
            DestinationEntry03.delete(0, END)
            DestinationEntry03.insert(0, DestinationName)
            Vars.DestinationCheck03Var.set(1)
        elif Destination == '04':
            DestinationEntry04.delete(0, END)
            DestinationEntry04.insert(0, DestinationName)
            Vars.DestinationCheck04Var.set(1)
        elif Destination == '05':
            DestinationEntry05.delete(0, END)
            DestinationEntry05.insert(0, DestinationName)
            Vars.DestinationCheck05Var.set(1)
        elif Destination == '06':
            DestinationEntry06.delete(0, END)
            DestinationEntry06.insert(0, DestinationName)
            Vars.DestinationCheck06Var.set(1)
        elif Destination == '07':
            DestinationEntry07.delete(0, END)
            DestinationEntry07.insert(0, DestinationName)
            Vars.DestinationCheck07Var.set(1)
        elif Destination == '08':
            DestinationEntry08.delete(0, END)
            DestinationEntry08.insert(0, DestinationName)
            Vars.DestinationCheck08Var.set(1)
        elif Destination == '09':
            DestinationEntry09.delete(0, END)
            DestinationEntry09.insert(0, DestinationName)
            Vars.DestinationCheck09Var.set(1)
        elif Destination == '10':
            DestinationEntry10.delete(0, END)
            DestinationEntry10.insert(0, DestinationName)
            Vars.DestinationCheck10Var.set(1)
        elif Destination == '11':
            DestinationEntry11.delete(0, END)
            DestinationEntry11.insert(0, DestinationName)
            Vars.DestinationCheck11Var.set(1)
        elif Destination == '12':
            DestinationEntry12.delete(0, END)
            DestinationEntry12.insert(0, DestinationName)
            Vars.DestinationCheck12Var.set(1)

#------------------------------
# Does the copy or move of the source file to the destination location


def CopyOrMoveActions(Action, Src, Dest):
    # remove leading and trailing double quotes
    Src = Src.strip('\n').replace('\"', '')
    # remove leading and trailing double quotes
    Dest = Dest.strip('\n').replace('\"', '')
    if not os.path.isfile(Src):
        tkinter.messagebox.showerror('Source error',
                                     'Source is not a file or does not exist.\n' + Src)
        Logger(MyTrace(GFI(CF())), Action +
               'Source is not a file or does not exist: ' + Src)
        return
    if not os.path.isdir(Dest):
        tkinter.messagebox.showerror(
            'Destination error', 'Destination is not a directory\n' + Dest)
        Logger(MyTrace(GFI(CF())), Action +
               'Destination error. Destination is not a directory: ' + Dest)
        return

    if Action == 'Copy':
        if Vars.AskOnCopyVar.get():
            if not tkinter.messagebox.askyesno('Proceed with copy?',
                                               'Proceed with copy?\nSource: ' + Src + '\nDestination: ' + Dest):
                Logger(MyTrace(GFI(CF())), Action +
                       ' aborted by user ' + Src + ' ' + Dest)
                return

        if Vars.AskBeforeOverWriteDuringCopyVar.get():
            if os.path.isfile(os.path.join(Dest, os.path.split(Src)[1])):
                # print(MyTrace(GFI(CF())),os.path.join(Dest))
                if not tkinter.messagebox.askyesno('Source file exists',
                                                   Dest + '\nSource file exists in destination.\nOverwrite?\n'):
                    Logger(MyTrace(GFI(CF())),
                           'Copy overwite aborted by user. ' + Src + ' ' + Dest)
                    return
        try:
            if Vars.KeepFlagsCheckVar.get():
                shutil.copy2(Src, Dest)  # Copy without flags
            else:
                shutil.copy(Src, Dest)  # Copy with flags
        except shutil.Error as e:
            Logger(MyTrace(GFI(CF())), Action + ' error. Error: %s' % e)
            tkinter.messagebox.showerror('Copy error', e)
        except OSError as e:
            Logger(MyTrace(GFI(CF())), Action + ' error: %s' % e)
            tkinter.messagebox.showerror('Copy error', e)

    if Action == 'Move':
        if Vars.AskOnMoveVar.get():
            if not tkinter.messagebox.askyesno('Move file',
                                               'Proceed with move?\nSource: ' + Src + '\nDestination: ' + Dest):
                Logger(MyTrace(GFI(CF())), Action +
                       ' aborted by user. ' + Src + ' ' + Dest)
                return

        DestFileName = os.path.join(Dest, os.path.split(Src)[1])
        if os.path.isfile(DestFileName):
            if Vars.AskBeforeOverWriteDuringMoveVar.get():
                if not tkinter.messagebox.askyesno('Move question',
                                                   'Source file exists in destination.\nOverwrite?\n' +
                                                   FileStats(DestFileName, Short=True)):
                    Logger(MyTrace(GFI(CF())),
                           'Move overwrite aborted. ' + Src + ' ' + Dest)
                    return
            Logger(MyTrace(GFI(CF())),
                   'Move overwrite dest file removed. ' + Src + ' ' + DestFileName)
            RemoveAFile(os.path.join(Dest, os.path.split(Src)[1]), Trash=True)
            send2trash(os.path.join(Dest, os.path.split(Src)[1]))

        try:
            shutil.move(Src, Dest)
        except shutil.Error as e:
            Logger(MyTrace(GFI(CF())), Action + ' error. Error: %s' % e)
            tkinter.messagebox.showerror('Move error\n', e)
        except OSError as e:
            Logger(MyTrace(GFI(CF())), Action + ' error: %s' % e)
            tkinter.messagebox.showerror('Move error\n', e)
    Logger(MyTrace(GFI(CF())), Action +
           ' Source:' + Src + ' Destination:' + Dest)
#------------------------------
# Handles multiple source files


def NextSource():
    try:
        Src = Vars.FileNameListVar.pop()
    except:
        Logger(MyTrace(GFI(CF())), 'Nothing in list')
        Vars.StatusVar.set('Nothing in list')
        FileSourceEntry.delete(0, END)
        FileSourceEntry.insert(0, 'Nothing in list')
        return
    Logger(MyTrace(GFI(CF())), Src)
    if os.path.exists(Src):
        Vars.StatusVar.set(Src)
        FileSourceEntry.delete(0, END)
        FileSourceEntry.insert(0, Src)
    else:
        Logger(MyTrace(GFI(CF())), Src + ' is not a valid file')

#------------------------------
# Tests to see where to copy or move the source file to
# Multiple destinations are valid


def CopyOrMove(Action):
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
        Logger(MyTrace(GFI(CF())), 'Copy Or Move. No destinations specified' + Src)
        tkinter.messagebox.showinfo(
            'Copy Or Move', 'No destinations specified\n' + Src)
#------------------------------
# Does the copy or move of the source file to the destination location


def DeleteRecycleRenameInfo(Action):
    Src = FileSourceEntry.get()
    # remove leading and trailing double quotes
    Src = Src.strip('\n').replace('\"', '')

    if not os.path.isfile(Src) and Action != 'Info':
        Logger(MyTrace(GFI(CF())), Action + ' Source is not a file ' + Src)
        tkinter.messagebox.showerror(
            'Source error', 'Source is not a file\n' + Src)
        return

    Logger(MyTrace(GFI(CF())), Action + ' Source: ' + Src)

    if Action == 'Recycle':
        if Vars.AskOnRecycleVar.get():
            if not tkinter.messagebox.askyesno('Recycle',
                                               'Recycle may not work unless drive is local!\n' +
                                               'Proceed with recycle?\nSource: ' + Src):
                Logger(MyTrace(GFI(CF())), Action +
                       ' file abort by user. ' + Src)
                return
        try:
            send2trash(Src)
            RemoveAFile(Src, Trash=True)
            Logger(MyTrace(GFI(CF())), Action + ' Source: ' + Src)
        except OSError as e:
            Logger(MyTrace(GFI(CF())), Action + ' file error: %s' % e)

    if Action == 'Delete':
        if Vars.AskOnDeleteVar.get():
            if not tkinter.messagebox.askyesno('Delete file', 'Proceed with delete?\nSource: ' + Src):
                Logger(MyTrace(GFI(CF())), Action +
                       ' file abort by user. ' + Src)
                return
        try:
            # os.remove(Src)
            RemoveAFile(Src, Trash=False)
            Logger(MyTrace(GFI(CF())), Action + ' Source: ' + Src)
        except OSError as e:
            Logger(MyTrace(GFI(CF())), Action + ' file error: %s' % e)

    if Action == 'Rename':
        FileRenameInstance = FileRename()
        FileRenameInstance.RenameAFile()

    if Action == 'Info':
        #print(MyTrace(GFI(CF())), "DeleteRecycleRenameInfo('Info')", FileSourceEntry.get())
        Logger(MyTrace(GFI(CF())), Action + ' File information ' + Src)
        tkinter.messagebox.showinfo(
            'File info', FileStats(FileSourceEntry.get()))
#------------------------------
# Fetch the current source file path from the file source list


def SourceListOperations(Operation):
    if not FileSourceListbox.curselection() and (Operation == 'Fetch' or Operation == 'Remove'):
        Logger(MyTrace(GFI(CF())), 'SourceListOperations: No item selected.')
        return

    if Operation == 'Fetch':
        FileSourceEntry.delete(0, END)
        FileSourceEntry.insert(0, FileSourceListbox.get(
            FileSourceListbox.curselection()))
    elif Operation == 'Remove':
        FileSourceListbox.delete(FileSourceListbox.curselection())
    elif Operation == 'Add':
        if not os.path.isfile(FileSourceEntry.get()):  # verify the data is valid
            Logger(MyTrace(GFI(CF())),
                   'FileSourceEntry path is not valid. ' + FileSourceEntry.get())
            return
        FileSourceListbox.insert(END, FileSourceEntry.get())

    # fetch the contents of FileSourceListbox
    temp_list = list(FileSourceListbox.get(0, END))

    # remove duplicates
    temp_list = list(set(temp_list))

    # sort the listbox
    temp_list.sort(key=str.lower)

    # delete contents of present listbox
    FileSourceListbox.delete(0, END)

    # load listbox with fixed up data
    for item in temp_list:
        FileSourceListbox.insert(END, item)

    Logger(MyTrace(GFI(CF())), 'Source list operations ' + Operation)
#------------------------------
# Show any text file using the defined system editor


def ViewEditAnyFile():
    ViewEditName = tkinter.filedialog.askopenfilename(
        initialdir=Vars.AuxDirectoryVar.get(),
        filetypes=[('All files', '*.*')],
        title='Select a file',
        parent=Main)

    if ViewEditName:
        Logger(MyTrace(GFI(CF())), 'View\Edit any file')
        StartFile(Vars.SystemEditorVar.get(), 'View\Edit any file',
                  os.path.normpath(ViewEditName))
#------------------------------
# Toggle all destinations from selected to un-selected state


def ToggleDestinations():
    Logger(MyTrace(GFI(CF())))
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
    Logger(MyTrace(GFI(CF())), 'ToggleDestinations  ' +
           str(Vars.DestinationCheckToggleStateVar.get()))
#------------------------------

# Verify that destinations exist and are writeable


def VerifyPaths(Type=''):

    Logger(MyTrace(GFI(CF())))
    Results = ''

    if not SearchPath(Vars.SystemEditorVar.get()):
        Results = 'System editor\n'

    # TODO
    print(MyTrace(GFI(CF())) + "  " + str(Vars.CheckSourceOnStartVar.get()))
    if Vars.CheckSourceOnStartVar.get():
        if len(FileSourceEntry.get()) > 0 and not os.path.isfile(FileSourceEntry.get()):
            Results += 'Source\n'

    if not os.path.isdir(DestinationEntry01.get()) or not os.access(DestinationEntry01.get(), os.W_OK):
        Results += 'Destination 1\n'
        DestinationEntry01.configure(fg = "red")
    else:
        DestinationEntry01.configure(fg = "green")

    if not os.path.isdir(DestinationEntry02.get()) or not os.access(DestinationEntry02.get(), os.W_OK):
        Results += 'Destination 2\n'
        DestinationEntry02.configure(fg = "red")
    else:
        DestinationEntry02.configure(fg = "green")
    if not os.path.isdir(DestinationEntry03.get()) or not os.access(DestinationEntry03.get(), os.W_OK):
        Results += 'Destination 3\n'
        DestinationEntry03.configure(fg = "red")
    else:
        DestinationEntry03.configure(fg = "green")
    if not os.path.isdir(DestinationEntry04.get()) or not os.access(DestinationEntry04.get(), os.W_OK):
        Results += 'Destination 4\n'
        DestinationEntry04.configure(fg = "red")
    else:
        DestinationEntry04.configure(fg = "green")
    if not os.path.isdir(DestinationEntry05.get()) or not os.access(DestinationEntry05.get(), os.W_OK):
        Results += 'Destination 5\n'
        DestinationEntry05.configure(fg = "red")
    else:
        DestinationEntry05.configure(fg = "green")
    if not os.path.isdir(DestinationEntry06.get()) or not os.access(DestinationEntry06.get(), os.W_OK):
        Results += 'Destination 6\n'
        DestinationEntry06.configure(fg = "red")
    else:
        DestinationEntry06.configure(fg = "green")
    if not os.path.isdir(DestinationEntry07.get()) or not os.access(DestinationEntry07.get(), os.W_OK):
        Results += 'Destination 7\n'
        DestinationEntry07.configure(fg = "red")
    else:
        DestinationEntry07.configure(fg = "green")
    if not os.path.isdir(DestinationEntry08.get()) or not os.access(DestinationEntry08.get(), os.W_OK):
        Results += 'Destination 8\n'
        DestinationEntry08.configure(fg = "red")
    else:
        DestinationEntry08.configure(fg = "green")
    if not os.path.isdir(DestinationEntry09.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 9\n'
        DestinationEntry09.configure(fg = "red")
    else:
        DestinationEntry09.configure(fg = "green")
    if not os.path.isdir(DestinationEntry10.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 10\n'
        DestinationEntry10.configure(fg = "red")
    else:
        DestinationEntry10.configure(fg = "green")
    if not os.path.isdir(DestinationEntry11.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 11\n'
        DestinationEntry11.configure(fg = "red")
    else:
        DestinationEntry11.configure(fg = "green")
    if not os.path.isdir(DestinationEntry12.get()) or not os.access(DestinationEntry09.get(), os.W_OK):
        Results += 'Destination 12\n'
        DestinationEntry12.configure(fg = "red")
    else:
        DestinationEntry12.configure(fg = "green")
    #if len(Results) != 0:
    #    xx = tkinter.messagebox.showerror('Invalid path(s)', 'Invalid path(s):\n' + Results)
    #else:
    #    if (Type != 'Save' and Type != 'Load'):
    #        tkinter.messagebox.showinfo('All paths valid', 'All paths valid!')
    return(len(Results))  # 0 is No bad paths
#------------------------------
# Some debug stuff


def About():
    Logger(MyTrace(GFI(CF())),
           main.Vars.StartUpDirectoryVar.get(), MyTrace(GFI(CF())))
    tkinter.messagebox.showinfo('About',  main.Vars.StartUpDirectoryVar.get() +
                                '\n' + Main.geometry() +
                                '\n' + str(Main.winfo_screenwidth()) + 'x' + str(Main.winfo_screenheight()) +
                                '\n' + 'Python version: ' + platform.python_version() +
                                '\n' + platform.platform() +
                                '\n' + 'PyCopyMoveTk version: ' + Vars.ProgramVersionNumber.get())
#------------------------------
# The help file


def Help():
    Logger(MyTrace(GFI(CF())), main.Vars.StartUpDirectoryVar.get())
    Vars.StatusVar.set('Help')

    try:
        f = open(Vars.HelpFileVar.get(), 'r')
    except IOError:
        tkinter.messagebox.showerror('Help file error',
                                     'Requested file does not exist.\n>>' + Vars.HelpFileVar.get() + '<<')
        return
    data = f.read()
    f.close()

    Doug = None
    MyMessageBox(Title='PyCopyMoveTk help',
                 TextMessage=data,
                 Buttons=['OK', 'Cancel'],
                 LabelText=['This is a test label'],
                 fgColor='pink',
                 bgColor='black',
                 Center=None,
                 Geometry='500x300+1300+20')

#------------------------------
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
    Popupmenu.entryconfigure("Clear", command=lambda: w.delete(0, tkinter.END))
    Popupmenu.entryconfigure(
        "Select", command=lambda: w.select_range(0, tkinter.END))
    Popupmenu.tk.call("tk_popup", Popupmenu, e.x_root, e.y_root)

#------------------------------

# Build all the gui and start the program
Vars.StatusVar.set('Starting')

menubar = Menu(Main)
Main['menu'] = menubar
ProjectsMenu = Menu(menubar)
SourceMenu = Menu(menubar)
OtherMenu = Menu(menubar)
OptionsMenu = Menu(menubar)
HelpMenu = Menu(menubar)

menubar.add_cascade(menu=ProjectsMenu, label='Project')
ProjectsMenu.add_command(label='Load', command=ProjectLoad)
ProjectsMenu.add_command(label='Save', command=ProjectSave)
ProjectsMenu.add_command(
    label='Edit', command=lambda: ShowEditFile(ProjectEntry.get()))

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

menubar.add_cascade(menu=HelpMenu, label='Help')
HelpMenu.add_command(label='About', command=About)
HelpMenu.add_command(label='Help', command=Help)

#---------------
FileFrame1 = Frame(Main, relief=SUNKEN, bd=1)
FileFrame1.pack(fill=X, side=TOP)
Label(FileFrame1, text='Source file', font=("Helvetica", 15)).pack(
    side=TOP, fill=BOTH, expand=YES)

BrowseSourceButon = Button(FileFrame1, text='Browse',
                           command=BrowseSourceFile, width=8)
BrowseSourceButon.pack(side=LEFT)
ToolTip(BrowseSourceButon, 'Browse for one or more source file')
FileSourceEntry = Entry(FileFrame1, relief=SUNKEN, bd=2)
FileSourceEntry.pack(fill=X)
ToolTip(FileSourceEntry, 'Path for the source file')

MakePopupmenu(Main)
FileSourceEntry.bind_class(
    "Entry", "<Button-3><ButtonRelease-3>", ShowPopupmenu)

#---------------
FileFrame2 = Frame(Main, relief=SUNKEN, bd=1)
FileFrame2.pack(side=TOP, fill=BOTH, expand=YES)

FileFrame3 = Frame(FileFrame2, relief=SUNKEN, bd=1, width=10)
FileFrame3.pack(side=LEFT)
ToolTip(FileFrame3, 'Operations to the source list')

Button(FileFrame3, text='Add', width=8,
       command=lambda: SourceListOperations('Add')).pack(side=TOP, fill=BOTH, expand=YES)
Button(FileFrame3, text='Fetch', width=8,
       command=lambda: SourceListOperations('Fetch')).pack(side=TOP, fill=BOTH, expand=YES)
Button(FileFrame3, text='Remove', width=8,
       command=lambda: SourceListOperations('Remove')).pack(side=TOP, fill=BOTH, expand=YES)

FileFrame4 = Frame(FileFrame2, relief=SUNKEN, bd=1)
FileFrame4.pack(side=LEFT, fill=X, expand=YES)

yScroll = Scrollbar(FileFrame4, orient=VERTICAL)
yScroll.pack(side=RIGHT, fill=Y)
xScroll = Scrollbar(FileFrame4, orient=HORIZONTAL)
xScroll.pack(side=BOTTOM, fill=X)
FileSourceListbox = Listbox(FileFrame4, height=6,
                            yscrollcommand=yScroll.set, xscrollcommand=xScroll.set)
FileSourceListbox.pack(fill=BOTH, expand=YES)

FileSourceListbox.bind('<Double-Button-1>',
                       lambda x: SourceListOperations('Fetch'))
ToolTip(FileSourceListbox, 'Saved list of source files. Double left click to fetch.')
yScroll.config(command=FileSourceListbox.yview)
xScroll.config(command=FileSourceListbox.xview)

OperationFrame = Frame(Main, relief=SUNKEN, bd=1)
OperationFrame.pack(side=TOP, fill=X, expand=YES)
ToolTip(OperationFrame, 'Click a button to perform action')
Label(OperationFrame, text='Operations', font=(
    "Helvetica", 15)).pack(side=TOP, fill=BOTH, expand=YES)

Button(OperationFrame, width=10, text='Copy',
       command=lambda: CopyOrMove('Copy')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Move',
       command=lambda: CopyOrMove('Move')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Recycle',
       command=lambda: DeleteRecycleRenameInfo('Recycle')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Delete',
       command=lambda: DeleteRecycleRenameInfo('Delete')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Rename',
       command=lambda: DeleteRecycleRenameInfo('Rename')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Info',
       command=lambda: DeleteRecycleRenameInfo('Info')).pack(side=LEFT)
Button(OperationFrame, width=10, text='Next',
       command=lambda: NextSource()).pack(side=LEFT)
#------------------------------
DestinationFrame = Frame(Main, relief=SUNKEN, bd=1)
DestinationFrame.pack(fill=X)
ToolTip(DestinationFrame, 'Chose/add a destination path')
Label(DestinationFrame, text='Destination directories',
      font=("Helvetica", 15)).pack(side=TOP, fill=BOTH, expand=YES)

DestinationFrame00 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame00.pack(side=TOP, fill=X)
ToggleAllButton = Button(DestinationFrame00, width=15,
                         text='Toggle all', command=ToggleDestinations)
ToggleAllButton.pack(padx=100, pady=5, side=LEFT)
ToolTip(ToggleAllButton, 'Toggle all destination selects')

VerifyPathsButton = Button(DestinationFrame00, width=15,
                         text='Verify paths', command=VerifyPaths)
VerifyPathsButton.pack(padx=5, pady=5, side=LEFT)
ToolTip(VerifyPathsButton, 'Verify all destination paths')

DestinationFrame01 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame01.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame01, text='Dest01',
            variable=Vars.DestinationCheck01Var).pack(side=LEFT)
Button(DestinationFrame01, text='Browse',
       command=lambda: BrowseDestinationFile('01')).pack(side=LEFT)
DestinationEntry01 = Entry(DestinationFrame01)
DestinationEntry01.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame02 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame02.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame02, text='Dest02',
            variable=Vars.DestinationCheck02Var).pack(side=LEFT)
Button(DestinationFrame02, text='Browse',
       command=lambda: BrowseDestinationFile('02')).pack(side=LEFT)
DestinationEntry02 = Entry(DestinationFrame02)
DestinationEntry02.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame03 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame03.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame03, text='Dest03',
            variable=Vars.DestinationCheck03Var).pack(side=LEFT)
Button(DestinationFrame03, text='Browse',
       command=lambda: BrowseDestinationFile('03')).pack(side=LEFT)
DestinationEntry03 = Entry(DestinationFrame03)
DestinationEntry03.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame04 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame04.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame04, text='Dest04',
            variable=Vars.DestinationCheck04Var).pack(side=LEFT)
Button(DestinationFrame04, text='Browse',
       command=lambda: BrowseDestinationFile('04')).pack(side=LEFT)
DestinationEntry04 = Entry(DestinationFrame04)
DestinationEntry04.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame05 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame05.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame05, text='Dest05',
            variable=Vars.DestinationCheck05Var).pack(side=LEFT)
Button(DestinationFrame05, text='Browse',
       command=lambda: BrowseDestinationFile('05')).pack(side=LEFT)
DestinationEntry05 = Entry(DestinationFrame05)
DestinationEntry05.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame06 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame06.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame06, text='Dest06',
            variable=Vars.DestinationCheck06Var).pack(side=LEFT)
Button(DestinationFrame06, text='Browse',
       command=lambda: BrowseDestinationFile('06')).pack(side=LEFT)
DestinationEntry06 = Entry(DestinationFrame06)
DestinationEntry06.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame07 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame07.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame07, text='Dest07',
            variable=Vars.DestinationCheck07Var).pack(side=LEFT)
Button(DestinationFrame07, text='Browse',
       command=lambda: BrowseDestinationFile('07')).pack(side=LEFT)
DestinationEntry07 = Entry(DestinationFrame07)
DestinationEntry07.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame08 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame08.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame08, text='Dest08',
            variable=Vars.DestinationCheck08Var).pack(side=LEFT)
Button(DestinationFrame08, text='Browse',
       command=lambda: BrowseDestinationFile('08')).pack(side=LEFT)
DestinationEntry08 = Entry(DestinationFrame08)
DestinationEntry08.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame09 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame09.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame09, text='Dest09',
            variable=Vars.DestinationCheck09Var).pack(side=LEFT)
Button(DestinationFrame09, text='Browse',
       command=lambda: BrowseDestinationFile('09')).pack(side=LEFT)
DestinationEntry09 = Entry(DestinationFrame09)
DestinationEntry09.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame10 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame10.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame10, text='Dest10',
            variable=Vars.DestinationCheck10Var).pack(side=LEFT)
Button(DestinationFrame10, text='Browse',
       command=lambda: BrowseDestinationFile('10')).pack(side=LEFT)
DestinationEntry10 = Entry(DestinationFrame10)
DestinationEntry10.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame11 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame11.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame11, text='Dest11',
            variable=Vars.DestinationCheck11Var).pack(side=LEFT)
Button(DestinationFrame11, text='Browse',
       command=lambda: BrowseDestinationFile('11')).pack(side=LEFT)
DestinationEntry11 = Entry(DestinationFrame11)
DestinationEntry11.pack(side=LEFT, fill=X, expand=TRUE)

DestinationFrame12 = Frame(DestinationFrame, relief=SUNKEN, bd=1)
DestinationFrame12.pack(side=TOP, fill=X)
Checkbutton(DestinationFrame12, text='Dest12',
            variable=Vars.DestinationCheck12Var).pack(side=LEFT)
Button(DestinationFrame12, text='Browse',
       command=lambda: BrowseDestinationFile('12')).pack(side=LEFT)
DestinationEntry12 = Entry(DestinationFrame12)
DestinationEntry12.pack(side=LEFT, fill=X, expand=TRUE)

#------------------------------
StatusFrame = Frame(Main, relief=SUNKEN, bd=1)
StatusFrame.pack(fill=X)
Label(StatusFrame, text='Status', font=("Helvetica", 15)).pack(
    side=TOP, fill=BOTH, expand=YES)
Statuslabel = Label(StatusFrame, textvariable=Vars.StatusVar, relief=GROOVE)
Statuslabel.pack(side=TOP, expand=TRUE, fill=X)
ToolTip(Statuslabel, 'Display status')
ProjectEntry = Entry(StatusFrame)
ProjectEntry.pack(side=TOP, expand=TRUE, fill=X)
ToolTip(ProjectEntry, 'Currently loaded project')
#------------------------------

SetDefaults()  # Initialize the variables
StartUpStuff()
ParseCommandLine()
#------------------------------
Vars.LogFileNameVar.set(os.path.join(
    Vars.StartUpDirectoryVar.get(), 'PyCopyMoveTk.log'))
#------------------------------
Main.bind('<F1>', lambda e: Help())
Main.bind('<F2>', lambda e: About())
Main.bind('<F3>', lambda e: BrowseSourceFile())
Main.bind('<F4>', lambda e: ProjectLoad())
#Main.bind('<Configure>', lambda e:ShowResize(Main))

Main.minsize(400, 300)
Main.resizable(True, False)
Main.option_add('*Font', 'courier 10')
Main.title('PyCopyMoveTk')
Main.wm_iconname('PyCopyMoveTk')
Main.mainloop()
