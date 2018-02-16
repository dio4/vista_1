# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

##### Передача данных (односторонняя) из ЛПУ в РЦОД - обмен между двумя Виста-Медами #####

import os.path

from library.database  import *
from library.Utils     import *
from Events.Action     import CAction
from Exchange.Utils import prepareRefBooksCacheById


# Выгружаемые данные:
# Дата создания документа
# Даты начала и окончания оказания услуги
# Автор документа (ФИО, СНИЛС/федеральный код)
# Врач, оказавший услугу (ФИО, СНИЛС)
# Медицинская организация (OID, название, максимально подробный адрес)
# Номер и название документа
# Номер истории болезни
# Федеральный код специальности врача

RCDP_UUID = '0a65d58e-1c2a-4e0a-99bf-c776f2331c42'
#RCDP_ID = '1.2.643.5.1.13.3.25.77.761'
RCDP_ID = '1.2.643.5.1.13.3.25.67.19'
RCDP_NAME =  u'ОГАУЗ "СОМИАЦ"'
#RCDP_ID = '1.2.643.5.1.13.3.25.67.71'
#RCDP_NAME = u'ОГБУЗ "Ельнинская ЦРБ"'


def createExportR67FIEMKQuery(db, mode, date, limit = 0):

    limitValue = forceInt(limit)
    limitStr = 'LIMIT 0, %d' % limitValue if limitValue else ''
    # Простите)
    dateCond = ''
    if date:
        dateCond = u" WHERE Event.%(dateField)s >= TIMESTAMP('%(date)s')" % \
                                {'dateField': 'modifyDatetime' if mode == 0 else 'clientDatetime',
                                'date': forceDateTime(date).toString('yyyy-MM-ddThh:mm:ss')}
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

            ClientContact.contact           AS clientPhoneNumber,

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
            LPU.id                  AS eventOrgId,
            MES.code                AS MEScode,
            ModifyPerson.federalCode        AS modifyPersonFederalCode,
            ModifyPerson.lastName           AS modifyPersonLastName,
            ModifyPerson.firstName          AS modifyPersonFirstName,
            ModifyPerson.patrName           AS modifyPersonPatrName,
            EventExecPerson.federalCode     AS eventExecPersonFederalCode,
            EventExecPerson.lastName        AS eventExecPersonLastName,
            EventExecPerson.firstName       AS eventExecPersonFirstName,
            EventExecPerson.patrName        AS eventExecPersonPatrName,
            EventExecPerson.regionalCode    AS eventExecPersonRegionalCode,
            EventExecPersonSpeciality.federalCode   AS eventExecPersonSpecialityFederalCode,
            EventExecPerson.SNILS           AS eventExecPersonSnils,
            #'12311125321'           AS eventExecPersonSnils,

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
        LEFT JOIN ClientContact ON ClientContact.id = (SELECT MAX(id) FROM ClientContact cc WHERE cc.client_id = Client.id AND cc.deleted = 0)
        LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id AND
                  ClientRegAddress.id = (SELECT MAX(CRA.id)
                                     FROM   ClientAddress AS CRA
                                     WHERE  CRA.type = 0 AND CRA.client_id = Client.id AND CRA.deleted=0)
        LEFT JOIN Address   RegAddress ON RegAddress.id = ClientRegAddress.address_id
        LEFT JOIN AddressHouse RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
        LEFT JOIN kladr.KLADR ON kladr.KLADR.CODE = RegAddressHouse.KLADRCode
        LEFT JOIN Event ON Event.client_id = Client.id AND Event.deleted = 0 AND Event.execDate IS NOT NULL
        LEFT JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
        LEFT JOIN rbMedicalAidKind ON rbMedicalAidKind.id = EventType.medicalAidKind_id
        LEFT JOIN rbEventGoal ON rbEventGoal.id = Event.goal_id
        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        LEFT JOIN Person AS EventExecPerson ON EventExecPerson.id = Event.execPerson_id
        LEFT JOIN rbSpeciality AS EventExecPersonSpeciality ON EventExecPersonSpeciality.id = EventExecPerson.speciality_id
        LEFT JOIN Person AS EventSetPerson ON EventSetPerson.id = Event.setPerson_id
        LEFT JOIN Person AS EventAssistantPerson ON EventAssistantPerson.id = Event.assistant_id
        LEFT JOIN Person as ModifyPerson ON ModifyPerson.id = Event.modifyPerson_id
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
        LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.deleted = 0
        LEFT JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id AND ActionPropertyType.actionType_id = ActionType.id
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
        %(dateCond)s
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
                                'dateCond': dateCond,
                         'limit': limitStr}

    query = db.query(stmt)
    return query

class CMessageDataStreamWriter(QXmlStreamWriter):
    # persZglvFields = {'VERSION': True, 'DATA': True, 'FILENAME' : True, 'FILENAME1' : True}
    # persFields = {'ID_PAC': True, 'FAM': True, 'IM': True, 'OT': True, 'W': True, 'DR': True, 'FAM_P': False, 'IM_P': False,
    #                     'OT_P': False, 'W_P': False, 'DR_P': False, 'MR': False, 'DOCTYPE': False, 'DOCSER': False, 'DOCNUM': False, 'SNILS': False,
    #                     'OKATOG': False, 'OKATOP': False, 'COMENTP': False, 'COMENTZ': False}
    # groupMap = {'ZGLV': persZglvFields, 'PERS': persFields}

    def __init__(self, parent = None, timestamp = QDateTime.currentDateTime()):
        # timestamp - время создания записи. используется для генерации уникальных идентификаторов.
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._clientsSet = None
        self.xmlErrorsList = []
        self.clientStr = u''
        self.processedDiags = set()
        self.processedVisits = set()
        self.processedActions = set()
        self.prevClientId = None
        self.prevEventId = None
        self.prevDiagId = None
        self.prevActionId = None
        self.prevVisitId = None
        self.visits = {}
        self.diags = {}
        self.actions = {}
        self.actionProperties = {}
        self.processedProperties = []
        self.timestamp = timestamp

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)


    def writeTextElementOld(self, element,  value, writeEmtpyTag = False):
        if self.groupMap.has_key(self.curGroupName):
            gr = self.groupMap[self.curGroupName]
            if gr.has_key(element):
                if gr[element] and (not value or value == ''):
                    self.xmlErrorsList.append(u'обязательное поле %s в группе %s не заполнено. Ид пациента: %s, пациент: %s' % (element, self.curGroupName, forceString(self.clientId), self.clientStr))
                    return
                elif (not value or value == ''):
                    return
            else:
                self.xmlErrorsList.append(u'неизвестное поле %s = %s в группе %s. Ид пациента: %s' % (element, value, self.curGroupName, forceString(self.clientId)))

        if not writeEmtpyTag and (not value or value == ''):
            return

        QXmlStreamWriter.writeTextElement(self, element, value)

    def writeEventData(self):

        if self.diags:
            for diag in self.diags.values():
                self.writeEmptyElement('Diagnosis')
                for key, value in diag.items():
                    if value:
                        self.writeAttribute(key, value)
        if self.visits:
            for visit in self.visits.values():
                self.writeEmptyElement('Visit')
                for key, value in visit.items():
                    if value:
                        self.writeAttribute(key, value)
        if self.actions:
            for actionId, action in self.actions.items():
                self.writeStartElement('Action')
                for key, value in action.items():
                    if value:
                        self.writeAttribute(key, value)
                if actionId in self.actionProperties:
                    for ap in self.actionProperties[actionId]:
                        self.writeEmptyElement('ActionProperty')
                        self.writeAttribute('actionPropertyType', ap[0])
                        self.writeAttribute('actionPropertyValue', ap[1])
                self.writeEndElement()

    def writeRecord(self, record):
        clientId = forceRef(record.value('client_id'))
        eventId = forceRef(record.value('eventId'))
        diagId = forceRef(record.value('diagnosticId'))
        visitId = forceRef(record.value('visitId'))
        actionId = forceRef(record.value('actionId'))
        actionPropertyId = forceRef(record.value('actionPropertyId'))
        orgId = forceString(record.value('orgFederalCode'))
        orgName = forceString(record.value('orgName'))
        #orgName = u'ОГАУЗ "СОМИАЦ"'
        orgName = RCDP_NAME
        orgId = RCDP_ID
        documentId = 'Document' + forceString(eventId)
        #personFederalCode = forceString(record.value('eventExecPersonFederalCode'))
        #if not personFederalCode:
        #    personFederalCode = 12312312311      # FIXME: stub
        personFederalCode = forceString(record.value('eventExecPersonSnils'))
        personLastName = forceString(record.value('eventExecPersonLastName'))
        personFirstName = forceString(record.value('eventExecPersonFirstName'))
        personPatrName = forceString(record.value('eventExecPersonPatrName'))

        # if not self.prevClientId is None and self.prevClientId != clientId:
        #     if not self.prevEventId is None:
        #         self.writeEventData()
        #         self.writeEndElement()
        #         self.visits = {}
        #         self.actions = {}
        #         self.diags = {}
        #         self.actionProperties = {}
        #         self.processedProperties = []
        #     self.writeEndElement()
        #     self.prevActionId = None
        #     self.prevVisitId = None
        #     self.prevDiagId = None
        #     self.prevEventId = None
        # if self.prevClientId is None or self.prevClientId != clientId:
        #     self.prevClientId = clientId
        #     self.writeStartElement('Client')
        #     self.writeAttribute('id', forceString(record.value('client_id')))
        #     self.writeAttribute('modifyDatetime', forceDateTime(record.value('clientModifyDatetime')).toString(Qt.ISODate))
        #     self.writeAttribute('lastName', forceString(record.value('clientLastName')))
        #     self.writeAttribute('firstName', forceString(record.value('clientFirstName')))
        #     self.writeAttribute('patrName', forceString(record.value('clientPatrName')))
        #     self.writeAttribute('sex', forceString(record.value('clientSex')))
        #     self.writeAttribute('birthDate', forceDate(record.value('clientBirthDate')).toString(Qt.ISODate))
        #     self.writeAttribute('birthPlace', forceString(record.value('birthPlace')))
        #     self.writeAttribute('SNILS', forceString(record.value('SNILS')))
        #
        #     self.writeEmptyElement('Document')
        #     documentTypeId = forceRef(record.value('documentTypeId'))
        #     if documentTypeId:
        #         self.writeAttribute('documentTypeCode', self.cache.documentType[documentTypeId]['code'])
        #     self.writeAttribute('serial', forceString(record.value('documentSerial')))
        #     self.writeAttribute('number', forceString(record.value('documentNumber')))
        #     self.writeAttribute('date', forceDate(record.value('documentDate')).toString(Qt.ISODate))
        #     self.writeAttribute('origin', forceString(record.value('origin')))
        #
        #     self.writeEmptyElement('Policy')
        #     policyTypeId = forceRef(record.value('policyType_id'))
        #     if policyTypeId:
        #         self.writeAttribute('policyTypeCode', self.cache.policyType[policyTypeId]['code'])
        #     policyKindId = forceRef(record.value('policyKind_id'))
        #     if policyKindId:
        #         self.writeAttribute('policyKindCode', self.cache.policyKind[policyKindId]['code'])
        #     self.writeAttribute('serial', forceString(record.value('policySerial')))
        #     self.writeAttribute('number', forceString(record.value('policyNumber')))
        #     self.writeAttribute('begDate', forceDate(record.value('policyBegDate')).toString(Qt.ISODate))
        #     self.writeAttribute('endDate', forceDate(record.value('policyEndDate')).toString(Qt.ISODate))
        #     self.writeAttribute('name', forceDate(record.value('policyName')).toString(Qt.ISODate))
        #     self.writeAttribute('insurerCode', forceString(record.value('insurerCode')))
        #
        #     self.writeTextElement('RegAddress', forceString(record.value('regAddress')))
        #     self.writeTextElement('LocAddress', forceString(record.value('locAddress')))

        # if not self.prevEventId is None and self.prevEventId != eventId:
        #     self.writeEventData()
        #     self.writeEndElement()
        #     self.visits = {}
        #     self.actions = {}
        #     self.diags = {}
        #     self.actionProperties = {}
        #     self.processedProperties = []

        if eventId:
            if self.prevEventId != eventId or self.prevEventId is None:
                self.writeStartElement('ProvideAndRegisterDocumentSetRequest')
                self.writeAttribute('xsi:schemaLocation', 'urn:ihe:iti:xds-b:2007 ../../schema/IHE/XDS.b_DocumentRepository.xsd')
                self.writeAttribute('xmlns', 'urn:ihe:iti:xds-b:2007')
                self.writeAttribute('xmlns:lcm', 'urn:oasis:names:tc:ebxml-regrep:xsd:lcm:3.0')
                self.writeAttribute('xmlns:rim', 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0')
                self.writeAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
                self.writeStartElement('lcm:SubmitObjectsRequest')
                self.writeStartElement('rim:RegistryObjectList')
                    #<!--
                    #         STABLE ("urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1"),
                    #         ON_DEMAND ("urn:uuid:34268e47-fdf5-41a6-ba33-82133c465248");
                    # -->
                self.writeStartElement('rim:ExtrinsicObject')
                self.writeAttribute('id', documentId)
                self.writeAttribute('mimeType', 'text/xml')
                self.writeAttribute('objectType', 'urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1')

                # Дата создания документа
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'creationTime')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', QDateTime.currentDateTime().toString('yyyyMMddHHmmss'))
                self.writeEndElement()
                self.writeEndElement()

                # Код языка документа
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'languageCode')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', 'RU')
                self.writeEndElement()
                self.writeEndElement()

                # Дата начала оказания услуги
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'serviceStartTime')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', forceDateTime(record.value('eventSetDate')).toString('yyyyMMddHHmm'))
                self.writeEndElement()
                self.writeEndElement()

                # Дата окончания оказания услуги
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'serviceStopTime')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', forceDateTime(record.value('eventExecDate')).toString('yyyyMMddHHmm'))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # Субъект исследования документа
                #9950710 - идентификатор пациента в МО;
                # 1.2.643.5.1.13.3.25.77.761 - OID МО.        -->
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'sourcePatientId')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', u'%s^^^&%s&ISO' % (clientId, RCDP_ID))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # Информация  по лицу, подписавшему документ
                #    Тип данных XCN.
                #    Обязательно наличие XCN.1 - идентификатор лица в МО
                #    и XCN.2 (3, 4) -  ФИО
                #<rim:Slot name="legalAuthenticator">
                #    <rim:ValueList>
                #        	<rim:Value>12345^Кривонос^Владимир^Владимирович</rim:Value>
                #    </rim:ValueList>
                #</rim:Slot>

                # Информация по пациенту. Используется для протоколирования
                # и регистрации пациента в случае, если пациент в ИЭМК еще не зарегистрирован.
                #     PID-3 - Список идентификаторов пациента, в формате CX (без ограничений). Нужно передавать как список
                #     PID-5 - Имя пациента в формате XPN
                #     PID-7 -  Дата рождения                -->

