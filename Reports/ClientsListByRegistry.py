# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils      import forceInt, forceString, smartDict, formatName, formatSex, formatSNILS
from Reports.ReportBase import createTable, CReportBase


def selectData(accountItemIdList, currentFinanceId=None, locAddr = False):
    stmt="""
        SELECT
            Client.id,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.birthDate,
            Client.sex,
            Client.SNILS,
            ClientPolicy.serial    AS policySerial,
            ClientPolicy.number    AS policyNumber,
            ClientPolicy.name      AS policyName,
            Insurer.infisCode      AS policyInsurer,
            Insurer.shortName      AS policyInsurerName,

            ClientDocument.serial  AS documentSerial,
            ClientDocument.number  AS documentNumber,
            rbDocumentType.code    AS documentType,
            Event.externalId,
            EmergencyCall.numberCardCall,
            getClientRegAddress(Client.id) AS address
            %s
        FROM
            Account_Item
            LEFT JOIN Event         ON  Event.id  = Account_Item.event_id
            LEFT JOIN Client        ON  Client.id = Event.client_id
            LEFT JOIN ClientPolicy  ON ClientPolicy.id = getClientPolicyId(Event.client_id, %s)
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND
                      ClientDocument.id = (SELECT MAX(CD.id)
                                         FROM   ClientDocument AS CD
                                         LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                         LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                                         WHERE  rbDTG.code = '1' AND CD.client_id = Client.id)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
            %s
            WHERE
                %s
                %s
            ORDER BY
                Client.lastName,
                Client.firstName,
                Client.patrName,
                Client.birthDate,
                Client.sex
    """
    if currentFinanceId and currentFinanceId == 3:
        isCompulsory = 0
    else:
        isCompulsory = 1
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    if locAddr:
        addressJoinStmt = '''LEFT JOIN ClientAddress AS ClientRegAddress ON ClientRegAddress.id = getClientRegAddressId(Client.id)
                                LEFT JOIN Address AS RegAddress ON RegAddress.id = ClientRegAddress.address_id
                                LEFT JOIN AddressHouse AS RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
                                LEFT JOIN ClientAddress AS ClientLocAddress ON ClientLocAddress.id = getClientLocAddressId(Client.id)
                                LEFT JOIN Address AS LocAddress ON LocAddress.id = ClientLocAddress.address_id
                                LEFT JOIN AddressHouse AS LocAddressHouse ON LocAddressHouse.id = LocAddress.house_id'''
        # Имитация функции Registry.Utils.getAddress, для получения полного адреса (Область-город-населенный пункт...)
        # getClientLocAddress из базы данных не дает желаемого результата, так как в нынешнем виде в ряде случаев отрезает область
        addressFields = ''', RegAddressHouse.KLADRCode AS regKLADRCode,
                            RegAddressHouse.KLADRStreetCode AS regKLADRStreetCode,
                            RegAddressHouse.number AS regNumber,
                            RegAddressHouse.corpus AS regCorpus,
                            RegAddress.flat AS regFlat,
                            ClientRegAddress.freeInput AS regFreeInput,
                            LocAddressHouse.KLADRCode AS locKLADRCode,
                            LocAddressHouse.KLADRStreetCode AS locKLADRStreetCode,
                            LocAddressHouse.number AS locNumber,
                            LocAddressHouse.corpus AS locCorpus,
                            LocAddress.flat AS locFlat,
                            ClientLocAddress.freeInput AS locFreeInput'''
    else:
        addressJoinStmt = ''
        addressFields =  ', getClientRegAddress(Client.id) as address'
    groupBy = 'GROUP BY Client.lastName, Client.firstName, Client.patrName' if locAddr else ''
    return db.query(stmt % (addressFields, isCompulsory, addressJoinStmt, tableAccountItem['id'].inlist(accountItemIdList), groupBy))


