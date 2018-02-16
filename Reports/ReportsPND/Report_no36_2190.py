# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params):
    stmt1 = u'''
        SELECT e.id AS vsego FROM Event e
        WHERE DATE(e.setDate) >= DATE('%s') AND DATE(e.setDate) <= DATE('%s');

    '''

    stmt = u'''
     SELECT (
     SELECT COUNT(vsego.clid) FROM(
SELECT (e.client_id) as clid FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
WHERE (ds.MKB LIKE 'F0%%' OR ds.MKB LIKE 'F2%%' OR ds.MKB LIKE 'F3%%'
    OR ds.MKB LIKE 'F4%%' OR ds.MKB LIKE 'F5%%' OR ds.MKB LIKE 'F6%%'
    OR ds.MKB LIKE 'F7%%' OR ds.MKB LIKE 'F8%%' OR ds.MKB LIKE 'F9%%')
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
    AND ((c.sex = 1 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <=59))
              OR (c.sex = 2 AND ((YEAR(CURRENT_DATE()) - YEAR(DATE(c.birthDate)) - (DATE_FORMAT(CURRENT_DATE(), '%%m%%d') < DATE_FORMAT(c.birthDate, '%%m%%d'))) <=54)))

GROUP BY cd.client_id
) vsego) AS vsego2 ;

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
            ('20%', [u'Из общего числа инвалидов по психическому заболеванию (стр.1 гр.7 т. 2180):'], CReportBase.AlignLeft),
            ('20%', [u''], CReportBase.AlignLeft),
            ('20%', [u''], CReportBase.AlignLeft),
            ('20%', [u''], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        lst_count = [0, 1, 2, 3]
        lst_scnd_row = [u'лиц трудоспособного возраста', u'работает:', u'', u'']
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'', u'на общем производстве', u'в спеццехах', u'в ЛТМ (ЛПМ)']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'1', u'2', u'3', u'4']
        i = table.addRow()
        for j in range(0, len(lst_frth_row)):
            table.setText(i, lst_count[j], lst_frth_row[j])

        i = table.addRow()
        query.next()
        record = query.record()
        table.setText(i, 0, forceString(record.value('vsego2')))
        table.setText(i, 1, forceString(record.value('')))
        table.setText(i, 2, forceString(record.value('')))
        table.setText(i, 3, forceString(record.value('')))


        self.merge_cells(table)

        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 0, 1, 4)  # first row, 1-4 columns
        table.mergeCells(0, 1, 1, 4)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(1, 1, 1, 3)  # second row, 2-4 columns
        table.mergeCells(1, 2, 1, 3)
        table.mergeCells(1, 3, 1, 3)
        table.mergeCells(1, 0, 2, 1)
        table.mergeCells(2, 0, 2, 1)

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
    connectionInfo = {'driverName': 'mysql',
                      'host': '192.168.0.3',
                      'port': 3306,
                      'database': 'pnd5',
                      'user': 'dbuser',
                      'password': 'dbpassword',
                      'connectionName': 'vista-med',
                      'compressData': True,
                      'afterConnectFunc': None}

    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportReHospitalization(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()