# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from Blank.BlanksDialog import CPersonFindInDocTableCol
from Events.Action import ActionStatus, CAction, CActionType, CActionTypeCache
from Events.ActionsModel import fillActionRecord, getActionDefaultContractId
from Events.ExecutionPlanDialog import CGetExecutionPlan
from Events.Utils import getEventActionContract, getMainActionTypesAnalyses
from Orgs.OrgComboBox import CContractComboBox, CContractDbModel
from library.InDocTable import CBoolInDocTableCol, CDateInDocTableCol, CDateTimeInDocTableCol, CFloatInDocTableCol, \
    CInDocTableCol, CInDocTableView, CIntInDocTableCol, CLocItemDelegate, CRBInDocTableCol, CRecordListModel
from library.TableView import CTableView
from library.Utils import forceDate, forceDateTime, forceDouble, forceInt, forceRef, forceString, pyDate, toVariant


class CCheckedActionsModel(CRecordListModel):
    class CLocEnableCol(CBoolInDocTableCol):
        def __init__(self, selector):
            CBoolInDocTableCol.__init__(self, u'Включить', 'checked', 10)
            self.selector = selector

        def toCheckState(self, val, record):
            return CBoolInDocTableCol.toCheckState(self, val, record)

    class CContractInDocTableCol(CInDocTableCol):
        def __init__(self, model):
            CInDocTableCol.__init__(self, u'Договор', 'contract_id', 20)
            self.model = model

        def toString(self, val, record):
            contractId = forceRef(val)
            if contractId:
                names = ['number', 'date', 'resolution']
                record = QtGui.qApp.db.getRecord('Contract', names, contractId)
                joinedString = ' '.join(forceString(record.value(name)) for name in names)
            else:
                joinedString = u'не задано'
            return QtCore.QVariant(joinedString)

        def createEditor(self, parent):
            eventEditor = self.model.parentWidget.eventEditorOwner().eventEditor
            editor = CContractComboBox(parent)
            editor.setOrgId(eventEditor.orgId)
            editor.setClientInfo(eventEditor.clientId,
                                 eventEditor.clientSex,
                                 eventEditor.clientAge,
                                 eventEditor.clientWorkOrgId,
                                 eventEditor.clientPolicyInfoList)
            return editor

        def getEditorData(self, editor):
            return QtCore.QVariant(editor.value())

        def setEditorData(self, editor, value, record):
            eventEditor = self.model.parentWidget.eventEditorOwner().eventEditor
            financeId = forceRef(record.value('finance_id')) or eventEditor.eventFinanceId
            editor.setFinanceId(financeId)
            editor.setActionTypeId(forceRef(record.value('actionType_id')))
            contractId = forceRef(value)
            if contractId is None:
                if financeId == eventEditor.eventFinanceId:
                    contractId = eventEditor.contractId
            editor.setValue(contractId)
            editor.setBegDate(forceDate(record.value('directionDate')) or QtCore.QDate.currentDate())
            editor.setEndDate(forceDate(record.value('endDate')) or QtCore.QDate.currentDate())

    class CPropertyInDocTableCol(CInDocTableCol):
        pass

    class CLocDateTimeInDocTableCol(CDateTimeInDocTableCol):

        def __init__(self, title, fieldName, width, **params):
            CDateTimeInDocTableCol.__init__(self, title, fieldName, width, **params)
            self.setCurrentDate = params.get('currentDate', False)

        def createEditor(self, parent):
            editor = QtGui.QDateTimeEdit(parent)
            editor.setDisplayFormat('dd.MM.yyyy HH:mm')
            return editor

        def getEditorData(self, editor):
            return toVariant(editor.dateTime())

        def setEditorData(self, editor, value, record):
            if self.setCurrentDate and forceDateTime(value).isNull():
                editor.setDateTime(QtCore.QDateTime.currentDateTime())
            else:
                editor.setDateTime(forceDateTime(value))

        def toString(self, val, record):
            if not val.isNull():
                return QtCore.QVariant(forceString(val))
            return QtCore.QVariant()

    def __init__(self, parent, existsActionsModel):
        CRecordListModel.__init__(self, parent)
        currentDateDict = {'currentDate': True}
        self.addExtCol(CInDocTableCol(u'№', '__serialNumber', 5), QtCore.QVariant.Int)
        self.addExtCol(CCheckedActionsModel.CLocEnableCol(parent), QtCore.QVariant.Bool)
        self.addExtCol(CRBInDocTableCol(u'Действие', 'actionType_id', 15, 'ActionType', showFields=2).setReadOnly(), QtCore.QVariant.Int)
        self.addExtCol(CCheckedActionsModel.CLocDateTimeInDocTableCol(u'Назначить', 'directionDate', 10), QtCore.QVariant.DateTime)
        self.addExtCol(CCheckedActionsModel.CLocDateTimeInDocTableCol(u'Начать', 'begDate', 10), QtCore.QVariant.DateTime)
        self.addExtCol(CCheckedActionsModel.CLocDateTimeInDocTableCol(u'Выполнено', 'endDate', 10, **currentDateDict), QtCore.QVariant.DateTime)
        self.addExtCol(CPersonFindInDocTableCol(u'Врач', 'person_id', 10, 'vrbPersonWithSpeciality', parent=parent), QtCore.QVariant.Int)
        self.addExtCol(CFloatInDocTableCol(u'Количество', 'amount', 10, precision=2), QtCore.QVariant.Double)
        self.addExtCol(CFloatInDocTableCol(u'ЧП', 'necessity', 10, precision=2), QtCore.QVariant.Double)
        self.addExtCol(CIntInDocTableCol(u'Длительность', 'duration', 10), QtCore.QVariant.Int)
        self.addExtCol(CIntInDocTableCol(u'Интервал', 'periodicity', 10), QtCore.QVariant.Int)
        self.addExtCol(CIntInDocTableCol(u'Кратность', 'aliquoticity', 10), QtCore.QVariant.Int)
        self.addExtCol(CDateInDocTableCol(u'План', 'plannedEndDate', 10), QtCore.QVariant.Date)
        self.addExtCol(CRBInDocTableCol(u'Тип финансирования', 'finance_id', 10, 'rbFinance', showFields=2), QtCore.QVariant.Int)
        self.addExtCol(CCheckedActionsModel.CContractInDocTableCol(self), QtCore.QVariant.Int)
        self.addExtCol(CFloatInDocTableCol(u'Сумма', 'price', 10, precision=2), QtCore.QVariant.Double)
        self.addExtCol(CFloatInDocTableCol(u'Закупочная стоимость упаковки', 'packPurchasePrice', 10, precision=2), QtCore.QVariant.Double)
        self.addExtCol(CFloatInDocTableCol(u'Стоимость курсовой дозы', 'doseRatePrice', 10, precision=2), QtCore.QVariant.Double)
        self.addHiddenCol('parent_id')

        self._existsActionsModel = existsActionsModel
        self.clientId = None
        self.defaultFinanceId = None
        self.defaultContractFilterPart = None
        self._idToRow = {}
        self.parentWidget = parent
        self._table = QtGui.qApp.db.table('Action')
        self._dbFieldNamesList = [field.fieldName.replace('`', '') for field in self._table.fields]
        self.prices = []
        self._mapPropertyTypeCellsActivity = {}
        self._propertyColsNames = ['recipe', 'doses', 'signa']
        self._propertyColsIndexes = [self.getColIndex(name) for name in self._propertyColsNames]
        self._mapActionTypeIdToPropertyValues = {}
        self._idToAction = {}
        self._parent = parent
        self._mainActionTypesAnalyses = set(getMainActionTypesAnalyses())

        boldFont = QtGui.QFont()
        boldFont.setWeight(QtGui.QFont.Bold)
        self._qBoldFont = QtCore.QVariant(boldFont)

    def setClientId(self, clientId):
        self.clientId = clientId

    def cellReadOnly(self, index):
        column = index.column()
        if column == self.getColIndex('plannedEndDate'):
            return not self.isRowPlanEndDateEdited(index.row())
        elif column in self._propertyColsIndexes:
            return not self._mapPropertyTypeCellsActivity.get((index.row(), column), False)
        return False

    def flags(self, index):
        flags = CRecordListModel.flags(self, index)
        column = index.column()
        if column in [self.getColIndex('packPurchasePrice'),
                      self.getColIndex('doseRatePrice')]:
            row = index.row()
            record = self._items[row]
            if forceRef(record.value('actionType_id')) not in self._parent.medicamentList:
                flags = flags & (~QtCore.Qt.ItemIsEditable)
        return flags

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.ToolTipRole:
                if section == self.getColIndex('duration'):
                    return QtCore.QVariant(u'Длительность курса лечения в днях.')
                elif section == self.getColIndex('periodicity'):
                    result = '\n'.join([u'0 - каждый день,',
                                        u'1 - через 1 день,', 
                                        u'2 - через 2 дня,', 
                                        u'3 - через 3 дня,', 
                                        u'и т.д.'])
                    return QtCore.QVariant(result)
                elif section == self.getColIndex('aliquoticity'):
                    return QtCore.QVariant(u'Сколько раз в сутки.')
        return CRecordListModel.headerData(self, section, orientation, role)

    def isEditable(self):
        return True

    def isRowPlanEndDateEdited(self, row):
        return not (self.isRowDpedBegDatePlusAmount(row) or self.isRowDpedBegDatePlusDuration(row))

    def getDefaultPlannedEndDate(self, actionTypeId):
        return CActionTypeCache.getById(actionTypeId).defaultPlannedEndDate

    def isDpedBegDatePlusAmount(self, actionTypeId):
        return self.getDefaultPlannedEndDate(actionTypeId) == CActionType.dpedBegDatePlusAmount

    def isDpedBegDatePlusDuration(self, actionTypeId):
        return self.getDefaultPlannedEndDate(actionTypeId) == CActionType.dpedBegDatePlusDuration

    def isRowDpedBegDatePlusAmount(self, row):
        actionTypeId = forceRef(self.items()[row].value('actionType_id'))
        return self.isDpedBegDatePlusAmount(actionTypeId)

    def isRowDpedBegDatePlusDuration(self, row):
        actionTypeId = forceRef(self.items()[row].value('actionType_id'))
        return self.isDpedBegDatePlusDuration(actionTypeId)

    def regenerate(self):
        count = len(self.items())
        self.prices = [0.0] * count
        self.updatePricesAndSums(0, count - 1)

    def getActionRecord(self, actionTypeId):
        row = self._idToRow[actionTypeId]
        item = self._items[row]
        return self.getClearActionRecord(item)

    def getPropertiesValues(self, actionTypeId):
        result = {}
        values = self._mapActionTypeIdToPropertyValues.get(actionTypeId, None)
        if values:
            for value in values.values():
                if value['value'].isValid():
                    result[value['propertyType'].id] = value['value']
        return result

    def getContractId(self):
        return self.parentWidget.getContractId()

    def getPrice(self, record):
        actionTypeId = forceRef(record.value('actionType_id'))
        financeId = forceRef(record.value('finance_id'))
        contractId = forceRef(record.value('contract_id'))
        return self.getPriceEx(actionTypeId, contractId, financeId)

    def getPriceEx(self, actionTypeId, contractId, financeId):
        return self.parentWidget.getPrice(actionTypeId, contractId, financeId)

    def getClearActionRecord(self, item):
        record = self._table.newRecord()
        for iCol in xrange(record.count()):
            fieldName = record.fieldName(iCol)
            record.setValue(fieldName, item.value(fieldName))
        return record

    def add(self, actionTypeId, amount=None, necessity=None, parentActionRecord=None):
        db = QtGui.qApp.db
        row = len(self._items)
        record = self.getEmptyRecord(self.getPropertyTypeCellsSettings(actionTypeId, row))
        fillActionRecord(self.parentWidget.eventEditorOwner(), record, actionTypeId)
        #Добавление типа финансирования по умолчанию, если он не заполнен на основе других данных
        if not forceRef(record.value('finance_id')) and self.defaultFinanceId:
            record.setValue('finance_id', QtCore.QVariant(self.defaultFinanceId))

        contractId = forceRef(record.value('contract_id'))
        paymentScheme = self.parentWidget.getPaymentScheme()
        if paymentScheme:
            paymentSchemeItem = self.parentWidget.getPaymentSchemeItem()
            tableAT = db.table('ActionType')
            tableContract = db.table('Contract')
            tableContractTariff = db.table('Contract_Tariff')
            tablePSI = db.table('PaymentSchemeItem')
            tableService = db.table('rbService')

            queryTable = tableAT.innerJoin(tableService, tableService['code'].eq(tableAT['code']))
            queryTable = queryTable.innerJoin(tableContractTariff, tableContractTariff['service_id'].eq(tableService['id']))
            queryTable = queryTable.innerJoin(tableContract, [tableContract['id'].eq(tableContractTariff['master_id']),
                                                              tableContract['deleted'].eq(0)])
            queryTable = queryTable.innerJoin(tablePSI, tablePSI['contract_id'].eq(tableContract['id']))
            cond = [
                tableAT['id'].eq(actionTypeId),
                tablePSI['paymentScheme_id'].eq(paymentScheme),
                db.joinOr([tablePSI['idx'].eq(paymentSchemeItem['idx']),
                           tablePSI['idx'].lt(0)]) if paymentSchemeItem else tablePSI['idx'].lt(0)
            ]
            recordContract = db.getRecordEx(queryTable, tablePSI['contract_id'], cond, order=tablePSI['idx'])
            if recordContract:
                contractId = forceRef(recordContract.value('contract_id'))
            # record.setValue('contract_id', QtCore.QVariant(self.getContractId()))
        #Добавление контракта по умолчанию, если он не заполнен на основе других данных
        elif not forceRef(record.value('contract_id')) and self.defaultContractFilterPart:
            contractModel = CContractDbModel(None)
            eventEditor = self.parentWidget.eventEditorOwner().eventEditor
            contractModel.setOrgId(eventEditor.orgId)
            contractModel.setClientInfo(eventEditor.clientId,
                                        eventEditor.clientSex,
                                        eventEditor.clientAge,
                                        eventEditor.clientWorkOrgId,
                                        eventEditor.clientPolicyInfoList)
            contractModel.setFinanceId(forceRef(record.value('finance_id')))
            contractModel.setActionTypeId(forceRef(record.value('actionType_id')))
            contractModel.setBegDate(forceDate(record.value('directionDate')) or QtCore.QDate.currentDate())
            contractModel.setEndDate(forceDate(record.value('endDate')) or QtCore.QDate.currentDate())
            contractModel.dbDataAvailable()
            availableIdList = contractModel.dbdata.idList
            tableContract = db.table('Contract')
            contractIdList = db.getIdList(tableContract,
                                          tableContract['id'],
                                          [tableContract['id'].inlist(availableIdList),
                                           self.defaultContractFilterPart],
                                          limit=1)
            contractId = contractIdList[0] if contractIdList else None

        record.setValue('contract_id', QtCore.QVariant(contractId))
        record.setValue('checked', QtCore.QVariant(QtCore.Qt.Checked))
        record.setValue('price', QtCore.QVariant(self.getPrice(record)))

        if amount:
            record.setValue('amount', QtCore.QVariant(amount))

        if necessity:
            record.setValue('necessity', QtCore.QVariant(necessity))

        if parentActionRecord:
            fieldsToDerive = ['begDate', 'endDate', 'plannedEndDate', 'status']
            for field in fieldsToDerive:
                record.setValue(field, parentActionRecord.value(field))
            record.setValue('parent_id', toVariant(1))  # fix it

        self.insertRecord(row, record)
        self._idToAction[actionTypeId] = CAction(record=record)
        self._idToRow[actionTypeId] = row
        self.prices.append(0.0)
        if not self.isRowPlanEndDateEdited(row):
            self.updatePlannedEndDate(row)
        self.emitPricesAndSumsUpdated()

        setPerson = forceRef(record.value('setPerson_id'))
        execPerson = forceRef(record.value('person_id'))
        if not QtGui.qApp.userSpecialityId:
            if setPerson == QtGui.qApp.userId:
                record.setValue('setPerson_id', toVariant(None))
            if execPerson == QtGui.qApp.userId:
                record.setValue('person_id', toVariant(None))

        return record

    def getSelectedAction(self, actionTypeId, returnDirtyRows):
        u"""Создает новую запись для таблицы Action по указанному ActionType.id и проставляет статус"""
        action = self._idToAction[actionTypeId]
        if not returnDirtyRows:
            action._record = self.getClearActionRecord(action._record)
        if not (forceDate(action._record.value('endDate')).isNull() or forceInt(action._record.value('status')) == ActionStatus.NotProvided):
            action._record.setValue('status', ActionStatus.Done)  # 2
        return self._idToAction[actionTypeId]

    def getPropertyTypeCellsSettings(self, actionTypeId, row):
        cellSettings = {}
        actionType = CActionTypeCache.getById(actionTypeId)
        for propertyType in actionType.getPropertiesById().values():
            if propertyType.inActionsSelectionTable:
                column = self._propertyColsIndexes[propertyType.inActionsSelectionTable - 1]
                result = self._mapPropertyTypeCellsActivity.get((row, column), None)
                if result is None:
                    self._cols[column].setValueType(propertyType.valueType.variantType)
                    self._mapPropertyTypeCellsActivity[(row, column)] = True
                    cellName = self._propertyColsNames[propertyType.inActionsSelectionTable - 1]
                    cellSettings[cellName] = True
                    values = self._mapActionTypeIdToPropertyValues.get(actionTypeId, None)
                    if values is None:
                        values = {cellName: {'propertyType': propertyType, 'value': QtCore.QVariant()}}
                        self._mapActionTypeIdToPropertyValues[actionTypeId] = values
                    else:
                        values[cellName] = {'propertyType': propertyType, 'value': QtCore.QVariant()}
        return cellSettings

    def removeAll(self):
        self.removeRows(0, len(self._items))
        self._idToRow.clear()
        self._idToAction.clear()
        self._items = []
        self.prices = []
        self.emitPricesAndSumsUpdated()

    def remove(self, actionTypeId):
        row = self._idToRow[actionTypeId]
        self.removeRows(row, 1)
        del self.prices[row]
        del self._idToRow[actionTypeId]
        del self._idToAction[actionTypeId]
        for key in self._idToRow.keys():
            oldRow = self._idToRow[key]
            self._idToRow[key] = oldRow if oldRow < row else oldRow - 1
        self.emitPricesAndSumsUpdated()

    def getEmptyRecord(self, propertyTypeCellsSettings=None):
        if not propertyTypeCellsSettings:
            propertyTypeCellsSettings = {}
        record = self._table.newRecord()
        for col in self._cols:
            if not col.fieldName() in self._dbFieldNamesList:
                record.append(QtSql.QSqlField(col.fieldName(), col.valueType()))
        for name in self._propertyColsNames:
            isActive = propertyTypeCellsSettings.get(name, False)
            if not isActive:
                record.setValue(name, QtCore.QVariant(u'----'))
        return record

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return QtCore.QVariant(row + 1)

            elif column == self.getColIndex('actionType_id'):
                record = self._items[row]
                outName = forceString(record.value('specifiedName'))
                actionTypeId = forceRef(record.value('actionType_id'))
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    if actionType:
                        outName = actionType.name + ' ' + outName if outName else actionType.name
                    return QtCore.QVariant(outName)

            elif column in self._propertyColsIndexes:
                record = self._items[row]
                actionTypeId = forceRef(record.value('actionType_id'))
                values = self._mapActionTypeIdToPropertyValues.get(actionTypeId, None)
                if values:
                    fieldName = self._cols[column].fieldName()
                    cellValues = values.get(fieldName, None)
                    if cellValues:
                        action = self._idToAction[actionTypeId]
                        propertyType = cellValues['propertyType']
                        prop = action.getPropertyById(propertyType.id)
                        return toVariant(prop.getText())

        elif role == QtCore.Qt.FontRole:
            record = self._items[row]
            actionTypeId = forceRef(record.value('actionType_id'))
            if self._existsActionsModel.hasActionTypeId(actionTypeId) or actionTypeId in self._mainActionTypesAnalyses:
                return self._qBoldFont

        return CRecordListModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.CheckStateRole and column == self.getColIndex('checked'):
            record = self._items[row]
            actionTypeId = forceRef(record.value('actionType_id'))
            self.parentWidget.setSelected(actionTypeId, forceInt(value) == QtCore.Qt.Checked, resetMainModel=True)
            return False
        result = CRecordListModel.setData(self, index, value, role)

        col = self.cols()[column]
        fieldName = col.fieldName()

        if fieldName == 'finance_id':
            self.initContract(row)
            self.updatePricesAndSums(row, row)
        elif fieldName == 'contract_id':
            self.updatePricesAndSums(row, row)
        elif fieldName == 'amount':
            self.updatePricesAndSums(row, row)
            if self.isRowDpedBegDatePlusAmount(row):
                self.updatePlannedEndDate(row)
        elif fieldName == 'duration':
            self.updatePlannedEndDate(row)
        elif fieldName == 'begDate' and not self.isRowPlanEndDateEdited(row):
            self.updatePlannedEndDate(row)

        return result

    def updatePlannedEndDate(self, row):
        if self.isRowDpedBegDatePlusAmount(row):
            item = self.items()[row]
            begDate = forceDate(item.value('begDate'))
            amountValue = forceInt(item.value('amount'))
            date = begDate.addDays(amountValue - 1) if (amountValue and begDate.isValid()) else QtCore.QDate()
            item.setValue('plannedEndDate', toVariant(date))
            self.emitValueChanged(row, 'plannedEndDate')
        else:
            item = self.items()[row]
            begDate = forceDate(item.value('begDate'))
            durationValue = forceInt(item.value('duration'))
            date = begDate.addDays(durationValue - 1) if begDate.isValid() and not durationValue == 0 else QtCore.QDate()
            item.setValue('plannedEndDate', toVariant(date))
            self.emitValueChanged(row, 'plannedEndDate')

    def initContract(self, row):
        item = self.items()[row]
        actionTypeId = forceRef(item.value('actionType_id'))
        financeId = forceRef(item.value('finance_id'))
        if financeId:
            eventEditor = self.parentWidget.eventEditorOwner().eventEditor
            if financeId == eventEditor.eventFinanceId and getEventActionContract(eventEditor.eventTypeId):
                contractId = eventEditor.contractId
            else:
                begDate = forceDate(item.value('directionDate'))
                endDate = forceDate(item.value('endDate'))
                contractId = getActionDefaultContractId(self.parentWidget.eventEditorOwner(),
                                                        actionTypeId,
                                                        financeId,
                                                        begDate,
                                                        endDate,
                                                        None)
        else:
            contractId = None
        item.setValue('contract_id', toVariant(contractId))
        self.emitValueChanged(row, 'contract_id')

    def getTotalSum(self):
        return sum(forceDouble(item.value('price')) for item in self._items)

    def updatePricesAndSums(self, top, bottom):
        sumChanged = False
        for i in xrange(top, bottom + 1):
            sumChanged = self.updatePriceAndSum(i, self.items()[i]) or sumChanged
        self.emitPricesAndSumsUpdated()

    def emitPricesAndSumsUpdated(self):
        self.emit(QtCore.SIGNAL('pricesAndSumsUpdated()'))

    def updatePriceAndSum(self, row, item):
        actionTypeId = forceRef(item.value('actionType_id'))
        eventEditor = self.parentWidget.eventEditorOwner().eventEditor
        if actionTypeId:
            contractId = forceRef(item.value('contract_id'))
            if contractId:
                financeId = forceRef(QtGui.qApp.db.translate('Contract', 'id', contractId, 'finance_id'))
            else:
                contractId = eventEditor.contractId
                financeId = eventEditor.eventFinanceId
            price = self.getPriceEx(actionTypeId, contractId, financeId) * forceDouble(item.value('amount'))
        else:
            price = 0.0
        if self.prices[row] != price:
            self.prices[row] = price
            item.setValue('price', price)
            self.emitValueChanged(row, 'price')

    def createEditor(self, index, parent):
        column = index.column()
        if column in self._propertyColsIndexes:
            return self.createPropertyEditor(index, parent)
        else:
            return CRecordListModel.createEditor(self, column, parent)

    def createPropertyEditor(self, index, parent):
        row = index.row()
        column = index.column()
        actionTypeId = forceRef(self._items[row].value('actionType_id'))
        values = self._mapActionTypeIdToPropertyValues[actionTypeId]
        fieldName = self._cols[column].fieldName()
        cellValues = values[fieldName]
        propertyType = cellValues['propertyType']
        editor = propertyType.createEditor(None, parent, self.clientId)
        return editor

    def setEditorData(self, index, editor, value, record):
        column = index.column()
        if column in self._propertyColsIndexes:
            return self.setPropertyEditorData(index, editor, value, record)
        else:
            return CRecordListModel.setEditorData(self, column, editor, value, record)

    def setPropertyEditorData(self, index, editor, value, record):
        editor.setValue(value)

    def getEditorData(self, index, editor):
        column = index.column()
        if column in self._propertyColsIndexes:
            return self.getPropertyEditorData(index, editor)
        else:
            return CRecordListModel.getEditorData(self, column, editor)

    def getPropertyEditorData(self, index, editor):
        value               = editor.value()
        row                 = index.row()
        column              = index.column()
        actionTypeId        = forceRef(self._items[row].value('actionType_id'))
        values              = self._mapActionTypeIdToPropertyValues[actionTypeId]
        fieldName           = self._cols[column].fieldName()
        cellValues          = values[fieldName]
        cellValues['value'] = toVariant(value)
        action              = self._idToAction[actionTypeId]
        propertyType        = cellValues['propertyType']
        property            = action.getPropertyById(propertyType.id)
        value = propertyType.convertQVariantToPyValue(value) if type(value) == QtCore.QVariant else value
        property.setValue(value)
        if property.isActionNameSpecifier():
            action.updateSpecifiedName()
            self.emitValueChanged(row, 'actionType_id')
        return value


