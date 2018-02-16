# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

##### Передача данных (односторонняя) из ЛПУ в РЦОД - обмен между двумя Виста-Медами #####
## TODO: при передаче рег. данных - адреса, отметка о прикреплении?

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *

from library.database   import connectDataBaseByInfo, decorateString
from library.exception import CDatabaseException
from library.Utils      import forceDate, forceDateTime, forceDouble, forceInt, forceRef, forceString
from Exchange.Utils     import prepareRefBooksCacheById
from Exchange.reg_iemk.iemc_settings import CRegIemcSettings
from IemcServer_services import *
from IemcServer_services_types import ns0


def createExportR67Query(db, mode, limit = 0):

    # limitValue = forceInt(limit)
    # limitStr = 'LIMIT 0, %d' % limitValue if limitValue else ''
    # Простите)
    # dateCond = ''
    # if date:
    #     dateCond = u" WHERE Event.%(dateField)s >= TIMESTAMP('%(date)s')" % \
    #                             {'dateField': 'modifyDatetime' if mode == 0 else 'clientDatetime',
    #                             'date': forceDateTime(date).toString('yyyy-MM-ddThh:mm:ss')}
    eventIdList = None
    if limit:
        limitStmt = u'''SELECT Event.id
        FROM Event
            LEFT JOIN ExportStatus ON ExportStatus.event_id = Event.id
            INNER JOIN Client ON Client.id = Event.client_id
        WHERE (ExportStatus.id IS NULL OR ExportStatus.status = 0)
            AND Event.execDate IS NOT NULL
            AND Client.deleted = 0
            AND Event.deleted = 0
        LIMIT %s
        ''' % limit
        limitQuery = db.query(limitStmt)
        eventIdList = []
        while limitQuery.next():
            eventIdList.append(forceInt(limitQuery.record().value(0)))

    if eventIdList == []:
        return None
    limitStr = u''
    if eventIdList:
        limitStr = u' AND Event.id IN (%s)' % ', '.join([str(eventId) for eventId in eventIdList])
    stmt = u"""SELECT
            Client.modifyDatetime       AS clientModifyDatetime,
            Client.id                   AS client_id,
            Client.lastName             AS clientLastName,
            Client.firstName            AS clientFirstName,
            Client.patrName             AS clientPatrName,
            Client.birthDate            AS clientBirthDate,
            Client.sex                  AS clientSex,
            Client.SNILS                AS SNILS,
            Client.birthPlace           AS birthPlace,

            ClientPolicy.serial         AS policySerial,
            ClientPolicy.number         AS policyNumber,
            ClientPolicy.begDate        AS policyBegDate,
            ClientPolicy.endDate        AS policyEndDate,
            ClientPolicy.policyType_id  AS policyTypeId,
            ClientPolicy.policyKind_id  AS policyKindId,
            ClientPolicy.name           AS policyName,
            Insurer.miacCode            AS insurerCode,

            ClientDocument.serial           AS documentSerial,
            ClientDocument.number           AS documentNumber,
            ClientDocument.documentType_id  AS documentTypeId,
            ClientDocument.date             AS documentDate,
            ClientDocument.origin           AS origin,

            kladr.KLADR.OCATD AS placeOKATO,

            Event.id                AS eventId,
            Event.modifyDatetime    AS eventModifyDatetime,
            Event.setDate           AS eventSetDate,
            Event.execDate          AS eventExecDate,
            EventType.code          AS eventTypeCode,
            EventExecPerson.code    AS eventExecPersonCode,
            Event.externalId        AS externalId,
            Event.isPrimary         AS eventIsPrimary,
            Event.order             AS eventOrder,
            Event.result_id         AS eventResultId,
            LPU.miacCode            AS eventOrgCode,
            MES.code                AS MEScode,

            Diagnostic.id               AS diagnosticId,
            Diagnostic.diagnosisType_id AS diagnosticTypeId,
            Diagnostic.character_id     AS diagnosticCharacterId,
            Diagnostic.stage_id         AS diagnosticStageId,
            Diagnostic.phase_id         AS diagnosticPhaseId,
            Diagnostic.setDate          AS diagnosticSetDate,
            Diagnostic.endDate          AS diagnosticEndDate,
            DiagnosticPerson.code       AS diagnosticPersonCode,
            Diagnostic.result_id        AS diagnosticResultId,
            Diagnosis.MKB               AS diagnosisMKB,

            Visit.id            AS visitId,
            Visit.scene_id      AS visitSceneId,
            Visit.visitType_id  AS visitType_id,
            VisitPerson.code    AS visitPersonCode,
            Visit.isPrimary     AS visitIsPrimary,
            Visit.date          AS visitDate,
            VisitService.code   AS visitServiceCode,
            Visit.finance_id    AS visitFinanceId,

            Action.id                   AS actionId,
            ActionType.code              AS actionTypeCode,
            Action.status               AS actionStatus,
            Action.begDate              AS actionBegDate,
            Action.endDate              AS actionEndDate,
            ActionPerson.code           AS actionPersonCode,
            Action.amount               AS actionAmount,
            Action.uet                  AS actionUet,
            Action.MKB                  AS actionMKB,
            ActionLPU.miacCode          AS actionOrgCode,
            Action.duration             AS actionDuration,
            ActionProperty.id           AS actionPropertyId,
            ActionPropertyType.name     AS actionPropertyTypeName,
            -- ActionLPU.code           AS actionOrgCode,

            CONVERT(IF(ActionPropertyType.typeName IN ('String', 'Text', 'Constructor', 'Жалобы'), ActionProperty_String.value,
            IF(ActionPropertyType.typeName = 'Integer', ActionProperty_Integer.value,
            IF(ActionPropertyType.typeName = 'Time', ActionProperty_Time.value,
            IF(ActionPropertyType.typeName = 'Double', ActionProperty_Double.value,
            IF(ActionPropertyType.typeName = 'Date', ActionProperty_Date.value, 0))))), CHAR) as actionPropertyValue
            -- IF(ActionPropertyType.typeName = 'Temperature', ActionProperty_Temperature.value,
            -- IF(ActionPropertyType.typeName = 'ArterialPressure', ActionProperty_ArterialPressure.value,
            -- IF(ActionPropertyType.typeName = 'Pulse', ActionProperty_Pulse.value, 0)))

        FROM Client
        INNER JOIN Event ON Event.client_id = Client.id AND Event.deleted = 0 AND Event.execDate IS NOT NULL
        LEFT JOIN ExportStatus ON ExportStatus.event_id = Event.id AND ExportStatus.status != 0
        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                  ClientPolicy.id = (SELECT MAX(CP.id)
                                     FROM   ClientPolicy AS CP
                                     LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                                     WHERE  CP.client_id = Client.id AND CP.deleted=0 AND CPT.code IN ('1','2')
                  )
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
        LEFT JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
        LEFT JOIN rbMedicalAidKind ON rbMedicalAidKind.id = EventType.medicalAidKind_id
        LEFT JOIN rbEventGoal ON rbEventGoal.id = Event.goal_id
        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        LEFT JOIN Person AS EventExecPerson ON EventExecPerson.id = Event.execPerson_id
        LEFT JOIN Person AS EventSetPerson ON EventSetPerson.id = Event.setPerson_id
        LEFT JOIN Person AS EventAssistantPerson ON EventAssistantPerson.id = Event.assistant_id
        LEFT JOIN mes.MES ON MES.id = Event.mes_id

        LEFT JOIN Visit ON Visit.event_id = Event.id AND Visit.deleted = 0
        LEFT JOIN Person AS VisitPerson ON VisitPerson.id = Visit.person_id
        LEFT JOIN rbService AS VisitService ON VisitService.id = Visit.service_id

        LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
        LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
        LEFT JOIN Person AS DiagnosticPerson ON DiagnosticPerson.id = Diagnostic.person_id
        LEFT JOIN Person AS DiagnosisPerson ON DiagnosisPerson.id = Diagnosis.person_id

        LEFT JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
        LEFT JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
        LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.typeName IN ('Double', 'Integer', 'String', 'Date', 'Time', 'Html', 'Text', 'Constructor', 'Жалобы')
        LEFT JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.action_id = Action.id AND ActionProperty.deleted = 0
        LEFT JOIN Person AS ActionPerson ON ActionPerson.id = Action.person_id

        -- LEFT JOIN ActionProperty_Action ON ActionProperty_Action.id = Action.id
        -- LEFT JOIN ActionProperty_ArterialPressure ON ActionProperty_ArterialPressure.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_BlankNumber ON ActionProperty_BlankNumber.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_BlankSerial ON ActionProperty_BlankSerial.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_Client_Quoting ON ActionProperty_Client_Quoting = ActionProperty.id
        LEFT JOIN ActionProperty_Date ON ActionProperty_Date.id = ActionProperty.id
        LEFT JOIN ActionProperty_Double ON ActionProperty_Double.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_Image ON ActionProperty_Image.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_ImageMap ON ActionProperty_ImageMap.id = ActionProperty.id
        LEFT JOIN ActionProperty_Integer ON ActionProperty_Integer.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_Job_Ticket ON ActionProperty_Job_Ticket.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_Organisation
        -- LEFT JOIN ActionProperty_Pulse ON ActionProperty_Pulse.id = ActionProperty.id
        LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
        -- LEFT JOIN ActionProperty_Temperature ON ActionProperty_Temperature.id = ActionProperty.id
        LEFT JOIN ActionProperty_Time ON ActionProperty_Time.id = ActionProperty.id

        LEFT JOIN Organisation AS ActionLPU ON ActionLPU.id = Action.org_id
        LEFT JOIN Organisation AS LPU ON LPU.id = Event.org_id
        WHERE ExportStatus.id IS NULL %(limit)s
                ORDER BY Client.%(dateField)s,
                        `Client`.lastName,
                        `Client`.firstName,
                        `Client`.patrName,
                        Client.id,
                        Event.%(dateField)s,
                        Event.id,
                        Action.id,
                        ActionProperty.id,
                        Visit.id,
                        Diagnostic.id
                %(limit)s""" % {'dateField': 'modifyDatetime' if mode == 0 else 'clientDatetime',
                                #'dateCond': dateCond,
                         'limit': limitStr}
    query = db.query(stmt)
    return query

