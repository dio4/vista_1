# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action import CAction
from Events.Utils import getEventType
from Orgs.Utils import getPersonInfo
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_DailyJournalBeforeRecordSetup import Ui_DailyJournalBeforeRecordSetup
from library.Utils import forceBool, forceInt, forceRef, forceString, forceTime, getVal, forceDate


class CDailyJournalBeforeRecordSetup(QtGui.QDialog, Ui_DailyJournalBeforeRecordSetup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbAccountingSystem.setTable('rbAccountingSystem')
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())

    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDateDailyJournal', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))
        self.cmbAccountingSystem.setValue(getVal(params, 'accountingSystemId', None))
        self.cmbOrderSorting.setCurrentIndex(getVal(params, 'orderSorting', 0))
        self.cmbIsPrimary.setCurrentIndex(getVal(params, 'isPrimary', 0))
        self.chkFreeTimes.setChecked(forceBool(getVal(params, 'isFreeTimes', 0)))
        self.chkPegeFormat.setChecked(forceBool(getVal(params, 'isPegeFormat', 0)))
        self.chkNoTimeLinePerson.setChecked(forceBool(getVal(params, 'isNoTimeLinePerson', 0)))
        self.chkViewBirthDate.setChecked(forceBool(getVal(params, 'isViewBirthDate', 0)))
        self.chkViewRegAdress.setChecked(forceBool(getVal(params, 'isViewRegAdress', 0)))

    def params(self):
        result = {}
        result['begDateDailyJournal'] = self.edtBegDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['accountingSystemId'] = self.cmbAccountingSystem.value()
        result['orderSorting'] = self.cmbOrderSorting.currentIndex()
        result['isPrimary'] = self.cmbIsPrimary.currentIndex()
        result['isFreeTimes'] = self.chkFreeTimes.isChecked()
        result['isPegeFormat'] = self.chkPegeFormat.isChecked()
        result['isNoTimeLinePerson'] = self.chkNoTimeLinePerson.isChecked()
        result['isViewBirthDate'] = self.chkViewBirthDate.isChecked()
        result['isViewRegAdress'] = self.chkViewRegAdress.isChecked()
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbIsPrimary_currentIndexChanged(self, index):
        if not self.cmbIsPrimary.currentIndex():
            self.chkFreeTimes.setEnabled(True)
        else:
            self.chkFreeTimes.setChecked(False)
            self.chkFreeTimes.setEnabled(False)


