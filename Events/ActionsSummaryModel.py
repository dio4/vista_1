# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Action import ActionStatus, CActionType, CActionTypeCache
from Events.ActionTypeComboBox import CActionTypeTableCol
from Events.ContractTariffCache import CContractTariffCache
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import CFinanceType, getEventActionContract, payStatusText
from Orgs.OrgComboBox import CContractComboBox, CContractDbModel
from Users.Rights import urActionSetVerified
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.InDocTable import CActionPersonInDocTableColSearch, CBackRelationInDockTableCol, CBoolInDocTableCol, \
    CDateInDocTableCol, CEnumInDocTableCol, CFloatInDocTableCol, CInDocTableCol, \
    CInDocTableModel, CRBInDocTableCol, CTimeInDocTableCol
from library.MES.MESComboBox import CMesInDocTableCol
from library.Utils import forceBool, forceDate, forceDateTime, forceDouble, forceInt, forceRef, forceString, \
    forceStringEx, toVariant


# TODO: atronah: преобразовать в прокси-модель, чтобы не хранить одни и те же данные и избавиться от сложной логики на изменение записей.
class CActionsSummaryModel(CInDocTableModel):
    class CUetCol(CFloatInDocTableCol):
        def __init__(self, model):
            CFloatInDocTableCol.__init__(self, u'УЕТ',  'amount', 6, precision=2)
            self.model = model
            self.setReadOnly()

        def getUet(self, value, record):
            actionTypeId = forceRef(record.value('actionType_id'))
            personId = forceRef(record.value('person_id'))
            financeId = forceRef(record.value('finance_id'))
            contractId = forceRef(record.value('contract_id'))
            result = forceDouble(value) * self.model.eventEditor.getUet(actionTypeId, personId, financeId, contractId)
            return result

        def toString(self, value, record):
            if value.isNull():
                return value
            if not record:
                return QtCore.QVariant()

            v = self.getUet(value, record)
            s = QtCore.QString()
            if self.precision is None:
                s.setNum(v)
            else:
                s.setNum(v, 'f', self.precision)
            return toVariant(s)

    class CPayStatusCol(CInDocTableCol):
        def __init__(self):
            CInDocTableCol.__init__(self, u'Оплата', 'payStatus', 10)
            self.setReadOnly()

        def toString(self, value, record):
            payStatus = forceInt(value)
            return toVariant(payStatusText(payStatus))

    # модель сводки действий
    __pyqtSignals__ = (
        'currentRowMovedTo(int)',
        'amountChanged()',
        'actionsListChanged()',
        'updateCsg()'
    )

    def __init__(self, parent, editable=False, endDate=None, loadMedicaments = False, loadMedicamentsFields = True, addTime = False):
        self.addTime = addTime
        CInDocTableModel.__init__(self, 'Action', 'id', 'event_id', parent)
        self.addCol(CActionTypeTableCol(u'Тип', 'actionType_id', 15, None, classesVisible=True))  # 0
        self.addCol(CICDExInDocTableCol(u'МКБ', 'MKB', 10))  # 1
        self.addCol(CMesInDocTableCol(u'Стандарт', 'MES_id', 10, parent))  # 2
        self.addCol(CBoolInDocTableCol(u'Срочный', 'isUrgent', 10))  # 3
        self.addCol(CDateInDocTableCol(u'Назначено', 'directionDate', 15, canBeEmpty=True))  # 4
        self.addCol(CDateInDocTableCol(u'Начато', 'begDate', 15, canBeEmpty=True))  # 5
        if self.addTime:
            self.addCol(CTimeInDocTableCol(u'Время начала', 'begDate', 15, canBeEmpty=True, inputMask="hh:mm"))
        self.addCol(CDateInDocTableCol(u'Окончено', 'endDate', 15, canBeEmpty=True))  # 6
        if self.addTime:
            self.addCol(CTimeInDocTableCol(u'Время окончания', 'endDate', 15, canBeEmpty=True, inputMask="hh:mm"))
        self.addCol(CEnumInDocTableCol(u'Состояние', 'status', 10, CActionType.retranslateClass(False).statusNames))  # 7
        self.colSetPerson = self.addCol(CActionPersonInDocTableColSearch(u'Назначил', 'setPerson_id', 20, 'vrbPersonWithSpeciality', order='name', parent=parent))  # 8
        self.colExecPerson = self.addCol(CActionPersonInDocTableColSearch(u'Выполнил', 'person_id', 20, 'vrbPersonWithSpeciality', order='name', parent=parent, isExecPerson=True))  # 9
        # self.colAssistant = self.addCol(CActionPerson(u'Ассистент',           'assistant_id',  20, 'vrbPersonWithSpeciality', order = 'name', parent=parent)) #10

        #Формирование нетривиального столбца для ассистента, работающего с подчиненной/доп. таблицей
        assistantTypeId = forceRef(QtGui.qApp.db.translate('rbActionAssistantType', 'code', 'assistant', 'id'))
        newAssistantRecord = QtGui.qApp.db.table('Action_Assistant').newRecord()
        newAssistantRecord.setValue('assistantType_id', QtCore.QVariant(assistantTypeId))
        #FIXME: atronah: необходимо устанавливать фильтр для столбца ассистентов (подробнее в комментарии ниже)
        # заметил, что для поля ассистентов общей модели не ставится фильтр,
        # что приводит к проблемам синхронизации с, скажем, cmbAPAssistant на CActionPage объектах, у которых фильтр стоит.
        self.colAssistant = self.addExtCol(CBackRelationInDockTableCol(interfaceCol = CActionPersonInDocTableColSearch(u'Ассистент', # 10
                                                                                                    'person_id',
                                                                                                    20,
                                                                                                    'vrbPersonWithSpeciality',
                                                                                                    order = 'name',
                                                                                                    parent=parent),
                                                                       primaryKey = 'id',
                                                                       surrogateFieldName = 'assistant_id',
                                                                       subTableName = 'Action_Assistant',
                                                                       subTableForeignKey = 'action_id',
                                                                       subTableCond = 'assistantType_id = %s' % assistantTypeId,
                                                                       subTableNewRecord = newAssistantRecord),
                                           QtCore.QVariant.Int
        )

        #i3607
        if not QtGui.qApp.isPNDDiagnosisMode():
            self.addCol(CInDocTableCol(u'Каб', 'office', 6))  # 11

        self.colAmountIdx = len(self.cols()) # Не используется self.getColIndex(fieldName), так как имя 'amount' используется для нескольких столбцов
        self.addCol(CFloatInDocTableCol(u'Кол-во', 'amount', 6, precision=2))  # 12

        if not QtGui.qApp.isPNDDiagnosisMode():
            self.colUetIdx = len(self.cols())  # Не используется self.getColIndex(fieldName), так как имя 'amount' используется для нескольких столбцов
            self.colUet = self.addCol(CActionsSummaryModel.CUetCol(self))  # 13

        self.addCol(CInDocTableCol(u'Примечания', 'note', 40))  # 14
        if loadMedicamentsFields:
            self.addCol(CFloatInDocTableCol(u'Закупочная стоимость упаковки', 'packPurchasePrice', 10, precision=2)) # 15
            self.addCol(CFloatInDocTableCol(u'Стоимость курсовой дозы', 'doseRatePrice', 10, precision=2)) # 16

        if not QtGui.qApp.isPNDDiagnosisMode():
            self.colOrgId = self.addCol(CInDocTableCol(u'Место выполнения', 'org_id', 20))
            self.addHiddenCol(self.colOrgId)

        if forceStringEx(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')) == u'б15':
            # self.addCol(CBoolInDocTableCol(u'Проверено', 'isVerified', 5))
            verifiedCol = self.addCol(CEnumInDocTableCol(u'Проверено', 'isVerified', 5, (u'Не проверено', u'Проверено', u'Проверено с ошибкой')))
            if not QtGui.qApp.userHasRight(urActionSetVerified):
                verifiedCol.setReadOnly()

        self.models = []
        self.notDeletedActionTypes = {}
        self.itemIndex = []
        self.setEditable(editable)
        self.setEnableAppendLine(self.isEditable())
        self.eventEditor = parent
        self._parent = parent
        self.connect(self.eventEditor, QtCore.SIGNAL('updateActionsPriceAndUet()'), self.updateActionsPriceAndUet)
        self.medicamentsIdList = []
        self.medicamentIsPresent = False
        self._actionTypeCompatibilitiesCache = {}

        if loadMedicaments:
            self.loadMedicamentIdList()

    def emitUpdateCsg(self):
        self.emit(QtCore.SIGNAL('updateCsg()'))

    def addModel(self, model):
        self.connect(model, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.onDataChanged)
        self.connect(model, QtCore.SIGNAL('modelReset'), self.onModelReset)
        self.connect(model, QtCore.SIGNAL('rowsInserted(QModelIndex, int, int)'), self.onRowInserted)
        self.connect(model, QtCore.SIGNAL('rowsRemoved(QModelIndex, int, int)'), self.onRowRemoved)
        self.connect(model, QtCore.SIGNAL('amountChanged(int)'), self.onAmountChanged)
        self.models.append(model)

    def regenerate(self):
        items = []
        itemIndex = []
        self.notDeletedActionTypes = {}
        for i, model in enumerate(self.models):
            self.notDeletedActionTypes.update(model.notDeletedActionTypes)
            for j, (record, action) in enumerate(model.items()):
                items.append(record)
                itemIndex.append((i, j))
        self.itemIndex = itemIndex
        self.setItems(items)
        self.checkMedicamentsPresence(items)
        self.emit(QtCore.SIGNAL('hideMedicamentColumns(bool)'), not self.medicamentIsPresent)

    def checkMedicamentsPresence(self, items):
        for item in items:
            actionTypeId = forceRef(item.value('actionType_id'))
            if actionTypeId:
                actionType = CActionTypeCache.getById(actionTypeId)
                if actionType.nomenclativeServiceId in self.medicamentsIdList:
                    self.medicamentIsPresent = True
                    break

    def onDataChanged(self, topLeft, bottomRight):
        newTop = 0
        newBottom = len(self.itemIndex) - 1

        if topLeft.model() in self.models:
            iModel = self.models.index(topLeft.model())
            top, bottom = topLeft.row(), bottomRight.row()
            try:
                newTop = self.itemIndex.index((iModel, top))
            except:
                newTop = 0
            try:
                newBottom = self.itemIndex.index((iModel, bottom))
            except:
                newBottom = len(self.itemIndex)-1

        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.index(newTop, 0), self.index(newBottom, len(self.cols())-1))

    def onModelReset(self):
        self.regenerate()

    def onRowInserted(self, parent, start, end):
        self.regenerate()
        self.emitUpdateCsg()

    def onRowRemoved(self, parent, start, end):
        self.regenerate()
        self.emitUpdateCsg()

    def onAmountChanged(self, row):
        self.emit(QtCore.SIGNAL('amountChanged()'))

    def isLocked(self, row):
        iModel, iAction = self.itemIndex[row]
        actionsModel = self.models[iModel]
        return actionsModel.isLocked(iAction)

    def isLockedOrExposed(self, row):
        iModel, iAction = self.itemIndex[row]
        actionsModel = self.models[iModel]
        return actionsModel.isLockedOrExposed(iAction)

    def isDeletable(self, row):
        if 0 <= row < len(self._items):
            mdl_index, row = self.itemIndex[row]
            model = self.models[mdl_index]
            record, action = model.getItemByRow(row)
            return not self.isLockedOrExposed(row) and action.isDeletable() and model.isDeletable(row)
        return True

    def flags(self, index=QtCore.QModelIndex()):
        if self.isEditable():
            row, column = index.row(), index.column()
            items = self.items()

            if 0 <= row < len(items):
                iModel, iAction = self.itemIndex[row]
                actionsModel = self.models[iModel]
                if actionsModel.isLocked(iAction) \
                        or column == self.getColIndex('actionType_id') \
                        or forceInt(items[row].value('payStatus')):
                    return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

            if column == self.getColIndex('MKB'):
                record = items[row] if 0 <= row < len(items) else None
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    if actionType.defaultMKB:
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
                    else:
                        return QtCore.Qt.ItemIsSelectable

            elif column == self.getColIndex('MES_id'):
                record = items[row] if 0 <= row < len(items) else None
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    if actionType.defaultMES:
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
                    else:
                        return QtCore.Qt.ItemIsSelectable

            elif column == self.getColIndex('assistant_id'):
                record = items[row] if 0 <= row < len(items) else None
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    if actionType.hasAssistant:
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
                    else:
                        return QtCore.Qt.ItemIsSelectable

            elif column == self.colAmountIdx:  # amount
                record = items[row] if 0 <= row < len(items) else None
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    if actionType.amountEvaluation == 0:
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
                    else:
                        return QtCore.Qt.ItemIsSelectable

            elif hasattr(self, 'colUetIdx') and column == self.colUetIdx:
                return QtCore.Qt.ItemIsSelectable

            elif column in [self.getColIndex('note'),
                            self.getColIndex('packPurchasePrice')]:
                record = items[row] if 0 <= row < len(items) else None
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                if actionTypeId:
                    actionType = CActionTypeCache.getById(actionTypeId)
                    if actionType.nomenclativeServiceId not in self.medicamentsIdList:
                        return CInDocTableModel.flags(self, index) & (~QtCore.Qt.ItemIsEditable)
                    else:
                        return QtCore.Qt.ItemIsSelectable

            elif column in [self.getColIndex('begDate'),
                            self.getColIndex('endDate')] and self.addTime:
                record = items[row] if 0 <= row < len(items) else None
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                if actionTypeId:
                    self.createEditor(column, self.eventEditor)
                    actionType = CActionTypeCache.getById(actionTypeId)
                    if actionType.showTime and bool(forceDate(record.value('begDate'))):
                        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
                    else:
                        return QtCore.Qt.ItemIsSelectable

            return CInDocTableModel.flags(self, index)
        else:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def getIncompatibilities(self, actionTypeId):
        result = self._actionTypeCompatibilitiesCache.get(actionTypeId, None)
        if result is None:
            db = QtGui.qApp.db
            tableATI = db.table('rbActionTypeIncompatibility')
            firstSecond = ('firstActionType_id', 'secondActionType_id')
            result = {}
            for idField, otherIdField in (firstSecond, reversed(firstSecond)):
                for record in db.iterRecordList(tableATI, [tableATI[idField], tableATI['reason']], tableATI[otherIdField].eq(actionTypeId)):
                    result[forceRef(record.value(idField))] = forceString(record.value('reason'))
            self._actionTypeCompatibilitiesCache[actionTypeId] = result
        return result

    def checkCompatibility(self, actionTypeId):
        incompatibilities = self.getIncompatibilities(actionTypeId)
        actionTypeName = CActionTypeCache.getById(actionTypeId).name

        items = []
        for x in self.models:
            items += x.items()

        for item in items:
            action = item[1]
            if not action:
                continue
            typeId = action.getType().id
            if typeId in incompatibilities:
                result = QtGui.QMessageBox.critical(
                    self.eventEditor,
                    u'Внимание!',
                    u'Выбранные мероприятия не совместимы.\n%s и %s могут иметь следующие последствия: %s' % (
                        action.getType().name,
                        actionTypeName,
                        incompatibilities[typeId]
                    ),
                                                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore)
                if result == QtGui.QMessageBox.Ignore:
                    continue
                return False
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole, presetAction=None):
        row, column = index.row(), index.column()
        items = self.items()
        cols = self.cols()
        col = cols[column]
        fieldName = col.fieldName()
        self.updateRetiredList()
        self.colExecPerson.setSpecialityRequired(True)

        if role == QtCore.Qt.EditRole:
            if row == self.rowCount() - 1:
                if value.isNull() or fieldName != 'actionType_id':
                    return False
                actionTypeId = forceRef(value)
                actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                actionTypeClass = actionType.class_ if actionType else None

                if actionTypeId and not self.checkCompatibility(actionTypeId):
                    return False

                for iModel, model in enumerate(self.models):
                    if model.actionTypeClass == actionTypeClass or (isinstance(model.actionTypeClass, list) and actionTypeClass in model.actionTypeClass):
                        if not model.checkPeriodicActionPosibility(actionTypeId):
                            break
                        model.addRow(forceRef(value), presetAction=presetAction)

                        if actionType and actionType.isSubstituteEndDateToEvent and self.eventEditor and hasattr(self.eventEditor, 'edtEndDate'):
                            date = forceDate(presetAction.getRecord().value('endDate'))
                            self.eventEditor.edtEndDate.setDate(date)
                        self.regenerate()
                        try:
                            # TODO: слот-обработчик этого сигнала пустой, нужно ли это вообще?
                            i = self.itemIndex.index((iModel, model.rowCount() - 2))
                            self.emit(QtCore.SIGNAL('currentRowMovedToWithActionTypeClass(int,int)'), i,
                                      actionTypeClass if actionTypeClass is not None else -1)
                        except ValueError as e:
                            pass
                        return True
                return False
            iModel, iAction = self.itemIndex[row]
            actionsModel = self.models[iModel]
            if actionsModel.isLocked(iAction):
                return False
            record = items[row]
            oldValue = record.value(fieldName)
            if oldValue != value:
                if fieldName == 'actionType_id':
                    actionTypeId = forceRef(value)
                    oldActionTypeId = forceRef(oldValue)
                    newClass = CActionTypeCache.getById(actionTypeId).class_ if actionTypeId else None
                    oldClass = CActionTypeCache.getById(oldActionTypeId).class_ if oldActionTypeId else None
                    if newClass == oldClass:
                        actionsModel.setData(actionsModel.index(iAction, 0), value, QtCore.Qt.EditRole)
                    else:
                        actionsModel.removeRow(iAction)
                        for iModel, model in enumerate(self.models):
                            if model.actionTypeClass == newClass or (type(model.actionTypeClass) == list and newClass in model.actionTypeClass):
                                model.addRow(forceRef(value))
                                self.regenerate()
                                i = self.itemIndex.index((iModel, model.rowCount() - 2))
                                self.emit(QtCore.SIGNAL('currentRowMovedTo(int)'), i)
                                return True
                else:
                    if fieldName == 'begDate' or fieldName == 'endDate':
                        oldValue = oldValue.toDateTime()
                        if value.toDateTime().isNull():
                            oldValue.setTime(QtCore.QTime.fromString(value.toString(), "hh:mm:ss"))
                        else:
                            oldValue.setDate(forceDate(value))
                        value = oldValue
                    record.setValue(fieldName, value)
                    if fieldName == 'endDate':
                        date = forceDate(value)
                        status = forceInt(record.value('status'))
                        newStatus = status
                        if date:
                            # Статус "Отменено" менять запретили :( А вслед за ним и новый "Не предусмотрено"
                            if newStatus not in (ActionStatus.Cancelled,
                                                 ActionStatus.NotProvided):
                                newStatus = ActionStatus.Done
                            actionTypeId = forceRef(record.value('actionType_id'))
                            actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                            if actionType and actionType.isSubstituteEndDateToEvent and self.eventEditor and hasattr(self.eventEditor, 'edtEndDate'):
                                self.eventEditor.edtEndDate.setDate(date)
                        else:
                            if status in (ActionStatus.Done,
                                          ActionStatus.WithoutResult,
                                          ActionStatus.Cancelled):
                                newStatus = ActionStatus.Cancelled
                        if status != newStatus:
                            record.setValue('status', toVariant(newStatus))
                            self.emitValueChanged(row, 'status')
                    elif fieldName == 'status':
                        status = forceInt(value)
                        date = forceDate(record.value('endDate'))
                        newDate = date
                        if status in (ActionStatus.Done,
                                      ActionStatus.WithoutResult,
                                      ActionStatus.Appointed) and not date.isValid():
                            newDate = QtCore.QDateTime.currentDateTime()
                        elif status not in (ActionStatus.Cancelled,
                                            ActionStatus.Done,
                                            ActionStatus.NotProvided):
                            newDate = QtCore.QDateTime()
                        if newDate != date:
                            record.setValue('endDate', toVariant(newDate))
                            self.emitValueChanged(row, 'endDate')
                        self.emitUpdateCsg()
                    elif fieldName == 'MKB':
                        MKB = forceString(value)
                        if not self.eventEditor.checkDiagnosis(MKB):
                            record.setValue('MKB', toVariant(oldValue))
                            self.emitValueChanged(row, 'MKB')
                    elif fieldName == 'assistant_id':
                        action = actionsModel.items()[iAction][1]
                        action.setAssistant('assistant', value)

                    self.emitCellChanged(row, column)
                    index = actionsModel.index(iAction, 0)
                    actionsModel.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
                    actionsModel.updateActionAmount(iAction)
            return True

        elif role == QtCore.Qt.CheckStateRole:
            if row == self.rowCount() - 1:
                return False
            iModel, iAction = self.itemIndex[row]
            actionsModel = self.models[iModel]
            if actionsModel.isLocked(iAction):
                return False
            record = items[row]
            oldValue = record.value(fieldName)
            if oldValue != value:
                record.setValue(fieldName, value)
                self.emitCellChanged(row, column)
                index = actionsModel.index(iAction, 0)
                actionsModel.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
                actionsModel.updateActionAmount(iAction)
            return True
        return False

    def setBegDate(self, row, date):
        self.setData(self.index(row, self.getColIndex('directionDate')), toVariant(date), QtCore.Qt.EditRole)
        self.setData(self.index(row, self.getColIndex('begDate')), toVariant(date), QtCore.Qt.EditRole)

    def calcTotalUet(self):
        return sum(self.colUet.getUet(item.value('amount'), item) for item in self.items())

    def updateActionsPriceAndUet(self):
        assistantIdx = self.getColIndex('assistant_id')
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.index(0, assistantIdx), self.index(len(self.items()), assistantIdx))

    def loadMedicamentIdList(self):
        db = QtGui.qApp.db
        tableService = db.table('rbService')
        tableMrbMedicament = db.table('mes.mrbMedicament')

        table = tableService.innerJoin(tableMrbMedicament, tableMrbMedicament['code'].eq(tableService['code']))
        self.medicamentsIdList = db.getDistinctIdList(table, tableService['id'], tableMrbMedicament['id'].isNotNull())

    def addAction(self, action):
        index = self.index(self.rowCount()-1, 0)
        self.setData(index, toVariant(action.getType().id), presetAction=action)
        return index.row()


