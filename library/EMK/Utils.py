# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

import library.LoggingModule.Logger
from library.LoggingModule.Logger import getLoggerDbName
from library.Utils import forceBool, forceDate, forceRef, forceString, forceStringEx, forceInt

CLIENT_STMT = u'''
SELECT
  Client.birthDate                  AS BirthDate,
  Client.lastName                   AS FamilyName,
  Client.firstName                  AS GivenName,
  Client.patrName                   AS MiddleName,
  Client.id                         AS IdPatientMIS,
  Client.sex                        AS Sex,
  rbBloodType.netrica_Code          AS IdBloodType
FROM Client Client
  LEFT JOIN rbBloodType ON Client.bloodType_id = rbBloodType.id
WHERE Client.deleted = 0 AND Client.id = %i;
'''


CLIENT_SOC_STATUS_STMT = u'''
SELECT
  rbSocStatusClass.netrica_Code    AS SocialGroup,
  rbSocStatusType.netrica_Code     AS SocialStatus
FROM Client Client
  INNER JOIN ClientSocStatus ON Client.id = ClientSocStatus.client_id
  INNER JOIN rbSocStatusType ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
  INNER JOIN rbSocStatusClass ON ClientSocStatus.socStatusClass_id = rbSocStatusClass.id
WHERE ClientSocStatus.deleted = 0 AND rbSocStatusClass.flatCode = 'socStatus' AND Client.id = %i
ORDER BY ClientSocStatus.id DESC LIMIT 0,1;
'''


CLIENT_PRIVILEGES_STMT = u'''
SELECT
  ClientSocStatus.begDate           AS DateStart,
  ClientSocStatus.endDate           AS DateEnd,
  rbSocStatusType.netrica_Code   AS IdPrivilegeType
FROM Client Client
  INNER JOIN ClientSocStatus ON Client.id = ClientSocStatus.client_id
  INNER JOIN rbSocStatusType ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
  INNER JOIN rbSocStatusClass ON ClientSocStatus.socStatusClass_id = rbSocStatusClass.id
WHERE ClientSocStatus.deleted = 0 AND rbSocStatusClass.flatCode = 'benefits'
      AND ClientSocStatus.begDate IS NOT NULL AND ClientSocStatus.endDate IS NOT NULL
      AND ClientSocStatus.begDate != '0000-00-00' AND ClientSocStatus.endDate != '0000-00-00'
      AND Client.id = %i;
'''


CLIENT_DOCUMENTS_STMT = u''' 
SELECT * FROM (
  SELECT
    rbDocumentType.netrica_Code AS IdDocumentType,
    ClientDocument.serial       AS DocS,
    ClientDocument.number       AS DocN,
    ClientDocument.endDate      AS ExpiredDate,
    ClientDocument.date         AS IssuedDate,
    ClientDocument.origin       AS ProviderName,
    NULL                        AS IdProvider
  FROM Client Client
    INNER JOIN ClientDocument ON Client.id = ClientDocument.client_id
    INNER JOIN rbDocumentType ON ClientDocument.documentType_id = rbDocumentType.id
  WHERE ClientDocument.deleted = 0 AND rbDocumentType.id IS NOT NULL
        AND Client.id = {clientId}

  UNION

  SELECT
    223          AS IdDocumentType,
    ''           AS DocS,
    Client.SNILS AS DocN,
    NULL         AS ExpiredDate,
    NULL         AS IssuedDate,
    'ПФР'        AS ProviderName,
    NULL         AS IdProvider
  FROM
    Client
  WHERE Client.SNILS != ''
        AND Client.id = {clientId}

  UNION

  SELECT
    *
  FROM
  (
    SELECT
      IFNULL(rbPolicyKind.netrica_Code, 240) AS IdDocumentType,
      ClientPolicy.serial                    AS DocS,
      ClientPolicy.number                    AS DocN,
      ClientPolicy.endDate                   AS ExpiredDate,
      ClientPolicy.begDate                   AS IssuedDate,
      Organisation.fullName                  AS ProviderName,
      Organisation.miacCode                  AS IdProvider
    FROM
      Client
      INNER JOIN ClientPolicy ON Client.id = ClientPolicy.client_id
      INNER JOIN rbPolicyKind ON ClientPolicy.policyKind_id = rbPolicyKind.id
      INNER JOIN Organisation ON ClientPolicy.insurer_id = Organisation.id
    WHERE
      ClientPolicy.deleted = 0
      AND Client.id = {clientId}
    ORDER BY
      IFNULL(ClientPolicy.begDate, '2000-01-01') DESC,
      IFNULL(ClientPolicy.endDate, '2200-01-01') DESC,
      ClientPolicy.id DESC
  ) AS cp
) t
  GROUP BY IdDocumentType
;
'''


CLIENT_ADDRESSES_STMT = u'''
SELECT
  ClientAddress.type + 1                AS IdAddressType, -- 0 у нас — 1 у нетрики. 1 у нас — 2 у нетрики
  formatClientAddress(ClientAddress.id) AS StringAddress
FROM Client Client
  INNER JOIN ClientAddress ON Client.id = ClientAddress.client_id
WHERE ClientAddress.deleted = 0 AND Client.id = %i;
'''


CLIENT_CONTACTS_STMT = u'''
SELECT
  rbContactType.netrica_Code         AS IdContactType,
  ClientContact.contact                 AS ContactValue
FROM Client Client
  INNER JOIN ClientContact ON Client.id = ClientContact.client_id
  INNER JOIN rbContactType ON ClientContact.contactType_id = rbContactType.id
WHERE ClientContact.deleted = 0 AND Client.id = %i;
'''