class CClientsListByRegistry(CReportBase):
    def __init__(self, parent):
        CReportBase.__init__(self, parent)
        self.setTitle(u'Список пациентов по реестру')


    def build(self, description, params):
        def getAddressRecord(record, type=0):
            if type == 0:
                prefix = 'reg'
            else:
                prefix = 'loc'
            address = smartDict()
            address.KLADRCode = forceString(record.value(prefix + 'KLADRCode'))
            address.KLADRStreetCode = forceString(record.value(prefix + 'KLADRStreetCode'))
            address.number = forceString(record.value(prefix + 'Number'))
            address.corpus = forceString(record.value(prefix + 'Corpus'))
            address.flat = forceString(record.value(prefix + 'Flat'))
            address.freeInput = forceString(record.value(prefix + 'FreeInput'))
            return address
        accountItemIdList = params.get('accountItemIdList', None)
        currentFinanceId = params.get('currentFinanceId',  None)
        showLocAddr = params.get('showLocAddr', False)
        query = selectData(accountItemIdList,  currentFinanceId, showLocAddr)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(description)
        cursor.insertBlock()

        if showLocAddr:
            tableColumns = [
                          ('3%',  [ u'№'            ], CReportBase.AlignRight ),
                          ('5%',  [ u'Номер карты'   ], CReportBase.AlignCenter),
                          ('10%', [ u'СНИЛС'         ], CReportBase.AlignLeft ),
                          ('20%', [ u'ФИО'           ], CReportBase.AlignLeft ),
                          ('8%', [ u'Дата рождения' ], CReportBase.AlignLeft ),
                          ('3%',  [ u'Пол'           ], CReportBase.AlignCenter ),
                          ('12%', [ u'Полис'         ], CReportBase.AlignCenter ),
                          ('10%', [ u'Документ'      ], CReportBase.AlignCenter ),
                          ('15%', [ u'Адрес регистрации'         ], CReportBase.AlignLeft ),
                          ('15%', [ u'Адрес проживания'         ], CReportBase.AlignLeft ),
                       ]
        else:
            tableColumns = [
                          ('3%',  [ u'№'             ], CReportBase.AlignRight ),
                          ('10%', [ u'СНИЛС'         ], CReportBase.AlignLeft ),
                          ('20%', [ u'ФИО'           ], CReportBase.AlignLeft ),
                          ('10%', [ u'Дата рождения' ], CReportBase.AlignLeft ),
                          ('3%',  [ u'Пол'           ], CReportBase.AlignCenter ),
                          ('15%', [ u'Полис'         ], CReportBase.AlignCenter ),
                          ('15%', [ u'Документ'      ], CReportBase.AlignCenter ),
                          ('20%', [ u'Адрес'         ], CReportBase.AlignLeft )
                       ]

        table = createTable(cursor, tableColumns)
        n = 0
        offset = 1 if showLocAddr else 0
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            n += 1
            record = query.record()
            externalId = forceString(record.value('numberCardCall'))
            if not externalId:
                externalId = forceString(record.value('externalId'))
            name = formatName(record.value('lastName'),
                              record.value('firstName'),
                              record.value('patrName'))
            birthDate = forceString(record.value('birthDate'))
            sex = formatSex(forceInt(record.value('sex')))
            SNILS   = formatSNILS(record.value('SNILS'))
            policyInfoList = [forceString(record.value('policySerial')), 
                                forceString(record.value('policyNumber')), 
                                forceString(record.value('policyInsurer'))]
            if showLocAddr:
                policyInfoList.append(forceString(record.value('policyInsurerName')))
            
            policy  = ' '.join(policyInfoList)
            policyName = forceString(record.value('policyName'))
            if policyName:
                policy += '\n' + policyName
            document= ' '.join([forceString(record.value('documentSerial')), forceString(record.value('documentNumber'))])
            i = table.addRow()
            table.setText(i, 0, n)
            if showLocAddr:
                table.setText(i, 1, externalId)
            table.setText(i, 1 + offset, SNILS)
            table.setText(i, 2 + offset, name)
            table.setText(i, 3 + offset, birthDate)
            table.setText(i, 4 + offset, sex)
            table.setText(i, 5 + offset, policy)
            table.setText(i, 6 + offset, document)

            if showLocAddr:
                from Registry.Utils import formatAddressInt
                regAddress = formatAddressInt(getAddressRecord(record))
                locAddress = formatAddressInt(getAddressRecord(record, 1))
                table.setText(i, 7 + offset, regAddress)
                table.setText(i, 8 + offset, locAddress)
            else:
                table.setText(i, 7 + offset, forceString(record.value('address')))
        return doc
