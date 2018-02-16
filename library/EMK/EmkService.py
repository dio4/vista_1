# -*- coding: utf-8 -*-
import base64
import logging
import sys

from suds import TypeNotFound, WebFault
from suds.cache import DocumentCache
from suds.client import Client

import config
import library.LoggingModule.Logger
from Events.ActionInfo import CActionInfo
from Events.EventInfo import CEventInfo
from Registry.Utils import CClientInfo
from Utils import *
from library.EpicrisExchange.EpicrisExchange import getEpicrisByAction, getEpicrisIdListByEventId, getHtmlbyXML
from library.PrintInfo import CInfoContext
from library.PrintTemplates import compileAndExecTemplate, getTemplate
from library.Utils import forceDateTuple, forceInt, forceDecimal
from library.constants import *

__author__ = 'skkachaev (skkachaev@gmail.com)'
__version__ = '2.12.3'


class Service(object):
    def __init__(self, EMK_WSDL_URL=config.EMK_WSDL_URL, PIX_WSDL_URL=config.PIX_WSDL_URL, GUID=config.KEY_TOKEN,
                 idLPU=None):

        self.emk = Client(EMK_WSDL_URL)
        self.emk.set_options(cache=DocumentCache())

        self.pix = Client(PIX_WSDL_URL)
        self.pix.set_options(cache=DocumentCache())

        self.db = QtGui.qApp.db
        self.MED_DOC_TYPES_LIST = [[medType, forceInt(self.db.translate('rbIEMKDocument', 'code', medType, 'applicability'))]
                              for medType in MED_DOC_TYPES_LIST]

        self.logger = logging.getLogger('suds.client')
        self.GUID = GUID
        self.idLPU = idLPU
        self.orgStructureIdLPU = None

    def logExceptionExtra(self, e, extra):
        u"""
        До версии 2.7.7 logger.exception() не принимает kw-аргументы в отличии от info, debug, etc.
        https://docs.python.org/release/2.7.7/library/logging.html#logging.Logger.exception
        """
        if sys.version_info >= (2, 7, 7):
            self.logger.exception(e, extra=extra)
        else:
            self.logger.debug(e, extra=extra)

    # noinspection PyUnresolvedReferences
    def getDoctorDocument(self, snils):
        Document = self.emk.factory.create('ns3:ArrayOfIdentityDocument')
        Document.IdentityDocument = [self.emk.factory.create('ns3:IdentityDocument')]
        Document.IdentityDocument[0].DocN = snils
        Document.IdentityDocument[0].IdDocumentType = 223
        Document.IdentityDocument[0].ProviderName = u'ПФР'
        return Document

    def sendClient(self, clientId):
        logExtra = {'client_id': clientId}

        clientRecord = self.db.getRecordEx(stmt=CLIENT_STMT % clientId)
        if clientRecord is None:
            self.logger.error(u'Клиент с id == %i не найден или помечен, как удалённый' % clientId,
                              extra=logExtra)
            return False

        client = self.pix.factory.create('ns0:PatientDto')

        client.BirthDate = forceDateTuple(clientRecord.value('BirthDate'))
        client.FamilyName = forceStringEx(clientRecord.value('FamilyName'))
        client.GivenName = forceStringEx(clientRecord.value('GivenName'))
        client.MiddleName = forceStringEx(clientRecord.value('MiddleName'))
        client.IdPatientMIS = forceStringEx(clientRecord.value('IdPatientMIS'))
        client.Sex = forceRef(clientRecord.value('Sex'))
        client.IdBloodType = forceRef(clientRecord.value('IdBloodType'))

        clientSocStatusRecord = self.db.getRecordEx(stmt=CLIENT_SOC_STATUS_STMT % clientId)
        if clientSocStatusRecord:
            client.SocialGroup = forceRef(clientSocStatusRecord.value('SocialGroup'))
            client.SocialStatus = forceStringEx(clientSocStatusRecord.value('SocialStatus'))

        clientDocumentRecordList = self.db.getRecordList(stmt=CLIENT_DOCUMENTS_STMT.format(clientId=clientId))
        if clientDocumentRecordList:
            client.Documents = self.pix.factory.create('ns0:ArrayOfDocumentDto')
            client.Documents.DocumentDto = []
            for docRecord in clientDocumentRecordList:
                if not forceStringEx(docRecord.value('ProviderName')):
                    continue  # не заполнено
                doc = self.pix.factory.create('ns0:DocumentDto')
                doc.IdDocumentType = forceRef(docRecord.value('IdDocumentType'))
                doc.DocS = forceStringEx(docRecord.value('DocS')).replace(' ', '').replace('\t', '')
                doc.DocN = forceStringEx(docRecord.value('DocN')).replace(' ', '').replace('\t', '')
                if forceDateTuple(docRecord.value('ExpiredDate')):
                    doc.ExpiredDate = forceDateTuple(docRecord.value('ExpiredDate'))
                if forceDateTuple(docRecord.value('IssuedDate')):
                    doc.IssuedDate = forceDateTuple(docRecord.value('IssuedDate'))
                doc.ProviderName = forceStringEx(docRecord.value('ProviderName'))
                doc.IdProvider = forceStringEx(docRecord.value('IdProvider')) or None
                client.Documents.DocumentDto.append(doc)

        clientAddressRecordList = self.db.getRecordList(stmt=CLIENT_ADDRESSES_STMT % clientId)
        if clientAddressRecordList:
            client.Addresses = self.pix.factory.create('ns0:ArrayOfAddressDto')
            client.Addresses.AddressDto = []
            for addrRecord in clientAddressRecordList:
                if not forceStringEx(addrRecord.value('StringAddress')):
                    continue  # не заполнено
                addr = self.pix.factory.create('ns0:AddressDto')
                addr.IdAddressType = forceRef(addrRecord.value('IdAddressType'))
                addr.StringAddress = forceStringEx(addrRecord.value('StringAddress'))
                client.Addresses.AddressDto.append(addr)

        clientContactRecordList = self.db.getRecordList(stmt=CLIENT_CONTACTS_STMT % clientId)
        if clientContactRecordList:
            client.Contacts = self.pix.factory.create('ns0:ArrayOfContactDto')
            client.Contacts.ContactDto = []
            for contactRecord in clientContactRecordList:
                if not forceStringEx(contactRecord.value('ContactValue')):
                    continue  # не заполнено
                contact = self.pix.factory.create('ns0:ContactDto')
                contact.IdContactType = forceRef(contactRecord.value('IdContactType'))
                contact.ContactValue = forceStringEx(contactRecord.value('ContactValue'))
                client.Contacts.ContactDto.append(contact)

        clientWorkRecord = self.db.getRecordEx(stmt=CLIENT_WORKS_STMT % clientId)
        if clientWorkRecord and forceStringEx(clientWorkRecord.value('CompanyName')):
            client.Job = self.pix.factory.create('ns0:JobDto')
            client.Job.CompanyName = forceStringEx(clientWorkRecord.value('CompanyName'))
            client.Job.Position = forceStringEx(clientWorkRecord.value('Position'))

        # TODO: skkachaev: Здесь должно быть заполнение льгот, но wsdl очень сильно отличается от доков API в этой части

        currLogStatus = getClientLogStatus(self.db, clientId)
        try:
            result = self.pix.service.AddPatient(self.GUID,
                                                 self.orgStructureIdLPU if self.orgStructureIdLPU is not None
                                                 else getIdLPU(self.db, self.idLPU, QtGui.qApp.currentOrgStructureId()),
                                                 client)
            # result = self.pix.service.AddPatient(self.GUID, getIdLPU(self.db, self.idLPU, QtGui.qApp.currentOrgStructureId()), client)
            setClientLogStatus(self.db, clientId, LogStatus.Success)
            self.logger.debug(u'Пациент с id={0} успешно отправлен'.format(clientId))
            return True

        except ValueError as err:
            self.logger.error(err.message, extra=logExtra)
            return False

        except WebFault as err:
            errList = err.fault.detail.ArrayOfRequestFault.RequestFault if hasattr(err.fault.detail,
                                                                                   'ArrayOfRequestFault') \
                else [err.fault.detail.RequestFault]
            if hasattr(errList[0], 'ErrorCode') and errList[0].ErrorCode == ERR_DUPLICATE_CLIENT:
                setClientLogStatus(self.db, clientId, LogStatus.Success)
                self.logger.debug(u'Пациент с id={0} успешно отправлен'.format(clientId))
                return True
            else:
                if currLogStatus != LogStatus.Failed:
                    setClientLogStatus(self.db, clientId, LogStatus.Failed)
                self.logger.error(errList, extra=logExtra)
            return False

        except Exception as e:
            self.logger.error(e, extra=logExtra)
            return False

    def fillBaseEvent(self, baseEventRecord, event):
        """
        :param baseEventRecord: 
        :type baseEventRecord: PyQt4.QtSql.QSqlRecord
        """
        event.OpenDate = forceDateTuple(baseEventRecord.value('OpenDate'))
        event.CloseDate = forceDateTuple(baseEventRecord.value('CloseDate'))
        event.HistoryNumber = forceStringEx(baseEventRecord.value('HistoryNumber'))
        event.IdCaseMis = forceStringEx(baseEventRecord.value('IdCaseMis'))
        event.IdCaseAidType = forceRef(baseEventRecord.value('IdCaseAidType'))
        event.IdPaymentType = forceRef(baseEventRecord.value('IdPaymentType'))
        event.Confidentiality = forceRef(baseEventRecord.value('Confidentiality'))
        event.DoctorConfidentiality = forceRef(baseEventRecord.value('DoctorConfidentiality'))
        event.CuratorConfidentiality = forceRef(baseEventRecord.value('CuratorConfidentiality'))
        event.IdLpu = forceStringEx(baseEventRecord.value('IdLpu'))
        event.IdCaseResult = forceRef(baseEventRecord.value('IdCaseResult'))
        event.IdPatientMis = forceStringEx(baseEventRecord.value('IdPatientMis'))
        event.Comment = 'No comments'

        event.DoctorInCharge = self.getMedicalStaff(record=baseEventRecord)

        event.Authenticator = self.emk.factory.create('ns3:Participant')
        event.Authenticator.Doctor = self.getMedicalStaff(record=baseEventRecord)
        event.Authenticator.IdRole = forceRef(baseEventRecord.value('IdRole'))

        event.Author = self.emk.factory.create('ns3:Participant')
        event.Author.Doctor = self.getMedicalStaff(record=baseEventRecord)
        event.Author.IdRole = forceRef(baseEventRecord.value('IdRole'))

        event.LegalAuthenticator = self.emk.factory.create('ns3:Participant')
        event.LegalAuthenticator.Doctor = self.getMedicalStaff(record=baseEventRecord)
        event.LegalAuthenticator.IdRole = forceRef(baseEventRecord.value('IdRole'))

        isHospWithParent = forceRef(baseEventRecord.value('isHospWithParent'))
        if isHospWithParent:
            guardianRecord = self.db.getRecordEx(stmt=GUARD_STMT % forceRef(baseEventRecord.value('IdPatientMis')))
            if guardianRecord is not None:
                event.Guardian = self.emk.factory.create('ns3:Guardian')
                event.Guardian.Person = self.getPersonWithIdentity(record=guardianRecord)
                event.Guardian.IdRelationType = forceRef(guardianRecord.value('IdRelationType'))

                guardDocList = self.db.getRecordList(
                    stmt=CLIENT_DOCUMENTS_STMT.format(clientId=event.Guardian.Person.IdPersonMis))
                if guardDocList:
                    event.Guardian.UnderlyingDocument = forceStringEx(guardDocList[-1].value('IdDocumentType'))
                else:
                    event.Guardian.UnderlyingDocument = u'Нет документа'  # TODO: skkachaev: Что-то передавать надо
        else:
            event.Guardian = None

    def fillStatEvent(self, event, eventId):
        statEventRecord = self.db.getRecordEx(stmt=STAT_EVENT_STMT % eventId)
        if statEventRecord is None:
            return False

        eventDeliveryRecord = self.db.getRecordEx(stmt=EVENT_DELIVERY_STMT % eventId)
        eventIntoxicationRecord = self.db.getRecordEx(stmt=EVENT_INTOXICATION_STMT % eventId)
        eventAdmissionRecord = self.db.getRecordEx(stmt=EVENT_ADMISSION_STMT % eventId)
        eventDiseaseRecord = self.db.getRecordEx(stmt=EVENT_DISEASE_STMT % eventId)
        eventTransportRecord = self.db.getRecordEx(stmt=EVENT_TRANSPORT_STMT % eventId)
        eventChannelRecord = self.db.getRecordEx(stmt=EVENT_CHANNEL_STMT % eventId)
        eventRW1Recrod = self.db.getRecordEx(stmt=EVENT_RW1_STMT % eventId)
        eventAIDSRecord = self.db.getRecordEx(stmt=EVENT_AIDS_STMT % eventId)

        event.IdRepetition = forceRef(statEventRecord.value('IdRepetition'))
        event.HospitalizationOrder = forceRef(statEventRecord.value('HospitalizationOrder'))
        event.HospResult = forceRef(statEventRecord.value('HospResult'))

        if eventDeliveryRecord:
            event.DeliveryCode = forceStringEx(eventDeliveryRecord.value('DeliveryCode'))
        if eventIntoxicationRecord:
            event.IdIntoxicationType = forceRef(eventIntoxicationRecord.value('IdIntoxicationType'))
        if eventAdmissionRecord:
            event.IdPatientConditionOnAdmission = forceRef(eventAdmissionRecord.value('IdPatientConditionOnAdmission'))
        if eventDiseaseRecord:
            event.IdTypeFromDiseaseStart = forceRef(eventDiseaseRecord.value('IdTypeFromDiseaseStart'))
        if eventTransportRecord:
            event.IdTransportIntern = forceRef(eventTransportRecord.value('IdTransportIntern'))
        if eventChannelRecord:
            event.IdHospChannel = forceRef(eventChannelRecord.value('IdHospChannel'))
        if eventRW1Recrod:
            event.RW1Mark = forceStringEx(eventRW1Recrod.value('RW1Mark')) == u'да'
        if eventAIDSRecord:
            event.AIDSMark = forceStringEx(eventAIDSRecord.value('AIDSMark')) == u'да'

        return True

    def fillAmbEvent(self, event, eventId):
        ambEventRecord = self.db.getRecordEx(stmt=AMB_EVENT_STMT % eventId)
        if ambEventRecord is None:
            return False

        event.IdCasePurpose = forceRef(ambEventRecord.value('IdCasePurpose'))
        event.IdCaseType = forceRef(ambEventRecord.value('IdCaseType'))
        event.IdAmbResult = forceRef(ambEventRecord.value('IdAmbResult'))
        event.IsActive = forceStringEx(ambEventRecord.value('IsActive'))
        return True

    def fillStatEventSteps(self, event, eventId):
        statStepRecordsList = self.db.getRecordList(stmt=STAT_STEPS_STMT % eventId)
        if not statStepRecordsList:
            return False

        event.Steps = self.emk.factory.create('ns9:ArrayOfStepStat')
        event.Steps.StepStat = []
        for r in statStepRecordsList:
            step = self.emk.factory.create('ns9:StepStat')
            step.DateStart = forceDateTuple(r.value('DateStart'))
            step.DateEnd = forceDateTuple(r.value('DateEnd'))
            step.IdPaymentType = forceRef(r.value('IdPaymentType'))
            step.Doctor = self.getMedicalStaff(record=r)
            step.IdStepMis = forceStringEx(r.value('IdStepMis'))
            step.HospitalDepartmentName = forceStringEx(r.value('HospitalDepartmentName'))
            step.IdHospitalDepartment = forceStringEx(r.value('IdHospitalDepartment'))
            step.IdRegimen = forceRef(r.value('IdRegimen'))
            step.WardNumber = forceStringEx(r.value('WardNumber'))
            step.BedNumber = forceStringEx(r.value('BedNumber'))
            step.BedProfile = forceRef(r.value('BedProfile'))
            step.DaySpend = forceRef(r.value('DaySpend'))

            event.Steps.StepStat.append(step)

        return True

    def fillAmbEventSteps(self, event, eventId):
        def addMedRecord(currentStep, medRecord):
            if hasattr(currentStep, 'MedRecords'):
                currentStep.MedRecords.MedRecord.append(medRecord)
            else:
                currentStep.MedRecords = self.emk.factory.create('ns6:ArrayOfMedRecord')
                currentStep.MedRecords.MedRecord = [medRecord]

        ambStepRecordsList = self.db.getRecordList(stmt=VISIT_AMB_STEPS_STMT % eventId)
        if not ambStepRecordsList:
            return False

        event.Steps = self.emk.factory.create('ns9:ArrayOfStepAmb')
        event.Steps.StepAmb = []
        for r in ambStepRecordsList:
            step = self.emk.factory.create('ns9:StepAmb')
            step.DateStart = forceDateTuple(r.value('DateStart'))
            step.DateEnd = forceDateTuple(r.value('DateEnd'))
            step.IdPaymentType = forceRef(r.value('IdPaymentType'))
            step.Doctor = self.getMedicalStaff(record=r)
            step.IdStepMis = forceStringEx(r.value('IdStepMis'))
            step.IdVisitPlace = forceRef(r.value('IdVisitPlace'))
            step.IdVisitPurpose = forceRef(r.value('IdVisitPurpose'))

            serviceRec = getVisitServiceRecord(self.db, forceRef(r.value('visitId')))
            if serviceRec:
                service = self.emk.factory.create('ns6:Service')
                service.DateStart = forceDateTuple(serviceRec.value('DateStart'))
                service.DateEnd = forceDateTuple(serviceRec.value('DateEnd'))
                service.IdServiceType = forceString(serviceRec.value('IdServiceType'))
                service.ServiceName = forceString(serviceRec.value('ServiceName'))
                service.PaymentInfo = self.emk.factory.create('ns6:PaymentInfo')
                service.PaymentInfo.HealthCareUnit = forceString(serviceRec.value('HealthCareUnit'))
                service.PaymentInfo.IdPaymentType = forceString(serviceRec.value('IdPaymentType'))
                service.PaymentInfo.PaymentState = forceInt(serviceRec.value('PaymentState'))
                service.PaymentInfo.Quantity = forceInt(serviceRec.value('Quantity'))
                service.PaymentInfo.Tariff = forceDecimal(serviceRec.value('Tariff'))
                service.Performer = self.emk.factory.create('ns6:Performer')
                service.Performer.Doctor = self.getMedicalStaff(record=r)
                service.Performer.IdRole = 3

                # addMedRecord(step, service)

            drugRecipeRecList = getDrugRecipeRecordList(self.db, eventId)
            for recipeRec in drugRecipeRecList:
                recipe = self.emk.factory.create('ns835:AppointedMedication')
                recipe.AnatomicTherapeuticChemicalClassification = forceString(recipeRec.value('ATCC'))
                recipe.CourseDose = self.emk.factory.create('ns835:CourseDose')
                recipe.CourseDose.IdUnit = forceInt(recipeRec.value('CourseDoseIdUnit'))
                recipe.CourseDose.Value = forceDecimal(recipeRec.value('CourseDoseValue'))
                recipe.DayDose = self.emk.factory.create('ns835:DayDose')
                recipe.DayDose.IdUnit = forceInt(recipeRec.value('DayDoseIdUnit'))
                recipe.DayDose.Value = forceDecimal(recipeRec.value('DayDoseValue'))
                recipe.DaysCount = forceInt(recipeRec.value('DaysCount'))
                recipe.Doctor = self.getMedicalStaff(personId=forceInt(recipeRec.value('IdPersonMis')))
                recipe.IssuedDate = forceDateTuple(recipeRec.value('IssuedDate'))
                recipe.MedicineIssueType = forceString(recipeRec.value('MedicineIssueType'))
                recipe.MedicineName = forceString(recipeRec.value('MedicineName'))
                recipe.MedicineType = forceInt(recipeRec.value('MedicineType'))
                recipe.MedicineUseWay = forceInt(recipeRec.value('MedicineUseWay'))
                recipe.Number = forceString(recipeRec.value('Number'))
                recipe.OneTimeDose = self.emk.factory.create('ns835:OneTimeDose')
                recipe.OneTimeDose.IdUnit = forceInt(recipeRec.value('DayDoseIdUnit'))
                recipe.OneTimeDose.Value = forceDecimal(recipeRec.value('DayDoseValue'))
                recipe.Seria = forceString(recipeRec.value('Seria'))
                addMedRecord(step, recipe)

            event.Steps.StepAmb.append(step)

        return True

    def fillMainDiagnosis(self, event, eventId):
        diagnosisRecord = self.db.getRecordEx(stmt=MAIN_DIAGNOSIS_STMT % eventId)
        if diagnosisRecord is None:
            return False

        event.MedRecords = self.emk.factory.create('ns6:ArrayOfMedRecord')
        event.MedRecords.MedRecord = []

        diagnosis = self.emk.factory.create('ns7:ClinicMainDiagnosis')
        diagnosis.DiagnosisInfo = self.emk.factory.create('ns7:DiagnosisInfo')
        diagnosis.DiagnosisInfo.IdDiseaseType = forceRef(diagnosisRecord.value('IdDiseaseType'))
        diagnosis.DiagnosisInfo.DiagnosedDate = forceDateTuple(diagnosisRecord.value('DiagnosedDate'))
        diagnosis.DiagnosisInfo.IdDiagnosisType = forceRef(diagnosisRecord.value('IdDiagnosisType'))
        diagnosis.DiagnosisInfo.MkbCode = forceStringEx(diagnosisRecord.value('MkbCode'))
        diagnosis.DiagnosisInfo.DiagnosisStage = forceRef(diagnosisRecord.value('DiagnosisStage'))
        diagnosis.DiagnosisInfo.IdDispensaryState = forceRef(diagnosisRecord.value('IdDispensaryState'))
        diagnosis.Doctor = self.getMedicalStaff(record=diagnosisRecord)

        event.MedRecords.MedRecord.append(diagnosis)

        return True

    def fillMedDocument(self, eventId, event, documentCode, html=None):
        clientId = forceRef(self.db.translateEx(table=u'Event', keyCol=u'id', keyVal=eventId, valCol=u'client_id'))
        medRecord = self.db.getRecordEx(stmt=MED_DOCUMENT_STMT % eventId)
        tname = u'Эпикриз'
        if html is None:  # Заполняем документ по шаблонам печати
            medDocumentPrintTemplateId = forceRef(self.db.getIdList(stmt=MED_DOCUMENT_PRINT_TEMPLATE_STMT % documentCode))
            if not medDocumentPrintTemplateId:
                return False
            medDocumentPrintTemplateId = medDocumentPrintTemplateId[0]
            tname, template, tt = getTemplate(medDocumentPrintTemplateId)

            data = {'client': CClientInfo(CInfoContext(), clientId),
                    'event' : CEventInfo(CInfoContext(), eventId)}
            try:
                res = compileAndExecTemplate(template, data)
                html = res[0].encode('utf8')
            except Exception as e:
                self.logExceptionExtra(e, {'event_id': eventId})
                html = ''

        data1 = base64.b64encode(html)
        data2 = base64.b64encode(SIGN_DATA % data1)

        medDocument = self.emk.factory.create('ns8:%s' % documentCode)
        medDocument.CreationDate = forceDateTuple(medRecord.value('CreationDate'))
        medDocument.IdDocumentMis = forceRef(medRecord.value('IdDocumentMis'))
        medDocument.Header = tname
        medDocument.Attachment.Data = data2
        medDocument.Attachment.MimeType = MIME_TYPE
        medDocument.Author = self.getMedicalStaff(record=medRecord)

        if documentCode == 'SickList':
            tempInvRecord = getTempInvalidRecord(self.db, eventId)
            if tempInvRecord:
                medDocument.SickListInfo = self.emk.factory.create('ns8:SickListInfo')
                medDocument.SickListInfo.Number = forceStringEx(tempInvRecord.value('number'))
                medDocument.SickListInfo.DateStart = forceDateTuple(tempInvRecord.value('begDate'))
                medDocument.SickListInfo.DateEnd = forceDateTuple(tempInvRecord.value('endDate'))
                medDocument.SickListInfo.IsPatientTaker = True
            else:
                return False

        elif documentCode == 'DispensaryOne':
            dispensaryInfo = getDispensaryOneInfo(self.db, eventId)
            if dispensaryInfo:
                medDocument.IsGuested = dispensaryInfo['IsGuested']
                medDocument.IsUnderObservation = dispensaryInfo['IsUnderObservation']
                medDocument.HasExpertCareRefferal = dispensaryInfo['HasExtraResearchRefferal']
                medDocument.HasHealthResortRefferal = dispensaryInfo['HasHealthResortRefferal']
                medDocument.HasSecondStageRefferal = dispensaryInfo['HasSecondStageRefferal']
                medDocument.HasPrescribeCure = dispensaryInfo['HasPrescribeCure']
                medDocument.HasExtraResearchRefferal = dispensaryInfo['HasExtraResearchRefferal']
                medDocument.HealthGroup = self.emk.factory.create('ns8:HealthGroup')
                medDocument.HealthGroup.Doctor = self.getMedicalStaff(record=medRecord)
                medDocument.HealthGroup.HealthGroupInfo = self.emk.factory.create('ns8:HealthGroupInfo')
                medDocument.HealthGroup.HealthGroupInfo.IdHealthGroup = dispensaryInfo['IdHealthGroup']
                medDocument.HealthGroup.HealthGroupInfo.Date = forceDateTuple(dispensaryInfo['Date'])
                medDocument.Recommendations = self.getDispensaryOneRecommendations(eventId)
            else:
                return False

        elif documentCode == 'Referral':
            referralRecord = getReferralRecord(self.db, eventId)
            if referralRecord:
                medDocument.IdSourceLpu = forceStringEx(referralRecord.value('IdSourceLpu'))
                medDocument.IdTargetLpu = forceStringEx(referralRecord.value('IdTargetLpu'))
                medDocument.DepartmentHead = self.getMedicalStaff(personId=forceRef(referralRecord.value('personId')))
                medDocument.ReferralInfo = self.emk.factory.create('ns8:ReferralInfo')
                medDocument.ReferralInfo.Reason = forceStringEx(referralRecord.value('Reason'))
                medDocument.ReferralInfo.IdReferralMis = forceStringEx(referralRecord.value('IdReferralMis'))
                medDocument.ReferralInfo.IdReferralType = forceInt(referralRecord.value('IdReferralType'))
                medDocument.ReferralInfo.IssuedDateTime = forceDateTuple(referralRecord.value('IssuedDateTime'))
                medDocument.ReferralInfo.HospitalizationOrder = forceInt(referralRecord.value('HospitalizationOrder'))
                medDocument.ReferralInfo.MkbCode = forceStringEx(referralRecord.value('MkbCode'))
            else:
                return False

        elif documentCode == 'ConsultNote':
            if getEventTypeCode(self.db, eventId) in ('211', '261'):
                return False

        event.MedRecords.MedRecord.append(medDocument)
        return True

    def getDispensaryOneRecommendations(self, eventId):
        recommendations = self.emk.factory.create('ns8:ArrayOfRecommendation')
        recommendations.Recommendation = []

        for rec in getDispensaryOneRecommendationRecords(self.db, eventId):
            actionId = forceRef(rec.value('id'))
            personId = forceRef(rec.value('person_id'))
            templateId = forceRef(rec.value('templateId'))
            endDate = forceDate(rec.value('endDate'))

            try:
                tname, template, tt = getTemplate(templateId)
                data = {
                    'action': CActionInfo(CInfoContext(), actionId)
                }
                res = compileAndExecTemplate(template, data)
                html = res[0].encode('utf8')
            except Exception as e:
                self.logExceptionExtra(e, {'event_id': eventId})
                html = ''

            recommendation = self.emk.factory.create('ns8:Recommendation')
            recommendation.Date = forceDateTuple(endDate)
            recommendation.Doctor = self.getMedicalStaff(personId=personId)
            recommendation.Text = html

            recommendations.Recommendation.append(recommendation)

        return recommendations

    def getPersonWithIdentity(self, record=None, personId=None):
        if record is None:
            record = getMedicalStaffRecord(self.db, personId)

        person = self.emk.factory.create('ns3:PersonWithIdentity')
        person.HumanName = self.emk.factory.create('ns3:HumanName')
        person.HumanName.GivenName = forceStringEx(record.value('GivenName'))
        person.HumanName.MiddleName = forceStringEx(record.value('MiddleName'))
        person.HumanName.FamilyName = forceStringEx(record.value('FamilyName'))
        person.Sex = forceRef(record.value('Sex'))
        person.Birthdate = forceDateTuple(record.value('Birthdate'))
        person.IdPersonMis = forceStringEx(record.value('IdPersonMis'))
        return person

    def getMedicalStaff(self, record=None, personId=None):
        if record is None:
            record = getMedicalStaffRecord(self.db, personId)

        staff = self.emk.factory.create('ns3:MedicalStaff')
        staff.Person = self.getPersonWithIdentity(record=record)
        staff.Person.Documents = self.getDoctorDocument(forceStringEx(record.value('SNILS')))
        staff.IdLpu = forceStringEx(record.value('IdLpu')) or None
        staff.IdSpeciality = forceRef(record.value('IdSpeciality'))
        staff.IdPosition = forceRef(record.value('IdPosition'))
        return staff

    def fillMedDocs(self, eventId, event, isStat, newEpicrisis):
        if newEpicrisis:
            epIdList = getEpicrisIdListByEventId(eventId)
            if not epIdList:
                self.logger.error(u'Случай с id == %i не имеет эпикризов в веб-модуле' % eventId, extra={'event_id': eventId})
                return False
            epId = epIdList[0]
            html = getHtmlbyXML(getEpicrisByAction(epId)).encode('utf8')
            return self.fillMedDocument(eventId, event, 'DischargeSummary', html)
        else:
            for medType, applicability in self.MED_DOC_TYPES_LIST:
                if applicability == 3 or (applicability == 1 and not isStat) or (applicability == 2 and isStat):
                    self.fillMedDocument(eventId, event, medType)

    def sendClientIfNeed(self, eventId):
        clientId = forceRef(self.db.translateEx(table=u'Event', keyCol=u'id', keyVal=eventId, valCol=u'client_id'))
        inLog = forceRef(self.db.getRecordEx(
            stmt=u'SELECT * FROM {logger}.IEMKClientLog WHERE client_id = {clientId} AND status = 2'.format(
                logger=library.LoggingModule.Logger.loggerDbName,
                clientId=clientId)))
        if inLog is None:
            try:
                result = self.sendClient(clientId)
            except Exception as e:
                self.logger.error(e, extra={'client_id': clientId})
                return False
            else:
                return result
        return True

    def sendEvent(self, eventId, newEpicrisis=False):
        logExtra = {'event_id': eventId}

        baseEventRecord = self.db.getRecordEx(stmt=BASE_EVENT_STMT % eventId)
        if baseEventRecord is None:
            self.logger.error(u'Случай с id == %i не найден, не заполнен или помечен, как удалённый' % eventId,
                              extra=logExtra)
            return False

        if not self.sendClientIfNeed(eventId):
            self.logger.error(u'Случай с id == %i не может быть послан, потому что возникла проблема при синхронизации пациента' % eventId,
                              extra=logExtra)
            return False

        isStat = forceRef(baseEventRecord.value('isStat'))

        event = self.emk.factory.create('ns4:CaseStat' if isStat else 'ns4:CaseAmb')
        # noinspection PyTypeChecker
        self.fillBaseEvent(baseEventRecord, event)

        if not self.fillMainDiagnosis(event, eventId):
            self.logger.error(u'В случае с id == %i не найден заключительный диагноз' % eventId, extra=logExtra)
            return False

        self.fillMedDocs(eventId, event, isStat, newEpicrisis)

        if isStat:
            if not self.fillStatEvent(event, eventId):
                self.logger.error(u'Случай с id == %i не найден, не заполнен или помечен, как удалённый' % eventId, extra=logExtra)
                return False

            if not self.fillStatEventSteps(event, eventId):
                self.logger.error(u'В случае с id == %i нет или неправильно заполнены действия поступление' % eventId, extra=logExtra)
                return False
        else:
            if not self.fillAmbEvent(event, eventId):
                self.logger.error(u'Случай с id == %i не найден, не заполнен или помечен, как удалённый' % eventId, extra=logExtra)
                return False

            if not self.fillAmbEventSteps(event, eventId):
                self.logger.error(u'В случае с id == %i нет или неправильно заполнены посещения' % eventId, extra=logExtra)
                return False

        currLogStatus = getEventLogStatus(self.db, eventId)
        try:
            self.emk.service.AddCase(self.GUID, event)
            setEventLogStatus(self.db, eventId, LogStatus.Success)  # 2
            return True

        except WebFault as err:
            errList = err.fault.detail.ArrayOfRequestFault.RequestFault if hasattr(
                err.fault.detail, 'ArrayOfRequestFault') else [err.fault.detail.RequestFault]
            self.logger.error(errList, extra=logExtra)
            if currLogStatus != LogStatus.Failed:
                setEventLogStatus(self.db, eventId, LogStatus.Failed)  # 3
            return False

        except Exception as e:
            self.logger.error(e, extra=logExtra)
            return False

    def test(self):
        print self.emk

    def getNotSentEvents(self, startDate=dateLeftInfinity.toPyDate(), endDate=dateRightInfinity.toPyDate(),
                         maxCount=10000, resend=False, orgStructureId=None, eventTypeId=None):
        tblEvent = self.db.table('Event')
        tblPerson = self.db.table('Person')
        tblIEMKLog = self.db.table(library.LoggingModule.Logger.loggerDbName + '.IEMKEventLog')
        tbl = tblEvent.innerJoin(tblPerson, tblEvent['execPerson_id'].eq(tblPerson['id']))
        tbl = tbl.leftJoin(tblIEMKLog,
                           tblIEMKLog['id'].eqStmt(self.db.selectMax(tblIEMKLog,
                                                                     tblIEMKLog['id'],
                                                                     tblIEMKLog['event_id'].eq(tblEvent['id']))))
        where = [
            tblEvent['isClosed'].eq(1),
            tblEvent['deleted'].eq(0),
            tblEvent['execDate'].between(startDate, endDate)
        ]
        if orgStructureId:
            orgStructureIds = self.db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
            where.append(tblPerson['orgStructure_id'].inlist(orgStructureIds))
        if eventTypeId:
            where.append(tblEvent['eventType_id'].eq(eventTypeId))
        if resend:
            where.append(tblIEMKLog['status'].eq(LogStatus.Failed))  # 3
        else:
            where.append(self.db.joinOr([tblIEMKLog['status'].isNull(),
                                         tblIEMKLog['status'].eq(LogStatus.NotSent)]))  # 0

        return self.db.getDistinctIdList(tbl, tblEvent['id'], where, limit=maxCount)

    def sendEvents(self, startDate=dateLeftInfinity.toPyDate(), endDate=dateRightInfinity.toPyDate(), maxCount=10000,
                   resend=False, eventId=None, newEpicrisis=False, orgStructureId=None, eventTypeId=None):
        if eventId is not None:
            eventIdList = [eventId]
        else:
            eventIdList = self.getNotSentEvents(startDate, endDate, maxCount, resend, orgStructureId, eventTypeId)
        self.orgStructureIdLPU = getIdLPU(self.db, self.idLPU, orgStructureId)

        count = 0
        try:
            self.logger.debug(u'Выгрузка начата: %i случаев к выгрузке', len(eventIdList))
            for eventId in eventIdList:
                try:
                    QtGui.qApp.processEvents()
                    self.logger.debug(u'\n\nВыгрузка случая с id={0}\n'.format(eventId))
                    if self.sendEvent(eventId, newEpicrisis):
                        self.logger.debug(u'Случай с id={0} успешно выгружен'.format(eventId))
                        count += 1

                except TypeNotFound as e:
                    self.logger.debug(u'Service description:\n{0}\n\n'.format(self.emk))
                    self.logExceptionExtra(e, {'event_id': eventId})
                    raise

                except Exception as e:
                    self.logExceptionExtra(e, {'event_id': eventId})
        finally:
            countErrors = len(eventIdList) - count
            self.logger.debug(u'\n\nВыгрузка окончена. Выгружено случаев: {0}{1}.'.format(
                count,
                u', {0} с ошибками'.format(countErrors) if countErrors else u''
            ))