CLIENT_WORKS_STMT = u'''
SELECT
  IFNULL(WorkOrganisation.fullName, freeInput)      AS CompanyName,
  ClientWork.post                                   AS Position
FROM Client Client
  INNER JOIN ClientWork ON Client.id = ClientWork.client_id
  LEFT JOIN Organisation WorkOrganisation ON ClientWork.org_id = WorkOrganisation.id
WHERE ClientWork.deleted = 0 AND formatClientWork(ClientWork.id) != '' AND Client.id = %i;
'''


GUARD_STMT = u'''
SELECT
  Client.firstName                AS GivenName,
  Client.patrName                 AS MiddleName,
  Client.lastName                 AS FamilyName,
  Client.sex                      AS Sex,
  Client.birthDate                AS Birthdate,
  Client.id                       AS IdPersonMis,
  rbRelationType.netrica_Code  AS IdRelationType
FROM ClientRelation
  INNER JOIN Client ON ClientRelation.relative_id = Client.id
  INNER JOIN rbRelationType ON ClientRelation.relativeType_id = rbRelationType.id
WHERE Client.deleted = 0 AND ClientRelation.deleted = 0
      AND ClientRelation.client_id = %i
ORDER BY ClientRelation.id DESC;
'''


BASE_EVENT_STMT = u'''
SELECT
  Event.setDate                       AS OpenDate,
  Event.execDate                      AS CloseDate,
  Client.id                           AS HistoryNumber,
  Event.id                            AS IdCaseMis,
  rbMedicalAidType.netrica_Code       AS IdCaseAidType,
  if(ContractFinance.id IS NOT NULL,
     ContractFinance.netrica_Code,
     EventTypeFinance.netrica_Code)   AS IdPaymentType,
  1                                   AS Confidentiality,
  1                                   AS DoctorConfidentiality,
  1                                   AS CuratorConfidentiality,
  OrgStructure.netrica_Code           AS IdLpu,
  rbDiagnosticResult.netrica_Code     AS IdCaseResult,
  NULL                                AS Comment,
  Client.id                           AS IdPatientMis,

  DoctorSpeciality.netrica_Code       AS IdSpeciality,
  DoctorPost.netrica_Code             AS IdPosition,
  Doctor.sex                          AS Sex,
  Doctor.birthDate                    AS BirthDate,
  Doctor.id                           AS IdPersonMis,
  Doctor.lastName                     AS FamilyName,
  Doctor.firstName                    AS GivenName,
  Doctor.patrName                     AS MiddleName,
  Doctor.orgStructure_id              AS LPU,
  Doctor.SNILS                        AS SNILS,

  (EventType.form IN ('003', '030') AND 
  ((rbEventProfile.code IS NULL) OR
   (rbEventProfile.code NOT IN ('111', '112')))) AS isStat,
  Event.hospParent                    AS isHospWithParent

FROM
  Event
  INNER JOIN Client ON Event.client_id = Client.id
  LEFT JOIN Diagnostic ON Diagnostic.id = (
    SELECT DC.id
    FROM 
      Diagnostic DC
      INNER JOIN Diagnosis DS ON DS.id = DC.diagnosis_id
      INNER JOIN rbDiagnosisType DT ON DC.diagnosisType_id = DT.id
    WHERE 
      DC.deleted = 0 AND DS.deleted = 0 AND DT.code IN ('1', '2') AND DC.event_id = Event.id
    ORDER BY 
      DS.MKB = '', DT.code = '2', DS.id 
    LIMIT 1
  )
  LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id = Diagnostic.result_id
  INNER JOIN EventType ON Event.eventType_id = EventType.id
  LEFT JOIN rbEventTypePurpose AS EventPurpose ON EventType.purpose_id = EventPurpose.id
  LEFT JOIN rbEventProfile ON rbEventProfile.id = EventType.eventProfile_id
  INNER JOIN Person AS Doctor ON Event.execPerson_id = Doctor.id
  LEFT JOIN rbSpeciality AS DoctorSpeciality ON Doctor.speciality_id = DoctorSpeciality.id
  LEFT JOIN rbPost AS DoctorPost ON Doctor.post_id = DoctorPost.id
  LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
  LEFT JOIN Contract ON Contract.id = Event.contract_id
  LEFT JOIN rbFinance EventTypeFinance ON EventTypeFinance.id = EventType.finance_id
  LEFT JOIN rbFinance ContractFinance ON ContractFinance.id = Contract.finance_id 
  LEFT JOIN OrgStructure ON Doctor.orgStructure_id = OrgStructure.id
  LEFT JOIN Organisation ON OrgStructure.organisation_id = Organisation.id
WHERE Event.deleted = 0 AND Event.id = %i;
'''


STAT_EVENT_STMT = u'''
SELECT
  Event.id,
  IF(Event.isPrimary = 1, 1, 2)           AS IdRepetition,
  IF(Event.`order` = 1, 1, 2)             AS HospitalizationOrder,
  rbResult.netrica_Code                   AS HospResult
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN rbResult ON Event.result_id = rbResult.id
WHERE Event.deleted = 0 AND Event.id = %i;
'''


EVENT_DELIVERY_STMT = u'''
SELECT
  Event.id,
  Delivery.value                          AS DeliveryCode
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType DeliveryType ON ReceivedActionType.id = DeliveryType.actionType_id AND DeliveryType.name = '№ бригады'
  LEFT JOIN ActionProperty DeliveryProperty ON DeliveryType.id = DeliveryProperty.type_id AND DeliveryProperty.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_Integer Delivery ON DeliveryProperty.id = Delivery.id
WHERE Event.deleted = 0 AND DeliveryType.deleted = 0 AND DeliveryProperty.deleted = 0 AND Event.id = %i;
'''


