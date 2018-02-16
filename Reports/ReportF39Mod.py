# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils               import getWorkEventTypeFilter
from library.database           import addDateInRange
from library.Utils              import forceBool, forceDate, forceInt, forceRef, forceString, getVal, pyDate
from Orgs.OrgStructComboBoxes   import COrgStructureModel
from Orgs.Utils                 import getOrgStructureDescendants
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase


def selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, personId, rowGrouping, visitPayStatus, visitHospital, sex, ageFrom, ageTo):
    stmt="""
SELECT
    COUNT(*) AS cnt,
    %s AS rowKey,
    EXISTS(SELECT kladr.KLADR.OCATD
    FROM ClientAddress
    INNER JOIN Address ON ClientAddress.address_id = Address.id
    INNER JOIN AddressHouse ON Address.house_id = AddressHouse.id
    INNER JOIN kladr.KLADR ON kladr.KLADR.CODE = AddressHouse.KLADRCode
    WHERE Client.id IS NOT NULL AND ClientAddress.client_id = Client.id AND (((SUBSTRING(kladr.KLADR.OCATD,3,1) IN (1, 2, 4)) AND SUBSTRING(kladr.KLADR.OCATD,6,1) = 8) OR ((SUBSTRING(kladr.KLADR.OCATD,3,1) NOT IN (1, 2, 4))
    AND SUBSTRING(kladr.KLADR.OCATD,6,1) = 9))) AS clientRural,
    IF(rbScene.code = '2' OR rbScene.code = '3',0,1)  AS atAmbulance,
    rbEventTypePurpose.code AS purpose,
    age(Client.birthDate, Visit.date) as clientAge,
    Visit.finance_id AS finance_id
FROM Visit
LEFT JOIN Event     ON Event.id = Visit.event_id
LEFT JOIN EventType ON EventType.id = Event.eventType_id
LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
LEFT JOIN Person    ON Person.id = Visit.person_id
LEFT JOIN Client    ON Client.id = Event.client_id
LEFT JOIN rbScene   ON rbScene.id = Visit.scene_id
WHERE rbEventTypePurpose.code != \'0\'
AND Visit.deleted=0
AND Event.deleted=0
AND %s
GROUP BY
    rowKey,
    clientRural,
    atAmbulance,
    purpose,
    clientAge,
    Visit.finance_id
    """
    db = QtGui.qApp.db
    tableVisit  = db.table('Visit')
    tableEvent  = db.table('Event')
    tableEventType = db.table('EventType')
    tablePerson = db.table('Person')
    tableClient = db.table('Client')
    cond = []
    addDateInRange(cond, tableVisit['date'], begDate, endDate)
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        tableEvent = db.table('Event')
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tableVisit['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if rowGrouping == 4: # by post_id
        groupField = 'Person.post_id'
    elif rowGrouping == 3: # by speciality_id
        groupField = 'Person.speciality_id'
    elif rowGrouping == 2: # by orgStructureId
        groupField = 'Person.orgStructure_id'
    elif rowGrouping == 1: # by personId
        groupField = 'Visit.person_id'
    else:
        groupField = 'DATE(Visit.date)'
    if visitPayStatus >= 0:
        cond.append(u'getPayCode(Visit.finance_id, Visit.payStatus) = %d'%(visitPayStatus))
    if not visitHospital:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'7\')))''')
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    return db.query(stmt % (groupField, db.joinAnd(cond)))


