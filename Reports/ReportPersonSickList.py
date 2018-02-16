# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from Events.Action import CActionType

from Events.Utils           import getWorkEventTypeFilter
from library.crbcombobox    import CRBComboBox
from library.Utils          import forceDate, forceDateTime, forceInt, forceString
from Orgs.Orgs              import selectOrganisation
from Orgs.Utils             import getOrgStructureDescendants, getOrgStructures
from Registry.Utils         import getClientBanner
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from library.database import addDateInRange


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventPurposeIdList = params.get('eventPurposeIdList', [])
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', None)
    chkTraumaType = params.get('chkTraumaType', False)
    chkTraumaTypeAny = params.get('chkTraumaTypeAny', False)
    traumaTypeId = params.get('traumaTypeId', None)
    personId = params.get('personId', None)
    workOrgId = params.get('workOrgId', None)
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    areaIdEnabled = params.get('areaIdEnabled', False)
    areaId = params.get('areaId', None)
    MKBFilter = params.get('MKBFilter', 0)
    MKBFrom = params.get('MKBFrom', 'A00')
    MKBTo = params.get('MKBTo', 'Z99.9')
    MKBExFilter = params.get('MKBExFilter', 0)
    MKBExFrom = params.get('MKBExFrom', 'A00')
    MKBExTo = params.get('MKBExTo', 'Z99.9')
    diseaseCharacterCodes = classToCodes(params.get('characterClass', 0))
    onlyFirstTime = params.get('onlyFirstTime', False)
    accountAccomp = params.get('accountAccomp', False)
    locality = params.get('locality', 0)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)
    visitEmergency = params.get('visitEmergency', False)
    period = params.get('regInPeriod', False)
    
    stmt="""
SELECT
    Diagnosis.client_id,
    Diagnosis.id AS diagnosis_id,
    Diagnosis.MKB,
    Diagnosis.MKBEx,
    Diagnosis.setDate,
    Diagnosis.endDate,
    rbDiseaseCharacter.code AS diseaseCharacter,
    rbTraumaType.name AS traumaType,
    DATE(Diagnostic.endDate) AS diagnosticDate,
    Diagnostic.hospital AS diagnosticHospital,
    Diagnostic.sanatorium AS diagnosticSanatorium,
    rbDispanser.name AS diagnosticDispanser,
    vrbPersonWithSpeciality.name AS diagnosticPerson
FROM Diagnosis
LEFT JOIN Client ON Client.id = Diagnosis.client_id
LEFT JOIN ClientAddress ON ClientAddress.client_id = Diagnosis.client_id
                        AND ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA WHERE CA.Type=1 and CA.client_id = Diagnosis.client_id)
LEFT JOIN Address ON Address.id = ClientAddress.address_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id
LEFT JOIN rbTraumaType ON rbTraumaType.id = Diagnosis.traumaType_id
LEFT JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
LEFT JOIN rbDispanser ON rbDispanser.id = Diagnostic.dispanser_id
LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Diagnostic.person_id
LEFT JOIN Event      ON Event.id = Diagnostic.event_id
LEFT JOIN EventType  ON EventType.id = Event.eventType_id
WHERE
    %s
ORDER BY
    Client.lastName, Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.id,
    Diagnosis.MKB, Diagnosis.MKBEx, Diagnostic.endDate
"""
    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableClient = db.table('Client')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableDiagnostic = db.table('Diagnostic')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableEvent  = db.table('Event')
    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    if period:
       addDateInRange(cond, tableDiagnostic['endDate'], begDate, endDate)
    cond.append(tableDiagnostic['setDate'].le(endDate))
    cond.append(db.joinOr([tableDiagnostic['endDate'].ge(begDate), tableDiagnostic['endDate'].isNull()]))
