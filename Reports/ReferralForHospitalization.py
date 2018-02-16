# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceDate, forceInt, forceString
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReferralForHospitalizationSetup import Ui_ReferralForHospitalizationSetupDialog


def dumpParams(self, cursor):
    currentDate = QtCore.QDate.currentDate()
    cursor.insertText(u'Дата предоставления информации: ' + currentDate.toString('dd.MM.yyyy'))
    cursor.insertBlock()
    orgId = QtGui.qApp.currentOrgId()
    db = QtGui.qApp.db
    tableOrganisation = db.table('Organisation')
    stmt = db.selectStmt(tableOrganisation, tableOrganisation['fullName'], '`id` = %s' %orgId)
    query = QtGui.qApp.db.query(stmt)
    if query.first():
        record = query.record()
        cursor.insertText(u'Наименование медицинской организации: ' + forceString(record.value('fullName')))
        cursor.insertBlock()
    cursor.insertText(u'Реестровый номер медицинской организации: ' + forceString(orgId))


class CReferralForHospitalization(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setTitle(u'Cостав сведений о направлении на госпитализацию')

    def getSetupDialog(self, parent):
        result = CReferralForHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def selectData(self, begDate, endDate):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableDiagnostic = db.table('Diagnostic')
        tableDiagnosis = db.table('Diagnosis')
        tableClientPolicy = db.table('ClientPolicy')
        tableRbPolicyKind = db.table('rbPolicyKind')
        tableKLADRCodeReg = db.table('kladr.KLADR')
        tableOrganisation = db.table('Organisation')

        queryTable = tableEvent.innerJoin(tableAction, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.innerJoin(tableClientPolicy, tableClient['id'].eq(tableClientPolicy['client_id']))
        queryTable = queryTable.innerJoin(tableRbPolicyKind, tableClientPolicy['policyKind_id'].eq(tableRbPolicyKind['id']))
        queryTable = queryTable.leftJoin(tableOrganisation, tableClientPolicy['insurer_id'].eq(tableOrganisation['id']))
        queryTable = queryTable.leftJoin(tableKLADRCodeReg, tableKLADRCodeReg['CODE'].eq(tableOrganisation['area']))
        queryTable = queryTable.innerJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
        queryTable = queryTable.innerJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
        cols = [
            tableAction['id'].alias('ActionId'),
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['sex'],
            tableAction['begDate'],
            tableDiagnosis['MKB'],
            tableRbPolicyKind['code'].alias('policyKindCode'),
            tableClientPolicy['serial'],
            tableClientPolicy['number'],
            tableKLADRCodeReg['NAME'].alias('kladrName'),
            tableKLADRCodeReg['SOCR'].alias('kladrSocr'),
            tableKLADRCodeReg['CODE'].alias('kladrCode'),
            tableOrganisation['obsoleteInfisCode']
        ]
        stmt = db.selectStmt(queryTable, cols, u'''`ActionType`.`code` LIKE '1-3г'
            AND `ClientPolicy`.`endDate` IS NOT NULL
            AND DATE(`Action`.`begDate`) >= DATE('%s') AND DATE(`Action`.`begDate`) <= DATE('%s')''' % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))
        return stmt

    def selectPropertyDataString(self, actionId, actionPropertyName):
        db = QtGui.qApp.db
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyString = db.table('ActionProperty_String')
        tableActionPropertyType = db.table('ActionPropertyType')

        queryTable = tableActionProperty.innerJoin(tableActionPropertyString, tableActionProperty['id'].eq(tableActionPropertyString['id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionProperty['type_id'].eq(tableActionPropertyType['id']))
        stmt = db.selectStmt(queryTable, tableActionPropertyString['value'], '''ActionPropertyType.`name` LIKE '%s' AND ActionProperty.`action_id` = %s ''' % (actionPropertyName, actionId))
        return stmt

    def selectPropertyDataDate(self, actionId, actionPropertyName):
        db = QtGui.qApp.db
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyDate = db.table('ActionProperty_Date')
        tableActionPropertyType = db.table('ActionPropertyType')

        queryTable = tableActionProperty.innerJoin(tableActionPropertyDate, tableActionProperty['id'].eq(tableActionPropertyDate['id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionProperty['type_id'].eq(tableActionPropertyType['id']))
        stmt = db.selectStmt(queryTable, tableActionPropertyDate['value'], '''ActionPropertyType.`name` LIKE '%s' AND ActionProperty.`action_id` = %s ''' % (actionPropertyName, actionId))
        return stmt

    def selectPropertyDataOrganisation(self, actionId, actionPropertyName):
        db = QtGui.qApp.db
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyOrganisation = db.table('ActionProperty_Organisation')
        tableActionPropertyType = db.table('ActionPropertyType')
        tableOrganisation = db.table('Organisation')

        queryTable = tableActionProperty.innerJoin(tableActionPropertyOrganisation, tableActionProperty['id'].eq(tableActionPropertyOrganisation['id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionProperty['type_id'].eq(tableActionPropertyType['id']))
        queryTable = queryTable.innerJoin(tableOrganisation, tableOrganisation['id'].eq(tableActionPropertyOrganisation['value']))
        stmt = db.selectStmt(queryTable, tableOrganisation['obsoleteInfisCode'], '''ActionPropertyType.`name` LIKE '%s' AND ActionProperty.`action_id` = %s ''' % (actionPropertyName, actionId))
        return stmt

    def build(self, params):

        begDate = params.get('begDate')
        endDate = params.get('endDate')

        tableColumns = [
            ( '6%', u'Номер направления', CReportBase.AlignRight),
            ( '6%', u'Дата направления', CReportBase.AlignRight),
            ( '11%', u'Форма оказания медицинской помощи', CReportBase.AlignRight),
            ( '6%', u'Реестровый номер стационара', CReportBase.AlignRight),
            ( '6%', u'Тип документа, подтверждающего факт страхования по ОМС', CReportBase.AlignRight),
            ( '9%', u'Номер полиса ОМС', CReportBase.AlignRight),
            ( '6%', u'Реестровый номер СМО', CReportBase.AlignRight),
            ( '9%', u'Субъект РФ, в котором застрахован гражданин', CReportBase.AlignRight),
            ( '11%', u'Фамилия Имя Отчество', CReportBase.AlignRight),
            ( '6%', u'Пол', CReportBase.AlignRight),
            ( '6%', u'Код основного диагноза по МКБ 10', CReportBase.AlignRight),
            ( '6%', u'Код профиля коек отделения стационара', CReportBase.AlignRight),
            ( '6%', u'Код отделения стационара (профиль)', CReportBase.AlignRight),
            ( '6%', u'Плановая дата госпитализации', CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Состав сведений о направлении на госпитализацию:')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        dumpParams(self, cursor)
        cursor.insertBlock()
        cursor.insertBlock()

        table = createTable(cursor, tableColumns)
        query = QtGui.qApp.db.query(self.selectData(begDate, endDate))
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            i = table.addRow()
            actionId = forceInt(record.value('ActionId'))
            queryNumber = QtGui.qApp.db.query(self.selectPropertyDataString(actionId, u'Номер направления'))
            if queryNumber.first():
                recordNumber = queryNumber.record()
                table.setText(i, 0, forceString(recordNumber.value('value')))
            table.setText(i, 1, forceDate(record.value('begDate')).toString('dd.MM.yyyy'))
            queryForm = QtGui.qApp.db.query(self.selectPropertyDataString(actionId, u'Форма оказания медицинской помощи'))
            if queryForm.first():
                recordForm = queryForm.record()
                form = forceString(recordForm.value('value'))
                form = form[0:1]
                # form = form.replace('1 - ', '')
                # form = form.replace('2 - ', '')
                table.setText(i, 2, form)
            queryOrganisation = QtGui.qApp.db.query(self.selectPropertyDataOrganisation(actionId, u'Медицинская организация, куда направлен пациент'))
            if queryOrganisation.first():
                recordOrganisation = queryOrganisation.record()
                table.setText(i, 3, forceString(recordOrganisation.value('obsoleteInfisCode')))
            if record.value('policyKindCode'):
                kindCode = forceInt(record.value('policyKindCode'))
                kindName = ''
                if kindCode == 1:
                    kindName = u'С'
                elif kindCode == 2:
                    kindName = u'В'
                elif kindCode == 3:
                    kindName = u'П'
            table.setText(i, 4, kindName)
            table.setText(i, 5, u'серия полиса: ' + forceString(record.value('serial')) + u' номер полиса: ' + forceString(record.value('number')))
            table.setText(i, 6, forceString(record.value('obsoleteInfisCode')))
            if forceString(record.value('kladrCode')) == '7800000000000':
                table.setText(i, 7, u'40000')
            else:
                table.setText(i, 7, forceString(record.value('kladrName')) + ' ' + forceString(record.value('kladrSOCR')))
            fullName = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
            table.setText(i, 8, fullName)
            if forceInt(record.value('sex')) == 0:
                table.setText(i, 9, u'неопределено')
            elif forceInt(record.value('sex')) == 1:
                table.setText(i, 9, u'М')
            elif forceInt(record.value('sex')) == 2:
                table.setText(i, 9, u'Ж')
            table.setText(i, 10, forceString(record.value('MKB')))
            queryCode = QtGui.qApp.db.query(self.selectPropertyDataString(actionId, u'Код отделения (профиль)'))
            if queryCode.first():
                recordCode = queryCode.record()
                profile1 = forceString(recordCode.value('value')).split()
                table.setText(i, 11, profile1[0])
                profile2 = forceString(recordCode.value('value')).replace(profile1[0] + ' - ', '')
                table.setText(i, 12, profile2)
            queryDate = QtGui.qApp.db.query(self.selectPropertyDataDate(actionId, u'Плановая дата госпитализации'))
            if queryDate.first():
                recordDate = queryDate.record()
                table.setText(i, 13, forceString(recordDate.value('value')))
        return doc


class CRemoveReferralForHospitalization(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setTitle(u'Cостав сведений об аннулировании направления на госпитализацию')

    def getSetupDialog(self, parent):
        result = CReferralForHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def selectData(self, begDate, endDate):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')

        queryTable = tableEvent.innerJoin(tableAction, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
        cols = [
            tableAction['id'].alias('ActionId'),
            tableAction['begDate']
        ]
        stmt = db.selectStmt(queryTable, cols, u'''`ActionType`.`code` LIKE '1-4г'
            AND DATE(`Action`.`begDate`) >= DATE('%s') AND DATE(`Action`.`begDate`) <= DATE('%s') ''' % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')))
        return stmt

    def selectPropertyDataString(self, actionId, actionPropertyName):
        db = QtGui.qApp.db
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyString = db.table('ActionProperty_String')
        tableActionPropertyType = db.table('ActionPropertyType')

        queryTable = tableActionProperty.innerJoin(tableActionPropertyString, tableActionProperty['id'].eq(tableActionPropertyString['id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionProperty['type_id'].eq(tableActionPropertyType['id']))
        stmt = db.selectStmt(queryTable, tableActionPropertyString['value'], '''ActionPropertyType.`name` LIKE '%s' AND ActionProperty.`action_id` = %s ''' % (actionPropertyName, actionId))
        return stmt

    def selectPropertyDataDate(self, actionId, actionPropertyName):
        db = QtGui.qApp.db
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyDate = db.table('ActionProperty_Date')
        tableActionPropertyType = db.table('ActionPropertyType')

        queryTable = tableActionProperty.innerJoin(tableActionPropertyDate, tableActionProperty['id'].eq(tableActionPropertyDate['id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionProperty['type_id'].eq(tableActionPropertyType['id']))
        stmt = db.selectStmt(queryTable, tableActionPropertyDate['value'], '''ActionPropertyType.`name` LIKE '%s' AND ActionProperty.`action_id` = %s ''' % (actionPropertyName, actionId))
        return stmt

    def selectPropertyDataOrganisation(self, actionId, actionPropertyName):
        db = QtGui.qApp.db
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyOrganisation = db.table('ActionProperty_Organisation')
        tableActionPropertyType = db.table('ActionPropertyType')

        queryTable = tableActionProperty.innerJoin(tableActionPropertyOrganisation, tableActionProperty['id'].eq(tableActionPropertyOrganisation['id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType, tableActionProperty['type_id'].eq(tableActionPropertyType['id']))
        stmt = db.selectStmt(queryTable, tableActionPropertyOrganisation['value'], '''ActionPropertyType.`name` LIKE '%s' AND ActionProperty.`action_id` = %s ''' % (actionPropertyName, actionId))
        return stmt

    def build(self, params):

        begDate = params.get('begDate')
        endDate = params.get('endDate')

        tableColumns = [
            ( '20%', u'Номер направления', CReportBase.AlignRight),
            ( '20%', u'Дата направления', CReportBase.AlignRight),
            ( '20%', u'Источник аннулирования', CReportBase.AlignRight),
            ( '20%', u'Реестровый номер источника аннулирования', CReportBase.AlignRight),
            ( '20%', u'Причина аннулирования', CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Состав сведений об аннулировании направления на госпитализацию:')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        dumpParams(self, cursor)
        cursor.insertBlock()
        cursor.insertBlock()

        table = createTable(cursor, tableColumns)
        query = QtGui.qApp.db.query(self.selectData(begDate, endDate))
        while query.next():
            record = query.record()
            i = table.addRow()
            actionId = forceInt(record.value('ActionId'))
            queryNumber = QtGui.qApp.db.query(self.selectPropertyDataString(actionId, u'Номер направления'))
            if queryNumber.first():
                recordNumber = queryNumber.record()
                table.setText(i, 0, forceString(recordNumber.value('value')))
            queryDate = QtGui.qApp.db.query(self.selectPropertyDataDate(actionId, u'Дата направления'))
            if queryDate.first():
                recordDate = queryDate.record()
                table.setText(i, 1, forceString(recordDate.value('value')))
            querySource = QtGui.qApp.db.query(self.selectPropertyDataString(actionId, u'Источник аннулирования'))
            if querySource.first():
                recordSource = querySource.record()
                source = forceString(recordSource.value('value'))
                j = 1
                while j <= 3:
                    source = source.replace(forceString(j) + ' - ', '')
                    j += 1
                table.setText(i, 2, source)
            queryOrganisation = QtGui.qApp.db.query(self.selectPropertyDataOrganisation(actionId, u'Реестровый номер источника аннулирования'))
            if queryOrganisation.first():
                recordOrganisation = queryOrganisation.record()
                table.setText(i, 3, forceString(recordOrganisation.value('value')))
            queryReason = QtGui.qApp.db.query(self.selectPropertyDataString(actionId, u'Причина аннулирования'))
            if queryReason.first():
                recordReason = queryReason.record()
                reason = forceString(recordReason.value('value'))
                j = 1
                while j <= 5:
                    reason = reason.replace(forceString(j) + ' - ', '')
                    j += 1
                table.setText(i, 4, reason)
        return doc

class CReferralForHospitalizationSetupDialog(QtGui.QDialog, Ui_ReferralForHospitalizationSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        return result