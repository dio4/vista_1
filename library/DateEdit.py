# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4.QtGui import *

from library.calendar import *


class CDateValidator(QValidator):
    def __init__(self, parent, format, canBeEmpty):
        QValidator.__init__(self, parent)
        self.min=QDate(1900, 1, 1)
        self.max=QDate(2099,12,31)
        self.format=format
        self.canBeEmpty = canBeEmpty


    def inputIsEmpty(self, input):
        return not unicode(input).strip(' 0.-')


    def validate(self, input, pos):
        if self.inputIsEmpty(input):
            if self.canBeEmpty:
                return (QValidator.Acceptable, pos)
            else:
                return (QValidator.Intermediate, pos)
        else:
            d = QDate.fromString(input, self.format)
            if d.isValid():
                if self.min!=None and d<self.min:
                    return (QValidator.Intermediate, pos)
                elif self.max!=None and d>self.max:
                    return (QValidator.Intermediate, pos)
                else:
                    return (QValidator.Acceptable, pos)
            else:
                return (QValidator.Intermediate, pos)


    def fixup(self, input):
        if self.inputIsEmpty(input) and self.canBeEmpty:
            newInput = ''
        else:
            d = QDate.fromString(input, self.format)
            newInput = d.toString(self.format)
        if not newInput:
            input.clear()


class CCalendarPopup(QFrame):
    def __init__(self, parent = None):
        QFrame.__init__(self, parent, Qt.Popup)
#        self.setFrameShape(QFrame.Panel)
        self.setFrameShape(QFrame.StyledPanel)
        self.setAttribute(Qt.WA_WindowPropagation)
        self.initialDate = QDate()
        self.dateChanged = False
        self.disabledDates = []
        self.calendar = CCalendarWidget(self)
        self.calendar.setList(QtGui.qApp.calendarInfo)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.widgetLayout = QVBoxLayout(self)
        self.widgetLayout.setMargin(0)
        self.widgetLayout.setSpacing(0)
        self.widgetLayout.addWidget(self.calendar)
        self.connect(self.calendar,QtCore.SIGNAL('activated(QDate)'), self.dateSelected)
        self.connect(self.calendar,QtCore.SIGNAL('clicked(QDate)'), self.dateSelected)
        self.connect(self.calendar,QtCore.SIGNAL('selectionChanged()'), self.dateSelectionChanged)
        self.calendar.setFocus()


    def setInitialDate(self, date):
        self.initialDate = date
        self.dateChanged = False
        self.calendar.setSelectedDate(date)


    def dateSelected(self, date):
        self.dateChanged=True
        if self.disabledDates and date in self.disabledDates:
            return False
        self.close()
        self.emit(QtCore.SIGNAL('activated(QDate)'), date)


    def mousePressEvent(self, event):
        dateTime = self.parentWidget()
        if dateTime!=None:
            opt=QStyleOptionComboBox()
            opt.init(dateTime)
            arrowRect = dateTime.style().subControlRect(
                QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, dateTime)
            arrowRect.moveTo(dateTime.mapToGlobal(arrowRect.topLeft()))
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(Qt.WA_NoMouseReplay)
        QFrame.mousePressEvent(self, event)


    def mouseReleaseEvent(self, event):
#        self.emit(QtCore.SIGNAL('resetButton()'))
        self.parent().mouseReleaseEvent(event)
        pass


    def event(self, event):
        if event.type()==QEvent.KeyPress:
            if event.key()==Qt.Key_Escape:
                self.dateChanged = False
        return QFrame.event(self, event)


    def dateSelectionChanged(self):
        date = self.calendar.selectedDate()
        if self.disabledDates and date in self.disabledDates:
            return False
        self.dateChanged=True
        self.emit(QtCore.SIGNAL('newDateSelected(QDate)'), self.calendar.selectedDate())


    def hideEvent(self, event):
        if not self.dateChanged:
            self.dateSelected(self.initialDate)

    def setDatesForDisable(self, dates):
        self.disabledDates = dates


class CDateEdit(QComboBox):
    __pyqtSignals__ = ('dateChanged(const QDate &)',
                      )

    def __init__(self, parent = None):
        QComboBox.__init__(self, parent)
        self._hiddenDates = []
        self.setMinimumContentsLength(10)
        self.highlightRedDate = QtGui.qApp.highlightRedDate()
