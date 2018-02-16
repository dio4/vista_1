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
from library.AmountToWords import amountToWords
from Registry.Utils import formatAddress
from Events.Action import CAction
from Exchange.Utils import getClientRepresentativeInfo

from Ui_ExportR67NativePage1 import Ui_ExportPage1
from Ui_ExportR67NativePage2 import Ui_ExportPage2


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    lpuCategory = ''
    tariffFactor = 1
    accountRecord = db.getRecord('Account', 'settleDate, number, exposeDate,'\
        'contract_id', accountId)
    if accountRecord:
        contractId = forceRef(accountRecord.value('contract_id'))

        contractRecord = db.getRecord('Contract', 'orgCategory, regionalTariffRegulationFactor', contractId)

        date = forceDate(accountRecord.value('settleDate'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        number = forceString(accountRecord.value('number'))

        if contractRecord:
            lpuCategory = forceString(contractRecord.value('orgCategory'))
            tariffFactor = forceDouble(contractRecord.value('regionalTariffRegulationFactor'))
    else:
        date = exposeDate = contractId = None
        number = ''
    return date, number, exposeDate, contractId,  lpuCategory,  tariffFactor


def exportR67Native(widget, accountId, accountItemIdList):
    wizard = CExportWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта Смоленской области')
        self.dbfFileName = ''
        self.tmpDir = ''
        self.contractId = None


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId, lpuCategory, tariffFactor = getAccountInfo(accountId)
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.contractId = contractId
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
            self.tmpDir = QtGui.qApp.getTmpDir('R67')
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


class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1):
    maxPageLines = 62
    hospitalLeavedResultMap = {
        u'выписан':'1',
        u'выписан в дневной стационар':'12',
        u'выписан в круглосуточный стационар':'13',
        u'переведен в другой стационар':'3',
        u'летальный':'5',
        u'смерть':'5',
    }

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
        self.parent = parent
        self.exportedClients = set()
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR67IgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR67VerboseLog', 'False')))
        self.chkExportFormatAliens.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR67ExportFormatAliens', 'False')))
        self.chkSkipZeroSum.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR67SkipZeroSum', 'True')))
        self.chkNumerateRecId.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR67NumerateClients', False)))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.clientNoteRegExp = re.compile(u'REGS:(?P<code>[^;]+);')
        self.currentOrgStructureId = None
        self.currentOrgStructureName = 'currentOrgStructureName'
        self.orgStuctStat = {}
        self.lines = 0
        self.pageNum = 1
        self.clientNum = 1
        self.appendixStr = QString(u"")
        self.appendixStream =  QTextStream(self.appendixStr)
        self.appendixStream.setCodec('CP866')
        self.accDate = QDate()
        self.contractId = None


    def validatePage(self):
        QtGui.qApp.preferences.appPrefs['ExportR67IgnoreErrors'] = toVariant(self.chkIgnoreErrors.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR67VerboseLog'] = toVariant(self.chkVerboseLog.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR67ExportFormatAliens'] = toVariant(self.chkExportFormatAliens.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR67SkipZeroSum'] = toVariant(self.chkSkipZeroSum.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR67NumerateClients'] = toVariant(self.chkNumerateRecId.isChecked())
        return self.done


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.chkExportFormatAliens.setEnabled(not flag)
        self.chkNumerateRecId.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)


    def log(self, str, forceLog = False):
        if self.chkVerboseLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self, aliens):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf(aliens)
        txt,  txtStream = self.createTxt()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery(self.parent.contractId)
        serviceQuery = self.createServiceQuery()
        self.progressBar.setMaximum(max(query.size()+serviceQuery.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query, txt,  txtStream,  serviceQuery


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
        return forceString(lpuCode + u'.DBF')


    def getTxtFileName(self):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
        return forceString(lpuCode + u'.TXT')


# *****************************************************************************************

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        lpuId = QtGui.qApp.currentOrgId()
        lpuOKPO = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'OKPO'))
        lpuOGRN = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'OGRN'))
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'infisCode'))
        self.log(u'ЛПУ: ОКПО "%s", ОГРН "%s", код инфис: "%s".' % (lpuOKPO, lpuOGRN, lpuCode))

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан код инфис', True)
            if not self.ignoreErrors:
                return

        aliens = self.chkExportFormatAliens.isChecked()
        dbf, query, txt, txtStream, serviceQuery = self.prepareToExport(aliens)
        self.accDate, accNumber, exposeDate, self.contractId, lpuCategory, tariffFactor =\
            getAccountInfo(self.parent.accountId)
        strContractNumber = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', self.contractId , 'number')) if self.contractId else u'б/н'
        self.exportedClients = set()
        process = self.processAliens if aliens else self.process

        if self.idList:
            self.clientNum = 1
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                process(dbf, query.record(), lpuCode, strContractNumber, exposeDate,  lpuCategory, tariffFactor, lpuOKPO)

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

        txt.close()
        for x in dbf:
            x.close()


    def createDbf(self,  aliens):
        return (self.createIDbf(), self.createCDbf()) if aliens else (self.createPDbf(),
                    self.createSDbf())


    def createTxt(self):
        txt = QFile(os.path.join(self.parent.getTmpDir(), self.getTxtFileName()))
        txt.open(QIODevice.WriteOnly | QIODevice.Text)
        txtStream =  QTextStream(txt)
        txtStream.setCodec('CP866')
        return txt,  txtStream


    def createPDbf(self):
        u""" Создает структуру dbf для файла 'Реестр пролеченных пациентов' """

        dbfName = os.path.join(self.parent.getTmpDir(), 'P'+self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            # Номер соответствующей записи из реестра пролеченных пациентов в основной базе ЛПУ
            ('RECID',  'C',  6),
            # Код ЛПУ
            ('MCOD', 'C',  7),
            # Серия и номер полиса пациента
            ('SN_POL', 'C', 25),
            # СНИЛС пациента
            ('SNILS', 'C', 14),
            # Фамилия пациента
            ('FAM', 'C',  25),
            # Имя пациента
            ('IM', 'C',  20),
            # Отчество пациента
            ('OT', 'C',  20),
            # Дата рождения пациента
            ('DR', 'D'),
            # Пол пациента
            ('W', 'N', 1),
            # Территория проживания
            ('REGS', 'C', 10),
            # Код улицы
            ('UL', 'N', 5, 0),
            # Дом
            ('DOM', 'C', 7),
            # Корпус
            ('KOR', 'C', 5),
            #  Строение
            ('STR', 'C', 5),
            # Квартира
            ('KV', 'C', 5),
            # Адрес пациента
            ('ADRES',  'C',  80),
            # Код МСО, выдавшей полис пациенту
            ('Q', 'C', 2),
            # Льготная категория пациента
            ('KT', 'C', 2),
            # Социальное положение пациента
            ('SP', 'C', 2),
            # Ведомственная принадлежность
            ('VED', 'C', 2),
            # Место работы
            ('MR', 'C', 30),
            # Признак «особый случай»
            ('D_TYPE', 'C', 1),
            #ИНН работодателя
            ('PS_INN', 'C', 12),
            #КРР работодателя
            ('PS_KPP', 'C', 9),
            #№ договора
            ('N_D', 'C', 10),
            #Дата договора
            ('DATE_D', 'D', 8)
            )

        return dbf


    def createSDbf(self):
        u"""Создает структуру dbf для файла 'Реестр медицинских услуг, оказанных в медицинских учреждениях' """

        dbfName = os.path.join(self.parent.getTmpDir(), 'S'+self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            # Номер соответствующей записи из реестра пролеченных пациентов в основной базе ЛПУ
            ('RECID','C', 6),
            # Код ЛПУ в кодировке ТФОМС
            ('MCOD', 'C', 7),
            # Серия и номер полиса пролеченного пациента
            ('SN_POL', 'C', 25),
            # Номер амбулаторной карты или истории болезни
            ('C_I', 'C', 18),
            # Код отделения, в котором выполнена услуга
            ('OTD', 'C', 4),
            # Код медицинской услуги (койко-дня, МЭСа)
            ('COD',  'N', 6, 0),
            # Признак учета по МЭСам
            ('TIP',  'C',  1),
            # Дата оказания услуги (выписки или перевода пациента)
            ('D_U',  'D'),
            # Количество услуг (для койко-дня, профильного пациента или МЭСа — фактическое количество койко-дней)
            ('K_U', 'N', 3, 0),
            # Основной диагноз
            ('DS', 'C',  6),
            # Сопутствующий диагноз
            ('DS2', 'C', 6),
            # Тип травмы
            ('TR',  'C',  2),
            # Вид госпитализации (планово/экстренно)
            ('EXTR',  'C', 1),
            # Признак стационарного пациента
            ('PS', 'C',  1),
            # Код исхода лечения
            ('BE', 'C', 2),
            # Табельный номер врача, оказавшего услугу (выписавшего пациента стационара)
            ('TN1', 'C',  6),
            # Табельный номер медсестры, оказавшей услугу
            ('TN2', 'C', 6),
            #Код тарифа
            ('TARIF', 'C', 1),
            # Категория ЛПУ
            ('KLPU', 'C',  1),
            # Коэффициент районного регулирования тарифов (по умолчанию -1 )
            ('KRR', 'N', 6, 3),
            # Уровень качества лечения (по умолчанию-1)
            ('UKL', 'N',  6, 3),
            # Коэффициент сложности курации (по умолчанию -1)
            ('SK', 'N', 4, 2),
            # Стоимость лечения
            ('S_ALL', 'N', 11, 2),
            # Код КСГ
            ('KSG', 'C',  6),
            # Признак «особый случай»
            ('D_TYPE', 'C', 1),
            # Количество койко-дней (посещений) по стандарту (используется в ТФОМС при проверке счета)
            ('STAND', 'N', 4),
            # Количество койко-дней (посещений) представленное к оплате (используется в ТФОМС при проверке счета)
            ('K_U_O', 'N', 3),
            #СНИЛС врача
            ('SSD', 'C', 14),
            #Код врачебной должности
            ('PRVD', 'N', 3, 0),
            #Код характера заболеваний
            ('Q_Z', 'N', 1, 0),
            #Вид медицинской помощи
            ('V_MU', 'N', 2, 0),
            #Код единицы учета медицинской помощи
            ('C_MU', 'N', 1, 0),
            #Количество единиц учета медицинской помощи
            ('K_MU', 'N', 5, 2),
            #Дата открытия больничного листа
            ('D_LISTIN', 'D'),
            #Дата закрытия больничного листа
            ('DLISTOUT', 'D')
            )
        return dbf

