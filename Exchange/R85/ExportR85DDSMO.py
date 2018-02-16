# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

import logging, os, zipfile

from PyQt4 import QtCore, QtGui, QtXml

from library.ProgressInformer import CProgressInformer
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceStringEx, getClassName, getPref, setPref, formatSNILS
from library.XML.XMLHelper import CXMLHelper

from ExportR85SMO import CExportDialog, CExportR85SMOEngine

def getAccountRecord(db, accountId):
    tableAccount = db.table('Account')
    tableContract = db.table('Contract')
    tableOrganisation = db.table('Organisation')

    cols = [tableAccount['date'].alias('accountDate'),
            tableAccount['number'].alias('accountNumber'),
            tableAccount['settleDate'].alias('accountSettleDate'),
            tableAccount['number'],
            tableOrganisation['infisCode'].alias('lpuInfis')]

    queryTable = tableAccount.innerJoin(tableContract, tableContract['id'].eq(tableAccount['contract_id']))
    queryTable = queryTable.innerJoin(tableOrganisation, tableOrganisation['id'].eq(tableContract['recipient_id']))
    return db.getRecordEx(queryTable,
                                cols,
                                where=tableAccount['id'].eq(accountId))

def exportR85DDSMO(widget, accountId):
    accountRecord = getAccountRecord(QtGui.qApp.db, accountId)
    if forceStringEx(accountRecord.value('number'))[:2].upper() in ['DP', 'DV', 'DO', 'DS', 'DU', 'DF', 'DD', 'DR']:
        engine = CExportR85DDSMOEngine
    else:
        engine = CExportR85SMOEngine
    exportWindow = CExportDialog(QtGui.qApp.db, accountId, engine, accountRecord, widget)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), {})
    exportWindow.setParams(params)
    exportWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), exportWindow.params())

class CExportR85DDSMOEngine(object):
    encoding = u'windows-1251'
    version = u'2.1'
    fundCode = u'85000'

    defaultDateFormat = QtCore.Qt.ISODate

    counterCode = 'smoCode'

    mapDispTypes = {'DP': u'ДВ1',
                    'DV': u'ДВ2',
                    'DO': u'ОПВ',
                    'DS': u'ДС1',
                    'DU': u'ДС2',
                    'DF': u'ОН1',
                    'DD': u'ОН2',
                    'DR': u'ОН3'}

    def __init__(self, db, accountRecord, progressInformer = None):
        self._db = db
        self._progressInformer = progressInformer if isinstance(progressInformer, CProgressInformer) \
                                                  else CProgressInformer(processEventsFlag=None)
        self._logger = logging.getLogger(name=getClassName(self))
        self._logger.setLevel(logging.INFO)
        self.accountRecord = accountRecord

        self.totalPhases = 0
        self.currentPhase = 0

        self.hDocuments = {}
        self.lDocuments = {}
        self.personSpecialityForDeferredFilling = {}
        self.orgForDeferredFilling = {}
        self.clientsForDeferredFilling = {}
        # self.firstVisitsForDeferredFilling = {}
        self.lpuInfis = None

        self._idPacMap = {}
        self.isTerminated = False
        self._counterId = None

    def logger(self):
        return self._logger

