# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil
import zipfile

from PyQt4 import QtCore, QtGui

from library.Utils     import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, toVariant, getVal, formatSNILS
from Exchange.Utils import CExportHelperMixin
from Exchange.ExportR53Native import CServiceInfoXmlStreamReader

from library.AmountToWords import amountToWords

from Ui_ExportR46XMLPage1 import Ui_ExportPage1
from Ui_ExportR46XMLPage2 import Ui_ExportPage2

# диагнозы


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'settleDate, number, exposeDate, contract_id, payer_id, date', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('settleDate'))
        aDate  = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        strNumber = forceString(accountRecord.value('number')).strip()
        if strNumber.isdigit():
            number = forceInt(strNumber)
        else:
            # убираем номер договора с дефисом, если они есть в номере
            i = len(strNumber) - 1
            while (i>0 and strNumber[i].isdigit()):
                i -= 1

            number = forceInt(strNumber[i+1:] if strNumber[i+1:] != '' else 0)

        contractId = forceRef(accountRecord.value('contract_id'))
        payerId = forceRef(accountRecord.value('payer_id'))
        recipientId = forceRef(accountRecord.value('recipient_id'))
    else:
        date = exposeDate = contractId = payerId = aDate = None
        number = 0
    return date, number, exposeDate, contractId,  payerId,  aDate


def exportR67XML(widget, accountId, accountItemIdList):
    wizard = CExportWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


# *****************************************************************************************


class CMyXmlStreamWriter(QtCore.QXmlStreamWriter, CExportHelperMixin):
    zglvFields  = {'VERSION': True, 'DATA': True, 'FILENAME' : True}
    schetFields = {'CODE': True, 'CODE_MO': True, 'YEAR': True, 'MONTH': True, 'NSCHET': True, 'DSCHET': True,
                   'PLAT': False, 'SUMMAV': True, 'COMENTS': False, 'SUMMAP': False, 'SANK_MEK': False,
                   'SANK_MEE': False, 'SANK_EKMP': False}
    zapFields   = {'N_ZAP': True, 'PR_NOV': True}
    pacientFields = {'ID_PAC': True, 'VPOLIS': True, 'SPOLIS': False, 'NPOLIS': True, 'ST_OKATO': False, 'SMO': False,
                     'SMO_OGRN': False, 'SMO_OK': False, 'SMO_NAM': False, 'NOVOR': True, 'VNOV_D': False}
    sluchFields = {'IDCASE': True, 'USL_OK': True, 'VIDPOM': True, 'FOR_POM': True, 'NPR_MO': False,
                   'EXTR': False, 'LPU': True, 'LPU_1': False, 'PODR': False, 'PROFIL': True, 'DET': True,
                   'NHISTORY': True, 'DATE_1': True, 'DATE_2': True, 'DS0': False, 'DS1': True, 'DS2': False,
                   'DS3': False, 'VNOV_M': False, 'CODE_MES1': False, 'CODE_MES2': False, 'RSLT': True, 'ISHOD': True,
                   'PRVS': True, 'VERS_SPEC': True, 'IDDOKT': True, 'OS_SLUCH': False, 'IDSP': True, 'ED_COL': False,
                   'TARIF': False, 'SUMV': True, 'OPLATA': False, 'SUMP': False, 'SANK_IT': False, 'COMENTSL': False}
    sankFields = {'S_CODE': True, 'S_SUM': True, 'S_TIP': True, 'S_OSN': True, 'S_COM': False, 'S_IST': True} # Нами не заполняется

    uslFields = {'IDSERV': True, 'LPU': True, 'LPU_1': False, 'PODR': False, 'PROFIL': True, #'VID_VME': False,
                 'DET': True, 'DATE_IN': True, 'DATE_OUT': True, 'DS': True, 'CODE_USL': True, 'KOL_USL': True,
                 'TARIF': True, 'SUMV_USL': True, 'PRVS': True, 'CODE_MD': True, 'COMENTU': False}

    groupMap = {'ZGLV': zglvFields, 'SCHET': schetFields, 'ZAP': zapFields, 'PACIENT': pacientFields,
                'SLUCH': sluchFields, 'USL': uslFields, 'SANK': sankFields}


    dispCodes = {
        0: u'ДВ1',
        1: u'ДВ2',
        2: u'ОПВ',
        3: u'ДС1',
        4: u'ДС2',
        5: u'ОН1',
        6: u'ОН2',
        7: u'ОН3'
    }

    def __init__(self, parent):
        QtCore.QXmlStreamWriter.__init__(self)
        CExportHelperMixin.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.recNum = 1
        self.caseNum = 1
        self.serviceNum = 1
        self._lastClientId = None
        self._lastEventId = None
        self.curGroupName = ''
        self.xmlErrorsList = []
        self.medicalAidProfileCache = {}
        self.clientStr = u''
        self.eventsInfo = {}
        self._isInMoving = False

    def setEventsInfo(self, eventsInfo):
        self.eventsInfo = eventsInfo

    def getProfile(self, serviceId, personId):
        key = (serviceId, personId)
        result = self.medicalAidProfileCache.get(key, -1)

        if result == -1:
            result = None
            stmt = """SELECT rbMedicalAidProfile.code
            FROM rbService_Profile
            LEFT JOIN rbSpeciality ON rbSpeciality.id = rbService_Profile.speciality_id
            LEFT JOIN Person ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN rbMedicalAidProfile ON rbService_Profile.medicalAidProfile_id = rbMedicalAidProfile.id
            WHERE rbService_Profile.master_id = %d AND Person.id = %d
            """ % (serviceId, personId)

            query = QtGui.qApp.db.query(stmt)

            if query and query.first():
                record = query.record()

                if record:
                    result = forceString(record.value(0))

            self.medicalAidProfileCache[key] = result

        return result

    def writeStartElement(self, str):
        self.curGroupName = str
        return QtCore.QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QtCore.QXmlStreamWriter.writeEndElement(self)


    def writeTextElement(self, element,  value, writeEmtpyTag = False):
        if self.groupMap.has_key(self.curGroupName):
            gr = self.groupMap[self.curGroupName]
            if gr.has_key(element):
                if not value:
                    if gr[element]:
                        self.xmlErrorsList.append(u'обязательное поле %s в группе %s не заполнено. Номер записи: %d, пациент: %s' % (element, self.curGroupName, self.recNum, self.clientStr))
                    return
            else:
                #self.xmlErrorsList.append(u'неизвестное поле %s = %s в группе %s. Номер записи: %d' % (element, value, self.curGroupName, self.recNum))
                return

        if not writeEmtpyTag and not value:
            return

        QtCore.QXmlStreamWriter.writeTextElement(self, element, value)

    def writeRecord(self, record, miacCode, idList, accDate, isStationaryRecord = False):
        clientId = forceRef(record.value('client_id'))
        littleId = forceRef(record.value('littleId'))
        self.clientStr = u'%s %s %s' % (forceString(record.value('lastName')), forceString(record.value('firstName')), forceString(record.value('patrName')))
        age = forceInt(record.value('clientAge'))
        months = forceInt(record.value('clientMonths'))
        specialCase = []

        if self._lastClientId != clientId: # новая запись, иначе - новый случай
            if self._lastEventId:
                #self.serviceNum = 1
                self.writeEndElement() # SLUCH
            self._lastEventId = None
            if self._lastClientId:
                self.recNum += 1
                self.writeEndElement() # ZAP

            self._lastClientId = clientId
            #self.caseNum = 1
            self.writeStartElement('ZAP')

            self.writeTextElement('N_ZAP', ('%4d' % self.recNum).strip())
            self.writeTextElement('PR_NOV', '1' if forceInt(record.value('rerun')) !=  0 else  '0')

            self.writeStartElement('PACIENT')
            self.writeTextElement('ID_PAC',  ('%d' % clientId)[:36])
            # Региональный код справочника ВИДЫ ПОЛИСОВ.
            self.writeTextElement('VPOLIS', forceString(record.value('policyKindFederalCode'))[:1])
            self.writeTextElement('SPOLIS', forceString(record.value(u'policySerial'))[:10])
            self.writeTextElement('NPOLIS', forceString(record.value(u'policyNumber'))[:20])
            if forceInt(record.value('policyKindFederalCode')) == 1:
                self.writeTextElement('ST_OKATO', forceString(record.value('insurerOKATO'))[:5] )
            if forceString(record.value('insurerMiac')) == '':
                   self.writeTextElement('SMO_OGRN', forceString(record.value('insurerOGRN'))[:15])
                   self.writeTextElement('SMO_OK', forceString(record.value('insurerOKATO'))[:5])
            else:
                  self.writeTextElement('SMO', '%s' % forceString(record.value('insurerMiac'))[:5]) #46
            self.writeTextElement('SMO_NAM', forceString(record.value('insurerName'))[:100], writeEmtpyTag = False)

            novor = '0'
            if littleId:
                birthDate = forceDate(record.value('littleBirthDate'))
                sex = forceString(record.value('littleSex'))[:1]
                if not sex:
                    self.xmlErrorsList.append(u'Не указан пол новорожденного для пациента %s' % clientId)
                number = forceInt(record.value('littleNumber'))
                novor = '%s%s%d' % (sex, birthDate.toString('ddMMyy'), number)

            self.writeTextElement('NOVOR', novor)
            weight = forceDouble(record.value('clientWeight'))
            if weight:
                self.writeTextElement('VNOV_D', forceString(weight)[:4])
            self.writeEndElement() # PACIENT

        #TODO check new SLUCH. new USL else new SLUCH

        serviceId = forceInt(record.value('service_id'))
        eventId = forceInt(record.value('event_id'))
        personId = forceRef(record.value('execPersonId'))
        profile = None
        if personId and serviceId:
            profile = self.getProfile(forceRef(record.value('serviceId')), personId)
        profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]
        price = forceDouble(record.value('price'))

        sum = forceDouble(record.value('sum'))
        ttype = forceInt(record.value('tariffType'))
        hasUsl = True #(ttype != 0 and ttype != 3)

        #FIXME: Изменения 28.08.2013 построены на допущении, что в стационарных обращениях в счета попадают только действия "Движение" (flatCode == moving).
        #В таком случае для каждого действия "движение" создается новая запись 'SLUCH'
        #FIXME: v2 - Предыдущий комментарий более не актуален. См. задачу 957.
        isMoving = forceString(record.value('flatCode')) == u'moving'
        if self._lastEventId != eventId or isMoving:
            self._isInMoving = isMoving
            if self._lastEventId:
                #self.serviceNum = 1
                self.writeEndElement() # SLUCH
            if self._lastEventId != eventId:
                self.currEventInfo = self.eventsInfo.get(eventId, {})
                self.movingCount = len(self.currEventInfo)
                self.multiMoving = self.movingCount > 1
            aiSum, aiAmount = self.currEventInfo.get(forceRef(record.value('action_id')), (0, 0))
            self._lastEventId = eventId

            self.writeStartElement('SLUCH')
            self.writeTextElement('IDCASE', '%d' % self.caseNum)
            # Федеральный код справочника НАЗНАЧЕНИЕ ТИПА СОБЫТИЯ
            serviceCode = forceString(record.value('medicalAidTypeFederalCode'))
            self.writeTextElement('USL_OK',  serviceCode)
            self.writeTextElement('VIDPOM', forceString(record.value('medicalAidKindFederalCode')))
            order = forceInt(record.value('order'))
            self.writeTextElement('FOR_POM', '1' if order == 2 else '2' if order == 5 else '3')
            # Вид и метод высокотехнологичной помощи
            self.writeTextElement('VID_HMP', forceString(record.value('hmpKindCode')))
            self.writeTextElement('METOD_HMP', forceString(record.value('hmpMethodCode')))

            #self.writeTextElement('NPR_MO','')
            # 1 – плановая; 2 – экстренная ИЗ СОБЫТИЯ
            self.writeTextElement('EXTR', '2' if forceInt(record.value('order')) == 2 else '1')
            #У N(8) Код отделения Отделение МО лечения из регионального справочника
            self.writeTextElement('LPU', '%s' % miacCode[:6]) #460
            self.writeTextElement('PODR', forceString(record.value('orgStructureCode')))

            self.writeTextElement('PROFIL', profileStr) #forceString(record.value('medicalAidProfileFederalCode'))[:3]
            self.writeTextElement('DET', (u'1' if age < 18 else u'0'))

            extId = forceString(record.value('externalId'))
            regId = forceString(record.value('regId'))

            nhistory = forceString(eventId)
            if serviceCode == '3':
                if regId:
                    nhistory = regId
                elif extId != '':
                    nhistory = extId
            elif extId != '':
                nhistory = extId

            self.writeTextElement('NHISTORY', nhistory)
            # Дата начала события
            self.writeTextElement('DATE_1', forceDate(record.value('begDate' if not self.multiMoving else 'uslBegDate')).toString(QtCore.Qt.ISODate))
            # Дата окончания события
            #if self.movingCount < 2:
            dd = forceDate(record.value('endDate' if not self.multiMoving else 'uslEndDate'))
            if dd > accDate:
                dd = accDate
            #else:
            #    dd = forceDate(record.value('uslBegDate'))

            self.writeTextElement('DATE_2', dd.toString(QtCore.Qt.ISODate))
            self.writeTextElement('DS1', forceString(record.value('MKB')))
            self.writeTextElement('DS2', forceString(record.value('AccMKB')))
            self.writeTextElement('DS3', forceString(record.value('CompMKB')))

            #TODO: VNOV_M / Вес при рождении, если пациент - мать
            self.writeTextElement('CODE_MES1', forceString(record.value('mesCode')))

            rslt = forceString(record.value('eventResultFederalCode'))
            rslt_d = forceString(record.value('eventResultRegionalCode'))
            purpose = forceInt(record.value('purposeId'))
            ishod = forceString(record.value('resultFederalCode'))

            db = QtGui.qApp.db
            table = db.table('rbResult')
            eventpurposes = []
            eventpurposeslist = db.getRecordList(table, 'federalCode', 'eventPurpose_id = %d' % purpose)
            for ep in eventpurposeslist:
                eventpurposes.append(forceString(ep.value('federalCode')))

            if self.movingCount <= 1:
                if not rslt in eventpurposes:
                    bFind = False
                    for rs in eventpurposes:
                        if rs[-1:] == rslt[-1:]:
                            bFind = True
                            rslt = rs
                            break
                    if not bFind:
                        rslt = None
            else:
                rslt = '104' # Переведен на другой профиль коек

            self.writeTextElement('RSLT', forceString(rslt))
            self.writeTextElement('RSLT_D', forceString(rslt_d))

            # Федеральный код из справочника РЕЗУЛЬТАТ ОСМОТРА. Результат ЗАКЛЮЧИТЕЛЬНОГО ДИАГНОЗА.

            table = db.table('rbDiagnosticResult')
            eventpurposes = []
            eventpurposeslist = db.getRecordList(table, 'federalCode', 'eventPurpose_id = %d' % purpose)
            for ep in eventpurposeslist:
                eventpurposes.append(forceString(ep.value('federalCode')))

            if self.movingCount <= 1:
                if not ishod in eventpurposes:
                    bFind = False
                    for ish in eventpurposes:
                        if ish[-1:] == ishod[-1:]:
                            bFind = True
                            ishod = ish
                            break
                    if not bFind:
                        ishod = None
            else:
                ishod = '103' # Без перемен

            self.writeTextElement('ISHOD', forceString(ishod))

            self.writeTextElement('PRVS', forceString(self.parent.getSpecialityFederalCode(personId)))
            self.writeTextElement('VERS_SPEC', 'V015')
            self.writeTextElement('IDDOKT', forceString(self.parent.getPersonFederalCode(personId)))
            if forceBool(record.value('littleMultipleBirths')):
                self.writeTextElement('OS_SLUCH', '1')
            if forceString(record.value('patrName')) == u'':
                self.writeTextElement('OS_SLUCH', '2')

            idsp = forceInt(record.value('medicalAidUnitFederalCode'))

            if idsp == 61:
                self.writeTextElement('OS_SLUCH', '3')

            if idsp == 62:
                self.writeTextElement('OS_SLUCH', '4')

            #if forceInt(record.value('isStac')) == 1 and forceDouble(record.value('amount')) * price < sum:
            #    print 'idsp', idsp
            #    idsp = idsp - 13

            self.writeTextElement('IDSP', forceString(idsp))

            self.writeTextElement('ED_COL', forceString(record.value('evamount') if not self.multiMoving else aiAmount))

            if not hasUsl:
                self.writeTextElement('TARIF', ('%.2f' % price))

            if isStationaryRecord and not self._isInMoving:
                sumv = 0
                self.xmlErrorsList.append(u'Для обращения с идентификатором %s поле SUMV = 0.' % eventId)
            else:
                sumv = forceDouble(record.value('evsum') if not self.multiMoving else aiSum)
            self.writeTextElement('SUMV', ('%.2f' % sumv))

            self.writeTextElement('OPLATA', forceString(record.value('OPLATA')))

            self.writeTextElement('SUMP', ('%.2f' % forceDouble(record.value('evsum') if not self.multiMoving else aiSum)))

            # Работа со словарем данных о предварительном реестре
            visitId = forceInt(record.value('visit_id'))
            actionId = forceInt(record.value('action_id'))
            key = (eventId, serviceId, visitId, actionId)
            (pAccNum, pAccDate, pRecNum) = self.parent.preliminaryRegistryInfo.get(key, ('', '', ''))
            self.caseNum+= 1

            federalSum = forceDouble(record.value('federalSum'))
            federalPrice = forceDouble(record.value('federalPrice'))
            self.movingCount -= 1

        if hasUsl:
            codeUsl = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'code'))
            self.writeService(record, miacCode, age, price, sum, codeUsl, profileStr)


    def writeService(self, record, miacCode, age, price, sum, code, profileStr):
        serviceId = forceRef(record.value('serviceId'))
        self.writeStartElement('USL')
        self.writeTextElement('IDSERV',  ('%d' % self.serviceNum).strip()) # O N(8) номер записи в реестре услуг
        self.writeTextElement('LPU', '%s' % miacCode[:6]) #O Т(6) Код МО МО лечения #460
        #self.writeTextElement('LPU_1', forceString(record.value('orgStructureCode'), writeEmtpyTag = False) #У Т(6) Подразделение МО Подразделение МО лечения из регионального справочника
        self.writeTextElement('PODR', forceString(record.value('orgStructureCode')), writeEmtpyTag = False) #У N(8) Код отделения Отделение МО лечения из регионального справочника
        self.writeTextElement('PROFIL', profileStr) #O N(3) Профиль Классификатор V002
        #self.writeTextElement('VID_VME', code[:15]) # Вид медицинского вмешательства в соответствии с номенклатурой медицинских услуг V001
        self.writeTextElement('DET', (u'1' if age < 18 else u'0')) #О N(1) Признак детского профиля 0-нет, 1-да.
        self.writeTextElement('DATE_IN', forceDate(record.value('uslBegDate')).toString(QtCore.Qt.ISODate)) #O D Дата начала оказания услуги
        self.writeTextElement('DATE_OUT', forceDate(record.value('uslEndDate')).toString(QtCore.Qt.ISODate)) #O D Дата окончания оказания услуги
        self.writeTextElement('DS', forceString(record.value('USLMKB'))) #O Т(10) Диагноз Код из справочника МКБ до уровня подрубрики
        self.writeTextElement('CODE_USL', code) #O Т(16) Код услуги Территориальный классификатор услуг

        amount = forceDouble(record.value('amount'))

        self.writeTextElement('KOL_USL', ('%.2f' % amount)) #O N(6.2) Количество услуг (кратность услуги)

        tarifftype = forceInt(record.value('tariffType'))
        tarifffrag1 = forceInt(record.value('tariffFrag1'))
        frag1Sum = forceDouble(record.value('frag1Sum'))
        tariffUnitId = forceInt(record.value('tariffUnitId'))

        tariff = price
        if tarifftype == 6: # and amount >= tarifffrag1
            if tariffUnitId == 6 or tariffUnitId == 7:
                tariff = sum/amount
            else:
                tariff = frag1Sum

        self.writeTextElement('TARIF', ('%.2f' % tariff)) #O N(15.2) Тариф
        self.writeTextElement('SUMV_USL', ('%.2f' % sum)) #O N(15.2) Стоимость медицинской услуги, выставленная к оплате (руб.)
        self.writeTextElement('PRVS', forceString(self.parent.getSpecialityFederalCode(forceRef(record.value('execPersonId'))))) #O N(9) Специальность медработника, выполнившего услугу
        self.writeTextElement('CODE_MD', forceString(self.parent.getPersonFederalCode(forceRef(record.value('execPersonId'))))) #O Т(16) Код медицинского работника, оказавшего медицинскую услугу В соответствии с территориальным справочником
        self.writeEndElement() #USL
        self.serviceNum += 1


    def writeFileHeader(self,  device, fileName, accNumber, accDate, year, month, miacCode, payerCode, accSum=0.0, dispType = None):
        self._lastClientId = None
        self._lastEventId = None
        self.recNum = 1
        self.caseNum = 1
        self.serviceNum = 1
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('ZL_LIST')
        self.writeHeader(fileName, accNumber, accDate, year, month, miacCode, payerCode, accSum, dispType)


    def writeHeader(self, fileName, accNumber, accDate, year, month, miacCode, payerCode, accSum, dispType = None):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '2.1')
        self.writeTextElement('DATA', accDate.toString(QtCore.Qt.ISODate))
        (fname,  ext) = os.path.splitext(os.path.basename(fileName))
        self.writeTextElement('FILENAME', fname[:26])
        self.writeEndElement()
        self.writeStartElement('SCHET')
        self.writeTextElement('CODE', ('%s%s' % (miacCode, accNumber))[:8]) #46
        self.writeTextElement('CODE_MO',  u'%s' % miacCode) #460
        self.writeTextElement('YEAR', year)
        self.writeTextElement('MONTH',  month)
        self.writeTextElement('NSCHET',  forceString(accNumber))
        self.writeTextElement('DSCHET', accDate.toString(QtCore.Qt.ISODate))
        self.writeTextElement('PLAT', '%s' % payerCode[:5], writeEmtpyTag = False) #46
        self.writeTextElement('SUMMAV', ('%.2f' % accSum))
        self.writeTextElement('DISP', self.dispCodes.get(dispType, None))
        self.writeEndElement()


    def writeFileFooter(self):
        self.writeEndElement() # root
        self.writeEndDocument()

