# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.SimpleProgressDialog   import CSimpleProgressDialog
from library.Utils                  import forceBool, forceDateTime, forceInt, forceRef, forceString, calcAgeInYears, smartDict

from Registry.Utils                 import getClientInfo


class CProcessHelper(object):
    def __init__(self, tasks):
        self.tasks = tasks
#        self.currTask = 0
        self.mapEquipmentIdToInterface = {}
        self.mapClientIdToInfo = {}


    def getEquipmentInterface(self, equipmentId):
        if equipmentId in self.mapEquipmentIdToInterface:
            return self.mapEquipmentIdToInterface[equipmentId]

        interface = getEquipmentInterface(equipmentId)
        self.mapEquipmentIdToInterface[equipmentId] = interface
        return interface


    def getClientInfo(self, clientId):
        if clientId in self.mapClientIdToInfo:
            return self.mapClientIdToInfo[clientId]
        clientInfo = getClientInfo(clientId)
        self.mapClientIdToInfo[clientId] = clientInfo
        return clientInfo


    def stepIterator(self, progressDialog):
        for task in self.tasks:
            ((equipmentId, clientId, dateTime, externalId), testList) = task
            equipmentInterface = self.getEquipmentInterface(equipmentId)
            clientInfo = self.getClientInfo(clientId)
            if equipmentInterface and equipmentInterface.protocol == 1:
                sendRequestOverASTM(progressDialog, equipmentInterface, clientInfo, QtCore.QDateTime(dateTime), externalId, testList)
            yield len(testList)


def sendTests(widget, probeIdList):
    pd = CSimpleProgressDialog(widget)
    pd.setWindowTitle(u'Экспорт заданий')
    try:
        tasks = selectTasks(probeIdList)
        helper = CProcessHelper(tasks)
        count = sum(len(task[1]) for task in tasks)
        pd.setStepCount(count)
        pd.setAutoStart(True)
        pd.setAutoClose(False)
        pd.setStepIterator(helper.stepIterator)
        pd.exec_()
    finally:
        pass


def selectTasks(probeIdList):
    # возвращает список пар ( задание-на-исследование, список-исследуемых-параметров )
    # где задание-на-исследование это кортеж ( id-оборудования, наклейка, id-пациента, время-забора)
    # а каждый исследуемый параметр характеризуется кортежем ( id-пробы, код-теста, имя-теста, код-метериала, имя-материала, признак-срочности)
    result = []
    db = QtGui.qApp.db
    tableProbe = db.table('Probe')
    tableTissue = db.table('TakenTissueJournal')
    tableEqupmentTest = db.table('rbEquipment_Test')

    table = tableProbe.leftJoin(tableEqupmentTest, db.joinAnd([tableEqupmentTest['id'].eq(tableProbe['workTest_id']),
                                                               tableEqupmentTest['equipment_id'].eq(tableProbe['equipment_id']),
                                                              ]
                                                             )
                               )
    table = table.leftJoin(     tableTissue, tableTissue['id'].eq(tableProbe['takenTissueJournal_id']))
    stmt = db.selectStmt(table,
                         [tableProbe['equipment_id'], tableProbe['externalId'],
                          tableProbe['id'].alias('probe_id'), tableProbe['isUrgent'],
                          tableTissue['client_id'], tableTissue['datetimeTaken'],
                          tableEqupmentTest['hardwareTestCode'], tableEqupmentTest['hardwareTestName'],
                          tableEqupmentTest['hardwareSpecimenCode'], tableEqupmentTest['hardwareSpecimenName'],
                         ],
                         tableProbe['id'].inlist(probeIdList),
                         [tableProbe['equipment_id'].name(), tableTissue['client_id'].name(),
                          tableTissue['datetimeTaken'].name(), tableProbe['externalId'].name(),
                          tableProbe['id'].name()
                         ]
                        )
    query = db.query(stmt)
    prevKey = None
    while query.next():
        record = query.record()
        equipmentId = forceRef(record.value('equipment_id'))
        externalId  = forceString(record.value('externalId'))
        clientId    = forceRef(record.value('client_id'))
        dateTime    = forceDateTime(record.value('datetimeTaken'))
        probeId     = forceRef(record.value('probe_id'))
        hardwareTestCode = forceString(record.value('hardwareTestCode'))
        hardwareTestName = forceString(record.value('hardwareTestName'))
        hardwareSpecimenCode = forceString(record.value('hardwareSpecimenCode'))
        hardwareSpecimenName = forceString(record.value('hardwareSpecimenName'))
        isUrgent = forceBool(record.value('isUrgent'))
        key = ( equipmentId, clientId, dateTime.toPyDateTime(), externalId )
        if prevKey != key:
            result.append((key, []))
            prevKey = key
        result[-1][1].append((probeId, hardwareTestCode, hardwareTestName, hardwareSpecimenCode, hardwareSpecimenName, isUrgent))
    return result


def getEquipmentInterface(equipmentId):
    db = QtGui.qApp.db
    record = db.getRecord('rbEquipment', '*', equipmentId)
    if record:
        return smartDict(
                         protocol = forceInt(record.value('protocol')),
                         address = forceString(record.value('address')),
                         ownName = forceString(record.value('ownName')),
                         labName = forceString(record.value('labName'))
                        )
    else:
        return None


def sendRequestOverASTM(widget, equipmentInterface, clientInfo, dateTime, label, testList):
        from Exchange.Lab.AstmE1381.FileInterface import CFileInterface
        from Exchange.Lab.AstmE1394.Message import CMessage
        import json

        opts = json.loads(equipmentInterface.address)

        now = QtCore.QDateTime.currentDateTime()
        message = CMessage()
        patient = message.newPatient()
        patient.patientId = clientInfo['id']
        patient.laboratoryPatientId = label
        patient.lastName  = clientInfo['lastName']
        patient.firstName = clientInfo['firstName']
        patient.patrName  = clientInfo['patrName']
        patient.birthDate = clientInfo['birthDate']
        patient.sex = ['U', 'M', 'F'][clientInfo['sexCode']]
        patient.age = calcAgeInYears(clientInfo['birthDate'], dateTime.date())

        for test in testList:
            probeId, testCode, testName, specimenCode, specimenName, isUrgent = test
            order = patient.newOrder()
            order.specimenId      = label
            order.instrumentSpecimenId = label
            order.assayCode       = testCode
            order.assayName       = testName
            order.requestDateTime =  now
            order.specimenCollectionDateTime = dateTime
            order.priority        = 'A' if isUrgent else 'R'
            order.actionCode      = 'A'
            order.specimenDescr   = specimenCode
            order.userField1      = probeId
#            order.userField2      = probeId
            order.reportTypes     = 'O'
            #order.specimenInstitution='LAB2'

        records = message.getRecords(encoding=opts.get('encoding', 'utf-8'))
        interface = CFileInterface(opts)
        interface.write(records)
