# -*- coding: utf-8 -*-
from PyQt4 import QtGui

from Events.Utils import getMKBName
from Orgs.Utils import getOrgStructureDescendants
from Registry.Utils import getClientBanner
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDate, forceRef, forceString


def selectData(clientId, begDate, endDate, eventPurposeId, specialityId, personId, orgStructureId):
    stmt = """
SELECT
  Visit.date        AS date,
  vrbPerson.name    AS person,
  rbSpeciality.name AS speciality,
  rbScene.name      AS scene,
  rbService.code    AS service,
  EventType.name    AS eventType,
  Event.mes_id      AS mes,
  Diagnosis.MKB     AS MKB,
  Diagnosis.MKBEx   AS MKBEx,
  rbResult.name     AS resultName
FROM
  Visit
  LEFT JOIN vrbPerson       ON vrbPerson.id = Visit.person_id
  LEFT JOIN rbSpeciality    ON rbSpeciality.id = vrbPerson.speciality_id
  LEFT JOIN rbScene         ON rbScene.id = Visit.scene_id
  LEFT JOIN rbService       ON rbService.id = Visit.service_id
  LEFT JOIN Event           ON Event.id = Visit.Event_id
  LEFT JOIN EventType       ON EventType.id = Event.eventType_id
  LEFT JOIN Diagnosis       ON Diagnosis.id = getEventPersonDiagnosis(Event.id, Visit.person_id)
  LEFT JOIN Diagnostic      ON Diagnostic.event_id = Event.id AND Diagnostic.diagnosis_id = Diagnosis.id
  LEFT JOIN rbResult        ON rbResult.id = Diagnostic.result_id
WHERE
  %s
ORDER BY
  Visit.date DESC
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableDiagnostic = db.table('Diagnostic')
    tableVisit = db.table('Visit')
    tableVRBPerson = db.table('vrbPerson')

    cond = [
        tableEvent['deleted'].eq(0),
        tableVisit['deleted'].eq(0),
        db.joinOr([tableDiagnostic['deleted'].eq(0), tableDiagnostic['id'].isNull()])
    ]

    if clientId:
        cond.append(tableEvent['client_id'].eq(clientId))
    if begDate:
        cond.append(tableVisit['date'].ge(begDate))
    if endDate:
        cond.append(tableVisit['date'].le(endDate))
    if eventPurposeId:
        tableEventType = db.table('EventType')
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if specialityId:
        cond.append(tableDiagnostic['speciality_id'].eq(specialityId))
    if personId:
        cond.append(tableDiagnostic['person_id'].eq(personId))
    if orgStructureId:
        cond.append(tableVRBPerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    return db.query(stmt % (db.joinAnd(cond)))


class CClientVisits(CReport):
    name = u'Список визитов пациента'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)

    def getSetupDialog(self, parent):
        return None

    def build(self, params):
        clientId = params.get('clientId', None)
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        eventPurposeId = params.get('eventPurposeId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        orgStructureId = params.get('orgStructureId', None)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.setCharFormat(CReportBase.TableBody)
        cursor.insertBlock()
        cursor.insertHtml(getClientBanner(clientId))
        cursor.insertBlock()

        tableColumns = [
            ('10?', [u'Дата'], CReportBase.AlignLeft),
            ('15?', [u'Врач'], CReportBase.AlignLeft),
            ('15?', [u'Специальность'], CReportBase.AlignLeft),
            ('5?', [u'Место'], CReportBase.AlignLeft),
            ('10?', [u'Код услуги'], CReportBase.AlignLeft),
            ('10?', [u'Тип события'], CReportBase.AlignLeft),
            ('5?', [u'МЭС'], CReportBase.AlignLeft),
            ('5?', [u'Код диагноза'], CReportBase.AlignLeft),
            ('20?', [u'Расшифровка диагноза'], CReportBase.AlignLeft),
            ('5?', [u'Результат'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)

        db = QtGui.qApp.db
        query = selectData(clientId, begDate, endDate, eventPurposeId, specialityId, personId, orgStructureId)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceString(forceDate(record.value('date'))))
            table.setText(i, 1, forceString(record.value('person')))
            table.setText(i, 2, forceString(record.value('speciality')))
            table.setText(i, 3, forceString(record.value('scene')))
            table.setText(i, 4, forceString(record.value('service')))
            table.setText(i, 5, forceString(record.value('eventType')))
            table.setText(i, 6, forceString(db.translate('mes.MES', 'id', forceRef(record.value('mes')), 'code')))
            table.setText(i, 9, forceString(record.value('resultName')))
            diagnosisCodes = []
            diagnosisNames = []
            MKB = forceString(record.value('MKB'))
            MKBEx = forceString(record.value('MKBEx'))
            if MKB:
                diagnosisCodes.append(MKB)
                diagnosisNames.append(getMKBName(MKB))
            if MKBEx:
                diagnosisCodes.append(MKBEx)
                diagnosisNames.append(getMKBName(MKBEx))
            table.setText(i, 7, '\n'.join(diagnosisCodes))
            table.setText(i, 8, '\n'.join(diagnosisNames))
        return doc
