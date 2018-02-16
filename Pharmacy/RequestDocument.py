# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Pharmacy.ItemListComboBox import CStoreItemComboBox, CStoreItemSearchComboBox
from Pharmacy.ItemListModel import CReferenceAttribCol
from Pharmacy.Service import CPharmacyService, CPharmacyServiceException, UserPermission
from Pharmacy.Types import LiteDocumentPosition, M11Document, RequestDocument, Store, StoreItem
from library.DialogBase import CDialogBase
from library.Enum import CEnum
from library.ItemListModel import CEnumAttribCol, CIntAttribCol, CItemAttribCol, CItemListModel, CItemTableCol, CRowCounterCol
from library.Utils import forceRef, forceStringEx, getCounter, getCounterValue, updateCounterValue
from ui.Ui_RequestDocumentDialog import Ui_RequestDocumentDialog


class RequestDocumentType(CEnum):
    u""" RequestDocument.type """
    order = 'order'
    planned = 'planned'
    emergency = 'emergency'

    nameMap = {
        order    : u'Заявка на приобретение',
        planned  : u'Плановое требование',
        emergency: u'Экстренное требование'
    }


class RequestDocumentStatus(CEnum):
    u""" RequestDocument.transferFinished """
    NotFinished = False
    Finished = True

    nameMap = {
        NotFinished: u'Не отработано',
        Finished   : u'Отработано'
    }


class CRequestFinishedDateCol(CItemTableCol):
    u""" Дата отработки требования == дата утверждения М-11 """

    def displayValue(self, item, **params):
        u"""
        :type item: RequestDocument
        :param params: 
        """
        if item.transferFinished:
            for m11DocumentId in item.m11List:
                try:
                    doc = CPharmacyService.getInstance().getItem(M11Document, m11DocumentId)  # type: M11Document
                except CPharmacyServiceException:
                    doc = None
                if doc and doc.finalizeDate:
                    return doc.finalizeDate
        return None


class CIncomingRequestDocumentsModel(CItemListModel):
    u""" Входящие требования """
    NotTransferFinishedColor = QtGui.QColor("#ffcccc")
    OrderTypeColor = QtGui.QColor("#ffbb88")

    def __init__(self, parent):
        super(CIncomingRequestDocumentsModel, self).__init__(parent, cols=[
            CEnumAttribCol(u'Вид требования', 'type', RequestDocumentType),
            CReferenceAttribCol(u'Склад отправителя', 'storeTo', Store, 'name'),
            CReferenceAttribCol(u'Склад получателя', 'storeFrom', Store, 'name'),
            CItemAttribCol(u'Дата формирования запроса', 'date'),
            CRequestFinishedDateCol(u'Дата отработки запроса')
        ])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, column = index.row(), index.column()
        if 0 <= row < self.rowCount() and role == QtCore.Qt.BackgroundColorRole:
            doc = self._items[row]  # type: RequestDocument
            if not doc.transferFinished:
                return QtCore.QVariant(self.NotTransferFinishedColor)
            elif doc.type == RequestDocumentType.order:
                return QtCore.QVariant(self.OrderTypeColor)
        return super(CIncomingRequestDocumentsModel, self).data(index, role)

    def setItems(self, items, itemType=None, addNone=False):
        items = sorted(items, key=lambda item: item.transferFinished)  # неотработанные - сверху
        super(CIncomingRequestDocumentsModel, self).setItems(items)


class COutcomingRequestDocumentsModel(CItemListModel):
    u""" Исходящие требования """
    NotFinalizedColor = QtGui.QColor("#ffcccc")

    def __init__(self, parent):
        super(COutcomingRequestDocumentsModel, self).__init__(parent, cols=[
            CEnumAttribCol(u'Вид требования', 'type', RequestDocumentType),
            CReferenceAttribCol(u'Склад отправителя', 'storeTo', Store, 'name'),
            CReferenceAttribCol(u'Склад получателя', 'storeFrom', Store, 'name'),
            CItemAttribCol(u'Дата формирования запроса', 'date'),
            CItemAttribCol(u'Дата отработки запроса', 'finalizeDate')
        ])

    def setItems(self, items, itemType=None, addNone=False):
        items = sorted(items, key=lambda item: item.finalized)  # неутверждённые - сверху
        super(COutcomingRequestDocumentsModel, self).setItems(items)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, column = index.row(), index.column()
        if 0 <= row < self.rowCount() and role == QtCore.Qt.BackgroundColorRole:
            doc = self._items[row]  # type: RequestDocument
            if not doc.finalized:
                return QtCore.QVariant(self.NotFinalizedColor)
        return super(COutcomingRequestDocumentsModel, self).data(index, role)


