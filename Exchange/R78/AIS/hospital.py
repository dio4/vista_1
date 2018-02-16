# -*- coding: utf-8 -*-
import os
import sys
import xml

from PyQt4 import QtGui, QtCore
from library.database import connectDataBaseByInfo
from library.Utils import forceString, forceDate, forceInt
from datetime import date, timedelta, datetime
from prepareSoap import CPrepareSoap
import config, stmts
import xml.etree.ElementTree
from library.LoggingModule import Logger


class Exchange():
    if os.name == 'nt':
        app = QtCore.QCoreApplication(sys.argv)
    begDate = forceString(date.today() - timedelta(days=1)) + ' 00:00:00'
    endDate = forceString(date.today() - timedelta(days=1)) + ' 23:59:59'

    def __init__(self):
        self.db = QtGui.qApp.db
        self.url = forceString(QtGui.qApp.preferences.appPrefs['referralServiceUrl'])
        if not self.db:
            self.db = connectDataBaseByInfo(config.connectionInfo)

    @staticmethod
    def toDateTuple(datetime, date=None):
        if date is None:
            date = datetime.date()
        time = datetime.time()
        return date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second(), 0

    # Получение уникального номера направления
    def user_referral_number_download(self):
        msg = CPrepareSoap()
        user = forceString(QtGui.qApp.preferences.appPrefs['referralServiceUser'])
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ref="http://www.rintech.ru/isomp/referral_number">')
        msg.addField(u'<ref:DownloadRowsRequest ref:user_name="%s"/>' % user)
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sdat_vpol/user_referral_number_download')
        result = msg.getResult()
        root = xml.etree.ElementTree.fromstring(result)
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/referral_number}DownloadRowsResponse')
        refNum = root.find('{http://www.rintech.ru/isomp/referral_number}ReferralNumber').text
        return refNum

    # Получение сведений о наличии свободных мест
    def user_hospital_vacancy_filter(self, bedProfile):
        msg = CPrepareSoap()
        tableRbHospBed = self.db.table('rbHospitalBedProfile')
        bedProfileRec = self.db.getRecordEx(tableRbHospBed, 'regionalCode',
                                            tableRbHospBed['code'].eq(forceString(bedProfile)))
        if bedProfileRec:
            msg.addHeader(
                u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hos="http://www.rintech.ru/isomp/hospital_vacancy" xmlns:pla="http://www.rintech.ru/isomp/plainrows">')
            msg.addField(
                u'<hos:FilterRowsRequest hos:user_name="%s" hos:rows_max="2000" hos:d_filter="0" hos:order_by="VacancyFromDate-VacancyToDate-">' % config.userName)
            msg.addSection(u'hos:FilterRow')
            msg.addField(
                u'<hos:BedProfileCode>%s</hos:BedProfileCode>' % forceString(bedProfileRec.value('regionalCode')))
            msg.closeSection(u'hos:FilterRow')
            msg.closeSection(u'hos:FilterRowsRequest')
            msg.closeSection(u'soapenv:Body')
            msg.closeSection(u'soapenv:Envelope')
            msg.sendMessage(self.url + '/sdat_vpol/user_hospital_vacancy_filter')
        else:
            QtGui.QMessageBox.information(None, u'Профиль койки', u'Не найен региональный код профиля койки')
            return
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/hospital_vacancy}FilterRowsResponse')
        resultDictList = []
        for i in root:
            element = root.find('{http://www.rintech.ru/isomp/hospital_vacancy}ResultRow')
            if element:
                for k in element:
                    resultDict = {}
                    alreadyInResult = 0
                    resultDict['ReportDate'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}ReportDate').text
                    resultDict['VacancyFromDate'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}VacancyFromDate').text
                    resultDict['VacancyToDate'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}VacancyToDate').text
                    resultDict['HospitalInstitutionReestrNumber'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalInstitutionReestrNumber').text
                    resultDict['HospitalInstitutionShortName'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalInstitutionShortName').text
                    resultDict['HospitalUnitCode'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalUnitCode').text
                    resultDict['HospitalUnitName'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalUnitName').text
                    resultDict['HospitalDepartmentCode'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalDepartmentCode').text
                    resultDict['HospitalDepartmentName'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalDepartmentName').text
                    resultDict['BedProfileCode'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}BedProfileCode').text
                    resultDict['BedProfileName'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}BedProfileName').text
                    resultDict['PatientsStayed'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}PatientsStayed').text
                    resultDict['PatientsAdmitted'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}PatientsAdmitted').text
                    resultDict['PatientsDischarged'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}PatientsDischarged').text
                    resultDict['HospitalizationsPlanned'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalizationsPlanned').text
                    resultDict['BedsVacantAll'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}BedsVacantAll').text
                    resultDict['BedsVacantMale'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}BedsVacantMale').text
                    resultDict['BedsVacantFemale'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}BedsVacantFemale').text
                    resultDict['BedsVacantChild'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}BedsVacantChild').text
                    resultDict['HospitalizationTimeEstimate'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}HospitalizationTimeEstimate').text
                    resultDict['Id'] = element.find('{http://www.rintech.ru/isomp/hospital_vacancy}Id').text
                    resultDict['InputId'] = element.find('{http://www.rintech.ru/isomp/hospital_vacancy}InputId').text
                    resultDict['SourceLine'] = element.find(
                        '{http://www.rintech.ru/isomp/hospital_vacancy}SourceLine').text
                    for i in resultDictList:
                        if i['HospitalInstitutionReestrNumber'] == resultDict['HospitalInstitutionReestrNumber'] and i[
                            'BedProfileCode'] == resultDict['BedProfileCode']:
                            alreadyInResult = 1
                    if not alreadyInResult:
                        resultDictList.append(resultDict)
            else:
                QtGui.QMessageBox.information(None, u'Не найдено', u'Не найдены МО с заданным профилем коек')
        return resultDictList

    # Получение отборочных коммисий по дате коммисии
    def user_selection_commission_calendar_date_filter(self, date, commisionCode):
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sel="http://www.rintech.ru/isomp/selection_commission_calendar_date" xmlns:pla="http://www.rintech.ru/isomp/plainrows">')
        msg.addField(
            u'<sel:FilterRowsRequest sel:user_name="%s" sel:rows_max="100" sel:d_filter="0" sel:order_by="CalendarDate+BeginTime+EndTime+">' % config.userName)
        msg.addSection(u'sel:FilterRow')
        msg.addField(u'<sel:SelectionCommissionCode>%s</sel:SelectionCommissionCode>' % forceString(commisionCode))
        msg.addField(u'<sel:CalendarDate pla:list="intervals-incl">%s</sel:CalendarDate>' % forceString(date))
        msg.closeSection(u'sel:FilterRow')
        msg.closeSection(u'sel:FilterRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sref_vany/user_selection_commission_calendar_date_filter')
        if msg.getResult():
            root = xml.etree.ElementTree.fromstring(msg.getResult())
            root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
            root = root.find('{http://www.rintech.ru/isomp/selection_commission_calendar_date}FilterRowsResponse')
            for i in root:
                element = root.find('{http://www.rintech.ru/isomp/selection_commission_calendar_date}ResultRow')
                if element is not None:
                    resultDict = {}
                    resultDict['SelectionCommissionCode'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}SelectionCommissionCode').text
                    resultDict['SelectionCommissionName'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}SelectionCommissionName').text
                    resultDict['CalendarDate'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}CalendarDate').text
                    resultDict['BeginTime'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}BeginTime').text
                    resultDict['EndTime'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}EndTime').text
                    resultDict['PriorityLevel'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}PriorityLevel').text
                    resultDict['AdditionalInfo'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}AdditionalInfo').text
                    resultDict['AttendanceLimit'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}AttendanceLimit').text
                    resultDict['Id'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}Id').text
                    resultDict['InputId'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}InputId').text
                    resultDict['SourceLine'] = element.find(
                        '{http://www.rintech.ru/isomp/selection_commission_calendar_date}SourceLine').text

                    return resultDict
                else:
                    return

    #
    def user_appointment_queue_timetable_sign_filter(self, date, commisionCode):
        """
        Возвращает лист комиссий для МО

        :param date: строка с началом и концом периода, разделённых пробелом
        :param commisionCode: код комиссии
        :return:
        """
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sel="http://www.rintech.ru/isomp/appointment_queue_timetable_sign" xmlns:pla="http://www.rintech.ru/isomp/plainrows">')

        msg.addField(
            u'<sel:FilterRowsRequest sel:user_name="%s" sel:rows_max="100" sel:d_filter="0" sel:order_by="CalendarDate+BeginTime+EndTime+">' % config.userName)

        msg.addSection(u'sel:FilterRow')
        msg.addField(u'<sel:SelectionCommissionCode>%s</sel:SelectionCommissionCode>' % forceString(commisionCode))
        msg.addField(u'<sel:CalendarDate pla:list="intervals-incl">%s</sel:CalendarDate>' % forceString(date))

        msg.closeSection(u'sel:FilterRow')
        msg.closeSection(u'sel:FilterRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sdat_vany/user_appointment_queue_timetable_sign_filter')

        if msg.getResult():
            root = xml.etree.ElementTree.fromstring(msg.getResult())
            root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')

            beginning = '{http://www.rintech.ru/isomp/appointment_queue_timetable_sign}'

            root = root.find(beginning + 'FilterRowsResponse')

            if len(root) == 0 or root[0].find(beginning + 'SelectionCommissionCode') is None:
                return

            resultDict = {'SelectionCommissionCode': root[0].find(beginning + 'SelectionCommissionCode').text,
                          'SelectionCommissionName': root[0].find(beginning + 'SelectionCommissionName').text,
                          'commissions': []}

            for i in root:
                if i:
                    element = i

                    attendanceCount = forceInt(element.find(beginning + 'AttendanceCount').text)
                    attendanceLimit = forceInt(element.find(beginning + 'AttendanceLimit').text)

                    if not (attendanceCount < attendanceLimit):
                        continue

                    commissionDict = {'BeginTime': element.find(beginning + 'BeginTime').text,
                                      'EndTime': element.find(beginning + 'EndTime').text,
                                      'AdditionalInfo': element.find(beginning + 'AdditionalInfo').text,
                                      'AttendanceLimit': element.find(beginning + 'AttendanceLimit').text,
                                      'CalendarDate': element.find(beginning + 'CalendarDate').text,
                                      'attendance': attendanceLimit - attendanceCount}

                    resultDict['commissions'].append(commissionDict)

            # оставить только уникальные данные
            hashes = set()
            uniqueCommissions = []
            for c in resultDict['commissions']:
                _hash = c['CalendarDate'] + c['BeginTime'] + c['EndTime']

                if _hash not in hashes:
                    hashes.add(_hash)
                    uniqueCommissions.append(c)
            resultDict['commissions'] = uniqueCommissions
            # [dict(y) for y in set(tuple(x.items()) for x in resultDict['commissions'])]

            return resultDict

    # Получение отборочных коммисий
    def selection_commission_bed_profile(self, bedProfile):
        msg = CPrepareSoap()
        tableRbHospBed = self.db.table('rbHospitalBedProfile')
        bedProfileRec = self.db.getRecordEx(tableRbHospBed, 'regionalCode',
                                            tableRbHospBed['code'].eq(forceString(bedProfile)))
        if bedProfileRec:
            msg.addHeader(
                u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hos="http://www.rintech.ru/isomp/selection_commission_bed_profile" xmlns:pla="http://www.rintech.ru/isomp/plainrows">')
            msg.addField(
                u'<hos:FilterRowsRequest hos:user_name="%s" hos:rows_max="100" hos:d_filter="0" hos:order_by="SourceLine+">' % config.userName)
            msg.addSection(u'hos:FilterRow')
            msg.addField(
                u'<hos:BedProfileCode>%s</hos:BedProfileCode>' % forceString(bedProfileRec.value('regionalCode')))
            msg.closeSection(u'hos:FilterRow')
            msg.closeSection(u'hos:FilterRowsRequest')
            msg.closeSection(u'soapenv:Body')
            msg.closeSection(u'soapenv:Envelope')
            msg.sendMessage(self.url + '/sref_vany/user_selection_commission_bed_profile_filter')
        else:
            QtGui.QMessageBox.information(None, u'Профиль койки', u'Не найен региональный код профиля койки')
            return
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/selection_commission_bed_profile}FilterRowsResponse')
        resultDictList = []
        for i in root:
            element = root.findall('{http://www.rintech.ru/isomp/selection_commission_bed_profile}ResultRow')
            if element:
                for k in element:
                    resultDict = {}
                    alreadyInResult = 0
                    resultDict['SelectionCommissionCode'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}SelectionCommissionCode').text
                    resultDict['SelectionCommissionName'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}SelectionCommissionName').text
                    resultDict['MedicalInstitutionReestrNumber'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}MedicalInstitutionReestrNumber').text
                    resultDict['MedicalInstitutionShortName'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}MedicalInstitutionShortName').text
                    resultDict['MedicalUnitCode'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}MedicalUnitCode').text
                    resultDict['MedicalUnitName'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}MedicalUnitName').text
                    resultDict['MedicalDepartmentCode'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}MedicalDepartmentCode').text
                    resultDict['MedicalDepartmentName'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}MedicalDepartmentName').text
                    resultDict['BedProfileCode'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}BedProfileCode').text
                    resultDict['BedProfileName'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}BedProfileName').text
                    resultDict['Id'] = k.find('{http://www.rintech.ru/isomp/selection_commission_bed_profile}Id').text
                    resultDict['InputId'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}InputId').text
                    resultDict['SourceLine'] = k.find(
                        '{http://www.rintech.ru/isomp/selection_commission_bed_profile}SourceLine').text
                    for i in resultDictList:
                        if i['MedicalInstitutionReestrNumber'] == resultDict['MedicalInstitutionReestrNumber'] and i[
                            'BedProfileCode'] == resultDict['BedProfileCode']:
                            alreadyInResult = 1
                    if not alreadyInResult:
                        resultDictList.append(resultDict)
            else:
                QtGui.QMessageBox.information(None, u'Не найдено', u'Не найдены МО с заданным профилем коек')
        return resultDictList

    # Отправка сведений о направлениях на госпитализацию
    def owner_appointment_referral_upload(self, refInfo):
        msg = CPrepareSoap()
        url = forceString(QtGui.qApp.preferences.appPrefs['referralServiceUrl'])
        user = forceString(QtGui.qApp.preferences.appPrefs['referralServiceUser'])
        tblPerson = self.db.table('Person')
        recPerson = self.db.getRecordEx(tblPerson, '*', 'id = %s' % forceString(refInfo['Person']))
        recOrg = self.db.getRecordEx('Organisation', '*', 'id = %s' % forceString(refInfo['Organisation']))
        recClient = self.db.getRecordEx('Client', '*', 'id = %s' % QtGui.qApp.currentClientId())
        recCont = self.db.getRecordEx('ClientContact', 'contact', 'client_id = %s' % QtGui.qApp.currentClientId())
        recClPolicy = self.db.getRecordEx('ClientPolicy', 'insurer_id, policyKind_id, serial, number',
                                          'client_id = %s AND (endDate > CURDATE() OR endDate IS NULL) AND policyKind_id IS NOT NULL AND deleted = 0' % QtGui.qApp.currentClientId())
        recBedProfile = self.db.getRecordEx('rbHospitalBedProfile', 'regionalCode',
                                            'code = %s' % forceString(refInfo['bedProfile']))
        recCMO = ''
        recPolicyKind = ''
        errors = ShowError()
        if recClPolicy:
            recCMO = self.db.getRecordEx('Organisation', 'infisCode, OKATO',
                                         'id = %s' % forceString(recClPolicy.value('insurer_id')))
            recPolicyKind = self.db.getRecordEx('rbPolicyKind', 'regionalCode',
                                                'id = %s' % forceString(recClPolicy.value('policyKind_id')))

        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:app="http://www.rintech.ru/isomp/appointment_referral">')
        msg.addField(u'<app:UploadRowsRequest app:user_name="%s">' % user)
        msg.addSection(u'app:InputRow')
        msg.addField(
            u'<app:ReferralDate>%s</app:ReferralDate>' % forceDate(refInfo['refDate']).toString('yyyy-MM-dd') if
            refInfo['refDate'] else errors.addError(u'Не заполнена дата направления'))
        msg.addField(u'<app:ReferralNumber>%s</app:ReferralNumber>' % forceString(refInfo['number']) if refInfo[
            'number'] else errors.addError(u'Не введен номер направления'))
        msg.addField(u'<app:HospitalizationPlannedDate>%s</app:HospitalizationPlannedDate>' % forceDate(
            refInfo['refPlanDate']).toString('yyyy-MM-dd'))
        msg.addField(u'<app:HospitalizationTimeAgreementSign>%s</app:HospitalizationTimeAgreementSign>' % forceString(
            refInfo['agreement']))
        msg.addField(
            u'<app:PolyclinicInstitutionReestrNumber>%s</app:PolyclinicInstitutionReestrNumber>' % forceString(user))
        msg.addField(u'<app:MedicalPerson>%s</app:MedicalPerson>' % (
            forceString(recPerson.value('lastName')) + ' ' + forceString(
                recPerson.value('firstName')) + ' ' + forceString(
                recPerson.value('patrName'))))
        msg.addField(
            u'<app:HospitalInstitutionReestrNumber>%s</app:HospitalInstitutionReestrNumber>' % forceString(user))
        msg.addField(u'<app:HealthcareTypeCode>%s</app:HealthcareTypeCode>' % refInfo['order'] if refInfo[
            'order'] else errors.addError(u'Не выбран тип госпитализации'))
        msg.addField(u'<app:PatientLastName>%s</app:PatientLastName>' % forceString(recClient.value('lastName')))
        msg.addField(u'<app:PatientFirstName>%s</app:PatientFirstName>' % forceString(recClient.value('firstName')))
        msg.addField(u'<app:PatientMiddleName>%s</app:PatientMiddleName>' % forceString(recClient.value('patrName')))
        msg.addField(u'<app:PatientGenderCode>%s</app:PatientGenderCode>' % forceString(recClient.value('sex')))
        msg.addField(
            u'<app:PatientDateOfBirth>%s</app:PatientDateOfBirth>' % forceDate(recClient.value('birthDate')).toString(
                'yyyy-MM-dd'))
        msg.addField(u'<app:PatientEmploymentInfo>не определено, не определено</app:PatientEmploymentInfo>')
        msg.addField(u'<app:PatientContactInfo>%s</app:PatientContactInfo>' % forceString(
            recCont.value('contact')) if recCont else errors.addError(u'У клиента не заполнены контакты'))
        msg.addField(u'<app:SubjectOfRfOkato>%s</app:SubjectOfRfOkato>' % forceString(
            recCMO.value('OKATO')) if recCMO and forceString(recCMO.value('OKATO')) else errors.addError(
            u'Не удались найти код ОКАТО СМО'))
        msg.addField(u'<app:InsuranceCompanyReestrNumber>%s</app:InsuranceCompanyReestrNumber>' % forceString(
            recCMO.value('infisCode')) if recCMO else errors.addError(
            u'Не удалось найти СМО в которой застрахован клиент'))
        msg.addField(u'<app:InsuranceDocumentTypeCode>%s</app:InsuranceDocumentTypeCode>' % forceString(
            recPolicyKind.value('regionalCode')) if recPolicyKind else errors.addError(
            u'У клиента не выбран тип полиса'))
        msg.addField(u'<app:InsuranceDocumentSeries>%s</app:InsuranceDocumentSeries>' % forceString(
            recClPolicy.value('serial')) if recClPolicy else errors.addError(
            u'У клиента не внесен полис или не задан тип полиса'))
        msg.addField(u'<app:InsuranceDocumentNumber>%s</app:InsuranceDocumentNumber>' % forceString(
            recClPolicy.value('number')) if recClPolicy else errors.addError(
            u'У клиента не внесен полис или не задан тип полиса'))
        msg.addField(u'<app:BedProfileCode>%s</app:BedProfileCode>' % forceString(
            recBedProfile.value('regionalCode')) if recBedProfile else errors.addError(u'Не выбран код профиля койки'))
        msg.addField(
            u'<app:Icd10SubcategoryCode>%s</app:Icd10SubcategoryCode>' % forceString(refInfo['MKB']) if refInfo[
                'MKB'] else errors.addError(u'Не заполнен код МКБ'))
        msg.closeSection(u'app:InputRow')
        msg.closeSection(u'app:UploadRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        if errors.getErrors():
            errors.showError()
        else:
            msg.sendMessage(self.url + '/sdat_vpol/owner_appointment_referral_upload')
        try:
            if xml.etree.ElementTree.fromstring(msg.getResult()):
                return True
        except:
            return False

    # Предоставление сведений об экстренной госпитализации и о госпитализации по направлению
    def owner_hospital_admission_upload(self, eventId, refNum):
        recEvent = self.db.getRecordEx('Event', '*', 'id = %s' % forceString(eventId))
        recClient = self.db.getRecordEx('Client', '*', 'id = %s' % forceString(recEvent.value('client_id')))
        recPolicy = self.db.getRecordEx('ClientPolicy', '*', 'client_id = %s AND endDate IS NULL' % forceString(
            recEvent.value('client_id')))
        recRef = self.db.getRecordEx('Referral', '*',
                                     "client_id = %s ORDER BY id" % forceString(recEvent.value('client_id')))
        recMKB = self.db.getRecordEx('Action', 'MKB', 'event_id = %s AND MKB NOT IS NULL' % eventId)
        recBed = self.db.query(stmts.stmtCBedProfile % eventId)
        if recRef:
            recRelMO = self.db.getRecordEx('Organisation', 'infisCode',
                                           'id = %s' % recRef.value('relegateOrg_id'))
        if recPolicy:
            recSMO = self.db.getRecordEx('Organisation', '*',
                                         'id = %s' % forceString(recPolicy.value('insurer_id')))
            recPolicyType = self.db.getRecordEx('rbPolicyKind', 'federalCode',
                                                'id = %s' % recPolicy.value('policyKind_id'))
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hos="http://www.rintech.ru/isomp/hospital_admission" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
        msg.addField(u'<hos:UploadRowsRequest hos:user_name="%s">' % config.userName)
        msg.addSection(u'hos:InputRow')
        msg.addField(
            u'<hos:AdmissionDate>%s</hos:AdmissionDate>' % forceDate(recEvent.value('setDate')).toString('yyyy-MM-dd'))
        msg.addField(u'<hos:AdmissionTime>%s</hos:AdmissionTime>' % forceString(QtCore.QTime.currentTime()))
        msg.addField(u'<hos:RehospitalizationSign xsi:nil="true">0</hos:RehospitalizationSign>')
        msg.addField(
            u'<hos:ReferralDate>%s</hos:ReferralDate>' % forceDate(recRef.value('date')).toString('yyyy-MM-dd'))
        msg.addField(u'<hos:ReferralNumber>%s</hos:ReferralNumber>' % forceString(recRef.value('number')))
        msg.addField(u'<hos:PolyclinicInstitutionReestrNumber>%s</hos:PolyclinicInstitutionReestrNumber>' % forceString(
            recRelMO.value('infisCode')))
        msg.addField(u'<hos:PolyclinicUnitCode xsi:nil="true" />')
        msg.addField(u'<hos:PolyclinicDepartmentCode xsi:nil="true" />')
        msg.addField(u'<hos:HospitalInstitutionReestrNumber>%s</hos:HospitalInstitutionReestrNumber>' % forceString(
            config.userName))
        msg.addField(u'<hos:HospitalUnitCode xsi:nil="true" />')
        msg.addField(u'<hos:HospitalDepartmentCode xsi:nil="true" />')
        msg.addField(u'<hos:MedicalPerson>%s</hos:MedicalPerson>' % forceString(recEvent.value('setPerson_id')))
        msg.addField(u'<hos:HealthcareTypeCode>%s</hos:HealthcareTypeCode>' % forceString(recEvent.value('order')))
        msg.addField(u'<hos:PatientLastName>%s</hos:PatientLastName>' % forceString(recClient.value('lastName')))
        msg.addField(u'<hos:PatientFirstName>%s</hos:PatientFirstName>' % forceString(recClient.value('firstName')))
        msg.addField(u'<hos:PatientMiddleName>%s</hos:PatientMiddleName>' % forceString(recClient.value('patrName')))
        msg.addField(u'<hos:PatientGenderCode>%s</hos:PatientGenderCode>' % forceString(recClient.value('sex')))
        msg.addField(
            u'<hos:PatientDateOfBirth>%s</hos:PatientDateOfBirth>' % forceDate(recClient.value('birthDate')).toString(
                'yyyy-MM-dd'))
        if recPolicy:
            msg.addField(u'<hos:PatientInsuranceRegisterSign>1</hos:PatientInsuranceRegisterSign>')
            msg.addField(u'<hos:SubjectOfRfOkato>%s</hos:SubjectOfRfOkato>' % forceString(recSMO.value('OKATO')))
            msg.addField(u'<hos:InsuranceCompanyReestrNumber>%s</hos:InsuranceCompanyReestrNumber>' % forceString(
                recSMO.value('infisCode')))
            msg.addField(u'<hos:InsuranceDocumentTypeCode>%s</hos:InsuranceDocumentTypeCode>' % forceString(
                recPolicyType.value('federalCode')))
            msg.addField(u'<hos:InsuranceDocumentSeries xsi:nil="true">%s</hos:InsuranceDocumentSeries>' % forceString(
                recPolicy.value('serial')))
            msg.addField(u'<hos:InsuranceDocumentNumber>%s</hos:InsuranceDocumentNumber>' % forceString(
                recPolicy.value('number')))
        else:
            msg.addField(u'<hos:PatientInsuranceRegisterSign>0</hos:PatientInsuranceRegisterSign>')
        if recBed.next():
            msg.addField(u'<hos:BedProfileCode>%s</hos:BedProfileCode>' % forceString(recBed.value(0)))
        msg.addField(u'<hos:HospitalCardNumber>%s</hos:HospitalCardNumber>' % forceString(recEvent.value('client_id')))
        msg.addField(u'<hos:Icd10SubcategoryCode>%s</hos:Icd10SubcategoryCode>' % forceString(
            recMKB.value('MKB')) if recMKB else '-')
        msg.closeSection(u'hos:InputRow')
        msg.closeSection(u'hos:UploadRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sdat_vhos/owner_hospital_admission_upload')
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/hospital_admission}UploadRowsResponse')
        root = root.find('{http://www.rintech.ru/isomp/hospital_admission}OutputRow')
        if root.find('{http://www.rintech.ru/isomp/hospital_vacancy}Id'):
            return True
        else:
            return False

    # Предоставление сведений об экстренной госпитализации и о госпитализации по направлению
    def owner_hospital_admission_upload(self, eventId):
        msg = CPrepareSoap()
        recEvent = self.db.getRecordEx('Event', '*', 'id = %s' % forceString(eventId))
        recClient = self.db.getRecordEx('Client', '*', 'id = %s' % forceString(recEvent.value('client_id')))
        recPolicy = self.db.getRecordEx('ClientPolicy', '*', 'client_id = %s AND endDate IS NULL' % forceString(
            recEvent.value('client_id')))
        recRef = self.db.getRecordEx('Referral', '*',
                                     "client_id = %s ORDER BY id" % forceString(recEvent.value('client_id')))
        recMKB = self.db.getRecordEx('Action', 'MKB', 'event_id = %s AND MKB NOT IS NULL' % eventId)
        recBed = self.db.query(stmts.stmtCBedProfile % eventId)
        if recRef:
            recRelMO = self.db.getRecordEx('Organisation', 'infisCode',
                                           'id = %s' % recRef.value('relegateOrg_id'))
        if recPolicy:
            recSMO = self.db.getRecordEx('Organisation', '*',
                                         'id = %s' % forceString(recPolicy.value('insurer_id')))
            recPolicyType = self.db.getRecordEx('rbPolicyKind', 'federalCode',
                                                'id = %s' % recPolicy.value('policyKind_id'))
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hos="http://www.rintech.ru/isomp/hospital_admission" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
        msg.addField(u'<hos:UploadRowsRequest hos:user_name="%s">' % config.userName)
        msg.addSection(u'hos:InputRow')
        msg.addField(
            u'<hos:AdmissionDate>%s</hos:AdmissionDate>' % forceDate(recEvent.value('setDate')).toString(
                'yyyy-MM-dd'))
        msg.addField(u'<hos:AdmissionTime>%s</hos:AdmissionTime>' % forceString(QtCore.QTime.currentTime()))
        msg.addField(u'<hos:RehospitalizationSign xsi:nil="true">0</hos:RehospitalizationSign>')
        msg.addField(
            u'<hos:ReferralDate>%s</hos:ReferralDate>' % forceDate(recRef.value('date')).toString('yyyy-MM-dd'))
        msg.addField(u'<hos:ReferralNumber>%s</hos:ReferralNumber>' % forceString(recRef.value('number')))
        msg.addField(
            u'<hos:PolyclinicInstitutionReestrNumber>%s</hos:PolyclinicInstitutionReestrNumber>' % forceString(
                recRelMO.value('infisCode')))
        msg.addField(u'<hos:PolyclinicUnitCode xsi:nil="true" />')
        msg.addField(u'<hos:PolyclinicDepartmentCode xsi:nil="true" />')
        msg.addField(
            u'<hos:HospitalInstitutionReestrNumber>%s</hos:HospitalInstitutionReestrNumber>' % forceString(
                config.userName))
        msg.addField(u'<hos:HospitalUnitCode xsi:nil="true" />')
        msg.addField(u'<hos:HospitalDepartmentCode xsi:nil="true" />')
        msg.addField(u'<hos:MedicalPerson>%s</hos:MedicalPerson>' % forceString(recEvent.value('setPerson_id')))
        msg.addField(
            u'<hos:HealthcareTypeCode>%s</hos:HealthcareTypeCode>' % forceString(recEvent.value('order')))
        msg.addField(
            u'<hos:PatientLastName>%s</hos:PatientLastName>' % forceString(recClient.value('lastName')))
        msg.addField(
            u'<hos:PatientFirstName>%s</hos:PatientFirstName>' % forceString(recClient.value('firstName')))
        msg.addField(
            u'<hos:PatientMiddleName>%s</hos:PatientMiddleName>' % forceString(recClient.value('patrName')))
        msg.addField(u'<hos:PatientGenderCode>%s</hos:PatientGenderCode>' % forceString(recClient.value('sex')))
        msg.addField(u'<hos:PatientDateOfBirth>%s</hos:PatientDateOfBirth>' % forceDate(
            recClient.value('birthDate')).toString('yyyy-MM-dd'))
        if recPolicy:
            msg.addField(u'<hos:PatientInsuranceRegisterSign>1</hos:PatientInsuranceRegisterSign>')
            msg.addField(
                u'<hos:SubjectOfRfOkato>%s</hos:SubjectOfRfOkato>' % forceString(recSMO.value('OKATO')))
            msg.addField(
                u'<hos:InsuranceCompanyReestrNumber>%s</hos:InsuranceCompanyReestrNumber>' % forceString(
                    recSMO.value('infisCode')))
            msg.addField(u'<hos:InsuranceDocumentTypeCode>%s</hos:InsuranceDocumentTypeCode>' % forceString(
                recPolicyType.value('federalCode')))
            msg.addField(
                u'<hos:InsuranceDocumentSeries xsi:nil="true">%s</hos:InsuranceDocumentSeries>' % forceString(
                    recPolicy.value('serial')))
            msg.addField(u'<hos:InsuranceDocumentNumber>%s</hos:InsuranceDocumentNumber>' % forceString(
                recPolicy.value('number')))
        else:
            msg.addField(u'<hos:PatientInsuranceRegisterSign>0</hos:PatientInsuranceRegisterSign>')
        if recBed.next():
            msg.addField(u'<hos:BedProfileCode>%s</hos:BedProfileCode>' % forceString(recBed.value(0)))
        msg.addField(
            u'<hos:HospitalCardNumber>%s</hos:HospitalCardNumber>' % forceString(recEvent.value('client_id')))
        msg.addField(u'<hos:Icd10SubcategoryCode>%s</hos:Icd10SubcategoryCode>' % forceString(
            recMKB.value('MKB')) if recMKB else '-')
        msg.closeSection(u'hos:InputRow')
        msg.closeSection(u'hos:UploadRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sdat_vhos/owner_hospital_admission_upload')
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/hospital_admission}UploadRowsResponse')
        root = root.find('{http://www.rintech.ru/isomp/hospital_admission}OutputRow')
        if root.find('{http://www.rintech.ru/isomp/hospital_vacancy}Id'):
            return True
        else:
            return False

    # Предоставление сведений о записи в стационар
    def owner_appointment_queue_upload(self, data, isPolyclinic):
        user = forceString(QtGui.qApp.preferences.appPrefs['referralServiceUser'])
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:app="http://www.rintech.ru/isomp/appointment_queue" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
        msg.addField(u'<app:UploadRowsRequest app:user_name="%s">' % user)
        msg.addSection(u'app:InputRow')
        msg.addField(
            u'<app:EnqueuingDate>%s</app:EnqueuingDate>' % forceDate(QtCore.QDate.currentDate()).toString('yyyy-MM-dd'))
        msg.addField(u'<app:EnqueuingTime>%s</app:EnqueuingTime>' % QtCore.QTime.currentTime().toString('hh:mm:ss'))
        msg.addField(u'<app:ReferralDate>%s</app:ReferralDate>' % forceString(data['referralDate']))
        msg.addField(u'<app:ReferralNumber>%s</app:ReferralNumber>' % forceString(data['referralNumber']))
        msg.addField(
            u'<app:PolyclinicInstitutionReestrNumber>%s</app:PolyclinicInstitutionReestrNumber>' % forceString(user))
        msg.addField(u'<app:PolyclinicUnitCode xsi:nil="true"/>')
        msg.addField(u'<app:PolyclinicDepartmentCode xsi:nil="true"/>')
        msg.addField(
            u'<app:HospitalInstitutionReestrNumber>%s</app:HospitalInstitutionReestrNumber>' % forceString(user))
        msg.addField(u'<app:HospitalUnitCode xsi:nil="true"/>')
        msg.addField(u'<app:HospitalDepartmentCode xsi:nil="true"/>')
        msg.addField(u'<app:BedProfileCode>%s</app:BedProfileCode>' % forceString(data['bedProfile']))
        msg.addField(u'<app:Icd10SubcategoryCode>%s</app:Icd10SubcategoryCode>' % forceString(u'2'))
        msg.addField(u'<app:EnqueuingSourceCode>%s</app:EnqueuingSourceCode>' % forceString(u'2'))
        msg.addField(u'<app:EnqueuingSourceReestrNumber>%s</app:EnqueuingSourceReestrNumber>' % forceString(user))
        msg.addField(u'<app:EnqueuingSourceUnitCode xsi:nil="true"/>')
        msg.addField(u'<app:EnqueuingSourceDepartmentCode xsi:nil="true"/>')
        msg.addField(u'<app:ResponsiblePerson xsi:nil="true"/>')
        msg.addField(u'<app:EnqueuingPurposeCode>%s</app:EnqueuingPurposeCode>' % forceString(u'1'))
        msg.addField(
            u'<app:SelectionCommissionCode>%s</app:SelectionCommissionCode>' % forceString(data['commisionCode']))
        msg.addField(u'<app:AttendanceDate>%s</app:AttendanceDate>' % forceString(data['attendanceDate']))
        msg.addField(u'<app:AttendanceTime>%s</app:AttendanceTime>' % forceString(data['attendanceTime']))
        msg.closeSection(u'app:InputRow')
        msg.closeSection(u'app:UploadRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        if isPolyclinic:
            msg.sendMessage(self.url + '/sdat_vpol/owner_appointment_queue_upload ')
        else:
            msg.sendMessage(self.url + '/sdat_vhos/owner_appointment_queue_upload')
        response = msg.getResult()
        root = xml.etree.ElementTree.fromstring(response)
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/appointment_queue}UploadRowsResponse')
        root = root.find('{http://www.rintech.ru/isomp/appointment_queue}OutputRow')
        root = root.find('{http://www.rintech.ru/isomp/appointment_queue}Id')
        if root is not None:
            return True
        else:
            return False

    # Предоставление сведений о расписании
    def owner_selection_commission_timetable_period_upload(self):
        recPersons = self.db.query("SELECT id FROM Person WHERE code = 'comission'")
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:sel="http://www.rintech.ru/isomp/selection_commission_timetable_period">')
        msg.addField(u'<sel:UploadRowsRequest sel:user_name="%s">' % config.userName)
        while recPersons.next():
            recEvent = (
                "SELECT * FROM Event WHERE type_id = (SELECT id FROM EventType WHERE code = 0) AND setPerson_id = %s AND setDate >= CURDATE()" % forceString(
                    recPersons.value(0)))
            if recEvent.next():
                recPt = self.db.query(stmts.graphicInfo % recEvent.value(0))
                startTime = 0
                endTime = 0
                times = []
                addInfo = 0
                startDate = forceDate(min(recEvent.value(12)))
                endDate = forceDate(max(recEvent.value(12)))
                recStTime = self.db.getRecordEx('ActionPropertyType', 'id', "name = 'begTime'")
                recEndTime = self.db.getRecordEx('ActionPropertyType', 'id', "name = 'endTime'")
                recTimes = self.db.getRecordEx('ActionPropertyType', 'id', "name = 'times'")
                recAddInfo = self.db.getRecordEx('ActionPropertyType', 'id', "name = 'office'")
                while recPt.next():
                    if forceString(recStTime.value('id')) == forceString(recPt.value(1)):
                        startTime = self.db.getRecordEx('ActionProperty_Time', 'value',
                                                        'id = %s' % forceString(recPt.value(0)))
                    elif forceString(recEndTime.value('id')) == forceString(recPt.value(1)):
                        endTime = self.db.getRecordEx('ActionProperty_Time', 'value',
                                                      'id = %s' % forceString(recPt.value(0)))
                    elif forceString(recTimes.value('id')) == forceString(recPt.value(1)):
                        timesRec = self.db.query('ActionProperty_Time', 'id', 'id = %s' % forceString(recPt.value(0)))
                        while timesRec.next():
                            times.append(timesRec.value(0))
                    elif forceString(recAddInfo.value('id')) == forceString(recPt.value(1)):
                        addInfo = self.db.getRecordEx('ActionProperty_String', 'value',
                                                      'id = %s' % forceString(recPt.value(0)))
                msg.addSection(u'sel:InputRow')
                msg.addField(u'<sel:SelectionCommissionCode>%s</sel:SelectionCommissionCode>' % forceString(
                    config.userName + forceString(recPersons.value(0))))
                msg.addField(u'<sel:TimetablePeriodCode>D</sel:TimetablePeriodCode>')
                msg.addField(
                    u'<sel:StartDate>%s</sel:StartDate>' % forceDate(startDate.value('value')).toString('yyyy-MM-dd'))
                msg.addField(
                    u'<sel:FinishDate>%s</sel:FinishDate>' % forceDate(endDate.value('value')).toString('yyyy-MM-dd'))
                msg.addField(
                    u'<sel:BeginTime xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">%s</sel:BeginTime>' % forceString(
                        startTime))
                msg.addField(
                    u'<sel:EndTime xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">%s</sel:EndTime>' % forceString(
                        endTime))
                msg.addField(u'<sel:PriorityLevel>1</sel:PriorityLevel>')
                msg.addField(u'<sel:AdditionalInfo>%s</sel:AdditionalInfo>' % forceString(addInfo.value('value')))
                msg.addField(u'<sel:AttendanceLimit>%s</sel:AttendanceLimit>' % forceString(len(times)))
                msg.addField(u'<sel:TimetableDescription>-</sel:TimetableDescription>')
                msg.closeSection(u'sel:InputRow')
        msg.closeSection(u'sel:UploadRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sref_vhos/owner_selection_commission_timetable_period_upload')
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/hospital_admission}UploadRowsResponse')
        root = root.find('{http://www.rintech.ru/isomp/hospital_admission}OutputRow')
        if root.find('{http://www.rintech.ru/isomp/hospital_vacancy}Id'):
            return True
        else:
            return False

    # Получение сведений о записи на явку в стационар в т.ч. для прохождения коммисии
    def user_appointment_queue_cancelled_sign_filter(self, data):
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:app="http://www.rintech.ru/isomp/appointment_queue_cancelled_sign" xmlns:pla="http://www.rintech.ru/isomp/plainrows">')
        msg.addField(
            u'<app:FilterRowsRequest app:user_name="%s" app:rows_max="10" app:d_filter="0" app:order_by="AttendanceDate+AttendanceTime+">' % config.userName)
        msg.addField(
            u'<app:FilterRow xmlns="http://www.rintech.ru/isomp/appointment_queue_cancelled_sign" xmlns:ipr="http://www.rintech.ru/isomp/plainrows">')
        msg.addField(u'<HospitalInstitutionReestrNumber>%s</HospitalInstitutionReestrNumber>' % forceString(
            data['infisCodePolyclinic']))
        msg.addField(u'<SelectionCommissionCode>%s</SelectionCommissionCode>' % forceString(data['commisionCode']))
        msg.addField(u'<AttendanceDate>%s</AttendanceDate>' % forceString(data['attendanceDate']))
        msg.addField(u'<AttendanceCancelledSign>0</AttendanceCancelledSign>' % forceString(data['cancelled']))
        msg.addField(u'<HospitalAdmittedSign>%s</HospitalAdmittedSign>' % forceString(data['hospitalisation']))
        msg.addField(u'<EnqueuingLatestSign>%s</EnqueuingLatestSign>' % forceString(data['latestSign']))
        msg.closeSection(u'app:FilterRow')
        msg.closeSection(u'app:FilterRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sdat_vany/user_appointment_queue_cancelled_sign_filter')
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}FilterRowsResponse')
        resultList = []
        for i in root:
            elem = root.find('{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}ResultRow')
            resultDict = {}
            resultDict['HospitalInstitutionReestrNumber'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}HospitalInstitutionReestrNumber').text
            resultDict['HospitalInstitutionShortName'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}HospitalInstitutionShortName').text
            resultDict['HospitalUnitCode'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}HospitalUnitCode').text
            resultDict['HospitalUnitName'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}HospitalUnitName').text
            resultDict['HospitalDepartmentCode'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}HospitalDepartmentCode').text
            resultDict['HospitalDepartmentName'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}HospitalDepartmentName').text
            resultDict['BedProfileCode'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}BedProfileCode').text
            resultDict['BedProfileName'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}BedProfileName').text
            resultDict['SelectionCommissionCode'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}SelectionCommissionCode').text
            resultDict['SelectionCommissionName'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}SelectionCommissionName').text
            resultDict['AttendanceDate'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}AttendanceDate').text
            resultDict['AttendanceTime'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}AttendanceTime').text
            resultDict['AttendanceCancelledSign'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}AttendanceCancelledSign').text
            resultDict['AppointmentCancelledSign'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}AppointmentCancelledSign').text
            resultDict['HospitalAdmittedSign'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}HospitalAdmittedSign').text
            resultDict['EnqueuingLatestSign'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}EnqueuingLatestSign').text
            resultDict['Id'] = elem.find('{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}Id').text
            resultDict['InputId'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}InputId').text
            resultDict['SourceLine'] = elem.find(
                '{http://www.rintech.ru/isomp/appointment_queue_cancelled_sign}SourceLine').text
            resultList.append(resultDict)
        return resultList

    # Получение сведений о направлении на госпитализацию
    def user_appointment_referral_filter(self):
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:app="http://www.rintech.ru/isomp/appointment_referral" xmlns:pla="http://www.rintech.ru/isomp/plainrows">')
        msg.addField(
            u'<app:FilterRowsRequest app:user_name="%s" app:rows_max="10" app:d_filter="0" app:order_by="ReferralDate-ReferralNumber+">' % config.userName)
        msg.addSection(u'app:FilterRow')
        msg.closeSection(u'app:FilterRow')
        msg.closeSection(u'app:FilterRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(config.url + '/sdat_vhos/user_appointment_referral_filter')
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/appointment_referral}FilterRowsResponse')
        resultList = []
        for i in root:
            resultDict = {}
            element = root.find('{http://www.rintech.ru/isomp/appointment_referral}ResultRow')
            if element:
                resultDict['ReferralDate'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}ReferralDate').text
                resultDict['ReferralNumber'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}ReferralNumber').text
                resultDict['HospitalizationPlannedDate'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalizationPlannedDate').text
                resultDict['HospitalizationTimeAgreementSign'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalizationTimeAgreementSign').text
                resultDict['PolyclinicInstitutionReestrNumber'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PolyclinicInstitutionReestrNumber').text
                resultDict['PolyclinicInstitutionShortName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PolyclinicInstitutionShortName').text
                resultDict['PolyclinicUnitCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PolyclinicUnitCode').text
                resultDict['PolyclinicUnitName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PolyclinicUnitName').text
                resultDict['PolyclinicDepartmentCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PolyclinicDepartmentCode').text
                resultDict['PolyclinicDepartmentName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PolyclinicDepartmentName').text
                resultDict['MedicalPerson'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}MedicalPerson').text
                resultDict['HospitalInstitutionReestrNumber'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalInstitutionReestrNumber').text
                resultDict['HospitalInstitutionShortName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalInstitutionShortName').text
                resultDict['HospitalUnitCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalUnitCode').text
                resultDict['HospitalUnitName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalUnitName').text
                resultDict['HospitalDepartmentCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalDepartmentCode').text
                resultDict['HospitalDepartmentName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalDepartmentName').text
                resultDict['HealthcareTypeCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HealthcareTypeCode').text
                resultDict['HealthcareTypeName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HealthcareTypeName').text
                resultDict['PatientLastName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientLastName').text
                resultDict['PatientFirstName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientFirstName').text
                resultDict['PatientMiddleName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientMiddleName').text
                resultDict['PatientGenderCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientGenderCode').text
                resultDict['PatientGenderName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientGenderName').text
                resultDict['PatientDateOfBirth'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientDateOfBirth').text
                resultDict['PatientInsuranceRegisterSign'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientInsuranceRegisterSign').text
                resultDict['MedicalBenefitCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}MedicalBenefitCode').text
                resultDict['MedicalBenefitName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}MedicalBenefitName').text
                resultDict['PatientResidenceAddress'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientResidenceAddress').text
                resultDict['PatientEmploymentInfo'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientEmploymentInfo').text
                resultDict['PatientContactInfo'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}PatientContactInfo').text
                resultDict['AdditionalInfo'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}AdditionalInfo').text
                resultDict['SubjectOfRfOkato'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}SubjectOfRfOkato').text
                resultDict['SubjectOfRfName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}SubjectOfRfName').text
                resultDict['InsuranceCompanyReestrNumber'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}InsuranceCompanyReestrNumber').text
                resultDict['InsuranceCompanyShortName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}InsuranceCompanyShortName').text
                resultDict['InsuranceDocumentTypeCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}InsuranceDocumentTypeCode').text
                resultDict['InsuranceDocumentTypeName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}InsuranceDocumentTypeName').text
                resultDict['InsuranceDocumentSeries'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}InsuranceDocumentSeries').text
                resultDict['InsuranceDocumentNumber'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}InsuranceDocumentNumber').text
                resultDict['BedProfileCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}BedProfileCode').text
                resultDict['BedProfileName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}BedProfileName').text
                resultDict['Icd10SubcategoryCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}Icd10SubcategoryCode').text
                resultDict['Icd10SubcategoryName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}Icd10SubcategoryName').text
                resultDict['Icd10CategoryCode'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}Icd10CategoryCode').text
                resultDict['Icd10CategoryName'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}Icd10CategoryName').text
                resultDict['AppointmentCancelledSign'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}AppointmentCancelledSign').text
                resultDict['HospitalAdmittedSign'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}HospitalAdmittedSign').text
                resultDict['Id'] = element.find('{http://www.rintech.ru/isomp/appointment_referral}Id').text
                resultDict['InputId'] = element.find('{http://www.rintech.ru/isomp/appointment_referral}InputId').text
                resultDict['SourceLine'] = element.find(
                    '{http://www.rintech.ru/isomp/appointment_referral}SourceLine').text
                resultList.append(resultDict)
        return resultList

    # Отправка данных о выбывших пациентах
    def owner_hospital_discharge_upload(self, eventId):
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hos="http://www.rintech.ru/isomp/hospital_discharge" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
        msg.addField(u'<hos:UploadRowsRequest hos:user_name="%s">' % config.userName)
        msg.addSection(u'hos:InputRow')
        recEvent = self.db.getRecordEx('Event', '*', 'id = %s' % forceString(eventId))
        recDiag = self.db.getRecordEx('Diagnosis', '*', 'client_id = %s' % forceString(QtGui.qApp.currentClientId()))
        recClient = self.db.getRecordEx('Client', '*', 'id = %s' % forceString(recEvent.value('client_id')))
        recRef = self.db.getRecordEx('Referral', '*',
                                     "client_id = %s ORDER BY id" % forceString(recEvent.value('client_id')))
        recCd = self.db.query(stmts.stmtCBedProfile % forceString(eventId))
        recResult = self.db.getRecordEx('rbResult', 'regionalCode',
                                        'id = %s' % forceString(recEvent.value('result_id')))
        msg.addField(
            u'<hos:DischargeDate>%s</hos:DischargeDate>' % forceDate(recEvent.value('execDate')).toString('yyyy-MM-dd'))
        msg.addField(
            u'<hos:AdmissionDate>%s</hos:AdmissionDate>' % forceDate(recEvent.value('setDate')).toString('yyyy-MM-dd'))
        if recRef:
            msg.addField(
                u'<hos:ReferralDate>%s</hos:ReferralDate>' % forceDate(recRef.value('date')).toString('yyyy-MM-dd'))
            msg.addField(u'<hos:ReferralNumber>%s</hos:ReferralNumber>' % forceString(recRef.value('number')))
        msg.addField(u'<hos:HospitalInstitutionReestrNumber>%s</hos:HospitalInstitutionReestrNumber>' % config.userName)
        msg.addField(u'<hos:HospitalUnitCode xsi:nil="true"/>')
        msg.addField(u'<hos:HospitalDepartmentCode xsi:nil="true"/>')
        msg.addField(u'<hos:HealthcareTypeCode>%s</hos:HealthcareTypeCode>' % forceString(recEvent.value('order')))
        if recClient:
            msg.addField(u'<hos:PatientGenderCode>%s</hos:PatientGenderCode>' % forceString(recClient.value('sex')))
            msg.addField(u'<hos:PatientDateOfBirth>%s</hos:PatientDateOfBirth>' % forceDate(
                recClient.value('birthDate')).toString('yyyy-MM-dd'))
        msg.addField(u'<hos:HealthcareProfileCode>1</hos:HealthcareProfileCode>')
        if recCd.next():
            msg.addField(u'<hos:BedProfileCode>%s</hos:BedProfileCode>' % forceString(recCd.value(0)))
        if recClient:
            msg.addField(u'<hos:HospitalCardNumber>%s-%s</hos:HospitalCardNumber>' % (
                forceString(recClient.value('id')), forceString(recClient.value('id'))))
        msg.addField(u'<hos:Icd10SubcategoryCode>%s</hos:Icd10SubcategoryCode>' % forceString(recDiag.value('MKB')))
        if recResult:
            msg.addField(
                u'<hos:DischargeReasonCode>%s</hos:DischargeReasonCode>' % forceString(recResult.value('regionalCode')))
        msg.closeSection(u'hos:InputRow')
        msg.closeSection(u'hos:UploadRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(config.url + '/sdat_vhos/owner_hospital_discharge_upload')
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/hospital_discharge}UploadRowsResponse')
        root = root.find('{http://www.rintech.ru/isomp/hospital_discharge}OutputRow')
        if root.find('{http://www.rintech.ru/isomp/hospital_vacancy}Id'):
            return True
        else:
            return False

    # Коечный фонд
    def owner_hospital_vacancy_upload(self):
        msg = CPrepareSoap()
        msg.addHeader(
            u'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hos="http://www.rintech.ru/isomp/hospital_vacancy">')
        msg.addField(u'<hos:UploadRowsRequest hos:user_name="%s">' % config.userName)
        listLeavers = self.db.query(stmts.movingPatientsList % (self.begDate, self.endDate))
        bedList = []
        while listLeavers.next():
            record = self.db.getRecordEx(stmt=stmts.stmtCBedProfile % forceString(listLeavers.value(0)))
            if record and not forceString(record.value('hospBedProfile')) in bedList:
                if forceString(record.value('hospBedProfile')):
                    bedList.append(forceString(record.value('hospBedProfile')))
                    profileBed = self.db.getRecordEx('rbHospitalBedProfile', 'id, regionalCode',
                                                     'code = %s' % forceString(record.value('hospBedProfile')))

                    # Список евентов за сутки
                    eventsList = self.db.query(
                        stmts.stmtEventList % (self.begDate, self.endDate, forceString(record.value('hospBedProfile'))))

                    table = self.db.table('OrgStructure_HospitalBed')
                    tableOrg = self.db.table('OrgStructure')
                    tableEx = table.join(tableOrg, tableOrg['id'].eq(table['master_id']))

                    freeBedsList = self.db.getIdList(tableEx, idCol=table['id'].name(),
                                                     where='isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\') AND profile_id = %s'
                                                           % (
                                                               self.endDate,
                                                               forceString(profileBed.value('regionalCode'))))

                    # Количество поступивших
                    hospCount = 0
                    while eventsList.next():
                        hospList = self.db.query(stmts.stmtNewPatients % (
                            forceString(eventsList.value(0)), forceString(profileBed.value('id'))))
                        while hospList.next():
                            hospCount += 1

                    # Количество выбывших
                    leavedCount = 0
                    while eventsList.next():
                        leavedList = self.db.query(stmts.stmtLeavedPatients % (
                            forceString(eventsList.value(0)), forceString(profileBed.value('id'))))
                        while leavedList.next():
                            leavedCount += 1

                    # всего коек по профилю
                    freeBeds = 0
                    totalList = self.db.query(
                        "SELECT id FROM OrgStructure_HospitalBed WHERE NOT isHospitalBedBusy(OrgStructure_HospitalBed.id, \'" + self.begDate + " \') AND profile_id = " + forceString(
                            profileBed.value('id')))
                    while totalList.next():
                        freeBeds += 1

                    # Незанятых мужских коек
                    freeBedsMaleList = self.db.getIdList(tableEx, idCol=table['id'].name(),
                                                         where='NOT isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\') AND OrgStructure_HospitalBed.sex=1 AND profile_id = %s'
                                                               % (self.endDate, forceString(profileBed.value('id'))))

                    # Незанятых женских коек
                    freeBedsFemaleList = self.db.getIdList(tableEx, idCol=table['id'].name(),
                                                           where='NOT isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\') AND OrgStructure_HospitalBed.sex=2 AND profile_id = %s'
                                                                 % (self.endDate, forceString(profileBed.value('id'))))

                    # Незанятых детских коек
                    freeBedsChildList = self.db.getIdList(tableEx, idCol=table['id'].name(),
                                                          where='NOT isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\') AND OrgStructure_HospitalBed.age=\'%s\' AND profile_id = %s'
                                                                % (self.endDate, u'0г-17г',
                                                                   forceString(profileBed.value('id'))))

                    msg.addSection(u'hos:InputRow')
                    msg.addField(
                        u'<hos:ReportDate>%s</hos:ReportDate>' % forceDate(QtCore.QDate.currentDate()).toString(
                            'yyyy-MM-dd'))
                    msg.addField(u'<hos:VacancyFromDate>%s</hos:VacancyFromDate>' % forceString(
                        date.today() - timedelta(days=1)))
                    msg.addField(
                        u'<hos:VacancyToDate>%s</hos:VacancyToDate>' % forceString(date.today() - timedelta(days=1)))
                    msg.addField(
                        u'<hos:HospitalInstitutionReestrNumber>%s</hos:HospitalInstitutionReestrNumber>' % config.userName)
                    msg.addField(
                        u'<hos:HospitalUnitCode xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>')
                    msg.addField(
                        u'<hos:HospitalDepartmentCode xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>')
                    msg.addField(
                        u'<hos:BedProfileCode>%s</hos:BedProfileCode>' % forceString(profileBed.value('regionalCode')))
                    msg.addField(u'<hos:PatientsStayed>%s</hos:PatientsStayed>' % forceString(len(freeBedsList)))
                    msg.addField(u'<hos:PatientsAdmitted>%s</hos:PatientsAdmitted>' % forceString(hospCount))
                    msg.addField(u'<hos:PatientsDischarged>%s</hos:PatientsDischarged>' % forceString(leavedCount))
                    msg.addField(u'<hos:HospitalizationsPlanned>0</hos:HospitalizationsPlanned>')
                    msg.addField(u'<hos:BedsVacantAll>%s</hos:BedsVacantAll>' % forceString(freeBeds))
                    msg.addField(u'<hos:BedsVacantMale>%s</hos:BedsVacantMale>' % forceString(len(freeBedsMaleList)))
                    msg.addField(
                        u'<hos:BedsVacantFemale>%s</hos:BedsVacantFemale>' % forceString(len(freeBedsFemaleList)))
                    msg.addField(u'<hos:BedsVacantChild>%s</hos:BedsVacantChild>' % forceString(len(freeBedsChildList)))
                    msg.addField(u'<hos:HospitalizationTimeEstimate>0</hos:HospitalizationTimeEstimate>')
                    msg.closeSection(u'hos:InputRow')
        msg.closeSection(u'hos:UploadRowsRequest')
        msg.closeSection(u'soapenv:Body')
        msg.closeSection(u'soapenv:Envelope')
        msg.sendMessage(self.url + '/sdat_vhos/owner_hospital_vacancy_upload')
        root = xml.etree.ElementTree.fromstring(msg.getResult())
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{http://www.rintech.ru/isomp/hospital_vacancy}UploadRowsResponse')
        root = root.find('{http://www.rintech.ru/isomp/hospital_vacancy}OutputRow')
        if root.find('{http://www.rintech.ru/isomp/hospital_vacancy}Id'):
            return True
        else:
            return False

    ########Simple logic#######
    def sendHospital(self):
        recEventsList = self.db.query(
            stmts.newPatientsForInterval % forceString(datetime.now() - timedelta(minutes=config.interval)))
        while recEventsList.next():
            if not Logger.checkAlreadyPackage(recEventsList.value(0), 'owner_hospital_admission_upload'):
                self.owner_hospital_discharge_upload(recEventsList.value(0))
        recEventsList = self.db.query(
            stmts.leavePatientsForInterval % forceString(datetime.now() - timedelta(minutes=config.interval)))
        while recEventsList.next():
            if not Logger.checkAlreadyPackage(recEventsList.value(0), 'owner_hospital_discharge_upload'):
                self.owner_hospital_discharge_upload(recEventsList.value(0))


class ShowError():
    def __init__(self):
        self.errors = u''

    def addError(self, message):
        self.errors += message + u'\n'

    def showError(self):
        QtGui.QMessageBox.information(None, u'Ошибка', u'Список ошибок:\n' + self.errors)

    def getErrors(self):
        return self.errors
