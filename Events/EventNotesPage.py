# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Events.Utils import checkUniqueEventExternalId, getCounterType, getEventCounterId, getEventIsExternal, \
    getEventPrefix, getUniqueExternalIdRequired, hasEventAssistant, hasEventCurator, \
    getRealPayed, getEventFinanceCode, isLittleStranger
from library.LoggingModule.Logger import loggerDbName
from library.Counter import getDocumentNumber
from library.interchange import getDateEditValue, getLineEditValue, getRBComboBoxValue, getTextEditValue, \
    setDateEditValue, setLineEditValue, setRBComboBoxValue, setTextEditValue, \
    getCheckBoxValue, setCheckBoxValue
from library.Utils import forceInt, forceRef, forceString, forceStringEx, toVariant, forceDate
from Orgs.Orgs import selectOrganisation
from Orgs.OrgComboBox import CPolyclinicComboBox, CArmyOrgComboBox
from Users.Rights import urCreateReferral, urEditClientPolicyInClosedEvent, urAdmin, urEventLock
from Ui_EventNotesPage import Ui_EventNotesPageWidget
from library.EMK import EmkService


class CFastEventNotesPage(QtGui.QWidget, Ui_EventNotesPageWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.dontSaveReferral = False
        self._isEditable = True
        self._clientId = None
        self._eventResultId = None
        self._originalEventResultId = None
        self._IEMKService = None
        u""":type : EmkService.Service | None"""

    def sendClient(self):
        if self._IEMKService is None:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Сначала введите адреса сервисов и используйте их')
            return
        self._IEMKService.sendClient(self._clientId)

    def sendCase(self):
        if self._IEMKService is None:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Сначала введите адреса сервисов и используйте их')
            return
        eventId = int(self.lblEventIdValue.text())
        if not eventId:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Сначала сохраните случай')
            return
        self._IEMKService.sendEvent(eventId)

    def createService(self):
        self._IEMKService = EmkService.Service(EMK_WSDL_URL=unicode(self.edtCaseURL.text()),
                                               PIX_WSDL_URL=unicode(self.edtPixURL.text()),
                                               GUID=unicode(self.edtGUID.text()))
        QtGui.qApp.preferences.appPrefs['edtCaseURL'] = toVariant(self.edtCaseURL.text())
        QtGui.qApp.preferences.appPrefs['edtPixURL'] = toVariant(self.edtPixURL.text())
        QtGui.qApp.preferences.appPrefs['edtGUID'] = toVariant(self.edtGUID.text())
        QtGui.qApp.preferences.save()

    def useBtnExternalIdupd(self, slot):
        self.btnExternalIdupd.setVisible(True)
        self.btnExternalIdupd.clicked.connect(slot)

    def setEditable(self, editable):
        self._isEditable = editable
        self._updateEditable()

    def _updateEditable(self):
        self.setEnabled(self._isEditable)

    def setupUiMini(self, Dialog):
        pass

    def preSetupUiMini(self):
        pass

    def preSetupUi(self):
        # FIXME: atronah: почему не в init??
        self._externalIdIsChanged = False

    def postSetupUiMini(self, eventBegDate=None):
        self.edtPlannedDate.setDate(QtCore.QDate())
        self.edtDate.setDate(QtCore.QDate())
        self.setFocusProxy(self.edtEventNote)
        self.cmbCureType.setTable('rbCureType')
        self.cmbCureMethod.setTable('rbCureMethod')
        self.cmbSpeciality.setTable('rbSpeciality', True)
        db = QtGui.qApp.db
        cond = []
        tableReferral = db.table('Referral')
        clientId = self._clientId if self._clientId else QtGui.qApp.currentClientId()
        if clientId:
            cond.append('client_id=%d' % clientId)
        if eventBegDate:
            self.edtDate.setMinimumDate(eventBegDate.addMonths(-6))
            self.edtDate.setMaximumDate(eventBegDate)
            if not self.edtDate.date().isNull():
                self.edtPlannedDate.setMinimumDate(eventBegDate.addMonths(self.edtDate.date().addMonths(6)))
                self.edtPlannedDate.setMaximumDate(eventBegDate)
        self.cmbArmyNumber.setFilter(db.joinAnd(cond + [tableReferral['type'].eq(1)]))
        self.cmbArmyNumber.lineEdit().setCursorPosition(0)
        self.cmbReferralType.setTable('rbReferralType')
        self._updateEditable()
        self.edtCaseURL.setText(forceString(QtGui.qApp.preferences.appPrefs.get('edtCaseURL')))
        self.edtPixURL.setText(forceString(QtGui.qApp.preferences.appPrefs.get('edtPixURL')))
        self.edtGUID.setText(forceString(QtGui.qApp.preferences.appPrefs.get('edtGUID')))

    def postSetupUi(self):
        if QtGui.qApp.userHasAnyRight((urAdmin, urEventLock)):
            self.chkLock.setEnabled(True)
            self.lblLock.setEnabled(True)

        if not QtGui.qApp.isEventLockEnabled():
            self.chkLock.setVisible(False)
            self.lblLock.setVisible(False)

        self.setupReferral()
        self._updateEditable()

        EmkService.loggingConfigure(logToFile=False, textBrowser=self.txtBrowserIEMKCurrentLog)
        self.setConnections()
        self.loadIEMKHistory()

    def setConnections(self):
        self.btnSendCase.clicked.connect(self.sendCase)
        self.btnSendClient.clicked.connect(self.sendClient)
        self.btnCreateService.clicked.connect(self.createService)

    def loadIEMKHistory(self):
        db = QtGui.qApp.db
        if forceInt(self.lblEventIdValue.text()):
            eventId = forceInt(self.lblEventIdValue.text())
            logEventTable = db.table(loggerDbName+'.IEMKEventLog')
            logClientTable = db.table(loggerDbName+'.IEMKClientLog')

            self.txtBrowserIEMKHistoryLog.insertPlainText(u'Пациенты\n')
            records = db.getRecordList(table=logClientTable, where=logClientTable['client_id'].eq(QtGui.qApp.currentClientId()))
            for record in records:
                self.txtBrowserIEMKHistoryLog.insertPlainText(
                    'id: ' + forceString(record.value('id')) + '; ' +
                    'clientId: ' + forceString(record.value('client_id')) + '; ' +
                    'sendDate: ' + forceString(record.value('sendDate')) + '; ' +
                    'status: ' + forceString(record.value('status')) + '\n'
                )

            self.txtBrowserIEMKHistoryLog.insertPlainText(u'\nСлучаи\n')
            records = db.getRecordList(table=logEventTable, where=logEventTable['event_id'].eq(eventId))
            for record in records:
                self.txtBrowserIEMKHistoryLog.insertPlainText(
                    'id: ' + forceString(record.value('id')) + '; ' +
                    'eventId: ' + forceString(record.value('event_id')) + '; ' +
                    'sendDate: ' + forceString(record.value('sendDate')) + '; ' +
                    'status: ' + forceString(record.value('status')) + '\n'
                )

    @staticmethod
    def setId(widget, record, fieldName):
        value = forceString(record.value(fieldName))
        if value:
            text = unicode(value)
        else:
            text = ''
        widget.setText(text)

    @staticmethod
    def setDateTime(widget, record, fieldName):
        value = record.value(fieldName).toDateTime()
        if value:
            text = value.toString('dd.MM.yyyy hh:mm:ss')
        else:
            text = ''
        widget.setText(text)

    @staticmethod
    def setPerson(widget, record, fieldName):
        personId = forceRef(record.value(fieldName))
        if personId:
            record = QtGui.qApp.db.getRecord('vrbPersonWithSpeciality', 'code, name', personId)
            if record:
                text = forceString(record.value('code')) + ' | ' + forceString(record.value('name'))
            else:
                text = '{' + str(personId) + '}'
        else:
            text = ''
        widget.setText(text)

    def setNotes(self, record):
        self.edtPlannedDate.setDate(QtCore.QDate())
        self.edtDate.setDate(QtCore.QDate())
        self.cmbRelegateOrg.setValue(forceRef(record.value('relegateOrg_id')))
        self.setId(self.lblEventIdValue, record, 'id')
        self.setId(self.edtEventExternalIdValue, record, 'externalId')
        setRBComboBoxValue(self.cmbEventAssistant, record, 'assistant_id')
        setRBComboBoxValue(self.cmbEventCurator, record, 'curator_id')
        self.setDateTime(self.lblEventCreateDateTimeValue, record, 'createDatetime')
        self.setPerson(self.lblEventCreatePersonValue, record, 'createPerson_id')
        self.setDateTime(self.lblEventModifyDateTimeValue, record, 'modifyDatetime')
        self.setPerson(self.lblEventModifyPersonValue, record, 'modifyPerson_id')
        setTextEditValue(self.edtEventNote, record, 'note')
        setRBComboBoxValue(self.cmbPatientModel, record, 'patientModel_id')
        self.on_cmbPatientModel_currentIndexChanged(None)
        setRBComboBoxValue(self.cmbCureType, record, 'cureType_id')
        setRBComboBoxValue(self.cmbCureMethod, record, 'cureMethod_id')
        self._originalEventResultId = forceRef(record.value('result_id'))
        if QtGui.qApp.isReferralRequired():
            db = QtGui.qApp.db
            ref_id = forceInt(record.value('referral_id'))
            tableReferral = db.table('Referral')
            ref_record = db.getRecordEx(tableReferral, '*',
                                        [tableReferral['id'].eq(ref_id), tableReferral['isSend'].eq(0)])
            if ref_record:
                self.chkLPUReferral.setChecked(True)
                setLineEditValue(self.edtPerson, ref_record, 'person')
                self.edtNumber.setText(forceString(ref_record.value('number')))
                self.cmbRelegateOrg.setValue(forceRef(ref_record.value('relegateOrg_id')))
                self.cmbMKB.setText(forceString(ref_record.value('MKB')))
                self.cmbSpeciality.setValue(forceInt(ref_record.value('speciality_id')))
                self.cmbReferralType.setValue(forceInt(ref_record.value('type')))
                self.edtDate.setDate(forceDate(ref_record.value('date')))
                self.edtPlannedDate.setDate(forceDate(ref_record.value('hospDate')))
                if not ref_record.value('freeInput').isNull():
                    setLineEditValue(self.edtFreeInput, ref_record, 'freeInput')
                    self.chkFreeInput.setChecked(True)
                else:
                    self.edtFreeInput.setText('')
                    self.chkFreeInput.setChecked(False)
            else:
                self.chkLPUReferral.setChecked(False)
            armyRef_id = forceInt(record.value('armyReferral_id'))
            armyRef_record = db.getRecordEx(tableReferral, '*',
                                            [tableReferral['id'].eq(armyRef_id), tableReferral['type'].eq(1)])
            if armyRef_record:
                self.chkArmyReferral.setChecked(True)
                self.cmbArmyOrg.setValue(forceRef(armyRef_record.value('relegateOrg_id')))
                if not armyRef_record.value('freeInput').isNull():
                    setLineEditValue(self.edtArmyFreeInput, armyRef_record, 'freeInput')
                    self.chkArmyFreeInput.setChecked(True)
                else:
                    self.edtArmyFreeInput.setText('')
                    self.chkArmyFreeInput.setChecked(False)
                setDateEditValue(self.edtArmyDate, armyRef_record, 'date')
                self.cmbArmyNumber.setValue(forceInt(armyRef_record.value('id')))
            else:
                self.chkArmyReferral.setChecked(False)

        setRBComboBoxValue(self.cmbClientPolicy, record, 'clientPolicy_id')
        self.cmbClientPolicy.setPolicyFromRepresentative(
            isLittleStranger(forceRef(record.value('client_id')), forceDate(record.value('setDate')),
                             forceDate(record.value('execDate'))))
        self.updateClientPolicy(record)
        if QtGui.qApp.isEventLockEnabled():
            setCheckBoxValue(self.chkLock, record, 'locked')

    def updateClientPolicy(self, record):
        if record is None:
            self.cmbClientPolicy.updatePolicy()
            return

        execDate = forceDate(record.value('execDate'))
        eventIsClosed = not execDate.isNull()
        eventIsPayed = getRealPayed(forceInt(record.value('payStatus')))

        if eventIsPayed or (eventIsClosed and not QtGui.qApp.userHasRight(urEditClientPolicyInClosedEvent)):
            self.cmbClientPolicy.setEnabled(False)
        else:
            self.cmbClientPolicy.setEventIsClosed(eventIsClosed)
            self.cmbClientPolicy.setDate(execDate if eventIsClosed else QtCore.QDate.currentDate())

            if getEventFinanceCode(forceRef(record.value('eventType_id'))) == 3:  # ДМС
                franchisPolicyTypeId = forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', 'franchis', 'id'))
                if franchisPolicyTypeId:
                    self.cmbClientPolicy.setPolicyTypeId(franchisPolicyTypeId)
                    self.cmbClientPolicy.updatePolicy()
                    if not self.cmbClientPolicy.value():
                        self.cmbClientPolicy.setPolicyTypeId(
                            forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', '3', 'id')))
                        self.cmbClientPolicy.updatePolicy()
            else:
                self.cmbClientPolicy.updatePolicy()

    def setNotesEx(self, externalId, assistantId, curatorId, relegateOrgId, referrals=None):
        if not referrals:
            referrals = {}
        self.edtEventExternalIdValue.setText(externalId)
        self.cmbEventAssistant.setValue(assistantId)
        self.cmbEventCurator.setValue(curatorId)
        if QtGui.qApp.isReferralRequired():
            if 0 in referrals.keys():
                self.chkLPUReferral.setChecked(True)
                lpuRef = referrals[0]
                self.edtNumber.setText(forceString(lpuRef['number']))
                self.edtDate.setDate(lpuRef['date'])
                self.edtPlannedDate.setDate(lpuRef['hospDate'])
                self.cmbReferralType.setValue(lpuRef['type'])
                if lpuRef['person']:
                    self.edtPerson.setText(lpuRef['person'])
                if lpuRef['freeInput']:
                    self.chkFreeInput.setChecked(True)
                    self.edtFreeInput.setText(lpuRef['freeInput'])
                self.cmbSpeciality.setValue(lpuRef['speciality_id'])
                if lpuRef['MKB']:
                    self.cmbMKB.setText(lpuRef['MKB'])
            else:
                self.chkLPUReferral.setChecked(False)
            if 1 in referrals.keys():
                self.chkArmyReferral.setChecked(True)
                armyRef = referrals[1]
                self.cmbArmyNumber.setCurrentIndex(armyRef['number'][0])
                self.cmbArmyNumber.lineEdit().setText(QtCore.QString(armyRef['number'][1]))
                self.edtArmyDate.setDate(armyRef['date'])
                if armyRef['relegateOrg_id']:
                    self.cmbArmyOrg.setValue(armyRef['relegateOrg_id'])
                if armyRef['freeInput']:
                    self.edtArmyFreeInput.setText(armyRef['freeInput'])
                    self.chkArmyFreeInput.setChecked(True)
                    self.edtArmyFreeInput.setEnabled(True)
                else:
                    self.chkArmyFreeInput.setChecked(False)
                    self.edtArmyFreeInput.setEnabled(False)
            else:
                self.chkArmyReferral.setChecked(False)
        self.cmbRelegateOrg.setValue(relegateOrgId)
        self.updateClientPolicy(None)

    def enableEditors(self, eventTypeId):
        self.edtEventExternalIdValue.setEnabled(bool(getEventIsExternal(eventTypeId)))
        self.cmbEventAssistant.setEnabled(hasEventAssistant(eventTypeId))
        self.cmbEventCurator.setEnabled(hasEventCurator(eventTypeId))

    def getNotes(self, record, eventTypeId):
        db = QtGui.qApp.db
        tbl = db.table('Referral')
        record.setValue('relegateOrg_id', toVariant(self.cmbRelegateOrg.value()))
        getTextEditValue(self.edtEventNote, record, 'note')
        if getEventIsExternal(eventTypeId):
            getLineEditValue(self.edtEventExternalIdValue, record, 'externalId')
        if hasEventAssistant(eventTypeId):
            getRBComboBoxValue(self.cmbEventAssistant, record, 'assistant_id')
        if hasEventCurator(eventTypeId):
            getRBComboBoxValue(self.cmbEventCurator, record, 'curator_id')
        getRBComboBoxValue(self.cmbPatientModel, record, 'patientModel_id')
        getRBComboBoxValue(self.cmbCureType, record, 'cureType_id')
        getRBComboBoxValue(self.cmbCureMethod, record, 'cureMethod_id')
        getRBComboBoxValue(self.cmbClientPolicy, record, 'clientPolicy_id')
        if QtGui.qApp.isEventLockEnabled():
            getCheckBoxValue(self.chkLock, record, 'locked')
        refId = db.translate('Event', 'id', forceInt(record.value('id')), 'referral_id')
        if not refId:
            refId = db.translate('Referral', 'event_id', forceInt(record.value('id')), 'id')
        if QtGui.qApp.isReferralRequired() and not self.dontSaveReferral:
            if self.chkLPUReferral.isChecked() and not forceInt(refId):
                if not forceString(self.edtNumber.text()):
                    QtGui.QMessageBox.warning(self, u'Ошибка', u'Заполните номер направления')
                    return
                ref_record = db.getRecordEx(tbl, '*', [tbl['type'].eq(forceInt(self.cmbReferralType.value())),
                                                       tbl['number'].eq(forceString(self.edtNumber.text())),
                                                       tbl['client_id'].eq(forceInt(
                                                           self._clientId if self._clientId else QtGui.qApp.currentClientId())),
                                                       tbl['date'].eq(self.edtDate.date()),
                                                       tbl['isCancelled'].eq(0),
                                                       tbl['deleted'].eq(0)])
                if not ref_record:
                    ref_record = tbl.newRecord()
                ref_record.setValue('number', QtCore.QVariant(self.edtNumber.text()))
                ref_record.setValue('event_id', QtCore.QVariant(forceInt(record.value('id')) if forceInt(record.value('id')) else self.lblEventIdValue.text()))
                ref_record.setValue('relegateOrg_id', QtCore.QVariant(self.cmbRelegateOrg.value()))
                ref_record.setValue('client_id',
                                    QtCore.QVariant(self._clientId if self._clientId else QtGui.qApp.currentClientId()))
                ref_record.setValue('MKB', QtCore.QVariant(self.cmbMKB.text()))
                ref_record.setValue('speciality_id', QtCore.QVariant(self.cmbSpeciality.value()))
                ref_record.setValue('type', QtCore.QVariant(self.cmbReferralType.value()))
                getDateEditValue(self.edtDate, ref_record, 'date')
                getDateEditValue(self.edtPlannedDate, ref_record, 'hospDate')
                getLineEditValue(self.edtPerson, ref_record, 'person')
                if self.chkFreeInput.isChecked():
                    getLineEditValue(self.edtFreeInput, ref_record, 'freeInput')
                referralId = db.insertOrUpdate(db.table('Referral'), ref_record)
                record.setValue('referral_id', toVariant(referralId))
            elif forceInt(refId):
                if not forceString(self.edtNumber.text()):
                    QtGui.QMessageBox.warning(self, u'Ошибка', u'Заполните номер направления')
                    return
                record.setValue('referral_id', toVariant(refId))
                ref_record = db.getRecordEx(tbl, '*', [tbl['id'].eq(refId), tbl['isSend'].eq(0)])
                if ref_record and not forceInt(ref_record.value('isSend')):
                    if self.chkLPUReferral.isChecked():
                        if ref_record:
                            ref_record.setValue('number', QtCore.QVariant(self.edtNumber.text()))
                            ref_record.setValue('event_id', QtCore.QVariant(forceInt(record.value('id')) if forceInt(record.value('id')) else self.lblEventIdValue.text()))
                            ref_record.setValue('relegateOrg_id', QtCore.QVariant(self.cmbRelegateOrg.value()))
                            ref_record.setValue('client_id', QtCore.QVariant(
                                self._clientId if self._clientId else QtGui.qApp.currentClientId()))
                            ref_record.setValue('MKB', QtCore.QVariant(self.cmbMKB.text()))
                            ref_record.setValue('speciality_id', QtCore.QVariant(self.cmbSpeciality.value()))
                            ref_record.setValue('type', QtCore.QVariant(self.cmbReferralType.value()))
                            ref_record.setValue('date', QtCore.QVariant(self.edtDate.date()))
                            ref_record.setValue('hospDate', QtCore.QVariant(self.edtPlannedDate.date()))
                            ref_record.setValue('person', QtCore.QVariant(self.edtPerson.text()))
                            db.updateRecord(tbl, ref_record)
                    else:
                        record.setValue('referral_id', QtCore.QVariant())
            else:
                record.setValue('referral_id', QtCore.QVariant())

            if self.chkArmyReferral.isChecked():
                armyCond = [tbl['number'].eq(self.cmbArmyNumber.text()),
                            tbl['id'].eq(self.cmbArmyNumber.value())]
                army_ref_record = db.getRecordEx(tbl, '*', where=armyCond)
                if not army_ref_record:
                    army_ref_record = tbl.newRecord()
                    new = True
                else:
                    new = False
                army_ref_record.setValue('number', QtCore.QVariant(self.cmbArmyNumber.lineEdit().text()))
                army_ref_record.setValue('client_id', QtCore.QVariant(
                    self._clientId if self._clientId else QtGui.qApp.currentClientId()))
                army_ref_record.setValue('type', QtCore.QVariant(1))
                army_ref_record.setValue('relegateOrg_id', QtCore.QVariant(self.cmbArmyOrg.value()))
                getDateEditValue(self.edtArmyDate, army_ref_record, 'date')
                if self.chkArmyFreeInput.isChecked():
                    getLineEditValue(self.edtArmyFreeInput, army_ref_record, 'freeInput')
                if new:
                    referralId = db.insertRecord(db.table('Referral'), army_ref_record)
                else:
                    referralId = db.updateRecord(db.table('Referral'), army_ref_record)
                record.setValue('armyReferral_id', toVariant(referralId))
                self.cmbArmyNumber.forceUpdate()
            else:
                record.setValue('armyReferral_id', QtCore.QVariant())

    # Copied from PreCreateEventDialog
    def generateExternalIdByEventType(self, eventTypeId):
        counterId = getEventCounterId(eventTypeId)
        prefix = getEventPrefix(eventTypeId)
        return self.generateExternalId(counterId, prefix)

    def generateExternalIdByEventResult(self, eventTypeId, resultId):
        counterId = forceRef(QtGui.qApp.db.translate('rbResult', 'id', resultId, 'counter_id'))
        prefix = getEventPrefix(eventTypeId)
        return self.generateExternalId(counterId, prefix)

    def generateExternalId(self, counterId, prefix):
        if counterId:
            try:
                clientId = self._clientId if self._clientId else QtGui.qApp.currentClientId()
                externalId = getDocumentNumber(clientId, counterId)
                if prefix:
                    externalId = ''.join([prefix, externalId])
                self.edtEventExternalIdValue.setText(externalId)
            except Exception, e:
                QtGui.QMessageBox.critical(QtGui.qApp.mainWindow,
                                           u'Внимание!',
                                           u'Произошла ошибка при получении значения счетчика!\n%s' % e,
                                           QtGui.QMessageBox.Ok)
                return -1
        return 1

    def checkUniqueEventExternalId(self, eventId):
        if self._externalIdIsChanged:
            externalId = forceStringEx(self.edtEventExternalIdValue.text())
            if externalId:
                sameExternalIdListInfo = checkUniqueEventExternalId(externalId, eventId)
                if sameExternalIdListInfo:
                    return sameExternalIdListInfo

        return []

    def checkOrGenerateUniqueEventExternalId(self, eventId, eventTypeId):
        uniqueExternalIdRequired = getUniqueExternalIdRequired(eventTypeId)
        counterType = getCounterType(eventTypeId)
        externalId = forceStringEx(self.edtEventExternalIdValue.text())
        if counterType == 0 and not externalId and getEventIsExternal(eventTypeId) == 2:
            return -2
        if self._externalIdIsChanged:
            return not uniqueExternalIdRequired or self.checkUniqueEventExternalId(eventId)
        elif not forceString(self.edtEventExternalIdValue.text()) and counterType == 2 and not eventId:
            return self.generateExternalIdByEventType(eventTypeId)
        elif counterType == 3 and self._eventResultId and self._eventResultId != self._originalEventResultId:
            return self.generateExternalIdByEventResult(eventTypeId, self._eventResultId)

    def updateReferralPeriod(self, date):
        db = QtGui.qApp.db
        tableReferral = db.table('Referral')
        cond = [tableReferral['date'].ge(date.addMonths(-1)),
                tableReferral['date'].le(date)]
        clientId = self._clientId if self._clientId else QtGui.qApp.currentClientId()
        if clientId:
            cond.append('client_id=%d' % clientId)
        self.cmbArmyNumber.setFilter(db.joinAnd(cond + [tableReferral['type'].eq(1)]))

    @QtCore.pyqtSlot()
    def on_btnSelectRelegateOrg_clicked(self):
        orgId = selectOrganisation(self, self.cmbRelegateOrg.value(), False, filter=CPolyclinicComboBox._filter)
        self.cmbRelegateOrg.update()
        if orgId:
            self.cmbRelegateOrg.setValue(orgId)

    @QtCore.pyqtSlot()
    def on_btnSelectArmyOrg_clicked(self):
        orgId = selectOrganisation(self, self.cmbArmyOrg.value(), False, filter=CArmyOrgComboBox._filter)
        self.cmbArmyOrg.update()
        if orgId:
            self.cmbArmyOrg.setValue(orgId)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtEventExternalIdValue_textEdited(self, value):
        self._externalIdIsChanged = True

    def setEventEditor(self, eventEditor):
        self.cmbPatientModel.setEventEditor(eventEditor)

    @QtCore.pyqtSlot(int)
    def on_cmbPatientModel_currentIndexChanged(self, index):
        patientModelId = self.cmbPatientModel.value()
        db = QtGui.qApp.db
        tablePatientModelItem = db.table('rbPatientModel_Item')
        cond = [tablePatientModelItem['master_id'].eq(patientModelId)]
        cureTypeIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureType_id']], cond)
        if cureTypeIdList:
            self.cmbCureType.setFilter(
                'rbCureType.id IN (%s)' % (u','.join(str(cureTypeId) for cureTypeId in cureTypeIdList if cureTypeId)))
            cureTypeId = self.cmbCureType.value()
            cond = [tablePatientModelItem['cureType_id'].eq(cureTypeId),
                    tablePatientModelItem['master_id'].eq(patientModelId)]
            cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                    cond)
            if cureMethodIdList:
                self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s)' % (
                u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
            else:
                cond = [tablePatientModelItem['master_id'].eq(patientModelId)]
                cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                        cond)
                if cureMethodIdList:
                    self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s)' % (
                    u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
                else:
                    self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
            self.cmbCureMethod.setCurrentIndex(0)
        else:
            self.cmbCureType.setFilter('rbCureType.id IS NULL')
        self.cmbCureType.setCurrentIndex(0)

    @QtCore.pyqtSlot(int)
    def on_cmbCureType_currentIndexChanged(self, index):
        db = QtGui.qApp.db
        cureTypeId = self.cmbCureType.value()
        patientModelId = self.cmbPatientModel.value()
        tablePatientModelItem = db.table('rbPatientModel_Item')
        if cureTypeId:
            cond = [tablePatientModelItem['cureType_id'].eq(cureTypeId),
                    tablePatientModelItem['master_id'].eq(patientModelId)]
            cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                    cond)
            if cureMethodIdList:
                self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s)' % (
                u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
            else:
                self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
        elif patientModelId:
            cond = [tablePatientModelItem['master_id'].eq(patientModelId)]
            cureMethodIdList = db.getDistinctIdList(tablePatientModelItem, [tablePatientModelItem['cureMethod_id']],
                                                    cond)
            if cureMethodIdList:
                self.cmbCureMethod.setFilter('rbCureMethod.id IN (%s)' % (
                u','.join(str(cureMethodId) for cureMethodId in cureMethodIdList if cureMethodId)))
            else:
                self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
        else:
            self.cmbCureMethod.setFilter('rbCureMethod.id IS NULL')
        self.cmbCureMethod.setCurrentIndex(0)

    def getExternalId(self):
        return forceString(self.edtEventExternalIdValue.text())

    @QtCore.pyqtSlot(bool)
    def on_chkFreeInput_toggled(self, checked):
        if checked:
            self.edtFreeInput.setEnabled(True)
        else:
            self.edtFreeInput.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def on_chkArmyFreeInput_toggled(self, checked):
        if checked:
            self.edtArmyFreeInput.setEnabled(True)
        else:
            self.edtArmyFreeInput.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_cmbArmyNumber_currentIndexChanged(self, index):
        if index == 0:
            self.cmbArmyNumber.lineEdit().setCursorPosition(0)
            self.edtArmyFreeInput.setText('')
            self.edtArmyDate.setDate(QtCore.QDate.currentDate())
            if not QtGui.qApp.userHasRight(urCreateReferral):
                self.enableArmyReferral(False)
                return
        else:
            db = QtGui.qApp.db
            tbl = db.table('Referral')
            cond = [tbl['id'].eq(self.cmbArmyNumber.value()),
                    tbl['type'].eq(1)]
            record = db.getRecordEx(tbl, '*', where=cond)
            if record:
                setLineEditValue(self.cmbArmyNumber.lineEdit(), record, 'number')
                if not record.value('freeInput').isNull():
                    setLineEditValue(self.edtArmyFreeInput, record, 'freeInput')
                    self.chkArmyFreeInput.setChecked(True)
                else:
                    self.edtArmyFreeInput.setText('')
                    self.chkArmyFreeInput.setChecked(False)
                setDateEditValue(self.edtArmyDate, record, 'date')
                self.cmbArmyOrg.setValue(record.value('relegateOrg_id'))
            else:
                return
        self.enableArmyReferral(True)

    @QtCore.pyqtSlot(bool)
    def on_chkLPUReferral_toggled(self, checked):
        self.cmbReferralType.setVisible(checked)
        self.lblRefType.setVisible(checked)
        self.edtDate.setVisible(checked)
        self.lblDate.setVisible(checked)
        self.edtPlannedDate.setVisible(checked)
        self.lblPlannedDate.setVisible(checked)
        self.edtNumber.setVisible(checked)
        self.lblNumber.setVisible(checked)
        self.edtFreeInput.setVisible(checked)
        self.chkFreeInput.setVisible(checked)
        self.edtPerson.setVisible(checked)
        self.lblPerson.setVisible(checked)
        self.cmbSpeciality.setVisible(checked)
        self.lblSpeciality.setVisible(checked)
        self.cmbMKB.setVisible(checked)
        self.lblDiagnosis.setVisible(checked)
        self.cmbRelegateOrg.setVisible(checked)
        self.btnSelectRelegateOrg.setVisible(checked)
        self.lblRelegateOrg.setVisible(checked)
        self.useLPURef = checked

    @QtCore.pyqtSlot(bool)
    def on_chkArmyReferral_toggled(self, checked):
        self.edtArmyDate.setVisible(checked)
        self.lblArmyDate.setVisible(checked)
        self.cmbArmyNumber.setVisible(checked)
        self.lblArmyNumber.setVisible(checked)
        self.edtArmyFreeInput.setVisible(checked)
        self.lblArmyFreeInput.setVisible(checked)
        self.btnSelectArmyOrg.setVisible(checked)
        self.cmbArmyOrg.setVisible(checked)
        self.chkArmyFreeInput.setVisible(checked)
        self.useArmyRef = checked

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDate_dateChanged(self, date):
        if date > QtCore.QDate.currentDate():
            QtGui.QMessageBox.critical(self, u'Ошибка', u'Дата направления не может превышать текущую.',
                                       QtGui.QMessageBox.Close)

    def setupReferral(self):
        if QtGui.qApp.isReferralRequired():
            self.cmbReferralType.setVisible(True)
            self.lblRefType.setVisible(True)
            self.edtDate.setVisible(True)
            self.edtDate.setEnabled(True)
            self.edtPlannedDate.setVisible(True)
            self.edtPlannedDate.setEnabled(True)
            self.lblDate.setVisible(True)
            self.lblPlannedDate.setVisible(True)
            self.lblPlannedDate.setVisible(True)
            self.edtNumber.setVisible(True)
            self.edtNumber.setEnabled(True)
            self.lblNumber.setVisible(True)
            self.edtFreeInput.setVisible(True)
            self.chkFreeInput.setVisible(True)
            self.chkFreeInput.setEnabled(True)
            self.edtPerson.setVisible(True)
            self.edtPerson.setEnabled(True)
            self.lblPerson.setVisible(True)
            self.cmbSpeciality.setVisible(True)
            self.cmbSpeciality.setEnabled(True)
            self.lblSpeciality.setVisible(True)
            self.cmbMKB.setVisible(True)
            self.cmbMKB.setEnabled(True)
            self.lblDiagnosis.setVisible(True)
            self.on_chkLPUReferral_toggled(self.chkLPUReferral.isChecked())
            self.on_chkArmyReferral_toggled(self.chkArmyReferral.isChecked())
            if not QtGui.qApp.userHasRight(urCreateReferral):
                self.enableReferral(False)
                self.enableArmyReferral(False)
        else:
            self.cmbReferralType.setVisible(False)
            self.lblRefType.setVisible(False)
            self.edtDate.setVisible(False)
            self.edtDate.setEnabled(False)
            self.lblPlannedDate.setVisible(False)
            self.edtPlannedDate.setVisible(False)
            self.edtPlannedDate.setEnabled(False)
            self.lblDate.setVisible(False)
            self.edtNumber.setVisible(False)
            self.edtNumber.setEnabled(False)
            self.lblNumber.setVisible(False)
            self.edtFreeInput.setVisible(False)
            self.chkFreeInput.setVisible(False)
            self.chkFreeInput.setEnabled(False)
            self.edtPerson.setVisible(False)
            self.edtPerson.setEnabled(False)
            self.lblPerson.setVisible(False)
            self.cmbSpeciality.setVisible(False)
            self.cmbSpeciality.setEnabled(False)
            self.lblSpeciality.setVisible(False)
            self.cmbMKB.setVisible(False)
            self.cmbMKB.setEnabled(False)
            self.lblDiagnosis.setVisible(False)
            self.lblArmyDate.setVisible(False)
            self.edtArmyDate.setVisible(False)
            self.lblArmyNumber.setVisible(False)
            self.cmbArmyNumber.setVisible(False)
            self.edtArmyFreeInput.setVisible(False)
            self.lblArmyFreeInput.setVisible(False)
            self.cmbArmyOrg.setVisible(False)
            self.btnSelectArmyOrg.setVisible(False)
            self.chkArmyFreeInput.setVisible(False)
            self.chkLPUReferral.setChecked(False)
            self.chkLPUReferral.setVisible(False)
            self.chkArmyReferral.setChecked(False)
            self.chkArmyReferral.setVisible(False)

    def enableReferral(self, state):
        self.cmbSpeciality.setEnabled(state)
        self.cmbMKB.setEnabled(state)
        self.cmbRelegateOrg.setEnabled(state)
        self.edtDate.setEnabled(state)
        self.edtPerson.setEnabled(state)
        self.chkFreeInput.setEnabled(state)

    def enableArmyReferral(self, state):
        self.edtArmyDate.setEnabled(state)
        self.edtArmyFreeInput.setEnabled(state)
        self.chkArmyFreeInput.setEnabled(state)
        self.cmbArmyOrg.setEnabled(state)
        self.btnSelectArmyOrg.setEnabled(state)

    def setClientId(self, clientId):
        self._clientId = clientId
        self.cmbClientPolicy.setClientId(clientId)

    def setEventResultId(self, resultId):
        self._eventResultId = resultId


class CEventNotesPage(CFastEventNotesPage):
    def __init__(self, parent=None):
        CFastEventNotesPage.__init__(self, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        self.setupUiMini(self)
        self.setupUi(self)
        self.postSetupUiMini()
        self.postSetupUi()
