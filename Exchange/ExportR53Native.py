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
from Exchange.Utils import CExportHelperMixin, compressFileInZip

from Ui_ExportR53NativePage1 import Ui_ExportPage1
from Ui_ExportR53NativePage2 import Ui_ExportPage2

serviceInfoExportVersion = '1.0'

def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'settleDate, number, exposeDate, contract_id, payer_id, date', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('settleDate'))
        aDate  = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        strNumber = forceString(accountRecord.value('number')).strip()
        if strNumber.isdigit():
            number = forceInt(strNumber)
        else:
            # убираем номер договора с дефисом, если они есть в номере
            i = len(strNumber) - 1
            while (i>0 and strNumber[i].isdigit()):
                i -= 1

            number = forceInt(strNumber[i+1:] if strNumber[i+1:] != '' else 0)

        contractId = forceRef(accountRecord.value('contract_id'))
        payerId = forceRef(accountRecord.value('payer_id'))
    else:
        date = exposeDate = contractId = payerId = aDate = None
        number = 0
    return date, number, exposeDate, contractId,  payerId,  aDate


def exportR53Native(widget, accountId, accountItemIdList):
    wizard = CExportWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


# *****************************************************************************************

class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта в Новгородской области')
        self.tmpDir = ''
        self.dbfFileName = ''
        self.dbfLocalFileName = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId, payerId,  aDate = getAccountInfo(accountId)
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
            self.tmpDir = QtGui.qApp.getTmpDir('R53OMS')
        return self.tmpDir


    def getFullDbfFileName(self):
        # R + RSTRAAAYYYYNN.zip AAA - Организация код МИАЦ. YYYY - год. NN - номер счёта.

        if not self.dbfFileName:

            if self.page1.cmbExportType.currentIndex() == CExportPage1.exportTypeDMS:
                (date, number, exposeDate, contractId,  payerId,  aDate) = getAccountInfo(self.accountId)
                self.dbfFileName = os.path.join(self.getTmpDir(), '%d_%s.dbf' %(
                    number, forceString(date.toString('ddMMyyyy'))))
            else:
                lpuCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))
                (date, number, exposeDate, contractId,  payerId, aDate) = getAccountInfo(self.accountId)

                year = forceString(exposeDate.year() if exposeDate.isValid() else date.year())
                self.dbfFileName = os.path.join(self.getTmpDir(), 'RSTR%s%s%02d.dbf' % (
                        lpuCode, year, number))

        return self.dbfFileName


    def getFullXmlFileName(self):
        u"""Ryyyymm-MMMPP-SSS-xxxxx.zip
            yyyymm - год, месяц конца отчетного периода
            MMM - код МО
            PP - код подразделения (при отсутствии подразделения = 00)
            SSS - код СМО(НОФОМС) (для НОФОМС=000)
            xxxx - номер счета"""
        if not self.dbfLocalFileName:
            lpuInfis = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))
            orgStructCode = forceString(QtGui.qApp.db.translate(
                'OrgStructure', 'id', QtGui.qApp.currentOrgStructureId(), 'infisCode'))
            (date, number, exposeDate, contractId,  payerId,  aDate) = getAccountInfo(self.accountId)
            year = forceString(exposeDate.year() if exposeDate.isValid() else date.year())

            if self.page1.cmbExportType.currentIndex() == CExportPage1.exportTypeTFOMS:
                payerCode = '000'
                number = forceInt(self.page1.edtRegistryNumber.value())
                prefix = 'F'
            elif self.page1.cmbExportType.currentIndex() == CExportPage1.exportTypeTFOMS2011_10:
                prefix = 'G'
                payerCode = '000'
            elif self.page1.cmbExportType.currentIndex() == CExportPage1.exportTypeServiceInfo:
                prefix = 'ServiceInfo'
                number = forceInt(self.page1.edtRegistryNumber.value())
                payerCode = '000'
            else:
                prefix = 'R'
                payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'infisCode'))

            self.dbfLocalFileName = os.path.join(self.getTmpDir(), \
                '%s%s-%s%s-%s-%05d.xml' % (prefix, date.toString('yyyyMM'), lpuInfis, \
                    orgStructCode if orgStructCode else '00', payerCode, number))
        return self.dbfLocalFileName


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

