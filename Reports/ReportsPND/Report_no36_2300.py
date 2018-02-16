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
        self.setTitle(u"Состав пациентов, больных психическими расстройствами, получивших медицинскую помощь, в стационарных условиях")

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
            ('12%', [u'Наименование'], CReportBase.AlignLeft),
            ('8%', [u'Код по МКБ-X (класс V, адаптированный для использования в РФ)'], CReportBase.AlignLeft),
            ('3%', [u'№ строки'], CReportBase.AlignLeft),
            ('6%', [u'В отчётном году'], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('8%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft),
            ('6%', [u''], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        query1 = selectData(params)
        query_temp = selectData(params)

        query1.next()
        query_temp.next()
        record_temp = query_temp.record()
        self.setQueryText(forceString(query.lastQuery()))  # this does nothing?

        lst_MKB = [u'', u'', u'', u'', u'',
                    u'F00-F09, F20-F99',
                    u'',
                    u'F00-F05, F06 (часть), F09',
                    u'F01',
                    u'F00, F02.0, F02.2-3, F03',
                    u'F20',
                    u'F21',
                    u'F25, F3x.x4',
                    u'F23, F24',
                    u'F22, F28, F29, F84.0-4, F99.1',
                    u'F84.0-1',
                    u'F30-F39(часть)',
                    u'F31.23, F31.28, F31.53, 31.58',
                    u'',
                    u'F06(часть), F07',
                    u'F30-F39(часть)',
                    u'F31.0, F31.1, F31.3, F31.4, F31.6 - F31.9',
                    u'F50-59, F80-83, F84.5, F90-F98, F99.2,9',
                    u'F50-59, F80-83, F84.5, F90-F98, F99.2,9',
                    u'F84.5',
                    u'F60-F69',
                    u'F70,71-F79',
                    u'F10-F19',
                    u'F10.4, F10.7',
                    u'F11-F19',
                    u''
                   ]

        lst_numbers = [u'', u'', u'', u'', u'', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12', u'13', u'14', u'15',
                       u'16', u'17', u'18', u'19', u'20', u'21', u'22', u'23', u'24', u'25',u'26']

        lst_naimenovanie = [u'', u'', u'', u'', u'',
                            u'Психические расстройства - всего',
                            u"Психозы и состояния слабоумия (сумма строк 3,6-10,12)",
                            u'в том числе:органические психозы и (или) слабоумие',
                            u'из них:сосудистая деменция',
                            u'другие формы старческого слабоумия',
                            u"шизофрения",
                            u'шизотипические расстройства',
                            u'шизоаффективные психозы, аффективные психозы с некон-груэнтным аффекту бредом',
                            u'острые и преходящие неорганические психозы',
                            u'хронические неорганические психозы, детские психозы, неуточненые психот. расс-ва',
                            u"из них: детский аутизм, атипичный аутизм",
                            u'аффективные психозы',
                            u'из них биполярные расстройства',
                            u"Непсихотические психические расстройства (сумма строк 15,16,18,19,21)",
                            u"в том числе органические непсихотипические расстройства",
                            u"аффективные непсихотические расстройства",
                            u"из них биполярные расстройства",
                            u'невротические, связанные со стрессом и соматоформные расстройства',
                            u'другие непсихотические расстройства, поведенческие расстройства детского и подросткового возраста, неуточненные непсихотические расстройства',
                            u"из них синдром Аспергера",
                            u'расстройства зрелой личности и поведения у взрослых',
                            u'Умственная отсталость',
                            u"Кроме того:пациены с заболеваниями, связанными с употреблением психоактивных веществ",
                            u"из них: больные с алкогольными психозами",
                            u"наркоманиями, токсикоманиями",
                            u"признаны психически здоровыми и с заболеваниями, не вошедшими в стр.1 и 23"
                            ]
        lst_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

        lst_scnd_row = [u'', u'', u'', u'поступило пациентов', u'', u'', u'из них поступило (из гр.4)', u'', u'',
                        u'выбыло пациентов', u'число койко-дней, проведенных в стационаре выписанными и умершими',
                        u'Состоит на конец года', u'', u'']
        i = table.addRow()
        for j in range(0, len(lst_scnd_row)):
            table.setText(i, lst_count[j], lst_scnd_row[j])

        lst_thrd_row = [u'', u'', u'', u'', u'из них детей', u'', u'', u'', u'', u'', u'', u'', u'из них детей', u'']
        i = table.addRow()
        for j in range(0, len(lst_thrd_row)):
            table.setText(i, lst_count[j], lst_thrd_row[j])

        lst_frth_row = [u'', u'', u'', u'поступило больных', u'0-14 лет', u'15-17 лет', u'впервые в данном году',
                        u'из них впервые в жизни', u'недобровольно в соответствии со ст.29', u'', u'',
                        u'всего', u'0-14 лет', u'15-17 лет']
        i = table.addRow()
        for j in range(0, len(lst_frth_row)):
            table.setText(i, lst_count[j], lst_frth_row[j])

        lst_ffth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12', u'13', u'14']
        i = table.addRow()
        for j in range(0, len(lst_ffth_row)):
            table.setText(i, lst_count[j], lst_ffth_row[j])

        for i in range(0, 26):
            i = table.addRow()
            table.setText(i, 0, lst_naimenovanie[i])
            table.setText(i, 1, lst_MKB[i])
            table.setText(i, 2, lst_numbers[i])

        i = 0
        while query.next():
            record = query.record()

            #i = table.addRow()
            #table.setText(i+2, 1, forceString(record_temp.value('FIO_cl')))
            #table.setText(i+2, 6, forceString(record_temp.value('birthdate')))

        self.merge_cells(table)
        return doc

    def merge_cells(self, table):
        table.mergeCells(0, 3, 1, 11)  # first row, 5,6,7 columns
        table.mergeCells(0, 4, 1, 11)
        table.mergeCells(0, 5, 1, 11)
        table.mergeCells(0, 6, 1, 11)
        table.mergeCells(0, 7, 1, 11)
        table.mergeCells(0, 8, 1, 11)
        table.mergeCells(0, 9, 1, 11)
        table.mergeCells(0, 10, 1, 11)
        table.mergeCells(0, 11, 1, 11)
        table.mergeCells(0, 12, 1, 11)
        table.mergeCells(0, 13, 1, 11)
        table.mergeCells(1, 3, 1, 3)  #second row, col 4,5,6
        table.mergeCells(1, 4, 1, 3)
        table.mergeCells(1, 5, 1, 3)
        table.mergeCells(2, 4, 1, 2)  #third row, col 5,6
        table.mergeCells(2, 5, 1, 2)

        table.mergeCells(1, 6, 1, 3)  #second row, col 4,5,6
        table.mergeCells(1, 7, 1, 3)
        table.mergeCells(1, 8, 1, 3)

        table.mergeCells(2, 6, 1, 3)  #second row, col 4,5,6
        table.mergeCells(2, 7, 1, 3)
        table.mergeCells(2, 8, 1, 3)

        table.mergeCells(1, 6, 2, 3)
        table.mergeCells(2, 6, 2, 3)

        table.mergeCells(1, 11, 1, 3)  #second row, col 4,5,6
        table.mergeCells(1, 12, 1, 3)
        table.mergeCells(1, 13, 1, 3)
        table.mergeCells(2, 12, 1, 2)  #third row, col 5,6
        table.mergeCells(2, 13, 1, 2)

        table.mergeCells(0, 0, 4, 1)  # 3d column, row 1,2
        table.mergeCells(1, 0, 4, 1)
        table.mergeCells(2, 0, 4, 1)
        table.mergeCells(3, 0, 4, 1)

        table.mergeCells(0, 0, 4, 1)  # 3d column, row 1,2
        table.mergeCells(1, 0, 4, 1)
        table.mergeCells(2, 0, 4, 1)
        table.mergeCells(3, 0, 4, 1)

        table.mergeCells(0, 1, 4, 1)  # 3d column, row 1,2
        table.mergeCells(1, 1, 4, 1)
        table.mergeCells(2, 1, 4, 1)
        table.mergeCells(3, 1, 4, 1)

        table.mergeCells(0, 2, 4, 1)  # 3d column, row 1,2
        table.mergeCells(1, 2, 4, 1)
        table.mergeCells(2, 2, 4, 1)
        table.mergeCells(3, 2, 4, 1)

        table.mergeCells(0, 9, 3, 1)  # 3d column, row 1,2
        table.mergeCells(1, 9, 3, 1)
        table.mergeCells(2, 9, 3, 1)

        table.mergeCells(0, 10, 3, 1)  # 3d column, row 1,2
        table.mergeCells(1, 10, 3, 1)
        table.mergeCells(2, 10, 3, 1)

        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(3, 3, 2, 1)

        table.mergeCells(2, 11, 2, 1)
        table.mergeCells(3, 11, 2, 1)

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