# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

import os.path

from library.database  import *
from library.Utils     import *

def getCount(db, startDate, endDate):
    tableEvent = db.table('Event')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableEvent['setDate'].dateLe(endDate))
    cond.append(tableEvent['setDate'].dateGe(startDate))
    stmtCount = u'''
    SELECT
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Самостоятельно%%', Event.id, NULL)) as countByChannelHimself,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%СМП%%', Event.id, NULL)) as countByChannelAmbulance,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Неотложная помощь%%', Event.id, NULL)) as countByChannelAid,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Сан. транспорт%%', Event.id, NULL)) as countByChannelPoliclinics,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Самостоятельно%%' AND actionPropertyStringReceivedCount.value LIKE 'несоответствие диагноза направления', Event.id, NULL)) as countFailureHimselfCancel_diagnosis,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Самостоятельно%%' AND actionPropertyStringReceivedCount.value LIKE 'отказ пациента', Event.id, NULL)) as countFailureHimselfPatient_refusal,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%СМП%%' AND actionPropertyStringReceivedCount.value LIKE 'несоответствие диагноза направления', Event.id, NULL)) as countFailureAmbulanceCancel_diagnosis,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%СМП%%' AND actionPropertyStringReceivedCount.value LIKE 'отказ пациента', Event.id, NULL)) as countFailureAmbulancePatient_refusal,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Неотложная помощь%%' AND actionPropertyStringReceivedCount.value LIKE 'несоответствие диагноза направления', Event.id, NULL)) as countFailureFirstAidCancel_diagnosis,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Неотложная помощь%%' AND actionPropertyStringReceivedCount.value LIKE 'отказ пациента', Event.id, NULL)) as countFailureFirstAidPatient_refusal,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Сан. транспорт%%' AND actionPropertyStringReceivedCount.value LIKE 'несоответствие диагноза направления', Event.id, NULL)) as countFailurePoliclinicsCancel_diagnosis,
        COUNT(DISTINCT IF(actionPropertyString.value LIKE '%%Сан. транспорт%%' AND actionPropertyStringReceivedCount.value LIKE 'отказ пациента', Event.id, NULL)) as countFailurePoliclinicsPatient_refusal,
        COUNT(DISTINCT IF(rbDiagnosisType.code IN ('1', '2') AND Diagnosis.MKB LIKE 'K%%', Event.id, NULL)) as countAbdominals,
        COUNT(DISTINCT IF(Event.externalId NOT LIKE 'о%%', Event.id, NULL)) as countHosp,
        COUNT(DISTINCT IF(Event.externalId LIKE 'о%%', Event.id, NULL)) as countAmb,
        COUNT(DISTINCT IF(rbResult.code IN ('105', '106', '205', '206'), Event.id, NULL)) as countDie

        FROM Event
        INNER JOIN ActionType as actionTypeReceived ON actionTypeReceived.flatCode LIKE 'received' AND actionTypeReceived.deleted = 0
        INNER JOIN Action as actionReceived ON actionReceived.event_id = Event.id AND actionReceived.deleted = 0 AND actionTypeReceived.id = actionReceived.actionType_id

        LEFT JOIN ActionPropertyType as actionPropertyTypeReceived ON actionPropertyTypeReceived.name LIKE 'Кем доставлен' AND actionPropertyTypeReceived.actionType_id = actionTypeReceived.id AND actionPropertyTypeReceived.deleted = 0
        LEFT JOIN ActionProperty as actionPropertyReceived ON actionPropertyReceived.deleted = 0 AND actionPropertyReceived.type_id = actionPropertyTypeReceived.id AND actionPropertyReceived.action_id = actionReceived.id
        LEFT JOIN ActionProperty_String as actionPropertyString ON actionPropertyString.id = actionPropertyReceived.id AND actionPropertyString.value IN ('Самостоятельно', 'СМП', 'Неотложная помощь', 'Сан. транспорт')

        LEFT JOIN ActionPropertyType as actionPropertyTypeReceivedCount ON actionPropertyTypeReceivedCount.name LIKE 'Причина отказа от госпитализации' AND actionPropertyTypeReceivedCount.deleted = 0 AND actionPropertyTypeReceivedCount.actionType_id = actionTypeReceived.id
        LEFT JOIN ActionProperty as actionPropertyReceivedCount ON actionPropertyReceivedCount.deleted = 0 AND actionPropertyReceivedCount.type_id = actionPropertyTypeReceivedCount.id AND actionPropertyReceivedCount.action_id = actionReceived.id
        LEFT JOIN ActionProperty_String as actionPropertyStringReceivedCount ON actionPropertyStringReceivedCount.id = actionPropertyReceivedCount.id AND actionPropertyStringReceivedCount.value IN ('несоответствие диагноза направления', 'отказ пациента')

        LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
        LEFT JOIN Diagnosis ON Diagnosis.deleted = 0 AND Diagnostic.diagnosis_id = Diagnosis.id
        LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id

        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        WHERE %s
        ''' % (db.joinAnd(cond))
    queryCount = db.query(stmtCount)
    if queryCount.first():
        recordCount = queryCount.record()
        countByHimself = forceString(recordCount.value('countByChannelHimself'))
        countByAmbulance = forceString(recordCount.value('countByChannelAmbulance'))
        countByAid = forceString(recordCount.value('countByChannelAid'))
        countByPoliclinics = forceString(recordCount.value('countByChannelPoliclinics'))
        countFailureHimselfCancel_diagnosis = forceString(recordCount.value('countFailureHimselfCancel_diagnosis'))
        countFailureHimselfPatient_refusal = forceString(recordCount.value('countFailureHimselfPatient_refusal'))
        countFailureAmbulanceCancel_diagnosis = forceString(recordCount.value('countFailureAmbulanceCancel_diagnosis'))
        countFailureAmbulancePatient_refusal = forceString(recordCount.value('countFailureAmbulancePatient_refusal'))
        countFailureFirstAidCancel_diagnosis = forceString(recordCount.value('countFailureFirstAidCancel_diagnosis'))
        countFailureFirstAidPatient_refusal = forceString(recordCount.value('countFailureFirstAidPatient_refusal'))
        countFailurePoliclinicsCancel_diagnosis = forceString(recordCount.value('countFailurePoliclinicsCancel_diagnosis'))
        countFailurePoliclinicsPatient_refusal = forceString(recordCount.value('countFailurePoliclinicsPatient_refusal'))
        countAbdominals = forceString(recordCount.value('countAbdominals'))
        countResultHosp = forceString(recordCount.value('countHosp'))
        countResultAmb = forceString(recordCount.value('countAmb'))
        countResultDie = forceString(recordCount.value('countDie'))
    else:
        countByHimself = '0'
        countByAmbulance = '0'
        countByAid = '0'
        countByPoliclinics = '0'
        countFailureHimselfCancel_diagnosis = '0'
        countFailureHimselfPatient_refusal = '0'
        countFailureAmbulanceCancel_diagnosis = '0'
        countFailureAmbulancePatient_refusal = '0'
        countFailureFirstAidCancel_diagnosis = '0'
        countFailureFirstAidPatient_refusal = '0'
        countFailurePoliclinicsCancel_diagnosis = '0'
        countFailurePoliclinicsPatient_refusal = '0'
        countAbdominals = '0'
        countResultHosp = '0'
        countResultAmb = '0'
        countResultDie = '0'
    return [countByHimself,
            countByAmbulance,
            countByAid,
            countByPoliclinics,
            countFailureHimselfCancel_diagnosis,
            countFailureHimselfPatient_refusal,
            countFailureAmbulanceCancel_diagnosis,
            countFailureAmbulancePatient_refusal,
            countFailureFirstAidCancel_diagnosis,
            countFailureFirstAidPatient_refusal,
            countFailurePoliclinicsCancel_diagnosis,
            countFailurePoliclinicsPatient_refusal,
            countAbdominals,
            countResultHosp,
            countResultAmb,
            countResultDie]

