# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureID = params.get('orgStructureID', None)
    db = QtGui.qApp.db
    cond=[]
    tablePerson = db.table('Person')
    tableDeferredQueue = db.table('DeferredQueue')
    cond.append(db.joinOr([db.joinAnd([tableDeferredQueue['createDatetime'].compareDatetime(begDate,'>=', onlyDate=True),tableDeferredQueue['createDatetime'].compareDatetime(endDate,'<=', onlyDate=True)]),db.joinAnd([tableDeferredQueue['modifyDatetime'].compareDatetime(begDate,'>=', onlyDate=True),tableDeferredQueue['modifyDatetime'].compareDatetime(endDate,'<=', onlyDate=True)])]))
    if orgStructureID:
        cond.append(tablePerson['orgStructure_id'].inlist(db.getDescendants('OrgStructure', 'parent_id', orgStructureID)))
    stmt = u'''
        SELECT
            rbPost.name,
            COUNT(DISTINCT DeferredQueue.id) as allRecording,
            COUNT(DISTINCT IF(rbDeferredQueueStatus.code = 2, DeferredQueue.id, NULL)) as consultationRecording
        FROM DeferredQueue
        INNER JOIN Person ON Person.id = DeferredQueue.person_id AND Person.deleted = 0
        INNER JOIN rbPost ON rbPost.id = Person.post_id
        INNER JOIN rbDeferredQueueStatus ON rbDeferredQueueStatus.id = DeferredQueue.status_id
        WHERE %s
        GROUP BY rbPost.name
        ''' % (db.joinAnd(cond))
    return db.query(stmt)

class CReportDeferredQueueCount(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Количество записей в журнале отложенного спроса')

    def getSetupDialog(self, parent):
        result = CReportDeferredQueueCountSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def dumpParams(self, cursor, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())

        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result

        description = []
        if begDate and endDate:
            description.append(u'за период' + dateRangeAsStr(begDate, endDate))

        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Количество записей в журнале отложенного спроса')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()

        tableColumns = [
            ('10%', [u'№ п/п' ],                                CReportBase.AlignRight),
            ('30%',[u'Должность врача'],                        CReportBase.AlignLeft),
            ('30%', [u'Записаны в журнал отложенного спроса'  ], CReportBase.AlignCenter),
            ('30%', [u'Обеспечены консультацией'     ],          CReportBase.AlignCenter)
            ]

        table = createTable(cursor, tableColumns)
        sumAllRecording = 0
        sumConsultationRecording = 0
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            name = forceString(record.value('name'))
            allRecording = forceInt(record.value('allRecording'))
            consultationRecording = forceInt(record.value('consultationRecording'))
            sumAllRecording += allRecording
            sumConsultationRecording += consultationRecording
            i = table.addRow()
            table.setText(i, 0, forceString(i))
            table.setText(i, 1, name)
            table.setText(i, 2, forceString(allRecording))
            table.setText(i, 3, forceString(consultationRecording))
        i = table.addRow()
        table.setText(i, 1, u'Итого:')
        table.setText(i, 2, forceString(sumAllRecording))
        table.setText(i, 3, forceString(sumConsultationRecording))
        return doc

from Ui_ReportDeferredQueueCountSetup import Ui_ReportDeferredQueueCountSetupDialog

class CReportDeferredQueueCountSetupDialog(QtGui.QDialog, Ui_ReportDeferredQueueCountSetupDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        pass
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureID'] = self.cmbOrgStructure.value()
        return result

