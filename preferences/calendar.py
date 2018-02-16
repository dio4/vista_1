# -*- coding: utf-8 -*-
"""
editor of preferences of calendar
"""
from PyQt4 import QtGui, QtCore

from Ui_calendar import Ui_Dialog
from Ui_calendarChangeday import Ui_ChangeDayDialog
from Ui_calendarHoliday import Ui_HolidayDialog
from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CCol, CTextCol, CDateCol, CNumCol
from library.calendar import CHoliday, CChangeDay, CCalendarExceptionList
from library.exception import CDatabaseException


class CLongDateCol(CDateCol):
    u"""Колонка с датой, в которой отображаются все 4 цифры года"""

    def format(self, values):
        val = values[0]
        if val.type() == QtCore.QVariant.Date or val.type() == QtCore.QVariant.DateTime:
            val = val.toDate()
            return QtCore.QVariant(val.toString("dd.MM.yyyy"))
        return CCol.invalid


class CDayMonthCol(CDateCol):
    u"""Колонка с датой, в которой отображаются день и месяц, а год заменяется на текущий, взятый из календаря"""

    def __init__(self, title, fields, defaultWidth, calendar, alignment='l'):
        # CCol.__init__(self, title, fields, defaultWidth, alignment)
        CDateCol.__init__(self, title, fields, defaultWidth)
        self.calendar = calendar

    def format(self, values):
        val = values[0]
        if val.type() == QtCore.QVariant.Date or val.type() == QtCore.QVariant.DateTime:
            val = val.toDate()
            return QtCore.QVariant(val.toString("dd.MM.") + str(self.calendar.yearShown()))
        return CCol.invalid


class CCalendarDialog(QtGui.QDialog, Ui_Dialog):
    u"""Диалог для настройки параметров календаря"""

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.tableHoliday.setModel(CTableModel(
            self,
            [
                CDayMonthCol(u'Начало периода', ['date'], 15, self.calendarHoliday),
                CDayMonthCol(u'Конец периода', ['endDate'], 15, self.calendarHoliday),
                CTextCol(u'Имя праздника', ['text'], 50),
                CNumCol(u'Год нач.', ['startYear'], 7),
                CNumCol(u'Год оконч.', ['finishYear'], 3)
            ],
            'CalendarExceptions'
        ))

        self.tableChangeday.setModel(CTableModel(
            self,
            [
                CLongDateCol(u'Дата', ['date'], 80),
                CLongDateCol(u'Дата переноса', ['fromDate'], 80),
                CTextCol(u'Комментарий', ['text'], 325)
            ],
            'CalendarExceptions'
        ))

        self.tableHoliday.addPopupDelRow()
        self.tableChangeday.addPopupDelRow()

        self.list = CCalendarExceptionList()
        self.calendarHoliday.setList(self.list)
        self.calendarChangeday.setList(self.list)
        self.updateInfo()
        self.updateTable()

    def getCurrentYear(self):
        return self.calendarHoliday.yearShown()

    def getHolidayDate(self, row):
        holidays = self.tableHoliday.model()
        return QtCore.QDate.fromString(holidays.data(holidays.index(row, 0)).toString(), "dd.MM.yyyy")

    def getHolidayEndDate(self, row):
        holidays = self.tableHoliday.model()
        return QtCore.QDate.fromString(holidays.data(holidays.index(row, 1)).toString(), "dd.MM.yyyy")

    def getHolidayText(self, row):
        holidays = self.tableHoliday.model()
        return holidays.data(holidays.index(row, 2)).toString()

    def getHolidayStart(self, row):
        holidays = self.tableHoliday.model()
        text = holidays.data(holidays.index(row, 3)).toString()
        if len(text) == 0:
            return 1
        else:
            return text.toInt()

    def getHolidayFinish(self, row):
        holidays = self.tableHoliday.model()
        text = holidays.data(holidays.index(row, 4)).toString()
        if len(text) == 0:
            return 4999
        else:
            return text.toInt()

    def getChangedayDate(self, row):
        changedays = self.tableChangeday.model()
        return QtCore.QDate.fromString(changedays.data(changedays.index(row, 0)).toString(), "dd.MM.yyyy")

    def getChangedayChangeDate(self, row):
        changedays = self.tableChangeday.model()
        return QtCore.QDate.fromString(changedays.data(changedays.index(row, 1)).toString(), "dd.MM.yyyy")

    def getChangedayText(self, row):
        changedays = self.tableChangeday.model()
        changedays.data(changedays.index(row, 2)).toString()

    def saveHoliday(self, row, holiday):
        date = self.getHolidayDate(row)
        endDate = self.getHolidayEndDate(row)
        text = self.getHolidayText(row)
        start = self.getHolidayStart(row)
        finish = self.getHolidayFinish(row)
        CHoliday(date, text, start, finish, endDate)

    def saveChangeday(self, row, changeday):
        date = self.getChangedayDate(row)
        chdate = self.getChangedayChangeDate(row)
        comment = self.getChangedayText(row)
        CChangeDay(date, chdate, comment)

    def updateTable(self):
        year = self.getCurrentYear()
        (holidlist, chidlist) = self.list.loadYear(QtGui.qApp.db, year)
        self.tableHoliday.setIdList(holidlist)
        self.tableChangeday.setIdList(chidlist)

    def updateInfo(self):
        u"""Обновить информацию о праздниках и переносах, хранящуюся в БД"""
        self.list.load(QtGui.qApp.db)

    def updateCalendar(self):
        if self.tableHoliday.model().rowCount() > 0 and self.tableHoliday.currentIndex().row() >= 0:
            date = self.getHolidayDate(self.tableHoliday.currentIndex().row())
            self.calendarHoliday.setSelectedDate(date)
        if self.tableChangeday.model().rowCount() > 0 and self.tableChangeday.currentIndex().row() >= 0:
            date = self.getChangedayDate(self.tableChangeday.currentIndex().row())
            self.calendarChangeday.setSelectedDate(date)

    def add(self):
        if self.tabWidget.currentIndex() == 0:  # добавляем праздник:
            dialog = CHolidayDialog(self, None)
            dialog.exec_()
        else:
            dialog = CChangeDayDialog(self, None)
            dialog.exec_()

    def edit(self):
        if self.tabWidget.currentIndex() == 0:  # редактируем праздник:
            date = self.getHolidayDate(self.tableHoliday.currentIndex().row())
            holiday = self.list.getException(date)
            dialog = CHolidayDialog(self, holiday)
            dialog.exec_()
        else:  # редактируем перенос:
            date = self.getChangedayDate(self.tableChangeday.currentIndex().row())
            changeday = self.list.getException(date)
            dialog = CChangeDayDialog(self, changeday)
            dialog.exec_()

    def close(self):
        QtGui.qApp.calendarInfo.load(QtGui.qApp.db)  # обновляем информацию о праздниках
        # посылаем сигнал всем календарям об изменении праздников!!!!!!!!!!!!!!!!!!!!
        QtGui.QDialog.close(self)


