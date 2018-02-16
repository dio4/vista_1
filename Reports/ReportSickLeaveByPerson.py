# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils       import forceDate, forceInt, forceString, forceDouble, forceBool
from Orgs.Utils          import getOrgStructureDescendants
from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase


def selectData(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    orgStructureId = forceInt(params.get('orgStructureId'))
    forming = forceInt(params.get('forming'))
    open = forceBool(params.get('open'))
    select = ''
    where = ''
    innerJoin = ''
    groupBy = ''
    if forming == 0:
        select += '''CONCAT(Person.lastName, Person.firstName, Person.patrName) AS name,'''
        groupBy += '''Person.lastName'''
        if orgStructureId:
            orgStructureIdList = forceString(getOrgStructureDescendants(orgStructureId))
            orgStructureIdList = orgStructureIdList.replace('[', '(')
            orgStructureIdList = orgStructureIdList.replace(']', ')')
            where += ''' AND Person.orgStructure_id IN %s''' % orgStructureIdList
    elif forming == 1:
        select += '''OrgStructure.name,
        OrgStructure.parent_id,'''
        innerJoin += '''INNER JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id AND OrgStructure.deleted = 0'''
        groupBy += '''OrgStructure.name'''
    if begDate:
        where += ''' AND DATE(TempInvalid.endDate) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += ''' AND DATE(TempInvalid.endDate) <= DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    if not open:
        where += ''' AND TempInvalid.closed = 1'''

    stmt = u'''
        SELECT %s
            COUNT(DISTINCT TempInvalid.id) AS countTempInvalid,
            SUM(TIMESTAMPDIFF(DAY, TempInvalid.begDate, TempInvalid.endDate)) AS sumDay
        FROM Person
        INNER JOIN TempInvalid ON TempInvalid.person_id = Person.id AND TempInvalid.deleted = 0
        %s
        WHERE Person.deleted = 0 %s
        GROUP BY %s
    ''' % (select, innerJoin, where, groupBy)
    return db.query(stmt)


def selectDataLPU(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    open = forceBool(params.get('open'))
    where = ''
    if begDate:
        where += ''' AND DATE(TempInvalid.endDate) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += ''' AND DATE(TempInvalid.endDate) <= DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    if not open:
        where += ''' AND TempInvalid.closed = 1'''

    stmt = u'''
        SELECT Organisation.fullName AS name,
            COUNT(DISTINCT TempInvalid.id) AS countTempInvalid,
            SUM(TIMESTAMPDIFF(DAY, TempInvalid.begDate, TempInvalid.endDate)) AS sumDay
        FROM Person
        INNER JOIN TempInvalid ON TempInvalid.person_id = Person.id AND TempInvalid.deleted = 0
        INNER JOIN Organisation ON Person.orgStructure_id IS NULL AND Organisation.id = Person.org_id AND Organisation.deleted = 0
        WHERE Person.deleted = 0 %s
        GROUP BY Organisation.fullName
    ''' % where
    return db.query(stmt)


def setOrgStructFullName(orgStructId):
    db = QtGui.qApp.db
    orgStructHight = orgStructId
    resultName = ''
    while orgStructId != '':
        stmt = u'''
            SELECT OrgStructure.name,
                OrgStructure.parent_id
            FROM OrgStructure
            WHERE OrgStructure.id = %s AND OrgStructure.deleted = 0
        ''' % orgStructId
        query = db.query(stmt)
        if query.first():
            record = query.record()
            resultName += ' / ' + forceString(record.value('name'))
            orgStructId = forceString(record.value('parent_id'))
        else:
            orgStructId = ''

    nameLPU = ''
    if orgStructHight != '':
        stmt = u'''
            SELECT Organisation.shortName AS name
            FROM OrgStructure
            INNER JOIN Organisation ON OrgStructure.organisation_id = Organisation.id AND Organisation.deleted = 0
            WHERE OrgStructure.id = %s AND OrgStructure.deleted = 0
        ''' % orgStructHight
        query = db.query(stmt)
        if query.first():
            record = query.record()
            nameLPU = ' / ' + forceString(record.value('name'))
    return resultName + nameLPU


class CReportSickLeaveByPerson(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)

    def getSetupDialog(self, parent):
        result = CReportSickLeaveByPersonSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        forming = forceInt(params.get('forming'))
        if forming == 0:
            formingName1 = u'Врач'
            formingName2 = u'врачам'
        if forming == 1:
            formingName1 = u'Отделение'
            formingName2 = u'отделениям'
        self.setTitle(u'Отчёт по больничным листам по %s' % formingName2)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ( '40%', [formingName1], CReportBase.AlignCenter),
            ( '20%', [u'Всего Б/л'], CReportBase.AlignCenter),
            ( '20%', [u'Всего дней'], CReportBase.AlignCenter),
            ( '20%', [u'Средняя продолжительность'], CReportBase.AlignCenter)
        ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        resultTempInvalid = 0
        resultSumDay = 0
        queryList = [selectDataLPU(params), selectData(params)] if forming == 1 else [selectData(params)]
        flagLPU = True
        for query in queryList:
            while query.next():
                record = query.record()
                i = table.addRow()
                name = forceString(record.value('name'))
                if forming == 1 and not flagLPU:
                    name += setOrgStructFullName(forceString(record.value('parent_id')) if forceString(record.value('parent_id')) != '' else '')
                countTempInvalid = forceInt(record.value('countTempInvalid'))
                resultTempInvalid += countTempInvalid
                sumDay = forceInt(record.value('sumDay')) + countTempInvalid
                resultSumDay += sumDay
                if countTempInvalid != 0:
                    averageDuration = round(forceDouble(sumDay) / forceDouble(countTempInvalid), 2)
                else:
                    averageDuration = 0
                table.setText(i, 0, name)
                table.setText(i, 1, countTempInvalid)
                table.setText(i, 2, sumDay)
                table.setText(i, 3, averageDuration)
            flagLPU = False
        i = table.addRow()
        if resultTempInvalid != 0:
            resultAverageDuration = round(forceDouble(resultSumDay) / forceDouble(resultTempInvalid), 2)
        else:
            resultAverageDuration = 0
        table.setText(i, 0, u'Итого:')
        table.setText(i, 1, resultTempInvalid)
        table.setText(i, 2, resultSumDay)
        table.setText(i, 3, resultAverageDuration)
        return doc

from Ui_ReportSickLeaveByPersonSetup import Ui_ReportSickLeaveByPersonSetupDialog

class CReportSickLeaveByPersonSetupDialog(QtGui.QDialog, Ui_ReportSickLeaveByPersonSetupDialog):
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
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['forming'] = self.cmbForming.currentIndex()
        result['open'] = self.chkOpen.checkState()
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbForming_currentIndexChanged(self, index):
        if index == 0:
            self.lblOrgStructure.setVisible(True)
            self.cmbOrgStructure.setVisible(True)
        elif index == 1:
            self.lblOrgStructure.setVisible(False)
            self.cmbOrgStructure.setVisible(False)