# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil

from library.dbfpy.dbf import *
from library.Utils     import *
from Registry.Utils import getAttachRecord
from Exchange.ExportLOFOMS import myFormatAddress
from Events.Action import CAction

from Ui_ExportR51DDPage1 import Ui_ExportR51DDPage1
from Ui_ExportR51DDPage2 import Ui_ExportR51DDPage2


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number, exposeDate, contract_id', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        number = forceString(accountRecord.value('number'))
        contractId = forceRef(accountRecord.value('contract_id'))
    else:
        date = exposeDate = contractId = None
        number = ''
    return date, number, exposeDate, contractId


def exportR51DD(widget, accountId, accountItemIdList):
    wizard = CExportWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportR51DDPage1(self)
        self.page2 = CExportR51DDPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта ДД-2010 для Мурманской области')
        self.dbfFileName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId = getAccountInfo(accountId)
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменных файлов "*.dbf"')


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R51DD')
        return self.tmpDir


    def getFullDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '.dbf')


    def setAccountItemsIdList(self, accountItemIdList):
        self.page1.setAccountItemsIdList(accountItemIdList)


    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


# *****************************************************************************************


class CExportR51DDPage1(QtGui.QWizardPage, Ui_ExportR51DDPage1):
    exportFormat2009 = 0 # индексы из cmbExportFormat
    #exportFormat2010 = 2
    exportFormatTFOMS = 1
    mapAttachCodeToDispType= {'1':'1', '2':'1', '5':'2', '3':'3', '4':'4' }
    mapDispReasonCode = {'4':'1', '3':'2', '5':'3'}

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.exportedActionsList = []
        self.parent = parent
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51DDIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkMarkFirstForMKBZ00.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51DDMarkFirstForMKBZ00', 'True')))
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51DDVerboseLog', 'False')))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)

        self.hospitalDirectionActionTypeId = None


    def validatePage(self):
        QtGui.qApp.preferences.appPrefs['ExportR51DDIgnoreErrors'] = toVariant(self.chkIgnoreErrors.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR51DDMarkFirstForMKBZ00'] = toVariant(self.chkMarkFirstForMKBZ00.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR51DDVerboseLog'] = toVariant(self.chkVerboseLog.isChecked())
        return self.done


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.chkMarkFirstForMKBZ00.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)


    def log(self, str, forceLog = False):
        if self.chkVerboseLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query


    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


    def getDbfBaseName(self):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
        accDate, accNumber, exposeDate, contractId =\
            getAccountInfo(self.parent.accountId)
        return forceString(lpuCode + (accDate.toString('MMyy') if accDate.isValid() else u'0000') + u'.DBF')


    def getHospitalDirectionTypeId(self):
        u"""Ищет id типа действия (1-1) Направление.(1) Направление на госпитализацию"""
        db=QtGui.qApp.db
        tableActionType = db.table('ActionType')
        typeId = None
        record = db.getRecordEx(tableActionType, 'id', u'code=\'1-1\' AND name=\'Направление\' AND group_id IS NULL')

        if record:
            directionGroupId = forceRef(record.value(0))

            if directionGroupId:
                record = db.getRecordEx(tableActionType, 'id',
                    u'code=\'1\' AND name=\'Направление на госпитализацию\''\
                    u' AND group_id=\'%d\'' % directionGroupId)

                if record:
                    typeId = forceRef(record.value(0))

        return typeId


    def getHospitalDirectionNumberStr(self, eventId):
        numberStr = ''

        if self.hospitalDirectionActionTypeId:
            db=QtGui.qApp.db
            table = db.table('Action')
            record = db.getRecordEx(table, '*',
                u'event_id=\'%d\' AND actionType_id=\'%d\'' % (eventId, self.hospitalDirectionActionTypeId))

            if record:
                action = CAction()
                action.setRecord(record)
                property = action.getProperty(u'Номер направления')

                if property:
                    numberStr = property.getTextScalar()

        return numberStr

# *****************************************************************************************

    diagnosticDateCache = {}

    def getDiagnosticDate(self, eventId, dispanserCode, diagnosisTypeCode):
        key = (eventId, dispanserCode, diagnosisTypeCode)
        date = self.diagnosticDateCache.get(key)

        if not date:
            date = QDate()
            stmt = """SELECT endDate
                        FROM Diagnostic
                        LEFT JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id= rbDiagnosisType.id
                        LEFT JOIN rbDispanser ON Diagnostic.dispanser_id = rbDispanser.id
                        WHERE Diagnostic.event_id = %d AND rbDispanser.code = %s
                            AND rbDiagnosisType.code = %s
                        """ % (eventId, dispanserCode, diagnosisTypeCode)

            query = QtGui.qApp.db.query(stmt)

            while query.next():
                record = query.record()

                if record:
                    date = forceDate(record.value(0))

                    if date.isValid():
                        self.diagnosticDateCache[key] = date
                        break

        return date

