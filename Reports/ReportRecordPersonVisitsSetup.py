# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.database   import addDateInRange
from library.TreeModel  import CDBTreeModel
from library.Utils      import forceDate, forceInt, forceRef, forceString, getVal
from Orgs.Utils         import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventPurposeId = params.get('eventPurposeId', None)
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    rowGrouping = params.get('rowGrouping', 0)
    visitPayStatus = params.get('visitPayStatus', 0)
    visitPayStatus -= 1
    detailChildren = params.get('detailChildren', False)
    visitHospital = params.get('visitHospital', False)
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    socStatusClass = params.get('socStatusClass', 0)


    stmt = """
SELECT
    COUNT(*) as cnt,
    Visit.id as visit_id,
    rbSocStatusType.name as socStatus_name,
    rbSocStatusType.id as socStatus_id,
    (age(Client.birthDate, Visit.date)>=60) as age_flag,
    ClientWork_Hurt.id as hurt_id,
    Diagnosis.MKB as mkb,
    vrbPerson.id as person_id,
    vrbPerson.name as person_name,
    rbSpeciality.id as speciality_id,
    rbSpeciality.name as speciality_name,
    Visit.finance_id as finance_id,
    Visit.date as visit_date,
    EXISTS(
        SELECT v.`id`
        FROM `Visit` v
            LEFT JOIN `Event` e ON e.`id`=v.`event_id`
        WHERE `Visit`.`date`>v.`date`
            AND YEAR(v.`date`)=YEAR(CURRENT_TIMESTAMP)
            AND e.`client_id`=`Event`.`client_id`
            ) as thisYear_flag

FROM
    Visit
    LEFT JOIN Event ON Event.id = Visit.event_id
    LEFT JOIN EventType ON EventType.id = Event.eventType_id
    LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
    LEFT JOIN vrbPerson ON vrbPerson.id=Visit.person_id
    LEFT JOIN Client ON Client.id = Event.client_id
    LEFT JOIN rbScene ON rbScene.id=Visit.scene_id
    LEFT JOIN ClientSocStatus   ON ClientSocStatus.client_id = Client.id
    LEFT JOIN rbSocStatusType   ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
    LEFT JOIN ClientWork ON ClientWork.client_id = Client.id
    LEFT JOIN ClientWork_Hurt ON ClientWork_Hurt.master_id = ClientWork.Id
    LEFT JOIN Diagnostic ON (Diagnostic.event_id = Event.id AND Diagnostic.diagnosisType_id IN (1, 2))
    LEFT JOIN Diagnosis ON (Diagnosis.id = Diagnostic.diagnosis_id)
    LEFT JOIN rbSpeciality ON rbSpeciality.id=vrbPerson.speciality_id

WHERE
    rbEventTypePurpose.code != \'0\'
    AND Visit.deleted = 0
    AND Event.deleted = 0
    AND Client.deleted = 0
    AND (ClientSocStatus.deleted = 0 OR ClientSocStatus.id IS NULL) 
    AND Diagnostic.deleted = 0
    AND Diagnosis.deleted = 0
    AND (ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id AND CW.deleted = 0) OR ClientWork.id IS NULL)
    AND %s
GROUP BY
    socStatus_id,
    age_flag,
    hurt_id,
    mkb,
    speciality_id,
    person_id,
    finance_id,
    visit_date, visit_id

"""
    db = QtGui.qApp.db
    tablePerson = db.table('vrbPerson')
    tableVisit = db.table('Visit')

    cond = []
    addDateInRange(cond, tableVisit['date'], begDate, endDate)
    if eventTypeId:
        tableEvent = db.table('Event')
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        tableEventType = db.table('EventType')
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tableVisit['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if visitPayStatus >= 0:
        cond.append(u'getPayCode(Visit.finance_id, Visit.payStatus) = %d'%(visitPayStatus))
    if not visitHospital:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'7\')))''')
    if sex:
        tableClient = db.table('Client')
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if socStatusClass:
        tableClientSocStatus = db.table('ClientSocStatus')
        classes = [socStatusClass]
        newClasses = [socStatusClass]
        while newClasses:
            newClasses = getSubClasses(newClasses)
            classes += newClasses
        cond.append(tableClientSocStatus['socStatusClass_id'].inlist(classes))
    return db.query(stmt % (db.joinAnd(cond)))

