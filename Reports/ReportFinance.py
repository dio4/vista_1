# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import locale
from PyQt4 import QtGui

from ReportPlanningAndEconomicIndicators import CPlanningAndEconomicIndicators
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDouble, forceInt, forceString


def selectData(params, eventTypes):
    db = QtGui.qApp.db
    begDate = params.get('begDate').toString('yyyy-MM-dd')
    endDate = params.get('endDate').toString('yyyy-MM-dd')
    financeId = params.get('financeId')
    groupOrgStructure = params.get('groupOrgStructure')
    orgStructureId = params.get('orgStructureId')

    cond = ['''IF(Visit.id IS NOT NULL, DATE(Visit.date) >= DATE('%(begDate)s') AND DATE(Visit.date) <= DATE('%(endDate)s'),
                IF(Action.id IS NOT NULL, DATE(Action.endDate) >= DATE('%(begDate)s') AND DATE(Action.endDate) <= DATE('%(endDate)s'),
                DATE(Event.execDate) >= DATE('%(begDate)s') AND DATE(Event.execDate) <= DATE('%(endDate)s')))''' % {'begDate': begDate,
                                                                                                                    'endDate': endDate}]
    if eventTypes:
        tableEventType = db.table('EventType')
        cond.append(tableEventType['id'].notInlist(eventTypes))
    if financeId:
        tableFinance = db.table('rbFinance')
        cond.append(tableFinance['id'].eq(financeId))
    if orgStructureId:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].eq(orgStructureId))

    stmt = u'''SELECT
                      Action.endDate as endDate,
                      CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) clientFullName,
                      IF(rbService.code IS NULL, '', rbService.code) AS serviceCode,
                      IF(rbService.name IS NULL, EventType.name, rbService.name) AS service,
                      CONCAT_WS(' / ', Contract.number, Contract.date) as contractNumber,
                      Account_Item.price,
                      sum(Account_Item.amount) AS countService,
                      (SELECT CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) FROM Person WHERE Person.id = Action.setPerson_id) setPerson,
                      CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                      CONCAT_WS(' ', Assistant.lastName, Assistant.firstName, Assistant.patrName) AS assistant,
                      CONCAT_WS(' ', Assistant2.lastName, Assistant2.firstName, Assistant2.patrName) AS assistant2,
                      CONCAT_WS(' ', Assistant3.lastName, Assistant3.firstName, Assistant3.patrName) AS assistant3,
                      OrgStructure.name departmentName
               FROM
                    Account_Item
                    INNER JOIN Event         ON  Event.id  = Account_Item.event_id
                    INNER JOIN EventType     ON  EventType.id = Event.eventType_id
                    LEFT JOIN Visit         ON  Visit.id  = Account_Item.visit_id
                    LEFT JOIN Action        ON  Action.id  = Account_Item.action_id
                    LEFT JOIN ActionType    ON  ActionType.id = Action.actionType_id
                    LEFT JOIN Client        ON  Client.id = Event.client_id
                    LEFT JOIN rbService ON rbService.id = IF(Account_Item.service_id IS NOT NULL,
                                                             Account_Item.service_id,
                                                          IF(Account_Item.visit_id IS NOT NULL,
                                                             Visit.service_id,
                                                             EventType.service_id))
                    INNER JOIN Person ON Person.id = IF(Visit.id, Visit.person_id, IF(Action.id, Action.person_id, Event.execPerson_id))
                    LEFT JOIN Person AS Assistant  ON Assistant.id = (SELECT A_A.person_id
                                                                        FROM Action_Assistant AS A_A
                                                                        INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                                                                        WHERE A_A.action_id = Account_Item.action_id AND rbAAT.code like 'assistant')
                    LEFT JOIN Person AS Assistant2  ON Assistant2.id = (SELECT A_A.person_id
                                                                        FROM Action_Assistant AS A_A
                                                                        INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                                                                        WHERE A_A.action_id = Account_Item.action_id AND rbAAT.code like 'assistant2')
                    LEFT JOIN Person AS Assistant3  ON Assistant3.id = (SELECT A_A.person_id
                                                                        FROM Action_Assistant AS A_A
                                                                        INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id
                                                                        WHERE A_A.action_id = Account_Item.action_id AND rbAAT.code like 'assistant3')
                    INNER JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id AND OrgStructure.deleted = 0
                    INNER JOIN Account ON Account_Item.master_id = Account.id AND Account.deleted = 0
                    LEFT JOIN Contract ON Contract.id = Account.contract_id
                    LEFT JOIN rbFinance ON rbFinance.id = Contract.finance_id
               WHERE 
                Account_Item.refuseType_id IS NULL 
                AND Account_Item.deleted = 0
                AND %s
                GROUP BY serviceCode, service, price, person, assistant, assistant2, assistant3, Contract.number, Action.id %s
                ORDER BY service %s''' % (db.joinAnd(cond), ', OrgStructure.code' if groupOrgStructure else '', ', OrgStructure.code' if groupOrgStructure else '')
    return db.query(stmt)

