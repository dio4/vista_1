# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.ContractTariffCache import CContractTariffCache
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import recordAcceptable
from Orgs.Utils import getOrgStructureDescendants
from Registry.RegistryTable import CClientsTableModel
from Registry.Utils import getClientInfoEx
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from Ui_ReportClientActionsSetup import Ui_ReportClientActionsSetupDialog
from Ui_ReportClientSubsidiarySetupDialog import Ui_ReportClientSubsidiarySetupDialog
from library.AmountToWords import amountToWords
from library.DialogBase import CConstructHelperMixin
from library.TableView import CTableView
from library.Utils import calcAgeTuple, forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, formatName, nameCase


def getClientId(params):
    actionDateTypeValue    = params.get('actionDateTypeValue', 'begDate')
    begDate                = params.get('begDate', None)
    endDate                = params.get('endDate', None)
    chkClientCode          = params.get('chkClientCode', False)
    clientCode             = params.get('clientCode', None)
    accountingSystemId     = params.get('accountingSystemId', None)
    lastName               = params.get('lastName', None)
    firstName              = params.get('firstName', None)
    patrName               = params.get('patrName', None)
    birthDate              = params.get('birthDate', None)
    docType                = params.get('docType', None)
    leftSerial             = params.get('leftSerial', None)
    rightSerial            = params.get('rightSerial', None)
    number                 = params.get('number', None)
    policyType             = params.get('policyType', None)
    policySerial           = params.get('policySerial', None)
    policyNumber           = params.get('policyNumber', None)
    policyCompany          = params.get('policyCompany', None)
    contact                = params.get('contact', None)

    db = QtGui.qApp.db

    needJoinClientIdentification = bool(accountingSystemId)
    needJoinDocument             = (docType or (leftSerial and rightSerial) or number) and not chkClientCode
    needJoinPolicy               = (policyType or policySerial or policyNumber or policyCompany) and not chkClientCode
    needJoinContact              = bool(contact)

    tableClient               = db.table('Client')
    tableClientContact        = db.table('ClientContact')
    tableClientPolicy         = db.table('ClientPolicy')
    tableClientDocument       = db.table('ClientDocument')
    tableClientIdentification = db.table('ClientIdentification')

    tableAction               = db.table('Action')
    tableEvent                = db.table('Event')

    queryTable = tableClient.innerJoin(tableEvent, tableClient['id'].eq(tableEvent['client_id']))
#    queryTable = queryTable.innerJoin( tableEvent, tableEvent['id'].eq(tableAction['event_id']))

    if chkClientCode:
        if needJoinClientIdentification:
            queryTable = queryTable.innerJoin(tableClientIdentification,
                                              tableClientIdentification['client_id'].eq(tableClient['id']))
    else:
        if needJoinDocument:
            queryTable = queryTable.innerJoin(tableClientDocument,
                                              tableClientDocument['client_id'].eq(tableClient['id']))
        if needJoinPolicy:
            queryTable = queryTable.innerJoin(tableClientPolicy,
                                              tableClientPolicy['client_id'].eq(tableClient['id']))
        if needJoinContact:
            queryTable = queryTable.innerJoin(tableClientContact,
                                              tableClientContact['client_id'].eq(tableClient['id']))
    actionCond = '''
                    EXISTS (SELECT Action.`id` FROM Action WHERE %s AND %s AND %s AND Action.`event_id`=Event.`id`)
                 ''' %(tableAction[actionDateTypeValue].dateGe(begDate),
                       tableAction[actionDateTypeValue].dateLe(endDate),
                       tableAction['deleted'].eq(0))

    cond = [actionCond, tableEvent['deleted'].eq(0)]

    if chkClientCode:
        if accountingSystemId:
            cond.append(tableClientIdentification['accountingSystem_id'].eq(accountingSystemId))
            if clientCode:
                cond.append(tableClientIdentification['identifier'].eq(clientCode))
        else:
            if clientCode:
                cond.append(tableClient['id'].eq(clientCode))
    else:
        if lastName:
            cond.append(tableClient['lastName'].eq(nameCase(lastName)))
        if firstName:
            cond.append(tableClient['firstName'].eq(nameCase(firstName)))
        if patrName:
            cond.append(tableClient['patrName'].eq(nameCase(patrName)))
        if birthDate:
            cond.append(tableClient['birthDate'].eq(birthDate))

        if docType:
            cond.append(tableClientDocument['documentType_id'].eq(docType))
        if leftSerial and rightSerial:
            serial = ' '.join([forceStringEx(leftSerial), forceStringEx(rightSerial)])
            cond.append(tableClientDocument['serial'].eq(serial))
        if number:
            cond.append(tableClientDocument['number'].eq(number))

        if policyType:
            cond.append(tableClientPolicy['policyType_id'].eq(policyType))
        if policySerial:
            cond.append(tableClientPolicy['serial'].eq(policySerial))
        if policyNumber:
            cond.append(tableClientPolicy['number'].eq(policyNumber))
        if policyCompany:
            cond.append(tableClientPolicy['insurer_id'].eq(policyCompany))

        if contact:
            cond.append(tableClientContact['contact'].eq(contact))

    idField =  tableClient['id'].alias('clientId')

    order =  [
              tableClient['lastName'].name(),
              tableClient['firstName'].name(),
              tableClient['patrName'].name()
             ]

    idList  = db.getDistinctIdList(queryTable, idField, cond, order)
    selectedClientId = None
    QtGui.qApp.restoreOverrideCursor()
    if idList:
        if len(idList) > 1:
            clientCheckerDialog = CClientCheckerDialog(idList)
            clientCheckerDialog.exec_()
            selectedClientId = clientCheckerDialog.selectedClientId()
        else:
            selectedClientId = idList[0]
    QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    return selectedClientId


# #############################################################################
#                                                                             #
#                              variant two                                    #
#                      price like in EventCachPage                            #
#                                                                             #
# #############################################################################


