# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action import CAction
from Orgs.OrgStructComboBoxes import COrgStructureModel
from Orgs.Utils import getPersonInfo, getOrganisationMainStaff
from RefBooks.Person import CRBPersonEditor
from Registry.ResourcesDock import CActivityModel, CActivityTreeItem
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from Timeline.PlanNumbersDialog import CPlanNumbersDialog
from Timeline.TemplateDialog import CParamsForExternalDialog, CTemplateOnRotationDialog, CTemplateDialog, \
    CTemplateDialogMany, CTemplatePersonsCreate, CPersonTemplateDialog, setInterval
from Timeline.TimeTable import CTimeTableModel, getEvent, calcTimeInterval, calcTimePlan, calcSecondsInTime
from Ui_AbsenceDialog import Ui_AbsenceDialog
from Ui_CalcDialog import Ui_CalcDialog
from Ui_DublDialog import Ui_DublDialog
from Ui_TimelineDialog import Ui_TimelineDialog
from Users.Rights import urAccessEditTimelineDialog, urAdmin, urAccessRefPersonPersonal, urEditFilledTimetableAction
from library import constants
from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CTextCol, CNameCol, CBoolCol, CDateCol, CDesignationCol, CRefBookCol
from library.Utils import forceString, forceRef, forceInt


class CTimelineDialog(CDialogBase, Ui_TimelineDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId()))
        self.addModels('Activity',     CActivityModel(self))
        self.addModels('Personnel',    CPersonnelModel(self))
        self.addModels('TimeTable',    CTimeTableModel(self))
        self.actFillByTemplate = QtGui.QAction(u'Заполнить', self)
        self.actFillByTemplate.setObjectName('actFillByTemplate')
        self.actRecountNumbers = QtGui.QAction(u'Пересчитать', self)
        self.actRecountNumbers.setObjectName('actRecountNumbers')
        self.actPlanNumbers = QtGui.QAction(u'Номерки', self)
        self.actPlanNumbers.setObjectName('actPlanNumbers')
        self.actSelectAllRow = QtGui.QAction(u'Выделить все строки', self)
        self.actSelectAllRow.setObjectName('actSelectAllRow')
        self.actClearSelectionRow = QtGui.QAction(u'Снять выделение', self)
        self.actClearSelectionRow.setObjectName('actClearSelectionRow')
        self.actChangeTimelineAccessibility = QtGui.QAction(u'Изменить параметры доступа к расписанию', self)
        self.actChangeTimelineAccessibility.setObjectName('actChangeTimelineAccessibility')
        self.actSetAvailableForExternal = QtGui.QAction(u'Сделать доступным для внешней системы', self)
        self.actSetAvailableForExternal.setObjectName('actSetAvailableForExternal')
        self.actUnsetAvailableForExternal = QtGui.QAction(u'Сделать недоступным для внешней системы', self)
        self.actUnsetAvailableForExternal.setObjectName('actUnsetAvailableForExternal')
        self.modelActivity.setRootItem(CActivityRootTreeItem())

        self.actFillByTemplate.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))
        self.actRecountNumbers.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))
        self.actPlanNumbers.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))
        self.actChangeTimelineAccessibility.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))
        self.actSetAvailableForExternal.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))
        self.actUnsetAvailableForExternal.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))

        self.setupPrintMenu()
        self.setupFillMenu()

        self.setupUi(self)

        self.btnPrint.setMenu(self.mnuPrint)
        self.btnFill.setMenu(self.mnuFill)

        self.calendar.setList(QtGui.qApp.calendarInfo)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.activityListIsShown = False
        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        self.setModels(self.tblPersonnel, self.modelPersonnel, self.selectionModelPersonnel)
        self.setModels(self.tblTimeTable, self.modelTimeTable, self.selectionModelTimeTable)

        self.notSelectedRows = True
        self.tblTimeTable.createPopupMenu([self.actFillByTemplate, self.actRecountNumbers, self.actPlanNumbers])
        self.tblPersonnel.createPopupMenu([self.actSelectAllRow, self.actClearSelectionRow, self.actChangeTimelineAccessibility, self.actSetAvailableForExternal, self.actUnsetAvailableForExternal])

        orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
        if orgStructureIndex and orgStructureIndex.isValid():
            self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
            self.treeOrgStructure.setExpanded(orgStructureIndex, True)

        startDate = QtCore.QDate.currentDate()
        self.calendar.setSelectedDate(startDate)
#        self.on_calendar_selectionChanged()
        self.setDateInTable(startDate, False)
        self.connect(self.tblTimeTable.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAmbAboutToShow)
        self.connect(self.tblPersonnel.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuPersonAboutToShow)
        self.connect(self.btnFill.menu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuFillAboutToShow)
        self.connect(self.modelTimeTable, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.markAsDirty)
        self.headerTreeOS = self.treeOrgStructure.header()
        self.headerTreeOS.setClickable(True)
        QtCore.QObject.connect(self.headerTreeOS, QtCore.SIGNAL('sectionClicked(int)'), self.onSectionClicked)
        self.tblPersonnel.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.btnDubl.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))
        self.btnFill.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))
        self.btnOk.setEnabled(QtGui.qApp.userHasRight(urAccessEditTimelineDialog))

    def none(self):
        pass

    def saveData(self):
        QtGui.qApp.callWithWaitCursor(self, self.modelTimeTable.saveData)
        return True & QtGui.qApp.userHasRight(urAccessEditTimelineDialog)
        

    def onSectionClicked(self, col):
        if self.activityListIsShown:
            self.treeOrgStructure.setModel(None)
            self.activityListIsShown = False
            self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
            orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
            if orgStructureIndex and orgStructureIndex.isValid():
                self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
                self.treeOrgStructure.setExpanded(orgStructureIndex, True)
            self.updatePersonListByOrgStructure()
        else:
            self.treeOrgStructure.setModel(None)
            self.activityListIsShown = True
            self.setModels(self.treeOrgStructure, self.modelActivity, self.selectionModelActivity)
            activityIndex = self.modelActivity.findItemId(1)
            if activityIndex and activityIndex.isValid():
                self.treeOrgStructure.setCurrentIndex(activityIndex)
            self.treeOrgStructure.expandAll()
            self.updatePersonListByActivity()


    def popupMenuAmbAboutToShow(self):
        if QtGui.qApp.userHasRight(urAccessEditTimelineDialog):
            currentIndex = self.tblTimeTable.currentIndex()
            row = currentIndex.row()
            if row < self.modelTimeTable.daysInMonth:
                action = self.modelTimeTable.actionAmbulance[row]
                if action and any(action['queue']) and not QtGui.qApp.userHasRight(urEditFilledTimetableAction):
                    self.actFillByTemplate.setEnabled(False)
                    self.actRecountNumbers.setEnabled(False)
                    self.actPlanNumbers.setEnabled(False)
                else:
                    ambTime = self.modelTimeTable.items[row][CTimeTableModel.ciAmbTimeRange]
                    ambCount = self.modelTimeTable.items[row][CTimeTableModel.ciAmbPlan]
                    homeTime = self.modelTimeTable.items[row][CTimeTableModel.ciHomeTimeRange]
                    homeCount = self.modelTimeTable.items[row][CTimeTableModel.ciHomePlan]
                    if (ambTime and ambCount and ambCount > 0) or (homeTime and homeCount and  homeCount > 0):
                        self.actPlanNumbers.setEnabled(True)
                        self.actRecountNumbers.setEnabled(True)
                    else:
                        self.actPlanNumbers.setEnabled(False)
                        self.actRecountNumbers.setEnabled(False)


    def popupMenuPersonAboutToShow(self):
        if QtGui.qApp.userHasRight(urAccessEditTimelineDialog):
            currentIndex = self.tblPersonnel.currentIndex()
            curentIndexIsValid = currentIndex.isValid()
            if self.actSelectAllRow:
                self.actSelectAllRow.setEnabled(curentIndexIsValid)
            if self.actClearSelectionRow:
                self.actClearSelectionRow.setEnabled(curentIndexIsValid)
            if self.actChangeTimelineAccessibility:
                self.actChangeTimelineAccessibility.setEnabled(curentIndexIsValid)
            if self.actSetAvailableForExternal:
                self.actSetAvailableForExternal.setEnabled(curentIndexIsValid)
            if self.actUnsetAvailableForExternal:
                self.actUnsetAvailableForExternal.setEnabled(curentIndexIsValid)


    def popupMenuFillAboutToShow(self):
        if QtGui.qApp.userHasRight(urAccessEditTimelineDialog):
            self.actFillTemplate.setEnabled(len(self.tblPersonnel.selectedItemIdList()) > 0)
            self.actFillTemplateOnRotation.setEnabled(len(self.tblPersonnel.selectedItemIdList()) == 1)
            self.actFillPerson.setEnabled(len(self.tblPersonnel.selectedItemIdList()) > 0)


    def changeTimelineAccessibility(self):
        personIdList = self.tblPersonnel.selectedItemIdList()
        if personIdList:
            dialog = CParamsForExternalDialog(self)
            if dialog.exec_():
                db = QtGui.qApp.db
                table = db.table('Person')
                if dialog.chkLastAccessibleTimelineDate.isChecked() and dialog.chkTimelineAccessibilityDays.isChecked():
                    record = table.newRecord(['lastAccessibleTimelineDate', 'timelineAccessibleDays'])
                elif dialog.chkLastAccessibleTimelineDate.isChecked():
                    record = table.newRecord(['lastAccessibleTimelineDate'])
                elif dialog.chkTimelineAccessibilityDays.isChecked():
                    record = table.newRecord(['timelineAccessibleDays'])
                if dialog.chkLastAccessibleTimelineDate.isChecked():
                    date = dialog.edtLastAccessibleTimelineDate.date()
                    record.setValue('lastAccessibleTimelineDate', QtCore.QVariant(date) if date else QtCore.QVariant())
                if dialog.chkTimelineAccessibilityDays.isChecked():
                    days = dialog.edtTimelineAccessibilityDays.value()
                    record.setValue('timelineAccessibleDays', QtCore.QVariant(days))
                if dialog.chkLastAccessibleTimelineDate.isChecked() or dialog.chkTimelineAccessibilityDays.isChecked():
                    QtGui.qApp.callWithWaitCursor(self, db.updateRecords, table, record, table['id'].inlist(personIdList))
                    self.invalidatePersonTable()


    def setAvailableForExternal(self, value):
        personIdList = self.tblPersonnel.selectedItemIdList()
        db = QtGui.qApp.db
        table = db.table('Person')
        db.updateRecords(table,
                         table['availableForExternal'].eq(value),
                         table['id'].inlist(personIdList))
        self.invalidatePersonTable()


    def invalidatePersonTable(self):
        self.modelPersonnel.invalidateRecordsCache()
        self.modelPersonnel.emitDataChanged()


    def getOrgStructureId(self):
        # only selected
        if self.activityListIsShown:
            return None
        else:
            treeIndex = self.treeOrgStructure.currentIndex()
            treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
            return treeItem.id() if treeItem else None


    def getOrgStructureIdList(self):
        # selected and descendants
        if self.activityListIsShown:
            return None
        else:
            treeIndex = self.treeOrgStructure.currentIndex()
            treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
            return treeItem.getItemIdList() if treeItem else []


    def getActivityId(self):
        # only selected - descendants is not provided
        if self.activityListIsShown:
            treeIndex = self.treeOrgStructure.currentIndex()
            itemName = treeIndex.internalPointer().name()
            activityIdList = self.modelActivity.getItemIdList(treeIndex)
            if activityIdList and len(activityIdList) == 1:
                return activityIdList[0]
            elif itemName == u'Любой':
                return activityIdList
            elif itemName == u'Не определен':
                return 'withoutActivity'
            else:
                return None
        else:
            return None


    def getPersonIdListByOrgStructure(self, orgStructureIdList, date):
        if orgStructureIdList:
            db = QtGui.qApp.db
            table = db.table('Person')
            cond = [table['orgStructure_id'].inlist(orgStructureIdList)]
            if date:
                cond.append(db.joinOr([
                    table['retireDate'].isNull(), db.joinAnd([table['retireDate'].monthGe(date), table['retireDate'].yearGe(date)])]))
            return db.getIdList(table, where=cond, order='lastName, firstName, patrName')
        return []


    def updatePersonListByOrgStructure(self):
        orgStructureIdList = self.getOrgStructureIdList()
        date = QtCore.QDate(self.calendar.yearShown(), self.calendar.monthShown(), 1)
        personIdList = self.getPersonIdListByOrgStructure(orgStructureIdList, date)
        self.tblPersonnel.setIdList(personIdList)


    def getPersonIdListByActivity(self, activityIdList, date):
        if activityIdList:
            db = QtGui.qApp.db
            table = db.table('Person')
            tablePersonActivity = db.table('Person_Activity')
            queryTable = table.leftJoin(tablePersonActivity, tablePersonActivity['master_id'].eq(table['id']))
            cond = [
                    table['deleted'].eq(0),
                    tablePersonActivity['deleted'].eq(0)
                    ]
            withoutActivity = (len(activityIdList) == 1 and activityIdList[0] == 'withoutActivity')
            if withoutActivity:
                cond.append(tablePersonActivity['activity_id'].isNotNull())
            else:
                cond.append(tablePersonActivity['activity_id'].inlist(activityIdList))
            if date:
                retireCond = db.joinOr([
                    table['retireDate'].isNull(), table['retireDate'].ge(date)])
                cond.append(retireCond)
            activityPersonIdList = db.getDistinctIdList(queryTable, idCol='Person.id', where=cond, order='lastName, firstName, patrName')
            if withoutActivity:
                cond = [table['deleted'].eq(0), table['id'].notInlist(activityPersonIdList)]
                if date:
                    cond.append(retireCond)
                return db.getDistinctIdList(table, idCol='id', where=cond, order='lastName, firstName, patrName')
            return activityPersonIdList
        return []

    def getPersonIdListByAllActivity(self, activityId, date):
        resume = []
        for id in activityId:
            resume += self.getPersonIdListByActivity([id], date)
        return resume

    def updatePersonListByActivity(self):
        activityId = self.getActivityId()
        date = QtCore.QDate(self.calendar.yearShown(), self.calendar.monthShown(), 1)
        if isinstance(activityId, list):
            personIdList = self.getPersonIdListByAllActivity(activityId, date)
        else:
            personIdList = self.getPersonIdListByActivity([activityId], date)
        self.tblPersonnel.setIdList(personIdList)


    def setDateInTable(self, date, scrollToDate=True):
        personId = self.tblPersonnel.currentItemId()
        QtGui.qApp.callWithWaitCursor(
            self, self.modelTimeTable.setPersonAndMonth, personId, date.year(), date.month(), date)
        row = self.modelTimeTable.begDate.daysTo(date)
        currentIndex = self.tblTimeTable.currentIndex()
        currentColumn = currentIndex.column() if currentIndex.isValid() else 0
        newIndex = self.modelTimeTable.index(row, currentColumn)
        self.tblTimeTable.setCurrentIndex(newIndex)
