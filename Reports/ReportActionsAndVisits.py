# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from operator import add
from PyQt4 import QtCore, QtGui

from Events.Action                          import CActionType
from Orgs.Utils import getOrgStructureDescendants
from RefBooks.Utils import CServiceTypeModel
from library.DialogBase import CDialogBase

from library.Utils                          import forceDouble, forceInt, forceRef, forceString
from library.AgeSelector                    import parseAgeSelector

from Reports.Report                         import CReport
from Reports.ReportBase                     import createTable, CReportBase
from Ui_ReportSetupByActionsAndVisits import Ui_ReportSetupByOrgStructureDialog

def selectDataByActions(params):
    begDate           = params.get('begDate', None)
    endDate           = params.get('endDate', None)
    chkStatus         = params.get('chkStatus', False)
    status            = params.get('status', None)

    eventTypeId = params.get('eventTypeId',  None)

    contractIdList    = params.get('contractIdList', None)
    financeId         = params.get('financeId', None)

    chkClientAgeCategory       = params.get('chkClientAgeCategory', False)
    clientAgeCategory          = params.get('clientAgeCategory', None)
    chkOnlyClientAsPersonInLPU = params.get('chkOnlyClientAsPersonInLPU', False)

    chkOutputByOrgStructure = params.get('chkOutputByOrgStructure',  False)

    showClient = params.get('showClient', False)

    reportType = params.get('reportType', None)
    reportPerson = 'setPerson_id' if reportType == 1 else 'person_id'

    detailServiceTypes = params.get('detailServiceTypes', False)
    serviceTypes = params.get('serviceTypes', None)
    chkOrgStructure = params.get('chkOrgStructure', False)
    orgStructureId = params.get('orgStructureId', None)

    db = QtGui.qApp.db

    tableAction            = db.table('Action')
    tableActionType        = db.table('ActionType')
    tableActionTypeService = db.table('ActionType_Service')
    tableContract          = db.table('Contract')
    tableContractTariff    = db.table('Contract_Tariff')
    tableClient            = db.table('Client')
    tableClientWork        = db.table('ClientWork')
    tableEvent             = db.table('Event')
    tablePerson            = db.table('vrbPersonWithSpeciality')
    tableOrgStructure      = db.table('OrgStructure')

    queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionTypeService, tableActionType['id'].eq(tableActionTypeService['master_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.innerJoin(tableContract, 'Contract.`id`=IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)')
    queryTable = queryTable.innerJoin(tableContractTariff, tableContractTariff['master_id'].eq(tableContract['id']))

    contractTariffCond = 'IF(ActionType_Service.`finance_id`, ActionType_Service.`finance_id`=Contract.`finance_id` AND Contract_Tariff.`service_id`=ActionType_Service.`service_id`, ActionType_Service.`finance_id` IS NULL AND Contract_Tariff.`service_id`=ActionType_Service.`service_id`)'

    cond = [tableAction['begDate'].dateGe(begDate),
            tableAction['begDate'].dateLe(endDate),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            contractTariffCond,
            tableContractTariff['deleted'].eq(0)]
    group = []
    if contractIdList:
        cond.append(tableContract['id'].inlist(contractIdList))
    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))
    if chkStatus and not status is None:
        cond.append(tableAction['status'].eq(status))
    if chkClientAgeCategory and not clientAgeCategory is None:
        ageCond = '< 18' if clientAgeCategory == 0 else '>= 18'
        cond.append('age(Client.`birthDate`,CURRENT_DATE) %s'%ageCond)
    if chkOnlyClientAsPersonInLPU:
        clientWorkJoinCond = [tableClient['id'].eq(tableClientWork['client_id']),
                              'ClientWork.`id`=(SELECT MAX(CW.`id`) FROM ClientWork AS CW WHERE CW.`client_id`=Client.`id`)']
        queryTable = queryTable.innerJoin(tableClientWork, clientWorkJoinCond)
        cond.append(tableClientWork['org_id'].eq(QtGui.qApp.currentOrgId()))

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    if detailServiceTypes and serviceTypes and len(serviceTypes) > 0:
        cond.append(tableActionType['serviceType'].inlist([str(t) for t in serviceTypes]))

    if chkOrgStructure and orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction[reportPerson]))
    order  = []
    fields = [tableAction['endDate'].name(),
              tableActionType['code'].alias('serviceCode'),
              tableActionType['name'].alias('serviceName'),
              tablePerson['id'].alias('personId'),
              tablePerson['name'].alias('personName'),
              tablePerson['speciality_id'],
              tableContractTariff['price'].name(),
              tableClient['lastName'],
              tableClient['firstName'],
              tableClient['patrName']]

    if chkOutputByOrgStructure:
        queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))
        fields.append(tableOrgStructure['name'].alias('orgStructureName'))
        fields.append(tableOrgStructure['id'].alias('orgStructureId'))
        order.append(tableOrgStructure['id'].name())
        if showClient:
            group.append(tableOrgStructure['id'])
    order.append(tablePerson['name'].name())
    if showClient:
        #fields.append(tableAction['amount'].name())
        fields.append('sum(Action.amount) AS amount' )
        group.extend([tablePerson['id'], tableActionType['code'], tableClient['id']])
        order.extend([tableActionType['code'], tableClient['lastName'], tableClient['firstName'], tableClient['patrName']])
    else:
        fields.append(tableAction['amount'].name())
    stmt = db.selectStmt(queryTable, fields, cond, group=group, order = order)

    query = db.query(stmt)
    return query

