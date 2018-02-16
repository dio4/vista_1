# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import os.path
import shutil
import zlib

from library.dbfpy.dbf import *
from zipfile import *
from library.Utils     import *
from library.crbcombobox import CRBComboBox
from Exchange.Utils    import CExportHelperMixin
from Registry.Utils     import *

from Ui_ExportR23NativePage1 import Ui_ExportR23NativePage1
from Ui_ExportR23NativePage2 import Ui_ExportR23NativePage2


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number, exposeDate, contract_id, settleDate', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        number = forceString(accountRecord.value('number'))
        contractId = forceRef(accountRecord.value('contract_id'))
        settleDate = forceDate(accountRecord.value('settleDate'))
    else:
        date = exposeDate = contractId = None
        number = ''
    return date, number, exposeDate, contractId, settleDate


def exportR61Native(widget, accountId, accountItemIdList, isStacionar = False):
    wizard = CExportWizard(widget)
    wizard.isStacionar = isStacionar
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
        self.setWindowTitle(u'Мастер экспорта в ОМС Ростова')
        self.dbfFileName = ''
        self.tmpDir = ''
        self.contractId = None


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId, sdate = getAccountInfo(accountId)
        self.contractId = contractId
        strNumber = (number if trim(number) else u'б/н')
        self.accountNumber = number
        strDate = forceString(date) if date.isValid() else u'б/д'
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


# *****************************************************************************************

class CExportPage1(QtGui.QWizardPage, Ui_ExportR23NativePage1, CExportHelperMixin):
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

        self._specialityOKSOCodeCache = {}
        self.processedEvents = []

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.tariffCache = {}
        self.parent = parent
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR23NativeIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR23NativeVerboseLog', 'False')))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.exportedTempInvalidList = []
        self.tempInvalidCache = {}
        self.exportedClients = set()
        self.modernClients = set()

        self.edtRegistryNumber.setVisible(False)
        self.cmbPayMethod.setVisible(False)
        self.cmbAccountType.setVisible(False)
        self.lblRegistryNumber.setVisible(False)
        self.lblPayMethod.setVisible(False)
        self.lblAccountType.setVisible(False)


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.cmbAccountType.setEnabled(not flag)
        self.cmbPayMethod.setEnabled(not flag)
        self.edtRegistryNumber.setEnabled(not flag)


    def log(self, str, forceLog = False):
        if self.chkVerboseLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.eventData = {}
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        personQuery = self.createPersonQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query, personQuery


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

    def getDbfBaseName(self, modern):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
        postfix= u'M' if modern else u''
        return u'%s%s.DBF' % (lpuCode, postfix)


    def getZipFileName(self, modern):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
        accDate, accNumber, exposeDate, contractId, sdate = getAccountInfo(self.parent.accountId)

        return u'%s3%02d.zip' % (lpuCode[:5],  pyDate(sdate).month)