class CDispXmlStreamWriter(CMyXmlStreamWriter):
    zglvFields  = {'VERSION': True, 'DATA': True, 'FILENAME' : True}
    schetFields = {'CODE': True, 'CODE_MO': True, 'YEAR': True, 'MONTH': True, 'NSCHET': True, 'DSCHET': True,
                   'PLAT': False, 'SUMMAV': True, 'COMENTS': False, 'SUMMAP': False, 'SANK_MEK': False,
                   'SANK_MEE': False, 'SANK_EKMP': False, 'DISP': False}
    zapFields   = {'N_ZAP': True, 'PR_NOV': True}
    pacientFields = {'ID_PAC': True, 'VPOLIS': True, 'SPOLIS': False, 'NPOLIS': True, 'ST_OKATO': False, 'SMO': False,
                     'SMO_OGRN': False, 'SMO_OK': False, 'SMO_NAM': False}
    sluchFields = {'IDCASE': True, 'VIDPOM': True, 'LPU': True, 'LPU_1': False,
                   'NHISTORY': True, 'DATE_1': True, 'DATE_2': True, 'DS1': True, 'RSLT_D': True, 'IDSP': True,
                   'ED_COL': False, 'TARIF': False, 'SUMV': True, 'OPLATA': False, 'SUMP': False, 'SANK_IT': False,
                   'COMENTSL': False}
    sankFields = {'S_CODE': True, 'S_SUM': True, 'S_TIP': True, 'S_OSN': True, 'S_COM': False, 'S_IST': True} # Нами не заполняется

    uslFields = {'IDSERV': True, 'LPU': True, 'LPU_1': False, 'DATE_IN': True, 'DATE_OUT': True, 'CODE_USL': True,
                 'TARIF': True, 'SUMV_USL': True, 'PRVS': True, 'CODE_MD': True, 'COMENTU': False }

    groupMap = {'ZGLV': zglvFields, 'SCHET': schetFields, 'ZAP': zapFields, 'PACIENT': pacientFields,
                'SLUCH': sluchFields, 'USL': uslFields, 'SANK': sankFields}

