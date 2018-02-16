# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Ui_RBCounterEditor import Ui_RBCounterEditor
from library.ItemsListDialog import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel import CBoolCol, CDateCol, CEnumCol, CNumCol, CTextCol
from library.interchange import getCheckBoxValue, getComboBoxValue, getDateEditValue, getLineEditValue, getSpinBoxValue, setBigIntSpinBoxValue, setCheckBoxValue, setComboBoxValue, setDateEditValue, \
    setLineEditValue


class CRBCounterList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',                     ['code'],         10),
            CTextCol(u'Наименование',            ['name'],         30),
            CNumCol(u'Текущее значение',         ['value'],        16),
            CTextCol(u'Префикс',                 ['prefix'],       10),
            CTextCol(u'Постфикс',                ['postfix'],      10),
            CTextCol(u'разделитель',             ['separator'],    10),
            CEnumCol(u'Сброс',                   ['reset'],  [u'Не сбрасывается',
                                                              u'Через сутки',
                                                              u'Через неделю',
                                                              u'Через месяц',
                                                              u'Через квартал',
                                                              u'Через полугодие',
                                                              u'Через год'],
                                                                   16),
            CDateCol(u'Дата начала работы',      ['startDate'],    10),
            CDateCol(u'Дата последнего сброса',  ['resetDate'],    10),
            CBoolCol(u'Флаг последовательности', ['sequenceFlag'], 10)
            ], 'rbCounter', ['code', 'name'])
        self.setWindowTitleEx(u'Счетчики')

    def getItemEditor(self):
        return CRBCounterListEditor(self)



class CRBCounterListEditor(CItemEditorBaseDialog, Ui_RBCounterEditor):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbCounter')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Счетчик')
        self.setupDirtyCather()
        self.btnAddOrgCounter.clicked.connect(self.on_btnAddOrgCounter_click)
        self.cmbCompulsoryPolisCompany.setEnabled(False)
        self.oldCounterCode = ''
        self.cmbCompulsoryPolisCompany.setTable('rbFinance')
        self.edtValue.setMaximum(9999999999)
        #self.cmbCompulsoryPolisCompany.setVisible(False)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setBigIntSpinBoxValue(self.edtValue, record, 'value')
        setLineEditValue(self.edtPrefix, record, 'prefix')
        setLineEditValue(self.edtPostfix, record, 'postfix')
        setLineEditValue(self.edtSeparator, record, 'separator')
        setCheckBoxValue(self.chkSequenceFlag, record, 'sequenceFlag')
        setComboBoxValue(self.cmbReset, record, 'reset')
        setDateEditValue(self.edtStartDate, record, 'startDate')
        try:
            self.oldCounterCode = self.edtCode.text()
            if self.edtCode.text()[0] == 'p':
                self.cmbCompulsoryPolisCompany.setValue(int(self.edtCode.text()[1:]))
                self.btnAddOrgCounter.setChecked(True)
                self.on_btnAddOrgCounter_click()

        except:
            self.btnAddOrgCounter.setChecked(False)
            self.on_btnAddOrgCounter_click()

    # Проверяем на наличие счетчика для ИФ: True - have counter, False - counter is apsent
    def checkDuplicateOrgCode(self):
        if self.btnAddOrgCounter.isChecked() and \
                self.oldCounterCode != 'p%s' % self.cmbCompulsoryPolisCompany.value():
            db = QtGui.qApp.db
            rec = db.getRecordEx(table='rbCounter', cols='*', where="code = 'p%s'" % self.cmbCompulsoryPolisCompany.value())
            if rec:
                QtGui.QMessageBox.critical(self,
                                           u'Внимание!',
                                           u'Добавления еще одного счетчика для текущего ИФ невозможно.\nСчетчик должен быть один.',
                                           QtGui.QMessageBox.Ok,
                                           QtGui.QMessageBox.Ok
                                           )
                return True
        else:
            return False

    # Проверяем выбран ли ИФ
    def checkChoice(self):
        if self.btnAddOrgCounter.isChecked() and self.cmbCompulsoryPolisCompany.value() <= 0:
            QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Вы не выбрали источник финансирования.',
                                       QtGui.QMessageBox.Ok,
                                       QtGui.QMessageBox.Ok
                                       )
            return True
        else:
            return False

    def done(self, result):
        if result > 0 and self.checkDuplicateOrgCode():
            return
        if result > 0 and self.checkChoice():
            return
        if self.saveData() if result > 0 else self.canClose():
            self.saveDialogPreferences()
            QtGui.QDialog.done(self, result)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        if self.btnAddOrgCounter.isChecked():
            self.edtCode.setText('p%s' % self.cmbCompulsoryPolisCompany.value())
            self.edtName.setText(u'[Счетчик ИФ] %s' % self.cmbCompulsoryPolisCompany.currentText())
            self.edtPrefix.setText('')
            self.edtPostfix.setText('')
            self.edtSeparator.setText('')

        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getSpinBoxValue(self.edtValue, record, 'value')
        getLineEditValue(self.edtPrefix, record, 'prefix')
        getLineEditValue(self.edtPostfix, record, 'postfix')
        getLineEditValue(self.edtSeparator, record, 'separator')
        getCheckBoxValue(self.chkSequenceFlag, record, 'sequenceFlag')
        getComboBoxValue(self.cmbReset, record, 'reset')
        getDateEditValue(self.edtStartDate, record, 'startDate')
        return record

    def on_btnAddOrgCounter_click(self):
        self.edtName.setText('-')
        self.edtCode.setText('-')
        self.edtCode.setEnabled(not self.btnAddOrgCounter.isChecked())
        self.edtPrefix.setEnabled(not self.btnAddOrgCounter.isChecked())
        self.edtPostfix.setEnabled(not self.btnAddOrgCounter.isChecked())
        self.edtSeparator.setEnabled(not self.btnAddOrgCounter.isChecked())

        self.edtName.setEnabled(not self.btnAddOrgCounter.isChecked())
        self.cmbCompulsoryPolisCompany.setEnabled(self.btnAddOrgCounter.isChecked())
