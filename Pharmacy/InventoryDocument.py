# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui

from Pharmacy.ItemListModel import CReferenceAttribCol
from Pharmacy.Service import CPharmacyService, CPharmacyServiceException, UserPermission
from Pharmacy.StoreItem import CAmountCol, CExpirationClassCol, CExpiryDateCol
from Pharmacy.Types import InventoryDocument, InventoryItem, MeasurementUnit, Store
from Pharmacy.ui.Ui_InventoryDocumentDialog import Ui_InventoryDocumentDialog
from library.DialogBase import CDialogBase
from library.Enum import CEnum
from library.ItemListModel import CEnumAttribCol, CItemAttribCol, CItemListModel, CItemListSortFilterProxyModel
from library.ItemListView import CLocItemProxyDelegate
from library.Utils import forceStringEx


class InventoryStatus(CEnum):
    u""" InventoryDocument.finalized """
    InWork = False
    Finished = True

    nameMap = {
        InWork  : u'В работе',
        Finished: u'Проведено'
    }


class CInventoryDocumentsModel(CItemListModel):
    u""" Документы: инвентаризация """

    def __init__(self, parent):
        super(CInventoryDocumentsModel, self).__init__(parent, cols=[
            CItemAttribCol(u'Порядковый номер', 'id'),
            CItemAttribCol(u'Номер', 'number'),
            CItemAttribCol(u'Дата проведения', 'date'),
            CReferenceAttribCol(u'Склад', 'store', Store, 'name'),
            CEnumAttribCol(u'Статус', 'finalized', InventoryStatus)
        ])


class CInventoryItemsModel(CItemListModel):
    u""" Пункты инвентаризации """

    def __init__(self, parent):
        super(CInventoryItemsModel, self).__init__(parent, itemType=InventoryItem)
        self.amountCol = CAmountCol(u'Остаток', 'stockAmount')
        self.setCols([
            CItemAttribCol(u'Торговое наименование', 'tradeName'),
            CItemAttribCol(u'Действующие вещества (МНН)', 'INN'),
            CItemAttribCol(u'АТХ', 'ATC'),
            CItemAttribCol(u'Производитель', 'manufacturer'),
            CExpiryDateCol(u'Срок годности', 'expiryDate'),
            CReferenceAttribCol(u'Единица учета', 'unit', MeasurementUnit, 'name'),
            self.amountCol,
            CExpirationClassCol(u'Класс товара'),
        ])


