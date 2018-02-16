# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2015 Vista Software. All rights reserved.
##
#############################################################################
from operator import add

from PyQt4 import QtGui, QtCore

from Events.Utils import getExposed, getPayStatusMask, getRefused, getPayed
from library.Utils       import forceInt, forceString, forceRef, forceDouble
from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase
from Ui_ReportFE24SSetup import Ui_ReportFE24SSetupDialog


class CReportFE24SSetupDialog(QtGui.QDialog, Ui_ReportFE24SSetupDialog):
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

        self.cmbFinance.setTable('rbFinance')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbTariffType.setCurrentIndex(forceInt(params.get('tariffType', 0)))
        self.edtAccountNumber.setText(u', '.join(params.get('accountNumber', '')))
        self.rbtnByAction.setChecked(params.get('orgStructureByAction', True))
        self.rbtnByPerson.setChecked(not params.get('orgStructureByAction', True))
        self.chkPayStatus.setCheckState(params.get('payStatusCheckState', QtCore.Qt.Unchecked))
        self.cmbPayStatus.setCurrentIndex(self.payStatusList.index(params.get('payStatus', self.payStatusList[0])))

    def params(self):
        result = {}
        result['financeId'] = self.cmbFinance.value()
        result['tariffType'] = self.cmbTariffType.currentIndex()
        result['accountNumber'] = [s.strip() for s in forceString(self.edtAccountNumber.text()).split(u',') if len(s.strip()) > 0]
        result['orgStructureByAction'] = self.rbtnByAction.isChecked()

        result['payStatusCheckState'] = self.chkPayStatus.checkState()
        result['payStatus'] = self.cmbPayStatus.currentText()
        return result

    def accept(self):
        if self.edtAccountNumber.text() == u'':
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Не указан номер реестра!',
                QtGui.QMessageBox.Ok
            )
            return
        QtGui.QDialog.accept(self)


