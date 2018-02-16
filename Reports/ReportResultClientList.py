# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                  import forceString
from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase
from Ui_ReportResultClientListSetup import Ui_ReportResultClientListSetup


def selectData(begDate, endDate):

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableDeferredQueue = db.table('DeferredQueue')
    tableVrbPerson = db.table('vrbPerson')
    tableRbDeferredQueueStatus = db.table('rbDeferredQueueStatus')
    tableRbSpeciality = db.table('rbSpeciality')
    tableAction = db.table('Action')
    tablePerson = db.table('Person')
    queryTable = tableDeferredQueue
    queryTable = queryTable.leftJoin(tableClient, tableDeferredQueue['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableVrbPerson, tableDeferredQueue['person_id'].eq(tableVrbPerson['id']))
    queryTable = queryTable.leftJoin(tableRbDeferredQueueStatus, tableDeferredQueue['status_id'].eq(tableRbDeferredQueueStatus['id']))
    queryTable = queryTable.leftJoin(tableRbSpeciality, tableDeferredQueue['speciality_id'].eq(tableRbSpeciality['id']))
    queryTable = queryTable.leftJoin(tableAction, tableDeferredQueue['action_id'].eq(tableAction['id']))
    queryTable = queryTable.leftJoin(tablePerson, tableAction['person_id'].eq(tablePerson['id']))

    cols = [
        tableDeferredQueue['client_id'],
        tableClient['lastName'].alias('clientLastName'),
        tableClient['firstName'].alias('clientFirstName'),
        tableClient['patrName'].alias('clientPatrName'),
        tableClient['birthDate'],
        tableRbSpeciality['name'].alias('specialityName'),
        tableVrbPerson['name'].alias('selectedPersonName'),
        tableDeferredQueue['maxDate'],
        tableDeferredQueue['comment'],
        tablePerson['lastName'].alias('personLastName'),
        tablePerson['firstName'].alias('personFirstName'),
        tablePerson['patrName'].alias('personPatrName'),
        tableAction['directionDate']
    ]

    cond = []
    cond.append(tableRbDeferredQueueStatus['code'].eq(2))
    cond.append(tableDeferredQueue['createDatetime'].dateGe(begDate.toString('yyyy-MM-dd')))
    cond.append(tableDeferredQueue['createDatetime'].dateLe(endDate.toString('yyyy-MM-dd')))
    cond.append(tableClient['deleted'].eq(0))

    return db.selectStmt(queryTable, cols, cond)

class CResultClientList(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Результаты записи')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):

        begDate = params.get('begDate')
        endDate = params.get('endDate')

        tableColumns = [
            ( '10%', u'Код', CReportBase.AlignRight),
            ( '15%', u'Ф.И.О. пациента', CReportBase.AlignRight),
            ( '6%', u'Дата рождения', CReportBase.AlignRight),
            ( '6%', u'Специальность', CReportBase.AlignRight),
            ( '15%', u'Выбранный врач', CReportBase.AlignRight),
            ( '6%', u'Максимальная дата', CReportBase.AlignRight),
            ( '15%', u'Назначенный врач', CReportBase.AlignRight),
            ( '6%', u'Дата приёма', CReportBase.AlignRight),
            ( '10%', u'Комментарий', CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Результаты записи:')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        query = QtGui.qApp.db.query(selectData(begDate, endDate))
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceString(record.value('client_id')))
            table.setText(i, 1, forceString(record.value('clientLastName')) + ' ' + forceString(record.value('clientFirstName')) + ' ' + forceString(record.value('clientPatrName')))
            table.setText(i, 2, forceString(record.value('birthDate')))
            table.setText(i, 3, forceString(record.value('specialityName')))
            table.setText(i, 4, forceString(record.value('selectedPersonName')))
            table.setText(i, 5, forceString(record.value('maxDate'))[0:10])
            table.setText(i, 6, forceString(record.value('personLastName')) + ' ' + forceString(record.value('personFirstName')) + ' ' + forceString(record.value('personPatrName')))
            table.setText(i, 7, forceString(record.value('directionDate')))
            table.setText(i, 8, forceString(record.value('comment')))

        return doc

class CReportUnderageMedicalExaminationSetupDialog(QtGui.QDialog, Ui_ReportResultClientListSetup):
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
