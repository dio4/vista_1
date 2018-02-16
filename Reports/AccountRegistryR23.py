# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Orgs.Utils import getOrganisationInfo, getOrganisationMainStaff
from Reports.Report import CReportOrientation
from Reports.ReportBase import createAutographField, createTable, insertRequisitesBlock
from Ui_AccountRegistryR23SetupDialog import Ui_AccountRegistryR23Setup
from library.AmountToWords import amountToWords
from library.Utils import forceDate, forceDouble, forceInt, forceString


def selectDataStat(idList):
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')

    # KD = amount IF KUSL[0:1] IN ('K', 'S') OR 1 if KUSL[0:1] == 'K'
    # amount = amount if amount else if KUSL[0:1] == 'K' 1
    # KOLU = amount
    # sum_b = price * baseExpensePercent/100 * KOLU
    # sum_d = price * additionalExpensePercent/100 * kolu
    # sum_k = sum_b * regulator
    # sum_dm = price * additionalExpenseMPercent/100. * kolu
    # sum_uc = price * paymentExpensePercent/100. * kolu * regulator
    stmt = u"""SELECT
              if(rbItemService.infis LIKE 'S%%', if(BedDays.fact > mes.MES.maxDuration, mes.MES.maxDuration,
                  BedDays.fact), Account_Item.amount) AS amount,

              Account_Item.price   AS price,

              Account_Item.`sum`     AS `sum`,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.infis,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                ) AS service,
              BaseExpense.percent AS baseExpensePercent,
              AdditionalExpense.percent AS additionalExpensePercent,
              AdditionalExpenseM.percent AS additionalExpenseMPercent,
              PaymentExpense.percent AS paymentExpensePercent,
              Contract.regionalTariffRegulationFactor AS regulator
            FROM Account_Item
                LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
                LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
                LEFT JOIN Event  ON Event.id  = Account_Item.event_id
                LEFT JOIN (
                    SELECT Event.id as id,
                      IF(rbMedicalAidType.code = '7', timestampdiff(DAY, Event.setDate, Event.execDate) + 1 - ((WEEK(Event.execDate,1)-WEEK(Event.setDate,1))*2),
                          if(rbMedicalAidType.code = '10', timestampdiff(DAY, Event.setDate, Event.execDate) + 1, timestampdiff(DAY, Event.setDate, Event.execDate))) as fact
                      FROM Event
                      LEFT JOIN EventType ON EventType.id = Event.eventType_id
                      LEFT JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id
                ) AS BedDays ON BedDays.id = Event.id
                LEFT JOIN mes.MES ON Event.MES_id = mes.MES.id
                LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
                LEFT JOIN EventType ON EventType.id = Event.eventType_id
                LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
                LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
                LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
                LEFT JOIN Contract_CompositionExpense AS BaseExpense ON  BaseExpense.id = (
                    SELECT MAX(CCE.id)
                    FROM Contract_CompositionExpense AS CCE
                    LEFT JOIN rbExpenseServiceItem ON CCE.rbTable_id =rbExpenseServiceItem.id
                    WHERE rbExpenseServiceItem.code = '1'  AND CCE.master_id = Contract_Tariff.id
                )
                LEFT JOIN Contract_CompositionExpense AS AdditionalExpense ON  AdditionalExpense.id = (
                    SELECT MAX(CCE2.id)
                    FROM Contract_CompositionExpense AS CCE2
                    LEFT JOIN rbExpenseServiceItem ON CCE2.rbTable_id =rbExpenseServiceItem.id
                    WHERE rbExpenseServiceItem.code = '2'  AND CCE2.master_id = Contract_Tariff.id
                )
                LEFT JOIN Contract_CompositionExpense AS AdditionalExpenseM ON  AdditionalExpenseM.id = (
                    SELECT MAX(CCE3.id)
                    FROM Contract_CompositionExpense AS CCE3
                    LEFT JOIN rbExpenseServiceItem ON CCE3.rbTable_id =rbExpenseServiceItem.id
                    WHERE rbExpenseServiceItem.code = '3'  AND CCE3.master_id = Contract_Tariff.id
                )
                LEFT JOIN Contract_CompositionExpense AS PaymentExpense ON  PaymentExpense.id = (
                    SELECT MAX(CCE4.id)
                    FROM Contract_CompositionExpense AS CCE4
                    LEFT JOIN rbExpenseServiceItem ON CCE4.rbTable_id =rbExpenseServiceItem.id
                    WHERE rbExpenseServiceItem.code = '4'  AND CCE4.master_id = Contract_Tariff.id
                )
                LEFT JOIN Account ON Account_Item.master_id = Account.id AND Account.deleted = 0
                LEFT JOIN Contract ON Account.contract_id = Contract.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
                AND Account_Item.deleted = 0
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
                #если период(period) = пребыванию(fact), выводить только стандарт, отбрасывать койко-день (koika)
                #если пребывание меньше периода, то выводится только койко-день, отбраковываем стандарт (standart)
                #если пребывание больше периода, то выводить оба (0)
            AND(
                (rbItemService.infis LIKE 'S%%' and (BedDays.fact BETWEEN mes.MES.minDuration AND mes.MES.maxDuration))
             or
                (rbItemService.infis LIKE 'K%%' and (BedDays.fact < mes.MES.minDuration))
             or
                (rbItemService.infis not LIKE 'K%%' AND rbItemService.infis NOT LIKE 'S%%')
             or
                (rbItemService.infis LIKE 'K%%' OR  rbItemService.infis LIKE 'S%%') and (BedDays.fact > mes.MES.maxDuration)
            )
        """ % tableAccountItem['id'].inlist(idList) #ORDER BY client_id, , service

    amount = 0
    sum = 0.0
    summ_b = 0.0
    summ_dm = 0.0
    summ_uc = 0.0
    summ_d = 0.0
    summ_k = 0.0

    query = db.query(stmt)
    while query.next():
        record = query.record()
        amount_int = forceInt(record.value('amount'))
        price = forceDouble(record.value('price'))
        service = forceString(record.value('service'))
        baseExpensePercent = forceDouble(record.value('baseExpensePercent'))
        additionalExpensePercent = forceDouble(record.value('additionalExpensePercent'))
        additionalExpenseMPercent = forceDouble(record.value('additionalExpenseMPercent'))
        paymentExpensePercent = forceDouble(record.value('paymentExpensePercent'))
        regulator = forceDouble(record.value('regulator'))
        if amount_int == 0 and service[0:1] == 'K':
            amount_int = 1
        if service[0:1] in ('K', 'S'):
            amount += amount_int
        if service[0] == 'S':
            amount_int = 1
        sum += forceDouble(record.value('sum'))
        summ_b += price * baseExpensePercent * amount_int / 100.
        summ_d += price * additionalExpensePercent * amount_int / 100.
        summ_k += price * baseExpensePercent * amount_int * regulator / 100.
        summ_dm+= price * additionalExpenseMPercent * amount_int / 100.
        summ_uc+= price * paymentExpensePercent * amount_int * regulator / 100.
    return amount, sum, summ_b, summ_dm, summ_uc, summ_d, summ_k, forceString(query.lastQuery())