def getCountByDistrict(db, startDate, endDate):
    tableLeavedAction = db.table('Action').alias('LeavedAction')
    stmt = u'''
    SELECT rbDistrict.name, COUNT(DISTINCT IF(ChannelAPS.value LIKE '%%Неотложная помощь%%', LeavedAction.id, NULL)) as countFirstAid,
    COUNT(DISTINCT IF(ChannelAPS.value NOT LIKE '%%Неотложная помощь%%' AND Event.referral_id IS NOT NULL, LeavedAction.id, NULL)) as countPoliclinics
    FROM Action LeavedAction
    INNER JOIN ActionType LeavedAT ON LeavedAT.id = LeavedAction.actionType_id AND LeavedAT.flatCode LIKE 'leaved'
    INNER JOIN Action ReceivedAction ON ReceivedAction.event_id = LeavedAction.event_id
    INNER JOIN ActionType ReceivedAT ON ReceivedAT.id = ReceivedAction.actionType_id AND ReceivedAT.flatCode LIKE 'received'
    INNER JOIN ActionPropertyType as ChannelAPT ON ChannelAPT.name LIKE 'Кем доставлен' AND ChannelAPT.actionType_id = ReceivedAT.id
    INNER JOIN ActionProperty as ChannelAP ON ChannelAP.type_id = ChannelAPT.id AND ChannelAP.action_id = ReceivedAction.id
    INNER JOIN ActionProperty_String as ChannelAPS ON ChannelAPS.id = ChannelAP.id
    INNER JOIN Event ON Event.id = LeavedAction.event_id

    LEFT JOIN ActionPropertyType DistrictAPT ON DistrictAPT.actionType_id = ReceivedAT.id AND DistrictAPT.name LIKE 'Район доставки' AND DistrictAPT.deleted = 0
    LEFT JOIN ActionProperty DistrictAP ON DistrictAP.action_id = ReceivedAction.id AND DistrictAP.type_id = DistrictAPT.id AND DistrictAP.deleted = 0
    LEFT JOIN ActionProperty_rbDistrict DistrictAPV ON DistrictAPV.id = DistrictAP.id
    LEFT JOIN rbDistrict ON rbDistrict.id = DistrictAPV.value
    WHERE LeavedAction.deleted = 0 AND LeavedAT.deleted = 0 AND ReceivedAction.deleted = 0 AND ReceivedAT.deleted = 0
    AND ChannelAP.deleted = 0 AND ChannelAPT.deleted = 0
    AND %s
    GROUP BY rbDistrict.name
    '''
    cond = [tableLeavedAction['begDate'].dateGt(startDate),
            tableLeavedAction['begDate'].dateLe(endDate)]

    query = db.query(stmt % db.joinAnd(cond))
    results = {u'Неизвестно': [0, 0]}
    while query.next():
        record = query.record()
        districtName = forceString(record.value('name'))
        countFirstAid = forceInt(record.value('countFirstAid'))
        countPoliclinics = forceInt(record.value('countPoliclinics'))
        if not districtName:
            districtName = u'Неизвестно'
        resultCounts = results.setdefault(districtName, [0, 0])
        resultCounts[0] += countFirstAid
        resultCounts[1] += countPoliclinics
    return results