# *****************************************************************************************

    def createCDbf(self):
        u""" Создает структуру dbf для файла 'C' """

        dbfName = os.path.join(self.parent.getTmpDir(), 'C'+self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('M_OGRN', 'C', 8),  # КОд ЛПУ ОКПО
            ('SN_POL', 'C', 25),  # Серия и номер полиса ОМС пациента
            ('DATE_1', 'D'), # Дата начала оказания услуги
            ('DATE_2', 'D'), # Дата окончания оказания услуги
            ('C_I', 'C',  18), # Номер амбулаторной карты
            ('OTD', 'C', 4), # Код профиля вида медицинской помощи
            ('COD', 'C',  10), # Код оказанной услуги
            ('Q_U', 'N', 4), # Вид медецинской помощи
            ('K_U', 'N', 4), # Количество оказанных услуг
            ('DS', 'C',  6), # Диагноз по МКБ
            ('DS_S', 'C', 7), # Сопутствующий диагноз
            ('PS', 'C', 1),  # Признак стационара
            ('BE', 'C', 2), # Код исхода лечения
            ('TN1', 'C', 10), # Табельный номер врача
            ('TN2', 'C', 10), # Табельный номер седицинской сестры
            ('S_ALL', 'N', 11, 2), # Сумма за оказанные услуги
            ('STAND', 'N',  4),  # Количество койко-дней
            ('K_U_O', 'N', 4), # Кол-во койко-дней к оплате
            ('N_REC', 'N', 9), # Номер записи в таблице реестра пациента
            ('RECID', 'N', 9), # Номер записи в базе данных ЛПУ
            ('PRVS', 'C', 9), # Код специальности медицинского работника
            ('D_H', 'N',  9), # Номер истории создания записи
            ('VISIT', 'N', 9) # Количество посещений
            )
        return dbf


    def createIDbf(self):
        u""" Создает структуру dbf для файла 'I' """

        dbfName = os.path.join(self.parent.getTmpDir(), 'I'+self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('C_OKATO1', 'C',  5), # Код территории страхования по клас-ру ГАИ
            ('C_OKATO2', 'C', 5), # Код территории постоянной регистрации пациента по клас-уГАИ
            ('FAM', 'C', 60), # Фамилия пациента
            ('IM', 'C', 40), # Имя пациента
            ('OT', 'C', 40), # Отчество пациента
            ('W', 'N', 4), #Пол пациента
            ('SN_POL', 'C', 25), #Серия и номер полиса ОМС пациента
            ('DATE_N', 'D'), #Дата начала действия полиса ОМС
            ('DATE_E', 'D'), #Дата окончания действия полиса ОМС
            ('Q_NAME', 'C', 50), # Наименование СМО
            ('Q_OGRN', 'C', 8), # Код СМО ОКПО
            ('STAT_P', 'N', 4), #Статус представителя пациента
            ('FAMP', 'C', 30), #Фамилия представителя
            ('IMP', 'C', 20), #Имя представителя
            ('OTP', 'C', 20), #Отчество представителя
            ('DR', 'C', 10), #Дата рождения пациента
            ('MKB', 'N', 4), #Код классификатора МКБ
            ('M_OGRN', 'C', 8), #Код ЛПУ ОКПО
            ('SEND', 'L', 1), #Признак пересылки
            ('Q', 'C', 2), #Тип иногороднего
            ('D_H', 'N', 9), #Номер истории создания пациента
            ('C_DOC', 'N', 4), #Код документа, удостовер. личность
            ('S_DOC', 'C', 9), #Серия документа, удостовер. личность
            ('N_DOC', 'C', 8), #Номер документа, удостовер. личность
            ('R_NAME', 'C', 150), #Наименование района по месту регистрации пациента
            ('Q_NP', 'N', 4), #Код населенного пункта рег. пациента
            ('NP_NAME', 'C', 150), #Наименование населенного пункта по месту рег. пациента
            ('Q_UL', 'N', 4), #Код улицы
            ('UL_NAME', 'C', 150), #Наименование улицы
            ('DOM', 'C', 7), #Номер дома
            ('KOR', 'C', 5), #Корпус
            ('KV', 'C', 5), #Квартира
            ('C_OKSM', 'C', 3), #гражданство пациента по классификатору ОКСМ
            ('STAT_Z', 'N', 4 ), #Статус пациента
            ('PLACE_W', 'C', 150), #Место работы пациента
            ('RECID', 'N', 9), #Порядковый номер пациента в базе данных ЛПУ
            ('N_PP', 'N', 9), #Номер пациента в таблице реестров
            ('I_TYPE', 'N', 4), #Код причины отказа
            ('Q_G', 'C', 5) #Код особого случая
            )
        return dbf

