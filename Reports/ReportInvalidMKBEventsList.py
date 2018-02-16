# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportInvalidMKBEventsListSetup import Ui_ReportInvalidMKBEventsListSetup
from library.Utils import forceString, forceDate


def selectData(params):
    stmt = u'''
SELECT DISTINCT
    Client.id AS clientId,
    Event.externalId,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    Client.birthDate,
    Event.setDate,
    Event.execDate,
    OrgStructure.name AS orgStructureName,
    CONCAT_WS(' ', vrbPersonWithSpeciality.code, vrbPersonWithSpeciality.name) AS person,
    MKB_Tree.DiagID,
    getMKBBlockId(MKB_Tree.DiagID) as BlockID,
    getMKBClassID(MKB_Tree.DiagID) as ClassID,
    Diagnosis.diagnosisType_id,

    (
        CASE WHEN
        Diagnosis.diagnosisType_id IN ('1', '2')
        OR (
            Diagnosis.diagnosisType_id NOT IN ('1', '2')
            AND Diagnosis.id IN     (
                SELECT
                    Diagnosis.id
                FROM
                    Diagnosis
                    INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id
                    INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id = rbDiagnosisType.id
                WHERE
                    Diagnostic.event_id = Event.id
                    AND Diagnosis.deleted = 0
                    AND Diagnostic.deleted = 0
                    AND Diagnostic.person_id = Event.execPerson_id
                    AND (
                        NOT EXISTS (
                            SELECT
                                DC.id
                            FROM
                                Diagnostic AS DC
                                INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id
                            WHERE
                                DT.code in ('1', '2')
                                AND DC.event_id = Event.id
                        )
                    )
            )

        )
        THEN 1 ELSE 0 END
    ) as finalDiagnosisExists,

    Event.eventType_id,
    rbEventProfile.code AS eventProfileCode
FROM
    Event
    INNER JOIN Client ON Client.id = Event.client_id
    INNER JOIN vrbPersonWithSpeciality ON Event.execPerson_id = vrbPersonWithSpeciality.id
    INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
    INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
    INNER JOIN MKB_Tree ON Diagnosis.MKB = MKB_Tree.DiagID
    INNER JOIN Contract ON Event.contract_id = Contract.id
    INNER JOIN OrgStructure ON OrgStructure.id = vrbPersonWithSpeciality.orgStructure_id
    INNER JOIN EventType ON Event.eventType_id = EventType.id
    INNER JOIN rbEventProfile ON rbEventProfile.id = EventType.eventProfile_id
WHERE
    %s
ORDER BY
    clientId, setDate, execDate
'''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId', None)
    financeId = params.get('rbFinance', None)

    tableEvent = db.table('Event')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableContract = db.table('Contract')
    tableDiagnosis = db.table('Diagnosis')
    tableDiagnostic = db.table('Diagnostic')


    cond = db.joinAnd([
        tableEvent['setDate'].isNotNull(),
        tableEvent['execDate'].dateGe(begDate),
        tableEvent['execDate'].dateLe(endDate),
        db.joinOr([
            tablePerson['orgStructure_id'].eq(orgStructureId),
            tablePerson['orgStructure_id'].inInnerStmt(
                "(SELECT id FROM OrgStructure_Ancestors WHERE fullPath LIKE '%" + str(orgStructureId) + "%')"
            )
        ]),
        tableDiagnosis['deleted'].eq(0),
        tableDiagnostic['deleted'].eq(0),
        tableContract['finance_id'].eq(financeId),
    ])

    return db.query(stmt % cond)

class CReportInvalidMKBEventsListSetupDialog(QtGui.QDialog, Ui_ReportInvalidMKBEventsListSetup):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbFinance.setValue(params.get('rbFinance', 2))  # 2 -- код ОМС. Может, лучше бы не плодить магические константы?

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['rbFinance'] = self.cmbFinance.value()
        return result