class CCheckedActionsItemDelegate(CLocItemDelegate):
    def createEditor(self, parent, option, index):
        column = index.column()
        editor = index.model().createEditor(index, parent)
        self.connect(editor, QtCore.SIGNAL('commit()'), self.emitCommitData)
        self.connect(editor, QtCore.SIGNAL('editingFinished()'), self.commitAndCloseEditor)
        self.editor = editor
        self.row = index.row()
        self.rowcount = index.model().rowCount()
        self.column = column
        return editor

    def setEditorData(self, editor, index):
        if editor is not None:
            row = index.row()
            model = index.model()
            if row < len(model.items()):
                record = model.items()[row]
            else:
                record = model.getEmptyRecord()
            model.setEditorData(index, editor, model.data(index, QtCore.Qt.EditRole), record)

    def setModelData(self, editor, model, index):
        if editor is not None:
            model.setData(index, index.model().getEditorData(index, editor))

    def updateEditorGeometry(self, editor, option, index):
        def checkOnTextEdit(wgt):
            if isinstance(wgt, QtGui.QTextEdit):
                return True
            for child in wgt.children():
                if checkOnTextEdit(child):
                    return True
            return False

        CLocItemDelegate.updateEditorGeometry(self, editor, option, index)
        if checkOnTextEdit(editor):
            editor.resize(editor.width(), 8 * editor.height())


