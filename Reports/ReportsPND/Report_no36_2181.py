# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params):
    stmt = u'''
    SELECT  (
  SELECT COUNT(vsego.clid) FROM(
SELECT (e.client_id) as clid FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
WHERE ('G30%%')
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
GROUP BY cd.client_id
HAVING COUNT(cd.client_id) = 1 #ako ima samo eden klient znaic deka prv pat taa godina stanal invalid
) vsego ) AS vsego,

 (SELECT COUNT(vsego.clid) FROM(
SELECT (e.client_id) as clid FROM Event e
  INNER JOIN Client c ON e.client_id = c.id
  INNER JOIN ClientDisability cd ON c.id = cd.client_id
  Inner JOIN Diagnostic d ON e.id = d.event_id
  INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
WHERE ('G30%%')
    AND DATE(cd.setDate) >= DATE('%s') AND DATE(cd.setDate) <= DATE('%s')
GROUP BY cd.client_id
) vsego ) AS vsego_konec
;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')
                            ))

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
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        while query.next():
            record = query.record()
            cursor.insertBlock()
            txt = u'(2181) Число пациентов с психическими расстройствами, классифицированные в других рубриках МКБ-10 впервые признанных инвалидами в отчетном году 1: '
            txt = txt + forceString(record.value('vsego'))
            txt = txt + u', имевших инвалидности на конец отчетного года 2: '
            txt = txt + forceString(record.value('vsego_konec'))
            txt = txt + u'.'
            cursor.insertText(txt)

        return doc

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