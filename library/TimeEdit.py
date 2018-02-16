#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *


class CTimeRangeValidator(QtGui.QValidator):
     def validate(self, input, pos):
        return  1


class CTimeRangeEdit(QtGui.QLineEdit):
    validator = None
    
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setInputMask('09:99 - 09:99')
#        self.setValidator(self.getRangeValidator())
        
    def getValidator(self):
        if not CTimeRangeEdit.validator:
            CTimeRangeEdit.validator = CTimeRangeValidator()
        return CTimeRangeEdit.validator
        

    def setTimeRange(self, range):
        if range:
            start, finish = range
            self.setText(start.toString('HH:mm')+' - ' +finish.toString('HH:mm'))
        else:
            self.setText('')
        self.setCursorPosition(0)

    def setStrTimeRange(self, range):
        if range:
            start, finish = range
            self.setText(start + ' - ' + finish)
        else:
            self.setText('')
        self.setCursorPosition(0)

    def timeRange(self):
        times = self.text().split('-')
        if len(times) == 2:
            start = stringToTime(times[0])
            finish = stringToTime(times[1])
            if start.isValid() and finish.isValid():
                return start, finish
        return None


class CTimeValidator():
    def validate(self, input, pos):
        return 1

class CTimeEdit(QtGui.QLineEdit):
    validator = None
    
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setInputMask('09:99')
#        self.setValidator(self.getRangeValidator())
        
    def getValidator(self):
        if not CTimeEdit.validator:
            CTimeEdit.validator = CTimeValidator()
        return CTimeEdit.validator
        

    def setTime(self, time):
        self.setText(time.toString('HH:mm'))
        self.setCursorPosition(0)


    def time(self):
        return stringToTime(self.text())

        
def stringToTime(s):
    try:
        parts = s.split(':')
        if parts>=2:
            hours = trim(parts[0])
            minuts = trim(parts[1])
            if hours or minuts:
                return QTime(int('0'+hours), int('0'+minuts))
    except:
        pass
    return QTime()