def createExportR67ClientsQuery(db, mode, date, limit = 0):

    limitValue = forceInt(limit)
    limitStr = 'LIMIT 0, %d' % limitValue if limitValue else ''
    dateCond = ''
    if date:
        dateCond = u" WHERE (Client.%(dateField)s >= TIMESTAMP('%(date)s'))" % \
               {'dateField': 'modifyDatetime' if mode == 0 else 'createDatetime',
                'date': forceDate(date).toString('yyyy-MM-dd')}

    stmt = u"""SELECT
            Client.modifyDatetime       AS clientModifyDatetime,
            Client.id                   AS client_id,
            Client.lastName             AS clientLastName,
            Client.firstName            AS clientFirstName,
            Client.patrName             AS clientPatrName,
            Client.birthDate            AS clientBirthDate,
            Client.sex                  AS clientSex,
            Client.SNILS                AS SNILS,
            Client.birthPlace           AS birthPlace,

            ClientPolicy.serial         AS policySerial,
            ClientPolicy.number         AS policyNumber,
            ClientPolicy.begDate        AS policyBegDate,
            ClientPolicy.endDate        AS policyEndDate,
            ClientPolicy.policyType_id  AS policyTypeId,
            ClientPolicy.policyKind_id  AS policyKindId,
            ClientPolicy.name           AS policyName,
            Insurer.miacCode            AS insurerCode,

            ClientDocument.serial           AS documentSerial,
            ClientDocument.number           AS documentNumber,
            ClientDocument.documentType_id  AS documentTypeId,
            ClientDocument.date             AS documentDate,
            ClientDocument.origin           AS origin,

            kladr.KLADR.OCATD AS placeOKATO

        FROM Client
        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                  ClientPolicy.id = (SELECT MAX(CP.id)
                                     FROM   ClientPolicy AS CP
                                     LEFT JOIN rbPolicyType AS CPT ON CPT.id = CP.policyType_id
                                     WHERE  CP.client_id = Client.id AND CP.deleted=0 AND CPT.code IN ('1','2')
                  )
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
       %(dateCond)s
               ORDER BY Client.%(dateField)s,
                        `Client`.lastName,
                        `Client`.firstName,
                        `Client`.patrName,
                        Client.id
                %(limit)s""" % {'dateField': 'modifyDatetime' if mode == 0 else 'createDatetime',
                                'dateCond': dateCond,
                                'limit': limitStr}

    return db.query(stmt)