#        self.selectionModelTimeTable.select(
#            newIndex, QtGui.QItemSelectionModel.Clear|QtGui.QItemSelectionModel.Select|QtGui.QItemSelectionModel.Current)
        if scrollToDate:
            self.tblTimeTable.scrollTo(newIndex, QtGui.QAbstractItemView.EnsureVisible)

        self.tblTimeTable.setEnabled( bool(personId) )
        if QtGui.qApp.userHasRight(urAccessEditTimelineDialog):
            self.btnFill.setEnabled( bool(personId) )


    def fillByTemplateOnRotation(self):
        if len(self.tblPersonnel.selectedItemIdList()) == 1:
            dialog = CTemplateOnRotationDialog(self)
            begDate = self.modelTimeTable.begDate
            endDate = begDate.addDays(self.modelTimeTable.daysInMonth-1)
            dialog.setDateRange(begDate, endDate)
            dialog.setPersonInfo(self.tblPersonnel.currentItemId())
            dialog.setPersonId(self.tblPersonnel.currentItemId())
            if dialog.exec_():
                QtGui.qApp.callWithWaitCursor(self, self.modelTimeTable.setWorkPlanOnRotation, dialog.getWorkPlan(), dialog.getSelectedDays())


    def fillByTemplate(self):
        personIdList = self.tblPersonnel.selectedItemIdList()
        lenPersonIdList = len(personIdList)
        selectPersons = lenPersonIdList > 1
        currentPersonId = self.tblPersonnel.currentItemId()
        if selectPersons:
            dialog = CTemplateDialogMany(self)
        else:
            dialog = CTemplateDialog(self)
            dialog.setPersonInfo(self.tblPersonnel.currentItemId())
            dialog.setPersonId(self.tblPersonnel.currentItemId())
        if dialog.exec_():
            if selectPersons:
                db = QtGui.qApp.db
                dialogInfoCreate = CTemplatePersonsCreate(self)
                dialogInfoCreate.show()
                prbControlPercent = 0
                dialogInfoCreate.lblCountSelected.setText(u'Выбрано всего строк %d' % (lenPersonIdList,))
                dialogInfoCreate.prbTemplateCreate.setMaximum(lenPersonIdList)
                for personId in personIdList:
                    QtGui.qApp.processEvents()
                    dialogInfoCreate.lblPersonName.setText(forceString(db.translate('vrbPersonWithSpeciality', 'id',
                                                                                    personId, 'name')))
                    if dialogInfoCreate.abortProcess:
                        break
                    prbControlPercent += 1
                    dialogInfoCreate.prbTemplateCreate.setValue(prbControlPercent)
                    dialog.setPersonId(personId)
                    QtGui.qApp.callWithWaitCursor(self, self.getWorkPlanPersonTemplate,
                                                  dialog, personId, selectPersons)
                    dialogInfoCreate.lblCountCreate.setText(u'Обработано всего строк %d'%(prbControlPercent))
                QtGui.qApp.callWithWaitCursor(self, self.loadWorkPlanPerson, currentPersonId)
                dialogInfoCreate.lblPersonName.setText(u'ПРЕРВАНО' if dialogInfoCreate.abortProcess else u'ГОТОВО')
                dialogInfoCreate.abortProcess = False
                self.enabledButtonsForSelected()
            else:
                QtGui.qApp.callWithWaitCursor(self, self.modelTimeTable.setWorkPlan,
                                              dialog.getWorkPlan(), dialog.getDateRange())
                self.setIsDirty(True)
            # self.labelsUpdate()

    def getWorkPlanPersonTemplate(self, dialog, personId, selectPersons):
        self.modelTimeTable.setWorkPlanTemplates(dialog.getWorkPlan(), dialog.getDateRange())
        self.modelTimeTable.saveDataPersonTemplate(personId)
        self.setIsDirty(True)


    def fillByPerson(self):
        dialog = CPersonTemplateDialog(self)
        begDate = self.modelTimeTable.begDate
        endDate = begDate.addDays(self.modelTimeTable.daysInMonth-1)
        personIdList = self.tblPersonnel.selectedItemIdList()
        currentPersonId = self.tblPersonnel.currentItemId()
        dialog.setPersonIdList(personIdList)
        lenPersonIdList = len(dialog.personIdList)
        selectPersons = lenPersonIdList > 1
        dialog.setDateRange(begDate, endDate)
        if dialog.exec_():
            if selectPersons:
                db = QtGui.qApp.db
                dialogInfoCreate = CTemplatePersonsCreate(self)
                dialogInfoCreate.show()
                prbControlPercent = 0
                dialogInfoCreate.lblCountSelected.setText(u'Выбрано всего строк %d'%(lenPersonIdList))
                dialogInfoCreate.prbTemplateCreate.setMaximum(lenPersonIdList)
                for personId in dialog.personIdList:
                    QtGui.qApp.processEvents()
                    dialogInfoCreate.lblPersonName.setText(forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')))
                    if dialogInfoCreate.abortProcess:
                        break
                    prbControlPercent += 1
                    dialogInfoCreate.prbTemplateCreate.setValue(prbControlPercent)
                    QtGui.qApp.callWithWaitCursor(self, self.getWorkPlanPerson, dialog, selectPersons, personId)
                    dialogInfoCreate.lblCountCreate.setText(u'Обработано всего строк %d'%(prbControlPercent))
                QtGui.qApp.callWithWaitCursor(self, self.loadWorkPlanPerson, currentPersonId)
                dialogInfoCreate.lblPersonName.setText(u'ПРЕРВАНО' if dialogInfoCreate.abortProcess else u'ГОТОВО')
                dialogInfoCreate.abortProcess = False
                self.enabledButtonsForSelected()
            else:
                QtGui.qApp.callWithWaitCursor(self, self.modelTimeTable.setWorkPlanPerson, dialog.getDateRange(), dialog.chkFillRedDaysPerson.isChecked(), dialog.chkAmbSecondPeriodPerson.isChecked(), dialog.chkHomeSecondPeriodPerson.isChecked(), dialog.chkAmbInterPeriodPerson.isChecked(), currentPersonId, selectPersons)
                self.setIsDirty(True)


    def enabledButtonsForSelected(self, enabled = True):
        self.notSelectedRows = enabled
        if self.btnCalc.isEnabled() == (not enabled):
            self.btnCalc.setEnabled(enabled)
            self.btnPrint.setEnabled(enabled)
            self.btnDubl.setEnabled(enabled)
            self.btnSum.setEnabled(enabled)
            self.btnFact.setEnabled(enabled)


    def getWorkPlanPerson(self, dialog, selectPersons, personId):
        self.modelTimeTable.setWorkPlanPerson(dialog.getDateRange(), dialog.chkFillRedDaysPerson.isChecked(), dialog.chkAmbSecondPeriodPerson.isChecked(), dialog.chkHomeSecondPeriodPerson.isChecked(), dialog.chkAmbInterPeriodPerson.isChecked(), personId, selectPersons)
        self.modelTimeTable.saveDataPersonTemplate(personId)
        self.setIsDirty(True)


    def loadWorkPlanPerson(self, currentPersonId):
        self.tblPersonnel.setCurrentItemId(currentPersonId)
        self.modelTimeTable.loadData(self.tblPersonnel.currentItemId(), self.modelTimeTable.begDate.year(), self.modelTimeTable.begDate.month())
        self.labelsUpdate()


    def getPlanNumbersDialog(self):
        currentIndex = self.tblTimeTable.currentIndex()
        row = currentIndex.row()
        ambTime = self.modelTimeTable.items[row][CTimeTableModel.ciAmbTimeRange]
        ambCount = self.modelTimeTable.items[row][CTimeTableModel.ciAmbPlan]
        homeTime = self.modelTimeTable.items[row][CTimeTableModel.ciHomeTimeRange]
        homeCount = self.modelTimeTable.items[row][CTimeTableModel.ciHomePlan]
        visibleAmb = ambTime and ambCount and ambCount > 0
        visibleHome = homeTime and homeCount and  homeCount > 0
        date = QtCore.QDate(self.calendar.selectedDate())
        personId = self.tblPersonnel.currentItemId()
        if personId and date and (visibleAmb or visibleHome):
            dialog = CPlanNumbersDialog(self, personId, date, self.modelTimeTable.items[row], visibleAmb, self.modelTimeTable.items[row][CTimeTableModel.ciAmbChange], visibleHome, self.modelTimeTable.items[row][CTimeTableModel.ciHomeChange])
            dialog.exec_()


    def recountPlanNumbers(self):
        currentIndex = self.tblTimeTable.currentIndex()
        row = currentIndex.row()
        ambTime = self.modelTimeTable.items[row][CTimeTableModel.ciAmbTimeRange]
        ambCount = self.modelTimeTable.items[row][CTimeTableModel.ciAmbPlan]
        homeTime = self.modelTimeTable.items[row][CTimeTableModel.ciHomeTimeRange]
        homeCount = self.modelTimeTable.items[row][CTimeTableModel.ciHomePlan]
        self.modelTimeTable.items[row][CTimeTableModel.ciAmbChange] = ambTime and ambCount and ambCount > 0
        self.modelTimeTable.items[row][CTimeTableModel.ciHomeChange] = homeTime and homeCount and  homeCount > 0
        self.setIsDirty(True)


    @QtCore.pyqtSlot()
    def on_actSelectAllRow_triggered(self):
        self.notSelectedRows = False
        self.tblPersonnel.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblPersonnel.selectAll()
        self.tblPersonnel.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.btnCalc.setEnabled(False)
        self.btnPrint.setEnabled(False)
        self.btnDubl.setEnabled(False)
        self.btnSum.setEnabled(False)
        self.btnFact.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_actClearSelectionRow_triggered(self):
        self.tblPersonnel.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblPersonnel.clearSelection()
        self.tblPersonnel.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.enabledButtonsForSelected()


    @QtCore.pyqtSlot()
    def on_actChangeTimelineAccessibility_triggered(self):
        self.changeTimelineAccessibility()


    @QtCore.pyqtSlot()
    def on_actSetAvailableForExternal_triggered(self):
        QtGui.qApp.callWithWaitCursor(self, self.setAvailableForExternal, True)


    @QtCore.pyqtSlot()
    def on_actUnsetAvailableForExternal_triggered(self):
        QtGui.qApp.callWithWaitCursor(self, self.setAvailableForExternal, False)


    @QtCore.pyqtSlot(int, int)
    def on_calendar_currentPageChanged(self, year, month):
        selectedDate = self.calendar.selectedDate()
        currYear = selectedDate.year()
        currMonth = selectedDate.month()
        newDate = selectedDate.addMonths((year-currYear)*12+(month-currMonth))
        self.calendar.setSelectedDate(newDate)
        self.setDateInTable(newDate, True)
        if self.activityListIsShown:
            self.updatePersonListByActivity()
        else:
            self.updatePersonListByOrgStructure()


    @QtCore.pyqtSlot()
    def on_calendar_selectionChanged(self):
        selectedDate = self.calendar.selectedDate()
        self.setDateInTable(selectedDate, True)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelOrgStructure_currentChanged(self, current, previous):
        self.updatePersonListByOrgStructure()
        self.setDateInTable(self.calendar.selectedDate(), True)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActivity_currentChanged(self, current, previous):
        self.updatePersonListByActivity()
        self.setDateInTable(self.calendar.selectedDate(), True)


#    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
#    def on_selectionModelPersonnel_currentChanged(self, current, previous):
#         self.setDateInTable(self.calendar.selectedDate(), True)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelPersonnel_currentChanged(self, current, previous):
        self.on_tblPersonnel_clicked(current)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblPersonnel_clicked(self, index):
        selectedRows = []
        rowCount = self.tblPersonnel.model().rowCount()
        for index in self.tblPersonnel.selectedIndexes():
            if index.row() < rowCount:
                row = index.row()
                if row not in selectedRows:
                    selectedRows.append(row)
        if len(selectedRows) > 1:
            self.enabledButtonsForSelected(False)
        else:
            self.enabledButtonsForSelected()
            self.setDateInTable(self.calendar.selectedDate(), True)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTimeTable_currentChanged(self, current, previous):
        row = current.row()
        if 0 <= row < self.modelTimeTable.daysInMonth:
            selectedDate = self.modelTimeTable.begDate.addDays(row)
            self.calendar.setSelectedDate(selectedDate)
            self.modelTimeTable.selectedDate = QtCore.QDate(self.calendar.selectedDate())


    @QtCore.pyqtSlot()
    def on_modelTimeTable_dataChanged(self, topLeft, bottomRight):
        self.labelsUpdate()

    @QtCore.pyqtSlot()
    def on_modelTimeTable_attrsChanged(self):
        self.labelsUpdate()

    def labelsUpdate(self):
        self.modelTimeTable.updateAttrs()
        attrs = self.modelTimeTable.attrs
        self.lblShowNumDays.setText(str(attrs.numDays))
        self.lblShowAbsenceDays.setText(str(attrs.numAbsenceDays))
        self.lblShowAmbDays.setText(str(attrs.numAmbDays))
        self.lblShowHomeDays.setText(str(attrs.numHomeDays))
        self.lblShowExpDays.setText(str(attrs.numExpDays))

        self.lblShowHourLoad.setText(divIfPosible(3600*(attrs.numAmbFact+attrs.numHomeFact+attrs.numExpFact), attrs.numAmbTime+attrs.numHomeTime+attrs.numExpTime))
        self.lblShowServHourLoad.setText(divIfPosible(3600*(attrs.numAmbFact+attrs.numHomeFact), attrs.numAmbTime+attrs.numHomeTime))
        self.lblShowAmbHourLoad.setText(divIfPosible(3600*attrs.numAmbFact, attrs.numAmbTime))
        self.lblShowHomeHourLoad.setText(divIfPosible(3600*attrs.numHomeFact, attrs.numHomeTime))
        self.lblShowExpHourLoad.setText(divIfPosible(3600*attrs.numExpFact, attrs.numExpTime))

        self.lblShowLoad.setText(divIfPosible(attrs.numAmbFact+attrs.numHomeFact+attrs.numExpFact, attrs.numDays))
        self.lblShowServLoad.setText(divIfPosible(attrs.numAmbFact+attrs.numHomeFact, attrs.numServDays))
        self.lblShowAmbLoad.setText(divIfPosible(attrs.numAmbFact, attrs.numAmbDays))
        self.lblShowHomeLoad.setText(divIfPosible(attrs.numHomeFact, attrs.numHomeDays))
        self.lblShowExpLoad.setText(divIfPosible(attrs.numExpFact, attrs.numExpDays))

        self.lblShowExec.setText(divIfPosible(100*(attrs.numAmbFact+attrs.numHomeFact+attrs.numExpFact), attrs.numAmbPlan+attrs.numHomePlan+attrs.numExpPlan))
        self.lblShowServExec.setText(divIfPosible(100*(attrs.numAmbFact+attrs.numHomeFact), attrs.numAmbPlan+attrs.numHomePlan))
        self.lblShowAmbExec.setText(divIfPosible(100*(attrs.numAmbFact), attrs.numAmbPlan))
        self.lblShowHomeExec.setText(divIfPosible(100*(attrs.numHomeFact), attrs.numHomePlan))
        self.lblShowExpExec.setText(divIfPosible(100*(attrs.numExpFact), attrs.numExpPlan))


    @QtCore.pyqtSlot()
    def on_actFillByTemplate_triggered(self):
        self.fillByTemplate()


    @QtCore.pyqtSlot()
    def on_actFillTemplate_triggered(self):
        self.fillByTemplate()


    @QtCore.pyqtSlot()
    def on_actFillPerson_triggered(self):
        self.fillByPerson()


    @QtCore.pyqtSlot()
    def on_actFillTemplateOnRotation_triggered(self):
        self.fillByTemplateOnRotation()


    @QtCore.pyqtSlot()
    def on_actPlanNumbers_triggered(self):
        self.getPlanNumbersDialog()

    @QtCore.pyqtSlot()
    def on_actRecountNumbers_triggered(self):
        self.recountPlanNumbers()

#    @QtCore.pyqtSlot()
#    def on_btnFill_clicked(self):
#        self.fillByTemplate()

    @QtCore.pyqtSlot()
    def on_btnDubl_clicked(self):
        personId = self.tblPersonnel.currentItemId()
        if not personId:
            return
        if QtGui.QMessageBox.question(
                  self, 
                  u'Внимание!', 
                  u'Вы действительно хотите скопировать график с предыдущего месяца?'
                  + u'\n(Внимание: После выполнения этой операции данные о расписании будут сразу сохранены в базу)', 
                  QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
            return
        dialog = CDublDialog(self)
        model = self.modelTimeTable
        begDate = model.begDate
        monthName=[u'январь', u'февраль', u'март', u'апрель', u'май', u'июнь', u'июль', u'август', u'сентябрь', u'октябрь', u'ноябрь', u'декабрь'][begDate.month()-1]
        prevBegDate = begDate.addMonths(-1)
        prevMonthName=[u'января', u'февраля', u'марта', u'апреля', u'мая', u'июня', u'июля', u'августа', u'сентября', u'октября', u'ноября', u'декабря'][prevBegDate.month()-1]
        msg=u'Выберите режим копирования для выполнения дублирования графика с '+prevMonthName+u' на '+monthName
        dialog.textBrowser.setText(msg)
        prevBegDate = begDate.addMonths(-1)
        dialog.edtStart.setDate(prevBegDate)
        if dialog.exec_():
            self.dubl(personId, dialog)

    def dubl(self, personId, dialog):
        model = self.modelTimeTable
        begDate = model.begDate
        daysInMonth = model.daysInMonth
        endDate = begDate.addDays(daysInMonth-1)
        dow = begDate.dayOfWeek()
        prevBegDate = begDate.addMonths(-1)
        if dialog.chkStart.isChecked():
            prevBegDate=dialog.edtStart.date()
        prevDaysInMonth = prevBegDate.daysInMonth()
        prevEdDate = prevBegDate.addDays(prevDaysInMonth-1)
        prevDow = prevBegDate.dayOfWeek()
        prevDay = prevBegDate.day()

        def mk_copy(d1, d2):
            db = QtGui.qApp.db
            eventTable = db.table('Event')

            db.transaction()
            try:
                # load
                tableModel = CTimeTableModel(self)
                dayInfo = [ None ] * CTimeTableModel.numCols
                dayInfo[CTimeTableModel.ciReasonOfAbsence] = model.items[d2.day()][CTimeTableModel.ciReasonOfAbsence]
                event = getEvent(constants.etcTimeTable, d1, personId)
                eventId = forceRef(event.value('id'))
                if not eventId:
                    return

                actionAmbulance = CAction.getAction(eventId, constants.atcAmbulance)
                oldVersion = True if (len(actionAmbulance['times']) == actionAmbulance['plan']) else False
                begTime = actionAmbulance['begTime']
                endTime = actionAmbulance['endTime']
                if begTime and endTime:
                    dayInfo[CTimeTableModel.ciAmbTimeRange] = (begTime, endTime)
                else:
                    dayInfo[CTimeTableModel.ciAmbTimeRange] = None
                dayInfo[CTimeTableModel.ciAmbOffice] = actionAmbulance['office']
                # dayInfo[CTimeTableModel.ciAmbPlan] = actionAmbulance['plan']
                dayInfo[CTimeTableModel.ciAmbPlan] = len(actionAmbulance['times'])
                if oldVersion:
                    dayInfo[CTimeTableModel.ciAmbInterval] = tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange], len(actionAmbulance['times'])) if not actionAmbulance['plan'] else tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange], actionAmbulance['plan']) if not actionAmbulance['plan1'] else setInterval(tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange1], actionAmbulance['plan1']), tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange2], actionAmbulance['plan2']), tableModel.conversion(tableModel.getOutTurnTime(dayInfo[CTimeTableModel.ciAmbTimeRange1], dayInfo[CTimeTableModel.ciAmbTimeRange2]), actionAmbulance['planInter']))
                else:
                   dayInfo[CTimeTableModel.ciAmbInterval] = tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange], len(actionAmbulance['times'])) if not actionAmbulance['plan'] else actionAmbulance['plan'] if not actionAmbulance['plan1'] else setInterval(actionAmbulance['plan1'], actionAmbulance['plan2'], actionAmbulance['planInter'])

                begTime1 = actionAmbulance['begTime1']
                endTime1 = actionAmbulance['endTime1']
                if begTime1 and endTime1:
                    dayInfo[CTimeTableModel.ciAmbTimeRange1] = (begTime1, endTime1)
                else:
                    dayInfo[CTimeTableModel.ciAmbTimeRange1] = None
                dayInfo[CTimeTableModel.ciAmbOffice1] = actionAmbulance['office1']
                dayInfo[CTimeTableModel.ciAmbInterOffice] = actionAmbulance['officeInter']
                # dayInfo[CTimeTableModel.ciAmbPlan1] = actionAmbulance['plan1']
                dayInfo[CTimeTableModel.ciAmbPlan1] = actionAmbulance['plan1'] if oldVersion else tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange1], actionAmbulance['plan1'])
                dayInfo[CTimeTableModel.ciAmbInterval1] = tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange1], actionAmbulance['plan1']) if oldVersion else actionAmbulance['plan1']
                # dayInfo[CTimeTableModel.ciAmbInterPlan] = actionAmbulance['planInter']

                begTime2 = actionAmbulance['begTime2']
                endTime2 = actionAmbulance['endTime2']
                if begTime2 and endTime2:
                    dayInfo[CTimeTableModel.ciAmbTimeRange2] = (begTime2, endTime2)
                else:
                    dayInfo[CTimeTableModel.ciAmbTimeRange2] = None
                dayInfo[CTimeTableModel.ciAmbOffice2] = actionAmbulance['office2']
                # dayInfo[CTimeTableModel.ciAmbPlan2] = actionAmbulance['plan2']
                dayInfo[CTimeTableModel.ciAmbPlan2] = actionAmbulance['plan2'] if oldVersion else tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange2], actionAmbulance['plan2'])
                dayInfo[CTimeTableModel.ciAmbInterval2] = tableModel.conversion(dayInfo[CTimeTableModel.ciAmbTimeRange2], actionAmbulance['plan2']) if oldVersion else actionAmbulance['plan2']

                dayInfo[CTimeTableModel.ciAmbInterPlan] = tableModel.conversion((endTime1, begTime2) if endTime1 and begTime2 else None, actionAmbulance['planInter'])

                actionHome = CAction.getAction(eventId, constants.atcHome)
                oldVersion = True if (len(actionHome['times']) == actionHome['plan']) else False
                begTime = actionHome['begTime']
                endTime = actionHome['endTime']
                if begTime and endTime:
                    dayInfo[CTimeTableModel.ciHomeTimeRange] = (begTime, endTime)
                else:
                    dayInfo[CTimeTableModel.ciHomeTimeRange] = None
                # dayInfo[CTimeTableModel.ciHomePlan] = actionHome['plan']
                dayInfo[CTimeTableModel.ciHomePlan] = len(actionHome['times'])
                if oldVersion:
                    dayInfo[CTimeTableModel.ciHomeInterval] = tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange], len(actionHome['times'])) if not actionHome['plan'] else tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange], actionHome['plan']) if not actionHome['plan1'] else  setInterval(tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange1], actionHome['plan1']), tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange2], actionHome['plan2']))
                else:
                    dayInfo[CTimeTableModel.ciHomeInterval] = tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange], len(actionHome['times'])) if not actionHome['plan'] else actionHome['plan'] if not actionHome['plan1'] else setInterval(actionHome['plan1'], actionHome['plan2'])

                begTime1 = actionHome['begTime1']
                endTime1 = actionHome['endTime1']
                if begTime1 and endTime1:
                    dayInfo[CTimeTableModel.ciHomeTimeRange1] = (begTime1, endTime1)
                else:
                    dayInfo[CTimeTableModel.ciHomeTimeRange1] = None
                # dayInfo[CTimeTableModel.ciHomePlan1] = actionHome['plan1']
                dayInfo[CTimeTableModel.ciHomePlan1] = actionHome['plan1'] if oldVersion else tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange1], actionHome['plan1'] if actionHome['plan1'] else len(actionHome['times']))
                dayInfo[CTimeTableModel.ciHomeInterval1] = tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange1], actionHome['plan1']) if oldVersion else  actionHome['plan1']
                begTime2 = actionHome['begTime2']
                endTime2 = actionHome['endTime2']
                if begTime2 and endTime2:
                    dayInfo[CTimeTableModel.ciHomeTimeRange2] = (begTime2, endTime2)
                else:
                    dayInfo[CTimeTableModel.ciHomeTimeRange2] = None
                # dayInfo[CTimeTableModel.ciHomePlan2] = actionHome['plan2']
                dayInfo[CTimeTableModel.ciHomePlan2] = actionHome['plan2'] if oldVersion else tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange2], actionHome['plan2'])
                dayInfo[CTimeTableModel.ciHomeInterval2] = tableModel.conversion(dayInfo[CTimeTableModel.ciHomeTimeRange2], actionHome['plan2']) if oldVersion else actionHome['plan2']

                actionExp = CAction.getAction(eventId, constants.atcExp)
                begTime = actionExp['begTime']
                endTime = actionExp['endTime']
                if begTime and endTime:
                    dayInfo[CTimeTableModel.ciExpTimeRange] = (begTime, endTime)
                else:
                    dayInfo[CTimeTableModel.ciExpTimeRange] = None
                dayInfo[CTimeTableModel.ciExpOffice] = actionExp['office']
                dayInfo[CTimeTableModel.ciExpPlan] = actionExp['plan']

                # save
                event = getEvent(constants.etcTimeTable, d2, personId)
                eventId = db.insertOrUpdate(eventTable, event)
                if not eventId:
                    return

                if actionAmbulance:
                    actionAmbulance = CAction.getAction(eventId, constants.atcAmbulance)
                    timeRange = dayInfo[CTimeTableModel.ciAmbTimeRange]
                    if timeRange:
                        actionAmbulance['begTime'], actionAmbulance['endTime'] = timeRange
                    else:
                        del actionAmbulance['begTime']
                        del actionAmbulance['endTime']
                    actionAmbulance['office'] = dayInfo[CTimeTableModel.ciAmbOffice]
                    # actionAmbulance['plan'] = dayInfo[CTimeTableModel.ciAmbPlan]
                    actionAmbulance['plan'] = dayInfo[CTimeTableModel.ciAmbInterval]

                    timeRange1 = dayInfo[CTimeTableModel.ciAmbTimeRange1]
                    if timeRange1:
                        actionAmbulance['begTime1'], actionAmbulance['endTime1'] = timeRange1
                    else:
                        del actionAmbulance['begTime1']
                        del actionAmbulance['endTime1']
                    actionAmbulance['office1'] = dayInfo[CTimeTableModel.ciAmbOffice1]
                    actionAmbulance['officeInter'] = dayInfo[CTimeTableModel.ciAmbInterOffice]
                    # actionAmbulance['plan1']   = dayInfo[CTimeTableModel.ciAmbPlan1]
                    actionAmbulance['plan1']   = dayInfo[CTimeTableModel.ciAmbInterval1]
                    # actionAmbulance['planInter'] = dayInfo[CTimeTableModel.ciAmbInterPlan]
                    actionAmbulance['planInter'] = dayInfo[CTimeTableModel.ciAmbInterInterval]
                    timeRange2 = dayInfo[CTimeTableModel.ciAmbTimeRange2]
                    if timeRange2:
                        actionAmbulance['begTime2'], actionAmbulance['endTime2'] = timeRange2
                    else:
                        del actionAmbulance['begTime2']
                        del actionAmbulance['endTime2']
                    actionAmbulance['office2'] = dayInfo[CTimeTableModel.ciAmbOffice2]
                    # actionAmbulance['plan2']   = dayInfo[CTimeTableModel.ciAmbPlan2]
                    actionAmbulance['plan2']   = dayInfo[CTimeTableModel.ciAmbInterval2]
                    actionAmbulance['fact']   = dayInfo[CTimeTableModel.ciAmbFact]
                    actionAmbulance['time']   = dayInfo[CTimeTableModel.ciAmbTime]
                    if timeRange1 and timeRange2:
                        # result  = calcTimePlan(timeRange1, dayInfo[CTimeTableModel.ciAmbPlan1], personId, True, result = [])
                        # result  = calcTimePlan(timeRange2, dayInfo[CTimeTableModel.ciAmbPlan2], personId, True, result)
                        result = calcTimeInterval(timeRange1, dayInfo[CTimeTableModel.ciAmbPlan1], dayInfo[CTimeTableModel.ciAmbInterval1], personId, True, result = [])
                        result = calcTimeInterval(timeRange2, dayInfo[CTimeTableModel.ciAmbPlan2], dayInfo[CTimeTableModel.ciAmbInterval2], personId, True, result)
                        actionAmbulance['times'] = result
                    else:
                        # actionAmbulance['times']  = calcTimePlan(timeRange, dayInfo[CTimeTableModel.ciAmbPlan], personId, True, result = [])
                       actionAmbulance['times'] = calcTimeInterval(timeRange, dayInfo[CTimeTableModel.ciAmbPlan], dayInfo[CTimeTableModel.ciAmbInterval], personId, True, result = [])
                    actionAmbulance.save(eventId)

                if actionHome:
                    actionHome = CAction.getAction(eventId, constants.atcHome)
                    timeRange = dayInfo[CTimeTableModel.ciHomeTimeRange]
                    if timeRange:
                        actionHome['begTime'], actionHome['endTime'] = timeRange
                    else:
                        del actionHome['begTime']
                        del actionHome['endTime']
                    # actionHome['plan'] = dayInfo[CTimeTableModel.ciHomePlan]
                    actionHome['plan'] = dayInfo[CTimeTableModel.ciHomeInterval]
                    timeRange1 = dayInfo[CTimeTableModel.ciHomeTimeRange1]
                    if timeRange1:
                        actionHome['begTime1'], actionHome['endTime1'] = timeRange1
                    else:
                        del actionHome['begTime1']
                        del actionHome['endTime1']
                    # actionHome['plan1'] = dayInfo[CTimeTableModel.ciHomePlan1]
                    actionHome['plan1'] = dayInfo[CTimeTableModel.ciHomeInterval1]
                    timeRange2 = dayInfo[CTimeTableModel.ciHomeTimeRange2]
                    if timeRange2:
                        actionHome['begTime2'], actionHome['endTime2'] = timeRange2
                    else:
                        del actionHome['begTime2']
                        del actionHome['endTime2']
                    # actionHome['plan2'] = dayInfo[CTimeTableModel.ciHomePlan2]
                    actionHome['plan2'] = dayInfo[CTimeTableModel.ciHomeInterval2]
                    actionHome['fact']   = dayInfo[CTimeTableModel.ciHomeFact]
                    actionHome['time']   = dayInfo[CTimeTableModel.ciHomeTime]
                    if timeRange1 and timeRange2:
                        # result  = calcTimePlan(timeRange1, dayInfo[CTimeTableModel.ciHomePlan1], personId, False, result = [])
                        # result  = calcTimePlan(timeRange2, dayInfo[CTimeTableModel.ciHomePlan2], personId, False, result)
                        result = calcTimeInterval(timeRange1, dayInfo[CTimeTableModel.ciHomePlan1], dayInfo[CTimeTableModel.ciHomeInterval1], personId, True, result = [])
                        result = calcTimeInterval(timeRange2, dayInfo[CTimeTableModel.ciHomePlan2], dayInfo[CTimeTableModel.ciHomeInterval2], personId, True, result)
                        actionHome['times'] = result
                    else:
                        #actionHome['times'] = calcTimePlan(timeRange, dayInfo[CTimeTableModel.ciHomePlan], personId, False, result = [])
                        actionHome['times'] = calcTimeInterval(timeRange, dayInfo[CTimeTableModel.ciHomePlan], dayInfo[CTimeTableModel.ciHomeInterval], personId, True, result = [])
                    actionHome.save(eventId)

                if actionExp:
                    actionExp = CAction.getAction(eventId, constants.atcExp)
                    timeRange = dayInfo[CTimeTableModel.ciExpTimeRange]
                    if timeRange:
                        actionExp['begTime'], actionExp['endTime'] = timeRange
                    else:
                        del actionExp['begTime']
                        del actionExp['endTime']
                    actionExp['office'] = dayInfo[CTimeTableModel.ciExpOffice]
                    actionExp['plan'] = dayInfo[CTimeTableModel.ciExpPlan]
                    actionExp['times'] = calcTimePlan(timeRange, dayInfo[CTimeTableModel.ciExpPlan], personId, True)
                    actionExp.save(eventId)

                if dayInfo[CTimeTableModel.ciReasonOfAbsence]:
                    actionTimeLine = CAction.getAction(eventId, constants.atcTimeLine)
                    actionTimeLine['reasonOfAbsence'] = dayInfo[CTimeTableModel.ciReasonOfAbsence]
                    actionTimeLine.save(eventId)

                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise

        if dialog.rbSingle.isChecked():
            prevDay1= 0 if prevDow not in [6, 7] else 2
            d1=prevBegDate.addDays(prevDay1)
            for d in range(0, daysInMonth):
                day=begDate.addDays(d)
                mk_copy(d1, day)
        if dialog.rbDual.isChecked():
            prevDay1= 0 if prevDow not in [6, 7] else 2
            d1=prevBegDate.addDays(prevDay1)
            prevDay2= 1 if prevDow not in [5, 6] else 3
            d2=prevBegDate.addDays(prevDay2)
            for d in range(0, daysInMonth):
                day=begDate.addDays(d)
                if day.dayOfWeek()<6:
                    if (d%2):
                        mk_copy(d2, day)
                    else:
                        mk_copy(d1, day)
        if dialog.rbWeek.isChecked():
            for d in range(1, 8):
                day = d-dow+(0 if d>=dow else 7)
                prevDay = d-prevDow+(0 if d>=prevDow else 7)
                d1=prevBegDate.addDays(prevDay)
                for x in [0, 7, 14, 21, 28]:
                    day2 = day+x
                    if day2<=daysInMonth:
                        mk_copy(d1, begDate.addDays(day2))
        model.loadData(personId, begDate.year(), begDate.month())
        for column in xrange(CTimeTableModel.numCols):
            model.updateSums(column, False)
        self.labelsUpdate()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblPersonnel_doubleClicked(self, current):
        personId = self.tblPersonnel.currentItemId()
        if personId and (QtGui.qApp.userHasRight(urAdmin) or QtGui.qApp.userHasRight(urAccessRefPersonPersonal)):
            dialog = CRBPersonEditor(self)
            dialog.load(personId)
            dialog.exec_()


    @QtCore.pyqtSlot()
    def on_btnSum_clicked(self):
        if not self.tblPersonnel.currentItemId():
            return
        if QtGui.QMessageBox.question(self, u'Внимание!', u'Вы действительно хотите заполнить суммарное время на все дни месяца?', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
            return
        self.modelTimeTable.fillSum()
        self.setIsDirty(True)


    @QtCore.pyqtSlot()
    def on_btnFact_clicked(self):
        if not self.tblPersonnel.currentItemId():
            return
        if QtGui.QMessageBox.question(self, u'Внимание!', u'Вы действительно хотите заполнить фактическое время на все дни месяца?', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
            return
        self.modelTimeTable.fillFact()
        self.labelsUpdate()
        self.setIsDirty(True)


    def setupPrintMenu(self):
        self.mnuPrint = QtGui.QMenu(self)
        self.mnuPrint.setObjectName('mnuPrint')
        self.actPrintPerson = QtGui.QAction(u'Индивидуальный табель', self)
        self.actPrintPerson.setObjectName('actPrintPerson')
        self.actPrintPersons = QtGui.QAction(u'Общий табель', self)
        self.actPrintPersons.setObjectName('actPrintPersons')
        self.actPrintPersonsAmb = QtGui.QAction(u'Общий табель амбулаторного приёма', self)
        self.actPrintPersonsAmb.setObjectName('actPrintPersonsAmb')
        self.actPrintTimelineForPerson = QtGui.QAction(u'Расписание приёма врача', self)
        self.actPrintTimelineForPerson.setObjectName('actPrintTimelineForPerson')
        self.actPrintTimelineForOffices = QtGui.QAction(u'Расписание кабинетов', self)
        self.actPrintTimelineForOffices.setObjectName('actPrintTimelineForOffices')
        self.mnuPrint.addAction(self.actPrintPerson)
        self.mnuPrint.addAction(self.actPrintPersons)
        self.mnuPrint.addAction(self.actPrintPersonsAmb)
        self.mnuPrint.addSeparator()
        self.mnuPrint.addAction(self.actPrintTimelineForPerson)
        self.mnuPrint.addAction(self.actPrintTimelineForOffices)


    def setupFillMenu(self):
        self.mnuFill = QtGui.QMenu(self)
        self.mnuFill.setObjectName('mnuFill')
        self.actFillTemplate = QtGui.QAction(u'По шаблону', self)
        self.actFillTemplate.setObjectName('actFillTemplate')
        self.actFillTemplateOnRotation = QtGui.QAction(u'По шаблону "скользящий график"', self)
        self.actFillTemplateOnRotation.setObjectName('actFillTemplateOnRotation')
        self.actFillPerson = QtGui.QAction(u'По персональному графику', self)
        self.actFillPerson.setObjectName('actFillPerson')
        self.mnuFill.addAction(self.actFillTemplate)
        self.mnuFill.addAction(self.actFillTemplateOnRotation)
        self.mnuFill.addAction(self.actFillPerson)


#    @pyqtSlot()
#    def on_mnuPrint_aboutToShow(self):
#        self.actPrintPerson.setEnabled(True)
#        self.actPrintPersons.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_actPrintPerson_triggered(self):
        db = QtGui.qApp.db
        personId = self.tblPersonnel.currentItemId()
        if not personId:
            return
        model = self.modelTimeTable
        begDate = model.begDate
        daysInMonth = model.daysInMonth
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        model = self.modelTimeTable
        begDate = model.begDate
        monthName=[u'январь', u'февраль', u'март', u'апрель', u'май', u'июнь', u'июль', u'август', u'сентябрь', u'октябрь', u'ноябрь', u'декабрь'][begDate.month()-1]
        cursor.insertText(u'Табель на %s %d г.' % (monthName, begDate.year()))
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportBody)
        personInfo = getPersonInfo(personId)
        orgStructure_id = forceInt(db.translate('Person', 'id', personId, 'orgStructure_id'))
        orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
        cursor.insertText(u'врач: %s, %s\n' % (personInfo['fullName'], personInfo['specialityName']))
        cursor.insertText(u'подразделение: %s, %s\n' % (orgStructureName, personInfo['postName']))
        cursor.insertText(u'дата формирования: %s\n' % QtCore.QDate.currentDate().toString('dd.MM.yyyy'))
        cursor.insertBlock()

        tableColumns = [
            ('3%', [ u'Число'], CReportBase.AlignRight),
            ('10%', [ u'Амбулаторно'], CReportBase.AlignRight),
            ('3%', [ u'Кабинет'], CReportBase.AlignRight),
            ('3%', [ u'План'], CReportBase.AlignRight),
            ('5%', [ u'ФЧасы'], CReportBase.AlignRight),
            ('5%', [ u'Принято'], CReportBase.AlignRight),
            ('10%', [ u'На дому'], CReportBase.AlignRight),
            ('3%', [ u'План'], CReportBase.AlignRight),
            ('5%', [ u'ФЧасы'], CReportBase.AlignRight),
            ('5%', [ u'Принято'], CReportBase.AlignRight),
            ('10%', [ u'КЭР'], CReportBase.AlignRight),
            ('3%', [ u'Кабинет'], CReportBase.AlignRight),
            ('3%', [ u'План'], CReportBase.AlignRight),
            ('5%', [ u'ФЧасы'], CReportBase.AlignRight),
            ('5%', [ u'Принято'], CReportBase.AlignRight),
            ('5%', [ u'Прочее'], CReportBase.AlignRight),
            ('5%', [ u'Табель'], CReportBase.AlignRight),
            ('10%', [ u'Причина отсутствия'], CReportBase.AlignRight),
                       ]
        table = createTable(cursor, tableColumns)

        for d in range(0, daysInMonth+1):
            i = table.addRow()
            table.setText(i, 0, str(d+1) if d<daysInMonth else u'Всего')
            for n in xrange(len(tableColumns)-1):
                index = model.createIndex(d, n)
                text = forceString(model.data(index))
                table.setText(i, n+1, text)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()

        rows = []
        for i in range(5):
            rows.append([None]*4)

        rows[0][0]=u'Количество дней: '+(self.lblShowNumDays.text())
        rows[1][0]=u'Дней с отсутствием: '+self.lblShowAbsenceDays.text()
        rows[2][0]=u'Дней на приёме: '+self.lblShowAmbDays.text()
        rows[3][0]=u'Дней на вызовах: '+self.lblShowHomeDays.text()
        rows[4][0]=u'Дней на КЭР: '+self.lblShowExpDays.text()
        rows[0][1]=u'Среднечасовая нагрузка: '+self.lblShowHourLoad.text()
        rows[1][1]=u'на обслуживании '+self.lblShowServHourLoad.text()
        rows[2][1]=u'СН на приёме: '+self.lblShowAmbHourLoad.text()
        rows[3][1]=u'СН на вызовах: '+self.lblShowHomeHourLoad.text()
        rows[4][1]=u'СН на КЭР: '+self.lblShowExpHourLoad.text()
        rows[0][2]=u'Средняя подушевая нагрузка: '+self.lblShowLoad.text()
        rows[1][2]=u'на обслуживании '+self.lblShowServLoad.text()
        rows[2][2]=u'СПН на приёме: '+self.lblShowAmbLoad.text()
        rows[3][2]=u'СПН на вызовах: '+self.lblShowHomeLoad.text()
        rows[4][2]=u'СПН на КЭР: '+self.lblShowExpLoad.text()
        rows[0][3]=u'Выполнение плана: '+self.lblShowExec.text()
        rows[1][3]=u'на обслуживании '+self.lblShowServExec.text()
        rows[2][3]=u'ВП на приёме: '+self.lblShowAmbExec.text()
        rows[3][3]=u'ВП на вызовах: '+self.lblShowHomeExec.text()
        rows[4][3]=u'ВП на КЭР: '+self.lblShowExpExec.text()

        columnDescrs = [('25%', [], CReportBase.AlignLeft)]*4
        table1 = createTable (
            cursor, columnDescrs, headerRowCount=len(rows), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(rows):
            for j in range(4):
                table1.setText(i, j, row[j])
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        html = doc.toHtml(QtCore.QByteArray('utf-8'))
        view = CReportViewDialog(self)
        view.setWindowTitle(u'Табель')
        view.setText(html)
        view.exec_()


    @QtCore.pyqtSlot()
    def on_actPrintPersons_triggered(self):
        db = QtGui.qApp.db
        personIdList=self.modelPersonnel.idList()
        model = self.modelTimeTable
        begDate = model.begDate
        daysInMonth = model.daysInMonth
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        model = self.modelTimeTable
        begDate = model.begDate
        monthName=[u'январь', u'февраль', u'март', u'апрель', u'май', u'июнь', u'июль', u'август', u'сентябрь', u'октябрь', u'ноябрь', u'декабрь'][begDate.month()-1]
        cursor.insertText(u'Табель на %s %d г.' % (monthName, begDate.year()))
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportBody)
        treeIndex = self.treeOrgStructure.currentIndex()
        if treeIndex.isValid():
            treeItem = treeIndex.internalPointer()
            def getOrgNames(orgStructure_id):
                if not orgStructure_id:
                    return []
                orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
                parent_id=forceInt(db.translate('OrgStructure', 'id', orgStructure_id, 'parent_id'))
                return getOrgNames(parent_id)+[orgStructureName]
            orgNames=getOrgNames(treeItem.id())
            if orgNames:
                cursor.insertText(u'подразделение: '+u', '.join(orgNames)+u'\n')
        cursor.insertText(u'дата формирования: %s\n' % QtCore.QDate.currentDate().toString('dd.MM.yyyy'))
        cursor.insertBlock()

        reasonOfAbsenceList=db.getRecordList('rbReasonOfAbsence', 'code, name', '1', 'id')
        reasonOfAbsenceNum=len(reasonOfAbsenceList)
        reasonOfAbsenceCodeList=[forceString(x.value('code')) for x in reasonOfAbsenceList]
        reasonOfAbsenceNameList=[forceString(x.value('name')) for x in reasonOfAbsenceList]
        reasonOfAbsenceCodeList.append(u'Д')
        reasonOfAbsenceNameList.append(u'Другие причины')

        f = QtGui.QTextCharFormat()
        f.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(-6));
