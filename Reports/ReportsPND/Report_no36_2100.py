# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date


def selectData(params, query):
    stmt= u'''
     SELECT
  (SELECT COUNT(DISTINCT(ss.client_id)) FROM(
 SELECT e.id, cm.setDate, e.client_id
  FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON e.client_id = c.id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s)
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    GROUP BY e.client_id
  )ss
     WHERE DATE(ss.setDate) >= DATE('%s') AND DATE(ss.setDate) <= DATE('%s')
    ) AS otch_god,
     vpervye.sum_cl_id AS vsego,
     vpervye.diff_14 AS diff_14,
     vpervye.diff_17_15 AS diff_17_15,
  (SELECT COUNT(snjato.cl_id) FROM(
SELECT e.client_id AS cl_id
    FROM Event e
    INNER JOIN Client c ON e.client_id=c.id
    INNER JOIN ClientAttach ca ON ca.client_id = c.id
    INNER JOIN rbAttachType rbat ON ca.attachType_id = rbat.id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s)
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND DATE(cm.endDate) >= DATE('%s') AND DATE(cm.endDate) <= DATE('%s')
    AND (rbat.id = 7 OR rbat.id = 8)
    GROUP BY e.client_id
  ) snjato) AS snjato_vsego,

     (SELECT COUNT(*) FROM(
 SELECT chg.name, chg.client_id FROM (
    SELECT e.client_id AS client_id, cmk.name AS name
    FROM Event e
    INNER JOIN Client c ON e.client_id=c.id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s)
    AND (cmk.name LIKE 'К' OR cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND DATE(cm.setDate) >= DATE('%s') AND DATE(cm.setDate) <= DATE('%s')
    GROUP BY cmk.name, e.client_id
    ORDER BY e.client_id, cm.setDate) chg
    GROUP BY chg.client_id
    HAVING COUNT(chg.client_id) > 1
)chg2
  where (chg2.name LIKE 'Д' OR chg2.name LIKE 'АДЛ' OR chg2.name LIKE 'АПЛ')) snjato_chg,


    (SELECT COUNT(snjato.cl_id) FROM(
SELECT e.client_id AS cl_id
    FROM Event e
    INNER JOIN Client c ON e.client_id=c.id
    INNER JOIN ClientAttach ca ON ca.client_id = c.id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    INNER JOIN rbDetachmentReason dr ON ca.detachment_id = dr.id
    WHERE (%s)
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND DATE(cm.endDate) >= DATE('%s') AND DATE(cm.endDate) <= DATE('%s')
    AND (dr.id = 1)
    GROUP BY e.client_id
  ) snjato) AS vyzdorovlenie,

 (
    SELECT COUNT(s.client_id) FROM(
    SELECT e.id AS event_id, e.client_id
    FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s)
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ') AND (cm.endDate is null OR cm.endDate >= DATE('%s'))

    GROUP BY e.client_id
    )s
  ) AS all_this_year,

  (
    SELECT (SUM(s.all_diff_14)) AS e_id FROM(
    SELECT (((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <= 14) and
    (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 0) AS all_diff_14

    FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s)
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ') AND (cm.endDate is null OR cm.endDate >= DATE('%s'))

    GROUP BY e.client_id
    )s
  ) AS all_diff_14,

    (
    SELECT (SUM(s.all_diff_17_15)) AS e_id FROM(
    SELECT ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) < 18 and
    (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 15) AS all_diff_17_15

    FROM Event e
    #INNER JOIN EventType et ON et.id = e.eventType_id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s)
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ') AND (cm.endDate is null OR cm.endDate >= DATE('%s'))

    GROUP BY e.client_id
    )s
  ) AS all_diff_17_15,

  (SELECT COUNT(*) FROM(
 SELECT chg.name, chg.client_id, chg.setDate FROM (
    SELECT e.client_id AS client_id, cmk.name AS name, cm.setDate AS setDate
    FROM Event e
    INNER JOIN Client c ON e.client_id=c.id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s)
    AND (cmk.name LIKE 'К' OR cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND (DATE(cm.endDate) IS NULL or DATE(cm.endDate) >= DATE('%s'))
    GROUP BY cmk.name, e.client_id
    ORDER BY e.client_id, cm.setDate) chg
    GROUP BY chg.client_id
    HAVING COUNT(chg.client_id) > 1
)chg2
  where chg2.name LIKE 'К') col13


FROM
(
SELECT COUNT(DISTINCT(s.client_id)) AS sum_cl_id, SUM(s.diff_14) AS diff_14, SUM(s.diff_17_15) AS diff_17_15
  FROM(

 SELECT e.id, e.client_id AS client_id, e.setDate AS setDate, ds.setDate AS ds_setDate, cm.setDate AS cm_setDate,
(((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) < 15) and
(YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 0) AS diff_14,
((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <= 17 and
(YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 15) AS diff_17_15

    FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON e.client_id=c.id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (%s) AND
    (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    GROUP BY e.client_id, ds.MKB
    ORDER BY e.client_id, ds.setDate
)s
   WHERE DATE(s.ds_setDate) >= DATE('%s') AND DATE(s.ds_setDate) <= DATE('%s')
   AND DATE(s.cm_setDate) >= DATE('%s') AND DATE(s.cm_setDate ) <= DATE('%s')
) AS vpervye;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, endDate.toString('yyyy-MM-dd'),
                            query, endDate.toString('yyyy-MM-dd'),
                            query, endDate.toString('yyyy-MM-dd'),
                            query, endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

"""
def selected_date2(params, query):
    stmt = u'''
    SELECT e.client_id AS client_id, e.eventType_id AS eventType_id
        FROM Event e
        INNER JOIN Client c ON e.client_id=c.id
        INNER JOIN EventType et ON et.id = e.eventType_id
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
        WHERE (%s)
        AND (e.eventType_id = '6' OR e.eventType_id = '2' )
        AND DATE(e.setDate) >= DATE('%s')  AND DATE(e.setDate) <= DATE('%s')
        GROUP BY e.eventType_id, e.client_id
        #HAVING COUNT(e.client_id) > 1
        ORDER BY e.client_id, e.setDate
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

