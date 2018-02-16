# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import copy

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceDouble, forceInt, forceString
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportVisitsSetup import Ui_ReportVisitsSetupDialog


def selectData(params):
    stmt = u'''
SELECT
    COUNT(*) AS cnt,
    rbService.code AS code,
    rbService.adultUetDoctor AS uetDoctor,
    rbService.adultUetAverageMedWorker AS uetAverageMedWorker,
    Person.lastName AS lastName,
    Person.firstName AS firstName,
    Person.patrName AS middleName,
    rbSpeciality.name AS speciality
FROM Visit
    LEFT JOIN Event ON Event.id = Visit.event_id
    LEFT JOIN EventType ON EventType.id = Event.eventType_id
    LEFT JOIN Person ON Person.id = Visit.person_id
    LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
    LEFT JOIN rbService ON rbService.id = Visit.service_id
    LEFT JOIN Client ON Event.client_id=Client.id
    %s
WHERE
    %s
GROUP BY
    code,
    speciality,
    lastName,
    firstName,
    middleName
    '''
    
    joinCond = u''
    db = QtGui.qApp.db
    tableVisit  = db.table('Visit')
    tableEvent  = db.table('Event')
    tableOrganisation = db.table('Organisation')
    
    begEventDate = params.get('begEventDate', QtCore.QDate())
    endEventDate = params.get('endEventDate', QtCore.QDate())
    eventTypeId = params.get('eventTypeId', None)
    typeFinanceId = params.get('typeFinanceId', None)
    tariff = params.get('tariff', 0)
    visitPayStatus = params.get('visitPayStatus', 0) - 1
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    insurerId = params.get('insurerId',  None)
    
    cond = []
    if (params.get('checkOnlyEventExecDate', False)):
        cond.append(tableEvent['setDate'].ge(begEventDate))
        cond.append(tableEvent['execDate'].le(endEventDate))
    else:
        cond.append(tableEvent['execDate'].ge(begEventDate))
        cond.append(tableEvent['execDate'].le(endEventDate))
        
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if typeFinanceId:
        cond.append(tableVisit['finance_id'].eq(typeFinanceId))
    if tariff == 2:
        cond.append(tableVisit['service_id'].isNull())
    elif tariff == 1:
        cond.append(tableVisit['service_id'].isNotNull())
    if visitPayStatus >= 0:
        cond.append(u'getPayCode(Visit.finance_id, Visit.payStatus) = %d'%(visitPayStatus))
    if insurerId:
        joinCond = u'''
        LEFT JOIN ClientPolicy ON Event.client_id=ClientPolicy.client_id
        LEFT JOIN Organisation ON ClientPolicy.insurer_id=Organisation.id
        '''
        cond.append(tableOrganisation['id'].eq(insurerId))
    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    return db.query(stmt % (joinCond, db.joinAnd(cond)))
    
