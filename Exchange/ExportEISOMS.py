# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil
from PyQt4 import QtCore, QtGui
from collections import defaultdict

from PyQt4.QtCore import *

from Accounting.ServiceDetailCache import CServiceDetailCache
from Accounting.Utils import CTariff
from Events.Action import ActionServiceType, ActionStatus
from Registry.MIACExchange.Preferences import CMIACExchangePreferences
from Registry.MIACExchange.StattalonSender import CMIACStattalonSender
from Registry.Utils import formatAddress, getAddress, getClientAddress
from Ui_ExportEISOMSPage1 import Ui_ExportEISOMSPage1
from Ui_ExportEISOMSPage2 import Ui_ExportEISOMSPage2
from Utils import getClientRepresentativeInfo, setEIS_db
from library.Utils import MKBwithoutSubclassification, calcAgeInYears, calcAgeTuple, firstYearDay, forceBool, forceDate, \
    forceDateTime, forceDouble, forceInt, forceRef, forceString, forceStringEx, \
    formatSNILS, formatSex, getInfisCodes, getVal, nameCase, pyDate, smartDict, splitDocSerial, toVariant, trim
from library.crbcombobox import CRBComboBox, CRBModelDataCache
from library.dbfpy.dbf import CDbf, Dbf


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        number = forceString(accountRecord.value('number'))
    else:
        date = None
        number = ''
    return date, number, adviseDBFFileName(date, number)


def adviseDBFFileName(date, number):
    tmp = trim(''.join([c if c.isalnum() or '-_'.find(c)>=0 else ' ' for c in number]))
    return tmp.replace(' ','_')


def exportEISOMS(widget, accountId, accountItemIdList):
    try:
        setEIS_db()
    except:
        QtGui.qApp.logCurrentException()

    wizard = CExportEISOMSWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


def numberToWords(number):
    mapUnits = {1: u'Перв%',
                      2: u'Втор%',
                      3: u'Трет%',
                      4: u'Четверт%',
                      5: u'Пят%',
                      6: u'Шест%',
                      7: u'Седьм%',
                      8: u'Восьм%',
                      9: u'Девят%',
                      10: u'Десят%',
                      11: u'Одиннадц%',
                      12: u'Двенадц%',
                      13: u'Тринадц%',
                      14: u'Четырнадц%',
                      15: u'Пятнадц%',
                      16: u'Шестнадц%',
                      17: u'Семнадц%',
                      18: u'Восемнадц%',
                      19: u'Девятнадц%',
    }
    mapDecades = {
                      2: u'Двадцат%',
                      3: u'Тридцат%',
                      4: u'Сорок%',
                      5: u'Пятьдесят%',
                      6: u'Шестьдесят%',
                      7: u'Семьдесят%',
                      8: u'Восемьдесят%',
                      9: u'Девяност%',
                      }
    num = forceInt(number)
    if num < 1 or num > 99:
        return number
    elif num < 20:
        return mapUnits.get(num, number)
    else:
        dec = num/10
        units = num%10
        return mapDecades.get(dec) + mapUnits.get(units)


isUslDbfEmpty = True
isSluchDbfEmpty = True
isDirectDbfEmpty = True


class CExportEISOMSWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportEISOMSPage1(self)
        self.page2 = CExportEISOMSPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта в ЕИС.ОМС.ВМУ.АПУ')
        self.tmpDir = ''
        self.dbfFileName = ''

    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, fileName = getAccountInfo(accountId)
        self.dbfFileName = fileName
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменного файла "%s.dbf"' %(self.dbfFileName))

    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('eisoms')
        return self.tmpDir

    def getFullDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '.dbf')

    def getFullClientsDbfFileName(self):
        return os.path.join(self.getTmpDir(), 'pat_' + self.dbfFileName + '.dbf')

    def getUslDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '_V.dbf')

    def getDirectDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '_D.dbf')

    def getSluchDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '_add.dbf')

    def setAccountItemsIdList(self, accountItemIdList):
        self.page1.setAccountItemsIdList(accountItemIdList)

    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''

    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


