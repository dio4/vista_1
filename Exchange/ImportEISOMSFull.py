#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Events.Utils import getAvailableCharacterIdByMKB
from Cimport import CDBFimport
from Utils import *
from Ui_ImportEISOMSFull import Ui_ImportEISOMSFull

#TODO: Оптимизировать добавление врача/специальности в Event, Diagnosis, DiagnosisType - вынести поиск и проверку в родительскую функцию.

def ImportEISOMSFull(widget):
    dlg = CImportEISOMSFull()
    dlg.exec_()


class CImportEISOMSFull(QtGui.QDialog, Ui_ImportEISOMSFull, CDBFimport):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        CDBFimport.__init__(self)
        self.setupUi(self)
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.createdClients = 0
        self.createdEvents = 0
        self.createdVisits = 0
        self.createdDiagnosises = 0
        self.createdDiagnostics = 0
        self.btnImport.setEnabled(self.edtFileName.text()!='')
        self.tblEventType = tbl('EventType')
        self.tblEvent = tbl('Event')
        self.tblContract = tbl('Contract')
        self.tblContractSpec = tbl('Contract_Specification')
        self.tblDiagnosis = tbl('Diagnosis')
        self.tblDiagnostic = tbl('Diagnostic')
        self.tableClient = tbl('Client')
        self.tblClientDocument = tbl('ClientDocument')
        self.tblClientPolicy = tbl('ClientPolicy')
        self.tblClientAddress = tbl('ClientAddress')
        self.tblRbService = tbl('rbService')
        self.tblRbResult = tbl('rbResult')
        self.tblRbDiagnosticResult = tbl('rbDiagnosticResult')
        self.tblPerson = tbl('Person')
        self.tblVisit = tbl('Visit')
        self.tblRbSpeciality = tbl('rbSpeciality')

#        self.serviceCache = {}
#        self.accountItemIdListCache = {}
        self.clientCache = {}
        self.eventsCache = {}
