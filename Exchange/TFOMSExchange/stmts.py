# -*- coding: utf-8 -*-
stmtOrderHospital = u'''
    SELECT
        rbHospitalBedProfile.code                   AS      hospBedProfile,
        OrgStructure_HospitalBed.profile_id         AS      orgHospBedProfile,
        ActionProperty_HospitalBed.value            AS      actPropHospBedVal,
        ActionProperty.id                           AS      actPropId,
        Action.id                                   AS      actId,
        Event.client_id                             AS      evClientId,
        Event.setDate                               AS      evSDate,
        Event.`order`                               AS      evOrder,
        Event.referral_id                           AS      evRefId,
        Event.org_id                                AS      evOrgId,
        Referral.relegateOrg_id                     AS      refRelOrgId,
        Referral.number                             AS      refNumber,
        Referral.date                               AS      refDate,
        Referral.MKB                                AS      refMKB,
        Organisation.infisCode                      AS      orgInfisCode,
        OrgStructure.infisCode                      AS      orgStructInfisCode
    FROM
        Action
        LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id
        LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = ActionProperty.id AND ActionProperty.type_id = 1821
        LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
        LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id
        LEFT JOIN Event ON Event.id = Action.event_id
        LEFT JOIN Referral ON Referral.id = Event.referral_id
        LEFT JOIN Organisation ON Organisation.id = Event.org_id
        LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_HospitalBed.id = ActionProperty.id AND ActionProperty.type_id = 1826
        LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
    WHERE
        Action.event_id = %s AND actionType_id = 134 AND NOT rbHospitalBedProfile.code IS NULL OR Action.event_id = %s AND actionType_id = 133 AND NOT rbHospitalBedProfile.code IS NULL
    '''
#Получение профиля койки
stmtCBedProfile = u'''
    SELECT
        rbHospitalBedProfile.code                   AS      hospBedProfile,
        OrgStructure_HospitalBed.profile_id         AS      orgHospBedProfile,
        ActionProperty_HospitalBed.value            AS      actPropHospBedVal,
        ActionProperty.id                           AS      actPropId,
        Action.id                                   AS      actId
    FROM
        Action
        LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id
        LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = ActionProperty.id AND ActionProperty.type_id = 1821
        LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
        LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id

    WHERE
        Action.event_id = %s AND actionType_id = 134
'''

#Список новых пациентов
stmtNewPatients = u'''
    SELECT DISTINCT Action.id FROM
    Action
    INNER JOIN ActionProperty a ON Action.id = a.action_id
    INNER JOIN ActionProperty_HospitalBed ON a.id
    INNER JOIN OrgStructure_HospitalBed ON ActionProperty_HospitalBed.value = OrgStructure_HospitalBed.id
    INNER JOIN rbHospitalBedProfile r ON r.code = OrgStructure_HospitalBed.profile_id
    WHERE Action.event_id = %s AND Action.actionType_id = 134 AND r.code = %s
'''

#Список выбывших пациентов
stmtLeavedPatients = u'''
    SELECT DISTINCT Action.id FROM
    Action
    INNER JOIN ActionProperty a ON Action.id = a.action_id
    INNER JOIN ActionProperty_HospitalBed ON a.id
    INNER JOIN OrgStructure_HospitalBed ON ActionProperty_HospitalBed.value = OrgStructure_HospitalBed.id
    INNER JOIN rbHospitalBedProfile r ON r.code = OrgStructure_HospitalBed.profile_id
    WHERE Action.event_id = %s AND Action.actionType_id = 133 AND r.code = %s
'''

#Получение евентов для коечноо фонда
stmtEventList = u'''
    SELECT DISTINCT Event.id, Action.id FROM
    Event
    INNER JOIN Action ON Action.event_id = Event.id
    INNER JOIN ActionProperty a ON Action.id = a.action_id
    INNER JOIN ActionProperty_HospitalBed ON a.id
    INNER JOIN OrgStructure_HospitalBed ON ActionProperty_HospitalBed.value = OrgStructure_HospitalBed.id
    INNER JOIN rbHospitalBedProfile r ON r.code = OrgStructure_HospitalBed.profile_id
    WHERE Event.setDate > \'%s\' AND Event.setDate < \'%s\' AND r.code = %s
'''

#Получение кода Мо по ActionId
stmtMoCode = u'''
    SELECT infisCode FROM
    Action a
    INNER JOIN Person p ON a.setPerson_id = p.id
    INNER JOIN Organisation o ON p.org_id = o.id
    WHERE a.id = %s
'''

#Получение кода отделения
stmtOrgStruct = u'''
    SELECT o.infisDepTypeCode FROM
    OrgStructure_HospitalBed oh
    INNER JOIN OrgStructure o ON o.id = oh.master_id
    WHERE oh.profile_id = %s
'''

#Получение списка евентов с выбывшими пациентами
leavePatientsList = u'''
    SELECT Event.id FROM
    Event
    INNER JOIN Action ON Action.event_id = Event.id
    WHERE Event.setDate > \'%s\' AND Event.setDate < \'%s\' AND Action.actionType_id = 134
'''