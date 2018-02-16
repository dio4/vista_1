# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from Accounting.ContractComboBox import CContractPopupView
from library.TreeModel import CTreeItemWithId, CTreeModel
from library.Utils     import forceInt, forceRef, forceString

class CPaymnetSchemeTreeItem(CTreeItemWithId):
    def __init__(self, parent, id,  name, model, type):
        CTreeItemWithId.__init__(self, parent, name, id)
        self._type = type
        self._model = model

    def getType(self):
        return self._type

    def loadChildren(self):
        return self._model.loadChildrenItems(self)

class CPaymenSchemeTypeTreeItem(CPaymnetSchemeTreeItem):
    def __init__(self, parent, model, type):
        CPaymnetSchemeTreeItem.__init__(self, parent, None, [u'Клинические исследования', u'Безналичный расчет'][type], model, type)

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class CPaymentSchemeRootTreeItem(CPaymnetSchemeTreeItem):
    def __init__(self, model):
        CPaymnetSchemeTreeItem.__init__(self, None, None, u'Все схемы оплаты', model, None)

    def loadChildren(self):
        result = []
        for type in self._model._types:
            result.append(CPaymenSchemeTypeTreeItem(self, self._model, type))
        return result

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def resert(self):
        if self._items is None:
            return False
        else:
            self._items = None
            return True


class CPaymentSchemeModel(CTreeModel):
    def __init__(self, parent=None):
        CTreeModel.__init__(self, parent, CPaymentSchemeRootTreeItem(self))
        self._types = range(2) # 2 - количество типов схемы оплаты
        self._clientId = None
        self._enrollmentIsOpen = None
        self._begDate = QtCore.QDate.currentDate()
        self._endDate = None

    def setDates(self, begDate, endDate):
        if self._begDate != begDate or self._endDate != endDate:
            self._begDate = begDate
            self._endDate = endDate
            if self.getRootItem().reset():
                self.reset()

    def setType(self, type):
        if self._types != type:
            self._types = type
            if self.getRootItem().resert():
                self.reset()

    def setClientId(self, clientId):
        if self._clientId != clientId:
            self._clientId = clientId
            if self.getRootItem().resert():
                self.reset()

    def setEnrollment(self, isOpen):
        if self._enrollmentIsOpen != isOpen:
            self._enrollmentIsOpen = isOpen
            if self.getRootItem().resert():
                self.reset()

    def loadChildrenItems(self, group):
        db = QtGui.qApp.db
        items = []
        table = db.table('PaymentScheme')
        tableClientPaymentScheme = db.table('Client_PaymentScheme')
        tableOrganisation = db.table('Organisation')
        queryTable = table.innerJoin(tableOrganisation, tableOrganisation['id'].eq(table['org_id']))
        cond = []

        if self._clientId:
            queryTable = queryTable.innerJoin(tableClientPaymentScheme, tableClientPaymentScheme['paymentScheme_id'].eq(table['id']))
            cond.append(tableClientPaymentScheme['client_id'].eq(self._clientId))
        if self._begDate and self._endDate:
            cond.append(db.joinOr([db.joinAnd([table['begDate'].dateGe(self._begDate),
                                               table['begDate'].dateLt(self._endDate)]),
                                   db.joinAnd([table['begDate'].dateLe(self._begDate),
                                               table['endDate'].dateGt(self._begDate)])]))
        elif self._begDate:
            cond.append(table['begDate'].isNotNull())
            cond.append(db.joinOr([table['begDate'].dateGe(self._begDate),
                                   db.joinAnd([table['begDate'].dateLe(self._begDate),
                                               table['endDate'].dateGe(self._begDate)])]))
        elif self._endDate:
            cond.append(db.joinAnd([table['begDate'].isNotNull(),
                                    table['begDate'].dateLe(self._endDate)]))
        if self._enrollmentIsOpen and group._type == 0:
            cond.append(table['enrollment'].eq(not self._enrollmentIsOpen))
        cond.append(table['type'].eq(group._type))
        cond.append(table['deleted'].eq(0))
        recordList = db.getRecordList(queryTable,
                                      [table['id'], table['number'], tableOrganisation['shortName'], table['type']],
                                      db.joinAnd(cond),
                                      [table['type'], table['begDate'], table['number'], table['id']])
        for record in recordList:
            id = forceRef(record.value('id'))
            type = forceInt(record.value('type'))
            item = CPaymnetSchemeTreeItem(group,
                                          id,
                                          forceString(record.value('number')) + u' ' + forceString(record.value('shortName')),
                                          self,
                                          type)
            item._items = []
            items.append(item)
        return items


class CPaymentSchemeComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        # self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self._model = CPaymentSchemeModel(self)
        self.setModel(self._model)
        self._popupView = CContractPopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)

        self._previousValue = None
        self._mapPaymentItemsByContract = None
        self._mapPaymentItemsByIdx = None
        self._universalContractsIdList = None

        self.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        self.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.connect(self, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_currentIndexChanged)
        # self.connect(self, QtCore.SIGNAL('editTextChanged(QString)'), self.on_editTextChanged)


    def setType(self, type):
        if type is None:
            self._model.setType(range(2)) # 2 типа схемы оплаты
        else:
            self._model.setType(type if isinstance(type, list) else [type])

    def setClientId(self, clientId):
        self._model.setClientId(clientId)

    def setEnrollment(self, isOpen):
        self._model.setEnrollment(isOpen)

    def setValue(self, id):
        index = self._model.findItemId(id)
        self.setCurrentIndex(index)

    def getUniversalContract(self):
        if self._universalContractsIdList is None:
            self.loadPaymentItems()
        return self._universalContractsIdList

    def getItemsByContract(self):
        if self._mapPaymentItemsByContract is None:
            self.loadPaymentItems()
        return self._mapPaymentItemsByContract

    def getItemsByIdx(self):
        if self._mapPaymentItemsByIdx is None:
            self.loadPaymentItems()
        return self._mapPaymentItemsByIdx

    def loadPaymentItems(self):
        db = QtGui.qApp.db
        self._mapPaymentItemsByContract = {}
        self._mapPaymentItemsByIdx = {}
        self._universalContractsIdList = []
        paymentSchemeId = self.value()
        if paymentSchemeId:
            table = db.table('PaymentSchemeItem')
            tableContract = db.table('Contract')
            queryTable = table.innerJoin(tableContract, tableContract['id'].eq(table['contract_id']))
            recordList = db.getRecordList(queryTable,
                                          [table['id'], table['idx'], table['name'], table['paymentScheme_id'], table['contract_id'], 'CONCAT_WS(\' \',grouping, number, DATE_FORMAT(date,\'%d.%m.%Y`\'), resolution) AS contract'],
                                          [table['paymentScheme_id'].eq(paymentSchemeId), table['deleted'].eq(0)])
            for record in recordList:
                idx = forceInt(record.value('idx'))
                contractId = forceRef(forceRef(record.value('contract_id')))
                if idx < 0:
                    self._universalContractsIdList.append(contractId)
                else:
                    tmpMap = {'id': forceRef(record.value('id')),
                              'idx': idx,
                              'name': forceString(record.value('name')),
                              'paymentScheme_id': forceRef(record.value('paymentScheme_id')),
                              'contract_id': contractId,
                              'contract': forceString(record.value('contract'))}
                    self._mapPaymentItemsByContract[contractId] = tmpMap.copy()
                    self._mapPaymentItemsByIdx[idx] = tmpMap.copy()

    def value(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        if modelIndex.isValid():
            return self._model.itemId(modelIndex)
        return None

    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0:
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))

    def on_currentIndexChanged(self, index):
        value = self.value()
        if value != self._previousValue:
            self._previousValue = value
            self._mapPaymentItemsByContract = None
            self._universalContractsIdList = None
            self._mapPaymentItemsByIdx = None
            self.emit(QtCore.SIGNAL('valueChanged()'))

    # def on_editTextChanged(self, text):
    #     self.emit(QtCore.SIGNAL('editTextChanged(QString)'))

    def showPopup(self):
        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        rootIndex = self._model.index(0, 0)
        self._popupView.setExpanded(rootIndex, True)
        # self._popupView.expandAll()
        QtGui.QComboBox.showPopup(self)


    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        self.setRootModelIndex(index.parent())
        QtGui.QComboBox.setCurrentIndex(self, index.row())


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select ]:
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0:
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False