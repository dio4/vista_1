# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils                       import getWorkEventTypeFilter
from library.MapCode                    import createMapCodeToRowIdx
from library.Utils                      import forceDate, forceInt, forceRef, forceString, getVal
from Orgs.Utils                         import getOrgStructureDescendants, getOrgStructureFullName
from Reports.Report                     import CReport, normalizeMKB
from Reports.ReportBase                 import createTable, CReportBase

from Ui_StationaryF14DCSetup            import Ui_StationaryF14DCSetupDialog


TwoRows = [
          ( u'Всего', u'1', u'A00-T98'),
          ( u'Инфекционные и паразитарные болезни', u'2', u'A00-B99'),
          ( u'Новообразования', u'3', u'C00-C48'),
          ( u'Болезни крови и кроветворных органов', u'4', u'D50-D89'),
          ( u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'5', u'E00-E90'),
          ( u'Психические расстройства и расстройства поведения', u'6', u'F00-F99'),
          ( u'Болезни нервной системы', u'7', u'G00-G99'),
          ( u'Болезни глаза и его придаточного аппарата', u'8', u'H00-H59'),
          ( u'Болезни уха и сосцевидного отростка', u'9', u'H60-H95'),
          ( u'Болезни системы кровообращения', u'10', u'I00-I99'),
          ( u'Болезни органов дыхания', u'11', u'J00-J99'),
          ( u'Болезни органов пищеварения', u'12', u'K00-K93'),
          ( u'Болезни кожи и подкожной клетчатки', u'13', u'L00-L99'),
          ( u'Болезни костно-мышечной системы и соединительной ткани', u'14', u'M00-M99'),
          ( u'Болезни мочеполовой системы', u'15', u'N00-N99'),
          ( u'Беременность, роды и послеродовой период', u'16', u'O00-O99'),
          ( u'Отдельные состояния , возникающие в перинатальном периоде…', u'17', u'P00-P96'),
          ( u'Врождённые аномалии пороки развития', u'18', u'Q00-Q99'),
          ( u'Симптомы, признаки и отклонения от нормы', u'19', u'R00-R99'),
          ( u'Травмы, отравления', u'20', u'S00-T98'),
          ( u'Кроме того факторы, влияющие на состояние здоровья населения и обращения в учреждения здравоохранения', u'21', u'Z00-Z99'),
          ( u'Оперировано больных (числа выписанных и переведённых)', u'22', u''),
          ( u'Число проведённых операций', u'23', u'')
           ]


ThreeRows = [
          ( u'Всего', u'1', u'A00-T98'),
          ( u'Инфекционные и паразитарные болезни', u'2', u'A00-B99'),
          ( u'Новообразования', u'3', u'C00-C48'),
          ( u'Болезни крови и кроветворных органов', u'4', u'D50-D89'),
          ( u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'5', u'E00-E90'),
          ( u'Психические расстройства и расстройства поведения', u'6', u'F00-F99'),
          ( u'Болезни нервной системы', u'7', u'G00-G99'),
          ( u'Болезни глаза и его придаточного аппарата', u'8', u'H00-H59'),
          ( u'Болезни уха и сосцевидного отростка', u'9', u'H60-H95'),
          ( u'Болезни системы кровообращения', u'10', u'I00-I99'),
          ( u'Болезни органов дыхания', u'11', u'J00-J99'),
          ( u'Болезни органов пищеварения', u'12', u'K00-K93'),
          ( u'Болезни кожи и подкожной клетчатки', u'13', u'L00-L99'),
          ( u'Болезни костно-мышечной системы и соединительной ткани', u'14', u'M00-M99'),
          ( u'Болезни мочеполовой системы', u'15', u'N00-N99'),
          ( u'Беременность, роды и послеродовой период', u'16', u'O00-O99'),
          ( u'Отдельные состояния , возникающие в перинатальном периоде…', u'17', u'P00-P96'),
          ( u'Врождённые аномалии пороки развития', u'18', u'Q00-Q99'),
          ( u'Симптомы, признаки и отклонения от нормы', u'19', u'R00-R99'),
          ( u'Травмы, отравления', u'20', u'S00-T98'),
          ( u'Кроме того факторы, влияющие на состояние здоровья населения и обращения в учреждения здравоохранения', u'21', u'Z00-Z99'),
          ( u'Оперировано больных (числа выписанных и переведённых)', u'22', u''),
          ( u'Число проведённых операций', u'23', u'')
           ]