def getCountHospitalized(db, startDate, endDate):
    # FIXME: В ревизиях после 15150 плановость/экстренность госпитализации берется из Event.order (для б15). До этого
    # брали из свойства действия "Госпитализирован" - ибо так реализовано в Онко. Если понадобится выгружать и в Онко, то надо как-то объединить.

    tableActionType = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableAction = db.table('Action')

    stmtCount = u'''
        SELECT
            COUNT(DISTINCT IF(Event.order  = 2, Event.id, NULL)) as countUrgent,
            COUNT(DISTINCT IF(Event.order != 2, Event.id, NULL)) as countPlanned,
            OrgStructure.bookkeeperCode
        FROM Action
        INNER JOIN ActionType ON ActionType.id = Action.actionType_id
        INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id
        INNER JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.action_id = Action.id
        INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
        INNER JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
        INNER JOIN Event ON Event.id = Action.event_id

        WHERE %s
          AND Action.deleted = 0
          AND ActionProperty.deleted = 0
          AND Event.deleted = 0
          AND OrgStructure.bookkeeperCode != ''
        GROUP BY OrgStructure.id
    '''

    cond = [tableActionType['flatCode'].eq('received'),
            tableActionPropertyType['name'].eq(u'Направлен в отделение'),
            tableAction['endDate'].dateGt(startDate),
            tableAction['endDate'].dateLe(endDate)]

    cond2 = [tableActionType['flatCode'].eq('leaved'),
             tableActionPropertyType['name'].eq(u'Отделение'),
             tableAction['begDate'].dateGt(startDate),
             tableAction['begDate'].dateLe(endDate)]

    results = {}
    queryCountHospitalized = db.query(stmtCount % db.joinAnd(cond))
    while queryCountHospitalized.next():
        record = queryCountHospitalized.record()
        orgStructure = forceString(record.value('bookkeeperCode'))
        if not orgStructure in results:
            results[orgStructure] = [0]*4
        results[orgStructure][0] += forceInt(record.value('countUrgent'))
        results[orgStructure][1] += forceInt(record.value('countPlanned'))

    queryCountLeaved = db.query(stmtCount % db.joinAnd(cond2))
    while queryCountLeaved.next():
        record = queryCountLeaved.record()
        orgStructure = forceString(record.value('bookkeeperCode'))
        if not orgStructure in results:
            results[orgStructure] = [0]*4
        results[orgStructure][2] += forceInt(record.value('countUrgent'))
        results[orgStructure][3] += forceInt(record.value('countPlanned'))

    return results


