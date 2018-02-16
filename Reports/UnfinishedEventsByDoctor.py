# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceBool, forceInt, forceString
from Orgs.Utils         import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId):
    stmt="""
SELECT
    count(Event.id) AS `count`,
    EventType.name AS eventTypeName,
    vrbPersonWithSpeciality.name AS personName,
    Event.execDate IS NOT NULL AS isDone,
    (EventType.mesRequired AND Event.MES_id IS NULL) AS isMesUnspecified,
    IF(Event.MES_id IS NOT NULL,
       DATEDIFF(IF(Event.execDate IS NOT NULL, Event.execDate, CURDATE()), Event.setDate)+1>mes.MES.avgDuration,
       0) AS isMesRunout
FROM
    Event
    LEFT JOIN EventType ON EventType.id = Event.eventType_id
    LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
    LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.execPerson_id
    LEFT JOIN mes.MES ON mes.MES.id = Event.MES_id
WHERE
    rbEventTypePurpose.code != '0' AND %s
GROUP BY
    Event.eventType_id, Event.execPerson_id, isDone, isMesUnspecified, isMesRunout
"""
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tablePerson = db.table('vrbPersonWithSpeciality')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))

    cond.append(tableEvent['setDate'].ge(begDate))
    cond.append(tableEvent['setDate'].lt(endDate.addDays(1)))
#    cond.append(tableEvent['execDate'].isNull())
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        cond.append(db.table('EventType')['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    return db.query(stmt % (db.joinAnd(cond)))


class CUnfinishedEventsByDoctor(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводка по незакрытым случаям лечения, разделение по врачам')


    def getSetupDialog(self, parent):
        result = CUnfinishedEventsReportSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        query = selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId)

        reportData = {}
        dataSize = 4
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record = query.record()
            count  = forceInt(record.value('count'))
            eventTypeName = forceString(record.value('eventTypeName'))
            personName = forceString(record.value('personName'))
            isDone = forceBool(record.value('isDone'))
            isMesUnspecified = forceBool(record.value('isMesUnspecified'))
            isMesRunout = forceBool(record.value('isMesRunout'))
            key = (eventTypeName, personName)
            reportLine = reportData.get(key, None)
            if not reportLine:
                reportLine = [0]*dataSize
                reportData[key] = reportLine
            reportLine[0] += count
            if not isDone:
                reportLine[1] += count
            if isMesUnspecified:
                reportLine[2] += count
            if isMesRunout:
                reportLine[3] += count

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '5%', [u'№'            ], CReportBase.AlignRight),
            ('40%', [u'Врач'         ], CReportBase.AlignLeft),
            ('15%', [u'Всего'        ], CReportBase.AlignRight),
            ('15%', [u'Не закрыто'   ], CReportBase.AlignRight),
            ('15%', [u'МЭС не указан'], CReportBase.AlignRight),
            ('15%', [u'превышена средняя длительность по МЭС' ], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        keys = reportData.keys()
        keys.sort()
        totalByEventType = [0]*dataSize
        total = [0]*dataSize
        prevEventTypeName = None
        for key in keys:
            eventTypeName, personName = key
            if prevEventTypeName != eventTypeName:
                if prevEventTypeName is not None:
                    self.outTotal(table, u'итого', totalByEventType)
                    totalByEventType = [0]*dataSize
                i = table.addRow()
                table.mergeCells(i, 0, 1, 6)
                table.setText(i, 0, eventTypeName, CReportBase.ReportSubTitle, CReportBase.AlignLeft)
                prevEventTypeName = eventTypeName
                n = 0
            i = table.addRow()
            n += 1
            table.setText(i, 0, n)
            table.setText(i, 1, personName)
            for j, v in enumerate(reportData[key]):
                table.setText(i, 2+j, v)
                totalByEventType[j]+=v
                total[j]+=v
        if prevEventTypeName is not None:
            self.outTotal(table, u'итого', totalByEventType)
        self.outTotal(table, u'Итого по всем типам событий', total)
        return doc

    def outTotal(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal, CReportBase.AlignLeft)
        for j, v in enumerate(total):
            table.setText(i, 2+j, v, CReportBase.TableTotal)
        table.mergeCells(i, 0, 1, 2)


from Ui_UnfinishedEventsReportSetup import Ui_UnfinishedEventsReportSetupDialog


class CUnfinishedEventsReportSetupDialog(QtGui.QDialog, Ui_UnfinishedEventsReportSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSpeciality.setTable('rbSpeciality', True)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)
