# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Accounting.Utils   import getClientDiscountInfo
from Events.Action      import CActionType
from Events.Utils       import getStatusRefused
from library.Utils      import forceDouble, forceInt, forceRef, forceString, formatName

from Reports.Report     import CReport
from Reports.ReportActionsByOrgStructure import CSetupReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params):
    begDate           = params.get('begDate', None)
    endDate           = params.get('endDate', None)
    chkStatus         = params.get('chkStatus', False)
    status            = params.get('status', None)
    chkGroupByPatient = params.get('chkGroupByPatient', False)
    contractIdList    = params.get('contractIdList', None)
    financeId         = params.get('financeId', None)
    eventTypeId       = params.get('eventTypeId', None)

    chkClientAgeCategory       = params.get('chkClientAgeCategory', False)
    clientAgeCategory          = params.get('clientAgeCategory', None)
    chkOnlyClientAsPersonInLPU = params.get('chkOnlyClientAsPersonInLPU', False)

    chkOutputByOrgStructure = params.get('chkOutputByOrgStructure',  False)

    reportType = params.get('reportType', None)
    reportPerson = 'person_id'
    if reportType == 0:
        reportPerson = 'person_id'
    elif reportType == 1:
        reportPerson = 'setPerson_id'

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
    tableAccountItem       = db.table('Account_Item')
    tableOrgStructure      = db.table('OrgStructure')

    queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionTypeService, tableActionType['id'].eq(tableActionTypeService['master_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.innerJoin(tableContract, 'Contract.`id`=IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)')
    queryTable = queryTable.innerJoin(tableContractTariff, [tableContractTariff['master_id'].eq(tableContract['id']),
                                                            tableContractTariff['service_id'].eq(tableActionTypeService['service_id'])])
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['action_id'].eq(tableAction['id']))

    cond = [
        tableAction['begDate'].dateGe(begDate),
        tableAction['begDate'].dateLe(endDate),
        tableAction['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
        db.if_(tableActionTypeService['finance_id'].name(),
               tableActionTypeService['finance_id'].eq(tableContract['finance_id']),
               '1'),
        tableContractTariff['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0)
    ]

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    if contractIdList:
        cond.append(tableContract['id'].inlist(contractIdList))

    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))

    if chkStatus and not status is None:
        cond.append(tableAction['status'].eq(status))

    if chkClientAgeCategory and not clientAgeCategory is None:
        cond.append('age({0}, CURRENT_DATE) {1} {2}'.format(tableClient['birthDate'], '<' if clientAgeCategory == 0 else '>=', 18))

    if chkOnlyClientAsPersonInLPU:
        clientWorkJoinCond = [tableClient['id'].eq(tableClientWork['client_id']),
                              'ClientWork.`id`=(SELECT MAX(CW.`id`) FROM ClientWork AS CW WHERE CW.`client_id`=Client.`id`)']
        queryTable = queryTable.innerJoin(tableClientWork, clientWorkJoinCond)
        cond.append(tableClientWork['org_id'].eq(QtGui.qApp.currentOrgId()))

    if chkGroupByPatient:
        fields = [
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            'sum({0}) AS actionsCount'.format(tableAction['amount']),
            'sum({0} * {1}) AS priceSum'.format(tableContractTariff['price'], tableAction['amount']),
            tableAction['payStatus']
        ]
        order = [
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
        ]
        if chkOutputByOrgStructure:
            queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableAction[reportPerson]))
            queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))

            fields.extend([
                tableOrgStructure['name'].alias('orgStructureName'),
                tableActionType['name'].alias('actionTypeName')
            ])
            group = [
                tableClient['id'],
                tableOrgStructure['id'],
                tableActionType['id'],
                tableAction['payStatus']
            ]
            order.extend([
                tableOrgStructure['name'],
                tableActionType['name']
            ])
            stmt = db.selectStmt(queryTable, fields, cond, group, order)
        else:
            fields.extend([
                tableClient['id'].alias('clientId'),
                'sum({0} * {1}) AS realSum'.format(tableAccountItem['price'], tableAccountItem['amount'])
            ])
            group = [
                tableClient['id'],
                tableAction['payStatus']
            ]
            stmt = db.selectStmt(queryTable, fields, cond, group, order)
    else:
        if chkOutputByOrgStructure:
            tableOrgStructure = db.table('OrgStructure')
            queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableAction[reportPerson]))
            queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))

            order = [
                tableOrgStructure['name'],
                tableActionType['name']
            ]
            group = [
                tableOrgStructure['id'],
                tableActionType['id'],
                tableAction['payStatus']
            ]
            fields = [
                tableOrgStructure['name'].alias('orgStructureName'),
                tableActionType['name'].alias('actionTypeName'),
                'sum({0}) AS actionsCount'.format(tableAction['amount']),
                'sum({0} * {1}) AS priceSum'.format(tableContractTariff['price'], tableAction['amount']),
                tableAction['payStatus']
            ]
            stmt = db.selectStmt(queryTable, fields, cond, group, order)

        else:
            queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['createPerson_id']))
            order = [
                tableAction['modifyDatetime']
            ]
            fields = [
                tableAction['modifyDatetime'],
                tableClient['id'].alias('clientId'),
                tableClient['lastName'],
                tableClient['firstName'],
                tableClient['patrName'],
                tableEvent['externalId'],
                tableActionType['code'].alias('actionTypeCode'),
                tableActionType['name'].alias('actionTypeName'),
                tablePerson['name'].alias('personName'),
                tableAction['amount'],
                tableContractTariff['price'],
                tableAction['payStatus']
            ]
            stmt = db.selectStmt(queryTable, fields, cond, order=order)

    query = db.query(stmt)
    return query


