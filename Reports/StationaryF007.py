# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import *

from HospitalBeds.HospitalBedsDialog import getActionTypeIdListByFlatCode
from HospitalBeds.Utils import getTransferPropertyIn
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName, getOrgStructureFullNameList
from Reports.Report import CReportOrientation
from Reports.ReportBase import CReportBase, CReportTableBase, createTable
from Ui_StationaryF007Setup import Ui_StationaryF007SetupDialog
from library.DialogBase import CDialogBase
from library.Utils import forceBool, forceInt, forceRef, forceString, forceTime, getPref, getVal, setPref, toVariant


class CStationaryF007SetupDialog(CDialogBase, Ui_StationaryF007SetupDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        # self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        # self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.lstOrgStructure.setTable('OrgStructure')
        self.cmbProfileBed.setTable('rbHospitalBedProfile', True)
        self.chkDetailOrgStructure.setVisible(False)
        self.chkIsHideBeds.setVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegTime.setTime(params.get('begTime', QTime(7, 0)))
        self.edtEndDate.setDate(getVal(params, 'endDate', QDate.currentDate()))
        self.lstOrgStructure.setValues(getVal(params, 'orgStructures', []))
        self.cmbSchedule.setCurrentIndex(getVal(params, 'bedsSchedule', 0))
        self.cmbProfileBed.setValue(getVal(params, 'profileBed', None))
        self.chkDetailOrgStructure.setChecked(params.get('detailOrgStructure', False))
        self.chkIsHideBeds.setChecked(params.get('isHideBeds', False))

    def params(self):
        return {
            'begTime': self.edtBegTime.time(),
            'endDate': self.edtEndDate.date(),
            'orgStructures': self.lstOrgStructure.nameValues().keys(),
            'orgStructuresCount': self.lstOrgStructure.model().rowCount(),
            'bedsSchedule': self.cmbSchedule.currentIndex(),
            'profileBed': self.cmbProfileBed.value(),
            'detailOrgStructure': self.chkDetailOrgStructure.isChecked(),
            'isHideBeds': self.chkIsHideBeds.isChecked()
        }

    def loadPreferences(self, preferences):
        CDialogBase.loadPreferences(self, preferences)
        self.edtBegTime.setTime(forceTime(getPref(preferences, 'begTime', QTime())))

    def savePreferences(self):
        result = CDialogBase.savePreferences(self)
        setPref(result, 'begTime', toVariant(self.edtBegTime.time()))
        return result

    # @QtCore.pyqtSlot(int)
    # def on_cmbOrgStructure_currentIndexChanged(self, index):
    #     orgStructureId = self.cmbOrgStructure.value()

    @QtCore.pyqtSlot(QDate)
    def on_edtEndDate_dateChanged(self, date):
        endDate = date
        if endDate:
            begTime = self.edtBegTime.time() or QTime(9, 0)
            stringInfo = u'c %s до %s'%(forceString(QDateTime(endDate.addDays(-1), begTime)), forceString(QDateTime(endDate, begTime)))
        else:
            stringInfo = u'Введите дату'
        self.lblEndDate.setToolTip(stringInfo)

    @QtCore.pyqtSlot(bool)
    def on_chkIsHideBeds_toggled(self, checked):
        self.chkDetailOrgStructure.setEnabled(not checked)
        if checked:
            self.chkDetailOrgStructure.setChecked(checked)


class CStationaryF007(CReportOrientation):
    def __init__(self, parent):
        CReportOrientation.__init__(self, parent, QtGui.QPrinter.Landscape)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара')
        self.stationaryF007SetupDialog = None
        self.clientDeath = 8

    def getSetupDialog(self, parent):
        result = CStationaryF007SetupDialog(parent)
        self.stationaryF007SetupDialog = result
        return result

    @staticmethod
    def getOrgStructureIdList(treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []

    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = []
        endDate = params.get('endDate', QDate())
        description.append(u'Текущий день: ' + forceString(endDate))
        bedsSchedule = params.get('bedsSchedule', 0)
        description.append(u'режим койки: %s'%([u'Не учитывать', u'Круглосуточные', u'Не круглосуточные'][bedsSchedule]))
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    @staticmethod
    def getOrgInfo():
        orgId = QtGui.qApp.currentOrgId()
        orgName = u''
        orgOKPO = u''
        if orgId:
            record = QtGui.qApp.db.getRecordEx('Organisation',
                                               'shortName, OKPO',
                                               'id=%s AND deleted = 0' % (str(orgId)))
            if record:
                orgName = forceString(record.value('shortName'))
                orgOKPO = forceString(record.value('OKPO'))

        return orgName, orgOKPO

    @classmethod
    def insertCaption(cls, cursor, params, orgName, orgOKPO, title, headerRowCount=7):
        orgStructureIdList = params.get('orgStructures', None)
        orgStructureIdCount = params.get('orgStructureCount', None)

        underCaptionList = []
        if len(orgStructureIdList) != orgStructureIdCount:
            underCaptionList.append(u'подразделение: \n' + getOrgStructureFullNameList(orgStructureIdList) + u'.')
        else:
            underCaptionList.append(u'подразделение: ЛПУ')
        profileBedId = params.get('profileBed', None)
        if profileBedId:
            underCaptionList.append(u'профиль койки: %s'%(forceString(QtGui.qApp.db.translate('rbHospitalBedProfile', 'id', profileBedId, 'name'))))

        columns = [('50%', [], CReportBase.AlignLeft), ('50%', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=headerRowCount, border=0, cellPadding=2, cellSpacing=0)
        table.setText(0, 0, u'')
        table.setText(0, 1, u'Код формы по ОКУД ___________')
        table.setText(1, 0, u'')
        table.setText(1, 1, u'Код учреждения по ОКПО  %s'%(orgOKPO))
        table.setText(2, 0, u'')
        table.setText(2, 1, u'')
        table.setText(3, 0, u'')
        table.setText(3, 1, u'Медицинская документация')
        table.setText(4, 0, u'')
        table.setText(4, 1, u'Форма № 007/у')
        table.setText(5, 0, u'')
        table.setText(5, 1, u'Утверждена Минздравом СССР')
        table.setText(6, 0, orgName)
        table.setText(6, 1, u'04.10.80 г. № 1030')

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        columns2 = [('100%', [], CReportBase.AlignCenter)]
        table2 = createTable(cursor, columns2, headerRowCount=2, border=0, cellPadding=2, cellSpacing=0)
        table2.setText(0, 0, title, charFormat=boldChars)
        table2.setText(1, 0, u', '.join(underCaption for underCaption in underCaptionList if underCaption))

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        return table, table2


class CStationaryF007Moving(CStationaryF007):
    def __init__(self, parent):
        CStationaryF007.__init__(self, parent)

    @classmethod
    def insertCaption(cls, cursor, params, orgName, orgOKPO, title):
        table, _ = super(cls, cls).insertCaption(cursor, params, orgName, orgOKPO, title, headerRowCount=8)
        table.setText(4, 1, u'В настоящий момент действует форма № 007/у-02', clearBefore=True)
        table.setText(5, 1, u'Утверждена Приказом', clearBefore=True)
        table.setText(6, 0, u'', clearBefore=True)
        table.setText(6, 1, u'Минздрава России', clearBefore=True)
        table.setText(7, 0, orgName, clearBefore=True)
        table.setText(7, 1, u'от 30 декабря 2002 года N 413', clearBefore=True)

    @staticmethod
    def getHospitalBedIdList(db, tableVHospitalBed, tableHBSchedule, bedsSchedule, datetimeInterval, orgStructureIdList):
        cond = []
        queryTable = tableVHospitalBed
        begDateTime, endDateTime = datetimeInterval
        if orgStructureIdList:
            cond.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
        if bedsSchedule:
            queryTable = queryTable.innerJoin(tableHBSchedule, tableVHospitalBed['schedule_id'].eq(tableHBSchedule['id']))
        if bedsSchedule == 1:
            cond.append(tableHBSchedule['code'].eq(1))
        elif bedsSchedule == 2:
            cond.append(tableHBSchedule['code'].ne(1))
        joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].ge(begDateTime)])
        joinOr2 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].lt(endDateTime)])
        cond.append(db.joinAnd([joinOr1, joinOr2]))
        return db.getDistinctIdList(queryTable, [tableVHospitalBed['id']], cond)

    @staticmethod
    def getBedForProfile(db, dateTimeInterval, profile = None, hospitalBedIdList = None, textTable = None, row = None, column = None):
        """
        Подсчитывает число коек.

        :param db:
        :param dateTimeInterval:
        :param profile:
        :param hospitalBedIdList:
        :param textTable: таблица QTextTable для заполнения значеним кол-ва, если не указана, то данные вовзращаются в виде списка id коек
        :param row:
        :param column:
        :return:
        """
        tableRbAPHBP = db.table('ActionProperty_rbHospitalBedProfile')
        tableAP = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableAPT = db.table('ActionPropertyType')
        tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')
        begDateTime, endDateTime = dateTimeInterval
        queryTable = tableRbAPHBP.innerJoin(tableAP, tableRbAPHBP['id'].eq(tableAP['id']))
        queryTable = queryTable.innerJoin(tableRbHospitalBedProfile, tableRbHospitalBedProfile['id'].eq(tableRbAPHBP['value']))
        queryTable = queryTable.innerJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        cond = [tableAP['action_id'].isNotNull(),
                tableAP['deleted'].eq(0),
                tableAction['deleted'].eq(0),
                tableAPT['deleted'].eq(0),
                db.joinOr([tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%')),
                           tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('reanimation%'))]),
                tableAPT['typeName'].like('rbHospitalBedProfile')
                ]
        if profile:
            cond.append(tableRbHospitalBedProfile['id'].inlist(profile))
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDateTime)])
        cond.append(db.joinOr([joinOr1, joinOr2, joinOr3]))
        cond.append(u'''EXISTS(SELECT APHB.value
                            FROM ActionProperty AS AP
                            INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.`id`=AP.`id`
                            INNER JOIN Action AS A ON A.`id`=AP.`action_id`
                            INNER JOIN ActionPropertyType AS APT ON APT.`id`=AP.`type_id`
                            WHERE (AP.`action_id` IS NOT NULL AND AP.`action_id` = Action.id) AND (AP.`deleted`=0) AND (APT.`deleted`=0)
                            AND (APT.`typeName` LIKE 'HospitalBed') AND (APHB.`value` IN (%s)))'''%(u','.join(str(hospitalBedId) for hospitalBedId in hospitalBedIdList if hospitalBedId)))
        if textTable is None:
            return db.getDistinctIdList(queryTable, [tableRbHospitalBedProfile['id']], cond)
        else:
            countBeds = db.getCount(queryTable, countCol=tableRbHospitalBedProfile['id'], where=cond)
            textTable.setText(row if row else 4, column, countBeds)
            return None

    @classmethod
    def unrolledHospitalBed34(cls, db, table, bedsSchedule, unrolledColumn, totalInfo, orgStructureIdList, reanimationOSIdList,
                              hospitalBedIdList, dateTimeInterval, totalBedsColumn, bedsRepairsColumn,
                              profile = None, row = None, isReanimation = False):
        tableVHospitalBed = db.table('vHospitalBed')
        tableHBSchedule = db.table('rbHospitalBedShedule')

        begDateTime, endDateTime = dateTimeInterval
        osIdList = list(orgStructureIdList)
        if isReanimation:
            osIdList.extend(reanimationOSIdList)
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            queryTable = tableVHospitalBed
            condRepairs = [tableVHospitalBed['involution'].ne(0)]
            if bedsSchedule:
                queryTable = queryTable.innerJoin(tableHBSchedule, tableVHospitalBed['schedule_id'].eq(tableHBSchedule['id']))
            if bedsSchedule == 1:
                condRepairs.append(tableHBSchedule['code'].eq(1))
            elif bedsSchedule == 2:
                condRepairs.append(tableHBSchedule['code'].ne(1))
            joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].ge(begDateTime)])
            joinOr2 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].lt(endDateTime)])
            if osIdList:
                condRepairs.append(tableVHospitalBed['master_id'].inlist(osIdList))
            condRepairs.append(db.joinOr([db.joinAnd([tableVHospitalBed['endDateInvolute'].isNull(),
                                                      tableVHospitalBed['begDateInvolute'].isNull()]),
                                          db.joinAnd([tableVHospitalBed['begDateInvolute'].isNotNull(),
                                                      tableVHospitalBed['begDateInvolute'].ge(begDateTime),
                                                      tableVHospitalBed['begDateInvolute'].lt(endDateTime)]),
                                          db.joinAnd([tableVHospitalBed['endDateInvolute'].isNotNull(),
                                                      tableVHospitalBed['endDateInvolute'].gt(begDateTime),
                                                      tableVHospitalBed['endDateInvolute'].le(endDateTime)])
                                          ]))
            bedRepairIdList = db.getDistinctIdList(queryTable, [tableVHospitalBed['id']], condRepairs)
            if hospitalBedIdList:
                cls.getBedForProfile(db, (begDateTime, endDateTime), profile, hospitalBedIdList, table, row, totalBedsColumn) # Факт. развернуто коек
            else:
                table.setText(row, totalBedsColumn, 0) # Факт. развернуто коек
            if bedRepairIdList:
                cls.getBedForProfile(db, (begDateTime, endDateTime), profile, bedRepairIdList, table, row, bedsRepairsColumn) # в т.ч. коек, свернутых на ремонт
            else:
                table.setText(row, totalBedsColumn + 1, 0) # в т.ч. коек, свернутых на ремонт
        else:
            cond = []
            queryTable = tableVHospitalBed
            condRepairs = [tableVHospitalBed['involution'].ne(0)]
            if osIdList:
                cond.append(tableVHospitalBed['master_id'].inlist(osIdList))
                condRepairs.append(tableVHospitalBed['master_id'].inlist(osIdList))
            if profile:
                cond.append(tableVHospitalBed['profile_id'].inlist(profile))
            if bedsSchedule:
                queryTable = queryTable.innerJoin(tableHBSchedule, tableVHospitalBed['schedule_id'].eq(tableHBSchedule['id']))
            if bedsSchedule == 1:
                cond.append(tableHBSchedule['code'].eq(1))
                condRepairs.append(tableHBSchedule['code'].eq(1))
            elif bedsSchedule == 2:
                cond.append(tableHBSchedule['code'].ne(1))
                condRepairs.append(tableHBSchedule['code'].ne(1))
            joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].ge(begDateTime)])
            joinOr2 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].lt(endDateTime)])
            cond.append(db.joinAnd([joinOr1, joinOr2]))
            cond.append(tableVHospitalBed['isPermanent'].eq(1))
            if profile:
                condRepairs.append(tableVHospitalBed['profile_id'].inlist(profile))
            condRepairs.append(db.joinOr([db.joinAnd([tableVHospitalBed['endDateInvolute'].isNull(),
                                                              tableVHospitalBed['begDateInvolute'].isNull()]),
                                                  db.joinAnd([tableVHospitalBed['begDateInvolute'].isNotNull(),
                                                              tableVHospitalBed['begDateInvolute'].ge(begDateTime),
                                                              tableVHospitalBed['begDateInvolute'].lt(endDateTime)]),
                                                  db.joinAnd([tableVHospitalBed['endDateInvolute'].isNotNull(), tableVHospitalBed['endDateInvolute'].gt(begDateTime),
                                                              tableVHospitalBed['endDateInvolute'].le(endDateTime)])
                                                  ]))

            condRepairs.append(tableVHospitalBed['isPermanent'].eq(1))
            countBeds = db.getCount(queryTable, countCol='vHospitalBed.id', where=cond)
            countBedsRepairs = db.getDistinctCount(queryTable, countCol='vHospitalBed.id', where=condRepairs)
            table.setText(row, unrolledColumn, countBeds) # Факт. развернуто коек
            totalInfo['total'][unrolledColumn] += countBeds
            table.setText(row, unrolledColumn + 1, countBedsRepairs) # в т.ч. коек, свернутых на ремонт
            totalInfo['total'][unrolledColumn + 1] += countBedsRepairs

    def build(self, params):
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')

        tableOS = db.table('OrgStructure')
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableVHospitalBed = db.table('vHospitalBed')
        tableHBSchedule = db.table('rbHospitalBedShedule')

        begTime = params.get('begTime', QTime(7, 0))
        endDate = params.get('endDate', QDate())
        if not endDate:
            endDate = QDate.currentDate()
        if endDate:
            endDateTime = QDateTime(endDate, begTime.addSecs(-60))
            begDateTime = QDateTime(endDate.addDays(-1), begTime)
            bedsSchedule = getVal(params, 'bedsSchedule', 0)
            profileBedId = params.get('profileBed', None)
            # orgStructureId = params.get('orgStructureId', None)
            # выбранные (плановые) подразделения
            orgStructureIdList = getVal(params, 'orgStructures', [])  # getOrgStructureDescendants(orgStructureId) if orgStructureId else []
            # подразделения, соответствующие действиям "реанимация" (связанным с выбранными подразделениями) и найденные в процессе формирования отчета по плановым
            reanimationOSIdList = []
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertBlock()
            orgName, orgOKPO = self.getOrgInfo()
            self.insertCaption(cursor, params, orgName, orgOKPO, u'Листок учета движения больных и коечного фонда стационара (2013)')
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('10%',[u'', u'', u'', u'', u'1', u'Всего:\n\nв том числе по койкам:', u''], CReportBase.AlignRight),
                    ('3.9%', [u'Код', u'', u'', u'', u'2'], CReportBase.AlignRight),
                    ('3.9%', [u'Фактически развернуто коек, включая койки, свернутые на ремонт', u'', u'', u'', u'3'], CReportBase.AlignRight),
                    ('3.9%', [u'В том числе коек, свернутых на ремонт', u'', u'', u'', u'4'], CReportBase.AlignRight),
                    ('3.9%', [u'Движение больных за истекшие сутки', u'Состояло больных на начало истекших суток', u'',u'', u'5'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'Поступило больных(без переведенных внутри больницы)', u'Всего', u'', '6'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'в т.ч. из дневного стационара', u'', '7'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'Из них', u'Сельских жителей', u'8'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'', u'0 - 17 лет', u'9'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'', u'старше трудоспособного возраста', u'10'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'Переведено больных внутри больницы', u'Из других отделений', u'', u'11'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'В другие отделения', u'', u'12'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'Выписано больных', u'Всего', u'', u'13'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'В т.ч.', u'старше трудоспособного возраста', u'14'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'', u'переведенных в другие стационары', u'15'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'', u'в круглосуточный стационар', u'16'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'', u'в дневной стационар', u'17'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'Умерло', u'', u'', u'18'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'в т.ч.', u'старше трудоспособного возраста', u'', u'19'], CReportBase.AlignRight),
                    ('3.9%', [u'На начало текущего дня', u'Состоит больных - всего', u'', u'', u'20'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'в т.ч.', u'старше трудоспособного возраста', u'', u'21'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'Состоит матерей при больных детях', u'', u'', u'22'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'Свободных мест', u'Мужских', u'', u'23'], CReportBase.AlignRight),
                    ('3.9%', [u'', u'', u'Женских', u'', u'24'], CReportBase.AlignRight)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 4, 1) # 1
            table.mergeCells(0, 1, 4, 1) # код
            table.mergeCells(0, 2, 4, 1) # развернуто коек
            table.mergeCells(0, 3, 4, 1) # свернутых
            table.mergeCells(0, 4, 1, 15) # Движение больных за истекшие сутки
            table.mergeCells(1, 4, 3, 1) # Состояло больных на начало истекших суток
            table.mergeCells(1, 5, 1, 5) # Поступило больных
            table.mergeCells(2, 5, 2, 1) # - Всего
            table.mergeCells(2, 6, 2, 1) # - из дневного стационара
            table.mergeCells(2, 7, 1, 3) # - из них
            table.mergeCells(1, 10, 1, 2) # Переведено больных внутри больницы
            table.mergeCells(2, 10, 2, 1) # -Из других отделений
            table.mergeCells(2, 11, 2, 1) # Переведено больных внутри больницы-В другие отделения
            table.mergeCells(1, 12, 1, 5) # Выписано больных
            table.mergeCells(2, 12, 2, 1) # -Всего
            table.mergeCells(2, 13, 1, 4) # Выписано больных-В т.ч.
            table.mergeCells(1, 17, 3, 1) # Умерло
            table.mergeCells(2, 18, 2, 1) # Умерло - в т.ч.
            table.mergeCells(0, 19, 1, 5) # На начало текущего дня
            table.mergeCells(1, 19, 3, 1) # -Состоит больных всего
            table.mergeCells(2, 20, 2, 1) # На начало текущего дня-Состоит больных-В т.ч. старше трудоспособного возраста
            table.mergeCells(1, 21, 3, 1) # Состоит матерей при больных детях
            table.mergeCells(1, 22, 1, 2) # Свободных мест
            table.mergeCells(2, 22, 2, 1) # -Мужских
            table.mergeCells(2, 23, 2, 1) # -Женских

            totalInfo = {'total'    : [0] * len(cols),
                         'patronage': [0] * len(cols)}


            def getMovingPresent(profile = None, atBegin = True, isReanimation = False):
                cond = [ tableAction['deleted'].eq(0),
                         tableEvent['deleted'].eq(0),
                         tableAP['deleted'].eq(0),
                         tableActionType['deleted'].eq(0),
                         tableClient['deleted'].eq(0),
                         tableOS['deleted'].eq(0),
                         tableAPT['deleted'].eq(0),
                         tableAP['action_id'].eq(tableAction['id'])
                       ]
                elderCond = u'age(Client.birthDate, Action.begDate) >= 60'
                queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
                queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
                queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
                cond.append(tableOS['deleted'].eq(0))
                cond.append(tableAPT['typeName'].like('HospitalBed'))

                actionTypeIdList = getActionTypeIdListByFlatCode('reanimation%')
                # Если это не обработка реанимационных действий
                if not isReanimation:
                    # то добавить и обычные движения в обработку
                    actionTypeIdList.extend(getActionTypeIdListByFlatCode('moving%'))
                cond.append(tableAction['actionType_id'].inlist(actionTypeIdList))

                # формирование полного списка подразделений
                osIdList = list(orgStructureIdList)
                if isReanimation:
                    osIdList.extend(reanimationOSIdList)

                if osIdList:
                    cond.append(tableOSHB['master_id'].inlist(osIdList))

                #Работать только с переводами в реанимацию только из плановых отделений
                if isReanimation and orgStructureIdList:
                    cond.append(getTransferPropertyIn(u'Переведен из отделения%', orgStructureIdList))

                if profile:
                    if QtGui.qApp.defaultHospitalBedProfileByMoving():
                        cond.append(getPropertyAPHBP(profile))
                    else:
                        cond.append(tableOSHB['profile_id'].inlist(profile))
                if bedsSchedule:
                    queryTable = queryTable.innerJoin(tableHBSchedule, tableOSHB['schedule_id'].eq(tableHBSchedule['id']))
                if bedsSchedule == 1:
                    cond.append(tableHBSchedule['code'].eq(1))
                elif bedsSchedule == 2:
                    cond.append(tableHBSchedule['code'].ne(1))
                compareDate = begDateTime if atBegin else endDateTime
                cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].lt(compareDate)]))
                cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(compareDate)]))

                reanimationCond = [# Реанимация должна быть незавершенной на дату проверки (т.е. не иметь дату окончания или дата окончания должна быть после этой даты)
                                   u'reanimationAction.endDate IS NULL OR reanimationAction.endDate >= \'%s\'' % compareDate.toString(Qt.ISODate),
                                   # Реанимация должна начинаться в период действия текущего Движения
                                   u'reanimationAction.begDate >= Action.begDate',
                                   # Реанимация должна начинаться в период действия текущего Движения
                                   u'reanimationAction.begDate <= Action.endDate OR Action.endDate IS NULL',
                                   u'reanimationAction.event_id = Action.event_id',
                                   u'SourceAP.action_id = Action.id']
                reanimationExistsStmt = 'EXISTS(%s)' % getReanimationInfoTableStmt(u'Переведен из отделения%', reanimationCond) if not isReanimation else '0'
                cols = ['COUNT(IF(%s AND ActionType.flatCode LIKE \'moving%%\', NULL, 1)) AS countAll' % reanimationExistsStmt,
                        'SUM(%s AND NOT (ActionType.flatCode LIKE \'moving%%\' AND %s)) AS countPatronage' % (getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')'),
                                                                                                      reanimationExistsStmt),
                        'SUM(%s) as countElder' % elderCond
                        ]
                stmt = db.selectStmt(queryTable,
                                     cols,
                                     where=cond)
                query = db.query(stmt)
                if query.first():
                    record = query.record()
                    return [forceInt(record.value('countAll')), forceInt(record.value('countPatronage')), forceInt(record.value('countElder'))]
                else:
                    return [0, 0, 0]

            # Сост. больных на нач. истек. суток
            def presentBegDay(profile = None, row = None, isReanimation = False):
                presentAll, presentPatronage, presentElder = getMovingPresent(profile, True, isReanimation)
                table.setText(row, 4, presentAll)
                totalInfo['total'][4] += presentAll

            # Переведено больных внутри больницы/из др. отд.
            # orgStructureIdList - это список отделений перевод в(из) которые(-ых) надо учитывать, если пуст, то учитываются все переводы для указанной койки (i764)
            def fromMovingTransfer(profile = None, row = None, isReanimation = False):
                transferAll, transferPatronag, reanimationProfileIdList = getMovingTransfer(bedsSchedule,
                                                                                            begDateTime,
                                                                                            endDateTime,
                                                                                            u'Переведен из отделения',
                                                                                            profile,
                                                                                            False,
                                                                                            orgStructureIdList,
                                                                                            reanimationOSIdList = reanimationOSIdList,
                                                                                            isReanimation = isReanimation)
                table.setText(row, 10, transferAll)
                totalInfo['total'][10] += transferAll
                return reanimationProfileIdList

            # Поступило всего больных
            def receivedAll(profile = None, row = None, isReanimation = False):
                all, children, adultCount, clientRural, isStationaryDay, countPatronage = getReceived(bedsSchedule,
                                            begDateTime,
                                            endDateTime,
                                            u'Переведен из отделения',
                                            profile,
                                            orgStructureIdList) if not isReanimation else [0] * 6
                table.setText(row, 5, all) # всего
                table.setText(row, 6, isStationaryDay) # в т.ч. из дн. стационара
                table.setText(row, 7, clientRural) # сельских жителей
                table.setText(row, 8, children) # 0-17 лет
                table.setText(row, 9, adultCount) # старше трудоспособного возраста
                totalInfo['total'][5] += all
                totalInfo['total'][6] += isStationaryDay
                totalInfo['total'][7] += clientRural
                totalInfo['total'][8] += children
                totalInfo['total'][9] += adultCount

            # Переведено больных внутри больницы/в др. отд.
            def inMovingTransfer(profile = None, row = None, isReanimation = False):
                transferAll, transferPatronag, reanimationProfileIdList = getMovingTransfer(bedsSchedule,
                                                                                            begDateTime,
                                                                                            endDateTime,
                                                                                            u'Переведен в отделение',
                                                                                            profile,
                                                                                            True,
                                                                                            orgStructureIdList,
                                                                                            reanimationOSIdList = reanimationOSIdList,
                                                                                            isReanimation = isReanimation)
                table.setText(row, 11, transferAll)
                totalInfo['total'][11] += transferAll
                return reanimationProfileIdList

            # Выписано всего больных;
            # в т.ч. переведено в др. стационары;
            # умерло
            def leavedAll(profile = None, row = None, isReanimation = False):
                countLeavedAll, leavedDeath, leavedTransfer, leavedAllPatronag, leavedDeathPatronag, leavedTransferPatronag, leavedElder, deadElder, leavedDayStat, leavedNoctidialStat = getLeaved(bedsSchedule,
                                                                                                                                        begDateTime,
                                                                                                                                        endDateTime,
                                                                                                                                        profile,
                                                                                                                                        orgStructureIdList) if not isReanimation else [0] * 10
                # Не лучший вариант, но пока требуется только считать умерших отдельно - получаем общее количество здесь, а не в запросе.
                table.setText(row, 12, countLeavedAll - leavedDeath)
                totalInfo['total'][12] += countLeavedAll - leavedDeath

                table.setText(row, 13, leavedElder)
                totalInfo['total'][13] += leavedElder

                table.setText(row, 14, leavedTransfer)
                totalInfo['total'][14] += leavedTransfer

                table.setText(row, 15, leavedDayStat)
                totalInfo['total'][15] += leavedDayStat

                table.setText(row, 16, leavedNoctidialStat)
                totalInfo['total'][16] += leavedNoctidialStat

                table.setText(row, 17, leavedDeath)
                totalInfo['total'][17] += leavedDeath

                table.setText(row, 18, deadElder)
                totalInfo['total'][18] += deadElder

            # На начало текущего дня/Состоит больных всего
            # На начало текущего дня/Состоит матерей при больных детях
            def presentEndDay(profile = None, row = None, isReanimation = False):
                presentAll, presentPatronag, presentElder = getMovingPresent(profile, False, isReanimation)
                table.setText(row, 19, presentAll)
                totalInfo['total'][19] += presentAll

                table.setText(row, 20, presentElder)
                totalInfo['total'][20] += presentElder

                table.setText(row, 21, presentPatronag)
                totalInfo['total'][21] += presentPatronag

            #Всего коек пустых
            def freeHospitalBedAll(profile = None, row = None):
                tableVHospitalBedSchedule = tableVHospitalBed
                cond = [tableVHospitalBed['involution'].eq(0),
                        tableVHospitalBed['isBusy'].eq(0)
                        ]
                if orgStructureIdList:
                    cond.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
                if profile:
                    if QtGui.qApp.defaultHospitalBedProfileByMoving():
                        profileIdListNoBusi = self.getBedForProfile(db, (begDateTime, endDateTime), profile, hospitalBedIdList)
                        cond.append(tableVHospitalBed['profile_id'].inlist(profileIdListNoBusi))
                    else:
                        cond.append(tableVHospitalBed['profile_id'].inlist(profile))
                if bedsSchedule:
                    tableVHospitalBedSchedule = tableVHospitalBedSchedule.innerJoin(tableHBSchedule, tableVHospitalBed['schedule_id'].eq(tableHBSchedule['id']))
                if bedsSchedule == 1:
                    cond.append(tableVHospitalBed['code'].eq(1))
                elif bedsSchedule == 2:
                    cond.append(tableVHospitalBed['code'].ne(1))
                stmt = db.selectStmt(tableVHospitalBedSchedule, u'SUM(IF(vHospitalBed.sex = 1, 1, 0)) AS bedsMen, SUM(IF(vHospitalBed.sex = 2, 1, 0)) AS bedsWomen', where=cond)
                query = db.query(stmt)
                if query.first():
                    record = query.record()
                    bedsMen = forceInt(record.value('bedsMen'))
                    bedsWomen = forceInt(record.value('bedsWomen'))
                else:
                    bedsMen = 0
                    bedsWomen = 0
                if row:
                    table.setText(row, 22, bedsMen)
                    totalInfo['total'][22] = bedsMen

                    table.setText(row, 23, bedsWomen)
                    totalInfo['total'][23] = bedsWomen

            tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')
            cond = []
            profileIdList = []
            hospitalBedIdList = []
            if orgStructureIdList:
                cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
            if QtGui.qApp.defaultHospitalBedProfileByMoving():
                hospitalBedIdList = self.getHospitalBedIdList(db,
                                                              tableVHospitalBed,
                                                              tableHBSchedule,
                                                              bedsSchedule,
                                                              (begDateTime, endDateTime),
                                                              orgStructureIdList)
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
                        tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%') + getActionTypeIdListByFlatCode('reanimation%')),
                        tableAPT['typeName'].like('rbHospitalBedProfile')
                        ]
                joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
                joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)])
                joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDateTime)])
                cond.append(db.joinOr([joinOr1, joinOr2, joinOr3]))
                cond.append(u'''EXISTS(SELECT APHB.value
FROM ActionProperty AS AP
INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.`id`=AP.`id`
INNER JOIN Action AS A ON A.`id`=AP.`action_id`
INNER JOIN ActionPropertyType AS APT ON APT.`id`=AP.`type_id`
WHERE (AP.`action_id` IS NOT NULL AND AP.`action_id` = Action.id) AND (AP.`deleted`=0) AND (APT.`deleted`=0)
AND (APT.`typeName` LIKE 'HospitalBed') AND (APHB.`value` IN (%s)))'''%(u','.join(str(hospitalBedId) for hospitalBedId in hospitalBedIdList if hospitalBedId)))
                records = db.getRecordList(queryTable, [tableRbHospitalBedProfile['id'], tableRbHospitalBedProfile['code'], tableRbHospitalBedProfile['name']], cond)
                for record in records:
                    profileId = forceRef(record.value('id'))
                    if profileId not in profileIdList:
                        profileIdList.append(profileId)
            else:
                queryTable = tableOSHB.innerJoin(tableRbHospitalBedProfile, tableOSHB['profile_id'].eq(tableRbHospitalBedProfile['id']))
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

            rowProfile = 6
            processedProfileIdList = []
            reanimationProfileIdList = []
            isReanimation = False
            while profileIdList:
                rowProfile = table.addRow()
                profileId = profileIdList.pop(0)

                if profileId in processedProfileIdList:
                    continue
                else:
                    processedProfileIdList.append(profileId)

                profileRecord = db.getRecordEx(tableRbHospitalBedProfile, ['id', 'code', 'name'], [tableRbHospitalBedProfile['id'].eq(profileId)])
                #profileName = forceString(db.translate(tableRbHospitalBedProfile, 'id', profileId, 'name'))
                profileName = forceString(profileRecord.value('name'))
                profileCode = forceString(profileRecord.value('code'))
                table.setText(rowProfile, 0, profileName)
                table.setText(rowProfile, 0, profileCode)
                self.unrolledHospitalBed34(db, table, bedsSchedule, 2, totalInfo, orgStructureIdList, reanimationOSIdList,
                                           hospitalBedIdList, (begDateTime, endDateTime), 1, 2,
                                           profile=[profileId],
                                           row=rowProfile)
                presentBegDay([profileId], rowProfile, isReanimation)
                receivedAll([profileId], rowProfile, isReanimation)
                reanimationProfileIdList.extend(fromMovingTransfer([profileId],
                                                                   rowProfile,
                                                                   isReanimation))
                reanimationProfileIdList.extend(inMovingTransfer([profileId],
                                                                 rowProfile,
                                                                 isReanimation))
                leavedAll([profileId], rowProfile, isReanimation)
                presentEndDay([profileId], rowProfile,isReanimation)
                freeHospitalBedAll([profileId], rowProfile)

                if not profileIdList and reanimationProfileIdList:
                    profileIdList = reanimationProfileIdList
                    isReanimation = True

            for column in xrange(1, len(cols)):
                table.setText(5, column, totalInfo['total'][column])

        return doc