class CHighTechXmlStreamWriter(CMyXmlStreamWriter):
    ## SLIUCH: vid_hmp,
    zglvFields  = {'VERSION': True, 'DATA': True, 'FILENAME' : True}
    schetFields = {'CODE': True, 'CODE_MO': True, 'YEAR': True, 'MONTH': True, 'NSCHET': True, 'DSCHET': True,
                   'PLAT': False, 'SUMMAV': True, 'COMENTS': False, 'SUMMAP': False, 'SANK_MEK': False,
                   'SANK_MEE': False, 'SANK_EKMP': False}
    zapFields   = {'N_ZAP': True, 'PR_NOV': True}
    pacientFields = {'ID_PAC': True, 'VPOLIS': True, 'SPOLIS': False, 'NPOLIS': True, 'ST_OKATO': False, 'SMO': False,
                     'SMO_OGRN': False, 'SMO_OK': False, 'SMO_NAM': False, 'NOVOR': True, 'VNOV_D': False}
    sluchFields = {'IDCASE': True, 'USL_OK': True, 'VIDPOM': True, 'FOR_POM': True, 'VID_HMP': True, 'METOD_HMP': True, 'NPR_MO': False,
                   'EXTR': False, 'LPU': True, 'LPU_1': False, 'PODR': False, 'PROFIL': True, 'DET': True,
                   'NHISTORY': True, 'DATE_1': True, 'DATE_2': True, 'DS0': False, 'DS1': True, 'DS2': False,
                   'DS3': False, 'VNOV_M': False, 'CODE_MES1': False, 'CODE_MES2': False, 'RSLT': True, 'ISHOD': True,
                   'PRVS': True, 'VERS_SPEC': True, 'IDDOKT': True, 'OS_SLUCH': False, 'IDSP': True, 'ED_COL': False,
                   'TARIF': False, 'SUMV': True, 'OPLATA': False, 'SUMP': False, 'SANK_IT': False, 'COMENTSL': False}
    sankFields = {'S_CODE': True, 'S_SUM': True, 'S_TIP': True, 'S_OSN': True, 'S_COM': False, 'S_IST': True} # Нами не заполняется

    uslFields = {'IDSERV': True, 'LPU': True, 'LPU_1': False, 'PODR': False, 'PROFIL': True, #'VID_VME': False,
                 'DET': True, 'DATE_IN': True, 'DATE_OUT': True, 'DS': True, 'CODE_USL': True, 'KOL_USL': True,
                 'TARIF': True, 'SUMV_USL': True, 'PRVS': True, 'CODE_MD': True, 'COMENTU': False}

    groupMap = {'ZGLV': zglvFields, 'SCHET': schetFields, 'ZAP': zapFields, 'PACIENT': pacientFields,
                'SLUCH': sluchFields, 'USL': uslFields, 'SANK': sankFields}

# *****************************************************************************************

class CPersonalDataStreamWriter(QtCore.QXmlStreamWriter):
    persZglvFields = {'VERSION': True, 'DATA': True, 'FILENAME' : True, 'FILENAME1' : True}
    persFields = {'ID_PAC': True, 'FAM': True, 'IM': True, 'OT': True, 'W': True, 'DR': True, 'DOST': False,
                  'FAM_P': False, 'IM_P': False, 'OT_P': False, 'W_P': False, 'DR_P': False, 'DOST_P': False,
                  'MR': False, 'DOCTYPE': False, 'DOCSER': False, 'DOCNUM': False, 'SNILS': False,
                        'OKATOG': False, 'OKATOP': False, 'COMENTP': False, 'COMENTZ': False}
    groupMap = {'ZGLV': persZglvFields, 'PERS': persFields}

    def __init__(self, parent):
        QtCore.QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._clientsSet = None
        self.xmlErrorsList = []
        self.clientStr = u''


    def writeStartElement(self, str):
        self.curGroupName = str
        return QtCore.QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QtCore.QXmlStreamWriter.writeEndElement(self)


    def writeTextElement(self, element,  value, writeEmtpyTag = False):
        if self.groupMap.has_key(self.curGroupName):
            gr = self.groupMap[self.curGroupName]
            if gr.has_key(element):
                if gr[element] and (not value or value == ''):
                    self.xmlErrorsList.append(u'обязательное поле %s в группе %s не заполнено. Ид пациента: %s, пациент: %s' % (element, self.curGroupName, forceString(self.clientId), self.clientStr))
                    return
                elif (not value or value == ''):
                    return
            else:
                self.xmlErrorsList.append(u'неизвестное поле %s = %s в группе %s. Ид пациента: %s' % (element, value, self.curGroupName, forceString(self.clientId)))

        if not writeEmtpyTag and (not value or value == ''):
            return

        QtCore.QXmlStreamWriter.writeTextElement(self, element, value)


    def writeRecord(self, record):
        self.clientId = forceRef(record.value('client_id'))
        self.clientStr = u'%s %s %s' % (forceString(record.value('lastName')), forceString(record.value('firstName')), forceString(record.value('patrName')))
        sex = forceString(record.value('sex'))
        birthDate = forceDate(record.value('birthDate'))
        littleId = forceRef(record.value('littleId'))

        if (self.clientId, littleId) in self._clientsSet:
            return

        self.writeStartElement('PERS')
        self.writeTextElement('ID_PAC',  ('%d' % self.clientId)[:36])

        lastName = forceString(record.value('lastName'))
        firstName = forceString(record.value('firstName'))
        patrName = forceString(record.value('patrName'))
        if lastName.upper() == u'НЕТ':
            lastName = u''
        if firstName.upper() == u'НЕТ':
            firstName = u''
        if patrName.upper() == u'НЕТ':
            patrName = u''
        ln = lastName
        fn = firstName
        ot = patrName

        sexData = sex
        birthDateData = birthDate

        if littleId:
            ln = u''
            fn = u''
            ot = u''
            sexData = forceString(record.value('littleSex'))
            if not sex:
                self.xmlErrorsList.append(u'Не указан пол новорожденного для пациента %s' % self.clientId)
            birthDateData = forceDate(record.value('littleBirthDate'))

        #Фамилия пациента.
        if ln:
            self.writeTextElement('FAM', ln)
        #Имя пациента
        if fn:
            self.writeTextElement('IM', fn)
        #Отчество пациента
        if ot:
            self.writeTextElement('OT', ot)

        #Пол пациента.
        self.writeTextElement('W', sexData)
        #Дата рождения пациента.
        self.writeTextElement('DR', birthDateData.toString(QtCore.Qt.ISODate))
        # Код надежности идентификации пациента. Поле может повторяться несколько раз.
        # 1 - Не указано отчество
        # 2 - Не указана фамилия
        # 3 - Не указано имя
        # 4 - Известны месяц и год рождения
        # 5 - Известен только год рождения
        # 6 - Дата рождения не соответствует календарю.
        if not ot:
            self.writeTextElement('DOST', '1')
        if not ln:
            self.writeTextElement('DOST', '2')
        if not fn:
            self.writeTextElement('DOST', '3')
        if not birthDateData.isValid():
            self.writeTextElement('DOST', '6')

        if littleId:
            #Фамилия пациента.
            if lastName:
                self.writeTextElement('FAM_P', lastName)
            #Имя пациента
            if firstName:
                self.writeTextElement('IM_P', firstName)
            #Отчество пациента
            if patrName:
                self.writeTextElement('OT_P', patrName)

            self.writeTextElement('W_P', sex)

            self.writeTextElement('DR_P', birthDate.toString(QtCore.Qt.ISODate))
            if not patrName:
                self.writeTextElement('DOST', '1')
            if not lastName:
                self.writeTextElement('DOST', '2')
            if not firstName:
                self.writeTextElement('DOST', '3')
            if not birthDate.isValid():
                self.writeTextElement('DOST', '6')

        self.writeTextElement('MR', forceString(record.value('birthPlace')), writeEmtpyTag=False)
        # Федеральный код из справочника ТИПЫ ДОКУМЕНТОВ. Из карточки пациента.
        self.writeTextElement('DOCTYPE',  forceString(record.value('documentFederalCode')))
        # Серия документа, удо-стоверяющего личность пациента.
        self.writeTextElement('DOCSER', forceString(record.value('documentSerial')))
        # Номер документа, удостоверяющего личность пациента.
        self.writeTextElement('DOCNUM', forceString(record.value('documentNumber')))
        # СНИЛС пациента.
        self.writeTextElement('SNILS', formatSNILS(forceString(record.value('SNILS'))))
        # Код места жительства по ОКАТО. Берётся из адреса жительство.
        self.writeTextElement('OKATOG', forceString(record.value('placeOKATO')))
        # Код места пребывания по ОКАТО. Берётся из ОКАТО организации, чей полис у пациента.
        self.writeTextElement('OKATOP', forceString(record.value('insurerOKATO')))
        self.writeEndElement() # PERS
        self._clientsSet.add((self.clientId, littleId))


    def writeFileHeader(self,  device, fileName, accDate):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('PERS_LIST')
        self.writeHeader(fileName, accDate)


    def writeHeader(self, fileName, accDate):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '2.1')
        self.writeTextElement('DATA', accDate.toString(QtCore.Qt.ISODate))
        (fname,  ext) = os.path.splitext(os.path.basename(fileName))
        self.writeTextElement('FILENAME', 'L%s' % fname[1:26])
        self.writeTextElement('FILENAME1', fname[:26])
        self.writeEndElement()

    def writeFileFooter(self):
        self.writeEndElement() # root
        self.writeEndDocument()

# *****************************************************************************************

class CExportWizard(QtGui.QWizard):
    outPrefixes = {
        0: 'H',  # Все, что не попало в другие категории
        1: 'DP', # Диспансеризация взрослого населения, первый этап (et: dd2013_1, ДДвет),
        2: 'DV', # Диспансеризация взрослого населения, второй этап (et: dd2013_2),
        3: 'DO', # Профилактические осмотры взрослого населения (et: ПрофОсм),
        4: 'DS', # Диспансеризация пребывающих в стационарных учреждениях детей-сирот и детей, находящихся в трудной жизненной ситуации, (et: ДДСирТЖС)
        5: 'DU', # Диспансеризация детей-сирот и детей, оставшихся без попечения родителей, в том числе усыновленных, принятых под опеку (попечительство), в приемную или патронатную семью, (et: ДДСирот)
        6: 'DF', # Медицинские осмотры несовершеннолетних (профилактические), (et: ОсмДо18)
        7: 'DD', # Медицинские осмотры несовершеннолетних (предварительные),
        8: 'DR', # Медицинские осмотры несовершеннолетних (периодические),
        9: 'T',  # Высокотехнологичная медицинская помощь
    }

    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта в Смоленской области')
        self.tmpDir = ''
        self.xmlBaseLocalFileName = ''
        self.dispOutFiles = []
        self.outFiles = []
        self.isOutFileEmpty = [True] * len(self.outPrefixes)
        self._mapTypeToOutFile = {}

    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId, payerId,  aDate = getAccountInfo(accountId)
        strNumber = number if forceStringEx(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page1.setContractId(contractId, aDate, date)
        self.page2.setTitle(u'Укажите директорию для сохранения обменных файлов')


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QtCore.QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R67XML')
        return self.tmpDir


    def getBaseXmlFileName(self):
        u"""HPiNiPpNp_YYMMN.XML, где
            H – константа, обозначающая передаваемые данные.
            Pi – Параметр, определяющий организацию-источник:
            T – ТФОМС;
            S – СМО;
            M – МО. 	-	в нашем случаи M
            Ni – Номер источника (Код МИАЦ ЛПУ).
            Pp – Параметр, определяющий организацию -получателя:
            T – ТФОМС;
            S – СМО;
            M – МО	в нашем случаи S
            Np – Номер получателя (Код МИАЦ СМО).
            YY – две последние цифры порядкового номера года отчетного периода.
            MM – порядковый номер месяца отчетного периода - из даты на которую формируется счёт.
            N – порядковый номер пакета. Присваивается в порядке возрастания, начиная со значения «1»,
            увеличиваясь на единицу для каждого следующего пакета в данном отчетном периоде."""
        if not self.xmlBaseLocalFileName:
            lpuInfis = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))
