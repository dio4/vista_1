# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.Utils      import forceDouble, forceInt, forceRef, forceString, getVal, formatName

from Orgs.Utils         import getOrgStructureFullName

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportSetupDialog import CReportSetupDialog
from Reports.StatReport1NPUtil import havePermanentAttach


def selectData(begDate, endDate, eventTypeId, sex, ageFrom, ageTo, onlyPermanentAttach, MKBFilter, MKBFrom, MKBTo, onlyPayedEvents, begPayDate, endPayDate, detailPerson, personId, specialityId, orgStructureId, insurerId):
    db = QtGui.qApp.db
    tableEvent      = db.table('Event')
    tableClient     = db.table('Client')
    tableVisit      = db.table('Visit')
    tableActionType = db.table('ActionType')
    tablePerson     = db.table('Person')
    
    cond = []
    
    if begDate:
        cond.append(tableVisit['date'].ge(begDate))
    if endDate:
        cond.append(tableVisit['date'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if MKBFilter:
        tableDiagnostic = db.table('Diagnostic')
        tableDiagnosis = db.table('Diagnosis')
        subQueryTable = tableDiagnosis.leftJoin(tableDiagnostic, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
        subCond = [ tableDiagnostic['event_id'].eq(tableEvent['id']),
                    tableDiagnosis['MKB'].between(MKBFrom, MKBTo)
                  ]
        cond.append(db.existsStmt(subQueryTable, subCond))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    if not detailPerson:
        if personId:
            cond.append(tableVisit['person_id'].eq(personId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if orgStructureId:
        orgStructureIdList = getTheseAndChildrens([orgStructureId])
        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
    if insurerId:
        cond.append('EXISTS (SELECT ClientPolicy.`client_id` FROM ClientPolicy WHERE ClientPolicy.`insurer_id`=%d AND ClientPolicy.`client_id`=Client.`id`)' % insurerId)
    condStr = db.joinAnd(cond)
    
    stmt = '''
SELECT 
    Visit.`person_id`, Visit.`finance_id`, Visit.`payStatus` AS visitPayStatus, 
    Person.`lastName` AS personLastName, Person.`firstName` AS personFirstName, Person.`patrName` AS personPatrName,
    rbSpeciality.`name` AS specialityName,
    rbService.`code` AS serviceCode, 
    OrgStructure.`id` AS orgStructureId,
    OrgStructure.`code` AS orgStructureCode,
    IF(YEAR(FROM_DAYS(DATEDIFF(Visit.`date`, Client.`birthDate`))) < 18, rbService.`childUetDoctor`, rbService.`adultUetDoctor`) AS uetDoctor, 
    IF(YEAR(FROM_DAYS(DATEDIFF(Visit.`date`, Client.`birthDate`))) < 18, rbService.`childUetAverageMedWorker`, rbService.`adultUetAverageMedWorker`) AS uetAverageMedWorker
FROM Visit
INNER JOIN Event ON Event.`id` = Visit.`event_id`
INNER JOIN Client ON Client.`id` = Event.`client_id`
INNER JOIN rbService ON rbService.`id` = Visit.`service_id`
LEFT OUTER JOIN Person ON Person.id = Visit.`person_id`
LEFT OUTER JOIN rbSpeciality ON rbSpeciality.`id` = Person.`speciality_id`
LEFT OUTER JOIN OrgStructure ON OrgStructure.`id` = Person.`orgStructure_id` 
LEFT  JOIN Account_Item      ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                    )
WHERE Visit.deleted=0 AND Event.deleted=0 AND %s
ORDER BY rbService.`code`
    ''' % condStr
    return db.query(stmt)
    

def getTheseAndChildrens(idlist):
    db = QtGui.qApp.db
    table = db.table('OrgStructure')
    result = []
    childrenIdList = db.getIdList(table, 'id', table['parent_id'].inlist(idlist))
    if childrenIdList:
        result = getTheseAndChildrens(childrenIdList)
    result += idlist
    return result 
    
    
def payStatusCheck(payStatus, condFinanceCode):
    if condFinanceCode:
        payCode = (payStatus >> (2*condFinanceCode)) & 3
        if payCode:
            return True
    return False
    
    
class CReportVisitsServiceCutaway(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по УЕТ')
        self._mapOrgStructureToName = {}
        
        self.mainOrgStructureItems = None
        self.printedItemCount = 0
        self.headerCount = 0
        self.headerList  = []
        self.orgStructureResult = {}
        self._mapOrgStructureToFullName = {}
        self.result = []
        self.boldChars = None
        
    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setPayPeriodVisible(True)
        result.setWorkOrganisationVisible(True)
        result.setSexVisible(True)
        result.setAgeVisible(True)
        result.setMKBFilterVisible(True)
        result.setInsurerVisible(True)
        result.setOrgStructureVisible(True)
        result.setSpecialityVisible(True)
        result.setPersonVisible(True)
        result.setFinanceVisible(True)
        result.setTitle(self.title())
        
        self.mainOrgStructureItems = result.cmbOrgStructure.model().getRootItem().items()
        
        return result
        
        
    def build(self, params):
        begDate             = getVal(params, 'begDate', QtCore.QDate())
        endDate             = getVal(params, 'endDate', QtCore.QDate())
        eventTypeId         = getVal(params, 'eventTypeId', None)
        sex                 = params.get('sex', 0)
        ageFrom             = params.get('ageFrom', 0)
        ageTo               = params.get('ageTo', 150)
        onlyPermanentAttach = params.get('onlyPermanentAttach', None)
        MKBFilter           = params.get('MKBFilter', 0)
        MKBFrom             = params.get('MKBFrom', '')
        MKBTo               = params.get('MKBTo', '')
        onlyPayedEvents     = params.get('onlyPayedEvents', False)
        begPayDate          = params.get('begPayDate', QtCore.QDate())
        endPayDate          = params.get('endPayDate', QtCore.QDate())
        detailPerson        = params.get('detailPerson', False)
        personId            = params.get('personId', None)
        specialityId        = params.get('specialityId', None)
        orgStructureId      = params.get('orgStructureId', None)
        insurerId           = params.get('insurerId', None)
        condFinanceId       = params.get('financeId', None)
        condFinanceCode     = params.get('financeCode', '0')
        
        query = selectData(begDate, endDate, eventTypeId, sex, ageFrom, ageTo, onlyPermanentAttach, MKBFilter, MKBFrom, MKBTo, onlyPayedEvents, begPayDate, endPayDate, detailPerson, personId, specialityId, orgStructureId, insurerId)
        
        
        reportData = {}
        self._mapOrgStructureToName.clear()
        self._mapOrgStructureToFullName.clear()
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            orgStructureId         = forceRef(record.value('orgStructureId'))
            orgStructureCode       = forceString(record.value('orgStructureCode'))
            financeId              = forceRef(record.value('finance_id'))
            visitPayStatus         = forceInt(record.value('visitPayStatus'))
            serviceCode            = forceString(record.value('serviceCode'))
            uetDoctor              = forceDouble(record.value('uetDoctor'))
            uetAverageMedWorker    = forceDouble(record.value('uetAverageMedWorker'))
            personName             = formatName(record.value('personLastName'), 
                                                record.value('personFirstName'), 
                                                record.value('personPatrName'))
            specialityName         = forceString(record.value('specialityName'))
            
            
            if condFinanceId:
                if financeId:
                    if condFinanceId != financeId:
                        continue
                else:
                    if not payStatusCheck(visitPayStatus, forceInt(condFinanceCode)):
                        continue
            
            if specialityName:
                personName = personName + ' | ' + specialityName
            
            orgStructureFullName = self.getOrgStructureFullName(orgStructureId)
            
            self._mapOrgStructureToName.setdefault(orgStructureId, orgStructureCode)
            existsData = reportData.get(orgStructureId, None)
            if detailPerson:
                if not existsData:
                    existsData = {}
                    personData = {}
                    amount = 1
                    personData[serviceCode] =  [amount, uetDoctor, uetAverageMedWorker]
                    existsData[personName] = personData
                    reportData[orgStructureId] = existsData
                else:
                    personData = existsData.get(personName, None)
                    if not personData:
                        personData = {}
                        amount = 1
                        personData[serviceCode] =  [amount, uetDoctor, uetAverageMedWorker]
                        existsData[personName] = personData
                    else:
                        existsValue = personData.get(serviceCode, None)
                        if not existsValue:
                            amount = 1
                            personData[serviceCode] =  [amount, uetDoctor, uetAverageMedWorker]
                            existsData[personName] = personData
                        else:
                            existsValue[0] += 1
                            existsValue[1] += uetDoctor
                            existsValue[2] += uetAverageMedWorker
                            personData[serviceCode] = existsValue
                            existsData[personName] = personData
                    reportData[orgStructureId] = existsData
            else:
                if not existsData:
                    existsData = {}
                    amount = 1
                    existsData[serviceCode] =  [amount, uetDoctor, uetAverageMedWorker]
                    reportData[orgStructureId] = existsData
                else:
                    existsValue = existsData.get(serviceCode, None)
                    if not existsValue:
                        amount = 1
                        existsData[serviceCode] = [amount, uetDoctor, uetAverageMedWorker]
                    else:
                        existsValue[0] += 1
                        existsValue[1] += uetDoctor
                        existsValue[2] += uetAverageMedWorker
                        existsData[serviceCode] = existsValue
                    reportData[orgStructureId] = existsData
            
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        tableColumns = [
            ( '10%', [u'№ п/п'], CReportBase.AlignRight),
            ( '30%', [u'Код профиля'], CReportBase.AlignLeft),
            ( '15%', [u'Количество визитов'], CReportBase.AlignRight),
            ( '15%', [u'УЕТ врача'], CReportBase.AlignRight),
            ( '15%', [u'УЕТ ср.мед.персонала'], CReportBase.AlignRight)
        ]
        
        table = createTable(cursor, tableColumns)
        
        self.boldChars = QtGui.QTextCharFormat()
        self.boldChars.setFontWeight(QtGui.QFont.Bold)
        
        self.printedItemCount = 0
        self.orgStructureResult = {}
        self.result = [0, 0, 0]
        self.headerCount = 0
        self.headerList  = []
        
        result = self.printOrgStructureListValues(detailPerson, self.mainOrgStructureItems, reportData, table)
        i = table.addRow()
        table.setText(i, 0, u'Итого', charFormat=self.boldChars)
        self.headerList.append(i)
        self.setResult(i, result, table)
        
        for headerRow in self.headerList:
            table.mergeCells(headerRow, 0, 1, 2)

        return doc

    def getOrgStructureFullName(self, orgStructureId):
        orgStructureFullName = self._mapOrgStructureToFullName.get(orgStructureId, None)
        if not orgStructureFullName:
            orgStructureFullName = getOrgStructureFullName(orgStructureId)
            self._mapOrgStructureToFullName[orgStructureId] = orgStructureFullName
        return orgStructureFullName

    def checkNeedPrint(self, checkOrgStructureIdList, existsOrgStructureIdList):
        return bool( set(checkOrgStructureIdList) & set(existsOrgStructureIdList) )
        
    def printOrgStructureListValues(self, detailPerson, orgStructureItemList, 
                                    reportData, table, orgStructureNameShift=0):
        result = [0, 0, 0]
        localResult = [0, 0, 0]
        if bool(orgStructureItemList):
            for orgStructureItem in orgStructureItemList:
                if self.checkNeedPrint( orgStructureItem.getItemIdList(), reportData.keys() ):
                    orgStructureId = orgStructureItem.id()
                    orgStructureName = self.getOrgStructureFullName(orgStructureId)
                    i = table.addRow()
                    table.setText(i, 1, (' '*orgStructureNameShift)+orgStructureName, charFormat=self.boldChars)
                    self.headerList.append(i)
                    self.headerCount += 1
                    orgStructureResult = self.printOrgStructureValues(detailPerson, 
                                                                      orgStructureId, 
                                                                      reportData, 
                                                                      table)
                    
                    childrenResult = self.printOrgStructureListValues(detailPerson, 
                                                     orgStructureItem.items(), 
                                                     reportData, 
                                                     table, 
                                                     orgStructureNameShift+8)
                                                     
                    localResult = map(lambda x, y: x+y, childrenResult, orgStructureResult)
                    result = map(lambda x, y: x+y, result, localResult)
                    
                    self.setResult(i, localResult, table)
                    
        return result
        
    def printOrgStructureValues(self, detailPerson, orgStructureId, reportData, table):
        orgStructureResult = [0, 0, 0]
        if detailPerson:
            persons = reportData.get(orgStructureId, {})
            personsKeys = persons.keys()
            personsKeys.sort()
            for personKey in personsKeys:
                personResult = [0, 0, 0]
                i = table.addRow()
                table.setText(i, 0, personKey, charFormat=self.boldChars)
                currentPersonRow = i
                self.headerList.append(i)
                self.headerCount += 1
                existsData = persons.get(personKey, {})
                existsDataKeys = existsData.keys()
                existsDataKeys.sort()
                for existsDataKey in existsDataKeys:
                    i = table.addRow()
                    table.setText(i, 0, i-self.headerCount)
                    column = 1
                    table.setText(i, column, existsDataKey)
                    column += 1
                    values = existsData.get(existsDataKey)
                    for value in values:
                        table.setText(i, column, value)
                        personResult[column-2] += value
                        column += 1
                orgStructureResult = map(lambda x, y: x+y, personResult, orgStructureResult)
                self.setResult(currentPersonRow, personResult, table)
        else:
            existsData = reportData.get(orgStructureId, {})
            existsDataKeys = existsData.keys()
            existsDataKeys.sort()
            for existsDataKey in existsDataKeys:
                i = table.addRow()
                table.setText(i, 0, i-self.headerCount)
                column = 1
                table.setText(i, column, existsDataKey)
                column += 1
                values = existsData.get(existsDataKey)
                for value in values:
                    table.setText(i, column, value)
                    orgStructureResult[column-2] += value
                    column += 1
            
        return orgStructureResult
            
            
    def setResult(self, row, resultValues, table):
        for idx, value in enumerate(resultValues):
            table.setText(row, idx+2, value, charFormat=self.boldChars)
            
        