#TODO: atronah: необходимо попробовать объединить с CStationaryF007Moving
class CStationaryF007Moving2013(CStationaryF007Moving):
    def __init__(self, parent):
        CStationaryF007.__init__(self, parent)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара (2013)')


    @staticmethod
    def insertCaption(cursor, params, orgName, timeString):
        orgId = QtGui.qApp.currentOrgId()
        orgName = u''
        if orgId:
            record = QtGui.qApp.db.getRecordEx('Organisation', 'shortName', 'id=%s AND deleted = 0'%(str(orgId)))
            if record:
                orgName = forceString(record.value('shortName'))

        orgStructureIdList = params.get('orgStructures', None)
        orgStructureIdCount = params.get('orgStructureCount', None)

        underCaptionList = []
        if len(orgStructureIdList) != orgStructureIdCount:
            orgStructureName = getOrgStructureFullNameList(orgStructureIdList) + u'.'
        else:
            orgStructureName = u'ЛПУ'
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)
        columns = [('50%', [], CReportBase.AlignLeft), ('50%', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=2, border=0, cellPadding=2, cellSpacing=0)
        table.mergeCells(1, 0, 1, 2)
        table.setText(0, 0, orgName)
        table.setText(0, 1, orgStructureName)
        date = params.get('endDate', QDate()).addDays(-1)
        table.setText(1, 0, u'Сводная ежедневная ведомость учета движения больных и коечного фонда стационара на %s за %s' % (timeString, date.toString(u'dd.MM.yy')), blockFormat = CReportBase.AlignCenter)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
    
    def build(self, params):
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')

        tableOS = db.table('OrgStructure')
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableVHospitalBed = db.table('vHospitalBed')
        tableHBSchedule = db.table('rbHospitalBedShedule')

        begTime = params.get('begTime', QTime(7, 0))
        endDate = params.get('endDate', QDate())
        if not endDate:
            endDate = QDate.currentDate()
        if endDate:
            endDateTime = QDateTime(endDate, begTime.addSecs(-60))
            begDateTime = QDateTime(endDate.addDays(-1), begTime)
            bedsSchedule = getVal(params, 'bedsSchedule', 0)
            profileBedId = params.get('profileBed', None)
            # orgStructureId = params.get('orgStructureId', None)
            # выбранные (плановые) подразделения
            orgStructureIdList = getVal(params, 'orgStructures', [])  # getOrgStructureDescendants(orgStructureId) if orgStructureId else []
            # подразделения, соответствующие действиям "реанимация" (связанным с выбранными подразделениями) и найденные в процессе формирования отчета по плановым
            reanimationOSIdList = []
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertBlock()
            orgName, _ = self.getOrgInfo()
            self.insertCaption(cursor, params, orgName, u'7 часов утра')
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('10%',  [u'Наименование отделения, профиля коек', u'', u'', u'1', u'Всего:', u'Ухаживающие'], CReportBase.AlignRight),
                    ('8%', [u'Факт. развернуто коек', u'', u'', u'2'], CReportBase.AlignRight),
                    ('8%', [u'в т.ч. коек, свернутых на ремонт', u'', u'', u'3'], CReportBase.AlignRight),
                    ('8%', [u'Сост. больных на нач. истек. суток', u'', u'', u'4'], CReportBase.AlignRight),
                    ('8%', [u'Поступило всего больных', u'', u'', '5'], CReportBase.AlignRight),
                    ('8%', [u'Движение больных за истекшие сутки', u'Переведено больных внутри больницы', u'из др.отд.', u'6'], CReportBase.AlignRight),
                    ('8%', [u'', u'', u'в др. отд.', u'7'], CReportBase.AlignRight),
                    ('8%', [u'', u'Выписано всего больных', u'', u'8'], CReportBase.AlignRight),
                    ('8%', [u'', u'в т.ч. переведено в др. стационары', u'', u'9'], CReportBase.AlignRight),
                    ('8%', [u'', u'Умерло', u'', u'10'], CReportBase.AlignRight),
                    ('8%', [u'На начало текущего дня', u'Состоит больных всего', u'', u'11'], CReportBase.AlignRight),
                    ('8%', [u'', u'Состоит матерей при больных детях', u'', u'12'], CReportBase.AlignRight),
                    ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 3, 1) # Наименование отделения, профиля коек
            table.mergeCells(0, 1, 3, 1) # Факт. развернуто коек
            table.mergeCells(0, 2, 3, 1) # в т.ч. коек, свернутых на ремонт
            table.mergeCells(0, 3, 3, 1) # Сост. больных на нач. истек. суток
            table.mergeCells(0, 4, 3, 1) # Поступило всего больных

            table.mergeCells(0, 5, 1, 5) # Движение больных за истекшие сутки
            table.mergeCells(1, 5, 1, 2) # Переведено больных внутри больницы
            table.mergeCells(1, 7, 2, 1) # Выписано всего больных
            table.mergeCells(1, 8, 2, 1) # в т.ч. переведено в др. стационары
            table.mergeCells(1, 9, 2, 1) # Умерло

            table.mergeCells(0, 10, 1, 2) # На начало текущего дня
            table.mergeCells(1, 10, 2, 1) # Состоит больных всего
            table.mergeCells(1, 11, 2, 1) # Состоит матерей при больных детях

            totalInfo = {'total'    : [0] * len(cols),
                         'patronage': [0] * len(cols)}


            def getMovingPresent(profile = None, atBegin = True, isReanimation = False):
                cond = [ tableAction['deleted'].eq(0),
                         tableEvent['deleted'].eq(0),
                         tableAP['deleted'].eq(0),
                         tableActionType['deleted'].eq(0),
                         tableClient['deleted'].eq(0),
                         tableOS['deleted'].eq(0),
                         tableAPT['deleted'].eq(0),
                         tableAP['action_id'].eq(tableAction['id'])
                         ]
                queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
                queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
                queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
                cond.append(tableOS['deleted'].eq(0))
                cond.append(tableAPT['typeName'].like('HospitalBed'))

                actionTypeIdList = getActionTypeIdListByFlatCode('reanimation%')
                # Если это не обработка реанимационных действий
                if not isReanimation:
                    # то добавить и обычные движения в обработку
                    actionTypeIdList.extend(getActionTypeIdListByFlatCode('moving%'))
                cond.append(tableAction['actionType_id'].inlist(actionTypeIdList))

                # формирование полного списка подразделений
                osIdList = list(orgStructureIdList)
                if isReanimation:
                    osIdList.extend(reanimationOSIdList)

                if osIdList:
                    cond.append(tableOSHB['master_id'].inlist(osIdList))

                #Работать только с переводами в реанимацию только из плановых отделений    
                if isReanimation and orgStructureIdList:
                    cond.append(getTransferPropertyIn(u'Переведен из отделения%', orgStructureIdList))

                if profile:
                    if QtGui.qApp.defaultHospitalBedProfileByMoving():
                        cond.append(getPropertyAPHBP(profile))
                    else:
                        cond.append(tableOSHB['profile_id'].inlist(profile))
                if bedsSchedule:
                    queryTable = queryTable.innerJoin(tableHBSchedule, tableOSHB['schedule_id'].eq(tableHBSchedule['id']))
                if bedsSchedule == 1:
                    cond.append(tableHBSchedule['code'].eq(1))
                elif bedsSchedule == 2:
                    cond.append(tableHBSchedule['code'].ne(1))
                compareDate = begDateTime if atBegin else endDateTime
                cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].lt(compareDate)]))
                cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(compareDate)]))

                reanimationCond = [# Реанимация должна быть незавершенной на дату проверки (т.е. не иметь дату окончания или дата окончания должна быть после этой даты)
                    u'reanimationAction.endDate IS NULL OR reanimationAction.endDate >= \'%s\'' % compareDate.toString(Qt.ISODate),
                    # Реанимация должна начинаться в период действия текущего Движения
                    u'reanimationAction.begDate >= Action.begDate',
                    # Реанимация должна начинаться в период действия текущего Движения
                    u'reanimationAction.begDate <= Action.endDate OR Action.endDate IS NULL',
                    u'reanimationAction.event_id = Action.event_id',
                    u'SourceAP.action_id = Action.id']
                reanimationExistsStmt = 'EXISTS(%s)' % getReanimationInfoTableStmt(u'Переведен из отделения%', reanimationCond) if not isReanimation else '0'
                cols = ['COUNT(IF(%s AND ActionType.flatCode LIKE \'moving%%\', NULL, 1)) AS countAll' % reanimationExistsStmt,
                        'SUM(%s AND NOT (ActionType.flatCode LIKE \'moving%%\' AND %s)) AS countPatronage' % (getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')'),
                                                                                                              reanimationExistsStmt)
                        ]
                stmt = db.selectStmt(queryTable,
                                     cols,
                                     where=cond)
                query = db.query(stmt)
                if query.first():
                    record = query.record()
                    return [forceInt(record.value('countAll')), forceInt(record.value('countPatronage'))]
                else:
                    return [0, 0]

            # Сост. больных на нач. истек. суток
            def presentBegDay(profile = None, row = None, isReanimation = False):
                presentAll, presentPatronage = getMovingPresent(profile, True, isReanimation)
                table.setText(row, 3, presentAll)
                totalInfo['total'][3] += presentAll
                totalInfo['patronage'][3] += presentPatronage

            # Переведено больных внутри больницы/из др. отд.
            # orgStructureIdList - это список отделений перевод в(из) которые(-ых) надо учитывать, если пуст, то учитываются все переводы для указанной койки (i764)
            def fromMovingTransfer(profile = None, row = None, isReanimation = False):
                transferAll, transferPatronag, reanimationProfileIdList = getMovingTransfer(bedsSchedule,
                                                                                            begDateTime,
                                                                                            endDateTime,
                                                                                            u'Переведен из отделения',
                                                                                            profile,
                                                                                            False,
                                                                                            orgStructureIdList,
                                                                                            reanimationOSIdList = reanimationOSIdList,
                                                                                            isReanimation = isReanimation)
                table.setText(row, 5, transferAll)
                totalInfo['total'][5] += transferAll
                totalInfo['patronage'][5] += transferPatronag
                return reanimationProfileIdList

            # Поступило всего больных
            def receivedAll(profile = None, row = None, isReanimation = False):
                receiveValues = getReceived(bedsSchedule,
                                            begDateTime,
                                            endDateTime,
                                            u'Переведен из отделения',
                                            profile,
                                            orgStructureIdList) if not isReanimation else [0] * 6
                table.setText(row, 4, receiveValues[0])
                totalInfo['total'][4] += receiveValues[0]
                totalInfo['patronage'][4] += receiveValues[5]

            # Переведено больных внутри больницы/в др. отд.
            def inMovingTransfer(profile = None, row = None, isReanimation = False):
                transferAll, transferPatronag, reanimationProfileIdList = getMovingTransfer(bedsSchedule,
                                                                                            begDateTime,
                                                                                            endDateTime,
                                                                                            u'Переведен в отделение',
                                                                                            profile,
                                                                                            True,
                                                                                            orgStructureIdList,
                                                                                            reanimationOSIdList = reanimationOSIdList,
                                                                                            isReanimation = isReanimation)
                table.setText(row, 6, transferAll)
                totalInfo['total'][6] += transferAll
                totalInfo['patronage'][6] += transferPatronag
                return reanimationProfileIdList

            # Выписано всего больных; 
            # в т.ч. переведено в др. стационары; 
            # умерло
            def leavedAll(profile = None, row = None, isReanimation = False):
                countLeavedAll, leavedDeath, leavedTransfer, leavedAllPatronag, leavedDeathPatronag, leavedTransferPatronag, leavedElder, deadElder, leavedDayStat, leavedNoctidialStat = getLeaved(bedsSchedule,
                                                                                                                                                                                                    begDateTime,
                                                                                                                                                                                                    endDateTime,
                                                                                                                                                                                                    profile,
                                                                                                                                                                                                    orgStructureIdList) if not isReanimation else [0] * 6
                table.setText(row, 7, countLeavedAll)
                totalInfo['total'][7] += countLeavedAll
                totalInfo['patronage'][7] += leavedAllPatronag

                table.setText(row, 8, leavedTransfer)
                totalInfo['total'][8] += leavedTransfer
                totalInfo['patronage'][8] += leavedTransferPatronag

                table.setText(row, 9, leavedDeath)
                totalInfo['total'][9] += leavedDeath
                totalInfo['patronage'][9] += leavedDeathPatronag

            # На начало текущего дня/Состоит больных всего
            # На начало текущего дня/Состоит матерей при больных детях
            def presentEndDay(profile = None, row = None, isReanimation = False):
                presentAll, presentPatronag = getMovingPresent(profile, False, isReanimation)
                table.setText(row, 10, presentAll)
                totalInfo['total'][10] += presentAll
                totalInfo['patronage'][10] += presentPatronag

                table.setText(row, 11, presentPatronag)
                totalInfo['total'][11] += presentPatronag
                totalInfo['patronage'][11] += presentPatronag


            tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')
            cond = []
            profileIdList = []
            hospitalBedIdList = []
            if orgStructureIdList:
                cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
            if QtGui.qApp.defaultHospitalBedProfileByMoving():
                hospitalBedIdList = self.getHospitalBedIdList(db,
                                                              tableVHospitalBed,
                                                              tableHBSchedule,
                                                              bedsSchedule,
                                                              (begDateTime, endDateTime),
                                                              orgStructureIdList)
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
                        tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%') + getActionTypeIdListByFlatCode('reanimation%')),
                        tableAPT['typeName'].like('rbHospitalBedProfile')
                        ]
                joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
                joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)])
                joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDateTime)])
                cond.append(db.joinOr([joinOr1, joinOr2, joinOr3]))
                cond.append(u'''EXISTS(SELECT APHB.value
FROM ActionProperty AS AP
INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.`id`=AP.`id`
INNER JOIN Action AS A ON A.`id`=AP.`action_id`
INNER JOIN ActionPropertyType AS APT ON APT.`id`=AP.`type_id`
WHERE (AP.`action_id` IS NOT NULL AND AP.`action_id` = Action.id) AND (AP.`deleted`=0) AND (APT.`deleted`=0)
AND (APT.`typeName` LIKE 'HospitalBed') AND (APHB.`value` IN (%s)))'''%(u','.join(str(hospitalBedId) for hospitalBedId in hospitalBedIdList if hospitalBedId)))
                records = db.getRecordList(queryTable, [tableRbHospitalBedProfile['id'], tableRbHospitalBedProfile['code'], tableRbHospitalBedProfile['name']], cond)
                for record in records:
                    profileId = forceRef(record.value('id'))
                    if profileId not in profileIdList:
                        profileIdList.append(profileId)
            else:
                queryTable = tableOSHB.innerJoin(tableRbHospitalBedProfile, tableOSHB['profile_id'].eq(tableRbHospitalBedProfile['id']))
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


            rowProfile = 6
            processedProfileIdList = []
            reanimationProfileIdList = []
            isReanimation = False
            while profileIdList:
                rowProfile = table.addRow()
                profileId = profileIdList.pop(0)

                if profileId in processedProfileIdList:
                    continue
                else:
                    processedProfileIdList.append(profileId)

                profileName = forceString(db.translate(tableRbHospitalBedProfile, 'id', profileId, 'name'))
                table.setText(rowProfile, 0, profileName)
                self.unrolledHospitalBed34(db, table, bedsSchedule, 1, totalInfo, orgStructureIdList, reanimationOSIdList,
                                           hospitalBedIdList, (begDateTime, endDateTime), 1, 2,
                                           profile=[profileId],
                                           row=rowProfile)
                presentBegDay([profileId], rowProfile, isReanimation)
                receivedAll([profileId], rowProfile, isReanimation)
                reanimationProfileIdList.extend(fromMovingTransfer([profileId],
                                                                   rowProfile,
                                                                   isReanimation))
                reanimationProfileIdList.extend(inMovingTransfer([profileId],
                                                                 rowProfile,
                                                                 isReanimation))
                leavedAll([profileId], rowProfile, isReanimation)
                presentEndDay([profileId], rowProfile,isReanimation)

                if not profileIdList and reanimationProfileIdList:
                    profileIdList = reanimationProfileIdList
                    isReanimation = True

            for column in xrange(1, len(cols)):
                table.setText(4, column, totalInfo['total'][column])
                table.setText(5, column, totalInfo['patronage'][column])

        return doc


