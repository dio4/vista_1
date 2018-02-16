# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Users.Rights import urAccessEditJobPlanner
from library.DialogBase                 import CDialogBase
from library.TableModel                 import CTableModel, CDateCol, CDesignationCol, CNumCol, CTimeCol
from library.Utils                      import forceBool, forceDate, forceDouble, forceInt, forceRef, forceTime,  monthName, monthNameGC, toVariant

from Orgs.OrgStructComboBoxes           import COrgStructureModel

from Resources.JobPlanNumbersDialog     import CJobPlanNumbersDialog
from Resources.JobPlanTable             import CJobPlanModel
from Resources.TemplateDialog           import CTemplateDialog

from Ui_DublicateDialog                 import Ui_DublicateDialog
from Ui_DublicateWeekDialog             import Ui_DublicateWeekDialog
from Ui_JobPlannerDialog                import Ui_JobPlannerDialog


class CJobPlanner(CDialogBase, Ui_JobPlannerDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId()))
        self.addModels('Jobs',    CJobsModel(self))
        self.addModels('JobPlan', CJobPlanModel(self))
        self.actFillByTemplate = QtGui.QAction(u'Заполнить', self)
        self.actFillByTemplate.setObjectName('actFillByTemplate')
        self.actRecountNumbers = QtGui.QAction(u'Пересчитать', self)
        self.actRecountNumbers.setObjectName('actRecountNumbers')
        self.actPlanNumbers = QtGui.QAction(u'Номерки', self)
        self.actPlanNumbers.setObjectName('actPlanNumbers')

        self.actFillByTemplate.setEnabled(QtGui.qApp.userHasRight(urAccessEditJobPlanner))
        self.actRecountNumbers.setEnabled(QtGui.qApp.userHasRight(urAccessEditJobPlanner))
        self.actPlanNumbers.setEnabled(QtGui.qApp.userHasRight(urAccessEditJobPlanner))

        self.modelJobPlan.error.connect(self.handleModelError)
#        self.setupPrintMenu()
        self.setupUi(self)
#        self.btnPrint.setMenu(self.mnuPrint)
        self.calendar.setList(QtGui.qApp.calendarInfo)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        self.setModels(self.tblJobs, self.modelJobs, self.selectionModelJobs)
        self.setModels(self.tblJobPlan, self.modelJobPlan, self.selectionModelJobPlan)

        self.tblJobPlan.createPopupMenu([self.actFillByTemplate, self.actRecountNumbers, self.actPlanNumbers])
        self.connect(self.tblJobPlan.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAmbAboutToShow)
        orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
        if orgStructureIndex and orgStructureIndex.isValid():
            self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
            self.treeOrgStructure.setExpanded(orgStructureIndex, True)

        startDate = QtCore.QDate.currentDate()
        self.calendar.setSelectedDate(startDate)
#        self.on_calendar_selectionChanged()
        self.setDateInTable(startDate, False)

        self.btnFill.setEnabled(QtGui.qApp.userHasRight(urAccessEditJobPlanner))
        self.btnDuplicate.setEnabled(QtGui.qApp.userHasRight(urAccessEditJobPlanner))
        self.btnDublicateWeek.setEnabled(QtGui.qApp.userHasRight(urAccessEditJobPlanner))


    def popupMenuAmbAboutToShow(self):
        if QtGui.qApp.userHasRight(urAccessEditJobPlanner):
            currentIndex = self.tblJobPlan.currentIndex()
            row = currentIndex.row()
            planTime = self.modelJobPlan.items[row].timeRange
            planCount = self.modelJobPlan.items[row].quantity
            if planTime and planCount and planCount > 0:
                self.actPlanNumbers.setEnabled(True)
                self.actRecountNumbers.setEnabled(True)
            else:
                self.actPlanNumbers.setEnabled(False)
                self.actRecountNumbers.setEnabled(False)


    def exec_(self):
        result = CDialogBase.exec_(self)
        QtGui.qApp.callWithWaitCursor(self, self.modelJobPlan.saveData)
        return result


    @staticmethod
    def getOrgStructIdList(treeItem):
        if treeItem:
            return treeItem.getItemIdList()
        return []


    @staticmethod
    def getOrgStructureJobIdListList(orgStructIdList, date):
        if orgStructIdList:
            db = QtGui.qApp.db
            tableOSJ = db.table('OrgStructure_Job')
            cond = [tableOSJ['jobType_id'].isNotNull(),
                    tableOSJ['master_id'].inlist(orgStructIdList),]
            if date:
                date = QtCore.QDate(date.year(), date.month(), 1)
                dateCond = [tableOSJ['lastAccessibleDate'].isNull(),
                            tableOSJ['lastAccessibleDate'].dateGe(date)]
                cond.append(db.joinOr(dateCond))