# *****************************************************************************************

    def createQuery(self, contractId):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        insurerId = None

        if contractId:
            insurerId = forceRef(db.translate('Contract_Contingent',
                'master_id', contractId, 'insurer_id'))

        insurerRequest = 'AND CP.insurer_id = ''%d''' % insurerId if insurerId else ''
        stmt = """SELECT
                Account_Item.event_id,
                Account_Item.id AS serviceId,
                Event.client_id,
                TRIM(CONCAT(ClientPolicy.serial,' ', ClientPolicy.number)) AS policySN,
                ClientPolicy.begDate AS policyBegDate,
                ClientPolicy.endDate AS policyEndDate,
                Client.SNILS,
                Client.lastName,
                Client.firstName,
                Client.patrName,
                Client.birthDate,
                Client.sex,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    RegAddressHouse.KLADRCode, LocAddressHouse.KLADRCode) AS KLADRCode,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    regKLADR.OCATD, locKLADR.OCATD) AS placeOKATO,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    regKLADR.infis, locKLADR.infis) AS placeCode,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    regKLADR.NAME, locKLADR.NAME) AS placeName,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    regKLADRStreet.infis, locKLADRStreet.infis) AS streetCode,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    regKLADRStreet.NAME, locKLADRStreet.NAME) AS streetName,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    RegAddressHouse.number, LocAddressHouse.number) AS number,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    RegAddressHouse.corpus, LocAddressHouse.corpus) AS corpus,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    RegAddress.flat, LocAddress.flat) AS flat,
                IF (LocAddressHouse.KLADRCode IS NULL,
                    ClientRegAddress.freeInput, ClientLocAddress.freeInput) AS freeInput,
                Insurer.infisCode AS policyInsurer,
                Insurer.fullName AS insurerName,
                Insurer.OKPO AS insurerOKPO,
                Insurer.OKATO AS insurerOKATO,
                IF(work.title IS NOT NULL,
                    work.title, ClientWork.freeInput) AS `workName`,
                work.INN AS workINN,
                work.KPP AS workKPP,
                OrgStructure.infisCode AS orgStructureCode,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.infis,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                  ) AS serviceCode,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.qualityLevel,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.qualityLevel, rbEventService.qualityLevel)
                  ) AS qualityLevel,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.superviseComplexityFactor,
                   IF(Account_Item.visit_id IS NOT NULL,
                      rbVisitService.superviseComplexityFactor,
                      rbEventService.superviseComplexityFactor
                     )
                  ) AS superviseFactor,
                IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.code,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.code, EventMedicalAidProfile.code)
                  ) AS medicalAidProfileCode,
                Account_Item.amount,
                Account_Item.sum,
                IF(Action.MKB != '', Action.MKB, Diagnosis.MKB) AS MKB,
                AccDiagnosis.MKB AS AccMKB,
                rbTraumaType.code AS traumaTypeCode,
                IF(rbDiagnosticResult.regionalCode IS NULL,
                   EventResult.regionalCode,
                   rbDiagnosticResult.regionalCode
                  ) AS resultCode,
                Person.regionalCode AS personRegionalCode,
                Person.code AS personCode,
                Person.SNILS AS personSNILS,
		visitPerson.code AS visitPersonCode,
                rbSpeciality.regionalCode AS specialityCode,
                rbDiseaseCharacter.code AS characterCode,
                rbMedicalAidType.regionalCode AS medicalAidTypeCode,
                TempInvalid.begDate AS tempInvalidBegDate,
                TempInvalid.endDate AS tempInvalidEndDate,
                Event.execDate AS endDate,
                Benefit.regionalCode AS benefitCode,
                SocStatus.regionalCode AS socStatusCode,
                mes.MES.code AS mesCode,
                mes.MES.maxDuration AS mesAmount,
                rbMedicalAidUnit.regionalCode AS medicalAidUnitCode,
                Event.`order`,
                IF (HospitalAction.id IS NOT NULL,1,0) AS hospitalFlag,
                HospitalAction.id AS hospitalActionId,
                rbPost.regionalCode AS personPost,
                rbDocumentType.code AS documentTypeCode,
                age(Client.birthDate, Event.execDate) AS clientAge,
                Client.notes AS clientNotes,
                Visit.date AS visitDate,
                Action.endDate AS actionDate,
                ClientDocument.serial AS documentSerial,
                ClientDocument.number AS documentNumber,
                Citizenship.regionalCode AS citizenshipCode,
                HospitalLeavedAction.id AS hospitalLeavedActionId,
                MC.movementCount AS movementCount,
                HospitalAction.id AS lastMovementId,
                ActionType.flatCode AS actionFlatCode,
                Action.id AS actionId,
                Contract_Tariff.price AS tariffPrice,
                Contract_Tariff.frag1Start,
                ClientRegAddress.address_id AS addressId,
                IF (Contract_Tariff.tariffType IN ('8','9','10'),1,0) AS isMes
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
            ClientPolicy.id = (SELECT MAX(CP.id)
                FROM ClientPolicy AS CP
                LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                WHERE CP.client_id = Client.id
                    AND CP.deleted=0 %s
                    AND CPT.code IN ('1','2'))
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
            LEFT JOIN kladr.KLADR AS regKLADR ON regKLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN kladr.KLADR AS locKLADR ON locKLADR.CODE = LocAddressHouse.KLADRCode
            LEFT JOIN kladr.STREET AS regKLADRStreet ON regKLADRStreet.CODE = RegAddressHouse.KLADRStreetCode
            LEFT JOIN kladr.STREET AS locKLADRStreet ON locKLADRStreet.CODE = LocAddressHouse.KLADRStreetCode
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                      AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE 
                                                                          IF(IF(Account_Item.service_id IS NOT NULL,
                                                                                rbItemService.infis,
                                                                                IF(Account_Item.visit_id IS NOT NULL, 
                                                                                    rbVisitService.infis, 
                                                                                    rbEventService.infis)
                                                                             ) = '070042', 
                                                                            code in ('3'), 
                                                                            code IN ('1', '2')))                                                                          
                                      AND Diagnostic.person_id = Event.execPerson_id AND Diagnostic.deleted = 0)
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
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN OrgStructure AS setOrgStruct ON Person.orgStructure_id = setOrgStruct.id
            LEFT JOIN Person AS visitPerson ON visitPerson.id = Visit.person_id
            LEFT JOIN Diagnostic AS AccDiagnostic ON AccDiagnostic.id = (
             SELECT id FROM Diagnostic AS AD
             WHERE AD.event_id = Account_Item.event_id AND
                AD.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='9') AND
                AD.person_id = Event.execPerson_id AND
                AD.deleted = 0 LIMIT 1)
            LEFT JOIN Diagnosis AS AccDiagnosis ON
                AccDiagnosis.id = AccDiagnostic.diagnosis_id AND
                AccDiagnosis.deleted = 0
            LEFT JOIN rbTraumaType ON rbTraumaType.id = Diagnosis.traumaType_id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
            LEFT JOIN rbDiseaseCharacter ON Diagnosis.character_id = rbDiseaseCharacter.id
            LEFT JOIN TempInvalid ON
                TempInvalid.id = (
                    SELECT  TI.id
                    FROM    TempInvalid TI
                    WHERE   TI.client_id = Client.id AND
                                TI.deleted = 0 AND
                                (TI.begDate IS NULL OR TI.begDate >= Event.setDate) AND
                                (TI.endDate IS NULL OR TI.endDate <= Event.execDate)
                    LIMIT 1
                )
            LEFT JOIN ClientSocStatus ClientBenefit ON
                ClientBenefit.id = (
                    SELECT MAX(CSS.id)
                    FROM ClientSocStatus CSS
                    WHERE CSS.client_id = Client.id AND
                              CSS.deleted = 0 AND
                              (CSS.begDate IS NULL OR CSS.begDate >= Event.setDate) AND
                              (CSS.endDate IS NULL OR CSS.endDate <= Event.execDate) AND
                              CSS.socStatusClass_id = (
                                    SELECT S.id
                                    FROM rbSocStatusClass S
                                    WHERE S.code = '1'
                                    LIMIT 1
                              )
                    LIMIT 1
                )
            LEFT JOIN rbSocStatusType Benefit ON ClientBenefit.socStatusType_id = Benefit.id
            LEFT JOIN ClientSocStatus CSocStatus ON
                CSocStatus.id = (
                    SELECT MAX(CSS.id)
                    FROM ClientSocStatus CSS
                    WHERE CSS.client_id = Client.id AND
                              CSS.deleted = 0 AND
                              (CSS.begDate IS NULL OR CSS.begDate >= Event.setDate) AND
                              (CSS.endDate IS NULL OR CSS.endDate <= Event.execDate) AND
                              CSS.socStatusClass_id = (
                                    SELECT S.id
                                    FROM rbSocStatusClass S
                                    WHERE S.code = '9'
                                    LIMIT 1
                              )
                    LIMIT 1
                )
            LEFT JOIN rbSocStatusType SocStatus ON CSocStatus.socStatusType_id = SocStatus.id
            LEFT JOIN Action AS HospitalAction ON
                HospitalAction.id = (
                    SELECT MAX(A.id)
                    FROM Action A
                    WHERE A.event_id = Event.id AND
                              A.deleted = 0 AND
                              A.actionType_id = (
                                    SELECT AT.id
                                    FROM ActionType AS AT
                                    WHERE AT.flatCode ='moving'
                              )

                )
            LEFT JOIN Action AS HospitalLeavedAction ON
                HospitalLeavedAction.id = (
                    SELECT MAX(A.id)
                    FROM Action A
                    WHERE A.event_id = Event.id AND
                              A.deleted = 0 AND
                              A.actionType_id = (
                                    SELECT AT.id
                                    FROM ActionType AT
                                    WHERE AT.flatCode ='leaved'
                              )

                )
            LEFT JOIN mes.MES ON Event.MES_id = mes.MES.id
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN rbMedicalAidUnit ON Contract_Tariff.unit_id = rbMedicalAidUnit.id
            LEFT JOIN rbPost ON Person.post_id = rbPost.id
            LEFT JOIN ClientSocStatus AS ClientCitizenshipStatus ON
                ClientCitizenshipStatus.client_id = Client.id AND
                ClientCitizenshipStatus.deleted = 0 AND
                ClientCitizenshipStatus.socStatusClass_id = (
                    SELECT rbSSC.id
                    FROM rbSocStatusClass AS rbSSC
                    WHERE rbSSC.code = '8' AND rbSSC.group_id IS NULL
                    LIMIT 0,1
                )
            LEFT JOIN rbSocStatusType AS Citizenship ON
                ClientCitizenshipStatus.socStatusType_id = Citizenship.id
            LEFT JOIN rbMedicalAidProfile AS EventMedicalAidProfile ON
                EventMedicalAidProfile.id = rbEventService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS VisitMedicalAidProfile ON
                VisitMedicalAidProfile.id = rbVisitService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON
                ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN (
                SELECT AI1.event_id, COUNT(DISTINCT action_id) AS movementCount FROM Account_Item AS AI1
                LEFT JOIN `Action` AS Ac1 ON AI1.action_id = Ac1.id
                LEFT JOIN ActionType AS AT1 ON Ac1.actionType_id = AT1.id
                WHERE AT1.flatCode = 'moving'
                GROUP BY AI1.event_id
            ) AS MC ON MC.event_id = Account_Item.event_id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
        """ % (insurerRequest,  tableAccountItem['id'].inlist(self.idList))