# TODO: классы CStationaryF007Moving* состоят из уныния и отчаяния, сделайте с ними что-нибудь, пожалуйста.
class CStationaryF007Moving2015(CStationaryF007Moving2013):
    def __init__(self, parent):
        super(CStationaryF007Moving2015, self).__init__(parent)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара (2015)')

    def getSetupDialog(self, parent):
        result = CStationaryF007SetupDialog(parent)
        result.chkDetailOrgStructure.setVisible(True)
        result.chkIsHideBeds.setVisible(True)
        self.stationaryF007SetupDialog = result
        return result

    def build(self, params):
        def unrolledHospitalBed34(hospitalBedIdList, profile = None, row = None, isReanimation = False):
            osIdList = list(orgStructureIdList)
            if isReanimation:
                osIdList.extend(reanimationOSIdList)
            if QtGui.qApp.defaultHospitalBedProfileByMoving():
                tableVHospitalBedSchedule = tableVHospitalBed
                condRepairs = [tableVHospitalBed['involution'].ne(0)]
                if bedsSchedule:
                    tableVHospitalBedSchedule = tableVHospitalBedSchedule.innerJoin(tableHBSchedule, tableVHospitalBed['schedule_id'].eq(tableHBSchedule['id']))
                if bedsSchedule == 1:
                    condRepairs.append(tableHBSchedule['code'].eq(1))
                elif bedsSchedule == 2:
                    condRepairs.append(tableHBSchedule['code'].ne(1))
                joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].ge(begDateTime)])
                joinOr2 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].lt(endDateTime)])
                if osIdList:
                    condRepairs.append(tableVHospitalBed['master_id'].inlist(osIdList))
                condRepairs.append(db.joinOr([db.joinAnd([tableVHospitalBed['endDateInvolute'].isNull(),
                                                          tableVHospitalBed['begDateInvolute'].isNull()]),
                                              db.joinAnd([tableVHospitalBed['begDateInvolute'].isNotNull(),
                                                          tableVHospitalBed['begDateInvolute'].ge(begDateTime),
                                                          tableVHospitalBed['begDateInvolute'].lt(endDateTime)]),
                                              db.joinAnd([tableVHospitalBed['endDateInvolute'].isNotNull(),
                                                          tableVHospitalBed['endDateInvolute'].gt(begDateTime),
                                                          tableVHospitalBed['endDateInvolute'].le(endDateTime)])
                                              ]))
                bedRepairIdList = db.getDistinctIdList(tableVHospitalBedSchedule, [tableVHospitalBed['id']], condRepairs)
                if hospitalBedIdList:
                    self.getBedForProfile(db, (begDateTime, endDateTime), profile, hospitalBedIdList, table, row, table.TotalBeds) # Факт. развернуто коек
                else:
                    info[table.TotalBeds] = 0
                if bedRepairIdList:
                    self.getBedForProfile(db, (begDateTime, endDateTime), profile, bedRepairIdList, table, row, table.RepairBeds) # в т.ч. коек, свернутых на ремонт
                else:
                    info[table.RepairBeds] = 0
            else:
                cond = []
                tableVHospitalBedSchedule = tableVHospitalBed
                condRepairs = [tableVHospitalBed['involution'].ne(0)]
                if osIdList:
                    cond.append(tableVHospitalBed['master_id'].inlist(osIdList))
                    condRepairs.append(tableVHospitalBed['master_id'].inlist(osIdList))
                if profile:
                    cond.append(tableVHospitalBed['profile_id'].inlist(profile))
                if bedsSchedule:
                    tableVHospitalBedSchedule = tableVHospitalBedSchedule.innerJoin(tableHBSchedule, tableVHospitalBed['schedule_id'].eq(tableHBSchedule['id']))
                if bedsSchedule == 1:
                    cond.append(tableHBSchedule['code'].eq(1))
                    condRepairs.append(tableHBSchedule['code'].eq(1))
                elif bedsSchedule == 2:
                    cond.append(tableHBSchedule['code'].ne(1))
                    condRepairs.append(tableHBSchedule['code'].ne(1))
                joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].ge(begDateTime)])
                joinOr2 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].lt(endDateTime)])
                cond.append(db.joinAnd([joinOr1, joinOr2]))

                if profile:
                    condRepairs.append(tableVHospitalBed['profile_id'].inlist(profile))

                condShortInvolute = db.joinOr([
                    db.joinAnd([
                        tableVHospitalBed['endDateInvolute'].isNull(),
                        tableVHospitalBed['begDateInvolute'].isNull()
                    ]),
                    db.joinAnd([
                        tableVHospitalBed['begDateInvolute'].isNotNull(),
                        tableVHospitalBed['begDateInvolute'].ge(begDateTime),
                        tableVHospitalBed['begDateInvolute'].lt(endDateTime)
                    ]),
                    db.joinAnd([
                        tableVHospitalBed['endDateInvolute'].isNotNull(),
                        tableVHospitalBed['endDateInvolute'].gt(begDateTime),
                        tableVHospitalBed['endDateInvolute'].le(endDateTime)])
                ])

                condStock = cond + [tableVHospitalBed['isPermanent'].eq(1)]
                condRolled = cond + [db.joinOr([condShortInvolute, tableVHospitalBed['involution'].ne(0)])]
                condRepairs.append(condShortInvolute)
                condRepairs.append(tableVHospitalBed['isPermanent'].eq(1))  # нужно ли это условие здесь?

                countTotalBeds = db.getCount(tableVHospitalBedSchedule, countCol='vHospitalBed.id', where=condStock)
                countRolledBeds = db.getCount(tableVHospitalBedSchedule, countCol='vHospitalBed.id', where=condRolled)
                countBedsRepairs = db.getCount(tableVHospitalBedSchedule, countCol='vHospitalBed.id', where=condRepairs)
                info[table.TotalBeds] = countTotalBeds
                info[table.UnrolledBeds] = countRolledBeds
                info[table.RepairBeds] = countBedsRepairs


        def getMovingPresent(profile = None, atBegin = True, isReanimation = False):
            cond = [ tableAction['deleted'].eq(0),
                     tableEvent['deleted'].eq(0),
                     tableAP['deleted'].eq(0),
                     tableActionType['deleted'].eq(0),
                     tableClient['deleted'].eq(0),
                     tableOS['deleted'].eq(0),
                     tableAPT['deleted'].eq(0),
                     tableAP['action_id'].eq(tableAction['id'])
                     ]
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            cond.append(tableOS['deleted'].eq(0))
            cond.append(tableAPT['typeName'].like('HospitalBed'))

            actionTypeIdList = getActionTypeIdListByFlatCode('reanimation%')
            # Если это не обработка реанимационных действий
            if not isReanimation:
                # то добавить и обычные движения в обработку
                actionTypeIdList.extend(getActionTypeIdListByFlatCode('moving%'))
            cond.append(tableAction['actionType_id'].inlist(actionTypeIdList))

            # формирование полного списка подразделений
            osIdList = list(orgStructureIdList)
            if isReanimation:
                osIdList.extend(reanimationOSIdList)

            if osIdList:
                cond.append(tableOSHB['master_id'].inlist(osIdList))

            #Работать только с переводами в реанимацию только из плановых отделений
            if isReanimation and orgStructureIdList:
                cond.append(getTransferPropertyIn(u'Переведен из отделения%', orgStructureIdList))

            if profile:
                if QtGui.qApp.defaultHospitalBedProfileByMoving():
                    cond.append(getPropertyAPHBP(profile))
                else:
                    cond.append(tableOSHB['profile_id'].inlist(profile))
            if bedsSchedule:
                queryTable = queryTable.innerJoin(tableHBSchedule, tableOSHB['schedule_id'].eq(tableHBSchedule['id']))
            if bedsSchedule == 1:
                cond.append(tableHBSchedule['code'].eq(1))
            elif bedsSchedule == 2:
                cond.append(tableHBSchedule['code'].ne(1))
            compareDate = begDateTime if atBegin else endDateTime
            cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].lt(compareDate)]))
            cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(compareDate)]))

            reanimationCond = [# Реанимация должна быть незавершенной на дату проверки (т.е. не иметь дату окончания или дата окончания должна быть после этой даты)
                u'reanimationAction.endDate IS NULL OR reanimationAction.endDate >= \'%s\'' % compareDate.toString(Qt.ISODate),
                # Реанимация должна начинаться в период действия текущего Движения
                u'reanimationAction.begDate >= Action.begDate',
                # Реанимация должна начинаться в период действия текущего Движения
                u'reanimationAction.begDate <= Action.endDate OR Action.endDate IS NULL',
                u'reanimationAction.event_id = Action.event_id',
                u'SourceAP.action_id = Action.id']
            reanimationExistsStmt = 'EXISTS(%s)' % getReanimationInfoTableStmt(u'Переведен из отделения%', reanimationCond) if not isReanimation else '0'
            cols = ['COUNT(IF(%s AND ActionType.flatCode LIKE \'moving%%\', NULL, 1)) AS countAll' % reanimationExistsStmt,
                    'SUM(%s AND NOT (ActionType.flatCode LIKE \'moving%%\' AND %s)) AS countPatronage' % (getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')'),
                                                                                                          reanimationExistsStmt)
                    ]
            stmt = db.selectStmt(queryTable,
                                 cols,
                                 where=cond)
            query = db.query(stmt)
            if query.first():
                record = query.record()
                return [forceInt(record.value('countAll')), forceInt(record.value('countPatronage'))]
            else:
                return [0, 0]

        # Сост. больных на нач. истек. суток
        def presentBegDay(profile = None, isReanimation = False):
            presentAll, presentPatronage = getMovingPresent(profile, True, isReanimation)
            info[table.PresentAtBegin] = presentAll
            #            totalInfo['total'][presentBegDayColumn] += presentAll
            totalInfo['patronage'][table.PresentAtBegin] += presentPatronage

        # Переведено больных внутри больницы/из др. отд.
        # orgStructureIdList - это список отделений перевод в(из) которые(-ых) надо учитывать, если пуст, то учитываются все переводы для указанной койки (i764)
        def fromMovingTransfer(profile = None, isReanimation = False):
            transferAll, transferPatronag, reanimationProfileIdList = getMovingTransfer(
                bedsSchedule,
                begDateTime,
                endDateTime,
                u'Переведен из отделения',
                profile,
                False,
                orgStructureIdList,
                reanimationOSIdList = reanimationOSIdList,
                isReanimation = isReanimation
            )
            info[table.MovedFrom] = transferAll
            # totalInfo['total'][fromMovingTransferColumn] += transferAll
            totalInfo['patronage'][table.MovedFrom] += transferPatronag
            return reanimationProfileIdList


        # Поступило всего больных
        def receivedAll(profile = None, isReanimation = False):
            receiveValues = getReceived(bedsSchedule,
                                        begDateTime,
                                        endDateTime,
                                        u'Переведен из отделения',
                                        profile,
                                        orgStructureIdList,
                                        countOrder=True) if not isReanimation else [0] * 8
            info[table.ReceivedAll] = receiveValues[0]
            info[table.ReceivedPanning] = receiveValues[6]
            info[table.ReceivedEmergency] = receiveValues[7]
            #            totalInfo['total'][receivedAllColumn] += receiveValues[0]
            totalInfo['patronage'][table.ReceivedAll] += receiveValues[5]
        #            totalInfo['total'][receivedScheduledColumn] += receiveValues[6]
        #            totalInfo['total'][receivedEmergencyColumn] += receiveValues[7]

        # Переведено больных внутри больницы/в др. отд.
        def inMovingTransfer(profile = None, isReanimation = False):
            transferAll, transferPatronag, reanimationProfileIdList = getMovingTransfer(
                bedsSchedule,
                begDateTime,
                endDateTime,
                u'Переведен в отделение',
                profile,
                True,
                orgStructureIdList,
                reanimationOSIdList = reanimationOSIdList,
                isReanimation = isReanimation
            )
            info[table.MovedTo] = transferAll
            # totalInfo['total'][inMovingTransferColumn] += transferAll
            totalInfo['patronage'][table.MovedTo] += transferPatronag
            return reanimationProfileIdList

        # Выписано всего больных;
        # в т.ч. переведено в др. стационары;
        # умерло
        def leavedAll(profile = None, isReanimation = False):
            countLeavedAll, leavedDeath, leavedTransfer, leavedAllPatronag, leavedDeathPatronag, leavedTransferPatronag, leavedElder, deadElder, leavedDayStat, leavedNoctidialStat = getLeaved(bedsSchedule,
                                                                                                                                                                                                begDateTime,
                                                                                                                                                                                                endDateTime,
                                                                                                                                                                                                profile,
                                                                                                                                                                                                orgStructureIdList) if not isReanimation else [0] * 6
            info[table.DismissedAll] = countLeavedAll
            #            totalInfo['total'][leavedAllColumn] += countLeavedAll
            totalInfo['patronage'][table.DismissedAll] += leavedAllPatronag

            info[table.DismissedWithMoving] = leavedTransfer
            #            totalInfo['total'][leavedTransferColumn] += leavedTransfer
            totalInfo['patronage'][table.DismissedWithMoving] += leavedTransferPatronag

            info[table.Died] = leavedDeath
            #            totalInfo['total'][leavedDeathColumn] += leavedDeath
            totalInfo['patronage'][table.Died] += leavedDeathPatronag

        # На начало текущего дня/Состоит больных всего
        # На начало текущего дня/Состоит матерей при больных детях
        def presentEndDay(profile = None, isReanimation = False):
            presentAll, presentPatronage = getMovingPresent(profile, False, isReanimation)
            info[table.PresentAtEnd] = presentAll
            #            totalInfo['total'][presentEndDayColumn] += presentAll
            totalInfo['patronage'][table.PresentAtEnd] += presentPatronage

            info[table.Patronaged] = presentPatronage
            #            totalInfo['total'][presentEndDayPatronageColumn] += presentPatronage
            totalInfo['patronage'][table.Patronaged] += presentPatronage

            presentAll, presentPatronage = getMovingPresent(profile, False, True)
            info[table.ReanimatedAtEnd] = presentAll
            #            totalInfo['total'][presentEndDayReanimationColumn] += presentAll
            totalInfo['patronage'][table.ReanimatedAtEnd] += presentPatronage

        def getOrgStructureLists(root):
            allIds = db.getDistinctIdList(tableOSHB, idCol='master_id')
            idList = list(set(allIds).intersection(getOrgStructureDescendants(root))) if root else allIds
            return [[item] for item in idList] if detailOrgStructure else [idList]

        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')

        tableOS = db.table('OrgStructure')
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableVHospitalBed = db.table('vHospitalBed')
        tableHBSchedule = db.table('rbHospitalBedShedule')

        begTime = QtGui.qApp.changingDayTime()
        endDate = params.get('endDate', QDate())
        if not endDate:
            endDate = QDate.currentDate()
        if endDate:
            endDateTime = QDateTime(endDate, begTime.addSecs(-60))
            begDateTime = QDateTime(endDate.addDays(-1), begTime)
            bedsSchedule = params.get('bedsSchedule', 0)
            profileBedId = params.get('profileBed', None)
            orgStructures = params.get('orgStructures', None)
            isShowBeds = not params.get('isHideBeds', False)
            detailOrgStructure = params.get('detailOrgStructure', False) or not isShowBeds
            # выбранные (плановые) подразделения
            orgStructureIdLists = []
            for x in orgStructures:
                orgStructureIdLists += getOrgStructureLists(x)  # orgStructureIdLists = getOrgStructureLists(orgStructureId)
            # подразделения, соответствующие действиям "реанимация" (связанным с выбранными подразделениями) и найденные в процессе формирования отчета по плановым

            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertBlock()
            orgName, _ = self.getOrgInfo()
            changingDayTime = QtGui.qApp.changingDayTime()
            timeString = u'%d часов %d минут' % (changingDayTime.hour(), changingDayTime.minute())
            self.insertCaption(cursor, params, orgName, timeString)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()

            #акробатика ниже понадобилась, чтобы не запутаться в многочисленных колонках

            ColIdx = CReportTableBase.ColumnIndex
            cols = [(u'ProfileName', '10%',  [u'Наименование отделения' + (u', профиля коек' if isShowBeds else u''), u'', u'', ColIdx, u'Всего:', u'Ухаживающие'], CReportBase.AlignRight)]
            if isShowBeds:
                cols.extend([(u'TotalBeds', '5.6%', [u'Кол-во коек по коечному фонду', u'', u'', ColIdx], CReportBase.AlignRight),
                             (u'UnrolledBeds', '5.6%', [u'Факт. развернуто коек', u'', u'', ColIdx], CReportBase.AlignRight),
                             (u'RepairBeds', '5.6%', [u'в т.ч. коек, свернутых на ремонт', u'', u'', ColIdx], CReportBase.AlignRight)])

            cols.extend([(u'PresentAtBegin', '5.6%', [u'Сост. больных на нач. истек. суток', u'', u'', ColIdx], CReportBase.AlignRight),
                         (u'ReceivedAll', '5.6%', [u'Поступило больных', u'Всего', u'', ColIdx], CReportBase.AlignRight),
                         (u'ReceivedPanning', '5.6%', [u'', u'Планово', u'', ColIdx], CReportBase.AlignRight),
                         (u'ReceivedEmergency', '5.6%', [u'', u'Экстренно', u'', ColIdx], CReportBase.AlignRight),
                         (u'MovedFrom', '5.6%', [u'Переведено больных внутри больницы', u'из др.отд.', u'', ColIdx], CReportBase.AlignRight),
                         (u'MovedTo', '5.6%', [u'', u'в др. отд.', u'', ColIdx], CReportBase.AlignRight),
                         (u'DismissedAll', '5.6%', [u'Выписано', u'Всего', u'', ColIdx], CReportBase.AlignRight),
                         (u'DismissedWithMoving', '5.6%', [u'', u'в т.ч. переведено в др. стационары', u'', ColIdx], CReportBase.AlignRight),
                         (u'Died', '5.6%', [u'', u'Умерло', u'', ColIdx], CReportBase.AlignRight),
                         (u'PresentAtEnd', '5.6%', [u'Состоит больных на начало текущего дня', u'Всего', u'', ColIdx], CReportBase.AlignRight),
                         (u'Patronaged', '5.6%', [u'', u'Матерей при больных детях', u'', ColIdx], CReportBase.AlignRight),
                         (u'ReanimatedAtEnd', '5.6%', [u'', u'Больных в реанимации', u'', ColIdx], CReportBase.AlignRight)
                         ])
            if isShowBeds:
                cols.append((u'FreeBeds', '5.6%', [u'Свободных коек', u'', u'', ColIdx], CReportBase.AlignRight))

            table = createTable(cursor, cols)

            table.mergeCells(0, table.ProfileName, 3, 1) # Наименование отделения, профиля коек
            if isShowBeds:
                table.mergeCells(0, table.TotalBeds, 3, 1) # Факт. развернуто коек
                table.mergeCells(0, table.UnrolledBeds, 3, 1) # Факт. развернуто коек
                table.mergeCells(0, table.RepairBeds, 3, 1) # в т.ч. коек, свернутых на ремонт

            table.mergeCells(0, table.PresentAtBegin, 3, 1) # Сост. больных на нач. истек. суток

            table.mergeCells(0, table.ReceivedAll, 1, 3) # Поступило больных
            table.mergeCells(0, table.ReceivedAll, 2, 1) # Всего
            table.mergeCells(0, table.ReceivedPanning, 2, 1) # Планово
            table.mergeCells(0, table.ReceivedEmergency, 2, 1) # Экстренно

            #table.mergeCells(0, fromMovingTransferColumn, 1, 5) # Движение больных за истекшие сутки
            table.mergeCells(0, table.MovedFrom, 1, 2) # Переведено больных внутри больницы
            table.mergeCells(1, table.MovedFrom, 2, 1) # Переведено больных внутри больницы
            table.mergeCells(1, table.MovedTo, 2, 1) # Переведено больных внутри больницы

            table.mergeCells(0, table.DismissedAll, 1, 3) # Выписано
            table.mergeCells(1, table.DismissedAll, 2, 1) # Всего
            table.mergeCells(1, table.DismissedWithMoving, 2, 1) # в т.ч. переведено в др. стационары
            table.mergeCells(1, table.Died, 2, 1) # Умерло

            table.mergeCells(0, table.PresentAtEnd, 1, 3) # Состоит больных на начало текущего дня
            table.mergeCells(1, table.PresentAtEnd, 2, 1) # Всего
            table.mergeCells(1, table.Patronaged, 2, 1) # Матерей при больных детях
            table.mergeCells(1, table.ReanimatedAtEnd, 2, 1) # Больных в реанимации
            if isShowBeds:
                table.mergeCells(0, table.FreeBeds, 3, 1) # Свободных коек

            totalInfo = {'total'    : [0] * len(cols),
                         'patronage': [0] * len(cols)}


            tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')

            for orgStructureIdList in orgStructureIdLists:
                if detailOrgStructure:
                    row = table.addRow()
                    table.setText(row, table.ProfileName, forceString(db.translate(tableOS, 'id', orgStructureIdList[0], 'name')), blockFormat=CReportBase.AlignLeft, charFormat=boldChars)
                    table.mergeCells(row, table.ProfileName, 1, len(cols))

                cond = []
                totalByOrgStructureList = {'total': [0] * len(cols), 'patronage': [0] * len(cols)}
                reanimationOSIdList = []
                profileIdList = []
                hospitalBedIdList = []
                if orgStructureIdList:
                    cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
                if QtGui.qApp.defaultHospitalBedProfileByMoving():
                    hospitalBedIdList = self.getHospitalBedIdList(db,
                                                                  tableVHospitalBed,
                                                                  tableHBSchedule,
                                                                  bedsSchedule,
                                                                  (begDateTime, endDateTime),
                                                                  orgStructureIdList)
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
                            tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%') + getActionTypeIdListByFlatCode('reanimation%')),
                            tableAPT['typeName'].like('rbHospitalBedProfile')
                            ]
                    joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
                    joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)])
                    joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDateTime)])
                    cond.append(db.joinOr([joinOr1, joinOr2, joinOr3]))
                    cond.append(u'''EXISTS(SELECT APHB.value
                                        FROM ActionProperty AS AP
                                        INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.`id`=AP.`id`
                                        INNER JOIN Action AS A ON A.`id`=AP.`action_id`
                                        INNER JOIN ActionPropertyType AS APT ON APT.`id`=AP.`type_id`
                                        WHERE (AP.`action_id` IS NOT NULL AND AP.`action_id` = Action.id) AND (AP.`deleted`=0) AND (APT.`deleted`=0)
                                        AND (APT.`typeName` LIKE 'HospitalBed') AND (APHB.`value` IN (%s)))'''%(u','.join(str(hospitalBedId) for hospitalBedId in hospitalBedIdList if hospitalBedId)))
                    records = db.getRecordList(queryTable, [tableRbHospitalBedProfile['id'], tableRbHospitalBedProfile['code'], tableRbHospitalBedProfile['name']], cond)
                    for record in records:
                        profileId = forceRef(record.value('id'))
                        if profileId not in profileIdList:
                            profileIdList.append(profileId)
                else:
                    queryTable = tableOSHB.innerJoin(tableRbHospitalBedProfile, tableOSHB['profile_id'].eq(tableRbHospitalBedProfile['id']))
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


                processedProfileIdList = []
                reanimationProfileIdList = []
                isReanimation = False
                while profileIdList:
                    info = [0] * len(cols)
                    if isShowBeds:
                        rowProfile = table.addRow()
                    profileId = profileIdList.pop(0)

                    if profileId in processedProfileIdList:
                        continue
                    else:
                        processedProfileIdList.append(profileId)

                    if isShowBeds:
                        profileName = forceString(db.translate(tableRbHospitalBedProfile, 'id', profileId, 'name'))
                        table.setText(rowProfile, table.ProfileName, profileName)

                    if isShowBeds:
                        unrolledHospitalBed34(hospitalBedIdList, [profileId], rowProfile)
                    presentBegDay([profileId], isReanimation)
                    receivedAll([profileId], isReanimation)
                    reanimationProfileIdList.extend(fromMovingTransfer([profileId],
                                                                       isReanimation))
                    reanimationProfileIdList.extend(inMovingTransfer([profileId],
                                                                     isReanimation))
                    leavedAll([profileId], isReanimation)
                    presentEndDay([profileId], isReanimation)
                    # info[rolledBedsColumn] = info[totalBedsColumn] - info[bedsRepairsColumn]
                    if isShowBeds:
                        info[table.FreeBeds] = info[table.UnrolledBeds] - info[table.PresentAtEnd]


                    for column in xrange(1, len(cols)):
                        if isShowBeds:
                            table.setText(rowProfile, column, info[column])
                        totalByOrgStructureList['total'][column] += info[column]

                    if not profileIdList and reanimationProfileIdList:
                        profileIdList = reanimationProfileIdList
                        isReanimation = True

                for row in ['total', 'patronage']:
                    for column in xrange(1, len(cols)):
                        totalInfo[row][column] += totalByOrgStructureList[row][column]
                if detailOrgStructure:
                    row = table.addRow()
                    table.setText(row, table.ProfileName, u'Всего по отделению:', blockFormat=CReportBase.AlignCenter, charFormat=boldChars)
                    for column in xrange(1, len(cols)):
                        table.setText(row, column, totalByOrgStructureList['total'][column])
            if isShowBeds:
                for row in ['total', 'patronage']:
                    totalInfo[row][table.FreeBeds] = totalInfo[row][table.UnrolledBeds] - totalInfo[row][table.PresentAtEnd]
            for column in xrange(1, len(cols)):
                table.setText(4, column, totalInfo['total'][column])
                table.setText(5, column, totalInfo['patronage'][column])

        return doc


