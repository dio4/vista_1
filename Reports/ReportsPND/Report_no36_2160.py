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
            ('10%', [u'Число пациентов, содержавшихся в психоневрологических учреждениях социального обслуживания (кроме пациентов, показанных в табл. 2100 и 2110) на конец года'], CReportBase.AlignLeft),
            ('12%', [u''], CReportBase.AlignLeft),
            ('15%', [u'Число лиц, недобровольно освидетельствованных диспансером (диспансерным отделением, кабинетом)'], CReportBase.AlignLeft),
            ('20%', [u''], CReportBase.AlignLeft),
            ('18%', [u''], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        for i in range(0, 1):
            i = table.addRow()
            table.setText(i, 0, u'всего')
            table.setText(i, 1, u'из них детей 0-17 лет включительно')
            table.setText(i, 2, u'всего')
            table.setText(i, 3, u'в т. ч. признано страдающими психическими расстройствами')
            table.setText(i, 4, u'из них на момент обследования нуждаются в стационарном лечении')

        for i in range(0, 1):
            i = table.addRow()
            table.setText(i, 0, u'1')
            table.setText(i, 1, u'2')
            table.setText(i, 2, u'3')
            table.setText(i, 3, u'4')
            table.setText(i, 4, u'5')

        i = table.addRow()
        while query.next():
            record = query.record()
            table.setText(i, 3, forceString(record.value('otch_god')))

        self.merge_cells(table)
        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 0, 1, 2)  # first row, 1-4 columns
        table.mergeCells(0, 1, 1, 2)
        table.mergeCells(0, 2, 1, 3)  # first row, 5-8 columns
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(0, 4, 1, 3)
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