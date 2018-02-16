# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Action import CActionType, CActionTypeCache
from Events.ActionPropertiesTable import CExActionPropertiesTableModel
from Events.ActionsAnalysesModel import CActionsAnalysesModel
from Events.ActionsAnalysesSelector import selectActionTypesAnalyses
from Events.ActionsPage import CFastActionsPage
from Events.Utils import CActionTemplateCache, CFinanceType
from Orgs.Utils import getOrgStructureActionTypeIdList, getTopParentIdForOrgStructure, getRealOrgStructureId
from library.Utils import forceRef, toVariant


class CFastAnalysesActionsPage(CFastActionsPage):
    def __init__(self, parent=None):
        CFastActionsPage.__init__(self, parent)

    def preSetupUiMini(self):
        self.addModels('APActions', CActionsAnalysesModel(self))
        if QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
            topOrgStructureId = getTopParentIdForOrgStructure(QtGui.qApp.userOrgStructureId)
            if topOrgStructureId:
                actionTypeIdList = getOrgStructureActionTypeIdList(topOrgStructureId, True)
                actionTypeIdList = QtGui.qApp.db.getTheseAndParents('ActionType', 'group_id', actionTypeIdList)
                self.modelAPActions.enableActionTypeList(actionTypeIdList)
        self.addModels('APActionProperties', CExActionPropertiesTableModel(self))
        self._updateEditable()
        self.commonTakenTissueJournalRecordId = None
        self._visibleMorphologyMKB = QtGui.qApp.defaultMorphologyMKBIsVisible()
        self._canUseLaboratoryCalculator = False
        self.receivedFinanceId = None
        self.eventActionFinance = None
        self.defaultFinanceId = None
        self.defaultContractFilterPart = None
        self.allowedActionTypesByTissue = []
        self.notFilteredActionTypesClasses = []
        self.defaultDirectionDate = CActionType.dddUndefined
        self.actionTemplateCache = CActionTemplateCache(self.eventEditor)
        self.isPreUiMiniSetted = True

    def setupUi(self, widget):
        CFastActionsPage.setupUi(self, widget)
        self.connect(self.cmbAPStatus, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbAPStatus_currentIndexChanged)

    @QtCore.pyqtSlot()
    def on_actAPActionsAdd_triggered(self):
        model = self.tblAPActions.model()
        if not hasattr(model, 'isEditable') or model.isEditable():
            chkContractByFinanceId = CFinanceType.getCode(self.eventEditor.eventFinanceId) in (CFinanceType.VMI, CFinanceType.cash)
            typeClasses = self.modelAPActions.actionTypeClass
            if not isinstance(typeClasses, list):
                typeClasses = [typeClasses]

            actionTypes = selectActionTypesAnalyses(self.eventEditor,
                                                    actionTypeClasses=typeClasses,
                                                    clientSex=self.eventEditor.clientSex,
                                                    clientAge=self.eventEditor.clientAge,
                                                    orgStructureId=getRealOrgStructureId(),
                                                    eventTypeId=self.eventEditor.getEventTypeId(),
                                                    contractId=self.eventEditor.getContractId(),
                                                    mesId=self.eventEditor.getMesId(),
                                                    chkContractByFinanceId=chkContractByFinanceId,
                                                    eventId=self.eventEditor._id,
                                                    contractTariffCache=self.eventEditor.contractTariffCache,
                                                    notFilteredActionTypesClasses=self.notFilteredActionTypesClasses,
                                                    defaultFinanceId=self.defaultFinanceId,
                                                    defaultContractFilterPart=self.defaultContractFilterPart,
                                                    eventBegDate=self.eventEditor.begDate(),
                                                    eventEndDate=self.eventEditor.endDate(),
                                                    paymentScheme=self.eventEditor.getPaymentScheme(),
                                                    returnDirtyRows=False)
            for actionTypeId, action in actionTypes:
                model.addItem((action.getRecord(), action))
            model.reset()
            self.onActionCurrentChanged()

    @QtCore.pyqtSlot(int)
    def on_cmbAPStatus_currentIndexChanged(self, index):
        currentRow = self.tblAPActions.currentIndex().row()
        self.onChangeState(index, currentRow)

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtAPEndTime_timeChanged(self, time):
        row = self.tblAPActions.currentIndex().row()
        date = self.edtAPEndDate.date()
        self.onEdtTimeChange(date, time, row)

    @QtCore.pyqtSlot(int)
    def on_cmbAPPerson_currentIndexChanged(self, index):
        row = self.tblAPActions.currentIndex().row()
        self.onPersonChange(self.cmbAPPerson.value(), row)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtAPPlannedEndDate_dateChanged(self, date):
        self.edtAPPlannedEndTime.setEnabled(bool(date))
        time = self.edtAPPlannedEndTime.time() if date and self.edtAPPlannedEndTime.isVisible() else QtCore.QTime()
        self.onActionDataChanged('plannedEndDate', QtCore.QDateTime(date, time))

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtAPPlannedEndTime_timeChanged(self, time):
        date = self.edtAPPlannedEndDate.date()
        self.onActionDataChanged('plannedEndDate', QtCore.QDateTime(date, time if date else QtCore.QTime()))

    def onEdtTimeChange(self, date, time, row):
        self.onActionDataChanged('endDate', QtCore.QDateTime(date, time if date else QtCore.QTime()), row)

    def onPersonChange(self, value, row):
        self.onActionDataChanged('person_id', self.cmbAPPerson.value(), row)

    def onActionDataChanged(self, name, value, row=None):
        model = self.tblAPActions.model()
        items = model.items()
        if row is None:
            row = self.tblAPActions.currentIndex().row()
        if 0 <= row < len(items):
            record, action = items[row]
            record.setValue(name, toVariant(value))
            actionTypeId = forceRef(record.value('actionType_id')) if record else None
            actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None

            self.gBoxSupportService.setVisible(False)
            self.btnNextAction.setText(u'Действие')
            self.btnNextAction.setEnabled(False)
            self.btnPlanNextAction.setEnabled(False)

            if actionType.defaultPlannedEndDate == CActionType.dpedBegDatePlusAmount and name in ['amount', 'begDate']:
                begDate = self.edtAPBegDate.date()
                amountValue = int(self.edtAPAmount.value())
                date = begDate.addDays(amountValue-1) if (amountValue and begDate.isValid()) else QtCore.QDate()
                self.setEndDate(date, row)
                self.edtAPPlannedEndDate.setDate(date)

    def onChangeState(self, index, row):
        currentRow = self.tblAPActions.currentIndex().row()
        if self.modelAPActions.items():
            self.onActionDataChanged('status', index)
            for rowNumber in xrange(currentRow + 1, len(self.modelAPActions.items())):
                actionTypeIdOnRow = forceRef(self.modelAPActions.items()[rowNumber][0].value('actionType_id'))
                if self.modelAPActions.isMainActionType(actionTypeIdOnRow):
                    break
                self.onActionDataChanged('status', index, rowNumber)

            if index in [2, 4]:
                if not self.edtAPEndDate.date():
                    now = QtCore.QDateTime.currentDateTime()
                    self.setEndDate(now.date())
                    if self.edtAPEndTime.isVisible():
                        self.edtAPEndTime.setTime(now.time())
            elif index in [3]:
                eventPurposeId = self.eventEditor.getEventPurposeId()
                if not (QtGui.qApp.db.translate('rbEventTypePurpose', 'id', eventPurposeId, 'federalCode = 8')):
                    if QtGui.qApp.userId and QtGui.qApp.userSpecialityId:
                        self.onChangePerson(QtGui.qApp.userId)
                    else:
                        self.onChangePerson(QtGui.qApp.userId)
                        self.cmbAPPerson.setValue(self.cmbAPSetPerson.value())
            elif index in [5, 6]:
                pass
            else:
                self.setEndDate(QtCore.QDate())
