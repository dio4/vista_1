# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

"""
hl7 xml interface
"""
from PyQt4.QtCore import *
from bases import THl7Message


def datetimeToHl7(dt):
    if type(dt) == QDate:
        return unicode(dt.toString('yyyyMMdd000000'))
    elif type(dt) == QDateTime:
        return unicode(dt.toString('yyyyMMddhhmmss'))
    else:
        return dt.strftime('%Y%m%d%H%M%S')


def datetimeFromHl7(s):
    return QDateTime.fromString(s.ljust(14,'0')[:14],'yyyyMMddhhmmss')


def messageFromDom(element):
    return THl7Message.fromDom(element)