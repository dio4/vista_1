# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

#выгрузка для смоленска ИЭМК федеральный уровень, регистрационные данные

import uuid
import os

from PyQt4              import QtCore, QtGui
from PyQt4.QtCore       import QXmlStreamWriter, QDateTime

from library.database   import connectDataBaseByInfo
from library.Utils      import forceString, forceInt, forceDate, forceTime, forceStringEx

from KLADR.KLADRModel   import getCityName, getMainRegionName, getStreetName


# Типы документов:
# 1 - Полис ОМС
# 2 - Полис ДМС
# 3 - СНИЛС
# 4 - ИНН
# 5 - Объединенный код для документов, удостоверяющих личность (требует уточнения)
# 9 - Локальный идентификатор пациента в МИС
# 10 - Номер карты пациента в МО


def getAddr(KLADRCode, KLADRStreetCode):
    db = QtGui.qApp.db
    stmtCity = '''
        SELECT kladr.KLADR.NAME, kladr.KLADR.SOCR
        FROM kladr.KLADR
        WHERE kladr.KLADR.CODE = %s
    ''' % KLADRCode
    queryCity = db.query(stmtCity)
    if queryCity.first():
        recordCity = queryCity.record()
        nameCity = forceString(recordCity.value('NAME'))
        if forceString(recordCity.value('SOCR')) != u'г':
            regCode = KLADRCode[0:1] + '00000000000'
            stmtReg = '''
                SELECT kladr.KLADR.NAME
                FROM kladr.KLADR
                WHERE kladr.KLADR.CODE = %s
            ''' % regCode
            queryReg = db.query(stmtReg)
            if queryReg.first():
                recordReg = queryReg.record()
                nameReg = forceString(recordReg.value('NAME'))
        else:
            nameReg = nameCity
    stmtStreet = '''
    SELECT kladr.STREET.NAME, kladr.STREET.SOCR
    FROM kladr.STREET
    WHERE kladr.STREET.CODE = %s
    ''' % KLADRStreetCode
    queryStreet = db.query(stmtStreet)
    if queryStreet.first():
        recordStreet = queryStreet.record()
        nameStreet = forceString(recordStreet.value('NAME')) + ' ' + forceString(recordStreet.value('SOCR'))
    return [nameReg, nameCity, nameStreet]


