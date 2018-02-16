# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from Events.Utils import getWorkEventTypeFilter

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportUnclosedEventsSetup import Ui_ReportUnclosedEventsSetupDialog
from library.Utils import forceString


def selectData(params):
    stmt = u'''
SELECT
    Client.id AS clientId,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    EventType.name AS eventTypeName,
    Event.id AS eventId,
    Event.setDate AS eventSetDate
FROM
    Client
    INNER JOIN Event ON Client.id = Event.client_id
    INNER JOIN EventType ON Event.eventType_id = EventType.id
WHERE
    %s
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypeId = params.get('eventTypeId', None)

    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableEventType = db.table('EventType')

    cond = [
        tableClient['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
        tableEventType['deleted'].eq(0),
        tableEvent['execDate'].isNull(),
        tableEvent['setDate'].dateGe(begDate),
        tableEvent['setDate'].dateLe(endDate)
    ]
    if eventTypeId is not None:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    return db.query(stmt % db.joinAnd(cond))


class CReportUnclosedEventsSetupDialog(QtGui.QDialog, Ui_ReportUnclosedEventsSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbEventType.setValue(params.get('eventTypeId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        return result


class CReportUnclosedEvents(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Незакрытые обращения")

    def getSetupDialog(self, parent):
        result = CReportUnclosedEventsSetupDialog(parent)
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
            ('10%', [u'Код'], CReportBase.AlignLeft),
            ('40%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('15%', [u'Код обращения'], CReportBase.AlignLeft),
            ('20%', [u'Тип обращения'], CReportBase.AlignLeft),
            ('15%', [u'Дата начала'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        clientMap = {}
        while query.next():
            record = query.record()
            clientId = forceString(record.value('clientId'))
            clientName = forceString(record.value('clientName'))
            eventTypeName = forceString(record.value('eventTypeName'))
            eventId = forceString(record.value('eventId'))
            eventSetDate = forceString(record.value('eventSetDate'))
            clientMap.setdefault((clientId, clientName), []).append((eventId, eventTypeName, eventSetDate))

        clientList = clientMap.keys()
        clientList.sort()
        for clientInfo in clientList:
            clientId, clientName = clientInfo
            events = clientMap[clientInfo]
            events.sort()

            i = table.addRow()
            table.setText(i, 0, clientId)
            table.setText(i, 1, clientName)

            eventsAmount = len(events)
            rows = [i]
            for eventNumber in xrange(eventsAmount - 1):
                rows.append(table.addRow())
            for column in xrange(2):
                table.mergeCells(i, column, eventsAmount, 1)
            for eventNumber in xrange(eventsAmount):
                row = rows[eventNumber]
                eventId, eventTypeName, eventSetDate = events[eventNumber]
                table.setText(row, 2, eventId)
                table.setText(row, 3, eventTypeName)
                table.setText(row, 4, eventSetDate)

        return doc

