# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui
from library.Utils import forceString


def getActionTypeIdListByFlatCode(flatCode):
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    cond =[tableActionType['flatCode'].like(flatCode),
           tableActionType['deleted'].eq(0)
          ]
    return db.getIdList(tableActionType, 'id', cond)

#NOT USED. DELETEME?
def getDateReceivedCol():
    db = QtGui.qApp.db
    table = db.table('Action').alias('AR')
    return '(SELECT MIN(`AR`.`endDate`) '\
            'FROM `Action` AS `AR` '\
            'WHERE `AR`.`event_id`=`Action`.`event_id` '\
            'AND `AR`.`deleted`=0 '\
            'AND %s '\
            'AND `AR`.`status`=2) AS begDateReceived' % table['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%'))


#NOT USED. DELETEME?
def getDateLeavedCol():
    db = QtGui.qApp.db
    table = db.table('Action').alias('AL')
    return '(SELECT MAX(`AL`.`endDate`) '\
            'FROM `Action` AS `AL` '\
            'WHERE `AL`.`event_id`=`Action`.`event_id` '\
            'AND `AL`.`deleted`=0 '\
            'AND %s '\
            'AND `AL`.`status`=2) AS endDateLeaved' % table['actionType_id'].inlist(getActionTypeIdListByFlatCode('leaved%'))


def getAgeRangeCond(ageFor, ageTo):
    return '(Action.begDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)) '\
           'AND (Action.begDate < ADDDATE(Client.birthDate, INTERVAL %d YEAR))' % (ageFor, ageTo+1)


def getStatusObservation():
    return '''(SELECT CONCAT_WS('  ', rbStatusObservationClientType.code, rbStatusObservationClientType.name, rbStatusObservationClientType.color)
FROM Client_StatusObservation
INNER JOIN rbStatusObservationClientType ON rbStatusObservationClientType.id = Client_StatusObservation.statusObservationType_id
WHERE Client_StatusObservation.deleted = 0 AND Client_StatusObservation.master_id = Client.id
ORDER BY Client_StatusObservation.id DESC
LIMIT 0,1) AS statusObservation'''


def getCurrentOSHB():
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    return '''(SELECT CONCAT_WS('  ', OSHB.code, OSHB.name, IF(OSHB.sex=1, \'%s\', IF(OSHB.sex=2, \'%s\', ' ')))
FROM Action AS A
INNER JOIN ActionType AS AT ON AT.id=A.actionType_id
INNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id
INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id
INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value
INNER JOIN OrgStructure AS OS ON OS.id=OSHB.master_id
WHERE (A.event_id=Event.id) AND (A.deleted=0) AND (AP.deleted=0) AND (OS.deleted=0)
AND (APT.typeName LIKE 'HospitalBed') AND (AP.action_id=A.id)
AND (A.endDate IS NULL) AND (A.begDate<=%s)
LIMIT 0,1) AS bedCodeName'''%(forceString(u''' /М'''), forceString(u''' /Ж'''), tableAction['begDate'].formatValue(QtCore.QDate.currentDate()))

def getCurrentOSHBProfile():
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    return '''(SELECT HBP.name
FROM Action AS A
INNER JOIN ActionType AS AT ON AT.id=A.actionType_id
INNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id
INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id
INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value
INNER JOIN OrgStructure AS OS ON OS.id=OSHB.master_id
INNER JOIN rbHospitalBedProfile AS HBP ON HBP.id = OSHB.profile_id
WHERE (A.event_id=Event.id) AND (A.deleted=0) AND (AP.deleted=0) AND (OS.deleted=0)
AND (APT.typeName LIKE 'HospitalBed') AND (AP.action_id=A.id)
AND (A.endDate IS NULL) AND (A.begDate<=%s)
LIMIT 0,1) AS bedProfile'''%(tableAction['begDate'].formatValue(QtCore.QDate.currentDate()))


