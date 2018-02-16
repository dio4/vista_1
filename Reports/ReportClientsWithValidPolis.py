# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceBool, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportClientsWithValidPolis import Ui_ReportClientsWithValidPolisDialog


def selectData(params):
    ageFrom = params.get('ageFrom')
    ageTo = params.get('ageTo')
    sex = params.get('sex')
    reportDate = params.get('reportDate')
    confirmDate = params.get('confirmEISDate')
    orgInsurerId = params.get('insurerId')
    attachmentOrgStructureId = params.get('attachmentOrgStructureId', None)
    isShowRegAddress = forceBool(params.get('isShowRegAddress', False))
    isShowLocAddress = forceBool(params.get('isShowLocAddress', False))

    db = QtGui.qApp.db

    tableClient = db.table('Client')
    tableClientPolicy = db.table('ClientPolicy')
    tableClientIdentification = db.table('ClientIdentification')
    tableEvent = db.table('Event')

    queryTable = tableClient.innerJoin(tableEvent, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableClientPolicy, tableClient['id'].eq(tableClientPolicy['client_id']))

    fields = [tableClient['lastName'].name(),
                tableClient['firstName'].name(),
                tableClient['patrName'].name(),
                tableClient['birthDate'].name(),
                tableClient['sex'].name(),
                tableClientPolicy['serial'].name(),
                tableClientPolicy['number'].name()]
    if isShowRegAddress:
        fields.append(u'getClientRegAddress(%s) AS regAddress' % tableClient['id'].name())
    if isShowLocAddress:
        fields.append(u'getClientLocAddress(%s) AS locAddress' % tableClient['id'].name())


    cond = []
    group = 'Client.id'
    if orgInsurerId:
        cond.append(tableClientPolicy['insurer_id'].eq(orgInsurerId))
        cond.append(tableClientPolicy['policyType_id'].inlist((1, 2)))
    if ageFrom <= ageTo:
        cond.append('age(Client.`birthDate`,CURRENT_DATE)>=%s'%ageFrom)
        cond.append('age(Client.`birthDate`,CURRENT_DATE)<=%s'%ageTo)

    if sex:
        cond.append(tableClient['sex'].eq(sex))

    if confirmDate and reportDate:
        queryTable = queryTable.innerJoin(tableClientIdentification, tableClient['id'].eq(tableClientIdentification['client_id']))
        cond.append(tableClientIdentification['checkDate'].ge(confirmDate))
        cond.append(tableClientIdentification['checkDate'].le(reportDate))
        cond.append(tableClientIdentification['accountingSystem_id'].inlist((1, 2)))

    if attachmentOrgStructureId:
        tableClientAttach = db.table('ClientAttach')
        tableClient       = db.table('Client')
        cond.append(tableEvent['deleted'].eq(0))
        cond.append(db.existsStmt(tableClientAttach, [tableClientAttach['orgStructure_id'].inlist(getOrgStructureDescendants(attachmentOrgStructureId)),
                                                      tableClientAttach['client_id'].eq(tableClient['id']),
                                                      tableClientAttach['begDate'].le(tableEvent['setDate']),
                                                      db.joinOr([tableClientAttach['endDate'].isNull(),
                                                                 tableClientAttach['endDate'].ge(tableEvent['setDate'])])
        ]))

    stmt = db.selectStmt(queryTable, fields, cond, group = group)
    return db.query(stmt)



class CReportClientsWithValidPolis(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по застрахованным лицам')

    def getSetupDialog(self, parent):
        result = CSetupReportClientsWithValidPolis(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        isShowRegAddress = forceBool(params.get('isShowRegAddress', False))
        isShowLocAddress = forceBool(params.get('isShowLocAddress', False))

        tableColumns = [
                          ('40%', [ u'Имя пациента', u''], CReportBase.AlignLeft ),
                          ('15%',  [ u'Дата рождения', u''], CReportBase.AlignLeft ),
                          ('15%', [ u'Пол', u''], CReportBase.AlignRight ),
                          ('15%', [ u'Полис' , u'Серия'], CReportBase.AlignRight ),
                          ('15%', [ u'' , u'Номер'], CReportBase.AlignRight )
                       ]
        
        regAddressColumn = -1
        locAddressColumn = -1
        if isShowRegAddress:
            regAddressColumn = len(tableColumns)
            tableColumns.append(('15%', [ u'Адрес регистрации' , u''], CReportBase.AlignRight))
            
        if isShowLocAddress:
            locAddressColumn = len(tableColumns)
            tableColumns.append(('15%', [ u'Адрес проживания' , u''], CReportBase.AlignRight))

        table = createTable(cursor, tableColumns)
        
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 2)
        
        if isShowRegAddress:
            table.mergeCells(0, regAddressColumn, 2, 1)
        if isShowLocAddress:
            table.mergeCells(0, locAddressColumn, 2, 1)

        cnt = 0
        while query.next():
            record = query.record()

            name = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
            birthDate = forceString(record.value('birthDate'))
            sex = forceString(record.value('sex'))
            if sex == 1:
                sex = u'м'
            else:
                sex = u'ж'
            serial = forceString(record.value('serial'))
            number = forceString(record.value('number'))


            i = table.addRow()
            table.setText(i, 0, name)
            table.setText(i, 1, birthDate)
            table.setText(i, 2, sex)
            table.setText(i, 3, serial)
            table.setText(i, 4, number)
            if isShowRegAddress:
                regAddress = forceString(record.value('regAddress'))
                table.setText(i, regAddressColumn, regAddress)
            if isShowLocAddress:
                locAddress = forceString(record.value('locAddress'))
                table.setText(i, locAddressColumn, locAddress)

            cnt += 1
        i = table.addRow()
        table.mergeCells(i, 0, 1, 5)
        table.setText(i, 0, u'Итого: %s' % cnt)
        return doc


class CSetupReportClientsWithValidPolis(QtGui.QDialog, Ui_ReportClientsWithValidPolisDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbInsurerDoctors.setAddNone(True)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtReportDate.setDate(params.get('reportDate', date))
        self.edtReportDate.setMaximumDate(date)
        self.edtConfirmDate.setDate(params.get('confirmEISDate', QtCore.QDate()))
        self.cmbInsurerDoctors.setValue(params.get('insurerId', None))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.cmbAttachmentOrgStructureId.setValue(params.get('attachmentOrgStructureId', None))
        self.chkShowRegAddress.setChecked(forceBool(params.get('isShowRegAddress', False)))
        self.chkShowLocAddress.setChecked(forceBool(params.get('isShowLocAddress', False)))


    def params(self):
        result = {}
        result['reportDate'] = self.edtReportDate.date()
        result['confirmEISDate'] = self.edtConfirmDate.date()
        result['insurerId'] = self.cmbInsurerDoctors.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['attachmentOrgStructureId'] = self.cmbAttachmentOrgStructureId.value()
        result['sex'] = self.cmbSex.currentIndex()
        result['isShowRegAddress'] = self.chkShowRegAddress.isChecked()
        result['isShowLocAddress'] = self.chkShowLocAddress.isChecked()
        return result

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtReportDate_dateChanged(self, date):
        if not date.isNull():
            self.edtConfirmDate.setEnabled(True)
            self.edtConfirmDate.setMinimumDate(date.addMonths(-1))
            self.edtConfirmDate.setMaximumDate(date)
        else:
            self.edtConfirmDate.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_cmbInsurerDoctors_currentIndexChanged(self, index):
        if index in (0, -1):
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
