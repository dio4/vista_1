# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 30.04.2013

@author: atronah
"""

from PyQt4 import QtCore, QtGui

from library.Utils          import forceDate, forceInt, forceRef, forceString, getVal, getActionTypeIdListByFlatCode
from Orgs.Utils             import getOrgStructureFullName
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_StationaryF30Setup  import Ui_StationaryF30SetupDialog


MainRows = [(u'1', u'Из числа выписанных (гр. 9) переведено в другие стационары'),
 (u'2', u'обследовано серологически *) с целью выявления больных сифилисом'),
 (u'3', u'Число выбывших больных (гр.9 +11) по ОМС'),
 (u'4', u'по платным услугам включая ДМС'),
 (u'5', u'из них по ДМС'),
 (u'6', u'Проведено выбывшими больными койко-дней:  по ОМС'),
 (u'7', u'по платным услугам  включая ДМС'),
 (u'8', u'из них по ДМС'),
 (u'9', u'Посещений к  врачам стационара на платной основе')]

class CStationaryF30SetupDialog(QtGui.QDialog, Ui_StationaryF30SetupDialog):

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbProfileBed.setTable('rbHospitalBedProfile', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbProfileBed.setValue(getVal(params, 'profileBed', None))

    def params(self):
        result = {}
        result['endDate'] = self.edtEndDate.date()
        result['begDate'] = self.edtBegDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['profileBed'] = self.cmbProfileBed.value()
        return result


class CStationaryF30(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара')
        self.setOrientation(QtGui.QPrinter.Landscape)
        self.stationaryF30SetupDialog = None
        self.clientDeath = 8

    def getSetupDialog(self, parent):
        result = CStationaryF30SetupDialog(parent)
        self.stationaryF30SetupDialog = result
        return result

    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        if treeItem:
            return treeItem.getItemIdList()
        return []

    def dumpParams(self, cursor, params):

        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с ' + forceString(begDate)
            if endDate:
                result += u' по ' + forceString(endDate)
            return result

        description = []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        if begDate and endDate:
            description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        orgStructureId = params.get('orgStructureId', None)
        profileBedId = params.get('profileBed', None)
        if orgStructureId:
            description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        else:
            description.append(u'подразделение: ЛПУ')
        if profileBedId:
            description.append(u'профиль койки: %s' % forceString(QtGui.qApp.db.translate('rbHospitalBedProfile', 'id', profileBedId, 'name')))
        description.append(u'отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
        columns = [('100%', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def getCaption(self, cursor, params, title):
        orgStructureId = params.get('orgStructureId', None)
        underCaptionList = []
        if orgStructureId:
            underCaptionList.append(u'подразделение: ' + forceString(getOrgStructureFullName(orgStructureId)))
        else:
            underCaptionList.append(u'подразделение: ЛПУ')
        profileBedId = params.get('profileBed', None)
        if profileBedId:
            underCaptionList.append(u'профиль койки: %s' % forceString(QtGui.qApp.db.translate('rbHospitalBedProfile', 'id', profileBedId, 'name')))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        columns2 = [('100%', [], CReportBase.AlignCenter)]
        table2 = createTable(cursor, columns2, headerRowCount=2, border=0, cellPadding=2, cellSpacing=0)
        table2.setText(0, 0, title, charFormat=boldChars)
        table2.setText(1, 0, u', '.join((underCaption for underCaption in underCaptionList if underCaption)))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


class CStationaryF30Moving(CStationaryF30):

    def __init__(self, parent):
        CStationaryF30.__init__(self, parent)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара(3100)')

    def build(self, params):
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableAPOS = db.table('ActionProperty_OrgStructure')
        tableOS = db.table('OrgStructure')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableVHospitalBed = db.table('vHospitalBed')
        tableHBSchedule = db.table('rbHospitalBedShedule')
        endDateTime = getVal(params, 'endDate', QtCore.QDate())
        begDateTime = getVal(params, 'begDate', QtCore.QDate())
        if not endDateTime:
            endDateTime = QtCore.QDate.currentDate()
        if endDateTime and begDateTime:
            bedsSchedule = getVal(params, 'bedsSchedule', 0)
            profileBedId = params.get('profileBed', None)
            noProfileBed = getVal(params, 'noProfileBed', True)
            isPermanentBed = getVal(params, 'isPermanentBed', False)
            orgStructureIndex = self.stationaryF30SetupDialog.cmbOrgStructure._model.index(self.stationaryF30SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF30SetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertBlock()
            self.getCaption(cursor, params, u'Листок учета движения больных и коечного фонда стационара(3100)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('6%', [u'№ строки',
               u'',
               u'',
               u'',
               u'1'], CReportBase.AlignLeft),
             ('10%', [u'Профиль коек',
               u'',
               u'',
               u'',
               u'2'], CReportBase.AlignLeft),
             ('6%', [u'Число коек, фактически развернутых и свернутых на ремонт',
               u'на конец отчетного года',
               u'',
               u'',
               u'3'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'среднегодовых',
               u'',
               u'',
               u'4'], CReportBase.AlignLeft),
             ('6%', [u'В отчетном году',
               u'поступило больных - всего',
               u'',
               u'',
               u'5'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'из них сельских жителей',
               u'',
               u'',
               u'6'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'из общего числа поступивших (из гр.5)',
               u'0–17 лет (включительно)',
               u'',
               u'7'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'',
               u'старше трудоспособного возраста',
               u'',
               u'8'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'выписано больных',
               u'всего',
               u'',
               u'9'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'',
               u'в том числе старше  трудоспособного возраста',
               u'',
               u'10'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'из них в дневные стационары(всех типов)',
               u'',
               u'',
               u'11'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'Умерло',
               u'всего',
               u'',
               u'12'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'',
               u'в том числе старше трудоспособного возраста',
               u'',
               u'13'], CReportBase.AlignLeft),
             ('6%', [u'Проведено больными койко-дней',
               u'всего',
               u'',
               u'',
               u'14'], CReportBase.AlignLeft),
             ('6%', [u'',
               u'в том числе старше трудоспособного возраста',
               u'',
               u'',
               u'15'], CReportBase.AlignLeft),
             ('6%', [u'Койко-дни закрытия на ремонт',
               u'',
               u'',
               u'',
               u'16'], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 4, 1)
            table.mergeCells(0, 1, 4, 1)
            table.mergeCells(0, 2, 1, 2)
            table.mergeCells(1, 2, 3, 1)
            table.mergeCells(1, 3, 3, 1)
            table.mergeCells(0, 4, 1, 9)
            table.mergeCells(0, 13, 1, 2)
            table.mergeCells(1, 4, 3, 1)
            table.mergeCells(1, 5, 3, 1)
            table.mergeCells(0, 15, 4, 1)
            table.mergeCells(1, 6, 1, 2)
            table.mergeCells(2, 6, 2, 1)
            table.mergeCells(2, 7, 2, 1)
            table.mergeCells(1, 8, 1, 2)
            table.mergeCells(2, 8, 2, 1)
            table.mergeCells(2, 9, 2, 1)
            table.mergeCells(1, 10, 3, 1)
            table.mergeCells(1, 11, 1, 2)
            table.mergeCells(2, 11, 2, 1)
            table.mergeCells(2, 12, 2, 1)
            table.mergeCells(1, 13, 3, 1)
            table.mergeCells(1, 14, 3, 1)
            cnt = 0

            def getHospitalBedId():
                cond = []
                tableVHospitalBedSchedule = tableVHospitalBed.innerJoin(tableOS, tableVHospitalBed['master_id'].eq(tableOS['id']))
                cond.append(tableOS['type'].ne(0))
                cond.append(tableOS['deleted'].eq(0))
                if orgStructureIdList:
                    cond.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
                if bedsSchedule:
                    tableVHospitalBedSchedule = tableVHospitalBedSchedule.innerJoin(tableHBSchedule, tableVHospitalBed['schedule_id'].eq(tableHBSchedule['id']))
                if bedsSchedule == 1:
                    cond.append(tableVHospitalBed['code'].eq(1))
                elif bedsSchedule == 2:
                    cond.append(tableVHospitalBed['code'].ne(1))
                if not isPermanentBed:
                    cond.append(tableVHospitalBed['isPermanent'].eq(1))
                joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].ge(begDateTime)])
                joinOr2 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].lt(endDateTime)])
                cond.append(db.joinAnd([joinOr1, joinOr2]))
                return db.getDistinctIdList(tableVHospitalBedSchedule, [tableVHospitalBed['id']], cond)

            def getBedForProfile(noProfileBed, profile = None, hospitalBedIdList = None, countSetText = True, row = None, column = None):
                tableRbAPHBP = db.table('ActionProperty_rbHospitalBedProfile')
                tableAP = db.table('ActionProperty')
                tableAction = db.table('Action')
                tableAPT = db.table('ActionPropertyType')
                tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')
                queryTable = tableRbAPHBP.innerJoin(tableAP, tableRbAPHBP['id'].eq(tableAP['id']))
                queryTable = queryTable.innerJoin(tableRbHospitalBedProfile, tableRbHospitalBedProfile['id'].eq(tableRbAPHBP['value']))
                queryTable = queryTable.innerJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
                cond = [tableAP['action_id'].isNotNull(),
                 tableAP['deleted'].eq(0),
                 tableAction['deleted'].eq(0),
                 tableAPT['deleted'].eq(0),
                 tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%')),
                 tableAPT['typeName'].like('rbHospitalBedProfile')]
                if profile:
                    if noProfileBed and len(profile) > 1:
                        cond.append(db.joinOr([tableRbHospitalBedProfile['profile_id'].inlist(profile), tableRbHospitalBedProfile['profile_id'].isNull()]))
                    else:
                        cond.append(tableRbHospitalBedProfile['id'].inlist(profile))
                else:
                    cond.append(tableRbHospitalBedProfile['id'].isNull())
                joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
                joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)])
                joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDateTime)])
                cond.append(db.joinOr([joinOr1, joinOr2, joinOr3]))
                cond.append(u"EXISTS(SELECT APHB.value\nFROM ActionProperty AS AP\nINNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.`id`=AP.`id`\nINNER JOIN Action AS A ON A.`id`=AP.`action_id`\nINNER JOIN ActionPropertyType AS APT ON APT.`id`=AP.`type_id`\nWHERE (AP.`action_id` IS NOT NULL AND AP.`action_id` = Action.id) AND (AP.`deleted`=0) AND (APT.`deleted`=0)\nAND (APT.`typeName` LIKE 'HospitalBed') AND (APHB.`value` IN (%s)))" % u','.join((str(hospitalBedId) for hospitalBedId in hospitalBedIdList if hospitalBedId)))
                if countSetText:
                    countBeds = db.getCount(queryTable, countCol='rbHospitalBedProfile.id', where=cond)
                    if row:
                        table.setText(row, column, countBeds)
                    else:
                        table.setText(5, column, countBeds)
                    return None
                else:
                    return db.getDistinctIdList(queryTable, [tableRbHospitalBedProfile['id']], cond)

            def getLeaved(begDateTime, endDateTime, orgStructureIdList, nameProperty = u'Переведен в отделение', profile = None):
                cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('leaved%')),
                 tableAction['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableAP['deleted'].eq(0),
                 tableActionType['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 tableAP['action_id'].eq(tableAction['id']),
                 tableAction['begDate'].isNotNull()]
                queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                cond.append('%s' % getDataAPHBnoPropertyForLeaved(False, nameProperty, False, profile if profile else [], u' AND A.endDate IS NOT NULL', u'Отделение', orgStructureIdList))
                cond.append(db.joinAnd([tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)]))
                ageSeniorsStmt = 'EXISTS(SELECT A.id\n        FROM Action AS A\n        INNER JOIN ActionType AS AT ON AT.id=A.actionType_id\n        INNER JOIN Event AS E ON A.event_id=E.id\n        INNER JOIN Client AS C ON E.client_id=C.id\n        WHERE A.deleted = 0 AND Action.id IS NOT NULL AND A.id = Action.id AND ((C.sex = 2 AND age(C.birthDate, A.begDate) >= 55) \n        OR (C.sex = 1 AND age(C.birthDate, A.begDate) >= 60) ))'
                stmt = db.selectStmt(queryTable, u'COUNT(DISTINCT(Client.id)) AS countAll, SUM(%s) AS seniorsCount, SUM(%s) AS countDeath, SUM(%s) AS countTransfer' % (ageSeniorsStmt, getStringProperty(u'Исход госпитализации', u"(APS.value LIKE 'умер%%' OR APS.value LIKE 'смерть%%')"), getStringProperty(u'Исход госпитализации', u"(APS.value LIKE 'переведен в другой стационар')")), where=cond)
                query = db.query(stmt)
                if query.first():
                    record = query.record()
                    return [forceInt(record.value('countAll')),
                     forceInt(record.value('seniorsCount')),
                     forceInt(record.value('countDeath')),
                     forceInt(record.value('countTransfer'))]
                else:
                    return [0,
                     0,
                     0,
                     0]

            def unrolledHospitalBed(endDate, profile = None):
                cond = []
                tableVHospitalBedSchedule = tableVHospitalBed.innerJoin(tableOS, tableVHospitalBed['master_id'].eq(tableOS['id']))
                cond.append(tableOS['type'].ne(0))
                cond.append(tableOS['deleted'].eq(0))
                cond.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
                if profile:
                    cond.append(tableVHospitalBed['profile_id'].inlist(profile))
                joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].le(endDate)])
                joinOr2 = db.joinOr([tableVHospitalBed['endDate'].isNull(), tableVHospitalBed['endDate'].ge(endDate)])
                cond.append(db.joinAnd([joinOr1, joinOr2]))
                countBeds = db.getCount(tableVHospitalBedSchedule, countCol='vHospitalBed.id', where=cond)
                return countBeds

            def unrolledHospitalBedsMonth(row, monthEnd, profile = None):
                if endDateTime:
                    yearDateInt = endDateTime.year()
                elif begDateTime > QtCore.QDate.currentDate():
                    yearDateInt = begDateTime.year()
                else:
                    currentDate = QtCore.QDate.currentDate()
                    yearDateInt = currentDate.year()
                monthEndDate = QtCore.QDate(yearDateInt, monthEnd, 1)
                endDate = QtCore.QDate(yearDateInt, monthEnd, monthEndDate.daysInMonth())
                return unrolledHospitalBed(endDate, profile)

            def averageYarHospitalBed(orgStructureIdList, table, begDate, endDate, profile = None, row = None, isHospital = None, countMonths = None):
                days = 0
                daysMonths = 0
                begDatePeriod = begDate
                endDatePeriod = begDatePeriod.addMonths(1)
                while endDatePeriod <= endDate:
                    days = averageDaysHospitalBed(orgStructureIdList, begDatePeriod, endDatePeriod, profile, isHospital)
                    daysMonths += days / begDatePeriod.daysInMonth()
                    begDatePeriod = begDatePeriod.addMonths(1)
                    endDatePeriod = endDatePeriod.addMonths(1)

                if countMonths == 12:
                    daysMonths = daysMonths / 12
                elif countMonths == 6:
                    daysMonths = daysMonths / 6
                return daysMonths

            def averageDaysHospitalBed(orgStructureIdList, begDatePeriod, endDatePeriod, profile = None, isHospital = None):
                days = 0
                db = QtGui.qApp.db
                tableOSHB = db.table('OrgStructure_HospitalBed')
                tableOrg = db.table('Organisation')
                tableOS = db.table('OrgStructure')
                queryTable = tableOSHB.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
                queryTable = queryTable.innerJoin(tableOrg, tableOrg['id'].eq(tableOS['organisation_id']))
                cond = [tableOSHB['master_id'].inlist(orgStructureIdList),
                 tableOrg['deleted'].eq(0),
                 tableOS['deleted'].eq(0),
                 tableOS['type'].ne(0)]
                if isHospital != None:
                    cond.append(tableOrg['isHospital'].eq(isHospital))
                joinAnd = db.joinAnd([tableOSHB['endDate'].isNull(), db.joinOr([db.joinAnd([tableOSHB['begDate'].isNotNull(), tableOSHB['begDate'].lt(endDatePeriod)]), tableOSHB['begDate'].isNull()])])
                cond.append(db.joinOr([db.joinAnd([tableOSHB['endDate'].isNotNull(),
                  tableOSHB['endDate'].gt(begDatePeriod),
                  tableOSHB['begDate'].isNotNull(),
                  tableOSHB['begDate'].lt(endDatePeriod)]), joinAnd]))
                if profile:
                    cond.append(tableOSHB['profile_id'].eq(profile))
                stmt = db.selectStmt(queryTable, [tableOSHB['id'], tableOSHB['begDate'], tableOSHB['endDate']], where=cond)
                query = db.query(stmt)
                bedIdList = []
                while query.next():
                    record = query.record()
                    bedId = forceRef(record.value('id'))
                    if bedId not in bedIdList:
                        bedIdList.append(bedId)
                        begDate = forceDate(record.value('begDate'))
                        endDate = forceDate(record.value('endDate'))
                        if not begDate or begDate < begDatePeriod:
                            begDate = begDatePeriod
                        if not endDate or endDate > endDatePeriod:
                            endDate = endDatePeriod
                        if begDate and endDate:
                            if begDate == endDate:
                                days += 1
                            else:
                                days += begDate.daysTo(endDate)

                return days

            def getReceived(begDateTime, endDateTime, orgStructureIdList, nameProperty = u'Переведен из отделения', profile = None):
                cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
                 tableAction['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableAP['deleted'].eq(0),
                 tableActionType['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 tableAP['action_id'].eq(tableAction['id']),
                 tableAction['endDate'].isNotNull(),
                 tableAction['begDate'].isNotNull(),
                 tableOS['type'].ne(0),
                 tableOS['deleted'].eq(0),
                 tableAPT['name'].like(u'Направлен в отделение'),
                 tableOS['id'].inlist(orgStructureIdList)]
                queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                queryTable = queryTable.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
                queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
                cond.append('%s' % getDataAPHBnoProperty(False, nameProperty, False, profile if profile else [], u'', u'Отделение пребывания', orgStructureIdList))
                cond.append(db.joinAnd([tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)]))
                ageChildStmt = 'EXISTS(SELECT A.id\n    FROM Action AS A\n    INNER JOIN ActionType AS AT ON AT.id=A.actionType_id\n    INNER JOIN Event AS E ON A.event_id=E.id\n    INNER JOIN Client AS C ON E.client_id=C.id\n    WHERE A.deleted = 0 AND Action.id IS NOT NULL AND A.id = Action.id AND (age(C.birthDate, A.begDate)) <= 17)'
                ageSeniorsStmt = 'EXISTS(SELECT A.id\n    FROM Action AS A\n    INNER JOIN ActionType AS AT ON AT.id=A.actionType_id\n    INNER JOIN Event AS E ON A.event_id=E.id\n    INNER JOIN Client AS C ON E.client_id=C.id\n    WHERE A.deleted = 0 AND Action.id IS NOT NULL AND A.id = Action.id AND ((C.sex = 2 AND age(C.birthDate, A.begDate) >= 55) \n    OR (C.sex = 1 AND age(C.birthDate, A.begDate) >= 60) ))'
                stmt = db.selectStmt(queryTable, u'COUNT(Client.id) AS countAll, SUM(%s) AS childrenCount, SUM(%s) AS seniorsCount, SUM(%s) AS clientRural' % (ageChildStmt, ageSeniorsStmt, getKladrClientRural()), where=cond)
                query = db.query(stmt)
                if query.first():
                    record = query.record()
                    return [forceInt(record.value('countAll')),
                     forceInt(record.value('childrenCount')),
                     forceInt(record.value('seniorsCount')),
                     forceInt(record.value('clientRural'))]
                else:
                    return [0,
                     0,
                     0,
                     0]

            def getLeavedDeath(begDateTime, endDateTime, orgStructureIdList, nameProperty = u'Переведен в отделение', profile = None):
                cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('leaved%')),
                 tableAction['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableAP['deleted'].eq(0),
                 tableActionType['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 tableAP['action_id'].eq(tableAction['id']),
                 tableAction['begDate'].isNotNull()]
                queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                cond.append('%s' % getDataAPHBnoPropertyForLeaved(False, nameProperty, False, profile if profile else [], u' AND A.endDate IS NOT NULL', u'Отделение', orgStructureIdList))
                cond.append(db.joinAnd([tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)]))
                cond.append(getStringProperty(u'Исход госпитализации', u"(APS.value LIKE 'умер%' OR APS.value LIKE 'смерть%')"))
                ageSeniorsStmt = 'EXISTS(SELECT A.id\n    FROM Action AS A\n    INNER JOIN ActionType AS AT ON AT.id=A.actionType_id\n    INNER JOIN Event AS E ON A.event_id=E.id\n    INNER JOIN Client AS C ON E.client_id=C.id\n    WHERE A.deleted = 0 AND Action.id IS NOT NULL AND A.id = Action.id AND ((C.sex = 2 AND age(C.birthDate, A.begDate) >= 55) \n    OR (C.sex = 1 AND age(C.birthDate, A.begDate) >= 60) ))'
                stmt = db.selectStmt(queryTable, u'COUNT(DISTINCT(Client.id)) AS countDeathAll, SUM(%s) AS seniorsCount' % ageSeniorsStmt, where=cond)
                query = db.query(stmt)
                if query.first():
                    record = query.record()
                    return [forceInt(record.value('countDeathAll')), forceInt(record.value('seniorsDeathCount'))]
                else:
                    return [0, 0]

            def dataMovingDays(orgStructureIdList, begDatePeriod, endDatePeriod, profile = None):
                days = 0
                db = QtGui.qApp.db
                tableAPT = db.table('ActionPropertyType')
                tableAP = db.table('ActionProperty')
                tableActionType = db.table('ActionType')
                tableAction = db.table('Action')
                tableEvent = db.table('Event')
                tableClient = db.table('Client')
                tableOrg = db.table('Organisation')
                tableOS = db.table('OrgStructure')
                tableAPHB = db.table('ActionProperty_HospitalBed')
                tableOSHB = db.table('OrgStructure_HospitalBed')
                queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
                queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
                queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
                queryTable = queryTable.innerJoin(tableOrg, tableOrg['id'].eq(tableOS['organisation_id']))
                cond = [tableActionType['flatCode'].like('moving%'),
                 tableAction['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableAP['deleted'].eq(0),
                 tableActionType['deleted'].eq(0),
                 tableAPT['deleted'].eq(0),
                 tableOS['deleted'].eq(0),
                 tableOS['type'].ne(0),
                 tableClient['deleted'].eq(0),
                 tableOrg['deleted'].eq(0),
                 tableAPT['typeName'].like('HospitalBed'),
                 tableAP['action_id'].eq(tableAction['id'])]
                if profile:
                    cond.append(tableOSHB['profile_id'].inlist(profile))
                cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
                joinAnd = db.joinAnd([tableAction['endDate'].isNull(), tableAction['begDate'].isNotNull(), tableAction['begDate'].lt(endDatePeriod)])
                cond.append(db.joinOr([db.joinAnd([tableAction['endDate'].isNotNull(),
                  tableAction['endDate'].gt(begDatePeriod),
                  tableAction['begDate'].isNotNull(),
                  tableAction['begDate'].lt(endDatePeriod)]), joinAnd]))
                cols = [tableEvent['id'].alias('eventId'),
                 tableAction['id'].alias('actionId'),
                 tableAction['begDate'],
                 tableAction['endDate']]
                cols.append('(IF((Client.sex = 2 AND age(Client.birthDate, Action.begDate) >= 55) \n                OR (Client.sex = 1 AND age(Client.birthDate, Action.begDate) >= 60), 1, 0)) AS seniorsAge')
                stmt = db.selectStmt(queryTable, cols, cond)
                query = db.query(stmt)
                actionIdList = []
                daysSeniorsAge = 0
                while query.next():
                    record = query.record()
                    actionId = forceRef(record.value('actionId'))
                    seniorsAge = forceInt(record.value('seniorsAge'))
                    if actionId not in actionIdList:
                        actionIdList.append(actionId)
                        begDate = forceDate(record.value('begDate'))
                        endDate = forceDate(record.value('endDate'))
                        if begDate < begDatePeriod:
                            begDate = begDatePeriod
                        if not endDate or endDate > endDatePeriod:
                            endDate = endDatePeriod
                        if begDate and endDate:
                            if begDate == endDate:
                                days += 1
                                if seniorsAge:
                                    daysSeniorsAge += 1
                            else:
                                days += begDate.daysTo(endDate)
                                if seniorsAge:
                                    daysSeniorsAge += begDate.daysTo(endDate)

                return (days, daysSeniorsAge)

            def dataInvolutionDays(orgStructureIdList, begDatePeriod, endDatePeriod, profile = None):
                days = 0
                db = QtGui.qApp.db
                tableVHospitalBed = db.table('vHospitalBed')
                tableOS = db.table('OrgStructure')
                condRepairs = [tableVHospitalBed['involution'].ne(0)]
                queryTable = tableVHospitalBed.innerJoin(tableOS, tableVHospitalBed['master_id'].eq(tableOS['id']))
                condRepairs.append(tableOS['type'].ne(0))
                condRepairs.append(tableOS['deleted'].eq(0))
                condRepairs.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
                if profile:
                    condRepairs.append(tableVHospitalBed['profile_id'].inlist(profile))
                condRepairs.append(db.joinOr([db.joinAnd([tableVHospitalBed['endDateInvolute'].isNull(), tableVHospitalBed['begDateInvolute'].isNull()]), db.joinAnd([tableVHospitalBed['begDateInvolute'].isNotNull(), tableVHospitalBed['begDateInvolute'].ge(begDatePeriod), tableVHospitalBed['begDateInvolute'].lt(endDatePeriod)]), db.joinAnd([tableVHospitalBed['endDateInvolute'].isNotNull(), tableVHospitalBed['endDateInvolute'].gt(begDatePeriod), tableVHospitalBed['endDateInvolute'].le(endDatePeriod)])]))
                stmt = db.selectStmt(queryTable, [tableVHospitalBed['id'].alias('bedId'), tableVHospitalBed['begDateInvolute'], tableVHospitalBed['endDateInvolute']], condRepairs)
                query = db.query(stmt)
                bedIdList = []
                while query.next():
                    record = query.record()
                    bedId = forceRef(record.value('bedId'))
                    if bedId not in bedIdList:
                        bedIdList.append(bedId)
                        begDate = forceDate(record.value('begDateInvolute'))
                        endDate = forceDate(record.value('endDateInvolute'))
                        if not begDate or begDate < begDatePeriod:
                            begDate = begDatePeriod
                        if not endDate or endDate > endDatePeriod:
                            endDate = endDatePeriod
                        if begDate and endDate:
                            if begDate == endDate:
                                days += 1
                            else:
                                days += begDate.daysTo(endDate)

                return days

            tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')
            cond = []
            profileIdList = []
            self.hospitalBedIdList = []
            if orgStructureIdList:
                cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
            if QtGui.qApp.defaultHospitalBedProfileByMoving():
                self.hospitalBedIdList = getHospitalBedId()
                tableRbAPHBP = db.table('ActionProperty_rbHospitalBedProfile')
                tableAP = db.table('ActionProperty')
                tableAction = db.table('Action')
                tableAPT = db.table('ActionPropertyType')
                queryTable = tableRbAPHBP.innerJoin(tableAP, tableRbAPHBP['id'].eq(tableAP['id']))
                queryTable = queryTable.innerJoin(tableRbHospitalBedProfile, tableRbHospitalBedProfile['id'].eq(tableRbAPHBP['value']))
                queryTable = queryTable.innerJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
                cond = [tableAP['action_id'].isNotNull(),
                 tableAP['deleted'].eq(0),
                 tableAction['deleted'].eq(0),
                 tableAPT['deleted'].eq(0),
                 tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%')),
                 tableAPT['typeName'].like('rbHospitalBedProfile')]
                joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
                joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)])
                joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDateTime)])
                cond.append(db.joinOr([joinOr1, joinOr2, joinOr3]))
                cond.append(u"EXISTS(SELECT APHB.value\nFROM ActionProperty AS AP\nINNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.`id`=AP.`id`\nINNER JOIN Action AS A ON A.`id`=AP.`action_id`\nINNER JOIN ActionPropertyType AS APT ON APT.`id`=AP.`type_id`\nWHERE (AP.`action_id` IS NOT NULL AND AP.`action_id` = Action.id) AND (AP.`deleted`=0) AND (APT.`deleted`=0)\nAND (APT.`typeName` LIKE 'HospitalBed') AND (APHB.`value` IN (%s)))" % u','.join((str(hospitalBedId) for hospitalBedId in self.hospitalBedIdList if hospitalBedId)))
                records = db.getRecordList(queryTable, [tableRbHospitalBedProfile['id'], tableRbHospitalBedProfile['code'], tableRbHospitalBedProfile['name']], cond)
                for record in records:
                    profileId = forceRef(record.value('id'))
                    if profileId not in profileIdList:
                        profileIdList.append(profileId)

            else:
                if not noProfileBed:
                    cond.append('OrgStructure_HospitalBed.profile_id IS NOT NULL')
                if not isPermanentBed:
                    cond.append('OrgStructure_HospitalBed.isPermanent = 1')
                queryTable = tableOSHB.innerJoin(tableRbHospitalBedProfile, tableOSHB['profile_id'].eq(tableRbHospitalBedProfile['id']))
                queryTable = queryTable.innerJoin(tableOS, tableOSHB['master_id'].eq(tableOS['id']))
                cond.append(tableOS['type'].ne(0))
                cond.append(tableOS['deleted'].eq(0))
                if bedsSchedule:
                    queryTable = queryTable.innerJoin(tableHBSchedule, tableOSHB['schedule_id'].eq(tableHBSchedule['id']))
                    if bedsSchedule == 1:
                        cond.append(tableHBSchedule['code'].eq(1))
                    elif bedsSchedule == 2:
                        cond.append(tableHBSchedule['code'].ne(1))
                if profileBedId:
                    cond.append(tableRbHospitalBedProfile['id'].eq(profileBedId))
                profileIdList = db.getDistinctIdList(queryTable, [tableRbHospitalBedProfile['id']], cond)
            if not profileIdList:
                return doc
            if noProfileBed:
                profileIdList.append(None)
            rowProfileAll = table.addRow()
            cnt = 1
            table.setText(rowProfileAll, 0, cnt)
            table.setText(rowProfileAll, 1, u'всего')
            cnt += 1
            sumAllNoProfile = 0
            sumClientRuralNoProfile = 0
            sumCountBedsMonthNoProfile = 0
            sumDaysMonthsNoProfile = 0
            sumChildNoProfile = 0
            sumSeniorsNoProfile = 0
            sumCountLeavedAllNoProfile = 0
            sumSeniorsCountNoProfile = 0
            sumLeavedTransferNoProfile = 0
            sumDeathAllNoProfile = 0
            sumSeniorsDeathNoProfile = 0
            sumMovingDaysNoProfile = 0
            sumSeniorsMovingDaysNoProfile = 0
            sumInvolutionDaysNoProfile = 0
            if not profileBedId:
                rowProfile = table.addRow()
                table.setText(rowProfile, 0, cnt)
                table.setText(rowProfile, 1, u'профиль койки не определен')
            countBedsMonth = unrolledHospitalBedsMonth(rowProfileAll, 2, [])
            table.setText(rowProfileAll, 2, countBedsMonth)
            sumCountBedsMonthNoProfile = countBedsMonth
            daysMonths = averageYarHospitalBed(orgStructureIdList, table, begDateTime, endDateTime, [], rowProfileAll)
            table.setText(rowProfileAll, 3, daysMonths)
            sumDaysMonthsNoProfile = daysMonths
            allNoProfile, childNoProfile, seniorsNoProfile, clientRuralNoProfile = getReceived(begDateTime, endDateTime, orgStructureIdList, u'Переведен из отделения', [])
            table.setText(rowProfileAll, 4, allNoProfile)
            table.setText(rowProfileAll, 5, clientRuralNoProfile)
            table.setText(rowProfileAll, 6, childNoProfile)
            table.setText(rowProfileAll, 7, seniorsNoProfile)
            sumAllNoProfile = allNoProfile
            sumClientRuralNoProfile = clientRuralNoProfile
            sumChildNoProfile = childNoProfile
            sumSeniorsNoProfile = seniorsNoProfile
            countLeavedAll, seniorsCount, leavedDeath, leavedTransfer = getLeaved(begDateTime, endDateTime, orgStructureIdList, u'Переведен в отделение', [])
            table.setText(rowProfileAll, 8, countLeavedAll)
            table.setText(rowProfileAll, 9, seniorsCount)
            table.setText(rowProfileAll, 10, leavedTransfer)
            sumCountLeavedAllNoProfile = countLeavedAll
            sumSeniorsCountNoProfile = seniorsCount
            sumLeavedTransferNoProfile = leavedTransfer
            countLeavedDeathAll, seniorsDeathCount = getLeavedDeath(begDateTime, endDateTime, orgStructureIdList, u'Переведен в отделение', [])
            table.setText(rowProfileAll, 11, countLeavedDeathAll)
            table.setText(rowProfileAll, 12, seniorsDeathCount)
            sumDeathAllNoProfile = countLeavedDeathAll
            sumSeniorsDeathNoProfile = seniorsDeathCount
            movingDaysNoProfile, seniorsMovingDaysNoProfile = dataMovingDays(orgStructureIdList, begDateTime, endDateTime, [])
            table.setText(rowProfileAll, 13, movingDaysNoProfile)
            table.setText(rowProfileAll, 14, seniorsMovingDaysNoProfile)
            sumMovingDaysNoProfile = movingDaysNoProfile
            sumSeniorsMovingDaysNoProfile = seniorsMovingDaysNoProfile
            involutionDaysNoProfile = dataInvolutionDays(orgStructureIdList, begDateTime, endDateTime, [])
            table.setText(rowProfileAll, 15, involutionDaysNoProfile)
            sumInvolutionDaysNoProfile = involutionDaysNoProfile
            if not profileBedId:
                countBedsMonth = unrolledHospitalBedsMonth(rowProfile, 2, profileIdList)
                table.setText(rowProfile, 2, sumCountBedsMonthNoProfile - countBedsMonth)
                daysMonths = averageYarHospitalBed(orgStructureIdList, table, begDateTime, endDateTime, profileIdList, rowProfile)
                table.setText(rowProfile, 3, sumDaysMonthsNoProfile - daysMonths)
                all, children, seniors, clientRural = getReceived(begDateTime, endDateTime, orgStructureIdList, u'Переведен из отделения', profileIdList)
                table.setText(rowProfile, 4, sumAllNoProfile - all)
                table.setText(rowProfile, 5, sumClientRuralNoProfile - clientRural)
                table.setText(rowProfile, 6, sumChildNoProfile - children)
                table.setText(rowProfile, 7, seniors - sumSeniorsNoProfile)
                countLeavedAll, seniorsCount, leavedDeath, leavedTransfer = getLeaved(begDateTime, endDateTime, orgStructureIdList, u'Переведен в отделение', profileIdList)
                table.setText(rowProfile, 8, sumCountLeavedAllNoProfile - countLeavedAll)
                table.setText(rowProfile, 9, sumSeniorsCountNoProfile - seniorsCount)
                table.setText(rowProfile, 10, sumLeavedTransferNoProfile - leavedTransfer)
                countLeavedDeathAll, seniorsDeathCount = getLeavedDeath(begDateTime, endDateTime, orgStructureIdList, u'Переведен в отделение', profileIdList)
                table.setText(rowProfile, 11, sumDeathAllNoProfile - countLeavedDeathAll)
                table.setText(rowProfile, 12, sumSeniorsDeathNoProfile - seniorsDeathCount)
                movingDaysNoProfile, seniorsMovingDaysNoProfile = dataMovingDays(orgStructureIdList, begDateTime, endDateTime, profileIdList)
                table.setText(rowProfile, 13, sumMovingDaysNoProfile - movingDaysNoProfile)
                table.setText(rowProfile, 14, sumSeniorsMovingDaysNoProfile - seniorsMovingDaysNoProfile)
                involutionDaysNoProfile = dataInvolutionDays(orgStructureIdList, begDateTime, endDateTime, profileIdList)
                table.setText(rowProfile, 15, sumInvolutionDaysNoProfile - involutionDaysNoProfile)
            cond = []
            if QtGui.qApp.defaultHospitalBedProfileByMoving():
                queryTable = tableRbHospitalBedProfile
                if profileBedId and profileBedId in profileIdList:
                    cond.append(tableRbHospitalBedProfile['id'].eq(profileBedId))
                elif not profileBedId and profileIdList:
                    cond.append(tableRbHospitalBedProfile['id'].inlist(profileIdList))
            elif profileBedId:
                cond.append(tableRbHospitalBedProfile['id'].eq(profileBedId))
            stmt = db.selectStmt(queryTable, 
                                 [tableRbHospitalBedProfile['id'], tableRbHospitalBedProfile['code'], tableRbHospitalBedProfile['name']], 
                                 cond, 
                                 order = u'rbHospitalBedProfile.code',
                                 isDistinct = True)
            query = db.query(stmt)
            sizeQuery = query.size()
            if noProfileBed:
                if sizeQuery > 0:
                    rowProfile = table.addRow()
                    cnt += 1
            sizeQuery -= 1
            while query.next():
                record = query.record()
                profileId = forceRef(record.value('id'))
                profileCode = forceString(record.value('code'))
                profileName = forceString(record.value('name'))
                table.setText(rowProfile, 0, cnt)
                table.setText(rowProfile, 1, profileCode + u'-' + profileName)
                countBedsMonth = unrolledHospitalBedsMonth(rowProfile, 1, [profileId])
                table.setText(rowProfile, 2, countBedsMonth)
                daysMonths = averageYarHospitalBed(orgStructureIdList, table, begDateTime, endDateTime, [], rowProfile)
                table.setText(rowProfile, 3, daysMonths)
                all, children, seniorsCount, clientRural = getReceived(begDateTime, endDateTime, orgStructureIdList, u'Переведен из отделения', [profileId])
                table.setText(rowProfile, 4, all)
                table.setText(rowProfile, 5, clientRural)
                table.setText(rowProfile, 6, children)
                table.setText(rowProfile, 7, seniorsCount)
                countLeavedAll, seniorsCount, leavedDeath, leavedTransfer = getLeaved(begDateTime, endDateTime, orgStructureIdList, u'Переведен в отделение', [profileId])
                table.setText(rowProfile, 8, countLeavedAll)
                table.setText(rowProfile, 9, seniorsCount)
                table.setText(rowProfile, 10, leavedTransfer)
                countLeavedDeathAll, seniorsDeathCount = getLeavedDeath(begDateTime, endDateTime, orgStructureIdList, u'Переведен в отделение', [profileId])
                table.setText(rowProfile, 11, countLeavedDeathAll)
                table.setText(rowProfile, 12, seniorsDeathCount)
                movingDaysNoProfile, seniorsMovingDaysNoProfile = dataMovingDays(orgStructureIdList, begDateTime, endDateTime, [profileId])
                table.setText(rowProfile, 13, movingDaysNoProfile)
                table.setText(rowProfile, 14, seniorsMovingDaysNoProfile)
                involutionDaysNoProfile = dataInvolutionDays(orgStructureIdList, begDateTime, endDateTime, [profileId])
                table.setText(rowProfile, 15, involutionDaysNoProfile)
                if sizeQuery > 0:
                    rowProfile = table.addRow()
                    cnt += 1
                    sizeQuery -= 1

        return doc


class CStationaryF30_3101(CStationaryF30):

    def __init__(self, parent):
        CStationaryF30.__init__(self, parent)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара(3101)')

    def getLeaved_3101(self, begDateTime, endDateTime, orgStructureIdList, nameProperty = u'Переведен в отделение', profile = None):
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableContract = db.table('Contract')
        cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('leaved%')),
         tableAction['deleted'].eq(0),
         tableEvent['deleted'].eq(0),
         tableAP['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableContract['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableAP['action_id'].eq(tableAction['id']),
         tableAction['begDate'].isNotNull()]
        queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
        queryTable = queryTable.innerJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))
        cond.append('%s' % getDataAPHBnoPropertyForLeaved(False, nameProperty, False, profile if profile else [], u' AND A.endDate IS NOT NULL', u'Отделение', orgStructureIdList))
        cond.append(db.joinAnd([tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)]))
        financeStmt = '(IF(Action.finance_id IS NOT NULL, (SELECT rbFinance.code FROM rbFinance WHERE rbFinance.id = Action.finance_id), NULL)) AS codeActionFinance, \n        (IF(Contract.finance_id IS NOT NULL, (SELECT rbFinance.code FROM rbFinance WHERE rbFinance.id = Contract.finance_id), NULL)) AS codeContractFinance'
        stmt = db.selectStmt(queryTable, u'Event.id AS eventId, %s AS transfer, %s' % (getStringProperty(u'Исход госпитализации', u"(APS.value LIKE 'переведен в другой стационар')"), financeStmt), where=cond)
        query = db.query(stmt)
        transferCount = 0
        codeFinanceOMCCount = 0
        codeFinanceDMCCount = 0
        codeFinancePayMentCount = 0
        eventIdList = []
        while query.next():
            record = query.record()
            transferCount += forceInt(record.value('transfer'))
            eventId = forceRef(record.value('eventId'))
            if eventId and eventId not in eventIdList:
                eventIdList.append(eventId)
            codeActionFinance = forceString(record.value('codeActionFinance'))
            if codeActionFinance:
                codeFinanceOMCCount += 1 if codeActionFinance == '2' else 0
                codeFinanceDMCCount += 1 if codeActionFinance == '3' else 0
                codeFinancePayMentCount += 1 if codeActionFinance == '4' else 0
            else:
                codeContractFinance = forceString(record.value('codeContractFinance'))
                if codeContractFinance:
                    codeFinanceOMCCount += 1 if codeContractFinance == '2' else 0
                    codeFinanceDMCCount += 1 if codeContractFinance == '3' else 0
                    codeFinancePayMentCount += 1 if codeContractFinance == '4' else 0

        return [transferCount,
         codeFinanceOMCCount,
         codeFinanceDMCCount,
         codeFinancePayMentCount,
         eventIdList]

    def dataMovingDays_3101(self, orgStructureIdList, begDatePeriod, endDatePeriod, eventIdList, profile = None):
        codeFinanceOMCDays = 0
        codeFinanceDMCDays = 0
        codeFinancePayMentDays = 0
        if eventIdList:
            db = QtGui.qApp.db
            tableAPT = db.table('ActionPropertyType')
            tableAP = db.table('ActionProperty')
            tableActionType = db.table('ActionType')
            tableAction = db.table('Action')
            tableEvent = db.table('Event')
            tableClient = db.table('Client')
            tableOrg = db.table('Organisation')
            tableOS = db.table('OrgStructure')
            tableAPHB = db.table('ActionProperty_HospitalBed')
            tableOSHB = db.table('OrgStructure_HospitalBed')
            tableContract = db.table('Contract')
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            queryTable = queryTable.innerJoin(tableOrg, tableOrg['id'].eq(tableOS['organisation_id']))
            queryTable = queryTable.innerJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableActionType['flatCode'].like('moving%'),
             tableAction['deleted'].eq(0),
             tableEvent['deleted'].eq(0),
             tableAP['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableAPT['deleted'].eq(0),
             tableOS['deleted'].eq(0),
             tableOS['type'].ne(0),
             tableClient['deleted'].eq(0),
             tableOrg['deleted'].eq(0),
             tableContract['deleted'].eq(0),
             tableAPT['typeName'].like('HospitalBed'),
             tableAP['action_id'].eq(tableAction['id'])]
            if profile:
                cond.append(tableOSHB['profile_id'].inlist(profile))
            cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
            joinAnd = db.joinAnd([tableAction['endDate'].isNull(), tableAction['begDate'].isNotNull(), tableAction['begDate'].lt(endDatePeriod)])
            cond.append(db.joinOr([db.joinAnd([tableAction['endDate'].isNotNull(),
              tableAction['endDate'].gt(begDatePeriod),
              tableAction['begDate'].isNotNull(),
              tableAction['begDate'].lt(endDatePeriod)]), joinAnd]))
            cols = [tableEvent['id'].alias('eventId'),
             tableAction['id'].alias('actionId'),
             tableAction['begDate'],
             tableAction['endDate']]
            cols.append('(IF(Action.finance_id IS NOT NULL, (SELECT rbFinance.code FROM rbFinance WHERE rbFinance.id = Action.finance_id), NULL)) AS codeActionFinance, \n        (IF(Contract.finance_id IS NOT NULL, (SELECT rbFinance.code FROM rbFinance WHERE rbFinance.id = Contract.finance_id), NULL)) AS codeContractFinance')
            stmt = db.selectStmt(queryTable, cols, cond)
            query = db.query(stmt)
            actionIdList = []
            while query.next():
                record = query.record()
                actionId = forceRef(record.value('actionId'))
                codeActionFinance = forceString(record.value('codeActionFinance'))
                codeContractFinance = forceString(record.value('codeContractFinance'))
                if actionId not in actionIdList:
                    actionIdList.append(actionId)
                    begDate = forceDate(record.value('begDate'))
                    endDate = forceDate(record.value('endDate'))
                    if begDate < begDatePeriod:
                        begDate = begDatePeriod
                    if not endDate or endDate > endDatePeriod:
                        endDate = endDatePeriod
                    if begDate and endDate:
                        if codeActionFinance:
                            if codeActionFinance == '2':
                                if begDate == endDate:
                                    codeFinanceOMCDays += 1
                                else:
                                    codeFinanceOMCDays += begDate.daysTo(endDate)
                            elif codeActionFinance == '3':
                                if begDate == endDate:
                                    codeFinanceDMCDays += 1
                                else:
                                    codeFinanceDMCDays += begDate.daysTo(endDate)
                            elif codeActionFinance == '4':
                                if begDate == endDate:
                                    codeFinancePayMentDays += 1
                                else:
                                    codeFinancePayMentDays += begDate.daysTo(endDate)
                        elif codeContractFinance:
                            if codeContractFinance == '2':
                                if begDate == endDate:
                                    codeFinanceOMCDays += 1
                                else:
                                    codeFinanceOMCDays += begDate.daysTo(endDate)
                            elif codeContractFinance == '3':
                                if begDate == endDate:
                                    codeFinanceDMCDays += 1
                                else:
                                    codeFinanceDMCDays += begDate.daysTo(endDate)
                            elif codeContractFinance == '4':
                                if begDate == endDate:
                                    codeFinancePayMentDays += 1
                                else:
                                    codeFinancePayMentDays += begDate.daysTo(endDate)

        return (codeFinanceOMCDays, codeFinanceDMCDays, codeFinancePayMentDays)

    def getVisitStationary(self, orgStructureIdList, begDatePeriod, endDatePeriod, eventIdList, profile = None):
        db = QtGui.qApp.db
        tableEventType = db.table('EventType')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableOS = db.table('OrgStructure')
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableVisit = db.table('Visit')
        tableRBFinance = db.table('rbFinance')
        queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
        queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
        queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
        queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
        queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        queryTable = queryTable.innerJoin(tableVisit, tableVisit['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableRBFinance, tableRBFinance['id'].eq(tableVisit['finance_id']))
        cond = [tableActionType['flatCode'].like('moving%'),
         tableAction['deleted'].eq(0),
         tableEvent['deleted'].eq(0),
         tableAP['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableAPT['deleted'].eq(0),
         tableOS['deleted'].eq(0),
         tableOS['type'].ne(0),
         tableClient['deleted'].eq(0),
         tableVisit['deleted'].eq(0),
         tableAPT['typeName'].like('HospitalBed'),
         tableAP['action_id'].eq(tableAction['id']),
         tableRBFinance['code'].like(u'4')]
        cond.append(u"(EventType.medicalAidType_id IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN ('1', '2', '3', '7')))")
        if profile:
            cond.append(tableOSHB['profile_id'].inlist(profile))
        cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
        joinAnd = db.joinAnd([tableAction['endDate'].isNull(), tableAction['begDate'].isNotNull(), tableAction['begDate'].lt(endDatePeriod)])
        cond.append(db.joinOr([db.joinAnd([tableAction['endDate'].isNotNull(),
          tableAction['endDate'].gt(begDatePeriod),
          tableAction['begDate'].isNotNull(),
          tableAction['begDate'].lt(endDatePeriod)]), joinAnd]))
        stmt = db.selectStmt(queryTable, u'COUNT(Visit.id) AS visitCount', cond)
        query = db.query(stmt)
        if query.first():
            record = query.record()
            return forceInt(record.value('visitCount'))
        return 0

    def build(self, params):
        endDateTime = getVal(params, 'endDate', QtCore.QDate())
        begDateTime = getVal(params, 'begDate', QtCore.QDate())
        if not endDateTime:
            endDateTime = QtCore.QDate.currentDate()
        if endDateTime and begDateTime:
            profileBedId = params.get('profileBed', None)
            orgStructureIndex = self.stationaryF30SetupDialog.cmbOrgStructure._model.index(self.stationaryF30SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF30SetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertBlock()
            self.getCaption(cursor, params, u'Листок учета движения больных и коечного фонда стационара(3101)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('10%', [u'№ графы'], CReportBase.AlignLeft), ('70%', [u'Строка'], CReportBase.AlignLeft), ('20%', [u''], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            leavedTransfer, codeFinanceOMCCount, codeFinanceDMCCount, codeFinancePayMentCount, eventIdList = self.getLeaved_3101(begDateTime, endDateTime, orgStructureIdList, u'Переведен в отделение', [profileBedId] if profileBedId else [])
            codeFinanceOMCDays, codeFinanceDMCDays, codeFinancePayMentDays = self.dataMovingDays_3101(orgStructureIdList, begDateTime, endDateTime, eventIdList, [profileBedId] if profileBedId else [])
            visitCount = self.getVisitStationary(orgStructureIdList, begDateTime, endDateTime, [profileBedId] if profileBedId else [])
            for rows in MainRows:
                rowProfile = table.addRow()
                table.setText(rowProfile, 0, rows[0])
                table.setText(rowProfile, 1, rows[1])

            table.setText(1, 2, leavedTransfer)
            table.setText(2, 2, u'-')
            table.setText(3, 2, codeFinanceOMCCount)
            table.setText(4, 2, codeFinanceDMCCount + codeFinancePayMentCount)
            table.setText(5, 2, codeFinanceDMCCount)
            table.setText(6, 2, codeFinanceOMCDays)
            table.setText(7, 2, codeFinanceDMCDays + codeFinancePayMentDays)
            table.setText(8, 2, codeFinancePayMentDays)
            table.setText(9, 2, visitCount)
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertBlock()
            cursor.insertText(u'*) Исключая больных, выбывших с дермато-венерологических коек.')
            cursor.insertBlock()
        return doc


def getDataAPHBnoProperty(isPermanentBed, nameProperty, noProfileBed, profileList=None, endDate=u'',
                          namePropertyStay=u'Отделение пребывания', orgStructureIdList=None, isMedical=None,
                          bedsSchedule=None):
    if not profileList:
        profileList = []
    if not orgStructureIdList:
        orgStructureIdList = []
    strIsMedical = u''
    strIsMedicalJoin = u''
    strIsScheduleJoin = u''
    if isMedical != None:
        strIsMedicalJoin += u' INNER JOIN OrgStructure AS OS ON OSHB.master_id = OS.id INNER JOIN Organisation AS ORG ON OS.organisation_id = ORG.id'
        strIsMedical += u' AND OS.type != 0 AND ORG.isMedical = %d' % isMedical
    strFilter = u''
    if not isPermanentBed:
        strFilter += u' AND OSHB.isPermanent = 1'
    if profileList:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            strFilter += u' AND (' + getPropertyAPHBP(profileList, noProfileBed) + u')'
        else:
            strFilter += u' AND (OSHB.profile_id IN (%s)%s)' % (','.join((forceString(profile) for profile in profileList if profile)), u' OR OSHB.profile_id IS NULL' if noProfileBed and len(profileList) > 1 else u'')
    elif noProfileBed:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            strFilter += u' AND EXISTS(' + getPropertyAPHBPNoProfile() + u')'
        else:
            strFilter += u' AND OSHB.profile_id IS NULL'
    if bedsSchedule:
        strIsScheduleJoin += u' INNER JOIN rbHospitalBedShedule AS HBS ON OSHB.schedule_id = HBS.id'
    if bedsSchedule == 1:
        strFilter += u' AND HBS.code = 1'
    elif bedsSchedule == 2:
        strFilter += u' AND HBS.code != 1'
    return "EXISTS(SELECT APHB.value\nFROM ActionType AS AT\nINNER JOIN Action AS A ON AT.id=A.actionType_id\nINNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id\nINNER JOIN ActionProperty AS AP ON AP.type_id=APT.id\nINNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id\nINNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value%s%s\nWHERE A.event_id=Event.id%s%s AND A.deleted=0 AND APT.actionType_id=A.actionType_id AND AP.action_id=A.id AND AP.deleted=0 AND APT.deleted=0 AND APT.typeName LIKE 'HospitalBed'%s AND (NOT %s)%s)" % (strIsMedicalJoin,
     strIsScheduleJoin,
     strIsMedical,
     endDate,
     strFilter,
     getTransferProperty(nameProperty),
     u' AND %s' % (getDataOrgStructureStay(namePropertyStay, orgStructureIdList) if orgStructureIdList else u''))


def getDataAPHBnoPropertyForLeaved(isPermanentBed, nameProperty, noProfileBed, profileList=None, endDate=u'',
                                   namePropertyStay=u'Отделение', orgStructureIdList=None, isMedical=None,
                                   bedsSchedule=None):
    if not profileList:
        profileList = []
    if not orgStructureIdList:
        orgStructureIdList = []
    strIsMedical = u''
    strIsMedicalJoin = u''
    strIsScheduleJoin = u''
    if isMedical != None:
        strIsMedicalJoin += u' INNER JOIN OrgStructure AS OS ON OSHB.master_id = OS.id INNER JOIN Organisation AS ORG ON OS.organisation_id = ORG.id'
        strIsMedical += u' AND OS.type != 0 AND ORG.isMedical = %d' % isMedical
    strFilter = u''
    if not isPermanentBed:
        strFilter += u' AND OSHB.isPermanent = 1'
    if profileList:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            strFilter += u' AND (' + getPropertyAPHBP(profileList, noProfileBed) + u')'
        else:
            strFilter += u' AND (OSHB.profile_id IN (%s)%s)' % (','.join((forceString(profile) for profile in profileList if profile)), u' OR OSHB.profile_id IS NULL' if noProfileBed and len(profileList) > 1 else u'')
    elif noProfileBed:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            strFilter += u' AND EXISTS(' + getPropertyAPHBPNoProfile() + u')'
        else:
            strFilter += u' AND OSHB.profile_id IS NULL'
    if bedsSchedule:
        strIsScheduleJoin += u' INNER JOIN rbHospitalBedShedule AS HBS ON OSHB.schedule_id = HBS.id'
    if bedsSchedule == 1:
        strFilter += u' AND HBS.code = 1'
    elif bedsSchedule == 2:
        strFilter += u' AND HBS.code != 1'
    return "EXISTS(SELECT APHB.value\nFROM ActionType AS AT\nINNER JOIN Action AS A ON AT.id=A.actionType_id\nINNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id\nINNER JOIN ActionProperty AS AP ON AP.type_id=APT.id\nINNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id\nINNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value%s%s\nWHERE A.event_id=Event.id%s%s AND A.deleted=0 AND APT.actionType_id=A.actionType_id AND AP.action_id=A.id AND AP.deleted=0 AND APT.deleted=0 AND APT.typeName LIKE 'HospitalBed'%s %s)" % (strIsMedicalJoin,
     strIsScheduleJoin,
     strIsMedical,
     endDate,
     strFilter,
     u' AND %s' % (getDataOrgStructureStayForLeaved(namePropertyStay, orgStructureIdList) if orgStructureIdList else u''))


def getPropertyAPHBP(profileList, noProfileBed):
    return "EXISTS(SELECT APHBP.value\nFROM ActionPropertyType AS APT_Profile\nINNER JOIN ActionProperty AS AP_Profile ON AP_Profile.type_id=APT_Profile.id\nINNER JOIN ActionProperty_rbHospitalBedProfile AS APHBP ON APHBP.id=AP_Profile.id\nINNER JOIN rbHospitalBedProfile AS RBHBP ON RBHBP.id=APHBP.value\nWHERE APT_Profile.actionType_id = Action.actionType_id\nAND AP_Profile.action_id = Action.id\nAND AP_Profile.deleted = 0\nAND APT_Profile.deleted = 0\nAND APT_Profile.typeName LIKE 'rbHospitalBedProfile'\n%s)" % (u'AND (APHBP.value IN (%s)%s)' % (','.join((forceString(profile) for profile in profileList if profile)), u' OR APHBP.value IS NULL' if noProfileBed and len(profileList) > 1 else u'') if profileList else u'AND APHBP.value IS NULL')


def getPropertyAPHBPNoProfile():
    return "SELECT APHBP.value\nFROM ActionPropertyType AS APT_Profile\nLEFT JOIN ActionProperty AS AP_Profile ON AP_Profile.type_id=APT_Profile.id\nLEFT JOIN ActionProperty_rbHospitalBedProfile AS APHBP ON APHBP.id=AP_Profile.id\nLEFT JOIN rbHospitalBedProfile AS RBHBP ON RBHBP.id=APHBP.value\nWHERE APT_Profile.actionType_id = Action.actionType_id\nAND AP_Profile.action_id = Action.id\nAND AP_Profile.deleted = 0\nAND APT_Profile.deleted = 0\nAND APT_Profile.typeName LIKE 'rbHospitalBedProfile'\nAND APHBP.value IS NULL"


def getTransferProperty(nameProperty):
    return u"EXISTS(SELECT APOS2.value\n    FROM ActionPropertyType AS APT2\n    INNER JOIN ActionProperty AS AP2 ON AP2.type_id=APT2.id\n    INNER JOIN ActionProperty_OrgStructure AS APOS2 ON APOS2.id=AP2.id\n    INNER JOIN OrgStructure AS OS2 ON OS2.id=APOS2.value\n    WHERE APT2.actionType_id=A.actionType_id AND AP2.action_id=A.id AND APT2.deleted=0 AND APT2.name LIKE '%s' AND OS2.type != 0 AND OS2.deleted=0)" % nameProperty


def getStringProperty(nameProperty, value):
    return u"EXISTS(SELECT APS.id\n    FROM ActionPropertyType AS APT\n    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id\n    INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id\n    WHERE  Action.id IS NOT NULL AND APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND APT.name LIKE '%s' AND %s)" % (nameProperty, value)


def getDataOrgStructureStay(nameProperty, orgStructureIdList):
    orgStructureList = [u'NULL']
    for orgStructureId in orgStructureIdList:
        orgStructureList.append(forceString(orgStructureId))

    return "EXISTS(SELECT APOS2.value\n    FROM ActionPropertyType AS APT2\n    INNER JOIN ActionProperty AS AP2 ON AP2.type_id=APT2.id\n    INNER JOIN ActionProperty_OrgStructure AS APOS2 ON APOS2.id=AP2.id\n    INNER JOIN OrgStructure AS OS2 ON OS2.id=APOS2.value\n    WHERE APT2.actionType_id=A.actionType_id AND AP2.action_id=A.id AND APT2.deleted=0 AND APT2.name LIKE '%s' AND OS2.type != 0 AND OS2.deleted=0 AND APOS2.value %s)" % (nameProperty, u' IN (' + ','.join(orgStructureList) + ')')


def getDataOrgStructureStayForLeaved(nameProperty, orgStructureIdList):
    orgStructureList = [u'NULL']
    for orgStructureId in orgStructureIdList:
        orgStructureList.append(forceString(orgStructureId))

    return "EXISTS(SELECT APOS2.value\n    FROM ActionPropertyType AS APT2\n    INNER JOIN ActionProperty AS AP2 ON AP2.type_id=APT2.id\n    INNER JOIN ActionProperty_OrgStructure AS APOS2 ON APOS2.id=AP2.id\n    INNER JOIN OrgStructure AS OS2 ON OS2.id=APOS2.value\n    WHERE APT2.actionType_id=Action.actionType_id AND AP2.action_id=Action.id AND APT2.deleted=0 AND APT2.name LIKE '%s' AND OS2.type != 0 AND OS2.deleted=0 AND APOS2.value %s)" % (nameProperty, u' IN (' + ','.join(orgStructureList) + ')')


def getKladrClientRural():
    return u'EXISTS(SELECT kladr.KLADR.OCATD\n    FROM ClientAddress\n    INNER JOIN Address ON ClientAddress.address_id = Address.id\n    INNER JOIN AddressHouse ON Address.house_id = AddressHouse.id\n    INNER JOIN kladr.KLADR ON kladr.KLADR.CODE = AddressHouse.KLADRCode\n    WHERE Client.id IS NOT NULL AND ClientAddress.client_id = Client.id AND (((SUBSTRING(kladr.KLADR.OCATD,3,1) IN (1, 2, 4)) AND SUBSTRING(kladr.KLADR.OCATD,6,1) = 8) OR ((SUBSTRING(kladr.KLADR.OCATD,3,1) NOT IN (1, 2, 4))\n    AND SUBSTRING(kladr.KLADR.OCATD,6,1) = 9)))'


def getTransferPropertyInPeriod(nameProperty, begDateTime, endDateTime):
    return u"EXISTS(SELECT APOS.value\n    FROM ActionPropertyType AS APT\n    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id\n    INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id\n    INNER JOIN OrgStructure AS OS ON OS.id=APOS.value\n    WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND APT.name LIKE '%s' AND OS.type != 0 AND OS.deleted=0 AND (Action.begDate IS NULL OR (Action.begDate >= '%s' AND Action.begDate < '%s')))" % (nameProperty, begDateTime.toString(QtCore.Qt.ISODate), endDateTime.toString(QtCore.Qt.ISODate))