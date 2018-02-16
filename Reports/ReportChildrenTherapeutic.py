# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from ReportAccountingWork import CAccountingWork
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDouble, forceInt, forceString


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

    tableEvent     = db.table('Event')
    tablePerson    = db.table('Person')
    tableAction    = db.table('Action')
    tableEventType = db.table('EventType')
    actionTypeCode = params.get('actionTypeCode', None)

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
        stmt = u'''SELECT DISTINCT
            CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
            COUNT(DISTINCT IF((ActionType.code in ('стт002', 'стт010', 'стт001', 'стт009', 'сст004', 'стт004', 'МЭСI', 'МЭСII')), Action.id, NULL)) AS countAllVisits,
            COUNT(DISTINCT IF((ActionType.code in ('стт001', 'стт009', 'сст004', 'стт004', 'МЭСI' )) AND age(Client.birthDate, Event.setDate) <= 14, Action.id, NULL)) AS countPrimaryVisitsBefore14,
            COUNT(DISTINCT IF((ActionType.code in ('стт001', 'стт009', 'сст004', 'стт004', 'МЭСI')) AND age(Client.birthDate, Event.setDate) > 14, Action.id, NULL)) AS countPrimaryVisitsAfter14,
            COUNT(DISTINCT IF((ActionType.code in ('стт002', 'стт010', 'МЭСII')) AND age(Client.birthDate, Event.setDate) <= 14, Action.id, NULL)) AS countRepeatVisitsBefore14,
            COUNT(DISTINCT IF((ActionType.code in ('стт002', 'стт010', 'МЭСII')) AND age(Client.birthDate, Event.setDate) > 14, Action.id, NULL)) AS countRepeatVisitsAfter14,
            COUNT(DISTINCT IF((ActionType.code in ('стт001', 'стт009', 'сст004', 'стт004', 'МЭСI', 'МЭСII', 'стт002', 'стт010')) AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countPrimaryVisitsSchool,
            COUNT(DISTINCT IF((ActionType.code in ('стт001', 'стт009', 'сст004', 'стт004', 'МЭСI', 'МЭСII', 'стт002', 'стт010')) AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countPrimaryVisitsPreschool,
            COUNT(DISTINCT IF((ActionType.code = 'инт') AND a_int.id AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countIntactSchool,
            COUNT(DISTINCT IF((ActionType.code = 'инт') AND a_int.id AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countIntactPrechool,
            COUNT(DISTINCT IF((ActionType.code = 'р/с') AND a_san.id AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countEarlierSanSchool,
            COUNT(DISTINCT IF((ActionType.code = 'р/с') AND a_san.id AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countEarlierSanPrechool,
            COUNT(DISTINCT IF((ActionType.code = 'стт001' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND (Diagnosis.MKB LIKE 'K02%%') AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countNeedTreatmentSchool,
            COUNT(DISTINCT IF((ActionType.code = 'стт001' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND (Diagnosis.MKB LIKE 'K02%%') AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countNeedTreatmentPreschool,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB LIKE 'K02%%' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethCariesBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB LIKE 'K02%%' AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethCariesAfter14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB = 'K04.0' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethPulpitisBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB = 'K04.0' AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethPulpitisAfter14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB in ('K04.4', 'K04.5') AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethPeriodontitisBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB in ('K04.4', 'K04.5') AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethPeriodontitisAfter14,
            count(DISTINCT IF(e_permanentTeeth.id AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB IN ('K04.4', 'K04.5')) AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB IN ('K04.4', 'K04.5')) AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethAfter14,
            count(DISTINCT IF(e_calfTeeth.id AND Diagnosis.MKB LIKE 'K02%%' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countCalfteethCariesBefore14,
            count(DISTINCT IF(e_calfTeeth.id AND Diagnosis.MKB LIKE 'K04%%' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countCalfteethPulpitisBefore14,
            count(DISTINCT IF(e_calfTeeth.id AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB in ('K04.0', 'K04.5')) AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countCalfteethBefore14,
			count(DISTINCT IF(Action.person_id = Person.id AND e_permanentTeeth.id , e_permanentTeeth.id, 0)) AS countPermanentTeethPlomb,
            count(DISTINCT IF(Action.person_id = Person.id AND e_calfTeeth.id AND e_permanentTeeth.id IS NULL , e_calfTeeth.id, 0)) AS countCalfTeethPlomb,
            SUM(IF(Action.person_id = Person.id AND ActionType.code = 'стт035', Action.amount, 0)) AS countRemoved,
            SUM(IF(Action.person_id = Person.id AND (ActionType.code IN ('стт041')), Action.amount, 0)) AS countHygiene,
            SUM(IF(Action.person_id = Person.id AND (ActionType.code IN ('стт020')), Action.amount, NULL)) AS countFtorlak,
            SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('стт049'), Action.amount, 0)) AS countSealant,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND (ActionType.code IN ('стт023')), Action.id, NULL))  AS countHygieneLesson,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND (ActionType.code IN ('стт019')), Action.id, NULL))  AS countMucosal,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII') AND age(Client.birthDate, Event.setDate) > 7, Action.id, NULL)) AS countSanSchool,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII') AND age(Client.birthDate, Event.setDate) <= 7, Action.id, NULL)) AS countSanPreschool,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII') AND age(Client.birthDate, Event.setDate) > 14, Action.id, NULL)) AS countSanAfter14,
            COUNT(DISTINCT IF(Action.person_id = Person.id AND ActionType.code = 'СанI', Action.id, NULL)) AS countSan,
            SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('стт026', 'стт029', 'стт032'), Action.amount, 0)) AS countCement,
            SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('стт027', 'стт030', 'стт033'), Action.amount, 0)) AS countComposite,
            sum(IF(Action.person_id = Person.id AND ActionType.code IN ('стт026', 'стт029', 'стт032', 'стт027', 'стт030', 'стт033'), Action.amount, 0)) AS countPlomb,
            ROUND(SUM(IF(Action.person_id = Person.id, IF(at_mes.code IN ('МЭСI', 'МЭСII'), Account_Item.uet, Action.uet * Action.amount), 0)), 2) AS uet,
            ROUND(SUM(IF(Action.person_id = Person.id AND age(Client.birthDate, Event.setDate) > 14, IF(at_mes.code IN ('МЭСI', 'МЭСII'), Account_Item.uet, Action.uet * Action.amount), 0)), 2) AS uetAfter14
                FROM Event
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                    LEFT JOIN Action a_int ON a_int.event_id = Event.id AND a_int.actionType_id = (SELECT at.id FROM ActionType at WHERE at.code = 'инт') AND a_int.deleted = 0
                    LEFT JOIN Action a_san ON a_san.event_id = Event.id AND a_san.actionType_id = (SELECT at.id FROM ActionType at WHERE at.code = 'р/с') AND a_san.deleted = 0
                    LEFT JOIN ActionType at_mes ON at_mes.id = Action.actionType_id AND at_mes.code IN ('МЭСI', 'МЭСII') AND at_mes.deleted = 0
                    LEFT JOIN ActionPropertyType apt_s ON apt_s.actionType_id = at_mes.id AND apt_s.deleted = 0
                    LEFT JOIN ActionProperty ap_s ON ap_s.action_id = a_int.id AND ap_s.type_id = apt_s.id AND ap_s.deleted = 0
                    LEFT JOIN ActionProperty_String AP_String ON AP_String.id = ap_s.id
                    LEFT JOIN Event e_calfTeeth ON e_calfTeeth.id = Event.id AND e_calfTeeth.id IN (SELECT e.id
                                                                                                    FROM Event e
                                                                                                        INNER JOIN Action ON Action.event_id = e.id AND Action.deleted = 0
                                                                                                        INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode = 'calfTeeth'
                                                                                                        INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                                                                                                        INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                                                                                                        INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id
                                                                                                    WHERE ActionProperty_String.value LIKE 'л%%'
                                                                                                    GROUP BY e.id) AND e_calfTeeth.deleted =0
                    LEFT JOIN Event e_permanentTeeth ON e_permanentTeeth.id = Event.id AND e_permanentTeeth.id IN (SELECT e.id
                                                                                                    FROM Event e
                                                                                                        INNER JOIN Action ON Action.event_id = e.id AND Action.deleted = 0
                                                                                                        INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode = 'permanentTeeth'
                                                                                                        INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                                                                                                        INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                                                                                                        INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id
                                                                                                    WHERE ActionProperty_String.value LIKE 'л%%'
                                                                                                    GROUP BY e.id) AND e_permanentTeeth.deleted = 0
                    INNER JOIN Person ON Person.id = Action.person_id
                    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id  AND Diagnostic.deleted = 0
                    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                    LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                    LEFT JOIN mes.MES mes ON mes.id = Event.MES_id
                    LEFT JOIN Account_Item ON Account_Item.event_id = Event.id AND Account_Item.action_id IS NULL AND Account_Item.deleted = 0
                WHERE %s AND age(Client.birthDate, Event.setDate) < 18  AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
                %s
                %s''' % (db.joinAnd(cond), group, order)
    else:
        stmt = u'''SELECT
            CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
            COUNT(IF(ActionType.code = 'з101' OR ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code IN ('МЭСI', 'МЭСII')) , Action.id, NULL)) AS countAllVisits,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND age(Client.birthDate, Event.setDate) <= 14, Action.id, NULL)) AS countPrimaryVisitsBefore14,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND age(Client.birthDate, Event.setDate) > 14, Action.id, NULL)) AS countPrimaryVisitsAfter14,
            COUNT(IF((ActionType.code = 'з101' OR (Event.MES_id AND at_mes.code = 'МЭСII')) AND age(Client.birthDate, Event.setDate) <= 14, Action.id, NULL)) AS countRepeatVisitsBefore14,
            COUNT(IF((ActionType.code = 'з101' OR (Event.MES_id AND at_mes.code = 'МЭСII')) AND age(Client.birthDate, Event.setDate) > 14, Action.id, NULL)) AS countRepeatVisitsAfter14,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countPrimaryVisitsSchool,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countPrimaryVisitsPreschool,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND a_int.id AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countIntactSchool,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND a_int.id AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countIntactPrechool,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND a_san.id AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countEarlierSanSchool,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND a_san.id AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countEarlierSanPrechool,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB LIKE 'K04%%') AND age(Client.birthDate, Event.setDate) >= 7, Action.id, NULL)) AS countNeedTreatmentSchool,
            COUNT(IF((ActionType.code = 'з103' OR (Event.MES_id AND at_mes.code = 'МЭСI')) AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB LIKE 'K04%%') AND age(Client.birthDate, Event.setDate) < 7, Action.id, NULL)) AS countNeedTreatmentPreschool,
            count(DISTINCT IF(e_calfTeeth.id AND Diagnosis.MKB LIKE 'K02%%' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countCalfteethCariesBefore14,
            count(DISTINCT IF(e_calfTeeth.id AND Diagnosis.MKB LIKE 'K02%%' AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countCalfteethCariesAfter14,
            count(DISTINCT IF(e_calfTeeth.id AND Diagnosis.MKB = 'K04.0' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countCalfteethPulpitisBefore14,
            count(DISTINCT IF(e_calfTeeth.id AND Diagnosis.MKB = 'K04.0' AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countCalfteethPulpitisAfter14,
            count(DISTINCT IF(e_calfTeeth.id AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB = 'K04.0') AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countCalfteethBefore14,
            count(DISTINCT IF(e_calfTeeth.id AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB = 'K04.0') AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countCalfteethAfter14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB LIKE 'K02%%' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethCariesBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB LIKE 'K02%%' AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethCariesAfter14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB IN ('K04.4', 'K04.5') AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethPeriodontitisBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB IN ('K04.4', 'K04.5') AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethPeriodontitisAfter14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB = 'K04.0' AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethPulpitisBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND Diagnosis.MKB = 'K04.0' AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethPulpitisAfter14,
            count(DISTINCT IF(e_permanentTeeth.id AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB IN ('K04.0', 'K04.4', 'K04.5')) AND age(Client.birthDate, Event.setDate) <= 14, Event.id, NULL)) AS countPermanentteethBefore14,
            count(DISTINCT IF(e_permanentTeeth.id AND (Diagnosis.MKB LIKE 'K02%%' OR Diagnosis.MKB IN ('K04.0', 'K04.4', 'K04.5')) AND age(Client.birthDate, Event.setDate) > 14, Event.id, NULL)) AS countPermanentteethAfter14,
            SUM(IF(Action.person_id = Person.id AND ActionType.code = 'з118', Action.amount, 0)) AS countRemoved,
            SUM(IF(Action.person_id = Person.id AND ActionType.code = 'з106', Action.amount, 0)) AS countDevitalizedPaste,
            SUM(IF(Action.person_id = Person.id AND (ActionType.code = 'з126' OR ActionType.code = 'ож055'), Action.amount, 0)) AS countHygiene,
            COUNT(IF(Action.person_id = Person.id AND (ActionType.code IN ('з128', 'з127') OR mes.code = '812010'), Action.id, NULL)) AS countFtorlak,
            SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('з20102', 'ож061ж'), Action.amount, 0)) AS countSealant,
            SUM(IF(Action.person_id = Person.id AND ((Event.MES_id AND at_mes.code IN ('МЭСI', 'МЭСII')) OR ActionType.code = 'з122'), Action.amount, 0)) AS countHygieneLesson,
            SUM(IF(Action.person_id = Person.id AND ActionType.code = 'з123', Action.amount, 0)) AS countHygieneLessonParent,
            COUNT(DISTINCT IF(Event.setPerson_id = Person.id AND Diagnosis.MKB IN ('K12.0', 'K12.1', 'K13.0', 'K13.2', 'K13.3', 'K14.6', 'K14.6', 'B00.2'), Event.id, NULL)) AS countMucosal,
            COUNT(IF(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII') AND age(Client.birthDate, Event.setDate) > 7, Action.id, NULL)) AS countSanSchool,
            COUNT(IF(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII') AND age(Client.birthDate, Event.setDate) <= 7, Action.id, NULL)) AS countSanPreschool,
            COUNT(IF(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII') AND age(Client.birthDate, Event.setDate) > 14, Action.id, NULL)) AS countSanAfter14,
            COUNT(IF(Action.person_id = Person.id AND ActionType.code = 'СанI', Action.id, NULL)) AS countSan,
            SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('з20105', 'з20106', 'з20107'), Action.amount, 0)) AS countCement,
            SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('з20108', 'з20109', 'з20110'), Action.amount, 0)) AS countComposite,
            sum(IF(Action.person_id = Person.id AND e_permanentTeeth.id AND ActionType.code IN ('з20105', 'з20106', 'з20107', 'з20108', 'з20109', 'з20110'), Action.amount, 0)) AS countPermanentTeethPlomb,
            sum(IF(Action.person_id = Person.id AND e_calfTeeth.id AND e_permanentTeeth.id IS NULL AND ActionType.code IN ('з20105', 'з20106', 'з20107', 'з20108', 'з20109', 'з20110'), Action.amount, 0)) AS countCalfTeethPlomb,
            ROUND(SUM(IF(Action.person_id = Person.id, IF(at_mes.code IN ('МЭСI', 'МЭСII'), Account_Item.uet, Action.uet * Action.amount), 0)), 2) AS uet,
            ROUND(SUM(IF(Action.person_id = Person.id AND age(Client.birthDate, Event.setDate) > 14, IF(at_mes.code IN ('МЭСI', 'МЭСII'), Account_Item.uet, Action.uet * Action.amount), 0)), 2) AS uetAfter14
        FROM Event
            INNER JOIN EventType ON EventType.id = Event.eventType_id
            INNER JOIN Client ON Client.id = Event.client_id
            INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
            INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
            LEFT JOIN Action a_int ON a_int.event_id = Event.id AND a_int.actionType_id = (SELECT at.id FROM ActionType at WHERE at.code = 'инт') AND a_int.deleted = 0
            LEFT JOIN Action a_san ON a_san.event_id = Event.id AND a_san.actionType_id = (SELECT at.id FROM ActionType at WHERE at.code = 'р/с') AND a_san.deleted = 0
            LEFT JOIN ActionType at_mes ON at_mes.id = Action.actionType_id AND at_mes.code IN ('МЭСI', 'МЭСII') AND at_mes.deleted = 0
            LEFT JOIN Event e_calfTeeth ON e_calfTeeth.id = Event.id AND e_calfTeeth.id IN (SELECT e.id
                                                                                            FROM Event e
                                                                                                INNER JOIN Action ON Action.event_id = e.id AND Action.deleted = 0
                                                                                                INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode = 'calfTeeth'
                                                                                                INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                                                                                                INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                                                                                                INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id
                                                                                            WHERE ActionProperty_String.value LIKE 'л%%'
                                                                                            GROUP BY e.id) AND e_calfTeeth.deleted =0
            LEFT JOIN Event e_permanentTeeth ON e_permanentTeeth.id = Event.id AND e_permanentTeeth.id IN (SELECT e.id
                                                                                            FROM Event e
                                                                                                INNER JOIN Action ON Action.event_id = e.id AND Action.deleted = 0
                                                                                                INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode = 'permanentTeeth'
                                                                                                INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                                                                                                INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                                                                                                INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id
                                                                                            WHERE ActionProperty_String.value LIKE 'л%%'
                                                                                            GROUP BY e.id) AND e_permanentTeeth.deleted = 0
            INNER JOIN Person ON Person.id = Action.person_id
            LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id  AND Diagnostic.deleted = 0
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
            LEFT JOIN mes.MES mes ON mes.id = Event.MES_id
            LEFT JOIN Account_Item ON Account_Item.event_id = Event.id AND Account_Item.action_id IS NULL AND Account_Item.deleted = 0
        WHERE %s AND age(Client.birthDate, Event.setDate) < 18  AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
        %s
        %s''' % (db.joinAnd(cond), group, order)

    return db.query(stmt)

