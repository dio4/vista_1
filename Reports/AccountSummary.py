# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDate, forceDouble, forceRef, forceString


def selectData(accountItemIdList, orgInsurerId = None):
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    stmt="""
SELECT
    formatClientPolicyInsurer(ClientPolicy.id) AS insurerName,
    ClientPolicy.insurer_id AS insurer_id,
    IF(rbService.name IS NULL, EventType.name, rbService.name) AS service,
    IF(rbService.name IS NULL, '',             rbService.code) AS serviceCode,
    SUM(Account_Item.`amount`) AS `amount`,
    SUM(Account_Item.`uet`)    AS `uet`,
    Account_Item.`price`       AS `price`,
    SUM(Account_Item.`sum`)    AS `sum`
FROM
    Account_Item
    LEFT JOIN Event         ON  Event.id  = Account_Item.event_id
    LEFT JOIN EventType     ON  EventType.id = Event.eventType_id
    LEFT JOIN Visit         ON  Visit.id  = Account_Item.visit_id
    LEFT JOIN Action        ON  Action.id  = Account_Item.action_id
    LEFT JOIN ActionType    ON  ActionType.id = Action.actionType_id
    LEFT JOIN Client        ON  Client.id = Event.client_id
    LEFT JOIN ClientPolicy  ON ClientPolicy.client_id = Client.id AND
              ClientPolicy.id = (SELECT MAX(CP.id)
                                 FROM   ClientPolicy AS CP
                                 WHERE  CP.client_id = Client.id)
    LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
    LEFT JOIN rbService ON rbService.id =
        IF(Account_Item.service_id IS NOT NULL,
           Account_Item.service_id,
           IF(Account_Item.visit_id IS NOT NULL, Visit.service_id, EventType.service_id)
          )
WHERE
    %s """ % (tableAccountItem['id'].inlist(accountItemIdList))
    if orgInsurerId:
        tableOrganisation = db.table('Organisation').alias('Insurer')
        stmt += """ AND %s """ % (tableOrganisation['id'].eq(orgInsurerId))
    stmt += """
 GROUP BY
    insurerName, ClientPolicy.insurer_id, service, serviceCode, price
 ORDER BY
    insurerName, ClientPolicy.insurer_id, service, serviceCode, price
    """
    query = db.query(stmt)
    return query


