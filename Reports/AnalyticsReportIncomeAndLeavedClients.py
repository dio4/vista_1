# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceInt, forceRef, forceString, formatShortNameInt, formatName
from Orgs.Utils         import getOrgStructureFullName, getOrgStructureName
from RefBooks.QuotaType import getQuotaTypeClassNameList

from Reports.AnalyticsReportHospitalizedClients import CStationaryAnalyticsSetupDialog, getChildrenIdList
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


eventtypeids = [None, None]
eventtypetexts = {}
nurseCols = 10
def selectData(params):
##    print params
    begDate          = params.get('begDate', QtCore.QDate.currentDate())
    endDate          = params.get('endDate', QtCore.QDate.currentDate())
    financeId        = params.get('financeId', None)
    contractId       = params.get('contractId', None)
    chkQuotaClass    = params.get('chkQuotaClass', False)
    quotaClass       = params.get('quotaClass', 0)
    quotaTypeId      = params.get('quotaTypeId', None)
    chkDetailClients = params.get('chkDetailClients', False)
    chkNurseChief    = params.get('chkNurseChief', False)
    db = QtGui.qApp.db
    if not chkNurseChief:
        tableClient                     = db.table('Client')
        tableEvent                      = db.table('Event')
        tableContract                   = db.table('Contract')
        tableFinance                    = db.table('rbFinance')

        tableReceivedAction             = db.table('Action').alias('ActionReceived')
        tableReceivedActionType         = db.table('ActionType').alias('ActionTypeReceived')
        tableReceivedActionProperty     = db.table('ActionProperty').alias('ActionPropertyReceived')
        tableReceivedActionPropertyType = db.table('ActionPropertyType').alias('ActionPropertyTypeReceived')
        tableReceivedActionPropertyOrgStructure = db.table('ActionProperty_OrgStructure').alias('ActionPropertyOrgStructureReceived')
        tableReceivedOrgStructure       = db.table('OrgStructure').alias('OrgStructureReceived')
        

        tableMovingActionProperty       = db.table('ActionProperty').alias('ActionPropertyMoving')
        tableMovingActionPropertyType   = db.table('ActionPropertyType').alias('ActionPropertyTypeMoving')
        tableMovingActionPropertyOrgStructure   = db.table('ActionProperty_OrgStructure').alias('ActionPropertyOrgStructureMoving')
        tableMovingOrgStructure         = db.table('OrgStructure').alias('OrgStructureMoving')

        tableActionMovingStaying                       = db.table('Action').alias('ActionMovingStaying')
        tableActionTypeMovingStaying                   = db.table('ActionType').alias('ActionTypeMovingStaying')
        tableMovingActionPropertyStaying               = db.table('ActionProperty').alias('ActionPropertyMovingStaying')
        tableMovingActionPropertyTypeStaying           = db.table('ActionPropertyType').alias('ActionPropertyTypeMovingStaying')
        tableMovingActionPropertyOrgStructureStaying   = db.table('ActionProperty_OrgStructure').alias(
                                                                  'ActionPropertyOrgStructureMovingStaying')
        tableMovingStayingOrgStructure                 = db.table('OrgStructure').alias('OrgStructureMovingStaying')
        
        tableMovingActionPropertyFrom                  = db.table('ActionProperty').alias('ActionPropertyMovingFrom')
        tableMovingActionPropertyTypeFrom              = db.table('ActionPropertyType').alias('ActionPropertyTypeMovingFrom')
        tableMovingActionPropertyOrgStructureFrom      = db.table('ActionProperty_OrgStructure').alias(
                                                                  'ActionPropertyOrgStructureMovingFrom')
        tableMovingStayingOrgStructureFrom             = db.table('OrgStructure').alias('OrgStructureMovingFrom')
        
        
        tableActionLeaved                              = db.table('Action').alias('ActionLeaved')
        tableActionTypeLeaved                          = db.table('ActionType').alias('ActionTypeLeaved')
        tableActionPropertyLeaved                      = db.table('ActionProperty').alias('ActionPropertyLeaved')
        tableActionPropertyTypeLeaved                  = db.table('ActionPropertyType').alias('ActionPropertyTypeLeaved')
        tableActionPropertyLeavedResult                = db.table('ActionProperty_String').alias('tableActionPropertyLeavedResult')

        tableQuotaAction                  = db.table('Action').alias('ActionQuota')
        tableQuotaActionType              = db.table('ActionType').alias('ActionTypeQuota')
        tableQuotaActionProperty          = db.table('ActionProperty').alias('ActionPropertyQuota')
        tableQuotaActionPropertyType      = db.table('ActionPropertyType').alias('ActionPropertyTypeQuota')
        tableActionPropertyClientQuoting  = db.table('ActionProperty_Client_Quoting')
        tableClientQuoting                = db.table('Client_Quoting')
        tableQuotaType                    = db.table('QuotaType')

        queryTable = tableEvent.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    #    queryTable = queryTable.leftJoin( tableContract, tableContract['id'].eq(tableEvent['contract_id']))
    #    queryTable = queryTable.leftJoin( tableFinance, tableFinance['id'].eq(tableContract['finance_id']))


        ## Действие выбытие
        actionTypeLeavedIdList = db.getIdList('ActionType', 'id', 'flatCode LIKE \'leaved%\' AND deleted=0')
        
        actionLeavedJoinCond = [tableActionLeaved['event_id'].eq(tableEvent['id']), 
                                tableActionLeaved['actionType_id'].inlist(actionTypeLeavedIdList)]
        
        queryTable = queryTable.leftJoin(tableActionLeaved, db.joinAnd(actionLeavedJoinCond))
        queryTable = queryTable.leftJoin(tableActionTypeLeaved,
                                          tableActionTypeLeaved['id'].eq(tableActionLeaved['actionType_id']))
        
        actionPropertyTypeLeavedJoinCond = [tableActionPropertyTypeLeaved['actionType_id'].eq(
                                            tableActionTypeLeaved['id']),
                                            tableActionPropertyTypeLeaved['name'].eq(u'Исход госпитализации')]
        queryTable = queryTable.leftJoin(tableActionPropertyTypeLeaved, db.joinAnd(actionPropertyTypeLeavedJoinCond))
        
        actionPropertyLeavedJoinCond = [tableActionPropertyLeaved['type_id'].eq(tableActionPropertyTypeLeaved['id']),
                                        tableActionPropertyLeaved['action_id'].eq(tableActionLeaved['id'])]
        
        queryTable = queryTable.leftJoin(tableActionPropertyLeaved, actionPropertyLeavedJoinCond)
        
        queryTable = queryTable.leftJoin(tableActionPropertyLeavedResult, tableActionPropertyLeavedResult['id'].eq(tableActionPropertyLeaved['id']))

        # привязка к действию движение
        actionTypeMovingIdList = db.getIdList('ActionType', 'id', 'flatCode LIKE \'moving%\' AND deleted=0')


        ## Отделение пребывание
        actionMovingStayingJoinCond = [tableActionMovingStaying['event_id'].eq(tableEvent['id']),
                                       tableActionMovingStaying['actionType_id'].inlist(actionTypeMovingIdList),
                                 ]
        queryTable = queryTable.leftJoin(tableActionMovingStaying, db.joinAnd(actionMovingStayingJoinCond))
        queryTable = queryTable.innerJoin(tableActionTypeMovingStaying,
                                          tableActionTypeMovingStaying['id'].eq(tableActionMovingStaying['actionType_id']))


        actionPropertyTypeMovingStayingJoinCond = [tableMovingActionPropertyTypeStaying['actionType_id'].eq(
                                                   tableActionTypeMovingStaying['id']),
                                                   tableMovingActionPropertyTypeStaying['name'].eq(u'Отделение пребывания')]
        queryTable = queryTable.innerJoin(tableMovingActionPropertyTypeStaying, db.joinAnd(actionPropertyTypeMovingStayingJoinCond))

        actionPropertyMovingStayingJoinCond = [tableMovingActionPropertyStaying['type_id'].eq(
                                                                        tableMovingActionPropertyTypeStaying['id']),
                                                tableMovingActionPropertyStaying['action_id'].eq(tableActionMovingStaying['id'])]
        queryTable = queryTable.leftJoin(tableMovingActionPropertyStaying,
                                         actionPropertyMovingStayingJoinCond)

        queryTable = queryTable.leftJoin(tableMovingActionPropertyOrgStructureStaying,
                                         tableMovingActionPropertyOrgStructureStaying['id'].eq(tableMovingActionPropertyStaying['id']))

        queryTable = queryTable.leftJoin(tableMovingStayingOrgStructure,
                                         tableMovingStayingOrgStructure['id'].eq(
                                         tableMovingActionPropertyOrgStructureStaying['value']))
        
        
        
        ### откуда переведен
        actionPropertyTypeMovingFromJoinCond = [tableMovingActionPropertyTypeFrom['actionType_id'].eq(
                                                   tableActionTypeMovingStaying['id']),
                                                   tableMovingActionPropertyTypeFrom['name'].eq(u'Переведен из отделения')]
        queryTable = queryTable.leftJoin(tableMovingActionPropertyTypeFrom, db.joinAnd(actionPropertyTypeMovingFromJoinCond))

        actionPropertyMovingFromJoinCond = [tableMovingActionPropertyFrom['type_id'].eq(tableMovingActionPropertyTypeFrom['id']),
                                            tableMovingActionPropertyFrom['action_id'].eq(tableActionMovingStaying['id'])]
        queryTable = queryTable.leftJoin(tableMovingActionPropertyFrom, actionPropertyMovingFromJoinCond)

        queryTable = queryTable.leftJoin(tableMovingActionPropertyOrgStructureFrom, 
                                         tableMovingActionPropertyOrgStructureFrom['id'].eq(tableMovingActionPropertyFrom['id']))

        queryTable = queryTable.leftJoin(tableMovingStayingOrgStructureFrom,
                                         tableMovingStayingOrgStructureFrom['id'].eq(tableMovingActionPropertyOrgStructureFrom['value']))

        

        ## переведен в отделение

        actionPropertyTypeMovingJoinCond = [tableMovingActionPropertyType['actionType_id'].eq(
                                                   tableActionTypeMovingStaying['id']),
                                                   tableMovingActionPropertyType['name'].eq(u'Переведен в отделение')]
        queryTable = queryTable.innerJoin(tableMovingActionPropertyType, db.joinAnd(actionPropertyTypeMovingJoinCond))

        actionPropertyMovingJoinCond = [tableMovingActionProperty['type_id'].eq(tableMovingActionPropertyType['id']),
                                        tableMovingActionProperty['action_id'].eq(tableActionMovingStaying['id'])]
        queryTable = queryTable.leftJoin(tableMovingActionProperty,
                                         actionPropertyMovingJoinCond)

        queryTable = queryTable.leftJoin(tableMovingActionPropertyOrgStructure,
                                         tableMovingActionPropertyOrgStructure['id'].eq(tableMovingActionProperty['id']))

        queryTable = queryTable.leftJoin(tableMovingOrgStructure,
                                         tableMovingOrgStructure['id'].eq(tableMovingActionPropertyOrgStructure['value']))

        ## получение начальной даты для первого действия движения из даты закрытия действия поступление
        actionTypeReceivedIdList = db.getIdList('ActionType', 'id', 'flatCode LIKE \'received%\' AND deleted=0')

        actionReceivedJoinCond = [tableReceivedAction['event_id'].eq(tableEvent['id']),
                                  tableReceivedAction['actionType_id'].inlist(actionTypeReceivedIdList)
                                 ]
        queryTable = queryTable.innerJoin(tableReceivedAction, actionReceivedJoinCond)
        queryTable = queryTable.innerJoin(tableReceivedActionType,
                                          tableReceivedActionType['id'].eq(tableReceivedAction['actionType_id']))
        actionPropertyTypeReceivedJoinCond = [tableReceivedActionPropertyType['actionType_id'].eq(
                                                   tableReceivedActionType['id']),
                                                   tableReceivedActionPropertyType['name'].eq(u'Направлен в отделение')]
        queryTable = queryTable.innerJoin(tableReceivedActionPropertyType, db.joinAnd(actionPropertyTypeReceivedJoinCond))
        actionPropertyReceivedJoinCond = [tableReceivedActionProperty['type_id'].eq(tableReceivedActionPropertyType['id']),
                                        tableReceivedActionProperty['action_id'].eq(tableReceivedAction['id'])]
        queryTable = queryTable.leftJoin(tableReceivedActionProperty,
                                         actionPropertyReceivedJoinCond)
        queryTable = queryTable.leftJoin(tableReceivedActionPropertyOrgStructure,
                                         tableReceivedActionPropertyOrgStructure['id'].eq(tableReceivedActionProperty['id']))
        queryTable = queryTable.leftJoin(tableReceivedOrgStructure,
                                         tableReceivedOrgStructure['id'].eq(tableReceivedActionPropertyOrgStructure['value']))

    #    if (chkQuotaClass and (not quotaClass is None)) or quotaTypeId:
        ## Квота пациента
        queryTable = queryTable.innerJoin(tableQuotaActionType, tableQuotaActionType['id'].eq(tableActionMovingStaying['actionType_id']))
        queryTable = queryTable.leftJoin(tableQuotaAction, [tableQuotaAction['actionType_id'].eq(tableQuotaActionType['id']),
                                                            tableQuotaAction['event_id'].eq(tableEvent['id']),
                                                            tableQuotaAction['deleted'].eq(0)
                                                           ])
        actionPropertyTypeQuotaJoinCond = [tableQuotaActionPropertyType['actionType_id'].eq(tableQuotaActionType['id']),
                                           tableQuotaActionPropertyType['name'].eq(u'Квота')]
        queryTable = queryTable.innerJoin(tableQuotaActionPropertyType, db.joinAnd(actionPropertyTypeQuotaJoinCond))

        actionPropertyQuotaJoinCond = [tableQuotaActionProperty['type_id'].eq(tableQuotaActionPropertyType['id']),
                                       tableQuotaActionProperty['action_id'].eq(tableActionMovingStaying['id'])]
        queryTable = queryTable.leftJoin(tableQuotaActionProperty, actionPropertyQuotaJoinCond)
        queryTable = queryTable.leftJoin(tableActionPropertyClientQuoting, tableActionPropertyClientQuoting['id'].eq(tableQuotaActionProperty['id']))
        queryTable = queryTable.leftJoin(tableClientQuoting, tableClientQuoting['id'].eq(tableActionPropertyClientQuoting['value']))
        queryTable = queryTable.leftJoin(tableQuotaType, tableQuotaType['id'].eq(tableClientQuoting['quotaType_id']))
        
        tmpCond = [tableReceivedAction['endDate'].dateGe(begDate),
                   tableReceivedAction['endDate'].dateLe(endDate), 
                   tableMovingOrgStructure['id'].isNull()]
        recievedCond = db.joinAnd(tmpCond)

        tmpCond = [tableActionMovingStaying['endDate'].dateLe(endDate),
                   tableActionMovingStaying['endDate'].dateGe(begDate), 
                   tableMovingOrgStructure['id'].isNull()
                   ]
        leavedCond   = db.joinAnd(tmpCond)

        tmpCond = [tableReceivedAction['endDate'].dateLt(begDate),
                   db.joinOr([tableActionMovingStaying['endDate'].dateGe(begDate),
                              tableActionMovingStaying['endDate'].isNull()]), 
                    tableMovingOrgStructure['id'].isNull()]
        existsBottomCond = db.joinAnd(tmpCond)

        tmpCond = [tableReceivedAction['endDate'].dateLe(endDate),
                   db.joinOr([tableActionMovingStaying['endDate'].dateGt(endDate),
                              tableActionMovingStaying['endDate'].isNull()]), 
                    tableMovingOrgStructure['id'].isNull()]        
        existsTopCond = db.joinAnd(tmpCond)

        cond = [
                db.joinOr([existsBottomCond, recievedCond, leavedCond, existsTopCond]),
                tableEvent['deleted'].eq(0),
                tableActionMovingStaying['deleted'].eq(0),
                tableReceivedAction['deleted'].eq(0),
                tableReceivedAction['endDate'].isNotNull()
               ]

        if (chkQuotaClass and quotaClass is not None) or quotaTypeId:
            cond.append(tableActionMovingStaying['id'].eq(tableQuotaAction['id']))
        if contractId:
            cond.append(tableContract['id'].eq(contractId))

        if chkQuotaClass and (not quotaClass is None):
            cond.append(tableQuotaType['class'].eq(quotaClass))

        if quotaTypeId:
            quotaTypeIdList = getChildrenIdList([quotaTypeId])
            cond.append(tableQuotaType['id'].inlist(quotaTypeIdList))

        fields = [tableReceivedAction['endDate'].alias('movingActionBegDate'),
                  tableActionMovingStaying['endDate'].alias('movingActionEndDate'),
                  tableMovingOrgStructure['id'].alias('movingOrgStructureId'),
                  tableMovingStayingOrgStructure['id'].alias('stayingOrgStructureId'),
                  tableMovingStayingOrgStructure['code'].alias('stayingOrgStructureCode'),
                  tableEvent['id'].alias('eventId'), 
                  tableQuotaType['class'].alias('quotaClass')
                  ]

        if chkDetailClients:
            fields.extend([tableClient['id'].alias('clientId'),
                           tableClient['lastName'].alias('clientLastName'),
                           tableClient['firstName'].alias('clientFirstName'),
                           tableClient['patrName'].alias('clientPatrName'),
                           #tableFinance['name'].alias('financeTypeName'),
                           'CONCAT_WS(\' \',grouping, number, DATE_FORMAT(date,\'%d:%m:%Y`\'), resolution) AS contractInfo',
                           tableQuotaType['class'].alias('quotaTypeClass'),
                           tableQuotaType['code'].alias('quotaTypeCode'),
                           tableClientQuoting['status'].alias('quotaStatus'),
                           tableClientQuoting['id'].alias('clientQuotingId'),
                           tableActionMovingStaying['id'].alias('actionMovingStayingId')])

        if QtGui.qApp.defaultHospitalBedFinanceByMoving() == 2:
            tableRBFinanceBC = db.table('rbFinance').alias('rbFinanceByContract')
            fields.append(u'IF(ActionMovingStaying.finance_id IS NOT NULL AND ActionMovingStaying.deleted=0, rbFinance.name, IF(Contract.id IS NOT NULL AND Contract.deleted=0, rbFinanceByContract.name, NULL)) AS financeType')
            if financeId:
                cond.append('''((ActionMovingStaying.finance_id IS NOT NULL AND ActionMovingStaying.deleted=0 AND ActionMovingStaying.finance_id = %s) OR (Contract.id IS NOT NULL AND Contract.deleted=0 AND Contract.finance_id = %s))'''%(str(financeId), str(financeId)))
                queryTable = queryTable.innerJoin(tableFinance, tableFinance['id'].eq(tableActionMovingStaying['finance_id']))
                queryTable = queryTable.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.innerJoin(tableRBFinanceBC, tableRBFinanceBC['id'].eq(tableContract['finance_id']))
            else:
                queryTable = queryTable.leftJoin(tableFinance, tableFinance['id'].eq(tableActionMovingStaying['finance_id']))
                queryTable = queryTable.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.leftJoin(tableRBFinanceBC, tableRBFinanceBC['id'].eq(tableContract['finance_id']))
        elif QtGui.qApp.defaultHospitalBedFinanceByMoving() == 1:
            fields.append(tableFinance['name'].alias('financeType'))
            if financeId:
                cond.append('''(ActionMovingStaying.finance_id IS NOT NULL AND ActionMovingStaying.deleted=0 AND ActionMovingStaying.finance_id = %s)'''%(str(financeId)))
                queryTable = queryTable.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.innerJoin(tableFinance, tableFinance['id'].eq(tableActionMovingStaying['finance_id']))
            else:
                queryTable = queryTable.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.leftJoin(tableFinance, tableFinance['id'].eq(tableActionMovingStaying['finance_id']))
        else:
            fields.append(tableFinance['name'].alias('financeType'))
            if financeId:
                queryTable = queryTable.innerJoin( tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.innerJoin( tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
                cond.append(tableContract['deleted'].eq(0))
                cond.append(tableContract['finance_id'].eq(financeId))
            else:
                queryTable = queryTable.leftJoin( tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.leftJoin( tableFinance, tableFinance['id'].eq(tableContract['finance_id']))

        stmt = db.selectStmt(queryTable, fields, cond, group="ActionMovingStaying.`id`")
    else: # chkNurseChief == True
        #atronah: временный костыль, чтоб работало в pesdva и onko
        # EventType.code = '03' - это код типа события "Госпитализация" в НИИ Петрова
        # EventType.code = '05' - это код типа события "ДС Госпитализация" в НИИ Петрова
        query = db.query(u"""SELECT id FROM EventType WHERE EventType.`code` = '03' LIMIT 1""")
        query.next()
        record = query.record()
        eventtypeids[0] = forceRef(record.value('id'))
        query = db.query(u"""SELECT id FROM EventType WHERE EventType.`code` = '05' LIMIT 1""")
        query.next()
        record = query.record()
        eventtypeids[1] = forceRef(record.value('id'))
        eventtypetexts[eventtypeids[0]] = u'КС'
        if eventtypeids[1] is None: 
            eventtypeids[1] = eventtypeids[0]
        else:
            eventtypetexts[eventtypeids[1]] = u'ДС'
        stmt = u"""
            SELECT  Action.id,
                    Event.id as event_id,
                    Event.eventType_id as eventType_id,
                    Event.externalId AS medHistoryNumber,
                    Action.actionType_id,
                    Action.begDate,
                    Action.endDate,
                    OrgStructure.`id` AS `StructId`, 
                    OrgStructure.`code` AS `StructCode`, 
                    OrgStructureMoving.`id` AS `movedStructId`, 
                    OrgStructureMovingFrom.`id` AS `fromStructId`, 
                    QuotaType.`class` AS `quotaClass`, 
                    ActionPropertyLeavedResult.`value` AS `leavedResult`, 
                    %s
                    IF(Action.finance_id IS NOT NULL AND Action.deleted=0, rbFinance.name, 
                        IF(Contract.id IS NOT NULL AND Contract.deleted=0, rbFinanceByContract.name, NULL)) 
                      AS financeType,
                    if((age(Client.birthDate, Event.setDate)>=60 AND Client.sex = 1) OR (age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2), 1, 0) AS pensioner,
                    if(ClientAddress.isVillager =1 OR isClientVillager(Client.id) = 1, 1, 0) AS isVillager,
                    if(LEFT(AddressHouse.KLADRCode,2) != 78 OR rbDocumentType.isForeigner = 1, 1, 0) AS inhab
            FROM            Client
                  LEFT JOIN Event ON (Client.`id`=Event.`client_id`
                                      AND Event.`eventType_id` IN (%s,%s))
                  LEFT JOIN Action ON (Action.`event_id`=Event.`id`) 
                                  AND (Action.`actionType_id` IN (SELECT at.id
                                                                  FROM ActionType at
                                                                  WHERE at.flatCode IN ('received', 'moving', 'leaved') AND at.deleted = 0))
                  LEFT JOIN ActionType ON ActionType.`id`=Action.`actionType_id`  
                  LEFT JOIN ActionPropertyType AS ActionPropertyTypeLeaved ON (ActionPropertyTypeLeaved.`actionType_id`=ActionType.`id`) 
                                                                          AND (ActionPropertyTypeLeaved.`name`='Исход госпитализации')  
                  LEFT JOIN ActionProperty AS ActionPropertyLeaved ON (ActionPropertyLeaved.`type_id`=ActionPropertyTypeLeaved.`id`) 
                                                                  AND (ActionPropertyLeaved.`action_id`=Action.`id`)    
                  LEFT JOIN ActionProperty_String AS ActionPropertyLeavedResult ON ActionPropertyLeavedResult.`id`=ActionPropertyLeaved.`id`  
                  LEFT JOIN ActionPropertyType ON (ActionPropertyType.`actionType_id`=ActionType.`id`) 
                                                   AND (   ActionPropertyType.`name`='Отделение пребывания'
                                                        OR ActionPropertyType.`name`='Отделение'
                                                        OR ActionPropertyType.`name`='Направлен в отделение')
                  LEFT JOIN ActionProperty ON  (ActionProperty.`type_id`=ActionPropertyType.`id`) 
                                                                          AND (ActionProperty.`action_id`=Action.`id`)  
                  LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.`id`=ActionProperty.`id`  
                  LEFT JOIN OrgStructure ON OrgStructure.`id`=ActionProperty_OrgStructure.`value`  
                  LEFT JOIN ActionPropertyType AS ActionPropertyTypeMovingFrom ON (ActionPropertyTypeMovingFrom.`actionType_id`=ActionType.`id`) 
                                                                              AND (ActionPropertyTypeMovingFrom.`name`='Переведен из отделения')  
                  LEFT JOIN ActionProperty AS ActionPropertyMovingFrom ON (ActionPropertyMovingFrom.`type_id`=ActionPropertyTypeMovingFrom.`id`) 
                                                                      AND (ActionPropertyMovingFrom.`action_id`=Action.`id`)  
                  LEFT JOIN ActionProperty_OrgStructure AS ActionPropertyOrgStructureMovingFrom ON ActionPropertyOrgStructureMovingFrom.`id`=ActionPropertyMovingFrom.`id`  
                  LEFT JOIN OrgStructure AS OrgStructureMovingFrom ON OrgStructureMovingFrom.`id`=ActionPropertyOrgStructureMovingFrom.`value`  
                  LEFT JOIN ActionPropertyType AS ActionPropertyTypeMoving ON  (ActionPropertyTypeMoving.`actionType_id`=ActionType.`id`) 
                                                                           AND (ActionPropertyTypeMoving.`name`='Переведен в отделение')  
                  LEFT JOIN ActionProperty AS ActionPropertyMoving ON (ActionPropertyMoving.`type_id`=ActionPropertyTypeMoving.`id`) 
                                                                  AND (ActionPropertyMoving.`action_id`=Action.`id`)  
                  LEFT JOIN ActionProperty_OrgStructure AS ActionPropertyOrgStructureMoving ON ActionPropertyOrgStructureMoving.`id`=ActionPropertyMoving.`id`  
                  LEFT JOIN OrgStructure AS OrgStructureMoving ON OrgStructureMoving.`id`=ActionPropertyOrgStructureMoving.`value`  
                  LEFT JOIN ActionPropertyType AS ActionPropertyTypeQuota ON (ActionPropertyTypeQuota.`actionType_id`=ActionType.`id`) 
                                                                         AND (ActionPropertyTypeQuota.`name`='Квота')  
                  LEFT JOIN ActionProperty AS ActionPropertyQuota ON  (ActionPropertyQuota.`type_id`=ActionPropertyTypeQuota.`id`) 
                                                                  AND (ActionPropertyQuota.`action_id`=Action.`id`)  
                  LEFT JOIN ActionProperty_Client_Quoting ON ActionProperty_Client_Quoting.`id`=ActionPropertyQuota.`id`  
                  LEFT JOIN Client_Quoting ON Client_Quoting.`id`=ActionProperty_Client_Quoting.`value`  
                  LEFT JOIN QuotaType ON QuotaType.`id`=Client_Quoting.`quotaType_id`  
                  LEFT JOIN rbFinance ON rbFinance.`id`=Action.`finance_id`  
                  LEFT JOIN Contract ON Contract.`id`=Event.`contract_id`  
                  LEFT JOIN rbFinance AS rbFinanceByContract ON rbFinanceByContract.`id`=Contract.`finance_id`
                  LEFT JOIN ClientAddress ON ClientAddress.deleted = 0 AND ClientAddress.id = getClientRegAddressId(Event.client_id)
                  LEFT JOIN Address ON Address.deleted = 0 AND Address.id = ClientAddress.address_id
                  LEFT JOIN AddressHouse ON AddressHouse.deleted = 0 AND AddressHouse.id = Address.house_id
                  LEFT JOIN kladr.KLADR kl ON kl.CODE = AddressHouse.KLADRCode
                  LEFT JOIN ClientDocument ON ClientDocument.id = getClientDocumentID(Client.id)
                  LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            WHERE 
                  (
                    (
                      ActionType.flatCode = 'received'
                      AND
                      DATE(Action.`endDate`)<=DATE('%s')
                    )
                    OR
                    DATE(Action.`begDate`)<=DATE('%s')
                  )
                  AND
                  (
                    DATE(Action.`endDate`)>=DATE('%s')
                    OR
                    DATE(Action.`endDate`) IS NULL
                  )
                  AND (Event.`deleted`=0) 
                  AND (Action.`deleted`=0)
            GROUP BY Action.id"""%(
                        params.get('orgStructureId', None) and 
                        """Client.`lastName` AS `clientLastName`, 
                        Client.`firstName` AS `clientFirstName`, 
                        Client.`patrName` AS `clientPatrName`, 
                        """ or "", 
                    eventtypeids[0],
                    eventtypeids[1],  
                    endDate.toString('yyyy-MM-dd'),
                    endDate.toString('yyyy-MM-dd'), 
                    begDate.toString('yyyy-MM-dd')
                )
    return db.query(stmt)



class CAnalyticsReportIncomeAndLeavedClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по поступлению и выписке пациентов')
        #self.resetHelpers()


    def resetHelpers(self):
        self._existEvents = []
        self._orgStructureId = None
        self._orgStructureIdToFullName = {}
        self._mapOrgStructureToClientValues = {}
        self._rowsShift = 0
        self._clientInfo = {}
        self._clientFIO = {'receive':[], 'was':[], 'from':[], 'to':[], 'dead':[], 'leave':[], 'remain':[],}
        self.order = [u'ВМП', u'СМП', u'ОМС', u'ПМУ', u'ДМС', u'ВМП из ОМС', u'ОМС ЛТ', u'АКИ', u'бюджет', u'целевой', u'источник финансирования\nне определён']
        self.items2total = dict(map(lambda a: [(eventtypeids[0], a, self.order[a]), [0]*nurseCols], xrange(8))
                              + map(lambda a: [(eventtypeids[1], a, self.order[a]), [0]*nurseCols], xrange(8)))
        self.boldChars = None


    def getSetupDialog(self, parent):
        result = CStationaryAnalyticsSetupDialog(parent)
        result.setContractWidgetsVisible(True)
        result.setQuotingWidgetsVisible(True)
        result.setDetailClientsVisible(True)
        result.setNurseChiefVisible(False)
        result.chkFinance.setVisible(True)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.resetHelpers()
        self._orgStructureId = params.get('orgStructureId', None)
        chkNurseChief = params.get('chkNurseChief', False)
        finance = params.get('finance', False)
        if chkNurseChief:
            self.makeStructNurse(query, params)
        else:
            self.makeStruct(query, params)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [('%5',
                        [u'№'], CReportBase.AlignRight),
                        ('%25',
                        [u'Подразделение'], CReportBase.AlignLeft),
                        ('%7',
                        [u'Состояло'], CReportBase.AlignLeft),
                        ('%7',
                        [u'Поступило'], CReportBase.AlignLeft),
                        ('%7',
                        [u'Выписано'], CReportBase.AlignLeft),
                        ('%7',
                        [u'Состоит'], CReportBase.AlignLeft)
                        ]

        chkDetailClients = params.get('chkDetailClients', False)
        if chkDetailClients:
            # подразделение будет выводится как заголовок
            del tableColumns[1]

            tableColumns.insert(1, ('%10', [u'Ф.И.О.'], CReportBase.AlignLeft))
            tableColumns.insert(2, ('%10', [u'Тип финансирования'], CReportBase.AlignLeft))
            tableColumns.insert(3, ('%10', [u'Контракт'], CReportBase.AlignLeft))
            tableColumns.insert(4, ('%10', [u'Класс квоты'], CReportBase.AlignLeft))
            tableColumns.insert(5, ('%10', [u'Состояние'], CReportBase.AlignLeft))
            tableColumns.insert(6, ('%10', [u'Вид квоты'], CReportBase.AlignLeft))
        elif chkNurseChief:
            tableColumns = [('%5',
                            [u'', u'', u'', u'', u''], CReportBase.AlignLeft),
                            ('%25',
                            [u'', u'', u'', u'', u''], CReportBase.AlignLeft),
                            ('%10',
                            [u'Движение больных за истекшие сутки', u'Состояло\nбольных на\nначало текущих\nсуток', u'', u'', u'1'], CReportBase.AlignLeft),
                            ('%10',
                            [u'', u'Поступило\nбольных', u'Всего', u'', u'2'], CReportBase.AlignLeft),
                            ('%10',
                            [u'', u'', u'из них', u'старше 60 лет', u'3'], CReportBase.AlignLeft),
                            ('%10',
                            [u'', u'', u'из Иногородних', u'всего', u'4'], CReportBase.AlignLeft),
                            ('%10',
                            [u'', u'', u'', u'житель села', u'5'], CReportBase.AlignLeft),
                            ('%10',
                            [u'',u'Переведено больных\nвнутри больницы', u'из других отделений', u'', u'6'], CReportBase.AlignLeft),
                            ('%10',
                            [u'',u'', u'в другие отделения', u'', u'7'], CReportBase.AlignLeft),
                            ('%10',
                            [u'',u'Выписано больных', u'', u'', u'8'], CReportBase.AlignLeft),
                            ('%10',
                            [u'',u'Умерло', u'', u'', u'9'], CReportBase.AlignLeft),
                            ('%10',
                            [u'Состоит больных\nна начало текущего\nдня', u'', u'', u'', u'10'], CReportBase.AlignLeft)
                           ]
            

        table = createTable(cursor, tableColumns)
        
        if chkNurseChief:
            table.mergeCells(0, 0, 5, 1)
            table.mergeCells(0, 1, 5, 1)
            table.mergeCells(0, 2, 1, 9)
            table.mergeCells(1, 2, 3, 1)
            table.mergeCells(1, 3, 1, 4)
            table.mergeCells(2, 3, 2, 1)
            table.mergeCells(2, 5, 1, 2)
            table.mergeCells(0, 11, 4, 1)
            table.mergeCells(2, 7, 2, 1)
            table.mergeCells(2, 8, 2, 1)
            table.mergeCells(1, 7, 1, 2)
            table.mergeCells(1, 9, 3, 1)
            table.mergeCells(1, 10, 3, 1)

        self.boldChars = QtGui.QTextCharFormat()
        self.boldChars.setFontWeight(QtGui.QFont.Bold)
        
        vK = nurseCols if chkNurseChief else 4
        result = [0]*vK
        keys = self._mapOrgStructureToClientValues.keys()
        if chkNurseChief: # если для старших сестёр
            keys.sort(key=lambda item: [item[1], item[3], item[4]])
            curStruct = 0 # инициализирует текущий идентификатор структуры в 0
            curETid = 0
            curETrow = 0
            ETreq = True
            structResult = [0]*vK # инициализируем "итого" структур нулями
            for key in keys: # для каждого из доступных вариантов пар структур / источников финансирования
                if key[2] != curStruct or key[3] != curETid: # если новая структура
                    if curStruct: # и она не первая
                        if not finance:
                            i = table.addRow()
                        table.mergeCells(curETrow+1, 0, i-curETrow, 1)
                        if not finance:
                            table.setText(i, 1, u'Итого', charFormat=self.boldChars if not finance else None)
                        self.printResult(i, structResult, table, chkDetailClients, False, nurseShift=True, finance=True) # выдаём строку с "итого" для структуры
                        structResult = [0]*vK # и закрываем её
                    if key[2] != curStruct:
                        curStruct = key[2] # назначаем новую структуру
                        i = table.addRow()
                        table.setText(i, 0, curStruct, charFormat=self.boldChars) # пишем подзаголовок - название структуры
                        if not finance:
                            table.mergeCells(i, 0, 1, vK+2)
                    curETid = key[3]
                    curETrow = i
                    # if finance:
                    #     i = table.addRow()
                    ETreq = True
                if finance:
                    subResult = self.countValues(key, self._mapOrgStructureToClientValues, vK=vK) #считаем результаты по одному варианту
                else:
                    subResult = self.printValues(key, self._mapOrgStructureToClientValues, table, vK=vK,  nK=5 if finance else -1,  nums=False, nurseShift=True) # получаем результат по одному варианту
                if ETreq and not finance:
                    table.setText(table.table.rows()-1, 1 if finance else 0, eventtypetexts[key[3]])
                    ETreq = False
                self.items2total[key[3:]] = map(lambda a, b: a+b, self.items2total[key[3:]], self._mapOrgStructureToClientValues[key])
                structResult = map(lambda x, y: x+y, subResult, structResult) # наращиваем "итого" текущей структуры
                result = map(lambda x, y: x+y, subResult, result) # наращиваем общее "итого"
            if not finance:
                i = table.addRow()
                table.mergeCells(curETrow+1, 0, i-curETrow, 1)
            if not self._orgStructureId and not finance:
                table.setText(i, 1, u'Итого', charFormat=self.boldChars if not finance else None)
                self.printResult(i, structResult, table, chkDetailClients, False, nurseShift=True, finance=True) # выдаём строку с "итого" для структуры
                i = table.addRow()
                table.setText(i, 0, u'ИТОГОВОЕ ИТОГО', charFormat=self.boldChars)
                table.mergeCells(i, 0, 1, vK+2)
                keys = self.items2total.keys()
                keys.sort()
                curETid = keys[0][0]
                curETrow = i
                ETreq = True
                structResult = [0]*vK
                i = table.addRow()
                for key in keys:
                    if key[0] != curETid:
                        ETreq = True
                        table.mergeCells(curETrow+1, 0, i-curETrow-1, 1)
                        if finance:
                            table.setText(i, 0, eventtypetexts[curETid])
                            table.setText(i, 1, u'Итого')
                            self.printResult(i, structResult, table, chkDetailClients, False, nurseShift=True, finance=True)
                        structResult = [0]*vK
                        curETid = key[0]
                        curETrow = i
                    if ETreq and not finance:
                        table.setText(i, 0, eventtypetexts[key[0]])
                        ETreq = False
                    if finance:
                        subResult = self.countValues(key, self.items2total, vK=vK)
                        structResult = map(lambda x, y: x+y, subResult, structResult)
                    else:
                        table.setText(i, 1, key[2], charFormat=self.boldChars)
                        self.printResult(i, self.items2total[key], table, chkDetailClients,  False, nurseShift=True)
                        table.mergeCells(curETrow, 0, i-curETrow+1, 1)
                        i = table.addRow()
                # if finance:
                #     i = table.addRow()
                #     table.setText(i, 0, eventtypetexts[curETid])
                #     table.setText(i, 1, u'Итого')
                #     self.printResult(i, structResult, table, chkDetailClients, False, nurseShift=True, finance=True)
                #     i = table.addRow()
            if finance:
                i = table.addRow()
            table.setText(i, 0, u'Итоговое итого', charFormat=self.boldChars)
            table.mergeCells(i, 0, 1, 2)
            self.printResult(i, result, table, chkDetailClients,  False, nurseShift=True)
            cursor.movePosition(cursor.End, 0)
            cursor.insertBlock()
            cursor.insertText(u'\n\n\n\t\tДежурная медсестра:______________\n\n')
            if self._orgStructureId:
                cursor.insertBlock()
                for v in self._clientFIO.values(): v.sort()
                lens = [0, len(self._clientFIO['receive']), len(self._clientFIO['leave']), len(self._clientFIO['dead']), 
                            len(self._clientFIO['to']), len(self._clientFIO['from']), #len(self._clientFIO['was']), len(self._clientFIO['remain']), 
                            ]
                lens[0] = max(lens)+1
                tableColumns = [('var',[u'№'], CReportBase.AlignLeft),
                                             ('var',[u'Поступило:'], CReportBase.AlignLeft),
                                             ('var',[u'Выписано:'], CReportBase.AlignLeft)]
                n = {'to':3 + (lens[3] > 0), 'from':3 + (lens[3] > 0) + (lens[4] > 0), 
                                             #'was':3 + (lens[3] > 0) + (lens[4] > 0) + (lens[5] > 0),
                                             #'remain':3 + (lens[3] > 0) + (lens[4] > 0) + (lens[5] > 0) + (lens[6] > 0),
                                              }
                if lens[3]: tableColumns.append(  ('var',[u'Умерло:'], CReportBase.AlignLeft) )
                if lens[4]: tableColumns.append(  ('var',[u'Переведено в другие отд.:'], CReportBase.AlignLeft) )
                if lens[5]: tableColumns.append(  ('var',[u'Переведено из других отд.:'], CReportBase.AlignLeft) )
                #if lens[6]: tableColumns.append(  ('var',[u'Состояло:'], CReportBase.AlignLeft) )
                #if lens[7]: tableColumns.append(  ('var',[u'Состоит:'], CReportBase.AlignLeft) )
                table = createTable(cursor, 
                                            tableColumns, 
                                            border=0)
                for i in xrange(1, lens[0]):
                    table.addRow()
                    table.setText(i, 0, i, charFormat=None)
                    if lens[1] >= i:
                        table.setText(i, 1, self._clientFIO['receive'][i-1], charFormat=None)
                    if lens[2] >= i:
                        table.setText(i, 2, self._clientFIO['leave'][i-1], charFormat=None)
                    if lens[3] >= i:
                        table.setText(i, 3, self._clientFIO['dead'][i-1], charFormat=None)
                    if lens[4] >= i:
                        table.setText(i, n['to'], self._clientFIO['to'][i-1], charFormat=None)
                    if lens[5] >= i:
                        table.setText(i, n['from'], self._clientFIO['from'][i-1], charFormat=None)
                    #if lens[6] >= i:
                    #    table.setText(i, n['was'], self._clientFIO['was'][i-1], charFormat=None)
                    #if lens[7] >= i:
                    #    table.setText(i, n['remain'], self._clientFIO['remain'][i-1], charFormat=None)
            
        else: # не для старших сестёр
            keys.sort(key=lambda item: item[1])
            for key in keys:
                subResult = self.printValues(key, self._mapOrgStructureToClientValues, table, vK=vK,  nK=1)
                result = map(lambda x, y: x+y, subResult, result)
            i = table.addRow()
            table.setText(i, 1, u'Итого', charFormat=self.boldChars)
            self.printResult(i, result, table, chkDetailClients)
        return doc

    def printValues(self, key, valuesDict, table, depth=0, vK=4,  nK=1,  nums=True, nurseShift=False):
        values = valuesDict.get(key, None)
        nameKey = key[nK]
        i = table.addRow()
        charFormat = None# if depth else self.boldChars
        if isinstance(values, list):
            if nums:
                table.setText(i, 0, i-self._rowsShift)
            table.setText(i, nums+nurseShift, nameKey, charFormat=charFormat)
            if nameKey == u'Ревина Валентина Павловна':
                pass
            subResult = [0]*vK
            if depth:
                columnShift = 7
                clientValues = self._clientInfo.get(key, [])
                for idx, value in enumerate(clientValues):
                    table.setText(i, idx+1+nums, value)
            else:
                columnShift = 1+nums+nurseShift
            for idx, value in enumerate(values):
                table.setText(i, idx+columnShift, value)
                subResult[idx] += value
            return subResult

        elif isinstance(values, dict):
            self._rowsShift += 1
            table.setText(i, 1, nameKey, charFormat=charFormat)
            result = [0]*vK
            table.mergeCells(i, 0, 1, 6)
            subKeys = values.keys()
            subKeys.sort(key=lambda item: item[1])
            for subKey in subKeys:
                subResult = self.printValues(subKey, values, table, depth+1, vK=vK)
                result = map(lambda x, y: x+y, subResult, result)
            self.printResult(i, result, table)
            return result

    def countValues(self, key, valuesDict, vK=4):
        values = valuesDict.get(key, None)
        subResult = [0]*vK
        for idx, value in enumerate(values):
                subResult[idx] += value
        return subResult

    def printResult(self, row, values, table, chkDetailClients=True,  nums=True, nurseShift=False, finance=False):
        columnShift = 7 if chkDetailClients else 1+nums
        table.mergeCells(row, nurseShift, 1, columnShift)
        for idx, value in enumerate(values):
            table.setText(row, idx+columnShift+nurseShift, value, charFormat=self.boldChars if not finance else None)

    def makeStructNurse(self, query, params):
        orgStructureId   = params.get('orgStructureId', None)
        hosps = {}
        structs = []
        structs_ds = []
        if not orgStructureId:
            query2 = QtGui.qApp.db.query(u"SELECT id,code,hasDayStationary AS hasDS FROM OrgStructure WHERE parent_id IN (SELECT id FROM OrgStructure WHERE code = '01 Клинические подразделения') AND hasHospitalBeds = 1")
            while query2.next():
                record = query2.record()
                id = forceRef(record.value('id'))
                fullOrgStructureName = getOrgStructureFullName(id)
                self._orgStructureIdToFullName[id] = fullOrgStructureName
                structs.append( (id, fullOrgStructureName, forceString(record.value('code'))) )
                if forceInt(record.value('hasDS')):
                    structs_ds.append( (id, fullOrgStructureName, forceString(record.value('code'))) )
        else:
            query2 = QtGui.qApp.db.query(u"SELECT code,hasDayStationary AS hasDS FROM OrgStructure WHERE id = %s"%orgStructureId)
            query2.next()
            record = query2.record()
            fullOrgStructureName = getOrgStructureFullName(orgStructureId)
            self._orgStructureIdToFullName[orgStructureId] = fullOrgStructureName
            structs.append( (orgStructureId, fullOrgStructureName, forceString(record.value('code'))) )
            if forceInt(record.value('hasDS')):
                structs_ds.append( (orgStructureId, fullOrgStructureName, forceString(record.value('code'))) )
        for struct in structs:
            for ft in xrange(8): # ВМП, СМП, ОМС, ПМУ, ДМС, ОМС ЛТ, АКИ
               self._mapOrgStructureToClientValues.setdefault(struct+(eventtypeids[0], ft, self.order[ft]), [0,]*nurseCols) 
        for struct in structs_ds:
            for ft in xrange(8): # ВМП, СМП, ОМС, ПМУ, ДМС, ОМС ЛТ, АКИ
               self._mapOrgStructureToClientValues.setdefault(struct+(eventtypeids[1], ft, self.order[ft]), [0,]*nurseCols) 

        quotaClassMap = {0: u'ВМП', 1: u'СМП', 2: u'Родовой сертификат', 3: u'Платные', 4: u'ОМС', 5: u'ВМП из ОМС', 6: u'ВМП сверх базового', 7: u'АКИ'}
        while query.next():
            record = query.record()
            curH = forceString(record.value('event_id'))
            eventType_id = forceRef(record.value('eventType_id'))
            actionType_id = forceRef(record.value('actionType_id'))
            actionType = {8920:'leave', 8921:'moving', 8922:'receive'}[actionType_id]
            actionBeg = forceDate(record.value('begDate'))
            actionEnd = forceDate(record.value('endDate'))
            if not hosps.has_key(curH): # если действие из этой госпитализации не встречалось
                hosps[curH] = {'receive':{}, 'eventType_id':eventType_id, 'moving':[], 'leave':{}, 'rez':{'receive':0, 'pensioner':0, 'inhab':0, 'isVillager':0, 'was':0, 'from':0, 'to':0, 'dead':0, 'leave':0, 'remain':0}}
                hosps[curH]['medHistoryNumber'] = forceString(record.value('medHistoryNumber'))
                if orgStructureId:
                    hosps[curH]['firstName'] = forceString(record.value('clientFirstName'))
                    hosps[curH]['lastName'] = forceString(record.value('clientLastName'))
                    hosps[curH]['patrName'] = forceString(record.value('clientPatrName'))
            financeType = forceString(record.value('financeType'))
            if not financeType: financeType = u'источник финансирования\nне определён'
            if financeType == u'целевой':
                quotaClass = record.value('quotaClass')
                if not quotaClass.isNull():
                    quotaClass = forceInt(quotaClass)
                    financeType = quotaClassMap.get(quotaClass, financeType)

            if actionType == 'receive':
                curA = hosps[curH][actionType]
            elif actionType == 'leave':
                curA = hosps[curH][actionType]
                hosps[curH][actionType]['result'] = forceString(record.value('leavedResult'))
            else: # actionType == 'moving'
                hosps[curH][actionType].append({})
                curA = hosps[curH][actionType][-1]
                hosps[curH][actionType][-1]['from'] = forceRef(record.value('fromStructId'))
                hosps[curH][actionType][-1]['to'] = forceRef(record.value('movedStructId'))
            curA['begDate'] = actionBeg
            curA['endDate'] = actionEnd
            curA['financeType'] = financeType
            curA['struct'] = forceRef(record.value('StructId'))
            curA['structCode'] = forceString(record.value('StructCode'))
            curA['type'] = actionType
            curA['pensioner'] = forceInt(record.value('pensioner'))
            curA['inhab'] = forceInt(record.value('inhab'))
            curA['isVillager'] = forceInt(record.value('isVillager'))
        for curH in hosps.values():
            curH['moving'].sort(key=lambda a: a['begDate'])
            newBeg = None
            newFrom = None
            if curH['moving']:
                todel = []
                for i in xrange(len(curH['moving'])):
                    if curH['moving'][i]['from'] == curH['moving'][i]['struct']:
                        if newFrom:
                            curH['moving'][i]['from'] = newFrom
                            newFrom = None
                        else:
                            curH['moving'][i]['from'] = None
                        if newBeg:
                            curH['moving'][i]['begDate'] = newBeg
                            newBeg = None
                    if curH['moving'][i]['to'] == curH['moving'][i]['struct']:
                        if i != len(curH['moving']) - 1:
                            newBeg = curH['moving'][i]['begDate']
                            if curH['moving'][i]['from'] and curH['moving'][i]['from'] != curH['moving'][i]['struct']:
                                newFrom = curH['moving'][i]['from']
                            todel.append(i)
                        else:
                            curH['moving'][i]['to'] = None
                todel.sort(reverse=True)
                for i in todel:
                    del curH['moving'][i]
            ###
            worklist = []
            if curH['receive']: worklist.append(curH['receive'])
            if curH['leave']: worklist.append(curH['leave'])
            if curH['moving']: worklist += curH['moving']
            for curA in worklist:
                self.mapValuesNurseChiefPrepare(params, curH, curA, curH['eventType_id'])
            if self._orgStructureId:
                clientName = "%s (%s)"%(formatShortNameInt(curH['lastName'],
                                                            curH['firstName'],
                                                            curH['patrName']), 
                                        curH['medHistoryNumber'])
                sum = 0
                for key in curH['rez'].keys():
                    sum += curH['rez'][key]
                    for i in xrange(curH['rez'][key]):
                        if self._clientFIO.has_key(key):
                            self._clientFIO[key].append(clientName)
                        else:
                            self._clientFIO[key] = [clientName]


    def mapValuesNurseChiefPrepare(self, params, curH, curA, eventType_id):
        orgStructureId   = params.get('orgStructureId', None)
        # Если не выбрано отд. или выбрано и оно равно "отд. пребывания"
        if not orgStructureId or curA['struct'] == orgStructureId:
            fullOrgStructureName = self._orgStructureIdToFullName.get(curA['struct'], None)
            if not fullOrgStructureName:
                if not curA['struct']:
                    fullOrgStructureName = u'Подразделение не определено'
                else:
                    fullOrgStructureName = getOrgStructureFullName(curA['struct'])
                self._orgStructureIdToFullName[curA['struct']] = fullOrgStructureName
            key = (curA['struct'], fullOrgStructureName, curA['structCode'], eventType_id, self.order.index(curA['financeType']),   curA['financeType'])
            self.items2total.setdefault(key[3:], [0,]*nurseCols)
            self.mapValuesNurseChief(params, self._mapOrgStructureToClientValues.setdefault(key, [0,]*nurseCols), curH, curA)
        
        
    def mapValuesNurseChief(self, params, values, curH, curA):
        orgStructureId = params.get('orgStructureId', None)
        begDate = params.get('begDate', QtCore.QDate.currentDate())
        endDate = params.get('endDate', QtCore.QDate.currentDate())
        if curA['type'] == 'receive':
            values[1] += 1 # поступило
            values[2] += curA['pensioner']
            values[3] += curA['inhab']
            values[4] += curA['isVillager']
            curH['rez']['receive'] = 1
            curH['rez']['pensioner'] += curA['pensioner']
            curH['rez']['inhab'] += curA['inhab']
            curH['rez']['isVillager']+= curA['isVillager']
            if not curH['moving'] and not curH['leave']:
                values[9] += 1 # осталось
                curH['rez']['remain'] = 1
        elif curA['type'] == 'leave':
            if curA['result'].lower() == u'умер':
                values[8] += 1 # умер
                curH['rez']['dead'] = 1
            else:
                values[7] += 1 # выписано
                curH['rez']['leave'] = 1
        else:
            if curA['from']:
                if begDate <= curA['begDate'] and curA['begDate'] <= endDate:
                    values[5] += 1 # переведен из других отделений
                    curH['rez']['from'] += 1
            if not (curH['rez']['receive'] or curH['rez']['from']): # and not curH['rez']['was']:
                values[0] += 1 # состояло
                curH['rez']['was'] = 1
            if curA['to']:
                if begDate <= curA['endDate'] and curA['endDate'] <= endDate:
                    values[6] += 1 # переведен в другое отделение
                    curH['rez']['to'] += 1
            if not (curH['rez']['leave'] or curH['rez']['dead'] or curH['rez']['to'] > curH['rez']['from']):
                values[9] += 1 # осталось
                curH['rez']['remain'] = 1

    def makeStruct(self, query, params):
        begDate          = params.get('begDate', QtCore.QDate.currentDate())
        endDate          = params.get('endDate', QtCore.QDate.currentDate())
        chkDetailClients = params.get('chkDetailClients', False)
        #orgStructureId   = params.get('orgStructureId', None)
        while query.next():
            record = query.record()

            stayingOrgStructureId   = forceRef(record.value('stayingOrgStructureId'))
            stayingOrgStructureCode = forceString(record.value('stayingOrgStructureCode'))
            actionMovingStayingId   = forceRef(record.value('actionMovingStayingId'))
            if chkDetailClients:
                clientId = forceRef(record.value('clientId'))
                clientName = formatName(record.value('clientLastName'),
                                        record.value('clientFirstName'),
                                        record.value('clientPatrName'))

            fullOrgStructureName = self._orgStructureIdToFullName.get(stayingOrgStructureId, None)
            if not fullOrgStructureName:
                if not stayingOrgStructureId:
                    fullOrgStructureName = u'Подразделение не определено'
                else:
                    fullOrgStructureName = getOrgStructureFullName(stayingOrgStructureId)
                self._orgStructureIdToFullName[stayingOrgStructureId] = fullOrgStructureName
                    
            key = (stayingOrgStructureId, fullOrgStructureName, stayingOrgStructureCode)
            if chkDetailClients:
                clientDict = self._mapOrgStructureToClientValues.setdefault(key, {})
                clientKey = (clientId, clientName, actionMovingStayingId)
                self.makeClientInfo(clientKey, record)
                self.mapValues(clientDict, clientKey, record, begDate, endDate)
            else:
                self.mapValues(self._mapOrgStructureToClientValues, key, record, begDate, endDate)                

    def mapValues(self, valuesDict, key, record, begDate, endDate):
        movingActionBegDate     = forceDate(record.value('movingActionBegDate'))
        movingActionEndDate     = forceDate(record.value('movingActionEndDate'))
        movingOrgStructureId    = forceRef(record.value('movingOrgStructureId'))

        values = valuesDict.setdefault(key, [0, 0, 0, 0])

        if movingOrgStructureId is None:
            if movingActionBegDate < begDate:
                values[0] += 1 # состояло
            if begDate <= movingActionBegDate and movingActionBegDate <= endDate:
                values[1] += 1 # поступило
            if begDate <= movingActionEndDate and movingActionEndDate <= endDate:
                values[2] += 1 # выписано
            if movingActionBegDate <= endDate and (endDate < movingActionEndDate or not movingActionEndDate.isValid()):
                values[3] += 1 # осталось

    def makeClientInfo(self, key, record):
        if not key in self._clientInfo.keys():

            financeTypeName = forceString(record.value('financeTypeName'))
            contractInfo = forceString(record.value('contractInfo'))
            if forceRef(record.value('clientQuotingId')):
                quotaTypeClass = getQuotaTypeClassNameList()[forceInt(record.value('quotaTypeClass'))]
                quotaStatus = [u'Отменено',
                               u'Ожидание',
                               u'Активный талон',
                               u'Талон для заполнения',
                               u'Заблокированный талон',
                               u'Отказано',
                               u'Необходимо согласовать дату обслуживания',
                               u'Дата обслуживания на согласовании',
                               u'Дата обслуживания согласована',
                               u'Пролечен',
                               u'Обслуживание отложено',
                               u'Отказ пациента',
                               u'Импортировано из ВТМП'][forceInt(record.value('quotaStatus'))]
                quotaTypeCode = forceString(record.value('quotaTypeCode'))
            else:
                quotaTypeClass = u''
                quotaStatus    = u''
                quotaTypeCode  = u''

            self._clientInfo[key] = [financeTypeName, contractInfo, quotaTypeClass, quotaStatus, quotaTypeCode]


    def getDescription(self, params):
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        financeId = params.get('financeId', None)
        financeText = params.get('financeText', None)
        contractId = params.get('contractId', None)
        contractText = params.get('contractText', None)
        chkQuotaClass = params.get('chkQuotaClass', False)
        quotaClass = params.get('quotaClass', None) if chkQuotaClass else None
        quotaTypeId = params.get('quotaTypeId', False)
        chkNurseChief    = params.get('chkNurseChief', False)
        orgStructureId   = params.get('orgStructureId', None)
        
        rows = []
        if chkNurseChief and orgStructureId:
            rows.append(u'Ведомость движения больных по %s' % getOrgStructureName(orgStructureId))
        if financeId:
            rows.append(u'Тип финансирования: %s' % financeText)
        if contractId:
            rows.append(u'Контракт: %s' % contractText)
        if chkNurseChief:
            rows.append(u'Текущий день: %s'%forceString(QtCore.QDate.currentDate()))
            if begDate:
                if endDate and endDate != begDate:
                    rows.append(u'Отчет составлен за период: %s - %s'%(forceString(begDate), forceString(endDate)))
                else:
                    rows.append(u'Отчет составлен за: %s'%forceString(begDate))
        else:
            if begDate:
                rows.append(u'Начальная дата периода: %s'%forceString(begDate))
            if endDate:
                rows.append(u'Конечная дата периода: %s'%forceString(endDate))
        if not quotaClass is None:
            rows.append(u'Класс квоты: %s'%[u'ВТМП', u'СМП', u'Родовой сертификат', u'Платные', u'ОМС', u'ВМП из ОМС', u'ВМП сверх базового', u'АКИ'][quotaClass])
        if quotaTypeId:
            rows.append(u'Тип квоты: %s'%forceString(QtGui.qApp.db.translate('QuotaType', 'id',
                                                                            quotaTypeId, 'CONCAT_WS(\' | \', code, name)')))
        return rows

