# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrganisationShortName
from Reports.FinanceSummaryByDoctors import getCond, CFinanceSummarySetupDialog, getOrder
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceBool, forceDouble, forceInt, forceString


def selectDataByEvents(params):
    stmt="""
SELECT
    rbService.code,
    rbService.name,
    (SELECT COUNT(D.id) 
     FROM Diagnostic AS D
     LEFT JOIN rbDiagnosisType AS DT ON DT.id = D.diagnosisType_id
     WHERE DT.code in ('1','2') 
            AND D.event_id = Event.id 
            AND D.deleted = 0
                              ) as sumDivider,
    SUM(Account_Item.amount) AS amount,
    SUM(Account_Item.sum) AS sum,
    LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                   Account_Item.amount,
                                   LEAST(tariff.federalLimitation, Account_Item.amount)),
          Account_Item.sum) AS federalSum,
    SUM(Account_Item.uet) AS uet,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NULL) AS exposed,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NOT NULL) as refused,
    Account.payer_id as insurerId
FROM Account_Item
LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN Event           ON Event.id = Account_Item.event_id
LEFT JOIN Contract        ON Contract.id = Account.contract_id
LEFT JOIN EventType       ON EventType.id = Event.eventType_id
LEFT JOIN rbService       ON rbService.id = IF(Account_Item.service_id IS NULL, EventType.service_id, Account_Item.service_id)
LEFT JOIN Diagnostic      ON Diagnostic.event_id = Event.id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
LEFT JOIN Person          ON Person.id = Diagnostic.person_id AND Person.retired = 0
LEFT JOIN rbSpeciality    ON rbSpeciality.id = Person.speciality_id
LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
WHERE
    Account_Item.visit_id IS NULL
    AND Account_Item.deleted = 0
    AND Account_Item.action_id IS NULL
    AND Diagnostic.deleted = 0
    AND rbDiagnosisType.code in ('1','2')
    AND %s
GROUP BY
    rbService.id, exposed, refused
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params))


def selectDataByVisits(params):
    stmt="""
SELECT
    rbService.code,
    rbService.name,
    1 AS sumDivider,
    SUM(Account_Item.amount) AS amount,
    SUM(Account_Item.sum) AS sum,
    LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                   Account_Item.amount,
                                   LEAST(tariff.federalLimitation, Account_Item.amount)),
          Account_Item.sum) AS federalSum,
    SUM(Account_Item.uet) AS uet,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NULL) AS exposed,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NOT NULL) as refused,
    Account.payer_id as insurerId
FROM Account_Item
LEFT JOIN Account      ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN Event           ON Event.id = Account_Item.event_id
LEFT JOIN EventType       ON EventType.id = Event.eventType_id
LEFT JOIN Contract        ON Contract.id = Account.contract_id
LEFT JOIN Visit        ON Visit.id = Account_Item.visit_id
LEFT JOIN rbService    ON rbService.id = IF(Account_Item.service_id IS NULL, Visit.service_id, Account_Item.service_id)
LEFT JOIN Person       ON Person.id = Visit.person_id AND Person.retired = 0
LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
WHERE
    Account_Item.visit_id IS NOT NULL
    AND Account_Item.deleted = 0
    AND Account_Item.action_id IS NULL
    AND %s
GROUP BY
    rbService.id, exposed, refused
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 1))


def selectDataByActions(params):
    stmt="""
SELECT
    rbService.code,
    rbService.name,
    1 AS sumDivider,
    SUM(Account_Item.amount) AS amount,
    SUM(Account_Item.sum) AS sum,
    LEAST(tariff.federalPrice * IF(tariff.federalLimitation = 0,
                                   Account_Item.amount,
                                   LEAST(tariff.federalLimitation, Account_Item.amount)),
          Account_Item.sum) AS federalSum,
    SUM(Account_Item.uet) AS uet,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NULL) AS exposed,
    (Account_Item.date IS NOT NULL AND Account_Item.number != '' AND Account_Item.refuseType_id IS NOT NULL) AS refused,
    ActionType.serviceType AS serviceType,
    Account.payer_id as insurerId
FROM Account_Item
LEFT JOIN Account      ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN Event           ON Event.id = Account_Item.event_id
LEFT JOIN EventType       ON EventType.id = Event.eventType_id
LEFT JOIN Contract        ON Contract.id = Account.contract_id
LEFT JOIN Action       ON Action.id = Account_Item.action_id
LEFT JOIN ActionType   ON ActionType.id = Action.actionType_id
LEFT JOIN rbService    ON rbService.id = Account_Item.service_id
LEFT JOIN Person       ON Person.id = Action.person_id AND Person.retired = 0
LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
LEFT JOIN Contract_Tariff AS tariff ON tariff.id = Account_Item.tariff_id
LEFT JOIN OrgStructure_ActionType ON ActionType.id = OrgStructure_ActionType.actionType_id
WHERE
    Account_Item.visit_id IS NULL
    AND Account_Item.deleted = 0
    AND Account_Item.action_id IS NOT NULL
    AND %s
GROUP BY
    rbService.id, exposed, refused
    %s
    """
    db = QtGui.qApp.db
    return db.query(stmt % (getCond(params, 2), getOrder(params)))

