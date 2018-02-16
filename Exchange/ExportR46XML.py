# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil

from library.Utils     import *
from Exchange.Utils import CExportHelperMixin, compressFileInZip
from Exchange.ExportR53Native import CServiceInfoXmlStreamReader

from Ui_ExportR46XMLPage1 import Ui_ExportPage1
from Ui_ExportR46XMLPage2 import Ui_ExportPage2


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'settleDate, number, exposeDate, contract_id, payer_id, date', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('settleDate'))
        aDate  = forceDate(accountRecord.value('date'))
        exposeDate = forceDate(accountRecord.value('exposeDate'))
        strNumber = forceString(accountRecord.value('number')).strip()
        contractId = forceRef(accountRecord.value('contract_id'))
        payerId = forceRef(accountRecord.value('payer_id'))
    else:
        date = exposeDate = contractId = payerId = aDate = strNumber = None
    return date, strNumber, exposeDate, contractId,  payerId,  aDate


def exportR46XML(widget, accountId, accountItemIdList):
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
        self.setWindowTitle(u'Мастер экспорта в Республике Крым')
        self.tmpDir = ''
        self.xmlLocalFileName = ''


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
            self.tmpDir = QtGui.qApp.getTmpDir('R85XML')
        return self.tmpDir


    def getFullXmlFileName(self):
        u"""HPiNiPpNp_YYMMN.XML, где
            H – константа, обозначающая передаваемые данные.
            Pi – Параметр, определяющий организацию-источник:
            T – ТФОМС;
            S – СМО;
            M – МО. 	-	в нашем случаи M
            Ni – Номер источника (Код МИАЦ ЛПУ).
            Pp – Параметр, определяющий организацию -получателя:
            T – ТФОМС;
            S – СМО;
            M – МО	в нашем случаи S
            Np – Номер получателя (Код МИАЦ СМО).
            YY – две последние цифры порядкового номера года отчетного периода.
            MM – порядковый номер месяца отчетного периода - из даты на которую формируется счёт.
            N – порядковый номер пакета. Присваивается в порядке возрастания, начиная со значения «1»,
            увеличиваясь на единицу для каждого следующего пакета в данном отчетном периоде."""
        if not self.xmlLocalFileName:
            lpuInfis = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
            date, number, exposeDate, contractId,  payerId,  aDate = getAccountInfo(self.accountId)

            payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'infisCode'))

            #FIXME: Вместо 85000 лучше брать payerCode
            self.xmlLocalFileName = os.path.join(self.getTmpDir(), \
                u'HM%sT%s_%s%d.xml' % (lpuInfis, '85000', date.toString('yyMM'), self.page1.edtRegistryNumber.value()))
        return self.xmlLocalFileName


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
            'ExportR85XMLIgnoreErrors', False))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkVerboseLog.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR85XMLVerboseLog', False)))
        self.chkIgnoreErrors.setChecked(self.ignoreErrors)
        self.edtRegistryNumber.setValue(forceInt(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR85XMLRegistryNumber', 0))+1)
        self.chkGroupByService.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR85XMLGroupByService', True)))
        self.edtServiceInfoFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR85XMLServiceInfoFileName', '')))
        self.chkIgnoreErrors.setVisible(False)
        self.chkIgnoreErrors.setChecked(True)
        self.chkGroupByService.setVisible(False)
        self.chkVerboseLog.setVisible(False)
        self.edtServiceInfoFileName.setVisible(False)
        #self.edtRegistryNumber.setVisible(False)
        #self.lblRegistryNumber.setVisible(False)
        self.lblServiceInfoFileName.setVisible(False)
        self.btnSelectServiceInfoFileName.setVisible(False)
        self.grbSMO.setVisible(False)


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkIgnoreErrors.setEnabled(not flag)
        self.chkVerboseLog.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.edtRegistryNumber.setEnabled(not flag)
        self.chkGroupByService.setEnabled(not flag)


    def log(self, str, forceLog = True):
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
            QtGui.qApp.preferences.appPrefs['ExportR85XMLIgnoreErrors'] = \
                    toVariant(self.chkIgnoreErrors.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR85XMLVerboseLog'] = \
                    toVariant(self.chkVerboseLog.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR85XMLGroupByService'] = \
                    toVariant(self.chkGroupByService.isChecked())
            QtGui.qApp.preferences.appPrefs['ExportR85XMLServiceInfoFileName'] = \
                    toVariant(self.edtServiceInfoFileName.text())
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


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

    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')
        cond = tableAccountItem['id'].inlist(self.idList)

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
                IF(Account_Item.refuseType_id IS NOT NULL, 0, 1) AS OPLATA,
                Event.client_id        AS client_id,
                Client.lastName,
                Client.firstName,
                Client.patrName,
                Client.birthDate       AS birthDate,
                Client.sex AS sex,
                Client.SNILS AS SNILS,
                Client.birthPlace AS birthPlace,
                age(Client.birthDate, Event.execDate) as clientAge,
                ClientPolicy.serial AS policySerial,
                ClientPolicy.number AS policyNumber,
                ClientPolicy.begDate   AS policyBegDate,
                ClientPolicy.endDate   AS policyEndDate,
                rbPolicyKind.federalCode AS policyKindFederalCode,
                Insurer.OGRN AS insurerOGRN,
                Insurer.OKATO AS insurerOKATO,
                Insurer.area AS insurerArea,
                Insurer.infisCode AS insurerInfis,
                ClientDocument.serial  AS documentSerial,
                ClientDocument.number  AS documentNumber,
                rbDocumentType.federalCode AS documentFederalCode,
                kladr.KLADR.OCATD AS placeOKATO,
                IF(Account_Item.visit_id IS NOT NULL, Visit.person_id,
                    IF(Account_Item.action_id IS NOT NULL,
                        IF(Action.person_id IS NOT NULL, Action.person_id, Action.setPerson_id), Event.execPerson_id)
                ) AS execPersonId,
                Diagnosis.MKB          AS MKB,
                Event.setDate          AS begDate,
                Event.execDate         AS endDate,
                Contract_Tariff.federalPrice AS federalPrice,
                Contract_Tariff.tariffType AS tariffType,
                Contract_Tariff.price AS price, %s
                rbDiagnosticResult.federalCode AS resultFederalCode,
                -- rbMedicalAidType.federalCode AS medicalAidTypeFederalCode,
                rbEventTypePurpose.federalCode AS purposeFederalCode,
                rbMedicalAidKind.federalCode AS medicalAidKindFederalCode,
                IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.federalCode,
                   IF(Account_Item.visit_id IS NOT NULL, VisitMedicalAidProfile.federalCode, EventMedicalAidProfile.regionalCode)
                  ) AS medicalAidProfileFederalCode,
                IF(Account_Item.service_id IS NOT NULL,
                    rbItemService.id,
                    IF(Account_Item.visit_id IS NOT NULL, rbVisitService.id, rbEventService.id)
                    ) AS serviceId,
                AccDiagnosis.MKB AS AccMKB,
                OrgStructure.infisCode AS orgStructureCode,
                rbMedicalAidUnit.federalCode AS medicalAidUnitFederalCode,
                Event.`order`,
                Event.id AS eventId,
                EventResult.federalCode AS eventResultFederalCode,
                rbPayRefuseType.rerun,
                Event_LittleStranger.sex as novorSex,
                Event_LittleStranger.birthDate as novorBirthDate,
                Event_LittleStranger.currentNumber as novorNumber,
                Event_LittleStranger.id IS NOT NULL as isLittleStranger
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN ActionType ON ActionType.id = Action.ActionType_id
            LEFT JOIN rbService ON rbService.id = ActionType.nomenclativeService_id
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
            LEFT JOIN kladr.KLADR ON kladr.KLADR.CODE = RegAddressHouse.KLADRCode
            LEFT JOIN Diagnostic ON Diagnostic.id = (
              SELECT MAX(D.id)
              FROM Diagnostic AS D
              WHERE D.event_id = Account_Item.event_id
                AND ((D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code ='2')
                        AND D.person_id = Event.execPerson_id) OR (
                          D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='1')))
                          AND D.deleted = 0)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            -- LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
            LEFT JOIN rbMedicalAidKind ON EventType.medicalAidKind_id = rbMedicalAidKind.id
            LEFT JOIN rbEventProfile AS EventMedicalAidProfile ON
                EventType.eventProfile_id = EventMedicalAidProfile.id
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
            LEFT JOIN Person ON Person.id = Event.execPerson_id
            LEFT JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
            LEFT JOIN Event_LittleStranger ON Event_LittleStranger.id = Event.littleStranger_id
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
        self.ignoreErrors = True #self.chkIgnoreErrors.isChecked()
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

        recipientId = forceString(QtGui.qApp.db.translate(
            'Contract', 'id', contractId , 'recipient_id'))

        payerCode = None
        payerName = ''

        if payerId:
            payerCode = forceString(QtGui.qApp.db.translate(
                    'Organisation', 'id', payerId, 'infisCode'))

        if not payerCode:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                     u'Для плательщика не задан код МИАЦ', True)
            if not self.ignoreErrors:
                return

        self.recNum = 1

        # загружаем информацию о предварительном реестре для формата 2011.10
        self.preliminaryRegistryInfo = self.getPreliminaryInfo()

        if self.idList:
            file = out
            out = CMyXmlStreamWriter(self)
            clientsOut = CPersonalDataStreamWriter(self)
            out.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            infisCode = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', recipientId, 'infisCode')) #QtGui.qApp.currentOrgId()
            accSum = forceDouble(QtGui.qApp.db.translate(
                'Account', 'id', self.parent.accountId, 'sum'))
            out.writeFileHeader(file, self.parent.getFullXmlFileName(), accNumber, aDate,
                                forceString(accDate.year()),
                                forceString(accDate.month()),
                                infisCode, payerCode, accSum)
            clientsOut.writeFileHeader(clientsFile, self.parent.getFullXmlFileName(), aDate)

            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                out.writeRecord(query.record(), infisCode)
                clientsOut.writeRecord(query.record())

            out.writeFileFooter()
            clientsOut.writeFileFooter()
            file.close()
            clientsFile.close()

            for text in out.xmlErrorsList:
                self.log(u'Ошибка выгрузки данных: %s' % text)
            for text in clientsOut.xmlErrorsList:
                self.log(u'Ошибка выгрузки персональных данных: %s' % text)

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


    @QtCore.pyqtSignature('')
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSignature('')
    def on_btnCancel_clicked(self):
        self.abort()


    @QtCore.pyqtSignature('')
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
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R85XMLExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        success = False

        for src in (self.parent.getFullXmlFileName(),  self.parent.getFullXmlPersFileName()):
            (root, ext) = os.path.splitext(src)
            zipFileName = '%s.zip' % root

            if not compressFileInZip(src, zipFileName):
                break

            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(zipFileName))
            success, result = QtGui.qApp.call(self, shutil.move, (zipFileName, dst))

            if not success:
                break

        if success:
            QtGui.qApp.preferences.appPrefs['R85XMLExportDir'] = toVariant(self.edtDir.text())
            QtGui.qApp.preferences.appPrefs['ExportR85XMLRegistryNumber'] = \
                    toVariant(self.parent.page1.edtRegistryNumber.value())
            self.wizard().setAccountExposeDate()

        return success


    @QtCore.pyqtSignature('QString')
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSignature('')
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ОМС Республики Крым',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))