class CBriefDeliveryRequest(QXmlStreamWriter):

    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)

    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeHospitalBrief(self, record, db, startDate, endDate, numBrief):
        #self.writeStartElement('urn1:hospitalBrief')
        if numBrief == 0:
            self.writeBigBrief(record, db)
        elif numBrief == 1:
            self.writeSmallBriefByProfile(record, db, startDate, endDate)
        elif numBrief == 2:
            self.writeHospitalMortalityBrief(record, db, startDate, endDate)
        elif numBrief == 3:
            self.writeActualSheetEmployment(record, db)
        #self.writeEndElement()

    def writeBigBrief(self, record, db):
        formingDate = QDateTime.currentDateTime()
        orgStructId = forceInt(record.value('orgStructId'))

        tableOSHospitalBed = db.table('OrgStructure_HospitalBed')
        tableAction = db.table('Action')

        thisDayDateTime = QDateTime.currentDateTime()
        lastDayDateTime = thisDayDateTime.addDays(-1)

        condUsedInLastDay = []
        condUsedInLastDay.append(db.joinAnd(['isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\')' % lastDayDateTime.toString('yyyy-MM-ddThh:mm:ss'), tableOSHospitalBed['master_id'].eq(orgStructId)]))
        countBedsUsedInLastDay = db.getCount(tableOSHospitalBed, countCol='OrgStructure_HospitalBed.id', where= condUsedInLastDay)

        cond = [tableAction['begDate'].datetimeGe(lastDayDateTime),
                tableAction['begDate'].datetimeLt(thisDayDateTime)]
        condByEndDate = [tableAction['endDate'].datetimeGe(lastDayDateTime),
                         tableAction['endDate'].datetimeLt(thisDayDateTime)]
        stmtLastDayReceived = u'''
            SELECT
                COUNT(*)
            FROM Action
                INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.flatCode = 'received' AND ActionType.deleted = 0
                INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.deleted = 0 AND ActionPropertyType.name LIKE 'Направлен в отделение%%'
                INNER JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.action_id = Action.id AND ActionProperty.deleted = 0
                INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id AND ActionProperty_OrgStructure.value = %(orgStructureId)s
            WHERE %(cond)s
            ''' % {'orgStructureId': orgStructId, 'cond': db.joinAnd(cond)}
        queryLastDayReceived = db.query(stmtLastDayReceived)
        if queryLastDayReceived.first():
            countLastDayReceived = forceString(queryLastDayReceived.record().value(0))
        else:
            countLastDayReceived = '0'

        stmtLastDayLeaved = u'''
            SELECT
                COUNT(*)
            FROM Action
                INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.flatCode = 'leaved' AND ActionType.deleted = 0
                INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.deleted = 0 AND ActionPropertyType.name LIKE 'Отделение%%'
                INNER JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.action_id = Action.id AND ActionProperty.deleted = 0
                INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id AND ActionProperty_OrgStructure.value = %(orgStructureId)s
            WHERE %(cond)s
            ''' % {'orgStructureId': orgStructId, 'cond': db.joinAnd(cond)}
        queryLastDayLeaved = db.query(stmtLastDayLeaved)
        if queryLastDayLeaved.first():
            countLastDayLeaved = forceString(queryLastDayLeaved.record().value(0))
        else:
            countLastDayLeaved = '0'

        stmtMovedIn = u'''
            SELECT
                COUNT(*)
            FROM Action
                INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.flatCode = 'moving' AND ActionType.deleted = 0
                INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.deleted = 0 AND ActionPropertyType.name LIKE 'Переведен в отделение%%'
                INNER JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.action_id = Action.id AND ActionProperty.deleted = 0
                INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id AND ActionProperty_OrgStructure.value = %(orgStructureId)s
            WHERE %(cond)s
            ''' % {'orgStructureId': orgStructId, 'cond': db.joinAnd(condByEndDate)}
        queryMovedIn = db.query(stmtMovedIn)
        if queryMovedIn.first():
            countMovedIn = forceString(queryMovedIn.record().value(0))
        else:
            countMovedIn = '0'

        stmtMovedOut = u'''
            SELECT
                COUNT(*)
            FROM Action
                INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.flatCode = 'moving' AND ActionType.deleted = 0
                INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.deleted = 0 AND ActionPropertyType.name LIKE 'Переведен из отделения%%'
                INNER JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.action_id = Action.id AND ActionProperty.deleted = 0
                INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id AND ActionProperty_OrgStructure.value = %(orgStructureId)s
            WHERE %(cond)s
            ''' % {'orgStructureId': orgStructId, 'cond': db.joinAnd(cond)}
        queryMovedOut = db.query(stmtMovedOut)
        if queryMovedOut.first():
            countMovedOut = forceString(queryMovedOut.record().value(0))
        else:
            countMovedOut = '0'

        condUsedInThisDay = []
        condUsedInThisDay.append(db.joinAnd(['isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\')' % thisDayDateTime.toString('yyyy-MM-ddThh:mm:ss'), tableOSHospitalBed['master_id'].eq(orgStructId)]))
        countBedsUsedInThisDay = db.getCount(tableOSHospitalBed, countCol='OrgStructure_HospitalBed.id', where= condUsedInThisDay)

        totalBeds = forceInt(record.value('total'))
        underRepairBeds = forceInt(record.value('underRepair'))
        freeMen = forceInt(record.value('freeMen'))
        freeWomen = forceInt(record.value('freeWomen'))
        overloadMen = forceInt(record.value('overloadMen'))
        overloadWomen = forceInt(record.value('overloadWomen'))
        if freeMen and overloadMen:
            if freeMen > overloadMen:
                freeMen = freeMen - overloadMen
                overloadMen = 0
            else:
                overloadMen = overloadMen - freeMen
                freeMen = 0
        if freeWomen and overloadWomen:
            if freeWomen > overloadWomen:
                freeWomen = freeWomen - overloadWomen
                overloadWomen = 0
            else:
                overloadWomen = overloadWomen - freeWomen
                freeWomen = 0

        self.writeStartElement('urn1:bigBrief')
        self.writeTextElement('urn1:departmentName', forceString(record.value('bookkeeperCode')))   #+
        self.writeTextElement('urn1:formingDate', formingDate.toString('yyyy-MM-ddThh:mm:ss.zzz'))  #+
        self.writeTextElement('urn1:totalBerth', forceString(totalBeds))                            #+ 1  - Штат. – штатное количество койкомест по отделению стационара.
        self.writeTextElement('urn1:lastDayMorning', forceString(countBedsUsedInLastDay))           #+ 6  - Предыдущий день (утро) – количество занятых койкомест на утро предыдущего дня.
        self.writeTextElement('urn1:lastDayReceived', forceString(countLastDayReceived))            #+ 7  - Предыдущий день (пост.) – количество больных, определённых на койкоместа по отделению, в течение предыдущего дня.
        self.writeTextElement('urn1:lastDayReleased', forceString(countLastDayLeaved))              #+ 8  - Предыдущий день (вып.) – количество больных, выписанных из стационара, где ранее занимали койкоместо отделения.
        self.writeTextElement('urn1:transferTo', forceString(countMovedIn))                         #+ 9  – количество больных переведенных внутри стационара на данное отделение из какого-либо другого отделения.
        self.writeTextElement('urn1:transferFrom', forceString(countMovedOut))                      #+ 10 - количество больных переведенных внутри стационара с данного отделения на какое-либо другое отделение.
        self.writeTextElement('urn1:thisDayMorning', forceString(countBedsUsedInThisDay))           #+ 11 - Текущий (утро) – количество больных занимающих койкоместа в отделении на утро текущего дня – является результатом сложения количества занятых койкомест на утро предыдущего дня, поступивших больных, переводов на отделение и вычитания выписанных больных за предыдущий день, переводов из отделения ( = «6» + «7» + «9» - «8» - «10» ).
        self.writeTextElement('urn1:thisDayRelease', '0')                                           #- 12 - количество больных, которые планируются выписываться из стационара в текущий день.
        self.writeTextElement('urn1:freeMen', str(freeMen))                                              #+ 13 - Свободно (муж.) – количество свободных мужских койкомест (если отделение является общим, все места считаются в столбец мужских мест) – является результатом разницы количества больных на утро текущего дня и больных запланированных на выписку, если разница является положительным числом ( = «11» - «12» ).
        self.writeTextElement('urn1:freeWomen', str(freeWomen))                                          #+ 14 - Свободно (жен.) – количество свободных женских койкомест (если отделение является общим или мужским, все места считаются в столбец мужских мест) – является результатом разницы количества больных на утро текущего дня и больных запланированных на выписку, если разница является положительным числом ( = «11» - «12» ).
        self.writeTextElement('urn1:overloadMen', str(overloadMen))                                      #+ 15 - Перегруз (муж.) – количество больных превышающих количество функционирующих койкомест (если отделение является общим, все места считаются в столбец мужских мест) – является результатом разницы количества больных на утро текущего дня и больных запланированных на выписку, если разница является отрицательным числом ( = «11» - «12» ).
        self.writeTextElement('urn1:overloadWomen', str(overloadWomen))                                  #+ 16 - Свободно (муж.) – количество больных превышающих количество функционирующих койкомест (если отделение является общим или мужским, все места считаются в столбец мужских мест) – является результатом разницы количества больных на утро текущего дня и больных запланированных на выписку, если разница является отрицательным числом ( = «11» - «12» ).
        self.writeTextElement('urn1:dutyFreeMen', '0')                                              #+
        self.writeTextElement('urn1:dutyFreeWomen', '0')                                            #+
        self.writeTextElement('urn1:dutyOverloadMen', '0')                                          #+
        self.writeTextElement('urn1:dutyOverloadWomen', '0')                                        #+
        self.writeTextElement('urn1:underRepair', forceString(underRepairBeds))                     #+ 2  - Рем. – количество койкомест, не функционирующих по причине ремонта.
        self.writeTextElement('urn1:onVentilation', '0')                                            #+ 3  - Пров. – количество койкомест, не функционирующих по причине проветривания.
        self.writeTextElement('urn1:notMaximized', forceString(underRepairBeds))        #+ 4  - Не разв. – количество не развернутых койкомест.
        self.writeTextElement('urn1:quarantineBeginDate', '0')                                      #+
        self.writeTextElement('urn1:quarantineEndDate', '0')                                        #+
        self.writeTextElement('urn1:quarantineComment', '0')                                        #+
        self.writeEndElement()

    def writeHospitalSmallBrief(self, record, db, startDate, endDate):
        formingDate = QDateTime.currentDateTime()
        orgName = forceString(record.value('name'))
        self.writeStartElement('urn1:hospitalSmallBrief')
        self.writeTextElement('urn1:hospitalName', '15') #orgName
        self.writeTextElement('urn1:formingDate', formingDate.toString('yyyy-MM-ddThh:mm:ss.zzz'))
        self.writeSmallBrief(record, db, startDate, endDate)
        self.writeEndElement()

    def writeSmallBrief(self, db, startDate, endDate):
        self.writeStartElement('urn1:smallBrief')                       # 1

        count = getCount(db, startDate, endDate)

        self.writeTextElement('urn1:smallBriefHomeless', '0')
        self.writeStartElement('urn1:smallBriefByChannelDelivery')      # 2
        self.writeTextElement('urn1:channelDeliveryName', u'СМП')
        self.writeTextElement('urn1:patientsCount', count[0])
        self.writeEndElement()                                          # urn1:smallBriefByChannelDelivery 1
        self.writeStartElement('urn1:smallBriefByChannelDelivery')      # 2
        self.writeTextElement('urn1:channelDeliveryName', u'Сан. транспорт')
        self.writeTextElement('urn1:patientsCount', count[1])
        self.writeEndElement()                                          # urn1:smallBriefByChannelDelivery 1
        self.writeStartElement('urn1:smallBriefByChannelDelivery')      # 2
        self.writeTextElement('urn1:channelDeliveryName', u'Неотложная помощь')
        self.writeTextElement('urn1:patientsCount', count[2])
        self.writeEndElement()                                          # urn1:smallBriefByChannelDelivery 1
        self.writeStartElement('urn1:smallBriefByChannelDelivery')      # 2
        self.writeTextElement('urn1:channelDeliveryName', u'Самостоятельно')
        self.writeTextElement('urn1:patientsCount', count[3])
        self.writeEndElement()                                          # urn1:smallBriefByChannelDelivery 1

        self.writeSmallBriefByProfile(db, startDate, endDate)

        strList = [u'Самостоятельно', u'СМП', u'Неотложная помощь', u'Сан. транспорт']
        i = 4
        for str in strList:
            self.writeStartElement('urn1:smallBriefByReleasedCaused')   # 2
            self.writeTextElement('urn1:channelDeliveryName', str)
            self.writeTextElement('urn1:ambulance_service', '0')
            self.writeTextElement('urn1:cancel_diagnosis', count[i])
            i += 1
            self.writeTextElement('urn1:no_places', '0')
            self.writeTextElement('urn1:not_profile', '0')
            self.writeTextElement('urn1:patient_refusal', count[i])
            i += 1
            self.writeEndElement()                                      # urn1:smallBriefByReleasedCaused 1

        self.writeSmallBriefByDistrict(db, startDate, endDate)

        self.writeStartElement('urn1:smallBriefAbdominals')             # 2
        self.writeTextElement('urn1:abdomens', count[12])
        self.writeEndElement()                                          # urn1:smallBriefAbdominals 1

        self.writeStartElement('urn1:smallBriefTramp')                  # 2
        self.writeTextElement('urn1:hospitalizied', count[13])
        self.writeTextElement('urn1:outpatient', count[14])
        self.writeTextElement('urn1:died', count[15])
        self.writeEndElement()                                          # urn1:smallBriefTramp 1

        self.writeEndElement()                                          # urn1:smallBrief 0


    def writeSmallBriefByDistrict(self, db, startDate, endDate):
        results = getCountByDistrict(db, startDate, endDate)
        for districtName, values in results.items():
            self.writeStartElement('urn1:smallBriefByDistrict')             # 2
            self.writeTextElement('urn1:districtName', districtName)
            self.writeTextElement('urn1:firstAid', str(values[0]))
            self.writeTextElement('urn1:policlinic', str(values[1]))
            self.writeEndElement()                                          # urn1:smallBriefByDistrict 1


    def writeSmallBriefByProfile(self, db, startDate, endDate):
        results = getCountHospitalized(db, startDate, endDate)

        for orgStructure, values in results.items():
            self.writeStartElement('urn1:smallBriefByProfile')
            self.writeTextElement('urn1:depName', orgStructure)
            self.writeTextElement('urn1:hospitaliziedUrgently', str(values[0]))
            self.writeTextElement('urn1:hospitaliziedPlanning', str(values[1]))
            self.writeTextElement('urn1:releasedUrgently', str(values[2]))
            self.writeTextElement('urn1:releasedPlanning', str(values[3]))
            self.writeEndElement()

    def writeHospitalMortalityBrief(self, recordClient, db, startDate, endDate):

        name = forceString(recordClient.value('bookkeeperCode'))

        curDate = QDate.currentDate()
        curDate = curDate.year()
        birthDate = forceDate(recordClient.value('birthDate'))
        birthDate = birthDate.year()
        sex = forceInt(recordClient.value('sex'))
        if sex == 0 or sex == 1:
            sexName = u'male'
        elif sex == 2:
            sexName = u'female'
        else:
            sexName = ''
        stationarEntranceTime = forceDateTime(recordClient.value('setDate'))
        deathTime = forceDateTime(recordClient.value('execDate'))
        whoPass = forceString(recordClient.value('setPersonLastName')) + ' ' + forceString(recordClient.value('setPersonFirstName')) + ' ' + forceString(recordClient.value('setPersonPatrName')) + ' ' + forceString(recordClient.value('fullName'))
        personMortal = forceString(recordClient.value('personMortalLastName')) + ' ' + forceString(recordClient.value('personMortalFirstName')) + ' ' + forceString(recordClient.value('personMortalPatrName'))
        channelDeliveryMap = {u'Неотложная помощь': 'firstAid',
                              u'СМП': 'ambulance',
                              u'Самостоятельно': 'himself',
                              u'Сан. транспорт': 'policlinics'}
        self.writeStartElement('urn1:mortalityBrief')           # 1
        self.writeTextElement('urn1:departmentName ', name)
        self.writeStartElement('urn1:patient')                  # 2
        self.writeTextElement('urn1:lastName', forceString(recordClient.value('clientLastName')))
        self.writeTextElement('urn1:firstName', forceString(recordClient.value('clientFirstName')))
        self.writeTextElement('urn1:middleName', forceString(recordClient.value('clientPatrName')))
        self.writeTextElement('urn1:ageYear', forceString(curDate - birthDate))
        self.writeTextElement('urn1:ageMonth', '')
        self.writeTextElement('urn1:ageDays', '')
        self.writeTextElement('urn1:sex', sexName)
        self.writeEndElement()          # urn1:patient 1

        channelDeliveryName = forceString(recordClient.value('channelDelivery'))
        channelDelivery = channelDeliveryMap.get(re.sub(ur'^\d+:\s+', '', channelDeliveryName), None)
        self.writeTextElement('urn1:channelDelivery', channelDelivery)
        self.writeTextElement('urn1:stationarEntranceTime', stationarEntranceTime.toString('yyyy-MM-ddThh:mm:ss'))
        self.writeTextElement('urn1:deathDateTime', deathTime.toString('yyyy-MM-ddThh:mm:ss'))
        self.writeTextElement('urn1:patientDiagnosis', forceString(recordClient.value('DiagnosisName')))
        self.writeTextElement('urn1:patientClinicalDiagnosis', forceString(recordClient.value('DiagnosisName')))
        self.writeTextElement('urn1:whoPass', whoPass)
        self.writeTextElement('urn1:procedures', '0')
        self.writeTextElement('urn1:doctor', personMortal)
        substationNumber = forceString(recordClient.value('substationNumber'))
        if substationNumber.startswith(u'№'):
            substationNumber = substationNumber[1:]
        substationNumber = forceString(forceInt(substationNumber))
        self.writeTextElement('urn1:deliveryDepNum', substationNumber)
        self.writeTextElement('urn1:orderNum', forceString(recordClient.value('orderNumber')) if channelDelivery == 'firstAid' else '')
        self.writeTextElement('urn1:motherLastName ', '')
        self.writeTextElement('urn1:motherFirstName ', '')
        self.writeTextElement('urn1:motherSecondName', '')
        self.writeTextElement('urn1:motherAge', '')
        self.writeTextElement('urn1:womenConsultation', '')
        self.writeTextElement('urn1:weight', '')
        self.writeTextElement('urn1:height ', '')
        self.writeStartElement('urn1:briefDeliveryResponse')    # 2
        self.writeStartElement('urn1:ExecResult')               # 3
        self.writeTextElement('urn1:code', '')
        self.writeTextElement('urn1:errorDescription', '')
        self.writeTextElement('urn1:errorDetail', '')
        self.writeEndElement()                                  # urn1:ExecResult 2
        self.writeStartElement('urn1:bigBriefErrors')           # 3
        self.writeStartElement('urn1:department')               # 4
        self.writeTextElement('urn1:name', '')
        self.writeTextElement('urn1:error', '')
        self.writeEndElement()                                  # urn1:department 3
        self.writeEndElement()                                  # urn1:bigBriefsErrors 2
        self.writeEndElement()                                  # urn1:briefDeliveryResponse 1
        self.writeEndElement()                                  # urn1:mortalityBrief 0

    def writeActualSheetEmployment(self, record, db):
        self.writeStartElement('urn1:profileSheetEmployment')
        self.writeTextElement('urn1:profile', forceString(record.value('bookkeeperCode')))
        self.writeTextElement('urn1:formingTime', QDateTime.currentDateTime().toString('yyyy-MM-ddThh:mm:ss.zzz'))
        self.writeTextElement('urn1:freeWomen', forceString(record.value('freeWomen')))
        self.writeTextElement('urn1:freeMen', forceString(record.value('freeMen')))
        self.writeTextElement('urn1:overloadWomen', forceString(record.value('overloadWomen')))
        self.writeTextElement('urn1:overloadMen', forceString(record.value('overloadMen')))
        self.writeEndElement()

    def writeFileHeader(self, device, numberBrief):
        self._clientsSet = set()
        self.setDevice(device)
        formingDate = QDateTime.currentDateTime()
        if numberBrief == 0:
            self.writeStartElement('urn1:hospitalBigBrief')
        elif numberBrief == 1:
            self.writeStartElement('urn1:hospitalSmallBrief')
        elif numberBrief == 2:
            self.writeStartElement('urn1:hospitalMortalityBrief')
        self.writeTextElement('urn1:hospitalName', '15')
        self.writeTextElement('urn1:formingDate', formingDate.toString('yyyy-MM-ddThh:mm:ss.zzz'))

    def writeFileFooter(self, numberBrief):
        if numberBrief in (0, 1, 2):
            self.writeEndElement()
            #self.writeEndElement()

