# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################
from operator import add

from PyQt4 import QtCore, QtGui

from library.Utils       import forceDate, forceInt, forceString, forceRef, forceDouble
from Orgs.Utils          import getOrgStructureDescendants
from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase


def selectData(params):

    #print QtCore.QTime.currentTime().toString('hh:mm')
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate', None))
    endDate = forceDate(params.get('endDate', None))
    financeId = forceInt(params.get('financeId', None))
    ageIndex = forceInt(params.get('age', 0))
    where = ''
    if begDate:
        where += u"AND DATE(Account.settleDate) >= DATE('%s') " % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += u"AND DATE(Account.settleDate) <= DATE('%s') " % endDate.toString('yyyy-MM-dd')
    if params.get('orgStructureId', None):
        orgStruct = forceString(getOrgStructureDescendants(params['orgStructureId']))
        orgStruct = orgStruct.replace('[', '(')
        orgStruct = orgStruct.replace(']', ')')
        where += u"AND OrgStructure.id IN " + orgStruct
    if financeId:
        where += u"AND (Contract.finance_id = %(financeId)s) " % {'financeId' : financeId}
    if ageIndex:
        if ageIndex == 1:
            childAge = forceInt(db.translate('GlobalPreferences', 'code', -22, 'value'))
            where += u"AND age(Client.birthDate, DATE('%(curDate)s')) < %(age)s " % {'curDate' : QtCore.QDate.currentDate().toString('yyyy-MM-dd'),
                                                                                    'age' : childAge}
        elif ageIndex == 2:
            childAge = forceInt(db.translate('GlobalPreferences', 'code', -22, 'value'))
            menRetirementAge = forceInt(db.translate('GlobalPreferences', 'code', -23, 'value'))
            womenRetirementAge = forceInt(db.translate('GlobalPreferences', 'code', -24, 'value'))
            where += u'''AND age(Client.birthDate, DATE('%(curDate)s')) >= %(childAge)s
                         AND ((age(Client.birthDate, DATE('%(curDate)s')) < %(menRetirementAge)s AND Client.sex = 1)
                         OR (age(Client.birthDate, DATE('%(curDate)s')) < %(womenRetirementAge)s AND Client.sex = 2)) ''' \
                     % {'curDate' : QtCore.QDate.currentDate().toString('yyyy-MM-dd'),
                        'childAge' : childAge,
                        'menRetirementAge' : menRetirementAge,
                        'womenRetirementAge' : womenRetirementAge}
        elif ageIndex == 3:
            menRetirementAge = forceInt(db.translate('GlobalPreferences', 'code', -23, 'value'))
            womenRetirementAge = forceInt(db.translate('GlobalPreferences', 'code', -24, 'value'))
            where += u'''AND ((age(Client.birthDate, DATE('%(curDate)s')) < %(menRetirementAge)s AND Client.sex = 1)
                         OR (age(Client.birthDate, DATE('%(curDate)s')) < %(womenRetirementAge)s AND Client.sex = 2)) ''' \
                     % {'curDate' : QtCore.QDate.currentDate().toString('yyyy-MM-dd'),
                        'menRetirementAge' : menRetirementAge,
                        'womenRetirementAge' : womenRetirementAge}

    # для понимания происходящего в подзапросах рекомендуется прочесть
    # http://www.xaprb.com/blog/2006/12/07/how-to-select-the-firstleastmax-row-per-group-in-sql/
    stmt = u'''
    SELECT
        Account.number,
        LPU.title as LPUName,
        OrgStructureInfo.orgStructureName,
        Event.id as eventId,
        Event.MES_id as mesId,
        Account_Item.amount,
        Account_Item.sum,
        IF (
            Account_Item.service_id IS NOT NULL,
            rbItemService.infis,
            IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
        ) AS service
    FROM
        Account_Item
        INNER JOIN Event ON Account_Item.event_id = Event.id
        INNER JOIN EventType ON Event.eventType_id = EventType.id
        INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id AND rbEventTypePurpose.code IN (101, 102)
        INNER JOIN Client ON Event.client_id = Client.id
        INNER JOIN Contract_Tariff ON Contract_Tariff.id = Account_Item.tariff_id
        INNER JOIN Contract ON Contract.id = Contract_Tariff.master_id
        INNER JOIN Account ON Account_Item.master_id = Account.id
        INNER JOIN Person ON Event.execPerson_id = Person.id
        INNER JOIN Organisation AS LPU ON Person.org_id = LPU.id
        INNER JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id

        LEFT JOIN (
            SELECT
                Event.id as event_id,
                OS.name AS orgStructureName
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
                        MIN(A.begDate) AS begDate
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

        LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
        LEFT JOIN Visit ON Visit.id = Account_Item.visit_id
        LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
        LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id

    WHERE
        Event.execDate is not null
        AND Account_Item.deleted = 0
        AND Event.deleted = 0
        AND EventType.deleted = 0
        AND Contract_Tariff.deleted = 0
        AND Contract.deleted = 0
        AND Account.deleted = 0
        AND Person.deleted = 0
        AND LPU.deleted = 0
        AND OrgStructure.deleted = 0
        %s
    ''' % where

    return db.query(stmt)