# *****************************************************************************************

    def getDispanserBegDate(self, eventId):
        for diagCode in ('1', '2'):
            for code in ('2', '6', '7'):
                date = self.getDiagnosticDate(eventId, code, diagCode)

            if date.isValid():
                return date

        return QDate()


    def getDispanserExamDate(self, eventId):
        for diagCode in ('1', '2'):
            date = self.getDiagnosticDate(eventId, '6', diagCode)

            if date.isValid():
                return date

        return QDate()


    def getDispanserEndDateAndReason(self, eventId):
        for diagCode in ('1', '2'):
            for code in ('3', '4', '5'):
                date = self.getDiagnosticDate(eventId, code, diagCode)

                if date.isValid():
                    return (date, code)

        return (QDate(), None)

# *****************************************************************************************

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        self.log(u'Выгружаем счет в формате ДД-2010.')

        lpuId = QtGui.qApp.currentOrgId()
        lpuOKPO = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'OKPO'))
        lpuOGRN = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'OGRN'))
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'infisCode'))
        self.log(u'ЛПУ: ОКПО "%s", ОГРН "%s", код инфис: "%s".' % (lpuOKPO, lpuOGRN, lpuCode))
        self.exportedActionsList = []

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан код инфис', True)
            if not self.ignoreErrors:
                return

        dbf, query = self.prepareToExport()
        accDate, accNumber, exposeDate, contractId =\
            getAccountInfo(self.parent.accountId)
        strAccNumber = accNumber if trim(accNumber) else u'б/н'
        strContractNumber = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'number')) if contractId else u'б/н'

        self.hospitalDirectionActionTypeId = self.getHospitalDirectionTypeId()

        if not self.hospitalDirectionActionTypeId:
            self.log(u'Не найден тип действия "(1-1) Направление.'\
                u'(1) Направление на госпитализацию".')
            if not self.ignoreErrors:
                return

        if self.idList:
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), lpuCode, lpuOKPO, lpuOGRN,
                                accNumber, strContractNumber, exposeDate)
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        #self.processCounts(dbf)
        for x in dbf:
            x.close()


    def createDbf(self):
        return (self.createRDbf(),
                    self.createVDbf(),
                    self.createSDbf(),
                    )


    def createRDbf(self):
        u""" Создает структуру dbf для файла типа R (карта диспансеризации) """

        dbfName = os.path.join(self.parent.getTmpDir(), 'R'+self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_HOSP', 'C', 3),   # Код ЛПУ, где проведена дополнительная диспансеризация
            ('OGRN', 'C', 15),       # Код ОГРН  ЛПУ, где проведена дополнительная диспансеризация
            ('CODE_COUNT', 'C', 10), # Номер счета представляемого в фонд
            ('DATE_LOW', 'D', 8),    # Начальная дата интервала дат выписки
            ('DATE_UP', 'D', 8),     # Конечная дата интервала дат выписки
            ('SNILS', 'C', 14),      # Страховой номер индивидуального лицевого счета (СНИЛС)  пациента
            ('SERPOL', 'C', 10),     # Серия полиса
            ('NMBPOL', 'C', 16),     # Номер полиса
            ('DOGOVOR', 'C', 10),    # Номер договора по ОМС
            ('ECONOM_ACT', 'C', 15), # Код ОКВЭД предприятия
            ('INS', 'C', 2),         # Код страхователя (по справочнику фонда)
            ('FAM', 'C', 40),        # Фамилия пациента
            ('IMM', 'C', 40),        # Имя пациента
            ('OTC', 'C', 40),        # Отчество пациента
            ('BIRTHDAY', 'D', 8),    # Дата рождения пациента
            ('SEX', 'C', 1),         # Пол пациента(«М», «Ж»)
            ('TAUN', 'C', 3),        # Код населенного пункта проживания пациента по справочнику фонда
            ('ADDRESS', 'C', 75),    # Адрес места жительства
            ('CARD', 'C', 10),       # Номер карты
            ('PAT_DIAG', 'C', 6),    #	Заключительный диагноз (по справочнику МКБ10)
            ('DISP_TYPE', 'C', 1),   #	Тип диспансеризации:           - постоянного динамического наблюдения – «1»
                                     # - дополнительной диспансеризации       - «2»,
                                     # - периодического медицинского осмотра  - «3»,
                                     # - дополнительного медицинского осмотра - «4»
            ('LPU', 'C', 3),         # ЛПУ приписки  по справочнику фонда (указан в полисе)
            ('DATE_B', 'D', 8),      # Дата начала диспансеризации
            ('DATE_E', 'D', 8),      # Дата окончания диспансеризации
            ('DEAD', 'C', 1),        # Флаг летального исхода («1»-нет / «2»- да)
            ('SSD', 'C', 14),        # СНИЛС врача, определившего окончательный диагноз по МКБ10
            ('DIRECT', 'C', 1),      # Куда направлен по результатам ДД:
                                     # - не нуждается в направлении - «1»
                                     # - на госпитализацию в стационар «2»
                                     # - в орган управления для направления на ДВМП - «3»
            ('TALON_HOSP', 'C', 6),  # Номер направления на госпитализацию
            ('DIAG_HOSP', 'C', 6),   # Диагноз (по справочнику МКБ10) госпитализации
            )
        return dbf


    def createVDbf(self):
        u"""Создает структуру dbf для файла типа V (посещения врачей-специалистов)"""

        dbfName = os.path.join(self.parent.getTmpDir(), 'V'+self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_HOSP', 'C', 3),   # Код ЛПУ, где проведена дополнительная диспансеризация
            ('CODE_COUNT', 'C', 10), # Номер счета представляемого в фонд
            ('CARD', 'C',	10),     # Номер карты
            ('SPEC', 'C',	3),      # Код профиля специалиста
            ('SSD', 'C',	14),     # СНИЛС врача - специалиста
            ('EXAM_DATE', 'D',	8),  # Дата проведения осмотра
            ('DIAG', 'C',	6),      # Диагноз по справочнику МКБ10
            ('DIAG_GRUP', 'C',	1),  # Стадия заболевания ( «1»-ранняя / «2»-поздняя)
            ('FIRST', 'C',	1),      # Впервые выявлено– «1» /ранее известно – «0»
            ('HEALTHGRUP', 'C',	1),  # Группа здоровья:
                                     # - практически здоров                             – «1»
                                     # - риск развития заболевания                      – «2»
                                     # - необходимо амбулаторное обследование и лечение - «3»
                                     # - необходимо стационарное обследование и лечение - «4»
                                     # - нуждается в ВДМП           - «5»
            ('DISPDATE_B', 'D',	8),  # Дата постановки на Д-учет
            ('DISPDATE_E', 'D',	8),  # Дата снятия с Д-учета
            ('DIAG_6M', 'C',	6),  # Диагноз по справочнику МКБ10 через 6 месяцев
            ('DIAG_TO6M', 'C',	6),  # Диагноз по справочнику МКБ10 в течение 6 месяцев
            ('REASN', 'C',	1),      # Причина снятия с Д-учета:
                                     # - выздоровление  - «1»
                                     # - выбытие        - «2»
                                     # - смерть         - «3»
            ('REASN_6M', 'C',	1),  # Снят с Д-учета:
                                     # - в течении 6 мес. после ДД  - «1»
                                     # - позже 6 мес. после ДД         - «2»
            ('SAN_KUR', 'C', 1),     # Санаторно-курортное лечение ( «1»-да / «0»-нет)
            )
        return dbf


    def createSDbf(self):
        u"""Создает структуру dbf для файла типа S (параклинические услуги) """

        dbfName = os.path.join(self.parent.getTmpDir(), 'S'+self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_HOSP', 'C', 3),   # Код ЛПУ пребывания по справочнику фонда
            ('CODE_COUNT', 'C', 10), # Номер счета представляемого в фонд
            ('CARD', 'C', 10),       # Номер карты
            ('ID_SERVICE', 'C', 9),  # Код услуги
            ('SERV_DATE', 'D', 8),   # Дата услуги
            ('RESULTDATE', 'D', 8)   # Дата результата
            )
        return dbf


    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """SELECT
            Account_Item.id        AS accountItem_id,
            Account_Item.master_id AS account_id,
            Account_Item.event_id  AS event_id,
            Event.client_id        AS client_id,
            Event.`order`          AS `order`,
            Client.lastName        AS lastName,
            Client.firstName       AS firstName,
            Client.patrName        AS patrName,
            Client.birthDate       AS birthDate,
            Client.sex             AS sex,
            Client.SNILS           AS SNILS,
            ClientPolicy.serial    AS policySerial,
            ClientPolicy.number    AS policyNumber,
            ClientPolicy.note      AS policyNote,
            ClientPolicy.begDate   AS policyBegDate,
            ClientPolicy.endDate   AS policyEndDate,
            Insurer.infisCode      AS policyInsurer,
            Insurer.INN            AS insurerINN,
            Insurer.shortName      AS insurerName,
            Insurer.OKATO          AS insurerOKATO,
            Insurer.OGRN           AS insurerOGRN,
            rbPolicyType.code      AS policyType,
            ClientDocument.serial  AS documentSerial,
            ClientDocument.number  AS documentNumber,
            rbDocumentType.code    AS documentType,
            rbDocumentType.regionalCode AS documentRegionalCode,
            RegAddressHouse.KLADRCode AS regKLADRCode,
            RegAddressHouse.KLADRStreetCode AS regKLADRStreetCode,
            RegAddressHouse.number AS regNumber,
            RegAddressHouse.corpus AS regCorpus,
            RegAddress.flat        AS regFlat,
            ClientRegAddress.freeInput AS regFreeInput,
            LocAddressHouse.KLADRCode AS locKLADRCode,
            LocAddressHouse.KLADRStreetCode AS locKLADRStreetCode,
            LocAddressHouse.number AS locNumber,
            LocAddressHouse.corpus AS locCorpus,
            LocAddress.flat        AS locFlat,
            ClientLocAddress.freeInput AS locFreeInput,
            ClientContact.contact  AS phoneNumber,
            ClientWork.post        AS clientPost,
            work.fullName          AS clientWorkOrgName,
            work.INN               AS clientWorkOrgINN,
            work.infisCode         AS clientWorkInfisCode,
            work.OKVED             AS clientWorkOKVED,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.infis,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                ) AS service,
              IF(Account_Item.visit_id IS NOT NULL, Visit.person_id,
                    IF(Account_Item.action_id IS NOT NULL,
                            IF(Action.person_id IS NOT NULL, Action.person_id, Action.setPerson_id), Event.execPerson_id)
                ) AS execPersonId,
              Visit.date AS visitDate,
              Action.endDate AS actionDate,
              Diagnosis.MKB          AS MKB,
              diagnosisPerson.SNILS AS diagnosisPersonSNILS,
              Diagnostic.hospital,
              Diagnostic.sanatorium,
              MKB_Tree.Prim               AS prim,
              Event.setDate          AS begDate,
              Event.execDate         AS endDate,
              Account_Item.amount    AS amount,
              Account_Item.`sum`     AS `sum`,
              Account_Item.tariff_id AS tariff_id,
              Person.code AS personCode,
              Person.regionalCode AS personRegionalCode,
              rbSpeciality.regionalCode AS specialityCode,
              setOrgStruct.infisCode AS setOrgStructCode,
              EventType.code AS eventTypeCode,
              IF(rbDiagnosticResult.code IS NULL, EventResult.code, rbDiagnosticResult.code) AS resultCode,
            OrgStructure.infisCode,
                OrgStructure.infisInternalCode,
                OrgStructure.infisDepTypeCode,
                OrgStructure.infisTariffCode,
                OrgStructure.type AS lpuType,
                rbHealthGroup.code AS healthGroupCode,
                rbDispanser.code AS dispanserCode,
                rbDiseaseCharacter.code AS characterCode,
                rbDiseaseStage.code AS stageCode
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                      ClientPolicy.id = (SELECT MAX(CP.id)
                                         FROM   ClientPolicy AS CP
                                         LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                                         WHERE  CP.client_id = Client.id AND CP.deleted=0 AND CPT.code IN ('1','2'))
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
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
            LEFT JOIN ClientAddress ClientLocAddress ON ClientLocAddress.client_id = Client.id AND
                      ClientLocAddress.id = (SELECT MAX(CLA.id)
                                         FROM   ClientAddress AS CLA
                                         WHERE  CLA.type = 1 AND CLA.client_id = Client.id AND CLA.deleted=0)
            LEFT JOIN Address   RegAddress ON RegAddress.id = ClientRegAddress.address_id
            LEFT JOIN AddressHouse RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
            LEFT JOIN Address   LocAddress ON LocAddress.id = ClientLocAddress.address_id
            LEFT JOIN AddressHouse LocAddressHouse ON LocAddressHouse.id = LocAddress.house_id
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                      AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code= '1')
                                      AND Diagnostic.deleted = 0)
            LEFT JOIN ClientContact  ON ClientContact.client_id = Client.id AND
                      ClientContact.id = (SELECT MAX(CC.id)
                                         FROM   ClientContact AS CC
                                         LEFT JOIN rbContactType ON CC.contactType_id= rbContactType.id
                                         WHERE  rbContactType.code IN (1,2,3) AND CC.client_id = Client.id AND CC.deleted=0)
            LEFT JOIN ClientWork ON ClientWork.client_id=Event.client_id AND
                        ClientWork.id = (SELECT max(CW.id)
                                         FROM ClientWork AS CW
                                         WHERE CW.client_id=Client.id AND CW.deleted=0)
            LEFT JOIN Organisation AS work ON work.id=ClientWork.org_id AND work.deleted = 0
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN MKB_Tree       ON MKB_Tree.DiagID = Diagnosis.MKB
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbDiseaseCharacter ON Diagnosis.character_id = rbDiseaseCharacter.id
            LEFT JOIN rbHealthGroup ON Diagnostic.healthGroup_id = rbHealthGroup.id
            LEFT JOIN rbDispanser ON rbDispanser.id = Diagnostic.dispanser_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN OrgStructure AS setOrgStruct ON Person.orgStructure_id = setOrgStruct.id
            LEFT JOIN Person AS diagnosisPerson ON diagnosisPerson.id = Diagnosis.person_id
            LEFT JOIN rbDiseaseStage ON Diagnostic.stage_id = rbDiseaseStage.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
        """ % tableAccountItem['id'].inlist(self.idList)