class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1, CExportHelperMixin):
    sexMap = {1: u'М',  2: u'Ж'}
    exportTypeSMO = 0
    exportTypeInternal = 1
    exportTypeTFOMS = 2
    exportTypeDMS = 3
    exportTypeTFOMS2011_10 = 4
    exportTypeServiceInfo = 5

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        CExportHelperMixin.__init__(self)
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
        self.recNum= 0
        self.ignoreErrors = forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53IgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53VerboseLog', False)))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.edtRegistryNumber.setValue(forceInt(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53RegistryNumber', 0))+1)
        self.cmbExportType.setCurrentIndex(forceInt(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53ExportType', 0)))
        self.edtBegDate.canBeEmpty()
        self.edtEndDate.canBeEmpty()
        self.edtBegDate.setDate(forceDate(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53BegDate', QDate())))
        self.edtEndDate.setDate(forceDate(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53EndDate', QDate())))
        self.chkGroupByService.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53GroupByService', True)))
        self.edtServiceInfoFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR53ServiceInfoFileName', '')))
        self.checkWidgets(self.cmbExportType.currentIndex())


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.cmbExportType.setEnabled(not flag)
        self.edtBegDate.setEnabled(not flag)
        self.edtEndDate.setEnabled(not flag)
        self.edtRegistryNumber.setEnabled(not flag)
        self.chkGroupByService.setEnabled(not flag)
        self.edtServiceInfoFileName.setEnabled(not flag)
        self.btnSelectServiceInfoFileName.setEnabled(not flag)
        if not flag:
            self.checkWidgets(self.cmbExportType.currentIndex())


    def log(self, str, forceLog = False):
        if self.chkVerboseLog.isChecked() or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self, exportType):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        if exportType in (self.exportTypeInternal, self.exportTypeTFOMS,
                                self.exportTypeTFOMS2011_10, self.exportTypeServiceInfo):
            output = self.createXML()
        elif exportType == self.exportTypeDMS:
            output = self.createDbfDMS()
        else:
           output = self.createDbf()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQueryDMS() if exportType == self.exportTypeDMS else self.createQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return output, query


    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            QtGui.qApp.preferences.appPrefs['ExportR53IgnoreErrors'] = \
                    toVariant(self.chkIgnoreErrors.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR53VerboseLog'] = \
                    toVariant(self.chkVerboseLog.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR53ExportType'] = \
                    toVariant(self.cmbExportType.currentIndex())
            QtGui.qApp.preferences.appPrefs['ExportR53BegDate'] = \
                    toVariant(self.edtBegDate.date())
            QtGui.qApp.preferences.appPrefs['ExportR53EndDate'] = \
                    toVariant(self.edtEndDate.date())
            QtGui.qApp.preferences.appPrefs['ExportR53GroupByService'] = \
                    toVariant(self.chkGroupByService.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR53ServiceInfoFileName'] = \
                    toVariant(self.edtServiceInfoFileName.text())
            self.done = True
            self.cmbExportType.setEnabled(False)
            self.emit(QtCore.SIGNAL('completeChanged()'))

# *****************************************************************************************

    def getFirstAccountInfo(self, begDate, endDate):
        db = QtGui.qApp.db
        table = db.table('Account')
        record = QtGui.qApp.db.getRecordEx(table, 'settleDate, number', table['settleDate'].between(begDate, endDate))

        if record:
            date = forceDate(record.value(0))
            strNumber = forceString(record.value('number')).strip()

            if strNumber.isdigit():
                number = forceInt(strNumber)
            else:
                # убираем номер договора с дефисом, если они есть в номере
                i = len(strNumber) - 1
                while (i>0 and strNumber[i].isdigit()):
                    i -= 1

                number = forceInt(strNumber[i+1:] if strNumber[i+1:] != '' else 0)

            #number = forceInt(record.value(1))
        else:
            date = QDate()
            number = 0

        return date, number


# *****************************************************************************************

    def createQueryDMS(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        stmt = """SELECT
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.birthDate,
            IF(Action.MKB != '', Action.MKB, Diagnosis.MKB) AS aMKB,
            IF(Account_Item.service_id IS NOT NULL,
                rbItemService.infis,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                ) AS serviceCode,
            IF(Account_Item.service_id IS NOT NULL,
                rbItemService.name,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.name, rbEventService.name)
                ) AS serviceName,
            Event.execDate AS endDate,
            Visit.date AS visitDate,
            Action.endDate AS actionDate,
            Account_Item.amount,
            Account_Item.price,
            Account_Item.`sum`,
            Account_Item.event_id,
            ClientPolicy.serial AS policySerial,
            ClientPolicy.number AS policyNumber
        FROM Account_Item
        LEFT JOIN Action ON Action.id = Account_Item.action_id
        LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
        LEFT JOIN Event  ON Event.id  = Account_Item.event_id
        LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
        LEFT JOIN Client ON Client.id = Event.client_id
        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
            ClientPolicy.id = (SELECT MAX(CP.id)
                FROM   ClientPolicy AS CP
                LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                WHERE  CP.client_id = Client.id AND CP.deleted=0 AND CPT.code='3')
        LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                  AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1', '2'))
                                  AND Diagnostic.person_id = Event.execPerson_id AND Diagnostic.deleted = 0)
        LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
        LEFT JOIN EventType ON EventType.id = Event.eventType_id
        LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
        LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
        LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
        WHERE Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s ORDER BY Client.lastName, Client.firstName, Client.patrName, endDate""" % tableAccountItem['id'].inlist(self.idList)
        query = db.query(stmt)
        return query

# *****************************************************************************************

    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        if self.cmbExportType.currentIndex()  in (self.exportTypeTFOMS, self.exportTypeServiceInfo):
            begDate = self.edtBegDate.date()
            endDate = self.edtEndDate.date()

            stmt= """SELECT Account_Item.id
                    FROM Account
                    LEFT JOIN Account_Item ON Account_Item.master_id = Account.id
                    LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
                    LEFT JOIN Contract ON Account.contract_id = Contract.id
                    LEFT JOIN rbFinance ON Contract.finance_id = rbFinance.id
                    WHERE Account.settleDate BETWEEN '%s' AND '%s'
                    AND rbFinance.code = '2'
                    AND Account_Item.reexposeItem_id IS NULL
                    AND (Account_Item.date IS NULL
                    OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0))
                """ % (begDate.toString(QtCore.Qt.ISODate) if begDate.isValid() else '0000-00-00',
                          endDate.toString(QtCore.Qt.ISODate) if endDate.isValid() else '2999-12-31')

            query = db.query(stmt)
            idList = []
            while query.next():
                record = query.record()
                if record:
                    idList.append(forceRef(record.value(0)))
        else:
            idList = self.idList

        cond = tableAccountItem['id'].inlist(idList)

        if self.chkGroupByService.isChecked():
            sumStr = """SUM(Account_Item.`sum`) AS `sum`,
                SUM(Account_Item.amount) AS amount,
                SUM(LEAST(IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                            Account_Item.sum)) AS federalSum,"""
            cond += ' GROUP BY `Account_Item`.`event_id`, serviceId'
        else:
            sumStr = """Account_Item.`sum` AS `sum`,
                Account_Item.amount AS amount,
                 LEAST(IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                            Account_Item.sum) AS federalSum,"""

        stmt = """SELECT
                Account_Item.id AS accountItemId,
                Account_Item.event_id  AS event_id,
                Account_Item.visit_id,
                Account_Item.action_id,
                Account_Item.service_id,
                Event.client_id        AS client_id,
                Client.lastName,
                Client.firstName,
                Client.patrName,
                Client.birthDate       AS birthDate,
                Client.sex AS sex,
                Client.SNILS AS SNILS,
                Client.birthPlace AS birthPlace,
                age(Client.birthDate, Event.execDate) as clientAge,
                CONCAT(ClientPolicy.serial, ' ', ClientPolicy.number) AS policySN,
                ClientPolicy.serial AS policySerial,
                ClientPolicy.number AS policyNumber,
                ClientPolicy.begDate   AS policyBegDate,
                ClientPolicy.endDate   AS policyEndDate,
                rbPolicyKind.regionalCode AS policyKindCode,
                rbPolicyKind.federalCode AS policyKindFederalCode,
                Insurer.OGRN AS insurerOGRN,
                Insurer.OKATO AS insurerOKATO,
                Insurer.area AS insurerArea,
                ClientDocument.serial  AS documentSerial,
                ClientDocument.number  AS documentNumber,
                ClientDocument.date AS documentDate,
                ClientDocument.origin,
                rbDocumentType.regionalCode AS documentRegionalCode,
                rbDocumentType.federalCode AS documentFederalCode,
                rbDocumentType.code AS documentTypeCode,
                kladr.KLADR.infis AS placeCode,
                kladr.KLADR.OCATD AS placeOKATO,
                kladr.KLADR.NAME AS cityName,
                kladr.SOCRBASE.infisCode AS streetType,
                kladr.STREET.NAME AS streetName,
                RegAddressHouse.number AS number,
                RegAddressHouse.corpus AS corpus,
                RegAddressHouse.KLADRCode AS regKLADRCode,
                RegAddress.flat AS flat,
                IF(work.title IS NOT NULL,
                    work.title, ClientWork.freeInput) AS `workName`,
                IF(Account_Item.visit_id IS NOT NULL, Visit.person_id,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, Action.person_id, Action.setPerson_id), Event.execPerson_id)
                ) AS execPersonId,
                Diagnosis.MKB          AS MKB,
                Event.setDate          AS begDate,
                Event.execDate         AS endDate,
                Contract_Tariff.federalPrice AS federalPrice,
                Account_Item.price AS price, %s
                Person.regionalCode AS personRegionalCode,
                    rbDiagnosticResult.regionalCode AS resultCode,
                    rbDiagnosticResult.federalCode AS resultFederalCode,
                rbMedicalAidType.code AS medicalAidTypeCode,
                rbMedicalAidType.regionalCode AS medicalAidTypeRegionalCode,
                rbMedicalAidType.federalCode AS medicalAidTypeFederalCode,
                rbMedicalAidKind.regionalCode AS medicalAidKindRegionalCode,
                rbMedicalAidKind.federalCode AS medicalAidKindFederalCode,
                Citizenship.regionalCode AS citizenshipCode,
                IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.code,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.code, EventMedicalAidProfile.code)
                  ) AS medicalAidProfileCode,
                IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.regionalCode,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.regionalCode, EventMedicalAidProfile.regionalCode)
                  ) AS medicalAidProfileRegionalCode,
                IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.federalCode,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.federalCode, EventMedicalAidProfile.federalCode)
                  ) AS medicalAidProfileFederalCode,
                IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.id,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.id, rbEventService.id)
                    ) AS serviceId,
                AccDiagnosis.MKB AS AccMKB,
                rbEventProfile.regionalCode AS eventProfileRegCode,
                rbEventProfile.code AS eventProfileCode,
                OrgStructure.infisCode AS orgStructureCode,
                rbMedicalAidUnit.name AS medicalAidUnitName,
                rbMedicalAidUnit.federalCode AS medicalAidUnitFederalCode,
                RegSOCR.infisCODE AS placeTypeCode,
                RegRegionKLADR.NAME AS regionName,
                rbEventTypePurpose.regionalCode AS eventTypePurpose,
                rbEventTypePurpose.federalCode AS eventTypePurposeFederalCode,
                Event.`order`,
                Event.id AS eventId,
                EventResult.federalCode AS eventResultFederalCode,
                EventResult.regionalCode AS eventResultRegionalCode
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
            LEFT JOIN rbPolicyKind ON ClientPolicy.policyKind_id = rbPolicyKind.id
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
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
            LEFT JOIN kladr.STREET ON kladr.STREET.CODE =RegAddressHouse.KLADRStreetCode
            LEFT JOIN kladr.KLADR ON kladr.KLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN kladr.SOCRBASE ON kladr.SOCRBASE.KOD_T_ST = (SELECT KOD_T_ST
                        FROM kladr.SOCRBASE AS SB
                        WHERE SB.SCNAME = kladr.STREET.SOCR
                        LIMIT 1)
            LEFT JOIN kladr.SOCRBASE RegSOCR ON RegSOCR.KOD_T_ST = (SELECT KOD_T_ST
                        FROM kladr.SOCRBASE AS SB
                        WHERE SB.SCNAME = kladr.KLADR.SOCR
                        LIMIT 1)
            LEFT JOIN kladr.KLADR RegRegionKLADR ON RegRegionKLADR.CODE = (
                    SELECT RPAD(LEFT(RegAddressHouse.KLADRCode,5),13,'0') LIMIT 1)
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN Diagnostic ON Diagnostic.id = (
              SELECT MAX(D.id)
              FROM Diagnostic AS D
              WHERE D.event_id = Account_Item.event_id
                AND ((D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code ='2')
                        AND D.person_id = Event.execPerson_id) OR (
                          D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='1')))
                          AND D.deleted = 0)
            LEFT JOIN ClientWork ON ClientWork.client_id=Event.client_id AND
                        ClientWork.id = (SELECT max(CW.id)
                                         FROM ClientWork AS CW
                                         WHERE CW.client_id=Client.id AND CW.deleted=0)
            LEFT JOIN Organisation AS work ON work.id=ClientWork.org_id AND work.deleted = 0
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbDiseaseCharacter ON Diagnosis.character_id = rbDiseaseCharacter.id
            LEFT JOIN rbHealthGroup ON Diagnostic.healthGroup_id = rbHealthGroup.id
            LEFT JOIN rbDispanser ON rbDispanser.id = Diagnostic.dispanser_id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
            LEFT JOIN rbMedicalAidKind ON EventType.medicalAidKind_id = rbMedicalAidKind.id
            LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
            LEFT JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
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
            LEFT JOIN Diagnostic AS AccDiagnostic ON AccDiagnostic.id = (
             SELECT id FROM Diagnostic AS AD
             WHERE AD.event_id = Account_Item.event_id AND
                AD.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='9') AND
                AD.person_id = Event.execPerson_id AND
                AD.deleted = 0 LIMIT 1)
            LEFT JOIN Diagnosis AS AccDiagnosis ON
                AccDiagnosis.id = AccDiagnostic.diagnosis_id AND
                AccDiagnosis.deleted = 0
            LEFT JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s ORDER BY `Client`.lastName, `Client`.firstName, `Client`.patrName, Event.execDate""" % (sumStr, cond)

        query = db.query(stmt)
        return query

# *****************************************************************************************

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        exportType = self.cmbExportType.currentIndex()

        if exportType == self.exportTypeTFOMS:
            begDate = self.edtBegDate.date()
            endDate = self.edtEndDate.date()

            if begDate.isValid() and endDate.isValid():
                if begDate>endDate:
                    self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Дата начала периода больше даты окончания.', True)
                    return

        lpuName = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'fullName'))
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OGRN'))

        if not lpuCode and exportType != self.exportTypeDMS:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан ОГРН', True)
            if not self.ignoreErrors:
                return

        lpuOKATO = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OKATO'))

        if not lpuCode and exportType != self.exportTypeDMS:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан ОКАТО', True)
            if not self.ignoreErrors:
                return

        out, query = self.prepareToExport(exportType)
        accDate, accNumber, exposeDate, contractId,  payerId, aDate =\
            getAccountInfo(self.parent.accountId)
        strAccNumber = accNumber if trim(accNumber) else u'б/н'
        strContractNumber = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'number')) if contractId else u'б/н'

        payerCode = None
        payerName = ''

        if payerId:
            payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'OGRN' \
                    if exportType in (self.exportTypeTFOMS, self.exportTypeInternal) \
                    else 'OKATO'))
            payerName = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'fullName'))

        if not payerCode and exportType != self.exportTypeDMS:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для плательщика не задан ОКАТО\ОГРН', True)
            if not self.ignoreErrors:
                return

        if exportType in (self.exportTypeTFOMS, self.exportTypeInternal, self.exportTypeTFOMS2011_10, self.exportTypeServiceInfo):
            process = self.processXML
        elif exportType == self.exportTypeDMS:
            process = self.processDMS
        else:
            process = self.process

        self.recNum = 1

        if self.idList:
            if exportType in (self.exportTypeTFOMS, self.exportTypeInternal,
                                        self.exportTypeTFOMS2011_10, self.exportTypeServiceInfo):
                file = out
                if exportType == self.exportTypeTFOMS2011_10:
                    out = CTFOMSXmlStreamWriter(self, exportType)
                elif exportType == self.exportTypeServiceInfo:
                    out = CServiceInfoXmlStreamWriter(self, exportType)
                else:
                    out = CMyXmlStreamWriter(self, exportType)
                out.setCodec(QtCore.QTextCodec.codecForName('cp1251'))

                if exportType in (self.exportTypeTFOMS, self.exportTypeServiceInfo):
                    begDate = self.edtBegDate.date()
                    endDate = self.edtEndDate.date()
                    accDate, accNumber = self.getFirstAccountInfo(begDate, endDate)
                    payerName = u'НОФОМС'
                else:
                    begDate = firstMonthDay(accDate)
                    endDate = lastMonthDay(accDate)

                miacCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))
                accSum = forceDouble(QtGui.qApp.db.translate(
                    'Account', 'id', self.parent.accountId, 'sum'))
                out.writeFileHeader(file, lpuName, lpuCode, payerName, payerCode,  \
                    begDate, endDate, accNumber,
                    aDate, miacCode, accSum,  accDate)
            elif exportType == self.exportTypeSMO:
                # в dbf нужны коды ОКАТО района
                payerCode = self.getRegionOKATO(payerCode)
                lpuOKATO = self.getRegionOKATO(lpuOKATO)

            # загружаем информацию о предварительном реестре для формата 2011.10
            self.preliminaryRegistryInfo = self.getPreliminaryInfo() if exportType == self.exportTypeTFOMS2011_10 else {}

            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                process(out, query.record(), lpuCode, accNumber,  aDate, lpuOKATO, payerCode)

            if exportType in (self.exportTypeTFOMS, self.exportTypeInternal,
                              self.exportTypeTFOMS2011_10, self.exportTypeServiceInfo):
                out.writeFileFooter()
                file.close()
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

        if exportType in (self.exportTypeSMO, self.exportTypeDMS):
            out.close()

