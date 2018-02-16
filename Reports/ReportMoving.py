# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils          import forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Reports.ReportF16      import CF16

def selectData(params, lstOrgStructure, lstProfileBed):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    order           = params.get('order')
    orgStructureId  = params.get('orgStructureId')
    typeHosp        = params.get('typeHosp')
    cmbOrgStructure = params.get('cmbOrgStructure')
    cmbProfileBed   = params.get('cmbProfileBed')
    profileBed      = params.get('profileBed')
    financeId       = params.get('financeId')

    typeSubQuery = {'moving'         : ('moving',      u'Отделение пребывания'),
                    'received'       : ('received',    u'Направлен в отделение'),
                    'movingInto'     : ('moving',      u'Переведен в отделение'),
                    'movingFrom'     : ('moving',      u'Переведен из отделения'),
                    'leaved'         : ('leaved',      None)}

    def subQuery(typeQuery):
        infoTypeQuery = typeSubQuery[typeQuery]
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableAct = db.table('Action').alias('act')
        tableActionPropertyType = db.table('ActionPropertyType')
        tableActionProperty = db.table('ActionProperty')
        tableAp = db.table('ActionProperty').alias('ap')
        tableAPHospitalBed = db.table('ActionProperty').alias('apHospitalBedProfile')
        tableAPOrgStructure = db.table('ActionProperty_OrgStructure')
        tableAPHospitalBedProfile = db.table('ActionProperty_rbHospitalBedProfile')
        tableAPS = db.table('ActionProperty_String').alias('aps')
        tableOrgStructure = db.table('OrgStructure')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableHospitalBedProfile = db.table('rbHospitalBedProfile')
        tableMoving = tableAction

        select = []
        cond = [tableActionType['flatCode'].eq(infoTypeQuery[0])]

        queryTable = tableActionType.innerJoin(tableAction, [tableAction['actionType_id'].eq(tableActionType['id']),
                                                             tableAction['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableEvent, [tableEvent['id'].eq(tableAction['event_id']),
                                                           tableEvent['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

        if infoTypeQuery[1] is not None:
            select.append('COUNT(%s) %s' % (tableAction['id'], typeQuery))
            queryTable = queryTable.innerJoin(tableActionPropertyType, [tableActionPropertyType['actionType_id'].eq(tableActionType['id']),
                                                                        tableActionPropertyType['name'].eq(infoTypeQuery[1]),
                                                                        tableActionPropertyType['deleted'].eq(0)])
            queryTable = queryTable.innerJoin(tableActionProperty, [tableActionProperty['action_id'].eq(tableAction['id']),
                                                                    tableActionProperty['type_id'].eq(tableActionPropertyType['id']),
                                                                    tableActionProperty['deleted'].eq(0)])
        if typeQuery in ('received', 'leaved'):
            tableActMoving = db.table('Action').alias('act_moving')
            queryTable = queryTable.innerJoin(tableActMoving, u'''act_moving.id = (SELECT %s
                                                                  FROM ActionType at
                                                                    INNER JOIN Action a ON a.actionType_id = at.id AND a.deleted = 0
                                                                  WHERE at.flatCode = 'moving' AND a.event_id = Event.id AND at.deleted = 0)''' % ('MAX(a.id)' if typeQuery == 'leaved' else 'MIN(a.id)'))
            tableMoving = tableActMoving
            cond.extend([tableAction['begDate'].dateGe(begDate), tableAction['begDate'].dateLe(endDate)])

        queryTable = queryTable.leftJoin(tableAPHospitalBed, [tableAPHospitalBed['action_id'].eq(tableMoving['id']),
                                                              u'''apHospitalBedProfile.type_id = (SELECT apt.id
                                                                                                  FROM ActionPropertyType apt
                                                                                                  INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'moving' AND at.deleted = 0
                                                                                                  WHERE apt.name = 'Профиль') AND apHospitalBedProfile.deleted = 0 '''])
        queryTable = queryTable.leftJoin(tableAPHospitalBedProfile, tableAPHospitalBedProfile['id'].eq(tableAPHospitalBed['id']))
        queryTable = queryTable.leftJoin(tableHospitalBedProfile, tableHospitalBedProfile['id'].eq(tableAPHospitalBedProfile['value']))

        select.extend([tableHospitalBedProfile['id'].alias('hbpId'),
                       tableAPOrgStructure['value'].alias('id')])

        if typeQuery != 'leaved':
            queryTable = queryTable.innerJoin(tableAPOrgStructure, tableAPOrgStructure['id'].eq(tableActionProperty['id']))


        queryTable = queryTable.leftJoin(tableAct, [tableAct['event_id'].eq(tableEvent['id']),
                                                    tableAct['actionType_id'].eq(db.translate('ActionType', 'flatCode', 'received', 'id'))])
        queryTable = queryTable.leftJoin(tableAp, [tableAp['action_id'].eq(tableAct['id']),
                                                   u'''ap.type_id = (SELECT apt.id
                                                                     FROM ActionPropertyType apt
                                                                     WHERE apt.actionType_id = act.actionType_id AND apt.name = 'Причина отказа от госпитализации' AND apt.deleted = 0)'''])
        queryTable = queryTable.leftJoin(tableAPS, tableAPS['id'].eq(tableAp['id']))


        if order:
            cond.append(tableEvent['order'].eq(order))
        if lstOrgStructure and cmbOrgStructure:
            cond.append(tableAPOrgStructure['value'].inlist(lstOrgStructure))
        if orgStructureId and not cmbOrgStructure:
            cond.append(tableAPOrgStructure['value'].inlist(getOrgStructureDescendants(orgStructureId)))
        if lstProfileBed and cmbProfileBed:
            cond.append(tableHospitalBedProfile['id'].inlist(lstProfileBed))
        if profileBed:
            cond.append(tableHospitalBedProfile['id'].eq(profileBed))

        if typeHosp == 1:
            cond.extend([u'OrgStructure.hasDayStationary = 0', 'aps.value IS NULL'])
        if typeHosp == 3:
            cond.append('aps.value IS NOT NULL')
        if financeId:
            cond.append(tableAction['finance_id'].eq(financeId))

        if typeQuery == 'moving':
            cond.extend([tableAction['begDate'].dateLt(begDate),
                         db.joinOr([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].isNull()])])
        elif typeQuery == 'movingInto':
            cond.extend([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].dateLe(endDate)])
        elif typeQuery == 'movingFrom':
            cond.extend([tableAction['begDate'].dateGe(begDate), tableAction['begDate'].dateLe(endDate)])
        elif typeQuery == 'leaved':
            tableActionPropertyResult = db.table('ActionProperty').alias('ActionPropertyResult')
            tableActionPropertyTypeResult = db.table('ActionPropertyType').alias('ActionPropertyTypeResult')

            tableAPString = db.table('ActionProperty_String')
            tableAPOS = db.table('ActionProperty').alias('ap_os')
            select.append(u'''COUNT(ap_os.id) AS leaved
                            , COUNT(IF(ActionProperty_String.value = 'умер', ActionProperty_String.id, NULL)) AS leavedDeath
                            , COUNT(IF(ActionProperty_String.value = 'переведен в другой стационар', ActionProperty_String.id, NULL)) AS leavedOther''')
            queryTable = queryTable.innerJoin(tableAPOS, [tableAPOS['action_id'].eq(tableMoving['id']),
                                                          u'''ap_os.type_id = (SELECT apt.id
                                                                               FROM ActionPropertyType apt
                                                                               WHERE apt.actionType_id = act_moving.actionType_id AND apt.name = 'Отделение пребывания' AND apt.deleted = 0) AND ap_os.deleted = 0'''])
            queryTable = queryTable.innerJoin(tableAPOrgStructure, tableAPOrgStructure['id'].eq(tableAPOS['id']))
            queryTable = queryTable.leftJoin(tableActionPropertyTypeResult, [tableActionPropertyTypeResult['actionType_id'].eq(tableActionType['id']),
                                                                             tableActionPropertyTypeResult['name'].eq(u'Исход госпитализации'),
                                                                             tableActionPropertyTypeResult['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableActionPropertyResult, [tableActionPropertyResult['action_id'].eq(tableAction['id']),
                                                                         tableActionPropertyResult['type_id'].eq(tableActionPropertyTypeResult['id']),
                                                                         tableActionPropertyResult['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableAPString, tableAPString['id'].eq(tableActionPropertyResult['id']))

        queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableAPOrgStructure['value']))

        group = [tableAPOrgStructure['value'],
                 tableAPHospitalBedProfile['value']]

        return db.selectStmt(queryTable, select, cond, group)

    cond = []
    if typeHosp == 2:
        cond.append(u'mainTable.hasDayStationary = 1')

    stmt = ''' SELECT  OrgStructure.name AS osName,
                       rbHospitalBedProfile.name AS hbpName,
                       mainTable.deployed,
                       moving.moving,
                       leaved.leavedOther,
                       received.received,
                       leaved.leaved,
                       leaved.leavedDeath,
                       movingInto.movingInto,
                       movingFrom.movingFrom
                FROM OrgStructure
                LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.master_id = OrgStructure.id
                LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id
                LEFT JOIN ((SELECT os.id AS osId,
                              os.name AS osName,
                              hbp.id AS hbpId,
                              hbp.name AS hbpName,
                              COUNT(oshb.id) AS deployed
                        FROM OrgStructure_HospitalBed oshb, OrgStructure os, rbHospitalBedProfile hbp
                        WHERE oshb.master_id = os.id AND hbp.id = oshb.profile_id AND oshb.isPermanent = 1 AND oshb.involution = 0
                        GROUP BY os.id, hbp.id
                        ORDER BY os.id)  AS mainTable) ON mainTable.osId = OrgStructure.id AND mainTable.hbpId = rbHospitalBedProfile.id
                LEFT JOIN (%s) received ON received.id = OrgStructure.id AND rbHospitalBedProfile.id = received.hbpId
                LEFT JOIN (%s) movingInto ON movingInto.id = OrgStructure.id AND rbHospitalBedProfile.id = movingInto.hbpId
                LEFT JOIN (%s) movingFrom ON movingFrom.id = OrgStructure.id AND rbHospitalBedProfile.id = movingFrom.hbpId
                LEFT JOIN (%s) leaved ON leaved.id = OrgStructure.id AND rbHospitalBedProfile.id = leaved.hbpId
                LEFT JOIN (%s) moving ON moving.id = OrgStructure.id AND rbHospitalBedProfile.id = moving.hbpId
                WHERE OrgStructure.type = 1 AND OrgStructure.deleted = 0 %s
                GROUP BY OrgStructure.id, rbHospitalBedProfile.id
                ORDER BY OrgStructure.name, rbHospitalBedProfile.name''' % (subQuery('received'),
                                                                            subQuery('movingInto'),
                                                                            subQuery('movingFrom'),
                                                                            subQuery('leaved'),
                                                                            subQuery('moving'), 'AND %s' % db.joinAnd(cond) if cond else '')

    return db.query(stmt)

class CReportMoving(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения о движении больных (отделения и профили)')

    def getSetupDialog(self, parent):
        result = CF16(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        lstProfileBedDict = params.get('lstProfileBed', None)
        lstProfileBed = lstProfileBedDict.keys()
        query = selectData(params, lstOrgStructure, lstProfileBed)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Отделение'                                           ], CReportBase.AlignLeft),
            ('20%',  [u'Профиль'                                             ], CReportBase.AlignLeft),
            ('5%',  [u'Развернуто коек'                                     ], CReportBase.AlignRight),
            ('5%',  [u'Состояло'                                            ], CReportBase.AlignRight),
            ('5%',  [u'Поступило'                                           ], CReportBase.AlignRight),
            ('5%',  [u'Выбыло'                                              ], CReportBase.AlignRight),
            ('5%',  [u'Переведено из др.отд.'], CReportBase.AlignRight),
            ('5%',  [u'Переведено в др.отд.'], CReportBase.AlignRight),
            ('5%',  [u'Переведено в др.стац.'], CReportBase.AlignRight),
            ('5%',  [u'Умерло'], CReportBase.AlignRight),
            ('5%',  [u'Состоит'], CReportBase.AlignRight),
            ('5%',  [u'Назначено на выпис.'], CReportBase.AlignRight),
            ('5%',  [u'Свободных мест'], CReportBase.AlignRight),
            ('5%',  [u'Перегруз'], CReportBase.AlignRight)]

        table = createTable(cursor, tableColumns)

        countColumns = len(tableColumns)

        currentOrgStructure = None
        countHospitalBed = 0
        totalOrgStructure = [0] * (countColumns - 2)
        total = totalOrgStructure
        while query.next():
            record = query.record()
            orgStructure = forceString(record.value('osName'))
            hbpName  = forceString(record.value('hbpName'))
            deployed = forceInt(record.value('deployed'))
            moving = forceInt(record.value('moving'))
            leavedOther = forceInt(record.value('leavedOther'))
            received = forceInt(record.value('received'))
            leaved = forceInt(record.value('leaved'))
            leavedDeath = forceInt(record.value('leavedDeath'))
            movingInto = forceInt(record.value('movingInto'))
            movingFrom = forceInt(record.value('movingFrom'))
            overloadBed = 0
            freeBed = 0

            i = table.addRow()
            if currentOrgStructure != orgStructure:
                if currentOrgStructure is not None:
                    table.setText(i, 1, u'Итого', CReportBase.TableTotal)
                    for column, value in enumerate(totalOrgStructure):
                        total[column] += value
                        table.setText(i, column + 2, value, CReportBase.TableTotal)
                    table.mergeCells(i - countHospitalBed, 0, countHospitalBed + 1, 1)
                    i = table.addRow()
                totalOrgStructure = [0] * (countColumns - 2)
                table.setText(i, 0, orgStructure)
                currentOrgStructure = orgStructure
                countHospitalBed = 0

            isInHosp = moving + received - movingFrom + movingInto - leaved
            bookedBed = deployed - isInHosp
            if deployed:
                if bookedBed > 0:
                    freeBed = bookedBed
                else:
                    overloadBed = abs(bookedBed)
            table.setText(i,  1, hbpName)
            table.setText(i,  2, deployed)
            table.setText(i,  3, moving)
            table.setText(i,  4, received)
            table.setText(i,  5, leaved)
            table.setText(i,  6, movingInto)
            table.setText(i,  7, movingFrom)
            table.setText(i,  8, leavedOther)
            table.setText(i,  9, leavedDeath)
            table.setText(i, 10, isInHosp)
            table.setText(i, 11, 0)
            table.setText(i, 12, freeBed)
            table.setText(i, 13, overloadBed)

            totalOrgStructure[0] += deployed
            totalOrgStructure[1] += moving
            totalOrgStructure[2] += received
            totalOrgStructure[3] += leaved
            totalOrgStructure[4] += movingInto
            totalOrgStructure[5] += movingFrom
            totalOrgStructure[6] += leavedOther
            totalOrgStructure[7] += leavedDeath
            totalOrgStructure[8] += isInHosp
            totalOrgStructure[9] += 0
            totalOrgStructure[10] += freeBed
            totalOrgStructure[11] += overloadBed

            countHospitalBed += 1
        i = table.addRow()
        table.setText(i, 1, u'Итого', CReportBase.TableTotal)
        for column, value in enumerate(totalOrgStructure):
            total[column] += value
            table.setText(i, column + 2, value, CReportBase.TableTotal)
        table.mergeCells(i - countHospitalBed, 0, countHospitalBed + 1, 1)
        i = table.addRow()
        table.setText(i, 0, u'Стационар', CReportBase.TableTotal)
        for column, value in enumerate(total):
            table.setText(i, column + 2, value, CReportBase.TableTotal)

        return doc
