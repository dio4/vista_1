# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


import os.path
import shutil

from library.Utils     import *
from library.exception  import CException
from Events.Action import CAction
from Exchange.Utils import compressFileIn7Zip,CExportHelperMixin
from library.roman import rtoi

from Ui_ExportR29NativePage1 import Ui_ExportPage1
from Ui_ExportR29NativePage2 import Ui_ExportPage2


def getAccountInfo(accountId):
    accountRecord = None
    db = QtGui.qApp.db
    stmt = """SELECT
            Account.settleDate AS date,
            Account.number,
            Contract.resolution AS contractNum,
            Contract.date AS contractDate,
            Contract.grouping AS contractGrouping,
            rbFinance.code AS financeCode,
            Organisation.infisCode AS orgCode,
            Organisation.shortName AS orgName,
            Organisation.Address AS orgAddr,
            Organisation.chief AS orgChief
        FROM Account
        LEFT JOIN Contract ON Account.contract_id = Contract.id
        LEFT JOIN rbFinance ON Contract.finance_id = rbFinance.id
        LEFT JOIN Organisation ON Contract.payer_id = Organisation.id
        WHERE Account.id = %d
    """ % accountId
    query = db.query(stmt)

    if query:
        query.first()
        accountRecord = query.record()

    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        number = forceString(accountRecord.value('number'))
        orgCode = forceString(accountRecord.value('orgCode'))
        orgName = forceString(accountRecord.value('orgName'))
        financeCode = forceString(accountRecord.value('financeCode'))
        contractNum = forceString(accountRecord.value('contractNum'))
        contractDate = forceDate(accountRecord.value('contractDate'))
        orgAddr = forceString(accountRecord.value('orgAddr'))
        contractGrouping = forceString(accountRecord.value('contractGrouping'))
    else:
        date = None
        number = ''
        orgCode = ''
        orgName = ''
        financeCode = None
        contractDate = None
        contractNum = ''
        orgAddr = ''
        contractGrouping = ''

    return date, number,  financeCode,  contractNum, \
        contractDate,  orgName,  orgAddr, orgCode,  contractGrouping


def splitStrByLen(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]