EVENT_INTOXICATION_STMT = u'''
SELECT
  Event.id,
  netricaIntoxicationType.code            AS IdIntoxicationType
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType IntoxicationType ON ReceivedActionType.id = IntoxicationType.actionType_id AND IntoxicationType.name = 'Доставлен в состоянии опьянения'
  LEFT JOIN ActionProperty IntoxicationProperty ON IntoxicationType.id = IntoxicationProperty.type_id AND IntoxicationProperty.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_Reference IntoxicationRef ON IntoxicationProperty.id = IntoxicationRef.id
  LEFT JOIN netricaIntoxicationType ON IntoxicationRef.value = netricaIntoxicationType.id
WHERE Event.deleted = 0 AND IntoxicationType.deleted = 0 AND IntoxicationProperty.deleted = 0 AND Event.id = %i;
'''


EVENT_ADMISSION_STMT = u'''
SELECT
  Event.id,
  netricaPatientConditionOnAdmission.code AS IdPatientConditionOnAdmission
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType ConditionType ON ReceivedActionType.id = ConditionType.actionType_id AND ConditionType.name = 'состояние при поступлении'
  LEFT JOIN ActionProperty ConditionProperty ON ConditionType.id = ConditionProperty.type_id AND ConditionProperty.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_Reference ConditionReference ON ConditionProperty.id = ConditionReference.id
  LEFT JOIN netricaPatientConditionOnAdmission ON ConditionReference.value = netricaPatientConditionOnAdmission.id
WHERE Event.deleted = 0 AND ConditionType.deleted = 0 AND ConditionProperty.deleted = 0 AND Event.id = %i;
'''


EVENT_DISEASE_STMT = u'''
SELECT
  Event.id,
  netricaTypeFromDiseaseStart.code        AS IdTypeFromDiseaseStart
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType DiseaseType ON ReceivedActionType.id = DiseaseType.actionType_id AND DiseaseType.name = 'Доставлен'
  LEFT JOIN ActionProperty DiseaseProperty ON DiseaseType.id = DiseaseProperty.type_id AND DiseaseProperty.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_Reference DiseaseReference ON DiseaseProperty.id = DiseaseReference.id
  LEFT JOIN netricaTypeFromDiseaseStart ON DiseaseReference.value = netricaTypeFromDiseaseStart.id
WHERE Event.deleted = 0 AND DiseaseType.deleted = 0 AND DiseaseProperty.deleted = 0 AND Event.id = %i;
'''


EVENT_TRANSPORT_STMT = u'''
SELECT
  Event.id,
  netricaTransportIntern.code             AS IdTransportIntern
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType TransportType ON ReceivedActionType.id = TransportType.actionType_id AND TransportType.name = 'Траспортировка'
  LEFT JOIN ActionProperty TransportProperty ON TransportType.id = TransportProperty.type_id AND TransportProperty.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_Reference TransportReference ON TransportProperty.id = TransportReference.id
  LEFT JOIN netricaTransportIntern ON TransportReference.value = netricaTransportIntern.id
WHERE Event.deleted = 0 AND TransportType.deleted = 0 AND TransportProperty.deleted = 0 AND Event.id = %i;
'''


EVENT_CHANNEL_STMT = u'''
SELECT
  Event.id,
  netricaHospChannel.code                 AS IdHospChannel
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType ChannelType ON ReceivedActionType.id = ChannelType.actionType_id AND ChannelType.name = 'Канал доставки'
  LEFT JOIN ActionProperty ChannelProperty ON ChannelType.id = ChannelProperty.type_id AND ChannelProperty.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_Reference ChannelReference ON ChannelProperty.id = ChannelReference.id
  LEFT JOIN netricaHospChannel ON ChannelReference.value = netricaHospChannel.id
WHERE Event.deleted = 0 AND ChannelType.deleted = 0 AND ChannelProperty.deleted = 0 AND Event.id = %i;
'''


EVENT_RW1_STMT = u'''
SELECT
  Event.id,
  RW1.value                               AS RW1Mark
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType RW1Type ON ReceivedActionType.id = RW1Type.actionType_id AND RW1Type.name = 'RW1'
  LEFT JOIN ActionProperty RW1Property ON RW1Type.id = RW1Property.type_id AND RW1Property.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_String RW1 ON RW1Property.id = RW1.id
WHERE Event.deleted = 0 AND RW1Type.deleted = 0 AND RW1Property.deleted = 0 AND Event.id = %i;
'''


EVENT_AIDS_STMT = u'''
SELECT
  Event.id,
  AIDS.value                              AS AIDSMark
FROM Event
  INNER JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  INNER JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  INNER JOIN ActionPropertyType AIDSType ON ReceivedActionType.id = AIDSType.actionType_id AND AIDSType.name = 'AIDS'
  LEFT JOIN ActionProperty AIDSProperty ON AIDSType.id = AIDSProperty.type_id AND AIDSProperty.action_id = ReceivedAction.id
  LEFT JOIN ActionProperty_String AIDS ON AIDSProperty.id = AIDS.id
WHERE Event.deleted = 0 AND AIDSType.deleted = 0 AND AIDSProperty.deleted = 0 AND Event.id = %i;
'''


AMB_EVENT_STMT = u'''
SELECT
  EventType.netrica_Code                 AS IdCasePurpose,
  IF(rbEventKind.id IS NULL, 2, 4)          AS IdCaseType,
  rbResult.netrica_Code                  AS IdAmbResult,
  TRUE                                      AS IsActive
FROM Event
  INNER JOIN EventType ON Event.eventType_id = EventType.id
  LEFT JOIN rbEventKind ON EventType.eventKind_id = rbEventKind.id
  INNER JOIN rbResult ON Event.result_id = rbResult.id
WHERE Event.deleted = 0
AND Event.id = %i;
'''


