# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.Utils              import forceDate, forceInt, forceString, getVal, formatSex
from Registry.Utils             import formatAddress, getClientAddress, getClientDocument, getClientInfo, \
                                       getClientPolicy
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase


def selectData(
    begDate, endDate, eventTypeId, onlyPayedEvents, begPayDate, endPayDate, workOrgId, onlyPermanentAttach):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    if begDate:
        cond.append(db.joinOr([
            tableEvent['execDate'].ge(begDate), tableEvent['execDate'].isNull()]))
    if endDate:
        cond.append(tableEvent['setDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    if workOrgId:
        cond.append('ClientWork.org_id=%d' % (workOrgId))
    if onlyPermanentAttach:
        my_org_id=forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'orgId', None))
        cond.append('EXISTS (SELECT * FROM ClientAttach WHERE ClientAttach.client_id=Client.id and ClientAttach.attachType_id=2 and ClientAttach.LPU_id=%d)' % my_org_id)
    condStr = db.joinAnd(cond)
    stmt = """
SELECT
    Client.id as clientId, Event.id as eventId, EventType.name AS eventTypeName, Event.execDate, Diagnostic.healthGroup_id, Diagnosis.MKB
FROM
    Event
    LEFT JOIN EventType ON EventType.id = Event.eventType_id
    LEFT JOIN Client ON Client.id=Event.client_id
    LEFT JOIN Diagnostic ON Diagnostic.event_id=Event.id AND Diagnostic.diagnosisType_id=1
    LEFT JOIN Diagnosis ON Diagnosis.id=getEventDiagnosis(Event.id)
    LEFT JOIN ClientWork ON
        ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id=Client.id)
    LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                              )

WHERE Event.deleted = 0 AND Diagnostic.deleted = 0 AND Diagnosis.deleted = 0 AND %s
ORDER BY Client.lastName, Client.firstName, Client.patrName
    """ % (condStr)
    return db.query(stmt)


class CStatReportF131ByDD(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(True)
        self.setTitle(u'Список пациентов, прошедших ДД', u'Сводка по Ф.131')


    def getSetupDialog(self, parent):
        result = CReport.getSetupDialog(self, parent)
        result.setWorkOrganisationVisible(True)
        return result


    def build(self, params):
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId = getVal(params, 'eventTypeId', None)
        onlyPayedEvents = getVal(params, 'onlyPayedEvents', False)
        begPayDate = getVal(params, 'begPayDate', QtCore.QDate())
        endPayDate = getVal(params, 'endPayDate', QtCore.QDate())
        workOrgId = getVal(params, 'workOrgId', None)
        onlyPermanentAttach = getVal(params, 'onlyPermanentAttach', None)

        db = QtGui.qApp.db

        reportData = []

        query = selectData(
            begDate, endDate, eventTypeId, onlyPayedEvents, begPayDate, endPayDate, workOrgId, onlyPermanentAttach)

        while query.next() :
            record = query.record()
            clientId = forceInt(record.value('clientId'))
            Client=getClientInfo(clientId)
            lastName = Client['lastName']
            firstName = Client['firstName']
            patrName = Client['patrName']
            sex = formatSex(Client['sexCode'])
            birthDate = Client['birthDate'].toString('dd.MM.yyyy')
            policy = ''
            policyRecord = getClientPolicy(clientId)
            if policyRecord:
                serial=forceString(policyRecord.value('serial'))
                number=forceString(policyRecord.value('number'))
                policy = serial+' '+number
            document = ''
            documentRecord = getClientDocument(clientId)
            if documentRecord:
                documentType_id=forceInt(documentRecord.value('documentType_id'))
                documentTypeTable = db.table('rbDocumentType')
                documentTypeRecord = db.getRecord(documentTypeTable, 'name', documentType_id)
                if documentTypeRecord:
                    document = forceString(documentTypeRecord.value(0)) + ' '
                serial=forceString(documentRecord.value('serial'))
                number=forceString(documentRecord.value('number'))
                document += (serial+' '+number)
            address = ''
            ClientAddress=getClientAddress(clientId, 0)
            if ClientAddress:
                address_id=ClientAddress.value('address_id')
                address = formatAddress(address_id)
            eventTypeName = forceString(record.value('eventTypeName'))
            execDate = forceDate(record.value('execDate')).toString('dd.MM.yyyy')
            healthGroup = forceInt(record.value('healthGroup_id'))
            MKB = forceString(record.value('MKB'))
            reportData.append([
                clientId, lastName, firstName, patrName, sex, birthDate,
                policy, document, address, eventTypeName, execDate, healthGroup, MKB])


        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '6%', [u'№ п/п'], CReportBase.AlignLeft),
            ( '6%', [u'идентификатор клиента'], CReportBase.AlignLeft),
            ( '10%', [u'Фамилия'], CReportBase.AlignLeft),
            ( '10%', [u'Имя'], CReportBase.AlignLeft),
            ( '10%', [u'Отчество'], CReportBase.AlignLeft),
            ( '2%', [u'Пол'], CReportBase.AlignLeft),
            ( '8%', [u'д/рождения'], CReportBase.AlignLeft),
            ( '8%', [u'Полис'], CReportBase.AlignLeft),
            ( '18%', [u'документ'], CReportBase.AlignLeft),
            ( '50%', [u'Адрес'], CReportBase.AlignLeft),
            ( '15%', [u'Тип события'], CReportBase.AlignLeft),
            ( '8%', [u'дата окончания'], CReportBase.AlignLeft),
            ( '2%', [u'группа'], CReportBase.AlignLeft),
            ( '4%', [u'Закл.МКБ'], CReportBase.AlignLeft),
        ]

        table = createTable(cursor, tableColumns)

        for row in reportData:
            i = table.addRow()
            table.setText(i, 0, i)
            for j in xrange(len(row)):
                table.setText(i, j+1, row[j])
        return doc
