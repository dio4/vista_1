# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

"""
F025 planner
"""
from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import CActionTypeCache
from Events.ActionInfo import CActionTypeInfo
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import CFinanceType, recordAcceptable, getEventName, getEventShowActionsInPlanner, \
    getEventCanHavePayableActions, getEventFinanceCode
from Orgs.OrgComboBox import CPolyclinicExtendedInDocTableCol
from Orgs.PersonInfo import CPersonInfo
from Registry.Utils import CClientInfo
from Ui_PreF025 import Ui_PreF025Dialog
from library.DialogBase import CDialogBase
from library.InDocTable import CInDocTableModel, CInDocTableCol, CBoolInDocTableCol, CFloatInDocTableCol, \
    CIntInDocTableCol, CRBInDocTableCol
from library.PrintInfo import CInfoContext, CDateInfo
from library.PrintTemplates import applyTemplate, getPrintButton
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, toVariant, \
    calcAgeTuple, formatName, formatSex
from library.crbcombobox import CRBComboBox


class CPreF025DagnosticAndActionPresets:
    def __init__(self, clientId, eventTypeId, eventDate, specialityId, flagHospitalization, addActionTypeId,
                 recommendationList, useDiagnosticsAndActionsPresets=True):
        self.useDiagnosticsAndActionsPresets = useDiagnosticsAndActionsPresets
        self.unconditionalDiagnosticList = []
        self.unconditionalActionList = []
        self.disabledActionTypeIdList = []
        if recommendationList is None:
            recommendationList = []
        self.notDeletedActionTypes = {}
        self.setClientInfo(clientId, eventDate)
        self.setEventTypeId(eventTypeId, specialityId, flagHospitalization, addActionTypeId, recommendationList,
                            useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)

    def setClientInfo(self, clientId, eventDate):
        self.clientId = clientId
        self.eventDate = eventDate
        db = QtGui.qApp.db
        table = db.table('Client')
        record = db.getRecord(table, 'sex, birthDate', clientId)
        if record:
            self.clientSex = forceInt(record.value('sex'))
            self.clientBirthDate = forceDate(record.value('birthDate'))
            self.clientAge = calcAgeTuple(self.clientBirthDate, eventDate)
            if not self.clientAge:
                self.clientAge = (0, 0, 0, 0)

    def setEventTypeId(self, eventTypeId, specialityId, flagHospitalization, addActionTypeId, recommendationList,
                       useDiagnosticsAndActionsPresets=True):
        self.eventTypeId = eventTypeId
        if useDiagnosticsAndActionsPresets and self.useDiagnosticsAndActionsPresets:
            self.prepareDiagnositics(eventTypeId, specialityId)
            self.prepareActions(eventTypeId, specialityId, flagHospitalization, addActionTypeId, recommendationList)

    def prepareDiagnositics(self, eventTypeId, specialityId):
        db = QtGui.qApp.db
        table = db.table('EventType_Diagnostic')
        cond = [table['eventType_id'].eq(eventTypeId)]
        if specialityId:
            cond.append(db.joinOr([table['speciality_id'].eq(specialityId), table['speciality_id'].isNull()]))
        records = QtGui.qApp.db.getRecordList(table, '*', cond, 'idx, id')
        for record in records:
            selectionGroup = forceInt(record.value('selectionGroup'))
            if selectionGroup == 1 and self.recordAcceptable(record):
                MKB = forceString(record.value('defaultMKB'))
                dispanserId = forceRef(record.value('defaultDispanser_id'))
                healthGroupId = forceRef(record.value('defaultHealthGroup_id'))
                medicalGroupId = forceRef(record.value('defaultMedicalGroup_id'))
                visitTypeId = forceRef(record.value('visitType_id'))
                goalId = forceRef(record.value('defaultGoal_id'))
                serviceId = forceRef(record.value('service_id'))
                self.unconditionalDiagnosticList.append(
                    (MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId))

    def prepareActions(self, eventTypeId, specialityId, flagHospitalization, addActionTypeId, recommendationList):
        wholeEventForCash = getEventFinanceCode(eventTypeId) == 4
        db = QtGui.qApp.db
        table = db.table('EventType_Action')
        tableActionType = db.table('ActionType')
        self.disabledActionTypeIdList = []
        self.notDeletedActionTypes = {}
        join = table.leftJoin(tableActionType, tableActionType['id'].eq(table['actionType_id']))
        cond = [table['eventType_id'].eq(eventTypeId), tableActionType['deleted'].eq(0)]
        if specialityId:
            cond.append(db.joinOr( [ table['speciality_id'].eq(specialityId),  table['speciality_id'].isNull()] ))
        records = QtGui.qApp.db.getRecordList(join, 'EventType_Action.*, CONCAT_WS(\'|\', ActionType.code, ActionType.name) AS actionTypeName', cond, 'ActionType.class, idx, id')
        for record in records:
            actionTypeId = forceRef(record.value('actionType_id'))
            if actionTypeId and self.recordAcceptable(record):
                selectionGroup = forceInt(record.value('selectionGroup'))
                notDeleted = forceInt(record.value('isCompulsory'))
                if selectionGroup == -99:
                    self.disabledActionTypeIdList.append(actionTypeId)
                elif selectionGroup == 1 or flagHospitalization and addActionTypeId == actionTypeId:
                    payable = forceInt(record.value('payable'))
                    orgId = forceRef(record.value('defaultOrg_id'))
                    self.unconditionalActionList.append((actionTypeId, 1.0, payable or wholeEventForCash, orgId))
                    if notDeleted == 1:
                        self.notDeletedActionTypes[actionTypeId] = forceString(record.value('actionTypeName'))

        actionTypeIdRecMap = {}
        for rec in recommendationList:
            actionTypeIdRecMap[forceInt(rec.value('actionType_id'))] = rec
        records = db.getRecordList(tableActionType, where=tableActionType['id'].inlist(actionTypeIdRecMap))
        for record in records:
            actionTypeId = forceInt(record.value('id'))
            orgId = forceRef(record.value('defaultOrg_id'))
            amount = forceInt(actionTypeIdRecMap[actionTypeId].value('amount'))
            self.unconditionalActionList.append((actionTypeId, amount, False, orgId))

    def recordAcceptable(self, record):
        return recordAcceptable(self.clientSex, self.clientAge, record)


