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
from Registry.Utils    import getAttachRecord
from Exchange.Utils    import getClientRepresentativeInfo
from Accounting.Utils  import CTariff

from Ui_ExportR51OMSProcessPage import Ui_ExportR51OMSProcessPage
from Ui_ExportR51OMSOutDirPage import Ui_ExportR51OMSOutDirPage


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number, exposeDate, contract_id,  settleDate', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        contractId = forceRef(accountRecord.value('contract_id'))
        number = forceString(accountRecord.value('number'))
        settleDate = forceDate(accountRecord.value('settleDate'))
    else:
        number = ''
        date = exposeDate = contractId = settleDate = None
    return date, number, exposeDate, contractId, settleDate


def exportR51OMS(widget, accountId, accountItemIdList):
    wizard = CExportWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()

class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportR51OMSProcessPage(self)
        self.page2 = CExportR51OMSOutDirPage(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта в ОМС Мурманской области')
        self.dbfFileName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId, settleDate = getAccountInfo(accountId)
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
            self.tmpDir = QtGui.qApp.getTmpDir('R51OMS')
        return self.tmpDir


    def getFullDbfFileName(self): #TODO: atronah: удалить к чертям почти во всех экспортах (в которых она не используется) 
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

class CExportR51OMSProcessPage(QtGui.QWizardPage, Ui_ExportR51OMSProcessPage):
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
        self.tariffCache = {}
        self.parent = parent
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51OMSIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51OMSVerboseLog', 'False')))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.knownR51OMSCodes = {}
        self.educationIdList = []
        self.mapPersonSpecInfisCode = {}
        self.exportedEventSet = set()
        self.validActionTypeIdList = []
        self.accSystemId = None
        self.isAddInfAsAliens = False


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
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
        self.accSystemId = forceRef(QtGui.qApp.db.translate('rbAccountingSystem', 'code', '51',  'id'))

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

# *****************************************************************************************

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        self.isAddInfAsAliens = self.chkAddInfAsAliens.isChecked()
        self.isClinicalExamination = self.chkClinicalExamination.isChecked()
        ref = None
        record = QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code=\'6000000\' AND class=\'2\'', 'id')

        if record:
            ref = forceRef(record.value(0))

        if not record or not ref:
            self.log(u'В справочнике типов действий (ActionType)'
                u' отсутствует запись с кодом 6000000, класс "лечение"'
                u' (Простые медицинские услуги, оплачиваемые в составе...)')
            if not self.ignoreErrors:
                self.abort()
                return

        self.validActionTypeIdList.append(ref)
        lpuId = QtGui.qApp.currentOrgId()
        lpuOKPO = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'OKPO'))
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'infisCode'))
        lpuOGRN = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'OGRN'))
        self.log(u'ЛПУ: ОКПО "%s", ОГРН "%s",код инфис: "%s".' % (lpuOKPO, lpuOGRN,  lpuCode))

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан код инфис', True)
            if not self.ignoreErrors:
                return

        dbf, query = self.prepareToExport()
        accDate, accNumber, exposeDate, contractId, settleDate =\
            getAccountInfo(self.parent.accountId)

        strAccNumber = lpuCode + forceString(settleDate.toString('MMyy'))
        if contractId:
            contractRecord = QtGui.qApp.db.getRecord('Contract LEFT JOIN Organisation ON Organisation.id = Contract.payer_id',
                                                     'Contract.number AS contractNumber, Organisation.infisCode AS payerInfisCode',
                                                     contractId)
            strContractNumber = forceString(contractRecord.value('contractNumber'))
            strAccNumber += forceString(contractRecord.value('payerInfisCode'))
        else:
            strContractNumber = u'б/н'
            strAccNumber += '00'
        strAccNumber = strAccNumber.ljust(10, '0')[:10]
        self.exportedEventSet = set()
        #self.eventMesSums = {}
        mapEventIdToSum = self.getEventsSummaryPrice()

        #self.processAddServ(dbf, contractId)

        if self.idList:
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), lpuCode, lpuOKPO, lpuOGRN,
                                strAccNumber, strContractNumber, exposeDate,
                                mapEventIdToSum, accDate, settleDate)
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        self.processAddServ(dbf, contractId)
        for x in dbf:
            x.close()


    def createDbf(self):
        return (self.createAliensDbf(), self.createServiceDbf(),
                    self.createAddInfDbf(), self.createAddServDbf()
                    )


    def createAliensDbf(self):
        """ Создает структуру dbf для ALIENS.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'ALIENS.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_HOSP', 'C', 3),     # 1. Код ЛПУ пребывания по справочнику фонда
            ('CODE_COUNT', 'C', 10),   # 2. Номер счета представляемого в СМО
            ('DATE_LOW', 'D', 8),      # 3. Начальная дата интервала дат выписки
            ('DATE_UP', 'D', 8),       # 4. Конечная дата интервала дат выписки
            ('CARD', 'C', 10),         # 5. Номер статталона
            ('INS', 'C', 2),           # 6. Код СМО (по справочнику фонда)
            ('SERPOL', 'C', 10),       # 7. Серия полиса
            ('NMBPOL', 'C', 20),       # 8. Номер полиса
            #('DOGOVOR', 'C', 10),      # 9. Номер договора
            ('WORK', 'C', 1),          # 10. Статус пациента. 0-неработающий, 1-работающий, 2-учащийся очной формы обучения, 3-инвалид ВОВ
            ('DATIN', 'D', 8),         # 11. Дата поступления
            ('DATOUT', 'D', 8),        # 12. Дата выписки
            ('DIAG', 'C', 6),          # 13. Диагноз МКБ Х
            ('DS0', 'C', 6),           # 14. Диагноз первичный
            #('RESULT', 'C', 2),        # 15. Исход по справочнику фонда
            #('STOIM', 'N', 10, 2),     # 16. Суммарная стоимость услуг
            #('STOIM_V', 'N', 10, 2),   # 17. Суммарная стоимость услуг по расчетным данным Фонда (для ЛПУ сумма=0)
            ('FAM', 'C', 40),          # 18. Фамилия пациента
            ('IMM', 'C', 40),          # 19. Имя пациента
            ('OTC', 'C', 40),          # 20. Отчество пациента
            ('SER_PASP', 'C', 8),      # 21. Серия документа, удостоверяющего личность
            ('NUM_PASP', 'C', 8),         # 22. Номер документа, удостоверяющего личность
            ('TYP_DOC', 'N', 2),       # 23. Тип документа, удостоверяющего личность (приложение «Типы документов»)
            ('SS', 'C', 14),           # 24. Страховой номер индивидуального лицевого счета (СНИЛС)
            #('PIN', 'C', 16),          # 25. Персональный  индивидуальный номер застрахованного по ОМС
            ('BIRTHDAY', 'D', 8),      # 26. Дата рождения пациента
            ('SEX', 'C', 1),           # 27. Пол пациента («М», «Ж»)
            ('TAUN', 'C', 3),          # 28. Код населенного пункта проживания пациента по справочнику фонда
            ('MASTER', 'C', 3),        # 29. Код ЛПУ приписки
            ('DS_S', 'C', 6),          # 30. Код диагноза сопутствующего заболевания (состояния) по МКБ-10
            ('STOIM_S', 'N', 10, 2),   # 31. Сумма из средств Федеральных субвенций
            ('STOIM_R', 'N', 10, 2),   # 32. Сумма из средств Субъекта РФ (статья 6 – иные расходы)
            #('STOIM_F', 'N', 10, 2),   # 33. Сумма доплаты из средств Федерального фонда ОМС
            ('TPOLIS', 'N', 1),        # 34. Тип полиса:     1 – старого образца, 2 – временное свидетельство, 3 – нового образца
            ('PRIZN_ZS', 'N', 1),      # 35. «0» - не участвует в диспансеризации; «1» - признак законченного случая при проведении диспансеризации 14-летних подростков; «2» - признак законченного случая при проведении  ежегодной диспансеризации студентов
            ('RSLT', 'N', 3),          # 30. Результат обращения/госпитализации. (справочник V009)
            ('ISHOD', 'N', 3),         # 31. Исход заболевания. (справочник V012)
            ('DET', 'N', 1),           # 32. Признак детского профиля. 0-нет, 1-да. Зависит от профиля мед помощи.
            ('P_CODE', 'C', 25),       # 33. Код врача, закрывшего историю болезни.
            #('STOIM_ZS', 'N', 10, 2),  # 36. Сумма доплаты за законченный случай при проведении диспансеризации 14-летних подростков или студентов
            ('PURPOSE', 'N', 2),       # 37. Цель обращения (1 - профилактическая, 2 - неотложная, 3 - по заболеванию)
            )

        return dbf


    def createServiceDbf(self):
        """ Создает структуру dbf для SERVICE.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'SERVICE.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CARD', 'C', 10),         # 1. Номер статталона
            ('CODE_HOSP', 'C', 3),     # 2. Код ЛПУ пребывания по справочнику фонда
            ('CODE_COUNT', 'C', 10),   # 3. Номер счета представляемого в СМО
            ('P_CODE', 'C', 7),        # 4. Личный код  медицинского работника, оказавшего услугу
            ('SPEC', 'C', 3),          # 5. Код специальности медицинского работника, оказавшего услугу
            ('SERVICE', 'C', 15),      # 6. Код услуги
            ('UNITS', 'N', 3),         # 7. Кол-во услуг
            ('SERV_DATE', 'D', 8),     # 8. Дата оказания услуги
            ('PAY_SUM', 'N', 10, 2),   # 9. Стоимость
            # ('STOIM_V', 'N', 10, 2),   # 10. Стоимость по расчетным данным Фонда (для ЛПУ сумма=0)
            ('DS', 'C', 6),            # 10. Диагноз по МКБ
            ('DIRECT_LPU', 'C', 3),    # 11. Код ЛПУ, направившего пациента на консультацию (обследование)
            ('AIM', 'C', 2),           # 12. Цель обращения (указывается при приеме врача или консультации)
            ('STOIM_S', 'N', 10, 2),   # 13. Сумма из средств Федеральных субвенций
            ('STOIM_R', 'N', 10, 2),   # 14. Сумма из средств Субъекта РФ (статья 6 – иные расходы)
            # ('STOIM_F', 'N', 10, 2),   # 15. Сумма доплаты из средств Федерального фонда ОМС
            ('DIR_SPEC', 'N', 4),      # 15. Код специальности направителя (code из V015)
            )

        return dbf


    def createAddInfDbf(self):
        """ Создает структуру dbf для ADD_INF.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'ADD_INF.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CARD', 'C', 10),       # 1. Номер истории болезни, связь с ALIENS
            ('MR','C',  100),        # 2. Место рождения пациента или представителя
            ('OKATOG','C', 11),      # 3. Код места жительства по ОКАТО
            ('OKATOP','C', 11),      # 4. Код места пребывания по ОКАТО
            ('OKATO_OMS','C', 5),    # 5. Код ОКАТО территории страхования по ОМС (по справочнику фонда F010)
            ('FAMP','C', 40),        # 6. Фамилия (представителя) пациента
            ('IMP','C', 40),         # 7. Имя  (представителя) пациента
            ('OTP','C', 40),         # 8. Отчество родителя (представителя) пациента
            ('DRP','D', 8),          # 9. Дата рождения (представителя) пациента
            ('WP','C', 1),           # 10. Пол (представителя) пациента (М/Ж)
            ('C_DOC','N', 2),        # 11. Код типа документа, удостоверяющего личность пациента (представителя) (F011)
            ('S_DOC','C', 9),        # 12. Серия документа, удостоверяющего личность пациента (представителя)
            ('N_DOC','C', 8),        # 13. Номер документа, удостоверяющего личность пациента (представителя)
            ('NOVOR','C', 9),        # 14. Признак новорожденного. Указывается в случае оказания медицинской помощи ребенку до государственной регистрации рождения.
                                        # 0 – признак отсутствует.
                                        # Если значение признака отлично от нуля, он заполняется по следующему шаблону:
                                        # ПДДММГГН, где
                                        # П – пол ребенка в соответствии с классификатором V005;
                                        # ДД – день рождения;
                                        # ММ – месяц рождения;
                                        # ГГ – последние две цифры года рождения;
                                        # Н – порядковый номер ребенка (до двух знаков).

            ('Q_G','C', 7),          # 15. Признак «Особый случай» при регистрации обращения  за медицинской помощью. 1-новорожденный до регистрации при многоплодных родах. 2 - отсутствует имя/отчество
        )
        return dbf


    def createAddServDbf(self):
        """ Создает структуру dbf для ADDSERV.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'ADDSERV.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CARD', 'C', 10),        # 1. Номер статталона
            ('SERVICE', 'C', 10),     # 2. Код услуги
            ('SERV_DATE', 'D', 8 ),   # 3. Дата оказания услуги
            )
        return dbf


    def getEventsSummaryPrice(self):
        u"""возвращает общую стоимость услуг за событие"""

        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """SELECT event_id,
            SUM(Account_Item.sum) AS totalSum,
            LEAST(Tariff.federalPrice * IF(Tariff.federalLimitation = 0,
                                           Account_Item.amount,
                                           LEAST(Tariff.federalLimitation, Account_Item.amount)),
                  Account_Item.sum) AS federalSum
        FROM Account_Item
        LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
        LEFT JOIN Contract_Tariff AS Tariff ON Account_Item.tariff_id = Tariff.id
        WHERE Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
        GROUP BY event_id;
        """ % tableAccountItem['id'].inlist(self.idList)
        query = db.query(stmt)

        result = {}
        while query.next():
            record  = query.record()
            eventId = forceRef(record.value('event_id'))
            sum     = forceDouble(record.value('totalSum'))
            federal = forceDouble(record.value('federalSum'))
            result[eventId] = (sum,  federal)
        return result


    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        accSysFilter = 'ClientIdentification.accountingSystem_id = %d' % \
            self.accSystemId if self.accSystemId else '1'

        stmt = u"""SELECT Event.client_id,
                Account_Item.event_id,
                ClientPolicy.serial AS policySerial,
                ClientPolicy.number AS policyNumber,
                ClientPolicy.note AS policyNote,
                rbPolicyKind.regionalCode AS policyKind,
                Insurer.infisCode AS policyInsurer,
                IF (ClientWork.freeInput NOT LIKE 'пенсионер%%' AND ClientWork.freeInput NOT LIKE 'неработающ%%'
                AND ClientWork.freeInput NOT LIKE 'безработн%%' AND ClientWork.freeInput != '', 1, 0) as clientWorkStatus,
                Event.setDate AS begDate,
                Event.execDate AS endDate,
                Diagnosis.MKB,
                rbDiagnosticResult.regionalCode as diagnosticResultCode,
                EventResult.regionalCode as resultCode,
                Client.lastName,
                Client.firstName,
                Client.patrName,
                ClientDocument.serial AS documentSerial,
                ClientDocument.number AS documentNumber,
                rbDocumentType.regionalCode AS documentRegionalCode,
                Client.SNILS,
                Client.birthDate,
                Client.birthPlace,
                ClientIdentification.identifier AS identifier,
                Client.sex,
                Person.code as personCode2,
                RegAddressHouse.KLADRCode,
                RegAddressHouse.number,
                RegAddressHouse.corpus,
                RegAddress.flat,
                RegKLADR.infis AS placeCode,
                RegSOCR.infisCODE AS placeTypeCode,
                RegKLADR.NAME AS placeName,
                RegRegionKLADR.OCATD,
                RegStreet.NAME AS streetName,
                RegStreetSOCR.infisCODE AS streetType,
                AccDiagnosis.MKB AS accMKB,
                IF(Account_Item.visit_id IS NOT NULL, VisitPerson.regionalCode,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, ActionPerson.regionalCode,
                            ActionSetPerson.regionalCode), Person.regionalCode)
                ) AS personCode,
                IF(Account_Item.visit_id IS NOT NULL, VisitSpeciality.regionalCode,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, ActionSpeciality.regionalCode,
                            ActionSetSpeciality.regionalCode), rbSpeciality.regionalCode)
                )  AS specialityCode,
                ActionSetSpeciality.regionalCode as setSpecialityCode,
                IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.infis,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                    ) AS service,
                IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.code,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.code, rbEventService.code)
                    ) AS serviceCode,
                Account_Item.amount,
                Visit.date AS visitDate,
                Action.endDate AS actionDate,
                Action.MKB AS actionMKB,
                Account_Item.`sum` AS `sum`,
                LEAST(IF(tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(tariff.federalLimitation, Account_Item.amount)) * tariff.federalPrice,
                            Account_Item.sum)  AS federalSum,
                setOrgStruct.infisCode AS setOrgStructCode,
                ClientPolicy.begDate AS policyBegDate,
                ClientPolicy.endDate AS policyEndDate,
                age(Client.birthDate, Event.execDate) AS clientAge,
                Insurer.OKATO AS insurerOKATO,
                Insurer.shortName AS insurerName,
                Insurer.OGRN AS insurerOGRN,
                Account_Item.id AS accountItem_id,
                Account_Item.action_id AS action_id,
                IF(BirthCertificate.id IS NOT NULL, 1, 0) AS hasBirthCertificate,
                Citizenship.regionalCode AS citizenshipCode,
                rbEventTypePurpose.federalCode AS purpose,
                EventType.code AS eventTypeCode,
                IF(Action.org_id IS NULL, '105', ExecOrg.infisCode) AS execOrgInfis,
                VisitPerson.lastName AS visitPersonLastName,
                VisitPerson.firstName AS visitPersonFirstName,
                VisitPerson.patrName AS visitPersonPatrName
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
            LEFT JOIN rbPolicyKind ON rbPolicyKind.id = ClientPolicy.policyKind_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND
                      ClientDocument.id = (SELECT MAX(CD.id)
                                         FROM   ClientDocument AS CD
                                         LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                         LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                                         WHERE  rbDTG.code = '1' AND CD.client_id = Client.id AND CD.deleted=0)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN ClientDocument AS BirthCertificate ON BirthCertificate.client_id = Client.id AND
                      BirthCertificate.id = (SELECT MAX(CD.id)
                                         FROM   ClientDocument AS CD
                                         LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                         WHERE  rbDT.code = '3' AND CD.client_id = Client.id AND CD.deleted=0)
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
            LEFT JOIN kladr.KLADR RegKLADR ON RegKLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN kladr.SOCRBASE RegSOCR ON RegSOCR.KOD_T_ST = (SELECT KOD_T_ST
                    FROM kladr.SOCRBASE AS SB
                    WHERE SB.SCNAME = RegKLADR.SOCR
                    LIMIT 1)
            LEFT JOIN kladr.KLADR RegRegionKLADR ON RegRegionKLADR.CODE = (
                SELECT RPAD(LEFT(RegAddressHouse.KLADRCode,2),13,'0'))
            LEFT JOIN kladr.STREET RegStreet ON RegStreet.CODE = RegAddressHouse.KLADRStreetCode
            LEFT JOIN kladr.SOCRBASE RegStreetSOCR ON RegStreetSOCR.KOD_T_ST = (SELECT KOD_T_ST
                    FROM kladr.SOCRBASE AS SB
                    WHERE SB.SCNAME = RegStreet.SOCR
                    LIMIT 1)
            LEFT JOIN Person ON Person.id = Event.execPerson_id
                AND Person.id IS NOT NULL
            LEFT JOIN Person AS VisitPerson ON VisitPerson.id = Visit.person_id
                AND VisitPerson.id IS NOT NULL
            LEFT JOIN Person AS ActionPerson ON ActionPerson.id = Action.person_id
                AND ActionPerson.id IS NOT NULL
            LEFT JOIN Person AS ActionSetPerson ON ActionSetPerson.id = Action.setPerson_id
                AND ActionSetPerson.id IS NOT NULL
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
                AND rbSpeciality.id IS NOT NULL
            LEFT JOIN rbSpeciality AS VisitSpeciality ON VisitPerson.speciality_id = VisitSpeciality.id
                AND VisitSpeciality.id IS NOT NULL
            LEFT JOIN rbSpeciality AS ActionSpeciality ON ActionPerson.speciality_id = ActionSpeciality.id
                AND ActionSpeciality.id IS NOT NULL
            LEFT JOIN rbSpeciality AS ActionSetSpeciality ON ActionSetPerson.speciality_id = ActionSetSpeciality.id
                AND ActionSetSpeciality.id IS NOT NULL
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                      AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1', '2'))
                                      AND Diagnostic.person_id = Event.execPerson_id AND Diagnostic.deleted = 0)
            LEFT JOIN Diagnostic AS AccDiagnostic ON AccDiagnostic.id = (
             SELECT id FROM Diagnostic AS AD
             WHERE AD.event_id = Account_Item.event_id AND
                AD.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='9') AND
                AD.person_id = Event.execPerson_id AND
                AD.deleted = 0 LIMIT 1)
            LEFT JOIN Diagnosis AS AccDiagnosis ON
                AccDiagnosis.id = AccDiagnostic.diagnosis_id AND
                AccDiagnosis.deleted = 0
            LEFT JOIN ClientWork ON ClientWork.client_id=Event.client_id AND
                        ClientWork.id = (SELECT max(CW.id)
                                         FROM ClientWork AS CW
                                         WHERE CW.client_id=Client.id AND CW.deleted=0)
            LEFT JOIN Organisation AS work ON work.id=ClientWork.org_id AND work.deleted = 0
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN EventType ON Event.eventType_id = EventType.id
            LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN OrgStructure AS setOrgStruct ON Person.orgStructure_id = setOrgStruct.id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN ClientIdentification ON Client.id = ClientIdentification.client_id AND
                    ClientIdentification.deleted = 0 AND %s
            LEFT JOIN ClientSocStatus AS ClientCitizenshipStatus ON
                ClientCitizenshipStatus.client_id = Client.id AND
                ClientCitizenshipStatus.deleted = 0 AND
                ClientCitizenshipStatus.socStatusClass_id = (
                    SELECT rbSSC.id
                    FROM rbSocStatusClass AS rbSSC
                    WHERE rbSSC.code = '8' AND rbSSC.group_id IS NULL
                    LIMIT 0,1
                )
            LEFT JOIN Contract_Tariff AS tariff ON Account_Item.tariff_id = tariff.id
            LEFT JOIN rbSocStatusType AS Citizenship ON
                ClientCitizenshipStatus.socStatusType_id = Citizenship.id
            LEFT JOIN Organisation AS ExecOrg ON Action.org_id = ExecOrg.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            GROUP BY Account_Item.id
        """ % (accSysFilter,  tableAccountItem['id'].inlist(self.idList))
