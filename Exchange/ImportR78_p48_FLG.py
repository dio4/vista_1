# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4.QtXml import QDomDocument
from Events.Action import CAction

from Exchange.Utils import *




class CImportR78_p48_FLG():
    def __init__(self, args):
        connectionInfo = {
                      'driverName' : 'MYSQL',
                      'host' : args['host'],
                      'port' : args['port'],
                      'database' : args['database'],
                      'user' : args['user'],
                      'password' : args['password'],
                      'connectionName' : 'IEMK',
                      'compressData' : True,
                      'afterConnectFunc' : None
                }
        self.db = database.connectDataBaseByInfo(connectionInfo)
        QtGui.qApp.db = self.db

        self.tableClient = self.db.table('Client')
        self.tableClientAddress = self.db.table('ClientAddress')
        self.tableEvent = self.db.table('Event')
        self.tableAction = self.db.table('Action')

        self.nProcessed = 0
        self.nUpdated = 0
        self.nAdded = 0

        # Допустимые коды - FLG, FLG47.
        accSystemCode = args['accSystem']
        self.accountingSystem = forceRef(self.db.translate('rbAccountingSystem', 'code', accSystemCode, 'id'))
        self.actionType = forceRef(self.db.translate('ActionType', 'code', u'А06.09.007.002*', 'id'))

        self._mapIDOtoIDI = {}      # соответствие внешних и локальных идентификаторов пациентов

    def readFile(self, device):
        """
            Обработка импортируемого файла
        """
        self.doc = QDomDocument()
        self.doc.setContent(device, False)
        root = self.doc.documentElement()
        if root.tagName() != u'doc':
            print 'Error: incorrect root element. Import aborted.'
            return -1

        clients = root.firstChildElement('demography')
        results = root.firstChildElement('results')

        if not (clients and results):
            print 'Incorrect xml structure. Import aborted'
            return -2

        self.processRegData(clients.childNodes())
        self.processResults(results.childNodes())


        return 0

    def processRegData(self, clients):
        for i in range(clients.length()):
            client = clients.at(i)
            localId = client.firstChildElement('ido').text()
            if not localId:
                externalId = client.firstChildElement('idi').text()
                record = self.db.getRecordEx('ClientIdentification', 'client_id',
                                    'identifier = \'%s\' AND accountingSystem_id = %s' % (externalId, self.accountingSystem))
                if record:
                    self._mapIDOtoIDI[externalId] = forceRef(record.value(0))
                    continue

                lastName = client.firstChildElement('lastname').text()
                firstName = client.firstChildElement('firstname').text()
                patrName = client.firstChildElement('midlname').text()
                sex = forceInt(client.firstChildElement('sex').text())
                birthDate = QDate.fromString(client.firstChildElement('dob').text(), Qt.ISODate)

                cond = [self.tableClient['lastName'].eq(lastName),
                        self.tableClient['firstName'].eq(firstName),
                        self.tableClient['patrName'].eq(patrName),
                        self.tableClient['sex'].eq(1 if sex == 0 else 2 if sex == 1 else 0),
                        self.tableClient['birthDate'].eq(birthDate)]

                record = self.db.getRecordEx(self.tableClient, 'id', cond)
                if record:
                    self._mapIDOtoIDI[externalId] = forceRef(record.value(0))
                    continue

                record = self.tableClient.newRecord()
                record.setValue('lastName', toVariant(lastName))
                record.setValue('firstName', toVariant(firstName))
                record.setValue('patrName', toVariant(patrName))
                record.setValue('sex', toVariant(1 if sex == 0 else 2 if sex == 1 else 0))
                record.setValue('birthDate', toVariant(birthDate))

                address = client.firstChildElement('address')
                if address:
                    city = address.firstChildElement('sity').text()
                    street = address.firstChildElement('street').text()
                    streetSocr = address.firstChildElement('streetSokr').text()
                    number = address.firstChildElement('house').text()
                    corpus = address.firstChildElement('corpus').text()
                    flat = address.firstChildElement('flat').text()

                    freeInput = u''
                    if city:
                        freeInput = city
                    if street:
                        if freeInput:
                            freeInput += u', '
                        freeInput += street
                        if streetSocr:
                            freeInput += ' ' + streetSocr
                    if number:
                        if freeInput:
                            freeInput += u', '
                        freeInput += u'Д. ' + number
                    if corpus:
                        if freeInput:
                            freeInput += u', '
                        freeInput += u'К. ' + corpus
                    if flat:
                        if freeInput:
                            freeInput += u', '
                        freeInput += u'КВ. ' + flat

                    addrRecord = self.tableClientAddress.newRecord()
                    addrRecord.setValue('freeInput', toVariant(freeInput))
                    addrRecord.setValue('type', toVariant(0))

                    self.db.transaction()
                    try:
                        clientId = self.db.insertRecord(self.tableClient, record)
                        addrRecord.setValue('client_id', toVariant(clientId))
                        self.db.insertRecord(self.tableClientAddress, addrRecord)
                        self.db.commit()
                    except:
                        self.db.rollback()
                        raise
                else:
                    clientId = self.db.insertRecord(self.tableClient, record)

                self._mapIDOtoIDI[externalId] = forceRef(clientId)

    def processResults(self, results):
        defaultEventTypeId = forceRef(self.db.translate('EventType', 'code', '001', 'id'))
        tableJobTicket = self.db.table('Job_Ticket').alias('jt')
        tableAction = self.db.table('Action').alias('a')
        currentDate = QDate.currentDate()
        for i in range(results.length()):
            result = results.at(i)
            localId = result.firstChildElement('ido').text()
            externalId = result.firstChildElement('idi').text()
            tests = result.firstChildElement('tests')
            if not tests:
                continue

            test = tests.firstChildElement('test')
            if not test:
                continue
            dateString = test.firstChildElement('date').text()
            date = QDate.fromString(dateString, Qt.ISODate)
            value = test.firstChildElement('value').text()
            status = test.firstChildElement('status').text()
            comment = test.firstChildElement('comment').text()
            if localId:
                stmt = u'''SELECT
                  a.id as actionId, Event.id as eventId
                FROM Job_Ticket jt
                  INNER JOIN Job j
                    ON j.id = jt.master_id AND jt.status = 0
                  INNER JOIN rbJobType jt1 ON jt1.code = '4-4' AND jt1.id= j.jobType_id
                  INNER JOIN ActionProperty_Job_Ticket apjt
                    ON apjt.value = jt.id
                  INNER JOIN ActionProperty ap ON ap.id = apjt.id
                  INNER JOIN Action a ON a.id = ap.action_id AND a.deleted = 0
                  INNER JOIN Event ON Event.id = a.event_id AND Event.deleted = 0
                  INNER JOIN Client c ON c.id = Event.client_id AND c.deleted = 0
                WHERE %s'''
                cond = [self.tableEvent['client_id'].eq(forceRef(localId)),
                        tableJobTicket['datetime'].dateEq(date),
                        tableAction['actionType_id'].eq(self.actionType)]
                query = self.db.query(stmt % self.db.joinAnd(cond))
                if not query.first():
                    continue
                record = query.record()
                eventId = forceRef(record.value('eventId'))
                action = CAction.getAction(eventId, u'А06.09.007.002*')
                actionRecord = action.getRecord()
                endDate = forceDate(actionRecord.value('endDate'))
                if not endDate:
                    actionRecord.setValue('endDate', toVariant(currentDate))
                actionRecord.setValue('status', toVariant(2 if status == 1 else 3 if status == 2 else 0))
                action[u'Результат'] = externalId + u' ' + value
                action[u'Описание'] = comment
                action.setRecord(actionRecord)
                action.save()



            elif defaultEventTypeId:
                localId = self._mapIDOtoIDI.get(externalId, None)
                if localId is None:
                    print 'Error: found test result without information about client. Skipping.'
                    continue

                self.db.transaction()
                try:
                    eventRecord = self.tableEvent.newRecord()
                    eventRecord.setValue('eventType_id', toVariant(defaultEventTypeId))
                    eventRecord.setValue('client_id', toVariant(localId))
                    eventRecord.setValue('setDate', toVariant(date))
                    eventRecord.setValue('isPrimary', toVariant(1))
                    eventRecord.setValue('order', toVariant(1))
                    eventId = self.db.insertRecord('Event', eventRecord)

                    action = CAction.createByTypeId(self.actionType)
                    actionRecord = action.getRecord()
                    if not actionRecord:
                        actionRecord = self.tableAction.newRecord()
                        actionRecord.setValue('actionType_id', toVariant(self.actionType))
                    actionRecord.setValue('status', toVariant(2 if status == 1 else 3 if status == 2 else 0))
                    actionRecord.setValue('begDate', toVariant(date))
                    actionRecord.setValue('endDate', toVariant(currentDate))
                    action[u'Результат'] = externalId + ' ' + value
                    action[u'Описание'] = comment
                    action.setRecord(actionRecord)
                    action.save(eventId)
                    self.db.commit()
                except:
                    self.db.rollback()
                    raise

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Import IEMC or Reg Data to to specified database.')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-f', dest='fileName')
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-c', dest='accSystem', default='FLG')
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)
    if not args['fileName']:
        print 'Error: you should specify file name'
        sys.exit(-3)

    app = QtCore.QCoreApplication(sys.argv)
    dlg = CImportR78_p48_FLG(args)

    inFile = QtCore.QFile(args['fileName'])
    if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        print u'Couldnt open file for reading %s:\n%s.' % (args['fileName'], inFile.errorString())
        return

    dlg.readFile(inFile)

if __name__ == '__main__':
    main()