class CPreF025Dialog(CDialogBase, Ui_PreF025Dialog):
    def __init__(self, parent, contractTariffCache=None):
        CDialogBase.__init__(self, parent)
        self.addModels('Diagnostics', CDiagnosticsModel(self))
        self.addModels('Actions', CActionsModel(self))
        self.btnPrint = getPrintButton(self, 'planner')
        self.btnPrint.setObjectName('btnPrint')

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Планирование осмотра Ф.025')
        self.clientId = None
        self.clientName = None
        self.clientSex = None
        self.clientBirthDate = None
        self.clientAge = None
        self.eventTypeId = None
        self.eventDate = None
        self.contractId = None
        self.financeId = None
        self.tariffCategoryId = None
        self.personId = None
        self.showPrice = False
        self.tissueTypeId = None
        self.contractTariffCache = contractTariffCache
        self.tblDiagnostics.setModel(self.modelDiagnostics)
        self.tblDiagnostics.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblDiagnostics.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblActions.setModel(self.modelActions)
        self.tblActions.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblActions.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.unconditionalDiagnosticList = []
        self.disabledActionTypeIdList = []
        self.unconditional_actionTypes_list = []
        self.notDeletedActionTypes = {}
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.tblDiagnostics.installEventFilter(self)
        self.tblActions.installEventFilter(self)

    def prepare(self, clientId, eventTypeId, eventDate, personId, specialityId, tariffCategoryId,
                flagHospitalization=False, addActionTypeId=None, tissueTypeId=None, recommendationList=None,
                useDiagnosticsAndActionsPresets=True):
        if recommendationList is None:
            recommendationList = []
        self.showPrice = getEventCanHavePayableActions(eventTypeId)
        self.wholeEventForCash = getEventFinanceCode(eventTypeId) == 4
        self.personId = personId
        self.setClientInfo(clientId, eventDate)
        self.tissueTypeId = tissueTypeId
        if self.showPrice:
            self.modelDiagnostics.addPriceAndSumColumn()
            self.modelActions.addPriceAndSumColumn()
            self.setDefaultCash()
            self.grpContract.setVisible(True)
            self.tariffCategoryId = tariffCategoryId
            self.setEventTypeId(eventTypeId, specialityId, flagHospitalization, addActionTypeId, recommendationList)
            orgId = QtGui.qApp.currentOrgId()
            self.cmbContract.setOrgId(orgId)
            self.cmbContract.setClientInfo(clientId, self.clientSex, self.clientAge, None, None)
            self.cmbContract.setFinanceId(CFinanceType.getId(CFinanceType.cash))
            self.cmbContract.setBegDate(eventDate)
            self.cmbContract.setEndDate(eventDate)
        else:
            self.grpContract.setVisible(False)
            self.setEventTypeId(eventTypeId, specialityId, flagHospitalization, addActionTypeId, recommendationList,
                                useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)

    def setClientInfo(self, clientId, eventDate):
        self.clientId = clientId
        self.eventDate = eventDate
        db = QtGui.qApp.db
        table = db.table('Client')
        record = db.getRecord(table, 'lastName, firstName, patrName, sex, birthDate', clientId)
        if record:
            lastName = record.value('lastName')
            firstName = record.value('firstName')
            partName = record.value('patrName')
            self.clientName = formatName(lastName, firstName, partName)
            self.clientSex = forceInt(record.value('sex'))
            self.clientBirthDate = forceDate(record.value('birthDate'))
            self.clientAge = calcAgeTuple(self.clientBirthDate, eventDate)
            if not self.clientAge:
                self.clientAge = (0, 0, 0, 0)

    def setEventTypeId(self, eventTypeId, specialityId, flagHospitalization, addActionTypeId, recommendationList,
                       useDiagnosticsAndActionsPresets=True):
        self.eventTypeId = eventTypeId
        eventTypeName = getEventName(eventTypeId)
        showFlags = getEventShowActionsInPlanner(eventTypeId)
        title = u' Планирование: %s, Пациент: %s, Пол: %s, ДР.: %s '% (eventTypeName, self.clientName, formatSex(self.clientSex),
                                                                      forceString(self.clientBirthDate))
        QtGui.QDialog.setWindowTitle(self, title)
        if useDiagnosticsAndActionsPresets:
            self.prepareDiagnositics(eventTypeId, specialityId)
            self.prepareActions(eventTypeId, specialityId, showFlags, flagHospitalization, addActionTypeId,
                                recommendationList)

    def prepareDiagnositics(self, eventTypeId, specialityId):
        includedGroups = set()
        db = QtGui.qApp.db
        table = db.table('EventType_Diagnostic')
        cond = [table['eventType_id'].eq(eventTypeId)]
        if specialityId:
            cond.append(db.joinOr([table['selectionGroup'].eq(0), table['speciality_id'].eq(specialityId),
                                   table['speciality_id'].isNull()]))
        records = QtGui.qApp.db.getRecordList(table, '*', cond, 'idx, id')
        for record in records:
            if self.recordAcceptable(record):
                recSpecialityId = forceRef(record.value('speciality_id'))
                MKB = forceString(record.value('defaultMKB'))
                dispanserId = forceRef(record.value('defaultDispanser_id'))
                healthGroupId = forceRef(record.value('defaultHealthGroup_id'))
                medicalGroupId = forceRef(record.value('defaultMedicalGroup_id'))
                visitTypeId = forceRef(record.value('visitType_id'))
                selectionGroup = forceInt(record.value('selectionGroup'))
                defaultGoalId = forceRef(record.value('defaultGoal_id'))
                serviceId = forceRef(record.value('service_id'))
                if selectionGroup == 1:
                    self.unconditionalDiagnosticList.append((MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, defaultGoalId, serviceId))
                else:
                    item = self.modelDiagnostics.getEmptyRecord()
                    item.setValue('speciality_id', toVariant(recSpecialityId))
                    item.setValue('defaultMKB', toVariant(MKB))
                    item.setValue('defaultDispanser_id', toVariant(dispanserId))
                    item.setValue('defaulthealthGroup_id', toVariant(healthGroupId))
                    item.setValue('defaultMedicalGroup_id', toVariant(medicalGroupId))
                    item.setValue('visitType_id', toVariant(visitTypeId))
                    item.setValue('defaultGoal_id', toVariant(defaultGoalId))
                    item.setValue('service_id', toVariant(serviceId))
                    item.setValue('selectionGroup', record.value('selectionGroup'))
                    if selectionGroup <= 0 or selectionGroup in includedGroups:
                        item.setValue('include', QtCore.QVariant(0))
                    else:
                        item.setValue('include', QtCore.QVariant(1))
                        includedGroups.add(selectionGroup)
                    item.setValue('price', QtCore.QVariant(0.0))
                    if specialityId and (recSpecialityId == specialityId):
                        item.setValue('include', QtCore.QVariant(1))
                    self.modelDiagnostics.items().append(item)
        self.modelDiagnostics.reset()

    def prepareActions(self, eventTypeId, specialityId, showFlags, flagHospitalization, addActionTypeId, recommendationList):
        includedGroups = set()
        db = QtGui.qApp.db
        table = db.table('EventType_Action')
        tableActionType = db.table('ActionType')
        self.disabledActionTypeIdList = []
        self.notDeletedActionTypes = {}
        join = table.leftJoin(tableActionType, tableActionType['id'].eq(table['actionType_id']))
        cond = [table['eventType_id'].eq(eventTypeId),
                tableActionType['deleted'].eq(0)]
        if specialityId:
            cond.append(db.joinOr( [ table['speciality_id'].eq(specialityId),  table['speciality_id'].isNull()] ))
        records = QtGui.qApp.db.getRecordList(join, 'EventType_Action.*, CONCAT_WS(\'|\', ActionType.code, ActionType.name) AS actionTypeName', cond, 'ActionType.class, idx, id')
        complexActionType = {}
        for record in records:
            actionTypeId = forceRef(record.value('actionType_id'))
            actionType = CActionTypeCache.getById(actionTypeId)
            if self.wholeEventForCash:
                payable = 2
            elif not self.showPrice:
                payable = 0
            else:
                payable = forceInt(record.value('payable'))

            if actionType and self.recordAcceptable(record):
                tissueTypeId = forceRef(record.value('tissueType_id'))
                if tissueTypeId and self.tissueTypeId:
                    if self.tissueTypeId != tissueTypeId:
                        continue
                selectionGroup = forceInt(record.value('selectionGroup'))
                if forceBool(record.value('isCompulsory')):
                    self.notDeletedActionTypes[actionTypeId] = forceString(record.value('actionTypeName'))
                if selectionGroup == -99:
                    self.disabledActionTypeIdList.append(actionTypeId)
                elif selectionGroup == 1 and not payable:
                    el = {'actionType_id': actionTypeId, 'defaultOrg_id': forceRef(record.value('defaultOrg_id'))}
                    self.unconditional_actionTypes_list.append(el)
                else:
                    if selectionGroup > 1 or showFlags[actionType.class_] or payable:
                        item = self.modelActions.getEmptyRecord()
                        item.setValue('actionType_id', toVariant(actionTypeId))
                        item.setValue('actuality', record.value('actuality'))
                        item.setValue('selectionGroup', record.value('selectionGroup'))
                        if selectionGroup <= 0 or selectionGroup in includedGroups:
                            item.setValue('include', QtCore.QVariant(0))
                            if not complexActionType.has_key(selectionGroup):
                                complexActionType[selectionGroup] = [actionTypeId]
                            else:
                                complexActionType[selectionGroup].append(actionTypeId)
                        else:
                            item.setValue('include', QtCore.QVariant(1))
                            if selectionGroup != 1:
                                includedGroups.add(selectionGroup)
                        item.setValue('cash', QtCore.QVariant(self.wholeEventForCash or payable == 2))
                        item.setValue('price', QtCore.QVariant(0.0))
                        item.setValue('payable', QtCore.QVariant(payable))
                        if forceRef(record.value('defaultOrg_id')):
                            item.setValue('defaultOrg_id', record.value('defaultOrg_id'))
                        else:
                            item.setValue('defaultOrg_id', toVariant(actionType.defaultOrgId))
                        item.setValue('id', record.value('id'))
                        self.modelActions.items().append(item)
        if flagHospitalization and addActionTypeId:
            actionTypeId = addActionTypeId
            actionType = CActionTypeCache.getById(actionTypeId)
            if actionType:
                if not self.isInside_unconditional_actionTypes_list(actionTypeId):
                    el = {'actionType_id': actionTypeId}
                    self.unconditional_actionTypes_list.append(el)

        actionTypeIdRecMap = {}
        for rec in recommendationList:
            actionTypeIdRecMap[forceInt(rec.value('actionType_id'))] = rec
        records = db.getRecordList(tableActionType, where=tableActionType['id'].inlist(actionTypeIdRecMap))
        for record in records:
            actionTypeId = forceInt(record.value('id'))
            el = {
                'actionType_id': actionTypeId,
                'org_id': forceInt(record.value('defaultOrg_id')),
                'amount': forceInt(actionTypeIdRecMap[actionTypeId].value('amount'))
            }
            self.unconditional_actionTypes_list.append(el)

        self.modelActions.setComplexActionType(complexActionType)
        self.modelActions.reset()

    def isInside_unconditional_actionTypes_list(self, actionTypeId):
        u"""
        этот метод возвращает True, если в unconditional_actionTypes_list имеется значение actionTypeId
        False - в противном случае
        """
        return any(map(lambda el: el.get('actionType_id') == actionTypeId, self.unconditional_actionTypes_list))

    def getEventTypeId(self):
        return self.eventTypeId

    def recordAcceptable(self, record):
        return recordAcceptable(self.clientSex, self.clientAge, record)

    def setDefaultCash(self):
        self.modelDiagnostics.setDefaultCash(self.wholeEventForCash)
        self.modelActions.setDefaultCash(self.wholeEventForCash)

    def updatePrices(self):
        visitTariffMap, actionTariffMap = self.getTariffMap()
        self.updateVisitPrices(visitTariffMap)
        self.updateActionPrices(actionTariffMap)
        self.updateTotalSum()

    def getTariffMap(self):
        if self.contractTariffCache and self.contractId:
            tariffDescr = self.contractTariffCache.getTariffDescr(self.contractId, self, self.eventDate)
            return tariffDescr.visitTariffMap, tariffDescr.actionTariffMap
        return {}, {}

    def updateVisitPrices(self, tariffMap):
        for i, item in enumerate(self.modelDiagnostics.items()):
            self.modelDiagnostics.setPrice(i, 0)

    def updateActionPrices(self, tariffMap):
        for i, item in enumerate(self.modelActions.items()):
            actionTypeId = forceRef(item.value('actionType_id'))
            if actionTypeId:
                serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, self.financeId)
                price = self.contractTariffCache.getPrice(tariffMap, serviceIdList, self.tariffCategoryId)
            else:
                price = ''
            self.modelActions.setPrice(i, price)

    def updateTotalSum(self):
        s = 0.0
        for item in self.modelDiagnostics.items():
            if forceBool(item.value('include')) and forceBool(item.value('cash')):
                s += forceDouble(item.value('sum'))
        for item in self.modelActions.items():
            if forceBool(item.value('include')) and forceBool(item.value('cash')):
                s += forceDouble(item.value('sum'))
        self.lblSumValue.setText('%.2f' % s)

    def diagnosticsTableIsNotEmpty(self):
        return bool(self.modelDiagnostics.items())

    def actionsTableIsNotEmpty(self):
        return bool(self.modelActions.items())

    def diagnostics(self):
        result = self.unconditionalDiagnosticList
        for item in self.modelDiagnostics.items():
            if forceBool(item.value('include')):
                MKB = forceString(item.value('defaultMKB'))
                dispanserId = forceRef(item.value('defaultDispanser_id'))
                healthGroupId = forceRef(item.value('defaultHealthGroup_id'))
                medicalGroupId = forceRef(item.value('defaultMedicalGroup_id'))
                serviceId = forceRef(item.value('service_id'))
                visitTypeId = forceRef(item.value('visitType_id'))
                goalId = forceRef(item.value('defaultGoal_id'))
                diagnostic = (MKB, dispanserId, healthGroupId, medicalGroupId, visitTypeId, goalId, serviceId)
                if diagnostic not in result:
                    result.append(diagnostic)
        return result

    def actions(self):
        u"""
        метод должен возвращать список туплов вида
        (actionTypeId, amount, isCash, org_id)
        в этот список должны попадать те рекорды, в которых include = True
        """
        atList = []
        for item in self.modelActions.items():
            actionTypeId = forceRef(item.value('actionType_id'))
            isInclude = forceBool(item.value('include'))
            amount = forceDouble(item.value('amount'))
            isCash = forceBool(item.value('cash'))
            defaultOrg_id = forceRef(item.value('defaultOrg_id'))
            if isInclude:
                atList.append((actionTypeId, amount, isCash, defaultOrg_id))
        for el in self.unconditional_actionTypes_list:
            actionTypeId = el.get('actionType_id')
            defaultOrg_id = el.get('defaultOrg_id')
            amount = el.get('amount', 1.0)
            atList.append((actionTypeId, amount, False, defaultOrg_id))
        return atList

    def selectAll(self, model, newState):
        for i, item in enumerate(model.items()):
            selectionGroup = forceInt(item.value('selectionGroup'))
            if selectionGroup == 0:
                item.setValue('include', QtCore.QVariant(newState))
        model.reset()
        self.updateTotalSum()

    def addActionType(self, actionTypeId):
        model = self.modelActions
        item = model.getEmptyRecord()
        item.setValue('actionType_id', toVariant(actionTypeId))
        item.setValue('selectionGroup', toVariant(0))
        item.setValue('include', QtCore.QVariant(1))
        if self.showPrice:
            item.setValue('cash', QtCore.QVariant(self.wholeEventForCash or bool(self.contractId)))
            item.setValue('payable', 2 if self.wholeEventForCash else 1 if self.contractId else 0)
            serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, self.financeId)
            visitTariffMap, actionTariffMap = self.getTariffMap()
            price = self.contractTariffCache.getPrice(actionTariffMap, serviceIdList, self.tariffCategoryId)
            item.setValue('price', QtCore.QVariant(price))
            item.setValue('amount', QtCore.QVariant(1.0))
            item.setValue('sum', QtCore.QVariant(price))
        model.items().append(item)
        count = len(model.items())
        model.beginInsertRows(QtCore.QModelIndex(), count, count)
        model.insertRows(count, 1)
        model.endInsertRows()

    def eventFilter(self, watched, event):
        if watched == self.tblDiagnostics or watched == self.tblActions:
            if (event.type() == QtCore.QEvent.KeyPress
                    and event.key() in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down)
                    and event.modifiers() & QtCore.Qt.ControlModifier):
                event.accept()
                self.moveSelectionToNextIncluded(watched, event.key() == QtCore.Qt.Key_Up)
                return True
        return CDialogBase.eventFilter(self, watched, event)

    def moveSelectionToNextIncluded(self, tblWidget, moveUp):
        index = tblWidget.currentIndex()
        row = index.row()
        row = tblWidget.model().getNextIncludedRow(row, moveUp)
        tblWidget.setCurrentIndex(index.sibling(row, index.column()))

    @QtCore.pyqtSlot()
    def on_cmbContract_valueChanged(self):
        self.contractId = self.cmbContract.value()
        self.financeId = forceRef(QtGui.qApp.db.translate('Contract', 'id', self.contractId, 'finance_id'))
        self.updatePrices()

    @QtCore.pyqtSlot()
    def on_modelDiagnostics_sumChanged(self):
        if self.showPrice:
            self.updateTotalSum()

    @QtCore.pyqtSlot()
    def on_modelActions_sumChanged(self):
        if self.showPrice:
            self.updateTotalSum()

    @QtCore.pyqtSlot()
    def on_btnSelectVisits_clicked(self):
        self.selectAll(self.modelDiagnostics, 1)

    @QtCore.pyqtSlot()
    def on_btnDeselectVisits_clicked(self):
        self.selectAll(self.modelDiagnostics, 0)

    @QtCore.pyqtSlot()
    def on_btnSelectActions_clicked(self):
        self.selectAll(self.modelActions, 1)

    @QtCore.pyqtSlot()
    def on_btnDeselectActions_clicked(self):
        self.selectAll(self.modelActions, 0)

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        context = CInfoContext()
        data = {'client': context.getInstance(CClientInfo, self.clientId),
                'date': CDateInfo(self.eventDate),
                'person': context.getInstance(CPersonInfo, self.personId),
                'visits': [],
                'actions': self.modelActions.getInfoList(context)
                }
        applyTemplate(self, templateId, data)