# <!--                <rim:Slot name="sourcePatientInfo">-->
# <!--                    <rim:ValueList>-->
#                     <!-- СНИЛС-->
# <!--                        <rim:Value>PID-3|66666666666^^^^1.2.643.100.3</rim:Value>   -->
# <!--                        <rim:Value>PID-5|ТестоваяФамилияПациента^ТестовоеИмяПациента^ТестовоеОтчествоПациента^^</rim:Value>-->
# <!--                        <rim:Value>PID-7|19560527</rim:Value>-->
# <!--                        <rim:Value>PID-8|M</rim:Value>-->
# <!--                    </rim:ValueList>-->
# <!--                </rim:Slot>-->

                # Номер медицинской карты пациента
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'medicalRecordNumber')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', 'Document' + forceString(eventId))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                #<!--        Основной диагноз пациента     -->
# <!--                <rim:Slot name="primaryDiagnosis">-->
# <!--                    <rim:ValueList>-->
# <!--                        <rim:Value>M17.1</rim:Value>-->
# <!--                    </rim:ValueList>-->
# <!--                </rim:Slot>-->

                # Заголовок документа
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', u'Эпикриз стационара №50')
                self.writeEndElement()      # rim:Name

                # Комментарий к документу
                self.writeStartElement('rim:Description')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', u'Комментарий к документу')
                self.writeEndElement()      # rim:Description

                # Секция описания автора документа, определяется классификатором urn:uuid:93606bcf-9494-43ec-9b4e-a7748d1a838d
                self.writeStartElement('rim:Classification')
                self.writeAttribute('id', 'cl01')
                self.writeAttribute('classificationScheme', 'urn:uuid:93606bcf-9494-43ec-9b4e-a7748d1a838d')
                self.writeAttribute('classifiedObject', documentId)
                self.writeAttribute('nodeRepresentation', '')

                # XCN тип. ФИО
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'authorPerson')
                self.writeStartElement('rim:ValueList')

                self.writeTextElement('rim:Value', u'%s^%s^%s^%s' % (personFederalCode, personLastName, personFirstName, personPatrName))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # Код медицинской организации. XON тип
                #         Имя в 1-м элементе
                #          6 - OID классификатора организации, назначившей код
                #         10 - OID медицинского учреждения

                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'authorInstitution')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', u'%s^^^^^&1.2.643.5.1.13.3.25.77.761&ISO^^^^%s' % (orgName, orgId))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # Должность специалиста
                # self.writeStartElement('rim:Slot')
                # self.writeAttribute('name', 'authorRole')
                # self.writeStartElement('rim:ValueList')
                # self.writeTextElement('rim:Value', forceString(record.value('personPostName')))
                # self.writeEndElement()      # rim:ValueList
                # self.writeEndElement()      # rim:Slot

                # Профиль специалиста, автора документа
                # self.writeStartElement('rim:Slot')
                # self.writeAttribute('name', 'authorSpecialty')
                # self.writeStartElement('rim:ValueList')
                # self.writeTextElement('rim:Value', forceString(record.value('personSpecialityName')))
                # self.writeEndElement()      # rim:ValueList
                # self.writeEndElement()      # rim:Slot

                self.writeEndElement()      # rim:Classification

                # Секция описания типа СЭМД (classCode), определяется значением urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a
                self.writeStartElement('rim:Classification')
                self.writeAttribute('id', 'cl02')
                self.writeAttribute('classificationScheme', 'urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a')
                self.writeAttribute('classifiedObject', documentId)
                self.writeAttribute('nodeRepresentation', '1')

                # Схема кодирования классификаторов типов СЭМД
                #      Должен быть 1.2.643.5.1.13.2.7.5.1
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'codingScheme')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', '1.2.643.5.1.13.2.1.1.646')
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # Отображаемое значеие типа СЭМД ко классификатору 1.2.643.5.1.13.2.7.5.1
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', u'Эпикриз стационара')
                self.writeEndElement()      # rim:Name

                self.writeEndElement()      # rim:Classification

                # Уровень конфиденциальности документа, определяется значением urn:uuid:f4f85eac-e6cb-4883-b524-f2705394840f
                self.writeStartElement('rim:Classification')
                self.writeAttribute('id', 'cl03')
                self.writeAttribute('classificationScheme', 'urn:uuid:f4f85eac-e6cb-4883-b524-f2705394840f')
                self.writeAttribute('classifiedObject', documentId)
                self.writeAttribute('nodeRepresentation', 'N')

                # Схема кодирования уровня документа врача   -->
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'codingScheme')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', '1.2.643.5.1.13.2.7.1.10')
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # DisplayName уровня конфиденциальности
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', u'Открыто')
                self.writeEndElement()      # rim:Name

                self.writeEndElement()      # rim:Classification

                self.writeStartElement('rim:Classification')
                self.writeAttribute('id', 'cl03')
                self.writeAttribute('classificationScheme', 'urn:uuid:f4f85eac-e6cb-4883-b524-f2705394840f')
                self.writeAttribute('classifiedObject', documentId)
                self.writeAttribute('nodeRepresentation', 'V')

                # Схема кодирования уровня документа для пациента
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'codingScheme')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', '2.16.840.1.113883.5.25')
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # DisplayName уровня конфиденциальности
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', u'Закрыто')
                self.writeEndElement()      # rim:Name

                self.writeEndElement()      # rim:Classification

                # Секция кода формата документа
                self.writeStartElement('rim:Classification')
                self.writeAttribute('id', 'cl04')
                self.writeAttribute('classificationScheme', 'urn:uuid:a09d5840-386c-46f2-b5ad-9c3699a4309d')
                self.writeAttribute('classifiedObject', documentId)
                self.writeAttribute('nodeRepresentation', 'application/hl7-cda-level-one+xml')

                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'codingScheme')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', '1.2.643.5.1.13.2.7.1.40')
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', 'application/hl7-cda-level-one+xml')
                self.writeEndElement()      # rim:Name

                self.writeEndElement()      # rim:Classification

                # Вид медицинской организации. Опционально
                #<rim:Classification id="cl05" classificationScheme="urn:uuid:f33fb8ac-18af-42cc-ae0e-ed0b0bdb91e1" classifiedObject="Document01" nodeRepresentation="111052">
                #    <rim:Slot name="codingScheme">
                #        <rim:ValueList>
                #            <rim:Value>1.2.643.5.1.13.2.1.1.77</rim:Value>
                #        </rim:ValueList>
                #    </rim:Slot>
                #    <rim:Name>
                #        <rim:LocalizedString value="Центральная районная больница"/>
                #    </rim:Name>
                #</rim:Classification>


                # Наименование отделения в МО. Опционально.
                #    practiceSettingCode

                # <rim:Classification id="cl06" classificationScheme="urn:uuid:cccf5598-8b07-4b77-a05e-ae952c785ead" classifiedObject="Document01" nodeRepresentation="27">
                #     <rim:Slot name="codingScheme">
                #         <rim:ValueList>
                #             <rim:Value>1.2.643.5.1.13.2.7.1.25</rim:Value>
                #         </rim:ValueList>
                #     </rim:Slot>
                #     <rim:Name>
                #         <rim:LocalizedString value="Травматологическое отделение"/>
                #     </rim:Name>
                # </rim:Classification>

                # Тип медицинского документа.

                self.writeStartElement('rim:Classification')
                self.writeAttribute('id', 'cl07')
                self.writeAttribute('classificationScheme', 'urn:uuid:f0306f51-975f-434e-a61c-c59651d33983')
                self.writeAttribute('classifiedObject', documentId)
                self.writeAttribute('nodeRepresentation', 'POCD_MT000040_RU01')

                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'codingScheme')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', '2.16.840.1.113883.1.3')
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', 'CDA R2')
                self.writeEndElement()      # rim:Name

                self.writeEndElement()      # rim:Classification

                # ID пациента в МО.
                #        9950710 - идентификатор пациента в МО;
                #       1.2.643.5.1.13.3.25.77.761 - OID МО
                self.writeStartElement('rim:ExternalIdentifier')
                self.writeAttribute('id', 'ei01')
                self.writeAttribute('registryObject', documentId)
                self.writeAttribute('identificationScheme', 'urn:uuid:58a6f841-87b3-4a3e-92fd-a8ffeff98427')
                self.writeAttribute('value', u'%s^^^&%s&ISO' % (clientId, RCDP_ID))
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', 'XDSDocumentEntry.patientId')
                self.writeEndElement()      # rim:Name
                self.writeEndElement()      # rim:ExternalIdentifier

                # Уникальный идентификатор документа в МИС
                self.writeStartElement('rim:ExternalIdentifier')
                self.writeAttribute('id', 'ei02')
                self.writeAttribute('registryObject', documentId)
                self.writeAttribute('identificationScheme', 'urn:uuid:2e82c1f6-a085-4c72-9da3-8640a32e42ab')
                self.writeAttribute('value', 'Document' + forceString(eventId))
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', 'XDSDocumentEntry.uniqueId')
                self.writeEndElement()      # rim:Name
                self.writeEndElement()      # rim:ExternalIdentifier

                self.writeEndElement()      # rim:ExtrinsicObject

                # Секция описания набора документов
                self.writeStartElement('rim:RegistryPackage')
                self.writeAttribute('id', 'SubmissionSet011231231')
                # Дата создания и отправки на регистрацию набора документов
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'submissionTime')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', QDateTime.currentDateTime().toString('yyyyMMddHHmm'))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # Наименовение набора документов
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', u'Эпикриз стационара')
                self.writeEndElement()      # rim:Name

                # Комментарий к набору документов
                self.writeStartElement('rim:Description')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', u'Эпикриз стационара комментарий')
                self.writeEndElement()      # rim:Description

                # Автор набора документов
                # Может быть другое лицо, отличное от авторов самих документов, входящих в набор..
                # Описание секции аналогично секции автора в документе выше.
                self.writeStartElement('rim:Classification')
                self.writeAttribute('id', 'cl08')
                self.writeAttribute('classificationScheme', 'urn:uuid:a7058bb9-b4e4-4307-ba5b-e3f0ab85e12d')
                self.writeAttribute('classifiedObject', 'SubmissionSet011231231')
                self.writeAttribute('nodeRepresentation', '')
                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'authorPerson')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', u'%s^%s^%s^%s' % (personFederalCode, personLastName, personFirstName, personPatrName))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                 # Код МО по справочнику в реестре НСИ МЗ РФ: MDR308.
                 #                OID справочника: 1.2.643.5.1.13.2.1.1.178.
                 #                OID МО 1.2.643.5.1.13.3.25.77.761

                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'authorInstitution')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', u'%s^^^^^&1.2.643.5.1.13.2.1.1.178&ISO^^^^%s' % (orgName, orgId))
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                # self.writeStartElement('rim:Slot')
                # self.writeAttribute('name', 'authorRole')
                # self.writeStartElement('rim:ValueList')
                # self.writeTextElement('rim:Value', forceString(record.value('personPostName')))
                # self.writeEndElement()      # rim:ValueList
                # self.writeEndElement()      # rim:Slot
                #
                # self.writeStartElement('rim:Slot')
                # self.writeAttribute('name', 'authorSpecialty')
                # self.writeStartElement('rim:ValueList')
                # self.writeTextElement('rim:Value', forceString(record.value('personSpecialityName')))
                # self.writeEndElement()      # rim:ValueList
                # self.writeEndElement()      # rim:Slot

                self.writeEndElement()      # rim:Classification

                # Идентификатор документа в МИС
                self.writeStartElement('rim:ExternalIdentifier')
                self.writeAttribute('id', 'ei03')
                self.writeAttribute('registryObject', 'SubmissionSet011231231')
                self.writeAttribute('identificationScheme', 'urn:uuid:96fdda7c-d067-4183-912e-bf5ee74998a8')
                self.writeAttribute('value', 'SS%s' % self.timestamp.toString('yyMMddTHHmmss.zzz'))
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', 'XDSSubmissionSet.uniqueId')
                self.writeEndElement()      # rim:Name
                self.writeEndElement()      # rim:ExternalIdentifier

                # <!-- Идентификатор системы-источника документов (в МИС) -->
                # <rim:ExternalIdentifier id="ei04" registryObject="SubmissionSet01" identificationScheme="urn:uuid:554ac39e-e3fe-47fe-b233-965d2a147832" value="1.3.6.1.4.1.21367.2005.3.7">
                #     <rim:Name>
                #         <rim:LocalizedString value="XDSSubmissionSet.sourceId"/>
                #     </rim:Name>
                # </rim:ExternalIdentifier>

                # ID пациента в МО
                #        9950710 - идентификатор пациента в МО;
                #        1.2.643.5.1.13.3.25.77.761 - OID МО.      -->
                self.writeStartElement('rim:ExternalIdentifier')
                self.writeAttribute('id', 'ei05')
                self.writeAttribute('registryObject', 'SubmissionSet011231231')
                self.writeAttribute('identificationScheme', 'urn:uuid:6b5aea1a-874d-4603-a4bc-96a0a7b38446')
                self.writeAttribute('value', u'%s^^^&%s&ISO' % (clientId, RCDP_ID))
                self.writeStartElement('rim:Name')
                self.writeEmptyElement('rim:LocalizedString')
                self.writeAttribute('value', 'XDSSubmissionSet.patientId')
                self.writeEndElement()      # rim:Name
                self.writeEndElement()      # rim:ExternalIdentifier>
                self.writeEndElement()      # rim:RegistryPackage





                # Идентификатор urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd опеределяет что classifiedObject указанный тут относится к типу SubmitionSet
                self.writeEmptyElement('rim:Classification')
                self.writeAttribute('id', 'cl10')
                self.writeAttribute('classifiedObject', 'SubmissionSet011231231')
                self.writeAttribute('classificationNode', 'urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd')

                # Описывает тип связи между набором документов и документом, в данном примере HasMember - документ Document01 входит в состав набора документов SubmissionSet01
                self.writeStartElement('rim:Association')
                self.writeAttribute('id', 'as01')
                self.writeAttribute('associationType', 'urn:oasis:names:tc:ebxml-regrep:AssociationType:HasMember')
                self.writeAttribute('sourceObject', 'SubmissionSet011231231')
                self.writeAttribute('targetObject', documentId)

                self.writeStartElement('rim:Slot')
                self.writeAttribute('name', 'SubmissionSetStatus')
                self.writeStartElement('rim:ValueList')
                self.writeTextElement('rim:Value', 'Original')
                self.writeEndElement()      # rim:ValueList
                self.writeEndElement()      # rim:Slot

                self.writeEndElement()      # rim:Association

                self.writeEndElement()      # rim:RegistryObjectList
                self.writeEndElement()      # lcm:SubmitObjectsRequest

                # Сам СЭМД в формате base64binary
                self.writeStartElement('Document')
                self.writeAttribute('id', documentId)
                semdBuffer = QBuffer()
                semdBuffer.open(QIODevice.WriteOnly)
                semdWriter = CSEMDDataStreamWriter(self)
                semdWriter.writeFileHeader(semdBuffer, eventId)
                semdWriter.writeRecord(record)
                semdWriter.writeFileFooter()
                print semdBuffer.buffer()
                self.writeCharacters(QString(semdBuffer.data().toBase64()))
                #self.writeCharacters('asdasda')
                ####PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiP…
                self.writeEndElement()      # Document
                self.writeEndElement()      # ProvideAndRegisterDocumentSetRequest
                self.writeEndElement()

        #         self.prevEventId = eventId
        #         self.writeStartElement('Event')
        #         self.writeAttribute('modifyDatetime', forceDateTime(record.value('eventModifyDatetime')).toString(Qt.ISODate))
        #         self.writeAttribute('setDate', forceDate(record.value('eventSetDate')).toString(Qt.ISODate))
        #         self.writeAttribute('execDate', forceDate(record.value('eventExecDate')).toString(Qt.ISODate))
        #         self.writeAttribute('eventTypeCode', forceString(record.value('eventTypeCode')))
        #         self.writeAttribute('execPersonCode', forceString(record.value('eventExecPersonCode')))
        #         self.writeAttribute('externalId', forceString(eventId))
        #         self.writeAttribute('isPrimary', forceString(record.value('eventIsPrimary')))
        #         self.writeAttribute('order', forceString(record.value('eventOrder')))
        #         self.writeAttribute('orgCode', forceString(record.value('eventOrgCode')))
        #         resultId = forceRef(record.value('eventResultId'))
        #         if resultId:
        #             self.writeAttribute('resultCode', self.cache.result[resultId]['code'])
        #         self.writeAttribute('MESCode', forceString(record.value('MEScode')))
        #         #self.writeAttribute('')
        #
        #     if diagId and  not diagId in self.diags:
        #         tempDiag = {}
        #         tempDiag['diagnosticTypeCode'] = self.cache.diagnosisType[forceRef(record.value('diagnosticTypeId'))]['code']
        #         diagnosticCharacterId = forceRef(record.value('diagnosticCharacterId'))
        #         if diagnosticCharacterId:
        #             tempDiag['diagnosticCharacterCode'] = self.cache.diseaseCharacter[diagnosticCharacterId]['code']
        #         diagnosticStageId = forceRef(record.value('diagnosticStageId'))
        #         if diagnosticStageId:
        #             tempDiag['diagnosticStageCode'] = self.cache.diseaseStage[diagnosticStageId]['code']
        #         diagnosticPhaseId = forceRef(record.value('diagnosticPhaseId'))
        #         if diagnosticPhaseId:
        #             tempDiag['diagnosticPhaseCode'] = self.cache.diseasePhases[diagnosticPhaseId]['code']
        #         tempDiag['diagnosticSetDate'] = forceDate(record.value('diagnosticSetDate')).toString(Qt.ISODate)
        #         tempDiag['diagnosticEndDate'] = forceDate(record.value('diagnosticEndDate')).toString(Qt.ISODate)
        #         tempDiag['diagnosticPersonCode'] = forceString(record.value('diagnosticPersonCode'))
        #         diagnosticResultId = forceRef(record.value('diagnosticResultId'))
        #         if diagnosticResultId:
        #             tempDiag['diagnosticResultCode'] = self.cache.diagnosticResult[diagnosticResultId]['code']
        #         tempDiag['MKB'] = forceString(record.value('diagnosisMKB'))
        #         self.diags[diagId] = tempDiag
        #
        #     if visitId and not visitId in self.visits:
        #         tempVisit = {}
        #         sceneId = forceRef(record.value('visitSceneId'))
        #         if sceneId:
        #             tempVisit['sceneCode'] =  self.cache.scene[sceneId]['code']
        #         tempVisit['visitTypeCode'] = self.cache.visitType[forceRef(record.value('visitType_id'))]['code']
        #         tempVisit['personCode'] = forceString(record.value('visitPersonCode'))
        #         tempVisit['isPrimary'] = forceString(record.value('visitIsPrimary'))
        #         tempVisit['date'] = forceDate(record.value('visitDate')).toString(Qt.ISODate)
        #         tempVisit['serviceCode'] = forceString(record.value('visitServiceCode'))
        #         financeId = forceRef(record.value('visitFinanceId'))
        #         if financeId:
        #             tempVisit['financeCode'] = self.cache.finance[financeId]['code']
        #         self.visits[visitId] = tempVisit
        #
        #     if actionId and not actionId in self.actions:
        #         tempAction = {}
        #         tempAction['actionTypeCode'] = forceString(record.value('actionTypeCode'))
        #         tempAction['status'] = forceString(record.value('actionStatus'))
        #         tempAction['begDate'] = forceDate(record.value('actionBegDate')).toString(Qt.ISODate)
        #         tempAction['endDate'] = forceDate(record.value('actionEndDate')).toString(Qt.ISODate)
        #         tempAction['personCode'] = forceString(record.value('actionPersonCode'))
        #         tempAction['amount'] = forceString(record.value('actionAmount'))
        #         tempAction['uet'] = forceString(record.value('actionUet'))
        #         tempAction['MKB'] = forceString(record.value('actionMKB'))
        #         tempAction['orgCode'] = forceString(record.value('actionOrgCode'))
        #         tempAction['duration'] = forceString(record.value('actionDuration'))
        #         self.actions[actionId] = tempAction
        #
        #     if actionId and actionPropertyId and not actionPropertyId in self.processedProperties:
        #         if not actionId in self.actionProperties:
        #             self.actionProperties[actionId] = []
        #         self.actionProperties[actionId].append(
        #             (forceString(record.value('actionPropertyTypeName')),
        #              forceString(record.value('actionPropertyValue')))
        #         )
        #         self.processedProperties.append(forceRef(actionPropertyId))
        # self._clientsSet.add(clientId)

    def closeEverything(self):
        """
        Выполняется после обработки всех данных - запись данных по последнему обработанному обращению, если они есть.
        """
        if not self.prevEventId is None:
            # Есть незакрытый тег <Event>
            self.writeEventData()
            self.writeEndElement()
            self.visits = {}
            self.actions = {}
            self.diags = {}
            self.actionProperties = {}
            self.processedProperties = []
        # К окончанию экспорта остается незакрытый тег <Client>
        self.writeEndElement()

    def writeFileHeader(self,  device, fileName, accDate, webService):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('soap:Envelope')
        self.writeAttribute('xmlns:a', 'http://www.w3.org/2005/08/addressing')
        self.writeAttribute('xmlns:egis', 'http://egisz.rosminzdrav.ru')
        self.writeAttribute('xmlns:oas', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')
        self.writeAttribute('xmlns:soap', 'http://www.w3.org/2003/05/soap-envelope')
        self.writeAttribute('xmlns:urn', 'urn:ihe:iti:xds-b:2007')
        self.writeAttribute('xmlns:urn1', 'urn:oasis:names:tc:ebxml-regrep:xsd:lcm:3.0')
        self.writeAttribute('xmlns:urn2', 'urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0')
        self.writeAttribute('xmlns:urn3', 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0')

        self.writeStartElement('soap:Header')
        self.writeStartElement('egis:transportHeader')
        self.writeAttribute('oas:Id', '23423')
        self.writeStartElement('egis:authInfo')
        self.writeTextElement('egis:userSession', '123123')
        self.writeTextElement('clientEntityId', RCDP_UUID)
        self.writeEndElement()      # egis:authInfo
        self.writeEndElement()      # egis:transportHeader
        self.writeTextElement('a:Action', 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b')
        # ID сообщения, должно быть указано в ответе на запрос
        self.writeTextElement('a:MessageID', 'SEMD%s' % self.timestamp.toString('yyMMddTHHmmss.zzz'))
        # Адрес источника запроса (МИС), куда нужно будет отправить асинхронный ответ
        self.writeStartElement('a:ReplyTo')
        self.writeTextElement('a:Address', webService)
        self.writeEndElement()      # a:ReplyTo
        # Адрес ИШ ИЭМК, куда отправляется этот запрос
        self.writeTextElement('a:To', 'https://api-iemc-test.rosminzdrav.ru/xds/xdsClientRep?wsdl')
        self.writeEndElement()      # soap:Header
        self.writeStartElement('soap:Body')

        #self.writeStartElement('IEMC')
        #self.writeEmptyElement('ORG')
        #self.writeAttribute('code', forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode')) if not self.miacCode else self.miacCode)
        #self.writeStartElement('PERS_LIST')
        #self.writeHeader(fileName, accDate)

    def writeHeader(self, fileName, accDate):
        self.writeStartElement('ZGLV')
        self.writeTextElement('VERSION', '1.0')
        #self.writeTextElement('DATA', accDate.toString(Qt.ISODate))
        (fname,  ext) = os.path.splitext(os.path.basename(fileName))
        #elf.writeTextElement('FILENAME', 'L%s' % fname[1:26])
        #self.writeTextElement('FILENAME1', fname[:26])
        self.writeEndElement()

    def writeFileFooter(self):
        self.writeEndElement() # s:Body
        self.writeEndElement() # s:Envelope
        self.writeEndDocument()

class CSEMDDataStreamWriter(QXmlStreamWriter):
    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeFileHeader(self,  device, eventId):
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('ClinicalDocument')
        self.writeAttribute('xmlns', 'urn:hl7-org:v3')
        self.writeAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        self.writeAttribute('xmlns:ext', 'urn:hl7-RU-EHR:v1')
        self.writeAttribute('xsi:schemaLocation', 'urn:hl7-org:v3 ../infrastructure/cda/CDA_RU01.xsd urn:hl7-RU-EHR:v1 ../infrastructure/cda/POCD_MT000040_RU01_Extension.xsd')

        # Выписной эпикриз оформляется строго определенным образом. Так, он в обязательном порядке включает следующие составные части:
        # данные о личности пациента, жалобы, анамнез, диагноз, результаты обследований, анализов, осмотров и т.д.;
        # мнения разных специалистов, данные о ходе и итогах лечения, прогноз и рекомендации по продолжению лечения, реабилитации и т.д. -->
        # ЗАГОЛОВОК ДОКУМЕНТА
        self.writeEmptyElement('realmCode')
        self.writeAttribute('code', 'RU')
        # Шаблон: Тип документа CDA [1]
        self.writeEmptyElement('typeId')
        self.writeAttribute('root', '2.16.840.1.113883.1.3')
        self.writeAttribute('extension', 'POCD_MT000040_RU01')
        # Шаблон: Версия шаблона стандарта: Эпикриз стационара, версия № 1
        self.writeEmptyElement('templateId')
        self.writeAttribute('root', '1.2.643.5.1.13.2.7.5.1')
        self.writeEmptyElement('templateId')
        self.writeAttribute('root', '1.2.643.5.1.13.2.7.5.1.1')
        # Шаблон: Уникальный номер экземпляра документа. OID root и extention должны образовать уникальную комбинацию. Extention может задаваться в виде UUID
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        self.writeAttribute('extension', 'Document' + forceString(eventId))
        # Шаблон: Тип медицинского документа [1]
        self.writeEmptyElement('code')
        self.writeAttribute('code', '1_1')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.1')
        self.writeAttribute('codeSystemName', u'Система электронных медицинских документов')
        self.writeAttribute('displayName', u'Эпикриз стационара')
        # Шаблон: Название [1]
        self.writeTextElement('title', u'Эпикриз стационара №50')
        # Шаблон: Дата создания документа [1]
        self.writeEmptyElement('effectiveTime')
        self.writeAttribute('value', QDateTime.currentDateTime().toString('yyyyMMddHHmmss'))
        # Шаблон: Уровень конфиденциальности документа [1]
        self.writeStartElement('confidentialityCode')
        self.writeAttribute('code', 'V')
        self.writeAttribute('codeSystem', '2.16.840.1.113883.5.25')
        self.writeAttribute('codeSystemName', u'Уровень конфиденциальности документа')
        self.writeAttribute('displayName', u'Закрыто')

        # Уровень доступа опекуна/попечителя
        self.writeEmptyElement('translation')
        self.writeAttribute('code', 'R')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.9')
        self.writeAttribute('codeSystemName', u'Уровень конфиденциальности опекуна')
        self.writeAttribute('displayName', u'Ограниченно')

        # Уровень доступа врача
        self.writeEmptyElement('translation')
        self.writeAttribute('code', 'N')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.10')
        self.writeAttribute('codeSystemName', u'Уровень конфиденциальности врача')
        self.writeAttribute('displayName', u'Открыто')

        self.writeEndElement()      # confidentialityCode
        # Шаблон: Язык документа [1]
        self.writeEmptyElement('languageCode')
        self.writeAttribute('code', 'RU')

        # Шаблон: Номер истории болезни, к которой относится документ [1]
        self.writeEmptyElement('setId')
        self.writeAttribute('root', RCDP_ID)
        self.writeAttribute('extension', 'Document' + forceString(eventId))

        # Шаблон: Версия данного документа [1]
        self.writeEmptyElement('versionNumber')
        self.writeAttribute('value', '2')

    def writeFileFooter(self):
        self.writeEndElement() # ClinicalDocument
        self.writeEndDocument()

    def writeRecord(self, record):
        eventExecPersonFederalCode = forceString(record.value('eventExecPersonFederalCode'))
        eventExecPersonLastName = forceString(record.value('eventExecPersonLastName'))
        eventExecPersonFirstName = forceString(record.value('eventExecPersonFirstName'))
        eventExecPersonPatrName = forceString(record.value('eventExecPersonPatrName'))
        eventExecPersonSnils = forceString(record.value('eventExecPersonSnils'))
        # НАЧАЛО ДАННЫХ О ПАЦИЕНТЕ
        # Шаблон: Эпикриз_пациент [1]
        self.writeStartElement('recordTarget')
        self.writeAttribute('typeCode', 'RCT')


        # Область описания: "PAT" - пациент
        self.writeEmptyElement('realmCode')
        self.writeAttribute('code', 'PAT')

        self.writeStartElement('patientRole')
        self.writeAttribute('classCode', 'PAT')
        # Код пациента
        # Это автоматически генерируемый МИС id используется для соотнесения детальных данных таких как способ обращения, дата рождения, возраст и т.д. Может быть как UUID, так и код, присвоенный МО, см. тег patient
        # <!-- id root="1.2.643.5.1.13.3.25.77.761" extension="7AA0BAAC-0CD0-11E0-9516-4350DFD72085"/> -->
        # Код физического лица ("48905059995") в организации ("1.2.643.5.1.13.3.25.77.761")
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        self.writeAttribute('extension', forceString(record.value('client_id')))

        # Адрес пациента [0..2] начало блока
        # Адрес фактического места жительства
        self.writeStartElement('addr')
        self.writeAttribute('use', 'H')
        # Страна
        self.writeTextElement('country', u'Российская Федерация')
        # Область/Край
        #self.writeTextElement('county', 'Новосибирская область')
        # Город
        #self.writeTextElement('city', 'Новосибирск')
        # streetAddressLine используется только для неструктурированного указания адреса, например:
        #self.writeTextElement('streetAddressLine', '9, Лескова ул., Новосибирск, Новосибирская область, Российская Федерация, 630008')
        # Улица
        #self.writeTextElement('streetName', 'Лескова ул.')
        # Номер дома
        #self.writeTextElement('houseNumber', '69')
        # Квартира
        #self.writeTextElement('additionalLocator', '9')
        # Почтовый индекс
        #self.writeTextElement('postalCode', '630008')
        # Код КЛАДР населенного пункта
        #self.writeTextElement('unitID', '5400000100000')
        # Геокоординаты объекта
        #self.writeTextElement('direction', '55.022155,82.950660')
        self.writeEndElement()      # addr
        # Адрес постоянной регистрации
        self.writeStartElement('addr')
        self.writeAttribute('use', 'HP')
        # Страна
        self.writeTextElement('country', u'Российская Федерация')
        # Область/Край
        #self.writeTextElement('state', u'Новосибирская область')
        # Район
        #self.writeTextElement('county', u'Калининский район')
        # Город/Населенный пункт
        #self.writeTextElement('city', u'Пашино')
        # streetAddressLine используется только для неструктурированного указания адреса, например:
        #<!--<streetAddressLine>11-25, Новоуральская ул., Пашино, Калининский район, Новосибирская область, Российская Федерация, 630900</streetAddressLine> -->
        # Улица
        #self.writeTextElement('streetName', u'Новоуральская ул.')
        # Номер дома
        #self.writeTextElement('houseNumber', '11')
        # Квартира
        #self.writeTextElement('additionalLocator', '25')
        # Почтовый индекс
        #self.writeTextElement('postalCode', '630900')
        # Код КЛАДР населенного пункта
        #self.writeTextElement('unitID', '5400000100400')
        self.writeEndElement()      # addr
        # Конец блока адреса

        # Телефон пациента 1
        self.writeEmptyElement('telecom')
        self.writeAttribute('value', 'tel:%s' % forceString(record.value('clientPhoneNumber')))
        # Телефон пациента 2
        # self.writeEmptyElement('telecom')
        # self.writeAttribute('use', 'MC')
        # self.writeAttribute('value', 'tel:+79030123456')
        # Адрес электронной почты пациента
        # self.writeEmptyElement('telecom')
        # self.writeAttribute('value', 'mailto:vasya.pupkovich@mail.ru')
        # Факс пациента
        # <telecom value="fax:+78442171300"/>
        # Информация, для идентификации пациента
        self.writeStartElement('patient')
        self.writeAttribute('classCode', 'PSN')
        self.writeAttribute('determinerCode', 'INSTANCE')
        # Идентификатор пациента в МО (МИС)
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        self.writeAttribute('extension', forceString(record.value('client_id')))
        # Фамилия, Имя, Отчество [0..1]
        self.writeStartElement('name')
        # Фамилия
        self.writeTextElement('family', forceString(record.value('clientLastName')))
        # Имя
        self.writeTextElement('given', forceString(record.value('clientFirstName')))
        # Отчество
        self.writeTextElement('given', forceString(record.value('clientPatrName')))
        self.writeEndElement()      # name
        # Пол пациента [1]
        sexCode = forceInt(record.value('clientSex'))
        if sexCode:
            self.writeEmptyElement('administrativeGenderCode')
            self.writeAttribute('code', forceString(sexCode))
            self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.156')
            self.writeAttribute('codeSystemName', u'Классификатор типов пола')
            self.writeAttribute('displayName', u'Мужской' if sexCode == 1 else u'Женский')

        # Дата рождения [0..1]
        self.writeEmptyElement('birthTime')
        self.writeAttribute('value', forceDate(record.value('clientBirthDate')).toString('yyyyMMdd'))

        # <!-- Шаблон: Другие участники [0..*] -->
        # <!-- Другой участник случая 1 (опекун / родитель) -->
        # <guardian classCode="GUARD">
        # <!-- Код другого участника [1] -->
        # <!-- Код физического лица ("36598") в реестре ("1.2.643.5.1.13.3.25.77.761") -->
        # <id root="1.2.643.5.1.13.3.25.77.761" extension="9950711"/>
        # <!-- Отношение к пациенту [1] -->
        # <code code="1" codeSystem="1.2.643.5.1.13.2.7.1.15" codeSystemName="Отношение к пациенту" displayName="Родитель"/>
        # <!-- Фамилия, имя, отчество -->
        # <guardianPerson>
        # <name>
        # <!-- Фамилия -->
        # <family>Незнамов</family>
        # <!-- Имя -->
        # <given>Василий</given>
        # <!-- Отчество -->
        # <given>Трофимович</given>
        # </name>
        # <ext:patient HL7-ClassName="PAT" HL7-Domain="PRPA_RM000000" realmCode="RU">
        # <!--Идентификаторы -->
        # <ext:asOtherIDs classCode="IDENT">
        #         <ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        #         <!-- OID документа-->
        #         <ext:id root="1.2.643.5.1.13.2.7.1.62.3"/>
        #         <!--Тип идентификатора-->
        #         <ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Документ, удостоверяющий личность">
        #         <!--Тип документа, удостоверяющего личность -->
        #         <ext:translation code="14" codeSystem="1.2.643.5.1.13.2.1.1.187" codeSystemName="Классификатор типов документов, удостоверяющих личность" displayName="ПАСПОРТ РОССИИ"/>
        #         </ext:documentType>
        #         <!-- Номер и серия документа-->
        #         <ext:documentNumber series="5501" number="123368"/>
        #         <!-- Дата выдачи документа-->
        #         <ext:effectiveTime value="200206505"/>
        #         <!-- Организация, выдавшая документ-->
        #         <ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        #         <!--Идентификатор организации, выдавшей документ -->
        #         <ext:id nullFlavor="NA"/>
        #         <!--Наименование организации, выдавшей документ-->
        #         <ext:name>ОУФМС России, по Даниловскому району, г Москвы в ЮАО</ext:name>
        #         </ext:scopingOrganization>
        # </ext:asOtherIDs>
        # <!-- Полисы страхования, предъявленные представителем пациента -->
        # <!-- Полис ОМС представителя пациента-->
        # <ext:asOtherIDs classCode="HLD">
        #         <ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        #         <ext:id root="1.2.643.5.1.13.2.7.1.62.1" extension="Полис обязательного медицинского страхования "/>
        #         <ext:documentType code="1" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис обязательного медицинского страхования"/>
        #         <!-- Собственно номер и серия (если есть) и тип полиса -->
        #         <ext:documentNumber series="35" number="3034879659"/>
        #         <!-- Даты выдачи полиса -->
        #         <ext:effectiveTime value="20100214"/>
        #         <!-- Страховая компания, выдавшая полис представителю пациента-->
        #         <ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        #         <!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
        #         <ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
        #         <!-- Название страховой компании -->
        #         <ext:name>ЗАО "МАКС-М"</ext:name>
        #         </ext:scopingOrganization>
        #         <!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
        #         <ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
        # </ext:asOtherIDs>
        # <!-- Полис ДМС представителя пациента -->
        # <ext:asOtherIDs classCode="HLD">
        #         <ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        #         <ext:documentType code="2" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис добровольного медицинского страхования"/>
        #         <!-- Собственно номер и серия (если есть) и тип полиса -->
        #         <ext:documentNumber series="1111" number="0987654321"/>
        #         <!-- Даты начала и окончания действия полиса -->
        #         <ext:effectiveTime>
        #         <ext:low value="20130214"/>
        #         <ext:high value="20130813"/>
        #         </ext:effectiveTime>
        #         <!-- Страховая компания, выдавшая полис -->
        #         <ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        #         <!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
        #         <ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
        #         <!-- Название страховой компании -->
        #         <ext:name>ЗАО "МАКС-М"</ext:name>
        #         </ext:scopingOrganization>
        #         <!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
        #         <ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
        # </ext:asOtherIDs>
        # <!-- Другие идентификаторы представителя пациента -->
        # <!-- СНИЛС представителя пациента -->
        # <ext:asOtherIDs classCode="IDENT">
        #         <ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        #         <ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Страховой номер индивидуального лицевого счёта"/>
        #         <ext:documentNumber number="11223344524"/>
        #         <ext:effectiveTime value="20100214"/>
        # </ext:asOtherIDs>
        # <!-- ИНН пациента -->
        # <ext:asOtherIDs classCode="IDENT">
        #         <ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        #         <ext:documentType code="4" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Индивидуальный номер налогоплательщика"/>
        #         <ext:documentNumber number="123456789101"/>
        #         <ext:effectiveTime value="20100214"/>
        #         <ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        #         <!-- Идентификатор организации, выдавшей полис -->
        #         <ext:id nullFlavor="NA"/>
        #         </ext:scopingOrganization>
        #         <!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
        #         <ext:InsuredTerritory nullFlavor="NA"/>
        # </ext:asOtherIDs>
        # </ext:patient>
        # </guardianPerson>
        # </guardian>
        # Место рождения [0..1]
        self.writeStartElement('birthplace')
        self.writeAttribute('classCode', 'BIRTHPL')
        self.writeStartElement('place')
        self.writeStartElement('addr')
        self.writeAttribute('use', 'PHYS')
        # Страна
        self.writeTextElement('country', u'Российская Федерация')
        # Область/Край
        #self.writeTextElement('state', 'Волгоградская область')
        # Город
        #self.writeTextElement('city', 'Урюпинск')
        self.writeEndElement()      # unitID
        self.writeEndElement()      # addr
        self.writeEndElement()      # place
        self.writeEndElement()      # birthplace

        self.writeStartElement('providerOrganization')
        self.writeAttribute('classCode', 'ORG')
        self.writeAttribute('determinerCode', 'INSTANCE')
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        self.writeTextElement('name', RCDP_NAME)
        self.writeEndElement()

        #self.writeStartElement('ext:patient')
        #self.writeAttribute('HL7-ClassName', 'PAT')
        #self.writeAttribute('HL7-Domain', 'PRPA_RM000000')
        #self.writeAttribute('realmCode', 'RU')

        # Шаблон: Место работы пациента [0..1]
        # <ext:asEmployment>
        #    <!-- Название отрасли -->
        #    <ext:jobCode code="51141" codeSystem="1.2.643.5.1.13.2.1.1.62" codeSystemName="Общероссийский классификатор видов экономической деятельности" displayName="Деятельность агентов по оптовой торговле офисным оборудованием и вычислительной техникой [2]"/>
        #    <!-- Должность -->
        #    <ext:jobTitleName>Агент по оптовой торговле офисным оборудованием и вычислительной техникой [2]</ext:jobTitleName>
        #    <ext:employerOrganization classCode="ORG" determinerCode="INSTANCE">
        #        <!-- Код ОГРН работодателя [1]-->
        #        <ext:id nullFlavor="NI"/>
        #        <!-- Название предприятия [1] -->
        #        <ext:name>ООО "Формоза"</ext:name>
        #    </ext:employerOrganization>
        # </ext:asEmployment>
        #<ext:asLivingTerritoryCode code="77000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
        #<!-- Тип места жительства -->
        # <ext:asResidenceType code="1" codeSystem="1.2.643.5.1.13.2.1.1.504" codeSystemName="Справочник жителя села или города" displayName="Городской"/>
        # <!-- Социальный статус -->
        # <ext:asMember classCode="MBR">
        #     <!-- Группа, к которой относится пациент -->
        #     <ext:group classCode="SocialStatus">
        #         <ext:code code="4" codeSystem="1.2.643.5.1.13.2.1.1.366" codeSystemName="Справочник социального статуса (СМП)" displayName="Работающий"/>
        #     </ext:group>
        # </ext:asMember>
        # <!-- Категория льготности -->
        # <ext:asMember classCode="MBR">
        #     <ext:effectiveTime>
        #         <ext:low inclusive="false" value="17120101"/>
        #         <ext:high value="20200101"/>
        #     </ext:effectiveTime>
        #     <!-- Группа, к которой относится пациент -->
        #     <ext:group classCode="PopulationCategory">
        #         <ext:code code="10" codeSystem="1.2.643.5.1.13.2.1.1.185" codeSystemName="Классификатор льготных категорий" displayName="Подвергшиеся воздействию радиации"/>
        #     </ext:group>
        # </ext:asMember>
        # <!--Идентификаторы -->
        # <ext:asOtherIDs classCode="IDENT">
        #     <ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        #     <!-- OID документа-->
        #     <ext:id root="1.2.643.5.1.13.2.7.1.62.3"/>
        #     <!--Тип идентификатора-->
        #     <ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Документ, удостоверяющий личность">
        #         <!--Тип документа, удостоверяющего личность -->
        #         <ext:translation code="14" codeSystem="1.2.643.5.1.13.2.1.1.187" codeSystemName="Классификатор типов документов, удостоверяющих личность" displayName="ПАСПОРТ РОССИИ"/>
        #     </ext:documentType>
        #     <!-- Номер и серия документа-->
        #     <ext:documentNumber series="4567" number="1234567890"/>
        #     <!-- Дата выдачи документа-->
        #     <ext:effectiveTime value="20020505"/>
        #     <!-- Организация, выдавшая документ-->
        #     <ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        #         <!--Идентификатор организации, выдавшей документ -->
        #         <ext:id nullFlavor="NA"/>
        #         <!--Наименование организации, выдавшей документ-->
        #         <ext:name>ОУФМС России, по Даниловскому району, г Москвы в ЮАО</ext:name>
        #     </ext:scopingOrganization>
        #         </ext:asOtherIDs>
        # 		<!-- Полисы страхования, предъявленные пациентом -->
        # 		<!-- Полис ОМС -->
        # 		<ext:asOtherIDs classCode="HLD">
        # 			<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        # 			<ext:documentType code="1" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис обязательного медицинского страхования"/>
        # 			<!-- Собственно номер и серия (если есть) и тип полиса -->
        # 			<ext:documentNumber series="35" number="1234567890"/>
        # 			<!-- Даты начала и окончания действия полиса -->
        # 			<ext:effectiveTime value="20100214"/>
        # 			<!-- Страховая компания, выдавшая полис -->
        # 			<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        # 				<!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
        # 				<ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
        # 				<!-- Название страховой компании -->
        # 				<ext:name>ЗАО "МАКС-М"</ext:name>
        # 			</ext:scopingOrganization>
        # 			<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
        # 			<ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
        # 		</ext:asOtherIDs>
        # 		<!-- Полис ДМС -->
        # 		<ext:asOtherIDs classCode="HLD">
        # 			<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        # 			<ext:documentType code="2" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис добровольного медицинского страхования"/>
        # 			<!-- Собственно номер и серия (если есть) и тип полиса -->
        # 			<ext:documentNumber series="1111" number="0987654321"/>
        # 			<!-- Даты начала и окончания действия полиса -->
        # 			<ext:effectiveTime>
        # 				<ext:low value="20130214"/>
        # 				<ext:high value="20130813"/>
        # 			</ext:effectiveTime>
        # 			<!-- Страховая компания, выдавшая полис -->
        # 			<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        # 				<!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
        # 				<ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
        # 				<!-- Название страховой компании -->
        # 				<ext:name>ЗАО "МАКС-М"</ext:name>
        # 			</ext:scopingOrganization>
        # 			<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
        # 			<ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
        # 		</ext:asOtherIDs>
        # 		<!-- Другие идентификаторы пациента -->
        # 		<!-- СНИЛС пациента -->
        # 		<ext:asOtherIDs classCode="IDENT">
        # 			<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        # 			<ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Страховой номер индивидуального лицевого счёта"/>
        # 			<!--<ext:documentNumber type="СНИЛС" number="000-000-000 00"/>-->
        # 			<ext:documentNumber number="000-000-000 00"/>
        # 			<ext:effectiveTime value="20100214"/>
        # 		</ext:asOtherIDs>
        # 		<!-- ИНН пациента -->
        # 		<ext:asOtherIDs classCode="IDENT">
        # 			<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
        # 			<ext:documentType code="4" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Индивидуальный номер налогоплательщика"/>
        # 			<ext:documentNumber number="123456789101"/>
        # 			<ext:effectiveTime value="20100214"/>
        # 			<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
        # 				<!-- Идентификатор организации -->
        # 				<ext:id nullFlavor="NA"/>
        # 			</ext:scopingOrganization>
        # 			<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
        # 			<ext:InsuredTerritory nullFlavor="NA"/>
        # 		</ext:asOtherIDs>
        # 		<ext:asUnidentified value="true"/>
        #self.writeEndElement()      # ext:patient
        #self.writeEndElement()      # patient
        self.writeEndElement()      # patientRole
        self.writeEndElement()      # recordTarget

        # КОНЕЦ ДАННЫХ О ПАЦИЕНТЕ

        # ДАННЫЕ ОБ АВТОРЕ ДОКУМЕНТА
        # Шаблон: Медицинский работник - автор [1]
        self.writeStartElement('author')
        self.writeAttribute('typeCode', 'AUT')
        # дата и время создания включенного объекта (дата и время компиляции) [1]
        self.writeEmptyElement('time')
        self.writeAttribute('value', QDateTime.currentDateTime().toString('yyyyMMddHHmmss'))
        self.writeStartElement('assignedAuthor')
        self.writeAttribute('classCode', 'ASSIGNED')
        # код медицинского работника (врача) [1]
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        self.writeAttribute('extension', forceString(record.value('eventExecPersonSnils')))
        self.writeAttribute('assigningAuthorityName', RCDP_NAME)

        self.writeStartElement('ext:asLicencedEntity')
        self.writeAttribute('HL7-ClassName', 'LIC')
        self.writeAttribute('HL7-Domain', 'PRPM_RM000000')
        self.writeAttribute('realmCode', 'RU')
        self.writeEmptyElement('ext:code')
        self.writeAttribute('code', '28')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.181')
        self.writeAttribute('codeSystemName', u'Номенклатура специальностей специалистов с высшим и послевузовским медицинским и фармацевтическим образованием в сфере здравоохранения')
        self.writeAttribute('displayName', u'Травматология и ортопедия')
        self.writeEndElement()      # ext:asLicencedEntity

        self.writeStartElement('code')
        self.writeAttribute('code', '90')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.607')
        self.writeAttribute('codeSystemName', u'Номенклатура должностей медицинских работников и фармацевтических работников')
        self.writeAttribute('displayName', u'Врач-хирург')

        self.writeEmptyElement('translation')
        self.writeAttribute('code', 'DOCOBS')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.30')
        self.writeAttribute('codeSystemName', u'Роль в оказании медицинской помощи')
        self.writeAttribute('displayName', u'Лечащий врач')
        self.writeEndElement()      # code

        # Шаблон: Специальность [0..1]
        # <ext:asLicencedEntity HL7-ClassName="LIC" HL7-Domain="PRPM_RM000000" realmCode="RU">
        # <!-- код специальности и название -->
        # <ext:code code="28" codeSystem="1.2.643.5.1.13.2.1.1.181" codeSystemName="Номенклатура специальностей специалистов с высшим и послевузовским медицинским и фармацевтическим образованием в сфере здравоохранения"  displayName="Травматология и ортопедия"/>
        # </ext:asLicencedEntity>
        # <!-- Код должности роли медицинского работника по справочнику ("1.2.643.5.1.13.2.1.1.89") Минздрава РФ -->
        # <code code="90" codeSystem="1.2.643.5.1.13.2.1.1.607" codeSystemName="Номенклатура должностей медицинских работников и фармацевтических работников" displayName="Врач-хирург">
        # <translation code="DOCOBS" codeSystem="1.2.643.5.1.13.2.7.1.30" codeSystemName="Роль в оказании медицинской помощи" displayName="Лечащий врач"/>
        # </code>
        # <telecom value="tel:+78442171311"/>
        # <telecom value="mailto:a.privalov@oblhosp.volgograd.ru"/>
        # <telecom value="fax:+78442171300"/>
        # Фамилия, Имя, Отчество [1]
        self.writeStartElement('assignedPerson')
        self.writeAttribute('classCode', 'PSN')
        self.writeAttribute('determinerCode', 'INSTANCE')

        self.writeStartElement('name')
        # Фамилия
        self.writeTextElement('family', eventExecPersonLastName)
        # Имя
        self.writeTextElement('given', eventExecPersonFirstName)
        # Отчество
        if eventExecPersonPatrName:
            self.writeTextElement('given', eventExecPersonPatrName)
        self.writeEndElement()      # name

        self.writeStartElement('ext:person')
        self.writeStartElement('ext:asOtherIDs')
        self.writeAttribute('classCode', 'IDENT')
        self.writeEmptyElement('ext:documentType')
        self.writeAttribute('code', '3')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.62')
        self.writeAttribute('codeSystemName', u'Тип внешнего идентификатора')
        self.writeAttribute('displayName', u'Страховой номер индивидуального лицевого счёта')
        self.writeEmptyElement('ext:documentNumber')
        self.writeAttribute('number', eventExecPersonSnils)
        self.writeEndElement()      # ext:asOtherIDs
        self.writeEndElement()      # ext:person
        self.writeEndElement()      # assignedPerson

        # Шаблон: Медицинская организация [1]
        self.writeStartElement('representedOrganization')
        self.writeAttribute('classCode', 'ORG')
        self.writeAttribute('determinerCode', 'INSTANCE')

        # Код учреждения в реестре Минздрава РФ [1]
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        # Наименование учреждения [1]
        self.writeTextElement('name', RCDP_NAME)
        # Контактные данные [1..*]
        #telecom value="tel:+74952171300"/>
        #<telecom value="mailto:info@oblhosp.mos.ru"/>
        #<telecom value="fax:+74952171300"/>
        # Адрес больницы [1]
        self.writeStartElement('addr')
        self.writeAttribute('use', 'PHYS')
        # Страна
        self.writeTextElement('country', u'Российская Федерация')
        # Область/Край
        #self.writeTextElement('state', u'Москва')
        # Город
        self.writeTextElement('city', u'Смоленск')
        # Улица
        #self.writeTextElement('streetName', 'ул. Ангарская')
        # Номер дома
        #self.writeTextElement('houseNumber', '22')
        # Почтовый индекс
        #self.writeTextElement('postalCode', '104567')
        self.writeEndElement()      # addr
        self.writeEndElement()      # representedOrganization
        self.writeEndElement()      # assignedAuthor
        self.writeEndElement()      # author
        # КОНЕЦ ДАННЫХ ОБ АВТОРЕ

        # ДАННЫЕ ОБ ОРГАНИЗАЦИИ-ВЛАДЕЛЬЦЕ ДОКУМЕНТА НАЧАЛО
        # Шаблон: Владелец документа [1]
        self.writeStartElement('custodian')

        self.writeAttribute('typeCode', 'CST')
        self.writeStartElement('assignedCustodian')
        self.writeStartElement('representedCustodianOrganization')
        # Код учреждения в реестре Минздрава РФ [1]
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        # Наименование учреждения [1]
        self.writeTextElement('name', RCDP_NAME)
        self.writeEndElement()      # representedCustodianOrganization
        self.writeEndElement()      # assignedCustodian
        self.writeEndElement()      # custodian
        # КОНЕЦ ДАННЫХ ОБ ОРГАНИЗАЦИИ-ВЛАДЕЛЬЦЕ ДОКУМЕНТА

        # ОБЩИЕ СВЕДЕНИЯ О ДОКУМЕНТЕ НАЧАЛО
        self.writeStartElement('documentationOf')
        self.writeStartElement('serviceEvent')
        self.writeAttribute('classCode', 'PCPR')
        self.writeEmptyElement('templateId')
        self.writeAttribute('root', '1.2.643.5.1.13.2.7.5.1.6.6')
        self.writeStartElement('effectiveTime')
        # Дата начала госпитализации
        self.writeEmptyElement('low')
        self.writeAttribute('value', forceDateTime(record.value('eventSetDate')).toString('yyyyMMddHHmm'))
        # Дата окончания госпитализации
        self.writeEmptyElement('high')
        self.writeAttribute('value', forceDateTime(record.value('eventExecDate')).toString('yyyyMMddHHmm'))
        self.writeEndElement()      # effectiveTime
        self.writeStartElement('performer')
        self.writeAttribute('typeCode', 'PRF')
        self.writeEmptyElement('functionCode')
        self.writeAttribute('code', '12')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.30')
        self.writeAttribute('codeSystemName', u'Роль в оказании медицинской помощи')
        self.writeAttribute('displayName', u'Лечащий врач')
        self.writeStartElement('assignedEntity')
        # код медицинского работника (врача) [1]
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        self.writeAttribute('extension', eventExecPersonSnils)
        # Код должности роли медицинского работника по справочнику ("1.2.643.5.1.13.2.1.1.89") Минздрава РФ
        # self.writeEmptyElement('code')
        # self.writeAttribute('code', '91')
        # self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.607')
        # self.writeAttribute('codeSystemName', u'Номенклатура должностей медицинских работников и фармацевтических работников')
        # self.writeAttribute('displayName', u'врач-хирург')
        self.writeStartElement('assignedPerson')
        self.writeStartElement('name')
        # Фамилия
        self.writeTextElement('family', eventExecPersonLastName)
        # Имя
        self.writeTextElement('given', eventExecPersonFirstName)
        # Отчество
        if eventExecPersonPatrName:
            self.writeTextElement('given', eventExecPersonPatrName)
        self.writeEndElement()      # name
        self.writeEndElement()      # assignedPerson
        self.writeEndElement()      # assignedEntity
        self.writeEndElement()      # performer
        self.writeEndElement()      # serviceEvent
        self.writeEndElement()      # documentationOf
        # КОНЕЦ ОБЩИХ СВЕДЕНИЙ О ДОКУМЕНТЕ
        #FIXME: max
        # Случай оказания медицинской помощи [1]
        self.writeStartElement('componentOf')
        self.writeStartElement('encompassingEncounter')
        # Номер истории болезни
        # OID и номер истории болезни должны образовывать уникальную комбинацию в рамках всей системы
        self.writeEmptyElement('id')
        self.writeAttribute('root', RCDP_ID)
        self.writeAttribute('extension', 'Document' + forceString(record.value('eventId')))

        #FIXME: Следующие справочники не найдены.
        # Тип случая заболевания (госпитализация)
        self.writeEmptyElement('code')
        self.writeAttribute('code', 'STAT')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.1')
        self.writeAttribute('codeSystemName', u'Вид случая заболевания')
        self.writeAttribute('displayName', u'Госпитализация')

        # Дата госпитализации
        self.writeStartElement('effectiveTime')
        # Дата начала госпитализации
        self.writeEmptyElement('low')
        self.writeAttribute('value', forceDate(record.value('eventSetDate')).toString('yyyyMMdd'))
        # Дата окончания госпитализации
        self.writeEmptyElement('high')
        self.writeAttribute('value', forceDate(record.value('eventExecDate')).toString('yyyyMMdd'))
        self.writeEndElement()      # effectiveTime
        # Шаблон: Госпитализация стационар, дневной стационар [1]
        self.writeStartElement('ext:encounter')
        self.writeAttribute('HL7-ClassName', 'ENC')
        self.writeAttribute('HL7-Domain', 'PRPA_RM000000')
        self.writeAttribute('realmCode', 'RU')
        # Кем доставлен [1]
        self.writeEmptyElement('ext:admissionReferralSourceCode')
        self.writeAttribute('code', '12')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.110')
        self.writeAttribute('codeSystemName', u'Классификатор каналов госпитализации')
        self.writeAttribute('displayName', u'Самостоятельно')
        # Общее количество койко-дней
        self.writeEmptyElement('ext:lengthOfStayQuantity')
        self.writeAttribute('value', '16')
        # Госпитализирован по поводу данного заболевания в текущем году [1]
        self.writeEmptyElement('ext:priorityCode')
        self.writeAttribute('code', '1')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.109')
        self.writeAttribute('codeSystemName', u'Классификатор количества госпитализаций')
        self.writeAttribute('displayName', u'Госпитализирован впервые в данном году по диагнозу')
        # Время доставки в стационар от начала заболевания [1]
        self.writeEmptyElement('ext:timeAfterBegining')
        self.writeAttribute('code', u'3')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.537')
        self.writeAttribute('codeSystemName', u'Справочник доставки в стационар от начала заболевания')
        self.writeAttribute('displayName', u'позднее 24-х часов')

        self.writeEmptyElement('ext:statusCode')
        self.writeAttribute('code', 'completed')
        self.writeEndElement()      # ext:encounter
        # Исход госпитализации [1]
        # FIXME: Справочник 123 устарел?!
        self.writeEmptyElement('dischargeDispositionCode')
        self.writeAttribute('code', '5')
        self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.123')
        self.writeAttribute('codeSystemName', u'Классификатор исходов госпитализации')
        self.writeAttribute('displayName', u'Умер')
        # FIXME: Конец проблемных справочников

        # Шаблон: Присутствовали [0..1]
        #self.writeStartElement('encounterParticipant')
        #self.writeAttribute('typeCode', 'REF')

        #self.writeStartElement('assignedEntity')
        # Код участника [1]
        #self.writeEmptyElement('id')
        #self.writeAttribute('root', RCDP_ID)
        #self.writeAttribute('extension', forceString(record.value('eventExecPersonRegionalCode')))

        # Код должности и роли медицинского работника
        # FIXME: Справочник не найден
        #self.writeStartElement('code')
        #self.writeAttribute('code', '90')
        #self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.607')
        #self.writeAttribute('codeSystemName', u'Номенклатура должностей медицинских работников и фармацевтических работников')
        #self.writeAttribute('displayName', u'Врач-хирург')

        #self.writeEmptyElement('translation')
        #self.writeAttribute('code', '17')
        #self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.7.1.30')
        #self.writeAttribute('codeSystemName', u'Роль в оказании медицинской помощи')
        #self.writeAttribute('displayName', u'Наблюдатель')
        #self.writeEndElement()      # code

        # Код и название специальности
        # Шаблон: Специальность [1]
        #self.writeStartElement('ext:asLicencedEntity')
        #self.writeAttribute('HL7-ClassName', 'LIC')
        #self.writeAttribute('HL7-Domain', 'PRPM_RM000000')
        #self.writeAttribute('realmCode', 'RU')
        #self.writeEmptyElement('ext:code')
        #self.writeAttribute('code', forceString(record.value('eventExecPersonSpecialityFederalCode')))
        #self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.181')
        #self.writeAttribute('codeSystemName', u'Номенклатура специальностей специалистов с высшим и послевузовским медицинским и фармацевтическим образованием в сфере здравоохранения')
        #self.writeAttribute('displayName', forceString(record.value('specialityName')))
        #self.writeEndElement()      # ext:asLicencedEntity
        # Фамилия, Имя, Отчество (если есть) участника [1]
        #self.writeStartElement('assignedPerson')
        #self.writeAttribute('classCode', 'PSN')
        #self.writeAttribute('determinerCode', 'INSTANCE')
        #self.writeStartElement('name')
        # Фамилия
        #self.writeTextElement('family', eventExecPersonLastName)
        # Имя
        #self.writeTextElement('given', eventExecPersonFirstName)
        # Отчество
        #if eventExecPersonPatrName:
        #    self.writeTextElement('given', eventExecPersonPatrName)
        #self.writeEndElement()      # name
        #self.writeEndElement()      # assignedPerson
        #self.writeStartElement('representedOrganization')
        #self.writeAttribute('classCode', 'ORG')
        #self.writeAttribute('determinerCode', 'INSTANCE')

        # Код организации
        #self.writeEmptyElement('id')
        #self.writeAttribute('root', RCDP_ID)

        # FIXME: справочник не найден
        # Название организации [1]
        #self.writeTextElement('name', RCDP_NAME)
        # Тип медицинской орагнизации
        #self.writeEmptyElement('standardIndustryClassCode')
        #self.writeAttribute('code', '111052')
        #self.writeAttribute('codeSystem', '1.2.643.5.1.13.2.1.1.77')
        #self.writeAttribute('codeSystemName', u'Тип медицинской организации')
        #self.writeAttribute('displayName', u'Центральная районная больница')
        #self.writeEndElement()      # representedOrganization
        #self.writeEndElement()      # assignedEntity
        #self.writeEndElement()      # encounterParticipant
        self.writeEndElement()      # encompassingEncounter
        self.writeEndElement()      # componentOf
        self.writeStartElement('component')
        self.writeAttribute('typeCode', 'COMP')
        self.writeStartElement('nonXMLBody')
        eventText = u''
        MKB = forceString(record.value('diagnosisMKB'))
        if MKB:
            eventText += u'Выявленные диагнозы:\n\t%s, код ответственного врача: %s\n\n' % (MKB, forceString(record.value('diagnosisPersonCode')))
        if forceRef(record.value('visitId')):
            eventText += u'Посещения:\n\t%s, %s, код услуги: %s, код врача: %s\n' % \
                         (forceString(record.value('visitDate')),
                          u'первичное' if forceInt(record.value('visitIsPrimary')) == 1 else u'повторное',
                          forceString(record.value('visitServiceCode')),
                          forceString(record.value('visitPersonCode'))
                         )
        if forceRef(record.value('actionId')):
            eventText += u'Проведенные мероприятия:\n\t%s - %s, код услуги: %s, статус: %s, количество: %s, код врача: %s, код организации: %s' % \
                         (
                             forceString(record.value('actionBegDate')),
                             forceString(record.value('actionEndDate')),
                             forceString(record.value('actionTypeCode')),
                             forceString(record.value('actionStatus')),
                             forceString(record.value('actionAmount')),
                             forceString(record.value('actionPersonCode')),
                             forceString(record.value('actionOrgCode'))
                         )



        self.writeTextElement('text', eventText)

        self.writeEndElement()      # nonXMLBody
        self.writeEndElement()      # component
        # СОДЕРЖАНИЕ КОНЕЦ

class CFIEMKExport(object):
    def __init__(self, args, dt):
        self.dir = forceStringEx(args['dir'])
        self.dt = dt
        self.prevClientId = None
        self.prevEventId = None
        self.clientData = smartDict()
        self.prevClientId = None

    def createFile(self, dir):
        fileName = u'HM_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddTHHmmss.zzz'))
        return QtCore.QFile(os.path.join(dir, fileName))

    def startExport(self):
        outFile = self.createFile(dir)
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)

        db = QtGui.qApp.db
        query = db.query(createExportR67FIEMKQuery(db, self.dt))

        if query.size() > 0:
            out = CMessageDataStreamWriter(None, {}, None)
            out.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            out.writeFileHeader(outFile)

            while query.next():
                self.processRecord(query.record())

            out.writeFileFooter()
        outFile.close()

    def processRecord(self, record):
        clientId = forceRef(record.value('client_id'))
        eventId = forceRef(record.value('eventId'))
        self.clientData = smartDict()
        if self.prevClientId != clientId:
            self.prevClientId = clientId
        self.write

        if not clientId in self.clientData:
            self.clientData[clientId] = smartDict()
            cd = self.clientData[clientId]
            cd.lastName = forceString(record.value('clientLastName'))
            cd.firstName = forceString(record.value('clientFirstName'))
            cd.patrName = forceString(record.value('clientPatrName'))
            cd.SNILS = forceString(record.value('SNILS'))
            cd.sex = forceInt(record.value('clientSex'))
            cd.birthDate = forceString(record.value('clientBirthDate'))
            cd.birthPlace = forceString(record.value('clientBirthPlace'))
            cd.locAddressKLADR = forceString(record.value('clientLocAddressKLADR'))
            cd.locAddressStreet = forceString(record.value('clientLocAddressStreet'))
            cd.locAddressHouse = forceString(record.value('clientLocAddressHouse'))
            cd.locAddressCorpus = forceString(record.value('clientLocAddressCorpus'))
            cd.locAddressFlat = forceString(record.value('clientLocAddressFlat'))
            cd.regAddressKLADR = forceString(record.value('clientRegAddressKLADR'))
            cd.regAddressStreet = forceString(record.value('clientRegAddressStreet'))
            cd.regAddressHouse = forceString(record.value('clientRegAddressHouse'))
            cd.regAddressCorpus = forceString(record.value('clientRegAddressCorpus'))
            cd.regAddressFlat = forceString(record.value('clientRegAddressFlat'))
            cd.cPolicyNumber = forceString(record.value('clientCPolicyNumber'))
            cd.cPolicySerial = forceString(record.value('clientCPolicySerial'))
            cd.cPolicyBegDate = forceString(record.value('clientCPolicyBegDate'))
            cd.cPolicyEndDate = forceString(record.value('clientCPolicyEndDate'))
            cd.vPolicyNumber = forceString(record.value('clientVPolicyNumber'))
            cd.vPolicySerial = forceString(record.value('clientVPolicySerial'))
            cd.vPolicyBegDate = forceString(record.value('clientVPolicyBegDate'))
            cd.vPolicyEndDate = forceString(record.value('clientVPolicyEndDate'))
            cd.insurerCode = forceString(record.value('clientPolicyInsurerCode'))
            cd.insurerName = forceString(record.value('clientPolicyInsurerName'))
            cd.documentNumber = forceString(record.value('clientDocumentNumber'))
            cd.documentSerial = forceString(record.value('clientDocumentSerial'))
            cd.documentDate = forceString(record.value('clientDocumentDate'))
            cd.documentOrg = forceString(record.value('clientDocumentDate'))
            cd.documentTypeCode = forceString(record.value('clientDocumentTypeCode'))
            cd.documentTypeName = forceString(record.value('clientDocumentTypeName'))
            cd.contactNumber = forceString(record.value('clientContactNumber'))
            cd.post = forceString(record.value('clientPost'))
            cd.employerName = forceString(record.value('clientEmployerName'))
            cd.events = {}
        else:
            cd = self.clientData[clientId]

        if not eventId in cd.events:
            event = smartDict()
            event.eventId = eventId
            event.begDate = forceDateTime(record.value('eventSetDate'))
            event.endDate = forceDateTime(record.value('eventExecDate'))
            event.createDatetime = forceString(record.value('eventCreateDatetime'))
            event.modifyDatetime = forceString(record.value('eventModifyDatetime'))
            event.orgOID = forceString(record.value('eventOrgOID'))
            event.orgName = forceString(record.value('eventOrgName'))
            event.order = forceInt(record.value('eventOrder'))
            event.isPrimary = forceInt(record.value('eventIsPrimary'))
            event.externalId = forceString(record.value('eventExternalId'))

            execPerson = smartDict()
            execPerson.personId = forceString(record.value('eventExecPersonId'))
            execPerson.lastName = forceString(record.value('eventExecPersonLastName'))
            execPerson.firstName = forceString(record.value('eventExecPersonFirstName'))
            execPerson.patrName = forceString(record.value('eventExecPersonPatrName'))
            execPerson.SNILS = forceString(record.value('eventExecPersonSNILS'))
            execPerson.specialityCode = forceString(record.value('eventExecPersonSpecialityCode'))
            execPerson.specialityName = forceString(record.value('eventExecPersonSpecialityName'))
            execPerson.postCode = forceString(record.value('eventExecPersonPostCode'))
            execPerson.postName = forceString(record.value('eventExecPersonPostName'))
            execPerson.orgOID = forceString(record.value('eventExecPersonOrgOID'))
            execPerson.orgName = forceString(record.value('eventExecPersonOrgName'))
            event.execPerson = execPerson
            event.diags = {}
            event.actions = {}
            event.visits = {}
            # TODO: подробная информация об организации врача (?)

        diagnosisId = forceRef(record.value('diagnosisId'))
        if diagnosisId and not diagnosisId in event.diags:
            diag = smartDict()
            diag.diagId = diagnosisId
            diag.MKBCode = forceString(record.value('diagnosisMKBCode'))
            diag.MKBName = forceString(record.value('diagnosisMKBName'))
            diag.characterCode = forceString(record.value('diagnosticCharacterCode'))
            diag.characterName = forceString(record.value('diagnosticCharacterName'))
            diag.typeCode = forceString(record.value('diagnosticTypeCode'))
            diag.typeName = forceString(record.value('diagnosticTypeName'))
            event.diags[diagnosisId] = diag

        visitId = forceRef(record.value('visitId'))
        if visitId and not visitId in event.visits:
            visit = smartDict()
            visit.visitId = visitId
            visit.date = forceDateTime(record.value('visitDate'))
            visitPerson = smartDict()
            visitPerson.lastName = forceString(record.value('visitPersonLastName'))
            visitPerson.firstName = forceString(record.value('visitPersonFirstName'))
            visitPerson.patrName = forceString(record.value('visitPersonPatrName'))
            visitPerson.SNILS = forceString(record.value('visitPersonSNILS'))
            visitPerson.speciatityCode = forceString(record.value('visitPersonSpecialityCode'))
            visitPerson.specialityName = forceString(record.value('visitPersonSpecialityName'))
            visitPerson.postCode = forceString(record.value('visitPersonPostCode'))
            visitPerson.postName = forceString(record.value('visitPersonPostName'))
            visitPerson.orgOID = forceString(record.value('visitPersonOrgOID'))
            visitPerson.orgName = forceString(record.value('visitPersonOrgName'))

        actionId = forceRef(record.value('actionId'))
        if actionId and not actionId in event.actions:
            tAction = smartDict()
            tAction.action = CAction.getActionById(actionId)

            actionPerson = smartDict()
            actionPersonId = forceRef(record.value('actionPersonId'))
            if actionPersonId:
                actionPerson.personId = actionPersonId
                actionPerson.lastName = forceString(record.value('actionPersonLastName'))
                actionPerson.firstName = forceString(record.value('actionPersonFirstName'))
                actionPerson.patrName = forceString(record.value('actionPersonPatrName'))
                actionPerson.SNILS = forceString(record.value('actionPersonSNILS'))
                actionPerson.specialityCode = forceString(record.value('actionPersonSpecialityCode'))
                actionPerson.specialityName = forceString(record.value('actionPersonSpecialityName'))
                actionPerson.postCode = forceString(record.value('actionPersonPostCode'))
                actionPerson.postName = forceString(record.value('actionPersonPostName'))
                actionPerson.orgOID = forceString(record.value('actionPersonOrgOID'))
                actionPerson.orgName = forceString(record.value('actionPersonOrgName'))
            tAction.person = actionPerson

            actionSetPerson = smartDict()
            actionSetPersonId = forceRef(record.value('actionSetPersonId'))
            if actionSetPersonId:
                actionSetPerson.personId = actionSetPersonId
                actionSetPerson.lastName = forceString(record.value('actionSetPersonLastName'))
                actionSetPerson.firstName = forceString(record.value('actionSetPersonFirstName'))
                actionSetPerson.patrName = forceString(record.value('actionSetPersonPatrName'))
                actionSetPerson.SNILS = forceString(record.value('actionSetPersonSNILS'))
                actionSetPerson.specialityCode = forceString(record.value('actionSetPersonSpecialityCode'))
                actionSetPerson.specialityName = forceString(record.value('actionSetPersonSpecialityName'))
                actionSetPerson.postCode = forceString(record.value('actionSetPersonPostCode'))
                actionSetPerson.postName = forceString(record.value('actionSetPersonPostName'))
                actionSetPerson.orgOID = forceString(record.value('actionSetPersonOrgOID'))
                actionSetPerson.orgName = forceString(record.value('actionSetPersonOrgName'))
            tAction.setPerson = actionSetPerson

            tAction.orgOID = forceString(record.value('actionOrgOIS'))
            tAction.orgName = forceString(record.value('actionOrgName'))
            event.actions[actionId] = tAction


