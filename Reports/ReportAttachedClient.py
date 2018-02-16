# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.Ui_ReportAttachedClientSetup import Ui_ReportAttachedClientSetup
from library.Utils import forceString
from Reports.ReportBase import createTable, CReportBase

def selectData(params):
    stmt = u'''
SELECT DISTINCT
    Client.id AS clientId,
    Client.lastName,
    Client.firstName,
    Client.patrName,
    Event.id AS eventId,
    Event.eventType_id,
    EventType.name AS eventName
FROM
    Client
    LEFT JOIN ClientAttach ON Client.id = ClientAttach.client_id
    LEFT JOIN Event ON Client.id = Event.client_id
    LEFT JOIN Person ON Event.execPerson_id = Person.id
    LEFT JOIN EventType ON Event.eventType_id = EventType.id
WHERE
    %s
ORDER BY
    clientId
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = params.get('orgStructureId', None)
    permanentAttach = params.get('PermanentAttach', None)

    tableClient = db.table('Client')
    tableClientAttach = db.table('ClientAttach')
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')

    cond = []
    cond.append(tableClient['createDatetime'].dateGe(begDate))
    cond.append(tableClient['createDatetime'].dateLe(endDate))
    cond.append(tableClientAttach['LPU_id'].eq(permanentAttach))

    cond.append(db.joinOr([
        db.joinAnd([
            tableEvent['deleted'].eq(0),
            tableEvent['eventType_id'].eq(eventTypeId) if eventTypeId else tableEvent['eventType_id'].isNotNull(),
            db.joinOr([
                tablePerson['orgStructure_id'].eq(orgStructureId),
                tablePerson['orgStructure_id'].inInnerStmt(
                    "(SELECT id FROM OrgStructure_Ancestors WHERE fullPath LIKE '%" + (str(orgStructureId) if orgStructureId else '') + "%')"
                )
            ])
        ]),
        tableEvent['client_id'].isNull()
    ]))

    return db.query(stmt % db.joinAnd(cond))


class CReportAttachedClientSetupDialog(QtGui.QDialog, Ui_ReportAttachedClientSetup):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate().currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbOrganisationAttachment.setValue(params.get('PermanentAttach', QtGui.qApp.currentOrgId()))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['PermanentAttach'] = self.cmbOrganisationAttachment.value()
        return result


class CReportAttachedClient(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Обслуженный контингент")

    def getSetupDialog(self, parent):
        result = CReportAttachedClientSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('10%', [u'Код'],           CReportBase.AlignLeft),
            ('45%', [u'Пациент'],       CReportBase.AlignLeft),
            ('45%', [u'Тип обращения'], CReportBase.AlignLeft),
        ]

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        totalAssigned = 0
        totalClients = 0
        totalNotAssigned = 0
        prevClientId = None
        prevClientName = None
        rowNumber = 1

        # Далее происходит следующее:
        # мы группируем кортежи (id пациента, ФИО пациента, наименование обращения) по id пациента.
        # Учитывая, что тип обращения задается в диалоговом окне ранее, во всех _разумных_ случаях
        # каждая группа будет состоять из одного элемента. Но что, если он не задан?

        while query.next():
            record = query.record()
            clientId = record.value('clientId')
            eventTypeExists = not record.isNull('eventType_id')
            if eventTypeExists:
                if prevClientId != clientId:
                    if prevClientId is not None:
                        table.mergeCells(clientRowStart, 0, rowNumber - clientRowStart, 1)
                        table.mergeCells(clientRowStart, 1, rowNumber - clientRowStart, 1)
                        table.setText(clientRowStart, 0, forceString(prevClientId))
                        table.setText(clientRowStart, 1, prevClientName)

                    totalClients += 1
                    clientRowStart = rowNumber

                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                clientName = u' '.join([lastName, firstName, patrName])

                prevClientId = clientId
                prevClientName = clientName

                eventName = forceString(record.value('eventName'))
                i = table.addRow()
                table.setText(i, 2, forceString(eventName))
                totalAssigned += 1

                rowNumber += 1
            else:
                totalNotAssigned += 1

        if prevClientId is not None:
            table.mergeCells(clientRowStart, 0, rowNumber - clientRowStart, 1)
            table.mergeCells(clientRowStart, 1, rowNumber - clientRowStart, 1)
            table.setText(clientRowStart, 0, forceString(prevClientId))
            table.setText(clientRowStart, 1, prevClientName)

        i = table.addRow()
        table.setText(i, 0, u'Всего', CReportBase.TableTotal)
        table.setText(i, 1, u'Пациентов: ' + forceString(totalClients), CReportBase.TableTotal)
        table.setText(i, 2, u'Обращений: ' + forceString(totalAssigned), CReportBase.TableTotal)

        i = table.addRow()
        table.mergeCells(i, 0, 1, 2)
        table.setText(i, 0, u'Всего пациентов без обращений', CReportBase.TableTotal)
        table.setText(i, 2, totalNotAssigned, CReportBase.TableTotal)
        return doc