# class CExportWizard(QtGui.QWizard):
#     def __init__(self, parent=None):
#         QtGui.QWizard.__init__(self, parent)
#         self.setWizardStyle(QtGui.QWizard.ModernStyle)
#         self.page1 = CExportPage1(self)
#         self.page2 = CExportPage2(self)
#         self.addPage(self.page1)
#         self.addPage(self.page2)
#         self.setWindowTitle(u'Мастер экспорта в Смоленской области')
#         self.tmpDir = ''
#         self.xmlLocalFileName = ''
#         self.fileName = ''
#
#     def getTmpDir(self):
#         if not self.tmpDir:
#             self.tmpDir = QtGui.qApp.getTmpDir('R67XML')
#         return self.tmpDir
#
#     def getFullXmlFileName(self):
#         self.xmlLocalFileName = os.path.join(self.tmpDir, self.getTxtFileName())
#         return self.xmlLocalFileName
#
#     def getTxtFileName(self):
#         if not self.fileName:
#             self.fileName = u'HM_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
#         return self.fileName
#
#     def cleanup(self):
#         if self.tmpDir:
#             QtGui.qApp.removeTmpDir(self.tmpDir)
#             self.tmpDir = ''
#
#     def exec_(self):
#         QtGui.QWizard.exec_(self)
#         self.cleanup()

