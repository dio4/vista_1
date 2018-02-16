# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.FinanceSummaryByDoctors import getCond, CFinanceSummarySetupDialog
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDouble, forceInt, forceRef, forceString, formatName


def selectDataByEvents(params):
    stmt="""
SELECT
    Account_Item.refuseType_id AS refuseType_id,
    rbPayRefuseType.code     AS refuseTypeCode,
    rbPayRefuseType.name     AS refuseTypeName,
    rbSpeciality.name        AS specialityName,
    Person.speciality_id     AS speciality_id,
    Event.execPerson_id      AS person_id,
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    COUNT(Account_Item.id)   AS itemCount,
    SUM(Account_Item.amount) AS amount,
    SUM(Account_Item.sum)    AS sum,
    SUM(Account_Item.uet)    AS uet
FROM Account_Item
LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN Event           ON Event.id = Account_Item.event_id
LEFT JOIN EventType       ON EventType.id = Event.eventType_id
LEFT JOIN Person          ON Person.id = Event.execPerson_id AND Person.retired = 0
LEFT JOIN rbSpeciality    ON rbSpeciality.id = Person.speciality_id
LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
WHERE
    Account_Item.date IS NOT NULL
    AND Account_Item.deleted = 0
    AND Account_Item.refuseType_id IS NOT NULL
    AND Account_Item.visit_id IS NULL
    AND Account_Item.action_id IS NULL
    AND %s
GROUP BY
    Account_Item.refuseType_id, Event.execPerson_id
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params))


def selectDataByVisits(params):
    stmt="""
SELECT
    Account_Item.refuseType_id AS refuseType_id,
    rbPayRefuseType.code     AS refuseTypeCode,
    rbPayRefuseType.name     AS refuseTypeName,
    rbSpeciality.name        AS specialityName,
    Person.speciality_id     AS speciality_id,
    Visit.person_id          AS person_id,
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    COUNT(Account_Item.id)   AS itemCount,
    SUM(Account_Item.amount) AS amount,
    SUM(Account_Item.sum)    AS sum,
    SUM(Account_Item.uet)    AS uet
FROM Account_Item
LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN Event           ON Event.id = Account_Item.event_id
LEFT JOIN EventType       ON EventType.id = Event.eventType_id
LEFT JOIN Visit           ON Visit.id = Account_Item.visit_id
LEFT JOIN Person          ON Person.id = Visit.person_id AND Person.retired = 0
LEFT JOIN rbSpeciality    ON rbSpeciality.id = Person.speciality_id
LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
WHERE
    Account_Item.date IS NOT NULL
    AND Account_Item.deleted = 0
    AND Account_Item.refuseType_id IS NOT NULL
    AND Account_Item.visit_id IS NOT NULL
    AND Account_Item.action_id IS NULL
    AND %s
GROUP BY
    Account_Item.refuseType_id, Visit.person_id
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 1))


