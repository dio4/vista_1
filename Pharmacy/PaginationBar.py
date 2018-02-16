# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Pharmacy.ui.Ui_PaginationBar import Ui_PagnationBar


class CPaginationBar(QtGui.QFrame, Ui_PagnationBar, object):
    pageChanged = QtCore.pyqtSignal(int)
    pageSizeChanged = QtCore.pyqtSignal(int)
    itemsCountFormat = u'записей в таблице: %s'

    def __init__(self, parent, pageSize=100, pageCount=1):
        super(CPaginationBar, self).__init__(parent)
        self.setupUi(self)

        self.__current = 1
        self.__pageCount = pageCount
        self.__pageSize = pageSize
        self.__itemsCount = 0

        self.edtCurrent.setText(unicode(self.__current))
        self.edtCount.setText(unicode(self.__pageCount))
        self.edtPageSize.setValue(self.__pageSize)
        self.lblItemsCount.setText(self.itemsCountFormat % self.__itemsCount)
        self.updateButtonState()
        self.updateEdtSizes()

    def page(self):
        return self.__current

    def pageSize(self):
        return self.__pageSize

    def setPageCount(self, pageCount):
        pageCount = max(pageCount, 1)
        self.__pageCount = pageCount
        self.edtCount.setText(unicode(pageCount))
        if self.__current > pageCount:
            self.setPage(pageCount)
        self.updateButtonState()
        self.updateEdtSizes()

    def setPageSize(self, pageSize):
        if self.__pageSize != pageSize:
            self.__pageSize = pageSize
            self.edtPageSize.setValue(pageSize)
            self.setPage(1)

    def setPage(self, page):
        if self.__current != page:
            self.__current = page
            self.edtCurrent.setText(unicode(page))
            self.pageChanged.emit(page)
            self.updateButtonState()
            self.updateEdtSizes()

    def setItemsCount(self, itemsCount):
        self.__itemsCount = itemsCount
        self.lblItemsCount.setText(self.itemsCountFormat % itemsCount)

    def updateButtonState(self):
        self.btnFirst.setEnabled(self.__current > 1)
        self.btnPrev.setEnabled(self.__current > 1)
        self.btnNext.setEnabled(self.__current < self.__pageCount)
        self.btnLast.setEnabled(self.__current < self.__pageCount)

    def updateEdtSizes(self):
        for widget in (self.edtCurrent, self.edtCount):
            widget.setFixedWidth(widget.minimumSizeHint().width())

    @QtCore.pyqtSlot()
    def on_btnFirst_clicked(self):
        self.setPage(1)

    @QtCore.pyqtSlot()
    def on_btnPrev_clicked(self):
        self.setPage(max(1, self.__current - 1))

    @QtCore.pyqtSlot()
    def on_btnNext_clicked(self):
        self.setPage(min(self.__current + 1, self.__pageCount))

    @QtCore.pyqtSlot()
    def on_btnLast_clicked(self):
        self.setPage(self.__pageCount)

    @QtCore.pyqtSlot(int)
    def on_edtPageSize_valueChanged(self, pageSize):
        self.__pageSize = pageSize
        self.setPage(1)
        self.pageSizeChanged.emit(pageSize)