#            ORDER BY insurerName
        return db.query(stmt)

# *****************************************************************************************

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
                SUM(IF (HospitalAction.id IS NULL,Account_Item.amount,NULL)) AS serviceCount,
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
                IF(Contract_Tariff.tariffType IN ('8','9','10'),1,0) AS isMES1,
                COUNT(DISTINCT Event.client_id) AS clientCount,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7',Event.client_id,NULL)) AS hospClientCount,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7',Event.client_id,NULL)) AS dayHospClientCount,
                COUNT(DISTINCT IF (HospitalAction.id IS NOT NULL,NULL,Event.client_id)) AS ambClientCount,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'),Account_Item.`sum`,0)) AS hospSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType NOT IN ('8','9','10'),Account_Item.`sum`,0)) AS dayHospSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code != '7' AND Contract_Tariff.tariffType IN ('8','9','10'),Account_Item.`sum`,0)) AS hospMesSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND rbMedicalAidType.code = '7' AND Contract_Tariff.tariffType IN ('8','9','10'),Account_Item.`sum`,0)) AS dayHospMesSum,
                SUM(IF (HospitalAction.id IS NOT NULL,0,Account_Item.`sum`)) AS ambSum,
                SUM(IF (HospitalAction.id IS NOT NULL AND Contract_Tariff.tariffType NOT IN ('8','9','10') AND Account_Item.`sum` != 0,
                    Account_Item.`amount`-IF(Contract_Tariff.price=0 AND Contract_Tariff.frag1Start>0,Contract_Tariff.frag1Start,0 ),0)) AS bedDays,
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