STAT_STEPS_STMT = u'''
SELECT
  Moving.begDate                                                            AS DateStart,
  Moving.endDate                                                            AS DateEnd,
  IFNULL(MovingFinance.netrica_Code, EventFinance.netrica_Code)             AS IdPaymentType,
  Moving.id                                                                 AS IdStepMis,
  OrgStructure.name                                                         AS HospitalDepartmentName,
  OrgStructure.infisCode                                                    AS IdHospitalDepartment,
  rbMedicalAidType.netrica_Code                                             AS IdRegimen,
  OrgStructure_HospitalBed.ward                                             AS WardNumber,
  OrgStructure_HospitalBed.name                                             AS BedNumber,
  rbHospitalBedProfile.netrica_Code                                         AS BedProfile,
  DATEDIFF(Moving.endDate, Moving.begDate)                                  AS DaySpend,

  rbSpeciality.netrica_Code                                                         AS IdSpeciality,
  rbPost.netrica_Code                                                               AS IdPosition,
  Doctor.sex                                                                AS Sex,
  Doctor.birthDate                                                          AS BirthDate,
  Doctor.id                                                                 AS IdPersonMis,
  Doctor.lastName                                                           AS FamilyName,
  Doctor.firstName                                                          AS GivenName,
  Doctor.patrName                                                           AS MiddleName,
  Doctor.orgStructure_id                                                    AS LPU,
  Doctor.SNILS                                                              AS SNILS,
  OrgStructure.netrica_Code                                                 AS IdLpu
FROM Event
  INNER JOIN EventType ON Event.eventType_id = EventType.id
  INNER JOIN Action Moving ON Event.id = Moving.event_id
  INNER JOIN ActionType ON Moving.actionType_id = ActionType.id
  LEFT JOIN rbFinance MovingFinance ON Moving.finance_id = MovingFinance.id
  LEFT JOIN rbFinance EventFinance ON EventType.finance_id = EventFinance.id
  INNER JOIN Person Doctor ON Moving.person_id = Doctor.id
  LEFT JOIN rbSpeciality ON Doctor.speciality_id = rbSpeciality.id
  LEFT JOIN rbPost ON Doctor.post_id = rbPost.id
  LEFT JOIN OrgStructure DoctorOS ON Doctor.orgStructure_id = DoctorOS.id
  LEFT JOIN Organisation ON DoctorOS.organisation_id = Organisation.id

  INNER JOIN ActionPropertyType HospDepartPT ON ActionType.id = HospDepartPT.actionType_id AND HospDepartPT.name = 'Отделение пребывания'
  INNER JOIN ActionProperty HospDepartAP ON Moving.id = HospDepartAP.action_id AND HospDepartPT.id = HospDepartAP.type_id
  INNER JOIN ActionProperty_OrgStructure ON HospDepartAP.id = ActionProperty_OrgStructure.id
  INNER JOIN OrgStructure ON ActionProperty_OrgStructure.value = OrgStructure.id

  LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id

  INNER JOIN ActionPropertyType BedPT ON ActionType.id = BedPT.actionType_id AND BedPT.name = 'койка'
  INNER JOIN ActionProperty BedAP ON Moving.id = BedAP.action_id AND BedPT.id = BedAP.type_id
  INNER JOIN ActionProperty_HospitalBed ON BedAP.id = ActionProperty_HospitalBed.id
  INNER JOIN OrgStructure_HospitalBed ON ActionProperty_HospitalBed.value = OrgStructure_HospitalBed.id
  INNER JOIN rbHospitalBedProfile ON OrgStructure_HospitalBed.profile_id = rbHospitalBedProfile.id
WHERE Event.deleted = 0 AND Moving.deleted = 0 AND ActionType.flatCode = 'moving'
AND Event.id = %i;
'''


ACTION_AMB_STEPS_STMT = u'''
SELECT
  Action.begDate                                                AS DateStart,
  Action.endDate                                                AS DateEnd,
  IFNULL(ActionFinance.netrica_Code, EventFinance.netrica_Code) AS IdPaymentType,
  Action.id                                                     AS IdStepMis,
  rbScene.netrica_Code                                          AS IdVisitPlace,
  rbEventGoal.netrica_Code                                      AS IdVisitPurpose,
  rbSpeciality.netrica_Code                                     AS IdSpeciality,
  rbPost.netrica_Code                                           AS IdPosition,
  Doctor.sex                                                    AS Sex,
  Doctor.birthDate                                              AS BirthDate,
  Doctor.id                                                     AS IdPersonMis,
  Doctor.lastName                                               AS FamilyName,
  Doctor.firstName                                              AS GivenName,
  Doctor.patrName                                               AS MiddleName,
  Doctor.orgStructure_id                                        AS LPU,
  Doctor.SNILS                                                  AS SNILS,
  DoctorOS.netrica_Code                                         AS IdLpu
FROM Event
  INNER JOIN EventType ON Event.eventType_id = EventType.id
  INNER JOIN Action ON Event.id = Action.event_id
  INNER JOIN ActionType ON Action.actionType_id = ActionType.id
  LEFT JOIN ActionType_Service ON ActionType.id = ActionType_Service.master_id
  LEFT JOIN rbService ON ActionType_Service.service_id = rbService.id
  LEFT JOIN rbFinance ActionFinance ON Action.finance_id = ActionFinance.id
  LEFT JOIN rbFinance EventFinance ON EventType.finance_id = EventFinance.id
  LEFT JOIN rbScene ON EventType.scene_id = rbScene.id
  LEFT JOIN rbEventGoal ON Event.goal_id = rbEventGoal.id

  INNER JOIN Person Doctor ON Action.person_id = Doctor.id
  LEFT JOIN rbSpeciality ON Doctor.speciality_id = rbSpeciality.id
  LEFT JOIN rbPost ON Doctor.post_id = rbPost.id
  LEFT JOIN OrgStructure DoctorOS ON Doctor.orgStructure_id = DoctorOS.id
  LEFT JOIN Organisation ON DoctorOS.organisation_id = Organisation.id
WHERE Event.deleted = 0 AND rbService.category_id IN (3,4,5,6,7,8) AND Action.deleted = 0
  AND Event.id = %i;
'''