#            if date:
#                cond.append(db.joinOr([
#                    table['retireDate'].isNull(), table['retireDate'].ge(date)]))
            tableJobType = db.table('rbJobType')
            tableOrgStructure = db.table('OrgStructure')
            table = tableOSJ.join(tableJobType, tableJobType['id'].eq(tableOSJ['jobType_id']) )
            table = table.join(tableOrgStructure, tableOrgStructure['id'].eq(tableOSJ['master_id']) )
            return db.getIdList(table, idCol='OrgStructure_Job.id', where=cond, order='rbJobType.name, OrgStructure.code, OrgStructure_Job.idx')
        return []


    def updateJobList(self):
        treeIndex = self.treeOrgStructure.currentIndex()
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        orgStructIdList = self.getOrgStructIdList(treeItem)
        date = QtCore.QDate(self.calendar.yearShown(), self.calendar.monthShown(), 1)
        orgStructureJobIdList = self.getOrgStructureJobIdListList(orgStructIdList, date)
        self.tblJobs.setIdList(orgStructureJobIdList)


    def setDateInTable(self, date, scrollToDate=True):
        orgStructureJobRecord = self.tblJobs.currentItem()
        if orgStructureJobRecord:
            orgStructureJobId = forceRef(orgStructureJobRecord.value('id'))
            jobTypeId = forceRef(orgStructureJobRecord.value('jobType_id'))
        else:
            orgStructureJobId = None
            jobTypeId = None

        QtGui.qApp.callWithWaitCursor(
            self, self.modelJobPlan.setJobAndMonth, orgStructureJobId, jobTypeId, date.year(), date.month())
        delta = self.modelJobPlan.begDate.daysTo(date)
        currentIndex = self.selectionModelJobPlan.currentIndex()
        currentColumn = max(currentIndex.column(), 0)
        newIndex = self.modelJobPlan.index(delta, currentColumn)
        self.tblJobPlan.setCurrentIndex(newIndex)
