# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil

from library.dbfpy.dbf import *

from library.database  import *
from library.Utils     import forceBool, forceDate, forceDouble, forceInt, forceStringEx, getVal, formatSNILS, pyDate
from Exchange.Utils import CExportHelperMixin
from Events.Action import CAction

from Ui_ExportR51HospitalPage1 import Ui_ExportPage1
from Ui_ExportR51HospitalPage2 import Ui_ExportPage2


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


def exportR51Hospital(widget, accountId, accountItemIdList):
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
        self.page1.cmbExportType.setCurrentIndex(forceInt(getVal(
            QtGui.qApp.preferences.appPrefs, 'ExportR51HospitalExportType', 0)))
        self.setWindowTitle(u'Мастер экспорта в ОМС Мурманской области (стационар)')
        self.dbfFileName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId = getAccountInfo(accountId)
        strNumber = number if forceStringEx(number) else u'б/н'
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
            self.tmpDir = QtGui.qApp.getTmpDir('R51Hospital')
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
        QtGui.qApp.preferences.appPrefs['ExportR51HospitalExportFormat'] = toVariant(
                self.page1.cmbExportType.currentIndex())


# *****************************************************************************************

class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1, CExportHelperMixin):
    exportTypeSMO = 0 # индексы из cmbExportType
    exportTypeTFOMS = 1

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        CExportHelperMixin.__init__(self)
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
        self.ignoreErrors = False
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51HospitalVerboseLog', False)))
        self.chkIgnoreErrors.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR51HospitalIgnoreErrors', False)))

        self.actionTypeMovement = None
        self.actionTypeArrival = None
        self.actionTypeIllegalActions = None
        self.actionTypeMultipleBirth = None

        self.medicalAidProfileCache = {}

        self.exportedEventSet = set()

        self.prevEventId = None


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.cmbExportType.setEnabled(not flag)


    def log(self, str, forceLog = False):
        if self.chkVerboseLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self, exportFormat):
        self.done = False
        self.aborted = False
        self.prevEventId = None
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf(exportFormat)
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
            self.cmbExportType.setEnabled(False)
            self.emit(QtCore.SIGNAL('completeChanged()'))
            QtGui.qApp.preferences.appPrefs['ExportR51HospitalIgnoreErrors'] =\
                toVariant(self.chkIgnoreErrors.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR51HospitalVerboseLog'] =\
                toVariant(self.chkVerboseLog.isChecked())

# *****************************************************************************************

    def getActionPropertyTypeId(self, name, actionTypeId):
        db = QtGui.qApp.db
        table = db.table('ActionPropertyType')
        result = 0

        record = db.getRecordEx(table, 'id', [
            table['name'].eq(name),
            table['actionType_id'].eq(actionTypeId)])

        if record:
            result = forceInt(record.value(0))

        return result

# *****************************************************************************************

    def exportInt(self):
        db = QtGui.qApp.db
        tableOrganisation = db.table('Organisation')
        tableActionType = db.table('ActionType')

        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        exportType = self.cmbExportType.currentIndex()
        self.log(u'Выгружаем счет в формате "%d".' % exportType)

        lpuId = QtGui.qApp.currentOrgId()
        lpuOKPO = forceString(db.translate(
            tableOrganisation, 'id', lpuId , 'OKPO'))
        lpuCode = forceString(db.translate(
            tableOrganisation, 'id', lpuId , 'infisCode'))
        lpuOGRN = forceString(db.translate(
            tableOrganisation, 'id', lpuId , 'OGRN'))
        self.log(u'ЛПУ: ОКПО "%s", ОГРН "%s",код инфис: "%s".' % (lpuOKPO, lpuOGRN,  lpuCode))

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан код инфис', True)
            if not self.ignoreErrors:
                return

        self.actionTypeArrival = forceRef(db.translate(tableActionType, 'flatCode', 'received', 'id'))

        if not self.actionTypeArrival:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Не найден тип действия "Поступление" (плоский код: "received")', True)
            if not self.ignoreErrors:
                return

        self.actionTypeMovement= forceRef(db.translate(tableActionType, 'name', u'Движение', 'id'))

        if not self.actionTypeMovement:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Не найден тип действия "Движение"', True)
            if not self.ignoreErrors:
                return

        self.actionTypeIllegalActions =  forceRef(db.translate(tableActionType,  'flatCode', 'IllegalActions', 'id'))

        if not self.actionTypeIllegalActions:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Не найден тип действия "Противоправные действия" (плоский код: "IllegalActions")', True)
            if not self.ignoreErrors:
                return

        self.actionTypeMultipleBirth = forceRef(db.translate(tableActionType, 'flatCode', 'MultipleBirth', 'id'))

        if not self.actionTypeMultipleBirth:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Не найден тип действия "Многоплодные роды" (плоский код: "MultipleBirth")', True)
            if not self.ignoreErrors:
                return

        dbf, query = self.prepareToExport(exportType)
        accDate, accNumber, exposeDate, contractId =\
            getAccountInfo(self.parent.accountId)
        strAccNumber = accNumber if forceStringEx(accNumber) else u'б/н'
        strContractNumber = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'number')) if contractId else u'б/н'
        
        mapEventIdToSum = self.getEventsSummaryPrice()
        
        if self.idList:
            self.curIdCase = 1
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), lpuCode, lpuOKPO, lpuOGRN,
                                accNumber, strContractNumber, exposeDate, exportType, mapEventIdToSum)
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        for x in dbf:
            if x is not None:
                x.close()


    def createDbf(self, exportType):
        return (self.createReestrDbf(),
                    self.createDepReeDbf(),
                    self.createAddInfDbf() if exportType == CExportPage1.exportTypeTFOMS else None,
                    self.createOperDbf(),
                    self.createNotesDbf(),
                    # self.createDializDbf()
                    )

    
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
    

    def createReestrDbf(self):
        """ Создает структуру dbf для REESTR.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'REESTR.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NIB', 'C', 10), # 1. Номер истории болезни	Не повторяется в отчетном году
            ('INS', 'C', 2), # 2. Код СМО (по справочнику фонда)
            ('DATA1', 'D', 8), # 3. Начальная дата интервала, за который представляется реестр
            ('DATA2', 'D', 8), # 4. Конечная дата интервала, за который представляется реестр
            ('FAM', 'C', 40), # 5. Фамилия пациента
            ('IMM', 'C', 40), # 6. Имя пациента
            ('OTC', 'C', 40), # 7. Отчество пациента
            ('SER_PASP', 'C', 8), # 8. Серия документа, удостоверяющего личность
            ('NUM_PASP', 'C', 8), # 9. Номер документа, удостоверяющего личность
            ('TYP_DOC', 'N', 2), # 10. Тип документа, удостоверяющего личность (приложение «Типы документов»)	sp_документы
            ('SS', 'C', 14), # 11. Страховой номер индивидуального лицевого счета (СНИЛС)
            #('PIN', 'C', 16), # 12. Персональный  индивидуальный номер застрахованного по ОМС
            ('DROJD', 'D', 8), # 13. Дата рождения пациента
            ('POL', 'C', 1), # 14. Пол пациента   («М», «Ж»)
            ('RAB', 'C', 1), # 15. Признак работающий- “1”/неработающий – “0”
            ('SPOLIS', 'C', 10), # 16. Серия полиса
            ('NPOLIS', 'C', 20), # 17. Номер полиса
            # ('DOGOVOR', 'C', 10), # 18. Номер договора
            ('TAUN', 'C', 3), # 19. Код населенного пункта проживания пациента по справочнику фонда	TAUNS
            ('HOSP', 'C', 1), # 20. Признак поступления экстренное –“1” /плановое –“0	У нас дневной стационар =0
            # ('ISHOD', 'C', 2), # 21. Исход (фондовская кодировка) лечения в ЛПУ	Исход.dbf
            ('DATAP', 'D'), # 22. Дата поступления в ЛПУ
            ('DATAV', 'D'), # 23.Дата выписки из ЛПУ
            ('STOIM', 'N', 10, 2), # 24. Суммарная стоимость пребывания в ЛПУ
            # ('STOIM_V', 'N', 10, 2), # 25. Суммарная стоимость пребывания в ЛПУ по расчетным данным Фонда (для ЛПУ сумма=0)
            ('KRIM', 'C', 1), # 26. Признак противоправных действий	0 – обычное СБО, 1- противоправное действие.
            ('DIAG', 'C', 6), # 27. Заключительный диагноз
            ('DIRECT_LPU', 'C', 3), # 28. Код ЛПУ, направившего на госпитализацию
            ('MASTER', 'C', 9), # 29. Коды ЛПУ приписки по справочнику фонда (поликлиника + стоматология +ЖК)	В строке через 3 пробела. Пример 103   160   121
            ('LPU', 'C', 3), # 30. Код ЛПУ пребывания по справочнику фонда	141- это стационар на дому пол-ки 3, 951- реабилитация, 605- дневной стационар
            ('COUNT', 'C', 10), # 31. Номер счета представляемого в фонд
            ('STOIM_S', 'N', 10, 2), # 32. Сумма из средств Федеральных субвенций
            ('STOIM_R', 'N', 10, 2), # 33. Сумма из средств Субъекта РФ (статья 6 – иные расходы)
            # ('STOIM_F', 'N', 10, 2), # 34. Сумма доплаты из средств Федерального фонда ОМС
            ('TPOLIS', 'N', 1), # 35. Тип полиса: 	1 – старого образца, 2 – временное свидетельство, 3 – нового образца
            ('VNOV_D', 'N', 4)  # Вес при рождении в граммах
        )
        return dbf


    def createDepReeDbf(self):
        """ Создает структуру dbf для DEP_REE.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'DEP_REE.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NIB', 'C', 10), # Номер истории болезни
            ('ID_CASE', 'N', 10), # Порядковый номер случая в реестре
            ('OTD', 'C', 3), # Код отделения по справочнику фонда
            ('DIRECT_OTD', 'C', 3), # Код отделения, откуда переведен пациент (при переводе из одного отделения в другое отделение)
            ('HOSP', 'C', 1), # Признак поступления экстренное – “1” /плановое – “0”  / перевод из отделения в отделение – “2”
            ('MES', 'C', 10), # Код МЭСа без точки	R_MES
            ('MES_ZAK', 'C', 10), # Заключительный код диагноза (МЭС без точки) – диагностический стационар МДЦ
            ('DATAP', 'D', 8), # Дата поступления  в отделение
            ('DATAV', 'D', 8), # Дата выписки из отделения
            # ('ISHOD', 'C', 2), # Исход (фондовская кодировка) лечения в отделении
            ('STOIM', 'N', 10, 2), # Стоимость пребывания
            ('STOIM_V', 'N',10, 2), # Стоимость пребывания в ЛПУ по расчетным данным Фонда (для ЛПУ сумма=0)
            ('DOCTOR', 'C', 8), # Код врача лечившего пациента
            # ('SPEC', 'C', 3), # Код специальности медицинского работника, оказавшего услугу
            ('LEVEL', 'C',1), # Уровень оказанной помощи (“1”- дневные стационары,  “0” – стационары круглосуточного пребывания)
            ('TALON', 'C',6), # № направления на госпитализацию
            # ('TAL_PROF', 'C',2), # Профиль талона	TAL_PROF
            # ('SALARY', 'N', 10, 2), # Дополнительная оплата высокотехнологичных видов помощи
            ('DIAG', 'C',6), # Код МКБ Х
            ('DS0', 'C',6), # Диагноз первичный
            ('DS_S', 'C',6), # Код диагноза сопутствующего заболевания (состояния) по МКБ-10
            ('BED_PROF', 'C',3), # Код профиля койки	bed_prof
            ('STOIM_S', 'N', 10, 2), # Сумма из средств Федеральных субвенций
            ('STOIM_R', 'N', 10, 2), # Сумма из средств Субъекта РФ (статья 6 – иные расходы)
            ('STOIM_F', 'N', 10, 2), # Сумма доплаты из средств Федерального фонда ОМС
            ('PRIZN_ZS', 'N', 2), # Признак законченного случая для ВМП. (При указании значения = 50 применяется способ оплаты для высокотехнологичной медицинской помощи (ВМП) (значения = 0 для всех др.видов МП)
            ('RSLT', 'N', 3), # Результат обращения
            ('ISHOD', 'N', 3), # Исход заболевания
            ('VID_HMP', 'C', 12), # Вид ВМП
            ('METOD_HMP', 'N', 3), # Метод ВМП
            ('PROFIL', 'N', 3), # Профиль оказания МП
            ('PRVS', 'N', 4), # Код специальности врача, оказавшего услугу
            ('KSG', 'N', 5, 1), # Код КСГ
            ('DS_P', 'C', 6), # Код диагноза заболевания при переводе в другое учреждение/отделение
            )
        return dbf
    
    
    def createNotesDbf(self):
        """ Создает структуру dbf для NOTES.DBF
            (Информация о родах - только для родильных домов)"""

        dbfName = os.path.join(self.parent.getTmpDir(), 'NOTES.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NIB', 'C', 10), # 1. Номер истории болезни роженицы
            ('CHILD', 'C', 10), # 2. Номер истории развития новорожденного
            ('REM', 'C', 1),    # 3. Признак особенности: «1» – роды + новорожденный ребенок; «2» – новорожденный ребенок с патологией, требующей коррекции; «3» – роды + мертворожденный
            ('VNOV_D', 'N', 4), # 4. Вес при рождении в граммах
        )
        return dbf
    
    def createOperDbf(self):
        """ Создает структуру dbf для OPER.DBF 
            (информация по услугам, оказанным в период стационарного лечения)"""

        dbfName = os.path.join(self.parent.getTmpDir(), 'OPER.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NIB', 'C', 10), # 1. Номер истории болезни
            ('ID_CASE', 'N', 10), # 2. Порядковый номер случая
            ('OTD_O', 'C', 3), # 3. Код отделения, где проведена операция
            ('DATA_O', 'D', 8), # 4. Дата, когда проведена операция
            ('OPER', 'C', 10), # 5. Код операции
            ('KOL_OPER', 'N', 1), # 6. Количество операций
            # ('STOIM', 'N', 10, 2), # 6. Стоимость расходного материала
            # ('STOIM_V', 'N', 10, 2), # 7. Стоимость расходного материала по расчетным данным Фонда (для ЛПУ сумма = 0)
            ('DOCTOR', 'C', 8), # 7. Код врача лечившего пациента
            ('PROFIL', 'N', 3), # 8. Профиль оказанной медицинской помощи
            ('PRVS', 'N', 4), # 9. Код специальности врача, оказавшего услугу
        )
        return dbf
    
    # def createDializDbf(self):
    #     """ Создает структуру dbf для DIALIZ.DBF
    #         (информация по услугам гемодиализа)"""
    #
    #     dbfName = os.path.join(self.parent.getTmpDir(), 'DIALIZ.DBF')
    #     dbf = Dbf(dbfName, new=True, encoding='cp866')
    #     dbf.addField(
    #         ('NIB', 'C', 10), # 1. Номер истории болезни
    #         ('OTD_G', 'C', 3), # 2. Код отделения
    #         ('OPER_UG', 'C', 10), # 3. Код услуг
    #         ('KOL_UG', 'N', 3), # 4. Количество услуг
    #         ('STOIM_UG', 'N', 10, 2), # 5. Стоимость услуг по базовой программе гос. гарантий
    #         ('STOIM_V', 'N', 10, 2), # 6. Стоимость услуг по расчетным данным Фонда (для ЛПУ сумма=0)
    #     )
    #     return dbf


    def createAddInfDbf(self):
        """ Создает структуру dbf для ADD_INF.DBF """

        dbfName = os.path.join(self.parent.getTmpDir(), 'ADD_INF.DBF')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NIB', 'C', 10), # Номер истории болезни
            ('MR', 'C', 100), # Место рождения пациента или представителя
            ('OKATOG', 'C', 11), # Код места жительства по ОКАТО
            ('OKATOP', 'C', 11), # Код места пребывания по ОКАТО
            ('OKATO_OMS', 'C', 5),  # Код ОКАТО территории страхования по ОМС (по справочнику фонда)

            ('FAMP', 'C', 40), # Фамилия родителя (представителя) пациента (п.2 Примечаний)
            ('IMP', 'C', 	40), # Имя родителя (представителя) пациента (п.2 Примечаний)
            ('OTP', 'C', 40), # Отчество родителя (представителя) пациента (п.2 Примечаний)
            ('DRP', 'D', 8), # Дата рождения родителя (представителя) пациента
            ('WP', 'C', 1), # Пол родителя (представителя) пациента
            ('C_DOC', 'N', 2), # Код типа документа, удостоверяющего личность пациента (представителя) (по  справочнику фонда)
            ('S_DOC', 'C', 9), # Серия документа, удостоверяющего личность пациента (представителя) (по справочнику фонда)
            ('N_DOC', 'C', 8), # Номер документа, удостоверяющего личность пациента (представителя) (справочник фонда)	sp_документы
            ('NOVOR', 'C', 9), # Признак новорожденного
            ('Q_G', 'C', 7), # Признак «Особый случай» при регистрации обращения  за медицинской помощью
                                    #«1» –  отсутствие у пациента полиса обязательного медицинского страхования;
                                    #«2»  - медицинская помощь оказана новорожденному;
                                    #«3» – при оказании медицинской помощи ребенку до 14 лет был предъявлен документ,
                                    # удостоверяющий личность, и полис ОМС одного из его родителей или  представителей;
                                    #«4» – отсутствие отчества в документе, удостоверяющем личность пациента (представителя пациента);
                                    #«5» -  медицинская помощь, оказанная новорожденному при  многоплодных родах.
        )

        return dbf