#        self.parent=parent
        self.lineEdit=QLineEdit()
        self.lineEdit.setInputMask('99.99.9999')
        self.validator=CDateValidator(self, 'dd.MM.yyyy', False)
        self.lineEdit.setValidator(self.validator)
        self.setLineEdit(self.lineEdit)
        self.lineEdit.setText(QDate.currentDate().toString(self.validator.format))
        self.lineEdit.setCursorPosition(0)
        self.calendarPopup=None
        self.oldDate = QtCore.QDate()
        self.connect(self.lineEdit, QtCore.SIGNAL('textEdited(QString)'), self.onTextChange)
        self.connect(self.lineEdit, QtCore.SIGNAL('editingFinished()'), self.onEditingFinished)


    def minimumDate(self):
        return self.validator.min


    def setMinimumDate(self, min):
        if isinstance(min, QDate) and min.isValid():
            max =self.validator.max
            if max.isValid() and max<min:
                max = min
            self.setRange(min, max)


    def clearMinimumDate(self):
        self.setMinimumDate(QDate())


    def maximumDate(self):
        return self.validator.max


    def setMaximumDate(self, max):
        if isinstance(max, QDate) and max.isValid():
            min=self.validator.min
            if min.isValid() and min>max:
                min=max
            self.setRange(min, max)


    def clearMaximumDate(self):
        self.setMaximumDate(QDate())


    def setDateRange(self, min, max):
        if  isinstance(min, QDate) and isinstance(max, QDate) and min.isValid() and max.isValid():
            self.validator.min=min
            self.validator.max=max


    def setRange(self, min, max):
        self.setDateRange(min, max)


    def displayFormat(self):
        return self.format()


    def setDisplayFormat(self, format):
        self.setFormat(format)


    def format(self):
        return self.validator.format


    def setFormat(self, format):
        self.validator.format=format


    def canBeEmpty(self, value=True):
        self.validator.canBeEmpty = value


    def setHighlightRedDate(self, value=True):
        self.highlightRedDate = value and QtGui.qApp.highlightRedDate()


    def setCalendarPopup(self, value=True):
        pass


    def showPopup(self):
        if not self.calendarPopup:
            self.calendarPopup = CCalendarPopup(self)

            self.connect(self.calendarPopup,QtCore.SIGNAL('newDateSelected(QDate)'), self.calendarSelectionChanged)
#            self.connect(self.calendarPopup,QtCore.SIGNAL('hidingCalendar(QDate)'), self.setDate)
            self.connect(self.calendarPopup,QtCore.SIGNAL('activated(QDate)'), self.setDate)
            self.connect(self.calendarPopup,QtCore.SIGNAL('activated(QDate)'), self.calendarPopup.close)
#            self.connect(self.calendarPopup,QtCore.SIGNAL('resetButton()'), self._q_resetButton)

        self.calendarPopup.calendar.setMinimumDate(self.minimumDate())
        self.calendarPopup.calendar.setMaximumDate(self.maximumDate())
        self.calendarPopup.calendar.setColor([dict(brush=QtGui.QColor(205, 205, 205), values=self._hiddenDates)], disabledDates=self._hiddenDates)
        self.calendarPopup.setDatesForDisable(self._hiddenDates)
        date = self.date()
        if not date.isValid():
            date = QDate.currentDate()
        self.calendarPopup.setInitialDate(date)

        pos = self.rect().bottomLeft()
#        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
#        pos2 = self.mapToGlobal(pos2)
        size=self.calendarPopup.sizeHint()
        size.setWidth(size.width()+20) # magic. похоже, что sizeHint считается неправильно. русские буквы виноваты?
        screen = QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )

