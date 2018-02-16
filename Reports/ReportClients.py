# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils               import getActionTypeDescendants

from library.Utils              import forceDate, forceInt, forceString, calcAge, formatName, formatSNILS
from library.database           import addDateInRange

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog
from Reports.StatReport1NPUtil  import havePermanentAttach


def selectData(begDate, endDate, eventTypeId, sex, ageFrom, ageTo, actionTypeClass, actionTypeId, onlyPermanentAttach, MKBFilter, MKBFrom, MKBTo, onlyPayedEvents, begPayDate, endPayDate):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableActionType = db.table('ActionType')
    cond = []
    if begDate:
        cond.append(db.joinOr([
            tableEvent['execDate'].ge(begDate), tableEvent['execDate'].isNull()]))
    if endDate:
        cond.append(tableEvent['setDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.execDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.execDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if actionTypeId:
        cond.append(tableActionType['id'].inlist(getActionTypeDescendants(actionTypeId, actionTypeClass)))
    elif actionTypeClass is not None:
        cond.append(tableActionType['class'].eq(actionTypeClass))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if MKBFilter:
        tableDiagnostic = db.table('Diagnostic')
        tableDiagnosis = db.table('Diagnosis')
        subQueryTable = tableDiagnosis.leftJoin(tableDiagnostic, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
        subCond = [ tableDiagnostic['event_id'].eq(tableEvent['id']),
                    tableDiagnosis['MKB'].between(MKBFrom, MKBTo)
                  ]
        cond.append(db.existsStmt(subQueryTable, subCond))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    condStr = db.joinAnd(cond)
    stmt = """
SELECT
    Client.lastName, Client.firstName, Client.patrName,
    Client.birthDate, Client.sex,
    formatClientAddress(ClientAddress.id) AS address,
    ClientPolicy.serial AS policySerial, ClientPolicy.number AS policyNumber,
    ClientDocument.serial AS documentSerial, ClientDocument.number AS documentNumber,
    Client.SNILS,
    Event.setDate AS date,
    Action.office, Action.note,
    Action.actionType_id,
    ActionType.name AS actionTypeName
FROM
    Action
    INNER JOIN Event ON Action.event_id=Event.id
    INNER JOIN Client ON Client.id=Event.client_id
    INNER JOIN ActionType on ActionType.id=Action.actionType_id
    LEFT JOIN ClientAddress ON
        ClientAddress.client_id = Client.id AND
        ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA WHERE CA.Type=0 AND CA.client_id = Client.id)
    LEFT JOIN ClientPolicy  ON
        ClientPolicy.client_id = Client.id AND
        ClientPolicy.id = (SELECT MAX(CP.id) FROM ClientPolicy AS CP WHERE  CP.client_id = Client.id)
    LEFT JOIN ClientDocument ON
        ClientDocument.client_id = Client.id AND
        ClientDocument.id = (
            SELECT MAX(CD.id)
            FROM
                ClientDocument AS CD
                LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
            WHERE rbDTG.code = '1' AND CD.client_id = Client.id)
    LEFT  JOIN Account_Item      ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                    )
WHERE Action.deleted=0 AND Event.deleted=0 AND %s
order BY ActionType.class, ActionType.group_id, ActionType.name, ActionType.id, Client.lastName, Client.firstName, Client.patrName
    """ % (condStr)
    return db.query(stmt)

class CReportClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Список обслуженных пацентов')

    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setPayPeriodVisible(True)
        result.setWorkOrganisationVisible(True)
        result.setSexVisible(True)
        result.setAgeVisible(True)
        result.setActionTypeVisible(True)
        result.setMKBFilterVisible(True)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        actionTypeClass = params.get('actionTypeClass', None)
        actionTypeId = params.get('actionTypeId', None)
        onlyPermanentAttach = params.get('onlyPermanentAttach', None)
        MKBFilter = params.get('MKBFilter', 0)
        MKBFrom   = params.get('MKBFrom', '')
        MKBTo     = params.get('MKBTo', '')
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())

        db = QtGui.qApp.db

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '5%', [u'№ п/п'], CReportBase.AlignRight),
            ('15%', [u'ФИО'], CReportBase.AlignLeft),
            ( '5%', [u'д/р'], CReportBase.AlignLeft),
            ( '5%', [u'возраст'], CReportBase.AlignLeft),
            ('25%', [u'Адрес'],CReportBase.AlignLeft),
            ( '7%', [ u'Полис'], CReportBase.AlignCenter),
            ( '9%', [ u'паспорт'], CReportBase.AlignCenter),
            ('10%', [ u'СНИЛС' ], CReportBase.AlignLeft ),
            ( '5%', [u'кабинет'],CReportBase.AlignLeft),
            ('15%', [u'примечение'],CReportBase.AlignLeft),
        ]

        table = createTable(cursor, tableColumns)

        query = selectData(begDate, endDate, eventTypeId, sex, ageFrom, ageTo, actionTypeClass, actionTypeId, onlyPermanentAttach, MKBFilter, MKBFrom, MKBTo, onlyPayedEvents, begPayDate, endPayDate)

        num = 0
        prevActionTypeId = None
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            fio = formatName(record.value('lastName'), record.value('firstName'), record.value('patrName'))
            birthDate = forceDate(record.value('birthDate'))
            date = forceDate(record.value('date'))
            age = calcAge(birthDate, date)
            address = forceString(record.value('address'))
            policy = ' '.join([forceString(record.value('policySerial')), forceString(record.value('policyNumber'))])
            document= ' '.join([forceString(record.value('documentSerial')), forceString(record.value('documentNumber'))])
            SNILS = formatSNILS(record.value('SNILS'))
            office = forceString(record.value('office'))
            note = forceString(record.value('note'))
            row = [fio, birthDate.toString('dd.MM.yyyy'), age, address, policy, document, SNILS, office, note]
            actionTypeId = forceInt(record.value('actionType_id'))
            actionTypeName = forceString(record.value('actionTypeName'))
            if actionTypeId!=prevActionTypeId:
                num = 0
                i = table.addRow()
                prevActionTypeId=actionTypeId
                table.mergeCells(i, 0, 1, 10)
                table.setText(i, 0, actionTypeName, CReportBase.ReportSubTitle, CReportBase.AlignLeft)
            i = table.addRow()
            num+=1
            table.setText(i, 0, num)
            for j, val in enumerate(row):
                table.setText(i, j+1, val)
        return doc