# *****************************************************************************************

    def createDbf(self):
        """ Создает структуру dbf для REESTR.DBF """

        dbfName = self.parent.getFullDbfFileName()
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('C_OKATO1', 'C',	5,  0),
            ('C_OKATO2', 'C',	5,  0),
            ('OKATO_OMS', 'C',	5,  0),
            ('NUM_S', 'C',	5,  0),
            ('DATE_S', 'D'),
            ('SN_POL', 'C',	30,  0),
            ('DATE_N', 'D'),
            ('DATE_E', 'D'),
            ('FAM', 'C',	40),
            ('IM', 'C',	40),
            ('OT', 'C',	40),
            ('W', 'C',	1),
            ('DR', 'D'),
            ('STAT_P', 'N', 1),
            ('FAMP', 'C',	40),
            ('IMP', 'C',	40),
            ('OTP', 'C',	40),
            ('Q_OGRN', 'C',	15),
            ('C_OKSM', 'C',	3),
            ('C_DOC', 'N', 2),
            ('S_DOC', 'C',	9),
            ('N_DOC', 'C',	8),
            ('R_NAME', 'C',	150),
            ('Q_NP', 'N', 2),
            ('NP_NAME', 'C',	150),
            ('Q_UL', 'N', 2),
            ('UL_NAME', 'C',	150),
            ('DOM', 'C',	7),
            ('KOR', 'C',	5),
            ('KV', 'C',	5),
            ('STAT_Z', 'N', 2),
            ('PLACE_W', 'C',	150),
            ('DATE_1', 'D'),
            ('DATE_2', 'D'),
            ('Q_U', 'N', 1),
            ('PRMP', 'N', 2),
            ('PRVS', 'C',	9),
            ('DS', 'C',	7),
            ('DS_S', 'C',	7),
            ('RSLT', 'N', 2),
            ('M_OGRN', 'C',	15),
            ('S_ALL', 'N', 11, 2),
            ('N_PP', 'N', 5),
            ('I_TYPE', 'C',	8),
            ('Q_G', 'C',	7),
            ('HOSP_TYPE', 'N', 1),
            ('BR_ID','N', 2),
            ('NUM_DAY',  'N', 3),
            ('TARIF', 'N', 11, 2)
        )
        return dbf

# *****************************************************************************************

    def createDbfDMS(self):
        """ Создает структуру dbf для ДМС """

        dbfName = self.parent.getFullDbfFileName()
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('SURNAME', 'C', 30),  # фамилия
            ('NAME', 'C', 30),  # имя
            ('PATRONOMIC', 'C', 30),  #отчество
            ('BIRTHDAY', 'D'),  #дата рождения
            ('POLIS_S', 'C', 30),  #серия полиса
            ('POLIS_N', 'C', 30),  #номер полиса
            ('CODE_U', 'C', 31),  #код услуги
            ('NAME_U', 'C', 150),  #название услуги
            ('CODE_D', 'C', 7),  #код дигноза
            ('DATE', 'D'),  #дата оказания услуги
            ('TARIF', 'N', 11, 2),  #тариф
            ('AMOUNT', 'N', 6),  #кол-во услуг
            ('SUM', 'N', 11, 2),  #сумма
        )
        return dbf

# *****************************************************************************************

    def createXML(self):
        fileName = self.parent.getFullXmlFileName()
        outFile = QtCore.QFile(fileName)
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        return outFile


    def processXML(self, xml, record, codeLPU, accNumber,  accDate, lpuOKATO, payerCode):
        xml.writeRecord(record)


