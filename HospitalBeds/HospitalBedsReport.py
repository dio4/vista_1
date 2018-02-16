# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils              import forceInt, forceRef, forceString, monthNameGC, forceBool, forceDateTime

from Orgs.OrgStructComboBoxes   import COrgStructureModel

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase

from Ui_FeedReportDialog import Ui_FeedReportDialog


class CHospitalBedsReport(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Коечный фонд')


    def build(self, descr, idList):
        db = QtGui.qApp.db
        table = db.table('vHospitalBed')
        tableEx = table
        tableProfile = db.table('rbHospitalBedProfile')
        tableEx = tableEx.leftJoin(tableProfile, tableProfile['id'].eq(table['profile_id']))

        cond = table['id'].inlist(idList)
        stmt = db.selectStmt(tableEx,
                             fields='vHospitalBed.*, rbHospitalBedProfile.name as profileName',
                             where=cond)
        query = db.query(stmt)

        reportData = {}
        while query.next():
            record    = query.record()
            orgStructureId = forceInt(record.value('master_id'))
            profileName = forceString(record.value('profileName'))
            involution = forceInt(record.value('involution'))
            if involution > 0:
                busy = 3
            else:
                busy = forceInt(record.value('isBusy'))
            reportSubTable = reportData.setdefault(orgStructureId, {})
            row = reportSubTable.setdefault(profileName, [0, 0, 0, 0])
            row[busy] += 1

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(descr)
        cursor.insertBlock()

        tableColumns = [
            ('50%', [u'Профиль'], CReportBase.AlignLeft),
            ('10%', [u'Всего'], CReportBase.AlignRight),
            ('10%', [u'Свободно'], CReportBase.AlignRight),
            ('10%', [u'Резерв'], CReportBase.AlignRight),
            ('10%', [u'Занято'], CReportBase.AlignRight),
            ('10%', [u'Свернуто'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        self.genOrgStructureReport(table, reportData, len(tableColumns))
        return doc


    def genOrgStructureReport(self, table, reportData, rowSize):
        model = COrgStructureModel(None, QtGui.qApp.currentOrgId())
        item = model.getRootItem()
        total = self.genOrgStructureReportForItem(table, reportData, item, rowSize)
        self.genTotalEx(table, u'ИТОГО', rowSize, total)


    def dataPresent(self, reportData, item):
        reportSubTable = reportData.get(item.id(), None)
        return bool(reportSubTable)


    def dataPresentInChildren(self, reportData, item):
        for subitem in item.items():
            if self.dataPresent(reportData, subitem) or self.dataPresentInChildren(reportData, subitem):
                return True
        return False


    def genTitle(self, table, item, rowSize):
        i = table.addRow()
        table.mergeCells(i,0, 1, rowSize)
        table.setText(i, 0, item.name(), CReportBase.TableHeader)


    def genTotalEx(self, table, title, rowSize, total):
        i = table.addRow()
        table.setText(i, 0, title)
        table.setText(i, 1, sum(total))
        for j, v in enumerate(total):
            table.setText(i, j+2, v)


    def genTotal(self, table, item, rowSize, total):
        self.genTotalEx(table, u'Итого по ' + item.name(), rowSize, total)


    def genTable(self, table, reportData, item, rowSize):
        self.genTitle(table, item, rowSize)
        total = [0, 0, 0, 0]
        reportSubTable = reportData.get(item.id(), None)
        if reportSubTable:
            profiles = reportSubTable.keys()
            profiles.sort()
            for profile in profiles:
                i = table.addRow()
                row = reportSubTable[profile]
                table.setText(i, 0, profile)
                table.setText(i, 1, sum(row))
                for j, v in enumerate(row):
                    table.setText(i, j+2, v)
                    total[j] += v
        return total


    def genOrgStructureReportForItem(self, table, reportData, item, rowSize):
        total = [0, 0, 0, 0]
        if item.childCount() == 0:
            if self.dataPresent(reportData, item):
                total = self.genTable(table, reportData, item, rowSize)
                self.genTotal(table, item, rowSize, total)
        else:
            if self.dataPresent(reportData, item):
                tolal = self.genTable(table, reportData, item, rowSize)
                if self.dataPresentInChildren(reportData, item):
                    for subitem in item.items():
                        subtotal = self.genOrgStructureReportForItem(table, reportData, subitem, rowSize)
                        total = [x+y for x, y in zip(total,subtotal)]
                self.genTotal(table, item, rowSize, total)
            elif self.dataPresentInChildren(reportData, item):
                self.genTitle(table, item, rowSize)
                for subitem in item.items():
                    subtotal = self.genOrgStructureReportForItem(table, reportData, subitem, rowSize)
                    total = [x+y for x, y in zip(total,subtotal)]
                self.genTotal(table, item, rowSize, total)
        return total


class CFeedReportDialog(QtGui.QDialog, Ui_FeedReportDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.edtBegDate.setDate(QtCore.QDate.currentDate())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.cmbIsFinal.setCurrentIndex(params.get('isFinal', 1))
        feedDate = params.get('feedDate', QtCore.QDate.currentDate())
        if params.get('isFinal', 1) == 0 and feedDate == QtCore.QDate.currentDate():
            feedDate = feedDate.addDays(1)
        self.edtBegDate.setDate(feedDate)
        self.edtNameReg.setText(params.get('nameReg', u''))
        self.edtNameNurse.setText(params.get('nameNurse', u''))
        self.edtNameDoctor.setText(params.get('nameDoctor', u''))

    def params(self):
        result = {}
        result['feedDate'] = self.edtBegDate.date()
        result['isFinal'] = self.cmbIsFinal.currentIndex()
        result['nameReg'] = self.edtNameReg.text()
        result['nameNurse'] = self.edtNameNurse.text()
        result['nameDoctor'] = self.edtNameDoctor.text()
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbIsFinal_currentIndexChanged(self, index):
        isFinal = index == 1
        if not isFinal and self.edtBegDate.date() == QtCore.QDate.currentDate():
            self.edtBegDate.setDate(QtCore.QDate.currentDate().addDays(1))
        self.edtNameReg.setEnabled(isFinal)
        self.edtNameNurse.setEnabled(isFinal)
        self.edtNameDoctor.setEnabled(isFinal)


class CFeedReport(CReport):
    def __init__(self, parent, model, modelExcludeList=None, modelAdd=None, forReanimation=False):
        if modelExcludeList is None:
            modelExcludeList = []
        CReport.__init__(self, parent)
        self.getOrganisationName()
        self.orgStructureId = None
        self.model = model
        self.modelAdd = modelAdd
        self.modelExcludeList = modelExcludeList
        self.items = []
        self.itemsAdd = []
        self.itemsExclude = []
        self.clientIdFeedList = []
        self.parent = parent      
        self.orgStructureGroups = {}
        self.forReanimation = forReanimation

    def getSetupDialog(self, parent):
        result = CFeedReportDialog(parent)
        result.setTitle(self.title())
        self.feedReportDialog = result
        return result

    def dumpParams(self, cursor, params):
        description = self.getDescription(params)
        columns = [ ('50%', [], CReportBase.AlignLeft), ('50%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 1, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def getDescription(self, params):
        rows = []
        rows.insert(0, self.getOrgStructureName() )
        rows.insert(1, u'Общее количество больных ' + forceString(len(self.clientIdFeedList)) + u' чел.')
        rows.insert(3, u'')
        rows.append(u'Отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
        return rows

    def selectMealData(self, params, orgStructureId):
        isFinal = params.get('isFinal', False)
        feedDate = params.get('feedDate', QtCore.QDate.currentDate())
        presenceDateTime = QtCore.QDateTime(feedDate if isFinal else feedDate.addDays(-1), QtCore.QTime(7 if isFinal else 10, 0))
        excludedClientIdSet = set([forceRef(item['clientId']) for item in self.itemsExclude])

        stmt = u'''
        SELECT
            rbMealTime.name AS mealTime,
            rbMeal.name AS mealName,
            rbMeal.amount,
            rbMeal.unit,
            rbDiet.name AS dietName,
            rbCourtingDiet.name AS courtingDietName,
            rbCourtingDiet.noCourtingAtReanimation AS noCourtingAtReanimation,
            Client.id AS clientId,
            CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
            Event.externalId,
            Action.begDate AS reanimDate,
            Action.endDate AS reanimEndDate
        FROM
            Event
            INNER JOIN Client ON Event.client_id = Client.id
            INNER JOIN Event_Feed ON Event_Feed.event_id = Event.id
            LEFT JOIN Action ON Action.event_id = Event.id AND Action.actionType_id = (SELECT id FROM ActionType at WHERE at.flatCode = 'reanimation' LIMIT 0,1)
            LEFT JOIN Event_Feed_Meal ON Event_Feed_Meal.master_id = Event_Feed.id
            LEFT JOIN rbMeal ON Event_Feed_Meal.meal_id = rbMeal.id
            LEFT JOIN rbMealTime ON Event_Feed_Meal.mealTime_id = rbMealTime.id
            LEFT JOIN rbDiet ON Event_Feed.diet_id = rbDiet.id
            LEFT JOIN rbDiet AS rbCourtingDiet ON Event_Feed.courtingDiet_id = rbCourtingDiet.id
        WHERE
            %s
        GROUP BY
            clientId
        ORDER BY
            mealTime, mealName
        '''
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableEF = db.table('Event_Feed')

        cond = [
            tableEF['date'].dateEq(feedDate),
            tableEF['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableEvent['id'].inlist(self.orgStructureGroups[orgStructureId]),
            tableClient['deleted'].eq(0)
        ]
        if presenceDateTime:
            cond.append(db.joinOr([tableEvent['setDate'].isNull(), tableEvent['setDate'].le(presenceDateTime)]))
            cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].ge(presenceDateTime)]))

        query = db.query(stmt % db.joinAnd(cond))
        self.setQueryText(forceString(query.lastQuery()))
        mealData = {}
        while query.next():
            record = query.record()
            if not record.value('courtingDietName').isNull() and \
                    not self.forReanimation:
                if not forceBool(record.value('noCourtingAtReanimation')):
                    mealCourtingDietData = mealData.setdefault(forceString(record.value('courtingDietName')), {})
                    mealCourtingDietData.setdefault('courtingClients', set()).add(
                        (forceString(record.value('externalId')), forceString(record.value('clientName'))))
                elif record.value('reanimDate').isNull() or forceDateTime(record.value('reanimDate')) > forceDateTime(presenceDateTime):
                    mealCourtingDietData = mealData.setdefault(forceString(record.value('courtingDietName')), {})
                    mealCourtingDietData.setdefault('courtingClients', set()).add((forceString(record.value('externalId')), forceString(record.value('clientName'))))
                elif not record.value('reanimEndDate').isNull() and forceDateTime(record.value('reanimEndDate')) < forceDateTime(presenceDateTime):
                    mealCourtingDietData = mealData.setdefault(forceString(record.value('courtingDietName')), {})
                    mealCourtingDietData.setdefault('courtingClients', set()).add((forceString(record.value('externalId')), forceString(record.value('clientName'))))
            if forceRef(record.value('clientId')) not in excludedClientIdSet:
                mealDietData = mealData.setdefault(forceString(record.value('dietName')) if not record.value('dietName').isNull() else None, {})
                mealDietData.setdefault('clients', set()).add((forceString(record.value('externalId')), forceString(record.value('clientName'))))
                if not record.value('mealTime').isNull():
                    mealTimeData = mealDietData.setdefault(forceString(record.value('mealTime')), {})
                    mealNameData = mealTimeData.setdefault(forceString(record.value('mealName')), {})
                    mealNameData.setdefault('amount', 0)
                    mealNameData['amount'] += forceInt(record.value('amount'))
                    mealNameData['unit'] = forceString(record.value('unit'))
        return mealData

    def build(self, params):
        db = QtGui.qApp.db
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        isFinal = params.get('isFinal', False)
        feedDate = params.get('feedDate', QtCore.QDate.currentDate())
        presenceDateTime = QtCore.QDateTime(feedDate if isFinal else feedDate.addDays(-1), QtCore.QTime(7 if isFinal else 10, 0))

        if not self.forReanimation:
            self.model.loadData(self.parent.getFilter(directives={
                'presenceDay': max(0, presenceDateTime.date().daysTo(QtCore.QDate.currentDate()))
            }))
        else:
            self.model.loadData(self.parent.getFilter(directives={
                'begDateTime': presenceDateTime,
                'endDateTime': presenceDateTime,
                'begDate': presenceDateTime.date(),
                'endDate': presenceDateTime.date()
            }))

        if self.modelAdd is not None:
            self.modelAdd.loadData(self.parent.getFilter(directives={
                'begDateTime': presenceDateTime,
                'begDate': presenceDateTime.date()
            }))
        for modelExclude in self.modelExcludeList:
            modelExclude.loadData(self.parent.getFilter(directives={
                'orgStructureIndex': self.parent.treeOrgStructure.rootIndex(),
                'begDateTime': presenceDateTime,
                'endDateTime': presenceDateTime,
                'begDate': presenceDateTime.date(),
                'endDate': presenceDateTime.date()
            }))
        self.items = self.model.items[:]
        self.itemsAdd = self.modelAdd.items[:] if self.modelAdd is not None else []
        self.itemsExclude = []
        for modelExclude in self.modelExcludeList:
            self.itemsExclude += modelExclude.items[:]

        eventIdSet = set([forceRef(item['eventId']) for item in self.items])
        for item in self.itemsAdd:
            if forceRef(item['eventId']) not in eventIdSet: # and item['endDate'] >= feedDate:
                self.items.append(item)

        for item in self.items:
            self.orgStructureGroups.setdefault(forceRef(item['idOS']), []).append(forceRef(item['eventId']))

        orgStructures = {}
        for orgStructureId in self.orgStructureGroups:
            mealData = self.selectMealData(params, orgStructureId)
            if len(mealData) > 0:
                orgStructures[orgStructureId] = mealData

        for index, orgStructureId in enumerate(sorted(orgStructures.keys())):
            mealData = orgStructures[orgStructureId]
            if len(mealData) > 0:
                cursor.setCharFormat(CReportBase.ReportSubTitle)
                bf = QtGui.QTextBlockFormat()
                bf.setAlignment(QtCore.Qt.AlignRight)
                cursor.setBlockFormat(bf)
                cursor.insertText(u'Форма № 1-84')
                cursor.insertBlock()

                cursor.setCharFormat(CReportBase.ReportSubTitle)
                bf = QtGui.QTextBlockFormat()
                bf.setAlignment(QtCore.Qt.AlignCenter)
                cursor.setBlockFormat(bf)
                cursor.insertText(forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'fullName')))
                cursor.insertBlock()
                cursor.insertText(u'ПОРЦИОННИК на ' + QtCore.QTime(7 if isFinal else 10, 0).toString(u'HH:mm часов'))
                cursor.insertBlock()
                cursor.insertText(u'на питание больных "' + forceString(feedDate.day()) + u'" ' + monthNameGC[feedDate.month()] + u' ' + forceString(feedDate.year()) + u'г.')
                cursor.insertBlock()
                cursor.insertBlock()

                dietNames = sorted([diet for diet in mealData.keys() if diet is not None])
                if len(dietNames) > 0:
                    tableColumns = []
                    widthInPercents = str(min(30, max(1, 80 / len(dietNames)))) + '%'
                    tableColumns.append((u'15%', [u'Наименование отделения', u''], CReportBase.AlignLeft))
                    tableColumns.append((u'5%', [u'Количество больных', u''], CReportBase.AlignLeft))
                    for dietName in dietNames:
                        tableColumns.append((widthInPercents, [u'', forceString(dietName)], CReportBase.AlignLeft))
                    tableColumns[2][1][0] = u'Столы лечебного питания'  # oh god!..

                    table = createTable(cursor, tableColumns)
                    table.mergeCells(0, 0, 2, 1)
                    table.mergeCells(0, 1, 2, 1)
                    table.mergeCells(0, 2, 1, len(dietNames))
                    iTableRow = table.addRow()
                    clientsTotal = 0

                    for i, dietName in enumerate(dietNames):
                        clientCount = len(set([clientInfo[1] for clientInfo in mealData[dietName].get('clients', set()) | mealData[dietName].get('courtingClients', set())]))
                        clientsTotal += clientCount
                        table.setText(iTableRow, i + 2, clientCount)
                    table.setText(iTableRow, 0, forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId,'name')))
                    table.setText(iTableRow, 1, clientsTotal)

                cursor.movePosition(QtGui.QTextCursor.End)
                cursor.insertBlock()
                cursor.insertBlock()
                cursor.insertBlock()
                tableClientsColumns = [
                    ('10%',  [u'№ и/б'], CReportBase.AlignLeft),
                    ('30%',  [u'Ф.И.О. больного'], CReportBase.AlignLeft),
                ]
                tableMealColumns = [
                    ('10%',  [u'Время'], CReportBase.AlignLeft),
                    ('30%',  [u'Питание'], CReportBase.AlignLeft),
                    ('10%',  [u'Количество'], CReportBase.AlignLeft)
                ]
                # dietNames = sorted([diet for diet in mealData.keys() if diet is not None])
                if None in mealData:
                    dietNames.append(None)
                for dietName in dietNames:
                    dietNameData = mealData[dietName]
                    mealTimes = [mealTime for mealTime in sorted(dietNameData) if mealTime not in ['clients', 'courtingClients']]

                    if len(dietNameData.get('clients', set())) > 0:
                        cursor.setCharFormat(CReportBase.ReportTitle)
                        cursor.insertText((u'Пациенты с «' + dietName + u'»') if dietName is not None else u'Прочие пациенты')
                        cursor.setCharFormat(CReportBase.ReportBody)

                        tableClients = createTable(cursor, tableClientsColumns)
                        for externalId, clientName in sorted(dietNameData['clients']):
                            i = tableClients.addRow()
                            tableClients.setText(i, 0, externalId)
                            tableClients.setText(i, 1, clientName)
                        cursor.movePosition(QtGui.QTextCursor.End)
                        cursor.insertBlock()
                        cursor.insertBlock()

                    if len(mealTimes) > 0:
                        tableMeal = createTable(cursor, tableMealColumns)
                        for mealTime in mealTimes:
                            mealTimeData = dietNameData[mealTime]
                            mealTimeItems = 0
                            for mealName in sorted(mealTimeData):
                                mealTimeItems += 1
                                i = tableMeal.addRow()
                                tableMeal.setText(i, 1, mealName)
                                tableMeal.setText(i, 2, forceString(mealTimeData[mealName]['amount']) + u' ' + mealTimeData[mealName]['unit'])
                            tableMeal.mergeCells(i - mealTimeItems + 1, 0, mealTimeItems, 1)
                            tableMeal.setText(i, 0, mealTime)
                        cursor.movePosition(QtGui.QTextCursor.End)
                        cursor.insertBlock()
                        cursor.insertBlock()

                cursor.movePosition(QtGui.QTextCursor.End)
                bf = QtGui.QTextBlockFormat()
                bf.setAlignment(QtCore.Qt.AlignRight)
                cursor.setBlockFormat(bf)
                cursor.insertText(u'Отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
                if not isFinal:
                    footerColumns = [(percent, [], CReportBase.AlignLeft) for percent in ['15%', '25%', '10%']]
                    table = createTable(cursor, footerColumns, border=0, cellPadding=2, cellSpacing=0)
                    signatures = [
                        (u'Зав. отделением', 'orgStructureHead'),
                        (u'Ст. мед.сестра отделения', 'orgStructureHeadNurse'),
                        (u'Мед.сестра диетическая отделения', 'orgStructureFeedNurse')
                    ]
                    for postName, flatCode in signatures:
                        i = table.addRow()
                        table.setText(i, 0, postName)
                        i = table.addRow()
                        if orgStructureId is not None:
                            personInfo = db.getRecordList('Person', cols='*', where='orgStructure_id = ' + forceString(orgStructureId) + ' AND post_id IN (SELECT id FROM rbPost where flatCode = "' + flatCode + '")')
                            if len(personInfo) == 1:
                                table.setText(i, 0, u' '.join([
                                    forceString(personInfo[0].value('lastName')),
                                    forceString(personInfo[0].value('firstName')),
                                    forceString(personInfo[0].value('patrName'))
                                ]))
                        table.setText(i, 2, u'(подпись)')
                        i = table.addRow()
                    cursor.movePosition(QtGui.QTextCursor.End)
                cursor.insertBlock()
                cursor.insertBlock()
                cursor.insertBlock()
                if index != len(orgStructures) - 1:
                    endofpage = QtGui.QTextBlockFormat()
                    endofpage.setPageBreakPolicy(QtGui.QTextFormat.PageBreak_AlwaysAfter)
                    cursor.insertBlock(endofpage)
                    cursor.insertBlock(endofpage)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        footerColumns = [(percent, [], CReportBase.AlignLeft) for percent in ['15%', '25%', '10%']]
        table = createTable(cursor, footerColumns, border=0, cellPadding=2, cellSpacing=0)
        if isFinal:
            signatures = {
                u'Регистратор': 'nameReg',
                u'Дежурный врач': 'nameDoctor',
                u'Дежурная медсестра': 'nameNurse',
            }
            for postName in signatures:
                i = table.addRow()
                table.setText(i, 0, postName)
                i = table.addRow()
                table.setText(i, 0, params.get(signatures[postName], u''))
                table.setText(i, 2, u'(подпись)')
                table.addRow()

        return doc


    def getOrgStructureId(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem._id if treeItem else None


    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []


    def getOrganisationName(self):
        currentOrgId = QtGui.qApp.currentOrgId()
        db = QtGui.qApp.db
        table = db.table('Organisation')
        record = db.getRecordEx(table, table['shortName'], [table['id'].eq(currentOrgId), table['deleted'].eq(0)])
        self.setTitle(forceString(record.value('shortName')))


    def getOrgStructureName(self, orgStructureId):
        if orgStructureId:
            db = QtGui.qApp.db
            table = db.table('OrgStructure')
            record = db.getRecordEx(table, table['name'], [table['id'].eq(orgStructureId), table['deleted'].eq(0)])
            return forceString(forceString(record.value('name')))
        return u'ЛПУ'
