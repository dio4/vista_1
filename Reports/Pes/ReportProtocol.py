# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore

from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Ui_ReportProtocol import Ui_Dialog
from library.Utils import forceInt, forceString, forceDecimal, forceDate


def selectEventsList(begDate, endDate, protocolNumber, isValid, clientId = None):
    db = QtGui.qApp.db
    stmt = u"""
         SELECT
         cl.id AS clientId,
         cl.lastName,
         cl.firstName,
         cl.patrName,
         e.id AS EventId,
         ps.begDate AS begDate,
         ps.endDate AS endDate,
         psi.id AS protocolId,
         psi.name AS protocolName,
         s.name AS serviceName,
         ct.price AS price,
         ct.amount AS amount,
         SUM(ct.price) AS sumUsl,
         IF (a.account = 1, SUM(ct.price), 0) AS sumAcc,
         IF (a.account = 0, SUM(ct.price), 0) AS sumNotAcc,
         IF (a.payStatus = 3, SUM(ct.price), 0) AS sumPayed
         FROM
         PaymentScheme ps
         INNER JOIN PaymentSchemeItem psi ON psi.paymentScheme_id = ps.id
         INNER JOIN Contract c ON psi.contract_id = c.id AND c.deleted = 0
         INNER JOIN Event e ON e.contract_id = c.id AND e.deleted = 0
         INNER JOIN Client cl ON e.client_id = cl.id
         INNER JOIN Action a ON a.event_id = e.id AND a.deleted = 0
         INNER JOIN ActionType at ON at.id = a.actionType_id AND at.deleted = 0
         INNER JOIN ActionType_Service ats ON ats.master_id = at.id
         INNER JOIN rbService s ON ats.service_id = s.id
         INNER JOIN Contract_Tariff ct ON c.id = ct.master_id AND ct.service_id = s.id AND ct.deleted = 0
         WHERE ps.begDate > \'%s\' AND ps.begDate < \'%s\' AND ps.deleted = 0 AND ps.numberProtocol = \'%s\'
        """ % (begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), protocolNumber)
    if isValid:
        stmt += u' AND ps.endDate >= \'%s\'' % QtCore.QDate.currentDate().toString('yyyy-MM-dd')
    if clientId:
        stmt += u' AND cl.id = %s' % forceString(clientId)
    return db.query(stmt)

class CReportProtocol(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет: конкретный протокол')
        self.db = QtGui.qApp.db
        self.tblOrganisation = self.db.table('Organisation')
        self.tblOrgStruct = self.db.table('OrgStructure')
        self.tblPrson = self.db.table('Person')
        self.clintIdList = []


    def getSetupDialog(self, parent):
        result = CProtocol(parent)
        result.setTitle(self.title())
        return result

    def getServices(self, record):
        tblContractTariff = self.db.table('Contract_Tariff')
        recServices = self.db.getRecordList(tblContractTariff, '*', tblContractTariff['master_id'].eq(forceInt(record.value('contractId'))))

    def checkOnClose(self, record):
        if forceDate(record.value('endDate')) < QtCore.QDate.currentDate():
            return u'Закрыт/'
        else:
            return u''

    def getClientList(self, record, params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        isValid = params.get('isValid')
        protocolNum = params.get('protocolNum')
        resultString = u''
        totalCount = forceDecimal(0)
        if not forceInt(record.value('clientId')) in self.clintIdList:
            query = selectEventsList(begDate, endDate, protocolNum, isValid, forceInt(record.value('clientId')))
            while query.next():
                rec = query.record()
                totalCount += (forceDecimal(rec.value('price')) * forceDecimal(rec.value('amount')))
                resultString += forceString(rec.value('serviceName')) + u': ' + forceString(rec.value('price')) + u' * ' + forceString(rec.value('amount')) + u'\n'
            if resultString:
                resultString += u'Итого: ' + forceString(totalCount)
            self.clintIdList.append(forceInt(record.value('clientId')))
            return resultString

    def getVisitDone(self, record, params, columnName):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        isValid = params.get('isValid')
        protocolNum = params.get('protocolNum')
        resultString = u''
        query = selectEventsList(begDate, endDate, protocolNum, isValid, forceInt(record.value('clientId')))
        while query.next():
            rec = query.record()
            if forceString(rec.value('protocolName')) == forceString(columnName):
                resultString += forceString(rec.value('sumPayed')) + u'/ ' + forceString(rec.value('sumAcc'))
        self.clintIdList.append(forceInt(record.value('clientId')))
        return resultString

    def getVisitsList(self, schemeId):
        tblScheme = self.db.table('PaymentSchemeItem')
        recList = self.db.getRecordList(tblScheme, tblScheme['name'], tblScheme['paymentScheme_id'].eq(schemeId))
        visitsNameList = []
        for v in recList:
            visitsNameList.append(forceString(v.value('name')))
        return visitsNameList


    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        isValid = params.get('isValid')
        group = params.get('group')
        protocolNum = params.get('protocolNum')

        if forceInt(group):
            query = selectEventsList(begDate, endDate, protocolNum, isValid)
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(self.title())
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.insertBlock()
            names = self.getVisitsList(forceInt(self.db.translate('PaymentScheme', 'numberProtocol', protocolNum, 'id')))
            tableColumns = [('20%',  [u'Пациент'], CReportBase.AlignLeft)]
            for v in names:
                tableColumns.append(('10%', forceString(v), CReportBase.AlignLeft))

            table = createTable(cursor, tableColumns)
            while query.next():
                columnsCount = len(names)
                record = query.record()
                i = table.addRow()
                table.setText(i, 0, forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')))
                for count in xrange(columnsCount):
                    table.setText(i, count + 1, self.getVisitDone(record, params, names[count]))
            return doc
        else:
            query = selectEventsList(begDate, endDate, protocolNum, isValid)
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(self.title())
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.insertBlock()
            tableColumns = [('20%',  [u'Пациент'], CReportBase.AlignLeft),
                            ('10%', [u'Номер визита'],  CReportBase.AlignLeft),
                            ('60%', [u'Сумма оказанных услуг'], CReportBase.AlignLeft),
                            ('10%', [u'Статус визита'],  CReportBase.AlignLeft)]
            table = createTable(cursor, tableColumns)
            while query.next():
                record = query.record()
                i = table.addRow()
                table.setText(i, 0, forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')))
                table.setText(i, 1, forceString(record.value('protocolName')))
                table.setText(i, 2, forceString(self.getClientList(record, params)))
                table.setText(i, 3, forceString(self.checkOnClose(record)) + u'оплачен' if forceDecimal(record.value('sumUsl')) == forceDecimal(record.value('sumPayed')) else self.checkOnClose(record) + u'не оплачен')
            return doc

class CProtocol(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        db = QtGui.qApp.db
        tblScheme = db.table('PaymentScheme')
        recList = db.getRecordList(tblScheme, tblScheme['numberProtocol'], tblScheme['deleted'].eq(0))
        if recList:
            self.cmbProtocolNumber.addItems([forceString(v.value('numberProtocol')) for v in recList])

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))


    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['isValid']   = self.chkOnlyClose.isChecked()
        params['group']       = self.chkGroupByClients.isChecked()
        params['protocolNum'] = self.cmbProtocolNumber.currentText()
        return params