class CPreModel(CInDocTableModel):
    __pyqtSignals__ = ('sumChanged()',
                       )

    def __init__(self, *args, **kwargs):
        CInDocTableModel.__init__(self, *args, **kwargs)
        self.wholeEventForCash = False

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.append(QtSql.QSqlField('payable', QtCore.QVariant.Int))
        result.setValue('amount', QtCore.QVariant(1.0))
        result.setValue('cash', QtCore.QVariant(self.wholeEventForCash))
        return result

    def flags(self, index):
        row = index.row()
        column = index.column()
        if column == self.ciCash:
            payable = forceInt(self.items()[row].value('payable'))
            if self.wholeEventForCash or payable == 2:
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
            elif payable == 0:
                return QtCore.Qt.ItemIsSelectable
        return CInDocTableModel.flags(self, index)

    def data(self, index, role):
        if role == QtCore.Qt.CheckStateRole and index.column() == self.ciCash:
            row = index.row()
            payable = forceInt(self.items()[row].value('payable'))
            if payable == 0:
                return QtCore.QVariant()
        return CInDocTableModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.CheckStateRole:
            column = index.column()
            if column == 0:
                group = forceInt(self.items()[row].value('selectionGroup'))
                newState = 1 if forceInt(value) == QtCore.Qt.Checked else 0
                if group > 0:
                    newState = 1
                if group == 0:  # нулевая группа - всегда переключается
                    result = CInDocTableModel.setData(self, index, value, role)
                    self.emit(QtCore.SIGNAL('sumChanged()'))
                    return result
                if group == 1:  # первая группа - никогда не переключается
                    return False
                for itemIndex, item in enumerate(self.items()):
                    itemGroup = forceInt(item.value('selectionGroup'))
                    if itemGroup == group:
                        item.setValue('include', QtCore.QVariant(newState if itemIndex == row else 0))
                self.emitColumnChanged(0)
                self.emit(QtCore.SIGNAL('sumChanged()'))
                return True
            elif column == self.ciCash:
                payable = forceInt(self.items()[row].value('payable'))
                if payable == 1:
                    result = CInDocTableModel.setData(self, index, value, role)
                    self.emit(QtCore.SIGNAL('sumChanged()'))
                    return result
                else:
                    return False
        result = CInDocTableModel.setData(self, index, value, role)
        if result and role == QtCore.Qt.EditRole:
            if column == self.ciPrice or column == self.ciAmount:
                item = self.items()[row]
                price = forceDouble(item.value('price'))
                amount = forceDouble(item.value('amount'))
                sum = round(price * amount, 2)
                item.setValue('sum', toVariant(sum))
                self.emitCellChanged(row, column)
                self.emit(QtCore.SIGNAL('sumChanged()'))
        return result

    def setDefaultCash(self, wholeEventForCash):
        self.wholeEventForCash = wholeEventForCash

    def setPrice(self, i, price):
        self.setData(self.index(i, self.ciPrice), toVariant(price), QtCore.Qt.EditRole)

    def getNextIncludedRow(self, row, moveUp):
        items = self.items()
        step = -1 if moveUp else 1
        nextrow = row + step
        while 0 <= nextrow < len(items):
            if forceBool(items[nextrow].value('include')):
                return nextrow
            nextrow += step
        return row


