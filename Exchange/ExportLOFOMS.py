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
from KLADR.KLADRModel import getStreetName, getCityName

from Ui_ExportLOFOMSPage1 import Ui_ExportLOFOMSPage1
from Ui_ExportLOFOMSPage2 import Ui_ExportLOFOMSPage2
from Ui_ExportLOFOMSPage3 import Ui_ExportLOFOMSPage3


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number, exposeDate, payer_id', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        number = forceString(accountRecord.value('number'))
        payerId = forceRef(accountRecord.value('payer_id'))
    else:
        date = exposeDate = payerId = None
        number = ''
    return date, number, exposeDate, payerId


def getPostIndex(KLADRCode, KLADRStreetCode, house, corpus):
    """Ищет почтовый индекс по адресу"""
    db = QtGui.qApp.db
    postIndex = forceString(db.translate('kladr.STREET', 'CODE', KLADRStreetCode, '`INDEX`'))
    if KLADRStreetCode and not postIndex:
        firstPart = house.split('/')[0]
        if re.match('^\d+$', firstPart):
            intHouse = int(firstPart)
        else:
            intHouse = None
        table = db.table('kladr.DOMA')
        cond=table['CODE'].like(KLADRStreetCode[:-2]+'%')
        list = db.getRecordList(table, 'CODE,NAME,KORP,`INDEX`', where=cond)
        for record in list:
            NAME=forceString(record.value('NAME'))
            KORP=forceString(record.value('KORP'))
            if checkHouse(NAME, KORP, house, intHouse, corpus):
                postIndex = forceString(record.value('INDEX'))
                break
    return postIndex


def myFormatAddress(KLADRCode, KLADRStreetCode, number, corpus, flat):
    parts = []
    if KLADRCode:
        parts.append(getCityName(KLADRCode))
    if KLADRStreetCode:
        parts.append(getStreetName(KLADRStreetCode))
    if number:
        parts.append(u'д. '+number)
    if corpus:
        parts.append(u'к. '+corpus)
    if flat:
        parts.append(u'кв. '+flat)
    return ', '.join(parts)


def exportLOFOMS(widget, accountId, accountItemIdList):
    wizard = CExportWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportLOFOMSPage1(self)
        self.page2 = CExportLOFOMSPage2(self)
        self.page3 = CExportLOFOMSPage3(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.addPage(self.page3)
        self.setWindowTitle(u'Мастер экспорта в ЛОФОМС')
        self.dbfFileName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, payerId = getAccountInfo(accountId)
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page2.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page3.setTitle(u'Укажите директорию для сохранения обменных файлов "*.dbf"')


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('lofoms')
        return self.tmpDir


    def getFullDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '.dbf')


    def setAccountItemsIdList(self, accountItemIdList):
        self.page2.setAccountItemsIdList(accountItemIdList)


    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()
        QtGui.qApp.preferences.appPrefs['ExportLOFOMSVerboseLog'] = toVariant(
                self.page2.chkVerboseLog.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportLOFOMSIgnoreErrors'] = toVariant(
                self.page2.chkIgnoreErrors.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportLOFOMSActionTypeCytological'] = toVariant(
                self.page1.cmbActionTypeCytological.value())
        QtGui.qApp.preferences.appPrefs['ExportLOFOMSActionTypeFluorography'] = toVariant(
                self.page1.cmbActionTypeFluorography.value())


