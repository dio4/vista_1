# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params):
    stmt = u'''
    SELECT A.cl_id AS cl_id,
    e.id AS eID,
    DATE(e.setDate) AS setDate,
    DATE(e.execDate) AS execDate,
    CONCAT_WS(' - ', DATE(e.setDate), DATE(e.execDate)) AS hospitalization,
    A.FIO_cl AS FIO_cl,
    A.birthdate AS birthdate,
    A.d_MKB AS MKB,
    a1.descr AS descr,
    CONCAT_WS(' ', p.lastName, p.firstName, p.patrName) AS FIO_p
    FROM (
    SELECT diag_MKB.cl_id, diag_MKB.d_MKB, diag_MKB.FIO_cl, diag_MKB.birthdate
      FROM
      (
        SELECT c.id AS cl_id, d.MKB AS d_MKB, CONCAT_WS(' ', c.lastName, c.firstName, c.patrName) AS FIO_cl, c.birthDate AS birthdate
          FROM Client c
          INNER JOIN Event e ON e.client_id = c.id
          INNER JOIN Diagnostic d1 ON d1.event_id = e.id
          INNER JOIN Diagnosis d ON d1.diagnosis_id = d.id
          GROUP BY d.MKB
          HAVING COUNT(*) > 1
          ORDER BY c.id
      ) diag_MKB

      INNER JOIN Event e ON diag_MKB.cl_id = e.client_id
      WHERE e.execDate IS NOT NULL
      GROUP BY e.client_id
      HAVING COUNT(*) > 1
      ) A

      INNER JOIN Event e ON e.client_id = A.cl_id
      INNER JOIN Action act ON e.id = act.event_id
      INNER JOIN ActionType act_type ON act.actionType_id = act_type.id
      INNER JOIN ActionPropertyType a1 ON a1.actionType_id = act_type.id
      INNER JOIN Person p ON p.id = act.person_id
      WHERE act_type.flatCode = 'leaved' AND a1.name='Отделение'
      AND e.execDate IS NOT NULL
      AND DATE(e.setDate) >= DATE('%s')  AND DATE(e.setDate) <= DATE('%s')
      ORDER BY e.client_id, e.setDate;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))

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
        self.setTitle(u"Контингенты больных, получающих консультативно-лечебную помощь")

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
            ('10%', [u'Из общего числа выбывших (стр. 1, 22, 25 гр. 10 т. 2300):'], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('7%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('7%', [u''], CReportBase.AlignLeft),
            ('9%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('12%', [u''], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        lst_frst_row = [u'получили курс лечения/реабилитации бригадным методом', u'переведено в другие стационары', u'',
                        u'переведено в учреждения социального обслуживания (впервые оформленных)', u'',
                        u'выбыло детей в возрасте 0-14 лет включительно', u'',
                        u'выбыло детей в возрасте 15-17 лет включительно', u'', u'умерли', u'', u'', u'']

        lst_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        i = table.addRow()
        for j in range(0, len(lst_frst_row)):
            table.setText(i, lst_count[j], lst_frst_row[j])

        lst_scnd_row = [u'', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'из них', u'', u'']
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'', u'всего', u'из них в психиатрические стационары', u'для взрослых', u'для детей', u'всего',
                        u'проведено ими койко-дней', u'всего', u'проведено ими койко-дней', u'всего',
                        u'от несчастных случаев', u'от самоубийств',
                        u'непосредственно от психического заболевания(коды F00 – F09,F20 – F99)']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12', u'13']
        i = table.addRow()
        for j in range(0, len(lst_frth_row)):
            table.setText(i, lst_count[j], lst_frth_row[j])

        i = 0
        while query.next():
            record = query.record()
            #i = table.addRow()
            #table.setText(i+2, 1, forceString(record_temp.value('FIO_cl')))
            #table.setText(i+2, 6, forceString(record_temp.value('birthdate')))
            #table.setText(i+2, 2, forceString(record_temp.value('hospitalization')))

        self.merge_cells(table)
        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 0, 1, 13)  # first row, 5,6,7 columns
        table.mergeCells(0, 1, 1, 13)
        table.mergeCells(0, 2, 1, 13)
        table.mergeCells(0, 3, 1, 13)
        table.mergeCells(0, 4, 1, 13)
        table.mergeCells(0, 5, 1, 13)
        table.mergeCells(0, 6, 1, 13)
        table.mergeCells(0, 7, 1, 13)
        table.mergeCells(0, 8, 1, 13)
        table.mergeCells(0, 9, 1, 13)
        table.mergeCells(0, 10, 1, 13)
        table.mergeCells(0, 11, 1, 13)
        table.mergeCells(0, 12, 1, 13)
        table.mergeCells(1, 1, 1, 2)  # second row, 2,3 columns
        table.mergeCells(1, 2, 1, 2)
        table.mergeCells(2, 1, 1, 2)  # third row, 2,3 columns
        table.mergeCells(2, 2, 1, 2)
        table.mergeCells(1, 1, 2, 2)  # merge second and third row
        table.mergeCells(2, 1, 2, 2)
        table.mergeCells(1, 3, 1, 2)  # second row, 4,5 columns
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(2, 3, 1, 2)  # third row, 4,5 columns
        table.mergeCells(2, 4, 1, 2)
        table.mergeCells(1, 3, 2, 2)  # merge second and third row
        table.mergeCells(2, 3, 2, 2)
        table.mergeCells(1, 5, 1, 2)  # second row, 6,7 columns
        table.mergeCells(1, 6, 1, 2)
        table.mergeCells(2, 5, 1, 2)  # third row, 6,7 columns
        table.mergeCells(2, 6, 1, 2)
        table.mergeCells(1, 5, 2, 2)  # merge second and third row
        table.mergeCells(2, 5, 2, 2)
        table.mergeCells(1, 7, 1, 2)  # second row, 8,9 columns
        table.mergeCells(1, 8, 1, 2)
        table.mergeCells(2, 7, 1, 2)  # third row, 8,9 columns
        table.mergeCells(2, 8, 1, 2)
        table.mergeCells(1, 7, 2, 2)  # merge second and third row
        table.mergeCells(2, 7, 2, 2)
        table.mergeCells(1, 9, 1, 4)  # second row, 10-13 columns
        table.mergeCells(1, 10, 1, 4)
        table.mergeCells(1, 11, 1, 4)
        table.mergeCells(1, 12, 1, 4)
        table.mergeCells(2, 10, 1, 3)  # third row, 11-13 columns
        table.mergeCells(2, 11, 1, 3)
        table.mergeCells(2, 12, 1, 3)
        table.mergeCells(1, 0, 3, 1)  # first column, 1-3 rows
        table.mergeCells(2, 0, 3, 1)
        table.mergeCells(3, 0, 3, 1)
        table.mergeCells(2, 9, 2, 1)
        table.mergeCells(3, 9, 2, 1)

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