class CReportE15S(CReport):
    def __init__(self, parent = None, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Ан-з нагрузки на отд-е по плательщикам Э-15С (стац. виды помощи)')

    def getSetupDialog(self, parent):
        result = CReportE15SSetupDialog(parent)
        result.setTitle(self.title())
        return result

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
            table.setText(row, 0, text, charFormat=charFormat, blockFormat=CReportBase.AlignLeft)
            for j in xrange(3):
                table.setText(row, j + 1, values[j], blockFormat=CReportBase.AlignRight)
            table.setText(row, 4, "%.2f" % values[3], blockFormat=CReportBase.AlignRight)

        def printAll(reportData):
            totalByReport = printInsurers(reportData)
            printLine(table.addRow(), totalByReport, boldChars, u'Итого')

        def printInsurers(reportData):
            total = [0] * (len(tableColumns) - 1)
            insurers = reportData.keys()
            insurers.sort()
            for insurer in insurers:
                i = table.addRow()
                table.mergeCells(i, 0, 1, len(tableColumns))
                table.setText(i, 0, u'Плательщик: ' + insurer, charFormat=boldChars, blockFormat=CReportBase.AlignCenter)
                totalByInsurer = printOrganisations(reportData[insurer])
                printLine(table.addRow(), totalByInsurer, boldChars, u'Итого по плательщику')
                total = map(add, total, totalByInsurer)
            return total

        def printOrganisations(reportData):
            total = [0] * (len(tableColumns) - 1)
            organisations = reportData.keys()
            organisations.sort()
            for organisation in organisations:
                i = table.addRow()
                totalByOrganisation = printAccounts(reportData[organisation])
                printLine(i, totalByOrganisation, boldChars, organisation)
                total = map(add, total, totalByOrganisation)
            return total

        def printAccounts(reportData):
            total = [0] * (len(tableColumns) - 1)
            accounts = reportData.keys()
            accounts.sort()
            for account in accounts:
                i = table.addRow()
                totalByAccount = printOrgStructures(reportData[account])
                printLine(i, totalByAccount, boldChars, account)
                total = map(add, total, totalByAccount)
            return total

        def printOrgStructures(reportData):
            total = [0] * (len(tableColumns) - 1)
            orgStructures = reportData.keys()
            orgStructures.sort()
            for orgStructure in orgStructures:
                values = reportData[orgStructure]['values']
                printLine(table.addRow(), values, CReportBase.TableBody, u'    ' + orgStructure if orgStructure else u'Подразделение не определено')
                total = map(add, total, values)
            return total

        db = QtGui.qApp.db
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Анализ нагрузки на отделение по плательщикам Э-15С (стационарные виды помощи)')
        cursor.insertBlock()

        pf = QtGui.QTextCharFormat()
        cursor.setCharFormat(pf)

        begDate = forceDate(params.get('begDate', None))
        endDate = forceDate(params.get('endDate', None))
        financeId = forceInt(params.get('financeId', None))
        ageIndex = forceInt(params.get('age', 0))
        orgStructId = forceInt(params.get('orgStructureId', None))
        financeType = u'не задано'
        if financeId:
            financeType = forceString(db.translate('rbFinance', 'id', financeId, 'name'))
        cursor.insertText(u'Тип финансирования: ' + financeType)
        cursor.insertBlock()
        orgStructure = u'ЛПУ'
        if orgStructId:
            orgStructure = forceString(db.translate('OrgStructure', 'id', orgStructId, 'name'))
        cursor.insertText(u'Подразделение: ' + orgStructure)
        cursor.insertBlock()
        cursor.insertText(u'Тип подразделения: Стационар')
        cursor.insertBlock()
        age = u'Все'
        if ageIndex == 1:
            age = u'Дети'
        if ageIndex == 2:
            age = u'Взрослые'
        if ageIndex == 3:
            age = u'Лица старше трудоспособного возраста'
        cursor.insertText(u'Возрастные категории: ' + age)
        cursor.insertBlock()
        period = u''
        if begDate:
            period += u'c ' + begDate.toString('dd.MM.yyyy') + ' '
        if endDate:
            period += u'по ' + endDate.toString('dd.MM.yyyy')
        else:
            period += u'по ' + QtCore.QDate.currentDate().toString('dd.MM.yyyy')
        cursor.insertText(u'Период: ' + period)
        cursor.insertBlock()

        tableColumns = [
            ( '40%', [u'Плательщик / Отделение'], CReportBase.AlignCenter),
            ( '15%', [u'Кол-во случаев'], CReportBase.AlignCenter),
            ( '15%', [u'Кол-во КСГ'], CReportBase.AlignCenter),
            ( '15%', [u'Кол-во койко-дней'], CReportBase.AlignCenter),
            ( '15%', [u'Сумма (руб)'], CReportBase.AlignCenter)
        ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        recordList = []
        insurerInfisSet = set()
        while query.next():
            record = query.record()
            recordList.append(record)
            insurerInfisSet.add(getInfisByAccountNumber(forceString(record.value('number'))))

        tableOrganisation = db.table('Organisation')
        insurers = db.getRecordList(
            tableOrganisation,
            [tableOrganisation['fullName'], tableOrganisation['area'], tableOrganisation['infisCode']],
            db.joinAnd([
                tableOrganisation['deleted'].eq(0),
                tableOrganisation['isInsurer'].eq(1),
                tableOrganisation['infisCode'].inlist(list(insurerInfisSet.difference([None])))
            ])
        )
        insurerMap = {}
        for insurer in insurers:
            infisCode = forceString(insurer.value('infisCode'))
            area = forceString(insurer.value('area'))
            fullName = forceString(insurer.value('fullName'))
            insurerMap[infisCode] = infisCode + u' ' + fullName if area.startswith('23') else u'9007 «ТФОМС»'

        if None in insurerInfisSet:
            insurerMap[None] = u'не определен'

        resultMap = {}
        insurerAccounts = {}
        for record in recordList:
            accountNumber = forceString(record.value('number'))
            insurer = insurerMap[getInfisByAccountNumber(accountNumber)]
            insurerAccounts.setdefault(insurer, set()).add(accountNumber)

            orgMap = resultMap.setdefault(insurer, {})
            orgStructureMap = orgMap.setdefault(forceString(record.value('LPUName')), {})
            orgStructureName = forceString(record.value('orgStructureName'))
            existAccountMap = orgStructureMap.setdefault(accountNumber, {})
            existData = existAccountMap.setdefault(orgStructureName, {'events': set(), 'values': [0] * 4})

            eventId = forceInt(record.value('eventId'))
            newEvent = 1 if eventId not in existData['events'] else 0
            existData['events'].add(eventId)
            isKsg = 1 if newEvent and forceRef(record.value('mesId')) is not None else 0
            amount = forceInt(record.value('amount'))
            serviceInfis = forceString(record.value('service'))
            bedDays = amount if isKsg and serviceInfis[0] in ['K', 'S', 'G', 'V'] else 0
            sum = forceDouble(record.value('sum'))

            data = [newEvent, isKsg, bedDays, sum]
            existData['values'] = map(add, existData['values'], data)

        printAll(resultMap)

        return doc

from Ui_ReportE15SSetup import Ui_ReportE15SSetupDialog

class CReportE15SSetupDialog(QtGui.QDialog, Ui_ReportE15SSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance')
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbAge.setCurrentIndex(forceInt(params.get('age', 0)))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['financeId'] = self.cmbFinance.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['age'] = self.cmbAge.currentIndex()
        return result