# *****************************************************************************************

    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        
        stmt = """SELECT Event.client_id,
                Account_Item.event_id,
                ClientPolicy.serial AS policySerial,
                ClientPolicy.number AS policyNumber,
                ClientPolicy.note AS policyNote,
                rbPolicyKind.regionalCode AS policyKind,
                Insurer.infisCode AS policyInsurer,
                IF(work.title IS NOT NULL,
                    work.title,
                    ClientWork.freeInput) AS workName,
                Event.setDate AS begDate,
                Event.execDate AS endDate,
                Diagnosis.MKB,
                EventResult.regionalCode AS resultCode,
                rbDiagnosticResult.regionalCode AS diagnosticResultRegCode,
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
                IF(Account_Item.visit_id IS NOT NULL, VisitPerson.code,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, ActionPerson.code,
                            ActionSetPerson.code), Person.code)
                ) AS personCode,
                IF(Account_Item.visit_id IS NOT NULL, VisitPerson.id,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, ActionPerson.id,
                            ActionSetPerson.id), Person.id)
                ) AS personId,
                IF(Account_Item.visit_id IS NOT NULL, VisitSpeciality.regionalCode,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, ActionSpeciality.regionalCode,
                            ActionSetSpeciality.regionalCode), rbSpeciality.regionalCode)
                )  AS specialityCode,
                IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.infis,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                    ) AS service,
                IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.id,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.id, rbEventService.id)
                    ) AS serviceId,
                IF(Account_Item.visit_id IS NOT NULL, Visit.date,
                    IF(Account_Item.action_id IS NOT NULL,
                        Action.endDate, Event.execDate)
                ) AS serviceDate,
                mes.MES.descr AS bedProfile,
                Account_Item.amount,
                Visit.date AS visitDate,
                Action.endDate AS actionDate,
                Account_Item.`sum` AS `sum`,
                setOrgStruct.infisCode AS setOrgStructCode,
                OrgStructure.infisCode AS orgStructureInfisCode,
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
                RelegateOrg.infisCode AS relegateOrgCode,
                mes.MES.code AS mesCode,
                AttachOrg.infisCode AS attachCodeString,
                rbEventTypePurpose.code AS eventPurposeCode,
                rbMedicalAidType.code AS medicalAidTypeCode,
                rbScene.code AS lastVisitSceneCode,
                Event.externalId AS ticketProfile,
                EventType.code AS eventTypeCode,
                IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.federalCode, EventMedicalAidProfile.regionalCode
                  ) AS medicalAidProfileFederalCode
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
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN OrgStructure AS setOrgStruct ON Person.orgStructure_id = setOrgStruct.id
            LEFT JOIN OrgStructure ON OrgStructure.id = IF(Account_Item.visit_id IS NOT NULL, VisitPerson.orgStructure_id,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, ActionPerson.orgStructure_id,
                            ActionSetPerson.orgStructure_id), Person.orgStructure_id)
                )
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN ClientIdentification ON Client.id = ClientIdentification.client_id AND
                    ClientIdentification.deleted = 0
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
            LEFT JOIN Organisation AS RelegateOrg ON Event.relegateOrg_id = RelegateOrg.id
            LEFT JOIN ClientAttach ON ClientAttach.client_id=Event.client_id AND
                        ClientAttach.id = (SELECT max(CA.id)
                                         FROM ClientAttach AS CA
                                         WHERE CA.client_id=Client.id AND CA.deleted=0)
            LEFT JOIN Organisation AS AttachOrg ON ClientAttach.LPU_id = AttachOrg.id
            LEFT JOIN mes.MES ON Event.MES_id = mes.MES.id AND mes.MES.deleted = 0
            LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
            LEFT JOIN Visit AS LastVisit ON LastVisit.id = (SELECT max(LV.id)
                                         FROM Visit AS LV
                                         WHERE LV.event_id=Event.id AND LV.deleted=0)
            LEFT JOIN rbScene ON LastVisit.scene_id = rbScene.id
            LEFT JOIN rbService AS LastVisitService ON LastVisitService.id = LastVisit.service_id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN rbEventProfile AS EventMedicalAidProfile ON
                EventType.eventProfile_id = EventMedicalAidProfile.id

            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            ORDER BY Event.id
        """ % (tableAccountItem['id'].inlist(self.idList))
        query = db.query(stmt)
        return query