#        self.clientByAccountItemIdCache = {}
#        self.refuseTypeIdCache = {}

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)


    def err2log(self, e):
        self.log.append(e)


    def startImport(self):
        # Initialization000
        inFile = forceStringEx(self.edtFileName.text())

        # Prepare environment
        self.createdClients = 0
        self.createdDiagnosises = 0
        self.createdDiagnostics = 0
        self.createdEvents = 0
        self.createdVisits = 0
        self.progressBar.reset()
        self.progressBar.setValue(0)
        size = max(len(inFile), 1)

        #Process the import
        eventType = self.db.getRecordEx(self.tblEventType, '*', [self.tblEventType['code'].eq(u'100-Т'),  self.tblEventType['name'].like(u'...травм...')])
        if not eventType:
            self.err2log(u'Не найден тип события с кодом 100-Т')
            return
        self.eventTypeId = forceInt(eventType.value('id'))
        self.eventPurposeId = forceInt(eventType.value('purpose_id'))
        if not self.readFile(inFile):
            if self.abort:
                self.err2log(u'Прервано пользователем.')
            else:
                self.err2log(u'Ошибка: файл %s %s' % (inFile, self.errorString()))
        else:
            self.err2log(u'Обработано %d записей' % self.count)
            self.err2log(u'В базу добавлено %d пациентов' % self.createdClients)
            self.err2log(u'Создано %d обращений' % self.createdEvents)
            self.err2log(u'Создано %d посещений' % self.createdVisits)
            self.err2log(u'Создано %d диагнозов' % self.createdDiagnosises)

    def readFile(self, fileName):
        dbf = Dbf(fileName, True, encoding='cp866')
        self.progressBar.setFormat(u'%v/' + unicode(len(dbf)) + u' записей')
        self.progressBar.setMaximum(len(dbf))
        self.count = 0
        for dbfRecord in dbf:
            clientId = self.processClient(dbfRecord)
            eventId = self.processEvent(clientId, dbfRecord)
            if eventId:
                self.processVisit(eventId, dbfRecord)
                diagnosisId = self.processDiagnosis(clientId, dbfRecord)
                self.processDiagnostic(eventId, diagnosisId, dbfRecord)
            self.count+=1
            self.progressBar.setValue(self.count)
        dbf.close()
        return True

    def processClient(self, dbfRecord):
        db = QtGui.qApp.db
        # Get info from DBF
        clientData = {}
        addressData = {}
        clientData['lastName'] = dbfRecord['SURNAME']
        clientData['firstName'] = dbfRecord['NAME1']
        clientData['patrName'] = dbfRecord['NAME2']
        clientData['birthDate'] = dbfRecord['BIRTHDAY']
        sex = dbfRecord['SEX'].lower()
        if sex == u'м':
            sex = 1
        elif sex == u'ж':
            sex = 2
        else:
            sex = 0
        clientData['sex'] = sex

        documentData = {}
        ser1 = dbfRecord['SER1']
        ser2 = dbfRecord['SER2']
        docNumber = dbfRecord['NPASP']
        typeDoc = dbfRecord['TYPEDOC']
        polisSerial = dbfRecord['POLIS_S']
        polisNumber = dbfRecord['POLIS_N']

        hasPolisData = polisSerial or polisNumber
        hasDocumentData = docNumber or ser1 or ser2
        documentData['serial'] = ser1 + ' ' + ser2
        documentData['number'] = docNumber
        documentData['documentType_id'] = typeDoc

        addressData['freeinput'] = dbfRecord['LONGADDR']

        connectUnverified = self.chkConnectUnverified.isChecked()
        updateClientInfo = self.chkUpdateClientInfo.isChecked()

        # Try to find client by Name-sex-birtday
        clientRec = self.findClientByNameSexAndBirthDate(clientData['lastName'], clientData['firstName'], clientData['patrName'], clientData['sex'], clientData['birthDate'])
        if clientRec:
            clientId = forceInt(clientRec.value(0))
        else:
            clientId = None
        #i If exists
        if clientId:
            if typeDoc and (hasDocumentData):
                stmt = db.selectStmt(self.tblClientDocument, ['serial', 'number', 'documentType_id'], [self.tblClientDocument['client_id'].eq(clientId)])
                query = db.query(stmt)
                query.setForwardOnly(False)
                if not query.next():
                    #Нет инфо о документе в БД
                    if not (hasPolisData):
                        #Нет инфо о документе в БД, нет инфо о полисе в dbf - добавляем инфо о документе в БД
                        if connectUnverified:
                            if updateClientInfo:
                                self.setDocumentInfo(clientId, documentData)
                            return clientId
                        else:
                            clientId = self.createClient(clientData, addressData)
                            self.setDocumentInfo(clientId, documentData)
                            return clientId

                    polisFound, polisMatches = self.checkPolis(id, polisSerial, polisNumber)
                    if polisFound:
                        #Нет инфор о документе в БД,  есть инфо о полисе в БД
                        if polisMatches:
                            #Полис совпадает - цепляемся к нему, добавляем инфо о документе в БД
                            if updateClientInfo:
                                self.setDocumentInfo(clientId, documentData)
                            return clientId
                        else:
                            #Полис не совпадает - создаем нового пациента
                            clientId = self.createClient(clientData, addressData)
                            self.setDocumentInfo(clientId, documentData)
                            self.setPolisInfo(clientId, polisSerial, polisNumber)
                            return clientId
                    else:
                        #Нет инфо о документе в БД, нет инфо о полисе в БД - цепляемся к старому/добавляем инфо о полисе и документе/создаем нового пациента
                        if connectUnverified:
                            if updateClientInfo:
                                self.setDocumentInfo(clientId, documentData)
                                self.setPolisInfo(clientId, polisSerial, polisNumber)
                            return clientId
                        else:
                            clientId = self.createClient(clientData, addressData)
                            self.setDocumentInfo(clientId, documentData)
                            self.setPolisInfo(clientId, polisSerial, polisNumber)
                            return clientId
                else:
                    #Есть инфо о документе в БД
                    query.previous()
                    while query.next():
                        docRec = query.record()
                        documentSerial=forceStringEx(docRec.value('serial'))
                        if len(documentSerial)==4 and documentSerial.isdigit():
                            documentSerial=documentSerial[:2]+' '+documentSerial[2:]
                        documentSeries = trim(documentSerial.replace('-', ' ')).split()
                        documentNumber = forceString(docRec.value('number'))
                        documentSer1 = documentSeries[0] if len(documentSeries)>=1 else ''
                        documentSer2 = documentSeries[1] if len(documentSeries)>=2 else ''
                        #TODO: check the way of filling SER1 and SER2 fields in the external tool
                        if ser1 == documentSer1 and ser2 == documentSer2 and docNumber == documentNumber:
                            # В БД найден совпадающий документ, возвращаем id клиента
                            if updateClientInfo and hasPolisData and self.checkPolis(clientId, polisSerial, polisNumber) == (0, 0):
                                self.setPolisInfo(clientId, polisSerial, polisNumber)
                            return clientId
                    #Документы не совпадают, создаем нового пациента
                    clientId = self.createClient(clientData, addressData)
                    self.setDocumentInfo(clientId, documentData)
                    if hasPolisData:
                        self.setPolisInfo(clientId, polisSerial, polisNumber)
                    return clientId
            else:
                if not hasPolisData:
                    #Нет инфо о документе в dbf, нет инфо о полисе в dbf - цепляемся к старому/создаем нового, ничего не обновляем
                    if connectUnverified:
                        return clientId
                    else:
                        return self.createClient(clientData, addressData)

                polisFound, polisMatches = self.checkPolis(id, polisSerial, polisNumber)
                if polisFound:
                    if polisMatches:
                        #Нет инфо о документе в dbf, совпадение по полису
                        return clientId
                    else:
                        #Нет инфо о документе в dbf, полисы не совпадают
                        clientId = self.createClient(clientData, addressData)
                        if updateClientInfo:
                            self.setPolisInfo(clientId, polisSerial, polisNumber)
                        return clientId
                else:
                    #Нет инфо о документе в dbf, нет инфо о полисе в БД - присоединяемся к старому/обновляем полис/создаем нового
                    if connectUnverified:
                        if updateClientInfo:
                            self.setPolisInfo(clientId, polisSerial, polisNumber)
                        return clientId
                    else:
                        clientId = self.createClient(clientData, addressData)
                        self.setPolisInfo(clientId, polisSerial, polisNumber)
                        return clientId
        else:
            #Не найден пациент с заданными ФИО/полом/датой рождения. Создаем нового
            clientId = self.createClient(clientData, addressData)
            if hasDocumentData:
                self.setDocumentInfo(clientId, documentData)
            if hasPolisData:
                self.setPolisInfo(clientId, polisSerial, polisNumber)
            return clientId


    def createClient(self, clientData, addressData=None):
        rec = self.tableClient.newRecord()
        for key, val in clientData.iteritems():
            rec.setValue(key, toVariant(val))

        clientId = self.db.insertRecord(self.tableClient, rec)

        if addressData:
            addressrec = self.tblClientAddress.newRecord()
            addressrec.setValue('client_id', clientId)
            addressrec.setValue('freeinput', addressData['freeinput'])
            self.db.insertRecord(self.tblClientAddress, addressrec)
        self.createdClients += 1
        return clientId

    def setDocumentInfo(self, clientId, documentData):
        documentData['client_id'] = clientId
        docrec = self.tblClientDocument.newRecord()
        for key, val in documentData.iteritems():
            docrec.setValue(key, toVariant(val))
        self.db.insertRecord(self.tblClientDocument, docrec)

    def setPolisInfo(self, clientId, serial, number):
        polisrec = self.tblClientPolicy.newRecord()
        polisrec.setValue('serial',  toVariant(serial))
        polisrec.setValue('number', toVariant(number))
        polisrec.setValue('client_id', toVariant(clientId))
        self.db.insertRecord(self.tblClientPolicy, polisrec)

    def checkPolis(self, clientId, serial, number):
        db = QtGui.qApp.db
        selectStmt = db.selectStmt(self.tblClientPolicy, [self.tblClientPolicy['serial'], self.tblClientPolicy['number']], [self.tblClientPolicy['client_id'].eq(clientId)])
        query = db.query(selectStmt)
        query.setForwardOnly(False)
        if not query.next():
            return (0, 0)
        query.previous()
        while query.next():
            polisRec = query.record()
            if forceString(polisRec.value('serial')) == serial and forceString(polisRec.value('number')) == number:
                return (1, 1)
        return (1, 0)



    def processEvent(self, clientId, dbfRecord):
        db = QtGui.qApp.db
        eventData = {}
        eventData['setDate'] = dbfRecord['DATEIN']
        eventData['execDate'] = dbfRecord['DATEOUT']

        if not clientId in self.eventsCache.keys():
            self.eventsCache[clientId] = []
            selectStmt = db.selectStmt(self.tblEvent, ['setDate', 'execDate'], [self.tblEvent['client_id'].eq(clientId), self.tblEvent['deleted'].eq(0)])
            query = db.query(selectStmt)
            while query.next():
                record = query.record()
                self.eventsCache[clientId].append( (forceDate(record.value('setDate')), forceDate(record.value('execDate'))) )
        # TODO: Перенести проверку в запрос, не получать ВСЕ обращения пациента
        if (QDate(eventData['setDate']), QDate(eventData['execDate'])) in self.eventsCache[clientId]:
            return None

        eventData['client_id'] = clientId
        eventData['eventType_id'] = self.eventTypeId
        eventData['deleted'] = 0
        eventData['isPrimary'] = 1

        contractRecord = db.getRecordEx(self.tblContractSpec, ['master_id'], [self.tblContractSpec['eventType_id'].eq(self.eventTypeId), self.tblContractSpec['deleted'].eq(0)])
        self.contractId = forceRef(contractRecord.value('master_id'))

        eventData['contract_id'] = self.contractId

        eventData['org_id'] = QtGui.qApp.currentOrgId()
        if dbfRecord['ORDER'] in (u'э', u'Э'):
            eventData['order'] = 2
        else:
            eventData['order'] = 1

        resultId = forceRef(db.getRecordEx(self.tblRbResult, ['id'], [self.tblRbResult['eventPurpose_id'].eq(self.eventPurposeId), self.tblRbResult['regionalCode'].eq(dbfRecord['QRESULT'])]).value('id'))
        eventData['result_id'] = resultId

        specRegCode = dbfRecord['ID_PRVS_C'].split('.')[-1]
        speciality = db.getRecordEx(self.tblRbSpeciality, ['id'], [self.tblRbSpeciality['regionalCode'].eq(specRegCode)])
        if speciality:
            specialityId = forceRef(speciality.value('id'))
            personId = forceRef(db.getRecordEx(self.tblPerson, ['id'], [self.tblPerson['speciality_id'].eq(specialityId)]).value('id'))
            if personId:
                eventData['execPerson_id'] = personId
            else:
                self.err2log(u'Не найден врач с соответствующей специальностью при создании обращения')
                return None
        else:
            self.err2log(u'Не найдено специальности, соответствующей региональному коду при создании обращения')
            return None

        eventrec = self.tblEvent.newRecord()
        for key, val in eventData.iteritems():
            eventrec.setValue(key, toVariant(val))
        eventId = self.db.insertRecord(self.tblEvent, eventrec)
        self.createdEvents += 1
        return eventId


    def processVisit(self, eventId, dbfRecord):
        db = QtGui.qApp.db
        visitData = {}
        visitData['deleted'] = 0
        visitData['event_id'] = eventId
        visitData['scene_id'] = 1
        visitData['visitType_id'] = 1
        visitData['date'] = dbfRecord['DATEIN']

        specRegCode = dbfRecord['ID_PRVS_C'].split('.')[-1]
        specialityId = db.getRecordEx(self.tblRbSpeciality, ['id', 'service_id'], [self.tblRbSpeciality['regionalCode'].eq(specRegCode)])
        if specialityId:
            personId = forceRef(db.getRecordEx(self.tblPerson, ['id'], [self.tblPerson['speciality_id'].eq(forceRef(specialityId.value('id')))]).value('id'))
            visitData['person_id'] = personId
            visitData['service_id'] = forceRef(specialityId.value('service_id'))
        else:
            self.err2log(u'Ошибка: не найден врач с региональным кодом специальности %d, невозможно создать посещение' % specRegCode)
            return
        financeId = forceRef(db.getRecordEx(self.tblContract, ['finance_id'], [self.tblContract['id'].eq(self.contractId)]).value('finance_id'))
        visitData['finance_id'] = financeId

        visitrec = self.tblVisit.newRecord()
        for key, val in visitData.iteritems():
            visitrec.setValue(key, toVariant(val))
        visitId = self.db.insertRecord(self.tblVisit, visitrec)
        self.createdVisits += 1

    def processDiagnosis(self, clientId, dbfRecord):
        db = QtGui.qApp.db
        diagnosisData = {}
        diagnosisData['deleted']=0
        diagnosisData['client_id'] = clientId
        diagnosisData['diagnosisType_id'] = 2
        diagnosisData['character_id'] = getAvailableCharacterIdByMKB(dbfRecord['DIAGNOSIS'])[0]
        diagnosisData['MKB'] = dbfRecord['DIAGNOSIS']
        diagnosisData['endDate'] = dbfRecord['DATEIN']
        specRegCode = dbfRecord['ID_PRVS_C'].split('.')[-1]
        speciality = db.getRecordEx(self.tblRbSpeciality, ['id'], [self.tblRbSpeciality['regionalCode'].eq(specRegCode)])
        if speciality:
            specialityId = forceRef(speciality.value('id'))
            personId = forceRef(db.getRecordEx(self.tblPerson, ['id'], [self.tblPerson['speciality_id'].eq(specialityId)]).value('id'))
            if personId:
                diagnosisData['person_id'] = personId
            else:
                self.err2log(u'Не найден врач с соответствующей специальностью при создании обращения')
                return None
        else:
            self.err2log(u'Не найдено специальности, соответствующей региональному коду при создании обращения')
            return None

        diagnosisrec = self.tblDiagnosis.newRecord()
        for key, val in diagnosisData.iteritems():
            diagnosisrec.setValue(key, toVariant(val))
        diagnosisId = self.db.insertRecord(self.tblDiagnosis, diagnosisrec)
        self.createdDiagnosises += 1
        return diagnosisId

    def processDiagnostic(self, eventId, diagnosisId, dbfRecord):
        db = QtGui.qApp.db
        diagnosticData = {}
        diagnosticData['deleted']=0
        diagnosticData['event_id'] = eventId
        diagnosticData['diagnosis_id'] = diagnosisId
        diagnosticData['diagnosisType_id'] = 1
        diagnosticData['character_id'] = getAvailableCharacterIdByMKB(dbfRecord['DIAGNOSIS'])[0]
        diagnosticData['sanatorium'] = 0
        diagnosticData['hospital'] = 0

        diagnosticData['setDate'] = dbfRecord['DATEIN']
        diagnosticData['endDate'] = dbfRecord['DATEIN']

        result = db.getRecordEx(self.tblRbDiagnosticResult, ['id'], [self.tblRbDiagnosticResult['eventPurpose_id'].eq(self.eventPurposeId), self.tblRbDiagnosticResult['regionalCode'].eq(dbfRecord['ID_EXITUS'])])
        if not result:
            return None
        diagnosticData['result_id'] = forceRef(result.value('id'))

        specRegCode = dbfRecord['ID_PRVS_C'].split('.')[-1]
        speciality = db.getRecordEx(self.tblRbSpeciality, ['id'], [self.tblRbSpeciality['regionalCode'].eq(specRegCode)])
        if speciality:
            specialityId = forceRef(speciality.value('id'))
            personId = forceRef(db.getRecordEx(self.tblPerson, ['id'], [self.tblPerson['speciality_id'].eq(specialityId)]).value('id'))
            if personId:
                diagnosticData['person_id'] = personId
                diagnosticData['speciality_id'] = specialityId
            else:
                self.err2log(u'Не найден врач с соответствующей специальностью при создании обращения')
                return None
        else:
            self.err2log(u'Не найдено специальности, соответствующей региональному коду при создании обращения')
            return None

        diagnosticrec = self.tblDiagnostic.newRecord()
        for key, val in diagnosticData.iteritems():
            diagnosticrec.setValue(key, toVariant(val))
        diagnosticId = self.db.insertRecord(self.tblDiagnostic, diagnosticrec)
        self.createdDiagnostics += 1


    def findClientByNameSexAndBirthDate(self, lastName, firstName, patrName, sex, birthDate):
        key = (lastName, firstName, patrName, sex, birthDate)
        result = self.clientCache.get(key, -1)

        if result == -1:
            result = None
            table = self.tableClient
            filter = [table['deleted'].eq(0),
                        table['lastName'].eq(lastName),
                        table['firstName'].eq(firstName),
                        table['patrName'].eq(patrName),
                        table['birthDate'].eq(birthDate)]

            if sex != 0:
                filter.append(table['sex'].eq(sex))
            record = self.db.getRecordEx(table, '*',  filter, 'id')

            if record:
                result = record

            self.clientCache[key] = result

        return result

