# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.ProgressBar    import CProgressBar
from library.Utils          import forceBool, forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants, getOrgStructureFullName, getOrgStructures
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase


def selectData(date, areaIdList, addressType):
    stmt="""
SELECT
    COUNT(*) AS cnt,
    age(Client.birthDate, %s) AS clientAge,
    Client.sex AS clientSex,
    ClientWork.org_id IS NOT NULL AND ClientWork.org_id != 0 AS busy
FROM Client
LEFT JOIN ClientAddress AS CAReg ON CAReg.client_id = Client.id
                        AND CAReg.id = (SELECT MAX(CARegInt.id) FROM ClientAddress AS CARegInt WHERE CARegInt.type=0 AND CARegInt.client_id=Client.id)
LEFT JOIN Address       AS AReg ON AReg.id = CAReg.address_id
LEFT JOIN ClientAddress AS CALoc ON CALoc.client_id = Client.id
                        AND CALoc.id = (SELECT MAX(CALocInt.id) FROM ClientAddress AS CALocInt WHERE CALocInt.type=1 AND CALocInt.client_id=Client.id)
LEFT JOIN Address       AS ALoc ON ALoc.id = CALoc.address_id
LEFT JOIN ClientAttach  ON ClientAttach.client_id = Client.id
                        AND ClientAttach.id = (SELECT MAX(CAT.id) FROM ClientAttach AS CAT
                                               LEFT JOIN rbAttachType ON rbAttachType.id=CAT.attachType_id
                                               WHERE CAT.deleted=0
                                               AND   CAT.client_id=Client.id
                                               AND   rbAttachType.temporary=0
                                              )
LEFT JOIN ClientWork    ON ClientWork.client_id = Client.id
                        AND ClientWork.id = (SELECT MAX(CW.id) FROM ClientWork AS CW WHERE CW.deleted=0 AND CW.client_id=Client.id)
LEFT JOIN rbAttachType ON rbAttachType.id=ClientAttach.attachType_id
WHERE
  %s
GROUP BY clientAge, clientSex, busy
    """
    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableAttachType = db.table('rbAttachType')

    cond = [ tableClient['deleted'].eq(0),
#             tableAttachType['outcome'].eq(0)
             db.joinOr( [tableAttachType['outcome'].eq(0), tableAttachType['id'].isNull()] )
           ]
    reg = (addressType+1) & 1
    loc = (addressType+1) & 2
    attach = (addressType+1) & 4
    condAddr = []
    if reg:
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableAddress = db.table('Address').alias('AReg')
        subCond = [ tableOrgStructureAddress['master_id'].inlist(areaIdList),
                    tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                  ]
        condAddr.append(db.existsStmt(tableOrgStructureAddress, subCond))
    if loc:
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableAddress = db.table('Address').alias('ALoc')
        subCond = [ tableOrgStructureAddress['master_id'].inlist(areaIdList),
                    tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                  ]
        condAddr.append(db.existsStmt(tableOrgStructureAddress, subCond))
    if attach:
        tableClientAttach = db.table('ClientAttach')
        condAddr.append(db.joinAnd([tableClientAttach['orgStructure_id'].inlist(areaIdList),
                                    tableClientAttach['deleted'].eq(0)
                                   ]))
    if condAddr:
        cond.append(db.joinOr(condAddr))
    return db.query(stmt % (tableClient['birthDate'].formatValue(date), db.joinAnd(cond)))