def getDataAPHB(permanent=0, typeId=0, profile=0, codeBeds=None):
    strFilter = u''''''
    strSelected = u''''''
    if permanent and permanent > 0:
        strFilter += u''' AND OSHB.isPermanent=%s'''%(forceString(permanent - 1))
    if typeId:
        strFilter += u''' AND OSHB.type_id=%s'''%(forceString(typeId))
    if codeBeds:
        strFilter += u''' AND OSHB.code LIKE '%s' '''%(codeBeds)
    if profile:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            strSelected = getPropertyAPHBP(profile) + u''' AND '''
        else:
            strFilter += u''' AND OSHB.profile_id=%s'''%(forceString(profile))
    strSelected += '''EXISTS(SELECT APHB.value
FROM ActionPropertyType AS APT
INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id
INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value
WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND AP.deleted=0 AND APT.deleted=0 AND APT.typeName LIKE 'HospitalBed'%s)'''%(strFilter)
    return strSelected


def getPropertyAPHBP(profile):
    return '''EXISTS(SELECT APHBP.value
FROM ActionPropertyType AS APT_Profile
INNER JOIN ActionProperty AS AP_Profile ON AP_Profile.type_id=APT_Profile.id
INNER JOIN ActionProperty_rbHospitalBedProfile AS APHBP ON APHBP.id=AP_Profile.id
INNER JOIN rbHospitalBedProfile AS RBHBP ON RBHBP.id=APHBP.value
WHERE APT_Profile.actionType_id = Action.actionType_id
AND AP_Profile.action_id = Action.id
AND AP_Profile.deleted = 0
AND APT_Profile.deleted = 0
AND APT_Profile.typeName LIKE 'rbHospitalBedProfile'
AND APHBP.value = %s)'''%(str(profile))


def getDataOrgStructure(propertyNameList, orgStructureIdList):
    orgStructureList = [u'NULL']
    for orgStructureId in orgStructureIdList:
        orgStructureList.append(forceString(orgStructureId))

    if isinstance(propertyNameList, basestring):
        propertyNameList = [propertyNameList]
    propertyNameCond = QtGui.qApp.db.joinOr(["APT.name LIKE '%s'" % propertyName for propertyName in propertyNameList])
    return '''EXISTS(SELECT APOS.value
    FROM ActionPropertyType AS APT
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
    INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
    INNER JOIN OrgStructure AS OS ON OS.id=APOS.value
    WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND %s AND OS.deleted=0 AND APOS.value %s)'''%(propertyNameCond, u' IN ('+(','.join(orgStructureList))+')')


def getDataClientQuoting(nameProperty, quotingTypeIdList):
    quotingTypeList = [u'NULL']
    for quotingTypeId in quotingTypeIdList:
        quotingTypeList.append(forceString(quotingTypeId))
    return '''EXISTS(SELECT APOS.value
    FROM ActionPropertyType AS APT
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
    INNER JOIN ActionProperty_Client_Quoting AS APOS ON APOS.id=AP.id
    INNER JOIN Client_Quoting AS CQ ON CQ.id=APOS.value
    INNER JOIN QuotaType AS QT ON CQ.quotaType_id=QT.id
    WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND QT.deleted = 0 AND APT.name LIKE '%s' AND CQ.deleted=0 AND QT.id %s)'''%(nameProperty, u' IN ('+(','.join(quotingTypeList))+')')


def getActionPropertyTypeName(nameProperty):
    return '''EXISTS(SELECT APT.id
FROM ActionPropertyType AS APT
INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
WHERE (AP.action_id=Action.id)
AND (APT.actionType_id=Action.actionType_id AND APT.deleted=0 AND APT.name LIKE '%s'))'''%(nameProperty)


def getDataOrgStructureName(propertyNameList, fieldAlias = 'nameOS', actionTableAlias = u'Action', codeFieldAlias='codeOS'):
    if isinstance(propertyNameList, basestring):
        propertyNameList = [propertyNameList]
    propertyNameCond = QtGui.qApp.db.joinOr(["APT.name LIKE '%s'" % propertyName for propertyName in propertyNameList])
    return u'''(SELECT
        OS.id
    FROM
        ActionPropertyType AS APT
        INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
        INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
        INNER JOIN OrgStructure AS OS ON OS.id=APOS.value
    WHERE
        APT.actionType_id=%(actionTable)s.actionType_id
        AND AP.action_id=%(actionTable)s.id
        AND APT.deleted=0
        AND %(propertyCond)s
        AND OS.deleted=0
    LIMIT 1) AS OSid,
    (SELECT OrgS.name FROM OrgStructure OrgS WHERE OrgS.id=OSid) AS %(fieldAlias)s,
    (SELECT OrgS.code FROM OrgStructure OrgS WHERE OrgS.id=OSid) AS %(codeFieldAlias)s''' % {
        'fieldAlias': fieldAlias,
        'actionTable': actionTableAlias,
        'propertyCond': propertyNameCond,
        'codeFieldAlias': codeFieldAlias
    }


