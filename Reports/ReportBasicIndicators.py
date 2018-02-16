# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################
import copy

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceBool, forceInt, forceRef, forceString

from Orgs.Utils         import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params, flagVisits=False):
    db = QtGui.qApp.db

    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypeId = forceRef(params.get('eventTypeId', None))
    eventPurposeId = forceRef(params.get('eventPurposeId', None))
    orgStructureId = forceRef(params.get('orgStructureId'))
    personId = forceInt(params.get('personId', None))
    groupByProfile = forceBool(params.get('groupByProfile', False))

    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableRBEventGoal = db.table('rbEventGoal')
    tableVisit = db.table('Visit')
    tableClient = db.table('Client')
    tablePerson = db.table('Person')
    tableRBSpeciality = db.table('rbSpeciality')

    cond = [tableEvent['deleted'].eq(0),
            tableClient['deleted'].eq(0)]
    if flagVisits:
        cond.append(tableVisit['deleted'].eq(0))

    if begDate:
        cond.append(tableEvent['execDate'].dateGe(begDate))
    if endDate:
        cond.append(tableEvent['execDate'].dateLt(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

    mainTable = 'Visit' if flagVisits else 'Event'
    dateField = 'Visit.date' if flagVisits else 'Event.setDate'
    cols = ['COUNT(DISTINCT %s.id) AS countTotal' % mainTable,
            tableRBEventGoal['regionalCode'].alias('goalCode'),
            'COUNT(DISTINCT IF(age(Client.birthDate, %s) <= 17, %s.id, NULL)) as countChildren' % (dateField, mainTable),
            ]

    queryTable = tableEvent.innerJoin(tableRBEventGoal, tableRBEventGoal['id'].eq(tableEvent['goal_id']))
    queryTable = queryTable.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    if flagVisits:
        queryTable = queryTable.innerJoin(tableVisit, tableVisit['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableVisit['person_id']))
    else:
        queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))

    groupBy = [tableRBEventGoal['regionalCode']]
    orderBy = []

    if groupByProfile:
        queryTable = queryTable.leftJoin(tableRBSpeciality, tableRBSpeciality['id'].eq(tablePerson['speciality_id']))
        groupBy.append(tableRBSpeciality['name'])
        cols.append(tableRBSpeciality['name'].alias('specialityName'))
        orderBy.append(tableRBSpeciality['name'])

    stmt = db.selectStmt(queryTable, cols, cond, groupBy, orderBy)
    return db.query(stmt)

    # whereBasic = ''
    # if begDate:
    #     whereBasic += ''' AND DATE(Event.execDate) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    # if endDate:
    #     whereBasic += ''' AND DATE(Event.execDate) < DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    # if eventTypeId:
    #     whereBasic += ''' AND Event.eventType_id = %s''' % eventTypeId
    # if personId:
    #     whereBasic += ''' AND Event.execPerson_id = %s''' % personId
    # whereChildren = ''' AND TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') <= 17''' % QtCore.QDate.currentDate().toString('yyyy-MM-dd')
    # innerJoinClient = '''INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0'''

    # regionalCode = [0, 0, 2, 2, 3, 3, 5, 5, 4, 4, 1, 1]
    # result = []
    # isChildren = False
    #
    # for code in regionalCode:
    #     if code == 0:
    #         andCode = ''
    #     else:
    #         andCode = '''AND rbEventGoal.regionalCode = %s''' % code
    #
    #     if isChildren:
    #         innerJoin = innerJoinClient
    #         where = whereBasic + whereChildren
    #         isChildren = False
    #     else:
    #         innerJoin = ''
    #         where = whereBasic
    #         isChildren = True
    #
    #     stmt = u'''
    #         SELECT
    #             COUNT(DISTINCT Event.id) as countEvent,
    #             COUNT(DISTINCT Visit.id) as countVisit
    #         FROM Event
    #         INNER JOIN rbEventGoal ON rbEventGoal.id = Event.goal_id %s
    #         INNER JOIN Visit ON Visit.event_id = Event.id AND Visit.deleted = 0
    #         %s
    #         WHERE Event.deleted = 0 %s
    #         GROUP BY rbEventGoal.code
    #         ''' % (andCode, innerJoin, where)
    #
    #     query = db.query(stmt)
    #     if query.first():
    #         record = query.record()
    #         result.append([forceInt(record.value('countEvent')), forceInt(record.value('countVisit'))])
    #     else:
    #         result.append([0, 0])
    #
    # return result

class CReportBasicIndicators(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Основные показатели деятельности медицинских организаций')

    def getSetupDialog(self, parent):
        result = CReportDeferredQueueCountSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def prepareData(self, eventQuery, visitQuery, groupByProfile):
        mapGoalCodeToRow = {2:1, 3:2, 5:3, 4:4, 1:5, 7:6}
        data = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        if groupByProfile:
            result = {}
            while eventQuery.next():
                record = eventQuery.record()
                specialityName = forceString(record.value('specialityName'))
                dataItem = result.setdefault(specialityName, copy.deepcopy(data))
                goal = forceInt(record.value('goalCode'))
                row = mapGoalCodeToRow.get(goal, None)
                if row is not None and row != 0:
                    events = forceInt(record.value('countTotal'))
                    childEvents = forceInt(record.value('countChildren'))
                    dataItem[row][1] += events
                    dataItem[row][3] += childEvents
                    dataItem[0][1] += events
                    dataItem[0][3] += childEvents
                    # dataItem[row] = [0, events, 0, childEvents]
            while visitQuery.next():
                record = visitQuery.record()
                specialityName = forceString(record.value('specialityName'))
                dataItem = result.setdefault(specialityName, copy.deepcopy(data))
                goal = forceInt(record.value('goalCode'))
                row = mapGoalCodeToRow.get(goal, None)
                if row is not None and row != 0:
                    visits = forceInt(record.value('countTotal'))
                    childVisits = forceInt(record.value('countChildren'))
                    dataItem[row][0] += visits
                    dataItem[row][2] += childVisits
                    dataItem[0][0] += visits
                    dataItem[0][2] += childVisits
        else:
            result = data
            while eventQuery.next():
                record = eventQuery.record()
                goal = forceInt(record.value('goalCode'))
                row = mapGoalCodeToRow.get(goal, None)
                if row is not None and row != 0:
                    events = forceInt(record.value('countTotal'))
                    childEvents = forceInt(record.value('countChildren'))
                    data[row][1] += events
                    data[row][3] += childEvents
                    data[0][1] += events
                    data[0][3] += childEvents
                    # data[row] = [0, events, 0, childEvents]
            while visitQuery.next():
                record = visitQuery.record()
                goal = forceInt(record.value('goalCode'))
                row = mapGoalCodeToRow.get(goal, None)
                if row is not None and row != 0:
                    visits = forceInt(record.value('countTotal'))
                    childVisits = forceInt(record.value('countChildren'))
                    data[row][0] += visits
                    data[row][2] += childVisits
                    data[0][0] += visits
                    data[0][2] += childVisits

        return result

    def build(self, params):
        groupByProfile = params.get('groupByProfile', False)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Основные показатели деятельности медицинских организаций')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()

        tableColumns = [
            ('30%', [u'Наименование показателя', u'', u'1'], CReportBase.AlignLeft),
            ]
        if not groupByProfile:
            tableColumns += [
                        ('10%', [u'№ строки', u'', u'2'], CReportBase.AlignCenter),
                        ('30%', [u'Величина показателя', u'посещения', u'3'], CReportBase.AlignCenter),
                        ('30%', [u'', u'обращения', u'4'], CReportBase.AlignCenter) #,
            ]
        else:
            tableColumns += [
            ('30%', [u'Величина показателя', u'посещения', u'2'], CReportBase.AlignCenter),
            ('30%', [u'', u'обращения', u'3'], CReportBase.AlignCenter) #,
            ]

        tableRow = [
            (u'Посещения всего', u'01'),
            (u'из них: посещения, сделанные детьми', u'02'),
            (u'Посещения с профилактической целью', u'03'),
            (u'из них: посещения, сделанные детьми', u'04'),
            (u'Посещения в неотложной форме', u'05'),
            (u'из них: посещеня, сделанные детьми', u'06'),
            (u'Посещения при обращении по поводу заболевания', u'07'),
            (u'из них: посещения, сделанные детьми', u'08'),
            (u'Посещения с иными целями', u'09'),
            (u'из них: посещения, сделанные детьми', u'10'),
            (u'Посещения без уточнения цели', u'11'),
            (u'из них: посещения, сделанные детьми', u'12'),
            (u'Разовые посещения по поводу заболевания', u'13'),
            (u'из них: посещения, сделанные детьми', u'14'),
        ]

        table = createTable(cursor, tableColumns)
        eventQuery = selectData(params)
        visitQuery = selectData(params, True)
        self.setQueryText(forceString(eventQuery.lastQuery()) + '\n\n' + forceString(visitQuery.lastQuery()))
        result = self.prepareData(eventQuery, visitQuery, groupByProfile)

        table.mergeCells(0, 0, 2, 1)
        if groupByProfile:
            table.mergeCells(0, 1, 1, 2)
        else:
            table.mergeCells(0, 1, 2, 1)
            table.mergeCells(0, 2, 1, 2)
        #table.mergeCells(0, 4, 2, 1)

        if groupByProfile:

            for speciality in sorted(result.keys()):
                rows = result[speciality]
                i = table.addRow()
                table.setText(i, 0, speciality, fontBold=True)
                for j, rowData in enumerate(rows):
                    i = table.addRow()
                    table.setText(i, 0, tableRow[j*2][0])
                    table.setText(i, 1, rowData[0])
                    table.setText(i, 2, rowData[1])
                    i = table.addRow()
                    table.setText(i, 0, tableRow[j*2+1][0])
                    table.setText(i, 1, rowData[2])
                    table.setText(i, 2, rowData[3])

        else:
            for j, rowData in enumerate(result):
                i = table.addRow()
                table.setText(i, 0, tableRow[j*2][0])
                table.setText(i, 1, tableRow[j*2][1])
                table.setText(i, 2, rowData[0])
                table.setText(i, 3, rowData[1])
                i = table.addRow()
                table.setText(i, 0, tableRow[j*2+1][0])
                table.setText(i, 1, tableRow[j*2+1][1])
                table.setText(i, 2, rowData[2])
                table.setText(i, 3, rowData[3])

        return doc

from Ui_ReportBasicIndicatorsSetup import Ui_ReportBasicIndicatorsSetupDialog

class CReportDeferredQueueCountSetupDialog(QtGui.QDialog, Ui_ReportBasicIndicatorsSetupDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose')
        self.cmbEventType.setTable('EventType', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkGroupByProfile.setChecked(params.get('groupByProfile', False))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['groupByProfile'] = self.chkGroupByProfile.isChecked()
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)