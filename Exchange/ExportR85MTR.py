# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 26/03/15

@author: atronah
"""
import codecs
import logging
import os

from PyQt4 import QtCore, QtGui
import re
from Accounting.Utils import getContractInfo
from library.ProgressBar import CProgressBar

from library.ProgressInformer import CProgressInformer
from library.Utils import getClassName, forceStringEx, formatSNILS, forceInt, forceDate, forceTr, \
    CLogHandler, forceDouble, forceRef, forceBool, unformatSNILS, getPref, setPref, toVariant
from library.XML.XMLHelper import CXMLHelper
from library.database import connectDataBaseByInfo, CDatabase


def exportR85MTR(widget, accountId):
    exportWindow = CExportDialog(QtGui.qApp.db, accountId, widget)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), {})
    exportWindow.setParams(params)
    exportWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), exportWindow.params())

def importR85MTR(widget, orgId):
    importWindow = CImportDialog(QtGui.qApp.db, orgId)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), {})
    importWindow.setParams(params)
    importWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), importWindow.params())

# class CIncrementerFactory(object):
#     def __init__(self, startValue = 0):
#         self._currentValue = startValue
#
#
#     def reset(self, startValue):
#         self._currentValue = startValue
#
#
#     @property
#     def value(self):
#         self._currentValue += 1
#         return self._currentValue - 1


class CExchangeEngine(object):
    encoding = u'utf-8'

    PrimaryMKBTypeCode = 2
    SecondaryMKBTypeCode = 9
    ComplicatedMKBTypeCode = 3

    defaultDateFormat = 'yyyy-MM-dd'

    dummy = u'#' * 32
    dummyN = 0
    dummyD = QtCore.QDate(0, 0, 0)



    def __init__(self, progressInformer = None):
        self._progressInformer = progressInformer if isinstance(progressInformer, CProgressInformer) \
                                                  else CProgressInformer(processEventsFlag=None)
        self._logger = logging.getLogger(name=getClassName(self))
        self._logger.setLevel(logging.NOTSET)

        self.totalPhases = 0
        self.currentPhase = 0

        self.isAbort = False


    def logger(self):
        return self._logger


    def setProgressInformer(self, progressInformer):
        if isinstance(progressInformer, CProgressInformer):
            progressInformer.syncWithOther(self._progressInformer)
            self._progressInformer = progressInformer


    def progressInformer(self):
        return self._progressInformer



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


    def abort(self):
        self.isAbort = True


    def onAborted(self):
        self.logger().info(u'Прервано')
        self._progressInformer.reset(0, u'Прервано')


class CExchangeR85Engine(CExchangeEngine):
    encoding = u'windows-1251'
    version = u'2.1'


    @staticmethod
    def formatOKATO(OKATO, length=5):
        return forceStringEx(OKATO)[:length].ljust(length, '0')


class CExportR85MTREngine(CExchangeR85Engine):


    counterCode = 'mtrCode'

    def __init__(self, db, progressInformer = None):
        super(CExportR85MTREngine, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None

        self.orgForDeferredFilling = {}
        self.personSpecialityForDeferredFilling = {}
        self.accCodeToAccountItemId = {}
        self.documents = {}
        self.fileNameParts = {}

        self._counterId = None


#----- XML struct makers and fillers -----
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
                newRecord.setValue('name', QtCore.QVariant(u'Порядковый номер счета для выгрузки МежТер Крыма'))
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


    def addHeaderElement(self, rootElement, sourceOKATO, destOKATO):
        header = CXMLHelper.addElement(rootElement, 'ZGLV')
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'VERSION'),
                            self.version[:5])
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'DATA'),
                            QtCore.QDate.currentDate().toString(self.defaultDateFormat))


        #TODO: atronah: сомневаюсь, что верно, ибо ОКАТО организации более конкретно, нежели ОКАТО территории страхования
        #TODO: atronah: ОКАТО ЛПУ или ТФОМСА?
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'C_OKATO1'), # Код ОКАТО территории, выставившей счет (текущий фонд)
                            self.formatOKATO(sourceOKATO))
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'OKATO_OMS'), # Код ОКАТО территории страхования по ОМС (территория, в которую выставляется счет)
                            self.formatOKATO(destOKATO))
        return header


    def addAccountElement(self, rootElement, record, accCode = None):
        """
        Добавляет узел "SCHET"

        :param rootElement:
        :param record: запись базы данных, из которой будут браться данные для заполнения.
            Ожидается наличие следующих полей:
                * **date** (Account.date)
                * **number** (Account.number)
                * **exposeDate** (Account.exposeDate)
        :param accCode: код, полученный из элемента счета
        :return:
        """
        account = CXMLHelper.addElement(rootElement, 'SCHET')

        accDate = forceDate(record.value('settleDate'))
        accCode = forceStringEx(accCode if accCode else self.getCounterValue())


        CXMLHelper.setValue(CXMLHelper.addElement(account, 'CODE'),
                            accCode[-8:])
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'YEAR'),
                            accDate.year())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'MONTH'),
                            accDate.month())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'NSCHET'),
                            forceStringEx(record.value('number'))[:15])
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'DSCHET'),
                            forceDate(record.value('exposeDate')).toString(self.defaultDateFormat))
        CXMLHelper.addElement(account, 'SUMMAV')
        # if False:
        #     CXMLHelper.setValue(CXMLHelper.addElement(account, 'COMENTS'),
        #                         self.dummy[:250])
        CXMLHelper.addElement(account, 'SUMMAP')
        # if False:
        #     CXMLHelper.setValue(CXMLHelper.addElement(account, 'SANK_MEK'),
        #                         '%.2f' % self.dummyN)
        # if False:
        #     CXMLHelper.setValue(CXMLHelper.addElement(account, 'SANK_MEE'),
        #                         '%.2f' % self.dummyN)
        # if False:
        #     CXMLHelper.setValue(CXMLHelper.addElement(account, 'SANK_EKMP'),
        #                         '%.2f' % self.dummyN)
        return account


    def addEntryElement(self, rootElement, record, entryNumber):
        entryElement = CXMLHelper.addElement(rootElement, 'ZAP')

        CXMLHelper.setValue(CXMLHelper.addElement(entryElement, 'N_ZAP'),
                            entryNumber)
        patientElement = CXMLHelper.addElement(entryElement, 'PACIENT')
        self.fillPacient(patientElement, record)
        return entryElement, patientElement


    def fillPacient(self, patientElement, record):
        """

        :param patientElement:
        :param record:
            Ожидается наличие следующих полей:
            * **policyKindCode** - rbPolicyKind.code
            * **policySerial** - ClientPolicy.serial
            * **policyNumber** - ClientPolicy.number
            * **isLittleStranger** - Event.littleStranger_id IS NOT NULL
            * **clientLastName** - Client.lastName
            * **clientFirstName** - Client.firstName
            * **clientPatrName** - Client.patrName
            * **clientSex** - Client.sex
            * **clientBirthDate** - Client.birthDate
            * **strangerSex** - Event_LittleStranger.sex
            * **strangerBirthdate** - Event_LittleStranger.sex
            * **clientDocType** - rbDocumentType.code
            * **clientDocSerial** - ClientDocument.serial
            * **clientDocNumber** - ClientDocument.number
            * **clientSNILS** - Client.SNILS
        """
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'VPOLIS'),
                            forceInt(record.value('policyKindCode')))

        policySerial = forceStringEx(record.value('policySerial'))
        policyNumber = forceStringEx(record.value('policyNumber'))
        isUnified = policySerial.lower() == u'еп'
        if not isUnified:
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SPOLIS'),
                                forceStringEx(record.value('policySerial'))[:10])
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'NPOLIS'),
                            policyNumber[:20])


        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'ENP'),
                            policyNumber[:16] if isUnified else u'')

        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'ST_OKATO'),
        #                     forceStringEx(record.value('policyOriginOKATO'))[:5])

        isLittleStranger = forceBool(record.value('isLittleStranger'))
        reliability = []
        for elemName, fieldName, reliabilityCode in [('FAM', 'clientLastName', 3),
                                                     ('IM', 'clientFirstName', 2),
                                                     ('OT', 'clientPatrName', 1)]:
            value = forceStringEx(record.value(fieldName)) if not isLittleStranger else u''
            if value:
                CXMLHelper.setValue(CXMLHelper.addElement(patientElement, elemName),
                                    value[:40])
            else:
                reliability.append(reliabilityCode)

        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'W'),
                            forceInt(record.value('clientSex')) if not isLittleStranger
                                                                else forceInt(record.value('strangerSex')))
        birthDate = forceDate(record.value('clientBirthdate')) if not isLittleStranger else forceInt(record.value('strangerBirthdate'))
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'DR'),
                            birthDate.toString(self.defaultDateFormat) if not birthDate.isNull()
                                                                          else '01')
        for reliabilityCode in reliability:
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'DOST'),
                                reliabilityCode)

        if isLittleStranger:
            reliability = []
            for elemName, fieldName, reliabilityCode in [('FAM_P', 'clientLastName', 3),
                                                         ('IM_P', 'clientFirstName', 2),
                                                         ('OT_P', 'clientPatrName', 1)]:
                value = forceStringEx(record.value(fieldName))
                if value:
                    CXMLHelper.setValue(CXMLHelper.addElement(patientElement, elemName),
                                        value[:40])
                else:
                    reliability.append(reliabilityCode)
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'W_P'),
                            forceInt(record.value('clientSex')))
            birthDate = forceDate(record.value('clientBirthdate'))
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'DR_P'),
                                birthDate.toString(self.defaultDateFormat) if not birthDate.isNull()
                                                                           else '01')
            for reliabilityCode in reliability:
                CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'DOST_P'),
                                    reliabilityCode)

        birthPlace = forceStringEx(record.value('birthPlace')) if not isLittleStranger else None
        if birthPlace:
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'MR'),
                                birthPlace[:100])

        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'DOCTYPE'),
                            forceStringEx(record.value('clientDocType'))[:2])
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'DOCSER'),
                            forceStringEx(record.value('clientDocSerial'))[:10])
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'DOCNUM'),
                            forceStringEx(record.value('clientDocNumber'))[:20])
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SNILS'),
                            formatSNILS(unformatSNILS(record.value('clientSNILS')))[:14])
        OKATO = forceStringEx(record.value('regAddressOKATO'))

        #TODO: atronah: Как определять признак новорожденного? По наличию пометки события "Признак новорожденного" или по возрасту = 0?
        #TODO: atronah: откуда брать данные о представителе новорожденного? (В логике с признаком новорожденного из события пациент и есть представитель, но тогда нет данных о ребенке, кроме веса и даты рождения)
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'NOVOR'),
                            1 if isLittleStranger else 0)

        # if isLittleStranger:
        #     CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'VNOV_D'),
        #                         self.dummyN)
        # CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'COMENTP'),
        #                     self.dummy[:250)





    def addServiceElement(self, eventElement, idServ, record):
        """

        :param eventElement:
        :param idServ:
        :param record:
            Ожидается наличие следующих полей:
            * **lpuInfis** - Organisation.infisCode
            * **serviceAidProfileCode** - rbMedicalAidProfile.code <- rbService.medicalAidProfile_id <- Account_Item.service_id
            * **serviceAidKindCode** - rbMedicalAidKind.code <- rbService.medicalAidKind_id
            * **** -
            * **** -
            * ***
        :return:
        """

        serviceElement = CXMLHelper.addElement(eventElement, 'USL', afterElem=['USL', 'SANK', 'SANK_IT', 'SUMP'])

        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'IDSERV'),
                            forceStringEx(idServ)[:36])
        #atronah: "LPU" заполняется позже, отдельным запросом
        #atronah: предполагается, что место проведение Visit'а совпадает с местом Event'a (иначе пришлось бы джойнить врача из Visit и брать его организацию)
        serviceOrgId = forceRef(record.value('actionOrgId')) \
                       or forceRef(record.value('eventOrgId'))
        self.orgForDeferredFilling.setdefault(serviceOrgId,
            []).append(CXMLHelper.addElement(serviceElement, 'LPU'))
        # CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'LPU'),
        #                     forceStringEx(record.value('lpuInfis'))[:6])
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'PROFIL'),
                            forceInt(record.value('serviceAidProfileCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'VID_VME'),
                            forceStringEx(record.value('serviceAidKindCode'))[:15])
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'DET'),
                            1 if forceInt(record.value('clientAge')) < 18 else 0)
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
            #Получение диагноза из события
            mkb = forceStringEx(eventElement.firstChildElement('DS1').text())
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'DS'),
                            mkb[:10])
        #atronah: для счета по событию тоже имя из rbService?
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'USL'),
                            forceStringEx(record.value('serviceName'))[:254])
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'KOL_USL'),
                            '%.2f' % forceDouble(record.value('serviceAmount')))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'TARIF'),
                            '%.2f' % forceDouble(record.value('servicePrice')))
        CXMLHelper.setValue(CXMLHelper.addElement(serviceElement, 'SUMV_USL'),
                            '%.2f' % forceDouble(record.value('serviceSum')))
        #atronah: "PRVS" заполняется позже, отдельным запросом
        personId = forceRef(record.value('visitPersonId')) \
                   or forceRef(record.value('actionPersonId')) \
                   or forceRef(record.value('eventExecPersonId'))
        self.personSpecialityForDeferredFilling.setdefault(personId,
            []).append(CXMLHelper.addElement(serviceElement, 'PRVS'))
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'PRVS'),
        #                     forceInt(record.value('serviceExecPersonSpecialityCode')))
        return serviceElement


    def addEventElement(self, entryElement, idCase, record):
        eventElement = CXMLHelper.addElement(entryElement, 'SLUCH')

        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDCASE'),
                            idCase)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'USL_OK'),
                            forceInt(record.value('eventTypePurposeCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VIDPOM'),
                            forceInt(record.value('eventTypeAidKindCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'FOR_POM'),
                            #Конвертирование в соответствии со справочником V014 (формы оказания мед.помощи) от 01.01.2013
                            {1: 3, # плановая
                             2: 1, # экстренная
                             6: 2  # неотложная
                             }.get(forceInt(record.value('eventOrder')), 3))
        hmpKindCode = forceStringEx(record.value('eventHMPKindCode'))
        if hmpKindCode:
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VID_HMP'),
                                hmpKindCode[:9])
        hmpMethod = forceStringEx(record.value('eventHMPMethodCode'))
        if hmpMethod:
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'METOD_HMP'),
                                hmpMethod)

        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'EXTR'),
        #                     self.dummy)
        # Заполняем только, если круглосуточный стационар
        aidType = forceInt(record.value('eventTypeAidTypeCode'))
        if aidType in (1, 2, 3):
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'EXTR'),
                                1)
        #atronah: "LPU" заполняться будет позже отдельным запросом
        self.orgForDeferredFilling.setdefault(forceRef(record.value('eventOrgId')),
            []).append(CXMLHelper.addElement(eventElement, 'LPU'))

        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'LPU'),
        #                     forceStringEx(record.value('lpuInfis'))[:6])
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'PROFIL'),
                            forceInt(record.value('serviceAidProfileCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DET'),
                            1 if forceInt(record.value('clientAge')) < 18 else 0)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NHISTORY'),
                            forceStringEx(record.value('eventId'))[:50])
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_1'),
                            forceDate(record.value('eventSetDate')).toString(self.defaultDateFormat))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DATE_2'),
                            forceDate(record.value('eventExecDate')).toString(self.defaultDateFormat))
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DS0'),
        #                     forceStringEx(record.value('eventInitialMKB'))[:10])
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'DS1'),
                            forceStringEx(record.value('eventPrimaryMKB'))[:10])
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'RSLT'),
                            forceInt(record.value('eventResultCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'ISHOD'),
                            forceInt(record.value('eventPrimaryMKBResultCode')))
        #atronah: "PRVS" будет заполнен позже, отдельным запросом
        personId = forceRef(record.value('eventExecPersonId'))
        self.personSpecialityForDeferredFilling.setdefault(personId,
            []).append(CXMLHelper.addElement(eventElement, 'PRVS'))
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'PRVS'),
        #                     forceInt(record.value('setPersonSpecialityCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'VERS_SPEC'),
                             'V015')
        #atronah: данное поле (если брать из Account_item.unit_id заполняется несколько раз для одного события и вероятно оно должно быть согласовано с полями TARIF, ED_COL, SUMV, SUMP, что пока не так.
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDSP'),
                            forceInt(record.value('eventAidUnitCode')))

        #atronah: принято решение, что для случая кол-во всегда 1, а цена и сумма равны суммарной стоимости всех услуг
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'ED_COL'),
                            '%.2f' % 1.0)
        CXMLHelper.addElement(eventElement, 'TARIF')
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'TARIF'),
        #                     '%.2f' % price)
        # assert round(total, 2) == round(amount * price, 2)
        CXMLHelper.addElement(eventElement, 'SUMV')
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'SUMV'),
        #                     '%.2f' % total)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'OPLATA'),
                            1) # 0 - не принято решение об оплате, 1 - полная оплата, 2 - полный отказ, 3 - частичный отказ
        CXMLHelper.addElement(eventElement, 'SUMP')
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'SUMP'),
        #                     '%.2f' % total)
        # CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'SANK_IT'),
        #                     '%.2f' % self.dummyN)
        return eventElement


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
                                                   tableDiagnosis['deleted'].eq(0)]
                                            )
        self.nextPhase(len(recordList), u'Обработка данных по доп. диагнозам')
        for record in recordList:
            if self.isAbort:
                self.onAborted()
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
                                forceStringEx(record.value('MKB')))
            self.nextPhaseStep()


    def fillAddressess(self, entries, clientAddressIdList):
        self.nextPhase(1, u'Загрузка данных по адресам пациентов')
        tableClientAddress = self._db.table('ClientAddress')
        tableAddress = self._db.table('Address')
        tableHouse = self._db.table('AddressHouse')
        tableKladr = self._db.table('kladr.KLADR')

        queryTable = tableClientAddress.innerJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
        queryTable = queryTable.innerJoin(tableHouse, tableHouse['id'].eq(tableAddress['house_id']))
        queryTable = queryTable.innerJoin(tableKladr, tableKladr['CODE'].eq(tableHouse['KLADRCode']))

        recordList = self._db.getRecordList(queryTable,
                                            cols=[tableClientAddress['client_id'].alias('clientId'),
                                                  tableClientAddress['type'],
                                                  tableKladr['OCATD'].alias('OKATO')],
                                            where=tableClientAddress['id'].inlist(clientAddressIdList),
                                            order=tableClientAddress['type'])
        self.nextPhase(len(recordList), u'Обработка данных по адресам пациентов')
        for record in recordList:
            if self.isAbort:
                self.onAborted()
                return

            clientId = forceRef(record.value('clientId'))

            _, patientElement = entries.get(clientId, (None, None))
            if patientElement is None or patientElement.isNull():
                self.nextPhaseStep()
                continue

            isLocAddress = forceBool(record.value('type'))
            OKATO = forceStringEx(record.value('OKATO'))
            if not OKATO:
                self.nextPhaseStep()
                continue

            # Вставить новый элемент после SNILS. Но если это адрес проживания, то сначала попытаться после OKATOG, а уж потом после SNILS
            afterNodeList = ['SNILS']
            if isLocAddress:
                afterNodeList.insert(0, 'OKATOG')
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement,
                                                      'OKATOP' if isLocAddress else 'OKATOG',
                                                      ifNotExist=True,
                                                      afterElem=afterNodeList),
                                self.formatOKATO(OKATO, 11))
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
            if self.isAbort:
                self.onAborted()
                return
            orgId = forceRef(record.value('orgId'))
            elementList = self.orgForDeferredFilling.get(orgId, [])
            for element in elementList:
                infisCode = forceStringEx(record.value('infisCode'))[:6]
                if not infisCode:
                    orgName = forceStringEx(record.value('shortName'))
                    self.logger().warning(u'Пустой инфис код у организации {%s}"%s"' % (orgId, orgName))
                    continue
                CXMLHelper.setValue(element, infisCode)
            self.nextPhaseStep()


    def fillPersonSpeciality(self):
        self.nextPhase(1, u'Загрузка данных по врачам')
        tablePerson = self._db.table('Person')
        tableSpeciality = self._db.table('rbSpeciality')
        recordList = self._db.getRecordList(table=tablePerson.innerJoin(tableSpeciality,
                                                                        tableSpeciality['id'].eq(tablePerson['speciality_id'])),
                                            cols=[tablePerson['id'].alias('personId'),
                                                  tableSpeciality['federalCode'],
                                                  "CONCAT_WS(' ', %s, %s, %s) AS personName" % (tablePerson['lastName'].name(),
                                                                                                tablePerson['firstName'].name(),
                                                                                                tablePerson['patrName'].name())
                                                  ],
                                            where=[tablePerson['id'].inlist(self.personSpecialityForDeferredFilling.keys())])
        self.nextPhase(len(recordList), u'Обработка данных по врачам')
        for record in recordList:
            if self.isAbort:
                self.onAborted()
                return
            personId = forceRef(record.value('personId'))
            elementList = self.personSpecialityForDeferredFilling.get(personId, [])
            for element in elementList:
                federalCode = forceStringEx(record.value('federalCode'))[:6]
                if not federalCode:
                    personName = forceStringEx(record.value('personName'))
                    self.logger().warning(u'Пустой федеральный код специальности у врача {%s}"%s"' % (personId, personName))
                    continue
                CXMLHelper.setValue(element, federalCode)
            self.nextPhaseStep()


    def createXMLDocument(self, accountRecord, accCode, sourceOKATO, destOKATO):
        doc = CXMLHelper.createDomDocument(rootElementName='ZL_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        self.addHeaderElement(rootElement, sourceOKATO, destOKATO)
        accountElement = self.addAccountElement(rootElement, accountRecord, accCode)
        return doc, accountElement


    # def getFundOKATOCache(self):
    #     tableKladr = self._db.table('kladr.KLADR').alias('FundKladr')
    #     return dict([(forceStringEx(record.value('CODE'))[:2], forceStringEx(record.value('OCATD')))
    #                  for record in self._db.getRecordList(tableKladr,
    #                                                       cols=[tableKladr['CODE'],
    #                                                             tableKladr['OCATD']],
    #                                                       where=tableKladr['isInsuranceArea'].eq(1))
    #                  ])


    def process(self, accountId):
        self.isAbort = False
        self.phaseReset(11)

        tableOrganisation = self._db.table('Organisation')

        tableAccount = self._db.table('Account')
        tableContract = self._db.table('Contract')
        tableContractPayer = tableOrganisation.alias('ContractPayer') # Сторонний фонд, в который происходит выгрузка
        tableContractRecipient = tableOrganisation.alias('ContractRecipient') # Текущий фонд, откуда происходит выгрузка

        queryTable = tableAccount.innerJoin(tableContract, tableContract['id'].eq(tableAccount['contract_id']))
        queryTable = queryTable.innerJoin(tableContractPayer, tableContractPayer['id'].eq(tableContract['payer_id']))
        queryTable = queryTable.innerJoin(tableContractRecipient, tableContractRecipient['id'].eq(tableContract['recipient_id']))

        cols = [
                tableAccount['settleDate'],
                tableAccount['number'],
                tableAccount['exposeDate'],
                tableAccount['sum'],
                tableContractPayer['OKATO'].alias('payerOKATO'),
                tableContractPayer['infisCode'].alias('payerInfis'),
                tableContractPayer['area'].alias('payerArea'),
                tableContractRecipient['OKATO'].alias('recipientOKATO'),
                tableContractRecipient['infisCode'].alias('recipientInfis'),
                # tableContractRecipient['area'].alias('recipientArea')
        ]

        self.nextPhase(3, u'Загрузка данных по счету')
        accountRecord = self._db.getRecordEx(queryTable,
                                             cols,
                                             where=tableAccount['id'].eq(accountId))
        accSumForCheck = forceDouble(accountRecord.value('sum'))


        currentOKATO = forceStringEx(accountRecord.value('recipientOKATO'))
        currentInfis = forceStringEx(accountRecord.value('recipientInfis'))
        # currentArea = forceStringEx(accountRecord.value('recipientArea'))

        insuranceArea = forceStringEx(accountRecord.value('payerArea'))
        insurerFundOKATO = forceStringEx(accountRecord.value('payerOKATO'))
        insurerFundInfis = forceStringEx(accountRecord.value('payerInfis'))

        # self.nextPhaseStep(u'Загрузка данных по фондам')
        # fundCodesCache = self.getFundOKATOCache()

        tableAccountItem = self._db.table('Account_Item')
        tableEvent = self._db.table('Event')
        tableAction = self._db.table('Action')
        tableVisit = self._db.table('Visit')
        tableEventType = self._db.table('EventType')
        tableEventResult = self._db.table('rbResult').alias('EventResult')
        tableEventTypePurpose = self._db.table('rbEventTypePurpose')
        #TODO: atronah: костыль из-за кривого значения в Event.org_id
        tableEventContract = tableContract.alias('EventContract')

        tableLittleStranger = self._db.table('Event_LittleStranger')
        # tableContract = self._db.table('Contract')
        tableClient = self._db.table('Client')
        tablePolicy = self._db.table('ClientPolicy')
        tablePolicyKind = self._db.table('rbPolicyKind')
        # tableInsurer = tableOrganisation.alias('Insurer')
        tableDocument = self._db.table('ClientDocument')
        tableDocumentType = self._db.table('rbDocumentType')
        tableService = self._db.table('rbService')
        tableServiceAidProfile = self._db.table('rbMedicalAidProfile').alias('ServiceAidProfile')
        tableServiceAidKind = self._db.table('rbMedicalAidKind').alias('ServiceAidKind')
        tableEventTypeAidProfile = self._db.table('rbEventProfile').alias('EventTypeAidProfile')
        tableEventTypeAidKind = self._db.table('rbMedicalAidKind').alias('EventTypeAidKind')
        tableEventTypeAidType = self._db.table('rbMedicalAidType').alias('EventTypeAidType')
        tableEventAidUnit = self._db.table('rbMedicalAidUnit')
        tableEventHMPKind = self._db.table('rbHighTechCureKind')
        tableEventHMPMethod = self._db.table('rbHighTechCureMethod')
        tableEventPrimaryDiagnostic = self._db.table('Diagnostic').alias('EventDiagnostic')
        tableEventPrimaryDiagnosis = self._db.table('Diagnosis').alias('EventDiagnosis')
        tableDiagnosticResult = self._db.table('rbDiagnosticResult')

        # tableLPU = tableOrganisation.alias('LPU')
        # tableServiceOrg = tableOrganisation.alias('ServiceOrg')
        # tableRegClientAddress = self._db.table('ClientAddress').alias('RegClientAddress')
        # tableLocClientAddress = self._db.table('ClientAddress').alias('LocClientAddress')

        queryTable = tableAccountItem.innerJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
        queryTable = queryTable.leftJoin(tableEventContract, tableEventContract['id'].eq(tableEvent['contract_id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAccountItem['action_id']))
        queryTable = queryTable.leftJoin(tableVisit, tableVisit['id'].eq(tableAccountItem['visit_id']))
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableEventAidUnit, tableEventAidUnit['id'].eq(tableAccountItem['unit_id']))
        queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        queryTable = queryTable.leftJoin(tableEventResult, tableEventResult['id'].eq(tableEvent['result_id']))
        queryTable = queryTable.leftJoin(tableEventTypePurpose, tableEventTypePurpose['id'].eq(tableEventType['purpose_id']))
        queryTable = queryTable.leftJoin(tableEventHMPKind, tableEventHMPKind['id'].eq(tableEvent['hmpKind_id']))
        queryTable = queryTable.leftJoin(tableEventHMPMethod, tableEventHMPMethod['id'].eq(tableEvent['hmpMethod_id']))

        queryTable = queryTable.leftJoin(tableEventPrimaryDiagnostic,
                                         # получение диагноза по соответствию врачу и событию, и в случае неудачи только по соответствию событию
                                         '%(idField)s = IFNULL(getEventPersonDiagnostic(%(eventId)s, %(personId)s),'
                                         '                     getEventDiagnostic(%(eventId)s))' % {'idField': tableEventPrimaryDiagnostic['id'],
                                                                                                    'eventId': tableEvent['id'],
                                                                                                    'personId': tableEvent['execPerson_id']}
                                         )
        queryTable = queryTable.leftJoin(tableEventPrimaryDiagnosis,
                                         tableEventPrimaryDiagnosis['id'].eq(tableEventPrimaryDiagnostic['diagnosis_id']))
        queryTable = queryTable.leftJoin(tableDiagnosticResult, tableDiagnosticResult['id'].eq(tableEventPrimaryDiagnostic['result_id']))
        queryTable = queryTable.leftJoin(tableLittleStranger, tableLittleStranger['id'].eq(tableEvent['littleStranger_id']))
        queryTable = queryTable.leftJoin(tableDocument, '%s = %s' % (tableDocument['id'].name(),
                                                                     'getClientDocumentId(%s)' % tableClient['id'].name()))
        queryTable = queryTable.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableDocument['documentType_id']))

        #TODO: atronah: полис на дату или последний?
        queryTable = queryTable.innerJoin(tablePolicy, '%s = %s' % (tablePolicy['id'].name(),
                                                                    'getClientPolicyId(%s, %s)' % (tableClient['id'].name(), 1)))
        queryTable = queryTable.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tablePolicy['policyKind_id']))

        # queryTable = queryTable.leftJoin(tableInsurer, tableInsurer['id'].eq(tablePolicy['insurer_id']))
        queryTable = queryTable.leftJoin(tableService, tableService['id'].eq(tableAccountItem['service_id']))
        queryTable = queryTable.leftJoin(tableServiceAidProfile, tableServiceAidProfile['id'].eq(tableService['medicalAidProfile_id']))
        queryTable = queryTable.leftJoin(tableServiceAidKind, tableServiceAidKind['id'].eq(tableService['medicalAidKind_id']))
        queryTable = queryTable.leftJoin(tableEventTypeAidProfile, tableEventTypeAidProfile['id'].eq(tableEventType['eventProfile_id']))
        queryTable = queryTable.leftJoin(tableEventTypeAidKind, tableEventTypeAidKind['id'].eq(tableEventType['medicalAidKind_id']))
        queryTable = queryTable.leftJoin(tableEventTypeAidType, tableEventTypeAidType['id'].eq(tableEventType['medicalAidType_id']))
        # queryTable = queryTable.innerJoin(tableLPU, tableLPU['id'].eq(tableEvent['org_id']))

        # addressIdStmt =  'getClientRegAddressId(%s)' % tableClient['id'].name()
        # queryTable = queryTable.innerJoin(tableRegClientAddress, '%s = %s' % (tableRegClientAddress['id'].name(),
        #                                                                       addressIdStmt))
        # queryTable = queryTable.innerJoin(tableRegAddress, tableRegAddress['id'].eq(tableRegClientAddress['address_id']))
        # addressIdStmt =  'getClientLocAddressId(%s)' % tableClient['id'].name()
        # queryTable = queryTable.innerJoin(tableLocClientAddress, '%s = %s' % (tableLocClientAddress['id'].name(),
        #                                                                       addressIdStmt))

        cols = [tableClient['id'].alias('clientId'),
                tableEvent['id'].alias('eventId'),
                # tableInsurer['area'],
                # tableInsurer['infisCode'].alias('insurerInfis'),
                # tableInsurer['OKATO'].alias('insurerOKATO'),
                tableAccountItem['id'].alias('accountItemId'),
                tableAccountItem['note'],

                # for fillPatient
                tablePolicyKind['federalCode'].alias('policyKindCode'),
                tablePolicy['serial'].alias('policySerial'),
                tablePolicy['number'].alias('policyNumber'),
                '%s IS NOT NULL AS isLittleStranger' % tableLittleStranger['id'].name(),
                tableClient['lastName'].alias('clientLastName'),
                tableClient['firstName'].alias('clientFirstName'),
                tableClient['patrName'].alias('clientPatrName'),
                tableClient['sex'].alias('clientSex'),
                tableClient['birthDate'].alias('clientBirthdate'),
                tableLittleStranger['sex'].alias('strangeSex'),
                tableLittleStranger['birthDate'].alias('strangeBirthdate'),
                tableDocumentType['federalCode'].alias('clientDocType'),
                tableDocument['serial'].alias('clientDocSerial'),
                tableDocument['number'].alias('clientDocNumber'),
                tableClient['SNILS'].alias('clientSNILS'),
                'getClientLocAddressId(%s) AS clientLocAddressId' % tableClient['id'],
                'getClientRegAddressId(%s) AS clientRegAddressId' % tableClient['id'],
                'age(%s, %s) AS clientAge' % (tableClient['birthDate'], tableEvent['execDate']),

                # for addServiceElement
                tableServiceAidKind['federalCode'].alias('serviceAidKindCode'),
                tableServiceAidProfile['federalCode'].alias('serviceAidProfileCode'),
                tableAction['begDate'].alias('actionBegDate'),
                tableAction['endDate'].alias('actionEndDate'),
                tableVisit['date'].alias('visitDate'),
                tableEvent['setDate'].alias('eventSetDate'),
                tableEvent['execDate'].alias('eventExecDate'),
                tableService['name'].alias('serviceName'),
                tableAccountItem['amount'].alias('serviceAmount'),
                tableAccountItem['price'].alias('servicePrice'),
                tableAccountItem['sum'].alias('serviceSum'),
                tableAction['MKB'].alias('actionMKB'),
                tableVisit['MKB'].alias('visitMKB'),


                # for addEventElement
                tableEventTypePurpose['federalCode'].alias('eventTypePurposeCode'),
                tableEventTypeAidKind['federalCode'].alias('eventTypeAidKindCode'),
                tableEvent['order'].alias('eventOrder'),
                tableEventHMPKind['code'].alias('eventHMPKindCode'),
                tableEventHMPMethod['code'].alias('eventHMPMethodCode'),
                # tableEventTypeAidProfile['code'].alias('eventTypeAidProfileCode'),
                tableEventPrimaryDiagnosis['MKB'].alias('eventPrimaryMKB'),
                tableEventResult['federalCode'].alias('eventResultCode'),
                tableDiagnosticResult['federalCode'].alias('eventPrimaryMKBResultCode'),
                tableEventAidUnit['federalCode'].alias('eventAidUnitCode'),
                tableEventTypeAidType['code'].alias('eventTypeAidTypeCode'),


                # for deferred filling (by additional queries)
                #TODO: atronah: костыль из-за некорректного Event.org_id
                tableEventContract['recipient_id'].alias('eventOrgId'),
                # tableEvent['org_id'].alias('eventOrgId'),

                tableAction['org_id'].alias('actionOrgId'),
                tableEvent['execPerson_id'].alias('eventExecPersonId'),
                'IFNULL(%s, %s) AS actionPersonId' % (tableAction['person_id'],
                                                      tableAction['setPerson_id']),
                tableVisit['person_id'].alias('visitPersonId')
                ]
        cond = [tableAccountItem['master_id'].eq(accountId),
                tableAccountItem['deleted'].eq(0)]
        # if currentArea:
        #     cond.append("LEFT(%s, 2) != '%s'" % (tableInsurer['area'], currentArea[:2]))
        # else:
        #     for area, (_, insurerFundInfis) in fundCodesCache.iteritems():
        #         if insurerFundInfis == currentInfis:
        #             cond.append('LEFT(%s, 2) != LEFT(%s, 2)' % (tableInsurer['area'], area))


        self.nextPhaseStep(u'Загрузка данных по счету')
        recordList = self._db.getRecordList(queryTable, cols, where=cond)
        self.nextPhaseStep(u'Загрузка данных завершена')

        self.documents.clear()
        self.fileNameParts.clear()
        self.accCodeToAccountItemId.clear()
        entries = {}
        events = {}
        idCaseCounter = {}
        entryCounter = {}
        clientAddressIdList = []
        # serviceCounter = {}
        self.orgForDeferredFilling.clear()
        self.personSpecialityForDeferredFilling.clear()
        eventsTotal = {}
        accountTotal = {}
        self.nextPhase(len(recordList), u'Обработка позиций счета')
        for record in recordList:
            if self.isAbort:
                self.onAborted()
                return False


            if not self.fileNameParts.has_key(insuranceArea):
                #atronah: или надо infisCode?
                self.fileNameParts[insuranceArea] = (currentInfis, insurerFundInfis)

            #FIXME: atronah: текущая логика чревата ошибками:
            # Если у первого элемента счета в "Примечаниях" отсутствует код счета (SCHET.CODE),
            # то будет сгенерированн новый код с использованием счетчикаи он будет проставлен в выгрузке
            # и в "Примечаниях" только у тех элементов счета, которые не содержат другой код.
            # Таким образом может быть ситуация, когда в одном счете базы у элементов разные коды,
            # в то время как в экспортируемом файле код проставляется только у счета
            existedAccCode = self.parseAccCode(forceStringEx(record.value('note')))

            if not self.documents.has_key(insuranceArea):
                self.documents[insuranceArea] = self.createXMLDocument(accountRecord,
                                                                       existedAccCode,
                                                                       sourceOKATO=currentOKATO,
                                                                       destOKATO=insurerFundOKATO)

            doc, accountElement = self.documents[insuranceArea]

            rootElement = CXMLHelper.getRootElement(doc)
            clientId = forceRef(record.value('clientId'))

            accCode = forceStringEx(accountElement.firstChildElement('CODE').text())
            itemId = forceRef(record.value('accountItemId'))
            if existedAccCode is None:
                self.accCodeToAccountItemId.setdefault(accCode, []).append(itemId)


            if not entries.has_key(clientId):
                entryCounter[insuranceArea] = entryCounter.setdefault(insuranceArea, 0) + 1
                entries[clientId] = self.addEntryElement(rootElement, record, entryCounter[insuranceArea])
                addressId = forceRef('clientLocAddressId')
                if addressId:
                    clientAddressIdList.append(addressId)
                addressId = forceRef('clientRegAddressId')
                if addressId:
                    clientAddressIdList.append(addressId)

            entryElement, _ = entries[clientId]


            eventId = forceRef(record.value('eventId'))

            if not events.has_key(eventId):
                idCaseCounter[insuranceArea] = idCaseCounter.setdefault(insuranceArea, 0) + 1
                events[eventId] = self.addEventElement(entryElement,
                                                       idCaseCounter[insuranceArea],
                                                       record)
            eventElement = events[eventId]



            # serviceCounter[eventId] = serviceCounter.setdefault(eventId, 0) + 1
            self.addServiceElement(eventElement,
                                   idServ=forceRef(record.value('accountItemId')),
                                   record=record)
            serviceSum = forceDouble(record.value('serviceSum'))
            eventsTotal[eventId] = eventsTotal.setdefault(eventId, 0) + serviceSum
            accountTotal[insuranceArea] = accountTotal.setdefault(insuranceArea, 0) + serviceSum
            # serviceSumList.append(serviceSum)
            self.nextPhaseStep()


        self.nextPhase(len(accountTotal), u'Заполнение данных об общей стоимости счетов')
        if round(accSumForCheck, 2) != round(sum(accountTotal.values()), 2):
            self.logger().critical(u'Обнаружено расхождение стоимости исходного '
                                   u'общего счета (%s) и суммы стоимостей счетов по регионам (%s)' % (round(accSumForCheck, 2),
                                                                                                      round(sum(accountTotal.values()), 2))
                                   )
        for insuranceArea, total in accountTotal.iteritems():
            if self.isAbort:
                self.onAborted()
                return False
            _, accountElement = self.documents[insuranceArea]

            exposedSumElement = accountElement.firstChildElement('SUMMAV')
            payedSumElement = accountElement.firstChildElement('SUMMAP')
            CXMLHelper.setValue(exposedSumElement, '%.2f' % total)
            CXMLHelper.setValue(payedSumElement, '%.2f' % total)
            self.nextPhaseStep()

        self.nextPhase(len(eventsTotal), u'Заполнение данных о стоимости случаев')
        for eventId, total in eventsTotal.iteritems():
            if self.isAbort:
                self.onAborted()
                return False
            eventElement = events[eventId]
            for elemName in ['TARIF', 'SUMV', 'SUMP']:
                element = eventElement.firstChildElement(elemName)
                CXMLHelper.setValue(element, '%.2f' % total)
            self.nextPhaseStep()

        if not self.isAbort:
            self.fillAdditionalDiagnosis(events)
        if not self.isAbort:
            self.fillAddressess(entries, clientAddressIdList)
        if not self.isAbort:
            self.fillOrganisations()
        if not self.isAbort:
            self.fillPersonSpeciality()



        self.logger().info(u'Завершено')
        if self.isAbort:
            self.onAborted()
            return False
        return True


    @staticmethod
    def parseAccCode(accCodeNote):
        codeList = re.findall(ur'SCHET\.CODE=(\d{1,8})\b', accCodeNote)
        return int(codeList[-1]) if codeList else None


    @staticmethod
    def makeAccCodeNote(accCode):
        return 'SCHET.CODE=%s' % accCode



    def updateAccountItems(self):
        self.nextPhase(1, u'Обновление элементов счета')
        tableAccountItem = self._db.table('Account_Item')
        caseVariants = []
        allItemIdList = []
        for accCode, itemIdList in self.accCodeToAccountItemId.iteritems():
            caseVariants.append("WHEN %s THEN ';%s'" % (tableAccountItem['id'].inlist(itemIdList), self.makeAccCodeNote(accCode)))
            allItemIdList.extend(itemIdList)
        if caseVariants:
            updateStmt = '''UPDATE %(tableName)s
                                SET %(modifyField)s = CONCAT(%(modifyField)s,
                                                            CASE
                                                                %(caseVariants)s
                                                                ELSE ''
                                                            END)
                            WHERE
                                %(cond)s''' % {'tableName': tableAccountItem.name(),
                                               'modifyField': tableAccountItem['note'],
                                               'caseField': tableAccountItem['id'],
                                               'caseVariants': ' \n'.join(caseVariants),
                                               'cond': tableAccountItem['id'].inlist(allItemIdList)
                                               }
            self._db.transaction()
            try:
                self._db.query(updateStmt)
                self._db.commit()
            except:
                self._db.rollback()
                raise
        self.accCodeToAccountItemId.clear()


    def save(self, outDir, exportNumber):
        self.phaseReset(2)
        outDir = forceStringEx(outDir)
        self.nextPhase(len(self.documents), u'Сохранение файлов')
        for destArea in self.documents.keys():
            doc, _ = self.documents[destArea]
            currentInfis, insurerFundInfis = self.fileNameParts[destArea]
            fileFullName = forceStringEx(os.path.join(outDir, u''.join([u'R',
                                                                        self.formatOKATO(currentInfis, 2),
                                                                        self.formatOKATO(insurerFundInfis, 2),
                                                                        u'%s' % QtCore.QDate.currentDate().toString('yy'),
                                                                        u'%.4d' % exportNumber,
                                                                        u'.xml'])))
            try:
                with codecs.open(fileFullName, 'w', encoding=self.encoding) as outFile:
                    outFile.write(forceStringEx(doc.toString(4)))
                    self.logger().info(u'Создан файл: "%s"' % fileFullName)
                self.documents.pop(destArea)
            except Exception, e:
                self.logger().critical(u'Не удалось сохранить файл "%s" (%s)' % (e.message, fileFullName))

        if not self.documents:
            self.updateAccountItems()


class CExportDialog(QtGui.QDialog):
    InitState = 0
    ExportState = 1
    SaveState = 2


    def __init__(self, db, accountId, parent = None):
        super(CExportDialog, self).__init__(parent = parent)
        self._db = db
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._accountId = accountId
        self._engine = CExportR85MTREngine(db, progressInformer=self._pi)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._loggerHandler.setLevel(logging.INFO)
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
        self.btnSave.setEnabled(bool(self._engine.documents))
        QtCore.QCoreApplication.processEvents()


    # noinspection PyAttributeOutsideInit
    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        self.gbInit = QtGui.QGroupBox()
        gbLayout = QtGui.QHBoxLayout()
        self.lblAccountNumber = QtGui.QLabel()
        gbLayout.addWidget(self.lblAccountNumber)
        self.spbAccountNumber = QtGui.QSpinBox()
        self.spbAccountNumber.setRange(1, 9999)
        gbLayout.addWidget(self.spbAccountNumber)
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
        self.btnBrowseDir.clicked.connect(self.onBrowseDirClicked)
        lineLayout.addWidget(self.btnBrowseDir)
        gbLayout.addLayout(lineLayout)
        lineLayout = QtGui.QHBoxLayout()
        # self.chkZipping = QtGui.QCheckBox()
        # lineLayout.addWidget(self.chkZipping)
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


    # noinspection PyAttributeOutsideInit
    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Экспорт. Крым. МежТер.', context))
        self.gbInit.setTitle(forceTr(u'Параметры экспорта', context))
        self.lblAccountNumber.setText(forceTr(u'Номер выгрузки по счету', context))

        self.gbExport.setTitle(forceTr(u'Экспорт', context))

        self.gbSave.setTitle(forceTr(u'Сохранение результата', context))
        # self.chkZipping.setText(forceTr(u'Поместить файл(-ы) в архив', context))
        self.btnSave.setText(forceTr(u'Сохранить', context))

        self._actionNames = {self.InitState: forceTr(u'Экспорт',context),
                             self.ExportState: forceTr(u'Прервать', context),
                             self.SaveState: forceTr(u'Повторить', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))


    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ExportState
            try:
                result = self._engine.process(self._accountId)
            except Exception, e:
                self.currentState = self.InitState
                raise
            self.currentState = self.SaveState if result else self.InitState

        elif self.currentState == self.ExportState:
            self._engine.abort()
        elif self.currentState == self.SaveState:
            self.currentState = self.InitState
        self.onStateChanged()


    def canClose(self):
        return not self._engine.documents or \
               QtGui.QMessageBox.warning(self,
                                         u'Внимание',
                                         u'Остались несохраненные файлы выгрузок,\n'
                                         u'которые будут утеряны.\n'
                                         u'Уверены, что хотить выйти из экспорта?\n',
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
    def onBrowseDirClicked(self):
        saveDir = forceStringEx(QtGui.QFileDialog.getExistingDirectory(self,
                                                                       u'Укажите директорию для сохранения файлов выгрузки',
                                                                       self.edtSaveDir.text()))
        if os.path.isdir(saveDir):
            self.edtSaveDir.setText(saveDir)


    @QtCore.pyqtSlot()
    def onSaveClicked(self):
        self.btnClose.setEnabled(False)
        self._engine.save(self.edtSaveDir.text(), self.spbAccountNumber.value())
        self.onStateChanged()



class CImportR85MTREngine(CExchangeR85Engine):
    def __init__(self, db, orgId, progressInformer = None):
        super(CImportR85MTREngine, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None

        self._orgId = orgId
        self._orgInfis = None
        self._currentOKATO = None

        self._contractIdByInfis = {}
        self._resultCache = {}
        self._diagnosticResultCache = {}
        self._personIdBySpeciality = {}
        self._aidKindCache = {}
        self._purposeCache = {}
        self._lpuCache = {}
        self._unitCache = {}
        self._documentTypeCache = {}
        self._eventTypeCache = {}
        self._funds = {}
        self._userConfirmation = None



    def getElement(self, parentNode, elementName, isRequired=False):
        element = parentNode.firstChildElement(elementName)
        if element.isNull() and isRequired:
            self.logger().warning(u'Ошибка формата файла. Ожидаемый узел: "%s" не был найден [%s:%s]' % (elementName, element.nodeName(), parentNode.lineNumber(), parentNode.columnNumber()))
        return element


    def clearAll(self):
        self._contractIdByInfis.clear()

        self.clearDocumentCache()


    def clearDocumentCache(self):
        #TODO: atronah: очищать документо зависимые данные
        pass


    def initContractIdInfo(self):
        """
        Формирует кэш идентификаторов договоров для всех ТФ с учетом года действия.
        Делается выборка по всем договорам, дата окончания которых в этом или в предыдущем году,
        а также, у которых получателем является ТФ (5ти значный инфис код с 3 нулями на конце).
        Результаты выборки (id договоров) помещаются в словарь с ключом (инфис_код, год).

        Если год начала отличается от года окончания договора, то данный договор попадает в словарь столько раз,
        сколько лет охватывает его период действия.
        """
        #FIXME: craz: переделано под то, что есть на тестовой базе. Сейчас берем не получателя, а плательщика. И код не 5 символов, а 2
        self.nextPhase(1, u'Загрузка данных по договорам ТФ')
        self._contractIdByInfis.clear()
        tableContract = self._db.table('Contract')
        tableOrganisation = self._db.table('Organisation')
        queryTable = tableContract.innerJoin(tableOrganisation,
                                             tableOrganisation['id'].eq(tableContract['payer_id']))

        recordList = self._db.getRecordList(table=queryTable,
                                            cols=[tableContract['id'].alias('contractId'),
                                                  tableContract['begDate'].alias('contractBegDate'),
                                                  tableContract['endDate'].alias('contractEndDate'),
                                                  tableOrganisation['infisCode']],
                                            where=[tableContract['deleted'].eq(0),
                                                   'YEAR(%s) >= (YEAR(CURRENT_DATE) - 1)' % tableContract['endDate'],
                                                   #TODO: не уверен, что у ТФ у всех инфис формата __000
                                                   tableOrganisation['infisCode'].like('__')],
                                            order=tableContract['endDate'])
        self.nextPhase(len(recordList), u'Обработка данных по договорам ТФ')
        for record in recordList:
            sourceInfis = forceStringEx(record.value('infisCode'))[:2]
            begDate = forceDate(record.value('contractBegDate'))
            endDate = forceDate(record.value('contractEndDate'))
            contractId = forceRef(record.value('contractId'))
            for year in xrange(begDate.year(), endDate.year() + 1):
                self._contractIdByInfis[sourceInfis, year] = contractId


    def loadCurrentFundInfo(self):
        self.nextPhase(1, u'Получение данных по текущему ТФ')
        tableOrganisation = self._db.table('Organisation')
        record = self._db.getRecord(tableOrganisation,
                                    cols=[tableOrganisation['infisCode'],
                                          tableOrganisation['OKATO']],
                                    itemId=self._orgId)
        self._orgInfis = forceStringEx(record.value('infisCode'))
        if not self._orgInfis:
            self.logger().warning(u'Не удалось получить инфис код текущего ТФ{%s}' % self._orgId)
        self._currentOKATO = self.formatOKATO(record.value('OKATO'), 2)


    def getContractId(self, infisCode, year):
        infisCode = forceStringEx(infisCode)[:2]
        contractId = self._contractIdByInfis.get((infisCode, year), None)
        if not contractId:
            self.logger().warning(u'Не удалось найти договор для импорта данных по территории с инфис "%s"' % infisCode)

        return contractId


    def setUserConfirmationFunction(self, func):
        self._userConfirmation = func


    def getUserConfimation(self, title, message):
        return self._userConfirmation(title, message) if callable(self._userConfirmation) else True


    def process(self, fileName):
        self.phaseReset(2)
        self.initContractIdInfo()
        self.loadCurrentFundInfo()
        self.processFile(fileName)
        return True


    def parseFileName(self, fileName):
        """
        Вычленяет из имени файла важную информацию.
        Предполагается, что имя файла представлено в формате:
            R + код территориального фонда обязательного медицинского страхования, выставившего счет
            + код территориального фонда обязательного медицинского страхования, которому предъявлен счет
            + две последние цифры года
            + четырехзначный порядковый номер представления основной части в текущем году
        :param fileName: имя обрабатываемого файла
        :return: isOk, sourceInfis, destInfis, year, number
        """
        try:
            name = os.path.splitext(os.path.basename(fileName))[0].lower()
            if name.startswith('r') and len(name) == 11:
                return True, forceStringEx(name[1:3]), forceStringEx(name[3:5]), 2000 + int(name[5:7], 10), int(name[7:11], 10)
        except Exception, e:
            self.logger().critical(u'Некорректное имя файла "%s" (%s)' % (fileName, e.message))

        return False, u'', u'', None, None


    def processFile(self, fileName):
        try:
            isOk, sourceInfis, destInfis, year, number = self.parseFileName(fileName)
            if destInfis[:2] != self._orgInfis[:2]:
                self.logger().info(u'Пропуск обработки файла "%s": территория назначения (%s) не соответствует текущей (%s)' % (fileName, destInfis, self._orgInfis))
            with codecs.open(fileName, 'r', encoding=self.encoding) as docFile:
                self.processDocument(CXMLHelper.loadDocument(docFile.read().encode('utf-8')),
                                     sourceInfis,
                                     year,
                                     number)
        except Exception, e:
            self.logger().warning(u'Не удалось импортировать файл "%s" (%s)' % (fileName, e.message))


    def processDocument(self, document, sourceInfis, year, number):
        self.clearDocumentCache()
        rootElement = self.getElement(document, 'ZL_LIST', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'ZGLV', isRequired=True)
        if not headerElement:
            return False
        isOk, fundInfo = self.parseHeaderElement(headerElement, sourceInfis)
        if not isOk:
            return False

        accountElement = self.getElement(rootElement, 'SCHET', isRequired=True)
        isOk, accInfo = self.parseAccountElement(accountElement, sourceInfis, year, fundInfo)
        if not isOk:
            return False

        entityElement = accountElement.nextSiblingElement('ZAP')
        while not entityElement.isNull():
            if not self.parseEntityElement(entityElement, accInfo):
                return False
            entityElement = entityElement.nextSiblingElement('ZAP')

        self.processEntities(accInfo)
        return True


    def parseHeaderElement(self, headerElement, sourceInfis):
        targetOKATO = self.formatOKATO(self.getElement(headerElement,
                                                       'OKATO_OMS',
                                                       isRequired=True).text(),
            2)
        if targetOKATO != self._currentOKATO:
            self.logger().warning(u'Целевой ОКАТО (OKATO_OMS) файла не соответствует ОКАТО текущего ТФ')
            return False, None

        sourceOKATO = self.formatOKATO(self.getElement(headerElement, 'C_OKATO1', isRequired=True).text())
        return True, self._funds.setdefault(sourceInfis, {'OKATO' : sourceOKATO})


    def parseAccountElement(self, accountElement, sourceInfis, year, fundInfo):
        contractId = self.getContractId(sourceInfis, year)
        if not contractId:
            return False, None

        accNumber = forceStringEx(self.getElement(accountElement, 'NSCHET', isRequired=True).text())
        accExposeDateString = forceStringEx(self.getElement(accountElement, 'DSCHET', isRequired=True).text())
        accExposeDate = QtCore.QDate.fromString(accExposeDateString, self.defaultDateFormat)

        accInfo = fundInfo.setdefault(accNumber, {})

        tableAccount = self._db.table('Account')
        record = self._db.getRecordEx(tableAccount,
                                      cols='*',
                                      where=[tableAccount['number'].like(accNumber),
                                             tableAccount['exposeDate'].eq(accExposeDate),
                                             'YEAR(%s) = %s' % (tableAccount['settleDate'], year)])
        if record:
            if self.getUserConfimation(u'Подтвердите удаление',
                                       u'Данный счет (%s от %s) уже был загружен ранее.\n'
                                       u'Удалить ранее загруженный счет?' % (accNumber, accExposeDateString)):
                accInfo['deletedCond'] = tableAccount['id'].eq(forceRef(record.value('id')))
            else:
                return False, None

        contractInfo = getContractInfo(contractId)

        record = tableAccount.newRecord()
        record.setValue('number', toVariant(accNumber))
        record.setValue('exposeDate', toVariant(accExposeDate))
        settleMonth = forceInt(self.getElement(accountElement, 'MONTH', isRequired=True).text())
        record.setValue('settleDate', toVariant(QtCore.QDate(year, settleMonth, 1)))
        record.setValue('amount', toVariant(self.dummyN))
        exposeTotal = forceDouble(self.getElement(accountElement, 'SUMMAV', isRequired=True).text())
        record.setValue('sum', toVariant(exposeTotal))
        record.setValue('contract_id', toVariant(contractId))
        record.setValue('payer_id', toVariant(contractInfo.payer_id))

        accInfo['record'] = record
        accInfo['contractInfo'] = contractInfo
        accInfo['entities'] = {}

        return True, accInfo


    def parseEntityElement(self, entityElement, accInfo):
        entityKey = forceStringEx(self.getElement(entityElement, 'N_ZAP', isRequired=True).text())
        if not entityKey:
            return False

        entityInfo = accInfo['entities'].setdefault(entityKey, {})
        patientElement = self.getElement(entityElement, 'PACIENT', isRequired=True)
        entityInfo['patient'] = self.parsePatient(patientElement)
        entityInfo['events'] = {}
        sluchElement = patientElement.nextSiblingElement('SLUCH')
        while not sluchElement.isNull():
            if not self.parseSluch(sluchElement, entityInfo):
                return False
            sluchElement = sluchElement.nextSiblingElement('SLUCH')
        return True

    def parsePatient(self, patientElement):
        patientInfo = {}
        patientInfo['policyKind'] = forceInt(self.getElement(patientElement, 'VPOLIS', isRequired=True).text())
        patientInfo['policySerial'] = forceStringEx(self.getElement(patientElement, 'SPOLIS').text())
        patientInfo['policyNumber'] = forceStringEx(self.getElement(patientElement, 'NPOLIS').text())
        patientInfo['enp'] = forceStringEx(self.getElement(patientElement, 'ENP', isRequired=True).text())
        patientInfo['stOkato'] = forceStringEx(self.getElement(patientElement, 'ST_OKATO', isRequired=False).text())
        patientInfo['lastName'] = forceStringEx(self.getElement(patientElement, 'FAM').text())
        patientInfo['firstName'] = forceStringEx(self.getElement(patientElement, 'IM').text())
        patientInfo['patrName'] = forceStringEx(self.getElement(patientElement, 'OT').text())
        patientInfo['sex'] = forceInt(self.getElement(patientElement, 'W', isRequired=True).text())
        patientInfo['birthDate'] = QtCore.QDate.fromString(forceStringEx(self.getElement(patientElement, 'DR', isRequired=True).text()),
            self.defaultDateFormat)
        #TODO: craz: process DOST tag and all _P tags
        patientInfo['birthPlace'] = forceStringEx(self.getElement(patientElement, 'MR').text())
        patientInfo['documentType'] = forceStringEx(self.getElement(patientElement, 'DOCTYPE').text())
        self._documentTypeCache[patientInfo['documentType']] = None
        patientInfo['documentSerial'] = forceStringEx(self.getElement(patientElement, 'DOCSER').text())
        patientInfo['documentNumber'] = forceStringEx(self.getElement(patientElement, 'DOCNUM').text())
        patientInfo['SNILS'] = forceStringEx(self.getElement(patientElement, 'SNILS').text())
        #TODO: craz: process OKATO_* and NOVOR tags
        return patientInfo

    def parseSluch(self, sluchElement, entityInfo):
        sluchKey = forceStringEx(self.getElement(sluchElement, 'IDCASE', isRequired=True).text())
        if not sluchKey:
            return False

        sluchInfo = entityInfo['events'].setdefault(sluchKey, {})
        sluchInfo['eventTypePurpose'] = forceStringEx(self.getElement(sluchElement, 'USL_OK', isRequired=True).text())
        sluchInfo['medicalAidKind'] = forceStringEx(self.getElement(sluchElement, 'VIDPOM', isRequired=True).text())
        sluchInfo['order'] = forceInt(self.getElement(sluchElement, 'FOR_POM', isRequired=True).text())
        sluchInfo['lpu'] = forceStringEx(self.getElement(sluchElement, 'LPU', isRequired=True).text())
        sluchInfo['profil'] = forceStringEx(self.getElement(sluchElement, 'PROFIL', isRequired=True).text())
        sluchInfo['det'] = forceInt(self.getElement(sluchElement, 'PROFIL', isRequired=True).text())
        sluchInfo['externalId'] = forceStringEx(self.getElement(sluchElement, 'NHISTORY', isRequired=True).text())
        sluchInfo['setDate'] = QtCore.QDate.fromString(self.getElement(sluchElement, 'DATE_1', isRequired=True).text(),
            self.defaultDateFormat)
        sluchInfo['execDate'] = QtCore.QDate.fromString(self.getElement(sluchElement, 'DATE_2', isRequired=True).text(),
            self.defaultDateFormat)
        sluchInfo['mainMKB'] = forceStringEx(self.getElement(sluchElement, 'DS1', isRequired=True).text())
        #TODO: craz: process other DS* tags, VNOV_M, CODE_MES*
        sluchInfo['result'] = forceStringEx(self.getElement(sluchElement, 'RSLT', isRequired=True).text())
        sluchInfo['diagnosticResult'] = forceStringEx(self.getElement(sluchElement, 'ISHOD', isRequired=True).text())
        sluchInfo['speciality'] = forceStringEx(self.getElement(sluchElement, 'PRVS', isRequired=True).text())
        sluchInfo['unit'] = forceStringEx(self.getElement(sluchElement, 'IDSP', isRequired=True).text())
        #TODO: craz: process ED_COL
        sluchInfo['tarif'] = forceDouble(self.getElement(sluchElement, 'TARIF').text())
        sluchInfo['sum'] = forceDouble(self.getElement(sluchElement, 'SUMMV').text())

        self._purposeCache[sluchInfo['eventTypePurpose']] = None
        self._aidKindCache[sluchInfo['medicalAidKind']] = None
        self._lpuCache[sluchInfo['lpu']] = None
        self._resultCache[sluchInfo['result']] = None
        self._diagnosticResultCache[sluchInfo['diagnosticResult']] = None
        self._unitCache[sluchInfo['unit']] = None
        return True

    def processEntities(self, accInfo):
        self.loadRefBooks()

        # TODO: craz: поиск существующих записей.
        # TODO: craz: проработать логику внешних идентификаторов (какие используем, где храним)
        accountId = self._db.insertRecord('Account', accInfo['record'])
        contractId = accInfo['record'].value('contract_id')
        tableEvent = self._db.table('Event')
        tableAccountItem = self._db.table('Account_Item')
        for entityKey, entity in accInfo['entities'].items():

            self._db.transaction()
            try:
                clientId = self.processPatient(entity['patient'])
                for eventKey, eventInfo in entity['events'].items():
                    purposeId = self._purposeCache.get(eventInfo['eventTypePurpose'], None)
                    aidKindId = self._aidKindCache.get(eventInfo['medicalAidKind'], None)
                    if purposeId is None:
                        self.logger().critical(u'Не удалось определить назначение обращения для IDCASE = %s' % eventKey)
                        continue
                    if aidKindId is None:
                        self.logger().critical(u'Не удалось определить вид помощи для IDCASE = %s' % eventKey)
                        continue
                    eventTypeId = self.getEventType(purposeId, aidKindId)
                    if eventTypeId is None:
                        self.logger().critical(u'Не удалось определить тип обращения для IDCASE = %s' % eventKey)
                        continue
                    lpuId = self._lpuCache.get(eventInfo['lpu'], None)
                    if lpuId is None:
                        lpuId = accInfo['contractInfo'].recipient_id
                    resultId = self._resultCache.get(eventInfo['result'], None)

                    eventRecord = tableEvent.newRecord()
                    eventRecord.setValue('client_id', toVariant(clientId))
                    eventRecord.setValue('contract_id', contractId)
                    eventRecord.setValue('eventType_id', toVariant(eventTypeId))
                    eventRecord.setValue('setDate', toVariant(eventInfo['setDate']))
                    eventRecord.setValue('execDate', toVariant(eventInfo['execDate']))
                    eventRecord.setValue('org_id', toVariant(lpuId))
                    eventRecord.setValue('isPrimary', toVariant(1))
                    eventRecord.setValue('externalId', toVariant(eventInfo['externalId']))
                    eventRecord.setValue('order', toVariant({
                                                   3: 1,    # Плановая
                                                   1: 2,    # Экстренная
                                                   2: 6,    # Неотложная
                                                   }.get(eventInfo['order'], 1)))
                    if resultId:
                        eventRecord.setValue('result_id', toVariant(resultId))
                    eventRecord.setValue('pregnancyWeek', toVariant(0))
                    eventRecord.setValue('totalCost', toVariant(0))
                    # TODO: craz: Определять врача по специальности и ЛПУ (либо нагенерить заглушек для каждой организации, либо брать ответственными врачей из фонда)
                    eventId = self._db.insertRecord(tableEvent, eventRecord)

                    # TODO: craz: обработка диагнозов и услуг

                    aiRecord = tableAccountItem.newRecord()



                self._db.commit()
            except:
                self._db.rollback()
                QtGui.qApp.logCurrentException()
                raise

    def processPatient(self, patientInfo):
        #TODO: craz: Обработка полисов и документов.
        tableClient = self._db.table('Client')
        # tableClientPolicy = self._db.table('ClientPolicy')
        # tableClientDocument = self._db.table('ClientDocument')
        cols = [tableClient['id'],
                tableClient['lastName'],
                tableClient['firstName'],
                tableClient['patrName'],
                tableClient['sex'],
                tableClient['birthDate'],
                tableClient['birthPlace'],
                tableClient['SNILS'],
                ]

        cond = [tableClient['SNILS'].eq(unformatSNILS(patientInfo['SNILS']))]
        clientRecord = self._db.getRecordEx(tableClient, cols, cond)
        if not clientRecord:
            cond = [tableClient['lastName'].eq(patientInfo['lastName']),
                    tableClient['firstName'].eq(patientInfo['firstName']),
                    tableClient['patrName'].eq(patientInfo['patrName']),
                    tableClient['birthDate'].dateEq(patientInfo['birthDate'])]
            if patientInfo['sex']:
                cond.append(tableClient['sex'].eq(patientInfo['sex']))
            clientRecord = self._db.getRecordEx(tableClient, cols, cond)

        if clientRecord:
            return forceRef(clientRecord.value('id'))

        clientRecord = tableClient.newRecord()
        clientRecord.setValue('lastName', toVariant(patientInfo['lastName']))
        clientRecord.setValue('firstName', toVariant(patientInfo['firstName']))
        clientRecord.setValue('patrName', toVariant(patientInfo['patrName']))
        clientRecord.setValue('birthDate', toVariant(patientInfo['birthDate']))
        clientRecord.setValue('birthPlace', toVariant(patientInfo['birthPlace']))
        clientRecord.setValue('sex', toVariant(patientInfo['sex']))
        clientRecord.setValue('SNILS', toVariant(unformatSNILS(patientInfo['SNILS'])))
        clientId = self._db.insertRecord(tableClient, clientRecord)
        return clientId

    def loadRefBooks(self):
        self.loadPurposeCache()
        self.loadAidKindCache()
        self.loadResultCache()
        self.loadDiagnosticResultCache()
        self.loadUnitCache()
        self.loadLpuCache()

    def loadPurposeCache(self):
        self.loadRefBookCache('rbEventTypePurpose', 'federalCode', self._purposeCache)

    def loadAidKindCache(self):
        self.loadRefBookCache('rbMedicalAidKind', 'federalCode', self._aidKindCache)

    def loadResultCache(self):
        self.loadRefBookCache('rbResult', 'federalCode', self._resultCache)

    def loadDiagnosticResultCache(self):
        self.loadRefBookCache('rbDiagnosticResult', 'federalCode', self._diagnosticResultCache)

    def loadUnitCache(self):
        self.loadRefBookCache('rbMedicalAidUnit', 'federalCode', self._unitCache)

    def loadLpuCache(self):
        self.loadRefBookCache('Organisation', 'infisCode', self._lpuCache)

    def loadRefBookCache(self, tableName, keyField, cache):
        table = self._db.table(tableName)
        cond = [table[keyField].inlist(cache.keys())]
        recordList = self._db.getRecordList(table,
                                            [table.idField(), table[keyField]],
                                            cond)
        for record in recordList:
            key = forceStringEx(record.value(keyField))
            value = forceRef(record.value(table.idFieldName()))
            cache[key] = value

    def getEventType(self, purposeId, aidKindId):
        result = self._eventTypeCache.get((purposeId, aidKindId), None)
        if result is None:
            table = self._db.table('EventType')
            cond = [table['purpose_id'].eq(purposeId),
                    table['medicalAidKind_id'].eq(aidKindId)]
            record = self._db.getRecordEx(table, 'id', cond)
            if record:
                result = forceRef(record.value('id'))
                self._eventTypeCache[(purposeId, aidKindId)] = result

        return result


class CImportDialog(QtGui.QDialog):
    InitState = 0
    ImportState = 1

    def __init__(self, db, orgId, parent = None):
        super(CImportDialog, self).__init__(parent = parent)
        self._db = db
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._engine = CImportR85MTREngine(db, orgId, progressInformer=self._pi)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._loggerHandler.setLevel(logging.INFO)
        self._currentState = self.InitState

        self.setupUi()

        self.onStateChanged()


    def setParams(self, params):
        if isinstance(params, dict):
            fileName = forceStringEx(getPref(params, 'fileName', u''))
            if os.path.isdir(fileName):
                self.edtFileName.setText(fileName)


    def params(self):
        params = {}
        setPref(params, 'inputFile', forceStringEx(self.edtFileName.text()))
        return params


    @property
    def currentState(self):
        return self._currentState


    @currentState.setter
    def currentState(self, value):
        if value in [self.InitState, self.ImportState]:
            self._currentState = value
            self.onStateChanged()


    def onStateChanged(self):
        self.btnNextAction.setText(self._actionNames.get(self.currentState, u'<Error>'))
        self.btnClose.setEnabled(self.currentState != self.ImportState)
        self.gbInit.setEnabled(self.currentState == self.InitState)
        self.gbImport.setEnabled(self.currentState == self.ImportState)
        # self.btnSave.setEnabled(bool(self._engine.documents))
        QtCore.QCoreApplication.processEvents()


    # noinspection PyAttributeOutsideInit
    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        self.gbInit = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtFileName = QtGui.QLineEdit()
        self.edtFileName.setReadOnly(True)
        lineLayout.addWidget(self.edtFileName)
        self.btnBrowseFile = QtGui.QToolButton()
        self.btnBrowseFile.clicked.connect(self.onBrowseFileClicked)
        lineLayout.addWidget(self.btnBrowseFile)
        gbLayout.addLayout(lineLayout)
        self.gbInit.setLayout(gbLayout)
        layout.addWidget(self.gbInit)

        # import block
        self.gbImport = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        self.progressBar = CProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setRange(0, 0)
        self.progressBar.setProgressFormat(u'(%v/%m)')
        self._pi.progressChanged.connect(self.progressBar.setProgress)
        gbLayout.addWidget(self.progressBar)
        self.gbImport.setLayout(gbLayout)
        layout.addWidget(self.gbImport)

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


    # noinspection PyAttributeOutsideInit
    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Импорт. Крым. МежТер.', context))
        self.gbInit.setTitle(forceTr(u'Параметры импорта', context))

        self.gbImport.setTitle(forceTr(u'Импорт', context))

        self._actionNames = {self.InitState: forceTr(u'Импорт',context),
                             self.ImportState: forceTr(u'Прервать', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))


    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ImportState
            try:
                self._engine.process(forceStringEx(self.edtFileName.text()))
            except Exception, e:
                self.currentState = self.InitState
                raise
            self.currentState = self.InitState

        elif self.currentState == self.ImportState:
            self._engine.abort()
            self.currentState = self.InitState
        self.onStateChanged()


    def canClose(self):
        return True
        # not self._engine.documents or \
        #        QtGui.QMessageBox.warning(self,
        #                                  u'Внимание',
        #                                  u'Остались несохраненные файлы выгрузок,\n'
        #                                  u'которые будут утеряны.\n'
        #                                  u'Уверены, что хотить выйти из экспорта?\n',
        #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        #                                  QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes


    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()


    def done(self, result):
        if self.canClose():
            super(CImportDialog, self).done(result)



    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()


    @QtCore.pyqtSlot()
    def onBrowseFileClicked(self):
        fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                       u'Укажите директорию для сохранения файлов выгрузки',
                                                                       self.edtFileName.text()))
        if os.path.isfile(fileName):
            self.edtFileName.setText(fileName)




def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    isTestExport = False

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.3',
                      'port' : 3306,
                      'database' : 'crimea',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    if isTestExport:
        accountId = 248 #253
        w = CExportDialog(QtGui.qApp.db, accountId)
        w.show()
    else:
        e = CImportR85MTREngine(QtGui.qApp.db)
        e.processFile(u'/home/atronah/R2285152908.XML')

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()