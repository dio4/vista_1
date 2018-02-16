# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from DataCheck.CCheck import CCheck
from Events.Utils import CFinanceType, getClientRepresentativePolicyList, getEventAcceptablePolicyList, getEventFinanceCode, getEventFinanceId, \
    getWorkEventTypeFilter, isLittleStranger
from Orgs.OrgComboBox import CContractDbData, CContractDbModel
from Registry.Utils import getClientWork
from Ui_EventContractCheckDialog import Ui_EventContractChecklDialog
from library.DialogBase import CDialogBase
from library.Utils import calcAgeTuple, forceDate, forceInt, forceRef, toVariant


class CEventPolicyChecker(object):
    def __init__(self, db=None):
        self.db = db or QtGui.qApp.db
        self.franchisPolicyTypeId = forceRef(self.db.translate('rbPolicyType', 'code', 'franchis', 'id'))
        self.voluntaryPolicyTypeId = forceRef(self.db.translate('rbPolicyType', 'code', '3', 'id'))
        self.contractModel = CContractDbModel(None)
        self.contractData = CContractDbData()
        self.curDate = QtCore.QDate.currentDate()

    def getPolicy(self, eventRec):
        clientId = forceRef(eventRec.value('client_id'))
        littleStranger = isLittleStranger(clientId,
                                          forceDate(eventRec.value('setDate')),
                                          forceDate(eventRec.value('execDate')))
        eventTypeId = forceRef(eventRec.value('eventType_id'))
        execDate = forceDate(eventRec.value('execDate'))
        eventIsClosed = not execDate.isNull()
        atDate = self.curDate if eventIsClosed else execDate

        if getEventFinanceCode(eventTypeId) == CFinanceType.VMI:
            idList = (getEventAcceptablePolicyList(clientId, policyTypeId=self.franchisPolicyTypeId, date=atDate) or
                      getEventAcceptablePolicyList(clientId, policyTypeId=self.voluntaryPolicyTypeId, date=atDate))
            newPolicy = idList[-1] if idList else None
        elif littleStranger:
            newPolicy = getClientRepresentativePolicyList(clientId, date=atDate)
        else:
            idList = getEventAcceptablePolicyList(clientId, date=atDate, eventIsClosed=eventIsClosed)
            newPolicy = idList[-1] if idList else None

        return newPolicy

    def getContract(self, eventRec, clientRec=None):
        eventTypeId = forceRef(eventRec.value('eventType_id'))
        financeId = getEventFinanceId(eventTypeId)
        setDate = forceDate(eventRec.value('setDate'))
        execDate = forceDate(eventRec.value('execDate'))
        clientId = forceRef(eventRec.value('client_id'))
        clientPolicyId = forceRef(eventRec.value('clientPolicy_id'))
        orgId = forceRef(eventRec.value('org_id'))

        self.contractModel.setOrgId(orgId)
        self.contractModel.setCheckMaxClients(True)
        self.contractModel.setBegDate(setDate)
        self.contractModel.setEndDate(execDate)
        self.contractModel.setEventTypeId(eventTypeId)
        self.contractModel.setFinanceId(financeId)

        if clientId:
            clientSex = forceInt(clientRec.value('sex'))
            clientAge = calcAgeTuple(forceDate(clientRec.value('birthDate')), setDate)
            clientWorkRecord = getClientWork(clientId)
            clientWorkOrgId = forceRef(clientWorkRecord.value('org_id')) if clientWorkRecord else None

            policyRec = self.db.getRecord('ClientPolicy', 'insurer_id, policyType_id', clientPolicyId)
            insurerId, policyTypeId = (forceRef(policyRec.value('insurer_id')),
                                       forceRef(policyRec.value('policyType_id'))) if policyRec else (None, None)
            clientPolicyInfoList = [(insurerId, policyTypeId)]

            self.contractModel.setClientInfo(clientId, clientSex, clientAge, clientWorkOrgId, clientPolicyInfoList)

        self.contractData.select(self.contractModel)

        return self.contractData.idList[0] if self.contractData.idList else None

    def updateEvents(self, eventIdList, updateContracts=False):
        tableClient = self.db.table('Client')
        tableEvent = self.db.table('Event')

        for eventRec in self.db.iterRecordList(tableEvent, where=tableEvent['id'].inlist(eventIdList)):
            updateRecord = False

            oldPolicy = forceRef(eventRec.value('clientPolicy_id'))
            newPolicy = self.getPolicy(eventRec)
            if newPolicy and newPolicy != oldPolicy:
                eventRec.setValue('clientPolicy_id', toVariant(newPolicy))
                updateRecord = True

            if updateContracts:
                clientId = forceRef(eventRec.value('client_id'))
                clientRec = self.db.getRecord(tableClient, 'birthDate', clientId)
                oldContract = forceRef(eventRec.value('contract_id'))
                newContract = self.getContract(eventRec, clientRec)
                if newContract and newContract != oldContract:
                    eventRec.setValue('contract_id', toVariant(newContract))
                    updateRecord = True

            if updateRecord:
                self.db.updateRecord(tableEvent, eventRec)


