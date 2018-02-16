# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportAccount import Ui_ReportAccount
from library.AmountToWords import amountToWords
from library.Utils import forceDate, forceDouble, forceInt, forceRef, forceString
from library.vm_collections import OrderedDict

nameUnit = OrderedDict()
nameUnit[u'Стационар']                                 = (5,  u'койко-день')
nameUnit[u'Поликлиника']                               = (6,  u'посещение')
nameUnit[u'Стоматология']                              = (7,  u'УЕТ')
nameUnit[u'Дневной стационар']                         = (9,  u'пациенто-день')
nameUnit[u'Стационар дневного пребывания']             = (10, u'пациенто-день')
nameUnit[u'Женская консультация']                      = (11, u'посещение')
nameUnit[u'Стационар на дому']                         = (12, u'пациенто-день')
nameUnit[u'Дневной стационар женской консультации']    = (13, u'пациенто-день')
nameUnit[u'Центр здоровья']                            = (14, u'посещение')
nameUnit[u'Приемное отделение']                        = (15, u'посещение')
nameUnit[u'Фельдшерско-акушерский пункт']              = (16, u'посещение')
nameUnit[u'Скорая медицинская помощь']                 = (17, u'вызов')
nameUnit[u'Неотложная помощь']                         = (18, u'посещение')
nameUnit[u'Стационар санаторно-курортного учреждения'] = (19, u'койко-день')
nameUnit[u'Высокотехнологичная МП']                    = (20, u'койко-день')

def getCond(params):
    db = QtGui.qApp.db

    date           = forceDate(params.get('begDate', QtCore.QDate()))
    insurerHeaderId      = forceRef(params.get('insurerId', None))
    eventProfileId = forceRef(params.get('eventProfileId', None))
    financeId      = forceRef(params.get('financeId', None))

    tableEventProfile   = db.table('rbEventProfile')
    tableContract       = db.table('Contract')
    tableAccount        = db.table('Account')
    tableOrganisation   = db.table('Organisation')

    cond = [tableAccount['settleDate'].dateEq(date), tableAccount['deleted'].eq(0)]
    if insurerHeaderId:
        if forceString(db.translate('Organisation', 'id', insurerHeaderId, 'infisCode')) == '9007':
            cond.append('left(organisation.area, 2) != \'23\'')
        else:
            cond.append(db.joinOr([tableOrganisation['head_id'].eq(insurerHeaderId), tableOrganisation['id'].eq(insurerHeaderId)]))
            cond.append('left(organisation.area, 2) = \'23\'')
    if eventProfileId:
        cond.append(tableEventProfile['id'].eq(eventProfileId))
    if financeId:
        cond.append(tableContract['finance_id'].eq(financeId))
    return cond

