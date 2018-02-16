# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""
Форма 25Тр: нечто для травмы.
"""
import codecs
from PyQt4 import QtCore, QtGui

from Events.EventEditDialog import CEventEditDialog
from Events.Utils import EventOrder, checkDiagnosis, getDiagnosisId2, getEventShowTime, getMKBName
from Orgs.Utils import getPersonInfo
from Registry.Utils import getClientInfoEx
from Ui_F025Tr import Ui_Dialog
from Users.Rights import urAdmin, urRegTabWriteRegistry, urEventLock
from library.PrintTemplates import applyTemplateInt
from library.Utils import forceInt, forceRef, forceString, forceStringEx, toVariant
from library.crbcombobox import CRBComboBox
from library.interchange import getDatetimeEditValue, getLineEditValue, getRBComboBoxValue, \
    setDatetimeEditValue, setLineEditValue, setRBComboBoxValue, \
    getCheckBoxValue, setCheckBoxValue


class CF025TrDialog(CEventEditDialog, Ui_Dialog):
    defaultMKB = 'Z04.1'
    defaultOrder = 2

    def __init__(self, parent):
        CEventEditDialog.__init__(self, parent)
        self.diagnosticRecord = None
        self.availableDiagnostics = []
        self.mapSpecialityIdToDiagFilter = {}

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'"Карточка травматика" Ф.025')

        if not QtGui.qApp.isEventLockEnabled():
            self.lblLock.setVisible(False)
            self.chkLock.setVisible(False)
        elif QtGui.qApp.userHasAnyRight((urAdmin, urEventLock)):
            self.chkLock.setEnabled(True)

        self.cmbTraumaType.setTable('rbTraumaType', False)

        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))

        self.setupDirtyCather()
        self.setIsDirty(False)

        self.cmbResult.setShowFields(CRBComboBox.showCodeAndName)

    @property
    def eventSetDateTime(self):
        return QtCore.QDateTime(self.edtBegDate.date(), self.edtBegTime.time())

    @eventSetDateTime.setter
    def eventSetDateTime(self, value):
        if isinstance(value, QtCore.QDate):
            self.edtBegDate.setDate(value)
            self.edtBegTime.setTime(QtCore.QTime())
        elif isinstance(value, QtCore.QDateTime):
            self.edtBegDate.setDate(value.date())
            self.edtBegTime.setTime(value.time())

    @property
    def eventDate(self):
        return self.edtEndDate.date()

    @eventDate.setter
    def eventDate(self, value):
        if isinstance(value, QtCore.QDate):
            self.edtEndDate.setDate(value)
            self.edtEndTime.setTime(QtCore.QTime())
        elif isinstance(value, QtCore.QDateTime):
            self.edtEndDate.setDate(value.date())
            self.edtEndTime.setTime(value.time())

    def exec_(self):
        result = CEventEditDialog.exec_(self)
        if result:
                self.print_()
        return result

    def prepare(self, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                externalId, assistantId, curatorId, flagHospitalization=False, actionTypeIdValue=None,
                valueProperties=None, tissueTypeId=None, selectPreviousActions=False, relegateOrgId=None, diagnos=None,
                financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                recommendationList=None, useDiagnosticsAndActionsPresets=True, orgStructureId=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setEventTypeId(eventTypeId)
        self.edtCardNo.setText(self.getNextCardNo(eventTypeId))
        self.setClientId(clientId)
        self.setPersonId(personId)
        self.setOrgStructureId(orgStructureId)
        self.cmbOrder.setCode(self.defaultOrder)
        self.edtMKB.setText(self.defaultMKB)
        self.diagnosticRecord = None
        self.initFocus()
        self.setIsDirty(False)
        return True

    def setLeavedAction(self, actionTypeIdValue):
        pass

    def initFocus(self):
        pass

    def getNextCardNo(self, eventTypeId):
        db = QtGui.qApp.db
        table = db.table('Event')
        lastEvent = db.getRecordEx(table, 'externalId', table['eventType_id'].eq(eventTypeId), 'id DESC')
        if lastEvent:
            return str(forceInt(lastEvent.value(0))+1)
        else:
            return '1'

    def setRecord(self, record):
        CEventEditDialog.setRecord(self, record)
        setLineEditValue(self.edtCardNo,        record, 'externalId')
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate')
        setRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        setRBComboBoxValue(self.cmbResult,      record, 'result_id')
        # setComboBoxValue(self.cmbOrder,         record, 'order')
        self.cmbOrder.setCode(forceString(record.value('order')))
        setCheckBoxValue(self.chkLock, record, 'locked')
        self.setPersonId(self.cmbPerson.value())
        self.loadDiagnostics()
        self.initFocus()
        self.setIsDirty(False)
        self.setEditable(self.getEditable())

    def loadDiagnostics(self):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        tablePerson = db.table('Person')
        record = db.getRecordEx(table, '*', [table['deleted'].eq(0), table['event_id'].eq(self.itemId())], 'id')
        if record:
            traumaTypeId = forceRef(record.value('traumaType_id'))
            diagnosisId = record.value('diagnosis_id')
            MKB   = forceString(db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKB'))
            MKBEx = forceString(db.translate('Diagnosis', 'id', forceRef(diagnosisId), 'MKBEx'))
            self.diagnosticRecord = record
        else:
            traumaTypeId = None
            MKB = self.defaultMKB
            MKBEx = ''
            self.diagnosticRecord = None
        self.cmbTraumaType.setValue(traumaTypeId)
        self.edtMKB.setText(MKB)
        self.edtMKBEx.setText(MKBEx)

    def getModelFinalDiagnostics(self):
        return None

    def getRecord(self):
        record = CEventEditDialog.getRecord(self)
        showTime = getEventShowTime(self.eventTypeId)

        getLineEditValue(self.edtCardNo,        record, 'externalId')
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'setDate', showTime)
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'execDate', showTime)
        getRBComboBoxValue(self.cmbPerson,      record, 'execPerson_id')
        getRBComboBoxValue(self.cmbResult,      record, 'result_id')
        # getComboBoxValue(self.cmbOrder,         record, 'order')
        record.setValue('order', toVariant(self.cmbOrder.code()))
        getCheckBoxValue(self.chkLock, record, 'locked')
        return record

    def saveInternals(self, eventId):
        self.saveDiagnostic(eventId)

    def saveDiagnostic(self, eventId):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')

        if not self.diagnosticRecord:
            self.diagnosticRecord = table.newRecord()
            self.diagnosticRecord.setValue('event_id', toVariant(eventId))

        record = self.diagnosticRecord
        diagnosisTypeId = self.getDiagnosisTypeId()
        characterId     = self.getCharacterId()
        dispanserId     = None
        traumaTypeId    = self.cmbTraumaType.value()
        resultId        = self.cmbResult.value()

        MKB    = forceString(self.edtMKB.text())
        MKBEx  = forceString(self.edtMKBEx.text())

        diagnosisId, characterId = getDiagnosisId2(
            self.eventDate,
            self.personId,
            self.clientId,
            diagnosisTypeId,
            MKB,
            MKBEx,
            characterId,
            dispanserId,
            traumaTypeId,
            forceRef(record.value('diagnosis_id')),
            forceRef(record.value('id')))

        record.setValue('diagnosisType_id', toVariant(diagnosisTypeId))
        record.setValue('speciality_id', toVariant(self.personSpecialityId))
        record.setValue('person_id', toVariant(self.personId) )
        record.setValue('setDate', toVariant(self.eventDate) )
        record.setValue('endDate', toVariant(self.eventDate) )
        record.setValue('diagnosis_id',  toVariant(diagnosisId))
        record.setValue('character_id',  toVariant(characterId))
        record.setValue('traumaType_id', toVariant(traumaTypeId))
        record.setValue('result_id',    toVariant(resultId))
        db.insertOrUpdate(table, record)
        self.modifyDiagnosises([(MKB, diagnosisId)])

    def setOrgId(self, orgId):
        self.orgId = orgId
        self.cmbPerson.setOrgId(orgId)

    def setEventTypeId(self, eventTypeId):
        CEventEditDialog.setEventTypeId(self, eventTypeId, u'Ф.025Тр')
        showTime = getEventShowTime(eventTypeId)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        self.cmbResult.setTable('rbResult', False, 'eventPurpose_id=\'%d\'' % self.eventPurposeId)

    def getTemplate(self):
        import os.path
        templateFileName   = 'F25Tr.html'
        fullPath = os.path.join(QtGui.qApp.getTemplateDir(), templateFileName)
        for enc in ['utf-8', 'cp1251']:
            try:
                file = codecs.open(fullPath, encoding=enc, mode='r')
                return file.read()
            except:
                pass
        return \
            u'<HTML><BODY>' \
            u'<HR>' \
            u'<CENTER>КАРТОЧКА ТРАВМAТИКА № {cardNo}</CENTER>' \
            u'<HR>' \
            u'код: {client.id}&nbsp;<FONT FACE="Code 3 de 9" SIZE=+3>*{client.id}*</FONT><BR/>' \
            u'ФИО: <B>{client.fullName}</B><BR/>' \
            u'ДР:  <B>{client.birthDate}</B>(<B>{client.age}</B>),&nbsp;Пол: <B>{client.sex}</B>,&nbsp;СНИЛС:<B>{client.SNILS}</B><BR/>' \
            u'Док: <B>{client.document}</B><BR/>' \
            u'Полис:<B>{client.policy}</B><BR/>' \
            u'<HR>' \
            u'Врач: <B>{person.fullName}</B>(<B>{person.specialityName}</B>)<BR>' \
            u'Порядок поступления: <B>{order}</B><BR>' \
            u'Тип травмы: <B>{traumaType}</B><BR>' \
            u'обстоятельства: <B>{MKBEx}</B>(<B>{MKBExName}</B>)<BR>' \
            u'</BODY></HTML>'

    def getEventInfo(self):
        result = {}
        result['person'] = getPersonInfo(self.personId)
        result['cardNo'] = forceString(self.edtCardNo.text())
        result['order']  = EventOrder.getName(self.cmbOrder.currentIndex())
        result['traumaType']  = forceString(self.cmbTraumaType.currentText())
        result['MKB']       = forceString(self.edtMKB.text())
        result['MKBName']   = getMKBName(result['MKB'])
        result['MKBEx']     = forceString(self.edtMKBEx.text())
        result['MKBExName'] = getMKBName(result['MKBEx'])
        result['date']  = forceString(self.eventDate)
        result['client'] = getClientInfoEx(self.clientId, self.eventDate)
        return result

    def print_(self):
        eventInfo = self.getEventInfo()
        template = self.getTemplate()
        applyTemplateInt(self, u'карточка травматика', template, eventInfo)

    def checkDataEntered(self):
        result = CEventEditDialog.checkDataEntered(self)
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck else QtCore.QDate()
        result = result and (forceStringEx(self.edtCardNo) or self.checkInputMessage(u'номер карты', False, self.edtCardNo))
        result = result and (not begDate.isNull() or self.checkInputMessage(u'дату происшествия', False, self.edtBegDate))
        result = result and (not endDate.isNull() or self.checkInputMessage(u'дату обращения',    False, self.edtEndDate))
        result = result and (self.cmbPerson.value()   or self.checkInputMessage(u'врач',        False, self.cmbPerson))
        result = result and (self.cmbOrder.currentIndex() or self.checkInputMessage(u'порядок поступления', False, self.cmbOrder))
        result = result and (self.cmbTraumaType.value()   or self.checkInputMessage(u'тип травмы',          False, self.cmbTraumaType))
        result = result and self.checkDiagnosticDataEntered()
        # result = result and (self.cmbResult.value()   or self.checkInputMessage(u'результат',   False, self.cmbResult))
        return result

    def checkDiagnosticDataEntered(self):
        result = True
        MKB    = forceString(self.edtMKB.text())
        MKBEx  = forceString(self.edtMKBEx.text())
        result = result and (MKB or self.checkInputMessage(u'диагноз', False, self.edtMKB))
        if result:
            result = self.checkDiagnosis(MKB)
            if not result:
                self.edtMKB.setFocus(QtCore.Qt.OtherFocusReason)
                self.edtMKB.update()
        result = result and (MKBEx or self.checkInputMessage(u'обстоятельства',   False, self.edtMKBEx))
        if result:
            result = self.checkDiagnosis(MKBEx)
            if not result:
                self.edtMKBEx.setFocus(QtCore.Qt.OtherFocusReason)
                self.edtMKBEx.update()
        return result

    def getDiagFilter(self):
        specialityId = self.personSpecialityId
        result = self.mapSpecialityIdToDiagFilter.get(specialityId, None)
        if result == None:
            result = QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'mkbFilter')
            if result == None:
                result = ''
            else:
                result = forceString(result)
            self.mapSpecialityIdToDiagFilter[specialityId] = forceString(result)
        return result

    def checkDiagnosis(self, MKB, isEx=False):
        diagFilter = self.getDiagFilter()
        return checkDiagnosis(self, MKB, diagFilter, self.clientId, self.clientSex, self.clientAge, self.begDate(), self.endDate(), self.eventTypeId, isEx)

    def getDiagnosisTypeId(self):
        return forceRef(QtGui.qApp.db.translate('rbDiagnosisType', 'code', '90', 'id'))

    def getCharacterId(self):
        return forceRef(QtGui.qApp.db.translate('rbDiseaseCharacter', 'code', '1', 'id'))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.updateModelsRetiredList()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(self.eventDate)
        if QtGui.qApp.isAutoClosed():
            self.chkIsClosed.setChecked(date != QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        self.setPersonId(self.cmbPerson.value())

    def setEditable(self, editable):
        for widget in (self.edtCardNo, self.edtBegDate, self.edtBegTime, self.edtEndDate, self.edtEndTime,
                       self.cmbPerson, self.cmbOrder, self.cmbTraumaType, self.edtMKB, self.edtMKBEx, self.cmbResult):
            widget.setEnabled(editable)