#            orgStructCode = forceString(QtGui.qApp.db.translate(
#                'OrgStructure', 'id', QtGui.qApp.currentOrgStructureId(), 'infisCode'))
            (date, number, exposeDate, contractId,  payerId,  aDate) = getAccountInfo(self.accountId)

            payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'miacCode'))

            self.xmlBaseLocalFileName = \
                u'M%sS%s_%s%d.xml' % (lpuInfis, payerCode, date.toString('yyMM'), self.page1.edtRegistryNumber.value())
        return self.xmlBaseLocalFileName

    #def getFullXmlFileName(self, outType):
    #    prefix = self.outPrefixes.get(outType, outType)
    #    return os.path.join(self.getTmpDir(), u'%s%s' % (prefix, self.getBaseXmlFileName()))

    def getFullXmlPersFileName(self):
        return os.path.join(self.getTmpDir(), u'L%s' % os.path.basename(self.getFullXmlFileName())[1:])

    def getFullXmlFileName(self, type=0):
        prefix = self.outPrefixes.get(type, type)
        return os.path.join(self.getTmpDir(), u'%s%s' % (prefix, self.getBaseXmlFileName()))

    def setAccountItemsIdList(self, accountItemIdList):
        self.page1.setAccountItemsIdList(accountItemIdList)


    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''

    def setNotEmptyOuts(self, outFileEmptyList):
        self.isOutFileEmpty = outFileEmptyList

    def getNotEmptyOuts(self):
        return self.isOutFileEmpty

    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()

# *****************************************************************************************

