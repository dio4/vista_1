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

def selectData(params):
    db = QtGui.qApp.db
    begDate        = params.get('begDate', QtCore.QDate())
    endDate        = params.get('endDate', QtCore.QDate())
    eventTypeId    = params.get('eventTypeId', None)
    specialityId   = params.get('specialityId', None)
    personId       = params.get('personId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    detalilPerson  = params.get('detailPerson', False)

    tableAction    = db.table('Action')
    tableEvent     = db.table('Event')
    tablePerson    = db.table('Person')
    tableEventType = db.table('EventType')

    cond = [db.joinOr([db.joinAnd([tableAction['endDate'].dateLe(endDate), tableAction['endDate'].dateGe(begDate)]),
                       db.joinAnd([tableAction['begDate'].isNull(), tableEvent['setDate'].dateLe(endDate), tableEvent['setDate'].dateGe(begDate)])]),
            'age(Client.birthDate, Event.setDate) >= 18']
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
        group = 'GROUP BY person'
        order = 'ORDER BY person'

    stmt = u'''SELECT CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code = 'з103', Action.id, NULL)) AS primaryVisit,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code = 'з101', Action.id, NULL)) AS repeated,
                        COUNT(IF(at.flatCode = 'permanentTeeth' AND ActionProperty_String.value LIKE 'л%%' AND Diagnosis.MKB LIKE 'K02%%', Action.id, NULL)) AS permanentCaries,
                        COUNT(IF(at.flatCode = 'calfTeeth' AND ActionProperty_String.value LIKE 'л%%' AND Diagnosis.MKB LIKE 'K02%%', Action.id, NULL)) AS calfCaries,
                        COUNT(IF(at.flatCode = 'permanentTeeth' AND ActionProperty_String.value LIKE 'л' AND Diagnosis.MKB LIKE 'K04%%', Action.id, NULL)) AS complicationPermanentCaries,
                        COUNT(IF(at.flatCode = 'calfTeeth' AND ActionProperty_String.value LIKE 'л%%' AND Diagnosis.MKB LIKE 'K04%%', Action.id, NULL)) AS complicationCalfCaries,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code = 'p1' AND Diagnosis.MKB LIKE 'K04%%', Action.id, NULL)) AS inOneVisit,
                        SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('з20105', 'з20106', 'з20107'), Action.amount, 0)) AS cement,
                        SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('з20108', 'з20109', 'з20110'), Action.amount, 0)) AS composite,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code = 'СанI', Action.id, NULL)) AS debridement1,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII'), Action.id, NULL)) AS debridement2,
                        ROUND(SUM(IF(Action.person_id = Person.id, Action.uet * Action.amount,0)), 2) AS uet
                FROM Action
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                    LEFT JOIN ActionType at ON at.id = Action.actionType_id AND at.flatCode IN ('permanentTeeth', 'calfTeeth') AND at.deleted = 0
                    LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = at.id AND ActionPropertyType.deleted = 0
                    LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                    LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
                    INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN Person ON Person.id IN (Action.person_id, Event.setPerson_id)
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                    LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                WHERE %s AND rbDiagnosisType.id IS NOT NULL AND Action.deleted = 0
                %s
                %s
                ''' % (db.joinAnd(cond), group, order)
    return db.query(stmt)


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
        group = 'GROUP BY p.id'
        order = 'ORDER BY p.lastName'

    stmt = u'''
SELECT
  CONCAT_WS(' ', p.lastName, p.firstName, p.patrName) AS person,
  SUM(IF(at.code='стт005' AND a.person_id=p.id, 1, 0)) AS primaryVisit,
  SUM(IF(at.code IN ('стт006', 'стт007', 'стт008', 'стт010', 'стт011', 'стт012') AND a.person_id=p.id, 1, 0)) AS repeated,
  SUM(IF(at.flatCode='permanentTeeth' AND aps.value LIKE 'л%%' AND d.MKB REGEXP '^K02\.[01389]$' AND e.setPerson_id=p.id, 1, 0)) AS permanentCaries,
  SUM(IF(at.flatCode='calfTeeth' AND aps.value LIKE 'л%%' AND d.MKB  REGEXP '^K02\.[01389]$' AND e.setPerson_id=p.id, 1, 0)) AS calfCaries,
  SUM(IF(at.flatCode='permanentTeeth' AND aps.value LIKE 'л%%' AND d.MKB REGEXP '^K0(4\.[015]|5\.[23])$' AND e.setPerson_id=p.id, 1, 0)) AS complicationPermanentCaries,
  SUM(IF(at.flatCode='calfTeeth' AND aps.value LIKE 'л%%' AND d.MKB REGEXP '^K0(4\.[015]|5\.[23])$' AND e.setPerson_id=p.id, 1, 0)) AS complicationCalfCaries,
  SUM(IF(at.code='p1' AND d.MKB REGEXP '^K0(4\.[015]|5\.[23])$' AND a.person_id=p.id, 1, 0)) as inOneVisit,
  SUM(IF(at.code IN ('стт026', 'стт029', 'стт032') AND a.person_id=p.id, a.amount, 0)) AS cement,
  SUM(IF(at.code IN ('стт027', 'стт030', 'стт033') AND a.person_id=p.id, a.amount, 0)) AS composite,
  SUM(IF(at.code='СанI' AND a.person_id=p.id, 1, 0)) AS debridement1,
  SUM(IF(at.code IN ('СанI', 'СанII') AND a.person_id=p.id, 1, 0)) AS debridement2,
  ROUND(SUM(IF(a.person_id=p.id, a.uet*a.amount, 0)), 2) AS uet
FROM Event e
  INNER JOIN EventType et ON e.eventType_id = et.id AND et.deleted=0
  INNER JOIN Action a ON e.id=a.event_id AND a.deleted=0
  INNER JOIN ActionType at ON a.actionType_id=at.id AND at.deleted=0
  LEFT JOIN ActionPropertyType apt ON at.id=apt.actionType_id AND at.flatCode IN ('permanentTeeth', 'calfTeeth') AND apt.deleted=0
  LEFT JOIN ActionProperty ap ON a.id=ap.action_id AND ap.type_id=apt.id AND ap.deleted=0
  LEFT JOIN ActionProperty_String aps ON ap.id=aps.id
  INNER JOIN Person p ON p.id IN (a.person_id, e.setPerson_id) AND p.deleted=0
  INNER JOIN Client c ON e.client_id = c.id AND c.deleted=0
  LEFT JOIN Diagnostic diag ON e.id=diag.event_id AND diag.deleted=0
  LEFT JOIN Diagnosis d ON diag.diagnosis_id=d.id AND d.deleted=0
  LEFT JOIN rbDiagnosisType rbdt ON diag.diagnosisType_id=rbdt.id AND rbdt.code IN ('1', '2')
WHERE a.deleted=0 AND %s
%s
%s
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
        actionType = params.get('actionTypeCode', 0)
        if actionType == 0:  # 0 = з, 1 = стх
            query = selectData(params)
        else:
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
                        ('%5',  [u'',                     u'кариес',     u'пост.'], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'',           u'мол.' ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'его ослож.', u'пост.'], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'',           u'мол.' ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'',           u'в одно посещение' ], CReportBase.AlignLeft),
                        ('%5',  [u'Количество пломб',     u'всего'               ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'цемент'              ], CReportBase.AlignLeft),
                        ('%5',  [u'',                     u'композит'            ], CReportBase.AlignLeft),
                        ('%5',  [u'Всего санир. в порядке плановой санации',    u'санир. за 1 раз'], CReportBase.AlignLeft),
                        ('%5',  [u'',                                           u'санир. за 2 раз'], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ'                                          ], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 3, 1)
        table.mergeCells(0, 4, 3, 1)
        table.mergeCells(0, 5, 1, 6)
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(1, 6, 1, 2)
        table.mergeCells(1, 8, 1, 3)
        table.mergeCells(0, 11, 1, 3)
        table.mergeCells(1, 11, 2, 1)
        table.mergeCells(1, 12, 2, 1)
        table.mergeCells(1, 13, 2, 1)
        table.mergeCells(0, 14, 1, 2)
        table.mergeCells(1, 14, 2, 1)
        table.mergeCells(1, 15, 2, 1)
        table.mergeCells(0, 16, 3, 1)

        total = [0] * 15
        while query.next():
            record = query.record()
            primaryVisit                = forceInt(record.value('primaryVisit'))
            repeated                    = forceInt(record.value('repeated'))
            permanentCaries             = forceInt(record.value('permanentCaries'))
            calfCaries                  = forceInt(record.value('calfCaries'))
            complicationPermanentCaries = forceInt(record.value('complicationPermanentCaries'))
            complicationCalfCaries      = forceInt(record.value('complicationCalfCaries'))
            inOneVisit                  = forceInt(record.value('inOneVisit'))
            cement                      = forceInt(record.value('cement'))
            composite                   = forceInt(record.value('composite'))
            debridement1                = forceInt(record.value('debridement1'))
            debridement2                = forceInt(record.value('debridement2'))
            uet                         = forceDouble(record.value('uet'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, i - 2)
                table.setText(i, 1, forceString(record.value('person')))
                table.setText(i, 2, primaryVisit + repeated)
                table.setText(i, 3, primaryVisit)
                table.setText(i, 4, repeated)
                table.setText(i, 5,  permanentCaries + complicationPermanentCaries)
                table.setText(i, 6, permanentCaries)
                table.setText(i, 7, calfCaries)
                table.setText(i, 8, complicationPermanentCaries)
                table.setText(i, 9, complicationCalfCaries)
                table.setText(i, 10, inOneVisit)
                table.setText(i, 11, cement + composite)
                table.setText(i, 12, cement)
                table.setText(i, 13, composite)
                table.setText(i, 14, debridement1)
                table.setText(i, 15, debridement2)
                table.setText(i, 16, uet)

            total[0] += primaryVisit + repeated
            total[1] += primaryVisit
            total[2] += repeated
            total[3] += permanentCaries + complicationPermanentCaries
            total[4] += permanentCaries
            total[5] += calfCaries
            total[6] += complicationPermanentCaries
            total[7] += complicationCalfCaries
            total[8] += inOneVisit
            total[9] += cement + composite
            total[10] += cement
            total[11] += composite
            total[12] += debridement1
            total[13] += debridement2
            total[14] += uet
        i = table.addRow()
        table.setText(i, 0, u'Всего', CReport.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 2, value, CReport.TableTotal)
        return doc