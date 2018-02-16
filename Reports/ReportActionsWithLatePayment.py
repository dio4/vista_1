# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on Sep 17, 2012

@author: atronah
"""

from PyQt4 import QtGui

from Orgs.Utils                 import getOrgStructureDescendants
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog
from library.Utils import forceString, forceRef, formatName, forceDate, forceBool


def selectData(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', None)
    personId = params.get('personId', None)
    contractIdList = params.get('contractIdList', None)
    onlyNotPayedEvents = params.get('onlyNotPayedEvents', None)
    onlyEmployee = params.get('onlyEmployee', None)
    ageFrom = params.get('ageFrom', None)
    ageTo = params.get('ageTo', None)
    
    db = QtGui.qApp.db
    
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tablePerson = db.table('Person')
    tableAccountItem = db.table('Account_Item')
    tableContract = db.table('Contract')
    
    queryTable = tableAction.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableContract, '%s = %s' %(tableContract['id'].name(),
                                                                 'IF(Action.`contract_id`, Action.`contract_id`, Event.`contract_id`)'))
    
    cond = []
    orderList = [tableAction['endDate'].name(),
                 tableClient['lastName'].name(),
                 tableClient['firstName'].name(),
                 tableClient['patrName'].name()]
    
    cond.append(tableAction['deleted'].eq(0))
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableClient['deleted'].eq(0))
    cond.append(db.joinOr([tablePerson['id'].isNull(), tablePerson['deleted'].eq(0)]))
    
    cond.append(db.joinOr([tableAccountItem['date'].isNull(),
                           tableAction['endDate'].dateLt(tableAccountItem['date'])]
                          )
                )    
    
    if begDate:
        cond.append(tableAction['endDate'].dateGe(begDate))
    if endDate:
        cond.append(tableAction['endDate'].dateLe(endDate))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if contractIdList:
        cond.append(tableContract['id'].inlist(contractIdList))
    if onlyNotPayedEvents:
        cond.append(db.joinOr([tableAccountItem['date'].isNull(),
                               tableAccountItem['refuseType_id'].isNotNull()]))
    if onlyEmployee:
        cond.append('EXISTS (SELECT * \
                             FROM ClientWork \
                             WHERE ClientWork.id = (SELECT MAX(id) \
                                                     FROM ClientWork AS CW \
                                                     WHERE CW.client_id = Client.id) \
                                    AND ClientWork.org_id=%d)' % (QtGui.qApp.currentOrgId()))
    if ageFrom <= ageTo:
        cond.append('%s >= %s' % (tableAction['endDate'].name(), 'ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % ageFrom))
        cond.append('%s < %s' % (tableAction['endDate'].name(), 'SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR), 1)' % (ageTo + 1)))
        
        
    fields = [tableClient['id'].alias('clientId'),
              tableClient['lastName'].alias('clientLastName'),
              tableClient['firstName'].alias('clientFirstName'),
              tableClient['patrName'].alias('clientPatrName'),
              tableActionType['name'].alias('actionName'),
              tableAction['endDate'].alias('actionEndDate'),
              tableAccountItem['date'].alias('actionPayDate'),
              tableAccountItem['number'].alias('payConfirmationNumber'),
              tablePerson['lastName'].alias('personLastName'),
              tablePerson['firstName'].alias('personFirstName'),
              tablePerson['patrName'].alias('personPatrName'),
              '(%s) AS isRefused' % tableAccountItem['refuseType_id'].isNotNull()
              ]
    
    stmt = db.selectStmt(queryTable, fields = fields, where = cond, order = orderList)
    
    return db.query(stmt)


class CReportActionsWithLatePayment(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по услугам, имеющим позднюю оплату')
        
    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setOrgStructureVisible(True)
        result.setSpecialityVisible(True)
        result.setPersonWithoutDetailCheckboxVisible(True)
        result.setContractVisible(True)
        result.setEventTypeVisible(False)
        result.setOnlyPermanentAttachVisible(False)
        result.setOnlyNotPayedVisible(True)
        result.setOnlyEmployeeVisible(True)
        result.setGroupByClients(True)
        result.setAgeVisible(True)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        groupByClients = params.get('groupByClients', None)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('?2', [u'№ п/п'], CReportBase.AlignRight),
                        ('?5', [u'Ф.И.О. пациента'], CReportBase.AlignCenter),
                        ('?5', [u'Номер услуги'], CReportBase.AlignCenter),
                        ('%5', [u'Название услуги'], CReportBase.AlignLeft),
                        ('%5', [u'Дата выполнения услуги'], CReportBase.AlignCenter),
                        ('%5', [u'Дата оплаты услуги'], CReportBase.AlignCenter),
                        ('%5', [u'Исполнитель услуги'], CReportBase.AlignLeft),
                        ]

        table = createTable(cursor, tableColumns)

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        
        prevClientId = None
        rowIndex = 1
        clientRepetitionNumber = 1
        while query.next():
            record = query.record()
            
            i = table.addRow()

            clientId = forceRef(record.value('clientId'))
            clientName = formatName(
                                    record.value('clientLastName'),
                                    record.value('clientFirstName'),
                                    record.value('clientPatrName')
                                   )
            actionName = forceString(record.value('actionName'))
            execDate = forceDate(record.value('actionEndDate')).toString('dd.MM.yyyy')
            payDate = forceDate(record.value('actionPayDate')).toString('dd.MM.yyyy')
            isRefused = forceBool(record.value('isRefused'))
            payConfirmationNumber = forceString(record.value('payConfirmationNumber'))
            personName = formatName(
                                    record.value('personLastName'),
                                    record.value('personFirstName'),
                                    record.value('personPatrName')
                                   )
            payDateText = payDate if (payDate and not isRefused and payConfirmationNumber) \
                                    else (u'Отказано' if payDate and isRefused else u'Выставлено')
            
            if not groupByClients or clientId != prevClientId :
                table.setText(i, 0, rowIndex)
                table.setText(i, 1, u'%s; %s' % (clientName, clientId), charFormat = CReportBase.TableBody)
                rowIndex += 1
                if clientRepetitionNumber > 1:
                    clientRepetitionNumber -= 1
                    table.mergeCells(i - clientRepetitionNumber, 0, clientRepetitionNumber, 1)
                    table.mergeCells(i - clientRepetitionNumber, 1, clientRepetitionNumber, 1)
                clientRepetitionNumber = 1
            table.setText(i, 2, i, charFormat = CReportBase.TableBody)
            table.setText(i, 3, actionName, charFormat = CReportBase.TableBody)
            table.setText(i, 4, execDate, charFormat = CReportBase.TableBody)
            table.setText(i, 5, payDateText, charFormat = CReportBase.TableBody)
            table.setText(i, 6, personName, charFormat = CReportBase.TableBody)            
            prevClientId = clientId
            clientRepetitionNumber += 1
        return doc