class CAccActionsSummary(CActionsSummaryModel):
    __pyqtSignals__ = ('sumChanged()',
                      )

    class CFinanceInDocTableCol(CRBInDocTableCol):
        def __init__(self):
            CRBInDocTableCol.__init__(self, u'Тип финансирования', 'finance_id', 10, 'rbFinance', addNone=True, prefferedWidth=100)
            self.eventEditor = None

    class CContractInDocTableCol(CInDocTableCol):
        def __init__(self):
            CInDocTableCol.__init__(self, u'Договор', 'contract_id', 20)
            self.eventEditor = None

        def toString(self, val, record):
            contractId = forceRef(val)
            if contractId:
                names = ['number', 'date', 'resolution']
                record = QtGui.qApp.db.getRecord('Contract', names, contractId)
                string = ' '.join(forceString(record.value(name)) for name in names)
            else:
                string = u'не задано'
            return QtCore.QVariant(string)

        def getFirstContractId(self, actionTypeId, financeId, begDate, endDate):
            model = CContractDbModel(None)
            model.setOrgId(self.eventEditor.orgId)
            model.setEventTypeId(self.eventEditor.eventTypeId)
            model.setClientInfo(self.eventEditor.clientId,
                                 self.eventEditor.clientSex,
                                 self.eventEditor.clientAge,
                                 self.eventEditor.clientWorkOrgId,
                                 self.eventEditor.clientPolicyInfoList)
            model.setFinanceId(financeId)
            model.setActionTypeId(actionTypeId)
            model.setBegDate(begDate or QtCore.QDate.currentDate())
            model.setEndDate(endDate or QtCore.QDate.currentDate())
            model.initDbData()
            return model.getId(0)

        def createEditor(self, parent):
            editor = CContractComboBox(parent)
            editor.setOrgId(self.eventEditor.orgId)
            editor.setClientInfo(self.eventEditor.clientId,
                                 self.eventEditor.clientSex,
                                 self.eventEditor.clientAge,
                                 self.eventEditor.clientWorkOrgId,
                                 self.eventEditor.clientPolicyInfoList)
            return editor

        def setEditorData(self, editor, value, record):
            financeId = forceRef(record.value('finance_id')) or self.eventEditor.eventFinanceId
            editor.setFinanceId(financeId)
            editor.setActionTypeId(forceRef(record.value('actionType_id')))
            contractId = forceRef(value)
            if contractId is None:
                if financeId == self.eventEditor.eventFinanceId:
                    contractId = self.eventEditor.contractId
            editor.setValue(contractId)
            editor.setBegDate(forceDate(record.value('directionDate')) or QtCore.QDate.currentDate())
            editor.setEndDate(forceDate(record.value('endDate')) or QtCore.QDate.currentDate())

        def getEditorData(self, editor):
            contractId = editor.value()
            return toVariant(contractId)

    def __init__(self, parent, editable=False):
        CActionsSummaryModel.__init__(self, parent, editable, loadMedicamentsFields = False)
        for col in self.cols():
            col.setReadOnly(True)

        self.addExtCol(CBoolInDocTableCol(u'Считать', 'account', 10), QtCore.QVariant.Int)  # 14
        self.addExtCol(CFloatInDocTableCol(u'Цена', 'price', 6, precision=2), QtCore.QVariant.Double).setReadOnly(True)  # 15
        self.addExtCol(CFloatInDocTableCol(u'Сумма', 'sum', 6, precision=2), QtCore.QVariant.Double).setReadOnly(True)  # 16
        self.addCol(CFloatInDocTableCol(u'Изменяемая сумма', 'customSum', 6, precision=2))
        self.financeCol  = self.addCol(CAccActionsSummary.CFinanceInDocTableCol()) #17
        self.contractCol = self.addCol(CAccActionsSummary.CContractInDocTableCol()) #18
        self.addCol(CActionsSummaryModel.CPayStatusCol()) #19
        self.prices = []
        self.sums = []
        self.accSum = []
        self.setEnableAppendLine(False)

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor
        self.financeCol.eventEditor = eventEditor
        self.contractCol.eventEditor = eventEditor

    def regenerate(self):
        CActionsSummaryModel.regenerate(self)
        count = len(self.items())
        self.prices = [0.0]*count
        self.sums = [0.0]*count
        self.accSum = [0.0]*count
        self.setCountFlag()
        self.updatePricesAndSums(0, count-1)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.StatusTipRole:
            column = index.column()
            row = index.row()
            if 0<=row<len(self.items()):
                col = self.cols()[column]
                fieldName = col.fieldName()
                if fieldName == 'price':
                    return QtCore.QVariant(self.prices[row])
                elif fieldName == 'sum':
                    return QtCore.QVariant(self.sums[row])
        return CActionsSummaryModel.data(self, index, role)

    def flags(self, index=QtCore.QModelIndex()):
        flags = super(CAccActionsSummary, self).flags(index)
        row = index.row()
        column = index.column()
        if row >= 0 and self.cols()[column].fieldName() == 'customSum':
            actionTypeId = forceRef(self.items()[row].value('actionType_id'))
            actionType = CActionTypeCache.getById(actionTypeId)
            if not actionType.isCustomSum:
                flags &= ~QtCore.Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        items = self.items()
        cols = self.cols()
        col = cols[column]
        fieldName = col.fieldName()
        if role == QtCore.Qt.EditRole:
            iModel, iAction = self.itemIndex[row]
            actionsModel = self.models[iModel]
            if actionsModel.isLocked(iAction):
                return False
            record = items[row]
            oldValue = record.value(fieldName)
            if oldValue != value:
                if fieldName == 'note':
                    record.setValue(fieldName, value)
                    self.emitCellChanged(row, column)
                if fieldName == 'finance_id':
                    record.setValue(fieldName, value)
                    self.emitCellChanged(row, column)
                    self.initContract(row)
                    self.updatePricesAndSums(row, row)
                elif fieldName == 'contract_id':
                    record.setValue(fieldName, value)
                    self.emitCellChanged(row, column)
                    self.updatePricesAndSums(row, row)
                elif fieldName == 'amount':
                    record.setValue(fieldName, value)
                    self.emitCellChanged(row, column)
                    self.updatePricesAndSums(row, row)
                elif fieldName == 'customSum':
                    record.setValue(fieldName, value)
                    self.emitCellChanged(row, column)
                else:
                    return False
            return True
        if role == QtCore.Qt.CheckStateRole:
            if fieldName == 'account':
                val = forceInt(items[row].value('account'))
                items[row].setValue('account',  QtCore.QVariant(forceInt(not val)))
                self.emitCellChanged(row, column)
                self.updatePricesAndSums(0, len(self.items())-1)
            return True
        return False

    def initContract(self, row):
        item = self.items()[row]
        actionTypeId = forceRef(item.value('actionType_id'))
        financeId = forceRef(item.value('finance_id'))
        if financeId:
            if financeId == self.eventEditor.eventFinanceId and getEventActionContract(self.eventEditor.eventTypeId):
                contractId = self.eventEditor.contractId
            else:
                begDate = forceDate(item.value('directionDate'))
                endDate = forceDate(item.value('endDate'))
                contractId = self.contractCol.getFirstContractId(actionTypeId, financeId, begDate, endDate)
        else:
            contractId = None
        item.setValue('contract_id', toVariant(contractId))
        self.emitValueChanged(row, 'contract_id')

    def onDataChanged(self, topLeft, bottomRight):
        CActionsSummaryModel.onDataChanged(self, topLeft, bottomRight)
        self.updatePricesAndSums(topLeft.row(), bottomRight.row())

    def onAmountChanged(self, row):
        CActionsSummaryModel.onAmountChanged(self, row)
        iModel = self.models.index(self.sender())
        try:
            row = self.itemIndex.index((iModel, row))
        except:
            row = -1

        if row>=0:
            self.updatePricesAndSums(row, row)
        else:
            self.updatePricesAndSums(0, len(self.items())-1)

    #TODO: atronah: refactoring: идентично CEventEditDialog.setContractId
    def setContractId(self, contractId):
        if getEventActionContract(self.eventEditor.eventTypeId):
            financeId = self.eventEditor.eventFinanceId
            for row, item in enumerate(self.items()):
                if forceRef(item.value('finance_id')) == financeId:
                    item.setValue('contract_id', contractId)