class CDailyJournalBeforeRecord(CReport):
    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Суточный журнал предварительной записи')
        self.dailyJournalBeforeRecordSetup = None

    def getSetupDialog(self, parent):
        result = CDailyJournalBeforeRecordSetup(parent)
        self.dailyJournalBeforeRecordSetup = result
        return result

    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []

    def build(self, params):
        begDate = getVal(params, 'begDateDailyJournal', QtCore.QDate())
        personId = getVal(params, 'personId', None)

        orgStructureIndex = self.dailyJournalBeforeRecordSetup.cmbOrgStructure._model.index(
            self.dailyJournalBeforeRecordSetup.cmbOrgStructure.currentIndex(),
            0,
            self.dailyJournalBeforeRecordSetup.cmbOrgStructure.rootModelIndex()
        )
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)

        if not personId and orgStructureIdList:
            db = QtGui.qApp.db
            table = db.table('Person')
            cond = [
                table['orgStructure_id'].inlist(orgStructureIdList),
                table['deleted'].eq(0)
            ]
            if begDate:
                cond.append(db.joinOr([
                    table['retireDate'].isNull(),
                    db.joinAnd([table['retireDate'].monthGe(begDate), table['retireDate'].yearGe(begDate)])
                ]))
            personIdList = db.getIdList(table, where=cond, order='lastName, firstName, patrName')
        else:
            personIdList = [personId]

        doc = QtGui.QTextDocument()
        if begDate and personIdList:
            isPegeFormat = forceBool(getVal(params, 'isPegeFormat', 0))
            isNoTimeLinePerson = forceBool(getVal(params, 'isNoTimeLinePerson', 0))
            isFreeTimes = forceBool(getVal(params, 'isFreeTimes', 0))

            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            for personId in personIdList:
                if personId:
                    queueBool = False
                    timeRange, office, times, queue = self.getTimeRangeOffice(begDate, personId)
                    if not isFreeTimes:
                        for queueId in queue:
                            if queueId:
                                queueBool = True
                                break
                    if (isNoTimeLinePerson) or (
                                not isNoTimeLinePerson and (
                                (isFreeTimes and times) or (not isFreeTimes and queueBool))):
                        if isPegeFormat:
                            page = QtGui.QTextBlockFormat()
                            page.setPageBreakPolicy(QtGui.QTextFormat.PageBreak_AlwaysAfter)
                            cursor.setBlockFormat(page)
                        cursor = self.createTableForPerson(cursor, personId, timeRange, office, times, queue, params)
                        cursor.insertBlock()
                        cursor.insertBlock()
                        cursor.insertBlock()
                        cursor.insertBlock()
                        cursor.movePosition(QtGui.QTextCursor.End)
        return doc

    def createTableForPerson(self, cursor, personId, timeRange, office, times, queue, params):
        begDate = getVal(params, 'begDateDailyJournal', QtCore.QDate())
        orderSorting = getVal(params, 'orderSorting', None)
        isPrimary = getVal(params, 'isPrimary', None)
        accountingSystem = getVal(params, 'accountingSystemId', None)
        isFreeTimes = forceBool(getVal(params, 'isFreeTimes', 0))
        isViewBirthDate = forceBool(getVal(params, 'isViewBirthDate', 0))
        isViewRegAdress = forceBool(getVal(params, 'isViewRegAdress', 0))

        isPrimaryList = [u'Нет', u'Да']
        orderSortingList = [
            u'clientIdentifier' if accountingSystem else u'Client.id',
            u'ActionProperty_Time.value',
            u'Client.lastName, Client.firstName, Client.patrName'
        ]

        db = QtGui.qApp.db
        tableAction = db.table('Action')
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        personInfo = getPersonInfo(personId)

        orgStructureId = forceInt(db.translate('Person', 'id', personId, 'orgStructure_id'))
        if times:
            lenQueue = len(queue) if queue else 0
            diff = len(times) - lenQueue
            if diff < 0:
                times.extend([None] * (-diff))
            elif diff > 0:
                queue.extend([None] * diff)
        orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name'))

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        columns = [
            ('25%', [], CReportBase.AlignLeft),
            ('50%', [], CReportBase.AlignLeft),
            ('25%', [], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, columns, headerRowCount=1, border=0, cellPadding=2, cellSpacing=0)

        table.setText(0, 0, forceString(begDate), charFormat=boldChars)
        table.setText(0, 1, forceString(begDate.longMonthName(begDate.month())), charFormat=boldChars)
        table.setText(0, 2, forceString(begDate.longDayName(begDate.dayOfWeek())), charFormat=boldChars)
        row = table.addRow()
        table.setText(row, 0, u'')
        table.setText(row, 1, u'Карточка предварительной записи больных', charFormat=boldChars)
        table.setText(row, 2, u'')
        row = table.addRow()
        table.setText(row, 0, u'к врачу:')
        table.setText(row, 1, u'%s(%s)' % (orgStructureName, personInfo['specialityName']))
        table.setText(row, 2, u'кабинет %s' % (office))
        row = table.addRow()
        table.setText(row, 0, u'')
        table.setText(row, 1, personInfo['fullName'])
        table.setText(row, 2, u'')
        row = table.addRow()
        table.setText(row, 0, u'часы приема:')
        table.setText(row, 1, timeRange)
        table.setText(row, 2, u'')
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        cursor.insertText(u'\nпервичные: %s\n' % (forceString(isPrimaryList[isPrimary])))
        cursor.insertText(u'идентификатор: %s\n' % (forceString(
            db.translate('rbAccountingSystem', 'id', accountingSystem, 'name')
        ) if accountingSystem else u'идентификатор пациента в лечебном учреждении'))
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [
            ('3%', [u'№'], CReportBase.AlignRight),
            ('2%', [u'П'], CReportBase.AlignLeft),
            ('15%', [u'Идентификатор'], CReportBase.AlignLeft),
            ('5%', [u'Время'], CReportBase.AlignLeft),
            ('20%', [u'ФИО'], CReportBase.AlignLeft),
            ('5%', [u'Дата рождения' if isViewBirthDate else u'Возраст'], CReportBase.AlignLeft),
            ('25%', [u'Адрес регистрации' if isViewRegAdress else u'Прикрепление'], CReportBase.AlignLeft),
            ('25%', [u'Примечание'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, cols)
        cnt = 1
        clientIdList = []
        actionIdList = []
        colsStmt = u''
        if accountingSystem:
            colsStmt = u''', 
            (   
                SELECT ClientIdentification.identifier
                FROM ClientIdentification
                WHERE ClientIdentification.client_id = Client.id 
                    AND ClientIdentification.accountingSystem_id = %d 
                    AND ClientIdentification.deleted = 0
                ORDER BY ClientIdentification.id DESC
                LIMIT 1
            ) AS clientIdentifier
            ''' % (accountingSystem)

        stmt = u'''
        SELECT
            QueueEvent.client_id AS clientId,
            DATE(QueueEvent.setDate) AS date,
            ActionProperty_Time.value AS time,
            ActionProperty_Action.index AS indexAPA,
            QueueAction.person_id AS personId,
            QueueAction.note AS note,
            Action.note AS noteAction,
            QueueAction.id AS queueActionId,
            ActionProperty.action_id AS ambActionId,
            Client.lastName, Client.firstName, Client.patrName,
            Client.birthDate AS birthDate,
            age(Client.birthDate, %s) AS clientAge,
            getClientLocAddress(Client.id) AS locAddress,
            (
                SELECT CONCAT(rbAttachType.name COLLATE utf8_general_ci, ', прикреплен с: ', ClientAttach.begDate)
                FROM ClientAttach INNER JOIN rbAttachType ON ClientAttach.attachType_id = rbAttachType.id
                WHERE ClientAttach.client_id = Client.id AND ClientAttach.deleted = 0 AND ClientAttach.endDate IS NULL
                ORDER BY ClientAttach.id DESC
                LIMIT 1
            ) AS clientAttachInfo %s
        FROM Action AS QueueAction
            LEFT JOIN ActionType AS QueueActionType ON QueueActionType.id = QueueAction.actionType_id
            LEFT JOIN Event AS QueueEvent ON QueueEvent.id = QueueAction.event_id
            INNER JOIN Client ON Client.id = QueueEvent.client_id
            LEFT JOIN EventType AS QueueEventType ON QueueEventType.id = QueueEvent.eventType_id
            LEFT JOIN ActionProperty_Action ON ActionProperty_Action.value = QueueAction.id
            LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
            LEFT JOIN Action ON Action.id = ActionProperty.action_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN ActionPropertyType AS APTTime ON APTTime.actionType_id = ActionType.id AND APTTime.name='times'
            LEFT JOIN ActionProperty AS APTime ON APTime.type_id = APTTime.id AND APTime.action_id = Action.id
            LEFT JOIN ActionProperty_Time ON ActionProperty_Time.id = APTime.id AND ActionProperty_Time.index = ActionProperty_Action.index
            LEFT JOIN Event ON Event.id = Action.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
        WHERE QueueAction.deleted = 0
            AND QueueActionType.code = 'queue'
            AND QueueEvent.deleted = 0
            AND QueueEventType.code = 'queue'
            AND Action.deleted = 0
            AND ActionType.code = 'amb'
            AND Event.deleted = 0
            AND EventType.code = '0'
            AND QueueAction.person_id = %d
            AND DATE(QueueEvent.setDate) = DATE(%s)
        ORDER BY %s
        ''' % (
            tableAction['begDate'].formatValue(begDate),
            colsStmt,
            personId,
            tableAction['begDate'].formatValue(begDate),
            orderSortingList[orderSorting]
        )

        query = QtGui.qApp.db.query(stmt)
        recordInfo = {}
        while query.next():
            record = query.record()
            if record:
                clientId = forceRef(record.value('clientId'))
                if clientId and (clientId not in clientIdList):
                    stmt = u'''
                    SELECT
                        QueueAction.person_id AS personId,
                        QueueAction.id AS queueActionId
                    FROM Action AS QueueAction
                        LEFT JOIN ActionType AS QueueActionType ON QueueActionType.id = QueueAction.actionType_id
                        LEFT JOIN Event AS QueueEvent ON QueueEvent.id = QueueAction.event_id
                        LEFT JOIN EventType AS QueueEventType ON QueueEventType.id = QueueEvent.eventType_id
                        LEFT JOIN ActionProperty_Action ON ActionProperty_Action.value = QueueAction.id
                        LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
                        LEFT JOIN Action ON Action.id = ActionProperty.action_id
                        LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
                        LEFT JOIN ActionPropertyType AS APTTime ON APTTime.actionType_id = ActionType.id AND APTTime.name='times'
                        LEFT JOIN ActionProperty AS APTime ON APTime.type_id = APTTime.id AND APTime.action_id = Action.id
                        LEFT JOIN ActionProperty_Time ON ActionProperty_Time.id = APTime.id AND ActionProperty_Time.index = ActionProperty_Action.index
                        LEFT JOIN Event ON Event.id = Action.event_id
                        LEFT JOIN EventType ON EventType.id = Event.eventType_id
                    WHERE QueueAction.deleted = 0
                        AND QueueActionType.code = 'queue'
                        AND QueueEvent.deleted = 0
                        AND QueueEventType.code = 'queue'
                        AND Action.deleted = 0
                        AND ActionType.code = 'amb'
                        AND Event.deleted = 0
                        AND EventType.code = '0'
                        AND DATE(QueueEvent.setDate) = DATE(%s)
                        AND QueueEvent.client_id = %d
                    ORDER BY ActionProperty_Time.value
                    LIMIT 1
                    ''' % (tableAction['begDate'].formatValue(begDate), clientId)
                    queryIsPrimary = QtGui.qApp.db.query(stmt)
                    while queryIsPrimary.next():
                        recordClient = queryIsPrimary.record()
                        queueActionId = forceRef(recordClient.value('queueActionId'))
                        personClientId = forceRef(recordClient.value('personId'))
                        if personClientId and (personClientId == personId) and (clientId not in clientIdList):
                            clientIdList.append(clientId)
                            actionIdList.append(queueActionId)
                if not isFreeTimes:
                    actionId = forceRef(record.value('queueActionId'))
                    if isPrimary and (actionId in actionIdList):
                        cnt = self.printDailyJournal(
                            cnt,
                            table,
                            record, u'П', accountingSystem,
                            clientId,
                            isViewBirthDate,
                            isViewRegAdress
                        )
                    elif not isPrimary:
                        cnt = self.printDailyJournal(
                            cnt,
                            table,
                            record, u'П' if actionId in actionIdList else u'', accountingSystem,
                            clientId,
                            isViewBirthDate,
                            isViewRegAdress
                        )
                else:
                    indexAPA = forceInt(record.value('indexAPA'))
                    if not recordInfo.get(indexAPA, None):
                        recordInfo[indexAPA] = record
        if isFreeTimes:
            for i, time in enumerate(times):
                if recordInfo.get(i, None):
                    recordFreeTime = recordInfo[i]
                    cnt = self.printDailyJournal(
                        cnt,
                        table,
                        recordFreeTime,
                        u'П' if forceRef(recordFreeTime.value('queueActionId')) in actionIdList else u'',
                        accountingSystem,
                        forceRef(recordFreeTime.value('clientId')),
                        isViewBirthDate,
                        isViewRegAdress
                    )
                else:
                    row = table.addRow()
                    table.setText(row, 0, cnt)
                    table.setText(row, 1, u'')
                    table.setText(row, 2, u'')
                    table.setText(row, 3, time.toString('hh:mm') if time else u'--:--')
                    table.setText(row, 4, u'')
                    table.setText(row, 5, u'')
                    table.setText(row, 6, u'')
                    table.setText(row, 7, u'')
                    cnt += 1
        cursor.movePosition(QtGui.QTextCursor.End)
        return cursor

    def printDailyJournal(
            self, cnt, table, record, primaryInfo, accountingSystem, clientId, isViewBirthDate, isViewRegAdress
    ):
        row = table.addRow()
        table.setText(row, 0, cnt)
        table.setText(row, 1, primaryInfo)
        table.setText(row, 2,
                      forceString(record.value('clientIdentifier')) if accountingSystem else forceString(clientId))
        time = forceTime(record.value('time'))
        table.setText(row, 3, time.toString('hh:mm') if time else u'--:--')
        table.setText(row, 4, forceString(record.value('lastName')) + u' ' + forceString(
            record.value('firstName')) + u' ' + forceString(record.value('patrName')))

        if isViewBirthDate:
            table.setText(row, 5, forceDate(record.value('birthDate')).toString('yyyy-MM-dd'))
        else:
            table.setText(row, 5, forceString(record.value('clientAge')))

        table.setText(row, 6, forceString(record.value('locAddress' if isViewRegAdress else 'clientAttachInfo')))
        table.setText(row, 7, forceString(record.value('note')))
        cnt += 1
        return cnt

    def getTimeRangeOffice(self, date, personId):
        atcAmbulance = 'amb'
        etcTimeTable = '0'
        timeRange = ('--:--', '--:--')
        office = u''
        times = []
        queue = []
        db = QtGui.qApp.db
        eventTypeId = getEventType(etcTimeTable).eventTypeId
        eventTable = db.table('Event')
        cond = [
            eventTable['deleted'].eq(0),
            eventTable['eventType_id'].eq(eventTypeId),
            eventTable['execDate'].eq(date),
            eventTable['execPerson_id'].eq(personId)
        ]
        event = db.getRecordEx(eventTable, '*', cond)
        if event:
            eventId = forceRef(event.value('id'))
            action = CAction.getAction(eventId, atcAmbulance)
            begTime = action['begTime']
            endTime = action['endTime']
            office = action['office']
            times = action['times']
            queue = action['queue']
            if begTime and endTime:
                timeRange = begTime.toString('H:mm') + ' - ' + endTime.toString('H:mm')
        return timeRange, office, times, queue


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'kvd2',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CDailyJournalBeforeRecord(None)
    w.exec_()


if __name__ == '__main__':
    main()