def getMortalityBriefStmt(dt, curDt):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableLeaved = db.table('Action').alias('actionLeaved')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableLeaved['createDatetime'].datetimeGe(dt))
    cond.append(tableLeaved['createDatetime'].datetimeLe(curDt))
    # cond.append(tableEvent['execDate'].datetimeGe(dt))
    # cond.append(tableEvent['execDate'].datetimeLe(curDt))
    stmtHospitalMortality = u'''
      SELECT Client.id as clientId, Event.id as eventId,
        Client.lastName as clientLastName,
        Client.firstName as clientFirstName,
        Client.patrName as clientPatrName,
        Client.birthDate,
        Client.sex,
        ActionProperty_String.value as channelDelivery,
        actionPropertyOrderString.value as orderNumber,
        actionPropertySubstationString.value as substationNumber,
        Event.setDate,
        Event.execDate,
        os.name,
        CONCAT_WS(' ', Diagnosis.MKB, MKB_Tree.DiagName) as DiagnosisName,
        setPerson.lastName as setPersonLastName,
        setPerson.firstName as setPersonFirstName,
        setPerson.patrName as setPersonPatrName,
        personSetOrganisation.fullName,

        personMortal.lastName as personMortalLastName,
        personMortal.firstName as personMortalFirstName,
        personMortal.patrName as personMortalPatrName,
        os.bookkeeperCode
      FROM Event
      INNER JOIN rbResult ON rbResult.code IN ('105', '106', '205', '206') AND rbResult.id = Event.result_id
      INNER JOIN Action as actionMoving ON actionMoving.event_id = Event.id AND actionMoving.deleted = 0
      INNER JOIN ActionType as actionTypeMoving ON actionTypeMoving.id = actionMoving.actionType_id AND actionTypeMoving.flatCode LIKE 'moving' AND actionTypeMoving.deleted = 0
      INNER JOIN ActionPropertyType as actionPropertyTypeMoving ON actionPropertyTypeMoving.actionType_id = actionTypeMoving.id AND actionPropertyTypeMoving.name LIKE 'Отделение пребывания' AND actionPropertyTypeMoving.deleted = 0
      INNER JOIN ActionProperty as actionPropertyMoving ON actionPropertyMoving.type_id = actionPropertyTypeMoving.id AND actionPropertyMoving.deleted = 0 AND actionPropertyMoving.action_id = actionMoving.id
      INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = actionPropertyMoving.id #AND ActionProperty_OrgStructure.value = 14
      INNER JOIN OrgStructure os ON os.id = ActionProperty_OrgStructure.value
      INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
      INNER JOIN Action as actionReceived ON actionReceived.event_id = Event.id AND actionReceived.deleted = 0
      INNER JOIN ActionType as actionTypeReceived ON actionTypeReceived.id = actionReceived.actionType_id AND actionTypeReceived.flatCode LIKE 'received' AND actionTypeReceived.deleted = 0
      INNER JOIN ActionPropertyType as actionPropertyTypeReceived ON actionPropertyTypeReceived.actionType_id = actionTypeReceived.id AND actionPropertyTypeReceived.name LIKE 'Кем доставлен' AND actionPropertyTypeReceived.deleted = 0
      INNER JOIN ActionProperty as actionPropertyReceived ON actionPropertyReceived.type_id = actionPropertyTypeReceived.id AND actionPropertyReceived.action_id = actionReceived.id AND actionPropertyReceived.deleted = 0
      INNER JOIN ActionProperty_String ON ActionProperty_String.id = actionPropertyReceived.id
      INNER JOIN Action as actionLeaved ON actionLeaved.event_id = Event.id AND actionLeaved.deleted = 0
      INNER JOIN ActionType as actionTypeLeaved ON actionTypeLeaved.id = actionLeaved.actionType_id AND actionTypeLeaved.flatCode LIKE 'leaved' AND actionTypeLeaved.deleted = 0
      LEFT JOIN ActionPropertyType as actionPropertyTypeOrder ON actionPropertyTypeOrder.actionType_id = actionTypeReceived.id AND actionPropertyTypeOrder.name = '№ Наряда' AND actionPropertyTypeOrder.deleted = 0
      LEFT JOIN ActionProperty as actionPropertyOrder ON actionPropertyOrder.type_id = actionPropertyTypeOrder.id AND actionPropertyOrder.action_id = actionReceived.id AND actionPropertyOrder.deleted = 0
      LEFT JOIN ActionProperty_String as actionPropertyOrderString ON actionPropertyOrderString.id = actionPropertyOrder.id
      LEFT JOIN ActionPropertyType as actionPropertyTypeSubstation ON actionPropertyTypeSubstation.actionType_id = actionTypeReceived.id AND actionPropertyTypeSubstation.name = 'Подстанция СМП' AND actionPropertyTypeSubstation.deleted = 9
      LEFT JOIN ActionProperty as actionPropertySubstation ON actionPropertySubstation.type_id = actionPropertyTypeSubstation.id AND actionPropertySubstation.action_id = actionReceived.id AND actionPropertySubstation.deleted = 0
      LEFT JOIN ActionProperty_String as actionPropertySubstationString ON actionPropertySubstationString.id = actionPropertySubstation.id
      INNER JOIN Person as setPerson ON Event.setPerson_id = setPerson.id AND setPerson.deleted = 0
      INNER JOIN Organisation as personSetOrganisation ON personSetOrganisation.id = Event.org_id AND personSetOrganisation.deleted = 0
      INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
      INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
      INNER JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB
      INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code = 1
      INNER JOIN Person as personMortal ON Diagnosis.person_id = personMortal.id AND personMortal.deleted = 0
      WHERE os.bookkeeperCode != '' AND %s
    ''' % (db.joinAnd(cond))
    return stmtHospitalMortality


