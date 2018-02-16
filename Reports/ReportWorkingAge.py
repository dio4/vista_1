
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceBool, forceInt, forceString
from Orgs.Utils         import getOrgStructureDescendants

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportWorkingAge import Ui_ReportWorkingAge


def selectData(begDate, endDate, orgStructureId):

    db = QtGui.qApp.db

    tableClient            = db.table('Client')
    tableClientSocStatus   = db.table('ClientSocStatus')
    tableSocStatusType     = db.table('rbSocStatusType')
    tableClientAttach      = db.table('ClientAttach')
    tableOrgStructure      = db.table('OrgStructure')

    queryTable = tableClient.innerJoin(tableClientSocStatus, tableClientSocStatus['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableSocStatusType, tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id']))
    queryTable = queryTable.leftJoin(tableClientAttach, tableClientAttach['client_id'].eq(tableClient['id']))

    cols = [tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate'],
            'TIMESTAMPDIFF(YEAR,%s,now()) as age' % (tableClient['birthDate']),
            'if(TIMESTAMPDIFF(YEAR,%s,now()) >= 16 AND if(%s = 1, TIMESTAMPDIFF(YEAR,%s,now()) < 60, TIMESTAMPDIFF(YEAR,%s,now()) < 55), 1, 2) AS workingAge' % (tableClient['birthDate'], tableClient['sex'], tableClient['birthDate'], tableClient['birthDate']),
            tableSocStatusType['code'],
            'if(count(DISTINCT %s) = 1, 1, 0) as first' % tableClientSocStatus['socStatusType_id']]

    cond = [tableClientSocStatus['begDate'].dateLe(endDate),
            tableClientSocStatus['begDate'].dateGe(begDate),
            tableClient['deleted'].eq(0),
            tableClientSocStatus['deleted'].eq(0),
            '%s is not NULL' % tableClientAttach['orgStructure_id']]

    tmpCond = []
    for j in xrange(9):
        tmpCond.append(tableSocStatusType['code'].eq(u'Л_0' + forceString(j+1)))
    cond.append(db.joinOr(tmpCond))

    if orgStructureId:
        cond.append(tableClientAttach['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

    order = []

    group = tableClient['lastName'].name()

    order.append('workingAge')
    order.append(tableClient['lastName'].name())

    stmt = db.selectStmt(queryTable, cols, cond, group = group, order=order)
    query = db.query(stmt)
    print stmt
    return query

class CReportWorkingAge(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Первичные инвалиды, из них трудоспособного возраста')

    def getSetupDialog(self, parent):
        result = CWorkingAge(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate        = params.get('begDate', None)
        endDate        = params.get('endDate', None)
        orgStructureId = params.get('orgStructureId', None)
        age            = params.get('age', None)

        query = selectData(begDate, endDate, orgStructureId)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        self.dumpParams(cursor, params)
        tableColumns = [('%30',[u'ФИО'], CReportBase.AlignLeft),
                        ('%30',  [u'Дата рождения (Возраст)'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)

        total = [0]*2
        prevAge = ''
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            nameClient   = forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName'))
            birthDate    = forceString(record.value('birthDate'))
            ageClient    = forceString(record.value('age'))
            workAge      = forceInt(record.value('workingAge'))
            first        = forceBool(record.value('first'))
            if prevAge and prevAge != workAge:
                text = u'всего трудоспособного возраста'
                i = table.addRow()
                table.setText(i, 0, text, CReportBase.TableTotal)
                table.setText(i, 1, total[1])
                total[1] = 0
            if prevAge != workAge:
                if workAge == 1 and age != 2:
                    text = u'Трудоспособного возраста'
                else:
                    text = u'Нетрудоспособного возраста'
                i = table.addRow()
                table.setText(i, 0, text, CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, 2)
                prevAge = workAge
            if first:
                i = table.addRow()
                table.setText(i, 0, nameClient)
                table.setText(i, 1, birthDate + u' (' + ageClient + u')')
                for j in xrange(2):
                    total[j] += 1
        if age == 1:
            text =  u'всего трудоспособного возраста'
        else:
            text = u'всего нетрудоспособного возраста'
        i = table.addRow()
        table.setText(i, 0, text, CReportBase.TableTotal)
        table.setText(i, 1, total[1])
        i = table.addRow()
        table.setText(i, 0, u'ВСЕГО', CReportBase.TableTotal)
        table.setText(i, 1, total[0])
        return doc

class CWorkingAge(QtGui.QDialog, Ui_ReportWorkingAge):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbAge.setCurrentIndex(params.get('age', 0))

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['age']  = self.cmbAge.currentIndex()
        return params