# *****************************************************************************************

class CMyXmlStreamWriter(QXmlStreamWriter, CExportHelperMixin):
    zglvFields = {'VERSION': True, 'DATA': True, 'FILENAME' : True}
    schetFields = {'CODE': True, 'CODE_MO': True, 'YEAR': True, 'MONTH': True, 'NSCHET': True, 'DSCHET': True, 'SUMMAV': True,
                            'COMENTS': False, 'SUMMAP': False, 'SANK_MEK': False, 'SANK_MEE': False, 'SANK_EKMP': False, 'PLAT': False}
    pacientFields = {'ID_PAC': True, 'SMO': False, 'VPOLIS': True, 'SPOLIS': False, 'NPOLIS': True, 'NOVOR': True,
                            'SMO_OGRN': False, 'SMO_OK': False, 'SMO_NAM': False}
    sluchFields = {'PODR': True, 'IDDOKT': True, 'IDCASE': True, 'USL_OK': True, 'VIDPOM': True, 'EXTR': False, 'LPU': True, 'PROFIL': True, 'DET': True, 
                            'NHISTORY': True, 'DATE_1': True, 'DATE_2': True, 'DS0': False, 'DS1': True, 'DS2': False, 'CODE_MES1': False, 'CODE_MES2': False, 'RSLT': True,
                            'ISHOD': True, 'PRVS': True, 'VERS_SPEC': False, 'IDSP': True, 'ED_COL': False, 'TARIF': False, 'SUMV': True,
                            'OPLATA': False, 'SUMP': False, 'REFREASON': False, 'CODE_MES1': False, 'CODE_MES2': False, 'FOR_POM': False,
                            'SANK_MEK': False, 'SANK_MEE': False, 'SANK_EKMP': False, 'COMENTSL': False, 'OS_SLUCH': False, 'LPU_1': False, 'NPR_MO': False}
    uslFields = {'PROFIL': True, 'IDSERV': True, 'LPU': True, 'PROFIL': True, 'DET': True, 'DATE_IN': True, 'DATE_OUT': True, 'DS': True, 'KOL_USL': True,
                        'TARIF': True, 'SUMV_USL': True, 'PRVS': True, 'COMENTU': False, 'PODR': False, 'CODE_USL': True, 'CODE_MD': True, 'LPU_1': False}

    groupMap = {'ZGLV': zglvFields, 'SCHET': schetFields, 'PACIENT': pacientFields, 'SLUCH': sluchFields, 'USL': uslFields}  


    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        CExportHelperMixin.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.recNum = 1
        self.caseNum = 1
        self.serviceNum = 1
        self._lastClientId = None
        self.curGroupName = ''
        self.xmlErrorsList = []
        self.medicalAidProfileCache = {}
        self.clientStr = u''

    def getProfile(self, serviceId, personId):
        key = (serviceId, personId)
        result = self.medicalAidProfileCache.get(key, -1)

        if result == -1:
            result = None
            if not (serviceId and personId):
                return result
            stmt = """SELECT rbMedicalAidProfile.code
            FROM rbService_Profile
            LEFT JOIN rbSpeciality ON rbSpeciality.id = rbService_Profile.speciality_id
            LEFT JOIN Person ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN rbMedicalAidProfile ON rbService_Profile.medicalAidProfile_id = rbMedicalAidProfile.id
            WHERE rbService_Profile.master_id = %s AND Person.id = %s
            """ % (serviceId, personId)

            query = QtGui.qApp.db.query(stmt)

            if query and query.first():
                record = query.record()

                if record:
                    result = forceString(record.value(0))

            self.medicalAidProfileCache[key] = result

        return result


    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)


    def writeTextElement(self, element,  value, writeEmtpyTag = False):
        if self.groupMap.has_key(self.curGroupName):
            gr = self.groupMap[self.curGroupName]
            if gr.has_key(element):
                if gr[element] and (not value or value == ''):
                    self.xmlErrorsList.append(u'обязательное поле %s в группе %s не заполнено. Номер записи: %d, пациент: %s' % (element, self.curGroupName, self.recNum, self.clientStr))
                    return
                elif (not value or value == ''):
                    return
            else:
                self.xmlErrorsList.append(u'неизвестное поле %s = %s в группе %s. Номер записи: %d' % (element, value, self.curGroupName, self.recNum))

        if not writeEmtpyTag and (not value or value == ''):
            return
        
        QXmlStreamWriter.writeTextElement(self, element, value)

    def writeRecord(self, record, infisCode):
        clientId = forceRef(record.value('client_id'))
        self.clientStr = u'%s %s %s' % (forceString(record.value('lastName')), forceString(record.value('firstName')), forceString(record.value('patrName')))
        age = forceInt(record.value('clientAge'))
        specialCase = []

        if self._lastClientId != clientId: # новая запись, иначе - новый случай
            if self._lastClientId:
                self.recNum += 1
                self.writeEndElement() # ZAP

            self._lastClientId = clientId
            self.writeStartElement('ZAP')

            self.writeTextElement('N_ZAP', ('%4d' % self.recNum).strip())
            self.writeTextElement('PR_NOV', '1' if forceInt(record.value('rerun')) !=  0 else  '0')

            self.writeStartElement('PACIENT')
            self.writeTextElement('ID_PAC',  ('%d' % clientId)[:36])
            spolis = forceString(record.value(u'policySerial'))[:10]
            npolis = forceString(record.value(u'policyNumber'))[:20]
            # Региональный код справочника ВИДЫ ПОЛИСОВ.
            vpolis = forceString(record.value('policyKindFederalCode'))[:1]
            if not vpolis:
                if len(npolis) == 16:
                    vpolis = '3'
                elif len(npolis) == 9:
                    vpolis = '2'
                else:
                    vpolis = '1'

            self.writeTextElement('VPOLIS', vpolis)
            if spolis.lower() not in (u'еп', u'вс'):
                self.writeTextElement('SPOLIS', spolis)
            self.writeTextElement('NPOLIS', npolis)
            if forceString(record.value('insurerInfis')) == '':
                   self.writeTextElement('SMO_OGRN', forceString(record.value('insurerOGRN'))[:15])
                   self.writeTextElement('SMO_OK', forceString(record.value('insurerOKATO'))[:5])
            else:
                  self.writeTextElement('SMO', '%s' % forceString(record.value('insurerInfis'))[:5]) #46
            self.writeTextElement('SMO_NAM', forceString(record.value('insurerName'))[:100], writeEmtpyTag = False)
            novorBirthDate = forceDate(record.value('novorBirthDate'))
            novorSex = forceInt(record.value('novorSex'))
            novorNumber = forceInt(record.value('novorNumber'))
            self.writeTextElement('NOVOR', '0' if novorBirthDate.isNull() else '%s%s%s' % (novorSex, novorBirthDate.toString('ddMMyy'), novorNumber))
            self.writeEndElement() # PACIENT

        self.writeStartElement('SLUCH')
        self.writeTextElement('IDCASE', '%d' % self.caseNum)
        # Федеральный код справочника НАЗНАЧЕНИЕ ТИПА СОБЫТИЯ
        # Ранее - medicalAitTypeFederalCode
        serviceCode = forceString(record.value('purposeFederalCode'))
        self.writeTextElement('USL_OK',  serviceCode)
        self.writeTextElement('VIDPOM', forceString(record.value('medicalAidKindFederalCode')))
        #self.writeTextElement('NPR_MO','')
        # 1 – плановая; 2 – экстренная ИЗ СОБЫТИЯ
        self.writeTextElement('EXTR', '2' if forceInt(record.value('order')) == 2 else '1')
        #У N(8) Код отделения Отделение МО лечения из регионального справочника
        self.writeTextElement('LPU', '%s' % infisCode[:6]) #460
        self.writeTextElement('PODR', forceString(record.value('orgStructureCode')), writeEmtpyTag = False) 

        personId = forceRef(record.value('execPersonId'))
        profile = self.getProfile(forceRef(record.value('serviceId')), personId)
        profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]

        self.writeTextElement('PROFIL', profileStr) #forceString(record.value('medicalAidProfileFederalCode'))[:3]
        self.writeTextElement('DET', (u'1' if age < 18 else u'0'))
        self.writeTextElement('NHISTORY', forceString(record.value('eventId'))[:50])
        # Дата начала события
        self.writeTextElement('DATE_1', forceDate(record.value('begDate')).toString(QtCore.Qt.ISODate))
        # Дата окончания события
        self.writeTextElement('DATE_2', forceDate(record.value('endDate')).toString(QtCore.Qt.ISODate))
        self.writeTextElement('DS1', forceString(record.value('MKB')))
        self.writeTextElement('DS2', forceString(record.value('AccMKB')))
        self.writeTextElement('RSLT', forceString(record.value('eventResultFederalCode')))
        # Федеральный код из справочника РЕЗУЛЬТАТ ОСМОТРА. Результат ЗАКЛЮЧИТЕЛЬНОГО ДИАГНОЗА.
        self.writeTextElement('ISHOD', forceString(record.value('resultFederalCode')))
        self.writeTextElement('PRVS', forceString(self.parent.getSpecialityFederalCode(personId)))
        self.writeTextElement('VERS_SPEC', 'V015')
        self.writeTextElement('IDDOKT', forceString(self.parent.getPersonFederalCode(personId)))
        self.writeTextElement('IDSP', forceString(record.value('medicalAidUnitFederalCode')))
        self.writeTextElement('ED_COL', '%.2f' % forceDouble(record.value('amount')))
        eventOrder = forceInt(record.value('order'))
        forPom = '1' if eventOrder == 2 else '3' #or eventAidTypeCode == '4' else 3
        self.writeTextElement('FOR_POM', forPom)

        if not forceString(record.value('patrName')):
            self.writeTextElement('OS_SLUCH', '2')

        price = forceDouble(record.value('price'))
        sum = forceDouble(record.value('sum'))

        self.writeTextElement('TARIF', ('%.2f' % price))
        self.writeTextElement('SUMV', ('%.2f' % sum))
        self.writeTextElement('OPLATA', '0')#forceString(record.value('OPLATA')))
        self.writeTextElement('SUMP', ('%.2f' % sum))

        # Работа со словарем данных о предварительном реестре
        eventId = forceInt(record.value('event_id'))
        serviceId = forceInt(record.value('service_id'))
        visitId = forceInt(record.value('visit_id'))
        actionId = forceInt(record.value('action_id'))
        key = (eventId, serviceId, visitId, actionId)
        (pAccNum, pAccDate, pRecNum) = self.parent.preliminaryRegistryInfo.get(key, ('', '', ''))
        self.caseNum+= 1

        federalSum = forceDouble(record.value('federalSum'))
        federalPrice = forceDouble(record.value('federalPrice'))

        #TODO: find all usl by sluch 

        #if forceString(record.value('codeUsl')):

        codeUsl = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'code'))

        ttype = forceInt(record.value('tariffType'))

        #if ttype != 0 and ttype != 3:
        if serviceId:
            self.writeService(record, infisCode, age, price, sum, codeUsl, profileStr)
        #if federalPrice > 0:
        #    self.writeService(record, infisCode, age, federalPrice, federalSum, '2')

        self.serviceNum = 1
        self.writeEndElement() # SLUCH


    def writeService(self, record, infisCode, age, price, sum, code, profileStr):
        serviceId = forceRef(record.value('serviceId'))
        self.writeStartElement('USL')
        self.writeTextElement('IDSERV',  ('%8d' % self.serviceNum).strip()) # O N(8) номер записи в реестре услуг
        self.writeTextElement('LPU', '%s' % infisCode[:6]) #O Т(6) Код МО МО лечения #460
        #self.writeTextElement('LPU_1', forceString(record.value('orgStructureCode'), writeEmtpyTag = False) #У Т(6) Подразделение МО Подразделение МО лечения из регионального справочника
        self.writeTextElement('PODR', forceString(record.value('orgStructureCode')), writeEmtpyTag = False) #У N(8) Код отделения Отделение МО лечения из регионального справочника
        self.writeTextElement('PROFIL', profileStr) #O N(3) Профиль Классификатор V002
        self.writeTextElement('DET', (u'1' if age < 18 else u'0')) #О N(1) Признак детского профиля 0-нет, 1-да.
        self.writeTextElement('DATE_IN', forceDate(record.value('begDate')).toString(QtCore.Qt.ISODate)) #O D Дата начала оказания услуги
        self.writeTextElement('DATE_OUT', forceDate(record.value('endDate')).toString(QtCore.Qt.ISODate)) #O D Дата окончания оказания услуги
        self.writeTextElement('DS', forceString(record.value('MKB'))) #O Т(10) Диагноз Код из справочника МКБ до уровня подрубрики
        self.writeTextElement('CODE_USL', code) #O Т(16) Код услуги Территориальный классификатор услуг
        self.writeTextElement('KOL_USL', ('%.2f' % forceDouble(record.value('amount')))) #O N(6.2) Количество услуг (кратность услуги)
        self.writeTextElement('TARIF', ('%.2f' % price)) #O N(15.2) Тариф
        self.writeTextElement('SUMV_USL', ('%.2f' % sum)) #O N(15.2) Стоимость медицинской услуги, выставленная к оплате (руб.)
        self.writeTextElement('PRVS', forceString(self.parent.getSpecialityFederalCode(forceRef(record.value('execPersonId'))))) #O N(9) Специальность медработника, выполнившего услугу
        self.writeTextElement('CODE_MD', forceString(self.parent.getPersonFederalCode(forceRef(record.value('execPersonId'))))) #O Т(16) Код медицинского работника, оказавшего медицинскую услугу В соответствии с территориальным справочником
        self.writeEndElement() #USL
        self.serviceNum += 1


    def writeFileHeader(self,  device, fileName, accNumber, accDate, year, month, infisCode, payerCode, accSum=0.0):
        self._lastClientId = None
        self.recNum = 1
        self.caseNum = 1
        self.serviceNum = 1
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('ZL_LIST')
        self.writeHeader(fileName, accNumber, accDate, year, month, infisCode, payerCode, accSum)


    def writeHeader(self, fileName, accNumber, accDate, year, month, infisCode, payerCode, accSum):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '2.1')
        self.writeTextElement('DATA', accDate.toString(Qt.ISODate))
        (fname,  ext) = os.path.splitext(os.path.basename(fileName))
        self.writeTextElement('FILENAME', fname[:26])
        self.writeEndElement()
        self.writeStartElement('SCHET')
        self.writeTextElement('CODE', ('%s%s' % (infisCode, forceString(self.parent.edtRegistryNumber.value())))[:8]) #46
        self.writeTextElement('CODE_MO',  u'%s' % infisCode) #460
        self.writeTextElement('YEAR', year)
        self.writeTextElement('MONTH',  month)
        self.writeTextElement('NSCHET',  forceString(accNumber))
        self.writeTextElement('DSCHET', accDate.toString(Qt.ISODate))
        self.writeTextElement('PLAT', '%s' % '85000') #payerCode[:5], writeEmtpyTag = False) #46
        self.writeTextElement('SUMMAV', ('%.2f' % accSum))
        self.writeEndElement()


    def writeFileFooter(self):
        self.writeEndElement() # root
        self.writeEndDocument()