#----- XML Fillers -----

    def getCounterValue(self):
        if self._counterId is None:
            tableCounter = self._db.table('rbCounter')
            self._counterId = forceRef(self._db.translate(tableCounter, 'code', self.counterCode, 'id'))
            if self._counterId is None:

                newRecord = tableCounter.newRecord(fields=['code',
                                                           'value',
                                                           'name',
                                                           'reset',
                                                           'startDate'])
                newRecord.setValue('code', QtCore.QVariant(self.counterCode))
                newRecord.setValue('value', QtCore.QVariant(0))
                newRecord.setValue('name', QtCore.QVariant(u'Порядковый номер счета для выгрузки в СМО Крыма'))
                newRecord.setValue('reset', QtCore.QVariant(3)) # ежегодно
                year = QtCore.QDate.currentDate().year()
                newRecord.setValue('startDate', QtCore.QVariant(QtCore.QDate(year, 1, 1)))
                self._counterId = self._db.insertRecord(tableCounter, newRecord)
        query = self._db.query('SELECT getCounterValue(%d)' % self._counterId)
        if query.next():
            return forceInt(query.record().value(0))
        else:
            self.logger().critical(u'Не удалось получить значение счетчика для кода счета')
            return None

    def createHXMLDocument(self, exportNumber, insurerInfis, dispType):
        doc = CXMLHelper.createDomDocument(rootElementName='ZL_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        headerElement = self.addHeaderElement(rootElement, exportNumber, insurerInfis)
        accountElement = self.addAccountElement(rootElement, insurerInfis, dispType)
        return doc, accountElement, headerElement

    def createLXMLDocument(self, insurerInfis, exportNumber):
        doc = CXMLHelper.createDomDocument(rootElementName='PERS_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        header = self.addHeaderElement(rootElement, insurerInfis, exportNumber, lfile=True)
        return doc

    def addHeaderElement(self, rootElement, exportNumber, insurerInfis, lfile=False):
        header = CXMLHelper.addElement(rootElement, 'ZGLV')
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'VERSION'),
                            self.version[:5])
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'DATA'),
                            QtCore.QDate.currentDate().toString(self.defaultDateFormat))
        lpuInfis = forceStringEx(self.accountRecord.value('lpuInfis'))
        settleDate = forceDate(self.accountRecord.value('accountSettleDate'))
        numberAccount = forceStringEx(self.accountRecord.value('number'))
        if insurerInfis:
            fileName = u'%sM%sS%s_%s%d' % (numberAccount[:2],
                                           lpuInfis,
                                           insurerInfis,
                                           settleDate.toString('yyMM'),
                                           exportNumber)
        else:
            fileName = u'%sT85M%s_%s%d' % (numberAccount[:2],
                                          lpuInfis,
                                          settleDate.toString('yyMM'),
                                          exportNumber)

        if lfile:
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME'),
                                'L' + fileName[2:])
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME1'),
                                fileName)
        else:
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME'),
                                fileName)
        return header

    def addAccountElement(self, rootElement, insurerInfis, dispType):
        """
        Добавляет узел "SCHET"

        @param rootElement:
        @param record: QSqlRecord, из которой будут браться данные для заполнения.
            Необходимые поля:
                * **settleDate** (Account.settleDate)
                * **number** (Account.number)
                * **exposeDate** (Account.exposeDate)
        @return:
        """

        account = CXMLHelper.addElement(rootElement, 'SCHET')

        accDate = forceDate(self.accountRecord.value('accountSettleDate'))
        accCode = forceStringEx(self.getCounterValue())

        CXMLHelper.setValue(CXMLHelper.addElement(account, 'CODE'),
                            accCode[-8:])
        lpuInfis = forceStringEx(self.accountRecord.value('lpuInfis'))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'CODE_MO'),
                            lpuInfis)
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'YEAR'),
                            accDate.year())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'MONTH'),
                            accDate.month())
        nschet = lpuInfis + forceStringEx(accDate.toString('MM')) + accCode
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'NSCHET'),
                            nschet[:15])
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'DSCHET'),
                            forceDate(self.accountRecord.value('accountDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'PLAT'),
                            insurerInfis if insurerInfis.startswith('85') else '85000')

        CXMLHelper.addElement(account, 'SUMMAV')
        CXMLHelper.addElement(account, 'SUMMAP')
        CXMLHelper.addElement(account, 'SANK_MEK')
        # CXMLHelper.addElement(account, 'SANK_MEE')
        # CXMLHelper.addElement(account, 'SANK_EKMP')
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'DISP'),
                            dispType)
        return account

    def addEntryElement(self, rootElement, record, entryNumber):
        entryElement = CXMLHelper.addElement(rootElement, 'ZAP')
        CXMLHelper.setValue(CXMLHelper.addElement(entryElement, 'N_ZAP'),
                            entryNumber)
        CXMLHelper.setValue(CXMLHelper.addElement(entryElement, 'PR_NOV'),
                            1 if forceInt(record.value('rerun')) != 0 else 0) # FIXME: не так это должно определяться
        patientElement = CXMLHelper.addElement(entryElement, 'PACIENT')
        self.fillPacient(patientElement, record)
        return entryElement, patientElement

    def fillPacient(self, patientElement, record):
        """

        @param patientElement:
        @param record: QSqlRecord
            Необходимые поля:
            * **policyKindFederalCode** - rbPolicyKind.federalCode
            * **policySerial** - ClientPolicy.serial
            * **policyNumber** - ClientPolicy.number
            * **isLittleStranger** - Event.littleStranger_id IS NOT NULL
            * **insurerInfis** - Organisation.infisCode
            * **newbornBirthDate** - Event_LittleStranger.birthDate
            * **newbornSex** - Event_LittleStranger.sex
            * **newbornNumber** - Event_LittleStranger.number
            * **
        @return:
        """

        clientId = forceInt(record.value('clientId'))
        idPac = CExportR85SMOEngine.getExternalId(forceStringEx(record.value('externalId')), 'idpac', clientId)

        self._idPacMap[clientId] = idPac
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'ID_PAC'),
                            forceInt(record.value('clientId')))

        policyKind = forceInt(record.value('policyKindFedCode'))
        policySerial = forceStringEx(record.value('policySerial'))
        policyNumber = forceStringEx(record.value('policyNumber'))

        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'VPOLIS'),
                            policyKind)
        if policySerial:
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SPOLIS'),
                                policySerial[:10])
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'NPOLIS'),
                            policyNumber[:20])

        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'ST_OKATO'),
        #                     self.dummy)

        smoCode = forceStringEx(record.value('insurerInfis'))
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SMO'),
                            smoCode[:5])

        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SMO_OGRN'),
        #                     forceStringEx(record.value('insurerOGRN'))[:15])
        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SMO_OK'),
        #                     forceStringEx(record.value('insurerOKATO'))[:5])
        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SMO_NAM'),
        #                     forceStringEx(record.value('insurerNAME'))[:100])


    def addEventElement(self, entryElement, idCase, record):
        """

        @param entryElement:
        @param idCase:
        @param record:
        @return:
        """

        eventElement = CXMLHelper.addElement(entryElement, 'SLUCH')

        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDCASE'),
                            idCase)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VIDPOM'),
                            forceInt(record.value('eventTypeAidKindFedCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'LPU'),
                            self.lpuInfis)
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'LPU_1'),
        #                     self.dummy)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NHISTORY'),
                            CExportR85SMOEngine.getExternalId(forceStringEx(record.value('externalId')),
                                                              'nhistory',
                                                              forceStringEx(record.value('eventId')))[:50])
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_1'),
                            forceDate(record.value('eventSetDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_2'),
                            forceDate(record.value('eventExecDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DS1'),
                            forceStringEx(record.value('eventPrimaryMKB')))
        result = forceInt(record.value('eventResultFedCode'))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'RSLT_D'),
                            result if result else '')
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDSP'),
                            forceInt(record.value('eventAidUnitFedCode')))
        CXMLHelper.addElement(eventElement, 'ED_COL')
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'TARIF'),
        #                     '%.2f' % forceDouble(record.value('price')))

        CXMLHelper.addElement(eventElement, 'SUMV')
        CXMLHelper.addElement(eventElement, 'OPLATA')
        CXMLHelper.addElement(eventElement, 'SUMP')
        CXMLHelper.addElement(eventElement, 'SANK_IT')

        return eventElement

    def addSankElement(self, entryElement, idCase, record):
        sankElement = CXMLHelper.addElement(entryElement, 'SANK')

        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_CODE'),
                            idCase)
        CXMLHelper.addElement(sankElement, 'S_SUM')
        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_TIP'),
                            1)
        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_OSN'),
                            forceStringEx(record.value('accountItemRefuseCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_IST'),
                            1)
        return sankElement


    def addServiceElement(self, eventElement, idServ, record):
        """

        @param eventElement:
        @param idServ:
        @param record:
        @return:
        """
        serviceCode = forceStringEx(record.value('serviceCode'))

        serviceElement = CXMLHelper.addElement(eventElement, 'USL', afterElem=['USL', 'SANK', 'SANK_IT', 'SUMP', 'OPLATA'])

        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'IDSERV'),
                            forceStringEx(idServ)[:36])
        serviceOrgId = forceRef(record.value('actionOrgId')) \
                       or forceRef(record.value('eventOrgId'))
        self.orgForDeferredFilling.setdefault(serviceOrgId,
            []).append(CXMLHelper.addElement(serviceElement, 'LPU'))
        # CXMLHelper.addElement(serviceElement, 'LPU_1')

        serviceBegDate = forceDate(record.value('visitDate')) \
                         or forceDate(record.value('actionBegDate')) \
                         or forceDate(record.value('eventSetDate'))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'DATE_IN'),
                            serviceBegDate.toString(self.defaultDateFormat))
        serviceEndDate = forceDate(record.value('visitDate')) \
                         or forceDate(record.value('actionEndDate')) \
                         or forceDate(record.value('eventExecDate'))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'DATE_OUT'),
                            serviceEndDate.toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'TARIF'),
                            '%.2f' % forceDouble(record.value('servicePrice')))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'SUMV_USL'),
                            '%.2f' % forceDouble(record.value('serviceSum')))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'COMENTU'),
                            'service:%s#status:%s' % (serviceCode, forceInt(record.value('actionStatus'))))

        personId = forceRef(record.value('visitPersonId')) \
                   or forceRef(record.value('actionPersonId')) \
                   or forceRef(record.value('eventExecPersonId'))

        self.personSpecialityForDeferredFilling.setdefault(personId,
            []).append((CXMLHelper.addElement(serviceElement, 'PRVS'),
                       CXMLHelper.addElement(serviceElement, 'CODE_MD')))
        return serviceElement

    def fillPersonSpeciality(self):
        self.nextPhase(1, u'Загрузка данных по врачам')
        tablePerson = self._db.table('Person')
        tableSpeciality = self._db.table('rbSpeciality')
        recordList = self._db.getRecordList(table=tablePerson.leftJoin(tableSpeciality,
                                                                        tableSpeciality['id'].eq(tablePerson['speciality_id'])
                                                            ),
                                                  cols=[tablePerson['id'].alias('personId'),
                                                  tablePerson['federalCode'].alias('personFedCode'),
                                                  tableSpeciality['federalCode'].alias('specialityFedCode'),
                                                  "CONCAT_WS(' ', %s, %s, %s) AS personName" % (tablePerson['lastName'],
                                                                                                tablePerson['firstName'],
                                                                                                tablePerson['patrName'])
                                                  ],
                                            where=[tablePerson['id'].inlist(self.personSpecialityForDeferredFilling.keys())])

        self.nextPhase(len(recordList), u'Обработка данных по врачам')
        for record in recordList:
            if self.isTerminated:
                self.onTerminating()
                return
            personId = forceRef(record.value('personId'))
            elementList = self.personSpecialityForDeferredFilling.get(personId, [])
            personFederalCode = forceStringEx(record.value('personFedCode'))
            specialityFederalCode = forceStringEx(record.value('specialityFedCode'))
            personName = forceStringEx(record.value('personName'))
            if not personFederalCode:
                self.logger().warning(u'Не заполнен федеральный код врача {%s}"%s"' % (personId, personName))
            if not specialityFederalCode:
                self.logger().warning(u'Не заполнен федеральный код специальности у врача {%s}"%s"' % (personId, personName))
            for specialityElement, personElement in elementList:
                if personFederalCode:
                    CXMLHelper.setValue(personElement, personFederalCode)
                if specialityFederalCode:
                    CXMLHelper.setValue(specialityElement, specialityFederalCode)
            self.nextPhaseStep()

    def fillOrganisations(self):
        self.nextPhase(1, u'Загрузка данных по организациям')
        tableOrg = self._db.table('Organisation')
        recordList = self._db.getRecordList(table=tableOrg,
                                            cols=[tableOrg['id'].alias('orgId'),
                                                  tableOrg['infisCode'],
                                                  tableOrg['shortName']],
                                            where=[tableOrg['id'].inlist(self.orgForDeferredFilling.keys()),
                                                   tableOrg['deleted'].eq(0)])
        self.nextPhase(len(recordList), u'Обработка данных по организациям')
        for record in recordList:
            if self.isTerminated:
                self.onTerminating()
                return
            orgId = forceRef(record.value('orgId'))
            elementList = self.orgForDeferredFilling.get(orgId, [])
            for element in elementList:
                infisCode = forceStringEx(record.value('infisCode'))[:6]
                if not infisCode:
                    orgName = forceStringEx(record.value('shortName'))
                    self.logger().warning(u'Отсутствует инфис код у организации {%s}"%s"' % (orgId, orgName))
                    continue
                CXMLHelper.setValue(element, infisCode)
            self.nextPhaseStep()

    def fillPersonalData(self, mapInsurerOkato):
        for insurerInfis, clients in self.clientsForDeferredFilling.iteritems():
            lDoc = self.lDocuments.get(insurerInfis, None)
            insurerOKATO = mapInsurerOkato.get(insurerInfis, None)
            rootElement = CXMLHelper.getRootElement(lDoc)
            tableClient = self._db.table('Client')
            tableClientDocument = self._db.table('ClientDocument')
            tableDocumentType = self._db.table('rbDocumentType')
            tableClientAddress = self._db.table('ClientAddress')
            tableAddress = self._db.table('Address')
            tableAddressHouse = self._db.table('AddressHouse')
            tableKLADR = self._db.table('kladr.KLADR')

            queryTable = tableClient.leftJoin(tableClientDocument,
                                              u'%s = getClientDocumentId(%s)' % (tableClientDocument['id'].name(),
                                                                                   tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableDocumentType,
                                             tableDocumentType['id'].eq(tableClientDocument['documentType_id']))
            queryTable = queryTable.leftJoin(tableClientAddress,
                                             u'%s = getClientRegAddressId(%s)' % (tableClientAddress['id'].name(),
                                                                                  tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableAddress,
                                             tableAddress['id'].eq(tableClientAddress['address_id']))
            queryTable = queryTable.leftJoin(tableAddressHouse,
                                             tableAddressHouse['id'].eq(tableAddress['house_id']))
            queryTable = queryTable.leftJoin(tableKLADR,
                                             tableKLADR['CODE'].eq(tableAddressHouse['KLADRCode']))

            cols = [tableClient['id'].alias('clientId'),
                    tableClient['lastName'],
                    tableClient['firstName'],
                    tableClient['patrName'],
                    tableClient['birthDate'],
                    tableClient['birthPlace'],
                    tableClient['sex'],
                    tableClient['SNILS'],
                    tableClientDocument['serial'].alias('documentSerial'),
                    tableClientDocument['number'].alias('documentNumber'),
                    tableDocumentType['federalCode'].alias('docTypeFedCode'),
                    tableKLADR['OCATD'].alias('placeOKATO')]
            recordList = self._db.getRecordList(queryTable,
                                                cols,
                                                where=tableClient['id'].inlist(clients.keys())
                                                )
            self.nextPhase(len(recordList), u'Обработка персональных данных')
            for record in recordList:
                pers = CXMLHelper.addElement(rootElement, 'PERS')
                clientId = forceInt(record.value('clientId'))
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'ID_PAC'),
                                    self._idPacMap.get(clientId, clientId))
                isLittleStranger, newbornSex, newbornBirthDate = clients.get(clientId, (False, 0, QtCore.QDate()))
                lastName = forceStringEx(record.value('lastName'))
                firstName = forceStringEx(record.value('firstName'))
                patrName = forceStringEx(record.value('patrName'))
                sex = forceInt(record.value('sex'))
                birthDate = forceDate(record.value('birthDate'))
                birthPlace = forceStringEx(record.value('birthPlace'))

                famElement = CXMLHelper.addElement(pers, 'FAM')
                imElement = CXMLHelper.addElement(pers, 'IM')
                otElement = CXMLHelper.addElement(pers, 'OT')
                wElement = CXMLHelper.addElement(pers, 'W')
                drElement = CXMLHelper.addElement(pers, 'DR')

                if birthPlace:
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'MR'),
                                        birthPlace)
                if not isLittleStranger:
                    CXMLHelper.setValue(famElement, lastName)
                    CXMLHelper.setValue(imElement, firstName)
                    CXMLHelper.setValue(otElement, patrName)
                    CXMLHelper.setValue(wElement, sex)
                    CXMLHelper.setValue(drElement, birthDate.toString(self.defaultDateFormat))
                    if not patrName:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST'),
                                            1)
                    if not lastName:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST'),
                                            2)
                    if not firstName:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST'),
                                            3)
                else:
                    CXMLHelper.setValue(drElement,
                                        newbornBirthDate.toString(self.defaultDateFormat))
                    CXMLHelper.setValue(wElement,
                                        newbornSex)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST'),
                                        1)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST'),
                                        2)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST'),
                                        3)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'FAM_P'),
                                        lastName)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'IM_P'),
                                        firstName)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OT_P'),
                                        patrName)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'W_P'),
                                        sex)
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DR_P'),
                                        birthDate.toString(self.defaultDateFormat))
                    if not patrName:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST_P'),
                                            1)
                    if not lastName:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST_P'),
                                            2)
                    if not firstName:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOST_P'),
                                            3)
                docSerial = forceStringEx(record.value('documentSerial'))
                docNumber = forceStringEx(record.value('documentNumber'))
                if docSerial or docNumber:
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCTYPE'),
                                        forceInt(record.value('docTypeFedCode')))
                    if docSerial:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCSER'),
                                            docSerial)
                    if docNumber:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCNUM'),
                                            docNumber)
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'SNILS'),
                                    formatSNILS(forceStringEx(record.value('SNILS'))))
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OKATOG'),
                                    forceStringEx(record.value('placeOKATO')))
                # CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OKATOP'),
                #                     insurerOKATO)
                self.nextPhaseStep()

    def terminate(self):
        self.isTerminated = True

    def onTerminating(self):
        self.logger().info(u'Прервано')
        self._progressInformer.reset(0, u'Прервано')

    def phaseReset(self, phasesCount):
        self.currentPhase = 0
        self.totalPhases = phasesCount

    @property
    def phaseInfo(self):
        return u'[Этап %s/%s] ' % (self.currentPhase, self.totalPhases)

    def nextPhase(self, steps, description = u''):
        self.currentPhase += 1
        self._progressInformer.reset(steps, self.phaseInfo + description)
        self.logger().info(self.phaseInfo + description)

    def nextPhaseStep(self, description = None):
        self._progressInformer.nextStep((self.phaseInfo + description) if description else None)

    def loadData(self, accountId):
        tableAccountItem = self._db.table('Account_Item')
        tableEvent = self._db.table('Event')
        tableAction = self._db.table('Action')
        tableVisit = self._db.table('Visit')
        tableEventType = self._db.table('EventType')
        tableEventResult = self._db.table('rbResult').alias('EventResult')
        tableEventTypePurpose = self._db.table('rbEventTypePurpose')
        tableLittleStranger = self._db.table('Event_LittleStranger')
        tableContractTariff = self._db.table('Contract_Tariff')

        tableClient = self._db.table('Client')
        tablePolicy = self._db.table('ClientPolicy')
        tablePolicyKind = self._db.table('rbPolicyKind')
        tableInsurer = self._db.table('Organisation').alias('Insurer')

        tableServiceAidProfile = self._db.table('rbMedicalAidProfile').alias('ServiceAidProfile')
        tableServiceAidKind = self._db.table('rbMedicalAidKind').alias('ServiceAidKind')
        tableEventTypeAidProfile = self._db.table('rbEventProfile').alias('EventTypeAidProfile')
        tableEventTypeAidKind = self._db.table('rbMedicalAidKind').alias('EventTypeAidKind')
        tableEventAidUnit = self._db.table('rbMedicalAidUnit')
        tableEventPrimaryDiagnostic = self._db.table('Diagnostic').alias('EventDiagnostic')
        tableEventPrimaryDiagnosis = self._db.table('Diagnosis').alias('EventDiagnosis')
        tableDiagnosticResult = self._db.table('rbDiagnosticResult')
        tableService = self._db.table('rbService')

        tableRefuseType = self._db.table('rbPayRefuseType')


        queryTable = tableAccountItem.innerJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAccountItem['action_id']))
        queryTable = queryTable.leftJoin(tableVisit, tableVisit['id'].eq(tableAccountItem['visit_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableEventAidUnit, tableEventAidUnit['id'].eq(tableAccountItem['unit_id']))
        queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        queryTable = queryTable.leftJoin(tableEventResult, tableEventResult['id'].eq(tableEvent['result_id']))
        queryTable = queryTable.leftJoin(tableEventTypePurpose, tableEventTypePurpose['id'].eq(tableEventType['purpose_id']))
        queryTable = queryTable.leftJoin(tableContractTariff, tableContractTariff['id'].eq(tableAccountItem['tariff_id']))

        queryTable = queryTable.leftJoin(tableEventPrimaryDiagnostic,
                                         # получение диагноза по соответствию врачу и событию, а в случае неудачи - по соответствию событию
                                         '%(idField)s = IFNULL(getEventPersonDiagnostic(%(eventId)s, %(personId)s),'
                                         '                    getEventDiagnostic(%(eventId)s))' % {'idField': tableEventPrimaryDiagnostic['id'],
                                                                                                   'eventId': tableEvent['id'],
                                                                                                   'personId': tableEvent['execPerson_id']}
                                         )
        queryTable = queryTable.leftJoin(tableEventPrimaryDiagnosis,
                                         tableEventPrimaryDiagnosis['id'].eq(tableEventPrimaryDiagnostic['diagnosis_id']))
        queryTable = queryTable.leftJoin(tableDiagnosticResult,
                                         tableDiagnosticResult['id'].eq(tableEventPrimaryDiagnostic['result_id']))
        queryTable = queryTable.leftJoin(tableLittleStranger, tableLittleStranger['id'].eq(tableEvent['littleStranger_id']))

        queryTable = queryTable.leftJoin(tableService, tableService['id'].eq(tableAccountItem['service_id']))
        queryTable = queryTable.leftJoin(tableServiceAidProfile, tableServiceAidProfile['id'].eq(tableService['medicalAidProfile_id']))
        queryTable = queryTable.leftJoin(tableServiceAidKind, tableServiceAidKind['id'].eq(tableService['medicalAidKind_id']))
        queryTable = queryTable.leftJoin(tableEventTypeAidProfile, tableEventTypeAidProfile['id'].eq(tableEventType['eventProfile_id']))
        queryTable = queryTable.leftJoin(tableEventTypeAidKind, tableEventTypeAidKind['id'].eq(tableEventType['medicalAidKind_id']))
        queryTable = queryTable.leftJoin(tablePolicy, '%s = %s' % (tablePolicy['id'].name(),
                                                                   'getClientPolicyId(%s, %s)' % (tableEvent['client_id'].name(), 1)))
        queryTable = queryTable.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tablePolicy['policyKind_id']))
        queryTable = queryTable.leftJoin(tableInsurer, tableInsurer['id'].eq(tablePolicy['insurer_id']))

        queryTable = queryTable.leftJoin(tableRefuseType, tableRefuseType['id'].eq(tableAccountItem['refuseType_id']))

        cols = [tableEvent['client_id'].alias('clientId'),
                tableEvent['id'].alias('eventId'),
                tableEvent['externalId'],
                tableVisit['id'].alias('visitId'),
                tableAction['id'].alias('actionId'),
                tableAccountItem['id'].alias('accountItemId'),
                tableAccountItem['date'].alias('accountItemDate'),
                tableRefuseType['flatCode'].alias('accountItemRefuseCode'),
                #tableRefuseType['rerun'],
                tableInsurer['infisCode'].alias('insurerInfis'),
                tableInsurer['OKATO'].alias('insurerOKATO'),

                # for addEventElement
                tableEventTypeAidKind['federalCode'].alias('eventTypeAidKindFedCode'),
                tableEvent['setDate'].alias('eventSetDate'),
                tableEvent['execDate'].alias('eventExecDate'),
                tableEventPrimaryDiagnosis['MKB'].alias('eventPrimaryMKB'),
                tableEventResult['federalCode'].alias('eventResultFedCode'),
                tableEventAidUnit['federalCode'].alias('eventAidUnitFedCode'),

                #for addServiceElement
                tableAction['org_id'].alias('actionOrgId'),
                tableEvent['org_id'].alias('eventOrgId'),
                tableEvent['execPerson_id'].alias('eventExecPersonId'),
                'IFNULL(%s, %s) AS actionPersonId' % (tableAction['person_id'],
                                                      tableAction['setPerson_id']),
                tableVisit['person_id'].alias('visitPersonId'),
                tableAction['begDate'].alias('actionBegDate'),
                tableAction['endDate'].alias('actionEndDate'),
                tableAction['status'].alias('actionStatus'),
                tableVisit['date'].alias('visitDate'),
                tableService['code'].alias('serviceCode'),
                tableAccountItem['amount'].alias('serviceAmount'),
                tableContractTariff['price'].alias('servicePrice'),
                tableAccountItem['sum'].alias('serviceSum'),
                'if(%s IS NULL, Account_Item.sum, 0) AS servicePayed' % tableRefuseType['id'],
                'if(%s IS NOT NULL, Account_Item.sum, 0) AS serviceSank' % tableRefuseType['id'],
                u'''IF(Account_Item.date IS NULL AND Account_Item.refuseType_id IS NULL, 0,
                       IF(Account_Item.date IS NOT NULL AND Account_Item.refuseType_id IS NULL, 1, 2)) AS serviceOplata''',

                #for fillPatient
                '%s IS NOT NULL AS isLittleStranger' % tableLittleStranger['id'].name(),
                tablePolicyKind['federalCode'].alias('policyKindFedCode'),
                tablePolicy['serial'].alias('policySerial'),
                tablePolicy['number'].alias('policyNumber'),
                tableLittleStranger['sex'].alias('newbornSex'),
                tableLittleStranger['birthDate'].alias('newbornBirthDate'),
                tableLittleStranger['currentNumber'].alias('newbornNumber')
                ]

        cond = [tableAccountItem['master_id'].eq(accountId)]

        self.nextPhaseStep(u'Загрузка данных по счету')
        recordList = self._db.getRecordList(queryTable, cols, where=cond)
        self.nextPhaseStep(u'Загрузка данных завершена')
        return recordList

    def clear(self):
        self.isTerminated = False
        self.phaseReset(15)
        self.hDocuments.clear()
        self.lDocuments.clear()
        self.orgForDeferredFilling.clear()
        self.personSpecialityForDeferredFilling.clear()
        self.clientsForDeferredFilling.clear()

    def process(self, accountId, exportNumber):
        self.clear()
        entries = {}
        events = {}
        idCaseCounter = {}
        entryCounter = {}
        sankCounter = {}
        sankTotal = {}
        accountTotal = {}
        eventsTotal = {}
        oplataTotal = {}
        insurerOkato = {}
        self._idPacMap.clear()

        recordList = self.loadData(accountId)
        self.lpuInfis = forceStringEx(self.accountRecord.value('lpuInfis'))
        numberDispType = forceStringEx(self.accountRecord.value('number'))[:2].upper()
        dispType = self.mapDispTypes[numberDispType]

        self.nextPhase(len(recordList), u'Обработка позиций счета')
        for record in recordList:
            if self.isTerminated:
                self.onTerminating()
                return False

            insurerInfis = forceStringEx(record.value('insurerInfis'))

            if insurerInfis and not insurerInfis.startswith(u'85'):
                insurerInfis = ''

            insurerOkato.setdefault(insurerInfis, forceStringEx(record.value('insurerOKATO')))

            self.hDocuments.setdefault(insurerInfis, self.createHXMLDocument(exportNumber, insurerInfis, dispType))
            self.lDocuments.setdefault(insurerInfis, self.createLXMLDocument(exportNumber, insurerInfis))
            doc, accountElement, headerElement = self.hDocuments[insurerInfis]
            rootElement = CXMLHelper.getRootElement(doc)

            clientId = forceRef(record.value('clientId'))
            if not entries.has_key(clientId):
                entryCounter[insurerInfis] = entryCounter.setdefault(insurerInfis, 0) + 1
                entries[clientId] = self.addEntryElement(rootElement, record, entryCounter[insurerInfis])

            entryElement, _ = entries[clientId]
            currentSankTotal = sankTotal.setdefault(insurerInfis, {})
            eventId = forceRef(record.value('eventId'))
            if not events.has_key(eventId):
                currentSankTotal[eventId] = {}
                idCaseCounter[insurerInfis] = idCaseCounter.setdefault(insurerInfis, 0) + 1
                events[eventId] = self.addEventElement(entryElement, idCaseCounter[insurerInfis], record)

            eventElement = events[eventId]


            refuseTypeCode = forceStringEx(record.value('accountItemRefuseCode'))
            if refuseTypeCode:
                if not currentSankTotal[eventId].has_key(refuseTypeCode):
                    sankCounter[eventId] = sankCounter.setdefault(eventId, 0) + 1
                    currentSankTotal[eventId][refuseTypeCode] = [self.addSankElement(eventElement,
                                                                  sankCounter[eventId],
                                                                  record=record), 0]
                currentSankTotal[eventId][refuseTypeCode][1] += forceDouble(record.value('serviceSum'))


            self.addServiceElement(eventElement, forceRef(record.value('accountItemId')), record)

            currentEventsTotal = eventsTotal.setdefault(insurerInfis, {})
            currentOplataTotal = oplataTotal.setdefault(insurerInfis, {})
            if not currentEventsTotal.has_key(eventId):
                currentEventsTotal[eventId] = [0.0] * 4
                currentOplataTotal[eventId] = [0, 1]
            currentEventsTotal[eventId][0] += round(forceDouble(record.value('serviceSum')))
            currentEventsTotal[eventId][1] += round(forceDouble(record.value('servicePayed')))
            currentEventsTotal[eventId][2] += round(forceDouble(record.value('serviceSank')))
            currentEventsTotal[eventId][3] += round(forceDouble(record.value('serviceAmount')))
            currentOplataTotal[eventId][0] += 1
            currentOplataTotal[eventId][1] *= forceInt(record.value('serviceOplata'))

            self.clientsForDeferredFilling.setdefault(insurerInfis, {}).setdefault(clientId,
                                                                                   (forceBool(record.value('isLittleStranger')),
                                                                                    forceInt(record.value('newbornSex')),
                                                                                    forceDate(record.value('newbornBirthDate')),
                                                                                    ))

            self.nextPhaseStep()

        self.nextPhase(len(eventsTotal), u'Заполнение данных о стоимости случаев')
        for insurerInfis, currentEventTotal in eventsTotal.iteritems():
            for eventId, total in currentEventTotal.iteritems():
                if self.isTerminated:
                    self.onTerminating()
                    return False
                eventElement = events[eventId]
                element = eventElement.firstChildElement('OPLATA')
                currentOplataTotal = oplataTotal[insurerInfis][eventId]
                CXMLHelper.setValue(element, 0 if currentOplataTotal[1] == 0 else 1 if currentOplataTotal[1] == 1 else 2 if currentOplataTotal[1] % currentOplataTotal[0] == 0 else 3)
                element = eventElement.firstChildElement('ED_COL')
                CXMLHelper.setValue(element, '%.2f' % total[-1])
                for index, elemName in enumerate(['SUMV', 'SUMP', 'SANK_IT']):
                    element = eventElement.firstChildElement(elemName)
                    CXMLHelper.setValue(element, '%.2f' % total[index])
                    currentAccountTotal = accountTotal.setdefault(insurerInfis, [0.0] * 3)  # ['SUMMAV', 'SUMMAP', 'SANK_MEK']
                    currentAccountTotal[index] += total[index]
                currentSankTotal = sankTotal[insurerInfis][eventId]
                for refuseTypeCode, total in currentSankTotal.iteritems():
                    sankElement = currentSankTotal[refuseTypeCode][0]
                    element = sankElement.firstChildElement('S_SUM')
                    CXMLHelper.setValue(element, '%.2f' % total[1])
                self.nextPhaseStep()

            self.nextPhase(len(accountTotal), u'Заполнение данных об общей стоимости счетов')
            for insurerInfis, total in accountTotal.iteritems():
                if self.isTerminated:
                    self.onTerminating()
                    return False
                _, accountElement, _ = self.hDocuments[insurerInfis]
                for index, elemName in enumerate(['SUMMAV', 'SUMMAP', 'SANK_MEK']):
                    element = accountElement.firstChildElement(elemName)
                    CXMLHelper.setValue(element, '%.2f' % total[index])
                self.nextPhaseStep()

        if not self.isTerminated:
            self.fillOrganisations()
        if not self.isTerminated:
            self.fillPersonSpeciality()

        if not self.isTerminated:
            self.fillPersonalData(insurerOkato)

        self.logger().info(u'Завершено')
        if self.isTerminated:
            self.onTerminating()
            return False
        return True

    def save(self, outDir):
        outDir = forceStringEx(outDir)
        self.nextPhase(len(self.hDocuments), u'Сохранение файлов')
        for insurerInfis in self.hDocuments.keys():
            doc, _, headerElement = self.hDocuments[insurerInfis]
            fileName = forceStringEx(headerElement.firstChildElement('FILENAME').text())
            zipFileName = u'%s.zip' % fileName
            zipFilePath = os.path.join(outDir, zipFileName)
            try:
                hTmp = QtCore.QTemporaryFile(u'%s.xml' % fileName)
                if not hTmp.open(QtCore.QFile.WriteOnly):
                    self.logger().critical(u'Не удалось открыть временный файл для записи')
                    break
                doc.save(QtCore.QTextStream(hTmp), 4, QtXml.QDomNode.EncodingFromDocument)
                hTmp.close()
                zf = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
                zf.write(QtCore.QFileInfo(hTmp).absoluteFilePath(), u'%s.xml' % fileName)
                self.logger().info(u'Создан файл: %s' % zipFileName)
                zf.close()
                self.hDocuments.pop(insurerInfis)
            except Exception, e:
                QtGui.qApp.logCurrentException()
                self.logger().critical(u'Не удалось сохранить файл %s' % zipFileName)

        self.nextPhase(len(self.lDocuments), u'Сохранение файлов L')
        for insurerInfis in self.lDocuments.keys():
            doc = self.lDocuments[insurerInfis]
            rootElement = CXMLHelper.getRootElement(doc)
            headerElement = rootElement.firstChildElement('ZGLV')
            fileName = forceStringEx(headerElement.firstChildElement('FILENAME').text())
            zipFileName = u'%s.zip' % fileName
            zipFilePath = os.path.join(outDir, zipFileName)
            try:
                lTmp = QtCore.QTemporaryFile(u'%s.xml' % fileName)
                if not lTmp.open(QtCore.QFile.WriteOnly):
                    self.logger().critical(u'Не удалось открыть временный файл для записи')
                    break
                doc.save(QtCore.QTextStream(lTmp), 4, QtXml.QDomNode.EncodingFromDocument)
                lTmp.close()
                zf = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
                # body = codecs.encode(forceStringEx(doc.toString(4)), self.encoding)
                # zf.writestr(u'%s.xml' % fileName, body)
                zf.write(QtCore.QFileInfo(lTmp).absoluteFilePath(), u'%s.xml' % fileName)
                self.logger().info(u'Создан файл: %s' % zipFileName)
                zf.close()
                self.lDocuments.pop(insurerInfis)
            except Exception, e:
                self.logger().critical(u'Не удалось сохранить файл %s' % zipFileName)