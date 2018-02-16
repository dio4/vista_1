# -*- coding: utf-8 -*-
from PyQt4.QtCore.QVariant import QVariant

from config import db

HOSP_EVENT_STMT = u'''
SELECT
  Event.id                                AS caseNumber,
  Event_OutgoingReferral.plannedDate      AS directionDate,
  Event_OutgoingReferral.org_id           AS directionLpuId,
  '111'                                   AS vmpNumber, #TODO:skkachaev: Эмм, обязательное поле номер талона ВМП?
  '111'                                   AS directionDoctorSpec, #TODO:skkacahev: Направивший врач?
  Event.execDate                          AS cureEndDate,
  Event.order                             AS hospitalizationType, #TODO:skkachaev: Канал госпитализации
  EmergencyCall.id                        AS smpNumber,
  '111'                                   AS newbornWeightGr, #TODO:skkachaev: Вес для новорождённых
  '111'                                   AS directionNumber, #TODO:skkachaev: Направление? Обязательное поле?
  SendDiag.value                          AS diagnosisSend,
  RecDiag.value                           AS diagnosisReception,
  MainDiagnosis.MKB                       AS clinicalDiagnosis_Main, #TODO:skkachaev: МКБ?
  AccompDiagnosis.MKB                     AS clinicalDiagnosis_Accomp, #TODO:skkachaev: МКБ?
  rbResult.name                           AS diseaseOutcome, #TODO:skkachaev: Наименование результата? Может, код? Может, справочник?
  rbPolicyType.name                       AS policyTypeName,
  ClientPolicy.insuranceArea              AS policyArea,
  TRUE                                    AS canEdit
FROM Event
  LEFT JOIN Event_OutgoingReferral ON Event_OutgoingReferral.master_id = Event.id
  LEFT JOIN EmergencyCall ON Event.id = EmergencyCall.event_id
  LEFT JOIN Action ReceivedAction ON Event.id = ReceivedAction.event_id
  LEFT JOIN ActionType ReceivedActionType ON ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedActionType.flatCode = 'received'
  LEFT JOIN ActionPropertyType SendDiagActionPropertyType ON ReceivedActionType.id = SendDiagActionPropertyType.actionType_id AND SendDiagActionPropertyType.name = 'Диагноз направившего учреждения'
  LEFT JOIN ActionProperty SendDiagActionProperty ON SendDiagActionPropertyType.id = SendDiagActionProperty.type_id AND ReceivedAction.id = SendDiagActionProperty.action_id
  LEFT JOIN ActionProperty_String SendDiag ON SendDiagActionProperty.id = SendDiag.id
  LEFT JOIN ActionPropertyType RecDiagActionPropertyType ON ReceivedActionType.id = RecDiagActionPropertyType.actionType_id AND RecDiagActionPropertyType.name = 'Диагноз приемного отделения'
  LEFT JOIN ActionProperty RecDiagActionProperty ON RecDiagActionPropertyType.id = RecDiagActionProperty.type_id AND ReceivedAction.id = RecDiagActionProperty.action_id
  LEFT JOIN ActionProperty_String RecDiag ON RecDiagActionProperty.id = RecDiag.id
  LEFT JOIN Diagnostic MainDiagnostic ON Event.id = MainDiagnostic.event_id
  LEFT JOIN rbDiagnosisType MainDiagType ON MainDiagnostic.diagnosisType_id = MainDiagType.id AND MainDiagType.code in ('1', '2')
  LEFT JOIN Diagnosis MainDiagnosis ON MainDiagnostic.diagnosis_id = MainDiagnosis.id
  LEFT JOIN Diagnostic AccompDiagnostic ON Event.id = AccompDiagnostic.event_id
  LEFT JOIN rbDiagnosisType AccompDiagType ON AccompDiagnostic.diagnosisType_id = AccompDiagType.id AND AccompDiagType.code = 9
  LEFT JOIN Diagnosis AccompDiagnosis ON AccompDiagnostic.diagnosis_id = AccompDiagnosis.id
  LEFT JOIN rbResult ON Event.result_id = rbResult.id
  LEFT JOIN Client ON Event.client_id = Client.id
  LEFT JOIN ClientPolicy ON clientPolicy_id = (SELECT CL.id FROM ClientPolicy CL WHERE CL.client_id = Client.id ORDER BY CL.endDate, CL.id DESC LIMIT 1)
  LEFT JOIN rbPolicyType ON ClientPolicy.policyType_id = rbPolicyType.id
WHERE Event.id = %i
'''

HOSP_ACTION_STMT = u'''
SELECT
  Action.id                               AS id,
  Action.person_id                        AS doctorId,
  rbPost.name                             AS doctorJobId, #TODO:skkachaev: Id, Строковое поле...
  OrgStructure.code                       AS departmentId, #TODO:skkachaev: Опять айди просят и строковое поле. И наше айди им ничего не даст. Скорее всего, справочник
  mes.MES.code                            AS msCode,
  Diag.value                              AS diagnosisCode,
  rbFinance.code                          AS paymentSource, #TODO:skkachaev: Вид оплаты. Скорее всего, справочник
  Action.begDate                          AS startDate,
  Action.endDate                          AS endDate,
  FALSE                                   AS skipInvoice
FROM Action
  LEFT JOIN Person ON Action.person_id = Person.id
  LEFT JOIN rbPost ON Person.post_id = rbPost.id
  LEFT JOIN ActionType ON Action.actionType_id = ActionType.id
  LEFT JOIN ActionPropertyType OrgActionPropertyType ON ActionType.id = OrgActionPropertyType.actionType_id AND OrgActionPropertyType.name = 'Отделение пребывания'
  LEFT JOIN ActionProperty OrgActionProperty ON OrgActionPropertyType.id = OrgActionProperty.type_id AND Action.id = OrgActionProperty.action_id
  LEFT JOIN ActionProperty_OrgStructure ON OrgActionProperty.id = ActionProperty_OrgStructure.id
  LEFT JOIN OrgStructure ON ActionProperty_OrgStructure.value = OrgStructure.id
  LEFT JOIN mes.MES ON Action.MES_id = mes.MES.id
  LEFT JOIN ActionPropertyType DiagActionPropertyType ON ActionType.id = DiagActionPropertyType.actionType_id AND DiagActionPropertyType.name = 'Диагноз'
  LEFT JOIN ActionProperty DiagActionProperty ON DiagActionPropertyType.id = DiagActionProperty.type_id AND Action.id = DiagActionProperty.action_id
  LEFT JOIN ActionProperty_String Diag ON DiagActionProperty.id = Diag.id
  LEFT JOIN rbFinance ON Action.finance_id = rbFinance.id
WHERE Action.event_id = %i;
'''

def setPatientType(record):
    record.setValue('patientType', QVariant()) #TODO:skkachaev: Вычисление этого магического типа

def createUpdateHospCase(eventId):
    eventRecord = db.getRecordEx(stmt=HOSP_EVENT_STMT % eventId)
    setPatientType(eventRecord)
    actionRecordList = db.getRecordList(stmt=HOSP_ACTION_STMT % eventId)