def getAPOSNameField(tableAction, propertyName, fieldAlias='orgStructureName'):
    db = QtGui.qApp.db
    tableAP = db.table('ActionProperty')
    tableAPOS = db.table('ActionProperty_OrgStructure')
    tableAPT = db.table('ActionPropertyType')
    tableOrgStructure = db.table('OrgStructure')

    table = tableAPT
    table = table.innerJoin(tableAP, [tableAP['type_id'].eq(tableAPT['id']),
                                      tableAP['deleted'].eq(0)])
    table = table.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
    table = table.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableAPOS['value']))
    cols = [
        tableOrgStructure['name']
    ]
    cond = [
        tableAP['action_id'].eq(tableAction['id']),
        tableAPT['actionType_id'].eq(tableAction['actionType_id']),
        tableAPT['name'].like(propertyName),
        tableAPT['deleted'].eq(0)
    ]
    return db.makeField('(' + db.selectStmt(table, cols, cond, limit=1) + ')').alias(fieldAlias)


def getDataOrgStructureId(propertyNameList, fieldAlias = 'idOS', actionTableAlias = u'Action'):
    if isinstance(propertyNameList, basestring):
        propertyNameList = [propertyNameList]
    propertyNameCond = QtGui.qApp.db.joinOr(["APT.name LIKE '%s'" % propertyName for propertyName in propertyNameList])
    return u'''(SELECT
        APOS.value
    FROM
        ActionPropertyType AS APT
        INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
        INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
    WHERE
        APT.actionType_id=%(actionTable)s.actionType_id
        AND AP.action_id=%(actionTable)s.id
        AND APT.deleted=0
        AND %(propertyCond)s
    LIMIT 1) AS %(fieldAlias)s''' % {'fieldAlias' : fieldAlias, 'actionTable' : actionTableAlias, 'propertyCond' : propertyNameCond}


def getTransferPropertyIn(nameProperty, orgStructureIdList = None):
    orgStructureCond = '1'
    if orgStructureIdList and isinstance(orgStructureIdList, list):
        orgStructureCond = 'OS.id IN (%s)' % ', '.join(map(lambda x: str(x), orgStructureIdList))

    stmt = u'''EXISTS(SELECT APOS.value
    FROM ActionPropertyType AS APT
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
    INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
    INNER JOIN OrgStructure AS OS ON OS.id=APOS.value
    WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND APT.name LIKE '%s' AND OS.deleted=0 AND %s)'''
    return stmt % (nameProperty, orgStructureCond)


def getEventFeedId(dateFeed, alias=u''):
    return u'''
    EXISTS(
        SELECT
            EF.id
        FROM
            Event_Feed AS EF
        WHERE
        EF.event_id = Action.event_id
        AND EF.deleted = 0
        AND DATE(EF.date) = %s
        AND (
            diet_id IS NOT NULL
            OR courtingDiet_id IS NOT NULL
            OR EXISTS(SELECT id FROM Event_Feed_Meal WHERE master_id = EF.id)
        )
    ) %s'''%(dateFeed, alias)


# NOT USED. DELETEME??
def getPropertyAPOS(nameProperty, actionTypeIdList):
    return u'''(EXISTS(SELECT APOS.value
    FROM Event AS E
    INNER JOIN Action AS A ON A.event_id = E.id
    INNER JOIN ActionType AS AT ON AT.id=A.actionType_id
    INNER JOIN ActionPropertyType AS APT ON AT.id = APT.actionType_id
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id AND AP.action_id = A.id
    INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
    WHERE E.client_id = Event.client_id AND E.deleted = 0 AND A.deleted = 0 AND AT.deleted = 0 AND AP.deleted = 0 AND A.endDate IS NOT NULL AND (Action.plannedEndDate IS NULL OR (DATE(A.begDate) <= DATE(Action.plannedEndDate) AND DATE(Action.plannedEndDate) <= DATE(A.endDate))) AND APT.deleted=0 AND APT.name LIKE \'%s\' AND A.actionType_id IN (%s))) AS APOS_value'''%(nameProperty, ','.join(str(actionTypeId) for actionTypeId in actionTypeIdList if actionTypeId))