class CStationaryF14DCSetupDialog(QtGui.QDialog, Ui_StationaryF14DCSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbGroupMES.setTable('mes.mrbMESGroup', addNone=True)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbMes._popup.setCheckBoxes('stationaryF14DC')

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.chkGroupingForMES.setChecked(getVal(params, 'groupingForMES', False))
        self.cmbGroupMES.setValue(getVal(params, 'groupMES', None))
        self.cmbMes.setValue(getVal(params, 'MES', None))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbDurationType.setCurrentIndex(params.get('durationType', 0))


    def params(self):
        result = {}
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        if not (begDate and endDate):
            # Не знаю, зачем это сделано. Логика перенесена из отчетов, дабы не было путаницы.
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        result['durationType'] = self.cmbDurationType.currentIndex()
        result['begDate'] = begDate
        result['endDate'] = endDate
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['groupingForMES'] = self.chkGroupingForMES.isChecked()
        result['groupMES'] = self.cmbGroupMES.value()
        result['MES'] = self.cmbMes.value()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        return result


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()

    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


class CReportStationary(CReport):

    durationByVisits         = 0     # Длительность госпитализации считается по количеству посещений, попадающих в период
    durationByEventDays      = 1     #
    durationByEventWeekdays  = 2

    def __init__(self, parent = None):
        CReport.__init__(self, parent)
        self.clientDeath = 8


    def getSetupDialog(self, parent):
        result = CStationaryF14DCSetupDialog(parent)
        self.stationaryF14DCSetupDialog = result
        return result


    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []


    def dumpParams(self, cursor, params):
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result
        description = []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        if begDate and endDate:
            description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        orgStructureId = params.get('orgStructureId', None)
        if orgStructureId:
            description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        else:
            description.append(u'подразделение: ЛПУ')
        if params.get('groupingForMES', False):
            description.append(u'учитывать МЭС')
            groupMES = params.get('groupMES', None)
            if groupMES:
                description.append(u'Группа МЭС: %s'%(forceString(QtGui.qApp.db.translate('mes.mrbMESGroup', 'id', groupMES, 'name'))))
            MES = params.get('MES', None)
            if MES:
                description.append(u'МЭС: %s'%(forceString(QtGui.qApp.db.translate('mes.MES', 'id', MES, 'name'))))
        durationType = params.get('durationType', 0)
        if durationType == 0:
            description.append(u'Длительность по количеству посещений')
        elif durationType == 1:
            description.append(u'Длительность по количеству дней в событии')
        elif durationType == 2:
            description.append(u'Длительность по количеству рабочих дней в событии')
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def getDataEventHospital(self, orgStructureIdList, begDate, endDate, profileIdList, isHospital, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId):
        db = QtGui.qApp.db
        tableVisit = db.table('Visit')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableEventType = db.table('EventType')
        tableRBHBP = db.table('rbHospitalBedProfile')
        tableRBScene = db.table('rbScene')
        tablePerson = db.table('Person')
        tableOS = db.table('OrgStructure')
        tableMES = db.table('mes.MES')
        tableGroupMES = db.table('mes.mrbMESGroup')
        tableRBMedicalAidType = db.table('rbMedicalAidType')

        cond = [ tableEvent['deleted'].eq(0),
                 tablePerson['deleted'].eq(0),
                 tableEventType['deleted'].eq(0),
                 tableVisit['deleted'].eq(0)
               ]
        queryTable = tableEvent.innerJoin(tableVisit, tableVisit['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tablePerson, tableEvent['execPerson_id'].eq(tablePerson['id']))
        queryTable = queryTable.leftJoin(tableOS, tablePerson['orgStructure_id'].eq(tableOS['id']))
        queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        queryTable = queryTable.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        if groupingForMES:
            cond.append(tableEvent['MES_id'].isNotNull())
            if groupMES or MES:
                queryTable = queryTable.innerJoin(tableMES, tableEvent['MES_id'].eq(tableMES['id']))
                cond.append(tableMES['deleted'].eq(0))
                if MES:
                    cond.append(tableEvent['MES_id'].eq(MES))
                if groupMES:
                    queryTable = queryTable.innerJoin(tableGroupMES, tableMES['group_id'].eq(tableGroupMES['id']))
                    cond.append(tableGroupMES['deleted'].eq(0))
                    cond.append(tableMES['group_id'].eq(groupMES))
        if isHospital == 1:
            cond.append(tableEvent['execDate'].ge(begDate))
            cond.append(tableEvent['execDate'].le(endDate))
        else:
            joinOr1 = db.joinAnd([tableEvent['setDate'].isNull(), tableEvent['execDate'].isNull()])
            joinOr2 = db.joinAnd([tableEvent['setDate'].isNotNull(), tableEvent['setDate'].ge(begDate), tableEvent['setDate'].lt(endDate)])
            joinOr3 = db.joinAnd([tableEvent['setDate'].isNull(), tableEvent['execDate'].isNotNull(), tableEvent['execDate'].gt(begDate)])
            joinOr4 = db.joinAnd([tableEvent['setDate'].isNotNull(), tableEvent['setDate'].le(begDate), db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].gt(begDate)])])
            cond.append(db.joinOr([joinOr1, joinOr2, joinOr3, joinOr4]))
        cond.append(tableRBMedicalAidType['code'].eq(7))
        if eventTypeId:
            cond.append(tableEvent['eventType_id'].eq(eventTypeId))
        elif eventPurposeId:
            cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
        if orgStructureIdList:
            cond.append(tableOS['deleted'].eq(0))
            cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
        else:
            cond.append(u'(OrgStructure.id IS NULL OR OrgStructure.deleted = 0)')
        if isHospital == 0:
            cond.append(tableOS['type'].eq(1))
        elif isHospital == 1:
            queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
            cond.append(tableRBScene['code'].eq(1))
        elif isHospital == 2:
            queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
            cond.append(tableRBScene['code'].eq(2))
        if profileIdList:
            cond.append('''EXISTS(SELECT V.id FROM Visit AS V INNER JOIN rbHospitalBedProfile ON rbHospitalBedProfile.service_id = V.service_id WHERE rbHospitalBedProfile.id IN (%s) AND V.event_id = Event.id AND V.deleted = 0 AND V.id in (SELECT MIN(VMI.id) FROM Visit AS VMI WHERE VMI.event_id = Event.id AND VMI.deleted = 0 AND VMI.date = (SELECT MIN(VMD.date) FROM Visit AS VMD WHERE VMD.event_id = Event.id AND VMD.deleted = 0)))'''%(','.join(str(profileId) for profileId in profileIdList if profileId)))
        eventIdList = db.getDistinctIdList(queryTable, 'Event.id', cond, 'Event.id, Visit.date ASC')
        if eventIdList:
            stmtVisit = u'''SELECT
(SELECT RBHBP.id FROM rbHospitalBedProfile AS RBHBP INNER JOIN Visit AS V ON RBHBP.service_id = V.service_id WHERE V.event_id = Event.id
AND V.deleted = 0 AND V.id = (SELECT MIN(VMI.id) FROM Visit AS VMI WHERE VMI.event_id = Event.id AND VMI.deleted = 0
AND VMI.date = (SELECT MIN(VMD.date) FROM Visit AS VMD WHERE VMD.event_id = Event.id AND VMD.deleted = 0))) AS bedProfile,
(SELECT MIN(VIDMin.id) FROM Visit AS VIDMin WHERE VIDMin.event_id = Event.id AND VIDMin.deleted = 0
AND VIDMin.date = (SELECT MIN(V.date) FROM Visit AS V WHERE V.event_id = Event.id)) AS visitReceivedId,
(SELECT MIN(V.date) FROM Visit AS V WHERE V.event_id = Event.id AND V.deleted = 0) AS visitReceivedDate,
(SELECT MAX(VIDMax.id) FROM Visit AS VIDMax WHERE VIDMax.event_id = Event.id AND  VIDMax.deleted = 0
AND VIDMax.date = (SELECT MAX(V.date) FROM Visit AS V WHERE V.event_id = Event.id AND V.deleted = 0 AND Event.execDate IS NOT NULL)) AS visitLeavedId,
(SELECT MAX(V.date) FROM Visit AS V WHERE V.event_id = Event.id AND V.deleted = 0 AND Event.execDate IS NOT NULL) AS visitLeavedDate,
age(Client.birthDate, Event.setDate) AS ageClient,
EXISTS(SELECT rbResult.name FROM rbResult WHERE rbResult.id = Event.result_id AND rbResult.name LIKE '%%круглосуточный стационар%%') AS countTransfer,
(SELECT COUNT(VC.id) FROM Visit AS VC WHERE VC.event_id = Event.id AND VC.deleted = 0 AND (VC.date >= %s AND VC.date <= %s)) AS countVisit

FROM Event
INNER JOIN Visit ON Visit.event_id=Event.id
INNER JOIN Client ON Event.client_id=Client.id

WHERE (Event.deleted=0) AND (Client.deleted = 0) AND (Visit.deleted=0) AND Event.id IN (%s)

GROUP BY Event.id
ORDER BY Event.id, Visit.date ASC'''%(db.formatDate(begDate), db.formatDate(endDate), u','.join(str(eventId) for eventId in eventIdList if eventId))
            self.addQueryText(queryText=stmtVisit, queryDesc=u'DataEventHospital')
            return db.query(stmtVisit)
        return None


    def unrolledHospitalBedEvent(self, orgStructureIdList, begDate, endDate, reportLineList, profile = None):
        db = QtGui.qApp.db
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')
        queryTable = tableOSHB.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
        cond = [tableOSHB['master_id'].inlist(orgStructureIdList),
                tableOS['deleted'].eq(0)
                ]
        joinOr1 = db.joinOr([tableOSHB['begDate'].isNull(), tableOSHB['begDate'].ge(begDate)])
        joinOr2 = db.joinOr([tableOSHB['begDate'].isNull(), tableOSHB['begDate'].lt(endDate)])
        cond.append(db.joinAnd([joinOr1, joinOr2]))
        cond.append(tableOSHB['profile_id'].eq(profile))
        countBeds = db.getCount(queryTable, countCol='OrgStructure_HospitalBed.id', where=cond)
        reportLineAll = reportLineList.get('', None)
        if reportLineAll:
            reportLineAll['countBed'] += countBeds
            reportLineList[''] = reportLineAll
        reportLine = reportLineList.get(profile, None)
        if reportLine:
            reportLine['countBed'] += countBeds
            reportLineList[profile] = reportLine
        return reportLineList


    def averageDaysHospitalBedEvent(self, orgStructureIdList, begDatePeriod, endDatePeriod, profile = None):
        days = 0
        db = QtGui.qApp.db
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')
        queryTable = tableOSHB.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
        cond = [tableOSHB['master_id'].inlist(orgStructureIdList),
                tableOS['deleted'].eq(0)
                ]
        joinAnd = db.joinAnd([tableOSHB['endDate'].isNull(), db.joinOr([db.joinAnd([tableOSHB['begDate'].isNotNull(), tableOSHB['begDate'].lt(endDatePeriod)]), tableOSHB['begDate'].isNull()])])
        cond.append(db.joinOr([db.joinAnd([tableOSHB['endDate'].isNotNull(), tableOSHB['endDate'].gt(begDatePeriod), tableOSHB['begDate'].isNotNull(), tableOSHB['begDate'].lt(endDatePeriod)]), joinAnd]))
        cond.append(tableOSHB['profile_id'].eq(profile))
        stmt = db.selectStmt(queryTable, [tableOSHB['id'], tableOSHB['begDate'], tableOSHB['endDate'], tableOSHB['relief']], where=cond)
        self.addQueryText(queryText=stmt, queryDesc=u'averageDaysHospitalBedEvent')
        query = db.query(stmt)
        bedIdList = []
        while query.next():
            record = query.record()
            bedId = forceRef(record.value('id'))
            relief = forceInt(record.value('relief'))
            if bedId not in bedIdList:
                daysBed = 0
                bedIdList.append(bedId)
                begDate = forceDate(record.value('begDate'))
                endDate = forceDate(record.value('endDate'))
                if not begDate or begDate < begDatePeriod:
                    begDate = begDatePeriod
                if not endDate or endDate > endDatePeriod:
                    endDate = endDatePeriod
                if begDate and endDate:
                    if begDate == endDate:
                        daysBed = relief if relief else 1
                    else:
                        daysBed = begDate.daysTo(endDate) * relief if relief else begDate.daysTo(endDate)
                    days += daysBed
        return days


    def averageYarHospitalBedEvent(self, orgStructureIdList, begDate, endDate, reportLineList, profile = None):
        days = 0
        begDay = begDate.day()
        begMonth = begDate.month()
        begYear = begDate.year()
        begDatePeriod = QtCore.QDate(begYear, begMonth, 1)
        endDay = endDate.day()
        endMonth = endDate.month()
        endYear = endDate.year()
        endDatePeriod = begDatePeriod.addMonths(1)
        daysMonths = 0
        daysYears = 0
        while endDatePeriod.month() <= endMonth and endDatePeriod.year() <= endYear:
            days = self.averageDaysHospitalBedEvent(orgStructureIdList, begDatePeriod, endDatePeriod, profile)
            daysMonths += days / begDatePeriod.daysInMonth()
            begDatePeriod = begDatePeriod.addMonths(1)
            endDatePeriod = endDatePeriod.addMonths(1)
        daysYears = daysMonths / begDatePeriod.month()
        reportLineAll = reportLineList.get('', None)
        if reportLineAll:
            reportLineAll['countAverageBed'] += daysYears
            reportLineList[''] = reportLineAll
        reportLine = reportLineList.get(profile, None)
        if reportLine:
            reportLine['countAverageBed'] += daysYears
            reportLineList[profile] = reportLine
        return reportLineList


    def getDataEventAdult(self, params, orgStructureIdList, ageChildren, isHospital, ):
        db = QtGui.qApp.db
        tableVisit = db.table('Visit')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableEventType = db.table('EventType')
        tableRBScene = db.table('rbScene')
        tablePerson = db.table('Person')
        tableOS = db.table('OrgStructure')
        tableMES = db.table('mes.MES')
        tableGroupMES = db.table('mes.mrbMESGroup')
        tableRBMedicalAidType = db.table('rbMedicalAidType')

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        eventPurposeId = params.get('eventPurposeId', None)

        groupingForMES = params.get('groupingForMES', False)
        if groupingForMES:
            groupMES = params.get('groupMES', None)
            MES = params.get('MES', None)
        else:
            groupMES = None
            MES = None

        durationType = params.get('durationType', 0)

        cond = [ tableEvent['deleted'].eq(0),
                 tablePerson['deleted'].eq(0),
                 tableEventType['deleted'].eq(0),
                 tableVisit['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 #tableEvent['execDate'].isNotNull()   # Избыточно
               ]
        queryTable = tableEvent.innerJoin(tableVisit, tableVisit['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tablePerson, tableEvent['execPerson_id'].eq(tablePerson['id']))
        queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.leftJoin(tableOS, tablePerson['orgStructure_id'].eq(tableOS['id']))
        queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        queryTable = queryTable.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        if groupingForMES:
            cond.append(tableEvent['MES_id'].isNotNull())
            if groupMES or MES:
                queryTable = queryTable.innerJoin(tableMES, tableEvent['MES_id'].eq(tableMES['id']))
                cond.append(tableMES['deleted'].eq(0))
                if MES:
                    cond.append(tableEvent['MES_id'].eq(MES))
                if groupMES:
                    queryTable = queryTable.innerJoin(tableGroupMES, tableMES['group_id'].eq(tableGroupMES['id']))
                    cond.append(tableGroupMES['deleted'].eq(0))
                    cond.append(tableMES['group_id'].eq(groupMES))
        if isHospital == 1:
            cond.append(tableEvent['execDate'].dateLe(endDate))
            cond.append(tableEvent['execDate'].dateGe(begDate))
        else:
            cond.append(tableEvent['setDate'].dateLe(endDate))
            cond.append(tableEvent['execDate'].dateGt(begDate))
        cond.append(tableRBMedicalAidType['code'].eq(7))
        if eventTypeId:
            cond.append(tableEvent['eventType_id'].eq(eventTypeId))
        elif eventPurposeId:
            cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
        if orgStructureIdList:
            cond.append(tableOS['deleted'].eq(0))
            cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
        else:
            cond.append(u'(OrgStructure.id IS NULL OR OrgStructure.deleted = 0)')
        if isHospital == 0:
            cond.append(tableOS['type'].eq(1))
        elif isHospital == 1:
            queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
            cond.append(tableRBScene['code'].eq(1))
        elif isHospital == 2:
            queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
            cond.append(tableRBScene['code'].eq(2))
        cond.append(ageChildren)
        eventIdList = db.getDistinctIdList(queryTable, 'Event.id', cond, 'Event.id, Visit.date ASC')
        if eventIdList:
            durationCond = '1'
            if durationType == CReportStationary.durationByVisits:
                durationCond = u'''(SELECT COUNT(VC.id) FROM Visit AS VC WHERE VC.event_id = Event.id AND Event.execDate IS NOT NULL AND VC.deleted = 0
AND (VC.date >= %s AND VC.date <= %s)) AS countVisit''' % (db.formatDate(begDate), db.formatDate(endDate))
            elif durationType == CReportStationary.durationByEventDays:
                durationCond = u'''DATEDIFF(LEAST(Event.execDate, %(endDate)s), GREATEST(Event.setDate, %(begDate)s)) + 1 as countVisit''' % {'begDate': db.formatDate(begDate),
                                                                                                                                       'endDate': db.formatDate(endDate)}
            elif durationType == CReportStationary.durationByEventWeekdays:
                durationCond = u'''5 * (DATEDIFF(LEAST(Event.execDate, %(endDate)s), GREATEST(Event.setDate, %(begDate)s)) DIV 7) + MID('0123444401233334012222340111123400001234000123440', 7 * WEEKDAY(GREATEST(Event.setDate, %(begDate)s)) + WEEKDAY(LEAST(Event.execDate, %(endDate)s)) + 1, 1) + IF(WEEKDAY(LEAST(Event.execDate, %(endDate)s)) > 4 AND WEEKDAY(GREATEST(Event.setDate, %(begDate)s)) > 4, 0, 1)
                 as countVisit''' % {'begDate': db.formatDate(begDate),
                                                                                                                                       'endDate': db.formatDate(endDate)}

            stmtVisit = u'''SELECT Diagnosis.MKB,
(SELECT MAX(V.date) FROM Visit AS V WHERE V.event_id = Event.id AND V.deleted = 0 AND Event.execDate IS NOT NULL) AS visitLeavedDate,
EXISTS(SELECT rbResult.name FROM rbResult WHERE rbResult.id = Event.result_id AND rbResult.name LIKE '%%круглосуточный стационар%%') AS countTransfer,
EXISTS(SELECT rbResult.name FROM rbResult WHERE rbResult.id = Event.result_id
AND (rbResult.code = 99 OR rbResult.name LIKE '%%умер%%' OR rbResult.name LIKE '%%смерть%%')) AS countDeath,
%(durationCond)s,
(SELECT count(DISTINCT A.id)
FROM Action AS A INNER JOIN ActionType AS AT ON A.actionType_id = AT.id
WHERE A.event_id = Event.id AND A.deleted = 0 AND AT.deleted = 0 AND A.endDate IS NOT NULL AND AT.class IN (2, 3)
AND (AT.code LIKE '1-2' OR AT.code LIKE 'А16%%' OR AT.code LIKE '6%%' OR AT.code LIKE 'о%%')) AS countSurgery

FROM Event
INNER JOIN Visit ON Visit.event_id=Event.id
INNER JOIN Client ON Event.client_id=Client.id
INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id

WHERE (Event.deleted=0) AND (Client.deleted = 0) AND (Visit.deleted=0) AND Event.id IN (%(eventList)s) AND (rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id
AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id
WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1))))

GROUP BY Event.id
ORDER BY Event.id, Visit.date ASC'''%{'durationCond': durationCond,
                                      'eventList': u','.join(str(eventId) for eventId in eventIdList if eventId)}
            #print stmtVisit
            self.addQueryText(queryText=stmtVisit, queryDesc=u'DataEventAdult')
            return db.query(stmtVisit)
        return None

    def selectFinanceData(self, begDate, endDate, orgStructureId, groupingForMES, eventPurposeId, eventTypeId, groupMES, MES):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableEventType = db.table('EventType')
        tablePerson = db.table('Person')
        tableOS = db.table('OrgStructure')
        tableMES = db.table('mes.MES')
        tableGroupMES = db.table('mes.mrbMESGroup')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        cond  = [tableEvent['execDate'].dateGe(begDate),
                 tableEvent['execDate'].dateLe(endDate),
                 tableEvent['deleted'].eq(0),
                 tableEventType['deleted'].eq(0),
                 tableClient['deleted'].eq(0)
               ]

        queryTable = tableEvent.innerJoin(tablePerson, tableEvent['execPerson_id'].eq(tablePerson['id']))
        queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.leftJoin(tableOS, tablePerson['orgStructure_id'].eq(tableOS['id']))
        queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        queryTable = queryTable.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))

        if groupingForMES:
            cond.append(tableEvent['MES_id'].isNotNull())
            if groupMES or MES:
                queryTable = queryTable.innerJoin(tableMES, tableEvent['MES_id'].eq(tableMES['id']))
                cond.append(tableMES['deleted'].eq(0))
                if MES:
                    cond.append(tableEvent['MES_id'].eq(MES))
                if groupMES:
                    queryTable = queryTable.innerJoin(tableGroupMES, tableMES['group_id'].eq(tableGroupMES['id']))
                    cond.append(tableGroupMES['deleted'].eq(0))
                    cond.append(tableMES['group_id'].eq(groupMES))
        cond.append(tableRBMedicalAidType['code'].eq(7))
        if eventTypeId:
            cond.append(tableEvent['eventType_id'].eq(eventTypeId))
        elif eventPurposeId:
            cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
        if orgStructureId:
            cond.append(tableOS['deleted'].eq(0))
            cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
        else:
            cond.append(u'(OrgStructure.id IS NULL OR OrgStructure.deleted = 0)')
        # if isHospital == 0:
        #     cond.append(tableOS['type'].eq(1))
        # elif isHospital == 1:
        #     queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
        #     cond.append(tableRBScene['code'].eq(1))
        # elif isHospital == 2:
        #     queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
        #     cond.append(tableRBScene['code'].eq(2))
        eventIdList = db.getDistinctIdList(queryTable, 'Event.id', cond, 'Event.id')
        if eventIdList:
            stmtVisit = u'''SELECT rbFinance.name
                            , count(Event.id) AS countLeaved
                            , sum(DATEDIFF(Event.execDate, Event.setDate) + 1) AS countDays

                            FROM
                                Event
                                INNER JOIN Client ON Event.client_id=Client.id
                                INNER JOIN Contract ON Contract.id = Event.contract_id
                                LEFT JOIN rbFinance ON rbFinance.id = Contract.finance_id
                            WHERE
                                Event.id IN (%s)
                                AND (Event.deleted=0)
                                AND (Client.deleted = 0)
                                AND Contract.deleted = 0
                            GROUP BY
                                rbFinance.id''' % (u','.join(str(eventId) for eventId in eventIdList if eventId))
            self.addQueryText(queryText=stmtVisit, queryDesc=u'FinanceData')
            return db.query(stmtVisit)
        return None

class CStationaryOneF14DC(CReportStationary):#actOneForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Общий.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        orgStructureId = getVal(params, 'orgStructureId', None)
        groupingForMES = getVal(params, 'groupingForMES', False)
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        if groupingForMES:
            groupMES = getVal(params, 'groupMES', None)
            MES = getVal(params, 'MES', None)
        else:
            groupMES = None
            MES = None
        doc = QtGui.QTextDocument()
        if (not begDate) or (not endDate):
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Раздел I. Использование коечного фонда\n(1100)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('3%',[u'№стр.', u'', u'1'], CReportBase.AlignRight),
                    ('7.7%',[u'Профили коек.', u'', u'2'], CReportBase.AlignLeft),
                    ('4.7%', [u'Дневной стационар при больничном учреждении', u'Число мест', u'3'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'число среднегодовых мест', u'4'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'поступило больных', u'5'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'выписано', u'6'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'из них детей (0-17 лет)', '7'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'в т.ч. круглосуточный стационар(из г.6)', u'8'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'проведено больными дней лечения', u'9'], CReportBase.AlignRight),

                    ('4.7%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'Число мест', u'10'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'число среднегодовых мест', u'11'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'поступило больных', u'12'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'выписано', u'13'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'из них детей (0-17 лет)', '14'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'в т.ч. круглосуточный стационар(из г.13)', u'15'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'проведено больными дней лечения', u'16'], CReportBase.AlignRight),

                    ('4.7%', [u'Стационар на дому', u'Число мест', u'17'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'выписано', u'18'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'из них детей (0-17 лет)', '19'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'в т.ч. круглосуточный стационар(из г.18)', u'20'], CReportBase.AlignRight),
                    ('4.7%', [u'', u'проведено больными дней лечения', u'21'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 7)  # Дневной стационар при больничном учреждении
            table.mergeCells(0, 9, 1, 7)  # Дневной стационар при амбулаторно-поликлинических учреждениях
            table.mergeCells(0, 16, 1, 5) # Стационар на дому
            reportLineList, bedProfileIdList, rowProfileIdList = self.getProfileIdList(table)
            self.fillReportTable(orgStructureIdList, begDate, endDate, table, 2, 0, bedProfileIdList, reportLineList, rowProfileIdList, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId)
            self.fillReportTable(orgStructureIdList, begDate, endDate, table, 9, 1, bedProfileIdList, reportLineList, rowProfileIdList, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId)
            self.fillReportTable(orgStructureIdList, begDate, endDate, table, 16, 2, bedProfileIdList, reportLineList, rowProfileIdList, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId)
        return doc


    def getProfileIdList(self, table):
        db = QtGui.qApp.db
        bedProfileRecords = db.getRecordList('rbHospitalBedProfile', 'id, code, name')
        reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}}
        rowProfileIdList = {}
        bedProfileIdList = []
        rowProfile = table.addRow()
        rowProfileIdList[''] = rowProfile
        cnt = 1
        table.setText(rowProfile, 0, cnt)
        table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
        for bedProfileRecord in bedProfileRecords:
            profileId = forceRef(bedProfileRecord.value('id'))
            code = forceString(bedProfileRecord.value('code'))
            name = forceString(bedProfileRecord.value('name'))
            if profileId not in bedProfileIdList:
                bedProfileIdList.append(profileId)
            if not reportLineList.get(profileId, None):
                reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                reportLine['code'] = code
                reportLine['name'] = name
                reportLineList[profileId] = reportLine
                cnt += 1
                rowProfile = table.addRow()
                rowProfileIdList[profileId] = rowProfile
                table.setText(rowProfile, 0, cnt)
                table.setText(rowProfile, 1, reportLine['name'])
        return reportLineList, bedProfileIdList, rowProfileIdList


    def fillReportTable(self, orgStructureIdList, begDate, endDate, table, cols, isHospital, bedProfileIdList, reportLineList, rowProfileIdList, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId):
        db = QtGui.qApp.db
        tableRBHospitalBedProfile = db.table('rbHospitalBedProfile')
        for profileId in bedProfileIdList:
            reportLineList = self.unrolledHospitalBedEvent(orgStructureIdList, begDate, endDate, reportLineList, profileId)
            if isHospital != 2:
                reportLineList = self.averageYarHospitalBedEvent(orgStructureIdList, begDate, endDate, reportLineList, profileId)
        records = self.getDataEventHospital(orgStructureIdList, begDate, endDate, bedProfileIdList, isHospital, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId)
        if records:
            while records.next():
                record = records.record()
                profileId = forceRef(record.value('bedProfile'))
                reportLine = reportLineList.get(profileId, None)
                reportLineAll = reportLineList.get('', None)
                if not reportLine:
                    bedRepRecord = db.getRecordEx(tableRBHospitalBedProfile, [tableRBHospitalBedProfile['code'], tableRBHospitalBedProfile['name']], [tableRBHospitalBedProfile['id'].eq(profileId)])
                    if bedRepRecord:
                        code = forceString(bedRepRecord.value('code'))
                        name = forceString(bedRepRecord.value('name'))
                        reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                        reportLine['code'] = code
                        reportLine['name'] = name
                if reportLine:
                    visitReceivedId = forceRef(record.value('visitReceivedId'))
                    visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                    if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                        reportLine['visitReceived'] += 1
                        reportLineAll['visitReceived'] += 1
                    visitLeavedId = forceRef(record.value('visitLeavedId'))
                    visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                    if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                        reportLine['visitLeaved'] += 1
                        reportLineAll['visitLeaved'] += 1
                    ageClient = forceInt(record.value('ageClient'))
                    if ageClient <= 17:
                        reportLine['ageChildren'] += 1
                        reportLineAll['ageChildren'] += 1
                    countTransfer = forceInt(record.value('countTransfer'))
                    countVisit = forceInt(record.value('countVisit'))
                    reportLine['countTransfer'] += countTransfer
                    reportLine['countVisit'] += countVisit
                    reportLineAll['countTransfer'] += countTransfer
                    reportLineAll['countVisit'] += countVisit
                    reportLineList[profileId] = reportLine
                    reportLineList[''] = reportLineAll
        reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
        rowAll = rowProfileIdList.get('', None)
        if isHospital != 2:
            table.setText(rowAll, cols, reportLine['countBed'])
            table.setText(rowAll, cols+1, reportLine['countAverageBed'])
            table.setText(rowAll, cols+2, reportLine['visitReceived'])
            table.setText(rowAll, cols+3, reportLine['visitLeaved'])
            table.setText(rowAll, cols+4, reportLine['ageChildren'])
            table.setText(rowAll, cols+5, reportLine['countTransfer'])
            table.setText(rowAll, cols+6, reportLine['countVisit'])
            if reportLineList.get('', None):
                del reportLineList['']
            for key, reportLine in reportLineList.items():
                rowProfile = rowProfileIdList.get(key, None)
                table.setText(rowProfile, cols, reportLine['countBed'])
                table.setText(rowProfile, cols+1, reportLine['countAverageBed'])
                table.setText(rowProfile, cols+2, reportLine['visitReceived'])
                table.setText(rowProfile, cols+3, reportLine['visitLeaved'])
                table.setText(rowProfile, cols+4, reportLine['ageChildren'])
                table.setText(rowProfile, cols+5, reportLine['countTransfer'])
                table.setText(rowProfile, cols+6, reportLine['countVisit'])
                reportLine['countBed'] = 0
                reportLine['countAverageBed'] = 0
                reportLine['visitReceived'] = 0
                reportLine['visitLeaved'] = 0
                reportLine['ageChildren'] = 0
                reportLine['countTransfer'] = 0
                reportLine['countVisit'] = 0
                reportLineList[key] = reportLine
        else:
            table.setText(rowAll, cols, reportLine['countBed'])
            table.setText(rowAll, cols+1, reportLine['visitLeaved'])
            table.setText(rowAll, cols+2, reportLine['ageChildren'])
            table.setText(rowAll, cols+3, reportLine['countTransfer'])
            table.setText(rowAll, cols+4, reportLine['countVisit'])
            if reportLineList.get('', None):
                del reportLineList['']
            for key, reportLine in reportLineList.items():
                rowProfile = rowProfileIdList.get(key, None)
                table.setText(rowProfile, cols, reportLine['countBed'])
                table.setText(rowProfile, cols+1, reportLine['visitLeaved'])
                table.setText(rowProfile, cols+2, reportLine['ageChildren'])
                table.setText(rowProfile, cols+3, reportLine['countTransfer'])
                table.setText(rowProfile, cols+4, reportLine['countVisit'])
                reportLine['countBed'] = 0
                reportLine['visitLeaved'] = 0
                reportLine['ageChildren'] = 0
                reportLine['countTransfer'] = 0
                reportLine['countVisit'] = 0
                reportLineList[key] = reportLine
        if not reportLineList.get('', None):
            reportLineList[''] = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}


