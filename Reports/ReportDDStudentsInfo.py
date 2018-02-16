# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Orgs import selectOrganisation
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportDDStudentsInfoSetup import Ui_ReportDDStudentsInfoSetupDialog
from library.Utils import forceDate, forceInt, forceString, firstMonthDay, lastMonthDay


def selectDataCommon(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    sex = params.get('sex', 0)
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    workOrganisationId = params.get('workOrganisation',  None)
    
    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableAccountItem = db.table('Account_Item')
    tablePerson = db.table('Person')
    tableClientWork = db.table('ClientWork')
    cond = []
    joinCond = []
    
    cond.append(tableEvent['setDate'].ge(begDate))
    cond.append(tableEvent['execDate'].le(endDate))
    
    if personId:
        cond.append(tableEvent['execPerson_id'].eq(personId))
    elif orgStructureId:
        joinCond.append('LEFT JOIN Person ON Event.execPerson_id=Person.id')
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Event.execDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Event.execDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
        
    if params.get('podtver', None):
        joinCond.append("LEFT JOIN Account_Item ON Event.id=Account_Item.event_id AND Account_Item.deleted = 0")
        if params.get('podtverType', 0) == 1:
            cond.append(tableAccountItem['date'].isNotNull())
            cond.append(tableAccountItem['refuseType_id'].isNull())
        elif params.get('podtverType', 0) == 2:
            cond.append(tableAccountItem['date'].isNotNull())
            cond.append(tableAccountItem['refuseType_id'].isNotNull())
            
        if params.get('begDatePodtver', None):
            cond.append(tableAccountItem['date'].ge(params['begDatePodtver']))
        if params.get('endDatePodtver', None):
            cond.append(tableAccountItem['date'].lt(params['endDatePodtver'].addDays(1)))
        
        if params.get('refuseType', None) != 0:
            cond.append(tableAccountItem['refuseType_id'].eq(params['refuseType']))
    
    if workOrganisationId:
        joinCond.append("LEFT JOIN ClientWork ON Client.id=ClientWork.client_id")
        cond.append(tableClientWork['org_id'].eq(workOrganisationId))
        
    """stmt = u'''
SELECT
    COUNT(*) AS cnt,
    Client.sex AS sex,
    Diagnosis.MKB AS mkb
FROM Event
    LEFT JOIN Client ON Event.client_id=Client.id
    LEFT JOIN Diagnostic ON Event.id=Diagnostic.event_id
    LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id=Diagnosis.id
    %s
WHERE
    Event.eventType_id=107 AND
    Diagnostic.diagnosisType_id=1 AND

    %s
GROUP BY
    sex,
    mkb
    '''
    """
    
    stmt = u'''
SELECT
    Event.execDate AS execDate,
    Client.sex AS sex,
    Diagnosis.MKB AS mkb,
    Event.client_id AS client_id
FROM Event
    LEFT JOIN Client ON Event.client_id=Client.id
    LEFT JOIN Diagnostic ON Event.id=Diagnostic.event_id
    LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id=Diagnosis.id
    %s
WHERE
    Event.eventType_id=107 AND
    Diagnostic.diagnosisType_id=1 AND
    %s
    '''
    return db.query(stmt % (' '.join(joinCond), db.joinAnd(cond)))
    
def selectDataCured(client_id, prevExecDate,  mkb,  params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    
    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableAccountItem = db.table('Account_Item')
    tablePerson = db.table('Person')
    tableDiagnosis = db.table('Diagnosis')
    cond = []
    joinCond = []
    
    cond.append(tableEvent['setDate'].ge(begDate))
    cond.append(tableEvent['setDate'].ge(prevExecDate))
    cond.append(tableEvent['execDate'].le(endDate))
    
    cond.append(tableClient['id'].eq(client_id))
    cond.append(tableDiagnosis['MKB'].eq(mkb))
    
    if params.get('podtver', None):
        if params.get('podtverType', 0) == 1:
            cond.append(tableAccountItem['date'].isNotNull())
            cond.append(tableAccountItem['refuseType_id'].isNull())
        elif params.get('podtverType', 0) == 2:
            cond.append(tableAccountItem['date'].isNotNull())
            cond.append(tableAccountItem['refuseType_id'].isNotNull())
            
        if params.get('begDatePodtver', None):
            cond.append(tableAccountItem['date'].ge(params['begDatePodtver']))
        if params.get('endDatePodtver', None):
            cond.append(tableAccountItem['date'].lt(params['endDatePodtver'].addDays(1)))
        
        if params.get('refuseType', None) != 0:
            cond.append(tableAccountItem['refuseType_id'].eq(params['refuseType']))
    
    if personId:
        cond.append(tableEvent['execPerson_id'].eq(personId))
    elif orgStructureId:
        joinCond.append('LEFT JOIN Person ON Event.execPerson_id=Person.id')
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    
    stmt = u'''
SELECT
    Event.id as id
FROM Event
    LEFT JOIN Client ON Event.client_id=Client.id
    LEFT JOIN Diagnostic ON Event.id=Diagnostic.event_id
    LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id=Diagnosis.id
    %s
WHERE
    %s
    '''
    return db.query(stmt % (' '.join(joinCond), db.joinAnd(cond)))
    
class CReportDDStudentsInfo(CReport):
    def __init__(self,  parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Информация о диспансеризации студентов за 2012 год')

    def getSetupDialog(self,  parent):
        result = CReportDDStudentsInfoSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        db = QtGui.qApp.db

        reportRowSize = 25
        reportRow = [0]*reportRowSize
        reportRow[0] = u'МБУЗ "Гор.пол.№3'
        query = selectDataCommon(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            execDate = forceDate(record.value('execDate'))
            sex = forceInt(record.value('sex'))
            current = False
            if execDate.month()==params.get('endDate', QtCore.QDate()).month():
                current = True
            reportRow[2] += 1
            if current:
                reportRow[1] += 1
            if sex==1:
                reportRow[4] += 1
                if current:
                    reportRow[3] += 1
            elif sex==2:
                if current:
                    reportRow[5] += 1
                reportRow[6] += 1
            if forceString(record.value('mkb'))[:3]!='Z00':
                reportRow[8] += 1
                if current:
                    reportRow[7] += 1
                if sex == 1:
                    if current:
                        reportRow[9] += 1
                    reportRow[10] += 1
                elif sex == 2:
                    if current:
                        reportRow[11] += 1
                    reportRow[12] += 1
                mkb = record.value('mkb')
                client_id = record.value('client_id')
                
                queryCured = selectDataCommon(client_id,  execDate,  mkb,  params)
                if queryCured.next():
                    if current:
                        reportRow[19] += 1
                    reportRow[20] += 1
                    if sex == 1:
                        if current:
                            reportRow[21] += 1
                        reportRow[22] += 1
                    elif sex == 2:
                        if current:
                            reportRow[23] += 1
                        reportRow[24] += 1
                    
        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('12%',  [u'Наименование медицинской организации',           u'',       u''],  CReportBase.AlignLeft), 
            ('3%',  [u'число студентов которым проведена диспансеризация',
                        u'Всего', 
                        u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('3%',  [u'',  u'мужчины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'женщины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('3%',  [u'Из них число студентов, у которых выявлены заболевания',
                        u'Всего', 
                        u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('3%',  [u'',  u'мужчины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'женщины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('3%',  [u'Из них число студентов, у которых выявлены факторы риска развития заболеваний',
                        u'Всего', 
                        u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('3%',  [u'',  u'мужчины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'женщины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('3%',  [u'Из них получили лечение',
                        u'Всего', 
                        u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('3%',  [u'',  u'мужчины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'женщины',  u'За текущий месяц'],  CReportBase.AlignRight), 
            ('4%',  [u'',  u'',  u'Нарастающим итогом'],  CReportBase.AlignRight)] 
            

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 6)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(0, 7, 1, 6)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)
        table.mergeCells(1, 11, 1, 2)
        table.mergeCells(0, 13, 1, 6)
        table.mergeCells(1, 13, 1, 2)
        table.mergeCells(1, 15, 1, 2)
        table.mergeCells(1, 17, 1, 2)
        table.mergeCells(0, 19, 1, 6)
        table.mergeCells(1, 19, 1, 2)
        table.mergeCells(1, 21, 1, 2)
        table.mergeCells(1, 23, 1, 2)
        
        j = table.addRow()
        for i in range(reportRowSize):
            table.setText(j, i, reportRow[i])       
        return doc


class CReportDDStudentsInfoSetupDialog(QtGui.QDialog,  Ui_ReportDDStudentsInfoSetupDialog):
    def __init__(self,  parent=None):
        QtGui.QDialog.__init__(self,  parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbRefuseType.setTable('rbPayRefuseType', True)
        self.cmbPodtver.addItem(u'без подтверждения')
        self.cmbPodtver.addItem(u'оплаченные')
        self.cmbPodtver.addItem(u'отказанные')

    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.chkPodtver.setChecked(params.get('podtver', False))
        self.edtBegDatePodtver.setDate(params.get('begDatePodtver', firstMonthDay(date)))
        self.edtEndDatePodtver.setDate(params.get('endDatePodtver', lastMonthDay(date)))
        self.cmbPodtver.setCurrentIndex(params.get('podtverType', 0))
        self.cmbRefuseType.setValue(params.get('refuseType', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbWorkOrganisation.setValue(params.get('workOrganisation',  None))
        
    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['podtver'] = self.chkPodtver.isChecked()
        result['podtverType'] = self.cmbPodtver.currentIndex()
        result['begDatePodtver'] = self.edtBegDatePodtver.date()
        result['endDatePodtver'] = self.edtEndDatePodtver.date()
        result['refuseType'] = self.cmbRefuseType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['workOrganisation'] = self.cmbWorkOrganisation.value()
        
        return result
        
    @QtCore.pyqtSlot(int)
    def on_chkPodtver_stateChanged(self, state):
        self.lblPodtver.setEnabled(state)
        self.lblBegDatePodtver.setEnabled(state)
        self.lblEndDatePodtver.setEnabled(state)
        self.lblRefuseType.setEnabled(state)
        self.cmbPodtver.setEnabled(state)
        self.edtBegDatePodtver.setEnabled(state)
        self.edtEndDatePodtver.setEnabled(state)
        self.cmbRefuseType.setEnabled(state)

    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)
