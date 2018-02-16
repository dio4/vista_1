# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Pharmacy.ItemListModel import CReferenceAttribCol
from Pharmacy.RequestDocument import RequestDocumentType
from Pharmacy.Service import CPharmacyService, CPharmacyServiceException, UserPermission
from Pharmacy.StoreItem import CStoreItemSelectionDialog
from Pharmacy.Types import M11Document, M11DocumentPosition, MeasurementUnit, RequestDocument
from library.DialogBase import CDialogBase
from library.ItemListModel import CIntAttribCol, CItemAttribCol, CItemListModel, CRowCounterCol
from ui.Ui_M11DocumentDialog import Ui_M11DocumentDialog


class CRequestDocumentItems(CItemListModel):
    u""" Запрашиваемые товары: позиции требования """

    def __init__(self, parent):
        super(CRequestDocumentItems, self).__init__(parent, cols=[
            CRowCounterCol(u'Порядковый номер'),
            CItemAttribCol(u'Запрашиваемый МНН', 'INN'),
            CItemAttribCol(u'Запрашиваемое торговое наименование', 'tradeName'),
            CItemAttribCol(u'Дозировка', 'dosage'),
            CReferenceAttribCol(u'Единица измерения', 'unit', MeasurementUnit, 'name'),
            CItemAttribCol(u'Запрашиваемое количество', 'amount')
        ], itemType=M11DocumentPosition)


class CTrasferAmountCol(CIntAttribCol):
    u""" Отпускаемое кол-во товара """

    def getMaximum(self, item):
        u"""
        :type item: M11DocumentPosition
        """
        return item.maxAmount


class CM11DocumentItems(CItemListModel):
    u""" Отпускаемые товары: позиции М11 """

    def __init__(self, parent):
        super(CM11DocumentItems, self).__init__(parent, cols=[
            CRowCounterCol(u'Порядковый номер'),
            CItemAttribCol(u'МНН', 'INN'),
            CItemAttribCol(u'Торговое наименование', 'tradeName'),
            CItemAttribCol(u'Дозировка', 'dosage'),
            CReferenceAttribCol(u'Единица измерения', 'unit', MeasurementUnit, 'name'),
            CTrasferAmountCol(u'Количество', 'amount', editable=True),
            CItemAttribCol(u'Срок годности', 'expiryDate')
        ], itemType=M11DocumentPosition)