class CStationaryOneHospitalF14DC(CReportStationary):#actOneForma14DC CStationaryOnePolyclinicF14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Дневной стационар при больничном учреждении.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        groupingForMES = getVal(params, 'groupingForMES', False)
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        if groupingForMES:
            groupMES = getVal(params, 'groupMES', None)
            MES = getVal(params, 'MES', None)
        else:
            groupMES = None
            MES = None
        doc = QtGui.QTextDocument()
        if (not begDate) or (not endDate):
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Раздел I. Использование коечного фонда\n(1100)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('4%',[u'№стр.', u'', u'1'], CReportBase.AlignRight),
                    ('19%',[u'Профили коек.', u'', u'2'], CReportBase.AlignLeft),
                    ('11%', [u'Дневной стационар при больничном учреждении', u'Число мест', u'3'], CReportBase.AlignRight),
                    ('11%', [u'', u'число среднегодовых мест', u'4'], CReportBase.AlignRight),
                    ('11%', [u'', u'поступило больных', u'5'], CReportBase.AlignRight),
                    ('11%', [u'', u'выписано', u'6'], CReportBase.AlignRight),
                    ('11%', [u'', u'из них детей (0-17 лет)', '7'], CReportBase.AlignRight),
                    ('11%', [u'', u'в т.ч. круглосуточный стационар(из г.6)', u'8'], CReportBase.AlignRight),
                    ('11%', [u'', u'проведено больными дней лечения', u'9'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 7)  # Дневной стационар при больничном учреждении
            tableRBHospitalBedProfile = db.table('rbHospitalBedProfile')
            bedProfileRecords = db.getRecordList('rbHospitalBedProfile', 'id, code, name')
            reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}}
            bedProfileIdList = []
            for bedProfileRecord in bedProfileRecords:
                profileId = forceRef(bedProfileRecord.value('id'))
                if profileId not in bedProfileIdList:
                    bedProfileIdList.append(profileId)
                if not reportLineList.get(profileId, None):
                    reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                    reportLine['code'] = forceString(bedProfileRecord.value('code'))
                    reportLine['name'] = forceString(bedProfileRecord.value('name'))
                    reportLineList[profileId] = reportLine

                reportLineList = self.unrolledHospitalBedEvent(orgStructureIdList, begDate, endDate, reportLineList, profileId)
                reportLineList = self.averageYarHospitalBedEvent(orgStructureIdList, begDate, endDate, reportLineList, profileId)
            records = self.getDataEventHospital(orgStructureIdList, begDate, endDate, bedProfileIdList, 0, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId)
            if records:
                while records.next():
                    record = records.record()
                    profileId = forceRef(record.value('bedProfile'))
                    reportLine = reportLineList.get(profileId, None)
                    reportLineAll = reportLineList.get('', None)
                    if not reportLine:
                        bedRepRecord = db.getRecordEx(tableRBHospitalBedProfile, [tableRBHospitalBedProfile['code'], tableRBHospitalBedProfile['name']], [tableRBHospitalBedProfile['id'].eq(profileId)])
                        if bedRepRecord:
                            code = forceString(bedRepRecord.value('code'))
                            name = forceString(bedRepRecord.value('name'))
                            reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                            reportLine['code'] = forceString(bedProfileRecord.value('code'))
                            reportLine['name'] = forceString(bedProfileRecord.value('name'))
                    if reportLine:
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLine['visitReceived'] += 1
                            reportLineAll['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLine['visitLeaved'] += 1
                            reportLineAll['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLine['ageChildren'] += 1
                            reportLineAll['ageChildren'] += 1
                        countTransfer = forceInt(record.value('countTransfer'))
                        countVisit = forceInt(record.value('countVisit'))
                        reportLine['countTransfer'] += countTransfer
                        reportLine['countVisit'] += countVisit
                        reportLineAll['countTransfer'] += countTransfer
                        reportLineAll['countVisit'] += countVisit
                        reportLineList[profileId] = reportLine
                        reportLineList[''] = reportLineAll
            cnt = 1
            rowProfile = table.addRow()
            reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            table.setText(rowProfile, 0, cnt)
            table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
            table.setText(rowProfile, 2, reportLine['countBed'])
            table.setText(rowProfile, 3, reportLine['countAverageBed'])
            table.setText(rowProfile, 4, reportLine['visitReceived'])
            table.setText(rowProfile, 5, reportLine['visitLeaved'])
            table.setText(rowProfile, 6, reportLine['ageChildren'])
            table.setText(rowProfile, 7, reportLine['countTransfer'])
            table.setText(rowProfile, 8, reportLine['countVisit'])
            if reportLineList.get('', None):
                del reportLineList['']
            for key, reportLine in reportLineList.items():
                rowProfile = table.addRow()
                cnt += 1
                table.setText(rowProfile, 0, cnt)
                table.setText(rowProfile, 1, reportLine['name'])
                table.setText(rowProfile, 2, reportLine['countBed'])
                table.setText(rowProfile, 3, reportLine['countAverageBed'])
                table.setText(rowProfile, 4, reportLine['visitReceived'])
                table.setText(rowProfile, 5, reportLine['visitLeaved'])
                table.setText(rowProfile, 6, reportLine['ageChildren'])
                table.setText(rowProfile, 7, reportLine['countTransfer'])
                table.setText(rowProfile, 8, reportLine['countVisit'])
        return doc


class CStationaryOnePolyclinicF14DC(CReportStationary):#actOneForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Дневной стационар при амбулаторно-поликлинических учреждениях.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        groupingForMES = getVal(params, 'groupingForMES', False)
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        if groupingForMES:
            groupMES = getVal(params, 'groupMES', None)
            MES = getVal(params, 'MES', None)
        else:
            groupMES = None
            MES = None
        doc = QtGui.QTextDocument()
        if (not begDate) or (not endDate):
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Раздел I. Использование коечного фонда\n(1100)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('4%',[u'№стр.', u'', u'1'], CReportBase.AlignRight),
                    ('19%',[u'Профили коек.', u'', u'2'], CReportBase.AlignLeft),
                    ('11%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'Число мест', u'3'], CReportBase.AlignRight),
                    ('11%', [u'', u'число среднегодовых мест', u'4'], CReportBase.AlignRight),
                    ('11%', [u'', u'поступило больных', u'5'], CReportBase.AlignRight),
                    ('11%', [u'', u'выписано', u'6'], CReportBase.AlignRight),
                    ('11%', [u'', u'из них детей (0-17 лет)', '7'], CReportBase.AlignRight),
                    ('11%', [u'', u'в т.ч. круглосуточный стационар(из г.6)', u'8'], CReportBase.AlignRight),
                    ('11%', [u'', u'проведено больными дней лечения', u'9'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 7)  # Дневной стационар при амбулаторно-поликлинических учреждениях
            tableRBHospitalBedProfile = db.table('rbHospitalBedProfile')
            bedProfileRecords = db.getRecordList('rbHospitalBedProfile', 'id, code, name')
            reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}}
            bedProfileIdList = []
            for bedProfileRecord in bedProfileRecords:
                profileId = forceRef(bedProfileRecord.value('id'))
                if profileId not in bedProfileIdList:
                    bedProfileIdList.append(profileId)
                if not reportLineList.get(profileId, None):
                    reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                    reportLine['code'] = forceString(bedProfileRecord.value('code'))
                    reportLine['name'] = forceString(bedProfileRecord.value('name'))
                    reportLineList[profileId] = reportLine

                reportLineList = self.unrolledHospitalBedEvent(orgStructureIdList, begDate, endDate, reportLineList, profileId)
                reportLineList = self.averageYarHospitalBedEvent(orgStructureIdList, begDate, endDate, reportLineList, profileId)
            records = self.getDataEventHospital(orgStructureIdList, begDate, endDate, bedProfileIdList, 1, groupingForMES, groupMES, MES, eventTypeId, eventPurposeId)
            if records:
                while records.next():
                    record = records.record()
                    profileId = forceRef(record.value('bedProfile'))
                    reportLine = reportLineList.get(profileId, None)
                    reportLineAll = reportLineList.get('', None)
                    if not reportLine:
                        bedRepRecord = db.getRecordEx(tableRBHospitalBedProfile, [tableRBHospitalBedProfile['code'], tableRBHospitalBedProfile['name']], [tableRBHospitalBedProfile['id'].eq(profileId)])
                        if bedRepRecord:
                            code = forceString(bedRepRecord.value('code'))
                            name = forceString(bedRepRecord.value('name'))
                            reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                            reportLine['code'] = forceString(bedProfileRecord.value('code'))
                            reportLine['name'] = forceString(bedProfileRecord.value('name'))
                    if reportLine:
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLine['visitReceived'] += 1
                            reportLineAll['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLine['visitLeaved'] += 1
                            reportLineAll['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLine['ageChildren'] += 1
                            reportLineAll['ageChildren'] += 1
                        countTransfer = forceInt(record.value('countTransfer'))
                        countVisit = forceInt(record.value('countVisit'))
                        reportLine['countTransfer'] += countTransfer
                        reportLine['countVisit'] += countVisit
                        reportLineAll['countTransfer'] += countTransfer
                        reportLineAll['countVisit'] += countVisit
                        reportLineList[profileId] = reportLine
                        reportLineList[''] = reportLineAll
            cnt = 1
            rowProfile = table.addRow()
            reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            table.setText(rowProfile, 0, cnt)
            table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
            table.setText(rowProfile, 2, reportLine['countBed'])
            table.setText(rowProfile, 3, reportLine['countAverageBed'])
            table.setText(rowProfile, 4, reportLine['visitReceived'])
            table.setText(rowProfile, 5, reportLine['visitLeaved'])
            table.setText(rowProfile, 6, reportLine['ageChildren'])
            table.setText(rowProfile, 7, reportLine['countTransfer'])
            table.setText(rowProfile, 8, reportLine['countVisit'])
            if reportLineList.get('', None):
                del reportLineList['']
            for key, reportLine in reportLineList.items():
                rowProfile = table.addRow()
                cnt += 1
                table.setText(rowProfile, 0, cnt)
                table.setText(rowProfile, 1, reportLine['name'])
                table.setText(rowProfile, 2, reportLine['countBed'])
                table.setText(rowProfile, 3, reportLine['countAverageBed'])
                table.setText(rowProfile, 4, reportLine['visitReceived'])
                table.setText(rowProfile, 5, reportLine['visitLeaved'])
                table.setText(rowProfile, 6, reportLine['ageChildren'])
                table.setText(rowProfile, 7, reportLine['countTransfer'])
                table.setText(rowProfile, 8, reportLine['countVisit'])
        return doc


class CStationaryOneHouseF14DC(CReportStationary):#actOneForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Стационар на дому.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        groupingForMES = getVal(params, 'groupingForMES', False)
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        if groupingForMES:
            groupMES = getVal(params, 'groupMES', None)
            MES = getVal(params, 'MES', None)
        else:
            groupMES = None
            MES = None
        doc = QtGui.QTextDocument()
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Раздел I. Использование коечного фонда\n(1100)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('4%',[u'№стр.', u'', u'1'], CReportBase.AlignRight),
                    ('21%',[u'Профили коек.', u'', u'2'], CReportBase.AlignLeft),
                    ('15%', [u'Стационар на дому', u'Число мест', u'3'], CReportBase.AlignRight),
                    ('15%', [u'', u'выписано', u'4'], CReportBase.AlignRight),
                    ('15%', [u'', u'из них детей (0-17 лет)', '5'], CReportBase.AlignRight),
                    ('15%', [u'', u'в т.ч. круглосуточный стационар(из г.18)', u'6'], CReportBase.AlignRight),
                    ('15%', [u'', u'проведено больными дней лечения', u'7'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 5) # Стационар на дому
            tableRBHospitalBedProfile = db.table('rbHospitalBedProfile')
            bedProfileRecords = db.getRecordList('rbHospitalBedProfile', 'id, code, name')
            reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}}
            bedProfileIdList = []
            for bedProfileRecord in bedProfileRecords:
                profileId = forceRef(bedProfileRecord.value('id'))
                if profileId not in bedProfileIdList:
                    bedProfileIdList.append(profileId)
                if not reportLineList.get(profileId, None):
                    reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                    reportLine['code'] = forceString(bedProfileRecord.value('code'))
                    reportLine['name'] = forceString(bedProfileRecord.value('name'))
                    reportLineList[profileId] = reportLine

                reportLineList = self.unrolledHospitalBedEvent(orgStructureIdList, begDate, endDate, reportLineList, profileId)
            records = self.getDataEventHospital(orgStructureIdList, begDate, endDate, bedProfileIdList, 2, groupingForMES, groupMES, MES,eventTypeId, eventPurposeId )
            if records:
                while records.next():
                    record = records.record()
                    profileId = forceRef(record.value('bedProfile'))
                    reportLine = reportLineList.get(profileId, None)
                    reportLineAll = reportLineList.get('', None)
                    if not reportLine:
                        bedRepRecord = db.getRecordEx(tableRBHospitalBedProfile, [tableRBHospitalBedProfile['code'], tableRBHospitalBedProfile['name']], [tableRBHospitalBedProfile['id'].eq(profileId)])
                        if bedRepRecord:
                            code = forceString(bedRepRecord.value('code'))
                            name = forceString(bedRepRecord.value('name'))
                            reportLine = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}
                            reportLine['code'] = forceString(bedProfileRecord.value('code'))
                            reportLine['name'] = forceString(bedProfileRecord.value('name'))
                    if reportLine:
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLine['visitReceived'] += 1
                            reportLineAll['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLine['visitLeaved'] += 1
                            reportLineAll['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLine['ageChildren'] += 1
                            reportLineAll['ageChildren'] += 1
                        countTransfer = forceInt(record.value('countTransfer'))
                        countVisit = forceInt(record.value('countVisit'))
                        reportLine['countTransfer'] += countTransfer
                        reportLine['countVisit'] += countVisit
                        reportLineAll['countTransfer'] += countTransfer
                        reportLineAll['countVisit'] += countVisit
                        reportLineList[profileId] = reportLine
                        reportLineList[''] = reportLineAll
            cnt = 1
            rowProfile = table.addRow()
            reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            table.setText(rowProfile, 0, cnt)
            table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
            table.setText(rowProfile, 2, reportLine['countBed'])
            table.setText(rowProfile, 3, reportLine['visitLeaved'])
            table.setText(rowProfile, 4, reportLine['ageChildren'])
            table.setText(rowProfile, 5, reportLine['countTransfer'])
            table.setText(rowProfile, 6, reportLine['countVisit'])
            if reportLineList.get('', None):
                del reportLineList['']
            for key, reportLine in reportLineList.items():
                rowProfile = table.addRow()
                cnt += 1
                table.setText(rowProfile, 0, cnt)
                table.setText(rowProfile, 1, reportLine['name'])
                table.setText(rowProfile, 2, reportLine['countBed'])
                table.setText(rowProfile, 3, reportLine['visitLeaved'])
                table.setText(rowProfile, 4, reportLine['ageChildren'])
                table.setText(rowProfile, 5, reportLine['countTransfer'])
                table.setText(rowProfile, 6, reportLine['countVisit'])
        return doc


class CStationaryTwoAdultF14DC(CReportStationary):#actTwoAdultForma14D
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. 18 лет и старше. Общий.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 12
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in TwoRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(TwoRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2000) (18 лет и старше)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('7%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('7%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('7%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('7%', [u'Дневной стационар при больничных учреждениях', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('7%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('7%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('7%', [u'', u'умерло', '7'], CReportBase.AlignRight),

                ('7%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'выписано больных', u'8'], CReportBase.AlignRight),
                ('7%', [u'', u'из них направлено в круглосуточн. Стационар', u'9'], CReportBase.AlignRight),
                ('7%', [u'', u'проведено выписанными больными дней лечения', u'10'], CReportBase.AlignRight),
                ('7%', [u'', u'умерло', u'11'], CReportBase.AlignRight),

                ('7%', [u'Стационар на дому', u'выписано больных', u'12'], CReportBase.AlignRight),
                ('7%', [u'', u'из них направлено в круглосуточн. Стационар', u'13'], CReportBase.AlignRight),
                ('7%', [u'', u'проведено выписанными больными дней лечения', u'14'], CReportBase.AlignRight),
                ('7%', [u'', u'умерло', u'15'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Дневной стационар при больничных учреждениях
        table.mergeCells(0, 7, 1, 4)  # Дневной стационар при амбулаторно-поликлинических учреждениях
        table.mergeCells(0, 11, 1, 4) # Дневной стационар при амбулаторно-поликлинических учреждениях

        isHospitals = [(0, 0), (4, 1), (8, 2)]
        for i, isHospital in isHospitals:
            records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) >= 18''', isHospital)
            if records:
                while records.next():
                    record = records.record()
                    MKBRec = normalizeMKB(forceString(record.value('MKB')))
                    visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                    countTransfer = forceInt(record.value('countTransfer'))
                    countDeath = forceInt(record.value('countDeath'))
                    countVisit = forceInt(record.value('countVisit'))
                    countSurgery = forceInt(record.value('countSurgery'))

                    for row in mapMainRows.get(MKBRec, []):
                        reportLine = reportMainData[row]
                        if visitLeavedDate:
                            reportLine[i] += 1
                        reportLine[i+1] += countTransfer
                        reportLine[i+2] += countVisit
                        reportLine[i+3] += countDeath
                    if countSurgery:
                        reportLine = reportMainData[len(TwoRows)-2]
                        if visitLeavedDate:
                            reportLine[i] += 1
                        reportLine[i+1] += countTransfer
                        reportLine[i+2] = u'X'
                        reportLine[i+3] += countDeath
                        reportLine = reportMainData[len(TwoRows)-1]
                        if visitLeavedDate:
                            reportLine[i] += countSurgery
                        reportLine[i+1] = u'X'
                        reportLine[i+2] = u'X'
                        reportLine[i+3] = u'X'
        for row, rowDescr in enumerate(TwoRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc


class CStationaryTwoAdultHospitalF14DC(CReportStationary):#actTwoAdultForma14D
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. 18 лет и старше. Дневной стационар при больничном учреждении.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 4
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in TwoRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(TwoRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2000) (18 лет и старше)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('21%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('4%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('15%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('15%', [u'Дневной стационар при больничных учреждениях', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('15%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('15%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('15%', [u'', u'умерло', '7'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Дневной стационар при больничных учреждениях

        records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) >= 18''', 0)
        if records:
            while records.next():
                record = records.record()
                MKBRec = normalizeMKB(forceString(record.value('MKB')))
                visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                countTransfer = forceInt(record.value('countTransfer'))
                countDeath = forceInt(record.value('countDeath'))
                countVisit = forceInt(record.value('countVisit'))
                countSurgery = forceInt(record.value('countSurgery'))

                for row in mapMainRows.get(MKBRec, []):
                    reportLine = reportMainData[row]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] += countVisit
                    reportLine[3] += countDeath
                if countSurgery:
                    reportLine = reportMainData[len(TwoRows)-2]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] = u'X'
                    reportLine[3] += countDeath
                    reportLine = reportMainData[len(TwoRows)-1]
                    if visitLeavedDate:
                        reportLine[0] += countSurgery
                    reportLine[1] = u'X'
                    reportLine[2] = u'X'
                    reportLine[3] = u'X'
        for row, rowDescr in enumerate(TwoRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc


class CStationaryTwoAdultPoliclinicF14DC(CReportStationary):#actTwoAdultForma14D
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. 18 лет и старше. Дневной стационар при амбулаторно-поликлинических учреждениях.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 4
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in TwoRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(TwoRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2000) (18 лет и старше)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('21%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('4%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('15%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('15%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('15%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('15%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('15%', [u'', u'умерло', u'7'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Дневной стационар при амбулаторно-поликлинических учреждениях
        records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) >= 18''', 1)
        if records:
            while records.next():
                record = records.record()
                MKBRec = normalizeMKB(forceString(record.value('MKB')))
                visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                countTransfer = forceInt(record.value('countTransfer'))
                countDeath = forceInt(record.value('countDeath'))
                countVisit = forceInt(record.value('countVisit'))
                countSurgery = forceInt(record.value('countSurgery'))

                for row in mapMainRows.get(MKBRec, []):
                    reportLine = reportMainData[row]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] += countVisit
                    reportLine[3] += countDeath
                if countSurgery:
                    reportLine = reportMainData[len(TwoRows)-2]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] = u'X'
                    reportLine[3] += countDeath
                    reportLine = reportMainData[len(TwoRows)-1]
                    if visitLeavedDate:
                        reportLine[0] += countSurgery
                    reportLine[1] = u'X'
                    reportLine[2] = u'X'
                    reportLine[3] = u'X'
        for row, rowDescr in enumerate(TwoRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc


class CStationaryTwoAdultHouseF14DC(CReportStationary):#actTwoAdultForma14D
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. 18 лет и старше. Стационар на дому.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 4
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in TwoRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(TwoRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2000) (18 лет и старше)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('21%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('4%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('15%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('15%', [u'Стационар на дому', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('15%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('15%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('15%', [u'', u'умерло', u'7'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Стационар на дому

        records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) >= 18''', 2)
        if records:
            while records.next():
                record = records.record()
                MKBRec = normalizeMKB(forceString(record.value('MKB')))
                visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                countTransfer = forceInt(record.value('countTransfer'))
                countDeath = forceInt(record.value('countDeath'))
                countVisit = forceInt(record.value('countVisit'))
                countSurgery = forceInt(record.value('countSurgery'))

                for row in mapMainRows.get(MKBRec, []):
                    reportLine = reportMainData[row]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] += countVisit
                    reportLine[3] += countDeath
                if countSurgery:
                    reportLine = reportMainData[len(TwoRows)-2]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] = u'X'
                    reportLine[3] += countDeath
                    reportLine = reportMainData[len(TwoRows)-1]
                    if visitLeavedDate:
                        reportLine[0] += countSurgery
                    reportLine[1] = u'X'
                    reportLine[2] = u'X'
                    reportLine[3] = u'X'
        for row, rowDescr in enumerate(TwoRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc


class CStationaryTwoChildrenF14DC(CReportStationary):#actTwoChildrenForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. Дети 0-17 лет включительно. Общий.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 12
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in ThreeRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(ThreeRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2003) (дети 0-17 лет включительно)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('7%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('7%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('7%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('7%', [u'Дневной стационар при больничных учреждениях', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('7%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('7%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('7%', [u'', u'умерло', '7'], CReportBase.AlignRight),

                ('7%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'выписано больных', u'8'], CReportBase.AlignRight),
                ('7%', [u'', u'из них направлено в круглосуточн. Стационар', u'9'], CReportBase.AlignRight),
                ('7%', [u'', u'проведено выписанными больными дней лечения', u'10'], CReportBase.AlignRight),
                ('7%', [u'', u'умерло', u'11'], CReportBase.AlignRight),

                ('7%', [u'Стационар на дому', u'выписано больных', u'12'], CReportBase.AlignRight),
                ('7%', [u'', u'из них направлено в круглосуточн. Стационар', u'13'], CReportBase.AlignRight),
                ('7%', [u'', u'проведено выписанными больными дней лечения', u'14'], CReportBase.AlignRight),
                ('7%', [u'', u'умерло', u'15'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Дневной стационар при больничных учреждениях
        table.mergeCells(0, 7, 1, 4)  # Дневной стационар при амбулаторно-поликлинических учреждениях
        table.mergeCells(0, 11, 1, 4) # Дневной стационар при амбулаторно-поликлинических учреждениях

        isHospitals = [(0, 0), (4, 1), (8, 2)]
        for i, isHospital in isHospitals:
            records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) < 18''', isHospital)
            if records:
                while records.next():
                    record = records.record()
                    MKBRec = normalizeMKB(forceString(record.value('MKB')))
                    visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                    countTransfer = forceInt(record.value('countTransfer'))
                    countDeath = forceInt(record.value('countDeath'))
                    countVisit = forceInt(record.value('countVisit'))
                    countSurgery = forceInt(record.value('countSurgery'))

                    for row in mapMainRows.get(MKBRec, []):
                        reportLine = reportMainData[row]
                        if visitLeavedDate:
                            reportLine[i] += 1
                        reportLine[i+1] += countTransfer
                        reportLine[i+2] += countVisit
                        reportLine[i+3] += countDeath
                    if countSurgery:
                        reportLine = reportMainData[len(TwoRows)-2]
                        if visitLeavedDate:
                            reportLine[i] += 1
                        reportLine[i+1] += countTransfer
                        reportLine[i+2] = u'X'
                        reportLine[i+3] += countDeath
                        reportLine = reportMainData[len(TwoRows)-1]
                        if visitLeavedDate:
                            reportLine[i] += countSurgery
                        reportLine[i+1] = u'X'
                        reportLine[i+2] = u'X'
                        reportLine[i+3] = u'X'

        for row, rowDescr in enumerate(ThreeRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc


class CStationaryTwoChildrenHospitalF14DC(CReportStationary):#actTwoChildrenForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. Дети 0-17 лет включительно. Дневной стационар при больничном учреждении.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 4
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in ThreeRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(ThreeRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2003) (дети 0-17 лет включительно)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('21%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('4%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('15%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('15%', [u'Дневной стационар при больничных учреждениях', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('15%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('15%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('15%', [u'', u'умерло', '7'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Дневной стационар при больничных учреждениях
        records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) < 18''', 0)
        if records:
            while records.next():
                record = records.record()
                MKBRec = normalizeMKB(forceString(record.value('MKB')))
                visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                countTransfer = forceInt(record.value('countTransfer'))
                countDeath = forceInt(record.value('countDeath'))
                countVisit = forceInt(record.value('countVisit'))
                countSurgery = forceInt(record.value('countSurgery'))

                for row in mapMainRows.get(MKBRec, []):
                    reportLine = reportMainData[row]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] += countVisit
                    reportLine[3] += countDeath
                if countSurgery:
                    reportLine = reportMainData[len(TwoRows)-2]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] = u'X'
                    reportLine[3] += countDeath
                    reportLine = reportMainData[len(TwoRows)-1]
                    if visitLeavedDate:
                        reportLine[0] += countSurgery
                    reportLine[1] = u'X'
                    reportLine[2] = u'X'
                    reportLine[3] = u'X'
        for row, rowDescr in enumerate(ThreeRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc


class CStationaryTwoChildrenPoliclinicF14DC(CReportStationary):#actTwoChildrenForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. Дети 0-17 лет включительно. Дневной стационар при амбулаторно-поликлинических учреждениях.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 4
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in ThreeRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(ThreeRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2003) (дети 0-17 лет включительно)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('21%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('4%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('15%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('15%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('15%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('15%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('15%', [u'', u'умерло', u'7'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Дневной стационар при амбулаторно-поликлинических учреждениях
        records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) < 18''', 1)
        if records:
            while records.next():
                record = records.record()
                MKBRec = normalizeMKB(forceString(record.value('MKB')))
                visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                countTransfer = forceInt(record.value('countTransfer'))
                countDeath = forceInt(record.value('countDeath'))
                countVisit = forceInt(record.value('countVisit'))
                countSurgery = forceInt(record.value('countSurgery'))

                for row in mapMainRows.get(MKBRec, []):
                    reportLine = reportMainData[row]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] += countVisit
                    reportLine[3] += countDeath
                if countSurgery:
                    reportLine = reportMainData[len(TwoRows)-2]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] = u'X'
                    reportLine[3] += countDeath
                    reportLine = reportMainData[len(TwoRows)-1]
                    if visitLeavedDate:
                        reportLine[0] += countSurgery
                    reportLine[1] = u'X'
                    reportLine[2] = u'X'
                    reportLine[3] = u'X'
        for row, rowDescr in enumerate(ThreeRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc


class CStationaryTwoChildrenHouseF14DC(CReportStationary):#actTwoChildrenForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел II. Дети 0-17 лет включительно. Стационар на дому.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        doc = QtGui.QTextDocument()
        rowSize = 4
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in ThreeRows] )
        reportMainData = [ [0]*rowSize for row in xrange(len(ThreeRows)) ]
        orgStructureIndex = self.stationaryF14DCSetupDialog.cmbOrgStructure._model.index(self.stationaryF14DCSetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14DCSetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        titleText = u'Раздел II. Состав больных в дневном стационаре, сроки и исходы лечения\n(2003) (дети 0-17 лет включительно)'
        cursor.insertText(titleText)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('21%',[u'', u'', u'1'], CReportBase.AlignLeft),
                ('4%',[u'№ строки', u'', u'2'], CReportBase.AlignRight),
                ('15%', [u'Код по МКБ-X', u'', u'3'], CReportBase.AlignLeft),
                ('15%', [u'Стационар на дому', u'выписано больных', u'4'], CReportBase.AlignRight),
                ('15%', [u'', u'из них направлено в круглосуточн. Стационар', u'5'], CReportBase.AlignRight),
                ('15%', [u'', u'проведено выписанными больными дней лечения', u'6'], CReportBase.AlignRight),
                ('15%', [u'', u'умерло', u'7'], CReportBase.AlignRight)
               ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)  # название
        table.mergeCells(0, 1, 2, 1)  # №стр
        table.mergeCells(0, 2, 2, 1)  # код по МКБ
        table.mergeCells(0, 3, 1, 4)  # Стационар на дому
        records = self.getDataEventAdult(params, orgStructureIdList, u'''(age(Client.birthDate, Event.setDate)) < 18''', 2)
        if records:
            while records.next():
                record = records.record()
                MKBRec = normalizeMKB(forceString(record.value('MKB')))
                visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                countTransfer = forceInt(record.value('countTransfer'))
                countDeath = forceInt(record.value('countDeath'))
                countVisit = forceInt(record.value('countVisit'))
                countSurgery = forceInt(record.value('countSurgery'))

                for row in mapMainRows.get(MKBRec, []):
                    reportLine = reportMainData[row]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] += countVisit
                    reportLine[3] += countDeath
                if countSurgery:
                    reportLine = reportMainData[len(TwoRows)-2]
                    if visitLeavedDate:
                        reportLine[0] += 1
                    reportLine[1] += countTransfer
                    reportLine[2] = u'X'
                    reportLine[3] += countDeath
                    reportLine = reportMainData[len(TwoRows)-1]
                    if visitLeavedDate:
                        reportLine[0] += countSurgery
                    reportLine[1] = u'X'
                    reportLine[2] = u'X'
                    reportLine[3] = u'X'
        for row, rowDescr in enumerate(TwoRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3+col, reportLine[col])
        return doc

class CStationaryTypeFinanceTypeF14DC(CReportStationary):#actFinanceForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Виды финансирования.')
        self.stationaryF14DCSetupDialog = None

    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        groupingForMES = params.get('groupingForMES', False)
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)

        if groupingForMES:
            groupMES = params.get('groupMES', None)
            MES = params.get('MES', None)
        else:
            groupMES = None
            MES = None
        query = self.selectFinanceData(begDate, endDate, orgStructureId, groupingForMES, eventPurposeId, eventTypeId, groupMES, MES)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%20', [u'Виды оплаты'], CReportBase.AlignRight),
                        ('%5',  [u'Число выбывших больных  из дневного стационара'], CReportBase.AlignLeft),
                        ('%5',  [u'Число дней лечения, проведенное выбывшими из дневного стационара'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        resultTable = {}
        if query:
            while query.next():
                record = query.record()
                nameFinance = forceString(record.value('name'))
                countLeaved = forceInt(record.value('countLeaved'))
                countDays   = forceInt(record.value('countDays'))

                resultTable[nameFinance] = [0]*2
                resultTable[nameFinance][0] = countLeaved
                resultTable[nameFinance][1] = countDays
        name = QtGui.qApp.db.getColumnValues('rbFinance', 'rbFinance.name',  QtGui.qApp.db.table('rbFinance')['name'].notInlist(resultTable.keys()))
        for nameFinance in name:
            resultTable[nameFinance] = [0]*2
        for key in sorted(resultTable.keys()):
            i = table.addRow()
            table.setText(i, 0, key)
            table.setText(i, 1, resultTable[key][0])
            table.setText(i, 2, resultTable[key][1])
        return doc

