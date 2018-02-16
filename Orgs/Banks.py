# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.interchange        import getLineEditValue, setLineEditValue
from library.ItemsListDialog    import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel         import CTextCol
from library.Utils              import forceStringEx, forceString

from Ui_BankEditor              import Ui_BankEditorDialog


class CBanksList(CItemsListDialog):
    def __init__(self, parent, forSelect=False):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'БИК',                    ['BIK'],        10),
            CTextCol(u'Наименование',           ['name'],       40),
            CTextCol(u'Наименование филиала',   ['branchName'], 40),
            CTextCol(u'Корр.счет',              ['corrAccount'],20),
            CTextCol(u'Суб.счет',               ['subAccount'], 20),
            ], 'Bank', ['BIK', 'name', 'branchName'],
            forSelect, None
            )
        self.setWindowTitleEx(u'Банки')


    def getItemEditor(self):
        return CBankEditor(self)
#
# ##########################################################################
#

class CBankEditor(CItemEditorBaseDialog, Ui_BankEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Bank')
        self.setupUi(self)
        self.setWindowTitleEx(u'Банк')
        self.setupDirtyCather()
#        self.edtBIK.setValidator(QtGui.QRegExpValidator(QRegExp ('[0-9]*'), self))
#        self.edtCorrAccount.setValidator(QtGui.QRegExpValidator(QRegExp ('[0-9]*'), self))
#        self.edtSubAccount.setValidator(QtGui.QRegExpValidator(QRegExp ('[0-9]*'), self))


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtBIK,           record, 'BIK')
        setLineEditValue(self.edtName,          record, 'name')
        setLineEditValue(self.edtBranchName,    record, 'branchName')
        setLineEditValue(self.edtCorrAccount,   record, 'corrAccount')
        setLineEditValue(self.edtSubAccount,    record, 'subAccount')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtBIK,           record, 'BIK')
        getLineEditValue(self.edtName,          record, 'name')
        getLineEditValue(self.edtBranchName,    record, 'branchName')
        getLineEditValue(self.edtCorrAccount,   record, 'corrAccount')
        getLineEditValue(self.edtSubAccount,    record, 'subAccount')
        return record


    def checkDataEntered(self):
        result = True
        result = result and (forceStringEx(self.edtName.text()) or  self.checkInputMessage(u'наименование', False, self.edtName))
        result = result and (forceStringEx(self.edtBIK.text()) or  self.checkInputMessage(u'БИК', False, self.edtBIK))
#        result = result and (forceStringEx(self.edtBranchName.text()) or  self.checkInputMessage(u'наименование филиала', True, self.edtBranchName))
        result = result and (forceStringEx(self.edtCorrAccount.text()) or  self.checkInputMessage(u'корр.счет', True, self.edtCorrAccount))
#        result = result and (forceStringEx(self.edtSubAccount.text()) or  self.checkInputMessage(u'суб.счет', False, self.edtSubAccount))

        # проверка на уникальность:
        if self.itemId():
            same = QtGui.qApp.db.query(u"""SELECT id
                                    FROM Bank
                                    WHERE BIK='%s' and branchName='%s' and id!=%d"""%(self.edtBIK.text(), self.edtBranchName.text(), self.itemId()))
        else:
            same = QtGui.qApp.db.query(u"""SELECT id
                                    FROM Bank
                                    WHERE BIK='%s' and branchName='%s'"""%(self.edtBIK.text(), self.edtBranchName.text()))
        if same.next():
            QtGui.QMessageBox.warning(self, u'Банк уже существует', u'Банк с таким BIK и именем филиала уже существует (id=%s).'%forceString(same.record().value(0)))
            return False
        return result
