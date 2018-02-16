# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore

from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Ui_ReportClinicalIssues import Ui_Dialog
from library.Utils import forceInt, forceString, forceDecimal, forceDate


def selectData(begDate, endDate, partner, isValid, orgStruct, researcher, isEnrollment):
    db = QtGui.qApp.db
    tblPaymentScheme = db.table('PaymentScheme')
    cond = [tblPaymentScheme['begDate'].ge(begDate),
            tblPaymentScheme['begDate'].le(endDate),
            tblPaymentScheme['type'].eq(0)]
    if orgStruct:
        cond.append(tblPaymentScheme['orgStructure_id'].eq(orgStruct))
    if researcher:
        cond.append(tblPaymentScheme['person_id'].eq(researcher))
    if isValid:
        cond.append(tblPaymentScheme['endDate'].le(QtCore.QDate.currentDate()))
    if partner:
        cond.append(tblPaymentScheme['org_id'].eq(partner))
    if isEnrollment:
        cond.append(tblPaymentScheme['enrollment'].eq(0))

    return db.getRecordList(tblPaymentScheme, '*', cond, [tblPaymentScheme['orgStructure_id'], tblPaymentScheme['person_id']])

def selectFinanceData(begDate, endDate, partner, isValid, orgStruct, researcher, isEnrollment):
    db = QtGui.qApp.db
    stmt = u"""
         SELECT
         ps.number AS number,
         ps.person_id AS person_id,
         ps.orgStructure_id AS orgStructure_id,
         ps.org_id AS org_id,
         ps.numberProtocol AS numberProtocol,
         ps.begDate AS begDate,
         ps.endDate AS endDate,
         SUM(ct.price) AS sumUsl,
         IF (a.account = 1, SUM(ct.price), 0) AS sumAcc,
         IF (a.account = 0, SUM(ct.price), 0) AS sumNotAcc,
         IF (a.payStatus = 0 OR a.payStatus = 3, SUM(ct.price), 0) AS sumNotPayed
         FROM
         PaymentScheme ps
         INNER JOIN PaymentSchemeItem psi ON psi.paymentScheme_id = ps.id
         INNER JOIN Contract c ON psi.contract_id = c.id AND c.deleted = 0
         INNER JOIN Event e ON e.contract_id = c.id AND e.deleted = 0
         INNER JOIN Action a ON a.event_id = e.id AND a.deleted = 0
         INNER JOIN ActionType at ON at.id = a.actionType_id AND at.deleted = 0
         INNER JOIN ActionType_Service ats ON ats.master_id = at.id
         INNER JOIN rbService s ON ats.service_id = s.id
         INNER JOIN Contract_Tariff ct ON c.id = ct.master_id AND ct.service_id = s.id AND ct.deleted = 0
         WHERE ps.begDate > \'%s\' AND ps.begDate < \'%s\' AND ps.deleted = 0 AND ps.type = 0
        """ % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'))
    if isValid:
        stmt += u' AND ps.endDate >=' % QtCore.QDate.currentDate().toString('yyyy-MM-dd')
    if partner:
        stmt += u' AND ps.org_id = %s' % partner
    if orgStruct:
        stmt += u' AND ps.orgStructure_id = %s' % orgStruct
    if researcher:
        stmt += u' AND ps.person_id = %s' % researcher
    if isEnrollment:
        stmt += u' AND ps.enrollment = 0'
    return db.query(stmt)