# *****************************************************************************************

class CPersonalDataStreamWriter(QXmlStreamWriter):
    persZglvFields = {'VERSION': True, 'DATA': True, 'FILENAME' : True, 'FILENAME1' : True}
    persFields = {'ID_PAC': True, 'FAM': True, 'IM': True, 'OT': True, 'W': True, 'DR': True, 'FAM_P': False, 'IM_P': False, 
                        'OT_P': False, 'W_P': False, 'DR_P': False, 'MR': False, 'DOCTYPE': False, 'DOCSER': False, 'DOCNUM': False, 'SNILS': False, 
                        'OKATOG': False, 'OKATOP': False, 'COMENTP': False, 'COMENTZ': False, 'DOST': False}
    groupMap = {'ZGLV': persZglvFields, 'PERS': persFields}
              
    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._clientsSet = None
        self.xmlErrorsList = []
        self.clientStr = u''


    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)


    def writeTextElement(self, element,  value, writeEmtpyTag = False):
        if self.groupMap.has_key(self.curGroupName):
            gr = self.groupMap[self.curGroupName]
            if gr.has_key(element):
                if gr[element] and (not value or value == ''):
                    self.xmlErrorsList.append(u'обязательное поле %s в группе %s не заполнено. Ид пациента: %s, пациент: %s' % (element, self.curGroupName, forceString(self.clientId), self.clientStr))
                    if not writeEmtpyTag:
                        return
                # elif (not value or value == ''):
                #     return
            else:
                self.xmlErrorsList.append(u'неизвестное поле %s = %s в группе %s. Ид пациента: %s' % (element, value, self.curGroupName, forceString(self.clientId)))

        if not writeEmtpyTag and (not value or value == ''):
            return
        
        QXmlStreamWriter.writeTextElement(self, element, value)


    def writeRecord(self, record):
        self.clientId = forceRef(record.value('client_id'))
        self.clientStr = u'%s %s %s' % (forceString(record.value('lastName')), forceString(record.value('firstName')), forceString(record.value('patrName')))
        sex = forceString(record.value('sex'))
        birthDate = forceDate(record.value('birthDate'))

        if self.clientId in self._clientsSet:
            return

        self.writeStartElement('PERS')
        self.writeTextElement('ID_PAC',  ('%d' % self.clientId)[:36])

        #Фамилия пациента.
        lastName = forceString(record.value('lastName'))
        firstName = forceString(record.value('firstName'))
        patrName = forceString(record.value('patrName'))

        isLittleStranger = forceBool(record.value('isLittleStranger'))
        if not isLittleStranger:
            self.writeTextElement('FAM', lastName)
            #Имя пациента
            self.writeTextElement('IM', firstName)
            #Отчество пациента
            self.writeTextElement('OT', patrName)
        else:
            self.writeTextElement('FAM', '', writeEmtpyTag=True)
            self.writeTextElement('IM', '', writeEmtpyTag=True)
            self.writeTextElement('OT', '', writeEmtpyTag=True)
            self.writeTextElement('FAM_P', lastName)
            self.writeTextElement('IM_P', firstName)
            self.writeTextElement('OT_P', patrName)

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
        if not patrName:
            self.writeTextElement('DOST', '1')
        if not lastName:
            self.writeTextElement('DOST', '2')
        if not firstName:
            self.writeTextElement('DOST', '3')
        self.writeEndElement() # PERS
        self._clientsSet.add(self.clientId)


    def writeFileHeader(self,  device, fileName, accDate):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('PERS_LIST')
        self.writeHeader(fileName, accDate)


    def writeHeader(self, fileName, accDate):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '2.1')
        self.writeTextElement('DATA', accDate.toString(Qt.ISODate))
        (fname,  ext) = os.path.splitext(os.path.basename(fileName))
        self.writeTextElement('FILENAME', 'L%s' % fname[1:26])
        self.writeTextElement('FILENAME1', fname[:26])
        self.writeEndElement()

    def writeFileFooter(self):
        self.writeEndElement() # root
        self.writeEndDocument()

# *****************************************************************************************