#        self.selectionModelJobPlan.select(
#            newIndex, QtGui.QItemSelectionModel.Clear|QtGui.QItemSelectionModel.Select|QtGui.QItemSelectionModel.Current)
        if scrollToDate:
            self.tblJobPlan.scrollTo(newIndex, QtGui.QAbstractItemView.EnsureVisible)

        self.tblJobPlan.setEnabled( bool(orgStructureJobId and jobTypeId) )
        if QtGui.qApp.userHasRight(urAccessEditJobPlanner):
            self.btnFill.setEnabled( bool(orgStructureJobId and jobTypeId) )


    def fillByTemplate(self):
        orgStructureJobRecord = self.tblJobs.currentItem()
        orgStructureId = forceRef(orgStructureJobRecord.value('master_id')) if orgStructureJobRecord else None
        currentJobTypeId = forceRef(orgStructureJobRecord.value('jobType_id'))
        dialog = CTemplateDialog(self, orgStructureId = orgStructureId, currentJobTypeId = currentJobTypeId)
        begDate = self.modelJobPlan.begDate
        endDate = begDate.addDays(self.modelJobPlan.daysInMonth-1)
        record = self.tblJobs.currentItem()
        dialog.setDefaults(forceTime(record.value('begTime')),
                           forceTime(record.value('endTime')),
                           forceInt(record.value('quantity')),
                           forceRef(record.value('eQueueType_id')))
        dialog.setDateRange(begDate, endDate)
        if dialog.exec_():
            self.modelJobPlan.setWorkPlan(dialog.getWorkPlan(), dialog.getDateRange(), dialog.eQueueTypeId())


    @QtCore.pyqtSlot(int, int)
    def on_calendar_currentPageChanged(self, year, month):
        selectedDate = self.calendar.selectedDate()
        currYear = selectedDate.year()
        currMonth = selectedDate.month()
        newDate = selectedDate.addMonths((year-currYear)*12+(month-currMonth))
        self.calendar.setSelectedDate(newDate)
        self.setDateInTable(newDate, True)
        self.updateJobList()


    @QtCore.pyqtSlot()
    def on_calendar_selectionChanged(self):
        selectedDate = self.calendar.selectedDate()
        self.setDateInTable(selectedDate, True)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelOrgStructure_currentChanged(self, current, previous):
        self.updateJobList()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelJobs_currentChanged(self, current, previous):
        self.setDateInTable(self.calendar.selectedDate(), True)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelJobPlan_currentChanged(self, current, previous):
        row = current.row()
        if 0 <= row < self.modelJobPlan.daysInMonth:
            selectedDate = self.modelJobPlan.begDate.addDays(row)
            self.calendar.setSelectedDate(selectedDate)


#    @QtCore.pyqtSlot()
#    def on_modelJobPlan_dataChanged(self, topLeft, bottomRight):
#        self.labelsUpdate()


#    @QtCore.pyqtSlot()
#    def on_modelJobPlan_attrsChanged(self):
#        self.labelsUpdate()
#
#
#
#
    def getJobPlanNumbersDialog(self):
        currentIndex = self.tblJobPlan.currentIndex()
        row = currentIndex.row()
        date = QtCore.QDate(self.calendar.selectedDate())
        orgStructureJobRecord = self.tblJobs.currentItem()
        if orgStructureJobRecord:
            orgStructureId = forceRef(orgStructureJobRecord.value('master_id'))
            jobTypeId = forceRef(orgStructureJobRecord.value('jobType_id'))
        else:
            orgStructureId = None
            jobTypeId = None
        if orgStructureId and jobTypeId and date:
            dialog = CJobPlanNumbersDialog(self, orgStructureId, jobTypeId, date, self.modelJobPlan.items[row])
            dialog.exec_()


    def recountJobPlanNumbers(self):
        currentIndex = self.tblJobPlan.currentIndex()
        row = currentIndex.row()
        planTime = self.modelJobPlan.items[row].timeRange
        planCount = self.modelJobPlan.items[row].quantity
        self.modelJobPlan.items[row].forceChange = planTime and planCount > 0



    @QtCore.pyqtSlot(QtCore.QString)
    def handleModelError(self, message):
        QtGui.QMessageBox.warning(self,
                                  u'Внимание.',
                                  message,
                                  buttons = QtGui.QMessageBox.Ok)


    @QtCore.pyqtSlot()
    def on_actFillByTemplate_triggered(self):
        self.fillByTemplate()


    @QtCore.pyqtSlot()
    def on_actPlanNumbers_triggered(self):
        self.getJobPlanNumbersDialog()


    @QtCore.pyqtSlot()
    def on_actRecountNumbers_triggered(self):
        self.recountJobPlanNumbers()


    @QtCore.pyqtSlot()
    def on_btnFill_clicked(self):
        self.fillByTemplate()


    @QtCore.pyqtSlot()
    def on_btnDuplicate_clicked(self):
        if not self.tblJobs.currentItemId():
            return
        dialog = CDuplicateDialog(self.modelJobPlan.begDate, self)
        if dialog.exec_():
            self.modelJobPlan.copyDataFromPrevDate(dialog.date(), dialog.mode(), dialog.fillRedDays())

    @QtCore.pyqtSlot()
    def on_btnDublicateWeek_clicked(self):
        if not self.tblJobs.currentItemId():
            return
        dialog = CDublicateWeekDialog(self.modelJobPlan.begDate, self)
        if dialog.exec_():
            dialog.copyDayFromDate()
            date = dialog.getCopyDate()
            self.calendar.setSelectedDate(date)
            self.updateJobList()

    def duplicate(self, jobId, startDate, targetDate, mode):
        def copyDay(d1, d2):
            db = QtGui.qApp.db
            eventTable = db.table('Event')
            db.transaction()
            try:
