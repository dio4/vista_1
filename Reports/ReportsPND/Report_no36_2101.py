# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params):
    stmt = u'''
     SELECT COUNT(DISTINCT(ss.client_id)) AS vk_MKB FROM(
         SELECT e.id, cm.setDate, e.client_id
          FROM Event e
            INNER JOIN Diagnostic d ON d.event_id = e.id
            INNER JOIN Diagnosis ds ON d.diagnosis_id = ds.id
            INNER JOIN Client c ON e.client_id = c.id
            INNER JOIN ClientMonitoring cm ON cm.client_id = c.id
            INNER JOIN rbClientMonitoringKind cmk ON cmk.id = cm.kind_id
              WHERE (ds.MKB LIKE 'A52.1%%' OR ds.MKB LIKE 'A81.0%%' OR ds.MKB LIKE 'B22.0%%' OR ds.MKB LIKE 'G10%%'
              OR ds.MKB LIKE 'G11%%' OR ds.MKB LIKE 'G12%%' OR ds.MKB LIKE 'G13%%' OR ds.MKB LIKE 'G14%%'
              OR ds.MKB LIKE 'G15%%' OR ds.MKB LIKE 'G16%%' OR ds.MKB LIKE 'G17%%' OR ds.MKB LIKE 'G18%%'
              OR ds.MKB LIKE 'G19%%' OR ds.MKB LIKE 'G20%%' OR ds.MKB LIKE 'G21%%' OR ds.MKB LIKE 'G22%%'
              OR ds.MKB LIKE 'G23%%' OR ds.MKB LIKE 'G24%%' OR ds.MKB LIKE 'G25%%' OR ds.MKB LIKE 'G26%%'
              OR ds.MKB LIKE 'G27%%' OR ds.MKB LIKE 'G28%%' OR ds.MKB LIKE 'G29%%' OR ds.MKB LIKE 'G30%%'
              OR ds.MKB LIKE 'G31%%' OR ds.MKB LIKE 'G32%%' OR ds.MKB LIKE 'G33%%' OR ds.MKB LIKE 'G34%%'
              OR ds.MKB LIKE 'G35%%' OR ds.MKB LIKE 'G36%%' OR ds.MKB LIKE 'G37%%' OR ds.MKB LIKE 'G38%%'
              OR ds.MKB LIKE 'G39%%' OR ds.MKB LIKE 'G40%%')
              AND DATE(cm.setDate) >= DATE('%s') AND DATE(cm.setDate) <= DATE('%s')
            AND (cmk.name LIKE 'Д' OR cmk.name LIKE 'АДЛ' OR cmk.name LIKE 'АПЛ')
            GROUP BY e.client_id
          )ss;
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
            ('100%', [u'Число пациентов, больных психическими расстройствами, классифицированными в других рубриках МКБ-10, выявленных в отчетном году 1: '],
             CReportBase.AlignLeft)
          ]

        table = createTable(cursor, tableColumns)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        while query.next():
            record = query.record()
            table.setText(0, 0, forceString(record.value('vk_MKB')))

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