def selectData2(params, clientId=None):
    chkClientCode = params.get('chkClientCode', False)
    onlyAccouting = params.get('onlyAccounting', False)
    clientCode = params.get('clientCode', None)
    accountingSystemId = params.get('accountingSystemId', None)
    lastName = params.get('lastName', None)
    firstName = params.get('firstName', None)
    patrName = params.get('patrName', None)
    birthDate = params.get('birthDate', None)
    docType = params.get('docType', None)
    leftSerial = params.get('leftSerial', None)
    rightSerial = params.get('rightSerial', None)
    number = params.get('number', None)
    policyType = params.get('policyType', None)
    policySerial = params.get('policySerial', None)
    policyNumber = params.get('policyNumber', None)
    policyCompany = params.get('policyCompany', None)
    contact = params.get('contact', None)
    actionDateTypeValue = params.get('actionDateTypeValue', 'begDate')
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    contractIdList = params.get('contractIdList', None)
    financeId = params.get('financeId', None)
    orgStructureId = params.get('orgStructureId', None)
    resultTypeIndex = params.get('resultTypeIndex', 0)
    mkbDiagnosis = params.get('mkbDiagnosis', '')
    payededOrg = params.get('payededOrg', None)

    needJoinClientIdentification = bool(accountingSystemId)
    needJoinDocument = (docType or (leftSerial and rightSerial) or number) and not chkClientCode
    needJoinPolicy = (policyType or policySerial or policyNumber or policyCompany) and not chkClientCode
    needJoinContact = contact and not chkClientCode

    db = QtGui.qApp.db

    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tablePerson = db.table('Person')
    tableEvent = db.table('Event')
    tableContract = db.table('Contract')
    tableFinance = db.table('rbFinance')
    tableClient = db.table('Client')
    tableClientContact = db.table('ClientContact')
    tableClientPolicy = db.table('ClientPolicy')
    tableClientDocument = db.table('ClientDocument')
    tableClientIdentification = db.table('ClientIdentification')
    tableOrgStructureAT = db.table('OrgStructure_ActionType')

    queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableOrgStructureAT,
                                      tableOrgStructureAT['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.innerJoin(tableContract,
                                      'Contract.`id`=IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)')
    queryTable = queryTable.innerJoin(tableFinance,
                                      'rbFinance.`id`=IF(Action.`finance_id`, Action.`finance_id`, Contract.`finance_id`)')

    if chkClientCode:
        if needJoinClientIdentification:
            queryTable = queryTable.innerJoin(tableClientIdentification,
                                              tableClientIdentification['client_id'].eq(tableClient['id']))
    else:
        if needJoinDocument:
            queryTable = queryTable.innerJoin(tableClientDocument,
                                              tableClientDocument['client_id'].eq(tableClient['id']))
        if needJoinPolicy:
            queryTable = queryTable.innerJoin(tableClientPolicy,
                                              tableClientPolicy['client_id'].eq(tableClient['id']))
        if needJoinContact:
            queryTable = queryTable.innerJoin(tableClientContact,
                                              tableClientContact['client_id'].eq(tableClient['id']))

    cond = [tableAction[actionDateTypeValue].dateGe(begDate),
            tableAction[actionDateTypeValue].dateLe(endDate),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            ]

    if onlyAccouting:
        cond.append(tableAction['payStatus'].eq(256))
    if clientId or resultTypeIndex in (1, 2):
        cond.append(tableClient['id'].eq(clientId))
    if contractIdList:
        cond.append(tableContract['id'].inlist(contractIdList))
    if financeId:
        cond.append(tableFinance['id'].eq(financeId))
    if orgStructureId:
        cond.append(tableOrgStructureAT['master_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if mkbDiagnosis:
        cond.append(
            '''EXISTS(SELECT Diagnosis.id
            FROM Diagnosis INNER JOIN Diagnostic ON Diagnostic.diagnosis_id=Diagnosis.id
            INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id=rbDiagnosisType.id
            WHERE Diagnostic.event_id = Event.id AND Diagnosis.deleted = 0 AND Diagnosis.MKB LIKE '%s' AND Diagnostic.deleted = 0
            AND (rbDiagnosisType.code = '1'
            OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id
            AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC
            INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1'
            AND DC.event_id = Event.id
            LIMIT 1)))))
            ''' % (mkbDiagnosis)
        )
    if payededOrg:
        tableEventLocalContract = db.table('Event_LocalContract')
        queryTable = queryTable.innerJoin(tableEventLocalContract,
                                          tableEventLocalContract['master_id'].eq(tableEvent['id']))
        cond.append(tableEventLocalContract['org_id'].eq(payededOrg))
        cond.append(tableEventLocalContract['deleted'].eq(0))
    if chkClientCode:
        if accountingSystemId:
            cond.append(tableClientIdentification['accountingSystem_id'].eq(accountingSystemId))
            if clientCode:
                cond.append(tableClientIdentification['identifier'].eq(clientCode))
        else:
            if clientCode:
                cond.append(tableClient['id'].eq(clientCode))
    else:
        if lastName:
            cond.append(tableClient['lastName'].eq(nameCase(lastName)))
        if firstName:
            cond.append(tableClient['firstName'].eq(nameCase(firstName)))
        if patrName:
            cond.append(tableClient['patrName'].eq(nameCase(patrName)))
        if birthDate:
            cond.append(tableClient['birthDate'].eq(birthDate))

        if docType:
            cond.append(tableClientDocument['documentType_id'].eq(docType))
        if leftSerial and rightSerial:
            serial = ' '.join([forceStringEx(leftSerial), forceStringEx(rightSerial)])
            cond.append(tableClientDocument['serial'].eq(serial))
        if number:
            cond.append(tableClientDocument['number'].eq(number))

        if policyType:
            cond.append(tableClientPolicy['policyType_id'].eq(policyType))
        if policySerial:
            cond.append(tableClientPolicy['serial'].eq(policySerial))
        if policyNumber:
            cond.append(tableClientPolicy['number'].eq(policyNumber))
        if policyCompany:
            cond.append(tableClientPolicy['insurer_id'].eq(policyCompany))

        if contact:
            cond.append(tableClientContact['contact'].eq(contact))

    fields = [
        tableEvent['id'].alias('eventId'),
        tableEvent['execDate'].name(),
        tableEvent['setDate'].alias('setDate'),
        tableEvent['eventType_id'].alias('eventTypeId'),
        tableActionType['name'].alias('actionTypeName'),
        tableActionType['code'].alias('actionTypeCode'),
        tableActionType['id'].alias('actionTypeId'),
        tableAction['amount'].alias('actionAmount'),
        tableAction['id'].alias('actionId'),
        tableAction['endDate'].alias('actionEndDate'),
        'getClientRegAddress(Client.`id`) AS clientAddress',
        tableClient['id'].alias('clientId'),
        tableClient['lastName'].alias('clientLastName'),
        tableClient['firstName'].alias('clientFirstName'),
        tableClient['patrName'].alias('clientPatrName'),
        tableClient['sex'].alias('clientSex'),
        tableClient['birthDate'].alias('clientBirthDate'),
        tableContract['id'].alias('contractId'),
        tableFinance['name'].alias('financeTypeName'),
        tableFinance['id'].alias('financeId'),
        tableAction['person_id'].alias('personId'),
        tablePerson['tariffCategory_id'].alias('personTariffCategoryId'),
        tablePerson['code'].alias('personCode')
    ]

    order = [
        tableClient['id'].name(),
        tableEvent['id'].name(),
        tableAction[actionDateTypeValue].name()
    ]

    stmt = db.selectStmt(queryTable, fields, cond, order=order)
    #    print stmt
    query = db.query(stmt)
    return query


class CReportClientActions(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.parent = parent
        self.setupDialog = None
        self._title = ''
        self._preferences = ''
        self.setTitle(u'Отчет работ по пациенту')
        self.contractTariffCache = CContractTariffCache()
        self.resetHelpers()

    def resetHelpers(self):
        self.mapClientIdToInfo = {}
        self.clientIdOrder = []
        self.contractNumberList = []
        self.clientActionKeysNeedFinanceTypeName = {}
        self.clientSex       = None
        self.clientAge       = None

    def reportLoop(self):
        params = self.getDefaultParams()
        while True:
            self.setupDialog = self.getSetupDialog(self.parent)
            self.setupDialog.setParams(params)
            if not self.setupDialog.exec_() :
                break
            params = self.setupDialog.params()
            setupSubsidiaryDialog = self.getSubsidiarySetupDialog(self.parent)
            setupSubsidiaryDialog.setParams(params)
            paramsSubsidiary = params
            self.saveDefaultParams(paramsSubsidiary)
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                reportResult = self.build(paramsSubsidiary)
            finally:
                QtGui.qApp.restoreOverrideCursor()
            viewDialog = CReportViewDialog(self.parent)
            if self.viewerGeometry:
                viewDialog.restoreGeometry(self.viewerGeometry)
            viewDialog.setWindowTitle(self.title())
            viewDialog.setRepeatButtonVisible()
            viewDialog.setText(reportResult)
            done = not viewDialog.exec_()
            self.viewerGeometry = viewDialog.saveGeometry()
            if done:
                break

    def getSetupDialog(self, parent):
        result = CReportClientActionsSetupDialog(parent, self)
        result.setTitle(self.title())
        return result

    def getSubsidiarySetupDialog(self, parent):
        result = CReportClientSubsidiarySetupDialog(parent, self)
        result.setTitle(self.title())
        return result

    def build(self, params):
        fontSize = 12
        self.resetHelpers()
        clientId = None
        resultTypeIndex = params.get('resultTypeIndex', 0)
        if resultTypeIndex in (1, 2):
            clientId = getClientId(params)
        query = selectData2(params, clientId)
        self.setQueryText(forceString(query.lastQuery()))
        detailDateAndPersonCode = params.get('detailDateAndPersonCode', False)
        self.structInfo(query, detailDateAndPersonCode)

        doc = QtGui.QTextDocument()
        if query is None:
            return doc
        cursor = QtGui.QTextCursor(doc)
        if resultTypeIndex in (1, 2) and clientId:
            self.setReportHeaderForAct(cursor, clientId, params, fontSize = fontSize)
        else:
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(self.title())
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.insertBlock()

        tableBodyBold = CReportBase.TableBody
        tableBodyBold.setFontWeight(QtGui.QFont.Bold)
        tableBodyBold.setFontPointSize(fontSize)
        tableBody = CReportBase.TableBody
        tableBody.setFontPointSize(fontSize)
        inc = 0
        tableColumns = [
            ('3%', [u'№'], CReportBase.AlignLeft),
            ('7%', [u'Код услуги'], CReportBase.AlignLeft),
            ('60%', [u'Наименование услуги'], CReportBase.AlignLeft),
            ('5%', [u'Количество'], CReportBase.AlignLeft),
            ('5%', [u'Стоимость.руб'], CReportBase.AlignLeft),
            ('5%', [u'Сумма.руб'], CReportBase.AlignLeft)
        ]
        if resultTypeIndex == 2:
            inc = 1
            tableColumns.insert(3, ('8%', [u'Дата выполнения услуги'], CReportBase.AlignLeft))
        elif detailDateAndPersonCode:
            tableColumns.extend([
                ('8%', [u'Дата оказания услуги'], CReportBase.AlignLeft),
                ('7%', [u'Код врача'], CReportBase.AlignLeft)
            ])
        mergeLength = len(tableColumns)
        tableHeader = CReportBase.TableHeader
        tableHeader.setFontPointSize(fontSize)
        table = createTable(cursor, tableColumns, charFormat = tableHeader)
        
        result = [0, 0, 0]
        actionIdx = 0
        for clientId in self.clientIdOrder:
            printClientInfo = False or (resultTypeIndex in (1, 2))
            clientInfo = self.mapClientIdToInfo.get(clientId, None)
            if not clientInfo:
                continue
            if not printClientInfo:
                clientName, clientAddress = clientInfo['aboutClient']
                i = table.addRow()
                table.setText(i, 0, clientName+u', карта №: %d'%clientId, charFormat=tableBodyBold)
                i = table.addRow()
                table.setText(i, 0, clientAddress, charFormat=tableBodyBold)
                table.mergeCells(i-1, 0, 2, mergeLength)
            clientActions = clientInfo['clientActions']
            actionKeys = clientActions.keys()
            actionKeys.sort()
            clientResult = [0, 0, 0]
            for key in actionKeys:
                actionIdx += 1
                i = table.addRow()
                table.setText(i, 0, actionIdx, charFormat = tableBody)
                actionInfo = clientActions[key]
                actionTypeCode  = key[1]
                actionTypeName  = key[0]
                financeTypeName = key[2]
                actionAmount    = actionInfo['actionAmount']
                price           = actionInfo['price']
                sum             = actionInfo['sum']
                table.setText(i, 1, actionTypeCode, charFormat = tableBody)
                financeTypeAdditionIfNeed = self.getFinanceTypeAdditionIfNeed(clientId,
                                                                              actionTypeCode,
                                                                              actionTypeName,
                                                                              financeTypeName)
                table.setText(i, 2, actionTypeName+financeTypeAdditionIfNeed, charFormat = tableBody)
                table.setText(i, 3+inc, actionAmount, charFormat = tableBody)
                table.setText(i, 4+inc, price, charFormat = tableBody)
                table.setText(i, 5+inc, sum, charFormat = tableBody)
                if resultTypeIndex == 2:
                    table.setText(i, 3, actionInfo['actionEndDate'], charFormat = tableBody)
                elif detailDateAndPersonCode:
                    table.setText(i, 6, actionInfo['actionEndDate'], charFormat = tableBody)
                    table.setText(i, 7, actionInfo['personCode'], charFormat = tableBody)

                clientResult[0] += actionAmount
                clientResult[2] += sum
            if len(self.clientIdOrder) > 1:
                i = table.addRow()
                table.setText(i, 2, u'Итого', charFormat=tableBodyBold)
                table.mergeCells(i, 0, 1, 3)
                table.setText(i, 3, clientResult[0], charFormat=tableBodyBold)
                table.setText(i, 5, clientResult[2], charFormat=tableBodyBold)

            result[0] += clientResult[0]
            result[2] += clientResult[2]

        i = table.addRow()
        table.setText(i, 2, u'Всего', charFormat=tableBodyBold)
        table.mergeCells(i, 0, 1, 3)
        quantity, amount = (4, 6) if resultTypeIndex == 2 else (3, 5)
        table.setText(i, quantity, result[0], charFormat=tableBodyBold)
        table.setText(i, amount, result[2], charFormat=tableBodyBold)

        resultPriceText = amountToWords(result[2])
        i = table.addRow()
        table.setText(i, 2, resultPriceText, charFormat=tableBodyBold,  blockFormat = CReportBase.AlignCenter)
        table.mergeCells(i, 0, 1, mergeLength)

        cursor.movePosition(QtGui.QTextCursor.End)
        if resultTypeIndex in (1, 2):
            chiefPref = u'Главный врач'
            chief = forceStringEx(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'chief'))
            chiefLine = u'_'*(40-len(chief))
            if chief:
                chief = chiefPref+chiefLine+chief
            else:
                chief = chiefPref+chiefLine
            cursor.insertBlock(CReportBase.AlignLeft)
            cursor.insertText(u'\n\n'+chief, tableBody)

            underLineChars = QtGui.QTextCharFormat()
            underLineChars.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)
            cursor.insertBlock(CReportBase.AlignRight, underLineChars)
            cursor.insertText(forceString(QtCore.QDate.currentDate()), tableBody)
        return doc

    def getFinanceTypeAdditionIfNeed(self, clientId, actionTypeCode, actionTypeName, financeTypeName):
        actionKey = self.clientActionKeysNeedFinanceTypeName.get(clientId, {})
        financeTypeList = actionKey.get((actionTypeName, actionTypeCode), [])
        if len(financeTypeList) > 1:
            return '('+financeTypeName+')'
        return ''

    def structInfo(self, query, detailActions=False):
        existActionIdList = []
        contractIdList = []
        while query.next():
            record = query.record()

            actionId = forceRef(record.value('actionId'))
            if actionId in existActionIdList:
                continue
            existActionIdList.append(actionId)

            actionAmount = forceDouble(record.value('actionAmount'))
            if not actionAmount:
                continue
            contractId = forceRef(record.value('contractId'))
            actionTypeId = forceRef(record.value('actionTypeId'))
            financeId = forceRef(record.value('financeId'))
            actionTypeName = forceString(record.value('actionTypeName'))
            actionTypeCode = forceString(record.value('actionTypeCode'))
            personId = forceRef(record.value('personId'))
            clientId = forceRef(record.value('clientId'))
            clientSex = forceInt(record.value('clientSex'))
            clientBirthDate = forceDate(record.value('clientBirthDate'))
            financeTypeName = forceString(record.value('financeTypeName'))
            eventTypeId = forceRef(record.value('eventTypeId'))
            eventSetDate = forceDate(record.value('setDate'))
            eventExecDate = forceDate(record.value('execDate'))
            tariffCategoryId = forceRef(record.value('personTariffCategoryId'))
            actionEndDate = forceString(record.value('actionEndDate'))
            personCode = forceString(record.value('personCode'))
            eventDate = eventExecDate if eventExecDate.isValid() else eventSetDate
            if not clientId in self.clientIdOrder:
                self.clientIdOrder.append(clientId)
            clientName = formatName(
                record.value('clientLastName'),
                record.value('clientFirstName'),
                record.value('clientPatrName')
            )
            clientAddress = forceString(record.value('clientAddress'))
            self.setCurrentEventTypeId(eventTypeId)
            self.updateClientInfo(clientSex, clientBirthDate, eventDate)
            serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
            price = CContractTariffCache.getPrice(self.getTariffMap(contractId), serviceIdList, tariffCategoryId)
            if not price:
                continue

            if not contractId in contractIdList:
                contractIdList.append(contractId)

            clientInfo = self.mapClientIdToInfo.setdefault(clientId, {})
            if not clientInfo:
                clientInfo['aboutClient'] = [clientName, clientAddress]
            clientActions = clientInfo.setdefault('clientActions', {})
            key = (actionTypeName, actionTypeCode, financeTypeName)
            if detailActions:
                key = key + (actionId,)
            actionTypeValues = clientActions.setdefault(
                key,
                {'actionsCount': 0, 'actionAmount': 0, 'price': price, 'sum': 0}
            )
            actionTypeValues['actionsCount'] += 1
            actionTypeValues['actionAmount'] += actionAmount
            actionTypeValues['sum'] += actionAmount * price

            actionTypeValues['actionEndDate'] = actionEndDate

            if detailActions:
                actionTypeValues['actionEndDate'] = actionEndDate
                actionTypeValues['personCode'] = personCode

            actionKey = self.clientActionKeysNeedFinanceTypeName.setdefault(clientId, {
                (actionTypeName, actionTypeCode): [financeTypeName]})
            financeTypeNameList = actionKey.setdefault((actionTypeName, actionTypeCode), [])
            if not financeTypeName in financeTypeNameList:
                financeTypeNameList.append(financeTypeName)
        self.formatContractIdList(contractIdList)

    def formatContractIdList(self, contractIdList):
        db = QtGui.qApp.db
        table = db.table('Contract')
        recordList = db.getRecordList(table, 'number', table['id'].inlist(contractIdList))
        result = []
        for record in recordList:
            result.append(forceString(record.value('number')))
        self.contractNumberList = result

    def setReportHeaderForAct(self, cursor, clientId, params, fontSize = 0):
        reportBody = QtGui.QTextCharFormat()
        reportBody.setFontPointSize(fontSize)
        reportSubTitle = QtGui.QTextCharFormat()
        reportSubTitle.setFontWeight(QtGui.QFont.Bold)
        reportSubTitle.setFontPointSize(fontSize)
        
        clientInfo = getClientInfoEx(clientId)
        cursor.setCharFormat(reportSubTitle)
        orgName = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'shortName'))
        cursor.insertText(orgName)

        cursor.insertBlock(CReportBase.AlignLeft)
        cursor.setCharFormat(reportBody)
        cursor.insertText(u'Договор: '+', '.join(self.contractNumberList), reportBody)

        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText('\n\n\n'+self.title(), reportBody)

        cursor.insertBlock()
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        periodText = u'период: с %s по %s' %(forceString(begDate), forceString(endDate))
        cursor.insertText(periodText, reportBody)

        cursor.insertBlock(CReportBase.AlignLeft)
        financeText = params.get('financeText', None)
        financeText = financeText if financeText else u'не уточнен'
        cursor.insertText(u'\nИсточник финансирования: %s'%financeText, reportBody)

        cursor.insertBlock()
        cursor.insertText(u'Пациент: ', reportBody)
        cursor.insertText(clientInfo.fullName, reportSubTitle)

        cursor.insertBlock()
        cursor.insertText(u'Дата рождения: %s'%clientInfo.birthDate, reportBody)

        cursor.insertBlock()
        cursor.insertText(u'Карта, №: %d'%clientInfo.id, reportBody)