#
# class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1, CExportHelperMixin):
#     def __init__(self, parent):
#         QtGui.QWizardPage.__init__(self, parent)
#         self.setupUi(self)
#         CExportHelperMixin.__init__(self)
#         self.progressBar.setMinimum(0)
#         self.progressBar.setMaximum(1)
#         self.progressBar.setText('')
#
#         self.setTitle(u'Экспорт для Смоленской области')
#         self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')
#
#         self.setExportMode(False)
#         self.aborted = False
#         self.done = False
#         self._cache = smartDict()
#         self.parent = parent
#         self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
#
#     def setExportMode(self, flag):
#         self.btnCancel.setEnabled(flag)
#         self.btnExport.setEnabled(not flag)
#         #self.chkIgnoreErrors.setEnabled(not flag)
#         #self.chkVerboseLog.setEnabled(not flag)
#         self.btnExport.setEnabled(not flag)
#         self.chkExportEvents.setEnabled(not flag)
#         #self.edtRegistryNumber.setEnabled(not flag)
#         #self.chkGroupByService.setEnabled(not flag)
#
#     def log(self, str, forceLog = True):
#         #if self.chkVerboseLog.isChecked() or forceLog:
#         self.logBrowser.append(str)
#         self.logBrowser.update()
#
#     def prepareRefBooks(self):
#         self._cache = prepareRefBooksCacheById()
#
#     def prepareToExport(self):
#         self.done = False
#         self.aborted = False
#         self.emit(QtCore.SIGNAL('completeChanged()'))
#         self.setExportMode(True)
#         output = self.createXML()
#         self.progressBar.reset()
#         self.progressBar.setMaximum(1)
#         self.progressBar.setValue(0)
#         self.progressBar.setText(u'Запрос в БД...')
#         QtGui.qApp.processEvents()
#         if self.chkExportEvents.isChecked():
#             query = self.createQuery()
#         else:
#             query = self.createClientsQuery()
#         self.progressBar.setMaximum(max(query.size(), 1))
#         self.progressBar.reset()
#         self.progressBar.setValue(0)
#         return output, query
#
#     def export(self):
#         (result, rc) = QtGui.qApp.call(self, self.exportInt)
#         self.setExportMode(False)
#         if self.aborted or not result:
#             self.progressBar.setText(u'прервано')
#         else:
#             self.progressBar.setText(u'готово')
#             # QtGui.qApp.preferences.appPrefs['ExportR46XMLIgnoreErrors'] = \
#             #         toVariant(self.chkIgnoreErrors.isChecked())
#             # QtGui.qApp.preferences.appPrefs['ExportR46XMLVerboseLog'] = \
#             #         toVariant(self.chkVerboseLog.isChecked())
#             # QtGui.qApp.preferences.appPrefs['ExportR46XMLGroupByService'] = \
#             #         toVariant(self.chkGroupByService.isChecked())
#             # QtGui.qApp.preferences.appPrefs['ExportR46XMLServiceInfoFileName'] = \
#             #         toVariant(self.edtServiceInfoFileName.text())
#             self.done = True
#             self.emit(QtCore.SIGNAL('completeChanged()'))
#
# # *****************************************************************************************
#
#     def getTxtFileName(self):
#         lpuCode = forceString(QtGui.qApp.db.translate(
#             'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
#         return forceString(lpuCode + u'.TXT')
#
#     def createTxt(self):
#         txt = QFile(os.path.join(self.parent.getTmpDir(), self.getTxtFileName()))
#         txt.open(QIODevice.WriteOnly | QIODevice.Text)
#         txtStream =  QTextStream(txt)
#         txtStream.setCodec('CP866')
#         return txt,  txtStream
#
#     def createClientsQuery(self):
#         limit = self.edtRecordsCount.value()
#         date = self.edtStartDate.date()
#         return createExportR67ClientsQuery(QtGui.qApp.db, 0, date, limit)
#
#     def createQuery(self):
#         date = self.edtStartDate.date()
#         limit = self.edtRecordsCount.value()
#         return createExportR67Query(QtGui.qApp.db, 0, date, limit)
#
# # *****************************************************************************************
#
#     def exportInt(self):
#         self.prepareRefBooks()
#         out, query = self.prepareToExport()
#         clientsOut = CPersonalDataStreamWriter(self, self._cache)
#         clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
#         clientsOut.writeFileHeader(out, self.parent.getFullXmlFileName(), QtCore.QDate.currentDate())
#         if query.size() > 0:
#             while query.next():
#                 QtGui.qApp.processEvents()
#                 if self.aborted:
#                     break
#                 self.progressBar.step()
#                 clientsOut.writeRecord(query.record())
#
#             clientsOut.closeEverything()
#             clientsOut.writeFileFooter()
#             out.close()
#         else:
#             self.log(u'Нечего выгружать.')
#             self.progressBar.step()
#
# # *****************************************************************************************
#
#     def createXML(self):
#         outFile = QtCore.QFile(self.parent.getFullXmlFileName())
#         outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
#         return outFile
#
# # *****************************************************************************************
#
#     def isComplete(self):
#         return self.done
#
#     def abort(self):
#         self.aborted = True
#
#     @QtCore.pyqtSignature('')
#     def on_btnExport_clicked(self):
#         self.export()
#
#     @QtCore.pyqtSignature('')
#     def on_btnCancel_clicked(self):
#         self.abort()
#
# # *****************************************************************************************
#
# # *****************************************************************************************
#
#     def validatePage(self):
#         return True