class CDiagnosticsModel(CPreModel):
    ciCash = 7
    ciPrice = 8
    ciAmount = 9
    ciSum = 10

    def __init__(self, parent):
        CPreModel.__init__(self, 'EventType_Diagnostic', 'id', 'eventType_id', parent)
        self.addExtCol(CBoolInDocTableCol( u'Включить',       'include', 10), QtCore.QVariant.Int)
        self.addCol(CRBInDocTableCol(      u'Специальность',  'speciality_id', 20, 'rbSpeciality')).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'Услуга',         'service_id', 10, 'rbService', prefferedWidth=300, showFields=CRBComboBox.showCodeAndName)).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'Тип визита',     'visitType_id',  20, 'rbVisitType')).setReadOnly()
        self.addCol(CInDocTableCol(        u'МКБ',            'defaultMKB', 5)).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'ДН',             'defaultDispanser_id',   20, 'rbDispanser', showFields=CRBComboBox.showCode)).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'ГрЗд',           'defaultHealthGroup_id', 10, 'rbHealthGroup', showFields=CRBComboBox.showCode)).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'МедГр',          'defaultMedicalGroup_id', 10, 'rbMedicalGroup', showFields=CRBComboBox.showCode)).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'Цель обращения', 'defaultGoal_id', 20, 'rbEventGoal', showFields=CRBComboBox.showName)).setReadOnly()
        self.addCol(CIntInDocTableCol(     u'Группа выбора',  'selectionGroup', 5)).setReadOnly()
        self.setEnableAppendLine(False)

    def addPriceAndSumColumn(self):
        self.addExtCol(CBoolInDocTableCol(u'Нал.', 'cash', 10), QtCore.QVariant.Int)
        self.addExtCol(CFloatInDocTableCol(u'Цена', 'price', 7, precision=2), QtCore.QVariant.Double).setReadOnly()
        self.addExtCol(CInDocTableCol(u'Кол-во', 'amount', 7, precision=2), QtCore.QVariant.Double).setReadOnly(False)
        self.addExtCol(CFloatInDocTableCol(u'Сумма', 'sum', 7, precision=2), QtCore.QVariant.Double).setReadOnly()


