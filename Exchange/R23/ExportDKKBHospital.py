# -*- coding: utf-8 -*-

import os.path
from PyQt4 import QtCore, QtGui
from decimal import *

from Accounting.Utils import updateAccountInfo
from Events.Action import ActionStatus
from Exchange.ExportR23Native import getAccountInfo, CBaseExportPage1, CExportPage2, getWeightIfAborted
from Exchange.Utils import isExternalOrgCode, getPersonIdList, getAdditionalPersonIdList
from library.Utils import forceDate, forceDouble, forceInt, forceRef, forceString, forceStringEx, \
    toVariant, calcAgeInYears, formatSex, nameCase, pyDate, calcAgeInDays, formatSNILS, forceDecimal

getcontext().prec = 12


def exportR23DKKBS(widget, accountId, accountItemIdList):
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
        self.setWindowTitle(u'Мастер экспорта в ОМС Краснодарского края (Стационар)')
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
        drugQuery = self.createDrugQuery()
        self.progressBar.setMaximum(max(query.size() + personQuery.size() + drugQuery.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        # i2776: список КСГ, которые не стоит учитывать при формировании счета
        self.ignoredCsg = None

        self.exportedUID = []
        return dbf, query, personQuery, drugQuery

    def exportInt(self):
        self.ignoreErrors = self.chkIgnoreErrors.isChecked()

        dbf, query, personQuery, drugQuery = self.prepareToExport()
        accDate, accNumber, settleDate, contractId = getAccountInfo(self.parent.accountId)
        origAccNumber = accNumber

        accOrgStructureId = forceRef(QtGui.qApp.db.translate('Account', 'id', self.parent.accountId, 'orgStructure_id')) or QtGui.qApp.currentOrgStructureId()
        bookkeeperCode = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', accOrgStructureId , 'bookkeeperCode'))
        if not bookkeeperCode:
            self.log(u'<b><font color=red>ОШИБКА</font></b>: Для текущего ЛПУ не задан код для бухгалтерии', True)
            if not self.ignoreErrors:
                return
        self.log(u'ЛПУ: код для бухгалтерии: "%s".' % bookkeeperCode)

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
            self.log(u'Невозможно привести номер счёта "%s" к числовому виду' % accNumber)

        accType = self.cmbAccountType.code()
        # self.eventInfo = self.getEventInfo()
        self.modernClients = set() # модернизированные пациенты (есть федеральная цена)

        payerId = forceRef(QtGui.qApp.db.translate('Contract', 'id', self.parent.contractId, 'payer_id'))
        payerOGRN = forceString(QtGui.qApp.db.translate('Organisation', 'id', payerId, 'OGRN')) if payerId else ''
        isOutArea = forceInt(QtGui.qApp.db.translate('Contract', 'id', self.parent.contractId, 'exposeDiscipline'))
        isOutArea = ((isOutArea & 0b1100000) >> 5) == 0
        self.log(u'ОГРН плательщика `%s`.' % payerOGRN)

        if self.idList:
            # Составляем множество событий, содержащих услуги с модернизацией
            while query.next():
                record = query.record()
                if record:
                    federalPrice = forceDecimal(record.value('federalPrice'))

                    if federalPrice != 0.0:
                        self.modernClients.add(forceRef(record.value('client_id')))

            query.exec_() # встаем перед первой записью

            self.exportListP = []
            # i3393 D file
            self.personIdForFileD = []
            self.exportedRIDs = []
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), bookkeeperCode, iAccNumber, settleDate, accType, payerOGRN)

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
        #TODO: Выпилить услуги на S и K из запроса, они упразднены.

        stmt = u"""SELECT DISTINCT
              IF(BedProfile.code IS NOT NULL, BedProfile.code, `OrgStructure`.`bookkeeperCode`) AS KPK,
              Account_Item.amount    AS amount,
              Account_Item.id        AS accountItem_id,
              Account_Item.master_id AS account_id,
              Account_Item.event_id  AS event_id,
              Account_Item.action_id AS action_id,
              Event.client_id        AS client_id,
              Event.`order`          AS `order`,
              Event.setDate AS begDate,
              Event.execDate AS endDate,
              Event.`hospParent`     AS `hospParent`,
              Event.dispByMobileTeam AS isDispMobileTeam,
              IF(Account_Item.action_id, Action.begDate, IF(Account_Item.visit_id, Visit.date, Event.setDate)) as servBegDate,
              IF(Account_Item.action_id, Action.endDate, IF(Account_Item.visit_id, Visit.date, Event.execDate)) as servEndDate,
              Visit.visitType_id AS visitTypeId,
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
              Insurer.OKATO AS insurerOKATO,
              Insurer.OGRN AS insurerOGRN,
              Insurer.area AS insurerArea,
              rbPolicyKind.regionalCode AS policyKindCode,
              ClientDocument.serial  AS documentSerial,
              ClientDocument.number  AS documentNumber,
              rbDocumentType.regionalCode AS documentRegionalCode,
              {15_extension}
              IF(clientWorkOrg.title IS NOT NULL,
                  clientWorkOrg.title, ClientWork.freeInput) AS `workName`,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.infis,
                rbEventService.infis
                ) AS service,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.id,
                rbEventService.id
                ) AS serviceId,
              IF(Account_Item.service_id IS NOT NULL,
                Account_Item.service_id,
                IF(Account_Item.action_id IS NOT NULL, Account_Item.action_id, Event.id)
                ) AS cardId,
              IF(Account_Item.action_id IS NOT NULL,
                            IF(Action.person_id IS NOT NULL, Action.person_id, Action.setPerson_id), Event.execPerson_id
                ) AS execPersonId,
              Event.execPerson_id AS pureExecPersonId,
              Action.begDate AS actionDate,
              Diagnosis.MKB          AS MKB,
              AssociatedDiagnosis.MKB AS AssociatedMKB,
              ComplicationDiagnosis.MKB AS ComplicationMKB,
              Account_Item.price   AS price,

              Account_Item.`sum`     AS `sum`,
              Contract_Tariff.federalPrice AS federalPrice,
              LEAST(
                IF(Contract_Tariff.federalLimitation = 0,Account_Item.amount,
                    LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                Account_Item.sum) AS federalSum,
              Person.code AS personCode,
              Person.regionalCode AS personRegionalCode,
              servPerson.regionalCode AS servRegionalPersonCode,
              rbSpeciality.regionalCode AS specialityCode,
              rbSpeciality.federalCode AS fedSpecialityCode,
              rbSpeciality.id AS specialityId,
              servPersonSpeciality.id as servPersonSpecialityId,
              DiagnosticResult.regionalCode AS diagnosticResultCode,
              EventResult.regionalCode AS eventResultCode,
              # (
              #       SELECT org.infisCode FROM OrgStructure org INNER JOIN Person p ON p.orgStructure_id = org.id 
              #       WHERE p.id = IF(
              #           Account_Item.action_id IS NOT NULL, 
              #           COALESCE(Action.person_id, Action.setPerson_id), 
              #           Event.execPerson_id)
              # ) AS orgStructCode,
              OrgStructure.infisCode AS orgStructCode,
              RelegateOrg.infisCode AS RelegateOrgCode,
              Referral.id AS referralId,
              Referral.number AS referralNumber,
              (SELECT rbr.netrica_Code FROM rbReferralType rbr WHERE rbr.id = Referral.type LIMIT 1) AS referralType,
              Referral.date AS referralDate,
              Referral.hospDate AS referralHospDate,
              OutgoingOrg.infisCode AS outgoingOrgCode,
              Event_OutgoingReferral.number AS outgoingRefNumber,
              ActionOrg.infisCode AS actionOrgCode,
              rbEventProfile.code AS eventProfileCode,
              rbMedicalAidType.code AS medicalAidTypeCode,
              rbMedicalAidKind.federalCode AS medicalAidKindFederalCode,
              rbMedicalAidUnit.federalCode AS medicalAidUnitFederalCode,
              IF(Account_Item.service_id IS NOT NULL,
                   ItemMedicalAidProfile.federalCode, EventMedicalAidProfile.regionalCode
                  ) AS medicalAidProfileFederalCode,
              (SELECT Event_LittleStranger.currentNumber FROM Event_LittleStranger WHERE Event_LittleStranger.id = Event.littleStranger_id) as nborn
           FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event_OutgoingReferral ON Event_OutgoingReferral.master_id = Event.id AND Event_OutgoingReferral.deleted = 0
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN Event PolicyEvent ON PolicyEvent.id = IFNULL(Event.id, IFNULL(Action.event_id, Visit.event_id))
            LEFT JOIN ClientPolicy ON ClientPolicy.id = PolicyEvent.clientPolicy_id
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
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
            LEFT JOIN Person ON Person.id = Event.execPerson_id
            LEFT JOIN Person AS setActionPerson ON setActionPerson.id = Action.setPerson_id
            LEFT JOIN Person AS servPerson ON servPerson.id = IF(Account_Item.action_id IS NOT NULL,
                                                                 Action.person_id,
                                                                 IF(Account_Item.visit_id IS NOT NULL,
                                                                    Visit.person_id,
                                                                    Event.execPerson_id))
            LEFT JOIN Diagnostic ON ( Diagnostic.event_id = Account_Item.event_id
                                      AND Diagnostic.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1', '2'))
                                      AND Diagnostic.deleted = 0)
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
            LEFT JOIN ClientWork ON ClientWork.client_id=Event.client_id AND
                        ClientWork.id = (SELECT max(CW.id)
                                         FROM ClientWork AS CW
                                         WHERE CW.client_id=Client.id AND CW.deleted=0)
            LEFT JOIN Organisation AS clientWorkOrg ON clientWorkOrg.id=ClientWork.org_id AND clientWorkOrg.deleted = 0
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN Diagnosis AS AssociatedDiagnosis ON AssociatedDiagnosis.id = AssociatedDiagnostic.diagnosis_id AND AssociatedDiagnosis.deleted = 0
            LEFT JOIN Diagnosis AS ComplicationDiagnosis ON ComplicationDiagnosis.id = ComplicationDiagnostic.diagnosis_id AND ComplicationDiagnosis.deleted = 0
            LEFT JOIN rbDiagnosticResult AS DiagnosticResult ON DiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            # LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id  # setActionPerson
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN rbSpeciality AS servPersonSpeciality ON servPersonSpeciality.id = servPerson.speciality_id
            LEFT JOIN Referral ON ((Referral.id = Event.referral_id) OR (Referral.event_id = Event.id)) AND Referral.deleted = 0 AND Referral.isCancelled = 0
            LEFT JOIN Organisation AS RelegateOrg ON RelegateOrg.id = IF(Event.referral_id IS NULL, Event.relegateOrg_id, Referral.relegateOrg_id)
            LEFT JOIN Organisation AS OutgoingOrg ON OutgoingOrg.id = Referral.relegateOrg_id
            LEFT JOIN Organisation AS ActionOrg ON Action.org_id = ActionOrg.id AND ActionOrg.deleted = 0
            LEFT JOIN rbEventProfile ON EventType.eventProfile_id = rbEventProfile.id
            LEFT JOIN rbMedicalAidProfile AS ItemMedicalAidProfile ON ItemMedicalAidProfile.id = rbItemService.medicalAidProfile_id
            LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id =rbMedicalAidType.id
            LEFT JOIN rbMedicalAidKind ON EventType.medicalAidKind_id = rbMedicalAidKind.id
            LEFT JOIN rbEventProfile AS EventMedicalAidProfile ON
                EventType.eventProfile_id = EventMedicalAidProfile.id
            LEFT JOIN rbMedicalAidUnit ON Account_Item.unit_id = rbMedicalAidUnit.id
            LEFT JOIN OrgStructure_HospitalBed AS OrgsHospBed ON OrgsHospBed.id = 
            (
                SELECT OrgStructure_HospitalBed.id
                FROM Action A
                INNER JOIN ActionType AT ON AT.id = A.actionType_id
                INNER JOIN ActionProperty ON A.id = ActionProperty.action_id
                INNER JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = ActionProperty.id
                INNER JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
                WHERE A.deleted = 0 AND AT.flatCode LIKE 'moving%%'  AND AT.deleted = 0
                    AND A.event_id = Event.id
                    # AND IF(Action.id IS NULL, 1,  Action.endDate >= A.begDate AND Action.endDate <= A.endDate)
                ORDER BY 
                    IF(Action.id IS NULL, 1, Action.endDate BETWEEN A.begDate AND A.endDate) Desc, 

                    CASE WHEN Account_Item.action_id IS NOT NULL THEN A.begDate END ASC,
                    CASE WHEN Account_Item.action_id IS NULL THEN A.begDate END DESC,

                    CASE WHEN Account_Item.action_id IS NOT NULL THEN A.endDate END ASC,
                    CASE WHEN Account_Item.action_id IS NULL THEN A.endDate END DESC,

                    CASE WHEN Account_Item.action_id IS NOT NULL THEN A.id END ASC,
                    CASE WHEN Account_Item.action_id IS NULL THEN A.id END DESC
                LIMIT 1
            )
            LEFT JOIN rbHospitalBedProfile AS BedProfile ON BedProfile.id = OrgsHospBed.profile_id
            LEFT JOIN OrgStructure ON OrgStructure.id = OrgsHospBed.master_id
            LEFT JOIN (SELECT ActionProperty.id,
                          Action.event_id
                        FROM
                          ActionProperty
                        LEFT JOIN ActionPropertyType ON ActionPropertyType.id = ActionProperty.type_id
                        LEFT JOIN Action ON Action.id = ActionProperty.action_id 
                        LEFT JOIN ActionType ON ActionType.id = ActionPropertyType.actionType_id
                        INNER JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id 
                          AND ActionProperty_String.value LIKE "в плановом порядке"
                        WHERE
                          ActionPropertyType.name LIKE "Госпитализирован"
                          AND ActionProperty.deleted = 0
                          AND ActionType.flatCode LIKE "received") ActProp ON ActProp.event_id = Event.id

            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN Account ON Account_Item.master_id = Account.id
            LEFT JOIN Contract ON Account.contract_id = Contract.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND {cond}
        """# .format(tableAccountItem['id'].inlist(self.idList))
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
              (SELECT diagOrg.infisCode FROM Diagnostic visitDiag INNER JOIN Organisation diagOrg ON  diagOrg.id = visitDiag.`org_id` WHERE visitDiag.`id` = Visit.`diagnostic_id` ) AS `diagOrgCode`,
              (SELECT diagOrg.OGRN FROM Diagnostic visitDiag INNER JOIN Organisation diagOrg ON  diagOrg.id = visitDiag.`org_id` WHERE visitDiag.`id` = Visit.`diagnostic_id` ) AS `diagOrgOGRN`,
              (
                  SELECT
                    netricaHospChannel.code 
                  FROM 
                    Action ReceivedAction
                    INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
                    INNER JOIN ActionPropertyType ChannelType ON ReceivedActionType.id = ChannelType.actionType_id AND ChannelType.name = 'Канал доставки'
                    LEFT JOIN ActionProperty ChannelProperty ON ChannelType.id = ChannelProperty.type_id AND ChannelProperty.action_id = ReceivedAction.id
                    LEFT JOIN ActionProperty_Reference ChannelReference ON ChannelProperty.id = ChannelReference.id
                    LEFT JOIN netricaHospChannel ON ChannelReference.value = netricaHospChannel.id
                  WHERE 
                    ReceivedAction.event_id = Event.id 
                    AND ChannelType.deleted = 0 
                    AND ChannelProperty.deleted = 0 
                  LIMIT 1
              ) AS deliveredChanelCode, 
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
                  ORDER BY dateRegistration DESC, id DESC
                  LIMIT 1
              ) AS clientQuotaTicketRegDate,
            """
        )
        return db.query(stmt)

    def createDrugQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """SELECT
              mes.MES.code AS KSTAND,
              ActionType.code AS CODETRN,
              Action.packPurchasePrice AS CENAUP,
              Action.doseRatePrice AS SUMDOZA,
              Event.externalId       AS externalId,
              Account_Item.id        AS accountItem_id,
              Account_Item.master_id AS account_id,
              Account_Item.event_id  AS event_id,
              Account_Item.action_id AS action_id
          FROM Account_Item
          LEFT JOIN Event  ON Event.id  = Account_Item.event_id
          LEFT JOIN Action ON Action.event_id = Event.id
          LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
          LEFT JOIN mes.MES ON Event.MES_id = mes.MES.id
          INNER JOIN mes.MES_medicament ON mes.MES.id = mes.MES_medicament.master_id AND ActionType.code = mes.MES_medicament.medicamentCode
          WHERE
                (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL)
                ) AND %s
                GROUP BY ActionType.code, externalId
        """ % tableAccountItem['id'].inlist(self.idList)
        return db.query(stmt)

    def getEventInfo(self):
        u"""возвращает общую стоимость услуг за пациента"""

        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = u"""SELECT
            Event.id as eventId,
            Event.externalId,
            SUM(sum) AS totalSum,
            MIN(Event.setDate) AS begDate,
            MAX(Event.execDate) AS endDate,
            SUM(LEAST(IF(Contract_Tariff.federalLimitation = 0,
                Account_Item.amount,
                LEAST(Contract_Tariff.federalLimitation, Account_Item.amount)) * Contract_Tariff.federalPrice,
                Account_Item.sum)) AS federalSum
            FROM
                Account_Item
                LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
                LEFT JOIN Event ON Account_Item.event_id = Event.id
                LEFT JOIN EventType ON EventType.id = Event.eventType_id
                LEFT JOIN (SELECT Event.id as id,
                              IF(rbMedicalAidType.code = '7', timestampdiff(DAY, date(Event.setDate), date(Event.execDate)) + 1 - ((WEEK(date(Event.execDate),1)-WEEK(date(Event.setDate),1))*2) - COUNT(holidays.cid),
                                  if(rbMedicalAidType.code = '10', timestampdiff(DAY, date(Event.setDate), date(Event.execDate)) + 1, IF(rbMedicalAidType.code IN ('1', '2', '3') and timestampdiff(DAY, date(Event.setDate), date(Event.execDate)) = 0, timestampdiff(DAY, date(Event.setDate), date(Event.execDate)) + 1, timestampdiff(DAY, date(Event.setDate), date(Event.execDate))))) as fact
                           FROM Event
                              LEFT JOIN EventType ON EventType.id = Event.eventType_id
                              LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
                              LEFT JOIN (SELECT `CalendarExceptions`.`id` AS cid, `CalendarExceptions`.`date` FROM `CalendarExceptions`) AS holidays ON
                                  DATE_FORMAT(holidays.`date`,'%%m-%%d')>= DATE_FORMAT(Event.setDate,'%%m-%%d') AND DATE_FORMAT(holidays.`date`,'%%m-%%d')<= DATE_FORMAT(Event.execDate,'%%m-%%d')
                            GROUP BY id
                            ) AS BedDays ON BedDays.id = Event.id
                LEFT JOIN Visit ON Visit.id = Account_Item.visit_id
                LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
                LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
                LEFT JOIN mes.MES ON Event.MES_id = mes.MES.id
                LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
                LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            WHERE
                Account_Item.reexposeItem_id IS NULL
                AND (Account_Item.date IS NULL
                OR (Account_Item.date IS NOT NULL
                AND rbPayRefuseType.rerun != 0)
                )
                AND %s
                #если период(period) = пребыванию(fact), выводить только стандарт, отбрасывать койко-день (koika)
                #если пребывание меньше периода, то выводится только койко-день, отбраковываем стандарт (standart)
                #если пребывание больше периода, то выводить оба (0)
                AND (
                  (Event.MES_id is NULL)
                 or
                  (rbItemService.infis LIKE 'S%%' AND (BedDays.fact  BETWEEN mes.MES.minDuration AND mes.MES.maxDuration))
                 OR
                  (rbItemService.infis LIKE 'K%%' AND (BedDays.fact < mes.MES.minDuration))
                 OR
                  (rbItemService.infis NOT LIKE 'K%%' AND rbItemService.infis NOT LIKE 'S%%')
                 OR
                  (rbItemService.infis LIKE 'K%%' OR rbItemService.infis LIKE 'S%%') AND (BedDays.fact > mes.MES.maxDuration)
                )
                GROUP BY eventId, externalId;
        """ % (tableAccountItem['id'].inlist(self.idList))
        query = db.query(stmt)

        result = {}
        while query.next():
            record  = query.record()
            # id = forceRef(record.value(0))
            # extId = forceString(record.value(1))
            #FIXME: may be dangerous & slow
            isti = forceString(record.value(1))
            if isti[0:5].upper() == u'ДСДДЦ':
                isti = isti[5:]
            elif isti[0:2].upper() == u'ДС':
                isti = isti[2:]
            sn = forceInt(isti)
            if not sn:
                sn = forceInt(record.value(0))
            if not sn in result:
                result[sn] = (forceDecimal(record.value(2)),
                                    forceDate(record.value(3)),
                                    forceDate(record.value(4)),
                                  forceDecimal(record.value(5)))
            else:
                tmp = result[sn]
                result[sn] = (tmp[0] + forceDecimal(record.value(2)),
                              min(tmp[1], forceDate(record.value(3))),
                              max(tmp[2], forceDate(record.value(4))),
                              tmp[3] + forceDecimal(record.value(5)))
        return result

    def processDrug(self, dbf, record, codeLPU):
        isti = forceString(record.value('externalId'))
        if isti[0:5].upper() == u'ДСДДЦ':
            isti = isti[5:]
        elif isti[0:2].upper() == u'ДС':
            isti = isti[2:]
        sn = forceInt(isti)
        dbfRecord = dbf.newRecord()
        dbfRecord['NS'] = self.edtRegistryNumber.value()
        dbfRecord['SN'] = sn
        dbfRecord['CODE_MO'] = codeLPU
        dbfRecord['KSTAND'] = forceString(record.value('KSTAND'))
        dbfRecord['CODETRN'] = forceInt(record.value('CODETRN'))
        dbfRecord['CENAUP'] = forceDouble(record.value('CENAUP'))
        dbfRecord['SUMDOZA'] = forceDouble(record.value('SUMDOZA'))
        dbfRecord.store()

    def process(self, dbf, record, bookkeeperCode, accNumber, settleDate, accType, payerOGRN):
        db = QtGui.qApp.db
        birthDate = forceDate(record.value('birthDate'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        # Номер стат.талона
        clientId = forceRef(record.value('client_id'))
        eventId = forceRef(record.value('event_id'))
        accountItemId = forceRef(record.value('accountItem_id'))
        number = forceString(record.value('regNumber'))
        corpus = forceString(record.value('regCorpus'))
        flat = forceString(record.value('regFlat'))
        #hospitalFlag = forceBool(record.value('hospitalFlag'))
        referralNumber = forceString(record.value('referralNumber'))
        outgoingOrgCode = forceInt(record.value('outgoingOrgCode'))
        outgoingRefNumber = forceString(record.value('outgoingRefNumber'))
        setOrgCode = forceInt(record.value('RelegateOrgCode'))
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
        externalId = forceString(record.value('externalId'))
        isti = forceString(record.value('externalId'))
        if isti[0:5].upper() == u'ДСДДЦ':
            isti = isti[5:]
        elif isti[0:2].upper() == u'ДС':
            isti = isti[2:]
        sn = forceInt(isti)
        if not sn:
            sn = forceInt(eventId)

        documentNumber = forceString(record.value('documentNumber'))

        (dbfP, dbfU, dbfD, dbfN, dbfR) = dbf
        # FIXME: pirozhok: Временный КК костыль, разобраться почему происходит задвоение
        if accountItemId not in self.exportedUID:
            self.exportedUID.append(accountItemId)
        else:
            return

        # ======================================================================================
        # P FILE
        if not ((sn, modern) in self.exportedClients):
            workOrgName = forceString(record.value('workName'))
            age = calcAgeInYears(birthDate, endDate)

            dbfRecord = dbfP.newRecord()

            # (clientSum, clientBegDate, clientEndDate, clientFederalSum) = self.eventInfo[sn]

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
            DATO = begDate
            dbfRecord['DATO'] = pyDate(DATO)

            # номер реестра счетов (п. 1; 4 примечаний) обязательное
            dbfRecord['NS'] = self.edtRegistryNumber.value()

            # тип реестра счетов (п. 2; 4 примечаний) обязательное SPR21
            dbfRecord['VS'] = accType

            # дата формирования реестра счетов (п. 3; 4 примечаний) обязательное
            dats = self.edtDats.date()
            dbfRecord['DATS'] = pyDate(dats if dats and dats.isValid() else settleDate if settleDate and settleDate.isValid() else QtCore.QDate.currentDate())

            # номер персонального счета (п. 13 примечаний) обязательное
            dbfRecord['SN'] = sn # clientId

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
            dbfRecord['POL']=formatSex(record.value('sex')).upper()

            # дата рождения (п. 7 примечаний) обязательное
            dbfRecord['DATR'] = pyDate(birthDate)

            # категория граждан обязательное SPR09
            # 1 работающий/ 0 не работающий
            if age < 18:
                dbfRecord['KAT'] = 0
            else:
                if not workOrgName:
                    dbfRecord['KAT'] = 0
                else:
                    dbfRecord['KAT'] = 1

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
            if exportAsLittleStranger and weight is not None:
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
            if dbfRecord['SPS'] == '' and dbfRecord['SPN'] == '' and DATO <= QtCore.QDate(2016, 9, 30):
                # нет данных по полису
                flags += '1'
            if exportAsLittleStranger:
                flags += '2'
            if dbfRecord['OTCH'] == '':
                # отсутствие отчества
                flags += '4'
            if forceInt(record.value('hospParent')) == 1:
                flags += '7'
            if forceInt(record.value('isDispMobileTeam')):
                flags += '8'
            if forceInt(record.value('eventProfileCode')) in [211, 232, 252, 261, 262] \
                    and forceInt(record.value('haveRefusedVisit')):
                flags += '9'
            dbfRecord['Q_G'] = forceStringEx(flags)

            if isFromRelegateOrg:
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
            dbfRecord['MP'] = forceString(record.value('MP'))
            # сумма к оплате по случаю заболевания пациента обязательное
            # DROPED i4332
            # dbfRecord['SUMMA_I'] = clientSum
            # табельный номер врача закрывшего талон/историю (п. 17 примечаний) обязательное

            # i3393 P file personCode -> personRegionalCode
            # dbfRecord['DOC_TABN'] = forceString(record.value('personRegionalCode'))

            # i4432 P file: СНИЛС врача из файла D*
            personId = forceInt(record.value('pureExecPersonId'))
            dbfRecord['DOC_SS'] = formatSNILS(forceString(self.getPersonInfoById(personId).value('SNILS')))

            # i4432 P file: код специальности врача, закрывшего талон/историю
            dbfRecord['SPEC'] = forceString(self.getPersonInfoById(personId).value('specialityCode'))

            # i4432 P file: профиль оказанной мед.помощи для всех случаев лечения
            serviceId = forceRef(record.value('serviceId'))
            profile = self.getProfile(serviceId, personId) if personId and serviceId else None
            profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]
            dbfRecord['PROFIL'] = profileStr

            # i4432 P file: вид мед.помощи
            serviceDetail = self.serviceDetailCache.get(serviceId)
            serviveAidProfileCode, serviceAidKindCode, serviceAidTypeCode = self.getAidCodes(
                serviceDetail,
                begDate,
                forceRef(record.value('servPersonSpecialityId')),
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

            # i4432 P file: код диагноза основного заболевания по МКБ–Х
            dbfRecord['MKBX'] = forceString(record.value('MKB'))

            # i4432 P file: цель посещения
            dbfRecord['P_CEL'] = ''  # forceString(record.value('goalRegionalCode'))

            # коды причин возврата (п. 10 примечаний) обязательное для возвратных счетов SPR15
            # dbfRecord['PV']

            # дата возврата обязательное для возвратных счетов
            # dbfRecord['DVOZVRAT']

            # appendToList = True
            # if len(self.exportListP) > 0:
            #    for x in self.exportListP:
            #        if dbfRecord['SN'] == x['SN'] and \
            #                        dbfRecord['DATR'] == x['DATR'] and \
            #                        dbfRecord['FIO'] == x['FIO'] and \
            #                        dbfRecord['IMA'] == x['IMA'] and \
            #                        dbfRecord['OTCH'] == x['OTCH']:
            #            appendToList = False
            #            x['DATO'] = dbfRecord['DATO']
            #            x['SUMMA_I'] += dbfRecord['SUMMA_I']
            #            x['DOC_TABN'] = dbfRecord['DOC_TABN']
            #            break

            # if appendToList:
            #    self.exportListP.append(dbfRecord)

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
                    если указаны коды Нетрики 3,4,5 то выгружаем "3"
                    если указаны коды Нетрики 6,7, то выгружаем "4". 
                Для остальных случаев поле не заполняется. 
            """
            netricaCodeMap = {
                '1': 2,
                '2': 1,
                '3': 3,
                '4': 3,
                '6': 4,
                '7': 4,
                '8': 1
            }
            deliveredChanelCode = netricaCodeMap.get(forceString(record.value('deliveredChanelCode')), None)
            if deliveredChanelCode:
                dbfRecord['P_PER'] = deliveredChanelCode

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

            u"""
                Для корректной выгрузки случаев амбулаторной помощи в приемном отделении в формате выгрузки ДККБ нужно добавить условие:
                если в типе события указан профиль (условие оказания мед.помощи) - приемное отделение (код 112 или 111),
                то в файл P выгружаем: SN=externalId, ISTI=externalId;
                в файл U: SN=externalId.
                Если externalId не введен, то выгружаем client_id.
            """
            if forceString(record.value('eventProfileCode')) in ['111', '112']:
                dbfRecord['SN'] = externalId if externalId else clientId
                dbfRecord['ISTI'] = externalId if externalId else clientId

            appendToList = True
            if len(self.exportListP) > 0:
                for x in self.exportListP:
                    if dbfRecord['SN'] == x['SN']:
                        appendToList = False
                        # x['DATO'] = pyDate(endDate)  # dbfRecord['DATO']
                        # x['SUMMA_I'] += dbfRecord['SUMMA_I']
                        # x['DOC_TABN'] = dbfRecord['DOC_TABN']

            if appendToList:
                self.exportListP.append(dbfRecord)

            # dbfRecord.store()
            self.exportedClients.add((sn, modern))

        # ======================================================================================
        # U FILE
        dbfRecord = dbfU.newRecord()
        # уникальный номер записи об оказанной медицинской услуге в пределах реестра (п. 1 примечаний) обязательное
        dbfRecord['UID'] = accountItemId
        # код МО, оказавшей медицинскую помощь обязательное SPR01
        dbfRecord['CODE_MO'] = bookkeeperCode
        # номер реестра счетов обязательное
        dbfRecord['NS'] = self.edtRegistryNumber.value()
        # номер персонального счета	обязательное
        dbfRecord['SN'] = sn #externalId #clientId
        # код отделения (п. 2, 6 примечаний) обязательное SPR07
        dbfRecord['KOTD'] = forceString(record.value('orgStructCode'))

        # код профиля койки (п. 2 примечаний) обязательное (для стационаров всех типов) SPR08
        # dbfRecord['KPK'] = medicalAidTypeCode
        # if hospitalFlag:
        #    dbfRecord['KPK'] = '00'
        # if medicalAidTypeCode == '7':
        dbfRecord['KPK'] = forceString(record.value('KPK'))

        # код диагноза основного заболевания по МКБ–Х (п. 2 примечаний) обязательное (кроме диагностических услуг) SPR20
        dbfRecord['MKBX'] = forceString(record.value('MKB'))

        # код диагноза сопутствующего заболевания по МКБ–Х (п. 2 примечаний) SPR20
        dbfRecord['MKBXS'] = forceString(record.value('AssociatedMKB'))

        # код диагноза осложнения заболевания по МКБ–Х (п. 2 примечаний) SPR20
        dbfRecord['MKBXO'] = forceString(record.value('ComplicationMKB'))

        # код условия оказания медицинской помощи (п. 2, 3 примечаний) обязательное SPR13
        dbfRecord['VP'] = forceString(record.value('eventProfileCode'))

        # код медицинской услуги обязательное SPR18
        dbfRecord['KUSL'] = forceString(record.value('service'))

        mesId = forceRef(record.value('mesId'))
        maxDur = forceInt(record.value('maxDur'))
        daysFact = forceInt(record.value('amount')) #forceInt(record.value('daysfact'))

        # i3716 U file deprecated
        # резервное поле
        # dbfRecord['KSTAND'] = ''

        # количество услуг обязательное
        amount = forceInt(record.value('amount'))
        if dbfRecord['KUSL'][0:1] == 'K' and amount == 0:
            amount = 1
        dbfRecord['KOLU'] = amount

        if dbfRecord['KUSL'][0:1] in ('G', 'V'):
            dbfRecord['KOLU'] = 1

        # количество койко-дней (дней лечения) обязательное (для стационаров всех типов)
        ## KD должно быть заполнено, только если в поле KUSL стоит стандарт или койко-день
        if dbfRecord['KUSL'][0:1] in ('K', 'S', 'G', 'V'):
            dbfRecord['KD'] = amount


        # код профиля койки (п. 2 примечаний) обязательное для стационаров SPR08
        medicalAidTypeCode = forceString(record.value('medicalAidTypeCode'))
        self.medType = medicalAidTypeCode

        # дата начала выполнения услуги обязательное
        # if dbfRecord['KUSL'][0:1] == 'S':
        #     dbfRecord['KOLU'] = 1
        #     if daysFact > maxDur and medicalAidTypeCode == '7':
        #         endDate = addPeriod(forceDate(record.value('basicBegDate')), forceInt(record.value('maxDur')), False)
        #
        # if dbfRecord['KUSL'][0:1] == 'K':
        #     if daysFact > maxDur and medicalAidTypeCode == '7':
        #         begDate = addPeriod(forceDate(record.value('basicBegDate')), forceInt(record.value('maxDur')), False)

        servDate = forceDate(record.value('actionDate'))
        if not servDate.isValid():
            servDate = begDate

        if not servDate.isValid():
            self.log(u'Не задана дата услуги: accountItemId=%s,' \
                     u' eventId=%s.' % (accountItemId, eventId))

        # дата начала выполнения услуги обязательное
        #dbfRecord['DATN'] = pyDate(begDate)
        dbfRecord['DATN'] = pyDate(forceDate(record.value('servBegDate')))
        if self.ignoredCsg is None:
            from Accounting.Utils import getIgnoredCsgList
            self.ignoredCsg = getIgnoredCsgList()

        for x in self.ignoredCsg:
            if record.value('event_id') == x['idCsg'] and not x['checked']:
                dbfRecord['DATN'] = pyDate(forceDate(x['date']))
                x['checked'] = True
                break

        price = forceDecimal(record.value('sum' if dbfRecord['KUSL'][0] == 'G' else 'price')) # Для КСГ TARU = SUMM

        summ = forceDecimal(record.value('sum'))

        u"""
        # дата окончания выполнения услуги обязательное
        #dbfRecord['DATO'] = pyDate(endDate)
        dbfRecord['DATO'] = pyDate(forceDate(record.value('servEndDate')))


        # тариф на оплату по ОМС (п.5 примечаний) обязательное SPR22
        dbfRecord['TARU'] = price

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
        if status is None and not forceRef(record.value('actPersId')):
            status = forceInt(record.value('diagStatus'))

        if status == ActionStatus.NotDoneByMedicalReasons:  # Не выполнено по мед. противопоказаниям
            dbfRecord['IS_OUT'] = 2
        elif status == ActionStatus.NotDoneByOtherReasons:  # Не выполнено по прочим причинам
            dbfRecord['IS_OUT'] = 3
        elif status == ActionStatus.PatientRefused:  # Пациент отказался от услуги
            dbfRecord['IS_OUT'] = 4
        elif status == ActionStatus.DoneOnTime:  # Выполнено в пределах установленных сроков
            dbfRecord['IS_OUT'] = 1 if actionOrgCode != 0 else 0
        elif status == ActionStatus.DoneWhilstClinicalExamination:  # Выполнено при проведении диспансеризации
            dbfRecord['IS_OUT'] = 1 if isExternalService else 0
        else:
            dbfRecord['IS_OUT'] = 1 if isExternalService else 0

        if dbfRecord['IS_OUT'] == 1:
            dbfRecord['KOLU'] = 0

        u""" i3393 U file
            При этом:
            - если дата выполнения не указана, то в поле DATO выгружаем дату окончания лечения;
            - в поля TARU и SUMM ничего не выгружаем.
            - все обязательные реквизиты (код отделения, код профиля койки, код диагноза основного, и т.п.) заполняются данными на момент обращения в МО.
        """
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
        else:
            # дата окончания выполнения услуги обязательное
            dbfRecord['DATO'] = pyDate(forceDate(record.value('endDate')))

        if isExternalService:
             # код МО, оказавшей услугу (п.4 примечаний) SPR01
            dbfRecord['OUT_MO'] = ('%s' % actionOrgCode).rjust(5, '0')

        # табельный номер сотрудника, оказавшего услугу (п. 7 примечаний)
        # i3393 U file personCode -> servRegionalPersonCode
        # dbfRecord['DOC_TABN'] = forceString(record.value('servRegionalPersonCode'))

        personId = forceRef(record.value('execPersonId'))
        # код специальности специалиста, оказавшего услугу SPR46
        dbfRecord['SPEC'] = forceString(self.getPersonInfoById(personId).value('specialityCode'))

        # i4432 U file: СНИЛС врача закрывшего талон/историю (п. 17 примечаний)
        dbfRecord['DOC_SS'] = formatSNILS(forceString(self.getPersonInfoById(personId).value('SNILS')))
        self.SNILS_fileU.append(forceString(self.getPersonInfoById(personId).value('SNILS')))

        personId = forceRef(record.value('execPersonId'))
        serviceId = forceRef(record.value('serviceId'))
        profile = self.getProfile(serviceId, personId) if personId and serviceId else None
        profileStr = (profile if profile else forceString(record.value('medicalAidProfileFederalCode')))[:3]

        # профиль оказанной медицинской помощи SPR60
        dbfRecord['PROFIL'] = profileStr

        serviceDetail = self.serviceDetailCache.get(serviceId)
        serviveAidProfileCode, serviceAidKindCode, serviceAidTypeCode = self.getAidCodes(serviceDetail,
                                                                                         begDate,
                                                                                         forceRef(record.value('servPersonSpecialityId')),
                                                                                         birthDate,
                                                                                         forceInt(record.value('sex')),
                                                                                         forceString(record.value('MKB')))
        if dbfRecord['IS_OUT'] == 0:
            # вид медицинской помощи SPR59
            dbfRecord['VMP'] = serviceAidKindCode if serviceAidKindCode else forceString(record.value('medicalAidKindFederalCode'))
        else:
            dbfRecord['VMP'] = ''

        # способ оплаты медицинской помощи SPR17
        # dbfRecord['KSO'] = forceString(record.value('medicalAidUnitFederalCode'))

        # i3393 D file
        execPersonId = forceRef(record.value('execPersonId'))
        if execPersonId and execPersonId not in self.personIdForFileD:
            self.personIdForFileD.append(execPersonId)

        # if actionExecPersonId and actionExecPersonId not in self.personIdForFileD:
        #    self.personIdForFileD.append(actionExecPersonId)

        # i3092
        #for x in self.exportListP:
        #    if x['SN'] == clientId:
        #        x['DATO'] = dbfRecord['DATO']
        #        x['SUMMA_I'] += dbfRecord['SUMM']
        #        x['DOC_TABN'] = dbfRecord['DOC_TABN']
        #        break

        if forceString(record.value('eventProfileCode')) in ['111', '112']:
            dbfRecord['SN'] = externalId if externalId else clientId

        if dbfRecord['IS_OUT'] == 0 and status == ActionStatus.DoneWhilstClinicalExamination and not actionOrgCode:
            # dbfRecord['DOC_TABN'] = u''
            dbfRecord['SPEC'] = u''

        # i4447 file U
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

        dbfRecord.store() # U.dbf

        # ======================================================================================
        # N FILE
        if outgoingOrgCode and outgoingRefNumber and not (outgoingOrgCode, outgoingRefNumber) in self.exportedDirections:
            dbfRecord = dbfN.newRecord()
            # i3393: Файл обязателен для медицинских организаций, оказывающих первичную  медико-санитарную помощь,
            # для стационара данные по направлениям выгружаем только в файл P

            dbfRecord['CODE_MO'] = outgoingOrgCode
            dbfRecord['NAPR_N'] = outgoingRefNumber  # '%.5d_%.7d' % (outgoingOrgCode, outgoingRefNumber)
            dbfRecord['NAPR_MO'] = '%.5d' % forceInt(db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
            dbfRecord['NAPR_D'] = pyDate(endDate)
            # dbfRecord['DOC_TABN'] = forceString(record.value('personRegionalCode'))

            personId = forceRef(record.value('execPersonId'))
            dbfRecord['DOC_SS'] = formatSNILS(forceString(self.getPersonInfoById(personId).value('SNILS')))

            dbfRecord.store()
            self.exportedDirections.append((outgoingOrgCode, outgoingRefNumber))
        # ======================================================================================
        # R FILE ONLY FOR R23Native && DKKBHospital