# class CExportPage2(QtGui.QWizardPage, Ui_ExportPage2):
#     def __init__(self, parent):
#         QtGui.QWizardPage.__init__(self, parent)
#         self.parent = parent
#         self.setupUi(self)
#         self.setTitle(u'Экспорт для Смоленской области')
#         self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')
#
#         self.pathIsValid = True
#         homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
#         exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R67XMLExportDir', homePath))
#         self.edtDir.setText(exportDir)
#
#
#     def isComplete(self):
#         return self.pathIsValid
#
#     def validatePage(self):
#
#         srcFullName = self.parent.getFullXmlFileName()
#         dst = os.path.join(forceStringEx(self.edtDir.text()),
#                                             self.parent.getTxtFileName())
#         success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))
#
#         QtGui.qApp.preferences.appPrefs['R67XMLExportDir'] = toVariant(self.edtDir.text())
#
#         return success
#
#     @QtCore.pyqtSignature('QString')
#     def on_edtDir_textChanged(self):
#         dir = forceStringEx(self.edtDir.text())
#         pathIsValid = os.path.isdir(dir)
#         if self.pathIsValid != pathIsValid:
#             self.pathIsValid = pathIsValid
#             self.emit(QtCore.SIGNAL('completeChanged()'))
#
#     @QtCore.pyqtSignature('')
#     def on_btnSelectDir_clicked(self):
#         dir = QtGui.QFileDialog.getExistingDirectory(self,
#                 u'Выберите директорию для сохранения файла выгрузки в ОМС Смоленской области',
#                  forceStringEx(self.edtDir.text()),
#                  QtGui.QFileDialog.ShowDirsOnly)
#         if forceString(dir):
#              self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))