# *****************************************************************************************

    def process(self, dbf, record, codeLPU, contractNumber, contractDate,  lpuCategory,  tariffFactor, lpuOKPO):
        (dbfP, dbfS) = dbf

        if self.chkSkipZeroSum.isChecked() and forceDouble(record.value('sum')) == 0:
            return

        eventId = forceString(record.value('event_id'))
        clientId = forceString(record.value('client_id'))
        policySN = forceString(record.value('policySN'))
        age = forceInt(record.value('clientAge'))
        documentTypeCode = forceString(record.value('documentTypeCode'))
        specialCase = ''

        if ((not policySN) or policySN == '') and documentTypeCode == '1':
            specialCase += '1' #Пациент при обращении в ЛПУ предъявил только паспорт гражданина РФ
        if documentTypeCode != '1':
            specialCase += '2' #Пациент при обращении в ЛПУ предъявил иной документ, удостоверяющий личность
        if age < 1:
            specialCase += '3' #Медицинская помощь оказана новорожденному
        if age < 1 and documentTypeCode != '3':
            specialCase += '4' # При регистрации оказания медицинской помощи ребенку был предъявлен паспорт одного из его родителей или законных представителей
        if forceString(record.value('patrName')) == '':
            specialCase += '5' # У пациента по документу, удостоверяющему личность, отсутствует отчество.

        if not(clientId in self.exportedClients):
            row = dbfP.newRecord()
            # Номер соответствующей записи из реестра пролеченных пациентов в основной базе ЛПУ
            row['RECID'] = forceString(self.clientNum) if self.chkNumerateRecId.isChecked() else clientId
            # Код ЛПУ
            row['MCOD'] = codeLPU
            # Серия и номер полиса пациента
            row['SN_POL'] = policySN
            # СНИЛС пациента
            row['SNILS'] = forceString(record.value('SNILS'))
            # Фамилия пациента
            row['FAM'] =forceString(record.value('lastName'))
            # Имя пациента
            row['IM'] =forceString(record.value('firstName'))
            # Отчество пациента
            row['OT'] = forceString(record.value('patrName'))
            # Дата рождения пациента
            row['DR'] = pyDate(forceDate(record.value('birthDate')))
            # Пол пациента
            row['W'] = forceInt(record.value('sex'))
            # Территория проживания
            row['REGS'] = forceString(record.value('placeCode'))

            #if row['REGS'] == '':
            # попытка вытащить код из примечания к клиенту
            # он пишется  туда в формате REGS:код; утилитой импорта населения
            m = self.clientNoteRegExp.search(forceString(record.value('clientNotes')))

            if m:
                row['REGS'] = m.group('code')

            # Код улицы
            row['UL'] = forceInt(record.value('streetCode'))
            # Дом
            row['DOM'] = forceString(record.value('number'))
            # Корпус
            row['KOR'] = forceString(record.value('corpus'))
            #  Строение
            row['STR'] = forceString(record.value('corpus'))
            # Квартира
            row['KV'] = forceString(record.value('flat'))
            # Адрес пациента
            clientAddress = formatAddress(forceRef(record.value('addressId')))
            row['ADRES'] = clientAddress if clientAddress else forceString(record.value('freeInput'))
            # Код МСО, выдавшей полис пациенту
            row['Q'] = forceString(record.value('policyInsurer'))
            # Льготная категория пациента
            row['KT'] = forceString(record.value('benefitCode')).rjust(2)
            # Социальное положение пациента
            row['SP'] = forceString(record.value('socStatusCode')).rjust(2)
            # Ведомственная принадлежность
            #('VED', 'C', 2),
            # Место работы
            row['MR'] = forceString(record.value('workName'))
            # Признак «особый случай»
            row['D_TYPE'] = specialCase if specialCase else '0'
            #ИНН работодателя
            row['PS_INN'] = forceString(record.value('workINN'))
            #КРР работодателя
            row['PS_KPP'] = forceString(record.value('workKPP'))
            #№ договора
            row['N_D'] = contractNumber
            #Дата договора
            row['DATE_D'] = pyDate(contractDate)
            row.store()
            self.exportedClients.add(clientId)
            self.clientNum += 1

        row = dbfS.newRecord()
        # Номер соответствующей записи из реестра пролеченных пациентов в основной базе ЛПУ
        row['RECID']  = forceString(record.value('serviceId'))[-6:]
        # Код ЛПУ в кодировке ТФОМС
        row['MCOD'] = codeLPU
        # Серия и номер полиса пролеченного пациента
        row['SN_POL'] = policySN
        # Номер амбулаторной карты или истории болезни
        row['C_I'] = eventId
        # Код отделения, в котором выполнена услуга
        if forceBool(record.value('hospitalFlag')):
            r = QtGui.qApp.db.getRecord('Action', '*', forceRef(record.value('hospitalActionId')))

            if r:
                action = CAction(record=r)
                orgStructureId = action[u'Отделение пребывания']
                row['OTD'] = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'infisCode'))

            r = QtGui.qApp.db.getRecord('Action', '*', forceRef(record.value('hospitalLeavedActionId')))

            if r:
                action = CAction(record=r)
                row['BE'] = self.hospitalLeavedResultMap.get(action[u'Исход госпитализации'], '').rjust(2)

            if forceString(record.value('actionFlatCode')) == 'moving' and \
                forceInt(record.value('movementCount')) > 1 and \
                forceRef(record.value('lastMovementId')) != forceRef(record.value('actionId')):
                    # При наличии в обращении одного Движения, все остается так же поле BE заполняется из действия Выписка.
                    # При наличии переводов и соответственно нескольких движений, то во всех кроме последнего в поле BE
                    # заполняется кодом 3-перевод, а для последнего как обычно из действия Выписка.
                    row['BE'] = '3'.rjust(2)
        else:
            row['OTD'] = forceString(record.value('orgStructureCode'))
            # Код исхода лечения
            row['BE'] = forceString(record.value('resultCode')).rjust(2)

        # Код медицинской услуги (койко-дня, МЭСа)
        row['COD'] = forceInt(record.value('serviceCode')) % 10**6
        # Признак учета по МЭСам
        isMes = forceBool(record.value('isMes'))
        amount = forceInt(record.value('amount'))
        frag1Start = forceInt(record.value('frag1Start'))

        if isMes:
            row['TIP']  ='0' if amount >= frag1Start else '1'

        # Дата оказания услуги (выписки или перевода пациента)
        servDate = forceDate(record.value('actionDate'))

        if not servDate.isValid():
            servDate = forceDate(record.value('visitDate'))

            if not servDate.isValid():
                servDate = forceDate(record.value('endDate'))

        if not servDate.isValid():
            self.log(u'Не задана дата услуги: accountItemId=%d,'\
                u' код карточки "%d".' % (forceRef(record.value('serviceId')), eventId))

        row['D_U'] = pyDate(servDate)
        # Количество услуг (для койко-дня, профильного пациента или МЭСа — фактическое количество койко-дней)

