# -*- coding: utf-8 -*-

# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

path_platforms = ( "C:\Python33\Lib\site-packages\PyQt5\plugins\platforms\qwindows.dll", "platforms\qwindows.dll" )
includefiles = [path_platforms]
excludes = [
    '_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
    'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
    'Tkconstants', 'Tkinter'
]

options = {
    'build_exe': {
        'includes': ['atexit', 'requests', 'pyproj', 'PyQt5.QtCore','PyQt5.QtGui', 'PyQt5.QtWidgets'],
        'include_files': [path_platforms],
        'excludes': excludes
    }
}

executables = [
    Executable('main.py', base=base)
]

setup(name='GrMap',
      version='0.1',
      description='Client for Ktimatologio WMS server / exporting tiff+tfw',
      options=options,
      executables=executables
      )