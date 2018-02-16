# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceRef, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportLocationCard import Ui_ReportLocationCard

def selectData(params):
    begDate = forceDate(params.get('begDate', QtCore.QDate()))
    endDate = forceDate(params.get('endDate', QtCore.QDate()))
    locationCardType = forceRef(params.get('locationCardTypeId', None))

    db = QtGui.qApp.db

    tableClient             = db.table('Client')
    tableLocalCardType      = db.table('rbLocationCardType')
    tableClientLocationCard = db.table('Client_LocationCard')

    fields = [tableClient['lastName'],
              tableClient['firstName'],
              tableClient['patrName'],
              tableClient['birthDate'],
              tableLocalCardType['name'],
              tableClient['id']]

    cond = [tableLocalCardType['id'].eq(locationCardType),
            tableClientLocationCard['createDatetime'].ge(begDate),
            tableClientLocationCard['createDatetime'].le(endDate)]

    queryTable = tableClient.innerJoin(tableClientLocationCard, [tableClientLocationCard['master_id'].eq(tableClient['id'])])
    queryTable = queryTable.innerJoin(tableLocalCardType, tableLocalCardType['id'].eq(tableClientLocationCard['locationCardType_id']))

    stmt = db.selectStmt(queryTable, fields, cond)
    return db.query(stmt)

class CReportLocationCard(CReport):
    def __init__(self, parent ):
        CReport.__init__(self, parent)
        self.setTitle(u'По месту нахождения амбулаторной карты')

    def getSetupDialog(self, parent):
        result = CLocationCard(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('2%',  [u'№'                   ], CReportBase.AlignLeft),
            ('25%', [u'ФИО'                  ], CReportBase.AlignLeft),
            ('15%', [u'Дата рождения'        ], CReportBase.AlignCenter),
            ('15%', [u'№ Амбулаторной карты'], CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)

        total = 0
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, ' '.join([forceString(record.value('lastName')), forceString(record.value('firstName')), forceString(record.value('partName'))]))
            table.setText(i, 2, forceString(record.value('birthDate')))
            table.setText(i, 3, forceRef(record.value('id')))
            total += 1
        i = table.addRow()
        table.mergeCells(i, 1, 1, 3)
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        table.setText(i, 1, total, CReportBase.TableTotal, CReportBase.AlignRight)
        return doc

class CLocationCard(QtGui.QDialog, Ui_ReportLocationCard):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbLocationCardType.setTable('rbLocationCardType', False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbLocationCardType.setValue(params.get('locationCardTypeId', None))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['locationCardTypeId'] = self.cmbLocationCardType.value()
        return params