#        if isMes:
#            row['K_U'] = amount
#        else:
        if forceDouble(record.value('tariffPrice')) == 0 and frag1Start > 0:
            amount -= frag1Start

        row['K_U'] = amount

        # Основной диагноз
        row['DS'] = forceString(record.value('MKB'))
        # Сопутствующий диагноз
        row['DS2'] = forceString(record.value('AccMKB'))
        # Тип травмы
        row['TR'] =forceString(record.value('traumaTypeCode'))
        # Вид госпитализации (планово/экстренно)
        row['EXTR'] = forceString(record.value('order'))
        # Признак стационарного пациента
        row['PS'] = forceString(record.value('hospitalFlag'))

        # Табельный номер врача, оказавшего услугу (выписавшего пациента стационара)
        personCode = forceString(record.value('personCode'))
        visitPersonCode = forceString(record.value('visitPersonCode'))
	if visitPersonCode:        
	    row['TN1'] = visitPersonCode
	else:
            row['TN1'] = personCode
        # Табельный номер медсестры, оказавшей услугу
        if personCode[:1] in ('4', '5'):
            row['TN2'] = personCode
        #Код тарифа
        row['TARIF'] = '5' #forceString(record.value('serviceCode'))
        # Категория ЛПУ
        row['KLPU'] = lpuCategory
        # Коэффициент районного регулирования тарифов (по умолчанию -1 )
        row['KRR'] = tariffFactor
        # Уровень качества лечения (по умолчанию-1)
        row['UKL'] = forceDouble(record.value('qualityLevel'))
        # Коэффициент сложности курации (по умолчанию -1)
        row['SK'] = forceDouble(record.value('superviseFactor'))
        # Стоимость лечения
        row['S_ALL'] = forceDouble(record.value('sum'))
        # Код КСГ
        row['KSG'] = forceString(record.value('mesCode'))
        # Признак «особый случай»
        row['D_TYPE'] = specialCase if specialCase else '0'
        # Количество койко-дней (посещений) по стандарту (используется в ТФОМС при проверке счета)
        row['STAND'] = forceInt(record.value('mesAmount'))
        # Количество койко-дней (посещений) представленное к оплате (используется в ТФОМС при проверке счета)
        row['K_U_O'] = forceInt(record.value('amount'))
        #СНИЛС врача
        row['SSD'] = forceString(record.value('personSNILS'))
        #Код врачебной должности
        row['PRVD'] = forceInt(record.value('personPost'))
        #Код характера заболеваний
        row['Q_Z'] = forceInt(record.value('characterCode'))
        #Вид медицинской помощи
        row['V_MU'] = forceInt(record.value('medicalAidTypeCode'))
        #Код единицы учета медицинской помощи
        row['C_MU'] = forceInt(record.value('medicalAidUnitCode'))
        #Количество единиц учета медицинской помощи
        row['K_MU'] = forceInt(record.value('amount'))
        #Дата открытия больничного листа
        row['D_LISTIN'] = pyDate(forceDate(record.value('tempInvalidBegDate')))
        #Дата закрытия больничного листа
        row['DLISTOUT'] = pyDate(forceDate(record.value('tempInvalidEndDate')))
        row.store()

# *****************************************************************************************

    def processAliens(self, dbf, record, codeLPU, contractNumber, contractDate,  lpuCategory,  tariffFactor, lpuOKPO):
        (dbfI, dbfC) = dbf
        clientId = forceString(record.value('client_id'))

        if not(clientId in self.exportedClients):
            row = dbfI.newRecord()
            #'C', 5 Код территории страхования по клас-ру ГАИ
            row['C_OKATO1'] = forceString(record.value('insurerOKATO'))
            #'C', 5 Код территории постоянной регистрации пациента по клас-уГАИ
            row['C_OKATO2'] = forceString(record.value('placeOKATO'))
            #'C', 60 Фамилия пациента
            row['FAM'] = forceString(record.value('lastName'))
            #'C', 40 Имя пациента
            row['IM'] = forceString(record.value('firstName'))
            #'C', 40 Отчество пациента
            row['OT'] = forceString(record.value('patrName'))
            #'N', 4 Пол пациента
            row['W'] = forceInt(record.value('sex'))
            # 'C', 25 Серия и номер полиса ОМС пациента
            row['SN_POL'] = forceString(record.value('policySN'))
            #Дата начала действия полиса ОМС
            row['DATE_N'] =pyDate(forceDate(record.value('policyBegDate')))
            #Дата окончания действия полиса ОМС
            row['DATE_E'] =pyDate(forceDate(record.value('policyEndDate')))
            # 'C', 50, Наименование СМО
            row['Q_NAME'] = forceString(record.value('insurerName'))
            # 'C', 8, Код СМО ОКПО
            row['Q_OGRN'] = forceString(record.value('insurerOKPO'))

            info = getClientRepresentativeInfo(forceRef(record.value('client_id')))

            if info != {}:
                #'N', 4, Статус представителя пациента
                r = info.get('relationTypeCode', 0)
                row['STAT_P'] = forceInt(r if r else 0)
                #Фамилия представителя
                row['FAMP']  = info.get('lastName')
                #Имя представителя
                row['IMP'] = info.get('firstName')
                #Отчество представителя
                row['OTP'] = info.get('patrName')

            #'C', 10, Дата рождения пациента
            row['DR'] = forceString(record.value('birthDate'))
            #'N', 4, Код классификатора МКБ
            row['MKB'] = forceInt(record.value('MKB'))
            # 'C', 8, Код ЛПУ ОКПО
            row['M_OGRN'] = lpuOKPO
            #'L', 1, Признак пересылки
            row['SEND'] = False
            # 'C', 2, Тип иногороднего
            row['Q'] = '--'
            #Номер истории создания пациента
            row['D_H'] = forceInt(clientId)
            #'N', 4, Код документа, удостовер. личность
            row['C_DOC']  = forceInt(record.value('documentTypeCode'))
            #'C', 9, Серия документа, удостовер. личность
            row['S_DOC'] = forceString(record.value('documentSerial'))
            #'C', 8, Номер документа, удостовер. личность
            row['N_DOC'] = forceString(record.value('documentNumber'))
            #'C', 150, Наименование района по месту регистрации пациента
            row['R_NAME'] = self.getKLADRName(forceString(record.value('KLADRCode'))[:5])
            #'N', 4, Код населенного пункта рег. пациента
            row['Q_NP'] = forceInt(record.value('placeCode'))
            # 'C', 150, Наименование населенного пункта по месту рег. пациента
            row['NP_NAME'] = forceString(record.value('placeName'))
            # 'N', 4, Код улицы
            row['Q_UL'] = forceInt(record.value('streetCode'))
            #, 'C', 150, Наименование улицы
            row['UL_NAME'] = forceString(record.value('streetName'))
            # 'C', 7, Номер дома
            row['DOM'] = forceString(record.value('number'))
            #, 'C', 5), Корпус
            row['KOR'] = forceString(record.value('corpus'))
            #, 'C', 5), #Квартира
            row['KV'] = forceString(record.value('flat'))
            # 'C', 3, гражданство пациента по классификатору ОКСМ
            row['C_OKSM'] = forceString(record.value('citizenshipCode'))
            # 'N', 4 ), Статус пациента
            row['STAT_Z'] =forceInt(record.value('socStatusCode'))
            # 'C', 150, #Место работы пациента
            row['PLACE_W'] = forceString(record.value('workName'))
            # 'N', 9, #Порядковый номер пациента в базе данных ЛПУ
            row['RECID'] = forceInt(clientId)
            #('N_PP', 'N', 9), #Номер пациента в таблице реестров
            #('I_TYPE', 'N', 4), #Код причины отказа
            #('Q_G', 'C', 5) #Код особого случая
            row.store()

        row = dbfC.newRecord()
        #, 'C', 8),  # КОд ЛПУ ОКПО
        row['M_OGRN'] = lpuOKPO
        #, 'C', 25),  # Серия и номер полиса ОМС пациента
        row['SN_POL'] = forceString(record.value('policySN'))
        #, 'D'), # Дата начала оказания услуги
        servDate = forceDate(record.value('actionDate'))

        if not servDate.isValid():
            servDate = forceDate(record.value('visitDate'))

            if not servDate.isValid():
                servDate = forceDate(record.value('endDate'))

        if not servDate.isValid():
            self.log(u'Не задана дата услуги: accountItemId=%d,'\
                u' код карточки "%d".' % (forceRef(record.value('serviceId')), forceInt(record.value('event_id'))))

        row['DATE_1'] = pyDate(servDate)
        #, 'D'), # Дата окончания оказания услуги
        row['DATE_2'] = pyDate(forceDate(record.value('endDate')))
        #, 'C',  18), Номер амбулаторной карты
        row['C_I'] = clientId
        # 'C', 4),  Код профиля вида медицинской помощи
        row['OTD'] = forceString(record.value('medicalAidProfileCode'))
        #, 'C',  10), Код оказанной услуги
        row['COD'] = forceString(record.value('serviceCode'))
        # 'N', 4), Вид медецинской помощи
        row['Q_U'] = forceInt(record.value('medicalAidTypeCode'))
        #, 'N', 4), # Количество оказанных услуг
        row['K_U'] = forceInt(record.value('amount'))
        # , 'C',  6), Диагноз по МКБ
        row['DS'] = forceString(record.value('MKB'))
        # , 'C', 7),  Сопутствующий диагноз
        row['DS_S'] = forceString(record.value('AccMKB'))
        # , 'C', 1,  # Признак стационара
        hospitalFlag = forceBool(record.value('hospitalFlag'))
        row['PS'] = '1' if hospitalFlag else '0'
        #, 'C', 2, # Код исхода лечения
        row['BE'] = forceString(record.value('resultCode'))
        personCode = forceString(record.value('personCode'))
        # , 'C', 10), # Табельный номер врача
        row['TN1'] = personCode
        #, 'C', 10), # Табельный номер седицинской сестры
        if personCode[:1] in ('4', '5'):
            row['TN2'] = personCode
        # 'N', 11, 2), # Сумма за оказанные услуги
        row['S_ALL'] = forceDouble(record.value('sum'))

        if hospitalFlag:
            #'N',  4),  # Количество койко-дней
            row['STAND'] = forceInt(record.value('mesAmount'))
            #, 'N', 4), # Кол-во койко-дней к оплате
            row['K_U_O'] = forceInt(record.value('amount'))

        #, 'N', 9), # Номер записи в таблице реестра пациента
        row['N_REC'] = 0
        #, 'N', 9), # Номер записи в базе данных ЛПУ
        row['RECID'] = forceInt(record.value('serviceId'))
        #, 'C', 9), # Код специальности медицинского работника
        row['PRVS'] = forceString(record.value('specialityCode'))
        #, 'N',  9), # Номер истории создания записи
        row['D_H'] = 0
        # 'N', 9) # Количество посещений
        row['VISIT'] = forceInt(record.value('amount'))
        row.store()
        return

