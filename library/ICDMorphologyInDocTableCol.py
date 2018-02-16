#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.ICDMorphologyCodeEdit import CICDMorphologyCodeEditEx

from library.InDocTable     import *

class CMKBMorphologyCol(CCodeRefInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, **params):
        CCodeRefInDocTableCol.__init__(self, title, fieldName, width, tableName, **params)
        self.filterCache = {}
    
    def createEditor(self, parent):
        editor = CICDMorphologyCodeEditEx(parent)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order = self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor
        
    def getEditorData(self, editor):
        return toVariant(editor.text())
        
    def setEditorData(self, editor, value, record):
        MKB = forceString(record.value('MKB'))
        if bool(MKB):
            filter = self.filterCache.get(MKB, None)
            if not filter:
                filter = editor.getMKBFilter(MKB)
                self.filterCache[MKB] = filter
#            editor.setMKBFilter(self.tableName, addNone=self.addNone, filter=filter)
            editor.setMKBFilter(filter)
        editor.setText(forceString(value))
        
        
        
        
        
        
