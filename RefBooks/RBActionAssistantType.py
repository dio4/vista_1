# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.ItemsListDialog import CItemsListDialogEx, CItemEditorDialog
from library.TableModel import CTextCol, CBoolCol
from library.interchange import setCheckBoxValue, getCheckBoxValue
from library.Utils import forceStringEx
from RefBooks.Tables import rbCode, rbName
from PyQt4 import QtGui


class CRBActionAssistantTypeList(CItemsListDialogEx):
    def __init__(self, parent):
        super(CRBActionAssistantTypeList, self).__init__(parent, [
            CTextCol(u'Код', [rbCode], 20),
            CTextCol(u'Имя', [rbName], 40),
            CBoolCol(u'Свободный ввод', ['isEnabledFreeInput'], 5)
            ], 'rbActionAssistantType', [rbCode, rbName])
        self.setWindowTitleEx(u'Типы ассистентов')

    def getItemEditor(self):
        return CRBActionAssistantTypeEditor(self)

    def select(self, props=None):
        if not props:
            props = {}
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(), self.idFieldName, "code not in ('assistant','assistant2','assistant3')", self.order)


class CRBActionAssistantTypeEditor(CItemEditorDialog):
    def __init__(self,  parent):
        super(CRBActionAssistantTypeEditor, self).__init__(parent, 'rbActionAssistantType')
        self.setWindowTitleEx(u'Редактировать тип ассистента')
        self.setupDirtyCather()

    @staticmethod
    def setupUi(window):
        layout = QtGui.QGridLayout()

        window.lblCode = QtGui.QLabel(u'&Код')
        window.edtCode = QtGui.QLineEdit()
        window.lblCode.setBuddy(window.edtCode)
        layout.addWidget(window.lblCode, 0, 0)
        layout.addWidget(window.edtCode, 0, 1)

        window.lblName = QtGui.QLabel(u'&Имя')
        window.edtName = QtGui.QLineEdit()
        window.lblName.setBuddy(window.edtName)
        layout.addWidget(window.lblName, 1, 0)
        layout.addWidget(window.edtName, 1, 1)

        window.chkFreeInput = QtGui.QCheckBox(u'&Свободный ввод')
        layout.addWidget(window.chkFreeInput, 2, 0, 1, 2)

        window.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        window.buttonBox.accepted.connect(window.accept)
        window.buttonBox.rejected.connect(window.reject)
        layout.addWidget(window.buttonBox, 5, 0, 1, 2)

        window.setLayout(layout)

    def setRecord(self, record):
        super(CRBActionAssistantTypeEditor, self).setRecord(record)
        setCheckBoxValue(self.chkFreeInput, record, 'isEnabledFreeInput')

    def getRecord(self):
        record = super(CRBActionAssistantTypeEditor, self).getRecord()
        getCheckBoxValue(self.chkFreeInput, record, 'isEnabledFreeInput')
        return record

    def checkDataEntered(self):
        result = super(CRBActionAssistantTypeEditor, self).checkDataEntered()
        code = forceStringEx(self.edtCode.text())
        if code in ('assistant','assistant2','assistant3'):
            result = False
            message = u"""Код ассистента не может быть равен следущим значениям:\nassistant, assistant2, assistant3"""
            QtGui.QMessageBox.warning(self, u'Внимание!', message, QtGui.QMessageBox.Ok)
        return result
