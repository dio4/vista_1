# -*- coding: utf-8 -*-

import os.path
import shutil
from PyQt4 import QtCore, QtGui
from decimal import *
from zipfile import ZIP_DEFLATED, ZipFile

from Accounting.ServiceDetailCache import CServiceDetailCache
from Accounting.Utils import updateAccountInfo
from Events.Action import ActionStatus
from Exchange.ExportHL7 import getPersonFireDate, getPersonHireDate
from Exchange.ExportR23Native import getWeightIfAborted
from Exchange.Utils import CExportHelperMixin, isExternalOrgCode, getPersonIdList, getAdditionalPersonIdList
from Reports.AccountInvoice import CAccountInvoice
from library.AmountToWords import amountToWords
from library.Utils import calcAgeInDays, calcAgeInYears, calcAgeTuple, forceBool, forceDate, forceDecimal, forceDouble, \
    forceInt, forceRef, forceString, \
    forceStringEx, formatSNILS, formatSex, getVal, monthName, nameCase, pyDate, toVariant
from library.crbcombobox import CRBComboBox
from library.dbfpy.dbf import Dbf

getcontext().prec = 12
from Reports.ReportBase import createTable, CReportBase

from ..Ui_ExportR23NativePage1 import Ui_ExportR23NativePage1
from ..Ui_ExportR23NativePage2 import Ui_ExportR23NativePage2


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number, settleDate, contract_id', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        settleDate = forceDate(accountRecord.value('settleDate'))
        number = forceString(accountRecord.value('number'))
        contractId = forceRef(accountRecord.value('contract_id'))
    else:
        date = settleDate = contractId = None
        number = ''
    return date, number, settleDate, contractId


def exportR23DKKB(widget, accountId, accountItemIdList):
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
        self.page2.fileNameList.append('R')

        self.setWindowTitle(u'Мастер экспорта в ОМС Краснодарского края')
        self.dbfFileName = ''
        self.tmpDir = ''
        self.contractId = None
        self.hasLFile = False

    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, settleDate, contractId = getAccountInfo(accountId)
        self.contractId = contractId
        strNumber = (number if forceStringEx(number) else u'б/н')
        self.accountNumber = number
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.edtDatps.setDate(settleDate if settleDate and settleDate.isValid() else QtCore.QDate.currentDate())
        self.page1.edtDats.setDate(settleDate if settleDate and settleDate.isValid() else QtCore.QDate.currentDate())
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменных файлов "*.dbf"')

    def setAccountExposeDate(self):
        #db = QtGui.qApp.db
        #accountRecord = db.table('Account').newRecord(['id', 'exposeDate', 'number'])
        #accountRecord.setValue('id', toVariant(self.accountId))
        #accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        #accountRecord.setValue('number', toVariant(self.page1.edtRegistryNumber.value()))
        #db.updateRecord('Account', accountRecord)
        pass

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R23NATIVE')
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