docServiceTypeName = [
    u'прочие',
    u'консультация',
    u'консультация',
    u'процедуры',
    u'операция',
    u'анализы',
    u'лечение',
    u'расходники',
    u'оплата палат',
]


class CFinanceSummaryByServices(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Финансовая сводка по услугам')


    def build(self, description, params):
        reportRowSize = 9
        reportData = {}
        detailServiceTypes = params.get('detailServiceTypes', False)
        detailInsurer = params.get('chkInsurer', False)

        def processQuery(query):
            self.setQueryText(forceString(query.lastQuery()))
            while query.next():
                record = query.record()
                code = forceString(record.value('code'))
                name = forceString(record.value('name'))
                sumDivider = forceInt(record.value('sumDivider'))

                amount = forceDouble(record.value('amount')) / sumDivider
                uet = forceDouble(record.value('uet')) / sumDivider
                if amount == int(amount):
                    amount = int(amount)
                sum = forceDouble(record.value('sum'))
                isWithoutModernisation = params.get('withoutModernisation', False)
                if isWithoutModernisation:
                    federalSum = forceDouble(record.value('federalSum')) / sumDivider
                    sum = sum - federalSum
                exposed = forceBool(record.value('exposed'))
                refused = forceBool(record.value('refused'))

                group = (forceInt(record.value('serviceType')) if detailServiceTypes else None,
                         forceInt(record.value('insurerId')) if detailInsurer else None)
                reportLine = reportData.setdefault(group, {}).setdefault((name, code), [0]*reportRowSize)

                # serviceType = forceInt(record.value('serviceType')) if detailServiceTypes else None
                # reportLine = reportData.setdefault(serviceType, {}).setdefault((name, code), [0]*reportRowSize)
                reportLine[0] += amount
                reportLine[1] += uet
                reportLine[2] += sum
                if exposed:
                    reportLine[3] += amount
                    reportLine[4] += uet
                    reportLine[5] += sum
                if refused:
                    reportLine[6] += amount
                    reportLine[7] += uet
                    reportLine[8] += sum

        query = selectDataByEvents(params)
        processQuery(query)
        query = selectDataByVisits(params)
        processQuery(query)
        query = selectDataByActions(params)
        processQuery(query)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()

        headerStmt = u"""
            SELECT
              Organisation.shortName AS payerName,
              Account.number AS accNumber,
              Contract.grouping AS accGroup,
              Contract.resolution AS accResolution
            FROM Account
              INNER JOIN Contract ON Contract.id = Account.contract_id
              INNER JOIN Organisation ON Account.payer_id = Organisation.id
            WHERE
              Account.id = %s
            """ % params.get('accountId', 0)
        record = QtGui.qApp.db.getRecordEx(stmt=headerStmt)
        if record:
            # Можно сделать при помощи Report.getDescription(params)
            cursor.setCharFormat(QtGui.QTextCharFormat())
            cursor.insertText(u'Наименование СМО: ' + forceString(record.value('payerName')))
            cursor.insertBlock()
            cursor.insertText(u'Номер счета: ' + forceString(record.value('accNumber')))
            cursor.insertBlock()
            cursor.insertText(
                u'Группа / основание договора: '
                + forceString(record.value('accGroup'))
                + u' / '
                + forceString(record.value('accResolution'))
            )
            cursor.insertBlock()

        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                          ('30%', [ u'Услуга',   u'наименование'], CReportBase.AlignLeft ),
                          ('5%',  [ u'',         u'код'         ], CReportBase.AlignLeft ),
                          ('7%', [ u'Всего',    u'кол-во'      ], CReportBase.AlignRight ),
                          ('7%', [ u'',         u'УЕТ'         ], CReportBase.AlignRight ),
                          ('7%', [ u'',         u'руб'         ], CReportBase.AlignRight ),
                          ('7%', [ u'Оплачено', u'кол-во'      ], CReportBase.AlignRight ),
                          ('7%', [ u'',         u'УЕТ'         ], CReportBase.AlignRight ),
                          ('7%', [ u'',         u'руб'         ], CReportBase.AlignRight ),
                          ('7%', [ u'Отказано', u'кол-во'      ], CReportBase.AlignRight ),
                          ('7%', [ u'',         u'УЕТ'         ], CReportBase.AlignRight ),
                          ('7%', [ u'',         u'руб'         ], CReportBase.AlignRight ),
                       ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 8, 1, 3)

        locale = QtCore.QLocale()
        reportPrefs = {
            'detailServiceTypes': detailServiceTypes,
            'reportRowSize': reportRowSize,
            'detailInsurer': detailInsurer
        }
        self.printAll(table, reportData, '', locale, reportPrefs)

        return doc

    def printAll(self, table, reportData, indent, locale, prefs):
        totalByReport = self.printServiceTypes(table, reportData, indent, locale, prefs)
        self.addTotal(table, u'Всего', totalByReport, locale)

    def printInsurer(self, table, reportData, indent, locale, prefs, serviceType):
        insurerTotalText = indent + u'всего по СМО'
        total = [0] * prefs['reportRowSize']
        addIndent = '    ' if prefs['detailServiceTypes'] else ''
        insurers = []
        for key in reportData.keys():
            if key[0] == serviceType:
                insurers.append(key[1])
        insurers.sort()
        for insurerId in insurers:
            totalByInsurer = 0
            if prefs['detailInsurer']:
                self.addHeader(table, 0, 10, indent + u'СМО: ' + getOrganisationShortName(insurerId))
            totalByInsurer = self.printServices(table, reportData[(serviceType, insurerId)], indent + addIndent, locale, prefs)
            for j in xrange(prefs['reportRowSize']):
                total[j] += totalByInsurer[j]
            if prefs['detailInsurer']:
                self.addTotal(table, insurerTotalText, totalByInsurer, locale)
        return total

    def printServiceTypes(self, table, reportData, indent, locale, prefs):
        serviceTypeTotalText = indent + u'всего по виду услуги'
        total = [0] * prefs['reportRowSize']
        addIndent = '    ' if prefs['detailServiceTypes'] else ''
        #serviceTypes = reportData.keys()
        serviceTypes = list(set([key[0] for key in reportData.keys()]))
        serviceTypes.sort()
        for serviceType in serviceTypes:
            if prefs['detailServiceTypes']:
                self.addHeader(table, 0, 10, indent + u'Вид услуги: ' + docServiceTypeName[serviceType])
            totalByServiceType = self.printInsurer(table, reportData, indent + addIndent, locale, prefs, serviceType)
            for j in xrange(prefs['reportRowSize']):
                total[j] += totalByServiceType[j]
            if prefs['detailServiceTypes']:
                self.addTotal(table, serviceTypeTotalText, totalByServiceType, locale)
        return total

    def printServices(self, table, reportData, indent, locale, prefs):
        total = [0] * prefs['reportRowSize']
        services = reportData.keys()
        services.sort()
        for serviceKey in services:
            serviceName, serviceCode = serviceKey
            reportLine = reportData[serviceKey]
            for j in xrange(prefs['reportRowSize']):
                total[j] += reportLine[j]
            self.addLine(table, indent + serviceName, serviceCode, reportLine, locale)
        return total

    def addHeader(self, table, mergeFrom, mergeNum, title, code=None):
        i = table.addRow()
        table.mergeCells(i, mergeFrom, 1, mergeNum)
        table.setText(i, 0, title, CReportBase.TableHeader)
        if code is not None:
            table.setText(i, 1, code, CReportBase.TableHeader)

    def addLine(self, table, title, code, reportLine, locale):
        i = table.addRow()
        table.setText(i, 0, title)
        if code is None:
            table.mergeCells(i, 0, 1, 2)
        else:
            table.setText(i, 1, code)
        for j in xrange(0, len(reportLine), 3):
            table.setText(i, j+2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(1, len(reportLine), 3):
            table.setText(i, j+2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(2, len(reportLine), 3):
            table.setText(i, j+2, self.formatDouble(float(reportLine[j]), locale))

    def addTotal(self, table, title, reportLine, locale):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(0, len(reportLine), 3):
            table.setText(i, j+2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(1, len(reportLine), 3):
            table.setText(i, j+2, self.formatDouble(float(reportLine[j]), locale))
        for j in xrange(2, len(reportLine), 3):
            table.setText(i, j+2, self.formatDouble(float(reportLine[j]), locale))

    def formatDouble(self, value, locale):
        if QtGui.qApp.region() == '23':
            return u'{0:.2f}'.format(value)
        else:
            return locale.toString(value, 'f', 2)

class CFinanceSummaryByServicesEx(CFinanceSummaryByServices):
    def exec_(self, accountIdList=None):
        self.accountIdList = accountIdList
        CFinanceSummaryByServices.exec_(self)


    def getSetupDialog(self, parent):
        result = CFinanceSummarySetupDialog(parent)
        result.setTitle(self.title())
        result.setVisibleFinance(True)
        result.setVisibleDescendants(True)
        result.setVisibleInsurerList(True)
        result.setVisibleByOrgStructAction(True)
        return result


    def build(self, params):
        params['accountIdList'] = self.accountIdList
        return CFinanceSummaryByServices.build(self, '\n'.join(self.getDescription(params)), params)