VISIT_AMB_STEPS_STMT = u'''
SELECT
  Visit.id                                                     AS visitId,
  Visit.date                                                   AS DateStart,
  Visit.date                                                   AS DateEnd,
  IFNULL(VisitFinance.netrica_Code, EventFinance.netrica_Code) AS IdPaymentType,
  Visit.id                                                     AS IdStepMis,
  rbScene.netrica_Code                                         AS IdVisitPlace,
  rbEventGoal.netrica_Code                                     AS IdVisitPurpose,
  rbSpeciality.netrica_Code                                    AS IdSpeciality,
  rbPost.netrica_Code                                          AS IdPosition,
  Doctor.sex                                                   AS Sex,
  Doctor.birthDate                                             AS BirthDate,
  Doctor.id                                                    AS IdPersonMis,
  Doctor.lastName                                              AS FamilyName,
  Doctor.firstName                                             AS GivenName,
  Doctor.patrName                                              AS MiddleName,
  Doctor.orgStructure_id                                       AS LPU,
  Doctor.SNILS                                                 AS SNILS,
  DoctorOS.netrica_Code                                        AS IdLpu
FROM Event
  INNER JOIN EventType ON Event.eventType_id = EventType.id
  INNER JOIN Visit ON Event.id = Visit.event_id
  LEFT JOIN rbFinance VisitFinance ON Visit.finance_id = VisitFinance.id
  LEFT JOIN rbFinance EventFinance ON EventType.finance_id = EventFinance.id
  LEFT JOIN rbScene ON Visit.scene_id = rbScene.id
  LEFT JOIN rbEventGoal ON Event.goal_id = rbEventGoal.id

  INNER JOIN Person Doctor ON Visit.person_id = Doctor.id
  LEFT JOIN rbSpeciality ON Doctor.speciality_id = rbSpeciality.id
  LEFT JOIN rbPost ON Doctor.post_id = rbPost.id
  LEFT JOIN OrgStructure DoctorOS ON Doctor.orgStructure_id = DoctorOS.id
  LEFT JOIN Organisation ON DoctorOS.organisation_id = Organisation.id
WHERE Event.deleted = 0 AND Visit.deleted = 0
   AND Event.id = %i;
'''


MAIN_DIAGNOSIS_STMT = u'''
SELECT
  Diagnostic.setDate              AS DiagnosedDate,
  1                               AS IdDiagnosisType,
  Diagnosis.MKB                   AS MkbCode,
  rbDiseaseCharacter.netrica_Code AS IdDiseaseType,
  3                               AS DiagnosisStage,
  rbDispanser.netrica_Code        AS IdDispensaryState,
  DoctorSpeciality.netrica_Code   AS IdSpeciality,
  DoctorPost.netrica_Code         AS IdPosition,
  Doctor.sex                      AS Sex,
  Doctor.birthDate                AS BirthDate,
  Doctor.id                       AS IdPersonMis,
  Doctor.lastName                 AS FamilyName,
  Doctor.firstName                AS GivenName,
  Doctor.patrName                 AS MiddleName,
  Doctor.orgStructure_id          AS LPU,
  Doctor.SNILS                    AS SNILS,
  DoctorOrgStructure.netrica_Code AS IdLpu
FROM Event
  INNER JOIN Diagnostic ON Event.id = Diagnostic.event_id
  INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id
  INNER JOIN Person AS Doctor ON Diagnostic.person_id = Doctor.id
  LEFT JOIN rbSpeciality AS DoctorSpeciality ON Doctor.speciality_id = DoctorSpeciality.id
  LEFT JOIN rbPost AS DoctorPost ON Doctor.post_id = DoctorPost.id
  LEFT JOIN OrgStructure AS DoctorOrgStructure ON DoctorOrgStructure.id = Doctor.orgStructure_id
  INNER JOIN rbDiagnosisType ON Diagnosis.diagnosisType_id = rbDiagnosisType.id
  LEFT JOIN rbDiseaseCharacter ON Diagnosis.character_id = rbDiseaseCharacter.id
  LEFT JOIN rbDispanser ON Diagnosis.dispanser_id = rbDispanser.id
WHERE ( rbDiagnosisType.code = 2 OR
        rbDiagnosisType.code = 1 OR
        rbDiagnosisType.code = 97 OR
        rbDiagnosisType.code = 98 OR
        rbDiagnosisType.code = 99 OR
        rbDiagnosisType.code = 90) AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0
      AND Event.id = %i;
'''


MED_DOCUMENT_STMT = u'''
SELECT
  NOW()                           AS CreationDate,
  Event.id                        AS IdDocumentMis,
  DoctorSpeciality.netrica_Code   AS IdSpeciality,
  DoctorPost.netrica_Code         AS IdPosition,
  Doctor.sex                      AS Sex,
  Doctor.birthDate                AS BirthDate,
  Doctor.id                       AS IdPersonMis,
  Doctor.lastName                 AS FamilyName,
  Doctor.firstName                AS GivenName,
  Doctor.patrName                 AS MiddleName,
  Doctor.orgStructure_id          AS LPU,
  Doctor.SNILS                    AS SNILS,
  DoctorOrgStructure.netrica_Code AS IdLpu
FROM Event
  INNER JOIN Person AS Doctor ON Event.execPerson_id = Doctor.id
  LEFT JOIN rbSpeciality AS DoctorSpeciality ON Doctor.speciality_id = DoctorSpeciality.id
  LEFT JOIN rbPost AS DoctorPost ON Doctor.post_id = DoctorPost.id
  LEFT JOIN OrgStructure AS DoctorOrgStructure ON DoctorOrgStructure.id = Doctor.orgStructure_id
WHERE Event.deleted = 0 AND Event.id = %i;
'''


MED_DOCUMENT_PRINT_TEMPLATE_STMT = u'''
SELECT rbPrintTemplate.id
FROM rbPrintTemplate
  INNER JOIN rbIEMKDocument ON rbPrintTemplate.documentType_id = rbIEMKDocument.id
WHERE rbIEMKDocument.code = '%s' AND rbPrintTemplate.deleted = 0
'''


