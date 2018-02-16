# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################
"""
Created on Jul 26, 2012

@author: atronah
"""

from PyQt4 import QtGui, QtCore

from library.Utils      import forceDouble, forceString, formatName, formatSex
from Orgs.Utils         import getOrganisationInfo, getOrganisationMainStaff
from Reports.Report     import getAccountName
from Reports.ReportBase import createAutographField, createTable, CReportBase


def selectData(params):
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    accountItemIdList = params.get('accountItemIdList', None)
    orgInsurerId = params.get('orgInsurerId', None)
    policeCondDate = """
    IF(Action.begDate IS NOT NULL,
       Action.begDate,
       IF(Visit.date IS NOT NULL,
          Visit.date,
          Event.setDate)
    )
    """
    
    policyCond = '(CP.begDate <= DATE(%(policyDate)s))'
    if params.get('isLocRegistry', True):
        policyCond +=  u' AND (CP.endDate IS NULL OR CP.endDate >= DATE(%(policyDate)s))'
    
    policyCond = policyCond % {'policyDate' : policeCondDate}
    
    stmt="""
        SELECT DISTINCT 
            Account_Item.id,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.sex,
            Client.birthDate,
            Client.birthPlace,
            TRIM(CONCAT(rbDocumentType.name, ' ',
                        ClientDocument.serial, ' ',
                        ClientDocument.number)) AS document,
            Client.SNILS,
            TRIM(CONCAT(ClientPolicy.serial, ' ', ClientPolicy.number)) AS policy,
            rbMedicalAidKind.federalCode AS medicalKindCode,
            Diagnosis.MKB AS MKB,
            DATE(IF(Action.begDate IS NOT NULL,
                    Action.begDate,
                    IF(Visit.date IS NOT NULL,
                         Visit.date,
                         Event.setDate)
                   )) AS begDate,
            DATE(IF(Action.endDate IS NOT NULL,
                    Action.endDate,
                    IF(Visit.date IS NOT NULL,
                         Visit.date,
                         Event.execDate)
                   )) AS endDate,
            Account_Item.amount AS amount,
            rbSpeciality.federalCode AS medicalProfile,
            rbSpeciality.regionalCode AS specialityCode,
            Account_Item.price as price,
            LEAST(tariff.federalPrice, Account_Item.price) AS federalPrice,
            (Account_Item.price * Account_Item.amount) AS sum,
            LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                           Account_Item.amount,
                                           LEAST(tariff.federalLimitation, Account_Item.amount)),
                  Account_Item.sum) AS federalSum,
            rbResult.regionalCode AS resultCode,
            getClientRegAddress(Client.id) AS registerAddress,
            getClientLocAddress(Client.id) AS residentAddress
        FROM Account_Item
            LEFT JOIN Event ON Event.id = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Visit ON  Visit.id  = Account_Item.visit_id
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN rbService ON rbService.id = IF(Account_Item.service_id IS NOT NULL,
                                                        Account_Item.service_id,
                                                        IF(Account_Item.visit_id IS NOT NULL, 
                                                            Visit.service_id, 
                                                            EventType.service_id)
                                                    )
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id 
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id = rbDocumentType.group_id
            LEFT JOIN ClientPolicy ON ClientPolicy.id = (SELECT CP.id 
                                                         FROM ClientPolicy AS CP
                                                                 LEFT JOIN rbPolicyType AS CPType ON CPType.id = CP.policyType_id
                                                         WHERE CP.client_id = Client.id
                                                                 AND (CPType.code LIKE '1' OR CPType.code LIKE '2')
                                                                 AND %(policyCond)s
                                                                 
                                                         ORDER BY CP.begDate DESC, CP.id DESC
                                                         LIMIT 1)
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN rbMedicalAidKind ON rbMedicalAidKind.id = IF(EventType.medicalAidKind_id IS NOT NULL,
                                                                    EventType.medicalAidKind_id,
                                                                    rbService.medicalAidKind_id)
            LEFT JOIN Diagnosis ON Diagnosis.id = IF(Account_Item.visit_id IS NULL,
                                                        getEventDiagnosis(Account_Item.event_id),
                                                        getEventPersonDiagnosis(Account_Item.event_id, Visit.person_id))
            LEFT JOIN rbResult ON rbResult.id = Event.result_id
            LEFT JOIN Person ON Person.id = IF(Account_Item.visit_id IS NULL,
                                                IF(Account_Item.action_id IS NULL,
                                                    Event.execPerson_id,
                                                    Action.person_id),
                                                Visit.person_id)
            LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
            LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
        WHERE
            ClientDocument.id = (SELECT MAX(CD.id)
                                FROM ClientDocument AS CD
                                        LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                        LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                                WHERE  rbDTG.code = '1' AND CD.client_id = Client.id)
            AND %(cond)s 
        ORDER BY Client.lastName, Client.firstName, Client.patrName ASC
        """ % {'policyCond' : policyCond, 
                                'cond' : tableAccountItem['id'].inlist(accountItemIdList)}
        
    if orgInsurerId:
        tableOrganisation = db.table('Organisation').alias('Insurer')
        stmt += """ AND %s """ % (tableOrganisation['id'].eq(orgInsurerId))
    return db.query(stmt)