def selectDataAmb(idList):
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    stmt = """SELECT
              SUM(Account_Item.amount) AS amount,
              SUM(Account_Item.sum) AS sum,
              SUM(Account_Item.price * BaseExpense.percent * Account_Item.amount / 100) AS summ_base,
              SUM(Account_Item.price * AdditionalExpenseM.percent * Account_Item.amount / 100) AS summ_dm,
              SUM(Account_Item.price * PaymentExpense.percent * Account_Item.amount * Contract.regionalTariffRegulationFactor / 100) AS summ_uc,
              SUM(Account_Item.price * AdditionalExpense.percent * Account_Item.amount / 100) AS summ_d,
              SUM(Account_Item.price * BaseExpense.percent * Account_Item.amount * Contract.regionalTariffRegulationFactor / 100) AS summ_k
            FROM Account_Item
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN Contract_Tariff ON Account_Item.tariff_id = Contract_Tariff.id
            LEFT JOIN Contract_CompositionExpense AS BaseExpense ON  BaseExpense.id = (
                SELECT MAX(CCE.id)
                FROM Contract_CompositionExpense AS CCE
                LEFT JOIN rbExpenseServiceItem ON CCE.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '1'  AND CCE.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS AdditionalExpense ON  AdditionalExpense.id = (
                SELECT MAX(CCE2.id)
                FROM Contract_CompositionExpense AS CCE2
                LEFT JOIN rbExpenseServiceItem ON CCE2.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '2'  AND CCE2.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS AdditionalExpenseM ON  AdditionalExpenseM.id = (
                SELECT MAX(CCE3.id)
                FROM Contract_CompositionExpense AS CCE3
                LEFT JOIN rbExpenseServiceItem ON CCE3.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '3'  AND CCE3.master_id = Contract_Tariff.id
            )
            LEFT JOIN Contract_CompositionExpense AS PaymentExpense ON  PaymentExpense.id = (
                SELECT MAX(CCE4.id)
                FROM Contract_CompositionExpense AS CCE4
                LEFT JOIN rbExpenseServiceItem ON CCE4.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code = '4'  AND CCE4.master_id = Contract_Tariff.id
            )
            LEFT JOIN Account ON Account_Item.master_id = Account.id AND Account.deleted = 0
            LEFT JOIN Contract ON Account.contract_id = Contract.id
            WHERE
                Account_Item.reexposeItem_id IS NULL
                AND Account_Item.deleted = 0
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
        """ % tableAccountItem['id'].inlist(idList)
    query = db.query(stmt)
    while query.next():
        record = query.record()
        amount = forceInt(record.value('amount'))
        sum = forceDouble(record.value('sum'))
        summ_b = forceDouble(record.value('summ_base'))
        summ_dm = forceDouble(record.value('summ_dm'))
        summ_uc = forceDouble(record.value('summ_uc'))
        summ_d = forceDouble(record.value('summ_d'))
        summ_k = forceDouble(record.value('summ_k'))
    return amount, sum, summ_b, summ_dm, summ_uc, summ_d, summ_k, forceString(query.lastQuery())


