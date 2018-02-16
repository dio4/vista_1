# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceInt, forceString
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from Reports.Ui_ReportPatientEntranceOrgStructureSetup import Ui_PatientEntranceOrgStructureSetupDialog
from library.vm_collections import OrderedDict


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    begTime = params.get('begTime')
    endTime = params.get('endTime')
    financeId = params.get('financeId')
    orgStruct = params.get('orgStructure')
    eventType = params.get('eventType')

    tableFinance   = db.table('rbFinance')
    tableEventType = db.table('EventType')
    tableAction    = db.table('Action').alias('a1')
    tableOrgStruct = db.table('OrgStructure')

    begDateTime = QtCore.QDateTime(begDate, begTime)
    endDateTime = QtCore.QDateTime(endDate, endTime)

    cond = [tableAction['endDate'].datetimeGe(begDateTime),
            tableAction['endDate'].datetimeLe(endDateTime)]

    if eventType:
        cond.append(tableEventType['id'].eq(eventType))
    if financeId:
        cond.append(tableFinance['id'].eq(financeId))
    if orgStruct:
        cond.append(tableOrgStruct['id'].eq(orgStruct))

    stmt = u"""SELECT
os.name as departmnt,
os.type as depType,
e.order as evOrder,
rbf.name as rbFinance,
aps1.value as reasonDeny,
aps2.value as actionResult,
res.name as eventResult
FROM
Event e
INNER JOIN EventType et ON et.id = e.eventType_id
INNER JOIN ActionType at1 ON at1.flatCode = 'received' AND at1.deleted = 0
INNER JOIN ActionType at2 ON at2.flatCode = 'leaved' AND at2.deleted = 0
INNER JOIN Action a1 ON a1.actionType_id = at1.id AND a1.event_id = e.id AND a1.deleted = 0
LEFT JOIN Action a2 ON a2.actionType_id = at2.id AND a2.event_id = e.id AND a2.deleted = 0

LEFT JOIN ActionPropertyType apt1 ON apt1.actionType_id = at1.id AND apt1.name = 'Направлен в отделение' AND apt1.deleted = 0
LEFT JOIN ActionProperty ap1 ON ap1.action_id = a1.id AND apt1.id = ap1.type_id AND ap1.deleted = 0
LEFT JOIN ActionProperty_OrgStructure apos ON apos.id = ap1.id

LEFT JOIN OrgStructure os ON os.id = apos.value
LEFT JOIN rbFinance rbf ON rbf.id = a1.finance_id

LEFT JOIN ActionPropertyType apt2 ON apt2.actionType_id = at1.id AND apt2.name = 'Причина отказа от госпитализации' AND apt2.deleted = 0
LEFT JOIN ActionProperty ap2 ON ap2.type_id = apt2.id AND ap2.action_id = a1.id AND ap2.deleted = 0
LEFT JOIN ActionProperty_String aps1 ON aps1.id = ap2.id

LEFT JOIN rbResult res ON res.id = e.result_id

LEFT JOIN ActionPropertyType apt3 ON apt3.actionType_id = at2.id AND apt3.name = 'Исход госпитализации' AND apt3.deleted = 0
LEFT JOIN ActionProperty ap3 ON ap3.action_id = a2.id AND ap3.type_id = apt3.id AND ap3.deleted = 0
LEFT JOIN ActionProperty_String aps2 ON aps2.id = ap3.id
WHERE e.deleted = 0 AND %s
ORDER BY departmnt
    """ % db.joinAnd(cond)
    return db.query(stmt)