class CStationaryF007ClientList(CStationaryF007):
    def __init__(self, parent):
        super(CStationaryF007ClientList, self).__init__(parent)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара')

    def build(self, params):
        db = QtGui.qApp.db
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableHBSchedule = db.table('rbHospitalBedShedule')

        begTime = params.get('begTime', QTime(7, 0))
        endDate = params.get('endDate', QDate())
        if not endDate:
            endDate = QDate.currentDate()
        if endDate:
            endDateTime = QDateTime(endDate, begTime)
            begDateTime = QDateTime(endDate.addDays(-1), begTime)
            bedsSchedule = getVal(params, 'bedsSchedule', 0)
            profileBedId = params.get('profileBed', None)
            # orgStructureIndex = self.stationaryF007SetupDialog.cmbOrgStructure._model.index(self.stationaryF007SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF007SetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = getVal(params, 'orgStructures', [])  # self.getOrgStructureIdList(orgStructureIndex)
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertBlock()
            orgName, orgOKPO = self.getOrgInfo()
            self.insertCaption(cursor, params, orgName, orgOKPO, u'СПИСОК БОЛЬНЫХ')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('14.3%',[u'ФИО поступивших', u''], CReportBase.AlignLeft),
                    ('14.3%', [u'ФИО переведенных из других отделений', u''], CReportBase.AlignLeft),
                    ('14.3%', [u'ФИО выписанных', u''], CReportBase.AlignLeft),
                    ('14.3%', [u'ФИО переведенных', u'в другие отделения данной больницы'], CReportBase.AlignLeft),
                    ('14.3%', [u'', u'в другие стационары'], CReportBase.AlignLeft),
                    ('14.3%', [u'ФИО умерших', u''], CReportBase.AlignLeft),
                    #                    ('14.3%', [u'ФИО больных, находящихся во временном отпуске', u''], CReportBase.AlignLeft)
                    ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 2, 1)
            table.mergeCells(0, 1, 2, 1)
            table.mergeCells(0, 2, 2, 1)
            table.mergeCells(0, 3, 1, 2)
            table.mergeCells(0, 5, 2, 1)
            table.mergeCells(0, 6, 2, 1)

            tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')
            cond = []
            if orgStructureIdList:
                cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
            queryTable = tableOSHB.innerJoin(tableRbHospitalBedProfile, tableOSHB['profile_id'].eq(tableRbHospitalBedProfile['id']))
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
            def setInfoClient(nextQuery, firstRow, nextRow, column):
                i = firstRow
                while nextQuery.next():
                    if i <= nextRow:
                        record = nextQuery.record()
                        lastName = forceString(record.value('lastName'))
                        firstName = forceString(record.value('firstName'))
                        patrName = forceString(record.value('patrName'))
                        table.setText(i, column, lastName + u' ' + firstName + u' ' + patrName)
                        i += 1
            receivedAll = getReceived(bedsSchedule, begDateTime, endDateTime, u'Переведен из отделения', profileIdList, orgStructureIdList, True)
            # из других отделений
            fromMovingTransfer = getMovingTransfer(bedsSchedule, begDateTime, endDateTime, u'Переведен из отделения', profileIdList, False, orgStructureIdList, True)
            # в другие отделения
            inMovingTransfer = getMovingTransfer(bedsSchedule, begDateTime, endDateTime, u'Переведен в отделение', profileIdList, True, orgStructureIdList, True)
            leavedAll, leavedDeath, leavedTransfer = getLeaved(bedsSchedule, begDateTime, endDateTime, profileIdList, orgStructureIdList, True)
            sizeQuerys = [receivedAll.size(),
                          fromMovingTransfer.size(),
                          inMovingTransfer.size(),
                          leavedAll.size(),
                          leavedDeath.size(),
                          leavedTransfer.size()
                          ]
            sizeQuerysMax = -1
            for sizeQuery in sizeQuerys:
                if sizeQuery > sizeQuerysMax:
                    sizeQuerysMax = sizeQuery
            firstRow = -1
            nextRow = -1
            for newRow in range(0, sizeQuerysMax):
                i = table.addRow()
                nextRow = i
                if firstRow == -1:
                    firstRow = i
            setInfoClient(receivedAll, firstRow, nextRow, 0)
            setInfoClient(fromMovingTransfer, firstRow, nextRow, 1)
            setInfoClient(inMovingTransfer, firstRow, nextRow, 3)
            setInfoClient(leavedAll, firstRow, nextRow, 2)
            setInfoClient(leavedDeath, firstRow, nextRow, 5)
            setInfoClient(leavedTransfer, firstRow, nextRow, 4)
        return doc
    
    
