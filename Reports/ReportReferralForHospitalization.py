# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils       import forceDate, forceInt, forceString, forceDateTime
from Orgs.Utils          import getOrgStructureDescendants
from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase
from Exchange.ExportReferralForHospitalization import selectSendPlanOrdersClinic, selectSendFactOrdersHospital, selectSendOrdersHospitalUrgently, selectSendOrdersLeave

def getPersonInfo(record):
    personInfo = ''
    if forceInt(record.value('policyKindCode')) == 1:
        personInfo += u'Тип документа: Полис ОМС старого образца, код ' + forceString(record.value('policyKindCode')) + ' ; '
    elif forceInt(record.value('policyKindCode')) == 2:
        personInfo += u'Тип документа: Временное свидетельство, код ' + forceString(record.value('policyKindCode')) + ' ; '
    elif forceInt(record.value('policyKindCode')) == 3:
        personInfo += u'Тип документа: Полис ОМС единого образца, код ' + forceString(record.value('policyKindCode')) + ' ; '
    else:
        personInfo += u'Тип документа: - , код ' + forceString(record.value('policyKindCode')) + ' ; '
    if forceString(record.value('policySerial')):
        personInfo += u'серия полиса: ' + forceString(record.value('policySerial')) + '; '
    if forceString(record.value('policyNumber')):
        personInfo += u'номер полиса: ' + forceString(record.value('policyNumber')) + '; '
    if forceString(record.value('orgInsInfisCode')):
        personInfo += u'код СМО: ' + forceString(record.value('orgInsInfisCode')) + '; '
    if forceString(record.value('orgInsArea')):
        personInfo += u'код территории страхования: ' + forceString(record.value('orgInsArea')) + '; '
    if forceString(record.value('lastName')) or forceString(record.value('firstName')) or forceString(record.value('patrName')):
        personInfo += u'ФИО пациента: ' + forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName')) + '; '
    if forceInt(record.value('sex')) == 0:
        personInfo += u'пол: не определено; '
    elif forceInt(record.value('sex')) == 1:
        personInfo += u'пол: М; '
    else:
        personInfo += u'пол: Ж; '
    if forceDate(record.value('birthDate')):
        personInfo += u'дата рождения: ' + forceDate(record.value('birthDate')).toString('yyyy-MM-dd') + 'T00:00:00; '
    if forceString(record.value('contactName')) or forceString(record.value('contact')):
        personInfo += u'контактная информация: ' + forceString(record.value('contactName')) + ' ' + forceString(record.value('contact')) + '; '
    if forceString(record.value('documentSerial')):
        personInfo += u'серия документа, удостоверяющего личность: ' + forceString(record.value('documentSerial')) + '; '
    if forceString(record.value('documentNumber')):
        personInfo += u'номер документа, удостоверяющего личность: ' + forceString(record.value('documentNumber')) + '; '
    if forceString(record.value('documentType')):
        personInfo += u'тип документа, удостоверяющего личность: ' + forceString(record.value('documentType')) + '. '
    return personInfo

class CReportSendPlanOrdersClinic(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Детализированный список сведений о направлениях на госпитализацию')

    def getSetupDialog(self, parent):
        result = CReportReferralForHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        begDate = forceDate(params.get('begDate'))
        orgStructId = params.get('orgStructId')

        tableColumns = [
            ( '3%', [u'№'], CReportBase.AlignCenter),
            ( '8%', [u'Номер направления'], CReportBase.AlignCenter),
            ( '5%', [u'Дата направления'], CReportBase.AlignCenter),
            ( '8%', [u'Форма оказания медицинской помощи (1 – плановая, 2 – неотложная, 3 - экстренная)'], CReportBase.AlignCenter),
            ( '8%', [u'Код МО, направившей на госпитализацию'], CReportBase.AlignCenter),
            ( '8%', [u'Код МО, куда направлен пациент'], CReportBase.AlignCenter),
            ( '20%', [u'Персональные данные пациента'], CReportBase.AlignCenter),
            ( '8%', [u'Код диагноза МКБ'], CReportBase.AlignCenter),
            ( '8%', [u'Код профиля койки'], CReportBase.AlignCenter),
            ( '8%', [u'Код отделения'], CReportBase.AlignCenter),
            ( '8%', [u'Код медицинского работника'], CReportBase.AlignCenter),
            ( '8%', [u'Плановая дата госпитализации'], CReportBase.AlignCenter)
        ]

        table = createTable(cursor, tableColumns)

        query = selectSendPlanOrdersClinic(getOrgStructureDescendants(orgStructId), begDate)
        number = 1
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, number)
            table.setText(i, 1, forceString(record.value('referralNumber')))
            if forceDate(record.value('referralDate')):
                table.setText(i, 2, forceDate(record.value('referralDate')).toString('yyyy-MM-dd') + 'T00:00:00')
            if forceInt(record.value('formMedicalCare')) == 1:
                formMedicalCare = '1'
            elif forceInt(record.value('formMedicalCare')) == 6:
                formMedicalCare = '2'
            elif forceInt(record.value('formMedicalCare')) == 2:
                formMedicalCare = '3'
            else:
                formMedicalCare = ''
            table.setText(i, 3, formMedicalCare)
            table.setText(i, 4, forceString(record.value('orgSendInfisCode')))
            table.setText(i, 5, forceString(record.value('orgOutInfisCode')))
            table.setText(i, 6, getPersonInfo(record))
            table.setText(i, 7, forceString(record.value('MKB')))
            table.setText(i, 8, forceString(record.value('hospitalBedCode')))
            table.setText(i, 9, forceString(record.value('orgStructureCode')))
            table.setText(i, 10, forceString(record.value('personCode')))
            table.setText(i, 11, '')
            number += 1

        return doc

