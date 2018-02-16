# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action              import CActionTypeCache
from library.Utils              import forceString, forceStringEx, firstMonthDay, lastMonthDay
from Orgs.Utils                 import getOrgStructureDescendants, getOrgStructureFullName, getPersonInfo
from Reports.PreRecordDoctors   import CPreRecord
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase

from Ui_JournalBeforeRecordDialog  import Ui_JournalBeforeRecordDialog


def selectData(params):
    db = QtGui.qApp.db
    tablePerson = db.table('vrbPersonWithSpeciality').alias('ExecPerson')
    tableAction = db.table('Action')

    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    begDateRecord = params.get('begDateBeforeRecord', None)
    endDateRecord = params.get('endDateBeforeRecord', None)
    personId = params.get('personId', None)
    userId = params.get('beforeRecordUserId', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', None)
    chkOrgStructure = params.get('chkOrgStructure', None)
    queueType = params.get('queueType', 0)
    chkPeriodRecord = params.get('chkPeriodRecord', None)
    chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
    userProfileId = params.get('userProfileId', None)
    showWithoutOverTime = params.get('showWithoutOverTime', None)
    ignoreRehabilitation = params.get('ignoreRehabilitation', None)
    detailExternalIS = params.get('detailExternalIS', None)

    cond = [tableAction['deleted'].eq(0)]
    if chkPeriodRecord:
        if begDate:
            cond.append(tableAction['createDatetime'].dateGe(begDate))
        if endDate:
            cond.append(tableAction['createDatetime'].dateLe(endDate))
    if chkPeriodBeforeRecord:
        if begDateRecord:
            cond.append(tableAction['directionDate'].dateGe(begDateRecord))
        if endDateRecord:
            cond.append(tableAction['directionDate'].dateLe(endDateRecord))


    if queueType == 0:
        ambActionType = CActionTypeCache.getByCode('amb')
        codeAT = 'AT.id = %d' % ambActionType.id
    elif queueType == 1:
        homeActionType = CActionTypeCache.getByCode('home')
        codeAT = 'AT.id = %d' % homeActionType.id
    else:
        ambActionType = CActionTypeCache.getByCode('amb')
        homeActionType = CActionTypeCache.getByCode('home')
        codeAT = '(AT.id = %d OR AT.id = %d)' % (ambActionType.id, homeActionType.id)
    if chkOrgStructure:
        if personId:
            cond.append(tableAction['person_id'].eq(personId))
        if orgStructureId:
            cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
        else:
            if not personId:
                cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
        if specialityId:
            cond.append(tablePerson['speciality_id'].eq(specialityId))
    if userId:
        cond.append(tableAction['createPerson_id'].eq(userId))
    if userProfileId:
        cond.append('EXISTS(SELECT PUP.id '
                    '       FROM Person_UserProfile AS PUP '
                    '       WHERE PUP.person_id = PersonUserProfile.id '
                    '               AND PUP.userProfile_id = %s)' % userProfileId)
    if showWithoutOverTime:
        cond.append('APTime.value IS NOT NULL')
    if ignoreRehabilitation:
        cond.append(tablePerson['orgStructure_id'].notInlist(db.getIdList('OrgStructure', where = u'name LIKE "%реабилитац%"' )))

    queueActionType = CActionTypeCache.getByCode('queue')
    cond.append(tableAction['actionType_id'].eq(queueActionType.id))

    mainCond = []
    if detailExternalIS:
        mainCond.append(u'''Locate('Call-центр', A2.note)
        or Locate('CALLCENTER', A2.note)
        or Locate('оператор колл-центра', setPerson.lastName)
        or Locate('call-центр', setPerson.lastName)
        or Locate('менеджер колл-центра', rbPost.name)
        or Locate('инфомат', A2.note)
        or Locate('E-mail', A2.note)
        or Locate('iVista Web Medical Service', A2.note)
        or Locate('ЗАПИСЬ ОСУЩЕСТВЛЕНА ЧЕРЕЗ СИСТЕМУ "НЕТРИКА"', A2.note)
        or Locate('FROM RIR', A2.note)
        or not (setPerson.lastName
            or setPerson.firstName
            or setPerson.patrName
            or setPerson.post_id
            or setPerson.speciality_id)''')
        mainCond = u'AND ' + db.joinAnd(mainCond)

    if not mainCond:
        mainCond = u''
    stmt = u'''
            SELECT DISTINCTROW
				A2.createPerson_id,
                A2.person_id,
                Client.id,
                Client.lastName,
                Client.firstName,
                Client.patrName,
                Client.birthDate,
                getClientContacts(Client.id) AS clientPhones,
                getClientRegAddress(Client.id) AS clientAddress,
                rbPolicyType.name AS policyType,
                ClientPolicy.serial,
                ClientPolicy.number,
                Insurer.shortName AS insurerName,
                AT.code AS codeAT, A2.note AS actionNote,
                A2.directionDate,
                A2.createDatetime,
                ExecPerson.speciality_id AS personSpecialyty,               
                PersonUser.name AS userName,
                ExecPerson.name AS personName,
                setPerson.lastName  AS setPersonLastName,
                setPerson.firstName  AS setPersonFirstName,
                setPerson.patrName  AS setPersonPatrName,
                setPerson.post_id  AS setPersonPost,
                setPerson.speciality_id AS setPersonSpeciality,
                rbPost.name As postName
            FROM ActionProperty_Action
            INNER JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
            
            INNER JOIN Action AS A ON A.id = ActionProperty.action_id
            INNER JOIN ActionType AS AT ON AT.id = A.actionType_id

            INNER JOIN Action AS A2 ON A2.id = ActionProperty_Action.value
            INNER JOIN Event ON Event.id = A2.event_id
            INNER JOIN Person AS setPerson ON setPerson.id = A2.setPerson_id
            
            INNER JOIN Client ON Client.id = Event.client_id
            INNER JOIN ClientPolicy ON ClientPolicy.client_id = Client.id
            INNER JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            INNER JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
            
			LEFT JOIN rbPost ON rbPost.id = setPerson.post_id
            LEFT JOIN vrbPersonWithSpeciality AS ExecPerson ON ExecPerson.id = A2.person_id
            LEFT JOIN vrbPersonWithSpeciality AS PersonUser ON PersonUser.id = A2.createPerson_id
            WHERE %s
                AND Client.deleted = 0 AND Event.deleted = 0 AND A.deleted = 0 AND A2.deleted = 0   
				AND ClientPolicy.id = (SELECT MAX(CP.id) FROM ClientPolicy AS CP WHERE  CP.client_id = Client.id AND CP.deleted = 0)
                AND ActionProperty_Action.value IN (SELECT DISTINCT Action.id FROM Action WHERE %s)
                %s
            ORDER BY A2.directionDate
    ''' % (codeAT, db.joinAnd(cond), mainCond)
    return db.query(stmt)


class CJournalBeforeRecordDialog(QtGui.QDialog, Ui_JournalBeforeRecordDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbUserProfile.setTable('rbUserProfile')
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbUserId.setSpecialityPresent(False)


    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(date)))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(date)))
        self.edtBegDateRecord.setDate(params.get('begDateBeforeRecord', firstMonthDay(date)))
        self.edtEndDateRecord.setDate(params.get('endDateBeforeRecord', lastMonthDay(date)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkOrgStructure.setChecked(params.get('chkOrgStructure', False))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbUserId.setValue(params.get('beforeRecordUserId', None))
        self.cmbUserProfile.setValue(params.get('userProfileId', None))
        self.chkShowNotes.setChecked(params.get('chkShowNote', False))
        currentIndex = params.get('queueType', 0)
        if currentIndex is None:
            currentIndex = 0
        self.cmbQueueType.setCurrentIndex(currentIndex)


    def params(self):
        result = {'begDate': self.edtBegDate.date(),
                  'endDate': self.edtEndDate.date(),
                  'begDateBeforeRecord': self.edtBegDateRecord.date(),
                  'endDateBeforeRecord': self.edtEndDateRecord.date(),
                  'chkPeriodRecord': self.chkPeriodRecord.isChecked(),
                  'chkPeriodBeforeRecord': self.chkPeriodBeforeRecord.isChecked(),
                  'chkOrgStructure': self.chkOrgStructure.isChecked(),
                  'orgStructureId': self.cmbOrgStructure.value(),
                  'specialityId': self.cmbSpeciality.value(),
                  'personId': self.cmbPerson.value(),
                  'userProfileId': self.cmbUserProfile.value(),
                  'beforeRecordUserId': self.cmbUserId.value(),
                  'detailCallCentr': self.chkDetailCallCentr.isChecked(),
                  'detailExternalIS': self.chkDetailExternalIS.isChecked(),
                  'queueType': self.cmbQueueType.currentIndex(),
                  'showWithoutOverTime': self.chkShowWithoutOverTime.isChecked(),
                  'ignoreRehabilitation': self.chkIgnoreRehabilitation.isChecked(),
                  'chkShowNote': self.chkShowNotes.isChecked(),
                  }
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))
        self.cmbUserId.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)


