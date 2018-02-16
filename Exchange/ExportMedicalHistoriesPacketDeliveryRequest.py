# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

import os.path

from library.database  import *
from library.Utils     import *

class CBriefDeliveryRequest(QXmlStreamWriter):
    mapChannelDelivery = {
        u'Неотложка': 'firstAid',
        u'СМП': 'Ambulance',
        u'Сан. транспорт': 'policlinic',
        u'Самостоятельно': 'himself'
    }

    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)

    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeMedicalHistoriesPacketDeliveryRequest(self, record):
        self.writeMedicalHistory(record)

    def writeMedicalHistory(self, record):
        self.writeStartElement('urn1:medicalHistory')
        self.writeTextElement('urn1:carNum', forceString(record.value('carNum')))
        self.writeTextElement('urn1:orderNum', forceString(record.value('orderNum')))
        deliveryType = forceInt(record.value('deliveryType'))
        self.writeTextElement('urn1:deliveryType', 'EMERGENCY' if deliveryType == 2 else 'PLANNING')
        channelDelivery = re.sub(ur'^\d+:\s+', '', forceString(record.value('channelDelivery')))
        self.writeTextElement('urn1:channelDelivery', self.mapChannelDelivery.get(channelDelivery, ''))
        self.writeTextElement('urn1:room', forceString(record.value('room')))
        self.writeTextElement('urn1:stationarDepartment', forceString(record.value('stationarDepartment')))
        dateReception = forceDateTime(record.value('dateReception'))
        self.writeTextElement('urn1:dateReception', dateReception.toString(Qt.ISODate))

        medCardNum = forceString(record.value('medCardNum'))
        if medCardNum == '':
            medCardNum = '0'
        self.writeTextElement('urn1:medCardNum', medCardNum)

        dischargeDate = forceDateTime(record.value('dischargeDate'))
        self.writeTextElement('urn1:dischargeDate', dischargeDate.toString(Qt.ISODate))
        self.writeTextElement('urn1:callDistrict', forceString(record.value('callDistrict')))
        self.writePatient(record)
        self.writeEndElement()

    def writePatient(self, record):
        self.writeStartElement('urn1:patient')
        self.writeTextElement('urn1:surname', forceString(record.value('surname')))
        self.writeTextElement('urn1:firstname', forceString(record.value('firstname')))
        self.writeTextElement('urn1:secondname', forceString(record.value('secondname')))
        sex = forceInt(record.value('sex'))
        self.writeTextElement('urn1:sex', 'MALE' if sex == 1 else 'FEMALE' if sex == 2 else 'UNKNOWN')
        bloodTypeName = forceString(record.value('bloodTypeName'))
        if bloodTypeName:
            bloodType = bloodTypeName.split('Rh')
            self.writeTextElement('urn1:bloodType', bloodType[0])
            self.writeTextElement('urn1:bloodRes', bloodType[1])
        else:
            self.writeTextElement('urn1:bloodType', '')
            self.writeTextElement('urn1:bloodRes', '')
        self.writeTextElement('urn1:birthDate', forceString(record.value('birthDate')))
        self.writeTextElement('urn1:passport', forceString(record.value('passport')))
        self.writeTextElement('urn1:benefits', forceString(record.value('benefits')))
        self.writeTextElement('urn1:birthPlace', forceString(record.value('birthPlace')))
        self.writeTextElement('urn1:addressFact', forceString(record.value('addressFact')))
        self.writeAddressReg(record)
        self.writeWork(record)
        referralDiagnosis = forceString(record.value('referralDiagnosis'))
        if referralDiagnosis:
            self.writeStartElement('urn1:diagnose')
            self.writeTextElement('urn1:type', 'MAIN')
            self.writeTextElement('urn1:diagnoseString', referralDiagnosis)
            self.writeEndElement()

        clinicalDiagnosisMKB = record.value('clinicalDiagnosisMKB')
        if clinicalDiagnosisMKB:
            self.writeDiagnose(record, 0)
        concomitantDiagnosisMKB = record.value('concomitantDiagnosisMKB')
        if concomitantDiagnosisMKB:
            self.writeDiagnose(record, 1)
        preliminaryDiagnosisMKB = record.value('preliminaryDiagnosisMKB')
        if preliminaryDiagnosisMKB:
            self.writeDiagnose(record, 2)
        receivedDiagnosis = forceString(record.value('receivedDiagnosis'))
        if receivedDiagnosis:
            self.writeStartElement('urn1:diagnose')
            self.writeTextElement('urn1:type', 'RECEPTION')
            self.writeTextElement('urn1:diagnoseString', receivedDiagnosis)
            self.writeEndElement()
        self.writePolis(record)
        self.writeEndElement()

    def writeAddressReg(self, record):
        self.writeStartElement('urn1:addressReg')
        self.writeTextElement('urn1:region', forceString(record.value('region')))
        self.writeTextElement('urn1:addressRegCode', forceString(record.value('addressRegCode')))
        self.writeTextElement('urn1:addressReg', forceString(record.value('addressReg')))
        self.writeEndElement()

    def writeWork(self, record):
        self.writeStartElement('urn1:work')
        self.writeTextElement('urn1:organization', forceString(record.value('organization')))
        self.writeTextElement('urn1:addressOrg', forceString(record.value('addressOrg')))
        self.writeTextElement('urn1:position', forceString(record.value('position')))
        self.writeEndElement()

    def writeDiagnose(self, record, diag):
        def f(value):
            return '(' + value + ')' if value else ''
        if diag == 0:
            type = 'CLINIC'
            diagnoseString = f(forceString(record.value('nameClinicalDiagnosisMKB')))
            diagnosisMKB = f(forceString(record.value('clinicalDiagnosisMKB')))
        elif diag == 1:
            type = 'CONCOMITANT'
            diagnoseString = f(forceString(record.value('nameConcomitantDiagnosisMKB')))
            diagnosisMKB = f(forceString(record.value('concominantDiagnosisMKB')))
        elif diag == 2:
            type = 'PRELIMINARY'
            diagnoseString = f(forceString(record.value('namePreliminaryDiagnosisMKB')))
            diagnosisMKB = f(forceString(record.value('preliminaryDiagnosisMKB')))
        else:
            type = ''
            diagnoseString = ''
            diagnosisMKB = ''
        self.writeStartElement('urn1:diagnose')
        self.writeTextElement('urn1:type', type)
        self.writeTextElement('urn1:diagnoseString', u'%s%s' % (diagnosisMKB, diagnoseString))
        self.writeEndElement()

    def writePolis(self, record):
        self.writeStartElement('urn1:polis')
        self.writeTextElement('urn1:polisType', forceString(record.value('polisType')))
        self.writeTextElement('urn1:polisNum', forceString(record.value('polisNum')))
        self.writeTextElement('urn1:smo', forceString(record.value('smo')))
        self.writeTextElement('urn1:polisText', forceString(record.value('polisText')))
        self.writeEndElement()

    def writeFileHeader(self, device, fileName, startDate, endDate):
        self._clientsSet = set()
        self.setDevice(device)
        #self.writeStartDocument()
        #self.writeStartElement('urn1:medicalHistoriesPacketDeliveryRequest')
        self.writeStartElement('urn1:hospitalMedicalHistoriesPacket')
        self.writeTextElement('urn1:hospitalName', '15') #TODO
        self.writeTextElement('urn1:dateFrom', startDate.toString('yyyy-MM-ddThh:mm:ss.zzz'))
        self.writeTextElement('urn1:dateTo', endDate.toString('yyyy-MM-ddThh:mm:ss.zzz'))

    def writeFileFooter(self):
        self.writeEndElement()
        #self.writeEndDocument()


