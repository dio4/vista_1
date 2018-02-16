# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.InDocTable      import CInDocTableModel, CInDocTableCol, CRBInDocTableCol
from library.interchange     import getLineEditValue, getRBComboBoxValue, getSpinBoxValue, setLineEditValue, \
                                    setRBComboBoxValue, setSpinBoxValue
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel      import CNumCol, CTextCol
from library.Utils           import forceRef

from Orgs.EquipmentComboBox  import CEquipmentComboBox

from RefBooks.Tables         import rbCode, rbName

from Ui_TestListDialog       import Ui_TestListDialog
from Ui_RBTestEditor         import Ui_RBTestEditorDialog


class CRBTestList(CItemsListDialog, Ui_TestListDialog):
    setupUi       = Ui_TestListDialog.setupUi
    retranslateUi = Ui_TestListDialog.retranslateUi

    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CNumCol(u'Позиция', ['position'], 15)
            ], 'rbTest', [rbCode, rbName])
        self.input_timer = QtCore.QTimer()
        self.input_timer.setSingleShot(True)
        self.input_timer.timeout.connect(self.update_list)

        self.cmbGroup.setTable('rbTestGroup')
        self.setWindowTitleEx(u'Показатели исследований')

    def update_list(self):
        self.renewListAndSetTo(self.currentItemId())

    def getItemEditor(self):
        return CRBTestEditor(self)

    def select(self, props):
        table = self.model.table()
        cond = []
        if self.chkGroup.isChecked() and self.cmbGroup.value():
            cond.append(table['testGroup_id'].eq(self.cmbGroup.value()))
        if self.chkCode.isChecked() and self.edtCode.text():
            cond.append(table['code'].like(u'%{}%'.format(self.edtCode.text())))
        if self.chkName.isChecked() and self.edtName.text():
            cond.append(table['name'].like(u'%{}%'.format(self.edtName.text())))
        cond = cond if cond else ''
        return QtGui.qApp.db.getIdList(table.name(), self.idFieldName, cond, self.order)

    @QtCore.pyqtSlot(bool)
    def on_chkGroup_clicked(self, value):
        self.renewListAndSetTo(self.currentItemId())
        if value:
            self.cmbGroup.setFocus()

    @QtCore.pyqtSlot(int)
    def on_cmbGroup_currentIndexChanged(self, index):
        self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(bool)
    def on_chkName_clicked(self, value):
        self.renewListAndSetTo(self.currentItemId())
        if value:
            self.edtName.setFocus()

    @QtCore.pyqtSlot(str)
    def on_edtName_textChanged(self, index):
        self.input_timer.start(300)

    @QtCore.pyqtSlot(bool)
    def on_chkCode_clicked(self, value):
        self.renewListAndSetTo(self.currentItemId())
        if value:
            self.edtCode.setFocus()

    @QtCore.pyqtSlot(str)
    def on_edtCode_textChanged(self, index):
        self.input_timer.start(300)


class CRBTestEditor(CItemEditorBaseDialog, Ui_RBTestEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbTest')
        self.setupUi(self)
        self.addModels('TestEquipments', CTestEquipmentModel(self))
        self.addModels('TestAnalog',     CTestAnalogModel(self))
        self.setModels(self.tblEquipments, self.modelTestEquipments, self.selectionModelTestEquipments)
        self.setModels(self.tblTestAnalog, self.modelTestAnalog, self.selectionModelTestAnalog)

        self.tblEquipments.addPopupSelectAllRow()
        self.tblEquipments.addPopupClearSelectionRow()
        self.tblEquipments.addPopupDelRow()

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Показатель исследования')

        self.cmbTestGroup.setTable('rbTestGroup', addNone=True)

        self.actSyncTestAnalogList = QtGui.QAction(u'Синхронизировать аналоги тестов по текущему', self)
        self.tblTestAnalog.createPopupMenu(actions=[self.actSyncTestAnalogList])
        self.connect(self.actSyncTestAnalogList, QtCore.SIGNAL('triggered()'), self.syncTestAnalogListByCurrent)

        self.connect(self.tblTestAnalog.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.on_aboutToShow)

        self.setupDirtyCather()

    def on_aboutToShow(self):
        self.actSyncTestAnalogList.setEnabled(bool(len(self.modelTestAnalog.items())))

    def syncTestAnalogListByCurrent(self):
        db = QtGui.qApp.db
        testIdList = [forceRef(item.value('analogTest_id')) for item in self.modelTestAnalog.items()]
        currentTestId = self.itemId()
        table = db.table('rbTest_AnalogTest')
        for testId in testIdList:
            localAnalogTestIdList = list(set(testIdList) - set([testId])) + [currentTestId]
            for analogTestId in localAnalogTestIdList:
                cond = [table['master_id'].eq(testId),
                        table['analogTest_id'].eq(analogTestId)]
                record = db.getRecordEx(table, '*', cond)
                if not record:
                    record = table.newRecord()
                    record.setValue('master_id', QtCore.QVariant(testId))
                    record.setValue('analogTest_id', QtCore.QVariant(analogTestId))
                    db.insertRecord(table, record)


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, rbCode)
        setLineEditValue(self.edtName, record, rbName)
        setRBComboBoxValue(self.cmbTestGroup, record, 'testGroup_id')
        setSpinBoxValue(self.edtPosition, record, 'position')

        itemId = self.itemId()
        self.modelTestEquipments.loadItems(itemId)
        self.modelTestAnalog.loadItems(itemId)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, rbCode)
        getLineEditValue(self.edtName, record, rbName)
        getRBComboBoxValue(self.cmbTestGroup, record, 'testGroup_id')
        getSpinBoxValue(self.edtPosition, record, 'position')
        return record

    def saveInternals(self, id):
        self.modelTestEquipments.saveItems(id)
        self.modelTestAnalog.saveItems(id)


# ##############################################
class CRBEquipmentCol(CRBInDocTableCol):
    def createEditor(self, parent):
        editor = CEquipmentComboBox(parent)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order = self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor


class CTestEquipmentModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbEquipment_Test', 'id', 'test_id', parent)
        self.addCol(CRBEquipmentCol(   u'Оборудование',  'equipment_id',   15, 'rbEquipment'))
        self.addCol(CInDocTableCol(u'Код теста', 'hardwareTestCode', 15))
        self.addCol(CInDocTableCol(u'Наименование теста', 'hardwareTestName', 15))
        self.addCol(CInDocTableCol(u'Код образца', 'hardwareSpecimenCode', 15))
        self.addCol(CInDocTableCol(u'Наименование образца', 'hardwareSpecimenName', 15))


# ####

class CRBTestAnalogCol(CRBInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, parentEditor, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, tableName, **params)
        self._parentEditor = parentEditor

    def createEditor(self, parent):
        self.filter = u'`id` != %d' % self._parentEditor.itemId()
        return CRBInDocTableCol.createEditor(self, parent)


class CTestAnalogModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbTest_AnalogTest', 'id', 'master_id', parent)
        self.addCol(CRBTestAnalogCol(u'Тест аналог',  'analogTest_id',   15, 'rbTest', parent, showFields=2))
