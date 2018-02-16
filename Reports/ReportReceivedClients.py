# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from ReportBedspace import CReceivedClients
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceInt, forceString


def selectData(params, reportOrgStructure = False):
    db = QtGui.qApp.db
    begDate = params.get('edtBegDateTime', QtCore.QDateTime())
    endDate = params.get('edtEndDateTime', QtCore.QDateTime())
    orgStructureId = params.get('orgStructureId')
    profileBed = params.get('profileBed')

    tableAction = db.table('Action')
    tableOrgStructure = db.table('OrgStructure')
    tableHospitalBedProfile = db.table('rbHospitalBedProfile')

    cond = [tableAction['begDate'].ge(begDate),
            tableAction['begDate'].le(endDate)]

    if profileBed:
        cond.append(tableHospitalBedProfile['id'].eq(profileBed))
    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    stmt = u'''SELECT %s,
                     COUNT(act.id) AS countEvent,
                     COUNT(aps.value) AS countRefusal
               FROM ActionType
                      INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
                      INNER JOIN Action act ON act.id = (SELECT MIN(a.id) AS id
                                                         FROM ActionType
                                                         INNER JOIN Action a ON a.actionType_id = ActionType.id AND a.deleted = 0
                                                         WHERE ActionType.flatCode = 'moving' AND a.event_id = Action.event_id AND ActionType.deleted = 0)
                      INNER JOIN ActionProperty ON ActionProperty.action_id = act.id AND ActionProperty.deleted =0
                      INNER JOIN ActionPropertyType ON ActionPropertyType.id = ActionProperty.type_id AND ActionPropertyType.name = 'Отделение пребывания' AND ActionPropertyType.deleted =0
                      INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                      INNER JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                      LEFT JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id IN (SELECT apt.id
                                                                                                FROM ActionPropertyType apt
                                                                                                WHERE apt.name = 'Причина отказа от госпитализации' AND apt.deleted = 0)
                      LEFT JOIN ActionProperty_String aps ON aps.id = ap.id
                      LEFT JOIN ActionProperty apHospitalBedProfile ON apHospitalBedProfile.action_id = act.id AND apHospitalBedProfile.type_id IN (SELECT apt.id
                                                                                                                                               FROM ActionPropertyType apt
                                                                                                                                               INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'moving' AND at.deleted = 0
                                                                                                                                               WHERE apt.name = 'Профиль') AND apHospitalBedProfile.deleted = 0
                        %s
                    --  LEFT JOIN ActionProperty_rbHospitalBedProfile aphb ON aphb.id = apHospitalBedProfile.id
                     -- LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = aphb.value
                    --  LEFT JOIN OrgStructure_HospitalBed ON OrgStructure.id = OrgStructure_HospitalBed.master_id
                     -- LEFT JOIN rbHospitalBedProfile ON OrgStructure_HospitalBed.profile_id = rbHospitalBedProfile.id
               WHERE ActionType.flatCode = 'received' AND %s
               GROUP BY %s''' % (u'OrgStructure.code' if reportOrgStructure else u'rbHospitalBedProfile.name AS code',
                                 u'LEFT JOIN ActionProperty_rbHospitalBedProfile aphb ON aphb.id = apHospitalBedProfile.id '
                                 u'LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = aphb.value' if reportOrgStructure else u'LEFT JOIN OrgStructure_HospitalBed ON OrgStructure.id = OrgStructure_HospitalBed.master_id'
                                                                                                                                      u' LEFT JOIN rbHospitalBedProfile ON OrgStructure_HospitalBed.profile_id = rbHospitalBedProfile.id',
                                 db.joinAnd(cond), u'OrgStructure.id' if reportOrgStructure else u'rbHospitalBedProfile.id')
    return db.query(stmt)

class CReportReceivedClients(CReport):
    def __init__(self, parent, reportOrgStructure = False):
        CReport.__init__(self, parent)
        self.reportOrgStrucutre = reportOrgStructure
        self.setTitle(u'Структура поступления пациентов в стационар по отделениям' if self.reportOrgStrucutre else u'Структура поступления пациентов в стационар по профилям')

    def getSetupDialog(self, parent):
        result = CReceivedClients(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params, self.reportOrgStrucutre)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Отделение' if self.reportOrgStrucutre else u'Профиль'], CReportBase.AlignCenter),
            ('3%',   [u'Количество'                                          ], CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)

        total = 0
        totalRefusal = 0
        if self.reportOrgStrucutre:
            table.addRow()
            table.addRow()
        while query.next():
            record = query.record()
            code = forceString(record.value('code')).strip()
            countEvent = forceInt(record.value('countEvent'))
            countRefusal = forceInt(record.value('countRefusal'))
            if len(code):
                total += countEvent
                totalRefusal += countRefusal
                i = table.addRow()
                table.setText(i, 0, code)
                table.setText(i, 1, countEvent if self.reportOrgStrucutre else countEvent - countRefusal)
        if self.reportOrgStrucutre:
            table.setText(1, 0, u'Количество обратившихся пациентов')
            table.setText(1, 1, total)
            table.setText(2, 0, u'Госпитализировано')
            table.setText(2, 1, total - totalRefusal)
        return doc