#        cursor.setCharFormat(f)
        tableColumns = [('3%', [u'№ п.п'], CReportBase.AlignRight)]
        tableColumns.append(('7%', [ u'врач'], CReportBase.AlignRight))
        tableColumns.append(('7%', [ u'должность'], CReportBase.AlignRight))
        for d in range(daysInMonth):
            tableColumns.append(('2.4%', [str(d+1)], CReportBase.AlignRight))
        tableColumns.append(('3%', [u'всего часы'], CReportBase.AlignRight))
        tableColumns.append(('2%', [u'факт. дни'], CReportBase.AlignRight))
        tableColumns.append(('3%', [u'табельный номер'], CReportBase.AlignRight))
#        tableColumns.append(('2%', [u'дни неявки'], CReportBase.AlignRight))
        for reasonOfAbsenceCode in reasonOfAbsenceCodeList:
            tableColumns.append(('1%', [reasonOfAbsenceCode], CReportBase.AlignRight))
        table = createTable(cursor, tableColumns)
#        cursor.setCharFormat(f)

        def sec2str(sec):
            minuts = sec//60
            if minuts<600:
                return '%02d:%02d'%(minuts//60, minuts%60)
            else:
                return '%d:%02d'%(minuts//60, minuts%60)

        days_fact_all = 0
#        days_n_all = 0
        days_n_all = [0]*(reasonOfAbsenceNum+1)
        timesum_day = [0]*daysInMonth
        timesum_all = 0
        for personId in personIdList:
#            break
            i = table.addRow()
            table.setText(i,0, i)
            table.setText(i, 1, getPersonInfo(personId)['fullName'], charFormat=f)
            table.setText(i, 2, getPersonInfo(personId)['postName'], charFormat=f)
            timesum=0
            days_fact = 0
#            days_n = 0
            days_n = [0]*(reasonOfAbsenceNum+1)
            for d in range(daysInMonth):
                day=begDate.addDays(d)
                event = getEvent(constants.etcTimeTable, day, personId)
                eventId = forceRef(event.value('id'))
                if not eventId:
                    continue
                actionAmbulance = CAction.getAction(eventId, constants.atcAmbulance)
                actionHome = CAction.getAction(eventId, constants.atcHome)
                actionExp = CAction.getAction(eventId, constants.atcExp)
                if not (actionAmbulance['begTime'] or actionAmbulance['endTime'] or actionHome['begTime'] or actionHome['endTime'] or actionExp['begTime'] or actionExp['endTime']):
                    continue
                action = CAction.getAction(eventId, constants.atcTimeLine)
                factTime = action['factTime']
                if not factTime:
                    reasonOfAbsenceId = action['reasonOfAbsence']
                    if reasonOfAbsenceId:
                        days_n[reasonOfAbsenceId-1]+=1
                        days_n_all[reasonOfAbsenceId-1]+=1
                    else:
                        days_n[reasonOfAbsenceNum]+=1
                        days_n_all[reasonOfAbsenceNum]+=1
#                    days_n+=1
#                    days_n_all+=1
                    continue
                factTimeSec = calcSecondsInTime(factTime)
                timesum += factTimeSec
                timesum_day[d] += factTimeSec
                timesum_all += factTimeSec
                days_fact+=1
                days_fact_all+=1
                table.setText(i, d+1, factTime.toString('HH:mm'), charFormat=f)
            table.setText(i, daysInMonth+3, sec2str(timesum), charFormat=f)
            table.setText(i, daysInMonth+4, days_fact, charFormat=f)
            table.setText(i, daysInMonth+5, getPersonInfo(personId)['code'])
#            table.setText(i, daysInMonth+3, days_n, charFormat=f)
            for x in range(reasonOfAbsenceNum+1):
                table.setText(i, daysInMonth+6+x, days_n[x], charFormat=f)
        i = table.addRow()
        table.setText(i, 1, u'всего')
        for d in range(daysInMonth):
            table.setText(i, d+3, sec2str(timesum_day[d]), charFormat=f)
        table.setText(i, daysInMonth+3, sec2str(timesum_all), charFormat=f)
        table.setText(i, daysInMonth+4, days_fact_all, charFormat=f)
#        table.setText(i, daysInMonth+3, days_n_all, charFormat=f)
        for x in range(reasonOfAbsenceNum+1):
            table.setText(i, daysInMonth+6+x, days_n_all[x], charFormat=f)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'Причины отсутствия:\n')
        for i in range(reasonOfAbsenceNum+1):
            cursor.insertText(reasonOfAbsenceCodeList[i]+' - '+reasonOfAbsenceNameList[i]+'\n')

        html = doc.toHtml(QtCore.QByteArray('utf-8'))
        view = CReportViewDialog(self)
        view.setWindowTitle(u'Табель')
        view.setText(html)
        view.exec_()

    @QtCore.pyqtSlot()
    def on_actPrintPersonsAmb_triggered(self):
        db = QtGui.qApp.db
        personIdList=self.modelPersonnel.idList()
        model = self.modelTimeTable
        begDate = model.begDate
        daysInMonth = model.daysInMonth
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)


        model = self.modelTimeTable
        begDate = model.begDate
        monthName=[u'январь', u'февраль', u'март', u'апрель', u'май', u'июнь', u'июль', u'август', u'сентябрь', u'октябрь', u'ноябрь', u'декабрь'][begDate.month()-1]
        orgNames = u''
        treeIndex = self.treeOrgStructure.currentIndex()
        if treeIndex.isValid():
            treeItem = treeIndex.internalPointer()
            def getOrgNames(orgStructure_id):
                if not orgStructure_id:
                    return []
                orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
                parent_id=forceInt(db.translate('OrgStructure', 'id', orgStructure_id, 'parent_id'))
                return getOrgNames(parent_id)+[orgStructureName]
            orgNames=getOrgNames(treeItem.id())
            if orgNames:
                orgNames = u', '.join(orgNames)

        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'ФГБУ "НИИ онкологии им. Н.Н. Петрова" Минздрава России')
        cursor.insertBlock(CReportBase.AlignRight)
        cursor.insertText(u'Утверждаю')
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'ГРАФИК РАБОТЫ ПЕРСОНАЛА\n')
        if orgNames:
            cursor.insertText(u''.join([u''.join([u'_'] * (forceInt(len(orgNames) - 100))), orgNames, u''.join([u''.join([u'_'] * (forceInt(len(orgNames) - 100)))])]))
        else:
            cursor.insertText(u'____________________________________________________________________________')
        cursor.insertBlock(CReportBase.AlignRight)
        chief = getOrganisationMainStaff(QtGui.qApp.currentOrgId())[0]
        cursor.insertText(u'Директор        %s' % chief if chief else u'(не указано в настройках организации)')

        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'на %s месяц %s года' % (monthName, begDate.year()))
        cursor.insertBlock(CReportBase.AlignRight)
        cursor.insertText(u'Дата %s' % QtCore.QDate.currentDate().toString('dd.MM.yyyy'))
        cursor.insertBlock()


        f = QtGui.QTextCharFormat()
        f.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(-6));
