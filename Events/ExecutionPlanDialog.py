# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.DialogBase   import CDialogBase
from library.TableModel   import CCol, CDateCol, CTimeCol
from library.Utils        import forceDateTime, forceInt, forceRef, forceString, pyDate, toVariant

from Reports.ReportView   import CReportViewDialog

from Users.Rights         import urEditExecutionPlanAction

from Ui_ExecutionPlanDialog import Ui_ExecutionPlanDialog
from Ui_ExecutionPlanEditor import Ui_ExecutionPlanEditor


class CExecutionPlanDialog(CDialogBase, Ui_ExecutionPlanDialog):
    def __init__(self, parent, cols, tableName, order, record, executionPlan, forSelect=False, filterClass=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setup(cols, tableName, order, record, executionPlan, forSelect, filterClass)


    def setup(self, cols, tableName, order, record, executionPlan, forSelect=False, filterClass=None):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.forSelect = forSelect
        self.executionPlan = executionPlan
        self.record = record
        self.filterClass = filterClass
        self.props = {}
        self.order = order
        self.model = CExecutionPlanModel(self)
        self.tblExecutionPlan.setModel(self.model)
        self.btnEdit.setDefault(not self.forSelect)
        self.tblExecutionPlan.setFocus(QtCore.Qt.OtherFocusReason)

        directionDateTime = forceDateTime(record.value('directionDate'))
        self.edtDirectionDate.setDate(directionDateTime.date())
        self.edtDirectionTime.setTime(directionDateTime.time())
        self.cmbSetPerson.setValue(forceRef(record.value('setPerson_id')))
        self.isEditor = False if forceDateTime(record.value('endDate')) else True
        self.specifiedName = forceString(record.value('specifiedName'))
        self.actionTypeId = forceRef(record.value('actionType_id'))
        begDateTime = forceDateTime(record.value('begDate'))
        begDate = begDateTime.date()
        self.edtBegDate.setDate(begDate)
        duration = forceInt(record.value('duration'))
        plannedEndDateTime = forceDateTime(record.value('plannedEndDate'))
        if not plannedEndDateTime:
            plannedEndDateTime = begDateTime.addDays(duration-1)
        plannedEndDate = plannedEndDateTime.date()
        self.edtEndDate.setDate(plannedEndDate)
        self.edtDuration.setValue(duration)
        self.actionId = forceRef(record.value('id'))
        begDateNext = begDate
        while begDateNext <= plannedEndDate:
            if begDateNext not in self.executionPlan.keys():
                self.executionPlan[pyDate(begDateNext)] = {}
            begDateNext = begDateNext.addDays(1)
        self.model.loadData(self.executionPlan)
        self.label.setText(u'всего: %d' % len(self.model.items))

        QtCore.QObject.connect(
            self.tblExecutionPlan.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)


    def select(self, props):
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(), 'id', '', self.order)


    def getItemEditor(self):
        return CExecutionPlanEditor(self)


    def selectItem(self):
        return self.exec_()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExecutionPlan_doubleClicked(self, index):
        self.selected = True
        self.on_btnEdit_clicked()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.close()


    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        if self.isEditor:
            if QtGui.qApp.userHasRight(urEditExecutionPlanAction):
                item = {}
                row = self.tblExecutionPlan.currentRow()
                if row >= 0:
                    items = self.tblExecutionPlan.model().items
                    item = items[row][2]
                    if item:
                        dialog = self.getItemEditor()
                        dialog.load(item)
                        if dialog.exec_():
                            execDate = item.keys()[0]
                            item = dialog.getInfoDict()
                            self.tblExecutionPlan.model().loadDataItem(item, execDate, row)
                            if 0 < len(items) and (row + 1) < len(items):
                                self.tblExecutionPlan.setCurrentRow(row + 1)
                            else:
                                self.btnCancel.setFocus(QtCore.Qt.OtherFocusReason)
            else:
                QtGui.QMessageBox.information(
                    self,
                    u'Внимание!',
                    u'У вас нет прав на редактирование календаря выполнения назначений!')
        else:
            QtGui.QMessageBox.information(
                self,
                u'Внимание!',
                u'Вы не можете редактировать календарь выполнения назначений, так как действие выполнено!')


    def getReportHeader(self):
        return self.objectName()


    def getFilterAsText(self):
        return u''


    def contentToHTML(self):
        actionTypeName = ''
        if self.actionTypeId:
            db = QtGui.qApp.db
            table = db.table('ActionType')
            record = db.getRecordEx(table, [table['name']], [table['id'].eq(self.actionTypeId), table['deleted'].eq(0)])
            if record:
                actionTypeName = forceString(record.value('name'))
        reportHeader = self.getReportHeader() + u'\n'+ u'Действие: ' + actionTypeName + ((u'(' + self.specifiedName + u')') if self.specifiedName else u'')
        self.tblExecutionPlan.setReportHeader(reportHeader)
        reportDescription=self.getFilterAsText()
        self.tblExecutionPlan.setReportDescription(reportDescription)
        return self.tblExecutionPlan.contentToHTML()


    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        html = self.contentToHTML()
        view = CReportViewDialog(self)
        view.setText(html)
        view.exec_()


    def setSort(self, col):
        name=self.model.cols()[col].fields()[0]
        self.order = name
        header=self.tblExecutionPlan.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(col, QtCore.Qt.AscendingOrder)


