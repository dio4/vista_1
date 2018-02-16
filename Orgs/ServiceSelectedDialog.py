# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore, QtSql

from Events.ActionsSelector import CEnableCol
from TariffModel import CTariffModel
from Ui_ServiceSelectedDialog import Ui_ServiceSelectedDialog
from library.DialogBase import CDialogBase
from library.InDocTable import CRecordListModel, CInDocTableCol, \
    CEnumInDocTableCol, CDateInDocTableCol, \
    CFloatInDocTableCol, CIntInDocTableCol, CLocEnableInDocTableCol, CRBInDocTableCol
from library.TableModel import CFindManager, CSelectionManager, CTableModel, CTextCol
from library.Utils import forceInt, forceRef, forceString, toVariant


class CServiceTableModel(CTableModel):
    def __init__(self, parent=None):
        CTableModel.__init__(self, parent, [
            CEnableCol(u'Включить',     ['id'],   20,  parent),
            CTextCol(u'Код',            ['code'], 20),
            CTextCol(u'Наименование',   ['name'], 20)
        ], 'rbService')
        self.parentWidget = parent
        self.cacheByCode = {}
        self.cacheByName = {}

    def getCacheByCode(self):
        return self.cacheByCode

    def getCacheByName(self):
        return self.cacheByName

    def flags(self, index):
        result = CTableModel.flags(self, index)
        if index.column() == 0:
            result |= QtCore.Qt.ItemIsUserCheckable
        return result

    def updateItems(self, eis=False):
        db = QtGui.qApp.db
        idList = []
        self.cacheByCode.clear()
        self.cacheByName.clear()
        table = self.table()
        cond = []
        if eis:
            cond.append(table['eisLegacy'].eq(not eis))
        cond.append(table['endDate'].gt(QtCore.QDate.currentDate()))
        recordList = db.getRecordList(table, [table['id'], table['code'], table['name']], where=db.joinAnd(cond), order='code')
        for record in recordList:
            idList.append(forceRef(record.value('id')))
            self.cacheByCode[forceString(record.value('code'))] = len(idList) - 1
            self.cacheByName[forceString(record.value('name'))] = len(idList) - 1
        self.setIdList(idList)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            row = index.row()
            self.parentWidget.setSelected(self._idList[row], forceInt(value) == QtCore.Qt.Checked)
            self.emitDataChanged()
            return True
        return False



class CSelectedServiceTableModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addExtCol(CInDocTableCol(u'№', '__serialNumber', 5), QtCore.QVariant.Int)
        self.addExtCol(CLocEnableInDocTableCol(parent), QtCore.QVariant.Bool)
        self.addExtCol(CRBInDocTableCol(u'Услуга', 'service_id', 40, 'rbService', showFields=2).setReadOnly(), QtCore.QVariant.Int)
        self.addExtCol(CRBInDocTableCol(u'Событие', 'eventType_id',  30, 'EventType', showFields=2), QtCore.QVariant.Int)
        self.addExtCol(CEnumInDocTableCol(u'Тарифицируется', 'tariffType', 30, CTariffModel.tariffTypeNames), QtCore.QVariant.Int)
        self.addExtCol(CDateInDocTableCol(u'Дата начала', 'begDate', 10), QtCore.QVariant.Date)
        self.addExtCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 10), QtCore.QVariant.Date)
        self.addExtCol(CIntInDocTableCol(u'Кол-во', 'amount', 10), QtCore.QVariant.Int)
        self.addExtCol(CFloatInDocTableCol(u'Цена', 'price', 10, precision=2), QtCore.QVariant.Double)

        self.contractId = None
        self.parent = parent
        self.table = QtGui.qApp.db.table('Contract_Tariff')
        self._dbFieldNamesList = [field.fieldName.replace('`', '') for field in self.table.fields]
        self.idToRow = {}
        self.idToRecord = {}

    def setContractId(self, contractId):
        self.countractId = contractId

    def add(self, serviceId, eventTypeId = None, tariffType = None, begDate = None, endDate = None):
        db = QtGui.qApp.db
        row = len(self._items)
        record = db.record(self.table.name())
        for col in self._cols:
            if not col.fieldName() in self._dbFieldNamesList:
                record.append(QtSql.QSqlField(col.fieldName(), col.valueType()))
        record.setValue('eventType_id', toVariant(eventTypeId))
        record.setValue('service_id', toVariant(serviceId))
        record.setValue('tariffType', toVariant(tariffType))
        record.setValue('begDate', toVariant(begDate))
        record.setValue('endDate', toVariant(endDate))
        record.setValue('checked', QtCore.QVariant(True))
        self.insertRecord(row, record)
        self.idToRow[serviceId] = row
        self.idToRecord[serviceId] = record

    def remove(self, serviceId):
        row = self.idToRow[serviceId]
        self.removeRows(row, 1)
        del self.idToRow[serviceId]
        del self.idToRecord[serviceId]
        for key in self.idToRow.keys():
            oldRow = self.idToRow[key]
            self.idToRow[key] = oldRow if oldRow < row else oldRow-1


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return QtCore.QVariant(row + 1)
        return CRecordListModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.CheckStateRole and column == self.getColIndex('checked'):
            record = self._items[row]
            self.parent.setSelected(forceRef(record.value('service_id')), forceInt(value) == QtCore.Qt.Checked)
            return False
        return CRecordListModel.setData(self, index, value, role)