class CStationaryF007ClientList2013(CStationaryF007ClientList):
    def __init__(self, parent):
        super(CStationaryF007ClientList2013, self).__init__(parent)
        self.setTitle(u'Листок учета движения больных и коечного фонда стационара (2013)')

    def build(self, params):
        db = QtGui.qApp.db
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableHBSchedule = db.table('rbHospitalBedShedule')

        begTime = params.get('begTime', QTime(7, 0))
        endDate = params.get('endDate', QDate())
        if not endDate:
            endDate = QDate.currentDate()
        if endDate:
            endDateTime = QDateTime(endDate, begTime)
            begDateTime = QDateTime(endDate.addDays(-1), begTime)
            bedsSchedule = getVal(params, 'bedsSchedule', 0)
            profileBedId = params.get('profileBed', None)
            # orgStructureIndex = self.stationaryF007SetupDialog.cmbOrgStructure._model.index(self.stationaryF007SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF007SetupDialog.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = getVal(params, 'orgStructures', [])  # self.getOrgStructureIdList(orgStructureIndex)
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertBlock()
            orgName, orgOKPO = self.getOrgInfo()
            self.insertCaption(cursor, params, orgName, orgOKPO, u'СПИСОК БОЛЬНЫХ')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('4%', [u'Поступившие', u'№ И/Б'], CReportBase.AlignLeft),
                    ('12.6%', [u'', u'Фамилия И.О.'], CReportBase.AlignLeft),
                    ('4%', [u'Переведенные из других отделений', u'№ И/Б'], CReportBase.AlignLeft),
                    ('12.6%', [u'', u'Фамилия И.О.'], CReportBase.AlignLeft),
                    ('4%', [u'Выписанные', u'№ И/Б'], CReportBase.AlignLeft),
                    ('12.6%', [u'', u'Фамилия И.О.'], CReportBase.AlignLeft),
                    ('4%', [u'Переведенные в другие отделения больницы', u'№ И/Б'], CReportBase.AlignLeft),
                    ('12.6%', [u'', u'Фамилия И.О.'], CReportBase.AlignLeft),
                    ('4%', [u'Переведенные в другие стаицонары', u'№ И/Б'], CReportBase.AlignLeft),
                    ('12.6%', [u'', u'Фамилия И.О.'], CReportBase.AlignLeft),
                    ('4%', [u'Умершие', u'№ И/Б'], CReportBase.AlignLeft),
                    ('12.6%', [u'', u'Фамилия И.О.'], CReportBase.AlignLeft),
                    ]
            table = createTable(cursor, cols)

            table.mergeCells(0, 0, 1, 2)
            table.mergeCells(0, 2, 1, 2)
            table.mergeCells(0, 4, 1, 2)
            table.mergeCells(0, 6, 1, 2)
            table.mergeCells(0, 8, 1, 2)
            table.mergeCells(0, 10, 1, 2)

            tableRbHospitalBedProfile = db.table('rbHospitalBedProfile')
            cond = []
            if orgStructureIdList:
                cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
            queryTable = tableOSHB.innerJoin(tableRbHospitalBedProfile, tableOSHB['profile_id'].eq(tableRbHospitalBedProfile['id']))
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


            def setInfoClient(nextQuery, column):
                i = 1
                processedActionsIdList = []
                while nextQuery.next():
                    record = nextQuery.record()
                    eventExternalId = forceString(record.value('externalId'))
                    clientName = '%s %s %s'  % (forceString(record.value('lastName')),
                                                forceString(record.value('firstName')),
                                                forceString(record.value('patrName')))
                    clientBedProfile = forceString(record.value('profileName'))
                    isPatronage = forceBool(record.value('nursing'))
                    actionId = forceRef(record.value('actionId'))
                    isOrdinaryMoving = forceBool(record.value('isOrdinaryMoving'))
                    orgStructureName = forceString(record.value('orgStructureName'))
                    reanimationActionId = forceRef(record.value('reanimationActionId'))
                    if actionId not in processedActionsIdList and (isOrdinaryMoving or reanimationActionId):
                        processedActionsIdList.append(actionId)
                        if isOrdinaryMoving:
                            clientText = '%s\n%s\n(%s)%s' % (clientName,
                                                             orgStructureName,
                                                             clientBedProfile,
                                                             u'\nУход' if isPatronage else '')
                            i = i + 1 if i < (table.table.rows() - 1) else table.addRow()
                            table.setText(i, column, eventExternalId)
                            table.setText(i, column + 1, clientText)
                        if reanimationActionId:
                            clientText = '%s\n%s\n(%s)%s' % (clientName,
                                                             u'РО',
                                                             clientBedProfile,
                                                             u'\nУход' if isPatronage else '')
                            i = i + 1 if i < (table.table.rows() - 1) else table.addRow()
                            table.setText(i, column, eventExternalId)
                            table.setText(i, column + 1, clientText)

            receivedAll = getReceived(bedsSchedule, begDateTime, endDateTime, u'Переведен из отделения%', profileIdList, orgStructureIdList, True)
            # из других отделений
            fromMovingTransfer = getMovingTransfer(bedsSchedule, begDateTime, endDateTime, u'Переведен из отделения%', profileIdList, False, orgStructureIdList, True)
            # в другие отделения
            inMovingTransfer = getMovingTransfer(bedsSchedule, begDateTime, endDateTime, u'Переведен в отделение%', profileIdList, True, orgStructureIdList, True)
            leavedAll, leavedDeath, leavedTransfer = getLeaved(bedsSchedule, begDateTime, endDateTime, profileIdList, orgStructureIdList, True)


            setInfoClient(receivedAll, 0)
            setInfoClient(fromMovingTransfer, 2)
            setInfoClient(leavedAll, 4)
            setInfoClient(inMovingTransfer, 6)
            setInfoClient(leavedTransfer, 8)
            setInfoClient(leavedDeath, 10)
        return doc
    

