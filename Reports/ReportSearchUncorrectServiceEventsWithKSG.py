# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils import CFinanceType
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportSearchUncorrectServiceEventsWithKSG import Ui_ReportSearchUncorrectServiceEventsWithKSG
from library.Utils import firstMonthDay, forceDate, forceRef, forceString, lastMonthDay


def secondMesControlForSettleDateControl(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    personId = params.get('personId')
    orgStructureId = params.get('orgStructureId')
    financeId = params.get('typeFinanceId', None)

    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableOrgStructure = db.table('OrgStructure')
    tableContract = db.table('Contract')
    tableEventType = db.table('EventType')
    tableRbEventProfile = db.table('rbEventProfile')

    cond = [
        tableAccount['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0)
    ]
    condDate = [tableAccount['settleDate'].dateGe(begDate), tableAccount['settleDate'].dateLe(endDate)]
    cond.extend(condDate)
    if personId: cond.append(tableVrbPersonWithSpeciality['id'].eq(personId))
    if orgStructureId: cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    # cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableContract['finance_id'].eq(financeId))
    cond.append(tableRbEventProfile['regionalCode'].inlist([11, 12, 41, 42, 43, 51, 52, 71, 72, 90]))
    cond.append(tableEvent['MES_id'].isNotNull())
    cond.append("""
    NOT EXISTS(
      SELECT *
      FROM
        mes.MES
        LEFT JOIN mes.MES_service ON mes.MES.id = mes.MES_service.master_id
        LEFT JOIN mes.mrbService ON mes.MES_service.service_id = mes.mrbService.id
        LEFT JOIN ActionType ON mes.mrbService.code = ActionType.code
        LEFT JOIN Action ON ActionType.id = Action.actionType_id AND Action.deleted = 0
	    LEFT JOIN Account_Item AI ON AI.action_id = Action.id AND AI.deleted = 0
      WHERE
        mes.MES.id = Event.MES_id
        AND (mes.MES_service.id IS NULL OR AI.id IS NOT NULL)
        AND IF (Action.id IS NOT NULL, Action.event_id = Event.id, 1)
        AND IF (AI.id IS NOT NULL, AI.master_id = Account.id, 1)
  )
    """
    )

    select = [
        tableClient['id'],
        # 'CONCAT_WS(\' \', Client.lastName, Client.firstName, Client.patrName) AS client',
        db.CONCAT_WS([tableClient['lastName'], tableClient['firstName'], tableClient['patrName']], alias='client'),
        tableClient['birthDate'],
        tableEvent['setDate'],
        tableEvent['execDate'],
        # 'CONCAT_WS(\' \', vrbPersonWithSpeciality.code, vrbPersonWithSpeciality.name) AS person',
        db.CONCAT_WS([tableVrbPersonWithSpeciality['code'], tableVrbPersonWithSpeciality['name']], alias='person'),
        tableVrbPersonWithSpeciality['orgStructure_id'].alias('orgStructure')
    ]

    order = [tableClient['id'], tableEvent['setDate'], tableEvent['execDate']]

    queryTable = tableAccount.innerJoin(tableAccountItem, tableAccount['id'].eq(tableAccountItem['master_id']))
    queryTable = queryTable.innerJoin(tableEvent, [tableAccountItem['event_id'].eq(tableEvent['id']), tableEvent['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableVrbPersonWithSpeciality, tableEvent['execPerson_id'].eq(tableVrbPersonWithSpeciality['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableVrbPersonWithSpeciality['orgStructure_id'].eq(tableOrgStructure['id']))
    queryTable = queryTable.innerJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))
    queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
    queryTable = queryTable.innerJoin(tableRbEventProfile, tableEventType['eventProfile_id'].eq(tableRbEventProfile['id']))

    return db.query(db.selectStmt(queryTable, select, cond, order=order))

def secondMesControl(params):
    if not params.get('type'): return secondMesControlForSettleDateControl(params)

    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    personId = params.get('personId')
    orgStructureId = params.get('orgStructureId')
    financeId = params.get('typeFinanceId', None)

    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableOrgStructure = db.table('OrgStructure')
    tableContract = db.table('Contract')
    tablePerson = db.table('Person')
    tableEventType = db.table('EventType')
    tableRbEventProfile = db.table('rbEventProfile')

    cond = []
    condDate = [tableEvent['execDate'].dateGe(begDate), tableEvent['execDate'].dateLe(endDate)]
    cond.extend(condDate)
    if personId: cond.append(tablePerson['id'].eq(personId))
    if orgStructureId: cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableContract['finance_id'].eq(financeId))
    cond.append(tableRbEventProfile['regionalCode'].inlist([11, 12, 41, 42, 43, 51, 52, 71, 72, 90]))

    select = [tableClient['id'],
          # 'CONCAT_WS(\' \', Client.lastName, Client.firstName, Client.patrName) AS client',
          db.CONCAT_WS([tableClient['lastName'], tableClient['firstName'], tableClient['patrName']], alias='client'),
          tableClient['birthDate'],
          tableEvent['setDate'],
          tableEvent['execDate'],
          # 'CONCAT_WS(\' \', vrbPersonWithSpeciality.code, vrbPersonWithSpeciality.name) AS person',
          db.CONCAT_WS([tableVrbPersonWithSpeciality['code'], tableVrbPersonWithSpeciality['name']], alias='person'),
          tableVrbPersonWithSpeciality['orgStructure_id'].alias('orgStructure')]

    queryTable = tableEvent.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableVrbPersonWithSpeciality, tableEvent['execPerson_id'].eq(tableVrbPersonWithSpeciality['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableVrbPersonWithSpeciality['orgStructure_id'].eq(tableOrgStructure['id']))
    queryTable = queryTable.innerJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))
    queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
    queryTable = queryTable.innerJoin(tableRbEventProfile, tableEventType['eventProfile_id'].eq(tableRbEventProfile['id']))

    cond.append(tableEvent['MES_id'].isNotNull())
    cond.append("""
    NOT EXISTS(
          SELECT *
          FROM
            mes.MES
            LEFT JOIN mes.MES_service ON mes.MES.id = mes.MES_service.master_id
            LEFT JOIN mes.mrbService ON mes.MES_service.service_id = mes.mrbService.id
            LEFT JOIN ActionType ON mes.mrbService.code = ActionType.code
            LEFT JOIN Action ON ActionType.id = Action.actionType_id AND Action.deleted = 0
          WHERE
            mes.MES.id = Event.MES_id
            AND (mes.MES_service.id IS NULL OR (Action.id IS NOT NULL
            AND Action.event_id = Event.id ))
    )
    """
    )

    order = [tableClient['id'], tableEvent['setDate'], tableEvent['execDate']]
    return db.query(db.selectStmt(queryTable, select, cond, order=order))

def selectDataForSettleDateControl(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    personId = params.get('personId')
    orgStructureId = params.get('orgStructureId')
    financeId = params.get('typeFinanceId', None)

    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableOrgStructure = db.table('OrgStructure')
    tableContract = db.table('Contract')
    tableEventType = db.table('EventType')
    tableRbEventProfile = db.table('rbEventProfile')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableMES = db.table('mes.MES')
    tableMrbService = db.table('mes.mrbService')
    tableMES_service = db.table('mes.MES_service')
    tableMES2 = tableMES.alias('MES2')

    select = [
        tableClient['id'],
        # 'CONCAT_WS(\' \', Client.lastName, Client.firstName, Client.patrName) AS client',
        db.CONCAT_WS([tableClient['lastName'], tableClient['firstName'], tableClient['patrName']], alias='client'),
        tableClient['birthDate'],
        tableEvent['setDate'],
        tableEvent['execDate'],
        # 'CONCAT_WS(\' \', vrbPersonWithSpeciality.code, vrbPersonWithSpeciality.name) AS person',
        db.CONCAT_WS([tableVrbPersonWithSpeciality['code'], tableVrbPersonWithSpeciality['name']], alias='person'),
        tableVrbPersonWithSpeciality['orgStructure_id'].alias('orgStructure')
    ]

    cond = [
        tableAccount['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0)
    ]
    condDate = [tableAccount['settleDate'].dateGe(begDate), tableAccount['settleDate'].dateLe(endDate)]
    cond.extend(condDate)
    if personId: cond.append(tableVrbPersonWithSpeciality['id'].eq(personId))
    if orgStructureId: cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableContract['finance_id'].eq(financeId))
    cond.append(tableRbEventProfile['regionalCode'].inlist([11, 12, 41, 42, 43, 51, 52, 71, 72, 90]))
    cond.append(tableMES['code'].inlist(["G10.02.008", "G10.31.226", "G10.34.244", "G10.02.007", "G10.16.081", "G10.04.022", "G10.30.200", "G10.26.166", "G10.02.007", "G10.21.143", "G10.16.081", "G40.21.143", "G40.31.226", "G50.21.143", "G50.31.226", "G70.21.143", "G70.31.226"]))
    cond.append(tableMES2['code'].inlist(["G10.02.013", "G10.31.211", "G10.34.245", "G10.02.013", "G10.29.193", "G10.14.064", "G10.09.037", "G10.34.245", "G10.02.014", "G10.21.138", "G10.29.196", "G40.21.138", "G40.31.211", "G50.21.138", "G50.31.211", "G70.21.138", "G70.31.211"]))

    group = [tableEvent['id']]

    order = [tableClient['id'], tableEvent['setDate'], tableEvent['execDate']]

    queryTable = tableAccount.innerJoin(tableAccountItem, tableAccount['id'].eq(tableAccountItem['master_id']))
    queryTable = queryTable.innerJoin(tableEvent, [tableAccountItem['event_id'].eq(tableEvent['id']), tableEvent['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableVrbPersonWithSpeciality, tableEvent['execPerson_id'].eq(tableVrbPersonWithSpeciality['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableVrbPersonWithSpeciality['orgStructure_id'].eq(tableOrgStructure['id']))
    queryTable = queryTable.innerJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))
    queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
    queryTable = queryTable.innerJoin(tableRbEventProfile, tableEventType['eventProfile_id'].eq(tableRbEventProfile['id']))

    queryTable = queryTable.innerJoin(tableAction, tableAccountItem['action_id'].eq(tableAction['event_id']))
    queryTable = queryTable.innerJoin(tableActionType, [tableAction['actionType_id'].eq(tableActionType['id']), tableActionType['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableMES, tableEvent['MES_id'].eq(tableMES['id']))
    queryTable = queryTable.innerJoin(tableMrbService, tableActionType['code'].eq(tableMrbService['code']))
    queryTable = queryTable.innerJoin(tableMES_service, tableMrbService['id'].eq(tableMES_service['service_id']))
    queryTable = queryTable.innerJoin(tableMES2, tableMES_service['master_id'].eq(tableMES2['id']))

    return db.query(db.selectStmt(queryTable, select, cond, group=group, order=order))

def selectData(params):
    #
    if not params.get('type'): return selectDataForSettleDateControl(params)

    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    personId = params.get('personId')
    orgStructureId = params.get('orgStructureId')
    financeId = params.get('typeFinanceId', None)

    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableOrgStructure = db.table('OrgStructure')
    tableContract = db.table('Contract')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')

    cond = []
    condDate = [tableEvent['execDate'].dateGe(begDate), tableEvent['execDate'].dateLe(endDate)]
    cond.extend(condDate)
    if personId: cond.append(tableVrbPersonWithSpeciality['id'].eq(personId))
    if orgStructureId: cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableContract['finance_id'].eq(financeId))

    select = [
        tableClient['id'],
        # 'CONCAT_WS(\' \', Client.lastName, Client.firstName, Client.patrName) AS client',
        db.CONCAT_WS([tableClient['lastName'], tableClient['firstName'], tableClient['patrName']], alias='client'),
        tableClient['birthDate'],
        tableEvent['setDate'],
        tableEvent['execDate'],
        # 'CONCAT_WS(\' \', vrbPersonWithSpeciality.code, vrbPersonWithSpeciality.name) AS person',
        db.CONCAT_WS([tableVrbPersonWithSpeciality['code'], tableVrbPersonWithSpeciality['name']], alias='person'),
        tableVrbPersonWithSpeciality['orgStructure_id'].alias('orgStructure')
    ]

    queryTable = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.innerJoin(tableActionType, [tableActionType['id'].eq(tableAction['actionType_id']),
                                                        #TODO: skkachaev: Возможно, это нужно для typeQuery == 'mesDuration'
                                                        #tableActionType['flatCode'].eq('moving'),
                                                        tableActionType['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableVrbPersonWithSpeciality, tableEvent['execPerson_id'].eq(tableVrbPersonWithSpeciality['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableVrbPersonWithSpeciality['orgStructure_id']))
    queryTable = queryTable.innerJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))

    group = [tableEvent['id']]

    tableMES = db.table('mes.MES')
    tableMES2 = tableMES.alias('mes2')
    tableMrbService = db.table('mes.mrbService')
    tableMESService = db.table('mes.MES_service')
    tableEventType = db.table('EventType')
    tableRbEventProfile = db.table('rbEventProfile')
    queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
    queryTable = queryTable.innerJoin(tableRbEventProfile, tableEventType['eventProfile_id'].eq(tableRbEventProfile['id']))
    queryTable = queryTable.innerJoin(tableMES, tableEvent['MES_id'].eq(tableMES['id']))
    queryTable = queryTable.innerJoin(tableMrbService, tableActionType['code'].eq(tableMrbService['code']))
    queryTable = queryTable.innerJoin(tableMESService, tableMrbService['id'].eq(tableMESService['service_id']))
    queryTable = queryTable.innerJoin(tableMES2, tableMESService['master_id'].eq(tableMES2['id']))
    cond.append(tableRbEventProfile['regionalCode'].inlist([11, 12, 41, 42, 43, 51, 52, 71, 72, 90]))
    cond.append(tableMES['code'].inlist(["G10.02.008", "G10.31.226", "G10.34.244", "G10.02.007", "G10.16.081", "G10.04.022", "G10.30.200", "G10.26.166", "G10.02.007", "G10.21.143", "G10.16.081", "G40.21.143", "G40.31.226", "G50.21.143", "G50.31.226", "G70.21.143", "G70.31.226"]))
    cond.append(tableMES2['code'].inlist(["G10.02.013", "G10.31.211", "G10.34.245", "G10.02.013", "G10.29.193", "G10.14.064", "G10.09.037", "G10.34.245", "G10.02.014", "G10.21.138", "G10.29.196", "G40.21.138", "G40.31.211", "G50.21.138", "G50.31.211", "G70.21.138", "G70.31.211"]))

    order = [tableClient['id'], tableEvent['setDate'], tableEvent['execDate']]
    return db.query(db.selectStmt(queryTable, select, cond, group=group, order=order))

class CReportSearchUncorrectServiceEventsWithKSG(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Контроль комбинации КСГ и услуги оперативного вмешательства')

    def getSetupDialog(self, parent):
        result = CSearchUncorrectServiceEventsWithKSG(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title(), CReportBase.ReportTitle)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            (' 3%',  [u'№ п/п'                ], CReportBase.AlignLeft),
            (' 5%',  [u'Код пациента'          ], CReportBase.AlignRight),
            ('20%',  [u'ФИО пациента'          ], CReportBase.AlignRight),
            (' 5%',  [u'Дата рождения'         ], CReportBase.AlignRight),
            ('10%',  [u'Период лечения'        ], CReportBase.AlignRight),
            ('20%',  [u'Врач'                  ], CReportBase.AlignRight),
            ('10%',  [u'Подразделение'         ], CReportBase.AlignRight),
            ('15%',  [u'Контроль'              ], CReportBase.AlignRight)]

        table = createTable(cursor, tableColumns)

        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, forceRef(record.value('id')))
            # table.setText(i, 2, forceString(record.value('externalId')))
            table.setText(i, 2, forceString(record.value('client')))
            table.setText(i, 3, forceString(record.value('birthDate')))
            table.setText(i, 4, forceDate(record.value('setDate')).toString('dd.MM.yyyy') + ' - ' + forceDate(record.value('execDate')).toString('dd.MM.yyyy'))
            table.setText(i, 5, forceString(record.value('person')))
            table.setText(i, 6, getOrgStructureFullName(record.value('orgStructure')))
            table.setText(i, 7, u" Указанный КСГ не соответствует страховому случаю и справочнику SPR69, SPR70")

        query = secondMesControl(params)
        self.setQueryText(self.queryText() + '\n\n' + forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, forceRef(record.value('id')))
            table.setText(i, 2, forceString(record.value('client')))
            table.setText(i, 3, forceString(record.value('birthDate')))
            table.setText(i, 4, forceDate(record.value('setDate')).toString('dd.MM.yyyy') + ' - ' + forceDate(record.value('execDate')).toString('dd.MM.yyyy'))
            table.setText(i, 5, forceString(record.value('person')))
            table.setText(i, 6, getOrgStructureFullName(record.value('orgStructure')))
            table.setText(i, 7, u'Для указанного КСГ, отсутствует услуга оперативного вмешательства по справочнику SPR69')

        return doc

class CSearchUncorrectServiceEventsWithKSG(QtGui.QDialog, Ui_ReportSearchUncorrectServiceEventsWithKSG):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    # noinspection PyArgumentList
    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(QtCore.QDate.currentDate())))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(QtCore.QDate.currentDate())))

        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))

        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbFinance.setValue(params.get('typeFinanceId', CFinanceType.getId(CFinanceType.CMI))) # 2 — код ОМС

    def params(self):
        result = {'begDate'         : self.edtBegDate.date(),
                  'endDate'         : self.edtEndDate.date(),
                  'orgStructureId'  : self.cmbOrgStructure.value(),
                  'personId'        : self.cmbPerson.value(),
                  'typeFinanceId'   : self.cmbFinance.value(),
                  #Обратите сюда внимание, если захотите добавить еще один чекбокс — работать не будет
                  'type'            : self.rb1.isChecked()
                 }
        return result

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    # noinspection PyUnusedLocal
    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)