ERR_DUPLICATE_CLIENT = '23'


def getTempInvalidRecord(db, eventId):
    tableEvent = db.table('Event')
    tableTempInvalid = db.table('TempInvalid')

    table = tableEvent
    table = table.innerJoin(tableTempInvalid, tableTempInvalid['client_id'].eq(tableEvent['client_id']))
    cols = [
        tableTempInvalid['number'],
        tableTempInvalid['begDate'],
        tableTempInvalid['endDate']
    ]
    cond = [
        tableEvent['id'].eq(eventId),
        tableTempInvalid['deleted'].eq(0),
        tableTempInvalid['closed'].eq(0),
        tableTempInvalid['type'].eq(0),  # ВУТ

        # date conditions from Events/TempInvalid.py
        db.joinOr([
            tableEvent['execDate'].isNull(),
            db.joinAnd([
                tableTempInvalid['begDate'].dateLe(tableEvent['execDate']),
                db.joinOr([
                    tableTempInvalid['endDate'].isNull(),
                    tableTempInvalid['endDate'].dateGe(tableEvent['setDate'])
                ])
            ])
        ]),

        db.joinOr([
            tableEvent['setDate'].isNull(),
            tableTempInvalid['endDate'].isNull(),
            tableTempInvalid['endDate'].dageGe(tableEvent['setDate'])
        ])
    ]
    order = [
        tableTempInvalid['endDate'].desc()
    ]
    return db.getRecordEx(table, cols, cond, order)


def getDispensaryOneRecommendationRecords(db, eventId):
    RecommendationFlatCode = 'recommendation'

    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableIEMKDocument = db.table('rbIEMKDocument')
    tablePrintTemplate = db.table('rbPrintTemplate')

    table = tableAction
    table = table.innerJoin(tableActionType, [tableActionType['id'].eq(tableAction['actionType_id']),
                                              tableActionType['deleted'].eq(0)])
    table = table.innerJoin(tablePrintTemplate, [tablePrintTemplate['context'].eq(tableActionType['context']),
                                                 tablePrintTemplate['deleted'].eq(0)])
    table = table.innerJoin(tableIEMKDocument, [tableIEMKDocument['id'].eq(tablePrintTemplate['documentType_id']),
                                                tableIEMKDocument['code'].eq('DispensaryOne')])
    cols = [
        tableAction['id'],
        tableAction['endDate'],
        tableAction['person_id'],
        tablePrintTemplate['id'].alias('templateId')
    ]
    cond = [
        tableAction['event_id'].eq(eventId),
        tableAction['deleted'].eq(0),
        tableActionType['flatCode'].eq(RecommendationFlatCode)
    ]
    group = [
        tableAction['id']
    ]
    return db.getRecordList(table, cols, cond, group=group)


class HealthGroupMap(object):
    resultCodeMap = {}  # rbResult.regionalCode -> health group [1..5]

    groupNameMap = {
        u'I'  : 1,
        u'II' : 2,
        u'III': 3,
        u'IV' : 4,
        u'V'  : 5
    }

    @classmethod
    def extractGroup(cls, name):
        for group in (u'IV', u'V', u'III', u'II', u'I'):
            if group in name:
                return cls.groupNameMap[group]
        return 0

    @classmethod
    def get(cls, resultCode):
        if resultCode not in cls.resultCodeMap:
            resultName = forceString(QtGui.qApp.db.translate('rbResult', 'regionalCode', resultCode, 'name'))
            cls.resultCodeMap[resultCode] = cls.extractGroup(resultName)
        return cls.resultCodeMap[resultCode]


def getDispensaryOneInfo(db, eventId):
    DipensaryOneEventTypeCode = '211'
    SecondStageResultCodes = ['353', '357', '358']
    HealthGroupResultList = [
        '317', '318', '321', '322', '323', '324', '325', '332', '333', '334', '335', '336', '337', '338', '339',
        '340', '341', '343', '344', '345', '347', '348', '349', '350', '351', '353', '355', '356', '357', '358'
    ]

    tableDiagnosis = db.table('Diagnosis')
    tableDiagnostic = db.table('Diagnostic')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableResult = db.table('rbResult')

    table = tableEvent
    table = table.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    table = table.innerJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    table = table.innerJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                              tableDiagnostic['deleted'].eq(0)])
    table = table.innerJoin(tableDiagnosis, [tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']),
                                             tableDiagnosis['deleted'].eq(0)])
    cols = [
        tableResult['regionalCode'].alias('resultCode'),
        tableEvent['dispByMobileTeam'],
        tableEvent['execDate'],
        tableDiagnostic['hospital'],
        tableDiagnostic['sanatorium'],
        tableDiagnosis['dispanser_id']
    ]
    cond = [
        tableEvent['id'].eq(eventId),
        tableEventType['code'].eq(DipensaryOneEventTypeCode)
    ]

    recordList = db.getRecordList(table, cols, cond)
    if not recordList:
        return {}

    result = {
        'IsGuested'               : False,
        'IsUnderObservation'      : False,
        'HasExtraResearchRefferal': False,
        'HasExpertCareRefferal'   : False,
        'HasPrescribeCure'        : False,
        'HasHealthResortRefferal' : False,
        'HasSecondStageRefferal'  : False,
        'IdHealthGroup'           : 0,
        'Date'                    : QtCore.QDate.currentDate()
    }

    for rec in recordList:
        dispByMobileTeam = forceBool(rec.value('dispByMobileTeam'))
        dispanserId = forceRef(rec.value('dispanser_id'))
        hospital = forceBool(rec.value('hospital'))
        sanatorium = forceBool(rec.value('sanatorium'))
        resultCode = forceString(rec.value('resultCode'))
        execDate = forceDate(rec.value('execDate'))

        if dispByMobileTeam:
            result['IsGuested'] = True
        if dispanserId is not None:
            result['IsUnderObservation'] = True
        if hospital:
            result['HasExpertCareRefferal'] = True
        if sanatorium:
            result['HasHealthResortRefferal'] = True
        if resultCode in SecondStageResultCodes:
            result['HasSecondStageRefferal'] = True
        if resultCode in HealthGroupResultList:
            result['IdHealthGroup'] = HealthGroupMap.get(resultCode)
            result['Date'] = execDate

    return result