def selectDataByVisits(params):
    begDate           = params.get('begDate', None)
    endDate           = params.get('endDate', None)
    chkStatus         = params.get('chkStatus', False)
    status            = params.get('status', None)

    eventTypeId = params.get('eventTypeId', None)

    contractIdList    = params.get('contractIdList', None)
    financeId         = params.get('financeId', None)

    chkClientAgeCategory       = params.get('chkClientAgeCategory', False)
    clientAgeCategory          = params.get('clientAgeCategory', None)
    chkOnlyClientAsPersonInLPU = params.get('chkOnlyClientAsPersonInLPU', False)

    chkOutputByOrgStructure = params.get('chkOutputByOrgStructure',  False)
    reportType = params.get('reportType', None)
    reportPerson = 'setPerson_id' if reportType == 1 else 'person_id'

    showClient = params.get('showClient', False)

    detailServiceTypes = params.get('detailServiceTypes', False)
    serviceTypes = params.get('serviceTypes', None)
    chkOrgStructure = params.get('chkOrgStructure', False)
    orgStructureId = params.get('orgStructureId', None)

    db = QtGui.qApp.db

    tableVisit             = db.table('Visit')
    tableService        = db.table('rbService')
    tableEvent          = db.table('Event')
    tableContract          = db.table('Contract')
    tableContractTariff    = db.table('Contract_Tariff')
    tableClient            = db.table('Client')
    tableClientWork        = db.table('ClientWork')
    tablePerson            = db.table('vrbPersonWithSpeciality')
    tableActionType        = db.table('ActionType')
    tableActionTypeService = db.table('ActionType_Service')
    tableOrgStructure      = db.table('OrgStructure')

    queryTable = tableVisit.innerJoin(tableService,  tableService['id'].eq(tableVisit['service_id']))
    queryTable = queryTable.innerJoin(tableEvent,  tableEvent['id'].eq(tableVisit['event_id']))
    queryTable = queryTable.innerJoin(tableContract,  tableContract['id'].eq(tableEvent['contract_id']))
    queryTable = queryTable.innerJoin(tableContractTariff,  db.joinAnd([tableContractTariff['master_id'].eq(tableContract['id']),
                                                                                                                tableContractTariff['service_id'].eq(tableService['id'])]))
    queryTable = queryTable.innerJoin(tablePerson,  tableVisit['person_id'].eq(tablePerson['id']))
    queryTable = queryTable.innerJoin(tableClient,  tableEvent['client_id'].eq(tableClient['id']))
    if detailServiceTypes and serviceTypes and len(serviceTypes) > 0:
        queryTable = queryTable.innerJoin(tableActionTypeService, tableService['id'].eq(tableActionTypeService['service_id']))
        queryTable = queryTable.innerJoin(tableActionType, tableActionTypeService['master_id'].eq(tableActionType['id']))

    #contractTariffCond = 'IF(ActionType_Service.`finance_id`, ActionType_Service.`finance_id`=Contract.`finance_id` AND Contract_Tariff.`service_id`=ActionType_Service.`service_id`, ActionType_Service.`finance_id` IS NULL AND Contract_Tariff.`service_id`=ActionType_Service.`service_id`)'
    contractTariffAgeCond = 'IF(Contract_Tariff.`sex`=0, Contract_Tariff.`sex`=0,Contract_Tariff.`sex`=Client.`sex`)'
    contractTariffDateCond = 'IF(Contract_Tariff.`begDate` IS NULL, Contract_Tariff.`begDate` IS NULL, Visit.`date`>=Contract_Tariff.`begDate` AND Contract_Tariff.`endDate`>=Visit.`date`)'

    cond = [tableVisit['date'].dateGe(begDate),
            tableVisit['date'].dateLe(endDate),
            tableVisit['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableContract['deleted'].eq(0),
            tableContractTariff['deleted'].eq(0),
            contractTariffAgeCond,
            contractTariffDateCond]
    group = []
    if contractIdList:
        cond.append(tableContract['id'].inlist(contractIdList))
    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))
    #if chkStatus and not status is None:
    #    cond.append(tableAction['status'].eq(status))
    if chkClientAgeCategory and not clientAgeCategory is None:
        ageCond = '< 18' if clientAgeCategory == 0 else '>= 18'
        cond.append('age(Client.`birthDate`,CURRENT_DATE) %s'%ageCond)
    if chkOnlyClientAsPersonInLPU:
        clientWorkJoinCond = [tableClient['id'].eq(tableClientWork['client_id']),
                              'ClientWork.`id`=(SELECT MAX(CW.`id`) FROM ClientWork AS CW WHERE CW.`client_id`=Client.`id`)']
        queryTable = queryTable.innerJoin(tableClientWork, clientWorkJoinCond)
        cond.append(tableClientWork['org_id'].eq(QtGui.qApp.currentOrgId()))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    if detailServiceTypes and serviceTypes and len(serviceTypes) > 0:
        cond.append(tableActionType['serviceType'].inlist([str(t) for t in serviceTypes]))
    if chkOrgStructure and orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

    order  = []
    fields = [tableVisit['date'].name(),
              tableService['code'].alias('serviceCode'),
              tableService['name'].alias('serviceName'),
              tablePerson['id'].alias('personId'),
              tablePerson['name'].alias('personName'),
              tablePerson['speciality_id'],
              #tableAction['amount'].name(),
              tableContractTariff['price'].name(),
              tableContractTariff['age'].alias('tariffAge'),
              'age(Client.`birthDate`,Visit.`date`) as clientAge',
              tableClient['lastName'],
              tableClient['firstName'],
              tableClient['patrName']]

    if chkOutputByOrgStructure:
        queryTable = queryTable.leftJoin(tableOrgStructure,  tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))
        fields.append(tableOrgStructure['name'].alias('orgStructureName'))
        fields.append(tableOrgStructure['id'].alias('orgStructureId'))
        order.append(tableOrgStructure['id'].name())
        if showClient:
            group.append(tableOrgStructure['id'])
    order.append(tablePerson['name'].name())
    if showClient:
        fields.append('sum(1) AS amount')
        group.extend([tablePerson['id'], tableService['code'], tableClient['id']])
        order.extend([tableService['code'], tableClient['lastName'], tableClient['firstName'], tableClient['patrName']])
    else:
        fields.append('1 AS amount')
    stmt = db.selectStmt(queryTable, fields, cond, group=group, order = order)

    query = db.query(stmt)
    return query