# *****************************************************************************************

    actionPropertyCache = {}

    def getActionPropertyText(self, eventId, actionTypeId, name):

        key = (eventId, actionTypeId, name)
        result = self.actionPropertyCache.get(key,  -1)

        if result == -1:
            result = None

            if actionTypeId and eventId and name:
                db=QtGui.qApp.db
                table = db.table('Action')
                record = db.getRecordEx(table, '*', [
                    table['event_id'].eq(eventId),
                    table['actionType_id'].eq(actionTypeId)])

                if record:
                    action = CAction(record=record)
                    property = action.getProperty(name)

                    if property:
                        result = property.getTextScalar()

            self.actionPropertyCache[key] = result

        return result

# *****************************************************************************************

    def process(self, dbf, record, lpuCode, lpuOKPO, lpuOGRN,  accNumber,
                contractNumber, exposeDate, exportType, mapEventIdToSum):
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        eventId = forceRef(record.value('event_id'))
        clientId = forceRef(record.value('client_id'))
        KLADRCode = forceString(record.value('KLADRCode'))
        if not KLADRCode:
            self.log(u'Отсутвует КЛАДР адрес проживания и регистрации для клиента clientId=%d' % clientId)

        if self.prevEventId is None and eventId:
            self.curIdCase = 1
            self.prevEventId = eventId
        elif self.prevEventId != eventId:
            self.curIdCase += 1
            self.prevEventId = eventId
        (dbfReestr, dbfDepRee, dbfAddInf, dbfOper) = dbf[:4]
        policySerial = forceString(record.value('policySerial'))
        policyNumber = forceString(record.value('policyNumber'))

        personId = forceRef(record.value('personId'))
        serviceId = forceRef(record.value('serviceId'))
        profile = self.getProfile(serviceId, personId) if personId and serviceId else None
        profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]

        if eventId not in self.exportedEventSet:
            row = dbfReestr.newRecord()
            row['NIB'] = eventId #, 'C', 10), # Номер истории болезни	Не повторяется в отчетном году
            insurerInfis = forceString(record.value('policyInsurer'))
            row['INS'] = insurerInfis if insurerInfis in ('14', '17') else '01' #, 'C', 2), # Код СМО (по справочнику фонда)
            firstDayDate = QDate(endDate.year(), endDate.month(), 1)
            lastDayDate = QDate(endDate.year(), endDate.month(), endDate.daysInMonth())
            row['DATA1'] = pyDate(firstDayDate) # Начальная дата интервала, за который представляется реестр
            # Конечная дата интервала, за который представляется реестр
            row['DATA2'] = pyDate(lastDayDate)
            row['FAM'] = forceString(record.value('lastName')) #, 'C', 40), # Фамилия пациента
            row['IMM'] = forceString(record.value('firstName')) #, 'C', 40), # Имя пациента
            row['OTC'] = forceString(record.value('patrName')) #, 'C', 40), # Отчество пациента
            row['SER_PASP'] = forceString(record.value('documentSerial')) # Серия документа, удостоверяющего личность
            row['NUM_PASP'] = forceString(record.value('documentNumber')) # Номер документа, удостоверяющего личность
            row['TYP_DOC'] = forceInt(record.value('documentRegionalCode')) #, 'N', 2, Тип документа, удостоверяющего личность
            row['SS'] = formatSNILS(forceString(record.value('SNILS'))) # Страховой номер индивидуального лицевого счета (СНИЛС)
            # row['PIN'] = forceString(record.value('identifier')) #, 'C', 16), # Персональный  индивидуальный номер застрахованного по ОМС
            row['DROJD'] = pyDate(forceDate(record.value('birthDate'))) #, 'D', 8), # Дата рождения пациента
            row['POL'] = u'М' if forceInt(record.value('sex')) == 1 else u'Ж' # Пол пациента   («М», «Ж»)
            row['RAB'] = ''
            row['SPOLIS'] =  policySerial #, 'C', 10), # Серия полиса
            row['NPOLIS'] =  policyNumber #, 'C', 10), # Номер полиса
            # row['DOGOVOR'] = forceString(record.value('policyNote')) #, 'C', 10), # Номер договора
            placeCode = forceString(record.value('placeCode'))
            row['TAUN'] = placeCode if placeCode and placeCode != '000' else '' # Код населенного пункта проживания пациента по справочнику фонда
            row['HOSP'] = '0' # Признак поступления экстренное –“1” /плановое –“0	У нас дневной стационар =0
            # row['ISHOD']  = forceString(record.value('resultCode')) # Исход (фондовская кодировка) лечения в ЛПУ
            row['DATAP'] = pyDate(begDate) # Дата поступления в ЛПУ
            row['DATAV'] = pyDate(endDate) # Дата выписки из ЛПУ
            (sum,  federalSum) = mapEventIdToSum.get(eventId, (0.0, 0.0))
            row['STOIM'] = sum # Суммарная стоимость пребывания в ЛПУ
            row['STOIM_S'] = row['STOIM']
            # row['STOIM_V'] = 0 # Суммарная стоимость пребывания в ЛПУ по расчетным данным Фонда (для ЛПУ сумма=0)
            row['TPOLIS'] = forceInt(record.value('policyKind'))
    
            #, 'C', 1), # Признак противоправных действий	0 – обычное СБО, 1- противоправное действие.
            criminalSign = self.getActionPropertyText(eventId, self.actionTypeIllegalActions, u'Признак')
    
            if criminalSign:
                row['KRIM'] = criminalSign
    
            row['DIAG'] = forceString(record.value('MKB')) # Заключительный диагноз
            
            #Дневной стационар - EventType.code = 27
            #Стационар на дому - EventType.code = 25
            #Реабилитация - EventType.code = 26
            eventTypeCode = forceString(record.value('eventTypeCode'))
            
            attachOrgInfisCode = forceString(record.value('attachCodeString'))
            
            #DIRECT_LPU - "дневной стационар" и "стационар на дому" = 105. "реабилитация" взять значение из прикрепления пациента
            directLPU = '105' if (eventTypeCode == '27' or eventTypeCode == '25') else (attachOrgInfisCode if (eventTypeCode == '26' or eventTypeCode == '27-диа') else '')
            row['DIRECT_LPU'] = directLPU # Код ЛПУ, направившего на госпитализацию
    #        if not row['DIRECT_LPU']:
    #            relegateOrgCode = self.getActionPropertyText(eventId, self.actionTypeArrival, u'Кем направлен')
    #            if relegateOrgCode:
    #                row['DIRECT_LPU'] = relegateOrgCode
            
            row['MASTER'] = attachOrgInfisCode if attachOrgInfisCode != '999' else '000' #, 'C', 9), # Коды ЛПУ приписки по справочнику фонда (поликлиника + стоматология +ЖК)	В строке через 3 пробела. Пример 103   160   121
            # Код ЛПУ пребывания по справочнику фонда
            row['LPU'] = '606' if eventTypeCode == '27' else ('143' if eventTypeCode == '25' 
                                                                    else ('825' if eventTypeCode == '26' 
                                                                                else ('073' if eventTypeCode == '27-диа'
                                                                                            else lpuCode)))
            row['COUNT'] = accNumber # Номер счета представляемого в фонд
            row.store()

            row = dbfDepRee.newRecord()
            row['NIB'] = forceString(eventId) #, 'C', 10), # Номер истории болезни
            row['ID_CASE'] = self.curIdCase
            row['OTD'] = '029' if (eventTypeCode == '27' or eventTypeCode == '25') else ('099' if eventTypeCode == '26'
                                                                                               else ('740' if eventTypeCode == u'27-диа'
                                                                                                           else '0')) #, 'C', 3), # Код отделения по справочнику фонда
            medicalAidTypeCode = forceString(record.value('medicalAidTypeCode'))
    #        eventPurposeCode = forceString(record.value('eventPurposeCode'))
    #        lastVisitSceneCode = forceString(record.value('lastVisitSceneCode'))
    
    #        if medicalAidTypeCode == '7': # Дневной стационар
    #            row['OTD'] = '5' # Дневной стационар при поликлинике
    #
    #            if eventPurposeCode == '6': # Реабилитация
    #                row['OTD'] = 'A' # Реабилитация
    #
    #            if lastVisitSceneCode in ('2','3'): # на дому
    #                row['OTD'] = 'C'
    
            #, 'C', 3), # Код отделения, откуда переведен пациент (при переводе из одного отделения в другое отделение)
            row['DIRECT_OTD'] = '' #self.getActionPropertyText(eventId, self.actionTypeMovement, u'Переведен из отделения')
            #, 'С', 1), # Признак поступления экстренное – “1” /плановое – “0”  / перевод из отделения в отделение – “2”
            row['HOSP'] = '2' if row['DIRECT_OTD'] else '0'
            #, 'С', 10), # Код МЭСа без точки	R_MES
            row['MES'] = forceString(record.value('mesCode')).replace('.', '')
            #, 'С', 10), # Заключительный код диагноза (МЭС без точки) – диагностический стационар МДЦ
            row['MES_ZAK'] = ''
            row['DATAP'] = pyDate(begDate) # Дата поступления  в отделение
            row['DATAV'] = pyDate(endDate) # Дата выписки из отделения
            row['PRIZN_ZS'] = 0 # Признак законченного случая. Актуален только для ВМП.
            #, 'C', 2), # Исход (фондовская кодировка) лечения в отделении
            row['RSLT'] = forceInt(record.value('resultCode'))
            row['ISHOD'] = forceInt(record.value('diagnosticResultRegCode'))
            #, 'N', 10, 2), # Стоимость пребывания
            row['STOIM'] = sum
            row['STOIM_S'] = row['STOIM']
            #, 'N',10, 2), # Стоимость пребывания в ЛПУ по расчетным данным Фонда (для ЛПУ сумма=0)
            row['STOIM_V'] = 0
            #'C', 8, Код врача лечившего пациента
            row['DOCTOR'] = forceString(record.value('personCode'))
            # Код специальности медицинского работника, оказавшего услугу
            row['PRVS'] = forceInt(record.value('specialityCode'))
            # row['SPEC'] = forceString(record.value('specialityCode'))


            row['PROFIL'] = forceInt(profileStr)
            #'C',1, Уровень оказанной помощи (“1”- дневные стационары,  “0” – стационары круглосуточного пребывания)
            row['LEVEL'] = '1' if medicalAidTypeCode == '7' else '0'
            # 'C',6), № направления на госпитализацию
            row['TALON'] = forceString(record.value('directionNumber'))
            # Профиль талона	TAL_PROF
            #row['TAL_PROF'] = forceString(record.value('ticketProfile'))
            #, 'N', 10, 2), Дополнительная оплата высокотехнологичных видов помощи
            # row['SALARY'] = 0
            # Код МКБ Х
            row['DIAG'] = forceString(record.value('MKB'))
            # Код диагноза сопутствующего заболевания (состояния) по МКБ-10
            row['DS_S'] = forceString(record.value('AccMKB'))
            row['BED_PROF'] = forceString(record.value('bedProfile')) # Код профиля койки (взят из mes.MES.descr)
            row.store()


        row = dbfOper.newRecord()
        row['NIB'] = forceString(eventId)
        row['ID_CASE'] = self.curIdCase
        row['OTD_O'] = forceString(record.value('orgStructureInfisCode'))[:3]
        row['DATA_O'] = pyDate(forceDate(record.value('serviceDate')))
        row['OPER'] = forceString(record.value('service'))
        row['KOL_OPER'] = forceInt(record.value('amount'))
        row['DOCTOR'] = forceString(record.value('personCode'))
        row['PROFIL'] = forceInt(profileStr)
        row['PRVS'] = forceInt(record.value('specialityCode'))
        row.store()

        if exportType == self.exportTypeTFOMS:
            insurerOKATO = forceString(record.value('insurerOKATO'))
            # ОКАТО всех объектов Мурманской области начинается с 47 (у Мурманской области окато 47000000000)
            if insurerOKATO[:2] != '47':
                row = dbfAddInf.newRecord()
    
                row['NIB'] = forceString(eventId) # Номер истории болезни
                row['MR'] = forceString(record.value('birthPlace')) # Место рождения пациента или представителя
    
                # Код места жительства по ОКАТО
                row['OKATOG'] = forceString(record.value('regionOKATO'))
                # Код места пребывания по ОКАТО
                row['OKATOP'] = forceString(record.value('regionOKATO'))
                # Код ОКАТО территории страхования по ОМС (по справочнику фонда)
                row['OKATO_OMS'] = insurerOKATO
                # Статус представителя пациента
                info = self.getClientRepresentativeInfo(clientId)
                age = forceInt(record.value('clientAge'))
    
