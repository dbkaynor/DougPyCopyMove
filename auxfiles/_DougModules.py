#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://www.tutorialspoint.com/online_python_formatter.htm
import os
import sys
import time
import platform
import stat
import logging
import argparse
import shutil
import subprocess
from subprocess import Popen, PIPE

import subprocess
from subprocess import Popen, PIPE

import hashlib  # sha1
import binascii

from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import tkinter.scrolledtext

from inspect import currentframe as CF
from inspect import getframeinfo as GFI
from inspect import getmodulename as GMN

GeometryVar = None
EditorResults = ''
EditorToplevelName = 'None'

#EditorToplevel = Tk()
#EditorToplevel.title(" " + Title)
#EditorToplevel.Geometry = '10x10+200+0'
# -----------------------------


def MessageTimeOut(Message='TimeOut test', TimeOut=2000):
    Mroot = Toplevel()
    #Mroot = Tk()
    Mroot.title = 'Message'
    label1 = Label(Mroot, text=Message, width=len(Message))
    label1.pack()

    def close_after_timeout():
        Mroot.destroy()

    #root.after(TimeOut, close_after_timeout)
    Mroot.after(TimeOut, Mroot.destroy)
    Mroot.mainloop()

# ------------------------------
# http://knowpapa.com/text-editor/
# This is a built in editor
# Width and Height values are in pixels
# todo

def Editor(
    FileToEdit=None,
    TextData=None,
    Title='Editor',
    Width=100,
    Height=400,
    XPos=900,
    YPos=100,
):
    if FileToEdit:
        with open(FileToEdit, 'r') as stream:
            text = stream.read()
    if TextData:
        text = TextData
    global EditorToplevelName

    EditorToplevel = Tk()
    EditorToplevel.title(" " + Title)
    EditorToplevel.Geometry = '10x10+200+0'
    EditorToplevel.geometry('%dx%d+%d+%d' % (Width, Height, XPos, YPos))
    EditorToplevelName = Title
    #print(MyTrace(GFI(CF())), '>>' + EditorToplevelName + '<<')

    def destroyEditor():
        global EditorToplevelName
        EditorToplevel.destroy()
        EditorToplevelName = 'None'
        return

    EditorToplevel.protocol('WM_DELETE_WINDOW', destroyEditor)

    textPad = Text(EditorToplevel, relief=SUNKEN, wrap=WORD)
    sbar = Scrollbar(EditorToplevel)
    sbar['command'] = textPad.yview
    textPad['yscrollcommand'] = sbar.set
    sbar.pack(side=RIGHT, fill=Y)

    # This prints out the window geometry on configure event
    # EditorToplevel.bind("<Configure>",lambda e:ShowResize("Edit window: ", EditorToplevel))

    # This handles getting the text from the edit top level

    def G(junk):
        global EditorResults
        print(MyTrace(GFI(CF())), EditorResults)
        EditorResults = textPad.get('current linestart',
                                    'current lineend')
        print(MyTrace(GFI(CF())), EditorResults)

    textPad.bind('<Button-1>', G)

    # create a menu

    # def exit_command():
    # destroyEditor()

    # def save_command():
    #file = tkinter.filedialog.asksaveasfile(mode='w')
    # if file != None:

    # slice off the last character from get, as an extra return is added

    #data = self.textPad.get('1.0', END + '-1c')
    # file.write(data)
    # file.close()

    #menu = Menu(EditorToplevel)
    # EditorToplevel.config(menu=menu)
    #filemenu = Menu(menu)
    #menu.add_cascade(label='File', menu=filemenu)
    #filemenu.add_command(label='Save', command=save_command)
    # filemenu.add_separator()
    #filemenu.add_command(label='Exit', command=exit_command)

    # end of menu creation

    textPad.delete('1.0', END)
    textPad.insert('1.0', text)
    textPad.mark_set(INSERT, '1.0')
    textPad.focus()
    textPad.pack(expand=YES, fill=BOTH)
    EditorToplevel.mainloop()


