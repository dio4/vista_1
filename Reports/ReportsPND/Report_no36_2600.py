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
        SELECT COUNT(s.id) FROM(
        SELECT c.id FROM Event e
          INNER JOIN Action a ON e.id = a.event_id
          INNER JOIN Client c ON e.client_id = c.id
          INNER JOIN ActionType act ON a.actionType_id = act.id
          INNER JOIN OrgStructure_ActionType osat ON act.id = osat.actionType_id
          INNER JOIN OrgStructure os ON osat.master_id = os.id
          WHERE (act.name='выписка') AND
          DATE(e.execDate) >= DATE('%s') AND DATE(e.execDate) <= DATE('%s')
          AND (os.name LIKE '%%Дневной стационар%%' OR os.name LIKE '%%Медико реабилитационное%%')

          GROUP BY c.id ) s
          ) AS vypisanno
          ,

          (SELECT COUNT(s.id) FROM(
        SELECT c.id FROM Event e
          INNER JOIN Action a ON e.id = a.event_id
          INNER JOIN Client c ON e.client_id = c.id
          INNER JOIN ActionType act ON a.actionType_id = act.id
          INNER JOIN OrgStructure_ActionType osat ON act.id = osat.actionType_id
          INNER JOIN OrgStructure os ON osat.master_id = os.id
          WHERE (act.name LIKE 'движение%%' OR act.name LIKE '%%поступление%%') AND
           (e.execDate is null OR e.execDate >= DATE('%s'))
          AND (os.name LIKE '%%Дневной стационар%%' OR os.name LIKE '%%Медико реабилитационное%%')
          GROUP BY c.id ) s
          ) AS pacienty_konec_goda
          ,
        (
        SELECT COUNT(s.id) FROM(
        SELECT c.id FROM Event e
          INNER JOIN Action a ON e.id = a.event_id
          INNER JOIN Client c ON e.client_id = c.id
          INNER JOIN ActionType act ON a.actionType_id = act.id
          INNER JOIN OrgStructure_ActionType osat ON act.id = osat.actionType_id
          INNER JOIN OrgStructure os ON osat.master_id = os.id
          WHERE (act.name = 'движение' OR act.name = 'поступление') AND
          (DATE(e.setDate) >= DATE('%s') AND DATE(e.execDate) <= DATE('%s'))
          AND (os.name LIKE '%%Дневной стационар%%' OR os.name LIKE '%%Медико реабилитационное%%')

          GROUP BY c.id ) s
          ) AS stacionar_dnej
          ;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            endDate.toString('yyyy-MM-dd'),
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')
                            )
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
        self.setTitle(u"Полустационарные и стационарные подразделения для пациентов, больных психическими расстройствами")

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
            ('20%', [u'Виды подразделений'], CReportBase.AlignLeft),
            ('3%', [u'№ строки'], CReportBase.AlignLeft),
            ('10%', [u'Число мест (коек)'], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('7%', [u'Выписано пациентов'], CReportBase.AlignLeft),
            ('8%', [u'Состоит пациентов на конец года'], CReportBase.AlignLeft),
            ('9%', [u'Число дней, проведенных в стационаре'], CReportBase.AlignLeft),
            ('8%', [u'По закрытым листкам нетрудоспособности:'], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('12%', [u'Из них у пациентов с заболеваниями, связанными  употреблением ПАВ'], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        lst_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        lst_numbers = [u'', u'', u'', u'1', u'2', u'3', u'4']
        lst_naimenovanie = [u'', u'', u'',
                            u'Дневной стационар',
                            u"Ночной стационар",
                            u"Стационар на дому",
                            u"Реабилитационное отделение психиатрического стационара"]

        lst_scnd_row = [u'', u'', u'по смете', u'средне-годовых', u'', u'', u'', u'число случаев', u'число дней',
                        u'число случаев (из графы 8)', u'число дней (из графы 9)']
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        for i in range(0, 4):
            i = table.addRow()
            table.setText(i, 0, lst_naimenovanie[i])
            table.setText(i, 1, lst_numbers[i])

        i = 0
        for j in range(0, 4):

            query = selectData(params)
            self.setQueryText(forceString(query.lastQuery()))
            while query.next():
                record = query.record()
                #i = table.addRow()
                if ((i + 3)==3):
                    table.setText(i + 3, 5, forceString(record.value('vypisanno')))
                    table.setText(i + 3, 6, forceString(record.value('pacienty_konec_goda')))
                    table.setText(i + 3, 7, forceString(record.value('stacionar_dnej')))
                    table.setText(i + 3, 2, forceString('-'))
                    table.setText(i + 3, 3, forceString('-'))
                    table.setText(i + 3, 4, forceString('-'))
                    table.setText(i + 3, 8, forceString('-'))
                    table.setText(i + 3, 9, forceString('-'))
                    table.setText(i + 3, 10, forceString('-'))
                else:
                    table.setText(i + 3, 2, forceString('X'))
                    table.setText(i + 3, 3, forceString('X'))
                    table.setText(i + 3, 4, forceString('X'))
                    table.setText(i + 3, 5, forceString('X'))
                    table.setText(i + 3, 6, forceString('X'))
                    table.setText(i + 3, 7, forceString('X'))
                    table.setText(i + 3, 8, forceString('X'))
                    table.setText(i + 3, 9, forceString('X'))
                    table.setText(i + 3, 10, forceString('X'))

            i = i + 1


        self.merge_cells(table)
        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 0, 2, 1)  # first column, 1,2 rows
        table.mergeCells(1, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)  # second column, 1,2 rows
        table.mergeCells(1, 1, 2, 1)
        table.mergeCells(0, 4, 2, 1)  # 5th column, 1,2 rows
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)  # 6th column, 1,2 rows
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)  # 7th column, 1,2 rows
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(0, 2, 1, 2)  # first row,3,4 columns
        table.mergeCells(0, 3, 1, 2)
        table.mergeCells(0, 7, 1, 2)  # first row,8,9 columns
        table.mergeCells(0, 8, 1, 2)
        table.mergeCells(0, 9, 1, 2)  # first row,10,11 columns
        table.mergeCells(0, 10, 1, 2)




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