def getHospitalBedsStmt():
    stmt = u'''SELECT
          os.bookkeeperCode, os.id as orgStructId, os.name as orgStructName,
          COUNT(IF(hb.isPermanent = 1, 1, NULL)) AS total,
          COUNT(hbi.id) AS underRepair,
          COUNT(IF(hb.isBusy = 0 AND hb.sex = 2 AND hb.isPermanent = 1, 1, NULL)) AS freeWomen,
          COUNT(IF(hb.isBusy = 0 AND hb.sex != 2 AND hb.isPermanent = 1, 1, NULL)) AS freeMen,
          COUNT(IF(hb.isBusy = 1 AND hb.sex = 2 AND hb.isPermanent = 0, 1, NULL)) AS overloadWomen,
          COUNT(IF(hb.isBusy = 1 AND hb.sex != 2 AND hb.isPermanent = 0, 1, NULL)) AS overloadMen
        FROM vHospitalBed hb
          INNER JOIN OrgStructure os
            ON os.id = hb.master_id
          LEFT JOIN HospitalBed_Involute hbi
            ON hbi.master_id = hb.id AND hbi.involuteType > 0
            AND hbi.begDateInvolute < NOW()
            AND (hbi.endDateInvolute > NOW() OR hbi.endDateInvolute IS NULL)
        WHERE os.bookkeeperCode != ''
        GROUP BY os.id
    '''
    return stmt

