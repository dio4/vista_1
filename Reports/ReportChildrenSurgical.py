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
    detailPerson   = params.get('detailPerson', False)
    actionTypeCode = params.get('actionTypeCode', None)

    tableEvent     = db.table('Event')
    tableAction    = db.table('Action')
    tablePerson    = db.table('Person')
    tableEventType = db.table('EventType')

    cond = [db.joinOr([db.joinAnd([tableAction['endDate'].dateLe(endDate), tableAction['endDate'].dateGe(begDate)]),
                       db.joinAnd([tableAction['begDate'].isNull(), tableEvent['setDate'].dateLe(endDate), tableEvent['setDate'].dateGe(begDate)])])]

    group = ''
    order = ''

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if detailPerson:
        group = 'GROUP BY person'
        order = 'ORDER BY person'
    if actionTypeCode:
        stmt = u'''
        SELECT DISTINCTROW
            CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND Action.person_id = Person.id AND ActionType.code IN ('стх001', 'стх002'), Action.id, NULL)) AS countVisit,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND Action.person_id = Person.id AND ActionType.code IN ('стх001', 'стх002') AND age(Client.birthDate, Action.begDate) <= 14, Action.id, NULL)) AS countVisitSchool,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND Action.person_id = Person.id AND ActionType.code IN ('стх001', 'стх002') AND age(Client.birthDate, Action.begDate) > 14, Action.id, NULL)) AS countVisitPreschool,
            sum(IF(Diagnosis.MKB IN ('K04.5', 'K04.4', 'K10.2') AND ActionType.code IN ('стх029'), Action.amount, NULL)) AS field4,
            sum(IF(Diagnosis.MKB = 'K04.5' AND ActionType.code IN ('стх029'), Action.amount, NULL)) AS field5,
            sum(IF( Diagnosis.MKB = 'K04.4' AND ActionType.code IN ('стх029'), Action.amount, NULL)) AS field6,
            sum(IF(Diagnosis.MKB = 'K10.2' AND ActionType.code IN ('стх029'), Action.amount , NULL)) AS field7,
            sum(IF( Diagnosis.MKB = 'K04.5' AND ActionType.code IN ('стх030', 'стх031', 'стх034'), Action.amount, NULL)) AS field9,
            sum(IF(Diagnosis.MKB = 'K04.4' AND ActionType.code IN ('стх030', 'стх031', 'стх034'), Action.amount, NULL)) AS field10,
            sum(IF(Diagnosis.MKB = 'K10.2' AND ActionType.code IN ('стх030', 'стх031', 'стх034'), Action.amount, NULL)) AS field11,
            sum(IF( Diagnosis.MKB = 'K07.3' AND ActionType.code IN ('стх029'), Action.amount, NULL)) AS field12,
            sum(IF(Diagnosis.MKB = 'K07.3' AND ActionType.code IN ('стх030', 'стх031', 'стх034'), Action.amount, NULL)) AS field13,
            sum(IF( Diagnosis.MKB = 'K00.6' AND ActionType.code IN ('стх029','стх030', 'стх031', 'стх034'), Action.amount, NULL))as field14,
             sum(IF(ActionType.code = 'стх029' AND Diagnosis.MKB NOT IN ('K00.6', 'K07.3', 'K10.2', 'K04.4', 'K04.5'), Action.amount, NULL)) AS field15,
            sum( IF(ActionType.code IN ('стх030', 'стх031', 'стх034') AND Diagnosis.MKB NOT IN ('K00.6', 'K07.3', 'K10.2', 'K04.4', 'K04.5'), Action.amount, NULL)) AS field16,

          sum( if(ActionType.code = 'стх029', Action.amount, NULL)) as field17,
          sum( IF(ActionType.code IN ('стх030', 'стх031', 'стх034') , Action.amount, NULL)) as field18,
            sum(if( ActionType.code IN ('сто002', 'сто003'), Action.amount, NULL)) AS field20,
            sum(if(Action.person_id = Person.id AND ActionType.code IN ('сто001'), Action.amount, NULL)) AS field21,
            sum(IF(ActionType.code = 'стх015', Action.amount, NULL)) AS field22,
            sum( IF(Action.person_id = Person.id AND age(Client.birthDate, Action.begDate) <= 7, (SELECT SUM(Action1.amount)
                       FROM Action Action1
                       INNER JOIN ActionType at ON Action1.actionType_id
                       INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                       INNER JOIN ActionProperty ap ON ap.action_id = Action1.id AND ap.type_id = apt.id AND ap.deleted = 0
                       INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id AND ActionProperty_String.value LIKE 'о'
                       WHERE Action1.deleted =0 AND Action.id = Action1.id), NULL)) AS field23,
            SUM( IF(Action.person_id = Person.id ,(SELECT SUM(Action1.amount)
                       FROM Action Action1
                       INNER JOIN ActionType at ON Action1.actionType_id
                       INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                       INNER JOIN ActionProperty ap ON ap.action_id = Action1.id AND ap.type_id = apt.id AND ap.deleted = 0
                       INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id AND ActionProperty_String.value LIKE 'о'
                       WHERE Action1.deleted =0 AND Action.id = Action1.id), NULL)) AS field24,
            ROUND(sum(IF(age(Client.birthDate, Event.setDate) < 18, (SELECT Action1.uet*Action1.amount
                       FROM Action Action1
                       INNER JOIN ActionType at ON Action1.actionType_id
                       INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                       INNER JOIN ActionProperty ap ON ap.action_id = Action1.id AND ap.type_id = apt.id AND ap.deleted = 0
                       INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id AND ActionProperty_String.value LIKE 'о'
                       WHERE Action1.deleted =0 AND Action.id = Action1.id),0)), 2) AS uetOperacion,
            ROUND(sum(IF( age(Client.birthDate, Event.setDate) >= 14, Action.uet*Action.amount, 0)), 2) AS uetAfter14,
            ROUND(sum(IF(Action.event_id = Event.id,Action.uet*Action.amount,0)), 2) AS uet
        FROM Event
            INNER JOIN EventType ON EventType.id = Event.eventType_id
            INNER JOIN Client ON Client.id = Event.client_id
            INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
            INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
            LEFT JOIN ActionProperty AP ON AP.action_id = Action.id
            LEFT JOIN ActionProperty_String AP_String ON AP_String.id = AP.id

            INNER JOIN Person ON Person.id= Action.person_id and Person.id = 49
-- AND Person.id = Event.setPerson_id

            LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
        WHERE %s AND age(Client.birthDate, Event.setDate) < 18  AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
        %s
        %s''' % (db.joinAnd(cond), group, order)
        stmt = stmt.format(begDate=begDate.toString('yyyy-MM-dd'), endDate=endDate.toString('yyyy-MM-dd'))
    else:
        stmt = u'''SELECT
                        CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND Action.person_id = Person.id AND ActionType.code = 'з101', Action.id, NULL)) AS countVisit,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND Action.person_id = Person.id AND ActionType.code = 'з101' AND age(Client.birthDate, Action.begDate) <= 14, Action.id, NULL)) AS countVisitSchool,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND Action.person_id = Person.id AND ActionType.code = 'з101' AND age(Client.birthDate, Action.begDate) > 14, Action.id, NULL)) AS countVisitPreschool,
                        count(IF(Diagnosis.MKB = 'K04.5' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_calfTeeth.id, NULL)) AS field4,
                        count(IF(Diagnosis.MKB = 'K04.4' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_calfTeeth.id, NULL)) AS field5,
                        count(IF(Diagnosis.MKB = 'K10.2' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_calfTeeth.id , NULL)) AS field6,
                        count(IF(Diagnosis.MKB = 'K04.5' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_permanentTeeth.id, NULL)) AS field8,
                        count(IF(Diagnosis.MKB = 'K04.4' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_permanentTeeth.id, NULL)) AS field9,
                        count(IF(Diagnosis.MKB = 'K10.2' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_permanentTeeth.id, NULL)) AS osteom,
                        count(IF(Diagnosis.MKB = 'K07.3' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_calfTeeth.id, NULL)) AS field10,
                        count(IF(Diagnosis.MKB = 'K07.3' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_permanentTeeth.id, NULL)) AS field11,
                        count(IF(Diagnosis.MKB = 'K00.6' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_calfTeeth.id, NULL)) AS field12,
                        count(IF(Diagnosis.MKB NOT IN ('K00.6', 'K07.3', 'K10.2', 'K04.4', 'K04.5') AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_calfTeeth.id, NULL)) AS calfTeethOther,
                        count(IF(Diagnosis.MKB NOT IN ('K00.6', 'K07.3', 'K10.2', 'K04.4', 'K04.5') AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з'), act_permanentTeeth.id, NULL)) AS permanentTeethOther,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code = 'з11102', Action.id, NULL)) AS field15,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code = 'з11101', Action.id, NULL)) AS field16,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code = 'з311', Action.id, NULL)) AS field17,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code IN ('оЖ018к', 'оЖ018и', 'оЖ018л', 'оЖ018м', 'з323', 'з318', 'з322', 'з324', 'з328', 'з329', 'з330') AND age(Client.birthDate, Action.begDate) >= 7, Action.id, NULL)) AS field18,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code IN ('оЖ018к', 'оЖ018и', 'оЖ018л', 'оЖ018м', 'з323', 'з318', 'з328', 'з322', 'з324', 'з329', 'з330') AND age(Client.birthDate, Action.begDate) < 7, Action.id, NULL)) AS field19,
                        ROUND(SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('оЖ018к', 'оЖ018и', 'оЖ018л', 'оЖ018м', 'з323', 'з318', 'з328', 'з322', 'з324', 'з329', 'з330'), Action.uet * Action.amount,0)), 2) AS uetOperacion,
                        ROUND(SUM(IF(Action.person_id = Person.id, IF((act_calfTeeth.id AND act_permanentTeeth.id) OR (act_calfTeeth.id IS NULL AND act_permanentTeeth.id IS NULL), Action.uet * Action.amount, Action.uet), 0)), 2) AS uet,
                        ROUND(SUM(IF(Action.person_id = Person.id AND age(Client.birthDate, Event.setDate) > 14, IF((act_calfTeeth.id AND act_permanentTeeth.id) OR (act_calfTeeth.id IS NULL AND act_permanentTeeth.id IS NULL), Action.uet * Action.amount, Action.uet), 0)), 2) AS uetAfter14
                    FROM Event
                        INNER JOIN EventType ON EventType.id = Event.eventType_id
                        INNER JOIN Client ON Client.id = Event.client_id
                        INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                        INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0

                        LEFT JOIN (SELECT Action.event_id, Action.id
                                  FROM Action
                                  INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode = 'calfTeeth'
                                  INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                                  INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                                  INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id AND ActionProperty_String.value LIKE 'у%%'
                                  WHERE Action.deleted =0) act_calfTeeth ON act_calfTeeth.event_id = Event.id AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з')
                        LEFT JOIN (SELECT Action.event_id, Action.id
                                   FROM Action
                                   INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode = 'permanentTeeth'
                                   INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                                   INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                                   INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id AND ActionProperty_String.value LIKE 'у%%'
                                   WHERE Action.deleted =0) act_permanentTeeth ON act_permanentTeeth.event_id = Event.id AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001к', 'оЖ001з')

                        INNER JOIN Person ON Person.id IN (Action.person_id, Event.setPerson_id)
                        LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id  AND Diagnostic.deleted = 0
                        LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                        LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                    WHERE %s AND age(Client.birthDate, Event.setDate) < 18  AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
                    %s
                    %s''' % (db.joinAnd(cond), group, order)

    return db.query(stmt)


