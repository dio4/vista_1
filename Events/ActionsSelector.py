# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from collections import defaultdict

from Events.Action import ActionClass, ActionStatus, CActionType, CActionTypeCache
from Events.ActionEditDialog import CActionEditDialog
from Events.ActionTypeComboBox import CActionTypeModel, getActionTypeIdListByContract
from Events.ActionsModel import getActionDefaultAmountEx, getActionDefaultContractId
from Events.ActionsSelectorSelectedTable import CCheckedActionsModel
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import CEventTypeDescription, getEventGoalFilter, getEventLengthDays, recordAcceptable, \
    getMainActionTypesAnalyses
from Orgs.Utils import getActionTypesIdSetByClasses, getOrgStructureActionTypeIdSet, getTopParentIdForOrgStructure
from Ui_ActionsSelectorDialog import Ui_ActionsSelectorDialog
from Users.Rights import urDisableCheckActionSpeciality
from library.DialogBase import CDialogBase
from library.MES.Utils import getMedicamentServiceIdList, getMesServiceInfo, getServiceIdList
from library.TableModel import CBoolCol, CDateCol, CEnumCol, CRefBookCol, CTableModel, CTextCol
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, formatNum, \
    getActionTypeIdListByMKB, getPref, setPref, smartDict, toVariant


def getActionTypeIdListByMesId(mesId, necessity=None, isGrouping = False, date = None):
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')

    serviceIdInfo = getServiceIdList(mesId, necessity, isGrouping, date=date)
    if isGrouping:
        result = {}
        for groupCode, serviceIdList in serviceIdInfo.iteritems():
            cond = [
                tableActionType['nomenclativeService_id'].inlist(serviceIdList),
                tableActionType['deleted'].eq(0),
            ]
            result[groupCode] = db.getDistinctIdList(tableActionType, tableActionType['id'], cond)
    else:
        cond = [
            tableActionType['nomenclativeService_id'].inlist(serviceIdInfo),
            tableActionType['deleted'].eq(0)
        ]
        result = db.getDistinctIdList(tableActionType, tableActionType['id'], cond)
    return result


def getMedicamentActionTypeIdListByMesId(mesId, necessity=None):
    serviceIdList = getMedicamentServiceIdList(mesId, necessity)
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    cond = [tableActionType['deleted'].eq(0),
            tableActionType['nomenclativeService_id'].inlist(serviceIdList)]
    return db.getDistinctIdList(tableActionType, tableActionType['id'], cond)


def selectActionTypes(parent, actionTypeClasses=None, clientSex=None, clientAge=None, orgStructureId=None,
                      eventTypeId=None, contractId=None, mesId=None, chkContractByFinanceId=None,
                      eventId=None, existsActionTypesList=None, contractTariffCache=None,
                      eventEditorOwner=None, notFilteredActionTypesClasses=None, defaultFinanceId=None,
                      defaultContractFilterPart=None, showAmountFromMes=None, eventBegDate=None,
                      eventEndDate=QtCore.QDate(), showMedicaments=False, isQuietAddingByMes=False, paymentScheme=None,
                      MKB=None, chosenActionTypes=None, returnDirtyRows=False):
    u"""
    Открыает редактор выбора типов действия для добавления
    :return: list of tuple (ActionType.id, CAction)
    :rtype: list
    """
    QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    dlg = CActionTypesSelectionDialog(parent)
    dlg.setBlockSignals(True)
    dlg.setExistsActionTypes(existsActionTypesList or [])
    dlg.setOrgStructurePriority(eventTypeId)
    if hasattr(parent, 'cmbPerson'):
        dlg.setExecPerson(parent.cmbPerson.value())
    dlg.setMesId(mesId)
    dlg.setShowAmount(showAmountFromMes)
    dlg.setShowMedicaments(showMedicaments)
    dlg.setActionTypeClasses(actionTypeClasses or [])
    dlg.setSexAndAge(clientSex, clientAge)
    dlg.setEventId(eventId)
    dlg.setSpecialityId()
    dlg.setEventTypeId(eventTypeId)
    dlg.setDefaultFinanceId(defaultFinanceId)
    dlg.setDefaultContractFilterPart(defaultContractFilterPart)
    dlg.setOrgStructureId(orgStructureId)
    dlg.setContractId(contractId, chkContractByFinanceId)
    dlg.updateSelectedCount()
    dlg.setContractTariffCache(contractTariffCache)
    dlg.setBegDate(eventBegDate)
    dlg.setEndDate(eventEndDate)
    dlg.setClientId()
    dlg.setNotFilteredClasses(notFilteredActionTypesClasses or [])
    dlg.setMKB(MKB)
    dlg.setBlockSignals(False)
    dlg.setEventEditorOwner(eventEditorOwner)
    dlg.setPaymentScheme(paymentScheme)
    dlg.setPreviousActionTypeIds(chosenActionTypes or [])
    QtGui.qApp.restoreOverrideCursor()

    if isQuietAddingByMes:
        dlg.updateTreeData()
        dlg.chkNecessity.setChecked(True)
        dlg.edtNecessity.setValue(1.00)
        dlg.on_bntSelectAll_pressed()

    if isQuietAddingByMes or dlg.exec_():
        result = dlg.getSelectedList(returnDirtyRows)
    else:
        result = []
    result = checkAmount(result, contractId, eventId)
    return result

def checkAmount(actions, contractId, eventId):
    db = QtGui.qApp.db
    tblActTypeService = db.table('ActionType_Service')
    tblContractTariff = db.table('Contract_Tariff')
    tblEvent = db.table('Event')
    tblAction = db.table('Action')
    tableActions = tblEvent.innerJoin(tblAction, tblEvent['id'].eq(tblAction['event_id']))
    table = tblActTypeService.innerJoin(tblContractTariff, tblContractTariff['service_id'].eq(tblActTypeService['service_id']))

    elementsForDelete = []
    for actionTypeId, action in actions:
        recAmount = db.getRecordEx(table, tblContractTariff['amount'], [tblContractTariff['master_id'].eq(contractId), tblActTypeService['master_id'].eq(actionTypeId)])
        if recAmount and forceInt(recAmount.value('amount')):
            recEventAmount = db.getRecordEx(tableActions, tblAction['amount'], [tblEvent['id'].eq(eventId), tblAction['actionType_id'].eq(actionTypeId)])
            if recEventAmount:
                total = forceInt(recEventAmount.value('amount')) + forceInt(action._record.value('amount'))
            else:
                total = forceInt(action._record.value('amount'))

            if total > forceInt(recAmount.value('amount')):
                QtGui.QMessageBox.warning(None, u'Ошибка', u'Превышено максимальное количество назначений:\n' + forceString(action._actionType.name))
                elementsForDelete.append((actionTypeId, action))
    if elementsForDelete:
        for element in elementsForDelete:
            actions.remove(element)
    return actions




class CActionTypesSelectionManager(object):
    def __init__(self):
        self.selectedActionTypeIdList = []
        self.actionTypeIdList = []
        self.actionsCacheByCode = {}
        self.actionsCacheByName = {}

    def updateSelectedCount(self):
        pass

    def getSelectedList(self):
        return self.getSelectedActionTypeIdList()

    def getSelectedActionTypeIdList(self):
        return self.selectedActionTypeIdList

    def setSelected(self, actionTypeId, value):
        present = self.isSelected(actionTypeId)
        if value:
            if not present:
                self.selectedActionTypeIdList.append(actionTypeId)
                self.updateSelectedCount()
                return True
        else:
            if present:
                self.selectedActionTypeIdList.remove(actionTypeId)
                self.updateSelectedCount()
                return True
        return False

    def isSelected(self, actionTypeId):
        return actionTypeId in self.selectedActionTypeIdList

    def findByCode(self, value):
        uCode = unicode(value).upper()
        return [self.actionTypeIdList[self.actionsCacheByCode[c]]
                for c in sorted(self.actionsCacheByCode.keys())
                if unicode(c).startswith(uCode)]

    def findByName(self, name):
        uName = unicode(name).upper()
        return [self.actionTypeIdList[self.actionsCacheByName[n]]
                for n in sorted(self.actionsCacheByName.keys())
                if uName in n]