class CReportSendFactOrdersHospital(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Детализированный список сведений о госпитализациях')

    def getSetupDialog(self, parent):
        result = CReportReferralForHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        begDate = forceDate(params.get('begDate'))
        orgStructId = params.get('orgStructId')

        tableColumns = [
            ( '3%', [u'№'], CReportBase.AlignCenter),
            ( '8%', [u'Номер направления'], CReportBase.AlignCenter),
            ( '5%', [u'Дата направления'], CReportBase.AlignCenter),
            ( '8%', [u'Форма оказания медицинской помощи (1 – плановая, 2 – неотложная, 3 - экстренная)'], CReportBase.AlignCenter),
            ( '8%', [u'Код МО, направившей на госпитализацию'], CReportBase.AlignCenter),
            ( '8%', [u'Код МО, куда направлен пациент'], CReportBase.AlignCenter),
            ( '8%', [u'Дата и время фактической госпитализации'], CReportBase.AlignCenter),
            ( '20%', [u'Персональные данные пациента'], CReportBase.AlignCenter),
            ( '8%', [u'Код профиля койки'], CReportBase.AlignCenter),
            ( '8%', [u'Код отделения'], CReportBase.AlignCenter),
            ( '8%', [u'Номер карты стационарного больного'], CReportBase.AlignCenter),
            ( '8%', [u'Код МКБ приемного отделения'], CReportBase.AlignCenter)
        ]

        table = createTable(cursor, tableColumns)

        query = selectSendFactOrdersHospital(getOrgStructureDescendants(orgStructId), begDate)
        number = 1
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, number)
            table.setText(i, 1, forceString(record.value('referralNumber')))
            if forceDate(record.value('referralDate')):
                table.setText(i, 2, forceDate(record.value('referralDate')).toString('yyyy-MM-dd') + 'T00:00:00')
            if forceInt(record.value('formMedicalCare')) == 1:
                formMedicalCare = '1'
            elif forceInt(record.value('formMedicalCare')) == 6:
                formMedicalCare = '2'
            elif forceInt(record.value('formMedicalCare')) == 2:
                formMedicalCare = '3'
            else:
                formMedicalCare = ''
            table.setText(i, 3, formMedicalCare)
            table.setText(i, 4, forceString(record.value('orgSendInfisCode')))
            table.setText(i, 5, forceString(record.value('orgOutInfisCode')))
            table.setText(i, 6, forceDateTime(record.value('setDate')).toString('yyyy-MM-ddThh:mm:ss'))
            table.setText(i, 7, getPersonInfo(record))
            table.setText(i, 8, forceString(record.value('hospitalBedCode')))
            table.setText(i, 9, forceString(record.value('orgStructureCode')))
            table.setText(i, 10, forceString(record.value('externalId')))
            table.setText(i, 11, '')
            number += 1

        return doc