class CReportChildrenSurgical(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Детский хирургический отчет')

    def getSetupDialog(self, parent):
        result = CAccountingWork(parent)
        result.setTitle(self.title())
        result.chkGroup.setVisible(False)
        return result

    def build(self, params):
        if params.get('actionTypeCode', None):
            return self.newBuild(params)
        else:
            return self.oldBuild(params)

    def newBuild(self, params):
        detailPerson = params.get('detailPerson', False)
        # actionTypeCode = params.get('actionTypeCode', None)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%50', [u'ФИО'                         ], CReportBase.AlignRight),
                        ('%5',  [u'Всего'                       ], CReportBase.AlignLeft),
                        ('%5',  [u'до 14 лет'                   ], CReportBase.AlignLeft),
                        ('%5',  [u'старше 14 лет'               ], CReportBase.AlignLeft),
                        ('%5',  [u'МОЛОЧНЫЕ',    u'всего'       ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'хр. п-т'     ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'ою. хр. п-тп'], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'остеомелит'  ], CReportBase.AlignLeft),
                        ('%5',  [u'ПОСТОЯННЫЕ',  u'всего'       ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'хр. п-т'     ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'ою. хр. п-пт'], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'остеомелит'  ], CReportBase.AlignLeft),
                        ('%5',  [u'по орт.',     u'м'           ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'п'           ], CReportBase.AlignLeft),
                        ('%5',  [u'мешающ. пр.'                 ], CReportBase.AlignLeft),
                        ('%5',  [u'прочие',      u'м'           ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'п'           ], CReportBase.AlignLeft),
                        ('%5',  [u'всего',       u'м'           ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'п'           ], CReportBase.AlignLeft),
                        ('%5',  [u'Всего\nудаленных'            ], CReportBase.AlignLeft),
                        ('%5',  [u'Инъекций анестезия/леч.'     ], CReportBase.AlignLeft),
                        ('%5',  [u'апплин.'                     ], CReportBase.AlignLeft),
                        ('%5',  [u'разрезы'                     ], CReportBase.AlignLeft),
                        ('%5',  [u'ОПЕРАЦИИ',    u'дошк.'       ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'всего'       ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ по операциям'            ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ ст.14 лет'               ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ'                         ], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 1, 4)
        table.mergeCells(0, 8, 1, 4)
        table.mergeCells(0, 12, 1, 2)
        table.mergeCells(0, 14, 2, 1)
        table.mergeCells(0, 15, 1, 2)
        table.mergeCells(0, 17, 1, 2)
        table.mergeCells(0, 18, 2, 1)
        table.mergeCells(0, 19, 2, 1)
        table.mergeCells(0, 20, 2, 1)
        table.mergeCells(0, 21, 2, 1)
        table.mergeCells(0, 22, 2, 1)
        table.mergeCells(0, 23, 1, 2)
        table.mergeCells(0, 25, 2, 1)
        table.mergeCells(0, 26, 2, 1)
        table.mergeCells(0, 27, 2, 1)

        total = [0] * (len(tableColumns) - 1)
        while query.next():
            record = query.record()
            countVisit = forceInt(record.value('countVisit'))
            countVisitSchool = forceInt(record.value('countVisitSchool'))
            countVisitPreschool = forceInt(record.value('countVisitPreschool'))
            field4 = forceInt(record.value('field4'))
            field5 = forceInt(record.value('field5'))
            field6 = forceInt(record.value('field6'))
            field7 = forceInt(record.value('field7'))
            field9 = forceInt(record.value('field9'))
            field10 = forceInt(record.value('field10'))
            field11 = forceInt(record.value('field11'))
            field12 = forceInt(record.value('field12'))
            field13 = forceInt(record.value('field13'))
            field14 = forceInt(record.value('field14'))
            field15 = forceInt(record.value('field15'))
            field16 = forceInt(record.value('field16'))
            field17 = forceInt(record.value('field17'))
            field18 = forceInt(record.value('field18'))
            field20 = forceInt(record.value('field20'))
            field21 = forceInt(record.value('field21'))
            field22 = forceInt(record.value('field22'))
            field23 = forceInt(record.value('field23'))
            field24 = forceInt(record.value('field24'))

            # field17 += field4 + field12 + field15
            # field18 += (field9 + field10 + field11) + field13 + field16

            uetOperation = forceDouble(record.value('uetOperacion'))
            uetAfter14 = forceDouble(record.value('uetAfter14'))
            uet = forceDouble(record.value('uet'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, forceString(record.value('person')))
                table.setText(i, 1, countVisit)
                table.setText(i, 2, countVisitSchool)
                table.setText(i, 3, countVisitPreschool)
                table.setText(i, 4, field4)
                table.setText(i, 5, field5)
                table.setText(i, 6, field6)
                table.setText(i, 7, field7)
                table.setText(i, 8, field9 + field10 + field11)
                table.setText(i, 9, field9)
                table.setText(i, 10, field10)
                table.setText(i, 11, field11)
                table.setText(i, 12, field12)
                table.setText(i, 13, field13)
                table.setText(i, 14, field14)
                table.setText(i, 15, field15)
                table.setText(i, 16, field16)
                table.setText(i, 17, field17)
                table.setText(i, 18, field18)
                table.setText(i, 19, field17 + field18)
                table.setText(i, 20, field20)
                table.setText(i, 21, field21)
                table.setText(i, 22, field22)
                table.setText(i, 23, field23)
                table.setText(i, 24, field24)
                table.setText(i, 25, uetOperation)
                table.setText(i, 26, uetAfter14)
                table.setText(i, 27, uet)

            total[0] += countVisit
            total[1] += countVisitSchool
            total[2] += countVisitPreschool
            total[3] += field4
            total[4] += field5
            total[5] += field6
            total[6] += field7
            total[7] += field10 + field9 + field11
            total[8] += field9
            total[9] += field10
            total[10] += field11
            total[11] += field12
            total[12] += field13
            total[13] += field14
            total[14] += field15
            total[15] += field16
            total[16] += field17
            total[17] += field18
            total[18] += field17 + field18
            total[19] += field20
            total[20] += field21
            total[21] += field22
            total[22] += field23
            total[23] += field24
            total[24] += uetOperation
            total[25] += uetAfter14
            total[26] += uet

        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 1, value, CReportBase.TableTotal)
        return doc

    def oldBuild(self, params):
        detailPerson = params.get('detailPerson', False)
        # actionTypeCode = params.get('actionTypeCode', None)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%50', [u'ФИО'                         ], CReportBase.AlignRight),
                        ('%5',  [u'Всего'                       ], CReportBase.AlignLeft),
                        ('%5',  [u'до 14 лет'                   ], CReportBase.AlignLeft),
                        ('%5',  [u'старше 14 лет'               ], CReportBase.AlignLeft),
                        ('%5',  [u'МОЛОЧНЫЕ',    u'всего'       ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'хр. п-т'     ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'ою. хр. п-тп'], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'остеомелит'  ], CReportBase.AlignLeft),
                        ('%5',  [u'ПОСТОЯННЫЕ',  u'всего'       ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'хр. п-т'     ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'ою. хр. п-пт'], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'остеомелит'  ], CReportBase.AlignLeft),
                        ('%5',  [u'по орт.',     u'м'           ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'п'           ], CReportBase.AlignLeft),
                        ('%5',  [u'мешающ. пр.'                 ], CReportBase.AlignLeft),
                        ('%5',  [u'прочие',      u'м'           ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'п'           ], CReportBase.AlignLeft),
                        ('%5',  [u'всего',       u'м'           ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'п'           ], CReportBase.AlignLeft),
                        ('%5',  [u'Всего\nудаленных'            ], CReportBase.AlignLeft),
                        ('%5',  [u'нов./леч.'                   ], CReportBase.AlignLeft),
                        ('%5',  [u'апплин.'                     ], CReportBase.AlignLeft),
                        ('%5',  [u'разрезы'                     ], CReportBase.AlignLeft),
                        ('%5',  [u'ОПЕРАЦИИ',    u'шк.'         ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'дошк.'       ], CReportBase.AlignLeft),
                        ('%5',  [u'',            u'всего'       ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ по операциям'            ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ ст.14 лет'               ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ'                         ], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 1, 4)
        table.mergeCells(0, 8, 1, 4)
        table.mergeCells(0, 12, 1, 2)
        table.mergeCells(0, 14, 2, 1)
        table.mergeCells(0, 15, 1, 2)
        table.mergeCells(0, 17, 1, 2)
        table.mergeCells(0, 18, 2, 1)
        table.mergeCells(0, 19, 2, 1)
        table.mergeCells(0, 20, 2, 1)
        table.mergeCells(0, 21, 2, 1)
        table.mergeCells(0, 22, 2, 1)
        table.mergeCells(0, 23, 1, 3)
        table.mergeCells(0, 26, 2, 1)
        table.mergeCells(0, 27, 2, 1)
        table.mergeCells(0, 28, 2, 1)

        total = [0] * (len(tableColumns) - 1)
        while query.next():
            record = query.record()
            countVisit = forceInt(record.value('countVisit'))
            countVisitSchool = forceInt(record.value('countVisitSchool'))
            countVisitPreschool = forceInt(record.value('countVisitPreschool'))
            field4 = forceInt(record.value('field4'))
            field5 = forceInt(record.value('field5'))
            field6 = forceInt(record.value('field6'))
            field8 = forceInt(record.value('field8'))
            field9 = forceInt(record.value('field9'))
            field10 = forceInt(record.value('field10'))
            field11 = forceInt(record.value('field11'))
            field12 = forceInt(record.value('field12'))
            field15 = forceInt(record.value('field15'))
            field16 = forceInt(record.value('field16'))
            field17 = forceInt(record.value('field17'))
            field18 = forceInt(record.value('field18'))
            field19 = forceInt(record.value('field19'))
            calfTeethOther = forceInt(record.value('calfTeethOther'))
            permanentTeethOther = forceInt(record.value('permanentTeethOther'))
            uetOperation = forceDouble(record.value('uetOperacion'))
            uet = forceDouble(record.value('uet'))
            uetAfter14 = forceDouble(record.value('uetAfter14'))
            osteom = forceInt(record.value('osteom'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, forceString(record.value('person')))
                table.setText(i, 1, countVisit)
                table.setText(i, 2, countVisitSchool)
                table.setText(i, 3, countVisitPreschool)
                table.setText(i, 4, field4 + field5 + field6)
                table.setText(i, 5, field4)
                table.setText(i, 6, field5)
                table.setText(i, 7, field6)
                table.setText(i, 8, field8 + field9 + osteom)
                table.setText(i, 9, field8)
                table.setText(i, 10, field9)
                table.setText(i, 11, osteom)
                table.setText(i, 12, field10)
                table.setText(i, 13, field11)
                table.setText(i, 14, field12)
                table.setText(i, 15, calfTeethOther)
                table.setText(i, 16, permanentTeethOther)
                table.setText(i, 17, field12 + field4 + field5 + field6 + field10 + calfTeethOther)
                table.setText(i, 18, field8 + field9 + osteom + field11 + permanentTeethOther)
                table.setText(i, 19, field12 + field4 + field5 + field6 + field10 + calfTeethOther + field8 + field9 + osteom + field11 + permanentTeethOther)
                table.setText(i, 20, field15)
                table.setText(i, 21, field16)
                table.setText(i, 22, field17)
                table.setText(i, 23, field18)
                table.setText(i, 24, field19)
                table.setText(i, 25, field19 + field18)
                table.setText(i, 26, uetOperation)
                table.setText(i, 27, uetAfter14)
                table.setText(i, 28, uet)

            total[0] += countVisit
            total[1] += countVisitSchool
            total[2] += countVisitPreschool
            total[3] += field4 + field5 + field6
            total[4] += field4
            total[5] += field5
            total[6] += field6
            total[7] += field8 + field9 + osteom
            total[8] += field8
            total[9] += field9
            total[10] += osteom
            total[11] += field10
            total[12] += field11
            total[13] += field12
            total[14] += calfTeethOther
            total[15] += permanentTeethOther
            total[16] += field12 + field4 + field5 + field6 + field10 + calfTeethOther
            total[17] += field8 + field9 + osteom + field11 + permanentTeethOther
            total[18] += field12 + field4 + field5 + field6 + field10 + calfTeethOther + field8 + field9 + osteom + field11 + permanentTeethOther
            total[19] += field15
            total[20] += field16
            total[21] += field17
            total[22] += field18
            total[23] += field19
            total[24] += field19 + field18
            total[25] += uetOperation
            total[26] += uetAfter14
            total[27] += uet

        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 1, value, CReportBase.TableTotal)
        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pz12',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportChildrenSurgical(None)
    w.exec_()
    sys.exit(QtGui.qApp.exec_())


if __name__ == '__main__':
    main()