class CActionTypesView(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)
        self.__addToFavourites = QtGui.QAction(u'Добавить в Избранное', self)
        self.__addToFavourites.setObjectName('addToFavourites')
        self.addPopupAction(self.__addToFavourites)
        self.connect(self.__addToFavourites, QtCore.SIGNAL('triggered()'), self.on_addToFavourites_triggered)
        self.__delFromFavourites = QtGui.QAction(u'Удалить из избранного', self)
        self.__delFromFavourites.setObjectName('delFromFavourites')
        self.addPopupAction(self.__delFromFavourites)
        self.connect(self.__delFromFavourites, QtCore.SIGNAL('triggered()'), self.on_delFromFavourites_triggered)

    def on_addToFavourites_triggered(self):
        db = QtGui.qApp.db
        tablePFAT = db.table('Person_FavouriteActionTypes')
        record = tablePFAT.newRecord()
        record.setValue('person_id', toVariant(QtGui.qApp.userId))
        record.setValue('actionType_id', toVariant(self.currentItemId()))
        db.insertRecord(tablePFAT, record)
        self.model().updateFavourites()

    def on_delFromFavourites_triggered(self):
        db = QtGui.qApp.db
        tablePFAT = db.table('Person_FavouriteActionTypes')
        db.deleteRecord(tablePFAT, db.joinAnd([tablePFAT['person_id'].eq(QtGui.qApp.userId), tablePFAT['actionType_id'].eq(self.currentItemId())]))
        self.model().updateFavourites()

    def popupMenuAboutToShow(self):
        CTableView.popupMenuAboutToShow(self)
        recordExists = self.currentItemId() in self.model().favouritesSet
        showFavourites = QtGui.qApp.showFavouriteActionTypesButton()
        self.__delFromFavourites.setVisible(recordExists and showFavourites)
        self.__addToFavourites.setVisible(not recordExists and showFavourites)