def selectDataByActions(params):
    stmt="""
SELECT
    Account_Item.refuseType_id AS refuseType_id,
    rbPayRefuseType.code     AS refuseTypeCode,
    rbPayRefuseType.name     AS refuseTypeName,
    rbSpeciality.name        AS specialityName,
    Person.speciality_id     AS speciality_id,
    Action.person_id         AS person_id,
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    COUNT(Account_Item.id)   AS itemCount,
    SUM(Account_Item.amount) AS amount,
    SUM(Account_Item.sum)    AS sum,
    SUM(Account_Item.uet)    AS uet
FROM Account_Item
LEFT JOIN Account         ON Account.id = Account_Item.master_id AND Account.deleted = 0
LEFT JOIN Event           ON Event.id = Account_Item.event_id
LEFT JOIN EventType       ON EventType.id = Event.eventType_id
LEFT JOIN Action          ON Action.id = Account_Item.action_id
LEFT JOIN ActionType      ON ActionType.id = Action.actionType_id
LEFT JOIN rbService       ON rbService.id = Account_Item.service_id
LEFT JOIN Person          ON Person.id = Action.person_id AND Person.retired = 0
LEFT JOIN rbSpeciality    ON rbSpeciality.id = Person.speciality_id
LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
WHERE
    Account_Item.date IS NOT NULL
    AND Account_Item.deleted = 0
    AND Account_Item.refuseType_id IS NOT NULL
    AND Account_Item.visit_id IS NULL
    AND Account_Item.action_id IS NOT NULL
    AND %s
GROUP BY
    Account_Item.refuseType_id, Action.person_id
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 2))


class CFinanceSummaryByRejections(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Финансовая сводка по причинам отказа в оплате услуг')


    def build(self, description, params):
        reportRowSize = 4
        reportData = {}

        def processQuery(query):
            while query.next() :
                record = query.record()
                refuseTypeId = forceRef(record.value('refuseType_id'))
                refuseTypeCode = forceString(record.value('refuseTypeCode'))
                refuseTypeName = forceString(record.value('refuseTypeName'))
                personId = forceRef(record.value('person_id'))
                specialityName = forceString(record.value('specialityName'))
                specialityId = forceInt(record.value('speciality_id'))
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                code = forceString(record.value('code'))

                itemCount = forceInt(record.value('itemCount'))
                amount = forceDouble(record.value('amount'))
                uet = forceDouble(record.value('uet'))
                sum = forceDouble(record.value('sum'))
                name = formatName(lastName,  firstName, patrName)
                key = (specialityName if specialityName else u'Без указания специальности',
                       name if name else u'Без указания врача',
                       code,
#                       personId,
                       refuseTypeCode,
                       refuseTypeName,
#                       refuseTypeId
                       )

                reportLine = reportData.setdefault(key, [0]*reportRowSize)
                reportLine[0] += itemCount
                reportLine[1] += amount
                reportLine[2] += uet
                reportLine[3] += sum

        query = selectDataByEvents(params)
        processQuery(query)
        queryTextParts = [u'----------------select data by events----------------']
        queryTextParts.append(forceString(query.lastQuery()))
        
        query = selectDataByVisits(params)
        processQuery(query)
        queryTextParts.append(u'----------------select data by visits----------------')
        queryTextParts.append(forceString(query.lastQuery()))
        
        query = selectDataByActions(params)
        processQuery(query)
        queryTextParts.append(u'----------------select data by actions----------------')
        queryTextParts.append(forceString(query.lastQuery()))

        self.setQueryText('\n\n'.join(queryTextParts))
        
        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(description)
        cursor.insertBlock()

        tableColumns = [
                          ('25%', [ u'Врач',           u'ФИО'],          CReportBase.AlignLeft ),
                          ('5%',  [ u'',               u'код'],          CReportBase.AlignLeft ),
                          ('5%',  [ u'Причина отказа', u'код'],          CReportBase.AlignLeft ),
                          ('25%', [ u'',               u'наименование'], CReportBase.AlignLeft ),
                          ('10%', [ u'Позиций в счетах' ], CReportBase.AlignRight ),
                          ('10%', [ u'Количество'       ], CReportBase.AlignRight ),
                          ('10%', [ u'УЕТ'              ], CReportBase.AlignRight ),
                          ('10%', [ u'Сумма'            ], CReportBase.AlignRight ),
                       ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 1, 2)

        totalByReport = [0]*reportRowSize
        totalBySpeciality = [0]*reportRowSize
        prevSpecialityName = None
        locale = QtCore.QLocale()
        keys = reportData.keys()
        keys.sort()
        for key in keys:
            specialityName, doctorName, doctorCode, refuseTypeCode, refuseTypeName = key
            if prevSpecialityName != specialityName:
                if prevSpecialityName != None:
                    self.addTotal(table, u'всего по специальности', totalBySpeciality, locale)
                    totalBySpeciality = [0]*reportRowSize
                self.addSpecialityHeader(table, specialityName)
                prevSpecialityName = specialityName
            i = table.addRow()
            table.setText(i, 0, doctorName)
            table.setText(i, 1, doctorCode)
            table.setText(i, 2, refuseTypeCode)
            table.setText(i, 3, refuseTypeName)
            reportLine = reportData[key]
            table.setText(i, 4, reportLine[0])
            table.setText(i, 5, reportLine[1])
            table.setText(i, 6, locale.toString(float(reportLine[2]), 'f', 2))
            table.setText(i, 7, locale.toString(float(reportLine[3]), 'f', 2))
            for j in xrange(reportRowSize):
                totalBySpeciality[j] += reportLine[j]
                totalByReport[j] += reportLine[j]
        self.addTotal(table, u'всего по специальности', totalBySpeciality, locale)
        self.addTotal(table, u'Всего', totalByReport, locale)
        return doc


    def addSpecialityHeader(self, table, specialityName):
#        format = QtGui.QTextCharFormat()
        i = table.addRow()
        table.mergeCells(i, 0, 1, 8)
        table.setText(i, 0, specialityName, CReportBase.TableHeader)


    def addTotal(self, table, title, reportLine, locale):
        i = table.addRow()
        table.mergeCells(i, 0, 1, 4)
        table.setText(i, 0, title, CReportBase.TableTotal)
        table.setText(i, 4, reportLine[0])
        table.setText(i, 5, reportLine[1])
        table.setText(i, 6, locale.toString(float(reportLine[2]), 'f', 2))
        table.setText(i, 7, locale.toString(float(reportLine[3]), 'f', 2))


class CFinanceSummaryByRejectionsEx(CFinanceSummaryByRejections):
    def exec_(self, accountIdList=None):
        self.accountIdList = accountIdList
        CFinanceSummaryByRejections.exec_(self)


    def getSetupDialog(self, parent):
        result = CFinanceSummarySetupDialog(parent)
        result.setTitle(self.title())
        result.setVisibleByOrgStructAction(False)
        return result


    def build(self, params):
        params['accountIdList'] = self.accountIdList
        return CFinanceSummaryByRejections.build(self, '\n'.join(self.getDescription(params)), params)
