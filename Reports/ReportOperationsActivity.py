# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceBool, forceRef, forceString, forceInt
from library.vm_collections import OrderedDict
from Orgs.Utils             import getOrgStructureDescendants, getOrgStructureName
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportOperationsActivity import Ui_ReportOperationsActivity


columns = OrderedDict()
columns['ExternalId']       = u'№ истории \n болезни'
columns['ClientId']         = u'№ Амб. карты'
columns['FullName']         = u'ФИО'
columns['DaysBefore']       = u'Кол-во дней до'
columns['DaysAfter']        = u'Кол-во дней после'
columns['ExecPerson']       = u'Лечащий врач'
columns['ExecDate']         = u'Дата выписки'
columns['Result']           = u'Результат'

def selectData(params):
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    orgStructureIds = (params.get('chkOrgStructure'), params.get('orgStructureId'), params.get('lstOrgStructure'))
    result = params.get('result')
    groupOrgStructure = params.get('chkGroupOrgStructure')

    db = QtGui.qApp.db
    tableEvent = db.table('Event').alias('e')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableOrgStructure = db.table('OrgStructure').alias('os')
    tableResult = db.table('rbResult').alias('r')

    join = u""
    condEvent = [
        tableEvent['execDate'].dateLe(endDate),
        tableEvent['execDate'].dateGe(begDate),
        tableEvent['deleted'].eq(0)]
    condAction = [
        tableAction['deleted'].eq(0),
        tableActionType['deleted'].eq(0),
        tableAction['endDate'].dateLe(endDate),
        tableAction['endDate'].dateGe(begDate),
        tableAction['endDate'].isNotNull(),
        tableAction['endDate'].ne("Date('0000-00-00')")
    ]
    if orgStructureIds[0] and orgStructureIds[2]:
        condEvent.append(tableOrgStructure['id'].inlist(orgStructureIds[2]))
    elif orgStructureIds[1]:
        condEvent.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureIds[1])))
    if result:
        condEvent.append(tableResult['id'].eq(result))
    if groupOrgStructure:
        order = u"Order by os.id, e.execDate"
    else:
        order = u"Order by e.execDate"
    stmt = u"""
        Select e.id as eventId,
            e.externalId as externalId,
            c.id as clientId,
            Concat_WS(' ', c.lastName, c.firstName, c.patrName) as fullName,
            TO_DAYS((Select Action.endDate
                From Action
                    inner join ActionType
                        on ActionType.id = Action.actionType_id
                where ActionType.serviceType = 4
                    and Action.event_id = e.id
                    and not isNull(Action.endDate)
                    and Action.endDate != Date('0000-00-00')
                    and Action.deleted = 0
                Order by Action.endDate, Action.begDate
                Limit 0,1)) - TO_DAYS(e.setDate) as daysBefore,
            TO_DAYS(e.execDate) - TO_DAYS((Select Action.endDate
                From Action
                    inner join ActionType
                        on ActionType.id = Action.actionType_id
                where ActionType.serviceType = 4
                    and Action.event_id = e.id
                    and not isNull(Action.endDate)
                    and Action.endDate != Date('0000-00-00')
                    and Action.deleted = 0
                Order by Action.endDate DESC, Action.begDate DESC
                Limit 0,1)) as daysAfter,
            (Select OrgStructure.hasDayStationary
             From Action
                inner join ActionProperty
                    on ActionProperty.action_id = Action.id
                inner join ActionProperty_OrgStructure
                    on ActionProperty_OrgStructure.id = ActionProperty.id
                inner join ActionType
                    on ActionType.id = Action.actionType_id
                inner join OrgStructure
                    on OrgStructure.id = ActionProperty_OrgStructure.value
                where ActionType.flatcode = 'received'
                    and Action.event_id = e.id
                    and Action.deleted = 0
                Limit 0,1
            ) as recievedOrgHasDayStationary,
            (Select OrgStructure.hasDayStationary
             From Action
                inner join ActionProperty
                    on ActionProperty.action_id = Action.id
                inner join ActionProperty_OrgStructure
                    on ActionProperty_OrgStructure.id = ActionProperty.id
                inner join ActionType
                    on ActionType.id = Action.actionType_id
                inner join OrgStructure
                    on OrgStructure.id = ActionProperty_OrgStructure.value
                where ActionType.flatcode = 'moving'
                    and Action.event_id = e.id
                    and not isNull(Action.endDate)
                    and Action.endDate != Date('0000-00-00')
                    and Action.deleted = 0
             Order by Action.endDate desc, Action.begDate desc
             Limit 0,1
            ) as lastMovingOrgHasDayStationary,
            p.name as execPerson,
            e.execDate as execDate,
            os.id as orgStructureID,
            os.code as orgStructureCode,
            r.name as result
        From Event e
            inner join Client c
                on c.id = e.client_id
            left join rbResult r
                on r.id = e.result_id
            left join vrbPerson p
                on p.id = e.execPerson_id
            left join OrgStructure as os
		        on os.id = p.orgStructure_id
        Where e.id in (
            Select Event.id
            From Event
                inner join Action
                    on Action.event_id = Event.id
                inner join ActionType
                    on ActionType.id = Action.actionType_id
            Where ActionType.flatCode = 'leaved'
                and %(condAction)s
            )
        and e.id in (
            Select Event.id
            From Event
                inner join Action
                    on Action.event_id = Event.id
                inner join ActionType
                    on ActionType.id = Action.actionType_id
            Where ActionType.serviceType = 4
                and %(condAction)s
            )
        and %(condEvent)s
        %(order)s""" %{u'condAction': db.joinAnd(condAction),
                       u'condEvent': db.joinAnd(condEvent),
                       u'order': order}
    return db.query(stmt)