class CActionTypesSelectionDialog(CDialogBase, CActionTypesSelectionManager, Ui_ActionsSelectorDialog):
    cachePlannedActionTypesBySpeciality   = {}
    cachePlannedActionTypesByOrgStructure = {}

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        CActionTypesSelectionManager.__init__(self)
        self.parentWidget = parent
        self.eventEditor  = parent
        self._eventEditorOwner = self

        self.addModels('ActionTypeGroups', CActionTypeModel(self))
        self.addModels('ActionTypes', CActionsModel(self))
        self.addModels('ExistsClientActions', CExistsClientActionsModel(self))
        self.addModels('SelectedActionTypes', CCheckedActionsModel(self, self.modelExistsClientActions))
        self.bntSelectAll = QtGui.QPushButton(u'Выбрать всё', self)
        self.bntSelectAll.setObjectName('bntSelectAll')
        self.bntClearSelection = QtGui.QPushButton(u'Очистить выбор', self)
        self.bntClearSelection.setObjectName('bntClearSelection')

        self.modelActionTypeGroups.setAllSelectable(True)
        self.setupUi(self)

        self.modelActionTypeGroups.setRootItemVisible(True)
        self.modelActionTypeGroups.setLeavesVisible(False)
        self.setModels(self.treeActionTypeGroups, self.modelActionTypeGroups, self.selectionModelActionTypeGroups)
        self.setModels(self.tblActionTypes, self.modelActionTypes, self.selectionModelActionTypes)
        self.setModels(self.tblSelectedActionTypes, self.modelSelectedActionTypes, self.selectionModelSelectedActionTypes)
        self.setModels(self.tblExistsClientActions, self.modelExistsClientActions, self.selectionModelExistsClientActions)
        self.buttonBox.addButton(self.bntSelectAll, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.bntClearSelection, QtGui.QDialogButtonBox.ActionRole)

        self.clientSex = None
        self.clientAge = None
        self.orgStructureId = None
        self.eventId = None
        self.eventTypeId = None
        self.contractId = None
        self.mesId = None
        self.specialityId = None
        self.nomenclativeActionTypes = None
        self.preferableActionTypes = None
        self.allowableActionTypes = None
        self.orgStructureActionTypes = None
        self.plannedActionTypes = None
        self.contractActionTypes = None
        self.enabledActionTypes = None
        self.ksgActionTypes = None
        self.MKBActionTypes = None
        self.execPerson = None
        self.eventSetDate = None
        self.begDate = None
        self.endDate = None
        self.paymentScheme = None
        self.chkDatesState = True
        self.mesActionTypeIdList = []
        self.actionTypeClasses = []
        self.edtFindByCode.installEventFilter(self)
        self.mesActionTypes = None
        self.disabledActionTypeIdList = self.modelActionTypeGroups.getDisabledForProfileActionTypeIdList()
        self.cmbSpeciality.setTable('rbSpeciality')
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.isOrgStructurePriority = None
        self.existsActionTypesList = []
        self.notFilteredActionTypeClasses = []
        self._contractTariffCache = None
        self.goalFilter = False
        self.medicamentList = []
        self.mainActionTypesAnalyses = set(getMainActionTypesAnalyses())

        self.tblSelectedActionTypes.addGetExecutionPlan()
        self.chkUseDates.setEnabled(QtGui.qApp.userHasRight('changeChkServiceDates'))
        self.chkIndications.setVisible(False)
        self.toggleActionSelection =  QtGui.QAction(u'Выбрать действие', self)
        self.toggleActionSelection.setObjectName('toggleActionSelection')
        self.toggleActionSelection.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Space))
        self.addAction(self.toggleActionSelection)
        self.connect(self.toggleActionSelection, QtCore.SIGNAL('triggered()'), self.on_toggleActionSelection_triggered)
        self.connect(self.modelSelectedActionTypes, QtCore.SIGNAL('pricesAndSumsUpdated()'), self.on_pricesAndSumsUpdated)

        if not QtGui.qApp.showFavouriteActionTypesButton():
            self.btnAllActionTypes.setVisible(False)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionTypes_doubleClicked(self, index):
        try:
            actionTypeId = forceRef(self.tblActionTypes.model().getRecordValues(0, index.row())[1][0])
        except:
            actionTypeId = None

        if actionTypeId and not self.isSelected(actionTypeId):
            value = QtCore.Qt.Checked
        else:
            value = QtCore.Qt.Unchecked

        self.tblActionTypes.model().setData(index, value, QtCore.Qt.CheckStateRole)

    def updateSelectedCount(self):
        cnt = len(self.selectedActionTypeIdList)
        if cnt:
            msg = u'выбрано {0}'.format(formatNum(cnt, [u'действие', u'действия', u'действий']))
        else:
            msg = u'ничего не выбрано'
        self.lblSelectedCount.setText(msg)

    def loadPreferences(self, preferences):
        self.btnSearchMode.setChecked(forceBool(getPref(preferences, 'searchmodeforaddactions', QtCore.QVariant())))

        self.chkUseDates.setChecked(forceBool(getPref(preferences, 'chkUseDates', True)))
        self.chkOnlyNotExists.setChecked(forceBool(getPref(preferences, 'chkOnlyNotExists', True)))
        self.chkContract.setChecked(forceBool(getPref(preferences, 'chkContract', False)))
        self.chkPreferable.setChecked(forceBool(getPref(preferences, 'chkPreferable', True)))
        self.chkSexAndAge.setChecked(forceBool(getPref(preferences, 'chkSexAndAge', True)))
        self.chkIndications.setChecked(forceBool(getPref(preferences, 'chkIndications', False)))
        self.chkOrgStructure.setChecked(forceBool(getPref(preferences, 'chkOrgStructure', False)))
        self.chkMKB.setChecked(forceBool(getPref(preferences, 'chkMKB', False)))
        self.chkNomenclative.setChecked(forceBool(getPref(preferences, 'chkNomenclative', False)))
        self.chkMes.setChecked(forceBool(getPref(preferences, 'chkMes', False)))
        self.chkMedicament.setChecked(forceBool(getPref(preferences, 'chkMedicament', False)))
        self.chkNecessity.setChecked(forceBool(getPref(preferences, 'chkNecessity', False)))
        self.chkPlanner.setChecked(forceBool(getPref(preferences, 'chkPlanner', False)))

        if forceBool(getPref(preferences, 'addActionsOnlyFavouriteMode', False)):
            self.on_btnAllActionTypes_clicked()
        CDialogBase.loadPreferences(self, preferences)

    def savePreferences(self):
        result = CDialogBase.savePreferences(self)

        setPref(result, 'chkUseDates', self.chkUseDates.isChecked())
        setPref(result, 'chkOnlyNotExists', self.chkOnlyNotExists.isChecked())
        setPref(result, 'chkContract', self.chkContract.isChecked())
        setPref(result, 'chkPreferable', self.chkPreferable.isChecked())
        setPref(result, 'chkSexAndAge', self.chkSexAndAge.isChecked())
        setPref(result, 'chkIndications', self.chkIndications.isChecked())
        setPref(result, 'chkOrgStructure', self.chkOrgStructure.isChecked())
        setPref(result, 'chkMKB', self.chkMKB.isChecked())
        setPref(result, 'chkNomenclative', self.chkNomenclative.isChecked())
        setPref(result, 'chkMes', self.chkMes.isChecked())
        setPref(result, 'chkMedicament', self.chkMedicament.isChecked())
        setPref(result, 'chkNecessity', self.chkNecessity.isChecked())
        setPref(result, 'chkPlanner', self.chkPlanner.isChecked())

        setPref(result, 'searchmodeforaddactions', self.btnSearchMode.isChecked())
        setPref(result, 'addActionsOnlyFavouriteMode', self.stackedFilters.currentIndex() == self.stackedFilters.indexOf(self.pageFavourites))
        return result

    def on_pricesAndSumsUpdated(self):
        sum = self.modelSelectedActionTypes.getTotalSum()
        text = u'Назначить: %.2f' % sum if sum else u'Назначить'
        self.lblSelected.setText(text)

    def setEventEditorOwner(self, eventEditor):
        if eventEditor:
            self._eventEditorOwner = eventEditor

    def setClientId(self):
        clientId = self.getClientId()
        self.modelSelectedActionTypes.setClientId(clientId)
        self.modelExistsClientActions.setCurrentEventItems(self.getCurrentEventItems())
        self.modelExistsClientActions.setClientId(clientId)

    def getCurrentEventItems(self):
        return self.eventEditorOwner().eventEditor.getActionsModelsItemsList()

    def setContractTariffCache(self, contractTariffCache):
        self._contractTariffCache = contractTariffCache

    def getPrice(self, actionTypeId, contractId, financeId):
        if self._contractTariffCache:
            tariffDescr = self._contractTariffCache.getTariffDescr(contractId, self)
            tariffMap = tariffDescr.actionTariffMap
            serviceIdList = self.getActionTypeServiceIdList(actionTypeId, financeId)
            price = self._contractTariffCache.getPrice(tariffMap, serviceIdList, self.getTariffCategoryId())
            return price
        return None

    def getClientId(self):
        return self.eventEditorOwner().eventEditor.clientId

    def getTariffCategoryId(self):
        return self.eventEditorOwner().eventEditor.personTariffCategoryId

    def getActionTypeServiceIdList(self, actionTypeId, financeId):
        return CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)

    def recordAcceptable(self, record):
        return self.eventEditorOwner().eventEditor.recordAcceptable(record)

    def getSelectedList(self, returnDirtyRows):
        return self.getSelectedActionList(returnDirtyRows)

    def getSelectedAnalyses(self):
        return self._selectedAnalyses

    def getSelectedActionList(self, returnDirtyRows):
        return [(actionTypeId,
                 self.modelSelectedActionTypes.getSelectedAction(actionTypeId, returnDirtyRows))
                for actionTypeId in self.selectedActionTypeIdList]

    def eventEditorOwner(self):
        return self._eventEditorOwner

    def getActionLength(self, record, countRedDays):
        if record:
            startDate = forceDate(record.value('begDate'))
            stopDate  = forceDate(record.value('endDate'))
            if startDate and stopDate:
                return getEventLengthDays(startDate, stopDate, countRedDays,
                                          self.eventEditorOwner().eventEditor.eventTypeId)
        return 0

    def getDefaultAmountEx(self, actionType, record, action):
        return getActionDefaultAmountEx(self, actionType, record, action)

    def getDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId):
        return getActionDefaultContractId(self, actionTypeId, financeId, begDate, endDate, contractId)

    def getComplexActionTypeList(self, actionTypeId):
        db = QtGui.qApp.db
        tableETAction = db.table('EventType_Action')
        tableETA = tableETAction.alias('ETA')
        return db.getIdList(
            tableETAction,
            tableETAction['actionType_id'],
            where=[
                tableETAction['selectionGroup'].eqStmt(
                    db.selectStmt(tableETA,
                                  tableETA['selectionGroup'],
                                  where=[tableETA['actionType_id'].eq(actionTypeId),
                                         tableETA['eventType_id'].eq(tableETAction['eventType_id'])],
                                  limit=1)),
                tableETAction['eventType_id'].eq(self.eventEditor.eventTypeId),
                tableETAction['selectionGroup'].gt(-99),
                tableETAction['selectionGroup'].lt(0),
                tableETAction['actionType_id'].ne(actionTypeId)
            ])

    def getComplexServiceByMesList(self, actionTypeId):
        db = QtGui.qApp.db
        tableMesService = db.table('mes.MES_service')
        tableService = db.table('rbService')
        tableMrbService = db.table('mes.mrbService')
        tableActionType = db.table('ActionType')

        queryTable = tableMesService.innerJoin(tableMrbService, tableMesService['service_id'].eq(tableMrbService['id']))
        queryTable = queryTable.innerJoin(tableService, tableMrbService['code'].eq(tableService['code']))
        queryTable = queryTable.innerJoin(tableActionType, tableService['id'].eq(tableActionType['nomenclativeService_id']))

        return db.getIdList(queryTable,
                            tableActionType['id'],
                            ['''MES_service.selectionGroup = (SELECT ms.selectionGroup
                                                              FROM mes.MES_service ms
                                                              INNER JOIN mes.mrbService rs ON ms.service_id = rs.id
                                                              INNER JOIN rbService s ON s.code = rs.code
                                                              INNER JOIN ActionType at ON at.nomenclativeService_id = s.id
                                                              WHERE at.id = %s AND ms.master_id = MES_service.master_id LIMIT 0, 1)''' % actionTypeId,
                            tableMesService['master_id'].eq(self.eventEditor.getMesId()),
                            tableMesService['selectionGroup'].gt(-99),
                            tableMesService['selectionGroup'].lt(0),
                            tableActionType['id'].ne(actionTypeId),
                            tableMesService['deleted'].eq(0),
                            tableMrbService['deleted'].eq(0),
                            tableActionType['deleted'].eq(0)])

    def addSelection(self, actionTypeId, resetMainModel=False):
        complexActionTypeIdList = (set(self.getComplexActionTypeList(actionTypeId)) |
                                   set(self.getComplexServiceByMesList(actionTypeId))).difference(set(self.existsActionTypesList))
        complexActionTypeIdList = list(complexActionTypeIdList) + [actionTypeId]
        for complexActionTypeId in complexActionTypeIdList:
            self.selectedActionTypeIdList.append(complexActionTypeId)
            self.modelSelectedActionTypes.add(complexActionTypeId, self.getMESqwt(complexActionTypeId), self.getMESNecessity(complexActionTypeId))
            self.updateSelectedCount()
            if resetMainModel:
                self.modelActionTypes.emitDataChanged()

    def addSelectionAnalyses(self, actionTypeId, resetMainModel=False):
        selected = []
        actionType = CActionTypeCache.getById(actionTypeId)
        if actionType.groupId is not None and actionType.groupId not in self.selectedActionTypeIdList:
            selected.append(actionType.groupId)
        selected.append(actionType.id)

        for actionTypeId in selected:
            self.selectedActionTypeIdList.append(actionTypeId)
            self.modelSelectedActionTypes.add(actionTypeId, self.getMESqwt(actionTypeId), self.getMESNecessity(actionTypeId))
            self.updateSelectedCount()
            if resetMainModel:
                self.modelActionTypes.emitDataChanged()

    def removeSelection(self, actionTypeId, resetMainModel=False):
        complexActionTypeIdList = set(self.getComplexActionTypeList(actionTypeId)) | \
                                  set(self.getComplexServiceByMesList(actionTypeId))
        complexActionTypeIdList = list(complexActionTypeIdList) + [actionTypeId]
        for complexActionTypeId in complexActionTypeIdList:
            self.selectedActionTypeIdList.remove(complexActionTypeId)
            self.modelSelectedActionTypes.remove(complexActionTypeId)
        self.updateSelectedCount()
        if resetMainModel:
            self.modelActionTypes.emitDataChanged()

    def removeSelectionAnalyses(self, actionTypeId, resetMainModel=False):
        db = QtGui.qApp.db
        if actionTypeId in self.mainActionTypesAnalyses:
            descendantAnalyses = set(db.getDescendants('ActionType', 'group_id', actionTypeId))
            selectedDescendants = descendantAnalyses.intersection(set(self.selectedActionTypeIdList))
            for typeId in selectedDescendants:
                self.selectedActionTypeIdList.remove(typeId)
                self.modelSelectedActionTypes.remove(typeId)
        else:
            self.selectedActionTypeIdList.remove(actionTypeId)
            self.modelSelectedActionTypes.remove(actionTypeId)

            actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
            mainActionTypeId = actionType.groupId if actionType else None
            if mainActionTypeId:
                descendantAnalyses = set(db.getDescendants('ActionType', 'group_id', mainActionTypeId))
                selectedDescendants = descendantAnalyses.intersection(set(self.selectedActionTypeIdList))
                if not selectedDescendants:
                    self.selectedActionTypeIdList.remove(mainActionTypeId)
                    self.modelSelectedActionTypes.remove(mainActionTypeId)

        self.updateSelectedCount()
        if resetMainModel:
            self.modelActionTypes.emitDataChanged()

    @staticmethod
    def isAnalyses(actionTypeId):
        return forceInt(QtGui.qApp.db.translate('ActionType', 'id', actionTypeId, 'class')) == ActionClass.Analyses

    def setSelected(self, actionTypeId, value, resetMainModel=False):
        selected = self.isSelected(actionTypeId)
        if value:
            if not selected:
                if self.isAnalyses(actionTypeId):
                    self.addSelectionAnalyses(actionTypeId, resetMainModel)
                else:
                    self.addSelection(actionTypeId, resetMainModel)
                return True
        else:
            if selected:
                if self.isAnalyses(actionTypeId):
                    self.removeSelectionAnalyses(actionTypeId, resetMainModel)
                else:
                    self.removeSelection(actionTypeId, resetMainModel)
                return True
        return False

    def emitModelActionTypesDataChanged(self):
        self.modelActionTypes.emitDataChanged()

    def exec_(self):
        self.updateTreeData()
        return CDialogBase.exec_(self)

    def setBlockSignals(self, val):
        widgets = [self.chkOnlyNotExists,
                   self.chkContract,
                   self.chkPreferable,
                   self.chkSexAndAge,
                   self.chkOrgStructure,
                   self.cmbOrgStructure,
                   self.chkNomenclative,
                   self.chkMes,
                   self.chkNecessity,
                   self.chkMedicament,
                   self.chkPlanner,
                   self.cmbSpeciality]
        for w in widgets:
            w.blockSignals(val)

    @classmethod
    def getCachedPlannedActionTypesBySpeciality(cls, specialityId, eventTypeId):
        key = (specialityId, eventTypeId)
        return cls.cachePlannedActionTypesBySpeciality.get(key, None)

    @classmethod
    def setCachedPlannedActionTypesBySpeciality(cls, specialityId, eventTypeId, setIdList):
        key = (specialityId, eventTypeId)
        cls.cachePlannedActionTypesBySpeciality[key] = setIdList

    @classmethod
    def getCachedActionTypesByOrgStructure(cls, orgStructureId):
        return cls.cachePlannedActionTypesByOrgStructure.get(orgStructureId, None)

    @classmethod
    def setCachedActionTypesByOrgStructure(cls, orgStructureId, setIdList):
        cls.cachePlannedActionTypesByOrgStructure[orgStructureId] = setIdList

    def setExistsActionTypes(self, existsActionTypesList):
        self.existsActionTypesList = existsActionTypesList or []

    def setOrgStructurePriority(self, eventTypeId):
        self.isOrgStructurePriority = forceBool(QtGui.qApp.preferences.appPrefs.get('orgStructurePriorityForAddActions', QtCore.QVariant()))
        if not self.isOrgStructurePriority and eventTypeId:
            self.isOrgStructurePriority = CEventTypeDescription.get(eventTypeId).isOrgStructurePriority
            pass

    def setExecPerson(self, execPerson):
        self.execPerson = execPerson

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if obj == self.edtFindByCode:
                if key in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:
                    self.tblActionTypes.keyPressEvent(event)
                    return True
        return False

    def setCmbOrgStructure(self, orgStructureId):
        orgId = QtGui.qApp.currentOrgId()
        if orgId:
            rootOrgStructureId = None
            if QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
                rootOrgStructureId = getTopParentIdForOrgStructure(orgStructureId)
            self.cmbOrgStructure.setOrgId(orgId, rootOrgStructureId)
            if orgStructureId:
                self.cmbOrgStructure.setValue(orgStructureId)
        else:
            self.cmbOrgStructure.setEnabled(False)

    def setActionTypeClasses(self, actionTypeClasses):
        if None in actionTypeClasses:
            actionTypeClasses = ActionClass.All
        self.actionTypeClasses = actionTypeClasses
        self.modelActionTypeGroups.setClasses(actionTypeClasses)
        self.modelActionTypeGroups.setClassesVisible(len(actionTypeClasses) > 1)

    def setNotFilteredClasses(self, actionTypeClasses):
        if not isinstance(actionTypeClasses, list):
            actionTypeClasses = [actionTypeClasses]
        self.notFilteredActionTypeClasses = actionTypeClasses

    def setSexAndAge(self, clientSex, clientAge):
        self.clientSex = clientSex
        self.clientAge = clientAge
        self.chkSexAndAge.setEnabled(bool(self.clientSex and self.clientAge))

    def setMKB(self, MKB):
        self.MKB = MKB
        self.chkMKB.setEnabled(bool(self.MKB) and self.MKB != '')

    def setOrgStructureId(self, orgStructureId):
        if not orgStructureId and not QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
            execPersonId = self.execPerson
            if not execPersonId and self.eventId:
                record = QtGui.qApp.db.getRecord('Event', 'execPerson_id', self.eventId)
                if record:
                    execPersonId = forceRef(record.value('execPerson_id'))
            if execPersonId:
                orgStructureId = forceRef(QtGui.qApp.db.translate('Person', 'id', execPersonId, 'orgStructure_id'))
        self.orgStructureId = orgStructureId
        self.setCmbOrgStructure(orgStructureId)
        if QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
            self.chkOrgStructure.setChecked(bool(self.orgStructureId)
                                            and forceBool(QtGui.qApp.preferences.appPrefs.get('ActionsSelector_chkOrgStructure', True)))
        elif not self.mesId:
            if (bool(QtGui.qApp.currentOrgStructureId()) or bool(orgStructureId)) and not self.chkPlanner.isChecked():
                self.chkOrgStructure.setChecked(bool(self.orgStructureId)
                                                and forceBool(QtGui.qApp.preferences.appPrefs.get('ActionsSelector_chkOrgStructure', True)))

        if not QtGui.qApp.userHasRight('changeStateOrgStructureActionsFilter'):
            self.chkOrgStructure.setEnabled(False)
        else:
            self.chkOrgStructure.setEnabled(bool(QtGui.qApp.currentOrgId()))
        self.cmbOrgStructure.setEnabled(self.chkOrgStructure.isChecked())

    def setEventId(self, eventId):
        self.eventId = eventId

    def setDefaultFinanceId(self, financeId):
        self.modelSelectedActionTypes.defaultFinanceId = financeId

    def setDefaultContractFilterPart(self, filterPart):
        self.modelSelectedActionTypes.defaultContractFilterPart = filterPart

    def getEventTypeId(self):
        return self.eventTypeId

    def setEventTypeId(self, eventTypeId):
        self.eventTypeId = eventTypeId
        self.chkPlanner.setEnabled(bool(self.eventTypeId)
                                   and QtGui.qApp.userHasRight(urDisableCheckActionSpeciality))
        if not self.mesId and not QtGui.qApp.currentOrgStructureId() and not self.isOrgStructurePriority:
            b = bool(self.getPlannedActionTypes())
            self.chkPlanner.setChecked(b)
            self.cmbSpeciality.setEnabled(b)
        self.goalFilter = getEventGoalFilter(eventTypeId)

    def setContractId(self, contractId, chkContractByFinanceId):
        self.contractId = contractId
        enabled = bool(self.contractId)
        self.chkContract.setEnabled(enabled)
        self.chkContract.setChecked(bool(self.contractId and bool(chkContractByFinanceId)))
        self.chkContract.setEnabled(QtGui.qApp.userHasRight('editContractConditionF9') and enabled)

    def getContractId(self):
        return self.contractId

    def setPaymentScheme(self, paymentScheme):
        self.paymentScheme = paymentScheme
        if self.paymentScheme and paymentScheme['paymentScheme']:
            self.chkIndications.setVisible(True)
            self.chkContract.setChecked(True)
            self.chkContract.setVisible(False)
            self.chkOrgStructure.setVisible(False)
            self.cmbOrgStructure.setVisible(False)
            self.chkUseDates.setVisible(False)
            self.chkMedicament.setVisible(False)
            self.chkMes.setVisible(False)
            self.chkNecessity.setVisible(False)
            self.chkNomenclative.setVisible(False)
            self.chkOnlyNotExists.setVisible(False)
            self.chkOnlyNotExists.setChecked(False)
            self.chkPreferable.setVisible(False)
            self.chkSexAndAge.setVisible(False)
            self.edtNecessity.setVisible(False)
            self.btnAmountFromMES.setVisible(False)
            self.chkPlanner.setVisible(False)
            self.cmbSpeciality.setVisible(False)

    def getPaymentScheme(self):
        if self.paymentScheme:
            return self.paymentScheme['paymentScheme']

    def getPaymentSchemeItem(self):
        if self.paymentScheme:
            return self.paymentScheme['item']

    def setPreviousActionTypeIds(self, actionTypeIdList):
        for actionTypeId in actionTypeIdList:
            self.setSelected(actionTypeId, True)

    def setMesId(self, mesId):
        self.mesId = mesId
        self.chkMes.setEnabled(bool(self.mesId))
        self.btnAmountFromMES.setEnabled(bool(self.mesId))
        self.chkNecessity.setEnabled(bool(self.mesId))
        self.chkNecessity.setChecked(bool(self.mesId) and not QtGui.qApp.userHasRight('chkMesNecessityNomenclativeDefault'))
        self.chkMedicament.setEnabled(bool(self.mesId))
        self.chkNomenclative.setChecked(bool(self.mesId) and not QtGui.qApp.userHasRight('chkMesNecessityNomenclativeDefault'))
        self.chkMes.setChecked(bool(self.mesId) and not QtGui.qApp.userHasRight('chkMesNecessityNomenclativeDefault'))
        if self.mesId:
            self.chkDatesState = self.chkUseDates.isChecked()
        self.chkUseDates.setEnabled(QtGui.qApp.userHasRight('changeChkServiceDates') and not bool(self.mesId))
        self.chkUseDates.setChecked(False if bool(self.mesId) else self.chkDatesState)
        self.tblActionTypes.model().setMesId(self.mesId)

    def setBegDate(self, date):
        if date:
            self.eventSetDate = date
            self.begDate = QtGui.qApp.db.formatDate(date)
        else:
            self.eventSetDate = None
            self.begDate = None

    def setEndDate(self, date):
        if date:
            self.endDate = QtGui.qApp.db.formatDate(date)
        else:
            self.endDate = None

    def setShowAmount(self, showAmount):
        if bool(showAmount):
            self.btnAmountFromMES.setChecked(True)

    def setShowMedicaments(self, showMedicaments):
        self.chkMedicament.setEnabled(showMedicaments)
        self.chkMedicament.setVisible(showMedicaments)
        self.chkMedicament.setChecked(showMedicaments)

    def getPreferableActionTypes(self):
        if self.preferableActionTypes is None:
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            idList = QtGui.qApp.db.getIdList(tableActionType, tableActionType['id'], [tableActionType['isPreferable'].ne(0),
                                                                                      tableActionType['deleted'].eq(0)])
            self.preferableActionTypes = set(idList)
        return self.preferableActionTypes

    def getAllowableActionTypes(self):
        if self.allowableActionTypes is None:
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            tableActionTypeService = db.table('ActionType_Service')
            tableServiceGoal = db.table('rbService_Goal')

            queryTable = tableServiceGoal
            queryTable = queryTable.innerJoin(tableActionTypeService, tableActionTypeService['service_id'].eq(tableServiceGoal['master_id']))
            queryTable = queryTable.innerJoin(tableActionType, [tableActionType['id'].eq(tableActionTypeService['master_id']),
                                                                tableActionType['deleted'].eq(0)])
            cond = [
                tableServiceGoal['goal_id'].eq(self.eventEditor.cmbGoal.value()),
                tableServiceGoal['deleted'].eq(0)
            ]

            idList = QtGui.qApp.db.getIdList(queryTable, tableActionType['id'], cond)
            self.allowableActionTypes = set(idList)
        return self.allowableActionTypes

    def getNomenclativeActionTypes(self):
        if self.nomenclativeActionTypes is None:
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            idList = db.getIdList(tableActionType, tableActionType['id'], [tableActionType['nomenclativeService_id'].isNotNull(),
                                                                           tableActionType['deleted'].eq(0)])
            self.nomenclativeActionTypes = set(idList)
        return self.nomenclativeActionTypes

    #TODO: mdldml: этот метод несколько выбивается из остальных (нет кэша); возможно, унифицировать.
    def getFavouriteActionTypes(self):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tablePFAT = db.table('Person_FavouriteActionTypes')
        idList = db.getIdList(
            tableActionType.join(tablePFAT, tableActionType['id'].eq(tablePFAT['actionType_id'])),
            tableActionType['id'],
            [
                tableActionType['deleted'].eq(0),
                tablePFAT['person_id'].eq(QtGui.qApp.userId)
            ]
        )
        return set(idList)

    def getOrgStructureActionTypes(self):
        if self.cmbOrgStructure.isEnabled():
            orgStructureId = self.cmbOrgStructure.value()
        else:
            orgStructureId = self.orgStructureId
        idSet = self.getCachedActionTypesByOrgStructure(orgStructureId)
        if not bool(idSet):
            idSet = getOrgStructureActionTypeIdSet(orgStructureId)
            self.setCachedActionTypesByOrgStructure(orgStructureId, idSet)
        self.orgStructureActionTypes = idSet
        return self.orgStructureActionTypes

    def getActiveActionTypes(self):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tableService = db.table('rbService')
        tableATService = db.table('ActionType_Service')
        cond = [tableActionType['deleted'].eq(0),
                tableActionType['class'].inlist(self.actionTypeClasses)]

        tmpCond = ['0']
        if self.begDate:
            tmpCond.append('rbService.endDate<%s' % self.begDate)
        if self.endDate and self.endDate != '':
            tmpCond.append('rbService.begDate>%s' % self.endDate)

        cond.append('IF(rbService.id IS NULL, 1, NOT (%s))' %db.joinOr(tmpCond))
        queryTable = tableActionType.leftJoin(tableATService, tableATService['master_id'].eq(tableActionType['id']))
        queryTable = queryTable.leftJoin(tableService, 'IF(ActionType_Service.service_id IS NOT NULL, ActionType_Service.service_id, ActionType.nomenclativeService_id)=rbService.id')
        idList= db.getIdList(queryTable, tableActionType['id'],  cond)
        idSet = set(idList)
        return idSet

    def setSpecialityId(self):
        specialityId = QtGui.qApp.userSpecialityId
        if not specialityId:
            execPersonId = self.execPerson
            if not execPersonId and self.eventId:
                record = QtGui.qApp.db.getRecord('Event', 'execPerson_id', self.eventId)
                if record:
                    execPersonId = forceRef(record.value('execPerson_id'))
            if execPersonId:
                specialityId = forceRef(QtGui.qApp.db.translate('Person',
                                                                'id',
                                                                execPersonId,
                                                                'speciality_id'))
        if specialityId:
            self.specialityId = specialityId
            self.cmbSpeciality.setValue(self.specialityId)

    def getPlannedActionTypes(self):
        if self.isOrgStructurePriority:
            return []
        specialityId = self.cmbSpeciality.value()
        setIdList = self.getCachedPlannedActionTypesBySpeciality(specialityId, self.eventTypeId)
        if bool(setIdList):
            self.plannedActionTypes = setIdList
        else:
            db = QtGui.qApp.db
            tableETA = db.table('EventType_Action')
            cond = [
                tableETA['eventType_id'].eq(self.eventTypeId),
                tableETA['actionType_id'].isNotNull()
            ]
            if specialityId:
                cond.append(db.joinOr([tableETA['speciality_id'].eq(specialityId),
                                       tableETA['speciality_id'].isNull()]))
            else:
                cond.append(tableETA['speciality_id'].isNull())
            setIdList = set(db.getIdList(tableETA, tableETA['actionType_id'], cond))
            self.setCachedPlannedActionTypesBySpeciality(specialityId, self.eventTypeId, setIdList)
            self.plannedActionTypes = setIdList
        return self.plannedActionTypes

    def getContractActionTypes(self):
        if self.contractActionTypes is None or self.getPaymentScheme():
            actionTypeIdListByContract = []
            if self.contractId:
                actionTypeIdListByContract.extend(getActionTypeIdListByContract(self.contractId))
            self.contractActionTypes = set(actionTypeIdListByContract)
        return self.contractActionTypes

    def getUniversalContractsActionTypes(self):
        actionTypeIdListByUniversalContract = []
        for universalContract in self.paymentScheme['universalContracts']:
            actionTypeIdListByUniversalContract.extend(getActionTypeIdListByContract(universalContract))
        return set(actionTypeIdListByUniversalContract)

    def getMesActionTypes(self):
        idList = []
        if self.chkNecessity.isChecked():
            necessity = self.edtNecessity.value()
        else:
            necessity = None
        idList += getActionTypeIdListByMesId(self.mesId, necessity, date = self.eventSetDate)
        self.medicamentList = []
        if self.chkMedicament.isChecked():
            self.medicamentList = getMedicamentActionTypeIdListByMesId(self.mesId, necessity)
            if self.medicamentList:
                idList += self.medicamentList
        idSet = set(idList) if idList else set()
        return idSet, idSet

    # TODO:skkachaev: А где её предполагается присваивать? (есть предположение, что это кэш, ниже использовал так, как думаю что должно)
    def getMKBActionTypes(self):
        if self.MKBActionTypes is None:
            self.MKBActionTypes = set(getActionTypeIdListByMKB(self.MKB))
            return self.MKBActionTypes
        else: return self.MKBActionTypes

    def updateTreeData(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        if self.stackedFilters.currentIndex() == self.stackedFilters.indexOf(self.pageFilters):
            sets = []
            mesActionTypeIdList = []
            self.mesActionTypeIdList = []
            if self.chkSexAndAge.isChecked() and self.clientSex and self.clientAge:
                self.modelActionTypeGroups.setFilter(self.clientSex, self.clientAge)
            else:
                self.modelActionTypeGroups.setFilter(0, None)
            if self.chkMes.isChecked() and self.mesId:
                mesActionTypeGroupId, mesActionTypeIdList = self.getMesActionTypes()
                sets.append(mesActionTypeGroupId)
            if self.chkPreferable.isChecked():
                sets.append(self.getPreferableActionTypes())
            if self.chkNomenclative.isChecked():
                sets.append(self.getNomenclativeActionTypes())
            if self.chkOrgStructure.isChecked() and self.orgStructureId:
                sets.append(self.getOrgStructureActionTypes())
            if self.chkPlanner.isChecked() and self.eventTypeId:
                sets.append(self.getPlannedActionTypes())
            if self.chkIndications.isChecked() and self.paymentScheme and self.paymentScheme['universalContracts']:
                sets.append(self.getUniversalContractsActionTypes())
            elif self.chkContract.isChecked() and (self.contractId or self.paymentScheme):
                sets.append(self.getContractActionTypes())
            if self.chkUseDates.isChecked() and (self.begDate or self.endDate):
                sets.append(self.getActiveActionTypes())
            if self.chkMKB.isChecked() and self.MKB and self.MKB != '':
                sets.append(self.getMKBActionTypes())
            if self.goalFilter:
                sets.append(self.getAllowableActionTypes())
            if sets:
                enabledActionTypes = list(reduce(lambda x, y: x&y, sets))
                enabledActionTypes.extend(getActionTypesIdSetByClasses(self.notFilteredActionTypeClasses))
                enabledActionTypes = QtGui.qApp.db.getTheseAndParents('ActionType', 'group_id', enabledActionTypes)
                self.mesActionTypes = self.mesActionTypeIdList = list( set(mesActionTypeIdList) & set(enabledActionTypes) )
            else:
                enabledActionTypes = None
            self.enabledActionTypes = enabledActionTypes
            if self.chkOnlyNotExists.isChecked():
                self.setDisabledActionTypeIdList(list(self.existsActionTypesList))
                if self.chkMes.isChecked():
                    for mesActionTypeId in mesActionTypeIdList:
                        if mesActionTypeId not in self.existsActionTypesList:
                            continue
                        checkMesGroupsHelper = self.tblActionTypes.model().getCheckMesGroupsHelper()
                        mesExistsList = checkMesGroupsHelper.getListByIdOverGroupCodeLimit(mesActionTypeId)
                        for at in mesExistsList:
                            self.disabledActionTypeIdList.append(at.id)
            else:
                self.setDisabledActionTypeIdList(None)
        elif self.stackedFilters.currentIndex() == self.stackedFilters.indexOf(self.pageFavourites):
            self.mesActionTypeIdList = []
            sets = [self.getFavouriteActionTypes()]
            if self.chkContract.isChecked() and (self.contractId or self.paymentScheme):
                sets.append(self.getContractActionTypes())
            if self.chkUseDates.isChecked() and (self.begDate or self.endDate):
                sets.append(self.getActiveActionTypes())
            if self.goalFilter:
                sets.append(self.getAllowableActionTypes())
            self.enabledActionTypes = list(reduce(lambda x, y: x&y, sets))  # self.getFavouriteActionTypes() # enabledActionTypes
            self.setDisabledActionTypeIdList(None)

        index = self.treeActionTypeGroups.currentIndex()
        if index.isValid() and index.internalPointer():
            currentGroupId = index.internalPointer().id()
        else:
            currentGroupId = None
        self.modelActionTypeGroups.setEnabledActionTypeIdList(self.enabledActionTypes)
        self.modelActionTypeGroups.setDisabledActionTypeIdList(self.disabledActionTypeIdList)
        self.treeActionTypeGroups.updateExpandState()
        index = self.modelActionTypeGroups.findItemId(currentGroupId)
        if not index:
            index = self.modelActionTypeGroups.index(0, 0, None)
        self.treeActionTypeGroups.setCurrentIndex(index)
        if not self.enabledActionTypes:
            self.clearGroup()
        QtGui.qApp.restoreOverrideCursor()

    def setDisabledActionTypeIdList(self, lst):
        self.disabledActionTypeIdList = (lst or []) + self.modelActionTypeGroups.getDisabledForProfileActionTypeIdList()

    def setGroupId(self, groupId, _class=None):
        favouritesMode = self.stackedFilters.currentIndex() == self.stackedFilters.indexOf(self.pageFavourites)
        if not self.actionTypeClasses:
            return
        self.actionsCacheByCode.clear()
        self.actionsCacheByName.clear()

        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tableAT = tableActionType.alias('AT')
        tableATS = db.table('ActionType_Service')
        tableService = db.table('rbService')

        cond = [
            tableActionType['class'].inlist(self.actionTypeClasses),
            tableActionType['deleted'].eq(0)
        ]
        if groupId:
            groupIdList = db.getDescendants('ActionType', 'group_id', groupId)
            cond.append(tableActionType['group_id'].inlist(groupIdList))
        if _class is not None:
            cond.append(tableActionType['class'].eq(_class))
        if self.enabledActionTypes is not None:
            cond.append(tableActionType['id'].inlist(self.enabledActionTypes))
        if self.disabledActionTypeIdList:
            cond.append(tableActionType['id'].notInlist(self.disabledActionTypeIdList))

        if self.mesActionTypeIdList:
            #Исключение тех типов действий, которые не содержатся в списке МЕС и при этом являются группой.
            cond.append(db.not_(db.existsStmt(tableAT, [tableActionType['id'].notInlist(filter(bool, self.mesActionTypeIdList)),
                                                        tableAT['group_id'].eq(tableActionType['id'])])))
        else:
            cond.append(db.not_(db.existsStmt(tableAT, [tableAT['group_id'].eq(tableActionType['id']),
                                                        tableAT['deleted'].eq(0)])))

        cols = [
            tableActionType['id'],
            tableActionType['code'],
            tableActionType['name'],
            tableActionType['age'],
            tableActionType['sex']
        ]
        order = [
            tableActionType['code'],
            tableActionType['name']
        ]

        if self.chkUseDates.isChecked():
            tmpCond = ['0']
            if self.begDate:
                tmpCond.append('rbService.endDate<%s' % self.begDate)
            if self.endDate:
                tmpCond.append('rbService.begDate>%s' % self.endDate)

            cond.append('IF(rbService.id IS NULL, 1, %s)' % db.not_(db.joinOr(tmpCond)))

            queryTable = tableActionType.leftJoin(tableATS, tableATS['master_id'].eq(tableActionType['id']))
            queryTable = queryTable.leftJoin(tableService, tableService['id'].eq(db.if_(tableATS['service_id'].isNotNull(),
                                                                                        tableATS['service_id'],
                                                                                        tableActionType['nomenclativeService_id'])))
            recordList = QtGui.qApp.db.getRecordList(queryTable, cols, cond, order)
        else:
            recordList = QtGui.qApp.db.getRecordList(tableActionType, cols, cond, order)

        if recordList:
            idList = []
            for record in recordList:
                if self.chkSexAndAge.isChecked() and not recordAcceptable(self.clientSex, self.clientAge, record) and not favouritesMode:
                    continue
                id = forceRef(record.value('id'))
                code = forceString(record.value('code')).upper()
                name = forceString(record.value('name')).upper()
                if not id in idList:
                    idList.append(id)

                existCode = self.actionsCacheByCode.get(code, None)
                while existCode is not None:
                    code += ' '
                    existCode = self.actionsCacheByCode.get(code, None)
                self.actionsCacheByCode[code] = len(idList) - 1

                existName = self.actionsCacheByName.get(name, None)
                while existName is not None:
                    name += ' '
                    existName = self.actionsCacheByName.get(name, None)
                self.actionsCacheByName[name] = len(idList) - 1
        else:
            idList = []
        self.actionTypeIdList = idList
        self.tblActionTypes.setIdList(idList)
        self.tblActionTypes.model().updateFavourites()

    def clearGroup(self):
        self.tblActionTypes.setIdList([])

    def invalidateChecks(self):
        model = self.modelActionTypes
        lt = model.index(0, 0)
        rb = model.index(model.rowCount()-1, 1)
        model.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), lt, rb)

    def rebuildActionTypes(self, force=False):
        if not self.modelActionTypes.idList() or force:
            index = self.treeActionTypeGroups.currentIndex()
            self.on_selectionModelActionTypeGroups_currentChanged(index, index)

    def getMESNecessity(self, actionTypeId):
        if self.mesActionTypes and self.chkMes.isChecked():
            record = None
            if actionTypeId in self.mesActionTypes:
                code = forceString(QtGui.qApp.db.translate('ActionType', 'id', actionTypeId, 'code'))
                record = getMesServiceInfo(code, self.mesId, self.getNecessityFilter()  )
            if record:
                return forceString(record.value('necessity'))
        return None

    def getMESqwt(self, actionTypeId):
        if self.mesActionTypes and self.chkMes.isChecked() and self.btnAmountFromMES.isChecked():
            if actionTypeId in self.mesActionTypes:
                code = forceString(QtGui.qApp.db.translate('ActionType', 'id', actionTypeId, 'code'))
                record = getMesServiceInfo(code, self.mesId, self.getNecessityFilter())
                if record:
                    return forceInt(record.value('averageQnt'))
        return None

    def accept(self):
        QtGui.qApp.preferences.appPrefs['ActionsSelector_chkOrgStructure'] = self.chkOrgStructure.isChecked()
        CDialogBase.accept(self)

    def getNecessityFilter(self):
        if self.chkNecessity.isChecked():
            return forceDouble(self.edtNecessity.value())
        return None

    @QtCore.pyqtSlot(bool)
    def on_chkOnlyNotExists_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkSexAndAge_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkPreferable_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkNomenclative_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkPlanner_toggled(self, value):
        self.isOrgStructurePriority = not value
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkContract_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkMKB_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkMes_toggled(self, value):
        self.tblActionTypes.model().setCheckMesGroups(value)
        if value:
            self.chkDatesState = self.chkUseDates.isChecked()
        self.chkUseDates.setEnabled(QtGui.qApp.userHasRight('changeChkServiceDates') and not value)
        self.chkUseDates.setChecked(False if value else self.chkDatesState)
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkUseDates_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkMedicament_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkNecessity_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(bool)
    def on_chkIndications_toggled(self, value):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionTypeGroups_currentChanged(self, current, previous):
        if current.isValid() and current.internalPointer():
            actionTypeId = current.internalPointer().id()
            _class = current.internalPointer().class_()
        else:
            actionTypeId = None
            _class = None
        self.setGroupId(actionTypeId, _class)
        text = forceStringEx(self.edtFindByCode.text())
        if text:
            self.on_edtFindByCode_textChanged(text)

    @QtCore.pyqtSlot()
    def on_bntSelectAll_pressed(self):
        notSelected = [] #Список невыбираемых типов действий
        chkMes = self.chkMes.isChecked() # Опция "МЭС"
        #Для каждого типа действия из списка типов действий окна
        for actionTypeId in self.modelActionTypes.idList():
            if chkMes:
                #Если текущий тип действия отсутствует в списке невыбираемых
                if not actionTypeId in notSelected:
                    #Создать помошник проверки по МЭСам
                    checkMesGroupsHelper = self.tblActionTypes.model().getCheckMesGroupsHelper()
                    #Получить список всех типов действия с тем же кодом группировки по мес, что и у текущего типа (если этот код больше limit = 0)
                    mesExistsList = checkMesGroupsHelper.getListByIdOverGroupCodeLimit(actionTypeId)
                    #Сформировать список ID типов действия с тем же кодом
                    mesExistsListId = [at.id for at in mesExistsList]
                    #Если текущий тип действий есть среди списка с таким же кодом группы (Atronah: имхо, всегда будет True, если список mesExists не пуст)
                    if actionTypeId in mesExistsListId:
                        mesExistsListId.pop(mesExistsListId.index(actionTypeId))
                        #Пополнить список невыбираемых типов списком без учета текущего
                        notSelected += mesExistsListId
            if not actionTypeId in notSelected:
                self.setSelected(actionTypeId, True)
            else:
                if chkMes:
                    self.setSelected(actionTypeId, False)
        self.invalidateChecks()

    @QtCore.pyqtSlot()
    def on_bntClearSelection_pressed(self):
        self.selectedActionTypeIdList = []
        self.updateSelectedCount()
        self.invalidateChecks()
        self.modelSelectedActionTypes.removeAll()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFindByCode_textChanged(self, text):
        text = unicode(text).strip()
        if text:
            if self.btnSearchMode.isChecked():
                idList = self.findByName(text)
            else:
                idList = self.findByCode(text)
            self.tblActionTypes.setIdList(idList)
        else:
            self.tblActionTypes.setIdList(self.actionTypeIdList)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtNecessity_valueChanged(self, val):
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionTypes_currentChanged(self, current, previous):
        if self.mesActionTypes:
            id = self.tblActionTypes.currentItemId()
            if id and id in self.mesActionTypes:
                item = self.tblActionTypes.currentItem()
                code = forceString(item.value('code'))
                record = getMesServiceInfo(code, self.mesId, self.getNecessityFilter())
                if record:
                    averageQnt = forceInt(record.value('averageQnt'))
                    necessity = forceDouble(record.value('necessity'))
                    doctorWTU = forceDouble(record.value('doctorWTU'))
                    paramedicalWTU = forceDouble(record.value('paramedicalWTU'))
                    text = u'СК: %d; ЧП: %.1f; УЕТвр: %.1f; УЕТср: %.1f' % (averageQnt,
                                                                            necessity,
                                                                            doctorWTU,
                                                                            paramedicalWTU)
                    self.lblMesInfo.setText(text)
                    return
        self.lblMesInfo.clear()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExistsClientActions_doubleClicked(self, index):
        actionRecord = self.tblExistsClientActions.currentItem()
        dialog = CActionEditDialog(self)

        # бред полнейший. Надо как-то подругому
        dialog.save = lambda: True

        # в случае нового действия не определить clientId. Нет Action.event_id.
        dialog.setForceClientId(self.getClientId())

        dialog.setRecord(actionRecord)
        if dialog.exec_():
            model = self.modelExistsClientActions
            actionRecord = dialog.getRecord()
            actionId = forceRef(actionRecord.value('id'))
            if actionId and not model.isCurrentEventActionId(actionId):
                QtGui.qApp.db.updateRecord('Action', actionRecord)
            model.updateRecord(index.row(), actionRecord)

    @QtCore.pyqtSlot(bool)
    def on_btnSearchMode_toggled(self, state):
        if state:
            self.btnSearchMode.setText(u'наименованию')
        else:
            self.btnSearchMode.setText(u'коду')
        text = self.edtFindByCode.text()
        self.on_edtFindByCode_textChanged(text)
        self.edtFindByCode.setFocus()

    @QtCore.pyqtSlot()
    def on_btnAllActionTypes_clicked(self):
        self.chkUseDates.setChecked(True)
        self.stackedFilters.setCurrentIndex(self.stackedFilters.indexOf(self.pageFavourites))
        self.btnFavouriteActionTypes.setMaximumWidth(self.btnAllActionTypes.width())
        self.btnFavouriteActionTypes.setMinimumWidth(self.btnAllActionTypes.width())
        self.updateTreeData()
        self.rebuildActionTypes()

    @QtCore.pyqtSlot()
    def on_btnFavouriteActionTypes_clicked(self):
        self.stackedFilters.setCurrentIndex(self.stackedFilters.indexOf(self.pageFilters))
        self.updateTreeData()
        self.rebuildActionTypes()

    def on_toggleActionSelection_triggered(self):
        index = self.tblActionTypes.currentIndex()
        currentValue = forceInt(self.modelActionTypes.data(
            self.modelActionTypes.createIndex(index.row(), 0),
            QtCore.Qt.CheckStateRole))
        value = 2 if currentValue == 0 else 0
        if self.modelActionTypes.setData(index, value, QtCore.Qt.CheckStateRole):
            self.edtFindByCode.selectAll()
        self.tblActionTypes.model().emitDataChanged()