class CStoreItemCol(CItemAttribCol):
    u""" Столбец: ссылка на StoreItem (с возможностью фильтрации по складу) """

    def __init__(self, title, attribName, default=None, **params):
        super(CStoreItemCol, self).__init__(title, attribName, default, **params)
        self._order = params.get('order')
        self._storeId = None
        self._items = None

    def _getItems(self):
        if self._items is None:
            try:
                if self._storeId:
                    items = CPharmacyService.getInstance().getFlatStoreItems(storeId=self._storeId, detailed=True)
                    items = [item.item for item in items]
                else:
                    items = CPharmacyService.getInstance().getStoreItems()
            except CPharmacyServiceException:
                items = []
            if self._order:
                items = sorted(items, key=lambda item: getattr(item, self._order, u'').lower())
            self._items = items
        return self._items

    def setStore(self, storeId):
        self._storeId = storeId

    def createEditor(self, parent, item):
        editor = CStoreItemComboBox(parent)
        editor.setItems(self._getItems())
        return editor

    def getEditorData(self, editor):
        u"""
        :type editor: CStoreItemComboBox
        """
        return QtCore.QVariant(editor.itemId())

    def setEditorData(self, editor, value, item):
        u"""
        :type editor: CStoreItemComboBox
        :param value: StoreItem.id
        :type item: LiteDocumentPosition
        """
        editor.setValue(item.itemId if item else None)

    def setValue(self, item, value):
        super(CStoreItemCol, self).setValue(item, forceRef(value))

    def displayValue(self, item, **params):
        itemId = super(CStoreItemCol, self).displayValue(item, **params)
        storeItem = CPharmacyService.getInstance().getItem(StoreItem, itemId)
        return storeItem.tradeName


class CStoreItemSearchCol(CStoreItemCol):
    u""" Товар на складе (с поиском по названию) """

    def createEditor(self, parent, item):
        editor = CStoreItemSearchComboBox(parent)
        editor.setItems(self._getItems())
        return editor


class CStoreItemAmountCol(CItemAttribCol):
    u""" Остатки на складе """

    def __init__(self, title, attribName, default=None, **params):
        super(CStoreItemAmountCol, self).__init__(title, attribName, default, **params)
        self._parent = params.get('parent')

    def displayValue(self, item, **params):
        if self._parent:
            amount = self._parent.getItemAmount(item.itemId)
            if amount is not None:
                return amount
        return '-'


class CRequestedAmountCol(CIntAttribCol):
    u""" Запрашиваемое количество """

    def __init__(self, title, attribName, default=None, **params):
        super(CRequestedAmountCol, self).__init__(title, attribName, default, **params)
        self._parent = params.get('parent')

    def getMaximum(self, item):
        u"""
        :type item: LiteDocumentPosition
        """
        if self._parent and item is not None:
            maxValue = self._parent.getItemAmount(item.itemId)
            if maxValue is not None:
                return maxValue
        return super(CRequestedAmountCol, self).getMaximum(item)


class CRequestDocumentItemsModel(CItemListModel):
    u""" Создание требования: запрашиваемые товары """

    def __init__(self, parent):
        super(CRequestDocumentItemsModel, self).__init__(parent, itemType=LiteDocumentPosition)
        self._storeItemCol = CStoreItemSearchCol(u'Элемент каталога', 'itemId', order='tradeName', editable=True)
        self._storeAmountCol = CStoreItemAmountCol(u'Остаток на складе', 'itemId', parent=self)
        self._storeId = None
        self._storeItemAmountMap = {}
        self.setCols([
            CRowCounterCol(u'Порядковый номер'),
            self._storeItemCol,
            self._storeAmountCol,
            CRequestedAmountCol(u'Количество', 'amount', editable=True, parent=self)
        ])

    def getItemAmount(self, itemId):
        return self._storeItemAmountMap.get(itemId)

    def setStore(self, storeId):
        self._storeId = storeId
        self._storeItemAmountMap = CPharmacyService.getInstance().getStoreItemAmountMap(storeId)
        self._storeItemCol.setStore(storeId)