class CActionsModel(CPreModel):
    ciCash = 5  # ci - column index
    ciPrice = 6  # это индексы для колонок cash, price, amount, sum
    ciAmount = 7  # если будете добавлять колонки в эту модель, не забудьте поменять эти индексы
    ciSum = 8

    def \
            __init__(self, parent):
        CPreModel.__init__(self, 'EventType_Action', 'id', 'eventType_id', parent)
        self.addExtCol(CBoolInDocTableCol( u'Включить',      'include', 10), QtCore.QVariant.Int)
        self.addCol(CRBInDocTableCol(      u'Код',           'actionType_id',20, 'ActionType', showFields=CRBComboBox.showCode)).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'Наименование',  'actionType_id',20, 'ActionType', showFields=CRBComboBox.showName)).setReadOnly()
        self.addCol(CIntInDocTableCol(     u'Группа выбора', 'selectionGroup', 5)).setReadOnly()
        self.addCol(CPolyclinicExtendedInDocTableCol(u'Место проведения', 'defaultOrg_id', 20)).setReadOnly()
        self.setEnableAppendLine(False)
        self.complexActionType = {}

    def addPriceAndSumColumn(self):
        self.addExtCol(CBoolInDocTableCol(u'Нал.', 'cash', 10), QtCore.QVariant.Int)
        self.addExtCol(CFloatInDocTableCol(u'Цена', 'price', 7, precision=2), QtCore.QVariant.Double).setReadOnly()
        self.addExtCol(CInDocTableCol(u'Кол-во', 'amount', 7, precision=2), QtCore.QVariant.Double).setReadOnly(False)
        self.addExtCol(CFloatInDocTableCol(u'Сумма', 'sum', 7, precision=2), QtCore.QVariant.Double).setReadOnly()

    def getInfoList(self, context):
        result = []
        for item in self.items():
            include = forceBool(item.value('include'))
            cash = forceBool(item.value('cash'))
            if include:
                actionTypeId = forceRef(item.value('actionType_id'))
                actionType = CActionTypeCache.getById(actionTypeId)
                actionTypeInfo = CActionTypeInfo(context, actionType)
                price = forceDouble(item.value('price'))
                actionTypeInfo.price = price
                amount = forceDouble(item.value('amount'))
                actionTypeInfo.amount = amount
                sum = forceDouble(item.value('sum'))
                actionTypeInfo.sum = sum
                actionTypeInfo.cash = cash
                result.append(actionTypeInfo)
        return result

    def actionTypePresent(self, actionTypeId):
        for item in self.items():
            if actionTypeId == forceRef(item.value('actionType_id')):
                return True
        return False

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        if role == QtCore.Qt.CheckStateRole:
            column = index.column()
            if column == 0:
                group = forceInt(self.items()[row].value('selectionGroup'))
                newState = 1 if forceInt(value) == QtCore.Qt.Checked else 0
                for itemIndex, item in enumerate(self.items()):
                    itemGroup = forceInt(item.value('selectionGroup'))
                    if itemGroup == group and group < 0:
                        if forceRef(item.value('actionType_id')) in self.complexActionType[group]:
                            item.setValue('include', QtCore.QVariant(newState))
                            self.emitColumnChanged(0)
                            self.emit(QtCore.SIGNAL('sumChanged()'))
                            return True
        return CPreModel.setData(self, index, value, role)

    def setComplexActionType(self, complexActionType):
        self.complexActionType = complexActionType
