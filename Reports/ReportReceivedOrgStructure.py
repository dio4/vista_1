# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString
from Orgs.Utils         import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from ReportBedspace import CBedspace

def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId')

    tableAction = db.table('Action')
    tableOrgStructure = db.table('ActionProperty_OrgStructure')

    cond = [tableAction['begDate'].dateGe(begDate),
            tableAction['begDate'].dateLe(endDate)]

    if orgStructureId:
        cond.append(tableOrgStructure['value'].inlist(getOrgStructureDescendants(orgStructureId)))

    stmt = u'''SELECT aps.value,
                      COUNT(Action.id) AS countEvent,
                      COUNT(aps.value) AS countRefusal,
                      COUNT(IF(Event.order = 2 AND aps.value IS NULL, Action.id, NULL)) AS countExtra,
                      COUNT(IF(Event.order = 1 AND aps.value IS NULL, Action.id, NULL)) AS countPlan,
                      COUNT(IF(o.isMedical = 1, apDirected.id, NULL)) AS countClinic,
                      COUNT(IF(o.isMedical = 2, apDirected.id, NULL)) AS countStationary,
                      COUNT(IF(apsOtherDirected.value = 'СМП', Action.id, NULL)) AS countSMP,
                      COUNT(IF(o.id IS NULL AND apsOtherDirected.value IS NULL, Action.id, NULL)) AS countWithoutOrgStructure,
                      COUNT(aps.id) AS countNotRequire
              FROM ActionType
                      INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
                      INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
                      INNER JOIN Action act ON act.id = (SELECT MIN(a.id) AS id
                                                         FROM ActionType
                                                         INNER JOIN Action a ON a.actionType_id = ActionType.id AND a.deleted = 0
                                                         WHERE ActionType.flatCode = 'moving' AND a.event_id = Action.event_id AND ActionType.deleted = 0)
                      INNER JOIN ActionProperty ON ActionProperty.action_id = act.id AND ActionProperty.deleted =0
                      INNER JOIN ActionPropertyType ON ActionPropertyType.id = ActionProperty.type_id AND ActionPropertyType.name = 'Отделение пребывания' AND ActionPropertyType.deleted =0
                      INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                      LEFT JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = (SELECT apt.id
                                                                                                FROM ActionPropertyType apt
                                                                                                WHERE apt.actionType_id = ActionType.id AND apt.name = 'Причина отказа от госпитализации' AND apt.deleted = 0) AND ap.deleted = 0
                      LEFT JOIN ActionProperty_String aps ON aps.id = ap.id
                      LEFT JOIN ActionProperty apDirected ON apDirected.action_id = Action.id AND apDirected.type_id = (SELECT apt.id
                                                                                                                        FROM ActionPropertyType apt
                                                                                                                        WHERE apt.actionType_id = ActionType.id AND apt.name = 'Кем направлен' AND apt.deleted = 0) AND apDirected.deleted = 0
                      LEFT JOIN ActionProperty_Organisation apo ON apo.id = apDirected.id
                      LEFT JOIN Organisation o ON o.id = apo.value AND o.deleted =0
                      LEFT JOIN ActionProperty apOtherDirected ON apOtherDirected.action_id = Action.id AND apOtherDirected.type_id = (SELECT apt.id
                                                                                                                        FROM ActionPropertyType apt
                                                                                                                        WHERE apt.actionType_id = ActionType.id AND apt.name = 'Прочие направители' AND apt.deleted = 0) AND apOtherDirected.deleted = 0
                      LEFT JOIN ActionProperty_String apsOtherDirected ON apsOtherDirected.id = apOtherDirected.id
              WHERE ActionType.flatCode = 'received' AND %s AND ActionType.deleted = 0
              GROUP BY aps.value''' % db.joinAnd(cond)
    return db.query(stmt)

class CReportReceivedOrgStructure(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по приемному отделению')

    def getSetupDialog(self, parent):
        result = CBedspace(parent)
        result.setTitle(self.title())
        result.cmbProfileBed.setVisible(False)
        result.lblProfileBed.setVisible(False)
        return result

    def build(self, params):
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
            ('20%',  [u'Показатель'], CReportBase.AlignCenter),
            ('3%',   [u'Количество'], CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)
        for index in xrange(12):
            table.addRow()
        total = [0]*12
        while query.next():
            record = query.record()
            countEvent = forceInt(record.value('countEvent'))
            value = forceString(record.value('value'))
            countNotRequire = forceInt(record.value('countNotRequire'))
            countRefusal =  forceInt(record.value('countRefusal'))
            countExtra = forceInt(record.value('countExtra'))
            countPlan = forceInt(record.value('countPlan'))
            countClinic = forceInt(record.value('countClinic'))
            countSMP = forceInt(record.value('countSMP'))
            countStationary = forceInt(record.value('countStationary'))
            countWithoutOrgStructure = forceInt(record.value('countWithoutOrgStructure'))
            if len(value):
                i = table.addRow()
                table.setText(i, 0, value)
                table.setText(i, 1, countNotRequire)
            total[0] += countEvent
            total[1] += countEvent - countRefusal
            total[2] += countExtra
            total[3] += countPlan
            total[4] += countRefusal
            total[5] += countClinic
            total[6] += countSMP
            total[7] += countStationary
            total[8] += countWithoutOrgStructure
        table.setText(1,  0, u'Количество обратившихся пациентов', CReportBase.TableTotal)
        table.setText(1,  1, total[0])
        table.mergeCells(2, 0, 1, 2)
        table.setText(2,  0, u'Из них:', CReportBase.TableTotal)
        table.setText(3,  0, u'Госпитализировано')
        table.setText(3,  1, total[1])
        table.setText(4,  0, u'-экстрено')
        table.setText(4,  1, total[2])
        table.setText(5,  0, u'-планово')
        table.setText(5,  1, total[3])
        table.setText(6,  0, u'Амбулаторно')
        table.setText(6,  1, total[4])
        table.mergeCells(7, 0, 1, 2)
        table.setText(7,  0, u'Направлены:', CReportBase.TableTotal)
        table.setText(8,  0, u'Поликлиниками')
        table.setText(8,  1, total[5])
        table.setText(9,  0, u'СМП')
        table.setText(9,  1, total[6])
        table.setText(10, 0, u'Больницами')
        table.setText(10, 1, total[7])
        table.setText(11, 0, u'Без направления')
        table.setText(11, 1, total[8])
        table.mergeCells(12, 0, 1, 2)
        table.setText(12,  0, u'Амбулаторные пациенты', CReportBase.TableTotal)
        return doc