class CReportActionsAndVisits(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по посещениям и услугам')

    def getSetupDialog(self, parent):
        result = CSetupReport(parent)
        result.setOutputByOrgStructureVisible(True)
        result.setClientAgeCategoryVisible(True)
        result.setOnlyClientAsPersonInLPUVisible(True)
        result.setSetupByOrgStructureOnlyVisible(True)
        result.setSetupByEventTypeVisible(True)
        result.setChkShowClientVisible(True)
        result.setServiceTypesVisible(True)
        result.setStrongOrgStructureVisible(True)
        result.setTitle(self.title())
        return result

    def build(self, params):

        accumSize = 2  # [totalAmount, totalSum]

        def printTotal():
            totalByReport = printOrgStructures(resultDict)
            totalMessage = u'Итог по всем отделениям' if outputByOrgStructure else u'Итог по всем специалистам'
            row = table.addRow()
            table.setText(row, len(tableColumns) - 3, totalMessage, CReport.TableTotal)
            table.setText(row, len(tableColumns) - 2, totalByReport[0], CReport.TableTotal)
            table.setText(row, len(tableColumns) - 1, totalByReport[1], CReport.TableTotal)
            table.mergeCells(row, 0, 1, len(tableColumns) - 2)

        def printOrgStructures(reportData):
            total = [0] * accumSize
            printLeaf = onlyOrgStructures
            printHeadAndTotal = not onlyOrgStructures and outputByOrgStructure
            totalMessage = u'Итог по отделению'

            orgStructures = reportData.keys()
            orgStructures.sort()
            for orgStructure, orgStructureId in orgStructures:
                if printHeadAndTotal:
                    row = table.addRow()
                    table.setText(row, 0, orgStructure, blockFormat=CReportBase.AlignCenter, fontBold=True)
                    table.mergeCells(row, 0, 1, len(tableColumns))

                totalByOrgStructure = printSpecialities(reportData[(orgStructure, orgStructureId)])
                total = map(add, total, totalByOrgStructure)
                if printLeaf:
                    row = table.addRow()
                    table.setText(row, len(tableColumns) - 3, orgStructure)
                    table.setText(row, len(tableColumns) - 2, totalByOrgStructure[0])
                    table.setText(row, len(tableColumns) - 1, totalByOrgStructure[1])
                    table.mergeCells(row, 0, 1, len(tableColumns) - 2)

                if printHeadAndTotal:
                    row = table.addRow()
                    table.setText(row, len(tableColumns) - 3, totalMessage, fontBold=True)
                    table.setText(row, len(tableColumns) - 2, totalByOrgStructure[0], fontBold=True)
                    table.setText(row, len(tableColumns) - 1, totalByOrgStructure[1], fontBold=True)
                    table.mergeCells(row, 0, 1, len(tableColumns) - 2)
            return total

        def printSpecialities(reportData):
            total = [0] * accumSize
            printTotal = not onlyOrgStructures and not outputByOrgStructure
            totalMessage = u'Итог по специальности'

            specialities = reportData.keys()
            specialities.sort()
            for speciality in specialities:
                totalBySpeciality = printPersons(reportData[speciality])
                total = map(add, total, totalBySpeciality)

                if printTotal:
                    row = table.addRow()
                    table.setText(row, len(tableColumns) - 3, totalMessage, fontBold=True)
                    table.setText(row, len(tableColumns) - 2, totalBySpeciality[0], fontBold=True)
                    table.setText(row, len(tableColumns) - 1, totalBySpeciality[1], fontBold=True)
                    table.mergeCells(row, 0, 1, len(tableColumns) - 2)
            return total

        def printPersons(reportData):
            total = [0] * accumSize
            printLeaf = not onlyOrgStructures
            printTotal = not onlyOrgStructures and not outputByOrgStructure
            totalMessage = u'Итог по специалисту'

            persons = reportData.keys()
            persons.sort()
            for person, personId in persons:
                firstRow = table.rows()
                totalByPerson = printDates(reportData[(person, personId)])
                total = map(add, total, totalByPerson)

                if printLeaf:
                    table.setText(firstRow, 0, person)
                    table.mergeCells(firstRow, 0, table.rows() - firstRow, 1)

                if printTotal:
                    row = table.addRow()
                    table.setText(row, len(tableColumns) - 3, totalMessage, fontBold=True)
                    table.setText(row, len(tableColumns) - 2, totalByPerson[0], fontBold=True)
                    table.setText(row, len(tableColumns) - 1, totalByPerson[1], fontBold=True)
                    table.mergeCells(row, 0, 1, len(tableColumns) - 2)
            return total

        def printDates(reportData):
            total = [0] * accumSize
            printLeaf = not onlyOrgStructures and showDates

            dates = reportData.keys()
            dates.sort()
            for date in dates:
                firstRow = table.rows()
                totalByDate = printServices(reportData[date])
                total = map(add, total, totalByDate)

                if printLeaf:
                    table.setText(firstRow, 1, date)
                    table.mergeCells(firstRow, 1, table.rows() - firstRow, 1)
            return total

        def printServices(reportData):
            total = [0] * accumSize
            printLeaf = not onlyOrgStructures
            column = 2 if showDates else 1

            services = reportData.keys()
            services.sort()
            for serviceCode, serviceName in services:
                firstRow = table.rows()
                totalByService = printClients(reportData[(serviceCode, serviceName)])
                total = map(add, total, totalByService)

                if printLeaf:
                    table.setText(firstRow, column, serviceCode)
                    table.mergeCells(firstRow, column, table.rows() - firstRow, 1)
                    table.setText(firstRow, column + 1, serviceName)
                    table.mergeCells(firstRow, column + 1, table.rows() - firstRow, 1)
            return total

        def printClients(reportData):
            total = [0] * accumSize
            printLeaf = not onlyOrgStructures
            column = 3 + (1 if showDates else 0) + (1 if showClient else 0)

            clients = reportData.keys()
            clients.sort()
            for client in clients:
                serviceInfo = reportData[client]
                total[0] += serviceInfo['amount']
                total[1] += serviceInfo['sum']
                if printLeaf:
                    row = table.addRow()
                    if showClient:
                        table.setText(row, column - 1, client)
                    table.setText(row, column, serviceInfo['price'])
                    table.setText(row, column + 1, serviceInfo['amount'])
                    table.setText(row, column + 2, serviceInfo['sum'])
            return total

        queryActions = selectDataByActions(params)
        queryVisits = selectDataByVisits(params)
        outputByOrgStructure = params.get('chkOutputByOrgStructure',  False)
        onlyOrgStructures = outputByOrgStructure and params.get('onlyOrgStructures', False)
        showClient = params.get('showClient', False)
        showDates = params.get('showDates', False)

        resultDict = {}
        self.setQueryText('\n\n'.join([u'-------------Actions--------------',
                                       forceString(queryActions.lastQuery()),
                                       u'-------------Visits--------------',
                                       forceString(queryVisits.lastQuery())]))

        for query in [queryActions, queryVisits]:
            while query.next():
                record = query.record()
                endDate = forceString(record.value('endDate')).split(' ')[0]
                serviceCode = forceString(record.value('serviceCode'))
                serviceName = forceString(record.value('serviceName'))
                personId = forceRef(record.value('personId'))
                personName = forceString(record.value('personName'))
                clientFIO = ' '.join([forceString(record.value('lastName')),
                                      forceString(record.value('firstName')),
                                      forceString(record.value('patrName'))])
                amount = forceInt(record.value('amount'))
                price = forceDouble(record.value('price'))
                specialityId = forceRef(record.value('speciality_id'))
                orgStructureId = forceRef(record.value('orgStructureId'))
                orgStructureName = forceString(record.value('orgStructureName'))

                if query == queryVisits:
                    tariffAge = forceString(record.value('tariffAge'))
                    clientAge = forceInt(record.value('clientAge'))
                    if tariffAge:
                        begUnit,  begCount,  endUnit,  endCount = parseAgeSelector(tariffAge)
                        if (begUnit==4 and begCount>=clientAge) or (endUnit==4 and clientAge>=endCount):
                            continue

                orgStructureDict = resultDict.setdefault((orgStructureName, orgStructureId), {})
                specialityDict = orgStructureDict.setdefault(specialityId, {})
                personDict = specialityDict.setdefault((personName, personId), {})
                dateDict = personDict.setdefault(endDate if showDates else '', {})
                serviceDict = dateDict.setdefault((serviceCode, serviceName), {})
                serviceInfo = serviceDict.setdefault(clientFIO if showClient else '', {})
                serviceInfo.setdefault('price', 0.0)
                serviceInfo.setdefault('amount', 0)
                serviceInfo.setdefault('sum', 0.0)
                serviceInfo['price'] = price
                serviceInfo['amount'] += amount
                serviceInfo['sum'] += price * amount


        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('25%', [u'Специалист'], CReportBase.AlignLeft),
                        ('20%', [u'Код услуги'], CReportBase.AlignLeft),
                        ('20%', [u'Наименование услуги'], CReportBase.AlignLeft),
                        ('10%', [u'Цена услуги'], CReportBase.AlignRight),
                        ('10%', [u'Количество'], CReportBase.AlignRight),
                        ('10%', [u'Стоимость'], CReportBase.AlignRight),
                        ]
        if showClient:
            tableColumns.insert(3, ('15%', [u'Пациент'], CReportBase.AlignLeft))
        if showDates:
            tableColumns.insert(1, ('10%', [u'Дата'], CReportBase.AlignRight))

        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        printTotal()

        return doc

    def getDescription(self, params):
        begDate           = params.get('begDate', None)
        endDate           = params.get('endDate', None)
        chkStatus         = params.get('chkStatus', False)
        status            = params.get('status', None)
        chkGroupByPatient = params.get('chkGroupByPatient', None)
        contractText = params.get('contractText', None)
        financeText = params.get('financeText', None)

        rows = []

        if begDate:
            rows.append(u'Начальная дата периода: %s' % forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s'%forceString(endDate))
        if chkStatus and status is not None:
            rows.append(u'Статус: %s' % CActionType.retranslateClass(False).statusNames[status])
        if chkGroupByPatient:
            rows.append(u'Группировка по пациентам')
        if financeText:
            rows.append(u'Тип финансирования: %s' % financeText)
        if contractText:
            rows.append(u'Контракт: %s' % contractText)

        return rows


class CSetupReport(CDialogBase, Ui_ReportSetupByOrgStructureDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbStatus.clear()
        self.cmbStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbAssistantPost.setTable('rbPost')

        self.patientRequired                = False
        self.groupByPatientVisible          = False
        self.setupByOrgStructureVisible     = False
        self.setupByOrgStructureOnlyVisible = False
        self.setupByEventTypeVisible        = False
        self.setupByPersonVisible           = False
        self.strongOrgStructureVisible      = False
        self.clientAgeCategoryVisible       = False
        self.onlyClientAsPersonInLPUVisible = False
        self.outputByOrgStructureVisible    = False
        self.onlyDiscountPaymentVisible     = False
        self.onlyStaffRelativeVisible       = False
        self.chkPersonVisible               = False
        self.chkRefusedVisible              = False
        self.serviceTypesVisible            = False
        self.chkShowClientVisible           = False

        self.setStrongOrgStructureVisible(      self.strongOrgStructureVisible      )
        self.setGroupByPatientVisible(          self.groupByPatientVisible          )
        self.setSetupByOrgStructureVisible(     self.setupByOrgStructureVisible     )
        self.setSetupByEventTypeVisible(               self.setupByEventTypeVisible    )
        self.setSetupByPersonVisible(                  self.setupByPersonVisible       )
        self.setClientAgeCategoryVisible(       self.clientAgeCategoryVisible       )
        self.setOnlyClientAsPersonInLPUVisible( self.onlyClientAsPersonInLPUVisible )
        self.setOutputByOrgStructureVisible (   self.outputByOrgStructureVisible )
        self.setOnlyDiscountPaymentVisible (    self.onlyDiscountPaymentVisible )
        self.setOnlyStaffRelativeVisible (      self.onlyStaffRelativeVisible )
        self.setRefusedVisible(      self.chkRefusedVisible  )
        self.setChkPersonVisible(               self.chkPersonVisible )
        self.setVisibleAssistant(False)
        self.setServiceTypesVisible(self.serviceTypesVisible)
        self.setChkShowClientVisible(self.chkShowClientVisible)

        self.addModels('ServiceType', CServiceTypeModel(1, 13))
        self.lstServiceTypes.setModel(self.modelServiceType)
        self.lstServiceTypes.selectAll()

    def setStrongOrgStructureVisible(self, value):
        self.strongOrgStructureVisible = value
        self.chkOrgStructure.setVisible(value)
        self.cmbOrgStructure.setVisible(value)

    def setGroupByPatientVisible(self, value):
        self.groupByPatientVisible = value
        self.chkGroupByPatient.setVisible(value)

    def setSetupByOrgStructureVisible(self, value):
        self.setupByOrgStructureVisible = value
        self.lblReportType.setVisible(value)
        self.cmbReportType.setVisible(value)
        self.chkPatientInfo.setVisible(value)
        self.chkAllOrgStructure.setVisible(value)

    def setSetupByOrgStructureOnlyVisible(self,  value):
        self.setupByOrgStructureOnlyVisible = value
        self.lblReportType.setVisible(value)
        self.cmbReportType.setVisible(value)

    def setSetupByEventTypeVisible(self, value):
        self.setupByEventTypeVisible = value
        if value:
            self.cmbEventType.setTable('EventType', True)
        self.lblEventType.setVisible(value)
        self.cmbEventType.setVisible(value)

    def setSetupByPersonVisible(self, value):
        self.setupByPersonVisible = value
        self.lblPerson.setVisible(value)
        self.cmbPerson.setVisible(value)

    def setVisibleAssistant(self, value):
        self._assistantAvailable = value
        self.cmbAssistant.setVisible(value)
        self.chkAssistant.setVisible(value)
        self.cmbAssistantPost.setVisible(value)
        self.lblAssistant.setVisible(value)
        self.lblAssistantPost.setVisible(value)

    def setClientAgeCategoryVisible(self, value):
        self.clientAgeCategoryVisible = value
        self.chkClientAgeCategory.setVisible(value)
        self.cmbClientAgeCategory.setVisible(value)

    def setOnlyClientAsPersonInLPUVisible(self, value):
        self.onlyClientAsPersonInLPUVisible = value
        self.chkOnlyClientAsPersonInLPU.setVisible(value)

    def setOutputByOrgStructureVisible(self,  value):
        self.outputByOrgstructureVisible = value
        self.chkOutputByOrgStructure.setVisible(value)

    def setOnlyDiscountPaymentVisible(self, value):
        self.onlyDiscountPaymentVisible = value
        self.chkOnlyDiscountPayment.setVisible(value)

    def setOnlyStaffRelativeVisible(self, value):
        self.onlyStaffRelativeVisible = value
        self.chkOnlyStaffRelative.setVisible(value)

    def setRefusedVisible(self, value):
        self.RefusedVisible = value
        self.chkRefused.setVisible(value)

    def setChkPersonVisible(self, value):
        self.chkPersonVisible = value
        self.chkPerson.setVisible(value)

    def setServiceTypesVisible(self, value):
        self.chkDetailServiceTypes.setVisible(value)
        self.lstServiceTypes.setVisible(value)

    def setChkShowClientVisible(self, value):
        self.chkShowClientVisible = value
        self.chkShowClient.setVisible(value)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))

        chkStatus = params.get('chkStatus', False)
        self.chkStatus.setChecked(chkStatus)
        self.chkStatus.emit(QtCore.SIGNAL('clicked(bool)'), chkStatus)
        self.cmbStatus.setCurrentIndex(params.get('status', 0))

        self.cmbReportType.setCurrentIndex(params.get('reportType', 0))

        self.chkAllOrgStructure.setChecked(params.get('chkAllOrgStructure', False))

        self.chkPatientInfo.setChecked(params.get('chkPatientInfo', False))

        self.chkGroupByPatient.setChecked(params.get('chkGroupByPatient', True))

        self.cmbContract.setPath(params.get('contractPath', None))
        self.cmbFinance.setValue(params.get('typeFinanceId', None))
        self.chkNotContract.setChecked(params.get('notContract', False))

        if self.setupByEventTypeVisible:
            self.cmbEventType.setValue(params.get('eventTypeId', None))

        if self.setupByPersonVisible:
            self.cmbPerson.setValue(params.get('personId', None))

        self.chkAssistant.setChecked(params.get('isCheckAssistant', False))

        if self.cmbAssistant.isEnabled() and self._assistantAvailable:
            self.cmbAssistant.setValue(params.get('assistantId', None))

        if self.strongOrgStructureVisible:
            chkOrgStructure = params.get('chkOrgStructure', False)
            self.chkOrgStructure.setChecked(chkOrgStructure)
            self.chkOrgStructure.emit(QtCore.SIGNAL('clicked(bool)'), chkOrgStructure)
            self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

        if self.clientAgeCategoryVisible:
            chkClientAgeCategory = params.get('chkClientAgeCategory', False)
            self.chkClientAgeCategory.setChecked(chkClientAgeCategory)
            self.cmbClientAgeCategory.setCurrentIndex(params.get('clientAgeCategory', 0))
            self.cmbClientAgeCategory.setEnabled(chkClientAgeCategory)

        if self.onlyClientAsPersonInLPUVisible:
            self.chkOnlyClientAsPersonInLPU.setChecked(params.get('chkOnlyClientAsPersonInLPU', False))

        if self.outputByOrgstructureVisible:
            self.chkOutputByOrgStructure.setChecked(params.get('chkOutputByOrgStructure',  False))

        if self.chkPersonVisible:
            self.chkPerson.setChecked(params.get('chkPerson', False))

        self.chkOnlyDiscountPayment.setChecked(params.get('onlyDiscountPayment', False))
        self.chkOnlyStaffRelative.setChecked(params.get('onlyStaffRelative', False))
        self.chkRefused.setChecked(params.get('refused', False))
        self.chkPresenceInTariffs.setChecked(params.get('checkPresenceInTariffs', True))
        if self.cmbAssistantPost.isEnabled() and self._assistantAvailable:
            self.cmbAssistantPost.setValue(params.get('postId', None))
        self.chkPost.setChecked(params.get('enterPost', False))

        if params.get('byActionEndDate') is not None:
            self.rbtnByActionEndDate.setChecked(params.get('byActionEndDate', True))
            self.rbtnByFormingAccountDate.setChecked(not params.get('byActionEndDate', False))

        self.chkDetailServiceTypes.setChecked(params.get('detailServiceTypes', False))
        self.lstServiceTypes.setEnabled(self.chkDetailServiceTypes.isChecked())

        selectedServiceTypes = params.get('serviceTypes')
        if selectedServiceTypes is not None:
            flags = self.lstServiceTypes.selectionCommand(QtCore.QModelIndex())
            selectionModel = self.lstServiceTypes.selectionModel()
            model = self.lstServiceTypes.model()
            self.lstServiceTypes.clearSelection()
            for idx in selectedServiceTypes:
                selectionModel.select(model.index(idx), flags)

        if params.get('showClient'):
            self.chkShowClient.setChecked(params.get('showClient'))

        self.chkShowDates.setChecked(params.get('showDates', True))
        self.chkOnlyOrgStructures.setChecked(params.get('onlyOrgStructures', False))
        self.chkOnlyOrgStructures.setEnabled(self.chkOutputByOrgStructure.isChecked())

    def params(self):
        params = {}

        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['byActionEndDate'] = self.rbtnByActionEndDate.isChecked()
        params['chkStatus'] = self.chkStatus.isChecked()
        params['status']    = self.cmbStatus.currentIndex()

        params['contractPath'] = self.cmbContract.getPath()
        params['contractIdList'] = self.cmbContract.getIdList()
        params['contractText'] = forceString(self.cmbContract.currentText())
        params['typeFinanceId']  = self.cmbFinance.value()
        params['financeText'] = self.cmbFinance.currentText()
        params['chkRefused'] = self.chkRefused.isChecked()

        params['reportType'] = self.cmbReportType.currentIndex()
        params['notContract'] = self.chkNotContract.isChecked()

        if self.setupByEventTypeVisible:
            params['eventTypeId'] = self.cmbEventType.value()

        params['personId'] = self.cmbPerson.value() if self.cmbPerson.isEnabled() and self.setupByPersonVisible else None
        params['assistantId'] = self.cmbAssistant.value() if self.cmbAssistant.isEnabled() and self._assistantAvailable else None
        params['isCheckAssistant'] = self.chkAssistant.isChecked()

        if self.strongOrgStructureVisible:
            params['chkOrgStructure'] = self.chkOrgStructure.isChecked()
            params['orgStructureId'] = self.cmbOrgStructure.value()

        if self.setupByOrgStructureVisible:
            if self.chkAllOrgStructure.isEnabled():
                params['chkAllOrgStructure'] = self.chkAllOrgStructure.isChecked()
            else:
                params['chkAllOrgStructure'] = False

            params['chkPatientInfo'] = self.chkPatientInfo.isChecked()

        if self.groupByPatientVisible:
            params['chkGroupByPatient'] = self.chkGroupByPatient.isChecked()


        if self.clientAgeCategoryVisible:
            params['chkClientAgeCategory'] = self.chkClientAgeCategory.isChecked()
            params['clientAgeCategory'] = self.cmbClientAgeCategory.currentIndex()

        if self.onlyClientAsPersonInLPUVisible:
            params['chkOnlyClientAsPersonInLPU'] = self.chkOnlyClientAsPersonInLPU.isChecked()

        params['onlyDiscountPayment'] = self.chkOnlyDiscountPayment.isChecked()
        params['onlyStaffRelative'] = self.chkOnlyStaffRelative.isChecked()

        if self.outputByOrgstructureVisible:
            params['chkOutputByOrgStructure'] = self.chkOutputByOrgStructure.isChecked()

        if self.chkPersonVisible:
            params['chkPerson'] = self.chkPerson.isChecked()

        params['checkPresenceInTariffs'] = self.chkPresenceInTariffs.isChecked()
        params['postId'] = self.cmbAssistantPost.value() if self.cmbAssistantPost.isEnabled() and self._assistantAvailable else None
        params['enterPost'] = self.chkPost.isChecked()

        params['detailServiceTypes'] = self.chkDetailServiceTypes.isChecked()
        params['serviceTypes'] = self.lstServiceTypes.selectionModel().selectedIndexes()

        params['showClient'] = self.chkShowClient.isChecked()
        params['showDates'] = self.chkShowDates.isChecked()
        params['onlyOrgStructures'] = self.chkOnlyOrgStructures.isChecked()

        return params

    def getOrgStructureModel(self):
        return self.cmbOrgStructure.model()

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)
        self.cmbAssistant.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbReportType_currentIndexChanged(self, index):
        self.chkAllOrgStructure.setEnabled(index==1)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))
        self.cmbAssistant.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbAssistantPost_currentIndexChanged(self, index):
        postId = self.cmbAssistantPost.value()
        self.cmbAssistant.setPostId(postId)

    @QtCore.pyqtSlot(bool)
    def on_chkAssistant_toggled(self, value):
        if self.chkAssistant.isChecked():
            stringInfo = u'Группировать по ассистенту'
            stringEnterInfo = u'Выводить должность ассистента'
        else:
            stringInfo = u'Группировать по врачу'
            stringEnterInfo = u'Выводить должность врача'
        self.chkPerson.setToolTip(stringInfo)
        self.chkPost.setToolTip(stringEnterInfo)

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_toggled(self, value):
        if not self.chkOrgStructure.isChecked():
            self.cmbPerson.setOrgStructureId(None)
            self.cmbAssistant.setOrgStructureId(None)
        else:
            self.on_cmbOrgStructure_currentIndexChanged(0)

    @QtCore.pyqtSlot(bool)
    def on_chkDetailServiceTypes_clicked(self, checked):
        self.lstServiceTypes.setEnabled(self.chkDetailServiceTypes.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_chkNotContract_toggled(self, checked):
        self.lblContract.setEnabled(not self.chkNotContract.isChecked())
        self.cmbContract.setEnabled(not self.chkNotContract.isChecked())
        self.chkPresenceInTariffs.setEnabled(not self.chkNotContract.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_chkOutputByOrgStructure_toggled(self, checked):
        self.chkOnlyOrgStructures.setEnabled(self.chkOutputByOrgStructure.isChecked())