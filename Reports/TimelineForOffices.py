# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils              import forceString
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.TimelineForPerson  import CTimelineSetupDialog, selectData


class CTimelineForOffices(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Расписание кабинетов')


    def build(self, description, params):
        db = QtGui.qApp.db
        reportData = {}
        mapPersonIdToName = {}
        data = selectData(params)
        # список (date, personId, office, begTime, endTime)
        # перестраивается в иерархию reportData[date][office][(begTime, endTime, personId)...]
        for date, personId, office, begTime, endTime in data:
            dateData = reportData.setdefault(date, {})
            ranges   = dateData.setdefault(office, [])
            ranges.append((begTime, endTime, personId))
            if not personId in mapPersonIdToName:
                mapPersonIdToName[personId] = forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(description)
        cursor.insertBlock()

        self.outOrgStructureTable(cursor, reportData, mapPersonIdToName)
        return doc


    def outOrgStructureTable(self, cursor, orgStructureData, mapPersonIdToName):
        cursor.movePosition(QtGui.QTextCursor.End)
#        cursor.setCharFormat(CReportBase.ReportTitle)
#        cursor.insertText(personName)
#        cursor.insertBlock()

        tableColumns = [('5%', [u'Кабинет'],  CReportBase.AlignLeft)]
        for weekDay in xrange(7):
            name = forceString(QtCore.QDate.longDayName(weekDay+1)).capitalize()
            tableColumns.append(('5%', [name, u'Приём'], CReportBase.AlignLeft))
            tableColumns.append(('8%', ['',   u'Врач' ], CReportBase.AlignLeft))
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        for weekDay in xrange(7):
            table.mergeCells(0, weekDay*2+1, 1, 2)

        dateList = orgStructureData.keys()
        dateList.sort()
        prevIsoWeek = None
        week = [None]*7
        officesSet = set()
        for date in dateList:
            isoYear, isoWeek, isoWeekDay = date.isocalendar()
            if prevIsoWeek != isoWeek:
                if prevIsoWeek:
                    self.outWeek(table, week, officesSet, mapPersonIdToName)
                    week = [None]*7
                    officesSet = set()
                prevIsoWeek = isoWeek
            dateData = orgStructureData[date]
            officesSet.update(dateData.keys())
            week[isoWeekDay-1] = date, dateData
        self.outWeek(table, week, officesSet, mapPersonIdToName)


    def outWeek(self, table, week, officesSet, mapPersonIdToName):
        weekFirstRow = table.addRow()
        for weekDay, day in enumerate(week):
            table.mergeCells(weekFirstRow, weekDay*2+1, 1, 2)
            if day:
                table.setText(weekFirstRow, weekDay*2+1, forceString(QtCore.QDate(day[0])), CReportBase.TableHeader, CReportBase.AlignCenter)
        officesList = list(officesSet)
        officesList.sort()
        weekRowCount = 0
        for office in officesList:
            weekRowCount += self.outOffice(table, week, office, mapPersonIdToName)


    def outOffice(self, table, week, office, mapPersonIdToName):
        rowCount = 0
        for weekDay, day in enumerate(week):
            if day and office in day[1]:
                rowCount = max(rowCount, len(day[1][office])) # ranges

        i = table.addRow()
        for dummy in xrange(rowCount-1):
            table.addRow()

        table.mergeCells(i, 0, rowCount, 1)
        table.setText(i, 0, office, CReportBase.TableHeader, CReportBase.AlignCenter)
        for weekDay, day in enumerate(week):
            if day and office in day[1]:
                ranges = [(begTime, endTime, mapPersonIdToName[personId])
                           for begTime, endTime, personId in day[1][office]]
                ranges.sort()
                for j, (begTime, endTime, personName) in enumerate(ranges):
                    table.setText(i+j, weekDay*2+1, begTime.toString('HH:mm')+'-'+endTime.toString('HH:mm'))
                    table.setText(i+j, weekDay*2+2, personName)
        return rowCount


class CTimelineForOfficesEx(CTimelineForOffices):
    def exec_(self):
        CTimelineForOffices.exec_(self)


    def getSetupDialog(self, parent):
        result = CTimelineSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
#        params['accountIdList'] = self.accountIdList
        return CTimelineForOffices.build(self, '\n'.join(self.getDescription(params)), params)