# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.Ui_ReportDeathBSKSetup import Ui_ReportDeathBSKSetupDialog
from library.Utils import forceString, forceInt


def selectData(params):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    orgStructId     = params.get('orgStructId')

    tblEvent = db.table('Event')
    tblClient = db.table('Client')
    tblRbResult = db.table('rbResult')
    tblPerson = db.table('Person')
    tblMAction = db.table('Action').alias('MAction')
    tblMActionType = db.table('ActionType').alias('MActionType')
    tblMES = db.table('mes.MES').alias('MES')
    tblMES_mkb = db.table('mes.MES_mkb').alias('MES_mkb')

    fields = \
    [
        u'''IF(rbResult.`name` like '%умер%', 1, 0) AS isDeath''',
        tblMES_mkb['mkb'].alias('mkb'),
        '''CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS name''',
        tblEvent['externalId'].alias('id'),
    ]

    tblQuery = tblEvent.innerJoin(tblRbResult, tblEvent['result_id'].eq(tblRbResult['id']))
    tblQuery = tblQuery.innerJoin(tblClient, tblEvent['client_id'].eq(tblClient['id']))
    tblQuery = tblQuery.innerJoin(tblPerson, tblEvent['execPerson_id'].eq(tblPerson['id']))
    tblQuery = tblQuery.innerJoin(tblMAction, tblEvent['id'].eq(tblMAction['event_id']))
    tblQuery = tblQuery.innerJoin(tblMActionType, db.joinAnd([
        tblMAction['actionType_id'].eq(tblMActionType['id']),
        tblMActionType['flatCode'].eq('moving')
    ]))
    tblQuery = tblQuery.innerJoin(tblMES, tblMAction['MES_id'].eq(tblMES['id']))
    tblQuery = tblQuery.innerJoin(tblMES_mkb, tblMES['id'].eq(tblMES_mkb['master_id']))

    where = \
    [
        tblEvent['deleted'].eq(0),
        tblMAction['deleted'].eq(0),
        tblMES_mkb['mkb'].inlist(['I20.0', 'I21', 'I22', 'I23', 'I60', 'I61', 'I62', 'I63', 'I64'])
    ]
    if begDate and endDate:
        where.append(tblEvent['execDate'].between(begDate, endDate))
    if orgStructId:
        where.append(tblPerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructId)))

    stmt = db.selectStmt(tblQuery, fields=fields, where=where, isDistinct=True)
    return db.query(stmt)