class CM11DocumentDialog(CDialogBase, Ui_M11DocumentDialog):
    u""" Окно отработки требования """

    def __init__(self, parent):
        super(CM11DocumentDialog, self).__init__(parent)
        self.addModels('RequestDocumentItems', CRequestDocumentItems(self))
        self.addModels('M11DocumentItems', CM11DocumentItems(self))

        self.setupUi(self)
        self.setWindowTitle(u'Отработка требования')

        self.setModels(self.tblRequestDocumentItems, self.modelRequestDocumentItems, self.selectionModelRequestDocumentItems)
        self.setModels(self.tblM11DocumentItems, self.modelM11DocumentItems, self.selectionModelM11DocumentItems)

        self._editable = False
        self._doc = M11Document()
        self._requestDoc = RequestDocument()
        self._srv = CPharmacyService.getInstance()

        self.edtDatetime.setDate(QtCore.QDate.currentDate())
        self.cmbStoreFrom.setItems(self._srv.getStores())
        self.cmbUser.setItems(self._srv.getFlatUserList())

        self.btnSelectItems.clicked.connect(self.selectStoreItems)
        self.btnFinalize.clicked.connect(self.saveDocument)

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelRequestDocumentItems_selectionChanged(self, current, previous):
        selected = self.tblRequestDocumentItems.getSelectedRows()
        self.btnSelectItems.setEnabled(self._editable and len(selected) > 0)

    def selectStoreItems(self):
        storeId = self._requestDoc.storeFrom
        documentPosition = self.tblRequestDocumentItems.currentItem()  # type: M11DocumentPosition

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            storeStockItems = self._srv.getFlatStoreItems(storeId=storeId,
                                                          detailed=True,
                                                          name=documentPosition.catalogItemName)
        except CPharmacyServiceException:
            storeStockItems = []
        finally:
            QtGui.qApp.restoreOverrideCursor()

        dlg = CStoreItemSelectionDialog(self)
        dlg.setItems(storeStockItems)
        dlg.exec_()

        storeStockItem = dlg.getSelectedItem()
        if storeStockItem:
            m11Position = M11DocumentPosition(
                amount=min(storeStockItem.amount,
                           documentPosition.amount),
                itemId=storeStockItem.itemId,
                catalogItem=storeStockItem.item.catalogItem,
                catalogItemId=storeStockItem.catalogItemId
            )
            self.tblM11DocumentItems.model().addItem(m11Position)

    def setEditable(self, editable):
        self._editable = editable
        self.edtDatetime.setReadOnly(True)
        self.edtNumber.setReadOnly(True)
        self.cmbStoreFrom.setEnabled(False)
        self.cmbUser.setEnabled(False)
        self.edtHistoryNumber.setReadOnly(True)
        self.tblM11DocumentItems.model().setEditable(editable)
        self.btnFinalize.setEnabled(editable and
                                    not self._requestDoc.transferFinished and
                                    self._requestDoc.type != RequestDocumentType.order and
                                    self._srv.getCurrentUser().hasPermission(UserPermission.FinalizeRequest))

    def setRequestDocument(self, doc, editable=False):
        u"""
        :type doc: RequestDocument
        :param editable:
        """
        self._requestDoc = doc
        if doc:
            self.edtDatetime.setDateTime(doc.date)
            self.edtDocumentId.setText(unicode(doc.id) if doc.id else u'')
            self.edtNumber.setText(doc.number)
            self.cmbStoreFrom.setValue(doc.storeTo)
            self.cmbUser.setValue(doc.user)
            self.edtHistoryNumber.setText(doc.historyNumber)

            if doc.id:
                docIitems = self._srv.getFlatRequestDocumentPositions(doc.id)
                self.tblRequestDocumentItems.model().setItems(docIitems)

            if doc.transferFinished:
                m11Positions = []
                for m11DocumentId in doc.m11List:
                    m11Positions.extend(self._srv.getFlatM11DocumentPositions(m11DocumentId))
                self.tblM11DocumentItems.model().setItems(m11Positions)

        self.setEditable(editable)

    def getDocument(self):
        doc = M11Document()
        doc.requestId = self._requestDoc.id
        doc.storeTo = self._requestDoc.storeTo
        doc.storeFrom = self._requestDoc.storeFrom
        doc.number = self._requestDoc.number
        doc.date = QtCore.QDateTime.currentDateTime()
        return doc

    def saveDocument(self):
        if self._doc.id is None:
            try:
                doc = self.getDocument()
                createdDoc = self._srv.postItem(doc)  # type: M11Document
            except CPharmacyServiceException as e:
                createdDoc = None
                error = e.errorMessage
            else:
                self._doc = createdDoc
                error = None

            if not createdDoc:
                QtGui.QMessageBox.warning(self, u'М-11', u'Не удалось сохранить:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                return False

        for row, position in enumerate(self.tblM11DocumentItems.model().items()):
            if position.id is None:
                try:
                    createdPosition = self._srv.addM11DocumentPosition(self._doc.id, position.lite())
                except CPharmacyServiceException as e:
                    error = e.errorMessage
                else:
                    self.tblM11DocumentItems.model().setItem(row, createdPosition)
                    error = None

                if error:
                    QtGui.QMessageBox.warning(self, u'М-11', u'Не удалось добавить позицию:\n{0}'.format(error), QtGui.QMessageBox.Ok)
                    self.tblM11DocumentItems.selectRow(row)
                    return False

        if not self._doc.finalized:
            try:
                result = (self._srv.finalizeM11Document(self._doc.id) and
                          self._srv.finishTransferRequestDocument(self._requestDoc.id))
            except CPharmacyServiceException as e:
                result = False
                error = e.errorMessage
            else:
                error = None

            if not result:
                QtGui.QMessageBox.warning(self, u'М-11', u'Не удалось отработать требование:\n{0}'.format(error), QtGui.QMessageBox.Ok)

        QtGui.QMessageBox.information(self, u'М-11', u'Требование успешно отработано', QtGui.QMessageBox.Ok)

        self.setEditable(False)
        return True

    def saveData(self):
        return self.saveDocument()