# *****************************************************************************************

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Export IEMC or Reg Data of clients in specified database.')
    parser.add_argument('-m', dest='mode', type=int, default=0,
                        help='0 - export new IEMC data starting from specified date,'
                             '1 - export all modified Reg Data from specified date,'
                             '2 - export all NEW Reg Data from specified date'
                        )
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-c', dest='miacCode')
    parser.add_argument('-t', dest='datetime', default=None)

    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-D', dest='dir', default=os.getcwd())
    parser.add_argument('-w', dest='webService', default='https://api-iemc-test.rosminzdrav.ru/misstub/ws/miscallback?wsdl')
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)
    #if not args['miacCode']:
    #    print 'Error: you should specify organisation\'s miacCode'
    #    sys.exit(-3)

    app = QtCore.QCoreApplication(sys.argv)
    connectionInfo = {
                          'driverName' : 'MYSQL',
                          'host' : args['host'],
                          'port' : args['port'],
                          'database' : args['database'],
                          'user' : args['user'],
                          'password' : args['password'],
                          'connectionName' : 'IEMK',
                          'compressData' : True,
                          'afterConnectFunc' : None
                    }

    db = connectDataBaseByInfo(connectionInfo)
    QtGui.qApp.db = db
    timestamp = QtCore.QDateTime.currentDateTime()
    fileName = u'HM_%s.xml' % (timestamp.toString('yyMMddTHHmmss.zzz'))
    outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
    outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
    cache = prepareRefBooksCacheById(db)
    dt = args['datetime']
    dt = QDateTime.fromString(dt, 'yyyy-MM-ddTHH:mm:ss') if dt else None # QDateTime.currentDateTime().addSecs(-60)
    if not (dt is None or dt.isValid()):
        print 'Error: incorrect base datetime.'
        sys.exit(-4)

    query = createExportR67FIEMKQuery(db, 0, dt)
    cache = {}
    #test = CPersonalDataStreamWriter(None, cache, args['miacCode'])
    #test.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
    #test.writeFileHeader(outFile, None, QtCore.QDate.currentDate())
    #test.writeFileFooter()
    #outFile.close()
    if query.size() > 0:
        clientsOut = CMessageDataStreamWriter(None, timestamp)
        clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        clientsOut.writeFileHeader(outFile, None, QtCore.QDate.currentDate(), args['webService'])#

        query.first()
        clientsOut.writeRecord(query.record())
        clientsOut.writeFileFooter()
        outFile.close()
    #    while query.next():
    #        clientsOut.writeRecord(query.record())
    #    clientsOut.closeEverything()
    #    clientsOut.writeFileFooter()
    #    outFile.close()

