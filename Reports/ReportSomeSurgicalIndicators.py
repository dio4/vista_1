# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceInt, forceString, TableColIndex, TableRecord
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportSomeSurgicalIndicators import Ui_ReportSurgicalIndicators

def getData(params, lstOrgStructure, mainTable=True):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId')
    cmbOrgStructure = params.get('cmbOrgStructure')
    tableAction = db.table('Action').alias('a')
    condDate = [tableAction['endDate'].dateGe(begDate),
            tableAction['endDate'].dateLe(endDate)]

    tableOrgStructure = db.table('OrgStructure').alias('os')
    condOrgStructure = ''
    if lstOrgStructure and cmbOrgStructure:
        condOrgStructure = 'AND ' + tableOrgStructure['id'].inlist(lstOrgStructure)
    elif orgStructureId and not cmbOrgStructure:
        condOrgStructure = 'AND ' + tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId))
    cond = {'condDate': db.joinAnd(condDate),
            'condOrgStructure': condOrgStructure}
    if mainTable:
        stmtCreateTempTables = u'''
DROP TEMPORARY TABLE IF EXISTS temp_operation_actions;
CREATE TEMPORARY TABLE IF NOT EXISTS temp_operation_actions (INDEX(a_id), INDEX(e_id))
  ENGINE = MEMORY AS (
        SELECT DISTINCT a.id AS a_id, e_helper.id AS e_id
         FROM Event e_helper
            INNER JOIN Action a_leaved ON e_helper.id = a_leaved.event_id
            INNER JOIN ActionType at_leaved ON a_leaved.actionType_id = at_leaved.id
            INNER JOIN Action a_moving ON e_helper.id = a_moving.event_id
            INNER JOIN ActionType at_moving ON at_moving.id = a_moving.actionType_id
            INNER JOIN Action a ON a.event_id = e_helper.id
            INNER JOIN ActionType at ON a.actionType_id = at.id
        WHERE at_leaved.flatCode = "leaved" AND at_moving.flatCode = "moving"
        AND at.serviceType = 4
            AND a_leaved.deleted = 0 AND at_leaved.deleted = 0
            AND a_moving.deleted = 0 AND at_moving.deleted = 0
            AND (a.begDate BETWEEN a_moving.begDate AND a_moving.endDate)
            AND (a.endDate BETWEEN a_moving.begDate AND a_moving.endDate)
            AND %(condDate)s
);

DROP TABLE IF EXISTS temp_valid_operation_actions;
CREATE TABLE IF NOT EXISTS temp_valid_operation_actions
ENGINE = MEMORY AS (
    SELECT a.id AS actId,
        os.name AS org,
        at.name AS operName,
        e.client_id,
        a.isUrgent,
        IF(aps.value, 1, 0) AS sequalae,
        IF(aps.value AND a.isUrgent, 1, 0) AS pws,
        IF(r.regionalCode IN (5, 11), 1, 0) AS death,
        IF(r.regionalCode IN (5, 11) AND a.isUrgent = 0, 1, 0) AS pDeath,
        IFNULL(TO_DAYS(a.endDate) - TO_DAYS(e.setDate), 0) AS daysBefore,
        IF(a.isUrgent = 0, TO_DAYS(a.endDate) - TO_DAYS(e.setDate), 0) AS pDaysBefore,
        IFNULL(TO_DAYS(e.execDate) - TO_DAYS(a.endDate), 0) AS daysAfter,
        IF(a.isUrgent = 0, TO_DAYS(e.execDate) - TO_DAYS(a.endDate), 0) AS pDaysAfter,
        IFNULL(TO_DAYS(e.execDate) - TO_DAYS(e.setDate), 0) AS daysTotal,
        IF(a.isUrgent = 0, TO_DAYS(e.execDate) - TO_DAYS(e.setDate), 0) AS pDaysTotal
    FROM Event e
        INNER JOIN temp_operation_actions helper ON helper.e_id = e.id
        INNER JOIN Action a ON e.id = a.event_id AND helper.a_id = a.id
        INNER JOIN ActionType at ON at.id = a.actionType_id
        LEFT JOIN rbResult r ON e.result_id = r.id
        LEFT JOIN vrbPersonWithSpeciality p ON a.person_id = p.id
        LEFT JOIN OrgStructure os ON os.id = p.orgStructure_id AND os.deleted = 0
        LEFT JOIN (ActionProperty ap INNER JOIN    ActionPropertyType apt
                     ON ap.type_id = apt.id AND apt.name IN ("Осложнение", "Осложнения")
                                     AND ap.deleted = 0 AND apt.deleted = 0
                   INNER JOIN ActionProperty_String AS aps
                     ON aps.id = ap.id AND TRIM(aps.value) NOT IN ("", "нет")
                 ) ON a.id = ap.action_id
    WHERE at.serviceType = 4
        AND a.deleted = 0 AND at.deleted = 0
        AND %(condDate)s %(condOrgStructure)s);
ALTER TABLE temp_valid_operation_actions ADD INDEX `actId`(actId);
''' % cond
        createTempTablesQuery = db.query(stmtCreateTempTables)
        createTempTablesQueryString = forceString(createTempTablesQuery.lastQuery())
        stmtSelectValidRecords = u'''
SELECT org, operName,
    COUNT(DISTINCT client_id) AS clientsTotal,
    SUM(1 - isUrgent) AS clientsPlanned,
    SUM(sequalae) AS sequalae,
    SUM(pws) AS pws,
    SUM(death) AS death,
    SUM(pDeath) AS pDeath,
    SUM(daysBefore) AS daysBefore,
    SUM(pDaysBefore) AS pDaysBefore,
    SUM(daysAfter) AS daysAfter,
    SUM(pDaysAfter) AS pDaysAfter,
    SUM(daysTotal) AS daysTotal,
    SUM(pDaysTotal) AS pDaysTotal
FROM temp_valid_operation_actions t
GROUP BY org, operName WITH ROLLUP;
'''
        selectValidRecordsQuery = db.query(stmtSelectValidRecords)
        selectValidRecordsQueryString = forceString(selectValidRecordsQuery.lastQuery())
        return selectValidRecordsQuery, u'{0}\n{1}'.format(createTempTablesQueryString,
                                                   selectValidRecordsQueryString)
    else:
        stmtSelectBadRecords = u'''
SELECT
	t1.clientName,
	t1.personName,
	t1.operName,
	t1.endDate,
	t1.planned,
	t1.death,
	t1.daysBefore,
	t1.daysAfter,
	t1.daysTotal
FROM (
   SELECT
      CONCAT_WS(' ', c.lastName, c.firstName, c.patrName) AS clientName,
      p.name AS personName,
      a.endDate,
      a.id AS actId,
      at.name AS operName,
      IF(a.isUrgent = 0, "да", "нет") AS planned,
      IFNULL(aps.value, "нет") AS sequalae,
      IF(aps.value AND a.isUrgent, 1, 0) AS pws,
      IF(r.regionalCode IN (5, 11), "да", "нет") AS death,
      IFNULL(TO_DAYS(a.endDate) - TO_DAYS(e.setDate), 0) AS daysBefore,
      IFNULL(TO_DAYS(e.execDate) - TO_DAYS(a.endDate), 0) AS daysAfter,
      IFNULL(TO_DAYS(e.execDate) - TO_DAYS(e.setDate), 0) AS daysTotal
   FROM Event e
      INNER JOIN Client c ON c.id = e.client_id
      INNER JOIN (
            Action a_helper
            INNER JOIN ActionType at_helper ON a_helper.actionType_id = at_helper.id
                AND at_helper.flatCode = "leaved" AND at_helper.deleted = 0
        )    ON a_helper.event_id = e.id    AND a_helper.deleted = 0
        INNER JOIN Action a ON e.id = a.event_id
        INNER JOIN ActionType at ON a.actionType_id = at.id
        LEFT JOIN rbResult r ON e.result_id = r.id
        LEFT JOIN vrbPerson p ON a.person_id = p.id
        LEFT JOIN OrgStructure os ON os.id = p.orgStructure_id AND os.deleted = 0
        LEFT JOIN (ActionProperty ap INNER JOIN    ActionPropertyType apt
                 ON ap.type_id = apt.id AND apt.name IN ("Осложнение", "Осложнения")
                             AND ap.deleted = 0 AND apt.deleted = 0
                 INNER JOIN ActionProperty_String AS aps
                 ON aps.id = ap.id AND TRIM(aps.value) NOT IN ("", "нет")
                 ) ON a.id = ap.action_id

    WHERE at.serviceType = 4
        AND a.deleted = 0 AND at.deleted = 0
        AND %(condDate)s %(condOrgStructure)s
 ) t1  LEFT JOIN temp_valid_operation_actions t2 ON t1.actId = t2.actId
 WHERE t2.actId IS NULL;
''' % cond
        selectBadRecordsQuery = db.query(stmtSelectBadRecords)
        selectBadRecordsQueryString = forceString(selectBadRecordsQuery.lastQuery())
        stmtRemoveTempTables = u'''
DROP TEMPORARY TABLE IF EXISTS temp_operation_actions;
DROP TABLE IF EXISTS temp_valid_operation_actions;
'''
    db.query(stmtRemoveTempTables)
    return selectBadRecordsQuery, u'{0}\n{1}'.format(selectBadRecordsQueryString, stmtRemoveTempTables)

