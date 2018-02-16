# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceInt, forceRef, forceString, getVal
from Orgs.Utils         import getOrgStructureFullName
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_StationaryMESF14DCSetup import Ui_StationaryMESF14DCDialog


class CStationaryMESF14DCDialog(QtGui.QDialog, Ui_StationaryMESF14DCDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbGroupMES.setTable('mes.mrbMESGroup', addNone=True)
        self.cmbFilterProfile.setTable('rbHospitalBedProfile', addNone=True)
        self.cmbMes._popup.setCheckBoxes('stationaryMESF14DC')


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbGroupMES.setValue(getVal(params, 'groupMES', None))
        self.cmbMes.setValue(getVal(params, 'MES', None))
        self.cmbFilterProfile.setValue(getVal(params, 'profileBed', None))
        self.cmbGroupType.setCurrentIndex(getVal(params, 'groupType', 0))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['groupMES'] = self.cmbGroupMES.value()
        result['MES'] = self.cmbMes.value()
        result['profileBed'] = self.cmbFilterProfile.value()
        result['groupType'] = self.cmbGroupType.currentIndex()
        return result


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()


class CReportStationary(CReport):
    def __init__(self, parent = None):
        CReport.__init__(self, parent)
        self.clientDeath = 8


    def getSetupDialog(self, parent):
        result = CStationaryMESF14DCDialog(parent)
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
        groupMES = params.get('groupMES', None)
        if groupMES:
            description.append(u'Группа МЭС: %s'%(forceString(QtGui.qApp.db.translate('mes.mrbMESGroup', 'id', groupMES, 'name'))))
        MES = params.get('MES', None)
        if MES:
            description.append(u'МЭС: %s'%(forceString(QtGui.qApp.db.translate('mes.MES', 'id', MES, 'name'))))
        profileBedId = params.get('profileBed', None)
        if profileBedId:
            description.append(u'профиль койки: %s'%(forceString(QtGui.qApp.db.translate('rbHospitalBedProfile', 'id', profileBedId, 'name'))))
        groupType = params.get('groupType', 0)
        if groupType:
            description.append(u'группировать: ' + forceString([u'Не группировать', u'По типу события', u'По типу МЭС'][groupType]))

        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def getDataEventHospital(self, orgStructureIdList, begDate, endDate, isHospital, params):
        groupingForMES = getVal(params, 'groupingForMES', False)
        groupType = getVal(params, 'groupType', 0)
        profileBedId = getVal(params, 'profileBed', None)
        groupMES = getVal(params, 'groupMES', None)
        MES = getVal(params, 'MES', None)
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
        joinOr1 = db.joinAnd([tableEvent['setDate'].isNull(), tableEvent['execDate'].isNull()])
        joinOr2 = db.joinAnd([tableEvent['setDate'].isNotNull(), tableEvent['setDate'].ge(begDate), tableEvent['setDate'].lt(endDate)])
        joinOr3 = db.joinAnd([tableEvent['setDate'].isNull(), tableEvent['execDate'].isNotNull(), tableEvent['execDate'].gt(begDate)])
        joinOr4 = db.joinAnd([tableEvent['setDate'].isNotNull(), tableEvent['setDate'].le(begDate), db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].gt(begDate)])])
        cond.append(db.joinOr([joinOr1, joinOr2, joinOr3, joinOr4]))
        cond.append(tableRBMedicalAidType['code'].eq(7))
        if orgStructureIdList:
            cond.append(tableOS['deleted'].eq(0))
            cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
        else:
            cond.append(u'(OrgStructure.id IS NULL OR OrgStructure.deleted = 0')
        if isHospital == 0:
            cond.append(tableOS['type'].eq(1))
        elif isHospital == 1:
            queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
            cond.append(tableRBScene['code'].eq(1))
        elif isHospital == 2:
            queryTable = queryTable.innerJoin(tableRBScene, tableRBScene['id'].eq(tableVisit['scene_id']))
            cond.append(tableRBScene['code'].eq(2))
        if profileBedId:
            cond.append('''EXISTS(SELECT V.id FROM Visit AS V INNER JOIN rbHospitalBedProfile ON rbHospitalBedProfile.service_id = V.service_id WHERE rbHospitalBedProfile.id = %s AND V.event_id = Event.id AND V.deleted = 0 AND V.id = (SELECT MIN(VMI.id) FROM Visit AS VMI WHERE VMI.event_id = Event.id AND VMI.deleted = 0 AND VMI.date = (SELECT MIN(VMD.date) FROM Visit AS VMD WHERE VMD.event_id = Event.id AND VMD.deleted = 0)))'''%(str(profileBedId)))
        eventIdList = db.getDistinctIdList(queryTable, 'Event.id', cond, 'Event.id, Visit.date ASC')
        if eventIdList:
            if groupType == 1:
                fieldName = u' EventType.id AS eventTypeId, EventType.name AS eventTypeName,'
                strJoin = u'INNER JOIN EventType ON EventType.id = Event.eventType_id'
                strCond = u' AND EventType.deleted = 0 '
            elif groupType == 2:
                strJoin = u'LEFT JOIN mes.mrbMESGroup ON mes.mrbMESGroup.id = mes.MES.group_id '
                fieldName = u' mes.mrbMESGroup.id AS MESGroupId, mes.mrbMESGroup.name AS MESGroupName,'
                strCond = u' AND (mes.MES.group_id IS NULL OR mes.mrbMESGroup.deleted = 0) '
            else:
                fieldName = u''
                strJoin = u''
                strCond = u''
            stmtVisit = u'''SELECT mes.MES.id AS mesId, mes.MES.code AS mesCode, mes.MES.name AS mesName,%s
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
INNER JOIN Visit ON Visit.event_id = Event.id
INNER JOIN Client ON Event.client_id = Client.id
INNER JOIN mes.MES ON Event.MES_id = mes.MES.id
%s

WHERE (Event.deleted=0) AND (Client.deleted = 0) AND (Visit.deleted=0) AND Event.id IN (%s) AND mes.MES.deleted = 0%s

GROUP BY Event.id
ORDER BY Event.id, Visit.date ASC'''%(fieldName, db.formatDate(begDate), db.formatDate(endDate), strJoin, u','.join(str(eventId) for eventId in eventIdList if eventId), strCond)
            self.addQueryText(queryText=stmtVisit, queryDesc=u'DataEventHospital')
            return db.query(stmtVisit)
        return None