#Данные по действию "Реанимация", у которого свойство "Переведен из/в" соответствует свойству "Отделение пребывания" исходного движения
def getReanimationInfoTableStmt(transferPropertyName, cond = None):
    return u"""
            SELECT DISTINCT
                reanimationAction.id AS actionId,
                reanimationAction.begDate,
                reanimationAction.endDate,
                reanimationOSHB.profile_id AS profileId, 
                reanimationAction.event_id AS eventId,
                reanimationOSHB.master_id AS orgStructureId,
                SourceAP.action_id AS sourceActionId
            FROM Action AS reanimationAction
                INNER JOIN ActionType AS reanimationAT ON (reanimationAT.id = reanimationAction.actionType_id 
                                                           AND reanimationAT.deleted = 0 
                                                           AND reanimationAT.flatCode LIKE 'reanimation%%')
                INNER JOIN ActionPropertyType AS reanimationTransferAPT ON (reanimationTransferAPT.actionType_id = reanimationAT.id 
                                                                           AND reanimationTransferAPT.deleted = 0 
                                                                           AND reanimationTransferAPT.name LIKE '%(transferPropertyName)s')
                INNER JOIN ActionProperty AS reanimationTransferAP ON (reanimationTransferAP.type_id = reanimationTransferAPT.id
                                                                      AND reanimationTransferAP.action_id = reanimationAction.id
                                                                      AND reanimationTransferAP.deleted = 0)
                INNER JOIN ActionProperty_OrgStructure AS reanimationTransferAPOS ON (reanimationTransferAPOS.id = reanimationTransferAP.id 
                                                                                      AND reanimationTransferAPOS.value IS NOT NULL) 
                -- Отделение пребывания исследуемого/исходного "движения"
                INNER JOIN ActionType AS SourceAT ON (SourceAT.flatCode like 'moving%%' AND SourceAT.deleted = 0)
                INNER JOIN Action AS SourceAction ON (SourceAction.actionType_id = SourceAT.id 
                                                       AND SourceAction.deleted = 0 
                                                       AND SourceAction.event_id = reanimationAction.event_id)
                INNER JOIN ActionPropertyType AS SourceAPT ON (SourceAPT.actionType_id = SourceAT.id
                                                              AND SourceAPT.name LIKE 'Отделение пребывания%%'
                                                              AND SourceAPT.deleted = 0) -- Койка действия "Реанимация"
                INNER JOIN ActionProperty AS SourceAP ON SourceAP.type_id = SourceAPT.id AND SourceAP.action_id = SourceAction.id AND SourceAP.deleted = 0                  
                INNER JOIN ActionProperty_OrgStructure AS SourceAPOS ON (SourceAPOS.id = SourceAP.id
                                                                           -- отделение пребывания "движения" соответствует свойству "переведен из/в" "реанимации"
                                                                           AND SourceAPOS.value = reanimationTransferAPOS.value)
                -- койка в реанимации
                LEFT JOIN ActionPropertyType AS reanimationBedAPT ON (reanimationBedAPT.actionType_id = reanimationAT.id
                                                                     AND reanimationBedAPT.typeName LIKE 'HospitalBed'
                                                                     AND (reanimationBedAPT.deleted = 0 OR reanimationBedAPT.deleted IS NULL))
                LEFT JOIN ActionProperty AS reanimationBedAP ON (reanimationBedAP.action_id = reanimationAction.id
                                                                AND reanimationBedAP.type_id = reanimationBedAPT.id
                                                                AND (reanimationBedAP.deleted = 0 OR reanimationBedAP.deleted IS NULL))
                LEFT JOIN ActionProperty_HospitalBed AS reanimationAPHP ON reanimationAPHP.id = reanimationBedAP.id
                -- Отделение пребывания Реанимации
                LEFT JOIN OrgStructure_HospitalBed AS reanimationOSHB ON reanimationOSHB.id = reanimationAPHP.value 
                
            
            WHERE reanimationAction.deleted=0 AND %(cond)s
                """ % {u'transferPropertyName' : transferPropertyName,
                       u'cond' : QtGui.qApp.db.joinAnd(cond) or '1'}