#                # load d1
#
#                # save do d2
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise

        startDateDow = startDate.dayOfWeek()
        daysInMonth = targetDate.daysInMonth()
        if mode == 0: # один день
            fixedStartDate = startDate.addDays(0 if startDateDow not in [6, 7] else 2)
            for d in range(daysInMonth):
                copyDay(fixedStartDate, targetDate.addDays(d))
        elif mode == 1: # два дня
            fixedStartDates = [startDate.addDays(0 if startDateDow not in [6, 7] else 2),
                               startDate.addDays(1 if startDateDow not in [5, 6] else 3)]
            for d in range(daysInMonth):
                td = targetDate.addDays(d)
                if td.dayOfWeek()<6:
                    copyDay(fixedStartDates[d%2], td)
        else: # mode == 2: # неделя
            for d in range(daysInMonth):
                td = targetDate.addDays(d)
                offset = (td.dayOfWeek() - startDateDow)%7 # yes, it is python '%'
                copyDay(startDate.addDays(offset), td)

#        self.modelJobPlan.loadData(orgStructureId, jobTypeId, year, month)

#        for column in xrange(CTimeTableModel.numCols):
#            model.updateSums(column, False)
#        self.labelsUpdate()

#    @QtCore.pyqtSlot(QModelIndex)
#    def on_tblJobs_doubleClicked(self, current):
#        personId = self.tblPersonnel.currentItemId()
#        if personId:
#            dialog = CRBPersonEditor(self)
#            dialog.load(personId)
#            dialog.exec_()
#
#    @QtCore.pyqtSlot()
#    def on_btnSum_clicked(self):
#        personId = self.tblPersonnel.currentItemId()
#        if not personId:
#            return
#        if QtGui.QMessageBox.question(self, u'Внимание!', u'Вы действительно хотите заполнить суммарное время на все дни месяца?', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
#            return
#        self.fillSum(personId)

