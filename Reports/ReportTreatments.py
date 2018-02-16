# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.constants          import etcTimeTable, atcAmbulance, atcHome
from library.Utils              import forceInt, forceRef, forceString
from Orgs.Utils                 import getOrgStructureFullName

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase

from Ui_ReportTreatmentsSetup   import Ui_ReportTreatmentsSetupDialog


def selectVisitsData(params):
    begDate                = params.get('begDate', None)
    endDate                = params.get('endDate', None)
    financeId              = params.get('financeId', None)
    purposeId              = params.get('purposeId', None)
    eventTypeId            = params.get('eventTypeId', None)
    medicalAidTypeId       = params.get('medicalAidTypeId', None)
    orgStructureId         = params.get('orgStructureId', None)
    personId               = params.get('personId', None)
    tariffing              = params.get('tariffing', 0)
    
    db = QtGui.qApp.db
    
    tableEventType    = db.table('EventType')
    tableEvent        = db.table('Event')
    tableVisit        = db.table('Visit')
    tableScene        = db.table('rbScene')
    tableOrgStructure = db.table('OrgStructure')
    tablePerson       = db.table('vrbPersonWithSpeciality')
    
    queryTable = tableEvent
    
    queryTable = queryTable.leftJoin(tableVisit, tableVisit['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.leftJoin(tableScene, tableScene['id'].eq(tableVisit['scene_id']))
    queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableVisit['person_id']))
    queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))
    
    cond = []
    
    if begDate and begDate.isValid():
        cond.append(tableEvent['execDate'].dateGe(begDate))
    if endDate and endDate.isValid():
        cond.append(tableEvent['execDate'].dateLe(endDate))
    if purposeId:
        cond.append(tableEventType['purpose_id'].eq(purposeId))
    if eventTypeId:
        cond.append(tableEventType['id'].eq(eventTypeId))
    if medicalAidTypeId:
        cond.append(tableEventType['medicalAidType_id'].eq(medicalAidTypeId))
    if orgStructureId:
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        cond.append(tableOrgStructure['id'].inlist(orgStructureIdList))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    
    fields = [tablePerson['code'].alias('personCode'),
              tablePerson['name'].alias('personName'),
              tablePerson['id'].alias('personId'), 
              tableEvent['client_id'].alias('clientId'), 
              tableEvent['id'].alias('eventId'), 
              tableOrgStructure['id'].alias('orgStructureId'), 
              tableScene['code'].alias('sceneCode')
              ]
    
    stmt = db.selectStmt(queryTable, fields, cond)
    return db.query(stmt)

def selectActionsData(params):
    begDate                = params.get('begDate', None)
    endDate                = params.get('endDate', None)
    financeId              = params.get('financeId', None)
    purposeId              = params.get('purposeId', None)
    eventTypeId            = params.get('eventTypeId', None)
    medicalAidTypeId       = params.get('medicalAidTypeId', None)
    orgStructureId         = params.get('orgStructureId', None)
    personId               = params.get('personId', None)
    tariffing              = params.get('tariffing', 0)
    
    db = QtGui.qApp.db
    
    tableEventType    = db.table('EventType')
    tableEvent        = db.table('Event')
    tableActionType   = db.table('ActionType')
    tableAction       = db.table('Action')
    tableOrgStructure = db.table('OrgStructure')
    tablePerson       = db.table('vrbPersonWithSpeciality')
    
    queryTable = tableEvent
    
    queryTable = queryTable.leftJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
    queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))
    
    cond = []
    
    if begDate and begDate.isValid():
        cond.append(tableEvent['execDate'].dateGe(begDate))
    if endDate and endDate.isValid():
        cond.append(tableEvent['execDate'].dateLe(endDate))
    if purposeId:
        cond.append(tableEventType['purpose_id'].eq(purposeId))
    if eventTypeId:
        cond.append(tableEventType['id'].eq(eventTypeId))
    if medicalAidTypeId:
        cond.append(tableEventType['medicalAidType_id'].eq(medicalAidTypeId))
    if orgStructureId:
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        cond.append(tableOrgStructure['id'].inlist(orgStructureIdList))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    
    fields = [tablePerson['code'].alias('personCode'),
              tablePerson['name'].alias('personName'),
              tablePerson['id'].alias('personId'), 
              tableEvent['client_id'].alias('clientId'), 
              tableEvent['id'].alias('eventId'), 
              tableOrgStructure['id'].alias('orgStructureId'), 
              tableActionType['class'].alias('actionClass')
              ]
    
    stmt = db.selectStmt(queryTable, fields, cond)
    return db.query(stmt)