class CReportInvalidMKBEventsList(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Закрытые обращения, не прошедшие контроль МКБ")
        self.setClarifiableDiagnoses()

    def setClarifiableDiagnoses(self):
        db = QtGui.qApp.db
        query = db.query("select DiagID from MKB_Tree where Prim = '*'")
        self.clarifiableDiagnoses = set()
        while query.next():
            self.clarifiableDiagnoses.add(forceString(query.record().value('DiagID')))

    def getSetupDialog(self, parent):
        result = CReportInvalidMKBEventsListSetupDialog(parent)
        result.setTitle(self.title())
        return result

    unpaidBlockIds = set([
        '(А15-А19)',
        '(А50-А64)',
        '(B20-B24)',
        '(Z20-Z29)',
        '(Z55-Z65)',
        '(Z80-Z99)',
    ])

    unpaidClassIds = set([
        'V',
    ])

    unpaidDiagIds = set([
        'F41.0',
        'F45.3',

        'T12.1',

        'X09',

        'Y84.6',

        'Z00.4',
        'Z00.5',
        'Z00.6',
        'Z02.1',
        'Z02.3',
        'Z02.4',
        'Z02.6',
        'Z02.7',
        'Z02.8',
        'Z02.9',
        'Z03.0',
        'Z03.2',

        'Z04',
        'Z04.0',
        'Z04.1',
        'Z04.2',
        'Z04.3',
        'Z04.4',
        'Z04.5',
        'Z04.6',
        'Z04.7',
        'Z04.8',
        'Z04.9',

        'Z09.3',

        'Z10',
        'Z10.0',
        'Z10.1',
        'Z10.2',
        'Z10.3',

        'Z11.1',
        'Z11.3',
        'Z11.4',

        'Z13.3',

        'Z31.1',
        'Z31.2',
        'Z31.3',
        'Z31.8',
        'Z31.9',

        'Z36',
        'Z36.0',
        'Z36.1',
        'Z36.2',
        'Z36.3',
        'Z36.4',
        'Z36.5',
        'Z36.6',
        'Z36.7',
        'Z36.8',
        'Z36.9',

        'Z41',
        'Z41.0',
        'Z41.1',
        'Z41.2',
        'Z41.3',
        'Z41.4',
        'Z41.5',
        'Z41.6',
        'Z41.7',
        'Z41.8',
        'Z41.9',

        'Z43',
        'Z43.0',
        'Z43.1',
        'Z43.2',
        'Z43.3',
        'Z43.4',
        'Z43.5',
        'Z43.6',
        'Z43.7',
        'Z43.8',
        'Z43.9',

        'Z44',
        'Z44.0',
        'Z44.1',
        'Z44.2',
        'Z44.3',
        'Z44.4',
        'Z44.5',
        'Z44.6',
        'Z44.7',
        'Z44.8',
        'Z44.9',

        'Z45',
        'Z45.0',
        'Z45.1',
        'Z45.2',
        'Z45.3',
        'Z45.4',
        'Z45.5',
        'Z45.6',
        'Z45.7',
        'Z45.8',
        'Z45.9',

        'Z46',
        'Z46.0',
        'Z46.1',
        'Z46.2',
        'Z46.3',
        'Z46.4',
        'Z46.5',
        'Z46.6',
        'Z46.7',
        'Z46.8',
        'Z46.9',

        'Z49',
        'Z49.0',
        'Z49.1',
        'Z49.2',

        'Z50',
        'Z50.0',
        'Z50.1',
        'Z50.2',
        'Z50.3',
        'Z50.4',
        'Z50.5',
        'Z50.6',
        'Z50.7',
        'Z50.8',
        'Z50.9',

        'Z52',
        'Z52.0',
        'Z52.1',
        'Z52.2',
        'Z52.3',
        'Z52.4',
        'Z52.5',
        'Z52.6',
        'Z52.7',
        'Z52.8',
        'Z52.9',

        'Z53',
        'Z53.0',
        'Z53.1',
        'Z53.2',
        'Z53.3',
        'Z53.4',
        'Z53.5',
        'Z53.6',
        'Z53.7',
        'Z53.8',
        'Z53.9',

        'Z54',
        'Z54.0',
        'Z54.1',
        'Z54.2',
        'Z54.3',
        'Z54.4',
        'Z54.5',
        'Z54.6',
        'Z54.7',
        'Z54.8',
        'Z54.9',

        'Z71.0',
        'Z71.2',
        'Z71.4',
        'Z71.5',
        'Z71.6',
        'Z71.7',
        'Z71.8',
        'Z71.9',

        'Z72',
        'Z72.0',
        'Z72.1',
        'Z72.2',
        'Z72.3',
        'Z72.4',
        'Z72.5',
        'Z72.6',
        'Z72.7',
        'Z72.8',
        'Z72.9',

        'Z73',
        'Z73.0',
        'Z73.1',
        'Z73.2',
        'Z73.3',
        'Z73.4',
        'Z73.5',
        'Z73.6',
        'Z73.7',
        'Z73.8',
        'Z73.9',

        'Z74',
        'Z74.0',
        'Z74.1',
        'Z74.2',
        'Z74.3',
        'Z74.4',
        'Z74.5',
        'Z74.6',
        'Z74.7',
        'Z74.8',
        'Z74.9',

        'Z75',
        'Z75.0',
        'Z75.1',
        'Z75.2',
        'Z75.3',
        'Z75.4',
        'Z75.5',
        'Z75.6',
        'Z75.7',
        'Z75.8',
        'Z75.9',

        'Z76',
        'Z76.0',
        'Z76.1',
        'Z76.2',
        'Z76.3',
        'Z76.4',
        'Z76.5',
        'Z76.6',
        'Z76.7',
        'Z76.8',
        'Z76.9',

        'Z93.1',
    ])

    healthCenterAllowedDiagnoses = set([
        'Z00.8',
        'Z01.8',
        'Z13.6',
        'Z71.3'
    ])

    def diagIsUnpaid(self, diagId, blockId, classId):
        return diagId in self.unpaidDiagIds or blockId in self.unpaidBlockIds or classId in self.unpaidClassIds

    def diagNotInSPR20(self):
        # Сейчас предполагается, что диагноз всегда есть в SPR20.
        return False

    def invalidDiagForHealthCenter(self, diag):
        return diag not in self.healthCenterAllowedDiagnoses

    def diagNeedsClarification(self, diagId):
        return diagId in self.clarifiableDiagnoses

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('3%',  [u'№ п/п'], CReportBase.AlignLeft),
            ('5%',  [u'Код'], CReportBase.AlignLeft),
            ('5%',  [u'Внешний идентификатор'], CReportBase.AlignLeft),
            ('20%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('10%', [u'Дата рождения'], CReportBase.AlignLeft),
            ('10%', [u'Период лечения'], CReportBase.AlignLeft),
            ('10%', [u'Подразделение'], CReportBase.AlignLeft),
            ('20%', [u'Врач'], CReportBase.AlignLeft),
            ('5%',  [u'Код МКБ'], CReportBase.AlignLeft),
            ('10%', [u'Контроль'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next():
            record = query.record()
            diagId = forceString(record.value('DiagID'))
            blockId = forceString(record.value('BlockID'))
            classId = forceString(record.value('ClassID'))
            eventProfileCode = forceString(record.value('eventProfileCode'))
            finalDiagnosisExists = record.value('finalDiagnosisExists')

            invalidMKB = True
            reason = u''

            if self.diagIsUnpaid(diagId, blockId, classId):
                reason = u'выставленный диагноз не оплачивается в системе ОМС'
            elif self.diagNotInSPR20():
                reason = u'код МКБ не соответствует справочнику'
            elif eventProfileCode in ['01', '02'] and self.invalidDiagForHealthCenter(diagId):
                reason = u'код МКБ не может быть применен в центре здоровья'
            elif not finalDiagnosisExists:
                reason = u'отсутствует заключительный диагноз'
            elif self.diagNeedsClarification(diagId):
                reason = u'выставленный диагноз <*>  требует уточнения'
            else:
                invalidMKB = False

            if invalidMKB:
                i = table.addRow()
                table.setText(i, 0, i)
                table.setText(i, 1, forceString(record.value('clientId')))
                table.setText(i, 2, forceString(record.value('externalId')))
                table.setText(i, 3, forceString(record.value('clientName')))
                table.setText(i, 4, forceString(record.value('birthDate')))
                table.setText(i, 5, forceDate(record.value('setDate')).toString('dd.MM.yyyy') + '-' + forceDate(record.value('execDate')).toString('dd.MM.yyyy'))
                table.setText(i, 6, forceString(record.value('orgStructureName')))
                table.setText(i, 7, forceString(record.value('person')))
                table.setText(i, 8, forceString(diagId))
                table.setText(i, 9, reason)

        return doc