class CReportOperationsActivity(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Операционная активность')


    def getSetupDialog(self, parent):
        result = CReportOperationsActivityDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        outputColumns = params.get('outputColumns')
        groupOrgStructure = params.get('chkGroupOrgStructure')
        clientDetail = params.get('clientDetail')
        totalCountBefore = 0
        totalSumBefore = 0
        totalCountAfter = 0
        totalSumAfter = 0
        row = 0
        rowNumber = 0
        orgStructureId = 0
        curOrgStructureId = 0
        orgStructureRow = 0
        countBefore = 0
        sumBefore = 0
        countAfter = 0
        sumAfter = 0
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        if groupOrgStructure:
            cursor.insertText(u'Группировка: по отделениям')
        if clientDetail:
            cursor.insertText(u'\nДетализация по пациентам')
            cursor.insertBlock()
            tableColumns = [('2%', [u'№'], CReportBase.AlignLeft)]
            queryFeild = []
            for key in outputColumns.keys():
                if outputColumns[key]:
                    tableColumns.append(('10%', [columns[key]], CReportBase.AlignLeft))
                    queryFeild.append(key)
            colDaysAfter = -1
            colDaysBefore = -1
            colOrgStructure = -1
            widthOrgStructure = 0
            for index, feild in enumerate(queryFeild):
                if feild == 'DaysAfter':
                    colDaysAfter = index
                elif feild == 'DaysBefore':
                    colDaysBefore = index
                if feild == 'ExternalId' or feild == 'ClientId' or feild == 'FullName':
                    widthOrgStructure += 1
                    if colOrgStructure == -1:
                        colOrgStructure = 1

            table = createTable(cursor, tableColumns)
            if len(queryFeild):
                while query.next():
                    record = query.record()
                    row = table.addRow()
                    if groupOrgStructure:
                        curOrgStructureId = forceRef(record.value('orgStructureId'))
                    if orgStructureId != curOrgStructureId:
                        if orgStructureRow:
                            if colDaysAfter != -1:
                                table.setText(orgStructureRow, colDaysAfter + 1, u'%.2f' %(float(sumAfter)/float(countAfter)))
                            if colDaysBefore != -1:
                                table.setText(orgStructureRow, colDaysBefore + 1, u'%.2f' %(float(sumBefore)/float(countBefore)))
                            sumAfter = 0
                            countAfter = 0
                            sumBefore = 0
                            countBefore = 0
                        orgStructureRow = row
                        if colOrgStructure != -1:
                            table.setText(row, 1, getOrgStructureName(curOrgStructureId))
                            table.mergeCells(row, 1, 1, widthOrgStructure)
                        row = table.addRow()
                        orgStructureId = curOrgStructureId
                    rowNumber += 1
                    for index, feild in enumerate(queryFeild):
                        if feild == 'DaysAfter':
                            days = forceInt(record.value('daysAfter'))
                            if forceInt(record.value('lastMovingOrgHasDayStationary')) in (0, 1):
                                days += forceInt(record.value('lastMovingOrgHasDayStationary'))
                            elif forceInt(record.value('leavedOrgHasDayStationary')) in (0, 1):
                                days += forceInt(record.value('leavedOrgHasDayStationary'))
                            table.setText(row, index + 1, forceString(days))
                            countAfter += 1
                            sumAfter += days
                            totalCountAfter += 1
                            totalSumAfter += days
                        elif feild == 'DaysBefore':
                            days = forceInt(record.value('DaysBefore'))
                            table.setText(row, index + 1, forceString(days))
                            countBefore += 1
                            sumBefore += days
                            totalCountBefore += 1
                            totalSumBefore += days
                        elif feild:
                            table.setText(row, index + 1, forceString(record.value(feild)))
                    table.setText(row, 0, forceString(rowNumber))
            if orgStructureRow:
                if colDaysAfter != -1:
                    table.setText(orgStructureRow, colDaysAfter + 1, u'%.2f' %(float(sumAfter)/float(countAfter)))
                if colDaysBefore != -1:
                    table.setText(orgStructureRow, colDaysBefore + 1, u'%.2f' %(float(sumBefore)/float(countBefore)))
                sumAfter = 0
                countAfter = 0
                sumBefore = 0
                countBefore = 0
        else:
            cursor.insertBlock()
            tableColumns = [('2%', [u'№'], CReportBase.AlignLeft),
                            ('50%', [u'Отделение'], CReportBase.AlignLeft),
                            ('20%', [u'Ср. кол-во дней до операции'], CReportBase.AlignLeft),
                            ('20%', [u'Ср. кол-во дней после операции'], CReportBase.AlignLeft)
                            ]
            if groupOrgStructure:
                table = createTable(cursor, tableColumns)
            while query.next():
                record = query.record()
                if groupOrgStructure:
                    curOrgStructureId = forceRef(record.value('orgStructureId'))
                if orgStructureId != curOrgStructureId:
                    row = table.addRow()
                    if orgStructureRow:
                        fields = (
                            orgStructureRow,
                            forceString(getOrgStructureName(orgStructureId)),
                            forceString(u'%.2f' %(float(sumBefore)/float(countBefore))),
                            forceString(u'%.2f' %(float(sumAfter)/float(countAfter))),
                        )
                        for col, val in enumerate(fields):
                            table.setText(orgStructureRow, col, val)
                        sumAfter = 0
                        countAfter = 0
                        sumBefore = 0
                        countBefore = 0
                    orgStructureRow = row
                    orgStructureId = curOrgStructureId

                days = forceInt(record.value('daysAfter'))
                if forceInt(record.value('lastMovingOrgHasDayStationary')) in (0, 1):
                    days += forceInt(record.value('lastMovingOrgHasDayStationary'))
                elif forceInt(record.value('leavedOrgHasDayStationary')) in (0, 1):
                    days += forceInt(record.value('leavedOrgHasDayStationary'))
                countAfter += 1
                sumAfter += days
                totalCountAfter += 1
                totalSumAfter += days

                days = forceInt(record.value('DaysBefore'))
                countBefore += 1
                sumBefore += days
                totalCountBefore += 1
                totalSumBefore += days
            if orgStructureRow:
                fields = (
                    orgStructureRow,
                    forceString(getOrgStructureName(orgStructureId)),
                    forceString(u'%.2f' %(float(sumBefore)/float(countBefore))),
                    forceString(u'%.2f' %(float(sumAfter)/float(countAfter))),
                )
                for col, val in enumerate(fields):
                    table.setText(orgStructureRow, col, val)

        cursor.movePosition(QtGui.QTextCursor.PreviousBlock)

        avgDaysBeforeOperation = '%.2f' % (float(totalSumBefore)/float(totalCountBefore)) if totalCountBefore > 0 else u'не доступно'
        avgDaysAfterOperation = '%.2f' % (float(totalSumAfter)/float(totalCountAfter)) if totalCountAfter > 0 else u'не доступно'
        cursor.insertText(u'Среднее количество дней до операции: %s \n' % avgDaysBeforeOperation)
        cursor.insertText(u'Среднее количество дней после операции: %s' % avgDaysAfterOperation)

        return doc


class CReportOperationsActivityDialog(QtGui.QDialog, Ui_ReportOperationsActivity):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.lstOrgStructure.setTable('OrgStructure', filter="OrgStructure.type = '1'")
        self.lstOrgStructure.setVisible(False)
        self.cmbResult.setTable('rbResult')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbResult.setCurrentIndex(params.get('result', 0) if params.get('result', 0) != None else 0)
        arg = params.get('outputColumns', False)
        if type(arg) == QtCore.QVariant:
            arg = arg.toPyObject()
        if set(columns.keys()) == set(arg.keys()):
            for key in columns.keys():
                try:
                    self.callObjectAtributeMethod('chk%s' % key, 'setChecked', forceBool(arg[key.lower()]) if arg else True)
                except KeyError:
                    self.callObjectAtributeMethod('chk%s' % key, 'setChecked', forceBool(arg[key]) if arg else True)

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['result'] = self.cmbResult.value()
        params['outputColumns'] = OrderedDict()
        for key in columns.keys():
            params['outputColumns'][key] = self.callObjectAtributeMethod('chk%s' % key, 'isChecked')
        params['lstOrgStructure'] = self.lstOrgStructure.nameValues()
        params['chkOrgStructure'] = self.chkOrgStructureMulti.isChecked()
        params['cmbOrgStructure'] = params['chkOrgStructure']
        params['chkGroupOrgStructure'] = self.chkGroupOrgStructure.isChecked()
        params['clientDetail'] = self.chkClientDetail.isChecked()
        return params

    def callObjectAtributeMethod(self, objectName, nameMethod, *args):
        return self.__getattribute__(objectName).__getattribute__(nameMethod)(*args)

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructureMulti_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)