# *****************************************************************************************

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Export stationary briefs for ASOV03 from specified database.')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-t', dest='datetime', default=None)
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-D', dest='dir', default=os.getcwd())
    parser.add_argument('-b', dest='numberBrief', default=0)
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)

    app = QtCore.QCoreApplication(sys.argv)
    connectionInfo = {
                          'driverName' : 'MYSQL',
                          'host' : args['host'],
                          'port' : args['port'],
                          'database' : args['database'],
                          'user' : args['user'],
                          'password' : args['password'],
                          'connectionName' : 'ASOV',
                          'compressData' : True,
                          'afterConnectFunc' : None
                    }

    db = connectDataBaseByInfo(connectionInfo)
    QtGui.qApp.db = db
    numberBrief = forceInt(args['numberBrief'])
    if numberBrief == 0:
        name = u'BBDR_%s.xml'
    elif numberBrief == 1:
        name = u'SBDR_%s.xml'
    elif numberBrief == 2:
        name = u'HMBDR_%s.xml'
    elif numberBrief == 3:
        name = u'ASE_%s.xml'

    fileName = name % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
    dt = args['datetime']
    if dt:
        dt = QDateTime.fromString(dt, 'yyyy-MM-ddTHH:mm:ss')
    else:
        dt = QDateTime.currentDateTime()
        dt = dt.addDays(-1)
    curDt = QtCore.QDateTime.currentDateTime()
    if not (dt is None or dt.isValid()):
        print 'Error: incorrect base datetime.'
        sys.exit(-3)
    if numberBrief == 1:
        outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        clientsOut = CBriefDeliveryRequest(None)
        clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        clientsOut.writeFileHeader(outFile, numberBrief)
        clientsOut.writeSmallBrief(db, dt, curDt)
        clientsOut.writeFileFooter(numberBrief)
        outFile.close()
    else:
        if numberBrief == 2:
            stmtHospitalMortality = getMortalityBriefStmt(dt, curDt)
            query = db.query(stmtHospitalMortality)
        else:
            stmt = getHospitalBedsStmt()
            query = db.query(stmt)

        if query.size() > 0:
            outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
            outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
            clientsOut = CBriefDeliveryRequest(None)
            clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            clientsOut.writeFileHeader(outFile, numberBrief)
            while query.next():
                clientsOut.writeHospitalBrief(query.record(), db, dt, curDt, numberBrief)
            clientsOut.writeFileFooter(numberBrief)
            outFile.close()