class CMyDialog(CDialogBase):
    u"""Мой вариант базового диалога с `прослойкой` между БД и интерфейсом пользователя для хранения данных"""

    def __init__(self, parent, object):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.object = object
        if object != None:
            self.setObject(object)
        self.setupDirtyCather()

    def setObject(self, obj):
        u"""Абстрактный метод - заполнить диалог"""
        pass

    def getObject(self):
        u"""Абстрактный метод - получить данные из диалога"""
        pass

    def saveData(self):
        if self.checkDataEntered():
            try:
                if self.object != None:  # редактировать
                    self.object.update(QtGui.qApp.db, self.getObject())
                else:  # добавить
                    self.getObject().addToDB(QtGui.qApp.db)
                self.parentWidget().updateInfo()
            except CDatabaseException, e:
                QtGui.QMessageBox.critical(self, u'Ошибка базы данных', unicode(e), QtGui.QMessageBox.Close)
            self.parentWidget().updateTable()
            return True
        return False


class CHolidayDialog(CMyDialog, Ui_HolidayDialog):
    u"""Диалог для редактирования данных о празднике"""

    def setObject(self, hol):
        self.date.setDate(hol.getDate())
        self.endDate.setDate(hol.getEndDate())
        self.text.setText(hol.getText())
        self.checkStart.setChecked(hol.hasStartYear())
        self.spinStart.setValue(hol.getStartYear())
        self.spinStart.setEnabled(hol.hasStartYear())
        self.checkFinish.setChecked(hol.hasFinishYear())
        self.spinFinish.setValue(hol.getFinishYear())
        self.spinFinish.setEnabled(hol.hasFinishYear())

    def getObject(self):
        date = self.date.date()
        endDate = self.endDate.date()
        return CHoliday(
            date.day(),
            date.month(),
            self.spinStart.value() if self.checkStart.isChecked() else None,
            self.spinFinish.value() if self.checkFinish.isChecked() else None,
            self.text.text(),
            endDate
        )

    def checkDataEntered(self):
        hol = self.getObject()
        if hol.getStartYear() > hol.getFinishYear():
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка при вводе данных', u'Начальный год не может быть больше конечного!',
                QtGui.QMessageBox.Close
            )
            return False

        if self.date.date() > self.endDate.date():
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка при вводе данных', u'Дата начала периода не может быть больше дата конца периода!',
                QtGui.QMessageBox.Close
            )
            return False

        # проверка на пересечение
        self.parentWidget().list.load(QtGui.qApp.db)
        for ex in self.parentWidget().list.getList():
            if hol.intersects(ex) and ex != self.object:
                QtGui.QMessageBox.critical(
                    self,
                    u'Ошибка при вводе данных', u'Диапазон дат пересекается с уже существующим!',
                    QtGui.QMessageBox.Close
                )
                return False
        return True


class CChangeDayDialog(CMyDialog, Ui_ChangeDayDialog):
    u"""Диалог для редактирования данных о переносе"""

    def setObject(self, ch):
        self.date.setDate(ch.getDate())
        self.dateChange.setDate(ch.getChangeDate())
        self.text.setText(ch.getText())

    def getObject(self):
        return CChangeDay(self.date.date(), self.dateChange.date(), self.text.text())

    def checkDataEntered(self):
        chday = self.parentWidget().list.getException(self.getObject().getDate())
        if (chday != None) and (chday != self.object):
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка при вводе данных', u'Такая дата уже существует!',
                QtGui.QMessageBox.Close
            )
            return False
        return True