class CReportF39Mod(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Отчет по объемам медицинской помощи')


    def getSetupDialog(self, parent):
        result = CReportF39ModSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def calculateReportDataIfDetailaChildren(self, record, reportData, forceKeyVal, rowSize, financeIndexes):
        rowKey    = forceKeyVal(record.value('rowKey'))
        cnt       = forceInt(record.value('cnt'))
        atAmbulance = forceBool(record.value('atAmbulance'))
        purpose   = forceString(record.value('purpose'))
        age       = forceInt(record.value('clientAge'))
        financeId = forceInt(record.value('finance_id'))
        clientRural = forceInt(record.value('clientRural'))

        row = reportData.get(rowKey, None)
        if not row:
            row = [0]*rowSize
            reportData[rowKey] = row
        cure = purpose == '1'
        prophylaxy = purpose == '2'
        if atAmbulance:
            row[0] += cnt
            row[1] += clientRural
            if age<=1:
                row[2] += cnt
                row[4] += cnt
            elif age<=14:
                row[2] += cnt
            elif age>=15 and age<=17:
                row[3] += cnt
            elif age>=60:
                row[5] += cnt
            if cure:
                row[6] += cnt
                if age<=1:
                    row[7] += cnt
                    row[9] += cnt
                elif age<=14:
                    row[7] += cnt
                elif age>=15 and age<=17:
                    row[8] += cnt
                elif age>=60:
                    row[10] += cnt
            elif prophylaxy:
                row[11] += cnt
        else:
            row[12] += cnt
            if cure:
                row[13] += cnt
                if age<=1:
                    row[14] += cnt
                    row[16] += cnt
                elif age<=14:
                    row[14] += cnt
                elif age>=15 and age<=17:
                    row[15] += cnt
                elif age>=60:
                    row[17] += cnt
            elif prophylaxy:
                if age<=14:
                    row[18] += cnt
                    row[20] += cnt
                elif age>=15 and age<=17:
                    row[19] += cnt
                elif age<=1:
                    row[20] += cnt
        row[21+financeIndexes[financeId]] += cnt


    def calculateReportData(self, record, reportData, forceKeyVal, rowSize, financeIndexes):
        rowKey    = forceKeyVal(record.value('rowKey'))
        cnt       = forceInt(record.value('cnt'))
        atAmbulance = forceBool(record.value('atAmbulance'))
        purpose   = forceString(record.value('purpose'))
        age       = forceInt(record.value('clientAge'))
        financeId = forceInt(record.value('finance_id'))
        clientRural = forceInt(record.value('clientRural'))

        row = reportData.get(rowKey, None)
        if not row:
            row = [0]*rowSize
            reportData[rowKey] = row
        if age <= 17:
            row[0] += cnt
        else:
            row[1] += cnt


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        rowGrouping = params.get('rowGrouping', 0)
        visitPayStatus = params.get('visitPayStatus', 0)
        detailChildren = params.get('detailChildren', False)
        visitHospital = params.get('visitHospital', False)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        visitPayStatus -= 1
        if rowGrouping == 4: # by post_id
            postId = None
            forceKeyVal = forceRef
            keyValToString = lambda postId: forceString(QtGui.qApp.db.translate('rbPost', 'id', postId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Должность'
        elif rowGrouping == 3: # by speciality_id
            specialityId = None
            forceKeyVal = forceRef
            keyValToString = lambda specialityId: forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Специальность'
        elif rowGrouping == 2: # by orgStructureId
            forceKeyVal = forceRef
            keyValToString = None
            keyValToSort = None
            keyName = u'Подразделение'
        elif rowGrouping == 1: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Врач'
        else:
            forceKeyVal = lambda x: pyDate(forceDate(x))
            keyValToSort = None
            keyValToString = lambda x: forceString(QtCore.QDate(x))
            keyName = u'Дата'

        db = QtGui.qApp.db
        financeNames   = []
        financeIndexes = {}
        for index, record in enumerate(db.getRecordList('rbFinance', 'id, name', '', 'code')):
            financeId = forceRef(record.value(0))
            financeName = forceString(record.value(1))
            if financeName != u'ОМС': continue
            financeIndexes[financeId] = index
            financeNames.append(financeName)
        if not(financeNames):
            financeNames.append(u'не определено')

        rowSize = 21+len(financeNames) if detailChildren else 1+len(financeNames)
        query = selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, personId, rowGrouping, visitPayStatus, visitHospital, sex, ageFrom, ageTo)
        reportData = {}
        calculate = self.calculateReportDataIfDetailaChildren if detailChildren else self.calculateReportData
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            calculate(record, reportData, forceKeyVal, rowSize, financeIndexes)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '15%', [keyName],            CReportBase.AlignLeft),
            ( '10%',  [u'ОМС', u'дети'   ], CReportBase.AlignRight),
            ( '10%',  [u'',    u'взрос.' ], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        if detailChildren:
            self.mergeCellsIfDetailChildren(table, financeNames)
        else:
            self.mergeCells(table, financeNames)


#        prevSpecName = None
#        total = None
#        grandTotal = [0]*rowSize

        if rowGrouping == 2: # by orgStructureId
            self.genOrgStructureReport(table, reportData, rowSize, orgStructureId)
        else:
            keys = reportData.keys()
            if keyValToSort:
                keys.sort(key=keyValToSort)
            else:
                keys.sort()
            total = [0]*rowSize
            for key in keys:
                i = table.addRow()
                table.setText(i, 0, keyValToString(key))
                row = reportData[key]
                for j in xrange(rowSize):
                    table.setText(i, j+1, row[j])
                    total[j] += row[j]
            i = table.addRow()
            table.setText(i, 0, u'всего', CReportBase.TableTotal)
            for j in xrange(rowSize):
                table.setText(i, j+1, total[j], CReportBase.TableTotal)
        return doc

    def mergeCellsIfDetailChildren(self, table, financeNames):
        table.mergeCells(0, 0, 4, 1) # key
        table.mergeCells(0, 1, 1, 12) # Амбулаторно
        table.mergeCells(1, 1, 3, 1) # всего
        table.mergeCells(1, 2, 3, 1) # с.ж.
        table.mergeCells(1, 3, 2, 4) # в возрасте
        table.mergeCells(1, 7, 1, 5) # по забол.
        table.mergeCells(2, 7, 2, 1) # всего
        table.mergeCells(1, 12, 3, 1)# профилактических
        table.mergeCells(2, 8, 2, 1) # 0-14
        table.mergeCells(2, 9, 2, 1) # 15-17
        table.mergeCells(2, 10, 2, 1) # <=1
        table.mergeCells(2, 11, 2, 1) # >=60
        table.mergeCells(2, 15, 1, 4)# в т.ч. в возрасте
        table.mergeCells(2, 14, 2, 1)# Всего
        table.mergeCells(1, 14, 1, 5)# по поводу заболеваний
        table.mergeCells(0, 13, 1, 9) # на дому
        table.mergeCells(1, 13, 3, 1) # Всего
        table.mergeCells(1, 19, 1, 3) #
        table.mergeCells(2, 19, 2, 1) #
        table.mergeCells(2, 20, 2, 1) #
        table.mergeCells(2, 21, 2, 1) #

        for i in xrange(len(financeNames)):
            table.mergeCells(0, 22+i, 4, 1)

    def mergeCells(self, table, financeNames):
        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 1, 10)
        table.mergeCells(1, 1, 3, 1)
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(1, 3, 1, 3)

        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(2, 4, 2, 1)
        table.mergeCells(2, 5, 2, 1)

        table.mergeCells(1, 6, 1, 4)
        table.mergeCells(2, 6, 2, 1)
        table.mergeCells(2, 7, 2, 1)
        table.mergeCells(2, 8, 2, 1)
        table.mergeCells(2, 9, 2, 1)
        table.mergeCells(1, 10, 3, 1)

        table.mergeCells(0, 11, 1, 7)
        table.mergeCells(1, 11, 3, 1)
        table.mergeCells(1, 12, 1, 4)
        table.mergeCells(2, 12, 2, 1)
        table.mergeCells(2, 13, 1, 3)
        table.mergeCells(1, 16, 1, 2)
        table.mergeCells(2, 16, 2, 1)
        table.mergeCells(2, 17, 2, 1)

        for i in xrange(len(financeNames)):
            table.mergeCells(0,18+i, 4, 1)


    def genOrgStructureReport(self, table, reportData, rowSize, orgStructureId):
        model = COrgStructureModel(None, QtGui.qApp.currentOrgId())
        index = model.findItemId(orgStructureId)
        if index:
            item = index.internalPointer()
        else:
            item = model.getRootItem()
        self.genOrgStructureReportForItem(table, reportData, item, rowSize)


    def genOrgStructureReportForItem(self, table, reportData, item, rowSize):
        i = table.addRow()
        if item.childCount() == 0:
            table.setText(i, 0, item.name())
            row = reportData.get(item.id(), None)
            if row:
                for j in xrange(rowSize):
                    table.setText(i, j+1, row[j])
            return row
        else:
            table.mergeCells(i,0, 1, rowSize+1)
            table.setText(i, 0, item.name(), CReportBase.TableHeader)
            total = [0]*rowSize
            row = reportData.get(item.id(), None)
            if row:
                i = table.addRow()
                table.setText(i, 0, '-', CReportBase.TableHeader)
                for j in xrange(rowSize):
                    table.setText(i, j+1, row[j])
                    total[j] += row[j]
            for subitem in item.items():
                row = self.genOrgStructureReportForItem(table, reportData, subitem, rowSize)
                if row:
                    for j in xrange(rowSize):
                        total[j] += row[j]
            i = table.addRow()
            table.setText(i, 0, u'всего по '+item.name(), CReportBase.TableTotal)
            for j in xrange(rowSize):
                table.setText(i, j+1, total[j], CReportBase.TableTotal)
            return total


#    def produceTotalLine(self, table, title, total):
#        i = table.addRow()
#        table.setText(i, 0, title, CReportBase.TableTotal)
#        for j in xrange(len(total)):
#            table.setText(i, j+1, total[j], CReportBase.TableTotal)




from Ui_ReportF39ModSetup import Ui_ReportF39ModSetupDialog


class CReportF39ModSetupDialog(QtGui.QDialog, Ui_ReportF39ModSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.chkDetailChildren.setVisible(False)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbVisitPayStatus.setCurrentIndex(0)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))
        self.cmbRowGrouping.setCurrentIndex(getVal(params, 'rowGrouping', 0))
        self.cmbVisitPayStatus.setCurrentIndex(params.get('visitPayStatus', 0))
        self.chkDetailChildren.setChecked(params.get('detailChildren', False))
        self.chkVisitHospital.setChecked(params.get('visitHospital', False))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['rowGrouping'] = self.cmbRowGrouping.currentIndex()
        result['visitPayStatus'] = self.cmbVisitPayStatus.currentIndex()
        result['detailChildren'] = self.chkDetailChildren.isChecked()
        result['visitHospital'] = self.chkVisitHospital.isChecked()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)
