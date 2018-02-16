# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013-2014 Vista Software. All rights reserved.
##
#############################################################################
from Events.Ui_AddDosesDialog            import Ui_AddDosesDialog
from library.DialogBase                    import CDialogBase, CConstructHelperMixin
from library.InDocTable                    import *
from library.Utils                         import pyDate

#TODO: "Больше не спрашивать" с привязкой к пользователю и рабочему месту (хранить в S11App.ini)

class CDosesData:
    def __init__(self, dates=None, times=None):
        if not dates:
            dates = []
        if not times:
            times = []
        self._datesCount = len(dates)
        self._timesCount = len(times)
        self._count = self._datesCount*self._timesCount
        self._dates = sorted([pyDate(date) for date in dates]*self._timesCount)
        self._times = list(times)*self._datesCount
        self._items = [0.0]*(self._count)
        self._comments = [''] * (self._count)

    def __len__(self):
        return self._count

    def getDateByRow(self, row):
        return self._dates[row]

    def getTimeByRow(self, row):
        return self._times[row]

    def getDoseByRow(self, row):
        return self._items[row]

    def getCommentByRow(self, row):
        return self._comments[row]

    def getDayDosesByRow(self, row):
        date = self.getDateByRow(row)
        firstRow = self._dates.index(date)
        return self._items[firstRow:firstRow+self._timesCount]

    def setDoseByRow(self, row, value):
        self._items[row] = value

    def setCommentByRow(self, row, value):
        self._comments[row] = value

    def doses(self):
        return self._items

    def comments(self):
        return self._comments

    def setDoses(self, doses):
        self._items = doses

    def setComments(self, comments):
        self._comments = comments

    def fillAll(self, row):
        dosesForDay = self.getDayDosesByRow(row)
        if any(dosesForDay):
            self._items = list(dosesForDay) * self._datesCount

    def fillNextDay(self, row):
        date = self.getDateByRow(row)
        firstRow = self._dates.index(date)
        dosesForDay = self._items[firstRow:firstRow+self._timesCount]
        if any(dosesForDay):
            nextDayFirstRow = firstRow + self._timesCount
            self._items[nextDayFirstRow:nextDayFirstRow+self._timesCount] = dosesForDay

    def dates(self):
        return sorted(list(set(self._dates)))

    def times(self):
        return sorted(list(set(self._times)))

    def update(self, dates, times):
        oldValues = {}
        oldComments = {}
        for i in xrange(self._count):
            date = self._dates[i]
            time = self._times[i]
            dose = self._items[i]
            comment = self._comments[i]
            oldValues[(date, time)] = dose
            oldComments[(date, time)] = comment

        self._datesCount = len(dates)
        self._timesCount = len(times)
        self._count = self._datesCount*self._timesCount
        self._dates = sorted([pyDate(date) for date in dates]*self._timesCount)
        self._times = list(times)*self._datesCount
        self._items = [0.0]*(self._count)
        self._comments = [''] * (self._count)

        for i in xrange(self._count):
            date = self._dates[i]
            time = self._times[i]
            oldValue = oldValues.get((date, time), None)
            if oldValue:
                self._items[i] = oldValue
            oldComment = oldComments.get((date, time), None)
            if oldComment:
                self._comments[i] = oldComment

class CTimeTableModel(QtCore.QAbstractTableModel):

    item = []
    horizontalHeaderText = [u'Выбор времени']
    verticalHeaderText = [datetime.time(0),
                          datetime.time(1),
                          datetime.time(2),
                          datetime.time(3),
                          datetime.time(4),
                          datetime.time(5),
                          datetime.time(6),
                          datetime.time(7),
                          datetime.time(8),
                          datetime.time(9),
                          datetime.time(10),
                          datetime.time(11),
                          datetime.time(12),
                          datetime.time(13),
                          datetime.time(14),
                          datetime.time(15),
                          datetime.time(16),
                          datetime.time(17),
                          datetime.time(18),
                          datetime.time(19),
                          datetime.time(20),
                          datetime.time(21),
                          datetime.time(22),
                          datetime.time(23),
                          ]

    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        for time in self.verticalHeaderText:
            self.items.append([time, QtCore.Qt.white])


    def columnCount(self, index = None):
        return len(self.horizontalHeaderText)


    def rowCount(self, index = None):
        return len(self.verticalHeaderText)


    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.horizontalHeaderText[section])
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.verticalHeaderText[section].strftime('%H:%M'))
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.BackgroundColorRole:
           row = index.row()
           return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(self.items[row][1])))
        return QtCore.QVariant()

    def rowChecked(self, row):
        if self.items[row][1] == QtCore.Qt.white:
            self.items[row][1] = QtCore.Qt.green
            flag = True
        else:
            self.items[row][1] = QtCore.Qt.white
            flag = False
        self.reset()
        return flag, self.items[row][0]