class CStationaryMESOneF14DC(CReportStationary):#actMESOneF14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Общий.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        orgStructureId = getVal(params, 'orgStructureId', None)
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
                    ('7%',[u'Профили коек.', u'', u'2'], CReportBase.AlignLeft),
                    ('6.42%', [u'Дневной стационар при больничном учреждении', u'поступило больных', u'3'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'выписано', u'4'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'из них детей (0-17 лет)', '5'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'в т.ч. круглосуточный стационар(из г.6)', u'6'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'проведено больными дней лечения', u'7'], CReportBase.AlignRight),

                    ('6.42%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'поступило больных', u'8'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'выписано', u'9'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'из них детей (0-17 лет)', '10'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'в т.ч. круглосуточный стационар(из г.13)', u'11'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'проведено больными дней лечения', u'12'], CReportBase.AlignRight),

                    ('6.42%', [u'Стационар на дому', u'выписано', u'13'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'из них детей (0-17 лет)', '14'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'в т.ч. круглосуточный стационар(из г.18)', u'15'], CReportBase.AlignRight),
                    ('6.42%', [u'', u'проведено больными дней лечения', u'16'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 5)  # Дневной стационар при больничном учреждении
            table.mergeCells(0, 7, 1, 5)  # Дневной стационар при амбулаторно-поликлинических учреждениях
            table.mergeCells(0, 12, 1, 4) # Стационар на дому

            mesIdList = {}
            rowProfile = table.addRow()
            table.setText(rowProfile, 0, 1)
            table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
            mesIdList = self.fillReportTable(begDate, endDate, table, 2, params, self.getDataEventHospital(orgStructureIdList, begDate, endDate, 0, params), mesIdList, 0, rowProfile)
            mesIdList = self.fillReportTable(begDate, endDate, table, 7, params, self.getDataEventHospital(orgStructureIdList, begDate, endDate, 1, params), mesIdList, 1, rowProfile)
            mesIdList = self.fillReportTable(begDate, endDate, table, 12, params, self.getDataEventHospital(orgStructureIdList, begDate, endDate, 2, params), mesIdList, 2, rowProfile)
        return doc


    def fillReportTable(self, begDate, endDate, table, cols, params, records, mesIdList, isHospital, rowProfile):
        db = QtGui.qApp.db
        groupType = getVal(params, 'groupType', 0)
        reportLineListGroup = {'':{'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}}
        if not groupType:
            reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}
            reportLineAll = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}
        if records:
            while records.next():
                record = records.record()
                mesId = forceRef(record.value('mesId'))
                if groupType == 1:
                    groupId = forceInt(record.value('eventTypeId'))
                elif groupType == 2:
                    groupId = forceInt(record.value('MESGroupId'))
                if groupType:
                    reportLineList = reportLineListGroup.get(groupId, {mesId:{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                    reportLineListAll = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                    reportLineListNull = reportLineList.get(0, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    reportLineAll = reportLineListAll.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                else:
                    reportLineAll = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                reportLine = reportLineList.get(mesId, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                if reportLine:
                    reportLine['code'] = forceString(record.value('mesCode'))
                    reportLine['name'] = forceString(record.value('mesName'))
                    visitReceivedId = forceRef(record.value('visitReceivedId'))
                    visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                    if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                        reportLine['visitReceived'] += 1
                        if groupType:
                            reportLineListNull['visitReceived'] += 1
                    visitLeavedId = forceRef(record.value('visitLeavedId'))
                    visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                    if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                        reportLine['visitLeaved'] += 1
                        if groupType:
                            reportLineListNull['visitLeaved'] += 1
                    ageClient = forceInt(record.value('ageClient'))
                    if ageClient <= 17:
                        reportLine['ageChildren'] += 1
                        if groupType:
                            reportLineListNull['ageChildren'] += 1
                    countTransfer = forceInt(record.value('countTransfer'))
                    countVisit = forceInt(record.value('countVisit'))
                    reportLine['countTransfer'] += countTransfer
                    reportLine['countVisit'] += countVisit
                    if groupType:
                        reportLineListNull['countTransfer'] += countTransfer
                        reportLineListNull['countVisit'] += countVisit
                    reportLineList[mesId] = reportLine
                    if groupType:
                        reportLineList[0] = reportLineListNull
                        reportLineListGroup[groupId] = reportLineList
                if reportLineAll:
                    visitReceivedId = forceRef(record.value('visitReceivedId'))
                    visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                    if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                        reportLineAll['visitReceived'] += 1
                    visitLeavedId = forceRef(record.value('visitLeavedId'))
                    visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                    if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                        reportLineAll['visitLeaved'] += 1
                    ageClient = forceInt(record.value('ageClient'))
                    if ageClient <= 17:
                        reportLineAll['ageChildren'] += 1
                    reportLineAll['countTransfer'] += forceInt(record.value('countTransfer'))
                    reportLineAll['countVisit'] += forceInt(record.value('countVisit'))
                    reportLineList[''] = reportLineAll
        cnt = 1
        if groupType:
            reportLineGroup = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}})
            reportLine = reportLineGroup.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
        else:
            reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
        if isHospital == 2:
            table.setText(rowProfile, cols, reportLine['visitLeaved'])
            table.setText(rowProfile, cols+1, reportLine['ageChildren'])
            table.setText(rowProfile, cols+2, reportLine['countTransfer'])
            table.setText(rowProfile, cols+3, reportLine['countVisit'])
        else:
            table.setText(rowProfile, cols, reportLine['visitReceived'])
            table.setText(rowProfile, cols+1, reportLine['visitLeaved'])
            table.setText(rowProfile, cols+2, reportLine['ageChildren'])
            table.setText(rowProfile, cols+3, reportLine['countTransfer'])
            table.setText(rowProfile, cols+4, reportLine['countVisit'])
        if groupType:
            if reportLineListGroup.get('', None):
                del reportLineListGroup['']
                for reportLineListGroupNull in reportLineListGroup.values():
                    if reportLineListGroupNull.get('', None):
                        del reportLineListGroupNull['']
        else:
            if reportLineList.get('', None):
                del reportLineList['']
        if groupType:
            if groupType == 1:
                tableGroup = db.table('EventType')
            elif groupType == 2:
                tableGroup = db.table('mes.mrbMESGroup')
            records = db.getRecordList(tableGroup, [tableGroup['id'], tableGroup['name']], [tableGroup['deleted'].eq(0), tableGroup['id'].inlist(reportLineListGroup)])
            groupList = {}
            for record in records:
                id = forceRef(record.value('id'))
                if id and not groupList.get(id, None):
                    groupList[id] = forceString(record.value('name'))
            boldChars = QtGui.QTextCharFormat()
            boldChars.setFontWeight(QtGui.QFont.Bold)
            for keyGroup, reportLineList in reportLineListGroup.items():
                groupName = groupList.get(keyGroup, u'нет группы')
                for key, reportLine in reportLineList.items():
                    rowProfile = mesIdList.get((keyGroup, key), -1)
                    if rowProfile == -1:
                        rowProfile = table.addRow()
                        mesIdList[(keyGroup, key)] = rowProfile
                        cnt += 1
                        table.setText(rowProfile, 0, cnt, charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 1, groupName if key == 0 else reportLine['name'], charFormat=(boldChars if key == 0 else None))
                        for i in range(2, 16):
                            table.setText(rowProfile, i, '0')
                    if isHospital == 2:
                        table.setText(rowProfile, cols, reportLine['visitLeaved'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, cols+1, reportLine['ageChildren'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, cols+2, reportLine['countTransfer'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, cols+3, reportLine['countVisit'], charFormat=(boldChars if key == 0 else None))
                    else:
                        table.setText(rowProfile, cols, reportLine['visitReceived'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, cols+1, reportLine['visitLeaved'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, cols+2, reportLine['ageChildren'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, cols+3, reportLine['countTransfer'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, cols+4, reportLine['countVisit'], charFormat=(boldChars if key == 0 else None))
        else:
            for key, reportLine in reportLineList.items():
                rowProfile = mesIdList.get(key, -1)
                if rowProfile == -1:
                    rowProfile = table.addRow()
                    mesIdList[key] = rowProfile
                    cnt += 1
                    table.setText(rowProfile, 0, cnt)
                    table.setText(rowProfile, 1, reportLine['name'])
                    for i in range(2, 16):
                        table.setText(rowProfile, i, '0')
                if isHospital == 2:
                    table.setText(rowProfile, cols, reportLine['visitLeaved'])
                    table.setText(rowProfile, cols+1, reportLine['ageChildren'])
                    table.setText(rowProfile, cols+2, reportLine['countTransfer'])
                    table.setText(rowProfile, cols+3, reportLine['countVisit'])
                else:
                    table.setText(rowProfile, cols, reportLine['visitReceived'])
                    table.setText(rowProfile, cols+1, reportLine['visitLeaved'])
                    table.setText(rowProfile, cols+2, reportLine['ageChildren'])
                    table.setText(rowProfile, cols+3, reportLine['countTransfer'])
                    table.setText(rowProfile, cols+4, reportLine['countVisit'])
        return mesIdList


class CStationaryMESHospitalF14DC(CReportStationary):#actOneForma14DC CStationaryOnePolyclinicF14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Дневной стационар при больничном учреждении.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        orgStructureId = getVal(params, 'orgStructureId', None)
        groupType = getVal(params, 'groupType', 0)

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
                    ('15.4%', [u'Дневной стационар при больничном учреждении', u'поступило больных', u'3'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'выписано', u'4'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'из них детей (0-17 лет)', '5'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'в т.ч. круглосуточный стационар(из г.6)', u'6'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'проведено больными дней лечения', u'7'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 5)  # Дневной стационар при больничном учреждении

            reportLineListGroup = {'':{'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}}
            if not groupType:
                reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}
                reportLineAll = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}
            records = self.getDataEventHospital(orgStructureIdList, begDate, endDate, 0, params)
            if records:
                while records.next():
                    record = records.record()
                    mesId = forceRef(record.value('mesId'))
                    if groupType == 1:
                        groupId = forceInt(record.value('eventTypeId'))
                    elif groupType == 2:
                        groupId = forceInt(record.value('MESGroupId'))
                    if groupType:
                        reportLineList = reportLineListGroup.get(groupId, {mesId:{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                        reportLineListAll = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                        reportLineListNull = reportLineList.get(0, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                        reportLineAll = reportLineListAll.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    else:
                        reportLineAll = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    reportLine = reportLineList.get(mesId, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    if reportLine:
                        reportLine['code'] = forceString(record.value('mesCode'))
                        reportLine['name'] = forceString(record.value('mesName'))
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLine['visitReceived'] += 1
                            if groupType:
                                reportLineListNull['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLine['visitLeaved'] += 1
                            if groupType:
                                reportLineListNull['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLine['ageChildren'] += 1
                            if groupType:
                                reportLineListNull['ageChildren'] += 1
                        countTransfer = forceInt(record.value('countTransfer'))
                        countVisit = forceInt(record.value('countVisit'))
                        reportLine['countTransfer'] += countTransfer
                        reportLine['countVisit'] += countVisit
                        if groupType:
                            reportLineListNull['countTransfer'] += countTransfer
                            reportLineListNull['countVisit'] += countVisit
                        reportLineList[mesId] = reportLine
                        if groupType:
                            reportLineList[0] = reportLineListNull
                            reportLineListGroup[groupId] = reportLineList
                    if reportLineAll:
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLineAll['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLineAll['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLineAll['ageChildren'] += 1
                        reportLineAll['countTransfer'] += forceInt(record.value('countTransfer'))
                        reportLineAll['countVisit'] += forceInt(record.value('countVisit'))
                        reportLineList[''] = reportLineAll
            cnt = 1
            rowProfile = table.addRow()
            if groupType:
                reportLineGroup = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}})
                reportLine = reportLineGroup.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            else:
                reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            table.setText(rowProfile, 0, cnt)
            table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
            table.setText(rowProfile, 2, reportLine['visitReceived'])
            table.setText(rowProfile, 3, reportLine['visitLeaved'])
            table.setText(rowProfile, 4, reportLine['ageChildren'])
            table.setText(rowProfile, 5, reportLine['countTransfer'])
            table.setText(rowProfile, 6, reportLine['countVisit'])
            if groupType:
                if reportLineListGroup.get('', None):
                    del reportLineListGroup['']
                    for reportLineListGroupNull in reportLineListGroup.values():
                        if reportLineListGroupNull.get('', None):
                            del reportLineListGroupNull['']
            else:
                if reportLineList.get('', None):
                    del reportLineList['']
            if groupType:
                if groupType == 1:
                    tableGroup = db.table('EventType')
                elif groupType == 2:
                    tableGroup = db.table('mes.mrbMESGroup')
                records = db.getRecordList(tableGroup, [tableGroup['id'], tableGroup['name']], [tableGroup['deleted'].eq(0), tableGroup['id'].inlist(reportLineListGroup)])
                groupList = {}
                for record in records:
                    id = forceRef(record.value('id'))
                    if id and not groupList.get(id, None):
                        groupList[id] = forceString(record.value('name'))
                boldChars = QtGui.QTextCharFormat()
                boldChars.setFontWeight(QtGui.QFont.Bold)
                for keyGroup, reportLineList in reportLineListGroup.items():
                    groupName = groupList.get(keyGroup, u'нет группы')
                    for key, reportLine in reportLineList.items():
                        rowProfile = table.addRow()
                        cnt += 1
                        table.setText(rowProfile, 0, cnt, charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 1, groupName if key == 0 else reportLine['name'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 2, reportLine['visitReceived'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 3, reportLine['visitLeaved'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 4, reportLine['ageChildren'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 5, reportLine['countTransfer'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 6, reportLine['countVisit'], charFormat=(boldChars if key == 0 else None))
            else:
                for key, reportLine in reportLineList.items():
                    rowProfile = table.addRow()
                    cnt += 1
                    table.setText(rowProfile, 0, cnt)
                    table.setText(rowProfile, 1, reportLine['name'])
                    table.setText(rowProfile, 2, reportLine['visitReceived'])
                    table.setText(rowProfile, 3, reportLine['visitLeaved'])
                    table.setText(rowProfile, 4, reportLine['ageChildren'])
                    table.setText(rowProfile, 5, reportLine['countTransfer'])
                    table.setText(rowProfile, 6, reportLine['countVisit'])
        return doc


class CStationaryMESPolyclinicF14DC(CReportStationary):#actOneForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Дневной стационар при амбулаторно-поликлинических учреждениях.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        orgStructureId = getVal(params, 'orgStructureId', None)
        groupingForMES = getVal(params, 'groupingForMES', False)
        groupType = getVal(params, 'groupType', 0)
        profileBedId = getVal(params, 'profileBed', None)
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
                    ('15.4%', [u'Дневной стационар при амбулаторно-поликлинических учреждениях', u'поступило больных', u'3'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'выписано', u'4'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'из них детей (0-17 лет)', '5'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'в т.ч. круглосуточный стационар(из г.6)', u'6'], CReportBase.AlignRight),
                    ('15.4%', [u'', u'проведено больными дней лечения', u'7'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 5)  # Дневной стационар при амбулаторно-поликлинических учреждениях
            reportLineListGroup = {'':{'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}}
            if not groupType:
                reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}
                reportLineAll = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}
            records = self.getDataEventHospital(orgStructureIdList, begDate, endDate, 1, params)
            if records:
                while records.next():
                    record = records.record()
                    mesId = forceRef(record.value('mesId'))
                    if groupType == 1:
                        groupId = forceInt(record.value('eventTypeId'))
                    elif groupType == 2:
                        groupId = forceInt(record.value('MESGroupId'))
                    if groupType:
                        reportLineList = reportLineListGroup.get(groupId, {mesId:{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                        reportLineListAll = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                        reportLineListNull = reportLineList.get(0, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                        reportLineAll = reportLineListAll.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    else:
                        reportLineAll = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    reportLine = reportLineList.get(mesId, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    if reportLine:
                        reportLine['code'] = forceString(record.value('mesCode'))
                        reportLine['name'] = forceString(record.value('mesName'))
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLine['visitReceived'] += 1
                            if groupType:
                                reportLineListNull['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLine['visitLeaved'] += 1
                            if groupType:
                                reportLineListNull['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLine['ageChildren'] += 1
                            if groupType:
                                reportLineListNull['ageChildren'] += 1
                        countTransfer = forceInt(record.value('countTransfer'))
                        countVisit = forceInt(record.value('countVisit'))
                        reportLine['countTransfer'] += countTransfer
                        reportLine['countVisit'] += countVisit
                        if groupType:
                            reportLineListNull['countTransfer'] += countTransfer
                            reportLineListNull['countVisit'] += countVisit
                        reportLineList[mesId] = reportLine
                        if groupType:
                            reportLineList[0] = reportLineListNull
                            reportLineListGroup[groupId] = reportLineList
                    if reportLineAll:
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLineAll['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLineAll['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLineAll['ageChildren'] += 1
                        reportLineAll['countTransfer'] += forceInt(record.value('countTransfer'))
                        reportLineAll['countVisit'] += forceInt(record.value('countVisit'))
                        reportLineList[''] = reportLineAll
            cnt = 1
            rowProfile = table.addRow()
            if groupType:
                reportLineGroup = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}})
                reportLine = reportLineGroup.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            else:
                reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            table.setText(rowProfile, 0, cnt)
            table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
            table.setText(rowProfile, 2, reportLine['visitReceived'])
            table.setText(rowProfile, 3, reportLine['visitLeaved'])
            table.setText(rowProfile, 4, reportLine['ageChildren'])
            table.setText(rowProfile, 5, reportLine['countTransfer'])
            table.setText(rowProfile, 6, reportLine['countVisit'])
            if groupType:
                if reportLineListGroup.get('', None):
                    del reportLineListGroup['']
                    for reportLineListGroupNull in reportLineListGroup.values():
                        if reportLineListGroupNull.get('', None):
                            del reportLineListGroupNull['']
            else:
                if reportLineList.get('', None):
                    del reportLineList['']
            if groupType:
                if groupType == 1:
                    tableGroup = db.table('EventType')
                elif groupType == 2:
                    tableGroup = db.table('mes.mrbMESGroup')
                records = db.getRecordList(tableGroup, [tableGroup['id'], tableGroup['name']], [tableGroup['deleted'].eq(0), tableGroup['id'].inlist(reportLineListGroup)])
                groupList = {}
                for record in records:
                    id = forceRef(record.value('id'))
                    if id and not groupList.get(id, None):
                        groupList[id] = forceString(record.value('name'))
                boldChars = QtGui.QTextCharFormat()
                boldChars.setFontWeight(QtGui.QFont.Bold)
                for keyGroup, reportLineList in reportLineListGroup.items():
                    groupName = groupList.get(keyGroup, u'нет группы')
                    for key, reportLine in reportLineList.items():
                        rowProfile = table.addRow()
                        cnt += 1
                        table.setText(rowProfile, 0, cnt, charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 1, groupName if key == 0 else reportLine['name'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 2, reportLine['visitReceived'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 3, reportLine['visitLeaved'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 4, reportLine['ageChildren'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 5, reportLine['countTransfer'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 6, reportLine['countVisit'], charFormat=(boldChars if key == 0 else None))
            else:
                for key, reportLine in reportLineList.items():
                    rowProfile = table.addRow()
                    cnt += 1
                    table.setText(rowProfile, 0, cnt)
                    table.setText(rowProfile, 1, reportLine['name'])
                    table.setText(rowProfile, 2, reportLine['visitReceived'])
                    table.setText(rowProfile, 3, reportLine['visitLeaved'])
                    table.setText(rowProfile, 4, reportLine['ageChildren'])
                    table.setText(rowProfile, 5, reportLine['countTransfer'])
                    table.setText(rowProfile, 6, reportLine['countVisit'])
        return doc


class CStationaryMESHouseF14DC(CReportStationary):#actOneForma14DC
    def __init__(self, parent = None):
        CReportStationary.__init__(self, parent)
        self.setTitle(u'Форма 14ДС. Раздел I. Использование коечного фонда. Стационар на дому.')
        self.stationaryF14DCSetupDialog = None


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        orgStructureId = getVal(params, 'orgStructureId', None)
        groupingForMES = getVal(params, 'groupingForMES', False)
        groupType = getVal(params, 'groupType', 0)
        profileBedId = getVal(params, 'profileBed', None)
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
                    ('21%',[u'Профили коек.', u'', u'2'], CReportBase.AlignLeft),
                    ('18.75%', [u'Стационар на дому', u'выписано', u'3'], CReportBase.AlignRight),
                    ('18.75%', [u'', u'из них детей (0-17 лет)', '4'], CReportBase.AlignRight),
                    ('18.75%', [u'', u'в т.ч. круглосуточный стационар(из г.18)', u'5'], CReportBase.AlignRight),
                    ('18.75%', [u'', u'проведено больными дней лечения', u'6'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)  # №стр
            table.mergeCells(0, 1, 2, 1)  # Профили коек
            table.mergeCells(0, 2, 1, 4) # Стационар на дому
            reportLineListGroup = {'':{'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}}
            if not groupType:
                reportLineList = {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}}
                reportLineAll = {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}
            records = self.getDataEventHospital(orgStructureIdList, begDate, endDate, 2, params)
            if records:
                while records.next():
                    record = records.record()
                    mesId = forceRef(record.value('mesId'))
                    if groupType == 1:
                        groupId = forceInt(record.value('eventTypeId'))
                    elif groupType == 2:
                        groupId = forceInt(record.value('MESGroupId'))
                    if groupType:
                        reportLineList = reportLineListGroup.get(groupId, {mesId:{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                        reportLineListAll = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0}})
                        reportLineListNull = reportLineList.get(0, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                        reportLineAll = reportLineListAll.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    else:
                        reportLineAll = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    reportLine = reportLineList.get(mesId, {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0})
                    if reportLine:
                        reportLine['code'] = forceString(record.value('mesCode'))
                        reportLine['name'] = forceString(record.value('mesName'))
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLine['visitReceived'] += 1
                            if groupType:
                                reportLineListNull['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLine['visitLeaved'] += 1
                            if groupType:
                                reportLineListNull['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLine['ageChildren'] += 1
                            if groupType:
                                reportLineListNull['ageChildren'] += 1
                        countTransfer = forceInt(record.value('countTransfer'))
                        countVisit = forceInt(record.value('countVisit'))
                        reportLine['countTransfer'] += countTransfer
                        reportLine['countVisit'] += countVisit
                        if groupType:
                            reportLineListNull['countTransfer'] += countTransfer
                            reportLineListNull['countVisit'] += countVisit
                        reportLineList[mesId] = reportLine
                        if groupType:
                            reportLineList[0] = reportLineListNull
                            reportLineListGroup[groupId] = reportLineList
                    if reportLineAll:
                        visitReceivedId = forceRef(record.value('visitReceivedId'))
                        visitReceivedDate = forceDate(record.value('visitReceivedDate'))
                        if visitReceivedDate >= begDate and (not endDate or visitReceivedDate <= endDate):
                            reportLineAll['visitReceived'] += 1
                        visitLeavedId = forceRef(record.value('visitLeavedId'))
                        visitLeavedDate = forceDate(record.value('visitLeavedDate'))
                        if (visitReceivedId != visitLeavedId) and visitLeavedDate >= begDate and (not endDate or visitLeavedDate <= endDate):
                            reportLineAll['visitLeaved'] += 1
                        ageClient = forceInt(record.value('ageClient'))
                        if ageClient <= 17:
                            reportLineAll['ageChildren'] += 1
                        reportLineAll['countTransfer'] += forceInt(record.value('countTransfer'))
                        reportLineAll['countVisit'] += forceInt(record.value('countVisit'))
                        reportLineList[''] = reportLineAll
            cnt = 1
            rowProfile = table.addRow()
            if groupType:
                reportLineGroup = reportLineListGroup.get('', {'':{'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0}})
                reportLine = reportLineGroup.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            else:
                reportLine = reportLineList.get('', {'code':'', 'name':'', 'visitReceived':0, 'visitLeaved':0, 'ageChildren':0, 'countTransfer':0, 'countVisit':0, 'countBed':0, 'countAverageBed':0})
            table.setText(rowProfile, 0, cnt)
            table.setText(rowProfile, 1, u'ВСЕГО\nв том числе:')
            table.setText(rowProfile, 2, reportLine['visitLeaved'])
            table.setText(rowProfile, 3, reportLine['ageChildren'])
            table.setText(rowProfile, 4, reportLine['countTransfer'])
            table.setText(rowProfile, 5, reportLine['countVisit'])
            if groupType:
                if reportLineListGroup.get('', None):
                    del reportLineListGroup['']
                    for reportLineListGroupNull in reportLineListGroup.values():
                        if reportLineListGroupNull.get('', None):
                            del reportLineListGroupNull['']
            else:
                if reportLineList.get('', None):
                    del reportLineList['']
            if groupType:
                if groupType == 1:
                    tableGroup = db.table('EventType')
                elif groupType == 2:
                    tableGroup = db.table('mes.mrbMESGroup')
                records = db.getRecordList(tableGroup, [tableGroup['id'], tableGroup['name']], [tableGroup['deleted'].eq(0), tableGroup['id'].inlist(reportLineListGroup)])
                groupList = {}
                for record in records:
                    id = forceRef(record.value('id'))
                    if id and not groupList.get(id, None):
                        groupList[id] = forceString(record.value('name'))
                boldChars = QtGui.QTextCharFormat()
                boldChars.setFontWeight(QtGui.QFont.Bold)
                for keyGroup, reportLineList in reportLineListGroup.items():
                    groupName = groupList.get(keyGroup, u'нет группы')
                    for key, reportLine in reportLineList.items():
                        rowProfile = table.addRow()
                        cnt += 1
                        table.setText(rowProfile, 0, cnt, charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 1, groupName if key == 0 else reportLine['name'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 2, reportLine['visitLeaved'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 3, reportLine['ageChildren'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 4, reportLine['countTransfer'], charFormat=(boldChars if key == 0 else None))
                        table.setText(rowProfile, 5, reportLine['countVisit'], charFormat=(boldChars if key == 0 else None))
            else:
                for key, reportLine in reportLineList.items():
                    rowProfile = table.addRow()
                    cnt += 1
                    table.setText(rowProfile, 0, cnt)
                    table.setText(rowProfile, 1, reportLine['name'])
                    table.setText(rowProfile, 2, reportLine['visitLeaved'])
                    table.setText(rowProfile, 3, reportLine['ageChildren'])
                    table.setText(rowProfile, 4, reportLine['countTransfer'])
                    table.setText(rowProfile, 5, reportLine['countVisit'])
        return doc

