# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import uuid

from PyQt4 import QtCore, QtGui

from library.Utils import forceBool, forceInt, forceRef, forceString, calcAgeInYears, formatSNILS, smartDict


def getJobTypeAttributes(jobTicketId):
    db = QtGui.qApp.db
    tableJobTicket = db.table('Job_Ticket')
    tableJob = db.table('Job')
    tableJobType = db.table('rbJobType')
    queryTable = tableJobTicket.leftJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))
    queryTable = queryTable.leftJoin(tableJobType, tableJobType['id'].eq(tableJob['jobType_id']))
    record = db.getRecordEx(queryTable, [tableJobType['isInstant'], tableJobType['laboratory_id']], tableJobTicket['id'].eq(jobTicketId))
    if record:
        return smartDict(isInstant=forceBool(record.value('isInstant')),
                         laboratoryId=forceBool(record.value('laboratory_id'))
                        )
    else:
        return None


def isInstant(jobTicketId):
    d = getJobTypeAttributes(jobTicketId)
    return d.isInstant if d else False


def getLaboratoryId(jobTicketId):
    d = getJobTypeAttributes(jobTicketId)
    return d.laboratoryId if d else None


def getLaboratory(laboratoryId):
    db = QtGui.qApp.db
    record = db.getRecord('rbLaboratory', '*', laboratoryId)
    if record:
        return smartDict(
            code = forceString(record.value('code')),
            name = forceString(record.value('name')),
            protocol = forceInt(record.value('protocol')),
            address = forceString(record.value('address')),
            ownName = forceString(record.value('ownName')),
            labName = forceString(record.value('labName')))
    else:
        return None


def getTestCodes(laboratoryId, testIdList):
    db = QtGui.qApp.db
    tableLaboratoryTest = db.table('rbLaboratory_Test')
    tableTest = db.table('rbTest')
    queryTable = tableLaboratoryTest.leftJoin(tableTest, tableTest['id'].eq(tableLaboratoryTest['test_id']))
    records = db.getRecordList(queryTable,
                            [tableLaboratoryTest['test_id'],
                             tableLaboratoryTest['book'],
                             tableLaboratoryTest['code'],
                             tableTest['name']
                            ],
                            [tableLaboratoryTest['master_id'].eq(laboratoryId),
                             tableLaboratoryTest['test_id'].inlist(testIdList),
                            ])
    result = {}
    for record in records:
        testId = forceInt(record.value('test_id'))
        book   = forceString(record.value('book'))
        code   = forceString(record.value('code'))
        name   = forceString(record.value('name'))
        result[testId] = book, code, name
    return result


def sendTest(widget, clientInfo, jobTicketId, properties):
    def _sendTest():
        laboratoryId = getLaboratoryId(jobTicketId)
        laboratory = getLaboratory(laboratoryId)
        if laboratory:
            testIdList = [property.type().testId for property in properties]
            testCodes = getTestCodes(laboratoryId, testIdList)
            if laboratory.protocol == 0:
                sendTestHl7OverXml(widget, clientInfo, jobTicketId, laboratory, testCodes, properties)
            elif laboratory.protocol == 1:
                sendTestASTM(widget, clientInfo, jobTicketId, laboratory, testCodes, properties)
    QtGui.qApp.call(widget, _sendTest)


def idToUuid(timestamp, id):
    node = uuid.getnode() # 48 bit, 6 bytes
    timestamp_low = timestamp & 0xFFFFFFFFL # timestamp: 32 bit, 4 bytes
    id_low  = id & 0xFFFFL # id: low 16 bit
    id_mid = (id>>16) & 0xFFL # id: mid 8 bit
    id_high = (id>>24) & 0xFFL # id: high 8 bit
    intValue = (timestamp_low << 96L) | (id_low << 80L) | (id_mid << 64L) | (id_high << 48L) | node
    return uuid.UUID(int=intValue, version=4)


