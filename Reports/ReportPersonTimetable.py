# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceBool, forceDate, forceString, forceTime

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportPersonTimetable import Ui_ReportPersonTimetable


def selectData(date, personId, specialityId, locationCardTypeId):
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableEventType = db.table('EventType')
    tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableLocationCardType = db.table('rbLocationCardType')

    cond = [tableEventType['code'].eq('queue')]

    if personId:
        cond.append(tablePersonWithSpeciality['id'].eq(personId))
    if specialityId:
        cond.append(tablePersonWithSpeciality['speciality_id'].eq(specialityId))
    if locationCardTypeId:
        cond.append(tableLocationCardType['id'].eq(locationCardTypeId))

    cond.append(tableAction['directionDate'].dateEq(date))

    stmt = u'''SELECT vrbPersonWithSpeciality.name as person,
                      Time(Action.directionDate) as directionTime,
                      Client.id as clientId,
                      Client.lastName,
                      Client.firstName,
                      Client.patrName,
                      Client.birthDate,
                      age(Client.birthDate, directionDate) as clientAge,
                      getClientContacts(Client.id) as contacts
                    , concat(cpDMS.`serial`, ' ', cpDMS.number, ' ', orgDMS.shortName) AS policyDMS
                    , cpDMS.endDate AS endDatePolicyDMS,
                      Action.note
                FROM
                      EventType
                      inner join Event on Event.eventType_id = EventType.id and Event.deleted = 0
                      inner join Action on Action.event_id = Event.id and Action.deleted = 0
                      inner join ActionProperty_Action on ActionProperty_Action.value = Action.id
                      inner join Client on Event.client_id=Client.id
                      inner join vrbPersonWithSpeciality on Action.person_id=vrbPersonWithSpeciality.id
                      left join Client_LocationCard
                        on Client_LocationCard.master_id = Client.id
                        and Client_LocationCard.deleted = 0
                      left join rbLocationCardType on rbLocationCardType.id = Client_LocationCard.locationCardType_id
                      LEFT JOIN ClientPolicy cpDMS ON cpDMS.client_id = Client.id AND cpDMS.id = ( SELECT max(CP.id)
                                                                                                    FROM
                                                                                                      ClientPolicy AS CP
                                                                                                    LEFT JOIN rbPolicyType
                                                                                                    ON rbPolicyType.id = CP.policyType_id
                                                                                                    WHERE
                                                                                                      rbPolicyType.name LIKE 'ДМС%%'
                                                                                                      AND CP.client_id = Client.id
                                                                                                      AND CP.deleted = 0)
                      LEFT JOIN Organisation orgDMS ON orgDMS.id = cpDMS.insurer_id
                WHERE
                      %s
                ORDER BY
                      vrbPersonWithSpeciality.name, Time(Action.directionDate)''' % (db.joinAnd(cond))
    return db.query(stmt)

class CReportPersonTimetable(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Список пациентов по всем врачам за день')


    def getSetupDialog(self, parent):
        result = CPersonTimetable(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        date = params.get('begDate', QtCore.QDate())
        personId = params.get('personId', None)
        specialityId = params.get('specialityId', None)
        locationCardTypeId = params.get('locationCardTypeId', None)
        query = selectData(date, personId, specialityId, locationCardTypeId)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.TableTotal)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '2%',[u'№'], CReportBase.AlignLeft),
            ( '5%', [u'Время'], CReportBase.AlignRight),
            ( '75%', [u'Пациент'], CReportBase.AlignLeft),
            ( '8%', [u'Номер амб.карты'], CReportBase.AlignLeft),
            ( '25%', [u'Примечания/Жалобы'], CReportBase.AlignLeft)
            ]

        table = createTable(cursor, tableColumns)

        currentPerson = None

        while query.next():
            record = query.record()
            person = forceString(record.value('person'))
            directionTime = forceTime(record.value('directionTime'))
            client = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
            birthDate = forceDate(record.value('birthDate'))
            ageClient = forceString(record.value('clientAge'))
            policyDMS = forceString(record.value('policyDMS')) + u' по ' + forceString(forceDate(record.value('endDatePolicyDMS')).toString('dd.MM.yyyy')) if forceString(record.value('policyDMS')) else ''
            contacts = forceString(record.value('contacts'))
            note = forceString(record.value('note'))
            clientId = forceString(record.value('clientId'))

            clientInfo = [u'пациент: ' + client + u' Д.р. (возраст): ' + forceString(birthDate.toString('dd.MM.yyyy')) + ' (' + ageClient + ')']
            if forceBool(policyDMS):
                clientInfo.append(u'ДМС: №' + policyDMS)
            if forceBool(contacts):
                clientInfo.append(contacts)

            if not currentPerson or currentPerson != person:
                count = 0
                i = table.addRow()
                table.setText(i, 0, person, CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 4)
                currentPerson = person
            count += 1
            i = table.addRow()
            table.setText(i, 0, count)
            table.setText(i, 1, directionTime.toString('hh:mm'))
            table.setText(i, 2, '\n'.join(clientInfo))
            table.setText(i, 3, clientId)
            table.setText(i, 4, note)
        return doc

class CPersonTimetable(QtGui.QDialog, Ui_ReportPersonTimetable):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbLocationCardType.setTable('rbLocationCardType', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate()))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbLocationCardType.setValue(params.get('locationCardTypeId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['personId'] = self.cmbPerson.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['locationCardTypeId'] = self.cmbLocationCardType.value()
        return result





