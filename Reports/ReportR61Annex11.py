# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 31.01.2013
purpose: issue 652
@author: atronah
"""

from PyQt4 import QtCore, QtGui

from library.Utils              import forceDouble, forceInt, forceRef, forceString, forceStringEx
from Orgs.Utils                 import getOrgStructureDescendants, getOrganisationInfo, getOrganisationMainStaff
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog


def selectData(params):
    db = QtGui.qApp.db
    
    begDate = params.get('begDate', QtCore.QDate.currentDate())
    endDate = params.get('endDate', QtCore.QDate.currentDate())
    eventTypeId = params.get('eventTypeId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    
    cond = []
    if begDate and begDate.isValid():
        cond.append('DATE(Visit.date) >= DATE(\'%s\')' % forceString(begDate.toString(QtCore.Qt.ISODate)))
    if endDate and endDate.isValid():
        cond.append('DATE(Visit.date) <= DATE(\'%s\')' % forceString(endDate.toString(QtCore.Qt.ISODate)))
    if eventTypeId:
        cond.append('EventType.id = %d' % forceRef(eventTypeId))
    if eventPurposeId:
        cond.append('EventType.purpose_id = %d' % forceRef(eventPurposeId))
    if orgStructureId:
        tableOrgStructure = db.table('OrgStructure')
        orgStructureIdList = getOrgStructureDescendants(orgStructureId) 
        cond.append(tableOrgStructure['id'].inlist(orgStructureIdList))
    
    expenseServiceItemRecordList = db.getRecordList('rbExpenseServiceItem', 'id, code', 'code in (\'1\', \'2\', \'3\', \'5\', \'6\')')
    expenseServiceCodeToIdMap = {'1' : 0, '2': 0, '3': 0, '5' : 0, '6': 0}
    for expenseServiceItemRecord in expenseServiceItemRecordList:
        expenseServiceItemCode = forceString(expenseServiceItemRecord.value('code'))
        expenseServiceCodeToIdMap[expenseServiceItemCode] = forceRef(expenseServiceItemRecord.value('id'))
    
    queryParamsDict = {'wagesId' : expenseServiceCodeToIdMap['1'],
                       'additionalPaymentsId' : expenseServiceCodeToIdMap['6'],
                       'drugsId' : expenseServiceCodeToIdMap['2'],
                       'softInventoryId' : expenseServiceCodeToIdMap['3'],
                       'overheadId' : expenseServiceCodeToIdMap['5'],
                       'cond' : db.joinAnd(cond)}
    
    stmt = """
    SELECT 
        OrgStructure.id                AS orgStructureId,
        OrgStructure.infisCode        AS orgStructureCode,
        rbService.name                AS specialityName,
        rbService.code                AS serviceCode,
        COUNT(DISTINCT Visit.id)        AS visitCount,
        COUNT(DISTINCT Event.id)        AS eventCount,
        Tariff.price                    AS tariffPrice,
        WagesPart.percent                AS wagesPercent,
        AdditionalPaymentsPart.percent    AS additionalPaymentsPercent,
        DrugsPart.percent                AS drugsPercent,
        SoftInventoryPart.percent        AS softInventoryPercent,
        OverheadPart.percent            AS overheadPercent
    FROM
        Visit
        
        LEFT JOIN rbService ON rbService.id = Visit.service_id
        
        LEFT JOIN Person ON Person.id = Visit.person_id
        LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
        
        LEFT JOIN Event ON Event.id = Visit.event_id
        LEFT JOIN EventType ON EventType.id = Event.eventType_id
        
        LEFT JOIN Contract ON Contract.id = Event.contract_id
        LEFT JOIN Contract_Tariff AS Tariff ON Tariff.master_id = Contract.id 
                                                AND Tariff.service_id = Visit.service_id
        
        LEFT JOIN Contract_CompositionExpense AS WagesPart ON WagesPart.master_id = Tariff.id
                                                                AND WagesPart.rbTable_id = %(wagesId)d
        LEFT JOIN Contract_CompositionExpense AS AdditionalPaymentsPart ON AdditionalPaymentsPart.master_id = Tariff.id
                                                                            AND AdditionalPaymentsPart.rbTable_id = %(additionalPaymentsId)d
        LEFT JOIN Contract_CompositionExpense AS DrugsPart ON DrugsPart.master_id = Tariff.id
                                                                AND DrugsPart.rbTable_id = %(drugsId)d
        LEFT JOIN Contract_CompositionExpense AS SoftInventoryPart ON SoftInventoryPart.master_id = Tariff.id
                                                                        AND SoftInventoryPart.rbTable_id = %(softInventoryId)d
        LEFT JOIN Contract_CompositionExpense AS OverheadPart ON OverheadPart.master_id = Tariff.id
                                                                 AND OverheadPart.rbTable_id = %(overheadId)d
    WHERE
        %(cond)s 
    GROUP BY OrgStructure.id, rbService.id
    ORDER BY OrgStructure.infisCode, rbService.name
    """ % queryParamsDict
    
    return db.query(stmt)



def getDataFromFile(params, parentWidget = None):
    import os
    
    if parentWidget is None:
        parentWidget = QtGui.qApp.mainWindow
    
    
    dataFileName = forceString(params.get('dataFileName', None))
    if not dataFileName:
        QtGui.QMessageBox.warning(parentWidget, u'Ошибка', u'Не указан файл исходных данных отчета', buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
    elif not os.path.exists(dataFileName):
        QtGui.QMessageBox.warning(parentWidget, u'Ошибка', u'Указанный файл исходных данных отчета\nне существует', buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
    elif not os.path.isfile(dataFileName):
        QtGui.QMessageBox.warning(parentWidget, u'Ошибка', u'Указанный источник исходных данных отчета\nне является файлом', buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
    else:
        if os.path.splitext(dataFileName)[1].lower() == '.dbf':
            return getDataFromDbfFile(parentWidget, dataFileName)
        elif os.path.splitext(dataFileName)[1].lower() == '.xml':
            return getDataFromXmlFile(parentWidget, dataFileName)
    return {}, '_____________________________________________'


def getDataFromDbfFile(parentWidget, fileName):
    from library.dbfpy.dbf import Dbf
    
    reportDataByNumbers = {}
    
    dbf = Dbf(fileName, readOnly=True, encoding='cp866', enableFieldNameDups=True)
    
    unexistsFields = []
    for needField in ['NREESTR', 'NSVOD', 'KODLPU', 'KSPEC', 'NSCHT', 'STOIM', 'ZPL', 'DOPL', 'MED', 'M_INV', 'NAKL']:
        if needField not in dbf.fieldNames:
            unexistsFields.append(needField)
    if unexistsFields:
        QtGui.QMessageBox.warning(parentWidget, u'Ошибка', u'В указанном файле исходных данных отчета\n отсутсвтуют поля:\n%s' % ('\n'.join(unexistsFields)), buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
        return reportDataByNumbers, '_____________________________________________'
        
    rows = dbf.recordCount
    row = 0

    nr    = u'%05d' % forceInt(dbf[row]['NREESTR'])
    table  = QtGui.qApp.db.table('Organisation')
    platrec = QtGui.qApp.db.getRecordEx(table, 'shortName', 'infisCode LIKE \'61%%%s\' and deleted = 0' % nr[:2])
    plat = forceString(platrec.value('shortName'))
            
    specialityNameCashe = {}
    while row < rows:
        dbfRecord = dbf[row]
        
        nsvod = forceString(dbfRecord['NSVOD'])
        
        reportData = reportDataByNumbers.setdefault(nsvod, {})
        orgStructureCode = forceStringEx(dbfRecord['KODLPU'])
        
        serviceCode = forceString(dbfRecord['KSPEC'])
        if not specialityNameCashe.has_key(serviceCode):
            rbSpecialityTable = QtGui.qApp.db.table('rbSpeciality')
            specialityNameCashe[serviceCode] = forceString(QtGui.qApp.db.translate(rbSpecialityTable, rbSpecialityTable['federalCode'], serviceCode, rbSpecialityTable['OKSOName']))
        specialityName = specialityNameCashe[serviceCode]
        
        visitCount = 1
                
        nscht = forceInt(dbfRecord['NSCHT'])
        
        tariffPrice = forceDouble(dbfRecord['STOIM'])
        
        sum = visitCount * tariffPrice

        wages = forceDouble(dbfRecord['ZPL']) #1
        
        additionalPayments = forceDouble(dbfRecord['DOPL'])#5
        
        drugs = forceDouble(dbfRecord['MED'])#2
        
        softInventory = forceDouble(dbfRecord['M_INV'])#3
        
        overhead =  forceDouble(dbfRecord['NAKL'])#4
        
        orgStructureData = reportData.setdefault(serviceCode, {})
        serviceData = orgStructureData.setdefault(serviceCode, {'orgStructureCode': orgStructureCode,
                                                                'serviceCode' : serviceCode,
                                                                'specialityName' : specialityName,
                                                                'visitCount' : 0,
                                                                'eventCount' : 0,
                                                                'sum' : 0.0,
                                                                'wages' : 0.0,
                                                                'additionalPayments' : 0.0,
                                                                'drugs' : 0.0,
                                                                'softInventory' : 0.0,
                                                                'overhead' : 0.0,
                                                                'nschtValueSet' : []
                                                                })
        serviceData['visitCount'] += visitCount
        if nscht not in serviceData['nschtValueSet']:
            serviceData['nschtValueSet'].append(nscht)
            serviceData['eventCount'] += 1
        serviceData['sum'] += sum
        serviceData['wages'] += wages
        serviceData['additionalPayments'] += additionalPayments
        serviceData['drugs'] += drugs
        serviceData['softInventory'] += softInventory
        serviceData['overhead'] += overhead
        row += 1
    
    dbf.close()
    return reportDataByNumbers, plat
        

def getDataFromXmlFile(parentWidget, fileName):
    rootElementName = 'ZL_LIST'
    accountElementName = 'SCHET'
    recordElementName = 'ZAP'
    platElementName = 'PLAT'
    nsvodElementName = 'NSVOD'
    
    
    def moveToNearestOfElements(reader, elementNames, stopElements):
        if isinstance(elementNames, basestring):
            elementNames = [elementNames]
        
        while reader.readNext() not in [QtCore.QXmlStreamReader.Invalid, QtCore.QXmlStreamReader.EndDocument]:
            if reader.isEndElement() and forceString(reader.name()) in stopElements:
                return False
            if reader.isStartElement() and forceString(reader.name()) in elementNames:
                stopElements.append(forceString(reader.name()))
                return True
        return False
    #end moveToNearestElement
    
    def moveAfterEndElement(reader, elementNames, stopElements):
        if isinstance(elementNames, basestring):
            elementNames = [elementNames]
        
        if not reader.isEndElement() or forceString(reader.name()) not in stopElements:
            while reader.readNext() not in [QtCore.QXmlStreamReader.Invalid, QtCore.QXmlStreamReader.EndDocument]:
                if reader.isEndElement() and forceString(reader.name()) in stopElements:
                    break
        
        if reader.isEndElement() and forceString(reader.name()) in elementNames:
            stopElements.remove(forceString(reader.name()))
            reader.readNext()
            return True
            
        return False
    #end moveAfterEndElement
    
    
    def readElementText(reader):
        if hasattr(QtCore.QXmlStreamReader, 'SkipChildElements'):
            return reader.readElementText(QtCore.QXmlStreamReader.SkipChildElements)
        else:
            return reader.readElementText()
        
        
    def parseAccount(reader, accountInfo, stopElements):
        while moveToNearestOfElements(reader, platElementName, stopElements):
            insurrerInfis = forceString(readElementText(reader))
            tableOrganisation  = QtGui.qApp.db.table('Organisation')
            record = QtGui.qApp.db.getRecordEx(tableOrganisation, 'shortName', 'infisCode LIKE \'%s%%\' and deleted = 0' % insurrerInfis)
            infisName = forceString(record.value('shortName')) if record else ''
            accountInfo[platElementName] = infisName
            if not moveAfterEndElement(reader, platElementName, stopElements):
                return False
        return True
    #end parseAccount
    
    def parseRecord(reader, reportDataByNumbers, stopElements, specialityNameCashe=None):
        if not specialityNameCashe:
            specialityNameCashe = {}
        eventElementName = 'SLUCH'
        serviceElementName = 'USL'
        serviceTypeElementName = 'USL_OK'
        serviceCodeElementName = 'CODE_USL' 
        serviceSumElementName = 'SUMV_USL'    
        serviceAddPaymentsElementName = 'DOPL'   
        serviceWagesElementName = 'ZPL'
        serviceDrugsElementName = 'MED'
        serviceSoftInventoryElementName = 'M_INV'
        serviceOverheadElementName = 'NAKL'
        orgStructureCodeElementName = 'KODLPU'
        idCaseElementName = 'IDCASE'
        
        #перебор всех SLUCH в текущем ZAP
        while moveToNearestOfElements(reader, eventElementName, stopElements):
            uslOk = None
            nsvod = '____'
            orgStructureCode = None
            idCase = None
            
            #Временный словарь с данными для отчета
            #Необходим для того, чтобы не писать в основной словарь данные по случаям с USL_OK != 3 
            #(если в xml тег USL_OK задан после USL тегов в SLUCH)
            dataByServiceCode = {}

            eventElements = [idCaseElementName,
                            serviceTypeElementName, 
                            nsvodElementName,
                            orgStructureCodeElementName,
                            serviceElementName]
            
            #просмотр данных по случаю
            while moveToNearestOfElements(reader, eventElements, stopElements):
                currentEventElementName = forceString(reader.name()) 
                if currentEventElementName == idCaseElementName:
                    idCase = forceRef(readElementText(reader))
                    
                elif currentEventElementName == serviceTypeElementName:
                    uslOk = forceString(readElementText(reader))
                    if uslOk != '3':
                        if not moveAfterEndElement(reader, currentEventElementName, stopElements):
                            return False
                        break
                
                elif currentEventElementName == nsvodElementName:
                    nsvod = forceString(readElementText(reader))
                
                elif currentEventElementName == orgStructureCodeElementName:
                    orgStructureCode = forceString(readElementText(reader))
                
                elif currentEventElementName == serviceElementName:
                    serviceCode = None
                    serviceSum = 0.0
                    serviceAddPayments = 0.0
                    serviceWages = 0.0
                    serviceDrugs = 0.0
                    serviceSoftInventory = 0.0
                    serviceOverhead = 0.0
                    
                    serviceElements = [serviceCodeElementName,
                                       serviceSumElementName, 
                                       serviceAddPaymentsElementName,
                                       serviceWagesElementName,
                                       serviceDrugsElementName,
                                       serviceSoftInventoryElementName,
                                       serviceOverheadElementName]
                    #перебор всех данных по текущей услуге/посещению
                    while moveToNearestOfElements(reader, serviceElements, stopElements):
                        currentServiceElementName = forceString(reader.name())
                        if currentServiceElementName == serviceCodeElementName:
                            serviceCode = forceString(readElementText(reader))
                        elif currentServiceElementName == serviceSumElementName:
                            serviceSum = forceDouble(readElementText(reader))
                        elif currentServiceElementName == serviceAddPaymentsElementName:
                            serviceAddPayments = forceDouble(readElementText(reader))
                        elif currentServiceElementName == serviceWagesElementName:
                            serviceWages = forceDouble(readElementText(reader))
                        elif currentServiceElementName == serviceDrugsElementName:
                            serviceDrugs = forceDouble(readElementText(reader))
                        elif currentServiceElementName == serviceSoftInventoryElementName:
                            serviceSoftInventory = forceDouble(readElementText(reader))
                        elif currentServiceElementName == serviceOverheadElementName:
                            serviceOverhead = forceDouble(readElementText(reader))
                        if not moveAfterEndElement(reader, currentServiceElementName, stopElements):
                            return False
                    #end while moveToNearestOfElements(reader, serviceElements, stopElements):
                    
                    if serviceCode:
                        serviceData = dataByServiceCode.setdefault(serviceCode, {'serviceCode' : serviceCode,
                                                                                'visitCount' : 0,
                                                                                'sum' : 0.0,
                                                                                'wages' : 0.0,
                                                                                'additionalPayments' : 0.0,
                                                                                'drugs' : 0.0,
                                                                                'softInventory' : 0.0,
                                                                                'overhead' : 0.0
                                                                                })
                        
                        serviceData['visitCount'] += 1
                        serviceData['sum'] += serviceSum
                        serviceData['wages'] += serviceWages
                        serviceData['additionalPayments'] += serviceAddPayments
                        serviceData['drugs'] += serviceDrugs
                        serviceData['softInventory'] += serviceSoftInventory
                        serviceData['overhead'] += serviceOverhead
                    
                if not moveAfterEndElement(reader, currentEventElementName, stopElements):
                    return False
            #end while moveToNearestOfElements(reader, eventElements, stopElements)
            #конец просмотра случая
            
            #обработывать только случаи с USL_OK = 3
            if uslOk == '3':
                reportData = reportDataByNumbers.setdefault(nsvod, {})
                
                #Сохранение данных по всем услугам из текущего случая в конечный словарь reportData
                for serviceCode in dataByServiceCode.keys():
                    if not specialityNameCashe.has_key(serviceCode):
                        rbSpecialityTable = QtGui.qApp.db.table('rbSpeciality')
                        specialityNameCashe[serviceCode] = forceString(QtGui.qApp.db.translate(rbSpecialityTable, rbSpecialityTable['federalCode'], serviceCode, rbSpecialityTable['OKSOName']))
                    specialityName = specialityNameCashe[serviceCode]
                    orgStructureData = reportData.setdefault(serviceCode, {})
                    serviceData = orgStructureData.setdefault(serviceCode, {'orgStructureCode': orgStructureCode,
                                                                            'serviceCode' : serviceCode,
                                                                            'specialityName' : specialityName,
                                                                            'visitCount' : 0,
                                                                            'eventCount' : 0,
                                                                            'sum' : 0.0,
                                                                            'wages' : 0.0,
                                                                            'additionalPayments' : 0.0,
                                                                            'drugs' : 0.0,
                                                                            'softInventory' : 0.0,
                                                                            'overhead' : 0.0,
                                                                            'idCaseValueSet' : []
                                                                            })
                    
                    serviceData['visitCount'] += dataByServiceCode[serviceCode]['visitCount']
                    if idCase not in serviceData['idCaseValueSet']:
                        serviceData['idCaseValueSet'].append(idCase)
                        serviceData['eventCount'] += 1
                    serviceData['sum'] += dataByServiceCode[serviceCode]['sum']
                    serviceData['wages'] += dataByServiceCode[serviceCode]['wages']
                    serviceData['additionalPayments'] += dataByServiceCode[serviceCode]['additionalPayments']
                    serviceData['drugs'] += dataByServiceCode[serviceCode]['drugs']
                    serviceData['softInventory'] += dataByServiceCode[serviceCode]['softInventory']
                    serviceData['overhead'] += dataByServiceCode[serviceCode]['overhead']
            
            if not moveAfterEndElement(reader, eventElementName, stopElements):
                return False
        #end while moveToNearestOfElements(reader, eventElementName, stopElements):
        #конец перебора всех случаев в записи
        
        return True
    
    #end parseRecord
    
    
    
    
    reportDataByNumbers = {}
    accountInfo = {}
    specialityNameCashe = {}
    
    reportFile = QtCore.QFile(fileName)
    
    if not reportFile.open(QtCore.QIODevice.ReadOnly):
        QtGui.QMessageBox.warning(parentWidget, u'Ошибка', u'Не удалось открыть файл\n%s\n(%s)' % (reportFile.fileName(), reportFile.errorString()), buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
        return reportDataByNumbers, accountInfo.get(platElementName, '')
    
    reader = QtCore.QXmlStreamReader()
    reader.setDevice(reportFile)
    
    stopElements = []
    
    if moveToNearestOfElements(reader, rootElementName, stopElements):
        reportElements = [accountElementName, recordElementName]
        while moveToNearestOfElements(reader, reportElements, stopElements):
            currentReportElementName = forceString(reader.name())
            if currentReportElementName == accountElementName:
                if not parseAccount(reader, accountInfo, stopElements):
                    break
            elif currentReportElementName == recordElementName:
                if not parseRecord(reader, reportDataByNumbers, stopElements, specialityNameCashe):
                    break
            if not moveAfterEndElement(reader, currentReportElementName, stopElements):
                return False
            
    return reportDataByNumbers, accountInfo.get(platElementName, '')
        
        


def getDataFromDatabase(params):
    query = selectData(params)
    reportDataByNumbers = {}
    row = 0
    #TODO get plat from DB
    plat = u'_____________________________________________'    
    #TODO get nsvod from account.date
    nsvod = u'_____' #300 + pyDate(accDate).month

    while query.next():
        reportData = reportDataByNumbers.setdefault(nsvod, {})
        record = query.record()
        orgStructureCode = forceString(record.value('orgStructureCode'))
        specialityName = forceString(record.value('specialityName'))
        serviceCode = forceString(record.value('serviceCode'))
        visitCount = forceInt(record.value('visitCount'))
        eventCount = forceInt(record.value('eventCount'))
        tariffPrice = forceDouble(record.value('tariffPrice'))
        sum = tariffPrice * visitCount
        
        wagesPercent = forceDouble(record.value('wagesPercent'))
        wages = sum * wagesPercent / 100.
        
        additionalPaymentsPercent = forceDouble(record.value('additionalPaymentsPercent'))
        additionalPayments = sum * additionalPaymentsPercent / 100.
        
        drugsPercent = forceDouble(record.value('drugsPercent'))
        drugs = sum * drugsPercent / 100.
        
        softInventoryPercent = forceDouble(record.value('softInventoryPercent'))
        softInventory = sum * softInventoryPercent /100.
        
        overheadPercent = forceDouble(record.value('overheadPercent'))
        overhead =  sum * overheadPercent / 100.
        
        orgStructureData = reportData.setdefault(serviceCode, {})
        serviceData = orgStructureData.setdefault(serviceCode, {'orgStructureCode': orgStructureCode,
                                                                'serviceCode' : serviceCode,
                                                                'specialityName' : specialityName,
                                                                'visitCount' : 0,
                                                                'eventCount' : 0,
                                                                'sum' : 0.0,
                                                                'wages' : 0.0,
                                                                'additionalPayments' : 0.0,
                                                                'drugs' : 0.0,
                                                                'softInventory' : 0.0,
                                                                'overhead' : 0.0
                                                                })
        serviceData['visitCount'] += visitCount
        serviceData['eventCount'] += eventCount
        serviceData['sum'] += sum
        serviceData['wages'] = wages
        serviceData['additionalPayments'] += additionalPayments
        serviceData['drugs'] += drugs
        serviceData['softInventory'] += softInventory
        serviceData['overhead'] += overhead

        row += 1
    
    return reportDataByNumbers, plat



class CReportR61Annex11(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Приложение 11')
    
    def getSetupDialog(self, parent):
        setupDialog = CReportSetupDialog(parent)
        setupDialog.setOnlyNotPayedVisible(False)
        setupDialog.setOnlyEmployeeVisible(False)
        setupDialog.setGroupByClients(False)
        setupDialog.setOnlyPermanentAttachVisible(False)
        setupDialog.setContractVisible(False)
        setupDialog.setFinanceVisible(False)
        setupDialog.setPersonVisible(False)
        setupDialog.setPersonWithoutDetailCheckboxVisible(False)
        setupDialog.setSpecialityVisible(False)
        setupDialog.setInsurerVisible(False)
        setupDialog.setStageVisible(False)
        setupDialog.setPayPeriodVisible(False)
        setupDialog.setWorkTypeVisible(False)
        setupDialog.setOwnershipVisible(False)
        setupDialog.setWorkOrganisationVisible(False)
        setupDialog.setSexVisible(False)
        setupDialog.setDiagnosisType(False)
        setupDialog.setAgeVisible(False)
        setupDialog.setActionTypeVisible(False)
        setupDialog.setMKBFilterVisible(False)
        
        setupDialog.setEventTypeVisible(True)
        setupDialog.setOrgStructureVisible(True)
        setupDialog.setEventPurposeVisible(True)
        setupDialog.setSourceFileVisible(True)
        
        setupDialog.setSourceFileFilter(u'XML Files (*.xml);;DBF Files (*.dbf)')
        
        setupDialog.resize(setupDialog.sizeHint())
        
        return setupDialog
    
    
    def build(self, params):
        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        
        reportDataByNumbers, plat = getDataFromFile(params) if params.has_key('dataFileName') else getDataFromDatabase(params)
        
        isFirstReport = True
        for nsvod, reportData in reportDataByNumbers.items():
            
            if not isFirstReport:
                pageBreakBlockFormat = QtGui.QTextBlockFormat()
                pageBreakBlockFormat.setPageBreakPolicy(QtGui.QTextFormat.PageBreak_AlwaysBefore)
                cursor.insertBlock(pageBreakBlockFormat)
                cursor.movePosition(QtGui.QTextCursor.End)
            
            invisibleTableFormat = QtGui.QTextTableFormat()
            invisibleTableFormat.setBorder(0)
            
            invisibleTableFormat.setAlignment(QtCore.Qt.AlignRight)
            table = cursor.insertTable(1, 1, invisibleTableFormat)
            subCursor = table.cellAt(0, 0).firstCursorPosition()
            subCursor.insertBlock(CReportBase.AlignCenter)
            subCursor.insertText(u'Приложение 11\n', CReportBase.TableBody)
            cursor.movePosition(QtGui.QTextCursor.End)
            
            invisibleTableFormat.setAlignment(QtCore.Qt.AlignLeft)
            oldTableWidth = invisibleTableFormat.width()
            invisibleTableFormat.setWidth(QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 40))
            table = cursor.insertTable(1, 1, invisibleTableFormat)
            subCursor = table.cellAt(0, 0).firstCursorPosition()
            subCursor.insertBlock(CReportBase.AlignCenter)
            orgInfo = getOrganisationInfo(QtGui.qApp.currentOrgId())
            subCursor.insertText(u'Наименование МО %s\n' % orgInfo['fullName'], CReportBase.ReportBody)
            subCursor.insertText(u' код %s \n' % orgInfo['infisCode'], CReportBase.ReportBody)
            subCursor.insertText(u'штамп   медицинской организации\n', CReportBase.ReportBody)
            invisibleTableFormat.setWidth(oldTableWidth)
            cursor.movePosition(QtGui.QTextCursor.End)
            
            cursor.insertBlock(CReportBase.AlignCenter)
            begDate = params.get('begDate', QtCore.QDate.currentDate())
            endDate = params.get('endDate', QtCore.QDate.currentDate())
            intervalText = u''
            if begDate and begDate.isValid():
                intervalText += unicode(begDate.toString('MMMM yyyy')).lower()
                #intervalText += u'c %s' % formatDate(begDate)
            else:
                intervalText += u'__________'
            #if endDate and endDate.isValid():
            #    intervalText += u' по %s' % formatDate(endDate)
            #else:
            #    intervalText += '__________'
            if (begDate and begDate.isValid()) or (endDate and endDate.isValid()):
                pass
                #intervalText = u'период %s' % intervalText
            else:
                intervalText = u'_____________________ 200__ г.'
            
            
         
            cursor.insertText(u'Сводный счет № %s\n' % nsvod, CReportBase.ReportBody)
            cursor.insertText(u'за оказанные медицинские услуги по поликлинике, параклинические услуги,\n', CReportBase.ReportBody)
            cursor.insertText(u'отдельные врачебные манипуляции, стоматологические услуги \n', CReportBase.ReportBody)
            cursor.insertText(u'за %s \n' % intervalText, CReportBase.ReportBody)
            
            invisibleTableFormat.setAlignment(QtCore.Qt.AlignLeft)
            table = cursor.insertTable(1, 1, invisibleTableFormat)
            subCursor = table.cellAt(0, 0).firstCursorPosition()
            subCursor.insertBlock(CReportBase.AlignCenter)
            subCursor.insertText(u' %s \n' % plat, CReportBase.ReportBody)
            subCursor.insertText(u'(наименование плательщика)\n', CReportBase.ReportBody)
            cursor.movePosition(QtGui.QTextCursor.End)
            
            tableColumns = [
                            ('?5', [u'Код подразделения', '', '', '2'], CReportBase.AlignLeft),
                            ('?5', [u'Наименование врачебной специальности', '', '', '3'], CReportBase.AlignCenter),
                            ('?5', [u'Код посещения, услуги', '', '', '4'], CReportBase.AlignCenter),
                            ('?5', [u'Кол-во посещений', '', '', '5'], CReportBase.AlignCenter),
                            ('?5', [u'Кол-во услуг', '', '', '6'], CReportBase.AlignCenter),
                            ('?5', [u'Кол-во УЕТ', '', '', '7'], CReportBase.AlignCenter),
                            ('?5', [u'Количество индивид. счетов в т.ч. по стоматологии', '', '', '8'], CReportBase.AlignCenter),
                            ('?5', [u'Сумма счета за мед. помощь (руб.)', u'Всего', '', '9'], CReportBase.AlignCenter),
                            ('?5', [u'', u'В т.ч.', u'Заработная плата с начислениями', '10'], CReportBase.AlignCenter),
                            ('?5', [u'', '', u'Из них фин.обеспеч. доп.выплат работникам участковой службы и мед.перс.ФА.Пов', '11'], CReportBase.AlignCenter),
                            ('?5', [u'', '', u'Медикаменты', '12'], CReportBase.AlignCenter),
                            ('?5', [u'', '', u'Мелкий инвентарь', '13'], CReportBase.AlignCenter),
                            ('?5', [u'', '', u'Накладные расходы', '14'], CReportBase.AlignCenter)
                            ]
            
            table = createTable(cursor, tableColumns, charFormat = CReportBase.ReportBody)
            
            table.mergeCells(0, 0, 3, 1)    # Код подразделения
            table.mergeCells(0, 1, 3, 1)    # Наименование врачебной специальности
            table.mergeCells(0, 2, 3, 1)    # Код посещения, услуги
            table.mergeCells(0, 3, 3, 1)    # Кол-во посещений
            table.mergeCells(0, 4, 3, 1)    # Кол-во услуг
            table.mergeCells(0, 5, 3, 1)    # Кол-во УЕТ
            table.mergeCells(0, 6, 3, 1)    # Количество индивид. счастов в т.ч. по стоматологии
            table.mergeCells(0, 7, 1, 6)    # Сумма счета за мед. помощь (руб.)
            table.mergeCells(1, 7, 2, 1)    #    Всего
            table.mergeCells(1, 8, 1, 5)    #    В т.ч.
            
            #i = table.addRow()
               
            cursor.setCharFormat(CReportBase.TableBody)
            totalVisitCount = 0
            totalEventCount = 0
            totalSum = 0.0
            totalWages = 0.0
            totalAdditionalPayments = 0.0
            totalDrugs = 0.0
            totalSoftInventory = 0.0
            totalOverhead = 0.0
            codes0 = reportData.keys()
            codes0.sort()
            for orgStructureCode in codes0:
                orgStructureData = reportData[orgStructureCode]
                
                totalOSVisitCount = 0
                totalOSEventCount = 0
                totalOSSum = 0.0
                totalOSWages = 0.0
                totalOSAdditionalPayments = 0.0
                totalOSDrugs = 0.0
                totalOSSoftInventory = 0.0
                totalOSOverhead = 0.0
                codes = orgStructureData.keys()
                codes.sort()
                for serviceCode in codes:
                    serviceData = orgStructureData[serviceCode]
                    row = table.addRow()
                    table.setText(row, 0, serviceData['orgStructureCode'])
                    table.setText(row, 1, serviceData['specialityName'])
                    table.setText(row, 2, serviceData['serviceCode'])
                    table.setText(row, 3, forceString(serviceData['visitCount']))
                    table.setText(row, 4, 'x')
                    table.setText(row, 5, 'x')
                    table.setText(row, 6,  'x')#forceString(serviceData['eventCount']))
                    table.setText(row, 7, QtCore.QString.number(serviceData['sum'], 'g', 9))
                    table.setText(row, 8, QtCore.QString.number(serviceData['wages'], 'g', 9))
                    table.setText(row, 9, QtCore.QString.number(serviceData['additionalPayments'], 'g', 9))
                    table.setText(row, 10, QtCore.QString.number(serviceData['drugs'], 'g', 9))
                    table.setText(row, 11, QtCore.QString.number(serviceData['softInventory'], 'g', 9))
                    table.setText(row, 12, QtCore.QString.number(serviceData['overhead'], 'g', 9))
                    totalOSVisitCount += serviceData['visitCount']
                    totalOSEventCount += serviceData['eventCount']
                    totalOSSum += serviceData['sum']
                    totalOSWages += serviceData['wages']
                    totalOSAdditionalPayments += serviceData['additionalPayments']
                    totalOSDrugs += serviceData['drugs']
                    totalOSSoftInventory += serviceData['softInventory']
                    totalOSOverhead += serviceData['overhead']
                
                osTotalRow = table.addRow()
                table.setText(osTotalRow, 0, u'Итого по подразделению')
                table.setText(osTotalRow, 1, 'x')
                table.setText(osTotalRow, 2, 'x')
                table.setText(osTotalRow, 3, forceString(totalOSVisitCount))
                table.setText(osTotalRow, 4, 'x')
                table.setText(osTotalRow, 5, 'x')
                table.setText(osTotalRow, 6, forceString(totalOSEventCount)) # 'x')
                table.setText(osTotalRow, 7, QtCore.QString.number(totalOSSum, 'g', 9))
                table.setText(osTotalRow, 8, QtCore.QString.number(totalOSWages, 'g', 9))
                table.setText(osTotalRow, 9, QtCore.QString.number(totalOSAdditionalPayments, 'g', 9))
                table.setText(osTotalRow, 10, QtCore.QString.number(totalOSDrugs, 'g', 9))
                table.setText(osTotalRow, 11, QtCore.QString.number(totalOSSoftInventory, 'g', 9))
                table.setText(osTotalRow, 12, QtCore.QString.number(totalOSOverhead, 'g', 9))
                
                totalVisitCount += totalOSVisitCount
                totalEventCount += totalOSEventCount
                totalSum += totalOSSum
                totalWages += totalOSWages
                totalAdditionalPayments += totalOSAdditionalPayments
                totalDrugs += totalOSDrugs
                totalSoftInventory += totalOSSoftInventory
                totalOverhead += totalOSOverhead
            
            cursor.setCharFormat(CReportBase.TableTotal)
            totalRow = table.addRow()
            table.setText(totalRow, 0, u'Итого по %s' % (u'поликлинике' if params.get('orgStructureId', None) is not None or params.has_key('dataFileName') else u'всем подразделениям'))
            table.setText(totalRow, 1, 'x')
            table.setText(totalRow, 2, 'x')
            table.setText(totalRow, 3, forceString(totalVisitCount))
            table.setText(totalRow, 4, 'x')
            table.setText(totalRow, 5, 'x')
            table.setText(totalRow, 6, forceString(totalEventCount))
            table.setText(totalRow, 7, QtCore.QString.number(totalSum, 'g', 9))
            table.setText(totalRow, 8, QtCore.QString.number(totalWages, 'g', 9))
            table.setText(totalRow, 9, QtCore.QString.number(totalAdditionalPayments, 'g', 9))
            table.setText(totalRow, 10, QtCore.QString.number(totalDrugs, 'g', 9))
            table.setText(totalRow, 11, QtCore.QString.number(totalSoftInventory, 'g', 9))
            table.setText(totalRow, 12, QtCore.QString.number(totalOverhead, 'g', 9))
            
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock(CReportBase.AlignLeft)
            cursor.insertText(u'\nОбщая сумма оказанных медицинских услуг составляет ')
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(QtGui.QFont.Bold)
            cursor.insertText(u'%s руб.'% QtCore.QString.number(totalSum, 'g', 9, ), fmt)
            fmt.setFontWeight(QtGui.QFont.Normal)
            cursor.insertText(u', в т.ч.анестезиологических пособий ____________ руб.\n', fmt)
            cursor.insertText(u'%s\n' % unicode(QtCore.QDate.currentDate().toString('"d" MMMM yyyy')).lower())
            mainStaff = getOrganisationMainStaff(QtGui.qApp.currentOrgId())
            cursor.insertText(u'Руководитель МО_______________/%s\n' % mainStaff[0])
            cursor.insertText(u'Экономист   _______________/%s' % mainStaff[1])	
            cursor.insertText(u'__________МП\n')
            isFirstReport = False
        
        return doc
