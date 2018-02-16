# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ConsolidatedFinanceSumSetup import Ui_ConsolidatedFinanceSumSetup
from library.Utils import forceInt, forceString


def selectDataOrg(nullValue, begDate, endDate):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableOrganisation = db.table('Organisation')
    tableAccountItem = db.table('Account_Item')
    queryTable = tableOrganisation
    queryTable = queryTable.innerJoin(tableAccount, tableAccount['payer_id'].eq(tableOrganisation['id']))
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
    str = db.selectStmt(
        queryTable,
        'Organisation.`id` AS `OrgId`, Organisation.`shortName`, COUNT(Account_Item.`visit_id`) AS countVisit',
        where=[
            tableAccount['payer_id'].eq(nullValue),
            tableAccountItem['reexposeItem_id'].isNull(),
            tableAccount['date'].ge(begDate.toString('yyyy-MM-dd')),
            tableAccount['date'].le(endDate.toString('yyyy-MM-dd')),
            tableAccount['deleted'].eq(0),
            tableAccountItem['deleted'].eq(0)
        ]
    )
    str += 'GROUP BY Organisation.`shortName`'
    return str

def selectDataSumPrice(begDate, endDate, orgId):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    queryTable = tableAccount
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
    return db.selectStmt(
        queryTable,
        'SUM(Account_Item.`sum`) AS sumPrice',
        where=[
            tableAccount['payer_id'].eq(orgId),
            tableAccountItem['reexposeItem_id'].isNull(),
            tableAccount['date'].ge(begDate.toString('yyyy-MM-dd')),
            tableAccount['date'].le(endDate.toString('yyyy-MM-dd')),
            tableAccount['deleted'].eq(0),
            tableAccountItem['deleted'].eq(0)
        ]
    )

def selectDataCountClient(begDate, endDate, orgId):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableEvent = db.table('Event')
    queryTable = tableAccount
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
    return db.selectStmt(
        queryTable,
        'COUNT(DISTINCT Event.`client_id`) AS countClient',
        where=[
            tableAccount['payer_id'].eq(orgId),
            tableAccountItem['reexposeItem_id'].isNull(),
            tableAccount['date'].ge(begDate.toString('yyyy-MM-dd')),
            tableAccount['date'].le(endDate.toString('yyyy-MM-dd')),
            tableAccount['deleted'].eq(0),
            tableAccountItem['deleted'].eq(0)
        ]
    )

def selectSecondDataOrg(orgId):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableSecondAccountItem = db.table('Account_Item').alias('SecondAccountItem')
    queryTable = tableAccount
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
    queryTable = queryTable.innerJoin(tableSecondAccountItem, tableSecondAccountItem['master_id'].eq(tableAccountItem['reexposeItem_id']))
    return db.selectStmt(
        queryTable,
        'COUNT(Account_Item.`visit_id`) AS countVisit',
        where=[
            tableAccount['payer_id'].eq(orgId),
            tableAccount['deleted'].eq(0),
            tableAccountItem['deleted'].eq(0)
        ]
    )

def selectSecondDataSumPrice(orgId):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableSecondAccountItem = db.table('Account_Item').alias('SecondAccountItem')
    queryTable = tableAccount
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
    queryTable = queryTable.innerJoin(tableSecondAccountItem, tableSecondAccountItem['master_id'].eq(tableAccountItem['reexposeItem_id']))
    return db.selectStmt(
        queryTable,
        'SUM(SecondAccountItem.`sum`) AS sumPrice',
        where=[
            tableAccount['payer_id'].eq(orgId),
            tableAccount['deleted'].eq(0),
            tableAccountItem['deleted'].eq(0)
        ]
    )

def selectSecondDataCountClient(orgId):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableSecondAccountItem = db.table('Account_Item').alias('SecondAccountItem')
    tableEvent = db.table('Event')
    queryTable = tableAccount
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
    queryTable = queryTable.innerJoin(tableSecondAccountItem, tableSecondAccountItem['master_id'].eq(tableAccountItem['reexposeItem_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableSecondAccountItem['event_id']))
    return db.selectStmt(
        queryTable,
        'COUNT(DISTINCT Event.`client_id`) AS countClient',
        where=[
            tableAccount['payer_id'].eq(orgId),
            tableAccount['deleted'].eq(0),
            tableAccountItem['deleted'].eq(0)
        ]
    )


class CConsolidatedFinanceSumSetup(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводный счёт')

    def getSetupDialog(self, parent):
        result = CConsolidatedFinanceSumSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):

        begDate = params.get('begDate')
        endDate = params.get('endDate')

        tableColumns = [
            ( '40%', u'Название организации', CReportBase.AlignRight),
            ( '20%', u'Количество посещений', CReportBase.AlignRight),
            ( '20%', u'Количество физических лиц', CReportBase.AlignRight),
            ( '20%', u'Стоимость', CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сводный счёт:')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        nullValue = 'NULL'
        query = QtGui.qApp.db.query(selectDataOrg(nullValue, begDate, endDate))
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceString(record.value('shortName')))
            table.setText(i, 1, forceString(record.value('countVisit')))
            queryCountClient = QtGui.qApp.db.query(selectDataCountClient(begDate, endDate, forceString(record.value('OrgId'))))
            countClient = 0
            while queryCountClient.next() :
                recordCountClient = queryCountClient.record()
                countClient += forceInt(recordCountClient.value('countClient'))
            table.setText(i, 2, countClient)
            queryPrice = QtGui.qApp.db.query(selectDataSumPrice(begDate, endDate, forceString(record.value('OrgId'))))
            sumPrice = 0
            while queryPrice.next() :
                recordPrice = queryPrice.record()
                sumPrice += forceInt(recordPrice.value('sumPrice'))
            table.setText(i, 3, sumPrice)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        nullValue = 'NOT NULL'
        query = QtGui.qApp.db.query(selectDataOrg(nullValue, begDate, endDate))
        while query.next() :
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceString(record.value('shortName')))
            querySecondDataOrg = QtGui.qApp.db.query(selectSecondDataOrg(forceString(record.value('OrgId'))))
            recordSecondDataOrg = querySecondDataOrg.record()
            table.setText(i, 1, forceInt(recordSecondDataOrg.value('countVisit')))
            queryCountClient = QtGui.qApp.db.query(selectSecondDataCountClient(forceString(record.value('OrgId'))))
            countClient = 0
            while queryCountClient.next() :
                recordCountClient = queryCountClient.record()
                countClient += forceInt(recordCountClient.value('countClient'))
            table.setText(i, 2, countClient)
            queryPrice = QtGui.qApp.db.query(selectSecondDataSumPrice(forceString(record.value('OrgId'))))
            sumPrice = 0
            while queryPrice.next() :
                recordPrice = queryPrice.record()
                sumPrice += forceInt(recordPrice.value('sumPrice'))
            table.setText(i, 3, sumPrice)

        return doc

class CConsolidatedFinanceSumSetupDialog(QtGui.QDialog, Ui_ConsolidatedFinanceSumSetup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        return result