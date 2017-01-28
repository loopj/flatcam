############################################################
# FlatCAM: 2D Post-processing for Manufacturing            #
# http://flatcam.org                                       #
# Author: Juan Pablo Caram (c)                             #
# Date: 2/5/2014                                           #
# MIT Licence                                              #
############################################################

import sys
from PyQt4 import QtGui
from FlatCAMApp import App
import gettext 
import os
import sys
if sys.platform == 'win32':
       import gettext_windows
       gettext_windows.setup_env()	   
pathname = os.path.dirname(sys.argv[0])
localdir = os.path.abspath(pathname) + "/locale"
gettext.install("messages", localdir)


def debug_trace():
    """
    Set a tracepoint in the Python debugger that works with Qt
    :return: None
    """
    from PyQt4.QtCore import pyqtRemoveInputHook
    #from pdb import set_trace
    pyqtRemoveInputHook()
    #set_trace()

debug_trace()

# All X11 calling should be thread safe otherwise we have strange issues
# QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
# NOTE: Never talk to the GUI from threads! This is why I commented the above.

app = QtGui.QApplication(sys.argv)
fc = App()
sys.exit(app.exec_())