# ------------------------------
# Loads a selected file into the defined system editor

def ShowEditFile(
    SystemEditor,
    FileToShowEdit=None,
    InitialDir=None,
    ParentTopLevel=None,
):
    if FileToShowEdit == None:
        FileToShowEdit = \
            tkinter.filedialog.askopenfilename(defaultextension='.*',
                                               initialdir=InitialDir, filetypes=[('All files', '*.*'
                                                                                  )], title='Show/Edit a file', parent=ParentTopLevel)

    Logger(Trace=MyTrace(GFI(CF())), Message='Show/Edit file: '
           + FileToShowEdit)
    FileToShowEdit = os.path.normpath(FileToShowEdit)

    try:
        StartFile(SystemEditor, FileToShowEdit)
    except IOError:
        tkinter.messagebox.showerror('Show/Edit file error',
                                     'Show/Edit file error:\n' + SystemEditor + '\n'
                                     + FileToShowEdit)
        return


# ------------------------------

def StartFile(filename, args=[], Wait=True):
    command = []
    command.append(filename)
    command.extend(args)
    Logger(Trace=MyTrace(GFI(CF())), Message='StartFile arguments: '
           + str(command))
    ce = None

    try:
        if Wait:
            ce = subprocess.call(command)
        else:
            ce = subprocess.Popen(command)

        #print (MyTrace(GFI(CF())), str(command) + ' ' + str(Wait) + '  ' + str(ce))
    except OSError:

        tkinter.messagebox.showerror(MyTrace(GFI(CF())) + ' StartFile did a Badddddd thing ',
                                     'Arguments: ' +
                                     str(command) + '\nReturn code: '
                                     + str(ce))
        return


# ------------------------------

def crc32file(filename):
    filedata = open(filename, 'rt').read()
    return binascii.crc32(bytearray(filedata, 'utf-8'))


# ------------------------------

def md5file(filename, block_size=256 * 128):
    md5 = hashlib.md5()
    with open(filename, 'rt') as f:
        for chunk in iter(lambda: f.read(block_size), ''):
            md5.update(chunk)
    return md5.hexdigest()

# ------------------------------

    def sha1file(filename):
        sha1 = hashlib.sha1()
        f = open(filename, 'rb')
        try:
            sha1.update(f.read())
        except:
            Logger(Trace=MyTrace(GFI(CF())), Message='whoops '
                   + str(exception))
        finally:
            f.close()
        return sha1.hexdigest()


# ------------------------------
# Checks if file name exists
# File may be either on the system path
# or file may be a full path

def SearchPath(name):
    path = os.environ['PATH']
    for dir in path.split(os.pathsep):
        binpath = os.path.join(dir, name)
        if os.path.exists(binpath):
            return True
    return False


# ------------------------------
# Parses the frame inspect information
# Example: print(MyTrace(getframeinfo(currentframe())))
# Example: print(MyTrace(GFI(CF())), Long=False)
# Use Long to determine what Display is displayed

def MyTrace(FrameInfoDict, Display='line,func'):
    filename = 0
    lineno = 1
    function = 2
    code_context = 3
    index = 4
    tStr = ''
    Display = Display.lower()
    if 'line' in Display:
        tStr += str(FrameInfoDict[lineno]).zfill(5) + '  '
    if 'func' in Display:
        tStr += 'Function:' + FrameInfoDict[function] + '  '
    if 'file' in Display:
        tStr += 'Filename:' + FrameInfoDict[filename] + '  '
    if 'code' in Display:
        tStr += 'Code:' + str(FrameInfoDict[code_context]) + '  '
    if 'index' in Display:
        tStr += 'Index:' + str(FrameInfoDict[index])
    return tStr.strip()


# ------------------------------
# Show Disk Space