"""

class CReportReHospitalizationSetupDialog(QtGui.QDialog, Ui_ReportReHospitalizationSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(
            params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CReportReHospitalization(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Контингенты больных, находящихся под диспансерным наблюдением")

    def getSetupDialog(self, parent):
        result = CReportReHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('12%', [u'Наименование'], CReportBase.AlignLeft),
            ('8%', [u'Код по МКБ-10 (класс V, адаптированный для использования в РФ)'], CReportBase.AlignLeft),
            ('3%', [u'№ строки'], CReportBase.AlignLeft),
            ('8%', [u'Взято под наблюдение в отчетном году'], CReportBase.AlignLeft),
            ('8%', [u'из них с впервые в жизни установленным диагнозом'], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('8%', [u'Снято с наблюдения в отчетном году'], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('8%', [u'Состоит под наблюдением больных на конец отчетного года'], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('15%', [u'Из числа пациентов, показанных в гр.10, переведено в течение года из группы пациентов,\
             получавших консультативно-лечебную помощь'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        #
        # first column
        #
        lst_naimenovanie = [u'', u'', u'', u'',
                            u'Психические расстройства - всего',
                            u"Психозы и (или) состояния слабоумия",
                            u"из них: шизофрения, шизотипические расстройства, шизоаффективные психозы, \
                            аффективные психозы с неконгруэнтным аффекту бредом",
                            u"детский аутизм, атипичный аутизм",
                            u"Психические расстройства непсихотического характера",
                            u"из них синдром Аспергера",
                            u"Умственная отсталость",
                            u"Психические расстройства, классифицированные  в других рубриках МКБ-10"]
        #
        # second column
        #
        lst_MKB = [u'', u'', u'', u'',
                   u'F00-F09, F20-F99',
                   u'F00-F05, F06 (часть), F09, F20-F25, F28, F29, F84.0-4, F30-F39(часть)',
                   u'F20, F21, F25,F3x.x4',
                   u'F84.0-1',
                   u'F06(часть), F07, F30-F39(часть), F40-F69, F80-F83, F84.5, F90-F98',
                   u'F84.5',
                   u'F70 - F79',
                   u'A52.1, A81.0, B22.0, G10-G40 и др.']
        #
        # third column
        #
        lst_numbers = [u'', u'', u'', u'', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8']

        #
        # second row
        #
        lst_scnd_row = [u'', u'', u'', u'', u'', u'', u'из них детей:', u'всего',
                        u'из них в связи с выздоровлением или стойким улучшением',
                        u'', u'из них детей:', u'', u'']
        lst_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        i = table.addRow()
        for j in range(0, 13):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'', u'', u'', u'', u'всего', u'до 14 лет включительно', u'15-17 лет', u'',
                        u'', u'всего', u'до 14 лет включительно', u'15-17 лет', u'']
        i = table.addRow()
        for j in range(0, 13):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12', u'13']

        i = table.addRow()
        for j in range(0, 13):
            table.setText(i, lst_count[j], lst_frth_row[j])

        for i in range(0, 8):
            i = table.addRow()
            table.setText(i, 0, lst_naimenovanie[i])
            table.setText(i, 1, lst_MKB[i])
            table.setText(i, 2, lst_numbers[i])

        #
        # MKB
        #
        l = [['F0%%', 'F2%%', 'F3%%', 'F4%%', 'F5%%', 'F6%%', 'F7%%', 'F8%%', 'F9%%'],
             ['F00%%', 'F01%%', 'F02%%', 'F03%%', 'F04%%', 'F05%%', 'F06%%', 'F09%%', 'F20%%','F21%%', 'F22%%', 'F23%%', 'F24%%', 'F25%%',
              'F28%%', 'F29%%', 'F84.0%%', 'F84.1%%', 'F84.2%%','F84.3%%','F84.4%%',
              'F30%%', 'F31%%', 'F32%%', 'F33%%', 'F34%%', 'F35%%', 'F36%%', 'F37%%', 'F38%%', 'F39%%'],
             ['F20%%', 'F21%%', 'F25%%', 'F3%.%4'],
             ['F84.0%%', 'F84.1%%'],
             ['F06%%', 'F07%%', 'F30%%', 'F31%%', 'F32%%', 'F33%%', 'F34%%', 'F35%%', 'F36%%', 'F37%%', 'F38%%', 'F39%%'
              'F40%%', 'F41%%', 'F42%%', 'F43%%', 'F44%%','F45%%', 'F46%%', 'F47%%','F48%%','F49%%',
              'F50%%', 'F51%%', 'F52%%', 'F53%%', 'F54%%', 'F55%%', 'F56%%', 'F57%%', 'F58%%', 'F59%%',
              'F60%%', 'F61%%', 'F62%%', 'F63%%', 'F64%%', 'F65%%', 'F66%%', 'F67%%', 'F68%%', 'F69%%',
              'F80%%', 'F81%%', 'F82%%', 'F83%%', 'F84.5%%', 'F90%%', 'F91%%', 'F92%%', 'F93%%', 'F94%%',
              'F95%%', 'F96%%', 'F97%%', 'F98%%'],
             ['F84.5%'],
             ['F70%%', 'F71%%', 'F72%%', 'F73%%', 'F74%%', 'F75%%', 'F76%%', 'F77%%', 'F78%%', 'F79%%'],
             ['A52.1%%', 'A81.0%%', 'B22.0%%',
              'G10%%', 'G11%%', 'G12%%', 'G13%%', 'G14%%', 'G15%%', 'G16%%', 'G17%%', 'G18%%', 'G19%%',
              'G20%%', 'G21%%', 'G22%%', 'G23%%', 'G24%%', 'G25%%', 'G26%%', 'G27%%', 'G28%%', 'G29%%',
              'G30%%', 'G31%%', 'G32%%', 'G33%%', 'G34%%', 'G35%%', 'G36%%', 'G37%%', 'G38%%', 'G39%%', 'G40%%']
             ]

        ii = 0

        for j in range(0, len(l)):
            query_str = u''
            for f in l[j]:
                query_str += u"ds.MKB LIKE '%s' OR " % f
            query_str = query_str[:-4]

            query = selectData(params, query_str)
            self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

            while query.next():
                record = query.record()
                val_col_8 = int(forceString(record.value('snjato_vsego'))) + int(forceString(record.value('snjato_chg')))
                if ii != 5:
                    table.setText(ii + 4, 3, forceString(record.value('otch_god')))
                    table.setText(ii + 4, 4, forceString(record.value('vsego')))
                    table.setText(ii + 4, 5, forceString(record.value('diff_14')))
                    table.setText(ii + 4, 6, forceString(record.value('diff_17_15')))
                    table.setText(ii + 4, 7, forceString(record.value('snjato_vsego')))
                    table.setText(ii + 4, 8, forceString(record.value('vyzdorovlenie')))
                    table.setText(ii + 4, 9, forceString(record.value('all_this_year')))
                    table.setText(ii + 4, 10, forceString(record.value('all_diff_14')))
                    table.setText(ii + 4, 11, forceString(record.value('all_diff_17_15')))
                    table.setText(ii + 4, 12, forceString(record.value('col13')))
                else:
                    table.setText(ii + 4, 7, forceString(record.value('snjato_vsego')))
                    table.setText(ii + 4, 8, forceString(record.value('vyzdorovlenie')))
                    table.setText(ii + 4, 9, forceString(record.value('all_this_year')))
                    table.setText(ii + 4, 10, forceString(record.value('all_diff_14')))
                    table.setText(ii + 4, 11, forceString(record.value('all_diff_17_15')))

            ii = ii + 1

            self.merge_cells(table)

        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 4, 1, 3)  # first row, 5,6,7 columns
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 6, 1, 3)
        table.mergeCells(1, 5, 1, 2)  # first row, 5,6 columns
        table.mergeCells(1, 6, 1, 2)
        table.mergeCells(0, 7, 1, 2)  # first row, 8,9 columns
        table.mergeCells(0, 8, 1, 2)
        table.mergeCells(0, 9, 1, 3)  # first row, 10,11,12 columns
        table.mergeCells(0, 10, 1, 3)
        table.mergeCells(0, 11, 1, 3)
        table.mergeCells(1, 10, 1, 2)  # first row, 10,11 columns
        table.mergeCells(1, 11, 1, 2)

        table.mergeCells(0, 0, 3, 1)  # first column, 0,1,2 rows
        table.mergeCells(1, 0, 3, 1)
        table.mergeCells(2, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)  # second column, 0,1,2 rows
        table.mergeCells(1, 1, 3, 1)
        table.mergeCells(2, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)  # third column, 0,1,2 rows
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(2, 2, 3, 1)
        table.mergeCells(0, 3, 3, 1)  # forth column, 0,1,2 rows
        table.mergeCells(1, 3, 3, 1)
        table.mergeCells(2, 3, 3, 1)
        table.mergeCells(0, 12, 3, 1)  # 13th column, 0,1,2 rows
        table.mergeCells(1, 12, 3, 1)
        table.mergeCells(2, 12, 3, 1)
        table.mergeCells(1, 4, 2, 1)  # 7th column, 0,1,2 rows
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(1, 9, 2, 1)  # 7th column, 0,1,2 rows
        table.mergeCells(2, 9, 2, 1)
        table.mergeCells(1, 7, 2, 1)  # 8th column, 0,1,2 rows
        table.mergeCells(2, 7, 2, 1)
        table.mergeCells(1, 8, 2, 1)  # 9th column, 0,1,2 rows
        table.mergeCells(2, 8, 2, 1)

def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.3',
                      'port' : 3306,
                      'database' : 'pnd5',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    """
    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'pes',
                      'port' : 3306,
                      'database' : 's12',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}

    connectionInfo = {'driverName': 'mysql',
                      'host': '192.168.0.207',
                      'port': 3306,
                      'database': 'olyu_sochi2',
                      'user': 'dbuser',
                      'password': 'dbpassword',
                      'connectionName': 'vista-med',
                      'compressData': True,
                      'afterConnectFunc': None}
    """

    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportReHospitalization(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

"""
    stmt2 = u'''
        SELECT
      (SELECT COUNT(DISTINCT(ss.client_id))
        FROM(
        SELECT e.id, e.client_id AS client_id, e.setDate AS setDate, ds.setDate AS ds_setDate
        FROM Event e
        INNER JOIN EventType et ON et.id = e.eventType_id
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
        WHERE (%s)
        AND (et.form LIKE '%%025%%' OR et.form LIKE '%%030%%')
        AND e.eventType_id = '2'
        GROUP BY e.client_id
        ORDER BY e.client_id, e.setDate
    )ss
       WHERE DATE(ss.setDate) >= DATE('%s')  AND DATE(ss.setDate) <= DATE('%s')
        ) AS otch_god,
          vpervye.sum_cl_id AS vsego,
          vpervye.diff_14 AS diff_14,
          vpervye.diff_17_15 AS diff_17_15,
      (SELECT COUNT(snjato.cl_id) FROM(
    SELECT e.client_id AS cl_id
        FROM Event e
        INNER JOIN Client c ON e.client_id=c.id
        INNER JOIN ClientAttach ca ON ca.client_id = c.id
        INNER JOIN rbAttachType rbat ON ca.attachType_id = rbat.id
        INNER JOIN EventType et ON et.id = e.eventType_id
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
        WHERE (%s)
        AND e.eventType_id = '2'
        AND (et.form LIKE '%%025%%' OR et.form LIKE '%%030%%')
        AND ca.deleted = 1
        AND (rbat.id = 7 OR rbat.id = 8)
        AND DATE(ca.endDate) >= DATE('%s')  AND DATE(ca.endDate) <= DATE('%s')
        GROUP BY e.client_id
        ORDER BY e.client_id, ds.setDate
      ) snjato) AS snjato_vsego,

     (
        SELECT COUNT(s.event_id) FROM(
        SELECT e.id AS event_id
        FROM Event e
        INNER JOIN EventType et ON et.id = e.eventType_id
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
        INNER JOIN Client c ON c.id = e.client_id
        WHERE (%s)
        AND e.eventType_id = '2'
        AND (et.form LIKE '%%025%%' OR et.form LIKE '%%030%%')
        AND DATE(e.setDate) >= DATE('%s') AND DATE(e.setDate) <= DATE('%s')
        GROUP BY e.client_id
        )s
      ) AS all_this_year,

      (
        SELECT (SUM(s.all_diff_14)) AS e_id FROM(
        SELECT (((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <= 14) and
        (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 0) AS all_diff_14

        FROM Event e
        INNER JOIN EventType et ON et.id = e.eventType_id
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
        INNER JOIN Client c ON c.id = e.client_id
        WHERE (%s)
        AND e.eventType_id = '2'
        AND (et.form LIKE '%%025%%' OR et.form LIKE '%%030%%')
        AND DATE(e.setDate) >= DATE('%s') AND DATE(e.setDate) <= DATE('%s')
        GROUP BY e.client_id
        )s
      ) AS all_diff_14,

        (
        SELECT (SUM(s.all_diff_17_15)) AS e_id FROM(
        SELECT ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) < 18 and
        (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 15) AS all_diff_17_15

        FROM Event e
        INNER JOIN EventType et ON et.id = e.eventType_id
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
        INNER JOIN Client c ON c.id = e.client_id
        WHERE (%s)
        AND e.eventType_id = '2'
        AND (et.form LIKE '%%025%%' OR et.form LIKE '%%030%%')
        AND DATE(e.setDate) >= DATE('%s') AND DATE(e.setDate) <= DATE('%s')
        GROUP BY e.client_id
        )s
      ) AS all_diff_17_15


    FROM
    (
    SELECT COUNT(DISTINCT(s.client_id)) AS sum_cl_id, SUM(s.diff_14) AS diff_14, SUM(s.diff_17_15) AS diff_17_15
      FROM(
        SELECT e.id, e.client_id AS client_id, e.setDate AS setDate, ds.setDate AS ds_setDate,
     (((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) < 15) and
    (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 0) AS diff_14,
    ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <= 17 and
    (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 15) AS diff_17_15

        FROM Event e
        INNER JOIN Client c ON e.client_id=c.id
        INNER JOIN EventType et ON et.id = e.eventType_id
        INNER JOIN Diagnostic d ON d.event_id = e.id
        INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
        WHERE (%s)
        AND (et.form LIKE '%%025%%' OR et.form LIKE '%%030%%')
        AND e.eventType_id = '2'
        GROUP BY e.client_id
        ORDER BY e.client_id, ds.setDate
    )s
       WHERE DATE(s.ds_setDate) >= DATE('%s')  AND DATE(s.ds_setDate) <= DATE('%s')
    ) AS vpervye
     ;
        '''
"""