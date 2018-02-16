# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils import checkUniqueEventExternalId, getCounterType, getEventCode, getEventCounterId, getEventDateInput, getEventIsExternal, \
    getEventIsTakenTissue, getEventPrefix, getEventShowTime, getEventType, getEventTypeForm, getMKBList, getOrgStructureEventTypeFilter, \
    getUniqueExternalIdRequired, getWorkEventTypeFilter, hasEventAssistant, hasEventCurator, isEventLong, isEventStationary, isEventTypeResetSetDate
from GUIHider.VisibleControlMixin import CVisibleControlMixin
from Orgs.OrgComboBox import CArmyOrgComboBox, CPolyclinicComboBox
from Orgs.Orgs import selectOrganisation
from Orgs.Utils import getOrgStructureName, getPersonOrgId, getPersonOrgStructureOnDate
from Registry.Utils import getClientAttachOrgStructure
from Ui_PreCreateEventDialog import Ui_PreCreateEventDialog
from Users.Rights import urCreateReferral
from library.Counter import getDocumentNumber
from library.DialogBase import CDialogBase
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, getPref, getVal, \
    setPref, forceDecimal
from library.interchange import setDateEditValue, setLineEditValue


class CPreCreateEventDialog(CDialogBase, Ui_PreCreateEventDialog, CVisibleControlMixin):
    _orgId = None
    _relegateOrgId = None
    _clientId = None
    _eventTypeId = None
    _personId = None
    _assistantId = None
    _curatorId = None
    _eventSetDate = None
    _eventDate = None
    _addVisits = False
    _includeRedDays = False
    _tissueTypeId = None
    _selectPreviousActions = False
    _connected = False
    _referralNumber = None
    _referralDate = None
    _referralPerson = None
    _referralFreeInput = None
    _referralMKB = None
    _referralType = None
    _armyReferralNumber = None
    _armyReferralDate = None
    _armyReferralFreeInput = None
    isAppointment = False
    isRecreated = False

    def __init__(self, parent, eventTypeFilterHospitalization=None, dateTime=None, personId=None, orgStructureId=None, externalId='',
                 clientId=None, begDate=None, endDate=None, referralId=None):
        CDialogBase.__init__(self, parent)
        self.dateTime = dateTime
        self._clientId = clientId
        self.setupUi(self)

        self.edtPlannedDate.setDate(QtCore.QDate())
        self.edtDate.setDate(QtCore.QDate())
        if not CPreCreateEventDialog._orgId:
            self.loadDefaults()
        db = QtGui.qApp.db

        cond = [
            getWorkEventTypeFilter(),
            getOrgStructureEventTypeFilter(orgStructureId if orgStructureId else QtGui.qApp.currentOrgStructureId()),
            eventTypeFilterHospitalization if eventTypeFilterHospitalization else '1',
            'deleted = 0',
            'EventType.filterPosts = 0 OR '
            '   EXISTS(SELECT etp.id '
            '          FROM EventType_Post etp '
            '          WHERE etp.post_id = %s AND '
            '                etp.eventType_id = EventType.id)' % (QtGui.qApp.userPostId or '-1'),
            'EventType.filterSpecialities = 0 OR '
            '   EXISTS(SELECT etp.id '
            '          FROM EventType_Speciality etp '
            '          WHERE etp.speciality_id = %s AND '
            '                etp.eventType_id = EventType.id)' % (QtGui.qApp.userSpecialityId or '-1')
        ]
        if db.getRecordEx('Client_PaymentScheme c INNER JOIN PaymentScheme p ON p.id = c.paymentScheme_id',
                          'c.id',
                          'c.client_id = %s AND p.type = 0 AND c.deleted = 0' % self._clientId) is not None:
            CPreCreateEventDialog._eventTypeId = getEventType('protocol').eventTypeId
        else:
            cond.append('code != \'protocol\'')
        self.cmbEventType.setTable('EventType', False, db.joinAnd(cond), group='id')
        self.cmbTissueType.setTable('rbTissueType')

        self.cmbOrg.setValue(CPreCreateEventDialog._orgId)
        self.cmbRelegateOrg.setValue(CPreCreateEventDialog._relegateOrgId)
        if CPreCreateEventDialog._eventTypeId is None:
            self.cmbEventType.setCurrentIndex(0)
            CPreCreateEventDialog._eventTypeId = self.cmbEventType.value()
        else:
            self.cmbEventType.setValue(CPreCreateEventDialog._eventTypeId)
        if QtGui.qApp.currentOrgStructureId():
            self.cmbPerson.setOrgStructureId(QtGui.qApp.currentOrgStructureId())
        if orgStructureId:
            self.cmbPerson.setOrgStructureId(orgStructureId)
        self.cmbOrgStructure.setOrgId(CPreCreateEventDialog._orgId)
        self.cmbPerson.setValue(personId if personId else CPreCreateEventDialog._personId)
        eventType = self.cmbEventType.value()
        if hasEventAssistant(eventType):
            self.cmbAssistantId.setValue(CPreCreateEventDialog._assistantId)
        if hasEventCurator(eventType):
            self.cmbCuratorId.setValue(CPreCreateEventDialog._curatorId)
        self.chkAddVisits.setChecked(CPreCreateEventDialog._addVisits)
        self.chkIncludeRedDays.setChecked(CPreCreateEventDialog._includeRedDays)
        self.cmbTissueType.setValue(CPreCreateEventDialog._tissueTypeId)
        self.chkSelectPreviousActions.setChecked(CPreCreateEventDialog._selectPreviousActions)
        self.cmbReferralType.setTable('rbReferralType')
        if forceInt(CPreCreateEventDialog._referralType):
            self.cmbReferralType.setValue(CPreCreateEventDialog._referralType)

        self.prefix = ''
        self.on_cmbEventType_currentIndexChanged(0)

        self.edtExternalId.setText(externalId if externalId else '')
        self.edtPlannedDate.setMinimumDate(QtCore.QDate.currentDate())
        self.edtDate.setMinimumDate(QtCore.QDate.currentDate().addMonths(-6))
        self.edtDate.setMaximumDate(QtCore.QDate.currentDate())

        self.setupReferral()

        self.useArmyRef = False

        self.btnAppointment.setVisible(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'EGISZ', False)))

        if not CPreCreateEventDialog._connected:
            QtGui.qApp.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), CPreCreateEventDialog.onConnectionChanged)
            CPreCreateEventDialog._connected = True

        self._isNosologyInit = False

        if not QtGui.qApp.isSupportCreateNosologyEvent():
            self.tabWidget.setTabEnabled(1, False)

        if begDate:
            self.edtEventSetDate.setDate(begDate.date())
            self.edtEventSetTime.setTime(begDate.time())
            #FIXME:skkachaev: Предпологается, что у эвента, который мы пересоздаём, setDate есть всегда
            self.isRecreated = True
        if endDate:
            self.edtEventDate.setDate(endDate.date())
            self.edtEventTime.setTime(endDate.time())

        self.edtPlannedDate.setDate(QtCore.QDate.currentDate())

        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDefault(True)
        if QtGui.qApp.changeFocusInPreCreateEvent():
            self.cmbEventType.setFocus(QtCore.Qt.OtherFocusReason)

        self._invisibleObjectsNameList = self.reduceNames(QtGui.qApp.userInfo.hiddenObjectsNameList([self.moduleName()])) \
                                         if QtGui.qApp.userInfo else []
        self.updateVisibleState(self, self._invisibleObjectsNameList)
        if referralId:
            # showDefaultHint(u'Найдено направление', u'Данные заполнены автоматически')
            tblReferral = db.table('Referral')
            recReferral = db.getRecordEx(tblReferral, '*', tblReferral['id'].eq(referralId))
            # self.grpReferral.setChecked(True)
            self.cmbReferralType.setValue(forceInt(recReferral.value('type')))
            self.edtNumber.setText(forceString(recReferral.value('number')))
            self.cmbRelegateOrg.setValue(forceInt(recReferral.value('relegateOrg_id')))
            self.edtDate.setDate(forceDate(recReferral.value('date')))
            self.edtPlannedDate.setDate(forceDate(recReferral.value('hospDate')))
            self.cmbSpeciality.setValue(forceInt(recReferral.value('medProfile_id')))
            self.cmbMKB.setText(forceString(recReferral.value('MKB')))
            self.edtPerson.setText(forceString(recReferral.value('person')))

    @staticmethod
    def moduleName():
        return u'PreCreateEventDialog'

    @staticmethod
    def moduleTitle():
        return u'Создание обращения'

    @classmethod
    def hiddableChildren(cls):
        nameList = [(u'lblOrg', u'ЛПУ')]
        return cls.normalizeHiddableChildren(nameList)

    def show(self):
        self.loadDialogPreferences()
        CDialogBase.show(self)

    def loadPreferences(self, preferences):
        #showGrpReferral = forceBool(getPref(preferences, 'showGrpReferral', False))
        # self.grpReferral.setChecked(showGrpReferral)
        # self.setLayoutContentVisible(self.grpReferral.layout(), showGrpReferral)
        super(CPreCreateEventDialog, self).loadPreferences(preferences)

    def savePreferences(self):
        preferences = super(CPreCreateEventDialog, self).savePreferences()
        # setPref(preferences, 'showGrpReferral', QtCore.QVariant(self.grpReferral.isChecked()))
        return preferences

    def initNosology(self):
        if self._isNosologyInit:
            return
        endDate = QtCore.QDate.currentDate()
        begDate = QtCore.QDate(endDate.year(), 1, 1)
        mkbList = getMKBList(begDate, endDate)
        self.edtNosologyDiagnosis.clear()
        self.edtNosologyDiagnosis.addItems(mkbList)
        self._isNosologyInit = True
        self.edtNosologyDiagnosis.textChanged.connect(self.checkNosologyMKB)

    @QtCore.pyqtSlot(QtCore.QString)
    def checkNosologyMKB(self, newText):
        btnOk = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        btnOk.setEnabled(self.edtNosologyDiagnosis.findText(newText) != -1)

    def nosologyMKB(self):
        return forceStringEx(self.edtNosologyDiagnosis.currentText()) if self.tabWidget.currentIndex() == 1 else None

    def loadDefaults(self):
        db = QtGui.qApp.db
        tablePerson = db.table('Person')

        prefs = getPref(QtGui.qApp.preferences.appPrefs, 'PreCreateEvent', {})
        infisCode = getPref(prefs, 'infisCode', '')
        eventTypeCode = getPref(prefs, 'eventTypeCode', '01')
        personCode = getPref(prefs, 'personCode', '')
        personId = forceRef(getPref(prefs, 'personId', None))
        assistantCode = getPref(prefs, 'assistantCode', '')
        curatorCode = getPref(prefs, 'curatorCode', '')
        addVisits = bool(getPref(prefs, 'addVisits', False))
        includeRedDays = bool(getPref(prefs, 'includeRedDays', False))
        tissueTypeCode = getPref(prefs, 'tissueTypeCode', '1')
        referralType = getPref(prefs, 'referralType', '')
        selectPreviousActions = bool(getPref(prefs, 'selectPreviousActions', False))

        if infisCode:
            CPreCreateEventDialog._orgId = forceRef(db.translate('Organisation', 'infisCode', infisCode, 'id'))
        if not CPreCreateEventDialog._orgId:
            CPreCreateEventDialog._orgId = QtGui.qApp.currentOrgId()
        if not eventTypeCode:
            eventTypeCode = '01'
        CPreCreateEventDialog._eventTypeId = getEventType(eventTypeCode).eventTypeId
        if QtGui.qApp.userSpecialityId:
            CPreCreateEventDialog._personId = QtGui.qApp.userId
        elif personId and db.getRecordEx(tablePerson, 'id', [tablePerson['id'].eq(personId),
                                                             tablePerson['code'].eq(personCode)]) is not None:
            CPreCreateEventDialog._personId = personId
        elif personCode:
            CPreCreateEventDialog._personId = forceRef(db.translate('Person', 'code', personCode, 'id')) if personCode else None
        CPreCreateEventDialog._assistantId = forceRef(db.translate('Person', 'code', assistantCode, 'id')) if assistantCode else None
        CPreCreateEventDialog._curatorId = forceRef(db.translate('Person', 'code', curatorCode, 'id')) if curatorCode else None
        CPreCreateEventDialog._includeRedDays = includeRedDays
        CPreCreateEventDialog._tissueTypeId = forceRef(db.translate('rbTissueType', 'code', tissueTypeCode, 'id')) if tissueTypeCode else None
        CPreCreateEventDialog._selectPreviousActions = selectPreviousActions
        CPreCreateEventDialog._referralType = referralType

    def saveDefaults(self):
        db = QtGui.qApp.db

        orgId = self.cmbOrg.value()
        eventTypeId = self.cmbEventType.value()
        personId = self.cmbPerson.value()
        assistantId = self.cmbAssistantId.value()
        curatorId = self.cmbCuratorId.value()
        referralType = self.cmbReferralType.value()
        addVisits = self.chkAddVisits.isChecked()

        includeRedDays = self.chkIncludeRedDays.isChecked()
        tissueTypeId = self.cmbTissueType.value()
        selectPreviousActions = self.chkSelectPreviousActions.isChecked()

        prefs = getPref(QtGui.qApp.preferences.appPrefs, 'PreCreateEvent', {})
        if CPreCreateEventDialog._orgId != orgId:
            CPreCreateEventDialog._orgId = orgId
            infisCode = forceString(db.translate('Organisation', 'id', orgId, 'infisCode'))
            setPref(prefs, 'infisCode', infisCode)
        if CPreCreateEventDialog._eventTypeId != eventTypeId:
            CPreCreateEventDialog._eventTypeId = eventTypeId
            eventTypeCode = getEventCode(eventTypeId)
            setPref(prefs, 'eventTypeCode', eventTypeCode)
        if CPreCreateEventDialog._personId != personId:
            CPreCreateEventDialog._personId = personId
            personCode = forceString(db.translate('Person', 'id', personId, 'code')) if personId else ''
            setPref(prefs, 'personId', personId)
            setPref(prefs, 'personCode', personCode)
        if CPreCreateEventDialog._assistantId != assistantId:
            CPreCreateEventDialog._assistantId = assistantId
            assistantCode = forceString(db.translate('Person', 'id', assistantId, 'code')) if assistantId else ''
            setPref(prefs, 'assistantId', assistantCode)
        if CPreCreateEventDialog._curatorId != curatorId:
            CPreCreateEventDialog._curatorId = curatorId
            curatorCode = forceString(db.translate('Person', 'id', curatorId, 'code')) if curatorId else ''
            setPref(prefs, 'curatorId', curatorCode)
        if CPreCreateEventDialog._addVisits != addVisits:
            CPreCreateEventDialog._addVisits = addVisits
            setPref(prefs, 'addVisits', addVisits)
        if CPreCreateEventDialog._includeRedDays != includeRedDays:
            CPreCreateEventDialog._includeRedDays = includeRedDays
            setPref(prefs, 'includeRedDays', includeRedDays)
        if CPreCreateEventDialog._tissueTypeId != tissueTypeId:
            CPreCreateEventDialog._tissueTypeId = tissueTypeId
            tissueTypeCode = forceString(db.translate('rbTissueType', 'id', tissueTypeId, 'code')) if tissueTypeId else ''
            setPref(prefs, 'tissueTypeCode', tissueTypeCode)
        if CPreCreateEventDialog._selectPreviousActions != selectPreviousActions:
            CPreCreateEventDialog._selectPreviousActions = selectPreviousActions
            setPref(prefs, 'selectPreviousActions', selectPreviousActions)
        if CPreCreateEventDialog._referralType != referralType:
            CPreCreateEventDialog._referralType = referralType
            setPref(prefs, 'referralType', referralType)
        setPref(QtGui.qApp.preferences.appPrefs, 'PreCreateEvent', prefs)

    def checkPersonAttach(self, orgStructureId, personId, begDate):
        if orgStructureId and personId:
            if begDate.isNull():
                begDate = QtCore.QDate.currentDate()

            stmt = u"""
            SELECT
                pa.salary AS salary,
                (
                    SELECT 
                        COUNT(api.value) AS personPlan
                    FROM 
                        Event e
                        INNER JOIN EventType et ON et.id = e.eventType_id AND et.code = '0'
                        INNER JOIN Action a ON a.event_id = e.id AND a.deleted = 0
                        INNER JOIN ActionType at ON at.id = a.actionType_id AND at.code = 'amb'
                        INNER JOIN ActionPropertyType AS apt ON at.id = apt.actionType_id AND apt.name = 'notExternalSystems'
                        INNER JOIN ActionProperty AS ap ON apt.id = ap.type_id AND ap.action_id = a.id
                        INNER JOIN ActionProperty_Integer AS api ON ap.id = api.id
                    WHERE 
                        e.deleted = 0
                        AND e.setPerson_id = pa.master_id
                        AND DATE(e.setDate) = DATE('{begDate}')
                    LIMIT 1
                ) as personPlan,
                (
                    SELECT 
                        COUNT(*) 
                    FROM 
                        Event e 
                    WHERE 
                        e.deleted = 0 
                        AND e.setPerson_id = pa.master_id 
                        AND e.orgStructure_id = {orgStructureId}
                        AND DATE(e.setDate) = DATE('{begDate}')
                ) AS eventCount
            FROM
                PersonAttach pa
                INNER JOIN OrgStructure org ON org.id = pa.orgStructure_id
            WHERE 
                pa.master_id = {personId}
                AND pa.orgStructure_id = {orgStructureId}
                AND org.isArea = 1
                AND pa.salary IS NOT NULL
                AND LENGTH(pa.salary) > 0
                AND DATE(pa.begDate) < DATE('{begDate}')
                AND DATE(pa.endDate) >= DATE('{begDate}')
            """.format(begDate=begDate.toString('yyyy-MM-dd'), personId=personId, orgStructureId=orgStructureId)
            rec = QtGui.qApp.db.getRecordEx(stmt=stmt)
            if rec:
                salary = forceInt(rec.value('salary'))
                personPlan = forceInt(rec.value('personPlan'))
                eventCount = forceInt(rec.value('eventCount'))
                if salary and personPlan and (salary * personPlan / 100 > eventCount):
                    return self.checkValueMessage(
                        u'Лимит пациентов с участка замещения исчерпан.', True, self.cmbOrgStructure
                    )

        return True


    def saveData(self):
        result = True

        result = result and self.checkPersonAttach(
            self.cmbOrgStructure.value(), self.cmbPerson.value(), self.edtEventSetDate.date()
        )

        if QtGui.qApp.defaultNeedPreCreateEventPerson():
            result = bool(self.cmbPerson.value()) or self.checkInputMessage(u'ответственного врача', False, self.cmbPerson)
        if self.grpReferral.isChecked():
            # if self.edtPlannedDate.date().isNull():
            #     result = result and bool(self.checkInputMessage(u'дату планируемой госпитализации', False, self.edtPlannedDate))
            if not self.edtNumber.text():
                result = result and bool(self.checkInputMessage(u'номер направления', False, self.edtNumber))
            if not self.cmbReferralType.value():
                result = result and bool(self.checkInputMessage(u'тип направления', False, self.cmbReferralType))
            if self.edtDate.date().isNull():
                result = result and bool(self.checkInputMessage(u'дату выдачи направления', False, self.edtDate))
            if not self.cmbRelegateOrg.value() and not self.edtFreeInput.text():
                result = result and bool(self.checkInputMessage(u'направителя', False, self.cmbRelegateOrg))
            if self.edtPlannedDate.date().isNull():
                result = result and bool(self.checkInputMessage(u'корректную дату плановой госпитализации', False, self.edtPlannedDate))
            if not self.edtPlannedDate.date().isNull() and self.edtPlannedDate.date() < self.edtDate.date():
                result = result and bool(self.checkInputMessage(u'корректную дату плановой госпитализации', False, self.edtPlannedDate))
            if not self.edtPlannedDate.date().isNull() and self.edtPlannedDate.date() > self.edtDate.date().addMonths(6):
                result = result and bool(self.checkInputMessage(u'корректную дату плановой госпитализации', False, self.edtPlannedDate))
            # if not self.edtPerson.text():
            #     result = result and bool(self.checkInputMessage(u'врача', False, self.edtPerson))
            if not self.cmbMKB.text():
                result = result and bool(self.checkInputMessage(u'код МКБ', False, self.cmbMKB))
            else:
                db = QtGui.qApp.db
                tableMKB = db.table('MKB')
                if not db.getRecordEx(tableMKB, tableMKB['id'], tableMKB['DiagID'].eq(forceString(self.cmbMKB.text()))):
                    result = result and bool(self.checkInputMessage(u'верный код МКБ', False, self.cmbMKB))

        result = result and (not self.cmbPerson.value() or
                             self.cmbOrgStructure.value() or
                             self.checkInputMessage(u'подразделение работы врача',
                                                    skipable=getPersonOrgId(self.cmbPerson.value()) is not None,
                                                    widget=self.cmbOrgStructure))

        if result:
            clientOrgStructureId = getClientAttachOrgStructure(self._clientId)
            personOrgStructureId = self.cmbOrgStructure.value()
            if clientOrgStructureId and personOrgStructureId and clientOrgStructureId != personOrgStructureId:
                result = result and self.checkValueMessage(u'Пациент относится к другому участку: <b>{0}</b>'.format(getOrgStructureName(clientOrgStructureId)),
                                                           True, self.cmbOrgStructure)

        if result and self.checkOrGenerateUniqueEventExternalId():
            self.saveDefaults()
            CPreCreateEventDialog._eventSetDate = self.edtEventSetDate.date()
            CPreCreateEventDialog._eventDate = self.edtEventDate.date()
            return True

        return result

    def updatePersonOrgStructure(self):
        self.cmbOrgStructure.setValue(getPersonOrgStructureOnDate(self.cmbPerson.value(), self.edtEventSetDate.date()))

    def setupDatesAndTimes(self):
        eventTypeId = self.cmbEventType.value()
        dateInput = getEventDateInput(eventTypeId)
        showTime = getEventShowTime(eventTypeId)

        if dateInput == 0:
            self.edtEventSetDate.setEnabled(True)
            self.edtEventSetTime.setEnabled(True)
            self.edtEventDate.setEnabled(False)
            self.edtEventTime.setEnabled(False)
            self.edtEventDate.canBeEmpty(True)
            clearEndDate = False
        elif dateInput == 1:
            self.edtEventSetDate.setEnabled(False)
            self.edtEventSetTime.setEnabled(False)
            self.edtEventDate.setEnabled(True)
            self.edtEventTime.setEnabled(True)
            self.edtEventDate.canBeEmpty(False)
            clearEndDate = False
        else:
            self.edtEventSetDate.setEnabled(True)
            self.edtEventSetTime.setEnabled(True)
            self.edtEventDate.setEnabled(True)
            self.edtEventTime.setEnabled(True)
            self.edtEventDate.canBeEmpty(True)
            clearEndDate = True

        self.edtEventSetTime.setVisible(showTime)
        self.edtEventTime.setVisible(showTime)

        zeroTime = QtCore.QTime(0, 0)
        if self.dateTime:
            setDate, setTime = self.dateTime.date(), self.dateTime.time()
            date, time = (QtCore.QDate(), zeroTime) if clearEndDate else (setDate, setTime)
        else:
            now = QtCore.QDateTime.currentDateTime()
            setDate = CPreCreateEventDialog._eventSetDate if CPreCreateEventDialog._eventSetDate else now.date()
            setTime = now.time() #atronah: for i1171\\ if now.date() == setDate else zeroTime
            if clearEndDate:
                date, time = QtCore.QDate(), zeroTime
            else:
                date = CPreCreateEventDialog._eventDate if CPreCreateEventDialog._eventDate else now.date()
                time = now.time() #atronah: for i1171\\ if now.date() == date else zeroTime
        if isEventTypeResetSetDate(eventTypeId):
            setDate = QtCore.QDate.currentDate()
        if not self.isRecreated:
            self.edtEventSetDate.setDate(setDate)
            self.edtEventSetTime.setTime(setTime)
            self.edtEventDate.setDate(date)
            self.edtEventTime.setTime(time)

    def setupAssistant(self):
        self.cmbAssistantId.setEnabled(hasEventAssistant(self.cmbEventType.value()))

    def setupCurator(self):
        self.cmbCuratorId.setEnabled(hasEventCurator(self.cmbEventType.value()))

    def setupExternal(self):
        eventTypeId = self.cmbEventType.value()
        isExternal = getEventIsExternal(eventTypeId)
        self.edtExternalId.setEnabled(isExternal and not getEventCounterId(eventTypeId))
        if self.edtExternalId.isEnabled():
            prefix = getEventPrefix(eventTypeId)
            if prefix:
                self.prefix = prefix
                re = QtCore.QRegExp('%s.*' % prefix)
                val = QtGui.QRegExpValidator(re, self)
                self.edtExternalId.setText(prefix)
                self.edtExternalId.setValidator(val)
                return
        self.prefix = ''
        self.edtExternalId.setText('')
        self.edtExternalId.setValidator(None)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtExternalId_textChanged(self, text):
        if len(self.edtExternalId.text()) < len(self.prefix):
            self.edtExternalId.setText(self.prefix)

    def setupTissue(self):
        eventTypeId = self.cmbEventType.value()
        isTakenTissue = getEventIsTakenTissue(eventTypeId)
        self.cmbTissueType.setEnabled(isTakenTissue)
        self.lblTissueType.setVisible(isTakenTissue)
        self.cmbTissueType.setVisible(isTakenTissue)

    def setupSelectPreviousActions(self):
        eventTypeId = self.cmbEventType.value()
        showChkSelectPreviousActions = getEventTypeForm(eventTypeId) == '001'
        self.chkSelectPreviousActions.setEnabled(showChkSelectPreviousActions)
        self.chkSelectPreviousActions.setVisible(showChkSelectPreviousActions)

    def setupReferral(self):
        if QtGui.qApp.isReferralRequired():
            db = QtGui.qApp.db
            topDate = self.edtEventSetDate.date()
            tableReferral = db.table('Referral')
            clientId = self._clientId if self._clientId else QtGui.qApp.currentClientId()
            self.cmbArmyNumber.setFilter(db.joinAnd(['client_id=%d' % clientId,
                                                     tableReferral['date'].ge(topDate.addMonths(-1)),
                                                     tableReferral['date'].le(topDate),
                                                     tableReferral['type'].eq(1)]))
            self.cmbSpeciality.setTable('rbSpeciality', True)
            # self.edtDate.setMinimumDate(topDate.addMonths(-1))
            # self.edtDate.setMaximumDate(topDate)
            self.useLPURef = True
            # self.edtArmyDate.setMinimumDate(topDate.addMonths(-1))
            # self.edtArmyDate.setMaximumDate(topDate)
            if not QtGui.qApp.userHasRight(urCreateReferral):
                self.enableReferral(False)
                self.enableArmyReferral(False)
        else:
            self.grpReferral.setEnabled(False)
            self.grpReferral.setVisible(False)
            self.tabWidget.setTabEnabled(2, False)

    def enableReferral(self, state):
        self.grpReferral.setEnabled(state)

    def enableArmyReferral(self, state):
        self.tabWidget.setTabEnabled(2, state)

    def orgId(self):
        return self.cmbOrg.value()

    def relegateOrgId(self):
        return self.cmbRelegateOrg.value()

    def eventTypeId(self):
        return self.cmbEventType.value()

    def personId(self):
        return self.cmbPerson.value()

    def orgStructureId(self):
        return self.cmbOrgStructure.value()

    def assistantId(self):
        return self.cmbAssistantId.value() if self.cmbAssistantId.isEnabled() else None

    def curatorId(self):
        return self.cmbCuratorId.value() if self.cmbCuratorId.isEnabled() else None

    def eventSetDate(self):
        eventTypeId = self.cmbEventType.value()
        dateInput = getEventDateInput(eventTypeId)
        showTime = getEventShowTime(eventTypeId)
        if dateInput == 0:
            date = self.edtEventSetDate.date()
            time = self.edtEventSetTime.time()
        elif dateInput == 1:
            date = self.edtEventDate.date()
            time = self.edtEventTime.time()
        else:
            date = self.edtEventSetDate.date()
            time = self.edtEventSetTime.time()
        if showTime:
            return QtCore.QDateTime(date, time)
        else:
            return QtCore.QDateTime(date)

    def eventDate(self):
        """Возвращает дату окончания события"""
        eventTypeId = self.cmbEventType.value()
        dateInput = getEventDateInput(eventTypeId)
        showTime = getEventShowTime(eventTypeId)
        if dateInput == 0:
            return QtCore.QDateTime()
        else:
            date = self.edtEventDate.date()
            time = self.edtEventTime.time()
        if date.isNull():
            return QtCore.QDateTime()
        if showTime:
            return QtCore.QDateTime(date, time)
        else:
            return QtCore.QDateTime(date)

    def externalId(self):
        eventTypeId = self.cmbEventType.value()
        return forceStringEx(self.edtExternalId.text()) if getEventIsExternal(eventTypeId) else ''

    def armyRef(self):
        return {'date':self.armyDate(),  'number':self.armyNumber(), 'relegateOrg_id':self.armyOrgId(), 'freeInput':self.armyFreeInput()} if self.useArmyRef else {}

    def armyNumber(self):
        if not self.cmbArmyNumber.isEnabled() or not self.useArmyRef:
            return (None, None)
        if (self.cmbArmyNumber.currentIndex() in (-1, 0)):
            return (0, self.cmbArmyNumber.lineEdit().text())
        return (self.edtNumber.text())

    def armyDate(self):
        return self.edtArmyDate.date() if self.useArmyRef and self.edtArmyDate.isEnabled() else None

    def armyOrgId(self):
        return self.cmbArmyOrg.value() if self.useArmyRef and self.edtArmyFreeInput.isEnabled() == False else None

    def armyFreeInput(self):
        return self.edtArmyFreeInput.text() if self.useArmyRef and self.edtArmyFreeInput.isEnabled() else None

    def lpuRef(self):
        return {'date': self.date(), 'hospDate': self.hospDate(), 'number': self.number(), 'freeInput': self.freeInput(),
                'person': self.referralPerson(), 'MKB': self.MKB(), 'speciality_id': self.speciality(),
                'relegateOrg_id': self.relegateOrgId(), 'type': self.referralType()
                } if self.grpReferral.isChecked() else {}

    def number(self):
        if not self.edtNumber.isEnabled() or not self.useLPURef:
            return (None, None)
        if not self.edtNumber.text():
            return (self.edtNumber.text())
        return (self.edtNumber.text())

    def date(self):
        return self.edtDate.date() if self.edtDate.isEnabled() and self.useLPURef else None

    def hospDate(self):
        return self.edtPlannedDate.date() if self.edtPlannedDate.isEnabled() and self.useLPURef else None

    def freeInput(self):
        return self.edtFreeInput.text() if self.edtFreeInput.isEnabled() and self.useLPURef else None

    def referralPerson(self):
        return self.edtPerson.text() if self.edtPerson.isEnabled() and self.useLPURef else None

    def MKB(self):
        return self.cmbMKB.text() if self.cmbMKB.isEnabled() and self.useLPURef else None

    def speciality(self):
        return self.cmbSpeciality.value() if self.cmbSpeciality.isEnabled() and self.useLPURef else None

    def referralType(self):
        return self.cmbReferralType.value() if self.cmbReferralType.isEnabled() and self.useLPURef else None

    def addVisits(self):
        return self.chkAddVisits.isChecked() if self.chkAddVisits.isEnabled() else False

    def includeRedDays(self):
        return self.chkIncludeRedDays.isChecked() if self.chkIncludeRedDays.isEnabled() else False

    def days(self):
        return self.edtDays.value() if self.edtDays.isEnabled() else 0

    def tissueTypeId(self):
        return self.cmbTissueType.value() if self.cmbTissueType.isEnabled() else None

    def selectPreviousActions(self):
        return self.chkSelectPreviousActions.isChecked() and self.chkSelectPreviousActions.isEnabled()

    def setDays(self):
        isLong = bool(isEventLong(self.cmbEventType.value()))
        isStationary = bool(isEventStationary(self.cmbEventType.value()))
        setDate = self.edtEventSetDate.date()
        eventDate = self.edtEventDate.date()
        self.chkAddVisits.setEnabled(isLong and bool(eventDate))
        addVisits = bool(isLong and self.chkAddVisits.isChecked() and setDate and eventDate)
        self.chkIncludeRedDays.setEnabled(addVisits)
        self.edtDays.setEnabled(addVisits)
        if addVisits:
            totalDays = setDate.daysTo(eventDate) + 1
            numDays = totalDays
            if not self.chkIncludeRedDays.isChecked():
                for i in xrange(totalDays):
                    if setDate.addDays(i).dayOfWeek() in [QtCore.Qt.Saturday, QtCore.Qt.Sunday]:
                        numDays -= 1
            if isStationary:
                numDays = max(numDays - 1, 1)
            self.edtDays.setMaximum(totalDays)
            self.edtDays.setValue(numDays)

    def generateExternalId(self):
        eventTypeId = self.cmbEventType.value()
        counterId = getEventCounterId(eventTypeId)
        prefix = getEventPrefix(eventTypeId)
        if counterId:
            try:
                clientId = self._clientId if self._clientId else QtGui.qApp.currentClientId()
                externalId = getDocumentNumber(clientId, counterId)
                if prefix:
                    externalId = ''.join([prefix, externalId])
                self.edtExternalId.setText(externalId)
            except Exception, e:
                QtGui.QMessageBox.critical(QtGui.qApp.mainWindow,
                                           u'Внимание!',
                                           u'Произошла ошибка при получении значения счетчика!\n%s' % e,
                                           QtGui.QMessageBox.Ok)
                return False
        return True

    def checkUniqueEventExternalId(self):
        if self.edtExternalId.isEnabled():
            externalId = self.externalId()
            if bool(externalId):
                sameExternalIdListInfo = checkUniqueEventExternalId(externalId, eventId=None)
                if bool(sameExternalIdListInfo):
                    sameExternalIdListText = '\n'.join(sameExternalIdListInfo)
                    message = u'Подобный внешний идентификатор уже существует в других событиях:\n%s\n\n%s'%(
                                                                                    sameExternalIdListText, u'Исправить?')
                    return self.checkValueMessage(message, True, self.edtExternalId)
        return True

    def checkOrGenerateUniqueEventExternalId(self):
        eventTypeId = self.cmbEventType.value()
        uniqueExternalIdRequired = getUniqueExternalIdRequired(eventTypeId)
        counterType = getCounterType(eventTypeId)
        if self.edtExternalId.text():
            return not uniqueExternalIdRequired or self.checkUniqueEventExternalId()
        elif counterType == 1:
            return (not uniqueExternalIdRequired or self.checkUniqueEventExternalId()) and self.generateExternalId()
        else:
            return True

    def getReferralsList(self):
        #TODO shepas: Потребляет очень много памяти при большом количестве направлений, больше не используется, можно удалить
        db = QtGui.qApp.db
        result = []
        tblReferral = db.table('Referral')
        referralsRecords = db.getRecordList(tblReferral, '*', [tblReferral['deleted'].eq(0),
                                                               tblReferral['isSend'].eq(0)])
        for referral in referralsRecords:
            result.append(referral)
        referralsRecords = db.getRecordList(tblReferral, '*', [tblReferral['deleted'].eq(0),
                                                               tblReferral['isSend'].eq(1),
                                                               tblReferral['relegateOrg_id'].eq(QtGui.qApp.currentOrgId())])
        for referral in referralsRecords:
            result.append(referral)
        return result

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, idx):
        if idx == 0:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        elif idx == 1:
            self.initNosology()
            self.cmbEventType.setCode('prr30')
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(bool(self.cmbEventType.value()))
            if not self.isRecreated:
                self.edtEventSetDate.setDate(QtCore.QDate(QtCore.QDate.currentDate().year(), 1, 1))
                self.edtEventDate.setDate(QtCore.QDate.currentDate())

    @QtCore.pyqtSlot()
    def on_btnSelectRelegateOrg_clicked(self):
        orgId = selectOrganisation(self, self.cmbRelegateOrg.value(), False, filter=CPolyclinicComboBox._filter)
        self.cmbRelegateOrg.update()
        if orgId:
            self.setIsDirty()
            self.cmbRelegateOrg.setValue(orgId)

    @QtCore.pyqtSlot()
    def on_btnSelectArmyOrg_clicked(self):
        orgId = selectOrganisation(self, self.cmbArmyOrg.value(), False, filter=CArmyOrgComboBox._filter)
        self.cmbArmyOrg.update()
        if orgId:
            self.setIsDirty()
            self.cmbArmyOrg.setValue(orgId)

    @QtCore.pyqtSlot(int)
    def on_cmbOrg_currentIndexChanged(self):
        orgId = self.cmbOrg.value()
        self.cmbPerson.setOrgId(orgId)

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        self.updatePersonOrgStructure()

    @QtCore.pyqtSlot(int)
    def on_cmbEventType_currentIndexChanged(self, idx):
        eventTypeId = self.cmbEventType.value()
        if eventTypeId and (hasEventAssistant(eventTypeId) or hasEventCurator(eventTypeId)):
            db = QtGui.qApp.db
            tableEventType = db.table('EventType')
            record = db.getRecordEx(tableEventType, [tableEventType['form']], [tableEventType['deleted'].eq(0), tableEventType['id'].eq(eventTypeId)])
            form = forceString(record.value('form')) if record else ''
            if form == '027' or form == '025':
                tableEvent = db.table('Event')
                record = db.getRecordEx(tableEvent, [tableEvent['curator_id'], tableEvent['assistant_id']], [tableEvent['eventType_id'].eq(eventTypeId), tableEvent['deleted'].eq(0)], 'Event.id DESC')
                if record:
                    CPreCreateEventDialog._assistantId = forceRef(record.value('assistant_id'))
                    CPreCreateEventDialog._curatorId = forceRef(record.value('curator_id'))
                    self.cmbAssistantId.setValue(CPreCreateEventDialog._assistantId)
                    self.cmbCuratorId.setValue(CPreCreateEventDialog._curatorId)
        self.setupDatesAndTimes()
        self.setupAssistant()
        self.setupCurator()
        self.setupExternal()
        self.setupTissue()
        self.setupSelectPreviousActions()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEventSetDate_dateChanged(self, date):
        isLong = bool(isEventLong(self.cmbEventType.value()))
        if isLong:
            if self.edtEventSetDate.date() == QtCore.QDate.currentDate():
                self.edtEventDate.setDate(QtCore.QDate())
        self.setDays()
        self.updatePersonOrgStructure()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEventDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))
        self.setDays()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDate_dateChanged(self, date):
        self.edtPlannedDate.setMinimumDate(date)
        self.edtPlannedDate.setMaximumDate(date.addMonths(6))
        number = self.edtNumber.text()
        type = self.cmbReferralType.value()

        db = QtGui.qApp.db
        tblReferral = db.table('Referral')
        referral = db.getRecordEx(tblReferral, '*', [tblReferral['number'].eq(forceInt(number)), tblReferral['type'] == forceInt(type), tblReferral['date'].eq(forceDate(date))])
        if referral:
            if forceString(referral.value('number')) == forceString(number) and forceInt(referral.value('type')) == forceInt(type) \
                    and forceDate(referral.value('date')) == self.edtDate.date():
                if forceInt(referral.value('isCancelled')):
                    QtGui.QMessageBox.warning(self, u'Направление аннулировано', u'Данное направление аннулировано')
                    return
                elif forceInt(referral.value('event_id')) and not forceInt(referral.value('isSend')):
                    QtGui.QMessageBox.warning(self, u'Обращение уже создано', u'Для данного направления\nобращение уже создано')
                    return
                self.cmbRelegateOrg.setValue(forceInt(referral.value('relegateOrg_id')))
                self.edtDate.setDate(forceDate(referral.value('date')))
                self.edtPlannedDate.setDate(forceDate(referral.value('hospDate')))
                self.cmbSpeciality.setValue(forceInt(referral.value('medProfile_id')))
                self.cmbMKB.setText(forceString(referral.value('MKB')))
                self.edtPerson.setText(forceString(referral.value('person')))
                return

    @QtCore.pyqtSlot(bool)
    def on_chkAddVisits_toggled(self, checked):
        self.setDays()

    @QtCore.pyqtSlot(bool)
    def on_chkIncludeRedDays_toggled(self, checked):
        self.setDays()

    @staticmethod
    def onConnectionChanged(value):
        if value:
            CPreCreateEventDialog._orgId = None
            CPreCreateEventDialog._relegateOrgId = None
            CPreCreateEventDialog._eventTypeId = None
            CPreCreateEventDialog._personId = None
            CPreCreateEventDialog._assistantId = None
            CPreCreateEventDialog._curatorId = None
            CPreCreateEventDialog._eventSetDate = None
            CPreCreateEventDialog._eventDate = None
            CPreCreateEventDialog._addVisits = False
            CPreCreateEventDialog._includeRedDays = False
            CPreCreateEventDialog._tissueTypeId = None
            CPreCreateEventDialog._selectPreviousActions = False
            CPreCreateEventDialog._connected = False
            QtCore.QObject.disconnect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), CPreCreateEventDialog.onConnectionChanged)

    @staticmethod
    def setLayoutContentVisible(layout, show):
        for idx in xrange(layout.count()):
            widget = layout.itemAt(idx).widget()
            if widget is not None:
                widget.setVisible(show)

    @QtCore.pyqtSlot(bool)
    def on_grpReferral_toggled(self, checked):
        self.setLayoutContentVisible(self.grpReferral.layout(), checked)

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
        else:
            db = QtGui.qApp.db
            tbl = db.table('Referral')
            cond = [tbl['id'].eq(self.cmbArmyNumber.value()),
                    tbl['type'].eq(1)]
            record = db.getRecordEx(tbl, '*', where=cond)

            setLineEditValue(self.cmbArmyNumber.lineEdit(), record, 'number')
            if not record.value('freeInput').isNull():
                setLineEditValue(self.edtArmyFreeInput, record, 'freeInput')
                self.chkArmyFreeInput.setChecked(True)
            else:
                self.edtArmyFreeInput.setText('')
                self.chkArmyFreeInput.setChecked(False)
            setDateEditValue(self.edtArmyDate, record, 'date')
            self.cmbArmyOrg.setValue(record.value('relegateOrg_id'))

    @QtCore.pyqtSlot()
    def on_btnAppointment_clicked(self):
        self.isAppointment = True
        self.accept()
