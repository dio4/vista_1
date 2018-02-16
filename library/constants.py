# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

# action type code:
atcAmbulance = 'amb'
atcHome      = 'home'
atcExp       = 'exp'
atcTimeLine  = 'timeLine'

# event type code:
etcTimeTable = '0' # График

# DATE
dateLeftInfinity        = QtCore.QDate(2000, 1, 1)
dateRightInfinity       = QtCore.QDate(2200, 1, 1)
dateTimeLeftInfinity    = QtCore.QDateTime(dateLeftInfinity)
dateTimeRightInfinity   = QtCore.QDateTime(dateRightInfinity)