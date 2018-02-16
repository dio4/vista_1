# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from library.crbcombobox    import CRBModelDataCache
from library.Utils          import forceDate, forceRef, forceString, formatName

from Orgs.Utils             import getOrgStructureFullName

from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_StationaryAnalyticsSetup import Ui_StationaryAnalyticsSetupDialog


# форма 222,216

def selectData(params):
    begDate                 = params.get('begDate', None)
    endDate                 = params.get('endDate', None)
    medicalHistoryTypeIndex = params.get('medicalHistoryTypeIndex', 0)
    ambCardType             = params.get('ambCardType', None)
    diagType                = params.get('diagType', 0)
    financeId               = params.get('financeId', None)
    chkQuotaClass           = params.get('chkQuotaClass', False)
    quotaClass              = params.get('quotaClass', 0)
    quotaTypeId             = params.get('quotaTypeId', None)

    db = QtGui.qApp.db

    tableClient                     = db.table('Client')
    tableEvent                      = db.table('Event')
    tableEventType                  = db.table('EventType')
    tableMedicalAidType             = db.table('rbMedicalAidType')
    tableContract                   = db.table('Contract')
    tableClientIdentification       = db.table('ClientIdentification')
    tableClientQuoting              = db.table('Client_Quoting')
    tableQuotaType                  = db.table('QuotaType')
    tableDiagnostic                 = db.table('Diagnostic')
    tableDiagnosis                  = db.table('Diagnosis')
    tableFinance                    = db.table('rbFinance')
    tableOrgStructure               = db.table('OrgStructure')
    tableActionType                 = db.table('ActionType')
    tableActionMoving               = db.table('Action').alias('ActionMoving')
    tableActionLeaved               = db.table('Action').alias('ActionLeaved')
    tableActionProperty             = db.table('ActionProperty')
    tableActionPropertyType         = db.table('ActionPropertyType')
    tableActionPropertyOrgStructure = db.table('ActionProperty_OrgStructure')
    tableClientAddress              = db.table('ClientAddress')
    tableAddress                    = db.table('Address')
    tableAddressHouse               = db.table('AddressHouse')

    tableActionReceivedForQuota          = db.table('Action').alias('ActionReceived')
    tableActionTypeReceivedForQuota      = db.table('ActionType').alias('ActionTypeReceived')
    tableActionPropertyForQuota          = db.table('ActionProperty').alias('ActionPropertyForQuota')
    tableActionPropertyTypeForQuota      = db.table('ActionPropertyType').alias('ActionPropertyTypeForQuota')
    tableActionPropertyClientQuoting = db.table('ActionProperty_Client_Quoting').alias('ActionPropertyClientQuoting')


    queryTable = tableClient.innerJoin(tableEvent, tableEvent['client_id'].eq(tableClient['id']))

    queryTable = queryTable.innerJoin( tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    queryTable = queryTable.leftJoin(  tableMedicalAidType, tableMedicalAidType['id'].eq(tableEventType['medicalAidType_id']))
#    queryTable = queryTable.innerJoin( tableContract, tableContract['id'].eq(tableEvent['contract_id']))
#    queryTable = queryTable.innerJoin( tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
    queryTable = queryTable.innerJoin( tableDiagnostic, tableDiagnostic['event_id'].eq(tableEvent['id']))

    if diagType == 0:
        diagTypeCode = '7'
        diagnosisJoinCond = [tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']),
                         tableDiagnostic['diagnosisType_id'].eq(forceRef(db.translate('rbDiagnosisType', 'code',
                                                                                     diagTypeCode, 'id')))]
        queryTable = queryTable.leftJoin(tableDiagnosis, db.joinAnd(diagnosisJoinCond))
    elif diagType == 1:
        diagTypeCode = '1'
        diagnosisJoinCond = [tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']),
                         tableDiagnostic['diagnosisType_id'].eq(forceRef(db.translate('rbDiagnosisType', 'code',
                                                                                     diagTypeCode, 'id')))]
        queryTable = queryTable.innerJoin(tableDiagnosis, db.joinAnd(diagnosisJoinCond))
    else:
        return QtSql.QSqlQuery()

    if ambCardType:
        clientIdenticationJoinCond = [tableClientIdentification['client_id'].eq(tableClient['id']),
                                      tableClientIdentification['accountingSystem_id'].eq(ambCardType)]
        queryTable = queryTable.leftJoin(tableClientIdentification, db.joinAnd(clientIdenticationJoinCond))



    if diagType == 0:
        tableAction = tableActionMoving
        orgStructurePropertyTypeName = u'Отделение пребывания'
        actionTypeIdList = db.getIdList('ActionType', 'id', 'flatCode LIKE \'moving%\' AND deleted=0')
        actionJoinDateCond = [tableAction['begDate'].dateLe(endDate),
                              tableAction['begDate'].dateGe(begDate),
                              tableAction['deleted'].eq(0),
                              db.joinOr(
                                        [tableAction['endDate'].dateGe(endDate),
                                         tableAction['endDate'].isNull()
                                        ]
                                       )
                             ]
    elif diagType == 1:
        tableAction = tableActionLeaved
        orgStructurePropertyTypeName = u'Отделение'
        actionTypeIdList = db.getIdList('ActionType', 'id', 'flatCode LIKE \'leaved%\' AND deleted=0')
        actionJoinDateCond = [tableAction['begDate'].dateLe(endDate),
                              tableAction['begDate'].dateGe(begDate),
                              tableAction['endDate'].dateLe(endDate),
                              tableAction['endDate'].isNotNull(),
                              tableAction['deleted'].eq(0)
                             ]
    else:
        return QtSql.QSqlQuery()

    actionJoinCond = [tableAction['event_id'].eq(tableEvent['id']),
                      tableAction['actionType_id'].inlist(actionTypeIdList),
                     ]
    queryTable = queryTable.innerJoin(tableAction, db.joinAnd(actionJoinCond))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))

    actionPropertyTypeJoinCond = [tableActionPropertyType['actionType_id'].eq(tableActionType['id']),
                                  tableActionPropertyType['name'].eq(orgStructurePropertyTypeName)]
    queryTable = queryTable.leftJoin(tableActionPropertyType, db.joinAnd(actionPropertyTypeJoinCond))

    actionPropertyJoinCond = [tableActionProperty['action_id'].eq(tableAction['id']),
                              tableActionProperty['type_id'].eq(tableActionPropertyType['id'])]
    queryTable = queryTable.leftJoin(tableActionProperty, db.joinAnd(actionPropertyJoinCond))


    queryTable = queryTable.leftJoin(tableActionPropertyOrgStructure,
                                      tableActionPropertyOrgStructure['id'].eq(tableActionProperty['id']))

    queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableActionPropertyOrgStructure['value']))

    if diagType == 0:
    # квота при поступлении
        actionTypeReceivedIdList = db.getIdList('ActionType', 'id', 'flatCode LIKE \'received%\' AND deleted=0')
        actionReceivedJoinCond = [tableActionReceivedForQuota['event_id'].eq(tableEvent['id']),
                                  tableActionReceivedForQuota['actionType_id'].inlist(actionTypeReceivedIdList),
                                 ]
        queryTable = queryTable.innerJoin(tableActionReceivedForQuota, db.joinAnd(actionReceivedJoinCond))
        queryTable = queryTable.innerJoin(tableActionTypeReceivedForQuota,
                                          tableActionTypeReceivedForQuota['id'].eq(tableActionReceivedForQuota['actionType_id']))
        tableActionForQuota = tableActionReceivedForQuota
        tableActionTypeForQuota = tableActionTypeReceivedForQuota

    # Квота при выписке
    elif diagType == 1:
        tableActionForQuota = tableAction
        tableActionTypeForQuota = tableActionType
    else:
        return QtSql.QSqlQuery()


    actionPropertyTypeForQuotaJoinCond = [tableActionPropertyTypeForQuota['actionType_id'].eq(tableActionTypeForQuota['id']),
                                          tableActionPropertyTypeForQuota['name'].eq(u'Квота')]
    queryTable = queryTable.leftJoin(tableActionPropertyTypeForQuota, db.joinAnd(actionPropertyTypeForQuotaJoinCond))

    actionPropertyForQuotaJoinCond = [tableActionPropertyForQuota['action_id'].eq(tableActionForQuota['id']),
                                      tableActionPropertyForQuota['type_id'].eq(tableActionPropertyTypeForQuota['id'])]
    queryTable = queryTable.leftJoin(tableActionPropertyForQuota, db.joinAnd(actionPropertyForQuotaJoinCond))

    queryTable = queryTable.leftJoin(tableActionPropertyClientQuoting,
                                     tableActionPropertyClientQuoting['id'].eq(tableActionPropertyForQuota['id']))

    queryTable = queryTable.leftJoin(tableClientQuoting,
                                     tableClientQuoting['id'].eq(tableActionPropertyClientQuoting['value']))

    queryTable = queryTable.leftJoin(tableQuotaType,
                                     tableQuotaType['id'].eq(tableClientQuoting['quotaType_id']))


    queryTable = queryTable.leftJoin(tableClientAddress, tableClientAddress['id'].name()+'=getClientLocAddressId(Client.`id`)')
    queryTable = queryTable.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
    queryTable = queryTable.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id']))


    order = [tableClient['lastName'].name(),
             tableClient['firstName'].name(),
             tableClient['patrName'].name()]

    fields = order + ['getClientLocAddress(Client.`id`) AS clientAddress',
                      tableClient['id'].alias('clientId'),
                      tableEvent['id'].alias('eventId'),
                      tableDiagnosis['MKB'].name(),
                      #tableFinance['name'].alias('financeType'),
                      tableOrgStructure['name'].alias('orgStructureName'),
                      tableOrgStructure['id'].alias('orgStructureId'),
                      tableAddressHouse['KLADRCode'].name(),
                      tableEvent['setDate'].alias('eventSetDate'),
                      tableEvent['execDate'].alias('eventExecDate'),
                      tableMedicalAidType['code'].alias('medicalAidTypeCode'),
                      tableQuotaType['code'].alias('quotaTypeCode')]
    if ambCardType:
        fields.append(tableClientIdentification['identifier'].alias('ambCard'))
    else:
        fields.append(tableClient['id'].alias('ambCard'))

    # взависимости от типа диагноза tableActionForQuota будет либо действием "поступление"
    # либо дейтсвием "выписка"
    fields.append(tableActionForQuota['endDate'].alias('needDateForReport'))

    if medicalHistoryTypeIndex == 0:
        fields.append(tableEvent['id'].alias('medicalHistory'))
    else:
        fields.append(tableEvent['externalId'].alias('medicalHistory'))

    cond = list(actionJoinDateCond)
    cond.append(tableAction['deleted'].eq(0))
    cond.append(tableEvent['deleted'].eq(0))

    if diagType == 0:
        if QtGui.qApp.defaultHospitalBedFinanceByMoving() == 2:
            tableAction = tableActionMoving
            tableRBFinanceBC = db.table('rbFinance').alias('rbFinanceByContract')
            fields.append(u'IF(ActionMoving.finance_id IS NOT NULL AND ActionMoving.deleted=0, rbFinance.name, IF(Contract.id IS NOT NULL AND Contract.deleted=0, rbFinanceByContract.name, NULL)) AS nameFinance')
            if financeId:
                cond.append('''((ActionMoving.finance_id IS NOT NULL AND ActionMoving.deleted=0 AND ActionMoving.finance_id = %s) OR (Contract.id IS NOT NULL AND Contract.deleted=0 AND Contract.finance_id = %s))'''%(str(financeId), str(financeId)))
                queryTable = queryTable.innerJoin(tableFinance, tableFinance['id'].eq(tableAction['finance_id']))
                queryTable = queryTable.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.innerJoin(tableRBFinanceBC, tableRBFinanceBC['id'].eq(tableContract['finance_id']))
            else:
                queryTable = queryTable.leftJoin(tableFinance, tableFinance['id'].eq(tableAction['finance_id']))
                queryTable = queryTable.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
                queryTable = queryTable.leftJoin(tableRBFinanceBC, tableRBFinanceBC['id'].eq(tableContract['finance_id']))
        elif QtGui.qApp.defaultHospitalBedFinanceByMoving() == 1:
            tableAction = tableActionMoving
            fields.append(tableFinance['name'].alias('financeType'))
            if financeId:
                cond.append('''(ActionMoving.finance_id IS NOT NULL AND ActionMoving.deleted=0 AND ActionMoving.finance_id = %s)'''%(str(financeId)))
                queryTable = queryTable.innerJoin(tableFinance, tableFinance['id'].eq(tableAction['finance_id']))
            else:
                queryTable = queryTable.leftJoin(tableFinance, tableFinance['id'].eq(tableAction['finance_id']))
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
    elif diagType == 1 and (QtGui.qApp.defaultHospitalBedFinanceByMoving() in [0, 2]):
        fields.append(tableFinance['name'].alias('financeType'))
        if financeId:
            queryTable = queryTable.innerJoin( tableContract, tableContract['id'].eq(tableEvent['contract_id']))
            queryTable = queryTable.innerJoin( tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
            cond.append(tableContract['deleted'].eq(0))
            cond.append(tableContract['finance_id'].eq(financeId))
        else:
            queryTable = queryTable.leftJoin( tableContract, tableContract['id'].eq(tableEvent['contract_id']))
            queryTable = queryTable.leftJoin( tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
    else:
        return QtSql.QSqlQuery()

    if chkQuotaClass and (not quotaClass is None):
        cond.append(tableQuotaType['class'].eq(quotaClass))
    if quotaTypeId:
        quotaTypeIdList = getChildrenIdList([quotaTypeId])
        cond.append(tableQuotaType['id'].inlist(quotaTypeIdList))


    stmt = db.selectStmt(queryTable, fields, cond,  order = order)
#    print stmt
    return db.query(stmt)


def getChildrenIdList(idList):
    data = CRBModelDataCache.getData('QuotaType', False)
    db = QtGui.qApp.db
    table = db.table('QuotaType')
    result = idList
    while bool(idList):
        tmpResult = []
        for id in idList:
            code = data.getCodeById(id)
#            code = forceString(db.translate(table, 'id', id, 'code'))
            cond = [table['group_code'].eq(code)]
            tmpResult.extend(db.getIdList(table, 'id', cond))
        result.extend(tmpResult)
        idList = tmpResult
    return result

class CAnalyticsReportHospitalizedClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по пациентам')
        self.resetHelpers()

    def resetHelpers(self):
        self._existEventClients = []
        self._mapOrgStructureToClientValues = {}
        self._orgStructureIdToFullName = {}
        self._mapClientIdToQuotingIdList = {}
        self._mapQuotingIdToQuotaTypeCode = {}

    def getSetupDialog(self, parent):
        result = CStationaryAnalyticsSetupDialog(parent)
        result.setHospitalizedWidgetsVisible(True)
        result.setQuotingWidgetsVisible(True)
        result.setTitle(self.title())
        return result

    def build(self, params):
        self.resetHelpers()
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.makeStruct(query)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [('%2',
                        [u'№'], CReportBase.AlignRight),
                        ('%5',
                        [u'Карта амбулаторного больного'], CReportBase.AlignLeft),
                        ('%15',
                        [u'Пациент'], CReportBase.AlignLeft),
                        ('%7',
                        [u'История болезни'], CReportBase.AlignLeft),
                        ('%10',
                        [u'Регион'], CReportBase.AlignLeft),
                        ('%7',
                        [u'DS'], CReportBase.AlignLeft),
                        ('%7',
                        [u'В/Т'], CReportBase.AlignLeft),
                        ('%7',
                        [u'Источник финансирования'], CReportBase.AlignLeft)
                        ]

        diagType = params.get('diagType', 0)
        if diagType == 0:
            tableColumns.append(('%7', [u'Дата госпитализации'], CReportBase.AlignLeft))
        else:
            tableColumns.append(('%7', [u'Дата выписки'], CReportBase.AlignLeft))

        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        keys = self._mapOrgStructureToClientValues.keys()
        iClient = 0
        daysCount = 0
        keys.sort(key=lambda item: item[0])
        keys.reverse()
        for key in keys:
            orgStructureName = key[1]
            valuesList = self._mapOrgStructureToClientValues[key]
            row = table.addRow()
            table.setText(row, 0, orgStructureName, charFormat=boldChars)
            table.mergeCells(row, 0, 1, 8)
            locClientCount = 0
            locDaysCount = 0
            for values in valuesList:
                locClientCount += 1
                iClient += 1
                row = table.addRow()
                table.setText(row, 0, iClient)
                for itemIdx, valuesItem in enumerate(values[1:-1]):
                    table.setText(row, itemIdx+1, valuesItem)
                locDaysCount += values[-1]
            row = table.addRow()
            table.setText(row, 0,
                          u'Итого по отделению: пациентов - %d, койко дней - %d'%(locClientCount, locDaysCount),
                          charFormat=boldChars)
            table.mergeCells(row, 0, 1, 8)
            daysCount += locDaysCount
        row = table.addRow()
        table.setText(row, 0,
                      u'Итого: пациентов - %d, койко дней - %d'%(iClient, daysCount),
                      charFormat=boldChars)
        table.mergeCells(row, 0, 1, 8)

        return doc

    def makeStruct(self, query):
#        print query.size()
        while query.next():
            record = query.record()

            clientId         = forceRef(record.value('clientId'))
            fio              = formatName(
                                          record.value('lastName'),
                                          record.value('firstName'),
                                          record.value('patrName')
                                          )
            eventId            = forceRef(record.value('eventId'))
            clientAddress      = forceString(record.value('clientAddress'))
            KLADRCode          = forceString(record.value('KLADRCode'))
            mkb                = forceString(record.value('MKB'))
            financeType        = forceString(record.value('financeType'))
            orgStructureId     = forceRef(record.value('orgStructureId'))
            medicalHistory     = forceString(record.value('medicalHistory'))
            ambCard            = forceString(record.value('ambCard'))
            medicalAidTypeCode = forceString(record.value('medicalAidTypeCode'))
            eventSetDate       = forceDate(record.value('eventSetDate'))
            eventExecDate      = forceDate(record.value('eventExecDate'))
            quotaTypeCode      = forceString(record.value('quotaTypeCode'))
            needDateForReport  = forceString(record.value('needDateForReport'))


            if eventExecDate.isValid():
                if eventExecDate > QtCore.QDate.currentDate():
                    topDate = QtCore.QDate.currentDate()
                else:
                    topDate = eventExecDate
            else:
                topDate = QtCore.QDate.currentDate()

            dCount = eventSetDate.daysTo(topDate)
            if medicalAidTypeCode in ['1', '2', '3']:
                if dCount == 0:
                    dCount = 1
            else:
                dCount += 1

            if (clientId, eventId) in self._existEventClients:
                continue
            self._existEventClients.append((clientId, eventId))
            fullOrgStructureName = self._orgStructureIdToFullName.get(orgStructureId, None)
            if not fullOrgStructureName:
                if not orgStructureId:
                    fullOrgStructureName = u'Подразделение не определено'
                else:
                    fullOrgStructureName = getOrgStructureFullName(orgStructureId)
                self._orgStructureIdToFullName[orgStructureId] = fullOrgStructureName
            key = (orgStructureId, fullOrgStructureName)
            orgStructureValueList = self._mapOrgStructureToClientValues.setdefault(key, [])
            orgStructureValue = [clientId, ambCard, fio, medicalHistory,
                                 KLADRCode+', '+clientAddress, mkb, quotaTypeCode, financeType,
                                 needDateForReport, dCount]
            orgStructureValueList.append(orgStructureValue)

    def getDescription(self, params):
        begDate            = params.get('begDate', None)
        endDate            = params.get('endDate', None)
        diagType = params.get('diagType', 0)
        financeId = params.get('financeId', None)
        financeText = params.get('financeText', None)
        chkQuotaClass = params.get('chkQuotaClass', False)
        quotaClass = params.get('quotaClass', None) if chkQuotaClass else None
        quotaTypeId = params.get('quotaTypeId', False)

        rows = []

        if diagType == 0:
            rows.append(u'Предварительный диагноз')
        elif diagType == 1:
            rows.append(u'Заключительный диагноз')

        if financeId:
            rows.append(u'Тип финансирования: %s' % financeText)
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


class CStationaryAnalyticsSetupDialog(QtGui.QDialog, Ui_StationaryAnalyticsSetupDialog):
    _order = 'isObsolete, code'

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbAmbCardType.setTable('rbAccountingSystem', addNone=False, specialValues=[(0, u'-', u'код пациента')])
        ambValue = forceRef(QtGui.qApp.db.translate('rbAccountingSystem', 'code', u'Амб', 'id'))
        self.cmbAmbCardType.setValue(ambValue)
        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbQuotaType.setTable('QuotaType', addNone=True, order=self._order)
        self.setHospitalizedWidgetsVisible(False)
        self.setContractWidgetsVisible(False)
        self.setQuotingWidgetsVisible(False)
        self.setDetailClientsVisible(False)
        self.setNurseChiefVisible(False)
        
        #
        self.cmbOrgStructure.setVisible(False)
        self.chkFinance.setVisible(False)
    
    def setNurseChiefVisible(self, value):
        self._nurseChiefVisible = value
        self.chkNurseChief.setVisible(value)
        self.cmbOrgStructure.setVisible(value)

    def setDetailClientsVisible(self, value):
        self._detailClientsVisible = value
        self.chkDetailClients.setVisible(value)

    def setQuotingWidgetsVisible(self, value):
        self._quotingWidgetsVisible = value

        self.chkQuotaClass.setVisible(value)
        self.cmbQuotaClass.setVisible(value)

        self.lblQuotaType.setVisible(value)
        self.cmbQuotaType.setVisible(value)


    def setContractWidgetsVisible(self, value):
        self._contractWidgetsVisible = value

        self.lblContract.setVisible(value)
        self.cmbContract.setVisible(value)

    def setHospitalizedWidgetsVisible(self, value):
        self._hospitalizedWidgetsVisible = value

        self.lblAmbCardType.setVisible(value)
        self.cmbAmbCardType.setVisible(value)

        self.lblMedicalHistory.setVisible(value)
        self.cmbMedicalHistoryType.setVisible(value)

        self.lblDiagType.setVisible(value)
        self.cmbDiagType.setVisible(value)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbFinance.setValue(params.get('financeId', None))

        if self._contractWidgetsVisible:
            self.cmbContract.setValue(params.get('contractId', None))

        if self._hospitalizedWidgetsVisible:
            self.cmbAmbCardType.setValue(params.get('ambCardType', None))

            self.cmbMedicalHistoryType.setCurrentIndex(params.get('medicalHistoryTypeIndex', 0))

            self.cmbDiagType.setCurrentIndex(params.get('diagType', 0))

        if self._quotingWidgetsVisible:
            chkQuotaClass = params.get('chkQuotaClass', False)
            self.chkQuotaClass.setChecked(chkQuotaClass)
            self.chkQuotaClass.emit(QtCore.SIGNAL('clicked(bool)'), chkQuotaClass)
            self.cmbQuotaClass.setCurrentIndex(params.get('quotaClass', 0))
            self.cmbQuotaType.setValue(params.get('quotaTypeId', None))

        if self._detailClientsVisible:
            self.chkDetailClients.setChecked(params.get('chkDetailClients', False))
        
        if self._nurseChiefVisible:
            self.chkNurseChief.setChecked(params.get('chkNurseChief', False))
            self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
            self.chkFinance.setChecked(params.get('finance', False))

    def params(self):
        params = {}

        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['financeId']   = self.cmbFinance.value()
        params['financeText'] = self.cmbFinance.currentText()

        if self._contractWidgetsVisible:
            params['contractId'] = self.cmbContract.value()
            params['contractText'] = self.cmbContract.currentText()

        if self._hospitalizedWidgetsVisible:
            params['ambCardType'] = self.cmbAmbCardType.value()

            params['medicalHistoryTypeIndex'] = self.cmbMedicalHistoryType.currentIndex()
            params['medicalHistoryTypeText'] = self.cmbMedicalHistoryType.currentText()

            params['diagType'] = self.cmbDiagType.currentIndex()

        if self._quotingWidgetsVisible:
            params['chkQuotaClass'] = self.chkQuotaClass.isChecked()
            params['quotaClass']    = self.cmbQuotaClass.currentIndex()
            params['quotaTypeId']   = self.cmbQuotaType.value()

        if self._detailClientsVisible:
            params['chkDetailClients'] = self.chkDetailClients.isChecked()
        
        if self._nurseChiefVisible:
            params['chkNurseChief'] = self.chkNurseChief.isChecked()
            params['orgStructureId'] = self.cmbOrgStructure.value()
            params['finance'] = self.chkFinance.isChecked()


        return params

    @QtCore.pyqtSlot(bool)
    def on_chkQuotaClass_clicked(self, value):
        if value:
            index = self.cmbQuotaClass.currentIndex()
            self.cmbQuotaType.setFilter('class=%d' % index, order=self._order)
        else:
            self.cmbQuotaType.setFilter(None, order=self._order)

    @QtCore.pyqtSlot(int)
    def on_cmbQuotaClass_currentIndexChanged(self, index):
        if self.chkQuotaClass.isChecked():
            self.cmbQuotaType.setFilter('class=%d' % index, order=self._order)

    @QtCore.pyqtSlot(int)
    def on_cmbFinance_currentIndexChanged(self, index):
        self.cmbContract.setFinanceId(self.cmbFinance.value())

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbContract.setBegDate(date)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.cmbContract.setEndDate(date)
    
    
    @QtCore.pyqtSlot(bool)
    def on_chkNurseChief_clicked(self, value):
        if value:
            self.chkDetailClients.setChecked(False)
    
    
    @QtCore.pyqtSlot(bool)
    def on_chkDetailClients_clicked(self, value):
        if value:
            self.chkNurseChief.setChecked(False)