#            ORDER BY insurerName
        query = db.query(stmt)
        return query

# *****************************************************************************************


# #################### OLD VERSION #####################################
#    def createAddServQuery(self, contractId):
#        db = QtGui.qApp.db
#        tableEvent = db.table('Event')
#        tableVisit = db.table('Visit')
#        tableService = db.table('rbService')
#
#        surgicalServiceCodeList = ['911900102']
#
#        cond = [tableVisit['deleted'].eq(0),
#                tableEvent['deleted'].eq(0),
#                tableService['code'].inlist(surgicalServiceCodeList),
#                tableEvent['contract_id'].eq(contractId)]
#
#        stmt = """
#        SELECT
#            Event.id AS eventId,
#            rbService.infis AS code,
#            Visit.date AS visitDate
#        FROM Visit
#            LEFT JOIN Event ON Event.id = Visit.event_id
#            LEFT JOIN rbService ON rbService.id = Visit.service_id
#        WHERE %(cond)s
#        """ % {'cond' : db.joinAnd(cond)}
#
#        query = db.query(stmt)
#        return query
# ################# END OF OLD VERSION ###################################
    def createAddServQuery(self, contractId):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableVisit = db.table('Visit')
        tableService = db.table('rbService')
        
        surgicalServiceCodeList = ['911900102']

        cond = [tableEvent['deleted'].eq(0),
                tableVisit['deleted'].eq(0),
                tableAction['deleted'].eq(0),
                tableService['code'].inlist(surgicalServiceCodeList),
                tableEvent['contract_id'].eq(contractId)
                ]

        # ### Убрать groupBy???
        stmt = '''
        SELECT
            Event.id as eventId,
            ActionType.code as code,
            ActionType.id AS actionTypeId,
            Action.endDate as endDate
            
        FROM Visit
        INNER JOIN Event ON Event.id = Visit.event_id
        INNER JOIN Action ON Action.event_id = Event.id
        INNER JOIN ActionType ON ActionType.id = Action.actionType_id
        INNER JOIN rbService ON rbService.id = Visit.service_id
        WHERE %s
        GROUP BY eventId, code, endDate''' % db.joinAnd(cond)

        query = db.query(stmt)
        return query