# *****************************************************************************************

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        lpuId = QtGui.qApp.currentOrgId()
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', lpuId , 'infisCode'))
        self.log(u'ЛПУ: код инфис: "%s".' % lpuCode)

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан код инфис', True)
            if not self.ignoreErrors:
                return

        dbf, query, personQuery = self.prepareToExport()
        self.getEventData()
        accDate, accNumber, exposeDate, contractId, sdate = getAccountInfo(self.parent.accountId)


        iAccNumber = 0
        self.exportedTempInvalidList = []
        self.exportedClients = set()

        strContractNumber = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'number')) if contractId else u'б/н'
        accNumber = accNumber.replace(strContractNumber + u'-', u'')
        accNumberSplit = accNumber.split('/')
        if len(accNumberSplit) > 1:
            accNumber = accNumberSplit[0]
        try:
            iAccNumber = forceInt(accNumber)
        except:
            self.log(u'Невозможно привести номер счёта' \
                       u' "%s" к числовому виду' % accNumber)


        payMethod = self.mapPayMethod.get(self.cmbPayMethod.currentIndex())
        accType = self.cmbAccountType.code()
        self.clientInfo = self.getClientInfo()
        self.modernClients = set() # модернизированные пациенты (есть федеральная цена)

        payerId = forceRef(QtGui.qApp.db.translate(
            'Contract', 'id', self.parent.contractId, 'payer_id'))
        payerOGRN = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', payerId, 'OGRN')) if payerId else ''
        self.log(u'ОГРН плательщика `%s`.' % payerOGRN)

        if self.idList:
            # Составляем множество событий, содержащих услуги с модернизацией
            while query.next():
                record = query.record()
                if record:
                    federalPrice = forceDouble(record.value('federalPrice'))

                    if federalPrice != 0.0:
                        self.modernClients.add(forceRef(record.value('client_id')))

            query.exec_() # встаем перед первой записью

            self.processedEvents = []

            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), lpuCode,
                                iAccNumber, exposeDate, payMethod, accType, payerOGRN, sdate)

            #while personQuery.next():
            #    QtGui.qApp.processEvents()
            #    if self.aborted:
            #        break
            #    self.progressBar.step()
            #    self.processPerson(dbf, personQuery.record(), lpuCode)
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        for x in dbf:
            x.close()
            self.writeByte(x.name, 29, 0x65)    # set codepage "Russian MS-DOS"


    def createDbf(self):
        return (self.createPACIENTPDbf(False),
                self.createTALONDbf(False),
                self.createTALON1Dbf(False),
                self.createPOSLPRDbf(False),
                self.createUSLUGIPDbf(False),
                self.createRODPDbf(False),
                # модернизация
                self.createPACIENTPDbf(True),
                self.createTALONDbf(True),
                self.createTALON1Dbf(True),
                self.createPOSLPRDbf(True),
                self.createUSLUGIPDbf(True),                
                self.createRODPDbf(True)
            )

    rodpFields = {
        'NREESTR'   : True, 
        'KODP'      : True, 
        'NSVOD'     : True,
        'KODLPU'    : True,
        'FAMROD'    : True,
        'IMROD'     : True,
        'OTROD'     : True,
        'DROGD'     : True,
        'KODST'     : False,
        'NSTRA'     : False,
        'SERIA'     : False,
        'NPOLI'     : True,
        'SERROD'    : False,
        'NOMROD'    : True,
        'SVERTKA'   : True, 
        'STAT_P'    : True,
        'POLPA'     : True,
        'VIDDK'     : True,
        'CODE_MO'   : True, 
        'VPOLIS'    : True,
        'MR'        : False, 
        'SMO_ID'    : True,
        'VPOLIS_ID' : False,
        'SPOLIS_ID' : False,
        'NPOLIS_ID' : False
    }
    
        
    def createRODPDbf(self, modern):
        u"""Создает структуру, которая содержит информацию о родителе в случае оказания медицинской помощи новорожденному до государственной регистрации."""
        
        dbfName = os.path.join(self.parent.getTmpDir(), 'RODP%s.DBF' % ('M' if modern else ''))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NREESTR', 'N', 5, 0),
            ('KODP', 'N', 10, 0),
            ('NSVOD', 'N', 3, 0 ),
            ('KODLPU', 'N', 7, 0 ),            
            ('FAMROD', 'C', 40),
            ('IMROD', 'C', 40),
            ('OTROD', 'C', 40),
            ('DROGD', 'D'),
            ('KODST', 'C', 5),
            ('NSTRA', 'C', 100),
            ('SERIA', 'C', 10),
            ('NPOLI', 'C', 20),
            ('SERROD', 'C', 10),
            ('NOMROD', 'C', 20),
            ('SVERTKA', 'C', 16),
            ('STAT_P', 'N', 1, 0),
            ('POLPA', 'N', 1, 0),
            ('VIDDK', 'C', 2),
            ('CODE_MO', 'C', 6),
            ('VPOLIS', 'N', 1, 0),
            ('MR', 'C', 100),
            ('SMO_ID', 'C', 5),
            ('VPOLIS_ID', 'N', 1, 0),
            ('SPOLIS_ID', 'C', 10),
            ('NPOLIS_ID', 'C', 20),
        )
        return dbf

    polsprFields = {
        'NREESTR' : [True, u'Номер cчета'],
        'KODLPU'  : [True, u'Код МО, код подразделения'],
        'NSCHT'   : [True, u'Номер индивидуального счета'],
        'NSVOD'   : [True, u'Номер сводного счета, в который включена эта запись'],
        'DATAP'   : [True, u'Дата поступления в отделение'],
        'SHDZ'    : [True, u'Шифр основного диагноза по МКБ 10 до уровня подрубрики'],
        'KSPEC'   : [True, u'Код тарифа посещения врача ведущего прием'],
        'ZPL'     : [True, u'Оплата труда с начислениями во внебюджетные фонды'],
        'MED' 	  : [True, u'Стоимость медикаментов и перевязочных средств'],
        'M_INV'   : [True, u'Стоимость мягкого инвентаря'],
        'KOS'     : [True, u'Косвенные начисления'],
        'NAKL'    : [True, u'Накладные расходы'],
        'DOPL'    : [True, u'Доплаты узким специалистам/участковой службе'],
        'STOIM'   : [True, u'Стоимость данного посещения'],
        'DS0'     : [False,u'Диагноз первичный'],
        'DS2'     : [False,u'Диагноз сопутствующий'],
        'IDSP'    : [True, u'Код способа оплаты'],
        'ED_COL'  : [False,u'Количество единиц оплаты медицинской помощи'],
        'TARIF'   : [False,u'Стоимость за 1 еденицу оплаты медицинской помощи'],
        'LPU'     : [True, u'Реестровый номер МО лечения'],
        'LPU_1'   : [False,u'Подразделение. Код подразделения МО лечения из региона'],
        'PROFIL'  : [True, u'Профиль'],
        'PRVS'    : [True, u'Специальность лечащего врача/ врача, закрывшего талон'],
        'IDDOKT'  : [False,u'Код лечащего врача/ врача, закрывшего талон'],
        'PODR'    : [True, u'Код отделения МО лечения из регионального справочника'],
        'DET'     : [False,u'Признак детского профиля. 0- нет; 1 – да']
    }                      

    def createPOSLPRDbf(self, modern):
        u"""Структура содержит сведения о посещениях пациентом врача по каждому индивидуальному счету."""

        dbfName = os.path.join(self.parent.getTmpDir(), 'POSLPR%s.DBF' % ('M' if modern else ''))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NREESTR',	'N',	5, 0	), #Номер cчета.
            ('KODLPU',	'N',	7, 0	), #Код МО, код подразделения. Заполняется в соттвествие с региональным справочником (Приложение 2).            
            ('NSCHT',	'N',	8, 0	), #Номер индивидуального счета.
            ('NSVOD',	'N',	3, 0	), #Номер сводного счета, в который включена эта запись.
            ('DATAP',	'D'		),         #Дата поступления в отделение.            
            ('SHDZ',	'C',	10	),     #Шифр основного диагноза по МКБ 10 до уровня подрубрики.
            ('KSPEC',	'N',	11, 0	), #Код тарифа посещения врача ведущего прием. Заполняется в соответствие с порядком кодирования тарифов (приложение 6).
            ('ZPL', 	'N',	11,2),     #Оплата труда с начислениями во внебюджетные фонды.
            ('MED', 	'N',	11,2),     #Стоимость медикаментов и перевязочных средств.
            ('M_INV',	'N',	11,2),     #Стоимость мягкого инвентаря.
            ('KOS', 	'N',	11,2),     #Косвенные начисления.
            ('NAKL',    'N',    11,2),     #Накладные расходы.
            ('DOPL',    'N',    11,2),     #Доплаты узким специалистам/участковой службе
            ('STOIM',	'N',	11,2),     #Стоимость данного посещения.
            ('DS0', 	'C',	10	),     #Диагноз первичный. Код из справочника МКБ 10 до уровня подрубрики. Заполняется при наличии.
            ('DS2', 	'C',	10	),     #Диагноз сопутствующий. Код из справочника МКБ 10 до уровня подрубрики. Заполняется при наличии.
            ('IDSP',	'N',	2, 0	), #Код способа оплаты. Заполняется в соответствие с Классификатором V010.
            ('ED_COL',	'N',	5, 2),     #Количество единиц оплаты медицинской помощи.
            ('TARIF',	'N',	11,2),     #Стоимость за 1 еденицу оплаты медицинской помощи.
            ('LPU', 	'C',	6	),     #Реестровый номер МО лечения (Классификатор F003).
            ('LPU_1',	'C',	6	),     #Подразделение. Код подразделения МО лечения из регионального справочника.
            ('PROFIL',	'N',	3, 0	), #Профиль (Классификатор V002).
            ('PRVS',	'N',	9	),     #Специальность лечащего врача/ врача, закрывшего талон. Заполняется в соответствие с Классификатором V004.
            ('IDDOKT',	'C',	16	),     #Код лечащего врача/ врача, закрывшего талон. Заполняется из регионального справочника. До момента принятия регионального справочника медицинских работников значение поля равно 0(ноль).
            ('PODR',	'N',	8, 0	), #Код отделения МО лечения из регионального справочника. Заполняется первыми 4 символами кода тарифа.
            ('DET', 	'N',	1, 0	), #Признак детского профиля. 0- нет; 1 – да.
        )
        return dbf

    uslugipFields = {
        'NREESTR' : True,
        'NSVOD' : True,
        'NSCHT' : True,
        'KODLPU' : True,
        'KSPECP' : True,
        'DATE_IN' : True,
        'DATE_OUT' : True,
        'KODUS' : True,
        'SHDZ' : True,
        'KRATN' : True,
        'NZUB' : False,
        'ZPL' : True,
        'MED' : True,
        'M_INV' : True,
        'KOS' : True,
        'NAKL' : True,
        'STOIM' : True,
        'IDSP' : True,
        'PROFIL' : True,
        'IDDOKT' : False, #True,
        'PODR' : True,
        'DET' : False, #True,
        'LPU' : True,
        'LPU_1' : False
    }

    def createUSLUGIPDbf(self, modern):
        u"""Создает структуру переченя услуг, оказанных пациенту, по каждому индивидуальному счету."""

        dbfName = os.path.join(self.parent.getTmpDir(), 'USLUGIP%s.DBF'  % ('M' if modern else ''))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NREESTR',	'N',	5, 0	), #Номер счета.
            ('NSVOD',	'N',	3, 0	), #Номер сводного счета, в который включена эта услуга.
            ('NSCHT',	'N',	8, 0	), #Номер индивидуального счета.
            ('KODLPU',	'N',	7, 0	), #Код МО, код подразделения (Приложение 2).            
            ('KSPECP',	'N',	11, 0	), #Код тарифа. Заполняется в соответствие с порядком кодировки тарифов (Приложение 7).
            ('DATE_IN',	'D'		), #Дата начала оказания медицинской услуги.
            ('DATE_OUT','D'		), #Дата окончания оказания медицинской услуги .
            ('KODUS',	'C',	16	), #Код медицинской услуги в соответствии с Классификатором медицинских услуг.
            ('SHDZ',    'C',	11	), #Шифр диагноза по МКБ 10 до уровня подрубрики.
            ('KRATN',	'N',	5,2	), #Количество оказанных услуг.
            ('NZUB',    'C',	2	), #№ зуба для стоматологической мед.помощи.
            ('ZPL', 	'N',	11,2), #	Оплата труда с начислениями во внебюджетные фонды.
            ('MED', 	'N',	11,2), #	Стоимость медикаментов и перевязочных средств.
            ('M_INV',	'N',	11,2), #	Стоимость мягкого инвентаря.
            ('KOS', 	'N',	11,2), #	Косвенные начисления.
            ('NAKL',    'N',    11,2),
            ('STOIM',	'N',	11,2), #	Стоимость оказанных услуг.
            ('TARIF',	'N',	11,2), 
            ('IDSP',	'N',	2, 0	), #Код способа оплаты. Заполняется в соттветствие с Классификатором V010.
            ('PROFIL',	'N',	3, 0	), #Профиль (Классификатор V002).
            ('IDDOKT',	'C',	16	), #Код медицинского работника, оказавшего услугу. Заполняется из регионального справочника. До момента принятия регионального справочника медицинских работников значение поля равно 0(ноль).
            ('PRVS',	'N',	9   ),
            ('PODR',	'N',	8, 0	), #Код отделения МО лечения из регионального справочника. Заполняется первыми 4 символами кода тарифа.
            ('DET', 	'N',	1, 0	), #Признак детского профиля. 0- нет; 1 – да.
            ('LPU', 	'C',	6	), #Реестровый номер МО лечения (Классификатор F003).
            ('LPU_1',	'C',	6	), #Подразделение. Подразделение МО лечения из регионального справочника. 
        )    
        return dbf

    talonFields = {
        'NREESTR' : [True,  u'Номер счета'],
        'KODLPU'  : [True,  u'Код МО и её подразделения'],
        'NSVOD'   : [True,  u'Номер сводного счета, в который включена эта запись'],
        'KODP'    : [True,  u'Код пациента соответствует коду в файле PACIENTS.DBF'],
        'NSCHT'   : [True,  u'Номер индивидуального счета, указанный на статистической карте выбывшего (должен быть уникальным в пределах одного года)'],
        'NIBLZ'   : [True,  u'Номер медицинской карты'],
        'DATAS'   : [True,  u'Дата зактытия талона'],
        'PRZAB'   : [True,  u'Характер заболевания'],
        'SHDZO'   : [True,  u'Шифр основного диагноза по МКБ 10 до уровня подрубрики'],
        'SHDZS'   : [False, u'Шифр сопутствующего диагноза по МКБ 10 до уровня подрубрики. Заполняется при наличии'],
        'SHDZOS'  : [False, u'Шифр осложняющего диагноза по МКБ 10 до уровня подрубрики. Заполняется при наличии'],
        'ABZAC'   : [True,  u'Случай закончен (1 - Да, 0 - Нет)'],
        'ZPL'     : [True,  u'Оплата труда с начислениями во внебюджетные фонды'],
        'MED'     : [True,  u'Стоимость медикаментов и перевязочных средств'],                                                                                                                                                                                                                                                                                                                                            
        'M_INV'   : [True,  u'Стоимость мягкого инвентаря'],
        'KOS'     : [True,  u'Косвенные начисления'],
        'NAKL'    : [True,  u'Накладные расходы'],
        'DOPL'    : [True,  u'Доплаты узким специалистам/участковой службе'],
        'STOIM'   : [True,  u'Стоимость лечения пациента  – общая сумма индивидуального счета (по расчету МО)'],
        'NAPUCH'  : [False, u'Код МО, направившей на госпитализацию (Приложение 2)'],
        'NAPDAT'  : [False, u'Дата направления'],
        'DS0'     : [False, u'Диагноз первичный'],
        'RSLT'    : [True,  u'Результат обращения'],
        'USL_OK'  : [True,  u'Условия оказания медицинской помощи'],
        'VIDPOM'  : [True,  u'Вид оказания медицинской помощи'],
        'EXTR'    : [True,  u'Направление (госпитализация)'],
        'PRVS'    : [True,  u'Специальность врача, закрывшего талон'],
        'IDDOKT'  : [False, u'Код врача, закрывшего историю болезни'],
        'CNILSVR' : [True,  u'СНИЛС врача'],
        'ISHOD'   : [True,  u'Исход госпитализации'],
        'CODE_MO' : [True,  u'Реестровый номер МО лечения'],
        'OS_SLUCH': [True,  u'Указываются все имевшиеся особые случаи']
    }                        

    def createTALON1Dbf(self, modern):
        u"""Создает структуру индивидуальных счетов, включенных в реестр сводных счетов за отчетный период"""
        
        dbfName = os.path.join(self.parent.getTmpDir(), 'TALON1%s.DBF'  % ('M' if modern else ''))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NREESTR', 'N',	5, 0), #Номер счета.
            ('KODLPU',  'N',    7, 0), #Код МО и её подразделения (приложение 3).            
            ('NSVOD',	'N',	3, 0), #Номер сводного счета, в который включена эта запись.
            ('KODP',	'N',	10, 0), #Код пациента соответствует коду в файле PACIENTS.DBF.
            ('NSCHT',	'N',	8, 0), #Номер индивидуального счета, указанный на статистической карте выбывшего (должен быть уникальным в пределах одного года).          
            ('NIBLZ',	'C',	50), #Номер медицинской карты.
            ('DATAS',	'D'      	), #Дата зактытия талона
            ('PRZAB',	'N',	1, 0	), #Характер заболевания
                                       #0 – прочее;
                                       #1 – заболевание острое;
                                       #2 – хроническое, выявленное впервые;
                                       #3 – хроническое, известное ранее;
                                       #4 – обострение хронического заболевания;
                                       #5 – отравление;
                                       #6 – травма бытовая;
                                       #7 – здоров;
                                       #8 – несчастный случай на производстве.
            ('SHDZO',	'C',	10	), #Шифр основного диагноза по МКБ 10 до уровня подрубрики
            ('SHDZS',	'C',	10	), #Шифр сопутствующего диагноза по МКБ 10 до уровня подрубрики. Заполняется при наличии.
            ('SHDZOS',	'C',	10	), #Шифр осложняющего диагноза по МКБ 10 до уровня подрубрики. Заполняется при наличии.
            ('ABZAC', 	'N',	1, 0	), #Случай закончен (1 - Да, 0 - Нет).
            ('ZPL', 	'N',	11,2), #Оплата труда с начислениями во внебюджетные фонды.
            ('MED',  	'N',	11,2), #Стоимость медикаментов и перевязочных средств.
            ('M_INV',	'N',	11,2), #Стоимость мягкого инвентаря.
            ('KOS',	    'N',	11,2), #Косвенные начисления.
            ('NAKL',    'N',    11,2),
            ('DOPL',    'N',    11,2),
            ('STOIM',	'N',	11,2), #Стоимость лечения пациента  – общая сумма индивидуального счета (по расчету МО).
            ('NAPUCH',	'N',	7, 0	), #Код МО, направившей на госпитализацию (Приложение 2).
            ('NAPDAT',	'D'		), #Дата направления. 
            ('DS0', 	'C',	10	), #Диагноз первичный. Код из справочника МКБ до уровня подрубрики. Указывается при наличии.
            ('RSLT',	'N',	3, 0	), #Результат обращения. Заполняется в соотвествие с Классификатором V009.
            ('USL_OK',	'N',	2, 0	), #Условия оказания медицинской помощи. Заполняется в соответствие с классификатором V006.
            ('VIDPOM',	'N',	4, 0	), #Вид оказания медицинской помощи. Заполняется в соотвествие с Классификатором V008.
            ('EXTR',	'N',	2, 0	), #Направление (госпитализация) 1 –плановая; 2 – экстренная.
            ('PRVS', 	'N',	9	), #Специальность врача, закрывшего талон. Заполняется в соответствие с Классификатором V004.
            ('IDDOKT',	'C',	16	), #Код врача, закрывшего историю болезни. Заполняется из регионального справочника. До момента принятия регионального справочника медицинских работников значение поля равно 0(ноль).
            ('CNILSVR', 'C',	14	), #СНИЛС врача.
            ('ISHOD',	'N',	3, 0	), #Исход госпитализации. Заполняется в соотвествие с Классификатором V012.
            ('CODE_MO',	'C',	6	), #Реестровый номер МО лечения (Классификатор F003).
            ('OS_SLUCH','C',	4	), #Указываются все имевшиеся особые случаи. 0- нет особых случаев; 1- мед.помощь оказана новорожденному до государственной регистрации при многоплодных родах; 2- в документе, удостоверяющем личность пациента/представителя отсутствует отчество. При наличии нескольких случаев указываютя оба случая через «;». Возможные варианты заполнения: «0;», «1;», «2;», «1;2;», «2;1;».
            ('KSPECTAR', 'N', 11)
        )
        return dbf
        
    def createTALONDbf(self, modern):
        u"""Создает структуру индивидуальных счетов, включенных в реестр сводных счетов за отчетный период"""
        
        dbfName = os.path.join(self.parent.getTmpDir(), 'TALON%s.DBF'  % ('M' if modern else ''))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NREESTR', 'N',	5, 0), #Номер счета.
            ('KODLPU',  'N',    7, 0), #Код МО и её подразделения (приложение 3).            
            ('NSVOD',	'N',	3, 0), #Номер сводного счета, в который включена эта запись.
            ('KODP',	'N',	10, 0), #Код пациента соответствует коду в файле PACIENTS.DBF.
            ('NSCHT',	'N',	8, 0), #Номер индивидуального счета, указанный на статистической карте выбывшего (должен быть уникальным в пределах одного года).          
            ('NIBLZ',	'C',	50), #Номер медицинской карты.
            ('DATAS',	'D'      	), #Дата зактытия талона
            ('PRZAB',	'N',	1, 0	), #Характер заболевания
                                       #0 – прочее;
                                       #1 – заболевание острое;
                                       #2 – хроническое, выявленное впервые;
                                       #3 – хроническое, известное ранее;
                                       #4 – обострение хронического заболевания;
                                       #5 – отравление;
                                       #6 – травма бытовая;
                                       #7 – здоров;
                                       #8 – несчастный случай на производстве.
            ('SHDZO',	'C',	10	), #Шифр основного диагноза по МКБ 10 до уровня подрубрики
            ('SHDZS',	'C',	10	), #Шифр сопутствующего диагноза по МКБ 10 до уровня подрубрики. Заполняется при наличии.
            ('SHDZOS',	'C',	10	), #Шифр осложняющего диагноза по МКБ 10 до уровня подрубрики. Заполняется при наличии.
            ('ABZAC', 	'N',	1, 0	), #Случай закончен (1 - Да, 0 - Нет).
            ('ZPL', 	'N',	11,2), #Оплата труда с начислениями во внебюджетные фонды.
            ('MED',  	'N',	11,2), #Стоимость медикаментов и перевязочных средств.
            ('M_INV',	'N',	11,2), #Стоимость мягкого инвентаря.
            ('KOS',	    'N',	11,2), #Косвенные начисления.
            ('NAKL',    'N',    11,2),
            ('DOPL',    'N',    11,2),
            ('STOIM',	'N',	11,2), #Стоимость лечения пациента  – общая сумма индивидуального счета (по расчету МО).
            ('NAPUCH',	'N',	7, 0	), #Код МО, направившей на госпитализацию (Приложение 2).
            ('NAPDAT',	'D'		), #Дата направления. 
            ('DS0', 	'C',	10	), #Диагноз первичный. Код из справочника МКБ до уровня подрубрики. Указывается при наличии.
            ('RSLT',	'N',	3, 0	), #Результат обращения. Заполняется в соотвествие с Классификатором V009.
            ('USL_OK',	'N',	2, 0	), #Условия оказания медицинской помощи. Заполняется в соответствие с классификатором V006.
            ('VIDPOM',	'N',	4, 0	), #Вид оказания медицинской помощи. Заполняется в соотвествие с Классификатором V008.
            ('EXTR',	'N',	2, 0	), #Направление (госпитализация) 1 –плановая; 2 – экстренная.
            ('PRVS', 	'N',	9	), #Специальность врача, закрывшего талон. Заполняется в соответствие с Классификатором V004.
            ('IDDOKT',	'C',	16	), #Код врача, закрывшего историю болезни. Заполняется из регионального справочника. До момента принятия регионального справочника медицинских работников значение поля равно 0(ноль).
            ('CNILSVR', 'C',	14	), #СНИЛС врача.
            ('ISHOD',	'N',	3, 0	), #Исход госпитализации. Заполняется в соотвествие с Классификатором V012.
            ('CODE_MO',	'C',	6	), #Реестровый номер МО лечения (Классификатор F003).
            ('OS_SLUCH','C',	4	), #Указываются все имевшиеся особые случаи. 0- нет особых случаев; 1- мед.помощь оказана новорожденному до государственной регистрации при многоплодных родах; 2- в документе, удостоверяющем личность пациента/представителя отсутствует отчество. При наличии нескольких случаев указываютя оба случая через «;». Возможные варианты заполнения: «0;», «1;», «2;», «1;2;», «2;1;».           
        )
        return dbf

    pacientFields = {
        'NREESTR'  : [True, u'Номер счета'],                                          
        'KODLPU'   : [True, u'Код МО и её подразделения'],
        'NSVOD'    : [True, u'Номер сводного счета, в который включена эта запись'],
        'KODP'     : [True, u'Код пациента соответствует коду в файле PACIENTS.DBF'],
        'FAMIP'    : [True, u'Фамилия пациента'],
        'NAMEP'    : [True, u'Имя пациента'],
        'OTCHP'    : [True, u'Отчество пациента'],
        'POLPA'    : [True, u'Пол пациента'],
        'DROGD'    : [True, u'Дата рождения пациента'],
        'ADRES'    : [True, u'Адрес: регистрация по месту жительства'],
        'KLADR'    : [False, u'Адрес регистрации по КЛАДР'],
        'DOM'      : [False, u'Дом'],
        'KVART'    : [False, u'Квартира'],
        'KORP'     : [False, u'Корпус'],
        'KTERR'    : [True, u'ОКАТО территории страхования'],
        'KODST'    : [False, u'Реестровый номер СМО'],
        'NSTRA'    : [False, u'Наименование страховой компании'],
        'SERIA'    : [False, u'Серия документа, подтверждающего факт страхования по ОМС'],
        'NPOLI'    : [False, u'Номер документа, подтверждающего факт страхования по ОМС'],
        'VIDDK'    : [False, u'Тип документа удостоверяющего личность'],
        'SERDK'    : [False, u'Серия документа, удостоверяющего личность'],
        'NOMDK'    : [True, u'Номер документа, удостоверяющего личность'],
        'CNILS'    : [False, u'Страховой номер индивидуального лицевого счета гражданина в пенсионном фонде РФ'],
        'SVERTKA'  : [True, u'Контрольная сумма реквизитов пациента'],
        'STAT_Z'   : [True, u'Статус пациента'],
        'Q_OGRN'   : [False, u'ОГРН СМО, выдавшей документ, подтверждающей факт страхования по ОМС'],
        'SMO_ID'   : [False, u'Код СМО'],
        'VPOLIS_ID': [False, u'Тип документа, подтверждающего факт страхования по ОМС'],
        'SPOLIS_ID': [False, u'Серия документа, подтверждающего факт страхования по ОМС'],
        'NPOLIS_ID': [False, u'Номер документа, подтверждающего факт страхования по ОМС'],
        'CODE_MO'  : [True, u'Реестровый номер МО'],
        'VPOLIS'   : [True, u'Тип документа, подтверждающего факт страхования по ОМС'],
        'NOVOR'    : [True, u'Указывается в случае оказания медицинской по-мощи ребёнку до государственной регистрации рожде-ния'],
        'MR'       : [False, u'Место рождения пациента'],
        'OKATOG'   : [False, u'Код места жительства'],
        'OKATOP'   : [False, u'Код места пребывания']
    }

    def createPACIENTPDbf(self, modern):
        u"""Создает структуру для паспортной части реестра счетов."""

        dbfName = os.path.join(self.parent.getTmpDir(), 'PACIENTP%s.DBF' % ('M' if modern else ''))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NREESTR',  'N', 5, 0  ),
            ('KODLPU',   'N', 7 , 0 ),
            ('NSVOD',    'N', 3 , 0 ),
            ('KODP',     'N', 10, 0 ),
            ('FAMIP',    'C', 40 ),
            ('NAMEP',    'C', 40 ),
            ('OTCHP',    'C', 40 ),
            ('POLPA',    'N', 1 , 0 ),
            ('DROGD',    'D'	 ),
            ('ADRES',    'C', 110),
            ('KLADR',    'C', 17 ),
            ('DOM',      'C', 10 ),
            ('KVART',    'C', 10 ),
            ('KORP',     'C', 10 ),
            ('KTERR',    'C', 5  ),
            ('KODST',    'C', 5  ),
            ('NSTRA',    'C', 100),
            ('SERIA',    'C', 10 ),
            ('NPOLI',    'C', 20 ),
            ('VIDDK',    'C', 2  ),
            ('SERDK',    'C', 10 ),
            ('NOMDK',    'C', 20 ),
            ('CNILS',    'C', 14 ),
            ('SVERTKA',  'C', 16 ),
            ('STAT_Z',   'N', 1 , 0 ),
            ('Q_OGRN',   'C', 15 ),
            ('SMO_ID',   'C', 5  ),
            ('VPOLIS_ID','N', 1, 0  ),
            ('SPOLIS_ID','C', 10 ),
            ('NPOLIS_ID','C', 20 ),
            ('CODE_MO',  'C', 6  ),
            ('VPOLIS',   'N', 1 , 0 ),
            ('NOVOR',    'C', 9  ),
            ('MR',       'C', 100),
            ('OKATOG',   'C', 11 ),
            ('OKATOP',   'C', 11 ),
        )
        return dbf


    def createUDbf(self, modern):
        u"""Создает структуру dbf для медицинских услуг."""

        dbfName = os.path.join(self.parent.getTmpDir(), 'U'+self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_MO', 'C', 5),  # код медицинской организации в системе ОМС,
                                        # предоставившей медицинскую помощь обязательное SPR01
            ('NS', 'N', 4, 0),   # номер реестра счетов (п. 1 примечаний) обязательное
            ('SN', 'N', 10, 0), # номер персонального счета обязательное
            ('KOTD', 'C', 4),   # символьное (4) код отделения (п. 2 примечаний) обязательное SPR07
            ('KPK', 'C', 2),     # код профиля койки (п. 2 примечаний) обязательное для стационаров SPR08
            ('MKBX', 'C',	 5),  # код диагноза основного заболевания по МКБ–Х (п. 2 примечаний)
                                        # обязательное для всех услуг, кроме диагностических SPR20
            ('MKBXS', 'C', 5), # код диагноза сопутствующего заболевания по МКБ–Х (п. 2 примечаний) SPR20
            ('KSTAND', 'C', 14), # код стандарта оказания медицинской помощи обязательное
                                            # для нозологий, у которых разработан СОМП SPR38
            ('VP', 'C', 3), # код условия оказания медицинской помощи (п. 2, 3 примечаний) обязательное SPR13
            ('KUSL', 'C', 14), # код медицинской услуги обязательное SPR18
            ('KOLU', 'N', 3, 0), # количество услуг обязательное
            ('KD', 'N', 3, 0), 	# количество койко-дней	обязательное  для стационаров
            ('DATN', 'D'), # дата начала выполнения услуги обязательное
            ('DATO', 'D'), # дата окончания выполнения услуги обязательное
            ('TARU', 'N', 12, 2), # Тариф (см.п.6 примечаний)	обязательное	SPR22
            ('TARU_B', 'N', 12, 2), # Базовая часть тарифа услуги по ОМС из справочника spr 22 поле TARU_B
            ('TARU_D', 'N', 12, 2), #тариф на оплату дополнительных статей расходов из справочника spr 22 поле TARIF_D
            ('TARU_M', 'N', 12, 2),
            ('SUMM', 'N', 14, 2), # сумма к оплате 	обязательное
            ('SUMM_B', 'N', 14, 2), #сумма по базовой части тарифа к оплате по ОМС поле SUMM _B
            ('SUMM_D', 'N', 14, 2), # сумма дополнительных статей расходов к оплате по ОМС
            ('SUMM_K', 'N', 14, 2), # сумма расходов на оплату коммунальных услуг (п. 9 примечаний)
            ('SUMM_M', 'N', 14, 2),
            ('IS_OUT', 'N', 1, 0), # признак: услуга оказана в другой медицинской организации (п. 4 примечаний) обязательное
            ('OUT_MO', 'C', 5), # код медицинской организации в системе ОМС, оказавшей услугу (п. 5 примечаний) SPR01
            ('DOC_TABN', 'C', 10), #табельный номер специалиста, оказавшего услугу
            ('SPEC', 'C', 3) # код специальности специалиста, оказавшего услугу
            )
        return dbf


    def createBDbf(self, modern):
        u"""Создает структуру dbf для листка временной нетрудоспособности."""

        if self.parent.isStacionar:
            dbfName = os.path.join(self.parent.getTmpDir(), 'K'+self.getDbfBaseName(modern))
        else:
            dbfName = os.path.join(self.parent.getTmpDir(), 'B'+self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        if self.parent.isStacionar:
            dbf.addField(
                ('CODE_MO', 'C', 5),  # код медицинской организации в системе ОМС, предоставившей медицинскую помощь
                ('NS', 'N', 4, 0), # номер реестра счетов обязательное
                ('SN', 'N', 10, 0), # номер персонального счета обязательное
                ('KSTAND', 'C', 14), # Код стандарта МП, при оказании которого пациент лежал в сопутствующем отделении (стандарт по программе Модернизации)
                ('KOTD', 'C', 3), # Код отделения
                ('KPK', 'C', 2), # Код профиля койки
                ('KUSL', 'C',  14),  # Код койко-дня
                ('DATN', 'D'), # дата выписки б.листа обязательное
                ('DATO', 'D'), # дата закрытия б.листа обязательное
                ('KOLU', 'N', 10, 0), # Кол-во услуг
                ('KD',  'N', 10, 0), # Кол-во койко-дней
            )
        else:
            dbf.addField(
                ('CODE_MO', 'C', 5),  # код медицинской организации в системе ОМС,
                                                # предоставившей медицинскую помощь обязательное SPR01
                ('NS', 'N', 4, 0), # номер реестра счетов обязательное
                ('SN', 'N', 10, 0), # номер персонального счета обязательное
                ('BLS', 'C', 10), # серия листка нетрудоспособности	обязательное
                ('BLN', 'N', 7, 0), # номер листка нетрудоспособности обязательное
                ('KPBL', 'N', 2, 0), # причина нетрудоспособности обязательное SPR27
                ('DATN', 'D'), # дата выписки б.листа обязательное
                ('DATO', 'D'), # дата закрытия б.листа обязательное
                ('MKBX', 'C', 5), # код диагноза по МКБ–Х SPR20
            )

        return dbf


    def createDDbf(self, modern):
        u"""Специалисты структурного подразделения"""
        dbfName = os.path.join(self.parent.getTmpDir(), 'D'+self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_MO', 'C', 5), # код медицинской организации в системе ОМС, предоставившей медицинскую помощь
            ('DOC_TABN', 'C', 10), #табельный номер специалиста (врача)
            ('FIO', 'C', 40), #фамилия специалиста (врача)
            ('IMA', 'C', 40), #имя специалиста (врача)
            ('OTCH', 'C', 40), # отчество специалиста (врача)
            ('POL', 'C', 1), # пол (М/Ж)
            ('DATR', 'D'),  # дата рождения
            ('DATN', 'D'),  # дата устройства на работу
            ('DATO', 'D'),  # дата увольнения
        )
        return dbf


    def createSDbf(self, modern):
        dbfName = os.path.join(self.parent.getTmpDir(), 'S'+self.getDbfBaseName(modern))
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('CODE_MO', 'C', 5), #код медицинской организации в системе ОМС, предоставившей мед. помощь
            ('DOC_TABN', 'C', 10), #табельный номер врача
            ('SPEC', 'C', 3), #специальность врача
            ('KOTD', 'C', 4),  #код отделения
            ('DOLG', 'C', 4),  #занимаемая должность
            ('DATN', 'D'),  #дата начала работы в  должности
            ('DATO', 'D'),  #дата окончания работы в должности
        )
        return dbf


    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = u"""SELECT
              if(ClientPolicy.insurer_id is not NULL, Insurer.shortName, ClientPolicy.name) AS NSTRA,
              Account_Item.id        AS accountItem_id,
              Account_Item.master_id AS account_id,
              Account_Item.event_id  AS event_id,
              Account_Item.action_id AS action_id,
              Account.number AS accNumber,
              Event.client_id        AS client_id,
              Event.littleStranger_id     AS littleStrangerId,
              Event.`order`          AS `order`,
              Event.setDate          AS begDate,
              Event.execDate         AS endDate,
              Event.MES_id AS mesId,
			  Event.externalId       AS externalId,
              Client.lastName        AS lastName,
              Client.firstName       AS firstName,
              Client.patrName        AS patrName,
              Client.birthDate       AS birthDate,
              Client.birthPlace      AS birthPlace,
              Client.sex             AS sex,
              age(Client.birthDate, Event.execDate) as clientAge,
              Client.SNILS           AS SNILS,
              ClientPolicy.serial    AS policySerial,
              ClientPolicy.number    AS policyNumber,
              ClientPolicy.note AS policyNote,
              ClientPolicy.begDate AS policyBegDate,
              ClientPolicy.endDate AS policyEndDate,
              ClientPolicy.insuranceArea AS area,
              Insurer.infisCode    AS policyInsurer,
              Insurer.INN          AS insurerINN,
              Insurer.shortName    AS insurerName,
              Insurer.OKATO AS insurerOKATO,
              Insurer.OGRN  AS insurerOGRN,
              Insurer.area  AS insurerArea,
              Insurer.id    AS insurerId,
              rbPolicyType.code      AS policyType,
              rbPolicyKind.regionalCode AS policyKindCode,
              ClientDocument.serial  AS documentSerial,
              ClientDocument.number  AS documentNumber,
              rbDocumentType.code    AS documentType,
              rbDocumentType.regionalCode AS documentRegionalCode,
              rbMedicalAidUnit.federalCode AS medicalAidUnitFederalCode,
              rbDiseaseCharacter.code AS PRZAB,
              RegSOCR.infisCode AS placeCode,
              RegKLADR.NAME AS cityName,
              RegSTREETSOCR.infisCode AS streetType,
              RegKLADRStreet.NAME AS streetName,
              RegKLADRStreet.CODE AS streetCODE,
              RegAddressHouse.number AS regNumber,
              RegAddressHouse.corpus AS regCorpus,
              RegAddress.flat AS regFlat,
              RegAddressHouse.KLADRCode AS regKLADRCode,
              RegRegionKLADR.OCATD AS regionOKATO,
              RegRegionKLADR.NAME AS regionName,
              Referral.date  AS refDate,
              Event.referral_id    AS refId,
              Referral.relegateOrg_id AS refOrgId,
              IF(work.title IS NOT NULL,
                  work.title, ClientWork.freeInput) AS `workName`,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.code,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.code, rbEventService.code)
                ) AS service,
              IF(Account_Item.service_id IS NOT NULL,
                Account_Item.service_id,
                IF(Account_Item.visit_id IS NOT NULL, Account_Item.visit_id,
                    IF(Account_Item.action_id IS NOT NULL, Account_Item.action_id, Event.id)
                )) AS cardId,
              IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.federalCode,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.federalCode, EventMedicalAidProfile.regionalCode)
                  ) AS medicalAidProfileFederalCode,
              IF(Account_Item.visit_id IS NOT NULL, Visit.person_id,
                    IF(Account_Item.action_id IS NOT NULL,
                            IF(Action.person_id IS NOT NULL, Action.person_id, Action.setPerson_id), Event.execPerson_id)
                ) AS execPersonId,
              Visit.date AS visitDate,
              if(Visit.MKB is not null, Visit.MKB, Diagnosis.MKB) AS VISIT_MKB,
              Action.begDate AS actionDate,
              Action.begDate AS DATE_IN, #setDate
              Action.endDate AS DATE_OUT,
              Diagnosis.MKB          AS MKB,
              Diagnosis.MKBEx        AS MKBEx,
              AssociatedDiagnosis.MKB AS AssociatedMKB,
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
              rbSpeciality.regionalCode AS specialityCode,
              rbSpeciality.federalCode AS federalCode,              
              EventType.code AS eventTypeCode,
              DiagnosticResult.regionalCode AS diagnosticResultCode,
              EventResult.regionalCode AS eventResultCode,
              EventResult.federalCode AS eventResultFederalCode,
              OrgStructure.infisCode AS orgStructCode,
              RelegateOrg.infisCode AS RelegateOrgCode,
              Action.note AS actNote,
              Action.directionDate AS actSetDate,
              rbEventProfile.code AS eventProfileCode,
              SocStatus.regionalCode AS socStatusCode,
              rbMedicalAidType.code AS medicalAidTypeCode,
              rbMedicalAidType.federalCode AS medicalAidTypeFederalCode,
              rbMedicalAidKind.federalCode AS medicalAidKindFederalCode,
              DiagnosticResult.federalCode AS resultFederalCode,
              ZPLExpense.percent AS ZPLPercent,
              MEDExpense.percent AS MEDPercent,
              INVExpense.percent AS IVNVPercent,
              KOSExpense.percent AS KOSPercent,
              NAKLExpense.percent AS NAKLPercent,              
              DOPLExpense.percent AS DOPLPercent,
              Contract.regionalTariffRegulationFactor AS regulator
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN Referral ON Event.referral_id = Referral.id
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
            LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id AND
                      ClientRegAddress.id = (SELECT MAX(CRA.id)
                                         FROM   ClientAddress AS CRA
                                         WHERE  CRA.type = 0 AND CRA.client_id = Client.id AND CRA.deleted=0)
            LEFT JOIN Address   RegAddress ON RegAddress.id = ClientRegAddress.address_id
            LEFT JOIN AddressHouse RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
            LEFT JOIN kladr.KLADR AS RegKLADR ON RegKLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN kladr.STREET AS RegKLADRStreet ON RegKLADRStreet.CODE = RegAddressHouse.KLADRStreetCode
            LEFT JOIN kladr.SOCRBASE AS RegSTREETSOCR ON RegSTREETSOCR.KOD_T_ST = (SELECT KOD_T_ST
                        FROM kladr.SOCRBASE AS SB
                        WHERE SB.SCNAME = RegKLADRStreet.SOCR
                        LIMIT 1)
            LEFT JOIN kladr.SOCRBASE AS RegSOCR ON RegSOCR.KOD_T_ST = (SELECT KOD_T_ST
                        FROM kladr.SOCRBASE AS SB
                        WHERE SB.SCNAME = RegKLADR.SOCR
                        LIMIT 1)
            LEFT JOIN kladr.KLADR RegRegionKLADR ON RegRegionKLADR.CODE = (
                    SELECT RPAD(LEFT(RegAddressHouse.KLADRCode,2),13,'0') LIMIT 1)
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN Person AS setEventPerson ON setEventPerson.id = Event.setPerson_id
            LEFT JOIN Person AS setActionPerson ON setActionPerson.id = Action.setPerson_id
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                      AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1', '2'))
                                      AND Diagnostic.deleted = 0)
            LEFT JOIN Diagnostic AS AssociatedDiagnostic ON (
                AssociatedDiagnostic.event_id = Account_Item.event_id
                AND AssociatedDiagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='9')
                AND AssociatedDiagnostic.deleted = 0)
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
            LEFT JOIN rbDiseaseCharacter ON Diagnosis.character_id = rbDiseaseCharacter.id
            LEFT JOIN Diagnosis AS AssociatedDiagnosis ON AssociatedDiagnosis.id = AssociatedDiagnostic.diagnosis_id
                            AND AssociatedDiagnosis.deleted = 0
            LEFT JOIN rbDiagnosticResult AS DiagnosticResult ON DiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN Organisation AS RelegateOrg ON Event.relegateOrg_id = RelegateOrg.id
            LEFT JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id =rbMedicalAidType.id
            LEFT JOIN rbMedicalAidKind ON EventType.medicalAidKind_id = rbMedicalAidKind.id
            LEFT JOIN rbEventProfile AS EventMedicalAidProfile ON
                EventType.eventProfile_id = EventMedicalAidProfile.id
            LEFT JOIN rbMedicalAidProfile AS VisitMedicalAidProfile ON
                VisitMedicalAidProfile.id = rbVisitService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON
                ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
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
            LEFT JOIN Contract_CompositionExpense AS ZPLExpense ON  ZPLExpense.id IN (
                SELECT MAX(CCE.id)
                FROM Contract_CompositionExpense AS CCE
                LEFT JOIN rbExpenseServiceItem ON CCE.rbTable_id = rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '1' AND CCE.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS MEDExpense ON  MEDExpense.id = (
                SELECT MAX(CCE2.id)
                FROM Contract_CompositionExpense AS CCE2
                LEFT JOIN rbExpenseServiceItem ON CCE2.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '2' AND CCE2.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS INVExpense ON  INVExpense.id = (
                SELECT MAX(CCE3.id)
                FROM Contract_CompositionExpense AS CCE3
                LEFT JOIN rbExpenseServiceItem ON CCE3.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '3' AND CCE3.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS KOSExpense ON  KOSExpense.id = (
                SELECT MAX(CCE4.id)
                FROM Contract_CompositionExpense AS CCE4
                LEFT JOIN rbExpenseServiceItem ON CCE4.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '4' AND CCE4.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS NAKLExpense ON  NAKLExpense.id = (
                SELECT MAX(CCE5.id)
                FROM Contract_CompositionExpense AS CCE5
                LEFT JOIN rbExpenseServiceItem ON CCE5.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '5' AND CCE5.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS DOPLExpense ON  DOPLExpense.id = (
                SELECT MAX(CCE6.id)
                FROM Contract_CompositionExpense AS CCE6
                LEFT JOIN rbExpenseServiceItem ON CCE6.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '6' AND CCE6.master_id = Contract_Tariff.id
            )
            LEFT JOIN rbSocStatusType AS SocStatus ON
                ClientSocStatus.socStatusType_id = SocStatus.id
            LEFT JOIN Account ON Account_Item.master_id = Account.id
            LEFT JOIN Contract ON Account.contract_id = Contract.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            ORDER BY insurerId, lastName
        """ % tableAccountItem['id'].inlist(self.idList)
        return db.query(stmt)

