# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDouble, forceString, getVal
from Orgs.Utils         import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    begTime = params.get('begTime', QtCore.QTime())
    endDate = params.get('endDate', QtCore.QDate())
    endTime = params.get('endTime', QtCore.QTime())
    begDateTime = QtCore.QDateTime(begDate, begTime)
    endDateTime = QtCore.QDateTime(endDate, endTime)
    personId = params.get('personId', None)
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = params.get('orgStructureId', None)
    contractIdList = params.get('contractIdList', None)
    financeId = params.get('financeId', None)
    visitPayStatus = params.get('visitPayStatus', 0)
    visitPayStatus -= 1

    stmt = '''
SELECT
    Account.number as number,
    CONCAT_WS(" ", p.lastName, p.firstName, p.patrName) as accountCreator,
    Action.endDate as date,
    Client.lastName as lastName,
    Client.firstName as firstName,
    Client.patrName as patrName,
    Person.lastName as pLastName,
    Person.firstName as pFirstName,
    Person.patrName as pPatrName,.
    rbService.name as serviceName,
    Account_Item.price as price,
    Account_Item.amount as amount,
    Account_Item.sum as item_sum
FROM
    Account_Item
    LEFT JOIN Account ON Account.id=Account_Item.master_id
    INNER JOIN Action ON Action.id = Account_Item.action_id
    INNER JOIN Event ON Event.id = Action.event_id
    INNER JOIN Client ON Client.id = Event.client_id
    INNER JOIN Person p ON Account.createPerson_id = p.id
    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT JOIN rbService ON rbService.id = ActionType.nomenclativeService_id
    LEFT JOIN Person       ON Person.id = Action.person_id
    INNER JOIN Contract ON Account.contract_id = Contract.id
WHERE
    Action.deleted = 0
    AND p.deleted = 0
    AND Event.deleted = 0
    AND Client.deleted = 0
    AND Account_Item.deleted = 0
    AND Account.deleted = 0
    AND Account_Item.action_id IS NOT NULL
    AND %s
ORDER BY
    date,
    number
'''

    db = QtGui.qApp.db
    # tableAction = db.table('Action')
    tablePerson = db.table('Person')
    tableAccount = db.table('Account')

    cond = []
    cond.append(tableAccount['createDatetime'].datetimeBetween(begDateTime, endDateTime))
    #addDateInRange(cond, tableAccount['createDatetime'], begDateTime, endDateTime)
    if eventTypeId:
        tableEvent = db.table('Event')
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if contractIdList:
        cond.append(tableAccount['contract_id'].inlist(contractIdList))
    if financeId:
        tableContract = db.table('Contract')
        cond.append(tableContract['finance_id'].eq(financeId))
    if visitPayStatus >= 0:
        cond.append(u'getPayCode(Contract.finance_id, Action.payStatus) = %d'%(visitPayStatus))
    if personId:
        cond.append(tablePerson['id'].eq(personId))

    return db.query(stmt % (db.joinAnd(cond)))