def DiskSpace():
    DiskSpace = shutil.disk_usage('/')
    tkinter.messagebox.showinfo('Disk space', 'Free: %f Gbytes'
                                % (DiskSpace.free / 1e9) + '\n'
                                + 'Used: %f Gbytes' % (DiskSpace.used
                                                       / 1e9) + '\n' + 'Total: %f Gbytes'
                                % (DiskSpace.total / 1e9))
    Logger(Trace=MyTrace(GFI(CF())), Message='DiskSpace')


# ------------------------------
# Setup the logger

def SetUpLogger(LogFileName):
    logger = logging.getLogger(LogFileName)
    logger.setLevel(logging.DEBUG)
    if os.path.exists(LogFileName):
        os.remove(LogFileName)
    logger = logging.basicConfig(level=logging.DEBUG,
                                 filename=LogFileName,
                                 format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# ------------------------------
# Log anything that the program should


def Logger(
    Message='',
    Trace=None,
    PrintToTerminal=False,
    MessageBox=False,
):
    MyLogger = logging.getLogger()
    if not Trace:
        Trace = ''
    mystr = '%s   %s' % (Message, Trace)
    mystr = mystr.strip()
    MyLogger.debug(mystr)
    if MessageBox:
        tkinter.messagebox.showerror('Logger', mystr)
    if PrintToTerminal:
        print(mystr)


# ------------------------------

def ShowResize(TraceString, Item):
    global GeometryVar
    if str(GeometryVar) != str(Item.geometry()):
        GeometryVar = Item.geometry()
        #print(TraceString + ': ' + GeometryVar)
        return TraceString + ': ' + GeometryVar

# ------------------------------
# Parse the command line

def ParseCommandLine():
    parser = \
        argparse.ArgumentParser(description='A tool to compare to directories and move files'
                                )
    parser.add_argument('-debug', help='Enable debugging',
                        action='store_true')
    args = parser.parse_args()

    if args.debug:
        import pdb
        pdb.set_trace()
        Logger(Trace=MyTrace(GFI(CF())), Message='debug is on')
    else:
        Logger(Trace=MyTrace(GFI(CF())), Message='debug is off')


# ------------------------------
# returns string with status for a file

def FileStats(FilePath, Short=False):
    try:
        FileStatString = ''
        FileStats = os.stat(FilePath)
        if Short == True:
            FileStatString += 'Base name: %s' \
                % os.path.basename(FilePath) + '\n'
            FileStatString += 'Modified time: %s' \
                % time.ctime(FileStats.st_mtime) + '\n'
            FileStatString += \
                'File size: {:,}'.format(FileStats.st_size) + '\n'
        else:
            FileStatString += 'Full path: %s' % FilePath + '\n'
            FileStatString += 'Dir name: %s' \
                % os.path.dirname(FilePath) + '\n'
            FileStatString += 'Base name: %s' \
                % os.path.basename(FilePath) + '\n'
            FileStatString += \
                'File size: {:,}'.format(FileStats.st_size) + '\n'
            FileStatString += 'Creation time: %s' \
                % time.ctime(FileStats.st_ctime) + '\n'
            FileStatString += 'Modified time: %s' \
                % time.ctime(FileStats.st_mtime) + '\n'
            FileStatString += 'Access time: %s' \
                % time.ctime(FileStats.st_atime) + '\n'
            FileStatString += 'File mode bits: %o' % FileStats.st_mode \
                + '\n'

            mode = FileStats[0]
            if mode & stat.S_ISLNK(FileStats[stat.ST_MODE]):
                FileStatString += 'File is a link\n'
            else:
                FileStatString += 'File is not a link\n'
            if mode & stat.S_IREAD:
                FileStatString += 'File is readable\n'
            else:
                FileStatString += 'File is not readable\n'
            if mode & stat.S_IWRITE:
                FileStatString += 'File is writable\n'
            else:
                FileStatString += 'File is not writable\n'
            if mode & stat.S_IEXEC:
                FileStatString += 'File is executable\n'
            else:
                FileStatString += 'File is not executable\n'
            if stat.S_ISDIR(FileStats.st_mode):
                FileStatString += 'File is a directory\n'
            else:
                FileStatString += 'File is not a directory\n'
            if stat.S_ISREG(FileStats.st_mode):
                FileStatString += 'File is a regular file\n'
            else:
                FileStatString += 'File is a not regular file\n'
    except:
        FileStatString = 'Unable to retrieve file status for\n' \
            + FilePath
    return FileStatString


# ------------------------------
# This will either delete a file or move it to trash

def RemoveAFile(File, Trash):
    Logger(Trace=MyTrace(GFI(CF())), Message='Remove a file: ' + File
           + str(Trash))
    if not os.path.exists(File):
        return
    if Trash:
        try:
            send2trash(File)
            Logger(Trace=MyTrace(GFI(CF())),
                   Message='Success send2Trash: ' + File)
        except OSError:
            tkinter.messagebox.showerror('Send file to trash error. ',
                                         File + '\nPermissions?')
            Logger(Trace=MyTrace(GFI(CF())),
                   Message='Failed send2Trash: ' + File)
    else:
        try:
            os.remove(File)
            Logger(Trace=MyTrace(GFI(CF())), Message='Success remove: '
                   + File)
        except OSError:
            tkinter.messagebox.showerror('Delete a file error. ', File
                                         + '\nPermissions?')
            Logger(Trace=MyTrace(GFI(CF())), Message='Failed remove: '
                   + File)


# ------------------------------
# This places MyMessageBox on the display
# If Center is None the position is based on Geometry option
# If Center is type string the position center of the screen
# If Center is a pointer the position is the center of the pointed to item
# The Size in Geometry is always used, only the position is changed

def MyMessageBox(
    Title='MyMessageBox',
    LabelText=[],
    TextMessage=None,
    bgColor='black',
    fgColor='white',
    Buttons=['Close'],
    Center=None,
    Geometry=None,
):

    def ButtonHandle(data):
        global ButtonResult
        ButtonResult = data
        print(MyTrace(GFI(CF())), ButtonResult, data)
        MyMBMain.destroy()
        return data

    MyMBMain = Tk()  # Create a main window
    MyMBMain.title(Title)
    MyMBMain.config(bg=bgColor)

    # This prints out the window geometry on configure event

    MyMBMain.bind('<Configure>', lambda e: ShowResize('MyMessageBox',
                                                      MyMBMain))

    # parses the geometry parameter

    print(MyTrace(GFI(CF())), Center, Geometry)
    if not Geometry:
        Geometry = '250x250+10+20'
    Geom = Geometry.split('+')
    Size = Geom[0].split('x')
    XPos = int(Geom[1])
    YPos = int(Geom[2])
    XSize = int(Size[0])
    YSize = int(Size[1])

    # print(MyTrace(GFI(CF())), XPos, YPos, XSize, YSize)

    if 'None' in str(type(Center)):  # Uses the Geometry option
        print(MyTrace(GFI(CF())), 'Geometry: ', Geometry)
    elif 'tkinter.Tk' in str(type(Center)):

                                            # center of the item pointed to
        # parses the geometry of the CenterParam window

        CenterParamGeometry = Center.geometry()

        # These are the values from the passed in parameters

        CenterParamGeom = CenterParamGeometry.split('+')
        CenterParamSize = CenterParamGeom[0].split('x')
        CenterParamXPos = int(CenterParamGeom[1])
        CenterParamYPos = int(CenterParamGeom[2])
        CenterParamXSize = int(CenterParamSize[0])
        CenterParamYSize = int(CenterParamSize[1])

        # These are the values from the message box

        MyMBMainGeom = Geometry.split('+')
        MyMBSize = MyMBMainGeom[0].split('x')
        MyMBXPos = int(MyMBMainGeom[1])
        MyMBYPos = int(MyMBMainGeom[2])
        MyMBXSize = int(MyMBSize[0])
        MyMBYSize = int(MyMBSize[1])

        # This is the calculated position for the messagebox

        XPos = CenterParamXPos + CenterParamXSize / 2 - MyMBXSize / 2
        YPos = CenterParamYPos + CenterParamYSize / 2 - MyMBYSize / 2
    elif 'center' in Center.lower():

                                     # center of the screen

        XPos = MyMBMain.winfo_screenwidth() / 2 - XSize / 2
        YPos = MyMBMain.winfo_screenheight() / 2 - YSize / 2
        print(MyTrace(GFI(CF()), Display='line'), Center.upper())

    MyMBMain.geometry('%dx%d+%d+%d' % (XSize, YSize, XPos, YPos))

    # Add some buttons
    # Theoretically an unlimited number of buttons can be added

    ButtonFrame = Frame(MyMBMain, relief=SUNKEN, bd=1, bg=bgColor)
    ButtonFrame.pack(side=TOP, expand=FALSE, fill=X)
    for a in reversed(Buttons):
        Button(ButtonFrame, text=a, command=lambda a=a:
               ButtonHandle(a)).pack(side=RIGHT)

    # This adds labels for each message
    # Theoretically an unlimited number of labels can be added

    for x in range(len(LabelText)):

        Label(MyMBMain, text=LabelText[x], relief=GROOVE, fg=fgColor,
              bg=bgColor).pack(expand=FALSE, fill=X)

    # A text box http://effbot.org/tkinterbook/text.htm

    if TextMessage:
        Yscrollbar = Scrollbar(MyMBMain, orient=VERTICAL)
        Yscrollbar.pack(side=RIGHT, fill=Y)

        Xscrollbar = Scrollbar(MyMBMain, orient=HORIZONTAL)
        Xscrollbar.pack(side=BOTTOM, fill=X)

        Textbox = Text(
            MyMBMain,
            wrap=NONE,
            width=XSize,
            height=YSize,
            bg=bgColor,
            fg=fgColor,
            yscrollcommand=Yscrollbar.set,
            xscrollcommand=Xscrollbar.set,
        )
        Textbox.pack()

        Yscrollbar.config(command=Textbox.yview)
        Xscrollbar.config(command=Textbox.xview)
        Textbox.insert(END, TextMessage)

    MyMBMain.resizable(1, 1)
    MyMBMain.mainloop()


# ------------------------------
# Return path to best system editor

def GetBestEditor():
    if sys.platform.startswith('linux'):
        file = '/usr/bin/gedit'
        if os.path.isfile(file):
            return file
        file = '/usr/bin/kate'
        if os.path.isfile(file):
            return file
    elif sys.platform.startswith('win32'):
        file = 'C:\\Program Files (x86)\\Notepad++\\notepad++.exe'
        if os.path.isfile(file):
            return file
        file = 'C:\\Program Files\\Notepad++\\notepad++.exe'
        if os.path.isfile(file):
            return file
        else:
            return 'notepad.exe'


# ------------------------------

# Try to get source file from clipboard

def GetClipBoard():

    # DM.Logger(DM.MyTrace(GFI(CF())), 'GetClipBoard')

    try:
        temp = Main.clipboard_get()
        temp = temp.replace('"', '').strip()
        if os.path.isfile(temp):
            DM.Logger(DM.MyTrace(GFI(CF())), 'From clipboard: ' + temp)
        else:
            DM.Logger(DM.MyTrace(GFI(CF())),
                      'Invalid path from clipboard: ' + temp)
    except:
        DM.Logger(DM.MyTrace(GFI(CF())), 'No clipboard data')

# ------------------------------

if __name__ == '__main__':

    print(MyTrace(GFI(CF()), Display='line,func,file'))
    import pdb

    # pdb.set_trace()
    MessageTimeOut(Message='Message timeout test', TimeOut=2000)