class CExecutionPlanEditor(QtGui.QDialog, Ui_ExecutionPlanEditor):
    def __init__(self,  parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.tblPlanEditor.setModel(CExecutionPlanEditorModel(self))
        self.item = {}

    def load(self, item):
        self.item = item
        if self.item:
            self.tblPlanEditor.model().loadData(self.item)

    def getInfoDict(self):
        return self.tblPlanEditor.model().saveData()


class CExecutionPlanEditorModel(QtCore.QAbstractTableModel):
    column = [u'Выбранное время']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.executionPlan = {}


    def columnCount(self, index = QtCore.QModelIndex()):
        return 1


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)+1


    def flags(self, index = None):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.column[section])
        return QtCore.QVariant()


    def loadData(self, executionPlan):
        self.executionPlan = executionPlan
        self.items = []
        db = QtGui.qApp.db
        table = db.table('Action_ExecutionPlan')
        if self.executionPlan:
            execDateKeys = self.executionPlan.keys()
            execDateKeys.sort()
            for execDate in execDateKeys:
                self.column = [QtCore.QDate(execDate).toString('dd-MM-yyyy')]
                execTimeDict = self.executionPlan.get(execDate, {})
                execTimeKeys = execTimeDict.keys()
                execTimeKeys.sort()
                for execTime in execTimeKeys:
                    record = execTimeDict.get(execTime, None)
                    if not record:
                        record = table.newRecord()
                    item = [execTime,
                            QtCore.QDate(execDate),
                            record
                            ]
                    self.items.append(item)
        self.reset()


    def saveData(self):
        if len(self.items) < 1:
            return self.executionPlan
        self.executionPlan = {}
        db = QtGui.qApp.db
        table = db.table('Action_ExecutionPlan')
        for item in self.items:
            execTime = item[0]
            if execTime:
                execDate = pyDate(item[1])
                record = item[2]
                execTimeDict = self.executionPlan.get(execDate, {})
                if execTime in execTimeDict.keys():
                    record = execTimeDict.get(execTime, None)
                    if not record:
                        record = table.newRecord()
                else:
                    record = table.newRecord()
                record.setValue('execDate', toVariant(QtCore.QDateTime(QtCore.QDate(execDate), execTime)))
                execTimeDict[execTime] = record
                self.executionPlan[execDate] = execTimeDict
        return self.executionPlan


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if 0 <= row < len(self.items):
                if self.items[row][column]:
                    return toVariant(self.items[row][column])
        if role == QtCore.Qt.EditRole:
            if 0 <= row < len(self.items):
                if self.items[row][column]:
                    return toVariant(self.items[row][column])
        return QtCore.QVariant()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if row == len(self.items):
                if value.isNull():
                    return False
                execDateList = self.executionPlan.keys()
                if execDateList:
                    execDate = execDateList[0]
                    self.items.append([QtCore.QTime(), QtCore.QDate(execDate), None])
                    vCnt = len(self.items)
                    vIndex = QtCore.QModelIndex()
                    self.beginInsertRows(vIndex, vCnt, vCnt)
                    self.insertRows(vCnt, 1, vIndex)
                    self.endInsertRows()
                else:
                    return False
            if 0 <= row < len(self.items):
                newTime = value.toTime()
                if newTime.isNull():
                    self.items[row][column] = None
                    self.items[row][2] = None
                else:
                    self.items[row][column] = value.toTime()
                    record = self.items[row][2]
                    if not record:
                        db = QtGui.qApp.db
                        table = db.table('Action_ExecutionPlan')
                        record = table.newRecord()
                    record.setValue('execDate', toVariant(QtCore.QDateTime(self.items[row][1], self.items[row][column])))
                    self.items[row][2] = record
            self.emitCellChanged(row, column)
            return True
        return False


    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)


class CGetExecutionPlan(CExecutionPlanDialog):
    def __init__(self, parent, record, executionPlan):
        CExecutionPlanDialog.__init__(self, parent, [
            CDateCol(u'Дата',  ['execDate'], 20),
            CTimeCol(u'Время', ['execDate'], 40),
            ], 'Action_ExecutionPlan', ['execDate'], record, executionPlan)
        self.setWindowTitleEx(u'План выполнения назначений')
        self.selected = False
        self.executionPlan = executionPlan


    def exec_(self):
        result = CExecutionPlanDialog.exec_(self)
        return result


class CExecutionPlanModel(QtCore.QAbstractTableModel):
    column = [u'Дата', u'Время']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self._cols = []
        self.executionPlan = {}


    def cols(self):
        self._cols = [CCol(u'Дата',     ['execDate'], 20, 'l'),
                      CCol(u'Время',    ['execDate'], 20, 'l')
                      ]
        return self._cols


    def columnCount(self, index = QtCore.QModelIndex()):
        return 2


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.column[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column])
        return QtCore.QVariant()


    def loadData(self, executionPlan):
        self.items = []
        self.executionPlan = executionPlan
        execDateKeys = executionPlan.keys()
        execDateKeys.sort()
        for execDate in execDateKeys:
            resultDict = {}
            execTimeDict = executionPlan.get(execDate, {})
            execTimeKeys = execTimeDict.keys()
            execTimeKeys.sort()
            execTimeStr = u', '.join(str(execTime.toString('hh:mm')) for execTime in execTimeKeys if execTime)
            resultDict[execDate] = execTimeDict
            item = [QtCore.QDate(execDate).toString('dd-MM-yyyy'),
                    execTimeStr,
                    resultDict
                    ]
            self.items.append(item)
        self.reset()


    def loadDataItem(self, executionPlan, execDate, row):
        execTimeDict = executionPlan.get(execDate, {})
        execTimeKeys = execTimeDict.keys()
        execTimeKeys.sort()
        execTimeStr = u', '.join(str(execTime.toString('hh:mm')) for execTime in execTimeKeys if execTime)
        item = [QtCore.QDate(execDate).toString('dd-MM-yyyy'),
                execTimeStr,
                executionPlan
                ]
        self.executionPlan[execDate] = executionPlan.get(execDate, {})
        self.items[row] = item
        self.reset()