class CDoseModel(QtCore.QAbstractTableModel):

    unit = ''
    headers = [u'Дата', u'Время', u'Доза', u'Комментарий']

    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._items = CDosesData()

    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self._items)

    def columnCount(self, index = QtCore.QModelIndex()):
        return len(self.headers)

    def flags(self, index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 2:
            flags = flags | QtCore.Qt.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section < len(self.headers):
                return QVariant(self.headers[section])
        return QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        col = index.column()
        row = index.row()
        if col == 0 and role == QtCore.Qt.DisplayRole:
            return toVariant(self._items.getDateByRow(row))
        elif col == 1 and role == QtCore.Qt.DisplayRole:
            return toVariant(self._items.getTimeByRow(row).strftime('%H:%M'))
        elif col == 2:
            item = self._items.getDoseByRow(row)
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(forceString(item) + u' (' + self.unit + u')' if item else u'')
            elif role == QtCore.Qt.EditRole:
                return QtCore.QVariant(forceString(forceInt(item)) if item.is_integer() else forceString(item))
        elif col == 3 and role == QtCore.Qt.DisplayRole:
            return toVariant(self._items.getCommentByRow(row))
        return QVariant()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole and index.column() == 2:
            self._items.setDoseByRow(index.row(), forceDouble(value))
            self.reset()
            return True
        return False

    def setItems(self, items):
        self._items = items
        self.reset()

    def items(self):
        return self._items

    def doses(self):
        return self._items.doses()

    def setDoses(self, doses):
        self._items.setDoses(doses)

    def setComments(self, comments):
        self._items.setComments(comments)

    def comments(self):
        return self._items._comments()

    def dates(self):
        return self._items.dates()

    def times(self):
        return self._items.times()

    def uniqueTimes(self):
        return self._items.times()

    def setUnit(self, unit):
        self.unit = unit

    def rebuild(self, dates, times):
        self._items.update(dates, times)
        self.reset()

    def fillAll(self, row):
        self._items.fillAll(row)
        self.reset()

    def fillNextDay(self, row):
        self._items.fillNextDay(row)
        self.reset()


class CAddDosesSetupDialog(CDialogBase, Ui_AddDosesDialog, CConstructHelperMixin):
    curInterval  = 0
    curBegDate = QDate.currentDate()
    curEndDate = QDate.currentDate()

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.times = []
        self.dates = []

        self.addModels('TimeTable', CTimeTableModel(self))
        self.tblTimeList.setModel(self.modelTimeTable)
        self.tblTimeList.horizontalHeader().setStretchLastSection(True)
        self.tblTimeList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.addModels('DoseTable', CDoseModel(self))
        self.setModels(self.tblDoseList, self.modelDoseTable, self.selectionModelDoseTable)
        self.tblDoseList.horizontalHeader().setStretchLastSection(True)
        self.tblDoseList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblDoseList.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.tblDoseList.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.setModal(True)

        self.cmbInjectionPath.setTable('rbRoute')

    def setData(self, unit, timeList, doseItems, injectionPath, interval, begDate, endDate, commentsList):
        self.tblDoseList.model().setUnit(unit)
        if timeList:
            self.times = timeList
            for time in timeList:
                self.tblTimeList.model().rowChecked(time.hour)
        if injectionPath:
            self.cmbInjectionPath.setCurrentIndex(injectionPath)
        else:
            self.cmbInjectionPath.setCurrentIndex(0)
        self.cmbInterval.setCurrentIndex(interval)
        if begDate:
            self.edtBegDate.setDate(begDate)
        else:
            self.edtBegDate.setDate(QDate.currentDate())
        if endDate:
            self.edtEndDate.setDate(endDate)
        else:
            self.edtEndDate.setDate(QDate.currentDate())
        self.timeAdd()
        if doseItems != []:
            self.tblDoseList.model().setDoses(doseItems)
        if commentsList != []:
            self.tblDoseList.model().setComments(commentsList)

    def getData(self):
        #model = self.tblDoseList.model()
        return self.tblDoseList.model().items(), \
               self.cmbInjectionPath.currentIndex(), \
               self.cmbInterval.currentIndex(), \
               self.edtBegDate.date(), \
               self.edtEndDate.date()


    def isRebuild(self):
        return not any(self.tblDoseList.model().doses())

    def accept(self):
        if self.checkDataEntered():
            super(CAddDosesSetupDialog, self).accept()

    def checkDataEntered(self):
        if not self.edtBegDate.date():
            return self.checkInputMessage(u'дату начала приёма', False, self.edtBegDate)
        if not self.edtEndDate.date():
            return self.checkInputMessage(u'дату окончания приёма', False, self.edtEndDate)
        if not self.cmbInjectionPath.value():
            return self.checkInputMessage(u'путь введения', False, self.cmbInjectionPath)
        if not self.times:
            return self.checkInputMessage(u'время приёма', False, self.tblTimeList)
        for row, dose in enumerate(self.tblDoseList.model().doses()):
            if not dose:
                return self.checkInputMessage(u'дозу', False, self.tblDoseList, row, 2)
        return True

    def warnAboutDosesLoss(self):
        if not self.isRebuild():
            res = QtGui.QMessageBox.warning(None, u'Внимание', u'Расписание приёма доз будет изменено. Продолжить?', QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)
            return res == QtGui.QMessageBox.Ok
        return True


    @pyqtSlot(QModelIndex)
    def on_tblTimeList_clicked(self, index):
        if self.warnAboutDosesLoss():
            flag, time = self.tblTimeList.model().rowChecked(index.row())
            if flag:
                self.times.append(time)
                self.times.sort()
            else:
                self.times.remove(time)
            self.rebuildDosesModel()


    @pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        if self.warnAboutDosesLoss():
            self.timeAdd()
            self.rebuildDosesModel()
            self.curBegDate = date
        else:
            self.edtBegDate.setDate(self.curBegDate)


    @pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        if self.warnAboutDosesLoss():
            self.timeAdd()
            self.rebuildDosesModel()
            self.curEndDate = date
        else:
            self.edtEndDate.setDate(self.curEndDate)


    @pyqtSlot(int)
    def on_cmbInterval_currentIndexChanged(self, index):
        if self.warnAboutDosesLoss():
            self.timeAdd()
            self.rebuildDosesModel()
            self.curInterval = index
        else:
            self.cmbInterval.setCurrentIndex(self.curInterval)


    def timeAdd(self):
        if self.edtBegDate.date() <= self.edtEndDate.date():
            self.dates = []
            curDate = self.edtBegDate.date()
            while curDate <= self.edtEndDate.date():
                self.dates.append(curDate)
                curDate = curDate.addDays(self.cmbInterval.currentIndex()+1)


    def rebuildDosesModel(self):
        if self.edtBegDate.date() <= self.edtEndDate.date():
            self.tblDoseList.model().rebuild(self.dates, self.times)
            row = 0
            timesCount = len(self.times)
            self.tblDoseList.clearSpans()
            if timesCount > 1:
                for _ in self.dates:
                    self.tblDoseList.setSpan(row, 0, timesCount, 1)
                    row += timesCount


    @pyqtSlot()
    def on_btnAddDoseToAllDay_clicked(self):
        row = self.tblDoseList.currentIndex().row()
        self.tblDoseList.model().fillAll(row)


    @pyqtSlot()
    def on_btnAddDoseToNextDay_clicked(self):
        row = self.tblDoseList.currentIndex().row()
        self.tblDoseList.model().fillNextDay(row)

    def canClose(self):
        return True