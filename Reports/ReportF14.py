# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceBool, forceInt, forceRef, forceString, getVal, getActionTypeIdListByFlatCode
from Orgs.Utils             import getOrganisationInfo
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from Reports.ReportF30PRR   import CReportF30PRRSetupDialog
from Reports.StatReportDDFoundIllnesses import MKBinString
from Reports.StationaryF007 import getTransferProperty


def selectData(params, deathEventTypePurposeId):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableRBTraumaType = db.table('rbTraumaType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableActionPropertyString = db.table('ActionProperty_String')
    tableActionPropertyOrganisation = db.table('ActionProperty_Organisation')

    tableLastMovingAction = tableAction.alias('LastMovingAction')
    tableLastMovingAPT = db.table('ActionPropertyType').alias('LastMovingAPT')
    tableLastMovingAP = db.table('ActionProperty').alias('LastMovingAP')
    tableLastMovingAPHB = db.table('ActionProperty_HospitalBed').alias('LastMovingAPHB')
    tableLastMovingOSHB = db.table('OrgStructure_HospitalBed').alias('LastMovingOSHB')
    tableLastMovingOS = db.table('OrgStructure')

    tableArrivalAction = tableAction.alias('ArrivalAction')
    tableArrivalReasonAPT = tableActionPropertyType.alias('ArrivalReasonAPT')
    tableArrivalReasonAP = tableActionProperty.alias('ArrivalReasonAP')
    tableArrivalReasonAPS = tableActionPropertyString.alias('ArrivalReasonAPS')
    tableArrivalAPT = tableActionPropertyType.alias('ArrivalAPT')
    tableArrivalAP = tableActionProperty.alias('ArrivalAP')
    tableArrivalAPS = tableActionPropertyString.alias('ArrivalAPS')

    tableRefuseReasonAPT = tableActionPropertyType.alias('RefuseReasonAPT')
    tableRefuseReasonAP = tableActionProperty.alias('RefuseReasonAP')
    tableRefuseReasonAPS = tableActionPropertyString.alias('RefuseReasonAPS')

    tableRefuseActionsAPT = tableActionPropertyType.alias('RefuseActionsAPT')
    tableRefuseActionsAP = tableActionProperty.alias('RefuseActionsAP')
    tableRefuseActionsAPS = tableActionPropertyString.alias('RefuseActionsAPS')

    tableOrganisationAPT = tableActionPropertyType.alias('OrganisationAPT')
    tableOrganisationAP = tableActionProperty.alias('OrganisationAP')
    tableOrganisationAPO = tableActionPropertyOrganisation.alias('OrganisationAPO')

    tableResultAPT = tableActionPropertyType.alias('ResultAPT')
    tableResultAP = tableActionProperty.alias('ResultAP')
    tableResultAPS = tableActionPropertyString.alias('ResultAPS')

    deathEventTypeIdList = db.getDistinctIdList('EventType', 'id',
                                                db.joinAnd([tableEventType['purpose_id'].eq(deathEventTypePurposeId), tableEventType['deleted'].eq(0)]))
    tableDeathEvent = tableEvent.alias('DeathEvent')
    tableDeathAction = tableAction.alias('DeathAction')
    tableDeathAPT = tableActionPropertyType.alias('DeathAPT')
    tableDeathAP = tableActionProperty.alias('DeathAP')
    tableDeathAPS = tableActionPropertyString.alias('DeathAPS')

    cond = [ tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('leaved%')),
             tableAction['deleted'].eq(0),
             tableEvent['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableDiagnostic['deleted'].eq(0),
             tableDiagnosis['deleted'].eq(0),
             tableAction['endDate'].isNotNull(),
           ]

    # Основные данные о пациенте, обращении и действии "Выписка"
    queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableDiagnostic, tableDiagnostic['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableDiagnosis, [tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']),
                                                       tableDiagnosis['MKB'].ne('')])

    # Тип полученной травмы
    queryTable = queryTable.leftJoin(tableRBTraumaType, tableRBTraumaType['id'].eq(tableDiagnostic['traumaType_id']))

    # Данные о действии "Движение" - для фильтров?
    queryTable = queryTable.innerJoin(tableLastMovingAction, [tableLastMovingAction['event_id'].eq(tableEvent['id']),
                                                              tableLastMovingAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%')),
                                                              tableLastMovingAction['deleted'].eq(0),
                                                              'NOT %s' % getTransferProperty(u'Переведен в отделение%', tableLastMovingAction.aliasName),
                                                              tableLastMovingAction['status'].eq(2),
                                                              tableLastMovingAction['endDate'].isNotNull()])
    queryTable = queryTable.innerJoin(tableLastMovingAPT, [tableLastMovingAPT['typeName'].eq('HospitalBed'),
                                                           tableLastMovingAPT['actionType_id'].eq(tableLastMovingAction['actionType_id']),
                                                           tableLastMovingAPT['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableLastMovingAP, [tableLastMovingAP['type_id'].eq(tableLastMovingAPT['id']),
                                                          tableLastMovingAP['deleted'].eq(0),
                                                          tableLastMovingAP['action_id'].eq(tableLastMovingAction['id'])])
    queryTable = queryTable.innerJoin(tableLastMovingAPHB, [tableLastMovingAPHB['id'].eq(tableLastMovingAP['id'])])
    queryTable = queryTable.innerJoin(tableLastMovingOSHB, [tableLastMovingOSHB['id'].eq(tableLastMovingAPHB['value'])])
    queryTable = queryTable.innerJoin(tableLastMovingOS, [tableLastMovingOS['id'].eq(tableLastMovingOSHB['master_id']),
                                                          tableLastMovingOS['deleted'].eq(0)])


    # Исход госпитализации - выписан или умер?
    queryTable = queryTable.leftJoin(tableResultAPT, [tableResultAPT['name'].eq(u'Исход госпитализации'),
                                                      tableResultAPT['actionType_id'].eq(tableAction['actionType_id']),
                                                      tableResultAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableResultAP, [tableResultAP['type_id'].eq(tableResultAPT['id']),
                                                     tableResultAP['action_id'].eq(tableAction['id']),
                                                     tableResultAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableResultAPS, [tableResultAPS['id'].eq(tableResultAP['id'])])

    # Проверка расхождения диагнозов, если умер
    queryTable = queryTable.leftJoin(tableDeathEvent, [tableResultAPS['value'].like(u'умер%'),                  # Если пациент жив, то данные не нужны
                                                       tableDeathEvent['client_id'].eq(tableClient['id']),
                                                       tableDeathEvent['deleted'].eq(0),
                                                       tableDeathEvent['eventType_id'].inlist(deathEventTypeIdList)])
    # И проверка, проводилось ли патологоанатомическое вскрытие
    queryTable = queryTable.leftJoin(tableDeathAction, [tableDeathAction['event_id'].eq(tableDeathEvent['id']),
                                                        tableDeathAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('deathCircumstance')),
                                                        tableDeathAction['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableDeathAPT, [tableDeathAPT['name'].eq(u'Причина установлена'),
                                                     tableDeathAPT['actionType_id'].eq(tableDeathAction['actionType_id']),
                                                     tableDeathAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableDeathAP, [tableDeathAP['type_id'].eq(tableDeathAPT['id']),
                                                    tableDeathAP['action_id'].eq(tableDeathAction['id']),
                                                    tableDeathAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableDeathAPS, tableDeathAPS['id'].eq(tableDeathAP['id']))


    # Действие "Поступление", данные для столбцов "из них доставленных СМП" и "доставленных по экстренным показаниям"
    queryTable = queryTable.leftJoin(tableArrivalAction, [tableArrivalAction['event_id'].eq(tableEvent['id']),
                                                          tableArrivalAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
                                                          tableArrivalAction['deleted'].eq(0),
                                                          ])
    queryTable = queryTable.leftJoin(tableArrivalReasonAPT, [tableArrivalReasonAPT['name'].eq(u'Госпитализирован'),
                                                             tableArrivalReasonAPT['actionType_id'].eq(tableArrivalAction['actionType_id']),
                                                             tableArrivalReasonAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableArrivalReasonAP, [tableArrivalReasonAP['type_id'].eq(tableArrivalReasonAPT['id']),
                                                            tableArrivalReasonAP['deleted'].eq(0),
                                                            tableArrivalReasonAP['action_id'].eq(tableArrivalAction['id'])])
    queryTable = queryTable.leftJoin(tableArrivalReasonAPS, tableArrivalReasonAPS['id'].eq(tableArrivalReasonAP['id']))

    queryTable = queryTable.leftJoin(tableArrivalAPT, [tableArrivalAPT['name'].eq(u'Кем доставлен'),
                                                       tableArrivalAPT['actionType_id'].eq(tableArrivalAction['actionType_id']),
                                                       tableArrivalAPT['deleted'].eq(0)
                                                       ])
    queryTable = queryTable.leftJoin(tableArrivalAP, [tableArrivalAP['type_id'].eq(tableArrivalAPT['id']),
                                                      tableArrivalAP['action_id'].eq(tableArrivalAction['id']),
                                                      tableArrivalAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableArrivalAPS, tableArrivalAPS['id'].eq(tableArrivalAP['id']))

    # Причина отказа от госпитализации
    queryTable = queryTable.leftJoin(tableRefuseReasonAPT, [tableRefuseReasonAPT['name'].eq(u'Причина отказа от госпитализации'),
                                                           tableRefuseReasonAPT['actionType_id'].eq(tableArrivalAction['actionType_id']),
                                                           tableRefuseReasonAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableRefuseReasonAP, [tableRefuseReasonAP['type_id'].eq(tableRefuseReasonAPT['id']),
                                                         tableRefuseReasonAP['action_id'].eq(tableArrivalAction['id']),
                                                         tableRefuseReasonAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableRefuseReasonAPS, tableRefuseReasonAPS['id'].eq(tableRefuseReasonAP['id']))

    queryTable = queryTable.leftJoin(tableRefuseActionsAPT, [tableRefuseActionsAPT['name'].eq(u'Принятые меры при отказе в госпитализации'),
                                                           tableRefuseActionsAPT['actionType_id'].eq(tableArrivalAction['actionType_id']),
                                                           tableRefuseActionsAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableRefuseActionsAP, [tableRefuseActionsAP['type_id'].eq(tableRefuseActionsAPT['id']),
                                                         tableRefuseActionsAP['action_id'].eq(tableArrivalAction['id']),
                                                         tableRefuseActionsAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableRefuseActionsAPS, tableRefuseActionsAPS['id'].eq(tableRefuseActionsAP['id']))

    # Направитель
    queryTable = queryTable.leftJoin(tableOrganisationAPT, [tableOrganisationAPT['name'].eq(u'Кем направлен'),
                                                           tableOrganisationAPT['actionType_id'].eq(tableArrivalAction['actionType_id']),
                                                           tableOrganisationAPT['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableOrganisationAP, [tableOrganisationAP['type_id'].eq(tableRefuseReasonAPT['id']),
                                                         tableOrganisationAP['action_id'].eq(tableArrivalAction['id']),
                                                         tableOrganisationAP['deleted'].eq(0)])
    queryTable = queryTable.leftJoin(tableOrganisationAPO, tableOrganisationAPO['id'].eq(tableOrganisationAP['id']))

    cond.append(db.joinAnd([tableAction['begDate'].ge(begDate), tableAction['begDate'].lt(endDate)]))

    #if orgStructureIdList:
    #    cond.append(tableLastMovingOSHB['master_id'].inlist(orgStructureIdList))

    cols = [
        tableClient['id'].alias('clientId'),
        tableEvent['id'].alias('eventId'),
        tableClient['sex'],
        'age(Client.birthDate, Action.begDate) as clientAge',
        tableDiagnosis['MKB'],
        tableArrivalAPS['value'].alias('arrival'),
        tableArrivalReasonAPS['value'].alias('arrivalReason'),
        #tableAmountDaysAPI['value'].alias('amountDays'),
        tableResultAPS['value'].alias('result'),
        tableDeathEvent['result_id'].alias('deathResult'),
        tableDeathAPS['value'].alias('death'),
        'DATEDIFF(Action.begDate, ArrivalAction.begDate) as amountDays',
        u'rbTraumaType.code LIKE \'%дорожно-транспортн%\' AS trauma',
        'IF(Event.littleStranger_id, 1, IF(Event.pregnancyWeek >= 28, 1, 0)) as pregnant',
        tableRefuseReasonAPS['value'].alias('refuseReason'),
        tableRefuseActionsAPS['value'].alias('refuseActions'),
        tableOrganisationAPO['value'].alias('referringOrganisation')
    ]

    stmt = db.selectStmt(queryTable,
                         cols,
                         where=cond)
    return db.query(stmt)


class CStationaryReportF14(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'СОСТАВ БОЛЬНЫХ В СТАЦИОНАРЕ, СРОКИ И ИСХОДЫ ЛЕЧЕНИЯ')
        self.processedEvents = []
        self.deathEventResults = []

    def getSetupDialog(self, parent):
        result = CReportF30PRRSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processRow(self, row, record):
        sex = forceInt(record.value('sex'))
        age = forceInt(record.value('clientAge'))
        clientId = forceRef(record.value('clientId'))
        eventId = forceRef(record.value('eventId'))
        result = forceString(record.value('result')).lower()
        arrival = forceString(record.value('arrival')).lower()
        arrivalReason = forceString(record.value('arrivalReason')).lower()
        amountDays = forceInt(record.value('amountDays'))
        deathResult = forceRef(record.value('deathResult'))
        death = forceString(record.value('death')).lower()


        #DBG
        if eventId in self.processedEvents:
            print 'Duplicate eventId', eventId

        if not u'умер' in result:   # Выписаны
            if age >= 18:           # Взрослые, старше 18
                row[3] += 1
                if u'по экстренным показаниям' in arrivalReason:
                    row[4] += 1
                if u'смп' in arrival:
                    row[5] += 1

                if sex == 1 and age >= 60 or sex == 2 and age >= 55:    # Пенсионеры
                    row[10] += 1
                    if u'по экстренным показаниям' in arrivalReason:
                        row[11] += 1
                    if u'смп' in arrival:
                        row[12] += 1

            else:                   # Дети
                row[17] += 1
                if u'по экстренным показаниям' in arrivalReason:
                    row[18] += 1
                if u'смп' in arrival:
                    row[19] += 1
                if age < 1:
                    row[20] += 1
        else:                       # Умерли
            if age >= 18:
                row[7] += 1
                if u'патологоанатом' in death:
                    row[8] += 1
                if deathResult in self.deathEventResults:
                    row[9] += 1

                if sex == 1 and age >= 60 or sex == 2 and age >= 55:    # Пенсионеры
                    row[14] += 1
                    if u'патологоанатом' in death:
                        row[15] += 1
                    if deathResult in self.deathEventResults:
                        row[16] += 1
            else:
                row[22] += 1
                if u'патологоанатом' in death:
                    row[23] += 1
                if deathResult in self.deathEventResults:
                    row[24] += 1
                if age < 1:
                    row[25] += 1

        if age >= 18:
            row[6] += amountDays
            if sex == 1 and age >= 60 or sex == 2 and age >= 55:
                row[13] += amountDays

        else:
            row[21] += amountDays

    def processRecord(self, record):
        MKB = forceString(record.value('MKB'))
        result = forceString(record.value('result')).lower()
        amountDays = forceInt(record.value('amountDays'))
        clientAge = forceInt(record.value('clientAge'))
        for (i, row) in enumerate(self.resultSet):
            if MKBinString(MKB, row[2]):
                self.processRow(row, record)
        if MKBinString(MKB, u'S00-T98'):
            trauma = forceBool(record.value('trauma'))
            if trauma:
                self.otherResults[2001][0] += 1
                if u'умер' in result:
                    self.otherResults[2001][1] += 1
                    if amountDays < 31:
                        self.otherResults[2001][2] += 1
                        if amountDays < 8:
                            self.otherResults[2001][3] += 1
        if MKBinString(MKB, 'A00-T98'):
            if u'переведен в другой стационар' in result:
                self.otherResults[2100][0] += 1
            elif u'выписан в дневной стационар' in result:
                self.otherResults[2100][3] += 1
            elif u'направлен в санаторий' in result:
                self.otherResults[2100][4] += 1
        # Не уверен, что в данном случае amountDays отработает корректно.
        if MKBinString(MKB, 'I21, I22'):
            if amountDays < 1:
                self.otherResults[2300][4] += 1
                if  clientAge <= 65:
                    self.otherResults[2300][5] += 1
        if u'умер' in result:
            if forceBool(record.value('pregnant')):
                self.otherResults[2400][0] += 1
                if MKBinString(MKB, 'O00-O99'):
                    self.otherResults[2400][1] += 1

            if clientAge <= 17:
                self.otherResults[2500][0] += 1
            elif clientAge <= 65:
                self.otherResults[2500][1] += 1
                if MKBinString(MKB, 'I60-I64'):
                    self.otherResults[2500][2] += 1

        if forceRef(record.value('referringOrganisation')):
            self.otherResults[2600][0] += 1
            if clientAge < 18:
                self.otherResults[2600][1] += 1

        refuseReason = forceString(record.value('refuseReason')).lower()
        refuseActions = forceString(record.value('refuseActions')).lower()
        if refuseReason == u'отказ пациента':
            self.otherResults[2700][0] += 1
        elif refuseReason == u'нет показаний':
            self.otherResults[2700][1] += 1
        if refuseActions == u'оказана амбулаторная помощь':
            self.otherResults[2700][2] += 1
        elif refuseActions == u'направлен в другой стационар':
            self.otherResults[2700][3] += 1

    def build(self, params):
        self.processedEvents = []
        self.resultSet = [
            [u'Всего', u'1.0', u'A00-T98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: некоторые инфекционные и паразитарные болезни', u'2.0', u'A00-B99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: кишечные инфекции', u'2.1', u'A00-A09', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'туберкулез органов дыхания', u'2.2', u'A15-A16', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'менингококковая инфекция', u'2.3', u'A39', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сепсис', u'2.4', u'A40-A41', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'инфекции, передающиеся преимущественно половым путем', u'2.5', u'A50-A64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый полиомиелит', u'2.6', u'A80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'вирусный гепатит', u'2.7', u'B15-B19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь, вызыванная ВИЧ', u'2.8', u'B20-B24', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'новообразования', u'3.0', u'C00-D48', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: злокачественные новообразования', u'3.1', u'C00-C97', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: злокачественные новообразования лимфатической и кроветворной тканей', u'3.1.1', u'C81-C96', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: фолликулярная (нодулярная) неходжкинская лимфома', u'3.1.1.1', u'C82', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мелкоклеточная (диффузная) неходжкинская лимфома', u'3.1.1.2', u'C83.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мелкоклеточная с расщепленными ядрами (диффузная)неходжкинская лимфома', u'3.1.1.3', u'C83.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'крупноклеточная (диффузная)неходжкинская лимфома', u'3.1.1.4', u'C83.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'иммунобластная (диффузная)неходжкинская лимфома', u'3.1.1.5', u'C83.4', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие типы диффузных неходжкинских лимфом', u'3.1.1.6', u'C83.8', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'диффузная неходжкинская лимфома неуточненная', u'3.1.1.7', u'C83.9', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'периферические и кожные T-клеточные лимфомы', u'3.1.1.8', u'C84', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: другие и неуточненные T-клеточные лимфомы', u'3.1.1.8.1', u'C84.5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие и неуточненные типы неходжкинской лимфомы', u'3.1.1.9', u'C85', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'макроглобулинэмия Вальденстрема', u'3.1.1.10', u'C88.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронический лимфоцитарный лейкоз', u'3.1.1.11', u'C91.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронический миелоидный лейкоз', u'3.1.1.12', u'C92.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'доброкачественные новообразования', u'3.2', u'D10-D36', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: лейомиома матки', u'3.2.1', u'D25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'доброкачественные новообразования яичника', u'3.2.2', u'D27', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'4.0', u'D50-D89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: анемия', u'4.1', u'D50-D64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'апластические анемии', u'4.1.1', u'D60-D61', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нарушения свертываемости крови', u'4.2', u'D65-D69', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: диссеминированное внутрисосудистое свертывание (синдром дефибринации)', u'4.2.1', u'D65', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гемофилия', u'4.2.2', u'D66-D68', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'отдельные нарушения, вовлекающие иммунный механизм', u'4.3', u'D80-D89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'5.0', u'E00-E89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: гипотиреоз', u'5.1', u'E01-E03', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'тиреотоксикоз (гипертиреоз)', u'5.2', u'E05', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'тиреоидит', u'5.3', u'E06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сахарный диабет', u'5.4', u'E10-E14', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: сахарный диабет инсулинзависимый', u'5.4.1', u'E10', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сахарный диабет инсулиннезависимый', u'5.4.2', u'E11', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них с поражением глаз (из стр.5.4)', u'5.4.3', u'E10.3, E11.3, E12.3, E13.3, E14.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гиперфункция гипофиза', u'5.5', u'E22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипопитуитаризм', u'5.6', u'E23.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'несахарный диабет', u'5.7', u'E23.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'адреногенитальнве расстройства', u'5.8', u'E25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дисфункция яичников', u'5.9', u'E28', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дисфункция яичек', u'5.10', u'E29', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'ожирение', u'5.11', u'E66', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'фенилкетонурия', u'5.12', u'E70.0, E70.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нарушения обмена галактозы (галактоземия)', u'5.13', u'E74.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь Гоше', u'5.14', u'E75.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нарушения обмена гликозамино-гликанов (мукополисахаридоз)', u'5.15', u'E76.0-E76.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'муковисцидоз', u'5.16', u'E84', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'психические расстройства и расстройства поведения', u'6.0', u'F01-F99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: психические расстройства и расстройства поведения, связанные с употреблением психоактивных веществ', u'6.1', u'F10-F19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни нервной системы', u'7.0', u'G00-G99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: воспалительные болезни центральной нервной системы', u'7.1', u'G00-G09', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: бактериальный менингит', u'7.1.1', u'G00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'энцефалит, миелит и энцефаломиелит', u'7.1.2', u'G04', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'системные атрофии, поражающие преимущественно центральную нервную систему', u'7.2', u'G10-G12', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'экстрапирамидные и другие двигательные нарушения', u'7.3', u'G20, G21, G23-G25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них:болезнь Паркинсона', u'7.3.1', u'G20', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие экстрапирамидные и двигательные нарушения', u'7.3.2', u'G25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие дегенеративные болезни нервной системы', u'7.4', u'G30-G31', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: болезнь Альцгеймера', u'7.4.1', u'G30', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'демиелинизирующие болезни центральной нервной системы', u'7.5', u'G35-G37', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: рассеянный склероз', u'7.5.1', u'G35', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'эпизодические и пароксизмальные расстройства', u'7.6', u'G40-G47', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: эпилепсия, эпилептический статус', u'7.6.1', u'G40-G41', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'преходящие транзиторные церебральные ишемические приступы [атаки] и родственные синдромы', u'7.6.2', u'G45', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'поражения отдельных нервов, нервных корешков и сплетений, полиневропатии и другие поражения периферической нервной системы', u'7.7', u'G50-G64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: синдром Гийена-Барре', u'7.7.1', u'G61.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни нервно-мышечного синапса и мышц', u'7.8', u'G70-G73', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: миастения', u'7.8.1', u'G70.0, G70.2, G70.9', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мышечная дистрофия Дюшенна', u'7.8.2', u'G71.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'церебральный паралич и другие паралитические синдромы', u'7.9', u'G80-G83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: церебральный паралич', u'7.9.1', u'G80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'расстройства вегетативной (автономной)', u'7.10', u'G90', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сосудистые миелопатии', u'7.11', u'G95.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни глаза и его придаточного аппарата', u'8.0', u'H00-H59', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: язва роговицы', u'8.1', u'H16.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'катаракты', u'8.2', u'H25-H26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дегенерация макулы и заднего полюса', u'8.3', u'H35.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'глаукома', u'8.4', u'H40', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'неврит зрительного нерва', u'8.5', u'H46', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'слепота и пониженное зрение', u'8.6', u'H54', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: слепота обоих глаз', u'8.6.1', u'H54.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни уха и сосцевидного отростка', u'9.0', u'H60-H95', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни среднего уха и сосцевидного отростка', u'9.1', u'H65-H66, H68-H74', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острый отит', u'9.1.1', u'H65.0, H65.1, H66.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронический отит', u'9.1.2', u'H65.2-H65.4, H66.1-H66.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни слуховой (евстахиевой) трубы', u'9.1.3', u'H68-H69', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'перфорация барабанной перепонки', u'9.1.4', u'H72', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни среднего уха и сосцевидного отростка', u'9.1.5', u'H74', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни внутреннего уха', u'9.2', u'H80, H81, H83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: отосклероз', u'9.2.1', u'H80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь Меньера', u'9.2.2', u'H81.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'ондуктивная и нейросенсорная', u'9.3', u'H90', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: кондуктивная потеря слуха двусторонняя', u'9.3.1', u'H90.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нейросенсорная потеря слуха двусторонняя', u'9.3.2', u'H90.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни системы кровообращения', u'10.0', u'I00-I99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острая ревматическая лихорадка', u'10.1', u'I00-I02', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронические ревматические болезни сердца', u'10.2', u'I05-I09', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни, характеризующиеся повышенным кровяным давлением', u'10.3', u'I10-I13', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: эссенциальная гипертензия', u'10.3.1', u'I10', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипертензивная болезнь сердца (гипертоническая болезнь с преимущественным поражением сердца)', u'10.3.2', u'I11', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипертензивная (гипертоническая) болезнь с преимущественным поражением почек', u'10.3.3', u'I12', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипертензивная (гипертоническая) болезнь с преимущественным поражением сердца и почек', u'10.3.4', u'I13', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'ишемические болезни сердца', u'10.4', u'I20-I25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: стенокардия', u'10.4.1', u'I20', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из нее: нестабильная стенокардия', u'10.4.1.1', u'I20.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый инфаркт миокарда', u'10.4.2', u'I21', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'повторный инфаркт миокарда', u'10.4.3', u'I22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие формы острых ишемических болезней сердца', u'10.4.4', u'I24', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хроническая ишемическая болезнь сердца', u'10.4.5', u'I25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из нее постинфарктный кардиосклероз', u'10.4.5.1', u'I25.8', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'легочная эмболия', u'10.5', u'I26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни сердца', u'10.6', u'I30-I52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острый и подострый эндокардит', u'10.6.1', u'I33', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый миокардит', u'10.6.2', u'I40', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'кардиомиопатия', u'10.6.3', u'I42', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'предсердно-желудочковая [атриовентрикулярная] блокада', u'10.6.4', u'I44.0-I44.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'желудочковая тахикардия', u'10.6.5', u'I47.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'фибрилляция и трепетание предсердий', u'10.6.6', u'I48', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'цереброваскулярные болезни', u'10.7', u'I60-I69', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: субарахноидальное кровоизлияние', u'10.7.1', u'I60', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'внутримозговые и другие внутричерепные кровоизлияния', u'10.7.2', u'I61,I62', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'инфаркт мозга', u'10.7.3', u'I63', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'инсульт неуточненный, как кровоизлияние или инфаркт', u'10.7.4', u'I64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'закупорка и стеноз прецеребральных, це- ребральных артерий, не приводящих к инфаркту мозга и другие цереброваскулярные болезни', u'10.7.5', u'I65-I66', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие цереброваскулярные болезни', u'10.7.6', u'I67', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: церебральный атеросклероз', u'10.7.6.1', u'I67.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'атеросклероз артерий конечностей, тромбангиит облитерирующий', u'10.8', u'I70.2,I73.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни вен, лимфатических сосудов и лимфатических узлов', u'10.9', u'I80-I89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: флебит и тромбофлебит', u'10.9.1', u'I80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'тромбоз портальной вены', u'10.9.2', u'I81', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'варикозное расширение вен нижних конечностей', u'10.9.3', u'I83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'геморрой', u'10.9.4', u'I84', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни органов дыхания', u'11.0', u'J00-J98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острые респираторные верхних дыхательных путей', u'11.1', u'J00-J06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острый ларингит и трахеит', u'11.1.1', u'J04', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый обструктивный ларингит [круп] и эпиглоттит', u'11.1.2', u'J05', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'грипп', u'11.2', u'J10-J11', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'пневмония', u'11.3', u'J12-J18', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острые респираторные инфекции', u'11.4', u'J20-J22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'аллергический ринит (поллиноз)', u'11.5', u'J30.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронические болезни миндалин и аденоидов, перитонзиллярный абсцесс', u'11.6', u'J35-J36', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'бронхит хронический и неуточненный, эмфизема', u'11.7', u'J40-J43', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другая хроническая обструктивная легочная болезнь, бронхоэктатическая болезнь', u'11.8', u'J44, J47', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'астма; астматический статус', u'11.9', u'J45, J46', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'др. интерстициальные легочные болезни, гнойные и некротические состояния нижних дыхат. путей, др. б-ни плевры', u'11.10', u'J84-J94', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни органов пищеварения', u'12.0', u'K00-K92', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: язва желудка и двенадцатиперстной кишки', u'12.1', u'K25-K26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гастрит и дуоденит', u'12.2', u'K29', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'грыжи', u'12.3', u'K40-K46', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'неинфекционный энтерит и колит', u'12.4', u'K50-K52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: болезнь Крона', u'12.4.1', u'K50', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'язвенный колит', u'12.4.2', u'K51', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни кишечника', u'12.5', u'K55-K63', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них:паралитический илеус и непроходимость кишечника без грыжи', u'12.5.1', u'K56', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дивертикулярная болезнь кишечника', u'12.5.2', u'K57', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'перитонит', u'12.6', u'K65', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни печени', u'12.7', u'K70-K76', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: фиброз и цирроз печени', u'12.7.1', u'K74', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни желчного пузыря, желчевыводящих путей', u'12.8', u'K80-K83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни поджелудочной железы', u'12.9', u'K85-K86', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый панкреатит', u'12.9.1', u'K85', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни кожи и подкожной клетчатки', u'13.0', u'L00-L99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них псориаз, всего', u'13.1', u'L40', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: псориаз артропатический', u'13.1.1', u'L40.5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дискоидная красная волчанка', u'13.2', u'L93.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'локализованная склеродермия', u'13.3', u'L94.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни костно-мышечной системы и соединительной ткани', u'14.0', u'M00-M99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: артропатии', u'14.1', u'M00-M25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: реактивные артропатии', u'14.1.1', u'M02', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'серопозитивный и другие ревматоидные артриты', u'14.1.2', u'M05-M06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'юношеский (ювенильный) артрит', u'14.1.3', u'M08', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'артрозы', u'14.1.4', u'M15-M19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'системные поражения соединительной ткани', u'14.2', u'M30-M35', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'деформирующие дорсопатии', u'14.3', u'M40-M43', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'спондилопатии', u'14.4', u'M45-M49', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'синовиты и теносиновиты', u'14.5', u'M65-M68', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'остеопатии и хондропатии', u'14.6', u'M80-M94', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: остеопорозы', u'14.6.1', u'M80-M81', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни мочеполовой системы', u'15.0', u'N00-N99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: гломерулярные, тубулоинтерстициальные болезни почек, почечная недостаточность и другие болезни почки и мочеточника', u'15.1', u'N00-N15, N25-N28', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'почечная недостаточность', u'15.2', u'N17-N19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мочекаменная болезнь', u'15.3', u'N20-N21, N23', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни мочевой системы', u'15.4', u'N30-N32, N34-N36, N39', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни предстательной железы', u'15.5', u'N40-N42', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'доброкачественная дисплазия молочной железы', u'15.6', u'N60', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'воспалительные болезни женских тазовых органов', u'15.7', u'N70-N76', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: сальпингит и оофорит', u'15.7.1', u'N70', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'эндометриоз', u'15.8', u'N80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'расстройства менструаций', u'15.9', u'N91-N94', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'женское бесплодие', u'15.10', u'N97', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'беременность, роды и послеродовой период', u'16.0', u'O00-O99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'отдельные состояния, возникающие в перинатальном периоде', u'17.0', u'P00-P96', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии (пороки развития), деформации и хромосомные нарушения', u'18.0', u'Q00-Q99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: врожденные аномалии [пороки развития]', u'18.1', u'Q00-Q07', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии системы кровообращения', u'18.2', u'Q20-Q28', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии кишечника', u'18.3', u'Q41, Q42', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь Гиршпрунга', u'18.4', u'Q43.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии тела и шейки матки, другие врожденные аномалии женских половых', u'18.5', u'Q51-Q52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'неопределенность пола и псевдогермафродитизм', u'18.6', u'Q56', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденный ихтиоз', u'18.7', u'Q80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нейрофиброматоз (незлокачественный)', u'18.8', u'Q85.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'синдром Дауна', u'18.9', u'Q90', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях, не классифицированные в других рубриках', u'19.0', u'R00-R99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'травмы, отравления и некоторые другие последствия воздействия внешних причин', u'20.0', u'S00-T98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: переломы', u'20.1', u'S02, S12, S22, S32, S42, S52, S62, S72, S82, S82, T02, T08, T10, T12, T14.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: переломы черепа и лицевых костей', u'20.1.1', u'S02', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'внутричерепные травмы', u'20.2', u'S06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: термические и химические ожоги', u'20.3', u'T20-T32', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'отравления лекарственными средствами, медикаментами и биологическими веществами, токсическое действие веществ преимущественно немедицинского назначения', u'20.4', u'T36-T65', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: токсическое действие алкоголя', u'20.4.1', u'T51', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Кроме того:факторы, влияющие на состояние здоровья и обращения в учреждения здравоохранения', u'21.0', u'Z00-Z99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: носительство инфекционной болезни', u'21.1', u'Z22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'наличие илеостомы, колостомы', u'21.2', u'Z93.2, Z93.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.otherResults = {2001: [0, 0, 0, 0],
                             2100: [0, '___', '___', 0, 0],
                             2200: ['___', '___', '___', '___', '___'],
                             2300: ['___', '___', '___', '___', 0, 0, '___', '___'],
                             2301: ['___', '___', '___'],
                             2400: [0, 0],
                             2500: [0, 0, 0],
                             2600: [0, 0, '___', '___', '___'],
                             2700: [0, 0, 0, 0]}

        db = QtGui.qApp.db
        deathEventTypePurposeId = forceRef(db.translate('rbEventTypePurpose', 'code', '5', 'id')) # Летальность
        self.deathEventResults = db.getIdList('rbResult', 'id', 'eventPurpose_id=%d AND code != \'0\'' % deathEventTypePurposeId)
        query = selectData(params, deathEventTypePurposeId)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            self.processRecord(query.record())

        # now text
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        orgId = QtGui.qApp.currentOrgId()
        orgInfo = getOrganisationInfo(orgId)
        if not orgInfo:
            QtGui.qApp.preferences.appPrefs['orgId'] = QtCore.QVariant()
        shortName = getVal(orgInfo, 'shortName', u'не задано')

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(bf)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        #cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.insertText(u'\nЛПУ: ' + shortName)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        #cursor.setBlockFormat(bf)
        #cursor.insertText(u'1. СОСТАВ БОЛЬНЫХ В СТАЦИОНАРЕ, СРОКИ И ИСХОДЫ ЛЕЧЕНИЯ')

        boldFormat = QtGui.QTextCharFormat()
        boldFormat.setFontWeight(QtGui.QFont.Bold)

        plainFormat = QtGui.QTextCharFormat()

        tableFormat = QtGui.QTextTableFormat()
        tableFormat.setBorder(0)
        tableFormat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 50), QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 50)])
        table = cursor.insertTable(1, 2, tableFormat)

        c = table.cellAt(0, 0).lastCursorPosition()
        c.setBlockFormat(CReportBase.AlignLeft)
        c.setCharFormat(boldFormat)
        c.insertText(u'(2000)')

        c = table.cellAt(0, 1).lastCursorPosition()
        c.setBlockFormat(CReportBase.AlignRight)
        c.setCharFormat(QtGui.QTextCharFormat())
        c.insertText(u'Код по ОКЕИ: человек - ')

        cursor.movePosition(QtGui.QTextCursor.End)


        adultTableColumns = [
            ( '38%', [u'Наименование болезни', u'', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '4%', [u'№ строки', u'', u'', u'', u'2'], CReportBase.AlignLeft),
            ( '10%', [u'Код по МКБ Х пересмотра', u'', u'', u'', u'3'], CReportBase.AlignLeft),
            ( '7%', [u'A. Взрослые (18 лет и старше)', u'Выписано больных', u'Всего', u'', u'4'], CReportBase.AlignLeft),
            ( '7%', [u'', u'', u'Из них доставленных по экстренным показаниям', u'', u'5'], CReportBase.AlignLeft),
            ( '7%', [u'', u'', u'Из них больных, доставленных скорой медицинской помощью', u'', u'6'], CReportBase.AlignLeft),
            ( '7%', [u'', u'Проведено выписанными койко-дней', u'', u'', u'7'], CReportBase.AlignLeft),
            ( '7%', [u'', u'Умерло', u'Всего', u'', u'8'], CReportBase.AlignLeft),
            ( '7%', [u'', u'', u'Из них', u'Проведено патологоанатомических вскрытий', u'9'], CReportBase.AlignLeft),
            ( '6%', [u'', u'', u'', u'Установлено расхождений диагнозов', u'10'], CReportBase.AlignLeft),
        ]
        elderTableColumns = [
            ( '38%', [u'Наименование болезни', u'', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '4%', [u'№ строки', u'', u'', u'', u'2'], CReportBase.AlignLeft),
            ( '10%', [u'Код по МКБ Х пересмотра', u'', u'', u'', u'3'], CReportBase.AlignLeft),
            ( '7%', [u'Б. Взрослые старше трудоспособного возраста (с 55 лет у женщин и с 60 лет у мужчин)', u'Выписано больных', u'Всего', u'', u'11'], CReportBase.AlignLeft),
            ( '7%', [u'', u'', u'Из них доставленных по экстренным показаниям', u'', u'12'], CReportBase.AlignLeft),
            ( '7%', [u'', u'', u'Из них больных, доставленных скорой медицинской помощью', u'', u'13'], CReportBase.AlignLeft),
            ( '7%', [u'', u'Проведено выписанными койко-дней', u'', u'', u'14'], CReportBase.AlignLeft),
            ( '7%', [u'', u'Умерло', u'Всего', u'', u'15'], CReportBase.AlignLeft),
            ( '7%', [u'', u'', u'Из них', u'Проведено патологоанатомических вскрытий', u'16'], CReportBase.AlignLeft),
            ( '6%', [u'', u'', u'', u'Установлено расхождений диагнозов', u'17'], CReportBase.AlignLeft),
        ]
        childrenTableColumns = [
            ( '38%', [u'Наименование болезни', u'', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '4%', [u'№ строки', u'', u'', u'', u'2'], CReportBase.AlignLeft),
            ( '10%', [u'Код по МКБ Х пересмотра', u'', u'', u'', u'3'], CReportBase.AlignLeft),
            ( '5%', [u'В. Дети (в возрасте 0-17 включительно)', u'Выписано больных', u'Всего', u'', u'18'], CReportBase.AlignLeft),
            ( '5%', [u'', u'', u'Из них доставленных по экстренным показаниям', u'', u'19'], CReportBase.AlignLeft),
            ( '6%', [u'', u'', u'Из них больных, доставленных скорой медицинской помощью', u'', u'20'], CReportBase.AlignLeft),
            ( '6%', [u'', u'', u'Из них в возрасте до 1 года (из гр. 18)', u'', u'21'], CReportBase.AlignLeft),
            ( '6%', [u'', u'Проведено выписанными койко-дней', u'', u'', u'22'], CReportBase.AlignLeft),
            ( '5%', [u'', u'Умерло', u'Всего', u'', u'23'], CReportBase.AlignLeft),
            ( '5%', [u'', u'', u'Из них', u'Проведено патологоанатомических вскрытий', u'24'], CReportBase.AlignLeft),
            ( '5%', [u'', u'', u'', u'Установлено расхождений диагнозов', u'25'], CReportBase.AlignLeft),
            ( '5%', [u'', u'', u'Из них умерло в возрасте до 1 года', u'', u'26'], CReportBase.AlignLeft),
        ]

        subRowSize = 7                  # (Длина строки - 3 первых столбца)
        table = createTable(cursor, adultTableColumns)

        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 4, 1)
        table.mergeCells(0, 2, 4, 1)
        table.mergeCells(0, 3, 1, 7)
        table.mergeCells(1, 3, 1, 3)
        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(2, 5, 2, 1)
        table.mergeCells(1, 6, 3, 1)
        table.mergeCells(2, 7, 1, 3)
        table.mergeCells(2, 7, 2, 1)
        table.mergeCells(2, 8, 1, 2)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            table.setText(i, 2, row[2])
            for j in range(subRowSize):
                table.setText(i, 3 + j, row[3 + j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText('\n')
        table = createTable(cursor, elderTableColumns)

        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 4, 1)
        table.mergeCells(0, 2, 4, 1)
        table.mergeCells(0, 3, 1, 7)
        table.mergeCells(1, 3, 1, 3)
        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(2, 5, 2, 1)
        table.mergeCells(1, 6, 3, 1)
        table.mergeCells(2, 7, 1, 3)
        table.mergeCells(2, 7, 2, 1)
        table.mergeCells(2, 8, 1, 2)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            table.setText(i, 2, row[2])
            for j in range(subRowSize):
                table.setText(i, 3 + j, row[10 + j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText('\n')
        subRowSize = 9                  # (Длина строки - 3 первых столбца)
        table = createTable(cursor, childrenTableColumns)

        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 4, 1)
        table.mergeCells(0, 2, 4, 1)
        table.mergeCells(0, 3, 1, 9)
        table.mergeCells(1, 3, 1, 4)
        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(2, 5, 2, 1)
        table.mergeCells(2, 6, 2, 1)
        table.mergeCells(1, 7, 3, 1)
        table.mergeCells(1, 8, 1, 4)
        table.mergeCells(2, 8, 2, 1)
        table.mergeCells(2, 9, 1, 2)
        table.mergeCells(2, 11, 2, 1)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            table.setText(i, 2, row[2])
            for j in range(subRowSize):
                table.setText(i, 3 + j, row[17 + j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText('\n')

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2001)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Из общего числа больных с травмами (стр. 20.0), больные, пострадавшие в ДТП __%s__, из них умерло: всего __%s__, в том числе в первые 0-30 суток __%s__, из них в первые 0-7 суток __%s__.\n' % tuple(self.otherResults[2001]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2100)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Кроме того, больные, переведенные в другие стационары __%s__, в том числе новорожденные _%s_, '
                          u'из них недоношенные _%s_, из общего числа закончивших лечение (т2000, стр. 1) направлены в '
                          u'стационары восстановительного лечения __%s__, в санатории __%s__.\n' % tuple(self.otherResults[2100]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2200)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Из общего числа умерших (стр. 1) умерло новорожденных в первые 168 часов _%s_. Умерло в первые 24 '
                          u'часа после поступления в стационар: в возрасте 0-24 часа после рождения _%s_, из них недоношенных '
                          u'_%s_, до 1 года (без умерших в первые 24 часа после рождения) _%s_, в том числе от пневмонии _%s_.\n' % tuple(self.otherResults[2200]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2300)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Поступило с острым инфарктом миокарда в первые сутки от начала заболевания _%s_, в т.ч. в первые 12 '
                          u'часов _%s_, из них проведена тромболитическая терапия _%s_, стентирование _%s_. Из общего числа умерших '
                          u'(стр. 10.4.2+10.4.3.) умерло больных с инфарктом миокарда в первые 24 часа после поступления '
                          u'в стационар __%s__, в том числе в возрасте до 65 лет __%s__. Из числа умерших больных с '
                          u'инфарктом миокарда в первые 24 часа после поступления в стационар проведена тромболитическая '
                          u'терапия _%s_, стентирование _%s_.\n' % tuple(self.otherResults[2300]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2301)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Поступило больных острыми цереброваскулярными болезнями (стр. 10.7.1-10.7.5) в первые сутки '
                          u'от начала заболевания __%s__, из нич в первые 6 _%s_ из них (гр. 2) проведена тромболитическая '
                          u' терапия в первые 6 часов _%s_ (исключена баллонная ангиопластика)\n' % tuple(self.otherResults[2301]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2400)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Умерло беременных, рожениц и родильниц (при сроке беременности 28 недель и более) __%s__. Из '
                          u'них умерло от заболеваний, осложняющих беременность и роды __%s__.\n' % tuple(self.otherResults[2400]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2500)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Из общего числа умерших (стр. 1, гр. 7, 14) умерло в первые 24 часа после поступления в стационар: '
                          u'детей в возрасте 0-17 лет включительно __%s__; больных в возрасте от 18 до 65 лет __%s__, из '
                          u'них больных острыми цереброваскулярными болезнями (стра. 10.7.1-10.7.4) __%s__.\n' % tuple(self.otherResults[2500]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2600)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Из общего числа выписанные (стр. 1, гр. 4) было направлено в стационар поликлиникой __%s__, '
                          u'в т.ч. детей __%s__, полицией _%s_, в т.ч. детей _%s_, обратились самостоятельно _%s_.\n' % tuple(self.otherResults[2600]))

        cursor.setCharFormat(boldFormat)
        cursor.insertText(u'(2700)\t')
        cursor.setCharFormat(plainFormat)
        cursor.insertText(u'Из общего числа отказов в госпитализации (из формы № 001/у, гр. 14): отказ пациента от госпитализации '
                          u'__%s__, не было показаний к госпитализации __%s__, медицинская помощь была оказана амбулаторно '
                          u'__%s__, направлены в другие стационары __%s__.\n' % tuple(self.otherResults[2700]))

        return doc
