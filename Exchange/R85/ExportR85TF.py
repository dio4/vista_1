# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   09.04.2015
'''

#TODO: craz: выгрузка нескольких счетов
#TODO: craz: Сохранение директории по умолчанию
#TODO: craz: Объединить вызгрузки по Крыму
#TODO: Обработка номера реестра
#TODO: craz: Откуда брать PODR? Из eventExecPerson или из serviceExecPerson
#TODO: craz: Рассмотреть логику accCode из ExportR85MTR. Возможно, сделать нечто аналогичное
#TODO: craz: Хранить в IDSERV Account_Item.id из МО
#TODO: craz: отвязаться от названия договора
#FIXME: craz: insurerOKATO

import logging, os, zipfile

from PyQt4 import QtCore, QtGui, QtXml

from Accounting.Utils import CTariff, CPayStatus, getPayStatusMask, updateDocsPayStatus
from Events.Utils import getEventLengthDays
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, forceTr, \
                          getClassName, getPref, setPref, CLogHandler, formatSNILS, forceTime, forceDateTime, toVariant
from library.XML.XMLHelper import CXMLHelper

def exportR85TF(widget, accountId):
    exportR85Int(widget, accountId)

def exportR85HTTF(widget, accountId):
    exportR85Int(widget, accountId, isHighTech=True)

def exportR85Int(widget, accountId, isHighTech=False):
    exportWindow = CExportDialog(QtGui.qApp.db, accountId, widget, isHighTech=isHighTech)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), {})
    exportWindow.setParams(params)
    exportWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), exportWindow.params())


class CExportR85TFEngine(object):
    encoding = u'windows-1251'
    version = u'2.1'
    fundCode = u'85000'

    defaultDateFormat = QtCore.Qt.ISODate

    dummy = '#'*25
    dummyN = 0

    PrimaryMKBTypeCode = 2
    SecondaryMKBTypeCode = 9
    ComplicatedMKBTypeCode = 3

    counterCode = 'tfCode'

    fileNamePrefix = 'H'

    ecoKPGList = ['2.1.1371', '2.1.1372', '2.1.1373', '2.1.1374']

    def __init__(self, db, progressInformer=None, FLC=False):
        self._db = db
        self._progressInformer = progressInformer if isinstance(progressInformer, CProgressInformer) \
                                                  else CProgressInformer(processEventsFlag=None)
        self._logger = logging.getLogger(name=getClassName(self))
        self._logger.setLevel(logging.INFO)

        self.totalPhases = 0
        self.currentPhase = 0
        self.FLC = FLC

        self.hDocuments = {}
        self.lDocuments = {}
        self.pDocuments = {}
        self.personSpecialityForDeferredFilling = {}
        self.orgForDeferredFilling = {}
        self.clientsForDeferredFilling = {}
        self.firstVisitsForDeferredFilling = {}
        self.socStatusForDeferredFilling = {}
        self.mainOperationExported = set()
        self.eventsForDeferredUpdating = {}
        self.hospitalBedProfileCodesForDeferredFilling = {}
        self.emergencyCallsForDeferredFilling = {}
        self.edColForDeferredFilling = {}
        self.profilForDeferredFilling = {}
        self.kindForDefferredFilling = {}
        self.veteranSocStatusTypeId = None
        self.lpuInfis = None

        self.isTerminated = False
        self._counterId = None

        self.criticalErrors = [] # Список критических ошибок, с которыми фонд не примет данный счет.

        self.datePrev = None
        self.toothPrev = None
        self.isPRIMEUSL = 0

    def logger(self):
        return self._logger

    #TODO: craz: progressInformer setter/getter?

#----- XML Fillers -----

    def checkServiceElement(self, record):
        """Проверка, что данная запись должна попасть в тег USL (введена, чтобы исключать Account_Item'ы по ВМП)
        UPD: исключаем Account_Item'ы по МЭС, подозреваю, что это неправильно, уточнить правило исключения
        """
        return not record.value('actionId').isNull() or not record.value('visitId').isNull()

    def postProcessEventElement(self, eventElement, record):
        """Точка входа для наследников, которым нужно добавить в запись что-то свое.

        @param eventElement:
        @param record:
        @return:
        """
        pass

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

    def createLXMLDocument(self, insurerInfis, accountRecord):
        doc = CXMLHelper.createDomDocument(rootElementName='PERS_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        header = self.addHeaderElement(rootElement, insurerInfis, accountRecord, lfile=True)
        return doc

    def createHXMLDocument(self, insurerInfis, accountRecord):
        doc = CXMLHelper.createDomDocument(rootElementName='ZL_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        headerElement = self.addHeaderElement(rootElement, insurerInfis, accountRecord)
        accountElement = self.addAccountElement(rootElement, accountRecord)
        return doc, accountElement, headerElement

    def createPXMLDocument(self):
        doc = CXMLHelper.createDomDocument(rootElementName='PERSON_SPEC_LIST', encoding=self.encoding)
        return doc

    def addHeaderElement(self, rootElement, insurerInfis, accountRecord, lfile=False):
        header = CXMLHelper.addElement(rootElement, 'ZGLV')
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'VERSION'),
                            self.version[:5])
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'DATA'),
                            QtCore.QDate.currentDate().toString(self.defaultDateFormat))
        lpuInfis = forceStringEx(accountRecord.value('lpuInfis'))
        settleDate = forceDate(accountRecord.value('accountSettleDate'))
        accountNumber = forceStringEx(accountRecord.value('accountNumber')).zfill(5)
        fileName = u'%sM%sT%s_%s%s' % (self.fileNamePrefix,
                                       lpuInfis,
                                      insurerInfis,  # self.fundCode,
                                      settleDate.toString('yyMM'),
                                      accountNumber)
        lFileName = 'L' + fileName[1:]
        if self.FLC:
            fileName = 'P' + fileName
            lFileName = 'P' + lFileName
        if lfile:
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME'),
                                lFileName)
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME1'),
                                fileName)
        else:
            CXMLHelper.setValue(CXMLHelper.addElement(header, 'FILENAME'),
                            fileName)
        return header

    def addAccountElement(self, rootElement, record):
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

        accDate = forceDate(record.value('accountSettleDate'))
        accCode = forceStringEx(record.value('accountNumber')).zfill(5)#forceStringEx(self.getCounterValue())

        CXMLHelper.setValue(CXMLHelper.addElement(account, 'CODE'),
                            accCode[-8:])
        lpuInfis = forceStringEx(record.value('lpuInfis'))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'CODE_MO'),
                            lpuInfis)
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'YEAR'),
                            accDate.year())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'MONTH'),
                            accDate.month())
        # nschet = lpuInfis + forceStringEx(accDate.toString('MM')) + accCode
        nschet = accCode.lstrip('0')
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'NSCHET'),
                            nschet[:15])
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'DSCHET'),
                            forceDate(record.value('accountDate')).toString(self.defaultDateFormat))
        if not self.FLC:
            CXMLHelper.setValue(CXMLHelper.addElement(account, 'PLAT'),
                                '85')
        CXMLHelper.addElement(account, 'SUMMAV')
        # CXMLHelper.addElement(account, 'SUMMAP')
        # CXMLHelper.addElement(account, 'SANK_MEK')
        return account

    def addEntryElement(self, rootElement, record, entryNumber):
        entryElement = CXMLHelper.addElement(rootElement, 'ZAP')
        CXMLHelper.setValue(CXMLHelper.addElement(entryElement, 'N_ZAP'),
                            entryNumber)
        CXMLHelper.setValue(CXMLHelper.addElement(entryElement, 'PR_NOV'),
                            1 if forceInt(record.value('rerun')) != 0 else 0)
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
            * **newbornBirthWeight** - Event_LittleStranger.birthWeight
            * **
        @return:
        """

        clientId = forceInt(record.value('clientId'))
        littleStrangerId = forceInt(record.value('littleStrangerId'))
        if littleStrangerId:
            idPac = '{clientId}/{littleStrangerId}'.format(clientId=clientId, littleStrangerId=littleStrangerId)
        else:
            idPac = clientId
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
        policySerial = forceStringEx(record.value('policySerial'))
        if policyKind == 1 and policySerial:
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SPOLIS'),
                                policySerial[:10])
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
                            '0' if not isLittleStranger else '%d%s%d' % (1 if record.value('newbornSex').isNull() else forceInt(record.value('newbornSex')),
                                                            birthDate.toString('ddMMyy'),
                                                            forceInt(record.value('newbornNumber'))))

    def addEventElement(self, entryElement, idCase, record):
        """

        @param entryElement:
        @param idCase:
        @param record:
        @return:
        """

        serviceCode = forceStringEx(record.value('serviceCode'))
        eventId = forceRef(record.value('eventId'))
        emergencyAid = forceRef(record.value('emergencyCallId')) is not None
        #TODO: убедиться, что мы наконец можем использовать только eventExecPersonId
        personId = forceRef(record.value('eventExecPersonId'))

        self.eventsForDeferredUpdating[eventId] = idCase
        if forceString(record.value('eventGoalCode')) == '1' and not forceBool(record.value('isStoma')):
            self.edColForDeferredFilling[eventId] = 1.0
        eventTypePurposeFedCode = forceInt(record.value('eventTypePurposeFedCode'))

        eventElement = CXMLHelper.addElement(entryElement, 'SLUCH')
        if eventTypePurposeFedCode in [1, 2]:
            self.hospitalBedProfileCodesForDeferredFilling.setdefault(eventId, eventElement)

        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDCASE'),
                            idCase)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'USL_OK'),
                            eventTypePurposeFedCode)
        vidpomElement = CXMLHelper.addElement(eventElement, 'VIDPOM')
        CXMLHelper.setValue(vidpomElement, forceInt(record.value('eventTypeAidKindFedCode')))
        eventOrder = forceInt(record.value('eventOrder'))
        forPom = {
            1: 3,  # плановая
            2: 1,  # экстренная
            6: 2,  # неотложная (deprecated)
            5: 2,  # неотложка
        }.get(eventOrder, 3)
        if emergencyAid:
            forPom = 1
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'FOR_POM'),
                            forPom)
        referralNumber = forceStringEx(record.value('referralNumber'))
        if referralNumber:   # mdldml: при EXTR=1 заполняется в обязательном порядке (сейчас у нас не заполняется)
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NPR_N', afterElem='METOD_HMP'),
                                referralNumber)
        relegateMO = forceStringEx(record.value('relegateInfisCode'))
        if relegateMO:   # mdldml: при EXTR=1 заполняется в обязательном порядке (сейчас у нас не заполняется)
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NPR_MO'),
                                relegateMO)

        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NPR_MO'),
        #                     self.dummy)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'EXTR'),
                            2 if eventOrder == 2 else 1)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'LPU'),
                            self.lpuInfis)
        if emergencyAid:
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'LPU_1'),
                                forceString(record.value('emergencyMiacCode')))
        podrElement = CXMLHelper.addElement(eventElement, 'PODR')
        profilElement = CXMLHelper.addElement(eventElement, 'PROFIL')
        if serviceCode.startswith('63'):
            self.firstVisitsForDeferredFilling.setdefault(eventId, []).append(profilElement)
        else:
            CXMLHelper.setValue(profilElement,
                                forceInt(record.value('serviceAidProfileFedCode')))
            self.profilForDeferredFilling.setdefault((forceInt(record.value('serviceId')), personId), []).append(profilElement)
            self.kindForDeferredFilling.setdefault((forceInt(record.value('serviceId')), personId), []).append(vidpomElement)


        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DET'),
                            1 if forceInt(record.value('clientAge')) < 18
                                 or forceBool(record.value('isLittleStranger')) else 0)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NHISTORY'),
                            forceStringEx(record.value('eventId'))[:50])
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_1'),
                            forceDate(record.value('eventSetDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_2'),
                            forceDate(record.value('eventExecDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DS1'),
                            forceStringEx(record.value('eventPrimaryMKB')))
        # if eventTypePurposeFedCode in [1, 2]:
        #     CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'CODE_MES1'),
        #                         forceStringEx(record.value('mesCode')))
        if emergencyAid:
            # mdldml: знаем, чем заполнять, но пока не знаем, куда (после какого тега) и знать не хотим
            # поэтому заполняем после того, как уже появились USL-теги
            self.emergencyCallsForDeferredFilling[eventElement] = (
                forceDateTime(record.value('emergencyDepartureDate')).toString('hh:mm'),
                forceDateTime(record.value('emergencyArrivalDate')).toString('hh:mm'),
                forceInt(record.value('emergencyPlace'))
            )

        # TODO: поэксперементировать на сборке. Возможно, убрать forceString
        birthWeight = forceInt(forceDouble(forceStringEx(record.value('newbornBirthWeight'))))
        if birthWeight:
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VNOV_M'),
                            birthWeight)

        if forceRef(record.value('emergencyCallId')) is None:
            code_mes = forceStringEx(record.value('mesCode'))
            if not code_mes:
                code_mes = forceStringEx(record.value('visitServiceCode'))
            if code_mes:
                CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'CODE_MES1'),
                                    code_mes)
        else:   # mdldml: только для СМП
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'CODE_MES1'),
                                serviceCode)


        eventResult = forceInt(record.value('eventResultFedCode'))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'RSLT'),
                            eventResult)
        diagnosticResult = forceInt(record.value('eventPrimaryMKBResultFedCode'))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'ISHOD'),
                            diagnosticResult)

        specElement = CXMLHelper.addElement(eventElement, 'PRVS')
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VERS_SPEC'),
                            u'V015')

        self.personSpecialityForDeferredFilling.setdefault(personId,
             []).append((specElement,
                         CXMLHelper.addElement(eventElement, 'IDDOKT'),
                         podrElement,
                         eventElement))

        if not forceStringEx(record.value('clientPatrName')):
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'OS_SLUCH'),
                                2)

        #для подушевых, если нет суммы и codeusl.startswith(3) -> 26, codeusl.startswith(4) -> 35
        idsp = forceInt(record.value('eventAidUnitFedCode'))
        # if perCapita:
        #     if serviceCode.startswith('3'):
        #         idsp = '26'
        #     elif serviceCode.startswith('4'):
        #         idsp = '35'
        idspElement = CXMLHelper.addElement(eventElement, 'IDSP')
        smoCode = forceStringEx(record.value('insurerInfis'))
        if idsp:
            CXMLHelper.setValue(idspElement,
                                idsp)
        else:
            if not record.value('mesCode').isNull():
                CXMLHelper.setValue(idspElement,
                                    32)
            elif emergencyAid:
                CXMLHelper.setValue(idspElement,
                                    35 if smoCode.startswith('85') else 24)
            elif forceBool(record.value('isStoma')):
                CXMLHelper.setValue(idspElement,
                                    9)
            else:
                CXMLHelper.setValue(idspElement,
                                    29)

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
                            0)

        # CXMLHelper.addElement(eventElement, 'SUMP')
        # CXMLHelper.addElement(eventElement, 'SANK_IT')
        if eventTypePurposeFedCode == 1 and forceInt(record.value('hospParent')) == 1:
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'HOSP_PARENT'),
                                forceInt(record.value('hospParent')))

        self.postProcessEventElement(eventElement, record)
        return eventElement

    #Потому что появилась логика для стоматологий
    def addServiceElementProxy(self, eventElement, idServ, record):
        if forceStringEx(record.value('serviceCode')).startswith('63') \
                    and forceInt(record.value('toothNumber')) != self.toothPrev\
                    and self.isPRIMEUSL == 0:
            if all([hasattr(self, attr) for attr in ['stomaBaseEventElement', 'stomaBaseIdServ', 'stomaBaseServiceRecord']]):
                newIdServ = forceString(self.stomaBaseIdServ) + '-' + forceString(self.stomaIdServCounter)
                self.stomaIdServCounter += 1
                self.addServiceElement(self.stomaBaseEventElement, newIdServ, self.stomaBaseServiceRecord, tooth=forceInt(record.value('toothNumber')))

        self.isPRIMEUSL = 0
        if forceDouble(record.value('serviceUET')) != 0.0 and not forceStringEx(record.value('serviceCode')).startswith('63'):
            self.stomaBaseEventElement = eventElement
            self.stomaBaseIdServ = idServ
            self.stomaIdServCounter = 0
            self.stomaBaseServiceRecord = record
            self.isPRIMEUSL = 1

        serviceElement = self.addServiceElement(eventElement, idServ, record)

        if forceString(record.value('actionTypeCode')).startswith('63'):
            self.toothPrev = forceInt(record.value('toothNumber'))
        self.datePrev = forceDate(record.value('actionEndDate'))

        return serviceElement

    def addServiceElement(self, eventElement, idServ, record, tooth=None):
        """

        @param eventElement:
        @param idServ:
        @param record:
        @return:
        """
        serviceCode = forceStringEx(record.value('serviceCode'))
        eventId = forceRef(record.value('eventId'))
        eventTypePurposeFedCode = forceInt(record.value('eventTypePurposeFedCode'))
        personId = forceRef(record.value('visitPersonId')) \
                   or forceRef(record.value('actionPersonId')) \
                   or forceRef(record.value('eventExecPersonId'))
        #FIXME: Всегда ли есть врач? нужно ли брать из диагноза?
        if not self.checkServiceElement(record):
            return None

        serviceElement = CXMLHelper.addElement(eventElement, 'USL', afterElem=['USL', 'SANK', 'SANK_IT', 'SUMP', 'OPLATA', 'SUMV'])

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
        if serviceCode.startswith('63'):
            self.firstVisitsForDeferredFilling.setdefault(forceRef(record.value('eventId')), []).append(profilElement)
        else:
            CXMLHelper.setValue(profilElement,
                                forceInt(record.value('serviceAidProfileFedCode')))
            self.profilForDeferredFilling.setdefault((forceInt(record.value('serviceId')), personId), []).append(profilElement)

        hospitalBedCode = forceString(record.value('hospitalBedCode'))
        if eventTypePurposeFedCode in [1, 2]:
            # self.hospitalBedProfileCodesForDeferredFilling.setdefault(eventId, eventElement)
            if hospitalBedCode:
                CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'PROFIL_BED'), hospitalBedCode)
        # CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'VID_VME'),
        #                     self.dummy)
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'DET'),
                            1 if forceInt(record.value('clientAge')) < 18
                                 or forceBool(record.value('isLittleStranger'))  else 0)
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
        if eventTypePurposeFedCode in [1, 2] and forceBool(record.value('isMainOperation')) and eventId not in self.mainOperationExported:
            self.mainOperationExported.add(eventId)
            CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'OPERATION'), 1)

        if forceDouble(record.value('serviceUET')) != 0.0 and not forceString(record.value('actionTypeCode')).startswith('63'):
            if not tooth:
                stmt = u'''
                    SELECT
                        A.id AS action_id, API.value AS toothNumber
                    FROM
                        Action A
                        INNER JOIN ActionProperty AP ON A.id = AP.action_id
                        INNER JOIN ActionPropertyType APT ON AP.type_id = APT.id
                        INNER JOIN ActionProperty_Integer API ON AP.id = API.id
                        INNER JOIN ActionType AT ON A.actionType_id = AT.id
                    WHERE
                        APT.name = 'номер зуба'
                        AND A.event_id = %i
                        AND AT.code like '63%%'
                        AND A.endDate >= '%s'
                    ORDER BY DATE(A.endDate), A.id
                    LIMIT 1
                ''' % (forceRef(record.value('eventId'))
                                              # , forceDate(record.value('eventExecDate')).toString('yyyy.MM.dd')
                                                , forceDate(record.value('visitDate')).toString('yyyy.MM.dd')
                       )

                query1 = self._db.query(stmt)
                if query1.next():
                    record1 = query1.record()
                    if forceInt(record1.value('toothNumber')):
                        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'TOOTH'),
                                        forceInt(record1.value('toothNumber')))
            else:
                CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'TOOTH'),
                                    tooth)

        if forceString(record.value('actionTypeCode')).startswith('63') and forceInt(record.value('toothNumber')):
            CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'TOOTH'),
                                forceInt(record.value('toothNumber')))
        # mdldml: При выгрузке ФЛК не заполняем информацию о суммах
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'TARIF'),
                            '%.2f' % (forceDouble(record.value('servicePrice')) if not self.FLC else 0.0))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'SUMV_USL'),
                            '%.2f' % (forceDouble(record.value('serviceSum')) if not self.FLC else 0.0))
        # craz: PRVS и CODE_MD заполняются позже, отдельным запросом

        self.personSpecialityForDeferredFilling.setdefault(personId,
            []).append((CXMLHelper.addElement(serviceElement, 'PRVS'),
                       CXMLHelper.addElement(serviceElement, 'CODE_MD'),
                        podrElement,
                        serviceElement))

        if serviceCode.startswith('1'):
            self.socStatusForDeferredFilling.setdefault(forceInt(record.value('clientId')), set()).add(eventElement)

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
                                                   tableDiagnosis['deleted'].eq(0),
                                                   tableDiagnosis['MKB'].ne('')])
        self.nextPhase(len(recordList), u'Обработка данных по доп. диагнозам')
        additionalDiagnosisSet = set()
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
            tagType = afterNode[0]
            if (eventElement, tagType) not in additionalDiagnosisSet:
                CXMLHelper.setValue(CXMLHelper.addElement(eventElement, tagType, afterElem=afterNode),
                                    forceStringEx(record.value('MKB')))
                additionalDiagnosisSet.add((eventElement, tagType))
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
            for specialityElement, personElement, orgStructureElement, parentElement in elementList:
                if personFederalCode:
                    CXMLHelper.setValue(personElement, personFederalCode)
                if specialityFederalCode:
                    CXMLHelper.setValue(specialityElement, specialityFederalCode)
                if orgStructureInfisCode:
                    CXMLHelper.setValue(orgStructureElement, orgStructureInfisCode)
                else:
                    parentElement.removeChild(orgStructureElement)
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

    def fillPersonFullInfo(self):
        def createPersonsQuery():
            """
            mode: 0 - GUI, 1 - console
            """
            db = QtGui.qApp.db

            tablePerson = db.table('Person')
            tableSpeciality = db.table('rbSpeciality')
            tableOrg = db.table('Organisation')

            table = tablePerson.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
            table = table.leftJoin(tableOrg, tableOrg['id'].eq(tablePerson['org_id']))

            cols = [tablePerson['code'],
                    tablePerson['federalCode'],
                    tablePerson['regionalCode'],
                    tablePerson['lastName'],
                    tablePerson['firstName'],
                    tablePerson['patrName'],
                    tableOrg['miacCode'],
                    tablePerson['retireDate'],
                    tablePerson['retired'],
                    tablePerson['birthDate'],
                    tablePerson['sex'],
                    tablePerson['academicDegree'],
                    tableSpeciality['code'].alias('specialityCode'),
                    ]

            cond = [tablePerson['deleted'].eq(0)]
            cond.append(tableOrg['miacCode'].eq(forceStringEx(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))))

            stmt = db.selectStmt(table, cols, cond, isDistinct = True)
            return db.query(stmt)

        def createSpecialitiesQuery():
            """
            Получаем список всех специльностей, имеющихся у выгружаемых врачей.
            """
            db = QtGui.qApp.db

            tablePerson = db.table('Person')
            tableSpeciality = db.table('rbSpeciality')
            tableOrg = db.table('Organisation')

            table = tablePerson.innerJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
            table = table.innerJoin(tableOrg, [tableOrg['id'].eq(tablePerson['org_id']),
                                               tableOrg['miacCode'].eq(forceStringEx(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode')))]) # Почему так сложно?

            cols = [
                    tableSpeciality['code'],
                    tableSpeciality['name'],
                    tableSpeciality['OKSOName'],
                    tableSpeciality['OKSOCode'],
                    tableSpeciality['federalCode'],
                    tableSpeciality['sex'],
                    tableSpeciality['age'],
                    tableSpeciality['mkbFilter'],
                    tableSpeciality['regionalCode']
                    ]

            cond = [tablePerson['deleted'].eq(0)]

            stmt = db.selectStmt(table, cols, cond, isDistinct = True)
            return db.query(stmt)


        self.nextPhase(1, u'Загрузка данных о специальностях и врачах')
        pDoc = self.pDocuments.get(self.fundCode, None)
        if pDoc:
            rootElement  = CXMLHelper.getRootElement(pDoc)
            specsElement = CXMLHelper.addElement(rootElement, 'SPECS')
            specsQuery = createSpecialitiesQuery()
            while specsQuery.next():
                record = specsQuery.record()
                element = CXMLHelper.addElement(specsElement, 'Speciality')
                for i in xrange(record.count()):
                    CXMLHelper.addAttribute(element, forceStringEx(record.fieldName(i))).setValue(forceStringEx(record.value(i)))

            persElement = CXMLHelper.addElement(rootElement, 'PERSONS')
            persQuery = createPersonsQuery()
            while persQuery.next():
                record = persQuery.record()
                element = CXMLHelper.addElement(persElement, 'Person')
                for i in xrange(record.count()):
                    CXMLHelper.addAttribute(element, forceStringEx(record.fieldName(i))).setValue(forceStringEx(record.value(i)))


    def fillPersonalData(self, mapInsurerOkato):
        clientRelativesForDeferredFilling = {}
        okatoForDeferredFilling = {}
        for insurerInfis, clients in self.clientsForDeferredFilling.iteritems():
            self.nextPhase(1, u'Загрузка персональных данных')
            lDoc = self.lDocuments.get(insurerInfis, None)
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
                clientId = forceInt(record.value('clientId'))
                littleStrangerMap = clients.get(clientId, {})
                if not littleStrangerMap:
                    continue
                for littleStrangerId, (insurerInfis, isLittleStranger, newbornSex, newbornBirthDate, hospParent) in littleStrangerMap.items():
                    pers = CXMLHelper.addElement(rootElement, 'PERS')
                    insurerOKATO = mapInsurerOkato.get(insurerInfis, None)
                    if littleStrangerId:
                        idPac = '{clientId}/{littleStrangerId}'.format(clientId=clientId, littleStrangerId=littleStrangerId)
                    else:
                        idPac = clientId
                    CXMLHelper.setValue(CXMLHelper.addElement(pers, 'ID_PAC'),
                                        idPac)
                    lastName = forceStringEx(record.value('lastName'))
                    firstName = forceStringEx(record.value('firstName'))
                    patrName = forceStringEx(record.value('patrName'))
                    sex = forceInt(record.value('sex'))
                    birthDate = forceDate(record.value('birthDate'))
                    birthPlace = forceStringEx(record.value('birthPlace'))

                    if lastName:
                        famElement = CXMLHelper.addElement(pers, 'FAM')
                    if firstName:
                        imElement = CXMLHelper.addElement(pers, 'IM')
                    if patrName:
                        otElement = CXMLHelper.addElement(pers, 'OT')
                    wElement = CXMLHelper.addElement(pers, 'W')
                    drElement = CXMLHelper.addElement(pers, 'DR')

                    if birthPlace:
                        CXMLHelper.setValue(CXMLHelper.addElement(pers, 'MR'),
                                            birthPlace)
                    if not isLittleStranger:
                        if lastName:
                            CXMLHelper.setValue(famElement, lastName)
                        if firstName:
                            CXMLHelper.setValue(imElement, firstName)
                        if patrName:
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
                        if lastName:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'FAM_P'),
                                                lastName)
                        if firstName:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'IM_P'),
                                                firstName)
                        if patrName:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OT_P'),
                                                patrName)
                        if sex:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'W_P'),
                                                sex)
                        if birthDate.isValid():
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
                    if not hospParent or isLittleStranger:
                        docType = forceInt(record.value('docTypeFedCode'))
                        if docType:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCTYPE'),
                                                docType)
                        docSer = forceStringEx(record.value('documentSerial'))
                        if docSer:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCSER'),
                                                docSer)
                        docNum = forceStringEx(record.value('documentNumber'))
                        if docNum:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCNUM'),
                                                docNum)
                        snils = formatSNILS(forceStringEx(record.value('SNILS')))
                        if snils:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'SNILS'),
                                                snils)
                        okatog = forceStringEx(record.value('placeOKATO'))
                        if okatog:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OKATOG'),
                                                okatog)
                        if insurerOKATO:
                            CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OKATOP'),
                                                insurerOKATO)

                    if hospParent and not isLittleStranger:
                        clientRelativesForDeferredFilling.setdefault(clientId, pers)
                        okatoForDeferredFilling.setdefault(clientId, insurerOKATO)
                    self.nextPhaseStep()

        self.fillRelatives(clientRelativesForDeferredFilling, okatoForDeferredFilling)

    def fillRelatives(self, clientRelativesForDeferredFilling, okatoForDeferredFilling):
        tableClientRelation = self._db.table('ClientRelation')
        relativeClientMap = {}

        clientRelativesList = self._db.getRecordList(
            tableClientRelation,
            cols=[tableClientRelation['client_id'], tableClientRelation['relative_id']],
            where=tableClientRelation['client_id'].inlist(clientRelativesForDeferredFilling.keys())
        )
        clientRelativesList.extend(self._db.getRecordList(
            tableClientRelation,
            cols=[tableClientRelation['client_id'].alias('relative_id'), tableClientRelation['relative_id'].alias('client_id')],
            where=tableClientRelation['relative_id'].inlist(clientRelativesForDeferredFilling.keys())
        ))
        for record in clientRelativesList:
            relativeClientMap[forceInt(record.value('relative_id'))] = forceInt(record.value('client_id'))

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

        cols = [tableClient['id'].alias('relativeId'),
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
                                            where=tableClient['id'].inlist(relativeClientMap.keys())
                                            )

        for record in recordList:
            relativeId = forceInt(record.value('relativeId'))
            clientId = relativeClientMap[relativeId]
            pers = clientRelativesForDeferredFilling[clientId]

            lastName = forceStringEx(record.value('lastName'))
            firstName = forceStringEx(record.value('firstName'))
            patrName = forceStringEx(record.value('patrName'))
            sex = forceInt(record.value('sex'))
            birthDate = forceDate(record.value('birthDate'))
            birthPlace = forceStringEx(record.value('birthPlace'))

            if birthPlace:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'MR'),
                                    birthPlace)
            if lastName:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'FAM_P'),
                                    lastName)
            if firstName:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'IM_P'),
                                    firstName)
            if patrName:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OT_P'),
                                    patrName)
            if sex:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'W_P'),
                                    sex)
            if birthDate.isValid():
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
            docType = forceInt(record.value('docTypeFedCode'))
            if docType:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCTYPE'),
                                    docType)
            docSer = forceStringEx(record.value('documentSerial'))
            if docSer:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCSER'),
                                    docSer)
            docNum = forceStringEx(record.value('documentNumber'))
            if docNum:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'DOCNUM'),
                                    docNum)
            snils = formatSNILS(forceStringEx(record.value('SNILS')))
            if snils:
                CXMLHelper.setValue(CXMLHelper.addElement(pers, 'SNILS'),
                                    snils)
            # пока что уберем
            # okatog = forceStringEx(record.value('placeOKATO'))
            # if okatog:
            #     CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OKATOG'),
            #                         okatog)

            # insurerOKATO = okatoForDeferredFilling.get(clientId)
            # if insurerOKATO:
            #     CXMLHelper.setValue(CXMLHelper.addElement(pers, 'OKATOP'),
            #                         insurerOKATO)


    def fillSocStatusData(self):
        self.nextPhase(1, u'Загрузка данных о ветеранах')

        tableClientSocStatus = self._db.table('ClientSocStatus')
        tableSocStatusClass = self._db.table('rbSocStatusClass')

        queryTable = tableClientSocStatus.innerJoin(tableSocStatusClass,
                                                    tableSocStatusClass['id'].eq(tableClientSocStatus['socStatusClass_id']))

        # FIXME: craz: класс соц. статуса?
        recordList = self._db.getRecordList(table=queryTable,
                                            cols=[tableClientSocStatus['client_id']],
                                            where=[tableClientSocStatus['client_id'].inlist(self.socStatusForDeferredFilling),
                                                   tableClientSocStatus['socStatusType_id'].eq(self.veteranSocStatusTypeId),
                                                   tableSocStatusClass['flatCode'].eq('specialCase'),
                                                   tableClientSocStatus['deleted'].eq(0)],
                                            isDistinct=True)
        for record in recordList:
            clientId = forceRef(record.value('client_id'))
            for element in self.socStatusForDeferredFilling.get(clientId, []):
                CXMLHelper.setValue(CXMLHelper.addElement(element, 'OS_SLUCH', afterElem='IDDOKT'),
                                    '20')

    def fillHospitalBedProfiles(self):
        self.nextPhase(1, u'Загрузка данных о профилях коек')

        tableEvent = self._db.table('Event')
        query = self._db.query(u'''
            SELECT
                Event.id AS eventId,
                (
                    SELECT
                        rbHBP.code
                    FROM
                        Action A
                        INNER JOIN ActionType AT ON A.actionType_id = AT.id
                        INNER JOIN ActionProperty AP ON A.id = AP.action_id
                        INNER JOIN ActionPropertyType APT ON AP.type_id = APT.id
                        INNER JOIN ActionProperty_rbHospitalBedProfile APrbHBP ON APrbHBP.id = AP.id
                        INNER JOIN rbHospitalBedProfile rbHBP ON rbHBP.id = APrbHBP.value
                    WHERE
                        A.event_id = Event.id
                        AND AT.flatCode LIKE 'moving%%'
                        AND APT.name = 'профиль койки'
                        AND APT.valueDomain = 'rbHospitalBedProfile'
                    ORDER BY
                        A.idx
                    LIMIT 1
                ) AS movingHospitalBedCode
            FROM
                Event
            WHERE
                %s
        ''' % tableEvent['id'].inlist(self.hospitalBedProfileCodesForDeferredFilling))

        while query.next():
            record = query.record()
            eventId = forceRef(record.value('eventId'))
            eventElement = self.hospitalBedProfileCodesForDeferredFilling.get(eventId)
            # if not hospitalBedCode:
            hospitalBedCode = forceString(record.value('movingHospitalBedCode'))
            if hospitalBedCode:
                CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'PROFIL_BED', afterElem='PROFIL'), hospitalBedCode)

    def fillEmergencyInfo(self):
        self.nextPhase(1, u'Заполнение информации по СМП')
        for eventElement in self.emergencyCallsForDeferredFilling:
            departure, arrival, place = self.emergencyCallsForDeferredFilling[eventElement]
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'SMP_EXIT', afterElem=['HOSP_PARENT', 'USL', 'SANK', 'SANK_IT', 'SUMP', 'OPLATA']),
                                departure)
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'SMP_ARRIVAL', afterElem='SMP_EXIT'),
                                arrival)
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'SMP_MESTO', afterElem='SMP_ARRIVAL'),
                                place)

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

    def getAccountRecord(self, accountId):
        tableAccount = self._db.table('Account')
        tableContract = self._db.table('Contract')
        tableOrganisation = self._db.table('Organisation')

        cols = [
            tableAccount['date'].alias('accountDate'),
            tableAccount['number'].alias('accountNumber'),
            tableAccount['settleDate'].alias('accountSettleDate'),
            tableAccount['sum'].alias('accountSum'),
            tableOrganisation['infisCode'].alias('lpuInfis'),
        ]
        queryTable = tableAccount.innerJoin(tableContract, tableContract['id'].eq(tableAccount['contract_id']))
        queryTable = queryTable.innerJoin(tableOrganisation, tableOrganisation['id'].eq(tableContract['recipient_id']))
        accountRecord = self._db.getRecordEx(queryTable,
                                             cols,
                                             where=tableAccount['id'].eq(accountId))
        return accountRecord

    def makeQueryParts(self, accountId):
        tableAccountItem = self._db.table('Account_Item')
        tableEvent = self._db.table('Event')
        tableAction = self._db.table('Action')
        tableActionType = self._db.table('ActionType')

        tableVisit = self._db.table('Visit')
        tableEventType = self._db.table('EventType')
        tableEventGoal = self._db.table('rbEventGoal')
        tableEventResult = self._db.table('rbResult').alias('EventResult')
        tableEventTypePurpose = self._db.table('rbEventTypePurpose')
        tableLittleStranger = self._db.table('Event_LittleStranger')
        tableContractTariff = self._db.table('Contract_Tariff')
        tableEmergencyCall = self._db.table('EmergencyCall')
        tableEmergencyPlaceReceptionCall = self._db.table('rbEmergencyPlaceReceptionCall')

        tableClient = self._db.table('Client')
        tablePolicy = self._db.table('ClientPolicy')
        tablePolicyKind = self._db.table('rbPolicyKind')
        tableInsurer = self._db.table('Organisation').alias('Insurer')
        tableOrganisation = self._db.table('Organisation').alias('EmergencyOrganisation')

        tableServiceAidProfile = self._db.table('rbMedicalAidProfile').alias('ServiceAidProfile')
        tableServiceAidKind = self._db.table('rbMedicalAidKind').alias('ServiceAidKind')
        tableEventTypeAidProfile = self._db.table('rbEventProfile').alias('EventTypeAidProfile')
        tableEventTypeAidKind = self._db.table('rbMedicalAidKind').alias('EventTypeAidKind')
        tableEventAidUnit = self._db.table('rbMedicalAidUnit')
        tableEventPrimaryDiagnostic = self._db.table('Diagnostic').alias('EventDiagnostic')
        tableEventPrimaryDiagnosis = self._db.table('Diagnosis').alias('EventDiagnosis')
        tableDiagnosticResult = self._db.table('rbDiagnosticResult')
        tableMes = self._db.table('mes.MES')
        tableService = self._db.table('rbService')

        tableRefuseType = self._db.table('rbPayRefuseType')
        tableReferral = self._db.table('Referral')
        tableRelegateOrg = self._db.table('Organisation').alias('RelegateOrg')

        tableVisitService = tableService.alias('visitService')

        tableTooth = self._db.table(
            u'''
                SELECT
                    A.id AS action_id, API.value AS toothNumber
                FROM
                    Action A
                    INNER JOIN ActionProperty AP ON A.id = AP.action_id
                    INNER JOIN ActionPropertyType APT ON AP.type_id = APT.id
                    INNER JOIN ActionProperty_Integer API ON AP.id = API.id
                WHERE
                    APT.name = 'номер зуба'
            '''
        ).alias('Tooth')

        tableOperation = self._db.table(
            u'''
                SELECT
                    A.id AS action_id, IF(APS.value='да', 1, 0) AS isMainOperation
                FROM
                    Action A
                    INNER JOIN ActionProperty AP ON A.id = AP.action_id
                    INNER JOIN ActionPropertyType APT ON AP.type_id = APT.id
                    INNER JOIN ActionProperty_String APS ON AP.id = APS.id
                WHERE
                    APT.name = 'основная операция'
            '''
        ).alias('MainOperation')

        tableBedProfile = self._db.table(
            u'''
                SELECT
                    A.id AS action_id,
                    COALESCE(
                        rbHBP.code,
                        (
                            SELECT
                                rbHBP.code
                            FROM
                                Action A
                                INNER JOIN ActionType AT ON A.actionType_id = AT.id
                                INNER JOIN ActionProperty AP ON A.id = AP.action_id
                                INNER JOIN ActionPropertyType APT ON AP.type_id = APT.id
                                INNER JOIN ActionProperty_rbHospitalBedProfile APrbHBP ON APrbHBP.id = AP.id
                                INNER JOIN rbHospitalBedProfile rbHBP ON rbHBP.id = APrbHBP.value
                            WHERE
                                A.event_id = E.id
                                AND AT.flatCode LIKE 'moving%%'
                                AND APT.name = 'профиль койки'
                                AND APT.valueDomain = 'rbHospitalBedProfile'
                            ORDER BY
                                A.idx
                            LIMIT 1
                        )
                    ) AS hospitalBedCode
                FROM
                    Action A
                    INNER JOIN Event E ON A.event_id = E.id
                    LEFT JOIN ActionProperty AP ON A.id = AP.action_id
                    LEFT JOIN ActionPropertyType APT ON AP.type_id = APT.id AND APT.name = 'профиль койки' AND APT.valueDomain = 'rbHospitalBedProfile'
                    LEFT JOIN ActionProperty_rbHospitalBedProfile APrbHBP ON APrbHBP.id = AP.id
                    LEFT JOIN rbHospitalBedProfile rbHBP ON rbHBP.id = APrbHBP.value
                WHERE
                    AP.deleted = 0
                    AND APT.deleted = 0
                GROUP BY
                    action_id
                HAVING
                    hospitalBedCode is not null
            '''
        ).alias('BedProfile')

        tableIsStoma = self._db.table(
            u'''
                SELECT
                    Event.id,
                    COUNT(rbService.id) AS isStoma
                FROM
                    Event
                    LEFT JOIN Account_Item ON Event.id = Account_Item.event_id AND Account_Item.deleted = 0
                    LEFT JOIN rbService ON Account_Item.service_id = rbService.id AND rbService.code LIKE '63%'
                GROUP BY
                    Event.id
            '''
        ).alias('Stoma')

        queryTable = tableAccountItem.innerJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
        queryTable = queryTable.innerJoin(tableIsStoma, tableIsStoma['id'].eq(tableEvent['id']))
        queryTable = queryTable.leftJoin(tableEventGoal, tableEventGoal['id'].eq(tableEvent['goal_id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAccountItem['action_id']))
        queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.leftJoin(tableVisit, tableVisit['id'].eq(tableAccountItem['visit_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        queryTable = queryTable.leftJoin(tableEventResult, tableEventResult['id'].eq(tableEvent['result_id']))
        queryTable = queryTable.leftJoin(tableEventTypePurpose, tableEventTypePurpose['id'].eq(tableEventType['purpose_id']))
        queryTable = queryTable.leftJoin(tableContractTariff, tableContractTariff['id'].eq(tableAccountItem['tariff_id']))
        queryTable = queryTable.leftJoin(tableEventAidUnit, tableEventAidUnit['id'].eq(tableContractTariff['unit_id']))
        queryTable = queryTable.leftJoin(tableMes, tableMes['id'].eq(tableEvent['MES_id']))
        queryTable = queryTable.leftJoin(tableTooth, tableTooth['action_id'].eq(tableAction['id']))
        queryTable = queryTable.leftJoin(tableEmergencyCall, tableEmergencyCall['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.leftJoin(tableEmergencyPlaceReceptionCall, tableEmergencyPlaceReceptionCall['id'].eq(tableEmergencyCall['placeReceptionCall_id']))
        queryTable = queryTable.leftJoin(tableOperation, tableOperation['action_id'].eq(tableAction['id']))
        queryTable = queryTable.leftJoin(tableBedProfile, tableBedProfile['action_id'].eq(tableAction['id']))
        queryTable = queryTable.leftJoin(tableOrganisation, tableOrganisation['id'].eq(tableEvent['org_id']))

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
        queryTable = queryTable.leftJoin(tableReferral, tableEvent['referral_id'].eq(tableReferral['id']))
        queryTable = queryTable.leftJoin(tableRelegateOrg, tableRelegateOrg['id'].eq(tableReferral['relegateOrg_id']))

        queryTable = queryTable.leftJoin(tableVisitService, tableVisit['service_id'].eq(tableVisitService['id']))

        cols = [tableEvent['client_id'].alias('clientId'),
                tableEvent['id'].alias('eventId'),
                tableVisit['id'].alias('visitId'),
                tableAction['id'].alias('actionId'),
                tableService['id'].alias('serviceId'),
                tableAccountItem['id'].alias('accountItemId'),
                tableAccountItem['date'].alias('accountItemDate'),
                tableRefuseType['flatCode'].alias('accountItemRefuseCode'),
                tableRefuseType['rerun'],
                tableInsurer['infisCode'].alias('insurerInfis'),
                tableInsurer['OKATO'].alias('insurerOKATO'),
                '''DATE(IFNULL(Visit.date, Action.endDate))       AS serviceItemDate''',
                '''IF (Visit.date != '', 0, 1)                    AS serviceOrder''',
                tableEventType['id'].alias('eventTypeId'),

                # for addEventElement
                tableEventTypePurpose['federalCode'].alias('eventTypePurposeFedCode'),
                tableEventTypeAidKind['federalCode'].alias('eventTypeAidKindFedCode'),
                tableEvent['order'].alias('eventOrder'),
                tableEvent['setDate'].alias('eventSetDate'),
                tableEvent['execDate'].alias('eventExecDate'),
                tableEvent['hospParent'],
                tableEventPrimaryDiagnosis['MKB'].alias('eventPrimaryMKB'),
                tableEventResult['federalCode'].alias('eventResultFedCode'),
                tableDiagnosticResult['federalCode'].alias('eventPrimaryMKBResultFedCode'),
                tableEventAidUnit['federalCode'].alias('eventAidUnitFedCode'),
                tableClient['patrName'].alias('clientPatrName'),
                tableMes['code'].alias('mesCode'),
                tableEmergencyCall['id'].alias('emergencyCallId'),
                tableEmergencyCall['departureDate'].alias('emergencyDepartureDate'),
                tableEmergencyCall['arrivalDate'].alias('emergencyArrivalDate'),
                tableEmergencyPlaceReceptionCall['code'].alias('emergencyPlace'),
                tableOrganisation['miacCode'].alias('emergencyMiacCode'),
                tableIsStoma['isStoma'],
                tableEventGoal['code'].alias('eventGoalCode'),

                #for addServiceElement
                tableAction['org_id'].alias('actionOrgId'),
                tableActionType['code'].alias('actionTypeCode'),
                tableTooth['toothNumber'],
                tableOperation['isMainOperation'],
                tableBedProfile['hospitalBedCode'],
                tableEvent['org_id'].alias('eventOrgId'),
                tableEvent['execPerson_id'].alias('eventExecPersonId'),
                'IFNULL(%s, %s) AS actionPersonId' % (tableAction['person_id'],
                                                      tableAction['setPerson_id']),
                tableVisit['person_id'].alias('visitPersonId'),
                tableAction['begDate'].alias('actionBegDate'),
                tableAction['endDate'].alias('actionEndDate'),
                tableVisit['date'].alias('visitDate'),
                tableService['code'].alias('serviceCode'),
                tableAccountItem['amount'].alias('serviceAmount'),
                tableAccountItem['uet'].alias('serviceUET'),
                # tableContractTariff['price'].alias('servicePrice'),
                tableAccountItem['price'].alias('servicePrice'),
                tableAccountItem['sum'].alias('serviceSum'),
                tableAction['MKB'].alias('actionMKB'),
                tableVisit['MKB'].alias('visitMKB'),
                tableServiceAidProfile['federalCode'].alias('serviceAidProfileFedCode'),
                tableVisitService['code'].alias('visitServiceCode'),

                #for fillPatient
                '%s IS NOT NULL AS isLittleStranger' % tableLittleStranger['id'].name(),
                tableLittleStranger['id'].alias('littleStrangerId'),
                tablePolicyKind['federalCode'].alias('policyKindFedCode'),
                tablePolicy['serial'].alias('policySerial'),
                tablePolicy['number'].alias('policyNumber'),
                tableLittleStranger['sex'].alias('newbornSex'),
                tableLittleStranger['birthDate'].alias('newbornBirthDate'),
                tableLittleStranger['currentNumber'].alias('newbornNumber'),
                tableLittleStranger['birthWeight'].alias('newbornBirthWeight'),
                'age(%s, %s) as clientAge' % (tableClient['birthDate'], tableEvent['setDate']),
                tableReferral['number'].alias('referralNumber'),
                tableRelegateOrg['infisCode'].alias('relegateInfisCode'),
                ]

        cond = [
            tableAccountItem['master_id'].eq(accountId),
            tableAccountItem['deleted'].eq(0),
            self._db.joinOr([
                tableMes['code'].isNull(),
                self._db.joinAnd([tableMes['code'].notlike('1.%'), tableMes['code'].notlike('2.%')])
            ]),
            tableEvent['execDate'].ge(QtCore.QDate(2015, 12, 25))   # mdldml: новый регламент работает только для этих случаев
        ]

        queryTable, cols, cond = self.makeExtraQueryParts(queryTable, cols, cond)
        return queryTable, cols, cond

    def makeExtraQueryParts(self, queryTable, cols, cond):
        return queryTable, cols, cond

    def process(self, accountId):
        self.isTerminated = False
        self.phaseReset(17)

        accountRecord = self.getAccountRecord(accountId)

        queryTable, cols, cond = self.makeQueryParts(accountId)

        self.nextPhaseStep(u'Загрузка данных по счету')

        query = self._db.query(self._db.selectStmt(queryTable, cols, where=cond, order='Event.id, serviceItemDate, serviceOrder'))
        self.nextPhaseStep(u'Загрузка данных завершена')

        self.criticalErrors = []
        self.hDocuments.clear()
        self.lDocuments.clear()
        self.pDocuments.clear()
        # self.accCodeToAccountItemId.clear()
        self.lpuInfis = forceStringEx(accountRecord.value('lpuInfis'))
        entries = {}
        events = {}
        idCaseCounter = {}
        entryCounter = {}
        self.orgForDeferredFilling.clear()
        self.personSpecialityForDeferredFilling.clear()
        self.clientsForDeferredFilling.clear()
        self.firstVisitsForDeferredFilling.clear()
        self.socStatusForDeferredFilling.clear()
        self.mainOperationExported.clear()
        self.eventsForDeferredUpdating.clear()
        self.hospitalBedProfileCodesForDeferredFilling.clear()
        self.emergencyCallsForDeferredFilling.clear()
        self.edColForDeferredFilling.clear()
        self.profilForDeferredFilling.clear()
        eventsTotals = {}
        # eventRefuses = {}
        accountTotals = {}
        insurerOkato = {}
        self.veteranSocStatusTypeId = forceRef(self._db.translate('rbSocStatusType', 'code', '20', 'id'))
        self.nextPhase(query.size(), u'Обработка позиций счета')
        while query.next():
            record = query.record()
            if self.isTerminated:
                self.onTerminating()
                return False

            insurerInfis = forceStringEx(record.value('insurerInfis'))

            if not insurerInfis.startswith('85') or self.FLC:
                insurerInfis = self.fundCode
            # if insurerInfis and not insurerInfis.startswith(u'85'):
            #     self.nextPhaseStep()
            #     continue

            self.hDocuments.setdefault(insurerInfis, self.createHXMLDocument(insurerInfis, accountRecord))
            self.lDocuments.setdefault(insurerInfis, self.createLXMLDocument(insurerInfis, accountRecord))
            self.pDocuments.setdefault(insurerInfis, self.createPXMLDocument())
            hDoc, accountElement, headerElement = self.hDocuments[insurerInfis]

            insurerOkato.setdefault(insurerInfis, forceStringEx(record.value('insurerOKATO')))
            rootElement = CXMLHelper.getRootElement(hDoc)
            clientId = forceRef(record.value('clientId'))
            littleStrangerId = forceRef(record.value('littleStrangerId'))
            accCode = forceStringEx(accountElement.firstChildElement('CODE').text()) #????
            itemId = forceRef(record.value('accountItemId'))

            if not entries.has_key((insurerInfis, clientId, littleStrangerId)):
                entryCounter[insurerInfis] = entryCounter.setdefault(insurerInfis, 0) + 1
                entries[(insurerInfis, clientId, littleStrangerId)] = self.addEntryElement(rootElement, record, entryCounter[insurerInfis])

            entryElement, _ = entries[(insurerInfis, clientId, littleStrangerId)]

            eventId = forceRef(record.value('eventId'))

            if not events.has_key(eventId):
                idCaseCounter[insurerInfis] = idCaseCounter.setdefault(insurerInfis, 0) + 1
                events[eventId] = self.addEventElement(entryElement,
                                                       idCaseCounter[insurerInfis],
                                                       record)

            eventElement = events[eventId]

            self.addServiceElementProxy(eventElement, forceRef(record.value('accountItemId')), record)
            serviceSum = forceDouble(record.value('serviceSum'))
            accountItemRefuseCode = forceStringEx(record.value('accountItemRefuseCode'))
            # accountItemDate = forceDate(record.value('accountItemDate'))
            currEventTotals = eventsTotals.setdefault(eventId, [0.0, 0.0, 0.0, 0.0]) # [total, amount, uet, amount_kpg]
            currAccountTotals = accountTotals.setdefault(insurerInfis, [0.0]) # [total, payed, refused]
            currEventTotals[0] += round(serviceSum, 2)
            currAccountTotals[0] += round(serviceSum, 2)
            # if accountItemRefuseCode and not eventId in eventRefuses:
            #     eventRefuses[eventId] = accountItemRefuseCode
            # if accountItemDate:
            #     i = 2 if accountItemRefuseCode else 1
            #     currAccountTotals[i] += serviceSum
            #     currEventTotals[i] += serviceSum
            currEventTotals[1] += forceDouble(record.value('serviceAmount'))
            if forceBool(record.value('visitId')): # Основная информация хранится в Account_Item'е, соответствующем визиту.
                currEventTotals[2] += forceDouble(record.value('serviceUET'))
            if not (forceBool(record.value('visitId')) or forceBool(record.value('actionId'))):
                # Для ED_COL по КПГ важно только количество койко-дней, операции попадать не должны
                # daysLength = forceDouble(record.value('serviceAmount'))
                dateFrom = forceDate(record.value('eventSetDate'))
                dateTo = forceDate(record.value('eventExecDate'))
                eventTypePurposeFedCode = forceInt(record.value('eventTypePurposeFedCode'))
                daysLength = getEventLengthDays(dateFrom, dateTo, True, forceRef(record.value('eventTypeId')))
                # if eventTypePurposeFedCode == 2 and dateFrom != dateTo:
                #     daysLength += 1
                currEventTotals[3] += daysLength

            self.clientsForDeferredFilling.setdefault(insurerInfis, {}).setdefault(clientId, {}).setdefault(forceRef(record.value('littleStrangerId')),
                                                      (insurerInfis,
                                                       forceBool(record.value('isLittleStranger')),
                                                       forceInt(record.value('newbornSex')),
                                                       forceDate(record.value('newbornBirthDate')),
                                                       forceBool(record.value('hospParent'))
                                                       )
                                                      )

            self.nextPhaseStep()

        query = None    # Нам больше не нужен этот объект

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

            # mdldml: При выгрузке ФЛК не заполняем информацию о суммах
            exposedSumElement = accountElement.firstChildElement('SUMMAV')
            # payedSumElement = accountElement.firstChildElement('SUMMAP')
            # refusedSumElement = accountElement.firstChildElement('SANK_MEK')
            CXMLHelper.setValue(exposedSumElement, '%.2f' % (totals[0] if not self.FLC else 0.0))
            # CXMLHelper.setValue(payedSumElement, '%.2f' % (totals[1] + sums.get(insurerInfis, 0.0)))
            # CXMLHelper.setValue(refusedSumElement, '%.2f' % totals[2])
            self.nextPhaseStep()

        self.nextPhase(len(eventsTotals), u'Заполнение данных о стоимости счетов')
        for eventId, totals in eventsTotals.iteritems():
            if self.isTerminated:
                self.onTerminating()
                return False
            eventElement = events[eventId]
            totalElement = eventElement.firstChildElement('SUMV')
            # payedElement = eventElement.firstChildElement('SUMP')
            # refusedElement = eventElement.firstChildElement('SANK_IT')
            edColElement = eventElement.firstChildElement('ED_COL')
            edCol = 0.0
            if eventId in self.edColForDeferredFilling:
                edCol = self.edColForDeferredFilling[eventId]
            if not edCol:
                edCol = totals[2]   # Стоматология
            if not edCol:
                edCol = totals[3]   # КПГ (стационары)
            if not edCol:
                edCol = totals[1]
            CXMLHelper.setValue(edColElement, '%.2f' % edCol)
            CXMLHelper.setValue(totalElement, (totals[0] if not self.FLC else 0.0))
            # CXMLHelper.setValue(payedElement, totals[1])
            # CXMLHelper.setValue(refusedElement, totals[2])
            # refuseCode = eventRefuses.get(eventId)
            # if refuseCode:
            #     sank = CXMLHelper.addElement(eventElement, 'SANK', afterElem=['SANK_IT', 'SUMP', 'SUMV'])
            #     CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_CODE'),
            #                         1)
            #     CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_SUM'),
            #                         totals[2])
            #     CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_TIP'),
            #                         1)
            #     CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_OSN'),
            #                         refuseCode)
            #     CXMLHelper.setValue(CXMLHelper.addElement(sank, 'S_IST'),
            #                         1)

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

        if not self.isTerminated:
            self.fillPersonFullInfo()

        if not self.isTerminated:
            self.fillSocStatusData()

        if not self.isTerminated:
            self.fillHospitalBedProfiles()

        if not self.isTerminated:
            self.fillEmergencyInfo()
        if not self.isTerminated:
            self.fillProfiles()
        if not self.isTerminated:
            self.fillVidpom()

        if not self.isTerminated and not self.FLC:
            self.checkFLC(accountId)
        if not self.isTerminated:
            self.postprocessing()
        if not self.isTerminated:
            self.updateEvents()
        self.logger().info(u'Завершено')
        if self.isTerminated:
            self.onTerminating()
            return False
        return True

    def updateEvents(self):
        # хотим обновлять create/modify personId/datetime, не хотим думать,
        # поэтому используем наш слой абстракции и обновляем Event'ы по одному

        # UPD: добавил перестраховку на случай, если придется при импорте отказов
        # match'ить случаи по IDCASE
        self.nextPhase(len(self.eventsForDeferredUpdating), u'Обновление случаев в БД')
        tableEvent = self._db.table('Event')
        eventRecords = self._db.getRecordList(tableEvent, where=tableEvent['id'].inlist(self.eventsForDeferredUpdating))
        self._db.transaction()
        for eventRecord in eventRecords:
            if self.FLC:
                eventRecord.setValue('FLCStatus', toVariant(1))
                self._db.updateRecord(tableEvent, eventRecord)
            # oldNote = forceStringEx(eventRecord.value('note'))
            # if oldNote.split(';')[0].startswith('IDCASE'):
            #     oldNote = oldNote[(oldNote.index(';') + 1):]
            # oldNote = ('IDCASE: %s;' % self.eventsForDeferredUpdating[forceInt(eventRecord.value('id'))]) + oldNote
            # eventRecord.setValue('note', toVariant(oldNote))
            self.nextPhaseStep()
        self._db.commit()

    # mdldml: (tag, message, isCritical (prevent export if true; cut if false))
    # TODO: isCritical behaviour: to be implemented in future
    # TODO: make methods static
    # TODO: merge checkFLC and postprocessing into one method
    def _sluchFLCFields(self):
        return (
            ('PROFIL', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <PROFIL>.', True), # Выгрузка невозможна.'),
            ('ISHOD', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <ISHOD>.', True), # Выгрузка невозможна.'),
            ('RSLT', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <RSLT>.', True), # Выгрузка невозможна.'),
            ('IDSP', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <IDSP>.', True), # Выгрузка невозможна.'),
            ('PRVS', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <PRVS>.', True), # Выгрузка невозможна.'),
            ('IDDOKT', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <IDDOKT>.', True), # Выгрузка невозможна.'),
        )

    def _uslFLCFields(self):
        return (
            ('PROFIL', u'Ошибка ФЛК. Для услуги \'%s\' в случае с id = %s не удалось заполнить тэг <PROFIL>.', True), # Выгрузка невозможна.'),
            ('PRVS', u'Ошибка ФЛК. Для услуги \'%s\' в случае с id = %s не удалось заполнить тэг <PRVS>.', True), # Выгрузка невозможна.'),
            ('CODE_MD', u'Ошибка ФЛК. Для услуги \'%s\' в случае с id = %s не удалось заполнить тэг <CODE_MD>.', True), # Выгрузка невозможна.'),
        )

    def _pacientFLCFields(self):
        return (
            ('NPOLIS', u'Для пациента с id = %s не удалось заполнить тег <NPOLIS>. Данные не будут выгружены', False),
        )

    def postprocessing(self):
        for hDoc, _, _ in self.hDocuments.values():
            self.nextPhase(hDoc.elementsByTagName('ZAP').length(), u'Форматно-логический контроль')
            rootElement = CXMLHelper.getRootElement(hDoc)
            zapElement = rootElement.firstChildElement('ZAP')
            while not zapElement.isNull():
                entitySuccess = True
                pacient = zapElement.firstChildElement('PACIENT')
                idPac = forceStringEx(pacient.firstChildElement('ID_PAC').text())
                for checkElementName, message, isCritical in self._pacientFLCFields():
                    checkElement = pacient.firstChildElement(checkElementName)
                    if checkElement.isNull() or not forceStringEx(checkElement.text()):
                        self.logger().warning(message % idPac)
                        entitySuccess = False

                nextZap = zapElement.nextSiblingElement('ZAP')
                if not entitySuccess:
                    rootElement.removeChild(zapElement)
                zapElement = nextZap

    def checkFLC(self, accountId):
        success = True

        payStatusMask = self.getPayStatusMask(accountId)
        refuseId = forceRef(self._db.translate('rbPayRefuseType', 'code', '5.1.3.', 'id'))
        tblAccountItem = self._db.table('Account_Item')
        for hDoc, _, _ in self.hDocuments.values():
            self.nextPhase(hDoc.elementsByTagName('SLUCH').length(), u'Форматно-логический контроль')
            rootElement = CXMLHelper.getRootElement(hDoc)
            zapElement = rootElement.firstChildElement('ZAP')
            index = rootElement.elementsByTagName('ZAP').length() - 1
            while not zapElement.isNull():
                eventIdList = []
                entitySuccess = True
                sluch = zapElement.firstChildElement('SLUCH')
                while not sluch.isNull():
                    nhistory = forceStringEx(sluch.firstChildElement('NHISTORY').text())
                    eventIdList.append(nhistory)
                    hasECO = False
                    for checkElementName, message, isCritical in self._sluchFLCFields():
                        checkElement = sluch.firstChildElement(checkElementName)
                        if checkElement.isNull() or not forceStringEx(checkElement.text()):
                            self.logger().critical(message % nhistory)
                            success = False
                            entitySuccess = False

                    uslElement = sluch.firstChildElement('USL')
                    while not uslElement.isNull():
                        code_usl = forceStringEx(uslElement.firstChildElement('CODE_USL').text())
                        if code_usl in self.ecoKPGList:
                            hasECO = True
                        for checkElementName, message, isCritical in self._uslFLCFields():
                            checkElement = uslElement.firstChildElement(checkElementName)
                            if checkElement.isNull() or not forceStringEx(checkElement.text()):
                                self.logger().critical(message % (code_usl, nhistory))
                                success = False
                                entitySuccess = False
                        uslElement = uslElement.nextSiblingElement('USL')

                    if hasECO:
                        referralFields = (('NPR_MO', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <NPR_MO>.'),# Выгрузка невозможна.'),
                                          ('NPR_N', u'Ошибка ФЛК. Для случая с id = %s не удалось заполнить тэг <NPR_N>.'))# Выгрузка невозможна.'))
                        for checkElementName, message in referralFields:
                            checkElement = sluch.firstChildElement(checkElementName)
                            if checkElement.isNull() or not forceStringEx(checkElement.text()):
                                self.logger().critical(message % nhistory)
                                success = False
                                entitySuccess = False

                    sluch = sluch.nextSiblingElement('SLUCH')
                    self.nextPhaseStep()


                if not entitySuccess:
                    self._db.updateRecords(table=tblAccountItem,
                                           expr=[tblAccountItem['refuseType_id'].eq(refuseId),
                                                 tblAccountItem['number'].eq(u'Ошибка ФЛК'),
                                                 tblAccountItem['date'].eq(QtCore.QDate.currentDate())],
                                           where=[tblAccountItem['event_id'].inlist(eventIdList),
                                                  tblAccountItem['master_id'].eq(accountId)])
                    accountItems = self._db.getRecordList(tblAccountItem,
                                                          [tblAccountItem['event_id'],
                                                           tblAccountItem['visit_id'],
                                                           tblAccountItem['action_id']],
                                                          where=[tblAccountItem['event_id'].inlist(eventIdList),
                                                            tblAccountItem['master_id'].eq(accountId)])
                    for ai in accountItems:
                        updateDocsPayStatus(ai, payStatusMask, CPayStatus.refusedBits)
                    nextZap = zapElement.nextSiblingElement('ZAP')
                    rootElement.removeChild(zapElement)
                    zapElement = nextZap
                else:
                    zapElement = zapElement.nextSiblingElement('ZAP')
                index -= 1
        if not success:
            for key in self.hDocuments.keys():
                del self.hDocuments[key]
            for key in self.lDocuments.keys():
                del self.lDocuments[key]
        return success

        # if element.isNull() and isRequired:
        #     self.logger().warning(u'Ошибка формата файла. Ожидаемый узел: "%s" не был найден [%s:%s]' % (elementName, parentNode.lineNumber(), parentNode.columnNumber()))
        #     if isinstance(mekErrorList, list):
        #         mekErrorList.append((u'5.1.3',
        #                              u'Неполное заполнение полей реестра счетов',
        #                              parentNode.nodeName(),
        #                              elementName))

    def fillVidpom(self):
        self.nextPhase(1, u'Загрузка данных о видах мед. помощи')

        tableEvent = self._db.table('Event')
        stmt = u'''
            SELECT
                Person.id AS personId,
                rbService_Profile.master_id AS serviceId,
                rbMedicalAidKind.federalCode AS kindCode
            FROM
                Person
                INNER JOIN rbService_Profile ON rbService_Profile.speciality_id = Person.speciality_id
                INNER JOIN rbMedicalAidKind ON rbService_Profile.medicalAidKind_id = rbMedicalAidKind.id
            WHERE
                %s
        '''
        cond = u'(Person.id, rbService_Profile.master_id) IN (%s)' % u', '.join([str(key) for key in self.profilForDeferredFilling.keys()]) if self.profilForDeferredFilling else u'0'
        query = self._db.query(stmt % cond)
        while query.next():
            record = query.record()
            personId = forceString(record.value('personId'))
            serviceId = forceString(record.value('serviceId'))
            kindCode = forceString(record.value('kindCode'))
            if kindCode:
                vidpomList = self.kindForDeferredFilling[(personId, serviceId)]
                for vidpomTag in vidpomList:
                    CXMLHelper.setValue(vidpomTag, kindCode)

    def fillProfiles(self):
        self.nextPhase(1, u'Загрузка данных о профилях мед. помощи')

        tableEvent = self._db.table('Event')
        stmt = u'''
            SELECT
                Person.id AS personId,
                rbService_Profile.master_id AS serviceId,
                rbMedicalAidProfile.federalCode AS profileCode
            FROM
                Person
                INNER JOIN rbService_Profile ON rbService_Profile.speciality_id = Person.speciality_id
                INNER JOIN rbMedicalAidProfile ON rbService_Profile.medicalAidProfile_id = rbMedicalAidProfile.id
            WHERE
                %s
        '''
        cond = u'(Person.id, rbService_Profile.master_id) IN (%s)' % u', '.join([str(key) for key in self.profilForDeferredFilling.keys()]) if self.profilForDeferredFilling else u'0'
        query = self._db.query(stmt % cond)
        while query.next():
            record = query.record()
            personId = forceString(record.value('personId'))
            serviceId = forceString(record.value('serviceId'))
            profileCode = forceString(record.value('profileCode'))
            if profileCode:
                profilList = self.profilForDeferredFilling[(personId, serviceId)]
                for profilTag in profilList:
                    CXMLHelper.setValue(profilTag, profileCode)

    def getPayStatusMask(self, accountId):
        result = None
        tblAccount = self._db.table('Account')
        tblContract = self._db.table('Contract')
        tbl = tblAccount.join(tblContract, tblContract['id'].eq(tblAccount['contract_id']))
        record = self._db.getRecordEx(tbl, tblContract['finance_id'], tblAccount['id'].eq(accountId))
        if record:
            result = getPayStatusMask(forceRef(record.value('finance_id')))
        return result

    def save(self, outDir):
        self.phaseReset(2)
        outDir = forceStringEx(outDir)
        self.nextPhase(len(self.hDocuments), u'Сохранение файлов H')
        for insurerInfis in self.hDocuments.keys():
            doc, _, headerElement = self.hDocuments[insurerInfis]
            lDoc = self.lDocuments[insurerInfis]
            fileName = forceStringEx(headerElement.firstChildElement('FILENAME').text())
            lHeaderElement = CXMLHelper.getRootElement(lDoc).firstChildElement('ZGLV')
            lFileName = forceStringEx(lHeaderElement.firstChildElement('FILENAME').text())
            # fullFilename = os.path.join(outDir, u'%s.xml' % fileName)
            zipFileName = u'%s.zip' % fileName
            zipFilePath = os.path.join(outDir, zipFileName)
            try:
                hTmp = QtCore.QTemporaryFile(u'%s.xml' % fileName)
                lTmp = QtCore.QTemporaryFile(u'%s.xml' % lFileName)
                if not hTmp.open(QtCore.QFile.WriteOnly):
                    self.logger().critical(u'Не удалось открыть временный файл для записи')
                    break
                if not lTmp.open(QtCore.QFile.WriteOnly):
                    self.logger().critical(u'Не удалось открыть временный файл для записи')
                    break
                doc.save(QtCore.QTextStream(hTmp), 4, QtXml.QDomNode.EncodingFromDocument)
                lDoc.save(QtCore.QTextStream(lTmp), 4, QtXml.QDomNode.EncodingFromDocument)
                hTmp.close()
                lTmp.close()

                zf = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
                # body = codecs.encode(forceStringEx(doc.toString(4)), self.encoding)
                # zf.writestr(u'%s.xml' % fileName, body)
                zf.write(forceString(QtCore.QFileInfo(hTmp).absoluteFilePath()), u'%s.xml' % fileName)
                zf.write(forceString(QtCore.QFileInfo(lTmp).absoluteFilePath()), u'%s.xml' % lFileName)
                self.logger().info(u'Создан файл: %s' % zipFileName)
                zf.close()
                self.hDocuments.pop(insurerInfis)
                self.lDocuments.pop(insurerInfis)
            except Exception, e:
                QtGui.qApp.logCurrentException()
                self.logger().critical(u'Не удалось сохранить файл %s' % zipFileName)

        # self.nextPhase(len(self.lDocuments), u'Сохранение файлов L')
        # for insurerInfis in self.lDocuments.keys():
            # doc = self.lDocuments[insurerInfis]
            # rootElement = CXMLHelper.getRootElement(doc)
            # headerElement = rootElement.firstChildElement('ZGLV')
            # fileName = forceStringEx(headerElement.firstChildElement('FILENAME').text())
            # zipFileName = u'%s.zip' % fileName
            # zipFilePath = os.path.join(outDir, zipFileName)
            # try:
            #     lTmp = QtCore.QTemporaryFile(u'%s.xml' % fileName)
            #     if not lTmp.open(QtCore.QFile.WriteOnly):
            #         self.logger().critical(u'Не удалось открыть временный файл для записи')
            #         break
            #     doc.save(QtCore.QTextStream(lTmp), 4, QtXml.QDomNode.EncodingFromDocument)
            #     lTmp.close()
            #     zf = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
            #     # body = codecs.encode(forceStringEx(doc.toString(4)), self.encoding)
            #     # zf.writestr(u'%s.xml' % fileName, body)
            #     zf.write(QtCore.QFileInfo(lTmp).absoluteFilePath(), u'%s.xml' % fileName)
            #     self.logger().info(u'Создан файл: %s' % zipFileName)
            #     zf.close()
            # except Exception, e:
            #     self.logger().critical(u'Не удалось сохранить файл %s' % zipFileName)

        self.nextPhase(len(self.pDocuments), u'Сохранение файлов P')
        for insurerInfis in self.pDocuments.keys():
            doc = self.pDocuments[insurerInfis]
            # rootElement = CXMLHelper.getRootElement(doc)
            # headerElement = rootElement.firstChildElement('ZGLV')
            # fileName = forceStringEx(headerElement.firstChildElement('FILENAME').text())
            zipFileName = u'PERS_%s.zip' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz')) # % fileName
            zipFilePath = os.path.join(outDir, zipFileName)
            try:
                lTmp = QtCore.QTemporaryFile(u'PERS_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz')))# % fileName)
                if not lTmp.open(QtCore.QFile.WriteOnly):
                    self.logger().critical(u'Не удалось открыть временный файл для записи')
                    break
                doc.save(QtCore.QTextStream(lTmp), 4, QtXml.QDomNode.EncodingFromDocument)
                lTmp.close()
                zf = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
                # body = codecs.encode(forceStringEx(doc.toString(4)), self.encoding)
                # zf.writestr(u'%s.xml' % fileName, body)
                zf.write(QtCore.QFileInfo(lTmp).absoluteFilePath(), u'PERS_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz')))# % fileName)
                self.logger().info(u'Создан файл: %s' % zipFileName)
                zf.close()
                self.pDocuments.pop(insurerInfis)
            except Exception, e:
                self.logger().critical(u'Не удалось сохранить файл %s' % zipFileName)


class CExportR85HTTFEngine(CExportR85TFEngine):
    fileNamePrefix = 'T'
    def makeExtraQueryParts(self, queryTable, cols, cond):
        tableHMPKind = self._db.table('rbHighTechCureKind')
        tableHMPMethod = self._db.table('rbHighTechCureMethod')
        tableEvent = self._db.table('Event')
        tableContractTariff = self._db.table('Contract_Tariff')
        queryTable = queryTable.innerJoin(tableHMPKind, tableEvent['hmpKind_id'].eq(tableHMPKind['id']))
        queryTable = queryTable.innerJoin(tableHMPMethod, tableEvent['hmpMethod_id'].eq(tableHMPMethod['id']))

        cols.extend([tableHMPKind['code'].alias('hmpKindCode'),
                     tableHMPMethod['code'].alias('hmpMethodCode'),
                     tableContractTariff['tariffType'],         # Для исключения услуги ВМП из тегов USL
                     ])

        return queryTable, cols, cond

    def checkServiceElement(self, record):
        if forceInt(record.value('tariffType')) == CTariff.ttEventByHTG:
            return False
        return True

    def postProcessEventElement(self, eventElement, record):
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VID_HMP', afterElem='FOR_POM'),
                            forceStringEx(record.value('hmpKindCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'METOD_HMP', afterElem='VID_HMP'),
                            forceStringEx(record.value('hmpMethodCode')))

        idspElement = eventElement.firstChildElement('IDSP')
        CXMLHelper.setValue(idspElement, 13)
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NPR_MO'),
        #                     forceStringEx(record.value('relegateInfisCode')))
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NPR_N'),
        #                     forceStringEx(record.value('referralNumber')))
        # referralNumber = forceStringEx(record.value('referralNumber'))
        # if referralNumber:
        #     CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'COMENTSL'),
        #                     u'refNumber:%s' % referralNumber)

    def _sluchFLCFields(self):
        fields = super(CExportR85HTTFEngine, self)._sluchFLCFields()
        return fields + (('VID_HMP', u'Для случая с id = %s не удалось заполнить тэг <VID_HMP>. Выгрузка невозможна.'),
               ('METOD_HMP', u'Для случая с id = %s не удалось заполнить тэг <METOD_HMP>. Выгрузка невозможна.'),
               ('NPR_MO', u'Для случая с id = %s не удалось заполнить тэг <NPR_MO>. Выгрузка невозможна.'),
               ('NPR_N', u'Для случая с id = %s не удалось заполнить тэг <NPR_N>. Выгрузка невозможна.'),
               )

class CExportDialog(QtGui.QDialog):
    InitState = 0
    ExportState = 1
    SaveState = 2


    def __init__(self, db, accountId, parent=None, isHighTech=False):
        super(CExportDialog, self).__init__(parent=parent)
        self._db = db
        self._accountId = accountId
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        engine = CExportR85HTTFEngine if isHighTech else CExportR85TFEngine
        self._engine = engine(db, progressInformer=self._pi)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._currentState = self.InitState
        self._isHighTech = isHighTech

        self.setupUi()

        self.onStateChanged()

    def setParams(self, params):
        if isinstance(params, dict):
            outDir = forceStringEx(getPref(params, 'outDir', u''))
            if os.path.isdir(outDir):
                self.edtSaveDir.setText(outDir)
            # accNumber = forceInt(getPref(params, 'accNumber', 0)) + 1
            # self.spbAccountNumber.setValue(accNumber)

    def params(self):
        params = {}
        setPref(params, 'outDir', forceStringEx(self.edtSaveDir.text()))
        # setPref(params, 'accNumber', self.spbAccountNumber.value())
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
        # self.gbInit.setEnabled(self.currentState == self.InitState)
        self.gbExport.setEnabled(self.currentState == self.ExportState)
        self.gbSave.setEnabled(self.currentState == self.SaveState)
        self.btnSave.setEnabled(bool(self._engine.hDocuments or self._engine.lDocuments))
        QtCore.QCoreApplication.processEvents()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        # self.gbInit = QtGui.QGroupBox()
        # gbLayout = QtGui.QVBoxLayout()
        # numLayout = QtGui.QHBoxLayout()
        # self.lblAccountNumber = QtGui.QLabel()
        # numLayout.addWidget(self.lblAccountNumber)
        # self.spbAccountNumber = QtGui.QSpinBox()
        # self.spbAccountNumber.setRange(1, 999)
        # numLayout.addWidget(self.spbAccountNumber)
        # gbLayout.addLayout(numLayout)
        # sums = QtGui.QHBoxLayout()
        # sum1 = QtGui.QVBoxLayout()
        # self.lbl85001 = QtGui.QLabel()
        # self.lbl85001.setAlignment(QtCore.Qt.AlignCenter)
        # sum1.addWidget(self.lbl85001)
        # self.edt85001 = QtGui.QLineEdit()
        # sum1.addWidget(self.edt85001)
        # sums.addLayout(sum1)
        # sum2 = QtGui.QVBoxLayout()
        # self.lbl85002 = QtGui.QLabel()
        # self.lbl85002.setAlignment(QtCore.Qt.AlignCenter)
        # sum2.addWidget(self.lbl85002)
        # self.edt85002 = QtGui.QLineEdit()
        # sum2.addWidget(self.edt85002)
        # sums.addLayout(sum2)
        # sum3 = QtGui.QVBoxLayout()
        # self.lbl85003 = QtGui.QLabel()
        # self.lbl85003.setAlignment(QtCore.Qt.AlignCenter)
        # sum3.addWidget(self.lbl85003)
        # self.edt85003 = QtGui.QLineEdit()
        # sum3.addWidget(self.edt85003)
        # sums.addLayout(sum3)
        # gbLayout.addLayout(sums)
        # self.gbInit.setLayout(gbLayout)
        # layout.addWidget(self.gbInit)

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
        title = u'Экспорт. Крым. Фонд. ВМП.' if self._isHighTech else u'Экспорт. Крым. Фонд.'
        self.setWindowTitle(forceTr(title, context))
        # self.gbInit.setTitle(forceTr(u'Параметры экспорта', context))
        # self.lblAccountNumber.setText(forceTr(u'Номер реестра', context))
        # self.lbl85001.setText(forceTr(u'85001', context))
        # self.lbl85002.setText(forceTr(u'85002', context))
        # self.lbl85003.setText(forceTr(u'85003', context))

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
                # sums = {'85001': forceDouble(self.edt85001.text()),
                #         '85002': forceDouble(self.edt85002.text()),
                #         '85003': forceDouble(self.edt85003.text())}
                result = self._engine.process(self._accountId)
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
        return not (self._engine.hDocuments or self._engine.lDocuments) or \
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