#                # Фамилия родителя (представителя) пациента (п.2 Примечаний)
#                if info != {}:
#                    # Пол родителя (представителя) пациента
#                    row['WP']  = u'М' if info.get('sex', 1) == 1 else u'Ж'

                # Код типа документа, удостоверяющего личность пациента (представителя) (по  справочнику фонда)
                row['C_DOC'] = forceInt(record.value('documentRegionalCode'))
                #, 'C', 9), # Серия документа, удостоверяющего личность пациента (представителя) (по справочнику фонда)
                row['S_DOC'] = forceString(record.value('documentSerial'))
                # Номер документа, удостоверяющего личность пациента (представителя) (справочник фонда)	sp_документы
                row['N_DOC'] = forceString(record.value('documentNumber'))
                row['NOVOR'] = '' # Признак новорожденного
    
                specialCase = []
    
                # «1» –  отсутствие у пациента полиса обязательного медицинского страхования;
                if not policySerial and not policyNumber:
                    specialCase.append('1')
    
                #«2»  - медицинская помощь оказана новорожденному;
                if age < 1:
                    specialCase.append('2')
    
                    #«3» – при оказании медицинской помощи ребенку до 14 лет был предъявлен документ,
                    # удостоверяющий личность, и полис ОМС одного из его родителей или  представителей;
                    if not forceBool(record.value('hasBirthCertificate')):
                        specialCase.append('3')
    
                    multipleBirth = self.getActionPropertyText(eventId, self.actionTypeMultipleBirth, u'Признак') != ''
                    #«5» -  медицинская помощь, оказанная новорожденному при  многоплодных родах.
                    if multipleBirth:
                        specialCase.append('5')
    
                #«4» – отсутствие отчества в документе, удостоверяющем личность пациента (представителя пациента);
                if not forceString(record.value('patrName')):
                    specialCase.append('4')
    
                row['Q_G'] = ' '.join(x for x in specialCase)
                row.store()
        self.exportedEventSet.add(eventId)

# *****************************************************************************************
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
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ExportR51HospitalExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        fileList = ['REESTR.DBF', 'DEP_REE.DBF', 'NOTES.DBF', 'OPER.DBF']

        if self.parent.page1.cmbExportType.currentIndex() == CExportPage1.exportTypeTFOMS:
            fileList.append('ADD_INF.DBF')

        for src in fileList:
            srcFullName = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                    os.path.basename(src))
            dst = os.path.join(forceStringEx(self.edtDir.text()),
                                                    os.path.basename(src))
            success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

            if not success:
                break

        if success:
            QtGui.qApp.preferences.appPrefs['ExportR51HospitalExportDir'] = toVariant(self.edtDir.text())
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