def exportR29Native(widget, accountId, accountItemIdList):
    wizard = CExportR29NativeWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportR29NativeWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта для Архангельска')
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date,  number, financeCode, contractNum, \
            contractDate, orgName, orgAddr, orgCode,  grp = getAccountInfo(accountId)
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменного файла')
        self.page1.accNumber = number
        self.page1.financeCode = financeCode
        self.page1.contractNum = contractNum
        self.page1.contractDate = contractDate
        self.page1.payerAddr = orgAddr
        self.page1.payerName = orgName
        self.page1.accDate =date
        self.page1.contractModern = (grp == u'Модернизация')


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R29Native')
        return self.tmpDir


    def getFullTxtFileName(self):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'miacCode'))
        #year = forceString(self.page1.accDate.toString('yy'))

        strNumber = forceString(self.page1.accNumber).strip()
        if strNumber.isdigit():
            number = forceInt(strNumber)
        else:
            # убираем номер договора с дефисом, если они есть в номере
            i = len(strNumber) - 1
            while (i>0 and strNumber[i].isdigit()):
                i -= 1

            number = forceInt(strNumber[i+1:] if strNumber[i+1:] != '' else 0)

        return os.path.join(self.getTmpDir(), u'%s%03d.rlu' % (lpuCode, number))


    def setAccountItemsIdList(self, accountItemIdList):
        self.page1.setAccountItemsIdList(accountItemIdList)


    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1, CExportHelperMixin):
    ddSpecialityMap = {
    '38': u'ДД9', #терапевт
    '64': u'ДД10', #хирург
    '36': u'ДД11', #офтальмолог
    '25': u'ДД12', #невролог
    '2': u'ДД13', #акушер-гинеколог
    }

    dsSpecialityMap = {
    '52': u'ДС8', #педиатр
    '40': u'ДС9', #невролог
    '49': u'ДС10', #офтальмолог
    '19': u'ДС11', #детский хирург
    '48': u'ДС12', #оториноларинголог
    '02': u'ДС13', #акушер-гинеколог
    '71': u'ДС14', #детский стоматолог
    '81': u'ДС15', #ортопед-травматолог
    '54': u'ДС16', #психиатр
    '18': u'ДС17', #детский уролог-андролог
    '20': u'ДС18', #детский эндокринолог
    }

    mapRegistryType = {
        0:1,  1:2,  2:4, 3:5,  4:6, 5:7, 6:8, 7:9
    }

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        CExportHelperMixin.__init__(self)
        self.setupUi(self)
        self.tblEventTypeDS.setTable('EventType')
        self.tblEventTypeDD.setTable('EventType')
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')
        self.parent = parent

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.tariffCache = {}
        self.accSystemId = None
        self.financeCode = None
        self.recNum = 1
        self.totalSum = 0
        self.contractNum = ''
        self.contractDate = None
        self.payerAddr = ''
        self.payerName = ''
        self.accDate = None
        self.clientCount = 0
        self.db = QtGui.qApp.db
        self.tableDiagnostic = self.db.table('Diagnostic')
        self.tableSpeciality = self.db.table('rbSpeciality')
        self.tableAccountItem = self.db.table('Account_Item')
        self.tableActionType = self.db.table('ActionType')
        self.tableAction = self.db.table('Action')
        self.mapSex = {1: u'М',  2: u'Ж'}
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)

        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29NativeVerboseLog', 'False')))
        self.chkExportDD.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29NativeExportDD', 'False')))
        self.chkExportDS.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29NativeExportDS', 'False')))
        self.chkEventSplit.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29EventSplit', 'False')))
        ddEventTypesStr=forceString(getVal(
            QtGui.qApp.preferences.appPrefs, 'ExportR29NativeEventTypeDD', '1,12,25,27,26'))
        dsEventTypesStr=forceString(getVal(
            QtGui.qApp.preferences.appPrefs, 'ExportR29NativeEventTypeDS', '2,28'))
        self.currentOrgCode = ''
        self.eventTypesDD=[int(x) for x in ddEventTypesStr.split(',') if ddEventTypesStr]
        self.tblEventTypeDD.setValues(self.eventTypesDD)
        self.eventTypesDS=[int(x) for x in dsEventTypesStr.split(',') if dsEventTypesStr]
        self.tblEventTypeDS.setValues(self.eventTypesDS)

        self.actionTypeGroup1 = None
        self.actionTypeGroup2 = None
        self.ddAnalysisMap = None
        self.dsAnalysisMap = None
        self.exportDD = False
        self.exportDS = False
        self.registryType = None
        self.contractModern = False


    def prepareActionTypeGroups(self):
        if not self.actionTypeGroup1:
            record = self.db.getRecordEx('ActionType', 'id', 'code=\'1-1\' and class=1')

            if record:
                self.actionTypeGroup1 = forceInt(record.value(0)) # id лабораторных исследований

        if not self.actionTypeGroup2:
            record = self.db.getRecordEx('ActionType', 'id', 'code=\'1-2\' and class=1')

            if record:
                self.actionTypeGroup2 = forceInt(record.value(0)) # id лучевой диагностики


    def prepareForDD(self):
        u"""Готовит данные, необходимые для получения информации о ДД"""

        self.prepareActionTypeGroups()

        ddAnalysisTypes = [
            # name, code, group_id
            (u'ДД14', '03', self.actionTypeGroup1), # Клинический анализ крови
            (u'ДД15', '04', self.actionTypeGroup1), # Клинический анализ мочи
            (u'ДД16', '01', self.actionTypeGroup1), # исследование уровня холестерина крови
            (u'ДД17', '02', self.actionTypeGroup1), # Сахар крови
            (u'ДД18', '30', self.actionTypeGroup1), # Общий белок крови
            (u'ДД19', '31', self.actionTypeGroup1), # Креатинин крови
            (u'ДД20', '05', self.actionTypeGroup1), # Холестерин липопротеидов низкой плотности
            (u'ДД21', '06', self.actionTypeGroup1), # Триглицериды
            (u'ДД22', '32', self.actionTypeGroup1), # Мочевая кислота
            (u'ДД23', '33', self.actionTypeGroup1), # Билирубин крови
            (u'ДД24', '34', self.actionTypeGroup1), # Амилаза крови
            (u'ДД25', '07', self.actionTypeGroup1), # Онкомаркер специфический CA-125
            (u'ДД26', '08', self.actionTypeGroup1), # Онкомаркер специфический PSI
            (u'ДД27', '07', self.actionTypeGroup2), # ЭКГ
            (u'ДД28', '06', self.actionTypeGroup2), # Флюорография
            (u'ДД29', '05', self.actionTypeGroup2), # Маммография
            (u'ДД30', '35', self.actionTypeGroup1), # Цитологическое исследование мазка из цервикального канала
        ]

        self.ddAnalysisMap = self.makeAnalysisMap(ddAnalysisTypes)


    def prepareForDS(self):
        u"""Готовит данные, необходимые для получения информации о ДС"""

        self.prepareActionTypeGroups()

        dsAnalysisTypes = [
            # name, code, group_id
            (u'ДС19', '03', self.actionTypeGroup1), # Клинический анализ крови
            (u'ДС20', '04', self.actionTypeGroup1), # Клинический анализ мочи
            (u'ДС21', '07', self.actionTypeGroup2), # ЭКГ
            (u'ДС22', '11', self.actionTypeGroup2), # УЗИ сердца
            (u'ДС23', '12', self.actionTypeGroup2), # УЗИ почек
            (u'ДС24', '12', self.actionTypeGroup2), # УЗИ печени и желчного пузыря
            (u'ДС25', '13', self.actionTypeGroup2), # УЗИ тазобедренных суставов
        ]

        self.dsAnalysisMap = self.makeAnalysisMap(dsAnalysisTypes)


    def makeAnalysisMap(self, types):
        result = {}

        for (key, code,  groupId) in types:
            record = self.db.getRecordEx(self.tableActionType, 'id',
                self.db.joinAnd([self.tableActionType['code'].eq(code),
                                 self.tableActionType['group_id'].eq(groupId)]))
            if record:
                id = forceRef(record.value(0))
                result[id] = key
            else:
                self.log(u'<b><font color=red>ОШИБКА</font></b>:'\
                u' Не найден тип действия с кодом `%s`,'
                u' находящийся в группе id=`%d`,'
                u' необходимый для заполнения поля `%s` файла экспорта.' %\
                (code,  groupId, key))

        return result


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.chkExportDD.setEnabled(not flag)
        self.chkExportDS.setEnabled(not flag)
        self.tblEventTypeDD.setEnabled(not flag and self.chkExportDD.isChecked())
        self.tblEventTypeDS.setEnabled(not flag and self.chkExportDS.isChecked())


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
        txt,  txtStream = self.createTxt()
        self.accSystemId = forceRef(QtGui.qApp.db.translate('rbAccountingSystem', \
                'code', '29',  'id'))
        self.currentOrgCode = forceString(QtGui.qApp.db.translate('Organisation', 'id',
                                                                  QtGui.qApp.currentOrgId(), 'infisCode'))
        self.eventTypesDD = self.tblEventTypeDD.values()
        self.eventTypesDS = self.tblEventTypeDS.values()
        self.recNum = 1
        self.registryType = self.mapRegistryType.get(self.cmbRegistryType.currentIndex())

        if self.chkExportDD.isChecked() and (self.eventTypesDD != []):
            self.prepareForDD()
            self.exportDD = True
        else:
            self.exportDD = False

        if self.chkExportDS.isChecked() and (self.eventTypesDS != []):
            self.prepareForDS()
            self.exportDS = True
        else:
            self.exportDS = False


        self.eventSplit = self.chkEventSplit.isChecked()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return txt, txtStream, query


    def export(self):
        QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))

        QtGui.qApp.preferences.appPrefs['ExportR29NativeVerboseLog'] = \
            toVariant(self.chkVerboseLog.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR29NativeExportDD'] = \
            toVariant(self.chkExportDD.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR29NativeExportDS'] = \
            toVariant(self.chkExportDS.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR29EventSplit'] = \
            toVariant(self.chkEventSplit.isChecked())
        QtGui.qApp.preferences.appPrefs['ExportR29NativeEventTypeDD'] = \
            toVariant(','.join([str(x) for x in self.eventTypesDD]))
        QtGui.qApp.preferences.appPrefs['ExportR29NativeEventTypeDS'] = \
            toVariant(','.join([str(x) for x in self.eventTypesDS]))
        QtGui.qApp.preferences.appPrefs['ExportR29RegistryType'] = \
            toVariant(self.cmbRegistryType.currentIndex())


    def exportInt(self):
        txt, txtStream, query = self.prepareToExport()
        if self.idList:
            self.writeTextHeader(txtStream)
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(txtStream, query.record())
            self.writeTextFooter(txtStream)
        else:
            self.progressBar.step()

        txt.close()


    def createTxt(self):
        txt = QFile(self.wizard().getFullTxtFileName())
        txt.open(QIODevice.WriteOnly | QIODevice.Text)
        txtStream =  QTextStream(txt)
        txtStream.setCodec('CP866')
        return txt,  txtStream

# *****************************************************************************************

    def getAccountFileName(self, accountItemId):
        result = ''

        if accountItemId:
            accId = forceRef(QtGui.qApp.db.translate(
                'Account_Item', 'id',  accountItemId, 'master_id'))
            strNumber = forceString(QtGui.qApp.db.translate(
                'Account', 'id',  accId, 'number')).strip()

            if strNumber.isdigit():
                number = forceInt(strNumber)
            elif not strNumber:
                number = 0
            else:
                # убираем номер договора с дефисом, если они есть в номере
                i = len(strNumber) - 1
                while (i>0 and strNumber[i].isdigit()):
                    i -= 1

                number = forceInt(strNumber[i+1:] if strNumber[i+1:] != '' else 0)

            lpuCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', QtGui.qApp.currentOrgId() , 'miacCode'))
            result = '%s%03d.rlu' % (lpuCode, number)

        return result

# *****************************************************************************************

    def createQuery(self):
        if self.financeCode == '3': #ДМС
            policyType_id = forceRef(self.db.translate('rbPolicyType', \
                'code', '3',  'id'))
            policyFilter = 'CP.policyType_id = %d' % policyType_id
            lastPolicyFilter = 'CP1.policyType_id = %d' % policyType_id
        else:
            policyFilter = '1'
            lastPolicyFilter = '1'

        accSysFilter = 'ClientIdentification.accountingSystem_id = %d' % \
            self.accSystemId if self.accSystemId else '1'

        stmt = """SELECT
                Client.id               AS clientId,
                Client.lastName        AS lastName,
                Client.firstName       AS firstName,
                Client.patrName       AS patrName,
                Client.sex              AS sex,
                Client.birthDate AS birthDate,
                age(Client.birthDate, Event.execDate) as clientAge,
                ClientDocument.serial  AS documentSerial,
                ClientDocument.number  AS documentNumber,
                rbDocumentType.code AS documentTypeCode,
                rbDocumentType.regionalCode AS documentRegionalCode,
                Citizenship.regionalCode AS citizenshipCode,
                Employment.regionalCode AS employmentCode,
                kladr.STREET.NAME AS streetName,
                kladr.SOCRBASE.infisCode AS streetType,
                AddressHouse.number AS number,
                AddressHouse.corpus AS corpus,
                AddressHouse.KLADRCode,
                AddressHouse.KLADRStreetCode,
                Address.flat AS flat,
                Insurer.shortName AS insurerName,
                Insurer.OGRN AS insurerOGRN,
                Insurer.area AS insurerArea,
                ClientPolicy.id AS policyId,
                ClientPolicy.serial AS policySerial,
                ClientPolicy.number AS policyNumber,
                ClientPolicy.begDate AS policyBegDate,
                ClientPolicy.endDate AS policyEndDate,
                LastInsurer.shortName AS lastInsurerName,
                LastInsurer.OGRN AS lastInsurerOGRN,
                LastInsurer.area AS lastInsurerArea,
                ClientPolicy.id AS lastPolicyId,
                ClientLastPolicy.serial AS lastPolicySerial,
                ClientLastPolicy.number AS lastPolicyNumber,
                ClientLastPolicy.begDate AS lastPolicyBegDate,
                ClientLastPolicy.endDate AS lastPolicyEndDate,
                IF(work.title IS NOT NULL,
                    work.title, ClientWork.freeInput) AS `workName`,
                Event.id AS eventId,
                Event.setDate AS begDate,
                Event.execDate AS endDate,
                Visit.date AS visitDate,
                TempInvalid.begDate AS tempInvalidBegDate,
                TempInvalid.endDate AS tempInvalidEndDate,
                CONCAT(TempInvalid.serial,' ',TempInvalid.number) AS tempInvalidSN,
                Diagnosis.MKB          AS MKB,
                AccDiagnosis.MKB AS AccMKB,
                Person.SNILS AS personSNILS,
                rbSpeciality.regionalCode AS personRegionalCode,
                rbPost.regionalCode AS postRegionalCode,
                rbSpeciality.OKSOCode AS personOKSOCode,
                rbResult.regionalCode AS resultCode,
                Event.note AS eventNote,
                OrgStructure.infisCode AS bedCode,
                IF(Account_Item.service_id IS NOT NULL, rbItemService.group_id,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.group_id,
                    IF(EventType.service_id IS NOT NULL, rbEventService.group_id,
                    TariffService.group_id))) AS serviceGroupId,
                IF(Account_Item.service_id IS NOT NULL, rbItemService.infis,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis,
                    IF(EventType.service_id IS NOT NULL, rbEventService.infis,
                    TariffService.infis))) AS serviceCode,
                IF(Account_Item.service_id IS NOT NULL, rbItemService.name,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.name,
                    IF(EventType.service_id IS NOT NULL, rbEventService.name,
                    TariffService.name))) AS serviceName,
                IF(Account_Item.service_id IS NOT NULL,
                    ItemMedicalAidProfile.code,
                    IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.code, EventMedicalAidProfile.code)
                    ) AS medicalAidProfileCode,
                IF(Account_Item.service_id IS NOT NULL,
                    ItemMedicalAidProfile.regionalCode,
                    IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.regionalCode, EventMedicalAidProfile.regionalCode)
                    )  AS medicalAidTypeCode,
                rbMedicalAidUnit.regionalCode AS medicalAidUnitCode,
                Account_Item.price    AS price,
                Account_Item.amount    AS amount,
                Account_Item.`sum`     AS `sum`,
                Account_Item.uet AS uet,
                Account_Item.id AS accountItemId,
                HospitalAction.id AS hospActionId,
                ClientIdentification.identifier AS identifier,
                EventType.id AS eventTypeId,
                EventType.code AS eventTypeCode,
                ReexpItem.id AS oldAccountItemId,
                rbDiseaseCharacter.code AS characterCode,
                SpecialCase.regionalCode AS specialCaseCode,
                IF(SpecialCaseAction.id IS NULL, 0, 1) AS specialCaseAction,
                StdActionType.code AS stdActionCode,
                Action.begDate AS actionBegDate,
                Action.endDate AS actionEndDate
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                      ClientPolicy.id = (SELECT MAX(CP.id)
                                         FROM   ClientPolicy AS CP
                                         WHERE  CP.client_id = Client.id
                                            AND (Event.setDate BETWEEN CP.begDate AND CP.endDate OR Event.execDate BETWEEN CP.begDate AND CP.endDate)
                                            AND %s)
            LEFT JOIN ClientPolicy AS ClientLastPolicy ON ClientLastPolicy.client_id = Client.id AND
                      ClientLastPolicy.id = (SELECT MAX(CP1.id)
                                         FROM   ClientPolicy AS CP1
                                         WHERE  CP1.client_id = Client.id
                                            AND %s)
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN vrbPerson ON vrbPerson.id = Event.execPerson_id
            LEFT JOIN Diagnostic ON Diagnostic.id = (
              SELECT MAX(D.id)
              FROM Diagnostic AS D
              WHERE D.event_id = Account_Item.event_id
                AND ((D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code ='2')
                        AND D.person_id = Event.execPerson_id) OR (
                          D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='1')))
                          AND D.deleted = 0)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id =Diagnosis.character_id
            LEFT JOIN Diagnostic AS AccDiagnostic ON AccDiagnostic.id = (
             SELECT id FROM Diagnostic AS AD
             WHERE AD.event_id = Account_Item.event_id AND
                AD.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='9') AND
                AD.person_id = Event.execPerson_id AND
                AD.deleted = 0 LIMIT 1)
            LEFT JOIN Diagnosis AS AccDiagnosis ON
                AccDiagnosis.id = AccDiagnostic.diagnosis_id AND
                AccDiagnosis.deleted = 0
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN rbPost ON Person.post_id = rbPost.id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN ClientIdentification ON Client.id = ClientIdentification.client_id AND
                    ClientIdentification.deleted = 0 AND %s
            LEFT JOIN ClientWork ON ClientWork.client_id=Client.id AND
                        ClientWork.id = (SELECT max(CW.id)
                                         FROM ClientWork AS CW
                                         WHERE CW.client_id=Client.id AND CW.deleted = 0)
            LEFT JOIN Organisation AS work ON work.id=ClientWork.org_id AND work.deleted = 0
            LEFT JOIN ClientDocument ON
                ClientDocument.client_id = Client.id AND
                ClientDocument.id = (
                    SELECT MAX(CD.id)
                    FROM   ClientDocument AS CD
                    LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                    LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                    WHERE  rbDTG.code = '1' AND CD.client_id = Client.id)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN ClientAddress ON
                ClientAddress.client_id = Client.id AND
                ClientAddress.id = (
                    SELECT MAX(CA.id)
                    FROM ClientAddress AS CA
                    WHERE  CA.type = '0' AND CA.client_id = Client.id)
            LEFT JOIN Address ON Address.id = ClientAddress.address_id
            LEFT JOIN AddressHouse ON AddressHouse.id = Address.house_id
            LEFT JOIN kladr.STREET ON kladr.STREET.CODE = AddressHouse.KLADRStreetCode
            LEFT JOIN kladr.SOCRBASE ON kladr.SOCRBASE.KOD_T_ST = (SELECT KOD_T_ST
                        FROM kladr.SOCRBASE AS SB
                        WHERE SB.SCNAME = kladr.STREET.SOCR
                        LIMIT 1)
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
            LEFT JOIN ClientSocStatus AS ClientEmploymentStatus ON
                ClientEmploymentStatus.client_id = Client.id AND
                ClientEmploymentStatus.deleted = 0 AND
                ClientEmploymentStatus.socStatusClass_id = (
                    SELECT rbSSC.id
                    FROM rbSocStatusClass AS rbSSC
                    WHERE rbSSC.code = '5' AND rbSSC.group_id IS NULL
                    LIMIT 0,1
                )
            LEFT JOIN rbSocStatusType AS Employment ON
                ClientEmploymentStatus.socStatusType_id =Employment.id
            LEFT JOIN ClientSocStatus AS SpecialCaseStatus ON
                SpecialCaseStatus.client_id = Client.id AND
                SpecialCaseStatus.deleted = 0 AND
                SpecialCaseStatus.socStatusClass_id = (
                    SELECT rbSSC1.id
                    FROM rbSocStatusClass AS rbSSC1
                    WHERE rbSSC1.code = '10' AND rbSSC1.group_id IS NULL
                    LIMIT 0,1
                )
            LEFT JOIN rbSocStatusType AS SpecialCase ON
                SpecialCaseStatus.socStatusType_id =SpecialCase.id
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN Organisation AS LastInsurer ON LastInsurer.id = ClientLastPolicy.insurer_id
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
            LEFT JOIN rbResult ON Event.result_id = rbResult.id
            LEFT JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
            LEFT JOIN rbMedicalAidProfile AS EventMedicalAidProfile ON
                EventMedicalAidProfile.id = rbEventService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS VisitMedicalAidProfile ON
                VisitMedicalAidProfile.id = rbVisitService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON
                ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN Contract_Tariff ON Contract_Tariff.id = Account_Item.tariff_id
            LEFT JOIN rbService AS TariffService ON TariffService.id = Contract_Tariff.service_id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
            LEFT JOIN Account_Item AS ReexpItem ON Account_Item.id = ReexpItem.reexposeItem_id
            LEFT JOIN Action AS SpecialCaseAction ON SpecialCaseAction.id = (
                    SELECT SCA.id
                    FROM Action SCA
                    LEFT JOIN ActionType AS SCAType ON SCA.actionType_id = SCAType.id
                    WHERE SCA.event_id = Account_Item.event_id AND
                            SCAType.code = '111'
                    LIMIT 1
                )
            LEFT JOIN ActionType AS StdActionType ON StdActionType.id = (
                    SELECT AT1.id
                    FROM Action STD
                    LEFT JOIN ActionType AS AT1 ON STD.actionType_id =AT1.id
                    LEFT JOIN ActionType AS ATGroup ON AT1.group_id =ATGroup.id
                    WHERE STD.event_id = Account_Item.event_id AND
                            ATGroup.code = 'STD' AND ATGroup.deleted = 0 AND
                            AT1.deleted = 0 AND STD.deleted = 0
                    LIMIT 1
                )
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
            WHERE Account_Item.reexposeItem_id IS NULL
                AND(Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0))
            AND %s
            ORDER BY Client.id, Diagnosis.MKB, execDate, serviceCode
        """ % (policyFilter, lastPolicyFilter, accSysFilter, self.tableAccountItem['id'].inlist(self.idList))
        return self.db.query(stmt)


    def getDiagDates(self,  eventId,  specList):
        u""" Получаем словарь {имя_поля:дата_диагностика} по событию и списку специальностей"""

        stmt='''SELECT Diagnostic.endDate, rbSpeciality.code
            FROM Diagnostic
            LEFT JOIN Person on Diagnostic.person_id=Person.id
            LEFT JOIN rbSpeciality on rbSpeciality.id=Person.speciality_id
            WHERE %s
            ORDER BY rbSpeciality.code
        ''' % self.db.joinAnd([self.tableDiagnostic['event_id'].eq(eventId),
            self.tableSpeciality['code'].inlist(specList.keys())])

        query = self.db.query(stmt)
        result = {}

        while query.next():
            record = query.record()
            if record:
                fieldName = specList.get(forceString(record.value('code')))
                endDate = forceDate(record.value('endDate'))

                if fieldName and endDate.isValid():
                    result[fieldName] = endDate

        return result


    def getAnalysisDates(self, eventId, actionTypeMap):
        u""" Получаем словарь {код_типа_действия:дата_окончания} по событию и списку типов действий"""

        result = {}

        if actionTypeMap and eventId:
            recordList = self.db.getRecordList(self.tableAction, 'actionType_id, endDate', [
                self.tableAction['event_id'].eq(eventId),
                self.tableAction['actionType_id'].inlist(actionTypeMap.keys())])


            for record in recordList:
                if record:
                    code = actionTypeMap.get(forceRef(record.value(0)))
                    endDate = forceDate(record.value(1))

                    if code and endDate.isValid():
                        result[code] = endDate

        return result


    def process(self, txt,  record):
        result = {}
        clientId = forceRef(record.value('clientId'))
        KLADRCode = forceString(record.value('KLADRCode'))
        isAlien = KLADRCode[:2] != '29'
        eventTypeId = forceRef(record.value('eventTypeId'))
        # Уникальный код записи в реестре, для обеспечения ссылочной целостности
        # 7, Только цифры, не может повторяться в одном реестре, Обязательное поле
        result[u'УКЛ'] = (forceString(record.value('accountItemId'))+'00')[-7:]
        # Фамилия пациента. При предъявлении полиса(паспорта) родителей
        # (или других представителей) через символ "/" указывается их фамилия
        #60, Русские буквы, допускается символы "пробел" и "-" при двойных фамилиях
        # Обязательное поле
        result[u'ФАМ'] = forceString(record.value('lastName'))[:60]
        # Имя пациента. При предъявлении полиса(паспорта) родителей
        # (или других представителей) через символ "/" указывается их имя
        # 40 Русские буквы, допускается символы "пробел" и "-" при двойном имени
        # Обязательное поле
        result[u'ИМЯ'] = forceString(record.value('firstName')) [:40]
        # Отчество пациента. При предъявлении полиса(паспорта) родителей
        # (или других представителей) через символ "/" указывается их отчество
        # 40 Русские буквы, допускается символы "пробел" и "-" при двойном отчестве
        # Допускается не заполненным только в случае отсутствия отчества в документе,
        # удостоверяющем личность
        result[u'ОТЧ'] = forceString(record.value('patrName'))[:40]
        #Дата рождения пациента
        #10 Арабские цифры по формату дд/мм/гггг. Разделитель "/" Обязательное поле
        result[u'Д_Р'] = forceDate(record.value('birthDate')).toString('dd/MM/yyyy')
        # Пол пациента
        # 1  Русская буква "М" или "Ж" Обязательное поле
        result[u'ПОЛ'] = self.mapSex.get(forceInt(record.value('sex')),  u'М')
        # Гражданство пациента
        # 3 Арабские цифры. Код по классификатору ОКСМ (справочник, передаваемый Фондом).
        # В случае невозможности получения сведений о гражданстве поле не заполняется
        # Обязательное поле, для реестров, содержащих сведения о медицинской помощи, оказанной
        # лицам, застрахованным вне территории Архангельской области
        result[u'ГРАЖД'] = forceString(record.value('citizenshipCode'))[:3]
        # Статус представителя пациента
        # 1 Арабская цифра: 0 - отсутствует; 1 - родитель; 2 - усыновитель;
        # 3 - опекун ребенка (физическое лицо); 4 - опекун (представитель ребенка
        # от социального учреждения); 5 - попечитель
        # Обязательное поле, для реестров, содержащих сведения о медицинской помощи, оказанной
        # лицам, застрахованным вне территории Архангельской области
        representativeInfo = self.getClientRepresentativeInfo(clientId)

        if representativeInfo:
            result[u'СПП'] = representativeInfo['relationTypeCode']
#            result[u'ФАМ'] += u'/' + representativeInfo['lastName']
#            result[u'ИМЯ'] += u'/' +representativeInfo['firstName']
#            result[u'ОТЧ'] += u'/' +representativeInfo['patrName']
        else:
            result[u'СПП'] = u'0'

        #Данные документа, удостоверяющего личность
        #Обязательно заполняется для жителей из других территорий РФ, для жителей АО - при отсутствии у пациента полиса

        #Код вида документа, удостоверяющего личность
        # 1 Цифра, в соответствии с Таблица 6
        # Обязательное поле при отсутствии полиса
        result[u'КВД'] = forceString(record.value('documentRegionalCode'))[:1]


        documentTypeCode = forceInt(record.value('documentTypeCode'))
        if documentTypeCode == 1: # паспорт РФ
            #Номер серии документа. Обязательное поле при отсутствии полиса
            serial = forceString(record.value('documentSerial'))
            result[u'НСД'] = serial[:2]

            #Серия документа. Обязательное поле при отсутствии полиса
            result[u'ССД'] = serial[2:4]

            #Номер документа. Обязательное поле при отсутствии полиса
            result[u'Н_Д'] = forceString(record.value('documentNumber'))[:6]
        elif documentTypeCode in (3 ,  11): # свидетельство о рождении, вид на жительство (без гражданства)
            serial = forceString(record.value('documentSerial')).split()

            if len(serial) < 2:
                self.log( u'<b><font color=red>ОШИБКА<\font><\b>:' \
                        u' Неверно заполнена серия документа'\
                        u' пациента %s %s %s %s г.р. Должен быть формат: ' \
                        u'римские цифры (IVXCDML), пробел, две русские буквы.' % (
                            result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)
            else:
                result[u'НСД'] = forceString(rtoi(serial[0]))

                #Серия документа. Обязательное поле при отсутствии полиса
                result[u'ССД'] = serial[1][:2]

            #Номер документа. Обязательное поле при отсутствии полиса
            result[u'Н_Д'] = forceString(record.value('documentNumber'))[:7]
        elif documentTypeCode in (4,  7) : # Военные билеты форматом не поддерживаются
                self.log( u'<b><font color=red>ОШИБКА<\font><\b>:' \
                        u' Военный билет и удостоверение офицера не могут быть выгружены как документ,'\
                        u' удостоверяющий личность пациента %s %s %s %s г.р.' % (
                            result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)
        elif documentTypeCode == 32: # загранпаспорт
            #Серия документа. Обязательное поле при отсутствии полиса
            result[u'ССД'] =forceString(record.value('documentSerial'))
            #Номер документа. Обязательное поле при отсутствии полиса
            result[u'Н_Д'] = forceString(record.value('documentNumber'))[:7]

        elif documentTypeCode == 0: # документ отсутствует
            self.log( u'ВНИМАНИЕ: Отсутствуют данные о документе, удостоверяющем'\
                        u' личность пациента %s %s %s %s г.р.' % (
                            result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)
        else:
            self.log( u'ВНИМАНИЕ: Экспорт типа документа код `%d` не поддерживается!'\
                        u' Сообщите разработчикам.' % documentTypeCode,  True)


        if KLADRCode == '':
            self.log( u'ВНИМАНИЕ: Отсутствуют данные об адресе регистрации'\
                        u' пациента %s %s %s %s г.р.' % (
                            result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)

        # Область РФ
        # 50 Русские буквы, допускается символы "пробел", "-" ,"запятая", "точка"
        # Обязательно заполняется для жителей из других территорий РФ, для
        # жителей АО - при отсутствии у пациента полиса
        result[u'ОБЛ'] = self.getKLADRName(KLADRCode[:2])
        # Район в области
        # 50 Русские буквы, цифры, допускается символы "пробел", "-" ,"запятая", "точка"
        # Обязательно заполняется для жителей из других территорий РФ,
        # для жителей АО - при отсутствии у пациента полиса.
        # Допускается не заполнять для городов областного подчинения
        result[u'РАЙ'] = self.getKLADRName(KLADRCode[:5])
        #Адрес постоянного проживания
        # Код территории, на которой проживает по документу удостоверяющему личность.
        # Для жителей Архангельской области код района, города.
        # Для жителей из других территорий РФ код области, края, республики
        # 10 В соответствии с Таблица 15 Обязательное поле
        result[u'КТП'] = self.getKLADRInfis(KLADRCode[:2] if isAlien else KLADRCode[:8])[:4]
        #Код вида населенного пункта
        #2 Арабские цифры. 1 - город; 2 - поселок городского типа;
        # 3 - поселок сельского типа; 4 - рабочий поселок; 5 - дачный поселок;
        # 6 - курортный поселок; 7 - кишлак; 8 - железнодорожная станция;
        # 9 - село; 10 - местечко; 11 - деревня; 12 - слобода; 13 - станция;
        # 14 - станица; 15 - хутор; 16 - разъезд; 17 - колхоз; 18 - совхоз; 19 - зимовье
        # Обязательное поле, для реестров, содержащих сведения о медицинской помощи,
        # оказанной лицам, застрахованным вне территории Архангельской области
        result[u'КНП'] = self.getSOCRInfisCode(KLADRCode)
        #Города, сельские администрации, поселки
        # 50 Русские буквы, цифры, допускается символы "пробел", "-" ,"запятая", "точка"
        # Обязательно заполняется для жителей из других территорий РФ, для жителей АО - при отсутствии у пациента полиса
        socr = self.getSOCR(KLADRCode)
        if socr == u'г':
            result[u'ГОР'] = self.getKLADRName(KLADRCode)

        # Название села, поселка, деревни при указании в поле ГОР сельсовета или сельской администрации
        # 04 Русские буквы, цифры, допускается символы "пробел", "-" ,"запятая", "точка"
        # Обязательно заполняется для жителей из других территорий РФ, для жителей АО - при отсутствии у пациента полиса.
        socr = self.getSOCR(KLADRCode)
        if socr in (u'с/с', u'с/а',  u'с'):
            result[u'СЕЛ'] = self.getKLADRName(KLADRCode)

        # Название деревни в составе села
        #50 Русские буквы, цифры, допускается символы "пробел", "-" ,"запятая", "точка"
        # Обязательно заполняется для жителей из других территорий РФ,
        # для жителей АО - при отсутствии у пациента полиса.
        # Заполняется при наличии в полисе или документе

        if socr == u'c' and self.getSOCR(\
                forceString(record.value('KLADRStreetCode'))) == u'д':
            result[u'ДЕР'] = self.getKLADRName(KLADRCode)

        # Код типа наименования улицы
        # 2 Арабские цифры. 1 - улица; 2 - проспект; 3 - шоссе; 4 - аллея; 5 - бульвар;
        # 6 - квартал; 7 - переулок; 8 - площадь; 9 - проезд; 10 - тупик; 11 - набережная;
        # 12 - линия; 13 - микрорайон; 14 - другое
        #Обязательное поле, для реестров, содержащих сведения о медицинской помощи,
        # оказанной лицам, застрахованным вне территории Архангельской области
        streetType = forceString(record.value('streetType'))[:2]
        result[u'КУЛ'] = streetType if streetType else '14'
        # Улицы, деревни и поселки в составе городов
        # 50 Русские буквы, цифры, допускается символы "пробел", "-" ,"запятая", "точка"
        # Обязательно заполняется для жителей из других территорий РФ,
        # для жителей АО - при отсутствии у пациента полиса. Допускается отсутствие
        # при заполненных полях СЕЛ, ДЕР. Для проживающих в ВЧ указывается номер ВЧ,
        # обязательно для городов
        result[u'УЛИ'] = forceString(record.value('streetName'))[:50]
        #Номер дома, при отсутствии в документе удостоверяющем личность заносится
        # ЧД или ВЧ для проживающих на территориях воинских частей
        # 4 Буквы и цифры. Обязательно заполняется для жителей из других территорий РФ,
        # для жителей АО - при отсутствии у пациента полиса. При отсутствии в документах
        # заполняется значением «Н/У» - «не указан»
        result[u'ДОМ'] = forceString(record.value('number'))[:4]
        # Корпус
        # 3 Буквы и цифры
        result[u'КОР'] = forceString(record.value('corpus'))[:3]
        # Квартира
        # 3 Буквы и цифры
        result[u'КВА'] = forceString(record.value('flat'))[:3]

        # Работающий или неработающий
        # 3 Русские буквы, обозначение статуса (категории) пациента в соответствии со
        # следующим справочником: НВР – новорожденный, ДШК – дошкольник,
        # ШК – ребенок до 14 лет, СУ – студент/учащийся, Р – работающий, П – пенсионер,
        # Н – неработающий, Д – другое.
        # Обязательное поле
        result[u'КАТ'] = forceString(record.value('employmentCode'))

        if result[u'КАТ'] == '':
            result[u'КАТ'] = u'Д'
            self.log( u'ВНИМАНИЕ: Отсутствуют данные о социальной категории'\
                u' пациента %s %s %s %s г.р.' % (
                result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)

        # Наименование страховщика (по полису)
        # 100 Русские буквы, допускается символы "пробел", "-" , "кавычки", "точка"
        # Обязательное поле
        result[u'СМО'] = forceString(record.value('insurerName'))[:100]
        # ОГРН СМО, выдавшей полис ОМС
        # 15 Арабские цифры. Заполнение ОГРН СМО, выдавшей полис ОМС, производится
        # с помощью данных соответствующего поля справочника СМО, передаваемого
        # в МО Фондом. В случае невозможности получения сведений об ОГРН СМО,
        # выдавшей полис ОМС, поле не заполняется
        # Обязательное поле, для реестров, содержащих сведения о медицинской помощи,
        # оказанной лицам, застрахованным вне территории Архангельской области
        result[u'ОГРН_С'] = forceString(record.value('insurerOGRN'))[:15]
        # Серия полиса
        # 15 Серия полиса ОМС. Заполняется строго в соответствии с серией полиса,
        # без искажений, сокращений и добавлений. Для Арх.обл. 3 символа
        # Обязательное поле, при наличии в полисе
        result[u'С_П'] = forceString(record.value('policySerial'))[:15]
        # Номер полиса
        # 16 Только цифры. Номер полиса ОМС, заполняется строго в
        # соответствии с номером полиса, без сокращений и добавлений.
        # Для Арх.обл. 5 символов
        result[u'Н_П'] = forceString(record.value('policyNumber'))[:16]
        #Код территории, на которой застрахован пациент
        #8 В соответствии с Таблица 15
        # Обязательное поле, для реестров, содержащих сведения о медицинской помощи,
        # оказанной лицам, застрахованным вне территории Архангельской области
        insurerArea = forceString(record.value('insurerArea'))
        result[u'КТС'] = self.getKLADRInfis(insurerArea if insurerArea else KLADRCode)[:8]
        # Дата начала действия полиса повторяет указанную в полисе.
        # Дата начала действия полиса приравнивается к дате выдачи полиса.
        # 10 Арабские цифры по формату дд/мм/гггг. Разделитель "/"
        # Обязательное поле, для реестров, содержащих сведения о медицинской помощи,
        # оказанной лицам, застрахованным вне территории Архангельской области
        result[u'ДПН'] = forceDate(record.value('policyBegDate')).toString('dd/MM/yyyy')
        # Дата окончания действия полиса повторяет указанную в полисе.
        # Если полис бессрочный (не указана дата окончания действия), поле не заполняется.
        # Если поле ИСХ (исход заболевания) указан код «3», то в поле ДПО записывается дата смерти пациента
        # 10 Арабские цифры по формату дд/мм/гггг. Разделитель "/
        result[u'ДПО'] = forceDate(record.value('policyEndDate')).toString('dd/MM/yyyy')
        #Место работы/учебы пациента
        # 150 Русские буквы и арабские цифры (без применения латинских букв и цифр),
        # заполняется, если в поле КАТ указываются коды СУ, Р.

        if not forceRef(record.value('policyId')):
            self.log( u'<b><font color=orange>ВНИМАНИЕ</font></b>:' \
                        u' Отсутствуют данные об актуальном полисе'\
                        u' пациента %s %s %s %s г.р. Пишем данные о последнем.' % (
                        result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)

            if not forceRef(record.value('lastPolicyId')):
                self.log(u'<b><font color=red>ОШИБКА</font></b>:' \
                        u' Отсутствуют данные о полседнем полисе.')

            result[u'СМО'] = forceString(record.value('lastInsurerName'))[:100]
            result[u'ОГРН_С'] = forceString(record.value('lastInsurerOGRN'))[:15]
            result[u'С_П'] = forceString(record.value('lastPolicySerial'))[:15]
            result[u'Н_П'] = forceString(record.value('lastPolicyNumber'))[:16]
            insurerArea = forceString(record.value('insurerArea'))
            result[u'КТС'] = self.getKLADRInfis(insurerArea if insurerArea else KLADRCode)[:8]
            result[u'ДПН'] = forceDate(record.value('lastPolicyBegDate')).toString('dd/MM/yyyy')
            result[u'ДПО'] = forceDate(record.value('lastPolicyEndDate')).toString('dd/MM/yyyy')

        if result[u'КАТ'] in (u'СУ',  u'Р'):
            result[u'МРУ'] = forceString(record.value('workName'))

            if (result[u'МРУ'] == '') :
                self.log( u'ВНИМАНИЕ: Не указано место работы'\
                    u' пациента %s %s %s %s г.р.' % (
                    result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)

        # Код вида медицинской помощи
        # 2 Арабские цифры, в соответствии с Таблица 7
        medicalAidTypeCode = forceString(record.value('medicalAidTypeCode'))[:2]
        eventTypeCode= forceString(record.value('eventTypeCode'))
        result[u'ВМП'] = eventTypeCode[:2]
        #Код МО (подразделения МО), оказавшей медицинскую помощь
        #8 Код по Таблица 17 Обязательное поле
        result[u'МПЛПУ'] = self.currentOrgCode
        # Идентификатор случая лечения. Для объединения всех записей
        # по законченному случаю АПП
        #9 Арабские цифры, составляют число идентификатора,
        # Обязательное поле  Уникальное для каждого законченного случая АПП в базе данных МО
        # для записей об амбулаторно-поликлинической помощи (АПП)

        eventId = forceString(record.value('eventId'))
        result[u'ИДС'] = eventId[-9:]

        if len(eventId) > 9:
            self.log( u'ВНИМАНИЕ: Идентификатор случая лечения (eventId) больше 9 символов.'\
                u' Пациент %s %s %s %s г.р.' % (
                result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)

        medicalAidProfileCode = forceString(record.value('medicalAidProfileCode'))

        # Дата начала лечения
        # 10 Арабские цифры по формату дд/мм/гггг. Разделитель "/"
        # Обязательное поле
        result[u'ДНЛ'] = forceDate(record.value('actionBegDate' if eventTypeCode == '5' else 'begDate')).toString('dd/MM/yyyy')
        # Дата окончания лечения
        #10 Арабские цифры по формату дд/мм/гггг. Разделитель "/"
        # Обязательное поле
        result[u'ДКЛ'] = forceDate(record.value('actionEndDate' if eventTypeCode == '5' else 'endDate')).toString('dd/MM/yyyy')
        # Дата открытия больничного листа (БЛ), для работающих граждан
        # 10 Дата в формате ДД/ММ/ГГГГ. В случае открытия БЛ в месяце, предшествующем отчетному,
        # в качестве ДОБ проставляется 1-е число отчетного месяца.
        result[u'ДОБ'] = forceDate(record.value('tempInvalidBegDate')).toString('dd/MM/yyyy')
        # Дата закрытия больничного листа (БЛ), для работающих граждан
        # 10 Дата в формате ДД/ММ/ГГГГ. В случае, когда БЛ не закрыт в отчетном месяце,
        # в качестве ДЗБ проставляется последнее число отчетного месяца.
        # Обязательное поле для реестров по Постановлению Правительства РФ от 30.12.2006 №864
        result[u'ДЗБ'] = forceDate(record.value('tempInvalidEndDate')).toString('dd/MM/yyyy')
        #Серия и номер больничного листа, указанного в полях ДОБ и ДЗБ
        #15 Серия и номер БЛ, разделѐнные одним символом пробела.
        # Заполняются строго в соответствии с серией и номером, нанесёнными
        # на бланке БЛ, без сокращений и добавлений.
        # Обязательное поле для реестров по Постановлению Правительства РФ от 30.12.2006 №864
        result[u'НБЛ'] = forceString(record.value('tempInvalidSN'))[:15]
        #Код исхода лечения
        #1 Цифры, в соответствии с Таблица 8
        # Обязательное поле для всех видов медицинской помощи
        result[u'ИСХ'] = forceString(record.value('resultCode'))[:1]
        #Диагноз по МКБ основной
        #7 Латинская буква, цифры, знак "."
        # Обязательное поле
        result[u'ДИА'] = forceString(record.value('MKB'))[:7]
        # Дополнительный диагноз
        # 7 Латинская буква, цифры, знак "."
        # Не обязательное поле, заполняется при наличии доп. диагноза
        result[u'ДИ1'] = forceString(record.value('AccMKB'))[:7]
        # Страховой номер индивидуального лицевого счета в ПФР врача
        #15 Цифры, разделенные дефисами и пробелом, в соответствии с
        # форматом СНИЛС ###-###-### ##
        # Обязательное поле (см. прим. 1)
        result[u'ССВ'] = formatSNILS(forceString(record.value('personSNILS')))[:15]
        #Код специальности
        # 3 Код в соответствии с Таблица 10
        # Обязательное поле
        result[u'СПЦ'] = forceString(record.value('postRegionalCode'))[:3]
        #Код специальности врача или среднего медработника соответствии
        # с федеральным классификатором
        #9 Код в соответствии с Таблица 11
        # Обязательное поле, для реестров, содержащих сведения о медицинской
        # помощи, оказанной лицам, застрахованным вне территории Архангельской области
        result[u'КСВ'] = forceString(record.value('personOKSOCode')) #[:3]
        # Утвержденный тариф
        #10 Арабские цифры, разделитель целой и дробной части - символ "точка"
        # Обязательное поле
        price = forceDouble(record.value('price'))
        result[u'ТАР'] = (u'%10.2f'% (round(price, 2))).strip()
        #Вид тарифной единицы
        #Код тарифной единицы по справочнику
        #2 Арабские цифры, в соответствии с Таблица 9
        # Обязательное поле
        result[u'ВТЕ'] = forceString(record.value('medicalAidUnitCode'))[:2]
        #Код тарифа услуги
        #3 Одна заглавная латинская буква и 2 арабские цифры – код из поля USL_KOD Таблица 22
        # Обязательное поле для записи об услугах центров здоровья
        #result[u'КТУ'] = forceString(record.value('serviceCode'))
        # Количество дней в стационаре, количество УЕТ и т.п.
        #3 Арабские цифры, разделитель целой и дробной части - символ "точка"
        # Обязательное поле
        amount = forceDouble(record.value('amount'))
        uet = forceDouble(record.value('uet'))
        result[u'ЧТЕ'] = (u'%3.2f' % round(uet if uet else amount, 2)).strip()
        # Код вида стоматологической услуги
        # Код из справочника стоматологических услуг
        # 8 Код в соответствии с Таблица 21
        # Обязательное для стоматологической помощи. На каждый вид услуги формируется новая запись
        if result[u'ВМП'] == '5':
            result[u'КСУ'] = forceString(record.value('serviceCode'))
            #Число оказанных стоматологических услуг, приведенных в поле КСУ на одном приеме
            #3 Арабские цифры
            # Обязательное для стоматологической помощи. На каждый вид услуги формируется новая запись
            result[u'ЧСУ'] = forceString(record.value('amount'))[:3]
#            result[u'ЧТЕ'] = u'%3.2f' % (forceDouble(record.value('amount'))*forceDouble(record.value('uet')))

        # Код профиля отделения (койки)
        #5 Код в соответствии с Таблица 19
        # Обязательное поле
        serviceGroupId = forceRef(record.value('serviceGroupId'))
        if serviceGroupId and self.getServiceGroupCode(serviceGroupId) == '011':
            result[u'КМП'] = forceString(record.value('serviceCode'))[:5]

        if not result.get(u'КМП') :
            actionId = forceRef(record.value('hospActionId'))

            if actionId:
                action = CAction()
                action.setRecord(self.db.getRecord('Action', '*', actionId))
                bedId = forceRef(action[u'койка'])

                if bedId:
                    bedProfileId = forceRef(self.db.translate('OrgStructure_HospitalBed', 'id', bedId, 'profile_id'))

                    if bedProfileId:
                        bedServiceId = forceRef(self.db.translate('rbHospitalBedProfile', 'id', bedProfileId, 'service_id'))

                        if bedServiceId:
                            result[u'КМП'] = forceString(self.db.translate(
                                'rbService', 'id', bedServiceId, 'infis'))[:5]

        # Код профиля медицинской помощи
        #2 Арабские цифры, в соответствии с Таблица 20
        # Обязательное поле, для реестров, содержащих сведения о медицинской помощи, оказанной лицам,
        # застрахованным вне территории Архангельской области
        result[u'КПМП'] = forceString(record.value('personRegionalCode'))[:2]
        #Сумма к оплате
        #10 Арабские цифры, разделитель целой и дробной части - символ "точка"
        #Обязательное поле

        sum = price * amount
        if uet:
            sum = uet * price

        # борьба с округлениями
        if round(sum * 1000 % 10) > 4:
            sum += 0.0001

        result[u'СУМ'] = (u'%10.2f' % sum).strip()
        #Признак особый случай
        #Набор цифр, в соответствии с Таблица 12
        #3 Цифры Обязательно заполняется при наличии особого случая, описанного в Таблица 12
        result[u'ОСС'] = u''

        #1	Пациент при обращении в ЛПУ предъявил только паспорт
        if not result[u'С_П'] and not result[u'Н_П'] and result[u'КВД'] == '2':
            result[u'ОСС'] += '1'

        #2	Пациент при обращении в ЛПУ предъявил иной документ, удостоверяющий личность
        if result[u'КВД'] and (not result[u'КВД'] in ('1','2')):
            result[u'ОСС'] += '2'

        #3	МП оказана новорожденному
        age = forceInt(record.value('clientAge'))
        if age < 1:
            result[u'ОСС'] += '3'

        #4	Предъявлен паспорт одного из родителей
        if age < 14 and result[u'КВД'] in ('1','2'):
            result[u'ОСС'] += '4'

        #5	По документу отсутсвует отчество
        if not result[u'ОТЧ']:
            result[u'ОСС'] += '5'

        if forceBool(record.value('specialCaseAction')) and self.contractModern:
            result[u'ОСС'] += '9'

        result[u'ОСС'] += forceString(record.value('specialCaseCode'))

        if result[u'ОСС']:
            result[u'ОСС'] = result[u'ОСС'][:3]
        #6	Пострадавший от противоправных действий
        #7	Диспансеризация детей, находящихся в трудной жизненной ситуации
        #8	Пострадавший от несчастного случая на производстве


        if not record.isNull('oldAccountItemId'):
            # Наименование информационного файла
            # Имя предыдущего Реестра, в который включалась запись,
            # 12 Латинские буквы и цифры
            # Обязательное поле для записи, выставляющейся на оплату повторно
            result[u'НИФ'] = self.getAccountFileName(forceRef(record.value('oldAccountItemId')))[:12]
            #Код записи (УКЛ) в предыдущем Реестре
            #Уникальный код записи в реестре, для обеспечения ссылочной целостности
            #7 Только цифры, не может повторяться в одном реестре
            # Обязательное поле для записи, выставляющейся на оплату повторно
            result[u'РКЛ'] = (forceString(record.value('oldAccountItemId'))+'00')[-7:]
            # Примечание Заполняется в случае, когда пациент пострадал от противоправных действий.
            #160 указывается дата и регистрационный номер в журнале регистрации этих случаев

        result[u'ПРИ'] = forceString(record.value('eventNote'))[:150]
        result[u'СТД'] = forceString(record.value('stdActionCode'))

        # ДД
        if self.exportDD and (eventTypeId in self.eventTypesDD):
            self.log(u'Экпорт информации о ДД по событию %s' % eventId)
            # Код характера заболевания, заполняется в случае проведения
            # дополнительной диспансеризации работающего населения (Постановление Правительства № 876)
            # 1 Арабские цифры, в соответствии с Таблица 23
            # Обязательное при формировании реестра по доп. диспансеризации
            result[u'ХАР'] = forceString(record.value('characterCode'))[:1]

            diagDates = self.getDiagDates(eventId, self.ddSpecialityMap)
            analysisDates = self.getAnalysisDates(eventId, self.ddAnalysisMap)

            for dicts in (diagDates,  analysisDates):
                for (key, val) in dicts.iteritems():
                    result[key] = val.toString('dd/MM/yyyy')

        # ДС
        if self.exportDS and (eventTypeId in self.eventTypesDS):
            self.log(u'Экпорт информации о ДС по событию %s' % eventId)

            diagDates = self.getDiagDates(eventId, self.dsSpecialityMap)
            analysisDates = self.getAnalysisDates(eventId, self.dsAnalysisMap)

            for dicts in (diagDates,  analysisDates):
                for (key, val) in dicts.iteritems():
                    result[key] = val.toString('dd/MM/yyyy')

        if eventTypeCode == '2' and self.eventSplit:
            self.storeVisitRecords(result, txt, eventId)
        else:
            self.storeRecord(result,  txt)


    def storeVisitRecords(self, result, txt, eventId):
        visitInfo = self.getVisitInfo(eventId)
        amount = forceDouble(result[u'ЧТЕ'])
        visitCount = forceDouble(len(visitInfo))

        if amount != visitCount:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                       u' Количество визитов %.0f не совпадает с ЧТЕ %.02f.'
                       u' Пациент %s %s %s %s г.р.' % (visitCount,  amount,
                result[u'ФАМ'], result[u'ИМЯ'], result[u'ОТЧ'], result[u'Д_Р']),  True)

        result[u'ЧТЕ'] = '1'
        n = 0
        id = forceInt(result[u'УКЛ'])
        result[u'СУМ'] = result[u'ТАР']

        for x in visitInfo:
            date = x.toString('dd/MM/yyyy')
            result[u'ДНЛ'] = date
            result[u'ДКЛ'] = date
            result[u'УКЛ'] = ('%d' % (id + n))[-7:]
            n += 1
            self.storeRecord(result, txt)


    def getVisitInfo(self, eventId):
        result = []
        monthStr = self.accDate.toString('yyyy-MM')

        stmt = '''SELECT `date`
        FROM Visit
        WHERE Visit.event_id=%s
            AND SUBSTR(`date`,1,7)='%s'
            LIMIT 100''' % (eventId, monthStr)

        query = self.db.query(stmt)

        if query:
            while query.next():
                record = query.record()
                if record:
                    result.append(forceDate(record.value(0)))

        return result


    def storeRecord(self, row,  stream):
        stream  << '@@@\n'
        flag = False

        for (key, val) in row.items():
            if val:
                stream << (u'%s:%s\n'% (key, val))[:250]
                flag = True

        if flag:
            self.recNum += 1
            self.totalSum += forceDouble(row.get(u'СУМ', 0))


    def writeTextHeader(self,  txtStream):
        #  признак заголовка (группа символов «ЗАГ:»);
        #– код организации, передающей информацию;
        #– код организации, которой предназначена информация;
        #– код вида реестра оказанной медицинской помощи (Таблица 5);
        #– код, определяющий кодировку символов в файле:
        #– 1 – DOS кодировка,
        #– 2 – Windows кодировка;
        #– дату подготовки информации в формате ДД/ММ/ГГГГ;
        #– код типа файла:
        #– 1 – Реестр, сформированный МО (файл RLU),
        #– 2 – Реестр экспертизы, сформированный СМО (файл ELU).
        # ЗАГ:29000100,29000000,1,1,05/07/2007,1
        date, number,  financeCode,  contractNum, \
        contractDate,  orgName,  orgAddr, orgCode, grp = \
            getAccountInfo(self.parent.accountId)

        lpuCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
        txtStream << u'ЗАГ:%s,%s,%d,1,%s,1\n' % \
            (lpuCode, orgCode, self.registryType, date.toString('dd/MM/yyyy'))


    def writeTextFooter(self,  txtStream):
        #        признак окончания (группа символов «КОН:»);
        #– число записей в файле;
        #– Для файлов RLU - общая сумма, предъявленная к оплате по файлу; для файлов ELU общая сумма, принятая к оплате по файлу.
        #Число записей отделяется от суммы запятой, для отделения дробной части в сумме используется символ «точка».
        txtStream << u'КОН:%d,%.2f\n' % (self.recNum-1, round(self.totalSum, 2))

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

    kladrInfisCache = {}

    def getKLADRInfis(self, code):
        u""" Возвращает название из КЛАДР по коду."""
        result = ''

        if code != '':
            result = self.kladrInfisCache.get(code)

            if not result:
                result = forceString(QtGui.qApp.db.translate('kladr.KLADR','CODE',
                    code.ljust(13, '0'),'infis'))
                self.kladrInfisCache[code] = result

        return result
# *****************************************************************************************

    kladrSocrInfisCache = {}

    def getSOCRInfisCode(self, code):
        u""" Возвращает региональный инфис код по КЛАДР коду."""
        result = ''

        if code != '':
            result = self.kladrSocrInfisCache.get(code)

            if not result:
                stmt = '''
                    SELECT  kladr.SOCRBASE.infisCODE
                        FROM kladr.KLADR
                        LEFT JOIN kladr.SOCRBASE ON kladr.SOCRBASE.SCNAME =kladr.KLADR.SOCR
                        WHERE kladr.KLADR.CODE = '%s' ''' % (code.ljust(13, '0'))

                query = QtGui.qApp.db.query(stmt)

                if query.next():
                    record = query.record()
                    result = forceString(record.value(0))

                self.kladrSocrInfisCache[code] = result

        return result

# *****************************************************************************************

    kladrSocrCache = {}

    def getSOCR(self, code):
        u""" Возвращает региональный инфис код по КЛАДР коду."""
        result = ''

        if code != '':
            result = self.kladrSocrCache.get(code)

            result = forceString(QtGui.qApp.db.translate('kladr.KLADR', 'CODE', code.ljust(13, '0'), 'SOCR', idFieldName='CODE'))
            self.kladrSocrCache[code] = result

        return result

# *****************************************************************************************

    serviceGroupCodeCache = {}

    def getServiceGroupCode(self, id):
        u"""Возвращает код услуги по id."""
        result = self.serviceGroupCodeCache.get(id,  -1)

        if result == -1:
            result = forceString(QtGui.qApp.db.translate('rbServiceGroup', 'id', id, 'code'))
            self.serviceGroupCodeCache[id] = result

        return result

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
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R29NativeExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        success = False
        srcTxt = self.wizard().getFullTxtFileName()

        (root,  ext) = os.path.splitext(srcTxt)
        zipName = root + '.7z'

        try:
            compressFileIn7Zip(srcTxt, zipName)
        except CException, e:
            QtGui.QMessageBox.critical( self,
                u'Ошибка запуска архиватора',
                unicode(e), QtGui.QMessageBox.Close)
            return False

        dstDir = forceStringEx(self.edtDir.text())

        if not os.path.exists(dstDir):
            os.makedirs(dstDir)

        dstTxt = os.path.join(dstDir, os.path.basename(zipName))
        success, result = QtGui.qApp.call(self, shutil.move, (zipName, dstTxt))

        if success:
            QtGui.qApp.preferences.appPrefs['R29NativeExportDir'] = toVariant(self.edtDir.text())
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
                u'Выберите директорию для сохранения файла выгрузки',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
