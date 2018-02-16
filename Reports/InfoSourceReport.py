# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.Utils      import forceInt, forceRef, forceString, formatName

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportInfoSourceSetup import Ui_ReportInfoSourceSetupDialog


def selectData(begDate, endDate, grouping):
    R1 = """
    SELECT
    Client.rbInfoSource_id, rbI.name as rbInfoSource_name, COUNT(IFNULL(rbI.name,0)) as rbInfoSource_cnt
    FROM Client
    LEFT JOIN
    rbInfoSource AS rbI
    ON Client.rbInfoSource_id = rbI.id
    WHERE %s
    GROUP BY rbI.id
    ORDER BY rbInfoSource_name
    """
    R2 = """
    SELECT rbI.id as sourceID, rbI.name as sourceName, Client.id, Client.lastName, Client.firstName, Client.patrName
    FROM Client
    LEFT JOIN
    rbInfoSource AS rbI
    ON Client.rbInfoSource_id = rbI.id
    WHERE %s
    ORDER BY sourceName, Client.id
    """

    stmt = R1 if grouping else R2

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    cond = []
    addDateInRange(cond, tableClient['createDatetime'], begDate, endDate)

    return db.query(stmt % (db.joinAnd(cond)))


class CInfoSourceReport(CReport):

    def __init__(self, parent):
        super(CInfoSourceReport, self).__init__(parent)
        self.setTitle(u'Причина обращения в ЛПУ')

    def getSetupDialog(self, parent):
        result = CInfoSourceReportSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        grouping = params.get('grouping')

        query = selectData(begDate, endDate, grouping)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        if grouping:
            self.build_R1(cursor, query)
        else:
            self.build_R2(cursor, query)

        return doc

    def build_R1(self, cursor, query):
        tableColumns = [
            ('25%', [u'Источник информации'],  CReportBase.AlignLeft),
            ('25%', [u'Количество пациентов'], CReportBase.AlignRight),
            ('25%', [u'Соотношение'],          CReportBase.AlignCenter),
            ('25%', [u'Примечание'],           CReportBase.AlignLeft)
            ]
        table = createTable(cursor, tableColumns)
        total_cnt = 0
        virtTable = []
        while query.next():
            record = query.record()
            rbIS_id = forceRef(record.value('rbInfoSource_id'))
            name = forceString(record.value('rbInfoSource_name'))
            cnt = forceInt(record.value('rbInfoSource_cnt'))
            if rbIS_id:
                total_cnt += cnt
            virtTable.append({'rbIS_id': rbIS_id, 'name': name, 'cnt': cnt})

        for r in virtTable:
            if not r.get('rbIS_id'):
                noneRbIS = r
                continue
            cnt = r.get('cnt')
            rate = float(cnt) / float(total_cnt) * 100.0
            i = table.addRow()
            table.setText(i, 0, r.get('name'))
            table.setText(i, 1, cnt)
            table.setText(i, 2, '%.2f %%' % rate)
        i = table.addRow()
        charFormat = QtGui.QTextCharFormat()
        charFormat.setFontItalic(True)
        charFormat.setFontWeight(QtGui.QFont.Bold)
        table.setText(i, 0, u'Итоговое итого:', charFormat)
        table.setText(i, 1, str(total_cnt), charFormat)
        table.mergeCells(i, 2, 1, 2)
        i = table.addRow()
        table.setText(i, 0, u'<не указан источник информации>')
        table.setText(i, 1, noneRbIS.get('cnt'))
        table.mergeCells(i, 2, 1, 2)

    def build_R2(self, cursor, query):
        tableColumns = [
            ('35%', [u'Источник информации'], CReportBase.AlignLeft),
            ('10%', [u'Код пациента'],        CReportBase.AlignRight),
            ('35%', [u'ФИО'],                 CReportBase.AlignLeft),
            ('20%', [u'Примечание'],          CReportBase.AlignLeft)
            ]
        table = createTable(cursor, tableColumns)
        from library.vm_collections import OrderedDict
        virtTable = OrderedDict()
        #virtTable structure:
        #{ sourceID : {
        #    'sourceName' : sourceName,
        #    'cnt' : cnt,
        #    'clients' : [
        #        {'Id': id, 'FIO': lastName + firstName + patrName},
        #        {}, ...
        #     ]
        # }, sourceID : {}, ... }
        total_cnt = 0
        while query.next():
            record = query.record()
            sourceID = forceRef(record.value('sourceID'))
            sourceName = forceString(record.value('sourceName'))
            Id = forceString(record.value('id'))
            lastName = forceString(record.value('lastName'))
            firstName = forceString(record.value('firstName'))
            patrName = forceString(record.value('patrName'))
            total_cnt += 1
            sourceName = sourceName if sourceID else u'<не указан источник информации>'
            sourceDict = virtTable.setdefault(sourceID, {'sourceName': sourceName, 'cnt': 0, 'clients': []})
            sourceDict.get('clients').append({'Id': Id, 'FIO': formatName(lastName, firstName, patrName)})
            cnt = sourceDict.get('cnt')
            cnt += 1
            sourceDict['cnt'] = cnt

        charFormat = QtGui.QTextCharFormat()
        charFormat.setFontItalic(True)
        for sourceID, sourceDict in virtTable.items():
            i = table.addRow()
            sourceName = sourceDict.get('sourceName')
            clients = sourceDict.get('clients')
            cl = clients.pop(0)
            table.setText(i, 0, sourceName)
            table.setText(i, 1, cl.get('Id'))
            table.setText(i, 2, cl.get('FIO'))
            for cl in clients:
                j = table.addRow()
                table.setText(j, 1, cl.get('Id'))
                table.setText(j, 2, cl.get('FIO'))
            cnt = sourceDict.get('cnt')
            rate = float(cnt) / float(total_cnt) * 100.0
            table.mergeCells(i, 0, cnt, 1)
            i = table.addRow()
            table.setText(i, 0, u'Итого: ' + '%i (%.2f %%)' % (cnt, rate), charFormat)
            table.mergeCells(i, 0, 1, 4)
        i = table.addRow()
        charFormat.setFontWeight(QtGui.QFont.Bold)
        table.setText(i, 0, u'Итоговое итого: ' + str(total_cnt), charFormat)
        table.mergeCells(i, 0, 1, 4)


class CInfoSourceReportSetupDialog(QtGui.QDialog, Ui_ReportInfoSourceSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['grouping'] = self.chkGrouping.isChecked()
        return result

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.chkGrouping.setChecked(params.get('grouping', True))