#        if (pos.y() + size.height() > screen.bottom()):
#            pos.setY(pos2.y() - size.height())
#        elif (pos.y() < screen.top()):
#            pos.setY(screen.top())
#        if (pos.y() < screen.top()):
#            pos.setY(screen.top())
#        if (pos.y()+size.height() > screen.bottom()):
#            pos.setY(screen.bottom()-size.height())
        self.calendarPopup.move(pos)
        self.calendarPopup.show()

    def calendarSelectionChanged(self, date):
        self.setDate(date, True)

    def setDate(self, date, silent=False):
        if isinstance(date, QDateTime):
            date = date.date
        if date is None:
            date = QDate()

        self.setColor(date)
        self.lineEdit.setText(date.toString(self.validator.format))
        self.lineEdit.setCursorPosition(0)
        if not silent and self.oldDate != date:
            self.oldDate = date
            self.emit(QtCore.SIGNAL('dateChanged(QDate)'), date)

    def setColor(self, date):
        palette = QPalette()
        if self.highlightRedDate and date and QtGui.qApp.calendarInfo.getDayOfWeek(date) in [6,7]:
            palette.setColor(QPalette.Text, QtGui.QColor(255, 0, 0))
        self.lineEdit.setPalette(palette)


    def setInvalidColor(self):
        palette = QPalette()
        if QtGui.qApp.highlightInvalidDate():
            palette.setColor(QPalette.Text, QtGui.QColor(255, 0, 255))
        self.lineEdit.setPalette(palette)


    def selectAll(self):
        self.lineEdit.selectAll()
        self.lineEdit.setCursorPosition(0)


    def setCursorPosition(self,  pos=0):
        self.lineEdit.setCursorPosition(pos)


    def text(self):
        return self.lineEdit.text()


    def date(self):
        return QDate.fromString(self.text(), self.validator.format)


    def onTextChange(self, text):
        state, pos = self.validator.validate(self.text(), 0)
        if state == QValidator.Acceptable:
            date = self.date()
            self.setColor(date)
        else:
            if not unicode(text).replace('.', ''):
                self.emit(QtCore.SIGNAL('dateChanged(QDate)'), QDate())
            self.setInvalidColor()

    def onEditingFinished(self):
        if self.date() != self.oldDate:
            self.oldDate = self.date()
            self.emit(QtCore.SIGNAL('dateChanged(QDate)'), self.date())



    def currentSection(self):
        pos = self.lineEdit.cursorPosition()
        if pos>=6:
            return QtGui.QDateTimeEdit.YearSection
        elif pos>=3:
            return QtGui.QDateTimeEdit.MonthSection
        else:
            return QtGui.QDateTimeEdit.DaySection


    def event(self, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Equal or (key == Qt.Key_Space and not self.date().isValid()):
                    self.setDate(QDate.currentDate())
                    event.accept()
                    return True
            if key in (Qt.Key_Plus, Qt.Key_Minus):
                d = self.date()
                if not d.isValid():
                    d = QDate.currentDate()
                step = 1 if key  == Qt.Key_Plus else -1
                if self.currentSection() == QtGui.QDateTimeEdit.YearSection:
                    d = d.addYears(step)
                elif self.currentSection() == QtGui.QDateTimeEdit.MonthSection:
                    d = d.addMonths(step)
#                elif event.modifiers() & Qt.ControlModifier:
#                    d = d.addDays(step*7)
                else:
                    d = d.addDays(step)
                pos = self.lineEdit.cursorPosition()
                self.setDate(d)
                self.lineEdit.setCursorPosition(pos)
                event.accept()
                return True
        return QtGui.QComboBox.event(self, event)

    def setHiddenDates(self, dates):
        self._hiddenDates = dates


#    def _q_resetButton(self):
#        if (self.arrowState == QStyle.State_None):
#            return
#        self.arrowState=QStyle.State_None
#        self.buttonState = 0
#        self.hoverControl = QStyle.SC_ComboBoxFrame
#        self.q.update()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialog = QtGui.QDialog()
    gridlayout = QtGui.QGridLayout(dialog)
    gridlayout.setMargin(9)
    gridlayout.setSpacing(6)
#    cv = QtGui.QDateEdit(dialog)
#    cv.setCalendarPopup(True)
    cv = CDateEdit(dialog)
    gridlayout.addWidget(cv,0,0,1,1)
    out = QtGui.QLabel()
    gridlayout.addWidget(out,1,0,1,1)
    dialog.resize(QtCore.QSize(300, 300))
    out.setText('00.00.0000')
    le=cv.lineEdit
    QtCore.QObject.connect(le,QtCore.SIGNAL("returnPressed()"), lambda :(out.setText(le.text())))
    dialog.show()
    sys.exit(app.exec_())
