# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Events.ActionInfo import CActionInfoProxyList
from Events.ActionsPage import CActionsPage
from Events.EventEditDialog import CEventEditDialog
from Events.EventInfo import CEventInfo
from Forms.F025.PreF025Dialog import CPreF025DagnosticAndActionPresets
from Orgs.OrgComboBox import CContractComboBox
from library.Utils import toVariant, forceInt

'''
Created on 27.03.2014

@author: atronah
'''


class CFastCreateEventDialog(CEventEditDialog):
    PreDagnosticAndActionPresetsClass = CPreF025DagnosticAndActionPresets

    def __init__(self, parent=None):
        super(CFastCreateEventDialog, self).__init__(parent)
        self.setupUi()
        self.setupDirtyCather()

    def setOrgId(self, orgId):
        super(CFastCreateEventDialog, self).setOrgId(orgId)
        self.actionPage.setOrgId(orgId)

    def getRecord(self):
        record = super(CFastCreateEventDialog, self).getRecord()
        record.setValue('setPerson_id', toVariant(self.personId))
        record.setValue('execPerson_id', toVariant(self.personId))
        return record

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                 includeRedDays, numDays, presetDiagnostics, presetActions, disabledActions, externalId, assistantId,
                 curatorId, movingActionTypeId=None, valueProperties=None, relegateOrgId=None, diagnos=None,
                 financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                 recommendationList=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        if not referrals:
            referrals = {}
        result = super(CFastCreateEventDialog, self)._prepare(contractId, clientId, eventTypeId, orgId, personId,
                                                              eventSetDatetime, eventDatetime, includeRedDays, numDays,
                                                              presetDiagnostics, presetActions, disabledActions,
                                                              externalId, assistantId, curatorId, movingActionTypeId,
                                                              valueProperties, relegateOrgId, diagnos, financeId,
                                                              protocolQuoteId, actionByNewEvent, referrals)
        self.cmbContract.setBegDate(self.eventSetDateTime.date())
        self.cmbContract.setEndDate(self.eventSetDateTime.date())
        self.cmbContract.setValue(contractId)
        self.prepareActions(presetActions, disabledActions, movingActionTypeId, valueProperties, diagnos, financeId,
                            protocolQuoteId, actionByNewEvent)
        return result

    def setupUi(self):
        layout = QtGui.QVBoxLayout()

        contractLayout = QtGui.QHBoxLayout()
        self.cmbContract = CContractComboBox()
        self.lblContract = QtGui.QLabel(u'&Договор:')
        self.lblContract.setBuddy(self.cmbContract)
        contractLayout.addWidget(self.lblContract)
        contractLayout.addWidget(self.cmbContract)
        contractLayout.addStretch()
        layout.addLayout(contractLayout)

        self.actionPage = CActionsPage(self)
        self.actionPage.modelAPActions.setActionTypeClass(None)
        self.actionPage.setEventEditor(self)
        layout.addWidget(self.actionPage)

        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel,
                                                QtCore.Qt.Horizontal)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        QtCore.QMetaObject.connectSlotsByName(self)

    def saveInternals(self, eventId):
        self.actionPage.saveActions(eventId)

    # TODO: atronah: refactoring: сперто из CF003Dialog
    def prepareActions(self, presetActions, disabledActions, actionTypeIdValue, valueProperties, diagnos, financeId,
                       protocolQuoteId, actionByNewEvent):
        def addActionType(actionTypeId, amount, idListActionType, idListActionTypeIPH, actionFinance,
                          idListActionTypeMoving):
            for model in [self.actionPage.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    if actionTypeId in idListActionType and not actionByNewEvent:
                        model.addRow(actionTypeId, amount)
                        record, action = model.items()[-1]
                        action[u'Направлен в отделение'] #atronah: для инициализации этого Property, чтобы при сохранении оно записалось хотя бы со значением по умолчанию =)
                        if valueProperties and len(valueProperties) > 0 and valueProperties[0]:
                            action[u'Направлен в отделение'] = valueProperties[0]
                        if protocolQuoteId:
                            action[u'Квота'] = protocolQuoteId
                        if actionFinance == 0:
                            record.setValue('finance_id', toVariant(financeId))
                    elif actionTypeId in idListActionTypeIPH:
                        model.addRow(actionTypeId, amount)
                        record, action = model.items()[-1]
                        if diagnos:
                            record, action = model.items()[-1]
                            action[u'Диагноз'] = diagnos
                    # [self.eventActionFinance, self.receivedFinanceId, orgStructureTransfer, orgStructurePresence, oldBegDate, movingQuoting, personId]
                    elif actionByNewEvent and actionTypeId in idListActionTypeMoving:
                        model.addRow(actionTypeId, amount)
                        record, action = model.items()[-1]
                        if actionByNewEvent[0] == 0:
                            record.setValue('finance_id', toVariant(actionByNewEvent[1]))
                        action[u'Отделение пребывания'] = actionByNewEvent[2]
                        action[u'Переведен из отделения'] #atronah: для инициализации этого Property, чтобы при сохранении оно записалось хотя бы со значением по умолчанию =)
                        if actionByNewEvent[3]:
                            action[u'Переведен из отделения'] = actionByNewEvent[3]
                        if actionByNewEvent[4]:
                            record.setValue('begDate', toVariant(actionByNewEvent[4]))
                        else:
                            record.setValue('begDate', toVariant(QtCore.QDateTime.currentDateTime()))
                        if action.getType().containsPropertyWithName(u'Квота') and actionByNewEvent[5]:
                            action[u'Квота'] = actionByNewEvent[5]
                        if actionByNewEvent[6]:
                            record.setValue('person_id', toVariant(actionByNewEvent[6]))
                    elif (actionByNewEvent and actionTypeId not in idListActionType) or not actionByNewEvent:
                        model.addRow(actionTypeId, amount)
                        record, action = model.items()[-1]

        def disableActionType(actionTypeId):
            for model in [self.tabStatus.modelAPActions,
                          self.tabDiagnostic.modelAPActions,
                          self.tabCure.modelAPActions,
                          self.tabMisc.modelAPActions]:
                if actionTypeId in model.actionTypeIdList:
                    model.disableActionType(actionTypeId)
                    break

        if disabledActions:
            for actionTypeId in disabledActions:
                disableActionType(actionTypeId)
        if presetActions:
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            tableEventType = db.table('EventType')
            idListActionType = db.getIdList(tableActionType, [tableActionType['id']],
                                            [tableActionType['flatCode'].like(u'received%'),
                                             tableActionType['deleted'].eq(0)])
            idListActionTypeIPH = db.getIdList(tableActionType, [tableActionType['id']],
                                               [tableActionType['flatCode'].like(u'inspectPigeonHole%'),
                                                tableActionType['deleted'].eq(0)])
            idListActionTypeMoving = db.getIdList(tableActionType, [tableActionType['id']],
                                                  [tableActionType['flatCode'].like(u'moving%'),
                                                   tableActionType['deleted'].eq(0)])
            eventTypeId = self.getEventTypeId()
            actionFinance = None
            if eventTypeId:
                recordET = db.getRecordEx(tableEventType, [tableEventType['actionFinance']],
                                          [tableEventType['deleted'].eq(0), tableEventType['id'].eq(eventTypeId)])
                actionFinance = forceInt(recordET.value('actionFinance')) if recordET else None
            if actionByNewEvent:
                actionTypeMoving = False
                for actionTypeId, amount, _, orgId in presetActions:
                    if actionTypeId in idListActionTypeMoving:
                        actionTypeMoving = True
                        break
                if not actionTypeMoving and idListActionTypeMoving:
                    presetActions.append((idListActionTypeMoving[0], 1.0, False))
            for actionTypeId, amount, cash, orgId in presetActions:
                addActionType(actionTypeId, amount, idListActionType, idListActionTypeIPH, actionFinance,
                              idListActionTypeMoving)

    def getEventInfo(self, context, infoClass=CEventInfo):
        result = super(CFastCreateEventDialog, self).getEventInfo(context, infoClass)
        result._actions = CActionInfoProxyList(context,
                                               [self.actionPage.modelAPActions],
                                               result)
        return result