#        try:
#            region = getMainRegionName(clientInfo.regAddressInfo.KLADRCode)
#        except:
#            region = u'не определен'
#        cursor.insertBlock()
#        cursor.insertText(u'Регион: %s'%region)

        cursor.insertBlock()
        address = clientInfo.regAddress
        cursor.insertText(u'Адрес: %s'%address, reportBody)
        
        diagId = params.get('mkbDiagnosis', None)
        if diagId:
            cursor.insertBlock()
            cursor.insertText(u'Диагноз: %(diagId)s %(diagName)s' % {'diagId' : diagId, 
                                                                    'diagName' : forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', diagId, 'DiagName'))
                                                                    },
                              reportBody)
        else:
            diagnosis = QtGui.qApp.db.getRecordEx(
                stmt=u"""
                SELECT
                    CONCAT_WS(' ', DiagID, DiagName) AS clientDiagnosis
                FROM
                    Diagnostic
                    LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id
                    LEFT JOIN MKB_Tree ON Diagnosis.MKB = MKB_Tree.DiagID
                WHERE
                    Diagnosis.diagnosisType_id IN (1, 2)
                    AND Diagnosis.client_id = %s
                LIMIT 1;
                """ % clientInfo.id
            )
            if diagnosis:
                cursor.insertBlock()
                cursor.insertText(u'Диагноз: %s' % forceString(diagnosis.value('clientDiagnosis')))

        cursor.insertBlock()
        policySerial = u''
        policyNumber = u''
        if clientInfo.voluntaryPolicyRecord:
            policySerial = forceString(clientInfo.voluntaryPolicyRecord.value('serial'))
            policyNumber = forceString(clientInfo.voluntaryPolicyRecord.value('number'))
        cursor.insertText(u'Полис: %s %s' % (policySerial, policyNumber) , reportBody)
        
        cursor.insertBlock()
        cursor.insertText(u'\n\n', reportBody)
        
    def setVal(self, params):
        if self.setupDialog:
            self.setupDialog.setParams(params, dontChangeTitle=True)

    def getDescription(self, params):
        resultTypeIndex        = params.get('resultTypeIndex', 0)
        chkClientCode          = params.get('chkClientCode', False)
        clientCode             = params.get('clientCode', '')
        accountingSystemId     = params.get('accountingSystemId', None)
        lastName               = params.get('lastName', '')
        firstName              = params.get('firstName', '')
        patrName               = params.get('patrName', '')
        birthDate              = params.get('birthDate', None)
        docType                = params.get('docType', None)
        leftSerial             = params.get('leftSerial', '')
        rightSerial            = params.get('rightSerial', '')
        number                 = params.get('number', '')
        policyType              = params.get('policyType', None)
        policySerial            = params.get('policySerial', '')
        policyNumber            = params.get('policyNumber', '')
        policyCompany           = params.get('policyCompany', None)
        contact                = params.get('contact', '')
        actionDateTypeText     = params.get('actionDateTypeText', None)
        begDate                = params.get('begDate', None)
        endDate                = params.get('endDate', None)
        contractText           = params.get('contractText', None)
        financeText            = params.get('financeText', None)
        mkbDiagnosis           = params.get('mkbDiagnosis', '')
        payededOrg             = params.get('payededOrg', None)

        rows = []
        if actionDateTypeText:
            rows.append(u'Учитывается %s'%actionDateTypeText)
        if begDate:
            rows.append(u'Начальная дата периода: %s'%forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s'%forceString(endDate))
        if financeText:
            rows.append(u'Тип финансирования: %s' % financeText)
        if contractText:
            rows.append(u'Контракт: %s' % contractText)
        if payededOrg:
            rows.append(u'Плательщик: %s' % forceString(QtGui.qApp.db.translate('Organisation', 'id', payededOrg, 'shortName')))
        if mkbDiagnosis:
            rows.append(u'Диагноз: %s' % mkbDiagnosis)

        db = QtGui.qApp.db
        if chkClientCode:
            if accountingSystemId:
                accountingSysteName = forceString(db.translate('rbAccountingSystem', 'id', accountingSystemId, 'name'))
            if clientCode:
                if accountingSystemId:
                    rows.append(u'Код: %s %s'%(accountingSysteName, clientCode))
                else:
                    rows.append(u'Карта, №: %s'%clientCode)

                diagnosis = QtGui.qApp.db.getRecordEx(
                    stmt=u"""
                    SELECT
                        CONCAT_WS(' ', DiagID, DiagName) AS clientDiagnosis
                    FROM
                        Diagnostic
                        LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id
                        LEFT JOIN MKB_Tree ON Diagnosis.MKB = MKB_Tree.DiagID
                    WHERE
                        Diagnosis.diagnosisType_id IN (1, 2)
                        AND Diagnosis.client_id = %s
                    LIMIT 1;
                    """ % clientCode
                )
                if diagnosis:
                    rows.append(u'Диагноз: %s' % forceString(diagnosis.value('clientDiagnosis')))
        else:
            if lastName:
                rows.append(u'Фамилия: %s'%lastName)
            if firstName:
                rows.append(u'Имя: %s'%firstName)
            if patrName:
                rows.append(u'Отчество: %s'%patrName)
            if birthDate:
                rows.append(u'Дата рождения: %s'%forceString(birthDate))
            if docType:
                docTypeName = forceString(db.translate('rbDocumentType', 'id', docType, 'name'))
                rows.append(u'Тип документа: %s'%docTypeName)
            if leftSerial:
                rows.append(u'Левая часть серии документа: %s'%leftSerial)
            if rightSerial:
                rows.append(u'Правая часть серии документа: %s'%rightSerial)
            if number:
                rows.append(u'Номер документа: %s'%number)
            if policyType:
                policyTypeName = forceString(db.translate('rbPolicyType', 'id', policyType, 'name'))
                rows.append(u'Тип полиса: %s'%policyTypeName)
            if policySerial:
                rows.append(u'Серия полиса: %s'%policySerial)
            if policyNumber:
                rows.append(u'Номер полиса: %s'%policyNumber)
            if policyCompany:
                policyCompanyName = forceString(db.translate('Organisation', 'id', policyCompany, 'shortName'))
                rows.append(u'Страховая компания: %s'%policyCompanyName)
            if contact:
                rows.append(u'Контакт: %s'%contact)
        return rows

    def getTariffMap(self, contractId):
        tariffDescr = self.contractTariffCache.getTariffDescr(contractId, self)
        return tariffDescr.actionTariffMap

    def setCurrentEventTypeId(self, eventTypeId):
        self._currentEventTypeId = eventTypeId

    def getEventTypeId(self):
        return self._currentEventTypeId

    def updateClientInfo(self, clientSex, clientBirthDate, eventDate):
        self.clientSex       = clientSex
        self.clientAge       = calcAgeTuple(clientBirthDate, eventDate)

    def recordAcceptable(self, record):
        return recordAcceptable(self.clientSex, self.clientAge, record)


class CReportClientActionsSetupDialog(QtGui.QDialog, Ui_ReportClientActionsSetupDialog):
    def __init__(self, parent, report):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self._report = report
        self.contractIdListPayededOld = None
        self.actionDateValuePayededOld = ''
        self.financeIdPayededOld = None
        self.begDatePayededOld = QtCore.QDate()
        self.endDatePayededOld = QtCore.QDate()

        self.contractIdListMKBOld = None
        self.actionDateValueMKBOld = ''
        self.financeIdMKBOld = None
        self.begDateMKBOld = QtCore.QDate.currentDate()
        self.endDateMKBOld = QtCore.QDate.currentDate()

        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbAccountingSystem.setTable('rbAccountingSystem', True)
        self.cmbDocType.setTable(
            'rbDocumentType',
            True,
            'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')'
        )
        self.cmbPolicyType.setTable('rbPolicyType', True)
        self.valuesCmbActionDateType = [
            (u'дата назначения', QtCore.QVariant(u'directionDate')),
            (u'дата начала', QtCore.QVariant(u'begDate')),
            (u'дата выполнения', QtCore.QVariant(u'endDate'))
        ]
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.loadCmbActionDateType()

    def loadCmbActionDateType(self):
        self.cmbActionDateType.clear()
        for text, data in self.valuesCmbActionDateType:
            self.cmbActionDateType.addItem(text, data)

    def accept(self):
        if self.chkClientCode.isChecked():
            if not self.cmbAccountingSystem.value():
                try:
                    clientCode = int(forceStringEx(self.edtClientCode.text()))
                except ValueError:
                    QtGui.QMessageBox.critical(
                        QtGui.qApp.mainWindow,
                        u'Внимание!',
                        u'Идентификационный код пациента введен неверно!',
                        QtGui.QMessageBox.Ok
                    )
                    return None
        QtGui.QDialog.accept(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params, dontChangeTitle=False):
        if not dontChangeTitle:
            self.cmbResultType.setCurrentIndex(params.get('resultTypeIndex', 0))
        self.chkDetailDateAndPersonCode.setChecked(params.get('detailDateAndPersonCode', False))
        chkClientCode = params.get('chkClientCode', False)
        self.chkClientCode.setChecked(chkClientCode)
        self.chkClientCode.emit(QtCore.SIGNAL('clicked(bool)'), chkClientCode)
        self.edtClientCode.setText(params.get('clientCode', ''))
        self.cmbAccountingSystem.setValue(params.get('accountingSystemId', None))
        self.edtLastName.setText(params.get('lastName', ''))
        self.edtFirstName.setText(params.get('firstName', ''))
        self.edtPatrName.setText(params.get('patrName', ''))
        self.edtBirthDate.setDate(params.get('birthDate', QtCore.QDate()))
        self.cmbDocType.setValue(params.get('docType', None))
        self.edtLeftSerial.setText(params.get('leftSerial', ''))
        self.edtRightSerial.setText(params.get('rightSerial', ''))
        self.edtNumber.setText(params.get('number', ''))
        self.cmbPolicyType.setValue(params.get('policyType', None))
        self.edtPolicySerial.setText(params.get('policySerial', ''))
        self.edtPolicyNumber.setText(params.get('policyNumber', ''))
        self.cmbPolicyCompany.setValue(params.get('policyCompany', None))
        self.edtContact.setText(params.get('contact', ''))
        self.cmbActionDateType.setCurrentIndex(params.get('cmbActionDateTypeIndex', 0))
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbContract.setPath(params.get('contractPath', None))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkOnlyAccounting.setChecked(params.get('onlyAccounting', False))

    def params(self):
        params = {}
        params['resultTypeIndex'] = self.cmbResultType.currentIndex()
        params['detailDateAndPersonCode'] = self.chkDetailDateAndPersonCode.isChecked()
        params['chkClientCode'] = self.chkClientCode.isChecked()
        params['onlyAccounting'] = self.chkOnlyAccounting.isChecked()
        if params['chkClientCode']:
            params['clientCode'] = forceStringEx(self.edtClientCode.text())
            params['accountingSystemId'] = self.cmbAccountingSystem.value()
        else:
            params['lastName'] = forceStringEx(self.edtLastName.text())
            params['firstName'] = forceStringEx(self.edtFirstName.text())
            params['patrName'] = forceStringEx(self.edtPatrName.text())
            params['birthDate'] = self.edtBirthDate.date()
            params['docType'] = self.cmbDocType.value()
            params['leftSerial'] = forceStringEx(self.edtLeftSerial.text())
            params['rightSerial'] = forceStringEx(self.edtRightSerial.text())
            params['number'] = forceStringEx(self.edtNumber.text())
            params['policyType'] = self.cmbPolicyType.value()
            params['policySerial'] = forceStringEx(self.edtPolicySerial.text())
            params['policyNumber'] = forceStringEx(self.edtPolicyNumber.text())
            params['policyCompany'] = self.cmbPolicyCompany.value()
            params['contact'] = forceStringEx(self.edtContact.text())

        params['contractPath'] = self.cmbContract.getPath()
        params['contractIdList'] = self.cmbContract.getIdList()
        params['contractText'] = forceString(self.cmbContract.currentText())
        params['financeId'] = self.cmbFinance.value()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['financeText'] = self.cmbFinance.currentText()

        params['cmbActionDateTypeIndex'] = self.cmbActionDateType.currentIndex()
        params['actionDateTypeText'] = unicode(self.cmbActionDateType.currentText())
        params['actionDateTypeValue'] = forceString(self.cmbActionDateType.itemData(
            params['cmbActionDateTypeIndex']))
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        return params

    @QtCore.pyqtSlot(int)
    def on_cmbResultType_currentIndexChanged(self, index):
        if index == 0:
            title = u'Отчет работ по пациенту'
        elif index == 1:
            title = u'Реестр оказанных услуг'
        elif index == 2:
            title = u'Реестр оказанных услуг c датами выполнения'
            self.chkDetailDateAndPersonCode.setChecked(True)

        self.chkDetailDateAndPersonCode.setEnabled(index != 2)
        self.setTitle(title)
        self._report.setTitle(title)