class CReportTreatments(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Обращения по врачам')
        self._queueEventTypeId = forceRef(QtGui.qApp.db.translate('EventType', 'code', etcTimeTable, 'id'))
        self._mapOrgStructureToInfo = {}
        self._mapPersonPlan = {}
        self._mapFullOrgStructureNameToId = {}
        self.resetHelpers()
        
    def resetHelpers(self):
        self._mapOrgStructureToInfo.clear()
        self._mapPersonPlan.clear()
        self._mapFullOrgStructureNameToId.clear()
        
    def getSetupDialog(self, parent):
        result = CReportTreatmentsSetup(parent)
        result.setTitle(self.title())
        return result
        
        
    def getDescription(self, params):
        begDate                = params.get('begDate', None)
        endDate                = params.get('endDate', None)
    
        financeText            = params.get('financeText', '')
        financeId              = params.get('financeId', None)
        
        purposeText            = params.get('purposeText', '')
        purposeId              = params.get('purposeId', None)
        
        eventTypeText          = params.get('eventTypeText', '')
        eventTypeId            = params.get('eventTypeId', None)
        
        medicalAidTypeText     = params.get('medicalAidTypeText', '')
        medicalAidTypeId       = params.get('medicalAidTypeId', None)
        
        orgStructureText       = params.get('orgStructureText', '')
        orgStructureId         = params.get('orgStructureId', None)
        
        personText             = params.get('personText', '')
        personId               = params.get('personId', None)
        
        tariffingText          = params.get('tariffingText', '')
        
        rows = []
        if begDate:
            rows.append(u'Начальная дата периода: %s'%forceString(begDate))
        if endDate:
            rows.append(u'Конечная дата периода: %s'%forceString(endDate))
        if financeId:
            rows.append(u'Тип финансирования: %s' % financeText)
        if purposeId:
            rows.append(u'Назначение: %s' % purposeText)
        if eventTypeId:
            rows.append(u'Тип события: %s' % eventTypeText)
        if medicalAidTypeId:
            rows.append(u'Тип медицинской помощи: %s' % medicalAidTypeText)
        if orgStructureId:
            rows.append(u'Подразделение: %s' % orgStructureText)
        if personId:
            rows.append(u'Врач: %s' % personText)
        if tariffingText:
            rows.append(u'Тарификация: %s' % tariffingText)
            
        return rows
        
    def build(self, params):
        visitsQuery = selectVisitsData(params)
        actionsQuery = selectActionsData(params)
        self.setQueryText(u'\n\n'.join([forceString(visitsQuery.lastQuery()),
                                        forceString(actionsQuery.lastQuery())])
                          )
        self.structInfo(visitsQuery, actionsQuery, params)
        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        tableColumns = [
                        ('%2',
                        [u'№', u''], CReportBase.AlignRight),
                        ('%5',
                        [u'Код врача', u''], CReportBase.AlignLeft),
                        ('%15',
                        [u'ФИО врача', u''], CReportBase.AlignLeft),
                        ('%6',
                        [u'Кол-во пациентов', u''], CReportBase.AlignLeft), 
                        ('%6', 
                        [u'Кол-во обращений', u''], CReportBase.AlignLeft),  
                        ('%6',
                        [u'Визиты', u'План приема'], CReportBase.AlignLeft), 
                        ('%6',
                        [u'', u'План вызовы'], CReportBase.AlignLeft), 
                        ('%6',
                        [u'', u'Прием'], CReportBase.AlignLeft), 
                        ('%6',
                        [u'', u'Вызовы'], CReportBase.AlignLeft), 
                        ('%6',
                        [u'Услуги', u'Статус'], CReportBase.AlignLeft), 
                        ('%6',
                        [u'', u'Диагностика'], CReportBase.AlignLeft), 
                        ('%6',
                        [u'', u'Лечение'], CReportBase.AlignLeft), 
                        ('%6',
                        [u'', u'Прочие'], CReportBase.AlignLeft)
                       ]
        
        table = createTable(cursor, tableColumns)
        
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        
        table.mergeCells(0, 5, 1, 4)
        table.mergeCells(0, 9, 1, 4)
        
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        
        keysList = self._mapFullOrgStructureNameToId.keys()
        keysList.sort()
        numShift = 0
        result = [0]*10
        resClientIdList = []
        resEventIdList  = []
        for key in keysList:
            orgClientIdList = []
            orgEventIdList  = []
            orgStructureResult = [0]*10
            personInfoDict = self._mapOrgStructureToInfo[self._mapFullOrgStructureNameToId[key]]
            i = table.addRow()
            table.setText(i, 1, key, charFormat=boldChars)
            table.mergeCells(i, 0, 1, 13)
            numShift += 1
            for personId, personInfoList in personInfoDict.items():
                i = table.addRow()
                table.setText(i, 0, i-numShift-1)
                personInfoHelper = personInfoList[-1]
                for idx, value in enumerate(personInfoList[:-1]):
                    if idx > 3:
                        orgStructureResult[idx-2] += value
                    table.setText(i, idx+1, value)
                orgClientIdList.extend(personInfoHelper['clientIdList'])
                orgEventIdList.extend(personInfoHelper['eventIdList'])
            for idx, value in enumerate(orgStructureResult):
                result[idx] += value
            orgStructureResult[0] = len(set(orgClientIdList))
            orgStructureResult[1] = len(set(orgEventIdList))
            self.printResult(table, orgStructureResult, boldChars)
            numShift += 1
            resClientIdList.extend(orgClientIdList)
            resEventIdList.extend(orgEventIdList)
        result[0] = len(set(resClientIdList))
        result[1] = len(set(resEventIdList))
        self.printResult(table, result, boldChars, name=u'Всего')
        return doc
        
    def printResult(self, table, result, boldChars, name=u'Итого'):
        i = table.addRow()
        table.setText(i, 0, name, charFormat=boldChars)
        for idx, value in enumerate(result):
            table.setText(i, 3+idx, value, charFormat=boldChars)
        table.mergeCells(i, 0, 1, 3)
        
    def structInfo(self, visitsQuery, actionsQuery, params):
        self.resetHelpers()
        
        self.structVisitsInfo(visitsQuery, params)
        self.structActionsInfo(actionsQuery)
        
        
        
        
        
    def structVisitsInfo(self, query, params):
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        AMB_SCENE_CODE_LIST  = ['1']
        HOME_SCENE_CODE_LIST = ['2', '3']
        while query.next():
            record = query.record()
            
            orgStructureId = forceRef(record.value('orgStructureId'))
            personCode     = forceString(record.value('personCode'))
            personName     = forceString(record.value('personName'))
            clientId       = forceRef(record.value('clientId'))
            personId       = forceRef(record.value('personId'))
            eventId        = forceRef(record.value('eventId'))
            sceneCode      = forceString(record.value('sceneCode'))
            
            if not (sceneCode in AMB_SCENE_CODE_LIST or sceneCode in HOME_SCENE_CODE_LIST):
                continue
                
            if not orgStructureId in self._mapFullOrgStructureNameToId.values():
                if orgStructureId:
                    orgStructureFullName = getOrgStructureFullName(orgStructureId)
                else:
                    orgStructureFullName = u' Не определено'
                self._mapFullOrgStructureNameToId[orgStructureFullName] = orgStructureId
            
            personInfoDict = self._mapOrgStructureToInfo.setdefault(orgStructureId, {})
            personInfoList = personInfoDict.get(personId, None)
            if personInfoList is None:
                personInfoHelper = {'clientIdList':[], 'eventIdList':[]}
                personInfoList = [personCode, personName] + [0]*10 + [personInfoHelper]
                personInfoList[4] = self._getPersonPlan(personId, atcAmbulance, begDate, endDate)
                personInfoList[5] = self._getPersonPlan(personId, atcHome, begDate, endDate)
                personInfoDict[personId] = personInfoList
            
            personInfoHelper = personInfoList[-1]
            if not clientId in personInfoHelper['clientIdList']:
                personInfoList[2] += 1
                personInfoHelper['clientIdList'].append(clientId)
            if not eventId in personInfoHelper['eventIdList']:
                personInfoList[3] += 1
                personInfoHelper['eventIdList'].append(eventId)
            if sceneCode in AMB_SCENE_CODE_LIST:
                personInfoList[6] += 1
            elif sceneCode in HOME_SCENE_CODE_LIST:
                personInfoList[7] += 1
    
    
    def structActionsInfo(self, query):
        while query.next():
            record = query.record()
            
            orgStructureId = forceRef(record.value('orgStructureId'))
            personCode     = forceString(record.value('personCode'))
            personName     = forceString(record.value('personName'))
            clientId       = forceRef(record.value('clientId'))
            personId       = forceRef(record.value('personId'))
            eventId        = forceRef(record.value('eventId'))
            actionClass    = forceInt(record.value('actionClass'))
            
            if not orgStructureId in self._mapFullOrgStructureNameToId.values():
                orgStructureFullName = getOrgStructureFullName(orgStructureId)
                self._mapFullOrgStructureNameToId[orgStructureFullName] = orgStructureId
            
            personInfoDict = self._mapOrgStructureToInfo.setdefault(orgStructureId, {})
            personInfoList = personInfoDict.get(personId, None)
            if personInfoList is None:
                personInfoHelper = {'clientIdList':[], 'eventIdList':[]}
                personInfoList = [personCode, personName] + [0]*10 + [personInfoHelper]
                personInfoDict[personId] = personInfoList
            
            personInfoHelper = personInfoList[-1]
            personInfoList[8+actionClass] += 1
            if not clientId in personInfoHelper['clientIdList']:
                personInfoList[2] += 1
                personInfoHelper['clientIdList'].append(clientId)
            if not eventId in personInfoHelper['eventIdList']:
                personInfoList[3] += 1
                personInfoHelper['eventIdList'].append(eventId)
    
    
    
    
    
    def _getPersonPlan(self, personId, type, begDate, endDate):
        key = (personId, type)
        result = self._mapPersonPlan.get(key, None)
        if result is None:
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
                    tableEvent['execPerson_id'].eq(personId), 
                    tableActionType['code'].eq(type)
                   ]
            
            result = forceInt(db.getSum(queryTable, tableActionPropertyInteger['value'].name(), cond))
            self._mapPersonPlan[key] = result
        return result
            
        
        
        
        
