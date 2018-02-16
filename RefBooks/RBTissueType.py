# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Ui_RBTissueTypeEditor import Ui_TissueTypeEditorDialog
from library.ItemsListDialog import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel import CBoolCol, CEnumCol, CTextCol
from library.Utils import forceInt
from library.interchange import getCheckBoxValue, getComboBoxValue, getLineEditValue, setCheckBoxValue, setComboBoxValue, setLineEditValue


class TisssueTypeCounterResetType:
    Daily = 0
    Weekly = 1
    Monthly = 2
    HalfYearly = 3
    Yearly = 4
    Always = 5

    nameMap = {
        Daily     : u'День',
        Weekly    : u'Неделя',
        Monthly   : u'Месяц',
        HalfYearly: u'Полгода',
        Yearly    : u'Год',
        Always    : u'Постоянно'
    }
    nameList = [nameMap[k] for k in sorted(nameMap.keys())]


class CRBTissueTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', ['code'], 10),
            CTextCol(u'Наименование', ['name'], 30),
            CEnumCol(u'Пол', ['sex'], [u'Любой', u'М', u'Ж'], 5),
            CBoolCol(u'Ручной ввод идентификатора', ['counterManualInput'], 15),
            CEnumCol(u'Период уникальности идентификатора', ['counterResetType'], TisssueTypeCounterResetType.nameList, 15)
        ], 'rbTissueType', ['code', 'name'])
        self.setWindowTitleEx(u'Типы биоматериалов')

    def getItemEditor(self):
        return CRBTissueTypeListEditor(self)


class CRBTissueTypeListEditor(CItemEditorBaseDialog, Ui_TissueTypeEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbTissueType')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип биоматериала')
        self.setupDirtyCather()
        self.chkCounterManualInput.clicked.connect(self.disableIdentCounterFields)
        self.chkIdentCounter.clicked.connect(self.checkCreateCounter)
        self.tissueId = None
        self.haveCounter = True

    def checkCreateCounter(self):
        if self.chkIdentCounter.isChecked():
            self.createIdentCounter()

    def createIdentCounter(self):
        if not self.haveCounter:
            if QtGui.QMessageBox.question(
                    self,
                    u'Внимание!',
                    u'Счетчик идентификатора не был создан.\nХотите создать его?',
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.Yes
            ) == QtGui.QMessageBox.Yes:
                self.createCounter()
            else:
                self.chkIdentCounter.setDisabled(True)
                self.chkIdentCounter.setChecked(False)

    def disableIdentCounterFields(self):
        if self.chkCounterManualInput.isChecked():
            self.chkIdentCounter.setChecked(not self.chkCounterManualInput.isChecked())
        else:
            self.createIdentCounter()

    def checkDataEntered(self):
        if self.chkIdentCounter.isChecked():
            self.setCounterValue()

        if not str(self.edtExternalIdLimit.text()).isdigit():
            QtGui.QMessageBox.warning(
                self,
                u'Внимание!',
                u'Ограничение длины идентификатора должно быть числом.',
                QtGui.QMessageBox.Ok
            )
            return False
        if not str(self.edtCounterValue.text()).isdigit():
            QtGui.QMessageBox.warning(
                self,
                u'Внимание!',
                u'Значение счетчика идентификатора должно быть числом.',
                QtGui.QMessageBox.Ok
            )
            return False
        return True

    def getCounterValue(self):
        db = QtGui.qApp.db
        record = db.getRecordEx(db.table('rbCounter'), cols='value, reset', where='code = "tis%s"' % self.tissueId)
        if not record:
            self.haveCounter = False
            return 0
        else:
            counter = forceInt(record.value('value'))

            if forceInt(record.value('reset')):
                setComboBoxValue(self.cmbCounterResetType, record, 'reset')

            self.chkIdentCounter.setEnabled(True)
            self.chkIdentCounter.setChecked(True)

            return counter

    def setCounterValue(self):

        db = QtGui.qApp.db
        db.query(u"""
            UPDATE `rbCounter`
            SET
                `name` = "Счетчик индентификатора [%s]",
                `reset` = %s,
                `value` = %s
            WHERE `code` = "tis%s"
        """ % (
            self.edtName.text(),
            self.cmbCounterResetType.currentIndex(),
            self.edtCounterValue.text(),
            self.tissueId,
        ))

    def createCounter(self):
        db = QtGui.qApp.db
        db.query(u"""
        INSERT INTO `rbCounter` (`code`, `name`) VALUE ("tis%s", "%s")
        """ % (self.tissueId, u'Счетчик индентификатора [%s]' % self.edtName.text())
                 )

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setComboBoxValue(self.cmbSex, record, 'sex')
        setCheckBoxValue(self.chkCounterManualInput, record, 'counterManualInput')
        setComboBoxValue(self.cmbCounterResetType, record, 'counterResetType')
        setLineEditValue(self.edtExternalIdLimit, record, 'issueExternalIdLimit')
        self.tissueId = forceInt(record.value('id'))
        self.edtCounterValue.setText(str(self.getCounterValue()))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getComboBoxValue(self.cmbSex, record, 'sex')
        getCheckBoxValue(self.chkCounterManualInput, record, 'counterManualInput')
        getComboBoxValue(self.cmbCounterResetType, record, 'counterResetType')
        getLineEditValue(self.edtExternalIdLimit, record, 'issueExternalIdLimit')
        return record