# *****************************************************************************************

    kladrNameCache = {}

    def getKLADRName(self, code):
        u""" Возвращает название из КЛАДР по коду."""
        result = ''

        if code != '':
            result = self.kladrNameCache.get(code)

            if not result:
                result = forceString(QtGui.qApp.db.translate('kladr.KLADR','CODE',
                    code.ljust(13, '0'),'NAME'))
                self.kladrNameCache[code] = result

        return result

# *****************************************************************************************

    def processServices(self,  txtStream,  record):
        if self.parent.page1.chkSkipZeroSum.isChecked() and forceDouble(record.value('sum')) == 0:
            return

        if record.isNull('orgStructureId'):
            self.saveSummary(record, 'total')
            # из-за rollup
            return

        if record.isNull('serviceCode') and not record.isNull('isMES1'):
            return


        format = u'%6.6s│%60.60s│%19.19s│%16.16s│%6.6s│%11.11s\n'
        orgStructureId = forceRef(record.value('orgStructureId'))

        if self.currentOrgStructureId != orgStructureId:
            if self.currentOrgStructureId:
                self.writeOrgStructureFooter(txtStream)

            orgStructureName = forceString(record.value('orgStructureName'))
            self.writeOrgStructureHeader(txtStream, orgStructureName)
            self.currentOrgStructureId =orgStructureId
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

        self.appendixStream << format % (
                forceString(record.value('serviceCode')),
                forceString(record.value('serviceName')).ljust(60),
                    (u'%11.2f' % (price-federalPrice)),
                    (u'%11.2f' % federalPrice),
                    (u'%6d' % mesCount if isMES else amount),
                    (u'%11.2f' % sum)
                )

        self.lines += 1


    def saveSummary(self, record, name,  isMES=False):
        u"""Cохраняет статистику по подразедению с именем name."""

        if isMES and self.orgStuctStat.has_key(name):
            (amount,  sum, clientCount, ambClientCount, hospClientCount,
            bedDays, mesBedDays, ambSum, hospSum,  uet, dayHospSum, mesCount,
            federalSum, dayHospClientCount,  mesSum,  mesFederalSum,
            hospFederalSum, dayHospFederalSum,  isMES) = self.orgStuctStat[name]
            amount+= forceInt(record.value('serviceCount'))
            sum+= forceDouble(record.value('sum'))
