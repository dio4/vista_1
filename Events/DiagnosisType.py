# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from library.DbEntityCache      import CDbEntityCache
from library.InDocTable         import CInDocTableCol
from library.Utils              import forceRef, toVariant


class CDiagnosisTypeCol(CInDocTableCol, CDbEntityCache):
    # Комбо-бокс с типами диагнозов.
    # конструктор получает типы кодов, diagnosisTypeCodes соотв. заключительному, основному и соп. диагнозам

    names = [u'Закл', u'Осн', u'Соп']
    mapCodeToId = {}


    def __init__(self, title=u'Тип', fieldName='diagnosisType_id', width=5, diagnosisTypeCodes=None, smartMode=True, **params):
        if not diagnosisTypeCodes:
            diagnosisTypeCodes = []
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.ids = [self.codeToId(code) for code in diagnosisTypeCodes]
        self.smartMode = smartMode


    def toString(self, val, record):
        id = forceRef(val)
        if id in self.ids:
            return toVariant(CDiagnosisTypeCol.names[self.ids.index(id)])
        return QtCore.QVariant()


    def createEditor(self, parent):
        editor = QtGui.QComboBox(parent)
        return editor


    def setEditorData(self, editor, value, record):
        editor.clear()
        if value.isNull():
            value = record.value(self.fieldName())
        id = forceRef(value)
        if self.smartMode:
            if id == self.ids[0]:
                editor.addItem(CDiagnosisTypeCol.names[0], toVariant(self.ids[0]))
            elif id == self.ids[1]:
                if self.ids[0]:
                    editor.addItem(CDiagnosisTypeCol.names[0], toVariant(self.ids[0]))
                editor.addItem(CDiagnosisTypeCol.names[1], toVariant(self.ids[1]))
            else:
                editor.addItem(CDiagnosisTypeCol.names[2], toVariant(self.ids[2]))
        else:
            for itemName, itemId in zip(CDiagnosisTypeCol.names, self.ids):
                if itemId:
                    editor.addItem(itemName, toVariant(itemId))
        currentIndex = editor.findData(toVariant(id))
        editor.setCurrentIndex(currentIndex)


    def getEditorData(self, editor):
        return editor.itemData(editor.currentIndex())


    @classmethod
    def codeToId(cls, code):
        if code in CDiagnosisTypeCol.mapCodeToId:
            return CDiagnosisTypeCol.mapCodeToId[code]
        else:
            cls.connect()
            id = forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', code, 'id'))
            cls.mapCodeToId[code] = id
            return id


    @classmethod
    def purge(cls):
        cls.mapCodeToId.clear()