class CReportChildrenTherapeutic(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        title = u'Детский терапевтический отчет'
        self.setTitle(title)

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

    def oldBuild(self, params):
        detailPerson = params.get('detailPerson', False)
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
                        ('%20', [u'ФИО'                                                                 ], CReportBase.AlignRight),
                        ('%3',  [u'Посещения',                u'всего'                                  ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'первичные',             u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'повторные',             u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'Осмотрено',                u'школьников'                             ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'дошкольников'                           ], CReportBase.AlignLeft),
                        ('%3',  [u'Выявлено',                 u'интактных',             u'школьников'   ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'дошкольников' ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'ранее санирование',     u'школьников'   ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'дошкольников' ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'нуждающихся в лечении', u'школьников'   ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'дошкольников' ], CReportBase.AlignLeft),
                        ('%3',  [u'Лечение постоянных зубов', u'кариес',                u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'пульпит',               u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'периодонтит',           u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'всего вылечено зубов',  u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'Лечение молочных зубов',   u'кариес',                u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'пульпит',               u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'всего вылечено зубов',  u'до 14 лет'    ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'',                      u'старше 14 лет'], CReportBase.AlignLeft),
                        ('%3',  [u'Наложено пломб',           u'постоянные'                             ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'молочные'                               ], CReportBase.AlignLeft),
                        ('%3',  [u'Удалено пломб'                                                       ], CReportBase.AlignLeft),
                        ('%3',  [u'Девитализирующая паста'                                              ], CReportBase.AlignLeft),
                        ('%3',  [u'Проф. гигиена'                                                       ], CReportBase.AlignLeft),
                        ('%3',  [u'Фторлак'                                                             ], CReportBase.AlignLeft),
                        ('%3',  [u'Герметик'                                                            ], CReportBase.AlignLeft),
                        ('%3',  [u'Урок гигиены'                                                        ], CReportBase.AlignLeft),
                        ('%3',  [u'Урок гигиены родителей'                                              ], CReportBase.AlignLeft),
                        ('%3',  [u'Лечение слизистой'                                                   ], CReportBase.AlignLeft),
                        ('%3',  [u'Санировано',               u'школьников'                             ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'дошкольников'                           ], CReportBase.AlignLeft),
                        ('%3',  [u'',                         u'старше 14 лет'                          ], CReportBase.AlignLeft),
                        ('%3',  [u'Санировано в 1 пос'                                                  ], CReportBase.AlignLeft),
                        ('%3',  [u'Пломбы цемент'                                                       ], CReportBase.AlignLeft),
                        ('%3',  [u'Пломбы композит'                                                     ], CReportBase.AlignLeft),
                        ('%3',  [u'Всего пломб'                                                         ], CReportBase.AlignLeft),
                        ('%3',  [u'УЕТ',             u'всего'                                  ], CReportBase.AlignLeft),
                        ('%3',  [u'',                u'ст.14 лет'                              ], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 5)
        table.mergeCells(1, 1, 2, 1)
        table.mergeCells(1, 2, 1, 2)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(0, 8, 1, 6)
        table.mergeCells(1, 8, 1, 2)
        table.mergeCells(1, 10, 1, 2)
        table.mergeCells(1, 12, 1, 2)
        table.mergeCells(0, 14, 1, 8)
        table.mergeCells(1, 14, 1, 2)
        table.mergeCells(1, 16, 1, 2)
        table.mergeCells(1, 18, 1, 2)
        table.mergeCells(1, 20, 1, 2)
        table.mergeCells(0, 22, 1, 6)
        table.mergeCells(1, 22, 1, 2)
        table.mergeCells(1, 24, 1, 2)
        table.mergeCells(1, 26, 1, 2)
        table.mergeCells(0, 28, 1, 2)
        table.mergeCells(1, 28, 2, 1)
        table.mergeCells(1, 29, 2, 1)
        table.mergeCells(0, 30, 3, 1)
        table.mergeCells(0, 31, 3, 1)
        table.mergeCells(0, 32, 3, 1)
        table.mergeCells(0, 33, 3, 1)
        table.mergeCells(0, 34, 3, 1)
        table.mergeCells(0, 35, 3, 1)
        table.mergeCells(0, 36, 3, 1)
        table.mergeCells(0, 37, 3, 1)
        table.mergeCells(0, 38, 1, 3)
        table.mergeCells(1, 38, 2, 1)
        table.mergeCells(1, 39, 2, 1)
        table.mergeCells(1, 40, 2, 1)
        table.mergeCells(0, 41, 3, 1)
        table.mergeCells(0, 42, 3, 1)
        table.mergeCells(0, 43, 3, 1)
        table.mergeCells(0, 44, 3, 1)
        table.mergeCells(0, 45, 1, 2)
        table.mergeCells(1, 45, 2, 1)
        table.mergeCells(1, 46, 2, 1)

        total = [0] * (len(tableColumns) - 1)
        while query.next():
            record = query.record()
            countAllVisits              = forceInt(record.value('countAllVisits'))
            countPrimaryVisitsBefore14  = forceInt(record.value('countPrimaryVisitsBefore14'))
            countPrimaryVisitsAfter14   = forceInt(record.value('countPrimaryVisitsAfter14'))
            countRepeatVisitsBefore14   = forceInt(record.value('countRepeatVisitsBefore14'))
            countRepeatVisitsAfter14    = forceInt(record.value('countRepeatVisitsAfter14'))
            countPrimaryVisitsSchool    = forceInt(record.value('countPrimaryVisitsSchool'))
            countPrimaryVisitsPreschool = forceInt(record.value('countPrimaryVisitsPreschool'))
            countIntactSchool           = forceInt(record.value('countIntactSchool'))
            countIntactPrechool         = forceInt(record.value('countIntactPrechool'))
            countEarlierSanSchool       = forceInt(record.value('countEarlierSanSchool'))
            countEarlierSanPrechool     = forceInt(record.value('countEarlierSanPrechool'))
            countNeedTreatmentSchool    = forceInt(record.value('countNeedTreatmentSchool'))
            countNeedTreatmentPreschool = forceInt(record.value('countNeedTreatmentPreschool'))
            countCalfteethCariesBefore14        = forceInt(record.value('countCalfteethCariesBefore14'))
            countCalfteethCariesAfter14        = forceInt(record.value('countCalfteethCariesAfter14'))
            countCalfteethPulpitisBefore14      = forceInt(record.value('countCalfteethPulpitisBefore14'))
            countCalfteethPulpitisAfter14      = forceInt(record.value('countCalfteethPulpitisAfter14'))
            countPermanentteethPeriodontitisBefore14 = forceInt(record.value('countPermanentteethPeriodontitisBefore14'))
            countPermanentteethPeriodontitisAfter14 = forceInt(record.value('countPermanentteethPeriodontitisAfter14'))
            countCalfteethBefore14              = forceInt(record.value('countCalfteethBefore14'))
            countCalfteethAfter14              = forceInt(record.value('countCalfteethAfter14'))
            countPermanentteethCariesBefore14   = forceInt(record.value('countPermanentteethCariesBefore14'))
            countPermanentteethCariesAfter14   = forceInt(record.value('countPermanentteethCariesAfter14'))
            countPermanentteethPulpitisBefore14 = forceInt(record.value('countPermanentteethPulpitisBefore14'))
            countPermanentteethPulpitisAfter14 = forceInt(record.value('countPermanentteethPulpitisAfter14'))
            countPermanentteethBefore14         = forceInt(record.value('countPermanentteethBefore14'))
            countPermanentteethAfter14         = forceInt(record.value('countPermanentteethAfter14'))
            countRemoved                = forceInt(record.value('countRemoved'))
            countDevitalizedPaste       = forceInt(record.value('countDevitalizedPaste'))
            countHygiene                = forceInt(record.value('countHygiene'))
            countFtorlak                = forceInt(record.value('countFtorlak'))
            countSealant                = forceInt(record.value('countSealant'))
            countHygieneLesson          = forceInt(record.value('countHygieneLesson'))
            countHygieneLessonParent    = forceInt(record.value('countHygieneLessonParent'))
            countMucosal                = forceInt(record.value('countMucosal'))
            countSanSchool              = forceInt(record.value('countSanSchool'))
            countSanPreschool           = forceInt(record.value('countSanPreschool'))
            countSanAfter14             = forceInt(record.value('countSanAfter14'))
            countSan                    = forceInt(record.value('countSan'))
            countCement                 = forceInt(record.value('countCement'))
            countComposite              = forceInt(record.value('countComposite'))
            uet                         = forceDouble(record.value('uet'))
            uetAfter14                  = forceDouble(record.value('uetAfter14'))
            countPermanentTeethPlomb    = forceInt(record.value('countPermanentTeethPlomb'))
            countCalfteethTeethPlomb    = forceInt(record.value('countCalfTeethPlomb'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, forceString(record.value('person')))
                table.setText(i, 1, countAllVisits)
                table.setText(i, 2, countPrimaryVisitsBefore14)
                table.setText(i, 3, countPrimaryVisitsAfter14)
                table.setText(i, 4, countRepeatVisitsBefore14)
                table.setText(i, 5, countRepeatVisitsAfter14)
                table.setText(i, 6, countPrimaryVisitsSchool)
                table.setText(i, 7, countPrimaryVisitsPreschool)
                table.setText(i, 8, countIntactSchool)
                table.setText(i, 9, countIntactPrechool)
                table.setText(i, 10, countEarlierSanSchool)
                table.setText(i, 11, countEarlierSanPrechool)
                table.setText(i, 12, countNeedTreatmentSchool)
                table.setText(i, 13, countNeedTreatmentPreschool)
                table.setText(i, 14, countPermanentteethCariesBefore14)
                table.setText(i, 15, countPermanentteethCariesAfter14)
                table.setText(i, 16, countPermanentteethPulpitisBefore14)
                table.setText(i, 17, countPermanentteethPulpitisAfter14)
                table.setText(i, 18, countPermanentteethPeriodontitisBefore14)
                table.setText(i, 19, countPermanentteethPeriodontitisAfter14)
                table.setText(i, 20, countPermanentteethBefore14)
                table.setText(i, 21, countPermanentteethAfter14)
                table.setText(i, 22, countCalfteethCariesBefore14)
                table.setText(i, 23, countCalfteethCariesAfter14)
                table.setText(i, 24, countCalfteethPulpitisBefore14)
                table.setText(i, 25, countCalfteethPulpitisAfter14)
                table.setText(i, 26, countCalfteethBefore14)
                table.setText(i, 27, countCalfteethAfter14)
                table.setText(i, 28, countPermanentTeethPlomb)
                table.setText(i, 29, countCalfteethTeethPlomb)
                table.setText(i, 30, countRemoved)
                table.setText(i, 31, countDevitalizedPaste)
                table.setText(i, 32, countHygiene)
                table.setText(i, 33, countFtorlak)
                table.setText(i, 34, countSealant)
                table.setText(i, 35, countHygieneLesson)
                table.setText(i, 36, countHygieneLessonParent)
                table.setText(i, 37, countMucosal)
                table.setText(i, 38, countSanSchool)
                table.setText(i, 39, countSanPreschool)
                table.setText(i, 40, countSanAfter14)
                table.setText(i, 41, countSan)
                table.setText(i, 42, countCement)
                table.setText(i, 43, countComposite)
                table.setText(i, 44, countCement + countComposite)
                table.setText(i, 45, uet)
                table.setText(i, 46, uetAfter14)

            total[0] += countAllVisits
            total[1] += countPrimaryVisitsBefore14
            total[2] += countPrimaryVisitsAfter14
            total[3] += countRepeatVisitsBefore14
            total[4] += countRepeatVisitsAfter14
            total[5] += countPrimaryVisitsSchool
            total[6] += countPrimaryVisitsPreschool
            total[7] += countIntactSchool
            total[8] += countIntactPrechool
            total[9] += countEarlierSanSchool
            total[10] += countEarlierSanPrechool
            total[11] += countNeedTreatmentSchool
            total[12] += countNeedTreatmentPreschool
            total[13] += countPermanentteethCariesBefore14
            total[14] += countPermanentteethCariesAfter14
            total[15] += countPermanentteethPulpitisBefore14
            total[16] += countPermanentteethPulpitisAfter14
            total[17] += countPermanentteethPeriodontitisBefore14
            total[18] += countPermanentteethPeriodontitisAfter14
            total[19] += countPermanentteethBefore14
            total[20] += countPermanentteethAfter14
            total[21] += countCalfteethCariesBefore14
            total[22] += countCalfteethCariesAfter14
            total[23] += countCalfteethPulpitisBefore14
            total[24] += countCalfteethPulpitisAfter14
            total[25] += countCalfteethBefore14
            total[26] += countCalfteethAfter14
            total[27] += countPermanentTeethPlomb
            total[28] += countCalfteethTeethPlomb
            total[29] += countRemoved
            total[30] += countDevitalizedPaste
            total[31] += countHygiene
            total[32] += countFtorlak
            total[33] += countSealant
            total[34] += countHygieneLesson
            total[35] += countHygieneLessonParent
            total[36] += countMucosal
            total[37] += countSanSchool
            total[38] += countSanPreschool
            total[39] += countSanAfter14
            total[40] += countSan
            total[41] += countCement
            total[42] += countComposite
            total[43] += countCement + countComposite
            total[44] += uet
            total[45] += uetAfter14

        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 1, value, CReportBase.TableTotal)

        return doc

    def getUetData(self, begDate, endDate, orgStructureId):
        db = QtGui.qApp.db

        stmt = u"""
SELECT
	SUM(amount) AS totalAmount,
    SUM(sum) AS totalSum,
    SUM(uet) AS totalUet,
    SUM(uetAfter14) AS totalUetAfter14
FROM (
    SELECT
        SUM(Account_Item.amount) AS amount,
        SUM(Account_Item.sum) AS sum,
        SUM(Account_Item.uet) AS uet,
        SUM(IF(age(Client.birthDate, Event.setDate) > 14, Account_Item.uet, 0)) AS uetAfter14
    FROM Account_Item
    LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
    LEFT JOIN Event           ON Event.id = Account_Item.event_id
    LEFT JOIN Client 		  ON Client.id = Event.client_id
    LEFT JOIN Contract        ON Contract.id = Account.contract_id
    LEFT JOIN EventType       ON EventType.id = Event.eventType_id
    LEFT JOIN rbService       ON rbService.id = IF(Account_Item.service_id IS NULL, EventType.service_id, Account_Item.service_id)
    LEFT JOIN Diagnostic      ON Diagnostic.event_id = Event.id
    LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
    LEFT JOIN Person          ON Person.id = Diagnostic.person_id
    LEFT JOIN rbSpeciality    ON rbSpeciality.id = Person.speciality_id
    LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
    WHERE
        Account_Item.visit_id IS NULL
        AND Account_Item.deleted = 0
        AND Account_Item.action_id IS NULL
        AND Diagnostic.deleted = 0
        AND rbDiagnosisType.code in ('1','2')
        AND ((Account_Item.`reexposeItem_id` IS NULL) AND (Account_Item.`deleted` = 0) AND (Account.`deleted` = 0)
        AND (Event.`execDate` >= '{begDate}') AND (Event.`execDate` < '{endDate}')
        AND (Person.`orgStructure_id` IN ({orgStructure})))
UNION
    SELECT
        SUM(Account_Item.amount) AS amount,
        SUM(Account_Item.sum) AS sum,
        SUM(Account_Item.uet) AS uet,
        SUM(IF(age(Client.birthDate, Event.setDate) > 14, Account_Item.uet, 0)) AS uetAfter14
    FROM Account_Item
    LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
    LEFT JOIN Event           ON Event.id = Account_Item.event_id
    LEFT JOIN Client 		  ON Client.id = Event.client_id
    LEFT JOIN EventType       ON EventType.id = Event.eventType_id
    LEFT JOIN Contract        ON Contract.id = Account.contract_id
    LEFT JOIN Visit        ON Visit.id = Account_Item.visit_id
    LEFT JOIN rbService    ON rbService.id = IF(Account_Item.service_id IS NULL, Visit.service_id, Account_Item.service_id)
    LEFT JOIN Person       ON Person.id = Visit.person_id
    LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
    LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
    WHERE
        Account_Item.visit_id IS NOT NULL
        AND Account_Item.deleted = 0
        AND Account_Item.action_id IS NULL
        AND ((Account_Item.`reexposeItem_id` IS NULL) AND (Account_Item.`deleted` = 0) AND (Account.`deleted` = 0)
        AND (Visit.`date` >= '{begDate}') AND (Visit.`date` < '{endDate}')
        AND (Person.`orgStructure_id` IN ({orgStructure})))
UNION
    SELECT
        SUM(Account_Item.amount) AS amount,
        SUM(Account_Item.sum) AS sum,
        SUM(Account_Item.uet) AS uet,
        SUM(IF(age(Client.birthDate, Event.setDate) > 14, Account_Item.uet, 0)) AS uetAfter14
    FROM Account_Item
    LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
    LEFT JOIN Event           ON Event.id = Account_Item.event_id
    LEFT JOIN Client 		  ON Client.id = Event.client_id
    LEFT JOIN EventType       ON EventType.id = Event.eventType_id
    LEFT JOIN Contract        ON Contract.id = Account.contract_id
    LEFT JOIN Action       ON Action.id = Account_Item.action_id
    LEFT JOIN ActionType   ON ActionType.id = Action.actionType_id
    LEFT JOIN rbService    ON rbService.id = Account_Item.service_id
    LEFT JOIN Person       ON Person.id = Action.person_id
    LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
    LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
    LEFT JOIN OrgStructure_ActionType ON ActionType.id = OrgStructure_ActionType.actionType_id
    WHERE
        Account_Item.visit_id IS NULL
        AND Account_Item.deleted = 0
        AND Account_Item.action_id IS NOT NULL
        AND ((Account_Item.`reexposeItem_id` IS NULL) AND (Account_Item.`deleted` = 0) AND (Account.`deleted` = 0)
        AND (Action.`endDate` >= '{begDate}') AND (Action.`endDate` < '{endDate}')
        AND (Person.`orgStructure_id` IN ({orgStructure})))
) AS Uet
        """.format(begDate=begDate, endDate=endDate, orgStructure=orgStructureId if orgStructureId else 15)

        query = db.query(stmt)
        result = {
            'uet': 0.0,
            'uetAfter14': 0.0
        }
        while query.next():
            record = query.record()
            result['uet'] += forceDouble(record.value('totalUet'))
            result['uetAfter14'] += forceDouble(record.value('totalUetAfter14'))

        return result

    def newBuild(self, params):
        detailPerson = params.get('detailPerson', False)
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
            ('%20', [u'ФИО'], CReportBase.AlignRight),
            ('%3', [u'Посещения', u'всего'], CReportBase.AlignLeft),
            ('%3', [u'', u'первичные', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'старше 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'повторные', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'старше 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'Осмотрено', u'школьников'], CReportBase.AlignLeft),
            ('%3', [u'', u'дошкольников'], CReportBase.AlignLeft),
            ('%3', [u'Выявлено', u'интактных', u'школьников'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'дошкольников'], CReportBase.AlignLeft),
            ('%3', [u'', u'ранее санирование', u'школьников'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'дошкольников'], CReportBase.AlignLeft),
            ('%3', [u'', u'нуждающихся в лечении', u'школьников'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'дошкольников'], CReportBase.AlignLeft),
            ('%3', [u'Лечение постоянных зубов', u'кариес', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'старше 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'пульпит', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'старше 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'периодонтит', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'старше 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'всего вылечено зубов', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'', u'старше 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'Лечение молочных зубов', u'кариес', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'пульпит', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'', u'всего вылечено зубов', u'до 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'Наложено пломб', u'постоянные'], CReportBase.AlignLeft),
            ('%3', [u'', u'молочные'], CReportBase.AlignLeft),
            ('%3', [u'Удалено пломб'], CReportBase.AlignLeft),
            ('%3', [u'Проф. гигиена'], CReportBase.AlignLeft),
            ('%3', [u'Фторлак'], CReportBase.AlignLeft),
            ('%3', [u'Герметик'], CReportBase.AlignLeft),
            ('%3', [u'Урок гигиены'], CReportBase.AlignLeft),
            ('%3', [u'Лечение слизистой'], CReportBase.AlignLeft),
            ('%3', [u'Санировано', u'школьников'], CReportBase.AlignLeft),
            ('%3', [u'', u'дошкольников'], CReportBase.AlignLeft),
            ('%3', [u'', u'старше 14 лет'], CReportBase.AlignLeft),
            ('%3', [u'Санировано в 1 пос'], CReportBase.AlignLeft),
            ('%3', [u'Пломбы цемент'], CReportBase.AlignLeft),
            ('%3', [u'Пломбы композит'], CReportBase.AlignLeft),
            ('%3', [u'Всего пломб'], CReportBase.AlignLeft),
            ('%3', [u'УЕТ', u'всего'], CReportBase.AlignLeft),
            ('%3', [u'', u'ст.14 лет'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 5)
        table.mergeCells(1, 1, 2, 1)
        table.mergeCells(1, 2, 1, 2)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(0, 8, 1, 6)
        table.mergeCells(1, 8, 1, 2)
        table.mergeCells(1, 10, 1, 2)
        table.mergeCells(1, 12, 1, 2)
        table.mergeCells(0, 14, 1, 8)
        table.mergeCells(1, 14, 1, 2)
        table.mergeCells(1, 16, 1, 2)
        table.mergeCells(1, 18, 1, 2)
        table.mergeCells(1, 20, 1, 2)
        table.mergeCells(0, 22, 1, 3)
        table.mergeCells(1, 22, 1, 2)
        table.mergeCells(0, 25, 1, 2)
        table.mergeCells(1, 25, 2, 1)
        table.mergeCells(1, 26, 2, 1)
        table.mergeCells(0, 27, 3, 1)
        table.mergeCells(0, 28, 3, 1)
        table.mergeCells(0, 29, 3, 1)
        table.mergeCells(0, 30, 3, 1)
        table.mergeCells(0, 31, 3, 1)
        table.mergeCells(0, 32, 3, 1)
        table.mergeCells(0, 33, 1, 3)
        table.mergeCells(1, 33, 2, 1)
        table.mergeCells(1, 34, 2, 1)
        table.mergeCells(1, 35, 2, 1)
        table.mergeCells(0, 36, 3, 1)
        table.mergeCells(0, 37, 3, 1)
        table.mergeCells(0, 38, 3, 1)
        table.mergeCells(0, 39, 3, 1)
        table.mergeCells(0, 40, 1, 2)
        table.mergeCells(1, 40, 2, 1)
        table.mergeCells(1, 41, 2, 1)

        total = [0] * (len(tableColumns) - 1)

        begDate = params.get('begDate', QtCore.QDate()).toString('yyyy-MM-dd')
        endDate = params.get('endDate', QtCore.QDate()).addDays(1).toString('yyyy-MM-dd')
        orgStructureId = params.get('orgStructureId', None)
        uetData = self.getUetData(begDate, endDate, orgStructureId)

        while query.next():
            record = query.record()
            countAllVisits = forceInt(record.value('countAllVisits'))
            countPrimaryVisitsBefore14 = forceInt(record.value('countPrimaryVisitsBefore14'))
            countPrimaryVisitsAfter14 = forceInt(record.value('countPrimaryVisitsAfter14'))
            countRepeatVisitsBefore14 = forceInt(record.value('countRepeatVisitsBefore14'))
            countRepeatVisitsAfter14 = forceInt(record.value('countRepeatVisitsAfter14'))
            countPrimaryVisitsSchool = forceInt(record.value('countPrimaryVisitsSchool'))
            countPrimaryVisitsPreschool = forceInt(record.value('countPrimaryVisitsPreschool'))
            countIntactSchool = forceInt(record.value('countIntactSchool'))
            countIntactPrechool = forceInt(record.value('countIntactPrechool'))
            countEarlierSanSchool = forceInt(record.value('countEarlierSanSchool'))
            countEarlierSanPrechool = forceInt(record.value('countEarlierSanPrechool'))
            countNeedTreatmentSchool = forceInt(record.value('countNeedTreatmentSchool'))
            countNeedTreatmentPreschool = forceInt(record.value('countNeedTreatmentPreschool'))
            countCalfteethCariesBefore14 = forceInt(record.value('countCalfteethCariesBefore14'))
            countCalfteethPulpitisBefore14 = forceInt(record.value('countCalfteethPulpitisBefore14'))
            countPermanentteethPeriodontitisBefore14 = forceInt(
                record.value('countPermanentteethPeriodontitisBefore14'))
            countPermanentteethPeriodontitisAfter14 = forceInt(record.value('countPermanentteethPeriodontitisAfter14'))
            countCalfteethBefore14 = forceInt(record.value('countCalfteethBefore14'))
            countPermanentteethCariesBefore14 = forceInt(record.value('countPermanentteethCariesBefore14'))
            countPermanentteethCariesAfter14 = forceInt(record.value('countPermanentteethCariesAfter14'))
            countPermanentteethPulpitisBefore14 = forceInt(record.value('countPermanentteethPulpitisBefore14'))
            countPermanentteethPulpitisAfter14 = forceInt(record.value('countPermanentteethPulpitisAfter14'))
            countPermanentteethBefore14 = forceInt(record.value('countPermanentteethBefore14')) + countPermanentteethPulpitisBefore14
            countPermanentteethAfter14 = forceInt(record.value('countPermanentteethAfter14')) + countPermanentteethPulpitisAfter14
            countRemoved = forceInt(record.value('countRemoved'))
            countHygiene = forceInt(record.value('countHygiene'))
            countFtorlak = forceInt(record.value('countFtorlak'))
            countSealant = forceInt(record.value('countSealant'))
            countHygieneLesson = forceInt(record.value('countHygieneLesson'))
            countMucosal = forceInt(record.value('countMucosal'))
            countSanSchool = forceInt(record.value('countSanSchool'))
            countSanPreschool = forceInt(record.value('countSanPreschool'))
            countSanAfter14 = forceInt(record.value('countSanAfter14'))
            countSan = forceInt(record.value('countSan'))
            countCement = forceInt(record.value('countCement'))
            countComposite = forceInt(record.value('countComposite'))
            uet = forceDouble(record.value('uet'))
            uetAfter14 = forceDouble(record.value('uetAfter14'))
            countPermanentTeethPlomb = forceInt(record.value('countPermanentTeethPlomb'))
            countCalfteethTeethPlomb = forceInt(record.value('countCalfTeethPlomb'))

            countAllVisits = countPrimaryVisitsBefore14 + countPrimaryVisitsAfter14 + countRepeatVisitsBefore14 + countRepeatVisitsAfter14
            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, forceString(record.value('person')))
                table.setText(i, 1, countAllVisits)
                table.setText(i, 2, countPrimaryVisitsBefore14)
                table.setText(i, 3, countPrimaryVisitsAfter14)
                table.setText(i, 4, countRepeatVisitsBefore14)
                table.setText(i, 5, countRepeatVisitsAfter14)
                table.setText(i, 6, countPrimaryVisitsSchool)
                table.setText(i, 7, countPrimaryVisitsPreschool)
                table.setText(i, 8, countIntactSchool)
                table.setText(i, 9, countIntactPrechool)
                table.setText(i, 10, countEarlierSanSchool)
                table.setText(i, 11, countEarlierSanPrechool)
                table.setText(i, 12, countNeedTreatmentSchool)
                table.setText(i, 13, countNeedTreatmentPreschool)
                table.setText(i, 14, countPermanentteethCariesBefore14)
                table.setText(i, 15, countPermanentteethCariesAfter14)
                table.setText(i, 16, countPermanentteethPulpitisBefore14)
                table.setText(i, 17, countPermanentteethPulpitisAfter14)
                table.setText(i, 18, countPermanentteethPeriodontitisBefore14)
                table.setText(i, 19, countPermanentteethPeriodontitisAfter14)
                table.setText(i, 20, countPermanentteethBefore14)
                table.setText(i, 21, countPermanentteethAfter14)
                table.setText(i, 22, countCalfteethCariesBefore14)
                table.setText(i, 23, countCalfteethPulpitisBefore14)
                table.setText(i, 24, countCalfteethBefore14)
                table.setText(i, 25, countPermanentTeethPlomb)
                table.setText(i, 26, countCalfteethTeethPlomb)
                table.setText(i, 27, countRemoved)
                table.setText(i, 28, countHygiene)
                table.setText(i, 29, countFtorlak)
                table.setText(i, 30, countSealant)
                table.setText(i, 31, countHygieneLesson)
                table.setText(i, 32, countMucosal)
                table.setText(i, 33, countSanSchool)
                table.setText(i, 34, countSanPreschool)
                table.setText(i, 35, countSanAfter14)
                table.setText(i, 36, countSan)
                table.setText(i, 37, countCement)
                table.setText(i, 38, countComposite)
                table.setText(i, 39, countCement + countComposite)
                table.setText(i, 40, uet)
                table.setText(i, 41, uetAfter14)

            # countAllVisits = countPrimaryVisitsBefore14 + countPrimaryVisitsAfter14 + countRepeatVisitsBefore14 + countRepeatVisitsAfter14
            total[0] += countAllVisits
            total[1] += countPrimaryVisitsBefore14
            total[2] += countPrimaryVisitsAfter14
            total[3] += countRepeatVisitsBefore14
            total[4] += countRepeatVisitsAfter14
            total[5] += countPrimaryVisitsSchool
            total[6] += countPrimaryVisitsPreschool
            total[7] += countIntactSchool
            total[8] += countIntactPrechool
            total[9] += countEarlierSanSchool
            total[10] += countEarlierSanPrechool
            total[11] += countNeedTreatmentSchool
            total[12] += countNeedTreatmentPreschool
            total[13] += countPermanentteethCariesBefore14
            total[14] += countPermanentteethCariesAfter14
            total[15] += countPermanentteethPulpitisBefore14
            total[16] += countPermanentteethPulpitisAfter14
            total[17] += countPermanentteethPeriodontitisBefore14
            total[18] += countPermanentteethPeriodontitisAfter14
            total[19] += countPermanentteethBefore14
            total[20] += countPermanentteethAfter14
            total[21] += countCalfteethCariesBefore14
            total[22] += countCalfteethPulpitisBefore14
            total[23] += countCalfteethBefore14
            total[24] += countPermanentTeethPlomb
            total[25] += countCalfteethTeethPlomb
            total[26] += countRemoved
            total[27] += countHygiene
            total[28] += countFtorlak
            total[29] += countSealant
            total[30] += countHygieneLesson
            total[31] += countMucosal
            total[32] += countSanSchool
            total[33] += countSanPreschool
            total[34] += countSanAfter14
            total[35] += countSan
            total[36] += countCement
            total[37] += countComposite
            total[38] += countCement + countComposite
            total[39] += uet
            total[40] += uetAfter14

        #total[39] = uetData['uet']
        #total[40] = uetData['uetAfter14']

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

    w = CReportChildrenTherapeutic(None)
    w.exec_()
    sys.exit(QtGui.qApp.exec_())


if __name__ == '__main__':
    main()
