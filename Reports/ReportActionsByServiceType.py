# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action      import CActionType
from library.constants  import etcTimeTable
from library.Utils      import forceDouble, forceInt, forceRef, forceString, firstMonthDay, lastMonthDay
from Orgs.Utils         import getOrgStructureFullName
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportActionsByServiceTypeSetupDialog import Ui_ReportActionsByServiceTypeSetupDialog


def selectData(params):
    begDate        = params.get('begDate', None)
    endDate        = params.get('endDate', None)
    orgStructureId = params.get('orgStructureId', None)
    fiananceId     = params.get('fiananceId', None)
    podtver        = params.get('podtver', False)
    begDatePodtver = params.get('begDatePodtver', None)
    endDatePodtver = params.get('endDatePodtver', None)
    podtverType    = params.get('podtverType', 0)
    
    db = QtGui.qApp.db
    
    tableAction            = db.table('Action')
    tableActionTypeService = db.table('ActionType_Service')
    tableEvent             = db.table('Event')
    tablePerson            = db.table('vrbPerson')
    tableOrgStructure      = db.table('OrgStructure')
    tableActionType        = db.table('ActionType')
    tableAccountItem       = db.table('Account_Item')
    
    queryTable = tableAction
    
    queryTable = queryTable.leftJoin(tableEvent,        tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.leftJoin(tableActionType,   tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.leftJoin(tablePerson,       tablePerson['id'].eq(tableAction['person_id']))
    queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))
    
    existsCond = [tableActionTypeService['master_id'].eq(tableActionType['id'])]
    if fiananceId:
        existsCond.append(tableActionTypeService['finance_id'].eq(fiananceId))
    cond = [db.existsStmt(tableActionTypeService, existsCond), 
            tableAction['deleted'].eq(0), 
            tableEvent['deleted'].eq(0)]
    if begDate:
#        c = db.joinOr([tableAction['endDate'].dateGe(begDate), tableAction['endDate'].isNull()])
        cond.append(tableAction['endDate'].dateGe(begDate))
    if endDate:
#        c = db.joinOr([tableAction['begDate'].dateLe(endDate), tableAction['begDate'].isNull()])
        cond.append(tableAction['begDate'].dateLe(endDate))
    if orgStructureId:
        cond.append(tableOrgStructure['id'].eq(orgStructureId))
#    if fiananceId:
#        cond.append(tableAction['finance_id'].eq(fiananceId))
    if podtver:
        queryTable = queryTable.leftJoin(tableAccountItem, tableAccountItem['action_id'].eq(tableAction['id']))
        if podtverType == 0:
            cond.append(tableAccountItem['id'].isNull())
        elif podtverType == 1:
            cond.append(tableAccountItem['date'].isNotNull())
            cond.append(tableAccountItem['number'].ne(''))
        elif podtverType == 2:
            cond.append(tableAccountItem['date'].isNotNull())
            cond.append(tableAccountItem['number'].ne(''))
            cond.append(tableAccountItem['refuseType_id'].isNull())
        elif podtverType == 3:
            cond.append(tableAccountItem['date'].isNotNull())
            cond.append(tableAccountItem['number'].ne(''))
            cond.append(tableAccountItem['refuseType_id'].isNotNull())
            
        if begDatePodtver:
            cond.append(tableAccountItem['date'].dateGe(begDatePodtver))
        if endDatePodtver:
            cond.append(tableAccountItem['date'].dateLe(endDatePodtver))
            
    
    fields = [
              tableAction['id'].alias('actionId'), 
              tableOrgStructure['id'].alias('orgStructureId'), 
              tableAction['amount'].name(), 
              tableAction['office'].name(), 
              tableActionType['serviceType'].name(), 
              tablePerson['id'].alias('personId'), 
              tablePerson['code'].alias('personCode'),
              tablePerson['name'].alias('personName'), 
              tableEvent['client_id'].alias('clientId'), 
              tableEvent['id'].alias('eventId')
             ]


    stmt = db.selectStmt(queryTable, fields, cond)
    return db.query(stmt)