class CJournalBeforeRecord(CReport, CPreRecord):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Журнал предварительной записи')
        self.doctorsDict = {}
        self.callCentrDict = {}


    def getSetupDialog(self, parent):
        result = CJournalBeforeRecordDialog(parent)
        return result


    def dumpParams(self, cursor, params):
        description = []
        db = QtGui.qApp.db
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        begDateBeforeRecord = params.get('begDateBeforeRecord', QtCore.QDate())
        endDateBeforeRecord = params.get('endDateBeforeRecord', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        userProfileId = params.get('userProfileId', None)
        beforeRecordUserId = params.get('beforeRecordUserId', None)
        actionTypeCode = params.get('queueType', None)
        chkPeriodRecord = params.get('chkPeriodRecord', None)
        chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
        chkOrgStructure = params.get('chkOrgStructure', None)
        chkDetailCallCentr = params.get('detailCallCentr', None)
        chkDetailExternalIS = params.get('detailExternalIS', None)
        chkShowNote = params.get('chkShowNote', False)

        if chkPeriodRecord:
            if begDate or endDate:
                description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if chkPeriodBeforeRecord:
            if begDateBeforeRecord or endDateBeforeRecord:
                description.append(u'период предварительной записи' + dateRangeAsStr(begDateBeforeRecord, endDateBeforeRecord))
        if beforeRecordUserId:
            personInfo = getPersonInfo(beforeRecordUserId)
            description.append(u'пользователь: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if userProfileId:
            description.append(u'профиль прав пользователя: ' + forceString(db.translate('rbUserProfile', 'id', userProfileId, 'name')))
        if chkOrgStructure:
            if orgStructureId:
                description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
            else:
                description.append(u'подразделение: ЛПУ')
            if specialityId:
                description.append(u'специальность: ' + forceString(db.translate('rbSpeciality', 'id', specialityId, 'name')))
            if personId:
                personInfo = getPersonInfo(personId)
                description.append(u'врач: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if actionTypeCode == 0:
            description.append(u'мероприятие: Прием')
        elif actionTypeCode == 1:
            description.append(u'мероприятие: Вызовы')
        if chkDetailCallCentr:
            description.append(u'Детализировать Call-центр')
        if chkDetailExternalIS:
            description.append(u'Детализировать запись через внешние ИС')
        if chkShowNote:
            description.append(u'Выводить жалобы')
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        detailCallCentr = params.get('detailCallCentr', False)
        datailExternalIS = params.get('detailExternalIS', False)
        tableColumns = [('2%', [u'№'], CReportBase.AlignLeft),
                        ('8%', [u'Дата Записи'], CReportBase.AlignLeft),
                        ('15%', [u'Пользователь'], CReportBase.AlignLeft),
                        ('15%', [u'ФИО'], CReportBase.AlignLeft),
                        ('8%', [u'Д/р'], CReportBase.AlignLeft),
                        ('8%', [u'Полис'], CReportBase.AlignLeft),
                        ('14%', [u'Жалобы'], CReportBase.AlignLeft),
                        ('14%', [u'Адрес'], CReportBase.AlignLeft),
                        ('7%', [u'Телефон'], CReportBase.AlignLeft),
                        ('8%', [u'Дата приема'], CReportBase.AlignLeft),
                        ('15%', [u'Врач'], CReportBase.AlignLeft)
                        ]
        if datailExternalIS:
            tableColumns.append(('10%', [u'Источник'], CReportBase.AlignLeft))
        chkShowNote = params.get('chkShowNote', False)
        if not chkShowNote:
            tableColumns = tableColumns[:6] + tableColumns[7:]
        table = createTable(cursor, tableColumns)
        query = selectData(params)
        n = 1
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            if record:
                i = table.addRow()
                clientFIO = ' '.join(name for name in [forceString(record.value('lastName')), forceString(record.value('firstName')), forceString(record.value('patrName'))])
                userName = forceString(record.value('userName'))
                actionNote = forceString(record.value('actionNote'))
                actionNoteLowerCase = actionNote.lower()
                setPersonLastName = forceString(record.value('setPersonLastName'))
                setPersonFirstName = forceString(record.value('setPersonFirstName'))
                setPersonPatrName = forceString(record.value('setPersonPatrName'))
                setPersonPostId = forceString(record.value('setPersonPost'))
                setPersonSpecialityId = forceString(record.value('setPersonSpeciality'))
                noteExternalIS = u''
                postName = forceString(record.value('postName'))

                if (u'call-центр' in actionNoteLowerCase) or (u'callcenter' in actionNoteLowerCase) \
                    or (u'оператор колл-центра' in setPersonLastName) \
                    or (u'call-центр' in setPersonLastName) \
                    or (u'менеджер колл-центра' in postName):
                    userName = u'Call-центр'
                    noteExternalIS = u'Call-центр'
                    if detailCallCentr:
                        callCentrUser = u': '
                        p = actionNote.find(u'администратор')
                        if p > -1:
                            callCentrUserTmp = actionNote[p:].split(':')
                            if len(callCentrUserTmp) == 2:
                                callCentrUser += forceStringEx(callCentrUserTmp[1])
                                userName += callCentrUser
                elif u'инфомат' in actionNote.lower():
                    userName = u'Инфомат'
                    noteExternalIS = u'Инфомат'
                elif (u'E-mail' in actionNote) or (u'iVista Web Medical Service' in actionNote) \
                        or (u'ЗАПИСЬ ОСУЩЕСТВЛЕНА ЧЕРЕЗ СИСТЕМУ "НЕТРИКА"' in actionNote) \
                        or (u'FROM RIR' in actionNote) \
                        or not (setPersonLastName \
                                        or setPersonFirstName \
                                        or setPersonPatrName \
                                        or setPersonPostId \
                                        or setPersonSpecialityId):
                    userName = u'Интернет'
                    noteExternalIS = u'Интернет'
                policyName = ' '.join(name for name in [forceString(record.value('policyType')), forceString(record.value('serial')), forceString(record.value('number')), forceString(record.value('insurerName'))])

                fields = (
                    n,
                    forceString(record.value('createDatetime')),
                    userName,
                    clientFIO,
                    forceString(record.value('birthDate')),
                    policyName,
                    actionNote,
                    forceString(record.value('clientAddress')),
                    forceString(record.value('clientPhones')),
                    forceString(record.value('directionDate')),
                    forceString(record.value('personName')),
                    noteExternalIS
                )
                if not datailExternalIS:
                    fields = fields[:-1]
                if not chkShowNote:
                    fields = fields[:6] + fields[7:]
                for col, item in enumerate(fields):
                    table.setText(i, col, item)

                n += 1
        return doc
