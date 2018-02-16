# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Pharmacy.ItemListComboBox import CCatalogItemComboBox, CCatalogItemSearchComboBox
from Pharmacy.ItemListModel import CRbItemRefAttribCol, CReferenceAttribCol
from Pharmacy.Service import CPharmacyService, CPharmacyServiceException
from Pharmacy.Types import CatalogItem, FundSource, Organisation, ShippingDocument, ShippingDocumentPosition, Store, User
from Pharmacy.ui.Ui_ShippingDocumentDialog import Ui_ShippingDocumentDialog
from library.DialogBase import CDialogBase
from library.ItemListModel import CDateAttribCol, CDecimalAttribCol, CIntAttribCol, CItemAttribCol, CItemListModel, CRowCounterCol, CStringAttribCol
from library.Utils import forceRef, forceStringEx


class CShippingDocumentsModel(CItemListModel):
    u""" Накладные """

    def __init__(self, parent):
        super(CShippingDocumentsModel, self).__init__(parent, cols=[
            CDateAttribCol(u'Дата прихода накладной', 'date'),
            CItemAttribCol(u'Номер внутренней накладной', 'internalNumber'),
            CItemAttribCol(u'Номер внешней накладной', 'externalNumber'),
            CReferenceAttribCol(u'Поставщик', 'supplier', Organisation, 'shortName'),
            CReferenceAttribCol(u'Грузоотправитель', 'shipper', Organisation, 'shortName'),
            CItemAttribCol(u'Основание', 'reason'),
            CRbItemRefAttribCol(u'Источник финансирования', 'fundSource', FundSource),
            CReferenceAttribCol(u'Склад', 'store', Store, 'name'),
            CReferenceAttribCol(u'Сотрудник, принявший товар', 'user', User, 'fullName')
        ], itemType=ShippingDocument)


class CCatalogItemCol(CItemAttribCol):
    u""" Столбец: элемент каталога """

    def __init__(self, title, attribId, attribItem, default=None, **params):
        super(CCatalogItemCol, self).__init__(title, None, default, **params)
        self._storeId = None
        self._attribId = attribId
        self._attribItem = attribItem
        self._order = params.get('order')
        self._colWidths = None
        self._items = None

    def setStore(self, storeId):
        self._storeId = storeId

    def _getItems(self):
        if self._items is None:
            try:
                items = CPharmacyService.getInstance().getCatalogItems(flat=True)
            except CPharmacyServiceException:
                items = []
            except Exception:
                raise

            if self._order:
                items = sorted(items, key=lambda item: getattr(item, self._order, u'').lower())
            self._items = items
        return self._items

    def createEditor(self, parent, item):
        editor = CCatalogItemComboBox(parent)
        editor.setMaxVisibleItems(20)
        editor.setColumnsWidth(self._colWidths)
        editor.setItems(self._getItems())
        return editor

    def getEditorData(self, editor):
        u"""
        :type editor: CCatalogItemComboBox
        """
        self._colWidths = editor.getColumnsWidth()
        item = editor.item()  # type: CatalogItem
        return QtCore.QVariant(item.id if item else None)

    def setEditorData(self, editor, value, item):
        u"""
        :type editor: CCatalogItemComboBox
        :param value: Item.id
        :param item: CatalogItem instance
        """
        editor.setValue(item.catalogItemId if item else None)

    def setValue(self, item, value):
        itemId = forceRef(value)
        catalogItem = CPharmacyService.getInstance().getItem(CatalogItem, itemId)
        setattr(item, self._attribId, itemId)
        setattr(item, self._attribItem, catalogItem)

    def displayValue(self, item, **params):
        catalogItem = getattr(item, self._attribItem, None)
        return catalogItem.tradeName if catalogItem else u''


class CCatalogItemSearchCol(CCatalogItemCol):
    u""" Столбец: элемент каталога с поиском по наименованию """

    def createEditor(self, parent, item):
        editor = CCatalogItemSearchComboBox(parent)
        editor.setMaxVisibleItems(20)
        editor.setColumnsWidth(self._colWidths)
        editor.setItems(self._getItems())
        return editor


class CShipingDocumentItemsModel(CItemListModel):
    u""" Товары по накладной """

    def __init__(self, parent):
        super(CShipingDocumentItemsModel, self).__init__(parent, itemType=ShippingDocumentPosition)
        self.catalogItemCol = CCatalogItemSearchCol(u'Торговое наименование', 'catalogItemId', 'catalogItem', editable=True, order='tradeName')
        self.setCols([
            CRowCounterCol(u'Порядковый номер'),
            self.catalogItemCol,
            CStringAttribCol(u'Серия товара', 'serial', editable=True),
            CDateAttribCol(u'Дата производства', 'productionDate', editable=True),
            CDateAttribCol(u'Дата поступления', 'arrivalDate', editable=True),
            CDateAttribCol(u'Срок годности', 'expiryDate', editable=True),
            CIntAttribCol(u'Количество', 'amount', editable=True),
            CDecimalAttribCol(u'Цена', 'price', editable=True),
            CDecimalAttribCol(u'Сумма', 'sum'),
        ])
        self._storeId = None

    def setStore(self, storeId):
        self._storeId = storeId
        self.catalogItemCol.setStore(storeId)


