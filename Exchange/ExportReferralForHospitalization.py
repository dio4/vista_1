# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

import os.path
import uuid

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QDateTime, QXmlStreamWriter, Qt

from library.database  import connectDataBaseByInfo
from library.Utils     import forceString, forceInt, forceDate, forceDateTime, forceStringEx, forceRef

from Orgs.Utils        import getOrgStructureDescendants

def selectSendPlanOrdersClinic(orgStructures, date):
    if orgStructures != [None]:
        whereOrgStruct = u''' AND Person.orgStructure_id IN (%(orgStructures)s) ''' % {'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in orgStructures)}
    else:
        whereOrgStruct = ''
    stmt = u'''
            SELECT outRef.number as referralNumber,
            Event.execDate as referralDate,
            Event.order as formMedicalCare,
            orgIn.infisCode as orgInInfisCode,
            orgOut.infisCode as orgOutInfisCode,
            rbPolicyKind.code as policyKindCode,
            ClientPolicy.serial as policySerial,
            ClientPolicy.number as policyNumber,
            orgIns.infisCode as orgInsInfisCode,
            orgInsKLADR.OCATD as orgInsArea,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.sex,
            Client.birthDate,
            ClientContact.contact,
            rbContactType.name as contactName,
            ClientDocument.serial as documentSerial,
            ClientDocument.number as documentNumber,
            rbDocumentType.regionalCode as documentType,
            Diagnosis.MKB,
            rbHospitalBedProfile.code as hospitalBedCode,
            rbOrgStructureProfile.regionalCode as orgStructureCode,
            Person.regionalCode as personCode,
            planningAction.plannedEndDate
            FROM Event
            INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
            INNER JOIN Event_OutgoingReferral as outRef ON outRef.master_id = Event.id AND outRef.deleted = 0
            LEFT JOIN Referral ON Referral.id = Event.referral_id AND Referral.deleted = 0
            LEFT JOIN Organisation as orgIn ON orgIn.id = Referral.relegateOrg_id AND orgIn.deleted = 0
            LEFT JOIN Organisation as orgOut ON orgOut.id = outRef.org_id AND orgOut.deleted = 0
            LEFT JOIN rbOrgStructureProfile ON outRef.orgStructureProfile_id = rbOrgStructureProfile.id
            LEFT JOIN rbHospitalBedProfile ON outRef.hospitalBedProfile_id = rbHospitalBedProfile.id

            LEFT JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.deleted = 0 AND ClientPolicy.id = (SELECT MAX(cpTemp.id)
                                                                                                                             FROM ClientPolicy as cpTemp
                                                                                                                              WHERE cpTemp.client_id = Client.id AND cpTemp.deleted = 0)
            LEFT JOIN rbPolicyKind ON ClientPolicy.policyKind_id = rbPolicyKind.id
            LEFT JOIN Organisation as orgIns ON orgIns.id = ClientPolicy.insurer_id AND orgIns.deleted = 0
            LEFT JOIN kladr.KLADR as orgInsKLADR ON orgInsKLADR.CODE = orgIns.area
            LEFT JOIN ClientContact ON ClientContact.client_id = Client.id AND ClientContact.deleted = 0 AND ClientContact.id = (SELECT MAX(ccTemp.id)
                                                                                                                             FROM ClientContact as ccTemp
                                                                                                                              WHERE ccTemp.client_id = Client.id AND ccTemp.deleted = 0)
            LEFT JOIN rbContactType ON rbContactType.id = ClientContact.contactType_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND ClientDocument.deleted = 0 AND ClientDocument.id = (SELECT MAX(cdTemp.id)
                                                                                                                             FROM ClientDocument as cdTemp
                                                                                                                              WHERE cdTemp.client_id = Client.id AND cdTemp.deleted = 0)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
            INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN (1, 2)
            INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN ActionType as planningAT ON planningAT.flatCode = 'planning' AND planningAT.deleted = 0
            LEFT JOIN Action as planningAction ON planningAction.event_id = Event.id AND planningAction.actionType_id = planningAT.id AND planningAction.deleted = 0
            LEFT JOIN Person ON Person.id = Event.execPerson_id AND Person.deleted = 0
            WHERE Event.deleted = 0 AND DATE(Event.setDate) >= DATE('%(date)s') %(whereOrgStruct)s
            ORDER BY referralDate
    ''' % {'date': forceString(date.toString(Qt.ISODate)),
           'whereOrgStruct': whereOrgStruct}
    return QtGui.qApp.db.query(stmt)

def selectSendFactOrdersHospital(orgStructures, date):
    if orgStructures != [None]:
        whereOrgStruct = u''' AND OrgStructure.id IN (%(orgStructures)s) ''' % {'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in orgStructures)}
    else:
        whereOrgStruct = ''
    stmt = u'''
            SELECT Referral.number as referralNumber,
            Referral.date as referralDate,
            Event.order as formMedicalCare,
            orgIn.infisCode as orgInInfisCode,
            orgOut.infisCode as orgOutInfisCode,
            Event.setDate,
            rbPolicyKind.code as policyKindCode,
            ClientPolicy.serial as policySerial,
            ClientPolicy.number as policyNumber,
            orgIns.infisCode as orgInsInfisCode,
            orgInsKLADR.OCATD as orgInsArea,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.sex,
            Client.birthDate,
            ClientContact.contact,
            rbContactType.name as contactName,
            ClientDocument.serial as documentSerial,
            ClientDocument.number as documentNumber,
            rbDocumentType.regionalCode as documentType,
            rbHospitalBedProfile.code as hospitalBedCode,
            OrgStructure.code as orgStructureCode,
            Event.externalId
            FROM Event
            INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
            INNER JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id AND rbEventTypePurpose.code = 8
            INNER JOIN ActionType as MovingAT ON MovingAT.flatCode = 'moving' AND MovingAT.deleted = 0
            INNER JOIN Referral ON Referral.id = Event.referral_id AND Referral.deleted = 0
            LEFT JOIN Organisation as orgIn ON orgIn.id = Referral.relegateOrg_id AND orgIn.deleted = 0
            LEFT JOIN Organisation as orgOut ON orgOut.id = Event.outgoingOrg_id AND orgOut.deleted = 0
            LEFT JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.deleted = 0 AND ClientPolicy.id = (SELECT MAX(cpTemp.id)
                                                                                                                             FROM ClientPolicy as cpTemp
                                                                                                                              WHERE cpTemp.client_id = Client.id AND cpTemp.deleted = 0)
            LEFT JOIN rbPolicyKind ON ClientPolicy.policyKind_id = rbPolicyKind.id
            LEFT JOIN Organisation as orgIns ON orgIns.id = ClientPolicy.insurer_id AND orgIns.deleted = 0
            LEFT JOIN kladr.KLADR as orgInsKLADR ON orgInsKLADR.CODE = orgIns.area
            LEFT JOIN ClientContact ON ClientContact.client_id = Client.id AND ClientContact.deleted = 0 AND ClientContact.id = (SELECT MAX(ccTemp.id)
                                                                                                                             FROM ClientContact as ccTemp
                                                                                                                              WHERE ccTemp.client_id = Client.id AND ccTemp.deleted = 0)
            LEFT JOIN rbContactType ON rbContactType.id = ClientContact.contactType_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND ClientDocument.deleted = 0 AND ClientDocument.id = (SELECT MAX(cdTemp.id)
                                                                                                                             FROM ClientDocument as cdTemp
                                                                                                                              WHERE cdTemp.client_id = Client.id AND cdTemp.deleted = 0)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN Action as actHosp ON  actHosp.deleted = 0 AND actHosp.id = (SELECT MAX(aHTemp.id)
                                                                                     FROM Action AS aHTemp
                                                                                     WHERE aHTemp.event_id = Event.id AND aHTemp.actionType_id = MovingAT.id AND aHTemp.deleted = 0)

            LEFT JOIN ActionPropertyType aptHB ON aptHB.actionType_id = MovingAT.id AND aptHB.typeName = 'HospitalBed' AND aptHB.deleted = 0
            LEFT JOIN ActionProperty as apHB ON apHB.action_id = actHosp.id AND apHB.deleted = 0 AND apHB.type_id = aptHB.id
            LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = apHB.id
            LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
            LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id
            LEFT JOIN ActionPropertyType aptOS ON aptOS.actionType_id = MovingAT.id AND aptOS.name LIKE 'Отделение пребывания' AND aptOS.deleted = 0
            LEFT JOIN ActionProperty as apOS ON apOS.action_id = actHosp.id AND apOS.deleted = 0 AND apOS.type_id = aptOS.id
            LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = apOS.id
            LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value AND OrgStructure.deleted = 0
            WHERE Event.deleted = 0 AND DATE(Event.setDate) >= DATE('%(date)s') %(whereOrgStruct)s
            ORDER BY referralDate
    ''' % {'date': forceString(date.toString(Qt.ISODate)),
           'whereOrgStruct': whereOrgStruct}
    return QtGui.qApp.db.query(stmt)

def selectSendOrdersHospitalUrgently(orgStructures, date):
    if orgStructures != [None]:
        whereOrgStruct = u''' AND OrgStructure.id IN (%(orgStructures)s) ''' % {'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in orgStructures)}
    else:
        whereOrgStruct = ''
    stmt = u'''
            SELECT orgCur.infisCode as orgCurInfisCode,
            Event.setDate,
            rbPolicyKind.code as policyKindCode,
            ClientPolicy.serial as policySerial,
            ClientPolicy.number as policyNumber,
            orgIns.infisCode as orgInsInfisCode,
            orgInsKLADR.OCATD as orgInsArea,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.sex,
            Client.birthDate,
            ClientContact.contact,
            rbContactType.name as contactName,
            ClientDocument.serial as documentSerial,
            ClientDocument.number as documentNumber,
            rbDocumentType.regionalCode as documentType,
            rbHospitalBedProfile.code as hospitalBedCode,
            OrgStructure.code as orgStructureCode,
            Event.externalId
            FROM Event
            INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
            INNER JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id AND rbEventTypePurpose.code = 8
            INNER JOIN ActionType as MovingAT ON MovingAT.flatCode = 'moving' AND MovingAT.deleted = 0
            LEFT JOIN Organisation as orgCur ON orgCur.id = Event.org_id AND orgCur.deleted = 0
            LEFT JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.deleted = 0 AND ClientPolicy.id = (SELECT MAX(cpTemp.id)
                                                                                                                             FROM ClientPolicy as cpTemp
                                                                                                                              WHERE cpTemp.client_id = Client.id AND cpTemp.deleted = 0)
            LEFT JOIN rbPolicyKind ON ClientPolicy.policyKind_id = rbPolicyKind.id
            LEFT JOIN Organisation as orgIns ON orgIns.id = ClientPolicy.insurer_id AND orgIns.deleted = 0
            LEFT JOIN kladr.KLADR as orgInsKLADR ON orgInsKLADR.CODE = orgIns.area
            LEFT JOIN ClientContact ON ClientContact.client_id = Client.id AND ClientContact.deleted = 0 AND ClientContact.id = (SELECT MAX(ccTemp.id)
                                                                                                                             FROM ClientContact as ccTemp
                                                                                                                              WHERE ccTemp.client_id = Client.id AND ccTemp.deleted = 0)
            LEFT JOIN rbContactType ON rbContactType.id = ClientContact.contactType_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND ClientDocument.deleted = 0 AND ClientDocument.id = (SELECT MAX(cdTemp.id)
                                                                                                                             FROM ClientDocument as cdTemp
                                                                                                                              WHERE cdTemp.client_id = Client.id AND cdTemp.deleted = 0)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN Action as actHosp ON  actHosp.deleted = 0 AND actHosp.id = (SELECT MAX(aHTemp.id)
                                                                                     FROM Action AS aHTemp
                                                                                     WHERE aHTemp.event_id = Event.id AND aHTemp.actionType_id = MovingAT.id AND aHTemp.deleted = 0)

            LEFT JOIN ActionPropertyType aptHB ON aptHB.actionType_id = MovingAT.id AND aptHB.typeName = 'HospitalBed' AND aptHB.deleted = 0
            LEFT JOIN ActionProperty as apHB ON apHB.action_id = actHosp.id AND apHB.deleted = 0 AND apHB.type_id = aptHB.id
            LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = apHB.id
            LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
            LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id
            LEFT JOIN ActionPropertyType aptOS ON aptOS.actionType_id = MovingAT.id AND aptOS.name LIKE 'Отделение пребывания' AND aptOS.deleted = 0
            LEFT JOIN ActionProperty as apOS ON apOS.action_id = actHosp.id AND apOS.deleted = 0 AND apOS.type_id = aptOS.id
            LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = apOS.id
            LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value AND OrgStructure.deleted = 0
            WHERE Event.deleted = 0 AND Event.order = 2 AND DATE(Event.setDate) >= DATE('%(date)s') %(whereOrgStruct)s
            ORDER BY Event.setDate
    ''' % {'date': forceString(date.toString(Qt.ISODate)),
           'whereOrgStruct': whereOrgStruct}
    return QtGui.qApp.db.query(stmt)

def selectSendOrdersLeave(orgStructures, date):
    if orgStructures != [None]:
        whereOrgStruct = u''' AND OrgStructure.id IN (%(orgStructures)s) ''' % {'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in orgStructures)}
    else:
        whereOrgStruct = ''
    stmt = u'''
            SELECT Referral.number as referralNumber,
            Referral.date as referralDate,
            Event.order as formMedicalCare,
            orgCur.infisCode as orgCurInfisCode,
            Event.setDate,
            actLeav.begDate as actLeavBegDate,
            rbPolicyKind.code as policyKindCode,
            ClientPolicy.serial as policySerial,
            ClientPolicy.number as policyNumber,
            orgIns.infisCode as orgInsInfisCode,
            orgInsKLADR.OCATD as orgInsArea,
            Client.lastName,
            Client.firstName,
            Client.patrName,
            Client.sex,
            Client.birthDate,
            ClientContact.contact,
            rbContactType.name as contactName,
            ClientDocument.serial as documentSerial,
            ClientDocument.number as documentNumber,
            rbDocumentType.regionalCode as documentType,
            rbHospitalBedProfile.code as hospitalBedCode,
            OrgStructure.code as orgStructureCode,
            Event.externalId
            FROM Event
            INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
            INNER JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id AND rbEventTypePurpose.code = 8
            INNER JOIN ActionType as LeavedAT ON LeavedAT.flatCode = 'leaved' AND LeavedAT.deleted = 0
            INNER JOIN ActionType as MovingAT ON MovingAT.flatCode = 'moving' AND MovingAT.deleted = 0
            INNER JOIN Action as actLeav ON actLeav.event_id = Event.id AND actLeav.deleted = 0 AND actLeav.actionType_id = LeavedAT.id AND actLeav.deleted = 0
            LEFT JOIN Referral ON Referral.id = Event.referral_id AND Referral.deleted = 0
            LEFT JOIN Organisation as orgCur ON orgCur.id = Event.org_id AND orgCur.deleted = 0
            LEFT JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.deleted = 0 AND ClientPolicy.id = (SELECT MAX(cpTemp.id)
                                                                                                                             FROM ClientPolicy as cpTemp
                                                                                                                              WHERE cpTemp.client_id = Client.id AND cpTemp.deleted = 0)
            LEFT JOIN rbPolicyKind ON ClientPolicy.policyKind_id = rbPolicyKind.id
            LEFT JOIN Organisation as orgIns ON orgIns.id = ClientPolicy.insurer_id AND orgIns.deleted = 0
            LEFT JOIN kladr.KLADR as orgInsKLADR ON orgInsKLADR.CODE = orgIns.area
            LEFT JOIN ClientContact ON ClientContact.client_id = Client.id AND ClientContact.deleted = 0 AND ClientContact.id = (SELECT MAX(ccTemp.id)
                                                                                                                             FROM ClientContact as ccTemp
                                                                                                                              WHERE ccTemp.client_id = Client.id AND ccTemp.deleted = 0)
            LEFT JOIN rbContactType ON rbContactType.id = ClientContact.contactType_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND ClientDocument.deleted = 0 AND ClientDocument.id = (SELECT MAX(cdTemp.id)
                                                                                                                             FROM ClientDocument as cdTemp
                                                                                                                              WHERE cdTemp.client_id = Client.id AND cdTemp.deleted = 0)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN Action as actHosp ON  actHosp.deleted = 0 AND actHosp.id = (SELECT MAX(aHTemp.id)
                                                                                     FROM Action AS aHTemp
                                                                                     WHERE aHTemp.event_id = Event.id AND aHTemp.actionType_id = MovingAT.id AND aHTemp.deleted = 0)

            LEFT JOIN ActionPropertyType aptHB ON aptHB.actionType_id = MovingAT.id AND aptHB.typeName = 'HospitalBed' AND aptHB.deleted = 0
            LEFT JOIN ActionProperty as apHB ON apHB.action_id = actHosp.id AND apHB.deleted = 0 AND apHB.type_id = aptHB.id
            LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = apHB.id
            LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
            LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id
            LEFT JOIN ActionPropertyType aptOS ON aptOS.actionType_id = MovingAT.id AND aptOS.name LIKE 'Отделение пребывания' AND aptOS.deleted = 0
            LEFT JOIN ActionProperty as apOS ON apOS.action_id = actHosp.id AND apOS.deleted = 0 AND apOS.type_id = aptOS.id
            LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = apOS.id
            LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value AND OrgStructure.deleted = 0
            WHERE Event.deleted = 0 AND actLeav.begDate > DATE('%(date)s') %(whereOrgStruct)s
            ORDER BY referralDate
    ''' % {'date': forceString(date.toString(Qt.ISODate)),
           'whereOrgStruct': whereOrgStruct}
    return QtGui.qApp.db.query(stmt)

def selectSendKDInformation(orgStructures, date):
    if orgStructures != [None]:
        whereOrgStruct = u''' AND OrgStructure.id IN (%(orgStructures)s) ''' % {'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in orgStructures)}
    else:
        whereOrgStruct = ''
    #FIXME: добавить проверку подразделения и фильтр по назначению обращения
    stmt = u'''
            SELECT Referral.number as referralNumber,
            Referral.date as referralDate
            FROM Event
            INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0 AND EventType.code = 37
            LEFT JOIN Referral ON Referral.id = Event.referral_id AND Referral.deleted = 0
            WHERE Event.deleted = 0 AND Event.id IS NULL AND actLeav.begDate > DATE('%(date)s') %(whereOrgStruct)s
            ORDER BY referralDate
    ''' % {'date': forceString(date.toString(Qt.ISODate)),
           'whereOrgStruct': whereOrgStruct}
    return QtGui.qApp.db.query(stmt)

class CReferralForHospitalization(QXmlStreamWriter):

    auth = {'07108': ('root',  'vistamed'),
            '07526': ('root1',  'vistamed'),
            '07112': ('root2', 'vistamed')}
    def __init__(self, parent, orgCode, begDatetime):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.orgCode = orgCode
        self.rootOrgStructureId = forceRef(QtGui.qApp.db.translate('OrgStructure', 'infisInternalCode', orgCode, 'id'))
        self.orgStructures = getOrgStructureDescendants(self.rootOrgStructureId)
        self.begDateTime = begDatetime
        self.emptyExport = True
        self.mapExportTypeToFuncs = {1: (selectSendPlanOrdersClinic, self.writeOrderClinic),
                                    2: (selectSendFactOrdersHospital, self.writeOrderHospital),
                                    3: (selectSendOrdersHospitalUrgently, self.writeOrderHospitalUrgently),
                                    5: (selectSendOrdersLeave, self.writeOrderLeaveHospital),
                                    6: (selectSendKDInformation, self.writeKDInformation)}

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)

    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeSend(self, exportType, dateTime):
        default = ('root', 'vistamed')
        self.writeTextElement('username', self.auth.get(self.orgCode, default)[0]) #имя пользователя
        self.writeComment(u'имя пользователя')
        self.writeTextElement('password', self.auth.get(self.orgCode, default)[1]) #пароль
        self.writeComment(u'пароль')
        self.writeTextElement('sendercode', self.orgCode) #код организации отправителя пакета
        self.writeComment(u'код организации отправителя пакета')
        self.writeHighLevel(exportType, dateTime)

    def writeHighLevel(self, exportType, dateTime):
        self.writeStartElement('orderpack') #пакет с данными о сведениях о направлениях на госпитализацию
        self.writeComment(u'пакет с данными о сведениях о направлениях на госпитализацию')
        self.writePackageInformation(dateTime)
        self.writeList(exportType)
        self.writeEndElement()

    def writePackageInformation(self, dateTime):
        self.writeStartElement('p10_packinf') #сведения о пакете
        self.writeComment(u'сведения о пакете')
        self.writeTextElement('p10_pakagedate', dateTime.toString('yyyy-MM-ddThh:mm:ss')) #дата формирования пакета
        self.writeComment(u'дата формирования пакета')
        self.writeTextElement('p11_pakagesender', self.orgCode) #код отправителя пакета
        self.writeComment(u'код отправителя пакета')
        self.writeTextElement('p12_pakageguid', forceString(uuid.uuid4())) #GUID пакета
        self.writeComment(u'GUID пакета')
        #self.writeTextElement('p13_zerrpkg', '') #служебное поле для отображения кода ошибке
        self.writeTextElement('p14_errmsg', '') #служебное поле для отображения сообщения об ошибке
        self.writeComment(u'служебное поле для отображения сообщения об ошибке')
        self.writeEndElement()

    def writeList(self, exportType):
        number = 1
        if exportType == 1:
            self.writeStartElement('p11_ordercliniclist') #данные о направлениях на госпитализацию
            self.writeComment(u'данные о направлениях на госпитализацию')
        elif exportType == 2:
            self.writeStartElement('p11_orderhospitallist') #данные о госпитализациях
            self.writeComment(u'данные о госпитализациях')
        elif exportType == 3:
            self.writeStartElement('p11_orderhospitalurgentlylist') #данные об экстренных госпитализациях
            self.writeComment(u'данные об экстренных госпитализациях')
        elif exportType == 5:
            self.writeStartElement('p11_orderleavehospitallist') #данные о выбывших пациентах
            self.writeComment(u'данные о выбывших пациентах')
        elif exportType == 6:
            self.writeStartElement('p11_kdInformationlist') #данные о свободных койках
            self.writeComment(u'данные о свободных койках')
        # self.writeStartElement('p11_ordercliniclist')
        (selectFunc, writeFunc) = self.mapExportTypeToFuncs.get(exportType, (None, None))
        if selectFunc:
            query = selectFunc(self.orgStructures, self.begDateTime)
            while query.next():
                self.emptyExport = False
                record = query.record()
                writeFunc(record, number)
                number += 1
        self.writeEndElement()

    def writeOrderClinic(self, record, number):
        self.writeStartElement('l10_orcl') #детализированный список сведений о направлениях на госпитализацию
        self.writeComment(u'детализированный список сведений о направлениях на госпитализацию')
        self.writeTextElement('m10_nzap', forceString(number)) #номер записи, уникален в пределах пакета
        self.writeComment(u'номер записи, уникален в пределах пакета')
        self.writeTextElement('m11_ornm', forceString(record.value('referralNumber'))) #номер направления
        self.writeComment(u'номер направления')
        self.writeTextElement('m12_ordt', forceDate(record.value('referralDate')).toString('yyyy-MM-dd') + 'T00:00:00') #дата направления
        self.writeComment(u'дата направления')
        if forceInt(record.value('formMedicalCare')) == 1:
            self.writeTextElement('m13_ortp', '1') #форма оказания медицинской помощи (1 – плановая, 2 – неотложная, 3 - экстренная)
        elif forceInt(record.value('formMedicalCare')) == 6:
            self.writeTextElement('m13_ortp', '2')
        elif forceInt(record.value('formMedicalCare')) == 2:
            self.writeTextElement('m13_ortp', '3')
        self.writeComment(u'форма оказания медицинской помощи (1 – плановая, 2 – неотложная, 3 - экстренная)')
        # else:
        #     self.writeTextElement('m13_ortp', '')
        #в качестве кодов организаций везде используется ИНФИС код
        self.writeTextElement('m14_moscd', forceString(self.orgCode)) #код МО, направившей на госпитализацию
        self.writeComment(u'код МО, направившей на госпитализацию')
        orgOutInfisCode = forceString(record.value('orgOutInfisCode'))
        if orgOutInfisCode:
            self.writeTextElement('m15_modcd', orgOutInfisCode) #код МО, куда направлен пациент
            self.writeComment(u'код МО, куда направлен пациент')
        self.writePerson(16, record) #персональные данные пациента
        self.writeComment(u'персональные данные пациента')
        self.writeTextElement('m18_mkbcd', forceString(record.value('MKB'))) #код диагноза МКБ
        self.writeComment(u'код диагноза МКБ')
        hospitalBedCode = forceString(record.value('hospitalBedCode'))
        if hospitalBedCode:
            self.writeTextElement('m19_kpkcd', hospitalBedCode) #код профиля койки
            self.writeComment(u'код профиля койки')
        orgStructureCode = forceString(record.value('orgStructureCode'))
        if orgStructureCode:
            self.writeTextElement('m20_sccd', orgStructureCode) #код отделения
            self.writeComment(u'код отделения')
        self.writeTextElement('m21_dcnm', forceString(record.value('personCode'))) #код медицинского работника
        self.writeComment(u'код медицинского работника')
        self.writeTextElement('m22_dtph', forceDate(record.value('plannedEndDate')).toString('yyyy-MM-dd')) #плановая дата госпитализации
        self.writeComment(u'плановая дата госпитализации')
        # self.writeTextElement('m23_zerr', '') #служебное поле
        self.writeEndElement()

    def writePerson(self, number, record):
        self.writeStartElement('m' + forceString(number) + '_pr')
        if forceInt(record.value('policyKindCode')) == 1:
            self.writeTextElement('a10_dct', '1') #тип документа, подтверждающего факт страхования по обязательному медицинскому страхованию (1 - Полис ОМС старого образца, 2 - Временное свидетельство, 3 - Полис ОМС единого образца, 4 - Электронный полис ОМС единого образца, 5 - Полис ОМС в составе УЭК)
        elif forceInt(record.value('policyKindCode')) == 2:
            self.writeTextElement('a10_dct', '2')
        elif forceInt(record.value('policyKindCode')) == 3:
            self.writeTextElement('a10_dct', '3')
        self.writeComment(u'тип документа, подтверждающего факт страхования по обязательному медицинскому страхованию (1 - Полис ОМС старого образца, 2 - Временное свидетельство, 3 - Полис ОМС единого образца, 4 - Электронный полис ОМС единого образца, 5 - Полис ОМС в составе УЭК)')
        # else:
        #     self.writeTextElement('a10_dct', '')
        self.writeTextElement('a11_dcs', forceString(record.value('policySerial'))) #серия полиса
        self.writeComment(u'серия полиса')
        self.writeTextElement('a12_dcn', forceString(record.value('policyNumber'))) #номер полиса
        self.writeComment(u'номер полиса')
        self.writeTextElement('a13_smcd', forceString(record.value('orgInsInfisCode'))) #код СМО
        self.writeComment(u'код СМО')
        self.writeTextElement('a14_trcd', forceString(record.value('orgInsArea'))) #код территории страхования
        self.writeTextElement('a15_pfio', forceString(record.value('lastName'))) #фамилия пациента
        self.writeComment(u'фамилия пациента')
        self.writeTextElement('a16_pnm', forceString(record.value('firstName'))) #имя пациента
        self.writeComment(u'имя пациента')
        self.writeTextElement('a17_pln', forceString(record.value('patrName'))) #отчество пациента
        self.writeComment(u'отчество пациента')
        if forceInt(record.value('sex')) == 0:
            self.writeTextElement('a18_ps', u'не определено') #пол
        elif forceInt(record.value('sex')) == 1:
            self.writeTextElement('a18_ps', u'М')
        else:
            self.writeTextElement('a18_ps', u'Ж')
        self.writeComment(u'пол')
        self.writeTextElement('a19_pbd', forceDate(record.value('birthDate')).toString('yyyy-MM-dd') + 'T00:00:00') #дата рождения
        self.writeComment(u'дата рождения')
        self.writeTextElement('a20_pph', forceString(record.value('contactName')) + ' ' + forceString(record.value('contact'))) #контактная информация
        self.writeComment(u'контактная информация')
        self.writeTextElement('a21_ps', forceString(record.value('documentSerial'))) #серия документа удостоверяющего личность
        self.writeComment(u'серия документа удостоверяющего личность')
        self.writeTextElement('a22_pn', forceString(record.value('documentNumber'))) #номер документа удостоверяющего личность
        self.writeComment(u'номер документа удостоверяющего личность')
        self.writeTextElement('a23_dt', forceString(record.value('documentType'))) #тип документа удостоверяющего личность
        self.writeComment(u'тип документа удостоверяющего личность')
        self.writeEndElement()

    def writeOrderHospital(self, record, number):
        self.writeStartElement('l10_orcl') #детализированный список сведений о госпитализациях
        self.writeComment(u'детализированный список сведений о госпитализациях')
        self.writeTextElement('m10_nzap', forceString(number)) #номер записи, уникален в пределах пакета
        self.writeComment(u'номер записи, уникален в пределах пакета')
        self.writeTextElement('m11_ornm', forceString(record.value('referralNumber'))) #номер направления
        self.writeComment(u'номер направления')
        self.writeTextElement('m12_ordt', forceDate(record.value('referralDate')).toString('yyyy-MM-dd') + 'T00:00:00') #дата направления
        self.writeComment(u'дата направления')
        if forceInt(record.value('formMedicalCare')) == 1:
            self.writeTextElement('m13_ortp', '1') #форма оказания медицинской помощи (1 – плановая, 2 – неотложная, 3 - экстренная)
        elif forceInt(record.value('formMedicalCare')) == 6:
            self.writeTextElement('m13_ortp', '2')
        elif forceInt(record.value('formMedicalCare')) == 2:
            self.writeTextElement('m13_ortp', '3')
        self.writeComment(u'форма оказания медицинской помощи (1 – плановая, 2 – неотложная, 3 - экстренная)')
        # else:
        #     self.writeTextElement('m13_ortp', '')
        #в качестве кодов организаций везде используется ИНФИС код
        self.writeTextElement('m14_moscd', forceString(record.value('orgInInfisCode'))) #код МО, направившей на госпитализацию
        self.writeComment(u'код МО, направившей на госпитализацию')
        orgOutInfisCode = forceString(record.value('orgOutInfisCode'))
        if orgOutInfisCode:
            self.writeTextElement('m15_modcd', self.orgCode) #код МО, куда направлен пациент
            self.writeComment(u'код МО, куда направлен пациент')
        self.writeTextElement('m16_dttmfh', forceDateTime(record.value('setDate')).toString('yyyy-MM-ddThh:mm:ss')) #дата и время фактической госпитализации
        self.writeComment(u'дата и время фактической госпитализации')
        self.writePerson(17, record) #персональные данные пациента
        self.writeComment(u'персональные данные пациента')
        hospitalBedCode = forceString(record.value('hospitalBedCode'))
        if hospitalBedCode:
            self.writeTextElement('m18_kpkcd', hospitalBedCode) #код профиля койки
            self.writeComment(u'код профиля койки')
        orgStructureCode = forceString(record.value('orgStructureCode'))
        if orgStructureCode:
            self.writeTextElement('m19_sccd', orgStructureCode) #код отделения
            self.writeComment(u'код отделения')
        self.writeTextElement('m20_crdnum', forceString(record.value('externalId'))) #номер карты стационарного больного
        self.writeComment(u'номер карты стационарного больного')
        self.writeTextElement('m21_mkbcd ', '') #код МКБ приемного отделения
        self.writeComment(u'код МКБ приемного отделения')
        # self.writeTextElement('m22_zerr', '') #служебное поле
        self.writeEndElement()

    def writeOrderHospitalUrgently(self, record, number):
        self.writeStartElement('l10_orcl') #детализированный список сведений об экстренных госпитализациях
        self.writeComment(u'детализированный список сведений об экстренных госпитализациях')
        self.writeTextElement('m10_nzap', forceString(number)) #номер записи, уникален в пределах пакета
        self.writeComment(u'номер записи, уникален в пределах пакета')
        #в качестве кодов организаций везде используется ИНФИС код
        self.writeTextElement('m11_modcd', self.orgCode) #код МО
        self.writeComment(u'код МО')
        self.writeTextElement('m12_dttmfh', forceDateTime(record.value('setDate')).toString('yyyy-MM-ddThh:mm:ss')) #дата и время фактической госпитализации
        self.writeComment(u'дата и время фактической госпитализации')
        self.writePerson(13, record) #персональные данные пациента
        self.writeComment(u'персональные данные пациента')
        hospitalBedCode = forceString(record.value('hospitalBedCode'))
        if hospitalBedCode:
            self.writeTextElement('m14_kpkcd', hospitalBedCode) #код профиля койки
            self.writeComment(u'код профиля койки')
        orgStructureCode = forceString(record.value('orgStructureCode'))
        if orgStructureCode:
            self.writeTextElement('m15_sccd', orgStructureCode) #код отделения
            self.writeComment(u'код отделения')
        self.writeTextElement('m16_crdnum', forceString(record.value('externalId'))) #номер карты стационарного больного
        self.writeComment(u'номер карты стационарного больного')
        self.writeTextElement('m17_mkbcd ', '') #код МКБ приемного отделения
        self.writeComment(u'код МКБ приемного отделения')
        # self.writeTextElement('m18_zerr', '') #служебное поле
        self.writeComment(u'служебное поле')
        self.writeEndElement()

    def writeOrderLeaveHospital(self, record, number):
        self.writeStartElement('l10_orcl') #детализированный список сведений о выбывших пациентах
        self.writeComment(u'детализированный список сведений о выбывших пациентах')
        self.writeTextElement('m10_nzap', forceString(number)) #номер записи, уникален в пределах пакета
        self.writeComment(u'номер записи, уникален в пределах пакета')
        self.writeTextElement('m11_ornm', forceString(record.value('referralNumber'))) #номер направления
        self.writeComment(u'номер направления')
        self.writeTextElement('m12_ordt', forceDate(record.value('referralDate')).toString('yyyy-MM-dd') + 'T00:00:00') #дата направления
        self.writeComment(u'дата направления')
        if forceInt(record.value('formMedicalCare')) == 1:
            self.writeTextElement('m13_ortp', '1') #форма оказания медицинской помощи
        elif forceInt(record.value('formMedicalCare')) == 6:
            self.writeTextElement('m13_ortp', '2')
        elif forceInt(record.value('formMedicalCare')) == 2:
            self.writeTextElement('m13_ortp', '3')
        self.writeComment(u'форма оказания медицинской помощи')
        # else:
        #     self.writeTextElement('m13_ortp', '')
        #в качестве кодов организаций везде используется ИНФИС код
        self.writeTextElement('m14_modcd', self.orgCode) #код МО
        self.writeComment(u'код МО')
        self.writeTextElement('m15_dttmfh', forceDateTime(record.value('setDate')).toString('yyyy-MM-ddThh:mm:ss')) #дата госпитализации
        self.writeComment(u'дата госпитализации')
        self.writeTextElement('m16_dttmlv', forceDateTime(record.value('actLeavBegDate')).toString('yyyy-MM-ddThh:mm:ss')) #дата выбытия
        self.writeComment(u'дата выбытия')
        self.writePerson(17, record) #персональные данные пациента
        self.writeComment(u'персональные данные пациента')
        hospitalBedCode = forceString(record.value('hospitalBedCode'))
        if hospitalBedCode:
            self.writeTextElement('m18_kpkcd', hospitalBedCode) #код профиля койки
            self.writeComment(u'код профиля койки')
        orgStructureCode = forceString(record.value('orgStructureCode'))
        if orgStructureCode:
            self.writeTextElement('m19_sccd', orgStructureCode) #код отделения
            self.writeComment(u'код отделения')
        self.writeTextElement('m20_crdnum', forceString(record.value('externalId'))) #номер карты стационарного больного
        self.writeComment(u'номер карты стационарного больного')
        # self.writeTextElement('m21_zerr', '') #служебное поле
        self.writeEndElement()

    def writeKDInformation(self, record, number):
        self.writeStartElement('l10_orcl') #детализированный список сведений о свободных койках
        self.writeComment(u'детализированный список сведений о свободных койках')
        self.writeTextElement('m10_nzap', forceString(number)) #номер записи, уникален в пределах пакета
        self.writeComment(u'номер записи, уникален в пределах пакета')
        self.writeTextElement('m11_ornm', '') #номер направления
        self.writeComment(u'номер направления')
        self.writeTextElement('m11_indt', '') #дата
        self.writeComment(u'дата')
        self.writeTextElement('m12_mocd', '') #код МО
        self.writeComment(u'код МО')
        self.writeTextElement('m13_bprlist', '') #список данных в разрезе профилей коек
        self.writeComment(u'список данных в разрезе профилей коек')
        # self.writeTextElement('m14_zerr', '') #служебное поле
        self.writeEndElement()

    def writeFileHeader(self, device):
        self._clientsSet = set()
        self.setDevice(device)

    def writeFileFooter(self):
        pass
        #self.writeEndElement()

# *****************************************************************************************

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Export referrals for hospitalization in Krasnodar area.')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-t', dest='datetime', default=None)
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-D', dest='dir', default=os.getcwd())
    parser.add_argument('-T', dest='exportType')
    parser.add_argument('-c', dest='orgCode', default='07526')
    args = vars(parser.parse_args(sys.argv[1:]))
    exportType = forceInt(args['exportType'])

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)
    if not args['exportType'] or exportType not in (1, 2, 3, 5, 6):
        print 'Error: you should specify correct export type'
        sys.exit(-3)
    if not args['orgCode']:
        print 'Error: you should specify organisation ID'
        sys.exit(-5)

    app = QtCore.QCoreApplication(sys.argv)
    dateTime = QDateTime.currentDateTime()
    begDateTime = args['datetime']
    begDateTime = QDateTime.fromString(begDateTime, 'yyyy-MM-ddTHH:mm:ss') if begDateTime else QDateTime.currentDateTime() # QDateTime.currentDateTime().addSecs(-60)
    if not (begDateTime is None or begDateTime.isValid()):
        print 'Error: incorrect base datetime.'
        sys.exit(-4)

    connectionInfo = {
                          'driverName' : 'MYSQL',
                          'host' : args['host'],
                          'port' : args['port'],
                          'database' : args['database'],
                          'user' : args['user'],
                          'password' : args['password'],
                          'connectionName' : 'HospRefs',
                          'compressData' : True,
                          'afterConnectFunc' : None
                    }

    db = connectDataBaseByInfo(connectionInfo)
    QtGui.qApp.db = db

    if exportType == 1:
        refName = u'SendPlanOrdersClinic_%s'
    elif exportType == 2:
        refName = u'SendFactOrdersHospital_%s'
    elif exportType == 3:
        refName = u'SendOrdersHospitalUrgently_%s'
    elif exportType == 5:
        refName = u'SendOrdersLeave_%s'
    elif exportType == 6:
        refName = u'SendKDInformation_%s'
    name = u'ReferralForHospitalization_%s.xml' % refName

    fileName = name % (dateTime.toString('yyMMddThhmmss.zzz'))
    fullFileName = os.path.join(forceStringEx(args['dir']), fileName)
    outFile = QtCore.QFile(fullFileName)
    outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
    exporter = CReferralForHospitalization(None, args['orgCode'], begDateTime)
    exporter.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
    exporter.writeFileHeader(outFile)
    exporter.writeSend(exportType, dateTime)
    exporter.writeFileFooter()
    outFile.close()

    if exporter.emptyExport:
        os.remove(fullFileName)

if __name__ == '__main__':
    main()