#            ORDER BY insurerName
        return db.query(stmt)

# *****************************************************************************************

    def createDiagnosticQuery(self, eventId):
        db = QtGui.qApp.db
        table = db.table('Diagnostic')
        stmt = """
        SELECT  Diagnostic.person_id,
                    Diagnostic.setDate,
                    Diagnostic.endDate,
                    Diagnostic.sanatorium,
                    Diagnosis.MKB,
                    rbDiseaseStage.code AS stageCode,
                    rbHealthGroup.code AS healthGroupCode,
                    rbDiseaseCharacter.code AS characterCode
        FROM Diagnostic
        LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
        LEFT JOIN rbDiseaseStage ON Diagnostic.stage_id = rbDiseaseStage.id
        LEFT JOIN rbHealthGroup ON Diagnostic.healthGroup_id = rbHealthGroup.id
        LEFT JOIN rbDiseaseCharacter ON Diagnostic.character_id = rbDiseaseCharacter.id
        WHERE Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1', '2'))
            AND %s
        """ % db.joinAnd([table['deleted'].eq(0), table['event_id'].eq(eventId)])
        return db.query(stmt)

# *****************************************************************************************

    cachePersonSNILSandSpecCodes = {}

    def getPersonSNILSandSpecCodes(self, id):
        (specCode, SNILS) = self.cachePersonSNILSandSpecCodes.get(id, ('', ''))

        if ((specCode == '') or (SNILS == '')) and id:
            db = QtGui.qApp.db
            table  = db.table('Person')
            record = db.getRecord(table, 'speciality_id, SNILS', id)
            specId = forceRef(record.value('speciality_id'))
            SNILS = forceString(record.value('SNILS'))

            if specId:
                specCode = forceString(db.translate('rbSpeciality','id', specId,'regionalCode'))
                self.cachePersonSNILSandSpecCodes[id] = (specCode, SNILS)

        return (specCode, SNILS)

