# -*- coding: utf-8 -*-

from math import ceil, sqrt

import sip
from PyQt4.QtGui import QFrame, QSizePolicy, QPushButton, QStyle, QPixmap, QPainter, QPen, QIcon, QColor, QGridLayout, \
    QColorDialog, QBrush
from PyQt4.QtCore import Qt, SIGNAL, QRect, QEventLoop
from PyQt4 import QtGui

from library.Utils import trUtf8


class CColorPickerButton(QFrame):
    __pyqtSignals__ = ('clicked()',
                      )
    def __init__(self, parent):
        super(QFrame, self).__init__(parent)
        self.setFrameStyle(self.StyledPanel)

    def mousePressEvent(self, e):
        self.setFrameShadow(self.Sunken)
        self.update()

    def mouseMoveEvent(self, e):
        self.setFocus()
        self.update()

    def mouseReleaseEvent(self, e):
        self.setFrameShadow(self.Raised)
        self.repaint()
        self.emit(SIGNAL('clicked()'))

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            QtGui.qApp.sendEvent(self.parent(), e)
        elif e.key() in (Qt.Key_Enter, Qt.Key_Space, Qt.Key_Return):
            self.setFrameShadow(self.Sunken)
            self.update()
        else:
            super(QFrame, self).keyPressEvent(e)

    def keyReleaseEvent(self, e):
        if e.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
            QtGui.qApp.sendEvent(self.parent(), e)
        elif e.key() in (Qt.Key_Enter, Qt.Key_Space, Qt.Key_Return):
            self.setFrameShadow(self.Raised)
            self.repaint()
            self.emit(SIGNAL('clicked()'))
        else:
            super(QFrame, self).keyReleaseEvent(e)

    def paintEvent(self, e):
        super(QFrame, self).paintEvent(e)

        p = QPainter(self)
        p.fillRect(self.contentsRect(), self.palette().button())

        r = self.rect()

        offset = 1 if self.frameShadow() == self.Sunken else 0

        pen = QPen(self.palette().buttonText(), 1)
        p.setPen(pen)

        p.drawRect(r.center().x() + offset - 4, r.center().y() + offset, 1, 1)
        p.drawRect(r.center().x() + offset    , r.center().y() + offset, 1, 1)
        p.drawRect(r.center().x() + offset + 4, r.center().y() + offset, 1, 1)
        if self.hasFocus():
            p.setPen(QPen(Qt.black, 0, Qt.SolidLine))
            p.drawRect(0, 0, self.width() - 1, self.height() - 1)

        p.end()

    def focusInEvent(self, e):
        self.setFrameShadow(self.Raised)
        self.update()
        super(QFrame, self).focusOutEvent(e)

    def focueOutEvent(self, e):
        self.setFrameShadow(self.Raised)
        self.update()
        super(QFrame, self).focusOutEvent(e)


class CColorPickerItem(QFrame):
    __pyqtSignals__ = ('clicked()',
                       'selected()',
                      )
    def __init__(self, color=Qt.white, text='', parent=None):
        super(QFrame, self).__init__(parent)
        self.c = color
        self.t = text
        self.sel = False

        self.setToolTip(self.t)
        self.setFixedWidth(24)
        self.setFixedHeight(21)

    def color(self):
        return self.c

    def text(self):
        return self.t

    def setSelected(self, selected):
        self.sel = selected
        self.update()

    def isSelected(self):
        return self.sel

    def setColor(self, color, text=""):
        self.c = color
        self.t = text
        self.setToolTip(self.t)
        self.update()

    def mousePressEvent(self, e):
        self.setFocus()
        self.update()

    def mouseReleaseEvent(self, e):
        self.sel = True
        self.emit(SIGNAL('selected()'))

    def mouseMoveEvent(self, e):
        self.setFocus()
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        w = self.width()
        h = self.height()

        p.setPen(QPen(Qt.gray, 0, Qt.SolidLine))

        if self.sel:
            p.drawRect(1, 1, w-3, h-3)

        p.setPen(QPen(Qt.black, 0, Qt.SolidLine))
        p.drawRect(3, 3, w-7, h-7)
        p.fillRect(QRect(4, 4, w-8, h-8), QBrush(self.c))

        if self.hasFocus():
            p.drawRect(0, 0, w-1, h-1)


