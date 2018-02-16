# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils               import getActionTypeDescendants
from library.database           import addDateInRange
from library.Utils              import forceDouble, forceInt, forceRef, forceString, getVal, formatName
from Orgs.Utils                 import getOrgStructureFullName

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog
from Reports.StatReport1NPUtil  import havePermanentAttach


def selectData(begDate, endDate, eventTypeId, sex, ageFrom, ageTo, actionTypeClass, actionTypeId, onlyPermanentAttach, MKBFilter, MKBFrom, MKBTo, onlyPayedEvents, begPayDate, endPayDate, detailPerson, personId, specialityId, orgStructureId, insurerId):

    db = QtGui.qApp.db

    tableEvent              = db.table('Event')
    tableClient             = db.table('Client')
    tableAction             = db.table('Action')
    tableActionType         = db.table('ActionType')
    tableActionTypeService  = db.table('ActionType_Service')
    tableService            = db.table('rbService')
    tablePerson             = db.table('Person')
    tableFinance            = db.table('rbFinance')
    tableContract           = db.table('Contract')
    tableContractTariff     = db.table('Contract_Tariff')
    tableOrgStructure       = db.table('OrgStructure')
    tableSpeciality         = db.table('rbSpeciality')
    tableAccountItem        = db.table('Account_Item')


    queryTable = tableEvent.leftJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.leftJoin(tableContract, 'Contract.`id`=IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)')
    queryTable = queryTable.leftJoin(tableContractTariff, tableContractTariff['master_id'].eq(tableContract['id']))

    actionTypeServiceJoinCond = 'IF(ActionType_Service.`finance_id`, ActionType_Service.`finance_id`=Contract.`finance_id`, ActionType_Service.`finance_id` IS NULL)'
    queryTable = queryTable.leftJoin(tableActionTypeService,
                                     [tableActionType['id'].eq(tableActionTypeService['master_id']),
                                      actionTypeServiceJoinCond])
    queryTable = queryTable.leftJoin(tableService, tableService['id'].eq(tableActionTypeService['service_id']))

    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
    queryTable = queryTable.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
    queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))

    accountItemJoinCond = '(Account_Item.action_id = Action.id AND Account_Item.deleted=0 AND Account_Item.date IS NOT NULL AND Account_Item.refuseType_id IS NULL AND Account_Item.reexposeItem_id IS NULL AND Account_Item.visit_id IS NULL)'
    queryTable = queryTable.leftJoin(tableAccountItem, accountItemJoinCond)

    cond = [tableAction['endDate'].isNotNull(),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableContractTariff['service_id'].eq(tableActionTypeService['service_id'])]

    if begDate:
        cond.append(db.joinOr([
                               tableEvent['execDate'].ge(begDate),
                               tableEvent['execDate'].isNull()
                              ]
                             )
                   )
    if endDate:
        cond.append(tableEvent['setDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom:
        cond.append('Event.execDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
    if ageTo:
        cond.append('Event.execDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if actionTypeId:
        cond.append(tableActionType['id'].inlist(getActionTypeDescendants(actionTypeId, actionTypeClass)))
    elif actionTypeClass is not None:
        cond.append(tableActionType['class'].eq(actionTypeClass))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if MKBFilter:
        tableDiagnostic = db.table('Diagnostic')
        tableDiagnosis = db.table('Diagnosis')
        subQueryTable = tableDiagnosis.leftJoin(tableDiagnostic, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
        subCond = [ tableDiagnostic['event_id'].eq(tableEvent['id']),
                    tableDiagnosis['MKB'].between(MKBFrom, MKBTo)
                  ]
        cond.append(db.existsStmt(subQueryTable, subCond))
    if onlyPayedEvents:
#        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    if not detailPerson:
        if personId:
            cond.append(tableAction['person_id'].eq(personId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if orgStructureId:
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
    if insurerId:
        #cond.append('EXISTS (SELECT ClientPolicy.`client_id` FROM ClientPolicy WHERE ClientPolicy.`insurer_id`=%d AND ClientPolicy.`client_id`=Client.`id`)' % insurerId)
        cond.append(tableContract['payer_id'].eq(insurerId))        


    fieldUetDoctor = 'IF(YEAR(FROM_DAYS(DATEDIFF(Action.`endDate`, Client.`birthDate`))) < 18, rbService.`childUetDoctor`, rbService.`adultUetDoctor`) AS uetDoctor'
    fieldUetAverageMedWorker = 'IF(YEAR(FROM_DAYS(DATEDIFF(Action.`endDate`, Client.`birthDate`))) < 18, rbService.`childUetAverageMedWorker`, rbService.`adultUetAverageMedWorker`) AS uetAverageMedWorker'

    fields = [tableAction['id'].alias('actionId'),
              tableAction['person_id'].name(),
              tableAction['finance_id'].name(),
              tableAction['payStatus'].alias('actionPayStatus'),
              tableAction['amount'].alias('actionAmount'),
              tableEvent['payStatus'].alias('eventPayStatus'),
              tablePerson['lastName'].alias('personLastName'),
              tablePerson['firstName'].alias('personFirstName'),
              tablePerson['patrName'].alias('personPatrName'),
              tableSpeciality['name'].alias('specialityName'),
              tableActionType['code'].alias('actionTypeCode'),
              tableActionType['name'].alias('actionTypeName'),
              tableService['code'].alias('serviceCode'),
              tableOrgStructure['id'].alias('orgStructureId'),
              fieldUetDoctor,
              fieldUetAverageMedWorker
              ]


    order = ', '.join([tableAction['id'].name(),
             tableActionTypeService['finance_id'].name()])

    stmt = db.selectStmt(queryTable, fields, cond,  order = order+' DESC', isDistinct = True)
    return db.query(stmt)


def payStatusCheck(payStatus, condFinanceCode):
    if condFinanceCode:
        payCode = (payStatus >> (2*condFinanceCode)) & 3
        if payCode:
            return True
    return False

class CReportActionsServiceCutaway(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по УЕТ')
        self._mapOrgStructureIdOrder = {}

    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setPayPeriodVisible(True)
        result.setWorkOrganisationVisible(True)
        result.setSexVisible(True)
        result.setAgeVisible(True)
        result.setActionTypeVisible(True)
        result.setMKBFilterVisible(True)
        result.setInsurerVisible(True)
        result.setOrgStructureVisible(True)
        result.setSpecialityVisible(True)
        result.setPersonVisible(True)
        result.setFinanceVisible(True)
        result.setTitle(self.title())

        return result



    def build(self, params):
        begDate             = getVal(params, 'begDate', QtCore.QDate())
        endDate             = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId         = getVal(params, 'eventTypeId', None)
        sex                 = params.get('sex', 0)
        ageFrom             = params.get('ageFrom', 0)
        ageTo               = params.get('ageTo', 150)
        actionTypeClass     = params.get('actionTypeClass', None)
        actionTypeId        = params.get('actionTypeId', None)
        onlyPermanentAttach = params.get('onlyPermanentAttach', None)
        MKBFilter           = params.get('MKBFilter', 0)
        MKBFrom             = params.get('MKBFrom', '')
        MKBTo               = params.get('MKBTo', '')
        onlyPayedEvents     = params.get('onlyPayedEvents', False)
        begPayDate          = params.get('begPayDate', QtCore.QDate())
        endPayDate          = params.get('endPayDate', QtCore.QDate())
        detailPerson        = params.get('detailPerson', False)
        personId            = params.get('personId', None)
        specialityId        = params.get('specialityId', None)
        orgStructureId      = params.get('orgStructureId', None)
        insurerId           = params.get('insurerId', None)
        condFinanceId       = params.get('financeId', None)
        condFinanceCode     = params.get('financeCode', '0')

        query = selectData(begDate, endDate, eventTypeId, sex, ageFrom, ageTo, actionTypeClass, actionTypeId, onlyPermanentAttach, MKBFilter, MKBFrom, MKBTo, onlyPayedEvents, begPayDate, endPayDate, detailPerson, personId, specialityId, orgStructureId, insurerId)

        reportData = {}
        mapOrgStructureToFullName = {}
        origActionIdList = []
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            actionId               = forceRef(record.value('actionId'))
            if actionId in origActionIdList:
                continue
            origActionIdList.append(actionId)
            orgStructureId         = forceString(record.value('orgStructureId'))
            financeId              = forceRef(record.value('finance_id'))
            actionPayStatus        = forceInt(record.value('actionPayStatus'))
            eventPayStatus         = forceInt(record.value('eventPayStatus'))
            actionTypeCode         = forceString(record.value('actionTypeCode'))
            actionTypeName         = forceString(record.value('actionTypeName'))
            serviceCode            = forceString(record.value('serviceCode'))
            amount                 = forceInt(record.value('actionAmount'))
            uetDoctor              = forceDouble(record.value('uetDoctor'))
            uetAverageMedWorker    = forceDouble(record.value('uetAverageMedWorker'))
            personName             = formatName(record.value('personLastName'),
                                                record.value('personFirstName'),
                                                record.value('personPatrName'))
            specialityName         = forceString(record.value('specialityName'))

            if condFinanceId:
                if financeId:
                    if condFinanceId != financeId:
                        continue
                else:
                    payStatus = actionPayStatus if actionPayStatus else eventPayStatus
                    if not payStatusCheck(payStatus, forceInt(condFinanceCode)):
                        continue

            if specialityName:
                personName = personName + ' | ' + specialityName

            orgStructureName = mapOrgStructureToFullName.get(orgStructureId, None)
            if not orgStructureName:
                orgStructureName = getOrgStructureFullName(orgStructureId)
                mapOrgStructureToFullName[orgStructureId] = orgStructureName

            if not orgStructureName:
                continue

            existsData = reportData.get(orgStructureName, None)

            if detailPerson:
                if not existsData:
                    existsData = {}
                    personData = {}
                    actionAmount = 1
                    personData[(actionTypeName, actionTypeCode, serviceCode)] =  [actionAmount, amount, amount*uetDoctor, uetAverageMedWorker*amount]
                    existsData[personName] = personData
                    reportData[orgStructureName] = existsData
                else:
                    personData = existsData.get(personName, None)
                    if not personData:
                        personData = {}
                        actionAmount = 1
                        personData[(actionTypeName, actionTypeCode, serviceCode)] =  [actionAmount, amount, amount*uetDoctor, uetAverageMedWorker*amount]
                        existsData[personName] = personData
                    else:
                        existsValue = personData.get((actionTypeName, actionTypeCode, serviceCode), None)
                        if not existsValue:
                            actionAmount = 1
                            personData[(actionTypeName, actionTypeCode, serviceCode)] =  [actionAmount, amount, amount*uetDoctor, uetAverageMedWorker*amount]
                            existsData[personName] = personData
                        else:
                            existsValue[0] += 1
                            existsValue[1] += amount
                            existsValue[2] += uetDoctor*amount
                            existsValue[3] += uetAverageMedWorker*amount
                            personData[(actionTypeName, actionTypeCode, serviceCode)] = existsValue
                            existsData[personName] = personData
                    reportData[orgStructureName] = existsData
            else:
                if not existsData:
                    existsData = {}
                    actionAmount = 1
                    existsData[(actionTypeName, actionTypeCode, serviceCode)] =  [actionAmount, amount, amount*uetDoctor, uetAverageMedWorker*amount]
                    reportData[orgStructureName] = existsData
                else:
                    existsValue = existsData.get((actionTypeName, actionTypeCode, serviceCode), None)
                    if not existsValue:
                        actionAmount = 1
                        existsData[(actionTypeName, actionTypeCode, serviceCode)] = [actionAmount, amount, amount*uetDoctor, amount*uetAverageMedWorker]
                    else:
                        existsValue[0] += 1
                        existsValue[1] += amount
                        existsValue[2] += uetDoctor*amount
                        existsValue[3] += uetAverageMedWorker*amount
                        existsData[(actionTypeName, actionTypeCode, serviceCode)] = existsValue
                    reportData[orgStructureName] = existsData

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '6%', [u'№ п/п'], CReportBase.AlignRight),
            ( '25%', [u'Наименование типа действия'], CReportBase.AlignLeft),
            ( '13%', [u'Код типа действия'], CReportBase.AlignLeft),
            ( '13%', [u'Код профиля'], CReportBase.AlignLeft),
            ( '10%', [u'Количество действий'], CReportBase.AlignRight),
            ( '10%', [u'Количество'], CReportBase.AlignRight),
            ( '10%', [u'УЕТ врача'], CReportBase.AlignRight),
            ( '13%', [u'УЕТ ср.мед.персонала'], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        headerCount = 0
        headerList  = []


        if detailPerson:
            orgStructureList = reportData.keys()
            orgStructureList.sort()
            resume = [0, 0, 0, 0]
            for orgStructure in orgStructureList:
                orgStructureResult = [0, 0, 0, 0]
                i = table.addRow()
                currentOrgStructureRow = i
                table.setText(i, 1, orgStructure)
                headerList.append(i)
                headerCount += 1
                persons = reportData.get(orgStructure, {})
                personsKeys = persons.keys()
                personsKeys.sort()
                for personKey in personsKeys:
                    personResult = [0, 0, 0, 0]
                    i = table.addRow()
                    currentPersonRow = i
                    table.setText(i, 1, personKey)
                    headerList.append(i)
                    headerCount += 1
                    existsData = persons.get(personKey, {})
                    existsDataKeys = existsData.keys()
                    existsDataKeys.sort()
                    for existsDataKey in existsDataKeys:
                        i = table.addRow()
                        table.setText(i, 0, i-headerCount)
                        column = 1
                        for key in existsDataKey:
                            table.setText(i, column, key)
                            column += 1
                        values = existsData.get(existsDataKey)
                        for value in values:
                            orgStructureResult[column-4] += value
                            personResult[column-4] += value
                            resume[column-4] += value
                            table.setText(i, column, value)
                            column += 1
                    for column, val in enumerate(personResult):
                        table.setText(currentPersonRow, column+4, val)
                for column, val in enumerate(orgStructureResult):
                    table.setText(currentOrgStructureRow, column+4, val)
            for headerRow in headerList:
                table.mergeCells(headerRow, 0, 1, 3)
        else:
            orgStructureList = reportData.keys()
            orgStructureList.sort()
            resume = [0, 0, 0, 0]
            for orgStructure in orgStructureList:
                orgStructureResult = [0, 0, 0, 0]
                i = table.addRow()
                currentOrgStructureRow = i
                table.setText(i, 1, orgStructure)
                headerList.append(i)
                headerCount += 1
                existsData = reportData.get(orgStructure, {})
                existsDataKeys = existsData.keys()
                existsDataKeys.sort()
                for existsDataKey in existsDataKeys:
                    i = table.addRow()
                    table.setText(i, 0, i-headerCount)
                    column = 1
                    for key in existsDataKey:
                        table.setText(i, column, key)
                        column += 1
                    values = existsData.get(existsDataKey)
                    for value in values:
                        orgStructureResult[column-4] += value
                        resume[column-4] += value
                        table.setText(i, column, value)
                        column += 1
                for column, val in enumerate(orgStructureResult):
                    table.setText(currentOrgStructureRow, column+4, val)
            for headerRow in headerList:
                table.mergeCells(headerRow, 0, 1, 3)
        i = table.addRow()
        table.setText(i, 1, u'Итого')
        for column, val in enumerate(resume):
            table.setText(i, column+4, val)
        return doc
