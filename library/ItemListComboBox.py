# -*- coding: utf-8 -*-
from PyQt4 import QtGui

from library.ItemListModel import CItemListModel
from library.ItemListView import CItemListView


class CItemListComboBox(QtGui.QComboBox, object):
    itemType = object
    modelColumn = None
    cols = []

    def __init__(self, parent):
        super(CItemListComboBox, self).__init__(parent)
        self._itemType = None
        self._addNone = None
        self._filter = None
        self._order = None
        self._colWidths = None
        self._lineEdit = None
        view = CItemListView(self)
        view.setAlternatingRowColors(False)
        self.setView(view)
        self.setModel(CItemListModel(self))

    def getCols(self):
        return self.cols

    def setColumnsWidth(self, columnsWidth):
        self._colWidths = columnsWidth

    def getColumnsWidth(self):
        return self._colWidths

    def setReadOnly(self, readOnly):
        if readOnly:
            self._lineEdit = QtGui.QLineEdit(self)
            self._lineEdit.setReadOnly(readOnly)
            self.setView(None)
        else:
            self._lineEdit = None
        self.setLineEdit(self._lineEdit)

    def item(self):
        return self.model().getItem(self.currentIndex())

    def itemId(self):
        item = self.item()
        return item.id if item else None

    def setModel(self, model):
        super(CItemListComboBox, self).setModel(model)
        for colIdx, col in enumerate(model.cols()):
            self.view().setColumnHidden(colIdx, not col.isVisible())

    def setItems(self, items, cols=None, addNone=False):
        model = CItemListModel(None, cols or self.getCols())
        model.setItems(items, addNone=addNone)
        self.setModel(model)
        if self.modelColumn is not None:
            self.setModelColumn(self.modelColumn)

    def showPopup(self):
        rowCount = self.model().rowCount()
        if rowCount > 0:
            view = self.view()  # type: CItemListView
            frame = view.parent()
            comboRect = self.rect()
            below = self.mapToGlobal(comboRect.bottomLeft())
            above = self.mapToGlobal(comboRect.topLeft())
            screen = QtGui.qApp.desktop().availableGeometry(below)

            visibleItems = min(self.maxVisibleItems(), rowCount)
            if visibleItems > 0:
                headerHeight = view.horizontalHeader().height()
                view.setFixedHeight(view.rowHeight(0) * visibleItems + headerHeight)

            if self._colWidths:
                view.setColumnsWidth(self._colWidths)
            else:
                view.resizeRowsToContents()

            sizeHint = view.sizeHint()
            prefferedWidth = max(sizeHint.width(), self.width())
            frame.resize(prefferedWidth, view.height())
            view.resize(prefferedWidth, view.height())

            if screen.bottom() - below.y() >= view.height():
                popupTop = below.y()
            elif above.y() - screen.y() >= view.height():
                popupTop = above.y() - view.height() - 2 * frame.frameWidth()
            else:
                popupTop = max(screen.top(), screen.bottom() - view.height() - frame.frameWidth())
            if screen.right() - below.x() >= view.width():
                popupLeft = below.x()
            else:
                popupLeft = max(screen.left(), screen.right() - view.width() - frame.frameWidth())
            frame.move(popupLeft, popupTop)

            frame.show()
            view.setFocus()
            view.horizontalScrollBar().setValue(0)

    def hidePopup(self):
        self._colWidths = self.view().getColumnsWidth()
        super(CItemListComboBox, self).hidePopup()

    def setValue(self, itemId):
        rowIndex = self.model().searchId(itemId)
        self.setCurrentIndex(rowIndex if rowIndex > -1 else 0)