##Реестр счета для Краснодара
class CAccountRegistryR23(CReportOrientation):
    mapPlaces = {0: u'Поликлиника взрослая',
              1: u'Поликлиника детская',
              2: u'Стационар взрослый',
              3: u'Стационар детский',
              4: u'Дневной стационар взрослый',
              5: u'Дневной стационар детский'}

    mapUnits = {0: u'Посещения',
             1: u'Посещения',
             2: u'Услуг/человек',
             3: u'Услуг/человек',
             4: u'Посещ./дни',
             5: u'Посещ./дни'}

    def __init__(self, parent, accountRegistry = None):
        CReportOrientation.__init__(self, parent, QtGui.QPrinter.Landscape)
        self.setTitle(u'Реестр счёта')
        self.place = u'поликлиника детская'
        self.units = u'посещения'
        self.accountRegistry = accountRegistry

    def build(self, params):
        db = QtGui.qApp.db
        accountId = params.get('accountId', None)
        payerId = params.get('orgInsurerId')
        placeIndex = params.get('orgStructure')

        self.units = self.mapUnits[placeIndex]
        self.place = self.mapPlaces[placeIndex]

        accountRegistry = params.get('registryNumber')
        idList = params.get('accountItemIdList', [])
        settleDate = forceDate(db.translate('Account', 'id', accountId, 'settleDate'))


        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        format = QtGui.QTextCharFormat()

        cursor.insertBlock(CReportOrientation.AlignRight)
        format.setFontPointSize(8)
        cursor.insertText(u'Приложение N 2\nк тарифному соглашшению в сфере\nобязательного медицинского страхования\nна территории краснодарского края\nот \'__\'__________ 20__')

        cursor.insertBlock()
        insertRequisitesBlock(cursor, QtGui.qApp.currentOrgId(), payerId)
        cursor.movePosition(cursor.End)
        cursor.insertBlock(CReportOrientation.AlignCenter)
        format.setFontPointSize(12)
        cursor.insertText(u'СЧЕТ № %s от %s' % (accountRegistry, settleDate.toString(QtCore.Qt.SystemLocaleLongDate)), format)

        cursor.insertBlock(CReportOrientation.AlignCenter)
        format.setFontPointSize(8)
        currentOrgInfo = getOrganisationInfo(QtGui.qApp.currentOrgId())
        cursor.insertText(u'К реестру счетов № %s от %s за %s' % (accountRegistry, settleDate.toString(QtCore.Qt.SystemLocaleLongDate), settleDate.toString(u'yyyy г. MMMM месяц')), format)

        cursor.insertBlock()

        tableColumns = []
        tableColumns.append(('10%',  [u'Предмет счета', u'', u'', u'', str(1)], CReportOrientation.AlignLeft))
        tableColumns.append(('10%',  [u'Наименование условий оказания медицинской помощи', u'', u'', u'', str(2)], CReportOrientation.AlignLeft))
        tableColumns.append(('5%',   [u'Един. изм.', u'', u'', u'', str(3)], CReportOrientation.AlignCenter))
        tableColumns.append(('5%',   [u'Количество', u'', u'', u'', str(4)], CReportOrientation.AlignCenter))
        tableColumns.append(('10%',  [u'Сумма, руб.', u'Всего', u'', u'', str(5)], CReportOrientation.AlignCenter))
        tableColumns.append(('10%',  [u'',               u'В том числе', u'По базовой части тарифа', u'Всего', str(5)], CReportOrientation.AlignCenter))
        tableColumns.append(('15%',  [u'',               u'',            u'',                        u'В т.ч. по выполнению стандартов и повышению доступности амбулаторной медицинской помощи', str(6)], CReportOrientation.AlignCenter))
        tableColumns.append(('15%',  [u'',               u'',            u'По стимулирующим выплатам мадицинскому персоналу участковой службы', u'', str(7)], CReportOrientation.AlignCenter))
        tableColumns.append(('10%',  [u'',               u'',            u'По дополнительным расходам', u'Всего', str(8)], CReportOrientation.AlignCenter))
        tableColumns.append(('10%',  [u'',               u'',            u'',                           u'в т.ч. на коммунальные услуги', str(9)], CReportOrientation.AlignCenter))
        format.setFontPointSize(8)
        table = createTable(cursor, tableColumns, charFormat = format)

        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 4, 1)
        table.mergeCells(0, 2, 4, 1)
        table.mergeCells(0, 3, 4, 1)
        table.mergeCells(0, 4, 1, 6)
        table.mergeCells(1, 4, 3, 1)
        table.mergeCells(1, 5, 1, 5)
        table.mergeCells(2, 5, 1, 2)
        table.mergeCells(2, 7, 2, 1)
        table.mergeCells(2, 8, 1, 2)


        count = 0
        selectData = selectDataAmb if placeIndex < 2  or placeIndex > 3 else selectDataStat
        amount, sum, summ_b, summ_dm, summ_uc, summ_d, summ_k, queryText = selectData(idList)
        self.setQueryText(queryText)
        row = table.addRow()
        table.setText(row, 0, u'Медицинские услуги, оказанные в системе ОМС за период с %sг. по %sг.' % (settleDate.toString(u'01.MM.yy'), settleDate.toString(u'dd.MM.yy')))
        table.setText(row, 1, self.place)
        table.setText(row, 2, self.units)
        table.setText(row, 3, amount)
        table.setText(row, 4, '%.2f' % sum)
        table.setText(row, 5, '%.2f' % summ_b)
        table.setText(row, 6, '%.2f' % summ_dm)
        table.setText(row, 7, '%.2f' % summ_uc)
        table.setText(row, 8, '%.2f' % summ_d)
        table.setText(row, 9, '%.2f' % summ_k)

        font = QtGui.QFont()
        font.setBold(True)
        oldFont = format.font()
        format.setFont(font)
        format.setFontPointSize(8)

        row = table.addRow()
        table.mergeCells(row, 0, 1, 4)
        cell = table.cellAt(row, 3)
        cellFirst = cell.firstCursorPosition()
        b_format = cellFirst.blockFormat()
        b_format.setAlignment(QtCore.Qt.AlignRight)
        cellFirst.setBlockFormat(b_format)
        cell.lastCursorPosition().insertText(u'Итого', format)
        table.setText(row, 4, '%.2f' % sum)
        table.setText(row, 5, '%.2f' % summ_b)
        table.setText(row, 6, '%.2f' % summ_dm)
        table.setText(row, 7, '%.2f' % summ_uc)
        table.setText(row, 8, '%.2f' % summ_d)
        table.setText(row, 9, '%.2f' % summ_k)

        row = table.addRow()
        table.mergeCells(row, 0, 1, 4)
        cell = table.cellAt(row, 3)
        cellFirst = cell.firstCursorPosition()
        b_format = cellFirst.blockFormat()
        b_format.setAlignment(QtCore.Qt.AlignRight)
        cellFirst.setBlockFormat(b_format)
        cell.lastCursorPosition().insertText(u'НДС', format)
        table.setText(row, 4, '-')
        table.setText(row, 5, '-')
        table.setText(row, 6, '-')
        table.setText(row, 7, '-')
        table.setText(row, 8, '-')
        table.setText(row, 9, '-')

        row = table.addRow()
        table.mergeCells(row, 0, 1, 4)
        cell = table.cellAt(row, 3)
        cellFirst = cell.firstCursorPosition()
        b_format = cellFirst.blockFormat()
        b_format.setAlignment(QtCore.Qt.AlignRight)
        cellFirst.setBlockFormat(b_format)

        cell.lastCursorPosition().insertText(u'Всего без НДС', format)
        table.setText(row, 4, '%.2f' % sum)
        table.setText(row, 5, '%.2f' % summ_b)
        table.setText(row, 6, '%.2f' % summ_dm)
        table.setText(row, 7, '%.2f' % summ_uc)
        table.setText(row, 8, '%.2f' % summ_d)
        table.setText(row, 9, '%.2f' % summ_k)

        format.setFont(oldFont)

        cursor.movePosition(cursor.End)
        cursor.insertBlock()
        format.setFontPointSize(8)
        cursor.insertText(u'Итого: %s' % amountToWords(sum), format)

        cursor.insertBlock(CReportOrientation.AlignLeft)
        orgMainStaff = getOrganisationMainStaff(QtGui.qApp.currentOrgId())
        titles = [u'Главный врач']
        names = [orgMainStaff[0]]

        titles.append(u'Главный бухгалтер')
        names.append(orgMainStaff[1])
        colCount = 2
        sealOverTitle = 2

        cursor.movePosition(cursor.End)

        cursor.insertBlock(CReportOrientation.AlignLeft)
        createAutographField(cursor,
                             titles,
                             names,
                             sealOverTitle = sealOverTitle,
                             colCount = colCount,
                             signLabel = u'(подпись)',
                             transcriptLabel = u'(расшифровка подписи)',
                             charFormat = format)

        cursor.movePosition(cursor.End)

        cursor.insertBlock(CReportOrientation.AlignLeft)
        format.setFontPointSize(7)
        cursor.insertText(u'Примечание: Первый экземпляр - плательщику, второй экземпляр - поставщику', format)
        return doc

class CAccountRegistryR23SetupDialog(QtGui.QDialog, Ui_AccountRegistryR23Setup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(u'Параметры счёта')
        self.cmbInsurerFilterDialog.setAddNone(False)
        self.cmbInsurerFilterDialog.setCurrentIndex(0)

    def orgId(self):
            return self.cmbInsurerFilterDialog.value()

    def orgStructure(self):
        return self.cmbOrgStructure.currentIndex()

    def registryNumber(self):
        return self.edtRegistryNumber.text()



def getAccountRegistryR23Params(parent):
    ok = False
    orgId = None
    orgStructure = None
    registryNumber = None
    filterDialog = CAccountRegistryR23SetupDialog(parent)
    ok = filterDialog.exec_()
    if ok:
        orgId = filterDialog.orgId()
        orgStructure = filterDialog.orgStructure()
        registryNumber = filterDialog.registryNumber()
    return ok, orgId, orgStructure, registryNumber