# *****************************************************************************************

    def process(self, dbf, record, codeLPU, accNumber,  accDate, lpuOKATO, payerOKATO):
        specialCase = []
        clientId = forceRef(record.value('client_id'))
        dbfRecord = dbf.newRecord()
        # 'C',	5,  Код ОКАТО территории, выставившей счет 	Заполнение обязательно.
        dbfRecord['C_OKATO1'] = lpuOKATO
        # 'C' 5,	Код ОКАТО территории постоянной регистрации пациента  	Заполнение обязательно.
        # В случае отсутствия постоянной регистрации пациента указывается код ОКАТО территории
        # временной регистрации по месту жительства или код ОКАТО территории регистрации по
        # месту пребывания (для иностранных граждан).
        dbfRecord['C_OKATO2'] = self.getRegionOKATO(forceString(record.value('placeOKATO')))
        # 'C' 5 Код ОКАТО территории страхования по ОМС	Заполнение обязательно.
        # Код ОКАТО территории, в которую выставляется данный счет.
        dbfRecord['OKATO_OMS'] = forceString(record.value('insurerOKATO')).ljust(5, '0')
        #, 'C',	5,  0),	#Номер счета	Заполнение обязательно.
        dbfRecord['NUM_S'] = forceString(accNumber)
        # Дата счета	Заполнение обязательно.
        dbfRecord['DATE_S'] = pyDate(accDate)
        #, 'C',	30,  0), Серия и номер полиса ОМС пациента
        # Не заполняется только при признаке «Особый случай» (Q_G),  содержащем код 1
        # (отсутствие у пациента полиса обязательного медицинского страхования) и не
        # содержащем код 2 и код 3. При статусе представителя пациента (STAT_P)
        # отличном от 0 и признаке «Особый случай». (Q_G) , содержащем, кроме кода 1,
        # код 2 или код 3 , в данном поле указываются серия и номер полиса ОМС
        # застрахованного по ОМС представителя пациента.
        dbfRecord['SN_POL'] = forceString(record.value('policySN')).strip()

        if dbfRecord['SN_POL'] == '':
            specialCase.append('1')
        else:
            # Дата начала действия полиса ОМС.
            # Не заполняется только при признаке «Особый случай» (Q_G),
            # содержащем код 1 (отсутствие у пациента полиса обязательного медицинского страхования)
            dbfRecord['DATE_N'] = pyDate(forceDate(record.value('policyBegDate')))
            #Дата окончания действия полиса ОМС. Соответствует дате окончания действия полиса
            # ОМС пациента или содержит значение 31129999 для полиса ОМС неограниченного срока
            # действия. При признаке «Особый случай» (Q_G),  содержащем код 1 (отсутствие у пациента
            # полиса обязательного медицинского страхования) поле не заполняется.
            dbfRecord['DATE_E'] = pyDate(forceDate(record.value('policyEndDate')))

        #Фамилия пациента. Не заполняется только для случаев оказания медицинской
        #помощи новорожденным до государственной регистрации рождения.
        dbfRecord['FAM'] = forceString(record.value('lastName'))
        #Имя пациента. Не заполняется только для случаев оказания медицинской
        # помощи новорожденным до государственной регистрации рождения.
        dbfRecord['IM'] = forceString(record.value('firstName'))
        #Отчество пациента. Не заполняется только для случаев оказания медицинской
        # помощи новорожденным до государственной регистрации рождения или отсутствии
        # отчества в документе, удостоверяющем личность пациента.
        dbfRecord['OT'] = forceString(record.value('patrName'))
        #Пол пациента	Заполнение обязательно. (М-мужской, Ж-женский)
        dbfRecord['W'] = self.sexMap.get(forceInt(record.value('sex')),  0)

        if dbfRecord['W']  == 0:
            return

        #Дата рождения пациента	Заполнение обязательно. Если в документе,
        # удостоверяющем личность гражданина, отсутствует число рождения,
        # то число рождения в Реестре указывается равным «01». Если в документе,
        # удостоверяющем личность гражданина, отсутствует месяц рождения, то в
        # Реестре месяц рождения указывается равным «01» (январь).
        dbfRecord['DR'] = pyDate(forceDate(record.value('birthDate')))

        representativeInfo = self.getClientRepresentativeInfo(clientId)
        age = forceInt(record.value('clientAge'))

        #Статус представителя пациента	Заполнение обязательно.
        dbfRecord['STAT_P'] = forceInt(representativeInfo.get('relationTypeCode'))
        if age < 14:
            # Фамилия родителя (представителя) пациента. Заполняется только при оказании
            # медицинской помощи ребенку до 14 лет ( в том числе новорожденному) при
            # отсутствии регистрации ребенка в качестве застрахованного по ОМС.
            dbfRecord['FAMP'] = representativeInfo.get('firstName', '')
            # Имя родителя (представителя) пациента. Заполняется только при оказании
            # медицинской помощи ребенку до 14 лет ( в том числе новорожденному)
            # при отсутствии регистрации ребенка в качестве застрахованного по ОМС.
            dbfRecord['IMP'] = representativeInfo.get('lastName', '')
            # Отчество родителя (представителя) пациента. Заполняется только при оказании
            # медицинской помощи ребенку до 14 лет ( в том числе новорожденному)  при
            # отсутствии регистрации ребенка в качестве застрахованного по ОМС. В случае
            # отсутствия отчества в документе, удостоверяющем личность представителя
            # пациента, поле не заполняется.
            dbfRecord['OTP'] = representativeInfo.get('patrName', '')

        #ОГРН СМО, выдавшей полис ОМС 	Не заполняется в случае невозможности
        #получения сведений об ОГРН СМО,  застраховавшей пациента
        dbfRecord['Q_OGRN'] = forceString(record.value('insurerOGRN'))
        # Гражданство пациента (код по классификатору ОКСМ)
        # В случае невозможности получения сведений о гражданстве пациента, поле не заполняется.
        dbfRecord['C_OKSM'] = forceString(record.value('citizenshipCode'))
        # Код типа документа, удостоверяющего личность пациента (представителя).
        # Заполнение обязательно. Для случаев оказания медицинской помощи новорожденному
        # без государственной регистрации рождения заполняется с документа, удостоверяющего
        # личность представителя пациента.
        dbfRecord['C_DOC'] = forceInt(record.value('documentRegionalCode'))
        # Серия документа, удостоверяющего личность пациента (представителя)
        # Заполнение обязательно. Для случаев оказания медицинской помощи новорожденному
        # без государственной регистрации рождения заполняется с документа, удостоверяющего
        # личность представителя пациента.
        dbfRecord['S_DOC'] = forceString(record.value('documentSerial'))
        # Номер документа, удостоверяющего личность пациента (представителя).
        # Заполнение обязательно. Для случаев оказания медицинской помощи новорожденному
        # без государственной регистрации рождения заполняется с документа, удостоверяющего
        # личность представителя пациента.
        dbfRecord['N_DOC'] = forceString(record.value('documentNumber'))
        # Наименование района по месту регистрации пациента.
        # Заполняется для населенных пунктов районного подчинения и не заполняется для районов в городах.
        dbfRecord['R_NAME'] = forceString(record.value('regionName'))
        # Код вида населенного пункта. Заполнение обязательно.
        dbfRecord['Q_NP'] = forceInt(record.value('placeTypeCode'))
        # Наименование населенного пункта по месту регистрации 	Заполнение обязательно.
        dbfRecord['NP_NAME'] = forceString(record.value('cityName'))
        # Код типа наименования улицы. В случае отсутствия сведений об улице в документе,
        # подтверждающем адрес регистрации пациента, поле не заполняется.
        dbfRecord['Q_UL'] = forceInt(record.value('streetType'))
        # Наименование улицы. В случае отсутствия сведений об улице в документе,
        # подтверждающем адрес регистрации пациента, поле не заполняется.
        dbfRecord['UL_NAME'] = forceString(record.value('streetName'))
        # Дом. В случае отсутствия сведений о номере дома в документе,
        # подтверждающем адрес регистрации пациента, поле не заполняется.
        dbfRecord['DOM'] = forceString(record.value('number'))
        # Корпус/строение. В случае отсутствия сведений о корпусе (строении) в
        # документе, подтверждающем адрес регистрации пациента, поле не заполняется.
        dbfRecord['KOR'] = forceString(record.value('corpus'))
        #Квартира/комната	В случае отсутствия сведений о номере квартиры
        #(комнаты) в документе, подтверждающем адрес регистрации пациента, поле не заполняется.
        dbfRecord['KV'] = forceString(record.value('flat'))
        #Место работы/учебы пациента. Заполняется только для статуса пациента в
        # поле STAT_Z, равном 4 (студент/учащийся) или 5 (работающий).
        dbfRecord['PLACE_W'] = forceString(record.value('workName'))
        #Статус пациента.	Заполнение обязательно. (1 – новорожденный, 2 - дошкольник,
        # 3 – ребенок до 14 лет, 4 - студент/учащийся, 5 – работающий, 6- пенсионер,
        # 7 – неработающий, 8- другое)
        status = 8

        if age < 1:
            status = 1
        elif age > 0 and age < 6:
            status = 2
        elif age >5 and age < 14:
            status = 3
        elif dbfRecord['PLACE_W'] != '':
            status = 5
        elif age > 60:
            status = 6
        elif dbfRecord['PLACE_W'] == '':
            status = 7

        dbfRecord['STAT_Z'] = status
        #Дата начала лечения/обследования 	Заполнение обязательно.
        dbfRecord['DATE_1'] = pyDate(forceDate(record.value('begDate')))
        #Дата окончания лечения/обследования	Заполнение обязательно.
        dbfRecord['DATE_2'] = pyDate(forceDate(record.value('endDate')))
        # Код условий оказания медицинской помощи. Заполнение обязательно.
        # (1 - стационарная, 2 - амбулаторно-поликлиническая, 3 – медицинская помощь,
        # оказанная в дневных стационарах всех типов)
        dbfRecord['Q_U'] = forceInt(record.value('eventProfileRegCode'))
        # Код профиля оказанной медицинской помощи 	Заполнение обязательно.
        dbfRecord['PRMP'] = forceInt(record.value('medicalAidProfileCode'))
        # Код специальности врача/ среднего мед. работника 	Заполнение обязательно.
        dbfRecord['PRVS'] = forceString(self.getSpecialityRegionalCode(forceRef(record.value('execPersonId'))))
        #Код диагноза основного заболевания (состояния) по МКБ-10 с указанием подрубрики	Заполнение обязательно.
        dbfRecord['DS'] = forceString(record.value('MKB'))
        #Код диагноза сопутствующего заболевания (состояния) по МКБ-10
        # Не заполняется в случае отсутствия сведений о сопутствующем диагнозе в медицинской документации.
        dbfRecord['DS_S'] = forceString(record.value('AccMKB'))
        # Исход заболевания. Заполнение обязательно. (1 - выписан с выздоровлением,
        # 2 - с улучшением, 3 - без перемен, 4 - с ухудшением, 5 - переведен в другое учреждение,
        # 6 - умер, 7 – другое)
        insurerArea = forceString(record.value('insurerArea'))
        isAlien = insurerArea and insurerArea[:2] != QtGui.qApp.defaultKLADR()[:2]
        dbfRecord['RSLT'] = forceInt(record.value('resultFederalCode' if isAlien else 'resultCode')) % 100
        # ОГРН ЛПУ, оказавшего медицинскую помощь 	Заполнение обязательно.
        dbfRecord['M_OGRN'] = codeLPU
        #Сумма, предъявленная к оплате (руб./коп.) 	Заполнение обязательно.
        dbfRecord['S_ALL'] = forceDouble(record.value('sum'))
        #Порядковый номер в основном счете на бумажном носителе 	Заполнение обязательно.
        dbfRecord['N_PP'] = self.recNum
        # Код причины дополнительного рассмотрения.
        # Заполнение обязательно. Для  случаев отсутствия причин
        # дополнительного рассмотрения указывается 0.
        dbfRecord['I_TYPE'] = '0'
        #Признак «Особый случай».	Если признак особый случай отсутствует, поле не заполняется.
        dbfRecord['Q_G'] = ' '.join(x for x in specialCase)
        eventProfileCode = forceString(record.value('eventProfileCode'))
        hospType = 0

        if eventProfileCode == '02':
            hospType = 0
        elif eventProfileCode in ('01', '03'):
            order = forceInt(record.value('order'))
            if order == 1:
                hospType = 4

            if order == 2:
                hospType = 3

        dbfRecord['HOSP_TYPE'] = hospType
        dbfRecord['BR_ID'] = forceInt(record.value('medicalAidProfileRegionalCode'))
        dbfRecord['NUM_DAY'] = forceInt(record.value('amount'))
        dbfRecord['TARIF'] = forceDouble(record.value('price'))

        dbfRecord.store()
        self.recNum += 1