class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1, CExportHelperMixin):
    sexMap = {1: u'М',  2: u'Ж'}
    maxPageLines = 62

    outEventTypes = {
        u'dd2013_1': 1,
        u'ДДвет': 1,
        u'dd2013_2': 2,
        u'ПрофОсм': 3,
        u'ДДСирТЖС': 4,
        u'ДДСирот': 5,
        u'ОсмДо18': 6
    }

    outMedicalAidKinds = {
        u'32': 9,
    }

    writerTypes = {
        0: CMyXmlStreamWriter,
        1: CDispXmlStreamWriter,
        2: CDispXmlStreamWriter,
        3: CDispXmlStreamWriter,
        4: CDispXmlStreamWriter,
        5: CDispXmlStreamWriter,
        6: CDispXmlStreamWriter,
        7: CDispXmlStreamWriter,
        8: CDispXmlStreamWriter,
        9: CHighTechXmlStreamWriter,
    }

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        CExportHelperMixin.__init__(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.appendixStr = QtCore.QString(u"")
        self.appendixStream =  QtCore.QTextStream(self.appendixStr)
        self.appendixStream.setCodec('CP866')

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.parent = parent
        self.recNum= 0
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR46XMLIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR46XMLVerboseLog', False)))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.edtRegistryNumber.setValue(forceInt(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR46XMLRegistryNumber', 0))+1)
        self.chkGroupByService.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR46XMLGroupByService', False)))
        self.edtServiceInfoFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR46XMLServiceInfoFileName', '')))
        self.chkIgnoreErrors.setVisible(False)
        self.chkIgnoreErrors.setChecked(True)
        self.chkGroupByService.setVisible(False)
        self.chkVerboseLog.setVisible(False)
        self.edtServiceInfoFileName.setVisible(False)
        #self.edtRegistryNumber.setVisible(False)
        #self.lblRegistryNumber.setVisible(False)
        self.lblServiceInfoFileName.setVisible(False)
        self.btnSelectServiceInfoFileName.setVisible(False)
        self.isOutFileEmpty = []


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.edtRegistryNumber.setEnabled(not flag)
        self.chkGroupByService.setEnabled(not flag)


    def log(self, str, forceLog = True):
        if self.chkVerboseLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList

    def setContractId(self, cId, accD, setD):
        self.contractId = cId
        self.accDate = accD
        self.settleDate = setD

    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        outputFiles, clientOutput = self.createXML()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        stacQuery = self.createQuery(stac=True)
        serviceQuery = self.createServiceQuery()
        self.progressBar.setMaximum(max(query.size() + serviceQuery.size() + stacQuery.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.isOutFileEmpty = [True] * len(outputFiles)
        return outputFiles, query, stacQuery, serviceQuery, clientOutput


    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            QtGui.qApp.preferences.appPrefs['ExportR46XMLIgnoreErrors'] = \
                    toVariant(self.chkIgnoreErrors.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR46XMLVerboseLog'] = \
                    toVariant(self.chkVerboseLog.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR46XMLGroupByService'] = \
                    toVariant(self.chkGroupByService.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR46XMLServiceInfoFileName'] = \
                    toVariant(self.edtServiceInfoFileName.text())
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


# *****************************************************************************************

    def getPreliminaryInfo(self):
        u"""Загрузка информации о предварительном реестре из XML"""

        if self.edtServiceInfoFileName.text().isEmpty():
            return {}

        inFile = QtCore.QFile(self.edtServiceInfoFileName.text())
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных о предварительном реестре счета',
                                      QtCore.QString(u'Не могу открыть файл для чтения %1:\n%2.')
                                      .arg(self.edtServiceInfoFileName.text())
                                      .arg(inFile.errorString()))
            return {}

        myXmlStreamReader = CServiceInfoXmlStreamReader(self, self.chkVerboseLog.isChecked())
        if (not myXmlStreamReader.readFile(inFile)):
            if self.aborted:
                self.log(u'! Прервано пользователем.')
            else:
                self.log(u'! Ошибка: файл %s, %s' % (self.edtServiceInfoFileName.text(), myXmlStreamReader.errorString()))

        return myXmlStreamReader.registryInfo

# *****************************************************************************************

    def getTxtFileName(self):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
        return forceString(lpuCode + u'.TXT')

    def createTxt(self):
        txt = QtCore.QFile(os.path.join(self.parent.getTmpDir(), self.getTxtFileName()))
        txt.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)
        txtStream =  QtCore.QTextStream(txt)
        txtStream.setCodec('CP866')
        return txt,  txtStream

    def createQuery(self, stac=False):
        accDate, accNumber, exposeDate, contractId,  payerId, aDate =\
            getAccountInfo(self.parent.accountId)

        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        cond = []

        matList = ['1', '7'] # 1 - стационарная помощь, 7 - дневной стационар
        tableRBMedicalAidType = db.table('rbMedicalAidType')

        if stac:
            order = 'client_id, event_id, DATE(Action.begDate) ASC, DATE(Action.endDate) DESC, ActionType.flatCode = "moving" DESC'
            cond.append(tableRBMedicalAidType['code'].inlist(matList))
        else:
            order = 'client_id, event_id, Account_Item.sum DESC, Action.id'
            cond.append(tableRBMedicalAidType['code'].notInlist(matList))

        cond.append(tableAccountItem['id'].inlist(self.idList))
        cond = db.joinAnd(cond)

        sumStr = """Account_Item.`sum` AS `sum`,
                Account_Item.amount AS amount,
                 LEAST(IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                            Account_Item.sum) AS federalSum,"""


        stmt = """SELECT
                Account_Item.id AS accountItemId,
                Account_Item.event_id  AS event_id,
                Account_Item.visit_id,
                Account_Item.action_id,
                Account_Item.service_id,
                IF(Account_Item.refuseType_id IS NOT NULL, 0, 1) AS OPLATA,
                CAST(if(Event.littleStranger_id is not null, 
                     concat(Event.client_id, Date_format(Event_LittleStranger.birthDate, '%%d%%m%%y'), Event_LittleStranger.sex, Event_LittleStranger.currentNumber), Event.client_id) AS UNSIGNED) AS client_id,
                Client.lastName,
                Client.firstName,
                Client.patrName,
                Client.birthDate       AS birthDate,
                Client.sex AS sex,
                Client.SNILS AS SNILS,
                Client.weight AS clientWeight,
                Client.birthPlace AS birthPlace,
                Event.externalId       AS externalId,
                age(Client.birthDate, Event.execDate) as clientAge,
                timestampdiff(MONTH, Client.birthDate, Event.execDate) AS clientMonths,
                ClientPolicy.serial AS policySerial,
                ClientPolicy.number AS policyNumber,
                ClientPolicy.begDate   AS policyBegDate,
                ClientPolicy.endDate   AS policyEndDate,
                rbPolicyKind.federalCode AS policyKindFederalCode,
                Insurer.OGRN AS insurerOGRN,
                Insurer.OKATO AS insurerOKATO,
                Insurer.area AS insurerArea,
                Insurer.miacCode AS insurerMiac,
                ClientDocument.serial  AS documentSerial,
                ClientDocument.number  AS documentNumber,
                rbDocumentType.federalCode AS documentFederalCode,
                kladr.KLADR.OCATD AS placeOKATO,
                IF(Account_Item.visit_id IS NOT NULL, Visit.person_id,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, Action.person_id, Action.setPerson_id), Event.execPerson_id)
                ) AS execPersonId,
                Diagnosis.MKB AS MKB,
                IF(Action.MKB <> '', Action.MKB, Diagnosis.MKB)  AS USLMKB,
                Event.setDate          AS begDate,
                Event.execDate         AS endDate,
                DATE(if(Account_Item.visit_id IS NOT NULL, Visit.date, if(Account_Item.action_id IS NOT NULL, Action.begDate, Event.setDate))) AS uslBegDate,
                DATE(if(Account_Item.visit_id IS NOT NULL, Visit.date, if(Account_Item.action_id IS NOT NULL, Action.endDate, Event.execDate))) AS uslEndDate,
                Contract_Tariff.federalPrice AS federalPrice,
                Contract_Tariff.price AS price, %s
                Contract_Tariff.tariffType  AS tariffType,
                Contract_Tariff.frag1Start  AS tariffFrag1,
                Contract_Tariff.frag1Sum    AS frag1Sum,
                Contract_Tariff.unit_id     AS tariffUnitId,
                rbDiagnosticResult.federalCode AS resultFederalCode,
                rbMedicalAidType.federalCode AS medicalAidTypeFederalCode,
                rbMedicalAidKind.federalCode AS medicalAidKindFederalCode,
                IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.federalCode,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.federalCode, EventMedicalAidProfile.regionalCode)
                  ) AS medicalAidProfileFederalCode,
                IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.id,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.id, rbEventService.id)
                    ) AS serviceId,
                AccDiagnosis.MKB AS AccMKB,
                CompDiagnosis.MKB AS CompMKB,
                OrgStructure.infisCode AS orgStructureCode,
                rbMedicalAidUnit.federalCode AS medicalAidUnitFederalCode,
                Event.`order`,
                Event.id AS eventId,
                EventResult.federalCode AS eventResultFederalCode,
                EventResult.regionalCode AS eventResultRegionalCode,
                rbPayRefuseType.rerun,
                EventType.purpose_id AS purposeId,
                EventType.code AS eventTypeCode,
                Event.littleStranger_id AS littleId,
                Event_LittleStranger.multipleBirths     AS littleMultipleBirths,
                Event_LittleStranger.birthDate     AS littleBirthDate,
                Event_LittleStranger.sex           AS littleSex,
                Event_LittleStranger.currentNumber AS littleNumber, 
                Sums.sum AS evsum,
                Sums.amount AS evamount,
                ClientIdentification.identifier AS regId,
                ActionType.flatCode,
                Account_Item.sum as aisum,
                Account_Item.amount as aiamount,
                mes.MES.code AS mesCode,
                rbHighTechCureKind.code AS hmpKindCode,
                rbHighTechCureMethod.code AS hmpMethodCode

            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN ActionType ON ActionType.id = Action.ActionType_id
            LEFT JOIN rbService ON rbService.id = ActionType.nomenclativeService_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                      ClientPolicy.id = (SELECT MAX(CP.id)
                                         FROM   ClientPolicy AS CP
                                         LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                                         WHERE CP.dischargeDate IS NULL AND (CP.endDate > Event.setDate OR CP.endDate IS NULL)
                                         AND CP.client_id = Client.id AND CP.deleted=0 AND CPT.code IN ('1','2') AND CP.insurer_id = %d
                      )
            LEFT JOIN rbPolicyKind ON ClientPolicy.policyKind_id = rbPolicyKind.id
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND
                      ClientDocument.id = (SELECT MAX(CD.id)
                                         FROM   ClientDocument AS CD
                                         LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                         LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                                         WHERE  rbDTG.code = '1' AND CD.client_id = Client.id AND CD.deleted=0)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id AND
                      ClientRegAddress.id = (SELECT MAX(CRA.id)
                                         FROM   ClientAddress AS CRA
                                         WHERE  CRA.type = 0 AND CRA.client_id = Client.id AND CRA.deleted=0)
            LEFT JOIN Address   RegAddress ON RegAddress.id = ClientRegAddress.address_id
            LEFT JOIN AddressHouse RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
            LEFT JOIN kladr.KLADR ON kladr.KLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN Diagnostic ON Diagnostic.id = (
              SELECT MAX(D.id)
              FROM Diagnostic AS D
              WHERE D.event_id = Account_Item.event_id
                AND ((D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code ='2')
                        AND D.person_id = Event.execPerson_id) OR (
                          D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='1')))
                          AND D.deleted = 0)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbMedicalAidType ON IF(EventType.medicalAidType_id,
                                                EventType.medicalAidType_id = rbMedicalAidType.id,
                                                rbItemService.medicalAidType_id = rbMedicalAidType.id)
            LEFT JOIN rbMedicalAidKind ON EventType.medicalAidKind_id = rbMedicalAidKind.id
            LEFT JOIN rbEventProfile AS EventMedicalAidProfile ON
                EventType.eventProfile_id = EventMedicalAidProfile.id
            LEFT JOIN rbMedicalAidProfile AS VisitMedicalAidProfile ON
                VisitMedicalAidProfile.id = rbVisitService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON
                ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN Diagnostic AS AccDiagnostic ON AccDiagnostic.id = (
             SELECT id FROM Diagnostic AS AD
             WHERE AD.event_id = Account_Item.event_id AND
                AD.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='9') AND
                AD.person_id = Event.execPerson_id AND
                AD.deleted = 0 LIMIT 1)
            LEFT JOIN Diagnosis AS AccDiagnosis ON
                AccDiagnosis.id = AccDiagnostic.diagnosis_id AND
                AccDiagnosis.deleted = 0
            LEFT JOIN Diagnostic AS CompDiagnostic ON CompDiagnostic.id = (
             SELECT id FROM Diagnostic AS CD
             WHERE CD.event_id = Account_Item.event_id AND
                CD.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='3') AND
                CD.person_id = Event.execPerson_id AND
                CD.deleted = 0 LIMIT 1)
            LEFT JOIN Diagnosis AS CompDiagnosis ON
                CompDiagnosis.id = CompDiagnostic.diagnosis_id AND
                CompDiagnosis.deleted = 0
            LEFT JOIN Person ON Person.id = Event.execPerson_id
            LEFT JOIN ClientIdentification ON ClientIdentification.client_id = Client.id  AND ClientIdentification.id = (SELECT MAX(CI.id)
                FROM ClientIdentification AS CI
                WHERE CI.client_id = Client.id AND CI.deleted = 0)
            LEFT JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id


            LEFT JOIN Event_LittleStranger ON Event.littleStranger_id = Event_LittleStranger.id
            LEFT JOIN rbHighTechCureKind ON rbHighTechCureKind.id = Event.hmpKind_id
            LEFT JOIN rbHighTechCureMethod ON rbHighTechCureMethod.id = Event.hmpMethod_id

            LEFT JOIN mes.MES_service ON mes.MES_service.id = (SELECT
                    ms.id
                  FROM mes.MES_service ms
                    INNER JOIN mes.mrbService s
                      ON s.id = ms.service_id AND ms.deleted = 0
                    LEFT JOIN mes.MES_mkb mm
                      ON mm.master_id = ms.master_id AND mm.deleted = 0
                    WHERE s.code = rbItemService.code AND
                          IF (s.combineType = 0, 1,
                                IF (s.combineType = 1, isSexAndAgeSuitable(0, Client.birthDate, 0, ms.ageConstraint, Action.begDate),
                                IF (s.combineType = 2, isSexAndAgeSuitable(Client.sex, Client.birthDate, ms.sexConstraint, '', Action.begDate),
                                IF (s.combineType = 3, mm.mkb = Diagnosis.MKB OR ms.isDefault = 1, NULL
                          )))) ORDER BY ms.isDefault
                    LIMIT 1)
            LEFT JOIN mes.MES_mkb ON mes.MES_mkb.id = (SELECT mm.id FROM mes.MES_mkb mm
                        WHERE mm.mkb = Diagnosis.MKB  AND mm.deleted = 0
                              AND isSexAndAgeSuitable(Client.sex, Client.birthDate, mm.sexConstraint, mm.ageConstraint, Event.setDate)
                        LIMIT 1)
            LEFT JOIN mes.MES ON mes.MES.id = IF (mes.MES_service.master_id IS NOT NULL, mes.MES_service.master_id, mes.MES_mkb.master_id)
                                 AND mes.MES.deleted = 0
            

            INNER JOIN (

             select
               Account_Item.event_id AS id,
               SUM(Account_Item.`sum`) AS `sum`,
               SUM(Account_Item.amount) AS amount
             from Account_Item INNER JOIN Event ON Event.id  = Account_Item.event_id
             INNER JOIN EventType ON EventType.id = Event.eventType_id
               LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
               LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
               LEFT JOIN rbMedicalAidType ON rbMedicalAidType.id = IF(EventType.medicalAidType_id, EventType.medicalAidType_id, rbItemService.medicalAidType_id)
             where %s AND Account_Item.deleted = 0 and Event.deleted = 0 and
               Account_Item.reexposeItem_id IS NULL
               AND (Account_Item.date IS NULL
                  OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
               )
               group by event_id

            ) AS Sums ON Event.id = Sums.id

            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s ORDER BY %s""" % (sumStr, payerId, cond, cond, order)
        query = db.query(stmt)
        return query


    def getDispanserData(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        stmt = """SELECT
                COUNT(DISTINCT IF(rbMedicalAidUnit.federalCode in (61, 62),Event.client_id,NULL)) AS ambAdultClientCount,
                SUM(IF(rbMedicalAidUnit.federalCode in (61, 62), Account_Item.`sum`, 0))          AS ambAdultSum,                
                COUNT(DISTINCT IF(rbMedicalAidUnit.federalCode = 61,Event.client_id,NULL))        AS ambStage1ClientCount,
                SUM(IF(rbMedicalAidUnit.federalCode = 61, Account_Item.`sum`, 0))                 AS ambStage1Sum,
                COUNT(DISTINCT IF(rbMedicalAidUnit.federalCode = 62, Event.client_id,NULL))       AS ambStage2ClientCount,
                SUM(IF(rbMedicalAidUnit.federalCode = 62, Account_Item.`sum`, 0))                 AS ambStage2Sum,
                COUNT(DISTINCT IF(rbMedicalAidUnit.federalCode = 63, Event.client_id,NULL))       AS ambChild1ClientCount,
                SUM(IF(rbMedicalAidUnit.federalCode = 63, Account_Item.`sum`, 0))                 AS ambChild1Sum,
                COUNT(DISTINCT IF(rbMedicalAidUnit.federalCode = 64, Event.client_id,NULL))       AS ambChild2ClientCount,
                SUM(IF(rbMedicalAidUnit.federalCode = 64, Account_Item.`sum`, 0))                 AS ambChild2Sum,
                COUNT(DISTINCT IF(rbMedicalAidUnit.federalCode = 65, Event.client_id,NULL))       AS ambChild14ClientCount,
                SUM(IF(rbMedicalAidUnit.federalCode = 65, Account_Item.`sum`, 0))                 AS ambChild14Sum

            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Person ON Person.id = Event.execPerson_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Event.client_id AND
                ClientPolicy.id = (SELECT MAX(CP.id)
                    FROM   ClientPolicy AS CP
                    LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                    WHERE  CP.client_id = Event.client_id AND CP.deleted=0 AND CPT.code IN ('1','2'))
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN Action AS HospitalAction ON
                HospitalAction.id = (
                    SELECT MAX(A.id)
                    FROM Action A
                    WHERE A.event_id = Event.id AND
                              A.deleted = 0 AND
                              A.actionType_id = (
                                    SELECT AT.id
                                    FROM ActionType AT
                                    WHERE AT.flatCode ='moving'
                              )
                )
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id =rbMedicalAidType.id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s AND (rbMedicalAidType.code = '6' OR rbMedicalAidType.code = '9')
        """ % (tableAccountItem['id'].inlist(self.idList))
        query = db.query(stmt)

        ambAdultClientCount = 0
        ambAdultSum = 0
        ambStage1ClientCount = 0
        ambStage1Sum = 0
        ambStage2ClientCount = 0
        ambStage2Sum = 0
        ambChild1ClientCount = 0
        ambChild1Sum = 0
        ambChild2ClientCount = 0
        ambChild2Sum = 0        
        ambChild14ClientCount = 0
        ambChild14Sum  = 0
        if query.next():
            record = query.record()
            ambAdultClientCount    = forceInt(record.value('ambAdultClientCount'))
            ambAdultSum            = forceDouble(record.value('ambAdultSum'))
            ambStage1ClientCount   = forceInt(record.value('ambStage1ClientCount'))
            ambStage1Sum           = forceDouble(record.value('ambStage1Sum'))
            ambStage2ClientCount   = forceInt(record.value('ambStage2ClientCount'))
            ambStage2Sum           = forceDouble(record.value('ambStage2Sum'))
            ambChild1ClientCount   = forceInt(record.value('ambChild1ClientCount'))
            ambChild1Sum           = forceDouble(record.value('ambChild1Sum'))
            ambChild2ClientCount   = forceInt(record.value('ambChild2ClientCount'))
            ambChild2Sum           = forceDouble(record.value('ambChild2Sum'))
            ambChild14ClientCount  = forceInt(record.value('ambChild14ClientCount'))
            ambChild14Sum          = forceDouble(record.value('ambChild14Sum'))

        return ambAdultClientCount, ambAdultSum, ambStage1ClientCount, ambStage1Sum, ambStage2ClientCount, ambStage2Sum, ambChild1ClientCount, ambChild1Sum, ambChild2ClientCount, ambChild2Sum, ambChild14ClientCount, ambChild14Sum


    def createServiceQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        
        stmt = """SELECT
                OrgStructure.name AS orgStructureName,
                OrgStructure.id AS orgStructureId,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.infis,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                  ) AS serviceCode,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.name,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.name, rbEventService.name)
                  ) AS serviceName,
                Account_Item.price AS price,
                SUM(Account_Item.amount) AS amount,
                SUM(Account_Item.`sum`) AS `sum`,
                Contract_Tariff.price AS tariffPrice,
                Contract_Tariff.federalPrice,
                Contract_Tariff.federalLimitation,
                Contract_Tariff.frag1Start,
                Contract_Tariff.frag1Sum,
                Contract_Tariff.frag1Price,
                Contract_Tariff.frag2Start,
                Contract_Tariff.frag2Sum,
                Contract_Tariff.frag2Price,
                SUM(IF (HospitalAction.id IS NULL,
                    LEAST(IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                            Account_Item.sum), NULL)) AS federalSum,
                SUM(Account_Item.`uet`) AS `uet`,

                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '1', Account_Item.`sum`,0)) AS hospItemsSum,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '1', Account_Item.id,NULL)) AS hospItemsCount,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '1',Event.client_id,NULL)) AS hospClientCount,

                SUM(IF (rbMedicalAidType.code = '4', Account_Item.`sum`,0)) AS smpSum,
                COUNT(DISTINCT IF (rbMedicalAidType.code = '4', Account_Item.id,NULL)) AS smpCount,
                COUNT(DISTINCT IF (rbMedicalAidType.code = '4', Event.client_id,NULL)) AS smpClientCount,

                IF(Contract_Tariff.tariffType IN ('8','9','10'),1,0) AS isMES1,
                COUNT(DISTINCT Event.client_id) AS clientCount,
                
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7',Event.client_id,NULL)) AS dayHospClientCount,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7', Account_Item.`sum`,0)) AS dayHospItemsSum,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7', Account_Item.id,NULL)) AS dayHospItemsCount,
                
                COUNT(DISTINCT IF (rbMedicalAidType.code = '6' OR rbMedicalAidType.code = '9',Event.client_id,NULL)) AS ambClientCount,
                SUM(IF (rbMedicalAidType.code = '6' OR rbMedicalAidType.code = '9',Account_Item.`sum`,0)) AS ambSum,
                SUM(IF (HospitalAction.id IS NULL AND (rbMedicalAidType.code = '6' or rbMedicalAidType.code = '9'),Account_Item.amount,NULL)) AS serviceCount,
                
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'),Account_Item.`sum`,0)) AS hospSum,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'),Account_Item.event_id,NULL)) AS hospBedDays,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'),Account_Item.event_id,NULL)) AS dayHospBedDays,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'),Account_Item.`sum`,0)) AS dayHospSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType IN ('8','9','10'),Account_Item.`sum`,0)) AS hospMesSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType IN ('8','9','10'),Account_Item.`sum`,0)) AS dayHospMesSum,

                SUM(IF (HospitalAction.id IS NOT NULL AND Contract_Tariff.tariffType NOT IN ('8','9','10') AND Account_Item.`sum` != 0,
                    Account_Item.`amount`-IF(Contract_Tariff.price=0 AND Contract_Tariff.frag1Start>0,Contract_Tariff.frag1Start,0 ),0)) AS bedDays,
                #SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10') AND Account_Item.`sum` != 0,
                #    Account_Item.`amount`-IF(Contract_Tariff.price=0 AND Contract_Tariff.frag1Start>0,Contract_Tariff.frag1Start,0 ),0)) AS dayHospBedDays,
                #SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10') AND Account_Item.`sum` != 0,
                #    Account_Item.`amount`-IF(Contract_Tariff.price=0 AND Contract_Tariff.frag1Start>0,Contract_Tariff.frag1Start,0 ),0)) AS hospBedDays,
                SUM(IF (HospitalAction.id IS NOT NULL AND Contract_Tariff.tariffType IN ('8','9','10'),Account_Item.`amount`,0)) AS mesBedDays,
                COUNT(DISTINCT IF (Contract_Tariff.tariffType IN ('8','9','10'),Event.id,NULL)) AS mesCount,
                SUM(IF (Contract_Tariff.tariffType IN ('8','9','10'),Account_Item.`sum`,NULL)) AS mesSum,
                SUM(IF (Contract_Tariff.tariffType IN ('8','9','10'),
                      IF(Contract_Tariff.federalLimitation = 0, 0,
                      IF(Account_Item.amount BETWEEN -1 AND Contract_Tariff.frag1Start,
                        Account_Item.amount*Contract_Tariff.federalPrice/Contract_Tariff.federalLimitation,
                        Contract_Tariff.federalPrice)),
                      NULL)) AS mesFederalSum,
                    SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'),LEAST(IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                            Account_Item.sum), NULL)) AS hospFederalSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'), LEAST(IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                            Account_Item.sum), NULL)) AS dayHospFederalSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType IN ('8','9','10'),
                         LEAST(Contract_Tariff.federalPrice, Account_Item.sum), NULL)) AS hospMesFederalSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType IN ('8','9','10') ,
                            LEAST(Contract_Tariff.federalPrice, Account_Item.sum), NULL)) AS dayHospMesFederalSum,
                mes.MES.code AS mesCode
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Person ON Person.id = Event.execPerson_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Event.client_id AND
                ClientPolicy.id = (SELECT MAX(CP.id)
                    FROM   ClientPolicy AS CP
                    LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                    WHERE  CP.client_id = Event.client_id AND CP.deleted=0 AND CPT.code IN ('1','2'))
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN Action AS HospitalAction ON
                HospitalAction.id = (
                    SELECT MAX(A.id)
                    FROM Action A
                    WHERE A.event_id = Event.id AND
                              A.deleted = 0 AND
                              A.actionType_id = (
                                    SELECT AT.id
                                    FROM ActionType AT
                                    WHERE AT.flatCode ='moving'
                              )
                )
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id =rbMedicalAidType.id
            LEFT JOIN mes.MES ON Event.MES_id = mes.MES.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            GROUP BY orgStructureId, isMES1, serviceCode WITH ROLLUP
        """ % (tableAccountItem['id'].inlist(self.idList))
        query = db.query(stmt)
        return query


    def saveSummary(self, record, name,  isMES=False):
        u"""Cохраняет статистику по подразделению с именем name."""

        if isMES and self.orgStuctStat.has_key(name):
            (amount,  sum, clientCount, ambClientCount, hospClientCount,
            bedDays, mesBedDays, ambSum, hospSum,  uet, dayHospSum, mesCount,
            federalSum, dayHospClientCount,  mesSum,  mesFederalSum,
            hospFederalSum, dayHospFederalSum, hospBedDays, dayHospBedDays, isMES) = self.orgStuctStat[name]
            amount+= forceInt(record.value('serviceCount'))
            sum+= forceDouble(record.value('sum'))
#            clientCount += forceInt(record.value('clientCount'))
#            ambClientCount+= forceInt(record.value('ambClientCount'))
#            hospClientCount+= forceInt(record.value('hospClientCount'))
            bedDays += forceInt(record.value('bedDays'))
            hospBedDays    += forceInt(record.value('hospBedDays'))
            dayHospBedDays += forceInt(record.value('dayHospBedDays'))
            mesBedDays += forceInt(record.value('mesBedDays'))
            ambSum += forceDouble(record.value('ambSum'))
            hospSum += forceDouble(record.value('hospMesSum'))
            uet += forceDouble(record.value('uet'))
            dayHospSum += forceDouble(record.value('dayHospMesSum'))
            mesCount += forceInt(record.value('mesCount'))
            federalSum += forceDouble(record.value('federalSum'))
            dayHospClientCount += forceInt(record.value('dayHospClientCount'))
            mesSum += forceDouble(record.value('mesSum'))
            mesFederalSum += forceDouble(record.value('mesFederalSum'))
            hospFederalSum += forceDouble(record.value('hospFederalSum'))
            dayHospFederalSum += forceDouble(record.value('dayHospMesFederalSum'))
            hospItemsSum    += forceDouble(record.value('hospItemsSum'))
            dayHostItemsSum += forceDouble(record.value('hospItemsSum'))
            smpClientCount += forceInt(record.value('smpClientCount'))
            smpCount +=       forceInt(record.value('smpCount'))
            smpSum +=         forceDouble(record.value('smpSum'))
            
            self.orgStuctStat[name] = (amount,  sum, clientCount,
                ambClientCount, hospClientCount, bedDays, mesBedDays,
                ambSum, hospSum,  uet, dayHospSum, mesCount,
                federalSum, dayHospClientCount, mesSum, mesFederalSum,
                hospFederalSum, dayHospFederalSum, hospBedDays, dayHospBedDays, hospItemsSum, dayHospItemsSum, smpClientCount, smpCount, smpSum, isMES)
        else:
            self.orgStuctStat[name] = (
                forceInt(record.value('serviceCount')),
                forceDouble(record.value('mesSum')) if isMES else (forceDouble(record.value('sum'))-forceDouble(record.value('mesSum'))),
                forceInt(record.value('clientCount')),
                forceInt(record.value('ambClientCount')),
                forceInt(record.value('hospClientCount')),
                forceInt(record.value('bedDays')),
                forceInt(record.value('mesBedDays')),
                forceDouble(record.value('ambSum')),
                forceDouble(record.value('hospMesSum' if isMES else 'hospSum')),
                forceDouble(record.value('uet')),
                forceDouble(record.value('dayHospMesSum' if isMES else 'dayHospSum')),
                forceInt(record.value('mesCount')),
                forceDouble(record.value('federalSum')),
                forceInt(record.value('dayHospClientCount')),
                forceDouble(record.value('mesSum')),
                forceDouble(record.value('mesFederalSum')),
                forceDouble(record.value('hospMesFederalSum' if isMES else 'hospFederalSum')),
                forceDouble(record.value('dayHospMesFederalSum' if isMES else 'dayHospFederalSum')),
                forceInt(record.value('hospBedDays')),
                forceInt(record.value('dayHospBedDays')),
                forceDouble(record.value('hospItemsSum')),
                forceDouble(record.value('dayHospItemsSum')),
                forceInt(record.value('smpClientCount')),
                forceInt(record.value('smpCount')),
                forceDouble(record.value('smpSum')),
                isMES
                )


    def processServices(self,  txtStream,  record):
        #if self.parent.page1.chkSkipZeroSum.isChecked() and forceDouble(record.value('sum')) == 0:
        #    return

        if record.isNull('orgStructureId'):
            self.saveSummary(record, 'total')
            # из-за rollup
            return

        if record.isNull('serviceCode') and not record.isNull('isMES1'):
            return


        format = u'%12.12s│%60.60s│%36.36s│%6.6s│%11.11s\n'
        orgStructureId = forceRef(record.value('orgStructureId'))
        orgStructureName = forceString(record.value('orgStructureName'))

        if self.currentOrgStructureId != orgStructureId:
            if self.currentOrgStructureId:
                self.writeOrgStructureFooter(txtStream)

            orgStructureName = forceString(record.value('orgStructureName'))
            self.writeOrgStructureHeader(txtStream, orgStructureName)
            self.currentOrgStructureId = orgStructureId
            self.currentOrgStructureName = orgStructureName
        

        isMES = forceBool(record.value('isMES1'))

        if isMES:
            mesCode = forceString(record.value('serviceCode'))
            self.saveSummary(record, mesCode, True)

        if record.isNull('serviceCode') and record.isNull('isMES1'):
            self.saveSummary(record, self.currentOrgStructureName)
            # из-за rollup
            return

        amount = forceInt(record.value('amount'))
        mesCount = forceInt(record.value('mesCount'))
        mesBedDays = forceInt(record.value('mesBedDays'))
        sum = forceDouble(record.value('sum'))
        federalPrice = forceDouble(record.value('federalPrice'))
        federalLimitation = forceDouble(record.value('federalLimitation'))
        frag1Start = forceDouble(record.value('frag1Start'))

        frag1Sum = forceDouble(record.value('frag1Sum'))
        frag2Sum = forceDouble(record.value('frag2Sum'))
        frag1Price = forceDouble(record.value('frag1Price'))
        frag2Price = forceDouble(record.value('frag2Price'))

        #isLinearTariff = (frag1Start > 0) and ((frag1Price != 0 and frag1Sum != 0) or (frag2Price != 0 and frag2Sum != 0))

        if frag1Start>0 and amount < frag1Start:
            federalPrice = amount * federalPrice / federalLimitation if federalLimitation != 0 else 0
#        else:
#            if not isLinearTariff and federalLimitation > 0:
#                federalPrice /= federalLimitation

        if isMES:
            price = sum /mesCount if mesCount != 0 else 0
        else:
            price = sum /amount if amount != 0 else 0

        if forceDouble(record.value('tariffPrice')) == 0 and frag1Start > 0:
            amount = forceString(record.value('bedDays'))
            price = frag1Price

        if self.lines > self.maxPageLines:
            self.writeTableFooter(self.appendixStream)
            self.writeNewPage(self.appendixStream)
            self.pageNum += 1
            self.appendixStream << (u'-%d-' % self.pageNum).center(124)
            self.appendixStream << u'\n'
            self.writeTableLiteHeader(self.appendixStream)
            self.lines = 4

        hospItemsCount = forceInt(record.value('hospItemsCount'))
        dayHospItemsCount = forceInt(record.value('dayHospItemsCount'))
      
        self.appendixStream << format % (
                forceString(record.value('serviceCode')),
                forceString(record.value('serviceName')).ljust(60),
                    (u'%11d' % (hospItemsCount + dayHospItemsCount)),
                    (u'%6d' % mesCount if isMES else amount),
                    (u'%11.2f' % sum)
                )

        self.lines += 1

    def writeOrgStructureHeader(self,  txtStream,  name):
        header = \
u"""Отделение: %s
""" % name
        txtStream<<header
        self.lines += 9


    def writeOrgStructureFooter(self,  txtStream):
        (amount, sum, clientCount, ambClientCount,
            hospClientCount, bedDays, mesBedDays, ambSum, hospSum,  uet,
            dayHospSum, mesCount, federalSum, dayHospClientCount, mesSum,
            mesFederalSum, hospFederalSum, dayHospFederalSum, hospBedDays, dayHospBedDays, hospItemsSum, dayHospItemsSum, smpClientCount, smpCount, smpSum, isMES) = \
        self.orgStuctStat.get(self.currentOrgStructureName, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False))

        footer = \
u"""Количество пролеченных пациентов %7d на сумму %11.2f
             из них амбулаторных %7d на сумму %11.2f
                    стационарных %7d на сумму %11.2f
             дневного стационара %7d на сумму %11.2f
             скорой помощи       %7d на сумму %11.2f
Выполнено услуг                  %7d на сумму %11.2f
Выполнено законченных случаев
по стационару                    %7d на сумму %11.2f
Выполнено законченных случаев 
по дневному стационару 	         %7d на сумму %11.2f
Выполнено вызовов                %7d на сумму %11.2f
""" % (clientCount, sum+mesSum,
        ambClientCount,  ambSum,
        hospClientCount,  hospSum,
        dayHospClientCount, dayHospSum,
        smpClientCount, smpSum,
        amount, ambSum,
        hospBedDays, hospSum,
        dayHospBedDays, dayHospSum,
        smpCount, smpSum
        )

        txtStream<<footer
        self.writeTableHeader(txtStream)
        txtStream<<self.appendixStr
        self.appendixStr.clear()

        footer = \
u"""────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────┼──────┼───────────
   Итого    │                                                            │                                    │      │%11.2f
"""
        txtStream << footer % (sum+mesSum)
        self.writeTableFooter(txtStream)
        self.writeNewPage(txtStream)



    def writeTableHeader(self, txtStream):
        header = \
u"""
────────────┬────────────────────────────────────────────────────────────┬────────────────────────────────────┬──────┬───────────
Код услуги  │                        Наименование                        │          Количество                │Кол-во│ Всего
(законченный│                                                            │          законченных               │к/дней│стоимость
  случай,   │                                                            │            случаев                 │      │
 посещение, │                                                            │                                    │      │
  вызов)    │                                                            │                                    │      │
────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────┼──────┼───────────
"""
        txtStream << header

    def writeTextHeader(self,  txtStream):
        self.currentOrgStructureId = None
        self.currentOrgStructureName = None
        self.currentArea = QtGui.qApp.defaultKLADR()[:2]
        self.orgStuctStat = {}
        self.appendixStr.clear()
        self.lines = 10
        self.pageNum = 1
        orgName = forceString(QtGui.qApp.db.translate('Organisation', \
            'id',  QtGui.qApp.currentOrgId(), 'title'))
        record = QtGui.qApp.db.getRecord('Contract', 'date,number,resolution',  self.contractId)

        if record:
            contractDate = forceDate(record.value('date')).toString('dd.MM.yyyy')
            contractNumber = forceString(record.value('number'))
            contractResolution = forceString(record.value('resolution'))
        else:
            contractDate = u'б\д'
            contractNumber = u'б\н'
            contractResolution = '-'

        header = \
u"""Медицинская организация %s

СЧЕТ-ФАКТУРА от %s
за оказанные медицинские услуги по территориальной программе ОМС
пациентам своей территории за %s г.

Договор N %s (%s) от %s
--------------------------------------------------
Основная информация

1. РАБОТА ПРОФИЛЬНЫХ ОТДЕЛЕНИЙ
""" % (orgName, self.accDate.toString('dd/MM/yyyy'), self.settleDate.toString(u'MMMM yyyy').toLower(),
       contractNumber, contractResolution, contractDate)

        txtStream << header


    def writeTableHeader(self, txtStream):
        header = \
u"""────────────┬────────────────────────────────────────────────────────────┬────────────────────────────────────┬──────┬───────────
 Код услуги │                        Наименование                        │           Количество               │Кол-во│ Всего
(законченный│                                                            │          законченных               │к/дней│стоимость
  случай,   │                                                            │            случаев                 │      │
 посещение, │                                                            │                                    │      │
  вызов)    │                                                            │                                    │      │
────────────┼────────────────────────────────────────────────────────────┼────────────────────────────────────┼──────┼───────────
"""
        txtStream << header

    def writeTableLiteHeader(self, txtStream):
        header = \
u"""────────────┬────────────────────────────────────────────────────────────┬───┬───────────┬──────┬────────┬──────┬────┬───────────
     1      │                             2                              │ 3 │     4     │  5   │   6    │  7   │ 8  │     9
────────────┼────────────────────────────────────────────────────────────┼───┼───────────┼──────┼────────┼──────┼────┼───────────
"""
        txtStream << header

    def writeTableFooter(self, txtStream):
        footer = u'────────────┴────────────────────────────────────────────────────────────┴────────────────────────────────────┴──────┴───────────\n'
        txtStream << footer


    def writeNewPage(self, txtStream):
        txtStream << u'\n\x0C\n'
        self.lines = 0

    def writeTextFooter(self,  txtStream):
        self.writeOrgStructureFooter(txtStream)
        delimeter = u'+-------------------+------+------+------+------+------+------+--------------------+-------+-----------+------+----------------------+-----------+\n'
        format = u'|%19.19s|%6d|%6d|%6d|%6d|%6d|%6d|%20.2f|%7.2f|%11d|%6d|%22.2f|%11.2f|\n'
        totalClientCount = 0
        totalAmbClientCount = 0
        totalHospClientCount = 0
        totalAmount = 0
        totalAmbSum = 0
        totalUet = 0
        totalBedDays = 0
        totalMesBedDays = 0
        totalHospSum = 0
        totalSum = 0
        totalServiceCount = 0
        totalMESServiceCount = 0
        totalMESSum = 0
        totalDayHospClientCount = 0
        totalDayHospSum = 0
        totalTerSum =0
        totalFedSum = 0
        totalMesFedSum = 0
        totalHospFederalSum = 0
        totalDayHospFederalSum = 0
        totalDayHospTerSum = 0
        totalHospTerSum = 0
        isMES = False

        orgName = forceString(QtGui.qApp.db.translate('Organisation', \
            'id',  QtGui.qApp.currentOrgId(), 'title'))
        orgChief = forceString(QtGui.qApp.db.translate('Organisation', \
            'id',  QtGui.qApp.currentOrgId(), 'chief'))
        orgAccountant = forceString(QtGui.qApp.db.translate('Organisation', \
            'id',  QtGui.qApp.currentOrgId(), 'accountant'))

        self.appendixStr.clear()

        for (key, val) in self.orgStuctStat.iteritems():
            if key != 'total':
                (amount, sum, clientCount, ambClientCount,
                    hospClientCount, bedDays, mesBedDays, ambSum, hospSum, uet,
                    dayHospSum, mesCount, federalSum, dayHospClientCount, mesSum,
                    mesFederalSum, hospFederalSum, dayHospFederalSum, hospBedDays, dayHospBedDays, hospItemsSum, dayHospItemsSum, smpClientCount, smpCount, smpSum, isMES) = val
                if sum != 0:
                    self.appendixStream << format % (key.ljust(19), clientCount,
                        ambClientCount, hospClientCount, dayHospClientCount, smpClientCount, amount + smpCount, ambSum + smpSum - federalSum,
                        uet, 
                        hospBedDays + dayHospBedDays, mesBedDays if isMES else bedDays, hospItemsSum + dayHospItemsSum, #(mesSum-mesFederalSum) if isMES else (mesSum+dayHospSum+hospSum-hospFederalSum-dayHospFederalSum)
                         sum)
                    self.appendixStream << delimeter
            else:
                (totalAmount, totalSum, totalClientCount, totalAmbClientCount,
                    totalHospClientCount, totalBedDays, totalMesBedDays, totalAmbSum, totalHospSum,  totalUet,
                    totalDayHospSum, totalMESServiceCount, totalFedSum, totalDayHospClientCount,
                    totalMESSum,  totalMesFedSum,  totalHospFederalSum, totalDayHospFederalSum, totalHospBedDays, totalDayHospBedDays, totalHospItemsSum, totalDayHospItemsSum, 
                    totalSmpClientCount, totalSmpCount, totalSmpSum, isMES) =val
                totalTerSum = totalAmbSum - totalFedSum
                totalHospTerSum = totalHospSum - totalHospFederalSum
                totalDayHospTerSum = totalDayHospSum - totalDayHospFederalSum
                totalMesTerSum = totalMESSum - totalMesFedSum


        txtStream << u"""Медицинская организация %s

2. СВОДНАЯ СПРАВКА
за оказанные медицинские услуги по территориальной программе ОМС
пациентам своей территории
за %s г.
в разрезе МО

Количество пролеченных пациентов %7d на сумму %11.2f
             из них амбулаторных %7d на сумму %11.2f
                    стационарных %7d на сумму %11.2f
             дневного стационара %7d на сумму %11.2f
             скорой помощи       %7d на сумму %11.2f
Выполнено услуг                  %7d на сумму %11.2f
Выполнено законченных случаев
по стационару                    %7d на сумму %11.2f
Выполнено законченных случаев 
по дневному стационару 	         %7d на сумму %11.2f
Выполнено вызовов                %7d на сумму %11.2f

+-------------------+---------------------------+------+-----------------------------------+-----------------------------------------+-----------+
|Наименование       |      Пролечено пациентов         | Выполнено услуг,                  |  Реализовано законченных случаев        |Всего      |
|отделения,         |                                  |      вызовов                      |                                         |cтоимость  |
|МЭС                +------+------+------+------+------+------+--------------------+-------+-----------+------+----------------------+           |
|                   |Всего | Амб. | Стац.| Дн.  | Скор.|Кол-во|    Стоимость       | УЕТ   |Количество |Кол-во|    Стоимость         |           |
|                   |      |      |      |      |      |      |                    |       |законченных| к/дн |                      |           |
|                   |      |      |      | Стац.| Пом. |      |                    |       |случаев    |      |                      |           |
|                   |      |      |      |      |      |      |                    |       |           |      |                      |           |
|                   |      |      |      |      |      |      |                    |       |           |      |                      |           |
+-------------------+------+------+------+------+------+------+--------------------+-------+-----------+------+----------------------+-----------+
""" % (orgName, self.settleDate.toString(u'MMMM yyyy').toLower(),
        totalClientCount,  totalSum+totalMESSum,
        totalAmbClientCount,  totalAmbSum,
        totalHospClientCount, totalHospSum,
        totalDayHospClientCount, totalDayHospSum,
        totalSmpClientCount, totalSmpSum,
        totalAmount,  totalAmbSum,
        totalHospBedDays,  totalHospSum,
        totalDayHospBedDays,  totalDayHospSum,
        totalSmpCount, totalSmpSum
        )

        txtStream << self.appendixStr
        txtStream << format % (u'Итого'.ljust(19), totalClientCount,
                totalAmbClientCount, totalHospClientCount, totalDayHospClientCount, totalSmpClientCount, totalAmount + totalSmpCount,
                totalTerSum + totalSmpSum,  totalUet, 
                totalHospBedDays+totalDayHospBedDays, totalBedDays+totalMesBedDays,
                totalHospItemsSum + totalDayHospItemsSum,
                totalSum+totalMESSum)
        txtStream << delimeter

        ambAdultClientCount, ambAdultSum, ambStage1ClientCount, ambStage1Sum, ambStage2ClientCount, ambStage2Sum, ambChild1ClientCount, ambChild1Sum, ambChild2ClientCount, ambChild2Sum, ambChild14ClientCount, ambChild14Sum = self.getDispanserData()

        txtStream << u"""
ВСЕГО ПРЕДСТАВЛЕНО К ОПЛАТЕ: %11.2f
      (%s)

Руководитель мед.учреждения ____________________ %s

Гл.бухгалтер мед.учреждения ____________________ %s
""" % (totalSum+totalMESSum, amountToWords(totalSum+totalMESSum), orgChief, orgAccountant)
#ambAdultClientCount, ambAdultSum, ambStage1ClientCount, ambStage1Sum, ambStage2ClientCount, ambStage2Sum, ambChild1ClientCount, ambChild1Sum, ambChild2ClientCount, ambChild2Sum, ambChild14ClientCount, ambChild14Sum,
        self.writeNewPage(txtStream)

    def writeOrgStructureHeader(self,  txtStream,  name):
        header = \
u"""Отделение: %s
""" % name
        txtStream<<header
        self.lines += 9

# *****************************************************************************************

    def exportInt(self):
        self.ignoreErrors = True #self.chkIgnoreErrors.isChecked()
        lpuName = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'fullName'))
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OGRN'))

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан ОГРН', True)
            if not self.ignoreErrors:
                return

        lpuOKATO = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OKATO'))

        if not lpuOKATO:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан ОКАТО', True)
            if not self.ignoreErrors:
                return

        outFiles, query, stacQuery, serviceQuery, clientsFile = self.prepareToExport()
        accDate, accNumber, exposeDate, contractId,  payerId, aDate =\
            getAccountInfo(self.parent.accountId)

        strAccNumber = accNumber if forceStringEx(accNumber) else u'б/н'
        strContractNumber = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'number')) if contractId else u'б/н'

        recipientId = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'recipient_id'))

        payerCode = None
        payerName = ''

        if payerId:
            payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'miacCode'))

        if not payerCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для плательщика не задан код МИАЦ', True)
            if not self.ignoreErrors:
                return

        self.recNum = 1

        # загружаем информацию о предварительном реестре для формата 2011.10
        self.preliminaryRegistryInfo = self.getPreliminaryInfo()

        if self.idList:
            clientsOut = CPersonalDataStreamWriter(self)
            clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            miacCode = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', recipientId, 'miacCode')) #QtGui.qApp.currentOrgId()
            accSum = forceDouble(QtGui.qApp.db.translate(
                'Account', 'id', self.parent.accountId, 'sum'))
            clientsOut.writeFileHeader(clientsFile, self.parent.getFullXmlFileName(), aDate)
            outList = []

            for i, outFile in enumerate(outFiles):
                writer = self.writerTypes.get(i, CMyXmlStreamWriter)
                out = writer(self)
                out.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
                out.writeFileHeader(outFile, self.parent.getFullXmlFileName(i), accNumber, aDate,
                                    forceString(accDate.year()),
                                    forceString(accDate.month()),
                                    miacCode, payerCode, accSum)
                outList.append(out)

            # Движения могут выгружаться только в первом типе (HM*)
            outList[0].setEventsInfo(self.getMovingInfo(self.idList))

            record = None
            stacRecord = None
            needToShiftQuery = True
            needToShiftStacQuery = True
            finished = False
            while not finished:
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                if needToShiftQuery:
                    record = query.record() if query.next() else None
                    needToShiftQuery = False
                if needToShiftStacQuery:
                    stacRecord = stacQuery.record() if stacQuery.next() else None
                    needToShiftStacQuery = False

                if record and stacRecord:
                    clientId = forceRef(record.value('client_id'))
                    stacClientId = forceRef(stacRecord.value('client_id'))

                    if clientId <= stacClientId:
                        curOut = self.prepareCurOut(outList, record)
                        curOut.writeRecord(record, miacCode, self.idList, accDate)
                        clientsOut.writeRecord(record)
                        needToShiftQuery = True
                    else:
                        curOut = self.prepareCurOut(outList, stacRecord)
                        curOut.writeRecord(stacRecord, miacCode, self.idList, accDate, isStationaryRecord=True)
                        clientsOut.writeRecord(stacRecord)
                        needToShiftStacQuery = True

                elif record:
                    curOut = self.prepareCurOut(outList, record)
                    curOut.writeRecord(record, miacCode, self.idList, accDate)
                    clientsOut.writeRecord(record)
                    needToShiftQuery = True

                elif stacRecord:
                    curOut = self.prepareCurOut(outList, stacRecord)
                    curOut.writeRecord(stacRecord, miacCode, self.idList, accDate, isStationaryRecord=True)
                    clientsOut.writeRecord(stacRecord)
                    needToShiftStacQuery = True

                else:
                    finished = True

            clientsOut.writeFileFooter()
            for out in outList:
                out.writeFileFooter()
            clientsFile.close()
            for outFile in outFiles:
                outFile.close()

            for out in outList:
                for text in out.xmlErrorsList:
                    self.log(u'Ошибка выгрузки данных: %s' % text)
            for text in clientsOut.xmlErrorsList:
                self.log(u'Ошибка выгрузки персональных данных: %s' % text)

            self.wizard().setNotEmptyOuts(self.isOutFileEmpty)
            txt, txtStream = self.createTxt()
                
            self.writeTextHeader(txtStream)
            while serviceQuery.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.processServices(txtStream, serviceQuery.record())

            if not self.aborted:
                self.writeTextFooter(txtStream)

        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

    def prepareCurOut(self, outList, record):
        eventType = forceString(record.value('eventTypeCode'))
        curOutIndex = self.outEventTypes.get(eventType, 0)
        if curOutIndex == 0:
            medicalAidKind = forceString(record.value('medicalAidKindFederalCode'))
            curOutIndex = self.outMedicalAidKinds.get(medicalAidKind, 0)
        # elif curOutIndex == 6:
        #     stmt = u'''SELECT ActionType.code as atCode FROM Action INNER JOIN ActionType ON ActionType.id = Action.actionType_id
        #                     WHERE Action.deleted = 0 AND ActionType.deleted = 0 AND Action.event_id = %s AND ActionType.code LIKE '162%%' ''' % forceInt(record.value('event_id'))
        #     query = QtGui.qApp.db.query(stmt)
        #     preliminaryATList = ['162040', '162041', '162042']
        #     periodicATList = ['162060', '162061', '162062']
        #     # Профилактические - 162001..162010, но их не проверяем - берем их по умолчанию, если других не нашли
        #     while query.next():
        #         actionTypeCode = forceString(query.record().value(0))
        #         if actionTypeCode in preliminaryATList:
        #             curOutIndex = 7
        #             break
        #         elif actionTypeCode in periodicATList:
        #             curOutIndex = 8
        #             break

        self.isOutFileEmpty[curOutIndex] = False
        return outList[curOutIndex]

