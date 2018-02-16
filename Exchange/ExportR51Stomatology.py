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
from Exchange.Utils    import getClientRepresentativeInfo

from Ui_ExportR51StomatologyProcessPage import Ui_ExportR51StomatologyProcessPage
from Ui_ExportR51StomatologyOutDirPage import Ui_ExportR51StomatologyOutDirPage


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


def exportR51Stomatology(widget, accountId, accountItemIdList):
    wizard = CExportWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportR51StomatologyProcessPage(self)
        self.page2 = CExportR51StomatologyOutDirPage(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта по стоматологии для Мурманской области')
        self.dbfFileName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number = getAccountInfo(accountId)[:2]
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменных файлов "*.dbf"')


#    def setAccountExposeDate(self):
#        db = QtGui.qApp.db
#        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
#        accountRecord.setValue('id', toVariant(self.accountId))
#        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
#        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R51Stomatology')
        return self.tmpDir


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

class CExportR51StomatologyProcessPage(QtGui.QWizardPage, Ui_ExportR51StomatologyProcessPage):
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
#        self.tariffCache = {}
        self.parent = parent
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51StomatologyIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51StomatologyVerboseLog', 'False')))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
#        self.knownR51StomatologyCodes = {}
#        self.educationIdList = []
#        self.mapPersonSpecInfisCode = {}
        self.mapEventIdToDbfRecord = {}
        self.mapEventIdToCountedDates = {}
        self.mapToothToDbfRecord = {}
        self.mapToothToCountedDates = {}
        self.mapSpecialityToDbfRecord = {}
        self.mapSpecialityToCountedDates = {}
        self.accSystemId = None


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

        lpuCode = '120'
        
        dbf, query = self.prepareToExport()
        accDate, accNumber, exposeDate, contractId, settleDate = getAccountInfo(self.parent.accountId)

        strAccNumber = '120' + forceString(settleDate.toString('MMyy'))
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
        self.mapEventIdToDbfRecord = {}
        self.mapEventIdToCountedDates = {}
        self.mapToothToDbfRecord = {}
        self.mapToothToCountedDates = {}
        self.mapSpecialityToDbfRecord = {}
        self.mapSpecialityToCountedDates = {}
        

        #self.processAddServ(dbf, contractId)

        if self.idList:
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), lpuCode, strAccNumber, settleDate)
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        for x in dbf:
            x.close()


    def createDbf(self):
        return (self.createStReestrDbf(), self.createToothDbf(),
                    self.createSpecVisDbf(), self.createServicesDbf(),
                    self.createGuestsDbf()
                    )


    def createStReestrDbf(self):
        """ Создает структуру dbf для STREESTR.DBF """
        """ (информация о пациентах) """

        dbfName = os.path.join(self.parent.getTmpDir(), 'STREESTR.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('ID_TALON', 'C', 10),      # 1. Номер талона (Уникальное поле для реестра).
            ('INS', 'C', 2),            # 2. Код СМО (Код из справочника SMO).
            ('ADMITANCE', 'C', 1),      # 3. Тип приема (взрослый – 1, детский плановый – 2, детский амбулаторный – 3, ортодонтия - 4).
            ('DATE_LO', 'D', 8),        # 4. Отчетный месяц (Указывается первое число месяца).
            ('DATE_UP', 'D', 8),        # 5. Дата по ... выписки (Необязательное поле).
            ('PRIMARY', 'C', 1),        # 6. Признак первичности приема (Первичный – 1, Повторный – 2).
            ('RESULT', 'C', 2),         # 7. Полный исход лечения (Код из справочника RESULT).
            ('WORK', 'C', 1),           # 8. Признак: работающий-1/неработающий-0 (пациент) (Необязательное поле).
            ('DATIN', 'D', 8),          # 9. Дата начала лечения.
            ('DATOUT', 'D', 8),         # 10. Дата окончания лечения.
            ('URGENT', 'C', 1),         # 11. Признак оказания мед. помощи (0 – плановая, 1- экстренная).
            ('VISITS', 'N', 2),         # 12. Количество посещений.
            ('UNITS', 'N', 6, 2),       # 13. Сумма единиц трудозатрат (УЕТ).
            ('PAY_SUM', 'N', 10, 2),    # 14. Сумма к оплате (Равна сумме STOIM_S+STOIM_R).
            ('STOIM_V', 'N', 10, 2),    # 15. Суммарная стоимость по расчетным данным Фонда (для ЛПУ сумма=0) (Необязательное поле).
            
            #Для детей до гос. рег-ии рождения при отсутствии данных ФИО указывается «НЕТ», 
            #при этом обязательно заполняется информация по представителю пациента в файле GUESTS. 
            #Имя и (или) Отчество указывается «НЕТ» при отсутствии в удостоверении.
            ('FAM', 'C', 40),           # 16. Фамилия.
            ('IMM', 'C', 40),           # 17. Имя.
            ('OTC', 'C', 40),           # 18. Отчество.
            
            ('SER_PASP', 'C', 8),       # 19. Серия документа, удостоверяющего личность (В соответствии с маской (F011)).
            ('NUM_PASP', 'C', 8),       # 20. Номер документа, удостоверяющего личность (В соответствии с маской (F011)).
            ('TYP_DOC', 'N', 2),        # 21. Тип документа, удостоверяющего личность (приложение «Типы документов») (Код из справочника F011).
            ('SS', 'C', 14),            # 22. Страховой номер индивидуального лицевого счета (СНИЛС) (СНИЛС с разделителями. Указывается при наличии).
            ('PIN', 'C', 16),           # 23. Персональный  индивидуальный номер застрахованного по ОМС (Необязательное поле).
            ('SERPOL', 'C', 10),        # 24. Серия полиса (Для полисов нового образца не заполняется).
            ('NMBPOL', 'C', 20),        # 25. Номер полиса (Для временных свидетельств – 9 цифр, для полисов нового образца – 16 цифр).
            ('DOGOVOR', 'C', 10),       # 26. Номер договора (для инообластных поле не заполняется) (Необязательное поле).
            ('TAUN', 'C', 3),           # 27. Код населенного пункта проживания пациента (Код из справочника NASPUNKT).
            ('BIRTHDAY', 'D', 8),       # 28. Дата рождения пациента.
            ('SEX', 'C', 1),            # 29. Пол пациента («0» –женский, «1» – мужской).
            ('ID_REESTR', 'C', 10),     # 30. Номер реестра.
            ('ID_HOSP', 'C', 3),        # 31. Код стоматологического АПУ (Код из справочника HOSPITAL).
            ('STOIM_S', 'N', 10, 2),    # 32. Сумма по базовой программе гос. гарантий.
            ('STOIM_R', 'N', 10, 2),    # 33. Сумма по сверхбазовой программе гос. гарантий.
            ('STOIM_F', 'N', 10, 2),    # 34. Сумма доплаты из средств Федерального фонда ОМС (Необязательное поле).
            ('TPOLIS', 'N', 1),         # 35. Тип полиса (1 – старого образца, 2 – временное свидетельство, 3 – нового образца).
            ('MASTER', 'C', 3),         # 36. Коды ЛПУ приписки по справочнику фонда (стоматология) (По подушевому нормативу финансирования данное поле обязательно для заполнения (T001)).
            )

        return dbf


    def createToothDbf(self):
        """ Создает структуру dbf для TOOTH.DBF """
        """ (Трудозатраты на лечение зуба) """

        dbfName = os.path.join(self.parent.getTmpDir(), 'TOOTH.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('ID_TALON', 'C', 10),      # 1. Номер талона (Используется для связи с файлом STREESTR).
            ('TOOTH', 'C', 2),          # 2. Номер зуба по международной классификации.
            ('DIAG', 'C', 6),           # 3. Код диагноза (Код из справочника MKB).
            ('SPEC', 'C', 3),           # 4. Код специальности медицинского работника, оказавшего услугу (Код из справочника SPEC).
            ('VISITS', 'N', 2, 0),      # 5. Количество посещений по данному заболеванию.
            ('UNITS_SUM', 'N', 6, 2),   # 6. Сумма единиц трудозатрат услуг (УЕТ).
            ('ID_REESTR', 'C', 10),     # 7. Номер реестра.
            ('ID_HOSP', 'C', 3),        # 8. Код стоматологического АПУ (Код из справочника HOSPITAL).
            )

        return dbf


    def createSpecVisDbf(self):
        """ Создает структуру dbf для SPEC_VIS.DBF """
        """ (Объем оказанной помощи по специальности медицинского работника) """

        dbfName = os.path.join(self.parent.getTmpDir(), 'SPEC_VIS.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('ID_TALON', 'C', 10),      # 1. Номер талона (Используется для связи с файлом STREESTR).
            ('SPEC', 'C',  3),          # 2. Код специальности медицинского работника, оказавшего услугу (Код из справочника SPEC).
            ('VISITS', 'N', 2, 0),      # 3. Количество посещений по данной специальности.
            ('UNITS_SUM','N', 6, 2),    # 4. Сумма единиц трудозатрат услуг (УЕТ).
            ('ID_REESTR','C', 10),      # 5. Номер реестра.
            ('ID_HOSP', 'C', 3),        # 8. Код стоматологического АПУ (Код из справочника HOSPITAL).
        )
        return dbf


    def createServicesDbf(self):
        """ Создает структуру dbf для SERVICES.DBF """
        """ (Объем оказанной помощи на зуб) """

        dbfName = os.path.join(self.parent.getTmpDir(), 'SERVICES.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('ID_TALON', 'C', 10),      # 1. Номер талона (Используется для связи с файлом STREESTR).
            ('TOOTH', 'C', 2),          # 2. Номер зуба по международной классификации.
            ('DIAG', 'C', 6),           # 3. Код диагноза (Код из справочника MKB).
            ('DS0', 'C', 6),            # 4. Код диагноза первичный (Код из справочника MKB. Указывается при наличии).
            ('SPEC', 'C',  3),          # 5. Код специальности медицинского работника, оказавшего услугу (Код из справочника SPEC). 
            ('P_CODE', 'C', 7),         # 6. Личный код  медицинского работника, оказавшего услугу.
            ('ID_SERV', 'C', 6),        # 7. Код услуги (Код из справочника TSERV).
            ('SERV_DATE', 'D', 8),      # 8. Дата оказания услуги.
            ('SERVNUMBER', 'N', 2, 0),  # 9. Кол-во услуг данного типа.
            ('UNITS_SUM', 'N', 6, 2),   # 10. Сумма единиц трудозатрат услуг (УЕТ).
            ('SERV_SUM', 'N', 10, 2),   # 11. Стоимость оказанной услуги (Равна сумме STOIM_S+STOIM_R)
            ('ID_REESTR','C', 10),      # 12. Номер реестра.
            ('ID_HOSP', 'C', 3),        # 13. Код стоматологического АПУ (Код из справочника HOSPITAL).
            ('STOIM_S', 'N', 10, 2),    # 14. Сумма по базовой программе гос. гарантий.
            ('STOIM_R', 'N', 10, 2),    # 15. Сумма по сверхбазовой программе гос. гарантий.
            ('STOIM_F', 'N', 10, 2),    # 16. Сумма доплаты из средств Федерального фонда ОМС (Необязательное поле).
            )
        return dbf
    
    
    def createGuestsDbf(self):
        """ Создает структуру dbf для GUESTS.DBF """
        """ (информация по пациентам, застрахованным на территории других субъектов РФ) """

        dbfName = os.path.join(self.parent.getTmpDir(), 'GUESTS.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('ID_TALON', 'C', 10),      # 1. Номер талона (Используется для связи с файлом STREESTR).
            
            # Место рождения указывается в том виде, в котором оно записано в предъявленном документе, удостоверяющем личность.
            ('MR', 'C', 100),          # 2. Место рождения пациента или представителя.
            
            ('OKATOG', 'C', 11),           # 3. Код места жительства по ОКАТО (Заполняется при наличии сведений).
            ('OKATOP', 'C', 11),           # 4. Код места пребывания по ОКАТО (Заполняется при наличии сведений).
            ('OKATO_OMS', 'C', 5),          # 5. Код ОКАТО территории страхования по ОМС (Код KOD_OKATO из классификатора субъектов РФ (F010)). 
            
            # Заполняются данные о представителе только для детей до государственной регистрации рождения.
            # Отчество указывается «НЕТ» при отсутствии в удостоверении.
            ('FAMP', 'C', 40),         # 6. Фамилия (представителя) пациента.
            ('IMP', 'C', 40),        # 7. Имя  (представителя) пациента.
            ('OTP', 'C', 40),      # 8. Отчество родителя (представителя) пациента.
            ('DRP', 'D', 8),  # Дата рождения (представителя) пациента.
            ('WP', 'C', 1),   # 10. Пол  (представителя) пациента («М» или «Ж»).
            ('C_DOC', 'N', 2, 0),   # 11. Код типа документа, удостоверяющего личность пациента (представителя) (по справочнику фонда) (Код из справочника F011).
            ('S_DOC','C', 9),      # 12. Серия документа, удостоверяющего личность пациента (представителя) (по справочнику фонда) (В соответствии с маской (F011)).
            ('N_DOC', 'C', 8),        # 13. Номер документа, удостоверяющего личность пациента (представителя) (справочник фонда) (В соответствии с маской (F011)).
            
            # Указывается в случае оказания медицинской помощи ребенку до государственной регистрации рождения.
            # 0 – признак отсутствует.
            # Если значение признака отлично от нуля, он заполняется по следующему шаблону:
            # ПДДММГГН, где
            # П – пол ребенка в соответствии с классификатором V005;
            # ДД – день рождения;
            # ММ – месяц рождения;
            # ГГ – последние две цифры года рождения;
            # Н – порядковый номер ребенка (до двух знаков).
            ('NOVOR', 'C', 9),    # 14. Признак новорожденного.
            
            # 1 – медицинская помощь оказана новорожденному ребенку до государственной регистрации рождения при многоплодных родах;
            # 2 – в документе, удостоверяющем личность пациента / представителя пациента, отсутствует имя и/или отчество.
            ('Q_G', 'C', 7),    # 15. Признак «Особый случай» при регистрации обращения за медицинской помощью.
            )
        return dbf


    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        accSysFilter = 'ClientIdentification.accountingSystem_id = %d' % \
            self.accSystemId if self.accSystemId else '1'

        stmt = u"""
        SELECT
            Client.id AS clientId,
            Event.id AS eventId,                                       -- ID_TALON
            Insurer.infisCode AS policyInsurer,                        -- INS
            1 AS admittance,                                           -- ADMITANCE
            Event.isPrimary AS primaryCode,                            -- PRIMARY
            IF(rbDiagnosticResult.regionalCode IS NULL,
                    EventResult.regionalCode,
                    rbDiagnosticResult.regionalCode) AS resultCode,    -- RESULT
            ClientWork.id IS NOT NULL AS isWork,                       -- WORK
            Event.setDate AS begDate,                                  -- DATIN
            Event.execDate AS endDate,                                 -- DATOUT
            Event.order AS eventOrder,                                 -- URGENT
            Account_Item.`sum` AS `sum`,                               -- PAY_SUM + STOIM_F
            LEAST(IF(Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Tariff.federalLimitation, Account_Item.amount)) * Tariff.federalPrice,
                            Account_Item.sum)  AS federalSum,          -- STOIM_F
            
            Client.lastName AS clientLastName,                         -- FAM
            Client.firstName AS clientFirstName,                       -- IMM
            Client.patrName AS clientPatrName,                         -- OTC
            ClientDocument.serial AS documentSerial,                   -- SER_PASP
            ClientDocument.number AS documentNumber,                   -- NUM_PASP
            rbDocumentType.regionalCode AS documentRegionalCode,       -- TYP_DOC
            Client.SNILS,                                              -- SS
            ClientIdentification.identifier AS identifier,             -- PIN
            ClientPolicy.serial AS policySerial,                       -- SERPOL
            ClientPolicy.number AS policyNumber,                       -- NMBPOL
            ClientPolicy.note AS policyNote,                           -- DOGOVOR
            ClientRegAddressKLADR.infis AS placeCode,                  -- TAUN
            Client.birthDate AS clientBirthDate,                       -- BIRTHDATE
            Client.sex AS clientSex,                                   -- SEX
            rbPolicyKind.regionalCode AS policyKind,                   -- TPOLIS
            ClientAttachLPU.infisCode AS attachLPUInfis,               -- MASTER
            ToothAPValue.value AS tooth,                               -- TOOTH
            Action.MKB AS toothMKB,                                    -- DIAG
            IF(Account_Item.visit_id IS NOT NULL, 
               VisitPersonSpeciality.regionalCode,
               IF(Account_Item.action_id IS NOT NULL,
                  IF(Action.person_id IS NOT NULL, 
                     ActPersonSpeciality.regionalCode,
                     ActSetPersonSpeciality.regionalCode),
                  rbSpeciality.regionalCode)) AS specialityCode,       -- SPEC
            IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.adultUetDoctor + rbItemService.adultUetAverageMedWorker,
                    IF(Account_Item.visit_id IS NOT NULL, 
                       rbVisitService.adultUetDoctor + rbVisitService.adultUetAverageMedWorker,
                       rbEventService.adultUetDoctor + rbEventService.adultUetAverageMedWorker)
                ) AS uet,                                              -- для UNITS_SUM
            IF(Account_Item.visit_id IS NOT NULL, VisitPerson.regionalCode,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, ActPerson.regionalCode,
                            ActSetPerson.regionalCode), Person.regionalCode)
                ) AS personCode,                                      -- P_CODE
            IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.code,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.code, rbEventService.code)
                    ) AS serviceCode,                                 -- ID_SERV
            Action.endDate AS actionDate,                             -- SERV_DATE
            Account_Item.amount AS amount,                            -- SERVNUMBER
            Insurer.OKATO AS insurerOKATO,
            Client.birthPlace AS birthPlace,                          -- MR
            RegRegionKLADR.OCATD AS OCATD,                            -- OKATOG, OKATOP
            age(Client.birthDate, Event.execDate) AS clientAge        -- Q_G
        FROM 
            Account_Item
            LEFT JOIN Event ON Event.id = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                      ClientPolicy.id = (SELECT MAX(CP.id)
                                         FROM   ClientPolicy AS CP
                                         LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                                         WHERE  CP.client_id = Client.id AND CP.deleted=0 AND CPT.code IN ('1','2'))
            LEFT JOIN rbPolicyKind ON rbPolicyKind.id = ClientPolicy.policyKind_id
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN ClientWork ON ClientWork.id = getClientWorkId(Client.id)
            LEFT JOIN ClientDocument ON ClientDocument.id = getClientDocumentId(Client.id)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN ClientIdentification ON ClientIdentification.client_id = Client.id
            LEFT JOIN ClientAttach ON ClientAttach.id = (SELECT MAX(tmpCA.id)
                                                         FROM ClientAttach AS tmpCA
                                                             LEFT JOIN rbAttachType AS tmpCAT ON tmpCAT.id =  tmpCA.attachType_id
                                                         WHERE
                                                             tmpCAT.temporary = 0
                                                             AND tmpCA.client_id = Client.id
                                                             AND tmpCA.deleted = 0)
            LEFT JOIN Organisation AS ClientAttachLPU ON ClientAttachLPU.id = ClientAttach.LPU_id
                                                         
            LEFT JOIN ClientAddress AS ClientRegAddress ON ClientRegAddress.id = getClientRegAddressId(Client.id)
            LEFT JOIN Address AS RegAddress ON RegAddress.id = ClientRegAddress.address_id
            LEFT JOIN AddressHouse AS RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
            LEFT JOIN kladr.KLADR AS ClientRegAddressKLADR ON ClientRegAddressKLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN kladr.KLADR RegRegionKLADR ON RegRegionKLADR.CODE = (
                SELECT RPAD(LEFT(RegAddressHouse.KLADRCode,2),13,'0'))
            
            LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id
            LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            
            LEFT JOIN Contract_Tariff AS Tariff ON Account_Item.tariff_id = Tariff.id
            
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN ActionProperty AS ToothAP ON ToothAP.action_id = Action.id
            LEFT JOIN ActionPropertyType AS ToothAPT ON ToothAPT.id = ToothAP.type_id
            INNER JOIN ActionProperty_String AS ToothAPValue ON ToothAPValue.id = ToothAP.id
            LEFT JOIN Person AS ActPerson ON ActPerson.id = Action.person_id
            LEFT JOIN rbSpeciality AS ActPersonSpeciality ON ActPersonSpeciality.id = ActPerson.speciality_id
            LEFT JOIN Person AS ActSetPerson ON ActSetPerson.id = Action.setPerson_id
            LEFT JOIN rbSpeciality AS ActSetPersonSpeciality ON ActSetPersonSpeciality.id = ActSetPerson.speciality_id
            
            LEFT JOIN Visit ON Visit.id = Account_Item.visit_id
            LEFT JOIN Person AS VisitPerson ON VisitPerson.id = Visit.person_id
            LEFT JOIN rbSpeciality AS VisitPersonSpeciality ON VisitPersonSpeciality.id = VisitPerson.speciality_id
            
            LEFT JOIN Person ON Person.id = Event.execPerson_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
        WHERE
            Diagnostic.person_id = Event.execPerson_id 
            AND Diagnostic.deleted = 0
            AND rbDiagnosisType.code IN ('1', '2')
            
            AND (ClientIdentification.id IS NULL OR ClientIdentification.deleted = 0)
            
            AND (Account_Item.action_id IS NULL OR
                    (ToothAP.deleted = 0
                     AND ToothAPT.deleted = 0
                     AND ToothAPT.name LIKE 'Номер зуба'))
            AND %s
            
        GROUP BY Account_Item.id
        """ % db.joinAnd([accSysFilter, tableAccountItem['id'].inlist(self.idList)])
        
        query = db.query(stmt)
        return query


    def process(self, dbf, record, codeLPU,  accNumber, settleDate):
        birthDate = forceDate(record.value('clientBirthDate'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        eventId = forceRef(record.value('eventId'))
        clientId = forceRef(record.value('clientId'))
        sum = forceDouble(record.value('sum'))
        federalSum = forceDouble(record.value('federalSum'))
        specialityCode = forceString(record.value('specialityCode'))
        actionDate = forceDate(record.value('actionDate'))

        (dbfStReestr, dbfTooth, dbfSpecVis, dbfServices, dbfGuests) = dbf[:5]
        
        if not self.mapEventIdToDbfRecord.has_key(eventId):
            insurerOKATO = forceString(record.value('insurerOKATO'))
            # ОКАТО всех объектов Мурманской области начинается с 47 (у Мурманской области окато 47000000000)
            if insurerOKATO[:2] != '47':
                dbfGuestsRecord = dbfGuests.newRecord()
                # Номер истории болезни
                dbfGuestsRecord['ID_TALON'] = eventId
                # Место рождения пациента или представителя
                dbfGuestsRecord['MR'] = forceString(record.value('birthPlace'))
                # Код места жительства по ОКАТО
                dbfGuestsRecord['OKATOG'] = forceString(record.value('OCATD'))
                # Код места пребывания по ОКАТО
                dbfGuestsRecord['OKATOP'] = forceString(record.value('OCATD'))
                # Код ОКАТО территории страхования по ОМС
                dbfGuestsRecord['OKATO_OMS'] = insurerOKATO 
                # Фамилия (представителя) пациента
                dbfGuestsRecord['FAMP'] = ''
                # Имя  (представителя) пациента
                dbfGuestsRecord['IMP'] =  ''
                # Отчество родителя (представителя) пациента
                dbfGuestsRecord['OTP'] = ''
                # Дата рождения (представителя) пациента
                dbfGuestsRecord['DRP'] = pyDate(QDate())
                # Код типа документа, удостоверяющего личность пациента (представителя) (по  справочнику фонда)
                dbfGuestsRecord['C_DOC'] = forceInt(record.value('documentRegionalCode'))
                # Серия документа, удостоверяющего личность пациента (представителя) (по справочнику фонда)
                dbfGuestsRecord['S_DOC'] = forceString(record.value('documentSerial'))
                # Номер документа, удостоверяющего личность пациента (представителя) (справочник фонда)
                dbfGuestsRecord['N_DOC'] = forceString(record.value('documentNumber'))
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
                dbfGuestsRecord['NOVOR'] = '0' # Признак новорожденного
                specState = ''
                age = forceInt(record.value('clientAge'))
                if not forceString(record.value('policySerial')) and not forceString(record.value('policyNumber')):
                    specState += '1'
                if age == 0:
                    specState += '2'
                if age < 14 and self.getClientRepresentativeInfo(clientId) != {}:
                    specState += '3'
                if not forceString(record.value('clientPatrName')):
                    specState += '4'
                dbfGuestsRecord['Q_G'] = specState
                dbfGuestsRecord.store()
                
            dbfRecord = dbfStReestr.newRecord()
            # Номер талона
            dbfRecord['ID_TALON'] = eventId
            # Код СМО (по справочнику фонда)
            insurerInfis = forceString(record.value('policyInsurer'))
            dbfRecord['INS'] = insurerInfis if insurerInfis in ('14', '17') else '01'
            # Тип приема
            dbfRecord['ADMITANCE'] = forceString(record.value('admittance'))
            # Отчетный месяц
            firstDayDate = QDate(settleDate.year(), settleDate.month(), 1)
            lastDayDate = QDate(settleDate.year(), settleDate.month(), settleDate.daysInMonth())
            dbfRecord['DATE_LO'] = pyDate(firstDayDate)
            # Дата по ...  |выписки
            dbfRecord['DATE_UP'] = pyDate(lastDayDate)
            # Признак первичности приема
            dbfRecord['PRIMARY'] = forceString(record.value('primaryCode'))
            # Полный исход лечения
            dbfRecord['RESULT'] = forceString(record.value('resultCode'))
            # Признак: работающий-1/неработающий-0 (пациент)
            dbfRecord['WORK'] = '' # '1' if forceBool(record.value('isWork')) else '0'
            # Дата начала лечения
            dbfRecord['DATIN'] = pyDate(begDate)
            # Дата окончания лечения
            dbfRecord['DATOUT'] = pyDate(endDate)
            # Признак оказания мед. Помощи (0 - плановая, 1 - экстренная; в базе: 1 - плановая, 2 - экстренная)
            dbfRecord['URGENT'] = '0' if forceInt(record.value('eventOrder')) == 1 else '1'
            # Количество посещений
            dbfRecord['VISITS'] = 1
            # Сумма единиц трудозатрат (УЕТ)
            dbfRecord['UNITS'] = forceDouble(record.value('uet'))
            # Сумма к оплате
            dbfRecord['PAY_SUM'] = sum - federalSum
            # Суммарная стоимость по расчетным данным Фонда (для ЛПУ сумма=0)
            dbfRecord['STOIM_V'] = 0.0
            # Фамилия пациента
            dbfRecord['FAM'] = nameCase(forceString(record.value('clientLastName')))
            # Имя пациента
            dbfRecord['IMM'] = nameCase(forceString(record.value('clientFirstName')))
            # Отчество пациента
            dbfRecord['OTC'] =  nameCase(forceString(record.value('clientPatrName')))
            # Серия документа, удостоверяющего личность
            dbfRecord['SER_PASP'] = forceString(record.value('documentSerial'))
            # Номер документа, удостоверяющего личность
            dbfRecord['NUM_PASP'] = forceString(record.value('documentNumber'))
            # Тип документа, удостоверяющего личность (приложение «Типы документов»)
            dbfRecord['TYP_DOC'] = forceInt(record.value('documentRegionalCode'))
            # Страховой номер индивидуального лицевого счета (СНИЛС)
            dbfRecord['SS'] = formatSNILS(forceString(record.value('SNILS')))
            # Персональный индивидуальный номер застрахованного по ОМС
            dbfRecord['PIN'] = forceString(record.value('identifier'))
            # Серия полиса
            dbfRecord['SERPOL'] = forceString(record.value('policySerial'))
            # Номер полиса
            dbfRecord['NMBPOL'] = forceString(record.value('policyNumber'))
            # Номер договора
            dbfRecord['DOGOVOR'] = forceString(record.value('policyNote'))
            # Код населенного пункта проживания пациента по справочнику фонда
            townCode = forceString(record.value('placeCode'))
            dbfRecord['TAUN'] = townCode if townCode and townCode != '000' else ''
            # Дата рождения пациента
            dbfRecord['BIRTHDAY'] = pyDate(birthDate)
            # Пол пациента
            sex = forceInt(record.value('clientSex'))
            dbfRecord['SEX'] = '1' if sex == 1 else (0 if sex == 2 else '') 
            # Номер реестра
            dbfRecord['ID_REESTR'] = accNumber
            # Код стоматологического  АПУ
            dbfRecord['ID_HOSP'] = codeLPU
            # Сумма по базовой программе гос. гарантий
            dbfRecord['STOIM_S'] = dbfRecord['PAY_SUM']
            # Сумма по сверхбазовой программе гос. гарантий
            dbfRecord['STOIM_R'] = 0
            # Сумма доплаты из средств Федерального фонда ОМС
            dbfRecord['STOIM_F'] = federalSum
            # Тип полиса
            dbfRecord['TPOLIS'] = forceInt(record.value('policyKind'))
            # Код ЛПУ приписки
            dbfRecord['MASTER'] = ''
            self.mapEventIdToDbfRecord[eventId] = dbfRecord
            self.mapEventIdToCountedDates[eventId] = [actionDate]
        else:
            dbfRecord = self.mapEventIdToDbfRecord[eventId]
            # Сумма к оплате
            dbfRecord['PAY_SUM'] = dbfRecord['PAY_SUM'] + (sum - federalSum)
            # Сумма по базовой программе гос. гарантий
            dbfRecord['STOIM_S'] = dbfRecord['PAY_SUM']
            # Сумма по сверхбазовой программе гос. гарантий
            dbfRecord['STOIM_R'] = 0
            # Сумма доплаты из средств Федерального фонда ОМС
            dbfRecord['STOIM_F'] = dbfRecord['STOIM_F']  + federalSum
            
            if actionDate not in self.mapEventIdToCountedDates[eventId]:
                # Количество посещений
                dbfRecord['VISITS'] = dbfRecord['VISITS'] + 1
                self.mapEventIdToCountedDates[eventId].append(actionDate)
            # Сумма единиц трудозатрат (УЕТ)
            dbfRecord['UNITS'] = dbfRecord['UNITS'] + forceDouble(record.value('uet'))
        dbfRecord.store()
        
        
        tooth = forceString(record.value('tooth'))
        if not self.mapToothToDbfRecord.has_key((eventId, tooth)):
            dbfRecord = dbfTooth.newRecord()
            # Номер талона
            dbfRecord['ID_TALON'] = eventId
            # Номер талона
            dbfRecord['TOOTH'] = tooth
            # Код диагноза
            dbfRecord['DIAG'] = forceString(record.value('toothMKB'))    
            # Код специальности медицинского работника, оказавшего услугу
            dbfRecord['SPEC'] = specialityCode
            # Количество посещений по данному заболеванию
            dbfRecord['VISITS'] = 1
            # Сумма единиц трудозатрат (УЕТ)
            dbfRecord['UNITS_SUM'] = forceDouble(record.value('uet'))
            # Номер реестра
            dbfRecord['ID_REESTR'] = accNumber
            # Код стоматологического  АПУ
            dbfRecord['ID_HOSP'] = codeLPU
            self.mapToothToDbfRecord[(eventId, tooth)] = dbfRecord 
            self.mapToothToCountedDates[(eventId, tooth)] = [actionDate]
        else:
            dbfRecord = self.mapToothToDbfRecord[(eventId, tooth)]
            if actionDate not in self.mapToothToCountedDates[(eventId, tooth)]:
                # Количество посещений
                dbfRecord['VISITS'] = dbfRecord['VISITS'] + 1
                self.mapToothToCountedDates[(eventId, tooth)].append(actionDate)
            # Сумма единиц трудозатрат (УЕТ)
            dbfRecord['UNITS_SUM'] = dbfRecord['UNITS_SUM'] + forceDouble(record.value('uet'))
        dbfRecord.store()  
        
        if not self.mapSpecialityToDbfRecord.has_key((eventId, specialityCode)):
            dbfRecord = dbfSpecVis.newRecord()
            # Номер талона
            dbfRecord['ID_TALON'] = eventId   
            # Код специальности медицинского работника, оказавшего услугу
            dbfRecord['SPEC'] = specialityCode
            # Количество посещений по данному заболеванию
            dbfRecord['VISITS'] = 1
            # Сумма единиц трудозатрат (УЕТ)
            dbfRecord['UNITS_SUM'] = forceDouble(record.value('uet'))
            # Номер реестра
            dbfRecord['ID_REESTR'] = accNumber
            # Код стоматологического  АПУ
            dbfRecord['ID_HOSP'] = codeLPU
            self.mapSpecialityToDbfRecord[(eventId, specialityCode)] = dbfRecord 
            self.mapSpecialityToCountedDates[(eventId, specialityCode)] = [actionDate]
        else:
            dbfRecord = self.mapSpecialityToDbfRecord[(eventId, specialityCode)]
#            if isVisit:
            # Количество посещений по данному заболеванию
            if actionDate not in self.mapSpecialityToCountedDates[(eventId, specialityCode)]:
                # Количество посещений
                dbfRecord['VISITS'] = dbfRecord['VISITS'] + 1
                self.mapSpecialityToCountedDates[(eventId, specialityCode)].append(actionDate)
            # Сумма единиц трудозатрат (УЕТ)
            dbfRecord['UNITS_SUM'] = dbfRecord['UNITS_SUM'] + forceDouble(record.value('uet'))
        dbfRecord.store()
        
        dbfRecord = dbfServices.newRecord()
        # Номер талона
        dbfRecord['ID_TALON'] = eventId
        # Номер талона
        dbfRecord['TOOTH'] = tooth
        # Код диагноза
        dbfRecord['DIAG'] = forceString(record.value('toothMKB'))
        # Диагноз первичный
        dbfRecord['DS0'] = dbfRecord['DIAG']
        # Код специальности медицинского работника, оказавшего услугу
        dbfRecord['SPEC'] = specialityCode
        # Личный код  медицинского работника, оказавшего услугу
        dbfRecord['P_CODE'] = forceString(record.value('personCode'))
        # Код услуги
        dbfRecord['ID_SERV'] = forceString(record.value('serviceCode'))
        # Дата оказания услуги
        dbfRecord['SERV_DATE'] = actionDate
        
        # Дата оказания услуги
        servDate = forceDate(record.value('actionDate'))
        if not servDate.isValid():
            servDate = endDate
        dbfRecord['SERV_DATE'] = pyDate(servDate)
        # Кол-во услуг данного типа
        dbfRecord['SERVNUMBER'] = forceInt(record.value('amount'))
        # Сумма единиц трудозатрат услуг (УЕТ)
        dbfRecord['UNITS_SUM'] = forceDouble(record.value('uet'))
        # Стоимость оказанной услуги
        dbfRecord['SERV_SUM'] = sum - federalSum
        # Номер реестра
        dbfRecord['ID_REESTR'] = accNumber
        # Код стоматологического  АПУ
        dbfRecord['ID_HOSP'] = codeLPU
        # Сумма по базовой программе гос. гарантий
        dbfRecord['STOIM_S'] = dbfRecord['SERV_SUM']
        # Сумма по сверхбазовой программе гос. гарантий
        dbfRecord['STOIM_R'] = 0
        # Сумма доплаты из средств Федерального фонда ОМС
        dbfRecord['STOIM_F'] = federalSum
        dbfRecord.store()


# *****************************************************************************************

    representativeInfoCache = {}

    def getClientRepresentativeInfo(self, clientId):
        result = self.representativeInfoCache.get(clientId, None)
        if result is None:
            result = getClientRepresentativeInfo(clientId)
            self.representativeInfoCache[clientId] = result
        return result

# *****************************************************************************************

#    def getTariff(self, tariffId):
#        result = self.tariffCache.get(tariffId, False)
#        if result == False:
#            result = None
#            if tariffId:
#                record = QtGui.qApp.db.getRecord('Contract_Tariff', '*', tariffId)
#                if record:
#                    result = CTariff(record)
#            self.tariffCache[tariffId] = result
#        return result


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


class CExportR51StomatologyOutDirPage(QtGui.QWizardPage, Ui_ExportR51StomatologyOutDirPage):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R51StomatologyExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        for src in ('STREESTR.DBF', 'TOOTH.DBF', 'SPEC_VIS.DBF',
                    'SERVICES.DBF', 'GUESTS.DBF'
                    ):
            srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                    os.path.basename(src))
            dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                    os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

            if not success:
                break

        if success:
            QtGui.qApp.preferences.appPrefs['R51StomatologyExportDir'] = toVariant(self.edtDir.text())
#            self.wizard().setAccountExposeDate()
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
                u'Выберите директорию для сохранения файла выгрузки по стоматологии для Мурманской области',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