#        cursor.setCharFormat(f)
        tableColumns = [('1%', [u'№ п/п'], CReportBase.AlignRight)]
        tableColumns.append(('7%', [ u'Фамилия, имя, отчество'], CReportBase.AlignRight))
        tableColumns.append(('7%', [ u'Должность'], CReportBase.AlignRight))
        tableColumns.append(('2.4%', [ u'Числа месяца', u'1'], CReportBase.AlignRight))
        for d in range(1, daysInMonth):
            tableColumns.append(('2.4%', ['', str(d+1)], CReportBase.AlignRight))
        tableColumns.append(('3%', [u'кол-во смен'], CReportBase.AlignRight))
        tableColumns.append(('3%', [u'кол-во часов'], CReportBase.AlignRight))
        tableColumns.append(('6%', [u'из них', u'ночь'], CReportBase.AlignRight))
        tableColumns.append(('3%', [u'', u'праздн'], CReportBase.AlignRight))
        tableColumns.append(('3%', [u'Подпись'], CReportBase.AlignRight))

        table = createTable(cursor, tableColumns)
#        cursor.setCharFormat(f)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, daysInMonth)
        table.mergeCells(0, 3 + daysInMonth, 2, 1)
        table.mergeCells(0, 4 + daysInMonth, 2, 1)
        table.mergeCells(0, 5 + daysInMonth, 1, 2)
        table.mergeCells(0, 7 + daysInMonth, 2, 1)

        def sec2str(sec):
            minuts = sec//60
            if minuts<600:
                return '%02d:%02d'%(minuts//60, minuts%60)
            else:
                return '%d:%02d'%(minuts//60, minuts%60)

        def countNigthWorkTime(begTime, endTime):
            nightWorkTime = 0
            if begTime >= QtCore.QTime(22, 0):
                if endTime <= QtCore.QTime(8, 0) or endTime > QtCore.QTime(22, 0):
                    nightWorkTime = begTime.secsTo(endTime) % (24 * 60 * 60)
                elif endTime > QtCore.QTime(8, 0):
                    nightWorkTime = begTime.secsTo(QtCore.QTime(8, 0)) % (24 * 60 * 60)
            if begTime < QtCore.QTime(8, 0):
                if endTime <= QtCore.QTime(8, 0):
                    nightWorkTime = begTime.secsTo(endTime) % (24 * 60 * 60)
                elif endTime <= QtCore.QTime(22, 0):
                    nightWorkTime = begTime.secsTo(QtCore.QTime(8, 0)) % (24 * 60 * 60)
                elif endTime > QtCore.QTime(22, 0):
                    nightWorkTime = begTime.secsTo(QtCore.QTime(8, 0)) % (24 * 60 * 60) + QtCore.QTime(22, 0).secsTo(endTime)
            return nightWorkTime

        def countHolidayWorkTime(begTime, endTime, day):
            holidayWorkTimeSec = 0
            for holiday in QtGui.qApp.calendarInfo.holiday_list:
                if holiday.has(day):
                    if endTime < begTime:
                        holidayWorkTimeSec += begTime.secsTo(QtCore.QTime(0, 0)) % (24 * 60 * 60)
                    else:
                        holidayWorkTimeSec += begTime.secsTo(endTime) % (24 * 60 * 60)
                if holiday.has(day.addDays(1)) and endTime < begTime:
                    holidayWorkTimeSec += QtCore.QTime(0, 0).secsTo(endTime) % (24 * 60 * 60)
            return holidayWorkTimeSec


        timesum_all = 0
        for personId in personIdList:
            i = table.addRow()
            table.addRow()
            table.setText(i,0, i)
            table.setText(i, 1, getPersonInfo(personId)['fullName'], charFormat=f)
            table.setText(i, 2, getPersonInfo(personId)['postName'], charFormat=f)
            table.mergeCells(i, 0, 2, 1)
            table.mergeCells(i, 1, 2, 1)
            table.mergeCells(i, 2, 2, 1)
            timesum=0
            night_timesum = 0
            holiday_timesum = 0
            workDays = 0
            for d in range(daysInMonth):
                day=begDate.addDays(d)
                event = getEvent(constants.etcTimeTable, day, personId)
                eventId = forceRef(event.value('id'))
                if not eventId:
                    continue
                actionAmbulance = CAction.getAction(eventId, constants.atcAmbulance)
                if not (actionAmbulance['begTime'] or actionAmbulance['endTime']):
                    continue
                begTime = actionAmbulance['begTime']
                endTime = actionAmbulance['endTime']

                action = CAction.getAction(eventId, constants.atcTimeLine)
                reasonOfAbsenceId = action['reasonOfAbsence']
                if reasonOfAbsenceId:
                    continue
                begTime1 = actionAmbulance['begTime1']
                endTime1 = actionAmbulance['endTime1']
                begTime2 = actionAmbulance['begTime2']
                endTime2 = actionAmbulance['endTime2']

                if begTime1 and begTime2 and endTime1 and endTime2:  # begTime1 or begTime2 or endTime1 or endTime2:
                    workTimeSec = begTime1.secsTo(endTime1) % (24 * 60 * 60) + begTime2.secsTo(endTime2) % (24 * 60 * 60)
                    nightWorkTimeSec = countNigthWorkTime(begTime1, endTime1) + countNigthWorkTime(begTime2, endTime2)
                    holidayWorkTimeSec = countHolidayWorkTime(begTime1, endTime1, day) + countHolidayWorkTime(begTime2, endTime2, day)
                    table.setText(i, d+3, u'%s - %s' % (begTime1.toString('HH:mm'), endTime1.toString('HH:mm')), charFormat=f)
                    table.setText(i+1, d+3, u'%s - %s' % (begTime2.toString('HH:mm'), endTime2.toString('HH:mm')), charFormat=f)
                else:
                    workTimeSec = begTime.secsTo(endTime) % (24 * 60 * 60)
                    nightWorkTimeSec = countNigthWorkTime(begTime, endTime)
                    holidayWorkTimeSec = countHolidayWorkTime(begTime, endTime, day)
                    table.setText(i, d+3, u'%s - %s' % (begTime.toString('HH:mm'), endTime.toString('HH:mm')), charFormat=f)
                timesum += workTimeSec
                timesum_all += workTimeSec
                night_timesum += nightWorkTimeSec
                holiday_timesum += holidayWorkTimeSec
                workDays += workTimeSec / 28800 + forceInt(bool(workTimeSec % 28800))
            table.setText(i, daysInMonth+3, workDays, charFormat=f)
            table.setText(i, daysInMonth+4, sec2str(timesum), charFormat=f)
            table.setText(i, daysInMonth+5, sec2str(night_timesum), charFormat=f)
            table.setText(i, daysInMonth+6, sec2str(holiday_timesum), charFormat=f)
            table.mergeCells(i, daysInMonth+3, 2, 1)
            table.mergeCells(i, daysInMonth+4, 2, 1)
            table.mergeCells(i, daysInMonth+5, 2, 1)
            table.mergeCells(i, daysInMonth+6, 2, 1)
            table.mergeCells(i, daysInMonth+7, 2, 1)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'Время обозначается в 24-часовом исполнении')
        cursor.insertBlock(CReportBase.AlignRight)
        cursor.insertText(u'Итого: %s' % sec2str(timesum_all))
        cursor.insertBlock(CReportBase.AlignLeft)
        cursor.insertText(u'Руководитель подразделения ________________  _______________________       Специалист ОК ________________  _______________________\n')
        cursor.insertText(u'                                                   (подпись)            (расшифровка подписи)                                      (подпись)           (расшифровка подписи)\n')
        cursor.insertText(u'Исполнитель _______________  ________________  _______________________       <<___>>  ______________ %s\n' % begDate.year())
        cursor.insertText(u'                       (должность)             (подпись)          (расшифровка подписи)\n')


        html = doc.toHtml(QtCore.QByteArray('utf-8'))
        view = CReportViewDialog(self)
        view.setWindowTitle(u'Табель')
        view.setText(html)
        view.exec_()

    @QtCore.pyqtSlot()
    def on_actPrintTimelineForPerson_triggered(self):
        from Reports.TimelineForPerson import CTimelineForPerson
        personId = self.tblPersonnel.currentItemId()
        if not personId:
            return
        QtGui.qApp.callWithWaitCursor(self, self.modelTimeTable.saveData)
        begDate = self.modelTimeTable.begDate
        endDate = begDate.addDays(self.modelTimeTable.daysInMonth-1)
        report = CTimelineForPerson(self)
        params = {'begDate':begDate,
                  'endDate':endDate,
                  'personId':personId,
                 }

        view = CReportViewDialog(self)
        view.setWindowTitle(report.title())
        view.setText(report.build('', params))
        view.exec_()


    @QtCore.pyqtSlot()
    def on_actPrintTimelineForOffices_triggered(self):
        from Reports.TimelineForOffices import CTimelineForOffices
        personId = self.tblPersonnel.currentItemId()
        if not personId:
            return
        QtGui.qApp.callWithWaitCursor(self, self.modelTimeTable.saveData)
        begDate = self.modelTimeTable.begDate
        endDate = begDate.addDays(self.modelTimeTable.daysInMonth-1)
        report = CTimelineForOffices(self)
        params = {'begDate':begDate,
                  'endDate': endDate,
                  'orgStructureId': self.getOrgStructureId(),
                  'activityId': self.getActivityId(),
                 }
        view = CReportViewDialog(self)
        view.setWindowTitle(report.title())
        view.setText(report.build('', params))
        view.exec_()


    @QtCore.pyqtSlot()
    def on_tblAbsence_clicked(self):
        currentPersonId = self.tblPersonnel.currentItemId()
        personIdList = self.tblPersonnel.selectedItemIdList()
        if not personIdList:
            return
        lenPersonIdList = len(personIdList)
        selectPersons = lenPersonIdList > 1
        if QtGui.QMessageBox.question(self, u'Внимание!', u'Вы действительно хотите заполнить причину отсутствия?', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
            return
        dialog = CAbsenceDialog(self)
        if dialog.exec_():
            if selectPersons:
                db = QtGui.qApp.db
                dialogInfoCreate = CTemplatePersonsCreate(self)
                dialogInfoCreate.setWindowTitle(u'Массовое добавление причины отсутствия для специалистов')
                dialogInfoCreate.lblInfo.setText(u'В ГРАФИК ДОБАВЛЯЕТСЯ ПРИЧИНА ОТСУТСТВИЯ ДЛЯ СПЕЦИАЛИСТА'
                                                 + u'\n(Внимание: После выполнения этой операции данные о причинах отстуствия будут сразу сохранены в базу)')
                dialogInfoCreate.show()
                prbControlPercent = 0
                dialogInfoCreate.lblCountSelected.setText(u'Выбрано всего строк %d' % (lenPersonIdList))
                dialogInfoCreate.prbTemplateCreate.setMaximum(lenPersonIdList)
                for personId in personIdList:
                    QtGui.qApp.processEvents()
                    dialogInfoCreate.lblPersonName.setText(forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')))
                    if dialogInfoCreate.abortProcess:
                        break
                    prbControlPercent += 1
                    dialogInfoCreate.prbTemplateCreate.setValue(prbControlPercent)
                    QtGui.qApp.callWithWaitCursor(self, self.absencePersons, personId, dialog)
                    dialogInfoCreate.lblCountCreate.setText(u'Обработано всего строк %d' % (prbControlPercent))
                QtGui.qApp.callWithWaitCursor(self, self.loadWorkPlanPerson, currentPersonId)
                dialogInfoCreate.lblPersonName.setText(u'ПРЕРВАНО' if dialogInfoCreate.abortProcess else u'ГОТОВО')
                dialogInfoCreate.abortProcess = False
                self.enabledButtonsForSelected()
            else:
                QtGui.qApp.callWithWaitCursor(self, self.Absence, currentPersonId, dialog)


    def Absence(self, personId, dialog):
        reasonOfAbsence = dialog.cmbReasonOfAbsence.value()
        begDate = self.modelTimeTable.begDate
        daysInMonth = self.modelTimeTable.daysInMonth
        if dialog.edtBegDate.date():
            prevBegDate=dialog.edtBegDate.date()
        else:
            prevBegDate = begDate.addMonths(-1)
        if dialog.edtEndDate.date():
            prevEndDate = dialog.edtEndDate.date()
        else:
            prevEndDate = prevBegDate.addDays(daysInMonth-1)
        begDay = prevBegDate.day() - 1
        endDay = prevEndDate.day()
        addBegDate = prevBegDate
        for day in range(begDay, endDay):
            if (addBegDate.day() - 1) == day:
                if not dialog.chkFillRedDays.isChecked():
                    if addBegDate.dayOfWeek() in [6, 7]:
                        day = day + 2
                        addBegDate = addBegDate.addDays(2)
                    else:
                        addBegDate = addBegDate.addDays(1)
                else:
                    addBegDate = addBegDate.addDays(1)
                if day < endDay:
                    dayInfo = self.modelTimeTable.items[day]
                    if dayInfo[CTimeTableModel.ciReasonOfAbsence] is None:
                        dayInfo[CTimeTableModel.ciReasonOfAbsence] = reasonOfAbsence
                    dayInfo[CTimeTableModel.ciTimeLineChange] = True
                    self.setIsDirty(True)
        
        


    def absencePersons(self, personId, dialog):
        reasonOfAbsence = dialog.cmbReasonOfAbsence.value()
        begDate = self.modelTimeTable.begDate
        daysInMonth = self.modelTimeTable.daysInMonth
        if dialog.edtBegDate.date():
            prevBegDate=dialog.edtBegDate.date()
        else:
            prevBegDate = begDate.addMonths(-1)
        if dialog.edtEndDate.date():
            prevEndDate = dialog.edtEndDate.date()
        else:
            prevEndDate = prevBegDate.addDays(daysInMonth-1)
        begDay = prevBegDate.day() - 1
        endDay = prevEndDate.day()
        addBegDate = prevBegDate
        db = QtGui.qApp.db
        eventTable = db.table('Event')
        db.transaction()
        try:
            for day in range(begDay, endDay):
                if (addBegDate.day() - 1) == day:
                    if not dialog.chkFillRedDays.isChecked():
                        if addBegDate.dayOfWeek() in [6, 7]:
                            day = day + 2
                            addBegDate = addBegDate.addDays(2)
                        else:
                            addBegDate = addBegDate.addDays(1)
                    else:
                        addBegDate = addBegDate.addDays(1)
                    if day < endDay:
                        event = getEvent(constants.etcTimeTable, self.modelTimeTable.begDate.addDays(day), personId)
                        eventId = db.insertOrUpdate(eventTable, event)
                        action = CAction.getAction(eventId, constants.atcTimeLine)
                        action['reasonOfAbsence'] = reasonOfAbsence
                        action.save(eventId)
            db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise


    @QtCore.pyqtSlot()
    def on_btnCalc_clicked(self):
        personId = self.tblPersonnel.currentItemId()
        if not personId:
            return
        if QtGui.QMessageBox.question(self, u'Внимание!', u'Вы действительно хотите заполнить фактическое количество посещений?', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
            return
        dialog = CCalcDialog(self)
        if dialog.exec_():
            self.Calc(personId, dialog)


    def Calc(self, personId, dialog):
        model = self.modelTimeTable
        begDate = model.begDate
        daysInMonth = model.daysInMonth
        fillAll=dialog.rbFillAll.isChecked()
        for d in range(0, daysInMonth):
            dayInfo = model.items[d]
            day=begDate.addDays(d)

            db = QtGui.qApp.db
            table = db.table('Visit')
            cond0 = [table['person_id'].eq(personId), table['date'].eq(day)]
            finList=[]
            if dialog.boxBudget.isChecked():
                finList.append(1)
            if dialog.boxOMS.isChecked():
                finList.append(2)
            if dialog.boxDMS.isChecked():
                finList.append(3)
            if dialog.boxPlat.isChecked():
                finList.append(4)
            if dialog.boxCel.isChecked():
                finList.append(5)
            cond0.append(table['finance_id'].inlist(finList))

            def count_scene(scene_id_list):
                t = db.join('Visit', 'Event', 'Event.id=Visit.event_id')
                cnt_stmt='COUNT(DISTINCT client_id)'
                cond = cond0 + [table['scene_id'].inlist(scene_id_list)]
                countRecord = db.getRecordEx(t, cnt_stmt, cond)
                return countRecord.value(0).toInt()[0]

            if dialog.boxAmb.isChecked():
                i=CTimeTableModel.ciAmbFact
                if fillAll or not dayInfo[i]:
                    dayInfo[i]=count_scene([1, 4])

            if dialog.boxDom.isChecked():
                i=CTimeTableModel.ciHomeFact
                if fillAll or not dayInfo[i]:
                    dayInfo[i]=count_scene([2, 3])

        for column in xrange(CTimeTableModel.numCols):
            model.updateSums(column, False)
        self.labelsUpdate()
        self.setIsDirty(True)


def divIfPosible(nom,  denom):
    if denom != 0:
        return "%.2f"%(float(nom)/denom)
    else:
        return '-'


class CPersonnelModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent,  [
            CTextCol(u'Код',      ['code'], 6),
            CBoolCol(u'Доступ для ВС',   ['availableForExternal'], 15),
            CDateCol(u'Расписание видимо до', ['lastAccessibleTimelineDate'], 10),
            CTextCol(u'Расписание видимо дней', ['timelineAccessibleDays'], 6),
            CTextCol(u'Фамилия',  ['lastName'], 20),
            CNameCol(u'Имя',      ['firstName'], 20),
            CNameCol(u'Отчество', ['patrName'], 20),
            CDesignationCol(u'Подразделение', ['orgStructure_id'], ('OrgStructure', 'name'), 5),
            CRefBookCol(u'Должность',      ['post_id'], 'rbPost', 10),
            CRefBookCol(u'Специальность',  ['speciality_id'], 'rbSpeciality', 10),
            ], 'Person' )
        self.parentWidget = parent


class CDublDialog(CDialogBase, Ui_DublDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

class CCalcDialog(CDialogBase, Ui_CalcDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

class CAbsenceDialog(CDialogBase, Ui_AbsenceDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbReasonOfAbsence.setTable('rbReasonOfAbsence')
        begDate = parent.modelTimeTable.begDate
        endDate = begDate.addDays(parent.modelTimeTable.daysInMonth - 1)
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(endDate)
        self.edtBegDate.setDateRange(begDate, endDate)
        self.edtEndDate.setDateRange(begDate, endDate)

class CActivityAllTreeItem(CActivityTreeItem):
    def __init__(self):
        CActivityTreeItem.__init__(self, None, u'Любой', None)

    def loadChildren(self):
        items = []
        db = QtGui.qApp.db
        tableRBActivity = db.table('rbActivity')
        query = db.query(db.selectStmt(tableRBActivity, [tableRBActivity['id'], tableRBActivity['code'], tableRBActivity['name'] ]))
        while query.next():
            record = query.record()
            id   = forceInt(record.value('id'))
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            items.append(CActivityTreeItem(self, name, id))
        return items

class CActivityNoneTreeItem(CActivityTreeItem):
    def __init__(self):
        CActivityTreeItem.__init__(self, None, u'Не определен', None)

    def loadChildren(self):
        return []


class CActivityRootTreeItem(CActivityTreeItem):
    def __init__(self):
        CActivityTreeItem.__init__(self, None, u'-', None)

    def loadChildren(self):
        items = []
        items.append(CActivityNoneTreeItem())
        items.append(CActivityAllTreeItem())
        return items