# *****************************************************************************************

    def createPersonQuery(self):
        db = QtGui.qApp.db
        table = db.table('Person')
        orgStructId = QtGui.qApp.currentOrgStructureId()
        cond = table['orgStructure_id'].eq(orgStructId) if orgStructId\
            else table['org_id'].eq(QtGui.qApp.currentOrgId())

        stmt = """SELECT
            lastName, firstName, patrName, Person.sex, birthDate,
            Person.code AS tabNum,
            OrgStructure.infisCode AS orgStructCode,
            rbPost.regionalCode AS postCode,
            rbSpeciality.regionalCode AS specialityCode
        FROM Person
        LEFT JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
        LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
        LEFT JOIN rbPost ON Person.post_id = rbPost.id
        WHERE %s AND LEFT(rbPost.code,1) IN ('1','2','3')
        """ % cond
        return db.query(stmt)

# *****************************************************************************************

    def getClientInfo(self):
        u"""возвращает общую стоимость услуг за пациента"""

        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """SELECT Event.client_id, SUM(sum) AS totalSum,
            MIN(Event.setDate) AS begDate,
            MAX(Event.execDate) AS endDate,
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
        GROUP BY client_id;
        """ % tableAccountItem['id'].inlist(self.idList)
        query = db.query(stmt)

        result = {}
        while query.next():
            record  = query.record()
            id = forceRef(record.value(0))
            result[id] = (forceDouble(record.value(1)),
                                forceDate(record.value(2)),
                                forceDate(record.value(3)),
                              forceDouble(record.value(4)))
        return result