##Реестр счета для Мурманска
class CAccountRegistryR51(CReportBase):
    def __init__(self, parent, ):
        CReportBase.__init__(self, parent)
        self.setTitle(u'Реестр счёта')
        
    def build(self, params):
        db = QtGui.qApp.db
        accountId = params.get('accountId', None)
        accountName = getAccountName(accountId)
        query = selectData(params)
        
        isLocRegistry = params.get('isLocRegistry', True)
        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        format = QtGui.QTextCharFormat()
        
        cursor.insertBlock(CReportBase.AlignCenter)
        format.setFontPointSize(14)
        if isLocRegistry:
            cursor.insertText(u'РЕЕСТР СЧЕТОВ', format)
        else:
            cursor.insertText(u'РЕЕСТР СЧЕТА № %s' % accountName, format)
        
        cursor.insertBlock(CReportBase.AlignCenter)
        format.setFontPointSize(10)
        currentOrgInfo = getOrganisationInfo(QtGui.qApp.currentOrgId())
        cursor.insertText(u'%(fullName)s; ОГРН: %(OGRN)s' % currentOrgInfo, format)
        
        cursor.insertBlock(CReportBase.AlignCenter)
        dateInterval = {'begDate' : forceString(params.get('begDate', QtCore.QDate())),
                        'endDate' : forceString(params.get('endDate', QtCore.QDate()))
                        }
        cursor.insertText(u'за период с %(begDate)s по %(endDate)s' % dateInterval, format)
        
        cursor.insertBlock(CReportBase.AlignCenter)
        if isLocRegistry:
            orgInsurerId = params.get('orgInsurerId', None)
            if orgInsurerId:
                insurerOrgInfo = getOrganisationInfo(orgInsurerId)
            else:
                insurerOrgInfo = {'fullName' : '______________________________________'}    
            cursor.insertText(u'на оплату медицинской помощи, оказанной застрахованным лицам, в %(fullName)s' % insurerOrgInfo, format)
            format.setFontPointSize(7)
        else:
            cursor.insertText(u'на оплату медицинской помощи, оказанной застрахованным лицам за пределами субъекта Российской Федерации, на территории которого выдан полис обязательного медицинского страхования', format)
            format.setFontPointSize(8)
        
        cursor.insertBlock()
        cursor.insertBlock()
        
        tableColumns = []
        tableColumns.append(('10?',  [ u'№ позиции реестра', str(1)], CReportBase.AlignCenter))
        tableColumns.append(('26?', [ u'Фамилия,\nимя,\nотчество\n(при\nналичии)', str(2)], CReportBase.AlignCenter))
        tableColumns.append(('6?',  [ u'Пол', str(3)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Дата\nрождения', str(4)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Место\nрождения', str(5)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Данные\nдоку-\nмента,\nудосто-\nверяю-\nщего\nличность', str(6)], CReportBase.AlignCenter))
        colOffset = 0
        if isLocRegistry:
            tableColumns.append(('7?',  [ u'Место\nжитель-\nства', str(7)], CReportBase.AlignCenter))
            tableColumns.append(('7?',  [ u'Место\nрегист-\nрации', str(8) ], CReportBase.AlignCenter))
            colOffset = 2
        tableColumns.append(('7?',  [ u'СНИЛС\n(при\nналичии)', str(7 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'№ полиса\nобяза-\nтельного\nмеди-\nцинского\nстрахо-\nвания', str(8 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Вид\nоказан-\nной\nмедицин-\nской\nпомощи\n(код)', str(9 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Диагноз\nв соот-\nветствии\nс МКБ-10', str(10 + colOffset)], CReportBase.AlignCenter))
        if isLocRegistry:
            tableColumns.append(('7?',  [ u'Дата\nначала\nи дата\nокон-\nчания\nлечения', str(11 + colOffset)], CReportBase.AlignCenter))
            colOffset -= 1
        else:
            tableColumns.append(('7?',  [ u'Дата\nначала\nлечения', str(11 + colOffset)], CReportBase.AlignCenter))
            tableColumns.append(('7?',  [ u'Дата\nоконча-\nния\nлечения', str(12 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Объемы\nоказанной\nмедицин-\nской\nпомощи', str(13 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Профиль\nоказанной\nмедицин-\nской\nпомощи\n(код)', str(14 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Специ-\nальность\nмедицин-\nского\nработника,\nоказав-\nшего\nмедицин-\nскую\nпомощь\n(код)', str(15 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Тариф\nна оплату\nмедицин-\nской\nпомощи,\nоказанной\nзастрахо-\nванному\nлицу', str(16 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Стоимость\nоказанной\nмедицин-\nской\nпомощи', str(17 + colOffset)], CReportBase.AlignCenter))
        tableColumns.append(('7?',  [ u'Результат\nобращения\nза меди-\nцинской\nпомощью\n(код)', str(18 + colOffset)], CReportBase.AlignCenter))

        table = createTable(cursor, tableColumns, charFormat = format)
        count = 0
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            row = table.addRow()
            count += 1
            sum = forceDouble(record.value('sum'))
            federalSum = forceDouble(record.value('federalSum'))
            price = forceDouble(record.value('price'))
            federalPrice = forceDouble(record.value('federalPrice'))
            table.setText(row, 0, forceString(count), charFormat = format)
            table.setText(row, 1, formatName(record.value('lastName'),
                                            record.value('firstName'),
                                            record.value('patrName')), charFormat = format)
            table.setText(row, 2, formatSex(record.value('sex')).upper(), charFormat = format)
            table.setText(row, 3, forceString(record.value('birthDate')), charFormat = format)
            table.setText(row, 4, forceString(record.value('birthPlace')), charFormat = format)
            table.setText(row, 5, forceString(record.value('document')), charFormat = format)
            colOffset = 0
            if isLocRegistry:
                table.setText(row, 6, forceString(record.value('residentAddress')), charFormat = format)
                table.setText(row, 7, forceString(record.value('registerAddress')), charFormat = format)
                colOffset = 2
            table.setText(row, 6 + colOffset, forceString(record.value('SNILS')), charFormat = format)
            table.setText(row, 7 + colOffset, forceString(record.value('policy')), charFormat = format)
            table.setText(row, 8 + colOffset, forceString(record.value('medicalKindCode')), charFormat = format)
            table.setText(row, 9 + colOffset, forceString(record.value('MKB')), charFormat = format)
            if isLocRegistry:
                date = '%s - %s' % (forceString(record.value('begDate')), 
                                    forceString(record.value('endDate')))
                table.setText(row, 10 + colOffset, date, charFormat = format)
                colOffset -= 1
            else:
                table.setText(row, 10 + colOffset, forceString(record.value('begDate')), charFormat = format)
                table.setText(row, 11 + colOffset, forceString(record.value('endDate')), charFormat = format)                
            table.setText(row, 12 + colOffset, forceString(record.value('amount')), charFormat = format)
            table.setText(row, 13 + colOffset, forceString(record.value('medicalProfile')), charFormat = format)
            table.setText(row, 14 + colOffset, forceString(record.value('specialityCode')), charFormat = format)
            table.setText(row, 15 + colOffset, QtCore.QString.number(price - federalPrice, 'g', 9), charFormat = format)
            table.setText(row, 16 + colOffset, QtCore.QString.number(sum - federalSum, 'g', 9), charFormat = format)
            table.setText(row, 17 + colOffset, forceString(record.value('resultCode')), charFormat = format)
        
        cursor.movePosition(cursor.End)
        cursor.insertBlock(CReportBase.AlignLeft)
        titles = []
        names = []
        orgMainStaff = getOrganisationMainStaff(QtGui.qApp.currentOrgId())
        colCount = 1
        sealOverTitle = 1
        if not isLocRegistry:            
            titles = [u'Руководитель медицинской\nорганизации']
            names = [orgMainStaff[0]]
            colCount = 2
            sealOverTitle = 2
        titles.append(u'Главный бухгалтер')
        names.append(orgMainStaff[1])
        titles.append(u'Исполнитель')
        names.append(None)
        cursor.movePosition(cursor.End)

        cursor.insertBlock(CReportBase.AlignLeft)
        createAutographField(cursor, 
                             titles, 
                             names, 
                             sealOverTitle = sealOverTitle,
                             colCount = colCount, 
                             signLabel = u'(подпись)',
                             transcriptLabel = u'(расшифровка подписи)',
                             charFormat = format)

        cursor.movePosition(cursor.End)
        
        cursor.insertBlock(CReportBase.AlignLeft)
        cursor.insertText(u'Дата  ______________________', format)
        return doc        
        
        