#    addDateInRange(cond, tableDiagnostic['setDate'], begDate, endDate)

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeIdList:
        cond.append(db.table('EventType')['purpose_id'].inlist(eventPurposeIdList))
    if onlyFirstTime:
        cond.append(tableDiagnosis['setDate'].le(endDate))
        cond.append(tableDiagnosis['setDate'].ge(begDate))
    else:
        cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].le(endDate)]))
        cond.append(db.joinOr([tableDiagnosis['endDate'].ge(begDate), tableDiseaseCharacter['code'].eq('3')]))
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if personId:
        cond.append(tableDiagnostic['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if chkTraumaType:
        if chkTraumaTypeAny:
            cond.append(tableDiagnosis['traumaType_id'].isNotNull())
        elif traumaTypeId:
            cond.append(tableDiagnosis['traumaType_id'].eq(traumaTypeId))
        else:
            cond.append(tableDiagnosis['traumaType_id'].isNull())
    if workOrgId:
        cond.append('EXISTS (SELECT * FROM ClientWork WHERE ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id) and ClientWork.org_id=%d)' % (workOrgId))
    if not visitEmergency:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'4\')))''''')
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if areaIdEnabled:
        if areaId:
            orgStructureIdList = getOrgStructureDescendants(areaId)
        else:
            orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableAddress = db.table('Address')
        subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
                    tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                  ]
        cond.append(db.existsStmt(tableOrgStructureAddress, subCond))
    if diseaseCharacterCodes:
        if diseaseCharacterCodes != [None]:
            cond.append(tableDiseaseCharacter['code'].inlist(diseaseCharacterCodes))
        else:
            cond.append(tableDiseaseCharacter['code'].isNull())
    if not accountAccomp:
        tableDiagnosisType = db.table('rbDiagnosisType')
        cond.append(tableDiagnosisType['code'].inlist(['1', '2', '4']))
    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Client.id), 0) = %d' % (locality-1))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS('+subStmt+')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS('+subStmt+')')
    return db.query(stmt % (db.joinAnd(cond)))


class CReportPersonSickList(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Заболеваемость: список пациентов')


    def getSetupDialog(self, parent):
        result = CReportPersonSickListSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def dumpParamsTraumaType(self, cursor, params):
        description = []
        traumaTypeId = params.get('traumaTypeId', None)
        chkTraumaTypeAny = params.get('chkTraumaTypeAny', False)
        if chkTraumaTypeAny:
            nameTraumaType = u'любой'
        elif traumaTypeId:
            nameTraumaType = forceString(QtGui.qApp.db.translate('rbTraumaType', 'id', traumaTypeId, 'name'))
        else:
            nameTraumaType = u'не определен'
        description.append(u'Тип травмы: ' + nameTraumaType)
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)


    def build(self, params):        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        chkTraumaType = params.get('chkTraumaType', False)
        if chkTraumaType:
            self.dumpParamsTraumaType(cursor, params)
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('5%', [u'№' ],                                 CReportBase.AlignRight),
            ('25%',[u'Пациент'],                            CReportBase.AlignLeft),
            ('5%', [u'Заболевания',         u'Код по МКБ'], CReportBase.AlignLeft),
            ('5%', [u'',                    u'Доп.код'],    CReportBase.AlignLeft),
            ('5%', [u'',                    u'С'],          CReportBase.AlignLeft),
            ('5%', [u'',                    u'По'],         CReportBase.AlignLeft),
            ('5%', [u'',                    u'Характер'],   CReportBase.AlignLeft),
            ('5%', [u'',                    u'Тип травмы'], CReportBase.AlignLeft),

            ('5%', [u'Осмотры',             u'Дата'],       CReportBase.AlignLeft),
            ('5%', [u'',                    u'Госп.'],      CReportBase.AlignLeft),
            ('5%', [u'',                    u'СКЛ'],        CReportBase.AlignLeft),
            ('5%', [u'',                    u'ДН'],         CReportBase.AlignLeft),
            ('15%',[u'',                    u'Врач'],       CReportBase.AlignLeft)
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 6)
        table.mergeCells(0, 8, 1, 5)


        prevClientId = None
        prevClientRowIndex = 0
        prevDiagnosisId = None
        prevDiagnosisRowIndex = 0
        cnt = 0
        i = 0
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            clientId = forceInt(record.value('client_id'))
            diagnosisId = forceInt(record.value('diagnosis_id'))
            MKB = forceString(record.value('MKB'))
            MKBEx = forceString(record.value('MKBEx'))
            setDate = forceDate(record.value('setDate'))
            endDate = forceDate(record.value('endDate'))
            diseaseCharacter = forceString(record.value('diseaseCharacter'))
            if diseaseCharacter == '1':
                diseaseCharacter = u'острый'
            elif diseaseCharacter == '3':
                diseaseCharacter = u'хронический'

            traumaType = forceString(record.value('traumaType'))
            diagnosticDate = forceDate(record.value('diagnosticDate'))
            diagnosticHospital = forceString(record.value('diagnosticHospital'))
            diagnosticSanatorium = forceString(record.value('diagnosticSanatorium'))
            diagnosticDispanser = forceString(record.value('diagnosticDispanser'))
            diagnosticPerson = forceString(record.value('diagnosticPerson'))

            i = table.addRow()
            if prevClientId != clientId:
                prevClientId = clientId
                self.mergePatientRows(table, prevClientRowIndex, i)
                prevClientRowIndex = i
                cnt += 1
                table.setText(i, 0, cnt)
                table.setHtml(i, 1, getClientBanner(clientId))

            if prevDiagnosisId != diagnosisId:
                prevDiagnosisId = diagnosisId
                self.mergeDiagnosisRows(table, prevDiagnosisRowIndex, i)
                prevDiagnosisRowIndex = i

                table.setText(i, 2, MKB)
                table.setText(i, 3, MKBEx)
                table.setText(i, 4, forceString(setDate))
                table.setText(i, 5, forceString(endDate))
                table.setText(i, 6, forceString(diseaseCharacter))
                table.setText(i, 7, forceString(traumaType))
            table.setText(i, 8, forceString(diagnosticDate))
            table.setText(i, 9, diagnosticHospital)
            table.setText(i,10, diagnosticSanatorium)
            table.setText(i,11, diagnosticDispanser)
            table.setText(i,12, diagnosticPerson)
        self.mergePatientRows(table, prevClientRowIndex, i+1)
        self.mergeDiagnosisRows(table, prevDiagnosisRowIndex, i+1)
        return doc


    def mergePatientRows(self, table, start, current):
        if start:
            mergeRows = current-start
            if mergeRows>1:
                for j in [0, 1]:
                    table.mergeCells(start, j, mergeRows, 1)


    def mergeDiagnosisRows(self, table, start, current):
        if start:
            mergeRows = current-start
            if mergeRows>1:
                for j in xrange(2, 8):
                    table.mergeCells(start, j, mergeRows, 1)

def selectDataNew(params):
    begDate = params.get('begDate', QtCore.QDate()).toString('yyyy-MM-ddThh:mm:ss')
    endDate = params.get('endDate', QtCore.QDate()).toString('yyyy-MM-ddThh:mm:ss')
    eventType = params.get('eventTypeId')
    chkDiagnosis = params.get('chkDiagnosis')
    chkResult = params.get('chkResult')

    db = QtGui.qApp.db
    where = '''DATE(Event.setDate) >= DATE('%s') AND DATE(Event.execDate) <= DATE('%s') ''' % (begDate, endDate)
    if eventType:
        where += '''AND (Event.`eventType_id` = %s)''' % eventType

    joinResult = ''' JOIN rbResult ON Event.result_id = rbResult.id AND rbResult.notAccount = 0 '''
    if chkResult:
        joinResult = 'INNER' + joinResult
    else:
        joinResult = 'LEFT' + joinResult

    if chkDiagnosis:
        stmtClient = '''Diagnosis'''
        actionMKB = ''''''
        stmtDiagnosis = '''
            INNER JOIN Diagnostic ON Event.id = Diagnostic.event_id AND Diagnostic.deleted = 0 AND %s
            INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id AND Diagnosis.deleted = 0 AND Diagnosis.mod_id IS NULL
            LEFT JOIN Visit ON Event.id = Visit.event_id AND Visit.deleted = 0
            LEFT JOIN Person ON Person.id = Visit.person_id
            INNER JOIN Client ON Client.id = Event.client_id
            LEFT JOIN rbService ON rbService.id = Visit.service_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id
            LEFT JOIN rbPost ON rbPost.id = Person.post_id
            LEFT JOIN Action ON Action.event_id = Event.id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0 AND Action.deleted = 0
            %s
        ''' % (where, joinResult)
    else:
        stmtClient = '''Event'''
        actionMKB = '''Action.MKB as actionMKB,'''
        stmtDiagnosis = '''
            LEFT JOIN Diagnostic ON Event.id = Diagnostic.event_id AND Diagnostic.deleted = 0
            LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id AND Diagnosis.deleted = 0 AND Diagnosis.mod_id IS NULL
            LEFT JOIN Visit ON Event.id = Visit.event_id AND Visit.deleted = 0
            LEFT JOIN Person ON Person.id = Visit.person_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN rbService ON rbService.id = Visit.service_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id
            LEFT JOIN rbPost ON rbPost.id = Person.post_id
            LEFT JOIN Action ON Action.event_id = Event.id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0 AND Action.deleted = 0
            %s
            WHERE %s AND Event.client_id IS NOT NULL
        ''' % (joinResult, where)
    stmt='''
SELECT
    %s.client_id,
    Diagnosis.MKB,
    Diagnosis.setDate,
    Diagnosis.endDate,
    rbDiseaseCharacter.code AS diseaseCharacter,
    Person.lastName,
    Person.firstName,
    Person.patrName,
    rbPost.name as postName,
    Visit.date AS visitDate,
    rbService.name AS serviceName,
    ActionType.name AS actionTypeName,
    Action.begDate AS actionBegDate,
    Action.endDate AS actionEndDate,
    Action.status,
    Action.amount,
    %s
    Event.id as eventId,
    Diagnostic.id as diagnosticId,
    Visit.id as visitId,
    Action.id as actionId
FROM Event
%s
ORDER BY
    visitDate, Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.id, visitId, diagnosticId, actionId
''' % (stmtClient, actionMKB, stmtDiagnosis)
    return db.query(stmt)

class CReportPersonSickListNew(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Заболеваемость: список пациентов')


    def getSetupDialog(self, parent):
        result = CReportPersonSickListNewSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()

        self.chkDiagnosis = params.get('chkDiagnosis')

        if self.chkDiagnosis:
            tableColumns = [
                ('5%', [u'№' ],                                CReportBase.AlignRight),
                ('20%',[u'Пациент'],                            CReportBase.AlignLeft),
                ('5%', [u'Заболевания',         u'Код по МКБ'], CReportBase.AlignLeft),
                ('5%', [u'',                    u'С'],          CReportBase.AlignLeft),
                ('5%', [u'',                    u'По'],         CReportBase.AlignLeft),
                ('5%', [u'',                    u'Характер'],   CReportBase.AlignLeft),

                ('5%', [u'Посещения',           u'Дата'],       CReportBase.AlignLeft),
                ('20%',[u'',                    u'Врач'],       CReportBase.AlignLeft),
                ('5%', [u'',                    u'Услуга'],     CReportBase.AlignLeft),

                ('5%', [u'Мероприятия',         u'Тип'],        CReportBase.AlignLeft),
                ('5%', [u'',                    u'Начато'],     CReportBase.AlignLeft),
                ('5%', [u'',                    u'Окончено'],   CReportBase.AlignLeft),
                ('5%', [u'',                    u'Состояние'],  CReportBase.AlignLeft),
                ('5%', [u'',                    u'Количество'], CReportBase.AlignLeft)
                ]
        else:
            tableColumns = [
                ('5%', [u'№' ],                                CReportBase.AlignRight),
                ('15%',[u'Пациент'],                            CReportBase.AlignLeft),
                ('5%', [u'Заболевания',         u'Код по МКБ'], CReportBase.AlignLeft),
                ('5%', [u'',                    u'С'],          CReportBase.AlignLeft),
                ('5%', [u'',                    u'По'],         CReportBase.AlignLeft),
                ('5%', [u'',                    u'Характер'],   CReportBase.AlignLeft),

                ('5%', [u'Посещения',           u'Дата'],       CReportBase.AlignLeft),
                ('15%',[u'',                    u'Врач'],       CReportBase.AlignLeft),
                ('5%', [u'',                    u'Услуга'],     CReportBase.AlignLeft),

                ('5%', [u'Мероприятия',         u'Тип'],        CReportBase.AlignLeft),
                ('5%', [u'',                    u'Начато'],     CReportBase.AlignLeft),
                ('5%', [u'',                    u'Окончено'],   CReportBase.AlignLeft),
                ('5%', [u'',                    u'Состояние'],  CReportBase.AlignLeft),
                ('5%', [u'',                    u'Количество'], CReportBase.AlignLeft),
                ('10%', [u'',                    u'Код по MKБ'], CReportBase.AlignLeft)
                ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(0, 6, 1, 3)
        if self.chkDiagnosis:
            table.mergeCells(0, 9, 1, 5)
        else:
            table.mergeCells(0, 9, 1, 6)

        self.diagnostic = [[], [], [], [], [], []]
        self.visit = [[], [], [], [], []]
        if self.chkDiagnosis:
            self.action = [[], [], [], [], [], [], []]
        else:
            self.action = [[], [], [], [], [], [], [], []]

        def clearList(self):
            self.diagnostic[0] = [] # id диагноза
            self.diagnostic[1] = [] # код по МКБ
            self.diagnostic[2] = [] # дата С
            self.diagnostic[3] = [] # дата ПО
            self.diagnostic[4] = [] # характер заболевания
            self.diagnostic[5] = [] # посещение, за которым закреплено

            self.visit[0] = [] # id визита
            self.visit[1] = [] # дата визита
            self.visit[2] = [] # врач
            self.visit[3] = [] # услуга
            self.visit[4] = [] # хранит номер строки, разделяющей разные посещения

            self.action[0] = [] # id мероприятия
            self.action[1] = [] # тип мероприятия
            self.action[2] = [] # дата начала
            self.action[3] = [] # дата окончания
            self.action[4] = [] # состояние
            self.action[5] = [] # количество
            self.action[6] = [] # посещение, за которым закреплено
            if not self.chkDiagnosis:
                self.action[7] = [] # код по МКБ

        def addRow(table, currentRow, index, i, indexDeposite):
            oppositeIndex = 0 if index == 1 else 1
            if not currentRow[oppositeIndex] and currentRow[index]:
                indexDeposite[oppositeIndex].append(i)
            if len(indexDeposite[index]) == 0:
                if currentRow[index]:
                    i = table.addRow()
                    currentRow[oppositeIndex] = False
                    return i, currentRow, indexDeposite, i
                else:
                    currentRow[index] = True
                    return i, currentRow, indexDeposite, i
            else:
                currentI = i
                i = indexDeposite[index][0]
                del indexDeposite[index][0]
                return i, currentRow, indexDeposite, currentI

        def tableAddRows(self, table):
            if len(self.diagnostic) > 0 and len(self.visit) > 0 and len(self.action) > 0 and self.clientId != None:
                if self.clientId == 206570:
                    pass
                i = table.addRow()
                currentRow = [False, False]
                startRowClient = i
                table.setText(i, 0, self.number)
                table.setHtml(i, 1, getClientBanner(self.clientId))
                j = 0
                visitIndexLow = 0
                for visitMerge in self.visit[4]:
                    sumDiagnostic = 0
                    sumAction = 0
                    indexDeposite = [[], []]
                    if visitMerge != self.visit[4][0]:
                        i = table.addRow()
                        currentRow = [False, False]
                    table.setText(i, 6, self.visit[1][j])
                    table.setText(i, 7, self.visit[2][j])
                    table.setText(i, 8, self.visit[3][j])
                    for rowNumber in range(len(self.diagnostic[0]) if len(self.diagnostic[0]) >= len(self.action[0]) else len(self.action[0])):
                        if rowNumber < len(self.diagnostic[0]) and self.diagnostic[5][rowNumber] == visitIndexLow:
                            i, currentRow, indexDeposite, currentI = addRow(table, currentRow, 0, i, indexDeposite)
                            table.setText(i, 2, self.diagnostic[1][rowNumber])
                            table.setText(i, 3, self.diagnostic[2][rowNumber])
                            table.setText(i, 4, self.diagnostic[3][rowNumber])
                            table.setText(i, 5, self.diagnostic[4][rowNumber])
                            sumDiagnostic += 1
                            i = currentI
                        if rowNumber < len(self.action[0]) and self.action[6][rowNumber] == visitIndexLow:
                            i, currentRow, indexDeposite, currentI = addRow(table, currentRow, 1, i, indexDeposite)
                            table.setText(i, 9, self.action[1][rowNumber])
                            table.setText(i, 10, self.action[2][rowNumber])
                            table.setText(i, 11, self.action[3][rowNumber])
                            table.setText(i, 12, self.action[4][rowNumber])
                            table.setText(i, 13, self.action[5][rowNumber])
                            if not self.chkDiagnosis:
                                table.setText(i, 14, self.action[7][rowNumber])
                            sumAction += 1
                            i = currentI
                    j += 1
                    if sumDiagnostic == 0:
                        sumDiagnostic = 1
                    if sumAction == 0:
                        sumAction = 1
                    table.mergeCells(startRowClient + visitMerge + sumDiagnostic - 1, 2, sumAction - sumDiagnostic + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumDiagnostic - 1, 3, sumAction - sumDiagnostic + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumDiagnostic - 1, 4, sumAction - sumDiagnostic + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumDiagnostic - 1, 5, sumAction - sumDiagnostic + 1, 1)
                    table.mergeCells(startRowClient + visitMerge, 6, i + visitMerge - startRowClient + 1, 1)
                    table.mergeCells(startRowClient + visitMerge, 7, i + visitMerge - startRowClient + 1, 1)
                    table.mergeCells(startRowClient + visitMerge, 8, i + visitMerge - startRowClient + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumAction - 1, 9, sumDiagnostic - sumAction + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumAction - 1, 10, sumDiagnostic - sumAction + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumAction - 1, 11, sumDiagnostic - sumAction + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumAction - 1, 12, sumDiagnostic - sumAction + 1, 1)
                    table.mergeCells(startRowClient + visitMerge + sumAction - 1, 13, sumDiagnostic - sumAction + 1, 1)
                    if not self.chkDiagnosis:
                        table.mergeCells(startRowClient + visitMerge + sumAction - 1, 14, sumDiagnostic - sumAction + 1, 1)
                    visitIndexLow += 1
                table.mergeCells(startRowClient, 0, i - startRowClient + 1, 1)
                table.mergeCells(startRowClient, 1, i - startRowClient + 1, 1)
            clearList(self)

        self.clientId = None
        self.number = 0
        query = selectDataNew(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            if self.clientId != forceInt(record.value('client_id')) or self.clientId == None:
                tableAddRows(self, table)
                self.clientId = forceInt(record.value('client_id'))
                self.number += 1
                visitIndex = -1
            if len(self.visit[0]) == 0 or (self.visit[0][-1] != forceInt(record.value('visitId')) and forceInt(record.value('visitId')) != 0):
                self.visit[0].append(forceInt(record.value('visitId')))
                self.visit[1].append(forceDateTime(record.value('visitDate')).toString('hh:mm dd.MM.yyyy'))
                if forceString(record.value('lastName')) and forceString(record.value('firstName')) and forceString(record.value('patrName')) and forceString(record.value('postName')):
                    diagnosticPerson = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName')) + u', должность: ' + forceString(record.value('postName'))
                elif forceString(record.value('lastName')) and forceString(record.value('firstName')) and forceString(record.value('patrName')):
                    diagnosticPerson = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
                else:
                    diagnosticPerson = ''
                self.visit[2].append(diagnosticPerson)
                self.visit[3].append(forceString(record.value('serviceName')))
                self.visit[4].append(len(self.diagnostic[0]) if len(self.diagnostic[0]) >= len(self.action[0]) else len(self.action[0]))
                visitIndex += 1
            if len(self.diagnostic[0]) == 0 or (self.diagnostic[0][-1] != forceInt(record.value('diagnosticId')) and forceInt(record.value('diagnosticId')) != 0):
                self.diagnostic[0].append(forceInt(record.value('diagnosticId')))
                self.diagnostic[1].append(forceString(record.value('MKB')))
                self.diagnostic[2].append(forceDate(record.value('setDate')).toString('dd.MM.yyyy'))
                self.diagnostic[3].append(forceDate(record.value('endDate')).toString('dd.MM.yyyy'))
                diseaseCharacter = forceString(record.value('diseaseCharacter'))
                if diseaseCharacter == '1':
                    self.diagnostic[4].append(u'острый')
                elif diseaseCharacter == '3':
                    self.diagnostic[4].append(u'хронический')
                else:
                    self.diagnostic[4].append(u'')
                self.diagnostic[5].append(visitIndex)
            if len(self.action[0]) == 0 or (self.action[0][-1] != forceInt(record.value('actionId')) and forceInt(record.value('actionId')) != 0):
                self.action[0].append(forceInt(record.value('actionId')))
                self.action[1].append(forceString(record.value('actionTypeName')))
                self.action[2].append(forceDate(record.value('actionBegDate')).toString('dd.MM.yyyy'))
                self.action[3].append(forceDate(record.value('actionEndDate')).toString('dd.MM.yyyy'))
                status = forceInt(record.value('status'))
                self.action[4].append(CActionType.retranslateClass(False).statusNames[status] if status in xrange(5) else u'')
                self.action[5].append(forceString(record.value('amount')))
                if not self.chkDiagnosis:
                    self.action[7].append(forceString(record.value('actionMKB')))
                self.action[6].append(visitIndex)
        tableAddRows(self, table)
        return doc

def classToCodes(characterClass):
    if characterClass == 1:
        return ['1']
    elif characterClass == 2:
        return ['3']
    elif characterClass == 3:
        return ['1','3']
    elif characterClass == 4:
        return [None]
    else:
        return []


from Ui_ReportPersonSickListSetup import Ui_ReportPersonSickListSetupDialog


class CReportPersonSickListSetupDialog(QtGui.QDialog, Ui_ReportPersonSickListSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbTraumaType.setTable('rbTraumaType', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
#        self.cmbDiseaseCharacter.setTable('rbDiseaseCharacter', True)
        self.cmbArea.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbArea.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbSocStatusType.setShowFields(CRBComboBox.showNameAndCode)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeIdList', []))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.chkTraumaType.setChecked(params.get('chkTraumaType', False))
        self.chkTraumaTypeAny.setChecked(params.get('chkTraumaTypeAny', False))
        if self.chkTraumaType.isChecked() and not self.chkTraumaTypeAny.isChecked():
            self.cmbTraumaType.setValue(params.get('traumaTypeId', None))
        else:
            self.cmbTraumaType.setValue(None)
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbWorkOrganisation.setValue(params.get('workOrgId', None))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        areaIdEnabled = bool(params.get('areaIdEnabled', False))
        self.chkArea.setChecked(areaIdEnabled)
        self.cmbArea.setEnabled(areaIdEnabled)
        self.cmbArea.setValue(params.get('areaId', None))
        MKBFilter = params.get('MKBFilter', 0)
        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))
        MKBExFilter = params.get('MKBExFilter', 0)
        self.cmbMKBExFilter.setCurrentIndex(MKBExFilter if MKBExFilter else 0)
        self.edtMKBExFrom.setText(params.get('MKBExFrom', 'A00'))
        self.edtMKBExTo.setText(params.get('MKBExTo',   'Z99.9'))
        self.cmbCharacterClass.setCurrentIndex(params.get('characterClass', 0))
        self.chkOnlyFirstTime.setChecked(bool(params.get('onlyFirstTime', False)))
        self.chkAccountAccomp.setChecked(bool(params.get('accountAccomp', False)))
        self.cmbLocality.setCurrentIndex(params.get('locality', 0))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))
        self.chkVisitEmergency.setChecked(params.get('visitEmergency', False))
        self.chkPeriod.setChecked(params.get('regInPeriod', False))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeIdList'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['chkTraumaTypeAny'] = self.chkTraumaTypeAny.isChecked()
        if self.chkTraumaType.isChecked() and not self.chkTraumaTypeAny.isChecked():
            result['traumaTypeId'] = self.cmbTraumaType.value()
        result['chkTraumaType'] = self.chkTraumaType.isChecked()
        result['personId'] = self.cmbPerson.value()
        result['workOrgId'] = self.cmbWorkOrganisation.value()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['areaIdEnabled'] = self.chkArea.isChecked()
        result['areaId'] = self.cmbArea.value()
        result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
        result['MKBFrom']   = forceString(self.edtMKBFrom.text())
        result['MKBTo']     = forceString(self.edtMKBTo.text())
        result['MKBExFilter'] = self.cmbMKBExFilter.currentIndex()
        result['MKBExFrom']   = forceString(self.edtMKBExFrom.text())
        result['MKBExTo']     = forceString(self.edtMKBExTo.text())
        result['characterClass'] = self.cmbCharacterClass.currentIndex()
        result['onlyFirstTime'] = self.chkOnlyFirstTime.isChecked()
        result['accountAccomp'] = self.chkAccountAccomp.isChecked()
        result['locality']      = self.cmbLocality.currentIndex()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        result['visitEmergency'] = self.chkVisitEmergency.isChecked()
        result['regInPeriod'] = self.chkPeriod.isChecked()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        tableEventType = QtGui.qApp.db.table('EventType')
        eventPurposeIdList = self.cmbEventPurpose.value()
        filter = tableEventType['purpose_id'].inlist(eventPurposeIdList) if eventPurposeIdList else getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)



    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)


    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)


    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)


    @QtCore.pyqtSlot(int)
    def on_cmbMKBExFilter_currentIndexChanged(self, index):
        self.edtMKBExFrom.setEnabled(index == 1)
        self.edtMKBExTo.setEnabled(index == 1)
    
    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id = %d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)

from Ui_ReportPersonSickListNewSetup import Ui_ReportPersonSickListNewSetupDialog

class CReportPersonSickListNewSetupDialog(QtGui.QDialog, Ui_ReportPersonSickListNewSetupDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.chkDiagnosis.setChecked(params.get('chkDiagnosis', True))
        self.chkResult.setChecked(params.get('chkResult', True))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['chkDiagnosis'] = self.chkDiagnosis.isChecked()
        result['chkResult'] = self.chkResult.isChecked()
        return result