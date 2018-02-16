# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.Utils      import forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportAttachmentDoctors import Ui_ReportAttachmentDoctors


def selectData(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)

    db = QtGui.qApp.db

    tableClient           = db.table('Client')
    tableClientSocStatus  = db.table('ClientSocStatus')
    tableSocStatusType    = db.table('rbSocStatusType')
    tableSocStatusClass   = db.table('rbSocStatusClass')

    queryTable = tableClient.innerJoin(tableClientSocStatus, tableClientSocStatus['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableSocStatusClass, tableSocStatusClass['id'].eq(tableClientSocStatus['socStatusClass_id']))
    queryTable = queryTable.innerJoin(tableSocStatusType, tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id']))

    cols = [tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableSocStatusClass['code'],
            tableSocStatusType['name']]

    cond = [tableClientSocStatus['begDate'].dateLe(endDate),
            tableClientSocStatus['begDate'].dateGe(begDate),
            tableClient['deleted'].eq(0),
            tableClientSocStatus['deleted'].eq(0)]

    order = tableSocStatusType['name'].name()

    stmt = db.selectStmt(queryTable, cols, cond, order=order)
    query = db.query(stmt)
    return query

class CReportAttachmentDoctors(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Прикрепление по врачам')

    def getSetupDialog(self, parent):
        result = CAttachmentDoctors(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        if not query:
            return doc
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%5',
                        [u'№'], CReportBase.AlignRight),
                        ('%50',
                        [u'Клиент'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)
        currentPerson = None
        countPatient = 0
        while query.next():
            record = query.record()
            codeSocStatusType   = forceString(record.value('code'))
            namePatient         = forceString(record.value('lastName')) +' '+ forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
            namePerson          = forceString(record.value('name'))
            if codeSocStatusType == '12vr':
                if namePerson != currentPerson:
                    if currentPerson:
                        i = table.addRow()
                        table.setText(i, 0, u'Итого по врачу', charFormat=boldItalicChars)
                        table.setText(i, 1, countPatient, charFormat=boldItalicChars)
                        countPatient = 0
                if namePerson != currentPerson:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 2)
                    currentPerson = namePerson
                    i = table.addRow()
                    table.setText(i, 0, namePerson, charFormat = boldItalicChars, blockFormat = CReportBase.AlignLeft)
                    table.mergeCells(i, 0, 1, 2)
                i = table.addRow()
                countPatient += 1
                table.setText(i, 0, countPatient)
                table.setText(i, 1, namePatient)
        i = table.addRow()
        table.setText(i, 0, u'', charFormat=boldItalicChars)
        table.setText(i, 0, u'Итого по врачу', charFormat=boldItalicChars)
        table.setText(i, 1, countPatient, charFormat=boldItalicChars)
        return doc

class CAttachmentDoctors(QtGui.QDialog, Ui_ReportAttachmentDoctors):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        return params