def getMedicalStaffRecord(db, personId):
    tableOrgStructure = db.table('OrgStructure')
    tablePerson = db.table('Person')
    tablePost = db.table('rbPost')
    tableSpeciality = db.table('rbSpeciality')

    table = tablePerson
    table = table.leftJoin(tablePost, tablePost['id'].eq(tablePerson['post_id']))
    table = table.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
    table = table.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))

    cols = [
        tablePerson['lastName'].alias('FamilyName'),
        tablePerson['firstName'].alias('GivenName'),
        tablePerson['patrName'].alias('MiddleName'),
        tablePerson['sex'].alias('Sex'),
        tablePerson['birthDate'].alias('Birthdate'),
        tablePerson['SNILS'].alias('SNILS'),
        tablePerson['id'].alias('IdPersonMis'),
        tablePost['netrica_Code'].alias('IdPosition'),
        tableSpeciality['netrica_Code'].alias('IdSpeciality'),
        tableOrgStructure['netrica_Code'].alias('IdLpu')
    ]
    cond = [
        tablePerson['id'].eq(personId)
    ]
    return db.getRecordEx(table, cols, cond)


def getReferralRecord(db, eventId):
    tableMKBTree = db.table('MKB_Tree')
    tableReferral = db.table('Referral')
    tableOrganisation = db.table('Organisation')

    table = tableReferral
    table = table.innerJoin(tableOrganisation, tableOrganisation['id'].eq(tableReferral['relegateOrg_id']))
    table = table.innerJoin(tableMKBTree, tableMKBTree['DiagID'].eq(tableReferral['MKB']))

    cols = [
        tableMKBTree['DiagName'].alias('Reason'),
        tableReferral['MKB'].alias('MkbCode'),
        tableReferral['date'].alias('IssuedDateTime'),
        tableReferral['number'].alias('IdReferralMis'),
        tableReferral['type'].alias('IdReferralType'),
        tableReferral['clinicType'].alias('HospitalizationOrder'),
        tableReferral['createPerson_id'].alias('personId'),
        tableOrganisation['obsoleteInfisCode'].alias('IdSourceLpu'),
        tableOrganisation['obsoleteInfisCode'].alias('IdTargetLpu')
    ]
    cond = [
        tableReferral['deleted'].eq(0),
        tableReferral['event_id'].eq(eventId),
        tableMKBTree['DiagName'].ne('')
    ]
    order = [
        tableReferral['date'].desc()
    ]
    return db.getRecordEx(table, cols, cond, order)


def getDrugRecipeRecordList(db, eventId):
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableDrugRecipe = db.table('DrugRecipe')
    tableDDF_Item = db.table('DloDrugFormulary_Item')
    tableIssueForm = db.table('dlo_rbIssueForm')
    tableDosage = db.table('dlo_rbDosage')

    table = tableDrugRecipe
    table = table.innerJoin(tableEvent, tableEvent['id'].eq(tableDrugRecipe['event_id']))
    table = table.innerJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
    table = table.innerJoin(tableDDF_Item, tableDDF_Item['id'].eq(tableDrugRecipe['formularyItem_id']))
    table = table.innerJoin(tableDosage, tableDosage['id'].eq(tableDDF_Item['dosage_id']))
    table = table.innerJoin(tableIssueForm, tableIssueForm['id'].eq(tableDDF_Item['issueForm_id']))

    cols = [
        db.valueField('A').alias('ATCC'),
        tableDosage['miacCode'].alias('CourseDoseIdUnit'),
        tableDrugRecipe['signa'].alias('CourseDoseValue'),
        tableDosage['miacCode'].alias('DayDoseIdUnit'),
        db.makeField('{0} * {1}'.format(tableDrugRecipe['qnt'], tableDrugRecipe['numPerDay'])).alias('DayDoseValue'),
        tableDrugRecipe['qnt'].alias('DaysCount'),
        tablePerson['id'].alias('IdPersonMis'),  # Нам нужен только id, т.к. ФИО, ДР и т.п. заполним отдельно
        tableDrugRecipe['dateTime'].alias('IssuedDate'),
        db.valueField('PRE').alias('MedicineIssueType'),
        tableDDF_Item['name'].alias('MedicineName'),
        tableIssueForm['miacCode'].alias('MedicineType'),
        db.valueField('1').alias('MedicineUseWay'),
        "RIGHT(DrugRecipe.number, LENGTH(DrugRecipe.number) - INSTR(DrugRecipe.number, '#')) AS Number",
        tableDosage['miacCode'].alias('OneTimeDoseIdUnit'),
        tableDrugRecipe['dosage'].alias('OneTimeDoseValue'),
        "LEFT(DrugRecipe.number, INSTR(DrugRecipe.number, '#') - 1) AS Seria"
    ]

    cond = [
        tableDrugRecipe['event_id'].eq(eventId),
        tableDrugRecipe['deleted'].eq(0)
    ]

    order = [
    ]

    return db.getRecordList(table, cols, cond, order)


def getIdLPU(db, infis=None, orgStructureId=None):
    if orgStructureId is not None:
        return forceStringEx(db.translate('OrgStructure', 'id', orgStructureId, 'netrica_Code'))
    if infis is None:
        infis = QtGui.qApp.currentOrgInfis()
    record = db.getRecordEx(
        table='Organisation',
        cols='obsoleteInfisCode',
        where='''Organisation.infisCode = '%s' ''' % infis)
    if record is None:
        raise ValueError(u'Организация с infisCode == %s не найдена' % infis)
    return forceStringEx(record.value('obsoleteInfisCode'))