def selectData(params):

    db = QtGui.qApp.db

    cond  = getCond(params)

    stmt = u'''SELECT
                        IF(tbl.code IN ('11', '12'), 'Стационар',
                        IF(tbl.code IN ('21', '22'), 'Поликлиника',
                        IF(tbl.code IN ('31', '32'), 'Стомотология',
                        IF(tbl.code IN ('41', '42'), 'Дневной стационар',
                        IF(tbl.code IN ('51', '52'), 'Стационар дневного пребывания',
                        IF(tbl.code = '60', 'Женская консультация',
                        IF(tbl.code IN ('71', '72'), 'Стационар на дому',
                        IF(tbl.code = '90', 'Дневной стационар женской',
                        IF(tbl.code IN ('01', '02'), 'Центр здоровья',
                        IF(tbl.code IN ('111', '112'), 'Приемное отделение',
                        IF(tbl.code IN ('401', '402'), 'Высокотехнологичная МП', NULL))))))))))) AS name,
                        SUM(IF(tbl.service = 'K' AND tbl.amount = 0, 1, IF(tbl.service IN ('K', 'G', 'V', 'S'), tbl.amount, 0))) AS amount,
                        SUM(tbl.KOLU) AS countVisit,
                        SUM(tbl.uet) AS uet,
                        ROUND(SUM(tbl.sum), 2) AS sum,
                        ROUND(SUM(tbl.KOLU * tbl.price * tbl.baseExpense / 100), 2) AS sumB,
                        ROUND(SUM(tbl.KOLU * tbl.price * tbl.additionalExpense / 100), 2) AS sumD,
                        ROUND(SUM(tbl.KOLU * tbl.price * tbl.baseExpense / 100 * tbl.regionalTariffRegulationFactor), 2) AS sumK,
                        ROUND(SUM(tbl.KOLU * tbl.price * tbl.additionalExpenseM / 100), 2) AS sumDM,
                        ROUND(SUM(tbl.KOLU * tbl.price * tbl.paymentExpense / 100 * tbl.regionalTariffRegulationFactor), 2) AS sumUC
                FROM (SELECT
                        rbeventprofile.code,
                        @service := LEFT(IF(account_item.service_id IS NOT NULL,
                        rbItemService.infis,
                        rbEventService.infis), 1) AS service,
                        @amount := IF(rbItemService.infis LIKE 'S%%',
                        IF(bedDays.fact > mes.mes.maxDuration, mes.mes.maxDuration, bedDays.fact),
                        IF(rbItemService.infis LIKE 'K%%',
                        IF(bedDays.fact > mes.mes.maxDuration, bedDays.fact - mes.mes.maxDuration, bedDays.fact),
                        account_item.amount)) AS amount,
                        @kolu := IF(@service IN ('S', 'G'), 1, @amount) AS KOLU,
                        @price := IF(@service = 'G', account_item.sum, account_item.price) AS price,
                        account_item.sum,
                        account_item.uet,
                        BaseExpense.percent AS baseExpense,
                        AdditionalExpense.percent AS additionalExpense,
                        contract.regionalTariffRegulationFactor AS regionalTariffRegulationFactor,
                        AdditionalExpenseM.percent AS additionalExpenseM,
                        PaymentExpense.percent AS paymentExpense
                FROM account
                    INNER JOIN account_item ON account_item.master_id = account.id AND account_item.deleted = 0
                    INNER JOIN event ON event.id = account_item.event_id
                    INNER JOIN ClientPolicy ON ClientPolicy.client_id = Event.client_id AND ClientPolicy.id = getClientPolicyOnDateId(Event.client_id, 1, Event.setDate)
                    INNER JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id
                    INNER JOIN eventtype ON eventtype.id = event.eventType_id
                    INNER JOIN rbeventprofile ON rbeventprofile.id = eventProfile_id
                    INNER JOIN contract ON contract.id = account.contract_id
                    # LEFT JOIN rbfinance ON rbfinance.id = contract.finance_id
                    LEFT JOIN (SELECT event.id AS id,
                                    IF(rbmedicalaidtype.code = '7',
                                    TIMESTAMPDIFF(DAY, DATE(event.setDate), DATE(event.execDate)) + 1
                                    - ((WEEK(DATE(event.execDate), 1) - WEEK(DATE(event.setDate), 1)) * 2)
                                    - COUNT(holidays.cid),
                                    IF(rbmedicalaidtype.code = '10',
                                    TIMESTAMPDIFF(DAY, DATE(event.setDate), DATE(event.execDate)) + 1,
                                    IF(rbmedicalaidtype.code IN ('1', '2', '3') AND TIMESTAMPDIFF(DAY, DATE(event.setDate),
                                    DATE(event.execDate)) = 0, TIMESTAMPDIFF(DAY, DATE(event.setDate), DATE(event.execDate)) + 1,
                                    TIMESTAMPDIFF(DAY, DATE(event.setDate), DATE(event.execDate))))) AS fact
                                FROM event
                                    LEFT JOIN eventtype ON eventtype.id = event.eventType_id
                                    LEFT JOIN rbmedicalaidtype ON eventtype.medicalAidType_id = rbmedicalaidtype.id
                                    LEFT JOIN (SELECT `calendarexceptions`.`id` AS cid,
                                                        `calendarexceptions`.`date`
                                                FROM `calendarexceptions`) AS holidays ON DATE_FORMAT(holidays.`date`, '%%m-%%d') >= DATE_FORMAT(event.setDate, '%%m-%%d') AND DATE_FORMAT(holidays.`date`, '%%m-%%d') <= DATE_FORMAT(event.execDate, '%%m-%%d')
                                GROUP BY id) AS bedDays ON bedDays.id = event.id
                    JOIN (SELECT @service := NULL,
                                @amount := 0,
                                 @price := 0,
                                 @kolu := 0) tmp
                    LEFT JOIN rbservice AS rbEventService ON rbEventService.id = eventtype.service_id
                    LEFT JOIN rbservice AS rbItemService ON rbItemService.id = account_item.service_id
                    LEFT JOIN mes.mes ON event.MES_id = mes.mes.id
                    LEFT JOIN contract_tariff ON account_item.tariff_id = contract_tariff.id
                    LEFT JOIN contract_compositionexpense AS BaseExpense ON BaseExpense.id = (SELECT MAX(CCE.id)
                                                                                                  FROM contract_compositionexpense AS CCE
                                                                                                        LEFT JOIN rbexpenseserviceitem ON CCE.rbTable_id = rbexpenseserviceitem.id
                                                                                                  WHERE rbexpenseserviceitem.code IN ('1', '230002') AND CCE.master_id = contract_tariff.id)
                    LEFT JOIN contract_compositionexpense AS AdditionalExpense ON AdditionalExpense.id = (SELECT MAX(CCE2.id)
                                                                                                              FROM contract_compositionexpense AS CCE2
                                                                                                                    LEFT JOIN rbexpenseserviceitem ON CCE2.rbTable_id = rbexpenseserviceitem.id
                                                                                                              WHERE rbexpenseserviceitem.code IN ('2', '230003') AND CCE2.master_id = contract_tariff.id)
                    LEFT JOIN contract_compositionexpense AS AdditionalExpenseM ON AdditionalExpenseM.id = (SELECT MAX(CCE3.id)
                                                                                                            FROM contract_compositionexpense AS CCE3
                                                                                                                LEFT JOIN rbexpenseserviceitem
                                                                                                                    ON CCE3.rbTable_id = rbexpenseserviceitem.id
                                                                                                            WHERE rbexpenseserviceitem.code IN ('3', '230004') AND CCE3.master_id = contract_tariff.id)
                    LEFT JOIN contract_compositionexpense AS PaymentExpense ON PaymentExpense.id = (SELECT MAX(CCE4.id)
                                                                                                    FROM contract_compositionexpense AS CCE4
                                                                                                        LEFT JOIN rbexpenseserviceitem
                                                                                                            ON CCE4.rbTable_id = rbexpenseserviceitem.id
                                                                                                    WHERE rbexpenseserviceitem.code IN ('4', '230005') AND CCE4.master_id = contract_tariff.id)
                    WHERE %s) AS tbl
                    GROUP BY NAME
                    HAVING  NAME IS NOT NULL''' % db.joinAnd(cond)
    return db.query(stmt)