# *****************************************************************************************

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Export medical histories first lists in specified database.')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-t', dest='datetime', default=None)
    parser.add_argument('-a', dest='host', default='192.168.0.3')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-D', dest='dir', default=os.getcwd())
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)

    app = QtCore.QCoreApplication(sys.argv)
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
    db = connectDataBaseByInfo(connectionInfo)
    QtGui.qApp.db = db
    fileName = u'MHPDR_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
    dt = args['datetime']
    dt = QDateTime.fromString(dt, 'yyyy-MM-ddTHH:mm:ss') if dt else None # QDateTime.currentDateTime().addSecs(-60)
    curDt = QtCore.QDateTime.currentDateTime()
    if not (dt is None or dt.isValid()):
        print 'Error: incorrect base datetime.'
        sys.exit(-3)
    stmt = u'''
            SELECT
              ReceivedCarAPS.value AS carNum,
              ReceivedOrderAPS.value AS orderNum,
              e.`order` AS deliveryType,
              ReceivedChannelAPS.value AS channelDelivery,
              oshb.name AS room,

              os.name AS stationarDepartment,
              ReceivedAction.begDate AS dateReception,
              e.externalId AS medCardNum,
              LeavedAction.begDate AS dischargeDate,
              '' AS callDistrict,
              c.lastName AS surname,
              c.firstName AS firstname,
              c.patrName AS secondname,
              c.sex AS sex,
              bt.name AS bloodTypeName,    # Разбить на 2 поля - тип и резус
              c.birthDate AS birthDate,
              CONCAT(dt.name, ' ', cd.serial, ' ', cd.number) AS passport,
              '' AS benefits,
              ## addressReg
              K.OCATD AS region,
              '' AS addressRegCode,     # Мы не можем получить код дома по КЛАДР, максимум - код улицы.
              formatClientAddress(ca.id) AS addressReg,
              ## work
              o.fullName AS organization,
              o.Address AS addressOrg,
              cw.post AS `position`,
              # ClientInfo
              ReceivedDiagnosisAPS.value AS receivedDiagnosis,    # TYPE=RECEPTION
              ReferralDiagnosisAPS.value AS referralDiagnosis,    # TYPE=MAIN
              ClinicalDiagnosis.MKB AS clinicalDiagnosisMKB,      # TYPE=CLINIC
              ConcomitantDiagnosis.MKB AS concomitantDiagnosisMKB,# TYPE=CONCOMITANT
              PreliminaryDiagnosis.MKB AS preliminaryDiagnosisMKB,# TYPE=PRELIMINARY
              TableClinicalDiagnosisMKB.DiagName AS nameClinicalDiagnosisMKB,
              TableConcomitantDiagnosisMKB.DiagName AS nameConcomitantDiagnosisMKB,
              TablePreliminaryDiagnosisMKB.DiagName AS namePreliminaryDiagnosisMKB,
              c.birthPlace AS birthPlace,
              getClientLocAddress(c.id) AS addressFact,
              # polis
              pt.code AS polisType,
              cp.number AS polisNum,
              o2.fullName AS smo,
              cp.note AS polisText



              FROM Event e
              INNER JOIN Client c ON c.id = e.client_id
              LEFT JOIN rbBloodType bt ON bt.id = c.bloodType_id
              LEFT JOIN ClientDocument cd ON cd.id = getClientDocumentId(c.id)
              LEFT JOIN rbDocumentType dt ON dt.id = cd.documentType_id
              LEFT JOIN ClientAddress ca ON getClientRegAddress(c.id)
              LEFT JOIN Address a1 ON a1.id = ca.address_id
              LEFT JOIN AddressHouse ah ON ah.id = a1.house_id
              LEFT JOIN kladr.KLADR K ON K.CODE = ah.KLADRCode
              LEFT JOIN ClientWork cw ON cw.id = getClientWorkId(c.id)
              LEFT JOIN Organisation o ON cw.org_id = o.id
              LEFT JOIN ClientPolicy cp ON cp.id = getClientPolicyId(c.id, 1)
              LEFT JOIN rbPolicyType pt ON pt.id = cp.policyType_id
              LEFT JOIN Organisation AS o2 ON o2.id = cp.insurer_id
              INNER JOIN Action ReceivedAction ON ReceivedAction.event_id = e.id AND ReceivedAction.actionType_id = (SELECT at.id FROM ActionType at WHERE at.flatCode = 'received')
              INNER JOIN Action MovingAction ON MovingAction.id = (SELECT MIN(Action.id) FROM Action INNER JOIN ActionType ON ActionType.id = Action.actionType_id WHERE Action.event_id = e.id AND Action.deleted = 0 AND ActionType.deleted = 0 AND ActionType.flatCode = 'moving' LIMIT 1)
              LEFT JOIN ActionProperty ReceivedCarAP ON ReceivedCarAP.action_id = ReceivedAction.id AND ReceivedCarAP.type_id = (SELECT apt.id FROM ActionPropertyType apt INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND apt.name = '№ машины')
              LEFT JOIN ActionProperty_String ReceivedCarAPS ON ReceivedCarAPS.id = ReceivedCarAP.id
              LEFT JOIN ActionProperty ReceivedOrderAP ON ReceivedOrderAP.action_id = ReceivedAction.id AND ReceivedOrderAP.type_id = (SELECT apt.id FROM ActionPropertyType apt INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND apt.name = '№ Наряда')
              LEFT JOIN ActionProperty_String ReceivedOrderAPS ON ReceivedOrderAPS.id = ReceivedOrderAP.id
              LEFT JOIN ActionProperty ReceivedDiagnosisAP ON ReceivedDiagnosisAP.action_id = ReceivedAction.id AND ReceivedDiagnosisAP.type_id = (SELECT apt.id FROM ActionPropertyType apt INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND apt.name = 'Диагноз приемного отделения')
              LEFT JOIN ActionProperty_String ReceivedDiagnosisAPS ON ReceivedDiagnosisAPS.id = ReceivedDiagnosisAP.id
              LEFT JOIN ActionProperty ReferralDiagnosisAP ON ReferralDiagnosisAP.action_id = ReceivedAction.id AND ReferralDiagnosisAP.type_id = (SELECT apt.id FROM ActionPropertyType apt INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND apt.name = 'Диагноз направителя')
              LEFT JOIN ActionProperty_String ReferralDiagnosisAPS ON ReferralDiagnosisAPS.id = ReferralDiagnosisAP.id
              LEFT JOIN ActionProperty ReceivedChannelAP ON ReceivedChannelAP.action_id = ReceivedAction.id AND ReceivedChannelAP.type_id = (SELECT apt.id FROM ActionPropertyType apt INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND apt.name = 'Кем доставлен')
              LEFT JOIN ActionProperty_String ReceivedChannelAPS ON ReceivedChannelAPS.id = ReceivedChannelAP.id
              LEFT JOIN ActionProperty ReceivedOrgStructureAP ON ReceivedOrgStructureAP.action_id = ReceivedAction.id AND ReceivedOrgStructureAP.type_id = (SELECT apt.id FROM ActionPropertyType apt INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND apt.name = 'Направлен в отделение')
              LEFT JOIN ActionProperty_OrgStructure ReceivedOrgStructureAPOS ON ReceivedOrgStructureAPOS.id = ReceivedOrgStructureAP.id
              LEFT JOIN OrgStructure os ON os.id = ReceivedOrgStructureAPOS.value
              LEFT JOIN ActionProperty ReceivedHospitalBedAP ON ReceivedHospitalBedAP.action_id = ReceivedAction.id AND ReceivedHospitalBedAP.type_id = (SELECT apt.id FROM ActionPropertyType apt INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND apt.name = 'койка')
              LEFT JOIN ActionProperty_HospitalBed ReceivedHospitalBedAPHB ON ReceivedHospitalBedAPHB.id = ReceivedHospitalBedAP.id
              LEFT JOIN OrgStructure_HospitalBed oshb ON oshb.id = ReceivedHospitalBedAPHB.value
              LEFT JOIN Action LeavedAction  ON LeavedAction.event_id = e.id AND LeavedAction.actionType_id = (SELECT id FROM ActionType at WHERE at.flatCode = 'leaved')
              LEFT JOIN Diagnostic ClinicalDiagnostic ON ClinicalDiagnostic.event_id = e.id AND ClinicalDiagnostic.diagnosisType_id = (SELECT dt.id FROM rbDiagnosisType dt WHERE dt.code = '1')
              LEFT JOIN Diagnosis ClinicalDiagnosis ON ClinicalDiagnosis.id = ClinicalDiagnostic.diagnosis_id
              LEFT JOIN Diagnostic ConcomitantDiagnostic ON ConcomitantDiagnostic.event_id = e.id AND ConcomitantDiagnostic.diagnosisType_id = (SELECT dt.id FROM rbDiagnosisType dt WHERE dt.code = '9')
              LEFT JOIN Diagnosis ConcomitantDiagnosis ON ConcomitantDiagnosis.id = ConcomitantDiagnostic.diagnosis_id
              LEFT JOIN Diagnostic PreliminaryDiagnostic ON PreliminaryDiagnostic.event_id = e.id AND PreliminaryDiagnostic.diagnosisType_id = (SELECT dt.id FROM rbDiagnosisType dt WHERE dt.code = '7')
              LEFT JOIN Diagnosis PreliminaryDiagnosis ON PreliminaryDiagnosis.id = PreliminaryDiagnostic.diagnosis_id
              LEFT JOIN MKB_Tree TableClinicalDiagnosisMKB ON TableClinicalDiagnosisMKB.DiagID LIKE ClinicalDiagnosis.MKB
              LEFT JOIN MKB_Tree TableConcomitantDiagnosisMKB ON TableConcomitantDiagnosisMKB.DiagID LIKE ConcomitantDiagnosis.MKB
              LEFT JOIN MKB_Tree TablePreliminaryDiagnosisMKB ON TablePreliminaryDiagnosisMKB.DiagID LIKE PreliminaryDiagnosis.MKB


              WHERE MovingAction.createDatetime BETWEEN '%s' AND '%s'
            ''' % (dt.toString(Qt.ISODate), curDt.toString(Qt.ISODate))
    query = db.query(stmt)
    if query.size() > 0:
        outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        clientsOut = CBriefDeliveryRequest(None)
        clientsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        clientsOut.writeFileHeader(outFile, None, dt, curDt)

        while query.next():
            clientsOut.writeMedicalHistoriesPacketDeliveryRequest(query.record())
        clientsOut.writeFileFooter()
        outFile.close()

if __name__ == '__main__':
    main()