class CPersonalDataStreamWriter(QXmlStreamWriter):
    def __init__(self, parent, cache, miacCode = None):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)

        self._clientsSet = set()
        self.prevClientId = None
        self.prevEventId = None
        self.prevDiagId = None
        self.prevActionId = None
        self.prevVisitId = None
        self.cache = cache
        self.visits = []
        self.diags = []
        self.actions = []
        self.actionProperties = []
        self.processedProperties = []
        self._processedEvents = set()
        self._processedClients = set()
        self._failedEvents = {}
        self.miacCode = miacCode
        self.failedEvent = False
        self._clientDataSaved = []

        self._clients = []
        self.currentClient = None

    def clearCurrentData(self):
        #self.clientData = ns0.ClientType_Def('_Client')
        self.eventData = ns0.EventType_Def('_Event')
        self.actionData = ns0.ActionType_Def('_Action')
        self.diags = []
        self.visits = []
        self.actions = []
        self.processedProperties = []
        #self.clientData._Event = []

    def writeRecord(self, record):
        clientId = forceRef(record.value('client_id'))
        eventId = forceRef(record.value('eventId'))
        diagId = forceRef(record.value('diagnosticId'))
        visitId = forceRef(record.value('visitId'))
        actionId = forceRef(record.value('actionId'))
        actionPropertyId = forceRef(record.value('actionPropertyId'))

        if not self.prevClientId is None and self.prevClientId != clientId:
            if not self.prevEventId is None:
                if not self.failedEvent:
                    # self.writeEventData()
                    self.clientData._Event.append(self.eventData)
                    self._processedEvents.add(self.prevEventId)
                self.clearCurrentData()
                self.failedEvent = False
            if self.clientData._Event:
                self._clients.append(self.clientData)
            #self.writeEndElement()      # client
            self.prevActionId = None
            self.prevVisitId = None
            self.prevDiagId = None
            self.prevEventId = None
            self._clientDataSaved = False
            self._processedClients.add(self.prevClientId)
        if self.prevClientId is None or self.prevClientId != clientId:
            self.prevClientId = clientId
            self.clientData = ns0.ClientType_Def('_Client')
            # self.clientData = {}
            self.clientData._ClientId = forceInt(record.value('client_id'))
            self.clientData._modifyDatetime = forceDateTime(record.value('clientModifyDatetime')).toString(Qt.ISODate)
            self.clientData._lastName = forceString(record.value('clientLastName'))
            self.clientData._firstName = forceString(record.value('clientFirstName'))
            self.clientData._patrName = forceString(record.value('clientPatrName'))
            self.clientData._sex = forceInt(record.value('clientSex'))
            self.clientData._birthDate = forceDate(record.value('clientBirthDate')).toString(Qt.ISODate)
            self.clientData._birthPlace = forceString(record.value('birthPlace'))
            self.clientData._SNILS = forceString(record.value('SNILS'))
            self.clientData._Event = []

            document = ns0.DocumentType_Def('_document')
            documentTypeId = forceRef(record.value('documentTypeId'))
            if documentTypeId:
                document._documentTypeCode = self.cache.documentType[documentTypeId]['code']
                document._serial = forceString(record.value('documentSerial'))
                document._number = forceString(record.value('documentNumber'))
                document._date = forceDate(record.value('documentDate')).toPyDate()
                document._origin = forceString(record.value('origin'))
                self.clientData._document = document

            policy = ns0.DocumentType_Def('_policy')
            policyTypeId = forceRef(record.value('policyTypeId'))
            if policyTypeId:
                policy._policyTypeCode = self.cache.policyType[policyTypeId]['code']
                policyKindId = forceRef(record.value('policyKindId'))
                if policyKindId:
                    policy._policyKindCode = self.cache.policyKind[policyKindId]['code']
                policy._serial = forceString(record.value('policySerial'))
                policy._begDate = forceDate(record.value('policyBegDate')).toString(Qt.ISODate)
                policy._endDate = forceDate(record.value('policyEndDate')).toString(Qt.ISODate)
                policy._name = forceString(record.value('policyName'))
                policy._insurerCode = forceString(record.value('insurerCode'))
                self.clientData._policy = policy

            self.clientData._RegAddress = forceString(record.value('regAddress'))
            self.clientData._LocAddress = forceString(record.value('locAddress'))

        # Началась обработка нового события. Старое сохраняем.
        # Если не записали рег. данные - пишем и их.
        if not self.prevEventId is None and self.prevEventId != eventId:
            if not self.failedEvent:
                # self.writeEventData()
                self.clientData._Event.append(self.eventData)
                self._processedEvents.add(self.prevEventId)
            self.clearCurrentData()
            self.failedEvent = False

        if self.failedEvent:
            return
        if eventId:
            if self.prevEventId != eventId or self.prevEventId is None:
                self.prevEventId = eventId
                self.eventData = ns0.EventType_Def('_Event')
                self.eventData._modifyDatetime = forceDateTime(record.value('eventModifyDatetime')).toString(Qt.ISODate)
                self.eventData._setDate = forceDateTime(record.value('eventSetDate')).toString(Qt.ISODate)
                self.eventData._execDate = forceDateTime(record.value('eventExecDate')).toString(Qt.ISODate)
                eventTypeCode = forceString(record.value('eventTypeCode'))
                if not eventTypeCode:
                    self.failedEvent = True
                    self._failedEvents[eventId] = u'Не указан код типа события'
                    return
                self.eventData._eventTypeCode = eventTypeCode
                self.eventData._execPersonCode = forceString(record.value('eventExecPersonCode'))
                self.eventData._externalId = forceInt(eventId)
                self.eventData._isPrimary = forceInt(record.value('eventIsPrimary'))
                self.eventData._order = forceInt(record.value('eventOrder'))
                self.eventData._orgCode = forceString(record.value('eventOrgCode'))
                resultId = forceRef(record.value('eventResultId'))
                resultCode = self.cache.result.get(resultId, {}).get('code', None)
                if not resultCode:
                    self.failedEvent = True
                    self._failedEvents[eventId] = u'Не определен код результата события'
                    return
                self.eventData._resultCode = resultCode
                self.eventData._MESCode = forceString(record.value('MEScode'))
                self.eventData._Diagnosis = []
                self.eventData._Visit = []
                self.eventData._Action = []

            if diagId and not diagId in self.diags:
                tempDiag = ns0.DiagnosisType_Def('_Diagnosis')
                tempDiag._diagnosticTypeCode = self.cache.diagnosisType[forceRef(record.value('diagnosticTypeId'))]['code']
                diagnosticCharacterId = forceRef(record.value('diagnosticCharacterId'))
                if diagnosticCharacterId:
                    tempDiag._diagnosticCharacterCode = self.cache.diseaseCharacter[diagnosticCharacterId]['code']
                diagnosticStageId = forceRef(record.value('diagnosticStageId'))
                if diagnosticStageId:
                    tempDiag._diagnosticStageCode = self.cache.diseaseStage[diagnosticStageId]['code']
                diagnosticPhaseId = forceRef(record.value('diagnosticPhaseId'))
                if diagnosticPhaseId:
                    tempDiag._diagnosticPhaseCode = self.cache.diseasePhases[diagnosticPhaseId]['code']
                tempDiag._diagnosticSetDate = forceDate(record.value('diagnosticSetDate')).toString(Qt.ISODate)
                tempDiag._diagnosticEndDate = forceDate(record.value('diagnosticEndDate')).toString(Qt.ISODate)
                tempDiag._diagnosticPersonCode = forceString(record.value('diagnosticPersonCode'))
                diagnosticResultId = forceRef(record.value('diagnosticResultId'))
                if diagnosticResultId:
                    tempDiag._diagnosticResultCode = self.cache.diagnosticResult[diagnosticResultId]['code']
                tempDiag._MKB = forceString(record.value('diagnosisMKB'))
                self.eventData._Diagnosis.append(tempDiag)
                self.diags.append(diagId)

                # self.diags[diagId] = tempDiag

            if visitId and not visitId in self.visits:
                tempVisit = ns0.VisitType_Def('_Visit')
                sceneId = forceRef(record.value('visitSceneId'))
                if sceneId:
                    tempVisit._sceneCode =  self.cache.scene[sceneId]['code']
                visitTypeCode = self.cache.visitType[forceRef(record.value('visitType_id'))]['code']
                if not visitTypeCode:
                    self.failedEvent = True
                    self._failedEvents[eventId] = u'Не указан код типа посещения'
                    return
                tempVisit._visitTypeCode = visitTypeCode
                tempVisit._personCode = forceString(record.value('visitPersonCode'))
                tempVisit._isPrimary = forceInt(record.value('visitIsPrimary'))
                tempVisit._date = forceDate(record.value('visitDate')).toPyDate()
                tempVisit._serviceCode = forceString(record.value('visitServiceCode'))
                financeId = forceRef(record.value('visitFinanceId'))
                financeCode = self.cache.finance.get(financeId, {}).get('code', None)
                if not financeCode:
                    self.failedEvent = True
                    self._failedEvents[eventId] = u'Не определен код типа финансирования в посещении'
                    return
                tempVisit._financeCode = financeCode

                self.eventData._Visit.append(tempVisit)
                self.visits.append(visitId)
                # self.visits[visitId] = tempVisit

            if actionId and not actionId in self.actions:
                self.actionData = ns0.ActionType_Def('_Action')
                actionTypeCode = forceString(record.value('actionTypeCode'))
                if not actionTypeCode:
                    self.failedEvent = True
                    self._failedEvents[eventId] = u'Не указан код типа действия'
                self.actionData._actionTypeCode = actionTypeCode
                self.actionData._status = forceInt(record.value('actionStatus'))
                self.actionData._begDate = forceDateTime(record.value('actionBegDate')).toString(Qt.ISODate)
                self.actionData._endDate = forceDateTime(record.value('actionEndDate')).toString(Qt.ISODate)
                self.actionData._personCode = forceString(record.value('actionPersonCode'))
                self.actionData._amount = forceDouble(record.value('actionAmount'))
                self.actionData._uet = forceDouble(record.value('actionUet'))
                self.actionData._MKB = forceString(record.value('actionMKB'))
                self.actionData._orgCode = forceString(record.value('actionOrgCode'))
                self.actionData._duration = forceInt(record.value('actionDuration'))
                self.actionData._ActionProperty = []
                self.eventData._Action.append(self.actionData)
                self.actions.append(actionId)
                # self.actions[actionId] = tempAction

            if actionId and actionPropertyId and not actionPropertyId in self.processedProperties:
                # if not actionId in self.actionProperties:
                #     self.actionProperties[actionId] = []
                tempActionProperty = ns0.ActionPropertyType_Def('_ActionProperty')
                tempActionProperty._actionPropertyType = forceString(record.value('actionPropertyTypeName'))
                tempActionProperty._actionPropertyValue = forceString(record.value('actionPropertyValue'))
                self.processedProperties.append(forceRef(actionPropertyId))
        self._clientsSet.add(clientId)

    def markExported(self, errors):
        """Пометить объект экспортированным, чтобы он не попадал в выгрузку в дальнейшем.

        @param fieldId: идентификатор записи, которую помечаем обработанной
        @param isClient: True - строка из Client, False - строка из Event
        """
        ## На данный момент рег. данные и мед. карта не могут быть записаны одновременно. Таким образом, если у нас есть
        # переданные обращения, мы не считаем переданными рег. данные, т.к. они не будут записаны в базу РЦОД при импорте.
        if errors or self._failedEvents:
            stmt = 'INSERT INTO ExportStatus (client_id, event_id, status, note) VALUES '
            if errors:
                values = []
                for err in errors:
                    _type = err.Type.lower()
                    clientId, eventId = ('NULL', err.RemoteId) if _type == 'event' else (err.RemoteId, 'NULL')
                    status, message = ('1', '\'\'') if err.Description.lower() == 'success' else ('2', decorateString(err.Description))
                    values.append((clientId, eventId, status, message))
                stmt += ', '.join('(%s, %s, %s, %s)' % value for value in values)
            if errors and self._failedEvents:
                stmt += ', '
            if self._failedEvents:
                stmt += ', '.join(['(NULL, %s, 2, %s)' % (eventId, decorateString(note)) \
                                                                  for (eventId, note) in self._failedEvents.items()])
            stmt += ' ON DUPLICATE KEY UPDATE status = VALUES(status), note=VALUES(note)'
            QtGui.qApp.db.query(stmt).exec_()
            return

            # if self._processedEvents or self._failedEvents:# or self._processedClients:
            #     stmt = 'INSERT INTO ExportStatus (client_id, event_id, status, note) VALUES '
            #     # stmt += ', '.join('(%s, NULL, 1)' % clientId for clientId in self._processedClients)
            #     # if self._processedClients and self._processedEvents:
            #     #     stmt += ', '
            #     stmt += ', '.join('(NULL, %s, 1, \'\')' % eventId for eventId in self._processedEvents)
            #     if self._processedEvents and self._failedEvents:
            #         stmt += ', '
            #     stmt += ', '.join(['(NULL, %s, 3, %s)' % (eventId, decorateString(note)) \
            #                                                       for (eventId, note) in self._failedEvents.items()])
            #     stmt += ' ON DUPLICATE KEY UPDATE status = VALUES(status), note = VALUES(note)'
            #     QtGui.qApp.db.query(stmt).exec_()
            # Пометить часть обращений ошибочными, не передавая их лишний раз.

    def closeEverything(self):
        """
        Выполняется после обработки всех данных - запись данных по последнему обработанному обращению, если они есть.
        """
        if not self.prevEventId is None:
            if not self.failedEvent:
                self.clientData._Event.append(self.eventData)
                self._processedEvents.add(self.prevEventId)
            self.clearCurrentData()
            self.failedEvent = False
        # К окончанию экспорта остается незакрытый тег <Client>
        if not self.prevClientId is None: self._processedClients.add(self.prevClientId)
        self.writeEndElement()

    def writeFileHeader(self,  device):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('IEMC')
        self.writeEmptyElement('ORG')
        self.writeAttribute('code', forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode')) if not self.miacCode else self.miacCode)
        self.writeStartElement('PERS_LIST')

    def writeHeader(self, fileName, accDate):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '1.0')
        self.writeEndElement()

    def writeFileFooter(self):
        self.writeEndElement() # PERS_LIST
        self.writeEndElement() # IEMC
        self.writeEndDocument()

    def isEmpty(self):
        """Выгрузили ли мы кого-нибудь без ошибок. Если нет, удалить файл.

        @return:
        """
        return not (self._processedEvents or self._processedClients)

    def getClients(self):
        return self._clients
