# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from operator import add

from Events.Utils import getExposed, getPayStatusMask, getRefused, getPayed
from Orgs.Utils import getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportFE5PSetup import Ui_ReportFE5PSetupDialog
from library.Utils import forceString, forceInt, forceDouble, forceRef


class CReportFE5PSetupDialog(QtGui.QDialog, Ui_ReportFE5PSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.payStatusList = [
            QtCore.QString(u'Нет выставления, оплаты и отказа'),
            QtCore.QString(u'Выставлено, нет оплаты и отказа'),
            QtCore.QString(u'Отказано'),
            QtCore.QString(u'Оплачено'),
            QtCore.QString(u'Выставлено, оплачено, отказано')
        ]
        self.cmbPayStatus.addItems(self.payStatusList)

        self.cmbFinance.setTable('rbFinance', addNone=True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbFinance.setValue(params.get('typeFinanceId', 2))
        self.edtAccountNumber.setText(u', '.join(params.get('accountNumber', '')))

        self.chkPayStatus.setCheckState(params.get('payStatusCheckState', QtCore.Qt.Unchecked))
        self.cmbPayStatus.setCurrentIndex(self.payStatusList.index(params.get('payStatus', self.payStatusList[0])))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['typeFinanceId'] = self.cmbFinance.value()
        result['accountNumber'] = [s.strip() for s in forceString(self.edtAccountNumber.text()).split(u',') if len(s.strip()) > 0]

        result['payStatusCheckState'] = self.chkPayStatus.checkState()
        result['payStatus'] = self.cmbPayStatus.currentText()
        return result

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtAccountNumber_textChanged(self, text):
        self.edtBegDate.setEnabled(len(text) == 0)
        self.edtEndDate.setEnabled(len(text) == 0)


class CReportFE5P(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Анализ нагрузки на отделение (поликлинические виды помощи)")
        self._financeIds = QtGui.qApp.db.getIdList('rbFinance')

    def getSetupDialog(self, parent):
        self.dialog = CReportFE5PSetupDialog(parent)
        self.dialog.setTitle(self.title())
        return self.dialog

    def dumpParams(self, cursor, params, charFormat=QtGui.QTextCharFormat()):
        orgStructureId = params.get('orgStructureId', None)
        financeId = params.get('typeFinanceId', None)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        accountNumberList = params.get('accountNumber', None)

        payStatusCheckState = params.get('payStatusCheckState', QtCore.Qt.Unchecked)
        payStatus = params.get('payStatus', '')

        filterByDate = len(accountNumberList) == 0
        db = QtGui.qApp.db
        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(charFormat)

        financeType = u'не задано'
        if financeId is not None:
            financeType = forceString(db.translate('rbFinance', 'id', financeId, 'name'))
        cursor.insertText(u'Тип финансирования: ' + financeType)
        cursor.insertBlock()

        orgStructure = u'ЛПУ'
        if orgStructureId is not None:
            orgStructure = forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name'))
        cursor.insertText(u'Подразделение: ' + orgStructure)
        cursor.insertBlock()

        cursor.insertText(u'Тип подразделения: Амбулатория')
        cursor.insertBlock()

        if payStatusCheckState == QtCore.Qt.Checked:
            cursor.insertText(u'Тип реестра: %s' % payStatus)
        else:
            cursor.insertText(u'Тип реестра: не задан')
        cursor.insertBlock()

        if filterByDate:
            period = u''
            if begDate:
                period += u'c ' + begDate.toString('dd.MM.yyyy') + u' '
            if endDate:
                period += u'по ' + endDate.toString('dd.MM.yyyy')
            else:
                period += u'по ' + QtCore.QDate.currentDate().toString('dd.MM.yyyy')
            cursor.insertText(u'В отчет включены реестры с расчетными датами: ' + period)
            cursor.insertBlock()

    def selectData(self, params):
        stmt = u'''
            SELECT
                Account_Item.amount,
                Account_Item.sum,
                Account.number,

                IF (
                    Account_Item.service_id IS NOT NULL,
                    rbItemService.infis,
                    rbEventService.infis
                ) AS serviceCode,

                IF (
                    Account_Item.service_id IS NOT NULL,
                    rbItemService.name,
                    rbEventService.name
                ) AS serviceName,

                Person.orgStructure_id AS orgStructureId
            FROM
                Account_Item
                INNER JOIN Account ON Account_Item.master_id = Account.id AND Account.deleted = 0 
                INNER JOIN Event ON Account_Item.event_id = Event.id
                INNER JOIN Contract ON Event.contract_id = Contract.id
                LEFT JOIN EventType ON Event.eventType_id = EventType.id
                LEFT JOIN rbService AS rbItemService ON Account_Item.service_id = rbItemService.id
                LEFT JOIN rbService AS rbEventService ON EventType.service_id = rbEventService.id
                LEFT JOIN Person ON Person.id = Event.execPerson_id
                LEFT JOIN Action ON Action.id = Account_Item.action_id
                LEFT JOIN Visit ON Visit.id = Account_Item.visit_id
            %s
            HAVING
                serviceCode LIKE 'A%%' OR serviceCode LIKE 'B%%'
            ORDER BY
                orgStructureId
        '''

        orgStructureId = params.get('orgStructureId', None)
        financeId = params.get('typeFinanceId', None)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        accountNumberList = params.get('accountNumber', None)
        filterByDate = len(accountNumberList) == 0

        payStatusCheckState = params.get('payStatusCheckState', QtCore.Qt.Unchecked)
        payStatus = params.get('payStatus', '')

        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        tableContract = db.table('Contract')
        tableAccount = db.table('Account')
        tableEvent = db.table('Event')

        cond = [tableEvent['execDate'].isNotNull(), u'Account_Item.deleted = 0']
        if financeId is not None:
            cond.append(tableContract['finance_id'].eq(financeId))

        if orgStructureId:
            cond.append(db.joinAnd([
                db.joinOr([
                    tablePerson['orgStructure_id'].eq(orgStructureId),
                    tablePerson['orgStructure_id'].inInnerStmt(
                        "(SELECT id FROM OrgStructure_Ancestors WHERE fullPath LIKE '%" + str(orgStructureId) + "%')"
                    )
                ]),
            ]))

        if filterByDate:
            if begDate:
                cond.append(
                    u"DATE(COALESCE(Action.endDate, Visit.date, Event.execDate)) >= DATE('%s')" % begDate.toString(
                        'yyyy-MM-dd'))
            if endDate:
                cond.append(
                    u"DATE(COALESCE(Action.endDate, Visit.date, Event.execDate)) <= DATE('%s')" % endDate.toString(
                        'yyyy-MM-dd'))
        else:
            cond.append(tableAccount['number'].inlist(accountNumberList))

        # тип реестра
        if payStatusCheckState == QtCore.Qt.Checked:
            payStatusIndex = self.dialog.payStatusList.index(payStatus)
            payStatusList = []
            baseTable = 'Event'
            if payStatusIndex == 0:  # Нет выставления, оплаты и отказа
                cond.append('%s.payStatus = 0' % baseTable)
            elif payStatusIndex == 1:  # Выставлено, нет оплаты и отказа
                for f_id in self._financeIds:
                    payStatusList.append(str(getExposed(getPayStatusMask(f_id))))
                cond.append('%s.payStatus IN (%s)' % (baseTable, ','.join(payStatusList)))
            elif payStatusIndex == 2:  # Отказано, нет оплаты
                for f_id in self._financeIds:
                    payStatusList.append(str(getRefused(getPayStatusMask(f_id))))
                cond.append('%s.payStatus IN (%s)' % (baseTable, ','.join(payStatusList)))
            elif payStatusIndex == 3:  # Оплачено
                for f_id in self._financeIds:
                    payStatusList.append(str(getPayed(getPayStatusMask(f_id))))
                cond.append('%s.payStatus IN (%s)' % (baseTable, ','.join(payStatusList)))
            else:  # Выставлено, оплачено, отказано
                cond.append('%s.payStatus <> 0' % baseTable)

        return db.query(stmt % (u'WHERE\n' + db.joinAnd(cond) if cond else u''))

    def build(self, params):

        def printAll(reportData):
            totalByReport = printOrgStructures(reportData)
            i = table.addRow()
            table.setText(i, 1, u'Итого:', charFormat=boldChars, blockFormat=CReportBase.AlignRight)
            table.mergeCells(i, 0, 1, 2)
            table.setText(i, 2, totalByReport[0], blockFormat=CReportBase.AlignRight)
            table.setText(i, 3, "%.2f" % (totalByReport[1]), blockFormat=CReportBase.AlignRight)

        def printOrgStructures(reportData):
            total = [0, 0]
            orgStructures = reportData.keys()
            orgStructures.sort()
            for orgStructure in orgStructures:
                i = table.addRow()
                table.setText(i, 0, getOrgStructureFullName(orgStructure) if orgStructure else u'Подразделение не определено', charFormat=boldChars, blockFormat=CReportBase.AlignLeft)
                table.mergeCells(i, 0, 1, 4)

                i = table.addRow()
                table.setText(i, 0, u'Номера реестров: ' + u', '.join(sorted(orgStructureAccounts[orgStructure])))
                table.mergeCells(i, 0, 1, 4)

                totalByOrgStructure = printServices(reportData[orgStructure])
                total = map(add, total, totalByOrgStructure)

                i = table.addRow()
                table.setText(i, 0, u'Итого по отделению:', charFormat=boldChars, blockFormat=CReportBase.AlignRight)
                table.mergeCells(i, 0, 1, 2)
                table.setText(i, 2, totalByOrgStructure[0], blockFormat=CReportBase.AlignRight)
                table.setText(i, 3, "%.2f" % (totalByOrgStructure[1]), blockFormat=CReportBase.AlignRight)
            return total

        def printServices(reportData):
            total = [0, 0]
            services = reportData.keys()
            services.sort()
            for serviceCode, serviceName in services:
                i = table.addRow()
                table.setText(i, 0, serviceCode)
                table.setText(i, 1, serviceName)
                totalByService = reportData[(serviceCode, serviceName)]
                total = map(add, total, totalByService)
                table.setText(i, 2, totalByService[0], blockFormat=CReportBase.AlignRight)
                table.setText(i, 3, "%.2f" % (totalByService[1]), blockFormat=CReportBase.AlignRight)
            return total

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignRight)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'Форма Э-5П')
        cursor.insertBlock()

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()

        self.dumpParams(cursor, params)
        cursor.insertBlock()

        query = self.selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        orgStructureMap = {}
        orgStructureAccounts = {}
        while query.next():
            record = query.record()
            orgStructureId = forceRef(record.value('orgStructureId'))
            orgStructureAccounts.setdefault(orgStructureId, set()).add(forceString(record.value('number')))

            serviceMap = orgStructureMap.setdefault(orgStructureId, {})
            serviceCode = forceString(record.value('serviceCode'))
            serviceCode = serviceCode if serviceCode else None
            serviceName = forceString(record.value('serviceName'))
            serviceName = serviceName if serviceName else None
            existData = serviceMap.setdefault((serviceCode, serviceName), [0, 0])

            data = [forceInt(record.value('amount')), forceDouble(record.value('sum'))]
            serviceMap[(serviceCode, serviceName)] = map(add, existData, data)


        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        tableColumns = [
            ('10%', [u'Услуга', u'Код'], CReportBase.AlignLeft),
            ('70%', [u'', u'Наименование'], CReportBase.AlignLeft),
            ('10%', [u'Кол-во услуг', u''], CReportBase.AlignLeft),
            ('10%', [u'Сумма', u''], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)

        printAll(orgStructureMap)

        return doc

