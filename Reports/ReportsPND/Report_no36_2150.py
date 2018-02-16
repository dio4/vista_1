# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params):
    stmt = u'''
    SELECT (
SELECT COUNT(DISTINCT(s.client_id)) FROM (
    SELECT e.client_id, c.birthDate, c.sex
    FROM Event e
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    INNER JOIN ClientRemark cr ON c.id = cr.client_id
    INNER JOIN rbClientRemarkType crt ON crt.id = cr.remarkType_id
    WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND DATE(cr.date) >= DATE('%s') AND DATE(cr.date) <= DATE('%s')
    AND (crt.flatCode LIKE 'suicide' OR crt.flatCode LIKE 'suicideFinished')
    GROUP BY e.client_id
    )s ) disp_all,

(SELECT COUNT(DISTINCT(c.id)) FROM Event e
  INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    INNER JOIN ClientRemark cr ON c.id = cr.client_id
    INNER JOIN rbClientRemarkType crt ON crt.id = cr.remarkType_id
  WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND DATE(cr.date) >= DATE('%s') AND DATE(cr.date) <= DATE('%s')
    AND ((DATE(cm.endDate) >= DATE('%s') AND DATE(cm.endDate) <= DATE('%s')) OR (DATE(cm.endDate) IS NULL))
 # AND cm.endDate is NOT NULL
  AND (crt.flatCode LIKE 'suicideFinished')) disp_sicide_done,

  (
SELECT COUNT(s.client_id) FROM (
    SELECT e.client_id, c.birthDate, c.sex
    FROM Event e
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    INNER JOIN ClientRemark cr ON c.id = cr.client_id
    INNER JOIN rbClientRemarkType crt ON crt.id = cr.remarkType_id
    WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'К')
    AND DATE(cr.date) >= DATE('%s') AND DATE(cr.date) <= DATE('%s')
    AND ((DATE(cm.endDate) >= DATE('%s') AND DATE(cm.endDate) <= DATE('%s')) OR (DATE(cm.endDate) IS NULL))
    AND (crt.flatCode LIKE 'suicide' OR crt.flatCode LIKE 'suicideFinished')
    GROUP BY e.client_id
    )s ) kons_all,

(
  SELECT COUNT(DISTINCT(s.id)) FROM(
SELECT c.id FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    INNER JOIN ClientRemark cr ON c.id = cr.client_id
    INNER JOIN rbClientRemarkType crt ON crt.id = cr.remarkType_id
  WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'К')
    AND DATE(cr.date) >= DATE('%s') AND DATE(cr.date) <= DATE('%s')
    AND ((DATE(cm.endDate) >= DATE('%s') AND DATE(cm.endDate) <= DATE('%s')) OR (DATE(cm.endDate) IS NULL))
 # AND cm.endDate is NOT NULL
  AND crt.flatCode LIKE 'suicideFinished') s ) AS kons_sicide_done,

  (
 SELECT COUNT(s.tID) FROM(
   SELECT TempInvalid.id AS tID,
    DATEDIFF(TempInvalid.endDate, TempInvalid.caseBegDate)+1 AS duration

    FROM TempInvalid
    LEFT JOIN TempInvalid AS NextTempInvalid ON TempInvalid.id = NextTempInvalid.prev_id
    LEFT JOIN Diagnosis ON Diagnosis.id = TempInvalid.diagnosis_id
    LEFT JOIN Person ON Person.id = TempInvalid.person_id
    LEFT JOIN rbTempInvalidReason ON rbTempInvalidReason.id = TempInvalid.tempInvalidReason_id
    LEFT JOIN Client ON Client.id = TempInvalid.client_id
    WHERE NextTempInvalid.id IS NULL AND (TempInvalid.`type` = 0)
    and (Diagnosis.MKB LIKE 'F0%%' OR Diagnosis.MKB LIKE 'F2%%' OR Diagnosis.MKB LIKE 'F3%%'
    OR Diagnosis.MKB LIKE 'F4%%' OR Diagnosis.MKB LIKE 'F5%%' OR Diagnosis.MKB LIKE 'F6%%'
    OR Diagnosis.MKB LIKE 'F7%%' OR Diagnosis.MKB LIKE 'F8%%' OR Diagnosis.MKB LIKE 'F9%%')
    AND (TempInvalid.`deleted` = 0) AND (TempInvalid.`endDate` >= '%s')
    AND (TempInvalid.`endDate` < '%s') )s
 ) AS sluchaev,

  (
  SELECT SUM(s.duration) FROM(
   SELECT TempInvalid.id AS tID,
    DATEDIFF(TempInvalid.endDate, TempInvalid.caseBegDate)+1 AS duration

    FROM TempInvalid
    LEFT JOIN TempInvalid AS NextTempInvalid ON TempInvalid.id = NextTempInvalid.prev_id
    LEFT JOIN Diagnosis ON Diagnosis.id = TempInvalid.diagnosis_id
    LEFT JOIN Person ON Person.id = TempInvalid.person_id
    LEFT JOIN rbTempInvalidReason ON rbTempInvalidReason.id = TempInvalid.tempInvalidReason_id
    LEFT JOIN Client ON Client.id = TempInvalid.client_id
    WHERE NextTempInvalid.id IS NULL AND (TempInvalid.`type` = 0)
    and (Diagnosis.MKB LIKE 'F0%%' OR Diagnosis.MKB LIKE 'F2%%' OR Diagnosis.MKB LIKE 'F3%%'
    OR Diagnosis.MKB LIKE 'F4%%' OR Diagnosis.MKB LIKE 'F5%%' OR Diagnosis.MKB LIKE 'F6%%'
    OR Diagnosis.MKB LIKE 'F7%%' OR Diagnosis.MKB LIKE 'F8%%' OR Diagnosis.MKB LIKE 'F9%%')
    AND (TempInvalid.`deleted` = 0) AND (TempInvalid.`endDate` >= '%s')
    AND (TempInvalid.`endDate` < '%s') )s
) AS dnej
  ;

    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

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
            ('12%', [u'Из числа пациентов, находившихся под диспансерным наблюдением и получавших '
                     u'консультативно-лечебную помощь (стр. 1 гр. 8, 10 т. 2100 и 2110) в течение года - совершили '
                     u'суицидальные попытки'], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('6%', [u'Число случаев и дней нетрудоспособности у больных психическими расстройствами по '
                    u'закрытым листкам нетрудоспособности:'], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('10%', [u''], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        lst_scnd_row = [u'диспансерные пациенты', u'', u'пациенты, получавшие консультативно-лечебную помощь',
                        u'', u'', u'', u'из них у пациентов с заболеваниями, связанными с употреблением ПАВ', u'']
        lst_count = [0, 1, 2, 3, 4, 5, 6, 7]
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'всего', u'в т. ч. завершенные', u'всего',
                        u'в т. ч. завершенные', u'число случаев', u'число дней',
                        u'число случаев (из графы 5)', u'число дней (из графы 6)']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8']
        i = table.addRow()
        for j in range(0, len(lst_frth_row)):
            table.setText(i, lst_count[j], lst_frth_row[j])

        i = table.addRow()
        while query.next():
            record = query.record()
            table.setText(i, 0, forceString(record.value('disp_all')))
            table.setText(i, 1, forceString(record.value('disp_sicide_done')))
            table.setText(i, 2, forceString(record.value('kons_all')))
            table.setText(i, 3, forceString(record.value('kons_sicide_done')))
            table.setText(i, 4, forceString(record.value('sluchaev')))
            table.setText(i, 5, forceString(record.value('dnej')))
            table.setText(i, 6, forceString(record.value('')))
            table.setText(i, 7, forceString(record.value('')))

        self.merge_cells(table)
        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 0, 1, 4)  # first row, 1-4 columns
        table.mergeCells(0, 1, 1, 4)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(0, 4, 1, 4)  # first row, 5-8 columns
        table.mergeCells(0, 5, 1, 4)
        table.mergeCells(0, 6, 1, 4)
        table.mergeCells(0, 7, 1, 4)
        table.mergeCells(1, 0, 1, 2)  # first row, col 1,2
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 2, 1, 2)  # first row, col 3,4
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 6, 1, 2)  # first row, col 3,4
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 4, 2, 1)  # 2nd column, row 1,2
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(1, 5, 2, 1)  # 3d column, row 1,2
        table.mergeCells(2, 5, 2, 1)



def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147
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

    connectionInfo = {'driverName' : 'mysql',
                  'host' : '192.168.0.207',
                  'port' : 3306,
                  'database' : 'olyu_sochi2',
                  'user' : 'dbuser',
                  'password' : 'dbpassword',
                  'connectionName' : 'vista-med',
                  'compressData' : True,
                  'afterConnectFunc' : None}
    """
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