if __name__ == '__main__':
    main()

semd = '''
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="./test/XSL/1.0/main.xsl"?>
<ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ext="urn:hl7-RU-EHR:v1" xsi:schemaLocation="
	urn:hl7-org:v3 ../infrastructure/cda/CDA_RU01.xsd
	urn:hl7-RU-EHR:v1 ../infrastructure/cda/POCD_MT000040_RU01_Extension.xsd">
	<!-- Выписной эпикриз оформляется строго определенным образом. Так, он в обязательном порядке включает следующие составные части:
		 данные о личности пациента, жалобы, анамнез, диагноз, результаты обследований, анализов, осмотров и т.д.;
		 мнения разных специалистов, данные о ходе и итогах лечения, прогноз и рекомендации по продолжению лечения, реабилитации и т.д. -->
<!-- ЗАГОЛОВОК ДОКУМЕНТА -->
	<realmCode code="RU"/>
	<!-- Шаблон: Тип документа CDA [1] -->
	<typeId root="2.16.840.1.113883.1.3" extension="POCD_MT000040_RU01"/>
	<!-- Шаблон: Версия шаблона стандарта: Эпикриз стационара, версия № 1  -->
	<templateId root="1.2.643.5.1.13.2.7.5.1"/>
	<templateId root="1.2.643.5.1.13.2.7.5.1.1"/>
	<!-- Шаблон: Уникальный номер экземпляра документа. OID root и extention должны образовать уникальную комбинацию. Extention может задаваться в виде UUID [1] -->
	<id root="1.2.643.5.1.13.3.25.77.761" extension="87654765-8788-7657-2238-83DA8EF7D2SS15"/>
	<!-- Шаблон: Тип медицинского документа [1] -->
	<code code="1_1" codeSystem="1.2.643.5.1.13.2.1.1.1" codeSystemName="Система электронных медицинских документов" displayName="Эпикриз стационара"/>
	<!-- Шаблон: Название [1] -->
	<title>Эпикриз стационара №50</title>
	<!-- Шаблон: Дата создания документа [1] -->
	<effectiveTime value="20131218114723"/>
	<!-- Шаблон: Уровень конфиденциальности документа [1] -->
	<confidentialityCode code="V" codeSystem="2.16.840.1.113883.5.25" codeSystemName="Уровень конфиденциальности документа" displayName="Закрыто">
		<!-- Уровень доступа опекуна/попечителя -->
		<translation code="R" codeSystem="1.2.643.5.1.13.2.7.1.9" codeSystemName="Уровень конфиденциальности опекуна" displayName="Ограниченно"/>
		<!-- Уровень доступа врача -->
		<translation code="N" codeSystem="1.2.643.5.1.13.2.7.1.10" codeSystemName="Уровень конфиденциальности врача" displayName="Открыто"/>
	</confidentialityCode>
	<!-- Шаблон: Язык документа [1] -->
	<languageCode code="RU"/>
	<!-- Шаблон: Номер истории болезни, к которой относится документ [1] -->
	<setId root="1.2.643.5.1.13.3.25.77.761" extension="2013/8045"/>
	<!-- Шаблон: Версия данного документа [1] -->
	<versionNumber value="2"/>
	<!-- НАЧАЛО ДАННЫХ О ПАЦИЕНТЕ -->
	<!-- Шаблон: Эпикриз_пациент [1] -->
	<recordTarget typeCode="RCT">
		<!-- Область описания: "PAT" - пациент -->
		<realmCode code="PAT"/>
		<patientRole classCode="PAT">
			<!-- Код пациента -->
			<!-- Это автоматически генерируемый МИС id используется для соотнесения детальных данных таких как способ обращения, дата рождения, возраст и т.д. Может быть как UUID, так и код, присвоенный МО, см. тег patient -->
			<!-- id root="1.2.643.5.1.13.3.25.77.761" extension="7AA0BAAC-0CD0-11E0-9516-4350DFD72085"/> -->
			<!-- Код физического лица ("48905059995") в организации ("1.2.643.5.1.13.3.25.77.761") -->
			<id root="1.2.643.5.1.13.3.25.77.761" extension="9950710"/>
			<!-- Адрес пациента [0..2] начало блока -->
			<!-- Адрес фактического места жительства -->
			<addr use="H">
				<!-- Страна -->
				<country>Российская Федерация</country>
				<!-- Область/Край -->
				<county>Новосибирская область</county>
				<!-- Город -->
				<city>Новосибирск</city>
				<!-- streetAddressLine используется только для неструктурированного указания адреса, например: -->
				<streetAddressLine>9, Лескова ул., Новосибирск, Новосибирская область, Российская Федерация, 630008</streetAddressLine>
				<!-- Улица -->
				<streetName>Лескова ул.</streetName>
				<!-- Номер дома -->
				<houseNumber>69</houseNumber>
				<!-- Квартира -->
				<additionalLocator>9</additionalLocator>
				<!-- Почтовый индекс -->
				<postalCode>630008</postalCode>
				<!-- Код КЛАДР населенного пункта -->
				<unitID>5400000100000</unitID>
				<!-- Геокоординаты объекта -->
				<direction>55.022155,82.950660</direction>
			</addr>
			<!-- Адрес постоянной регистрации -->
			<addr use="HP">
				<!-- Страна -->
				<country>Российская Федерация</country>
				<!-- Область/Край -->
				<state>Новосибирская область</state>
				<!-- Район -->
				<county>Калининский район</county>
				<!-- Город/Населенный пункт -->
				<city>Пашино</city>
				<!-- streetAddressLine используется только для неструктурированного указания адреса, например: -->
				<!--<streetAddressLine>11-25, Новоуральская ул., Пашино, Калининский район, Новосибирская область, Российская Федерация, 630900</streetAddressLine> -->
				<!-- Улица -->
				<streetName>Новоуральская ул.</streetName>
				<!-- Номер дома -->
				<houseNumber>11</houseNumber>
				<!-- Квартира -->
				<additionalLocator>25</additionalLocator>
				<!-- Почтовый индекс -->
				<postalCode>630900</postalCode>
				<!-- Код КЛАДР населенного пункта -->
				<unitID>5400000100400</unitID>
			</addr>
			<!-- Конец блока адреса -->
			<!-- Телефон пациента 1 -->
			<telecom value="tel:+79876543210"/>
			<!-- Телефон пациента 2 -->
			<telecom use="MC" value="tel:+79031234567"/>
			<!-- Адрес электронной почты пациента -->
			<telecom value="mailto:viktor.korneev@mail.ru"/>
			<!-- Факс пациента -->
			<telecom value="fax:+78442171300"/>
			<!--Информация, для идентификации пациента -->
			<patient classCode="PSN" determinerCode="INSTANCE">
				<!--Идентификатор пациента в МО (МИС) -->
				<id root="1.2.643.5.1.13.3.25.77.761" extension="9950710"/>
				<!-- Фамилия, Имя, Отчество [0..1] -->
				<name>
					<!-- Фамилия -->
					<family>Незнамов</family>
					<!-- Имя -->
					<given>Сергей</given>
					<!-- Отчество -->
					<given>Васильевич</given>
				</name>
				<!-- Пол пациента [1] -->
				<administrativeGenderCode code="1" codeSystem="1.2.643.5.1.13.2.1.1.156" codeSystemName="Классификатор типов пола" displayName="Мужской"/>
				<!-- Дата рождения [0..1] -->
				<birthTime value="19240627"/>
				<!-- Шаблон: Другие участники [0..*] -->
				<!-- Другой участник случая 1 (опекун / родитель) -->
				<guardian classCode="GUARD">
					<!-- Код другого участника [1] -->
					<!-- Код физического лица ("36598") в реестре ("1.2.643.5.1.13.3.25.77.761") -->
					<id root="1.2.643.5.1.13.3.25.77.761" extension="9950711"/>
					<!-- Отношение к пациенту [1] -->
					<code code="1" codeSystem="1.2.643.5.1.13.2.7.1.15" codeSystemName="Отношение к пациенту" displayName="Родитель"/>
					<!-- Фамилия, имя, отчество -->
					<guardianPerson>
						<name>
							<!-- Фамилия -->
							<family>Незнамов</family>
							<!-- Имя -->
							<given>Василий</given>
							<!-- Отчество -->
							<given>Трофимович</given>
						</name>
						<ext:patient HL7-ClassName="PAT" HL7-Domain="PRPA_RM000000" realmCode="RU">
							<!--Идентификаторы -->
							<ext:asOtherIDs classCode="IDENT">
								<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
								<!-- OID документа-->
								<ext:id root="1.2.643.5.1.13.2.7.1.62.3"/>
								<!--Тип идентификатора-->
								<ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Документ, удостоверяющий личность">
									<!--Тип документа, удостоверяющего личность -->
									<ext:translation code="14" codeSystem="1.2.643.5.1.13.2.1.1.187" codeSystemName="Классификатор типов документов, удостоверяющих личность" displayName="ПАСПОРТ РОССИИ"/>
								</ext:documentType>
								<!-- Номер и серия документа-->
								<ext:documentNumber series="5501" number="123368"/>
								<!-- Дата выдачи документа-->
								<ext:effectiveTime value="200206505"/>
								<!-- Организация, выдавшая документ-->
								<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
									<!--Идентификатор организации, выдавшей документ -->
									<ext:id nullFlavor="NA"/>
									<!--Наименование организации, выдавшей документ-->
									<ext:name>ОУФМС России, по Даниловскому району, г Москвы в ЮАО</ext:name>
								</ext:scopingOrganization>
							</ext:asOtherIDs>
							<!-- Полисы страхования, предъявленные представителем пациента -->
							<!-- Полис ОМС представителя пациента-->
							<ext:asOtherIDs classCode="HLD">
								<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
								<ext:id root="1.2.643.5.1.13.2.7.1.62.1" extension="Полис обязательного медицинского страхования "/>
								<ext:documentType code="1" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис обязательного медицинского страхования"/>
								<!-- Собственно номер и серия (если есть) и тип полиса -->
								<ext:documentNumber series="35" number="3034879659"/>
								<!-- Даты выдачи полиса -->
								<ext:effectiveTime value="20100214"/>
								<!-- Страховая компания, выдавшая полис представителю пациента-->
								<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
									<!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
									<ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
									<!-- Название страховой компании -->
									<ext:name>ЗАО "МАКС-М"</ext:name>
								</ext:scopingOrganization>
								<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
								<ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
							</ext:asOtherIDs>
							<!-- Полис ДМС представителя пациента -->
							<ext:asOtherIDs classCode="HLD">
								<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
								<ext:documentType code="2" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис добровольного медицинского страхования"/>
								<!-- Собственно номер и серия (если есть) и тип полиса -->
								<ext:documentNumber series="1111" number="0987654321"/>
								<!-- Даты начала и окончания действия полиса -->
								<ext:effectiveTime>
									<ext:low value="20130214"/>
									<ext:high value="20130813"/>
								</ext:effectiveTime>
								<!-- Страховая компания, выдавшая полис -->
								<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
									<!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
									<ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
									<!-- Название страховой компании -->
									<ext:name>ЗАО "МАКС-М"</ext:name>
								</ext:scopingOrganization>
								<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
								<ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
							</ext:asOtherIDs>
							<!-- Другие идентификаторы представителя пациента -->
							<!-- СНИЛС представителя пациента -->
							<ext:asOtherIDs classCode="IDENT">
								<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
								<ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Страховой номер индивидуального лицевого счёта"/>
								<ext:documentNumber number="11223344524"/>
								<ext:effectiveTime value="20100214"/>
							</ext:asOtherIDs>
							<!-- ИНН пациента -->
							<ext:asOtherIDs classCode="IDENT">
								<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
								<ext:documentType code="4" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Индивидуальный номер налогоплательщика"/>
								<ext:documentNumber number="123456789101"/>
								<ext:effectiveTime value="20100214"/>
								<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
									<!-- Идентификатор организации, выдавшей полис -->
									<ext:id nullFlavor="NA"/>
								</ext:scopingOrganization>
								<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
								<ext:InsuredTerritory nullFlavor="NA"/>
							</ext:asOtherIDs>
						</ext:patient>
					</guardianPerson>
				</guardian>
				<!-- Место рождения [0..1] -->
				<birthplace classCode="BIRTHPL">
					<place>
						<addr use="PHYS">
							<!-- Страна -->
							<country>Российская Федерация</country>
							<!-- Область/Край  -->
							<state>Волгоградская область</state>
							<!-- Город -->
							<city>Урюпинск</city>
							<unitID/>
						</addr>
					</place>
				</birthplace>
				<ext:patient HL7-ClassName="PAT" HL7-Domain="PRPA_RM000000" realmCode="RU">
					<!-- Шаблон: Место работы пациента [0..1] -->
					<ext:asEmployment>
						<!-- Название отрасли -->
						<ext:jobCode code="51141" codeSystem="1.2.643.5.1.13.2.1.1.62" codeSystemName="Общероссийский классификатор видов экономической деятельности" displayName="Деятельность агентов по оптовой торговле офисным оборудованием и вычислительной техникой [2]"/>
						<!-- Должность -->
						<ext:jobTitleName>Агент по оптовой торговле офисным оборудованием и вычислительной техникой [2]</ext:jobTitleName>
						<ext:employerOrganization classCode="ORG" determinerCode="INSTANCE">
							<!-- Код ОГРН работодателя [1]-->
							<ext:id nullFlavor="NI"/>
							<!-- Название предприятия [1] -->
							<ext:name>ООО "Формоза"</ext:name>
						</ext:employerOrganization>
					</ext:asEmployment>
					<ext:asLivingTerritoryCode code="77000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
					<!-- Тип места жительства -->
					<ext:asResidenceType code="1" codeSystem="1.2.643.5.1.13.2.1.1.504" codeSystemName="Справочник жителя села или города" displayName="Городской"/>
					<!-- Социальный статус -->
					<ext:asMember classCode="MBR">
						<!-- Группа, к которой относится пациент -->
						<ext:group classCode="SocialStatus">
							<ext:code code="4" codeSystem="1.2.643.5.1.13.2.1.1.366" codeSystemName="Справочник социального статуса (СМП)" displayName="Работающий"/>
						</ext:group>
					</ext:asMember>
					<!-- Категория льготности -->
					<ext:asMember classCode="MBR">
						<ext:effectiveTime>
							<ext:low inclusive="false" value="17120101"/>
							<ext:high value="20200101"/>
						</ext:effectiveTime>
						<!-- Группа, к которой относится пациент -->
						<ext:group classCode="PopulationCategory">
							<ext:code code="10" codeSystem="1.2.643.5.1.13.2.1.1.185" codeSystemName="Классификатор льготных категорий" displayName="Подвергшиеся воздействию радиации"/>
						</ext:group>
					</ext:asMember>
					<!--Идентификаторы -->
							<ext:asOtherIDs classCode="IDENT">
								<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
								<!-- OID документа-->
								<ext:id root="1.2.643.5.1.13.2.7.1.62.3"/>
								<!--Тип идентификатора-->
								<ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Документ, удостоверяющий личность">
									<!--Тип документа, удостоверяющего личность -->
									<ext:translation code="14" codeSystem="1.2.643.5.1.13.2.1.1.187" codeSystemName="Классификатор типов документов, удостоверяющих личность" displayName="ПАСПОРТ РОССИИ"/>
								</ext:documentType>
								<!-- Номер и серия документа-->
								<ext:documentNumber series="4567" number="1234567890"/>
								<!-- Дата выдачи документа-->
								<ext:effectiveTime value="20020505"/>
								<!-- Организация, выдавшая документ-->
								<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
									<!--Идентификатор организации, выдавшей документ -->
									<ext:id nullFlavor="NA"/>
									<!--Наименование организации, выдавшей документ-->
									<ext:name>ОУФМС России, по Даниловскому району, г Москвы в ЮАО</ext:name>
								</ext:scopingOrganization>
							</ext:asOtherIDs>
					<!-- Полисы страхования, предъявленные пациентом -->
					<!-- Полис ОМС -->
					<ext:asOtherIDs classCode="HLD">
						<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
						<ext:documentType code="1" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис обязательного медицинского страхования"/>
						<!-- Собственно номер и серия (если есть) и тип полиса -->
						<ext:documentNumber series="35" number="1234567890"/>
						<!-- Даты начала и окончания действия полиса -->
						<ext:effectiveTime value="20100214"/>
						<!-- Страховая компания, выдавшая полис -->
						<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
							<!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
							<ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
							<!-- Название страховой компании -->
							<ext:name>ЗАО "МАКС-М"</ext:name>
						</ext:scopingOrganization>
						<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
						<ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
					</ext:asOtherIDs>
					<!-- Полис ДМС -->
					<ext:asOtherIDs classCode="HLD">
						<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
						<ext:documentType code="2" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Полис добровольного медицинского страхования"/>
						<!-- Собственно номер и серия (если есть) и тип полиса -->
						<ext:documentNumber series="1111" number="0987654321"/>
						<!-- Даты начала и окончания действия полиса -->
						<ext:effectiveTime>
							<ext:low value="20130214"/>
							<ext:high value="20130813"/>
						</ext:effectiveTime>
						<!-- Страховая компания, выдавшая полис -->
						<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
							<!-- Идентификатор страховой компании, по справочнику в данном случае ФОМС -->
							<ext:id root="1.2.643.5.1.13.2.1.1.635" extension="77" assigningAuthorityName="ЗАО МАКС-М"/>
							<!-- Название страховой компании -->
							<ext:name>ЗАО "МАКС-М"</ext:name>
						</ext:scopingOrganization>
						<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
						<ext:InsuredTerritory code="7700000000000" codeSystem="1.2.643.5.1.13.2.1.1.196" codeSystemName="Классификатор адресов России" displayName="Москва"/>
					</ext:asOtherIDs>
					<!-- Другие идентификаторы пациента -->
					<!-- СНИЛС пациента -->
					<ext:asOtherIDs classCode="IDENT">
						<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
						<ext:documentType code="3" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Страховой номер индивидуального лицевого счёта"/>
						<!--<ext:documentNumber type="СНИЛС" number="000-000-000 00"/>-->
						<ext:documentNumber number="000-000-000 00"/>
						<ext:effectiveTime value="20100214"/>
					</ext:asOtherIDs>
					<!-- ИНН пациента -->
					<ext:asOtherIDs classCode="IDENT">
						<ext:templateId root="1.2.643.5.1.13.2.7.5.1.3" extension="POCD_MT000040_RU01_Extension.OtherIDs"/>
						<ext:documentType code="4" codeSystem="1.2.643.5.1.13.2.7.1.62" codeSystemName="Тип внешнего идентификатора" displayName="Индивидуальный номер налогоплательщика"/>
						<ext:documentNumber number="123456789101"/>
						<ext:effectiveTime value="20100214"/>
						<ext:scopingOrganization classCode="ORG" determinerCode="INSTANCE">
							<!-- Идентификатор организации -->
							<ext:id nullFlavor="NA"/>
						</ext:scopingOrganization>
						<!-- Код территории страхования по справочникам ОКАТО, ОКТМО, КЛАДР -->
						<ext:InsuredTerritory nullFlavor="NA"/>
					</ext:asOtherIDs>
					<ext:asUnidentified value="true"/>
				</ext:patient>
			</patient>
		</patientRole>
	</recordTarget>
	<!-- КОНЕЦ ДАННЫХ О ПАЦИЕНТЕ -->
	<!-- ДАННЫЕ ОБ АВТОРЕ ДОКУМЕНТА-->
	<!-- Шаблон: Медицинский работник - автор [1] -->
	<author typeCode="AUT">
		<!-- дата и время создания включенного объекта (дата и время компиляции) [1] -->
		<time value="20070217114723"/>
		<assignedAuthor classCode="ASSIGNED">
			<!-- код медицинского работника (врача) [1] -->
			<id root="1.2.643.5.1.13.3.25.77.761" extension="2341" assigningAuthorityName="Институт кардиохирургии им. В. И. Бураковского"/>
			<!-- Шаблон: Специальность [0..1] -->
			<ext:asLicencedEntity HL7-ClassName="LIC" HL7-Domain="PRPM_RM000000" realmCode="RU">
				<!-- код специальности и название -->
				<ext:code code="28" codeSystem="1.2.643.5.1.13.2.1.1.181" codeSystemName="Номенклатура специальностей специалистов с высшим и послевузовским медицинским и фармацевтическим образованием в сфере здравоохранения"  displayName="Травматология и ортопедия"/>
			</ext:asLicencedEntity>
			<!-- Код должности роли медицинского работника по справочнику ("1.2.643.5.1.13.2.1.1.89") Минздрава РФ -->
			<code code="90" codeSystem="1.2.643.5.1.13.2.1.1.607" codeSystemName="Номенклатура должностей медицинских работников и фармацевтических работников" displayName="Врач-хирург">
				<translation code="DOCOBS" codeSystem="1.2.643.5.1.13.2.7.1.30" codeSystemName="Роль в оказании медицинской помощи" displayName="Лечащий врач"/>
			</code>
			<telecom value="tel:+78442171311"/>
			<telecom value="mailto:a.privalov@oblhosp.volgograd.ru"/>
			<telecom value="fax:+78442171300"/>
			<!-- Фамилия, Имя, Отчество [1] -->
			<assignedPerson classCode="PSN" determinerCode="INSTANCE">
				<name>
					<!-- Фамилия -->
					<family>Привалов</family>
					<!-- Имя -->
					<given>Александр</given>
					<!-- Отчество -->
					<given>Иванович</given>
				</name>
			</assignedPerson>
			<!-- Шаблон: Медицинская организация [1] -->
			<representedOrganization classCode="ORG" determinerCode="INSTANCE">
				<!-- Код учреждения в реестре Минздрава РФ [1] -->
				<id root="1.2.643.5.1.13.3.25.77.761"/>
				<!-- Наименование учреждения [1] -->
				<name>Институт кардиохирургии им. В. И. Бураковского</name>
				<!-- Контактные данные [1..*] -->
				<telecom value="tel:+74952171300"/>
				<telecom value="mailto:info@oblhosp.mos.ru"/>
				<telecom value="fax:+74952171300"/>
				<!-- Адрес больницы [1] -->
				<addr use="PHYS">
					<!-- Страна -->
					<country>Российская Федерация</country>
					<!-- Область/Край  -->
					<state>Москва</state>
					<!-- Город -->
					<city>Москва</city>
					<!-- Улица -->
					<streetName>ул. Ангарская</streetName>
					<!-- Номер дома -->
					<houseNumber>22</houseNumber>
					<!-- Почтовый индекс -->
					<postalCode>104567</postalCode>
				</addr>
			</representedOrganization>
		</assignedAuthor>
	</author>
	<!-- КОНЕЦ ДАННЫХ ОБ АВТОРЕ -->
	<!-- ДАННЫЕ ОБ ОРГАНИЗАЦИИ-ВЛАДЕЛЬЦЕ ДОКУМЕНТА НАЧАЛО -->
	<!-- Шаблон: Владелец документа [1] -->
	<custodian typeCode="CST">
		<assignedCustodian>
			<representedCustodianOrganization>
				<!-- Код учреждения в реестре Минздрава РФ [1] -->
				<id root="1.2.643.5.1.13.3.25.77.761"/>
				<!-- Наименование учреждения [1] -->
				<name>Институт кардиохирургии им. В. И. Бураковского</name>
			</representedCustodianOrganization>
		</assignedCustodian>
	</custodian>
	<!-- КОНЕЦ ДАННЫХ ОБ ОРГАНИЗАЦИИ-ВЛАДЕЛЬЦЕ ДОКУМЕНТА -->
	<!-- ДАННЫЕ ОБ УТВЕРЖДАЮЩЕЙ ПОДПИСИ НАЧАЛО -->
	<!-- Лицо утвердившее документ (Заведующий отделением, председатель комиссиии т.п.) -->
	<!-- Шаблон: Утвердивший документ документа [0..1] -->
	<legalAuthenticator>
		<time value="20130722"/>
		<signatureCode code="S"/>
		<assignedEntity>
			<id root="1.2.643.5.1.13.3.25.77.761" extension="12345" assigningAuthorityName="Институт кардиохирургии им. В. И. Бураковского"/>
			<!-- Код должности роли медицинского работника по справочнику ("1.2.643.5.1.13.2.1.1.89") Минздрава РФ -->
			<code code="262" codeSystem="1.2.643.5.1.13.2.1.1.607" codeSystemName="Номенклатура должностей медицинских работников и фармацевтических работников" displayName="Заведующий отделением">
				<translation code="4" codeSystem="1.2.643.5.1.13.2.7.1.30" codeSystemName="Роль в оказании медицинской помощи" displayName="Заведующий отделением"/>
			</code>
			<assignedPerson>
				<name>
					<family>Кривонос</family>
					<!-- Имя -->
					<given>Владимир</given>
					<!-- Отчество -->
					<given>Владимирович</given>
				</name>
			</assignedPerson>
		</assignedEntity>
	</legalAuthenticator>
	<!-- ДАННЫЕ ОБ УТВЕРЖДАЮЩЕЙ ПОДПИСИ КОНЕЦ-->
	<!-- ДАННЫЕ О ЛИЦЕ, ПОДПИСАВШЕМ ДОКУМЕНТ НАЧАЛО-->
	<!-- Шаблон: Подписавший документ [1] -->
	<authenticator>
		<time value="20130722"/>
		<signatureCode code="S"/>
		<!-- Код врача в МО + наименование организации-->
		<assignedEntity>
			<id root="1.2.643.5.1.13.3.25.77.761" extension="2341"/>
			<!-- Код должности роли медицинского работника по справочнику ("1.2.643.5.1.13.2.1.1.89") Минздрава РФ -->
			<code code="90" codeSystem="1.2.643.5.1.13.2.1.1.607" codeSystemName="Номенклатура должностей медицинских работников и фармацевтических работников" displayName="Врач-хирург">
				<translation code="DOCOBS" codeSystem="1.2.643.5.1.13.2.7.1.30" codeSystemName="Роль в оказании медицинской помощи" displayName="Лечащий врач"/>
			</code>
			<telecom value="tel:+78442171311"/>
			<telecom value="mailto:a.privalov@oblhosp.volgograd.ru"/>
			<telecom value="fax:+78442171300"/>
			<assignedPerson>
				<name>
					<!-- Фамилия -->
					<family>Привалов</family>
					<!-- Имя -->
					<given>Александр</given>
					<!-- Отчество -->
					<given>Иванович</given>
				</name>
			</assignedPerson>
		</assignedEntity>
	</authenticator>
	<!-- КОНЕЦ ДАННЫХ О ЛИЦЕ, ПОДПИСАВШЕМ ДОКУМЕНТ-->
	<!-- ДАННЫЕ О КОНТАКТНЫХ ЛИЦАХ ПАЦИЕНТА НАЧАЛО-->
	<!-- Контактные лица пациента -->
	<participant typeCode="NOT">
		<associatedEntity classCode="PRS">
			<!-- Код контактного лица [0..1] -->
			<id nullFlavor="NI"/>
			<!-- Отношение к пациенту [1] -->
			<code code="3" codeSystem="1.2.643.5.1.13.2.7.1.15" codeSystemName="Отношение к пациенту" displayName="Другие родственники"/>
			<!-- Способ контакта [1..*] -->
			<telecom value="tel:+74954223456"/>
			<!-- Фамилия, Имя, Отчество (если есть) контактного лица [1] -->
			<associatedPerson>
				<name>
					<!-- Фамилия -->
					<family>Савенкова</family>
					<!-- Имя -->
					<given>Арина</given>
					<!-- Отчество -->
					<given>Сергеевна</given>
				</name>
			</associatedPerson>
		</associatedEntity>
	</participant>
	<!-- КОНЕЦ ДАННЫХ О КОНТАКТНЫХ ЛИЦАХ ПАЦИЕНТА -->
	<!-- ДАННЫЕ О НАПРАВЛЕНИИ НА ГОСПИТАЛИЗАЦИЯ НАЧАЛО-->
	<!-- Шаблон: Номер направления [0..1] -->
	<inFulfillmentOf typeCode="FLFS">
		<order classCode="ACT" moodCode="RQO">
			<!-- Номер направления [1] -->
			<id root="1.2.643.5.1.13.3.25.64.108" extension="101"/>
			<!-- Тип документа [1] -->
			<code code="3" codeSystem="1.2.643.5.1.13.2.1.1.1" codeSystemName="Система электронных медицинских документов" displayName="Направление на госпитализацию"/>
			<!-- Срочность госпитализации [1] -->
			<priorityCode code="4" codeSystem="1.2.643.5.1.13.2.1.1.115" codeSystemName="Классификатор признаков экстренности госпитализации" displayName="Плановая"/>
			<!-- Дата выдачи направления -->
			<ext:asOrderDate value="20130507"/>
		</order>
	</inFulfillmentOf>
	<!--КОНЕЦ О НАПРАВЛЕНИИ НА ГОСПИТАЛИЗАЦИЯ-->
	<!--ОБЩИЕ СВЕДЕНИЯ О ДОКУМЕНТЕ НАЧАЛО  -->
	<documentationOf>
		<serviceEvent classCode="PCPR">
			<templateId root="1.2.643.5.1.13.2.7.5.1.6.6"/>
			<effectiveTime>
				<!-- Дата начала госпитализации -->
				<low value="201305310815"/>
				<!-- Дата окончания госпитализации -->
				<high value="201306152320"/>
			</effectiveTime>
			<performer typeCode="PRF">
				<functionCode code="12" codeSystem="1.2.643.5.1.13.2.7.1.30" codeSystemName="Роль в оказании медицинской помощи" displayName="Лечащий врач"/>
				<assignedEntity>
					<!-- код медицинского работника (врача) [1] -->
					<id root="1.2.643.5.1.13.3.25.77.761" extension="2341"/>
					<!-- Код должности роли медицинского работника по справочнику ("1.2.643.5.1.13.2.1.1.89") Минздрава РФ -->
					<code code="91" codeSystem="1.2.643.5.1.13.2.1.1.607" codeSystemName="Номенклатура должностей медицинских работников и фармацевтических работников" displayName="врач-хирург"/>
					<assignedPerson>
						<name>
							<!-- Фамилия -->
							<family>Привалов</family>
							<!-- Имя -->
							<given>Александр</given>
							<!-- Отчество -->
							<given>Иванович</given>
						</name>
					</assignedPerson>
				</assignedEntity>
			</performer>
		</serviceEvent>
	</documentationOf>
	<!--КОНЕЦ ОБЩИХ СВЕДЕНИЙ О ДОКУМЕНТЕ  -->
	<!-- СВЕДЕНИЯ О ЗАМЕНЯЕМОМ ДОКУМЕНТЕ НАЧАЛО-->
	<relatedDocument typeCode="RPLC">
		<templateId root="1.2.643.5.1.13.2.7.5.1.6.7"/>
		<parentDocument>
			<id root="1.2.643.5.1.13.3.25.77.761" extension="111"/>
			<code code="1" codeSystem="1.2.643.5.1.13.2.1.1.1" codeSystemName="Система электронных медицинских документов" displayName="Эпикриз стационара"/>
			<setId root="1.2.643.5.1.13.3.25.77.761" extension="2013/321"/>
			<versionNumber value="1"/>
		</parentDocument>
	</relatedDocument>
	<!-- КОНЕЦ СВЕДЕНИЙ О ЗАМЕНЯЕМОМ ДОКУМЕНТЕ-->
	<!-- Шаблон: Случай оказания медицинской помощи [1] -->
	<componentOf>
		<encompassingEncounter>
			<!-- Номер истории болезни -->
			<!-- OID и номер истории болезни должны образовывать уникальную комбинацию в рамках всей системы -->
			<id root="1.2.643.5.1.13.3.25.77.761" extension="2013/531"/>
			<!-- Тип случая заболевания (госпитализация) -->
			<code code="STAT" codeSystem="1.2.643.5.1.13.2.7.1.1" codeSystemName="Вид случая заболевания" displayName="Госпитализация"/>
			<!-- Дата госпитализации -->
			<effectiveTime>
				<!-- Дата начала госпитализации -->
				<low value="20130531"/>
				<!-- Дата окончания госпитализации -->
				<high value="20130615"/>
			</effectiveTime>
			<!--Шаблон: Госпитализация стационар, дневной стационар [1] -->
			<ext:encounter HL7-ClassName="ENC" HL7-Domain="PRPA_RM000000" realmCode="RU">
				<!-- Кем доставлен [1] -->
				<ext:admissionReferralSourceCode code="12" codeSystem="1.2.643.5.1.13.2.1.1.110" codeSystemName="Классификатор каналов госпитализации" displayName="Самостоятельно"/>
				<!-- Общее количество койко-дней -->
				<ext:lengthOfStayQuantity value="16"/>
				<!-- Госпитализирован по поводу данного заболевания в текущем году [1] -->
				<ext:priorityCode code="1" codeSystem="1.2.643.5.1.13.2.1.1.109" codeSystemName="Классификатор количества госпитализаций" displayName="Госпитализирован впервые в данном году по диагнозу"/>
				<!-- Время доставки в стационар от начала заболевания [1] -->
				<ext:timeAfterBegining code="3" codeSystem="1.2.643.5.1.13.2.1.1.537" codeSystemName="Справочник доставки в стационар от начала заболевания" displayName="позднее 24-х часов"/>
				<ext:statusCode code="completed"/>
			</ext:encounter>
			<!-- Исход госпитализации [1] -->
			<dischargeDispositionCode code="5" codeSystem="1.2.643.5.1.13.2.1.1.123" codeSystemName="Классификатор исходов госпитализации" displayName="Умер"/>
			<!--Шаблон: Присутствовали [0..1] -->
			<encounterParticipant typeCode="REF">
				<assignedEntity>
					<!-- Код участника [1] -->
					<id root="1.2.643.5.1.13.3.25.77.761" extension="6543"/>
					<!-- Код должности и роли медицинского работника-->
					<code code="90" codeSystem="1.2.643.5.1.13.2.1.1.607" codeSystemName="Номенклатура должностей медицинских работников и фармацевтических работников" displayName="Врач-хирург">
						<translation code="17" codeSystem="1.2.643.5.1.13.2.7.1.30" codeSystemName="Роль в оказании медицинской помощи" displayName="Наблюдатель"/>
					</code>
					<!-- Код и название специальности -->
					<!--Шаблон: Специальность [1] -->
					<ext:asLicencedEntity HL7-ClassName="LIC" HL7-Domain="PRPM_RM000000" realmCode="RU">
						<ext:code code="28" codeSystem="1.2.643.5.1.13.2.1.1.181" codeSystemName="Номенклатура специальностей специалистов с высшим и послевузовским медицинским и фармацевтическим образованием в сфере здравоохранения"  displayName="Травматология и ортопедия"/>
					</ext:asLicencedEntity>
					<!-- Фамилия, Имя, Отчество (если есть) участника [1] -->
					<assignedPerson classCode="PSN" determinerCode="INSTANCE">
						<name>
							<!-- Фамилия -->
							<family>Кривцов</family>
							<!-- Имя -->
							<given>Александр</given>
							<!-- Отчество -->
							<given>Сергеевич</given>
						</name>
					</assignedPerson>
					<representedOrganization classCode="ORG" determinerCode="INSTANCE">
						<!-- Код организации-->
						<id root="1.2.643.5.1.13.3.25.77.761"/>
						<!-- Название организации [1] -->
						<name>Институт кардиохирургии им. В. И. Бураковского</name>
						<!-- Тип медицинской орагнизации -->
						<standardIndustryClassCode code="111052" codeSystem="1.2.643.5.1.13.2.1.1.77" codeSystemName="Тип медицинской организации" displayName="Центральная районная больница"/>
					</representedOrganization>
				</assignedEntity>
			</encounterParticipant>
		</encompassingEncounter>
	</componentOf>
	<component typeCode="COMP">
		<nonXMLBody>
			<text>
Находился(ась)на стац. лечении в ТРАВМАТОЛОГИЧЕСКОМ ОТДЕЛЕНИИ С 31.05.2013 по 15.06.2013.
Анализы на ВИЧ, HBS Ag, HCV Ab, RW отрицательные.
Страховой полис: серия 30, № 34879659 компания РОСНО (Москва),
 Диагноз при поступлении
M17.1 – Другой первичный гонартроз
Диагноз при выписке
M17.1 – Другой первичный гонартроз
Жалобы: Боль при ходьбе, отек области коленного сустава
Анамнез: Считает себя заболевшим с ноября 2012 года, когда после физической нагрузки почувствовал боль при разгибании колена
Состояние при поступлении: удовлетворительное.
Проведено лечение в соответствии с стандартом специализированной медицинской помощи при заболеваниях костно-мышечной системы
Проведено хирургическое лечение: 11-03-2013- Эндопротезирование ортопедическое коленного сустава
Эффект проведенной терапии: частичная регрессия.
Общее состояние по ВОЗ: 1 - Улучшение
Выписан(а):15.06.2013
Трудоспособность: утрачена временно.
Рекомендации:
•	Режим:
Общий
•	Диета:
Стол №0
•	Общие рекомендации:
Динамическое наблюдение лечащего врача, травматолога-ортопеда, врача-физиотерапевта, реабилитолога. Постепенное повышение нагрузки на сустав. Рентгенологический контроль при необходимости.

Листок нетрудоспособности при выписке сер. 07, N 0089076 с 31.05.2013 г. по 15.06.2013 г.

</text>
		</nonXMLBody>
	</component>
	<!-- СОДЕРЖАНИЕ КОНЕЦ -->
</ClinicalDocument>


'''