class CReportPatientEntranceOrgStructure(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Поступление больных по отделениям')

    def getSetupDialog(self, parent):
        result = CReportPatientEntranceOrgStructureSetupDialog(parent)
        result.setTitle(self.title())
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
            ('28%', [u'Отделение',            u''          ], CReportBase.AlignLeft),
            ('5%',  [u'Госпитализировано',    u'Всего'     ], CReportBase.AlignRight),
            ('8%',  [u'',                     u'Плановых'  ], CReportBase.AlignRight),
            ('8%',  [u'',                     u'Экстренных'], CReportBase.AlignRight),
            ('10%', [u'',                     u'в т.ч. ОМС'], CReportBase.AlignRight),
            ('5%',  [u'Не госпитализировано', u'Всего'     ], CReportBase.AlignRight),
            ('10%', [u'',                     u'Амбулатор.'], CReportBase.AlignRight),
            ('10%', [u'',                     u'Отказн.'   ], CReportBase.AlignRight),
            ('8%',  [u'в т.ч. умерло',        u''          ], CReportBase.AlignRight),
            ('8%',  [u'Всего',                u''          ], CReportBase.AlignRight)]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 4)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)

        report = OrderedDict()

        while query.next():
            record = query.record()
            departmnt = forceString(record.value('departmnt'))
            depType = forceInt(record.value('depType'))
            evOrder = forceInt(record.value('evOrder'))
            rbFinance = forceString(record.value('rbFinance'))
            reasonDeny = forceString(record.value('reasonDeny'))
            actionResult = forceString(record.value('actionResult'))
            eventResult = forceString(record.value('eventResult'))

            """
            алгоритм:

            если есть св-во "Причина отказа от госпитализации":
                # это ветка Не госпитализировано
                если OrgStructure.type == 4:
                    -- это ветка Отказн --
                иначе:
                    -- это ветка Амбулатор --
            иначе:
                # это ветка Госпитализировано
                если Event.order == 1:
                    -- это ветка Плановых --
                если Event.order == 2:
                    -- это ветка Экстрен --
                если Event.order in (1,2) AND rbFinance == 'ОМС':
                    -- это ветка в т.ч. ОМС --

            если actionResult == 'умер' or eventResult.find('умер') > -1 or eventResult.find('смерть') > -1:
                -- это ветка в т.ч. умерло --
            """

            repRow = report.setdefault(departmnt, {'plan': 0, 'extren': 0, 'OMS': 0, 'amb': 0, 'deny': 0, 'died': 0})

            if reasonDeny:
                if depType == 4:
                    repRow['deny'] += 1
                else:
                    repRow['amb'] += 1
            else:
                if evOrder == 1:
                    repRow['plan'] += 1
                if evOrder == 2:
                    repRow['extren'] += 1
                if evOrder in (1, 2) and rbFinance.upper() == u'ОМС':
                    repRow['OMS'] += 1
            eventResult = eventResult.lower()
            if actionResult.lower() == u'умер' or eventResult.find(u'умер') > -1 or eventResult.find(u'смерть') > -1:
                repRow['died'] += 1

        total = {'plan': 0, 'extren': 0, 'OMS': 0, 'amb': 0, 'deny': 0, 'died': 0}
        for department, depStat in report.items():
            i = table.addRow()

            plan = depStat.get('plan')
            extren = depStat.get('extren')
            OMS = depStat.get('OMS')
            deny = depStat.get('deny')
            amb = depStat.get('amb')
            died = depStat.get('died')

            table.setText(i, 0, department if department else u'<без уточнения>')
            table.setText(i, 1, plan + extren)
            table.setText(i, 2, plan)
            table.setText(i, 3, extren)
            table.setText(i, 4, OMS)
            table.setText(i, 5, amb + deny)
            table.setText(i, 6, amb)
            table.setText(i, 7, deny)
            table.setText(i, 8, died)
            table.setText(i, 9, plan + extren + amb + deny)

            total['plan'] += plan
            total['extren'] += extren
            total['OMS'] += OMS
            total['deny'] += deny
            total['amb'] += amb
            total['died'] += died

        i = table.addRow()
        table.setText(i, 0, u'Итого:',                                                      CReportBase.TableTotal)
        table.setText(i, 1, total['plan'] + total['extren'],                                CReportBase.TableTotal)
        table.setText(i, 2, total['plan'],                                                  CReportBase.TableTotal)
        table.setText(i, 3, total['extren'],                                                CReportBase.TableTotal)
        table.setText(i, 4, total['OMS'],                                                   CReportBase.TableTotal)
        table.setText(i, 5, total['amb'] + total['deny'],                                   CReportBase.TableTotal)
        table.setText(i, 6, total['amb'],                                                   CReportBase.TableTotal)
        table.setText(i, 7, total['deny'],                                                  CReportBase.TableTotal)
        table.setText(i, 8, total['died'],                                                  CReportBase.TableTotal)
        table.setText(i, 9, total['plan'] + total['extren'] + total['amb'] + total['deny'], CReportBase.TableTotal)

        return doc


class CReportPatientEntranceOrgStructureSetupDialog(QtGui.QDialog, Ui_PatientEntranceOrgStructureSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType')
        self.cmbFinanceType.setTable('rbFinance')
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime(8, 00)))
        self.edtEndTime.setTime(params.get('endTime', QtCore.QTime(7, 59)))
        self.cmbEventType.setValue(params.get('eventType'))
        self.cmbFinanceType.setValue(params.get('financeId'))
        self.cmbOrgStructure.setValue(params.get('orgStructure'))

    def params(self):
        result = {'begDate': self.edtBegDate.date(),
                  'endDate': self.edtEndDate.date(),
                  'begTime': self.edtBegTime.time(),
                  'endTime': self.edtEndTime.time(),
                  'eventType': self.cmbEventType.value(),
                  'financeId': self.cmbFinanceType.value(),
                  'orgStructure': self.cmbOrgStructure.value()
                  }
        return result
