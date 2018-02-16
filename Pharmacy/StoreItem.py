# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Pharmacy.ItemListModel import CRbItemRefAttribCol, CReferenceAttribCol
from Pharmacy.Service import CPharmacyService
from Pharmacy.ShippingDocument import CShippingDocumentDialog
from Pharmacy.Types import MeasurementUnit, ShippingDocument, StockItemInfo, StoreStockItem
from Pharmacy.ui.Ui_StoreItemDialog import Ui_StoreItemDialog
from Pharmacy.ui.Ui_StoreItemSelectionDialog import Ui_StoreItemSelectionDialog
from library.DialogBase import CDialogBase
from library.Enum import CEnum
from library.ItemListModel import CDecimalAttribCol, CIntAttribCol, CItemAttribCol, CItemListModel, CItemTableCol


class ExpirationClass(CEnum):
    u""" Класс истечения срока годности """

    MoreThanHalfAYear = 0
    LessThanHalfAYear = 1
    LessThanThreeMonths = 2
    Expired = 3

    nameMap = {
        MoreThanHalfAYear  : u'Более полугода до истечения',
        LessThanHalfAYear  : u'Менее полугода до истечения',
        LessThanThreeMonths: u'Менее трех месяцев до истечения',
        Expired            : u'Срок годности истек'
    }
    colorMap = {
        Expired            : '#4a1517',
        LessThanThreeMonths: '#aa0000',
        LessThanHalfAYear  : '#b57900'
    }

    @classmethod
    def getDateClass(cls, date):
        u"""
        :type date: QtCore.QDate
        """
        if not date or not date.isValid(): return None

        curDate = QtCore.QDate.currentDate()
        if date <= curDate:
            return cls.Expired
        elif curDate.addMonths(6) < date:
            return cls.MoreThanHalfAYear
        elif curDate.addMonths(3) >= date:
            return cls.LessThanThreeMonths
        else:
            return cls.LessThanHalfAYear

    @classmethod
    def getDateClassName(cls, date):
        return cls.getName(cls.getDateClass(date))

    @classmethod
    def getDateColor(cls, date):
        return cls.colorMap.get(cls.getDateClass(date))

    @classmethod
    def getExpiryDays(cls, expClass):
        u"""
            d < 0 : 'осталось более N дней до истечения срока годности',
            d > 0 : 'осталось менее N дней до истечения срока годности'
            d == 0: 'просрочено'
        """
        date = QtCore.QDate.currentDate()
        if expClass == cls.MoreThanHalfAYear:
            return -date.daysTo(date.addMonths(6))
        elif expClass == cls.LessThanHalfAYear:
            return date.daysTo(date.addMonths(6))
        elif expClass == cls.LessThanThreeMonths:
            return date.daysTo(date.addMonths(3))
        return 0


class CAmountCol(CIntAttribCol):
    FewAmountColor = QtGui.QColor('#cc0000')

    def textColor(self, item, **params):
        u"""
        :type item: StoreStockItem
        """
        amount = self.displayValue(item, **params)
        return CAmountCol.FewAmountColor if amount < 30 else None


class CExpirationClassCol(CItemTableCol):
    def displayValue(self, item, **params):
        u"""
        :type item: StoreStockItem
        """
        return ExpirationClass.getDateClassName(item.expiryDate)


class CExpiryDateCol(CItemAttribCol):
    def textColor(self, item, **params):
        u"""
        :type item: StoreStockItem
        """
        dateColor = ExpirationClass.getDateColor(item.expiryDate)
        return QtGui.QColor(dateColor) if dateColor else None


class CStoreItemsModel(CItemListModel):
    u""" Описание остатков на складе  """

    def __init__(self, parent):
        super(CStoreItemsModel, self).__init__(parent, itemType=StoreStockItem)
        self.amountCol = CAmountCol(u'Остаток', 'amount', sortable=True)
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


class CCatalogItemShippingInfoModel(CItemListModel):
    u""" Накладные, по которым товар пришел на склад """

    def __init__(self, parent):
        super(CCatalogItemShippingInfoModel, self).__init__(parent, cols=[
            CItemAttribCol(u'Номер накладной', 'internalNumber'),
            CRbItemRefAttribCol(u'Единица учета', 'unitId', MeasurementUnit),
            CItemAttribCol(u'Остаток', 'amount', alignment='r'),
            CDecimalAttribCol(u'Цена', 'price', alignment='r')
        ])


class CStoreItemDialog(CDialogBase, Ui_StoreItemDialog):
    u""" Информация о товаре на складе """

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self._srv = CPharmacyService.getInstance()

        self.addModels('ShippingInfo', CCatalogItemShippingInfoModel(self))

        self.setupUi(self)
        self.setWindowTitle(u'Информация о товаре')

        self.setModels(self.tblShippingInfo, self.modelShippingInfo, self.selectionModelShippingInfo)
        self.tblShippingInfo.doubleClicked.connect(self.openShippingDocument)
        self._item = None

    def setEditable(self, editable=False):
        self.edtTradeName.setReadOnly(not editable)
        self.edtINN.setReadOnly(not editable)
        if editable:
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        else:
            self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)

    def setItem(self, item, shippingInfoList=None, editable=False):
        u"""
        :type item: StoreStockItem
        :type shippingInfoList: list of StockItemInfo
        :param editable: редактируемость
        """
        self._item = item
        if item:
            self.edtTradeName.setText(item.tradeName)
            self.edtINN.setText(item.INN)
            self.setWindowTitle(u'Информация о товаре: {0}'.format(item.tradeName))
        if shippingInfoList:
            self.tblShippingInfo.model().setItems(shippingInfoList)
            self.tblShippingInfo.resizeColumnsToContents()
        self.setEditable(editable)

    def openShippingDocument(self, index):
        shippingInfo = self.tblShippingInfo.model().getItem(index.row())  # type: StockItemInfo
        shippingDocId = shippingInfo.documentId if shippingInfo else None
        if shippingDocId:
            shippingDoc = self._srv.getItem(ShippingDocument, shippingDocId)
            shippingDocItems = self._srv.getShippingDocumentPositions(shippingDocId)

            dlg = CShippingDocumentDialog(self)
            dlg.setDocument(shippingDoc, items=shippingDocItems, editable=False)
            dlg.exec_()


class CStoreItemSelectionDialog(CDialogBase, Ui_StoreItemSelectionDialog):
    u""" Товары, подобранные по входящему требованию """

    def __init__(self, parent):
        super(CStoreItemSelectionDialog, self).__init__(parent)

        self.addModels('Items', CStoreItemsModel(self))
        self.modelItems.insertCol(1, CItemAttribCol(u'Дозировка', 'dosage'))

        self.setupUi(self)
        self.setWindowTitle(u'Подходящие товары')

        self.setModels(self.tblItems, self.modelItems, self.selectionModelItems)
        self.tblItems.doubleClicked.connect(self.setSelectedItem)

        self._selectedStoreItem = None  # type: StoreStockItem

    def setSelectedItem(self):
        self._selectedStoreItem = self.tblItems.currentItem()
        self.close()

    def getSelectedItem(self):
        return self._selectedStoreItem

    def setItems(self, items):
        u"""
        :type items: list of StoreStockItem
        """
        self.tblItems.model().setItems(items)
