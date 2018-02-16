# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                      import forceInt, forceString

from Orgs.Utils                         import getOrgStructureDescendants

from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase

from ReportBedspace import CBedspace

def selectData(params):
    db = QtGui.qApp.db

    begDate        = params.get('begDate')
    endDate        = params.get('endDate')
    orgStructureId = params.get('orgStructureId')
    insurerId = params.get('insurerId')
    profileBed = params.get('profileBed')
    ungroupInsurer = params.get('ungroupInsurer')
    ungroupOrgStructure = params.get('ungroupOrgStructure')
    ungroupProfileBed = params.get('ungroupProfileBed')

    tableAction = db.table('Action')
    tableOrgStructure = db.table('OrgStructure')
    tableInsurerOrganisation = db.table('Organisation')
    tableHospitalBedProfile = db.table('rbHospitalBedProfile')

    select = 'Organisation.shortName AS orgName'
    cond = [tableAction['endDate'].dateGe(begDate),
            tableAction['endDate'].dateLe(endDate)]
    group = ['orgName']
    order = ['orgName']

    if profileBed:
        cond.append(tableHospitalBedProfile['id'].eq(profileBed))
    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if insurerId:
        cond.append(tableInsurerOrganisation['id'].eq(insurerId))
    if not ungroupInsurer:
        select = u'if(Organisation.area LIKE \'78%%\' OR Organisation.shortName = \'иКом\', Organisation.shortName, \'кТф3\') AS orgName'
    if not ungroupOrgStructure:
        order.append('OrgStructure.id')
        group.append('OrgStructure.id')
    if not ungroupProfileBed:
        order.append('rbHospitalBedProfile.id')
        group.append('rbHospitalBedProfile.name')
    duration = u'''if(DATE(Event.setDate) >= DATE('%(begDate)s') AND DATE(Event.execDate) <= DATE('%(endDate)s'), datediff(Event.execDate, Event.setDate),
                         if(DATE(Event.setDate) < DATE('%(begDate)s') AND DATE(Event.execDate) <= DATE('%(endDate)s'), datediff(Event.execDate, DATE('%(begDate)s')),
                         if(DATE(Event.setDate) >= DATE('%(begDate)s') AND DATE(Event.execDate) > DATE('%(endDate)s'), datediff(DATE('%(endDate)s'), Event.setDate),
                         datediff(DATE('%(endDate)s'), DATE('%(begDate)s')))))''' % {'begDate': begDate.toString(QtCore.Qt.ISODate), 'endDate': endDate.toString(QtCore.Qt.ISODate)}
    # countSetEvent = u'if(DATE(received.execDate) > DATE(\'%s\') OR received.execDate IS NULL, datediff(received.execDate, DATE(\'%s\')) + 1, if(OrgStructure.hasDayStationary = 1, datediff(received.execDate, received.setDate), datediff(received.execDate, received.setDate)+1))' % (endDate, endDate)


    stmt = u'''SELECT %(select)s,
                      OrgStructure.code,
                      rbHospitalBedProfile.name,
                      COUNT(IF(apos.value, act_received.id, NULL)) AS setEvent,
                      COUNT(act_leaved.id) AS execEvent,
                      COUNT(IF(Event.order = 1, act_leaved.id, NULL)) AS execPlanEvent,
                      COUNT(IF(Event.order = 2, act_leaved.id, NULL)) AS execExtraEvent,
                      sum(if(OrgStructure.hasDayStationary = 1, %(duration)s + 1, %(duration)s)) AS duration,
                      sum(if(Event.order = 1, if(OrgStructure.hasDayStationary = 1, %(duration)s + 1, %(duration)s), 0)) AS durationPlanEvent,
                      sum(if(Event.order = 2, if(OrgStructure.hasDayStationary = 1, %(duration)s + 1, %(duration)s), 0))  AS durationExtraEvent

              FROM Event
                INNER JOIN ClientPolicy ON ClientPolicy.client_id = Event.client_id AND ClientPolicy.id = getClientPolicyOnDateId(ClientPolicy.client_id, 1, Event.setDate)
                INNER JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id
                INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                INNER JOIN ActionType ON ActionType.id = Action.actionType_id
                LEFT JOIN Action act_received ON act_received.id = Action.id AND ActionType.flatCode = 'received'
                LEFT JOIN Action act_leaved ON act_leaved.id = Action.id AND ActionType.flatCode = 'leaved'
                LEFT JOIN Action act_leavedMoving ON act_leavedMoving.id = (SELECT MAX(a.id)
                                                                            FROM Action a
                                                                                INNER JOIN ActionType at ON at.id = a.actionType_id
                                                                            WHERE at.flatCode = 'moving' AND a.event_id = Event.id AND a.deleted = 0)
                LEFT JOIN Action act_receivedMoving ON act_receivedMoving.id = (SELECT MIN(a.id)
                                                                                FROM Action a
                                                                                    INNER JOIN ActionType at ON at.id = a.actionType_id
                                                                                WHERE at.flatCode = 'moving' AND a.event_id = Event.id AND a.deleted = 0)
                LEFT JOIN ActionPropertyType apt_reason ON apt_reason.actionType_id = act_received.actionType_id AND apt_reason.name = 'Причина отказа от госпитализации' AND apt_reason.deleted = 0
                LEFT JOIN ActionProperty ap_reason ON ap_reason.action_id = act_received.id AND ap_reason.type_id = apt_reason.id AND ap_reason.deleted = 0
                LEFT JOIN ActionProperty_String aps ON aps.id = ap_reason.id
                INNER JOIN ActionPropertyType apt_orgStructure ON apt_orgStructure.actionType_id = IF(act_leavedMoving.id, act_leavedMoving.actionType_id, act_receivedMoving.actionType_id) AND apt_orgStructure.name = 'Отделение пребывания' AND apt_orgStructure.deleted = 0
                INNER JOIN ActionPropertyType apt_hospitalBed ON apt_hospitalBed.actionType_id = apt_orgStructure.actionType_id AND apt_hospitalBed.name = 'Профиль' AND apt_hospitalBed.deleted = 0
                INNER JOIN ActionProperty ap_orgStructure ON ap_orgStructure.action_id = IF(act_leaved.id, act_leavedMoving.id, act_receivedMoving.id) AND ap_orgStructure.type_id = apt_orgStructure.id AND ap_orgStructure.deleted = 0
                LEFT JOIN ActionProperty ap_hospitalBed ON ap_hospitalBed.action_id = IF(act_leaved.id, act_leavedMoving.id, act_receivedMoving.id) AND ap_hospitalBed.type_id = apt_hospitalBed.id AND ap_hospitalBed.deleted = 0
                INNER JOIN ActionProperty_OrgStructure apos ON apos.id = ap_orgStructure.id
                LEFT JOIN ActionProperty_rbHospitalBedProfile aphb ON aphb.id = ap_hospitalBed.id
                INNER JOIN OrgStructure ON OrgStructure.id = apos.value
                LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = aphb.value

              WHERE %(where)s AND ActionType.flatCode IN ('received', 'leaved') AND Event.deleted = 0
              GROUP BY	%(group)s
              ORDER BY  %(order)s''' % {'select'  : select,
                                                                                                  'duration': duration,
                                                                                                  'where'   : db.joinAnd(cond),
                                                                                                  'group'   : ','.join(group),
                                                                                                  'order'   : ','.join(order)}
    return db.query(stmt)

