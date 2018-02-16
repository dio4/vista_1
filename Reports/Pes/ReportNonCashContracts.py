# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore

from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Ui_ReportNonCachContract import Ui_ReportNonCashDialog
from library.Utils import forceInt, forceString, forceDecimal


def selectData(begDate, endDate, orgStatus, isValid, contrAgent):
    db = QtGui.qApp.db
    tblPaymentScheme = db.table('PaymentScheme')
    cond = [tblPaymentScheme['begDate'].ge(begDate),
            tblPaymentScheme['begDate'].le(endDate),
            tblPaymentScheme['type'].eq(1)]
    if not orgStatus == None:
        cond.append(tblPaymentScheme['status'].eq(orgStatus))
    if isValid:
        cond.append(tblPaymentScheme['endDate'].ge(QtCore.QDate.currentDate()))
    if contrAgent:
        cond.append(tblPaymentScheme['org_id'].eq(contrAgent))


    return db.getRecordList(tblPaymentScheme, '*', cond, [tblPaymentScheme['status'], tblPaymentScheme['org_id']])

def selectFinanceData(begDate, endDate, orgStatus, isValid, contrAgent):
    db = QtGui.qApp.db
    stmt = u"""
    SELECT
     ps.number AS number,
     ps.org_id AS org_id,
     ps.begDate AS begDate,
     ps.endDate AS endDate,
     ps.total AS total,
     ps.spent AS spent,
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
     WHERE ps.begDate > \'%s\' AND ps.begDate < \'%s\' AND ps.deleted = 0 AND ps.type = 1
    """ % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'))
    if not orgStatus == None:
        stmt += u' AND ps.status = %s' % orgStatus
    if isValid:
        stmt += u' AND ps.endDate >=' % QtCore.QDate.currentDate().toString('yyyy-MM-dd')
    if contrAgent:
        stmt += u' AND ps.org_id = %s' % contrAgent
    return db.query(stmt)


class CReportNonCashContracts(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет: безналичные договоры')
        self.db = QtGui.qApp.db
        self.tblOrganisation = self.db.table('Organisation')


    def getSetupDialog(self, parent):
        result = CNonCashContracts(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        statusOrg = params.get('statusOrg')
        partner = params.get('partner')
        isValid = params.get('isValid')

        query = selectData(begDate, endDate, statusOrg, isValid, partner)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('10%',  [u'Контрагент'], CReportBase.AlignLeft),
                        ('10%', [u'Номер договора'],  CReportBase.AlignLeft),
                        ('10%', [u'Дата заключения'], CReportBase.AlignLeft),
                        ('10%', [u'Дата окончания'],  CReportBase.AlignLeft),
                        ('20%', [u'Предмет договора'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма остатка'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 1) #Контрагент
        table.mergeCells(0, 0, 1, 1) #Номер договора
        table.mergeCells(0, 0, 1, 1) #Дата заключения
        table.mergeCells(0, 0, 1, 1) #Дата окончания
        table.mergeCells(0, 0, 1, 1) #Предмет договора
        table.mergeCells(0, 0, 1, 1) #Сумма остатка
        for record in query:
            i = table.addRow()
            table.setText(i, 0, forceString(self.db.translate(self.tblOrganisation,
                                                              self.tblOrganisation['id'],
                                                              forceInt(record.value('org_id')),
                                                              self.tblOrganisation['shortName'])))
            table.setText(i, 1, forceString(record.value('number')))
            table.setText(i, 2, forceString(record.value('begDate')))
            table.setText(i, 3, forceString(record.value('endDate')))
            table.setText(i, 4, forceString(record.value('subjectContract')))
            table.setText(i, 5, forceDecimal(forceDecimal(record.value('total')) - forceDecimal(record.value('spent'))))
        return doc

class CReportNonCashFinance(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет: финансы (безналичные договоры)')
        self.db = QtGui.qApp.db
        self.tblOrganisation = self.db.table('Organisation')


    def getSetupDialog(self, parent):
        result = CNonCashContracts(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        statusOrg = params.get('statusOrg')
        partner = params.get('partner')
        isValid = params.get('isValid')

        query = selectFinanceData(begDate, endDate, statusOrg, isValid, partner)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('10%',  [u'Контрагент'], CReportBase.AlignLeft),
                        ('10%', [u'Номер договора'],  CReportBase.AlignLeft),
                        ('10%', [u'Дата заключения'], CReportBase.AlignLeft),
                        ('10%', [u'Дата окончания'],  CReportBase.AlignLeft),
                        ('10%', [u'Сумма остатка'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма выписанных услуг'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма выставленных счетов'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма не выставленных счетов'], CReportBase.AlignLeft),
                        ('10%', [u'Сумма не оплаченных счетов'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 1)  # Контрагент
        table.mergeCells(0, 0, 1, 1)  # Номер договора
        table.mergeCells(0, 0, 1, 1)  # Дата заключения
        table.mergeCells(0, 0, 1, 1)  # Дата окончания
        table.mergeCells(0, 0, 1, 1)  # Сумма остатка
        table.mergeCells(0, 0, 1, 1)  # Сумма выписанных услуг
        table.mergeCells(0, 0, 1, 1)  # Сумма выставленных счетов
        table.mergeCells(0, 0, 1, 1)  # Сумма не выставленных счетов
        table.mergeCells(0, 0, 1, 1)  # Сумма не оплаченных счетов
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceString(self.db.translate(self.tblOrganisation,
                                                              self.tblOrganisation['id'],
                                                              forceInt(record.value('org_id')),
                                                              self.tblOrganisation['shortName'])))
            table.setText(i, 1, forceString(record.value('number')))
            table.setText(i, 2, forceString(record.value('begDate')))
            table.setText(i, 3, forceString(record.value('endDate')))
            table.setText(i, 4, forceDecimal(forceDecimal(record.value('total')) - forceDecimal(record.value('spent'))))
            table.setText(i, 5, forceDecimal(record.value('sumUsl')))
            table.setText(i, 6, forceDecimal(record.value('sumAcc')))
            table.setText(i, 7, forceDecimal(record.value('sumNotAcc')))
            table.setText(i, 8, forceDecimal(record.value('sumNotPayed')))
        return doc

class CNonCashContracts(QtGui.QDialog, Ui_ReportNonCashDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.statusesDict = {0: None, 1: 0, 2: 1, 3: 3, 4: 4}

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))


    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['statusOrg']   = self.statusesDict[self.cmbOrgStatus.currentIndex()]
        params['partner']     = self.cmbPartner.value()
        params['isValid']     = self.chkIsValid.isChecked()
        return params