def getSubClasses(classes):
    if len(classes)>0:
        return QtGui.qApp.db.getIdList('rbSocStatusClass', where = 'group_id IN (%s)' % (', '.join(str(v) for v in classes)))
    else:
        return []

class CReportRecordPersonVisits(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Ведомость учета врачебных посещений')


    def getSetupDialog(self, parent):
        result = CReportRecordPersonVisitsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        socStatusTypesDict = params.get('socStatusTypes', None)
        socStatusTypes = socStatusTypesDict.keys()
        db = QtGui.qApp.db

        financeNames   = []
        financeIndexes = {}
        for index, record in enumerate(db.getRecordList('rbFinance', 'id, name', '', 'code')):
            financeId = forceRef(record.value(0))
            financeName = forceString(record.value(1))
            financeIndexes[financeId] = index
            financeNames.append(financeName)
        if not(financeNames):
            financeNames.append(u'не определено')

        rowSize = 8 + len(financeNames)
        if socStatusTypes:
            rowSize += len(socStatusTypes)+1
        query = selectData(params)

        reportData = {}
        processedVisits = []
        processedVisitsBySocStatus = {}
        reportSummaryRow = [0]*rowSize
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            visit_id = forceInt(record.value('visit_id'))
            speciality_id = forceInt(record.value('speciality_id'))
            speciality_name = forceString(record.value('speciality_name'))
            person_id = forceInt(record.value('person_id'))
            person_name = forceString(record.value('person_name'))
            visit_date = forceDate(record.value('visit_date')).toPyDate()
            socStatus_name = forceString(record.value('socStatus_name'))
            socStatus_id = forceInt(record.value('socStatus_id'))
            count = forceInt(record.value('cnt'))
            age_flag = forceInt(record.value('age_flag'))
            hurt_id = forceInt(record.value('hurt_id'))
            mkb = forceString(record.value('mkb'))
            finance_id = forceInt(record.value('finance_id'))
            thisYear_flag = forceInt(record.value('thisYear_flag'))

            if not speciality_id in reportData.keys():
                reportData[speciality_id] = [speciality_name, {'resume':[0]*rowSize}]
            specialityDict = reportData[speciality_id][1]
            specialityResume = specialityDict['resume']
            if not person_id in specialityDict.keys():
                specialityDict[person_id] = [person_name, {'resume':[0]*rowSize}]
            personDict = specialityDict[person_id][1]
            personResume = personDict['resume']
            if not visit_date in personDict.keys():
                personDict[visit_date] = [0]*rowSize
            reportRow = personDict[visit_date]

            toCount = False if  visit_id in processedVisits else True

            if toCount:
                reportRow[2] += 1
                personResume[2] += 1
                specialityResume[2] += 1
                reportSummaryRow[2] += 1

            if socStatusTypes:
                if socStatus_id in socStatusTypes:
                    if not socStatus_id in processedVisitsBySocStatus:
                        processedVisitsBySocStatus[socStatus_id] = []
                    if not visit_id in processedVisitsBySocStatus[socStatus_id]:
                        processedVisitsBySocStatus[socStatus_id].append(visit_id)
                        index = socStatusTypes.index(socStatus_id) + 3
                        reportRow[index] += 1
                        personResume[index] += 1
                        specialityResume[index] += 1
                        reportSummaryRow[index] += 1
                elif toCount:
                    index = len(socStatusTypes) + 3
                    reportRow[index] += 1
                    personResume[index] += 1
                    specialityResume[index] += 1
                    reportSummaryRow[index] += 1

                if toCount:
                    if age_flag:
                        reportRow[5+len(socStatusTypes)] += 1
                        personResume[5+len(socStatusTypes)] += 1
                        specialityResume[5+len(socStatusTypes)] += 1
                        reportSummaryRow[5+len(socStatusTypes)] += 1

                    if thisYear_flag:
                        reportRow[6+len(socStatusTypes)] += 1
                        personResume[6+len(socStatusTypes)] += 1
                        specialityResume[6+len(socStatusTypes)] += 1
                        reportSummaryRow[6+len(socStatusTypes)] += 1

                    if hurt_id:
                        reportRow[4+len(socStatusTypes)] += 1
                        personResume[4+len(socStatusTypes)] += 1
                        specialityResume[4+len(socStatusTypes)] += 1
                        reportSummaryRow[4+len(socStatusTypes)] += 1

                    if mkb and mkb[0].upper() != 'Z':
                        reportRow[7+len(socStatusTypes)] += 1
                        personResume[7+len(socStatusTypes)] += 1
                        specialityResume[7+len(socStatusTypes)] += 1
                        reportSummaryRow[7+len(socStatusTypes)] += 1
                        if age_flag:
                            reportRow[8+len(socStatusTypes)] += 1
                            personResume[8+len(socStatusTypes)] += 1
                            specialityResume[8+len(socStatusTypes)] += 1
                            reportSummaryRow[8+len(socStatusTypes)] += 1

                    reportRow[9+len(socStatusTypes)+financeIndexes[finance_id]] += 1
                    personResume[9+len(socStatusTypes)+financeIndexes[finance_id]] += 1
                    specialityResume[9+len(socStatusTypes)+financeIndexes[finance_id]] += 1
                    reportSummaryRow[9+len(socStatusTypes)+financeIndexes[finance_id]] += 1
            else:
                if toCount:
                    if age_flag:
                        reportRow[4] += 1
                        personResume[4] += 1
                        specialityResume[4] += 1
                        reportSummaryRow[4] += 1
                    if thisYear_flag:
                        reportRow[5] += 1
                        personResume[5] += 1
                        specialityResume[5] += 1
                        reportSummaryRow[5] += 1
                    if hurt_id:
                        reportRow[3] += 1
                        personResume[3] += 1
                        specialityResume[3] += 1
                        reportSummaryRow[3] += 1
                    if mkb and mkb[0].upper() != 'Z':
                        reportRow[6] += 1
                        personResume[6] += 1
                        specialityResume[6] += 1
                        reportSummaryRow[6] += 1
                        if age_flag:
                            reportRow[7] += 1
                            personResume[7] += 1
                            specialityResume[7] += 1
                            reportSummaryRow[7] += 1
                    reportRow[8+financeIndexes[finance_id]] += 1
                    personResume[8+financeIndexes[finance_id]] += 1
                    specialityResume[8+financeIndexes[finance_id]] += 1
                    reportSummaryRow[8+financeIndexes[finance_id]] += 1

            if toCount:
                processedVisits.append(visit_id)
        # now text
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                        ('10%', [u'ФИО и должность врача',  u''], CReportBase.AlignLeft),
                        ('10%', [u'Дата', u''],  CReportBase.AlignLeft),
                        ('10%', [u'Число посещений в поликлинике', u'Всего посещений, из них:'], CReportBase.AlignRight)
                        ]
        if socStatusTypes:
            for socStatusType_id in socStatusTypes:
                tableColumns.append(('%f%%'%(20.0/len(socStatusTypes)), [u'', socStatusTypesDict[socStatusType_id]], CReportBase.AlignRight))
            tableColumns.append(('5%', [u'', u'Прочие'], CReportBase.AlignRight))

        restColumns = [
                       ('5%', [u'в том числе', u'Проф. вредн.'], CReportBase.AlignRight),
                       ('5%', [u'', u'в возрасте 60 лет и старше'], CReportBase.AlignRight),
                       ('5%', [u'', u'Впервые обратившихся'], CReportBase.AlignRight),
                       ('5%', [u'Из общего числа обращений по поводу заболеваний', u'Всего'], CReportBase.AlignRight),
                       ('5%', [u'', u'в т.ч. в возрасте 60 лет и старше'], CReportBase.AlignRight),
                       ]
        tableColumns = tableColumns + restColumns
        fnFirst = True
        for financeName in financeNames:
            if fnFirst:
                tableColumns.append(  ('4%', [u'Число посещений по видам оплаты', financeName], CReportBase.AlignRight) )
                fnFirst = False
            else:
                tableColumns.append(  ('4%', [u'', financeName], CReportBase.AlignRight) )

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        if socStatusTypes:
            shift = len(socStatusTypes) + 2
            table.mergeCells(0, 2, 1, shift)
            table.mergeCells(0, 2+shift, 1, 3)
            table.mergeCells(0, 5+shift, 1, 2)
            table.mergeCells(0, 7+shift, 1, len(financeNames))
        else:
            table.mergeCells(0, 3, 1, 3)
            table.mergeCells(0, 6, 1, 2)
            table.mergeCells(0, 8, 1, len(financeNames))

        reportDataKeys = reportData.keys()
        reportDataKeys.sort()
        for specKey in reportDataKeys:
            specName, specDict = reportData[specKey]
            i = table.addRow()
            table.setText(i, 0, specName, CReportBase.TableHeader)
            table.mergeCells(i, 0, 1, rowSize)
            specResume = specDict.pop('resume', 0)
            specDictKeys = specDict.keys()
            specDictKeys.sort()
            for personKey in specDictKeys:
                personName, personDict = specDict[personKey]
                personResume = personDict.pop('resume', 0)
                z = table.addRow()
                table.setText(z, 0, personName, CReportBase.TableHeader)
                personDictKeys = personDict.keys()
                personDictKeys.sort()
                for reportDate in personDictKeys:
                    reportRow = personDict[reportDate]
                    i = table.addRow()
                    table.setText(i, 1, reportDate.strftime('%d.%m.%Y'))
                    for j in range(2, rowSize):
                        table.setText(i, j, reportRow[j])
                table.mergeCells(z, 0, len(personDict.keys())+1, 1)
                table.mergeCells(z, 1, 1, rowSize-1)
                i = table.addRow()

                table.setText(i, 0, u'Итого по врачу', CReportBase.TableTotal)
                for j in range(2, rowSize):
                    table.setText(i, j, personResume[j], CReportBase.TableTotal)
            i = table.addRow()
            table.setText(i, 0, u'Итого по ' + specName, CReportBase.TableTotal)
            for j in range(2, rowSize):
                table.setText(i, j, specResume[j], CReportBase.TableTotal)
        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for j in range(2, rowSize):
            table.setText(i, j, reportSummaryRow[j], CReportBase.TableTotal)
        return doc