class CServiceSelectedDialog(CDialogBase, CSelectionManager, CFindManager, Ui_ServiceSelectedDialog):
    def __init__(self, parent, contractId):
        CDialogBase.__init__(self, parent)
        CSelectionManager.__init__(self, parent)
        CFindManager.__init__(self, parent)
        self.contractId = contractId
        self.parent = parent
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.addModels('Service', CServiceTableModel(self))
        self.addModels('SelectedService', CSelectedServiceTableModel(self))
        self.setupUi(self)
        self.setModels(self.tblService, self.modelService, self.selectionModelService)
        self.setModels(self.tblSelectedService, self.modelSelectedService, self.selectionModelSelectedService)
        self.modelService.updateItems()
        self.cmbEventType.setTable('EventType')
        protocolId = forceInt(QtGui.qApp.db.translate('EventType', 'code', u'protocol', 'id'))
        if protocolId:
            self.cmbEventType.setValue(protocolId)
        self.cmbTariffType.addItems(CTariffModel.tariffTypeNames)
        self.setIdList(self.modelService.idList())
        self.setCacheByCode(self.modelService.getCacheByCode())
        self.setCacheByName(self.modelService.getCacheByName())
        self.cmbTariffType.setCurrentIndex(2)
        self.edtBegDate.setVisible(False)
        self.edtEndDate.setVisible(False)
        self.label_3.setVisible(False)
        self.label_4.setVisible(False)

    def setContractId(self, contractId):
        self.modelSelectedService.setContractId(contractId)

    def setSelected(self, serviceId, value):
        present = self.isSelected(serviceId)
        if value:
            if not present:
                self.selectedIdList.append(serviceId)
                self.modelSelectedService.add(serviceId,
                                              eventTypeId=self.cmbEventType.value(),
                                              tariffType=self.cmbTariffType.currentIndex(),
                                              begDate=self.edtBegDate.date(),
                                              endDate=self.edtEndDate.date())
                self.modelSelectedService.emitDataChanged()
                return True
        else:
            if present:
                self.selectedIdList.remove(serviceId)
                self.modelSelectedService.remove(serviceId)
                self.modelService.emitDataChanged()
                return True
        return False

    def getSelectedServiceList(self):
        result = []
        for serviceId in self.selectedIdList:
            result.append((serviceId, self.modelSelectedService.idToRecord[serviceId]))
        return result

    @QtCore.pyqtSlot(bool)
    def on_btnSearchMode_toggled(self, state):
        if state:
            self.btnSearchMode.setText(u'наименованию')
        else:
            self.btnSearchMode.setText(u'коду')
        text = self.edtFindByCode.text()
        self.on_edtFindByCode_textChanged(text)
        self.edtFindByCode.setFocus()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFindByCode_textChanged(self, text):
        if text:
            if self.btnSearchMode.isChecked():
                idList = self.findByName(text)
            else:
                idList = self.findByCode(text)
            self.tblService.setIdList(idList)
        else:
            self.tblService.setIdList(self.getIdList())

    @QtCore.pyqtSlot(bool)
    def on_chkNotEIS_toggled(self, value):
        self.modelService.updateItems(eis=self.chkNotEIS.isChecked())
        self.setIdList(self.modelService.idList())
        self.setCacheByCode(self.modelService.getCacheByCode())
        self.setCacheByName(self.modelService.getCacheByName())