def getEventPhysicalActivity(date, alias):
    result = """
    (SELECT
        rbPhysicalActivityMode.name
    FROM Event_PhysicalActivity
        LEFT JOIN rbPhysicalActivityMode ON rbPhysicalActivityMode.id = Event_PhysicalActivity.physicalActivityMode_id
    WHERE
        Event_PhysicalActivity.event_id = Event.id
        AND Event_PhysicalActivity.deleted = 0
        AND DATE(Event_PhysicalActivity.date) = %s
    LIMIT 1) AS %s
    """ % (date, alias)
    return result




def getStringProperty(nameProperty, value):
    return u'''EXISTS(SELECT APS.id
    FROM ActionPropertyType AS APT
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
    INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
    WHERE  Action.id IS NOT NULL AND APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND APT.name LIKE '%s' AND %s)'''%(nameProperty, value)

def getExistsNonPayedActions():
    return u'''EXISTS( SELECT Action.id
      FROM Action
           LEFT JOIN rbFinance ON rbFinance.id = Action.finance_id
           INNER JOIN Contract ON Contract.id = Action.contract_id
      WHERE rbFinance.code = '4'
            AND Action.event_id = Event.id
            AND NOT Contract.ignorePayStatusForJobs
            AND ((Action.payStatus >> (CAST(rbFinance.code AS UNSIGNED) * 2)) & 3) != 3) AS isExistsNotPayedActions'''

#def getMKB():
#    return '''(SELECT Diagnosis.MKB
#FROM Diagnosis INNER JOIN Diagnostic ON Diagnostic.diagnosis_id=Diagnosis.id
#INNER JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id=rbDiagnosisType.id
#WHERE Diagnostic.event_id = Event.id AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0
#AND (rbDiagnosisType.code = '1'
#OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id
#AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC
#INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1'
#AND DC.event_id = Event.id
#LIMIT 1))))) AS MKB'''


def getComfortableColStmt(actionTypeIdList):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    return '''(SELECT CONCAT_WS('  ', A.plannedEndDate, A.payStatus)
FROM Action AS A
WHERE A.event_id = Event.id AND A.actionType_id IN (%s) AND A.deleted=0 AND A.plannedEndDate >= %s
ORDER BY A.plannedEndDate ASC
LIMIT 1) AS comfortable'''%(u', '.join(str(actionTypeId) for actionTypeId in actionTypeIdList if actionTypeId) , tableAction['begDate'].formatValue(QtCore.QDateTime.currentDateTime()))


def getOrgStructureIdList(treeIndex):
    treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
    return treeItem.getItemIdList() if treeItem else []


def getQuotingTypeIdList(quotingType):
    db = QtGui.qApp.db
    table = db.table('QuotaType')
    quotingTypeClass, quotingTypeId = quotingType
    if not quotingTypeId and (not quotingTypeClass == None):
        return db.getIdList(table, [table['id']], [table['deleted'].eq(0), table['class'].eq(quotingTypeClass)])
    elif quotingTypeId:
        groupCond = forceString(db.translate(table, 'id', quotingTypeId, 'code'))
        return getDescendantGroups(table, 'group_code', groupCond, quotingTypeId)
    return None


def getDescendantGroups(table, groupCol, groupCond, groupId):
    db = QtGui.qApp.db
    table = db.forceTable(table)
    group = table[groupCol]

    result = set([groupId])
    parents = set([groupCond])

    while parents:
        childrenId = set(db.getIdList(table, where=group.inlist(parents)))
        newChildrenId = childrenId-result
        result |= newChildrenId
        records = db.getRecordList(table, [table['code']], [table['id'].inlist(newChildrenId), table['deleted'].eq(0)])
        childrenCode = set([forceString(record.value('code')) for record in records])
        newChildrenCode = childrenCode-parents
        parents = newChildrenCode
    return list(result)