class CReportFinance(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Финансовая сводка')


    def getSetupDialog(self, parent):
        result = CPlanningAndEconomicIndicators(parent)
        result.setTitle(self.title())
        result.chkGroupingOrgStructure.setVisible(True)
        result.lblFinanceType.setVisible(True)
        result.cmbFinanceType.setVisible(True)
        return result

    def build(self, params):
        eventTypesDict = params.get('eventTypes', None)
        eventTypes =eventTypesDict.keys()
        groupOrgStructure = params.get('groupOrgStructure')
        query = selectData(params, eventTypes)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        if eventTypes:
            cursor.insertText(u'исключены обращения с типами действия: ' + ', '.join([forceString(eventTypesDict[key]) for key in eventTypes]))
        cursor.insertBlock()

        tableColumns = [
            ( '5%', [u'Дата выполнения'], CReportBase.AlignLeft),
            ( '10%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ( ' 5%', [u'Номер договора/Дата'], CReportBase.AlignLeft),
            ( ' 5%', [u'Код услуги'], CReportBase.AlignLeft),
            ( '10%', [u'Наименование услуги'], CReportBase.AlignLeft),
            ( ' 5%', [u'Цена'], CReportBase.AlignLeft),
            ( ' 5%', [u'Количество'], CReportBase.AlignLeft),
            ( ' 5%', [u'Cумма'], CReportBase.AlignLeft),
            ( '8%', [u'Назначивший'], CReportBase.AlignLeft),
            ( '8%', [u'Исполнитель'], CReportBase.AlignLeft),
            ( '8%', [u'Отделение исполнителя'], CReportBase.AlignLeft),
            ( '8%', [u'Ассистент1'], CReportBase.AlignLeft),
            ( '8%', [u'Ассистент2'], CReportBase.AlignLeft),
            ( '8%', [u'Ассистент3'], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)
        locale.setlocale(locale.LC_ALL, '')
        currentOrgStructure = None
        while query.next():
            record = query.record()
            code        = forceString(record.value('code'))
            if groupOrgStructure:
                if currentOrgStructure is None or currentOrgStructure != code:
                    i = table.addRow()
                    table.mergeCells(i, 0, 1, 7)
                    table.setText(i, 0, code, CReportBase.TableTotal)
                    currentOrgStructure = code
            i = table.addRow()
            table.setText(i, 0, forceString(record.value('endDate')))
            table.setText(i, 1, forceString(record.value('clientFullName')))
            table.setText(i, 2, forceString(record.value('contractNumber')))
            table.setText(i, 3, forceString(record.value('serviceCode')))
            table.setText(i, 4, forceString(record.value('service')))
            table.setText(i, 5, locale.format('%10.2f',forceDouble(record.value('price'))))
            table.setText(i, 6, forceInt(record.value('countService')))
            table.setText(i, 7, locale.format('%10.2f', forceDouble(record.value('price')) * forceInt(record.value('countService'))))
            table.setText(i, 8, forceString(record.value('setPerson')))
            table.setText(i, 9, forceString(record.value('person')))
            table.setText(i, 10, forceString(record.value('departmentName')))
            table.setText(i, 11, forceString(record.value('assistant')))
            table.setText(i, 12, forceString(record.value('assistant2')))
            table.setText(i, 13, forceString(record.value('assistant3')))
        return doc