class CExportEISOMSPage1(QtGui.QWizardPage, Ui_ExportEISOMSPage1):
    mapDocTypeToEIS = { '1' : '1', '14': '2', '3':'3', '2':'6', '5':'7', '6':'8', '16':'8' }
    mapEventOrderToEIS = {1: u'п', 2: u'э', 5: u'н'}
    reanimationActionTypes = ['431010', '431020', '431030', '431040', '431050', '431060',
                              '432010', '432020', '432030', '432040', '432050', '432060', '261344']
    streetTypeDict = {u'ул': 1,
                      u'пр-кт': 2,
                      u'ш': 3,
                      u'аллея': 4,
                      u'б-р': 5,
                      u'кв-л': 6,
                      u'пер': 7,
                      u'пл': 8,
                      u'проезд': 9,
                      u'туп': 10,
                      u'наб': 11,
                      u'линия': 12,
                      u'мкр': 13,
                      u'': 14}
    mapKladrCodeToIdRegion = {41: 93,
                              59: 92,
                              75: 94,
                              80: 94,
                              81: 92,
                              82: 93,
                              84: 24,
                              85: 38,
                              88: 24,
                              90: 52}
    mapKladrStrSocrToEis = { u'аллея':    u'ал.',
                             u'б-р':      u'б-р',
                             u'берег':    u'-',
                             u'вал':      u'-',
                             u'городок':	u'-',
                             u'д':        u'дорожка',
                             u'дор':      u'дор.',
                             u'ж/д_ст':   u'-',
                             u'канал':    u'-',
                             u'кв-л':     u'-',
                             u'км':       u'км',
                             u'коса':     u'-',
                             u'линия':    u'линия',
                             u'мост':     u'-',
                             u'наб':      u'наб.',
                             u'остров':   u'остров',
                             u'п':        u'-',
                             u'парк':     u'парк',
                             u'пер':      u'пер.',
                             u'переезд':  u'-',
                             u'пл':       u'пл.',
                             u'пл-ка':    u'-',
                             u'пр-кт':    u'пр.',
                             u'проезд':   u'пр-д',
                             u'проток':   u'-',
                             u'сад':      u'-',
                             u'сквер':    u'-',
                             u'спуск':    u'-',
                             u'ст':       u'-',
                             u'стр':      u'-',
                             u'тер':      u'-',
                             u'тракт':    u'-',
                             u'туп':      u'-',
                             u'ул':       u'ул.',
                             u'ш':        u'ш.'}
    mapReprType = { '01': 1,
                    '02': 1,
                    '03': 1,
                    '04': 1,
                    '05': 2,
                    '06': 2,
                    '07': 2,
                    '08': 2,
                    '09': 3,
                    '10': 4,
                    '11': 5

    }

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')
        self.MIACExchangePreferences = CMIACExchangePreferences()
        self.sendToMIACEnabled = self.MIACExchangePreferences.isValid()
        self.chkSendToMIAC.setChecked(self.sendToMIACEnabled and self.MIACExchangePreferences.sendByDefault)
        eisLpuId = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'EISOMSLpuId', ''))
        self.chkExportClients.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'EISOMSExportClients', False)))
        self.edtEisLpuId.setText(eisLpuId)
        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.currentOKATO = forceString(
            QtGui.qApp.db.translate('kladr.KLADR', 'CODE', QtGui.qApp.defaultKLADR(), 'OCATD')
        )
        self.currentProvinceOKATO = forceString(
            QtGui.qApp.db.translate('kladr.KLADR', 'CODE', QtGui.qApp.provinceKLADR(), 'OCATD')
        )
        self.eventIdList_Sluch = []
        self.eventIdList_Direct = []
        self.serviceDetailCache = CServiceDetailCache()
        self.profileCache = {}
        self.kindCache = {}
        self.typeCache = {}
        self.checkDuplicateEvents = {}
        self.eventRelegateOrgMiacCache = {}
        self._representativeInfoCache = {}
        self._refBooks = smartDict()
        self.processedServDatas = []

        self.curEventId = None
        self.curMovingActionData = {}
        self.curClinicalExaminationData = {}

        self.currentOrgMiac = QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode')
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.cmbPersonFormat.setCurrentIndex(forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'personalFormat', 1)))

        self.prevIsDayStationary = {}

        self.servIdsCounter = defaultdict(int)
        self.mainAccountItemMap = {}

    def validatePage(self):
        QtGui.qApp.preferences.appPrefs['personalFormat'] = toVariant(self.cmbPersonFormat.currentIndex())
        return True

    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkSendToMIAC.setEnabled(not flag and self.sendToMIACEnabled)

    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList

    def prepareToExport(self, ignoreConfirmation, exportClients, includeEvents, includeVisits,
                        includeActions, personFormat, exportUsl=True, exportSluch=True, exportDirect=True):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        self.curMovingActionData = {}
        self.curClinicalExaminationData = {}
        self.curEventId = None
        self.mainAccountItemMap = {}

        dbf = self.createDbf()
        clientsDbf = self.createClientsDbf() if exportClients else None
        uslDbf = self.createUslDbf() if exportUsl else None
        sluchDbf = self.createSluchDbf() if exportSluch else None
        directDbf = self.createDirectDbf() if exportDirect else None
        self.prepareRefBooks()
        query = self.createQuery(ignoreConfirmation, includeEvents, includeVisits, includeActions, personFormat)
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        if self.sendToMIACEnabled and self.chkSendToMIAC.isChecked():
            exporter = CMIACStattalonSender(self.wizard().getTmpDir(), self.MIACExchangePreferences.compress)
        else:
            exporter = None
        return dbf, clientsDbf, exporter, query, uslDbf, sluchDbf, directDbf

    def export(self, ignoreConfirmation, exportClients, includeEvents, includeVisits, includeActions, eisLpuId, personFormat):
        QtGui.qApp.call(self, self.exportInt, (ignoreConfirmation, exportClients, includeEvents, includeVisits, includeActions, eisLpuId, personFormat))
        self.setExportMode(False)
        if self.aborted:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))

    def exportInt(self, ignoreConfirmation, exportClients, includeEvents, includeVisits, includeActions, eisLpuId,
                  personFormat):
        dbf, clientsDbf, exporter, query, uslDbf, sluchDbf, directDbf = self.prepareToExport(ignoreConfirmation,
                                                                                  exportClients, includeEvents,
                                                                                  includeVisits, includeActions,
                                                                                  personFormat)
        if self.idList:
            processedClientIds = set()
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, clientsDbf, query.record(), eisLpuId, processedClientIds, personFormat, uslDbf, sluchDbf, directDbf)
        else:
            self.progressBar.step()

        dbf.close()
        if uslDbf is not None: uslDbf.close()
        if sluchDbf is not None: sluchDbf.close()
        if directDbf is not None: directDbf.close()
        if clientsDbf is not None: clientsDbf.close()

        self.postProcess(dbf.name)

        if exporter is not None:
            with CDbf(dbf.name, readOnly=True, encoding='cp866') as dbf:
                for dbfRecord in dbf:
                    exporter.writeRecord(dbfRecord)
            exporter.close()
            if not self.aborted:
                exporter.send(self.MIACExchangePreferences.address, self.MIACExchangePreferences.postBoxName)

    def createDbf(self):
        dbf = Dbf(self.wizard().getFullDbfFileName(), new=True, encoding='cp866')
        dbf.addField (
            ('SURNAME',     'C', 30),       # Фамилия пациента
            ('NAME1',       'C', 30),       # Имя пациента
            ('NAME2',       'C', 30),       # Отчество пациента
            ('BIRTHDAY',    'D'),           # Дата рождения
            ('SEX',         'C', 1),        # Пол (М/Ж)
            ('ORDER',       'C', 1),        # Признак экстренности случая лечения (если случай экстренный - принимает значение "э" или "Э")
            ('POLIS_S',     'C', 20),       # Серия полиса
            ('POLIS_N',     'C', 20),       # Номер полиса
            ('POLIS_W',     'C', 5),        # Код СМО, выдавшей полис (удалить)
            ('PAYER',       'C', 5),        # Код СМО, выдавшей полис?
            ('STREET',      'C', 5),       # Адрес пациента: код улицы
            ('STREETYPE',   'C', 2),        # Адрес пациента: тип улицы
            ('AREA',        'C', 3),        # Адрес пациента: код район
            ('HOUSE',       'C', 7),        # Адрес пациента: номер дома
            ('KORP',        'C', 2),        # Адрес пациента: корпус
            ('FLAT',        'C', 5),       # Адрес пациента: номер квартиры
            ('PROFILE',     'C', 30),        # Код профиля лечения
            ('PROFILENET',  'C', 1),        # Тип сети профиля (в - взрослая, д - детская)
            ('DATEIN',      'D'),           # Дата начала услуги
            ('DATEOUT',     'D'),           # Дата окончания услуги
            ('AMOUNT',      'N', 3,0),     #  Объем лечения
            ('DIAGNOSIS',   'C', 10),        # Код диагноза (6 - со звездой, нужно 5, - без звезды?)
            ('DIAG_PREF',   'C', 7),        # Код сопутствующего диагноза
            ('SEND',        'L'),           # Флаг обработки записи
            ('ERROR',       'C', 250),      # Описание ошибки
            ('TYPEDOC',     'C', 1),        # Тип документа
            ('SER1',        'C', 10),       # Серия документа, левая часть
            ('SER2',        'C', 10),       # Серия документа, левая часть
            ('NPASP',       'C', 10),       # Номер документа
            ('SERV_ID',     'N', 11,0),     # Идентификатор случая
            ('ID_IN_CASE',  'N', 3, 0),     # Порядковый номер записи в случае (в пределах одного SERV_ID)
            ('ID_PRVS',     'N', 11),       # Региональный код специальности врача
            ('IDPRVSTYPE',  'N', 6,0),      # код типа указанной услуги для КСГ
            ('PRVS_PR_G',   'N', 6,0),      # номер группы из справочника профилей ЗСКСГ
            ('ID_EXITUS',   'N', 11, 0),        # исход лечения
            ('ILLHISTORY',  'C', 20),       # история болезни (id клиента)
            ('CASE_CAST',   'N', 6,0),      # тип случая лечения
            ('AMOUNT_D',    'N', 3,0),      # кол-во дней (для случая МЭС ДСТАЦ при ЛПУ)
            ('ID_PRMP',     'N', 6,0),      # Код профиля по Классификатору профиля
            ('ID_PRMP_C',   'N', 6,0),      # Код профиля по Классификатору профиля для случая лечения
            ('DIAG_C',      'C', 10),        # Код диагноза для случая лечения
            ('DIAG_S_C',    'C', 10),        # Код сопутствующего диагноза для случая лечения
            ('DIAG_P_C',    'C', 10),        # Код первичного диагноза для случая лечения
            ('QRESULT',     'N', 6,0),      # Результат обращения за медицинской помощью
            ('ID_PRVS_C',   'N', 11,0),     # ID врачебной специальности для случая лечения
            ('ID_SP_PAY',   'N', 6,0),      # ID способа оплаты медицинской помощи
            ('ID_ED_PAY',   'N', 5,2),      # Количество единиц оплаты медицинской помощи
            ('ID_VMP',      'N', 6,0),      # ID вида медицинской помощи
            ('ID_DOC',      'C', 20),       # Идентификатор врача из справочника SPRAV_DOC.DBF (для услуги)
            ('ID_DEPT',     'C', 20),       # Идентификатор отделения МО из справочника SPRAV_DEPTS.DBF (для услуги)
            ('ID_DOC_C',    'C', 20),       # Идентификатор врача из справочника SPRAV_DOC.DBF (для случая)
            ('ID_DEPT_C',   'C', 20),       # Идентификатор отделения МО из справочника SPRAV_DEPTS.DBF (для случая)
            ('ID_LPU_D',    'N', 11, 0),    # Идентификатор ЛПУ, направившего на лечение (из справочника SPRAV_LPU.DBF)
            ('SNILS',       'C', 14),       # СНИЛС
            ('LONGADDR',    'C', 120),      # Длинный адрес
            ('ACC_ID',      'N', 8),        # Account.id
            ('ACCITEM_ID',  'N', 8),        # Account_Item.id
            ('CLIENT_ID',   'N', 8),        # Client.id
            ('PRIM',        'C', 255),      # примечание - возврат от страховщиков

            # Поля для диспансеризации
            ('IDSERVDATA',  'C', 11),       # Идентификатор пункта карты диспансеризации (Пусто)
            ('IDSERVMADE',  'N', 6),        # Идентификатор порядка выполнения пункта карты (Пусто)
            ('IDSERVLPU',   'C', 11),       # Идентификатор ЛПУ, выполнившего пункт карты (Пусто)
            # Конец полей для диспансеризации

            ('ID_GOAL',     'N', 6, 0),        # ID цели обращения для услуги (SPRAV_GOAL.DBF)
            ('ID_GOAL_C',   'N', 6, 0),        # ID цели обращения для случая (SPRAV_GOAL.DBF)
            ('ID_GOSP',     'N', 6, 0),        # Тип госпитализации (у нас всегда = 5)
            ('IDVIDVME',    'N', 6, 0),        # Идентификатор вида мед. вмешательства
            ('IDFORPOM',    'N', 6, 0),        # Идентификатор формы оказания помощи
            ('IDVIDHMP',    'N', 6),        # Идентификатор вида высокотехнологичной помощи (обязательно при CASE_CAST = 25)
            ('IDMETHMP',    'N', 6, 0),        # Идентификатор метода высокотехнологичной мед помощи (обязательно при CASE_CAST = 25)
            ('N_BORN',      'N', 1, 0),     # Порядковый номер новорожденного
            ('ID_PRVS_D',   'N', 6, 0),       # Идентификатор специальности направившего врача (Пусто)
            ('ID_GOAL_D',   'N', 6, 0),        # ID цели обращения при направлении (Пусто)
            ('ID_LPU',      'N', 11, 0),    # Идентификатор БД ЛПУ, в которую загружаются данные
            ('ID_FINT',     'N', 11, 0),       # Тип финансирования? (SPRAV_FIN_TYPE)
            ('ID_CASE',     'C', 20),       # Идентификатор случая в БД ЕИС (проставляется после принятия)
            ('ID_SERV',     'C', 20),       # Идентификатор услуги в БД ЕИС (проставляется после принятия)
            ('ID_TRANSF',   'N', 6, 0),     # Признак перевода (для случая) по умолчанию пусто (обязателен для случаев стационара КСГ и ВМП)
            ('ID_INCOMPL',  'N', 6, 0),     # Признак "Неполный объём" (для услуги) по умолчанию = 5
            ('ID_MAIN',     'N', 3, 0),     # Поле должно содержать идентификатор (поле ID_IN_CASE) главной услуги (для сопутствующих услуг).
            ('ID_LPU_RF',   'N', 11, 0),    # Идентификатор иногородней МО
            ('ID_LPU_P',    'N', 11, 0),    # Идентификатор подразделения МО (для услуги)
            ('ID_LPU_P_C',  'N', 11, 0),    # Идентификатор подразделения МО (для случая)
        )
        if self.chkDD.isChecked():
            dbf.addField(('ID_PAT_CAT',  'N', 10)) # Социальные статус пациента для выгрузки по диспансеризации
        return dbf

    def createClientsDbf(self):
        dbf = Dbf(self.wizard().getFullClientsDbfFileName(), new=True, encoding='cp866')
        dbf.addField(
            ('SURNAME',     'C', 30),       # Фамилия
            ('NAME',        'C', 30),       # Имя
            ('S_NAME',      'C', 30),       # Отчество
            ('BIRTHDAY',    'D'),           # Дата рождения
            ('SEX',         'C', 1),        # Пол
            ('ID_PAT_CAT',  'N', 6, 0),     # Статус
            ('DOC_TYPE',    'N', 2, 0),     # Тип документа
            ('SER_L',       'C', 10),       # Левая часть серии документа
            ('SER_R',       'C', 10),       # Правая часть серии документа
            ('DOC_NUMBER',  'C', 10),       # Номер документа
            ('SNILS',       'C', 14),       # СНИЛС
            ('C_OKSM',      'C', 3),        # Гражданство
            ('IS_SMP',      'L'),           # Признац "пациент СМП"
            ('POLIS_TYPE',  'C', 1),        # Тип полиса
            ('POLIS_S',     'C', 20),       # Серия полиса
            ('POLIS_N',     'C', 20),       # Номер полиса
            ('ID_SMO',      'N', 5, 0),     # СМО
            ('POLIS_BD',    'D'),           # Дата начала действия полиса
            ('POLIS_ED',    'D'),           # Дата окончания действия полиса
            ('ID_SMO_REG',  'N', 5, 0),     # Региональная СМО (для иногородних)
            ('ADDR_TYPE',   'C', 1),        # Тип адреса регистрации
            ('IDOKATOREG',  'N', 3, 0),     # Регион
            ('IDOBLTOWN',   'N', 4, 0),     # Не используется
            ('ID_PREFIX',   'N', 4, 0),     # Не используется
            ('ID_HOUSE',    'N', 8, 0),     # Идентификатор дома (для адресов СПБ, тип "г")
            ('HOUSE',       'C', 10),       # Номер дома (для типа "р")
            ('KORPUS',      'C', 5),        # Корпус (для типа "р")
            ('FLAT',        'C', 5),        # Квартира
            ('U_ADDRESS',   'C', 200),      # Неструктурированный адрес (для типа "п")
            ('KLADR_CODE',  'C', 13),       # Код КЛАДР (для типа "р")
            ('STREET',      'C', 150),      # Название улицы (для типа "р")
            ('IDSTRTYPE',   'N', 2, 0),     # Тип улицы (для типа "р")
            ('ADDRTYPE_L',  'C', 1),        # Тип адреса проживания
            ('OKATOREG_L',  'N', 3, 0),     # Регион
            ('OBLTOWN_L',   'N', 4, 0),     # Не используется
            ('PREFIX_L',    'N', 4, 0),     # Не используется
            ('ID_HOUSE_L',  'N', 8, 0),     # Идентификатор дома (для адресов СПб, тип "г")
            ('HOUSE_L',     'C', 10),       # Номер дома (для типа "р")
            ('KORPUS_L',    'C', 5),        # Корпус (для типа "р")
            ('FLAT_L',      'C', 5),        # Квартира
            ('U_ADDR_L',    'C', 200),      # Неструктурированный адрес (для типа "п")
            ('KLADR_L',     'C', 13),       # Код КЛАДР (для типа "р")
            ('STREET_L',    'C', 150),      # Название улицы (для типа "р")
            ('STRTYPE_L',   'N', 2, 0),     # Тип улицы (для типа "р")
            ('PLACE_WORK',  'C', 254),      # Место работы
            ('ADDR_WORK',   'C', 254),      # Адрес места работы
            ('ADDR_PLACE',  'C', 254),      # Место взятия
            ('REMARK',      'C', 254),      # Примечание
            ('B_PLACE',     'C', 100),      # Место рождения
            ('VNOV_D',      'N', 4, 0),     # Вес при рождении
            ('ID_G_TYPE',   'N', 2, 0),     # Тип представителя
            ('G_SURNAME',   'C', 30),       # Фамилия представителя
            ('G_NAME',      'C', 25),       # Имя представителя
            ('G_S_NAME',    'C', 25),       # Отчество представителя
            ('G_BIRTHDAY',  'D'),           # Дата рождения представителя
            ('G_SEX',       'C', 1),        # Пол представителя
            ('G_DOC_TYPE',  'N', 2, 0),     # Тип документа представителя
            ('C_DOC',       'N', 2, 0),     # Тип документа представителя
            ('G_SERIA_L',   'C', 6),        # Левая часть серии документа представителя
            ('G_SERIA_R',   'C', 2),        # Правая часть серии документа представителя
            ('G_DOC_NUM',   'C', 12),       # Номер документа представителя
            ('G_B_PLACE',   'C', 100),      # Место рождения представителя
            ('N_BORN',      'N', 1, 0),     # Порядковый номер новорожденного
            ('SEND',        'L'),           # Признак принят
            ('ERROR',       'C', 200),      # Описание ошибки
            ('ID_MIS',      'C', 20),       # Идентификатор пациента из внешних данных
            ('ID_PATIENT',  'C', 20),       # Идентификатор записи пациента в БД ЕИС (проставляется после принятия)
            ('LGOTS',       'C', 20),       # Льготы пациента (список ID через запятую)
        )
        return dbf

    # *_V file
    def createUslDbf(self):
        dbf = Dbf(self.wizard().getUslDbfFileName(), new=True, encoding='cp866')
        dbf.addField(
            ('ID_NMKL',     'N', 11, 0),    # Идентификатор чего-то
            ('SERV_ID',     'N', 11, 0),    # Идентификатор случая
            ('ID_IN_CASE',  'N', 3,  0),    # Порядковый номер записи в случае (в пределах одного SERV_ID)
            ('DATE_BEGIN',  'D'),           # Дата начала услуги
            ('DATE_END',    'D'),           # Дата окончания услуги
            ('V_MULTI',     'N', 6,  0),
            ('V_LONG_IVL',  'N', 6,  0),
            ('V_LONG_MON',  'N', 6,  0),
            ('ERROR',       'C', 200),
        )
        return dbf

    def createSluchDbf(self):
        dbf = Dbf(self.wizard().getSluchDbfFileName(), new=True, encoding='cp866')
        dbf.addField(
            ('SERV_ID',     'N', 11, 0),    # Идентификатор случая
            ('ID_OBJECT',   'N', 4, 0),
            ('OBJ_VALUE',   'C', 10),
            ('ERROR',       'C', 200),
        )
        return dbf

    # *_D file
    def createDirectDbf(self):
        dbf = Dbf(self.wizard().getDirectDbfFileName(), new=True, encoding='cp866')
        dbf.addField(
            ('SERV_ID',     'N', 11, 0),    # Идентификатор случая
            ('D_NUMBER',    'C', 20),       # Номер направления (талона)
            ('DATE_ISSUE',  'D'),           # Дата выдачи направления (талона)
            ('DATE_PLANG',  'D'),           # Дата планируемой госпитализации
            ('ID_D_TYPE',   'N', 11, 0),    # Тип направления (назначения)
            ('ID_D_GROUP',  'N', 11, 0),    # Группа направления
            ('ID_PRVS',     'N', 11, 0),    # Идентификатор специальности врача
            ('ID_OB_TYPE',  'N', 11, 0),    # Идентификатор вида обследования
            ('ID_PRMP',     'N', 11, 0),    # Идентификатор профиля медицинской помощи
            ('ID_B_PROF',   'N', 11, 0),    # Идентификатор профиля койки
            ('ERROR',       'C', 200)       # Описание ошибки
        )
        return dbf

    def prepareRefBooks(self):
        self._refBooks = smartDict()
        refBooks = self._refBooks
        db = QtGui.qApp.db

        refBooks.rbEventGoal = {}
        goals = refBooks.rbEventGoal
        for goalRecord in db.getRecordList('rbEventGoal'):
            goal = smartDict()
            goal.code = forceString(goalRecord.value('code'))
            goal.regionalCode = forceString(goalRecord.value('regionalCode'))
            goal.federalCode = forceString(goalRecord.value('federalCode'))
            goal.name = forceString(goalRecord.value('name'))
            goals[forceRef(goalRecord.value('id'))] = goal

        refBooks.rbMedicalAidUnit = {}
        units = refBooks.rbMedicalAidUnit
        for unitRecord in db.getRecordList('rbMedicalAidUnit'):
            unit = smartDict()
            unit.code = forceString(unitRecord.value('code'))
            unit.regionalCode = forceString(unitRecord.value('regionalCode'))
            unit.federalCode = forceString(unitRecord.value('federalCode'))
            unit.name = forceString(unitRecord.value('name'))
            units[forceRef(unitRecord.value('id'))] = unit

    def getRefBookValue(self, refBookName, itemId):
        return self._refBooks.get(refBookName, {}).get(itemId, smartDict())

    def createQuery(self, ignoreConfirmation, includeEvents, includeVisits, includeActions, personFormat):
        db = QtGui.qApp.db

        tableAccountItem = db.table('Account_Item')

        tableCitizenSocStatus = db.table('ClientSocStatus').alias('CitizenStatusClass')
        tableSocStatusClass = db.table('rbSocStatusClass')

        if includeEvents and includeVisits and includeActions:
            includeCond = '1'
        else:
            includeCondList = []
            if includeEvents:
                includeCondList.append('Account_Item.visit_id IS NULL AND Account_Item.action_id IS NULL')
            if includeVisits:
                includeCondList.append('Account_Item.visit_id IS NOT NULL AND Account_Item.action_id IS NULL')
            if includeActions:
                includeCondList.append('Account_Item.visit_id IS NULL AND Account_Item.action_id IS NOT NULL')
            if includeCondList:
                includeCond = db.joinOr(includeCondList)
            else:
                includeCond = '0'

        citizenshipSocStatusClassTopId = db.translate(tableSocStatusClass, tableSocStatusClass['flatCode'], 'citizenship', 'id')
        socStatusClassId = forceRef(db.translate(tableSocStatusClass, tableSocStatusClass['flatCode'], 'socStatus', 'id'))
        benefitSocStatusClassId = forceRef(db.translate(tableSocStatusClass, tableSocStatusClass['flatCode'], 'benefits', 'id'))
        citizenshipSocStatusClassesIdList = db.getDescendants(tableSocStatusClass, 'group_id', citizenshipSocStatusClassTopId)
        receivedATid = forceInt(db.translate('ActionType', 'flatCode', 'received', 'id'))
        movingCurrOrgStructAPTQuery = db.query(u'''SELECT ActionPropertyType.id FROM ActionType INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id WHERE ActionType.deleted = 0 AND ActionPropertyType.deleted = 0 AND ActionType.flatCode LIKE 'moving' AND ActionPropertyType.name LIKE 'Отделение пребывания' ''')
        if movingCurrOrgStructAPTQuery.first():
            movingCurrOrgStructAPTid = forceInt(movingCurrOrgStructAPTQuery.record().value(0))
        else:
            movingCurrOrgStructAPTid = 0

        cond = [includeCond,
                tableAccountItem['id'].inlist(self.idList)
                ]

        finalDiagnosisId = forceRef(db.translate('rbDiagnosisType', 'code', '1', 'id'))

        # TODO:skkachaev: Заджоинена уже 61 таблица. Это максимум для mysql. Больше джоинить нельзя. Только подзапросами.
        # TODO:skkachaev: Надо бы и это декомпозировать. В первую очередь вынести все сложные подзапросы и джоины с пропертями
        stmt = u"""
            SELECT
              Account_Item.id        AS accountItem_id,
              Account_Item.master_id AS account_id,
              Account_Item.event_id  AS event_id,
              Account_Item.visit_id  AS visit_id,
              Account_Item.action_id AS action_id,
              Event.client_id        AS client_id,
              Event.order            AS eventOrder,
              Event.MES_id           AS MES_id,
              Event.externalId      as externalId,
              rbMedicalAidKind.code  AS medicalAidKindCode,
              rbMedicalAidType.code  AS medicalAidTypeCode,
              Client.lastName        AS lastName,
              Client.firstName       AS firstName,
              Client.patrName        AS patrName,
              Client.birthDate       AS birthDate,
              Client.sex             AS sex,
              Client.SNILS           AS SNILS,
              Client.notes           AS clientNotes,
              ClientPolicy.serial    AS policySerial,
              ClientPolicy.number    AS policyNumber,
              ClientPolicy.begDate   AS policyBegDate,
              ClientPolicy.endDate   AS policyEndDate,
              rbPolicyKind.regionalCode AS policyKindRegionalCode,
              Insurer.infisCode      AS policyInsurer,
              Insurer.miacCode       AS policyInsurerEisId,
              Insurer.area           AS policyInsurerArea,
              CitizenStatusType.code   AS citizenship,
              rbSocStatusType.regionalCode   AS idPatCat,
              rbSocStatusType.name   AS socStatusName,
              BenefitType.regionalCode AS benefitTypeRegionalCode,
              group_concat(BenefitsSST.regionalCode) AS clientBenefitsCodes,
              ClientDocument.serial  AS documentSerial,
              ClientDocument.number  AS documentNumber,
              rbDocumentType.code    AS documentType,
              rbDocumentType.regionalCode AS documentRegionalCode,
              IF(Account_Item.service_id IS NOT NULL, rbItemService.id, rbVisitService.id) AS service_id,
              (
                  SELECT
                      rcc.code
                  FROM
                      rbCaseCast AS rcc
                      INNER JOIN rbService s ON rcc.id = s.caseCast_id
                  WHERE
                      s.id = IF(Account_Item.service_id IS NOT NULL, rbItemService.id, rbVisitService.id)
              ) AS visitServiceCaseCastCode,
              visitPerson.id AS visitPersonId,
              Diagnosis.MKB          AS MKB,
              Action.MKB             AS actionMKB,
              MKB_Tree.Prim               AS prim,
              IF(EventType.code IN ('80/5', '80/4'), IF(Diagnosis_PC.MKB, Diagnosis_PC.MKB, Action.MKB), '')  AS MKB_PC,
              DATE(IF(Account_Item.visit_id IS NOT NULL, Visit.date,
                      IF(Account_Item.action_id IS NOT NULL, Action.begDate, Event.setDate))) AS begDate,
              DATE(IF(Account_Item.visit_id IS NOT NULL, Visit.date,
                      IF(Account_Item.action_id IS NOT NULL, Action.endDate, Event.execDate))) AS endDate,
              Account_Item.amount    AS amount,
              rbDiagnosticResult.regionalCode AS diagnosticResultCode,
              EventResult.regionalCode AS eventResultCode,
              Event.execPerson_id AS eventExecPerson_id, # THAT WAS AT THE BEGINNING. NEXT LINE INTRODUCED FOR THE ABILITY TO CHOOSE DOCTOR'S ID/CODE/etc. MAY CAUSE PROBLEMS..
              eventPerson.%(personFormat)s AS eventPerson_id,
              eventPerson.speciality_id AS eventSpeciality_id,
              rbEventSpeciality.regionalCode AS eventSpecialityCode,
              Contract_Tariff.tariffType AS tariffType,
              Contract_Tariff.unit_id as unitId,
              IF(Account_Item.visit_id IS NOT NULL, visitPerson.%(personFormat)s,
                 IF( Account_Item.action_id IS NOT NULL, actionPerson.%(personFormat)s, eventPerson.%(personFormat)s)
                ) AS person_id,
              rbSpeciality.id        AS speciality_id,
              rbSpeciality.regionalCode AS specialityCode,
              rbActionSetSpeciality.regionalCode AS actionSetSpecialityCode,
              Event.relegateOrg_id AS relegateOrg_id,
              EmergencyCall.numberCardCall as numberCardCall,
              EmergencyCall.KLADRStreetCode as emergKLADRStreetCode,
              EmergencyCall.house as emergHouse,
              EmergencyCall.build as emergBuild,
              EmergencyCall.flat as emergFlat,
              EmergencyCall.address_freeInput as emergLongAddr,
              EmergencyCall.finishServiceDate AS emergFinishServiceDate,
              ActionOrganisation.miacCode as actionOrgEisId,
              ActionOrganisation.OKATO as actionOrgOKATO,
              ActionOrganisation.infisCode as actionOrgInfisCode,
              Action.status as actionStatus,
              Action.org_id as actionOrgId,
              Action.begDate as actionBegDate,
              Action.endDate as actionEndDate,
              Event.setDate as eventSetDate,
              Event.execDate as eventExecDate,
              Event.goal_id as goal,
              EventType.code as eventTypeCode,
              rbEventTypePurpose.regionalCode as purposeRegionalCode,
              Client.weight,
              ActionType.flatCode       as atFlatCode,
              ActionType.code           as atCode,
              ActionType.serviceType    as atServiceType,
              Action.MES_id     as actionMES_id,
              Action.person_id  as actionPerson_id,
              MovingCurrOrgStructure.hasDayStationary,
              MovingCurrOrgStructure.type as movingOSType,
              MovingResultAPS.value as MovingResult,
              HospReferralOrganisation.miacCode as hospReferralOrgEisCode,
              IF (MovingCurrOrgStructure.infisInternalCode LIKE '', MovingCurrOrgStructure.infisCode, MovingCurrOrgStructure.infisInternalCode) as movingCurrOrgStructCode,
              EventType.caseCast_id,
              rbHighTechCureKind.regionalCode as hmpKindRegionalCode,
              rbHighTechCureMethod.regionalCode as hmpMethodRegionalCode,
              (SELECT rbSpeciality.regionalCode FROM Referral INNER JOIN rbSpeciality ON rbSpeciality.id = Referral.speciality_id WHERE Referral.id = Event.referral_id) as referralSpecialityRegCode,
              (SELECT Event_LittleStranger.currentNumber FROM Event_LittleStranger WHERE Event_LittleStranger.id = Event.littleStranger_id) as nborn,
              IF(ActionType.flatCode = 'moving', Action.id = (SELECT tmpAction.id FROM Action as tmpAction WHERE tmpAction.event_id = Action.event_id AND tmpAction.deleted = 0 AND tmpAction.actionType_id = ActionType.id ORDER BY tmpAction.begDate DESC LIMIT 1), 0) as lastMoving,
              (
                SELECT
                    substring_index(APR.value, ':', 1)
                FROM Action AType
                    INNER JOIN ActionType ATType ON AType.actionType_id = ATType.id AND ATType.flatCode = 'received'
                    INNER JOIN ActionPropertyType APTType ON ATType.id = APTType.actionType_id AND APTType.name LIKE 'кем доставлен'
                    INNER JOIN ActionProperty AP ON AType.id = AP.action_id AND APTType.id = AP.type_id
                    INNER JOIN ActionProperty_Reference APR ON AP.id = APR.id
                WHERE
                    AType.event_id = Event.id AND AType.deleted = 0
                LIMIT 1
              ) AS transfCode,
              EventResult.regionalCode AS eventResultRegionalCode
            FROM Account_Item
            LEFT JOIN Account ON Account.id = Account_Item.master_id
            LEFT JOIN Contract ON Contract.id = Account.contract_id
            LEFT JOIN rbFinance ON rbFinance.id = Contract.finance_id
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id  = Event.eventType_id
            LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
            LEFT JOIN rbMedicalAidKind ON rbMedicalAidKind.id = EventType.medicalAidKind_id
            LEFT JOIN rbMedicalAidType ON rbMedicalAidType.id = EventType.medicalAidType_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN Event PolicyEvent ON PolicyEvent.id = IFNULL(Event.id, IFNULL(Action.event_id, Visit.event_id))
            LEFT JOIN ClientPolicy ON ClientPolicy.id = PolicyEvent.clientPolicy_id
            LEFT JOIN rbPolicyKind ON rbPolicyKind.id = ClientPolicy.policyKind_id
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN ClientSocStatus AS CitizenStatusClass ON CitizenStatusClass.client_id = Client.id
                                                AND %(citizenStatusClassCond)s
            LEFT JOIN rbSocStatusType AS CitizenStatusType ON CitizenStatusType.id = CitizenStatusClass.socStatusType_id
            LEFT JOIN ClientSocStatus ON ClientSocStatus.id = (SELECT css.id
                                                                FROM ClientSocStatus as css
                                                                INNER JOIN rbSocStatusType rsst ON rsst.id = css.socStatusType_id
                                                                WHERE css.client_id = Client.id
                                                                -- В рамках задачи 818 принято ID_PAT_CAT заполнять числовым региональным кодом типа статуса
                                                                    AND rsst.regionalCode RLIKE '^[[:digit:]]+$'
                                                                    AND ((css.begDate <= Event.setDate AND css.endDate >= Event.setDate) OR css.begDate IS NULL)
                                                                    AND css.socStatusClass_id = %(socStatusClassId)s -- Класс "социальный статус"
                                                                    AND css.deleted = 0
                                                                ORDER BY css.begDate DESC, rsst.id DESC     -- Если есть дата - берем самый последний подходящий соц. статус. Если нет - берем с максимальным id типа соц. статуса.
                                                                LIMIT 1)
            LEFT JOIN rbSocStatusType ON rbSocStatusType.id = ClientSocStatus.socStatusType_id
            LEFT JOIN rbSocStatusClass BenefitsSSC ON BenefitsSSC.flatCode = 'benefits'
            LEFT JOIN ClientSocStatus BenefitsCSS ON BenefitsCSS.client_id = Client.id AND BenefitsCSS.socStatusClass_id = BenefitsSSC.id AND BenefitsCSS.deleted = 0
                       AND (BenefitsCSS.begDate IS NULL OR BenefitsCSS.begDate = '0000-00-00' OR BenefitsCSS.begDate <= Event.setDate)
                       AND (BenefitsCSS.endDate IS NULL OR BenefitsCSS.endDate = '0000-00-00' OR BenefitsCSS.endDate >= Event.setDate)
            LEFT JOIN rbSocStatusType BenefitsSST ON BenefitsSST.id = BenefitsCSS.socStatusType_id
            LEFT JOIN ClientDocument ON
                ClientDocument.client_id = Client.id AND
                ClientDocument.id = (
                    SELECT MAX(CD.id)
                    FROM   ClientDocument AS CD
                    LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                    LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                    WHERE  rbDTG.code = '1' AND CD.client_id = Client.id AND CD.deleted = 0)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN Person AS visitPerson  ON visitPerson.id  = Visit.person_id
            LEFT JOIN Person AS actionPerson ON actionPerson.id = Action.person_id
            LEFT JOIN Person AS actionSetPerson ON actionSetPerson.id = Action.setPerson_id
            LEFT JOIN Person AS eventPerson  ON eventPerson.id  = Event.execPerson_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbSpeciality ON rbSpeciality.id = IF(Account_Item.visit_id IS NOT NULL, visitPerson.speciality_id,
                                               IF( Account_Item.action_id IS NOT NULL, actionPerson.speciality_id, eventPerson.speciality_id))
            LEFT JOIN rbSpeciality AS rbEventSpeciality ON rbEventSpeciality.id = IF(ActionType.flatCode = 'moving', actionPerson.speciality_id, eventPerson.speciality_id)
            LEFT JOIN rbSpeciality AS rbActionSetSpeciality ON rbActionSetSpeciality.id = actionSetPerson.speciality_id
            LEFT JOIN Diagnostic ON (Diagnostic.event_id = Account_Item.event_id AND Diagnostic.deleted = 0)
            LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN Diagnostic AS Diagnostic_PC ON Diagnostic_PC.event_id = Event.id AND Diagnostic_PC.deleted = 0 AND Diagnostic_PC.diagnosisType_id = %(finalDiagnosisId)d
            LEFT JOIN Diagnosis AS Diagnosis_PC ON Diagnostic_PC.diagnosis_id = Diagnosis_PC.id
            LEFT JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id

            LEFT JOIN ActionPropertyType MovingResultAPT ON MovingResultAPT.actionType_id = ActionType.id AND MovingResultAPT.name = 'результат'
            LEFT JOIN ActionProperty MovingResultAP ON MovingResultAP.action_id = Action.id AND MovingResultAP.type_id = MovingResultAPT.id
            LEFT JOIN ActionProperty_String MovingResultAPS ON MovingResultAPS.id = MovingResultAP.id
            -- Для определения направившей организации при госпитализации
            LEFT JOIN Action AS ReceivedAction ON ReceivedAction.event_id = Event.id AND ReceivedAction.deleted = 0
                                                    AND ReceivedAction.actionType_id = %(receivedAT)s
            LEFT JOIN ActionPropertyType AS ReferralAPT ON ReferralAPT.actionType_id = %(receivedAT)s
                                                        AND ReferralAPT.name = 'Кем направлен' AND ReferralAPT.deleted = 0
            LEFT JOIN ActionProperty AS ReferralAP ON ReferralAP.action_id = ReceivedAction.id AND ReferralAP.type_id = ReferralAPT.id
            LEFT JOIN ActionProperty_Organisation AS ReferralAPO ON ReferralAPO.id = ReferralAP.id
            LEFT JOIN Organisation AS HospReferralOrganisation ON HospReferralOrganisation.id = ReferralAPO.value AND HospReferralOrganisation.deleted = 0
            -- Для Для определения какого-то там отделения
            LEFT JOIN ActionProperty OrgStructAP ON OrgStructAP.action_id = Action.id AND OrgStructAP.type_id = %(movingCurrOSid)d AND OrgStructAP.deleted = 0
            LEFT JOIN ActionProperty_OrgStructure OrgStructAPOS ON OrgStructAPOS.id = OrgStructAP.id
            LEFT JOIN OrgStructure MovingCurrOrgStructure ON MovingCurrOrgStructure.id = OrgStructAPOS.value
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN Contract_Tariff ON Contract_Tariff.id = Account_Item.tariff_id
            LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
            LEFT JOIN Organisation AS ActionOrganisation ON ActionOrganisation.id = IF(Action.org_id IS NOT NULL, Action.org_id, Event.relegateOrg_id)
            LEFT JOIN rbHighTechCureKind ON rbHighTechCureKind.id = IF(Action.hmpKind_id IS NULL, Event.hmpKind_id, Action.hmpKind_id)
            LEFT JOIN rbHighTechCureMethod ON rbHighTechCureMethod.id = IF(Action.hmpMethod_id IS NULL, Event.hmpMethod_id, Action.hmpMethod_id)
            LEFT JOIN rbSocStatusType BenefitType ON BenefitType.id = (SELECT rsst.id
                                                                FROM ClientSocStatus as css
                                                                INNER JOIN rbSocStatusType rsst ON rsst.id = css.socStatusType_id
                                                                WHERE css.client_id = Client.id
                                                                    AND ((css.begDate <= Event.setDate AND css.endDate >= Event.setDate) OR css.begDate IS NULL)
                                                                    AND css.socStatusClass_id = %(benefitSocStatusClassId)s -- Класс "социальный статус"
                                                                    AND css.deleted = 0
                                                                ORDER BY css.begDate DESC, rsst.id DESC     -- Если есть дата - берем самый последний подходящий соц. статус. Если нет - берем с максимальным id типа соц. статуса.
                                                                LIMIT 1)
            WHERE
                (Account_Item.visit_id IS NOT NULL
                 OR rbItemService.eisLegacy
                 OR (Account_Item.event_id IS NOT NULL AND (Event.MES_id IS NOT NULL OR EventType.service_id IS NOT NULL))
                )
            AND Account_Item.reexposeItem_id IS NULL
            AND ( %(ignoreConfirmation)d
                 OR Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND
             (IF(Contract_Tariff.tariffType = 12,
                         Account_Item.visit_id IS NOT NULL AND (rbDiagnosisType.code IN ('1', '2') OR rbDiagnosisType.id IS NULL),
                         Diagnostic.person_id = Visit.person_id AND rbDiagnosisType.code IN ('1', '2')
                  )
                 OR
                 (Account_Item.visit_id IS NULL AND Diagnostic.id IN (
                    SELECT D1.id
                    FROM Diagnostic AS D1 LEFT JOIN rbDiagnosisType AS DT1 ON DT1.id = D1.diagnosisType_id
                    WHERE D1.event_id = Account_Item.event_id AND
                    DT1.code = (SELECT MIN(DT2.code)
                              FROM Diagnostic AS D2 LEFT JOIN rbDiagnosisType AS DT2 ON DT2.id = D2.diagnosisType_id
                              WHERE D2.event_id = Account_Item.event_id)
                    ))
                OR (rbEventTypePurpose.regionalCode = '6')
                )
            AND %(otherCond)s
        GROUP BY Account_Item.id
        ORDER BY Client.id,
                Event.id,
                DATE(Action.begDate),
                Contract_Tariff.tariffType = 9 DESC,
                IF(ActionType.flatCode = 'moving', 0, 1)
        """ % {'personFormat': personFormat,
               'ignoreConfirmation': (1 if ignoreConfirmation else 0),
               'socStatusClassId': socStatusClassId if socStatusClassId else 0,
               'citizenStatusClassCond': tableCitizenSocStatus['socStatusClass_id'].inlist(citizenshipSocStatusClassesIdList),
               'otherCond': db.joinAnd(cond),
               'finalDiagnosisId': finalDiagnosisId,
               'receivedAT': receivedATid,
               'movingCurrOSid': movingCurrOrgStructAPTid,
               'benefitSocStatusClassId': benefitSocStatusClassId if benefitSocStatusClassId else 0,
               }
        query = db.query(stmt)
        return query

    def getAddrRecord(self, clientId, adrType):
        db = QtGui.qApp.db
        stmt = '''
            SELECT
                kladr.STREET.NAME AS streetName, kladr.STREET.SOCR AS streetType,
                AddressHouse.number AS number, AddressHouse.corpus AS corpus, AddressHouse.KLADRCode,
                Address.flat AS flat, Address.id AS addressId, ClientAddress.freeInput AS freeInput,
                AddressHouse.KLADRStreetCode
            FROM ClientAddress
            LEFT JOIN Address ON Address.id = ClientAddress.address_id
            LEFT JOIN AddressHouse ON AddressHouse.id = Address.house_id
            LEFT JOIN kladr.STREET ON kladr.STREET.CODE = AddressHouse.KLADRStreetCode
            WHERE
                ClientAddress.client_id = %d AND
                ClientAddress.id = (
                    SELECT MAX(CA.id)
                    FROM ClientAddress AS CA
                    WHERE  CA.type = %d AND CA.client_id = %d)
        ''' % (clientId, adrType, clientId)
        query = db.query(stmt)
        if query.next():
            return query.record()
        else:
            return None

    def getEmergAreaAndStreet(self, house, build, KLADRStreetCode, KLADRCode = '7800000000000'):
        db = QtGui.qApp.db
        area, region, npunkt, street, streettype = getInfisCodes(
            KLADRCode, KLADRStreetCode, house, build)
        street = ''
        streetType = ''
        if not KLADRStreetCode:
            return area, street, streetType
        stmt = '''
            SELECT
                kladr.STREET.NAME AS streetName, kladr.STREET.SOCR AS streetType
            FROM kladr.STREET
            WHERE kladr.STREET.CODE = %s''' % KLADRStreetCode
        query = db.query(stmt)
        if query.next():
            record = query.record()
            street = forceString(record.value('streetName'))
            streetType = forceString(record.value('streetType'))
        return area, street, streetType

    def formatEmergAddr(self, emergStreet, emergStreetType, emergHouse, emergBuild, emergFlat):
        array = []
        result = u''
        if emergStreet and emergStreetType:
            array.append(u'%s %s.' % (emergStreet, emergStreetType))
        elif emergStreet:
            array.append(u'%s' % emergStreet)
        if emergHouse:
            array.append(u'д. %s' % emergHouse)
        if emergBuild:
            array.append(u'к. %s' % emergBuild)
        if emergFlat:
            array.append(u'кв. %s' % emergFlat)
        if array:
            array = [u'Санкт-Петербург'] + array
            result = u', '.join(array)
        return result

    def getAreaAndRegion(self, clientId, adrType):
        clientAddressRecord = getClientAddress(clientId, adrType)
        if clientAddressRecord:
            address = getAddress(clientAddressRecord.value('address_id'))
            area, region, npunkt, street, streettype = getInfisCodes(
                address.KLADRCode, address.KLADRStreetCode,
                address.number, address.corpus)
            return area, region
        return '', ''

    def getEventVisitsCircumstances(self, eventId, mesId):
        result = []
        db = QtGui.qApp.db
        stmt = u'''
            SELECT DATE(Visit.date)   AS date,
            Person.speciality_id      AS speciality_id,
            rbSpeciality.regionalCode AS specialityCode,
            mmv.visitType_id          AS prvsTypeIdRequired,
            mVT.id                    AS prvsTypeIdPresent,
            mmv.groupCode             AS prvsGroup,
            mmv.averageQnt            AS averageQnt,
            Visit.id                  AS visit_id,
            IF(mmv.visitType_id=mVT.id, 0, 1) AS visitTypeErr
            FROM Visit
            LEFT JOIN Person ON Person.id  = Visit.person_id
            LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
            LEFT JOIN rbVisitType  ON rbVisitType.id = Visit.visitType_id
            LEFT JOIN mes.mrbVisitType  AS mVT  ON rbVisitType.code = mVT.code
            LEFT JOIN mes.mrbSpeciality AS mS   ON mS.regionalCode = rbSpeciality.regionalCode
            LEFT JOIN mes.MES_visit     AS mmv  ON mmv.speciality_id = mS.id
            WHERE Visit.deleted = 0 AND Visit.event_id = %d AND mmv.master_id = %d
            ORDER BY visitTypeErr, mmv.groupCode, Visit.date
        ''' % (eventId, mesId)

        query = db.query(stmt)
        groupAvailable = {}
        countedVisits = set()
        while query.next():
            record = query.record()
            visitId = forceRef(record.value('visit_id'))
            if visitId not in countedVisits:
                date = forceDate(record.value('date'))
                specialityId = forceRef(record.value('speciality_id'))
                specialityCode = forceInt(record.value('specialityCode'))
                prvsTypeId = forceInt(record.value('prvsTypeIdRequired'))
                prvsGroup = forceInt(record.value('prvsGroup'))
                #averageQnt = forceInt(record.value('averageQnt'))
                #available = groupAvailable.get(prvsGroup, averageQnt)
                #if available > 0:
                #    groupAvailable[prvsGroup] = available-1
                #    result.append((date, date, specialityId, specialityCode, prvsTypeId, prvsGroup))
                #    countedVisits.add(visitId)
                result.append((date, date, specialityId, specialityCode, prvsTypeId, prvsGroup))
                countedVisits.add(visitId)
        return result

    def getVisitCountByEvent(self, eventId):
        db = QtGui.qApp.db
        tblVisit = db.table('Visit')
        return len(db.getRecordList(tblVisit, tblVisit['id'], [tblVisit['event_id'].eq(eventId), tblVisit['deleted'].eq(0)]))

    def getMiacCodeByPerson(self, personId):
        db = QtGui.qApp.db
        tblOrgStructure = db.table('OrgStructure')
        tblPerson = db.table('Person')
        if personId:
            recPerson = db.getRecordEx(tblPerson, tblPerson['orgStructure_id'], tblPerson['id'].eq(personId))
            if recPerson:
                recOrgStructure = db.getRecordEx(tblOrgStructure,
                                                 [tblOrgStructure['miacCode'], tblOrgStructure['parent_id']],
                                                 tblOrgStructure['id'].eq(forceInt(recPerson.value('orgStructure_id'))))
                if recOrgStructure:
                    while not forceString(recOrgStructure.value('miacCode')) and forceInt(recOrgStructure.value('parent_id')):
                        recOrgStructure = db.getRecordEx(tblOrgStructure,
                                                         [tblOrgStructure['miacCode'], tblOrgStructure['parent_id']],
                                                         tblOrgStructure['id'].eq(forceInt(recOrgStructure.value('parent_id'))))
                    if recOrgStructure:
                        return forceRef(recOrgStructure.value('miacCode'))
                else:
                    return None
            else:
                return None
        return None

    @staticmethod
    def getMainAccountItemForOperation(accountId, eventId):
        u"""
        Для действия с типом услуги "операция" главная услуга определяется по приоритету:
        1) услуга по МЭС (заполнено Event.MES_id)
        2) первый Visit
        :return: AccountItem.id
        """
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        tableEvent = db.table('Event')
        tableEventAI = tableAccountItem.alias('EventAI')
        tableVisit = db.table('Visit')
        tableVisitAI = tableAccountItem.alias('VisitAI')

        table = tableEvent
        table = table.leftJoin(tableEventAI, [tableEventAI['master_id'].eq(accountId),
                                              tableEventAI['event_id'].eq(tableEvent['id']),
                                              tableEventAI['action_id'].isNull(),
                                              tableEventAI['visit_id'].isNull(),
                                              tableEventAI['deleted'].eq(0)])
        table = table.leftJoin(tableVisitAI, [tableVisitAI['master_id'].eq(accountId),
                                              tableVisitAI['event_id'].eq(tableEvent['id']),
                                              tableVisitAI['visit_id'].isNotNull(),
                                              tableVisitAI['deleted'].eq(0)])
        table = table.leftJoin(tableVisit, tableVisit['id'].eq(tableVisitAI['visit_id']))
        cols = [
            db.if_(tableEvent['MES_id'].isNotNull(),
                   tableEventAI['id'],
                   tableVisitAI['id']).alias('id')
        ]
        cond = [
            tableEvent['id'].eq(eventId)
        ]
        order = [
            tableVisit['date']
        ]
        rec = db.getRecordEx(table, cols, cond, order)
        return forceRef(rec.value('id')) if rec else None

    def getAddressInfo(self, record):
        clientId = forceInt(record.value('client_id'))
        emergBuild = forceString(record.value('emergBuild'))
        emergFlat = forceString(record.value('emergFlat'))
        emergHouse = forceString(record.value('emergHouse'))
        emergKLADRStreetCode = forceString(record.value('KLADRStreetCode'))

        street = ''
        streetType = ''
        area = ''
        house = ''
        corpus = ''
        flat = ''
        longAddress = ''
        adrRecord = self.getAddrRecord(clientId, 0)
        adrType = 0
        if not adrRecord:
            adrRecord = self.getAddrRecord(clientId, 1)
            adrType = 1
        if adrRecord:
            KLADRCode = forceString(adrRecord.value('KLADRCode'))
            if KLADRCode[:2] == '78':
                street = forceString(adrRecord.value('streetName'))  # Адрес пациента: код улицы
                streetType = forceString(adrRecord.value('streetType'))  # Адрес пациента: тип улицы
                house = forceString(adrRecord.value('number'))  # Адрес пациента: номер дома
                corpus = forceString(adrRecord.value('corpus'))  # Адрес пациента: корпус
                flat = forceString(adrRecord.value('flat'))  # Адрес пациента: номер квартиры
            else:
                street = '*'
            addressId = forceInt(adrRecord.value('addressId'))
            longAddress = formatAddress(addressId)
        emergArea, emergStreet, emergStreetType = self.getEmergAreaAndStreet(emergHouse, emergBuild, emergKLADRStreetCode)
        emergLongAddr = self.formatEmergAddr(emergStreet, emergStreetType, emergHouse, emergBuild, emergFlat)
        if not emergLongAddr:
            emergLongAddr = forceString(record.value('emergLongAddr'))
        if not emergLongAddr:
            if adrType == 1:
                emergArea = area
                emergStreet = street
                emergStreetType = streetType
                emergHouse = house
                emergBuild = corpus
                emergFlat = flat
                emergLongAddr = longAddress
            else:
                emergAdrRecord = self.getAddrRecord(clientId, 1)
                if emergAdrRecord:
                    emergKLADRCode = forceString(emergAdrRecord.value('KLADRCode'))
                    emergArea, emergRegion = self.getAreaAndRegion(clientId, adrType)
                    if emergKLADRCode[:2] == '78':
                        emergStreet = forceString(emergAdrRecord.value('streetName'))  # Адрес пациента: код улицы
                        emergStreetType = forceString(emergAdrRecord.value('streetType'))  # Адрес пациента: тип улицы
                        emergHouse = forceString(emergAdrRecord.value('number'))  # Адрес пациента: номер дома
                        emergBuild = forceString(emergAdrRecord.value('corpus'))  # Адрес пациента: корпус
                        emergFlat = forceString(emergAdrRecord.value('flat'))  # Адрес пациента: номер квартиры
                    else:
                        emergStreet = '*'
                    emergAddressId = forceInt(emergAdrRecord.value('addressId'))
                    emergLongAddr = formatAddress(emergAddressId)
                else:
                    emergArea = ''
                    emergStreet = ''
                    emergStreetType = ''
                    emergHouse = ''
                    emergBuild = ''
                    emergFlat = ''
                    emergLongAddr = ''

        return {
            'street'         : street,
            'streetType'     : streetType,
            'area'           : area,
            'house'          : house,
            'corpus'         : corpus,
            'flat'           : flat,
            'longAddress'    : longAddress,
            'emergArea'      : emergArea,
            'emergStreet'    : emergStreet,
            'emergStreetType': emergStreetType,
            'emergHouse'     : emergHouse,
            'emergBuild'     : emergBuild,
            'emergFlat'      : emergFlat,
            'emergLongAddr'  : emergLongAddr
        }

    def getIdExitus(self, record, isHospitalization, isDayStationary):
        stacIdExitus = {u'Выздоровление': 13,
                        u'Улучшение'    : 14,
                        u'Без перемен'  : 15,
                        u'Ухудшение'    : 16}
        dayStacIdExitus = {u'Выздоровление': 17,
                           u'Улучшение'    : 18,
                           u'Без перемен'  : 19,
                           u'Ухудшение'    : 20}
        idExitus = None
        if isHospitalization and forceString(record.value('atFlatCode')) == 'moving':
            movingResult = forceString(record.value('movingResult'))
            if isDayStationary:
                idExitus = dayStacIdExitus.get(movingResult, None)
            else:
                idExitus = stacIdExitus.get(movingResult, None)
        if idExitus is None:
            idExitus = forceInt(record.value('diagnosticResultCode'))

        return idExitus

    def getCircumstances(self, record, isHospitalization, isClinicalExamination):
        amount = forceDouble(record.value('amount'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        eventId = forceInt(record.value('event_id'))
        eventAidTypeCode = forceString(record.value('medicalAidTypeCode'))
        mesId = forceRef(record.value('MES_id'))
        specialityId = forceRef(record.value('speciality_id'))
        specialityCode = forceInt(record.value('specialityCode'))
        tariffType = forceInt(record.value('tariffType'))
        unitEntry = self.getRefBookValue('rbMedicalAidUnit', forceRef(record.value('unitId')))

        if not isClinicalExamination:
            if isHospitalization:
                prvsMagicNumber = 1 if forceRef(record.value('actionMES_id')) else 2
                circumstances = [(begDate, endDate, specialityId, specialityCode, prvsMagicNumber, prvsMagicNumber)]
            elif not record.value('visit_id').isNull() or not record.value('action_id').isNull():
                # выставление визита или действия
                unitCode = forceInt(unitEntry.code if unitEntry else 0)
                prvsMagicNumber = 1 if unitCode == 2 else 0
                circumstances = [(begDate, endDate, specialityId, specialityCode, prvsMagicNumber, prvsMagicNumber)]
            elif eventAidTypeCode == '4':   # Неотложка
                prvsMagicNumber = 1 if tariffType == CTariff.ttEventByMES else 0
                circumstances = [(endDate, endDate, specialityId, specialityCode, prvsMagicNumber, prvsMagicNumber)]    #endDate использован дважды, так как в неотложке все события должны выгружаться за один день
            elif not record.value('event_id').isNull() and not record.value('MES_id').isNull():
                # выставление события по МЭС
                if tariffType == CTariff.ttVisitsByMES:
                    circumstances = self.getEventVisitsCircumstances(eventId, mesId)
                #Если это дневной стационар
                elif eventAidTypeCode == '7': #По настоянию Сирафимы (181012), так как программист из ЕИСа сказал, что "там должна быть единичка"
                    circumstances = [(begDate, endDate, specialityId, specialityCode, 1, 1)]
                else:
                    circumstances = [(begDate, endDate, specialityId, specialityCode, 0, 0)]
                amount = 1
            else: # Maybe should use 'elif record.value('EventType.service_id')' here istead of pure 'else'
                circumstances = [(begDate, endDate, specialityId, specialityCode, 0, 0)]
        else:
            if tariffType == CTariff.ttEventByMES:
                caseCastCode = forceInt(CRBModelDataCache.getData('rbCaseCast', needCache=True).getStringById(forceInt(record.value('caseCast_id')), CRBComboBox.showCode))
                if caseCastCode == 32:  # Профосмотр ДЕТ МЭС
                    circumstances = [(begDate, begDate, specialityId, specialityCode, 1, 1)]
                else:
                    circumstances = [(endDate, endDate, specialityId, specialityCode, 1, 1)]
            else:
                circumstances = [(endDate, endDate, specialityId, specialityCode, 4, 4)]

        return circumstances, amount

    def getIllHistory(self, record, isHospitalization, aidKindCode, aidTypeCode):
        clientId = forceInt(record.value('client_id'))
        eventId = forceInt(record.value('event_id'))
        externalId = forceString(record.value('externalId'))
        numberCardCall = forceString(record.value('numberCardCall'))

        if aidTypeCode == '4':  # СМП
            # Возможна ситуация, когда ILLHISTORY не заполнено ничем
            if not numberCardCall and not self.chkEnableEmptySMPIllhistory.isChecked():
                return externalId if externalId else str(clientId)
            else:
                return numberCardCall if numberCardCall else externalId
        elif aidKindCode == '13':  # Первичная специализированная медико-санитарная помощь (стом12)
            return str(eventId)
        elif isHospitalization or externalId:  # Стационар, рег. код типа назначения = 6 (СПБ)
            return externalId
        elif aidTypeCode == '7':  # Дневной стационар, СПб
            return externalId if externalId else str(eventId)
        else:
            return str(clientId)

    def getCaseCast(self, record, isHospitalization, isDayStationary, aidTypeCode):
        eventTypeCode = forceString(record.value('eventTypeCode'))
        mesId = forceRef(record.value('MES_id'))

        caseCast = forceInt(CRBModelDataCache.getData('rbCaseCast', needCache=True).getStringById(
            forceInt(record.value('caseCast_id')), CRBComboBox.showCode))

        visitServiceCaseCastCode = forceInt(record.value('visitServiceCaseCastCode'))
        if visitServiceCaseCastCode:
            return visitServiceCaseCastCode
        elif caseCast:
            return caseCast
        elif isHospitalization:
            return 26 if forceBool(record.value('hmpKindRegionalCode')) else self.curMovingActionData.get('CASE_CAST', 7 if isDayStationary else 6)
        elif eventTypeCode == 'dd2013_1':
            # Диспансеризация
            return 10
        elif eventTypeCode == 'dd2013_2':
            return 12
        elif eventTypeCode == 'ddet1':
            return 14
        elif eventTypeCode == 'ddet2':
            return 16
        elif eventTypeCode == 'ddet3':
            return 15
        elif eventTypeCode == '80/5':
            return 19
        elif eventTypeCode == '80/4':
            return 20
        else:
            return 8 if aidTypeCode == '4' else (2 if aidTypeCode == '7' else 0) + (1 if mesId else 0) + 1

    def getIdFint(self, record, caseCast, aidTypeCode):
        policyInsurer = forceStringEx(record.value('policyInsurer'))

        personOrgStructIsArea = QtGui.qApp.db.getRecordEx(stmt=u"""
        SELECT
            os.isArea AS isArea
        FROM
            OrgStructure os
            INNER JOIN Person p ON os.id = p.orgStructure_id
        WHERE
            p.id = %(personId)s
        """ % {
            'personId': forceInt(record.value('eventExecPerson_id'))
        })
        if personOrgStructIsArea and forceInt(personOrgStructIsArea.value('isArea')) and caseCast in [35, 36, 37]:
            return 5
        else:
            return 4 if aidTypeCode == '4' \
                        and policyInsurer.lower() not in (u'ктф3', u'нком', u'') \
                        and policyInsurer.lower()[0] != u'ф' \
                else 1

    def getIdServMade(self, record):
        actionEndDate = forceDate(record.value('actionEndDate'))
        actionOrgId = forceRef(record.value('actionOrgId'))
        actionStatus = forceInt(record.value('actionStatus'))
        eventSetDate = forceDate(record.value('eventSetDate'))
        tariffType = forceInt(record.value('tariffType'))

        if actionStatus == ActionStatus.NotProvided:
            idServMade = 6
        elif actionStatus == ActionStatus.Appointed:
            idServMade = 3
        elif actionEndDate < eventSetDate and tariffType != CTariff.ttEventByMES:
            idServMade = 5
        elif actionStatus == ActionStatus.Cancelled:
            idServMade = 4
        elif actionOrgId and actionOrgId != QtGui.qApp.currentOrgId():
            idServMade = 3
        elif self.getMiacCodeByPerson(forceInt(record.value('actionPerson_id'))) and self.getMiacCodeByPerson(forceInt(record.value('actionPerson_id'))) != self.getMiacCodeByPerson(
                forceInt(record.value('eventExecPerson_id'))):
            idServMade = 2
        else:
            idServMade = 1

        return idServMade

    @staticmethod
    def createUslDbfRecord(record, dbfRecord, uslDbf, recNKML):
        uslDbfRecord = uslDbf.newRecord()
        uslDbfRecord['ID_NMKL'] = forceInt(recNKML.value('ID_NMKL'))
        uslDbfRecord['SERV_ID'] = dbfRecord['SERV_ID']
        uslDbfRecord['ID_IN_CASE'] = dbfRecord['ID_IN_CASE']
        uslDbfRecord['DATE_BEGIN'] = dbfRecord['DATEIN']
        uslDbfRecord['DATE_END'] = dbfRecord['DATEOUT']
        uslDbfRecord['V_MULTI'] = forceInt(record.value('amount'))
        uslDbfRecord['V_LONG_IVL'] = forceInt(recNKML.value('V_LONG_IVL'))
        uslDbfRecord['V_LONG_MON'] = forceInt(recNKML.value('V_LONG_MON'))
        return uslDbfRecord

    @staticmethod
    def createSluchDbfRecord(dbfRecord, sluchDbf, sluchRecord):
        sluchDbfRecord = sluchDbf.newRecord()
        sluchDbfRecord['SERV_ID'] = dbfRecord['SERV_ID']
        sluchDbfRecord['ID_OBJECT'] = forceInt(sluchRecord.value('ID_OBJECT'))
        sluchDbfRecord['OBJ_VALUE'] = forceString(sluchRecord.value('OBJ_VALUE'))
        return sluchDbfRecord

    def createDirectDbfRecord(self, dbfRecord, directDbf, directRecord, dGroup=None, dType=None):
        directDbfRecord = directDbf.newRecord()
        directDbfRecord['SERV_ID'] = dbfRecord['SERV_ID']
        # Номер направления (талона)
        directDbfRecord['D_NUMBER'] = forceString(directRecord.value('D_NUMBER'))
        # Дата выдачи направления (талона)
        directDbfRecord['DATE_ISSUE'] = pyDate(forceDate(directRecord.value('DATE_ISSUE')))
        # Дата планируемой госпитализации
        directDbfRecord['DATE_PLANG'] = pyDate(forceDate(directRecord.value('DATE_PLANG')))
        # Идентификатор специальности врача (rbSpeciality.regionalCode
        directDbfRecord['ID_PRVS'] = forceInt(directRecord.value('ID_PRVS'))
        # Идентификатор вида обследования (rbOBSType_eis.code)
        directDbfRecord['ID_OB_TYPE'] = forceInt(directRecord.value('ID_OB_TYPE'))
        # Идентификатор профиля медицинской помощи
        directDbfRecord['ID_PRMP'] = forceInt(directRecord.value('ID_PRMP'))
        # Идентификатор профиля койки (rbHospitalBedProfile.regionalCode)
        directDbfRecord['ID_B_PROF'] = forceInt(directRecord.value('ID_B_PROF'))
        # Описание ошибки
        directDbfRecord['ERROR'] = forceString(directRecord.value('ERROR'))

        # Группа направления
        if dGroup is not None:
            directDbfRecord['ID_D_GROUP'] = dGroup
        elif self.chkDD.isChecked():
            directDbfRecord['ID_D_GROUP'] = 2

        # Тип направления (назначения) (rbDType_eis.code)
        if dType is not  None:
            directDbfRecord['ID_D_TYPE'] = dType
        else:
            dType = forceInt(directRecord.value('ID_D_TYPE'))
            if forceInt(directRecord.value('isHmp')):  # если случай ВМП, то по дефолту выставляем ID_D_TYPE = 7
                if not dType:
                    dType = 7
            directDbfRecord['ID_D_TYPE'] = dType

        return directDbfRecord

    def createClientsDbfRecord(self, record, clientsDbf, documentType, documentSeries, endDate):
        birthDate = forceDate(record.value('birthDate'))
        clientId = forceInt(record.value('client_id'))
        documentNumber = forceString(record.value('documentNumber'))
        lastName = nameCase(forceString(record.value('lastName')))
        firstName = nameCase(forceString(record.value('firstName')))
        patrName = nameCase(forceString(record.value('patrName')))
        sex = forceInt(record.value('sex'))
        snils = formatSNILS(forceString(record.value('SNILS')))
        policySerial = forceString(record.value('policySerial'))
        policyNumber = forceString(record.value('policyNumber'))
        isNewborn = forceString(record.value('socStatusName')).lower() == u'новорожденный'
        nborn = max(1, forceInt(record.value('nborn'))) if isNewborn else 0

        policyBegDate = forceDate(record.value('policyBegDate'))
        if not policyBegDate.isValid():
            policyBegDate = max(birthDate, QDate(1900, 1, 1), firstYearDay(endDate))
        policyEndDate = forceDate(record.value('policyEndDate'))
        if not policyEndDate.isValid():
            policyEndDate = QDate(2200, 1, 1)
        clientNotes = forceString(record.value('clientNotes'))
        citizenship = forceString(record.value('citizenship'))

        dbfRecord = clientsDbf.newRecord()
        dbfRecord['SURNAME'] = lastName
        dbfRecord['NAME'] = firstName
        dbfRecord['S_NAME'] = patrName if patrName else '-'
        dbfRecord['BIRTHDAY'] = pyDate(birthDate)
        dbfRecord['SEX'] = formatSex(sex).lower()
        dbfRecord['ID_PAT_CAT'] = forceInt(record.value('idPatCat')) or 2  # Iriska: 2 - соц.статус не определен
        dbfRecord['DOC_TYPE'] = int(documentType)
        dbfRecord['SER_L'] = documentSeries[0] if len(documentSeries) >= 1 else '-'
        dbfRecord['SER_R'] = documentSeries[1] if len(documentSeries) >= 2 else '-'
        dbfRecord['DOC_NUMBER'] = documentNumber if documentNumber else '-'
        dbfRecord['SNILS'] = snils
        dbfRecord['IS_SMP'] = u'Добавлен(а) через СМП' in clientNotes
        dbfRecord['C_OKSM'] = citizenship[1:] if citizenship else '643'
        dbfRecord['POLIS_TYPE'] = forceString(record.value('policyKindRegionalCode'))
        dbfRecord['POLIS_S'] = policySerial
        dbfRecord['POLIS_N'] = policyNumber
        insurerArea = forceString(record.value('policyInsurerArea'))
        if not insurerArea or insurerArea.startswith('78'):
            dbfRecord['ID_SMO'] = forceInt(record.value('policyInsurerEisId'))
            dbfRecord['ID_SMO_REG'] = 0
        else:
            dbfRecord['ID_SMO'] = 269  # кТф3
            dbfRecord['ID_SMO_REG'] = forceInt(record.value('policyInsurerEisId'))
        dbfRecord['POLIS_BD'] = pyDate(policyBegDate)
        dbfRecord['POLIS_ED'] = pyDate(policyEndDate)
        regAddrType, regOkatoId, regHouseId, regHouse, regCorpus, regFlat, regFreeInput, regKLADRCode, regStreet, regStreetTypeId = self.getClientAddressParts(clientId, 0)
        if (dbfRecord['C_OKSM'] == '643' and regAddrType == u'п'):
            regAddrType = u'р'
        dbfRecord['ADDR_TYPE'] = regAddrType
        dbfRecord['IDOKATOREG'] = regOkatoId
        dbfRecord['ID_HOUSE'] = regHouseId
        dbfRecord['HOUSE'] = regHouse
        dbfRecord['KORPUS'] = regCorpus
        dbfRecord['FLAT'] = regFlat
        dbfRecord['U_ADDRESS'] = regFreeInput
        dbfRecord['KLADR_CODE'] = regKLADRCode.lstrip('0')
        dbfRecord['STREET'] = regStreet
        dbfRecord['IDSTRTYPE'] = regStreetTypeId
        locAddrType, locOkatoId, locHouseId, locHouse, locCorpus, locFlat, locFreeInput, locKLADRCode, locStreet, locStreetTypeId = self.getClientAddressParts(clientId, 1)
        if (locHouseId == 0):
            locAddrType, locOkatoId, locHouseId, locHouse, locCorpus, locFlat, locFreeInput, locKLADRCode, locStreet, locStreetTypeId = self.getClientAddressParts(clientId, 0)
        if (dbfRecord['C_OKSM'] == '643' and locAddrType == u'п'):
            locAddrType = u'р'
        dbfRecord['ADDRTYPE_L'] = locAddrType
        dbfRecord['OKATOREG_L'] = locOkatoId
        dbfRecord['ID_HOUSE_L'] = locHouseId
        dbfRecord['HOUSE_L'] = locHouse
        dbfRecord['KORPUS_L'] = locCorpus
        dbfRecord['FLAT_L'] = locFlat
        dbfRecord['U_ADDR_L'] = locFreeInput
        dbfRecord['KLADR_L'] = locKLADRCode.lstrip('0')
        dbfRecord['STREET_L'] = locStreet
        dbfRecord['STRTYPE_L'] = locStreetTypeId
        dbfRecord['REMARK'] = forceStringEx(record.value('benefitTypeRegionalCode'))
        dbfRecord['SEND'] = False
        dbfRecord['ID_MIS'] = clientId
        dbfRecord['VNOV_D'] = forceInt(record.value('weight'))

        if isNewborn:
            representativeInfo = self.getClientRepresentativeInfo(clientId)

            if representativeInfo:
                # Тип представителя
                dbfRecord['ID_G_TYPE'] = self.mapReprType.get(representativeInfo.get('relationTypeCode', '0'), 0)
                # фамилия представителя
                dbfRecord['G_SURNAME'] = representativeInfo.get('lastName', '')
                # имя представителя
                dbfRecord['G_NAME'] = representativeInfo.get('firstName', '')
                # отчество представителя
                dbfRecord['G_S_NAME'] = representativeInfo.get('patrName', '')
                # дата рождения представителя
                dbfRecord['G_BIRTHDAY'] = pyDate(representativeInfo.get('birthDate', None))
                # пол представителя
                sexp = representativeInfo.get('sex', 0)
                dbfRecord['G_SEX'] = formatSex(sexp).lower()

                # тип документа представителя
                dbfRecord['G_DOC_TYPE'] = representativeInfo.get('documentTypeRegionalCode', 5)
                dbfRecord['C_DOC'] = representativeInfo.get('documentTypeRegionalCode', 5)

                serialLeft, serialRight = splitDocSerial(representativeInfo.get('serial', ''))
                # левая часть серии документа представителя
                dbfRecord['G_SERIA_L'] = serialLeft
                # правая часть серии документа представителя
                dbfRecord['G_SERIA_R'] = serialRight[:2] if serialRight else ''
                # номер документа представителя
                dbfRecord['G_DOC_NUM'] = representativeInfo.get('number', '')

        dbfRecord['N_BORN'] = nborn
        dbfRecord['LGOTS'] = forceString(record.value('clientBenefitsCodes'))
        return dbfRecord

    def postProcess(self, dbfName):
        with CDbf(dbfName, encoding='cp866') as dbf:
            idInCaseMap = dict((dbfRecord['ACCITEM_ID'], dbfRecord['ID_IN_CASE']) for dbfRecord in dbf)
            for dbfRecord in dbf:
                mainAccountItemId = self.mainAccountItemMap.get(dbfRecord['ACCITEM_ID'])
                if mainAccountItemId and mainAccountItemId in idInCaseMap:
                    dbfRecord['ID_MAIN'] = idInCaseMap[mainAccountItemId]
                    dbfRecord.store()

    def process(self, dbf, clientsDbf, record, eisLpuId, processedClientIds, personFormat='id', uslDbf=None, sluchDbf=None, directDbf=None):
        accountId = forceInt(record.value('account_id'))
        accountItemId = forceInt(record.value('accountItem_id'))
        eventId  = forceInt(record.value('event_id'))
        clientId = forceInt(record.value('client_id'))

        lastName  = nameCase(forceString(record.value('lastName')))
        firstName = nameCase(forceString(record.value('firstName')))
        patrName  = nameCase(forceString(record.value('patrName')))
        birthDate = forceDate(record.value('birthDate'))
        begDate = forceDate(record.value('begDate'))
        age = calcAgeInYears(birthDate, begDate)
        sex = forceInt(record.value('sex'))
        isNewborn = forceString(record.value('socStatusName')).lower() == u'новорожденный'
        nborn = max(1, forceInt(record.value('nborn'))) if isNewborn else 0
        documentRegionalCode = forceString(record.value('documentRegionalCode'))
        documentType = documentRegionalCode if documentRegionalCode else self.mapDocTypeToEIS.get(forceString(record.value('documentType')), '5')
        documentSerial=forceStringEx(record.value('documentSerial'))
        eventAidKindCode = forceString(record.value('medicalAidKindCode'))
        eventAidTypeCode = forceString(record.value('medicalAidTypeCode'))
        if len(documentSerial)==4 and documentSerial.isdigit():
            documentSerial=documentSerial[:2]+' '+documentSerial[2:]
        if documentType != '6': # atronah: Не "Ин. паспорт"
            documentSerial = documentSerial.replace('-', ' ')
        documentSeries = trim(documentSerial).split()
        documentNumber = forceString(record.value('documentNumber'))
        order = self.mapEventOrderToEIS.get(forceInt(record.value('eventOrder')), '')
        eventOrder = forceInt(record.value('eventOrder'))
        forPom = 1 if eventOrder == 2 or eventAidTypeCode == '4' else (2 if eventOrder == 5 else 3)
        policySerial = forceString(record.value('policySerial'))
        policyNumber = forceString(record.value('policyNumber'))
        policyInsurer = forceStringEx(record.value('policyInsurer'))
        snils = formatSNILS(forceString(record.value('SNILS')))
        externalId = forceString(record.value('externalId'))
        actionSetSpecialityCode = forceInt(record.value('actionSetSpecialityCode'))
        emergFinishServiceDate = forceDate(record.value('emergFinishServiceDate'))
        actionTypeCode = forceString(record.value('atCode'))
        actionTypeServiceType = forceRef(record.value('atServiceType'))
        transfCode = forceInt(record.value('transfCode'))

        isClinicalExamination = self.chkDD.isChecked() # Флаг диспансеризации (опции)
        eventPurposeRegionalCode = forceString(record.value('purposeRegionalCode'))
        isHospitalization = eventPurposeRegionalCode == '6'
        isDayStationary = forceBool(record.value('hasDayStationary')) or externalId.lower().startswith(u'дс')

        serviceId = forceRef(record.value('service_id'))
        serviceDetail = self.serviceDetailCache.get(serviceId)
        if isClinicalExamination and (clientId, serviceDetail.infisCode) in self.processedServDatas:
            return []

        addressInfo = self.getAddressInfo(record)
        profileNet = u'в' if age>=18 else u'д'

        mkb = forceString(record.value('MKB'))
        mkb = mkb.replace(' ', '') # новая вводная: в случае субклассификации без пятого знака
                                   # субклассификация должна помещаться на пятый знак
        mkb = MKBwithoutSubclassification(mkb)
        mkb = mkb+forceString(record.value('prim'))
        mkb_pc = forceString(record.value('MKB_PC'))
        actionMKB = forceString(record.value('actionMKB'))
        if not mkb_pc:
            mkb_pc = mkb

        personId = forceInt(record.value('person_id'))
        eventPersonId = forceInt(record.value('eventPerson_id'))
        eventSpecialityId = forceRef(record.value('eventSpeciality_id'))
        mesId = forceRef(record.value('MES_id'))
        tariffType = forceInt(record.value('tariffType'))

        idExitus = self.getIdExitus(record, isHospitalization, isDayStationary)

        if eventId != self.curEventId:
            self.curEventId = eventId
            self.curMovingActionData = {}         # При переходе в новое обращение всегда сбрасываем данные из движения.
            self.curClinicalExaminationData = {}
        actionId = forceRef(record.value('action_id'))
        unitEntry = self.getRefBookValue('rbMedicalAidUnit', forceRef(record.value('unitId')))
        idSpPay = forceInt(unitEntry.regionalCode if unitEntry else 0)
        hmpKindRegCode = forceInt(record.value('hmpKindRegionalCode'))
        isHighTech = forceBool(hmpKindRegCode)
        hmpMetRegCode = forceInt(record.value('hmpMethodRegionalCode'))

        if isClinicalExamination and tariffType == CTariff.ttEventByMES:
            self.curClinicalExaminationData = {
                'ID_SP_PAY': idSpPay
            }
        circumstances, amount = self.getCircumstances(record, isHospitalization, isClinicalExamination)

        eventSpecialityCode = forceInt(record.value('eventSpecialityCode')) # Для действия "движение" берется специальность исполнителя в движении

        isLastMoving = forceBool(record.value('lastMoving'))
        if forceString(record.value('atFlatCode')) == 'moving':
            _begDate, _, specialityId, _, _, _ = circumstances[0]   # Здесь всегда должна быть только одна строка
            self.curMovingActionData = {'DIAGNOSIS': actionMKB if actionMKB else mkb ,
                                        'DIAG_C': actionMKB if actionMKB else mkb_pc,
                                        'DIAG_P_C': actionMKB if actionMKB else mkb_pc,
                                        'SERV_ID': actionId,
                                        'ID_EXITUS': idExitus,
                                        'CASE_CAST': 26 if isHighTech else 7 if isDayStationary else 6,
                                        'ID_SP_PAY': 43 if isDayStationary else idSpPay,
                                        'ID_DEPT': forceString(record.value('movingCurrOrgStructCode')),
                                        'ID_DOC_C': self.getPersonIdentifier(forceRef(record.value('actionPerson_id')), eisLpuId),
                                        'IDVIDHMP': hmpKindRegCode,
                                        'IDMETHMP': hmpMetRegCode,
                                        'ID_PRVS_C': forceInt(record.value('eventSpecialityCode')),
                                        'ID_PRVS_D': eventSpecialityCode,
                                        'QRESULT': forceInt(record.value('eventResultCode')) if isLastMoving else
                                                                                        10 if isDayStationary and self.prevIsDayStationary.setdefault(eventId, True) else
                                                                                        3 if isDayStationary and not self.prevIsDayStationary.setdefault(eventId, True) else 4,   # Переведен на другой профиль коек
                                        'isHighTech': isHighTech,
                                        'ID_GOSP': self.getIdGosp(isDayStationary,
                                                                  forceDateTime(record.value('actionBegDate')),
                                                                  forceDateTime(record.value('actionEndDate')),
                                                                  forceInt(record.value('movingOSType')))}
            self.prevIsDayStationary[eventId] = isDayStationary
        eventAidProfileCode = self.getAidCodes(serviceDetail, begDate, eventSpecialityId, birthDate, sex, mkb)[0]
        result = []
        for begDate, endDate, specialityId, specialityCode, prvsTypeId, prvsGroup in circumstances:
            serviveAidProfileCode, serviceAidKindCode, serviceAidTypeCode = self.getAidCodes(serviceDetail, begDate, specialityId, birthDate, sex, mkb)
            aidProfileCode = serviveAidProfileCode or eventAidProfileCode
            aidKindCode = serviceAidKindCode or eventAidKindCode
            aidTypeCode = serviceAidTypeCode or eventAidTypeCode
            if forceString(record.value('atFlatCode')) == 'moving':
                self.curMovingActionData['ID_PRMP_C'] = aidProfileCode
            dbfRecord = dbf.newRecord()
            dbfRecord['SURNAME']    = lastName  # Фамилия пациента
            dbfRecord['NAME1']      = firstName # Имя пациента
            dbfRecord['NAME2']      = patrName if patrName else '-' # Отчество пациента
            dbfRecord['BIRTHDAY']   = pyDate(birthDate)  # дата рождения
            dbfRecord['SEX']        = formatSex(sex).lower()     # Пол (М/Ж)
            dbfRecord['POLIS_S']    = policySerial if policySerial else '-'  # Серия полиса
            dbfRecord['POLIS_N']    = policyNumber if policyNumber else '-' # Номер полиса
            dbfRecord['POLIS_W']    = policyInsurer # Код СМО, выдавшей полис
            dbfRecord['PAYER']      = policyInsurer # Код СМО, выдавшей полис?
            dbfRecord['TYPEDOC']    = documentType  # Тип документа
            dbfRecord['SER1']       = documentSeries[0] if len(documentSeries)>=1 and documentSeries[0] else '-' # Серия документа, левая часть
            dbfRecord['SER2']       = documentSeries[1] if len(documentSeries)>=2 and documentSeries[1] else '-' # Серия документа, правая часть
            dbfRecord['NPASP']      = documentNumber if documentNumber else '-'# Номер документа
            dbfRecord['SNILS']      = snils

            if aidTypeCode == '4':  # Неотложка
                dbfRecord['STREET'] = addressInfo['emergStreet']  # Адрес пациента: код улицы
                dbfRecord['STREETYPE'] = addressInfo['emergStreetType']  # Адрес пациента: тип улицы
                dbfRecord['AREA'] = addressInfo['emergArea']  # Адрес пациента: код район
                dbfRecord['HOUSE'] = addressInfo['emergHouse']  # Адрес пациента: номер дома
                dbfRecord['KORP'] = addressInfo['emergBuild']  # Адрес пациента: корпус
                dbfRecord['FLAT'] = addressInfo['emergFlat']  # Адрес пациента: номер квартиры
                dbfRecord['LONGADDR'] = addressInfo['emergLongAddr']  # дополнительно для поиска пациента
                if tariffType != CTariff.ttEventByMES:
                    dbfRecord['SERV_ID'] = 0
                    dbfRecord['ID_IN_CASE'] = 0
                else:
                    dbfRecord['SERV_ID'] = eventId
                    self.servIdsCounter[eventId] += 1
                    dbfRecord['ID_IN_CASE'] = self.servIdsCounter[eventId]
            else:
                dbfRecord['STREET'] = addressInfo['street']         # Адрес пациента: код улицы
                dbfRecord['STREETYPE'] = addressInfo['streetType']  # Адрес пациента: тип улицы
                dbfRecord['AREA'] = addressInfo['area']             # Адрес пациента: код район
                dbfRecord['HOUSE'] = addressInfo['house']           # Адрес пациента: номер дома
                dbfRecord['KORP'] = addressInfo['corpus']           # Адрес пациента: корпус
                dbfRecord['FLAT'] = addressInfo['flat']             # Адрес пациента: номер квартиры
                dbfRecord['LONGADDR'] = addressInfo['longAddress']  # дополнительно для поиска пациента
                if isHospitalization:
                    servId = self.curMovingActionData.get('SERV_ID', actionId if actionId else eventId)
                    dbfRecord['SERV_ID'] = servId
                    self.servIdsCounter[servId] += 1
                    dbfRecord['ID_IN_CASE'] = self.servIdsCounter[servId]
                else:
                    dbfRecord['SERV_ID']    = eventId      # идентификатор случая
                    self.servIdsCounter[eventId] += 1
                    dbfRecord['ID_IN_CASE'] = self.servIdsCounter[eventId]

            if actionTypeServiceType == ActionServiceType.Operation:
                self.mainAccountItemMap[accountItemId] = self.getMainAccountItemForOperation(accountId, eventId)

            dbfRecord['ORDER']      = order        # Признак экстренности случая лечения (если случай экстренный - принимает значение "э" или "Э")
            # TODO: Возможно стоит вынести получение кода МЭС в основной запрос, если здесь будет слишком много записей - но оно нужно только для диспансеризации
            dbfRecord['PROFILE']    = serviceDetail.infisCode if not isClinicalExamination else forceString(QtGui.qApp.db.translate('mes.MES', 'id', mesId, 'code'))# Код профиля лечения
            dbfRecord['PROFILENET'] = profileNet   # Тип сети профиля (в - взрослая, д - детская)
            dbfRecord['DATEIN']     = pyDate(emergFinishServiceDate if eventAidTypeCode == '4' and emergFinishServiceDate.isValid() else begDate) # Дата начала услуги
            dbfRecord['DATEOUT']    = pyDate(emergFinishServiceDate if eventAidTypeCode == '4' and emergFinishServiceDate.isValid() else endDate) # Дата окончания услуги
            dbfRecord['AMOUNT']     = amount if forceString(record.value('atFlatCode')) != 'moving' else 1 # Объем лечения
            dbfRecord['DIAGNOSIS']  = self.curMovingActionData.get('DIAGNOSIS', actionMKB if actionMKB and not isClinicalExamination else mkb) # Код диагноза
            dbfRecord['SEND']       = False        # Флаг обработки записи
            dbfRecord['ERROR']      = ''           # Описание ошибки
            dbfRecord['ID_PRVS']    = specialityCode
            dbfRecord['IDPRVSTYPE'] = prvsTypeId
            dbfRecord['PRVS_PR_G']  = prvsGroup
            dbfRecord['ID_EXITUS'] = self.curMovingActionData.get('ID_EXITUS', idExitus)
            dbfRecord['ILLHISTORY'] = self.getIllHistory(record, isHospitalization, aidKindCode, aidTypeCode)

            caseCast = self.getCaseCast(record, isHospitalization, isDayStationary, aidTypeCode)
            dbfRecord['CASE_CAST'] = caseCast
            dbfRecord['ID_FINT'] = self.getIdFint(record, caseCast, aidTypeCode)

            if isHospitalization:
                amount = forceInt(record.value('amount'))
                if actionTypeCode in self.reanimationActionTypes:
                    amountd = forceDate(record.value('actionBegDate')).daysTo(forceDate(record.value('actionEndDate')))
                    dbfRecord['AMOUNT_D'] = amountd if amountd else 1
                else: dbfRecord['AMOUNT_D']  = amount
            else:
                dbfRecord['AMOUNT_D']   = forceInt(record.value('amount')) if aidTypeCode == '7' and mesId else 0

            dbfRecord['ID_PRMP']    = aidProfileCode # Код профиля по Классификатору профиля
            dbfRecord['ID_PRMP_C']  = self.curMovingActionData.get('ID_PRMP_C', eventAidProfileCode) # Код профиля по Классификатору профиля для случая лечения
            dbfRecord['DIAG_C']     = self.curMovingActionData.get('DIAG_C', mkb_pc) # Код диагноза для случая лечения
            dbfRecord['DIAG_S_C']   = ''  # Код сопутствующего диагноза для случая лечения
            dbfRecord['DIAG_P_C']   = self.curMovingActionData.get('DIAG_P_C', mkb_pc) # Код первичного диагноза для случая лечения
            dbfRecord['QRESULT']    = self.curMovingActionData.get('QRESULT', forceInt(record.value('eventResultCode')))     # Результат обращения за медицинской помощью
            dbfRecord['ID_PRVS_C']  = self.curMovingActionData.get('ID_PRVS_C', forceInt(record.value('eventSpecialityCode'))) # ID врачебной специальности для случая лечения
            if isHospitalization:
                dbfRecord['ID_SP_PAY']  = self.curMovingActionData.get('ID_SP_PAY', 43 if isDayStationary else idSpPay)            # ID способа оплаты медицинской помощи
            elif isClinicalExamination:
                dbfRecord['ID_SP_PAY'] = self.curClinicalExaminationData.get('ID_SP_PAY', idSpPay)
            else:
                dbfRecord['ID_SP_PAY'] = idSpPay

            tmpAmount = forceDouble(record.value('amount'))
            dbfRecord['ID_ED_PAY']  = tmpAmount+1 if isDayStationary and isDayStationary else tmpAmount           # Количество единиц оплаты медицинской помощи
            dbfRecord['ID_VMP']     = 8 if self.curMovingActionData.get('isHighTech', isHighTech) else forceInt(QVariant(aidKindCode))               # ID вида медицинской помощи
            dbfRecord['ID_DOC']     = self.getPersonIdentifier(personId, eisLpuId)  # Идентификатор врача из справочника SPRAV_DOC.DBF (для услуги)
            dbfRecord['ID_DEPT']    = self.getOrgStructureIdentifier(personId, personFormat) # Идентификатор отделения МО из справочника SPRAV_DEPTS.DBF (для услуги)
            dbfRecord['ID_DOC_C']   = self.curMovingActionData.get('ID_DOC_C', self.getPersonIdentifier(eventPersonId, eisLpuId)) # Идентификатор врача из справочника SPRAV_DOC.DBF (для случая)

            #for test
            # dbfRecord['ID_DEPT_C'] = self.getOrgStructureIdentifier(personId, personFormat)
            dbfRecord['ID_DEPT_C'] = self.curMovingActionData.get('ID_DEPT', self.getOrgStructureIdentifier(eventPersonId, personFormat)) # Идентификатор отделения МО из справочника SPRAV_DEPTS.DBF (для случая)
            #atronah: Так как нет справочника SPRAV_LPU.DBF, а в ИНФИС коде иногда используются буквы, что вызывает ошибки в программе ЕИСа, выгружаем тупо 0, как и раньше
            #craz: Решили попробовать переносить ID_LPU из базы ЕИСа в МИАЦ код организации и подставлять этот код для места выполнения действия в ID_LPU_D
            actionOrgEisId = forceRef(record.value('actionOrgEisId'))
            actionOrgOKATO = forceString(record.value('actionOrgOKATO'))
            actionOrgInfisCode = forceInt(record.value('actionOrgInfisCode'))
            goalEntry = self.getRefBookValue('rbEventGoal', forceInt(record.value('goal')))
            goal = forceInt(goalEntry.regionalCode) if goalEntry else 0
            refSpecCode = forceInt(record.value('referralSpecialityRegCode'))
            if not refSpecCode:
                refSpecCode = actionSetSpecialityCode
            if not refSpecCode:
                refSpecCode = eventSpecialityCode

            if isHospitalization:
                hospReferral = forceInt(record.value('hospReferralOrgEisCode'))
                dbfRecord['ID_LPU_D'] = hospReferral
                dbfRecord['ID_PRVS_D']  = self.curMovingActionData.get('ID_PRVS_D', eventSpecialityCode)
                dbfRecord['ID_GOAL_D']  = 5 if hospReferral else 0
            elif actionOrgEisId and not isClinicalExamination:
                dbfRecord['ID_LPU_D']   = forceInt(actionOrgEisId) # Идентификатор ЛПУ, направившего на лечение (из справочника SPRAV_LPU.DBF)
                dbfRecord['ID_PRVS_D']  = refSpecCode
                dbfRecord['ID_GOAL_D']  = goal
            else:
                dbfRecord['ID_LPU_D']   = forceInt(self.currentOrgMiac)
                dbfRecord['ID_PRVS_D']  = refSpecCode
                dbfRecord['ID_GOAL_D']  = goal if goal else 1
            #            dbfRecord['Q_RES']      = resultCode
            dbfRecord['ACC_ID']     = accountId
            dbfRecord['ACCITEM_ID'] = accountItemId
            dbfRecord['CLIENT_ID']  = clientId
            dbfRecord['IDSERVDATA'] = serviceDetail.infisCode

            # shit is begin for i3978 task#
            if forceInt(dbfRecord['ID_SP_PAY']) == 29 and forceInt(dbfRecord['ID_GOAL_D']) == 5 and self.getVisitCountByEvent(forceInt(eventId)) > 1:
                dbfRecord['ID_SP_PAY'] = 30
            ##############end###############
            if isClinicalExamination:
                eventRelegateOrgId = forceRef(record.value('relegateOrg_id'))
                relegateMiacCode = self.eventRelegateOrgMiacCache.setdefault(eventRelegateOrgId,
                                                                             QtGui.qApp.db.translate('Organisation',
                                                                                                     'id',
                                                                                                     eventRelegateOrgId,
                                                                                                     'miacCode'))
                dbfRecord['ID_LPU_D']   = forceInt(relegateMiacCode) or forceInt(self.currentOrgMiac)
                dbfRecord['ID_PRVS_D']  = forceInt(record.value('eventSpecialityCode'))
                dbfRecord['ID_GOAL_D']  = goal
                self.processedServDatas.append((clientId, serviceDetail.infisCode))

                idServMade = self.getIdServMade(record)
                dbfRecord['IDSERVMADE'] = idServMade
                # Если потребуется менять условия для заполнения IDSERVLPU, необходимо учесть, что сейчас в actionOrgEisId
                # могут попасть как место выполнения действия (если есть), так и направившая организация из обращения.
                if not actionOrgEisId:
                    if actionId:
                        actionOrgEisId = self.getMiacCodeByPerson(forceInt(record.value('actionPerson_id')))
                    else:
                        actionOrgEisId = self.getMiacCodeByPerson(forceInt(record.value('eventExecPerson_id')))

                if idServMade in (4, 6):
                    eventOrgEisId = self.getMiacCodeByPerson(forceInt(record.value('eventExecPerson_id')))
                    dbfRecord['IDSERVLPU'] = forceString(eventOrgEisId) if eventOrgEisId else forceString(self.currentOrgMiac)
                else:
                    dbfRecord['IDSERVLPU'] = forceString(actionOrgEisId) if actionOrgEisId else forceString(self.currentOrgMiac)
            else:
                dbfRecord['IDSERVDATA'] = ''
                dbfRecord['IDSERVMADE'] = 0
                dbfRecord['IDSERVLPU'] = ''

            if actionOrgOKATO[:2] not in [self.currentProvinceOKATO[:2], self.currentOKATO[:2]]:
                dbfRecord['ID_LPU_RF'] = actionOrgInfisCode

            dbfRecord['ID_GOAL'] = goal if goal else 1 if not isClinicalExamination else 2
            dbfRecord['ID_GOAL_C'] = goal if goal else 1 if not isClinicalExamination else 2
            if isHospitalization:
                # 1 - госпитализация
                # 2 - приемное отделение
                # 3 - досуточная госпитализация
                # 4 - дневной стационар
                # 5 - не госпитализация
                dbfRecord['ID_GOSP'] = self.curMovingActionData.get('ID_GOSP', self.getIdGosp(isDayStationary,
                                                                  forceDateTime(record.value('eventSetDate')),
                                                                  forceDateTime(record.value('eventExecDate')),
                                                                  forceInt(record.value('movingOSType'))))
            else:
                dbfRecord['ID_GOSP'] = 5
            if isClinicalExamination:
                dbfRecord['ID_PAT_CAT'] = forceInt(record.value('idPatCat'))
            dbfRecord['IDVIDVME'] = 1
            dbfRecord['IDFORPOM'] = forPom
            dbfRecord['IDVIDHMP'] = self.curMovingActionData.get('IDVIDHMP', hmpKindRegCode)
            dbfRecord['IDMETHMP'] = self.curMovingActionData.get('IDMETHMP', hmpMetRegCode)

            dbfRecord['ID_LPU'] = forceInt(self.currentOrgMiac)
            dbfRecord['N_BORN'] = nborn

            dbfRecord['ID_INCOMPL'] = 5
            dbfRecord['ID_TRANSF'] = transfCode if transfCode else 0

            # Изменения по ЕИС ОМС от 15.05.2017
            # i4070
            # ID_LPU_P - Идентификатор подразделения МО (для услуги)
            # ID_LPU_P_C - Идентификатор подразделения МО (для случая)
            # IDSERVMADE - Идентификатор порядка выполнения пункта карты
            eventPersonMiac = self.getMiacCodeByPerson(forceInt(record.value('eventExecPerson_id')))
            if forceRef(record.value('actionPerson_id')):
                actionPersonMiac = self.getMiacCodeByPerson(forceInt(record.value('actionPerson_id')))
            else:
                actionPersonMiac = eventPersonMiac

            actionPersonMiac = actionPersonMiac if actionPersonMiac else forceInt(self.currentOrgMiac)
            eventPersonMiac = eventPersonMiac if eventPersonMiac else forceInt(self.currentOrgMiac)

            # Выставить IDSERVMADE = 2 если "код миац" исполнителя услуги отличается от "код миац" исполнителя обращения
            if dbfRecord['IDSERVMADE'] == 1:
                dbfRecord['IDSERVMADE'] = 2 if eventPersonMiac != actionPersonMiac else dbfRecord['IDSERVMADE']

            if dbfRecord['IDSERVMADE'] == 2:
                dbfRecord['ID_LPU_P'] = actionPersonMiac
                dbfRecord['ID_LPU_P_C'] = eventPersonMiac
            elif dbfRecord['IDSERVMADE'] > 2:
                dbfRecord['ID_LPU_P'] = dbfRecord['ID_LPU_P_C'] = eventPersonMiac
            else:
                eventMiac = self.getMiacCodeByPerson(forceInt(record.value('eventExecPerson_id')))
                intIdServMiac = forceInt(dbfRecord['IDSERVLPU'])

                tempMiac = intIdServMiac if intIdServMiac else eventMiac
                miacCode = tempMiac if tempMiac else forceInt(self.currentOrgMiac)

                dbfRecord['ID_LPU_P'] = dbfRecord['ID_LPU_P_C'] = miacCode

            dbfRecord.store()
            result.append(dbfRecord)

            if uslDbf is not None and actionTypeCode in self.reanimationActionTypes:
                NMKLRecords = self.getID_NMKLRecords(eventId, dbfRecord['DATEIN'], dbfRecord['DATEOUT'])
                for r in NMKLRecords:
                    global isUslDbfEmpty
                    isUslDbfEmpty = False
                    uslDbfRecord = self.createUslDbfRecord(record, dbfRecord, uslDbf, r)
                    uslDbfRecord.store()

            if sluchDbf is not None:
                sluchRecord = self.getSluchRecord(eventId)
                if sluchRecord:
                    global isSluchDbfEmpty
                    isSluchDbfEmpty = False
                    sluchDbfRecord = self.createSluchDbfRecord(dbfRecord, sluchDbf, sluchRecord)
                    sluchDbfRecord.store()

            exportD = False
            if self.chkDD.isChecked():
                if forceString(record.value('eventResultRegionalCode')) in ['52', '84', '85', '86', '90', '92', '93', '94', '95']:
                    exportD = True

            if directDbf is not None and exportD:
                directRecord = self.getDirectRecord(eventId)
                if directRecord:
                    global isDirectDbfEmpty
                    isDirectDbfEmpty = False
                    directDbfRecord = self.createDirectDbfRecord(dbfRecord, directDbf, directRecord)
                    directDbfRecord.store()

                    if forceInt(directRecord.value('resultCode')) in [90, 92, 93, 94, 95]:
                        D_GROUP = forceInt(directRecord.value('D_GROUP'))
                        if D_GROUP in [12, 14]:
                            directDbfRecord = self.createDirectDbfRecord(dbfRecord, directDbf, directRecord,
                                                                         dGroup=6,
                                                                         dType=D_GROUP)
                            directDbfRecord.store()

            if clientsDbf is not None and clientId not in processedClientIds:
                processedClientIds.add(clientId)
                clientDbfRecord = self.createClientsDbfRecord(record, clientsDbf, documentType, documentSeries, endDate)
                clientDbfRecord.store()

        return result

    def getID_NMKLRecords(self, eventId, begDate, endDate):
        records = QtGui.qApp.db.getRecordList(table='SPRAV_GROUP_NMKL', stmt=
            u'''
SELECT
  SPRAV_GROUP_NMKL.ID_NMKL  AS ID_NMKL,
  SPRAV_GROUP_NMKL.LONG_IVL AS V_LONG_IVL,
  SPRAV_GROUP_NMKL.LONG_MON AS V_LONG_MON
FROM Event
    INNER JOIN Action ON Event.id = Action.event_id AND Action.deleted = 0
    INNER JOIN ActionType ON Action.actionType_id = ActionType.id
    INNER JOIN ActionType_Service ON ActionType.id = ActionType_Service.master_id
    INNER JOIN rbService ON ActionType_Service.service_id = rbService.id
    INNER JOIN SPRAV_GROUP_NMKL ON rbService.code = SPRAV_GROUP_NMKL.NMKL_CODE
WHERE Event.id = %i AND Action.begDate >= '%s' AND Action.endDate <= '%s'
            ''' % (eventId, str(begDate), str(endDate)))
        return records

    def getSluchRecord(self, eventId):
        if eventId in self.eventIdList_Sluch: return None
        else: self.eventIdList_Sluch.append(eventId)
        record = QtGui.qApp.db.getRecordEx(stmt=
            u'''
SELECT
    rbSofa.code AS ID_OBJECT,
    APSValue.value AS OBJ_VALUE
FROM Event
    INNER JOIN Action AType ON Event.id = AType.event_id AND AType.deleted = 0
    INNER JOIN ActionType ATType ON AType.actionType_id = ATType.id AND ATType.flatCode = 'leaved'
    INNER JOIN ActionPropertyType APTType ON ATType.id = APTType.actionType_id AND APTType.name = 'Шкала SOFA/Шкала ASA'
    INNER JOIN ActionProperty APSofaType ON AType.id = APSofaType.action_id AND APTType.id = APSofaType.type_id
    INNER JOIN ActionProperty_Reference APRSofaType ON APSofaType.id = APRSofaType.id
    INNER JOIN rbSofa ON APRSofaType.value = rbSofa.id

    INNER JOIN Action AValue ON Event.id = AValue.event_id AND AValue.deleted = 0
    INNER JOIN ActionType ATValue ON AValue.actionType_id = ATValue.id AND ATValue.flatCode = 'leaved'
    INNER JOIN ActionPropertyType APTValue ON ATValue.id = APTValue.actionType_id AND APTValue.name = 'Оценка шкалы'
    INNER JOIN ActionProperty APValue ON AValue.id = APValue.action_id AND APTValue.id = APValue.type_id
    INNER JOIN ActionProperty_String APSValue ON APValue.id = APSValue.id
WHERE Event.id = %i
            ''' % eventId)
        return record

    def getDirectRecord(self, eventId):
        if eventId in self.eventIdList_Direct:
            return None
        else:
            self.eventIdList_Direct.append(eventId)
        u""" i3487
            по доп фаилу с направлением:
            структура описана в фаиле "Импорт направлений.docx"
            фаил формируется только для случаев диспансеризации и ВМП

                1. разобраться с глобальной настройкой №21(направления). почему в питере возможные значения 0,1,2. а в краснодаре да, нет?
                2. ВМП. в гуй интерфейса направления необходимо добавить:
                    "дата плановой госпитализации" после даты выдачи направления

            при выгрузке данных в фаил _D заполнять:
                SERV_ID из основного фаила счетов
                D_NUMBER - номер направления
                DATE_ISSUE - дата выдачи направления
                DATE_PLANG - дата плановой госпитализации
            диспансеризация:
                на базе ant_p48 сделан actiontype с flatcode = directionD
                Тип направления (назначения)
                    ID_D_TYPE(фаила экспорта *_D) = rbDType_eis.code
                Идентификатор специальности врача
                    ID_PRVS(фаила экспорта *_D) = rbSpeciality.regionalCode
                Идентификатор вида обследования
                    ID_OB_TYPE(фаила экспорта *_D) = rbOBSType_eis.code
                Идентификатор профиля койки
                    ID_B_PROF(фаила экспорта *_D) = rbHospitalBedProfile.regionalCode
        """
        record = QtGui.qApp.db.getRecordEx(
            stmt=u'''
                SELECT
                    rbResult.regionalCode AS resultCode,
                    Referral.number AS D_NUMBER,
                    Referral.date AS DATE_ISSUE,
                    Referral.hospDate AS DATE_PLANG,
                    IF(
                        Event.hmpKind_id IS NOT NULL
                        OR Event.hmpMethod_id IS NOT NULL
                        OR EXISTS(
                            SELECT * FROM
                                Action
                                INNER JOIN ActionType ATType ON Action.actionType_id = ATType.id AND ATType.flatCode = 'moving'
                            WHERE
                                Action.event_id = Event.id
                                AND (Action.hmpKind_id IS NOT NULL OR Action.hmpMethod_id IS NOT NULL)
                        ), 1, 0
                    ) AS isHmp,
                    (
                        SELECT
                            rbDType_eis.code
                        FROM Action AType
                            INNER JOIN ActionType ATType ON AType.actionType_id = ATType.id AND ATType.flatCode = 'directionD'
                            INNER JOIN ActionPropertyType APTType ON ATType.id = APTType.actionType_id AND APTType.descr = 'ID_D_TYPE'
                            INNER JOIN ActionProperty APSofaType ON AType.id = APSofaType.action_id AND APTType.id = APSofaType.type_id
                            INNER JOIN ActionProperty_Reference APRSofaType ON APSofaType.id = APRSofaType.id
                            INNER JOIN rbDType_eis ON APRSofaType.value = rbDType_eis.id
                        WHERE
                            Event.id = AType.event_id AND AType.deleted = 0
                        LIMIT 1
                    ) AS ID_D_TYPE,
                    (
                        SELECT
                            rbSpeciality.regionalCode
                        FROM Action AType
                            INNER JOIN ActionType ATType ON AType.actionType_id = ATType.id AND ATType.flatCode = 'directionD'
                            INNER JOIN ActionPropertyType APTType ON ATType.id = APTType.actionType_id AND APTType.descr = 'ID_PRVS'
                            INNER JOIN ActionProperty APSofaType ON AType.id = APSofaType.action_id AND APTType.id = APSofaType.type_id
                            INNER JOIN ActionProperty_Reference APRSofaType ON APSofaType.id = APRSofaType.id
                            INNER JOIN rbSpeciality ON APRSofaType.value = rbSpeciality.id
                        WHERE
                            Event.id = AType.event_id AND AType.deleted = 0
                        LIMIT 1
                    ) AS ID_PRVS,
                    (
                        SELECT
                            rbOBSType_eis.code
                        FROM
                            Action AType
                            INNER JOIN ActionType ATType ON AType.actionType_id = ATType.id AND ATType.flatCode = 'directionD'
                            INNER JOIN ActionPropertyType APTType ON ATType.id = APTType.actionType_id AND APTType.descr = 'ID_OB_TYPE'
                            INNER JOIN ActionProperty APSofaType ON AType.id = APSofaType.action_id AND APTType.id = APSofaType.type_id
                            INNER JOIN ActionProperty_Reference APRSofaType ON APSofaType.id = APRSofaType.id
                            INNER JOIN rbOBSType_eis ON APRSofaType.value = rbOBSType_eis.id
                        WHERE
                            Event.id = AType.event_id AND AType.deleted = 0
                        LIMIT 1
                    ) AS ID_OB_TYPE,
                    (
                        SELECT
                            rbHospitalBedProfile.regionalCode
                        FROM
                            Action AType
                            INNER JOIN ActionType ATType ON AType.actionType_id = ATType.id AND ATType.flatCode = 'directionD'
                            INNER JOIN ActionPropertyType APTType ON ATType.id = APTType.actionType_id AND APTType.descr = 'ID_B_PROF'
                            INNER JOIN ActionProperty APSofaType ON AType.id = APSofaType.action_id AND APTType.id = APSofaType.type_id
                            INNER JOIN ActionProperty_Reference APRSofaType ON APSofaType.id = APRSofaType.id
                            INNER JOIN rbHospitalBedProfile ON APRSofaType.value = rbHospitalBedProfile.id
                        WHERE
                            Event.id = AType.event_id AND AType.deleted = 0
                        LIMIT 1
                    ) AS ID_B_PROF,
                    (
                        SELECT
                            rbDTypeGroup_eis.code
                        FROM
                            Action A
                            INNER JOIN ActionType AT ON AT.id = A.actionType_id AND AT.flatCode = 'directionD'
                            INNER JOIN ActionPropertyType APT ON APT.actionType_id = AT.id AND APT.descr = 'ID_GROUP'
                            INNER JOIN ActionProperty AP ON AP.action_id = A.id AND AP.type_id = APT.id AND AP.deleted = 0
                            INNER JOIN ActionProperty_Reference APRef ON APRef.id = AP.id
                            INNER JOIN rbDTypeGroup_eis ON rbDTypeGroup_eis.id = APRef.value
                        WHERE
                            A.event_id = Event.id AND A.deleted = 0
                        LIMIT
                            0, 1
                    ) AS D_GROUP
                FROM Event
                    LEFT JOIN Referral ON Event.referral_id = Referral.id
                    LEFT JOIN rbResult ON rbResult.id = Event.result_id
                WHERE Event.id = %s
            ''' % eventId
        )
        return record

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
                kindCode = forceString(QtGui.qApp.db.translate('rbMedicalAidKind', 'id', kindId, 'code'))
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

    def getPersonIdentifier(self, personId, eisLpuId):
        return '%s.%s' % (eisLpuId, personId)

    def getOrgStructureIdentifier(self, personId, personFormat='id'):
        db = QtGui.qApp.db
        if personFormat != 'id':
            personId = '\'%s\'' % personId
        stmt = 'SELECT o.infisCode FROM OrgStructure o INNER JOIN Person p ON p.orgStructure_id = o.id WHERE p.%s = %s' % (personFormat, personId)
        query = db.query(stmt)
        if query.first():
            return forceStringEx(query.record().value(0))
        return '1'

    def clientDoesNotHaveEISId(self, clientId):
        asEIS = '2'
        asEISMU = '3'
        db = QtGui.qApp.db
        tableClientIdentification = db.table('ClientIdentification')
        tableAccountingSystem = db.table('rbAccountingSystem')
        table = tableClientIdentification.leftJoin(tableAccountingSystem, tableAccountingSystem['id'].eq(tableClientIdentification['accountingSystem_id']))
        cnt = db.getCount(table, where=db.joinAnd([tableClientIdentification['client_id'].eq(clientId), tableClientIdentification['deleted'].eq(0), 'YEAR(ClientIdentification.checkDate) = YEAR(CURRENT_DATE)', tableAccountingSystem['code'].inlist((asEIS, asEISMU))]))
        return cnt == 0

    def getClientRepresentativeInfo(self, clientId):
        key = clientId
        result = self._representativeInfoCache.get(key)

        if not result:
            result = getClientRepresentativeInfo(clientId)
            self._representativeInfoCache[key] = result

        return result

    def getClientAddressParts(self, clientId, addrType):
        addrRecord = self.getAddrRecord(clientId, addrType)
        if not addrRecord and addrType == 0:
            addrRecord = self.getAddrRecord(clientId, 1)
        eisAddrType = u''
        regOkatoId = 0
        houseId = 0
        house = ''
        corpus = ''
        flat = ''
        street = ''
        streetTypeId = 0
        KLADRCode = ''
        freeInput = ''
        if addrRecord:
            KLADRCode = forceString(addrRecord.value('KLADRCode'))
            freeInput = forceString(addrRecord.value('freeInput')) if addrRecord else ''
            street = '-'
            streetType = forceString(addrRecord.value('streetType'))
            streetTypeId = self.streetTypeDict.get(streetType, self.streetTypeDict[''])
            house = forceString(addrRecord.value('number'))
            corpus = forceString(addrRecord.value('corpus'))
            flat = forceString(addrRecord.value('flat'))
            if KLADRCode.startswith('78'):
                eisAddrType = u'г'
                regOkatoId = 78
                houseId = self.getEisHouseId(addrRecord.value('KLADRCode'), addrRecord.value('KLADRStreetCode'), addrRecord.value('number'), addrRecord.value('corpus'))
            elif KLADRCode:
                eisAddrType = u'р'
                regOkatoId = int(KLADRCode[:2])
                regOkatoId = self.mapKladrCodeToIdRegion.get(regOkatoId, regOkatoId)
            else:
                eisAddrType = u'п'
        return (eisAddrType,
                regOkatoId,
                houseId,
                house,
                corpus,
                flat,
                freeInput,
                KLADRCode,
                street,
                streetTypeId)

    def getEisHouseId(self, KLADRCode, KLADRStreetCode, number, corpus):
        db = QtGui.qApp.db
        number = trim(number)
        corpus = trim(corpus)
        EIS_db = QtGui.qApp.EIS_db
        if (not EIS_db):
            stmt = u'''SELECT kladr.eisHouse.ID_HOUSE
                      FROM kladr.eisHouse
                      JOIN kladr.infisToEis ON kladr.infisToEis.ID_PREFIX = kladr.eisHouse.ID_PREFIX
                      LEFT JOIN kladr.infisSTREET ON kladr.infisSTREET.code = kladr.infisToEis.CODE_INF
                      LEFT JOIN kladr.infisSTREETYP ON kladr.infisSTREETYP.CODE = kladr.infisToEis.TYPE_INF
                      LEFT JOIN kladr.infisAREA ON kladr.infisAREA.CODE = kladr.infisToEis.AREA_INF
                      WHERE kladr.infisSTREET.KLADR = '%s' AND IF(kladr.infisAREA.KLADR, kladr.infisAREA.KLADR = '%s', 1)
                            AND kladr.eisHouse.HOUSE = '%s' %s
                      LIMIT 1'''
            if forceString(corpus):
                corpusCond = u'AND kladr.eisHouse.KORPUS = \'%s\'' % forceString(corpus)
            else:
                corpusCond = u''
            query = db.query(stmt % (forceString(KLADRStreetCode), forceString(KLADRCode), forceString(number), corpusCond))
            if query.first():
                record = query.record()
                return forceInt(record.value(0))
            return 0
        else:
            # пытаемся найти данные напрямую в базе ЕИС
            strStmt = u'''select SOCR, NAME from kladr.STREET where `CODE` like "'''+forceString(KLADRStreetCode)+'''%" and `CODE` like '%00' limit 1'''
            nasStmt = u'''select SOCR, NAME from kladr.KLADR where `CODE` like "'''+forceString(KLADRCode)+'''%" and `CODE` like '%00' limit 1'''
            queryStr = db.query(strStmt)
            queryNas = db.query(nasStmt)
            if (queryStr.first() and queryNas.first() and EIS_db):
                recordStr = queryStr.record()
                recordNas = queryNas.record()

                nas = forceString(recordNas.value('NAME'))
                if nas == u'''Петергоф''':
                   nas = u'''Петродворец'''
                elif nas in (u'Торики', u'Володарская', u'Горелово'):
                    nas = u'''Санкт-Петербург'''
                elif nas == u'''Александровская (Пушкинский р-н)''':
                    nas = u'''Александровская'''

                socr = forceString(recordStr.value('SOCR'))
                socr = self.mapKladrStrSocrToEis.get(socr, socr)


                strName = forceString(recordStr.value('NAME'))

                if strName == u'Заводская 2-я' and nas == u'Старо-Паново':
                    strName = u'Заводская 1-я'

                # strName = strName.replace(u' В.О.', u'')
                if strName.upper().endswith(u' ВО'):
                    strName = strName[:-2] + u'В.О.'
                if strName.upper().endswith(u' ПС'):
                    strName = strName[:-2] + u'П.С.'
                if strName.find(' (') != -1:
                    strName = strName[:strName.find(' (')]
                if strName.find('(') != -1:
                    strName = strName[:strName.find(' (')]
                strNameSplit = strName.rsplit(' ', 1)
                if len(strNameSplit) > 1:
                    prefix = strNameSplit[0]
                    strNameSplit[0] = numberToWords(strNameSplit[0])
                    strName = u' '.join(strNameSplit)
                if len(strNameSplit) == 2:
                    suffix = strNameSplit[1]
                    body = strNameSplit[0]
                    if suffix == u'Б.':
                        strName = u'Б%' + body              # Большой Сампсониевский в ЕИС vs Сампсониевский Б. в КЛАДР
                    elif suffix == u'М.':
                        strName = u'М%' + body              # Аналогично
                    elif suffix[-2:] in (u'-я', u'-й'):     # 2-й Рабфаковский в ЕИС vs Рабфаковский 2-й в КЛАДР
                        strName = suffix + ' ' + body
                if len(strNameSplit) == 1 and nas == u'Песочный' and strName[-1:] in (u'-й', u'-я') and socr == '-':
                    strName = strName + u' квартал'
                if strName == u'Лесное ГПЗ':
                    strName = u'Лесное'

                if strName == u'Заводской' and nas == u'Санкт-Петербург' and socr == u'пер.':
                    nas = u'Ломоносов'

                eisStmt = u"""SELECT
                      FIRST 1
                      h.ID_HOUSE
                    FROM HOUSE h
                      LEFT JOIN PREFIX p ON p.ID_PREFIX = h.ID_PREFIX
                      LEFT JOIN GEONIM_NAME gn ON p.ID_GEONIM_NAME = gn.ID_GEONIM_NAME
                      LEFT JOIN T_GEONIM tg ON p.ID_GEONIM_TYPE = tg.ID_GEONIM_TYPE
                      LEFT JOIN TOWN t1 ON p.ID_TOWN = t1.ID_TOWN
                    WHERE
                      h.IS_ACTIVE = 1
                      AND p.IS_ACTIVE = 1
                      AND t1.IS_ACTIVE = 1
                      AND t1.TOWN_NAME LIKE '%"""+nas+"""'
                      AND UPPER(gn.GEONIM_NAME COLLATE WIN1251) LIKE '"""+strName.upper()+"""'
                      AND tg.GEONIM_TYPE_NAME ='"""+socr+"""'"""
                if (forceString(number) != u''):
                    eisStmt += u""" AND h.HOUSE = '"""+forceString(number)+"""'"""
                if (forceString(corpus) != u''):
                    eisStmt += u""" AND h.KORPUS = '"""+forceString(corpus)+"""'"""
                eisQuery = EIS_db.query(eisStmt)
                if (eisQuery.first()):
                    eisRecord = eisQuery.record()
                    res = forceInt(eisRecord.value(0))
                else:
                    print "HOUSE_ID: "+forceString(KLADRCode)+", s="+forceString(KLADRStreetCode)+", h="+forceString(number)+", c="+forceString(corpus)
                    if (forceString(corpus) != u''):
                        res = self.getEisHouseId(KLADRCode, KLADRStreetCode, number, u'')
                    else:
                        if (forceString(number) != u''):
                            res = self.getEisHouseId(KLADRCode, KLADRStreetCode, u'', u'')
                        else:
                            res = 0
                    print "Res = "+forceString(res)
                return forceInt(res)
            else:
                return 0

    def getIdGosp(self, isDayStationary, eventSetDate, eventExecDate, movingOSType):
        if isDayStationary:
            return 4        # Дневной стационар
        elif movingOSType == 4:
            return 2        # Приемное отделение
        elif eventSetDate.secsTo(eventExecDate) < 86400:#externalId.lower().startswith(u'о') :
            return 3        # Досуточная госпитализация
        else:
            return 1        # Госпитализация

    def isComplete(self):
        return self.done

    def abort(self):
        self.aborted = True

    def updateBtnExport(self):
        exportNotEmpty = ( self.chkIncludeEvents.isChecked()
                           or self.chkIncludeVisits.isChecked()
                           or self.chkIncludeActions.isChecked() )
        eisLpuIdPresent = self.edtEisLpuId.text() != ''
        self.btnExport.setEnabled(exportNotEmpty and eisLpuIdPresent)

    @QtCore.pyqtSlot(bool)
    def on_chkIncludeEvents_toggled(self, value):
        self.updateBtnExport()

    @QtCore.pyqtSlot(bool)
    def on_chkIncludeVisits_toggled(self, value):
        self.updateBtnExport()

    @QtCore.pyqtSlot(bool)
    def on_chkIncludeActions_toggled(self, value):
        self.updateBtnExport()

    @QtCore.pyqtSlot(QString)
    def on_edtEisLpuId_textChanged(self, value):
        self.updateBtnExport()

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        includeEvents = self.chkIncludeEvents.isChecked()
        includeVisits = self.chkIncludeVisits.isChecked()
        includeActions = self.chkIncludeActions.isChecked()
        exportClients = self.chkExportClients.isChecked()
        eisLpuId = unicode(self.edtEisLpuId.text())
        possibleFormats = {0:'id', 1:'code', 2:'regionalCode', 3:'federalCode'}
        personFormat = possibleFormats[self.cmbPersonFormat.currentIndex()]
        if (includeEvents or includeVisits or includeActions) and eisLpuId:
            QtGui.qApp.preferences.appPrefs['EISOMSLpuId'] = toVariant(eisLpuId)
            QtGui.qApp.preferences.appPrefs['EISOMSExportClients'] = toVariant(exportClients)
            self.export(self.chkIgnoreConfirmation.isChecked(), exportClients, includeEvents, includeVisits, includeActions, eisLpuId, personFormat)

    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.abort()


class CExportEISOMSPage2(QtGui.QWizardPage, Ui_ExportEISOMSPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'EISOMSExportDir', homePath))
        self.edtDir.setText(exportDir)

    def isComplete(self):
        return self.pathIsValid

    def validatePage(self):
        src = self.wizard().getFullDbfFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
        success, result = QtGui.qApp.call(self, shutil.move, (src, dst))
        if success:
            QtGui.qApp.preferences.appPrefs['EISOMSExportDir'] = toVariant(self.edtDir.text())
            self.wizard().setAccountExposeDate()
        if forceBool(QtGui.qApp.preferences.appPrefs['EISOMSExportClients']):
            src = self.wizard().getFullClientsDbfFileName()
            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (src, dst))

        if not isUslDbfEmpty:
            src = self.wizard().getUslDbfFileName()
            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (src, dst))
        if not isSluchDbfEmpty:
            src = self.wizard().getSluchDbfFileName()
            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (src, dst))
        if not isDirectDbfEmpty:
            src = self.wizard().getDirectDbfFileName()
            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (src, dst))

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
                u'Выберите директорию для сохранения файла выгрузки в ЕИС-ОМС',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