class CCheckMesGroupsHelper(object):
    def __init__(self, mesId=None):
        self.mesId = mesId
        self.dictById = {}
        self.dictByGroupCode = defaultdict(list)

    def setMesId(self, mesId):
        if mesId != self.mesId:
            self.mesId = mesId
            self.loadActionTypes()

    def loadActionTypes(self):
        # TODO: craz: check MES_service dates.
        self.dictById.clear()
        self.dictByGroupCode.clear()
        if not self.mesId:
            return

        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tableMesService = db.table('mes.MES_service')
        tableMRBService = db.table('mes.mrbService')
        tableService = db.table('rbService')

        table = tableMesService.leftJoin(tableMRBService, tableMRBService['id'].eq(tableMesService['service_id']))
        table = table.leftJoin(tableService, tableService['code'].eq(tableMRBService['code']))
        table = table.leftJoin(tableActionType, tableActionType['nomenclativeService_id'].eq(tableService['id']))
        cond = [
            tableMesService['master_id'].eq(self.mesId),
            tableMesService['deleted'].eq(0),
            tableMRBService['deleted'].eq(0),
            tableActionType['deleted'].eq(0)
        ]
        cols = [
            tableActionType['id'].alias('id'),
            tableActionType['code'].alias('code'),
            tableMesService['groupCode'].alias('groupCode')
        ]
        group = [
            tableActionType['code']
        ]
        order = [
            tableMesService['groupCode'],
            tableActionType['code'],
            tableMRBService['name'],
            tableMRBService['id']
        ]
        for record in db.iterRecordList(table, cols, cond, group=group, order=order):
            at = smartDict()
            at.id = forceRef(record.value('id'))
            at.code = forceString(record.value('code'))
            at.groupCode = forceInt(record.value('groupCode'))
            self.dictById[at.id] = at
            self.dictByGroupCode[at.groupCode].append(at)

    def getById(self, id):
        return self.dictById.get(id, None)

    def getListByGroupCode(self, groupCode):
        return self.dictByGroupCode.get(groupCode, [])

    def getListById(self, id):
        at = self.getById(id)
        if at:
            return self.getListByGroupCode(at.groupCode)
        return []

    def getListByIdOverGroupCodeLimit(self, id, limit=0):
        at = self.getById(id)
        if at:
            if at.groupCode > limit:
                return self.getListByGroupCode(at.groupCode)
        return []