# *****************************************************************************************

    def processDMS(self, dbf, record, codeLPU, accNumber,  accDate, lpuOKATO, payerOKATO):
        row = dbf.newRecord()
        row['SURNAME'] = forceString(record.value('lastName')) # фамилия
        row['NAME'] = forceString(record.value('firstName')) # имя
        row['PATRONOMIC'] = forceString(record.value('patrName')) #отчество
        row['BIRTHDAY'] = pyDate(forceDate(record.value('birthDate'))) #дата рождения
        row['POLIS_S'] = forceString(record.value('policySerial')) #серия полиса
        row['POLIS_N'] = forceString(record.value('policyNumber')) #номер полиса
        row['CODE_U'] = forceString(record.value('serviceCode')) #код услуги
        row['NAME_U'] = forceString(record.value('serviceName')) #название услуги
        row['CODE_D'] = forceString(record.value('aMKB'))  #код дигноза
        servDate = forceDate(record.value('actionDate'))

        if not servDate.isValid():
            servDate = forceDate(record.value('visitDate'))

            if not servDate.isValid():
                servDate = forceDate(record.value('endDate'))

        if not servDate.isValid():
            self.log(u'Не задана дата услуги: accountItemId=%d,'\
                u' код карточки "%d".' % (forceRef(record.value('accountItem_id')),
                                                        forceInt(record.value('event_id'))))

        row['DATE'] = pyDate(servDate) #дата оказания услуги
        row['TARIF'] = forceDouble(record.value('price')) #тариф
        row['AMOUNT'] = forceInt(record.value('amount')) #кол-во услуг
        row['SUM'] = forceDouble(record.value('sum')) #сумма
        row.store()

# *****************************************************************************************

    def checkWidgets(self, exportType):
        u"""Включает\выключает виджеты в зависимости от типа экспорта"""
        self.edtBegDate.setEnabled(exportType in (self.exportTypeTFOMS, self.exportTypeServiceInfo))
        self.edtEndDate.setEnabled(exportType  in (self.exportTypeTFOMS, self.exportTypeServiceInfo))
        self.edtRegistryNumber.setEnabled(exportType  in (self.exportTypeTFOMS, self.exportTypeServiceInfo))
        self.chkGroupByService.setEnabled(exportType != self.exportTypeDMS)
        self.edtServiceInfoFileName.setEnabled(exportType == self.exportTypeTFOMS2011_10)
        self.btnSelectServiceInfoFileName.setEnabled(exportType == self.exportTypeTFOMS2011_10)

# *****************************************************************************************

    def getPreliminaryInfo(self):
        u"""Загрузка информации о предварительном реестре из XML"""

        if self.edtServiceInfoFileName.text().isEmpty():
            return {}

        inFile = QtCore.QFile(self.edtServiceInfoFileName.text())
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных о предварительном реестре счета',
                                      QString(u'Не могу открыть файл для чтения %1:\n%2.')
                                      .arg(self.edtServiceInfoFileName.text())
                                      .arg(inFile.errorString()))
            return {}

        myXmlStreamReader = CServiceInfoXmlStreamReader(self, self.chkVerboseLog.isChecked())
        if (not myXmlStreamReader.readFile(inFile)):
            if self.aborted:
                self.log(u'! Прервано пользователем.')
            else:
                self.log(u'! Ошибка: файл %s, %s' % (self.edtServiceInfoFileName.text(), myXmlStreamReader.errorString()))

        return myXmlStreamReader.registryInfo

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


    @QtCore.pyqtSlot(int)
    def on_cmbExportType_currentIndexChanged(self, index):
        self.checkWidgets(index)

    @QtCore.pyqtSlot()
    def on_btnSelectServiceInfoFileName_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными предварительного счета', self.edtServiceInfoFileName.text(), u'Файлы XML (*.xml)')
        if fileName != '' :
            self.edtServiceInfoFileName.setText(QtCore.QDir.toNativeSeparators(fileName))


# *****************************************************************************************

class CExportPage2(QtGui.QWizardPage, Ui_ExportPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R53ExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        success = False
        srcFullName = self.parent.getFullDbfFileName() \
            if self.parent.page1.cmbExportType.currentIndex() \
                in (CExportPage1.exportTypeSMO, CExportPage1.exportTypeDMS) \
            else self.parent.getFullXmlFileName()

        (root,  ext) = os.path.splitext(srcFullName)
        zipName = root + '.zip'

        if compressFileInZip(srcFullName, zipName):
            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(zipName))
            success, result = QtGui.qApp.call(self, shutil.move, (zipName, dst))

            if success:
                QtGui.qApp.preferences.appPrefs['R53ExportDir'] = toVariant(self.edtDir.text())
                if self.parent.page1.edtRegistryNumber.isEnabled():
                    QtGui.qApp.preferences.appPrefs['ExportR53RegistryNumber'] = \
                        toVariant(self.parent.page1.edtRegistryNumber.value())
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
                u'Выберите директорию для сохранения файла выгрузки в ОМС Новгородской области',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))

# *****************************************************************************************

class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self, parent, exportType):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._exportType = exportType
        self.recNum = 1


    def writeRecord(self, record):
        self.writeStartElement("Rendering_assistance")
        clientId = forceRef(record.value('client_id'))
        specialCase = []

#    <N_PP>Уникальный порядковый номер в основном реестре счета содержит последовательность цифр, начиная с "1".</N_PP>
        self.writeTextElement('N_PP', '%d' % self.recNum)
#    <DEP_ID>Код структурного подразделения МО</DEP_ID>
        orgStructCode = forceString(record.value('orgStructureCode'))
        self.writeTextElement('DEP_ID', orgStructCode if orgStructCode else '0')