class CAccountSummary(CReportBase):
    def __init__(self, parent):
        CReportBase.__init__(self, parent)
        self.setTitle(u'Сводный счёт')


    def build(self, description, params):
        accountId = params.get('accountId', None)
        accountItemIdList = params.get('accountItemIdList', None)
        orgInsurerId = params.get('orgInsurerId', None)
        if orgInsurerId:
            self.setTitle(u'Счёт на СМО')
            query = selectData(accountItemIdList, orgInsurerId)
        else:
            query = selectData(accountItemIdList)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        number, date, payer, recipient = self.getContract(accountId)
        if orgInsurerId:
            payer = u''
            db = QtGui.qApp.db
            tableOrganisation = db.table('Organisation')
            record = db.getRecordEx(tableOrganisation,
                                [tableOrganisation['fullName'].name(), tableOrganisation['INN'].name()
                                ],
                                tableOrganisation['id'].eq(orgInsurerId)
                               )
            if record:
                fullName = forceString(record.value('fullName'))
                INN = forceString(record.value('INN'))
                payer = fullName + u', ИНН:' + INN

        table = createTable (cursor, [ ('30%', [], CReportBase.AlignLeft), ('70%', [], CReportBase.AlignLeft) ], headerRowCount=4, border=0, cellPadding=2, cellSpacing=0)
        table.setText(0, 0, u'по договору №')
        table.setText(0, 1, number)
        table.setText(1, 0, u'от')
        table.setText(1, 1, forceString(date))
        table.setText(2, 0, u'получатель')
        table.setText(2, 1, recipient)
        table.setText(3, 0, u'плательщик')
        table.setText(3, 1, payer)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(description)
        cursor.insertBlock()

        tableColumns = [
                          ('5%',   [ u'№' ],                 CReportBase.AlignRight ),
                          ('30%',  [ u'Профиль\n(Услуга)' ], CReportBase.AlignLeft ),
                          ('20%',  [ u'Тариф'             ], CReportBase.AlignRight ),
                          ('20%',  [ u'Количество'        ], CReportBase.AlignRight ),
                          ('20%',  [ u'УЕТ'               ], CReportBase.AlignRight ),
                          ('20%',  [ u'Сумма'             ], CReportBase.AlignRight ),
                       ]
        table = createTable(cursor, tableColumns)
        n = 0

        prevInsurerName = False
        prevInsurerId = False

        totalUet = 0
        grandTotalUet = 0

        total = 0
        grandTotal = 0
        
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()

            insurerName = forceString(record.value('insurerName'))
            insurerId = forceRef(record.value('insurer_id'))
            service = forceString(record.value('service'))
            serviceCode = forceString(record.value('serviceCode'))
            if serviceCode:
                service += '\n('+serviceCode+')'

            amount = forceDouble(record.value('amount'))
            uet    = forceDouble(record.value('uet'))
            price  = forceDouble(record.value('price'))
            sum    = forceDouble(record.value('sum'))

            if prevInsurerName != insurerName or prevInsurerId != insurerId:
                if n:
                    self.produceTotalLine(table, u'Всего по '+prevInsurerName, totalUet, total)

                if not orgInsurerId:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 5)
                    table.setText(i, 0, insurerName, CReportBase.ReportSubTitle, CReportBase.AlignLeft)
                prevInsurerName = insurerName
                prevInsurerId = insurerId
                n = 0
                totalUet = 0
                total = 0

            n += 1
            i = table.addRow()
            table.setText(i, 0, n)
            table.setText(i, 1, service)
            table.setText(i, 2, price)
            table.setText(i, 3, amount)
            table.setText(i, 4, uet)
            table.setText(i, 5, sum)
            totalUet += uet
            grandTotalUet += uet
            total += sum
            grandTotal += sum
        if n and (not orgInsurerId):
            self.produceTotalLine(table, u'Всего по '+insurerName, totalUet, total)
        self.produceTotalLine(table, u'Итого по счёту', grandTotalUet, grandTotal)
        return doc


    def produceTotalLine(self, table, title, totalUet, total):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 4)
        table.setText(i, 0, title, CReportBase.TableTotal, CReportBase.AlignLeft)
        table.setText(i, 4, totalUet, CReportBase.TableTotal)
        table.setText(i, 5, total, CReportBase.TableTotal)


    def getContract(self, accountId):
        db = QtGui.qApp.db
        tableAccount = db.table('Account')
        tableContract = db.table('Contract')
        tableOrganisation = db.table('Organisation')
        tablePayer = tableOrganisation.alias('Payer')
        tableRecipient = tableOrganisation.alias('Recipient')
        queryTable = tableContract.leftJoin(tableAccount, tableContract['id'].eq(tableAccount['contract_id']))
        queryTable = queryTable.leftJoin(tablePayer, tableContract['payer_id'].eq(tablePayer['id']))
        queryTable = queryTable.leftJoin(tableRecipient, tableContract['recipient_id'].eq(tableRecipient['id']))
        record = db.getRecordEx(
            queryTable,
            [
                tableContract['number'].name(), tableContract['date'].name(),
                tablePayer['fullName'].alias('payer'), tableRecipient['fullName'].alias('recipient')
            ],
            [
                tableAccount['id'].eq(accountId),
                tableAccount['deleted'].eq(0)
            ]
        )
        if record:
            return (forceString(record.value('number')), forceDate(record.value('date')),
                    forceString(record.value('payer')),  forceString(record.value('recipient')))
        else:
            return ('', '', '', '')