#    def fillSum(self, personId):
#        model = self.modelJobPlan
#        begDate = model.begDate
#        daysInMonth = model.daysInMonth
#        dow = begDate.dayOfWeek()
#        for d in range(0, daysInMonth):
#            dayInfo = model.items[d]
#            day=begDate.addDays(d)
#            if day.dayOfWeek()<6:
#                event = getEvent(etcTimeTable, day, personId)
#                eventId = forceRef(event.value('id'))
#                if not eventId:
#                    continue
#                timesum=QTime(0, 0)
#
#                actionAmbulance = CAction.getAction(eventId, atcAmbulance)
#                begTime = actionAmbulance['begTime']
#                endTime = actionAmbulance['endTime']
#                if begTime and endTime:
#                    timesum=timesum.addSecs(begTime.secsTo(endTime))
#
#                actionHome = CAction.getAction(eventId, atcHome)
#                begTime = actionHome['begTime']
#                endTime = actionHome['endTime']
#                if begTime and endTime:
#                    timesum=timesum.addSecs(begTime.secsTo(endTime))
#
#                actionExp = CAction.getAction(eventId, atcExp)
#                begTime = actionExp['begTime']
#                endTime = actionExp['endTime']
#                if begTime and endTime:
#                    timesum=timesum.addSecs(begTime.secsTo(endTime))
#
#                if timesum!=QTime(0, 0):
#                    dayInfo[CTimeTableModel.ciFactTime] = timesum
#
#        for column in xrange(CTimeTableModel.numCols):
#            model.updateSums(column, False)
#        self.labelsUpdate()
#
#    @QtCore.pyqtSlot()
#    def on_btnFact_clicked(self):
#        personId = self.tblPersonnel.currentItemId()
#        if not personId:
#            return
#        if QtGui.QMessageBox.question(self, u'Внимание!', u'Вы действительно хотите заполнить фактическое время на все дни месяца?', QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
#            return
#        self.fillFact(personId)
#
#    def fillFact(self, personId):
#        model = self.modelJobPlan
#        begDate = model.begDate
#        daysInMonth = model.daysInMonth
#        dow = begDate.dayOfWeek()
#        for d in range(0, daysInMonth):
#            dayInfo = model.items[d]
#            day=begDate.addDays(d)
#            if day.dayOfWeek()<6:
#                timesum = dayInfo[CTimeTableModel.ciFactTime]
#                if not timesum:
#                    continue
#                minuts = QTime(0, 0).secsTo(timesum)//60
#                if dayInfo[CTimeTableModel.ciAmbTime] or dayInfo[CTimeTableModel.ciHomeTime] or dayInfo[CTimeTableModel.ciExpTime] or dayInfo[CTimeTableModel.ciOtherTime]:
#                    continue
#                event = getEvent(etcTimeTable, day, personId)
#                eventId = forceRef(event.value('id'))
#                if not eventId:
#                    continue
#
#                actionAmbulance = CAction.getAction(eventId, atcAmbulance)
#                begTime = actionAmbulance['begTime']
#                endTime = actionAmbulance['endTime']
#                ambulanceTime = None
#                if begTime and endTime:
#                    ambulanceTime = begTime.secsTo(endTime)
#
#                actionHome = CAction.getAction(eventId, atcHome)
#                begTime = actionHome['begTime']
#                endTime = actionHome['endTime']
#                homeTime = None
#                if begTime and endTime:
#                    homeTime = begTime.secsTo(endTime)
#
#                if ambulanceTime and homeTime:
#                    ambulanceMinuts = (ambulanceTime*minuts)//(ambulanceTime+homeTime)
#                    dayInfo[CTimeTableModel.ciAmbTime] = QTime(0, 0).addSecs(ambulanceMinuts*60)
#                    homeMinuts = minuts-ambulanceMinuts
#                    dayInfo[CTimeTableModel.ciHomeTime] = QTime(0, 0).addSecs(homeMinuts*60)
#                elif ambulanceTime and not homeTime:
#                    dayInfo[CTimeTableModel.ciAmbTime] = timesum
#                elif not ambulanceTime and homeTime:
#                    dayInfo[CTimeTableModel.ciHomeTime] = timesum
#
#        for column in xrange(CTimeTableModel.numCols):
#            model.updateSums(column, False)
#        self.labelsUpdate()

#    def setupPrintMenu(self):
#        self.addObject('mnuPrint', QMenu(self))
#        self.addObject('actPrintPerson', QAction(u'Индивидуальный табель', self))
#        self.addObject('actPrintPersons', QAction(u'Общий табель', self))
#        self.mnuPrint.addAction(self.actPrintPerson)
#        self.mnuPrint.addAction(self.actPrintPersons)

#    @pyqtSlot()
#    def on_mnuPrint_aboutToShow(self):
#        self.actPrintPerson.setEnabled(True)
#        self.actPrintPersons.setEnabled(True)



def divIfPosible(nom,  denom):
    if denom != 0:
        return "%.2f"%(float(nom)/denom)
    else:
        return '-'


class CJobsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent,  [
            CDesignationCol(u'Код',          ['jobType_id'], ('rbJobType', 'code'),  6),
            CDesignationCol(u'Наименование', ['jobType_id'], ('rbJobType', 'name'), 20),
            CTimeCol(       u'С',            ['begTime'],  6),
            CTimeCol(       u'По',           ['endTime'],  6),
            CNumCol(        u'Количеcтво',   ['quantity'], 6),
            CDesignationCol(u'Подразделение',['master_id'], ('OrgStructure', 'code'), 5),
            CDateCol(       u'Расписание видимо до', ['lastAccessibleDate'], 6)
            ], 'OrgStructure_Job' )
        self.parentWidget = parent


class CDuplicateDialog(CDialogBase, Ui_DublicateDialog):
    def __init__(self, date, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.defaultStartDate = date.addMonths(-1)
        msg = u'Выберите режим копирования для выполнения дублирования графика с %s на %s' % (
            monthNameGC[self.defaultStartDate.month()],
            monthName[date.month()])
        self.edtStart.setDate(self.defaultStartDate)
        self.lblMessage.setText(msg)


    def date(self):
        return self.edtStart.date() if self.chkStart else self.defaultStartDate


    def mode(self):
        if self.rbWeek.isChecked():
            return 2
        elif self.rbDual.isChecked():
            return 1
        else:
            return 0


    def fillRedDays(self):
        return self.chkFillRedDays.isChecked() if not self.rbWeek.isChecked() else False

class CDublicateWeekDialog(CDialogBase, Ui_DublicateWeekDialog):
    def __init__(self, date, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.record = parent.tblJobs.currentItem()
        self.orgStructureJobId = forceRef(self.record.value('id'))
        self.jobTypeId = forceRef(self.record.value('jobType_id'))
        self.jobs = {}
        self.oldDate = None
        self.oldCountDays = None
        self.countDaysForCopy = self.edtCountDays.value()
        self.currentDate = QtCore.QDate.currentDate()
        self.copeidDate = date.addMonths(-1)
        self.edtStart.setDate(self.copeidDate)
        self.busyDates = []

    def getCopyDate(self):
        return self.calendar.selectedDate()



    def getCountDays(self):
        return self.countDaysForCopy

    def dataForCopy(self):
        return self.calendar.selectedDate(), self.countDaysForCopy

    #устанавливаем доступные для копирования дни в календаре
    def setDays(self, firstDateMonthCopyMade):
        dates = []
        freeDates = []
        self.busyDates = []
        if firstDateMonthCopyMade and self.checkCopyPeriod():
            monthOfSourceDate = firstDateMonthCopyMade == self.copeidDate.addDays(7) #в календаре открыт месяц, в котором находится копируемая дата
            suppousedStartDateCopyMade = firstDateMonthCopyMade
            for week in xrange(self.calendar.getCountSuitableWeeksInMonth(firstDateMonthCopyMade, monthOfSourceDate)):
                dates.append(suppousedStartDateCopyMade)
                for count in xrange(self.countDaysForCopy):
                    freeDates.append(suppousedStartDateCopyMade.addDays(count))
                suppousedStartDateCopyMade = suppousedStartDateCopyMade.addDays(7)
            records = self.getJobInfo(dates[0], endDate=suppousedStartDateCopyMade.addDays(-1))
            for record in records:
                date = forceDate(record.value('date'))
                busy = forceBool(record.value('busy'))
                if date in freeDates:
                    if not busy:
                        self.busyDates.append(date)
                    freeDates.remove(date)
            for index, date in enumerate(dates):
                if not (any(freeDate >= dates[index] or freeDate <= dates[index].addDays(7) for freeDate in freeDates) or any(busyDate >= dates[index] or busyDate <= dates[index].addDays(7) for busyDate in self.busyDates)):
                    dates.remove(date)
        self.calendar.setDateForSelect(dates)
        self.calendar.setColor([dict(brush=QtGui.QColor(205, 85, 85), values=self.busyDates), dict(brush=QtGui.QColor(152, 251, 152), values=freeDates)])


    #получаем список запиесей с днями без расписания и с днями, имеющими расписание, но без записи пациентов на них
    def getJobInfo(self, begDate, endDate=None, countDays=0):
        queryTable = None
        db = QtGui.qApp.db
        tableJob = db.table('Job')
        tableJobTicket = db.table('Job_Ticket')
        select = [tableJob['id'],
                  tableJob['date'],
                  tableJob['begTime'],
                  tableJob['endTime'],
                  tableJob['quantity'],
                  tableJob['isOvertime'],
                  tableJob['limitSuperviseUnit'],
                  tableJob['personQuota']]
        cond = [tableJob['orgStructureJob_id'].eq(self.orgStructureJobId),
                tableJob['jobType_id'].eq(self.jobTypeId),
                tableJob['date'].dateGe(begDate),
                tableJob['date'].dateLe(begDate.addDays(countDays) if countDays else endDate if endDate else begDate),
                tableJob['deleted'].eq(0)]
        if begDate != self.copeidDate:
            select.append('sum(if(%s, 1, 0)) AS busy' % tableJobTicket['resTimestamp'].isNotNull())
            queryTable = tableJob.innerJoin(tableJobTicket, tableJobTicket['master_id'].eq(tableJob['id']))
        return db.getRecordList(queryTable if queryTable else tableJob, cols=select, where=cond, order=tableJob['date'], group=tableJob['date'])

    #получаем список работ для копирования
    def getJobs(self):
        jobs = {}
        records = self.getJobInfo(self.copeidDate, countDays=self.countDaysForCopy)
        for record in records:
            jobs[forceDate(record.value('date')).toString('dd.MM.yyyy')] = (forceRef(record.value('id')),
                                                                            forceTime(record.value('begTime')),
                                                                            forceTime(record.value('endTime')),
                                                                            forceInt(record.value('quantity')),
                                                                            forceInt(record.value('isOvertime')),
                                                                            forceDouble(record.value('limitSuperviseUnit')),
                                                                            forceInt(record.value('personQuota')))
        return jobs

    #получаем список номерков для копирования
    def getTickets(self, masterId):
        db = QtGui.qApp.db
        table = db.table('Job_Ticket')
        select = [table['datetime'],
                  table['idx']]
        cond = [table['master_id'].eq(masterId)]
        return db.getRecordList(table, cols=select, where=cond)

    #получаем первую дату месяца, у которой день недели совпадает с днем копирования
    def getDateMonthShown(self, monthShown, yearShown):
        monthOfCopyDay = self.copeidDate.month()
        yearOfCopyDay = self.copeidDate.year()
        if monthShown == monthOfCopyDay and yearShown == yearOfCopyDay:
            return self.copeidDate.addDays(7)
        elif (monthShown > monthOfCopyDay and yearShown == yearOfCopyDay) or (yearShown > yearOfCopyDay):
            firstDayOfMonth = QtCore.QDate(yearShown, monthShown, 1)
            shiftOfDays = self.copeidDate.dayOfWeek() - firstDayOfMonth.dayOfWeek()
            return firstDayOfMonth.addDays(shiftOfDays) if shiftOfDays >= 0 else firstDayOfMonth.addDays(7 - abs(shiftOfDays))
        else:
            return None

    #копирование
    def copyDayFromDate(self):
        date = self.getCopyDate()
        jobs = self.getJobs()
        for day in xrange(self.countDaysForCopy):
            copyDate = self.copeidDate.addDays(day).toString('dd.MM.yyyy')
            if jobs.has_key(copyDate):
                date = date.addDays(day)
                if date in self.busyDates:
                    if self.chkBusyDays.isChecked():
                        self.deleteRecord(date)
                    else:
                        continue
                self.saveRecord(date, jobs[copyDate])

    def deleteRecord(self, date):
        db = QtGui.qApp.db
        tableJob = db.table('Job')
        # record = db.getRecordEx(tableJob, '*', [tableJob['orgStructureJob_id'].eq(self.orgStructureJobId),
        #                                tableJob['jobType_id'].eq(self.jobTypeId),
        #                                tableJob['date'].eq(date)])
        # record.setValue('deleted', QtCore.QVariant(1))
        # db.updateRecord(tableJob, record)
        db.deleteRecord(tableJob, [tableJob['orgStructureJob_id'].eq(self.orgStructureJobId),
                                    tableJob['jobType_id'].eq(self.jobTypeId),
                                    tableJob['date'].eq(date)])




    def saveRecord(self, date, jobsInfo):
        db = QtGui.qApp.db
        tableJob    = db.table('Job')
        tableTicket = db.table('Job_Ticket')
        record = tableJob.newRecord()
        record.setValue('orgStructure_id',    toVariant(forceRef(self.record.value('master_id'))))
        record.setValue('orgStructureJob_id', toVariant(self.orgStructureJobId))
        record.setValue('jobType_id',         toVariant(self.jobTypeId))
        record.setValue('date',               toVariant(date))
        record.setValue('begTime',            toVariant(jobsInfo[1]))
        record.setValue('endTime',            toVariant(jobsInfo[2]))
        record.setValue('quantity',           toVariant(jobsInfo[3]))
        record.setValue('isOvertime',         toVariant(jobsInfo[4]))
        record.setValue('limitSuperviseUnit', toVariant(jobsInfo[5]))
        record.setValue('personQuota',        toVariant(jobsInfo[6]))
        id = db.insertRecord(tableJob, record)
        assert id is not None
        for ticket in self.getTickets(jobsInfo[0]):
            record = tableTicket.newRecord(['master_id', 'datetime', 'idx'])
            record.setValue('master_id', toVariant(id))
            record.setValue('datetime',  toVariant(QtCore.QDateTime(date, forceTime(ticket.value('datetime')))))
            record.setValue('idx',       toVariant(ticket.value('idx')))
            db.insertRecord(tableTicket, record)

    def checkCopyPeriod(self):
        self.lblWarning.setText(u'<FONT COLOR=#800000></FONT>')
        if not self.jobs:
            text = u'Измените дату начала копирования или увеличте период.'
            self.lblWarning.setText(u'<FONT COLOR=#800000>  Предупреждение: ' + (u'C %s по %s расписание на заведено. ' % (self.copeidDate.toString('dd.MM.yyyy'), self.copeidDate.addDays(self.countDaysForCopy - 1).toString('dd.MM.yyyy'))
                                    if self.countDaysForCopy != 1 else u'На %s расписание на заведено. ' % self.copeidDate.toString('dd.MM.yyyy')) + u'\n' +text + '</FONT>')
            return False
        return True

    #обновление инфрмации о работых в связи с изменением одного из параметров поиска периода, на который будем копировать
    def updateJobs(self):
        if self.oldDate != self.copeidDate or self.oldCountDays != self.countDaysForCopy:
            self.jobs = self.getJobs()
            self.oldDate = self.copeidDate
            self.oldCountDays = self.countDaysForCopy

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtStart_dateChanged(self, date):
        self.copeidDate = date
        self.updateJobs()
        self.setDays(self.getDateMonthShown(self.calendar.monthShown(), self.calendar.yearShown()))

    @QtCore.pyqtSlot()
    def on_edtCountDays_editingFinished(self):
        self.countDaysForCopy = self.edtCountDays.value()
        self.updateJobs()
        self.setDays(self.getDateMonthShown(self.calendar.monthShown(), self.calendar.yearShown()))

    @QtCore.pyqtSlot(int, int)
    def on_calendar_currentPageChanged(self, year, month):
        self.setDays(self.getDateMonthShown(month, year))