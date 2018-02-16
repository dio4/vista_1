# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportFinanceSummary import Ui_ReportFinanceSummarySetupDialog
from library.DialogBase import CConstructHelperMixin
from library.TableModel import CTableModel, CTextCol
from library.Utils import forceInt, forceString


def selectData(params, eventTypes):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    financeId = params.get('financeId')
    person = params.get('person')
    orgStruct = params.get('orgStructure')
    byActionEndDate = params.get('byActionEndDate', False)
    contracts = params.get('contracts', [])

    tableAccount   = db.table('Account')
    tableAction    = db.table('Action')
    tablePerson    = db.table('Person')
    tableOrgStruct = db.table('OrgStructure')
    tableEvent     = db.table('Event')
    tableVisit     = db.table('Visit')
    tableContract  = db.table('Contract')

    if byActionEndDate:
        cond = ['if(Action.id IS NOT NULL, %s, IF( Visit.id IS NOT NULL, %s, %s))' % (db.joinAnd([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].dateLe(endDate)]),
                                                                                      db.joinAnd([tableVisit['date'].dateGe(begDate), tableVisit['date'].dateLe(endDate)]),
                                                                                      db.joinAnd([tableEvent['execDate'].dateGe(begDate), tableEvent['execDate'].dateLe(endDate)]))]
    else:
        cond = [
            # tableAction['deleted'].eq(0),
            tableAccount['date'].dateGe(begDate),
            tableAccount['date'].dateLe(endDate)
        ]

    if eventTypes:
        tableEventType = db.table('EventType')
        cond.append(tableEventType['id'].inlist(eventTypes))
    if financeId:
        tableFinance = db.table('rbFinance')
        cond.append(tableFinance['id'].eq(financeId))
    if person:
        cond.append(tablePerson['id'].eq(person))
    if orgStruct:
        cond.append(tableOrgStruct['id'].eq(orgStruct))
    if contracts:
        cond.append(tableContract['id'].inlist(contracts))

    stmt = u'''SELECT CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                      CONCAT_WS(' ', Assistant.lastName, Assistant.firstName, Assistant.patrName) AS assistant,
                      CONCAT_WS(' ', Assistant2.lastName, Assistant2.firstName, Assistant2.patrName) AS assistant2,
                      CONCAT_WS(' ', Assistant3.lastName, Assistant3.firstName, Assistant3.patrName) AS assistant3,
                      sum(Account_Item.amount) count,
                      sum(Account_Item.price * Account_Item.amount) AS summa
              FROM  Account_Item
                    INNER JOIN Event ON Event.id = Account_Item.event_id
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    LEFT JOIN Visit ON Visit.id = Account_Item.visit_id
                    LEFT JOIN Action ON Action.id = Account_Item.action_id AND Action.deleted = 0
                    INNER JOIN Person ON Person.id = IF(Visit.id, Visit.person_id, IF(Action.id, Action.person_id, Event.execPerson_id))
                    LEFT JOIN rbActionAssistantType as rbAAT1 ON rbAAT1.code = 'assistant'
                    LEFT JOIN rbActionAssistantType as rbAAT2 ON rbAAT2.code = 'assistant2'
                    LEFT JOIN rbActionAssistantType as rbAAT3 ON rbAAT3.code = 'assistant3'
                    LEFT JOIN Action_Assistant as A_A1 ON A_A1.action_id = Account_Item.action_id AND A_A1.assistantType_id = rbAAT1.id
                    LEFT JOIN Action_Assistant as A_A2 ON A_A2.action_id = Account_Item.action_id AND A_A2.assistantType_id = rbAAT2.id
                    LEFT JOIN Action_Assistant as A_A3 ON A_A3.action_id = Account_Item.action_id AND A_A3.assistantType_id = rbAAT3.id
                    LEFT JOIN Person AS Assistant ON Assistant.id = A_A1.person_id
                    LEFT JOIN Person AS Assistant2 ON Assistant2.id = A_A2.person_id
                    LEFT JOIN Person AS Assistant3 ON Assistant3.id = A_A3.person_id
                    LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id AND OrgStructure.deleted = 0
                    INNER JOIN Account ON Account_Item.master_id = Account.id AND Account.deleted = 0
                    LEFT JOIN Contract ON Contract.id = Account.contract_id
                    LEFT JOIN rbFinance ON rbFinance.id = Contract.finance_id
              WHERE Account_Item.refuseType_id IS NULL AND Account_Item.deleted = 0 AND %s
              GROUP BY person, assistant, assistant2, assistant3
              ORDER BY person, assistant, assistant2, assistant3''' % db.joinAnd(cond)
    return db.query(stmt)


