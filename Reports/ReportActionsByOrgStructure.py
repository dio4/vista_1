# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from operator import add

from Events.Action import CActionType
from Orgs.Utils import getOrgStructureFullName
from RefBooks.Utils import CServiceTypeModel
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportSetupByOrgStructure import Ui_ReportSetupByOrgStructureDialog
from library.DialogBase import CDialogBase
from library.Utils import forceDate, forceDouble, forceInt, forceRef, forceString, formatName, smartDict


def selectData(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    chkStatus = params.get('chkStatus', False)
    status    = params.get('status', None)
    reportType = params.get('reportType', None)
    chkPatientInfo = params.get('chkPatientInfo', False)
#   chkAllOrgStructure = params.get('chkAllOrgStructure', False)
#   contractId = params.get('contractId', None)
    contractIdList = params.get('contractIdList', [])
    financeId = params.get('typeFinanceId', None)
    chkPerson = params.get('chkPerson', False)  # Группировка по врачу
    eventTypeId = params.get('eventTypeId', None)
    personId = params.get('personId', None)     # Фильтрация по врачу
    chkAssistant = params.get('isCheckAssistant', False)
    assistantId = params.get('assistantId', None)     # Фильтрация по ассистенту
    checkPresenceInTariffs = params.get('checkPresenceInTariffs', None)     # Проверять наличие услуги в тарифах договора
    enterPost = params.get('enterPost', False)
    postId = params.get('postId', None)
    notContract = params.get('notContract', None)
    
    if reportType is None:
        return None

    db = QtGui.qApp.db

    tableAccount           = db.table('Account')
    tableAccountItem       = db.table('Account_Item')
    tableAction            = db.table('Action')
    tableActionType        = db.table('ActionType')
    tableActionTypeService = db.table('ActionType_Service')
    tablePerson            = db.table('Person')
    tableOrgStructure      = db.table('OrgStructure')
    tableContract          = db.table('Contract')
    tableContractTariff    = db.table('Contract_Tariff')
    tableClient            = db.table('Client')
    tableEvent             = db.table('Event')
    tableOrgStructureActionType = db.table('OrgStructure_ActionType')
    tableVRBPerson         = db.table('vrbPerson')

    byActionDate = params.get('byActionEndDate')
    if byActionDate:
        begDateCond = tableAction['endDate'].dateGe(begDate)
        endDateCond = tableAction['endDate'].dateLe(endDate)
    else:
        begDateCond = tableAccount['date'].dateGe(begDate)
        endDateCond = tableAccount['date'].dateLe(endDate)

    cond = [
        begDateCond,
        endDateCond,
        tableAction['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
        db.joinOr([
            tableActionTypeService['finance_id'].isNull(),
            tableActionTypeService['finance_id'].eq(tableContract['finance_id'])
        ])
    ]
    
#    if contractId:
#        cond.append(tableContract['id'].eq(contractId))
    if contractIdList and not notContract:
        cond.append(tableContract['id'].inlist(contractIdList))
    elif notContract:
        cond.append(tableContract['id'].isNull())
    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))
    if chkStatus and not status is None:
        cond.append(tableAction['status'].eq(status))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    
    
    
    if chkAssistant:
        if postId:
            cond.append(tablePerson['post_id'].eq(postId))
        if assistantId:
            cond.append(u"EXISTS(SELECT A_A.id "
                                u"       FROM Action_Assistant AS A_A"
                                u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                                u"       WHERE A_A.action_id = %s "
                                u"              AND (rbAAT.code like 'assistant'"
                                u"                      OR rbAAT.code like 'assistant2'"
                                u"                      OR rbAAT.code like 'assistant3')"
                                u"              AND A_A.person_id = %s)"  % (tableAction['id'].name(),
                                                                             assistantId))
    elif personId:
        cond.append(tableAction['person_id'].eq(personId))

        
    detailServiceTypes = params.get('detailServiceTypes', False)
    serviceTypes = params.get('serviceTypes', None)
    if detailServiceTypes and serviceTypes and len(serviceTypes) > 0:
        cond.append(tableActionType['serviceType'].inlist([str(t) for t in serviceTypes]))

    if not byActionDate:
        cond.append(tableAccountItem['deleted'].eq(0))
        cond.append(tableAccount['deleted'].eq(0))
        cond.append(tableAccountItem['tariff_id'].eq(tableContractTariff['id']))

    queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableActionTypeService, tableActionType['id'].eq(tableActionTypeService['master_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    if notContract:
        queryTable = queryTable.leftJoin(tableContract, 'Contract.`id` = Action.`contract_id`')
    else:
        queryTable = queryTable.innerJoin(tableContract, 'Contract.`id`=IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)')
    
    contractTariffJoinCond =  [tableContractTariff['master_id'].eq(tableContract['id']),
                               tableContractTariff['service_id'].eq(tableActionTypeService['service_id'])]
    
    if checkPresenceInTariffs and not notContract:
        queryTable = queryTable.innerJoin(tableContractTariff, contractTariffJoinCond)
    else:
        queryTable = queryTable.leftJoin(tableContractTariff, contractTariffJoinCond)
    
    
    if chkPatientInfo:
        queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

    if chkAssistant:
        queryTable = queryTable.leftJoin(tablePerson, 
                                         "%s IN (SELECT Action_Assistant.person_id )"\
                                         "       FROM Action_Assistant "
                                         "             INNER JOIN rbActionAssistantType AS aType ON aType.id = Action_Assistant.assistantType_id"
                                         "       WHERE Action_Assistant.action_id = %s "
                                         "             AND aType.code IN ('assistant', 'assistant2', 'assistant3')"
                                         % (tablePerson['id'].name(), tableAction['id'])
        )
    else:
        queryTable = queryTable.leftJoin(tablePerson, 
                                         tablePerson['id'].eq(tableAction['person_id']))

    if not byActionDate:
        queryTable = queryTable.innerJoin(tableAccountItem, tableAction['id'].eq(tableAccountItem['action_id']))
        queryTable = queryTable.innerJoin(tableAccount, tableAccountItem['master_id'].eq(tableAccount['id']))

    if reportType == 0:
        queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))
    elif reportType == 1:
        queryTable = queryTable.leftJoin(tableOrgStructureActionType,
            tableOrgStructureActionType['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.leftJoin(tableOrgStructure,
            tableOrgStructure['id'].eq(tableOrgStructureActionType['master_id']))
    else:
        return None
    
    fields = [
              tableAction['modifyDatetime'].name(),
              tableAction['endDate'].name(),
              tableAction['id'].name(),
              tableActionType['code'].name(),
              tableActionType['name'].name(),
              tableAction['amount'].name() if byActionDate else tableAccountItem['amount'].name(),
              tableOrgStructure['id'].alias('orgStructureId'),
              tableOrgStructure['name'].alias('orgStructureName'),
              tableContractTariff['price'].name()]
    
    if chkPerson:
        queryTable = queryTable.leftJoin(tableVRBPerson, tableVRBPerson['id'].eq(tablePerson['id']))
        fields.extend([tableVRBPerson['id'].alias('personId'),
                       tableVRBPerson['name'].alias('personName')])
        if enterPost:
            tablePost = db.table('rbPost')
            queryTable = queryTable.leftJoin(tablePost, tablePost['id'].eq(tablePerson['post_id']))
            fields.append(tablePost['name'].alias('personPost'))

    if detailServiceTypes:
        fields.append(tableActionType['serviceType'].name())

    if chkPatientInfo:
        tableActionLastMoving = db.table('Action').alias('ActionLastMoving')
        queryTable = queryTable.leftJoin(tableActionLastMoving, '''ActionLastMoving.id = (SELECT min(act.id)
                                                                                          FROM Action act
                                                                                               INNER JOIN ActionType actType ON actType.id = act.actionType_id
                                                                                          WHERE Event.id = act.event_id
                                                                                                AND actType.flatCode = 'moving'
                                                                                                AND act.endDate >= Action.endDate
                                                                                                AND act.deleted = 0
                                                                                                AND actType.deleted = 0)''')
        clientFields = [tableClient['lastName'].name(),
                        tableClient['firstName'].name(),
                        tableClient['patrName'].name()]
        fields.extend(clientFields)
        fields.append(tableClient['id'].alias('clientId'))
        fields.append(tableActionLastMoving['MKB'].alias('actionMKB'))
        order = clientFields
    else:
        order = [tableAction['begDate'].name()]

    stmt = db.selectStmt(queryTable, fields, cond,  order = order)
    query = db.query(stmt)
    return query

docServiceTypeName = [
    u'прочие',
    u'консультация',
    u'консультация',
    u'процедуры',
    u'операция',
    u'анализы',
    u'лечение',
    u'расходники',
    u'оплата палат',
]


class CReportActionsByOrgStructure(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по отделениям')
        self.resetHelpers()
        self._orgStructureHelperModel = None

    def resetHelpers(self):
        self._mapRowValues = {}
        self._mapOrgStructureIdToFullName = {}
        self._mapPersonIdToName = {}
        self._actualOrgStructureIdListByStrongOrgStructure = []


    def getSetupDialog(self, parent):
        result = CSetupReport(parent)
        result.setSetupByOrgStructureVisible(True)
        result.setSetupByEventTypeVisible(True)
        result.setSetupByPersonVisible(True)
        result.setStrongOrgStructureVisible(True)
        result.setChkPersonVisible(True)
        result.setTitle(self.title())
        result.setVisibleAssistant(True)
        result.setServiceTypesVisible(True)
        self._orgStructureHelperModel = result.getOrgStructureModel()
        return result


    def build(self, params):

        def printAll(reportData, indent):
            totalByReport = printOrgStructures(reportData, indent)
            i = table.addRow()
            table.setText(i, 0, u'Итого', charFormat=boldChars)
            table.setText(i, 6 if chkPatientInfo else 3, totalByReport[0], charFormat=boldChars)
            table.setText(i, 7 if chkPatientInfo else 4, totalByReport[1], charFormat=boldChars)
            table.mergeCells(i, 0, 1, 6 if chkPatientInfo else 3)

        def printOrgStructures(reportData, indent):
            total = [0, 0]
            orgStructures = reportData.keys()
            orgStructures.sort()
            for orgStructure in orgStructures:
                i = table.addRow()
                table.setText(i, 0, self._mapOrgStructureIdToFullName[orgStructure], charFormat=boldChars, blockFormat=CReportBase.AlignLeft)
                table.mergeCells(i, 0, 1, columnCount)

                totalByOrgStructure = printDoctors(reportData[orgStructure], indent)
                total = map(add, total, totalByOrgStructure)

                if not params.get('isCheckAssistant'):
                    i = table.addRow()
                    table.setText(i, 0, u'Итого по отделению', charFormat=boldChars)
                    table.setText(i, 6 if chkPatientInfo else 3, totalByOrgStructure[0], charFormat=boldChars)
                    table.setText(i, 7 if chkPatientInfo else 4, totalByOrgStructure[1], charFormat=boldChars)
                    table.mergeCells(i, 0, 1, 6 if chkPatientInfo else 3)
            return total

        def printDoctors(reportData, indent):
            total = [0, 0]
            doctors = reportData.keys()
            doctors.sort()
            for person in doctors:
                if chkPerson:
                    i = table.addRow()
                    table.setText(i, 0, ', '.join([self._mapPersonIdToName[person]['name'], self._mapPersonIdToName[person]['post']]) if enterPost else self._mapPersonIdToName[person], charFormat=boldItalicChars, blockFormat=CReportBase.AlignLeft)
                    table.mergeCells(i, 0, 1, columnCount)

                totalByPerson = printServiceTypes(reportData[person], indent + ('    ' if detailServiceTypes else ''))
                total = map(add, total, totalByPerson)

                if not params.get('isCheckAssistant') and chkPerson:
                    i = table.addRow()
                    table.setText(i, 0, u'Итого по врачу', charFormat=boldItalicChars)
                    table.setText(i, 6 if chkPatientInfo else 3, totalByPerson[0], charFormat=boldItalicChars)
                    table.setText(i, 7 if chkPatientInfo else 4, totalByPerson[1], charFormat=boldItalicChars)
                    table.mergeCells(i, 0, 1, 6 if chkPatientInfo else 3)
            return total

        def printServiceTypes(reportData, indent):
            total = [0, 0]
            serviceTypes = reportData.keys()
            serviceTypes.sort()
            for serviceType in serviceTypes:
                if detailServiceTypes:
                    i = table.addRow()
                    table.setText(i, 0, indent + u'Вид услуги: ' + docServiceTypeName[serviceType], charFormat=boldChars, blockFormat=CReportBase.AlignLeft)
                    table.mergeCells(i, 0, 1, columnCount)

                totalByServiceType = printClients(reportData[serviceType], indent)
                total = map(add, total, totalByServiceType)

                if detailServiceTypes:
                    i = table.addRow()
                    table.setText(i, 0, u'Итого по виду услуги', charFormat=boldItalicChars)
                    table.setText(i, 6 if chkPatientInfo else 3, totalByServiceType[0], charFormat=boldItalicChars)
                    table.setText(i, 7 if chkPatientInfo else 4, totalByServiceType[1], charFormat=boldItalicChars)
                    table.mergeCells(i, 0, 1, 6 if chkPatientInfo else 3)
            return total

        def printClients(reportData, indent):
            total = [0, 0]
            clients = reportData.keys()
            clients.sort()
            for client in clients:
                totalByClient = printServices(reportData[client], indent)
                total = map(add, total, totalByClient)
            return total

        def printServices(reportData, indent):
            total = [0, 0]
            actionInfoEntries = reportData.keys()
            actionInfoEntries.sort()
            for actionInfoEntry in actionInfoEntries:
                i = table.addRow()
                table.setText(i, 0, reportData[actionInfoEntry].number)
                values = reportData[actionInfoEntry].values
                total = map(add, total, values[-2:])
                for idx, value in enumerate(values):
                    table.setText(i, idx + 1, value)
            return total

        self.resetHelpers()
        chkPatientInfo = params.get('chkPatientInfo', False)
        chkPerson = params.get('chkPerson', False)
        detailServiceTypes = params.get('detailServiceTypes', False)
        enterPost = params.get('enterPost', False)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        if not query:
            return doc
        self.makeStructAction(query, params)

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('%2',
                        [u'№'], CReportBase.AlignRight),
                        ('%5',
                        [u'Код услуги'], CReportBase.AlignLeft),
                        ('%10',
                        [u'Наименование услуги'], CReportBase.AlignLeft),
                        ('%2',
                        [u'Количество'], CReportBase.AlignLeft),
                        ('%5',
                        [u'Цена'], CReportBase.AlignLeft)
                        ]

        if chkPatientInfo:
            tableColumns.insert(3, ('5%',
                                    [u'МКБ'], CReportBase.AlignCenter))
            tableColumns.insert(3, ('%10',
                                    [u'Пациент'], CReportBase.AlignLeft))
            tableColumns.insert(1, ('%5',
                                    [u'Дата исполнения'], CReportBase.AlignLeft))

        table = createTable(cursor, tableColumns)
        columnCount = len(tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        printAll(self._mapRowValues, '')

        return doc


    def makeStructAction(self, query, params):
        # chkAllOrgStructure:: если True - при структурировании по подразделениям к которым относится действие, 
        # действие может относится ко многим подразделениям, а если False мы учитываем только первое.
        chkAllOrgStructure   = params.get('chkAllOrgStructure', False)
        chkPatientInfo       = params.get('chkPatientInfo', False)
        chkOrgStructure      = params.get('chkOrgStructure', False)
        chkPerson            = params.get('chkPerson', False)
        detailServiceTypes   = params.get('detailServiceTypes', False)
        strongOrgStructureId = params.get('orgStructureId', None)
        enterPost            = params.get('enterPost', False)
        existsOrgStructureActions = []
        while query.next():
            record = query.record()

            modifyDatetime   = forceDate(record.value('modifyDatetime'))
            endDate          = forceDate(record.value('endDate'))
            actionId         = forceRef(record.value('id'))
            actionTypeCode   = forceString(record.value('code'))
            actionTypeName   = forceString(record.value('name'))
            amount           = forceInt(record.value('amount'))
            orgStructureId   = forceRef(record.value('orgStructureId'))
#            orgStructureName = forceString(record.value('orgStructureName'))
            price            = forceDouble(record.value('price'))

            if chkAllOrgStructure:
                if (orgStructureId, actionId) in existsOrgStructureActions:
                    continue
                existsOrgStructureActions.append((orgStructureId, actionId))
            else:
                if actionId in existsOrgStructureActions:
                    continue
                existsOrgStructureActions.append(actionId)

            result, orgStructureId = self.orgStructureFilterByParams(chkOrgStructure,
                                                                     strongOrgStructureId,
                                                                     orgStructureId)
            if not result:
                continue

            fullOrgStructureName = self._mapOrgStructureIdToFullName.get(orgStructureId, None)
            if not fullOrgStructureName:
                if not orgStructureId:
                    if chkOrgStructure:
                        fullOrgStructureName = u'Головное подразделение'
                    else:
                        fullOrgStructureName = u'Подразделение не определено'
                else:
                    fullOrgStructureName = getOrgStructureFullName(orgStructureId)
                self._mapOrgStructureIdToFullName[orgStructureId] = fullOrgStructureName

            actionValues = smartDict()
            actionValues.actionId         = actionId
            actionValues.orgStructureId   = orgStructureId
            actionValues.number           = 0
            values = [actionTypeCode, actionTypeName, amount, price*amount]

            if chkPatientInfo:
                clientName = formatName(
                                      record.value('lastName'),
                                      record.value('firstName'),
                                      record.value('patrName')
                                     )
                clientId = forceRef(record.value('clientId'))
                actionMKB = forceString(record.value('actionMKB'))
                endDate = endDate if endDate.isValid() else modifyDatetime

                values.insert(2, actionMKB)
                values.insert(2, clientName)
                values.insert(0, forceString(endDate))


            if chkPerson:
                personName = forceString(record.value('personName'))
                personId = forceString(record.value('personId'))
                self._mapPersonIdToName[personId] = personName
                if enterPost:
                    personPost = forceString(record.value('personPost'))
                    self._mapPersonIdToName[personId] = {}
                    self._mapPersonIdToName[personId]['name'] = personName
                    self._mapPersonIdToName[personId]['post'] = personPost

            if detailServiceTypes:
                serviceType = forceInt(record.value('serviceType'))

            actionValues.values = values

            orgStructureDict = self._mapRowValues.setdefault(orgStructureId, {})
            personDict = orgStructureDict.setdefault(personId if chkPerson else None, {})
            serviceTypeDict = personDict.setdefault(serviceType if detailServiceTypes else None, {})
            clientDict = serviceTypeDict.setdefault(clientId if chkPatientInfo else None, {})
            existActionValues = clientDict.setdefault((actionTypeCode, actionTypeName), actionValues)

            if existActionValues != actionValues:
                existActionValues.values[-2] += actionValues.values[-2]
                existActionValues.values[-1] += actionValues.values[-1]

        # set numbers within each orgStructure unit
        self.fillOrgStructureRows()

    def fillOrgStructureRows(self):
        def sortedWalk(obj):
            if isinstance(obj, smartDict):
                orgStructureRow[0] += 1
                obj.number = orgStructureRow[0]
            elif isinstance(obj, dict):
                keys = obj.keys()
                keys.sort()
                for key in keys:
                    sortedWalk(obj[key])
            else:
                pass

        for obj in self._mapRowValues.values():
            orgStructureRow = [0]
            sortedWalk(obj)

    def orgStructureFilterByParams(self, chkOrgStructure, strongOrgStructureId, orgStructureId):
        if chkOrgStructure:
            if strongOrgStructureId:
                if not self._actualOrgStructureIdListByStrongOrgStructure:
                    predicatObject = CPredicat(condId=strongOrgStructureId)
                    strongOrgStructureItemIndex = self._orgStructureHelperModel.findItem(predicatObject.eq)
                    if strongOrgStructureItemIndex:
                        strongOrgStructureItem = strongOrgStructureItemIndex.internalPointer()
                        self._actualOrgStructureIdListByStrongOrgStructure = strongOrgStructureItem.getItemIdList()
                if orgStructureId in self._actualOrgStructureIdListByStrongOrgStructure:
                    return True, strongOrgStructureId
                else:
                    return False, strongOrgStructureId
            else:
                return True, strongOrgStructureId
        return True, orgStructureId


    def getDescription(self, params):
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        chkStatus = params.get('chkStatus', False)
        status    = params.get('status', None)
        reportType = params.get('reportType', None)
        chkAllOrgStructure = params.get('chkAllOrgStructure', False)
        contractText = params.get('contractText', None)
        financeText = params.get('financeText', None)
        detailServiceTypes = params.get('detailServiceTypes', None)
        serviceTypes = params.get('serviceTypes', None)

        rows = []

        if begDate:
            rows.append(u'Начальная дата периода: %s'%forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s'%forceString(endDate))
        if chkStatus and status is not None:
            rows.append(u'Статус: %s' % CActionType.retranslateClass(False).statusNames[status])
        if reportType is not None:
            rows.append(u'Отчет по: %s' %[u'отделениям выполнившего действие врача',
                                          u'отделениям за которым закрепленно действие'][reportType])
        if chkAllOrgStructure:
            rows.append(u'Действия связаны со всеми возможными подразделениями')
        if financeText:
            rows.append(u'Тип финансирования: %s' % financeText)
        if contractText:
            rows.append(u'Контракт: %s' % contractText)
        if detailServiceTypes and serviceTypes:
            rows.append(u'Типы услуг: ' + u', '.join(map(lambda x: docServiceTypeName[x], serviceTypes)))
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

        self.addModels('ServiceType', CServiceTypeModel(1, 10))
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
        self.chkAssistant.setVisible(value)
        self.lblAssistant.setVisible(value)
        self.cmbAssistant.setVisible(value)
        self.lblAssistantPost.setVisible(value)
        self.cmbAssistantPost.setVisible(value)
    

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

#        self.cmbContract.setValue(params.get('contractId', None))
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

    def params(self):
        params = {}

        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['byActionEndDate'] = self.rbtnByActionEndDate.isChecked()
        params['chkStatus'] = self.chkStatus.isChecked()
        params['status']    = self.cmbStatus.currentIndex()

#        params['contractId'] = self.cmbContract.value()
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

#    @QtCore.pyqtSlot(int)
#    def on_cmbFinance_currentIndexChanged(self, index):
#        self.cmbContract.setFinanceId(self.cmbFinance.value())

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))
        self.cmbAssistant.setEndDate(QtCore.QDate(date))
#         self.cmbContract.setBegDate(date)
#
#    @QtCore.pyqtSlot(QDate)
#    def on_edtEndDate_dateChanged(self, date):
#        self.cmbContract.setEndDate(date)

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
            stringInfo = u'Группмровать по врачу'
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



# ####################################

#TODO: atronah: мб лучше лямбдой (Т.е вместо использования в виде "predicatObject.eq" писать "lambda item: item.id == mySomeFixedId")?
# И пока мне мало понятно, почему не использовать вместо findItem(predicat) функцию той же модели findItemId(id)
class CPredicat(object):
    def __init__(self, condId):
        self._condId = condId
    def eq(self, item):
        return item._id == self._condId
