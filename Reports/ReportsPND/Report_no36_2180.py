# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params, query):
    stmt = u'''
SELECT  (
  SELECT COUNT(vsego.clid) FROM(
SELECT (e.client_id) as clid FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
WHERE (%s)
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
GROUP BY cd.client_id
HAVING COUNT(cd.client_id) = 1 # ako ima samo eden klient znaic deka prv pat taa godina stanal invalid
) vsego ) AS vsego,
  (
  SELECT COUNT(group3.clid) FROM(
  SELECT (e.client_id) as clid FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
  WHERE (%s)
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
    AND cd.groupNumber=3
GROUP BY cd.client_id
HAVING COUNT(cd.client_id) = 1 #aako ima samo eden klient znaic deka prv pat taa godina stanal invalid
) group3) AS group3,

    (
  SELECT SUM(do_17.all_diff_17) FROM(
  SELECT
     (((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <= 17) and
    (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 0) AS all_diff_17
  FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
WHERE (%s)
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
GROUP BY cd.client_id
HAVING COUNT(cd.client_id) = 1 #aako ima samo eden klient znaic deka prv pat taa godina stanal invalid
) do_17 ) AS do_17,
 (
  SELECT COUNT(vsego.clid) FROM(
SELECT (e.client_id) as clid FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
WHERE (%s)
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
GROUP BY cd.client_id
) vsego ) AS vsego_konec,
  (
  SELECT COUNT(group3.clid) FROM(
  SELECT (e.client_id) as clid FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
  WHERE (%s)
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
    AND cd.groupNumber=3
GROUP BY cd.client_id
) group3) AS group3_konec,

    (
  SELECT SUM(do_17.all_diff_17) FROM(
  SELECT
     (((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <= 17) and
    (YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) >= 0) AS all_diff_17
  FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
WHERE (%s)
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
GROUP BY cd.client_id
) do_17 ) AS do_17_konec
;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            query, begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))


class CReportReHospitalizationSetupDialog(QtGui.QDialog, Ui_ReportReHospitalizationSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CReportReHospitalization(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Контингенты больных, имеющих группу инвалидности")

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
            ('8%', [u'Число больных, впервые признанных инвалидами в отчетном году'], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u'Число больных, имевших группу инвалидности на конец отчетного года'], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        lst_MKB = [ u'', u'', u'', u'',
                    u'F00-F09, F20-F99',
                    u'F20, F21, F25, F3x.x4',
                    u'F22, F28, F29, F84.0-4',
                    u'F84.0-1',
                    u'F04.2, F0x.x2, F0x.xx2',
                    u'F70 - F79',
                    u'G30']

        lst_numbers = [u'', u'', u'', u'', u'1', u'2', u'3', u'4', u'5', u'6', u'7']

        lst_naimenovanie = [u'', u'', u'', u'',
                            u'Психические расстройства - всего',
                            u"из них: шизофрения, шизотипические расстройства, шизоаффективные психозы, \
                            аффективные психозы с неконгруэнтным аффекту бредом",
                            u"хронические неорганические психозы, детские психозы",
                            u"из них:детский аутизм, атипичный аутизм",
                            u"психические расстройства вследствие эпилепсии",
                            u"Умственная отсталость",
                            u"Кроме того, больные, имеющие инвалидность по общесоматическим заболеваниям"]

        lst_scnd_row = [u'', u'', u'', u'', u'из них:', u'',  u'', u'из них:', u'']
        lst_count = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'', u'', u'', u'всего', u'инвалидами III группы',  u'инвалидами (до 17 лет вкл.)',
                        u'всего', u'имевших III группу', u'инвалидов (до 17 лет вкл.)']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
        i = table.addRow()
        for j in range(0, len(lst_frth_row)):
            table.setText(i, lst_count[j], lst_frth_row[j])

        for i in range(0, 7):
            i = table.addRow()
            table.setText(i, 0, lst_naimenovanie[i])
            table.setText(i, 1, lst_MKB[i])
            table.setText(i, 2, lst_numbers[i])

        l = [['F0%%', 'F2%%', 'F3%%', 'F4%%', 'F5%%', 'F6%%', 'F7%%', 'F8%%', 'F9%%'],
             ['F20%%', 'F21%%', 'F25%%', 'F3%.%4'],
             ['F22%%', 'F28%%', 'F29%%', 'F84.0', 'F84.1', 'F84.2', 'F84.3', 'F84.4'],
             ['F84.0%%', 'F84.1%%'],
             ['F04.2', 'F0%.%2', 'F0%.%%2'],
             ['F70%%', 'F71%%', 'F72%%', 'F73%%', 'F74%%', 'F75%%', 'F76%%', 'F77%%', 'F78%%', 'F79%%'],
             ['G30%%']
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

                table.setText(ii + 4, 3, forceString(record.value('vsego')))
                table.setText(ii + 4, 4, forceString(record.value('group3')))
                table.setText(ii + 4, 5, forceString(record.value('do_17')))
                table.setText(ii + 4, 6, forceString(record.value('vsego_konec')))
                table.setText(ii + 4, 7, forceString(record.value('group3_konec')))
                table.setText(ii + 4, 8, forceString(record.value('do_17_konec')))

            ii = ii + 1

        self.merge_cells(table)

        return doc


    def merge_cells(self, table):
        table.mergeCells(0, 3, 1, 3)  # first row, 4,5,6 columns
        table.mergeCells(0, 4, 1, 3)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 6, 1, 3)  # first row, 7,8,9 columns
        table.mergeCells(0, 7, 1, 3)
        table.mergeCells(0, 8, 1, 3)
        table.mergeCells(1, 4, 1, 2)  # second row, 5,6 columns
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)  # second row, 8,9 columns
        table.mergeCells(1, 8, 1, 2)
        table.mergeCells(0, 2, 3, 1)  # third column, 0,1,2 rows
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(2, 2, 3, 1)
        table.mergeCells(0, 1, 3, 1)  # second column, 0,1,2 rows
        table.mergeCells(1, 1, 3, 1)
        table.mergeCells(2, 1, 3, 1)
        table.mergeCells(0, 0, 3, 1)  # first column, 0,1,2 rows
        table.mergeCells(1, 0, 3, 1)
        table.mergeCells(2, 0, 3, 1)
        table.mergeCells(1, 3, 2, 1)  # 4th column, 0,1,2 rows
        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(1, 6, 2, 1)  # 7th column, 0,1,2 rows
        table.mergeCells(2, 6, 2, 1)
        table.mergeCells(1, 3, 2, 1)  # 7th column, 0,1,2 rows
        table.mergeCells(2, 3, 2, 1)


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
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportReHospitalization(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()