class CReportClinicalIssues(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет: клинические исследования')
        self.db = QtGui.qApp.db
        self.tblOrganisation = self.db.table('Organisation')
        self.tblOrgStruct = self.db.table('OrgStructure')
        self.tblPrson = self.db.table('Person')


    def getSetupDialog(self, parent):
        result = CClinicalIssues(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        partner = params.get('partner')
        isValid = params.get('isValid')
        orgStruct = params.get('orgStruct')
        researcher = params.get('researcher')
        isEnrollment = params.get('enrollment')


        query = selectData(begDate, endDate, partner, isValid, orgStruct, researcher, isEnrollment)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('10%',  [u'Подразделение'], CReportBase.AlignLeft),
                        ('10%', [u'Главный исследователь'],  CReportBase.AlignLeft),
                        ('10%', [u'Номер договора'], CReportBase.AlignLeft),
                        ('10%', [u'Дата заключения'],  CReportBase.AlignLeft),
                        ('10%', [u'Дата окончания'], CReportBase.AlignLeft),
                        ('20%', [u'Контрагент'], CReportBase.AlignLeft),
                        ('10%', [u'Номер протокола'], CReportBase.AlignLeft),
                        ('20%', [u'Название протокола'], CReportBase.AlignLeft),
                        ('10%', [u'Действующий'], CReportBase.AlignLeft),
                        ('10%', [u'Набор пациентов'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 1) #Подразделение
        table.mergeCells(0, 0, 1, 1) #Главный исследователь
        table.mergeCells(0, 0, 1, 1) #Номер договора
        table.mergeCells(0, 0, 1, 1) #Дата заключения
        table.mergeCells(0, 0, 1, 1) #Дата окончания
        table.mergeCells(0, 0, 1, 1) #Контрагент
        table.mergeCells(0, 0, 1, 1) #Номер протокола
        table.mergeCells(0, 0, 1, 1) #Название протокола
        table.mergeCells(0, 0, 1, 1) #Действующий
        table.mergeCells(0, 0, 1, 1) #Набор пациентов
        for record in query:
            i = table.addRow()
            recPerson = self.db.getRecordEx(self.tblPrson, '*', self.tblPrson['id'].eq(forceInt(record.value('person_id'))))
            table.setText(i, 0, forceString(self.db.translate(self.tblOrgStruct,
                                                              self.tblOrgStruct['id'],
                                                              forceInt(record.value('orgStructure_id')),
                                                              self.tblOrgStruct['name'])))
            table.setText(i, 1, forceString(forceString(recPerson.value('lastName')) + u' ' + forceString(recPerson.value('firstName')) + u' ' + forceString(recPerson.value('patrName'))))
            table.setText(i, 2, forceString(record.value('number')))
            table.setText(i, 3, forceString(record.value('begDate')))
            table.setText(i, 4, forceString(record.value('endDate')))
            table.setText(i, 5, forceString(self.db.translate(self.tblOrganisation,
                                                              self.tblOrganisation['id'],
                                                              forceInt(record.value('org_id')),
                                                              self.tblOrganisation['shortName'])))
            table.setText(i, 6, forceString(record.value('numberProtocol')))
            table.setText(i, 7, forceString(record.value('nameProtocol')))
            table.setText(i, 8, u'Действующий' if forceDate(record.value('endDate')) > QtCore.QDate.currentDate() else u'Недействующий')
            table.setText(i, 9, u'Идет' if not forceInt(record.value('enrollment')) else u'не идет')
        return doc


class CReportClinicalFinance(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет: финансы (клинические исследования)')
        self.db = QtGui.qApp.db
        self.tblOrganisation = self.db.table('Organisation')
        self.tblOrgStruct = self.db.table('OrgStructure')
        self.tblPrson = self.db.table('Person')


    def getSetupDialog(self, parent):
        result = CClinicalIssues(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        partner = params.get('partner')
        isValid = params.get('isValid')
        orgStruct = params.get('orgStruct')
        researcher = params.get('researcher')
        isEnrollment = params.get('enrollment')


        query = selectFinanceData(begDate, endDate, partner, isValid, orgStruct, researcher, isEnrollment)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('10%',  [u'Подразделение'], CReportBase.AlignLeft),
                        ('10%', [u'Главный исследователь'],  CReportBase.AlignLeft),
                        ('20%', [u'Контрагент'], CReportBase.AlignLeft),
                        ('10%', [u'Номер договора'], CReportBase.AlignLeft),
                        ('10%', [u'Номер протокола'], CReportBase.AlignLeft),
                        ('10%', [u'Действующий'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма выписанных услуг'],  CReportBase.AlignLeft),
                        ('10%', [u'Сумма выставленных счетов'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма не выставленных счетов'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма не оплаченных счетов'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 1)  # Подразделение
        table.mergeCells(0, 0, 1, 1)  # Главный исследователь
        table.mergeCells(0, 0, 1, 1)  # Контрагент
        table.mergeCells(0, 0, 1, 1)  # Номер договора
        table.mergeCells(0, 0, 1, 1)  # Номер протокола
        table.mergeCells(0, 0, 1, 1)  # Действующий
        table.mergeCells(0, 0, 1, 1)  # Сумма выписанных услуг
        table.mergeCells(0, 0, 1, 1)  # Сумма выставленных счетов
        table.mergeCells(0, 0, 1, 1)  # Сумма не выставленных счетов
        table.mergeCells(0, 0, 1, 1)  # Сумма не оплаченных счетов
        while query.next():
            record = query.record()
            i = table.addRow()
            recPerson = self.db.getRecordEx(self.tblPrson, '*', self.tblPrson['id'].eq(forceInt(record.value('person_id'))))
            table.setText(i, 0, forceString(self.db.translate(self.tblOrgStruct,
                                                              self.tblOrgStruct['id'],
                                                              forceInt(record.value('orgStructure_id')),
                                                              self.tblOrgStruct['name'])))
            table.setText(i, 1, forceString(forceString(recPerson.value('lastName')) + u' ' + forceString(recPerson.value('firstName')) + u' ' + forceString(recPerson.value('patrName'))))
            table.setText(i, 2, forceString(self.db.translate(self.tblOrganisation,
                                                              self.tblOrganisation['id'],
                                                              forceInt(record.value('org_id')),
                                                              self.tblOrganisation['shortName'])))
            table.setText(i, 3, forceString(record.value('number')))
            table.setText(i, 4, forceString(record.value('numberProtocol')))
            table.setText(i, 5, u'Действующий' if forceDate(record.value('endDate')) > QtCore.QDate.currentDate() else u'Недействующий')
            table.setText(i, 6, forceDecimal(record.value('sumUsl')))
            table.setText(i, 7, forceDecimal(record.value('sumAcc')))
            table.setText(i, 8, forceDecimal(record.value('sumNotAcc')))
            table.setText(i, 9, forceDecimal(record.value('sumNotPayed')))
        return doc

class CClinicalIssues(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbResearcher.setIsInvestigator(1)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))


    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['orgStruct']   = self.cmbOrgStruct.value()
        params['partner']     = self.cmbPartner.value()
        params['isValid']     = self.chkIsValid.isChecked()
        params['researcher']  = self.cmbResearcher.value()
        params['enrollment']  = self.chkIsEnrollment.isChecked()
        return params