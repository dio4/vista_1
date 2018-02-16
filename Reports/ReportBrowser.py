# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtGui

from library.TextDocument import CResourceLoaderMixin


class CReportBrowser(QtGui.QTextBrowser, CResourceLoaderMixin):
    def __init__(self, parent=None):
        QtGui.QTextBrowser.__init__(self, parent)
        CResourceLoaderMixin.__init__(self)
        
#        self._oldFrame = None
#        self._oldFormat = None
#        self.setMouseTracking(True)
#    
#    
#    
#    def mouseMoveEvent(self, event):
#        cursor = self.cursorForPosition(event.pos())
#        frame = cursor.currentFrame()
#        if frame != self._oldFrame:
#            if self._oldFrame:
#                self._oldFrame.setFrameFormat(self._oldFormat)
#            self._oldFrame = frame
#            self._oldFormat = frame.frameFormat()        
#            newFormat = frame.frameFormat()
#            newFormat.setBorderBrush(QtGui.QBrush(QtCore.Qt.red))
#            newFormat.setBorder(5)
#            frame.setFrameFormat(newFormat)

            
        