def getAccountNumbers(params):
    db = QtGui.qApp.db
    cond = getCond(params)
    stmt = u'''SELECT Account.number
               FROM Account
                INNER JOIN account_item ON account_item.master_id = account.id AND account_item.deleted = 0
                INNER JOIN event ON event.id = account_item.event_id
                INNER JOIN ClientPolicy ON ClientPolicy.client_id = Event.client_id AND ClientPolicy.id = getClientPolicyOnDateId(Event.client_id, 1, Event.setDate)
                INNER JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id
                INNER JOIN eventtype ON eventtype.id = event.eventType_id
                INNER JOIN rbeventprofile ON rbeventprofile.id = eventProfile_id
                INNER JOIN contract ON contract.id = account.contract_id
                WHERE %s
                GROUP BY Account.id''' % db.joinAnd(cond)
    query = db.query(stmt)
    numbers = []
    while query.next():
        numbers.append(forceString(query.record().value('number')))
    return numbers


class CReportAccount(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Счет на пациента')

    def getSetupDialog(self, parent):
        result = CAccount(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        db = QtGui.qApp.db
        insurerHeaderId = params.get('insurerId', 0)
        insurerId = insurerHeaderId if insurerHeaderId is not None else 0
        currentOrgId = QtGui.qApp.currentOrgId()
        numberList = getAccountNumbers(params)
        orgInfo = db.getRecordList('Organisation', 'fullName, Address', 'id IN (%s, %s)' % (currentOrgId, insurerId))
        currentOrgInfo = orgInfo.pop(1) if currentOrgId > insurerId and insurerId else orgInfo.pop(0)
        if insurerId:
            insurerInfo = orgInfo[0]
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        table = createTable(cursor, [('10%', [], CReportBase.AlignLeft), ('20%', [], CReportBase.AlignLeft), ('30%', [], CReportBase.AlignLeft), ('10%', [], CReportBase.AlignLeft), ('20%', [], CReportBase.AlignLeft)], 0, 0, 0)
        i = table.addRow()
        table.setText(i, 0, u'Поставщик: ', CReportBase.ReportSubTitle)
        table.setText(i, 1, forceString(currentOrgInfo.value('fullName')), CReportBase.ReportBody)
        table.setText(i, 3, u'Плательщик: ', CReportBase.ReportSubTitle)
        table.setText(i, 4, forceString(insurerInfo.value('fullName')) if insurerId else '', CReportBase.ReportBody)
        i = table.addRow()
        table.setText(i, 0, u'Расчетный счет: ', CReportBase.ReportSubTitle)
        # table.setText(0, 1, forceString(currentOrgInfo.value('fullName')), CReportBase.ReportBody)
        table.setText(i, 3, u'Расчетный счет: ', CReportBase.ReportSubTitle)
        # table.setText(0, 4, forceString(insurerInfo.value('fullName')) if insurerId else '', CReportBase.ReportBody)
        i = table.addRow()
        table.setText(i, 0, u'Адрес: ', CReportBase.ReportSubTitle)
        table.setText(i, 1, forceString(currentOrgInfo.value('Address')), CReportBase.ReportBody)
        table.setText(i, 3, u'Адрес: ', CReportBase.ReportSubTitle)
        table.setText(i, 4, forceString(insurerInfo.value('Address')) if insurerId else '', CReportBase.ReportBody)
        cursor.movePosition(cursor.End, 0)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.insertText(u'СЧЁТ № ______________ от %s г.' % QtCore.QDate.currentDate().toString('dd.MM.yyyy'), CReportBase.ReportTitle)
        cursor.insertBlock()
        cursor.insertText(u'к реестрам счетов № %s от %s' % (','.join(numberList),forceDate(params.get('begDate')).toString('dd.MM.yyyy')), CReportBase.ReportBody)
        cursor.insertBlock()
        cursor.insertBlock()
        tableColumns = [
                        ('%20',  [u'Предмет счета', u'',            u'',                                                 u'',                                                                     u'1'], CReportBase.AlignCenter),
                        ('%15',  [u'Наименование',  u'',            u'',                                                 u'',                                                                     u'2'], CReportBase.AlignCenter),
                        ('%10',  [u'Един.изм.',     u'',            u'',                                                 u'',                                                                     u'3'], CReportBase.AlignCenter),
                        ('%5',   [u'Количество',    u'',            u'',                                                 u'',                                                                     u'4'], CReportBase.AlignCenter),
                        ('%5',   [u'Сумма, руб.',   u'Всего',       u'',                                                 u'',                                                                     u'5'], CReportBase.AlignCenter),
                        ('%5',   [u'',              u'в том числе', u'по базовой части тарифа',                          u'всего',                                                                u'6'], CReportBase.AlignCenter),
                        ('%5',   [u'',              u'',            u'',                                                 u'в т.ч. по выполнению стандартов и повышению доступности амбулаторной', u'7'], CReportBase.AlignCenter),
                        ('%5',   [u'',              u'',            u'по стимулирующим выплатам медицинскому персоналу', u'',                                                                     u'8'], CReportBase.AlignCenter),
                        ('%5',   [u'',              u'',            u'по дополнительным расходам',                       u'всего',                                                                u'9'], CReportBase.AlignCenter),
                        ('%5',   [u'',              u'',            u'',                                                 u'в т.ч. на коммунальные услуги',                                        u'10'], CReportBase.AlignCenter)]

        table = createTable(cursor, tableColumns)
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
        for key, value in nameUnit.items():
            i = table.addRow()
            table.setText(i, 2, value[1])
            if key == u'Стоматология':
                i = table.addRow()
                table.setText(i, 2, u'посещение')
                table.mergeCells(i-1, 1, 2, 1)
            table.setText(i, 1, key)
        table.setText(i, 0, u'Медицинская помощь, оказанная застрахованным гражданам')
        table.mergeCells(i - 15, 0, 16, 1)
        total = [0] * (len(tableColumns) - 4)
        while query.next():
            record = query.record()
            name       = forceString(record.value('NAME'))
            amount     = forceInt(record.value('amount'))
            countVisit = forceInt(record.value('countVisit'))
            uet        = forceInt(record.value('uet'))
            sum        = forceDouble(record.value('sum'))
            sumB       = forceDouble(record.value('sumB'))
            sumD       = forceDouble(record.value('sumD'))
            sumK       = forceDouble(record.value('sumK'))
            sumDM      = forceDouble(record.value('sumDM'))
            sumUC      = forceDouble(record.value('sumUC'))

            curAmount = amount
            if nameUnit[name][1] == u'посещение':
                curAmount = countVisit
            elif nameUnit[name][1] == u'УЕТ':
                curAmount = uet

            # sum = sumB + sumDM + sumK
            def setTextTable():
                table.setText(row, 3, curAmount)
                table.setText(row, 4, sum)
                table.setText(row, 5, sumB)
                table.setText(row, 6, sumDM)
                table.setText(row, 7, sumUC)
                table.setText(row, 8, sumD)
                table.setText(row, 9, sumK)

            row = nameUnit[name][0]
            setTextTable()
            if name == u'Стоматология':
                row += 1
                curAmount = countVisit

            total[0] += sum
            total[1] += sumB
            total[2] += sumDM
            total[3] += sumUC
            total[4] += sumD
            total[5] += sumK

        def addTotalRows(text):
            i = table.addRow()
            table.setText(i, 0, text, CReportBase.TableTotal)
            table.mergeCells(i, 0, 1, 4)

        addTotalRows(u'Итого')
        addTotalRows(u'НДС')
        addTotalRows(u'Всего без НДС')
        for index, value in enumerate(total):
            table.setText(21, index + 4, value, CReportBase.TableTotal)
            table.setText(23, index + 4, value, CReportBase.TableTotal)
        cursor.movePosition(cursor.End, 0)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Итого: ' + amountToWords(total[0]), CReportBase.ReportSubTitle)
        cursor.insertBlock()
        table = createTable(cursor, [('50%', [], CReportBase.AlignLeft), ('50%', [], CReportBase.AlignLeft)], 0, 0, 0)
        i = table.addRow()
        table.setText(i, 0, u'Главный врач ______________ ', CReportBase.ReportBody)
        table.setText(i, 1, u'Главный бухгалтер ______________', CReportBase.ReportBody)
        return doc

class CAccount(QtGui.QDialog, Ui_ReportAccount):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance')
        self.cmbEventProfile.setTable('rbEventProfile', filter=u'code NOT IN ( \'211\', \' 80\', \' 262\', \' 222\', \'232\', \'252\', \'ГаЭнт\', \'Инф\', \'Кард\', \'Лор\', \'Невро\', \'Офтал\', \'Пульм\')' )
        self.cmbInsurerFilterDialog.setFilter('id IN (SELECT o.head_id FROM Organisation o WHERE o.head_id IS NOT NULL) AND left(area, 2) = \'23\'')
        self.cmbInsurerFilterDialog.setAddNone(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbEventProfile.setValue(params.get('eventProfileId', None))
        self.cmbInsurerFilterDialog.setValue(params.get('insurerId', 0))

    def params(self):
        params = {}
        params['begDate']           = self.edtBegDate.date()
        params['financeId']      = self.cmbFinance.value()
        params['eventProfileId'] = self.cmbEventProfile.value()
        params['insurerId']      = self.cmbInsurerFilterDialog.value()
        return params