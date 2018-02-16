# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportDDStudentsResultsSetup import Ui_ReportDDStudentsResultsSetupDialog
from library.Utils import forceInt, forceString, firstMonthDay, lastMonthDay


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    
    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    
    cond = []
    joinCond = []

    cond.append("first.setDate>='%s'" % begDate.toString('yyyy-MM-dd'))
    cond.append("first.execDate<='%s'" % endDate.toString('yyyy-MM-dd'))
    if params.get('podtver', None):
        joinCond.append("LEFT JOIN Account_Item ON first.id=Account_Item.event_id AND Account_Item.deleted = 0")
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
    
    stmt = u'''
SELECT
    COUNT(*) AS cnt,
    second.MKB AS mkb, 
    first.client_id AS client_id,
    first.execDate AS execDate
FROM Event first
    LEFT JOIN Diagnostic ON first.id=Diagnostic.event_id
    LEFT JOIN Diagnosis second ON Diagnostic.diagnosis_id=second.id
    %s
WHERE NOT EXISTS  (
        SELECT *
        FROM Event third
            LEFT JOIN Diagnostic ON third.id=Diagnostic.event_id
            LEFT JOIN Diagnosis fourth ON Diagnostic.diagnosis_id=fourth.id
        WHERE
            third.client_id=first.client_id AND
            fourth.MKB=second.MKB AND
            third.execDate<first.execDate
            ) AND
    first.eventType_id=107 AND
    Diagnostic.diagnosisType_id=1 AND
    %s
GROUP BY
    mkb
    '''
    return db.query(stmt % (' '.join(joinCond), db.joinAnd(cond)))
    
class CReportDDStudentsResults(CReport):
    def __init__(self,  parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Результаты диспансеризации студентов')

    def getSetupDialog(self,  parent):
        result = CReportDDStudentsResultsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        db = QtGui.qApp.db

        reportRowSize = 4
        reportColSize = 19
        reportCol = [0]*reportColSize
        reportData = []
        diagnoses = [u'Туберкулез',  
        u'Злокачественные новообразования:',  
        u'\tорганов пищеварения',  
        u'\tтрахеи, бронхов, легкого',  
        u'\tкожи',  
        u'\tмолочной железы',  
        u'\tженских половых органов',  
        u'\tпредстательной железы',  
        u'\tлимфатической и кроветворной ткани', 
        u'Анемия', 
        u'Сахарный диабет', 
        u'Ожирение', 
        u'Нарушение обмена липопротеидов', 
        u'Болезни, храктеризующиеся повышенным кровяным давлением', 
        u'Ишемические болезни сердца', 
        u'Повышенное содержание глюкозы в крови', 
        u'Отклонения от нормы, выявленные при получении диагностического изображения в ходе исследования легких', 
        u'Отклонения от нормы, выявленные при получении диагностического изображения в ходе исследования молочной железы', 
        u'Отклонения от нормы, выявленные при проведении функциональных исследований сердечно-сосудистой системы']
        
        nums = [1,  '',  2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        mkbCodes = ['A15-A19', '', 'C15-C26', 'C33-C34', 'C43-C44', 'C50', 'C50-C58', 'C61', 'C81-C96', 'D50-D64', 
                    'E10-E14', 'E66', 'E78', 'I10-I15', 'I20-I25', 'R73', 'R91', 'R92', 'R94.3']
        reportData.append(diagnoses)
        reportData.append(nums)
        reportData.append(mkbCodes)
        reportData.append(reportCol)
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            mkb = forceString(record.value('mkb'))
            cnt = forceInt(record.value('cnt'))
            if mkb:
                if mkb[0] == 'A':
                    if int(mkb[1:3]) in range(15,  20):
                        reportData[3][0] += cnt
                elif mkb[0] == 'C':
                    if int(mkb[1:3]) in range(15,  27):
                        reportData[3][1] += cnt
                        reportData[3][2] += cnt
                    elif int(mkb[1:3]) in range(33,  35):
                        reportData[3][1] += cnt
                        reportData[3][3] += cnt
                    elif int(mkb[1:3]) in range(43,  45):
                        reportData[3][1] += cnt
                        reportData[3][4] += cnt
                    elif int(mkb[1:3]) in range(50,  59):
                        if int(mkb[1:3])==50:
                            reportData[3][5] += cnt
                        reportData[3][1] += cnt
                        reportData[3][6] += cnt
                    elif int(mkb[1:3]) == 61:
                        reportData[3][1] += cnt
                        reportData[3][7] += cnt
                    elif int(mkb[1:3]) in range(81, 97):
                        reportData[3][1] += cnt
                        reportData[3][8] += cnt
                elif mkb[0] == 'D':
                    if int(mkb[1:3]) in range(50, 65):
                        reportData[3][9] += cnt
                elif mkb[0] == 'E':
                    if int(mkb[1:3]) in range(10, 15):
                        reportData[3][10] += cnt
                    elif int(mkb[1:3]) == 66:
                        reportData[3][11] += cnt
                    elif int(mkb[1:3]) == 78:
                        reportData[3][12] += cnt
                elif mkb[0] == 'I':
                    if int(mkb[1:3]) in range(10,  16):
                        reportData[3][13] += cnt
                    elif int(mkb[1:3]) in range(20,  26):
                        reportData[3][14] += cnt
                elif mkb[0] == 'R':
                    if int(mkb[1:3]) == 73:
                        reportData[3][15] += cnt
                    elif int(mkb[1:3]) == 91:
                        reportData[3][16] += cnt
                    elif int(mkb[1:3]) == 92:
                        reportData[3][17] += cnt
                    elif int(mkb[1:3]) == 94 and mkb[3:5]=='.3':
                        reportData[3][18] += cnt
    
        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('50%',  [u'Заболевания и отклонения от нормы, выявленные при клинических и лабораторных исследованиях',  u'1'],  CReportBase.AlignLeft), 
            ('7%',  [u'№ строки', u'2'],  CReportBase.AlignCenter), 
            ('15%',  [u'Код заболевания по МКБ-10',  u'3'],  CReportBase.AlignCenter), 
            ('28%',  [u'Число заболеваний, впервые выявленных у студентов во время проведения диспансеризации',  u'4'],  CReportBase.AlignCenter)] 
            
        table = createTable(cursor, tableColumns)
        
        for j in range(reportColSize):
            k = table.addRow()
            for i in range(reportRowSize):
                table.setText(k,  i, reportData[i][j])
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Главный врач')  
        return doc


class CReportDDStudentsResultsSetupDialog(QtGui.QDialog,  Ui_ReportDDStudentsResultsSetupDialog):
    def __init__(self,  parent=None):
        QtGui.QDialog.__init__(self,  parent)
        self.setupUi(self)
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
        self.chkPodtver.setChecked(params.get('podtver', False))
        self.edtBegDatePodtver.setDate(params.get('begDatePodtver', firstMonthDay(date)))
        self.edtEndDatePodtver.setDate(params.get('endDatePodtver', lastMonthDay(date)))
        self.cmbPodtver.setCurrentIndex(params.get('podtverType', 0))
        self.cmbRefuseType.setValue(params.get('refuseType', None))
        
    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['podtver'] = self.chkPodtver.isChecked()
        result['podtverType'] = self.cmbPodtver.currentIndex()
        result['begDatePodtver'] = self.edtBegDatePodtver.date()
        result['endDatePodtver'] = self.edtEndDatePodtver.date()
        result['refuseType'] = self.cmbRefuseType.value()
        
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