def fillRow(table, row, tabColIndex, valuesDict, decoration=CReportBase.TableBody, excludeCols=None):
        if excludeCols is None:
            excludeCols = []
        for key, value in valuesDict._record.iteritems():
            if key not in excludeCols:
                table.setText(row, getattr(tabColIndex, key), value, decoration)

class CReportSomeSurgicalIndicators(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Некоторые показатели хирургической деятельности')

    def getSetupDialog(self, parent):
        result = CSomeSurgicalIndicators(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        db = QtGui.qApp.db
        db.transaction()
        try:
            validRecordsQuery, validRecordsQueryText = getData(params, lstOrgStructure)
            db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '10%', [u'Отделение'               ], CReportBase.AlignLeft),
            ( '20%', [u'Название операции'       ], CReportBase.AlignRight),
            ( ' 5%', [u'Оперировано', u'Всего'   ], CReportBase.AlignLeft),
            ( ' 5%', [u'', u'С план. операц.'    ], CReportBase.AlignLeft),
            ( ' 5%', [u'Послеопер. осл', u'Всего'], CReportBase.AlignLeft),
            ( ' 5%', [u'', u'С план. операц.'    ], CReportBase.AlignLeft),
            ( ' 5%', [u'Умерло оперир', u'Всего' ], CReportBase.AlignLeft),
            ( ' 5%', [u'', u'С план. операц.'    ], CReportBase.AlignLeft),
            ( ' 5%', [u'Дооперац. к/д', u'Всего' ], CReportBase.AlignLeft),
            ( ' 5%', [u'', u'С план. операц.'    ], CReportBase.AlignLeft),
            ( ' 5%', [u'Послеоп. к/д', u'Всего'  ], CReportBase.AlignLeft),
            ( ' 5%', [u'', u'С план. операц.'    ], CReportBase.AlignLeft),
            ( ' 5%', [u'Общий к/д', u'Всего'     ], CReportBase.AlignLeft),
            ( ' 5%', [u'', u'С план. операц.'    ], CReportBase.AlignLeft)
        ]
        tabCol = TableColIndex()
        cols = ['org', 'operName',
                'clientsTotal', 'clientsPlanned',
                'sequalae', 'pws',
                'death', 'pDeath',
                'daysBefore', 'pDaysBefore',
                'daysAfter', 'pDaysAfter',
                'daysTotal', 'pDaysTotal']
        tabCol.addColumns(cols)
        recordValues = TableRecord(cols, [forceString]*2 + [forceInt]*12)
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, tabCol.org, 2, 1)
        table.mergeCells(0, tabCol.operName, 2, 1)
        for colIndex in xrange(tabCol.clientsTotal, len(tabCol), 2):
            table.mergeCells(0, colIndex, 1, 2)
        prevOrg = None
        rowGroupIndex = 2
        rowIndex = 2
        while validRecordsQuery.next():
            record = validRecordsQuery.record()
            recordValues.extractFields(record)
            row = table.addRow()
            if recordValues['operName']:
                fontDecoration = CReportBase.TableBody
            else:
                fontDecoration = CReportBase.TableTotal
                if recordValues['org'] or prevOrg == '':
                    recordValues['operName'] = u'Итого:'
                    table.setText(rowGroupIndex, tabCol.org,  recordValues['org'])
                    table.mergeCells(rowGroupIndex, tabCol.org, rowIndex - rowGroupIndex + 1, 1)
                    rowGroupIndex = rowIndex + 1
                else:
                    table.setText(row, tabCol.org, u'Итого: ', fontDecoration)
                    table.mergeCells(row, tabCol.org, 1, 2)
            fillRow(table, row, tabCol, recordValues, fontDecoration, excludeCols=['org'])
            prevOrg = recordValues['org']
            rowIndex += 1

        badRecordsQuery, badRecordsQueryText = getData(params, lstOrgStructure, False)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Отделение не определено или данные внесены с ошибкой')
        cursor.insertBlock()
        tableColumns = [
            ('15%', [u'Пациент'          ], CReportBase.AlignLeft),
            ('15%', [u'Лечащий врач'     ], CReportBase.AlignRight),
            ('10%', [u'Название операции'], CReportBase.AlignLeft),
            ('10%', [u'Дата'             ], CReportBase.AlignLeft),
            ('10%', [u'Запланирована'    ], CReportBase.AlignLeft),
            ('10%', [u'Осложнения'       ], CReportBase.AlignLeft),
            ('10%', [u'Лет. исход'       ], CReportBase.AlignLeft),
            ( '5%', [u'Дооперац. к/д'    ], CReportBase.AlignLeft),
            ( '5%', [u'Послеоп. к/д'     ], CReportBase.AlignLeft),
            ( '5%', [u'Общий к/д'        ], CReportBase.AlignLeft)
        ]
        tabCol = TableColIndex()
        cols = ['clientName', 'personName',
                'operName', 'endDate',
                'planned', 'sequalae', 'death',
                'daysBefore', 'daysAfter', 'daysTotal'
                ]
        tabCol.addColumns(cols)
        recordValues = TableRecord(cols, [forceString] * 7 + [forceInt] * 3)
        table = createTable(cursor, tableColumns)

        while badRecordsQuery.next():
            record = badRecordsQuery.record()
            recordValues.extractFields(record)
            row = table.addRow()
            fontDecoration = CReportBase.TableBody
            fillRow(table, row, tabCol, recordValues, fontDecoration)
        self.setQueryText(u'{0}\n{1}'.format(validRecordsQueryText, badRecordsQueryText))
        return doc

class CSomeSurgicalIndicators(QtGui.QDialog, Ui_ReportSurgicalIndicators):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstOrgStructure.setTable('OrgStructure')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkOrgStructure.setChecked(params.get('cmbOrgStructure', False))
        self.on_chkOrgStructure_clicked(self.chkOrgStructure.isChecked())

    def params(self):
        result = {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'lstOrgStructure': self.lstOrgStructure.nameValues(),
            'cmbOrgStructure': self.chkOrgStructure.isChecked()
        }
        return result

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)