class CReportFinanceSummary(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Финансовая сводка по врачам и ассистентам')


    def getSetupDialog(self, parent):
        result = CReportFinanceSummarySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        eventTypesDict = params.get('eventTypes', None)
        eventTypes = eventTypesDict.keys()
        query = selectData(params, eventTypes)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertText(u'Договоры: ')
        contracts = params.get('contracts', [])
        if contracts:
            db = QtGui.qApp.db
            tableContract = db.table('Contract')
            contractsList = db.getRecordList(tableContract, where=tableContract['id'].inlist(contracts))
            cursor.insertText(u', '.join([
                u' '.join([
                    forceString(contract.value(field)) for field in ['number', 'date', 'resolution']
                ]) for contract in contractsList
            ]))
        else:
            cursor.insertText(u'все')
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('20%', [u'ФИО врача'],        CReportBase.AlignLeft),
            ('20%', [u'Первый ассистент'], CReportBase.AlignLeft),
            ('20%', [u'Второй ассистент'], CReportBase.AlignLeft),
            ('20%', [u'Третий ассистент'], CReportBase.AlignLeft),
            ('10%', [u'Количество услуг'], CReportBase.AlignRight),
            ('10%', [u'Сумма'],            CReportBase.AlignRight)]

        table = createTable(cursor, tableColumns)
        total_count = 0
        total_sum = 0
        while query.next():
            record = query.record()
            person = forceString(record.value('person'))
            assistant = forceString(record.value('assistant'))
            assistant2 = forceString(record.value('assistant2'))
            assistant3 = forceString(record.value('assistant3'))
            count = forceInt(record.value('count'))
            summa = forceInt(record.value('summa'))
            i = table.addRow()
            table.setText(i, 0, person)
            table.setText(i, 1, assistant)
            table.setText(i, 2, assistant2)
            table.setText(i, 3, assistant3)
            table.setText(i, 4, count)
            table.setText(i, 5, u'%s руб' % summa)
            total_count += count
            total_sum += summa
        i = table.addRow()
        table.setText(i, 0, u'Итого:',   CReportBase.TableTotal, CReportBase.AlignRight)
        table.setText(i, 4, total_count, CReportBase.TableTotal)
        table.setText(i, 5, u'%s руб' % total_sum,   CReportBase.TableTotal)
        table.mergeCells(i, 0, 1, 4)

        return doc


class CContractsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(u'Номер',     ['number'],  30),
            CTextCol(u'Дата',      ['date'], 30),
            CTextCol(u'Основание', ['resolution'],  30),
        ], 'Contract')


class CReportFinanceSummarySetupDialog(QtGui.QDialog, CConstructHelperMixin, Ui_ReportFinanceSummarySetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstItems.setTable('EventType')

        self.addModels('Contracts', CContractsModel(self))
        self.modelContracts.sort('number')
        self.initContractList()
        self.lstContracts.setModel(self.modelContracts)

        self.cmbFinanceType.setTable('rbFinance')
        self.cmbOrgStruct.setOrgId(QtGui.qApp.currentOrgId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbFinanceType.setValue(params.get('financeId', None))
        self.cmbPerson.setValue(params.get('person'))
        self.cmbOrgStruct.setValue(params.get('orgStructure'))
        self.rbtnByActionEndDate.setChecked(params.get('byActionEndDate', False))
        self.lstContracts.setSelectedItemIdList(params.get('contracts', []))

    def params(self):
        result = {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'eventTypes': self.lstItems.nameValues(),
            'financeId': self.cmbFinanceType.value(),
            'person': self.cmbPerson.value(),
            'orgStructure': self.cmbOrgStruct.value(),
            'byActionEndDate': self.rbtnByActionEndDate.isChecked(),
            'contracts': self.lstContracts.selectedItemIdList()
        }
        return result

    def initContractList(self):
        db = QtGui.qApp.db
        tableContract = db.table('Contract')

        currentDate = QtCore.QDate.currentDate()
        minDate = QtCore.QDate(currentDate.year() - 2, currentDate.month(), currentDate.day())
        cond = []
        cond.append(tableContract['date'].dateGe(minDate))

        financeType = self.cmbFinanceType.value()
        if financeType:
            cond.append(tableContract['finance_id'].eq(financeType))

        cond = db.joinAnd(cond)
        self.modelContracts.setIdList(db.getIdList(tableContract, where=cond))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStruct_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStruct.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbFinanceType_currentIndexChanged(self, index):
        self.initContractList()