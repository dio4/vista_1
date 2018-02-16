# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.Utils      import forceDate, forceInt, forceRef, forceString, getVal, formatName, formatSex, formatSNILS
from Orgs.Orgs          import selectOrganisation
from Orgs.Utils         import getOrgStructureDescendants, getOrgStructures
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId, MKBFilter, MKBFrom, MKBTo, MKBExFilter, MKBExFrom, MKBExTo, personId, specialityId, rowGrouping, forChildren, orgStructureAttachTypeId):

    if rowGrouping == 1: # by orgStructureId
        groupField = 'Person.orgStructure_id'
    elif rowGrouping == 2: # by speciality_id
        groupField = 'Person.speciality_id'
    elif rowGrouping == 3: # by personId
        groupField = 'Diagnosis.person_id'
    else:
        groupField = 'concat(NULL)'

    stmt=u"""
SELECT DISTINCT
    %s as rowKey,
    Client.id, Client.lastName, Client.firstName, Client.patrName, Client.sex, Client.birthDate, Client.SNILS,
    formatClientAddress(ClientAddress0.id) AS regAddress,
    formatClientAddress(ClientAddress1.id) AS locAddress,
    ClientPolicy.serial    AS policySerial,
    ClientPolicy.number    AS policyNumber,
    formatInsurerName(ClientPolicy.insurer_id) as insurer,
    ClientDocument.serial  AS documentSerial,
    ClientDocument.number  AS documentNumber,
    rbDocumentType.code    AS documentType,
    IF(ClientWork.org_id IS NULL, ClientWork.freeInput, Organisation.shortName) AS workName,
    ClientWork.post AS workPost,
    ClientContact.contact AS contact,
    vrbSocStatusType.name AS socStatus,
    if(css.id IS NOT NULL, css.begDate, diag.endDate) AS dateAccount,
    Event.setDate         AS dateView,
    concat(Person.lastName, ' ', left(Person.firstName, 1), '.', left(Person.patrName, 1), '.') AS person,
    Diagnosis.MKB         AS MKB,
    rbDispanser.name AS firstInPeriod
FROM
    Diagnosis
    JOIN rbDispanser ON rbDispanser.id = Diagnosis.dispanser_id
    JOIN Client ON Client.id = Diagnosis.client_id
    LEFT JOIN ClientAddress AS ClientAddress0 ON ClientAddress0.client_id = Diagnosis.client_id
                            AND ClientAddress0.id = (SELECT MAX(id) FROM ClientAddress AS CA0 WHERE CA0.Type=0 and CA0.client_id = Diagnosis.client_id)
    LEFT JOIN Address       ON Address.id = ClientAddress0.address_id
    LEFT JOIN ClientAddress AS ClientAddress1 ON ClientAddress1.client_id = Diagnosis.client_id
                            AND ClientAddress1.id = (SELECT MAX(id) FROM ClientAddress AS CA1 WHERE CA1.Type=1 and CA1.client_id = Diagnosis.client_id)
    LEFT JOIN ClientPolicy  ON ClientPolicy.client_id = Client.id AND
              ClientPolicy.id = (SELECT MAX(CP.id)
                                 FROM   ClientPolicy AS CP
                                 LEFT JOIN rbPolicyType ON rbPolicyType.id = CP.policyType_id
                                 WHERE  CP.client_id = Client.id
                                 AND    rbPolicyType.name LIKE 'ОМС%%'
                                )
    LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND
              ClientDocument.id = (SELECT MAX(CD.id)
                                 FROM   ClientDocument AS CD
                                 LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                 LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                                 WHERE  rbDTG.code = '1' AND CD.client_id = Client.id)
    LEFT JOIN ClientContact ON (ClientContact.client_id = Client.id AND ClientContact.contactType_id=1 AND ClientContact.deleted=0)
    LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
    LEFT JOIN ClientWork    ON ClientWork.client_id = Client.id
                            AND ClientWork.id = (SELECT MAX(CW.id) FROM ClientWork AS CW WHERE CW.deleted=0 AND CW.client_id=Client.id)
    LEFT JOIN Organisation ON Organisation.id = ClientWork.org_id
    LEFT JOIN ClientSocStatus ON ClientSocStatus.client_id
                                        AND ClientSocStatus.id =
                                            (SELECT MAX(ClientSocStatus.id)
                                                FROM ClientSocStatus
                                                JOIN vrbSocStatusType ON vrbSocStatusType.id=ClientSocStatus.socStatusType_id AND vrbSocStatusType.class_id = 1
                                                WHERE ClientSocStatus.deleted = 0 AND ClientSocStatus.client_id = Client.id)
    LEFT JOIN vrbSocStatusType ON ClientSocStatus.socStatusType_id = vrbSocStatusType.id AND vrbSocStatusType.class_id = 1

    LEFT JOIN ClientSocStatus css ON css.client_id
                                    AND css.id = (SELECT MAX(ClientSocStatus.id)
                                                FROM ClientSocStatus
                                        JOIN rbSocStatusClass ON ClientSocStatus.socStatusClass_id = rbSocStatusClass.id
                                            AND rbSocStatusClass.code = '01'
                                        JOIN rbSocStatusType ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
                                            AND rbSocStatusType.code = '2'
                                        WHERE ClientSocStatus.deleted = '0' AND ClientSocStatus.client_id = Client.id)
    LEFT JOIN Diagnosis diag ON diag.id = Diagnosis.id AND diag.dispanser_id = (SELECT disp.id FROM rbDispanser disp WHERE disp.code = '2')
    %s
    LEFT JOIN Person ON Person.id = Event.execPerson_id
    LEFT JOIN vrbPerson ON Person.code = vrbPerson.code
WHERE
    %s
ORDER BY
    rowKey, Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.id
"""
    db = QtGui.qApp.db
    tableDiagnosis       = db.table('Diagnosis')
    tableClient          = db.table('Client')
    tableClientDispanser = db.table('rbDispanser')
    tablePerson = db.table('Person')
    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(tableClientDispanser['observed'].eq(1))
    addDateInRange(cond, tableDiagnosis['endDate'], begDate, endDate)

    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if workOrgId:
        tableClientWork = db.table('ClientWork')
        cond.append(tableClientWork['org_id'].eq(workOrgId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if not forChildren:
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
    if personId:
        cond.append(tableDiagnosis['person_id'].eq(personId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if forChildren:
        additionalFrom = '''LEFT JOIN Event ON Event.client_id = Client.id AND Event.id = (SELECT max(ev.id)
                                                                                           FROM
                                                                                             Event ev
                                                                                           INNER JOIN Diagnostic
                                                                                           ON ev.id = Diagnostic.event_id AND Diagnostic.deleted = 0
                                                                                           WHERE
                                                                                             Diagnostic.diagnosis_id = Diagnosis.id
                                                                                             AND ev.deleted = 0)'''
        cond.append('age(Client.birthDate, Event.setDate) <= 17')
        if orgStructureAttachTypeId:
            tableClientAttach = db.table('ClientAttach')
            attachTypeId = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
            additionalFrom += ''' LEFT JOIN ClientAttach ON ClientAttach.client_id = Client.id AND ClientAttach.id = (SELECT max(clAttach.id)
                                                                                                                    FROM ClientAttach clAttach
                                                                                                                    WHERE clAttach.attachType_id = %s
                                                                                                                    AND clAttach.client_id = Client.id)
                                LEFT JOIN OrgStructure ON OrgStructure.id = ClientAttach.orgStructure_id''' % (attachTypeId)
            orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
            cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))
    else:
        additionalFrom = '''LEFT JOIN Event ON Event.client_id AND Event.id = (SELECT MAX(Event.id)
                                                                               FROM Event
                                                                               LEFT JOIN EventType ON EventType.id = Event.eventType_id AND EventType.code = '03'
                                                                               WHERE Event.deleted = '0' AND Event.client_id = Client.id)'''
    cond.append(' Event.eventType_id NOT IN (SELECT et.id FROM EventType et WHERE et.name LIKE \'%Запись на прием%\') ')
    return db.query(stmt % (groupField, additionalFrom,(db.joinAnd(cond))))

def selectResultData(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId, MKBFilter, MKBFrom, MKBTo, MKBExFilter, MKBExFrom, MKBExTo, personId, forChildren, orgStructureAttachTypeId):
    stmt=u"""
SELECT
    COUNT(Diagnosis.id) AS count,
    COUNT(if(%s, Diagnosis.id, NULL)) AS countInFirst
FROM
    Diagnosis
    LEFT JOIN rbDispanser ON rbDispanser.id = Diagnosis.dispanser_id
    LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnosis.character_id
    LEFT JOIN Client ON Client.id = Diagnosis.client_id
    LEFT JOIN ClientAddress AS ClientAddress0 ON ClientAddress0.client_id = Diagnosis.client_id
                            AND ClientAddress0.id = (SELECT MAX(id) FROM ClientAddress AS CA0 WHERE CA0.Type=0 and CA0.client_id = Diagnosis.client_id)
    LEFT JOIN Address       ON Address.id = ClientAddress0.address_id
    %s
WHERE
    %s
"""
    db = QtGui.qApp.db
    tableDiagnosis       = db.table('Diagnosis')
    tableClient          = db.table('Client')
    tableClientDispanser = db.table('rbDispanser')
    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(tableClientDispanser['observed'].eq(1))
    addDateInRange(cond, tableDiagnosis['endDate'], begDate, endDate)

    if personId:
        cond.append(tableDiagnosis['person_id'].eq(personId))
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if workOrgId:
        tableClientWork = db.table('ClientWork')
        cond.append(tableClientWork['org_id'].eq(workOrgId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
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

    # date = endDate if endDate else QDate.currentDate()
    # firstDay = firstYearDay(date)
    # lastDay = lastYearDay(date)
    # dateCond = []
    # addDateInRange(dateCond, tableDiagnosis['endDate'], firstDay, lastDay)
    addisionalFrom = ''
    if forChildren:
        cond.append('age(Client.birthDate, Diagnosis.endDate) <= 17')
        if orgStructureAttachTypeId:
            tableClientAttach = db.table('ClientAttach')
            attachTypeId = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
            addisionalFrom = '''LEFT JOIN ClientAttach ON ClientAttach.client_id = Client.id AND ClientAttach.id = (SELECT max(clAttach.id)
                                                                                                                    FROM ClientAttach clAttach
                                                                                                                    WHERE clAttach.attachType_id = %s
                                                                                                                    AND clAttach.client_id = Client.id)
                                LEFT JOIN OrgStructure ON OrgStructure.id = ClientAttach.orgStructure_id''' % (attachTypeId)
            orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
            cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))
    return db.query(stmt % (db.joinAnd([tableDiagnosis['setDate'].le(endDate),
                                        tableDiagnosis['setDate'].ge(begDate)]),
                            addisionalFrom,
                            db.joinAnd(cond)))

class CDispObservationList(CReport):
    def __init__(self, parent, forChildren = False):
        CReport.__init__(self, parent)
        self.forChildren = forChildren
        self.setPayPeriodVisible(False)
        self.setTitle(u'Диспансерное наблюдение: список пациентов', u'Диспансерное наблюдение')


    def getSetupDialog(self, parent):
        result = CDispObservationListSetupDialog(parent)
        result.setTitle(self.title())
        result.setVisibleSocStatus(False)
        result.lblOrgStrucutreAttachType.setVisible(False)
        result.cmbOrgStructureAttachType.setVisible(False)
        if self.forChildren:
            result.lblAgeTo.setVisible(False)
            result.lblAge.setVisible(False)
            result.lblAgeYears.setVisible(False)
            result.edtAgeFrom.setVisible(False)
            result.edtAgeTo.setVisible(False)
            result.lblOrgStrucutreAttachType.setVisible(True)
            result.cmbOrgStructureAttachType.setVisible(True)
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
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
        personId = params.get('personId', None)
        specialityId = params.get('specialityId', None)
        rowGrouping      = params.get('rowGrouping', 0)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('2%', [u'№' ],        CReportBase.AlignLeft),
            ('11%',[u'ФИО'],        CReportBase.AlignLeft),
            ('2%', [u'пол'],        CReportBase.AlignCenter),
            ('6%', [u'д.р.'],       CReportBase.AlignLeft),
            ('5%', [u'СНИЛС'],      CReportBase.AlignLeft),
            ('8%',[u'Полис'],       CReportBase.AlignLeft),
            ('8%',[u'Документ'],    CReportBase.AlignLeft),
            ('17%',[u'Адрес'],      CReportBase.AlignLeft),
            ('7%',[u'Контакты'],    CReportBase.AlignLeft),
            ('9%',[u'Занятость'],   CReportBase.AlignLeft),
            ('8%',[u'Льгота'],      CReportBase.AlignLeft),
            ('5%',[u'Дата взятия на учет'],      CReportBase.AlignLeft),
            ('5%',[u'Дата последнего Д - осмотра'],      CReportBase.AlignLeft),
            ('8%',[u'Врач'],      CReportBase.AlignLeft),
            ('7%',[u'МКБ'],         CReportBase.AlignRight),
            ('10%',[u'Примечание'], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)

        query = selectData(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId, MKBFilter, MKBFrom, MKBTo, MKBExFilter, MKBExFrom, MKBExTo,  personId, specialityId, rowGrouping, self.forChildren, orgStructureAttachTypeId)
        
        if rowGrouping == 3: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
        elif rowGrouping == 2: # by speciality_id
            forceKeyVal = forceRef
            keyValToString = lambda specialityId: forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
        elif rowGrouping == 1: # by orgStructureId
            forceKeyVal = forceRef
            keyValToString = lambda orgStructureId: forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
        prevRowKey = ''
        count = 0
        n = 0
        countViewClient = 1
        
        self.setQueryText(forceString(query.lastQuery()))
        currentClient = None
        while query.next():
            record = query.record()
            clientId = forceInt(record.value('id'))
            name = formatName(record.value('lastName'),
                              record.value('firstName'),
                              record.value('patrName'))
            birthDate = forceString(record.value('birthDate'))
            sex = formatSex(forceInt(record.value('sex')))
            SNILS   = formatSNILS(record.value('SNILS'))
            policy  = ' '.join([forceString(record.value('policySerial')), forceString(record.value('policyNumber')), forceString(record.value('insurer'))])
            document= ' '.join([forceString(record.value('documentSerial')), forceString(record.value('documentNumber'))])
            regAddress = forceString(record.value('regAddress'))
            locAddress = forceString(record.value('locAddress'))
            MKB = forceString(record.value('MKB'))
#            endDate = forceDate(record.value('endDate'))
            contacts = forceString(record.value('contact'))
            socStatus = forceString(record.value('socStatus'))
            dateAccount = forceDate(record.value('dateAccount')).toString('dd.MM.yyyy')
            dateView =forceDate(record.value('dateView')).toString('dd.MM.yyyy')
            person = forceString(record.value('person'))
            work= ' '.join([forceString(record.value('workName')), forceString(record.value('workPost'))])
            firstInPeriod = forceString(record.value('firstInPeriod'))
            if rowGrouping:
                rowKey = forceKeyVal(record.value('rowKey'))
                if prevRowKey and rowKey != prevRowKey:
                    i = table.addRow()
                    if not rowKey:
                       table.setText(i, 1, u'всего по ' + '-', CReportBase.TableTotal)
                    else:
                        table.setText(i, 1, u'всего по ' + keyValToString(prevRowKey), CReportBase.TableTotal)
                    table.setText(i, 2, n, CReportBase.TableTotal)
                    table.mergeCells(i, 2, 1, 15)
                    n = 0
                if  rowKey!=prevRowKey:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 15)
                    i = table.addRow()
                    if not rowKey:
                        table.setText(i, 0, '-', CReportBase.TableTotal)
                    else:
                        table.setText(i, 0, keyValToString(rowKey), CReportBase.TableTotal)
                    table.mergeCells(i, 0, 1, 15)
                    prevRowKey = rowKey
            i = table.addRow()
            if not self.forChildren:
                currentClient = None
            if currentClient != clientId:
                currentDateAccount = None
                if self.forChildren:
                    for column in xrange(15):
                        if column not in (14, 13, 12, 11):
                            table.mergeCells(i - countViewClient, column, countViewClient, 1)
                n += 1
                table.setText(i, 0, n)
                table.setText(i, 1, name)
                table.setText(i, 2, sex)
                table.setText(i, 3, birthDate)
                table.setText(i, 4, SNILS)
                table.setText(i, 5, policy)
                table.setText(i, 6, document)
                table.setText(i, 7, regAddress+'\n'+locAddress)
                table.setText(i, 8, contacts)
                table.setText(i, 9, work)
                table.setText(i, 10, socStatus)
                table.setText(i, 11, dateAccount)
                table.setText(i, 12, dateView)
                table.setText(i, 13, person)
                table.setText(i, 14, MKB)
                if self.forChildren:
                    table.setText(i, 15, firstInPeriod)
                count += 1
                countViewClient = 1
                currentClient = clientId
                countDateAccount = 1
            else:
                countViewClient += 1
                if dateAccount != currentDateAccount:
                    table.mergeCells(i - countDateAccount, 11, countDateAccount, 1)
                    table.setText(i, 11, dateAccount)
                    currentDateAccount = dateAccount
                    countDateAccount = 0
                table.setText(i, 12, dateView)
                table.setText(i, 13, person)
                table.setText(i, 14, MKB)
                if self.forChildren:
                    table.setText(i, 15, firstInPeriod)
                countDateAccount += 1

        if rowGrouping:
            i = table.addRow()
            table.setText(i, 1, u'всего по ' + keyValToString(rowKey), CReportBase.TableTotal)
            table.setText(i, 2, n)
            table.mergeCells(i, 2, 1, 15)
            i = table.addRow()
            table.setText(i, 1, u'ВСЕГО', CReportBase.TableTotal)
            table.setText(i, 2, count, CReportBase.TableTotal)
            table.mergeCells(i, 2, 1, 15)
        if self.forChildren:
            sex = params.get('sex', 0)
            query = selectResultData(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId, MKBFilter, MKBFrom, MKBTo, MKBExFilter, MKBExFrom, MKBExTo, personId, self.forChildren, orgStructureAttachTypeId);
            self.setQueryText(forceString(query.lastQuery()))
            if query.first():
                record = query.record()
                count = forceInt(record.value('count'))
                countInFirst = forceInt(record.value('countInFirst'))
                i = table.addRow()
                table.mergeCells(i, 0, 1, 2)
                table.mergeCells(i, 2, 1, 14)
                table.setText(i, 0, u'Всего состоит: ')
                table.setText(i, 2, count)
                i = table.addRow()
                table.mergeCells(i, 0, 1, 2)
                table.mergeCells(i, 2, 1, 14)
                table.setText(i, 0, u'Всего взято впервые: ')
                table.setText(i, 2, countInFirst)
        return doc


from Ui_DispObservationListSetup import Ui_DispObservationSetupDialog


class CDispObservationListSetupDialog(QtGui.QDialog, Ui_DispObservationSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.edtBegDate.canBeEmpty()
        self.cmbArea.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbArea.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbSocStatusType.setTable('rbSocStatusType')
        self.cmbSocStatusClass.setTable('rbSocStatusClass')
        self.cmbSpeciality.setValue(0)


    def setVisibleSocStatus(self, value):
        self.lblSocStatusType.setVisible(value)
        self.lblSocStatusClass.setVisible(value)
        self.cmbSocStatusType.setVisible(value)
        self.cmbSocStatusClass.setVisible(value)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
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
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusType', None))
        self.cmbSocStatusClass.setValue(params.get('socStatusClass', None))
        self.cmbRowGrouping.setCurrentIndex(getVal(params, 'rowGrouping', 0))
        self.cmbOrgStructureAttachType.setValue(params.get('orgStructureAttachTypeId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
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
        result['personId'] = self.cmbPerson.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['socStatusType'] = self.cmbSocStatusType.value()
        result['socStatusClass'] = self.cmbSocStatusClass.value()
        result['rowGrouping'] = self.cmbRowGrouping.currentIndex()
        result['orgStructureAttachTypeId'] = self.cmbOrgStructureAttachType.value()
        return result


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
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)