class CReportTreatmentsSetup(QtGui.QDialog, Ui_ReportTreatmentsSetupDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', addNone=True)
        self.cmbPurpose.setTable('rbEventTypePurpose', addNone=True)
        self.cmbMedicalAidType.setTable('rbMedicalAidType', addNone=True)
        self.cmbFinance.setTable('rbFinance', addNone=True)
        
    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbPurpose.setValue(params.get('purposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbMedicalAidType.setValue(params.get('medicalAidTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbTariffing.setCurrentIndex(params.get('tariffing', 0))
        
        
    def params(self):
        params = {}
        
        params['financeId']  = self.cmbFinance.value()
        params['financeText'] = self.cmbFinance.currentText()
        
        params['purposeId'] = self.cmbPurpose.value()
        params['purposeText'] = self.cmbPurpose.currentText()
        
        params['medicalAidTypeId'] = self.cmbMedicalAidType.value()
        params['medicalAidTypeText'] = self.cmbMedicalAidType.currentText()
        
        params['eventTypeId'] = self.cmbEventType.value()
        params['eventTypeText'] = self.cmbEventType.currentText()
        
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['orgStructureText'] = self.cmbOrgStructure.currentText()
        
        params['personId'] = self.cmbPerson.value()
        params['personText'] = self.cmbPerson.currentText()
        
        params['tariffing'] = self.cmbTariffing.currentIndex()
        params['tariffingText'] = self.cmbTariffing.currentText()
        
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()

        return params
        
        
        
        
        
        
        
        
        