class CRequestDocumentDialog(CDialogBase, Ui_RequestDocumentDialog):
    u""" Диалог создания требования/заявки """
    NumberCounterCode = 'pharm_RD'

    def __init__(self, parent):
        super(CRequestDocumentDialog, self).__init__(parent)

        self.addModels('Items', CRequestDocumentItemsModel(self))

        self.setupUi(self)
        self.setWindowTitle(u'Требование')

        self.setModels(self.tblItems, self.modelItems, self.selectionModelItems)

        self._doc = RequestDocument()
        self._srv = CPharmacyService.getInstance()
        self._finalizeEnabled = self._srv.getCurrentUser().hasPermission(UserPermission.FinalizeRequest)
        self._numberCounter = getCounter(self.NumberCounterCode)

        self.edtNumber.setText(unicode(getCounterValue(counterId=self._numberCounter) or u''))
        self.cmbType.setEnum(RequestDocumentType)
        self.edtDatetime.setDateTime(QtCore.QDateTime.currentDateTime())
        self.cmbUser.setItems(self._srv.getFlatUserList())
        self.cmbStoreFrom.setItems(self._srv.getStores())
        self.cmbStoreTo.setItems(self._srv.getStores())

        self.btnFinalize.clicked.connect(self.saveDocument)

    @QtCore.pyqtSlot(int)
    def on_cmbType_currentIndexChanged(self, index):
        docType = self.cmbType.value()
        if docType == RequestDocumentType.emergency:
            self.edtHistoryNumber.setEnabled(True)
        else:
            self.edtHistoryNumber.clear()
            self.edtHistoryNumber.setEnabled(False)

        if docType != RequestDocumentType.order:
            self.tblItems.model().setStore(self.cmbStoreTo.itemId())
        else:
            self.tblItems.model().setStore(None)

    @QtCore.pyqtSlot(int)
    def on_cmbStoreTo_currentIndexChanged(self, index):
        docType = self.cmbType.value()
        if docType != RequestDocumentType.order:
            self.tblItems.model().setStore(self.cmbStoreTo.itemId())
        else:
            self.tblItems.model().setStore(None)

    def setEditable(self, editable=True):
        self.cmbType.setEnabled(editable)
        self.edtDatetime.setReadOnly(not editable)
        self.edtNumber.setReadOnly(not editable)
        self.cmbStoreFrom.setEnabled(editable)
        self.cmbStoreTo.setEnabled(editable)
        self.cmbUser.setEnabled(editable)
        self.edtHistoryNumber.setReadOnly(not editable)

        self.tblItems.model().setEditable(editable)
        self.tblItems.model().setExtendable(editable)
        if editable:
            self.tblItems.addPopupDelRow()
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Cancel)
        else:
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)

        self.btnFinalize.setEnabled(editable and self._finalizeEnabled)

    def setDocument(self, doc, editable=True):
        u"""
        :type doc: RequestDocument
        """
        self._doc = doc
        if doc:
            self.edtDocumentId.setText(unicode(doc.id) if doc.id else u'')
            self.cmbType.setValue(doc.type)
            self.edtDatetime.setDateTime(doc.date)
            self.edtNumber.setText(doc.number)
            self.cmbStoreTo.setValue(doc.storeFrom)
            self.cmbStoreFrom.setValue(doc.storeTo)
            self.cmbUser.setValue(doc.user)
            self.edtHistoryNumber.setText(doc.historyNumber)

            if doc.id:
                try:
                    QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                    docPositions = self._srv.getFlatRequestDocumentPositions(doc.id)
                except CPharmacyServiceException:
                    docPositions = []
                finally:
                    QtGui.qApp.restoreOverrideCursor()

                self.tblItems.model().setItems(docPositions)

        self.setEditable(editable)

    def getDocument(self):
        doc = RequestDocument()
        doc.type = self.cmbType.value()
        doc.number = forceStringEx(self.edtNumber.text())
        doc.date = self.edtDatetime.dateTime()
        doc.storeTo = self.cmbStoreFrom.itemId()
        doc.storeFrom = self.cmbStoreTo.itemId()
        doc.user = self.cmbUser.itemId()
        doc.historyNumber = forceStringEx(self.edtHistoryNumber.text())
        return doc

    def saveDocument(self):
        if self._doc.id is None:
            try:
                doc = self.getDocument()
                createdDoc = self._srv.postItem(doc)  # type: RequestDocument
                updateCounterValue(self._numberCounter)
            except CPharmacyServiceException as e:
                createdDoc = None
                error = e.errorMessage
            else:
                self._doc = createdDoc
                error = None

            if not createdDoc:
                QtGui.QMessageBox.warning(self, u'Требование', u'Не удалось сохранить:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                return False

        for row, position in enumerate(self.tblItems.model().items()):
            if not position.saved:
                try:
                    createdPosition = self._srv.addRequestDocumentPosition(self._doc.id, position)
                except CPharmacyServiceException as e:
                    error = e.errorMessage
                else:
                    error = None
                    litePosition = createdPosition.lite()
                    litePosition.saved = True
                    self.tblItems.model().setItem(row, litePosition)

                if error:
                    QtGui.QMessageBox.warning(self, u'Требование', u'Не удалось добавить позицию:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                    self.tblItems.selectRow(row)
                    return False

        if not self._doc.finalized and self._finalizeEnabled:
            try:
                result = self._srv.finalizeRequestDocument(self._doc.id)
            except CPharmacyServiceException as e:
                result = False
                error = e.resp.text
            else:
                error = None

            if not result:
                QtGui.QMessageBox.warning(self, u'Требование', u'Не удалось утвердить требование:\n{0}'.format(error), QtGui.QMessageBox.Ok)

        QtGui.QMessageBox.information(self, u'Требование', u'Успешно сохранено', QtGui.QMessageBox.Ok)

        self.setEditable(False)
        return True

    def saveData(self):
        return self.saveDocument()