class CBaseExportPage1(QtGui.QWizardPage, Ui_ExportR23NativePage1, CExportHelperMixin):
    mapVpName = {
        0: u'Стационар',
        1: u'Поликлиника',
        1.1: u'Поликлиника (прикрепленное население)',
        2: u'Стоматология',
        3: u'Дневной стационар',
        4: u'Стационар дневного пребывания',
        5: u'Женская консультация',
        6: u'Стационар на дому',
        7: u'Центр здоровья',
        8: u'Приемное отделение',
        9: u'Диагностические исследования',
        10: u'Фельдшерско-акушерский пункт',
        11: u'Скорая медицинская помощь',
        12: u'Диспансеризация детей-сирот',
        13: u'Диспансеризация детей, оставшихся без попечения родителей',
        14: u'Диспансеризация взрослого населения',
        15: u'Неотложная помощь',
        16: u'Медицинские осмотры взрослых',
        17: u'Медицинские осморы несовершеннолетних',
        18: u'Высокотехнологичная медицинская помощь'
    }
    mapPayMethod = {0:'1', 1:'2', 2:'3'}

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        CExportHelperMixin.__init__(self)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')
        self.cmbAccountType.setTable('rbAccountType', addNone=False)
        self.cmbAccountType.setShowFields(CRBComboBox.showCodeAndName)
        self.cmbAccountType.setCurrentIndex(0)

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.tariffCache = {}
        self.parent = parent
        self.ignoreErrors = forceBool(QtGui.qApp.preferences.appPrefs.get('ExportR23NativeIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(QtGui.qApp.preferences.appPrefs.get('ExportR23NativeVerboseLog', 'False')))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.exportedTempInvalidList = []
        self.tempInvalidCache = {}
        self.exportedClients = set()
        self.modernClients = set()
        self.medicalAidProfileCache = {}
        self.exportedDirections = []
        self.profileCache = {}
        self.kindCache = {}
        self.typeCache = {}
        self.serviceDetailCache = CServiceDetailCache()
        # payMethod не используется
        self.cmbPayMethod.setVisible(False)
        self.lblPayMethod.setVisible(False)
        self.personCache = {}

    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.cmbAccountType.setEnabled(not flag)
        self.cmbPayMethod.setEnabled(not flag)
        self.edtRegistryNumber.setEnabled(not flag)
        self.chkUpdateAccountNumber.setEnabled(not flag)

    def log(self, str, forceLog=False):
        if self.chkVerboseLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()

    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList

    def prepareToExport(self):
        pass

    def export(self):
        try:
            forceInt(self.edtOrgStructureCode.text())
        except ValueError:
            QtGui.QMessageBox.critical(self, u'Ошибка', u'Необходимо указать числовой код подразделения.', buttons = QtGui.QMessageBox.Ok)
            self.edtOrgStructureCode.setFocus(QtCore.Qt.OtherFocusReason)
            return
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))

    def getDbfBaseName(self, modern):
        lpuId = forceRef(QtGui.qApp.db.translate('Account', 'id', self.parent.accountId, 'orgStructure_id'))
        if not lpuId: lpuId = QtGui.qApp.currentOrgStructureId()
        lpuCode = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', lpuId , 'bookkeeperCode'))
        postfix= 'M' if modern else ''
        return u'%s%s.DBF' % (lpuCode, postfix)

    def getZipFileName(self, modern=False):
        lpuId = forceRef(QtGui.qApp.db.translate('Account', 'id', self.parent.accountId, 'orgStructure_id'))
        if not lpuId:
            lpuId = QtGui.qApp.currentOrgStructureId()
        lpuCode = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', lpuId , 'bookkeeperCode'))
        postfix= u'M' if modern else u''
        payerCode = self.getPayerCode()
        if self.chkPreliminaryInvoice.isChecked():
            return u'a%s%s%03d%s.zip' % (payerCode, lpuCode, self.edtRegistryNumber.value(), postfix)
        else:
            return u'%s%s%03d%s.zip' % (payerCode, lpuCode, self.edtRegistryNumber.value(), postfix)

    def getPayerCode(self):
        payerId = forceRef(QtGui.qApp.db.translate('Account', 'id', self.parent.accountId, 'payer_id'))
        payerCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', payerId, 'infisCode')) if payerId else u'000'
        accNumber = self.parent.accountNumber
        if len(accNumber) > 1 and accNumber[-2:].lower() == u'/п':
            accNumber = accNumber[:-2]
        accSplit = accNumber.split(u'/')
        if (len(accSplit) > 1):
            payerCode2 = forceString(QtGui.qApp.db.translate(u'Organisation', u'infisCode', forceInt(accSplit[-1]), u'infisCode'))
            if payerCode2 != '':
                payerCode = payerCode2
        return payerCode

    def createDbf(self):
        return (
            self.createPDbf(False),
            self.createUDbf(False),
            self.createDDbf(False),
            self.createNDbf(False),
            self.createRDbf(False),
        )

    def createPDbf(self, modern):
        u"""Создает структуру для паспортной части реестра счетов."""

        dbfName = os.path.join(self.parent.getTmpDir(), 'P' + self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NS', 'N', 5, 0),  # номер реестра счетов (п. 1; 4 примечаний) обязательное
            ('VS', 'C', 1),  # тип реестра счетов (п. 2; 4 примечаний) обязательное SPR21
            ('DATS', 'D'),  # дата формирования реестра счетов (п. 3; 4 примечаний) обязательное
            ('SN', 'N', 12, 0),  # номер персонального счета (п. 13 примечаний) обязательное
            ('DATPS', 'D'),  # Дата формирования персонального счета (п. 13 примечаний) обязательное
            ('CODE_MO', 'C', 5),  # код МО, оказавшей медицинскую помощь обязательное SPR01
            ('PL_OGRN', 'C', 15),  # ОГРН плательщика (п. 4 примечаний) обязательное SPR02
            ('FIO', 'C', 30),  # фамилия (п. 5 примечаний) обязательное
            ('IMA', 'C', 20),  # имя (п. 5 примечаний) обязательное
            ('OTCH', 'C', 30),  # отчество (п. 5 примечаний)
            ('POL', 'C', 1),  # пол (М/Ж) (п. 6 примечаний) обязательное
            ('DATR', 'D'),  # дата рождения (п. 7 примечаний) обязательное
            ('KAT', 'C', 1),  # категория граждан обязательное SPR09
            ('SNILS', 'C', 14),  # СНИЛС
            ('OKATO_OMS', 'C', 5),  # код ОКАТО территории страхования по ОМС обязательное для инокраевых SPR39
            ('SPV', 'N', 1),  # тип ДПФС (п. 11 примечаний) обязательное
            ('SPS', 'C', 10),  # серия ДПФС обязательное (для документов ОМС, имеющих серию)
            ('SPN', 'C', 20),  # номер ДПФС (п. 12 примечаний) обязательное
            ('INV', 'C', 1),  # группа инвалидности: заполняется из обращения (таблица...поле....) (ADDED i3393)
            ('P_PER', 'C', 1),  # признак поступления/перевода (ADDED i3393)
            # ('STAT_P', 'C', 1),     # статус представителя пациента  обязательное для инокраевых SPR41 (DROPED i3393)
            ('Q_G', 'C', 10),
            # признак "Особый случай" при регистрации  обращения за медицинской помощью (п. 8 примечаний)
            # обязательное (в случае наличия особого случая или для диспансеризации и профосмотров предполагающих этапность) SPR42
            ('NOVOR', 'C', 9),
            # признак новорожденного (п. 14 примечаний) обязательное (в случае оказания МП ребенку до государственной регистрации)
            ('VNOV_D', 'N', 10, 2),  # вес при рождении (п.16 примечаний)
            ('FAMP', 'C', 30),  # фамилия представителя пациента (п. 5 примечаний) обязательное (при STAT_P <> “0”)
            ('IMP', 'C', 20),  # имя представителя пациента (п. 5 примечаний) обязательное (при STAT_P <> “0”)
            ('OTP', 'C', 30),  # отчество представителя пациента (п. 5 примечаний) обязательное (при STAT_P <> “0”)
            ('POLP', 'C', 1),  # пол представителя пациента (М/Ж) (п. 6 примечаний) обязательное (при STAT_P <> “0”)
            ('DATRP', 'D'),
            # дата рождения представителя пациента (п. 7 примечаний) обязательное (для инокраевых, при STAT_P <> “0”)
            ('C_DOC', 'N', 2, 0),
            # код типа УДЛ (п. 9 примечаний) обязательное для инокраевых). При указании ЕНП может не заполняться. SPR43
            ('S_DOC', 'C', 10),
            # серия УДЛ (п. 9 примечаний) обязательное для инокраевых). При указании ЕНП может не заполняться.
            ('N_DOC', 'C', 15),
            # номер УДЛ (п. 9 примечаний) обязательное для инокраевых). При указании ЕНП может не заполняться.
            ('NAPR_MO', 'C', 5),  # код направившей МО обязательное (по направлениям и для телемедицины) SPR01
            ('NAPR_N', 'C', 15),
            # номер направления (п.15 примечаний) обязательное (по направлениям на плановую госпититализацию)
            ('NAPR_D', 'D'),  # дата выдачи направления на плановую госпитализацию (ADDED i3393)
            ('NAPR_DP', 'D'),  # дата планируемой госпитализации (ADDED i3393)
            ('TAL_N', 'C', 18),  # Для ВМП: номер талона на ВМП (п.22 примечаний) (ADDED i4432)
            ('TAL_D', 'D'),  # Для ВМП: дата выдачи талона на ВМП (п.22 примечаний) (ADDED i4432)
            ('PR_D_N', 'C', 1),  # признак диспансерного наблюдения, допустимые значения: 0-нет, 1-да; (ADDED i3716)
            # ('NAZR', 'C', 8),       # назначения по результатам проведенной диспансеризации/ профилактических медицинских осмотров (ADDED i3716) (DROPED i4432)
            # ('NAZ_V', 'C', 4),      # вид назначенного обследования по результатам диспансеризации/ профилактических медицинских осмотров (обязательно для заполнения для случаев, если NAZR содержит 3) (ADDED i3716) (DROPPED i4432)
            ('ISTI', 'C', 10),  # номер амбулаторной карты или истории болезни обязательное
            ('DATN', 'D'),  # дата начала лечения обязательное
            ('DATO', 'D'),  # дата окончания лечения обязательное
            ('ISHL', 'C', 3),  # код исхода заболевания обязательное SPR11
            ('ISHOB', 'C', 3),  # код исхода обращения обязательное SPR12
            ('MP', 'C', 1),  # код формы обращения обязательное SPR14
            # ('SUMMA_I', 'N', 14,2), # сумма к оплате по ОМС по случаю заболевания пациента обязательное (DROPED i4432)
            # ('DOC_TABN', 'C', 10),  # табельный номер врача закрывшего талон/историю (п. 17 примечаний) обязательное (DROPED i4432)
            ('DOC_SS', 'C', 14),  # СНИЛС врача закрывшего талон/историю (п. 17 примечаний) (ADDED i4432)
            ('SPEC', 'C', 9),  # код специальности врача закрывшего талон/историю (ADDED i4432)
            ('PROFIL', 'C', 3),  # профиль оказанной медицинской помощи (ADDED i4432)
            ('VMP', 'C', 2),  # вид медицинской помощи (ADDED i4432)
            ('KSO', 'C', 2),  # способ оплаты медицинской помощи (ADDED i4432)
            ('P_CEL', 'C', 1),  # цель посещения (п.21 примечаний) (ADDED i4432)
            ('MKBX', 'C', 6),  # код диагноза основного заболевания по МКБ–Х (ADDED i4432)
            ('PV', 'C', 40),  # коды причин возврата (п. 10 примечаний) обязательное для возвратных счетов SPR15
            ('DVOZVRAT', 'D'),  # дата возврата обязательное для возвратных счетов
            ('COMMENT', 'C', 20)  # (ADDED i3716)
        )
        return dbf

    def createUDbf(self, modern):
        u"""Создает структуру dbf для медицинских услуг."""

        dbfName = os.path.join(self.parent.getTmpDir(), 'U' + self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('UID', 'N', 14),
            # уникальный номер записи об оказанной медицинской услуге в пределах реестра (п. 1 примечаний) обязательное
            ('CODE_MO', 'C', 5),  # код МО, оказавшей медицинскую помощь обязательное SPR01
            ('NS', 'N', 5, 0),  # номер реестра счетов обязательное
            ('SN', 'N', 12, 0),  # номер персонального счета обязательное
            ('KOTD', 'C', 4),  # код отделения (п. 2, 6 примечаний) обязательное SPR07
            ('KPK', 'C', 2),  # код профиля койки (п. 2 примечаний) обязательное (для стационаров всех типов) SPR08
            ('MKBX', 'C', 6),
            # код диагноза основного заболевания по МКБ–Х (п. 2 примечаний) обязательное (кроме диагностических услуг) SPR20
            ('MKBX_PR', 'C', 1),
            # признак впервые установленного диагноза основного заболевания(для счетов по диспансеризации/профилактическим медицинским осмотрам) (ADDED i3716)
            ('MKBXS', 'C', 6),  # код диагноза сопутствующего заболевания по МКБ–Х (п. 2 примечаний) SPR20
            ('MKBXS_PR', 'C', 1),
            # признак впервые установленного диагноза сопутствующего заболевания (для счетов по диспансеризации/профилактическим медицинским осмотрам) (ADDED i3716)
            ('MKBXO', 'C', 6),  # код диагноза осложнения заболевания по МКБ–Х (п. 2 примечаний) SPR20
            # ('KSTAND', 'C', 15),   # резервное поле (REMOVED i3716)
            ('VP', 'C', 3),  # код условия оказания медицинской помощи (п.2 примечаний) обязательное SPR13
            ('KUSL', 'C', 15),  # код медицинской услуги обязательное SPR18
            ('KOLU', 'N', 3, 0),  # количество услуг обязательное
            ('KD', 'N', 3, 0),  # количество койко-дней (дней лечения) обязательное (для стационаров всех типов)
            ('DATN', 'D'),  # дата начала выполнения услуги обязательное
            ('DATO', 'D'),  # дата окончания выполнения услуги обязательное
            ('TARU', 'N', 10, 2),  # тариф на оплату по ОМС (п.5 примечаний)	обязательное	SPR22
            ('SUMM', 'N', 14, 2),  # сумма к оплате по ОМС (п.5 примечаний)	обязательное
            ('IS_OUT', 'N', 1, 0),  # признак: услуга оказана в другой МО (п. 3 примечаний) обязательное
            ('OUT_MO', 'C', 5),  # код МО, оказавшей услугу (п.4 примечаний) SPR01
            # Обязательные (для услуг с тарифом ОМС больше 0, а также для посещений врача стоматолога,  ФАПов и ССМП, услуг обращение):
            # ('DOC_TABN', 'C', 10), # табельный номер сотрудника, оказавшего услугу (п. 7 примечаний) (DROPED i4432)
            ('DOC_SS', 'C', 14),  # СНИЛС врача закрывшего талон/историю (п. 17 примечаний) (ADDED i4432)
            ('SPEC', 'C', 9),  # код специальности специалиста, оказавшего услугу SPR46
            ('PROFIL', 'C', 3),  # профиль оказанной медицинской помощи SPR60
            ('VMP', 'C', 2),  # вид медицинской помощи SPR59
            # ('KSO', 'C', 2),       # способ оплаты медицинской помощи SPR17 (DROPED i4432)
            ('COMMENT', 'C', 20)  # (ADDED i3716)
        )
        return dbf

    def createNDbf(self, modern):
        u"""Создает структуру dbf для направлений."""

        dbfName = os.path.join(self.parent.getTmpDir(), 'N' + self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_MO', 'C', 5),  # код МО, оказавшей медицинскую помощь и выдавшей направление обязательное SPR01
            ('NAPR_N', 'C', 15),  # номер направления, (ККККК_ХХХХХХХ) обязательное
            ('NAPR_MO', 'C', 5),  # код МО, в которое направлен пациент обязательное SPR01
            ('NAPR_D', 'D'),  # дата направления обязательное
            # ('DOC_TABN', 'C', 10), # табельный номер сотрудника, выдавшего направление обязательное (DROPED i4432)
            ('DOC_SS', 'C', 14),  # табельный номер сотрудника, выдавшего направление обязательное (ADDED i4432)
        )
        return dbf

    def createDDbf(self, modern):
        u"""Специалисты структурного подразделения"""
        dbfName = os.path.join(self.parent.getTmpDir(), 'D' + self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_MO', 'C', 5),  # код МО, оказавшей медицинскую помощь обязательное SPR01
            # ('DOC_TABN', 'C', 10), # табельный номер обязательное (DROPED i4432)
            ('SNILS', 'C', 14),  # СНИЛС (ХХХ-ХХХ-ХХХ ХХ) обязательное
            ('FIO', 'C', 30),  # фамилия медицинского работника обязательное
            ('IMA', 'C', 20),  # имя медицинского работника обязательное
            ('OTCH', 'C', 30),  # отчество медицинского работника
            ('POL', 'C', 1),  # пол (М/Ж) обязательное
            ('DATR', 'D'),  # дата рождения обязательное
            ('DATN', 'D'),  # дата устройства на работу
            ('DATO', 'D'),  # дата увольнения
        )
        return dbf

    def createRDbf(self, modern):
        u"""Назначения лечащего врача, по результатам проведенных профилактических мероприятий"""
        dbfName = os.path.join(self.parent.getTmpDir(), 'R' + self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('RID', 'N', 14),  # уникальный номер записи о назначении в пределах реестра (п. 1 примечаний)
            ('CODE_MO', 'C', 5),  # код МО, оказавшей медицинскую помощь обязательное SPR01
            ('NS', 'N', 5),  # номер реестра счетов
            ('SN', 'N', 12),  # номер персонального счета
            ('NAZR', 'C', 2),  # вид назначения (п.2 примечаний)
            ('SPEC', 'C', 9),  # специальность врача, к которому направлен за консультацией
            ('VID_OBS', 'C', 2),  # вид назначенного обследования (п.3 примечаний)
            ('PROFIL', 'C', 3),  # профиль назначенной медицинской помощи
            ('KPK', 'C', 3),  # код профиля койки
        )
        return dbf

    def getPersonInfoById(self, personId):
        if personId not in self.personCache:
            db = QtGui.qApp.db
            Person = db.table('Person')
            Post = db.table('rbPost')
            OrgStructure = db.table('OrgStructure')
            Speciality = db.table('rbSpeciality')

            queryTable = Person.leftJoin(OrgStructure, OrgStructure['id'].eq(Person['orgStructure_id']))
            queryTable = queryTable.leftJoin(Speciality, Speciality['id'].eq(Person['speciality_id']))
            queryTable = queryTable.leftJoin(Post, Post['id'].eq(Person['post_id']))

            cols = [
                Person['id'].alias('personId'),
                Person['SNILS'].alias('SNILS'),
                Person['lastName'].alias('lastName'),
                Person['firstName'].alias('firstName'),
                Person['patrName'].alias('patrName'),
                Person['sex'].alias('sex'),
                Person['birthDate'].alias('birthDate'),
                Person['regionalCode'].alias('tabNum'),
                OrgStructure['infisCode'].alias('orgStructCode'),
                Post['regionalCode'].alias('postCode'),
                Speciality['regionalCode'].alias('specialityCode'),
                Speciality['federalCode'].alias('federalCode')
            ]

            cond = [
                Person['deleted'].eq(0),
                Person['id'].eq(personId)
            ]
            self.personCache[personId] = db.getRecordEx(queryTable, cols, cond)
        return self.personCache[personId]

    def createPersonQuery(self):
        db = QtGui.qApp.db
        Person = db.table('Person')
        Post = db.table('rbPost')
        OrgStructure = db.table('OrgStructure')
        Speciality = db.table('rbSpeciality')

        queryTable = Person.leftJoin(OrgStructure, OrgStructure['id'].eq(Person['orgStructure_id']))
        queryTable = queryTable.leftJoin(Speciality, Speciality['id'].eq(Person['speciality_id']))
        queryTable = queryTable.leftJoin(Post, Post['id'].eq(Person['post_id']))

        cols = [
            Person['id'].alias('personId'),
            Person['SNILS'].alias('SNILS'),
            Person['lastName'].alias('lastName'),
            Person['firstName'].alias('firstName'),
            Person['patrName'].alias('patrName'),
            Person['sex'].alias('sex'),
            Person['birthDate'].alias('birthDate'),
            Person['regionalCode'].alias('tabNum'),  # Person['code'].alias('tabNum') i3393
            OrgStructure['infisCode'].alias('orgStructCode'),
            Post['regionalCode'].alias('postCode'),
            Speciality['regionalCode'].alias('specialityCode')
        ]

        # orgStructId = QtGui.qApp.currentOrgStructureId()
        # idList = db.getDescendants('OrgStructure', 'parent_id', orgStructId)

        cond = [
            # Person['orgStructure_id'].inlist(idList) if orgStructId else Person['org_id'].eq(QtGui.qApp.currentOrgId()),
            Person['deleted'].eq(0),
            "LEFT(rbPost.code,1) IN ('1','2','3', '4')"
        ]

        group = [
            Person['lastName'],
            Person['firstName'],
            Person['patrName'],
            Person['birthDate']
        ]
        # i3393 D file
        if hasattr(self, 'personIdForFileD'):
            cond.append(Person['id'].inlist(self.personIdForFileD))

        stmt = db.selectStmt(queryTable, cols, cond, group, isDistinct=True)
        return db.query(stmt)

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

    def processPerson(self, dbf, record, bookkeeperCode):
        (dbfP, dbfU, dbfD, dbfN, dbfR) = dbf
        personId = forceRef(record.value('personId'))
        personCode = forceString(record.value('tabNum'))
        SNILS = forceString(record.value('SNILS'))

        row = dbfD.newRecord()
        row['CODE_MO'] = bookkeeperCode  # код МО, оказавшей медицинскую помощь обязательное SPR01
        # row['DOC_TABN'] = personCode                               # табельный номер обязательное (DROPED i4432)
        row['SNILS'] = formatSNILS(SNILS) if SNILS else ''  # СНИЛС (ХХХ-ХХХ-ХХХ ХХ) обязательное
        row['FIO'] = forceString(record.value('lastName'))  # фамилия медицинского работника обязательное
        row['IMA'] = forceString(record.value('firstName'))  # имя медицинского работника обязательное
        row['OTCH'] = forceString(record.value('patrName'))  # отчество медицинского работника
        row['POL'] = formatSex(record.value('sex')).upper()  # пол (М/Ж) обязательное
        row['DATR'] = pyDate(forceDate(record.value('birthDate')))  # дата рождения обязательное
        row['DATN'] = pyDate(getPersonHireDate(personId))  # дата устройства на работу
        row['DATO'] = pyDate(getPersonFireDate(personId))  # дата увольнения
        self.SNILS_fileD.append(SNILS)
        row.store()

    def getAidCodes(self, serviceDetail, date, specialityId, birthDate, sex, mkb):
        age = calcAgeTuple(birthDate, date)
        profileId, kindId, typeId = serviceDetail.getMedicalAidIds(specialityId, sex, age, mkb)
        if profileId:
            profileCode = self.profileCache.get(profileId, None)
            if profileCode is None:
                profileCode = forceInt(QtGui.qApp.db.translate('rbMedicalAidProfile', 'id', profileId, 'regionalCode'))
                self.profileCache[profileId] = profileCode
        else:
            profileCode = 0
        if kindId:
            kindCode = self.kindCache.get(kindId, None)
            if kindCode is None:
                kindCode = forceString(QtGui.qApp.db.translate('rbMedicalAidKind', 'id', kindId, 'federalCode'))
                self.kindCache[kindId] = kindCode
        else:
            kindCode = ''
        if typeId:
            typeCode = self.typeCache.get(typeId, None)
            if typeCode is None:
                typeCode = forceString(QtGui.qApp.db.translate('rbMedicalAidType', 'id', typeId, 'code'))
                self.typeCache[typeId] = typeCode
        else:
            typeCode = ''
        return profileCode, kindCode, typeCode

    def getClientTempInvalidList(self, clientId, begDate, endDate, personId):
        key = (clientId, begDate, endDate, personId)
        list = self.tempInvalidCache.get(key, [])

        if list == []:
            db = QtGui.qApp.db
            table = db.table('TempInvalid')
            stmt = """
                SELECT  tr.regionalCode AS reasonCode,
                            TempInvalid.begDate,
                            TempInvalid.endDate,
                            TempInvalid.serial,
                            TempInvalid.number,
                            TempInvalid.id,
                            Diagnosis.MKB
                FROM TempInvalid
                LEFT JOIN rbTempInvalidDocument td ON doctype_id = td.id
                LEFT JOIN rbTempInvalidReason tr ON tempInvalidReason_id = tr.id
                LEFT JOIN Diagnosis ON diagnosis_id = Diagnosis.id
                WHERE %s AND td.code = '1'
            """ % db.joinAnd([ table['client_id'].eq(clientId),
                table['deleted'].eq(0),
                table['closed'].eq(1),
                table['person_id'].eq(personId),
                db.joinOr([table['begDate'].isNull(), table['begDate'].ge(begDate)]),
                db.joinOr([table['endDate'].isNull(), table['endDate'].le(endDate)])])

            query = db.query(stmt)
            while query.next():
                record=query.record()
                list.append((forceDate(record.value('begDate')),
                    forceDate(record.value('endDate')),
                    forceString(record.value('serial')),
                    forceInt(record.value('number')),
                    forceRef(record.value('id')),
                    forceInt(record.value('reasonCode')),
                    forceString(record.value('MKB'))
                    ))

            self.tempInvalidCache[key] = list

        return list

    def getAccountUET(self, accNumber, kusl=None, enddate=None):
        db = QtGui.qApp.db
        tableAccount = db.table('Account')
        record = db.getRecordEx(tableAccount, tableAccount['uet'], [tableAccount['number'].eq(accNumber),
                                                                    tableAccount['deleted'].eq(0)])
        return forceDouble(record.value('uet')) if record else 0.0

    def getServiceCategory(self, accountItemId):
        db = QtGui.qApp.db
        AccountItem = db.table('Account_Item')
        Event = db.table('Event')
        EventType = db.table('EventType')
        Service = db.table('rbService')
        ServiceCategory = db.table('rbServiceCategory')
        Visit = db.table('Visit')

        table = AccountItem.leftJoin(Visit, Visit['id'].eq(AccountItem['visit_id']))
        table = table.leftJoin(Event, Event['id'].eq(AccountItem['event_id']))
        table = table.leftJoin(EventType, EventType['id'].eq(Event['eventType_id']))
        table = table.leftJoin(Service, Service['id'].eq(db.if_(AccountItem['service_id'].isNotNull(),
                                                                AccountItem['service_id'],
                                                                db.if_(AccountItem['visit_id'].isNotNull(),
                                                                       Visit['service_id'],
                                                                       EventType['service_id']))))
        table = table.leftJoin(ServiceCategory, ServiceCategory['id'].eq(Service['category_id']))

        record = QtGui.qApp.db.getRecordEx(table, ServiceCategory['code'], AccountItem['id'].eq(accountItemId))
        return forceString(record.value('code')) if record else ''

    def isArea(self, infisCode):
        db = QtGui.qApp.db
        return forceBool(db.translate('OrgStructure', 'infisCode', infisCode, 'isArea'))

    def getInvoiceData(self,accNumber):
        def getKSO():
            result = {}
            for x in dbf_p:
                result[x['SN']] = x['KSO']
            return result

        dbfNameP = os.path.join(self.parent.getTmpDir(), 'P' + self.getDbfBaseName(False))
        dbfNameU = os.path.join(self.parent.getTmpDir(), 'U' + self.getDbfBaseName(False))
        dbf_p = Dbf(dbfNameP, True, encoding='cp866')
        dbf_u = Dbf(dbfNameU, True, encoding='cp866')

        mapVpToRow = {'11': 0, '12': 0,
                      '21': 1, '22': 1, '271': 1, '272': 1,
                      '31': 2, '32': 2,
                      '41': 3, '42': 3, '43': 3, '90': 3,
                      '51': 4, '52': 4,
                      '60': 5,
                      '71': 6, '72': 6,
                      '01': 7, '02': 7,
                      '111': 8, '112': 8,
                      '201': 10, '202': 10,
                      '801': 11, '802': 11,
                      '232': 12,
                      '252': 13,
                      '211': 14,
                      '241': 15, '242': 15,
                      '261': 16,
                      '262': 17,
                      '401': 18, '402': 18,
        }
        ksoDict = getKSO()
        self.progressBar.reset()
        self.progressBar.setMaximum(max(len(dbf_u), 1))
        self.progressBar.setValue(0)

        result = {}
        result['accountUET'] = self.getAccountUET(accNumber)

        result.setdefault(1.1, {'tsumm': 0.0, 'eventSet': set(), 'uet': 0.0, 'visits': 0, 'tkd': 0})

        ServiceCategory_EventByIllness = '1'  # обращение по поводу заболевания

        pogrn = dict()
        pinfis = ''
        # Грузим признаки работающих и неработающих в словарь, чтоб быстрее работало
        for rec_p in dbf_p:
            pogrn[rec_p['PL_OGRN']]=1

        for rec_u in dbf_u:
            self.progressBar.step()
            accountItemId = rec_u['UID']
            eventId = rec_u['SN']
            eventProfile = rec_u['VP']
            service = rec_u['KUSL']
            spec = rec_u['SPEC']
            vmp = rec_u['VMP']
            kotd = rec_u['KOTD']
            if eventId in ksoDict.keys():
                kso = ksoDict[eventId]
            else:
                kso = '0'
            # serviceCategory = self.getServiceCategory(accountItemId)

            currRow = mapVpToRow.get(eventProfile, None)
            if currRow is None:
                continue

            if service == 'B01.047.018':
                currVpData = result.setdefault(15, {'tsumm':0.0, 'eventSet':set(), 'uet':0.0, 'visits':0, 'tkd': 0})
                currVpData['tsumm'] += rec_u['SUMM']
                currVpData['visits'] += 1
                continue

            currVpData = result.setdefault(currRow, {'tsumm': 0.0, 'eventSet': set(), 'uet': 0.0, 'visits': 0, 'tkd': 0})
            currVpData['tsumm'] += rec_u['SUMM']

            # if spec in ('2019', '1134', '1122', '1110', '22', '224', '27', '16'):
            #     result[1.1]['tsumm'] += rec_u['SUMM']

            #Стационары, дневные стационары, стационары дневного пребывания, стационары на дому и ВМП
            if eventProfile in ('11', '12', '41', '42', '43', '90', '51', '52', '71', '72', '401', '402'):
                currVpData['eventSet'].add(eventId)
                currVpData['tkd'] += rec_u['KD']

            # Поликлиника
            # elif eventProfile in ('21', '22'):
            #     if serviceCategory == ServiceCategory_EventByIllness:
            #         currVpData['eventSet'].add(eventId)
            #         if spec in ('2019', '1134', '1122', '1110', '22', '224', '27', '16'):
            #             result[1.1]['eventSet'].add(eventId)
            #     elif service[:3] in ('B01', 'B02', 'B04'):
            #         currVpData['visits'] += 1
            #         if spec in ('2019', '1134', '1122', '1110', '22', '224', '27', '16'):
            #             result[1.1]['visits'] += 1

            # Поликлиника
            elif eventProfile in ('21', '22') and vmp in ('12', '13'):
                if kso == '30':
                    currVpData['eventSet'].add(eventId)
                elif kso == '29':
                    currVpData['visits'] += 1

            # Поликлиника (в том числе учачстковые)
            elif eventProfile in ('271', '272'):
                if kso == '30':
                    result[1.1]['eventSet'].add(eventId)
                elif kso == '29':
                    result[1.1]['visits'] += 1
                    result[1.1]['tsumm'] += rec_u['SUMM']

            # Стоматология
            elif eventProfile in ('31', '32'):
                currVpData['eventSet'].add(eventId)

            # Женская консультация
            elif eventProfile in ('60'):
                currVpData['eventSet'].add(eventId)
                if service[0] == 'B' and service[4:7] == '001' and service not in ('B01.001.019', 'B01.001.020'):
                    currVpData['visits'] += 1

            # Центр здоровья
            elif eventProfile in ('01', '02'):
                currVpData['visits'] += 1

            # Приемное отделение
            elif eventProfile in ('111', '112'):
                if service in ('B01.069.003', 'B01.069.013'):
                    currVpData['visits'] += 1

            # ФАП
            elif eventProfile in ('201', '202'):
                if service[0] == 'B':
                    currVpData['visits'] += 1

            # СМП
            elif eventProfile in ('801', '802'):
                if service[0] == 'B': # or only 'B%.044.%'
                    currVpData['visits'] += 1

            # Диспансеризация детей-сирот
            elif eventProfile == '232':
                currVpData['eventSet'].add(eventId)

            # Диспансеризация детей, оставшихся без попечения
            elif eventProfile == '252':
                currVpData['eventSet'].add(eventId)

            # Диспансеризация взрослых
            elif eventProfile == '211':
                currVpData['eventSet'].add(eventId)

            # Неотложная помощь, мед. осмотры взрослых и детей
            elif eventProfile in ('241', '242', '261', '262'):
                currVpData['eventSet'].add(eventId)

        return result, pogrn, pinfis

    def makeInvoice(self, accNumber, dats, isOutArea, accType, datps, codeLpu):
        accName = self.cmbAccountType.name()
        reps, pogrn, pinfis =  self.getInvoiceData(accNumber)
        invoice  = QtGui.QTextDocument()
        fnt = invoice.defaultFont()
        fnt.setPointSize(9)
        invoice.setDefaultFont(fnt)
        invoice_cursor = QtGui.QTextCursor(invoice)
        fmtdiv = QtGui.QTextBlockFormat()
        # invoice_cursor.insertBlock(fmtdiv)
        # invoice_cursor.insertHtml("@@@@=@@@@")
        invoice_num  = forceString(accNumber)
        invoice_date = forceString(dats)
        zamonth = monthName[datps.month()]
        fmt =QtGui.QTextBlockFormat()
        db = QtGui.qApp.db
        tableOrganisation = db.table('Organisation')
        tableAccount = db.table('Organisation_Account')
        tableBank = db.table('Bank')
        tablef = tableOrganisation.leftJoin(tableAccount,[tableAccount['organisation_id'].eq(tableOrganisation['id'])])
        tablef = tablef.leftJoin(tableBank,[tableAccount['bank_id'].eq(tableBank['id'])])

        #Выгружаем данные поставщика и плательщика
        record = db.getRecordEx(tablef,
                                [tableOrganisation['fullName'].name(),
                                 tableOrganisation['INN'].name(),
                                 tableOrganisation['KPP'].name(),
                                 tableOrganisation['Address'].name(),
                                 tableOrganisation['chief'].name(),
                                 tableOrganisation['accountant'].name(),
                                 tableOrganisation['infisCode'].name(),
                                 tableBank['name'].alias('BankName'),
                                 tableBank['BIK'].name(),
                                 tableAccount['name'].alias('schet'),
                                 # tableAccount['personalAccount']
                                ],
                                tableOrganisation['id'].eq(QtGui.qApp.currentOrgId())
        )
        fmtc =QtGui.QTextBlockFormat()
        fmtc.setAlignment(QtCore.Qt.AlignCenter)
        fmtl=QtGui.QTextBlockFormat()
        fmtl.setAlignment(QtCore.Qt.AlignLeft)

        db = QtGui.qApp.db
        #Формируем запросы
        tableOrganisation = db.table('Organisation')
        tableAccount = db.table('Organisation_Account')
        tableBank = db.table('Bank')
        tablef = tableOrganisation.leftJoin(tableAccount,[tableAccount['organisation_id'].eq(tableOrganisation['id'])])
        tablef = tablef.leftJoin(tableBank,[tableAccount['bank_id'].eq(tableBank['id'])])
        payerCode = self.getPayerCode()
        r = db.getRecordEx(tableOrganisation,[tableOrganisation['id'].name(),tableOrganisation['head_id'].name()],
                                [tableOrganisation['isInsurer'].eq(1),
                                 tableOrganisation['deleted'].eq(0),
                                 tableOrganisation['infisCode'].eq(payerCode)])
        payerId = None
        if r: payerId = forceRef(r.value('id')) if not forceRef(record.value('head_id')) else forceRef(record.value('head_id'))

        #Определяем плательщика - тфомс или конкретная СМК
        if len(pogrn)==1 and not isOutArea:
            ogrn = pogrn.keys()[0]
            record = db.getRecordEx(tableOrganisation,[tableOrganisation['id'].name(),tableOrganisation['head_id'].name()],
                                [tableOrganisation['OGRN'].eq(ogrn),
                                 tableOrganisation['isInsurer'].eq(1),
                                 tableOrganisation['deleted'].eq(0),
                                 tableOrganisation['infisCode'].eq(pinfis)])
            if record:
                payerId = forceInt(record.value('id')) if not forceRef(record.value('head_id')) else forceInt(record.value('head_id'))

        #Выгружаем данные поставщика и плательщика
        record = db.getRecordEx(tablef,
                                [tableOrganisation['fullName'].name(),
                                 tableOrganisation['INN'].name(),
                                 tableOrganisation['KPP'].name(),
                                 tableOrganisation['Address'].name(),
                                 tableOrganisation['chief'].name(),
                                 tableOrganisation['accountant'].name(),
                                 tableOrganisation['infisCode'].name(),
                                 tableBank['name'].alias('BankName'),
                                 tableBank['BIK'].name(),
                                 tableAccount['name'].alias('schet'),
                                 # tableAccount['personalAccount']
                                ],
                                tableOrganisation['id'].eq(QtGui.qApp.currentOrgId())
        )
        record_pay = db.getRecordEx(tablef,
                                    [tableOrganisation['fullName'].name(),
                                     tableOrganisation['INN'].name(),
                                     tableOrganisation['KPP'].name(),
                                     tableOrganisation['Address'].name(),
                                     tableBank['name'].alias('BankName'),
                                     tableBank['BIK'].name(),
                                     tableAccount['name'].alias('schet'),
                                     # tableAccount['personalAccount']
                                    ],
                                    tableOrganisation['id'].eq(payerId)
        )
        seller = forceString(record.value('fullName'))
        if forceString(record.value('infisCode')) != codeLpu:
            record_s = db.getRecordEx(tableOrganisation,
                                    [tableOrganisation['fullName'].name()],
                                    tableOrganisation['infisCode'].eq(codeLpu))
            if record_s is not None:
                seller += ', ' + forceString(record_s.value('fullName'))


        # FIXME: Здесь был счет-фактура
        invoice_cursor.insertBlock(fmtdiv)
        # invoice_cursor.insertHtml("$$$$=$$$$@@@@=@@@@")
        invoice_cursor.insertHtml("@@@@=@@@@")

        chr = QtGui.QTextCharFormat()
        chr.setFontWeight(QtGui.QFont.Bold)
        invoice_cursor.insertBlock()
        table = createTable (invoice_cursor, [ ('15%', [], CReportBase.AlignLeft),
                                               ('30%', [], CReportBase.AlignLeft),
                                               ('15%', [], CReportBase.AlignLeft),
                                               ('30%', [], CReportBase.AlignLeft)
        ], headerRowCount=3, border=0, cellPadding=0, cellSpacing=0)
        chr.setFontWeight(QtGui.QFont.Bold)
        table.cellAt(0,0).setFormat(chr)
        table.cellAt(0,2).setFormat(chr)
        chr.setFontUnderline(True)
        chr.setFontWeight(QtGui.QFont.Normal)
        table.cellAt(0,1).setFormat(chr)
        table.cellAt(0,3).setFormat(chr)
        table.setText(0, 0, u'Поставщик:')
        table.setText(0, 1, seller)
        table.setText(0, 2, u'Плательщик:')
        table.setText(0, 3, forceString(record_pay.value('fullName')))
        chr.setFontWeight(QtGui.QFont.Bold)
        table.cellAt(1,0).setFormat(chr)
        table.cellAt(1,2).setFormat(chr)
        chr.setFontUnderline(True)
        chr.setFontWeight(QtGui.QFont.Normal)
        table.cellAt(1,1).setFormat(chr)
        table.cellAt(1,3).setFormat(chr)
        table.setText(1, 0, u'Расчетный:')
        pacc_str = u""
        pacc_val = forceString(record.value('personalAccount'))
        if pacc_val:
            pacc_str = u", л/с %s" % pacc_val
        table.setText(1, 1, u'ИНН %s, КПП %s, %s, БИК: %s, р/с %s%s' % (forceString(record.value('INN')),
                                                              forceString(record.value('KPP')),
                                                              forceString(record.value('BankName')),
                                                              forceString(record.value('BIK')),
                                                              forceString(record.value('schet')),
                                                              pacc_str
        ))
        table.setText(1, 2, u'Расчетный счет:')
        pacc_str = u""
        pacc_val = forceString(record_pay.value('personalAccount'))
        if pacc_val:
            pacc_str = u", л/с %s" % pacc_val
        table.setText(1, 3, u'ИНН %s, КПП %s, %s, БИК: %s, р/с %s%s' %  (forceString(record_pay.value('INN')),
                                                                       forceString(record_pay.value('KPP')),
                                                                       forceString(record_pay.value('BankName')),
                                                                       forceString(record_pay.value('BIK')),
                                                                       forceString(record_pay.value('schet')),
                                                                       pacc_str
        ))

        chr.setFontWeight(QtGui.QFont.Bold)
        table.cellAt(2,0).setFormat(chr)
        table.cellAt(2,2).setFormat(chr)
        chr.setFontUnderline(True)
        chr.setFontWeight(QtGui.QFont.Normal)
        table.cellAt(2,1).setFormat(chr)
        table.cellAt(2,3).setFormat(chr)
        table.setText(2, 0, u'Адрес:')
        table.setText(2, 1, forceString(record.value('Address')))
        table.setText(2, 2, u'Адрес:')
        table.setText(2, 3, forceString(record_pay.value('Address')))
        invoice_cursor.movePosition(QtGui.QTextCursor.End)

        fmt =QtGui.QTextBlockFormat()
        fmt.setAlignment(QtCore.Qt.AlignCenter)
        invoice_cursor.insertBlock(fmt)
        invoice_cursor.insertHtml(u"<br><b>СЧЕТ № %s от %s</b><br>" % ('_'*3,invoice_date.rjust(10,'_')))
        invoice_cursor.insertHtml(u"к реестру счетов № %s от %s за %s %s %s<br>" % (invoice_num,invoice_date,str(datps.year()), zamonth, accName))
        tableColumns = [
            ('10%', [ u'Предмет счета' ],CReportBase.AlignCenter ),
            ('50%',  [ u'Наименование' ], CReportBase.AlignCenter ),
            ('18%',  [ u'Един. изм.' ], CReportBase.AlignCenter ),
            ('16%',  [ u'Количество'], CReportBase.AlignCenter ),
            ('26%',  [ u'Сумма, руб.'], CReportBase.AlignCenter ),
            ]
        invoice_cursor.movePosition(QtGui.QTextCursor.End)
        invoice_cursor.insertBlock()
        vps = db.getRecordListGroupBy('rbMedicalAidType','name,regionalCode',group='regionalCode')
        table = createTable(invoice_cursor,tableColumns, 2, border=1, cellPadding=0, cellSpacing=0)
        for i in range(0,5):
            table.setText(1,i,str(i+1),blockFormat=fmtc)
        rownum=2
        summ=0.0

        for i in sorted(self.mapVpName.keys()):
            name = self.mapVpName[i]
            vpData = reps.get(i, {'tsumm':0.0, 'eventSet':set(), 'uet':0.0, 'visits':0, 'tkd': 0})
            table.addRow()
            table.setText(rownum, 1, name, blockFormat=fmtl)
            if i in (0, 1, 1.1, 3, 4, 5, 6, 18):
                table.addRow()
                table.mergeCells(rownum, 1, 2, 1)
            elif i == 2:
                table.addRow()
                table.addRow()
                table.mergeCells(rownum, 1, 3, 1)
            if i in (0, 18):
                table.setText(rownum,   2, u'Случаи', blockFormat=fmtl)
                table.setText(rownum+1, 2, u'койко-день', blockFormat=fmtl)
                table.setText(rownum,   3, len(vpData['eventSet']), blockFormat=fmtc)
                table.setText(rownum,   4, vpData['tsumm'], blockFormat=fmtc)
                table.setText(rownum+1, 3, vpData['tkd'], blockFormat=fmtc)
                table.setText(rownum+1, 4, 0.0, blockFormat=fmtc)
                rownum += 2
            elif i in (1, 1.1, 5):
                # if i == 1.1:
                #   table.addRow()
                #   table.addRow()
                table.setText(rownum,   2, u'посещение', blockFormat=fmtl)
                table.setText(rownum+1, 2, u'обращение', blockFormat=fmtl)
                table.setText(rownum,   3, vpData['visits'], blockFormat=fmtc)
                table.setText(rownum,   4, vpData['tsumm'], blockFormat=fmtc)
                table.setText(rownum+1, 3, len(vpData['eventSet']), blockFormat=fmtc)
                table.setText(rownum+1, 4, 0.0, blockFormat=fmtc)
                rownum += 2
            elif i == 2:
                table.setText(rownum,   2, u'УЕТ', blockFormat=fmtl)
                table.setText(rownum+1, 2, u'посещение', blockFormat=fmtl)
                table.setText(rownum+2, 2, u'обращение', blockFormat=fmtl)
                table.setText(rownum,   3, reps['accountUET'], blockFormat=fmtc)
                table.setText(rownum,   4, vpData['tsumm'], blockFormat=fmtc)
                table.setText(rownum+1, 3, vpData['visits'], blockFormat=fmtc)
                table.setText(rownum+1, 4, 0.0, blockFormat=fmtc)
                table.setText(rownum+2, 3, len(vpData['eventSet']), blockFormat=fmtc)
                table.setText(rownum+2, 4, 0.0, blockFormat=fmtc)
                rownum += 3
            elif i in (3, 4, 6):
                table.setText(rownum,   2, u'Случаи', blockFormat=fmtl)
                table.setText(rownum+1, 2, u'пациенто-день', blockFormat=fmtl)
                table.setText(rownum,   3, len(vpData['eventSet']), blockFormat=fmtc)
                table.setText(rownum,   4, vpData['tsumm'], blockFormat=fmtc)
                table.setText(rownum+1, 3, vpData['tkd'], blockFormat=fmtc)
                table.setText(rownum+1, 4, 0.0, blockFormat=fmtc)
                rownum += 2
            elif i in (7, 8, 10, 12, 13, 14, 15, 16, 17):
                table.setText(rownum,   2, u'посещение', blockFormat=fmtl)
                if i in (7, 8, 10):
                    table.setText(rownum, 3, vpData['visits'], blockFormat=fmtc)
                elif i == 15:
                    table.setText(rownum, 3, len(vpData['eventSet']) + vpData['visits'], blockFormat=fmtc)
                else:
                    table.setText(rownum, 3, len(vpData['eventSet']), blockFormat=fmtc)
                table.setText(rownum, 4, vpData['tsumm'], blockFormat=fmtc)
                rownum += 1
            elif i == 9:
                table.setText(rownum,   2, u'услуга', blockFormat=fmtl)
                table.setText(rownum, 3, vpData['visits'], blockFormat=fmtc)
                table.setText(rownum, 4, vpData['tsumm'], blockFormat=fmtc)
                rownum += 1
            elif i == 11:
                table.setText(rownum,   2, u'вызов', blockFormat=fmtl)
                table.setText(rownum, 3, vpData['visits'], blockFormat=fmtc)
                table.setText(rownum, 4, vpData['tsumm'], blockFormat=fmtc)
                rownum += 1
            summ += vpData['tsumm'] if i != 1.1 else 0


        table.addRow()
        table.addRow()
        table.addRow()
        table.mergeCells(2,0,rownum-2,1)
        table.setText(2,0,u'Медицинская помощь, оказанная гражданам',blockFormat=fmtc)
        table.mergeCells(rownum,0,3,3)
        chr.setFontWeight(QtGui.QFont.Bold)
        chr.setFontUnderline(False)
        table.cellAt(rownum,3).setFormat(chr)
        table.setText(rownum,3,u'Итого',blockFormat=fmtl);
        table.setText(rownum,4,u'%.2f'%summ,blockFormat=fmtc);
        rownum+=1
        table.cellAt(rownum,3).setFormat(chr)
        table.setText(rownum,3,u'НДС',blockFormat=fmtl);
        table.setText(rownum,4,u'-',blockFormat=fmtc);
        rownum+=1
        table.cellAt(rownum,3).setFormat(chr)
        table.setText(rownum,3,u'Всего без НДС',blockFormat=fmtl);
        table.setText(rownum,4,u'%.2f'%summ,blockFormat=fmtc);
        rownum+=1
        invoice_cursor.movePosition(QtGui.QTextCursor.End)
        fmt =QtGui.QTextBlockFormat()
        fmt.setAlignment(QtCore.Qt.AlignLeft)
        invoice_cursor.insertBlock(fmt)
        invoice_cursor.insertHtml(u"<br><b>Итого:</b> <u><i>%s</i></u>" % amountToWords(summ))
        invoice_cursor.movePosition(QtGui.QTextCursor.End)
        invoice_cursor.insertHtml(u"<br><br>"+u"Главный врач __________ %30s."%forceString(record.value('chief'))+u"&nbsp;"*25 +
                                  u"Гл. бухгалтер __________ %30s."%forceString(record.value('accountant')))
        invoice_cursor.insertBlock(fmtdiv)
        invoice_cursor.insertHtml("$$$$=$$$$")
        invoice_writer = QtGui.QTextDocumentWriter()
        filePath = os.path.join(forceStringEx(self.parent.getTmpDir()), os.path.basename("schet.html"))
        invoice_writer.setFileName(filePath)
        invoice_writer.setFormat("HTML")
        invoice_writer.write(invoice)
        #Разрывы стрниц
        f = open(filePath)
        inv = f.read()
        inv = inv.replace('$$$$=$$$$',r'</div>')
        inv = inv.replace('@@@@=@@@@',r'<div style="page-break-after:always;">')
        inv = inv.replace('####=####',r'<div">')
        f.close()

        f = open(filePath, 'w')
        f.seek(0)
        f.write(inv)
        f.close()

    def getInvoiceDataNew(self):
        def getSummaI(eId):
            return reduce(
                lambda a, x: a + x['SUMM'],
                filter(lambda k: k['SN'] == eId, dbf_u),
                0
            )

        dbfNameP = os.path.join(self.parent.getTmpDir(), 'P' + self.getDbfBaseName(False))
        dbfNameU = os.path.join(self.parent.getTmpDir(), 'U' + self.getDbfBaseName(False))
        dbf_p = Dbf(dbfNameP, True, encoding='cp866')
        dbf_u = Dbf(dbfNameU, True, encoding='cp866')

        pogrn = dict()
        pinfis = ''

        for rec_p in dbf_p:
            pogrn[rec_p['PL_OGRN']] = 1

        result = {
            u'муж 0-1': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'жен 0-1': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'муж 1-4': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'жен 1-4': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'муж 5-17': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'жен 5-17': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'муж 18-59': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'жен 18-54': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'муж от 60': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
            u'жен от 55': { 'count': 0, 'tariff': 0.0, 'total': 0.0},
        }

        for rec_p in dbf_p:
            age = calcAgeInYears(forceDate(rec_p['DATR']), forceDate(rec_p['DATO']))
            gender = rec_p['POL']
            summaI = getSummaI(rec_p['SN'])

            if gender == u'М':
                if 0 <= age <= 1:
                    result[u'муж 0-1']['count'] += 1
                    result[u'муж 0-1']['total'] += summaI
                if 1 < age <= 4:
                    result[u'муж 1-4']['count'] += 1
                    result[u'муж 1-4']['total'] += summaI
                if 5 <= age <= 17:
                    result[u'муж 5-17']['count'] += 1
                    result[u'муж 5-17']['total'] += summaI
                if 18 <= age <= 59:
                    result[u'муж 18-59']['count'] += 1
                    result[u'муж 18-59']['total'] += summaI
                if age >= 60:
                    result[u'муж от 60']['count'] += 1
                    result[u'муж от 60']['total'] += summaI
            elif gender == u'Ж':
                if 0 <= age <= 1:
                    result[u'жен 0-1']['count'] += 1
                    result[u'жен 0-1']['total'] += summaI
                if 1 < age <= 4:
                    result[u'жен 1-4']['count'] += 1
                    result[u'жен 1-4']['total'] += summaI
                if 5 <= age <= 17:
                    result[u'жен 5-17']['count'] += 1
                    result[u'жен 5-17']['total'] += summaI
                if 18 <= age <= 54:
                    result[u'жен 18-54']['count'] += 1
                    result[u'жен 18-54']['total'] += summaI
                if age >= 55:
                    result[u'жен от 55']['count'] += 1
                    result[u'жен от 55']['total'] += summaI
        return result, pogrn, pinfis

    def printInvoiceSF(self, accNumber, accType, isOutArea):  # счет-фактура
        accName = self.cmbAccountType.name()
        if accType in 'mop':
            reps, pogrn, pinfis = self.getInvoiceDataNew()
            invoice = CAccountInvoice()
            filePath = os.path.join(forceStringEx(self.parent.getTmpDir()), os.path.basename("invoice.html"))
            invoice_writer = QtGui.QTextDocumentWriter()
            invoice_writer.setFileName(filePath)
            invoice_writer.setFormat('HTML')
            invoice_writer.write(
                invoice.buildNew(reps, pogrn, self.edtDats.date(), self.edtDatps.date(), isOutArea, accNumber,
                              accName, self.getPayerCode()))
        else:
            reps, pogrn, pinfis = self.getInvoiceData(accNumber)
            invoice = CAccountInvoice()
            filePath = os.path.join(forceStringEx(self.parent.getTmpDir()), os.path.basename("invoice.html"))
            invoice_writer = QtGui.QTextDocumentWriter()
            invoice_writer.setFileName(filePath)
            invoice_writer.setFormat('HTML')
            invoice_writer.write(
                invoice.build(reps, pogrn, self.edtDats.date(), self.edtDatps.date(), isOutArea, accNumber,
                                               accName, self.getPayerCode()))

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