# *****************************************************************************************

    def createXML(self):
        outFile2 = QtCore.QFile( self.parent.getFullXmlPersFileName())
        outFile2.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        outFiles = []
        for i in xrange(len(self.wizard().outPrefixes)):
            tempOutFile = QtCore.QFile(self.parent.getFullXmlFileName(i))
            tempOutFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
            outFiles.append(tempOutFile)
        return outFiles, outFile2

# *****************************************************************************************

    def getMovingInfo(self, idList):
        """
            Для стационара необходимо разделять каждое обращение на несколько записей SLUCH, разделитель - действие "Движение"
            (то есть для каждого отделения, в котором побывал больной за время пребывания, свой SLUCH)
            При этом в каждом отделении могут проводиться операции. Нам надо как-то считать сумму и количество услуг для
            каждого отделения, что и производится в данной функции.
        """
        db = QtGui.qApp.db
        stmt = '''SELECT DISTINCT Account_Item.action_id, Account_Item.event_id, ActionType.flatCode, Action.begDate, Action.endDate, Account_Item.sum, Account_Item.amount
            FROM Account_Item
            INNER JOIN Action ON Action.id = Account_Item.action_id
            INNER JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
        WHERE
            Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
        ORDER BY Account_Item.event_id, Action.begDate, Action.id'''
        table = db.table('Account_Item')
        cond = [table['deleted'].eq(0), table['id'].inlist(idList)]
        query = db.query(stmt % db.joinAnd(cond))

        eventsTempInfo = {}
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('event_id'))
            actionId = forceRef(record.value('action_id'))
            flatCode = forceString(record.value('flatCode'))
            begDate = forceDate(record.value('begDate'))
            endDate = forceDate(record.value('endDate'))
            sum = forceDouble(record.value('sum'))
            amount = forceInt(record.value('amount'))

            event = eventsTempInfo.setdefault(eventId, [])
            event.append((actionId, flatCode, begDate, endDate, sum, amount))

        eventsInfo = {}
        for eventId, eventInfo in eventsTempInfo.items():
            movingItems = {}
            # Определяем, сколько у нас будет записей SLUCH для одного event'а на основе количества действий "Движение"
            # Считаем базовые стоимость и количество услуг
            for actionInfo in eventInfo:
                if actionInfo[1] == 'moving':
                    movingItems[(actionInfo[2], actionInfo[3])] = [actionInfo[0], actionInfo[4], actionInfo[5]]

            for actionInfo in eventInfo:
                if actionInfo[1] != 'moving':
                    for (begDate, endDate), values in movingItems.items():
                        if actionInfo[2] >= begDate and actionInfo[2] <= endDate:
                            values[1] += actionInfo[4]
                            values[2] += actionInfo[5]
                            break
            eventsInfo[eventId] = {}
            for item in movingItems.values():
                eventsInfo[eventId][item[0]] = (item[1], item[2])
        return eventsInfo