#    <VID_P>Тип документа, подтверждающего право на ОМС (Согласно классификатора типов документов, подтверждающих право на ОМС (F008))</VID_P>

        if self._exportType == CExportPage1.exportTypeTFOMS:
            #<C_OGRN>ОГРН СМО</C_OGRN>
            self.writeTextElement('C_OGRN', forceString(record.value('insurerOGRN')))
            #<C_OKATO>ОКАТО СМО</C_OKATO>
            self.writeTextElement('C_OKATO', forceString(record.value('insurerOKATO')))

        self.writeTextElement('VID_P', forceString(record.value('policyKindCode')))
#    <SN_POL>Серия и номер полиса ОМС пациента</SN_POL>
        policySerial = forceString(record.value(u'policySerial'))
        policyNumber = forceString(record.value(u'policyNumber'))
        policySN = u'%s № %s' % (policySerial,  policyNumber) if policySerial else policyNumber
        self.writeTextElement(u'SN_POL', policySN)

        #<SS>СНИЛС</SS>
        self.writeTextElement('SS', formatSNILS(forceString(record.value('SNILS'))))

        #    <C_P>Тип документа, удостоверяющего личность</C_P>
        self.writeTextElement('C_P', forceString(record.value('documentRegionalCode')))
#    <SN_DOC>Серия и номер документа, удостоверяющего личность</SN_DOC>
        self.writeTextElement('SN_DOC', u'%s № %s' % (forceString(record.value('documentSerial')),
                                                forceString(record.value('documentNumber'))))

        self.writeTextElement('DATE_DOC', forceDate(record.value('documentDate')).toString(QtCore.Qt.ISODate))
        self.writeTextElement('NAME_VP', forceString(record.value('origin')))
        self.writeTextElement('ADS_B', forceString(record.value('birthPlace')))
        self.writeTextElement('C_SHIP', '')

        info = self.parent.getClientRepresentativeInfo(clientId)
        age = forceInt(record.value('clientAge'))
        documentType = forceString(record.value('documentTypeCode'))

        if age < 1 and documentType != '3' and info != {}:
            specialCase.append('1')
            # Признак представителя  Обязательно 1-пациент/2-представитель
            relationTypeCode= info.get('relationTypeCode', '0')
            # Дата рождения родителя (представителя) пациента
            representativeBirthDate  = info.get('birthDate').toString(QtCore.Qt.ISODate)
            # Пол родителя (представителя) пациента "1 Мужской 2 Женский"
            representativeSex = info.get('sex', '')
            lastName= info.get('lastName', '')
            firstName = info.get('firstName', '')
            patrName = info.get('patrName', '')
        else:
            lastName= forceString(record.value('lastName'))
            # Имя застрахованного	Обязательно
            firstName =forceString(record.value('firstName'))
            # Отчество застрахованного При наличии
            patrName= forceString(record.value('patrName'))
            # Признак представителя  Обязательно 1-пациент/2-представитель
            relationTypeCode = '1'
            representativeSex = representativeBirthDate = ''

        if patrName == '':
            specialCase.append('2')

#    <FAM>Фамилия застрахованного</FAM>
        self.writeTextElement('FAM', lastName)
#    <IM>Имя застрахованного</IM>
        self.writeTextElement('IM', firstName)
#    <OT>Отчество застрахованного</OT>
        self.writeTextElement('OT', patrName)
#    <DR>Дата рождения застрахованного</DR>
        self.writeTextElement('DR', forceDate(record.value('birthDate')).toString(QtCore.Qt.ISODate))
#    <W>Пол застрахованного</W>
        self.writeTextElement('W', forceString(record.value('sex')))
#    <PR_PR>Признак представителя 1-пациент/2-представитель</PR_PR>

        if self._exportType == CExportPage1.exportTypeTFOMS:
            self.writeTextElement('ATTACH_SIGN', '')

        self.writeTextElement('PR_PR', relationTypeCode)
#    <DRP>Дата рождения родителя (представителя) пациента</DRP>
        self.writeTextElement('DRP', representativeBirthDate)
#    <WP>Пол родителя (представителя) пациента</WP>
        self.writeTextElement('WP', forceString(representativeSex))
#    <Q_G>Особый случай</Q_G>
        self.writeTextElement('Q_G', ' '.join(x for x in specialCase))
#        <Q_R></Q_R> - код причины обращения - брать из НАЗНАЧЕНИЕ ТИПЯ СОБЫТИЯ
        self.writeTextElement('Q_R', forceString(record.value('eventTypePurpose')))
#    <Q_V>Вид оказанной медицинской помощи</Q_V>
        medicalAidTypeCode = forceInt(record.value('medicalAidTypeCode'))
        if self._exportType == CExportPage1.exportTypeTFOMS:
            self.writeTextElement('Q_V', forceString(record.value('medicalAidKindRegionalCode')))
            self.writeTextElement('Q_U', forceString(record.value('medicalAidTypeRegionalCode')))
        else:
            self.writeTextElement('Q_V', forceString(record.value('medicalAidTypeRegionalCode')))
#    <Q_U>Код условий оказания медицинской помощи (Согласно классификатора условий оказания медицинской помощи (V006))</Q_U>
            self.writeTextElement('Q_U', forceString(record.value('eventProfileRegCode')))
#    <V_ED>Единицы измерения объёма оказанной медицинской помощи</V_ED>
        self.writeTextElement('V_ED', forceString(record.value('medicalAidUnitName')))
#    <V_V>Объём оказанной медицинской помощи</V_V>
        self.writeTextElement('V_V', forceString(record.value('amount')))
#    <DS>Код основного диагноза</DS>
        self.writeTextElement('DS', forceString(record.value('MKB')))
#    <DS_S>Код сопутствующего диагноза</DS_S>
        self.writeTextElement('DS_S', forceString(record.value('AccMKB')))
#    <PRMP>Код профиля оказания медицинской помощи</PRMP>
        self.writeTextElement('PRMP', forceString(record.value('medicalAidProfileRegionalCode')))
#    <C_LC/>
        self.writeTextElement('C_LC', '')
#    <NUM_CARD>Номер амбулаторной карты или номер истории болезни</NUM_CARD>
        self.writeTextElement('NUM_CARD', forceString(record.value('accountItemId')))
#    <DATE_1>Дата начала лечения/обследования (ГГГГ-ММ-ДД)</DATE_1>
        self.writeTextElement('DATE_1', forceDate(record.value('begDate')).toString(QtCore.Qt.ISODate))
#    <DATE_2>Дата окончания лечения/обследования (ГГГГ-ММ-ДД)</DATE_2>
        self.writeTextElement('DATE_2', forceDate(record.value('endDate')).toString(QtCore.Qt.ISODate))
        self.writeTextElement('IDRB', '')
        self.writeTextElement('MED_ST', '')
#    <PRVS>Специальность (специализация) медицинского работника, оказавшего медицинскую помощь</PRVS>
        self.writeTextElement('PRVS', forceString(self.parent.getSpecialityRegionalCode(forceRef(record.value('execPersonId')))))
#    <RSLT>Результат обращения за медицинской помощью</RSLT>
        insurerArea = forceString(record.value('insurerArea'))
        isAlien = insurerArea and insurerArea[:2] != QtGui.qApp.defaultKLADR()[:2]
        if self._exportType == CExportPage1.exportTypeTFOMS:
            self.writeTextElement('RSLT', forceString(record.value('eventResultRegionalCode')))
        else:
            self.writeTextElement('RSLT', forceString(record.value('resultFederalCode' if isAlien else 'resultCode')))
#    <IDSP>Код способа оплаты (Согласно классификатора способов оплаты (V010))</IDSP>
        self.writeTextElement('IDSP', '')
#    <TARIF>Тариф</TARIF>
        fieldName = 'sum' if medicalAidTypeCode in (1, 2, 3, 7) else 'price'
        fieldName2 = 'federalSum' if medicalAidTypeCode in (1, 2, 3, 7) else 'federalPrice'
        self.writeTextElement('TARIF', ('%11.2f' %
            (forceDouble(record.value(fieldName))-forceDouble(record.value(fieldName2)))).strip())