# orgStructureIdList - это список подразделение, выбранных пользователем для поиска переводов
# reanimationOSIdList - это список подразделение перевод в(из) которые(-ых) надо учитывать, если пуст, то учитываются все переводы для указанной койки (i764)
def getMovingTransfer(bedsSchedule, begDateTime, endDateTime, nameProperty, profile=None, transferIn=False,
                      orgStructureIdList=None, boolFIO=False, reanimationOSIdList=None, isReanimation=False,
                      simplifyDateCond=False, socStatusTypeId=None, socStatusClassId=None):
    if not orgStructureIdList:
        orgStructureIdList = []
    if not reanimationOSIdList:
        reanimationOSIdList = []
    db = QtGui.qApp.db
    tableAPT = db.table('ActionPropertyType')
    tableAP = db.table('ActionProperty')
    tableActionType = db.table('ActionType')
    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    
    tableOS = db.table('OrgStructure')
    tableAPHB = db.table('ActionProperty_HospitalBed')
    tableOSHB = db.table('OrgStructure_HospitalBed')
    tableHBSchedule = db.table('rbHospitalBedShedule')
    cond = [ tableAction['deleted'].eq(0),
             tableEvent['deleted'].eq(0),
             tableAP['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableAP['action_id'].eq(tableAction['id'])
           ]
    
    actionTypeCond = [tableActionType['flatCode'].like('reanimation%')]
    if not isReanimation:
        actionTypeCond.append(tableActionType['flatCode'].like('moving%'))
    
    # Искать действия "движение" и "реанимация" (которое является тем же движением)
    cond.append(db.joinOr(actionTypeCond))
    
    # ordinaryMoving - это движение/реанимация, у которого есть свойство "переведен из/в", заполненное отделением, попадающим в список обрабатываемых для реанимации
    # Условие для определения, что 
    ordinaryTransferCond = [getTransferPropertyIn(nameProperty, orgStructureIdList if isReanimation else None)]
    reanimationCond = []

    if simplifyDateCond:
        cond.append(db.joinAnd([tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)]))
    else:
        cond.append(db.joinOr([tableAction['endDate'].gt(begDateTime), tableAction['endDate'].isNull()]))
        cond.append(db.joinOr([tableAction['begDate'].lt(endDateTime), tableAction['begDate'].isNull()]))
    # atronah: Условие, проверяющее, что у законченного действия-реанимация (имеющего дату окончания) 
    # есть свойство "Переведен в отделение%".
    # Иначе (если дата окончания есть, а перевода в др. отделение отсутствует) считать, 
    # что это случай создания нового обращения через создание движения и реанимация продолженна в новом событии
    # и не должна учитываться дважды.
    cond.append(u'IF(%s, %s, 1)' % (db.joinAnd([tableActionType['flatCode'].like('reanimation%'),
                                                tableAction['endDate'].isNotNull()]),
                                    getTransferProperty(u'Переведен в отделение%', u'Action')))
    if transferIn:        
        # Действие "Переведен в" актуально для завершенных действий и дата их начала не имеет значения
        ordinaryTransferCond.append(tableAction['endDate'].le(endDateTime))
        
        # Реанимация должна иметь свойство "Переведен из отделение", заполненное отделением пребывания Движения
        reanimationInfoTableStmt = getReanimationInfoTableStmt(u'Переведен из отделения%')
        # Реанимация должна быть начата в выбранный период
        reanimationCond.append(u'ReanimationInfoTable.begDate BETWEEN \'%s\' AND \'%s\''  % (begDateTime.toString(Qt.ISODate), endDateTime.toString(Qt.ISODate)))
        # Реанимация должна быть начата в рамках движения (т.е. начата позже, чем само движение)
        reanimationCond.append(u'ReanimationInfoTable.begDate >= Action.begDate')
        # Реанимация должна быть начата в рамках движения (т.е. начата раньше, чем окончание движения)
        reanimationCond.append(u'ReanimationInfoTable.begDate <= Action.endDate OR Action.endDate IS NULL')                           
    else:
        # Действие "Переведен из" актуально для начатых действий и дата их окончания не имеет значения
        ordinaryTransferCond.append(tableAction['begDate'].ge(begDateTime))
        
        # Реанимация должна иметь свойство "Переведен в отделение", заполненное отделением пребывания Движения
        reanimationInfoTableStmt = getReanimationInfoTableStmt(u'Переведен в отделение%')
        # Реанимация должна быть начата после текущего действия, чтобы иметь к нему отношение
        reanimationCond.append(u'ReanimationInfoTable.endDate >= Action.begDate')
        # Реанимация должна быть закончена в выбранный период
        reanimationCond.append(u'ReanimationInfoTable.endDate BETWEEN \'%s\' AND \'%s\''  % (begDateTime.toString(Qt.ISODate), endDateTime.toString(Qt.ISODate)))
        # Реанимация должна быть завершена в рамках этого движения (т.е. завершена раньше, чем само движение)
        reanimationCond.append(u'ReanimationInfoTable.endDate <= Action.endDate OR Action.endDate IS NULL')
    

    queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableAPT, [tableAPT['actionType_id'].eq(tableActionType['id']),
                                                 tableAPT['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableAP, [tableAP['type_id'].eq(tableAPT['id']),
                                                tableAP['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
    queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
    queryTable = queryTable.innerJoin(tableOS, [tableOS['id'].eq(tableOSHB['master_id']),
                                                tableOS['deleted'].eq(0)])
    cond.append(tableAPT['typeName'].like(u'HospitalBed'))
    
    osIdList = list(orgStructureIdList)
    if isReanimation and reanimationOSIdList:
        osIdList.extend(reanimationOSIdList)
    if osIdList:
        cond.append(tableOSHB['master_id'].inlist(osIdList))
    if profile:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            cond.append(getPropertyAPHBP(profile))
        else:
            cond.append(tableOSHB['profile_id'].inlist(profile))
    if bedsSchedule:
        queryTable = queryTable.innerJoin(tableHBSchedule, tableOSHB['schedule_id'].eq(tableHBSchedule['id']))
    if bedsSchedule == 1:
        cond.append(tableHBSchedule['code'].eq(1))
    elif bedsSchedule == 2:
        cond.append(tableHBSchedule['code'].ne(1))

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

    cols = [tableAction['id'].alias('actionId'),
            u'(%s) AS isOrdinaryMoving' % db.joinAnd(ordinaryTransferCond), 
            u'ReanimationInfoTable.profileId AS reanimationProfileId',
            u'ReanimationInfoTable.actionId AS reanimationActionId',
            u'ReanimationInfoTable.orgStructureId AS reanimationOrgStructureId',
            u'(%s) AS isPatronage' % getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')')]
    
    if boolFIO:
        tableRBBedProfile = db.table('rbHospitalBedProfile')
#        tablePlaceAction = tableAction.alias('placeAction')
        tablePlaceAPT = tableAPT.alias('PlaceAPT')
        tablePlaceAP = tableAP.alias('PlaceAP')
        tablePlaceAPOS = db.table('ActionProperty_OrgStructure').alias('PlaceAPOS')
        tablePlaceOS = tableOS.alias('PlaceOS')
        
        queryTable = queryTable.leftJoin(tableRBBedProfile, tableRBBedProfile['id'].eq(tableOSHB['profile_id']))
#        queryTable = queryTable.leftJoin(tablePlaceAction, [tablePlaceAction['event_id'].eq(tableEvent['id']),
#                                                            tablePlaceAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%')),
#                                                            db.joinOr([tablePlaceAction['begDate'].isNull(), tablePlaceAction['begDate'].le(endDateTime)]),
#                                                            db.joinOr([tablePlaceAction['endDate'].isNull(), tablePlaceAction['endDate'].ge(endDateTime)]),
#                                                            db.joinOr([tablePlaceAction['deleted'].eq(0), tablePlaceAction['deleted'].isNull()])])
        queryTable = queryTable.leftJoin(tablePlaceAPT, [tablePlaceAPT['actionType_id'].eq(tableAction['actionType_id']),
                                                         tablePlaceAPT['name'].like(nameProperty),
                                                         db.joinOr([tablePlaceAPT['deleted'].eq(0), tablePlaceAPT['deleted'].isNull()])])
        queryTable = queryTable.leftJoin(tablePlaceAP, [tablePlaceAP['type_id'].eq(tablePlaceAPT['id']),
                                                        tablePlaceAP['action_id'].eq(tableAction['id']),
                                                        db.joinOr([tablePlaceAP['deleted'].eq(0), tablePlaceAP['deleted'].isNull()])])
        queryTable = queryTable.leftJoin(tablePlaceAPOS, tablePlaceAPOS['id'].eq(tablePlaceAP['id']))
        queryTable = queryTable.leftJoin(tablePlaceOS, [tablePlaceOS['id'].eq(tablePlaceAPOS['value']),
                                                        tablePlaceOS['deleted'].eq(0),
                                                        db.joinOr([tablePlaceOS['deleted'].eq(0), tablePlaceOS['deleted'].isNull()])])
        
        stmt = u'SELECT DISTINCT %s FROM %s WHERE  %s' % (db.prepareFieldList([tableAction['id'].alias('actionId'),
                                                                               u'(%s) AS isOrdinaryMoving' % db.joinAnd(ordinaryTransferCond),
                                                                               tableEvent['externalId'],
                                                                               tableClient['lastName'],
                                                                               tableClient['firstName'],
                                                                               tableClient['patrName'],
                                                                               u'ReanimationInfoTable.actionId AS reanimationActionId',
                                                                               tablePlaceOS['code'].alias('orgStructureName'),
                                                                               tableRBBedProfile['name'].alias('profileName'),
                                                                               '(%s AND ReanimationInfoTable.actionId IS NULL) AS nursing' % getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')'),
                                                                              ]),
                                                         u'%s LEFT JOIN (%s) AS ReanimationInfoTable ON (%s)' % (queryTable.name(), 
                                                                                                                reanimationInfoTableStmt,
                                                                                                                db.joinAnd([u'ReanimationInfoTable.eventId = Event.id',
                                                                                                                            u'ReanimationInfoTable.sourceActionId = Action.id',
                                                                                                                            tableActionType['flatCode'].like('moving%')
                                                                                                                            ] + reanimationCond
                                                                                                                           )
                                                                                                                ),
                                                         db.joinAnd(cond)
                                                         )
        return db.query(stmt)
    else:
        stmt = u'SELECT %s FROM %s WHERE %s' % (db.prepareFieldList(cols),
                                               u'%s LEFT JOIN (%s) AS ReanimationInfoTable ON (%s)' % (queryTable.name(), 
                                                                                                      reanimationInfoTableStmt,
                                                                                                      db.joinAnd([u'ReanimationInfoTable.eventId = Event.id',
                                                                                                                  u'ReanimationInfoTable.sourceActionId = Action.id',
                                                                                                                  tableActionType['flatCode'].like('moving%')
                                                                                                                  ] +  reanimationCond),
                                                                                                      ),
                                               db.joinAnd(cond)
                                               )
#        queryTable = queryTable.leftJoin(db.table(reanimationInfoTableStmt).alias('ReanimationInfoTable'), db.joinAnd([u'ReanimationInfoTable.eventId = Event.id',
#                                                                                                                  u'ReanimationInfoTable.sourceActionId = Action.id',
#                                                                                                                  tableActionType['flatCode'].like('moving%')
#                                                                                                                  ] +  reanimationCond))
#        stmt = db.selectStmt(queryTable, cols, cond)
        query = db.query(stmt)
        countAll = 0
        processedActionsIdList = []
        countPatronage = 0
        reanimationProfileIdList = []
        while query.next():
            record = query.record()
            actionId = forceRef(record.value('actionId'))
            isOrdinaryMoving = forceBool(record.value('isOrdinaryMoving'))
            isPatronage = forceBool(record.value('isPatronage'))
            reanimationActionId = forceRef(record.value('reanimationActionId'))
            reanimationProfileId = forceRef(record.value('reanimationProfileId'))
            reanimationOrgStructureId = forceRef(record.value('reanimationOrgStructureId'))
            if actionId not in processedActionsIdList and isOrdinaryMoving:
                #Посчитать само движение
                countAll += 1
                processedActionsIdList.append(actionId)
                #Посчитать "Уход", если из движения не было перевода в реанимацию
                countPatronage += 1 if isPatronage and not reanimationActionId else 0
            
            if reanimationActionId:
                #Перевод в Реанимацию, относящиеся к текущему действию "Движение"
                if reanimationActionId not in processedActionsIdList:
                    countAll += 1
                    processedActionsIdList.append(reanimationActionId)
                if reanimationProfileId and reanimationProfileId not in reanimationProfileIdList:
                    reanimationProfileIdList.append(reanimationProfileId)
                if reanimationOrgStructureId and reanimationOrgStructureId not in reanimationOSIdList:
                    reanimationOSIdList.append(reanimationOrgStructureId)
        
        return [countAll, countPatronage, reanimationProfileIdList]


def getReceived(bedsSchedule, begDateTime, endDateTime, nameProperty=u'Переведен из отделения', profile=None,
                orgStructureIdList=None, boolFIO=False, simplifyDateCond=False, socStatusTypeId=None,
                socStatusClassId=None, countOrder=False):
    if not orgStructureIdList:
        orgStructureIdList = []
    db = QtGui.qApp.db
    tableAPT = db.table('ActionPropertyType')
    tableAP = db.table('ActionProperty')
    tableActionType = db.table('ActionType')
    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    
    tableOS = db.table('OrgStructure')
    tableAPHB = db.table('ActionProperty_HospitalBed')
    tableOSHB = db.table('OrgStructure_HospitalBed')
    tableHBSchedule = db.table('rbHospitalBedShedule')
    cond = [ tableAction['deleted'].eq(0),
             tableEvent['deleted'].eq(0),
             tableAP['deleted'].eq(0),
             tableAPT['deleted'].eq(0),
             tableOS['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableAP['action_id'].eq(tableAction['id'])
           ]
    queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
    queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
    queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
    queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
    cond.append(tableAPT['typeName'].like('HospitalBed'))
    cond.append(tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%'))) 
    cond.append('NOT %s' % (getTransferPropertyInPeriod(u'Переведен из отделения%', begDateTime, endDateTime)))
    if orgStructureIdList:
        cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
    if profile:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            cond.append(getPropertyAPHBP(profile))
        else:
            cond.append(tableOSHB['profile_id'].inlist(profile))
    if bedsSchedule:
        queryTable = queryTable.innerJoin(tableHBSchedule, tableOSHB['schedule_id'].eq(tableHBSchedule['id']))
    if bedsSchedule == 1:
        cond.append(tableHBSchedule['code'].eq(1))
    elif bedsSchedule == 2:
        cond.append(tableHBSchedule['code'].ne(1))

    if simplifyDateCond:
        cond.append(db.joinAnd([tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)]))
    else:
        cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].between(begDateTime, endDateTime)]))
        cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(begDateTime)]))
    
    reanimationCond = [u'reanimationAction.begDate >= \'%s\''  % begDateTime.toString(Qt.ISODate),
                       u'reanimationAction.begDate >= Action.begDate',
                       u'reanimationAction.begDate <= Action.endDate OR Action.endDate IS NULL',
                       u'reanimationAction.event_id = Action.event_id',
                       u'SourceAP.action_id = Action.id']

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
    
    if boolFIO:
        tableHBProfile = db.table('rbHospitalBedProfile')
        queryTable = queryTable.leftJoin(tableHBProfile, tableHBProfile['id'].eq(tableOSHB['profile_id']))

        stmt = db.selectStmt(queryTable,
                             [tableAction['id'].alias('actionId'),
                              u'(1) AS isOrdinaryMoving',
                              tableEvent['externalId'],
                              tableClient['lastName'],
                              tableClient['firstName'],
                              tableClient['patrName'],
                              u'NULL AS reanimationActionId',
                              tableOS['code'].alias('orgStructureName'),
                              tableHBProfile['name'].alias('profileName'),
                              u'(%s AND NOT (EXISTS(%s))) AS nursing' % (getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')'),
                                                                         getReanimationInfoTableStmt(u'Переведен из отделения%') + ' AND ' + db.joinAnd(reanimationCond)),
                              ], 
                             cond, 
                             isDistinct = True)
        return db.query(stmt)
    else:
        ageStmtChildren = u'''age(Client.birthDate, Action.begDate) <= 17'''
        ageStmtAdult = u'''age(Client.birthDate, Action.begDate) >= 60'''
        isStationaryDay = u'''EXISTS(SELECT A.id
    FROM Action AS A
    INNER JOIN ActionPropertyType AS APT ON (APT.actionType_id = A.actionType_id AND APT.name LIKE 'Поступил из' AND APT.deleted=0)
    INNER JOIN ActionProperty AS AP ON (AP.type_id = APT.id AND AP.action_id = A.id)
    INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
    WHERE  A.event_id = Action.event_id AND APS.value LIKE 'ДС')'''

        cols = u'''
        COUNT(Client.id) AS countAll,
        SUM(%s) AS childrenCount,
        SUM(%s) AS adultCount,
        SUM(%s) AS clientRural,
        COUNT(IF(%s, 1, NULL)) AS isStationaryDay,
        SUM(%s AND NOT (EXISTS(%s))) AS countPatronage
        ''' % (
            ageStmtChildren,
            ageStmtAdult,
            getKladrClientRural(),
            isStationaryDay,
            getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')'),
            getReanimationInfoTableStmt(u'Переведен из отделения%') + ' AND ' + db.joinAnd(reanimationCond)
        )
        if countOrder:
            countTemplate = u'''
            COALESCE((SELECT APS.value
            FROM Action AS A
            INNER JOIN ActionPropertyType AS APT ON (APT.actionType_id = A.actionType_id AND APT.name IN ('Госпитализирован') AND APT.deleted=0)
            INNER JOIN ActionProperty AS AP ON (AP.type_id = APT.id AND AP.action_id = A.id)
            INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
            WHERE  A.event_id = Action.event_id),
            Event.`order`) RLIKE '%s'
            '''
            countScheduled = countTemplate % u'1|планов'
            countEmergency = countTemplate % u'2|экстренн'
            cols += u''',
            SUM(IF(%s, 1, 0)) AS countScheduled,
            SUM(IF(%s, 1, 0)) AS countEmergency
            ''' % (countScheduled, countEmergency)

        stmt = db.selectStmt(queryTable,
                             cols,
                             where=cond)
        query = db.query(stmt)
        if query.first():
            record = query.record()
            result = [forceInt(record.value('countAll')), forceInt(record.value('childrenCount')), forceInt(record.value('adultCount')), forceInt(record.value('clientRural')), forceInt(record.value('isStationaryDay')), forceInt(record.value('countPatronage'))]
            if countOrder:
                result.extend([forceInt(record.value('countScheduled')), forceInt(record.value('countEmergency'))])
        else:
            result = [0] * (8 if countOrder else 6)
        return result