class CReportClientSubsidiarySetupDialog(QtGui.QDialog, Ui_ReportClientSubsidiarySetupDialog):
    def __init__(self, parent, report):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self._report = report
        self.paramsSubsidiary = {}

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.Subsidiary = params
        resultTypeIndex = self.Subsidiary.get('resultTypeIndex', 0)
        if resultTypeIndex == 0:
            title = u'Отчет работ по пациенту'
        elif resultTypeIndex == 1:
            title = u'Реестр оказанных услуг'
        elif resultTypeIndex == 2:
            title = u'Реестр оказанных услуг с датами выполнения'
        self.setTitle(title)
        self.getFilterPayeded()
        self.getFilterMKB()

    def params(self):
        self.Subsidiary['payededOrg'] = self.cmbPayeded.value()
        self.Subsidiary['mkbDiagnosis'] = self.edtDiagnosis.text()
        return self.Subsidiary

    def getFilterPayeded(self):
        self.cmbPayeded.clear()
        actionDateTypeValue    = self.Subsidiary.get('actionDateTypeValue', 'begDate')
        begDate                = self.Subsidiary.get('begDate', None)
        endDate                = self.Subsidiary.get('endDate', None)
        contractIdList         = self.Subsidiary.get('contractIdList', None)
        financeId              = self.Subsidiary.get('financeId', None)
        if actionDateTypeValue:
            db = QtGui.qApp.db
            tableAction               = db.table('Action')
            tableActionType           = db.table('ActionType')
            tableEvent                = db.table('Event')
            tableContract             = db.table('Contract')
            tableFinance              = db.table('rbFinance')
            tableEventLocalContract   = db.table('Event_LocalContract')
            tableOrganisation         = db.table('Organisation')
            queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            queryTable = queryTable.innerJoin(tableContract, 'Contract.`id`=IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)')
            queryTable = queryTable.innerJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
            queryTable = queryTable.innerJoin(tableEventLocalContract, tableEventLocalContract['master_id'].eq(tableEvent['id']))
            actionCond = '''
                            EXISTS (SELECT Action.`id` FROM Action WHERE %s AND %s AND %s AND Action.`event_id`=Event.`id`)
                         ''' %(tableAction[actionDateTypeValue].dateGe(begDate),
                               tableAction[actionDateTypeValue].dateLe(endDate),
                               tableAction['deleted'].eq(0))
            cond = [actionCond, tableEvent['deleted'].eq(0)]
            cond.append(tableEventLocalContract['org_id'].isNotNull())
            cond.append(tableEventLocalContract['deleted'].eq(0))
            cond.append(tableContract['id'].inlist(contractIdList))
            cond.append(tableContract['finance_id'].eq(financeId))
            orgIdList = db.getDistinctIdList(queryTable, [tableEventLocalContract['org_id']], cond)
            if orgIdList:
                filterCond = u'Organisation.id IN (%s)'%(','.join(str(orgId) for orgId in orgIdList if orgId))
                self.cmbPayeded.setFilter(filterCond)

    def getFilterMKB(self):
        self.edtDiagnosis.clear()
        actionDateTypeValue    = self.Subsidiary.get('actionDateTypeValue', 'begDate')
        begDate                = self.Subsidiary.get('begDate', None)
        endDate                = self.Subsidiary.get('endDate', None)
        contractIdList         = self.Subsidiary.get('contractIdList', None)
        financeId              = self.Subsidiary.get('financeId', None)
        if actionDateTypeValue:
            db = QtGui.qApp.db
            tableAction               = db.table('Action')
            tableActionType           = db.table('ActionType')
            tableEvent                = db.table('Event')
            tableContract             = db.table('Contract')
            tableFinance              = db.table('rbFinance')
            tableDiagnosis            = db.table('Diagnosis')
            tableDiagnostic           = db.table('Diagnostic')
            tableRBDiagnosisType      = db.table('rbDiagnosisType')
            queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            queryTable = queryTable.innerJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
            queryTable = queryTable.innerJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
            queryTable = queryTable.innerJoin(tableRBDiagnosisType, tableDiagnostic['diagnosisType_id'].eq(tableRBDiagnosisType['id']))
            actionCond = '''EXISTS (SELECT Action.`id` FROM Action WHERE %s AND %s AND %s AND Action.`event_id`=Event.`id`)
                         ''' %(tableAction[actionDateTypeValue].dateGe(begDate),
                               tableAction[actionDateTypeValue].dateLe(endDate),
                               tableAction['deleted'].eq(0))
            cond = [actionCond, tableEvent['deleted'].eq(0)]
            if contractIdList or financeId:
                queryTable = queryTable.innerJoin(tableContract, 'Contract.`id`=IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)')
                if financeId:
                    queryTable = queryTable.innerJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
            if contractIdList:
                cond.append(tableContract['id'].inlist(contractIdList))
            if financeId:
                cond.append(tableContract['finance_id'].eq(financeId))
            cond.append('''Diagnostic.event_id = Event.id AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0
        AND (rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id
        AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1))))''')
            records = db.getRecordList(queryTable, [tableDiagnosis['MKB']], cond)
            for record in records:
                mkb = forceString(record.value('MKB'))
                if mkb and self.edtDiagnosis.findText(mkb) == -1:
                    self.edtDiagnosis.addItem(mkb)


class CClientCheckerDialog(QtGui.QDialog, CConstructHelperMixin):
    def __init__(self, clientIdList):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle(u'Список подобранных пациентов')
        # gui
        self.tblClients = CTableView(self)
        self.tblClients.setObjectName('tblClients')
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setObjectName('buttonBox')
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setObjectName('vLayout')
        self.vLayout.addWidget(self.tblClients)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)

        self.addModels('Clients', CClientsTableModel(self))
        self.setModels(self.tblClients, self.modelClients)
        self.modelClients.setIdList(clientIdList)

        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(self.tblClients, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_tblClients_doubleClicked)

        self._selectedClientId = None

    def on_tblClients_doubleClicked(self, index):
        self.accept(self.tblClients.currentItemId())

    def accept(self, selectedClientId=None):
        if not selectedClientId:
            selectedClientId = self.tblClients.currentItemId()
            if not selectedClientId:
                if len(self.modelClients.idList()) > 0:
                    selectedClientId = self.modelClients.idList()[0]
        self._selectedClientId = selectedClientId
        QtGui.QDialog.accept(self)

    def selectedClientId(self):
        return self._selectedClientId
