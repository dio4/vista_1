# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils      import forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Reports.StatReport1DD2000 import CStatReport1DD2000
from Reports.StatReport1DD3000 import CStatReport1DD3000
from Reports.StatReport1DD4000 import CStatReport1DD4000


class CStatReport1DDAll(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Итоги дополнительной диспансеризации граждан', u'Итоги дополнительной диспансеризации')


    def getSetupDialog(self, parent):
        result = CReport.getSetupDialog(self, parent)
        result.setStageVisible(True)
        return result


    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Итоги дополнительной диспансеризации граждан')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
## тут нужна изоляция типа
#        db = QtGui.qApp.db
#        db.transaction()
#        try:
        CStatReport1DD2000(None).buildInt(params, cursor)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        CStatReport1DD3000(None).buildInt(params, cursor)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        CStatReport1DD4000(None).buildInt(params, cursor)
#        finally:
#            db.commit()

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText('\n\n\n')
        cursor.insertBlock()
        rows = []
        orgId = QtGui.qApp.currentOrgId()
        db = QtGui.qApp.db
        table = db.table('Organisation')
        record = db.getRecordEx(table, table['chief'], [table['id'].eq(orgId), table['deleted'].eq(0)])
        chief = forceString(record.value('chief'))
        text0 = u'Руководитель ЛПУ                                   %s'%(chief)
        rows.append([text0])
        rows.append([u'\n'])
        rows.append([u'_____________________________'])
        rows.append([u'                    (подпись)'])
        rows.append([u'\n                                                                                       М.П.\n'])
        rows.append([u'"_____"________________2010г.'])
        columnDescrs = [('100%', [], CReportBase.AlignLeft)]
        table1 = createTable (
            cursor, columnDescrs, headerRowCount=len(rows), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(rows):
            table1.setText(i, 0, row[0])
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        return doc

