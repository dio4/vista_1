# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params, query):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    stmt = u'''
         SELECT
           (
            SELECT SUM(s.salary) FROM(
             SELECT p.id, po.salary FROM Person p
               INNER JOIN Person_Order po ON po.master_id = p.id
               INNER JOIN rbPost rbp ON p.post_id = rbp.id
               INNER JOIN Event e ON e.execPerson_id = p.id
               WHERE (%s)
               AND po.salary <> ''
               GROUP BY p.id
             ) s
         ) AS dolznosti,

         (
         SELECT COUNT(*) FROM (
         SELECT v.id FROM Visit v
           INNER JOIN rbScene s ON v.scene_id=s.id
           INNER JOIN Person p ON v.person_id = p.id
           INNER JOIN rbPost rbp ON p.post_id = rbp.id
           WHERE (%s)
           AND DATE(v.date) >= DATE('%s') AND DATE(v.date) <= DATE('%s')
           ORDER BY p.id
         )s
         ) AS all_visits,

         (
         SELECT COUNT(*) FROM (
         SELECT v.id FROM Visit v
           INNER JOIN rbScene s ON v.scene_id=s.id
           INNER JOIN Person p ON v.person_id = p.id
           INNER JOIN rbPost rbp ON p.post_id = rbp.id
           INNER JOIN Event e ON v.event_id = e.id
           INNER JOIN EventType et ON e.eventType_id = et.id
           WHERE (%s)
           AND et.name LIKE '%%свидетельствов%%'
           AND DATE(v.date) >= DATE('%s') AND DATE(v.date) <= DATE('%s')
           ORDER BY p.id
         )s
         ) AS osvidetelnost

         ;
     '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (query,
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
        self.setTitle(u"Число занятых должностей психиатров и психотерапевтов, осуществляющих "
                      u"диспансерное наблюдение и консультативно-лечебную помощь")

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
            ('17%', [u'Наименование'], CReportBase.AlignLeft),
            ('5%', [u'№ строки'], CReportBase.AlignLeft),
            ('15%', [u'Занято должностей на конец года'], CReportBase.AlignLeft),
            ('15%', [u'Число посещений к врачам, включая посещения на дому - всего'], CReportBase.AlignLeft),
            ('15%', [u'из них (из гр.4) по поводу освидетельствования для работы с источниками повышенной'
                     u' опасности и по другим основаниям'], CReportBase.AlignLeft),
            ('15%', [u'Число посещений по поводу заболеваний, включая посещения на дому (из гр.4)- всего'], CReportBase.AlignLeft),
            ('12%', [u'Кроме того, проведено осмотров в военкоматах, учебных и других учреждениях'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        lst_naimenovanie = [u'', u'',
                            u'Психиатры, работающие по участковому принципу:для взрослых',
                            u"для подростков",
                            u"детские",
                            u"Психотерапевты"]
        lst_numbers = [u'', u'', u'1', u'2', u'3', u'4']

        lst_count = [0, 1, 2, 3, 4, 5, 6]
        lst_scnd_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7']

        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        for i in range(0,4):
            i = table.addRow()
            table.setText(i, 0, lst_naimenovanie[i])
            table.setText(i, 1, lst_numbers[i])

        l= [
            '%психиатр участковый%',
            '%психиатр детский участковый%',
            '%психиатр подростковый участковый%',
            '%психотерапевт%'

        ]

        ii=0
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        for j in l:
            query_str = u"rbp.name LIKE '%s' " % j

            query = selectData(params, query_str)
            self.setQueryText(forceString(query.lastQuery()))
            while query.next():
                record = query.record()
                #val_col_8 = int(forceString(record.value('snjato_vsego'))) + int(forceString(record.value('snjato_chg')))
                if (ii+2)==5:
                    print "VLEZE"
                    table.setText(ii + 2, 2, forceString(record.value('dolznosti')))
                    table.setText(ii + 2, 3, forceString(record.value('all_visits')))
                    table.setText(ii + 2, 4, forceString('X'))
                    table.setText(ii + 2, 5, forceString(record.value('all_visits')))
                else:
                    table.setText(ii + 2, 2, forceString(record.value('dolznosti')))
                    table.setText(ii + 2, 3, forceString(record.value('all_visits')))
                    table.setText(ii + 2, 4, forceString(record.value('osvidetelnost')))
                    diff = int(forceString(record.value('all_visits'))) - int(forceString(record.value('osvidetelnost')))
                    table.setText(ii + 2, 5, forceString(int(diff)))


            ii = ii + 1

        return doc


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