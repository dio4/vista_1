
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params):
    stmt=u'''
    SELECT
  (
SELECT COUNT(s.client_id) FROM (
    SELECT e.client_id, c.birthDate, c.sex
    FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'К' OR cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ') AND (cm.endDate is null OR cm.endDate >= DATE('%s'))
    AND ((c.sex = 1 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <=59)) #male
              OR (c.sex = 2 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <=54)))

    GROUP BY e.client_id
    )s) working_age,
  (
  SELECT COUNT(s.client_id) FROM(
    SELECT e.client_id FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    INNER JOIN ClientWork cw ON c.id = cw.client_id
    WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'К' OR cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND (cm.endDate is null OR cm.endDate >= DATE('%s'))
    AND (cw.freeInput <> "" OR cw.org_id <> "")
    GROUP BY e.client_id
  ) s ) currently_working,

    (
  SELECT COUNT(s.client_id) FROM(
    SELECT e.client_id FROM Event e
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN Client c ON c.id = e.client_id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    INNER JOIN ClientWork cw ON c.id = cw.client_id
    WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'К' OR cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND (cm.endDate is null OR cm.endDate >= DATE('%s'))
    AND (cw.freeInput <> "" OR cw.org_id <> "")
    AND ((c.sex = 1 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <=59)) #male
    OR (c.sex = 2 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <=54)))

    GROUP BY e.client_id
  ) s ) currently_working_age,

 (SELECT COUNT(snjato.cl_id) FROM(
    SELECT e.client_id AS cl_id
    FROM Event e
    INNER JOIN Client c ON e.client_id=c.id
    INNER JOIN ClientAttach ca ON ca.client_id = c.id
    #INNER JOIN rbDetachmentReason dr ON ca.detachment_id = dr.id
    INNER JOIN Diagnostic d ON d.event_id = e.id
    INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
    INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
    INNER JOIN rbAttachType rbat ON ca.attachType_id = rbat.id
    INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
    WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
    AND DATE(cm.endDate) >= DATE('%s') AND DATE(cm.endDate) <= DATE('%s')
    #AND (dr.id = 9)
    AND rbat.id = 8
    GROUP BY e.client_id
  ) snjato) AS snjato_umerlo
;
    '''


    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (endDate.toString('yyyy-MM-dd'),
                            endDate.toString('yyyy-MM-dd'),
                            endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'))
                    )

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
            ('10%', [u'Из числа больных, находившихся под диспансерным наблюдением и получавших'
                     u'консультативно-лечебную помощь на конец года (стр. 1 гр. 10 т. 2100 и 2110)'], CReportBase.AlignLeft),
            ('10%', [u''], CReportBase.AlignLeft),
            ('10%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('12%', [u''], CReportBase.AlignLeft),
            ('8%', [u'Из числа снятых с диспансерного наблюдения (стр.1, гр.8, т.2100)'], CReportBase.AlignLeft),
            ('12%', [u''], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        lst_scnd_row = [u'получили курс лечения/реабилитации бригадным методом', u'лиц трудоспособного возраста',
                        u'работающих', u'', u'находится под опекой', u'умерло',
                        u'в том числе непосредственно от псих. заболеваний(коды F00-F09, F20-99)']
        lst_count = [0, 1, 2, 3, 4, 5, 6]
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'', u'', u'всего',
                        u'из них в трудоспособном возрасте (из гр.3)', u'', u'', u'']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7']
        i = table.addRow()
        for j in range(0, len(lst_frth_row)):
            table.setText(i, lst_count[j], lst_frth_row[j])

        i = table.addRow()
        query.next()
        record = query.record()
        table.setText(i, 0, forceString(record.value('')))
        table.setText(i, 1, forceString(record.value('working_age')))
        table.setText(i, 2, forceString(record.value('currently_working')))
        table.setText(i, 3, forceString(record.value('currently_working_age')))
        table.setText(i, 4, forceString(record.value('')))
        table.setText(i, 5, forceString(record.value('snjato_umerlo')))
        table.setText(i, 6, forceString(record.value('')))

        self.merge_cells(table)

        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 0, 1, 5)  # first row, 1-6 columns
        table.mergeCells(0, 1, 1, 5)
        table.mergeCells(0, 2, 1, 5)
        table.mergeCells(0, 3, 1, 5)
        table.mergeCells(0, 4, 1, 5)
        table.mergeCells(0, 5, 1, 2)  # first row, 6, 7 columns
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(1, 2, 1, 2)  # first row, col 2,3
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 0, 2, 1)  # 2nd column, row 1,2
        table.mergeCells(2, 0, 2, 1)
        table.mergeCells(1, 1, 2, 1)  # 3d column, row 1,2
        table.mergeCells(2, 1, 2, 1)
        table.mergeCells(1, 4, 2, 1)  # 5th column, row 1,2
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(1, 5, 2, 1)  # 6th column, row 1,2
        table.mergeCells(2, 5, 2, 1)
        table.mergeCells(1, 6, 2, 1)  # 7th column, row 1,2
        table.mergeCells(2, 6, 2, 1)


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
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportReHospitalization(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

    stmt2 = u'''
        SELECT
        (
          SELECT sss.vk #SUM(sss.age_M)
            FROM(
                SELECT COUNT(ss.e_id) AS vk
                FROM (
                SELECT s.id AS e_id, s.birthDate, s.eventType_id
                  FROM (
                     SELECT e.id, e.client_id, e.eventType_id, c.birthDate, c.sex
                      FROM Event e
                      INNER JOIN EventType et ON et.id = e.eventType_id
                      INNER JOIN Client c ON c.id = e.client_id
                      WHERE (e.eventType_id = 2 OR e.eventType_id = 6)
                      AND DATE(e.setDate) >= DATE('%s')  AND DATE(e.setDate) <= DATE('%s')
                      GROUP BY e.eventType_id, e.client_id
                      ORDER BY e.client_id, e.setDate
                  )s
                  WHERE (s.sex = 1 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(s.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(s.birthDate, '%%m%%d'))) <=59)) #male
                  OR (s.sex = 2 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(s.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(s.birthDate, '%%m%%d'))) <=54))
                  GROUP BY s.client_id
                  HAVING COUNT(s.client_id) > 1
                ) ss
                 WHERE ss.eventType_id = '2' # GROUP BY go zema prvoto, t.e. bila do dis. a posle kons ako vo output od gornoto query eventType = 2
              ) sss
        ) AS age_ppl,

          (
          SELECT COUNT(ss.freeInput)
                FROM (
                SELECT s.eventType_id, s.freeInput
                  FROM (
                     SELECT e.client_id, e.eventType_id, cw.freeInput
                      FROM Event e
                      INNER JOIN EventType et ON et.id = e.eventType_id
                      INNER JOIN Client c ON c.id = e.client_id
                      INNER JOIN ClientWork cw ON c.id = cw.client_id
                      WHERE (e.eventType_id = 2 OR e.eventType_id = 6)
                      AND DATE(e.setDate) >= DATE('%s')  AND DATE(e.setDate) <= DATE('%s')
                      GROUP BY e.eventType_id, e.client_id
                      ORDER BY e.client_id, e.setDate
                  )s
                  WHERE s.freeInput <> ""
                  GROUP BY s.client_id
                  HAVING COUNT(s.client_id) > 1
                ) ss
                 WHERE ss.eventType_id = '2'  # GROUP BY go zema prvoto, t.e. bila do dis. a posle kons ako vo output od gornoto query eventType = 2
              ) AS work_all,

         ( SELECT sss.vk #SUM(sss.age_M)
            FROM(
                SELECT COUNT(ss.e_id) AS vk
                FROM (
                SELECT s.id AS e_id, s.birthDate, s.eventType_id
                  FROM (
                     SELECT e.id, e.client_id, e.eventType_id, c.birthDate, c.sex, cw.freeInput
                      FROM Event e
                      INNER JOIN EventType et ON et.id = e.eventType_id
                      INNER JOIN Client c ON c.id = e.client_id
                      INNER JOIN ClientWork cw ON c.id = cw.client_id
                      WHERE (e.eventType_id = 2 OR e.eventType_id = 6)
                      AND DATE(e.setDate) >= DATE('%s')  AND DATE(e.setDate) <= DATE('%s')
                      GROUP BY e.eventType_id, e.client_id
                      ORDER BY e.client_id, e.setDate
                  )s
                  WHERE (s.sex = 1 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(s.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(s.birthDate, '%%m%%d'))) <=59)) #male
                  OR (s.sex = 2 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(s.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(s.birthDate, '%%m%%d'))) <=54))
                  AND s.freeInput <> ""
                  GROUP BY s.client_id
                  HAVING COUNT(s.client_id) > 1
                ) ss
                 WHERE ss.eventType_id = '2' # GROUP BY go zema prvoto, t.e. bila do dis. a posle kons ako vo output od gornoto query eventType = 2
              ) sss
          ) AS work_age,


          (SELECT COUNT(snjato.cl_id) FROM(
        SELECT e.client_id AS cl_id
            FROM Event e
            INNER JOIN Client c ON e.client_id=c.id
            INNER JOIN ClientAttach ca ON ca.client_id = c.id
            INNER JOIN rbAttachType rbat ON ca.attachType_id = rbat.id
            INNER JOIN EventType et ON et.id = e.eventType_id
            WHERE e.eventType_id = '2'
           # AND (et.form LIKE '%%025%%' OR et.form LIKE '%%030%%')
            AND ca.deleted = 1 AND (rbat.id = 8)
            AND DATE(ca.endDate) >= DATE('%s')  AND DATE(ca.endDate) <= DATE('%s')
            GROUP BY e.client_id
            ORDER BY e.client_id
          ) snjato) AS disp_dead

        FROM(
          SELECT e.client_id, e.setdate, e.eventType_id, c.birthDate, c.sex
          FROM Event e
          INNER JOIN EventType et ON et.id = e.eventType_id
          INNER JOIN Client c ON c.id = e.client_id
          WHERE (e.eventType_id = 2 OR e.eventType_id = 6)
          AND DATE(e.setDate) >= DATE('%s')  AND DATE(e.setDate) <= DATE('%s')
          GROUP BY e.eventType_id, e.client_id
          ORDER BY e.client_id, e.setDate
    ) dispanser_konsult;
        '''