class CReportDoneActions(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по выписанным услугам')


    def getSetupDialog(self, parent):
        result = CSetupDoneActionsReport(parent)
        result.setGroupByPatientVisible(True)
        result.setClientAgeCategoryVisible(True)
        result.setOnlyClientAsPersonInLPUVisible(True)
        result.setOnlyDiscountPaymentVisible(True)
        result.setOnlyStaffRelativeVisible(True)
        result.setRefusedVisible(True)
        result.setOutputByOrgStructureVisible(True)
        result.setSetupByOrgStructureOnlyVisible(True)
        result.setSetupByEventTypeVisible(True)
        result.cmbReportType.setEnabled(False)
        result.setTitle(self.title())
        return result


    def build(self, params):
        query = selectData(params)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        onlyDiscountPayment = params.get('onlyDiscountPayment', False)
        onlyStaffRelative = params.get('onlyStaffRelative', False)
        chkRefused = params.get('chkRefused', False)
        chkGroupByPatient = params.get('chkGroupByPatient', False)
        chkOutputByOrgStructure = params.get('chkOutputByOrgStructure', False)

        if chkOutputByOrgStructure:
            tableColumns = [
                ('%20', [u'Свойство номенклатуры/Номенклатура'], CReportBase.AlignLeft),
                ('%2', [u'Ед.'], CReportBase.AlignLeft),
                ('%5', [u'Количество'], CReportBase.AlignLeft),
                ('%8', [u'Продажи'], CReportBase.AlignLeft)
            ]
            resume = [0] * 4
            resumeColumns = [2]

        elif onlyDiscountPayment and chkGroupByPatient:
            tableColumns = [
                ('%2', [u'№'], CReportBase.AlignRight),
                ('%5', [u'ФИО'], CReportBase.AlignLeft),
                ('%5', [u'Количество'], CReportBase.AlignLeft),
                ('%5', [u'стоимость'], CReportBase.AlignLeft),
                ('%5', [u'скидка(%)'], CReportBase.AlignLeft),
                ('%5', [u'сумма скидки'], CReportBase.AlignLeft),
                ('%5', [u'Примечание ("связь")'], CReportBase.AlignLeft)
            ]
            resume = [0] * 5
            resumeColumns = [1, 2, 3, 4]

        else:
            tableColumns = [
                ('%2', [u'№'], CReportBase.AlignRight),
                ('%5', [u'Код пациента'], CReportBase.AlignLeft),
                ('%5', [u'Имя пациента'], CReportBase.AlignLeft),
                ('%5', [u'Количество'], CReportBase.AlignLeft),
                ('%5', [u'Цена'], CReportBase.AlignLeft)
            ]
            if not chkGroupByPatient:
                tableColumns.insert(1, ('%5', [u'Дата и время'], CReportBase.AlignLeft))
                tableColumns.insert(4, ('%5', [u'№ обращения'], CReportBase.AlignLeft))
                tableColumns.insert(5, ('%5', [u'Код действия'], CReportBase.AlignLeft))
                tableColumns.insert(6, ('%5', [u'Наименование действия'], CReportBase.AlignLeft))
                tableColumns.insert(7, ('%5', [u'Оператор'], CReportBase.AlignLeft))
                resume = [0] * 9
                resumeColumns = [7, 8]
            else:
                resume = [0] * 4
                resumeColumns = [2, 3]
        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.DemiBold)
        boldItalicChars.setFontItalic(True)

        byOrgStruct = {}
        byClient = {}
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            isShow = True
            record = query.record()
            clientId = forceRef(record.value('clientId'))
            clientName = formatName(record.value('lastName'), record.value('firstName'), record.value('patrName'))
            #Вывод данных, если включен фильтр, исключающий отмененные услуги
            if chkRefused:
                if getStatusRefused(forceInt(record.value('payStatus'))):
                    isShow=False
            if chkGroupByPatient:
                if not chkOutputByOrgStructure:
                    actionsCount = forceInt(record.value('actionsCount'))
                    priceSum = forceDouble(record.value('priceSum'))
                    if onlyDiscountPayment:
                        realSum = forceDouble(record.value('realSum'))
                        discountInfo = getClientDiscountInfo(clientId)
                        discount = int(discountInfo[0] * 100)
                        #Не выводить данные, если нет скидки или если включена опция "Родственники сотрудников" и при этом пациент является причиной скидки
                        if discount <= 0 or (onlyStaffRelative and discountInfo[1] == clientId):
                            isShow = False
                        else:
                            discountNote = discountInfo[2]
                            values = [clientName, actionsCount, realSum, discount, priceSum - realSum, discountNote]
                    else:
                        values = [clientId, clientName, actionsCount, priceSum]
                else:
                    isShow = False
                    orgStructureName = forceString(record.value('orgStructureName'))
                    actionTypeName = forceString(record.value('actionTypeName'))
                    actionsCount = forceInt(record.value('actionsCount'))
                    priceSum = forceDouble(record.value('priceSum'))
                    values = [actionTypeName, u'шт.', actionsCount, priceSum]
                    byClient.setdefault(clientName, {}).setdefault(orgStructureName, []).append(values)
            elif chkOutputByOrgStructure:
                isShow = False
                record = query.record()
                orgStructureName = forceString(record.value('orgStructureName'))
                actionTypeName = forceString(record.value('actionTypeName'))
                actionsCount = forceInt(record.value('actionsCount'))
                priceSum = forceDouble(record.value('priceSum'))
                values = [actionTypeName, u'шт.', actionsCount, priceSum]
                byOrgStruct.setdefault(orgStructureName, []).append(values)
            else:
                date = forceString(record.value('modifyDatetime'))
                externalId = forceString(record.value('externalId'))
                actionTypeCode = forceString(record.value('actionTypeCode'))
                actionTypeName = forceString(record.value('actionTypeName'))
                amount = forceDouble(record.value('amount'))
                price = forceDouble(record.value('price'))
                personName = forceString(record.value('personName'))
                values = [date, clientId, clientName, externalId, actionTypeCode, actionTypeName, personName, amount, price*amount]

            #Вывод данных, если отключена опция выводить только оплаченные, либо (если только оплаченных), если скидка больше 0
            if isShow:
                i = table.addRow()
                table.setText(i, 0, i)
                for valueIdx, value in enumerate(values):
                    table.setText(i, valueIdx+1, value)
                    if valueIdx in resumeColumns:
                        resume[valueIdx] += value

        if chkOutputByOrgStructure:
            if chkGroupByPatient:
                byClientKeys = byClient.keys()
                byClientKeys.sort()
                for client in byClientKeys:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 3)
                    tmpClientSum = 0
                    for orgStruct in byClient[client].keys():
                        j = table.addRow()
                        table.mergeCells(j, 0, 1, 3)
                        tmpOrgSum = 0
                        for values in byClient[client][orgStruct]:
                            k = table.addRow()
                            for valueIdx, value in enumerate(values):
                                table.setText(k, valueIdx, value)
                                if valueIdx == 3:
                                    tmpOrgSum += value
                        table.setText(j, 0, orgStruct, charFormat = boldItalicChars)
                        table.setText(j, 3, tmpOrgSum, charFormat = boldItalicChars)
                        tmpClientSum += tmpOrgSum
                    table.setText(i, 0, client, charFormat = boldItalicChars)
                    table.setText(i, 3, tmpClientSum, charFormat = boldItalicChars)
                    resume[2] += tmpClientSum
            else:
                for orgStruct in byOrgStruct.keys():
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 3)
                    tmpSum = 0
                    for values in byOrgStruct[orgStruct]:
                        j = table.addRow()
                        for valueIdx, value in enumerate(values):
                            table.setText(j, valueIdx, value)
                            if valueIdx == 3:
                                tmpSum += value
                    table.setText(i, 0, orgStruct, charFormat=boldItalicChars)
                    table.setText(i, 3, tmpSum, charFormat=boldItalicChars)
                    resume[2] += tmpSum

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, u'Всего', charFormat=boldChars)
        for column in resumeColumns:
            table.setText(i, column+1, resume[column], charFormat=boldChars)

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
            rows.append(u'Начальная дата периода: %s'%forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s'%forceString(endDate))
        if chkStatus and not status is None:
            rows.append(u'Статус: %s' % CActionType.retranslateClass(False).statusNames[status])
        if chkGroupByPatient:
            rows.append(u'Группировка по пациентам')
        if financeText:
            rows.append(u'Тип финансирования: %s' % financeText)
        if contractText:
            rows.append(u'Контракт: %s' % contractText)

        return rows


class CSetupDoneActionsReport(CSetupReport):

    def __init__(self, parent=None):
        CSetupReport.__init__(self, parent)
        self.setStrongOrgStructureVisible(True)


    @QtCore.pyqtSlot(bool)
    def on_chkOutputByOrgStructure_toggled(self, checked):
        self.cmbReportType.setEnabled(checked)