class CAttachedContingent(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Прикреплённый контингент')


    def getSetupDialog(self, parent):
        result = CAttachedContingentSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        areaId = params.get('areaId', None)
        endDate = params.get('endDate', QtCore.QDate())
        addressType = params.get('addressType', 0)
        isDetailByDepartment = params.get('detailByDepartment', False)
        isDetailByAge = params.get('detailByAge', False)
        
        rowNumber = [1]
        
        employableColBases = {  19 : 10,
                                24 : 12,
                                29 : 14,
                                34 : 16,
                                39 : 18,
                                44 : 20,
                                49 : 22,
                                54 : 24,
                                59 : 26,
                                64 : 28,
                                69 : 30,
                                74 : 32,
                                79 : 34
                                }
        #Количество столбцов с данными (за исключением столбцов "Категория населения", "№": 10 на детские возраста, 28 или 4 на взрослые и 1 на поле "Всего")
        reportRowSize = [39 if isDetailByAge else 15]

        def insertDataInTable(reportTable, reportData, charFormat = None):
            for rowIndex, rowName in enumerate([u'ИТОГО', u'работающие', u'неработающие']):
                i = reportTable.addRow()
                reportTable.setText(i, 0, rowName, charFormat = charFormat)
                reportTable.setText(i, 1, rowNumber[0], charFormat = charFormat)
                rowNumber[0] += 1
                for j in xrange(len(reportData[rowIndex])):
                    reportTable.setText(i, 2+j, reportData[rowIndex][j], charFormat = charFormat)
        #end insertDataInTable
        
        def getData(areaId, endDate, addressType, isDetailByAge = False):
            if areaId:
                areaIdList = getOrgStructureDescendants(areaId)
            else:
                areaIdList = getOrgStructures(QtGui.qApp.currentOrgId())
            
            query = selectData(endDate, areaIdList, addressType)
            
            
            reportData = [[0]*reportRowSize[0] for row in xrange(3)]
            self.setQueryText(forceString(query.lastQuery()))
            while query.next() :
                record = query.record()
                cnt    = forceInt(record.value('cnt'))
                age    = forceInt(record.value('clientAge'))
                sex    = forceInt(record.value('clientSex'))
                busy   = forceBool(record.value('busy'))
                if age < 1:
                    colBase = 0
                elif age == 1:
                    colBase = 2
                elif age <= 6:
                    colBase = 4
                elif age <= 14:
                    colBase = 6
                elif age <= 17:
                    colBase = 8
                else:
                    if isDetailByAge:
                        minAgeHigh = 150
                        colBase = 36
                        for ageHigh in employableColBases.keys():
                            if age <= ageHigh and ageHigh < minAgeHigh:
                                minAgeHigh = ageHigh
                                colBase = employableColBases[ageHigh]
                    else:
                        if (sex==1 and age < 60) or (sex != 1 and age < 55):
                            colBase = 10
                        else:
                            colBase = 12
                cols = [colBase+(0 if sex==1 else 1), reportRowSize[0] - 1]
                rows = [0, 1 if busy else 2]
                if cols[0] < 0 or cols[0] > reportRowSize[0] - 1:
                    print cols[0]
                for row in rows:
                    for col in cols:
                        reportData[row][col] += cnt
            return reportData
        #end getData
                    
        def detailByDepartment(reportTable, areaId, endDate, addressType, isDetailByAge, progressDialog = None):
            subAreaIdList = []
            db = QtGui.qApp.db
            tableOrgStructure = db.table('OrgStructure')
            whereCond = []
            if areaId: #Если указан отдельный участок или группа участков
                whereCond.append(tableOrgStructure['parent_id'].eq(areaId))
            else: #Если в качестве участка указан весь ЛПУ
                whereCond.append(tableOrgStructure['parent_id'].isNull())
                whereCond.append(tableOrgStructure['organisation_id'].eq(QtGui.qApp.currentOrgId()))
            
            subAreaIdList = db.getIdList(table = tableOrgStructure,
                                         where = whereCond)
            if subAreaIdList:
                for subAreaId in subAreaIdList:
                    row = reportTable.addRow()
                    reportTable.mergeCells(row, 0, 1, reportRowSize[0] + 3)
                    charFormat = QtGui.QTextCharFormat()
                    charFormat.setFontWeight(QtGui.QFont.Bold)
                    subAreaName = getOrgStructureFullName(subAreaId)
                    reportTable.setText(row, 0, subAreaName,
                                        charFormat = charFormat,
                                        blockFormat = CReportBase.AlignLeft)
                    if progressDialog:
                        progressDialog.setWindowTitle(u'Обработка %s' % subAreaName)
                        progressDialog.step()
                        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                    detailByDepartment(reportTable, subAreaId, endDate, addressType, isDetailByAge, progressDialog)
            else:
                insertDataInTable(reportTable, getData(areaId, endDate, addressType, isDetailByAge))
        #end detailByDepartment

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('15?', [u'Категории населения',   u''], CReportBase.AlignLeft),
            ( '5?', [u'№ стр.',                u''], CReportBase.AlignRight),
            ( '5?', [u'Численность прикреплённого населения по возрастному составу', u'дети', u'', u'до 1 года', u'М'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'', u'Ж'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'1 год', u'М'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'', u'Ж'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'2-6 лет', u'М'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'', u'Ж'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'7-14 лет', u'М'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'', u'Ж'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'15-17 лет', u'М'], CReportBase.AlignRight),
            ( '5?', [u'', u'', u'', u'', u'Ж'], CReportBase.AlignRight)]
        if isDetailByAge:
            ageHighKeys = employableColBases.keys()
            ageHighKeys.sort()
            for ageHigh in ageHighKeys:
                index = ageHighKeys.index(ageHigh)
                if index <= 0:
                    startAge = '18'
                else:
                    startAge = '%d' % (ageHighKeys[index - 1] + 1)
                ageRangeText = u'%s - %d лет' % (startAge, ageHigh)
                ageState = u'взрослые' if ageHigh == 19 else u''
                employableState = u'трудосп. возраста' if ageHigh == 59 else u''
                tableColumns.append(( '5?', [u'', ageState, employableState, ageRangeText, u'М'], CReportBase.AlignRight))
                employableState = u'нетрудосп. возраста' if ageHigh == 59 else u''
                tableColumns.append(( '5?', [u'', u'', employableState, u'', u'Ж'], CReportBase.AlignRight))
            tableColumns.append(( '5?', [u'', u'', u'', u'80 и ст.', u'М'], CReportBase.AlignRight))
            tableColumns.append(( '5?', [u'', u'', u'', u'', u'Ж'], CReportBase.AlignRight))
        else:
            tableColumns.append(( '5?', [u'', u'взрослые', u'трудосп. возраста', u'18-59 лет', u'М'], CReportBase.AlignRight))
            tableColumns.append(( '5?', [u'', u'', u'', u'18-54 лет', u'Ж'], CReportBase.AlignRight))
            tableColumns.append(( '5?', [u'', u'', u'нетрудосп. возраста', u'60 и ст.', u'М'], CReportBase.AlignRight))
            tableColumns.append(( '5?', [u'', u'', u'', u'55 и ст.', u'Ж'], CReportBase.AlignRight))
        
        tableColumns.append(( '5?', [u'Всего', ], CReportBase.AlignRight))


        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 4, 1) # Категории населения
        table.mergeCells(0, 1, 4, 1) # № стр.
        table.mergeCells(0, 2, 1, reportRowSize[0] - 1) # Численность...
        table.mergeCells(1, 2, 2, 10) # дети
        table.mergeCells(3, 2, 1, 2) # <1
        table.mergeCells(3, 4, 1, 2) # 1
        table.mergeCells(3, 6, 1, 2) # 2-6
        table.mergeCells(3, 8, 1, 2) # 7-14
        table.mergeCells(3,10, 1, 2) # 15-17
        if isDetailByAge:
            for i in xrange(27):
                table.mergeCells(3, 12 + i * 2, 1, 2)
                table.mergeCells(3, 12 + i * 2 + 1, 1, 2)
            table.mergeCells(1,12, 1, 28) # взрослые
            table.mergeCells(2,12, 1, 17) # тр.
            table.mergeCells(2,29, 1, 11) # нетр.
            table.mergeCells(0,40, 4, 1) # всего
        else:
            table.mergeCells(1,12, 1, 4) # взрослые
            table.mergeCells(2,12, 1, 2) # тр.
            table.mergeCells(2,14, 1, 2) # нетр.
            table.mergeCells(0,16, 4, 1) # всего
        
        reportData = getData(areaId, endDate, addressType, isDetailByAge)
        
        charFormat = None
        if isDetailByDepartment:
            if areaId:
                areaIdList = getOrgStructureDescendants(areaId)
            else:
                areaIdList = getOrgStructures(QtGui.qApp.currentOrgId())
            progressBar = CProgressBar() #QtGui.QProgressDialog(u'Обработка данных по участкам', 'Отмена', 0, len(areaIdList))
            progressBar.setMinimum(0)
            progressBar.setMaximum(len(areaIdList))
            parentCenter = QtGui.QDesktopWidget().availableGeometry().center()
            progressBar.setWindowFlags(progressBar.windowFlags() | QtCore.Qt.WindowCloseButtonHint)
            progressBar.setGeometry(parentCenter.x() - 250, parentCenter.y() - 40, 500, 80)
            progressBar.setText('%v/%m')
            progressBar.show()
            QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            
            detailByDepartment(table, areaId, endDate, addressType, isDetailByAge, progressBar)
            progressBar.hide()
            charFormat = QtGui.QTextCharFormat()
            charFormat.setFontWeight(QtGui.QFont.Bold)
            row = table.addRow()
            table.mergeCells(row, 0, 1, reportRowSize[0] + 3)
            table.setText(row, 0, getOrgStructureFullName(areaId),
                          charFormat = charFormat,
                          blockFormat = CReportBase.AlignLeft)
        insertDataInTable(table, reportData, charFormat = charFormat)

        return doc


from Ui_AttachedContingentSetup import Ui_AttachedContingentSetupDialog


class CAttachedContingentSetupDialog(QtGui.QDialog, Ui_AttachedContingentSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
#        self.chkDetailByAge.setVisible(False)


    def setPayPeriodVisible(self, value):
        pass


    def setWorkTypeVisible(self, value):
        pass


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setEventTypeVisible(self, visible=True):
        pass


    def setParams(self, params):
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('areaId', None))
        self.cmbAddressOrgStructureType.setCurrentIndex(params.get('addressType', 4))
        self.chkDetailByDepartment.setChecked(params.get('detailByDepartment', False))
        self.chkDetailByAge.setChecked(params.get('detailByAge', False))


    def params(self):
        result = {}
        result['endDate'] = self.edtEndDate.date()
        result['areaId'] = self.cmbOrgStructure.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['addressType'] = self.cmbAddressOrgStructureType.currentIndex()
        result['detailByDepartment'] = self.chkDetailByDepartment.isChecked()
        result['detailByAge'] = self.chkDetailByAge.isChecked()
        return result