message = '''
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">

    <s:Body>
    <ProvideAndRegisterDocumentSetRequest xsi:schemaLocation="urn:ihe:iti:xds-b:2007 ../../schema/IHE/XDS.b_DocumentRepository.xsd" xmlns="urn:ihe:iti:xds-b:2007" xmlns:lcm="urn:oasis:names:tc:ebxml-regrep:xsd:lcm:3.0" xmlns:rim="urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <lcm:SubmitObjectsRequest>
        <rim:RegistryObjectList>
            <!--
                     STABLE ("urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1"),
                     ON_DEMAND ("urn:uuid:34268e47-fdf5-41a6-ba33-82133c465248");
             -->
            <rim:ExtrinsicObject id="Document01" mimeType="text/xml" objectType="urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1">

                <!-- Дата создания документа  -->
                <rim:Slot name="creationTime">
                    <rim:ValueList>
                        <rim:Value>20131218114723</rim:Value>
                    </rim:ValueList>
                </rim:Slot>

                <!-- Код языка документа  -->
                <rim:Slot name="languageCode">
                    <rim:ValueList>
                        <rim:Value>RU</rim:Value>
                    </rim:ValueList>
                </rim:Slot>

                <!--   Дата начала оказания услуги    -->
                <rim:Slot name="serviceStartTime">
                    <rim:ValueList>
                        <rim:Value>201305310815</rim:Value>
                    </rim:ValueList>
                </rim:Slot>

                <!--    Дата окончания оказания услуги  -->
                <rim:Slot name="serviceStopTime">
                    <rim:ValueList>
                        <rim:Value>201306152320</rim:Value>
                    </rim:ValueList>
                </rim:Slot>

                <!--    Субъект исследования документа
                9950710 - идентификатор пациента в МО;
                1.2.643.5.1.13.3.25.77.761 - OID МО.        -->
                <rim:Slot name="sourcePatientId">
                    <rim:ValueList>
                        <rim:Value>9950710^^^&amp;1.2.643.5.1.13.3.25.77.761&amp;ISO</rim:Value>
                    </rim:ValueList>
                </rim:Slot>


                <!--    Информация  по лицу, подписавшему документ
                    Тип данных XCN.
                    Обязательно наличие XCN.1 - идентификатор лица в МО
                    и XCN.2 (3, 4) -  ФИО
                -->
                <rim:Slot name="legalAuthenticator">
                    <rim:ValueList>
                        	<rim:Value>12345^Кривонос^Владимир^Владимирович</rim:Value>
                    </rim:ValueList>
                </rim:Slot>

      <!--       Информация по пациенту. Используется для протоколирования
                  и регистрации пациента в случае, если пациент в ИЭМК еще не зарегистрирован.
                     PID-3 - Список идентификаторов пациента, в формате CX (без ограничений). Нужно передавать как список
                     PID-5 - Имя пациента в формате XPN
                     PID-7 -  Дата рождения                -->

<!--                <rim:Slot name="sourcePatientInfo">-->
<!--                    <rim:ValueList>-->
                    <!-- СНИЛС-->
<!--                        <rim:Value>PID-3|66666666666^^^^1.2.643.100.3</rim:Value>   -->
<!--                        <rim:Value>PID-5|ТестоваяФамилияПациента^ТестовоеИмяПациента^ТестовоеОтчествоПациента^^</rim:Value>-->
<!--                        <rim:Value>PID-7|19560527</rim:Value>-->
<!--                        <rim:Value>PID-8|M</rim:Value>-->
<!--                    </rim:ValueList>-->
<!--                </rim:Slot>-->

                <!--
                   Номер медицинской карты пациента
                 -->
                <rim:Slot name="medicalRecordNumber">
                    <rim:ValueList>
                        <rim:Value>2013/8045</rim:Value>
                    </rim:ValueList>
                </rim:Slot>

                <!--        Основной диагноз пациента     -->
<!--                <rim:Slot name="primaryDiagnosis">-->
<!--                    <rim:ValueList>-->
<!--                        <rim:Value>M17.1</rim:Value>-->
<!--                    </rim:ValueList>-->
<!--                </rim:Slot>-->

                <!--     Заголовок документа     -->
                <rim:Name>
                    <rim:LocalizedString value="Эпикриз стационара №50"/>
                </rim:Name>

                <!--    Комментарий к документу  -->
                <rim:Description>
                    <rim:LocalizedString value="Комментарий к документу"/>
                </rim:Description>

                 <!--    Секция описания автора документа, определяется классификатором urn:uuid:93606bcf-9494-43ec-9b4e-a7748d1a838d
                 -->
                <rim:Classification id="cl01" classificationScheme="urn:uuid:93606bcf-9494-43ec-9b4e-a7748d1a838d" classifiedObject="Document01" nodeRepresentation="">

                   <!--  XCN тип. ФИО   -->

                    <rim:Slot name="authorPerson">
                        <rim:ValueList>
                            <rim:Value>00000000003^Привалов^Александр^Иванович</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>

                    <!-- Код медицинской организации. XON тип
                         Имя в 1-м элементе
                          6 - OID классификатора организации, назначившей код
                         10 - OID медицинского учреждения       -->


                    <rim:Slot name="authorInstitution">
                        <rim:ValueList>
                            <rim:Value>Институт кардиохирургии им. В. И. Бураковского^^^^^&amp;1.2.643.5.1.13.3.25.77.761&amp;ISO^^^^1.2.643.5.1.13.3.25.77.761</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>

                    <!--    Должность специалиста    -->
                    <rim:Slot name="authorRole">
                        <rim:ValueList>
                            <rim:Value>Врач-хирург</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>

                    <!--   Профиль специалиста, автора документа   -->
                    <rim:Slot name="authorSpecialty">
                        <rim:ValueList>
                            <rim:Value>Травматология и ортопедия</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                </rim:Classification>

                <!--
                   Секция описания типа СЭМД (classCode), определяется значением urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a
                -->
                <rim:Classification id="cl02" classificationScheme="urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a" classifiedObject="Document01" nodeRepresentation="1.2.643.5.1.13.2.7.5.1.1.1">
                    <!--    Схема кодирования классификаторов типов СЭМД
                      Должен быть 1.2.643.5.1.13.2.7.5.1           -->
                    <rim:Slot name="codingScheme">
                        <rim:ValueList>
                           <rim:Value>1.2.643.5.1.13.2.7.5.1</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>

                    <!--      Отображаемое значеие типа СЭМД ко классификатору 1.2.643.5.1.13.2.7.5.1       -->
                    <rim:Name>
                        <rim:LocalizedString value="Эпикриз стационара"/>
                    </rim:Name>
                </rim:Classification>

                <!-- Уровень конфиденциальности документа, определяется значением urn:uuid:f4f85eac-e6cb-4883-b524-f2705394840f
                -->
                <rim:Classification id="cl03" classificationScheme="urn:uuid:f4f85eac-e6cb-4883-b524-f2705394840f" classifiedObject="Document01" nodeRepresentation="N">

                    <!-- Схема кодирования уровня документа врача   -->
                    <rim:Slot name="codingScheme">
                        <rim:ValueList>
                              <rim:Value>1.2.643.5.1.13.2.7.1.10</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <!--  DisplayName уровня конфиденциальности   -->
                    <rim:Name>
                        <rim:LocalizedString value="Открыто"/>
                    </rim:Name>
                </rim:Classification>

                <rim:Classification id="cl03" classificationScheme="urn:uuid:f4f85eac-e6cb-4883-b524-f2705394840f" classifiedObject="Document01" nodeRepresentation="V">

                    <!-- Схема кодирования уровня документа для пациента     -->
                    <rim:Slot name="codingScheme">
                        <rim:ValueList>
                          <rim:Value>2.16.840.1.113883.5.25</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <!--   DisplayName уровня конфиденциальности     -->
                    <rim:Name>
                        <rim:LocalizedString value="Закрыто"/>
                    </rim:Name>
                </rim:Classification>

                <!--   Секция кода формата документа     -->
                <rim:Classification id="cl04" classificationScheme="urn:uuid:a09d5840-386c-46f2-b5ad-9c3699a4309d" classifiedObject="Document01" nodeRepresentation="application/hl7-cda-level-one+xml">
                    <rim:Slot name="codingScheme">
                        <rim:ValueList>
                            <rim:Value>1.2.643.5.1.13.2.7.1.40</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <rim:Name>
                         <rim:LocalizedString value="application/hl7-cda-level-one+xml"/>
                    </rim:Name>
                </rim:Classification>

                <!--    Вид медицинской организации. Опционально   -->
                <rim:Classification id="cl05" classificationScheme="urn:uuid:f33fb8ac-18af-42cc-ae0e-ed0b0bdb91e1" classifiedObject="Document01" nodeRepresentation="111052">
                    <rim:Slot name="codingScheme">
                        <rim:ValueList>
                            <rim:Value>1.2.643.5.1.13.2.1.1.77</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <rim:Name>
                        <rim:LocalizedString value="Центральная районная больница"/>
                    </rim:Name>
                </rim:Classification>


                <!-- Наименование отделения в МО. Опционально.
                    practiceSettingCode  -->

                <rim:Classification id="cl06" classificationScheme="urn:uuid:cccf5598-8b07-4b77-a05e-ae952c785ead" classifiedObject="Document01" nodeRepresentation="27">
                    <rim:Slot name="codingScheme">
                        <rim:ValueList>
                            <rim:Value>1.2.643.5.1.13.2.7.1.25</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <rim:Name>
                        <rim:LocalizedString value="Травматологическое отделение"/>
                    </rim:Name>
                </rim:Classification>

                <!--     Тип медицинского документа.  -->

                   <rim:Classification id="cl07" classificationScheme="urn:uuid:f0306f51-975f-434e-a61c-c59651d33983"
                                       classifiedObject="Document01" nodeRepresentation="POCD_MT000040_RU01">
                    <rim:Slot name="codingScheme">
                        <rim:ValueList>
                            <rim:Value>2.16.840.1.113883.1.3</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <rim:Name>
                        <rim:LocalizedString value="CDA R2"/>
                    </rim:Name>
                </rim:Classification>

                <!--   ID пациента в МО.
                        9950710 - идентификатор пациента в МО;
                       1.2.643.5.1.13.3.25.77.761 - OID МО  -->
                <rim:ExternalIdentifier id="ei01" registryObject="Document01" identificationScheme="urn:uuid:58a6f841-87b3-4a3e-92fd-a8ffeff98427" value="9950710^^^&amp;1.2.643.5.1.13.3.25.77.761&amp;ISO">
                    <rim:Name>
                        <rim:LocalizedString value="XDSDocumentEntry.patientId"/>
                    </rim:Name>
                </rim:ExternalIdentifier>

                <!--    Уникальный идентификатор документа в МИС   -->
                <rim:ExternalIdentifier id="ei02" registryObject="Document01" identificationScheme="urn:uuid:2e82c1f6-a085-4c72-9da3-8640a32e42ab" value="87654765-8788-7657-2238-83DA8EF7D2SS15">
                    <rim:Name>
                        <rim:LocalizedString value="XDSDocumentEntry.uniqueId"/>
                    </rim:Name>
                </rim:ExternalIdentifier>
            </rim:ExtrinsicObject>

   <!-- Секция описания набора документов -->
            <rim:RegistryPackage id="SubmissionSet01">
                <!-- Дата создания и отправки на регистрацию набора документов -->
                <rim:Slot name="submissionTime">
                    <rim:ValueList>
                        <rim:Value>201312181450</rim:Value>
                    </rim:ValueList>
                </rim:Slot>

                <!-- Наименовение набора документов -->
                <rim:Name>
                    <rim:LocalizedString value="Эпикриз стационара"/>
                </rim:Name>

                <!--  Комментарий к набору документов -->
                <rim:Description>
                    <rim:LocalizedString value="Эпикриз стационара комментарий"/>
                </rim:Description>
                <!-- Автор набора документов
                 Может быть другое лицо, отличное от авторов самих документов, входящих в набор..
                 Описание секции аналогично секции автора в документе выше.
                 -->
                <rim:Classification id="cl08" classificationScheme="urn:uuid:a7058bb9-b4e4-4307-ba5b-e3f0ab85e12d" classifiedObject="SubmissionSet01" nodeRepresentation="">
                    <rim:Slot name="authorPerson">
                        <rim:ValueList>
                            <rim:Value>00000000004^Привалов^Александр^Иванович</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>

                         <!-- Код МО по справочнику в реестре НСИ МЗ РФ: MDR308.
                                OID справочника: 1.2.643.5.1.13.2.1.1.178.
                                OID МО 1.2.643.5.1.13.3.25.77.761                             -->

                    <rim:Slot name="authorInstitution">
                        <rim:ValueList>
                            <rim:Value>Институт кардиохирургии им. В. И. Бураковского^^^^^&amp;1.2.643.5.1.13.2.1.1.178&amp;ISO^^^^1.2.643.5.1.13.3.25.77.761</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <rim:Slot name="authorRole">
                        <rim:ValueList>
                            <rim:Value>Врач-кардиолог</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                    <rim:Slot name="authorSpecialty">
                        <rim:ValueList>
                            <rim:Value>Кардиология</rim:Value>
                        </rim:ValueList>
                    </rim:Slot>
                </rim:Classification>

                <!--    Идентификатор документа в МИС   -->
                <rim:ExternalIdentifier id="ei03" registryObject="SubmissionSet01" identificationScheme="urn:uuid:96fdda7c-d067-4183-912e-bf5ee74998a8" value="7AA0B129-0CD0-23E0-2516-3AA4AB439C1SS15">
                    <rim:Name>
                        <rim:LocalizedString value="XDSSubmissionSet.uniqueId"/>
                    </rim:Name>
                </rim:ExternalIdentifier>

                <!-- Идентификатор системы-источника документов (в МИС) -->
                <rim:ExternalIdentifier id="ei04" registryObject="SubmissionSet01" identificationScheme="urn:uuid:554ac39e-e3fe-47fe-b233-965d2a147832" value="1.3.6.1.4.1.21367.2005.3.7">
                    <rim:Name>
                        <rim:LocalizedString value="XDSSubmissionSet.sourceId"/>
                    </rim:Name>
                </rim:ExternalIdentifier>

                <!-- ID пациента в МО
                       9950710 - идентификатор пациента в МО;
                       1.2.643.5.1.13.3.25.77.761 - OID МО.      -->

                <rim:ExternalIdentifier id="ei05" registryObject="SubmissionSet01" identificationScheme="urn:uuid:6b5aea1a-874d-4603-a4bc-96a0a7b38446" value="9950710^^^&amp;1.2.643.5.1.13.3.25.77.761&amp;ISO">
                    <rim:Name>
                        <rim:LocalizedString value="XDSSubmissionSet.patientId"/>
                    </rim:Name>
                </rim:ExternalIdentifier>

            </rim:RegistryPackage>

            <!-- Идентификатор urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd опеределяет что classifiedObject указанный тут относится к типу SubmitionSet -->
            <rim:Classification id="cl10" classifiedObject="SubmissionSet01" classificationNode="urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd"/>

            <!-- Описывает тип связи между набором документов и документом, в данном примере HasMember - документ Document01 входит в состав набора документов SubmissionSet01  -->
            <rim:Association id="as01" associationType="urn:oasis:names:tc:ebxml-regrep:AssociationType:HasMember" sourceObject="SubmissionSet01" targetObject="Document01">
                <rim:Slot name="SubmissionSetStatus">
                    <rim:ValueList>
                        <rim:Value>Original</rim:Value>
                    </rim:ValueList>
                </rim:Slot>
            </rim:Association>

        </rim:RegistryObjectList>
    </lcm:SubmitObjectsRequest>
    <!-- Сам СЭМД в формате base64binary  -->
	<Document id="Document01">PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiP…
             </Document>
</ProvideAndRegisterDocumentSetRequest>
</s:Body>
</s:Envelope>

'''