# *****************************************************************************************
    def isValidActionTypeId(self, id):
        if id in self.validActionTypeIdList:
            return True

        parentId = forceRef(QtGui.qApp.db.translate('ActionType', 'id', id, 'group_id'))

        if parentId:
            if parentId in self.validActionTypeIdList:
                self.validActionTypeIdList.append(id)
                return True
            else:
                if self.isValidActionTypeId(parentId):
                    self.validActionTypeIdList.append(parentId)
                    self.validActionTypeIdList.append(id)
                    return True

        return False

# *****************************************************************************************

    regionNameCache = {}

    def getRegionName(self, code):
        u""" Возвращает название района. Области отфильтровываются."""

        result = self.regionNameCache.get(code)

        if not result:
            if code != '':
                regionCode = code[:5].ljust(13, '0')
                result = forceString(QtGui.qApp.db.translate('kladr.KLADR','CODE',
                    regionCode,'NAME')) if regionCode[2:5] != '000' else \
                    self.getRegionCenterName(code)
            else:
                result = ''

            self.regionNameCache[code] = result

        return result

# *****************************************************************************************

    regionCenterNameCache = {}

    def getRegionCenterName(self, code):
        u"""Возвращает название регионального центра."""

        result = self.regionCenterNameCache.get(code)

        if not result:
            result = ''

            stmt = """
            SELECT `NAME` FROM kladr.KLADR
            WHERE `CODE` LIKE '%s%%' AND `STATUS` IN ('2','3')
            """ % code[:2]
            db = QtGui.qApp.db
            query = db.query(stmt)

            while query.next():
                record = query.record()

                if record:
                    result = forceString(record.value(0))

            self.regionCenterNameCache[code] = result

        return result