class TextBrowserHandler(logging.Handler):
    def __init__(self, textBrowser, textBrowserDetailed=None):
        u"""
        :param textBrowser: 
        :type textBrowser: PyQt4.QtGui.QTextBrowser.QTextBrowser
        """
        logging.Handler.__init__(self)
        self.textBrowser = textBrowser

    def emit(self, record):
        self.textBrowser.insertPlainText(self.format(record=record).decode('utf-8'))


class ErrorLogTableHandler(logging.Handler):
    def __init__(self, tblErrorLog):
        logging.Handler.__init__(self)
        self._tblErrorLog = tblErrorLog

    def emit(self, record):
        clientId = getattr(record, 'client_id', None)
        eventId = getattr(record, 'event_id', None)
        if clientId or eventId:
            self._tblErrorLog.model().addItem(clientId, eventId, self.format(record).decode('utf-8'))


def loggingConfigure(logToFile, textBrowser=None, textBrowserDetailed=None, tblError=None, handlerClass=TextBrowserHandler):
    emklogger = logging.getLogger('suds.client')
    emklogger.setLevel(logging.DEBUG)
    if textBrowser:
        emklogger.handlers = []
        handler = handlerClass(textBrowser, textBrowserDetailed)
        handler.setLevel(logging.DEBUG)
        logging.getLogger('suds.client').addHandler(handler)
    if logToFile:
        handler = logging.FileHandler(config.LOGGING_DIRECTORY + 'EmkV2.log')
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(funcName)s %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        emklogger.addHandler(handler)
    if tblError:
        handler = ErrorLogTableHandler(tblError)
        handler.setLevel(logging.DEBUG)
        emklogger.addHandler(handler)


