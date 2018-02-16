# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil

from zipfile import *

from library.Utils     import *
from Exchange.Utils import CExportHelperMixin

from Ui_ExportR29XMLPage1 import Ui_ExportPage1
from Ui_ExportR29XMLPage2 import Ui_ExportPage2

serviceInfoExportVersion = '1.0'

def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'settleDate, number, exposeDate, contract_id, payer_id, date', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('settleDate'))
        aDate  = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        number = forceString(accountRecord.value('number')).strip()
        contractId = forceRef(accountRecord.value('contract_id'))
        payerId = forceRef(accountRecord.value('payer_id'))
    else:
        date = exposeDate = contractId = payerId = aDate = None
        number = '0'
    return date, number, exposeDate, contractId,  payerId,  aDate


def exportR29XML(widget, accountId, accountItemIdList):
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
        self.setWindowTitle(u'Мастер экспорта в XML для Архангельской области')
        self.tmpDir = ''
        self.xmlFileName = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, exposeDate, contractId, payerId,  aDate = getAccountInfo(accountId)
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменных файлов')


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R29XML')
        return self.tmpDir


    def getFullXmlFileName(self):
        if not self.xmlFileName:
            (date, number, exposeDate, contractId,  payerId,  aDate) = getAccountInfo(self.accountId)

            if self.page1.chkExportTypeBelonging.isChecked():
                payerCode = '29'
                infix = 'T'
            else:
                payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'miacCode'))
                infix = 'S'

            lpuInfis  = '292301'
            self.xmlFileName = os.path.join(self.getTmpDir(), \
                u'HM%s%s%s_%s%d.xml' % (lpuInfis, infix,  payerCode, date.toString('yyMM'), self.page1.edtRegistryNumber.value()))
        return self.xmlFileName


    def getFullXmlPersFileName(self):
        return os.path.join(self.getTmpDir(), u'L%s' % os.path.basename(self.getFullXmlFileName())[1:])


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
            'ExportR29XMLIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29XMLVerboseLog', False)))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.chkGroupByService.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29XMLGroupByService', True)))
        self.edtRegistryNumber.setValue(forceInt(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29XMLRegistryNumber', 0))+1)
        self.chkExportTypeBelonging.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR29XMLBelonging', True)))


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.chkGroupByService.setEnabled(not flag)
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
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        output, clientOutput = self.createXML()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return output, query,  clientOutput


    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            QtGui.qApp.preferences.appPrefs['ExportR29XMLIgnoreErrors'] = \
                    toVariant(self.chkIgnoreErrors.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR29XMLVerboseLog'] = \
                    toVariant(self.chkVerboseLog.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR29XMLGroupByService'] = \
                    toVariant(self.chkGroupByService.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR29XMLBelonging'] = \
                    toVariant(self.chkExportTypeBelonging.isChecked())
            self.done = True
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

    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        cond = tableAccountItem['id'].inlist(self.idList)

        if self.chkGroupByService.isChecked():
            sumStr = """SUM(Account_Item.`sum`) AS `sum`,
                SUM(Account_Item.amount) AS amount,
                SUM(IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice) AS federalSum,"""
            cond += ' GROUP BY `Account_Item`.`event_id`, serviceId'
        else:
            sumStr = """Account_Item.`sum` AS `sum`,
                Account_Item.amount AS amount,
                 IF(Contract_Tariff.federalLimitation = 0,
                            Account_Item.amount,
                            LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice AS federalSum,"""

        stmt = """SELECT Account_Item.id AS accountItemId,
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
                Account_Item.uet,
                Account_Item.price AS price, %s
                Person.regionalCode AS personRegionalCode,
                rbDiagnosticResult.federalCode AS resultFederalCode,
                rbMedicalAidType.code AS medicalAidTypeCode,
                rbMedicalAidType.regionalCode AS medicalAidTypeRegionalCode,
                rbMedicalAidType.regionalCode AS medicalAidTypeFederalCode,
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
                rbMedicalAidUnit.federalCode AS medicalAidUnitFederalCode,
                RegSOCR.infisCODE AS placeTypeCode,
                RegRegionKLADR.NAME AS regionName,
                rbEventTypePurpose.regionalCode AS eventTypePurpose,
                rbEventTypePurpose.federalCode AS eventTypePurposeFederalCode,
                Event.`order`,
                Event.id AS eventId,
                EventResult.federalCode AS eventResultFederalCode,
                EventResult.regionalCode AS eventResultRegionalCode,
                RelegateOrg.miacCode AS relegateOrgMiac,
                rbTariffCategory.federalCode AS tariffCategoryFederalCode,
                EventType.code AS eventTypeCode
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
            LEFT JOIN Organisation AS RelegateOrg ON Event.relegateOrg_id = RelegateOrg.id
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
            LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
            LEFT JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
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
            LEFT JOIN rbTariffCategory ON  Contract_Tariff.tariffCategory_id = rbTariffCategory.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s ORDER BY Client.id, Event.id, Event.execDate""" % (sumStr, cond)

        query = db.query(stmt)
        return query

# *****************************************************************************************

    def getEventsSummaryPrice(self):
        u"""возвращает общую стоимость услуг за событие"""

        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """SELECT event_id,
            SUM(Account_Item.sum) AS totalSum,
            SUM(IF(Account_Item.uet!=0,Account_Item.uet,Account_Item.amount)) AS totalAmount
        FROM Account_Item
        LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
        LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
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
            amount = forceDouble(record.value('totalAmount'))
            result[eventId] = (amount,  sum)
        return result

# *****************************************************************************************

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()
        lpuName = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'fullName'))
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OGRN'))

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан ОГРН', True)
            if not self.ignoreErrors:
                return

        lpuOKATO = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OKATO'))

        if not lpuOKATO:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для текущего ЛПУ не задан ОКАТО', True)
            if not self.ignoreErrors:
                return

        out, query, clientsFile = self.prepareToExport()
        accDate, accNumber, exposeDate, contractId,  payerId, aDate =\
            getAccountInfo(self.parent.accountId)
        strAccNumber = accNumber if trim(accNumber) else u'б/н'
        strContractNumber = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'number')) if contractId else u'б/н'

        payerCode = None
        payerName = ''

        if payerId:
            payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'miacCode'))

        if not payerCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для плательщика не задан код МИАЦ', True)
            if not self.ignoreErrors:
                return

        self.recNum = 1

        if self.idList:
            file = out
            out = CMyXmlStreamWriter(self)
            clientsOut = CPersonalDataStreamWriter(self)
            out.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            miacCode = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))
            accSum = forceDouble(QtGui.qApp.db.translate(
                'Account', 'id', self.parent.accountId, 'sum'))
            out.writeFileHeader(file, self.parent.getFullXmlFileName(), accNumber, aDate,
                                forceString(accDate.year()),
                                forceString(accDate.month()),
                                miacCode, payerCode, accSum)
            clientsOut.writeFileHeader(clientsFile, self.parent.getFullXmlFileName(), aDate)
            eventsInfo = self.getEventsSummaryPrice()

            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                out.writeRecord(query.record(), miacCode, eventsInfo)
                clientsOut.writeRecord(query.record())

            out.writeFileFooter()
            clientsOut.writeFileFooter()
            file.close()
            clientsFile.close()
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()


# *****************************************************************************************

    def createXML(self):
        outFile = QtCore.QFile(self.parent.getFullXmlFileName())
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        outFile2 = QtCore.QFile( self.parent.getFullXmlPersFileName())
        outFile2.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        return outFile, outFile2


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
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ExportR29XMLExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        success = False
        baseName = os.path.basename(self.parent.getFullXmlFileName())
        (root, ext) = os.path.splitext(baseName)
        zipFileName = '%s.zip' % root
        zipFilePath = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                zipFileName)
        zf = ZipFile(zipFilePath, 'w', allowZip64=True)

        for src in (self.parent.getFullXmlFileName(),  self.parent.getFullXmlPersFileName()):
            zf.write(src, os.path.basename(src), ZIP_DEFLATED)

        zf.close()

        dst = os.path.join(forceStringEx(self.edtDir.text()), zipFileName)
        success, result = QtGui.qApp.call(self, shutil.move, (zipFilePath, dst))

        if success:
            QtGui.qApp.preferences.appPrefs['ExportR29XMLExportDir'] = toVariant(self.edtDir.text())
            QtGui.qApp.preferences.appPrefs['ExportR29XMLRegistryNumber'] = \
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
                u'Выберите директорию для сохранения файла выгрузки в ОМС Архангельской области',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))

# *****************************************************************************************

class CMyXmlStreamWriter(QXmlStreamWriter, CExportHelperMixin):
    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        CExportHelperMixin.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.recNum = 1 # номер записи
        self.caseNum = 1 # номер случая
        self.serviceNum = 1 # номер услуги
        self._lastClientId = None
        self._lastEventId = None
        self.medicalAidProfileCache = {}
        self.rbPostFederalCache= {}
        self.rbPostRegionalCache = {}


    def writeRecord(self, record, miacCode, eventsInfo):
        clientId = forceRef(record.value('client_id'))
        age = forceInt(record.value('clientAge'))
        endDate = forceDate(record.value('endDate'))
        eventId = forceRef(record.value('event_id'))
        federalPrice = forceDouble(record.value('federalPrice'))
        federalSum = forceDouble(record.value('federalSum'))
        personId = forceRef(record.value('execPersonId'))
        profile = self.getProfile(forceRef(record.value('serviceId')), personId)
        profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]
        amount = forceDouble(record.value('amount'))

        specialCase = []

        if self._lastClientId != clientId: # новая запись, иначе - новый случай
            if self._lastClientId:
                self.recNum += 1
                self.writeEndElement() # SLUCH
                self.writeEndElement() # ZAP
                self._lastEventId = None

            self._lastClientId = clientId
            self.writeStartElement('ZAP')

            self.writeTextElement('N_ZAP', ('%4d' % self.recNum).strip())
            self.writeTextElement('PR_NOV', '0')

            self.writeStartElement('PACIENT')
            self.writeTextElement('ID_PAC',  ('%d' % clientId)[:36])
            # Региональный код справочника ВИДЫ ПОЛИСОВ.
            self.writeTextElement('VPOLIS', forceString(record.value('policyKindCode'))[:1])
            self.writeTextElement('SPOLIS', forceString(record.value(u'policySerial'))[:10])
            self.writeTextElement('NPOLIS', forceString(record.value(u'policyNumber'))[:20])
            self.writeTextElement('SMO', forceString(record.value('insurerMiac'))[:5])
            self.writeTextElement('SMO_OGRN', forceString(record.value('insurerOGRN'))[:15])
            self.writeTextElement('SMO_OK', forceString(record.value('insurerOKATO'))[:5])
            self.writeTextElement('SMO_NAM', forceString(record.value('insurerName'))[:100], writeEmtpyTag = False)
            birthDate = forceDate(record.value('birthDate'))
            self.writeTextElement('NOVOR', '0' if endDate.toJulianDay()-birthDate.toJulianDay() > 30
                                else '%s%s0' % (forceString(record.value('sex'))[:1], birthDate.toString('ddMMyy')))
            self.writeEndElement() # PACIENT

        if self._lastEventId != eventId:
            if self._lastEventId:
                self.writeEndElement() # SLUCH

            self._lastEventId = eventId
            self.writeStartElement('SLUCH')
            self.writeTextElement('IDCASE', '%d' % self.caseNum)
            # Федеральный код справочника НАЗНАЧЕНИЕ ТИПА СОБЫТИЯ
            self.writeTextElement('USL_OK',  forceString(record.value('medicalAidTypeFederalCode')))
            self.writeTextElement('VIDPOM', forceString(record.value('medicalAidTypeCode')))
            self.writeTextElement('NPR_MO', forceString(record.value('relegateOrgMiac')),  writeEmtpyTag = False)
            # 1 – плановая; 2 – экстренная ИЗ СОБЫТИЯ
            if forceInt(record.value('order')) == 2:
                self.writeTextElement('EXTR', '1')
            self.writeTextElement('PODR', forceString(record.value('orgStructureCode')))
            self.writeTextElement('LPU', miacCode[:6])
            self.writeTextElement('PROFIL', profileStr)
            self.writeTextElement('DET', (u'1' if age < 18 else u'0'))
            self.writeTextElement('NHISTORY', ('%d' % eventId)[:50])
            # Дата начала события
            self.writeTextElement('DATE_1', forceDate(record.value('begDate')).toString(QtCore.Qt.ISODate))
            # Дата окончания события
            self.writeTextElement('DATE_2', endDate.toString(QtCore.Qt.ISODate))
            self.writeTextElement('DS1', forceString(record.value('MKB')))
            self.writeTextElement('DS2', forceString(record.value('AccMKB')))
            self.writeTextElement('RSLT', forceString(record.value('eventResultFederalCode')))
            # Федеральный код из справочника РЕЗУЛЬТАТ ОСМОТРА. Результат ЗАКЛЮЧИТЕЛЬНОГО ДИАГНОЗА.
            self.writeTextElement('ISHOD', forceString(record.value('resultFederalCode')))
            self.writeTextElement('PRVS', forceString(self.parent.getSpecialityFederalCode(personId)))
            #self.writeTextElement('IDDOKT', forceString(self.parent.getPersonRegionalCode(forceRef(record.value('execPersonId')))))
            self.writeTextElement('IDSP', forceString(record.value('medicalAidUnitFederalCode')))
            (totalAmount,  totalSum) = eventsInfo[eventId]
            self.writeTextElement('ED_COL', ('%6.2f' % totalAmount).strip())
            #self.writeTextElement('TARIF', ('%10.2f' % forceDouble(record.value('price'))).strip())
            self.writeTextElement('SUMV', ('%10.2f' % totalSum).strip())
            self.caseNum+= 1

        serviceId = forceRef(record.value('serviceId'))
        serviceStr = self.getServiceInfis(serviceId)
        eventTypeCode = forceString(record.value('eventTypeCode'))

        if eventTypeCode in ('2', '7'):
            serviceStr += self.getPersonPostRegionalCode(personId)

        lpu1Str = '7' if eventTypeCode == '7' else ''

        uet = forceDouble(record.value('uet'))
        sum = forceDouble(record.value('sum'))
        price = forceDouble(record.value('price'))

        if uet != 0.0:
            price *= uet

        self.writeService(record, miacCode, age, profileStr,
                                    serviceStr,
                                    forceDouble(record.value('price')),
                                    amount, sum, lpu1Str)

#        tariffCategoryFederalCode = forceString(record.value('tariffCategoryFederalCode'))

        if federalPrice > 0.0:
            serviceCode = self.getServiceCode(serviceId)
            serviceStr = self.getServiceInfis(serviceId)

            if serviceCode and serviceCode[:4] == 'STD_':
                serviceStr = '51%s' % serviceStr[2:]
            else:
                postFederalCode = self.getPersonPostFederalCode(personId)

                if postFederalCode:
                    serviceStr = postFederalCode

            self.writeService(record, miacCode, age, profileStr, serviceStr, federalPrice, amount, federalSum)


    def writeService(self, record, miacCode, age, profileStr, serviceStr, price, amount, sum,  lpu1Str=''):
        serviceId = forceRef(record.value('serviceId'))
        self.writeStartElement('USL')
        self.writeTextElement('IDSERV',  ('%8d' % self.serviceNum).strip()) # O N(8) номер записи в реестре услуг
        self.writeTextElement('LPU', miacCode[:6]) #O Т(6) Код МО МО лечения
        self.writeTextElement('LPU_1', lpu1Str, writeEmtpyTag = False) #У Т(6) Подразделение МО Подразделение МО лечения из регионального справочника
        self.writeTextElement('PODR', forceString(record.value('orgStructureCode')), writeEmtpyTag = False) #У N(8) Код отделения Отделение МО лечения из регионального справочника
        self.writeTextElement('PROFIL', profileStr) #O N(3) Профиль Классификатор V002
        self.writeTextElement('DET', (u'1' if age < 18 else u'0')) #О N(1) Признак детского профиля 0-нет, 1-да.
        self.writeTextElement('DATE_IN', forceDate(record.value('begDate')).toString(QtCore.Qt.ISODate)) #O D Дата начала оказания услуги
        self.writeTextElement('DATE_OUT', forceDate(record.value('endDate')).toString(QtCore.Qt.ISODate)) #O D Дата окончания оказания услуги
        self.writeTextElement('DS', forceString(record.value('MKB'))) #O Т(10) Диагноз Код из справочника МКБ до уровня подрубрики
        self.writeTextElement('CODE_USL', serviceStr) #O Т(16) Код услуги Территориальный классификатор услуг
        self.writeTextElement('KOL_USL', ('%6.2f' % amount).strip()) #O N(6.2) Количество услуг (кратность услуги)
        self.writeTextElement('TARIF', ('%15.2f' % price).strip()) #O N(15.2) Тариф
        self.writeTextElement('SUMV_USL', ('%15.2f' % sum).strip()) #O N(15.2) Стоимость медицинской услуги, выставленная к оплате (руб.)
        self.writeTextElement('PRVS', forceString(self.parent.getSpecialityFederalCode(forceRef(record.value('execPersonId'))))) #O N(9) Специальность медработника, выполнившего услугу
        self.writeTextElement('CODE_MD', forceString(self.parent.getPersonFederalCode(forceRef(record.value('execPersonId'))))) #O Т(16) Код медицинского работника, оказавшего медицинскую услугу В соответствии с территориальным справочником
        self.writeEndElement() #USL
        self.serviceNum += 1


    def writeFileHeader(self,  device, fileName, accNumber, accDate, year, month, miacCode, payerCode, accSum):
        self.recNum = 1
        self.caseNum = 1
        self._lastClientId = None
        self.serviceNum = 1
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('ZL_LIST')
        self.writeHeader(fileName, accNumber, accDate, year, month, miacCode, payerCode, accSum)


    def writeHeader(self, fileName, accNumber, accDate, year, month, miacCode, payerCode, accSum):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '1,0')
        self.writeTextElement('DATA', accDate.toString(Qt.ISODate))
        (fname,  ext) = os.path.splitext(os.path.basename(fileName))
        self.writeTextElement('FILENAME', fname[:26])
        self.writeEndElement()

        if not self.parent.chkExportTypeBelonging.isChecked():
            self.writeStartElement('SCHET')
            #self.writeTextElement('CODE', ('%s%s' % (miacCode[-4:], accNumber.rjust(4, '0'))))
            self.writeTextElement('CODE', ('%d' % self.parent.parent.accountId)[:8])
            self.writeTextElement('CODE_MO', miacCode)
            self.writeTextElement('YEAR', year)
            self.writeTextElement('MONTH',  month)
            self.writeTextElement('NSCHET',  forceString(accNumber)[:15])
            self.writeTextElement('DSCHET', accDate.toString(Qt.ISODate))
            self.writeTextElement('PLAT', payerCode[:5], writeEmtpyTag = False)
            self.writeTextElement('SUMMAV', ('%15.2f' % accSum).strip())
            self.writeTextElement('SUMMAP', '0.00')
            self.writeTextElement('SANK_MEK', '0.00')
            self.writeTextElement('SANK_MEE', '0.00')
            self.writeTextElement('SANK_EKMP', '0.00')
            self.writeEndElement()

    def writeTextElement(self, element,  value, writeEmtpyTag = False):
        if not writeEmtpyTag and (not value or value == ''):
            return

        QXmlStreamWriter.writeTextElement(self, element, value)

    def writeFileFooter(self):
        self.writeEndElement() # SLUCH
        self.writeEndElement() # root
        self.writeEndDocument()


    def getPersonPostFederalCode(self, personId):
        result = self.rbPostFederalCache.get(personId, -1)

        if result == -1:
            stmt = """SELECT rbPost.federalCode
                FROM Person
                LEFT JOIN rbPost ON rbPost.id = Person.post_id
                WHERE Person.id = %d""" % personId

            query = QtGui.qApp.db.query(stmt)

            if query and query.first():
                record = query.record()

                if record:
                    result = forceString(record.value(0))

            self.rbPostFederalCache[personId] = result
        return result


    def getPersonPostRegionalCode(self, personId):
        result = self.rbPostRegionalCache.get(personId, -1)

        if result == -1:
            stmt = """SELECT rbPost.regionalCode
                FROM Person
                LEFT JOIN rbPost ON rbPost.id = Person.post_id
                WHERE Person.id = %d""" % personId

            query = QtGui.qApp.db.query(stmt)

            if query and query.first():
                record = query.record()

                if record:
                    result = forceString(record.value(0))

            self.rbPostRegionalCache[personId] = result
        return result


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

# *****************************************************************************************

class CPersonalDataStreamWriter(QXmlStreamWriter):
    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._clientsSet = None


    def writeTextElement(self, element,  value, writeEmtpyTag = False):
        if not writeEmtpyTag and (not value or value == ''):
            return

        QXmlStreamWriter.writeTextElement(self, element, value)


    def writeRecord(self, record):
        clientId = forceRef(record.value('client_id'))
        sex = forceString(record.value('sex'))
        birthDate = forceDate(record.value('birthDate'))

        if clientId in self._clientsSet:
            return

        self.writeStartElement('PERS')
        self.writeTextElement('ID_PAC',  ('%d' % clientId)[:36])

        #Фамилия пациента.
        self.writeTextElement('FAM', forceString(record.value('lastName')))
        #Имя пациента
        self.writeTextElement('IM', forceString(record.value('firstName')))
        #Отчество пациента
        self.writeTextElement('OT', forceString(record.value('patrName')))
        #Пол пациента.
        self.writeTextElement('W', sex)
        #Дата рождения пациента.
        self.writeTextElement('DR', birthDate.toString(QtCore.Qt.ISODate))
        self.writeTextElement('MR', forceString(record.value('birthPlace')), writeEmtpyTag=False)
        # Федеральный код из справочника ТИПЫ ДОКУМЕНТОВ. Из карточки пациента.
        self.writeTextElement('DOCTYPE',  forceString(record.value('documentFederalCode')))
        # Серия документа, удо-стоверяющего личность пациента.
        self.writeTextElement('DOCSER', forceString(record.value('documentSerial')))
        # Номер документа, удостоверяющего личность пациента.
        self.writeTextElement('DOCNUM', forceString(record.value('documentNumber')))
        # СНИЛС пациента.
        self.writeTextElement('SNILS', formatSNILS(forceString(record.value('SNILS'))))
        # Код места жительства по ОКАТО. Берётся из адреса жительство.
        self.writeTextElement('OKATOG', forceString(record.value('placeOKATO')))
        # Код места пребывания по ОКАТО. Берётся из ОКАТО организации, чей полис у пациента.
        self.writeTextElement('OKATOP', forceString(record.value('insurerOKATO')))
        self.writeEndElement() # PERS
        self._clientsSet.add(clientId)


    def writeFileHeader(self,  device, fileName, accDate):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('PERS_LIST')
        self.writeHeader(fileName, accDate)


    def writeHeader(self, fileName, accDate):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '1.0')
        self.writeTextElement('DATA', accDate.toString(Qt.ISODate))
        (fname,  ext) = os.path.splitext(os.path.basename(fileName))
        self.writeTextElement('FILENAME', 'L%s' % fname[1:26])
        self.writeTextElement('FILENAME1', fname[:26])
        self.writeEndElement()

    def writeFileFooter(self):
        self.writeEndElement() # root
        self.writeEndDocument()

# *****************************************************************************************
