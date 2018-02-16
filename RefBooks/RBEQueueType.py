# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

__author__ = 'atronah'

'''
    author: atronah
    date:   31.10.2014

    rbEQueueType refbook editor (general module located in library.ElectronicQueue).

'''

from PyQt4 import QtGui


from RefBooks.Tables import rbCode, rbName
from library.ItemsListDialog import CItemsListDialogEx, CItemEditorBaseDialog
from library.TableModel import CTextCol, CBoolCol, CDesignationCol
from library.interchange import setLineEditValue, getLineEditValue, getCheckBoxValue, getRBComboBoxValue, \
    setRBComboBoxValue, setCheckBoxValue


class CRBEQueueType(CItemsListDialogEx):
    def __init__(self, parent):
        super(CRBEQueueType, self).__init__(parent, [
            CTextCol(u'Код',              [rbCode],         20),
            CTextCol(u'Наименование',     [rbName],         40),
            CTextCol(u'Префикс номерка',  ['ticketPrefix'],  40),
            CDesignationCol(u'Подразделение', ['orgStructure_id'], ('OrgStructure', 'name'), 5),
            CBoolCol(u'Сразу готов к вызову', ['isImmediatelyReady'], 40),
            ], 'rbEQueueType', [rbCode, rbName])
        self.setWindowTitleEx(u'Типы электронной очереди')

    def getItemEditor(self):
        return CRBEQueueTypeEditor(self)


class CRBEQueueTypeEditor(CItemEditorBaseDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbEQueueType')
        self.setupUi(self)
        # self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип электронной очередь')
        self.setupDirtyCather()

    @staticmethod
    def setupUi(window):
        layout = QtGui.QGridLayout()


        # subLayout = QtGui.QHBoxLayout()
        window.lblCode = QtGui.QLabel(u'&Код')
        window.edtCode = QtGui.QLineEdit()
        window.lblCode.setBuddy(window.edtCode)
        layout.addWidget(window.lblCode, 0, 0)
        layout.addWidget(window.edtCode, 0, 1)
        # subLayout.addWidget(window.lblCode)
        # subLayout.addWidget(window.edtCode)
        # layout.addLayout(subLayout)

        # subLayout = QtGui.QHBoxLayout()
        window.lblName = QtGui.QLabel(u'&Название очереди')
        window.edtName = QtGui.QLineEdit()
        window.lblName.setBuddy(window.edtName)
        layout.addWidget(window.lblName, 1, 0)
        layout.addWidget(window.edtName, 1, 1)
        # subLayout.addWidget(window.lblName)
        # subLayout.addWidget(window.edtName)
        # layout.addLayout(subLayout)


        # subLayout = QtGui.QHBoxLayout()
        window.lblTicketPrefix = QtGui.QLabel(u'&Префикс номерка')
        window.edtTicketPrefix = QtGui.QLineEdit()
        window.lblTicketPrefix.setBuddy(window.edtTicketPrefix)
        layout.addWidget(window.lblTicketPrefix, 2, 0)
        layout.addWidget(window.edtTicketPrefix, 2, 1)
        # subLayout.addWidget(window.lblTicketPrefix)
        # subLayout.addWidget(window.edtTicketPrefix)
        # layout.addLayout(subLayout)


        # subLayout = QtGui.QHBoxLayout()
        window.lblOrgStructure = QtGui.QLabel(u'&Базовое подразделение')
        window.edtOrgStructure = COrgStructureComboBox(window)
        window.lblOrgStructure.setBuddy(window.edtOrgStructure)
        layout.addWidget(window.lblOrgStructure, 3, 0)
        layout.addWidget(window.edtOrgStructure, 3, 1)
        # subLayout.addWidget(window.lblOrgStructure)
        # subLayout.addWidget(window.edtOrgStructure)
        # layout.addLayout(subLayout)

        window.chkImmediatelyReady = QtGui.QCheckBox(u'Считать талоны очереди готовыми к вызову сразу после выдачи')
        layout.addWidget(window.chkImmediatelyReady, 4, 0, 1, 2)

        window.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        window.buttonBox.accepted.connect(window.accept)
        window.buttonBox.rejected.connect(window.reject)
        layout.addWidget(window.buttonBox, 5, 0, 1, 2)

        window.setLayout(layout)


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,         record, 'code')
        setLineEditValue(   self.edtName,         record, 'name')
        setLineEditValue(   self.edtTicketPrefix, record, 'ticketPrefix')
        setRBComboBoxValue( self.edtOrgStructure,  record, 'orgStructure_id')
        setCheckBoxValue(   self.chkImmediatelyReady, record, 'isImmediatelyReady')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,         record, 'code')
        getLineEditValue(   self.edtName,         record, 'name')
        setLineEditValue(   self.edtTicketPrefix, record, 'ticketPrefix')
        getRBComboBoxValue( self.edtOrgStructure,  record, 'orgStructure_id')
        getCheckBoxValue(   self.chkImmediatelyReady, record, 'isImmediatelyReady')
        return record
