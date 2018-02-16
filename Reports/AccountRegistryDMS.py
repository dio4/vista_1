# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013-2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceDouble, forceInt, forceRef, forceString, formatName, getVal, \
    forceStringEx

from library.AmountToWords import amountToWords

from Reports.ReportBase import createTable, CReportBase

def selectData(accountItemIdList, financeId, orgInsurerId = None, isFranchise=None):
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    finanseCode = forceString(db.translate('rbFinance', 'id', financeId, 'code'))
    
    #atronah(30.05.2012, 344): убрал из запроса "Account_Item.sum       AS sum" и добавил "Account_Item.price       AS price". 
    #сумма будет вычисляться как price*amount
    stmt="""
        SELECT
            Client.id,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            ClientPolicy.serial    AS policySerial,
            ClientPolicy.number    AS policyNumber,
            Insurer.infisCode      AS policyInsurer,
            Diagnosis.MKB AS diagMKB,
            Diagnosis.MKBEx AS diagExMKB,

            (
                SELECT
                    GROUP_CONCAT(Diagnosis.MKB) AS MKB
                FROM
                    Diagnosis
                    INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id
                    INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
                WHERE
                    Diagnostic.event_id = Account_Item.event_id
                    AND Diagnostic.deleted = 0
                    AND Diagnosis.deleted = 0
                    AND rbDiagnosisType.code = '9'
            ) AS diagAccompMKB,

            Action.MKB AS actMKB,
            IF(rbService.name IS NULL, EventType.name, rbService.name) AS service,
            IF(rbService.code IS NULL, '',             rbService.code) AS serviceCode,
            IF(Account_Item.visit_id IS NULL,
                    IF(Account_Item.action_id IS NULL,
                        Event.execPerson_id,
                        Action.person_id),
                    Visit.person_id) AS person,
            IF(Account_Item.visit_id IS NULL,
                    IF(Account_Item.action_id IS NULL,
                        Event.assistant_id,
                        (SELECT A_A.person_id
                         FROM Action_Assistant AS A_A
                         INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                         WHERE A_A.action_id = Account_Item.action_id AND rbAAT.code like 'assistant'
                         LIMIT 1)),
                    Visit.assistant_id) AS assistant,
            Account_Item.amount    AS amount,
            Account_Item.price     AS price,
            IF(Account_Item.visit_id IS NULL,
                    IF(Account_Item.action_id IS NULL,
                        NULL,
                        Action.begDate),
                    Visit.date) AS begDate,
            IF(Account_Item.visit_id IS NULL,
                    IF(Account_Item.action_id IS NULL,
                        NULL,
                        Action.endDate),
                    Visit.date) AS endDate
        FROM
            Account_Item
            LEFT JOIN Event         ON  Event.id  = Account_Item.event_id AND Event.deleted = 0
            LEFT JOIN EventType     ON  EventType.id = Event.eventType_id AND EventType.deleted = 0
            LEFT JOIN Visit         ON  Visit.id = Account_Item.visit_id AND Visit.deleted = 0
            LEFT JOIN Action        ON  Action.id = Account_Item.action_id AND Action.deleted = 0
            LEFT JOIN Client        ON  Client.id = Event.client_id AND Client.deleted = 0

            LEFT JOIN Event MainEvent ON MainEvent.id = IFNULL(Action.event_id, IFNULL(Visit.event_id, Event.id))
            LEFT JOIN ClientPolicy ON ClientPolicy.id = MainEvent.clientPolicy_id
            # LEFT JOIN ClientPolicy ON ClientPolicy.id = (SELECT max(CP.id)
            #                                              FROM ClientPolicy AS CP
            #                                                      LEFT JOIN rbPolicyType AS CPType ON CPType.id = CP.policyType_id
            #                                              WHERE CP.client_id = Client.id
            #                                                      AND IF('%(financeCode)s' LIKE '3', CPType.code IN ('3'), CPType.code IN ('1', '2'))
            #                                                      AND CP.endDate >= IF(Account_Item.visit_id IS NULL, Action.endDate, Visit.date))
            #                           AND ClientPolicy.deleted = 0

            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
                                                 AND Insurer.deleted = 0
                                                 %(insurerOrgId)s

            LEFT JOIN Diagnosis     ON Diagnosis.id = IF(Account_Item.visit_id IS NULL,
                                                         getEventDiagnosis(Account_Item.event_id),
                                                         getEventPersonDiagnosis(Account_Item.event_id, Visit.person_id))
                                       AND Diagnosis.deleted = 0

            LEFT JOIN rbService ON rbService.id =
                IF(Account_Item.service_id IS NOT NULL,
                   Account_Item.service_id,
                   IF(Account_Item.visit_id IS NOT NULL, Visit.service_id, EventType.service_id)
                  )

        WHERE
            Account_Item.deleted = 0
            %(whereCond)s """ % {'insurerOrgId' : ('AND Insurer.id = %s ' % orgInsurerId) if orgInsurerId else '',
                                 'whereCond' : ('AND ' + tableAccountItem['id'].inlist(accountItemIdList)) if accountItemIdList else '',
                                 'financeCode' : finanseCode}
    if isFranchise is not None:
        if isFranchise:
            stmt += "AND ClientPolicy.franchisePercent > 0"
        else:
            stmt += "AND ClientPolicy.franchisePercent = 0"

    stmt += """ ORDER BY
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.birthDate,
            Client.sex,
            Account_Item.id
    """
    query = db.query(stmt)
    return query

