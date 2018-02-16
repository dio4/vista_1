# -*- coding: utf-8 -*-
import logging

from PyQt4 import QtGui, QtCore
from suds.cache import DocumentCache
from suds.client import Client, WebFault
import sys

from Registry.Utils import getClientAddress, getAddressInfo, formatAddressInt
from library.Utils import forceString, forceInt, forceDateTime
from library.LoggingModule.Log import Logger

# Класс методами для взаимодействия с нетрикой
class NetricaServices():
    def __init__(self):
        self.db = QtGui.qApp.db
        self.api = Client(forceString(QtGui.qApp.preferences.appPrefs['UOServiceAddress']))
        # self.api = Client('http://qm-demo.zdrav.netrika.ru/MqService.svc?wsdl')
        self.api.set_options(cache=DocumentCache())
        self.logger = Logger('netrica.log')
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('suds.client').setLevel(logging.DEBUG)
        handler = logging.FileHandler('suds.log')
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(funcName)s %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger('suds.client').addHandler(handler)

    # Получение значения проперти по коду
    def getValueByPropetyRecord(self, propertyList, code):
        tblProperty = self.db.table('ActionProperty')
        tblProprtyType = self.db.table('ActionPropertyType')
        tblPropertyStr = self.db.table('ActionProperty_String')
        tblProp = tblProperty.innerJoin(tblProprtyType, tblProprtyType['id'].eq(tblProperty['type_id']))
        propRec = self.db.getRecordEx(tblProp, tblProperty['id'], [tblProperty['id'].inlist(propertyList), tblProprtyType['shortName'].eq(code)])
        if propRec:
            valueRec = self.db.getRecordEx(tblPropertyStr, tblPropertyStr['value'], tblPropertyStr['id'].eq(forceInt(propRec.value('id'))))
            if valueRec:
                return forceString(valueRec.value('value'))
            else:
                return None
        else:
            return None

    # Поиск одного направления
    def searchOne(self, referralCode):
        tableOrganisation = self.db.table('Organisation')

        if referralCode:
            # Авторизация
            auth = self.api.factory.create('credentials')
            auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
            auth.Organization = forceString(
                self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                                  tableOrganisation['netrica_Code']))

            # Ид направления
            options = self.api.factory.create('options')
            options.IdMq = forceString(referralCode)

            try:
                responce = self.api.service.SearchOne(auth, options)
                if responce:
                    return responce
            except WebFault, err:
                print unicode(err)
            except:
                err = sys.exc_info()[1]
                print 'Other error: ' + str(err)



    # Аннулирование
    def sendCancellation(self, referralCode):
        errors = ErrorList()

        if referralCode:
            tableReferral = self.db.table('Referral')
            tableOrganisation = self.db.table('Organisation')

            recReferral = self.db.getRecordEx(tableReferral, '*', tableReferral['netrica_id'].eq(referralCode))
            recOrganisation = self.db.getRecordEx(tableOrganisation, '*', tableOrganisation['id'].eq(QtGui.qApp.currentOrgId()))

            if not forceInt(recOrganisation.value('isMedical')) in (1, 2):
                errors.addError(u'У выбраной в умолчаниях организации поле isMedical должно быть 1 или 2')

            if errors.getErrors():
                errors.showError()
                return

            # Авторизация
            auth = self.api.factory.create('credentials')
            auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
            auth.Organization = forceString(
                self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                                  tableOrganisation['netrica_Code']))

            # Данные о аннулировании
            referral = self.api.factory.create('referral')
            referral.EventsInfo.Cancellation.Date = forceDateTime(QtCore.QDateTime.currentDateTime()).toPyDateTime()
            referral.EventsInfo.Cancellation.CancellationReason.Code = '5'
            referral.EventsInfo.Cancellation.CancellationReason.System = '1.2.643.2.69.1.1.1.60'
            if forceInt(recOrganisation.value('isMedical') == 1):
                referral.EventsInfo.Cancellation.CancellationSource.Code = '3'
            elif forceInt(recOrganisation.value('isMedical') == 2):
                referral.EventsInfo.Cancellation.CancellationSource.Code = '2'
            referral.EventsInfo.Cancellation.CancellationSource.System = '1.2.643.2.69.1.1.1.49'
            referral.ReferralInfo.IdMq = forceString(recReferral.value('netrica_id'))
            try:
                responce = self.api.service.Cancellation(auth, referral)
                if responce:
                    return responce
            except WebFault, err:
                print unicode(err)
            except:
                err = sys.exc_info()[1]
                print 'Other error: ' + str(err)


    # Заполнение и отправка направления
    def sendReferral(self, refInfo):
        errors = ErrorList()

        # Таблицы
        tableOrganisation = self.db.table('Organisation')
        tablePerson = self.db.table('Person')
        tableClient = self.db.table('Client')
        tableSpeciality = self.db.table('rbSpeciality')
        tableMkb = self.db.table('MKB')
        tableMedProfile = self.db.table('rbMedicalAidProfile')
        tablePost = self.db.table('rbPost')
        tableClientContacts = self.db.table('ClientContact')
        tableWork = self.db.table('ClientWork')
        tableDocuments = self.db.table('ClientDocument')

        # записи
        recPerson = self.db.getRecordEx(tablePerson, '*', tablePerson['id'].eq(refInfo['person']))
        recClient = self.db.getRecordEx(tableClient, '*', tableClient['id'].eq(QtGui.qApp.currentClientId()))
        recContact = self.db.getRecordList(tableClientContacts, '*', [tableClientContacts['client_id'].eq(QtGui.qApp.currentClientId()), tableClientContacts['contact'].isNotNull(), tableClientContacts['deleted'].eq(0)])

        if not recContact:
            errors.addError(u'У пациента не заполнены контакты')

        if not forceString(self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(), tableOrganisation['netrica_Code'])):
            errors.addError(u'Не заполнено netrica_code в organisation для направляющей МО')

        if not forceString(self.db.translate(tableMedProfile, tableMedProfile['id'], refInfo['medProfile'], tableMedProfile['netrica_Code'])):
            errors.addError(u'Не заполнено netrica_code в rbMedicalAidProfile для выбранного профиля помощи')

        if not forceString(self.db.translate(tableSpeciality, tableSpeciality['id'], forceInt(recPerson.value('speciality_id')), tableSpeciality['netrica_Code'])):
            errors.addError(u'Не заполнено netrica_code в rbSpeciality для выбранной специальности')

        if not forceString(self.db.translate(tablePost, tablePost['id'], forceInt(recPerson.value('post_id')), tablePost['netrica_Code'])):
            errors.addError(u'Не заполнено netrica_code в rbPost для выбранного врача')

        if not forceInt(recPerson.value('sex')):
            errors.addError(u'Не выбран пол врача')

        if not forceString(self.db.translate(tableOrganisation, 'id', refInfo['relegateMO'], tableOrganisation['netrica_Code'])):
            errors.addError(u'Не заполнено netrica_code в organisation для целевой МО')

        if errors.getErrors():
            errors.showError()
            return

        # recWork = self.db.getRecordEx(tableWork, [tableWork['freeInput'], tableWork['org_id']], [tableWork['client_id'].eq(QtGui.qApp.currentClientId()), tableWork['deleted'].eq(0)])
        regAddress = ''
        locAddress = ''
        regAddrRecord = getClientAddress(QtGui.qApp.currentClientId(), 0)
        if regAddrRecord:
            reAddr = getAddressInfo(regAddrRecord)
            regAddress = formatAddressInt(reAddr)
        locAddrRecord = getClientAddress(QtGui.qApp.currentClientId(), 1)
        if locAddrRecord:
            locAddr = getAddressInfo(locAddrRecord)
            locAddress = formatAddressInt(locAddr)
        recDocuments = self.db.getRecordList(tableDocuments, '*', [tableDocuments['client_id'].eq(QtGui.qApp.currentClientId()), tableDocuments['deleted'].eq(0)])

        # if recWork and not forceString(recWork.value('freeInput')) and forceString(recWork.value('org_id')):
        #     recWork = self.db.getRecordEx(tableOrganisation, tableOrganisation['fullName'], tableOrganisation['id'].eq(forceInt(recWork.value('org_id'))))

        # Авторизация
        auth = self.api.factory.create('credentials')
        auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
        auth.Organization = forceString(
            self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                              tableOrganisation['netrica_Code']))

        # Структура направления
        referral = self.api.factory.create('referral')

        # Информация о направлении
        referral.ReferralInfo.Date = refInfo['refDate']
        referral.ReferralInfo.ReferralType.Code = forceString(refInfo['type'])
        referral.ReferralInfo.ReferralType.System = 'urn:oid:1.2.643.2.69.1.1.1.55'
        referral.ReferralInfo.ProfileMedService.Code = forceString(self.db.translate(tableMedProfile,
                                                                                     tableMedProfile['id'], refInfo['medProfile'],
                                                                                     tableMedProfile['netrica_Code']))
        referral.ReferralInfo.ProfileMedService.System = 'urn:oid:1.2.643.2.69.1.1.1.56'
        # Информация для офтальмологов
        if refInfo.has_key('eyesInfo'):
            def getKeyValue(code, value):
                data = self.api.factory.create('ns6:KeyValueOfstringstring')
                data.Key = code
                data.Value = value
                return data

            additional = self.api.factory.create('ns0:Additional')
            additional.ExtraData = self.api.factory.create('ns6:ArrayOfKeyValueOfstringstring')
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'AddProff')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('AddProff', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'AddCatComp')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('AddCatComp', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYIntPres')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYIntPres', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYOD')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYOD', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYsph')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYsph', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYcyl')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYcyl', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYDax')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYDax', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYeql')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYeql', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYIntPres')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYIntPres', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYOS')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYOS', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYsph')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYsph', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYcyl')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYcyl', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYDax')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYDax', addInfo))
            addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYeql')
            if addInfo:
                additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYeql', addInfo))

            # Информация о направляющей МО
        if refInfo.has_key('eyesInfo'):
            referral.ReferralSurvey.Additional = additional
        referral.Source.IdReferralMis = forceString(refInfo['number'])
        referral.Source.Lpu.Code = forceString(
            self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                              tableOrganisation['netrica_Code']))
        referral.Source.Lpu.System = 'urn:oid:1.2.643.2.69.1.1.1.64'
        referral.Source.Doctors.Doctor = self.api.factory.create('referral.Source.Doctors.Doctor')
        referral.Source.Doctors.Doctor.Role.Code = '1'
        referral.Source.Doctors.Doctor.Role.System = 'urn:oid:1.2.643.2.69.1.1.1.66'
        referral.Source.Doctors.Doctor.Lpu.Code = forceString(
            self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                              tableOrganisation['netrica_Code']))
        referral.Source.Doctors.Doctor.Lpu.System = 'urn:oid:1.2.643.2.69.1.1.1.64'
        referral.Source.Doctors.Doctor.Speciality.Code = forceString(
            self.db.translate(tableSpeciality, tableSpeciality['id'], forceInt(recPerson.value('speciality_id')),
                              tableSpeciality['netrica_Code']))
        referral.Source.Doctors.Doctor.Speciality.System = 'urn:oid:1.2.643.5.1.13.2.1.1.181'
        referral.Source.Doctors.Doctor.Position.Code = forceString(self.db.translate(tablePost, tablePost['id'], forceInt(recPerson.value('post_id')), tablePost['netrica_Code']))
        referral.Source.Doctors.Doctor.Position.System = 'urn:oid:1.2.643.5.1.13.2.1.1.607'
        referral.Source.Doctors.Doctor.Person.IdPersonMis = forceString(recPerson.value('id'))
        referral.Source.Doctors.Doctor.Person.Sex.Code = forceString(recPerson.value('sex'))
        referral.Source.Doctors.Doctor.Person.Sex.System = 'urn:oid:1.2.643.5.1.13.2.1.1.156'
        referral.Source.Doctors.Doctor.Person.HumanName.FamilyName = forceString(recPerson.value('lastName'))
        referral.Source.Doctors.Doctor.Person.HumanName.GivenName = forceString(recPerson.value('firstName'))
        referral.Source.Doctors.Doctor.Person.HumanName.MiddleName = forceString(recPerson.value('patrName'))
        referral.Source.MainDiagnosis.MainDiagnosis = self.api.factory.create('referral.Source.MainDiagnosis.MainDiagnosis')
        referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.DiagnosedDate = forceDateTime(
            QtCore.QDateTime.currentDateTime()).toPyDateTime()
        referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.Comment = forceString(
            self.db.translate(tableMkb, tableMkb['DiagID'], refInfo['MKB'], tableMkb['DiagName']))
        referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.DiagnosisType.Code = '1'
        referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.DiagnosisType.System = 'urn:oid:1.2.643.2.69.1.1.1.26'
        referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.MkbCode.Code = forceString(refInfo['MKB'])
        referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.MkbCode.System = 'urn:oid:1.2.643.2.69.1.1.1.2'

        # Информация о пациенте
        referral.Patient.Person.BirthDate = forceDateTime(recClient.value('birthDate')).toPyDateTime()
        referral.Patient.Person.Sex.Code = forceString(recClient.value('sex'))
        referral.Patient.Person.Sex.System = 'urn:oid:1.2.643.5.1.13.2.1.1.156'
        referral.Patient.Person.HumanName.FamilyName = forceString(recClient.value('lastName'))
        referral.Patient.Person.HumanName.GivenName = forceString(recClient.value('firstName'))
        referral.Patient.Person.HumanName.MiddleName = forceString(recClient.value('patrName'))
        referral.Patient.Person.IdPatientMis = forceString(recClient.value('id'))
        referral.Patient.ContactDtos.ContactDto = []
        if recContact:
            for contact in recContact:
                if forceInt(contact.value('contactType_id')) == 3:
                    con = self.api.factory.create('referral.Patient.ContactDtos.ContactDto')
                    con.ContactValue = forceString(contact.value('contact'))
                    con.ContactType.Code = '1'
                    con.ContactType.System = 'urn:oid:1.2.643.2.69.1.1.1.27'
                    referral.Patient.ContactDtos.ContactDto.append(con)
                elif forceInt(contact.value('contactType_id')) == 1:
                    con = self.api.factory.create('referral.Patient.ContactDtos.ContactDto')
                    con.ContactValue = forceString(contact.value('contact'))
                    con.ContactType.Code = '2'
                    con.ContactType.System = 'urn:oid:1.2.643.2.69.1.1.1.27'
                    referral.Patient.ContactDtos.ContactDto.append(con)
        # if recWork and forceString(recWork.value('freeInput')):
        #     referral.Patient.Jobs.Job = []
        #     job = self.api.factory.create('referral.Patient.Jobs.Job')
        #     job.CompanyName = forceString(recWork.value('freeInput'))
        #     referral.Patient.Jobs.Job.append(job)
        # elif recWork and forceString(recWork.value('fullName')):
        #     referral.Patient.Jobs.Job = []
        #     job = self.api.factory.create('referral.Patient.Jobs.Job')
        #     job.CompanyName = forceString(recWork.value('fullName'))
        #     referral.Patient.Jobs.Job.append(job)
        referral.Patient.Addresses.AddressDto = []
        if regAddress:
            regAdd = self.api.factory.create('referral.Patient.Addresses.AddressDto')
            regAdd.StringAddress = regAddress
            regAdd.AddressType.Code = '1'
            regAdd.AddressType.System = 'urn:oid:1.2.643.2.69.1.1.1.28'
            referral.Patient.Addresses.AddressDto.append(regAdd)
        if locAddress:
            locAdd = self.api.factory.create('referral.Patient.Addresses.AddressDto')
            locAdd.StringAddress = locAddress
            locAdd.AddressType.Code = '2'
            locAdd.AddressType.System = 'urn:oid:1.2.643.2.69.1.1.1.28'
            referral.Patient.Addresses.AddressDto.append(locAdd)
        referral.Patient.Documents.DocumentDto = []
        if recDocuments:
            for docum in recDocuments:
                tableDocType = self.db.table('rbDocumentType')
                recDocType = self.db.getRecordEx(tableDocType, '*', tableDocType['id'].eq(forceInt(docum.value('documentType_id'))))
                if forceString(recDocType.value('netrica_code2')):
                    doc = self.api.factory.create('referral.Patient.Documents.DocumentDto')
                    doc.DocS = forceString(docum.value('serial'))
                    doc.DocN = forceString(docum.value('number'))
                    if forceString(docum.value('date')):
                        doc.IssuedDate = forceDateTime(docum.value('date')).toPyDateTime()
                    if forceString(docum.value('endDate')):
                        doc.ExpiredDate = forceDateTime(docum.value('endDate')).toPyDateTime()
                    doc.DocumentType.Code = forceString(recDocType.value('netrica_code2'))
                    doc.DocumentType.System = 'urn:oid:1.2.643.2.69.1.1.1.59'
                    referral.Patient.Documents.DocumentDto.append(doc)

        # Информация о событии
        referral.EventsInfo.Source.IsReferralReviewed = None
        if refInfo['type'] == 1:
            referral.EventsInfo.Source.PlannedDate = refInfo['plannedDate']
        referral.EventsInfo.Source.ReferralCreateDate = forceDateTime(QtCore.QDateTime.currentDateTime()).toPyDateTime()
        referral.EventsInfo.Source.ReferralOutDate = refInfo['refDate']

        # Информация о целевой МО
        referral.Target.Lpu.Code = forceString(
            self.db.translate(tableOrganisation, 'id', refInfo['relegateMO'], tableOrganisation['netrica_Code']))
        referral.Target.Lpu.System = 'urn:oid:1.2.643.2.69.1.1.1.64'

        responce = self.api.service.Register(auth, referral)
        if responce:
            return responce

    # Заполнение и отправка направления
    def updateReferral(self, refInfo):
            # Таблицы
            tableOrganisation = self.db.table('Organisation')
            tablePerson = self.db.table('Person')
            tableClient = self.db.table('Client')
            tableSpeciality = self.db.table('rbSpeciality')
            tableMkb = self.db.table('MKB')
            tableMedProfile = self.db.table('rbMedicalAidProfile')
            tablePost = self.db.table('rbPost')
            tableClientContacts = self.db.table('ClientContact')
            tableWork = self.db.table('ClientWork')
            tableDocuments = self.db.table('ClientDocument')

            # записи
            recClient = self.db.getRecordEx(tableClient, '*', tableClient['id'].eq(QtGui.qApp.currentClientId()))
            recContact = self.db.getRecordList(tableClientContacts, '*',
                                               [tableClientContacts['client_id'].eq(QtGui.qApp.currentClientId()),
                                                tableClientContacts['contact'].isNotNull(),
                                                tableClientContacts['deleted'].eq(0)])
            if not recContact:
                QtGui.QMessageBox.warning(None, u'Ошибка', u'У пациента не заполнены контакты')
                return
            # recWork = self.db.getRecordEx(tableWork, [tableWork['freeInput'], tableWork['org_id']], [tableWork['client_id'].eq(QtGui.qApp.currentClientId()), tableWork['deleted'].eq(0)])
            regAddress = ''
            locAddress = ''
            regAddrRecord = getClientAddress(QtGui.qApp.currentClientId(), 0)
            if regAddrRecord:
                reAddr = getAddressInfo(regAddrRecord)
                regAddress = formatAddressInt(reAddr)
            locAddrRecord = getClientAddress(QtGui.qApp.currentClientId(), 1)
            if locAddrRecord:
                locAddr = getAddressInfo(locAddrRecord)
                locAddress = formatAddressInt(locAddr)
            recDocuments = self.db.getRecordList(tableDocuments, '*',
                                                 [tableDocuments['client_id'].eq(QtGui.qApp.currentClientId()),
                                                  tableDocuments['deleted'].eq(0)])

            # if recWork and not forceString(recWork.value('freeInput')) and forceString(recWork.value('org_id')):
            #     recWork = self.db.getRecordEx(tableOrganisation, tableOrganisation['fullName'], tableOrganisation['id'].eq(forceInt(recWork.value('org_id'))))

            # Авторизация
            auth = self.api.factory.create('credentials')
            auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
            auth.Organization = forceString(
                self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                                  tableOrganisation['netrica_Code']))

            # Структура направления
            referral = self.api.factory.create('referral')

            # Информация о направлении
            referral.ReferralInfo.IdMq = refInfo['netrica_id']
            referral.ReferralInfo.Date = refInfo['refDate']
            referral.ReferralInfo.ReferralType.Code = forceString(refInfo['type'])
            referral.ReferralInfo.ReferralType.System = 'urn:oid:1.2.643.2.69.1.1.1.55'
            referral.ReferralInfo.ProfileMedService.Code = forceString(self.db.translate(tableMedProfile,
                                                                                         tableMedProfile['id'],
                                                                                         refInfo['medProfile'],
                                                                                         tableMedProfile[
                                                                                             'netrica_Code']))
            referral.ReferralInfo.ProfileMedService.System = 'urn:oid:1.2.643.2.69.1.1.1.56'
            # Информация для офтальмологов
            if refInfo.has_key('eyesInfo'):
                def getKeyValue(code, value):
                    data = self.api.factory.create('ns6:KeyValueOfstringstring')
                    data.Key = code
                    data.Value = value
                    return data

                additional = self.api.factory.create('ns0:Additional')
                additional.ExtraData = self.api.factory.create('ns6:ArrayOfKeyValueOfstringstring')
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'AddProff')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('AddProff', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'AddCatComp')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('AddCatComp', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYIntPres')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYIntPres', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYOD')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYOD', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYsph')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYsph', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYcyl')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYcyl', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYDax')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYDax', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'RYeql')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('RYeql', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYIntPres')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYIntPres', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYOS')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYOS', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYsph')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYsph', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYcyl')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYcyl', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYDax')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYDax', addInfo))
                addInfo = self.getValueByPropetyRecord(refInfo['eyesInfo'], 'LYeql')
                if addInfo:
                    additional.ExtraData.KeyValueOfstringstring.append(getKeyValue('LYeql', addInfo))

                    # Информация о направляющей МО
            if refInfo.has_key('eyesInfo'):
                referral.ReferralSurvey.Additional = additional
            referral.Source.IdReferralMis = forceString(refInfo['number'])
            referral.Source.Lpu.Code = forceString(
                self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                                  tableOrganisation['netrica_Code']))
            referral.Source.Lpu.System = 'urn:oid:1.2.643.2.69.1.1.1.64'
            referral.Source.MainDiagnosis.MainDiagnosis = self.api.factory.create(
                'referral.Source.MainDiagnosis.MainDiagnosis')
            referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.DiagnosedDate = forceDateTime(
                QtCore.QDateTime.currentDateTime()).toPyDateTime()
            referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.Comment = forceString(
                self.db.translate(tableMkb, tableMkb['DiagID'], refInfo['MKB'], tableMkb['DiagName']))
            referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.DiagnosisType.Code = '1'
            referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.DiagnosisType.System = 'urn:oid:1.2.643.2.69.1.1.1.26'
            referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.MkbCode.Code = forceString(refInfo['MKB'])
            referral.Source.MainDiagnosis.MainDiagnosis.DiagnosisInfo.MkbCode.System = 'urn:oid:1.2.643.2.69.1.1.1.2'

            # Информация о пациенте
            referral.Patient.Person.BirthDate = forceDateTime(recClient.value('birthDate')).toPyDateTime()
            referral.Patient.Person.Sex.Code = forceString(recClient.value('sex'))
            referral.Patient.Person.Sex.System = 'urn:oid:1.2.643.5.1.13.2.1.1.156'
            referral.Patient.Person.HumanName.FamilyName = forceString(recClient.value('lastName'))
            referral.Patient.Person.HumanName.GivenName = forceString(recClient.value('firstName'))
            referral.Patient.Person.HumanName.MiddleName = forceString(recClient.value('patrName'))
            referral.Patient.Person.IdPatientMis = forceString(recClient.value('id'))
            referral.Patient.ContactDtos.ContactDto = []
            if recContact:
                for contact in recContact:
                    if forceInt(contact.value('contactType_id')) == 3:
                        con = self.api.factory.create('referral.Patient.ContactDtos.ContactDto')
                        con.ContactValue = forceString(contact.value('contact'))
                        con.ContactType.Code = '1'
                        con.ContactType.System = 'urn:oid:1.2.643.2.69.1.1.1.27'
                        referral.Patient.ContactDtos.ContactDto.append(con)
                    elif forceInt(contact.value('contactType_id')) == 1:
                        con = self.api.factory.create('referral.Patient.ContactDtos.ContactDto')
                        con.ContactValue = forceString(contact.value('contact'))
                        con.ContactType.Code = '2'
                        con.ContactType.System = 'urn:oid:1.2.643.2.69.1.1.1.27'
                        referral.Patient.ContactDtos.ContactDto.append(con)
            # if recWork and forceString(recWork.value('freeInput')):
            #     referral.Patient.Jobs.Job = []
            #     job = self.api.factory.create('referral.Patient.Jobs.Job')
            #     job.CompanyName = forceString(recWork.value('freeInput'))
            #     referral.Patient.Jobs.Job.append(job)
            # elif recWork and forceString(recWork.value('fullName')):
            #     referral.Patient.Jobs.Job = []
            #     job = self.api.factory.create('referral.Patient.Jobs.Job')
            #     job.CompanyName = forceString(recWork.value('fullName'))
            #     referral.Patient.Jobs.Job.append(job)
            referral.Patient.Addresses.AddressDto = []
            if regAddress:
                regAdd = self.api.factory.create('referral.Patient.Addresses.AddressDto')
                regAdd.StringAddress = regAddress
                regAdd.AddressType.Code = '1'
                regAdd.AddressType.System = 'urn:oid:1.2.643.2.69.1.1.1.28'
                referral.Patient.Addresses.AddressDto.append(regAdd)
            if locAddress:
                locAdd = self.api.factory.create('referral.Patient.Addresses.AddressDto')
                locAdd.StringAddress = locAddress
                locAdd.AddressType.Code = '2'
                locAdd.AddressType.System = 'urn:oid:1.2.643.2.69.1.1.1.28'
                referral.Patient.Addresses.AddressDto.append(locAdd)
            referral.Patient.Documents.DocumentDto = []
            if recDocuments:
                for docum in recDocuments:
                    tableDocType = self.db.table('rbDocumentType')
                    recDocType = self.db.getRecordEx(tableDocType, '*',
                                                     tableDocType['id'].eq(forceInt(docum.value('documentType_id'))))
                    if forceString(recDocType.value('netrica_code2')):
                        doc = self.api.factory.create('referral.Patient.Documents.DocumentDto')
                        doc.DocS = forceString(docum.value('serial'))
                        doc.DocN = forceString(docum.value('number'))
                        if forceString(docum.value('date')):
                            doc.IssuedDate = forceDateTime(docum.value('date')).toPyDateTime()
                        if forceString(docum.value('endDate')):
                            doc.ExpiredDate = forceDateTime(docum.value('endDate')).toPyDateTime()
                        doc.DocumentType.Code = forceString(recDocType.value('netrica_code2'))
                        doc.DocumentType.System = 'urn:oid:1.2.643.2.69.1.1.1.59'
                        referral.Patient.Documents.DocumentDto.append(doc)

            # Информация о событии
            referral.EventsInfo.Source.IsReferralReviewed = None
            if refInfo['type'] == 1:
                referral.EventsInfo.Source.PlannedDate = refInfo['plannedDate']
            referral.EventsInfo.Source.ReferralCreateDate = forceDateTime(
                QtCore.QDateTime.currentDateTime()).toPyDateTime()
            referral.EventsInfo.Source.ReferralOutDate = refInfo['refDate']

            # Информация о целевой МО
            referral.Target.Lpu.Code = forceString(
                self.db.translate(tableOrganisation, 'id', refInfo['relegateMO'], tableOrganisation['netrica_Code']))
            referral.Target.Lpu.System = 'urn:oid:1.2.643.2.69.1.1.1.64'

            try:
                responce = self.api.service.UpdateFromSourcedMo(auth, referral)
                if responce:
                    return responce

            except WebFault, err:
                print unicode(err)
            except:
                err = sys.exc_info()[1]
                print 'Other error: ' + str(err)

    # Подтверждение направления
    def sendApproved(self, referralCode):
        tableReferral = self.db.table('Referral')
        tableOrganisation = self.db.table('Organisation')

        recReferral = self.db.getRecordEx(tableReferral, '*', tableReferral['netrica_id'].eq(referralCode))

        # Авторизация
        auth = self.api.factory.create('credentials')
        auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
        auth.Organization = forceString(
            self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                              tableOrganisation['netrica_Code']))

        # Данные о направлении
        referral = self.api.factory.create('referral')
        referral.ReferralInfo.IdMq = forceString(recReferral.value('netrica_id'))
        referral.EventsInfo.Target.IsReferralReviwed = True
        referral.EventsInfo.Target.ReferralReviewDate = forceDateTime(QtCore.QDateTime.currentDateTime()).toPyDateTime()
        referral.Target.IsReferralReviewed = True
        referral.Target.ReferralReviewDate = forceDateTime(QtCore.QDateTime.currentDateTime()).toPyDateTime()

        try:
            responce = self.api.service.AgreedFromTargetMo(auth, referral)
            if responce:
                return responce

        except WebFault, err:
            print unicode(err)
        except:
            err = sys.exc_info()[1]
            print 'Other error: ' + str(err)

    # Получение результирующего документа
    def getResultDocument(self, referralId):
        tableOrganisation = self.db.table('Organisation')
        # Авторизация
        auth = self.api.factory.create('credentials')
        auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
        auth.Organization = forceString(
            self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                              tableOrganisation['netrica_Code']))

        # Данные о направлении
        referral = self.api.factory.create('referral')
        referral.ReferralInfo.IdMq = forceString(referralId)
        try:
            responce = self.api.service.GetResultDocument(auth, referral)
            if responce:
                return responce

        except WebFault, err:
            print unicode(err)
        except:
            err = sys.exc_info()[1]
            print 'Other error: ' + str(err)

    # Запрос очередей по заданному профилю
    def getQueueInfo(self, profileCode):
        tableOrganisation = self.db.table('Organisation')
        auth = self.api.factory.create('credentials')
        auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
        auth.Organization = forceString(
            self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                              tableOrganisation['netrica_Code']))

        options = self.api.factory.create('options')
        options.ReferralInfo.ProfileMedService.Code = profileCode
        options.ReferralInfo.ProfileMedService.System = '1.2.643.2.69.1.1.1.56'
        options.DateReport = forceDateTime(QtCore.QDate.currentDate()).toPyDateTime()
        try:
            responce = self.api.service.GetQueueInfo(auth, options)
            if responce:
                return responce

        except WebFault, err:
            print unicode(err)
        except:
            err = sys.exc_info()[1]
            print 'Other error: ' + str(err)

    # Регистрация новой очереди
    def updateMedServiceProfile(self, profileDict):
        tableOrganisation = self.db.table('Organisation')
        auth = self.api.factory.create('credentials')
        auth.Token = forceString(QtGui.qApp.preferences.appPrefs['UOServiceToken'])
        auth.Organization = forceString(
            self.db.translate(tableOrganisation, tableOrganisation['id'], QtGui.qApp.currentOrgId(),
                              tableOrganisation['netrica_Code']))
        profile = self.api.factory.create('profileMedService')
        profile.IdProfileMedService.Code = profileDict['profile']
        profile.IdProfileMedService.System = '1.2.643.2.69.1.1.1.56'
        profile.StartDate = forceDateTime(profileDict['begDate']).toPyDateTime()
        profile.EndDate = forceDateTime(profileDict['endDate']).toPyDateTime()
        profile.Address = profileDict['address']
        profile.ContactValue = profileDict['contacts']
        profile.Comment = profileDict['comment']
        try:
            responce = self.api.service.UpdateMedServiceProfile(auth, profile)
            if responce:
                return responce

        except WebFault, err:
            print unicode(err)
        except:
            err = sys.exc_info()[1]
            print 'Other error: ' + str(err)