from Ui_ReportRecordPersonVisitsSetup import Ui_ReportRecordPersonVisitsSetupDialog


class CReportRecordPersonVisitsSetupDialog(QtGui.QDialog, Ui_ReportRecordPersonVisitsSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbVisitPayStatus.setCurrentIndex(0)
        treeModel = CDBTreeModel(self, 'rbSocStatusClass', 'id', 'group_id', 'name', ['code', 'name', 'id'])
        treeModel.setLeavesVisible(True)
        treeModel.setOrder('code')
        self.treeItems.setModel(treeModel)
        self.lstItems.setTable('vrbSocStatusType', 'class_id=1')
        self.socStatusClassId = 0


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))
        self.cmbVisitPayStatus.setCurrentIndex(params.get('visitPayStatus', 0))
        self.chkDetailChildren.setChecked(params.get('detailChildren', False))
        self.chkVisitHospital.setChecked(params.get('visitHospital', False))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        #self.lstItems.setValues(params.get('socStatusTypes', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['visitPayStatus'] = self.cmbVisitPayStatus.currentIndex()
        result['detailChildren'] = self.chkDetailChildren.isChecked()
        result['visitHospital'] = self.chkVisitHospital.isChecked()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['socStatusTypes'] = self.lstItems.nameValues()
        result['socStatusClass'] = self.socStatusClassId
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

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeItems_clicked(self,index):
        self.socStatusClassId = forceInt(self.treeItems.model().itemId(index))
        db = QtGui.qApp.db
        tbl = db.table('rbSocStatusType')
        tableAssoc = db.table('rbSocStatusClassTypeAssoc')
        cond = [tableAssoc['class_id'].eq(forceInt(self.treeItems.model().itemId(index)))]
        stmt = db.selectStmt(tableAssoc, tableAssoc['type_id'], cond)
        query = db.query(stmt)
        idList = []
        while query.next():
            idList.append(forceRef(query.record().value(0)))
        tbl3 = tbl.join(tableAssoc, [tableAssoc['type_id'].eq(tbl['id']), tableAssoc['class_id'].eq(forceInt(self.treeItems.model().itemId(index)))])
        self.lstItems.setTable('rbSocStatusType', tbl['id'].inlist(idList))