class CShippingDocumentDialog(CDialogBase, Ui_ShippingDocumentDialog):
    u""" Окно накладной """

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self._doc = ShippingDocument()
        self._srv = CPharmacyService.getInstance()  # type: CPharmacyService
        self._editable = False
        self.addModels('Items', CShipingDocumentItemsModel(self))

        self.setupUi(self)
        self.setWindowTitle(u'Информация о накладной')

        self.edtDateTime.setDateTime(QtCore.QDateTime.currentDateTime())
        orgs = self._srv.getOrganisations()
        self.cmbShipper.setItems(orgs, addNone=True)  # TODO: фильтр по типу организации?
        self.cmbSupplier.setItems(orgs, addNone=True)
        self.cmbOrganisation.setItems(orgs, addNone=True)
        self.cmbFundSource.setItems(self._srv.getFundSources(), addNone=True)
        self.cmbStore.setItems(self._srv.getStores(), addNone=True)
        self.cmbUser.setItems(self._srv.getFlatUserList(), addNone=True)

        self.setModels(self.tblItems, self.modelItems, self.selectionModelItems)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if (obj == self
            and event.type() == QtCore.QEvent.KeyPress
            and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]):
            return True
        return False

    @QtCore.pyqtSlot(int)
    def on_cmbStore_currentIndexChanged(self, index):
        self.modelItems.setStore(self.cmbStore.itemId())

    def setEditable(self, editable=True):
        self.edtNumber.setReadOnly(True)
        self.edtInternalNumber.setReadOnly(not editable)
        self.edtExternalNumber.setReadOnly(not editable)
        self.edtInvoiceNumber.setReadOnly(not editable)
        self.edtDateTime.setReadOnly(not editable)
        self.cmbUser.setEnabled(editable)
        self.cmbSupplier.setEnabled(editable)
        self.cmbShipper.setEnabled(editable)
        self.edtReason.setReadOnly(not editable)
        self.cmbFundSource.setEnabled(editable)
        self.cmbOrganisation.setEnabled(editable)
        self.cmbStore.setEnabled(editable)

        self.tblItems.model().setEditable(editable)
        self.tblItems.model().setExtendable(editable)

        if editable:
            self.tblItems.addPopupDelRow()
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)
        else:
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)

    def setDocument(self, doc, items=None, editable=True):
        u"""
        :type doc: ShippingDocument
        :type items: list of ShippingDocumentPosition
        :param editable: режим редактирования
        """
        self._doc = doc
        if doc:
            self.edtNumber.setText(unicode(doc.id) if doc.id else u'')
            self.edtInternalNumber.setText(doc.internalNumber)
            self.edtExternalNumber.setText(doc.externalNumber)
            self.edtInvoiceNumber.setText(doc.invoiceNumber)
            self.edtDateTime.setDateTime(doc.date)
            self.cmbUser.setValue(doc.user)
            self.cmbSupplier.setValue(doc.supplier)
            self.cmbShipper.setValue(doc.shipper)
            self.edtReason.setText(doc.reason)
            self.cmbFundSource.setValue(doc.fundSource)
            self.cmbOrganisation.setValue(doc.organisation)
            self.cmbStore.setValue(doc.store)
        if items:
            self.tblItems.model().setItems(items)
        self.setEditable(editable)

    def getDocument(self):
        doc = ShippingDocument()
        doc.internalNumber = forceStringEx(self.edtInternalNumber.text())
        doc.externalNumber = forceStringEx(self.edtExternalNumber.text())
        doc.invoiceNumber = forceStringEx(self.edtInvoiceNumber.text())
        doc.date = self.edtDateTime.dateTime()
        doc.user = self.cmbUser.itemId()
        doc.supplier = self.cmbSupplier.itemId()
        doc.shipper = self.cmbShipper.itemId()
        doc.reason = forceStringEx(self.edtReason.text())
        doc.fundSource = self.cmbFundSource.itemId()
        doc.organisation = self.cmbOrganisation.itemId()
        doc.store = self.cmbStore.itemId()
        return doc

    def saveDocument(self):
        if self._doc.id is None:
            try:
                doc = self.getDocument()
                createdDoc = self._srv.postItem(doc)  # type: ShippingDocument
            except CPharmacyServiceException as e:
                createdDoc = None
                error = e.resp.text
            else:
                self._doc = createdDoc
                error = None

            if not createdDoc:
                QtGui.QMessageBox.warning(self, u'Накладная', u'Не удалось сохранить накладную:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                return False

        for row, position in enumerate(self.tblItems.model().items()):
            if position.id is None:
                try:
                    createdPosition = self._srv.addShippingDocumentPosition(self._doc.id, position)
                except CPharmacyServiceException as e:
                    createdPosition = None
                    error = e.errorMessage
                else:
                    error = None

                if not createdPosition:
                    QtGui.QMessageBox.warning(self, u'Накладная', u'Не удалось добавить позицию:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                    self.tblItems.selectRow(row)
                    return False
                else:
                    self.tblItems.model().setItem(row, createdPosition)

        try:
            result = self._srv.finalizeShippingDocument(self._doc.id)
        except CPharmacyServiceException as e:
            result = None
            error = e.resp.text
        else:
            error = None

        if not result:
            QtGui.QMessageBox.warning(self, u'Накладная', u'Не удалось финализировать накладную:\n{0}'.format(error), QtGui.QMessageBox.Ok)

        QtGui.QMessageBox.information(self, u'Накладная', u'Успешно сохранено', QtGui.QMessageBox.Ok)
        return True

    def saveData(self):
        return self.saveDocument()