class CEventContractCheck(CDialogBase, Ui_EventContractChecklDialog, CCheck):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        CCheck.__init__(self)
        self.tblEventType.setTable('EventType', filter=getWorkEventTypeFilter())

        self.curDate = QtCore.QDate.currentDate()
        self.orgId = QtGui.qApp.currentOrgId()
        self.eventTypeMap = {}
        self.finishedEventTypes = set()
        self._franchisPolicyTypeId = forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', 'franchis', 'id'))
        self._voluntaryPolicyTypeId = forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', '3', 'id'))

    def getClientPolicy(self, clientId, date, policyTypeId=None, eventIsClosed=False):
        idList = getEventAcceptablePolicyList(clientId, policyTypeId=policyTypeId, date=date, eventIsClosed=eventIsClosed)
        return idList[-1] if idList else None

    def getClientRepresentativePolicy(self, clientId, date, policyTypeId=None):
        idList = getClientRepresentativePolicyList(clientId, policyTypeId=policyTypeId, date=date)
        return idList[-1] if idList else None

    def getContract(self, eventRecord, clientRecord=None):
        eventTypeId = forceRef(eventRecord.value('eventType_id'))
        financeId = getEventFinanceId(eventTypeId)
        setDate = forceDate(eventRecord.value('setDate'))
        execDate = forceDate(eventRecord.value('execDate'))
        clientId = forceRef(eventRecord.value('client_id'))
        clientPolicyId = forceRef(eventRecord.value('clientPolicy_id'))
        orgId = forceRef(eventRecord.value('org_id'))

        model = CContractDbModel(self)
        model.setOrgId(orgId)
        model.setCheckMaxClients(True)
        model.setBegDate(setDate)
        model.setEndDate(execDate)
        model.setEventTypeId(eventTypeId)
        model.setFinanceId(financeId)

        if clientId:
            clientSex = forceInt(clientRecord.value('sex'))
            clientAge = calcAgeTuple(forceDate(clientRecord.value('birthDate')), setDate)
            clientWorkRecord = getClientWork(clientId)
            clientWorkOrgId = forceRef(clientWorkRecord.value('org_id')) if clientWorkRecord else None

            clientPolicyRecord = QtGui.qApp.db.getRecord('ClientPolicy', 'insurer_id, policyType_id', clientPolicyId)
            insurerId, policyTypeId = (forceRef(clientPolicyRecord.value('insurer_id')),
                                       forceRef(clientPolicyRecord.value('policyType_id'))) if clientPolicyRecord else (None, None)
            clientPolicyInfoList = [(insurerId, policyTypeId)]

            model.setClientInfo(clientId, clientSex, clientAge, clientWorkOrgId, clientPolicyInfoList)

        dbData = CContractDbData()
        dbData.select(model)

        return dbData.idList[0] if dbData.idList else None

    def check(self):
        db = QtGui.qApp.db
        Client = db.table('Client')
        Event = db.table('Event')

        dateFrom = self.edtDateFrom.date()
        dateTo = self.edtDateTo.date()
        eventTypeIdList = self.tblEventType.values()

        cond = [
            Event['setDate'].dateGe(dateFrom),
            Event['setDate'].dateLe(dateTo),
            Event['client_id'].isNotNull(),
            Event['org_id'].eq(self.orgId),
            Event['deleted'].eq(0)
        ]
        if eventTypeIdList:
            cond.append(Event['eventType_id'].inlist(eventTypeIdList))

        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            self.lblInfo.setText(u'Выполнение запроса к БД ...')
            events = db.getRecordList(Event, where=cond)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        policyCount = 0
        contractCount = 0
        noPolicyCount = 0
        noContractCount = 0
        noChangesCount = 0
        self.progressBar.setMaximum(len(events))

        for i, eventRec in enumerate(events):
            QtGui.qApp.processEvents()
            if self.abort:
                break

            clientId = forceRef(eventRec.value('client_id'))
            littleStranger = isLittleStranger(clientId,
                                              begDate=forceDate(eventRec.value('setDate')),
                                              endDate=forceDate(eventRec.value('execDate')))

            eventId = forceRef(eventRec.value('id'))
            eventTypeId = forceRef(eventRec.value('eventType_id'))
            self.eventTypeMap[eventId] = eventTypeId
            execDate = forceDate(eventRec.value('execDate'))
            eventIsClosed = not execDate.isNull()
            atDate = self.curDate if eventIsClosed else execDate

            self.itemId = eventId
            self.item_bad = False
            self.err_str = u'Обращение {0}: '.format(eventId)
            updateRecord = False

            oldPolicy = forceRef(eventRec.value('clientPolicy_id'))
            if getEventFinanceCode(eventTypeId) == CFinanceType.VMI:
                newPolicy = self.getClientPolicy(clientId, atDate, self._franchisPolicyTypeId, eventIsClosed) or \
                            self.getClientPolicy(clientId, atDate, self._voluntaryPolicyTypeId, eventIsClosed)
            elif littleStranger:
                newPolicy = self.getClientRepresentativePolicy(clientId, atDate)
            else:
                newPolicy = self.getClientPolicy(clientId, atDate, eventIsClosed=eventIsClosed)

            if newPolicy and newPolicy != oldPolicy:
                policyCount += 1
                self.err2log(u'переподвязан полис' if oldPolicy else (u'не был выбран полис, подвязан' + (u' полис представителя' if littleStranger else '')))
                eventRec.setValue('clientPolicy_id', newPolicy)
                updateRecord = True
            elif not oldPolicy and not newPolicy:
                noPolicyCount += 1
                self.err2log(u'не удалось подвязать полис')

            clientRecord = db.getRecord(Client, 'birthDate', clientId)
            oldContract = forceRef(eventRec.value('contract_id'))
            newContract = self.getContract(eventRec, clientRecord)
            if newContract and newContract != oldContract:
                contractCount += 1
                self.err2log(u'переподвязан договор' if oldContract else u'не был выбран договор, подвязан')
                eventRec.setValue('contract_id', newContract)
                updateRecord = True
            elif not oldContract and not newContract:
                noContractCount += 1
                self.err2log(u'не удалось подвязать договор')

            if updateRecord:
                db.updateRecord(Event, eventRec)
            else:
                noChangesCount += 1

            self.progressBar.setValue(i + 1)
            self.updateInfoLabel(i + 1, policyCount, noPolicyCount, contractCount, noContractCount, noChangesCount)

        if not events:
            self.progressBar.setMaximum(1)
            self.progressBar.setValue(1)
            self.lblInfo.setText(u'Нет подходящих обращений')

        self.finishedEventTypes |= set(eventTypeIdList)

    @QtCore.pyqtSlot()
    def on_btnStart_clicked(self):
        self.btnStart.setEnabled(False)
        self.lblInfo.setText(u'')
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.log.clear()
        self.btnClose.setText(u'Прервать')
        self.abort = False
        self.checkRun = True
        self.items = {}
        self.rows = 0

        try:
            self.check()
        except IOError, e:
            QtGui.qApp.logCurrentException()
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical(self,
                                       u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical(self,
                                       u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.abort = True
        self.progressBar.setText(u'прервано' if self.abort else u'готово')
        self.btnClose.setText(u'Закрыть')
        self.abort = False
        self.checkRun = False
        self.btnStart.setEnabled(True)

    def updateInfoLabel(self, eventCount, policyCount, noPolicyCount, contractCount, noContractCount, noChangesCount):
        self.lblInfo.setText(u'Обработано {0} обращений: переподвязано полисов: {1}{2}; переподвязано договоров {3}{4}; без изменений: {5}'.format(
            eventCount,
            policyCount, u' (не удалось %s)' % noPolicyCount if noPolicyCount else u'',
            contractCount, u' (не удалось %s)' % noContractCount if noContractCount else u'',
            noChangesCount)
        )

    def openItem(self, eventId):
        eventTypeId = self.eventTypeMap.get(eventId)
        formClass = self.getEventFormClass(eventTypeId)
        form = formClass(self)
        form.load(eventId)
        return form
