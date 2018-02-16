# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportDuplicateEventsSetup import Ui_ReportDuplicateEventsSetupDialog
from library.Utils import forceString


def firstSelectKSGcodes(params):
    ids = params.get('eventIds')
    db = QtGui.qApp.db

    tableEvent = db.table('Event')
    tableVisit = db.table('Visit')
    tableRbService = db.table('rbService')

    cond = [
        tableEvent['id'].inlist(ids),
        tableRbService['code'].like('B%')
    ]

    select = [
        tableEvent['id'].alias('eventId'),
        '''GROUP_CONCAT(rbService.code ORDER BY rbService.code ASC SEPARATOR ',')      AS code'''
    ]

    group = [tableEvent['id']]

    queryTable = tableEvent.leftJoin(tableVisit, [tableEvent['id'].eq(tableVisit['event_id']), tableVisit['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableRbService, tableVisit['service_id'].eq(tableRbService['id']))

    return db.query(db.selectStmt(queryTable, select, where=cond, group=group))

def secondSelectKSGcodes(params):
    ids = params.get('eventIds')
    db = QtGui.qApp.db

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')

    cond = [
        tableEvent['id'].inlist(ids),
        tableActionType['code'].like('B%')
    ]

    select = [
        tableEvent['id'].alias('eventId'),
        '''GROUP_CONCAT(ActionType.code ORDER BY ActionType.code ASC SEPARATOR ' ')      AS code'''
    ]

    group = [tableEvent['id']]

    queryTable = tableEvent.leftJoin(tableAction, [tableEvent['id'].eq(tableAction['event_id']), tableAction['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))

    return db.query(db.selectStmt(queryTable, select, where=cond, group=group))

def selectData(params):
    stmt = u'''
SELECT
    Client.id AS clientId,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    EventType.name AS eventTypeName,
    COUNT(DISTINCT Event.id) AS eventCount,
    GROUP_CONCAT(DISTINCT CONCAT_WS('_', Event.id, DATE_FORMAT(Event.setDate, '%%d-%%m-%%Y'), DATE_FORMAT(Event.execDate, '%%d-%%m-%%Y')) ORDER BY Event.id) AS eventList,
    vrbPersonWithSpeciality.name as personName,
    vrbPersonWithSpeciality.orgStructure_id as orgStructureId,
    Diagnosis.MKB AS MKB,
    Event.id      AS eventId
FROM
    Client
    INNER JOIN Event ON Client.id = Event.client_id
    INNER JOIN EventType ON Event.eventType_id = EventType.id
    -- Diagnosis
    INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
    INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id = rbDiagnosisType.id
    INNER JOIN Diagnosis ON
        Diagnostic.diagnosis_id = Diagnosis.id
        AND Diagnosis.deleted = 0
        AND Diagnostic.deleted = 0
        AND (
            rbDiagnosisType.code = '1'
            OR (
                rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id
                AND (
                    NOT EXISTS (
                        SELECT
                            DC.id
                        FROM
                            Diagnostic AS DC
                            INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id
                        WHERE
                            DT.code = '1'
                            AND DC.event_id = Event.id
                    )
                )
            )
        )
    -- END Diagnosis
    LEFT JOIN Visit ON Event.id = Visit.event_id AND Visit.deleted = 0
    LEFT JOIN rbService ON rbService.id = Visit.service_id
    LEFT JOIN Action ON Event.id = Action.event_id
    LEFT JOIN ActionType ON Action.actionType_id = ActionType.id
    LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.execPerson_id
    LEFT JOIN Account_Item ON Event.id = Account_Item.event_id AND Account_Item.deleted = 0
    LEFT JOIN Account ON Account_Item.master_id = Account.id AND Account.deleted = 0

WHERE
    %s
GROUP BY
    Client.id, EventType.id, personName, orgStructureId, MKB, Event.execPerson_id
HAVING
    eventCount > 1 AND Diagnosis.MKB is not null
ORDER BY
    clientId
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypeId = params.get('eventTypeId', None)

    personId = params.get("personId", None)
    orgStructureId = params.get("orgStructureId", None)

    speciality = params.get('speciality', None)

    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableEventType = db.table('EventType')
    tablePerson = db.table("vrbPersonWithSpeciality")
    tableAccountItem = db.table('Account_Item')
    tableAccount = db.table('Account')

    cond = [
        tableClient['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
        tableEventType['deleted'].eq(0)
    ]

    if params.get('type'):
        cond.append(tableEvent['setDate'].dateGe(begDate))
        cond.append(tableEvent['setDate'].dateLe(endDate))
    else:
        cond.append(tableAccount['settleDate'].dateGe(begDate))
        cond.append(tableAccount['settleDate'].dateLe(endDate))

    if eventTypeId is not None:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    if personId is not None:
        cond.append(tablePerson["id"].eq(personId))
    elif orgStructureId is not None:
        cond.append(tablePerson["orgStructure_id"].inlist(getOrgStructureDescendants(orgStructureId)))
    if speciality:
        cond.append(tablePerson['speciality_id'].eq(speciality))

    cond.append(tableEvent['execDate'].isNotNull())
    cond.append('''
        rbService.code LIKE 'B01%'
        OR (Diagnosis.MKB NOT LIKE 'Z%' AND rbService.code LIKE 'B04%')
        OR ActionType.code LIKE 'B01%'
        OR (Diagnosis.MKB NOT LIKE 'Z%' AND ActionType.code LIKE 'B04%')
    ''')

    return db.query(stmt % db.joinAnd(cond))


class CReportDuplicateEventsSetupDialog(QtGui.QDialog, Ui_ReportDuplicateEventsSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpeciality.setTable('rbSpeciality')

        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())


    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get("orgStructureId", None))
        self.cmbPerson.setValue(params.get("personId", None))
        self.cmbSpeciality.setValue(params.get('speciality', None))

    def params(self):
        result = {
            'begDate'           : self.edtBegDate.date(),
            'endDate'           : self.edtEndDate.date(),
            'eventTypeId'       : self.cmbEventType.value(),
            "personId"          : self.cmbPerson.value(),
            "orgStructureId"    : self.cmbOrgStructure.value(),
            'speciality'        : self.cmbSpeciality.value(),
            'eventIds'          : [],
            #Обратите сюда внимание, если захотите добавить еще один чекбокс — работать не будет
            'type'              : self.rb1.isChecked()
        }
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        self.cmbPerson.setSpecialityId(self.cmbSpeciality.value())


class CReportDuplicateEvents(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Проверка законченных случаев по поликлинике")

    def getSetupDialog(self, parent):
        result = CReportDuplicateEventsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('5%',   [u'Код пациента'],     CReportBase.AlignLeft),
            ('20%',  [u'ФИО пациента'],     CReportBase.AlignLeft),
            ('20%',  [u'Врач'],             CReportBase.AlignLeft),
            ('5%',   [u'Код МКБ'],          CReportBase.AlignLeft),
            ('20%',  [u'Тип обращения'],    CReportBase.AlignLeft),
            ('10%',  [u'Код обращения'],    CReportBase.AlignLeft),
            ('10%',  [u'Дата начала'],      CReportBase.AlignLeft),
            ('10%',  [u'Дата выполнения'],  CReportBase.AlignLeft),
            ('30%',  [u'Код услуги'],       CReportBase.AlignRight)
        ]
        table = createTable(cursor, tableColumns)
        eventIdToId = {}

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceString(record.value('clientId')))
            table.setText(i, 1, forceString(record.value('clientName')))
            table.setText(i, 2, forceString(record.value('personName')))
            table.setText(i, 3, forceString(record.value('MKB')))
            table.setText(i, 4, forceString(record.value('eventTypeName')))

            events = [eventInfo.split('_') for eventInfo in forceString(record.value('eventList')).split(',')]
            eventsAmount = len(events)
            rows = [i]
            for eventNumber in xrange(eventsAmount - 1):
                j = table.addRow()
                rows.append(j)
            for column in xrange(5):
                table.mergeCells(i, column, eventsAmount, 1)
            for eventNumber in xrange(eventsAmount):
                row = rows[eventNumber]
                for column, columnInfo in enumerate(events[eventNumber]):
                    table.setText(row, 5 + column, columnInfo)
                    eventIdToId[forceString(events[eventNumber][0])] = row
                    params['eventIds'].append(forceString(events[eventNumber][0]))

        query = firstSelectKSGcodes(params)
        self.addQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            table.setText(eventIdToId[forceString(record.value('eventId'))], 8, forceString(record.value('code')))

        query = secondSelectKSGcodes(params)
        self.addQueryText(forceString((query.lastQuery())))
        while query.next():
            record = query.record()
            table.setText(eventIdToId[forceString(record.value('eventId'))], 8, forceString(record.value('code')))

        return doc