#    <S_ALL>Выставленная сумма к оплате (Стоимость оказанной медицинской помощи)</S_ALL>
        federalSum = forceDouble(record.value('federalSum'))
        sum = forceDouble(record.value('sum')) - federalSum
        self.writeTextElement('S_ALL',  ('%11.2f' % sum).strip())

        if self._exportType == CExportPage1.exportTypeTFOMS:
            self.writeTextElement('S_OPL', '')

        self.writeTextElement('S_ALL_M',  ('%11.2f' % federalSum).strip())

        if self._exportType == CExportPage1.exportTypeTFOMS:
            self.writeTextElement('S_OPL_M', '')
            self.writeTextElement('I_TYPE', '')
            self.writeTextElement('RES_CTRL', '')

        self.recNum += 1
        self.writeEndElement()


    def writeFileHeader(self,  device, senderName, senderOGRN, insurerName, insurerOGRN,  \
            begDate, endDate, accNumber, accDate, miacCode,  accSum,  settleDate):
        self.recNum = 1
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement("root")
        self.writeHeader(senderName, senderOGRN, insurerName, insurerOGRN,
                         begDate, endDate, accNumber, accDate,  miacCode, accSum, settleDate)


    def writeHeader(self, senderName, senderOGRN, insurerName, insurerOGRN,  begDate,
            endDate, accNumber, accDate,  miacCode,  accSum, settleDate):
        self.writeStartElement('heading')
        self.writeTextElement('Version', '1,01')
        self.writeTextElement('Sender', senderName)
        self.writeTextElement('M_OGRN', senderOGRN)

        if self._exportType == CExportPage1.exportTypeTFOMS:
            self.writeTextElement('LPU_ID', miacCode)

        self.writeTextElement('Addressee', insurerName)

        if self._exportType == CExportPage1.exportTypeInternal:
            self.writeTextElement('C_OGRN', insurerOGRN)

        self.writeTextElement('Theme', u'Отчет об объемах медицинской помощи,'\
            u' оказанной застрахованным гражданам')
        self.writeTextElement('Accounting_period',
            begDate.toString(QtCore.Qt.ISODate)+' '+endDate.toString(QtCore.Qt.ISODate))
        self.writeTextElement('NUM_S', forceString(accNumber))
        self.writeTextElement('DATE_S', accDate.toString(QtCore.Qt.ISODate))
        self.writeEndElement()


    def writeFileFooter(self):
        self.writeEndElement() # root
        self.writeEndDocument()

# *****************************************************************************************

class CTFOMSXmlStreamWriter(CMyXmlStreamWriter):
    def __init__(self, parent, exportType):
        CMyXmlStreamWriter.__init__(self, parent, exportType)
        self.miacCode = ''
        self.lastClientId = None
        self.caseNum = 1

    def writeTextElement(self, element,  value, writeEmtpyTag = True):
        if not writeEmtpyTag and (not value or value == ''):
            return

        CMyXmlStreamWriter.writeTextElement(self, element, value)

    def writeRecord(self, record):
        clientId = forceRef(record.value('client_id'))
        age = forceInt(record.value('clientAge'))
        sex = forceString(record.value('sex'))
        birthDate = forceDate(record.value('birthDate'))

        if self.lastClientId != clientId: # новая запись, иначе - новый случай
            if self.lastClientId:
                self.recNum += 1
                self.writeEndElement() # ZAP

            self.lastClientId = clientId

            self.writeStartElement('ZAP')
            # Уникально идентифицирует запись в пределах счета(1,2,3,4...)
            self.writeTextElement('N_ZAP', '%d' % self.recNum)

            self.writeStartElement('PACIENT')
            #Окато территории страховой, полис которой у человека
            self.writeTextElement('OKATO_OMS', forceString(record.value('insurerOKATO')))
            #Федеральный код из справочника ВИДЫ ПОЛИСА. Указывается в карточке пациента.
            self.writeTextElement('VPOLIS', forceString(record.value('policyKindFederalCode')))
            #Серия полиса.
            self.writeTextElement('SPOLIS',  forceString(record.value('policySerial')), writeEmtpyTag=False)
            #Номер полиса.
            self.writeTextElement('NPOLIS', forceString(record.value('policyNumber')))
            #Фамилия пациента.
            self.writeTextElement('FAM', forceString(record.value('lastName')))
            #Имя пациента
            self.writeTextElement('IM', forceString(record.value('firstName')))
            #Отчество пациента
            self.writeTextElement('OT', forceString(record.value('patrName')), writeEmtpyTag=False)
            #Пол пациента.
            self.writeTextElement('W', sex)
            #Дата рождения пациента.
            self.writeTextElement('DR', birthDate.toString(QtCore.Qt.ISODate))
#            self.writeTextElement('FAM_P', '')
#            self.writeTextElement('IM_P', '')
#            self.writeTextElement('OT_P', '')
#            self.writeTextElement('W_P', '')
            # Место рождения пациента или представителя. Из карточки пациента.
#            self.writeTextElement('DR_P', forceString(record.value('birthPlace')), writeEmtpyTag=False)
            # Тип документа, удо-стоверяющего лич-ность пациента.
            self.writeTextElement('MR', forceString(record.value('birthPlace')), writeEmtpyTag=False)
            # Федеральный код из справочника ТИПЫ ДОКУМЕНТОВ. Из карточки пациента.
            self.writeTextElement('DOCTYPE',  forceString(record.value('documentFederalCode')), writeEmtpyTag=False)
            # Серия документа, удо-стоверяющего личность пациента.
            self.writeTextElement('DOCSER', forceString(record.value('documentSerial')), writeEmtpyTag=False)
            # Номер документа, удостоверяющего личность пациента.
            self.writeTextElement('DOCNUM', forceString(record.value('documentNumber')), writeEmtpyTag=False)
            # СНИЛС пациента.
            self.writeTextElement('SNILS', formatSNILS(forceString(record.value('SNILS'))), writeEmtpyTag=False)
            # Код места жительства по ОКАТО. Берётся из адреса жительство.
            self.writeTextElement('OKATOG', forceString(record.value('placeOKATO')), writeEmtpyTag=False)
            # Код места пребывания по ОКАТО. Берётся из ОКАТО организации, чей полис у пациента.
            self.writeTextElement('OKATOP', forceString(record.value('insurerOKATO')), writeEmtpyTag=False)
            self.writeTextElement('NOVOR', '0' if age > 0 else
                '%s%s0' % (sex[:1], birthDate.toString('ddMMyy')))
            self.writeTextElement('COMENTP', '', writeEmtpyTag=False)
            self.writeEndElement() # PACIENT

        self.writeStartElement('SLUCH')
        self.writeTextElement('IDCASE', '%d' % self.caseNum)
        # Федеральный код справочника НАЗНАЧЕНИЕ ТИПА СОБЫТИЯ
        self.writeTextElement('USL_OK',  forceString(record.value('medicalAidTypeFederalCode')))
        self.writeTextElement('VIDPOM',  forceString(record.value('medicalAidKindFederalCode')))
        # 1 – плановая; 2 – экстренная ИЗ СОБЫТИЯ
        self.writeTextElement('EXTR', '2' if forceInt(record.value('order')) == 2 else '1')
        # Код МИАЦ ЛПУ
        self.writeTextElement('LPU', '530%s' % self.miacCode)
        # Федеральный код из справочника ПРОФИЛЬ МЕДЕЦИНСКОЙ ПОМОЩИ
        self.writeTextElement('PROFIL', forceString(record.value('medicalAidProfileFederalCode')))
        # Здесь наверное на основании тарифа, если -18г, то ДА. Если 18г-, то НЕТ. В дальнейшем может у профиля добавить св-во ДЕСТКИЙ(ДА, нет)

        self.writeTextElement('DET', (u'1' if age < 18 else u'0'))
        # event_id
        self.writeTextElement('NHISTORY', forceString(record.value('eventId')))
        # Дата начала события
        self.writeTextElement('DATE_1', forceDate(record.value('begDate')).toString(QtCore.Qt.ISODate))
        # Дата окончания события
        self.writeTextElement('DATE_2', forceDate(record.value('endDate')).toString(QtCore.Qt.ISODate))
        # Предворительный основной диагноз, врача ответственного за событие
#        self.writeTextElement('DS0', '')
        self.writeTextElement('DS1', forceString(record.value('MKB')), writeEmtpyTag=False)
        self.writeTextElement('DS2', '', writeEmtpyTag=False)