# *****************************************************************************************

    def processAddServ(self, dbf, contractId):
        query = self.createAddServQuery(contractId)
        self.progressBar.setText(u'Выгрузка дополнительных услуг')

        dbfAddServ = dbf[3]

        while query.next():
            record = query.record()
            QtGui.qApp.processEvents()

            if self.aborted:
                break

            if record:
                eventId = forceRef(record.value('eventId'))
                code = forceString(record.value('code'))
                actionTypeId = forceRef(record.value('actionTypeId'))
                servEndDate = forceDate(record.value('endDate'))
                if eventId in self.exportedEventSet and self.isValidActionTypeId(actionTypeId):
                    dbfRecord = dbfAddServ.newRecord()
                    dbfRecord['CARD'] = eventId
                    dbfRecord['SERVICE'] = code
                    dbfRecord['SERV_DATE'] = pyDate(servEndDate)
                    dbfRecord.store()

    def serviceIsMes(self, serviceCode):
        return QtGui.qApp.db.translate('mes.MES', 'code', serviceCode, 'id') is not None

    def process(self, dbf, record, codeLPU, OKPO, lpuOGRN,  accNumber,
                contractNumber, exposeDate, mapEventIdToSum,
                accDate, settleDate):
        birthDate = forceDate(record.value('birthDate'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        # Номер стат.талона
        eventId = forceRef(record.value('event_id'))
        clientId = forceRef(record.value('client_id'))
        clientAttachRecord = getAttachRecord(clientId, False)
        KLADRCode = forceString(record.value('KLADRCode'))
        if not KLADRCode:
            self.log(u'Отсутвует КЛАДР адрес проживания и регистрации для клиента clientId=%d' % clientId)

        attachOrgCode = ''

        if clientAttachRecord:
            clientAttachOrgId = clientAttachRecord.get('LPU_id', None)

            if clientAttachOrgId:
                attachOrgCode = forceString(QtGui.qApp.db.translate('Organisation', \
                'id', clientAttachOrgId, 'infisCode'))
            else:
                self.log(u'В записи прикрепления отсутствует код ЛПУ.')

        else:
            self.log(u'Внимание: не задано ЛПУ постоянного прикрепления пациента. clientId=%d' % clientId)

        (dbfAliens, dbfService, dbfAddInf) = dbf[:3]

        if eventId not in self.exportedEventSet:
            dbfRecord = dbfAliens.newRecord()
            # Код ЛПУ пребывания по справочнику фонда
            dbfRecord['CODE_HOSP'] = codeLPU
            # Номер счета представляемого в СМО
            dbfRecord['CODE_COUNT'] = accNumber
            
            firstDayDate = QDate(settleDate.year(), settleDate.month(), 1)
            lastDayDate = QDate(settleDate.year(), settleDate.month(), settleDate.daysInMonth())
            dbfRecord['DATE_LOW'] = pyDate(firstDayDate) # Account.date
            dbfRecord['DATE_UP'] = pyDate(lastDayDate) # Account.settleDate
    
            # Номер статталона
            dbfRecord['CARD'] = eventId
            # Код СМО (по справочнику фонда)
            insurerInfis = forceString(record.value('policyInsurer'))
            dbfRecord['INS'] = insurerInfis if insurerInfis in ('14', '17') else '01'
            # Серия полиса
            dbfRecord['SERPOL'] = forceString(record.value('policySerial'))
            # Номер полиса
            dbfRecord['NMBPOL'] = forceString(record.value('policyNumber'))
            # Номер договора
            # dbfRecord['DOGOVOR'] = forceString(record.value('policyNote'))
            # Признак работающий- “1”/неработающий – “0”
            dbfRecord['WORK'] = '' if not self.isClinicalExamination else forceString(record.value('clientWorkStatus'))
            # Дата поступления
            dbfRecord['DATIN'] = pyDate(begDate)
            # Дата выписки
            dbfRecord['DATOUT'] = pyDate(endDate)
            # Диагноз основной МКБ Х
            dbfRecord['DIAG'] = forceString(record.value('MKB'))
            # Диагноз первичный
            dbfRecord['DS0'] = dbfRecord['DIAG']
            # # Исход по справочнику фонда
            # dbfRecord['RESULT'] = forceString(record.value('resultCode'))
            # Суммарная стоимость услуг
            (sum,  federalSum) = mapEventIdToSum.get(eventId, (0.0, 0.0))
            # dbfRecord['STOIM'] = sum - federalSum
            # Суммарная стоимость услуг по расчетным данным Фонда (для ЛПУ сумма=0)
            # dbfRecord['STOIM_V'] = 0
            # Фамилия пациента
            dbfRecord['FAM'] = nameCase(forceString(record.value('lastName')))
            # Имя пациента
            dbfRecord['IMM'] = nameCase(forceString(record.value('firstName')))
            # Отчество пациента
            dbfRecord['OTC'] =  nameCase(forceString(record.value('patrName')))
            # Серия документа, удостоверяющего личность
            dbfRecord['SER_PASP'] = forceString(record.value('documentSerial'))
            # Номер документа, удостоверяющего личность
            dbfRecord['NUM_PASP'] = forceString(record.value('documentNumber'))
            # Тип документа, удостоверяющего личность (приложение «Типы документов»)
            dbfRecord['TYP_DOC'] = forceInt(record.value('documentRegionalCode'))
            # Страховой номер индивидуального лицевого счета (СНИЛС)
            dbfRecord['SS'] = formatSNILS(forceString(record.value('SNILS')))
            # Персональный  индивидуальный номер застрахованного по ОМС
            # dbfRecord['PIN'] = forceString(record.value('identifier'))
            # Дата рождения пациента
            dbfRecord['BIRTHDAY'] = pyDate(birthDate)
            # Пол пациента   («М», «Ж»)
            dbfRecord['SEX'] = formatSex(record.value('sex')).upper()
            # Код населенного пункта проживания пациента по справочнику фонда
            townCode = forceString(record.value('placeCode'))
            dbfRecord['TAUN'] = townCode if townCode and townCode != '000' else ''
            # Код ЛПУ приписки
            dbfRecord['MASTER'] = attachOrgCode if attachOrgCode != '999' else '000'
    
            # Код диагноза сопутствующего заболевания (состояния) по МКБ-10
            dbfRecord['DS_S'] = forceString(record.value('accMKB'))
            # Сумма по базовой программе гос. гарантий
            dbfRecord['STOIM_S'] = sum-federalSum #dbfRecord['STOIM']
            # Сумма по сверхбазовой программе гос. гарантий
            dbfRecord['STOIM_R'] = 0
            # Сумма доплаты из средств Федерального фонда ОМС
            # dbfRecord['STOIM_F'] = federalSum
            # Тип полиса
            dbfRecord['TPOLIS'] = forceInt(record.value('policyKind'))
            if self.isClinicalExamination:
                dbfRecord['PRIZN_ZS'] = 3 if forceString(record.value('eventTypeCode')) == 'dd2013_1' else 4 if forceString(record.value('eventTypeCode')) == 'dd2013_2' else 0
            else:
                dbfRecord['PRIZN_ZS'] = 0
            # Результат обращения (V009)
            dbfRecord['RSLT'] = forceInt(record.value('resultCode'))
            # Исход заболевания (V012)
            dbfRecord['ISHOD'] = forceInt(record.value('diagnosticResultCode'))
            dbfRecord['P_CODE'] = forceString(record.value('personCode2'))
            # Сумма доплаты за окончанный случай при проведении диспансеризации 14-летних подростков или студентов
            # dbfRecord['STOIM_ZS'] = 0
            # Цель обращения
            dbfRecord['PURPOSE'] = forceInt(record.value('purpose'))
    
            dbfRecord.store()
        
        
        mainSum = forceDouble(record.value('sum'))
        fedSum = forceDouble(record.value('federalSum'))
        isExportService = True
        
        if self.isClinicalExamination:
            serviceCode = forceStringEx(record.value('serviceCode'))
            if self.serviceIsMes(serviceCode):
                #self.eventMesSums.setdefault(eventId, []).append((mainSum, fedSum))
                isExportService = False
                
        
        
        if isExportService:
            #eventMesSums = self.eventMesSums.get(eventId, [])
            #if self.isClinicalExamination and eventMesSums:
            #    mainSum, fedSum = eventMesSums.pop()
            
            dbfRecord = dbfService.newRecord()
            # Номер статталона
            dbfRecord['CARD'] = eventId
            # Код ЛПУ пребывания по справочнику фонда
            dbfRecord['CODE_HOSP'] = codeLPU
            # Номер счета представляемого в СМО
            dbfRecord['CODE_COUNT'] = accNumber
            # Личный код  медицинского работника, оказавшего услугу
            dbfRecord['P_CODE'] = forceString(record.value('personCode2')) ##forceString(record.value('personCode'))
            if not dbfRecord['P_CODE']:
                self.log(u'Для события "%d" не задан региональный код исполнителя.' % eventId)
            # Код специальности медицинского работника, оказавшего услугу
            dbfRecord['SPEC'] = forceString(record.value('specialityCode'))
            if not dbfRecord['SPEC']:
                self.log(u'Для события "%d" не задан региональный код специальности исполнителя.' % eventId)
            # Код услуги
            dbfRecord['SERVICE'] = forceString(record.value('service'))
            codeService = ['9102101020', '940211003',  '940211004', '940211005', '940211006', '940211007', '940211500']
            for index in xrange(len(codeService)):
                if codeService[index] == dbfRecord['SERVICE']:
                    dbfRecord['SPEC'] = '021'
            # Кол-во услуг
            dbfRecord['UNITS'] = forceDouble(record.value('amount'))
            # Дата оказания услуги
            servDate = forceDate(record.value('actionDate'))
    
            if not servDate.isValid():
                servDate = forceDate(record.value('visitDate'))
    
                if not servDate.isValid():
                    servDate = endDate
    
            if not servDate.isValid():
                self.log(u'Не задана дата услуги: accountItemId=%d,'\
                    u' код карточки "%d".' % (forceRef(record.value('accountItem_id')), eventId))
    
            dbfRecord['SERV_DATE'] = pyDate(servDate)
            # Стоимость
            dbfRecord['PAY_SUM'] = mainSum -  fedSum
            # Стоимость по расчетным данным Фонда (для ЛПУ сумма=0)
            # dbfRecord['STOIM_V'] = 0
            # Диагноз
            actionMKB = forceString(record.value('actionMKB'))
            dbfRecord['DS'] = actionMKB if actionMKB else forceString(record.value('MKB'))
            # Код ЛПУ, направившего пациента на консультацию (обследование)
            dbfRecord['DIRECT_LPU'] = forceString(record.value('setOrgStructCode'))
            # Цель обращения (указывается при приеме врача или консультации)
            aim =  '1' if (servDate < begDate) or (self.isClinicalExamination and forceString(record.value('execOrgInfis')) != '105')  else '0' if begDate <= servDate <= endDate else ''
            
            if aim != '1':
                for namePart in (forceString(record.value('visitPersonLastName')),
                                 forceString(record.value('visitPersonFirstName')),
                                 forceString(record.value('visitPersonPatrName'))):
                    if namePart.startswith(u'врач') or namePart.startswith(u'внеш') or namePart.startswith(u'лпу'):
                        aim = '1'
                        break
                                
            dbfRecord['AIM'] = aim
            dbfRecord['STOIM_S'] = dbfRecord['PAY_SUM']
            # Сумма по сверхбазовой программе гос. гарантий
            dbfRecord['STOIM_R'] = 0
            # dbfRecord['STOIM_F'] = fedSum
            dbfRecord['DIR_SPEC'] = forceInt(record.value('setSpecialityCode'))
            dbfRecord.store()


        if (eventId not in self.exportedEventSet):
            insurerOKATO = forceString(record.value('insurerOKATO'))
            # ОКАТО всех объектов Мурманской области начинается с 47 (у Мурманской области окато 47000000000)
            if insurerOKATO[:2] != '47' or self.isAddInfAsAliens:
                dbfRecord = dbfAddInf.newRecord()
                #Номер истории болезни
                dbfRecord['CARD'] = eventId
                dbfRecord['MR'] = forceString(record.value('birthPlace')) # Место рождения пациента или представителя
                dbfRecord['OKATOG'] = forceString(record.value('OCATD')) # Код места жительства по ОКАТО
                dbfRecord['OKATOP'] = forceString(record.value('OCATD')) # Код места пребывания по ОКАТО
                dbfRecord['OKATO_OMS'] = forceString(record.value('insurerOKATO')) #	Код ОКАТО территории страхования по ОМС (по справочнику фонда)
                dbfRecord['FAMP'] = '' #forceString(record.value('lastName')) #Фамилия (представителя) пациента
                dbfRecord['IMP'] =  '' #forceString(record.value('firstName')) #Имя  (представителя) пациента
                dbfRecord['OTP'] = '' #forceString(record.value('patrName'))  #Отчество родителя (представителя) пациента
                dbfRecord['DRP'] = pyDate(QDate())
#                dbfRecord['WP'] = formatSex(record.value('sex')).upper() #Пол (представителя) пациента
                dbfRecord['C_DOC'] = forceInt(record.value('documentRegionalCode'))
                dbfRecord['S_DOC'] = forceString(record.value('documentSerial'))
                dbfRecord['N_DOC'] = forceString(record.value('documentNumber'))
    
                # NOVOR
                # Указывается в случае оказания медицинской помощи ребенку до государственной регистрации рождения.
                # 0 – признак отсутствует.
                # Если значение признака отлично от нуля, он заполняется по следующему шаблону:
                # ПДДММГГН, где
                # П – пол ребенка в соответствии с классификатором V005;
                # ДД – день рождения;
                # ММ – месяц рождения;
                # ГГ – последние две цифры года рождения;
                # Н – порядковый номер ребенка (до двух знаков).
                dbfRecord['NOVOR'] = '0' # Признак новорожденного
                specState = ''
                age = forceInt(record.value('clientAge'))
                if not forceString(record.value('policySerial')) and not forceString(record.value('policyNumber')):
                    specState += '1'
                if age == 0:
                    specState += '2'
                if age < 14 and self.getClientRepresentativeInfo(clientId) != {}:
                    specState += '3'
                if not forceString(record.value('patrName')):
                    specState += '4'
                dbfRecord['Q_G'] = specState
                dbfRecord.store()

        self.exportedEventSet.add(eventId)

# *****************************************************************************************

    representativeInfoCache = {}

    def getClientRepresentativeInfo(self, clientId):
        result = self.representativeInfoCache.get(clientId, None)
        if result is None:
            result = getClientRepresentativeInfo(clientId)
            self.representativeInfoCache[clientId] = result
        return result

# *****************************************************************************************

    def getTariff(self, tariffId):
        result = self.tariffCache.get(tariffId, False)
        if result == False:
            result = None
            if tariffId:
                record = QtGui.qApp.db.getRecord('Contract_Tariff', '*', tariffId)
                if record:
                    result = CTariff(record)
            self.tariffCache[tariffId] = result
        return result


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


class CExportR51OMSOutDirPage(QtGui.QWizardPage, Ui_ExportR51OMSOutDirPage):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R51OMSExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        for src in ('ALIENS.DBF', 'SERVICE.DBF', 'ADD_INF.DBF',
                    'ADDSERV.DBF'
                    ):
            srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                    os.path.basename(src))
            dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                    os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

            if not success:
                break

        if success:
            QtGui.qApp.preferences.appPrefs['R51OMSExportDir'] = toVariant(self.edtDir.text())
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