# *****************************************************************************************

    def getAdrRecord(self, clientId, adrType):
        db = QtGui.qApp.db
        stmt = '''
            SELECT
                kladr.STREET.NAME AS streetName, kladr.STREET.SOCR AS streetType,
                AddressHouse.number AS number, AddressHouse.corpus AS corpus, AddressHouse.KLADRCode,
                Address.flat AS flat, Address.id AS addressId, ClientAddress.freeInput AS freeInput, kladr.KLADR.OCATD AS okato
            FROM ClientAddress
            LEFT JOIN Address ON Address.id = ClientAddress.address_id
            LEFT JOIN AddressHouse ON AddressHouse.id = Address.house_id
            LEFT JOIN kladr.STREET ON kladr.STREET.CODE = AddressHouse.KLADRStreetCode
            LEFT JOIN kladr.KLADR ON kladr.KLADR.CODE = AddressHouse.KLADRCode
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

    def getSpecialityOKSOCode(self, personId):
        u"""Определяем федеральный код специальности врача по его id"""
        result = self._specialityOKSOCodeCache.get(personId, -1)

        if result == -1:
            result = None
            specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))

            if specialityId:
                result = forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'code'))

            self._specialityOKSOCodeCache[personId] =result

        return result


    def hash(self, f ,n ,o, d):
        st1 = st2 = u''
        encoding = 'cp866'
        st = u'%s %s %s %d.%d.%d' % (f, n, o, d.day, d.month, d.year)
        st = st.upper()
        for i in xrange(len(st)):
            if i % 2 == 0:
                st2 += st[i]
            else:
                st1 += st[i]
        return ('%08x%08x' % (zlib.crc32(st1.encode(encoding)) & 0xffffffff, zlib.crc32(st2.encode(encoding)) & 0xffffffff)).upper()

    def getEventData(self):
        db = QtGui.qApp.db

        tableAccountItem = db.table('Account_Item')

        stmt = u"""SELECT
              Account_Item.event_id AS id,
              SUM(Account_Item.price)   AS price,
              SUM(Contract_Tariff.federalPrice) AS federalPrice,
              SUM(ZPLExpense.percent) AS ZPLPercent,
              SUM(MEDExpense.percent) AS MEDPercent,
              SUM(INVExpense.percent) AS IVNVPercent,
              SUM(KOSExpense.percent) AS KOSPercent,
              SUM(NAKLExpense.percent) AS NAKLPercent,
              SUM(DOPLExpense.percent) AS DOPLPercent
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN Referral ON Event.referral_id = Referral.id
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
            LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id AND
                      ClientRegAddress.id = (SELECT MAX(CRA.id)
                                         FROM   ClientAddress AS CRA
                                         WHERE  CRA.type = 0 AND CRA.client_id = Client.id AND CRA.deleted=0)
            LEFT JOIN Address   RegAddress ON RegAddress.id = ClientRegAddress.address_id
            LEFT JOIN AddressHouse RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
            LEFT JOIN kladr.KLADR AS RegKLADR ON RegKLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN kladr.STREET AS RegKLADRStreet ON RegKLADRStreet.CODE = RegAddressHouse.KLADRStreetCode
            LEFT JOIN kladr.SOCRBASE AS RegSTREETSOCR ON RegSTREETSOCR.KOD_T_ST = (SELECT KOD_T_ST
                        FROM kladr.SOCRBASE AS SB
                        WHERE SB.SCNAME = RegKLADRStreet.SOCR
                        LIMIT 1)
            LEFT JOIN kladr.SOCRBASE AS RegSOCR ON RegSOCR.KOD_T_ST = (SELECT KOD_T_ST
                        FROM kladr.SOCRBASE AS SB
                        WHERE SB.SCNAME = RegKLADR.SOCR
                        LIMIT 1)
            LEFT JOIN kladr.KLADR RegRegionKLADR ON RegRegionKLADR.CODE = (
                    SELECT RPAD(LEFT(RegAddressHouse.KLADRCode,2),13,'0') LIMIT 1)
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN Person AS setEventPerson ON setEventPerson.id = Event.setPerson_id
            LEFT JOIN Person AS setActionPerson ON setActionPerson.id = Action.setPerson_id
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                      AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1', '2'))
                                      AND Diagnostic.deleted = 0)
            LEFT JOIN Diagnostic AS AssociatedDiagnostic ON (
                AssociatedDiagnostic.event_id = Account_Item.event_id
                AND AssociatedDiagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='9')
                AND AssociatedDiagnostic.deleted = 0)
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
            LEFT JOIN rbDiseaseCharacter ON Diagnosis.character_id = rbDiseaseCharacter.id
            LEFT JOIN Diagnosis AS AssociatedDiagnosis ON AssociatedDiagnosis.id = AssociatedDiagnostic.diagnosis_id
                            AND AssociatedDiagnosis.deleted = 0
            LEFT JOIN rbDiagnosticResult AS DiagnosticResult ON DiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN Organisation AS RelegateOrg ON Event.relegateOrg_id = RelegateOrg.id
            LEFT JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id =rbMedicalAidType.id
            LEFT JOIN rbMedicalAidKind ON EventType.medicalAidKind_id = rbMedicalAidKind.id
            LEFT JOIN rbEventProfile AS EventMedicalAidProfile ON
                EventType.eventProfile_id = EventMedicalAidProfile.id
            LEFT JOIN rbMedicalAidProfile AS VisitMedicalAidProfile ON
                VisitMedicalAidProfile.id = rbVisitService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON
                ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
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
            LEFT JOIN Contract_CompositionExpense AS ZPLExpense ON  ZPLExpense.id = (
                SELECT MAX(CCE.id)
                FROM Contract_CompositionExpense AS CCE
                LEFT JOIN rbExpenseServiceItem ON CCE.rbTable_id = rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '1' AND CCE.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS MEDExpense ON  MEDExpense.id = (
                SELECT MAX(CCE2.id)
                FROM Contract_CompositionExpense AS CCE2
                LEFT JOIN rbExpenseServiceItem ON CCE2.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '2' AND CCE2.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS INVExpense ON  INVExpense.id = (
                SELECT MAX(CCE3.id)
                FROM Contract_CompositionExpense AS CCE3
                LEFT JOIN rbExpenseServiceItem ON CCE3.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '3' AND CCE3.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS KOSExpense ON  KOSExpense.id = (
                SELECT MAX(CCE4.id)
                FROM Contract_CompositionExpense AS CCE4
                LEFT JOIN rbExpenseServiceItem ON CCE4.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '4' AND CCE4.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS NAKLExpense ON  NAKLExpense.id = (
                SELECT MAX(CCE5.id)
                FROM Contract_CompositionExpense AS CCE5
                LEFT JOIN rbExpenseServiceItem ON CCE5.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '5' AND CCE5.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS DOPLExpense ON  DOPLExpense.id = (
                SELECT MAX(CCE6.id)
                FROM Contract_CompositionExpense AS CCE6
                LEFT JOIN rbExpenseServiceItem ON CCE6.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '6' AND CCE6.master_id = Contract_Tariff.id
            )
            LEFT JOIN rbSocStatusType AS SocStatus ON
                ClientSocStatus.socStatusType_id = SocStatus.id
            LEFT JOIN Account ON Account_Item.master_id = Account.id
            LEFT JOIN Contract ON Account.contract_id = Contract.id
            WHERE Account_Item.deleted = 0 and Event.deleted = 0 and %s AND 
            Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            GROUP BY Account_Item.event_id;
        """ % (tableAccountItem['id'].inlist(self.idList))

        query = db.query(stmt)
        while query.next():
            rec = query.record()
            id = forceInt(rec.value('id'))
            zpl = forceDouble(rec.value('ZPLPercent'))
            med = forceDouble(rec.value('MEDPercent'))
            m_inv = forceDouble(rec.value('IVNVPercent'))
            kos = forceDouble(rec.value('KOSPercent'))
            nakl = forceDouble(rec.value('NAKLPercent'))
            dopl = forceDouble(rec.value('DOPLPercent'))
            price = forceDouble(rec.value('price'))
            fedprice = forceDouble(rec.value('federalPrice'))

            self.eventData[id] = (zpl, med, m_inv, kos, nakl, dopl, price, fedprice)


    def dbfRecordToUpper(self, dbfRecord):
        dbf = dbfRecord.dbf
        stringFieldNames = []
        for fieldName in dbf.fieldNames:
            index = dbf.header.mapNameToIndex[fieldName] if dbf.header.mapNameToIndex.has_key(fieldName) else None
            if index and dbf.fieldDefs[index].typeCode == 'C':
                stringFieldNames.append(fieldName)
        for fieldName in stringFieldNames:
            dbfRecord[fieldName] = forceString(dbfRecord[fieldName]).upper()
        return dbfRecord


    def process(self, dbf, record, codeLPU, accNumber, exposeDate, payType, accType, payerOGRN, accDate):
        birthDate = forceDate(record.value('birthDate'))
        birthPyDate = pyDate(birthDate)
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        # Номер стат.талона
        clientId = forceRef(record.value('client_id'))
        accNumberString = forceString(record.value('accNumber'))
        number = forceString(record.value('regNumber'))
        corpus = forceString(record.value('regCorpus'))
        flat = forceString(record.value('regFlat'))
        modern = clientId in self.modernClients
        miacCode = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))

        infisCode = forceInt(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))

        prvs = forceInt(self.getSpecialityOKSOCode(forceRef(record.value('execPersonId'))))

        kspec = forceLong(record.value('service'))
        podr = forceInt(forceString(kspec)[:4])
        #forceInt(forceString(self.getSpecialityFederalCode(forceRef(record.value('execPersonId'))))[:4])        
      
        iddokt = forceString(self.getPersonFederalCode(forceRef(record.value('execPersonId'))))

        age = forceInt(record.value('clientAge'))
        patrName = forceString(record.value('patrName'))

        nsvod =  300 + pyDate(accDate).month #forceInt(forceString(record.value('account_id'))[-3:])

        kodstr = forceString(QtGui.qApp.db.translate('Organisation', 'id', record.value('insurerId'), 'infisCode'))
        nreestr = forceInt(u'%s%02d1' % ((kodstr[-1:] if kodstr[-2:-1] == '0' else kodstr[-2:]) if kodstr and kodstr[:2] == u'61' else u'10', pyDate(accDate.addMonths(1) if accNumberString and accNumberString.lower()[-1] == u'п' else accDate).month)) #forceInt(record.value('account_id'))
        nschet = forceInt(record.value('event_id')) #forceInt(record.value('accountItem_id'))
        famip = forceString(record.value('lastName'))

        client = u'%s %s %s, дата рождения: %s' % (famip, forceString(record.value('firstName')), patrName, forceString(birthDate))

        #TODO: create DBFs
        if modern:
            (dbfPacientP, dbfTalon, dbfTalon1, dbfPoslpr,  dbfUslugiP) = dbf[:5]
        else:
            (dbfPacientP, dbfTalon, dbfTalon1, dbfPoslpr,  dbfUslugiP) = dbf[:5]

        patrSluch = False
        if not patrName or patrName == u'' or patrName.upper() == u'НЕТ':
            patrSluch = True

        if not ((clientId, modern) in self.exportedClients):
            dbfRecord = dbfPacientP.newRecord()

            dbfRecord['NREESTR'] = nreestr
                      
            dbfRecord['KODST']  = kodstr if kodstr[:2] == u'61' else u''      
            
            dbfRecord['KODLPU'] =  infisCode

            dbfRecord['NSVOD'] =   nsvod

            dbfRecord['KODP'] =    clientId            

            longAddress = None
            adrRegRecord  = self.getAdrRecord(clientId, 0)
            adrFactRecord = self.getAdrRecord(clientId, 1)
            adrRecord = adrRegRecord
            if not adrRecord:
                adrRecord = adrFactRecord
            if adrRecord:                
                addressId = forceInt(adrRecord.value('addressId'))
                longAddress = formatAddress(addressId, adrRecord.value('freeInput'))

            dbfRecord['FAMIP'] =   nameCase(famip)

            dbfRecord['NAMEP'] =   nameCase(forceString(record.value('firstName')))

            dbfRecord['OTCHP'] =   nameCase(patrName) if not patrSluch else u'НЕТ'

            sex = forceInt(record.value('sex'))

            dbfRecord['POLPA'] =  sex

            dbfRecord['DROGD'] =  birthPyDate

            dbfRecord['MR']     =  forceString(record.value('birthPlace'))

            dbfRecord['OKATOG'] = forceString(adrRegRecord.value('okato')) if adrRegRecord else u''

            dbfRecord['OKATOP'] = forceString(adrFactRecord.value('okato')) if adrFactRecord else u''

            dbfRecord['ADRES'] = longAddress if longAddress else u''
            
            dbfRecord['KLADR'] = forceString(record.value('streetCODE'))
            
            dbfRecord['SVERTKA'] = self.hash(dbfRecord['FAMIP'], dbfRecord['NAMEP'], dbfRecord['OTCHP'], pyDate(birthDate))
            
            dbfRecord['DOM'] = number
            
            dbfRecord['KORP'] = corpus
            
            dbfRecord['KVART'] = flat

            #dbfRecord['KTERR'] = forceString(record.value('insurerOKATO'))[:5]

            kterr = forceString(QtGui.qApp.db.translate('kladr.KLADR', 'CODE', forceString(record.value('area')), 'OCATD', idFieldName='CODE'))[:5]
            kterrres = u''
            if kterr != u'':
                kterrres =  kterr if kodstr[:2] == u'61' else u'%s000' % kterr[:2]
            #else:
            #    kterrres = forceString(record.value('KTERR'))

            if kterrres == u'60000':
                kterrres = u'60401'

            dbfRecord['KTERR'] = kterrres            
          
            dbfRecord['NSTRA'] = forceString(record.value('NSTRA')) if kodstr[:2] != u'61' else u''

            dbfRecord['SERIA'] = forceString(record.value('policySerial')) #splitDocSerial

            dbfRecord['NPOLI'] = forceString(record.value('policyNumber'))

            dbfRecord['VIDDK'] = forceInt(record.value('documentRegionalCode')) % 100

            #JANUARY accounts huck
            if dbfRecord['VIDDK'] == 0 or not dbfRecord['VIDDK']:
                dbfRecord['VIDDK'] = 14
            #####################

            dbfRecord['SERDK'] = forceString(record.value('documentSerial'))    #splitDocSerial

            dbfRecord['NOMDK'] = forceString(record.value('documentNumber'))

            dbfRecord['CNILS'] = formatSNILS(forceString(record.value('SNILS')))

            dbfRecord['VPOLIS'] = forceInt(forceString(record.value('policyKindCode'))[-1:]) if forceInt(record.value('policyKindCode')) else 0

            #JANUARY accounts huck
            if dbfRecord['VPOLIS'] == 0 or not dbfRecord['VPOLIS']:
                dbfRecord['VPOLIS'] = 1
            ######################

            dbfRecord['CODE_MO'] = miacCode

            childNum = 0 #TODO child number from DB
            novor = '0'
            if childNum:
                novor = '%d%02d%02d%02d%d' % (sex,  birthPyDate.day, birthPyDate.month, birthPyDate.year, childNum)
            dbfRecord['NOVOR']   = novor

            (socClassIdList, socTypeList) = self.getClientSocStatus(clientId, endDate)

            if 2 in socClassIdList:
                i = 0
                for classId in socClassIdList:
                    if classId == 2:
                        break;
                    i+=1                   

                if i < len(socTypeList):
                    socType = forceInt(socTypeList[i])
                    dbfRecord['STAT_Z'] = socType if socType < 9 else 8
                else:
                    self.log(u'Невозможно определить STAT_Z')
            else:
                workOrgName = forceString(record.value('workName'))
                if workOrgName:
                    dbfRecord['STAT_Z'] = 5
                else:
                    dbfRecord['STAT_Z'] = 7

            dbfRecord['Q_OGRN'] = forceString(record.value('insurerOGRN')) if kodstr[:2] != u'61' else u''


            for name in self.pacientFields.keys():
                if self.pacientFields[name][0] and not dbfRecord[name]:
                    self.log(u'обязательное поле %s(%s) не заполнено, файл PACIENTP.DBF, пациент %s' % (name, self.pacientFields[name][1], client))

            if kodstr[:2] != u'61' and not dbfRecord['NSTRA']:
                self.log(u'обязательное поле NSTRA(%s) не заполнено, файл PACIENTP.DBF, пациент %s' % (self.pacientFields['NSTRA'][1], client))

            if kodstr[:2] != u'61' and not dbfRecord['Q_OGRN']:
                self.log(u'обязательное поле Q_OGRN(%s) не заполнено, файл PACIENTP.DBF, пациент %s' % (self.pacientFields['Q_OGRN'][1], client))

            dbfRecord = self.dbfRecordToUpper(dbfRecord)
            dbfRecord.store()

            self.exportedClients.add((clientId, modern))

        #TALON file

        evid = forceInt(record.value('event_id'))

        price = forceDouble(record.value('price'))

        #TODO: standalone query and function for TALON file to remove logic with big events buffer
        if not evid in self.processedEvents:

            self.processedEvents.append(evid)
        
            dbfRecord = dbfTalon.newRecord()
        
            dbfRecord['NREESTR'] = nreestr
        
            dbfRecord['KODLPU']  = infisCode
        
            dbfRecord['NSCHT']   =  nschet
        
            dbfRecord['NSVOD']   = nsvod
        
            dbfRecord['KODP']    = clientId        
        
            dbfRecord['NIBLZ']   = forceString(record.value('event_id')) #externalId
        
            dbfRecord['DATAS']   = pyDate(endDate)
        
            dbfRecord['PRZAB']   = forceInt(record.value('PRZAB'))
        
            dbfRecord['SHDZO']   = forceString(record.value('MKB'))
        
            dbfRecord['SHDZS']   = forceString(record.value('AssociatedMKB'))
        
            dbfRecord['ABZAC']   = 1 if endDate else 0
        
            (zpl, med, m_inv, kos, nakl, dopl, pr, fedpr) = self.eventData[evid]
        
            dbfRecord['ZPL']            =  price * zpl / 100.
            
            dbfRecord['MED']            =  price * med / 100. #price * forceDouble(record.value('MEDPercent'))/100.

            dbfRecord['M_INV']          =  price * m_inv / 100. #price * forceDouble(record.value('INVPercent'))/100.
        
            dbfRecord['KOS']            =  price * kos / 100. #price * forceDouble(record.value('KOSPercent'))/100.
 
            dbfRecord['NAKL']           =  price * nakl / 100. #price * forceDouble(record.value('KOSPercent'))/100.

            dbfRecord['DOPL']           =  price * dopl / 100. #price * forceDouble(record.value('KOSPercent'))/100.            
        
            dbfRecord['STOIM']          =  pr + fedpr #forceDouble(record.value('sum'))
        
            refOrgId = forceInt(record.value('refOrgId'))
            if refOrgId:
                nap = forceInt(QtGui.qApp.db.translate('Organisation', 'id', refOrgId, 'infisCode'))
                if nap:
                    dbfRecord['NAPUCH']         =  nap

            dbfRecord['NAPDAT']         =  pyDate(forceDate(record.value('refDate')))

            if not forceInt(record.value('refId')):
                dbfRecord['NAPUCH'] = 0
                dbfRecord['NAPDAT'] = pyDate(begDate) - datetime.timedelta(days=1)
        
            dbfRecord['DS0']            =  forceString(record.value('MKBEx'))
        
            dbfRecord['RSLT']           =  forceInt(record.value('eventResultFederalCode'))
        
            dbfRecord['USL_OK']         =  forceInt(record.value('medicalAidTypeFederalCode'))
        
            dbfRecord['VIDPOM']         =  forceInt(record.value('medicalAidKindFederalCode'))
        
            dbfRecord['EXTR']           =  2 if forceInt(record.value('order')) == 2 else 1
        
            dbfRecord['PRVS']           =  prvs
        
            dbfRecord['IDDOKT']         =  0 #iddokt
        
            dbfRecord['CNILSVR']        =  formatSNILS(forceString(QtGui.qApp.db.translate('Person', 'id', record.value('execPersonId'), 'SNILS')))
        
            dbfRecord['ISHOD']          =  forceInt(record.value('resultFederalCode'))
        
            dbfRecord['CODE_MO']        =  miacCode

            os_sluch = ''

            if forceRef(record.value('littleStrangerId')):
                os_sluch += '1;'

            if patrSluch:
                os_sluch += '2;'          
        
            dbfRecord['OS_SLUCH']       =  os_sluch if os_sluch != '' else '0;'

            for name in self.talonFields.keys():
                if self.talonFields[name][0] and not dbfRecord[name]:
                    self.log(u'обязательное поле %s(%s) не заполнено, файл TALON.DBF, пациент %s' % (name, self.talonFields[name][1], client))
            dbfRecord = self.dbfRecordToUpper(dbfRecord)
            dbfRecord.store()

            
            dbfRecord = dbfTalon1.newRecord()

            dbfRecord['NREESTR'] = nreestr
        
            dbfRecord['KODLPU']  = infisCode
        
            dbfRecord['NSCHT']   =  nschet
        
            dbfRecord['NSVOD']   = nsvod
        
            dbfRecord['KODP']    = clientId        
        
            dbfRecord['NIBLZ']   = forceString(record.value('event_id')) #externalId
        
            dbfRecord['DATAS']   = pyDate(endDate)
        
            dbfRecord['PRZAB']   = forceInt(record.value('PRZAB'))
        
            dbfRecord['SHDZO']   = forceString(record.value('MKB'))
        
            dbfRecord['SHDZS']   = forceString(record.value('AssociatedMKB'))
        
            dbfRecord['ABZAC']   = 1 if endDate else 0
              
            dbfRecord['ZPL']            =  price * zpl / 100.
            
            dbfRecord['MED']            =  price * med / 100. #price * forceDouble(record.value('MEDPercent'))/100.

            dbfRecord['M_INV']          =  price * m_inv / 100. #price * forceDouble(record.value('INVPercent'))/100.
        
            dbfRecord['KOS']            =  price * kos / 100. #price * forceDouble(record.value('KOSPercent'))/100.
 
            dbfRecord['NAKL']           =  price * nakl / 100. #price * forceDouble(record.value('KOSPercent'))/100.

            dbfRecord['DOPL']           =  price * dopl / 100. #price * forceDouble(record.value('KOSPercent'))/100.            
        
            dbfRecord['STOIM']          =  pr + fedpr #forceDouble(record.value('sum'))
        
            refOrgId = forceInt(record.value('refOrgId'))
            if refOrgId:
                nap = forceInt(QtGui.qApp.db.translate('Organisation', 'id', refOrgId, 'infisCode'))
                if nap:
                    dbfRecord['NAPUCH']         =  nap

            dbfRecord['NAPDAT']         =  pyDate(forceDate(record.value('refDate')))

            if not forceInt(record.value('refId')):
                dbfRecord['NAPUCH'] = 0
                dbfRecord['NAPDAT'] = pyDate(begDate) - datetime.timedelta(days=1)
        
            dbfRecord['DS0']            =  forceString(record.value('MKBEx'))
        
            dbfRecord['RSLT']           =  forceInt(record.value('eventResultFederalCode'))
        
            dbfRecord['USL_OK']         =  forceInt(record.value('medicalAidTypeFederalCode'))
        
            dbfRecord['VIDPOM']         =  forceInt(record.value('medicalAidKindFederalCode'))
        
            dbfRecord['EXTR']           =  2 if forceInt(record.value('order')) == 2 else 1
        
            dbfRecord['PRVS']           =  prvs
        
            dbfRecord['IDDOKT']         =  0 #iddokt
        
            dbfRecord['CNILSVR']        =  formatSNILS(forceString(QtGui.qApp.db.translate('Person', 'id', record.value('execPersonId'), 'SNILS')))
        
            dbfRecord['ISHOD']          =  forceInt(record.value('resultFederalCode'))
        
            dbfRecord['CODE_MO']        =  miacCode

            dbfRecord['OS_SLUCH'] =  os_sluch if os_sluch != '' else '0;'

            dbfRecord['KSPECTAR'] = forceLong(forceString(record.value('federalCode'))[:11])
            dbfRecord = self.dbfRecordToUpper(dbfRecord)
            dbfRecord.store()
        
        fedprice = forceDouble(record.value('federalPrice'))

        #POLSPR file

        dbfRecord = dbfPoslpr.newRecord()

        dbfRecord['NREESTR'] = nreestr

        dbfRecord['KODLPU']  = infisCode

        dbfRecord['NSCHT']   = nschet

        dbfRecord['NSVOD']   = nsvod

        dbfRecord['DATAP']   = pyDate(forceDate(record.value('visitDate')))

        dbfRecord['SHDZ']    = forceString(record.value('VISIT_MKB'))

        dbfRecord['KSPEC']   = kspec

        dbfRecord['ZPL']     = price * forceDouble(record.value('ZPLPercent'))/100
        
        dbfRecord['MED']     = price * forceDouble(record.value('MEDPercent'))/100

        dbfRecord['M_INV']   = price * forceDouble(record.value('IVNVPercent'))/100

        dbfRecord['KOS']      = price * forceDouble(record.value('KOSPercent'))/100

        dbfRecord['NAKL']     = price * forceDouble(record.value('NAKLPercent'))/100

        dbfRecord['DOPL']     = price * forceDouble(record.value('DOPLPercent'))/100

        dbfRecord['STOIM']   = price * forceInt(record.value('amount')) #forceDouble(record.value('sum'))

        dbfRecord['DS0']     = forceString(record.value('MKBEx'))

        dbfRecord['DS2']     = forceString(record.value('AssociatedMKB'))

        dbfRecord['IDSP']    = forceInt(record.value('medicalAidUnitFederalCode'))

        #dbfRecord['ED_COL']  = пусто forceInt(record.value('amount'))

        dbfRecord['TARIF']   = price

        dbfRecord['LPU']     = miacCode

        dbfRecord['PROFIL']  = forceInt(forceString(record.value('medicalAidProfileFederalCode'))[:3])

        dbfRecord['PRVS']    = prvs

        dbfRecord['IDDOKT']  = 0 #iddokt

        dbfRecord['PODR']    = podr #forceInt(forceString(kspec)[:4])

        dbfRecord['DET']     = 0 #1 if age < 18 else 0

        for name in self.polsprFields.keys():
                if self.polsprFields[name][0] and not dbfRecord[name]:
                    self.log(u'обязательное поле %s(%s) не заполнено, файл POLSPR.DBF, пациент %s' % (name, self.polsprFields[name][1], client))
        dbfRecord = self.dbfRecordToUpper(dbfRecord)
        dbfRecord.store()
       
        if fedprice:

            dbfRecord = dbfPoslpr.newRecord()
        
            dbfRecord['NREESTR'] = nreestr
         
            dbfRecord['KODLPU']  = infisCode
         
            dbfRecord['NSCHT']   = nschet
         
            dbfRecord['NSVOD']   = nsvod
         
            dbfRecord['DATAP']   = pyDate(forceDate(record.value('visitDate')))
         
            dbfRecord['SHDZ']    = forceString(record.value('VISIT_MKB'))
         
            dbfRecord['KSPEC']   = kspec
         
            dbfRecord['DS0']     = forceString(record.value('MKBEx'))
         
            dbfRecord['DS2']     = forceString(record.value('AssociatedMKB'))
         
            dbfRecord['IDSP']    = forceInt(record.value('medicalAidUnitFederalCode'))
         
            #dbfRecord['ED_COL']  = пусто forceInt(record.value('amount'))
        
            dbfRecord['LPU']     = miacCode
         
            dbfRecord['PROFIL']  = forceInt(forceString(record.value('medicalAidProfileFederalCode'))[:3])
         
            dbfRecord['PRVS']    = prvs
         
            dbfRecord['IDDOKT']  = 0 #iddokt
        
            dbfRecord['PODR']    = forceInt(forceString(kspec)[:4])
        
            dbfRecord['DET']     = 0 #1 if age < 18 else 0
    
            dbfRecord['ZPL']     = 0
        
            dbfRecord['MED']     = 0
    
            dbfRecord['M_INV']   = 0
    
            dbfRecord['KOS']     = 0

            dbfRecord['DOPL']     = 0            

            dbfRecord['NAKL']    = 0
    
            dbfRecord['STOIM'] = fedprice
    
            dbfRecord['TARIF'] = fedprice

            for name in self.polsprFields.keys():
                if self.polsprFields[name][0] and not dbfRecord[name]:
                    self.log(u'обязательное поле %s(%s) не заполнено, файл POLSPR.DBF, пациент %s' % (name, self.polsprFields[name][1], client))
            dbfRecord = self.dbfRecordToUpper(dbfRecord)
            dbfRecord.store()
        return
        #USLUGIP file
    
        dbfRecord = dbfUslugiP.newRecord()
    
        dbfRecord['NREESTR'] = nreestr
    
        dbfRecord['NSVOD']   = nsvod
    
        dbfRecord['NSCHT']   = nschet
    
        dbfRecord['KODLPU']  = infisCode
    
        #TODO dbfRecord['KSPECP']  =
    
        dbfRecord['DATE_IN'] = pyDate(forceDate(record.value('DATE_IN')))
    
        dbfRecord['DATE_OUT'] = pyDate(forceDate(record.value('DATE_OUT')))
    
        dbfRecord['KODUS']    = forceString(record.value('service'))[:7]
    
        dbfRecord['SHDZ']    = forceString(record.value('MKB'))

        dbfRecord['KRATN']   = forceInt(record.value('amount'))

        dbfRecord['ZPL']            = price * forceDouble(record.value('ZPLPercent'))/100
        
        dbfRecord['MED']            = price * forceDouble(record.value('MEDPercent'))/100

        dbfRecord['M_INV']          = price * forceDouble(record.value('INVPercent'))/100

        dbfRecord['KOS']            = price * forceDouble(record.value('KOSPercent'))/100

        dbfRecord['NAKL']           = price * forceDouble(record.value('NAKLPercent'))/100

        dbfRecord['DOPL']           = price * forceDouble(record.value('DOPLPercent'))/100

        dbfRecord['STOIM'] = fedprice

        dbfRecord['TARIF'] = fedprice

        dbfRecord['IDSP']          = forceInt(record.value('medicalAidUnitFederalCode'))

        dbfRecord['PROFIL'] = forceInt(forceString(record.value('medicalAidProfileFederalCode'))[:3])

        dbfRecord['IDDOKT'] = iddokt
        
        dbfRecord['PRVS'] = prvs
        
        dbfRecord['PODR'] = forceInt(record.value('orgStructCode'))

        dbfRecord['DET'] = 1 if age < 18 else 0
        
        dbfRecord['LPU'] = miacCode
        dbfRecord = self.dbfRecordToUpper(dbfRecord)
        dbfRecord.store()
        #TODO: dbfRecord = dbfRodP.newRecord()


# *****************************************************************************************

    def processPerson(self, dbf, record, codeLPU):
        (dbfP, dbfU, dbfB,  dbfD, dbfS,  dbfPM, dbfUM, dbfBM,  dbfDM, dbfSM) = dbf
        personCode = forceString(record.value('tabNum'))

        items = [(dbfD, dbfS)]

        if len(self.modernClients) > 0:
            items.append((dbfDM, dbfSM))

        for (d, s) in items:
            row = d.newRecord()
            row['CODE_MO'] = codeLPU
            row['DOC_TABN'] = personCode
            row['FIO'] = forceString(record.value('lastName'))
            row['IMA'] = forceString(record.value('firstName'))
            row['OTCH'] = forceString(record.value('patrName'))
            row['POL'] = self.sexMap.get(forceInt(record.value('sex')))
            row['DATR'] = pyDate(forceDate(record.value('birthDate')))
            row.store()

            row = s.newRecord()
            row['CODE_MO'] = codeLPU
            row['DOC_TABN'] = personCode
            row['SPEC'] = forceString(record.value('specialityCode')).rjust(3, '0')
            row['KOTD'] = forceString(record.value('orgStructCode'))
            row['DOLG'] = forceString(record.value('postCode'))
            row.store()

# *****************************************************************************************

    def getClientTempInvalidList(self, clientId, begDate, endDate, personId):
        key = (clientId, begDate, endDate, personId)
        lst = self.tempInvalidCache.get(key, [])

        if lst == []:
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
                lst.append((forceDate(record.value('begDate')),
                    forceDate(record.value('endDate')),
                    forceString(record.value('serial')),
                    forceInt(record.value('number')),
                    forceRef(record.value('id')),
                    forceInt(record.value('reasonCode')),
                    forceString(record.value('MKB'))
                    ))

            self.tempInvalidCache[key] = lst

        return lst

# *****************************************************************************************

    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True


    def writeByte(self, filename, byteNumber, byteValue):
        with open(filename,'r+b') as f:
            f.seek(byteNumber)
            f.write(chr(byteValue))


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.abort()


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


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        modern = (self.parent.page1.cmbAccountType.currentIndex() > 3)
        zipFileName = self.parent.page1.getZipFileName(modern)
        zipFilePath = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                zipFileName)
        zf = ZipFile(zipFilePath, 'w', allowZip64=True)

        for src in ('PACIENTP.DBF', 'POSLPR.DBF', 'TALON.DBF', 'TALON1.DBF', 'USLUGIP.DBF', 'RODP.DBF'):
            filePath = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                    os.path.basename(src))
            zf.write(filePath, src, ZIP_DEFLATED)

        zf.close()

        dst = os.path.join(forceStringEx(self.edtDir.text()), zipFileName)
        success = QtGui.qApp.call(self, shutil.move, (zipFilePath, dst))[0]

        if success:
            QtGui.qApp.preferences.appPrefs['ExportR23NativeExportDir'] = toVariant(self.edtDir.text())
            self.wizard().setAccountExposeDate()

        return success


    @QtCore.pyqtSlot(QString)
    def on_edtDir_textChanged(self):
        saveDir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(saveDir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        saveDir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ОМС Ростова',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(saveDir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(saveDir))
