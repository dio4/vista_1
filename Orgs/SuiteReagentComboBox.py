# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox            import CRBComboBox
from library.InDocTable             import CRBInDocTableCol
from library.TableModel             import CTableModel, CTextCol
from library.Utils                  import getPref, setPref

from Ui_SuiteReagentComboBoxPopup   import Ui_SuiteReagentPopupForm


class CSuiteReagentPopup(QtGui.QFrame, Ui_SuiteReagentPopupForm):
    __pyqtSignals__ = ('suiteReagentSelected(int)',
                      )
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.tableModel = CSuiteReagentTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.tblSuiteReagent.setModel(self.tableModel)
        self.tblSuiteReagent.setSelectionModel(self.tableSelectionModel)
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CSuiteReagentPopup', {})
        # self.tblSuiteReagent.loadPreferences(preferences)
        self._testId = None
        self.setTestId(self._testId)
        self._tissueJournalDate = None
        self.setTissueJournalDate(self._tissueJournalDate)
        
    def setTissueJournalDate(self, date):
        self._tissueJournalDate = date if date and date.isValid() else None
        self.setVisibleNotOverdue(bool(self._tissueJournalDate))
        self.setVisibleStartOperation(bool(self._tissueJournalDate))
        
    def setVisibleNotOverdue(self, value):
        self.chkNotOverdue.setChecked(value)
        self.chkNotOverdue.setVisible(value)
        
    def setVisibleStartOperation(self, value):
        self.chkStartOperation.setChecked(value)
        self.chkStartOperation.setVisible(value)
        
    def setTestId(self, testId):
        self._testId = testId
        self.setVisibleOnlyByTest(bool(self._testId))
        
    def setVisibleOnlyByTest(self, value):
        self.chkOnlyByTest.setChecked(value)
        self.chkOnlyByTest.setVisible(value)
        
    # def closeEvent(self, event):
    #     preferences = self.tblSuiteReagent.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CEquipmentPopupView', preferences)
    #     QtGui.QFrame.closeEvent(self, event)
        
    def getSuiteReagentIdList(self):
        db = QtGui.qApp.db
        tableSuiteReagent     = db.table('SuiteReagent')
        tableSuiteReagentTest = db.table('SuiteReagent_Test')
        tableProbe            = db.table('Probe')
        
        queryTable = tableSuiteReagent
        
        cond = []
        if self.chkOnlyByTest.isChecked():
            queryTable = queryTable.innerJoin(tableSuiteReagentTest, 
                                              tableSuiteReagentTest['master_id'].eq(tableSuiteReagent['id']))
            cond.append(tableSuiteReagentTest['test_id'].eq(self._testId))
        
        if self.chkNotOverdue.isChecked():
            cond.append(tableSuiteReagent['expiryDate'].ge(self._tissueJournalDate))
            
        if self.chkStartOperation.isChecked():
            cond.append(tableSuiteReagent['startOperationDate'].le(self._tissueJournalDate))
            
        if self.chkNotOverLimit.isChecked():
            cond.append('SuiteReagent.`execTestQuantity` <= (SELECT SUM(Probe.`id`) FROM Probe WHERE `suiteReagent_id`=SuiteReagent.`id`)')
            
        idList = db.getDistinctIdList(queryTable, tableSuiteReagent['id'].name(), cond)
        return idList

            
    def setIdList(self, idList, posToId=None):
        if bool(idList):
            self.tblSuiteReagent.setIdList(idList, posToId)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.tblSuiteReagent.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
        
    def on_buttonBox_apply(self, id=None):
        idList = self.getSuiteReagentIdList()
        self.setIdList(idList, id)
        
    def on_buttonBox_reset(self):
        for chkWidget in [self.chkOnlyByTest, 
                          self.chkNotOverdue, 
                          self.chkStartOperation, 
                          self.chkNotOverLimit]:
            chkWidget.setChecked(True)
            
        self.on_buttonBox_apply()
        
    def emitSuiteReagentSelected(self, id):
        self.emit(QtCore.SIGNAL('suiteReagentSelected(int)'), id)
        self.hide()
        
    def setSuiteReagents(self):
        self.on_buttonBox_apply(None)
        
    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()
            
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblSuiteReagent_clicked(self, index):
        itemId = self.tblSuiteReagent.itemId(index)
        self.emitSuiteReagentSelected(itemId)


class CSuiteReagentComboBox(CRBComboBox):
    def __init__(self, parent):
        CRBComboBox.__init__(self, parent)
        self.popupView  = None
        self._tableName = 'SuiteReagent'
        self._testId = None
        self._tissueJournalDate = None
        CRBComboBox.setTable(self, self._tableName)
        
    def showPopup(self):
        if not self.popupView:
            self.popupView = CSuiteReagentPopup(self)
            self.connect(self.popupView,QtCore.SIGNAL('suiteReagentSelected(int)'), self.setValue)
        self.popupView.setTestId(self._testId)
        self.popupView.setTissueJournalDate(self._tissueJournalDate)
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self.popupView.sizeHint()
        width= max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self.popupView.move(pos)
        self.popupView.resize(size)
        self.popupView.setSuiteReagents()
        self.popupView.show()
        
    def setTestId(self, testId):
        self._testId = testId

    def setTissueJournalDate(self, tissueJournalDate):
        self._tissueJournalDate = tissueJournalDate
        

# #############################################################

class CSuiteReagentTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, cols=[
                CTextCol(u'Код',                          ['code'],               20),
                CTextCol(u'Наименование',                 ['name'],               40),
#                CRefBookCol(u'Ответственный',             ['recipientPerson_id'], 'vrbPersonWithSpeciality', 10), 
#                CDateCol(u'Дата выпуска',                 ['releaseDate'],        10), 
#                CDateCol(u'Дата поступления',             ['supplyDate'],         12), 
#                CDateCol(u'Дата передачи в работу',       ['startOperationDate'], 14), 
#                CDateCol(u'Срок годности',                ['expiryDate'],         10),
#                CNumCol(u'Плановое количество тестов',    ['planTestQuantity'],   15), 
#                CNumCol(u'Выполненное количество тестов', ['execTestQuantity'],   15), 
#                CTextCol(u'Производитель',                ['manufacturer'],       10), 
#                CTextCol(u'Условия хранения',             ['storageConditions'],  12)
            ], tableName='SuiteReagent')
            
class CRBSuiteReagentCol(CRBInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, tableName, **params)
        self._testId = params.get('testId', None)
        self._tissueJournalDate = params.get('tissueJournalDate', None)
        
    def createEditor(self, parent):
        editor = CSuiteReagentComboBox(parent)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, needCache=False, order = self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        if self._testId:
            editor.setTestId(self._testId)
        if self._tissueJournalDate:
            editor.setTissueJournalDate(self._tissueJournalDate)
        return editor