#
# class MyModel(QAbstractTableModel):
#     def __init__(self):
#         QAbstractTableModel.__init__(self, None)
#         self.items = ['asd', 'zxc']
#         self.itemsCheckeds = [True, False]
#
#     def flags(self, QModelIndex):
#         return QAbstractTableModel.flags(self, QModelIndex) | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
#
#     def rowCount(self, parent):
#         return len(self.items)
#
#     def columnCount(self, parent):
#         return 1
#
#     def headerData(self, section, orientation, role = None):
#         if orientation == Qt.Horizontal:
#             return QVariant('111')
#         else:
#             return QVariant('222')
#
#     def data(self, index, role=None):
#         row = index.row()
#         col = index.column()
#         if role == Qt.DisplayRole and col == 0 and row < len(self.items):
#             return QVariant(self.items[row])
#         elif role == Qt.CheckStateRole:
#             return Qt.Checked if self.itemsCheckeds[row] else Qt.Unchecked
#
#     def setData(self, index, value, role ):
#         if role == Qt.CheckStateRole:
#             row = index.row()
#             col = index.column()
#             if row < len(self.items):
#                 self.itemsCheckeds[row] = forceBool(value)
#         return True
#
#
# def main():
#     import sys
#     qApp = QtGui.QApplication(sys.argv)
#     dlg = QtGui.QDialog()
#     tbl = QtGui.QTableView()
#     tbl.setModel(MyModel())
#     lyt = QtGui.QGridLayout()
#     dlg.setLayout(lyt)
#     dlg.layout().addWidget(tbl)
#     dlg.exec_()

if __name__ == '__main__':
    main()