class CReportVisits(CReport):
    def __init__(self,  parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Амбулаторно-поликлиническая помощь')

    def getSetupDialog(self,  parent):
        result = CReportVisitsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):        
        reportRowSize = 14
        query = selectData(params)
        
        reportData = {}
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            firstName = forceString(record.value('firstName'))
            firstNameInitial = ('%s.'  % firstName[0]) if firstName else ''
            middleName = forceString(record.value('middleName'))
            middleNameInitial = ('%s.'  % middleName[0]) if middleName else ''
            
            doctor = '%s %s %s' % (forceString(record.value('lastName')),
                                   firstNameInitial,
                                   middleNameInitial
                                   )
            doctor = doctor.strip()
            cnt = forceInt(record.value('cnt'))
            uetDoctor = forceDouble(record.value('uetDoctor'))
            uetAverageMedWorker = forceDouble(record.value('uetAverageMedWorker'))
            uet =  uetDoctor + uetAverageMedWorker
            code = forceString(record.value('code'))
            speciality = forceString(record.value('speciality'))
            if not speciality in reportData.keys() :
                reportData[speciality] = {}
            if not doctor in reportData[speciality].keys():
                reportData[speciality][doctor] = visitTypes()
            if code[5:7] == '01':
                if code[7:9] == '02':
                    reportData[speciality][doctor].surgeryIntrusion.add(cnt,  uet)
                else:
                    reportData[speciality][doctor].lpu.add(cnt,  uet)
            elif code[5:7] == '02':
                reportData[speciality][doctor].homeVisit.add(cnt,  uet)
            elif code[5:7] == '03':
                reportData[speciality][doctor].profosmotr.add(cnt,  uet)
            elif code[5:7] == '10':
                reportData[speciality][doctor].healthSchools.add(cnt,  uet)
            
        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        tableColumns = [
            ('12%',  [u'Профиль Специалиста',           u''],  CReportBase.AlignLeft), 
            ('12%',  [u'ФИО Врача',                             u''],  CReportBase.AlignRight), 
            ('6%',  [u'Поликлиника',  u'Посещ.'],  CReportBase.AlignRight), 
            ('5%',  [u'',                      u'УЕТ'],  CReportBase.AlignRight), 
            ('6%',  [u'Профосмотр',  u'Посещ.'],  CReportBase.AlignRight), 
            ('5%',  [u'',                     u'УЕТ'],  CReportBase.AlignRight), 
            ('6%',  [u'На дому',        u'Посещ.'],  CReportBase.AlignRight), 
            ('5%',  [u'',                     u'УЕТ'],  CReportBase.AlignRight), 
            ('6%',  [u'Хирургическое вмешательство', u'Посещ.'],  CReportBase.AlignRight), 
            ('5%',  [u'',                      u'УЕТ'],  CReportBase.AlignRight), 
            ('6%',  [u'Школы здоровья', u'Посещ.'],  CReportBase.AlignRight), 
            ('5%',  [u'',                      u'УЕТ'],  CReportBase.AlignRight), 
            ('6%',  [u'Итого',            u'Посещ.'],  CReportBase.AlignRight), 
            ('5%',  [u'',                      u'УЕТ'],  CReportBase.AlignRight)]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 2)
        table.mergeCells(0, 4, 1, 2)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(0, 8, 1, 2)
        table.mergeCells(0, 10, 1, 2)
        table.mergeCells(0, 12, 1, 2)
        
        totalRow = [0] * reportRowSize
        grandTotal = [0] * reportRowSize
        grandTotal[0] = u'Итого'
        grandTotal[1] = u''
        currentRowNum = 0
        for i in range(2,  14):
            grandTotal[i] = 0
        tempArray = []
        tempRow = [0] * reportRowSize
        for speciality in reportData.keys():
            del(tempArray[:])
            totalRow[0] = speciality
            totalRow[1] = ''
            for i in range(2,  14):
                totalRow[i] = 0
            for doctor in reportData[speciality].keys():
                tempRow[0] = ''
                tempRow[1] = doctor
                tempRow[2] =reportData[speciality][doctor].lpu.visits
                tempRow[3] =reportData[speciality][doctor].lpu.uets
                tempRow[4] =reportData[speciality][doctor].profosmotr.visits
                tempRow[5] =reportData[speciality][doctor].profosmotr.uets
                tempRow[6] =reportData[speciality][doctor].homeVisit.visits
                tempRow[7] =reportData[speciality][doctor].homeVisit.uets
                tempRow[8] =reportData[speciality][doctor].surgeryIntrusion.visits
                tempRow[9] =reportData[speciality][doctor].surgeryIntrusion.uets
                tempRow[10] =reportData[speciality][doctor].healthSchools.visits
                tempRow[11] =reportData[speciality][doctor].healthSchools.uets
                tempRow[12] = tempRow[2] + tempRow[4] + tempRow[6] + tempRow[8] + tempRow[10]
                tempRow[13] = tempRow[3] + tempRow[5] + tempRow[7] + tempRow[9] + tempRow[11]
                tempArray.append(copy.copy(tempRow))
                for i in range(2, 14):
                    totalRow[i] += tempRow[i]
            
            if totalRow[12] != 0 and totalRow[13] != 0:
                j = table.addRow()
                for i in range(reportRowSize):
                    table.setText(j, i, totalRow[i])
                    if i>1:
                        grandTotal[i] += totalRow[i]
                for row in tempArray:
                    if row[12] != 0 and row[13] != 0:
                        j = table.addRow()
                        for i in range(reportRowSize):
                            table.setText(j, i, row[i]) 
        j = table.addRow()
        for i in range(reportRowSize):
            table.setText(j, i, grandTotal[i])           
            
        return doc


class CReportVisitsSetupDialog(QtGui.QDialog,  Ui_ReportVisitsSetupDialog):
    def __init__(self,  parent=None):
        QtGui.QDialog.__init__(self,  parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbTypeFinance.setTable('rbFinance', True)
        self.cmbTariff.setCurrentIndex(0)
        self.cmbVisitPayStatus.setCurrentIndex(0)
        
    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setParams(self, params):
        self.edtBegEventDate.setDate(params.get('begEventDate', QtCore.QDate.currentDate()))
        self.edtEndEventDate.setDate(params.get('endEventDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.cmbTypeFinance.setValue(params.get('typeFinanceId', None))
        self.cmbInsurer.setValue(params.get('insurerId'))
        self.cmbTariff.setCurrentIndex(params.get('tariff', 0))
        self.cmbVisitPayStatus.setCurrentIndex(params.get('visitPayStatus', 0))
        self.chkOnlyEventExecDate.setChecked(params.get('checkOnlyEventExecDate', False))
        
    def params(self):
        result = {}
        result['begEventDate'] = self.edtBegEventDate.date()
        result['endEventDate'] = self.edtEndEventDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['typeFinanceId'] = self.cmbTypeFinance.value()
        result['insurerId'] = self.cmbInsurer.value()
        result['tariff'] = self.cmbTariff.currentIndex()
        result['visitPayStatus'] = self.cmbVisitPayStatus.currentIndex()
        result['checkOnlyEventExecDate'] = self.chkOnlyEventExecDate.isChecked()
        return result
        
    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegEventDate_dateChanged(self, date):
        self.edtEndEventDate.setMinimumDate(QtCore.QDate(date))

class visitsAndUETs:
    def __init__(self,  visits,  uet_norm):
        self.visits = visits
        self.uets = uet_norm*visits
    
    def add(self,  visits,  uet_norm):
        self.visits += visits
        self.uets += uet_norm*visits

class visitTypes:
    def __init__(self):
        self.lpu = visitsAndUETs(0, 0)
        self.profosmotr = visitsAndUETs(0, 0)
        self.homeVisit = visitsAndUETs(0, 0)
        self.surgeryIntrusion = visitsAndUETs(0, 0)
        self.healthSchools = visitsAndUETs(0, 0)