class CRegistryClientInIEMK(QXmlStreamWriter):
    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)

    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeRegistryClientInIEMK(self, query, curDateTime, typeFlag):
        if typeFlag == 0:
            self.writeSoapHeaderCreate()
        elif typeFlag == 1:
            self.writeSoapHeaderModify()
        self.writeSoapBody(query, curDateTime, typeFlag)

    def writeSoapHeaderCreate(self):
        self.writeStartElement('soap:Header')
        self.writeTransportHeader()
        self.writeComment(u'Тип запроса (идентификатор операции сервиса).')
        self.writeTextElement('a:Action', u'urn:hl7-org:v3:PRPA_IN201301')
        self.writeComment(u'Уникальный ID сообщения. Должен быть указан в ответе на данный запрос')
        self.writeTextElement('a:MessageID', u'urn:uuid:%s' % uuid.uuid1())
        self.writeComment(u'При асинхронном запросе – URI сервиса обратного вызова (МИС), для отправки ответного сообщения')
        self.writeReplyTo()
        self.writeComment(u'Адрес конечной точки, куда отправляется данное сообщение')
        self.writeTextElement('a:To', u'https://api-iemc-test.rosminzdrav.ru/pix/pixSync?wsdl')
        self.writeEndElement()

    def writeSoapHeaderModify(self):
        self.writeStartElement('soap:Header')
        self.writeTransportHeader()
        self.writeComment(u'Тип запроса (идентификатор операции сервиса).')
        self.writeTextElement('a:Action', u'urn:hl7-org:v3:PRPA_IN201302')
        self.writeComment(u'Уникальный ID сообщения. Должен быть указан в ответе на данный запрос')
        self.writeTextElement('a:MessageID', u'urn:uuid:%s' % uuid.uuid1())
        self.writeComment(u'При асинхронном запросе – URI сервиса обратного вызова (МИС), для отправки ответного сообщения')
        self.writeReplyTo()
        self.writeComment(u'Адрес конечной точки, куда отправляется данное сообщение')
        self.writeTextElement('a:To', u'https://api-iemc-test.rosminzdrav.ru/pix/pixSync?wsdl')
        self.writeEndElement()

    def writeTransportHeader(self):
        self.writeStartElement('transportHeader')
        self.writeAttribute('xmlns', u'http://egisz.rosminzdrav.ru')
        self.writeAuthInfo()
        self.writeEndElement()

    def writeAuthInfo(self):
        self.writeStartElement('authInfo')
        self.writeTextElement('clientEntityId', u'0a65d58e-1c2a-4e0a-99bf-c776f2331c42')
        self.writeEndElement()

    def writeReplyTo(self):
        self.writeStartElement('a:ReplyTo')
        self.writeTextElement('a:Address', u'http://www.w3.org/2005/08/addressing/anonymous')
        self.writeEndElement()

    def writeSoapBody(self, query, curDateTime, typeFlag):
        self.writeStartElement('soap:Body')
        if typeFlag == 0:
            self.writeStartElement('PRPA_IN201301RU02')
        elif typeFlag == 1:
            self.writeStartElement('PRPA_IN201302RU02')
        self.writeAttribute('xmlns:xsi', u'http://www.w3.org/2001/XMLSchema-instance')
        if typeFlag == 0:
            self.writeAttribute('xsi:schemaLocation', u'urn:hl7-org:v3 ../../../../../../iemk-integration/iemk-integration-ws-api/src/main/resources/integration/schema/HL7V3/NE2008/multicacheschemas/PRPA_IN201301RU01.xsd')
        elif typeFlag == 1:
            self.writeAttribute('xsi:schemaLocation', u'urn:hl7-org:v3 ../../../../../../iemk-integration/iemk-integration-ws-api/src/main/resources/integration/schema/HL7V3/NE2008/multicacheschemas/PRPA_IN201302RU01.xsd')
        self.writeAttribute('xmlns', u'urn:hl7-org:v3')
        self.writeAttribute('ITSVersion', u'XML_1.0')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.5.1.13.3.25.67.19')
        self.writeAttribute('extension', forceString(uuid.uuid1()))
        self.writeEndElement()
        self.writeStartElement('creationTime')
        self.writeAttribute('value', curDateTime.toString('yyyyMMddhhmmss'))
        self.writeEndElement()
        self.writeStartElement('interactionId')
        self.writeAttribute('root', u'1.2.643.5.1.13.2.7.3')
        if typeFlag == 0:
            self.writeAttribute('extension', u'PRPA_IN201301RU02')
        elif typeFlag == 1:
            self.writeAttribute('extension', u'PRPA_IN201302RU02')
        self.writeEndElement()
        self.writeStartElement('processingCode')
        self.writeAttribute('code', 'P')
        self.writeEndElement()
        self.writeStartElement('processingModeCode')
        self.writeAttribute('code', 'T')
        self.writeEndElement()
        self.writeStartElement('acceptAckCode')
        self.writeAttribute('code', 'AL')
        self.writeEndElement()
        self.writeReceiver()
        self.writeSender()
        self.writeControlActProcess(query)
        self.writeEndElement()
        self.writeEndElement()

    def writeReceiver(self):
        self.writeStartElement('receiver')
        self.writeAttribute('typeCode', u'RCV')
        self.writeStartElement('device')
        self.writeAttribute('classCode', u'DEV')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('root', u'd5a0f9c0-5db4-11e3-949a-0800200c9a66')
        self.writeEndElement()
        self.writeTextElement('name', u'ИЭМК')
        self.writeAsAgentReceiver()
        self.writeEndElement()
        self.writeEndElement()

    def writeAsAgentReceiver(self):
        self.writeStartElement('asAgent')
        self.writeAttribute('classCode', u'ASSIGNED')
        self.writeStartElement('representedOrganization')
        self.writeAttribute('classCode', u'ORG')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.5.1.13')
        self.writeEndElement()
        self.writeTextElement('name', u'МЗ РФ')
        self.writeEndElement()
        self.writeEndElement()

    def writeSender(self):
        self.writeStartElement('sender')
        self.writeAttribute('typeCode', u'SND')
        self.writeStartElement('device')
        self.writeAttribute('classCode', u'DEV')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('root', u'0a65d58e-1c2a-4e0a-99bf-c776f2331c42')
        self.writeEndElement()
        self.writeTextElement('name', u'VistaMed')
        self.writeAsAgentSender()
        self.writeEndElement()
        self.writeEndElement()

    def writeAsAgentSender(self):
        self.writeStartElement('asAgent')
        self.writeAttribute('classCode', u'ASSIGNED')
        self.writeStartElement('representedOrganization')
        self.writeAttribute('classCode', u'ORG')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.5.1.13.3.25.67.19')
        self.writeEndElement()
        self.writeTextElement('name', u'''ОГАУЗ 'СОМИАЦ' ''')
        self.writeEndElement()
        self.writeEndElement()

    def writeControlActProcess(self, query):
        self.writeStartElement('controlActProcess')
        self.writeAttribute('classCode', u'CACT')
        self.writeAttribute('moodCode', u'EVN')
        while query.next():
            record = query.record()
            self.writeStartElement('subject')
            self.writeAttribute('typeCode', u'SUBJ')
            self.writeStartElement('registrationEvent')
            self.writeAttribute('classCode', u'REG')
            self.writeAttribute('moodCode', u'EVN')
            self.writeStartElement('id')
            self.writeAttribute('nullFlavor', u'NA')
            self.writeEndElement()
            self.writeStartElement('statusCode')
            self.writeAttribute('code', u'active')
            self.writeEndElement()
            self.writeSubject1(record)
            self.writeCustodian()
            self.writeEndElement()
            self.writeEndElement()
        self.writeEndElement()

    def writeSubject1(self, record):
        self.writeStartElement('subject1')
        self.writeAttribute('typeCode', u'SBJ')
        self.writeStartElement('patient')
        self.writeAttribute('classCode', u'PAT')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.5.1.13.3.25.67.19')
        self.writeAttribute('extension', forceString(record.value('clientId')))
        self.writeEndElement()
        self.writeStartElement('statusCode')
        self.writeAttribute('code', u'active')
        self.writeEndElement()
        self.writePatientPerson(record)
        self.writeProviderOrganization(record)
        self.writeEndElement()
        self.writeEndElement()

    def writePatientPerson(self, record):
        self.writeStartElement('patientPerson')
        self.writeStartElement('name')
        self.writeTextElement('family', forceString(record.value('lastName')))
        self.writeTextElement('given', forceString(record.value('firstName')))
        if forceString(record.value('patrName')):
            self.writeTextElement('given', forceString(record.value('patrName')))
        self.writeEndElement()
        if forceString(record.value('clientContact')) and forceString(record.value('contactTypeCode')):
            contactType = forceInt(record.value('contactTypeCode'))
            if contactType == 4:
                type = u'mailto:'
            else:
                type = u'tel:'
            self.writeStartElement('telecom')
            self.writeAttribute('value', type + forceString(record.value('clientContact')) )
            self.writeEndElement()
        self.writeStartElement('administrativeGenderCode')
        self.writeAttribute('code', forceString(record.value('sex')))
        self.writeAttribute('codeSystem', u'1.2.643.5.1.13.2.1.1.156')
        self.writeEndElement()
        self.writeStartElement('birthTime')
        if forceTime(record.value('birthTime')).toString('hhmmss') != '000000' :
            self.writeAttribute('value', forceDate(record.value('birthDate')).toString('yyyyMMdd') + forceTime(record.value('birthTime')).toString('hhmmss'))
        else:
            self.writeAttribute('value', forceDate(record.value('birthDate')).toString('yyyyMMdd'))
        self.writeEndElement()
        KLADRCode = forceString(record.value('KLADRCode'))
        KLADRStreetCode = forceString(record.value('KLADRStreetCode'))
        freeInput = forceString(record.value('freeInput'))
        if freeInput or KLADRCode:
            self.writeStartElement('addr')
            if forceInt(record.value('KLADRCode')) and forceInt(record.value('KLADRStreetCode')):
                houseNumber = forceString(record.value('houseNumber'))
                houseCorpus = forceString(record.value('corpus'))
                flat = forceString(record.value('flat'))
                if KLADRCode:
                    self.writeTextElement('country', u'Российская Федерация')
                    region = getMainRegionName(KLADRCode)
                    city = getCityName(KLADRCode)
                    # FIXME: лучше, наверное, определять города федерального подчинения по полю STATUS в кладре.
                    if region != city:
                        self.writeTextElement('state', region)
                    self.writeTextElement('city', city)
                    self.writeTextElement('unitID', KLADRCode)
                #FIXME: если выгрузка будет медленно работать, возможно стоит заменить getStreetName на обработку полей из уже имеющегося запроса
                if KLADRStreetCode:
                    self.writeTextElement('streetName', getStreetName(KLADRStreetCode))
                if houseNumber:
                    self.writeTextElement('houseNumber', houseNumber)
                # FIXME: что делать с корпусом???
                if flat:
                    self.writeTextElement('additionalLocator', flat)
            if freeInput:
                self.writeTextElement('streetAddressLine', freeInput)
            self.writeEndElement()
        self.writeComment(u'социальный статус')
        #self.writeAsMemberSoc(record)
        self.writeComment(u'льготная категория населения')
        #self.writeAsMemberFacilities(record)
        self.writeComment(u'СНИЛС')
        if forceString(record.value('SNILS')):
            self.writeAsOtherDsSNILS(record)
        self.writeComment(u'ОМС')
        if forceString(record.value('policyNumber')) and forceString(record.value('policySerial')) and forceString(record.value('insurerName'))\
                or forceString(record.value('policyNumber')) and forceString(record.value('policySerial')):
            self.writeAsOtherDsOMS(record)
        self.writeComment(u'паспорт')
        if forceString(record.value('documentNumber')) and forceString(record.value('documentSerial')) and forceString(record.value('documentOrg'))\
                or forceString(record.value('documentNumber')) and forceString(record.value('documentSerial')):
            self.writeAsOtherDsPass(record)
        self.writeComment(u'место рождения')
        #self.writeBirthPlace(record)
        self.writeEndElement()

    def writeAsMemberSoc(self, record):
        self.writeStartElement('asMember')
        #
        self.writeStartElement('group')
        #
        self.writeStartElement('code')
        #
        #
        #
        self.writeEndElement()
        self.writeEndElement()
        self.writeEndElement()

    def writeAsMemberFacilities(self, record):
        self.writeStartElement('asMember')
        #
        self.writeStartElement('group')
        #
        self.writeStartElement('code')
        #
        #
        #
        self.writeEndElement()
        self.writeEndElement()
        self.writeEndElement()

    def writeAsOtherDsSNILS(self, record):
        self.writeStartElement('asOtherIDs')
        self.writeAttribute('classCode', u'IDENT')
        self.writeEmptyElement('documentType')
        self.writeAttribute('code', '3')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.62')
        self.writeEmptyElement('documentNumber')
        self.writeAttribute('number', forceString(record.value('SNILS')))
        self.writeStartElement('scopingOrganization')
        self.writeAttribute('classCode', u'ORG')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.3.9')
        self.writeAttribute('extension', u'PFR')
        self.writeEndElement()
        self.writeEndElement()
        self.writeEndElement()

    def writeAsOtherDsOMS(self, record):
        self.writeStartElement('asOtherIDs')
        self.writeAttribute('classCode', u'HLD')
        self.writeEmptyElement('documentType')
        self.writeAttribute('code', '1')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.62')
        self.writeEmptyElement('documentNumber')
        self.writeAttribute('number', forceString(record.value('policySerial')) + forceString(record.value('policyNumber')))
        self.writeEmptyElement('effectiveTime')
        self.writeAttribute('value', forceDate(record.value('policyBegDate')).toString('yyyyMMdd'))
        self.writeStartElement('scopingOrganization')
        self.writeAttribute('classCode', u'ORG')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.5.1.13.2.1.1.635')
        self.writeAttribute('extension', forceString(record.value('insurerCode')))
        #self.writeAttribute('extension', u'0')
        self.writeEndElement()
        if forceString(record.value('insurerName')):
            self.writeTextElement('name', forceString(record.value('insurerName')))
        self.writeEndElement()
        self.writeEndElement()

    def writeAsOtherDsPass(self, record):
        self.writeStartElement('asOtherIDs')
        self.writeAttribute('classCode', u'IDENT')
        self.writeStartElement('documentType')
        self.writeAttribute('code', '5')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.62')
        self.writeStartElement('qualifier')
        self.writeEmptyElement('name')
        docTypeCode = forceString(record.value('docTypeCode'))
        self.writeAttribute('code', docTypeCode if docTypeCode else '14')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.498')
        self.writeAttribute('codeSystemName', u'Классификатор документов, удостоверяющих личность гражданина Российской Федерации')
        #FIXME: заменить на значение из rbDocumentType. Заменить названия в справочнике на соответствующие федеральным.
        self.writeAttribute('displayName', u'Паспорт гражданина РФ')
        self.writeEndElement()                          # qualifier
        self.writeEndElement()                          # documentType
        self.writeEmptyElement('documentNumber')
        self.writeAttribute('number', forceString(record.value('documentSerial')) + forceString(record.value('documentNumber')))
        if forceString(record.value('documentDate')):
            self.writeStartElement('effectiveTime')
            self.writeAttribute('value', forceDate(record.value('documentDate')).toString('yyyyMMdd'))
            self.writeEndElement()                      # effectiveTime
        self.writeStartElement('scopingOrganization')
        self.writeAttribute('classCode', u'ORG')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('nullFlavor', u'NA')
        self.writeEndElement()                          # id
        #if forceString(record.value('documentOrg')):
        self.writeTextElement('name', forceString(record.value('documentOrg')))
        self.writeEndElement()                          # scopingOrganisation
        self.writeEndElement()                          # asOtherIDs

    def writeBirthPlace(self, record):
        addr = forceString(record.value('birthPlace'))
        if addr:
            addr = addr.split(',')
            if len(addr)>1:
                birthYear = forceInt(forceDate(record.value('birthDate')).toString('yyyy'))
                birthMonth = forceInt(forceDate(record.value('birthDate')).toString('MM'))
                birthDay = forceInt(forceDate(record.value('birthDate')).toString('dd'))
                if birthYear >= 1991 and birthMonth >= 12 and birthDay >= 26:
                    addr[1] = u'Российская Федерация'
                else:
                    addr[1] = u'CCCP'
            self.writeStartElement('birthPlace')
            self.writeStartElement('addr')
            self.writeTextElement('city', addr[0])
            if len(addr)>1:
                self.writeTextElement('state', addr[1])
            self.writeEndElement()
            self.writeEndElement()

    def writeProviderOrganization(self, record):
        self.writeStartElement('providerOrganization')
        self.writeAttribute('classCode', u'ORG')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.5.1.13.3.25.67.19')
        self.writeEndElement()
        self.writeTextElement('name', u'''ОГАУЗ 'СОМИАЦ' ''')
        self.writeStartElement('contactParty')
        self.writeAttribute('classCode', u'CON')
        if forceString(record.value('orgPhone')):
            self.writeStartElement('telecom')
            self.writeAttribute('value', u'tel:' + forceString(record.value('orgPhone')))
            self.writeEndElement()
        self.writeEndElement()
        self.writeEndElement()

    def writeCustodian(self):
        self.writeStartElement('custodian')
        self.writeAttribute('typeCode', u'CST')
        self.writeStartElement('assignedEntity')
        self.writeAttribute('classCode', u'ASSIGNED')
        self.writeStartElement('id')
        self.writeAttribute('root', u'1.2.643.5.1.13.3.25.67.19')
        self.writeEndElement()
        self.writeStartElement('assignedOrganization')
        self.writeAttribute('classCode', u'ORG')
        self.writeAttribute('determinerCode', u'INSTANCE')
        self.writeTextElement('name', u'''ОГАУЗ 'СОМИАЦ' ''')
        self.writeEndElement()
        self.writeEndElement()
        self.writeEndElement()

    def writeFileHeader(self, device):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartElement('soap:Envelope')
        self.writeAttribute('xmlns:soap', u'http://www.w3.org/2003/05/soap-envelope')
        self.writeAttribute('xmlns:urn', u'urn:hl7-org:v3')
        self.writeAttribute('xmlns:a', u'http://www.w3.org/2005/08/addressing')

    def writeFileFooter(self):
        self.writeEndElement()


