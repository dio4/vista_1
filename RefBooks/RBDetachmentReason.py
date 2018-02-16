# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 25.11.2013

@author: atronah
"""

from PyQt4 import QtCore, QtGui

from library.crbcombobox        import CRBComboBox
from library.interchange        import setLineEditValue, setRBComboBoxValue,  getLineEditValue, getRBComboBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol, CRefBookCol

from RefBooks.Tables            import rbCode, rbName, rbAttachType, rbDetachmentReason


class CRBDetachmentReasonList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',                     [rbCode], 10),
            CTextCol(u'Наименование',            [rbName], 30),
            CRefBookCol(u'Тип прикрепления',     ['attachType_id'], rbAttachType, 20),
            ], rbDetachmentReason, [rbCode, rbName])
        self.setWindowTitleEx(u'Причина открепления')

    def getItemEditor(self):
        return CRBDetachmentReasonEditor(self)
#
# ##########################################################################
#

class CRBDetachmentReasonEditor(CItemEditorBaseDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbDetachmentReason)
        self.setupUi()
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Причина открепления')
        self.cmbAttachType.setTable(rbAttachType, False)
        self.setupDirtyCather()
        
    
    def setupUi(self):
        self.edtCode = QtGui.QLineEdit()
        self.lblCode = QtGui.QLabel(u'&Код')
        self.lblCode.setBuddy(self.edtCode)
        
        self.edtName = QtGui.QLineEdit()
        self.lblName = QtGui.QLabel(u'&Наименование')
        self.lblName.setBuddy(self.edtName)
        
        self.cmbAttachType = CRBComboBox(self)
        self.lblAttachType = QtGui.QLabel(u'&Тип прикрепления')
        self.lblAttachType.setBuddy(self.cmbAttachType)
        
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                                QtCore.Qt.Horizontal)
        
        
        layout = QtGui.QGridLayout()
        layout.addWidget(self.lblCode, 0, 0, 1, 1)
        layout.addWidget(self.edtCode, 0, 1, 1, 1)
        layout.addWidget(self.lblName, 1, 0, 1, 1)
        layout.addWidget(self.edtName, 1, 1, 1, 1)
        layout.addWidget(self.lblAttachType, 2, 0, 1, 1)
        layout.addWidget(self.cmbAttachType, 2, 1, 1, 1)
        layout.addWidget(self.buttonBox, 3, 0, 1, 2)
        
        self.setLayout(layout)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)        
        QtCore.QMetaObject.connectSlotsByName(self)
    

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtCode,          record, 'code')
        setLineEditValue(   self.edtName,          record, 'name')
        setRBComboBoxValue( self.cmbAttachType,    record, 'attachType_id')



    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtCode,          record, 'code')
        getLineEditValue(   self.edtName,          record, 'name')
        getRBComboBoxValue( self.cmbAttachType,    record, 'attachType_id')
        return record