class CCheckedActionsTableView(CInDocTableView):
    def __init__(self, parent):
        CInDocTableView.__init__(self, parent)
        self.setItemDelegate(CCheckedActionsItemDelegate(self))
        self.__actGetExecutionPlan = None

    def addGetExecutionPlan(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actGetExecutionPlan = QtGui.QAction(u'План выполнения назначений', self)
        self.__actGetExecutionPlan.setObjectName('actGetExecutionPlan')
        self.__actGetExecutionPlan.setShortcut(QtCore.Qt.Key_F2)
        self.addAction(self.__actGetExecutionPlan)
        self._popupMenu.addAction(self.__actGetExecutionPlan)
        self.connect(self.__actGetExecutionPlan, QtCore.SIGNAL('triggered()'), self.getExecutionPlan)

    def getExecutionPlan(self):
        currentRow = self.currentIndex().row()
        model = self.model()
        items = model.items()
        if 0 <= currentRow < len(items):
            actionTypeId = forceRef(items[currentRow].value('actionType_id'))
            action = model._idToAction[actionTypeId] if actionTypeId else None
            record = action.getRecord() if action else None
            if record and action:
                dialog = CGetExecutionPlan(self, record, action.getExecutionPlan())
                dialog.exec_()
                begDate = forceDateTime(record.value('begDate'))
                duration = forceInt(record.value('duration'))
                aliquoticity = forceInt(record.value('aliquoticity'))
                periodicity = forceInt(record.value('periodicity'))
                plannedEndDate = forceDateTime(record.value('plannedEndDate'))
                executionPlan = dialog.model.executionPlan
                executionPlanKeys = executionPlan.keys()
                executionPlanKeys.sort()
                executionPlanBegDate = executionPlan.get(pyDate(begDate.date()), {})
                if not executionPlanBegDate:
                    iKey = 0
                    periodicity = 0
                    aliquoticity = 0
                    for keyDate in executionPlanKeys:
                        iKey += 1
                        executionPlanTimes = executionPlan.get(keyDate, {})
                        aliquoticityNew = len(executionPlanTimes)
                        if aliquoticityNew:
                            executionPlanTimeKeys = executionPlanTimes.keys()
                            executionPlanTimeKeys.sort()
                            aliquoticity = aliquoticityNew
                            begDateDate = begDate.date()
                            durationNew = duration - begDateDate.daysTo(QtCore.QDate(keyDate))
                            duration = durationNew
                            iKeys = iKey
                            while len(executionPlanKeys) > iKeys:
                                periodicityDate = executionPlanKeys[iKeys]
                                periodicityPlanTimes = executionPlan.get(periodicityDate, {})
                                if len(periodicityPlanTimes):
                                    periodicity = QtCore.QDate(keyDate).daysTo(QtCore.QDate(periodicityDate)) - 1
                                    break
                                else:
                                    iKeys += 1
                            if periodicity < 0:
                                periodicity = 0
                            begDate = QtCore.QDateTime(QtCore.QDate(keyDate), executionPlanTimeKeys[0])
                            break
                else:
                    executionPlanBegDateKeys = executionPlanBegDate.keys()
                    executionPlanBegDateKeys.sort()
                    begTime = executionPlanBegDateKeys[0]
                    aliquoticity = len(executionPlanBegDateKeys)
                    begDate = QtCore.QDateTime(begDate.date(), begTime)
                    executionPlanKeys = executionPlan.keys()
                    executionPlanKeys.sort()
                    newBegDate = begDate.date().addDays(1)
                    maxBegDate = executionPlanKeys[len(executionPlanKeys) - 1]
                    while newBegDate <= maxBegDate:
                        periodicityPlanTimes = executionPlan.get(pyDate(newBegDate), {})
                        if len(periodicityPlanTimes):
                            periodicity = begDate.date().daysTo(newBegDate) - 1
                            break
                        else:
                            newBegDate = newBegDate.addDays(1)
                    if periodicity < 0:
                        periodicity = 0
                record.setValue('aliquoticity', toVariant(aliquoticity))
                record.setValue('begDate', toVariant(begDate))
                record.setValue('duration', toVariant(duration))
                record.setValue('periodicity', toVariant(periodicity))
                record.setValue('plannedEndDate', toVariant(begDate.addDays(duration - 1)))
                action.setExecutionPlan(dialog.model.executionPlan)

    def on_popupMenu_aboutToShow(self):
        row = self.currentIndex().row()
        rowCount = len(self.model().items())
        if self.__actGetExecutionPlan:
            self.__actGetExecutionPlan.setEnabled(0 <= row < rowCount)
