# -*- coding: utf-8 -*- 


#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.database   import addDateInRange
from library.Utils      import forceBool, forceDate, forceInt, forceString
from Orgs.Utils         import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_StationaryF007DCSetup import Ui_StationaryF007DCSetupDialog


def selectData(eventTypeId, begDate, endDate,  socStatusClassId,  socStatusTypeId,  orgStructureId,  locality):
    stmt = u"""
SELECT
    COUNT(*) as cnt, 
    DATE(Event.setDate) as startDate,
    DATE(Event.execDate) as endDate, 
    age(Client.birthDate, Event.setDate) as clientAge, 
    rbResult.name as eventResult,
    IFNULL(isClientVillager(Event.client_id), 0) as isVillager
FROM %s 
WHERE %s
GROUP BY startDate, endDate, clientAge, eventResult, isVillager
    """
    db = QtGui.qApp.db
    
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableResult = db.table('rbResult')
    tablePerson = db.table('Person')
    
    queryTable = tableEvent.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableResult, tableEvent['result_id'].eq(tableResult['id']))

    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableEvent['client_id'].isNotNull())
    
    cond_tmp = []
    cond_tmp2 = []
    addDateInRange(cond_tmp, tableEvent['setDate'], begDate,  endDate)
    cond_tmp = [db.joinAnd(cond_tmp)]
    cond_tmp2.append(tableEvent['setDate'].lt(begDate))
    cond_tmp2.append(tableEvent['execDate'].ge(begDate))
    cond_tmp.append(db.joinAnd(cond_tmp2))
    cond.append(db.joinOr(cond_tmp))
    
    eventQuery = tableEvent
    eventCond = []
    if eventTypeId:
        eventCond.append(tableEvent['eventType_id'].eq(eventTypeId))
    eventQuery = eventQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
    if orgStructureId:
        eventCond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        eventCond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
       
    if eventCond:
        cond.append(db.existsStmt(eventQuery, eventCond))
        cond.append(db.joinAnd(eventCond))
    
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS('+subStmt+')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS('+subStmt+')')

    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Event.client_id), 0) = %d' % (locality-1))
    return db.query(stmt % (db.getTableName(queryTable), db.joinAnd(cond)))
 
class CStationaryF007DCSetupDialog(QtGui.QDialog, Ui_StationaryF007DCSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)

        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        
    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))
        self.cmbLocality.setCurrentIndex(params.get('locality', 0))
        
    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        result['locality'] = self.cmbLocality.currentIndex()
        
        return result
        
    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        if (self.edtBegDate.date() > self.edtEndDate.date()):
            self.edtEndDate.setDate(QtCore.QDate(date))
            
    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        if (self.edtBegDate.date() > self.edtEndDate.date()):
            self.edtBegDate.setDate(QtCore.QDate(date))
        
    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id=%d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)
        
class CStationaryF007DC(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Листок учета движения больных и коечного фонда дневного стационара')


    def getSetupDialog(self, parent):

        result = CStationaryF007DCSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        locality = params.get('locality', 0)

        db = QtGui.qApp.db

        reportRowSize = 11

        tmp = 0
        reportData = {}
        MKBList = []
        query = selectData(eventTypeId, begDate, endDate, socStatusClassId, socStatusTypeId, orgStructureId, locality)
        reportRow = [0]*reportRowSize
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record    = query.record()
            cnt       = forceInt(record.value('cnt'))
            age       = forceInt(record.value('clientAge'))
            evResult = forceString(record.value('eventResult'))
            isVillager = forceBool(record.value('isVillager'))
            setDate = forceDate(record.value('startDate'))
            execDate = forceDate(record.value('endDate'))
            
            if (execDate and execDate>=begDate and setDate<begDate):
                reportRow[2] += cnt
            if (setDate>=begDate and setDate<=endDate):
                reportRow[3] += cnt
                if (isVillager):
                    reportRow[4] += cnt
                if (age>=60):
                    reportRow[5] += cnt
            if (execDate and execDate>=begDate and execDate<=endDate):
                reportRow[6] += cnt
                if (u"cмерть" in evResult.lower() or u"умер" in evResult.lower()):
                    reportRow[7] += cnt
            if (not execDate or execDate>endDate):
                reportRow[8] += cnt       
            
            ### Подсчет количества проведенных дней
            if (not execDate or execDate>endDate):
                if (setDate>=begDate):
                    reportRow[9] += (setDate.daysTo(endDate)+1)*cnt
                    if isVillager:
                        reportRow[10] += (setDate.daysTo(endDate)+1)*cnt
                else:
                    reportRow[9] += (begDate.daysTo(endDate)+1)*cnt
                    if isVillager:
                        reportRow[10] += (begDate.daysTo(endDate)+1)*cnt
            elif (execDate<=endDate and execDate>=begDate):
                if (setDate>=begDate):
                    reportRow[9] += (setDate.daysTo(execDate)+1)*cnt
                    if isVillager:
                        reportRow[10] += (setDate.daysTo(execDate)+1)*cnt
                else:
                    reportRow[9] += (begDate.daysTo(execDate)+1)*cnt
                    if isVillager:
                        reportRow[10] += (begDate.daysTo(execDate)+1)*cnt
          
        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('8%',  [u'Число мест'],  CReportBase.AlignLeft), 
            ('8%',  [u'Среднемесячных мест'],  CReportBase.AlignRight), 
            ('8%',  [u'Состояло больных на начало периода'],  CReportBase.AlignRight), 
            ('8%',  [u'Поступило больных',  u'всего'],  CReportBase.AlignRight), 
            ('8%',  [u'',                         u'из них',  u'сельских жителей'],  CReportBase.AlignRight), 
            ('8%',  [u'',                         u'',            u'60 лет и старше'],  CReportBase.AlignRight), 
            ('8%',  [u'Выписано больных'],  CReportBase.AlignRight), 
            ('8%',  [u'Умерло'],  CReportBase.AlignRight), 
            ('8%',  [u'Состояло больных на конец периода'],  CReportBase.AlignRight), 
            ('10%',  [u'Проведено дней лечения',  u'всего'],  CReportBase.AlignRight), 
            ('10%',  [u'',                                     u'сельскими жителями'],  CReportBase.AlignRight)
            ]
            
        table = createTable(cursor,  tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(0, 6, 3, 1)
        table.mergeCells(0, 7, 3, 1)
        table.mergeCells(0, 8, 3, 1)
        table.mergeCells(0, 9, 1, 2)
        table.mergeCells(1, 9, 2, 1)
        table.mergeCells(1, 10, 2, 1)
            
        
        i = table.addRow()
        for j in xrange(reportRowSize):
            table.setText(i,  j,  reportRow[j])
        return doc
        

    def produceTotalLine(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(len(total)):
            table.setText(i, j+1, total[j], CReportBase.TableTotal)
