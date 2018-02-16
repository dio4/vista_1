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
        INNER JOIN ActionType at ON at.id = Action.actionType_id AND at.flatCode = 'moving' OR at.id = Action.actionType_id AND at.flatCode = 'leaved'
    WHERE
        Action.event_id = %s AND NOT rbHospitalBedProfile.code IS NULL OR Action.event_id = %s AND NOT rbHospitalBedProfile.code IS NULL
    '''
#Получение профиля койки
stmtCBedProfile = u'''
    SELECT DISTINCT
        rbHospitalBedProfile.code                   AS      hospBedProfile,
        OrgStructure_HospitalBed.profile_id         AS      orgHospBedProfile,
        ActionProperty_HospitalBed.value            AS      actPropHospBedVal,
        ActionProperty.id                           AS      actPropId,
        Action.id                                   AS      actId
    FROM
        Action
        INNER JOIN ActionProperty ON ActionProperty.action_id = Action.id
        INNER JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = ActionProperty.id
        INNER JOIN ActionPropertyType apt ON ActionProperty.type_id IN (SELECT id FROM ActionPropertyType WHERE typeName = 'hospitalBed')
        INNER JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
        INNER JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id
    WHERE
        Action.event_id = %s
'''

#Список новых пациентов
stmtNewPatients = u'''
    SELECT DISTINCT Action.id FROM
    Action
    INNER JOIN ActionProperty a ON Action.id = a.action_id
    INNER JOIN ActionProperty_HospitalBed ON a.id = ActionProperty_HospitalBed.id
    INNER JOIN OrgStructure_HospitalBed ON ActionProperty_HospitalBed.value = OrgStructure_HospitalBed.id
    INNER JOIN rbHospitalBedProfile r ON r.code = OrgStructure_HospitalBed.profile_id
    INNER JOIN ActionType at ON at.id = Action.actionType_id
    WHERE Action.event_id = %s AND at.flatCode = 'moving' AND r.code = %s
'''

#Список выбывших пациентов
stmtLeavedPatients = u'''
    SELECT DISTINCT Action.id FROM
    Action
    INNER JOIN ActionProperty a ON Action.id = a.action_id
    INNER JOIN ActionProperty_HospitalBed ON a.id = ActionProperty_HospitalBed.id
    INNER JOIN OrgStructure_HospitalBed ON ActionProperty_HospitalBed.value = OrgStructure_HospitalBed.id
    INNER JOIN rbHospitalBedProfile r ON r.code = OrgStructure_HospitalBed.profile_id
    WHERE Action.event_id = %s AND Action.flatCode = 'leaved' AND r.code = %s
'''

#Получение евентов для коечноо фонда
stmtEventList = u'''
    SELECT DISTINCT Event.id, Action.id FROM
    Event
    INNER JOIN Action ON Action.event_id = Event.id
    INNER JOIN ActionProperty a ON Action.id = a.action_id
    INNER JOIN ActionProperty_HospitalBed ON a.id = ActionProperty_HospitalBed.id
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
    SELECT bookkeeperCode, infisCode FROM
    OrgStructure_HospitalBed oh
    INNER JOIN OrgStructure o ON o.id = oh.master_id
    WHERE oh.profile_id = %s
'''

#Получение списка евентов с выбывшими пациентами
leavePatientsList = u'''
    SELECT Event.id FROM
    Event
    INNER JOIN Action ON Action.event_id = Event.id
    INNER JOIN ActionType at ON at.id = Action.actionType_id AND at.flatCode = 'leaved'
    WHERE Event.setDate > \'%s\' AND Event.setDate < \'%s\'
'''

# Получение списка евентов с движением пациентов
movingPatientsList = u'''
    SELECT Event.id FROM
    Event
    INNER JOIN Action ON Action.event_id = Event.id
    INNER JOIN ActionType at ON at.id = Action.actionType_id AND at.flatCode = 'leaved' OR at.id = Action.actionType_id AND at.flatCode = 'moving'
    WHERE Event.setDate > \'%s\' AND Event.setDate < \'%s\'
'''

# Получение сведений о расписании
graphicInfo = u'''
    SELECT DISTINCT ap.id, ap.type_id FROM
    Action a
    INNER JOIN ActionType at ON a.actionType_id = at.id AND at.code = 'amb'
    INNER JOIN ActionProperty ap ON ap.action_id = a.id
    WHERE a.event_id = %s
'''

# Получение списка новых пациентов за инрвал времени
newPatientsForInterval = u'''
    SELECT DISTINCT e.id FROM
    Event e
    INNER JOIN Action a ON a.event_id = e.id
    INNER JOIN ActionType at ON at.id = a.actionType_id AND at.flatCode = 'leaved' OR at.id = a.actionType_id AND at.flatCode = 'received'
    WHERE e.createDatetime > '%s'
'''

# Получение сиска выбывших пациентов за интревал времени
leavePatientsForInterval = u'''
    SELECT DISTINCT e.id FROM
    Event e
    INNER JOIN Action a ON a.event_id = e.id
    INNER JOIN ActionType at ON at.id = a.actionType_id AND at.flatCode = 'leaved'
    WHERE e.modifyDatetime > '%s' AND execDate IS NOT NULL
'''