class CColorPickerPopup(QFrame):
    __pyqtSignals__ = ('selected(QColor)',
                       'hid()'
                      )
    def __init__(self, width, withColorDialog, parent=None):
        super(QFrame, self).__init__(parent, Qt.Popup)

        self.setFrameStyle(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.cols = width

        if withColorDialog:
            self.moreButton = CColorPickerButton(self)
            self.moreButton.setFixedWidth(24)
            self.moreButton.setFixedHeight(21)
            self.moreButton.setFrameRect(QRect(2, 2, 20, 17))
            self.connect(self.moreButton, SIGNAL('clicked()'), self.getColorFromDialog)
        else:
            self.moreButton = None

        self.eventLoop = None
        self.grid = None
        self.items = []
        self.widgetAt = {}
        self.lastSel = QColor()
        self.regenerateGrid()


    def __del__(self):
        if self.eventLoop:
            self.eventLoop.exit()

    def find(self, col):
        for i in xrange(len(self.items)):
            if self.items[i] and self.items[i].color() == col:
                return self.items[i]
        return None

    def insertColor(self, col, text, index):
        existingItem = self.find(col)
        lastSelectedItem = self.find(self.lastSelected())

        if existingItem:
            if lastSelectedItem and existingItem != lastSelectedItem:
                lastSelectedItem.setSelected(False)
            existingItem.setFocus()
            existingItem.setSelected(True)
            return

        item = CColorPickerItem(col, text, self)
        if lastSelectedItem:
            lastSelectedItem.setSelected(False)
        else:
            item.setSelected(True)
            self.lastSel = col
        item.setFocus()

        self.connect(item, SIGNAL('selected()'), self.updateSelected)

        if index == -1:
            index = len(self.items)

        self.items.insert(index, item)
        self.regenerateGrid()

        self.update()

    def insertColors(self, colList):
        lastSelectedItem = self.find(self.lastSelected())
        for col, text in colList:
            existingItem = self.find(col)

            if existingItem:
                continue

            item = CColorPickerItem(col, text, self)
            # if lastSelectedItem:
            #     lastSelectedItem.setSelected(False)
            # else:
            #     item.setSelected(True)
            #     self.lastSel = col
            # item.setFocus()

            self.connect(item, SIGNAL('selected()'), self.updateSelected)

            index = len(self.items)
            self.items.insert(index, item)

        self.regenerateGrid()
        self.update()

    def color(self, index):
        if index < 0 or index > (len(self.items) - 1):
            return QColor()
        return self.items[index].color()

    def exec_(self):
        self.show()

        e = QEventLoop()
        self.eventLoop = e

        e.exec_()

        self.eventLoop = None

    def updateSelected(self):
        layoutItem = self.grid.itemAt(0)
        i = 0
        while layoutItem:
            w = layoutItem.widget()
            if w and isinstance(w, CColorPickerItem):
                if w != self.sender():
                    w.setSelected(False)
            i += 1
            layoutItem = self.grid.itemAt(i)

        s = self.sender()
        if s and isinstance(s, CColorPickerItem):
            item = s
            self.lastSel = item.color()
            self.emit(SIGNAL('selected(QColor)'), item.color())

        self.hide()

    def mouseReleaseEvent(self, e):
        if not self.rect().contains(e.pos()):
            self.hide()

    def keyPressEvent(self, e):
        curRow = 0
        curCol = 0

        foundFocus = False
        for j in xrange(self.grid.rowCount()):
            if foundFocus:
                break
            for i in xrange(self.grid.columnCount()):
                w = self.widgetAt.get(j, {}).get(i, None)
                if w and w.hasFocus():
                    curRow = j
                    curCol = i
                    foundFocus = True
                    break

        if e.key() == Qt.Key_Left:
            if curCol > 0:
                curCol -= 1
            elif curRow > 0:
                curRow -= 1
                curCol = self.grid.columnCount() - 1
        elif e.key() == Qt.Key_Right:
            if curCol < self.grid.columnCount() - 1 and self.widgetAt[curRow][curCol+1]:
                curCol += 1
            elif curRow < self.grid.rowCount() - 1:
                curRow += 1
                curCol = 0
        elif e.key() == Qt.Key_Up:
            if curRow > 0:
                curRow -= 1
            else:
                curCol = 0
        elif e.key() == Qt.Key_Down:
            if curRow < self.grid.rowCount() - 1:
                w = self.widgetAt.get(curRow + 1, {}).get(curCol, None)
                if w:
                    curRow += 1
                else:
                    for i in xrange(self.grid.columnCount()):
                        if not self.widgetAt.get(curRow+1, {}).get(i, None):
                            curCol = i - 1
                            curRow += 1
        elif e.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter):
            w = self.widgetAt.get(curRow, {}).get(curCol, None)
            if w and (isinstance(w, CColorPickerItem) or isinstance(w, QPushButton)):
                w.setSelected(True)
                layoutItem = self.grid.itemAt(0)
                i = 0
                while layoutItem:
                    wi = layoutItem.widget()
                    if wi and isinstance(wi, CColorPickerItem):
                        if wi != w:
                            wi.setSelected(False)
                    i += 1
                    layoutItem = self.grid.itemAt(i)

                self.lastSel = w.color()
                self.emit(SIGNAL('selected(QColor)'), w.color())
                self.hide()
        elif e.key() == Qt.Key_Escape:
            self.hide()
        else:
            e.ignore()

        self.widgetAt.get(curRow, {}).get(curCol, None).setFocus()

    def hideEvent(self, e):
        if self.eventLoop:
            self.eventLoop.exit()

        self.setFocus()
        self.emit(SIGNAL('hid()'))
        QFrame.hideEvent(self, e)

    def lastSelected(self):
        return self.lastSel

    def showEvent(self, e):
        foundSelected = False
        for i in xrange(self.grid.columnCount()):
            for j in xrange(self.grid.rowCount()):
                w = self.widgetAt.get(j, {}).get(i, None)
                if isinstance(w, CColorPickerItem) and w.isSelected():
                    w.setFocus()
                    foundSelected = True
                    break
        if not foundSelected:
            if not self.items:
                self.setFocus()
            else:
                self.widgetAt.get(0, {}).get(0, None).setFocus()

    def regenerateGrid(self):
        self.widgetAt.clear()

        columns = self.cols
        if columns == -1:
            columns = ceil(sqrt(len(self.items)))

        if self.grid:
            sip.delete(self.grid)
        self.grid = QGridLayout(self)
        self.grid.setMargin(1)
        self.grid.setSpacing(0)

        ccol = 0
        crow = 0
        for i in xrange(len(self.items)):
            if self.items[i]:
                self.widgetAt.setdefault(crow, {})[ccol] = self.items[i]
                self.grid.addWidget(self.items[i], crow, ccol)
                ccol += 1
                if ccol == columns:
                    ccol = 0
                    crow += 1
        if self.moreButton:
            self.grid.addWidget(self.moreButton, crow, ccol)
            self.widgetAt.setdefault(crow, {})[ccol] = self.moreButton

        self.updateGeometry()

    def getColorFromDialog(self):
        rgb, ok = QColorDialog.getRgba(self.lastSel.rgba(), self.parentWidget())
        if not ok:
            return
        col = QColor.fromRgba(rgb)
        self.insertColor(col, self.tr("Custom"), -1)
        self.lastSel = col
        self.emit(SIGNAL("selected(QColor)"), col)