def selectContractNumber(orgInsurerIs):
    db = QtGui.qApp.db
    stmt = '''
        SELECT MAX(Contract.id),
            Contract.number,
            Contract.date
        FROM Contract
        WHERE Contract.payer_id = %(orgInsurerIs)s AND Contract.deleted = 0
    ''' % {'orgInsurerIs' : orgInsurerIs}
    query = db.query(stmt)
    if query.first():
        record = query.record()
        return forceString(record.value('number')), forceDate(record.value('date')).toString('dd.MM.yyyy')
    return ''

class CAccountRegistryDMS(CReportBase):
    def __init__(self, parent):
        CReportBase.__init__(self, parent)
        self.setTitle(u'Реестр счёта')


    def build(self, description, params):
        db = QtGui.qApp.db
        financeId = params.get('currentFinanceId', None)
        accountItemIdList = params.get('accountItemIdList', None)
        if not accountItemIdList:
            accountItemIdList = params.get('accountIdList', None)
        orgInsurerId = params.get('orgInsurerId', None)
        chkAssistant    = params.get('assistant', False)
        if orgInsurerId:
            query = selectData(accountItemIdList, financeId, orgInsurerId, isFranchise=False)
        else:
            query = selectData(accountItemIdList, financeId, isFranchise=False)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        format = QtGui.QTextCharFormat()
        
        format.setFontPointSize(7)
        cursor.setCharFormat(format)

        smo = ""
        if forceInt(orgInsurerId):
            recordInsurerOrg = db.getRecord(db.table('Organisation'), ['fullName'], forceInt(orgInsurerId))
            if recordInsurerOrg:
                smo = forceString(recordInsurerOrg.value('fullName'))
        if smo:
            cursor.insertText(u'В страховую компанию ' + smo)
            cursor.insertBlock()
            contractNumber, contractDate = selectContractNumber(orgInsurerId)
            if contractNumber:
                contract = u'Приложение к договору ' + contractNumber
                if contractDate:
                    contract += u' от ' + contractDate
                cursor.insertBlock(CReportBase.AlignRight)
                cursor.insertText(contract)

        cursor.insertBlock(CReportBase.AlignLeft)
        format.setFontWeight(QtGui.QFont.Bold)
        format.setFontPointSize(8)
        cursor.setCharFormat(format)
        cursor.insertText(u'РАСЧЕТ СТОИМОСТИ МЕДИЦИНСКОГО ОБСЛУЖИВАНИЯ')

        cursor.insertBlock(CReportBase.AlignLeft)
        format.setFontWeight(QtGui.QFont.Normal)
        format.setFontPointSize(7)
        cursor.setCharFormat(format)
        cursor.insertText(u'Приложение к счёту ')

        orgId = forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'orgId', None))
        if orgId:
            recordOrg = db.getRecord(db.table('Organisation'), ['fullName'], forceInt(orgId))
            if recordOrg:
                cursor.insertBlock(CReportBase.AlignLeft)
                format.setFontWeight(QtGui.QFont.Bold)
                format.setFontPointSize(8)
                cursor.setCharFormat(format)
                cursor.insertText(u'Медицинское учреждение - "' + forceString(recordOrg.value('fullName')))

        format.setFontWeight(QtGui.QFont.Normal)
        cursor.setCharFormat(format)
        cursor.insertBlock(CReportBase.AlignLeft)
        cursor.insertBlock()

        tableColumns = [
                          ('3%',  [u'№ п/п', u''                    ], CReportBase.AlignRight),
                          ('15%', [ u'ФИО', u''                     ], CReportBase.AlignLeft ),
                          ('10%', [ u'Полис', u''                   ], CReportBase.AlignCenter ),
                          ('5%',  [ u'Дата начато', u''             ], CReportBase.AlignLeft ),
                          ('5%',  [ u'Дата выполнено', u''          ], CReportBase.AlignLeft ),
                          ('10%', [ u'Диагноз', u''                 ], CReportBase.AlignLeft ),
                          ('7%',  [ u'Оказанная мед. услуга', u'Код'], CReportBase.AlignLeft ),
                          ('15%', [ u'', u'Наименование'            ], CReportBase.AlignLeft ),
                          ('15%', [ u'ФИО специалиста', u''         ], CReportBase.AlignLeft ),
                          ('5%',  [ u'Кол-во', u''                  ], CReportBase.AlignRight ),
                          ('5%',  [ u'Стоимость ед. услуги', u''    ], CReportBase.AlignRight ),
                          ('5%',  [ u'Сумма к оплате', u''          ], CReportBase.AlignRight )]

        format.setFontWeight(QtGui.QFont.Bold)
        table = createTable(cursor, tableColumns,  charFormat = format)
        format.setFontWeight(QtGui.QFont.Normal)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)
        table.mergeCells(0, 10, 2, 1)
        table.mergeCells(0, 11, 2, 1)

        totalAmount = 0

        totalSum    = 0.0
        rowBegNumber = 1
        prevClientId = -1
        totalClientSum = 0.0
        totalClientAmount = 0
        self.setQueryText(forceString(query.lastQuery()))
        oldName = ''
        i = 1
        clientNumber = 1
        while query.next():
            record = query.record()
            
            clientId = forceRef(record.value('id'))
            name = formatName(record.value('lastName'),
                              record.value('firstName'),
                              record.value('patrName'))
            policy  = ' '.join([forceString(record.value('policySerial')), forceString(record.value('policyNumber')), forceString(record.value('policyInsurer'))])
            diagMKB = forceString(record.value('diagMKB'))
            diagExMKB = forceString(record.value('diagExMKB'))
            diagAccompMKB = forceString(record.value('diagAccompMKB'))
            actMKB = forceString(record.value('actMKB'))
            service = forceString(record.value('service'))
            serviceCode = forceString(record.value('serviceCode'))
            person = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', forceRef(record.value('person')), 'name'))
            assistant = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', forceRef(record.value('assistant')), 'name'))
            amount = forceInt(record.value('amount'))
            price   = forceDouble(record.value('price'))
            sum = price * amount
            begDate = forceDate(record.value('begDate')).toString('dd.MM.yy')
            endDate = forceDate(record.value('endDate')).toString('dd.MM.yy')

            if clientId == prevClientId or prevClientId == -1:
                totalClientAmount += amount
                totalClientSum += sum
            elif prevClientId != -1:
                i = table.addRow()
                table.mergeCells(i, 0, 1, 9)
                format.setFontWeight(QtGui.QFont.Bold)
                table.setText(i, 1, u'Итого по клиенту:', format, CReportBase.AlignLeft)
                table.setText(i, 9, totalClientAmount, format)
                table.setText(i, 11, QtCore.QString.number(totalClientSum, 'g', 9), format)
                format.setFontWeight(QtGui.QFont.Normal)
                totalClientAmount = amount
                totalClientSum = sum
            prevClientId = clientId

            i = table.addRow()
            if oldName != name:
                table.setText(i, 0, clientNumber)
                table.setText(i, 1, name,  format)
                if i - rowBegNumber > 2:
                    table.mergeCells(rowBegNumber, 0, i - rowBegNumber - 1, 1)
                    table.mergeCells(rowBegNumber, 1, i - rowBegNumber - 1, 1)
                oldName = name
                rowBegNumber = i
                clientNumber += 1
            table.setText(i, 2, policy,  format)
            mkb = ''
            if actMKB:
                mkb = actMKB
            else:
                mkb += diagMKB
                mkb += ', ' if mkb and diagExMKB else ''
                mkb += diagExMKB
            if diagAccompMKB:
                mkb = ', '.join([mkb, diagAccompMKB])
            table.setText(i, 3, begDate,  format)
            table.setText(i, 4, endDate,  format)
            table.setText(i, 5, mkb, format)
            table.setText(i, 6, serviceCode,  format)
            table.setText(i, 7, service,  format)
            if not chkAssistant or not assistant:
                table.setText(i, 8, person,  format)
            else:
                table.setText(i, 8, person + ' / ' + assistant, format)
            table.setText(i, 9, amount,  format)
            table.setText(i, 10, QtCore.QString.number(price, 'g',  9),  format)
            table.setText(i, 11, QtCore.QString.number(sum, 'g', 9),  format)

            totalAmount += amount
            totalSum += sum

        if i - rowBegNumber > 0:
            table.mergeCells(rowBegNumber, 0, i - rowBegNumber + 1, 1)
            table.mergeCells(rowBegNumber, 1, i - rowBegNumber + 1, 1)

        i = table.addRow()
        table.mergeCells(i, 0, 1, 9)
        format.setFontWeight(QtGui.QFont.Bold)
        table.setText(i, 1, u'Итого по клиенту:', format, CReportBase.AlignLeft)
        table.setText(i, 9, totalClientAmount, format)
        table.setText(i, 11, QtCore.QString.number(totalClientSum, 'g', 9), format)
        format.setFontWeight(0)

        i = table.addRow()

        table.mergeCells(i, 0, 1, 9)
        format.setFontWeight(QtGui.QFont.Bold)
        table.setText(i, 1, u'Итого:',   format, CReportBase.AlignLeft)
        table.setText(i, 9, totalAmount, format)
        table.setText(i, 11, QtCore.QString.number(totalSum, 'g', 9), format)
        format.setFontWeight(QtGui.QFont.Normal)
        cursor.movePosition(cursor.End)
        cursor.insertBlock(CReportBase.AlignLeft)
        cursor.insertBlock()

        cursor.insertText(u'Сумма к оплате: ' + amountToWords(totalSum))
        cursor.insertBlock()

        orgPhoneNumber = "-"
        if orgId:
            recordChief = db.getRecord(db.table('Organisation'), ['chief', 'phone'], orgId)
            if forceString(recordChief.value('chief')):
                if forceStringEx(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')) == u'мсч3':
                    cursor.insertText(u'Начальник \"Медико-санитарной части №3\"' +  forceString(recordChief.value('chief')))
                else:
                    cursor.insertText(u'Начальник отдела ' + forceString(recordChief.value('chief')))
                cursor.insertBlock()
                cursor.insertBlock()
                cursor.insertBlock()
            if forceString(recordChief.value('phone')):
                orgPhoneNumber = forceString(recordChief.value('phone'))

        cursor.insertText(u'Исполнитель ' +  forceString(QtGui.qApp.userInfo.name()))
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'тел. ' + orgPhoneNumber)
        cursor.insertBlock()

        return doc
