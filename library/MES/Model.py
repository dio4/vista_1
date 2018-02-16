#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *


def parseModel(model):
    result = []
    # model as string -> list of tuples (title, value)
    db = QtGui.qApp.db
    modelCodes = model.split('.')
    modelItems = db.getRecordList('mes.ModelDescription', ['name', 'fieldIdx', 'tableName'], order='idx')
    for item in modelItems:
        name = forceString(item.value('name'))
        fieldIdx = forceInt(item.value('fieldIdx'))
        tableName = forceString(item.value('tableName'))
        if 0<=fieldIdx<len(modelCodes):
            code = modelCodes[fieldIdx]
            value = db.translate(tableName,'code',code,'name')
            if value:
                value = forceString(value)
            else:
                value = u'{%s}' % code
        else:
            value = ''
        result.append((name,value))
    return result