class CExportPage1(CBaseExportPage1):
    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.SNILS_fileD = []
        self.SNILS_fileU = []
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        # i3393 сли собрались менять что-то с personQuery, то ищите комментарий: i3393 D file
        personQuery = self.createPersonQuery()
        self.progressBar.setMaximum(max(query.size() + personQuery.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.exportedUID = []
        # i2776: список КСГ, которые не стоит учитывать при формировании счета
        self.ignoredCsg = None
        return dbf, query, personQuery

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()

        dbf, query, personQuery = self.prepareToExport()
        accDate, accNumber, settleDate, contractId = getAccountInfo(self.parent.accountId)
        origAccNumber = accNumber

        accOrgStructureId = forceRef(QtGui.qApp.db.translate('Account', 'id', self.parent.accountId, 'orgStructure_id')) or QtGui.qApp.currentOrgStructureId()
        bookkeeperCode = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', accOrgStructureId , 'bookkeeperCode'))
        if not bookkeeperCode:
            self.log(u'<b><font color=red>ОШИБКА</font></b>: Для текущего ЛПУ не задан код для бухгалтерии', True)
            if not self.ignoreErrors:
                return
        self.log(u'ЛПУ: код для бухгалтерии: "%s".' % bookkeeperCode)

        recipientId = forceString(QtGui.qApp.db.translate('Contract', 'id', contractId , 'recipient_id'))
        self.recipientInfisCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', recipientId, 'infisCode'))

        iAccNumber = 0
        self.exportedTempInvalidList = []
        self.exportedClients = set()
        self.exportedDirections = []

        strContractNumber = forceString(QtGui.qApp.db.translate('Contract', 'id', contractId , 'number')) if contractId else u'б/н'
        accNumber = accNumber.replace(strContractNumber + u'-', u'')
        accNumberSplit = accNumber.split('/')
        if len(accNumberSplit) > 1:
            accNumber = accNumberSplit[0]
        try:
            iAccNumber = forceInt(accNumber)
        except:
            self.log(u'Невозможно привести номер счёта' \
                     u' "%s" к числовому виду' % accNumber)

        accType = self.cmbAccountType.code()
        self.eventInfo = self.getEventInfo()
        self.modernClients = set() # модернизированные пациенты (есть федеральная цена)

        payerId = forceRef(QtGui.qApp.db.translate('Contract', 'id', self.parent.contractId, 'payer_id'))
        payerOGRN = forceString(QtGui.qApp.db.translate('Organisation', 'id', payerId, 'OGRN')) if payerId else ''
        isOutArea = forceInt(QtGui.qApp.db.translate('Contract', 'id', self.parent.contractId, 'exposeDiscipline'))
        isOutArea = ((isOutArea & 0b1100000) >> 5) == 0
        self.log(u'ОГРН плательщика `%s`.' % payerOGRN)

        if self.idList:
            self.exportedUIDs = []
            self.exportedRIDs = []
            self.dictKSO = {}
            # Составляем множество событий, содержащих услуги с модернизацией
            while query.next():
                record = query.record()
                if record:
                    federalPrice = forceDouble(record.value('federalPrice'))

                    if federalPrice != 0.0:
                        self.modernClients.add(forceRef(record.value('client_id')))

            query.exec_() # встаем перед первой записью

            # i3646 Словарь посещений пациента (поликлинические приемы) KSO = 29
            # Ключ: 'ClientId_PersonSpecialityCode_MKBX' ('SN_SPEC_MKBX')
            # Значение: количество посещений к врачу одной специальности (SPEC) с одним кодом заболевания MKBX
            self.polyclinicVisitsDict = dict()

            self.exportListP = []
            # i3393 D file
            self.personIdForFileD = []
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), bookkeeperCode, iAccNumber, settleDate, accType, payerOGRN)

             # if that record already exists, update KSO
            for row in self.exportListP:
                if row['SN'] in self.dictKSO.keys():
                    if '27' in self.dictKSO[row['SN']]:
                        row['KSO'] = '27'
                    elif '30' in self.dictKSO[row['SN']]:
                        row['KSO'] = '30'

                u""" i4432, comment: (0018022)
                    У нас есть в файле P поля:
                    MP - код формы обращения
                    KSO - способ оплаты.
                    Eсли MP=2 и в файле P для одного SN есть KSO=29, то P_CEL выгружаем = 1
                    Если MP=8, то P_CEL выгружаем = 2
                    если MP=1 и в файле P для одного SN есть KSO=27 или 30, то P_CEL выгружаем = 3
                    если MP=1 и в файле P для одного SN нет KSO=27 или 30, то P_CEL выгружаем = 1
                """
                if row['MP'] == '2' and (row['KSO'] == "29"):
                    row['P_CEL'] = '1'
                elif row['MP'] == '8':
                    row['P_CEL'] = '2'
                elif row['MP'] == '1' and (row['KSO'] == "27" or row['KSO'] == "30"):
                    row['P_CEL'] = '3'
                elif row['MP'] == '1':
                    row['P_CEL'] = '1'

            for x in self.polyclinicVisitsDict:
                if self.polyclinicVisitsDict[x]['count'] > 1:
                    keys = self.polyclinicVisitsDict[x].keys()
                    keys.remove('count')
                    dbfRecord = dbf[1].newRecord()  # dbf[1] is dbfU
                    for k in keys:
                        dbfRecord[k] = self.polyclinicVisitsDict[x][k]
                    dbfRecord.store()

            for x in self.exportListP:
                x.store()

            # i3393 D file
            self.personIdForFileD = list(set(self.personIdForFileD).union(set(getPersonIdList())))
            self.progressBar.setMaximum(max(query.size() - personQuery.size(), 1))
            personQuery = self.createPersonQuery()
            self.progressBar.setMaximum(max(query.size() + personQuery.size(), 1))
            while personQuery.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.processPerson(dbf, personQuery.record(), bookkeeperCode)

            diff = list(set(self.SNILS_fileU) - set(self.SNILS_fileD))
            u"""
            Если есть СНИЛС-ы в файле U которые не попали в файл D
            записываем непопавших в файл D
            """
            if diff:
                self.personIdForFileD = getAdditionalPersonIdList(diff)
                personQuery = self.createPersonQuery()

                while personQuery.next():
                    QtGui.qApp.processEvents()
                    if self.aborted:
                        break
                    self.progressBar.step()
                    self.processPerson(dbf, personQuery.record(), bookkeeperCode)
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        for x in dbf:
            x.close()

        datps = self.edtDatps.date()
        d = datps if datps and datps.isValid() else settleDate if settleDate and settleDate.isValid() else QtCore.QDate.currentDate()
        dats = self.edtDats.date()
        d1 = dats if dats and dats.isValid() else settleDate if settleDate and settleDate.isValid() else QtCore.QDate.currentDate()
        account_number = toVariant(self.parent.page1.edtRegistryNumber.value())
        self.makeInvoice(account_number, d1, isOutArea, accType, d, bookkeeperCode)
        if self.chkGenInvoice.isChecked():
            self.printInvoiceSF(account_number, accType, isOutArea)

        if self.chkUpdateAccountNumber.isChecked():
            regNumber = forceStringEx(self.parent.page1.edtRegistryNumber.value())
            if regNumber and not (origAccNumber.startswith(regNumber + '-') or origAccNumber == regNumber):
                updateAccountInfo(self.parent.accountId, number=regNumber + '-' + origAccNumber)

        updateAccountInfo(self.parent.accountId,
                          accountType_id=self.cmbAccountType.value(),
                          exportFileName=self.getZipFileName())

    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = u"""SELECT DISTINCT
              Action.person_id AS actPersId,
              Account_Item.id        AS accountItem_id,
              Account_Item.master_id AS account_id,
              Account_Item.event_id  AS event_id,
              Account_Item.action_id AS action_id,
              Event.client_id        AS client_id,
              Event.`order`          AS `order`,
              Event.setDate          AS begDate,
              Event.execDate         AS endDate,
              Event.`hospParent`     AS `hospParent`,
              Event.dispByMobileTeam AS isDispMobileTeam,
              EventMedicalAidProfile.code AS eventType_code,
              IF(Account_Item.action_id, Action.begDate, IF(Account_Item.visit_id, Visit.date, Event.setDate)) as servBegDate,
              IF(Account_Item.action_id, Action.endDate, IF(Account_Item.visit_id, Visit.date, Event.execDate)) as servEndDate,
              Event.MES_id AS mesId,
              Event.externalId       AS externalId,
              Client.lastName        AS lastName,
              Client.firstName       AS firstName,
              Client.patrName        AS patrName,
              Client.birthDate       AS birthDate,
              Client.sex             AS sex,
              Client.SNILS           AS SNILS,
              ClientPolicy.serial    AS policySerial,
              ClientPolicy.number    AS policyNumber,
              ClientPolicy.note AS policyNote,
              ClientPolicy.begDate AS policyBegDate,
              ClientPolicy.endDate AS policyEndDate,
              ClientPolicy.insuranceArea AS policyInsuranceArea,
              {15_extension}
              Insurer.OKATO AS insurerOKATO,
              Insurer.OGRN AS insurerOGRN,
              Insurer.area AS insurerArea,
              rbPolicyType.code      AS policyType,
              rbPolicyKind.regionalCode AS policyKindCode,
              ClientDocument.serial  AS documentSerial,
              ClientDocument.number  AS documentNumber,
              rbDocumentType.code    AS documentType,
              rbDocumentType.regionalCode AS documentRegionalCode,
              IF(work.title IS NOT NULL,
                  work.title, ClientWork.freeInput) AS `workName`,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.infis,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                ) AS service,
              IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.id,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.id, rbEventService.id)
                    ) AS serviceId,
              IF(Account_Item.service_id IS NOT NULL,
                Account_Item.service_id,
                IF(Account_Item.visit_id IS NOT NULL, Account_Item.visit_id,
                    IF(Account_Item.action_id IS NOT NULL, Account_Item.action_id, Event.id)
                )) AS cardId,
              IF(Account_Item.visit_id IS NOT NULL, Visit.person_id,
                    IF(Account_Item.action_id IS NOT NULL,
                            IF(Action.person_id IS NOT NULL, Action.person_id, Action.setPerson_id), Event.execPerson_id)
                ) AS execPersonId,
              Event.execPerson_id AS pureExecPersonId,
              Visit.date AS visitDate,
              Visit.visitType_id AS visitTypeId,
              Action.begDate AS actionDate,
              Diagnosis.MKB          AS MKB,
              Action.MKB AS actMKB,
              AssociatedDiagnosis.MKB AS AssociatedMKB,
              ComplicationDiagnosis.MKB AS ComplicationMKB,
              Account_Item.price   AS price,
              Account_Item.amount    AS amount,
              Account_Item.`sum`     AS `sum`,
              Contract_Tariff.federalPrice AS federalPrice,
              LEAST(
                IF(Contract_Tariff.federalLimitation = 0,Account_Item.amount,
                    LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                Account_Item.sum) AS federalSum,
              Person.code AS personCode,
              Person.regionalCode AS personRegionalCode,
              servPerson.regionalCode AS servRegionalPersonCode,
              servPersonSpeciality.regionalCode as servPersonSpecialityCode,
              servPersonSpeciality.federalCode as fedServPersonSpecialityCode,
              servPersonSpeciality.id as servPersonSpecialityId,
              rbSpeciality.regionalCode AS specialityCode,
              rbSpeciality.id AS specialityId,
              DiagnosticResult.regionalCode AS diagnosticResultCode,
              EventResult.regionalCode AS eventResultCode,
              OrgStructure.infisCode AS orgStructCode,
              servOrgStructure.infisCode AS servOrgStructCode,
              `OrgStructure`.`bookkeeperCode` AS KPK,
              RelegateOrg.infisCode AS RelegateOrgCode,
              Referral.id AS referralId,
              Referral.number AS referralNumber,
              (SELECT rbr.netrica_Code FROM rbReferralType rbr WHERE rbr.id = Referral.type LIMIT 1) AS referralType,
              Referral.examType AS referralExamType,
              Referral.clinicType AS referralClinicType,
              Referral.date AS referralDate,
              Referral.hospDate AS referralHospDate,
              Referral.relegateOrg_id AS policRefOrgId,
              Referral.isSend AS referralIsOutgoing,
              # Referral.speciality_id AS referralSpeciality_id,
              (
                SELECT rbs.regionalCode 
                FROM 
                    rbMedicalAidProfile rbmap 
                    INNER JOIN rbSpeciality rbs ON rbs.OKSOName = rbmap.name
                WHERE rbmap.id = Referral.medProfile_id
                LIMIT 1
              ) AS referralSpec,
              OutgoingOrg.infisCode AS outgoingOrgCode,
              ActionOrg.infisCode AS actionOrgCode,
              Action.note AS actNote,
              Action.directionDate AS actSetDate,
              rbEventProfile.code AS eventProfileCode,
              EventType.code AS eventTypeCode,
              SocStatus.regionalCode AS socStatusCode,
              IF (HospitalAction.id IS NOT NULL,1,0) AS hospitalFlag,
              rbMedicalAidType.code AS medicalAidTypeCode,
              rbMedicalAidType.federalCode AS medicalAidTypeFederalCode,
              rbMedicalAidKind.federalCode AS medicalAidKindFederalCode,
              rbMedicalAidUnit.federalCode AS medicalAidUnitFederalCode,
              IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.federalCode,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.federalCode, EventMedicalAidProfile.regionalCode)
                  ) AS medicalAidProfileFederalCode,
              (SELECT Event_LittleStranger.currentNumber FROM Event_LittleStranger WHERE Event_LittleStranger.id = Event.littleStranger_id) as nborn
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN Event PolicyEvent ON PolicyEvent.id = IFNULL(Event.id, IFNULL(Action.event_id, Visit.event_id))
            LEFT JOIN ClientPolicy ON ClientPolicy.id = PolicyEvent.clientPolicy_id
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
            LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id AND
                      ClientRegAddress.id = (SELECT MAX(CRA.id)
                                         FROM   ClientAddress AS CRA
                                         WHERE  CRA.type = 0 AND CRA.client_id = Client.id AND CRA.deleted=0)
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN Person AS setEventPerson ON setEventPerson.id = Event.setPerson_id
            LEFT JOIN Person AS servPerson ON servPerson.id = IF(Account_Item.action_id IS NOT NULL,
                                                                 Action.person_id,
                                                                 IF(Account_Item.visit_id IS NOT NULL,
                                                                    Visit.person_id,
                                                                    Event.execPerson_id))
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Diagnostic ON Diagnostic.id = (SELECT D.id
                        FROM Diagnostic D
                            INNER JOIN Diagnosis D1
                                ON D1.id = D.diagnosis_id
                            INNER JOIN rbDiagnosisType DT
                                ON D.diagnosisType_id = DT.id
                            WHERE D.deleted = 0 AND D1.deleted = 0 AND DT.code IN ('1', '2') AND D.event_id = Event.id
                            ORDER BY D1.MKB = '', DT.code = '2', D1.id LIMIT 1)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN rbDiagnosticResult AS DiagnosticResult
                ON DiagnosticResult.id = Diagnostic.result_id
            LEFT JOIN Diagnostic AS AssociatedDiagnostic ON
                      AssociatedDiagnostic.id = (SELECT AD.id
                                         FROM Diagnostic AD
                                         INNER JOIN rbDiagnosisType rdt ON rdt.id = AD.diagnosisType_id
                                         WHERE rdt.code = '9' AND AD.deleted = 0 AND AD.event_id = Account_Item.event_id
                                                AND AD.person_id = Event.setPerson_id
                                         ORDER BY id LIMIT 1)
            LEFT JOIN Diagnostic AS ComplicationDiagnostic ON ComplicationDiagnostic.id = (
                SELECT AD.id
                FROM Diagnostic AD
                INNER JOIN rbDiagnosisType rdt ON rdt.id = AD.diagnosisType_id
                WHERE rdt.code = '3' AND AD.deleted = 0 AND AD.event_id = Account_Item.event_id AND AD.person_id = Event.setPerson_id
                ORDER BY id LIMIT 1)

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
            LEFT JOIN Diagnosis AS AssociatedDiagnosis ON AssociatedDiagnosis.id = AssociatedDiagnostic.diagnosis_id AND AssociatedDiagnosis.deleted = 0
            LEFT JOIN Diagnosis AS ComplicationDiagnosis ON ComplicationDiagnosis.id = ComplicationDiagnostic.diagnosis_id AND ComplicationDiagnosis.deleted = 0
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN OrgStructure AS servOrgStructure ON servOrgStructure.id = servPerson.orgStructure_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN rbSpeciality AS servPersonSpeciality ON servPersonSpeciality.id = servPerson.speciality_id
            LEFT JOIN Referral ON ((Referral.id = Event.referral_id) OR (Referral.event_id = Event.id)) AND Referral.deleted = 0 AND Referral.isCancelled = 0
            LEFT JOIN Organisation AS RelegateOrg ON RelegateOrg.id = IF(Event.referral_id IS NULL, Event.relegateOrg_id,  Referral.relegateOrg_id)
            LEFT JOIN Organisation AS OutgoingOrg ON OutgoingOrg.id = Referral.relegateOrg_id
            LEFT JOIN Organisation AS ActionOrg ON Action.org_id = ActionOrg.id AND ActionOrg.deleted = 0
            LEFT JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
            LEFT JOIN rbMedicalAidProfile AS VisitMedicalAidProfile ON VisitMedicalAidProfile.id = rbVisitService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id =rbMedicalAidType.id
            LEFT JOIN rbMedicalAidKind ON EventType.medicalAidKind_id = rbMedicalAidKind.id
            LEFT JOIN rbEventProfile AS EventMedicalAidProfile ON
                EventType.eventProfile_id = EventMedicalAidProfile.id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
            LEFT JOIN Action AS HospitalAction ON
                HospitalAction.id = (
                    SELECT MAX(A.id)
                    FROM Action A
                    WHERE A.event_id = Event.id AND
                              A.deleted = 0 AND
                              A.actionType_id = (
                                    SELECT AT.id
                                    FROM ActionType AT
                                    WHERE AT.flatCode ='moving' and AT.deleted = 0
                                    LIMIT 0, 1
                              )

                )
            LEFT JOIN ClientSocStatus ON ClientSocStatus.id= (
                SELECT MAX(CSS2.id)
                FROM ClientSocStatus AS CSS2
                WHERE CSS2.client_id = `Client`.id AND
                CSS2.deleted = 0 AND CSS2.socStatusClass_id = (
                    SELECT rbSSC2.id
                    FROM rbSocStatusClass AS rbSSC2
                    WHERE rbSSC2.code = '9' AND rbSSC2.group_id IS NULL
                    LIMIT 0,1
                ))
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            #LEFT JOIN rbMedicalAidUnit ON Contract_Tariff.unit_id = rbmedicalaidunit.id
            LEFT JOIN rbSocStatusType AS SocStatus ON
                ClientSocStatus.socStatusType_id = SocStatus.id
            LEFT JOIN Account ON Account_Item.master_id = Account.id
            LEFT JOIN Contract ON Account.contract_id = Contract.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND {cond}
            ORDER BY referralNumber DESC
        """  # .format(tableAccountItem['id'].inlist(self.idList))
        stmt = stmt.replace(u"{cond}", tableAccountItem['id'].inlist(self.idList))
        # i3393 new cols
        stmt = stmt.replace(
            u"{15_extension}",
            u"""
              (
                  SELECT
                    cd.groupNumber
                  FROM
                    ClientDisability cd
                  WHERE
                    Client.id = cd.client_id
                    AND cd.groupNumber IS NOT NULL
                    AND cd.isPrimary = 1
                  LIMIT 1
              ) AS disabilityGroupNumber,
              Action.`status` AS `actionStatus`,
              IF(EXISTS(SELECT * FROM Action a WHERE a.deleted = 0 AND a.status = 9 AND a.event_id = Event.id), 1, 0) AS haveRefusedVisit,
              (SELECT rb.`code` FROM rbMedicalAidProfile rb WHERE rb.`id` = Referral.medProfile_id) AS `referralMedProfile`,
              (SELECT rb.`code` FROM rbHospitalBedProfile rb WHERE rb.`id` = Referral.hospBedProfile_id) AS `referralHospitalBedProfile`,
              (SELECT visitDiag.`status` FROM Diagnostic visitDiag WHERE visitDiag.`id` = Visit.`diagnostic_id` ) AS `diagStatus`,
              (SELECT rb.regionalCode FROM rbEventGoal rb WHERE rb.`id` = Event.goal_id ) AS `goalRegionalCode`,
              (SELECT rb.netrica_Code FROM rbEventGoal rb WHERE rb.`id` = Event.goal_id ) AS `goalNetricaCode`,
              (SELECT diagOrg.infisCode FROM Diagnostic visitDiag INNER JOIN Organisation diagOrg ON  diagOrg.id = visitDiag.`org_id` WHERE visitDiag.`id` = Visit.`diagnostic_id` ) AS `diagOrgCode`,
              (SELECT diagOrg.OGRN FROM Diagnostic visitDiag INNER JOIN Organisation diagOrg ON  diagOrg.id = visitDiag.`org_id` WHERE visitDiag.`id` = Visit.`diagnostic_id` ) AS `diagOrgOGRN`,
              # (
              #     SELECT
              #       netricaHospChannel.code
              #     FROM
              #       Action ReceivedAction
              #       INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
              #       INNER JOIN ActionPropertyType ChannelType ON ReceivedActionType.id = ChannelType.actionType_id AND ChannelType.name = 'Канал доставки'
              #       LEFT JOIN ActionProperty ChannelProperty ON ChannelType.id = ChannelProperty.type_id AND ChannelProperty.action_id = ReceivedAction.id
              #       LEFT JOIN ActionProperty_Reference ChannelReference ON ChannelProperty.id = ChannelReference.id
              #       LEFT JOIN netricaHospChannel ON ChannelReference.value = netricaHospChannel.id
              #     WHERE
              #       ReceivedAction.event_id = Event.id
              #       AND ChannelType.deleted = 0
              #       AND ChannelProperty.deleted = 0
              #     LIMIT 1
              # ) AS deliveredChanelCode,
              (
                  SELECT
                    cq.quotaTicket
                  FROM
                    Client_Quoting cq
                  WHERE
                    cq.deleted = 0
                    AND cq.master_id = Client.id
                  ORDER BY dateRegistration DESC, id DESC
                  LIMIT 1
              ) AS clientQuotaTicketNumber,
              (
                  SELECT
                    cq.dateRegistration
                  FROM
                    Client_Quoting cq
                  WHERE
                    cq.deleted = 0
                    AND cq.master_id = Client.id
                  ORDER BY directionDate DESC, id DESC
                  LIMIT 1
              ) AS clientQuotaTicketRegDate,
              (
                  SELECT
                    DiagnosticDispanser.code
                  FROM
                    rbDispanser AS DiagnosticDispanser
                  WHERE
                    Diagnostic.dispanser_id = DiagnosticDispanser.id
              ) AS dispancerCode,
            """
        )
        return db.query(stmt)

    def getEventInfo(self):
        u"""возвращает общую стоимость услуг за пациента"""

        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """SELECT
            Event.id,
            SUM(sum) AS totalSum,
            SUM(LEAST(IF(Contract_Tariff.federalLimitation = 0,
                Account_Item.amount,
                LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                Account_Item.sum)) AS federalSum
        FROM Account_Item
        LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
        LEFT JOIN Event ON Account_Item.event_id = Event.id
        LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
        WHERE Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
        GROUP BY Event.id;
        """ % tableAccountItem['id'].inlist(self.idList)
        query = db.query(stmt)

        result = {}
        while query.next():
            record  = query.record()
            eventId = forceRef(record.value(0))
            result[eventId] = (forceDecimal(record.value(1)), forceDecimal(record.value(2)))
        return result

    def getSocStatusFederalCode(self, clientId):
        db = QtGui.qApp.db
        table = db.table('ClientSocStatus')
        stmt = """
            SELECT rbSocStatusType.regionalCode AS fedCode
            FROM ClientSocStatus
            LEFT JOIN rbSocStatusClass ON socStatusClass_id = rbSocStatusClass.id
            LEFT JOIN rbSocStatusType ON socStatusType_id = rbSocStatusType.id
            WHERE rbSocStatusClass.code = '12' AND %s
        """ % db.joinAnd([ table['client_id'].eq(clientId),
            table['deleted'].eq(0)])

        ret = ''

        query = db.query(stmt)
        if query.next():
            record=query.record()
            ret = forceString(record.value('fedCode'))

        return ret

    def process(self, dbf, record, bookkeeperCode, accNumber, settleDate, accType, payerOGRN):
        db = QtGui.qApp.db
        birthDate = forceDate(record.value('birthDate'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        age = calcAgeInYears(birthDate, endDate)
        # Номер стат.талона
        clientId = forceRef(record.value('client_id'))
        eventId = forceRef(record.value('event_id'))
        eventTypeCode = forceInt(record.value('eventType_code'))
        accountItemId = forceRef(record.value('accountItem_id'))

        hospitalFlag = forceBool(record.value('hospitalFlag'))
        setOrgCode = forceInt(record.value('RelegateOrgCode'))
        referralNumber = forceString(record.value('referralNumber'))
        outgoingOrgCode = forceInt(record.value('outgoingOrgCode'))
        outgoingRefNumber = forceString(record.value('referralNumber'))
        actionOrgInfisCode = forceString(record.value('actionOrgCode'))
        actionOrgCode = forceInt(record.value('actionOrgCode'))
        if not actionOrgCode and not forceRef(record.value('actPersId')):
            lpuOgrn = forceString(db.translate('Organisation', 'infisCode', bookkeeperCode, 'OGRN'))
            if lpuOgrn != forceString(record.value('diagOrgOGRN')):
                actionOrgCode = forceInt(record.value('diagOrgCode'))

        isExternalService = (actionOrgInfisCode != '' and isExternalOrgCode(actionOrgInfisCode))
        isFromRelegateOrg = ((setOrgCode != 0) and (setOrgCode != forceInt(bookkeeperCode)))
        insurerArea = forceString(record.value('insurerArea'))
        isAlien = insurerArea[:2] != QtGui.qApp.defaultKLADR()[:2]
        modern = clientId in self.modernClients

        externalId = forceInt(record.value('externalId'))
        isti = forceString(record.value('externalId'))
        if isti[0:5].upper() == u'ДСДДЦ':
            isti = isti[5:]
        elif isti[0:2].upper() == u'ДС':
            isti = isti[2:]
        sn = forceInt(isti)

        documentNumber = forceString(record.value('documentNumber'))

        (dbfP, dbfU, dbfD, dbfN, dbfR) = dbf
        # FIXME: pirozhok: Временный КК костыль, разобраться почему происходит задвоение
        if accountItemId not in self.exportedUID:
            self.exportedUID.append(accountItemId)
        else:
            return
        # i3582
        # Если в случае лечения с eventType.code = "48" (Стационарное обращение амбулаторное)
        # указан результат обращения "Направлен на госпитализацию", то в счет этот случай не выгружаем.
        if forceString(record.value('eventTypeCode')) == '48' and forceString(record.value('eventResultCode')) == '305':
            return

        medicalAidTypeCode = forceString(record.value('medicalAidTypeCode'))

        # filling dictionary will all possible KSOs from file U
        if accountItemId not in self.exportedUIDs:
            key = eventId
            self.dictKSO.setdefault(key, [])
            self.dictKSO[eventId].append((forceString(record.value('medicalAidUnitFederalCode'))))

        # ======================================================================================
        # P FILE
        if not ((eventId, modern, externalId) in self.exportedClients):
            dbfRecord = dbfP.newRecord()

            (clientSum, clientFederalSum) = self.eventInfo[eventId]

            # дата начала лечения обязательное
            dbfRecord['DATN'] = pyDate(begDate)
            if self.ignoredCsg is None:
                from Accounting.Utils import getIgnoredCsgList
                self.ignoredCsg = getIgnoredCsgList()

            for x in self.ignoredCsg:
                if record.value('event_id') == x['idCsg']:
                    dbfRecord['DATN'] = pyDate(forceDate(x['date']))
                    break

            # дата окончания лечения обязательное
            DATO = endDate
            dbfRecord['DATO'] = pyDate(DATO)


            # номер реестра счетов (п. 1; 4 примечаний) обязательное
            dbfRecord['NS'] = self.edtRegistryNumber.value()

            # номер персонального счета (п. 13 примечаний) обязательное
            dbfRecord['SN'] = clientId

            # тип реестра счетов (п. 2; 4 примечаний) обязательное SPR21
            dbfRecord['VS'] = accType

            # дата формирования реестра счетов (п. 3; 4 примечаний) обязательное
            dats = self.edtDats.date()
            dbfRecord['DATS'] = pyDate(dats if dats and dats.isValid() else settleDate if settleDate and settleDate.isValid() else QtCore.QDate.currentDate())

            # Дата формирования персонального счета (п. 13 примечаний) обязательное
            datps = self.edtDatps.date()
            dbfRecord['DATPS'] = pyDate(datps if datps and datps.isValid() else settleDate if settleDate and settleDate.isValid() else QtCore.QDate.currentDate())

            # код МО, оказавшей медицинскую помощь обязательное SPR01
            dbfRecord['CODE_MO'] = bookkeeperCode

            # ОГРН плательщика (п. 4 примечаний) обязательное SPR02
            dbfRecord['PL_OGRN'] = payerOGRN if isAlien else forceString(record.value('insurerOGRN'))

            #  фамилия (п. 5 примечаний) обязательное
            dbfRecord['FIO'] = nameCase(forceString(record.value('lastName')))

            # имя (п. 5 примечаний) обязательное
            dbfRecord['IMA'] = nameCase(forceString(record.value('firstName')))

            # отчество (п. 5 примечаний)
            patrName = forceString(record.value('patrName'))
            dbfRecord['OTCH'] = nameCase(patrName)

            # пол (М/Ж) (п. 6 примечаний) обязательное
            dbfRecord['POL'] = formatSex(record.value('sex')).upper()

            # дата рождения (п. 7 примечаний) обязательное
            dbfRecord['DATR'] = pyDate(birthDate)

            # категория граждан обязательное SPR09
            # 1 работающий / 0 не работающий
            workOrgName = forceString(record.value('workName'))
            dbfRecord['KAT'] = 1 if workOrgName else 0

            # СНИЛС
            SNILS = forceString(record.value('SNILS'))
            dbfRecord['SNILS'] = formatSNILS(SNILS) if SNILS else ''

            # код ОКАТО территории страхования по ОМС обязательное для инокраевых SPR39
            insuranceArea = forceString(db.translate('kladr.KLADR', 'CODE', forceString(record.value('policyInsuranceArea')), 'OCATD', idFieldName='CODE'))
            if not insuranceArea:
                self.log(u'<b><font color=orange>Внимание</font></b>: в полисе не задана территория страхования, пытаюсь определить по ОКАТО СМО!')

                insuranceArea = forceString(record.value('insurerOKATO'))
                if not insuranceArea:
                    insurerName = forceString(db.translate('kladr.KLADR', 'CODE', insurerArea, 'OCATD', idFieldName='CODE'))
                    self.log(u'<b><font color=orange>Внимание</font></b>: ОКАТО для СМО "%s" не задан, пытаюсь определить по области страхования!' % insurerName)

                    insuranceArea = forceString(db.translate('kladr.KLADR', 'CODE', insurerArea, 'OCATD', idFieldName='CODE'))
                    if not insuranceArea:
                        self.log(u'<b><font color=orange>Внимание</font></b>: Область страхования для СМО "%s" не задана!' % insurerName)
            dbfRecord['OKATO_OMS'] = insuranceArea

            # тип ДПФС (п. 11 примечаний) обязательное
            dbfRecord['SPV'] = forceInt(record.value('policyKindCode')) % 10

            # серия ДПФС обязательное (для документов ОМС, имеющих серию)
            dbfRecord['SPS'] = forceString(record.value('policySerial'))

            # номер ДПФС (п. 12 примечаний) обязательное
            dbfRecord['SPN'] = forceString(record.value('policyNumber'))

            # DROPED i3393
            # статус представителя пациента  обязательное для инокраевых SPR41
            # dbfRecord['STAT_P'] = '0'

            socStatusCode = forceInt(record.value('socStatusCode')) % 100

            documentRegionalCode = forceInt(record.value('documentRegionalCode')) % 100
            if documentRegionalCode:
                # код типа УДЛ (п. 9 примечаний) обязательное для инокраевых). При указании ЕНП может не заполняться. SPR43
                dbfRecord['C_DOC'] = documentRegionalCode

            documentSerial = forceString(record.value('documentSerial'))
            if documentSerial:
                # серия УДЛ (п. 9 примечаний) обязательное для инокраевых). При указании ЕНП может не заполняться.
                dbfRecord['S_DOC'] = documentSerial

            if documentNumber:
                # номер УДЛ (п. 9 примечаний) обязательное для инокраевых). При указании ЕНП может не заполняться.
                dbfRecord['N_DOC'] = documentNumber

            # Признак новорожденого
            isLittleStrangerAge = calcAgeInDays(birthDate, begDate) < 90
            exportAsLittleStranger = isLittleStrangerAge and (
                (dbfRecord['SPS'] == '' and dbfRecord['SPN'] == '') or
                (dbfRecord['S_DOC'] == '' and dbfRecord['N_DOC'] == '')
            )

            # признак новорожденного (п. 14 примечаний) обязательное (в случае оказания МП ребенку до государственной регистрации)
            if exportAsLittleStranger:
                dbfRecord['NOVOR'] = unicode(forceInt(record.value('sex'))).upper() + forceString(
                    birthDate.toString('ddMMyy')) + unicode(max(1, forceInt(record.value('nborn'))))

            # вес при рождении (п.16 примечаний)
            weight = getWeightIfAborted(eventId)
            if calcAgeInDays(birthDate, begDate) < 90 and weight is not None:
                dbfRecord['VNOV_D'] = weight

            representativeInfo = self.getClientRepresentativeInfo(clientId)
            # if representativeInfo and (exportAsLittleStranger or (not isLittleStrangerAge)):
            if representativeInfo and (exportAsLittleStranger):
                dbfRecord['FAMP'] = representativeInfo.get('lastName', '')
                dbfRecord['IMP'] = representativeInfo.get('firstName', '')
                dbfRecord['OTP'] = representativeInfo.get('patrName', '')
                dbfRecord['POLP'] = formatSex(representativeInfo.get('sex', 0))
                dbfRecord['DATRP'] = pyDate(representativeInfo.get('birthDate', None))
                dbfRecord['C_DOC'] = representativeInfo.get('documentTypeRegionalCode', 18) % 100
                dbfRecord['S_DOC'] = representativeInfo.get('serial', '')
                dbfRecord['N_DOC'] = representativeInfo.get('number', '')

                if exportAsLittleStranger:
                    dbfRecord['FIO'] = dbfRecord['FAMP']
                    dbfRecord['IMA'] = dbfRecord['IMP']
                    dbfRecord['OTCH'] = dbfRecord['OTP']
                    dbfRecord['POL'] = dbfRecord['POLP']
                    dbfRecord['DATR'] = dbfRecord['DATRP']
                    dbfRecord['SNILS'] = formatSNILS(representativeInfo.get('SNILS', ''))
                    dbfRecord['SPS'] = representativeInfo.get('policySerial', '')
                    dbfRecord['SPN'] = representativeInfo.get('policyNumber', '')

            # признак "Особый случай" при регистрации  обращения за медицинской помощью (п. 8 примечаний)
            # обязательное (в случае наличия особого случая или для диспансеризации и профосмотров предполагающих этапность) SPR42
            flags = ''
            if dbfRecord['SPS'] == '' and dbfRecord['SPN'] == '' and endDate <= QtCore.QDate(2016, 9, 30):
                # нет данных по полису
                flags += '1'
            if exportAsLittleStranger:
                flags += '2'
            if dbfRecord['OTCH'] == '':
                # отсутствие отчества
                flags += '4'
            if medicalAidTypeCode == '13':
                flags += '5'
            elif medicalAidTypeCode == '14':
                flags += '6'
            if forceInt(record.value('hospParent')) == 1:
                flags += '7'
            if forceInt(record.value('isDispMobileTeam')):
                flags += '8'
            if forceInt(record.value('eventProfileCode')) in [211, 232, 252, 261, 262] \
                    and forceInt(record.value('haveRefusedVisit')):
                flags += '9'
            flags += self.getSocStatusFederalCode(clientId)
            dbfRecord['Q_G'] = forceStringEx(flags)

            if isFromRelegateOrg and not forceInt(record.value('referralIsOutgoing')):
                # код направившей МО обязательное (по направлениям и для телемедицины) SPR01
                dbfRecord['NAPR_MO'] = '%.5d' % setOrgCode

                tblVisitType = db.table('rbVisitType')
                if not forceInt(db.translate(tblVisitType, tblVisitType['id'], forceInt(record.value('visitTypeId')), tblVisitType['code'])) == 15:
                    # номер направления (п.15 примечаний) обязательное (по направлениям на плановую госпититализацию)
                    dbfRecord['NAPR_N'] = '%.5d_%s' % (setOrgCode, referralNumber) if '_' not in referralNumber else referralNumber  # '%.5d_%.7d' % (forceInt(self.edtOrgStructureCode.text()), referralNumber)

                    # дата направления обязательное
                    dbfRecord['NAPR_D'] = pyDate(forceDate(record.value('referralDate')))  # pyDate(endDate)

                    if forceInt(record.value('referralType')) == 1:
                        # дата планируемой госпитализации
                        dbfRecord['NAPR_DP'] = pyDate(forceDate(record.value('referralHospDate')))

            # номер амбулаторной карты или истории болезни обязательное
            dbfRecord['ISTI'] = isti if isti else forceString(clientId)

            # код исхода заболевания обязательное SPR11
            dbfRecord['ISHL'] = forceString(record.value('diagnosticResultCode'))

            # код исхода обращения обязательное SPR12
            dbfRecord['ISHOB'] = forceString(record.value('eventResultCode'))

            # код вида обращения обязательное SPR14
            dbfRecord['MP'] = '2' if forceInt(record.value('order')) == 2 else '1'

            # сумма к оплате по ОМС по случаю заболевания пациента обязательное
            # dbfRecord['SUMMA_I'] = clientSum

            # табельный номер врача закрывшего талон/историю (п. 17 примечаний) обязательное
            # i3393 P file personCode -> personRegionalCode (DROPED i4432)
            # dbfRecord['DOC_TABN'] = forceString(record.value('personRegionalCode'))

            # коды причин возврата (п. 10 примечаний) обязательное для возвратных счетов SPR15
            #dbfRecord['PV']

            # дата возврата обязательное для возвратных счетов
            #dbfRecord['DVOZVRAT']

            # i4432 P file: СНИЛС врача из файла D*
            personId = forceInt(record.value('execPersonId'))
            dbfRecord['DOC_SS'] = formatSNILS(forceString(self.getPersonInfoById(personId).value('SNILS')))
            # i4432 P file: код специальности врача, закрывшего талон/историю
            #dbfRecord['SPEC'] = forceString(self.getPersonInfoById(personId).value('federalCode'))
            dbfRecord['SPEC'] = forceString(record.value('servPersonSpecialityCode'))



            # i4432 P file: профиль оказанной мед.помощи для всех случаев лечения
            serviceId = forceRef(record.value('serviceId'))
            profile = self.getProfile(serviceId, personId) if personId and serviceId else None
            profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]
            dbfRecord['PROFIL'] = profileStr

            # i4432 P file: вид мед.помощи
            # i4795 P file: SPEC, Profile, VMP должно браться из отвественного исполнителя
            vmpFromPerson = eventTypeCode in [232, 211, 252, 261, 262]
            serviceDetail = self.serviceDetailCache.get(serviceId)
            serviveAidProfileCode, serviceAidKindCode, serviceAidTypeCode = self.getAidCodes(
                serviceDetail,
                begDate,
                forceRef(record.value('specialityId')),
                birthDate,
                forceInt(record.value('sex')),
                forceString(record.value('MKB'))
            )
            if serviceAidKindCode:
                dbfRecord['VMP'] = serviceAidKindCode
            else:
                dbfRecord['VMP'] = forceString(record.value('medicalAidKindFederalCode'))

            # i4432 P file: способ оплаты медицинской помощи
            dbfRecord['KSO'] = forceString(record.value('medicalAidUnitFederalCode'))

            #TODO: shepas: i4795 заменить этот костыль на что-то вменяемое
            if vmpFromPerson:
                db = QtGui.qApp.db
                tblService = db.table('rbService')
                tblMedicalAidKind = db.table('rbMedicalAidKind')
                tblMedicalAidUnit = db.table('rbMedicalAidUnit')
                tblAccountItem = db.table('Account_Item')
                tblEvent = db.table('Event')
                tblVisit = db.table('Visit')

                tblQuery = tblVisit.innerJoin(tblEvent, tblVisit['event_id'].eq(tblEvent['id']))
                tblQuery = tblQuery.innerJoin(tblService, tblVisit['service_id'].eq(tblService['id']))
                tblQuery = tblQuery.innerJoin(tblAccountItem, [tblVisit['id'].eq(tblAccountItem['visit_id']), tblAccountItem['deleted'].eq(0)])
                tblQuery = tblQuery.innerJoin(tblMedicalAidUnit, tblMedicalAidUnit['id'].eq(tblAccountItem['unit_id']))
                tblQuery = tblQuery.leftJoin(tblMedicalAidKind, tblMedicalAidKind['id'].eq(tblService['medicalAidKind_id']))

                cond = [
                    tblVisit['person_id'].eq(personId),
                    tblVisit['deleted'].eq(0),
                    tblEvent['deleted'].eq(0),
                    tblEvent['id'].eq(eventId)
                ]
                recCode = db.getRecordEx(tblQuery, [tblMedicalAidKind['federalCode'], tblMedicalAidUnit['code']], cond)
                if recCode:
                    if forceString(recCode.value('federalCode')):
                        dbfRecord['VMP'] = forceString(recCode.value('federalCode'))
                    if forceString(recCode.value('code')):
                        dbfRecord['KSO'] = forceString(recCode.value('code'))

            # i4432 P file: код диагноза основного заболевания по МКБ–Х
            dbfRecord['MKBX'] = forceString(record.value('MKB'))

            # i4432 P file: цель посещения

            # убираем старую логику i4432, comment: (0018022)
            # if forceString(record.value('goalNetricaCode')) in ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11']:
            #    dbfRecord['P_CEL'] = "1"
            # elif forceString(record.value('goalNetricaCode')) in ['12']:
            #    dbfRecord['P_CEL'] = "2"
            # elif forceString(record.value('goalNetricaCode')) in ['1']:
            #    dbfRecord['P_CEL'] = "3"

            u""" i4432, comment: (0018022)
                У нас есть в файле P поля:
                MP - код формы обращения
                KSO - способ оплаты.
                Если MP=2 или 8, то P_CEL выгружаем = 2
                если MP=1 и в файле P для одного SN есть KSO=27 или 30, то P_CEL выгружаем = 3
                если MP=1 и в файле P для одного SN нет KSO=27 или 30, то P_CEL выгружаем = 1
            """
            if dbfRecord['MP'] == '2' or dbfRecord['MP'] == '8':
                dbfRecord['P_CEL'] = '2'
            elif dbfRecord['MP'] == '1' and (dbfRecord['KSO'] == "27" or dbfRecord['KSO'] == "30"):
                dbfRecord['P_CEL'] = '3'
            elif dbfRecord['MP'] == '1':
                dbfRecord['P_CEL'] = '1'

            u""" i3393 P file
                2. Добавить поле INV после поля SPS (серия документа, подтверждающего факт страхования):
                - INV,С (1)-группа инвалидности: заполняется из обращения (таблица...поле....).
                Допустимые значения:
                0-нет инвалидности,
                1-I группа,
                2-II группа,
                3-III группа,
                4-дети-инвалиды.
                Заполняется только при впервые установленной инвалидности (1-4) или в случае отказа в
                признании лица инвалидом (0).
                Для остальных случаев поле не заполняется.
            """
            # группа инвалидности: заполняется из обращения (таблица...поле....)
            if forceRef(record.value('disabilityGroupNumber')) is not None:
                dbfRecord['INV'] = forceString(record.value('disabilityGroupNumber'))

            u""" i3716
                В связи с тем, что для отправки ИЭМК в действие Поступление добавлено свойство "Канал доставки", а у
                нас уже есть похожее свойство "Кем доставлен", нужно для исключения дублирования ввода информации
                убрать свойство "Кем доставлен".

                1) Завязываемся на свойство "Канал доставки", в котором есть значения:
                СМП, Самостоятельно, Перевод из другой МО, Перевод внутри МО с другого профиля.

                2) В счета (файл P) в поле P_PER выгружаем значения:
                    1-Самостоятельно
                    2-СМП
                    3-Перевод из другой МО
                    4-Перевод внутри МО с другого профиля
                Соответствие кодов:
                    если указан код Нетрики 2, то выгружаем "1"
                    если указан код Нетрики 1, то выгружаем "2"
                    если указаны коды Нетрики 3,4 то выгружаем "3"
                    если указаны коды Нетрики 6,7, то выгружаем "4".
                Для остальных случаев поле не заполняется.
            """
            # netricaCodeMap = {
            #     '1': 2,
            #     '2': 1,
            #     '3': 3,
            #     '4': 3,
            #     '6': 4,
            #     '7': 4,
            #     '8': 1
            # }
            # deliveredChanelCode = netricaCodeMap.get(forceString(record.value('deliveredChanelCode')), None)
            # if deliveredChanelCode:
            #     dbfRecord['P_PER'] = deliveredChanelCode

            # i4432 P file: номер талона на ВМП & дата выдачи талона на ВМП
            # TAL_N номер талона на ВМП: берем с вкладки "Квоты" из карточки клиента - "Номер талона"
            clientQuotaTicketNumber = forceString(record.value('clientQuotaTicketNumber'))
            # TAL_D дата талона на ВМП: берем с вкладки "Квоты" из карточки клиента - "Дата регистрации"
            clientQuotaRegDate = pyDate(forceDate(record.value('clientQuotaTicketRegDate')))

            if clientQuotaTicketNumber and dbfRecord['VMP'] == '32':
                dbfRecord['TAL_N'] = clientQuotaTicketNumber

            if clientQuotaRegDate and dbfRecord['VMP'] == '32':
                dbfRecord['TAL_D'] = clientQuotaRegDate
            u""" i3393 P file
                5. Добавить после поля NAPR_N поле NAPR_D (D) (дата выдачи направления на плановую госпитализацию).
                Поле обязательно для заполнения, если есть направление на плановую госпитализацию, ВМП и исследования.

                Берем из вкл. Мероприятия -> Поступление -> Дата выдачи направления.
            """
            # dbfRecord['NAPR_D'] = pyDate(forceDate(record.value('receiveDirectionDate')))

            u""" i3393 P file
                6. Добавить после NAPR_D поле NAPR_DP (Д) (дата планируемой госпитализации).
                Берем из направления на ПГ.
                Поле обязательно для заполнения, если есть направление на плановую госпитализацию, ВМП.
            """
            # dbfRecord['NAPR_DP'] = pyDate(forceDate(record.value('receivePlannedEndDate')))

            u""" i3716 P file
            Форматы экспорта счетов R23NATIVE, R23DKKB.
            Для счетов по диспансеризации; типы: a,c,d,e,g,h. -> dbfRecord['VS'] (accType)
            Для VP с кодами:211,232,252,261,262.

            PR_D_N=1 - если в обращении в блоке "Осмотры" в столбце "ДН" указано одно из значений: 1 или 2 или 6;
            PR_D_N=0 - если в обращении в блоке "Осмотры" в столбце "ДН" указано другое.
            """

            if forceInt(record.value('eventProfileCode')) in [22, 211, 232, 252, 261, 262]:  # and accType in 'acdegh':
                if forceInt(record.value('dispancerCode')) in [1, 2, 6]:
                    dbfRecord['PR_D_N'] = 1
                else:
                    dbfRecord['PR_D_N'] = 0

            u""" i3716 P file
            Для счетов по диспансеризации; типы: a,c,d,e,g,h. Форматы экспорта счетов R23NATIVE, R23DKKB.
            - заполняем, если в обращении указан один из результатов обращения:
            323,324,325,334,335,336,339,340,341,345,349,350,351,355,356,357,358
            (т.е. результат диспансеризации - присвоение 3,4,5 групп здоровья);
            - заполняем по шаблону: XXXXХХХХ. Может быть несколько значений, выгружаем все без разделителей. Например: 146 .
            Коды:
            1 - направлен на консультацию в медицинскую организацию по месту прикрепления
            2 - направлен на консультацию в иную медицинскую организацию
            3 - направлен на обследование
            4 - направлен в дневной стационар
            5 - направлен на госпитализацию
            6 - направлен в реабилитационное отделение.

            P.S.: rbreferraltype.netrica_code == referral.type
            policRefOrgId - referral.relegateOrg_id
            Если в обращении есть направление на консультацию (rbreferraltype.netrica_code = 4),
            и referral.relegateOrg_id совпадает с кодом направляющей МО,
            то выгружаем NAZR=1

            Если в обращении есть направление на консультацию (rbreferraltype.netrica_code = 4),
            и referral.relegateOrg_id НЕ совпадает с кодом направляющей МО,
            то выгружаем NAZR=2

            Если в обращении есть направление на обследование (rbreferraltype.netrica_code = 3),
            то выгружаем NAZR=3

            Если в обращении есть направление на госпитализацию в дневной стационар (rbreferraltype.netrica_code=1, referral.clinicType=2),
            то выгружаем NAZR=4

            Если в обращении есть направление на госпитализацию в стационар (rbreferraltype.netrica_code=1, referral.clinicType=1),
            то выгружаем NAZR=5.
            """
            # DROPED i4432
            # if forceInt(record.value('eventResultCode')) in [
            #     323, 324, 325, 334, 335, 336, 339, 340, 341, 345, 349, 350, 351, 355, 356, 357, 358
            # ] and accType in 'acdegh' and forceString(record.value('eventTypeCode')) in ['06', '211', '232', '252', '261', '262']:
            #     referralType = forceInt(record.value('referralType'))
            #     referralClinicType = forceInt(record.value('referralClinicType'))
            #     referralOrgId = forceInt(record.value('policRefOrgId'))
            #     NAZR = ""
            #
            #     if referralType == 4 and referralOrgId == QtGui.qApp.currentOrgId():
            #         NAZR += '1'
            #     elif referralType == 4:
            #         NAZR += '2'
            #     if referralType == 4:
            #         NAZR += '3'
            #     if referralType == 1 and referralClinicType == 2:
            #         NAZR += '4'
            #     if referralType == 1 and referralClinicType == 1:
            #         NAZR += '5'
            #     dbfRecord['NAZR'] = NAZR

            u""" i3716 P file
            NAPR_N, NAPR_D.

            Для направлений на плановую госпитализацию и исследования, выданных на амбулаторно-поликлиническом приеме.
            (сейчас выгружается только для стационаров).
            Берем из таблицы referral.
            Тип направления "1" или "3" (rbreferraltype).
            Форматы экспорта счетов R23NATIVE, R23DKKB.
            """

            # if forceInt(record.value('referralType')) in [1, 3]:
            #     dbfRecord['NAPR_N'] = referralNumber
            #     dbfRecord['NAPR_D'] = pyDate(forceDate(record.value('referralDate')))

            appendToList = True
            if len(self.exportListP) > 0:
                for x in self.exportListP:
                    if dbfRecord['SN'] == x['SN']:
                        appendToList = False
                        x['DATO'] = pyDate(endDate)  # dbfRecord['DATO']
                        # x['SUMMA_I'] += dbfRecord['SUMMA_I']
                        # x['DOC_TABN'] = dbfRecord['DOC_TABN']

            if appendToList:
                self.exportListP.append(dbfRecord)

            # dbfRecord.store()
            self.exportedClients.add((eventId, modern, externalId))
        else:  # if that record already exists, update KSO
            for row in self.exportListP:
                if row['SN'] in self.dictKSO.keys():
                    for event in self.dictKSO:
                        if '26' in self.dictKSO[event] and '27' in self.dictKSO[event]:
                            row['KSO'] = '27'
                        elif '29' in self.dictKSO[event] and '30' in self.dictKSO[event]:
                            row['KSO'] = forceString('30')
                        elif '9' in self.dictKSO[event] and '30' in self.dictKSO[event]:
                            row['KSO'] = '30'
                        else:
                            row['KSO'] = forceString(record.value('medicalAidUnitFederalCode'))

                u""" i4432, comment: (0018022)
                    У нас есть в файле P поля:
                    MP - код формы обращения
                    KSO - способ оплаты.
                    Если MP=2 или 8, то P_CEL выгружаем = 2
                    если MP=1 и в файле P для одного SN есть KSO=27 или 30, то P_CEL выгружаем = 3
                    если MP=1 и в файле P для одного SN нет KSO=27 или 30, то P_CEL выгружаем = 1
                """
                if row['MP'] == '2' or row['MP'] == '8':
                    row['P_CEL'] = '2'
                elif row['MP'] == '1' and (row['KSO'] == "27" or row['KSO'] == "30"):
                    row['P_CEL'] = '3'
                elif row['MP'] == '1':
                    row['P_CEL'] = '1'

        mesId = forceRef(record.value('mesId'))
        # ======================================================================================
        # U FILE
        dbfRecord = dbfU.newRecord()
        # уникальный номер записи об оказанной медицинской услуге в пределах реестра (п. 1 примечаний) обязательное
        dbfRecord['UID'] = accountItemId

        # код МО, оказавшей медицинскую помощь обязательное SPR01
        dbfRecord['CODE_MO'] = bookkeeperCode

        # номер реестра счетов обязательное
        dbfRecord['NS'] = self.edtRegistryNumber.value()

        # номер персонального счета обязательное
        dbfRecord['SN'] = clientId #eventId

        # код профиля койки (п. 2 примечаний) обязательное (для стационаров всех типов) SPR08
        # dbfRecord['KPK'] = medicalAidTypeCode
        # if hospitalFlag:
        #    dbfRecord['KPK'] = '00'
        # if medicalAidTypeCode == '7':
        # dbfRecord['KPK'] = forceString(record.value('KPK'))#'40'

        # код отделения (п. 2, 6 примечаний) обязательное SPR07
        dbfRecord['KOTD'] = forceString(record.value('servOrgStructCode'))

        # код диагноза основного заболевания по МКБ–Х (п. 2 примечаний) обязательное (кроме диагностических услуг) SPR20
        dbfRecord['MKBX'] = forceString(record.value('MKB'))

        # код диагноза сопутствующего заболевания по МКБ–Х (п. 2 примечаний) SPR20
        dbfRecord['MKBXS'] = forceString(record.value('AssociatedMKB'))

        # код диагноза осложнения заболевания по МКБ–Х (п. 2 примечаний) SPR20
        dbfRecord['MKBXO'] = forceString(record.value('ComplicationMKB'))

        u""" i3716 U file
        4.1. Поле MKBХ_PR: только для счетов по диспансеризации/профилактическим медицинским осмотрам (типы счетов: a,c,d,e,g,h)
        Форматы экспорта счетов R23NATIVE, R23DKKB.

        0 - по умолчанию;
        1 - если диагноз выявлен впервые.

        Как определяем, что диагнозы установлены впервые: по образу и подобию определения для отчетной формы 12.
        Примерный алгоритм: проверяем наличие диагноза, указанного как заключительный, по всем эвентам.
        Смотрим среди диагнозов с типом "Заключительный" или "Основной".

        4.2. Поле MKBХS_PR: только для счетов по диспансеризации/профилактическим медицинским осмотрам (типы счетов: a,c,d,e,g,h)
        Форматы экспорта счетов R23NATIVE, R23DKKB.

        0 - по умолчанию;
        1 - если диагноз выявлен впервые.

        Как определяем, что диагноз установлен впервые: как и в предыдущем пункте.
        Примерный алгоритм: проверяем наличие диагноза, указанного как сопутствующий, по всем эвентам.
        Смотрим среди диагнозов с типом "Сопутствующий".
        """

        if accType in 'acdegh' and forceString(record.value('eventTypeCode')) in ['06', '211', '232', '252', '261', '262']:
            primaryQuery = u"""
            SELECT
                IF(COUNT(Diagnosis.MKB) > 0, 0, 1) AS isPrimary
            FROM
                Event
                INNER JOIN Diagnostic ON Event.id = Diagnostic.event_id
                INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id
                INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id = rbDiagnosisType.id
            WHERE
                Event.client_id = {clientId}
                AND Event.id <> {eventId}
                AND Diagnosis.MKB LIKE '{MKB}'
            """
            primaryQuery = primaryQuery.replace(u'{clientId}', forceString(clientId))
            primaryQuery = primaryQuery.replace(u'{eventId}', forceString(eventId))

            if dbfRecord['MKBX'] and dbfRecord['MKBX'] not in ['Z.00', 'Z.01.4']:
                isPrimary = db.getRecordEx(stmt=primaryQuery.replace(u'{MKB}', dbfRecord['MKBX']))
                dbfRecord['MKBX_PR'] = forceString(isPrimary.value('isPrimary'))
            if dbfRecord['MKBXS'] and dbfRecord['MKBXS'] not in ['Z.00', 'Z.01.4']:
                isPrimary = db.getRecordEx(stmt=primaryQuery.replace(u'{MKB}', dbfRecord['MKBXS']))
                dbfRecord['MKBXS_PR'] = forceString(isPrimary.value('isPrimary'))

        # код условия оказания медицинской помощи (п. 2, 3 примечаний) обязательное SPR13
        dbfRecord['VP'] = forceString(record.value('eventProfileCode'))

        # код медицинской услуги обязательное SPR18
        dbfRecord['KUSL'] = forceString(record.value('service'))

        mesId = forceRef(record.value('mesId'))

        # i3716 U file deprecated
        # резервное поле
        # dbfRecord['KSTAND'] = ''

        # количество услуг обязательное
        amount = forceInt(record.value('amount'))
        dbfRecord['KOLU'] = amount

        # количество койко-дней (дней лечения) обязательное (для стационаров всех типов)
        ## KD должно быть заполнено, только если в поле KUSL стоит стандарт или койко-день
        if (dbfRecord['KUSL'][0:1] not in ('K', 'S')) and not medicalAidTypeCode == '7':
            amount = amount #TODO: ???
        elif dbfRecord['KUSL'][0:1] in ('K', 'S') and (hospitalFlag or medicalAidTypeCode == '7'):
            if medicalAidTypeCode == '7':
                dbfRecord['KD'] = amount
            else:
                if endDate != None and begDate != None:
                    amount = begDate.daysTo(endDate) #forceInt(record.value('amount')) #???
                    if mesId:
                        try:
                            minAmount = forceInt(db.translate('mes.MES', 'id', mesId, 'minDuration'))
                            maxAmount = forceInt(db.translate('mes.MES', 'id', mesId, 'maxDuration'))
                            if (amount < minAmount):
                                # Если фактическое пребывание пациента меньше интервала по стандарту
                                amount = amount #TODO: ???
                            elif (amount <= maxAmount):
                                # Если фактическое пребывание пациента не выходит за пределы интервала
                                amount = amount #TODO: ???
                            else:
                                # Если фактическое пребывание пациента больше интервала по стандарту
                                amount = amount #TODO: ???
                        except:
                            pass
                        dbfRecord['KD'] = amount
                    else:
                        dbfRecord['KD'] = amount
                else:
                    dbfRecord['KD'] = amount

        servDate = forceDate(record.value('actionDate'))
        if not servDate.isValid():
            servDate = forceDate(record.value('visitDate'))
            if not servDate.isValid():
                servDate = begDate
                if not servDate.isValid():
                    self.log(u'Не задана дата услуги: accountItemId=%d,' \
                             u' eventId=%d.' % (accountItemId, eventId))

        # дата начала выполнения услуги обязательное
        dbfRecord['DATN'] = pyDate(forceDate(record.value('servBegDate')))
        if self.ignoredCsg is None:
            from Accounting.Utils import getIgnoredCsgList
            self.ignoredCsg = getIgnoredCsgList()

        for x in self.ignoredCsg:
            if record.value('event_id') == x['idCsg'] and not x['checked']:
                dbfRecord['DATN'] = pyDate(forceDate(x['date']))
                x['checked'] = True
                break

        price = forceDecimal(record.value('price'))
        summ = forceDecimal(record.value('sum'))
        u"""
        # дата окончания выполнения услуги обязательное
        dbfRecord['DATO'] = pyDate(forceDate(record.value('servEndDate')))

        # тариф на оплату по ОМС (п.5 примечаний) обязательное SPR22
        dbfRecord['TARU'] = price #'N', 12, 2),

        # сумма к оплате по ОМС (п.5 примечаний) обязательное
        dbfRecord['SUMM'] = summ

        # признак: услуга оказана в другой МО (п. 3 примечаний) обязательное
        dbfRecord['IS_OUT'] = 1 if isExternalService else 0
        """
        u""" i3393 U file
            1. Если услуга оказана в другой МО (в поле OUT_MO указан код другой МО):

            - в поле IS_OUT выгружаем код "1", если услуга оказана в другой МО;
            - в поле IS_OUT выгружаем код "0" по умолчанию ИЛИ
              если внешняя услуга (исследование) выполнена юридическим лицом при проведении диспансеризации определенных групп взрослого населения).

            2. В список состояний услуги добавить значения:

            "Услуга не выполнена по медицинским противопоказаниям": если указано, то в поле IS_OUT выгружаем код "2";
            "Услуга не выполнена по прочим причинам (пациент умер, переведен в другое отделение и пр.)": если указано, то в поле IS_OUT выгружаем код "3";
            "Пациент отказался от услуги (документированный отказ)": если указано, то в поле IS_OUT выгружаем код "4".
        """
        status = forceRef(record.value('actionStatus'))
        if status == ActionStatus.NotDoneByMedicalReasons:  # 7: Не выполнено по мед. противопоказаниям
            dbfRecord['IS_OUT'] = 2
        elif status == ActionStatus.NotDoneByOtherReasons:  # 8: Не выполнено по прочим причинам
            dbfRecord['IS_OUT'] = 3
        elif status == ActionStatus.PatientRefused:  # 9: Пациент отказался от услуги
            dbfRecord['IS_OUT'] = 4
        elif status == ActionStatus.DoneOnTime:  # 10: Выполнено в пределах установленных сроков
            dbfRecord['IS_OUT'] = 1
        else:
            dbfRecord['IS_OUT'] = 1 if isExternalService else 0

        if dbfRecord['IS_OUT'] in [2, 3, 4]:
            dbfRecord['KOLU'] = 0

        if dbfRecord['IS_OUT'] == 1:
            # код МО, оказавшей услугу (п.4 примечаний) SPR01
            dbfRecord['OUT_MO'] = ('%s' % actionOrgCode).rjust(5, '0') if actionOrgCode else ''
        elif dbfRecord['IS_OUT'] == 0 and actionOrgCode != QtGui.qApp.currentOrgStructureInfis():
            dbfRecord['OUT_MO'] = ('%s' % actionOrgCode).rjust(5, '0') if actionOrgCode else ''
        else:
            dbfRecord['OUT_MO'] = ''

        u""" i3393 U file
            При этом:
            - если дата выполнения не указана, то в поле DATO выгружаем дату окончания лечения;
            - в поля TARU и SUMM ничего не выгружаем.
            - все обязательные реквизиты (код отделения, код профиля койки, код диагноза основного, и т.п.) заполняются данными на момент обращения в МО.
        """
        if status is None and not forceRef(record.value('actPersId')):
            status = forceInt(record.value('diagStatus'))

        if forceDate(record.value('servBegDate')) != QtCore.QDate():
            # дата окончания выполнения услуги обязательное
            dbfRecord['DATO'] = pyDate(forceDate(record.value('servEndDate')))

            # тариф на оплату по ОМС (п.5 примечаний) обязательное SPR22
            dbfRecord['TARU'] = forceDecimal(price)  # 'N', 12, 2),

            # сумма к оплате по ОМС (п.5 примечаний) обязательное
            if status in [7, 8, 9, 10, 11]:
                dbfRecord['SUMM'] = forceDecimal(0.0)
            else:
                dbfRecord['SUMM'] = forceDecimal(record.value('sum'))

                # for x in self.exportListP:
                #     if dbfRecord['SN'] == x['SN']:
                #         x['SUMMA_I'] += dbfRecord['SUMM']
        else:
            # дата окончания выполнения услуги обязательное
            dbfRecord['DATO'] = pyDate(forceDate(record.value('endDate')))

        if dbfRecord['IS_OUT'] == 1:
            # код МО, оказавшей услугу (п.4 примечаний) SPR01
            dbfRecord['OUT_MO'] = ('%s' % actionOrgCode).rjust(5, '0') if actionOrgCode else ''
        elif dbfRecord['IS_OUT'] == 0 and actionOrgCode != QtGui.qApp.currentOrgStructureInfis():
            dbfRecord['OUT_MO'] = ('%s' % actionOrgCode).rjust(5, '0') if actionOrgCode else ''
        else:
            dbfRecord['OUT_MO'] = ''

        # табельный номер сотрудника, оказавшего услугу (п. 7 примечаний)
        # i3393 U file servPersonCode -> servRegionalPersonCode
        # dbfRecord['DOC_TABN'] = forceString(record.value('servRegionalPersonCode'))

        # i4432 U file: СНИЛС врача закрывшего талон/историю (п. 17 примечаний)
        personId = forceRef(record.value('actPersId'))
        if not personId:
            personId = forceRef(record.value('execPersonId'))
        dbfRecord['DOC_SS'] = formatSNILS(forceString(self.getPersonInfoById(personId).value('SNILS')))
        self.SNILS_fileU.append(forceString(self.getPersonInfoById(personId).value('SNILS')))

        # код специальности специалиста, оказавшего услугу SPR46
        dbfRecord['SPEC'] = forceString(record.value('servPersonSpecialityCode')) if forceDate(
            record.value('servEndDate')) >= QtCore.QDate(2016, 2, 1) else \
            forceString(record.value('fedServPersonSpecialityCode'))

        serviceId = forceRef(record.value('serviceId'))
        profile = self.getProfile(serviceId, personId) if personId and serviceId else None
        profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]

        # профиль оказанной медицинской помощи SPR60
        if dbfRecord['IS_OUT'] == 0:
            dbfRecord['PROFIL'] = profileStr
        else:
            dbfRecord['PROFIL'] = ''

        serviceDetail = self.serviceDetailCache.get(serviceId)
        serviveAidProfileCode, serviceAidKindCode, serviceAidTypeCode = self.getAidCodes(
            serviceDetail,
            begDate,
            forceRef(record.value('servPersonSpecialityId')),
            birthDate,
            forceInt(record.value('sex')),
            forceString(record.value('MKB'))
        )
        # вид медицинской помощи SPR59
        if dbfRecord['IS_OUT'] == 0:
            dbfRecord['VMP'] = serviceAidKindCode if serviceAidKindCode else forceString(
                record.value('medicalAidKindFederalCode'))
        else:
            dbfRecord['VMP'] = ''

        # i4535 U File
        if dbfRecord['IS_OUT'] == 1 and forceInt(record.value('eventProfileCode')) in [211, 232, 252, 261, 262]:
            # forceString(record.value('eventTypeCode')) in ['211', '232', '252', '261', '262']:
            dbfRecord['SUMM'] = forceDecimal(0.0)
            dbfRecord['TARU'] = forceDecimal(0.0)
            dbfRecord['DOC_SS'] = ''
            dbfRecord['SPEC'] = ''
            dbfRecord['PROFIL'] = ''
            dbfRecord['VMP'] = ''

        # i4447 U file
        if dbfRecord['VMP'] == '32' \
                and dbfRecord['KUSL'].startswith('V') and forceRef(record.value('action_id')) is None:
            rec = db.getRecordEx(stmt=u"""
                    SELECT
                        aps.value AS stent
                    FROM
                        Action a
                        JOIN ActionPropertyType apt ON a.actionType_id = apt.actionType_id
                        JOIN ActionProperty ap ON a.id = ap.action_id AND apt.id = ap.type_id
                        JOIN ActionProperty_String aps ON ap.id = aps.id
                    WHERE
                        a.deleted = 0
                        AND a.event_id = {eventId}
                        # AND a.id = actionId
                        AND apt.shortName = 'stent'
                    """.format(eventId=eventId))
            if rec:
                stentCount = forceRef(rec.value('stent'))
                if stentCount:
                    dbfRecord['TARU'] = dbfRecord['SUMM']

        # i4447 file U
        if dbfRecord['VMP'] == '32':
            rec = db.getRecordEx(stmt=u"""
            SELECT
                aps.value AS stent
            FROM
                Action a
                JOIN ActionPropertyType apt ON a.actionType_id = apt.actionType_id
                JOIN ActionProperty ap ON a.id = ap.action_id AND apt.id = ap.type_id
                JOIN ActionProperty_String aps ON ap.id = aps.id
            WHERE
                a.deleted = 0
                AND a.event_id = {eventId}
                AND a.id = {actionId}
                AND apt.shortName = 'stent'
            """.format(eventId=eventId, actionId=forceInt(record.value('action_id'))))
            if rec:
                stentCount = forceRef(rec.value('stent'))
                if stentCount:
                    dbfRecord['KOLU'] = stentCount
                    dbfRecord['TARU'] = dbfRecord['SUMM']

        # способ оплаты медицинской помощи SPR17
        # dbfRecord['KSO'] = forceString(record.value('medicalAidUnitFederalCode'))
        key = dbfRecord['SN']
        self.dictKSO.setdefault(key, [])
        self.dictKSO[dbfRecord['SN']].append((forceString(record.value('medicalAidUnitFederalCode'))))

        # appendToList = True
        gen = (sn for sn in self.exportListP if dbfRecord['SN'] == sn['SN'])
        if gen:
            for sn in gen:
                # appendToList = False
                # x['DATO'] = dbfRecord['DATO']# pyDate(endDate)
                # DROPED i4432
                # x['SUMMA_I'] += dbfRecord['SUMM']
                if sn['DATO'] < dbfRecord['DATO']:
                    sn['DATO'] = dbfRecord['DATO']
                    # x['DOC_TABN'] = dbfRecord['DOC_TABN']

        # i3393 D file
        # execPersonId = forceRef(record.value('execPersonId'))
        # if execPersonId and execPersonId not in self.personIdForFileD:
        #     self.personIdForFileD.append(execPersonId)

        if dbfRecord['IS_OUT'] == 0 and status == ActionStatus.DoneWhilstClinicalExamination and not isExternalService:
            dbfRecord['DOC_TABN'] = u''
            dbfRecord['SPEC'] = u''

        u"""
        Issue: i3646
        При выгрузке счетов по поликлинике (формат ДККБ)в файл U добавляем обращения.

        По файлу U:

        1. Для пациента с кодом SN находим все посещения (UID), KSO=29, к врачу одной специальности (SPEC) с одним кодом заболевания (MKBX).

        2. Если количество посещений (UID) больше 2, то добавляем строку (обращение),
        заполняем её значениями:

        UID
        KSO="30"
        TARU=0
        SUMM=0
        DATN = дата начала первого посещения
        DATO = дата окончания последнего посещения
        KOLU = 1
        KUSL
        """
        kso = forceString(record.value('medicalAidUnitFederalCode'))
        if kso == '29':
            dictKey = '%s_%s_%s' % (dbfRecord['SN'], dbfRecord['SPEC'], dbfRecord['MKBX'])
            keys = dbfRecord.dbf.fieldNames
            keys.remove('UID')
            # keys.remove('KSO')
            keys.remove('TARU')
            keys.remove('SUMM')
            keys.remove('DATN')
            keys.remove('DATO')
            keys.remove('KOLU')
            keys.remove('KUSL')
            kusl = u''
            # исключения
            if dbfRecord['KUSL'] in ('B01.001.004', 'B01.001.005') or \
                    (dbfRecord['KUSL'] in ('B01.001.001', 'B01.001.002') and dbfRecord['MKBX'] and dbfRecord['MKBX'][0] in 'OZ'):
                pass
            elif dbfRecord['KUSL'].startswith('B01.001.'):
                if age < 18:
                    kusl = u'B01.001.020'
                else:
                    kusl = u'B01.001.019'
            else:
                krec = db.getRecordEx(stmt=u"SELECT s.code "
                                           u"FROM rbService s "
                                           u"INNER JOIN rbServiceCategory sc ON "
                                           u"          s.category_id = sc.id AND sc.code = '1' "
                                           u"WHERE s.code LIKE '%s%%'" % dbfRecord['KUSL'][:8])
                if krec:
                    kusl = forceString(krec.value('code'))
            if kusl:
                if dictKey in self.polyclinicVisitsDict:
                    self.polyclinicVisitsDict[dictKey]['count'] += 1
                    self.polyclinicVisitsDict[dictKey]['DATO'] = dbfRecord['DATO']
                else:
                    self.polyclinicVisitsDict[dictKey] = dict()
                    self.polyclinicVisitsDict[dictKey]['count'] = 1
                    self.polyclinicVisitsDict[dictKey]['UID'] = dbfRecord['UID'] * 10
                    # self.polyclinicVisitsDict[dictKey]['KSO'] = '30'
                    self.polyclinicVisitsDict[dictKey]['TARU'] = forceDecimal(0.0)
                    self.polyclinicVisitsDict[dictKey]['SUMM'] = forceDecimal(0.0)
                    self.polyclinicVisitsDict[dictKey]['DATN'] = dbfRecord['DATN']
                    self.polyclinicVisitsDict[dictKey]['DATO'] = dbfRecord['DATO']
                    self.polyclinicVisitsDict[dictKey]['KOLU'] = 1
                    self.polyclinicVisitsDict[dictKey]['KUSL'] = kusl
                for x in keys:
                    self.polyclinicVisitsDict[dictKey][x] = dbfRecord[x]

        dbfRecord.store() # U.dbf

        # ======================================================================================
        # N FILE
        if outgoingOrgCode and outgoingRefNumber \
                and not (outgoingOrgCode, outgoingRefNumber) in self.exportedDirections and forceInt(
            record.value('referralIsOutgoing')):
            dbfRecord = dbfN.newRecord()

            # код МО, оказавшей медицинскую помощь и выдавшей направление обязательное SPR01
            dbfRecord['CODE_MO'] = bookkeeperCode
            # policRefOrgId
            # номер направления, (ККККК_ХХХХХХХ) обязательное
            dbfRecord['NAPR_N'] = '%.5d_%s' % (
                outgoingOrgCode, outgoingRefNumber) if '_' not in outgoingRefNumber else outgoingRefNumber
            # outgoingRefNumber  # '%.5d_%.7d' % (outgoingOrgCode, outgoingRefNumber)

            # код МО, в которое направлен пациент обязательное SPR01
            dbfRecord['NAPR_MO'] = '%.5d' % forceInt(
                db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))

            # дата направления обязательное
            dbfRecord['NAPR_D'] = pyDate(forceDate(record.value('referralDate')))  # pyDate(endDate)

            # табельный номер сотрудника, выдавшего направление обязательное
            # i3393 P file personCode -> personRegionalCode
            # dbfRecord['DOC_TABN'] = forceString(record.value('personRegionalCode'))

            personId = forceRef(record.value('execPersonId'))
            dbfRecord['DOC_SS'] = formatSNILS(forceString(self.getPersonInfoById(personId).value('SNILS')))

            dbfRecord.store()
            self.exportedDirections.append((outgoingOrgCode, outgoingRefNumber))
        # ======================================================================================
        # R FILE
        referralId = forceRef(record.value('referralId'))
        if referralId and referralId not in self.exportedRIDs:
            NAZR = ""
            if forceInt(record.value('eventResultCode')) in [
                323, 324, 325, 334, 335, 336, 339, 340, 341, 345, 349, 350, 351, 355, 356
            ] and forceString(record.value('eventProfileCode')) in ['211', '232', '252', '261', '262']:

                referralType = forceInt(record.value('referralType'))
                referralClinicType = forceInt(record.value('referralClinicType'))
                referralOrgId = forceInt(record.value('policRefOrgId'))

                self.exportedRIDs.append(referralId)
                dbfRecord = dbfR.newRecord()
                # Уникальный номер записи о назначении лечащего врача используется для идентификации записи о назначении в пределах реестра, для повторных реестров должен совпадать с первоначальным номером
                dbfRecord['RID'] = referralId

                # код МО, оказавшей медицинскую помощь и выдавшей направление обязательное SPR01
                dbfRecord['CODE_MO'] = bookkeeperCode

                # номер реестра счетов
                dbfRecord['NS'] = self.edtRegistryNumber.value()

                # номер персонального счета
                dbfRecord['SN'] = eventId  # clientId

                u"""
                Коды:
                1 - направлен на консультацию в медицинскую организацию по месту прикрепления
                2 - направлен на консультацию в иную медицинскую организацию
                3 - направлен на обследование
                4 - направлен в дневной стационар
                5 - направлен на госпитализацию
                6 - направлен в реабилитационное отделение.
                """
                if referralType == 4 and referralOrgId == QtGui.qApp.currentOrgId():
                    NAZR += '1'
                elif referralType == 4:
                    NAZR += '2'
                if referralType == 3:
                    NAZR += '3'
                if referralType == 1 and referralClinicType == 2:
                    NAZR += '4'
                if referralType == 1 and referralClinicType == 1:
                    NAZR += '5'
                dbfRecord['NAZR'] = NAZR

                if '1' in NAZR or '2' in NAZR:
                    # специальность врача, к которому направлен за консультацией
                    dbfRecord['SPEC'] = forceString(record.value('referralSpec'))  # clientId

                if '3' in NAZR:
                    # вид назначенного обследования (п.3 примечаний)
                    dbfRecord['VID_OBS'] = forceString(record.value('referralExamType'))

                if '4' in NAZR or '5' in NAZR:
                    # профиль назначенной медицинской помощи
                    dbfRecord['PROFIL'] = forceString(record.value('referralMedProfile'))

                if '6' in NAZR:
                    # код профиля койки
                    dbfRecord['KPK'] = forceString(record.value('referralHospitalBedProfile'))

                dbfRecord.store()


