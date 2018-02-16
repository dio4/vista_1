# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from HospitalBeds.HospitalBedsDialog import getActionTypeIdListByFlatCode
from HospitalBeds.Utils import getTransferPropertyIn
from library.Utils                   import forceDate, forceInt, forceRef, forceString, getVal
from Reports.Report                  import CReport
from Reports.ReportBase              import createTable, CReportBase
from Reports.ReportView              import CPageFormat
from Reports.StationaryF007          import getLeaved, getMovingTransfer, \
                                            getPropertyAPHBP, getReanimationInfoTableStmt, getReceived, \
                                            getStringProperty

from Ui_StationaryF016Setup import Ui_StationaryF016SetupDialog


class CStationaryF016SetupDialog(QtGui.QDialog, Ui_StationaryF016SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbProfilBed.setTable('rbHospitalBedProfile', addNone=True, order='code')
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtYear.setText(params.get('Year', ''))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbProfilBed.setValue(getVal(params, 'profilBedId', None))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))


    def params(self):
        result = {}
        result['Year'] = forceString(self.edtYear.text())
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['profilBedId'] = self.cmbProfilBed.value()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        return result


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id=%d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)


class CStationaryF016(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'СВОДНАЯ ВЕДОМОСТЬ учета движения больных и коечного фонда по стационару, отделению или профилю коек')
        self.stationaryF016SetupDialog = None
        self.clientDeath = 8


    def getSetupDialog(self, parent):
        result = CStationaryF016SetupDialog(parent)
        result.setTitle(self.title())
        self.stationaryF016SetupDialog = result
        return result


    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []


    def getPageFormat(self):
        return CPageFormat(pageSize=CPageFormat.A4, orientation=CPageFormat.Landscape, leftMargin=10.0, topMargin=10.0, rightMargin=10.0, bottomMargin=10.0)



    def createHeader(self, cursor, params):
        db = QtGui.qApp.db

        year = params.get('Year', u'____')

        orgId = QtGui.qApp.currentOrgId()
        orgName = forceString(db.translate('Organisation', 'id', orgId, 'fullName')) if orgId else u'_' * 50 + u'\n\n' + u'наименование учреждения'

        orgStructureId = params.get('orgStructureId', None)
        orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name')) if orgStructureId else u'_' * 30

        profilBedId = params.get('profilBedId', None)
        profilBedName = forceString(db.translate('rbHospitalBedProfile', 'id', profilBedId, 'name')) if profilBedId else u'_'  * 30

        headerCharFormat = QtGui.QTextCharFormat()
        headerCharFormat.setFontPointSize(5)

        headerLeft = u'Министерство здравоохранения\n' + \
                     u'Российской Федерации\n\n' + \
                     orgName
        headerRight = u'Медицинская документация\n' \
                      u'Форма N 016/у-02\n' \
                      u'Утверждена приказом Минздрава России\n' \
                      u'от 30.12.2002 N 413'
        headerColumns = [
            ('35%', [''], CReportBase.AlignCenter),
            ('30%', [''], CReportBase.AlignCenter),
            ('35%', [''], CReportBase.AlignLeft),
        ]
        headerTable = createTable(cursor, headerColumns, border=0, cellPadding=0, cellSpacing=0, charFormat=headerCharFormat)
        headerTable.setText(0, 0, headerLeft)
        headerTable.setText(0, 2, headerRight)
        cursor.movePosition(QtGui.QTextCursor.End)

        titleCharFormat = QtGui.QTextCharFormat()
        titleCharFormat.setFontWeight(QtGui.QFont.Bold)
        titleCharFormat.setFontPointSize(7)

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(titleCharFormat)
        cursor.insertText(u'СВОДНАЯ ВЕДОМОСТЬ\n'
                          u'ДВИЖЕНИЯ БОЛЬНЫХ И КОЕЧНОГО ФОНДА ПО СТАЦИОНАРУ,\n' + \
                          u'ОТДЕЛЕНИЮ ИЛИ ПРОФИЛЮ КОЕК СТАЦИОНАРА КРУГЛОСУТОЧНОГО\n' + \
                          u'ПРЕБЫВАНИЯ, ДНЕВНОГО СТАЦИОНАРА ПРИ БОЛЬНИЧНОМ\n' + \
                          u'УЧРЕЖДЕНИИ (нужное подчеркнуть)\n' + \
                          u'%s наименование отделения, профиля коек %s\n' % (orgStructureName, profilBedName) + \
                          u'за %s год' % year)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()


    # def dumpParams(self, cursor, params):
    #     description = []
    #     orgStructureId = params.get('orgStructureId', None)
    #     profilBedId = params.get('profilBedId', None)
    #     if orgStructureId:
    #         description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
    #     else:
    #         description.append(u'подразделение: ЛПУ')
    #     if profilBedId:
    #         description.append(u'профиль койки: ' + forceString(QtGui.qApp.db.translate('rbHospitalBedProfile', 'id', profilBedId, 'name')))
    #     description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
    #     columns = [ ('100%', [], CReportBase.AlignLeft) ]
    #     table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
    #     for i, row in enumerate(description):
    #         table.setText(i, 0, row)
    #     cursor.movePosition(QtGui.QTextCursor.End)
    #     cursor.insertBlock()


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
        tableHB_I = db.table('HospitalBed_Involute')

        profile = getVal(params, 'profilBedId', '')
        yearDate = getVal(params, 'Year', '')
        yearDateInt = forceInt(yearDate)
        orgStructureIndex = self.stationaryF016SetupDialog.cmbOrgStructure._model.index(self.stationaryF016SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF016SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)

        # подразделения, соответствующие действиям "реанимация" (связанным с выбранными подразделениями) и найденные в процессе формирования отчета по плановым
        reanimationOSIdList = []

        fontSizeHeader = 8
        fontSizeBody = 6
        charFormatHeader = CReportBase.TableHeader
        # charFormatHeader.setFontPointSize(fontSizeHeader)
        self.charFormatBody = QtGui.QTextCharFormat()
        self.charFormatBody.setFontPointSize(fontSizeBody)
        self.charFormatBodyBold = QtGui.QTextCharFormat()
        self.charFormatBodyBold.setFontWeight(QtGui.QFont.Bold)
        self.charFormatBodyBold.setFontPointSize(fontSizeBody)

        # Формирование отчета (формат)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        self.createHeader(cursor, params)

        # cursor.setCharFormat(CReportBase.ReportTitle)
        # cursor.insertText(u'СВОДНАЯ ВЕДОМОСТЬ учета движения больных и коечного фонда по стационару, отделению или профилю коек за %s год' % (yearDate))
        # cursor.insertBlock()
        # self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('20?',[u'', u'', u'', u'', u'1'], CReportBase.AlignLeft),
                ('4%',[u'Число коек в пределах сметы', u'Всего фактически развернутых', u'', u'', u'2'], CReportBase.AlignRight),
                ('4%',[u'', u'в т.ч. свернутых на ремонт', u'', u'', u'3'], CReportBase.AlignRight),
                ('4%',[u'Среднемесячных коек', u'', u'', u'', u'4'], CReportBase.AlignRight),
                ('4%',[u'Состояло больных на начало отчетного периода', u'', u'', u'', u'5'], CReportBase.AlignRight),
                ('4%',[u'За отчетный период', u'Поступило больных', u'Всего', u'', u'6'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'в т.ч. из дневных стационаров', u'', u'7'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'из них (из гр. 6)', u'сельских жителей', u'8'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'', u'0-17 лет', u'9'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'', u'60 лет и старше', u'10'], CReportBase.AlignRight),
                ('4%',[u'', u'Переведено больных внутри больницы', u'', u'из других отделений', u'11'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'', u'в другие отделения', u'12'], CReportBase.AlignRight),
                ('4%',[u'', u'Выписано больных', u'всего', u'', u'13'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'в т. ч.', u'в дневной стационар', u'14'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'', u'в круглосуточный стационар', u'15'], CReportBase.AlignRight),
                ('4%',[u'', u'', u'', u'переведено в другие стационары', u'16'], CReportBase.AlignRight),
                ('4%',[u'', u'Умерло', u'', u'', u'17'], CReportBase.AlignRight),
                ('4%',[u'Состояло больных на конец отчетного периода', u'', u'', u'', u'18'], CReportBase.AlignRight),
                ('4%',[u'Проведено больными к/дн в круглосут. стационаре (дней леч. в дн. стац.)', u'', u'', u'', u'19'], CReportBase.AlignRight),
                ('4%',[u'Кроме того:', u'число койко-дней закрытия', u'', u'', u'20'], CReportBase.AlignRight),
                ('4%',[u'', u'проведено койко-дней по уходу', u'', u'', u'21'], CReportBase.AlignRight),
        ]

        table = createTable(cursor, cols, charFormat=self.charFormatBodyBold, cellPadding=1)
        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 1, 2)
        table.mergeCells(1, 1, 3, 1)
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(0, 3, 4, 1)
        table.mergeCells(0, 4, 4, 1)
        table.mergeCells(0, 5, 1, 12)
        table.mergeCells(1, 5, 1, 5)
        table.mergeCells(2, 5, 2, 1)
        table.mergeCells(2, 6, 2, 1)
        table.mergeCells(2, 7, 1, 3)
        table.mergeCells(1, 10, 2, 2)
        table.mergeCells(1, 12, 1, 4)
        table.mergeCells(2, 12, 2, 1)
        table.mergeCells(2, 13, 1, 3)
        table.mergeCells(1, 16, 3, 1)
        table.mergeCells(0, 17, 4, 1)
        table.mergeCells(0, 18, 4, 1)
        table.mergeCells(0, 19, 1, 2)
        table.mergeCells(1, 19, 3, 1)
        table.mergeCells(1, 20, 3, 1)

        for period in (u'Январь', u'Февраль', u'Март', u'Апрель', u'Май', u'Июнь', u'За полугодие',
                       u'Июль', u'Август', u'Сентябрь', u'Октябрь', u'Ноябрь', u'Декабрь', u'За год'):
            i = table.addRow()
            table.setText(i, 0, period, charFormat=self.charFormatBodyBold)

        def unrolledHospitalBed(begDate, endDate, profile = None):
            countBeds = 0
            cond = []
            condRepairs = [tableHB_I['involuteType'].ne(0)]
            cond.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
            condRepairs.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
            if profile:
                cond.append(tableVHospitalBed['profile_id'].eq(profile))
                condRepairs.append(tableVHospitalBed['profile_id'].eq(profile))
            joinOr1 = db.joinOr([tableVHospitalBed['begDate'].isNull(), tableVHospitalBed['begDate'].le(endDate)])
            joinOr2 = db.joinOr([tableVHospitalBed['endDate'].isNull(), tableVHospitalBed['endDate'].ge(endDate)])
            cond.append(db.joinAnd([joinOr1, joinOr2]))
            condRepairs.append(db.joinOr([db.joinAnd([tableHB_I['endDateInvolute'].isNull(),
                                                              tableHB_I['begDateInvolute'].isNull()]),
                                                  db.joinAnd([tableHB_I['begDateInvolute'].isNotNull(),
                                                              tableHB_I['begDateInvolute'].ge(begDate),
                                                              tableHB_I['begDateInvolute'].lt(endDate)]),
                                                  db.joinAnd([tableHB_I['endDateInvolute'].isNotNull(),
                                                              tableHB_I['endDateInvolute'].gt(begDate),
                                                              tableHB_I['endDateInvolute'].le(endDate)])
                                                  ]))

            countBeds = db.getCount(tableVHospitalBed, countCol='id', where=cond)

            involuteTable = tableVHospitalBed.innerJoin(tableHB_I, tableHB_I['master_id'].eq(tableVHospitalBed['id']))
            countRepairBeds = db.getCount(involuteTable, countCol='vHospitalBed.id', where=condRepairs)
            return countBeds, countRepairBeds

        def unrolledHospitalBedsMonth(row, monthEnd, profile = None, fromYearBeginning = False):
            monthEndDate = QtCore.QDate(yearDateInt, monthEnd, 1)
            endDate = QtCore.QDate(yearDateInt, monthEnd, monthEndDate.daysInMonth())

            begDate = QtCore.QDate(yearDateInt, 1, 1) if fromYearBeginning else monthEndDate
            countBedsMonth, countRepairBedsMonth = unrolledHospitalBed(begDate, endDate, profile)
            table.setText(row, 1, countBedsMonth, charFormat=self.charFormatBody)
            table.setText(row, 2, countRepairBedsMonth, charFormat=self.charFormatBody)
            return countBedsMonth

        def getMovingPresent(begDate, endDateTime, orgStructureIdList, profile = None, atBegin = True, isReanimation = False):
            begDateTime = QtCore.QDateTime(begDate, QtCore.QTime(9, 0))
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
                    cond.append(tableOSHB['profile_id'].eq(profile))

            compareDate = begDateTime if atBegin else endDateTime
            cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].lt(compareDate)]))
            cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(compareDate)]))

            reanimationCond = [# Реанимация должна быть незавершенной на дату проверки (т.е. не иметь дату окончания или дата окончания должна быть после этой даты)
                               u'reanimationAction.endDate IS NULL OR reanimationAction.endDate >= \'%s\'' % compareDate.toString(QtCore.Qt.ISODate),
                               # Реанимация должна начинаться в период действия текущего Движения
                               u'reanimationAction.begDate >= Action.begDate',
                               # Реанимация должна начинаться в период действия текущего Движения
                               u'reanimationAction.begDate <= Action.endDate OR Action.endDate IS NULL',
                               u'reanimationAction.event_id = Action.event_id',
                               u'SourceAP.action_id = Action.id']
            reanimationExistsStmt = 'EXISTS(%s)' % getReanimationInfoTableStmt(u'Переведен из отделения%', reanimationCond) if not isReanimation else '0'
            cols = ['COUNT(IF(%s AND ActionType.flatCode LIKE \'moving%%\', NULL, 1)) AS countAll' % reanimationExistsStmt,
                    'SUM(%s) as countElder' % elderCond
                    ]
            stmt = db.selectStmt(queryTable,
                                 cols,
                                 where=cond)
            query = db.query(stmt)
            if query.first():
                record = query.record()
                return forceInt(record.value('countAll'))
            else:
                return 0

        self.movingsPresentBeg = 0
        self.movingsPresentEnd = 0
        def columnFill(begDate, endDate, orgStructureIdList, profile, row):
            self.averageYarHospitalBed(orgStructureIdList, table, begDate, endDate, profile, row)
            movingPresentBeg = getMovingPresent(begDate, endDate, orgStructureIdList, profile)
            self.movingsPresentBeg += movingPresentBeg
            table.setText(row, 4, movingPresentBeg, charFormat=self.charFormatBody)
            all, children, adultCount, clientRural, isStationaryDay, countPatronage = getReceived(None, begDate, endDate, u'Переведен из отделения', profile, orgStructureIdList, simplifyDateCond=True, socStatusTypeId=socStatusTypeId, socStatusClassId=socStatusClassId)
            table.setText(row, 5, all, charFormat=self.charFormatBody)
            table.setText(row, 6, isStationaryDay, charFormat=self.charFormatBody)
            table.setText(row, 7, clientRural, charFormat=self.charFormatBody)
            table.setText(row, 8, children, charFormat=self.charFormatBody)
            table.setText(row, 9, adultCount, charFormat=self.charFormatBody)
            table.setText(row, 10, getMovingTransfer(None, begDate, endDate, u'Переведен из отделения', profile, orgStructureIdList = orgStructureIdList, socStatusTypeId = socStatusTypeId, socStatusClassId = socStatusClassId)[0], charFormat=self.charFormatBody)
            table.setText(row, 11, getMovingTransfer(None, begDate, endDate, u'Переведен в отделение', profile, True, orgStructureIdList = orgStructureIdList, socStatusTypeId = socStatusTypeId, socStatusClassId = socStatusClassId)[0], charFormat=self.charFormatBody)
            countLeavedAll, leavedDeath, leavedTransfer, leavedAllPatronag, leavedDeathPatronag, leavedTransferPatronag, leavedElder, deadElder, leavedDayStat, leavedNoctidialStat = getLeaved(None,
                                                                                                                                        begDate,
                                                                                                                                        endDate,
                                                                                                                                        profile,
                                                                                                                                        orgStructureIdList,
                                                                                                                                        simplifyDateCond = True,
                                                                                                                                        socStatusTypeId = socStatusTypeId,
                                                                                                                                        socStatusClassId = socStatusClassId)
            table.setText(row, 12, countLeavedAll, charFormat=self.charFormatBody)
            # table.setText(row, 14, leavedElder)
            table.setText(row, 13, leavedDayStat, charFormat=self.charFormatBody)
            table.setText(row, 14, leavedNoctidialStat, charFormat=self.charFormatBody)
            table.setText(row, 15, leavedTransfer, charFormat=self.charFormatBody)
            table.setText(row, 16, leavedDeath, charFormat=self.charFormatBody)
            # table.setText(row, 19, deadElder)
            movingPresentEnd = getMovingPresent(begDate, endDate, orgStructureIdList, profile, False)
            self.movingsPresentEnd += movingPresentEnd
            table.setText(row, 17, movingPresentEnd, charFormat=self.charFormatBody)
            table.setText(row, 18, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile), charFormat=self.charFormatBody)
            # table.setText(row, 22, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile, contingent = 1))
            table.setText(row, 19, self.dataInvolutionDays(orgStructureIdList, begDate, endDate, profile), charFormat=self.charFormatBody)
            table.setText(row, 20, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile, contingent = 2), charFormat=self.charFormatBody)

        currentDate = QtCore.QDate.currentDate()
        currentDateYear = currentDate.year()
        # precedentDateMonth = currentDate.month() - 1
        precedentDateMonth = currentDate.month()
        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 1):
            unrolledHospitalBedsMonth(5, 1, profile)#Число коек на конец отчетного периода - Это как общее колво за весь период или наличие коек на последний день? Как за полугодие и за год?????????????????????????????????????
            begDate, endDate = self.createBegEndDate(1, 1, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 5)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 2):
            unrolledHospitalBedsMonth(6, 2, profile)
            begDate, endDate = self.createBegEndDate(2, 2, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 6)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 3):
            unrolledHospitalBedsMonth(7, 3, profile)
            begDate, endDate = self.createBegEndDate(3, 3, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 7)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 4):
            unrolledHospitalBedsMonth(8, 4, profile)
            begDate, endDate = self.createBegEndDate(4, 4, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 8)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 5):
            unrolledHospitalBedsMonth(9, 5, profile)
            begDate, endDate = self.createBegEndDate(5, 5, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 9)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 6):
            unrolledHospitalBedsMonth(10, 6, profile)
            begDate, endDate = self.createBegEndDate(6, 6, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 10)

        unrolledHospitalBedsMonth(11, 6, profile, True)
        begDate, endDate = self.createBegEndDate(1, precedentDateMonth if precedentDateMonth <= 6 else 6, yearDateInt)
        self.averageYarHospitalBed(orgStructureIdList, table, begDate, endDate, profile, 11, None, 6)
        table.setText(11, 4, self.movingsPresentBeg, charFormat=self.charFormatBodyBold)
        all, children, adultCount, clientRural, isStationaryDay, countPatronage = getReceived(None, begDate, endDate, u'Переведен из отделения', profile, orgStructureIdList, simplifyDateCond=True, socStatusTypeId=socStatusTypeId, socStatusClassId=socStatusClassId)
        table.setText(11, 5, all, charFormat=self.charFormatBodyBold)
        table.setText(11, 6, isStationaryDay, charFormat=self.charFormatBodyBold)
        table.setText(11, 7, clientRural, charFormat=self.charFormatBodyBold)
        table.setText(11, 8, children, charFormat=self.charFormatBodyBold)
        table.setText(11, 9, adultCount, charFormat=self.charFormatBodyBold)
        table.setText(11, 10, getMovingTransfer(None, begDate, endDate, u'Переведен из отделения', profile, orgStructureIdList = orgStructureIdList, socStatusTypeId = socStatusTypeId, socStatusClassId = socStatusClassId)[0], charFormat=self.charFormatBodyBold)
        table.setText(11, 11, getMovingTransfer(None, begDate, endDate, u'Переведен в отделение', profile, True, orgStructureIdList = orgStructureIdList, socStatusTypeId = socStatusTypeId, socStatusClassId = socStatusClassId)[0], charFormat=self.charFormatBodyBold)
        countLeavedAll, leavedDeath, leavedTransfer, leavedAllPatronag, leavedDeathPatronag, leavedTransferPatronag, leavedElder, deadElder, leavedDayStat, leavedNoctidialStat = getLeaved(None,
                                                                                                                                    begDate,
                                                                                                                                    endDate,
                                                                                                                                    profile,
                                                                                                                                    orgStructureIdList,
                                                                                                                                    simplifyDateCond = True,
                                                                                                                                    socStatusTypeId = socStatusTypeId,
                                                                                                                                    socStatusClassId = socStatusClassId)
        table.setText(11, 12, countLeavedAll, charFormat=self.charFormatBodyBold)
        # table.setText(11, 14, leavedElder)
        table.setText(11, 13, leavedDayStat, charFormat=self.charFormatBodyBold)
        table.setText(11, 14, leavedNoctidialStat, charFormat=self.charFormatBodyBold)
        table.setText(11, 15, leavedTransfer, charFormat=self.charFormatBodyBold)
        table.setText(11, 16, leavedDeath, charFormat=self.charFormatBodyBold)
        # table.setText(11, 19, deadElder)
        table.setText(11, 17, self.movingsPresentEnd, charFormat=self.charFormatBodyBold)
        table.setText(11, 18, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile), charFormat=self.charFormatBodyBold)
        # table.setText(11, 22, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile, contingent = 1))
        table.setText(11, 19, self.dataInvolutionDays(orgStructureIdList, begDate, endDate, profile), charFormat=self.charFormatBodyBold)
        table.setText(11, 20, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile, contingent = 2), charFormat=self.charFormatBodyBold)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 7):
            unrolledHospitalBedsMonth(12, 7, profile)
            begDate, endDate = self.createBegEndDate(7, 7, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 12)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 8):
            unrolledHospitalBedsMonth(13, 8, profile)
            begDate, endDate = self.createBegEndDate(8, 8, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 13)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 9):
            unrolledHospitalBedsMonth(14, 9, profile)
            begDate, endDate = self.createBegEndDate(9, 9, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 14)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 10):
            unrolledHospitalBedsMonth(15, 10, profile)
            begDate, endDate = self.createBegEndDate(10, 10, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 15)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 11):
            unrolledHospitalBedsMonth(16, 11, profile)
            columnFill(begDate, endDate, orgStructureIdList, profile, 16)

        if (yearDateInt != currentDateYear) or (precedentDateMonth >= 12):
            unrolledHospitalBedsMonth(17, 12, profile)
            begDate, endDate = self.createBegEndDate(12, 12, yearDateInt)
            columnFill(begDate, endDate, orgStructureIdList, profile, 17)

        unrolledHospitalBedsMonth(18, 12, profile, True)
        begDate, endDate = self.createBegEndDate(1, 12, yearDateInt)
        self.averageYarHospitalBed(orgStructureIdList, table, begDate, endDate, profile, 18, None, 12)
        begDate, endDate = self.createBegEndDate(1, precedentDateMonth, yearDateInt)
        table.setText(18, 4, self.movingsPresentBeg, charFormat=self.charFormatBodyBold)
        all, children, adultCount, clientRural, isStationaryDay, countPatronage = getReceived(None, begDate, endDate, u'Переведен из отделения', profile, orgStructureIdList, simplifyDateCond=True, socStatusTypeId=socStatusTypeId, socStatusClassId=socStatusClassId)
        table.setText(18, 5, all, charFormat=self.charFormatBodyBold)
        table.setText(18, 6, isStationaryDay, charFormat=self.charFormatBodyBold)
        table.setText(18, 7, clientRural, charFormat=self.charFormatBodyBold)
        table.setText(18, 8, children, charFormat=self.charFormatBodyBold)
        table.setText(18, 9, adultCount, charFormat=self.charFormatBodyBold)
        table.setText(18, 10, getMovingTransfer(None, begDate, endDate, u'Переведен из отделения', profile, orgStructureIdList = orgStructureIdList, socStatusTypeId = socStatusTypeId, socStatusClassId = socStatusClassId)[0], charFormat=self.charFormatBodyBold)
        table.setText(18, 11, getMovingTransfer(None, begDate, endDate, u'Переведен в отделение', profile, True, orgStructureIdList = orgStructureIdList, socStatusTypeId = socStatusTypeId, socStatusClassId = socStatusClassId)[0], charFormat=self.charFormatBodyBold)
        countLeavedAll, leavedDeath, leavedTransfer, leavedAllPatronag, leavedDeathPatronag, leavedTransferPatronag, leavedElder, deadElder, leavedDayStat, leavedNoctidialStat = getLeaved(None,
                                                                                                                                    begDate,
                                                                                                                                    endDate,
                                                                                                                                    profile,
                                                                                                                                    orgStructureIdList,
                                                                                                                                    simplifyDateCond = True,
                                                                                                                                    socStatusTypeId = socStatusTypeId,
                                                                                                                                    socStatusClassId = socStatusClassId)
        table.setText(18, 12, countLeavedAll, charFormat=self.charFormatBodyBold)
        # table.setText(18, 14, leavedElder)
        table.setText(18, 13, leavedDayStat, charFormat=self.charFormatBodyBold)
        table.setText(18, 14, leavedNoctidialStat, charFormat=self.charFormatBodyBold)
        table.setText(18, 15, leavedTransfer, charFormat=self.charFormatBodyBold)
        table.setText(18, 16, leavedDeath, charFormat=self.charFormatBodyBold)
        # table.setText(18, 19, deadElder)
        table.setText(18, 17, self.movingsPresentEnd, charFormat=self.charFormatBodyBold)
        table.setText(18, 18, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile), charFormat=self.charFormatBodyBold) # К - дней
        # table.setText(18, 22, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile, contingent = 1)) # К-дней старше ТВ
        table.setText(18, 19, self.dataInvolutionDays(orgStructureIdList, begDate, endDate, profile), charFormat=self.charFormatBodyBold) # К-дней закрытия
        table.setText(18, 20, self.dataMovingDays(orgStructureIdList, begDate, endDate, profile, contingent = 2), charFormat=self.charFormatBodyBold) # К-дней по уходу

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.insertText(u'Подпись ' + u'_' * 20)

        return doc


    def createBegEndDate(self, monthBeg, monthEnd, yearDateInt):
        begDate = QtCore.QDate(yearDateInt, monthBeg, 1)
        if monthEnd < 12:
            endDate = QtCore.QDate(yearDateInt, monthEnd +1, 1)
        else:
            endDate = QtCore.QDate(yearDateInt + 1, 1, 1)
        return begDate, endDate


    def averageYarHospitalBed(self, orgStructureIdList, table, begDate, endDate, profile = None, row = None, isHospital = None, countMonths = None):
        days = 0
        daysMonths = 0
        begDatePeriod = begDate
        endMonth = endDate.month()
        endDatePeriod = begDatePeriod.addMonths(1)
        while endDatePeriod <= endDate:
            days = self.averageDaysHospitalBed(orgStructureIdList, begDatePeriod, endDatePeriod, profile, isHospital)
            daysMonths += days / (begDatePeriod.daysInMonth())
            begDatePeriod = begDatePeriod.addMonths(1)
            endDatePeriod = endDatePeriod.addMonths(1)
        if countMonths == 12:
            daysMonths = daysMonths / 12
        elif countMonths == 6:
            daysMonths = daysMonths / 6
        if profile:
           table.setText(row, 3, daysMonths, charFormat=self.charFormatBodyBold)
        else:
            table.setText(row, 3, daysMonths, charFormat=self.charFormatBody)


    def averageDaysHospitalBed(self, orgStructureIdList, begDatePeriod, endDatePeriod, profile = None, isHospital = None):
        days = 0
        db = QtGui.qApp.db
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOrg = db.table('Organisation')
        tableOS = db.table('OrgStructure')
        queryTable = tableOSHB.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
        queryTable = queryTable.innerJoin(tableOrg, tableOrg['id'].eq(tableOS['organisation_id']))
        cond = [tableOSHB['master_id'].inlist(orgStructureIdList),
                tableOrg['deleted'].eq(0),
                tableOS['deleted'].eq(0)
                ]
        if isHospital != None:
           cond.append(tableOrg['isHospital'].eq(isHospital))
        joinAnd = db.joinAnd([tableOSHB['endDate'].isNull(), db.joinOr([db.joinAnd([tableOSHB['begDate'].isNotNull(), tableOSHB['begDate'].lt(endDatePeriod)]), tableOSHB['begDate'].isNull()])])
        cond.append(db.joinOr([db.joinAnd([tableOSHB['endDate'].isNotNull(), tableOSHB['endDate'].gt(begDatePeriod), tableOSHB['begDate'].isNotNull(), tableOSHB['begDate'].lt(endDatePeriod)]), joinAnd]))
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


    def dataMovingDays(self, orgStructureIdList, begDatePeriod, endDatePeriod, profile = None, isHospital = None, contingent = 0):
        # contingent == 0 - всего, 1 - старше трудоспособного возраста, 2 - койко-дни  по уходу
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
                tableClient['deleted'].eq(0),
                tableOrg['deleted'].eq(0),
                tableAPT['typeName'].like('HospitalBed'),
                tableAP['action_id'].eq(tableAction['id'])
               ]
        if isHospital != None:
           cond.append(tableOrg['isHospital'].eq(isHospital))
        if profile:
           cond.append(tableOSHB['profile_id'].eq(profile))
        cond.append(tableOSHB['master_id'].inlist(orgStructureIdList))
        joinAnd = db.joinAnd([tableAction['endDate'].isNull(), tableAction['begDate'].isNotNull(), tableAction['begDate'].lt(endDatePeriod)])
        cond.append(db.joinOr([db.joinAnd([tableAction['endDate'].isNotNull(), tableAction['endDate'].gt(begDatePeriod), tableAction['begDate'].isNotNull(), tableAction['begDate'].lt(endDatePeriod)]), joinAnd]))
        if contingent == 1:
            cond.append(u'age(Client.birthDate, Action.begDate) >= 60')
        elif contingent == 2:
            cond.append(getStringProperty(u'Патронаж%', u'(APS.value LIKE \'Да\')'))
        stmt = db.selectStmt(queryTable, [tableEvent['id'].alias('eventId'), tableAction['id'].alias('actionId'), tableAction['begDate'], tableAction['endDate']], cond)
        query = db.query(stmt)
        actionIdList = []
        while query.next():
            record = query.record()
            actionId = forceRef(record.value('actionId'))
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
                    else:
                        days += begDate.daysTo(endDate)
        return days


    def dataInvolutionDays(self, orgStructureIdList, begDatePeriod, endDatePeriod, profile = None, isHospital = None):
        days = 0
        db = QtGui.qApp.db
        tableVHospitalBed = db.table('vHospitalBed')
        condRepairs = [tableVHospitalBed['involution'].ne(0)]
        condRepairs.append(tableVHospitalBed['master_id'].inlist(orgStructureIdList))
        if profile:
           condRepairs.append(tableVHospitalBed['profile_id'].eq(profile))
        condRepairs.append(db.joinOr([db.joinAnd([tableVHospitalBed['endDateInvolute'].isNull(),tableVHospitalBed['begDateInvolute'].isNull()]), db.joinAnd([tableVHospitalBed['begDateInvolute'].isNotNull(), tableVHospitalBed['begDateInvolute'].ge(begDatePeriod), tableVHospitalBed['begDateInvolute'].lt(endDatePeriod)]),
            db.joinAnd([tableVHospitalBed['endDateInvolute'].isNotNull(), tableVHospitalBed['endDateInvolute'].gt(begDatePeriod), tableVHospitalBed['endDateInvolute'].le(endDatePeriod)])]))
        stmt = db.selectStmt(tableVHospitalBed, [tableVHospitalBed['id'].alias('bedId'), tableVHospitalBed['begDateInvolute'], tableVHospitalBed['endDateInvolute']], condRepairs)
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