# *****************************************************************************************

def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Import IEMC or Reg Data to to specified database.')
    parser.add_argument('-c', dest='config', type=str, default='reg_iemc',
                        help='name of config file without extension. reg_iemc by default')

    args = vars(parser.parse_args(sys.argv[1:]))
    app = QtCore.QCoreApplication(sys.argv)
    settings = CRegIemcSettings(args['config'])
    connectionInfo = settings.getConnectionInfo()
    loc = IemcServerLocator()
    webServiceHost = settings.getServiceHost()
    webServicePort = settings.getServicePort()
    fp = open('debug.out', 'a')
    port = loc.getIemcServer(url="http://%s:%s/iemcServer" % (webServiceHost, webServicePort), tracefile=fp)

    try:
        db = connectDataBaseByInfo(connectionInfo)
    except CDatabaseException, e:
        print u"Couldn't connect to database: %s" % e.message
        sys.exit(-1)

    QtGui.qApp.db = db
    cdt = (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))

    query = createExportR67Query(db, 0, limit=settings.getLimit())

    #TODO: mode?
    if query and query.size() > 0 :
        cache = prepareRefBooksCacheById(db)
        clientsOut = CPersonalDataStreamWriter(None, cache, settings.getMiacCode())

        while query.next():
            clientsOut.writeRecord(query.record())
        clientsOut.closeEverything()
        msg = SendEventDataRequest()
        msg._Org = settings.getMiacCode()
        #msg._Org = '12345'
        msg._Clients = ns0.ClientListType_Def('_Clients')
        clients = clientsOut.getClients()
        if clients:
            msg._Clients._Client = clients
            rsp = port.SendEventData(msg)
            clientsOut.markExported(rsp.Error)
        else:
            clientsOut.markExported([])

        # clientsOut.writeFileFooter()
        # outFile.close()
        # if clientsOut.isEmpty():
        #     outFile.remove()

    db.close()

if __name__ == '__main__':
    main()