# *****************************************************************************************

    def process(self, dbf, record, codeLPU, OKPO, OGRN, accNumber, contractNumber, exposeDate):
        birthDate = forceDate(record.value('birthDate'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        # Номер стат.талона
        eventId = forceRef(record.value('event_id'))
        clientId = forceRef(record.value('client_id'))
        clientAttachRecord = getAttachRecord(clientId, False)
        attachOrgCode = ''
#        clientDDAttachRecord = getAttachRecord(clientId, True)

        if clientAttachRecord:
            clientAttachOrgId = clientAttachRecord.get('LPU_id', None)

            if clientAttachOrgId:
                attachOrgCode = forceString(QtGui.qApp.db.translate('Organisation', \
                'id', clientAttachOrgId, 'infisCode'))
            else:
                self.log(u'В записи прикрепления отсутствует код ЛПУ.')

        else:
            self.log(u'Внимание: не задано ЛПУ постоянного прикрепления пациента. clientId=%d' % clientId)

        (dbfR, dbfV, dbfS) = dbf

        dbfRecord = dbfR.newRecord()
        #	Код ЛПУ, где проведена дополнительная диспансеризация
        dbfRecord['CODE_HOSP'] = codeLPU
        # Код ОГРН  ЛПУ, где проведена дополнительная диспансеризация
        dbfRecord['OGRN'] = OGRN
        # Номер счета представляемого в фонд
        dbfRecord['CODE_COUNT'] = accNumber
        # Начальная дата интервала дат выписки
        dbfRecord['DATE_LOW'] = pyDate(firstMonthDay(endDate))
        # Конечная дата интервала дат выписки
        dbfRecord['DATE_UP'] = pyDate(exposeDate if exposeDate and exposeDate.isValid() else QDate.currentDate())
        # Страховой номер индивидуального лицевого счета (СНИЛС)  пациента
        dbfRecord['SNILS'] = formatSNILS(forceString(record.value('SNILS')))
        # Серия полиса
        dbfRecord['SERPOL'] = forceString(record.value('policySerial'))
        # Номер полиса
        dbfRecord['NMBPOL'] = forceString(record.value('policyNumber'))
        # Номер договора
        dbfRecord['DOGOVOR'] = forceString(record.value('policyNote'))
        # Код ОКВЭД предприятия
        dbfRecord['ECONOM_ACT'] = forceString(record.value('clientWorkOKVED'))
        # Код страхователя (по справочнику фонда)
        dbfRecord['INS'] = forceString(record.value('clientWorkInfisCode'))
        # Фамилия пациента
        dbfRecord['FAM'] = nameCase(forceString(record.value('lastName')))
        # Имя пациента
        dbfRecord['IMM'] = nameCase(forceString(record.value('firstName')))
        # Отчество пациента
        dbfRecord['OTC'] =  nameCase(forceString(record.value('patrName')))
        # Дата рождения пациента
        dbfRecord['BIRTHDAY'] = pyDate(birthDate)
        # Пол пациента   («М», «Ж»)
        dbfRecord['SEX'] = formatSex(record.value('sex')).upper()
        locKLADRCode = forceString(record.value('locKLADRCode'))
        KLADRCode = forceString(record.value('regKLADRCode'))

        if (not locKLADRCode) or locKLADRCode == '':
            locKLADRCode = KLADRCode

        if not locKLADRCode or locKLADRCode == '':
            freeInput = forceString(record.value('locFreeInput'))
            if freeInput == '':
                freeInput = forceString(record.value('regFreeInput'))

            if freeInput == '':
                self.log(u'Отсутвует КЛАДР адрес проживания и регистрации для клиента clientId=%d' % clientId)
            else:
                self.log(u'Для клиента clientId=%d адрес заполнен в свободной форме.' % clientId)
                dbfRecord['ADDRESS'] = freeInput
        else:
            # Код населенного пункта проживания пациента по справочнику фонда
            townCode = forceString(QtGui.qApp.db.translate('kladr.KLADR', 'CODE', locKLADRCode, 'infis', idFieldName='CODE'))
            dbfRecord['TAUN'] = townCode
            if townCode == "":
                self.log(u'Не задан инфис код для города "%s", clientId=%d' %\
                        (locKLADRCode, clientId))
            locKLADRStreetCode = forceString(record.value('locKLADRStreetCode'))
            KLADRStreetCode = forceString(record.value('regKLADRStreetCode'))

            number = forceString(record.value('locNumber'))
            corpus = forceString(record.value('locCorpus'))
            flat = forceString(record.value('locFlat'))

            if (not locKLADRStreetCode) or locKLADRStreetCode == '':
                locKLADRStreetCode = KLADRStreetCode
                number = forceString(record.value('regNumber'))
                corpus = forceString(record.value('regCorpus'))
                flat = forceString(record.value('locFlat'))

            # Адрес места жительства
            dbfRecord['ADDRESS'] = myFormatAddress(locKLADRCode,
                    locKLADRStreetCode, number, corpus, flat)

        # Номер карты
        dbfRecord['CARD'] = eventId
        # Заключительный диагноз (по справочнику МКБ10)
        dbfRecord['PAT_DIAG'] = forceString(record.value('MKB'))
        # Тип диспансеризации:
        #   - постоянного динамического наблюдения – «1»
        #   - дополнительной диспансеризации       - «2»,
        #   - периодического медицинского осмотра  - «3»,
        #   - дополнительного медицинского осмотра - «4»
        dispType = '2'

#        if clientDDAttachRecord:
#            dispType = self.mapAttachCodeToDispType.get(clientDDAttachRecord['code'], '')
#        else:
#            self.log(u'Отстутсвует временное прикрепление для клиента clientId=%d,'\
#                u' поле "Тип диспансеризации" не заполнено.' % clientId)

        dbfRecord['DISP_TYPE'] = dispType
        # ЛПУ приписки  по справочнику фонда (указан в полисе)
        dbfRecord['LPU'] = attachOrgCode
        # Дата начала диспансеризации
        dbfRecord['DATE_B'] = pyDate(begDate)
        # Дата окончания диспансеризации
        dbfRecord['DATE_E'] = pyDate(endDate)
        # Флаг летального исхода («1»-нет / «2»- да)
        deadFlag = '2' if forceString(record.value('resultCode')) == '99' else '1'
        dbfRecord['DEAD'] = deadFlag
        # СНИЛС врача, определившего окончательный диагноз по МКБ10
        dbfRecord['SSD'] = formatSNILS(forceString(record.value('diagnosisPersonSNILS')))
        # Куда направлен по результатам ДД:
        #   - не нуждается в направлении - «1»
        #   - на госпитализацию в стационар «2»
        #   - в орган управления для направления на ДВМП - «3»
        healthGroup = forceInt(record.value('healthGroupCode'))
        hospital = forceInt(record.value('hospital'))
        direct = '1'

        if (healthGroup == 4) and (hospital in (2, 3)):
            direct = '2'
        elif healthGroup == 5:
            direct = '3'

        dbfRecord['DIRECT'] = direct

        if direct != '1':
            # Номер направления на госпитализацию
            dbfRecord['TALON_HOSP'] = self.getHospitalDirectionNumberStr(eventId)

            if dbfRecord['TALON_HOSP'] == '':
                self.log(u'Отсутствует номер направления на госпитализацию для клиента clientId=%d' % clientId)

            # Диагноз (по справочнику МКБ10) госпитализации
            dbfRecord['DIAG_HOSP'] =  forceString(record.value('MKB'))

        dbfRecord.store()

        diagnosticQuery = self.createDiagnosticQuery(eventId)

        if diagnosticQuery:
            while diagnosticQuery.next():
                diagRec = diagnosticQuery.record()

                if diagRec:
                    dbfRecord = dbfV.newRecord()
                    # Код ЛПУ, где проведена дополнительная диспансеризация
                    dbfRecord['CODE_HOSP'] = codeLPU
                    # Номер счета представляемого в фонд
                    dbfRecord['CODE_COUNT'] = accNumber
                    # Номер карты
                    dbfRecord['CARD'] = eventId
                    # Код профиля специалиста
                    (specCode, SNILS) = self.getPersonSNILSandSpecCodes(forceRef(diagRec.value('person_id')))
                    dbfRecord['SPEC']  = specCode
                    # СНИЛС врача - специалиста
                    dbfRecord['SSD'] = formatSNILS(SNILS)
                    # Дата проведения осмотра
                    servDate = forceDate(diagRec.value('endDate'))

                    if not servDate.isValid():
                        servDate = forceDate(diagRec.value('setDate'))

                        if not servDate.isValid():
                            servDate = endDate

                    if not servDate.isValid():
                        self.log(u'Не задана дата услуги: accountItemId=%d,'\
                            u' eventId=%d.' % (forceRef(record.value('accountItem_id')), eventId))

                    dbfRecord['EXAM_DATE'] = pyDate(servDate)
                    # Диагноз по справочнику МКБ10
                    mkb = forceString(diagRec.value('MKB'))
                    dbfRecord['DIAG'] = mkb
                    # Стадия заболевания ( «1»-ранняя / «2»-поздняя)
                    if forceString(diagRec.value('stageCode')) != '':
                        stageCode = forceInt(diagRec.value('stageCode'))
                        dbfRecord['DIAG_GRUP'] = forceString(stageCode) if stageCode < 2 else ''
                    # Впервые выявлено– «1» /ранее известно – «0»
                    if forceString(diagRec.value('characterCode')) != '':
                        characterCode = forceInt(diagRec.value('characterCode'))
                        dbfRecord['FIRST'] = '1' if characterCode < 3 else '0'
                    elif self.chkMarkFirstForMKBZ00.isChecked() and (mkb!= '' and mkb[0] == 'Z'):
                        dbfRecord['FIRST'] = '0'
                    # Группа здоровья:
                    #   - практически здоров                          – «1»
                    #   - риск развития заболевания               – «2»
                    #   - необходимо амбулаторное обследование и лечение       - «3»
                    #   - необходимо стационарное обследование и лечение       - «4»
                    #   - нуждается в ВДМП           - «5»
                    hg = forceInt(diagRec.value('healthGroupCode'))
                    dbfRecord['HEALTHGRUP'] = hg if hg < 6 else 2
                    # Дата постановки на Д-учет
                    dbfRecord['DISPDATE_B'] = pyDate(self.getDispanserBegDate(eventId))
                    # Дата снятия с Д-учета
                    dispEndDate, reasonCode = self.getDispanserEndDateAndReason (eventId)
                    if reasonCode and dispEndDate.isValid():
                        dbfRecord['DISPDATE_E'] = pyDate(dispEndDate)
                    # Диагноз по справочнику МКБ10 через 6 месяцев
                    #dbfRecord['DIAG_6M'] = forceString(record.value('MKB'))
                    # Диагноз по справочнику МКБ10 в течение 6 месяцев
                    #dbfRecord['DIAG_TO6M'] = forceString(record.value('MKB'))
                    # Причина снятия с Д-учета:
                    #   - выздоровление  - «1»
                    #   - выбытие             - «2»
                    #   - смерть                - «3»
                        dbfRecord['REASN'] = self.mapDispReasonCode.get(reasonCode, '')
                    # Снят с Д-учета:
                    #   - в течении 6 мес. после ДД  - «1»
                    #   - позже 6 мес. после ДД         - «2»
                    #dbfRecord['REASN_6M'] = '1'
                    # Санаторно-курортное лечение ( «1»-да / «0»-нет)
                    sanatorium = forceInt(diagRec.value('sanatorium'))
                    dbfRecord['SAN_KUR'] = '1' if sanatorium > 0 else '0'
                    dbfRecord.store()

        self.exportServices(dbfS, codeLPU, accNumber, eventId, endDate)
        dbfRecord.store()

# *****************************************************************************************

    def getServicesQuery(self, eventId, endDate):
        stmt = """SELECT Action.id,
            Action.endDate,
            ActionType.code
        FROM Action
        LEFT JOIN ActionType ON Action.actionType_id = ActionType.id
        WHERE Action.event_id = '%d' AND Action.endDate <= '%s' AND Action.deleted = '0'
            AND ActionType.class = '1'
        """ % (eventId, endDate.toString(Qt.ISODate))
        return QtGui.qApp.db.query(stmt)

# *****************************************************************************************

    def exportServices(self, dbfS, codeLPU, accNumber, eventId, endDate):
        query = self.getServicesQuery(eventId, endDate)

        while query.next():
            record = query.record()

            if record:
                actionId = forceRef(record.value('id'))

                if not (actionId in self.exportedActionsList):
                    actEndDate = pyDate(forceDate(record.value('endDate')))
                    actCode = forceString(record.value('code'))

                    dbfRecord = dbfS.newRecord()
                    # Код ЛПУ пребывания по справочнику фонда
                    dbfRecord['CODE_HOSP'] = codeLPU
                    # Номер счета представляемого в фонд
                    dbfRecord['CODE_COUNT'] = accNumber
                    # Номер карты
                    dbfRecord['CARD'] = eventId
                    # Код услуги
                    dbfRecord['ID_SERVICE'] = forceString(record.value('code'))
                    # Дата услуги
                    dbfRecord['SERV_DATE'] = actEndDate
                    # Дата результата
                    dbfRecord['RESULTDATE'] = actEndDate
                    dbfRecord.store()
                    self.exportedActionsList.append(actionId)


# *****************************************************************************************

    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.abort()


class CExportR51DDPage2(QtGui.QWizardPage, Ui_ExportR51DDPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R51DDExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        baseName = self.parent.page1.getDbfBaseName()
        for src in ('R', 'V', 'S'):
            srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                    os.path.basename(src+baseName))
            dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                    os.path.basename(src+baseName))
            success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

            if not success:
                break

        if success:
            QtGui.qApp.preferences.appPrefs['R51DDExportDir'] = toVariant(self.edtDir.text())
            self.wizard().setAccountExposeDate()
        return success


    @QtCore.pyqtSlot(QString)
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ОМС Мурманской области',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
