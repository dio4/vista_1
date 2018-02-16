# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils              import forceInt, forceRef, forceString, forceStringEx, getVal
from Orgs.Utils                 import getOrgStructureDescendants, getOrgStructures
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.EventResultSurvey  import CEventResultSetupDialog, STRICT_ADDRESS, NONRESIDENT_ADDRESS


def selectData(params):
    begDate                 = params.get('begDate', QtCore.QDate())
    endDate                 = params.get('endDate', QtCore.QDate())
    eventPurposeId          = params.get('eventPurposeId', None)
    eventTypeId             = params.get('eventTypeId', None)
    orgStructureId          = params.get('orgStructureId', None)
    specialityId            = params.get('specialityId', None)
    personId                = params.get('personId', None)
    workOrgId               = params.get('workOrgId', None)
    sex                     = params.get('sex', 0)
    ageFrom                 = params.get('ageFrom', 0)
    ageTo                   = params.get('ageTo', 150)
    areaIdEnabled           = params.get('areaIdEnabled', False)
    chkOrgStructureArea     = params.get('chkOrgStructureArea', False)
    areaId                  = params.get('areaId', None)
    MKBFilter               = params.get('MKBFilter', 0)
    MKBFrom                 = params.get('MKBFrom', 'A00')
    MKBTo                   = params.get('MKBTo', 'Z99.9')
    MKBExFilter             = params.get('MKBExFilter', 0)
    MKBExFrom               = params.get('MKBExFrom', 'A00')
    MKBExTo                 = params.get('MKBExTo', 'Z99.9')

    addressEnabled          = params.get('addressEnabled', False)
    addressType             = params.get('addressType', 0)
    clientAddressType       = params.get('clientAddressType', 0)
    clientAddressCityCode   = params.get('clientAddressCityCode', None)
    clientAddressCityCodeList = params.get('clientAddressCityCodeList', None)
    clientAddressStreetCode = params.get('clientAddressStreetCode', None)
    clientHouse             = params.get('clientHouse', '')
    clientCorpus            = params.get('clientCorpus', '')
    clientFlat              = params.get('clientFlat', '')

    order                   = params.get('order', 0)
    primary                 = params.get('primary', 0)
    resultId                = params.get('resultId', None)
    
    visitEmergency = params.get('visitEmergency', False)

    db = QtGui.qApp.db

    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableClientAddress = db.table('ClientAddress')
    tableAddress = db.table('Address')
    tableOrgStructureAddress = db.table('OrgStructure_Address')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableResult = db.table('rbResult')

    tableAddressHouseLiv = db.table('AddressHouse').alias('AddressHouseLiv')
    tableClientAddressForClientLiv = db.table('ClientAddress').alias('ClientAddressForClientLiv')
    tableAddressForClientLiv = db.table('Address').alias('AddressForClientLiv')

    tableAddressHouseReg = db.table('AddressHouse').alias('AddressHouseReg')
    tableClientAddressForClientReg = db.table('ClientAddress').alias('ClientAddressForClientReg')
    tableAddressForClientReg = db.table('Address').alias('AddressForClientReg')

    tableKLADRCodeReg = db.table('kladr.KLADR')
    tableKLADRStreetReg = db.table('kladr.STREET')

    tableClientContact = db.table('ClientContact')
    tableContactType = db.table('rbContactType')
    tableVisit = db.table('Visit')
    tableScene = db.table('rbScene')

    queryTable = tableEvent

    queryTable = queryTable.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.leftJoin(tableClientContact, tableClientContact['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableContactType, tableContactType['id'].eq(tableClientContact['contactType_id']))
    queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    queryTable = queryTable.leftJoin(tableClientAddress, tableClientAddress['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
    queryTable = queryTable.leftJoin(tableVisit, tableEvent['id'].eq(tableVisit['event_id']))
    queryTable = queryTable.leftJoin(tableScene, tableScene['id'].eq(tableVisit['scene_id']))

    diagnosticJoinCond = '''Diagnostic.event_id = Event.id AND Diagnostic.id IN
                                (SELECT D1.id
                                    FROM Diagnostic AS D1
                                    LEFT JOIN rbDiagnosisType AS DT1 ON DT1.id = D1.diagnosisType_id
                                    WHERE D1.event_id = Event.id AND DT1.code =
                                        (SELECT MIN(DT2.code)
                                            FROM Diagnostic AS D2
                                            LEFT JOIN rbDiagnosisType AS DT2 ON DT2.id = D2.diagnosisType_id WHERE D2.event_id = Event.id
                                        )
                                 )'''
    queryTable = queryTable.leftJoin(tableDiagnostic, diagnosticJoinCond)
    queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
    queryTable = queryTable.leftJoin(tableDiagnosisType, tableDiagnosisType['id'].eq(tableDiagnosis['diagnosisType_id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))

    joinCondClientAddressForClientReg = 'ClientAddressForClientReg.client_id = Event.client_id AND ClientAddressForClientReg.id = (SELECT MAX(id) FROM ClientAddress AS CAReg WHERE CAReg.Type=0 and CAReg.client_id = Event.client_id)'
    queryTable = queryTable.leftJoin(tableClientAddressForClientReg, joinCondClientAddressForClientReg)
    queryTable = queryTable.leftJoin(tableAddressForClientReg, tableAddressForClientReg['id'].eq(tableClientAddressForClientReg['address_id']))
    queryTable = queryTable.leftJoin(tableAddressHouseReg, tableAddressHouseReg['id'].eq(tableAddressForClientReg['house_id']))

    queryTable = queryTable.leftJoin(tableKLADRCodeReg, tableKLADRCodeReg['CODE'].eq(tableAddressHouseReg['KLADRCode']))
    queryTable = queryTable.leftJoin(tableKLADRStreetReg, tableKLADRStreetReg['CODE'].eq(tableAddressHouseReg['KLADRStreetCode']))

    joinCondClientAddressForClientLiv = 'ClientAddressForClientLiv.client_id = Event.client_id AND ClientAddressForClientLiv.id = (SELECT MAX(id) FROM ClientAddress AS CALiv WHERE CALiv.Type=0 and CALiv.client_id = Event.client_id)'
    queryTable = queryTable.leftJoin(tableClientAddressForClientLiv, joinCondClientAddressForClientLiv)
    queryTable = queryTable.leftJoin(tableAddressForClientLiv, tableAddressForClientLiv['id'].eq(tableClientAddressForClientLiv['address_id']))
    queryTable = queryTable.leftJoin(tableAddressHouseLiv, tableAddressHouseLiv['id'].eq(tableAddressForClientLiv['house_id']))

    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(db.joinOr([tableEvent['execDate'].lt(endDate.addDays(1)), tableEvent['execDate'].isNull()]))
#    cond.append(tableClientContact['deleted'].eq(0))

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        cond.append(db.table('EventType')['purpose_id'].eq(eventPurposeId))
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if personId:
        cond.append(tableDiagnostic['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if workOrgId:
        cond.append('EXISTS (SELECT * FROM ClientWork WHERE ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id) and ClientWork.org_id=%d)' % (workOrgId))
    if not visitEmergency:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'4\')))''''')
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        date = str(QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate))
        cond.append('IF(Diagnosis.endDate IS NOT NULL, Diagnosis.endDate, DATE(\'%s\')) >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%(date, ageFrom))
        cond.append('IF(Diagnosis.endDate IS NOT NULL, Diagnosis.endDate, DATE(\'%s\')) <  SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(date, ageTo+1))

    if areaIdEnabled:
        if chkOrgStructureArea:
            if areaId:
                orgStructureIdList = getOrgStructureDescendants(areaId)
            else:
                orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
            subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
                        tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                      ]
            cond.append(db.existsStmt(tableOrgStructureAddress, subCond))

        if addressEnabled:
            if addressType in [STRICT_ADDRESS, NONRESIDENT_ADDRESS]:
                clientAddressType = clientAddressType if addressType == STRICT_ADDRESS else 0
                if clientAddressType == 0:
                    tableAddressForClient = tableAddressForClientReg
                    tableAddressHouse = tableAddressHouseReg
                else:
                    tableAddressForClient = tableAddressForClientLiv
                    tableAddressHouse = tableAddressHouseLiv
                if addressType == STRICT_ADDRESS:
                    if clientFlat:
                        cond.append(tableAddressForClient['flat'].eq(clientFlat))
                    if clientCorpus:
                        cond.append(tableAddressHouse['corpus'].eq(clientCorpus))
                    if clientHouse:
                        cond.append(tableAddressHouse['number'].eq(clientHouse))
                    if clientAddressCityCodeList:
                        cond.append(tableAddressHouse['KLADRCode'].inlist(clientAddressCityCodeList))
                    else:
                        if clientAddressCityCode:
                            cond.append(tableAddressHouse['KLADRCode'].eq(clientAddressCityCode))
                    if clientAddressStreetCode:
                        cond.append(tableAddressHouse['KLADRStreetCode'].eq(clientAddressStreetCode))
                else:
                    props = QtGui.qApp.preferences.appPrefs
                    kladrCodeList = [forceString(getVal(props, 'defaultKLADR', '')), forceString(getVal(props, 'provinceKLADR', ''))]
                    cond.append(tableAddressHouse['KLADRCode'].notInlist(kladrCodeList))
            else:
                foreignDocumentTypeId = forceInt(db.translate('rbDocumentType', 'code', '9', 'id'))
                documentCond = 'EXISTS(SELECT ClientDocument.`id` FROM ClientDocument WHERE ClientDocument.`documentType_id`=%d AND ClientDocument.`client_id`=Client.`id`)'%foreignDocumentTypeId
                cond.append(documentCond)


    if order:
        cond.append(tableEvent['order'].eq(order-1))

    if primary:
        cond.append(tableEvent['isPrimary'].eq(primary))

    if resultId:
        cond.append(tableEvent['result_id'].eq(resultId))

    fields = ['CONCAT_WS(\' \', Client.`lastName`, Client.`firstName`, Client.`patrName`) AS fio',
              tableClient['sex'].name(),
              'IF(MONTH(Client.`birthDate`)>MONTH(CURRENT_DATE()) OR (MONTH(Client.`birthDate`) = MONTH(CURRENT_DATE()) AND DAYOFMONTH(Client.`birthDate`) > DAYOFMONTH(CURRENT_DATE())), YEAR(CURRENT_DATE())-YEAR(Client.`birthDate`)-1, YEAR(CURRENT_DATE())-YEAR(Client.`birthDate`)) AS clientAge',
              tableClient['id'].alias('clientId'),
              tableAddressForClientReg['flat'].alias('clientFlat'), tableAddressHouseReg['corpus'].alias('clientCorpus'), tableAddressHouseReg['number'].alias('clientNumber'),
              tableKLADRCodeReg['NAME'].alias('kladrName'), tableKLADRCodeReg['SOCR'].alias('kladrSocr'),
              tableKLADRStreetReg['NAME'].alias('kaldrStreetName'), tableKLADRStreetReg['SOCR'].alias('kladrStreetSocr'),
              tableClientContact['contact'].alias('clientContact'), tableContactType['name'].alias('contactTypeName'),
              tableDiagnosis['MKB'].name(), tableEventType['code'].alias('eventTypeCode'), tableEventType['name'].alias('eventTypeName'),
              tableEvent['setDate'].alias('eventSetDate'), tableEvent['execDate'].alias('eventExecDate'),
              tableEvent['id'].alias('eventId'), tableClientContact['id'].alias('clientContactId'),
              tableClientContact['deleted'].alias('contactDeleted'),
              tablePerson['name'].alias('person'),
              tableScene['name'].alias('scene')]

    stmt = db.selectStmt(queryTable, fields, cond,  order = 'fio')
#    print stmt
    return db.query(stmt)




class CReportEventResultList(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Список пациентов')
        self._data = {}
        self.clientIdList = []

    def structData(self, query):
        self.resetHelpers()
        eventIdList = []
        clientContactIdList = []
        while query.next():
            record = query.record()

            clientId = forceRef(record.value('clientId'))
            clientData = self._data.get(clientId, None)
            if clientData is None:
                self.clientIdList.append(clientId)
                fio = forceString(record.value('fio'))
                clientAge = forceInt(record.value('clientAge'))
                clientSex = forceInt(record.value('sex'))
                if clientSex == 1:
                    clientSex = u'М'
                elif clientSex == 2:
                    clientSex = u'Ж'
                else:
                    clientSex = ''
                clientFlat = forceString(record.value('clientFlat'))
                clientFlat = u'кв.'+clientFlat if clientFlat else ''
                clientCorpus = forceString(record.value('clientCorpus'))
                clientCorpus = u'крп.'+clientCorpus if clientCorpus else ''
                clientNumber = forceString(record.value('clientNumber'))
                clientNumber = u'д. '+clientNumber if clientNumber else ''
                kladrName = forceString(record.value('kladrName'))
                kladrSocr = forceString(record.value('kladrSocr'))
                kaldrStreetName = forceString(record.value('kaldrStreetName'))
                kladrStreetSocr = forceString(record.value('kladrStreetSocr'))
                clientAddress = u', '.join([forceStringEx(val) for val in [kladrName+' '+kladrSocr,
                                                        kaldrStreetName+' '+kladrStreetSocr,
                                                        clientNumber, clientCorpus, clientFlat] if forceStringEx(val)])
                clientData = {'fio':fio,
                              'clientAge':clientAge,
                              'clientSex': clientSex,
                              'clientAddress': clientAddress,
                              'contactList': [],
                              'eventList': []}
                self._data[clientId] = clientData
            eventId = forceRef(record.value('eventId'))
            if not eventId in eventIdList:
                eventIdList.append(eventId)

                eventTypeCode = forceString(record.value('eventTypeCode'))
                eventTypeName = forceString(record.value('eventTypeName'))
                eventSetDate = forceString(record.value('eventSetDate'))
                eventExecDate = forceString(record.value('eventExecDate'))
                MKB = forceString(record.value('MKB'))
                scene = forceString(record.value('scene'))
                person = forceString(record.value('person'))

                clientData['eventList'].append(
                                               {'MKB':MKB, 'eventType': eventTypeCode+' | '+eventTypeName,
                                                'eventSetDate':eventSetDate, 'eventExecDate':eventExecDate,
                                                'scene': scene if not scene == u'поликлиника' else u'амбулаторно',
                                                'person': person
                                               }
                                              )
            clientContactId = forceRef(record.value('clientContactId'))
            contactDeleted  = forceInt(record.value('contactDeleted'))
            if (not clientContactId in clientContactIdList) and (contactDeleted == 0):
                clientContactIdList.append(clientContactId)

                clientContact = forceString(record.value('clientContact'))
                contactTypeName = forceString(record.value('contactTypeName'))

                clientData['contactList'].append(u': '.join([val for val in [contactTypeName, clientContact] if forceStringEx(val)]))






    def getSetupDialog(self, parent):
        result = CEventResultSetupDialog(parent)
        result.setVisibleResult(True)
        result.setVisiblePrimary(True)
        result.setVisibleOrder(True)
        result.setVisibleAdditionlOutput(True)
        result.setTitle(self.title())
        result.setVisibleVisitEmergency(True)
        return result

    def resetHelpers(self):
        self._data.clear()
        self.clientIdList = []

    def build(self, params):
        person = params.get('person', False)
        visitPlace = params.get('visitPlace', False)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.structData(query)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('2%',  [u'№' ],                     CReportBase.AlignRight),
            ('13%', [u'ФИО'],                    CReportBase.AlignLeft),
            ('2%', [u'Пол'],                     CReportBase.AlignLeft),
            ('4%', [u'Возраст'],                 CReportBase.AlignRight),
            ('7%', [u'Идентификатор пациента'],  CReportBase.AlignLeft),
            ('15%', [u'Адрес'],                  CReportBase.AlignLeft),
            ('7%', [u'Контакты'],                CReportBase.AlignLeft),
            ('2%', [u'Номер обращения'],         CReportBase.AlignRight),
            ('5%', [u'Закл. диагноз'],           CReportBase.AlignLeft),
            ('20%', [u'Событие'],                CReportBase.AlignLeft),
            ('9%', [u'Дата начала'],             CReportBase.AlignLeft),
            ('9%', [u'Дата окончания'],          CReportBase.AlignLeft),
            ]

        if person:
            tableColumns.append(('20%', [u'Фамилия врача'],                CReportBase.AlignLeft))
        if visitPlace:
            tableColumns.append(('20%', [u'Место посещения'],                CReportBase.AlignLeft))
        countTableColumns = len(tableColumns)
        table = createTable(cursor, tableColumns)
        mergeLength = 6
        globalEventCount = 0
        countRowsClient = 0
        i = table.addRow()
        for idx, clientId in enumerate(self.clientIdList):
            clientData = self._data[clientId]

            if countRowsClient > 1:
                for index in xrange(7):
                    table.mergeCells(i - countRowsClient, index, countRowsClient, 1)
            countRowsClient = 0
            table.setText(i, 0, idx+1)
            table.setText(i, 1, clientData['fio'])
            table.setText(i, 2, clientData['clientSex'])
            table.setText(i, 3, clientData['clientAge'])
            table.setText(i, 4, clientId)
            table.setText(i, 5, clientData['clientAddress'])

            eventCount = len(clientData['eventList'])
            contactCount = len(clientData['contactList'])
            depth = max(eventCount, contactCount)

            # eventMKB = []
            # eventType = []
            # eventSetDate = []
            # eventExecDate = []
            # eventPerson = []
            # eventScene = []
            # contact = []
            # eventNumbers = []
            for additionalRow in xrange(depth):

                if additionalRow < contactCount:
                    table.setText(i, 6,  clientData['contactList'][additionalRow])
                    #eventNumbers.append(clientData['contract'])

                if additionalRow < eventCount:
                    event = clientData['eventList'][additionalRow]
                    globalEventCount += 1
                    table.setText(i, 7,  globalEventCount)
                    table.setText(i, 8,  event['MKB'])
                    table.setText(i, 9,  event['eventType'])
                    table.setText(i, 10, event['eventSetDate'])
                    table.setText(i, 11, event['eventExecDate'])
                    if person:
                        table.setText(i, countTableColumns - 2 if countTableColumns == 14 else countTableColumns - 1, event['person'])
                    if visitPlace:
                        table.setText(i, countTableColumns - 1, event['scene'])
                    # eventMKB.append(event['MKB'])
                    # eventType.append(event['eventType'])
                    # eventSetDate.append(event['eventSetDate'])
                    # eventExecDate.append(event['eventExecDate'])
                    # eventPerson.append(event['person'])
                    # eventScene.append(event['scene'])
                    # globalEventCount += 1
                    # eventNumbers.append(unicode(globalEventCount))

                i = table.addRow()
                countRowsClient += 1

            # table.setText(i, 6,  u'\n'.join(eventNumbers))
            # table.setText(i, 8,  u'\n'.join(eventMKB))
            # table.setText(i, 9,  u';\n'.join(eventType))
            # table.setText(i, 10, u'\n'.join(eventSetDate))
            # table.setText(i, 11, u'\n'.join(eventExecDate))


#                if additionalRow != depth-1:
#                    i = table.addRow()

#            if depth > 1:
#                table.mergeCells(i-(depth-2), 0, depth-1, mergeLength)
        for index in xrange(7):
            table.mergeCells(i - countRowsClient, index, countRowsClient, 1)
        for index in xrange(countTableColumns):
            table.mergeCells(i - countRowsClient, index, 2, 1)
        return doc