class CExportPage2(QtGui.QWizardPage, Ui_ExportR23NativePage2):

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ExportR23NativeExportDir', homePath))
        self.edtDir.setText(exportDir)
        self.fileNameList = ['P', 'U', 'D', 'N']

    def isComplete(self):
        return self.pathIsValid

    def validatePage(self):
        isModern = False
        baseName = os.path.basename(self.parent.page1.getDbfBaseName(isModern))
        clearBaseName = os.path.basename(self.parent.page1.getDbfBaseName(False))
        tmpDir = forceStringEx(self.parent.getTmpDir())
        zipFileName = self.parent.page1.getZipFileName(isModern)
        zipFilePath = os.path.join(tmpDir,
                                   zipFileName)
        zf = ZipFile(zipFilePath, 'w', allowZip64=True)

        if self.parent.hasLFile:
            self.fileNameList.append('L')

        for fileName in self.fileNameList:
            filePath = os.path.join(tmpDir,
                                    fileName + baseName)
            zf.write(filePath, fileName + clearBaseName, ZIP_DEFLATED)
        filePath = os.path.join(tmpDir, os.path.basename("schet.html"))
        zf.write(filePath, "schet.html", ZIP_DEFLATED)
        if os.path.exists(os.path.join(tmpDir, os.path.basename("invoice.html"))):
            filePath = os.path.join(tmpDir, os.path.basename("invoice.html"))
            zf.write(filePath, "invoice.html", ZIP_DEFLATED)
        zf.close()

        dst = os.path.join(forceStringEx(self.edtDir.text()), zipFileName)
        success, result = QtGui.qApp.call(self, shutil.move, (zipFilePath, dst))

        if success:
            QtGui.qApp.preferences.appPrefs['ExportR23NativeExportDir'] = toVariant(self.edtDir.text())
            self.wizard().setAccountExposeDate()

        return success

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))

    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ОМС Краснодарского края',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