class CReportContractsRegistry(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Реестр договоров')


    def getSetupDialog(self, parent):
        result = CReportContractsRegistrySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):

        rowSize = 10
        query = selectData(params)

        reportData = {}

        flag_all_sum = 0    #флаг, регистрирующий то, надо ли выводить строку Итог

        all_item_sum = 0
        all_amount = 0
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            number = forceString(record.value('number'))
            date = forceString(record.value('date')).split(' ')[0]
            accountCreator = forceString(record.value('accountCreator'))
            lastName = forceString(record.value('lastName'))
            firstName = forceString(record.value('firstName'))
            patrName = forceString(record.value('patrName'))
            pLastName = forceString(record.value('pLastName'))
            pFirstName = forceString(record.value('pFirstName'))
            pPatrName = forceString(record.value('pPatrName'))
            serviceName = forceString(record.value('serviceName'))
            price = forceDouble(record.value('price'))
            amount = forceDouble(record.value('amount'))
            item_sum = forceDouble(record.value('item_sum'))
            clientName = u' '.join([lastName, firstName, patrName])
            personName = u' '.join([pLastName, pFirstName, pPatrName])

            if not date in reportData.keys():
                reportData[date] = {}
            dateDict = reportData[date]
            if not number in dateDict.keys():
                dateDict[number] = {'resume':0.0}
            contractDict = dateDict[number]
            if not clientName in contractDict.keys():
                contractDict[clientName] = []
            clientRecord = contractDict[clientName]
            clientRecord.append([personName, serviceName, price, amount,  item_sum, accountCreator])
            contractDict['resume'] += item_sum

            all_item_sum += item_sum
            all_amount += amount

            if item_sum != 0 :
                flag_all_sum = 1


        # now text
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()


        tableColumns = [
                        ('10%', [u'Договор', u'Номер'], CReportBase.AlignLeft),
                        ('5%',  [u'', u'Дата'], CReportBase.AlignLeft),
                        ('15%', [u'Автор создания счёта', u''], CReportBase.AlignLeft),
                        ('15%', [u'ФИО пациента', u''], CReportBase.AlignLeft),
                        ('15%', [u'ФИО исполнителя', u''], CReportBase.AlignLeft),
                        ('20%', [u'Наименование услуги', u''], CReportBase.AlignLeft),
                        ('5%',  [u'Цена услуги', u''], CReportBase.AlignRight),
                        ('5%',  [u'Количество', u''], CReportBase.AlignRight),
                        ('5%',  [u'Стоимость', u''], CReportBase.AlignRight),
                        ('5%',  [u'Общая стоимость услуг по договору, руб.', u''], CReportBase.AlignRight)
                        ]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 2, 1)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)

        dateKeys = reportData.keys()
        dateKeys.sort()
        for date in dateKeys:
            numberKeys = reportData[date].keys()
            numberKeys.sort()
            for number in numberKeys:
                contractDict = reportData[date][number]
                contractSum = contractDict.pop('resume', 0.0)
                for client in contractDict.keys():
                    for [personName, serviceName, price, amount, item_sum, accountCreator] in contractDict[client]:
                        i = table.addRow()
                        table.setText(i, 0, number)
                        table.setText(i, 1, date)
                        table.setText(i, 2, accountCreator)
                        table.setText(i, 3, client)
                        table.setText(i, 4, personName)
                        table.setText(i, 5, serviceName)
                        table.setText(i, 6, price)
                        table.setText(i, 7, amount)
                        table.setText(i, 8, item_sum)
                table.setText(i, 9, contractSum)

        if flag_all_sum != 0 :
            i = table.addRow()

            format = QtGui.QTextCharFormat()
            format.setFontWeight(QtGui.QFont.Bold)
            table.mergeCells(i, 0, i, 7)
            table.mergeCells(i, 7, i, 1)
            table.mergeCells(i, 8, i, 1)
            table.setText(i, 0, u'Итого', format, CReportBase.AlignLeft)
            table.setText(i, 7, forceString(all_amount), format, CReportBase.AlignLeft)
            table.setText(i, 9, forceString(all_item_sum), format, CReportBase.AlignLeft)

        return doc


from Ui_ReportContractsRegistry import Ui_ReportContractsRegistrySetupDialog


class CReportContractsRegistrySetupDialog(QtGui.QDialog, Ui_ReportContractsRegistrySetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance', True)
        self.cmbEventType.setTable('EventType', True)

        #self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbVisitPayStatus.setCurrentIndex(0)

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(getVal(params, 'begTime', QtCore.QTime.currentTime()))
        self.edtEndTime.setTime(getVal(params, 'endTme', QtCore.QTime.currentTime()))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbContract.setPath(params.get('contractPath', u''))
        self.cmbVisitPayStatus.setCurrentIndex(params.get('visitPayStatus', 0))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['begTime'] = self.edtBegTime.time()
        result['endTime'] = self.edtEndTime.time()
        result['personId'] = self.cmbPerson.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['contractIdList'] = self.cmbContract.getIdList()
        result['contractPath'] = self.cmbContract.getPath()
        result['financeId'] = self.cmbFinance.value()
        result['financeCode'] = self.cmbFinance.code()
        result['visitPayStatus'] = self.cmbVisitPayStatus.currentIndex()
        return result
