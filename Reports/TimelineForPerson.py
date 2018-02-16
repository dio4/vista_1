# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceDate, forceRef, forceString, forceTime, firstMonthDay, lastMonthDay
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_TimelineSetupDialog import Ui_TimelineSetupDialog


def selectRawData(params):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')

    cond = []
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    personId = params.get('personId', None)
    personIdList = params.get('personIdList', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', None)
    activityId = params.get('activityId', None)
    if begDate:
        cond.append(tableEvent['setDate'].ge(begDate))
    if endDate:
        cond.append(tableEvent['setDate'].lt(endDate.addDays(1)))
    if personId:
        cond.append(tableEvent['setPerson_id'].eq(personId))
    if personIdList:
        cond.append(tableEvent['setPerson_id'].inlist(personIdList))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        if not personId and not personIdList:
            cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if activityId:
        tablePersonActivity = db.table('Person_Activity')
        cond.append(db.existsStmt(tablePersonActivity,
                                  [tablePersonActivity['master_id'].eq(tablePerson['id']),
                                   tablePersonActivity['activity_id'].eq(activityId),
                                   tablePersonActivity['deleted'].eq(0),
                                  ]))
#        cond.append('EXISTS (SELECT * FROM Person_Activity WHERE Person_Activity.master_id=Event.setPerson_id AND Person_Activity.deleted=0 AND Person_Activity.activity_id=%d)'%activityId)
    stmt="""
SELECT
    Event.setDate AS date, Event.setPerson_id AS person_id, APT.name AS paramName, APTimeValue.value AS time, APStringValue.value AS office
FROM Action
INNER JOIN Event ON Event.id = Action.event_id
INNER JOIN Person ON Person.id = Event.setPerson_id
INNER JOIN EventType ON EventType.id = Event.eventType_id
INNER JOIN ActionType ON ActionType.id = Action.actionType_id
INNER JOIN ActionPropertyType    AS APT  ON APT.actionType_id = ActionType.id AND APT.name IN ('begTime', 'begTime1', 'begTime2', 'endTime', 'endTime1', 'endTime2', 'office', 'office1', 'office2')
LEFT  JOIN ActionProperty        AS AP   ON AP.action_id  = Action.id AND AP.type_id = APT.id
LEFT  JOIN ActionProperty_Time   AS APTimeValue   ON APTimeValue.id   = AP.id
LEFT  JOIN ActionProperty_String AS APStringValue ON APStringValue.id = AP.id
WHERE Action.deleted =0
AND Event.deleted =0
AND ActionType.code = 'amb'
AND EventType.code = '0'
AND (APTimeValue.value IS NOT NULL OR APStringValue.value IS NOT NULL)
AND %s
ORDER BY Event.setDate, Event.setPerson_id"""
    return db.query(stmt % db.joinAnd(cond))


def bulkToRanges(bulk):
    result = []
    if 'begTime1' in bulk and 'endTime1' in bulk:
        result.append( (bulk.get('office1',''), bulk['begTime1'], bulk['endTime1']))
    if 'begTime2' in bulk and 'endTime2' in bulk:
        result.append( (bulk.get('office2',''), bulk['begTime2'], bulk['endTime2']))
    if not result and 'begTime' in bulk and 'endTime' in bulk:
        result.append( (bulk.get('office',''), bulk['begTime'], bulk['endTime']))
    return result


def selectData(params):
    result = []
    query = selectRawData(params)
    prevDate = None
    prevPersonId = None
    bulk = {}
    while query.next():
        record = query.record()
        date = forceDate(record.value('date')).toPyDate() # because QDate cannot work as key in dict
        personId = forceRef(record.value('person_id'))
        if prevDate != date or prevPersonId != personId:
            if prevDate:
                for office, begTime, endTime in bulkToRanges(bulk):
                    result.append( (prevDate, prevPersonId, office, begTime, endTime) )
                bulk = {}
            prevDate = date
            prevPersonId = personId

        paramName = forceString(record.value('paramName'))
        if paramName.startswith('office'):
            paramValue = forceString(record.value('office'))
        else:
            paramValue = forceTime(record.value('time'))
        bulk[paramName] = paramValue
    for office, begTime, endTime in bulkToRanges(bulk):
        result.append( (prevDate, prevPersonId, office, begTime, endTime) )
    return result



class CTimelineForPerson(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Расписание приёма врача')


    def build(self, description, params):
        isCommon = params.get('isCommon', False)
        db = QtGui.qApp.db
        reportData = {}
        personNames = {}
        data = selectData(params)
        for date, personId, office, begTime, endTime in data:
            if isCommon:
                mainKey = forceDate(date).toString('dd.MM.yyyy')
                key = personId
            else:
                mainKey = personId
                key = date
            personData = reportData.setdefault(mainKey, {})
            if personId not in personNames.keys():
                personNames[personId] = forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            ranges = personData.setdefault(key, [])
            ranges.append((begTime, endTime, office))
        personNames.keys().sort()

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(description)
        cursor.insertBlock()
        if isCommon:
            self.outPersonCommonTable(cursor, personNames, reportData, params.get('begDate'), params.get('endDate'))
        else:
            for personId in personNames.keys():
                self.outPersonTable(cursor, personNames[personId], reportData[personId])
        return doc

    def outPersonCommonTable(self, cursor,  personNames, reportData, begDate, endDate):
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertBlock()

        tableColumns = [('5%', [''], CReportBase.AlignLeft)]
        listPersonId = []
        for personId in personNames.keys():
            tableColumns.append(('5%', [personNames[personId]], CReportBase.AlignLeft))
            listPersonId.append(personId)
        table = createTable(cursor, tableColumns)
        currentDate = forceDate(begDate)
        while currentDate != endDate.addDays(1):
            i = table.addRow()
            table.setText(i, 0, currentDate.toString('dd.MM.yyyy') + ', ' + forceString(QtCore.QDate.shortDayName(currentDate.dayOfWeek())).capitalize())
            key = currentDate.toString('dd.MM.yyyy')
            for index, personId in enumerate(listPersonId):
                try:
                    for value in xrange(len(reportData[key][personId])):
                        table.setText(i, index + 1, reportData[key][personId][value][0].toString('hh:mm') + '-' + reportData[key][personId][value][1].toString('hh:mm') + u' каб. ' + reportData[key][personId][value][2] + '\n')
                except KeyError:
                    pass
            currentDate = currentDate.addDays(1)


    def outPersonTable(self, cursor, personName, personData):
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(personName)
        cursor.insertBlock()

        tableColumns = []
        for weekDay in xrange(7):
            name = forceString(QtCore.QDate.longDayName(weekDay+1)).capitalize()
            tableColumns.append(('5%', [name, u'Дата'],     CReportBase.AlignLeft))
            tableColumns.append(('5%', ['',   u'Приём'   ], CReportBase.AlignLeft))
            tableColumns.append(('3%', ['',   u'Кабинет' ], CReportBase.AlignLeft))
        table = createTable(cursor, tableColumns)
        for weekDay in xrange(7):
            table.mergeCells(0, weekDay*3, 1, 3)

        dateList = personData.keys()
        dateList.sort()
        prevIsoWeek = None
        week = [None]*7
        for date in dateList:
            isoYear, isoWeek, isoWeekDay = date.isocalendar()
            if prevIsoWeek != isoWeek:
                if prevIsoWeek:
                    self.outWeek(table, week)
                    week = [None]*7
                prevIsoWeek = isoWeek
            ranges = personData[date]
            ranges.sort()
            week[isoWeekDay-1] = date, ranges
        self.outWeek(table, week)


    def outWeek(self, table, week):
        rowCount = 0
        for weekDay, day in enumerate(week):
            if day:
                rowCount = max(rowCount, len(day[1])) # ranges

        i = table.addRow()
        for dummy in xrange(rowCount-1):
            table.addRow()
        for weekDay, day in enumerate(week):
            table.mergeCells(i, weekDay*3, rowCount, 1)
            if day:
                table.setText(i, weekDay*3, forceString(QtCore.QDate(day[0])))
                for j, r in enumerate(day[1]):
                    table.setText(i+j, weekDay*3+1, r[0].toString('HH:mm')+'-'+r[1].toString('HH:mm'))
                    table.setText(i+j, weekDay*3+2, r[2])
            else:
                table.mergeCells(i, weekDay*3+1, rowCount, 1)
                table.mergeCells(i, weekDay*3+2, rowCount, 1)


class CTimelineForPersonEx(CTimelineForPerson):
    def exec_(self):
        CTimelineForPerson.exec_(self)


    def getSetupDialog(self, parent):
        result = CTimelineSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
#        params['accountIdList'] = self.accountIdList
        return CTimelineForPerson.build(self, '\n'.join(self.getDescription(params)), params)


class CTimelineSetupDialog(QtGui.QDialog, Ui_TimelineSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.chkCommon.setToolTip(u'Отображение расписания в виде таблицы, в шапке которой врачи, а в первом столбце даты.')


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(date)))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(date)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkCommon.setChecked(params.get('isCommon', False))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        result['isCommon'] = self.chkCommon.isChecked()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)