class ErrorList():
    def __init__(self):
        self.errors = u''

    def addError(self, message):
        self.errors += message + u'\n'

    def showError(self):
        QtGui.QMessageBox.information(None, u'Ошибка', u'Список ошибок:\n' + self.errors)

    def getErrors(self):
        return self.errors

class NetricaAppointment():
    def __init__(self):
        self.db = QtGui.qApp.db
        self.api = Client('http://10.0.1.81/HubServicev2/hubservice.svc?wsdl')
        self.api.set_options(cache=DocumentCache())
        self.netricaService = NetricaServices()
        self.logger = Logger('netrica.log')

    # Запрос номерков
    def getTickets(self, referral):
        tableClient = self.db.table('Client')
        recClient = self.db.getRecordEx(tableClient, '*', tableClient['id'].eq(forceInt(referral.value('client_id'))))
        doctorsReferal = forceString(referral.value('netrica_id'))
        surname = forceString(recClient.value('lastName'))
        guid = '09D4AB57-EBB9-4202-BBA4-1DAF27E0A084'
        attachedReferral = None  #forceString(self.netricaService.searchOne(forceString(referral.value('netrica_id'))))

        try:
            responce = self.api.service.InspectDoctorsReferral2(doctorsReferal, surname, attachedReferral, guid)
            if responce:
                return responce

        except WebFault, err:
            print unicode(err)
        except:
            err = sys.exc_info()[1]
            print 'Other error: ' + str(err)

    # Бронирование номерка
    def SetAppointment(self, ticket, idLpu, clientId, referral):
        doctorsReferal = forceString(referral.value('netrica_id'))
        idAppointment = forceString(ticket)
        idLpu = idLpu
        idPat = clientId
        guid = '09D4AB57-EBB9-4202-BBA4-1DAF27E0A084'

        try:
            self.logger.insertFileLog(ticket=idAppointment, lpu=idLpu, pat=idPat, ref=doctorsReferal, giud=guid)
            responce = self.api.service.SetAppointment(idAppointment=idAppointment, idLpu=idLpu, idPat=idPat, doctorsReferral=doctorsReferal, guid=guid)
            if responce:
                return responce

        except WebFault, err:
            print unicode(err)
        except:
            err = sys.exc_info()[1]
            print 'Other error: ' + str(err)