def main():
    from s11mainConsole import CS11MainConsoleApp
    import argparse
    parser = argparse.ArgumentParser(description=u'Отправка карточек в ИЭМК')
    parser.add_argument('--startDate', dest='startDate', help=u'Дата, с которой выгружать', metavar='SDATE',
                        default=dateLeftInfinity.toPyDate())
    parser.add_argument('--endDate', dest='endDate', help=u'Дата, по которую выгружать', metavar='EDATE',
                        default=dateRightInfinity.toPyDate())
    parser.add_argument('--maxCount', dest='maxCount', help=u'Максимальное количество случаев для выгрузки',
                        metavar='COUNT', default=10000)
    parser.add_argument('--eventId', dest='eventId',
                        help=u'id Конкретного случая, который мы хотим послать. '
                             u'Если указан этот параметр прочие игнорируются',
                        metavar='EID', default=None)
    parser.add_argument('--resend', dest='resend', help=u'Перепослать отказанные случаи', default=False,
                        action='store_true')
    parser.add_argument('--webEpicrisis', dest='webEpicrisis',
                        help=u'Использовать веб модуль "Эпикризы" для выгрузки. '
                             u'По умолчанию используются шаблоны печати Виста-Меда',
                        default=False, action='store_true')
    parser.add_argument('--fLog', dest='fLog', help=u'Логировать в файл', default=False, action='store_true')
    parser.add_argument('--sendClient', dest='clientId', help=u'Послать только карту клиента', metavar='CLIENT_ID',
                        default=None)
    args = parser.parse_args()
    library.LoggingModule.Logger.loggerDbName = config.LOGGER_NAME

    try:
        QtGui.qApp = CS11MainConsoleApp(sys.argv, config.connectionInfo)
        loggingConfigure(args.fLog)
        s = Service(idLPU=config.LPU_INFIS)
        if args.clientId:
            s.sendClient(clientId=int(args.clientId))
        else:
            s.sendEvents(startDate=args.startDate, endDate=args.endDate, maxCount=args.maxCount, resend=args.resend,
                         eventId=int(args.eventId) if args.eventId else None, newEpicrisis=args.webEpicrisis)
    except Exception as e:
        print e
    finally:
        QtGui.qApp.closeDatabase()


if __name__ == '__main__':
    main()