# *****************************************************************************************

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-t', dest='datetime', default=None)
    parser.add_argument('-a', dest='host', default='37.44.41.26')
    parser.add_argument('-p', dest='port', type=int, default='63306')
    parser.add_argument('-d', dest='database', default='iemk')
    parser.add_argument('-D', dest='dir', default=os.getcwd())
    parser.add_argument('-T', dest='type', default='c')
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)

    app = QtCore.QCoreApplication(sys.argv)
    connectionInfo = {
                          'driverName' : 'MYSQL',
                          'host' : args['host'],
                          'port' : args['port'],
                          'database' : args['database'],
                          'user' : args['user'],
                          'password' : args['password'],
                          'connectionName' : 'IEMK',
                          'compressData' : True,
                          'afterConnectFunc' : None
                    }

    db = connectDataBaseByInfo(connectionInfo)
    QtGui.qApp.db = db
    curDateTime = QtCore.QDateTime.currentDateTime()
    dt = args['datetime']
    dt = QDateTime.fromString(dt, 'yyyy-MM-ddTHH:mm:ss') if dt else curDateTime.addSecs(-86400)
    typeDatetime = args['type']
    if typeDatetime == 'c':
        strTypeDatetime = u'Client.createDatetime'
        typeFlag = 0
    elif typeDatetime == 'm':
        strTypeDatetime = u'Client.modifyDatetime'
        typeFlag = 1
    else:
        print 'Error: wrong type'
        sys.exit(-4)
    stmt = '''
        SELECT Client.id as clientId,
               Client.lastName,
               Client.firstName,
               Client.patrName,
               rbContactType.code as contactTypeCode,
               ClientContact.contact as contactClient,
               Client.sex,
               Client.birthDate,
               Client.birthTime,
               AddressHouse.KLADRCode,
               AddressHouse.KLADRStreetCode,
               AddressHouse.number as houseNumber,
               AddressHouse.corpus as houseCorpus,
               ClientAddress.freeInput as freeInput,
               Address.flat as flat,
               Client.SNILS,
               ClientPolicy.serial as policySerial,
               ClientPolicy.number as policyNumber,
               ClientPolicy.begDate as policyBegDate,
               Organisation.fullName as insurerName,
               Organisation.obsoleteInfisCode as insurerCode,
               ClientDocument.serial as documentSerial,
               ClientDocument.number as documentNumber,
               ClientDocument.date as documentDate,
               ClientDocument.origin as documentOrg,
               Client.birthPlace,
               Organisation.phone as orgPhone,
               rbDocumentType.federalCode as docTypeCode
        FROM Client
        LEFT JOIN ClientContact ON ClientContact.client_id = Client.id AND ClientContact.deleted = 0
        LEFT JOIN rbContactType ON rbContactType.id = ClientContact.contactType_id
        LEFT JOIN ClientAddress ON ClientAddress.id = getClientRegAddressId(Client.id)
        LEFT JOIN Address ON Address.id = ClientAddress.address_id AND Address.deleted = 0
        LEFT JOIN AddressHouse ON AddressHouse.id = Address.house_id AND AddressHouse.deleted = 0
        LEFT JOIN ClientPolicy ON ClientPolicy.id = getClientPolicyId(Client.id, 1)
        LEFT JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id AND Organisation.deleted = 0
        LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND ClientDocument.deleted = 0
        LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id AND rbDocumentType.code = 1
        WHERE (%s >= TIMESTAMP('%s') OR IFNULL(TIMESTAMP(Client.notes), TIMESTAMP('0000-00-00')) >= TIMESTAMP('%s'))  AND Client.deleted = 0
    ''' % (strTypeDatetime, dt.toString('yyyy-MM-dd hh:mm:ss'), dt.toString('yyyy-MM-dd hh:mm:ss'))
    query = db.query(stmt)
    if query.size() > 0:
        if typeFlag == 0:
            fileName = u'RCIEMK_%s.xml' % (curDateTime.toString('yyMMddThhmmss.zzz'))
        elif typeFlag == 1:
            fileName = u'RMIEMK_%s.xml' % (curDateTime.toString('yyMMddThhmmss.zzz'))
        if not (dt is None or dt.isValid()):
            print 'Error: incorrect base datetime.'
            sys.exit(-4)
        outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        clientsOut = CRegistryClientInIEMK(None)
        clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        clientsOut.writeFileHeader(outFile)
        clientsOut.writeRegistryClientInIEMK(query, curDateTime, typeFlag)
        clientsOut.writeFileFooter()
        outFile.close()

if __name__ == '__main__':
    main()