#                self.emitFieldChanged(row, 'contract_id')
                self.emitCellChanged(row, self.getColIndex('contract_id'))
        self.updatePricesAndSums(0, len(self.items())-1)

    def getTariffMap(self, contractId):
        tariffDescr = self.eventEditor.contractTariffCache.getTariffDescr(contractId, self.eventEditor)
        return tariffDescr.actionTariffMap

    def setCountFlag(self):
        cashFinanceId = CFinanceType.getId(CFinanceType.cash)
        eventFinanceId = self.eventEditor.eventFinanceId
        for item in self.items():
            itemFinanceId = forceRef(item.value('finance_id'))
            if itemFinanceId is None:
                itemFinanceId = eventFinanceId
            item.setValue('account', toVariant(itemFinanceId == cashFinanceId))

    def updatePricesAndSums(self, top, bottom):
        sumChanged = False
        for i in xrange(top, bottom+1):
            if 0 <= i < len(self._items):
                sumChanged = self.updatePriceAndSum(i, self.items()[i]) or sumChanged
        if sumChanged:
            self.emitSumChanged()

    def updatePriceAndSum(self, row, item):
        result = False
        actionTypeId = forceRef(item.value('actionType_id'))
        if actionTypeId:
            personId = forceRef(item.value('person_id'))
            tariffCategoryId = self.eventEditor.getPersonTariffCategoryId(personId)
            contractId = forceRef(item.value('contract_id'))
            if contractId:
                financeId = forceRef(QtGui.qApp.db.translate('Contract', 'id', contractId, 'finance_id'))
            else:
                contractId = self.eventEditor.contractId
                financeId = self.eventEditor.eventFinanceId
            serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
            price = CContractTariffCache.getPrice(self.getTariffMap(contractId), serviceIdList, tariffCategoryId)
        else:
            price = 0.0
        if self.prices[row] != price:
            self.prices[row] = price
            self.emitValueChanged(row, self.getColIndex('price'))
        totalSum = price*forceDouble(item.value('amount'))
        if totalSum != self.sums[row]:
            result = True
            self.sums[row] = totalSum
            self.emitCellChanged(row, self.getColIndex('sum'))
        if forceBool(item.value('account')):
            self.accSum[row] = totalSum
            result = True
        else:
            self.accSum[row] = 0
            result = True
        return result

    def emitSumChanged(self):
        self.emit(QtCore.SIGNAL('sumChanged()'))

    def sum(self):
        return sum(self.accSum)

    def getDischargePayType(self):
        for row in range(self.rowCount()):
            actType = forceString(self.data(self.index(row,  self.getColIndex('actionType_id'))))
            if u'Выписка' in actType:
                actFinType = self.data(self.index(row,  self.getColIndex('finance_id')),  role = QtCore.Qt.EditRole)
                if actFinType:
                    return forceInt(actFinType),  row
                else:
                    return None,  row

        return None,  None


