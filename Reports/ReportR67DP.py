# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 18.06.2012

@author: zion
"""

from PyQt4 import QtCore, QtGui

from library.Utils import forceDate, forceDouble, forceInt, forceRef, forceString, formatSex

from Orgs.Utils import getOrganisationMainStaff

from Registry.Utils import formatAddress

from Reports.Report import CReport
from Reports.ReportBase import createAutographField, createTable, CReportBase


def selectData(params):
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    accountItemIdList = params.get('accountItemIdList', None)
    stmt = """
    SELECT
        Client.lastName,
        Client.firstName,
        Client.patrName,
        Client.birthDate,
        Client.sex,
        Insurer.infisCode AS policyInsurer,
        TRIM(CONCAT(ClientPolicy.serial,' ', ClientPolicy.number)) AS policySN,
        Event.execDate AS endDate,
        ClientRegAddress.address_id AS addressId,
        ClientRegAddress.freeInput AS freeInput,
        Account_Item.price AS price,
        tariff.federalPrice AS federalPrice,
        LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                   Account_Item.amount,
                                   LEAST(tariff.federalLimitation, Account_Item.amount)),
              Account_Item.sum) AS federalSum,
        Account_Item.`sum`,
        Diagnosis.MKB,
        Account_Item.event_id
    FROM 
        Account_Item
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id 
                                        AND ClientPolicy.id = (SELECT MAX(CP.id)
                                                               FROM ClientPolicy AS CP
                                                                        LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                                                               WHERE CP.client_id = Client.id
                                                                        AND CP.deleted=0
                                                                        AND CPT.code IN ('1','2'))
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id 
                                                            AND ClientRegAddress.id = (SELECT MAX(CRA.id)
                                                                                        FROM ClientAddress AS CRA
                                                                                        WHERE  CRA.type = 0 
                                                                                                    AND CRA.client_id = Client.id 
                                                                                                    AND CRA.deleted=0)
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                        AND Diagnostic.diagnosisType_id IN (SELECT id 
                                                                            FROM rbDiagnosisType 
                                                                            WHERE code IN ('1', '2'))
                                                                                    AND Diagnostic.person_id = Event.execPerson_id 
                                                                                    AND Diagnostic.deleted = 0)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id 
                                    AND Diagnosis.deleted = 0
            LEFT JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB
            LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
    WHERE Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                    OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)) 
            AND %s""" % tableAccountItem['id'].inlist(accountItemIdList)
    return db.query(stmt)


## Формирование списка дат проведения диагностических мероприятий
#    @param eventId: ID события, по которому собираются данные
#    @param specIdList: список id специальностей, по которым нужны даты
#    @return: словарь {специальность : дата}
def getDiagDates(eventId,  specIdList):
    db = QtGui.qApp.db    
    tableDiagnostic = db.table('Diagnostic')
    tableSpeciality = db.table('rbSpeciality')
    stmt='''SELECT Diagnostic.endDate, rbSpeciality.code
            FROM Diagnostic
            LEFT JOIN Person on Diagnostic.person_id=Person.id
            LEFT JOIN rbSpeciality on rbSpeciality.id=Person.speciality_id
            WHERE %s
            ORDER BY rbSpeciality.code
        ''' % db.joinAnd([tableDiagnostic['event_id'].eq(eventId),
    tableSpeciality['code'].inlist(specIdList.keys())])

    query = db.query(stmt)
    result = {}
    while query.next():
        record = query.record()
        if record:
            fieldName = specIdList.get(forceString(record.value('code')))
            endDate = forceDate(record.value('endDate'))

            if fieldName and endDate.isValid():
                result[fieldName] = endDate

    return result


##Формирование списка дат взятия анализов
#    @param eventId: ID события, по которому собираются данные
#    @param actionTypeMap: словарь типов действий
#    @return: словарь {код_типа_действия : дата_окончания}
def getAnalysisDates(eventId, actionTypeMap):
    result = {}
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    if actionTypeMap and eventId:
        recordList = db.getRecordList(tableAction, 'actionType_id, endDate', [
            tableAction['event_id'].eq(eventId),
            tableAction['actionType_id'].inlist(actionTypeMap.keys())])


        for record in recordList:
            if record:
                code = actionTypeMap.get(forceRef(record.value(0)))
                endDate = forceDate(record.value(1))

                if code and endDate.isValid():
                    result[code] = endDate

    return result


##Отчет о диспансереризации подростков в Смоленске
class CReportR67DP(CReport):
    dpSpecialityMap = {
        '52': 'PEDIATR',
        '48': 'OTOLAR',
        '89': 'HIRURG',
        '49': 'OFTAL',
        '40': 'NEVROL',
        '70': 'GINEKOL',
        '02': 'STOMAT',
        '20': 'ENDOKR',
        '18': 'ANDROL',
        '81': 'ORTOPED'
    }

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Смоленская область. Отчет по диспансеризации подростков.')
        self.db = QtGui.qApp.db
        self.dpAnalysisMap = None
        self.actionTypeGroup1 = None
        self.actionTypeGroup2 = None


    def prepareActionTypeGroups(self):
        if not self.actionTypeGroup1:
            record = self.db.getRecordEx('ActionType', 'id', 'code=\'1-1\' and class=1')

            if record:
                self.actionTypeGroup1 = forceInt(record.value(0)) # id лабораторных исследований

        if not self.actionTypeGroup2:
            record = self.db.getRecordEx('ActionType', 'id', 'code=\'1-2\' and class=1')

            if record:
                self.actionTypeGroup2 = forceInt(record.value(0)) # id лучевой диагностики

        dpAnalysisTypes = [
            # name, code, group_id
            ('AN_KROV', '03', self.actionTypeGroup1), # Дата анализа крови
            ('AN_MOCH', '04', self.actionTypeGroup1), # Дата анализа мочи
            ('AN_KAL', '16', self.actionTypeGroup1), # Дата анализа кала
            ('USI_SHC', '15', self.actionTypeGroup2), # Дата УЗИ щитовидной железы
            ('USI_MJ', '08', self.actionTypeGroup2), # Дата УЗИ молочных желез
            ('USI_MT', '50', self.actionTypeGroup2), # Дата УЗИ органов малого таза
            ('USI_YI', '14', self.actionTypeGroup2), # Дата УЗИ яичек
            ('GLAZ_DNO', '53', self.actionTypeGroup2) # Дата осмотра глазного дна
        ]

        self.dpAnalysisMap = self.makeAnalysisMap(dpAnalysisTypes)


    def makeAnalysisMap(self, types):
        result = {}
        tableActionType = self.db.table('ActionType')
        for (key, code,  groupId) in types:
            record = self.db.getRecordEx(tableActionType, 'id',
                self.db.joinAnd([tableActionType['code'].eq(code),
                                 tableActionType['group_id'].eq(groupId)]))
            if record:
                id = forceRef(record.value(0))
                result[id] = key
        return result
    
    
    def getAccountInfo(self, accountId):
        record = self.db.getRecord('Account', ['date', 'contract_id'], accountId)
        date = QtCore.QDate()
        emptyName = u'__________________________'
        orgSenderShortName = emptyName
        orgRecipientShortName = emptyName
        if record:
            date = forceDate(record.value('date'))
            contractId = forceRef(record.value('contract_id'))
            record = self.db.getRecord('Contract', ['recipient_id', 'payer_id'], contractId)
            if record:
                orgSenderId = forceRef(record.value('recipient_id')) #Отправитель счета - клиника, которая является получателем денег (Contract.recipient_id)
                orgRecipientId = forceRef(record.value('payer_id')) #Получатель счета - плательщик
                orgSenderShortName = forceString(self.db.translate('Organisation', 'id', orgSenderId, 'shortName'))
                orgRecipientShortName = forceString(self.db.translate('Organisation', 'id', orgRecipientId, 'shortName'))
        return (date, orgSenderShortName, orgRecipientShortName)


    def build(self, params):
        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        format = QtGui.QTextCharFormat()
        
        cursor.insertBlock()
        format.setFontPointSize(14)
        format.setFontWeight(QtGui.QFont.Bold)
        accountDate, sender, recipient = self.getAccountInfo(params.get('accountId', None))
        cursor.insertText(u'РЕЕСТР счетов за %s на %s.' % (forceString(accountDate),
                                                           u'оплату расходов по проведенной диспансеризации подростков'))
        cursor.insertBlock()
        
        cursor.insertBlock()
        format.setFontPointSize(8)
        format.setFontWeight(QtGui.QFont.Normal)
        cursor.insertText(u'Учреждение-отправитель: %s' % sender)
        cursor.insertBlock()
        
        cursor.insertBlock()
        cursor.insertText(u'Учреждение-получатель:  %s' % recipient)
        
        
        format.setFontPointSize(8)
        
        tableColumns = [
            ('?',  [u'№ п/п',
                    u'',
                    u'1'],  CReportBase.AlignLeft), 
            ('?',  [u'Фамилия',
                    u'',
                    u'2'],  CReportBase.AlignCenter), 
            ('?',  [u'Имя',
                    u'',
                    u'3'],  CReportBase.AlignCenter),  
            ('?',  [u'Отчество',
                    u'',
                    u'4'],  CReportBase.AlignCenter),  
            ('?',  [u'Пол',
                    u'',
                    u'5'],  CReportBase.AlignCenter),  
            ('?',  [u'Дата рождения',
                    u'',
                    u'6'],  CReportBase.AlignCenter),  
            ('?',  [u'Адрес по месту регистрации',
                    u'',
                    u'7'],  CReportBase.AlignCenter),  
            ('?',  [u'Серия и номер полиса',
                    u'',
                    u'8'],  CReportBase.AlignCenter),  
            ('?',  [u'СМО',
                    u'',
                    u'9'],  CReportBase.AlignCenter),  
            ('?',  [u'Диагноз по МКБ 10 (основной)',
                    u'',
                    u'10'],  CReportBase.AlignCenter),  
            ('?',  [u'Даты осмотров врачами-специалистами, проведения лабораторных и функциональных исследований',
                    u'педиатр',
                    u'11'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'невролог',
                    u'12'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'офтальмолог',
                    u'13'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'детский хирург',
                    u'14'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'оториноларинголог',
                    u'15'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'акушер-гинеколог',
                    u'16'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'травматолог-ортопед',
                    u'17'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'детский стоматолог',
                    u'18'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'детский уролог-андролог',
                    u'19'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'детский эндокринолог',
                    u'20'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'клин. анализ крови',
                    u'21'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'клин. анализ мочи',
                    u'22'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'анализ кала',
                    u'23'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'осмотр глазного дна',
                    u'24'],  CReportBase.AlignCenter),
            ('?',  [u'УЗИ',
                    u'щитовидной железы',
                    u'25'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'молочных желез',
                    u'26'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'органов малого таза',
                    u'27'],  CReportBase.AlignCenter),
            ('?',  [u'',
                    u'яичек',
                    u'28'],  CReportBase.AlignCenter),
            ('?',  [u'Цена',
                    u'',
                    u'29'],  CReportBase.AlignCenter),
            ('?',  [u'Федеральная цена',
                    u'',
                    u'30'],  CReportBase.AlignCenter),
            ('?',  [u'Норматив затрат на проведение диспансеризации',
                    u'',
                    u'31'],  CReportBase.AlignCenter),
            
            ]
        table = createTable(cursor, tableColumns, 3)
        
        for i in xrange(0, 10): #Объединение (вертикальное) для первых 10 полей
            table.mergeCells(0, i, 2, 1)
        table.mergeCells(0, 10, 1, 14)  #Объединение ячеек для поля "Даты осмотров врачами..."
        table.mergeCells(0, 24, 1, 4)   #Объединение для поля "УЗИ"
        table.mergeCells(0, 29, 1, 1)   #Объединение (вертикальное) для поля "Норматив затрат на проведение диспансеризации"
        
        self.prepareActionTypeGroups()
        
        query = selectData(params)
        n = 0
        fullSum = 0.0
        fullFederalSum = 0.0
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            n += 1
            record = query.record()
            
            i = table.addRow()
            sex = formatSex(record.value('sex')).upper()
            price = forceDouble(record.value('price'))
            federalPrice = forceDouble(record.value('federalPrice'))               
            sum = forceDouble(record.value('sum'))
            federalSum = forceDouble(record.value('federalSum'))
            table.setText(i, 0, n, format)
            table.setText(i, 1, forceString(record.value('lastName')), format)
            table.setText(i, 2, forceString(record.value('firstName')), format)
            table.setText(i, 3, forceString(record.value('patrName')), format)
            table.setText(i, 4, sex, format)
            table.setText(i, 5, forceString(forceDate(record.value('birthDate'))), format)
            table.setText(i, 6, formatAddress(forceRef(record.value('addressId'))), format)
            table.setText(i, 7, forceString(record.value('policySN')), format)
            table.setText(i, 8, forceString(record.value('policyInsurer')), format)
            table.setText(i, 9, forceString(record.value('MKB')), format)
            
            eventId = forceString(record.value('event_id'))
            diagDates = getDiagDates(eventId, self.dpSpecialityMap)
            table.setText(i, 10, forceString(diagDates.get('PEDIATR', '-')), format)
            table.setText(i, 11, forceString(diagDates.get('NEVROL', '-')), format)
            table.setText(i, 12, forceString(diagDates.get('OFTAL', '-')), format)
            table.setText(i, 13, forceString(diagDates.get('HIRURG', '-')), format)
            table.setText(i, 14, forceString(diagDates.get('OTOLAR', '-')), format)
            table.setText(i, 15, forceString(diagDates.get('GINEKOL', '-')), format)
            table.setText(i, 16, forceString(diagDates.get('ORTOPED', '-')), format)
            table.setText(i, 17, forceString(diagDates.get('STOMAT', '-')), format)
            table.setText(i, 18, forceString(diagDates.get('ANDROL', '-')), format)
            table.setText(i, 19, forceString(diagDates.get('ENDOKR', '-')), format)
            
            analysisDates = getAnalysisDates(eventId, self.dpAnalysisMap)
            table.setText(i, 20, forceString(analysisDates.get('AN_KROV', '-')), format)
            table.setText(i, 21, forceString(analysisDates.get('AN_MOCH', '-')), format)
            table.setText(i, 22, forceString(analysisDates.get('AN_KAL', '-')), format)
            table.setText(i, 23, forceString(analysisDates.get('GLAZ_DNO', '-')), format)
            table.setText(i, 24, forceString(analysisDates.get('USI_SHC', '-')), format)
            table.setText(i, 25, forceString(analysisDates.get('USI_MJ', '-')), format)
            table.setText(i, 26, forceString(analysisDates.get('USI_MT', '-')), format)
            table.setText(i, 27, forceString(analysisDates.get('USI_YI', '-')), format)
            
            table.setText(i, 28, QtCore.QString.number(price, 'g', 9), format)
            table.setText(i, 29, QtCore.QString.number(federalPrice, 'g', 9), format)
            table.setText(i, 30, QtCore.QString.number(sum, 'g', 9), format)
            
            fullSum += sum
            fullFederalSum += federalSum
        
        cursor.movePosition(cursor.End)
        cursor.insertBlock()
        
        cursor.insertBlock()
        cursor.insertText(u'ВСЕГО ПРЕДСТАВЛЕНО К ОПЛАТЕ:')
        
        cursor.insertBlock()
        cursor.insertText(u'По территориальному тарифу на сумму: %s' % QtCore.QString.number(fullSum - fullFederalSum, 'f', 2)) 
        
        cursor.insertBlock()
        cursor.insertText(u'По дополнительному тарифу на сумму: %s' %  QtCore.QString.number(fullFederalSum, 'f', 2))
        
        cursor.insertBlock()
        createAutographField(cursor, [u'Гл. врач', u'Гл. бухгалтер'], getOrganisationMainStaff(QtGui.qApp.currentOrgId()), format)
        
        return doc