class CReportDeathBSK(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Показатели заболеваемости и смертности от БСК')

    def getSetupDialog(self, parent):
        result = CDeathBSKDialog(parent)
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
        tableColumns = \
        [
            ('10%',     [u'Пациенты с ОНМК'],                                        CReportBase.AlignLeft),
            ('10%',     [u'Пациенты с острым инфарктом миокарда'],                   CReportBase.AlignLeft),
            ('10%',     [u'Пациенты с нестабильной стенокардией'],                   CReportBase.AlignLeft),
            ('10%',     [u'Пациенты, госпитализированные в профильные отделени'],    CReportBase.AlignLeft),
            ('10%',     [u'Пациенты, госпитализированные в непрофильные отделения'], CReportBase.AlignLeft),
            ('10%',     [u'Пациенты, оставленные на дому'],                          CReportBase.AlignLeft),
            ('10%',     [u'Умершие от инфаркта миокарда'],                                  CReportBase.AlignLeft),
            ('10%',     [u'Умершие от нестабильной стенокардии'],                           CReportBase.AlignLeft),
            ('10%',     [u'Умершие от ОНМК'],                                               CReportBase.AlignLeft),
            ('10%',     [u'Умершие от  БСК'],                                               CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        isHell = params['isHell']
        ONMK    = 0 #0
        OKS1    = 0 #1
        OKS2    = 0 #2
        sum     = 0 #3
        DOKS1   = 0 #4
        DOKS2   = 0 #5
        DONMK   = 0 #6
        Dsum    = 0 #7
        #TODO:skkachaev: Правда ли у нас table.addRow() всегда при первом вызове вернёт 1?
        row = 0
        while query.next():
            record = query.record()
            if forceInt(record.value('isDeath')) == 0:
                if forceString(record.value('mkb')) == 'I60' \
                    or forceString(record.value('mkb')) == 'I61' \
                    or forceString(record.value('mkb')) == 'I62' \
                    or forceString(record.value('mkb')) == 'I63' \
                    or forceString(record.value('mkb')) == 'I64':
                    ONMK += 1
                    if isHell:
                        if ONMK > row: row = table.addRow()
                        table.setText(ONMK, 0,
                                      forceString(record.value('id')) + '|' + forceString(record.value('name')))

                elif forceString(record.value('mkb')) == 'I21' \
                    or forceString(record.value('mkb')) == 'I22' \
                    or forceString(record.value('mkb')) == 'I23':
                    OKS1 += 1
                    if isHell:
                        if OKS1 > row: row = table.addRow()
                        table.setText(OKS1, 1,
                                      forceString(record.value('id')) + '|' + forceString(record.value('name')))
                elif forceString(record.value('mkb')) == 'I20.0':
                    OKS2 += 1
                    if isHell:
                        if OKS2 > row: row = table.addRow()
                        table.setText(OKS2, 2,
                                      forceString(record.value('id')) + '|' + forceString(record.value('name')))
                sum += 1
                if isHell:
                    if sum > row: row = table.addRow()
                    table.setText(sum, 3,
                                  forceString(record.value('id')) + '|' + forceString(record.value('name')))
            else:
                if forceString(record.value('mkb')) == 'I60' \
                    or forceString(record.value('mkb')) == 'I61' \
                    or forceString(record.value('mkb')) == 'I62' \
                    or forceString(record.value('mkb')) == 'I63' \
                    or forceString(record.value('mkb')) == 'I64':
                    DONMK += 1
                    if isHell:
                        if DONMK > row: row = table.addRow()
                        table.setText(DONMK, 6,
                                      forceString(record.value('id')) + '|' + forceString(record.value('name')))
                elif forceString(record.value('mkb')) == 'I21' \
                    or forceString(record.value('mkb')) == 'I22' \
                    or forceString(record.value('mkb')) == 'I23':
                    DOKS1 += 1
                    if isHell:
                        if DOKS1 > row: row = table.addRow()
                        table.setText(DOKS1, 7,
                                      forceString(record.value('id')) + '|' + forceString(record.value('name')))
                elif forceString(record.value('mkb')) == 'I20.0':
                    DOKS2 += 1
                    if isHell:
                        if DOKS2 > row: row = table.addRow()
                        table.setText(DOKS2, 8,
                                      forceString(record.value('id')) + '|' + forceString(record.value('name')))
                Dsum += 1
                if isHell:
                    if Dsum > row: row = table.addRow()
                    table.setText(Dsum, 9,
                                  forceString(record.value('id')) + '|' + forceString(record.value('name')))
        row = table.addRow()
        table.setText(row, 0, ONMK)
        table.setText(row, 1, OKS1)
        table.setText(row, 2, OKS2)
        table.setText(row, 3, sum)
        table.setText(row, 4, 0)
        table.setText(row, 5, 0)
        table.setText(row, 6, DOKS1)
        table.setText(row, 7, DOKS2)
        table.setText(row, 8, DONMK)
        table.setText(row, 9, Dsum)

        return doc


class CDeathBSKDialog(QtGui.QDialog, Ui_ReportDeathBSKSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currDate.year(), currDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currDate.year(), currDate.month(), currDate.daysInMonth())))
        self.cmbOrgStruct.setValue(params.get('orgStructId', None))

    def params(self):
        return \
        {
            'begDate'       :   self.edtBegDate.date(),
            'endDate'       :   self.edtEndDate.date(),
            'orgStructId'   :   self.cmbOrgStruct.value(),
            'isHell'        :   self.chkHell.isChecked()
        }