class CExportLOFOMSPage1(QtGui.QWizardPage, Ui_ExportLOFOMSPage1):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'Настройки экспорта счета. Для выполнения шага нажмите кнопку "Вперед".')
        actionTypeCytological = forceRef(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportLOFOMSActionTypeCytological', None))
        actionTypeFluorography = forceRef(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportLOFOMSActionTypeFluorography', None))
        if actionTypeCytological == None:
            actionTypeCytological = self.lookupActionTypeByName(u'цитологическ')
        if actionTypeFluorography == None:
            actionTypeFluorography = self.lookupActionTypeByName(u'флюорограф')
        self.cmbActionTypeCytological.setValue(actionTypeCytological)
        self.cmbActionTypeFluorography.setValue(actionTypeFluorography)


    def lookupActionTypeByName(self, name):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        record = db.getRecordEx(tableActionType, 'id', tableActionType['name'].like(u'%'+name+'%'))
        if record:
            return forceRef(record.value(0))
        return None


    def validatePage(self):
        return self.cmbActionTypeCytological.value() != None and \
                    self.cmbActionTypeFluorography.value() != None


    @QtCore.pyqtSlot(int)
    def on_cmbActionTypeFluorography_indexChanged(self, index):
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot(int)
    def on_cmbActionTypeCytological_indexChanged(self, index):
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CExportLOFOMSPage2(QtGui.QWizardPage, Ui_ExportLOFOMSPage2):
    mapDocTypeToLOFOMS = { '1' : u'Н', '14': u'П', '3': u'С', '13': u'В', None: ' '}
                                            # "П"-паспорт старого образца с 14 лет и старше,
                                            #  "Н"-паспорт нового образца с 14 лет и старше,
                                            #  "С"-до 14 полных лет,
                                            #  "В"-временное удостоверение личности - заглавные
                                            #      русские буквы
                                            #  " "- в случае отсутствия документа
    mapKLADRCodeToLiveIn = {'78': u'С', '47':u'Л', None: u'П'}
    mapINNToWorkIn = {'78': u'С', '47':u'Л', None: u'П'}
    mapSceneCodeToVisitPlace = {'1':' ', '2':'uД', '3':u'А', '4':' '}
    mapDispanserCode = {'1':'1', '2':'2', '3':'3', '4':'0', '5':'0', '6':'1' , '7':'0'}
    # (1-состоит, 2-взят, 3-снят, 0-не состоит)
    mapDispanserCodeToCancelReason = {'4':'1', '5':'3', '3':'0'}
    # причина снятия с дисп. наблюдения (1- выздоровление, 2-переезд, 3-смерть, 0-отсутствует)
    mapSanatoriumToRehabilitationCode = {'2':'1', '3':'1', '1':'0', '0':'0'}
    # (1-санаторно-курортное лечение, 2-прочее, 0-не было)
    mapAccountType = {0:' ', 1:u'И', 2:u'Р', 3:u'Л', 4:u'з', 5:u'и', 6:u'р', 7:u'л'}
    mapEducation = {6:'1', 2: '2', 3:'2', 4:'2', 1:'3', 0:'4'}
    mapTraumaType = {'01':'1', '02':'3', '03':'8', '04':'2', '05':'5', '06':'6',
        '07':'7', '08':'8', '09':'9', '10':'10', '11':'11', '12':'11'}
    mapEventTypeCode = {
#'13', #'Неотложная медицинская помощь в ЛПУ'
'21':'14', #'Неотложная медицинская помощь на дому'
'01':'1', #'Лечебно-диагностический'
'02':'2', #'Консультативный'
'03':'3', '03-ДН':'3', #'Диспансерное наблюдение'
'04':'4', '05':'4',#'Профилактический'
'06':'5', #'Профессиональный осмотр'
'07':'6', #'Реабилитационный'
'08':'7', #'Зубопротезный'
'09':'8', #'Протезно-ортопедический'
#'9', #'Прочий'
'19':'10', #'Лечебно-диагностический (на дому)'
#'11', #'Направление на МСЭК'
#'12', #'Прием с выездом на село'
    }
    # образование (1-высшее, 2-среднее, 3-нач., 4-не имеет, 0-неизвестно)
    mapClientCategory = {
        '011':'1', #'ИВОВ'
        '02':'2', '020':'2', #'УВОВ'
        '05':'4', '050':'4', #'Блокадник'
        #'5', #'Нагр. орденами и медалями'
        #'6', #'Инвалид труда'
        '09':'7', #'Ребенок-инвалид'
        '03':'8', '030':'8', #'Участник боевых действий'
        '10':'9', '091':'9', #'Подверженный рад. облучению'
        '830':'10', #'Реабилитированный'
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
        self.tariffCache = {}
        self.parent = parent
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportLOFOMSIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportLOFOMSVerboseLog', 'False')))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.knownLOFOMSCodes = {}
        self.educationIdList = []


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
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
        self.educationIdList = self.createEducationIdList()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query


    def export(self):
        QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


    def createApPostRecord(self, dbf, icCode, ambCode, icfCode, fieldLpuType, accountType):
        accDate, accNumber, exposeDate, payerId = getAccountInfo(self.parent.accountId)
        strAccNumber = accNumber if trim(accNumber) else u'б/н'
        begDate = accDate # fixme
        (dbfApPost, dbfAppPost, dbfCupPost, dbfMepPost, dbfAmpPost) = dbf
        dbfRecord = dbfApPost.newRecord()
        # 1.* ## код ЛПУ (значение из справочника S_POL)
        dbfRecord['AMB_CODE']   = ambCode
        # 2.* ## СМО (значение из справочника S_COMP)
        dbfRecord['IC_CODE']   = icCode
        # 3.* ## подразделение фонда, в которое выставлен счет
        #  (значение из справочника S_FIL_L, либо "00" - если счет
        #   выставлен в расчетный отдел  ЛОФОМС областными
        #   мед. учреждениями)
        dbfRecord['ICF_CODE']  = icfCode
        # 4.* дата формирования счета (дата в диапазоне от FinishDate до текущей даты)
        dbfRecord['Mak_Date'] = pyDate(exposeDate)
        # 5.* начальная дата
        dbfRecord['StartDate'] = pyDate(begDate)
        # 6.* конечная дата
        dbfRecord['FinishDate']= pyDate(accDate)
        # 7.* последняя часть номера сводного счета
        dbfRecord['Descript']   = strAccNumber[-8:]
        # 8.* категория счета
        dbfRecord['RespFlag']  = accountType
        # 9.* тип счета, заполняется из справочника типов счетов
        dbfRecord['lpu_type'] = fieldLpuType
        dbfRecord.store()


    def exportInt(self):
        # ид типов действий для поиска даты флюорографии и цитологического исследования
        self.actionTypeCytologicalId = self.parent.page1.cmbActionTypeCytological.value()
        self.actionTypeFluorography = self.parent.page1.cmbActionTypeFluorography.value()
        self.currentSMO = None
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        self.chkIgnoreErrors.setEnabled(False)
        self.chkVerboseLog.setEnabled(False)
        self.btnExport.setEnabled(False)
        isRFAccount = self.parent.page1.chkRFAccount.isChecked() # счет по РФ
        accountType = self.mapAccountType.get(\
            self.parent.page1.cmbAccountType.currentIndex(),' ')

        dbf, query = self.prepareToExport()
        currentOrgINN = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'INN'))
        accDate, accNumber, exposeDate, payerId = getAccountInfo(self.parent.accountId)
        # код ЛПУ (значение из справочника S_POL), ищем по ИНН
        ambCode = forceString(QtGui.qApp.db.translate('LOFOMS.S_POL', 'IIN', currentOrgINN, 'N'))
        payerINN = forceString(QtGui.qApp.db.translate('Organisation', 'id', payerId, 'INN'))
        fieldLpuType = '0'
        icfCode = None

        if currentOrgINN[:2] == '47':  # областное мед.учреждение
            self.log(u'ИНН организации "%s" является областным.' % currentOrgINN)
            icfCode = '00'
        else:
            self.log(u'ИНН плательщика "%s". (id=%d)' % (payerINN, payerId))
            if payerINN:
                icfCode = forceString(QtGui.qApp.db.translate('LOFOMS.S_FIL_L', 'IIN', payerINN, 'N'))

            if not icfCode:
                self.log(u'Поиск по ИНН не удался. Используем код ИНФИС.')
                icfCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', payerId, 'infisCode'))

        self.log(u'Используем код ИНФИС для плательщика: "%s".' % icfCode)

        if (not icfCode) or (not self.isValidLOFOMSrbCode(icfCode, 'N', 'S_FIL_L')):
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                u' код "%s" не найден в таблице S_FIL_L (id плательщика %d)' % (icfCode, payerId), True)
            if not self.ignoreErrors:
                self.abort()

        if self.idList:
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), ambCode, accDate, \
                        currentOrgINN, isRFAccount, accountType, fieldLpuType, icfCode, payerINN)
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        for x in dbf:
            x.close()

        self.chkIgnoreErrors.setEnabled(True)
        self.chkVerboseLog.setEnabled(True)
        self.btnExport.setEnabled(True)


    def createDbf(self):
        return (self.createApPostDbf(), self.createAppPostDbf(),
                    self.createCupPostDbf(), self.createMepPostDbf(),
                    self.createAmpPostDbf())


    def createApPostDbf(self):
        """ Создает структуру dbf для AP_POST.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'AP_POST.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(   # *  - обязательное поле  ## - заполняется значениями из справочника
            ('AMB_CODE', 'C', 3), # 1.* ## код ЛПУ (значение из справочника S_POL)
            ('IC_CODE', 'C', 2),   # 2.* ## СМО (значение из справочника S_COMP)
            ('ICF_CODE', 'C', 2), # 3.* ## подразделение фонда, в которое выставлен счет
                                            #  (значение из справочника S_FIL_L,
                                            #  либо "00" - если счет выставлен в расчетный отдел
                                            #  ЛОФОМС областными мед. учреждениями)
            ('Mak_Date', 'D'),     # 4.* дата формирования счета (дата в диапазоне
                                            #    от FinishDate до текущей даты)
            ('StartDate', 'D'),   # 5.* начальная дата
            ('FinishDate', 'D'),  # 6.* конечная дата
            ('Descript', 'C', 8), # 7.* последняя часть номера сводного счета
            ('RespFlag', 'C', 1), # 8.* категория счета
                                            #(' ' - счет за застрахованных жителей  Лен.области,
                                            # 'И' – счет за иные категории граждан
                                            #        (условно застрахованные),
                                            # 'Р' – счет за жителей других субъектов
                                            #         Российской Федерации (кроме
                                            #        Санкт-Петербурга),
                                            # 'Л' – счет за жителей Ленинградской
                                            #         области, работающих на
                                            #         предприятиях Российской Федерации)
                                            # 'з' - счет за застрахованных жителей
                                            #       Лен.области по стоматологии,
                                            # 'и' – счет за иные категории граждан
                                            #       (условно застрахованные) по стоматологии,
                                            # 'р' – счет за жителей других субъектов
                                            #         Российской Федерации (кроме
                                            #        Санкт-Петербурга) по стоматологии,
                                            # 'л' – счет за жителей Ленинградской
                                            #         области, работающих на
                                            #         предприятиях Российской Федерации
                                            #         по стоматологии
            ('lpu_type', 'C', 1)   # 9.* тип счета, заполняется из справочника типов счетов
        # Уникальность поддерживается полями AMB_CODE, IC_CODE, Mak_Date, lpu_type,RespFlag.
            )
        return dbf


    def createAppPostDbf(self):
        """APP_POST.DBF - перечень пациентов амбулатории"""

        dbfName = os.path.join(self.parent.getTmpDir(), 'APP_POST.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(   # *  - обязательное поле  ## - заполняется значениями из справочника
            ('code', 'C', 8),       # 1.* уникальный номер пациента (число с ведущими нулями)
            ('DOC_TYPE', 'C', 1), # 2. регистрационный документ - паспорт, свидетельство,
                                            #  временное удостоверение
                                            # ("П"-паспорт старого образца с 14 лет и старше,
                                            #  "Н"-паспорт нового образца с 14 лет и старше,
                                            #  "С"-до 14 полных лет,
                                            #  "В"-временное удостоверение личности - заглавные
                                            #      русские буквы
                                            #  " "- в случае отсутствия документа)
            ('DOC_NUMB', 'C', 7), # 3. номер паспорта (семизначное число с ведущими
                                            #  нулями, но не более 0999999 для паспорта или
                                            #  свидетельства о рождении)
            ('SERIA_NUM', 'C', 2), # 4. первая часть серии документа
                                            #( - аpабский эквивалент римского числа для
                                            #    паспорта старого образца или св-ва о  рождении,
                                            #  - двузначное число в диапазоне 1..99 для
                                            #    паспорта нового образца,
                                            #  - номер отделения милиции СПб для временного
                                            #    удостоверения личности застрахованного,
                                            #    прописанного в СПб,
                                            #  - код отделения милиции Лен.области для
                                            #    временного удостоверения личности
                                            #    застрахованного, прописанного в Лен.области,
                                            #    заполняемый из справочника
                                            #  - "00" - в случае отсутствия рег. документа
            ('SERIA_LET', 'C', 2), # 5. вторая часть в серии документа
                                            #( - две заглавные русские буквы для паспорта
                                            #    старого образца или свидетельства о рождении,
                                            #  - две цифры для паспорта нового образца,
                                            #  - "СП" для временного удостоверения личности
                                            #    застрахованного, прописанного в СПб,
                                            #  - "ЛО" для временного удостоверения личности
                                            #    застрахованного, прописанного в Лен.области)
                                            #  - "  " в случае отсутствия рег. документа
            ('SURNAME', 'C', 20), # 6.* фамилия (обязательно русскими буквами)
            ('NAME', 'C', 18),      # 7.* имя (обязательно русскими буквами)
            ('SEC_NAME', 'C', 22), # 8. отчество (обязательно русскими буквами)
            ('BIRTHDAY', 'D'),     # 9.* дата рождения - в диапазоне от 01/01/1880 до текущей даты
            ('SEX', 'C', 1),         # 10.* пол ("М" или "Ж")-заглавные русские буквы
            ('LIVE_IN', 'C', 1),  # 11.* где проживает (Лен.обл., С-П/б., Россия, Прочее)-
                                            #  ("Л" "С" "Р" "П")-заглавные русские буквы
            ('DIS_CODE', 'C', 2), # 12.  ## номер района прописки ("00", либо значение из
                                            #  справочника S_FIL)
            ('CP_CODE', 'C', 3),  # 13.   ##  населенный пункт ("000", либо значение из
                                            #  справочника NPUNKT)
            ('STREET', 'C', 40),   # 14. улица по прописке
            ('HOUSE', 'C', 7),      # 15. дом по прописке
            ('BUILDING', 'C', 2), # 16. корпус по прописке
            ('FLAT', 'C', 4),        # 17. квартира по прописке (четырехзначный номер с
                                            #  ведущими нулями)
            ('ADDRESS', 'C', 70), # 18.* адрес фактического проживания
            ('WORK_IN', 'C', 1),  # 19.* место регистрации страхователя (Лен.обл., С-П/б.,
                                            #  Прочее)-("Л", "С", "П")-заглавные русские буквы
            ('INSURER', 'C', 78), # 20. страхователь (место работы для работающих,
                                            #  администрация района или другой источник для
                                            #  неработающих)
            ('TOWN_C', 'C', 1),    # 21.* житель считается ГОРОДСКИМ или СЕЛЬСКИМ ("Г" или
                                            #  "С")-заглавные русские буквы
            ('PAR_DOC', 'C', 20),   # 22.  документы родителей для иногородних детей
            ('PAR_NAME', 'C', 40), # 23. ФИО родителей для иногородних детей
#            ('POST_IND', 'C', 6), # 24. почтовый индекс
#            ('PHONE', 'C', 15),      # 25. телефон
#            ('PROF', 'C', 30),        # 26. должность по месту работы
            #Поле Code должно быть уникально для каждого пациента в пределах всей почтовой посылки
            # для возможности однозначного определения пациента. Кроме того, данные регистрационного
            # документа (в том случае, если они заполнены) должны быть уникальными в пределах всей почтовой посылки.
            )
        return dbf

    def createCupPostDbf(self):
        """перечень статистических талонов пациентов амбулатории"""

        dbfName = os.path.join(self.parent.getTmpDir(), 'CUP_POST.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(   # *  - обязательное поле  ## - заполняется значениями из справочника
            ('AMB_CODE', 'C', 3), #1.*   ##  код ЛПУ (значение из справочника, соответствует
                                            #  полю "amb_Code" файла AP_POST)
            ('YEAR', 'C', 2),          # 2.* год выписки стат.талона (число в диапазоне 0..99 с ведущими нулями)
            ('MONTH', 'C', 2),         # 3.* месяц выписки стат.талона (число в диапазоне 1..12 с ведущими нулями)
            ('Blank_Numb', 'C', 6),  # 4.* номер стат.талона (число с ведущими нулями)
            ('APP_CODE', 'C', 8),     # 5.* код пациента (соответствует полю "code" файла App_post.dbf)
            ('IC_CODE', 'C', 2),       # 6.* ##  СМО (значение из справочника, соответствует полю
                                                # "ic_code" файла AP_POST)
            ('ICF_CODE', 'C', 2), # 7.* ## подразделение фонда, в которое выставлен счет
                                            # (значение из справочника S_FIL_L либо "00",
                                            # соответствует полю "icf_code" файла AP_POST)
            ('Mak_Date', 'D'),     # 8.* дата формирования почты (соответствует полю
                                            #  "mak_date" файла AP_POST)
            ('A_INSURAN', 'C', 25), # 9.  иногородняя СМО
            ('A_POLIC_S', 'C', 8),  # 10. серия иногороднего полиса
            ('A_POLIC_N', 'C', 10), # 11.  номер иногороднего полиса
            ('POLIC_N', 'C', 6),     # 12.  номер полиса (число с ведущими нулями)
            ('POLIC_S', 'C', 3),     # 13.  серия полиса (заглавные русские буквы либо пробелы)
            ('cs_code', 'C', 3),     # 14.* ## клиническая служба (значение из справочника CL_SERVS)
            ('children', 'C', 1),    # 15. признак детского врача (1-есть, 0-нет)
            ('visit', 'C', 2),         # 16.* количество посещений
            ('StartDate', 'D'),      # 17.*дата обращения
            ('FinishDate', 'D'),    # 18.*дата выписки
            ('Education', 'C', 1),  # 19. образование (1-высшее, 2-среднее, 3-нач., 4-не
                                                #  имеет, 0-неизвестно)
            ('Cat_code', 'C', 3),    # 20.* ## категория пациента (значение из справочника CAT_PACS)
            ('IG_found', 'C', 1),     # 21. инвалидность (1-подтверждена,
                                                #  2-установлена впервые, 3-снята, 0-отсутствует)
            ('IG_group', 'C', 1),     # 22.  группа инвалидности (1, 2, 3, 0-отсутствует)
            ('IG_date', 'D'),          # 23. дата инвалидности (дата либо пробелы в случае отсутствия)
            ('He_group', 'C', 1),     #24.  группа здоровья (1, 2, 3, 0-отсутствует)
            ('NT_open', 'D'),          # 25. дата выдачи б/л (дата либо пробелы в случае отсутствия)
            ('NT_close', 'D'),        # 26. дата закрытия б/л (дата либо пробелы в случае отсутствия)
            ('MKB3', 'C', 3),           #27. ## основной диагноз (пробелы либо значения из
            ('MKB1', 'C', 1),           #28. ## справочника)
            ('illnes', 'C', 1),        #29. характер заболевания (" "-отсутствие информации,
                                                #  1–выявлено впервые, 2-ранее зарегистрированное,
                                                #  3-зарегистрировано в данном году)
            ('dispensary', 'C', 1),  # 30.  диспансерное наблюдение (1-состоит, 2-взят,
                                                #  3-снят, 0-не состоит)
            ('un_cause', 'C', 1),     # 31. причина снятия с дисп. наблюдения (1-
                                                #  выздоровление, 2-переезд, 3-смерть, 0-
                                                #  отсутствует)
            ('hospital', 'C', 1),     # 32. стационарное лечение (1-круглосуточный, 2-
                                                #  дневной, 3-стационар на дому, 4-дневной в б-це,
                                                #  0-не было)
            ('rehabilit', 'C', 1),   # 33.  реабилитация (1-санаторно-курортное лечение,
                                                #  2-прочее, 0-не было)
            ('ec_code', 'C', 3),       # 34.* ## повод обращения (значение из справочника E_COUSES)
            ('tt_code', 'C', 3),       # 35.  ## вид травмы ("000", либо значение из
                                                #  справочника TR_TYPES)
            ('FLURAGRAFY', 'D'),      # 36.  дата флюорографии (дата либо пробелы в случае
                                                #  отсутствия)
            ('CITOLOGY', 'D'),         # 37. дата цитологического обследования (дата либо
                                                #  пробелы в случае отсутствия)
            ('Summa', 'C', 14),        # 38.* сумма лечения (сумма в рублях, 2 знака после
                                                #  точки, ведущие - пробелы)
            ('rej_code', 'C', 3),     # 39.  ## причина возврата ("000" - при приеме почты из ЛПУ)
            ('P_A_Code', 'C', 3),     # 40.  ## лечебное учреждение, к которому
                                                #     прикреплен пациент (значение из
                                                #     справочника S_POL), заполняется
                                                #     значением «000» для квитанции,
                                                #     вошедшей в счет по РФ
            ('Mun_Code', 'C', 2),     # 41.  ## муниципальное образование пациента
                                                #       ("00" в случае прикрепления пациента к
                                                #       ЛПУ СПб, либо значение из справочника
                                                #       S_MUN в случае  прикрепления пациента
                                                #       к ЛПУ Лен.области) для квитанций,
                                                #       вошедших в счета на застрахованных и
                                                #       условно застрахованных;
                                                #       код территориального фонда для квитанций,
                                                #       вошедших в счет по РФ (значение из
                                                #       справочника S_TERR)
            ('Not_Prof', 'C', 1),     # 42. признак непрофильной службы ( 1 - непрофильная,
                                                #  0 - профильная)
            ('Sub_Div', 'C', 3),      # 43.* подразделение стационара ( 003 - дневной
                                                #  стационар амбулатории, 004 - в противном случае)
            ('RespFlag', 'C', 1),     # 44.* категория счета (значение из справочника,
                                                #  соответствует полю "RespFlag" файла AP_POST)
            ('Visit_01', 'C', 2),     # 45.  количество посещений по группе А (число с ведущими
                                                #  нулями)
            ('Visit_02', 'C', 2),     # 46. количество посещений по группе Б (число с ведущими
                                                #  нулями)
            ('Visit_03', 'C', 2),     # 47. количество посещений по группе В (число с ведущими
                                                #  нулями)
            ('Visit_04', 'C', 2),     # 48. резервное поле (заполняется пробелами)
            ('Visit_05', 'C', 2),     # 49. резервное поле (заполняется пробелами)
            ('Visit_06', 'C', 2),     # 50. резервное поле (заполняется пробелами)
            ('Visit_07', 'C', 2),     # 51. резервное поле (заполняется пробелами)
            ('Visit_08', 'C', 2),     # 52. резервное поле (заполняется пробелами)
            ('Visit_09', 'C', 2),     # 53. резервное поле (заполняется пробелами)
            ('Visit_10', 'C', 2),     # 54. резервное поле (заполняется пробелами)
            ('Visit_11', 'C', 2),     # 55. резервное поле (заполняется пробелами)
            ('Visit_12', 'C', 2),     # 56. резервное поле (заполняется пробелами)
            ('lpu_type', 'C', 1),     # 57.* тип счета (значение из справочника, соответствует
                                                #  полю "lpu_type" файла AP_POST)
            ('Y_PARENT', 'C', 2),     # 58. год выписки стат.талона «родителя» для формирования
                                                #  информации о «законченном случае лечения»
                                                #  (число в диапазоне 0..99 с ведущими нулями,
                                                #  пробелы в случае отсутствия информации), см.
                                                #  комментарий ниже
            ('M_PARENT', 'C', 2),     # 59. месяц выписки стат.талона «родителя» для
                                                #  формирования информации о «законченном случае
                                                #  лечения» (число в диапазоне 1..12
                                                #  с ведущими нулями, пробелы в случае отсутствия
                                                #  информации), см. комментарий ниже
            ('N_PARENT', 'C', 6),     # 60. номер стат.талона «родителя» для формирования
                                                #  информации о «законченном случае лечения»
                                                #  (число с ведущими нулями, пробелы в случае
                                                #  отсутствия информации), см. комментарий ниже
#            ('NE_CODE', 'C', 3),      # 61.  причина отсутствия полиса (значение из справочника
#                                                #  NOT_POLIS, либо "000")
#            ('Sg_code', 'C', 3),      # 62. социальная группа (значение из справочника
#                                                #  S_GRUP либо "000")
#            ('NT_spr', 'C', 1),        # 63. больничный лист либо справка (1-больничный лист,
#                                                #  2-справка, " " в случае отсутствия информации)
#            ('Date_wri', 'D'),        # 64. дата заполнения стат.талона
#            ('NTsprREA', 'C', 1),     # 65. (1-6) как в МВК," " в случае отсутствия
#                                                #информации
# Уникальность поддерживается полями AMB_CODE, YEAR, MONTH, Blank_Numb.
# В соответсвии с правилами заполнения формы 025-10/у-97 целый ряд квитанций
# может быть включен в один «законченный случай». Набор полей Y_PARENT,
# M_PARENT, N_PARENT определяет последовательность заполнения квитанций,
# относящихся к одному «законченному случаю» и представляет собой ссылку
# на предшествующую квитанцию
            )
        return dbf


    def createMepPostDbf(self):
        """медицинские услуги"""

        dbfName = os.path.join(self.parent.getTmpDir(), 'MEP_POST.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(   # *  - обязательное поле  ## - заполняется значениями из справочника
            ('AMB_CODE', 'C', 3),     # 1.* ## код ЛПУ (значение из справочника, соответствует
                                                #   полю "amb_Code" файла CUP_POST)
            ('YEAR', 'C', 2),           # 2.* год выписки квитанции (соответствует полю "year"
                                                #  файла CUP_POST)
            ('MONTH', 'C', 2),         # 3.* месяц выписки квитанции (соответствует полю "month"
                                                #  файла CUP_POST)
            ('Blank_Numb', 'C', 6), # 4.* номер квитанции (соответствует полю "blank_numb"
                                                # файла CUP_POST)
            ('code', 'C', 2),           # 5.* порядковый номер медицинской услуги (число с
                                                #  ведущими нулями)
            ('serv_date', 'D'),       # 6.* дата оказания медицинской услуги (дата либо пробелы
                                                #  в случае отсутствия)
            ('man_code', 'C', 4),     # 7.* ## код медицинской услуги (значение из справочника
                                                #  MAN в случае стоматологического счета, значение
                                                #  из справочника OPER в случае амбулаторного
                                                #  счета)
#            ('Place', 'C', 1),          # 8.  место оказания услуги ("Д"-на дому, " "-не на дому,
#                                                #  "А"-активное посещение врача)
#            ('Cause', 'C', 1),          # 9. повод посещения (услуги), (" "
#                                                #  либо "К"-консультация)
#            ('Code_doc', 'C', 40),   # 10. фамилия врача, оказавшего мед.услугу
#            ('MS_Type', 'C', 1),       # 11. Тип услуги:
#                                                #       0 – мед.услуга
#                                                #       1 – операция
#                                                #       2 – стоматологическая манипуляция
# Уникальность поддерживается полями AMB_CODE, YEAR, MONTH, Blank_Numb, Code.
# Если медицинских услуг нет, передается пустой файл.
            )
        return dbf


    def createAmpPostDbf(self):
        """сопутствующие заболевания"""

        dbfName = os.path.join(self.parent.getTmpDir(), 'AMP_POST.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(   # *  - обязательное поле  ## - заполняется значениями из справочника
            ('AMB_CODE', 'C', 3),    # 1.* ## код ЛПУ (значение из справочника, соответствует
                                                #  полю "amb_Code" файла CUP_POST)
            ('YEAR', 'C', 2),          # 2.* год выписки квитанции (соответствует полю "year"
                                                #  файла CUP_POST)
            ('MONTH', 'C', 2),         # 3.* месяц выписки квитанции (соответствует полю "month"
                                                #  файла CUP_POST)
            ('Blank_Numb', 'C', 6),  # 4.* номер квитанции (соответствует полю "blank_numb"
                                                #  файла CUP_POST)
            ('code', 'C', 2),           # 5.* порядковый номер сопутствующего заболевания (число
                                                #  с ведущими нулями)
            ('MKB3', 'C', 3),           #6. ## сопутствующий диагноз (пробелы либо значения из
            ('MKB1', 'C', 1),           #7. ## справочника)
            ('illnes', 'C', 1),        # 8. выявлено впервые (1-да, 0-нет)
            ('dispensary', 'C', 1),  # 9.  диспансерное наблюдение (1-состоит, 2-взят,
                                                #  3-снят, 0-не состоит)
            ('un_cause', 'C', 1),     # 10. причина снятия с дисп. наблюдения (1-
                                                #  выздоровление, 2-переезд, 3-смерть, 0-
                                                #  отсутствует)
            ('hospital', 'C', 1),     # 11.  стационарное лечение (1-круглосуточный, 2-
                                                #  дневной, 3-стационар на дому, 4-дневной в б-це,
                                                #  0-не было)
            ('rehabilit', 'C', 1),   # 12.  реабилитация (1-санаторно-курортное лечение,
                                                #  2-прочее, 0-не было)
# Уникальность поддерживается полями AMB_CODE, YEAR, MONTH, Blank_Numb, Code.
# Если сопутствующих заболеваний нет, передается пустой файл.
            )
        return dbf


    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """
            SELECT
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
              Insurer.infisCode      AS policyInsurer,
              Insurer.INN               AS insurerINN,
              Insurer.shortName          AS insurerName,
              rbPolicyType.code      AS policyType,
              ClientDocument.serial  AS documentSerial,
              ClientDocument.number  AS documentNumber,
              rbDocumentType.code    AS documentType,
              rbDocumentType.regionalCode AS documentRegionalCode,
              RegAddressHouse.KLADRCode AS regKLADRCode,
              RegAddressHouse.KLADRStreetCode AS regKLADRStreetCode,
              RegAddressHouse.number    AS regNumber,
              RegAddressHouse.corpus    AS regCorpus,
              RegAddress.flat           AS regFlat,
              ClientRegAddress.freeInput AS regFreeInput,
              LocAddressHouse.KLADRCode AS locKLADRCode,
              LocAddressHouse.KLADRStreetCode AS locKLADRStreetCode,
              LocAddressHouse.number    AS locNumber,
              LocAddressHouse.corpus    AS locCorpus,
              LocAddress.flat           AS locFlat,
              ClientLocAddress.freeInput AS locFreeInput,
              ClientContact.contact AS phoneNumber,
              ClientWork.post AS clientPost,
              work.fullName AS clientWorkOrgName,
              work.INN AS clientWorkOrgINN,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.infis,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                ) AS service,
              Diagnosis.MKB          AS MKB,
              Diagnostic.hospital,
              Diagnostic.sanatorium,
              rbTraumaType.code AS traumaTypeCode,
              MKB_Tree.Prim               AS prim,
              Event.setDate          AS begDate,
              Event.execDate         AS endDate,
              Account_Item.amount    AS amount,
              Account_Item.`sum`     AS `sum`,
              Account_Item.tariff_id AS tariff_id,
              Person.code AS personCode,
              rbSpeciality.regionalCode AS personRegionalCode,
              EventType.code AS eventTypeCode,
              IF(rbDiagnosticResult.regionalCode IS NULL, EventResult.regionalCode, rbDiagnosticResult.regionalCode) AS resultCode,
                OrgStructure.infisCode,
                OrgStructure.infisInternalCode,
                OrgStructure.infisDepTypeCode,
                OrgStructure.infisTariffCode,
                OrgStructure.type AS lpuType,
                rbHealthGroup.code AS healthGroupCode,
                rbDispanser.code AS dispanserCode,
                rbDiseaseCharacter.code AS characterCode,
                rbMedicalAidType.code AS medicalAidTypeCode,
                rbEventTypePurpose.code AS eventTypePurposeCode
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                      ClientPolicy.id = (SELECT MAX(CP.id)
                                         FROM   ClientPolicy AS CP
                                         WHERE  CP.client_id = Client.id)
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND
                      ClientDocument.id = (SELECT MAX(CD.id)
                                         FROM   ClientDocument AS CD
                                         LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                         LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                                         WHERE  rbDTG.code = '1' AND CD.client_id = Client.id)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id AND
                      ClientRegAddress.id = (SELECT MAX(CRA.id)
                                         FROM   ClientAddress AS CRA
                                         WHERE  CRA.type = 0 AND CRA.client_id = Client.id)
            LEFT JOIN ClientAddress ClientLocAddress ON ClientLocAddress.client_id = Client.id AND
                      ClientLocAddress.id = (SELECT MAX(CLA.id)
                                         FROM   ClientAddress AS CLA
                                         WHERE  CLA.type = 1 AND CLA.client_id = Client.id)
            LEFT JOIN Address   RegAddress ON RegAddress.id = ClientRegAddress.address_id
            LEFT JOIN AddressHouse RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
            LEFT JOIN Address   LocAddress ON LocAddress.id = ClientLocAddress.address_id
            LEFT JOIN AddressHouse LocAddressHouse ON LocAddressHouse.id = LocAddress.house_id
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                      AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1', '2'))
                                      AND Diagnostic.person_id = Event.execPerson_id AND Diagnostic.deleted = 0)
            LEFT JOIN ClientContact  ON ClientContact.client_id = Client.id AND
                      ClientContact.id = (SELECT MAX(CC.id)
                                         FROM   ClientContact AS CC
                                         LEFT JOIN rbContactType ON CC.contactType_id= rbContactType.id
                                         WHERE  rbContactType.code IN (1,2,3) AND CC.client_id = Client.id)
            LEFT JOIN ClientWork ON ClientWork.client_id=Event.client_id AND
                        ClientWork.id = (SELECT max(CW.id)
                                         FROM ClientWork AS CW
                                         WHERE CW.client_id=Client.id)
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
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
            LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
            LEFT JOIN rbTraumaType ON Diagnostic.traumaType_id = rbTraumaType.id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            ORDER BY insurerName
        """ % tableAccountItem['id'].inlist(self.idList)
        query = db.query(stmt)
        return query


    def createVisitQuery(self, eventId):
        db = QtGui.qApp.db
        tableVisit = db.table('Visit')
        stmt = """
            SELECT  Visit.date,
                        rbService.infis AS serviceCode,
                        rbService.name AS serviceName,
                        rbScene.code AS sceneCode,
                        Person.lastName AS lastName,
                        Person.code AS personCode
            FROM Visit
            LEFT JOIN Person ON Visit.person_id = Person.id
            LEFT JOIN rbScene ON Visit.scene_id = rbScene.id
            LEFT JOIN rbService ON Visit.service_id = rbService.id
            WHERE Visit.deleted = 0
            AND %s
        """ % tableVisit['event_id'].eq(eventId)
        query = db.query(stmt)
        return query


    def createActionQuery(self, eventId):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
#(BANG!)
        stmt = """
            SELECT  Action.endDate,
                    rbService.infis AS serviceCode,
                    rbService.name AS serviceName,
                    Person.lastName AS lastName,
                    Person.code AS personCode,
                    ActionType.class AS actionClass
            FROM Action
            LEFT JOIN Person ON Action.person_id = Person.id
            LEFT JOIN ActionType ON Action.actionType_id = ActionType.id
            LEFT JOIN rbService ON ActionType.service_id = rbService.id
            WHERE Action.deleted = 0
            AND %s
        """ % tableAction['event_id'].eq(eventId)
        query = db.query(stmt)
        return query


    def createAdditionalDiagnosticQuery(self, eventId):
        db = QtGui.qApp.db
        tableDiagnostic = db.table('Diagnostic')
        stmt = """
        SELECT  Diagnostic.hospital,
                Diagnostic.sanatorium,
                Diagnosis.MKB   AS MKB,
                rbDispanser.code AS dispanserCode,
                rbDiseaseCharacter.code AS characterCode
        FROM    Diagnostic
        LEFT JOIN Diagnosis   ON Diagnostic.diagnosis_id = Diagnosis.id
        LEFT JOIN MKB_Tree         ON MKB_Tree.DiagID = Diagnosis.MKB
        LEFT JOIN rbDispanser ON rbDispanser.id = Diagnostic.dispanser_id
        LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
        WHERE Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('9', '10','11'))
                    AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0
                    AND %s
        """ % tableDiagnostic['event_id'].eq(eventId)
        query = db.query(stmt)
        return query


    def getActionDate(self, eventId, actionTypeId):
        db = QtGui.qApp.db
        table = db.table('Action')
        cond = []
        cond.append(table['event_id'].eq(eventId))
        cond.append(table['actionType_id'].eq(actionTypeId))
        record = db.getRecordEx(table, 'endDate', where=cond)
        if record:
            return forceDate(record.value('endDate'))
        return None


    def createEducationIdList(self):
        stmt = """
            SELECT  r2.id
            FROM rbSocStatusClass r1
            LEFT JOIN rbSocStatusClass r2 ON r2.group_id = r1.id
            WHERE r1.name = 'образование'
        """
        query = QtGui.qApp.db.query(stmt)
        result = []
        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            if id:
                result.append(id)
        return result


    def process(self, dbf, record, ambCode, accDate, currentLPUINN, \
            isRFAccount, accountType, fieldLpuType, icfCode, payerINN):
        clientId = forceInt(record.value('client_id'))
        birthDate = forceDate(record.value('birthDate'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
#        date = forceDate(record.value('date'))
        age = calcAgeInYears(birthDate, endDate)
        children = '0' if age>=18 else '1'
        mkb = forceString(record.value('MKB'))
        policyInsurer = forceString(record.value('policyInsurer'))
        insurerINN = forceString(record.value('insurerINN'))
        docType   = forceString(record.value('documentType'))
        documentRegionalCode = forceString(record.value('documentRegionalCode'))
        docSerial = forceStringEx(record.value('documentSerial'))
        docNumber = forceString(record.value('documentNumber'))
        regKLADRCode = forceString(record.value('regKLADRCode'))
        locKLADRCode = forceString(record.value('locKLADRCode'))
        locKLADRStreetCode = forceString(record.value('locKLADRStreetCode'))
        locFreeInput = forceString(record.value('locFreeInput'))
        # городской житель - 1, сельский - 0
        inCity = u'Г' if str(regKLADRCode if regKLADRCode else locKLADRCode)[8:11] == '000' else u'С'
        regKLADRStreetCode = forceString(record.value('regKLADRStreetCode'))
        regNumber = forceString(record.value('regNumber'))
        regCorpus = forceString(record.value('regCorpus'))
        regFlat = forceString(record.value('regFlat'))
        # номер стат.талона = event.id
        blankNumber = forceString(record.value('event_id'))[:6].zfill(6)
        blankYear = endDate.toString('yy')
        blankMonth = endDate.toString('MM')
        eventExecPersonCode = forceInt(record.value('personCode'))
        medicalAidTypeCode = forceInt(record.value('medicalAidTypeCode'))
        eventTypePurposeCode = forceInt(record.value('eventTypePurposeCode'))
        # Тип (предопределенные значения: "Стационар","Амбулатория","Скорая помощь","Мобильная станция")
        lpuType = forceInt(record.value('lpuType'))
        eventId = forceRef(record.value('event_id'))
        insurerName = forceString(record.value('insurerName'))

        insurerINN = forceString(record.value('insurerINN'))
        icCode = forceString(QtGui.qApp.db.translate('LOFOMS.S_COMP', 'IIN', insurerINN, 'N'))
        self.log(u'Страховая компания: "%s", ИНН: "%s", код S_COMP.N: "%s"' %\
                  (insurerName, insurerINN, icCode))

        if not icCode:
            self.log(u'Поиск по ИНН: СМО не найдена в справочнике S_COMP')
            icCode = forceString(record.value('policyInsurer'))

        self.log(u'Используем значение кода ИНФИС: "%s"' % icCode)

        if (not icCode) or (not self.isValidLOFOMSrbCode(icCode, 'N', 'S_COMP')):
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                u' код "%s" не найден в таблице S_COMP'
                u' (СМО "%s" (ИНН "%s"))' % (icCode, insurerName, insurerINN), True)
            if not self.ignoreErrors:
                self.abort()


        (dbfApPost, dbfAppPost, dbfCupPost, dbfMepPost, dbfAmpPost) = dbf
        dbfRecord = dbfAppPost.newRecord()
        # 1.* уникальный номер пациента (число с ведущими нулями)
        dbfRecord['code']  = str(clientId).zfill(8)
        # 2. регистрационный документ - паспорт, свидетельство, временное удостоверение
        dbfRecord['DOC_TYPE'] = self.mapDocTypeToLOFOMS[docType]
        # 3. номер паспорта (семизначное число с ведущими нулями, но не более 0999999 для паспорта или
        #     свидетельства о рождении)
        if docType in ('1', '14', '3'):
            dbfRecord['DOC_NUMB'] = str(docNumber[:6]).zfill(7)
        else:
            dbfRecord['DOC_NUMB'] = str(docNumber[:7]).zfill(7)

        # 4. первая часть серии документа
        dbfRecord['SERIA_NUM'] = docSerial[:2] if docSerial else '00'

        #Если лтип документа "ВРЕМ УДОСТ" (code = 13)
        if docType == '13':
            #Если КЛАДР код равен КЛАДР коду Санкт-Петербурга
            if locKLADRCode == 78:
                seriaLet = u'СП'
            #Если КЛАДР код равен КЛАДР коду Ленн. области
            elif locKLADRCode == 47:
                seriaLet = u'ЛО'
            else:
                seriaLet = u' '
        else:
            seriaLet = docSerial[3:5]

        # 5. вторая часть в серии документа
        dbfRecord['SERIA_LET'] = seriaLet
        # 6.* фамилия (обязательно русскими буквами)
        dbfRecord['SURNAME'] = nameCase(forceString(record.value('lastName')))
        # 7.* имя (обязательно русскими буквами)
        dbfRecord['NAME'] = nameCase(forceString(record.value('firstName')))
        # 8. отчество (обязательно русскими буквами)
        dbfRecord['SEC_NAME'] = nameCase(forceString(record.value('patrName')))
        # 9.* дата рождения - в диапазоне от 01/01/1880 до текущей даты
        dbfRecord['BIRTHDAY'] = pyDate(birthDate)
        self.log(u'Пациент: "%s" "%s" "%s"'% (\
            dbfRecord['SURNAME'], dbfRecord['NAME'], dbfRecord['SEC_NAME']))
        self.log(u'Документ: серия "%s" "%s", номер "%s"' %(\
            dbfRecord['SERIA_NUM'] , dbfRecord['SERIA_LET'], dbfRecord['DOC_NUMB']))
        # 10.* пол ("М" или "Ж")-заглавные русские буквы
        dbfRecord['SEX'] = formatSex(record.value('sex')).upper()
        # 11.* где проживает (Лен.обл., С-П/б., Россия, Прочее)-
        #       ("Л" "С" "Р" "П")-заглавные русские буквы
        dbfRecord['LIVE_IN'] = self.mapKLADRCodeToLiveIn.get(regKLADRCode[:2], u'Р')
        # 12.  ## номер района прописки ("00", либо значение из справочника S_FIL)
        dbfRecord['DIS_CODE'] = '00'
        # 13.   ##  населенный пункт ("000", либо значение из  справочника NPUNKT)
        dbfRecord['CP_CODE'] = '000'
        # 14. улица по прописке
        dbfRecord['STREET'] = getStreetName(regKLADRStreetCode) \
                                        if regKLADRStreetCode else ''
        # 15. дом по прописке
        dbfRecord['HOUSE'] = regNumber
        # 16. корпус по прописке
        dbfRecord['BUILDING'] = regCorpus
        # 17. квартира по прописке (четырехзначный номер с ведущими нулями)
        dbfRecord['FLAT']= regFlat.zfill(4)
        # 18.* адрес фактического проживания
        if locKLADRCode and locKLADRStreetCode:
            dbfRecord['ADDRESS'] = myFormatAddress(
                    locKLADRCode,
                    locKLADRStreetCode,
                    forceString(record.value('locNumber')),
                    forceString(record.value('locCorpus')),
                    forceString(record.value('locFlat')))
        elif  locFreeInput:
            dbfRecord['ADDRESS'] = locFreeInput
        elif regKLADRCode and regKLADRStreetCode:
            dbfRecord['ADDRESS'] = myFormatAddress(regKLADRCode,
                                            regKLADRStreetCode, regNumber, regCorpus, regFlat)
        else:
            dbfRecord['ADDRESS'] = forceString(record.value('regFreeInput'))
        # 19.* место регистрации страхователя (Лен.обл., С-П/б., Прочее)
        #       -("Л", "С", "П")-заглавные русские буквы
        dbfRecord['WORK_IN'] = self.mapINNToWorkIn.get(forceString(\
                record.value('clientWorkOrgINN'))[:2], u'П')
        # 20. страхователь (место работы для работающих, администрация района
        #       или другой источник для   неработающих)
        dbfRecord['INSURER'] = forceString(record.value('clientWorkOrgName'))
        # 21.* житель считается ГОРОДСКИМ или СЕЛЬСКИМ
        #       ("Г" или  "С")-заглавные русские буквы
        dbfRecord['TOWN_C'] = inCity
        # 22.  документы родителей для иногородних детей
        dbfRecord['PAR_DOC'] = ''
        # 23.  ФИО родителей для иногородних детей
        dbfRecord['PAR_NAME'] = ''
#        # 24. почтовый индекс
#        if regKLADRCode and regKLADRStreetCode:
#            dbfRecord['POST_IND'] = getPostIndex(regKLADRCode, regKLADRStreetCode,
#                                                                    regNumber, regCorpus)
#        else:
#            dbfRecord['POST_IND'] = getPostIndex(locKLADRCode, locKLADRStreetCode,
#                                                                forceString(record.value('locNumber')),
#                                                                forceString(record.value('locCorpus')))
#        # 25. телефон
#        dbfRecord['PHONE'] = forceString(record.value('phoneNumber'))
#        # 26. должность по месту работы
#        dbfRecord['PROF'] = forceString(record.value('clientPost'))
        dbfRecord.store()

        visitQuery = self.createVisitQuery(eventId)
        serviceNumber = 0
        self.log(u'Количество визитов: %d' % visitQuery.size())
        # Если в событии нет визитов, то считаем, что место обслуживания ЛПУ.
        # Если визиты есть, то место определяется по последнему визиту.
        lastVisitPlace = ' ' # ' ' не на дому
        # Счетчики визитов
        # А - по месту визита - ЛПУ
        # Б - по месту визита - на дому,актив на дому
        # В - по назначению типа события - профилактика
        visitCountA = visitCountB = visitCountC =0
        visitScene = 1 # ЛПУ
        while visitQuery.next():
            r = visitQuery.record()
            QtGui.qApp.processEvents()
            if self.aborted:
                    break

            visitDate = forceDate(r.value('date'))
            dbfRecord = dbfMepPost.newRecord()
            # 1.* ## код ЛПУ (значение из справочника, соответствует
            #       полю "amb_Code" файла CUP_POST)
            dbfRecord['AMB_CODE'] = ambCode
            # 2.* год выписки квитанции (соответствует полю "year"  файла CUP_POST)
            dbfRecord['YEAR'] = blankYear
            # 3.* месяц выписки квитанции (соответствует полю "month"  файла CUP_POST)
            dbfRecord['MONTH'] = blankMonth
            # 4.* номер квитанции (соответствует полю "blank_numb" файла CUP_POST)
            dbfRecord['Blank_Numb'] = blankNumber
            # 5.* порядковый номер медицинской услуги (число с ведущими нулями)
            dbfRecord['code'] = forceString(serviceNumber)[:2].zfill(2)
            serviceNumber += 1
            # 6.* дата оказания медицинской услуги (дата либо пробелы в случае отсутствия)
            dbfRecord['serv_date'] = pyDate(visitDate)
            # 7.* ## код медицинской услуги (значение из справочника
            #   MAN в случае стоматологического счета, значение из
            #   справочника OPER в случае амбулаторного счета)
            serviceCode = forceString(r.value('serviceCode'))
            if (not serviceCode) or (not ( \
                    self.isValidLOFOMSrbCode(serviceCode, 'N', 'MAN') or \
                    self.isValidLOFOMSrbCode(serviceCode, 'CODE', 'OPER'))):
                self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                    u' код услуги "%s" не найден в таблицах MAN и OPER'
                    u' (Услуга "%s")' % (serviceCode, \
                    forceString(r.value('serviceName'))), True)
                if not self.ignoreErrors:
                    self.abort()

            dbfRecord['man_code'] = serviceCode
            visitScene = forceString(r.value('sceneCode'))
            if visitScene == 1: # ЛПУ
                if eventTypePurposeCode == 3: # профилактика
                    visitCountC += 1
                else:
                    visitCountA += 1
            elif visitScene in (2, 3): # на дому,актив на дому
                visitCountB += 1

#            # 8.  место оказания услуги ("Д"-на дому, " "-не на дому,
#            #       "А"-активное посещение врача)
#            dbfRecord['Place'] = lastVisitPlace = self.mapSceneCodeToVisitPlace.get(\
#                forceString(r.value('sceneCode')), ' ')
#            # 9. повод посещения (услуги), (" " либо "К"-консультация)
#            dbfRecord['Cause'] = ' ' if forceInt(r.value('personCode')) == eventExecPersonCode else u'К'
#            # 10. фамилия врача, оказавшего мед.услугу
#            dbfRecord['Code_doc'] = forceString(r.value('lastName'))
#            # 11. Тип услуги:  0 – мед.услуга, 1 – операция, 2 – стоматологическая манипуляция
#            dbfRecord['MS_Type'] = '0'
            dbfRecord.store()

        actionQuery = self.createActionQuery(eventId)
        self.log(u'Количество действий: %d' % actionQuery.size())

        while actionQuery.next():
            r = actionQuery.record()
            QtGui.qApp.processEvents()
            if self.aborted:
                    break

            visitDate = forceDate(r.value('endDate'))
            dbfRecord = dbfMepPost.newRecord()
            # 1.* ## код ЛПУ (значение из справочника, соответствует
            #       полю "amb_Code" файла CUP_POST)
            dbfRecord['AMB_CODE'] = ambCode
            # 2.* год выписки квитанции (соответствует полю "year"  файла CUP_POST)
            dbfRecord['YEAR'] = blankYear
            # 3.* месяц выписки квитанции (соответствует полю "month"  файла CUP_POST)
            dbfRecord['MONTH'] = blankMonth
            # 4.* номер квитанции (соответствует полю "blank_numb" файла CUP_POST)
            dbfRecord['Blank_Numb'] = blankNumber
            # 5.* порядковый номер медицинской услуги (число с ведущими нулями)
            dbfRecord['code'] = forceString(serviceNumber)[:2].zfill(2)
            serviceNumber += 1
            # 6.* дата оказания медицинской услуги (дата либо пробелы в случае отсутствия)
            dbfRecord['serv_date'] = pyDate(visitDate)
            # 7.* ## код медицинской услуги (значение из справочника
            #   MAN в случае стоматологического счета, значение из
            #   справочника OPER в случае амбулаторного счета)
            serviceCode = forceString(r.value('serviceCode'))
            visitCountA += 1 # считаем, что действие происходит в ЛПУ.

            if (not serviceCode) or (not ( \
                    self.isValidLOFOMSrbCode(serviceCode, 'N', 'MAN') or \
                    self.isValidLOFOMSrbCode(serviceCode, 'CODE', 'OPER' ))):
                self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                    u' код услуги "%s" не найден в таблицах MAN и OPER'
                    u' (Услуга "%s")' % (serviceCode, \
                    forceString(r.value('serviceName'))), True)
                if not self.ignoreErrors:
                    self.abort()

            dbfRecord['man_code'] = serviceCode
#            # 8.  место оказания услуги ("Д"-на дому, " "-не на дому,
#            #       "А"-активное посещение врача)
#            dbfRecord['Place'] = ' '
#            # 9. повод посещения (услуги), (" " либо "К"-консультация)
#            serviceClass = forceInt(r.value('class'))
#            dbfRecord['Cause'] = u'К' if (forceInt(r.value('personCode')) != \
#                                            eventExecPersonCode) and (serviceClass == 0) else ' '
#            # 10. фамилия врача, оказавшего мед.услугу
#            dbfRecord['Code_doc'] = forceString(r.value('lastName'))
#            # 11. Тип услуги:  0 – мед.услуга, 1 – операция, 2 – стоматологическая манипуляция
#            dbfRecord['MS_Type'] = '0'
            dbfRecord.store()

        additionalDiagnosticQuery = self.createAdditionalDiagnosticQuery(eventId)
        additionalDiagnosticNumber = 0
        self.log(u'Количество доп.диагностик: %d' % additionalDiagnosticQuery.size())

        while additionalDiagnosticQuery.next():
            r = additionalDiagnosticQuery.record()

            dbfRecord = dbfAmpPost.newRecord()
            # 1.* ## код ЛПУ (значение из справочника, соответствует
            #       полю "amb_Code" файла CUP_POST)
            dbfRecord['AMB_CODE'] = ambCode
            # 2.* год выписки квитанции (соответствует полю "year"
            #       файла CUP_POST)
            dbfRecord['YEAR'] = blankYear
            # 3.* месяц выписки квитанции (соответствует полю "month"
            #       файла CUP_POST)
            dbfRecord['MONTH'] = blankMonth
            # 4.* номер квитанции (соответствует полю "blank_numb"
            #       файла CUP_POST)
            dbfRecord['Blank_Numb']= blankNumber
            # 5.* порядковый номер сопутствующего заболевания (число
            #        с ведущими нулями)
            dbfRecord['code'] = forceString(additionalDiagnosticNumber)[:2].zfill(2)
            additionalDiagnosticNumber += 1
            # 6. ## сопутствующий диагноз (пробелы либо значения из
            mkb = forceString(record.value('MKB'))
            dbfRecord['MKB3'] = mkb[:3]
            # 7. ## справочника)
            dbfRecord['MKB1'] = mkb[4:]
            # 8. выявлено впервые (1-да, 0-нет)
            dbfRecord['illnes'] = '1' if forceInt(r.value('characterCode')) == 2 else '0'
            # 9.  диспансерное наблюдение (1-состоит, 2-взят, 3-снят, 0-не состоит)
            dispanserCode = forceString(r.value('dispanserCode'))
            dbfRecord['dispensary'] = self.mapDispanserCode.get(dispanserCode, '0')
            # 10. причина снятия с дисп. наблюдения (1- выздоровление, 2-переезд,
            #       3-смерть, 0-отсутствует)
            dbfRecord['un_cause'] = self.mapDispanserCodeToCancelReason.get(dispanserCode, '0')
            # 11.  стационарное лечение (1-круглосуточный, 2- дневной, 3-стационар
            #       на дому, 4-дневной в б-це, 0-не было)
            dbfRecord['hospital'] = '0'
            # 12.  реабилитация (1-санаторно-курортное лечение, 2-прочее, 0-не было)
            dbfRecord['rehabilit'] = self.mapSanatoriumToRehabilitationCode.get(forceString(r.value('sanatorium')), '2')
            dbfRecord.store()

        dbfRecord = dbfCupPost.newRecord()
        #1.*   ##  код ЛПУ (значение из справочника, соответствует
        #       полю "amb_Code" файла AP_POST)
        dbfRecord['AMB_CODE'] = ambCode
        # 2.* год выписки стат.талона (число в диапазоне 0..99 с ведущими нулями)
        dbfRecord['YEAR'] = blankYear
        # 3.* месяц выписки стат.талона (число в диапазоне 1..12 с ведущими нулями)
        dbfRecord['MONTH'] = blankMonth
        # 4.* номер стат.талона (число с ведущими нулями)
        dbfRecord['Blank_Numb'] = blankNumber
        # 5.* код пациента (соответствует полю "code" файла App_post.dbf)
        dbfRecord['APP_CODE'] = str(clientId).zfill(8)
        # 6.* ##  СМО (значение из справочника, соответствует полю
        #           "ic_code" файла AP_POST)
        dbfRecord['IC_CODE'] = icCode
        # 7.* ## подразделение фонда, в которое выставлен счет
        # (значение из справочника S_FIL_L либо "00",
        # соответствует полю "icf_code" файла AP_POST)
        dbfRecord['ICF_CODE'] = icfCode
        # 8.* дата формирования почты (соответствует полю
        #  "mak_date" файла AP_POST)
        dbfRecord['Mak_Date'] = pyDate(accDate)
        isAlienSMO = forceString(record.value('insurerINN'))[:2] != currentLPUINN[:2]
         # 9.  иногородняя СМО
        dbfRecord['A_INSURAN'] = forceString(record.value('insurerName')) if isAlienSMO else ''
        # 10. серия иногороднего полиса
        dbfRecord['A_POLIC_S'] = forceString(record.value('policySerial')) if isAlienSMO else ''
        # 11.  номер иногороднего полиса
        dbfRecord['A_POLIC_N'] = forceString(record.value('policyNumber')).zfill(8) if isAlienSMO else ''
        # 12.  номер полиса (число с ведущими нулями)
        dbfRecord['POLIC_N'] = forceString(record.value('policyNumber')).zfill(8)
        # 13.  серия полиса (заглавные русские буквы либо пробелы)
        dbfRecord['POLIC_S'] = forceString(record.value('policySerial'))
        # 14.* ## клиническая служба (значение из справочника CL_SERVS)
        clService = forceString(record.value('personRegionalCode'))
        if (not clService) or (not self.isValidLOFOMSrbCode(serviceCode, 'CODE', 'CL_SERVICE')):
                self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                    u' код "%s" не найден в таблице CL_SERVICE' % \
                    serviceCode, True)
                if not self.ignoreErrors:
                    self.abort()
        dbfRecord['cs_code'] = clService
        # 15. признак детского врача (1-есть, 0-нет)
        dbfRecord['children'] = children
        # 16.* количество посещений
        amount = forceInt(record.value('amount'))
        self.log(u'Количество посещений (из счета): "%d"' % amount)
        dbfRecord['visit'] = '%d' % (amount if amount < 99 else 99)
        # 17.*дата обращения
        dbfRecord['StartDate'] = pyDate(begDate)
        # 18.*дата выписки
        dbfRecord['FinishDate'] = pyDate(endDate)

        # проверка соц. статусов пациента
        (socClassIdList, socTypeList) = self.getClientSocStatus(clientId, endDate)
        clientEducation = '0'

        for classId in socClassIdList:
            if classId in self.educationIdList:
                classCode = forceInt(QtGui.qApp.db.translate('rbSocStatusClass', \
                                                'id', classId, 'code'))
                self.log(u'Образование пациента: код "%d".' % classCode)
                clientEducation = self.mapEducation.get(classCode, '0')
                if clientEducation != '0':
                    break

        clientCategory= '013' # Прочее

        if age == 0:
            clienCategory = '012' # Ребенок до года
        elif children == '1':
            clienCategory = '011' # Подросток
        else:
            for socType in socTypeList:
                clientCategory = self.mapClientCategory.get(socType, '013')
                self.log(u'Соц. тип пациента: код "%s".' %  socType)
                if clientCategory != '013':
                    break

        # 19. образование (1-высшее, 2-среднее, 3-нач., 4-не имеет, 0-неизвестно)
        dbfRecord['Education'] = clientEducation
        # 20.* ## категория пациента (значение из справочника CAT_PACS)
        dbfRecord['Cat_code'] = clientCategory.zfill(3)

        igFound = '0'
        igGroup = '0'
        igDate = None
        ntOpen = None
        ntClose = None

        tempInvalidList = self.getClientTempInvalidList(clientId, endDate)
        for (tiCode, tiType, tiBegDate, tiEndDate) in tempInvalidList:
            if tiType == 0: # вут
                ntOpen = pyDate(tiBegDate)
                ntClose = pyDate(tiEndDate)
                self.log(u'ВУТ: с "%s" по "%s".' % \
                        (tiBegDate.toString('dd.MM.yyyy'),\
                        tiEndDate.toString('dd.MM.yyyy')))
            elif tiType == 1: # инвалидность
                igFound = '1'
                igGroup = forceString(tiCode)
                igDate = pyDate(tiBegDate)
                self.log(u'Инвалидность: группа "%d"' % tiCode)

        # 21. инвалидность (1-подтверждена, 2-установлена впервые, 3-снята, 0-отсутствует)
        dbfRecord['IG_found'] = igFound
        # 22.  группа инвалидности (1, 2, 3, 0-отсутствует)
        dbfRecord['IG_group'] = igGroup
        # 23. дата инвалидности (дата либо пробелы в случае отсутствия)
        if igDate:
            dbfRecord['IG_date'] = igDate
        # 24. группа здоровья (1, 2, 3, 0-отсутствует)
        dbfRecord['He_group'] = forceString(record.value('healthGroupCode'))
        # 25. дата выдачи б/л (дата либо пробелы в случае отсутствия)
        if ntOpen:
            dbfRecord['NT_open'] = ntOpen
        # 26. дата закрытия б/л (дата либо пробелы в случае отсутствия)
        if ntClose:
            dbfRecord['NT_close'] = ntClose
        #27. ## основной диагноз (пробелы либо значения из справочника)
        dbfRecord['MKB3'] = mkb[:3]
        dbfRecord['MKB1'] = mkb[4:]
        #29. характер заболевания (" "-отсутствие информации, 1–выявлено впервые,
        # 2-ранее зарегистрированное, 3-зарегистрировано в данном году)
        dbfRecord['illnes'] = ' '
        dispanserCode = forceString(record.value('dispanserCode'))
        # 30.  диспансерное наблюдение (1-состоит, 2-взят, 3-снят, 0-не состоит)
        dbfRecord['dispensary'] = self.mapDispanserCode.get(dispanserCode, '0')
        # 31. причина снятия с дисп. наблюдения (1-выздоровление, 2-переезд,
        #   3-смерть, 0- отсутствует)
        dbfRecord['un_cause'] = self.mapDispanserCodeToCancelReason.get(dispanserCode, '0')

        # Определяем по типу мед.помощи события: стационарная помощь - соответствует 1,
        # Дневной стационар - соответствует 2 если тип подразделения ответственного
        # "Амбулатория" и 4 если "Стационар" при месте визитов "ЛПУ",
        # 3 - при месте визитов "на дому"
        cureType = '0' # стационарное лечение

        if visitScene in (2, 3): # дома
            cureType = '3'
        elif visitScene == 1: # ЛПУ
            if medicalAidTypeCode == 1:
                cureType = '1'
            elif medicalAidTypeCode == 7:
                cureType = '4' if lpuType == 0 else '2'


        # 32. стационарное лечение (1-круглосуточный, 2- дневной, 3-стационар на дому,
        #      4-дневной в б-це, 0-не было)
        dbfRecord['hospital'] = cureType
        # 33.  реабилитация (1-санаторно-курортное лечение,
        #      2-прочее, 0-не было)
        if eventTypePurposeCode ==6:
            dbfRecord['rehabilit'] = '1' if medicalAidTypeCode == 8 else '2'
        else:
            dbfRecord['rehabilit'] = '0'
        # 34.* ## повод обращения (значение из справочника E_COUSES)
        eventTypeCode = forceString(record.value('eventTypeCode'))
        dbfRecord['ec_code'] = self.mapEventTypeCode.get(eventTypeCode, '9').zfill(3)
        # 35.  ## вид травмы ("000", либо значение из  справочника TR_TYPES)
        dbfRecord['tt_code'] = self.mapTraumaType.get(forceString(\
                            record.value('traumaTypeCode')), '000').zfill(3)
        # 36.  дата флюорографии (дата либо пробелы в случае отсутствия)
        fDate = self.getActionDate(eventId, self.parent.page1.cmbActionTypeFluorography.value())
        if fDate:
            dbfRecord['FLURAGRAFY'] = pyDate(fDate)
        # 37. дата цитологического обследования (дата либо пробелы в случае отсутствия)
        cDate = self.getActionDate(eventId, self.parent.page1.cmbActionTypeCytological.value())
        if cDate:
            dbfRecord['CITOLOGY'] = pyDate(cDate)
        # 38.* сумма лечения (сумма в рублях, 2 знака после точки, ведущие - пробелы)
        dbfRecord['Summa']= '%.2f' % forceDouble(record.value('sum'))
        # 39.  ## причина возврата ("000" - при приеме почты из ЛПУ)
        dbfRecord['rej_code'] ='000'
        # 40.  ## лечебное учреждение, к которому прикреплен пациент (значение из
        #     справочника S_POL), заполняется значением «000» для квитанции,
        #     вошедшей в счет по РФ

        clientAttachOrgCode = clientAttachOrgId = None
        clientAttachRecord = getAttachRecord(clientId, False)
        clientAttachedToSPbLPU = False
        clientAttachedToLOLPU = False

        if clientAttachRecord:
            clientAttachOrgId = clientAttachRecord.get('LPU_id', None)
        else:
            self.log(u'Внимание: не задано ЛПУ постоянного прикрепления пациента.')

        if clientAttachOrgId:
            clientAttachOrgINN = forceString(QtGui.qApp.db.translate('Organisation', \
                'id', clientAttachOrgId, 'INN'))
            clientAttachedToSPbLPU = (clientAttachOrgINN[:2] == '78')
            clientAttachedToLOLPU = (clientAttachOrgINN[:2] == '47')
            self.log(u'ЛПУ прикрепления пациента: ИНН "%s"' % clientAttachOrgINN)
            clientAttachOrgCode = forceString(QtGui.qApp.db.translate('LOFOMS.S_POL', \
                'IIN', clientAttachOrgINN, 'N'))
            if not clientAttachOrgCode:
                self.log(u'Поиск по ИНН: ЛПУ не найдено в справочнике S_POL')
                clientAttachOrgCode = forceString(QtGui.qApp.db.translate(\
                    'Organisation', 'id', clientAttachOrgId, 'infisCode'))
                self.log(u'Используем значение кода ИНФИС: "%s"' % clientAttachOrgCode)

        if not isRFAccount:
            if (not clientAttachOrgCode) or (not self.isValidLOFOMSrbCode(\
                    clientAttachOrgCode, 'N', 'S_POL')):
                self.log(u'<b><font color=brown>Предупреждение<\font><\b>:'
                    u' код "%s" не найден в таблице S_POL' % clientAttachOrgCode)
        else:
            self.log(u'Счет по РФ: код прикрепления установлен "000"')
            clientAttachOrgCode = '000'

        if clientAttachOrgCode: # заполняем, если есть (необязательное поле)
            dbfRecord['P_A_Code'] = clientAttachOrgCode
        # 41.  ## муниципальное образование пациента ("00" в случае прикрепления пациента к
        #       ЛПУ СПб, либо значение из справочника S_MUN в случае  прикрепления пациента
        #       к ЛПУ Лен.области) для квитанций, вошедших в счета на застрахованных и
        #       условно застрахованных; код территориального фонда для квитанций,
        #       вошедших в счет по РФ (значение из справочника S_TERR)
        if clientAttachedToSPbLPU:
            dbfRecord['Mun_Code'] = '00'
        elif clientAttachedToLOLPU:
            pass # значение из S_MUN
        elif isRFAccount: # значение из S_TERR
            terrCode = forceString(QtGui.qApp.db.translate('LOFOFMS.S_TERR', 'IIN', payerINN, 'N'))
            if terrCode:
                dbfRecord['Mun_Code'] = terrCode
            else:
                self.log(u'<b><font color=brown>Предупреждение<\font><\b>:'
                    u' Тер.фонд ИНН "%s" не найден в таблице S_TERR' % payerINN)

        # 42. признак непрофильной службы ( 1 - непрофильная, 0 - профильная)
        dbfRecord['Not_Prof'] = '0' # ???
        # 43.* подразделение стационара ( 003 - дневной стационар амбулатории, 004 - в противном случае)
        dbfRecord['Sub_Div'] = '003' if medicalAidTypeCode ==  7 else '004'
        # 44.* категория счета (значение из справочника, соответствует полю "RespFlag" файла AP_POST)
        dbfRecord['RespFlag'] = accountType
        # 45.  количество посещений по группе А (число с ведущими нулями)
        dbfRecord['Visit_01'] = forceString(visitCountA).zfill(2)
        # 46. количество посещений по группе Б (число с ведущими нулями)
        dbfRecord['Visit_02'] = forceString(visitCountB).zfill(2)
        # 47. количество посещений по группе В (число с ведущими нулями)
        dbfRecord['Visit_03'] = forceString(visitCountC).zfill(2)
        # 48 - 56  резервное поле (заполняется пробелами)
        dbfRecord['Visit_04'] = ' '
        dbfRecord['Visit_05'] = ' '
        dbfRecord['Visit_06'] = ' '
        dbfRecord['Visit_07'] = ' '
        dbfRecord['Visit_08'] = ' '
        dbfRecord['Visit_09'] = ' '
        dbfRecord['Visit_10'] = ' '
        dbfRecord['Visit_11'] = ' '
        dbfRecord['Visit_12'] = ' '
        # 57.* тип счета (значение из справочника, соответствует
        #       полю "lpu_type" файла AP_POST)
        dbfRecord['lpu_type'] = fieldLpuType
        # 58. год выписки стат.талона «родителя» для формирования
        #      информации о «законченном случае лечения»
        dbfRecord['Y_PARENT'] = ' '
        # 59. месяц выписки стат.талона «родителя»
        dbfRecord['M_PARENT'] = ' '
         # 60. номер стат.талона «родителя»
        dbfRecord['N_PARENT'] = '     '
#        # 61.  причина отсутствия полиса (значение из справочника
#        #       NOT_POLIS, либо "000")
#        dbfRecord['NE_CODE'] = '000'
#        # 62. социальная группа (значение из справочника
#        #       S_GRUP либо "000")
#        dbfRecord['Sg_code'] = '000'
#        # 63. больничный лист либо справка (1-больничный лист,
#        #       2-справка, " " в случае отсутствия информации)
#        dbfRecord['NT_spr'] = ' '
#        # 64. дата заполнения стат.талона
#        dbfRecord['Date_wri'] = pyDate(endDate)
#        # 65. (1-6) как в МВК," " в случае отсутствия информации
#        dbfRecord['NTsprREA'] = ' '
        dbfRecord.store()
        if insurerINN != self.currentSMO:
            self.currentSMO = insurerINN
            self.createApPostRecord(dbf, icCode, ambCode, icfCode,\
                fieldLpuType, accountType)

    def getClientSocStatus(self, clientId, date):
        classes = []
        types = []
        db = QtGui.qApp.db
        table = db.table('ClientSocStatus')
        stmt = """
            SELECT  rbSocStatusClass.id AS classId,
                        rbSocStatusType.code AS typeCode
            FROM ClientSocStatus
            LEFT JOIN rbSocStatusClass ON socStatusClass_id = rbSocStatusClass.id
            LEFT JOIN rbSocStatusType ON socStatusType_id = rbSocStatusType.id
            WHERE %s
        """ % db.joinAnd([ table['client_id'].eq(clientId),
            table['deleted'].eq(0),
            db.joinOr([table['begDate'].isNull(), table['begDate'].le(date)]),
            db.joinOr([table['endDate'].isNull(), table['endDate'].ge(date)])])

        query = db.query(stmt)
        while query.next():
            record=query.record()
            socClassId = forceRef(record.value('classId'))
            if socClassId:
                classes.append(socClassId)
            socType = forceString(record.value('typeCode'))
            if socType:
                types.append(socType)

        return (classes, types)


    def getClientTempInvalidList(self, clientId, date):
        list = []
        db = QtGui.qApp.db
        table = db.table('TempInvalid')
        stmt = """
            SELECT  td.code,
                        td.type,
                        begDate,
                        endDate
            FROM TempInvalid
            LEFT JOIN rbTempInvalidDocument td ON doctype_id = td.id
            WHERE %s
        """ % db.joinAnd([ table['client_id'].eq(clientId),
            table['deleted'].eq(0),
            db.joinOr([table['begDate'].isNull(), table['begDate'].le(date)]),
            db.joinOr([table['endDate'].isNull(), table['endDate'].ge(date)])])

        query = db.query(stmt)
        while query.next():
            record=query.record()
            list.append((forceInt(record.value('code')),
                forceInt(record.value('type')),
                forceDate(record.value('begDate')),
                forceDate(record.value('endDate'))))

        return list


    def isValidLOFOMSrbCode(self, code, fieldName, tableName):
        """ Возвращает True, если указанный код найден в справочнике из базы ЛОФОМС"""
        key = (code, fieldName, tableName)
        result = self.knownLOFOMSCodes.get(key, None)

        if not result:
            db = QtGui.qApp.db
            table = db.table('LOFOMS.%s' % tableName)
            record = db.getRecordEx(table, 'id', [table[fieldName].eq(code)])
            result = (record != None)
            self.knownLOFOMSCodes[key] = result

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


class CExportLOFOMSPage3(QtGui.QWizardPage, Ui_ExportLOFOMSPage3):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'LOFOMSExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        for src in ('AP_POST.DBF', 'APP_POST.DBF',
                        'CUP_POST.DBF', 'MEP_POST.DBF', 'AMP_POST.DBF'):
            srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                    os.path.basename(src))
            dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                    os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

            if not success:
                break

        if success:
            QtGui.qApp.preferences.appPrefs['LOFOMSExportDir'] = toVariant(self.edtDir.text())
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
                u'Выберите директорию для сохранения файла выгрузки в ЛОФОМС',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