class CColorPicker(QPushButton):
    __pyqtSignals__ = ('colorChanged(QColor)',
                        )
    def __init__(self, parent=None, columns=-1, enableColorDialog=True):
        QPushButton.__init__(self, parent)
        self.withColorDialog = enableColorDialog
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.setAutoDefault(False)
        self.setAutoFillBackground(True)
        self.setCheckable(True)

        # Set text
        self.setText(self.tr("White"))
        self.firstInserted = False

        # Create and set icon
        self.col = Qt.white
        self.dirty = True

        # Create color grid popup and connect to it
        self.popup = CColorPickerPopup(columns, self.withColorDialog, self)

        self.connect(self.popup, SIGNAL('selected(QColor)'), self.setCurrentColor)
        self.connect(self.popup, SIGNAL('hid()'), self.popupClosed)

        # Connect this push button's pressed() signal
        self.connect(self, SIGNAL('toggled(bool)'), self.buttonPressed)

        #self.setStandardColors()

    def buttonPressed(self, toggled):
        if not toggled:
            return

        desktop = QtGui.QApplication.desktop().geometry()
        pos = self.mapToGlobal(self.rect().bottomLeft())
        if pos.x() < desktop.left():
            pos.setX(desktop.left())
        if pos.y() < desktop.top():
            pos.setY(desktop.top())

        if (pos.x() + self.popup.sizeHint().width()) > desktop.width():
            pos.setX(desktop.width() - self.popup.sizeHint().width())
        if (pos.y() + self.popup.sizeHint().height()) > desktop.bottom():
            pos.setY(desktop.bottom() - self.popup.sizeHint().height())

        self.popup.move(pos)

        item = self.popup.find(self.col)
        if item:
            item.setSelected(True)

        self.clearFocus()
        self.update()

        self.popup.setFocus()
        self.popup.show()

    def paintEvent(self, e):
        if self.dirty:
            iconSize = self.style().pixelMetric(QStyle.PM_SmallIconSize)
            pix = QPixmap(iconSize, iconSize)
            pix.fill(self.palette().button().color())
            p = QPainter(pix)


            w = pix.width()
            h = pix.height()
            p.setPen(QPen(Qt.gray))
            p.setBrush(self.col)
            p.drawRect(2, 2, w-5, h-5)
            self.setIcon(QIcon(pix))

            self.dirty = False
            p.end()
        QPushButton.paintEvent(self, e)
        #super(QPushButton, self).paintEvent(e)

    def popupClosed(self):
        self.setChecked(False)
        self.setFocus()

    def color(self, index):
        return self.popup.color(index)

    def setStandardColors(self):
        self.insertColors([(Qt.black, trUtf8(u'Чёрный', u"Black")),
                           (Qt.white, trUtf8(u'Белый', u"White")),
                           (Qt.red, trUtf8(u'Красный', u"Red")),
                           (Qt.darkRed, trUtf8(u'Тёмно-красный', u"Dark red")),
                           (Qt.green, trUtf8(u'Зелёный', u"Green")),
                           (Qt.darkGreen, trUtf8(u'Тёмно-зеленый', u"Dark green")),
                           (Qt.blue, trUtf8(u'Синий', u"Blue")),
                           (Qt.darkBlue, trUtf8(u'Тёмно-синий', u"Dark blue")),
                           (Qt.cyan, trUtf8(u'Голубой', u"Cyan")),
                           (Qt.darkCyan, trUtf8(u'Сине-зелёный', u"Dark cyan")),
                           (Qt.magenta, trUtf8(u'Пурпурный', u"Magenta")),
                           (Qt.darkMagenta, trUtf8(u'Фиолетовый', u"Dark magenta")),
                           (Qt.yellow, trUtf8(u'Жёлтый', u"Yellow")),
                           (Qt.darkYellow, trUtf8(u'Оливковый', u"Dark yellow")),
                           (Qt.gray, trUtf8(u'Серый', u"Gray")),
                           (Qt.darkGray, trUtf8(u'Тёмно-серый', u"Dark gray")),
                           (Qt.lightGray, trUtf8(u'Светло-серый', u"Light gray")),
                           ])


    def setCurrentColor(self, color):
        if color is None: return
        color = QColor(color)
        if self.col == color or not color.isValid():
            return

        item = self.popup.find(color)
        if not item:
            self.insertColor(color, self.tr('Custom'))
            item = self.popup.find(color)

        self.col = color
        self.setText(item.text())

        self.dirty = True

        self.popup.hide()
        self.repaint()

        item.setSelected(True)
        self.emit(SIGNAL('colorChanged(QColor'), color)

    def currentColor(self):
        return self.col

    def currentColorName(self):
        return self.col.name()

    def insertColor(self, color, text = "", index = -1):
        self.popup.insertColor(color, text, index)
        if not self.firstInserted:
            self.col = color
            self.setText(text)
            self.firstInserted = True

    def insertColors(self, colorList):
        self.popup.insertColors(colorList)
        if not self.firstInserted:
            col, text = colorList[0]
            self.col = col
            self.setText(text)
            self.firstInserted = True

    def setColorDialogEnabled(self, enabled):
        self.withColorDialog = enabled

    def colorDialogEnabled(self):
        return self.withColorDialog

    def getColor(self, point, allowCustomColors=True):
        popup = CColorPickerPopup(-1, allowCustomColors)

        popup.insertColor(Qt.black, trUtf8(u'Чёрный', u"Black"), 0)
        popup.insertColor(Qt.white, trUtf8(u'Белый', u"White"), 1)
        popup.insertColor(Qt.red, trUtf8(u'Красный', u"Red"), 2)
        popup.insertColor(Qt.darkRed, trUtf8(u'Тёмно-красный', u"Dark red"), 3)
        popup.insertColor(Qt.green, trUtf8(u'Зелёный', u"Green"), 4)
        popup.insertColor(Qt.darkGreen, trUtf8(u'Тёмно-зеленый', u"Dark green"), 5)
        popup.insertColor(Qt.blue, trUtf8(u'Синий', u"Blue"), 6)
        popup.insertColor(Qt.darkBlue, trUtf8(u'Тёмно-синий', u"Dark blue"), 7)
        popup.insertColor(Qt.cyan, trUtf8(u'Голубой', u"Cyan"), 8)
        popup.insertColor(Qt.darkCyan, trUtf8(u'Сине-зелёный', u"Dark cyan"), 9)
        popup.insertColor(Qt.magenta, trUtf8(u'Пурпурный', u"Magenta"), 10)
        popup.insertColor(Qt.darkMagenta, trUtf8(u'Фиолетовый', u"Dark magenta"), 11)
        popup.insertColor(Qt.yellow, trUtf8(u'Жёлтый', u"Yellow"), 12)
        popup.insertColor(Qt.darkYellow, trUtf8(u'Тёмно жёлтый', u"Dark yellow"), 13)
        popup.insertColor(Qt.gray, trUtf8(u'Серый', u"Gray"), 14)
        popup.insertColor(Qt.darkGray, trUtf8(u'Тёмно-серый', u"Dark gray"), 15)
        popup.insertColor(Qt.lightGray, trUtf8(u'Светло-серый', u"Light gray"), 16)

        popup.move(point)
        popup.exec_()
        return popup.lastSelected()