#TODO hide column necessity if MES is not selected

class CActionsModel(CTableModel):
    def __init__(self, parent):
        cols = [
            CEnableCol(u'Включить', ['id'], 20, parent),
            CTextCol(u'Код', ['code'], 20),
            CTextCol(u'Наименование', ['name'], 20),
            CCodeCol(u'ЧП', ['code'], 10, parent)
        ]

        self.initModel(parent, cols)
        self._isEditable = True

    def initModel(self, parent, cols):
        self.parentWidget = parent
        self.checkMesGroupsHelper = CCheckMesGroupsHelper()
        self.checkMesGroups = False
        self.favouritesSet = set()
        CTableModel.__init__(self, parent, cols, 'ActionType')

    def setCheckMesGroups(self, val):
        self.checkMesGroups = val

    def getCheckMesGroupsHelper(self):
        return self.checkMesGroupsHelper

    def setMesId(self, mesId):
        self.checkMesGroupsHelper.setMesId(mesId)
        self.setCheckMesGroups(bool(mesId))

    def setEditable(self, value):
        self._isEditable = value

    def getEditable(self):
        return self._isEditable

    def flags(self, index):
        result = CTableModel.flags(self, index)
        if self.getEditable():
            result |= QtCore.Qt.ItemIsUserCheckable
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            row = index.row()
            id = self._idList[row]
            if self.checkMesGroups and forceInt(value) == QtCore.Qt.Checked:
                actionTypeGroupCodeList = self.checkMesGroupsHelper.getListByIdOverGroupCodeLimit(id)
                for at in actionTypeGroupCodeList:
                    if at.id != id:
                        self.parentWidget.setSelected(at.id, False)
            self.parentWidget.setSelected(self._idList[row], forceInt(value) == QtCore.Qt.Checked)
            self.emitDataChanged()
            return True
        return False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.FontRole:
            recordExists = forceInt(self.getRecordByRow(index.row()).value('id')) in self.favouritesSet
            showFavourites = QtGui.qApp.showFavouriteActionTypesButton()
            if recordExists and showFavourites:
                font = QtGui.QFont()
                font.setBold(True)
                return toVariant(font)
        return CTableModel.data(self, index, role)

    def updateFavourites(self):
        db = QtGui.qApp.db
        tablePFAT = db.table('Person_FavouriteActionTypes')
        self.favouritesSet = set(db.getIdList(tablePFAT, idCol='actionType_id', where=db.joinAnd([tablePFAT['actionType_id'].inlist(self.idList()), tablePFAT['person_id'].eq(QtGui.qApp.userId)])))