class CReportFE24S(CReport):
    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Ан-з нагрузки на отд-е по профилям коек Э-24С (стац. виды помощи)')
        self._financeIds = QtGui.qApp.db.getIdList('rbFinance')

    def getSetupDialog(self, parent):
        self.dialog = CReportFE24SSetupDialog(parent)
        self.dialog.setTitle(self.title())
        return self.dialog

    def selectData(self, params):
        # для понимания происходящего в подзапросах рекомендуется прочесть
        # http://www.xaprb.com/blog/2006/12/07/how-to-select-the-firstleastmax-row-per-group-in-sql/
        stmt = u'''
        SELECT
            OrgStructureInfo.name AS orgStructureName,
            HospitalBedsInfo.profileName AS profileName,
            Event.id AS eventId,
            Event.MES_id AS mesId,
            Account_Item.amount,
            Account_Item.sum,
            Account_Item.price,
            Contract.regionalTariffRegulationFactor AS regulator,
            AdditionalExpenseM.percent AS additionalExpenseMPercent,
            PaymentExpense.percent AS paymentExpensePercent,
            IF (
                Account_Item.service_id IS NOT NULL,
                rbItemService.infis,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
            ) AS service
        FROM
            Account_Item
            INNER JOIN Account ON Account_Item.master_id = Account.id
            INNER JOIN Event ON Account_Item.event_id = Event.id
            INNER JOIN EventType ON Event.eventType_id = EventType.id
            INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id AND rbEventTypePurpose.code IN (101, 102)
            INNER JOIN Contract_Tariff ON Contract_Tariff.id = Account_Item.tariff_id
            INNER JOIN Contract ON Contract.id = Contract_Tariff.master_id
            INNER JOIN Person ON Event.execPerson_id = Person.id

            LEFT JOIN %s

            LEFT JOIN (
                SELECT
                    A.event_id,
                    OS.name AS orgStructureName,
                    rbHBP.name AS profileName
                FROM
                    Action AS A
                    INNER JOIN ActionType AS AT ON A.actionType_id = AT.id
                    INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = AT.id AND APT.name RLIKE 'койк'
                    INNER JOIN ActionProperty AS AP ON AP.action_id = A.id AND AP.type_id = APT.id
                    INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id = AP.id
                    INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id = APHB.value
                    INNER JOIN rbHospitalBedProfile AS rbHBP ON OSHB.profile_id = rbHBP.id
                    INNER JOIN OrgStructure AS OS ON OS.id = OSHB.master_id

                    INNER JOIN (
                        SELECT
                            A.event_id,
                            MIN(A.id) as id
                        FROM
                            Action AS A
                            INNER JOIN ActionType AS AT ON A.actionType_id = AT.id
                            INNER JOIN ActionPropertyType AS APT ON APT.actionType_id = AT.id AND APT.name RLIKE 'койк'
                            INNER JOIN ActionProperty AS AP ON AP.action_id = A.id AND AP.type_id = APT.id
                            INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id = AP.id
                            INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id = APHB.value
                            INNER JOIN rbHospitalBedProfile AS rbHBP ON OSHB.profile_id = rbHBP.id
                            INNER JOIN OrgStructure AS OS ON OS.id = OSHB.master_id
                        WHERE
                            A.deleted = 0
                            AND AT.deleted = 0
                            AND APT.deleted = 0
                            AND AP.deleted = 0
                        GROUP BY
                            A.event_id
                    ) AS MA ON A.event_id = MA.event_id AND A.id = MA.id

                WHERE
                    A.deleted = 0
                    AND AT.deleted = 0
                    AND APT.deleted = 0
                    AND AP.deleted = 0
            ) AS HospitalBedsInfo ON HospitalBedsInfo.event_id = Event.id

            LEFT JOIN rbMedicalAidType ON rbMedicalAidType.id = EventType.medicalAidType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN Visit ON Visit.id = Account_Item.visit_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id

            LEFT JOIN Contract_CompositionExpense AS AdditionalExpenseM ON  AdditionalExpenseM.id = (
                SELECT MAX(CCE3.id)
                FROM Contract_CompositionExpense AS CCE3
                LEFT JOIN rbExpenseServiceItem ON CCE3.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code IN ('3', '230004')  AND CCE3.master_id = Contract_Tariff.id
            )

            LEFT JOIN Contract_CompositionExpense AS PaymentExpense ON  PaymentExpense.id = (
                SELECT MAX(CCE4.id)
                FROM Contract_CompositionExpense AS CCE4
                LEFT JOIN rbExpenseServiceItem ON CCE4.rbTable_id =rbExpenseServiceItem.id
                WHERE rbExpenseServiceItem.code IN ('4', '230005')  AND CCE4.master_id = Contract_Tariff.id
            )

        WHERE
            %s
        '''
        db = QtGui.qApp.db

        orgStructureByAction = params.get('orgStructureByAction', True)
        if orgStructureByAction:
            orgStructureInfo = u'''
            (
                SELECT
                    Event.id as event_id,
                    OS.name
                FROM
                    Event
                    INNER JOIN Action AS A ON Event.id = A.event_id
                    INNER JOIN ActionPropertyType AS APT
                    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
                    INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
                    INNER JOIN OrgStructure AS OS ON OS.id = APOS.value

                    INNER JOIN (
                        SELECT
                            Event.id AS event_id,
                            MAX(A.begDate) AS begDate
                        FROM
                            Event
                            INNER JOIN Action AS A ON Event.id = A.event_id
                            INNER JOIN ActionPropertyType AS APT
                            INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
                            INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
                            INNER JOIN OrgStructure AS OS ON OS.id = APOS.value
                        WHERE
                            A.actionType_id IN (SELECT id FROM ActionType where name = 'Движение')
                            AND APT.actionType_id = A.actionType_id
                            AND AP.action_id = A.id
                            AND APT.deleted = 0
                            AND (APT.name RLIKE 'Отделение')
                            AND OS.deleted = 0
                        GROUP BY
                            event_id
                    ) AS MA ON A.event_id = MA.event_id AND A.begDate = MA.begDate
                WHERE
                    A.actionType_id IN (SELECT id FROM ActionType where name = 'Движение')
                    AND APT.actionType_id = A.actionType_id
                    AND AP.action_id = A.id
                    AND APT.deleted = 0
                    AND (APT.name RLIKE 'Отделение')
                    AND OS.deleted = 0
            ) AS OrgStructureInfo ON OrgStructureInfo.event_id = Event.id
            '''
        else:
            orgStructureInfo = u'''OrgStructure AS OrgStructureInfo ON Person.orgStructure_id = OrgStructureInfo.id'''

        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tableContractTariff = db.table('Contract_Tariff')
        tableContract = db.table('Contract')
        tableAccount = db.table('Account')
        tableAccountItem = db.table('Account_Item')
        tablePerson = db.table('Person')
        tableOrgStructure = db.table('OrgStructure')

        cond = [
            tableEvent['execDate'].isNotNull(),
            tableEvent['deleted'].eq(0),
            tableEventType['deleted'].eq(0),
            tableContractTariff['deleted'].eq(0),
            tableContract['deleted'].eq(0),
            tableAccount['deleted'].eq(0),
            tableAccountItem['deleted'].eq(0),
            tablePerson['deleted'].eq(0),
        ]

        if not orgStructureByAction:
            cond.append(tableOrgStructure.alias('OrgStructureInfo')['deleted'].eq(0))

        financeId = forceInt(params.get('financeId', None))
        if financeId:
            cond.append(tableContract['finance_id'].eq(financeId))
        accountNumber = params.get('accountNumber')
        cond.append(tableAccount['number'].inlist(accountNumber))

        payStatusCheckState = params.get('payStatusCheckState', QtCore.Qt.Unchecked)
        payStatus = params.get('payStatus', '')

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

        return db.query(stmt % (orgStructureInfo, db.joinAnd(cond)))

    def build(self, params):

        def getInfisByAccountNumber(accountNumber):
            try:
                if accountNumber[accountNumber.rfind(u'/') + 1] == u'p':
                    accountNumber = accountNumber[:-2]
                infisStr = accountNumber[accountNumber.rfind(u'/') + 1:]
                if len(infisStr) != 4:
                    raise ValueError
                return infisStr
            except Exception, e:
                return None

        def printLine(row, values, charFormat, text):
            table.setText(row, 0, text, charFormat=charFormat, blockFormat=CReportBase.AlignRight)
            for j in xrange(3):
                table.setText(row, j + 1, values[j], charFormat=charFormat, blockFormat=CReportBase.AlignRight)
            table.setText(row, 4, "%.2f" % values[3], charFormat=charFormat, blockFormat=CReportBase.AlignRight)

        def printAll(reportData):
            totalByReport = printOrgStructures(reportData)
            printLine(table.addRow(), totalByReport, boldChars, u'Итого:')

        def printOrgStructures(reportData):
            total = [0] * (len(tableColumns) - 1)
            orgStructures = reportData.keys()
            orgStructures.sort()
            for orgStructure in orgStructures:
                row = table.addRow()
                table.mergeCells(row, 0, 1, len(tableColumns))
                table.setText(row, 0, orgStructure)
                totalByOrgStructure = printProfiles(reportData[orgStructure])
                printLine(table.addRow(), totalByOrgStructure, boldChars, u'Итого по отделению:')
                total = map(add, total, totalByOrgStructure)
            return total

        def printProfiles(reportData):
            total = [0] * (len(tableColumns) - 1)
            profiles = reportData.keys()
            profiles.sort()
            for profile in profiles:
                printLine(table.addRow(), reportData[profile]['values'], CReportBase.TableBody, profile)
                total = map(add, total, reportData[profile]['values'])
            return total

        db = QtGui.qApp.db
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        payStatusCheckState = params.get('payStatusCheckState', QtCore.Qt.Unchecked)
        payStatus = params.get('payStatus', '')

        cursor.setBlockFormat(CReportBase.AlignRight)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'Форма Э-24С')
        cursor.insertBlock()

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Анализ нагрузки на отделение по профилям коек Э-24С (стационарные виды помощи)')
        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignLeft)

        pf = QtGui.QTextCharFormat()
        cursor.setCharFormat(pf)

        lpuName = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'fullName'))
        cursor.insertText(lpuName)
        cursor.insertBlock()

        financeType = u'не задано'
        financeId = forceInt(params.get('financeId', None))
        if financeId:
            financeType = forceString(db.translate('rbFinance', 'id', financeId, 'name'))
        cursor.insertText(u'Тип финансирования: ' + financeType)
        cursor.insertBlock()

        cursor.insertText(u'Тип подразделения: Стационарный')
        cursor.insertBlock()

        if payStatusCheckState == QtCore.Qt.Checked:
            cursor.insertText(u'Тип реестра: %s' % payStatus)
        else:
            cursor.insertText(u'Тип реестра: не задан')
        cursor.insertBlock()

        # Пока предполагается, что отчет формируется по одному счету.
        accountNumber = params.get('accountNumber', None)[0]
        insurerInfis = getInfisByAccountNumber(accountNumber)
        insurerName = forceString(db.translate('Organisation', 'infisCode', insurerInfis, 'fullName'))
        cursor.insertText(u'По услугам, входяшим в счет: ' + accountNumber + u', плательщик — ' + insurerName)
        cursor.insertBlock()

        tariffType = params.get('tariffType', 0)

        tableColumns = [
            ( '40%', [u'Отделение / Профиль койки'], CReportBase.AlignCenter),
            ( '15%', [u'Кол-во случаев'], CReportBase.AlignCenter),
            ( '15%', [u'Кол-во КСГ'], CReportBase.AlignCenter),
            ( '15%', [u'Кол-во дней лечения'], CReportBase.AlignCenter),
            ( '15%', [u'Сумма (руб)'], CReportBase.AlignCenter)
        ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        reportData = {}
        while query.next():
            record = query.record()
            orgStructureName = forceString(record.value('orgStructureName'))
            bedProfiles = reportData.setdefault(orgStructureName if orgStructureName else u'Подразделение не определено', {})
            profileName = forceString(record.value('profileName'))
            existData = bedProfiles.setdefault(profileName if profileName else u'Не определено', {'events': set(), 'values': [0] * 4})

            eventId = forceInt(record.value('eventId'))
            newEvent = 1 if eventId not in existData['events'] else 0
            existData['events'].add(eventId)
            isKsg = 1 if forceRef(record.value('mesId')) is not None and newEvent else 0
            amount = forceInt(record.value('amount'))
            serviceInfis = forceString(record.value('service'))
            bedDays = amount if isKsg and serviceInfis[0] in ['K', 'S', 'G', 'V'] else 0
            if tariffType == 0:
                sum = forceDouble(record.value('sum'))
            else:
                price = forceDouble(record.value('price'))
                if tariffType == 1:
                    additionalExpenseMPercent = forceDouble(record.value('additionalExpenseMPercent'))
                    sum = price * additionalExpenseMPercent / 100.0 * amount
                else:
                    paymentExpensePercent = forceDouble(record.value('paymentExpensePercent'))
                    regulator = forceDouble(record.value('regulator'))
                    sum = price * paymentExpensePercent / 100.0 * amount * regulator
            values = [newEvent, isKsg, bedDays, sum]
            existData['values'] = map(add, existData['values'], values)

        printAll(reportData)

        return doc