class CInventoryDocumentDialog(CDialogBase, Ui_InventoryDocumentDialog):
    u""" Окно инвентаризации """

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self._doc = InventoryDocument()
        self._srv = CPharmacyService.getInstance()
        self._editable = False
        self.addModels('Items', CInventoryItemsModel(self))
        self._proxyModel = CItemListSortFilterProxyModel(self)
        self._proxyModel.setSourceModel(self.modelItems)

        self.setupUi(self)
        self.setWindowTitle(u'Инвентаризация')

        self.edtDatetime.setDateTime(QtCore.QDateTime.currentDateTime())
        self.cmbUser.setItems(self._srv.getFlatUserList())
        self.cmbStore.setItems(self._srv.getStores())
        self.cmbCatalog.setItems(self._srv.getCatalogs(), addNone=True)

        self.cmbStore.currentIndexChanged.connect(self.reloadStoreItems)
        self.cmbCatalog.currentIndexChanged.connect(self.reloadStoreItems)

        self.setModels(self.tblItems, self._proxyModel, self.selectionModelItems)
        self.tblItems.setItemDelegate(CLocItemProxyDelegate(self.tblItems))

        self.edtSearch.textChanged.connect(self.updateFilter)
        self.btnResetSearch.clicked.connect(self.resetFilter)
        self.btnSaveInventory.clicked.connect(self.saveData)
        self.installEventFilter(self)

    def updateFilter(self):
        self._proxyModel.clearFilter()
        self._proxyModel.addColumnPatternFilter(0, self.edtSearch.text())
        self._proxyModel.invalidate()

    def resetFilter(self):
        self.edtSearch.clear()
        self._proxyModel.clearFilter()
        self._proxyModel.invalidate()

    def eventFilter(self, obj, event):
        if obj == self and event.type() == QtCore.QEvent.KeyPress and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
            return True
        return False

    def reloadStoreItems(self):
        storeId = self.cmbStore.itemId()
        catalogId = self.cmbCatalog.itemId()

        if storeId and self._editable:
            self.modelItems.setItems(self.getStoreStockInventoryItems(storeId, catalogId))
        else:
            self.modelItems.clearItems()

        self.resetFilter()

    def getStoreStockInventoryItems(self, storeId, catalogId=None):
        u""" list of StoreStockItem -> list of InventoryItem """
        try:
            items = self._srv.getFlatStoreItems(storeId=storeId, catalogId=catalogId, detailed=True)
        except:
            items = []

        inventoryItems = [InventoryItem(item=stockItem.item,
                                        itemId=stockItem.itemId,
                                        stockAmount=stockItem.amount,
                                        expectedAmount=stockItem.amount)
                          for stockItem in items]
        return sorted(inventoryItems, key=lambda item: item.tradeName)


    def setEditable(self, editable=True):
        self._editable = editable
        self.edtNumber.setReadOnly(not editable)
        self.edtDatetime.setReadOnly(not editable)
        self.cmbUser.setEnabled(editable)
        self.cmbStore.setEnabled(editable)
        self.modelItems.setEditable(editable)

        self.modelItems.setEditable(editable)
        self.modelItems.amountCol.setEditable(editable)
        if editable:
            self.modelItems.setItems(self.getStoreStockInventoryItems(self.cmbStore.itemId()))

        self.btnSaveInventory.setEnabled(editable and self._srv.getCurrentUser().hasPermission(UserPermission.FinalizeInventory))

    def setDocument(self, doc, editable=False):
        u"""
        :type doc: InventoryDocument
        :param editable: редактируемость инвентаризации
        """
        self._doc = doc
        if doc:
            self.edtNumber.setText(doc.number)
            self.edtDatetime.setDateTime(doc.date)
            self.cmbUser.setValue(doc.user)
            self.cmbStore.setValue(doc.store)

            if doc.id:
                try:
                    QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                    items = self._srv.getFlatInventoryItems(doc.id)
                except CPharmacyServiceException:
                    items = []
                finally:
                    QtGui.qApp.restoreOverrideCursor()

                self.modelItems.setItems(items)

        self.setEditable(editable)

    def getDocument(self):
        doc = InventoryDocument()
        doc.number = forceStringEx(self.edtNumber.text())
        doc.date = self.edtDatetime.dateTime()
        doc.store = self.cmbStore.itemId()
        doc.user = self._srv.getCurrentUser().id
        doc.finalizeUser = self.cmbUser.itemId()
        return doc

    def saveDocument(self):
        if self._doc.id is None:
            try:
                doc = self.getDocument()
                createdDoc = self._srv.postItem(doc)  # type: InventoryDocument
            except CPharmacyServiceException as e:
                createdDoc = None
                error = e.errorMessage
            else:
                self._doc = createdDoc
                error = None

            if not createdDoc:
                QtGui.QMessageBox.warning(self, u'Инвентаризация', u'Не удалось сохранить инвентаризацию:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                return False

        for row, inventoryItem in enumerate(self.modelItems.items()):
            if not inventoryItem.saved:
                try:
                    createdItem = self._srv.addInventoryDocumentItem(self._doc.id, inventoryItem)
                except CPharmacyServiceException as e:
                    createdItem = None
                    error = e.errorMessage
                else:
                    createdItem.saved = True
                    self.modelItems.setItem(row, createdItem)
                    error = None

                if not createdItem:
                    QtGui.QMessageBox.warning(self, u'Инвентаризация', u'Не удалось добавить позицию:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                    self.tblItems.selectRow(row)
                    return False

        try:
            result = self._srv.finalizeInventoryDocument(self._doc.id)
        except CPharmacyServiceException as e:
            result = None
            error = e.errorMessage
        else:
            error = None

        if not result:
            QtGui.QMessageBox.warning(self, u'Инвентаризация', u'Не удалось финализировать инвентаризацию:\n{0}'.format(error), QtGui.QMessageBox.Ok)
            return False

        QtGui.QMessageBox.information(self, u'Инвентаризация', u'Успешно сохранено', QtGui.QMessageBox.Ok)

        self.setEditable(False)
        return True

    def saveData(self):
        self.resetFilter()
        return self.saveDocument()
