# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

import Pharmacy.Types as Types
from Pharmacy.ui.Ui_ItemListSearchComboBoxPopup import Ui_ItemListSearchComboBoxPopup
from library.DialogBase import CConstructHelperMixin
from library.ItemListComboBox import CItemListComboBox
from library.ItemListModel import CItemAttribCol, CItemListModel, CItemListSortFilterProxyModel


class CItemListSearchComboBoxPopup(QtGui.QFrame, CConstructHelperMixin, Ui_ItemListSearchComboBoxPopup):
    itemClicked = QtCore.pyqtSignal(int)

    def __init__(self, parent, searchPlaceholder=u''):
        super(CItemListSearchComboBoxPopup, self).__init__(parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)

        self._model = None  # type: CItemListModel
        self._proxyModel = None  # type: CItemListSortFilterProxyModel
        self._selectionModel = None
        self.setupUi(self)

        self.edtName.setPlaceholderText(searchPlaceholder)
        self.edtName.textChanged.connect(self.filterChanged)
        self.edtName.setFocus(QtCore.Qt.OtherFocusReason)

        self.tableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableView.clicked.connect(self.itemSelected)

    def getColumnsWidth(self):
        return self.tableView.getColumnsWidth()

    def setModel(self, model):
        self._model = model
        self._proxyModel = CItemListSortFilterProxyModel(self)
        self._proxyModel.setSourceModel(self._model)
        self._selectionModel = QtGui.QItemSelectionModel(self._proxyModel, self)
        self.setModels(self.tableView, self._proxyModel, self._selectionModel)

    def itemSelected(self, index):
        itemId = self.tableView.itemId(index)
        self.itemClicked.emit(itemId)

    def filterChanged(self):
        self._proxyModel.clearFilter()
        self._proxyModel.addColumnPatternFilter(0, self.edtName.text())
        self._proxyModel.invalidate()

    def setValue(self, itemId):
        self.tableView.setCurrentItemId(itemId)

    def value(self):
        return self.tableView.currentItemId()


class CItemListSearchComboBox(CItemListComboBox):
    searchPopupPlaceholderText = u''

    def __init__(self, parent):
        super(CItemListComboBox, self).__init__(parent)
        self._itemType = None
        self._addNone = None
        self._filter = None
        self._order = None
        self._colWidths = None
        self._model = CItemListModel(self)
        self._popup = CItemListSearchComboBoxPopup(self, self.searchPopupPlaceholderText)
        self.setModel(self._model)

        self._popup.itemClicked.connect(self.setValue)

    def setModel(self, model):
        super(CItemListComboBox, self).setModel(model)
        self._popup.setModel(self.model())

    def showPopup(self):
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))

        self._popup.tableView.resizeColumnsToContents()
        self._popup.tableView.resizeRowsToContents()

        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()

    def hidePopup(self):
        # self._colWidths = self._popup.getColumnsWidth()
        super(CItemListComboBox, self).hidePopup()

    def setValue(self, itemId):
        super(CItemListSearchComboBox, self).setValue(itemId)
        self._popup.setValue(itemId)
        self._popup.hide()


class CCatalogComboBox(CItemListComboBox):
    itemType = Types.Catalog
    cols = [
        CItemAttribCol(u'Наименование', 'name')
    ]


class CCatalogItemComboBox(CItemListComboBox):
    itemType = Types.CatalogItem
    cols = [
        CItemAttribCol(u'Торговое наименование', 'tradeName'),
        CItemAttribCol(u'Дозировка', 'dosage'),
        CItemAttribCol(u'МНН', 'INN')
    ]


class CCatalogItemSearchComboBox(CItemListSearchComboBox):
    itemType = Types.CatalogItem
    searchPopupPlaceholderText = u'Торговое наименование'
    cols = [
        CItemAttribCol(u'Торговое наименование', 'tradeName'),
        CItemAttribCol(u'Дозировка', 'dosage'),
        CItemAttribCol(u'МНН', 'INN')
    ]


class CStoreComboBox(CItemListComboBox):
    itemType = Types.Store
    cols = [
        CItemAttribCol(u'Наименование', 'name')
    ]


class CStoreItemComboBox(CItemListComboBox):
    itemType = Types.StoreItem
    cols = [
        CItemAttribCol(u'Торговое наименование', 'tradeName'),
        CItemAttribCol(u'Дозировка', 'dosage'),
        CItemAttribCol(u'МНН', 'INN'),
        CItemAttribCol(u'АТХ', 'ATC'),
    ]


class CStoreItemSearchComboBox(CItemListSearchComboBox):
    itemType = Types.StoreItem
    searchPopupPlaceholderText = u'Торговое наименование'
    cols = [
        CItemAttribCol(u'Торговое наименование', 'tradeName'),
        CItemAttribCol(u'Дозировка', 'dosage'),
        CItemAttribCol(u'МНН', 'INN'),
        CItemAttribCol(u'АТХ', 'ATC'),
        CItemAttribCol(u'Срок годности', 'expiryDate')
    ]


class CRbItemComboBox(CItemListComboBox):
    itemType = Types.RbItem
    cols = [
        CItemAttribCol(u'Код', 'code', noneName=u'-'),
        CItemAttribCol(u'Наименование', 'name', noneName=u'-'),
        CItemAttribCol(u'-', 'codeName', visible=False)
    ]
    modelColumn = 2


class CUserComboBox(CItemListComboBox):
    itemType = Types.User
    cols = [
        CItemAttribCol(u'ФИО', 'fullName'),
        CItemAttribCol(u'Имя пользователя', 'username')
    ]


class COrganisationComboBox(CItemListComboBox):
    itemType = Types.Organisation
    cols = [
        CItemAttribCol(u'Краткое наименование', 'shortName'),
        CItemAttribCol(u'Тип', 'typeName'),
        CItemAttribCol(u'Наименование', 'fullName')
    ]