#            clientCount += forceInt(record.value('clientCount'))
#            ambClientCount+= forceInt(record.value('ambClientCount'))
#            hospClientCount+= forceInt(record.value('hospClientCount'))
            bedDays += forceInt(record.value('bedDays'))
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

            self.orgStuctStat[name] = (amount,  sum, clientCount,
                ambClientCount, hospClientCount, bedDays, mesBedDays,
                ambSum, hospSum,  uet, dayHospSum, mesCount,
                federalSum, dayHospClientCount, mesSum, mesFederalSum,
                hospFederalSum, dayHospFederalSum, isMES)
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
                isMES
                )


    def writeTextHeader(self,  txtStream):
        self.currentOrgStructureId = None
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
""" % (orgName, self.accDate.toString('dd/MM/yyyy'), self.accDate.toString(u'MMMM yyyy').toLower(),
       contractNumber, contractResolution, contractDate)

        txtStream << header


    def writeTextFooter(self,  txtStream):
        self.writeOrgStructureFooter(txtStream)
        delimeter = u'+-------------------+------+------+------+------+------+----------+-----------+-----+------+----------+-----------+------+-----------+\n'
        format = u'|%19.19s|%6d|%6d|%6d|%6d|%6d|%10.2f|%11.2f|%5.2f|%6d|%10.2f|%11.2f|%6d|%11.2f|\n'
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
                    mesFederalSum, hospFederalSum, dayHospFederalSum,  isMES) = val
                if sum != 0:
                    self.appendixStream << format % (key.ljust(19), clientCount,
                        ambClientCount, hospClientCount, dayHospClientCount, amount,
                        ambSum-federalSum,  federalSum,  uet, mesCount if isMES else 0,
                        (mesSum-mesFederalSum) if isMES else (dayHospSum+hospSum-hospFederalSum-dayHospFederalSum),
                        mesFederalSum if isMES else (hospFederalSum+dayHospFederalSum), mesBedDays if isMES else bedDays, sum)
                    self.appendixStream << delimeter
            else:
                (totalAmount, totalSum, totalClientCount, totalAmbClientCount,
                    totalHospClientCount, totalBedDays, totalMesBedDays, totalAmbSum, totalHospSum,  totalUet,
                    totalDayHospSum, totalMESServiceCount, totalFedSum, totalDayHospClientCount,
                    totalMESSum,  totalMesFedSum,  totalHospFederalSum, totalDayHospFederalSum,  isMES) =val
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
Выполнено услуг                  %7d на сумму %11.2f
Выполнено услуг по МЭС	         %7d на сумму %11.2f
Выполнено к/д 		         %7d на сумму %11.2f
+-------------------+---------------------------+-----------------------------------+-----------------------------+------------------+
|Наименование       | Пролечено пациентов       | Выполнено услуг                   |  Реализовано МЭС, к/д       |      |Всего      |
|отделения,         |                           |                                   |   по учету к/д              |      |cтоимость  |
|МЭС                +------+------+------+------+------+----------------------+-----+------+-----------+----------+      |           |
|                   |Всего | Амб. | Стац.| Дн.  |Кол-во| Стоимость            | УЕТ |Кол-во| Стоимость            |Кол-во|           |
|                   |      |      |      |      |      +----------------------+     | МЭС  |----------------------+ к/д  |           |
|                   |      |      |      | Стац.|      | Тариф    | Тариф доп.|     |      | Тариф    | Тариф доп.|      |           |
|                   |      |      |      |      |      |(территори|(федера    |     |      |(территори|(федера    |      |           |
|                   |      |      |      |      |      | альный)  | льный)    |     |      | альный)  | льный)    |      |           |
+-------------------+------+------+------+------+------+----------+-----------+-----+------+----------+-----------+------+-----------+
""" % (orgName, self.accDate.toString(u'MMMM yyyy').toLower(),
        totalClientCount,  totalSum+totalMESSum,
        totalAmbClientCount,  totalAmbSum,
        totalHospClientCount, totalHospSum,
        totalDayHospClientCount, totalDayHospSum,
        totalAmount,  totalAmbSum,
        totalMESServiceCount,  totalMESSum,
        totalBedDays,  totalHospSum)

        txtStream << self.appendixStr
        txtStream << format % (u'Итого'.ljust(19), totalClientCount,
                totalAmbClientCount, totalHospClientCount, totalDayHospClientCount,  totalAmount,
                totalTerSum, totalFedSum,  totalUet, totalMESServiceCount,
                totalHospTerSum+totalDayHospTerSum+totalMesTerSum,
                totalHospFederalSum+totalDayHospFederalSum+totalMesFedSum, totalBedDays+totalMesBedDays, totalSum+totalMESSum)
        txtStream << delimeter
        txtStream << u"""
ВСЕГО ПРЕДСТАВЛЕНО К ОПЛАТЕ: %11.2f
      (%s)

По территориальному тарифу на сумму %11.2f (%s)
По дополнительному тарифу на сумму %11.2f (%s)

Руководитель мед.учреждения ____________________ %s

Гл.бухгалтер мед.учреждения ____________________ %s
""" % (totalSum+totalMESSum, amountToWords(totalSum+totalMESSum),
         totalTerSum+totalHospTerSum+totalDayHospTerSum+totalMesTerSum, amountToWords(totalTerSum+totalHospTerSum+totalDayHospTerSum+totalMesTerSum),
         totalFedSum+totalHospFederalSum+totalDayHospFederalSum+totalMesFedSum, amountToWords(totalFedSum+totalHospFederalSum+totalDayHospFederalSum+totalMesFedSum),
         orgChief, orgAccountant)
        self.writeNewPage(txtStream)

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
            mesFederalSum, hospFederalSum, dayHospFederalSum,  isMES) = \
        self.orgStuctStat.get(self.currentOrgStructureName, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False))

        footer = \
u"""Количество пролеченных пациентов %7d на сумму %11.2f
             из них амбулаторных %7d на сумму %11.2f
                    стационарных %7d на сумму %11.2f
             дневного стационара %7d на сумму %11.2f
Выполненно услуг                 %7d на сумму %11.2f
Выполненно услуг по МЭС          %7d на сумму %11.2f
Выполненно к/д                   %7d на сумму %11.2f
""" % (clientCount, sum+mesSum,
        ambClientCount,  ambSum,
        hospClientCount,  hospSum,
        dayHospClientCount, dayHospSum,
        amount, ambSum,
        mesCount, mesSum,
        bedDays, hospSum+dayHospSum)

        txtStream<<footer
        self.writeTableHeader(txtStream)
        txtStream<<self.appendixStr
        self.appendixStr.clear()

        footer = \
u"""──────┼────────────────────────────────────────────────────────────┼───────────────────┼────────────────┼──────┼───────────
Итого │                                                            │                   │                │      │%11.2f
"""
        txtStream << footer % (sum+mesSum)
        self.writeTableFooter(txtStream)
        self.writeNewPage(txtStream)



    def writeTableHeader(self, txtStream):
        header = \
u"""──────┬────────────────────────────────────────────────────────────┬────────────────────────────────────┬──────┬───────────
 Код  │                        Наименование                        │ Стоимость 1-й услуги (МЭС,К/Д,П/П) │Кол-во│ Всего
услуги│                                                            ├───────────────────┬────────────────┤      │стоимость
(МЭС) │                                                            │     Тариф         │     Тариф      │      │
(К/Д) │                                                            │ (территориальный) │ дополнительный │      │
(П/П) │                                                            │                   │  (федеральный) │      │
──────┼────────────────────────────────────────────────────────────┼───────────────────┼────────────────┼──────┼───────────
"""
        txtStream << header


    def writeTableLiteHeader(self, txtStream):
        header = \
u"""──────┬────────────────────────────────────────────────────────────┬───┬───────────┬──────┬────────┬──────┬────┬───────────
  1   │                             2                              │ 3 │     4     │  5   │   6    │  7   │ 8  │     9
──────┼────────────────────────────────────────────────────────────┼───┼───────────┼──────┼────────┼──────┼────┼───────────
"""
        txtStream << header

    def writeTableFooter(self, txtStream):
        footer = u'──────┴────────────────────────────────────────────────────────────┴───────────────────┴────────────────┴──────┴───────────\n'
        txtStream << footer


    def writeNewPage(self, txtStream):
        txtStream << u'\n\x0C\n'
        self.lines = 0

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


class CExportPage2(QtGui.QWizardPage, Ui_ExportPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R67ExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        baseName = self.parent.page1.getDbfBaseName()
        prefixes = ('I', 'C') if self.parent.page1.chkExportFormatAliens.isChecked() else ('P', 'S')
        for src in prefixes:
            srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                    os.path.basename(src+baseName))
            dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                    os.path.basename(src+baseName))
            success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

            if not success:
                break

        srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                self.parent.page1.getTxtFileName())
        dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                self.parent.page1.getTxtFileName())
        success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))


        if success:
            QtGui.qApp.preferences.appPrefs['R67ExportDir'] = toVariant(self.edtDir.text())
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
                u'Выберите директорию для сохранения файла выгрузки в ОМС Смоленской области',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
