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
        self.setTitle(u"ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ СТАТИСТИЧЕСКОЕ НАБЛЮДЕНИЕ")

    def getSetupDialog(self, parent):
        result = CReportReHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        #cursor.insertText(self.title())
        cursor.insertBlock()
        #self.dumpParams(cursor, params)
        cursor.insertBlock()

        lst_titles = [u'ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ СТАТИСТИЧЕСКОЕ НАБЛЮДЕНИЕ',
                      u'КОНФИДЕНЦИАЛЬНОСТЬ ГАРАНТИРУЕТСЯ ПОЛУЧАТЕЛЕМ ИНФОРМАЦИИ',
                      u'Нарушение порядка представления статистической информации, а равно предоставление недостоверной'
                      u'статистической информации влечет ответственность, установленную статьей 13.19 Кодекса'
                      u' Российской Федерации об административных правонарушениях от 30.12.2001.№ 195-Ф3б а также'
                      u'статьей 3 закона Российской Федерации от 13.05.92 № 2761-1 " Об ответственности за нарушение'
                      u' порядка представления государственной статистической отчётности" ',
                      u'ВОЗМОЖНО ПРЕТСТАВЛЕНИЕ В ЭЛЕКТРОННОМ ВИДЕ',
                      u'СВЕДЕНИЯ О КОНТИНГЕНТАХ ПСИХИЧЕСКИ БОЛЬНЫХ за ________ г.'
                      ]
        for i in range(0, len(lst_titles)):
            if i == 2:
                tableColumns = [
                    ('100%', [lst_titles[i]], CReportBase.AlignCenter)
                ]
            else:
                tableColumns = [
                    ('70%', [lst_titles[i]], CReportBase.AlignCenter)
                ]
            table = createTable(cursor, tableColumns)
            #query = selectData(params)
            #self.setQueryText(forceString(query.lastQuery()))  # this does nothing?
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertBlock()
            cursor.insertBlock()

        cursor.insertBlock()
        cursor.insertBlock()
        tableColumns = [
            ('53%', [u'Предоставляют:'], CReportBase.AlignCenter),
            ('17%', [u'Сроки предоставления'], CReportBase.AlignCenter),
            ('29%', [u''], CReportBase.AlignCenter)
        ]
        table = createTable(cursor, tableColumns)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        i = table.addRow()
        table.setText(i, 0, u'психоневрологические диспансеры, психиатрические, психоневрологические больницы; \n\n'
                            u'самостоятельные больницы, поликлиники, имеющие психиатрические (психоневрологические, \n\n'
                            u'психотерапевтические, психосоматические) отделения (кабинеты, койки): \n\n'
                            u'   - органу местного самоуправления в сфере здравоохранения;\n\n'
                            u'орган местного самоуправления в сфере здравоохранения:\n\n'
                            u'   - органу управления здравоохранения субьекта Российской Федерации;'
                            u'орган управления здравоохранения субьекта Российской Федерации:'
                            u'   - Минздраву России')
        table.setText(i, 1, u'5 января \n\n\n\n\n\n до 10 февраля \n\n\n\n\n\n до 5 марта')
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(1, 2, 2, 1)
        cursor.movePosition(QtGui.QTextCursor.EndOfWord, QtGui.QTextCursor.MoveAnchor, 1)
        cursor.anchor()
        cursor.movePosition(QtGui.QTextCursor.NextCell)
        cursor.movePosition(QtGui.QTextCursor.NextCell)
        cursor.insertTable(1, 1)
        cursor.insertText(
            u'*) Полные сведеической комиссии"')
        #
        # TO DO: da se napravi toa od desnata strana
        #

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        tableColumns = [
            ('20%', [u'Наименование отчитывающейся организации:'], CReportBase.AlignCenter),
            ('25%', [u''], CReportBase.AlignCenter),
            ('25%', [u''], CReportBase.AlignCenter),
            ('25%', [u''], CReportBase.AlignCenter)
        ]
        table = createTable(cursor, tableColumns)
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        lst_count = [0, 1, 2, 3]
        lst_scnd_row = [u'Почтовый  адрес:', u'', u'', u'']
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'Код  формы по ОКУД', u'', u'Код', u'']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'', u'Отчитывающейся организации по ОКПО', u'', u'']
        i = table.addRow()
        for j in range(0, len(lst_frth_row)):
            table.setText(i, lst_count[j], lst_frth_row[j])

        lst_ffth_row = [u'1', u'2', u'3', u'4']
        i = table.addRow()
        for j in range(0, len(lst_ffth_row)):
            table.setText(i, lst_count[j], lst_ffth_row[j])

        lst_sxth_row = [u'0609368', u'', u'', u'']
        i = table.addRow()
        for j in range(0, len(lst_sxth_row)):
            table.setText(i, lst_count[j], lst_sxth_row[j])

        i = 0
        while query.next():
            record = query.record()
            # i = table.addRow()
            # table.setText(i+2, 1, forceString(record_temp.value('FIO_cl')))
            # table.setText(i+2, 6, forceString(record_temp.value('birthdate')))
            # table.setText(i+2, 3, forceString(record_temp.value('MKB')))

        self.merge_cells(table)
        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 0, 1, 4)  # first row, 1-4 columns
        table.mergeCells(0, 1, 1, 4)
        table.mergeCells(0, 2, 1, 4)
        table.mergeCells(0, 3, 1, 4)
        table.mergeCells(1, 0, 1, 4)  # second row, 1-4 columns
        table.mergeCells(1, 1, 1, 4)
        table.mergeCells(1, 2, 1, 4)
        table.mergeCells(1, 3, 1, 4)
        table.mergeCells(2, 1, 1, 3)  # third row, 2-4 columns
        table.mergeCells(2, 2, 1, 3)
        table.mergeCells(2, 3, 1, 3)
        table.mergeCells(2, 0, 2, 1)  # first column, 3,4 rows
        table.mergeCells(3, 0, 2, 1)


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