# *****************************************************************************************

    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True


    @QtCore.pyqtSignature('')
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSignature('')
    def on_btnCancel_clicked(self):
        self.abort()


    @QtCore.pyqtSignature('')
    def on_btnSelectServiceInfoFileName_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными предварительного счета', self.edtServiceInfoFileName.text(), u'Файлы XML (*.xml)')
        if fileName != '' :
            self.edtServiceInfoFileName.setText(QtCore.QDir.toNativeSeparators(fileName))

# *****************************************************************************************

class CExportPage2(QtGui.QWizardPage, Ui_ExportPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R46XMLExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        success = False
        zips = []
        pfn = self.parent.getFullXmlPersFileName()

        isOutFileEmpty = self.wizard().getNotEmptyOuts()
        # Cоздаем и заполняем архивы с файлами по диспансеризации
        for outType in xrange(len(self.wizard().outPrefixes)):
            fn = self.parent.getFullXmlFileName(outType)
            if not isOutFileEmpty[outType]:
                (root, ext) = os.path.splitext(fn)
                zipFileName = '%s.zip' % root
                zf = zipfile.ZipFile(zipFileName, 'w', allowZip64=True)
                zf.write(fn, os.path.basename(fn), zipfile.ZIP_DEFLATED)
                zf.write(pfn, os.path.basename(pfn), zipfile.ZIP_DEFLATED)
                zf.close()
                zips.append(zipFileName)
            os.remove(fn)

        success = True
        for zfn in zips:
            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(zfn))
            success, result = QtGui.qApp.call(self, shutil.move, (zfn, dst))

        if success:

            srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                self.parent.page1.getTxtFileName())
            dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                self.parent.page1.getTxtFileName())
            success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

            QtGui.qApp.preferences.appPrefs['R46XMLExportDir'] = toVariant(self.edtDir.text())
            QtGui.qApp.preferences.appPrefs['ExportR46XMLRegistryNumber'] = \
                    toVariant(self.parent.page1.edtRegistryNumber.value())
            self.wizard().setAccountExposeDate()

        return success


    @QtCore.pyqtSignature('QString')
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSignature('')
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ОМС Смоленской области',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
             self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))

# *****************************************************************************************