def getEventTypeCode(db, eventId):
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    table = tableEvent.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    cols = [
        tableEventType['code']
    ]
    cond = [
        tableEvent['id'].eq(eventId)
    ]
    rec = db.getRecordEx(table, cols, cond)
    return forceString(rec.value('code')) if rec else None


def getActionServiceRecord(db, actionId):
    tableAction = db.table('Action')
    tableAT = db.table('ActionType')
    tableATS = db.table('ActionType_Service')
    tableContract = db.table('Contract')
    tableTariff = db.table('Contract_Tariff')
    tableEvent = db.table('Event')
    tableFinance = db.table('rbFinance')
    tableMedicalAidUnit = db.table('rbMedicalAidUnit')
    tableService = db.table('rbService')

    table = tableAction
    table = table.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    table = table.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
    table = table.innerJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
    table = table.innerJoin(tableAT, tableAT['id'].eq(tableAction['actionType_id']))
    table = table.innerJoin(tableATS, tableATS['master_id'].eq(tableAT['id']))
    table = table.innerJoin(tableService, tableService['id'].eq(tableATS['service_id']))
    table = table.innerJoin(tableTariff, [tableTariff['master_id'].eq(tableContract['id']),
                                          tableTariff['service_id'].eq(tableService['id']),
                                          tableTariff['deleted'].eq(0)])
    table = table.innerJoin(tableMedicalAidUnit, tableMedicalAidUnit['id'].eq(tableTariff['unit_id']))

    cols = [
        tableAction['person_id'].alias('personId'),

        tableAction['begDate'].alias('DateStart'),
        tableAction['endDate'].alias('DateEnd'),
        tableAT['code'].alias('IdServiceType'),
        tableAT['name'].alias('ServiceName'),

        tableMedicalAidUnit['code'].alias('HealthCareUnit'),
        tableFinance['code'].alias('IdPaymentType'),
        db.valueField(0).alias('PaymentState'),
        tableAction['amount'].alias('Quantity'),
        tableTariff['price'].alias('Tariff')
    ]
    cond = [
        tableAction['id'].eq(actionId),
        tableTariff['price'].ne(0)
    ]
    return db.getRecordEx(table, cols, cond)


def getVisitServiceRecord(db, visitId):
    tableContract = db.table('Contract')
    tableEvent = db.table('Event')
    tableFinance = db.table('rbFinance')
    tableMAUnit = db.table('rbMedicalAidUnit')
    tableService = db.table('rbService')
    tableTariff = db.table('Contract_Tariff')
    tableVisit = db.table('Visit')

    table = tableVisit
    table = table.innerJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
    table = table.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
    table = table.innerJoin(tableFinance, tableFinance['id'].eq(tableContract['finance_id']))
    table = table.innerJoin(tableService, tableService['id'].eq(tableVisit['service_id']))
    table = table.innerJoin(tableTariff, [tableTariff['master_id'].eq(tableContract['id']),
                                          tableTariff['service_id'].eq(tableService['id']),
                                          tableTariff['deleted'].eq(0)])
    table = table.innerJoin(tableMAUnit, tableMAUnit['id'].eq(tableTariff['unit_id']))

    cols = [
        tableVisit['date'].alias('DateStart'),
        tableVisit['date'].alias('DateEnd'),
        tableService['code'].alias('IdServiceType'),
        tableService['name'].alias('ServiceName'),
        tableMAUnit['netrica_Code'].alias('HealthCareUnit'),
        tableFinance['code'].alias('IdPaymentType'),
        db.valueField(0).alias('PaymentState'),
        db.valueField(1).alias('Quantity'),
        tableTariff['price'].alias('Tariff'),
    ]
    cond = [
        tableVisit['id'].eq(visitId),
        tableTariff['price'].ne(0)
    ]
    return db.getRecordEx(table, cols, cond)


class LogStatus(object):
    NotSent = 0
    Sent = 1
    Success = 2
    Failed = 3


def getClientLogStatus(db, clientId):
    tableClientLog = db.table('{logger}.IEMKClientLog'.format(logger=getLoggerDbName()))
    rec = db.getRecordEx(tableClientLog, tableClientLog['status'], tableClientLog['client_id'].eq(clientId), tableClientLog['id'].desc())
    return forceInt(rec.value('status')) if rec else None


def setClientLogStatus(db, clientId, status):
        return db.query(u'''
            INSERT %s.IEMKClientLog (client_id, status, sendDate) VALUES (%i, %i, NOW())
        ''' % (library.LoggingModule.Logger.loggerDbName, clientId, status))


def getEventLogStatus(db, eventId):
    tableEventLog = db.table('{logger}.IEMKEventLog'.format(logger=getLoggerDbName()))
    rec = db.getRecordEx(tableEventLog, tableEventLog['status'], tableEventLog['event_id'].eq(eventId), tableEventLog['id'].desc())
    return forceInt(rec.value('status')) if rec else None


def setEventLogStatus(db, eventId, status):
    return db.query(u'''
        INSERT %s.IEMKEventLog (event_id, status, sendDate) VALUES(%i, %i, NOW())
    ''' % (library.LoggingModule.Logger.loggerDbName, eventId, status))


SIGN_DATA = u'''<?xml version="1.0" encoding="utf-8"?><SignData><Data>%s</Data><PublicKey></PublicKey><Hash></Hash><Sign></Sign></SignData>'''


MIME_TYPE = u'text/html'


MED_DOC_TYPES_LIST = [
    'DispensaryOne',
    'Referral',
    'SickList',
    'DischargeSummary',
    'LaboratoryReport',
    'ConsultNote',
    'Form027U',
    'PacsResult',
]