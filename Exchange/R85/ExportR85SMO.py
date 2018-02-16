# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   04.04.2015
'''

#TODO: craz: выгрузка нескольких счетов
#TODO: craz: Сохранение директории по умолчанию
#TODO: craz: Объединить вызгрузки по Крыму
#TODO: Обработка номера реестра
#TODO: craz: Откуда брать PODR? Из eventExecPerson или из serviceExecPerson
#TODO: craz: Рассмотреть логику accCode из ExportR85MTR. Возможно, сделать нечто аналогичное
#TODO: craz: Хранить в IDSERV Account_Item.id из МО
#TODO: craz: отвязаться от названия договора


import logging, os, zipfile

from PyQt4 import QtCore, QtGui, QtXml


from Exchange.Utils import compressFileInZip
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceStringEx, forceTr, getClassName, getPref, setPref, CLogHandler, \
    formatSNILS
from library.XML.XMLHelper import CXMLHelper

# def exportR85SMO(widget, accountId):
#     exportWindow = CExportDialog(QtGui.qApp.db, accountId, widget)
#     params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), {})
#     exportWindow.setParams(params)
#     exportWindow.exec_()
#     setPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), exportWindow.params())


class CExportR85SMOEngine(object):
    encoding = u'windows-1251'
    version = u'2.1'

    defaultDateFormat = QtCore.Qt.ISODate

    dummy = '#'*25
    dummyN = 0

    PrimaryMKBTypeCode = 2
    SecondaryMKBTypeCode = 9
    ComplicatedMKBTypeCode = 3

    counterCode = 'smoCode'

    def __init__(self, db, accountRecord, progressInformer = None):
        self._db = db
        self._progressInformer = progressInformer if isinstance(progressInformer, CProgressInformer) \
                                                  else CProgressInformer(processEventsFlag=None)
        self._logger = logging.getLogger(name=getClassName(self))
        self._logger.setLevel(logging.INFO)

        self.totalPhases = 0
        self.currentPhase = 0
        self.accountRecord = accountRecord

        self.hDocuments = {}
        self.lDocuments = {}
        self.personSpecialityForDeferredFilling = {}
        self.orgForDeferredFilling = {}
        self.clientsForDeferredFilling = {}
        self.firstVisitsForDeferredFilling = {}
        self.lpuInfis = None

        self.customIdspMap = {} # Предварительное заполнение подушевых единиц учета для обращений. В итоге будет применено только для обращений с нулевой стоимостью
        self._idPacMap = {} # Словарь {Client.id: ID_PAC}
        self.isTerminated = False
        self._counterId = None

    def logger(self):
        return self._logger

    #TODO: craz: progressInformer setter/getter?

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
                newRecord.setValue('reset', QtCore.QVariant(6)) # ежегодно
                year = QtCore.QDate.currentDate().year()
                newRecord.setValue('startDate', QtCore.QVariant(QtCore.QDate(year, 1, 1)))
                self._counterId = self._db.insertRecord(tableCounter, newRecord)
        query = self._db.query('SELECT getCounterValue(%d)' % self._counterId)
        if query.next():
            return forceInt(query.record().value(0))
        else:
            self.logger().critical(u'Не удалось получить значение счетчика для кода счета')
            return None

    def createLXMLDocument(self, insurerInfis, exportNumber):
        doc = CXMLHelper.createDomDocument(rootElementName='PERS_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        header = self.addHeaderElement(rootElement, insurerInfis, exportNumber, lfile=True)
        return doc

    def createHXMLDocument(self,insurerInfis, exportNumber):
        doc = CXMLHelper.createDomDocument(rootElementName='ZL_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        headerElement = self.addHeaderElement(rootElement, insurerInfis, exportNumber)
        accountElement = self.addAccountElement(rootElement, insurerInfis)
        return doc, accountElement, headerElement

    def addHeaderElement(self, rootElement, insurerInfis, exportNumber, lfile=False):
        header = CXMLHelper.addElement(rootElement, 'ZGLV')
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'VERSION'),
                            self.version[:5])
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'DATA'),
                            QtCore.QDate.currentDate().toString(self.defaultDateFormat))
        lpuInfis = forceStringEx(self.accountRecord.value('lpuInfis'))
        settleDate = forceDate(self.accountRecord.value('accountSettleDate'))
        if insurerInfis:
            fileName = u'HM%sS%s_%s%d' % (lpuInfis,
                                          insurerInfis,
                                          settleDate.toString('yyMM'),
                                          exportNumber)
        else:
            fileName = u'HT85M%s_%s%d' % (lpuInfis,
                                          settleDate.toString('yyMM'),
                                          exportNumber)
        if lfile:
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME'),
                                'L' + fileName[1:])
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME1'),
                                fileName)
        else:
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME'),
                            fileName)
        return header

    def addAccountElement(self, rootElement, insurerInfis):
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
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'CODE_MO'),
                            forceStringEx(self.accountRecord.value('lpuInfis')))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'YEAR'),
                            accDate.year())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'MONTH'),
                            accDate.month())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'NSCHET'),
                            forceStringEx(self.accountRecord.value('accountNumber'))[:15])
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'DSCHET'),
                            forceDate(self.accountRecord.value('accountDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'PLAT'),
                            insurerInfis if insurerInfis.startswith('85') else '85000')
        CXMLHelper.addElement(account, 'SUMMAV')
        CXMLHelper.addElement(account, 'SUMMAP')
        CXMLHelper.addElement(account, 'SANK_MEK')
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

        # idPac = None
        # externalIdParts = forceStringEx(record.value('externalId')).split('#')
        clientId = forceInt(record.value('clientId'))
        idPac = self.getExternalId(forceStringEx(record.value('externalId')), 'idpac', clientId)
        # if len(externalIdParts)>1:
        #     idPac = forceInt(externalIdParts[1])
        # if not idPac:
        #     idPac = clientId
        self._idPacMap[clientId] = idPac
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'ID_PAC'),
                            idPac)
        policyKind = forceInt(record.value('policyKindFedCode'))
        policyNumber = forceStringEx(record.value('policyNumber'))

        #FIXME: craz: в мае 2015 костыльное определение вида полиса хотелось бы выпилить. Данные в фонде должны быть заполнены корректно.
        if len(policyNumber) == 16:
            policyKind = 3
        elif len(policyNumber) == 9:
            policyKind = 2

        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'VPOLIS'),
                            policyKind)
        if policyKind == 1:
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SPOLIS'),
                                forceStringEx(record.value('policySerial'))[:10])
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'NPOLIS'),
                            policyNumber[:20])

        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'ST_OKATO'),
        #                     self.dummy)

        smoCode = forceStringEx(record.value('insurerInfis'))
        # if smoCode:
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SMO'),
                            smoCode[:5])
        # else:
        # Для выгрузки в СМО неактуально. Нас устраивают только предопределенные СМО, в которых все заполнено
        #     CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SMO_OGRN'),
        #                         forceStringEx(record.value('insurerOGRN'))[:15])
        #     CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SMO_OK'),
        #                         forceStringEx(record.value('insurerOKATO'))[:5])

        isLittleStranger = forceBool(record.value('isLittleStranger'))
        birthDate = forceDate(record.value('newbornBirthDate'))
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'NOVOR'),
                            '0' if not isLittleStranger else '%d%s%d' % (forceInt(record.value('newbornSex')),
                                                            birthDate.toString('ddMMyy'),
                                                            forceInt(record.value('newbornNumber'))))
        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'VNOV_D'),
        #                     self.dummyN)

    @classmethod
    def getExternalId(cls, searchString, key, default=None):
        """В Event.externalId хранятся внешние идентификаторы для обеспечения однозначной идентификации пациента в МО, ТФ и СМО.

        Возможные значения:
        <nhistory> - в externalId хранится только идентификатор истории болезни, соответствующий Event.id в базе МО
        nhistory:<nhistory>#idpac:<idpac> - в externalId хранится набор внешних идентификаторов, таких как номер истории
         болезни и идентификатор пациента (Event.id и Client.id в базе МО соответственно). На данный момент порядок и
         набор данных именно такой, однако допускается расширение набора и задание в произвольном порядке. Форма записи
         для каждого поля выглядит как <тег_в_обмене>:<значение>.
        <nhistory>#<idpac> - два идентификатора с жестко определенным порядком следования. Был в очень небольшом наборе
        ревизий, предполагается, что нигде не использовался. В данном методе не обрабатывается.
         Если не удалось определить значение интересующего идентификатора, возвращаем default
        """
        parts = forceStringEx(searchString).split('#')
        if len(parts) == 1 and not key in parts[0] and key == 'nhistory':
            return parts[0]
        elif len(parts) > 1:
            for part in parts:
                parts2 = part.split(':')
                if len(parts2) == 2 and parts2[0] == key:
                    return parts2[1]
        return default

    def addEventElement(self, entryElement, idCase, record):
        """

        @param entryElement:
        @param idCase:
        @param record:
        @return:
        """

        serviceCode = forceStringEx(record.value('serviceCode'))
        eventId = forceRef(record.value('eventId'))

        eventElement = CXMLHelper.addElement(entryElement, 'SLUCH')

        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDCASE'),
                            idCase)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'USL_OK'),
                            forceInt(record.value('eventTypePurposeFedCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VIDPOM'),
                            forceInt(record.value('eventTypeAidKindFedCode')))
        eventOrder = forceInt(record.value('eventOrder'))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'FOR_POM'),
                            {1: 3, # плановая
                             2: 1, # экстренная
                             6: 2  # неотложная
                            }.get(eventOrder, 3))
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NPR_MO'),
        #                     self.dummy)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'EXTR'),
                            2 if eventOrder == 2 else 1)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'LPU'),
                            self.lpuInfis)
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'LPU_1'),
        #                     self.dummy)
        podrElement = CXMLHelper.addElement(eventElement, 'PODR')
        profilElement = CXMLHelper.addElement(eventElement, 'PROFIL')
        if serviceCode.startswith('6'):
            self.firstVisitsForDeferredFilling.setdefault(eventId, []).append(profilElement)
        else:
            CXMLHelper.setValue(profilElement,
                                forceInt(record.value('serviceAidProfileFedCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DET'),
                            1 if forceInt(record.value('clientAge'))
                                 or forceBool(record.value('isLittleStranger')) < 18 else 0)
        # externalIdParts = forceStringEx(record.value('externalId')).split('#')

        nHistory = self.getExternalId(forceStringEx(record.value('externalId')), 'nhistory', forceStringEx(record.value('eventId')))

        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NHISTORY'),
                            nHistory[:50])
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_1'),
                            forceDate(record.value('eventSetDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_2'),
                            forceDate(record.value('eventExecDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DS1'),
                            forceStringEx(record.value('eventPrimaryMKB')))
        result = forceInt(record.value('eventResultFedCode'))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'RSLT'),
                            result if result else '')
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'ISHOD'),
                            forceInt(record.value('eventPrimaryMKBResultFedCode')))

        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VERS_SPEC'),
                            u'V015')
        #TODO: убедиться, что мы наконец можем использовать только eventExecPersonId
        personId = forceRef(record.value('eventExecPersonId'))
        self.personSpecialityForDeferredFilling.setdefault(personId,
             []).append((CXMLHelper.addElement(eventElement, 'PRVS'),
                         CXMLHelper.addElement(eventElement, 'IDDOKT'),
                         podrElement))

        if not forceStringEx(record.value('clientPatrName')):
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'OS_SLUCH'),
                                2)

        # для подушевых, если нет суммы и codeusl.startswith(3) -> 26, codeusl.startswith(4) -> 35
        # перезаписывается на этапе заполнения стоимостей
        idsp = forceInt(record.value('eventAidUnitFedCode'))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDSP'),
                            idsp)
        #TODO: craz: проверить логику с учетом того, что сейчас у нас несколько услуг в одном случае
        CXMLHelper.addElement(eventElement, 'ED_COL')
        # edCol = forceDouble(record.value('serviceUET'))
        # if not edCol:
        #     edCol = forceDouble(record.value('serviceAmount'))
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'ED_COL'),
        #                     '%.2f' % edCol)
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'TARIF'),
        #                     0)
        CXMLHelper.addElement(eventElement, 'SUMV')
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'OPLATA'),
                            2 if forceStringEx(record.value('accountItemRefuseCode')) else 1)
        CXMLHelper.addElement(eventElement, 'SUMP')
        CXMLHelper.addElement(eventElement, 'SANK_IT')

        return eventElement

    def addServiceElement(self, eventElement, idServ, record):
        """

        @param eventElement:
        @param idServ:
        @param record:
        @return:
        """
        serviceCode = forceStringEx(record.value('serviceCode'))
        serviceName = forceStringEx(record.value('serviceName'))
        eventId = forceRef(record.value('eventId'))
        if serviceCode.startswith('3'):
            if not forceDouble(record.value('serviceSum')) \
                and not u'cтома' in serviceName.lower() and not eventId in self.customIdspMap:
                self.customIdspMap[eventId] = '26'
            elif self.customIdspMap.get(eventId, None) != '29':
                self.customIdspMap[eventId] = forceInt(record.value('eventAidUnitFedCode'))

        elif serviceCode.startswith('4') and not forceDouble(record.value('serviceSum')):
            self.customIdspMap[eventId] = '35'

        serviceElement = CXMLHelper.addElement(eventElement, 'USL', afterElem=['USL', 'SANK', 'SANK_IT', 'SUMP', 'OPLATA'])

        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'IDSERV'),
                            forceStringEx(idServ)[:36])
        #atronah: "LPU" заполняется позже, отдельным запросом
        #atronah: предполагается, что место проведение Visit'а совпадает с местом Event'a (иначе пришлось бы джойнить врача из Visit и брать его организацию)
        serviceOrgId = forceRef(record.value('actionOrgId')) \
                       or forceRef(record.value('eventOrgId'))
        self.orgForDeferredFilling.setdefault(serviceOrgId,
            []).append(CXMLHelper.addElement(serviceElement, 'LPU'))
        podrElement = CXMLHelper.addElement(serviceElement, 'PODR')
        profilElement = CXMLHelper.addElement(serviceElement, 'PROFIL')
        if serviceCode.startswith('6'):
            self.firstVisitsForDeferredFilling.setdefault(forceRef(record.value('eventId')), []).append(profilElement)
        else:
            CXMLHelper.setValue(profilElement,
                                forceInt(record.value('serviceAidProfileFedCode')))
        # CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'VID_VME'),
        #                     self.dummy)
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'DET'),
                            1 if forceInt(record.value('clientAge'))
                                 or forceBool(record.value('isLittleStranger'))< 18 else 0)
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
        mkb = forceStringEx(record.value('actionMKB')) or forceStringEx(record.value('visitMKB'))
        if not mkb:
            # Получение диагноза из события
            mkb = forceStringEx(eventElement.firstChildElement('DS1').text())
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'DS'),
                            mkb[:10])
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'CODE_USL'),
                            serviceCode)
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'KOL_USL'),
                            '%.2f' % forceDouble(record.value('serviceAmount')))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'TARIF'),
                            '%.2f' % forceDouble(record.value('servicePrice')))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'SUMV_USL'),
                            '%.2f' % forceDouble(record.value('serviceSum')))
        # craz: PRVS и CODE_MD заполняются позже, отдельным запросом
        personId = forceRef(record.value('visitPersonId')) \
                   or forceRef(record.value('actionPersonId')) \
                   or forceRef(record.value('eventExecPersonId'))
        #FIXME: Всегда ли есть врач? нужно ли брать из диагноза?

        self.personSpecialityForDeferredFilling.setdefault(personId,
            []).append((CXMLHelper.addElement(serviceElement, 'PRVS'),
                       CXMLHelper.addElement(serviceElement, 'CODE_MD'),
                        podrElement))
        return serviceElement



    def fillAdditionalDiagnosis(self, events):
        self.nextPhase(1, u'Загрузка данных по доп. диагнозам')
        tableDiagnostic = self._db.table('Diagnostic')
        tableDiagnosis = self._db.table('Diagnosis')
        tableDiagnosisType = self._db.table('rbDiagnosisType')

        queryTable = tableDiagnostic.innerJoin(tableDiagnosisType,
                                               tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']))
        queryTable = queryTable.innerJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))

        recordList = self._db.getRecordList(table=queryTable,
                                            cols=[tableDiagnostic['event_id'].alias('eventId'),
                                                  tableDiagnosisType['code'].alias('typeCode'),
                                                  tableDiagnosis['MKB']],
                                            where=[tableDiagnostic['event_id'].inlist(events.keys()),
                                                   tableDiagnosisType['code'].inlist([self.SecondaryMKBTypeCode,
                                                                                      self.ComplicatedMKBTypeCode]),
                                                   tableDiagnostic['deleted'].eq(0),
                                                   tableDiagnosis['deleted'].eq(0)])
        self.nextPhase(len(recordList), u'Обработка данных по доп. диагнозам')
        for record in recordList:
            if self.isTerminated:
                self.onTerminating()
                return
            eventElement = events.get(forceRef(record.value('eventId')), None)
            if eventElement is None:
                self.nextPhaseStep()
                continue

            typeCode = forceInt(record.value('typeCode'))
            afterNode = ['DS3', 'DS2', 'DS1']
            if typeCode == self.SecondaryMKBTypeCode:
                afterNode.pop(0)
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, afterNode[0], afterElem=afterNode),
                                forceStringEx(record.value('MKV')))
            self.nextPhaseStep()

    def fillPersonSpeciality(self):
        self.nextPhase(1, u'Загрузка данных по врачам')
        tablePerson = self._db.table('Person')
        tableSpeciality = self._db.table('rbSpeciality')
        tableOrgStructure = self._db.table('OrgStructure')
        recordList = self._db.getRecordList(table=tablePerson.leftJoin(tableSpeciality,
                                                                        tableSpeciality['id'].eq(tablePerson['speciality_id'])
                                                            ).leftJoin(tableOrgStructure,
                                                                        tableOrgStructure['id'].eq(tablePerson['orgStructure_id'])),
                                            cols=[tablePerson['id'].alias('personId'),
                                                  tablePerson['federalCode'].alias('personFedCode'),
                                                  tableSpeciality['federalCode'].alias('specialityFedCode'),
                                                  tableOrgStructure['infisCode'].alias('orgStructureInfisCode'),
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
            orgStructureInfisCode = forceStringEx(record.value('orgStructureInfisCode'))
            personName = forceStringEx(record.value('personName'))
            if not personFederalCode:
                self.logger().warning(u'Не заполнен федеральный код врача {%s}"%s"' % (personId, personName))
            if not specialityFederalCode:
                self.logger().warning(u'Не заполнен федеральный код специальности у врача {%s}"%s"' % (personId, personName))
            if not orgStructureInfisCode:
                self.logger().warning(u'Не заполнен инфис код подразделения у врача {%s}"%s"' % (personId, personName))
            for specialityElement, personElement, orgStructureElement in elementList:
                if personFederalCode and personFederalCode != '-1':
                    CXMLHelper.setValue(personElement, personFederalCode)
                if specialityFederalCode:
                    CXMLHelper.setValue(specialityElement, specialityFederalCode)
                if orgStructureInfisCode:
                    CXMLHelper.setValue(orgStructureElement, orgStructureInfisCode)
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

    def fillFirstVisitProfile(self):
        self.nextPhase(1, u'Загрузка данных по профилям стоматологий')

        tableMAP = self._db.table('rbMedicalAidProfile')
        tableService = self._db.table('rbService')
        tableVisit = self._db.table('Visit')
        tableEvent = self._db.table('Event')
        tableV = tableVisit.alias('v')

        queryTable = tableMAP.innerJoin(tableService, tableService['medicalAidProfile_id'].eq(tableMAP['id']))
        queryTable = queryTable.innerJoin(tableVisit, tableVisit['service_id'].eq(tableService['id']))
        queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
        cond = ['%s = %s' % (tableVisit['id'].name(),
                            '(SELECT MAX(v.id) FROM Visit v WHERE v.service_id IS NOT NULL and v.event_id = Event.id and v.deleted = 0)'),
                tableEvent['id'].inlist(self.firstVisitsForDeferredFilling.keys()),
                ]
        recordList = self._db.getRecordList(queryTable,
                                            [tableMAP['federalCode'].alias('profileFedCode'),
                                             tableEvent['id'].alias('eventId')],
                                            cond)
        self.nextPhase(len(recordList), u'Обработка данных по профилям стоматологий')
        for record in recordList:
            eventId = forceRef(record.value('eventId'))
            profile = forceStringEx(record.value('profileFedCode'))
            for element in self.firstVisitsForDeferredFilling.get(eventId, []):
                CXMLHelper.setValue(element, profile)
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

    def process(self, accountId, exportNumber, sums):
        self.isTerminated = False
        self.phaseReset(15)

        # tableAccount = self._db.table('Account')
        # tableContract = self._db.table('Contract')
        # tableOrganisation = self._db.table('Organisation')
        #
        # cols = [
        #     tableAccount['date'].alias('accountDate'),
        #     tableAccount['number'].alias('accountNumber'),
        #     tableAccount['settleDate'].alias('accountSettleDate'),
        #     tableAccount['sum'].alias('accountSum'),
        #     tableContract['number'].alias('lpuInfis'),
        # ]
        # accountRecord = self._db.getRecordEx(tableAccount.innerJoin(tableContract,
        #                                                             tableContract['id'].eq(tableAccount['contract_id'])),
        #                                      cols,
        #                                      where=tableAccount['id'].eq(accountId))

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
                tableEventTypePurpose['federalCode'].alias('eventTypePurposeFedCode'),
                tableEventTypeAidKind['federalCode'].alias('eventTypeAidKindFedCode'),
                tableEvent['order'].alias('eventOrder'),
                tableEvent['setDate'].alias('eventSetDate'),
                tableEvent['execDate'].alias('eventExecDate'),
                tableEventPrimaryDiagnosis['MKB'].alias('eventPrimaryMKB'),
                tableEventResult['federalCode'].alias('eventResultFedCode'),
                tableDiagnosticResult['federalCode'].alias('eventPrimaryMKBResultFedCode'),
                tableEventAidUnit['federalCode'].alias('eventAidUnitFedCode'),
                tableClient['patrName'].alias('clientPatrName'),

                #for addServiceElement
                tableAction['org_id'].alias('actionOrgId'),
                tableEvent['org_id'].alias('eventOrgId'),
                tableEvent['execPerson_id'].alias('eventExecPersonId'),
                'IFNULL(%s, %s) AS actionPersonId' % (tableAction['person_id'],
                                                      tableAction['setPerson_id']),
                tableVisit['person_id'].alias('visitPersonId'),
                tableAction['begDate'].alias('actionBegDate'),
                tableAction['endDate'].alias('actionEndDate'),
                tableVisit['date'].alias('visitDate'),
                tableService['code'].alias('serviceCode'),
                tableService['name'].alias('serviceName'),
                tableAccountItem['amount'].alias('serviceAmount'),
                tableAccountItem['uet'].alias('serviceUET'),
                tableContractTariff['price'].alias('servicePrice'),
                # tableAccountItem['price'].alias('servicePrice'),
                tableAccountItem['sum'].alias('serviceSum'),
                tableAction['MKB'].alias('actionMKB'),
                tableVisit['MKB'].alias('visitMKB'),
                tableServiceAidProfile['federalCode'].alias('serviceAidProfileFedCode'),

                #for fillPatient
                '%s IS NOT NULL AS isLittleStranger' % tableLittleStranger['id'].name(),
                tablePolicyKind['federalCode'].alias('policyKindFedCode'),
                tablePolicy['serial'].alias('policySerial'),
                tablePolicy['number'].alias('policyNumber'),
                tableLittleStranger['sex'].alias('newbornSex'),
                tableLittleStranger['birthDate'].alias('newbornBirthDate'),
                tableLittleStranger['currentNumber'].alias('newbornNumber'),
                'age(%s, %s) as clientAge' % (tableClient['birthDate'], tableEvent['setDate']),
                ]

        cond = [tableAccountItem['master_id'].eq(accountId)]

        self.nextPhaseStep(u'Загрузка данных по счету')
        recordList = self._db.getRecordList(queryTable, cols, where=cond)
        self.nextPhaseStep(u'Загрузка данных завершена')

        self.hDocuments.clear()
        self.lDocuments.clear()
        # self.accCodeToAccountItemId.clear()
        self.lpuInfis = forceStringEx(self.accountRecord.value('lpuInfis'))
        entries = {}
        events = {}
        idCaseCounter = {}
        entryCounter = {}
        self.orgForDeferredFilling.clear()
        self.personSpecialityForDeferredFilling.clear()
        self.clientsForDeferredFilling.clear()
        self.firstVisitsForDeferredFilling.clear()
        self.customIdspMap.clear()
        self._idPacMap.clear()
        eventsTotals = {}
        eventRefuses = {}
        accountTotals = {}
        insurerOkato = {}
        self.nextPhase(len(recordList), u'Обработка позиций счета')
        for record in recordList:
            if self.isTerminated:
                self.onTerminating()
                return False

            insurerInfis = forceStringEx(record.value('insurerInfis'))

            if not insurerInfis.startswith('85'):
                insurerInfis = ''
            # if insurerInfis and not insurerInfis.startswith(u'85'):
            #     self.nextPhaseStep()
            #     continue

            self.hDocuments.setdefault(insurerInfis, self.createHXMLDocument(insurerInfis, exportNumber))
            self.lDocuments.setdefault(insurerInfis, self.createLXMLDocument(insurerInfis, exportNumber))
            hDoc, accountElement, headerElement = self.hDocuments[insurerInfis]

            insurerOkato.setdefault(insurerInfis, forceStringEx(record.value('insurerOKATO')))
            rootElement = CXMLHelper.getRootElement(hDoc)
            clientId = forceRef(record.value('clientId'))
            accCode = forceStringEx(accountElement.firstChildElement('CODE').text()) #????
            itemId = forceRef(record.value('accountItemId'))

            if not entries.has_key(clientId):
                entryCounter[insurerInfis] = entryCounter.setdefault(insurerInfis, 0) + 1
                entries[clientId] = self.addEntryElement(rootElement, record, entryCounter[insurerInfis])

            entryElement, _ = entries[clientId]

            eventId = forceRef(record.value('eventId'))

            if not events.has_key(eventId):
                idCaseCounter[insurerInfis] = idCaseCounter.setdefault(insurerInfis, 0) + 1
                events[eventId] = self.addEventElement(entryElement,
                                                       idCaseCounter[insurerInfis],
                                                       record)

            eventElement = events[eventId]

            self.addServiceElement(eventElement, forceRef(record.value('accountItemId')), record)
            serviceSum = forceDouble(record.value('serviceSum'))
            accountItemRefuseCode = forceStringEx(record.value('accountItemRefuseCode'))
            accountItemDate = forceDate(record.value('accountItemDate'))
            currEventTotals = eventsTotals.setdefault(eventId, [0.0, 0.0, 0.0, 0.0, 0.0]) # [total, payed, refused, amount, uet]
            currAccountTotals = accountTotals.setdefault(insurerInfis, [0.0, 0.0, 0.0]) # [total, payed, refused]
            currEventTotals[0] += round(serviceSum, 2)
            currAccountTotals[0] += round(serviceSum, 2)
            if accountItemRefuseCode and not eventId in eventRefuses:
                eventRefuses[eventId] = accountItemRefuseCode
            if accountItemDate:
                i = 2 if accountItemRefuseCode else 1
                currAccountTotals[i] += round(serviceSum, 2)
                currEventTotals[i] += round(serviceSum, 2)
            currEventTotals[3] += forceDouble(record.value('serviceAmount'))
            if forceStringEx(record.value('serviceCode')).startswith('3.'):
                currEventTotals[4] += forceDouble(record.value('serviceUET'))

            self.clientsForDeferredFilling.setdefault(insurerInfis, {}).setdefault(clientId,
                                                                                   (forceBool(record.value('isLittleStranger')),
                                                                                    forceInt(record.value('newbornSex')),
                                                                                    forceDate(record.value('newbornBirthDate')),
                                                                                    ))

            self.nextPhaseStep()

        self.nextPhase(len(accountTotals), u'Заполнение данных об общей стоимости счетов')
        # if round(accSumForCheck, 2) != round(sum(accountTotal.values()), 2):
        #     self.logger().critical(u'Обнаружено расхождение стоимости исходного '
        #                            u'общего счета (%s) и суммы стоимостей счетов по СМО (%s)' % (round(accSumForCheck, 2),
        #                                                                                          round(sum(accountTotal.values()), 2)))

        for insurerInfis, totals in accountTotals.iteritems():
            if self.isTerminated:
                self.onTerminating()
                return False
            _, accountElement, _ = self.hDocuments[insurerInfis]

            exposedSumElement = accountElement.firstChildElement('SUMMAV')
            payedSumElement = accountElement.firstChildElement('SUMMAP')
            refusedSumElement = accountElement.firstChildElement('SANK_MEK')
            perCapita = forceDouble(sums.get(insurerInfis, ''))
            if not perCapita:
                perCapita = 0.0
            CXMLHelper.setValue(exposedSumElement, '%.2f' % (totals[0] + perCapita ))
            CXMLHelper.setValue(payedSumElement, '%.2f' % (totals[1] + perCapita))
            CXMLHelper.setValue(refusedSumElement, '%.2f' % totals[2])
            self.nextPhaseStep()

        isPerCapita = bool(''.join(sums.values()))
        self.nextPhase(len(eventsTotals), u'Заполнение данных о стоимости счетов')
        for eventId, totals in eventsTotals.iteritems():
            if self.isTerminated:
                self.onTerminating()
                return False
            eventElement = events[eventId]
            totalElement = eventElement.firstChildElement('SUMV')
            payedElement = eventElement.firstChildElement('SUMP')
            refusedElement = eventElement.firstChildElement('SANK_IT')
            edColElement = eventElement.firstChildElement('ED_COL')
            edCol = totals[4]
            if not edCol:
                edCol = totals[3]
            CXMLHelper.setValue(edColElement, edCol)
            CXMLHelper.setValue(totalElement, totals[0])
            CXMLHelper.setValue(payedElement, totals[1])
            CXMLHelper.setValue(refusedElement, totals[2])
            if isPerCapita:
                customIdsp = self.customIdspMap.get(eventId, None)
                if customIdsp:
                    idspElem = eventElement.firstChildElement('IDSP')
                    CXMLHelper.setValue(idspElem,
                                        customIdsp)
            refuseCode = eventRefuses.get(eventId)
            if refuseCode:
                sank = CXMLHelper.addElement(eventElement, 'SANK', afterElem=['SANK_IT', 'SUMP', 'SUMV'])
                CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_CODE'),
                                    1)
                CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_SUM'),
                                    totals[2])
                CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_TIP'),
                                    1)
                CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_OSN'),
                                    refuseCode)
                CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_IST'),
                                    1)

        if not self.isTerminated:
            self.fillAdditionalDiagnosis(events)
        if not self.isTerminated:
            self.fillOrganisations()
        if not self.isTerminated:
            self.fillPersonSpeciality()
        if not self.isTerminated:
            self.fillFirstVisitProfile()

        if not self.isTerminated:
            self.fillPersonalData(insurerOkato)

        self.logger().info(u'Завершено')
        if self.isTerminated:
            self.onTerminating()
            return False
        return True

    def save(self, outDir):
        self.phaseReset(2)
        outDir = forceStringEx(outDir)
        self.nextPhase(len(self.hDocuments), u'Сохранение файлов H')
        for insurerInfis in self.hDocuments.keys():
            doc, _, headerElement = self.hDocuments[insurerInfis]
            fileName = forceStringEx(headerElement.firstChildElement('FILENAME').text())
            # fullFilename = os.path.join(outDir, u'%s.xml' % fileName)
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
                # body = codecs.encode(forceStringEx(doc.toString(4)), self.encoding)
                # zf.writestr(u'%s.xml' % fileName, body)
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





class CExportDialog(QtGui.QDialog):
    InitState = 0
    ExportState = 1
    SaveState = 2


    def __init__(self, db, accountId, engine, accountRecord, parent=None):
        super(CExportDialog, self).__init__(parent=parent)
        self._db = db
        self._accountId = accountId
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._engine = engine(db, accountRecord, progressInformer=self._pi)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._currentState = self.InitState

        self.setupUi()

        self.onStateChanged()

    def setParams(self, params):
        if isinstance(params, dict):
            outDir = forceStringEx(getPref(params, 'outDir', u''))
            if os.path.isdir(outDir):
                self.edtSaveDir.setText(outDir)
            accNumber = forceInt(getPref(params, 'accNumber', 0)) + 1
            self.spbAccountNumber.setValue(accNumber)

    def params(self):
        params = {}
        setPref(params, 'outDir', forceStringEx(self.edtSaveDir.text()))
        setPref(params, 'accNumber', self.spbAccountNumber.value())
        return params

    @property
    def currentState(self):
        return self._currentState

    @currentState.setter
    def currentState(self, value):
        if value in [self.InitState, self.ExportState, self.SaveState]:
            self._currentState = value
            self.onStateChanged()

    def onStateChanged(self):
        self.btnNextAction.setText(self._actionNames.get(self.currentState, u'<Error>'))
        self.btnClose.setEnabled(self.currentState != self.ExportState)
        self.gbInit.setEnabled(self.currentState == self.InitState)
        self.gbExport.setEnabled(self.currentState == self.ExportState)
        self.gbSave.setEnabled(self.currentState == self.SaveState)
        self.btnSave.setEnabled(bool(self._engine.hDocuments or self._engine.lDocuments))
        QtCore.QCoreApplication.processEvents()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        self.gbInit = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        numLayout = QtGui.QHBoxLayout()
        self.lblAccountNumber = QtGui.QLabel()
        numLayout.addWidget(self.lblAccountNumber)
        self.spbAccountNumber = QtGui.QSpinBox()
        self.spbAccountNumber.setRange(1, 999)
        numLayout.addWidget(self.spbAccountNumber)
        gbLayout.addLayout(numLayout)
        sums = QtGui.QHBoxLayout()
        sum1 = QtGui.QVBoxLayout()
        self.lbl85001 = QtGui.QLabel()
        self.lbl85001.setAlignment(QtCore.Qt.AlignCenter)
        sum1.addWidget(self.lbl85001)
        self.edt85001 = QtGui.QLineEdit()
        sum1.addWidget(self.edt85001)
        sums.addLayout(sum1)
        sum2 = QtGui.QVBoxLayout()
        self.lbl85002 = QtGui.QLabel()
        self.lbl85002.setAlignment(QtCore.Qt.AlignCenter)
        sum2.addWidget(self.lbl85002)
        self.edt85002 = QtGui.QLineEdit()
        sum2.addWidget(self.edt85002)
        sums.addLayout(sum2)
        sum3 = QtGui.QVBoxLayout()
        self.lbl85003 = QtGui.QLabel()
        self.lbl85003.setAlignment(QtCore.Qt.AlignCenter)
        sum3.addWidget(self.lbl85003)
        self.edt85003 = QtGui.QLineEdit()
        sum3.addWidget(self.edt85003)
        sums.addLayout(sum3)
        gbLayout.addLayout(sums)
        self.gbInit.setLayout(gbLayout)
        layout.addWidget(self.gbInit)

        # export block
        self.gbExport = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        self.progressBar = CProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setRange(0, 0)
        self.progressBar.setProgressFormat(u'(%v/%m)')
        self._pi.progressChanged.connect(self.progressBar.setProgress)
        gbLayout.addWidget(self.progressBar)
        self.gbExport.setLayout(gbLayout)
        layout.addWidget(self.gbExport)

        # save block
        self.gbSave = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtSaveDir = QtGui.QLineEdit(QtCore.QDir.homePath())
        self.edtSaveDir.setReadOnly(True)
        lineLayout.addWidget(self.edtSaveDir)
        self.btnBrowseDir = QtGui.QToolButton()
        self.btnBrowseDir.clicked.connect(self.onBrowseDir)
        lineLayout.addWidget(self.btnBrowseDir)
        gbLayout.addLayout(lineLayout)
        lineLayout = QtGui.QHBoxLayout()
        self.btnSave = QtGui.QPushButton()
        self.btnSave.clicked.connect(self.onSaveClicked)
        lineLayout.addWidget(self.btnSave)
        gbLayout.addLayout(lineLayout)
        self.gbSave.setLayout(gbLayout)
        layout.addWidget(self.gbSave)

        # log block
        self.logInfo = QtGui.QTextEdit()
        layout.addWidget(self.logInfo)
        self._loggerHandler.logged.connect(self.logInfo.append)

        # buttons block
        subLayout = QtGui.QHBoxLayout()
        self.btnNextAction = QtGui.QPushButton()
        self.btnNextAction.clicked.connect(self.onNextActionClicked)
        subLayout.addStretch()
        subLayout.addWidget(self.btnNextAction)
        self.btnClose = QtGui.QPushButton()
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranslateUi()

    def retranslateUi(self):
        context = unicode(getClassName(self))
        if isinstance(self._engine, CExportR85SMOEngine):
            self.setWindowTitle(forceTr(u'Экспорт. Крым. СМО', context))
        else:
            self.setWindowTitle(forceTr(u'Экспорт. Крым. СМО. Диспансеризация', context))
        self.gbInit.setTitle(forceTr(u'Параметры экспорта', context))
        self.lblAccountNumber.setText(forceTr(u'Номер реестра', context))
        self.lbl85001.setText(forceTr(u'85001', context))
        self.lbl85002.setText(forceTr(u'85002', context))
        self.lbl85003.setText(forceTr(u'85003', context))

        self.gbExport.setTitle(forceTr(u'Экспорт', context))

        self.gbSave.setTitle(forceTr(u'Сохранение результата', context))
        self.btnSave.setText(forceTr(u'Сохранить', context))

        self._actionNames = {self.InitState: forceTr(u'Экспорт', context),
                             self.ExportState: forceTr(u'Прервать', context),
                             self.SaveState: forceTr(u'Повторить', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))

    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ExportState
            try:
                sums = {'85001': forceStringEx(self.edt85001.text()),
                        '85002': forceStringEx(self.edt85002.text()),
                        '85003': forceStringEx(self.edt85003.text())}
                result = self._engine.process(self._accountId, self.spbAccountNumber.value(), sums) if isinstance(self._engine, CExportR85SMOEngine) else self._engine.process(self._accountId, self.spbAccountNumber.value())
            except:
                self.currentState = self.InitState
                raise
            self.currentState = self.SaveState if result else self.InitState
        elif self.currentState == self.ExportState:
            self._engine.terminate()
        elif self.currentState == self.SaveState:
            self.currentState = self.InitState
        self.onStateChanged()


    def canClose(self):
        return not ((self._engine.hDocuments or self._engine.lDocuments)) or \
               QtGui.QMessageBox.warning(self,
                                         u'Внимание!',
                                         u'Остались несохраненные файлы выгрузок\n'
                                         u'которые будут утеряны.\n'
                                         u'Вы уверены, что хотите покинуть менеджер экспорта?\n',
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                         QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes

    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()

    def done(self, result):
        if self.canClose():
            super(CExportDialog, self).done(result)

    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()

    @QtCore.pyqtSlot()
    def onBrowseDir(self):
        saveDir = forceStringEx(QtGui.QFileDialog.getExistingDirectory(self,
                                                         u'Укажите директорию для сохранения файлов выгрузки',
                                                         self.edtSaveDir.text()))
        if os.path.isdir(saveDir):
            self.edtSaveDir.setText(saveDir)

    @QtCore.pyqtSlot()
    def onSaveClicked(self):
        self.btnClose.setEnabled(False)
        self._engine.save(self.edtSaveDir.text())
        self.onStateChanged()



def main():
    import sys
    from library.database import connectDataBaseByInfo
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.3',
                      'port' : 3306,
                      'database' : 'crimeaMar',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    accountId = 669 #248 #253
    w = CExportDialog(QtGui.qApp.db, accountId)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()