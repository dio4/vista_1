# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceDouble, forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from ReportAccountingWork import CAccountingWork

def selectDataNew(params):
    db = QtGui.qApp.db
    begDate        = params.get('begDate', QtCore.QDate())
    endDate        = params.get('endDate', QtCore.QDate())
    eventTypeId    = params.get('eventTypeId', None)
    specialityId   = params.get('specialityId', None)
    personId       = params.get('personId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    detalilPerson  = params.get('detailPerson', False)

    tableAction    = db.table('Action').alias('a')
    tableEvent     = db.table('Event').alias('e')
    tablePerson    = db.table('Person').alias('p')
    tableEventType = db.table('EventType').alias('et')

    cond = [db.joinOr([db.joinAnd([tableAction['endDate'].dateLe(endDate), tableAction['endDate'].dateGe(begDate)]),
                       db.joinAnd([tableAction['begDate'].isNull(), tableEvent['setDate'].dateLe(endDate), tableEvent['setDate'].dateGe(begDate)])]),
            'age(c.birthDate, e.setDate) >= 18']
    group = ''
    order = ''

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if detalilPerson:
        # group = 'GROUP BY p.id'
        order = 'ORDER BY p.lastName'

    stmt = u'''
SELECT
  CONCAT_WS(' ', p.lastName, p.firstName, p.patrName) AS person,
  SUM(IF(at.code='стт005' AND a.person_id=p.id, 1, 0)) AS primaryVisit,
  SUM(IF(at.code IN ('стт006', 'стт007', 'стт008', 'стт010', 'стт011', 'стт012') AND a.person_id=p.id, 1, 0)) AS repeated,
  SUM(IF(at.code IN ('стт005', 'стт006', 'стт007', 'стт008', 'стт010', 'стт011', 'стт012') AND d.MKB REGEXP '^K02\.[0123]$' AND e.setPerson_id=p.id, 1, 0)) AS caries,
  SUM(IF(at.code IN ('стт005', 'стт006', 'стт007', 'стт008', 'стт010', 'стт011', 'стт012') AND d.MKB IN ('K04.0', 'K04.1', 'K04.2') AND e.setPerson_id=p.id, 1, 0)) AS pulpit,
  SUM(IF(at.code IN ('стт005', 'стт006', 'стт007', 'стт008', 'стт010', 'стт011', 'стт012') AND d.MKB IN ('K04.4', 'K04.5', 'K04.6', 'K04.8') AND e.setPerson_id=p.id, 1, 0)) AS periodontite,
  SUM(IF(at.code IN ('стт026', 'стт029', 'стт032') AND a.person_id=p.id, a.amount, 0)) AS cement,
  SUM(IF(at.code IN ('стт027', 'стт030', 'стт033') AND a.person_id=p.id, a.amount, 0)) AS composite,
  SUM(IF(at.code IN ('стт002', 'стт003') AND a.person_id=p.id, a.amount, 0)) AS anestesy,
  SUM(IF(at.code IN ('стт053') AND a.person_id=p.id, a.amount, 0)) AS past,
  SUM(IF(at.code IN ('стт041') AND a.person_id=p.id AND d.MKB IN ('K05.0', 'K05.1', 'K05.2', 'K05.3', 'K05.4', 'K05.5', 'K05.6'), a.amount, 0)) AS scurf,
  SUM(IF(at.code='СанI' AND a.person_id=p.id, 1, 0)) AS debridement,
  ROUND(SUM(IF(a.person_id=p.id, a.uet*a.amount, 0)), 2) AS uet
FROM Event e
  INNER JOIN EventType et ON e.eventType_id = et.id AND et.deleted=0
  INNER JOIN Action a ON e.id=a.event_id AND a.deleted=0
  INNER JOIN ActionType at ON a.actionType_id=at.id AND at.deleted=0
  LEFT JOIN ActionPropertyType apt ON at.id=apt.actionType_id AND at.flatCode IN ('permanentTeeth', 'calfTeeth') AND apt.deleted=0
  LEFT JOIN ActionProperty ap ON a.id=ap.action_id AND ap.type_id=apt.id AND ap.deleted=0
  INNER JOIN Person p ON p.id IN (a.person_id, e.setPerson_id) AND p.deleted=0
  INNER JOIN Client c ON e.client_id = c.id AND c.deleted=0
  LEFT JOIN Diagnostic diag ON e.id=diag.event_id AND diag.deleted=0
  LEFT JOIN Diagnosis d ON diag.diagnosis_id=d.id AND d.deleted=0
  LEFT JOIN rbDiagnosisType rbdt ON diag.diagnosisType_id=rbdt.id AND rbdt.code IN ('1', '2')
WHERE a.deleted=0 AND %s
%s
GROUP BY person %s 
''' % (db.joinAnd(cond), group, order)
    return db.query(stmt)

# '^K02\.[01389]0*$'


class CReportTherapeutic(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Терапевтический отчет')

    def getSetupDialog(self, parent):
        result = CAccountingWork(parent)
        result.setTitle(self.title())
        result.chkGroup.setVisible(False)
        return result

    def build(self, params):
        detailPerson = params.get('detailPerson', False)
        query = selectDataNew(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%2',  [u'№'                                           ], CReportBase.AlignRight),
                        ('%5',  [u'ФИО'                                          ], CReportBase.AlignLeft),
                        ('%5',  [u'Всего'                                        ], CReportBase.AlignLeft),
                        ('%5',  [u'Первичный'                                    ], CReportBase.AlignLeft),
                        ('%5',  [u'Повторный'                                    ], CReportBase.AlignLeft),
                        ('%5',  [u'Запломбировано зубов', u'всего',              ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'кариес',             ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'пульпит',            ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'периодонтит',        ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'периодонтит в первое посещение'], CReportBase.AlignLeft),
                        ('%5',  [u'Количество пломб',     u'всего',               ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'цемент',              ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'композит'            ], CReportBase.AlignLeft),
                        ('%5',  [u'Анестезия'                                    ], CReportBase.AlignLeft),
                        ('%5',  [u'Девитализирующая паста'                       ], CReportBase.AlignLeft),
                        ('%5',  [u'Снятие зубных отложений'                      ], CReportBase.AlignLeft),
                        ('%5',  [u'Санировано'                                   ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ'                                          ], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 3, 1)
        table.mergeCells(0, 4, 3, 1)
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(0, 5, 1, 2)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 5, 1, 4)
        table.mergeCells(0, 5, 1, 5)
        table.mergeCells(1, 10, 2, 1)
        table.mergeCells(0, 10, 1, 2)
        table.mergeCells(0, 10, 1, 3)
        table.mergeCells(0, 13, 3, 1)
        table.mergeCells(0, 14, 3, 1)
        table.mergeCells(0, 15, 3, 1)
        table.mergeCells(0, 16, 3, 1)
        table.mergeCells(0, 17, 3, 1)

        total = [0] * 16
        while query.next():
            record = query.record()
            primaryVisit                = forceInt(record.value('primaryVisit'))
            repeated                    = forceInt(record.value('repeated'))
            caries                      = forceInt(record.value('caries'))
            pulpit                      = forceInt(record.value('pulpit'))
            periodontite                = forceInt(record.value('periodontite'))
            cement                      = forceInt(record.value('cement'))
            composite                   = forceInt(record.value('composite'))
            anestesy                    = forceInt(record.value('anestesy'))
            past                        = forceInt(record.value('past'))
            scurf                       = forceInt(record.value('scurf'))
            debridement                = forceInt(record.value('debridement'))
            uet                         = forceDouble(record.value('uet'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, i - 2)
                table.setText(i, 1, forceString(record.value('person')))
                table.setText(i, 2, primaryVisit + repeated)
                table.setText(i, 3, primaryVisit)
                table.setText(i, 4, repeated)
                table.setText(i, 5,  caries + pulpit + periodontite)
                table.setText(i, 6, caries)
                table.setText(i, 7, pulpit)
                table.setText(i, 8, periodontite)
                table.setText(i, 9, 0)
                table.setText(i, 10, cement + composite)
                table.setText(i, 11, cement)
                table.setText(i, 12, composite)
                table.setText(i, 13, anestesy)
                table.setText(i, 14, past)
                table.setText(i, 15, scurf)
                table.setText(i, 16, debridement)
                table.setText(i, 17, uet)

            total[0] += primaryVisit + repeated
            total[1] += primaryVisit
            total[2] += repeated
            total[3] += caries + pulpit + periodontite
            total[4] += caries
            total[5] += pulpit
            total[6] += periodontite
            total[7] += 0
            total[8] += cement + composite
            total[9] += cement
            total[10] += composite
            total[11] += anestesy
            total[12] += past
            total[13] += scurf
            total[14] += debridement
            total[15] += uet
        i = table.addRow()
        table.setText(i, 0, u'Всего', CReport.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 2, value, CReport.TableTotal)
        return doc