class CEnableCol(CBoolCol):
    def __init__(self, title, fields, defaultWidth, selector):
        CBoolCol.__init__(self, title, fields, defaultWidth)
        self.selector = selector

    def checked(self, values):
        actionTypeId = forceRef(values[0])
        if self.selector.isSelected(actionTypeId):
            return CBoolCol.valChecked
        else:
            return CBoolCol.valUnchecked


class CCodeCol(CTextCol):
    def __init__(self, title, fields, defaultWidth, parent):
        CTextCol.__init__(self, title, fields, defaultWidth)
        self.parent = parent

    def load(self, code):
        record = getMesServiceInfo(forceString(code), self.parent.mesId, self.parent.getNecessityFilter())
        self.putIntoCache(code, forceString(record.value('necessity')) if record else '')

    # def format(self, values):
    #     record = getMesServiceInfo(forceString(values[0]), self.parent.mesId, self.parent.getNecessityFilter())
    #     return record.value('necessity') if record else None


class CExistsClientActionsModel(CTableModel):
    actionTypeNameColIndex = 4

    def __init__(self, parent):
        cols = [CDateCol(u'Назначено', ['directionDate'], 10),
                CDateCol(u'Начато', ['begDate'], 10),
                CEnumCol(u'Статус', ['status'], CActionType.retranslateClass(False).statusNames, 10),
                CDateCol(u'План', ['plannedEndDate'], 10),
                CRefBookCol(u'Действие', ['actionType_id'], 'ActionType', 20, showFields=2),
                CRefBookCol(u'Назначил', ['setPerson_id'], 'vrbPersonWithSpeciality', 25)]
        CTableModel.__init__(self, parent, cols)
        self.loadField('*')
        self.setTable('Action', recordCacheCapacity=None)
        self._currentEventItems = {}
        self._currentEventItemsIdList = []
        self._currentEventItemsFakeIdList = []
        self._actionTypeIdList = []

    def setClientId(self, clientId):
        db =  QtGui.qApp.db

        tableAction = self._table
        tableEvent  = db.table('Event')

        queryTable = tableAction.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))

        plannedEndDateCond = [tableAction['plannedEndDate'].dateGe(QtCore.QDate.currentDate()),
                              'DATE(Action.`plannedEndDate`)=\'0000-00-00\'']

        cond = [tableAction['deleted'].eq(0),
                tableAction['status'].inlist([ActionStatus.Started,
                                              ActionStatus.Appointed]),
                db.joinOr(plannedEndDateCond),
                tableEvent['client_id'].eq(clientId),
                tableEvent['deleted'].eq(0)]
        if self._currentEventItemsIdList:
            cond.append(tableAction['id'].notInlist(self._currentEventItemsIdList))

        idList = []
        for record in db.iterRecordList(queryTable, tableAction['*'], cond):
            actionId = forceRef(record.value('id'))
            actionTypeId = forceRef(record.value('actionType_id'))
            actionClass = forceInt(record.value('class'))
            if actionClass != 4:
                continue
            if not actionTypeId in self._actionTypeIdList:
                self._actionTypeIdList.append(actionTypeId)
            actionType = CActionTypeCache.getById(actionTypeId)
            actualAppointmentDuration = actionType.actualAppointmentDuration
            if self.isValidRecord(record, actualAppointmentDuration):
                idList.append(actionId)

        self.setIdList(self._currentEventItemsFakeIdList+idList)
        for fakeId, item in self._currentEventItems.items():
            record, action = item
            self.recordCache().put(fakeId, record)

    def setCurrentEventItems(self, items):
        self._currentEventItemsFakeIdList = []
        self._currentEventItemsIdList = []
        self._actionTypeIdList = []
        self._currentEventItems.clear()
        for idx, item in enumerate(items):
            record, action = item
            actionType = action.getType()
            actualAppointmentDuration = actionType.actualAppointmentDuration
            if self.isValidRecord(record, actualAppointmentDuration) and action.getType().class_ == 4:
                fakeId = str(idx)
                self._currentEventItems[fakeId] = item
                self._currentEventItemsFakeIdList.append(fakeId)
                realId = forceRef(record.value('id'))
                if realId:
                    self._currentEventItemsIdList.append(realId)
                self._actionTypeIdList.append(forceRef(record.value('actionType_id')))

    def isValidRecord(self, record, actualAppointmentDuration):
        status = forceInt(record.value('status'))
        plannedEndDate = forceDate(record.value('plannedEndDate'))
        currentDate = QtCore.QDate.currentDate()
        if status in [ActionStatus.Started, ActionStatus.Appointed]:
            if plannedEndDate.isValid() and plannedEndDate >= currentDate:
                return True
            else:
                if actualAppointmentDuration:
                    directionDate = forceDate(record.value('directionDate'))
                    return directionDate.addDays(actualAppointmentDuration-1) >= currentDate
                else:
                    return True

        return False

    def isCurrentEventActionId(self, actionId):
        return actionId in self._currentEventItemsIdList

    def hasActionTypeId(self, actionTypeId):
        return actionTypeId in self._actionTypeIdList

    def updateRecord(self, row, record):
        id = self._idList[row]
        self.recordCache().put(id, record)
        if id in self._currentEventItemsFakeIdList:
            actionRecord, action = self._currentEventItems[id]
            self.syncRecords(record, actionRecord)
        self.emitDataChanged()

    def syncRecords(self, sourceRecord, targetRecord):
        for fieldIdx in xrange(sourceRecord.count()):
            fieldName = sourceRecord.fieldName(fieldIdx)
            targetRecord.setValue(fieldName, sourceRecord.value(fieldName))

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        column = index.column()
        if role == QtCore.Qt.DisplayRole and column == CExistsClientActionsModel.actionTypeNameColIndex:
            row = index.row()
            actionId = self.idList()[row]
            record = self.recordCache().get(actionId)
            actionTypeId = forceRef(record.value('actionType_id'))
            if actionTypeId:
                outName = forceString(record.value('specifiedName'))
                actionType = CActionTypeCache.getById(actionTypeId)
                if actionType:
                    actionTypeName = u' | '.join([actionType.code, actionType.name])
                    outName = actionTypeName + ' ' + outName if outName else actionTypeName
                return QtCore.QVariant(outName)

        return CTableModel.data(self, index, role)