class CFxxxActionsSummaryModel(CActionsSummaryModel):
    def setData(self, index, value, role=QtCore.Qt.EditRole, presetAction=None):
        result = CActionsSummaryModel.setData(self, index, value, role, presetAction)
        if result:
            column = index.column()
            if column == self.getColIndex('endDate'):
                newDateTime = forceDateTime(value)
                if not newDateTime.isValid():
                    pass
                elif newDateTime < self.eventEditor.eventSetDateTime:
                    self.setBegDate(index.row(), forceDate(value))
                elif newDateTime >= self.eventEditor.eventSetDateTime:
                    row = index.row()
                    if not forceDate(self.data(self.index(row, self.getColIndex('directionDate')), QtCore.Qt.EditRole)):
                        self.setData(self.index(row, self.getColIndex('directionDate')), toVariant(self.eventEditor.eventSetDateTime), QtCore.Qt.EditRole)
                    if not forceDate(self.data(self.index(row, self.getColIndex('begDate')), QtCore.Qt.EditRole)):
                        self.setData(self.index(row, self.getColIndex('begDate')), toVariant(self.eventEditor.eventSetDateTime), QtCore.Qt.EditRole)
        return result

    def setBegDate(self, row, date):
        execDate = forceDate(self.data(self.index(row, self.getColIndex('endDate')), QtCore.Qt.EditRole))
        if not execDate:
            CActionsSummaryModel.setBegDate(self, row, date)
        else:
            CActionsSummaryModel.setBegDate(self, row, date if date<=execDate else QtCore.Date())
