# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

__author__ = 'atronah'


class CExtendedTableView(QtGui.QTableView):
    """
        Safety extends functional of QTableView.

            Added support Frozen row.
            Added support change cell span by model signals.
    """

    def __init__(self, parent=None):
        super(CExtendedTableView, self).__init__(parent)
        self._frozenView = None
        self._frozenOrientation = QtCore.Qt.Horizontal
        self._frozenCount = 0

    def frozenView(self):
        return self._frozenView

    def initFreeze(self, orientation=QtCore.Qt.Horizontal, count=1, color=None):
        self._frozenCount = count
        self._frozenOrientation = orientation
        self._frozenView = QtGui.QTableView(self)
        self._frozenView.setModel(self.model())

        if isinstance(color, QtGui.QColor):
            self._frozenView.setStyleSheet('QTableView {background-color: %s;}' % color.name())

        self._frozenView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._frozenView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        if orientation == QtCore.Qt.Horizontal:
            # синхронизация скроллинга
            self._frozenView.setHorizontalScrollMode(self.horizontalScrollMode())
            self.horizontalScrollBar().valueChanged.connect(self._frozenView.horizontalScrollBar().setValue)
            self._frozenView.horizontalScrollBar().valueChanged.connect(self.horizontalScrollBar().setValue)

            self._frozenView.horizontalHeader().hide()
            self._frozenView.verticalHeader().sectionResized.connect(self.resizeFrozenVerticalSection)
        else:
            # синхронизация скроллинга
            self._frozenView.setVerticalScrollMode(self.verticalScrollMode())
            self.verticalScrollBar().valueChanged.connect(self._frozenView.verticalScrollBar().setValue)
            self._frozenView.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)

            self._frozenView.verticalHeader().hide()
            self._frozenView.horizontalHeader().sectionResized.connect(self.resizeFrozenHorizontalSection)

        self._frozenView.selectionModel().currentChanged.connect(self.changeFrozenCurrent)
        self.selectionModel().currentChanged.connect(self.changeFrozenCurrent)

        self.horizontalHeader().sectionResized.connect(self.resizeFrozenHorizontalSection)
        self.verticalHeader().sectionResized.connect(self.resizeFrozenVerticalSection)

        self._frozenView.installEventFilter(self)
        self.updateFrozenGeometry()
        self._frozenView.show()

    def eventFilter(self, obj, event):
        if obj == self._frozenView and event.type() == QtCore.QEvent.Wheel:
            event.ignore()
        return super(CExtendedTableView, self).eventFilter(obj, event)

    def resizeEvent(self, event):
        super(CExtendedTableView, self).resizeEvent(event)
        self.updateFrozenGeometry()

    def setHorizontalScrollMode(self, mode):
        super(CExtendedTableView, self).setHorizontalScrollMode(mode)
        if self._frozenView is not None:
            self._frozenView.setHorizontalScrollMode(mode)

    def setVerticalScrollMode(self, mode):
        super(CExtendedTableView, self).setVerticalScrollMode(mode)
        if self._frozenView is not None:
            self._frozenView.setVerticalScrollMode(mode)

    @QtCore.pyqtSlot(int, int, int)
    def resizeFrozenHorizontalSection(self, logicalIndex, oldSize, newSize):
        if self._frozenView is None:
            return

        if self._frozenOrientation == QtCore.Qt.Horizontal:
            self._frozenView.horizontalHeader().resizeSection(logicalIndex, newSize)
        else:
            if logicalIndex in xrange(self._frozenCount):
                self.horizontalHeader().resizeSection(logicalIndex, newSize)
                self._frozenView.horizontalHeader().resizeSection(logicalIndex, newSize)
                self.updateFrozenGeometry()

    @QtCore.pyqtSlot(int, int, int)
    def resizeFrozenVerticalSection(self, logicalIndex, oldSize, newSize):
        if self._frozenView is None:
            return

        if self._frozenOrientation == QtCore.Qt.Vertical:
            self._frozenView.verticalHeader().resizeSection(logicalIndex, newSize)
        else:
            if logicalIndex in xrange(self._frozenCount):
                self.verticalHeader().resizeSection(logicalIndex, newSize)
                self._frozenView.verticalHeader().resizeSection(logicalIndex, newSize)
                self.updateFrozenGeometry()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def changeFrozenCurrent(self, current, previous):
        if self._frozenView is None:
            return

        currentValue = current.row() if self._frozenOrientation == QtCore.Qt.Horizontal else current.column()
        previousValue = previous.row() if self._frozenOrientation == QtCore.Qt.Horizontal else previous.column()

        # Если текущий и предыдущий индексы находятся в разных отображениях
        # (один во frozen-области, другой в основном отображении)
        if (previousValue in xrange(self._frozenCount)) ^ (currentValue in xrange(self._frozenCount)):
            # перенести фокус с замороженной области в основную или наоборот
            isFrozenIn = currentValue in xrange(self._frozenCount)
            if isFrozenIn:
                self.selectionModel().clearSelection()
                self._frozenView.selectionModel().setCurrentIndex(current, QtGui.QItemSelectionModel.SelectCurrent)
                self._frozenView.setFocus(QtCore.Qt.ActiveWindowFocusReason)
            else:
                if self._frozenOrientation == QtCore.Qt.Horizontal:
                    self._frozenView.scrollToTop()
                else:
                    self._frozenView.scrollTo(previous)
                self._frozenView.selectionModel().clearSelection()
                self.selectionModel().setCurrentIndex(current, QtGui.QItemSelectionModel.SelectCurrent)
                self.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        # Если происходит уменьшение индекса
        elif previousValue > currentValue:
            # изменить скрол для предотвращение выеделения элемента за замороженной частью таблицы
            if self.visualRect(current).intersects(self._frozenView.geometry()):
                # Вычисление нового столбца или строки для изменения скрола
                newValue = max(currentValue - 2, 0)
                newIndex = self.model().index(newValue,
                                              current.column()) if self._frozenOrientation == QtCore.Qt.Horizontal \
                    else self.model().index(current.row(), newValue)
                self.scrollTo(newIndex)

    def updateFrozenGeometry(self):
        if self._frozenView is None:
            return

        if self._frozenOrientation == QtCore.Qt.Horizontal:
            x = 0
            y = self.horizontalHeader().height()
            width = self.viewport().width() + self.verticalHeader().width() + self.frameWidth()
            height = self.frameWidth()
            for row in xrange(self._frozenCount):
                height += self.rowHeight(row)
        else:
            x = self.verticalHeader().width()
            y = 0
            height = self.viewport().height() + self.horizontalHeader().height() + self.frameWidth()
            width = self.frameWidth()
            for column in xrange(self._frozenCount):
                width += self.columnWidth(column)

        self._frozenView.setGeometry(x, y, width, height)

    # -- below --- span logic ---
    @QtCore.pyqtSlot()
    def updateRowSpan(self):
        spanInfo = self.model().rowSpanInfo()
        self.clearSpans()
        for spanRow, spanCount in spanInfo:
            self.setSpan(spanRow, 0, spanCount, 1)

    @QtCore.pyqtSlot()
    def updateColumnSpan(self):
        spanInfo = self.model().columnSpanInfo()
        self.clearSpans()
        for spanColumn, spanCount in spanInfo:
            self.setSpan(0, spanColumn, 1, spanCount)

    @QtCore.pyqtSlot()
    def updateSpan(self):
        if not hasattr(self.model(), 'spanInfo'):
            return
        spanInfo = self.model().spanInfo()
        self.clearSpans()
        for spanRow, spanColumn, spanRowCount, spanColumnCount in spanInfo:
            self.setSpan(spanRow, spanColumn, spanRowCount, spanColumnCount)

    def setModel(self, model):
        QtGui.QTableView.setModel(self, model)
        if model:
            if hasattr(model, 'spanInfo'):
                model.modelReset.connect(self.updateSpan)
            if hasattr(model, 'rowSpanInfo'):
                model.modelReset.connect(self.updateRowSpan)
            if hasattr(model, 'columnSpanInfo'):
                model.modelReset.connect(self.updateColumnSpan)


def main():
    import sys
    app = QtGui.QApplication(sys.argv)

    model = QtGui.QStandardItemModel(100, 100)
    for column in xrange(model.columnCount()):
        for row in xrange(model.rowCount()):
            model.setData(model.index(row, column),
                          u'column %s; row %s' % (column, row))

    view = CExtendedTableView()
    view.setModel(model)
    view.initFreeze(color=QtGui.QColor('green'))
    view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)
    view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)

    view2 = CExtendedTableView()
    view2.setModel(model)
    view2.initFreeze(orientation=QtCore.Qt.Vertical, color=QtGui.QColor('cyan'))

    w = QtGui.QWidget()
    layout = QtGui.QHBoxLayout()
    layout.addWidget(view)
    layout.addWidget(view2)
    w.setLayout(layout)
    w.show()

    return app.exec_()


if __name__ == '__main__':
    main()