def getLeaved(bedsSchedule, begDateTime, endDateTime, profileIdList=None, orgStructureIdList=None, boolFIO=False,
              simplifyDateCond=False, socStatusTypeId=None, socStatusClassId=None):
    if not orgStructureIdList:
        orgStructureIdList = []
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableHBSchedule = db.table('rbHospitalBedShedule')
    
    tableLastMovingAction = tableAction.alias('LastMovingAction')
    tableLastMovingAPT = db.table('ActionPropertyType').alias('LastMovingAPT')
    tableLastMovingAP = db.table('ActionProperty').alias('LastMovingAP')
    tableLastMovingAPHB = db.table('ActionProperty_HospitalBed').alias('LastMovingAPHB')
    tableLastMovingOSHB = db.table('OrgStructure_HospitalBed').alias('LastMovingOSHB')
    tableLastMovingOS = db.table('OrgStructure')
    
    cond = [ tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('leaved%')),
             tableAction['deleted'].eq(0),
             tableEvent['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableAction['endDate'].isNotNull()
           ]
    queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
    
    queryTable = queryTable.innerJoin(tableLastMovingAction, [tableLastMovingAction['event_id'].eq(tableEvent['id']),
                                                              tableLastMovingAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('moving%')),
                                                              tableLastMovingAction['deleted'].eq(0),
                                                              'NOT %s' % getTransferProperty(u'Переведен в отделение%', tableLastMovingAction.aliasName),
                                                              tableLastMovingAction['status'].eq(2),
                                                              tableLastMovingAction['endDate'].isNotNull()])
    queryTable = queryTable.innerJoin(tableLastMovingAPT, [tableLastMovingAPT['typeName'].eq('HospitalBed'),
                                                           tableLastMovingAPT['actionType_id'].eq(tableLastMovingAction['actionType_id']),
                                                           tableLastMovingAPT['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableLastMovingAP, [tableLastMovingAP['type_id'].eq(tableLastMovingAPT['id']),
                                                          tableLastMovingAP['deleted'].eq(0),
                                                          tableLastMovingAP['action_id'].eq(tableLastMovingAction['id'])])
    queryTable = queryTable.innerJoin(tableLastMovingAPHB, [tableLastMovingAPHB['id'].eq(tableLastMovingAP['id'])])
    queryTable = queryTable.innerJoin(tableLastMovingOSHB, [tableLastMovingOSHB['id'].eq(tableLastMovingAPHB['value'])])
    queryTable = queryTable.innerJoin(tableLastMovingOS, [tableLastMovingOS['id'].eq(tableLastMovingOSHB['master_id']),
                                                          tableLastMovingOS['deleted'].eq(0)])

    if simplifyDateCond:
        cond.append(db.joinAnd([tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)]))
    else:
        # Условие JoinOr1 никогда не будет выполнено, так как в инициализации cond есть tableAction['endDate'].isNotNull()
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].ge(begDateTime), tableAction['begDate'].lt(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDateTime)])
        joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].le(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].gt(begDateTime)])])
        cond.append(db.joinOr([joinOr1, joinOr2, joinOr3, joinOr4]))

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

    if profileIdList:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            cond.append(getPropertyAPHBP(profileIdList, tableLastMovingAction.aliasName))
        else:
            cond.append(tableLastMovingOSHB['profile_id'].inlist(profileIdList))
    
    if bedsSchedule:
        queryTable = queryTable.innerJoin(tableHBSchedule, tableLastMovingOSHB['schedule_id'].eq(tableHBSchedule['id']))
    if bedsSchedule == 1:
        cond.append(tableHBSchedule['code'].eq(1))
    elif bedsSchedule == 2:
        cond.append(tableHBSchedule['code'].ne(1))
        
    if orgStructureIdList:
        cond.append(tableLastMovingOSHB['master_id'].inlist(orgStructureIdList))
    
    deathCond = [getStringProperty(u'Исход госпитализации', u'(APS.value LIKE \'умер%\' OR APS.value LIKE \'смерть%\' OR APS.value = \'death\')')]
    transferCond = [getStringProperty(u'Исход госпитализации', u'(APS.value LIKE \'переведен в другой стационар\')')]
    transferNoctidialStatCond = [getStringProperty(u'Исход госпитализации', u'(APS.value LIKE \'выписан в круглосуточный стационар\')')]
    transferDayStatCond = [getStringProperty(u'Исход госпитализации', u'(APS.value LIKE \'выписан в дневной стационар\')')]
    patronageCond = getStringProperty([u'Патронаж%', u'Уход%'], u'(APS.value LIKE \'Да\')')
        
    
    #cond.append(getDataAPHBnoProperty(nameProperty, profile, u' AND A.endDate IS NOT NULL', u'Отделение пребывания', orgStructureIdList, None, bedsSchedule))
    
    if boolFIO:
        tableHBProfile = db.table('rbHospitalBedProfile')
        queryTable = queryTable.leftJoin(tableHBProfile, tableHBProfile['id'].eq(tableLastMovingOSHB['profile_id']))
            
        cols = [tableAction['id'].alias('actionId'),
                              u'(1) AS isOrdinaryMoving',
                              tableEvent['externalId'],
                              tableClient['lastName'],
                              tableClient['firstName'],
                              tableClient['patrName'],
                              u'NULL AS reanimationActionId',
                              tableLastMovingOS['code'].alias('orgStructureName'),
                              tableHBProfile['name'].alias('profileName'),
                              u'(%s) AS nursing' % patronageCond,
                              ]
        
        stmt = db.selectStmt(queryTable, cols, cond, isDistinct = True)
        leavedAll = db.query(stmt)
        
        stmt = db.selectStmt(queryTable,cols, cond + deathCond, isDistinct = True)
        leavedDeath = db.query(stmt)

        stmt = db.selectStmt(queryTable, cols, cond + transferCond, isDistinct = True)
        leavedTransfer = db.query(stmt)
        return [leavedAll, leavedDeath, leavedTransfer]
    else:
        elderCond = u'age(Client.birthDate, Action.begDate) >= 60'
        stmt = db.selectStmt(queryTable, 
                             u'COUNT(Client.id) AS countAll, SUM(%s) AS countDeath, SUM(%s) AS countTransfer, SUM(%s) AS countAllPatronage, SUM(%s) AS countDeathPatronag, SUM(%s) AS countTransferPatronag, SUM(%s) AS countLeavedElder, SUM(%s) AS countDeadElder, SUM(%s) AS leavedDayStat, SUM(%s) AS leavedNoctidialStat'
                                % (db.joinAnd(deathCond), 
                                   db.joinAnd(transferCond),
                                   patronageCond,
                                   '%s AND %s' % (db.joinAnd(deathCond), patronageCond),
                                   '%s AND %s' % (db.joinAnd(transferCond), patronageCond),
                                   elderCond,
                                   db.joinAnd(deathCond + [elderCond]),
                                   db.joinAnd(transferDayStatCond),
                                   db.joinAnd(transferNoctidialStatCond)
                                   ),
                             where=cond)
        query = db.query(stmt)
        if query.first():
            record = query.record()
            return [forceInt(record.value('countAll')), forceInt(record.value('countDeath')), forceInt(record.value('countTransfer')), forceInt(record.value('countAllPatronage')), forceInt(record.value('countDeathPatronag')), forceInt(record.value('countTransferPatronag')), forceInt(record.value('countLeavedElder')), forceInt(record.value('countDeadElder')), forceInt(record.value('leavedDayStat')), forceInt(record.value('leavedNoctidialStat'))]
        else:
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def getDataAPHBnoProperty(nameProperty, profileList=None, endDate=u'', namePropertyStay=u'Отделение пребывания',
                          orgStructureIdList=None, isMedical=None, bedsSchedule=None):
    if not profileList:
        profileList = []
    if not orgStructureIdList:
        orgStructureIdList = []
    strIsMedical = u''
    strIsMedicalJoin = u''
    strIsScheduleJoin = u''
    if isMedical is not None:
        strIsMedicalJoin += u''' INNER JOIN OrgStructure AS OS ON OSHB.master_id = OS.id INNER JOIN Organisation AS ORG ON OS.organisation_id = ORG.id'''
        strIsMedical += u''' AND ORG.isMedical = %d'''%(isMedical)
    strFilter = u''
    if profileList:
        if QtGui.qApp.defaultHospitalBedProfileByMoving():
            strFilter += u''' AND (''' + getPropertyAPHBP(profileList) + u''')'''
        else:
            strFilter += u''' AND OSHB.profile_id IN (%s)'''%(','.join(forceString(profile) for profile in profileList))
    if bedsSchedule:
        strIsScheduleJoin += u''' INNER JOIN rbHospitalBedShedule AS HBS ON OSHB.schedule_id = HBS.id'''
    if bedsSchedule == 1:
        strFilter += u''' AND HBS.code = 1'''
    elif bedsSchedule == 2:
        strFilter += u''' AND HBS.code != 1'''

    return u'''EXISTS(SELECT APHB.value
                    FROM ActionType AS AT
                    INNER JOIN Action AS A ON AT.id=A.actionType_id
                    INNER JOIN ActionPropertyType AS APT ON APT.actionType_id=AT.id
                    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
                    INNER JOIN ActionProperty_HospitalBed AS APHB ON APHB.id=AP.id
                    INNER JOIN OrgStructure_HospitalBed AS OSHB ON OSHB.id=APHB.value
                    %s
                    %s
                    WHERE A.event_id=Event.id
                            %s
                            %s 
                            AND A.deleted=0 
                            AND APT.actionType_id=A.actionType_id 
                            AND AP.action_id=A.id 
                            AND AP.deleted=0 
                            AND APT.deleted=0 
                            AND APT.typeName LIKE 'HospitalBed'
                            %s 
                            AND (NOT %s)%s)''' % (strIsMedicalJoin, 
                                                  strIsScheduleJoin, 
                                                  strIsMedical, 
                                                  endDate, 
                                                  strFilter, 
                                                  getTransferProperty(nameProperty), 
                                                  u' AND %s' % getDataOrgStructureStay(namePropertyStay, orgStructureIdList) if orgStructureIdList else u'')


def getPropertyAPHBP(profileList, ownTableName = 'Action'):
    return u'''EXISTS(SELECT APHBP.value
FROM ActionPropertyType AS APT_Profile
INNER JOIN ActionProperty AS AP_Profile ON AP_Profile.type_id=APT_Profile.id
INNER JOIN ActionProperty_rbHospitalBedProfile AS APHBP ON APHBP.id=AP_Profile.id
INNER JOIN rbHospitalBedProfile AS RBHBP ON RBHBP.id=APHBP.value
WHERE APT_Profile.actionType_id = %s.actionType_id
AND AP_Profile.action_id = Action.id
AND AP_Profile.deleted = 0
AND APT_Profile.deleted = 0
AND APT_Profile.typeName LIKE 'rbHospitalBedProfile'
AND APHBP.value IN (%s))'''%(ownTableName, 
                             ','.join(forceString(profile) for profile in profileList))


## Возвращает запрос на проверку существования у действия заполненого свойства перевода
#    @param nameProperty: имя свойства перевода ("Переведен из отделения%" или "Переведен в отделение%")
#    @param ownActionTableName: имя таблицы проверяемого действия в базовом запросе
def getTransferProperty(nameProperty, ownActionTableName = u'A'):
    return u'''EXISTS(SELECT APOS2.value
    FROM ActionPropertyType AS APT2
    INNER JOIN ActionProperty AS AP2 ON AP2.type_id=APT2.id
    INNER JOIN ActionProperty_OrgStructure AS APOS2 ON APOS2.id=AP2.id
    INNER JOIN OrgStructure AS OS2 ON OS2.id=APOS2.value
    WHERE APT2.actionType_id=%(ownActionTable)s.actionType_id AND AP2.action_id=%(ownActionTable)s.id AND APT2.deleted=0 AND APT2.name LIKE '%(nameProperty)s' AND OS2.deleted=0)''' % {'ownActionTable' : ownActionTableName, 'nameProperty' : nameProperty}


def getStringProperty(namePropertyList, value):
    if not isinstance(namePropertyList, list):
        namePropertyList = [namePropertyList]
    namePropertyCond = ' OR '.join( ["APT.name LIKE '%s'" % nameProperty for nameProperty in namePropertyList] )
    return u'''EXISTS(SELECT APS.id
    FROM ActionPropertyType AS APT
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
    INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
    WHERE  Action.id IS NOT NULL AND APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND (%s) AND %s)'''%(namePropertyCond, value)


def getDataOrgStructureStay(nameProperty, orgStructureIdList):
    orgStructureList = [u'NULL']
    for orgStructureId in orgStructureIdList:
        orgStructureList.append(forceString(orgStructureId))
    return u'''EXISTS(SELECT APOS2.value
    FROM ActionPropertyType AS APT2
    INNER JOIN ActionProperty AS AP2 ON AP2.type_id=APT2.id
    INNER JOIN ActionProperty_OrgStructure AS APOS2 ON APOS2.id=AP2.id
    INNER JOIN OrgStructure AS OS2 ON OS2.id=APOS2.value
    WHERE APT2.actionType_id=A.actionType_id AND AP2.action_id=A.id AND APT2.deleted=0 AND APT2.name LIKE '%s' AND OS2.deleted=0 AND APOS2.value %s)'''%(nameProperty, u' IN ('+(','.join(orgStructureList))+')')


def getKladrClientRural():
    return u'''EXISTS(SELECT kladr.KLADR.OCATD
    FROM ClientAddress
    INNER JOIN Address ON ClientAddress.address_id = Address.id
    INNER JOIN AddressHouse ON Address.house_id = AddressHouse.id
    INNER JOIN kladr.KLADR ON kladr.KLADR.CODE = AddressHouse.KLADRCode
    WHERE Client.id IS NOT NULL AND ClientAddress.client_id = Client.id AND (((SUBSTRING(kladr.KLADR.OCATD,3,1) IN (1, 2, 4)) AND SUBSTRING(kladr.KLADR.OCATD,6,1) = 8) OR ((SUBSTRING(kladr.KLADR.OCATD,3,1) NOT IN (1, 2, 4))
    AND SUBSTRING(kladr.KLADR.OCATD,6,1) = 9)))'''


def getTransferPropertyInPeriod(nameProperty, begDateTime, endDateTime):
    return u'''EXISTS(SELECT APOS.value
    FROM ActionPropertyType AS APT
    INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
    INNER JOIN ActionProperty_OrgStructure AS APOS ON APOS.id=AP.id
    INNER JOIN OrgStructure AS OS ON OS.id=APOS.value
    WHERE APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND APT.name LIKE '%s' AND OS.deleted=0 AND (Action.begDate IS NULL OR (Action.begDate >= '%s' AND Action.begDate < '%s')))'''%(nameProperty, begDateTime.toString(Qt.ISODate), endDateTime.toString(Qt.ISODate))