def sendTestHl7OverXml(widget, clientInfo, jobTicketId, laboratory, testCodes, properties):
        import hl7.ORM_O01
        from ZSI import TC
        from aksiSoap import svcHl7Message_client

        now = QtCore.QDateTime.currentDateTime()
        timestamp = now.toTime_t()
        message = hl7.ORM_O01.ORM_O01()
        message.MSH.MSH_1 = '|'
        message.MSH.MSH_2 = '^~\\&'
        message.MSH.MSH_3.HD_1 = u'vista-med'
        message.MSH.MSH_4.HD_1 = laboratory.ownName
        message.MSH.MSH_6.HD_1 = laboratory.labName
        message.MSH.MSH_7.TS_1 = hl7.datetimeToHl7(now)
        message.MSH.MSH_9.MSG_1 = 'ORM'
        message.MSH.MSH_9.MSG_2 = 'O01'
        message.MSH.MSH_9.MSG_3 = 'ORM_O01'
        message.MSH.MSH_10 = idToUuid(timestamp,jobTicketId).hex

        message.MSH.MSH_11.PT_1 = 'D'
        message.MSH.MSH_12.VID_1 = '2.5'
        #message.MSH.MSH_18.append('UNICODE UTF-8')

        message.ORM_O01_PATIENT.PID.PID_3.append()
        message.ORM_O01_PATIENT.PID.PID_3[0].CX_1 = formatSNILS(clientInfo['SNILS'])
        message.ORM_O01_PATIENT.PID.PID_3[0].CX_5 = 'XX'
        message.ORM_O01_PATIENT.PID.PID_5.append()
        message.ORM_O01_PATIENT.PID.PID_5[0].XPN_1.FN_1 = clientInfo['lastName']
        message.ORM_O01_PATIENT.PID.PID_5[0].XPN_2 = clientInfo['firstName']
        message.ORM_O01_PATIENT.PID.PID_5[0].XPN_3 = clientInfo['patrName']
        message.ORM_O01_PATIENT.PID.PID_7.TS_1 = hl7.datetimeToHl7(clientInfo['birthDate'])
        message.ORM_O01_PATIENT.PID.PID_8 = ['U', 'M', 'F'][clientInfo['sexCode']]

        i = 0
        for property in properties:
            testId = property.type().testId
            if testId in testCodes:
                i += 1
                book, code, name = testCodes[testId]
                propertyRecordId = forceRef(property.getRecord().value('id'))
                id = idToUuid(timestamp,propertyRecordId).hex
                message.ORM_O01_ORDER.append()
                order = message.ORM_O01_ORDER[-1]
                order.ORC.ORC_1 = 'NW'
                order.ORC.ORC_2.EI_3 = id
                order.ORC.ORC_2.EI_4 = 'L'
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_1 = str(i)
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_2.EI_3 = id
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_2.EI_4 = 'L'
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_4.CE_1 = code
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_4.CE_2 = name
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_4.CE_3 = book
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_11 = 'L'
                order.ORM_O01_ORDER_DETAIL.ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP.OBR.OBR_13 = ''
            else:
                pass # 'testId' not found

        loc = svcHl7Message_client.svcHl7MessageLocator()
        port = loc.getHl7Message(laboratory.address)
        data = message.toDom()
        data.typecode = TC.XML('NoName', comments=0, inline=1, wrapped=False)
        req = svcHl7Message_client.msgHl7MessageIn()
        req._any = data
        res = QtGui.qApp.callWithWaitCursor(widget, port.opHl7Message, req)
        QtGui.QMessageBox.information(widget,
                                    u'Результат',
                                    u'Передача успешна',
                                    QtGui.QMessageBox.Close)


# ====================================================================================

def sendTestASTM(widget, clientInfo, jobTicketId, laboratory, testCodes, properties):
        from Exchange.Lab.AstmE1381.FileInterface import CFileInterface
        from Exchange.Lab.AstmE1394.Message import CMessage
        import json

        opts = json.loads(laboratory.address)

        now = QtCore.QDateTime.currentDateTime()
        message = CMessage()
        patient = message.newPatient()
        patient.patientId = clientInfo['id']
        patient.laboratoryPatientId = clientInfo['id']
        patient.lastName  = clientInfo['lastName']
        patient.firstName = clientInfo['firstName']
        patient.patrName  = clientInfo['patrName']
        patient.birthDate = clientInfo['birthDate']
        patient.sex = ['U', 'M', 'F'][clientInfo['sexCode']]
        patient.age       = calcAgeInYears(clientInfo['birthDate'], now.date())

        for property in properties:
            testId = property.type().testId
            if testId in testCodes:
                book, code, name = testCodes[testId]
                propertyRecordId = forceRef(property.getRecord().value('id'))
                order = patient.newOrder()
                order.specimenId = jobTicketId
                order.assayCode       =  code
                order.assayName       =  name
                order.requestDateTime =  now
                order.specimenCollectionDateTime = now
                order. propertyRecordId
                order.priority        = 'R'
                order.actionCode      = 'A'
                #order.specimenDescriptor =  'S'
                order.userField1      =  jobTicketId
                order.userField2      =  propertyRecordId
                order.reportTypes     =  'O'
                #order.specimenInstitution='LAB2'
            else:
                pass # 'testId' not found

        records = message.getRecords(encoding=opts.get('encoding', 'utf-8'))
        interface = CFileInterface(opts)
        interface.send(records)
        QtGui.QMessageBox.information(widget,
                                    u'Результат',
                                    u'Передача успешна',
                                    QtGui.QMessageBox.Close)