class CReportActionsByServiceType(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сводка об оказанных услугах')
        self._mapPersonPlan = {}
        self._mapOrgStructure2PersonDict = {}
        self._mapOrgStructureName2Id = {}
        self._mapPersonId2EventIdList = {}
        self._mapPersonId2InspectionCount = {}
        self._mapOrgStructure2Norm = {}
        self._totalNorm = 0
        self.resetHelpers()
        self._queueEventTypeId = forceRef(QtGui.qApp.db.translate('EventType', 'code', etcTimeTable, 'id'))
        
    def resetHelpers(self):
        self._mapPersonPlan.clear()
        self._mapOrgStructure2PersonDict.clear()
        self._mapOrgStructureName2Id.clear()
        self._mapPersonId2EventIdList.clear()
        self._mapPersonId2InspectionCount.clear()
        self._mapOrgStructure2Norm.clear()
        self._totalNorm = 0
        
    def getSetupDialog(self, parent):
        result = CReportReportActionsByServiceTypeSetup(parent)
        result.setTitle(self.title())
        return result
    
    
    def getDescription(self, params):
        begDate                = params.get('begDate', None)
        endDate                = params.get('endDate', None)
        
        rows = []
        if begDate:
            rows.append(u'Начальная дата периода: %s'%forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s'%forceString(endDate))
            
        return rows
    
    
    def build(self, params):
        self.resetHelpers()
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.structInfo(query, params)
        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        tableColumns = [
                        ('=1',
                        [u'№', u'', u''], CReportBase.AlignRight),
                        ('%3',
                        [u'Код исполнителя', u'', u''], CReportBase.AlignLeft),
                        ('%40',
                        [u'Имя исполнителя', u'', u''], CReportBase.AlignLeft),
                        ('%3',
                        [u'Обращения', u'', u''], CReportBase.AlignRight),
                        ('%3',
                        [u'Оказано услуг', u'В ЛПУ', u'Прочие'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Первичный осмотр'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Повторный осмотр'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Процедура'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Операция'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Исследование'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Лечение'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'На дому', u'Прочие'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Первичный осмотр'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Повторный осмотр'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Процедура'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Операция'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Исследование'], CReportBase.AlignRight),
                        ('%3',
                        [u'', u'', u'Лечение'], CReportBase.AlignRight),
                        ('%3',
                        [u'Норма', u'', u''], CReportBase.AlignRight),
                        ('%3',
                        [u'Норма исследований', u'', u''], CReportBase.AlignRight),
                        ('%3',
                        [u'% от нормы', u'', u''], CReportBase.AlignRight)
                       ]
        
        table = createTable(cursor, tableColumns)
        
        table.mergeCells(0, 0,  3, 1)
        table.mergeCells(0, 1,  3, 1)
        table.mergeCells(0, 2,  3, 1)
        table.mergeCells(0, 3,  3, 1)
        
        table.mergeCells(0, 4,  1, 14)
        table.mergeCells(1, 4,  1, 7)
        table.mergeCells(1, 11, 1, 7)
        table.mergeCells(0, 18, 3, 1)
        table.mergeCells(0, 19, 3, 1)
        table.mergeCells(0, 20, 3, 1)
        
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        
        keyList = self._mapOrgStructureName2Id.keys()
        keyList.sort()
        rowShift = 2
        result = ['', '']+[0]*16+[u'', 0]
        resultLen = 0
        i = 1
        resultCount = 0
        lineLen = len(result) 
        for key in keyList:
            orgStructureId = self._mapOrgStructureName2Id[key]
            i = table.addRow()
            table.setText(i, 1, key, charFormat=boldChars)
            table.mergeCells(i, 0, 1, 21)
            rowShift += 1
            personDict = self._mapOrgStructure2PersonDict[orgStructureId]
            orgStructureRezult = ['', '']+[0]*16+[u'', 0] 
            orgStructureRezultCount = 0
            orgStructureCount = 0
            for personId, personLine in personDict.items():
                personLine[2] = len(self._mapPersonId2EventIdList[personId])
                count = self.printLine(personLine, table, rowShift, orgStructureRezult, personId, self._mapPersonId2EventIdList)
                orgStructureCount += count
            resultCount += orgStructureCount
            self.printLine(orgStructureRezult, table, rowShift, result, orgStructureId, None, boldChars)
            resultLen = len(personDict.keys())
            table.mergeCells(i+resultLen+1, 0, 1, 3)
            self.setResultPercent(table, 
                                  i+resultLen+1, 
                                  lineLen, 
                                  orgStructureCount,  
                                  self._mapOrgStructure2Norm[orgStructureId][0], 
                                  boldChars)
            rowShift += 1
        self.printLine(result, table, rowShift, None, None, None, boldChars)
        table.mergeCells(i+2+resultLen, 0, 1, 3)
        self.setResultPercent(table, 
                              i+resultLen+2, 
                              lineLen, 
                              resultCount,  
                              self._totalNorm, 
                              boldChars)
        
        return doc
        
    def setResultPercent(self, table, row, column, count, norm, boldChars):
        percent = count*100/norm if norm else ''
        table.setText(row, column, percent, charFormat=boldChars)
    
    def printLine(self, values, table, rowShift, result, mapId, map, boldChars=None):
        i = table.addRow()
        if not boldChars:
            table.setText(i, 0, i-rowShift)
        for idx, value in enumerate(values):
            if not boldChars or idx > 1:
                if not boldChars or idx != 18:
                    table.setText(i, idx+1, value, charFormat=boldChars)
            if idx > 1 and result and idx != 18:
                result[idx] += value
        if not (map is None or boldChars):
            count = self._mapPersonId2InspectionCount.get(mapId, 0)
            norm  = values[-3]
            percent = count*100/norm if norm else ''
            table.setText(i, len(values), percent, charFormat=boldChars)
            return count
        return 0
        
        
    def structInfo(self, query, params):
        while query.next():
            record = query.record()
            
            actionId = forceRef(record.value('actionId'))
            orgStructureId = forceRef(record.value('orgStructureId'))
            amount = forceDouble(record.value('amount'))
            serviceType = forceInt(record.value('serviceType'))
            personId = forceRef(record.value('personId'))
            personCode = forceString(record.value('personCode')) 
            personName = forceString(record.value('personName')) if personId else u' Врач не известен'
            office = forceString(record.value('office'))
            clientId = forceRef(record.value('clientId'))
            eventId = forceRef(record.value('eventId'))

            personDict = self._mapOrgStructure2PersonDict.setdefault(orgStructureId, {})
            if not bool(personDict):
                orgStructureName = getOrgStructureFullName(orgStructureId) if orgStructureId else u' Не определено'
                self._mapOrgStructureName2Id[orgStructureName] = orgStructureId
            personLine = personDict.setdefault(personId, [personCode, personName]+[0]*16+[u'', 0])
            
            dataPoint = 3
            for c in [u'д', u'Д']:
                if c in office:
                    dataPoint = 10
            personLine[dataPoint+serviceType] += amount
            if serviceType in [CActionType.serviceTypeInitialInspection, 
                               CActionType.serviceTypeReinspection]:
                result = self._mapPersonId2InspectionCount.get(personId, 0)
                self._mapPersonId2InspectionCount[personId] = result+1
                
            self._setPersonPlan(personId, params, personLine)
            self._setEventId(eventId, personId)
            
            result = self._mapOrgStructure2Norm.setdefault(orgStructureId, [0, []])
            if not personId in result[1]:
                result[1].append(personId)
                result[0] += personLine[17]
            
                self._totalNorm += personLine[17]
            
    def _setEventId(self, eventId, personId):
        result = self._mapPersonId2EventIdList.setdefault(personId, [eventId])
        if not eventId in result:
            result.append(eventId)


    def _setPersonPlan(self, personId, params, personLine):
        result = self._mapPersonPlan.get(personId, None)
        if result is None:
            begDate        = params.get('begDate', None)
            endDate        = params.get('endDate', None)
            
            db = QtGui.qApp.db
            
            tableEvent                 = db.table('Event')
            tableActionType            = db.table('ActionType')
            tableAction                = db.table('Action')
            tableActionProperty        = db.table('ActionProperty')
            tableActionPropertyInteger = db.table('ActionProperty_Integer')
            
            queryTable = tableEvent
            queryTable = queryTable.leftJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.leftJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
            queryTable = queryTable.leftJoin(tableActionPropertyInteger, 
                                             tableActionPropertyInteger['id'].eq(tableActionProperty['id']))
            
            
            cond = [tableEvent['eventType_id'].eq(self._queueEventTypeId),
                    tableEvent['execDate'].dateGe(begDate), 
                    tableEvent['execDate'].dateLe(endDate), 
                    tableEvent['execPerson_id'].eq(personId)
                   ]
            
            result = forceInt(db.getSum(queryTable, tableActionPropertyInteger['value'].name(), cond))
            self._mapPersonPlan[personId] = result
            personLine[17] = result
        return result


class CReportReportActionsByServiceTypeSetup(QtGui.QDialog, Ui_ReportActionsByServiceTypeSetupDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance', addNone=True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(date)))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(date)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbFinance.setValue(params.get('fiananceId', None))
        self.chkPodtver.setChecked(params.get('podtver', False))
        self.edtBegDatePodtver.setDate(params.get('begDatePodtver', firstMonthDay(date)))
        self.edtEndDatePodtver.setDate(params.get('endDatePodtver', lastMonthDay(date)))
        self.cmbPodtver.setCurrentIndex(params.get('podtverType', 0))
    


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['fiananceId'] = self.cmbFinance.value()
        result['podtver'] = self.chkPodtver.isChecked()
        result['podtverType'] = self.cmbPodtver.currentIndex()
        result['begDatePodtver'] = self.edtBegDatePodtver.date()
        result['endDatePodtver'] = self.edtEndDatePodtver.date()
        
        return result