#        self.writeTextElement('CODE_MES1', '')
#        self.writeTextElement('CODE_MES2', '')
        # Федеральный код из справочника РЕЗУЛЬТАТ ОБРАЩЕНИЯ
        self.writeTextElement('RSLT', forceString(record.value('eventResultFederalCode')))
        # Федеральный код из справочника РЕЗУЛЬТАТ ОСМОТРА. Результат ЗАКЛЮЧИТЕЛЬНОГО ДИАГНОЗА.
        self.writeTextElement('ISHOD', forceString(record.value('resultFederalCode')))
        # Федеральный код из справочника СПЕЦИАЛЬНОСТИ ВРАЧЕЙ. Врач поставивший ЗАКЛЮЧИТЕЛЬНЫЙ ДИАГНОЗ
        self.writeTextElement('PRVS', forceString(self.parent.getSpecialityFederalCode(forceRef(record.value('execPersonId')))))
        # Федеральный код из справочника ЕДЕНИЦЫ УЧЁТА МЕДЕЦИНСКОЙ ПОМОЩИ
        self.writeTextElement('IDSP', forceString(record.value('medicalAidUnitFederalCode')))
        self.writeTextElement('ED_COL', forceString(record.value('amount')))
        self.writeTextElement('TARIF', ('%10.2f' % forceDouble(record.value('price'))).strip())
        self.writeTextElement('SUMV', ('%10.2f' % forceDouble(record.value('sum'))).strip())
        # Региональный код из справочника ПРОФИЛЬ МЕДЕЦИНСКОЙ ПОМОЩИ
        self.writeTextElement('PROFIL_FOMS',  forceString(record.value('medicalAidProfileRegionalCode')))
        # Региональный код из справочника СПЕЦИАЛЬНОСТИ ВРАЧЕЙ. Врач поставивший ЗАКЛЮЧИТЕЛЬНЫЙ ДИАГНОЗ
        self.writeTextElement('PRVS_FOMS', forceString(self.parent.getSpecialityRegionalCode(forceRef(record.value('execPersonId')))))

        # Работа со словарем данных о предварительном реестре
        eventId = forceInt(record.value('event_id'))
        serviceId = forceInt(record.value('service_id'))
        visitId = forceInt(record.value('visit_id'))
        actionId = forceInt(record.value('action_id'))
        key = (eventId, serviceId, visitId, actionId)
        (pAccNum, pAccDate, pRecNum) = self.parent.preliminaryRegistryInfo.get(key, ('', '', ''))
        # номер предварительного реестра (порядковый номер счёта, в клиенте)
        self.writeTextElement('PREPARE_ACC', pAccNum)
        # дата предварительного реестра (дата экспорта)
        self.writeTextElement('PREPARE_DATE', pAccDate)
        # номер позиции предварительного реестра (значение поля <N_PP>, в предварительном реестре)
        self.writeTextElement('PREPARE_NUM', pRecNum)
#        self.writeTextElement('OPLATA', '')
#        self.writeTextElement('SUMP', '')
#        self.writeTextElement('REFREASON', '')
#        self.writeTextElement('SANK_MEK', '')
#        self.writeTextElement('SANK_MEE', '')
#        self.writeTextElement('SANK_EKMP', '')
#        self.writeTextElement('USL', '')
#        self.writeTextElement('COMENTSL', '')
        self.writeEndElement() # SLUCH
        self.caseNum += 1


    def writeFileHeader(self,  device, senderName, senderOGRN, insurerName, insurerOGRN,  \
            begDate, endDate, accNumber, accDate, miacCode, accSum,  settleDate):
        self.recNum = 1
        self.miacCode = miacCode
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('ZL_LIST')
        self.writeHeader(senderName, senderOGRN, insurerName, insurerOGRN,
                         begDate, endDate, accNumber, accDate,  miacCode, accSum, settleDate)


    def writeHeader(self, senderName, senderOGRN, insurerName, insurerOGRN,  begDate,
            endDate, accNumber, accDate,  miacCode, accSum, settleDate):

        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '1.0')
        self.writeTextElement('DATA', accDate.toString(QtCore.Qt.ISODate))
        self.writeTextElement('C_OKATO1', '49000')
        self.writeEndElement() # ZGLV

        self.writeStartElement('SCHET')
        self.writeTextElement('CODE', '53%s%d' % (miacCode,  accNumber))
        # Отчетный год
        self.writeTextElement('YEAR', '%d' % settleDate.year())
        # Отчетный месяц
        self.writeTextElement('MONTH', '%d' % settleDate.month())
        # № счёта
        self.writeTextElement('NSCHET', '%d' % accNumber)
        self.writeTextElement('DSCHET', accDate.toString(QtCore.Qt.ISODate))
        # Сумма МО, выставленная на оплату
        self.writeTextElement('SUMMAV', '%.2f' % accSum)
        self.writeTextElement('COMENTS', '', writeEmtpyTag=False)
        self.writeTextElement('SUMMAP', '')
        self.writeTextElement('SANK_MEK', '', writeEmtpyTag=False)
        self.writeTextElement('SANK_MEE', '', writeEmtpyTag=False)
        self.writeTextElement('SANK_EKMP', '', writeEmtpyTag=False)
        self.writeEndElement() # SCHET


    def writeFileFooter(self):
        self.writeEndElement() # ZAP
        CMyXmlStreamWriter.writeFileFooter(self)

# *****************************************************************************************

class CServiceInfoXmlStreamWriter(CMyXmlStreamWriter):
    def __init__(self, parent, exportType):
        CMyXmlStreamWriter.__init__(self, parent, exportType)
        self.miacCode = ''
        self.lastClientId = None
        self.recNum = 1

    def writeFileHeader(self,  device, senderName, senderOGRN, insurerName, insurerOGRN,  \
            begDate, endDate, accNumber, accDate, miacCode, accSum, settleDate):
        self.recNum = 1
        self.miacCode = miacCode
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('AccountServiceInfo')
        self.writeAttribute('version', serviceInfoExportVersion)

        self.writeHeader(senderName, senderOGRN, insurerName, insurerOGRN,
                         begDate, endDate, accNumber, accDate,  miacCode, accSum, settleDate)


    def writeHeader(self, senderName, senderOGRN, insurerName, insurerOGRN,  begDate,
            endDate, accNumber, accDate,  miacCode, accSum, settleDate):


        self.writeStartElement('AccountInfo')
        self.writeAttribute('number', self.parent.edtRegistryNumber.text())
        self.writeAttribute('date', accDate.toString(QtCore.Qt.ISODate))
        self.writeEndElement()

    def writeRecord(self, record):
        eventId = forceString(record.value('event_id'))
        serviceId = forceString(record.value('service_id'))
        visitId = forceString(record.value('visit_id'))
        actionId = forceString(record.value('action_id'))

        self.writeStartElement('AccountItem')
        self.writeAttribute('recNum', forceString(self.recNum))
        self.writeAttribute('event_id', eventId)
        self.writeAttribute('service_id', serviceId)
        self.writeAttribute('visit_id', visitId)
        self.writeAttribute('action_id', actionId)
        self.writeEndElement()

        self.recNum += 1

# *****************************************************************************************

class CServiceInfoXmlStreamReader(QXmlStreamReader):
    def __init__(self, parent, showLog):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.showLog = showLog
        self.registryInfo = {}
        self._accountDate = ''
        self._accountNumber = ''


    def raiseError(self, str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def readNext(self):
        QXmlStreamReader.readNext(self)
        self.parent.progressBar.setValue(self.device().pos())


    def log(self, str, forceLog = False):
        if self.showLog or forceLog:
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device):
        self.registryInfo = {}
        self._accountDate = ''
        self._accountNumber = ''

        self.setDevice(device)
        try:
            while (not self.atEnd()):
                self.readNext()

                if self.isStartElement():
                    if self.name() == 'AccountServiceInfo':
                        if self.attributes().value('version') == serviceInfoExportVersion:
                            self.readData()
                        else:
                            self.raiseError(u'Версия формата "%s" не поддерживается. Должна быть "%s"' \
                                % (self.attributes().value('version').toString(), serviceInfoExportVersion))
                    else:
                        self.raiseError(u'Неверный формат экспорта данных.')

                if self.hasError() or self.parent.aborted:
                    return False

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            self.log(u'! Ошибка ввода-вывода: %s' % msg, True)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.log(u'! Ошибка: %s' % unicode(e), True)
            return False
        return not (self.hasError() or self.parent.aborted)


    def readData(self):
        assert self.isStartElement() and self.name() == 'AccountServiceInfo'
        while (not self.atEnd()):
            self.readNext()
            if self.isEndElement():
                break
            if self.isStartElement():
                if (self.name() == 'AccountInfo'):
                    self.readAccountInfoElement()
                elif (self.name() == 'AccountItem'):
                    self.readAccountItemElement()
                else:
                    self.readUnknownElement()
            if self.hasError() or self.parent.aborted:
                break


    def readAccountItemElement(self):
        assert self.isStartElement() and self.name() == 'AccountItem'

        eventId = forceInt(forceString(self.attributes().value('event_id').toString()))
        serviceId = forceInt(forceString(self.attributes().value('service_id').toString()))
        visitId = forceInt(forceString(self.attributes().value('visit_id').toString()))
        actionId = forceInt(forceString(self.attributes().value('action_id').toString()))
        key = (eventId, serviceId, visitId, actionId)

        recNum = forceString(self.attributes().value('recNum').toString())
        self.registryInfo[key] = (self._accountNumber, self._accountDate, recNum)

        while not self.atEnd():
            self.readNext()
            QtGui.qApp.processEvents()
            if self.isEndElement():
                break
            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                return None


    def readAccountInfoElement(self):
        assert self.isStartElement() and self.name() == 'AccountInfo'

        self._accountDate = forceString(self.attributes().value('date').toString())
        self._accountNumber = forceString(self.attributes().value('number').toString())

        while not self.atEnd():
            self.readNext()
            QtGui.qApp.processEvents()
            if self.isEndElement():
                break
            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                return None


    def readUnknownElement(self):
        assert self.isStartElement()
        self.log(u'Неизвестный элемент: '+self.name().toString())

        while (not self.atEnd()):
            self.readNext()
            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break