class CReportSendOrdersHospitalUrgently(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Детализированный список сведений об экстренных госпитализациях')

    def getSetupDialog(self, parent):
        result = CReportReferralForHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        begDate = forceDate(params.get('begDate'))
        orgStructId = params.get('orgStructId')

        tableColumns = [
            ( '4%', [u'№'], CReportBase.AlignCenter),
            ( '14%', [u'Код МО'], CReportBase.AlignCenter),
            ( '6%', [u'Дата и время фактической госпитализации'], CReportBase.AlignCenter),
            ( '20%', [u'Персональные данные пациента'], CReportBase.AlignCenter),
            ( '14%', [u'Код профиля койки'], CReportBase.AlignCenter),
            ( '14%', [u'Код отделения'], CReportBase.AlignCenter),
            ( '14%', [u'Номер карты стационарного больного'], CReportBase.AlignCenter),
            ( '14%', [u'Код МКБ приемного отделения'], CReportBase.AlignCenter)
        ]

        table = createTable(cursor, tableColumns)

        query = selectSendOrdersHospitalUrgently(getOrgStructureDescendants(orgStructId), begDate)
        number = 1
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, number)
            table.setText(i, 1, forceString(record.value('orgCurInfisCode')))
            table.setText(i, 2, forceDateTime(record.value('setDate')).toString('yyyy-MM-ddThh:mm:ss'))
            table.setText(i, 3, getPersonInfo(record))
            table.setText(i, 4, forceString(record.value('hospitalBedCode')))
            table.setText(i, 5, forceString(record.value('orgStructureCode')))
            table.setText(i, 6, forceString(record.value('externalId')))
            table.setText(i, 7, '')
            number += 1

        return doc

class CReportSendOrdersLeave(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Детализированный список сведений о выбывших пациентах')

    def getSetupDialog(self, parent):
        result = CReportReferralForHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        begDate = forceDate(params.get('begDate'))
        orgStructId = params.get('orgStructId')

        tableColumns = [
            ( '8%', [u'№'], CReportBase.AlignCenter),
            ( '8%', [u'Номер направления'], CReportBase.AlignCenter),
            ( '8%', [u'Дата направления'], CReportBase.AlignCenter),
            ( '8%', [u'Форма оказания медицинской помощи (1 – плановая, 2 – неотложная, 3 - экстренная)'], CReportBase.AlignCenter),
            ( '8%', [u'Код МО'], CReportBase.AlignCenter),
            ( '8%', [u'Дата госпитализации'], CReportBase.AlignCenter),
            ( '8%', [u'Дата выбытия'], CReportBase.AlignCenter),
            ( '20%', [u'Персональные данные пациента'], CReportBase.AlignCenter),
            ( '8%', [u'Код профиля койки'], CReportBase.AlignCenter),
            ( '8%', [u'Код отделения'], CReportBase.AlignCenter),
            ( '8%', [u'Номер карты стационарного больного'], CReportBase.AlignCenter)
        ]

        table = createTable(cursor, tableColumns)

        query = selectSendOrdersLeave(getOrgStructureDescendants(orgStructId), begDate)
        number = 1
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, number)
            table.setText(i, 1, forceString(record.value('referralNumber')))
            if forceDate(record.value('referralDate')):
                table.setText(i, 2, forceDate(record.value('referralDate')).toString('yyyy-MM-dd') + 'T00:00:00')
            if forceInt(record.value('formMedicalCare')) == 1:
                formMedicalCare = '1'
            elif forceInt(record.value('formMedicalCare')) == 6:
                formMedicalCare = '2'
            elif forceInt(record.value('formMedicalCare')) == 2:
                formMedicalCare = '3'
            else:
                formMedicalCare = ''
            table.setText(i, 3, formMedicalCare)
            table.setText(i, 4, forceString(record.value('orgCurInfisCode')))
            table.setText(i, 5, forceDateTime(record.value('setDate')).toString('yyyy-MM-ddThh:mm:ss'))
            table.setText(i, 6, forceDateTime(record.value('actLeavBegDate')).toString('yyyy-MM-ddThh:mm:ss'))
            table.setText(i, 7, getPersonInfo(record))
            table.setText(i, 8, forceString(record.value('hospitalBedCode')))
            table.setText(i, 9, forceString(record.value('orgStructureCode')))
            table.setText(i, 10, forceString(record.value('externalId')))
            number += 1

        return doc

from Ui_ReportReferralForHospitalizationSetup import Ui_ReportReferralForHospitalizationSetupDialog

class CReportReferralForHospitalizationSetupDialog(QtGui.QDialog, Ui_ReportReferralForHospitalizationSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['orgStructId'] = self.cmbOrgStructure.value()
        return result