class CReportBedspaceInsurance(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Использование коечного фонда по страховым компаниям')

    def getSetupDialog(self, parent):
        result = CBedspace(parent)
        result.setTitle(self.title())
        result.lblInsurance.setVisible(True)
        result.cmbInsurance.setVisible(True)
        result.chkUngroupInsurer.setVisible(True)
        result.chkUngroupOrgStructure.setVisible(True)
        result.chkUngroupProfileBeds.setVisible(True)
        return result

    def build(self, params):
        ungroupOrgStructure = params.get('ungroupOrgStructure', False)
        ungroupProfileBed = params.get('ungroupProfileBed')
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Страховая компания'                                 ], CReportBase.AlignCenter),
            ('3%',   [u'Отделение'                                          ], CReportBase.AlignCenter),
            ('3%',   [u'Профиль'                                            ], CReportBase.AlignCenter),
            ('3%',   [u'Госпитализир'                                       ], CReportBase.AlignRight),
            ('3%',   [u'Выбыло',               u'Всего'                     ], CReportBase.AlignRight),
            ( '3%',  [u'',                     u'План.'                     ], CReportBase.AlignRight),
            ( '3%',  [u'',                     u'Экстр'                     ], CReportBase.AlignRight),
            ( '3%',  [u'Проведено койко-дней', u'Всего'                     ], CReportBase.AlignRight),
            ( '10%', [u'',                     u'Средн. к/д'                ], CReportBase.AlignRight),
            ( '10%', [u'',                     u'План.госп.',  u'Всего'     ], CReportBase.AlignRight),
            ( '10%', [u'',                     u'',            u'Средн. к/д'], CReportBase.AlignRight),
            ( '10%', [u'',                     u'Экстр.госп.', u'Всего'     ], CReportBase.AlignRight),
            ( '10%', [u'',                     u'',            u'Средн. к/д'], CReportBase.AlignRight)]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 3, 1)
        table.mergeCells(0, 4, 1, 3)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(0, 7, 1, 6)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 2, 1)
        table.mergeCells(1, 9, 1, 2)
        table.mergeCells(1, 11, 1, 2)

        total = [0] * 10
        commonTotal = [0] * 10
        currentInsurer = None
        currentOrgStructure = None
        currentHospitalBedProfile = None
        rowsOrgStructure = 0
        rowsHospitalBedPlofile = 0
        while query.next():
            record = query.record()
            insurer = forceString(record.value('orgName'))
            orgStructure = forceString(record.value('code'))
            hospitalBedProfile = forceString(record.value('name'))
            setEvent = forceInt(record.value('setEvent'))
            execEvent = forceInt(record.value('execEvent'))
            execPlanEvent = forceInt(record.value('execPlanEvent'))
            execExtraEvent = forceInt(record.value('execExtraEvent'))
            duration = forceInt(record.value('duration'))
            execDurationPlanEvent = forceInt(record.value('durationPlanEvent'))
            execDurationExtraEvent = forceInt(record.value('durationExtraEvent'))

            argDurationEvent = round(float(duration)/(execEvent+setEvent) if execEvent or setEvent else 0, 2)
            argDurationPlanEvent = round(float(execDurationPlanEvent)/execPlanEvent if execPlanEvent else 0, 2)
            argDurationExtraEvent = round(float(execDurationExtraEvent)/execExtraEvent if execExtraEvent else 0, 2)
            if not ungroupOrgStructure:
                if currentInsurer is None or currentInsurer != insurer:
                    if rowsOrgStructure:
                        i = table.addRow()
                        table.setText(i, 1, u'Итого',  CReportBase.TableTotal)
                        commonTotal[5] = round(float(total[4])/(total[0] + total[1]) if total[0] or total[1] else 0, 2)
                        commonTotal[7] = round(float(total[6])/total[2] if total[2] else 0, 2)
                        commonTotal[9] = round(float(total[8])/total[3] if total[3] else 0, 2)
                        for column, value in enumerate(total):
                            if column not in [5, 7, 9]:
                                commonTotal[column] += value
                            table.setText(i, column + 3, value, CReportBase.TableTotal)
                        total = [0] * 10
                    i = table.addRow()
                    table.setText(i, 0, insurer)
                    table.mergeCells(i - rowsOrgStructure - 1, 0, rowsOrgStructure + 1, 1)
                    currentInsurer = insurer
                    rowsOrgStructure = 0
            else:
                i = table.addRow()
                table.setText(i, 0, insurer)
                table.setText(i, 1, u'Итого')
            if not ungroupProfileBed:
                if currentOrgStructure is None or currentOrgStructure != orgStructure or not rowsOrgStructure:
                    if rowsOrgStructure:
                        i = table.addRow()
                    table.setText(i, 1, orgStructure)
                    table.mergeCells(i-rowsHospitalBedPlofile if rowsOrgStructure else i-rowsHospitalBedPlofile - 1, 1, rowsHospitalBedPlofile, 1)
                    currentOrgStructure = orgStructure
                    rowsHospitalBedPlofile = 0
                if currentHospitalBedProfile is None or currentHospitalBedProfile != hospitalBedProfile or not rowsHospitalBedPlofile:
                    if rowsHospitalBedPlofile:
                        i = table.addRow()
                    table.setText(i, 2, hospitalBedProfile)
                    currentHospitalBedProfile = hospitalBedProfile
            elif not ungroupOrgStructure:
                if rowsOrgStructure:
                    i = table.addRow()
                table.setText(i, 1, orgStructure)
            table.setText(i, 3, setEvent)
            table.setText(i, 4, execEvent)
            table.setText(i, 5, execPlanEvent)
            table.setText(i, 6, execExtraEvent)
            table.setText(i, 7, duration)
            table.setText(i, 8, argDurationEvent)
            table.setText(i, 9, execDurationPlanEvent)
            table.setText(i, 10, argDurationPlanEvent)
            table.setText(i, 11, execDurationExtraEvent)
            table.setText(i, 12, argDurationExtraEvent)
            total[0] += setEvent
            total[1] += execEvent
            total[2] += execPlanEvent
            total[3] += execExtraEvent
            total[4] += duration
            total[5] =  round(float(total[4])/(total[0] + total[1]) if total[0] or total[1] else 0, 2)
            total[6] += execDurationPlanEvent
            total[7] =  round(float(total[6])/total[2] if total[2] else 0, 2)
            total[8] += execDurationExtraEvent
            total[9] =  round(float(total[8])/total[3] if total[3] else 0, 2)
            rowsHospitalBedPlofile += 1
            rowsOrgStructure += 1
        commonTotal = total
        if not ungroupOrgStructure:
            i = table.addRow()
            table.setText(i, 1, u'Итого',  CReportBase.TableTotal)
            commonTotal[5] = round(float(total[4])/(total[0] + total[1]) if total[0] or total[1] else 0, 2)
            commonTotal[7] = round(float(total[6])/total[2] if total[2] else 0, 2)
            commonTotal[9] = round(float(total[8])/total[3] if total[3] else 0, 2)
            for column, value in enumerate(total):
                if column not in [5, 7, 9]:
                    commonTotal[column] += value
                table.setText(i, column + 3, value, CReportBase.TableTotal)
            table.mergeCells(i - rowsOrgStructure, 0, rowsOrgStructure + 1, 1)
        if not ungroupProfileBed:
            table.mergeCells(i-rowsHospitalBedPlofile if rowsOrgStructure else i-rowsHospitalBedPlofile - 1, 1, rowsHospitalBedPlofile, 1)
        i = table.addRow()
        table.setText(i, 0, u'Стационар', CReportBase.TableTotal)
        for column, value in enumerate(commonTotal):
            table.setText(i, column + 3, value, CReportBase.TableTotal)
        return doc