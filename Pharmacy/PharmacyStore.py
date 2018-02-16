# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Pharmacy.InventoryDocument import CInventoryDocumentDialog, CInventoryDocumentsModel
from Pharmacy.M11Document import CM11DocumentDialog
from Pharmacy.PreferencesDialog import CPreferencesDialog
from Pharmacy.PrintInfo import CCatalogItemInfo, CRequestDocumentInfo, CStoreStockItemInfo
from Pharmacy.RequestDocument import CIncomingRequestDocumentsModel, COutcomingRequestDocumentsModel, CRequestDocumentDialog, RequestDocumentStatus, \
    RequestDocumentType
from Pharmacy.Service import CPharmacyService, CPharmacyServiceException, UserPermission
from Pharmacy.ShippingDocument import CShippingDocumentDialog, CShippingDocumentsModel
from Pharmacy.StoreItem import CStoreItemDialog, CStoreItemsModel, ExpirationClass
from Pharmacy.StoreStockReport import CStoreStockReport
from Pharmacy.Types import RequestDocument, ShippingDocument
from Pharmacy.ui.Ui_PharmacyStoreDialog import Ui_PharmacyStoreDialog
from library.DialogBase import CDialogBase
from library.PrintTemplates import CInfoContext, applyTemplate, customizePrintButton, getFirstPrintTemplate
from library.Utils import forceStringEx, getPref, setPref, toVariant, withWaitCursor


class CPharmacyStoreDialog(CDialogBase, Ui_PharmacyStoreDialog):
    u""" Основное окно сервиса Склад-Аптека """

    def __init__(self, parent):
        super(CPharmacyStoreDialog, self).__init__(parent)

        self.addModels('StoreItems', CStoreItemsModel(self))
        self.addModels('ShippingDocuments', CShippingDocumentsModel(self))
        self.addModels('IncomeRequestDocuments', CIncomingRequestDocumentsModel(self))
        self.addModels('OutcomeRequestDocuments', COutcomingRequestDocumentsModel(self))
        self.addModels('InventoryDocuments', CInventoryDocumentsModel(self))

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(u'Склад-Аптека')

        self.menuBar = QtGui.QToolBar(self)
        self.menuBar.setObjectName('menuBar')

        self.btnSession = QtGui.QToolButton(self)
        self.btnSession.setText(u'Сессия')
        self.btnSession.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.actConnect = QtGui.QAction(u'Подключиться', self)
        self.actConnect.setObjectName('actConnect')
        self.actConnect.triggered.connect(self._initService)
        self.actDisconnect = QtGui.QAction(u'Отключиться', self)
        self.actDisconnect.setObjectName('actDisconnect')
        self.actDisconnect.triggered.connect(self._deinitService)
        self.actDisconnect.setVisible(False)
        self.actClose = QtGui.QAction(u'Закрыть', self)
        self.actClose.setObjectName('actClose')
        self.actClose.triggered.connect(self.close)
        self.mnuSession = QtGui.QMenu(self.btnSession)
        self.mnuSession.setObjectName('mnuSession')
        self.mnuSession.addAction(self.actConnect)
        self.mnuSession.addAction(self.actDisconnect)
        self.mnuSession.addAction(self.actClose)
        self.btnSession.setMenu(self.mnuSession)
        self.menuBar.addWidget(self.btnSession)

        self.actAnalyse = QtGui.QAction(u'Анализ', self)
        self.actAnalyse.setObjectName('actAnalyse')
        self.menuBar.addAction(self.actAnalyse)

        self.actSettings = QtGui.QAction(u'Настройки', self)
        self.actSettings.setObjectName('actSettings')
        self.actSettings.triggered.connect(self.onSettings)
        self.menuBar.addAction(self.actSettings)

        self.layout().setMenuBar(self.menuBar)

        # self.tabWidget.setStyleSheet("QTabBar::tab { height: 30px; width: 20em; }")

        # tabStoreItem
        self.cmbStoreItemsExpirationClass.setEnum(ExpirationClass, addNone=True)
        self.cmbStoreItemsStore.currentIndexChanged.connect(self.resetStoreItemsPage)
        self.cmbStoreItemsStore.currentIndexChanged.connect(self.reloadStoreItems)
        self.cmbStoreItemsCatalog.currentIndexChanged.connect(self.resetStoreItemsPage)
        self.cmbStoreItemsCatalog.currentIndexChanged.connect(self.reloadStoreItems)
        self.cmbStoreItemsExpirationClass.currentIndexChanged.connect(self.reloadStoreItems)
        self.chkStoreItemsDetailed.toggled.connect(self.resetStoreItemsPage)
        self.chkStoreItemsDetailed.toggled.connect(self.reloadStoreItems)
        self.chkStoreItemsArrivalDate.toggled.connect(self.reloadStoreItems)
        self.edtStoreItemsArrivalDate.dateChanged.connect(self.reloadStoreItems)
        self.btnStoreItemsClear.clicked.connect(self.clearStoreItemsFilter)
        self.btnStoreItemsApply.clicked.connect(self.reloadStoreItems)
        customizePrintButton(self.btnStoreItemsPrint, 'pharmacy.storeItems')
        self.actStoreStockReport = QtGui.QAction(u'Отчет за период', self)
        self.actStoreStockReport.setObjectName('actStoreStockReport')
        self.actStoreStockReport.triggered.connect(self.onStoreStockReport)
        self.btnStoreItemsPrint.addAction(self.actStoreStockReport)

        self.setModels(self.tblStoreItems, self.modelStoreItems, self.selectionModelStoreItems)
        self.tblStoreItems.doubleClicked.connect(self.openStoreItem)
        self.tblStoreItems.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.pageBarStoreItems.pageChanged.connect(self.reloadStoreItems)
        self.pageBarStoreItems.pageSizeChanged.connect(self.reloadStoreItems)

        # tabShippingDocument
        self.cmbShippingStore.currentIndexChanged.connect(self.reloadShippingDocuments)
        self.cmbShippingSupplier.currentIndexChanged.connect(self.reloadShippingDocuments)
        self.cmbShippingFinalizeUser.currentIndexChanged.connect(self.reloadShippingDocuments)
        self.edtShippingDocumentDate.dateChanged.connect(self.reloadShippingDocuments)
        self.cmbShippingFundSource.currentIndexChanged.connect(self.reloadShippingDocuments)
        self.btnShippingClear.clicked.connect(self.clearShippingDocumentFilter)
        self.btnShippingApply.clicked.connect(self.reloadShippingDocuments)

        self.setModels(self.tblShippingDocuments, self.modelShippingDocuments, self.selectionModelShippingDocuments)
        self.tblShippingDocuments.doubleClicked.connect(self.openShippingDocument)
        self.tblShippingDocuments.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.pageBarShippingDocuments.pageChanged.connect(self.reloadShippingDocuments)
        self.pageBarShippingDocuments.pageSizeChanged.connect(self.reloadShippingDocuments)

        self.btnNewShippingDocument.clicked.connect(self.createShippingDocument)

        # tabRequestDocument
        self.cmbRequestDocumentStatus.setEnum(RequestDocumentStatus, addNone=True)
        self.cmbRequestDocumentType.setEnum(RequestDocumentType, addNone=True)
        self.cmbRequestDocumentStatus.currentIndexChanged.connect(self.reloadRequestDocuments)
        self.cmbRequestDocumentType.currentIndexChanged.connect(self.reloadRequestDocuments)
        self.cmbRequestDocumentStoreFrom.currentIndexChanged.connect(self.reloadRequestDocuments)
        self.cmbRequestDocumentStoreTo.currentIndexChanged.connect(self.reloadRequestDocuments)
        self.chkRequestDocumentDate.toggled.connect(self.reloadRequestDocuments)
        self.edtRequestDocumentDate.dateChanged.connect(self.reloadRequestDocuments)
        self.btnRequestDocumentClear.clicked.connect(self.clearRequestDocumentFilter)
        self.btnRequestDocumentApply.clicked.connect(self.reloadRequestDocuments)
        customizePrintButton(self.btnRequestDocumentPrint, 'pharmacy.requestDocs')

        self.setModels(self.tblIncomingRequestDocuments, self.modelIncomeRequestDocuments, self.selectionModelIncomeRequestDocuments)
        self.setModels(self.tblOutcomingRequestDocuments, self.modelOutcomeRequestDocuments, self.selectionModelOutcomeRequestDocuments)
        self.tblIncomingRequestDocuments.doubleClicked.connect(self.openIncomingRequestDocument)
        self.tblIncomingRequestDocuments.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblOutcomingRequestDocuments.doubleClicked.connect(self.openOutcomingRequestDocument)
        self.tblOutcomingRequestDocuments.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.pageBarIncomingRequestDocuments.pageChanged.connect(self.reloadRequestDocuments)
        self.pageBarIncomingRequestDocuments.pageSizeChanged.connect(self.reloadRequestDocuments)
        self.pageBarOutcomingRequestDocuments.pageChanged.connect(self.reloadRequestDocuments)
        self.pageBarOutcomingRequestDocuments.pageSizeChanged.connect(self.reloadRequestDocuments)

        self.btnNewRequestDocument.clicked.connect(self.createRequestDocument)

        # tabInventoryDocument
        self.cmbInventoryDocumentStore.currentIndexChanged.connect(self.reloadInventoryDocuments)
        self.btnInventoryClear.clicked.connect(self.clearInventoryDocumentFilter)
        self.btnInventoryApply.clicked.connect(self.reloadInventoryDocuments)

        self.setModels(self.tblInventoryDocuments, self.modelInventoryDocuments, self.selectionModelInventoryDocuments)
        self.tblInventoryDocuments.doubleClicked.connect(self.openInventoryDocument)
        self.tblInventoryDocuments.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.pageBarInventoryDocuments.pageChanged.connect(self.reloadInventoryDocuments)
        self.pageBarInventoryDocuments.pageSizeChanged.connect(self.reloadInventoryDocuments)

        self.btnMakeInventory.clicked.connect(self.createInventoryDocument)

        self.shortcutStoreItems = QtGui.QShortcut(QtGui.QKeySequence('Alt+1'), self, self.onTabStoreItems)
        self.shortcutShippingDocuments = QtGui.QShortcut(QtGui.QKeySequence('Alt+2'), self, self.onTabShippingDocument)
        self.shortcutRequestDocuments = QtGui.QShortcut(QtGui.QKeySequence('Alt+3'), self, self.onTabRequestDocument)
        self.shortcutInventoryDocuments = QtGui.QShortcut(QtGui.QKeySequence('Alt+4'), self, self.onTabInventoryDocument)

        self._settings = {}
        self._srv = None  # type: CPharmacyService
        self.tabWidget.setEnabled(False)
        for tabIdx in range(self.tabWidget.count()):
            self.tabWidget.removeTab(0)

        self.installEventFilter(self)

    def showWarningMessage(self, message):
        QtGui.QMessageBox.warning(self, self.windowTitle(), unicode(message), QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def onTabStoreItems(self):
        if self.tabStoreItem.isEnabled():
            self.tabWidget.setCurrentWidget(self.tabStoreItem)

    @QtCore.pyqtSlot()
    def onTabShippingDocument(self):
        if self.tabShippingDocument.isEnabled():
            self.tabWidget.setCurrentWidget(self.tabShippingDocument)

    @QtCore.pyqtSlot()
    def onTabRequestDocument(self):
        if self.tabRequestDocument.isEnabled():
            self.tabWidget.setCurrentWidget(self.tabRequestDocument)

    @QtCore.pyqtSlot()
    def onTabInventoryDocument(self):
        if self.tabInventoryDocument.isEnabled():
            self.tabWidget.setCurrentWidget(self.tabInventoryDocument)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if obj == self and key in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
                self.reloadCurrentTab()
                return True
            if obj == self and key == QtCore.Qt.Key_Escape:
                return True
        return False

    def reloadCurrentTab(self):
        widget = self.tabWidget.currentWidget()
        if widget == self.tabStoreItem:
            self.reloadStoreItems()
        elif widget == self.tabShippingDocument:
            self.reloadShippingDocuments()
        elif widget == self.tabRequestDocument:
            self.reloadRequestDocuments()
        elif widget == self.tabInventoryDocument:
            self.reloadInventoryDocuments()

    def _initService(self):
        url = self._settings.get('URL')
        user = self._settings.get('User')
        password = self._settings.get('Password')
        if not (url and user and password):
            QtGui.QMessageBox.information(self, self.windowTitle(), u'Не заданы параметры подключения к серверу', QtGui.QMessageBox.Ok)
            return

        srv = CPharmacyService(url, user, password)
        currentUser, error = srv.testConnect()
        if not (currentUser and currentUser.id):
            QtGui.QMessageBox.information(self, u'Не удалось подключиться к серверу', unicode(error), QtGui.QMessageBox.Ok)
            return

        self._srv = srv
        if self._initCache():
            self.tabWidget.setEnabled(True)
            for tabName, tab, isVisible in (
                    (u'Просмотр остатков', self.tabStoreItem, True),
                    (u'Накладные', self.tabShippingDocument, currentUser.hasAnyPermission((UserPermission.EditShipping,
                                                                             UserPermission.FinalizeShipping))),
                    (u'Требования', self.tabRequestDocument, currentUser.hasAnyPermission((UserPermission.EditRequest,
                                                                            UserPermission.FinalizeRequest,
                                                                            UserPermission.EditM11,
                                                                            UserPermission.FinalizeM11))),
                    (u'Инвентаризация', self.tabInventoryDocument, currentUser.hasAnyPermission((UserPermission.EditM11,
                                                                              UserPermission.FinalizeM11)))
            ):
                if isVisible:
                    self.tabWidget.addTab(tab, tabName)
            self.tabWidget.setCurrentIndex(0)

            self.actConnect.setVisible(False)
            self.actDisconnect.setVisible(True)

    def _initCache(self):
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self._srv.getMeasurementUnits()
            fundSources = self._srv.getFundSources()
            orgs = self._srv.getOrganisations()
            users = self._srv.getFlatUserList()
            suppliers = [org for org in orgs if org.type.code == 'supplier']
            stores = self._srv.getStores()
            catalogs = self._srv.getCatalogs()

            self.cmbStoreItemsStore.setItems(stores)
            self.cmbStoreItemsCatalog.setItems(catalogs, addNone=True)
            self.cmbShippingStore.setItems(stores, addNone=True)
            self.cmbShippingSupplier.setItems(suppliers, addNone=True)
            self.cmbShippingFinalizeUser.setItems(users, addNone=True)
            self.cmbShippingFundSource.setItems(fundSources, addNone=True)

            self.cmbRequestDocumentStoreFrom.setItems(stores, addNone=True)
            self.cmbRequestDocumentStoreTo.setItems(stores, addNone=True)
            self.cmbInventoryDocumentStore.setItems(stores)

        except CPharmacyServiceException as e:
            error = e.errorMessage
        except Exception as e:
            error = unicode(e)
        else:
            error = None
        finally:
            QtGui.qApp.restoreOverrideCursor()

        if error:
            QtGui.QMessageBox.warning(self, u'Не удалось инициализировать сервис', unicode(error), QtGui.QMessageBox.Ok)
            return False

        return True

    def _deinitService(self):
        self._srv = None
        CPharmacyService.reset()

        self.clearStoreItemsFilter()
        self.clearShippingDocumentFilter()
        self.clearRequestDocumentFilter()
        self.clearInventoryDocumentFilter()
        self.tblStoreItems.model().clearItems()
        self.tblShippingDocuments.model().clearItems()
        self.tblIncomingRequestDocuments.model().clearItems()
        self.tblOutcomingRequestDocuments.model().clearItems()
        self.tblInventoryDocuments.model().clearItems()

        self.tabWidget.setCurrentIndex(0)
        for tabIdx in range(self.tabWidget.count()):
            self.tabWidget.removeTab(0)
        self.tabWidget.setEnabled(False)
        self.actConnect.setVisible(True)
        self.actDisconnect.setVisible(False)

    def close(self):
        CPharmacyService.reset()
        super(CPharmacyStoreDialog, self).close()

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        self.reloadCurrentTab()

    def loadSettings(self, preferences):
        self._settings = {
            'URL'     : forceStringEx(getPref(preferences, 'URL', '')),
            'User'    : forceStringEx(getPref(preferences, 'User', '')),
            'Password': forceStringEx(getPref(preferences, 'Password', ''))
        }

    def saveSettings(self):
        result = {}
        for k, v in self._settings.iteritems():
            setPref(result, k, toVariant(v))
        return result

    def loadPreferences(self, preferences):
        super(CPharmacyStoreDialog, self).loadPreferences(preferences)
        self.loadSettings(getPref(preferences, 'settings', {}))

    def savePreferences(self):
        preferences = super(CPharmacyStoreDialog, self).savePreferences()
        setPref(preferences, 'settings', self.saveSettings())
        return preferences

    def onSettings(self):
        dlg = CPreferencesDialog(self)
        dlg.setSettings(self._settings)
        if dlg.exec_():
            self._settings = dlg.getSettings()

    # 1
    def clearStoreItemsFilter(self):
        self.cmbStoreItemsStore.setCurrentIndex(0)
        self.edtStoreItemsName.clear()
        self.chkStoreItemsDetailed.setChecked(False)
        self.chkStoreItemsArrivalDate.setChecked(False)
        self.edtStoreItemsArrivalDate.setDate(QtCore.QDate.currentDate())
        self.cmbStoreItemsExpirationClass.setValue(None)

    def resetStoreItemsPage(self):
        self.pageBarStoreItems.setPage(1)

    @withWaitCursor
    @QtCore.pyqtSlot()
    def reloadStoreItems(self):
        if not self._srv: return

        storeId = self.cmbStoreItemsStore.itemId()
        catalogId = self.cmbStoreItemsCatalog.itemId()
        detailed = self.chkStoreItemsDetailed.isChecked()
        name = forceStringEx(self.edtStoreItemsName.text()).lower()
        fields = forceStringEx(self.edtStoreItemsFields.text()).lower()
        byArrivalDate = self.chkStoreItemsArrivalDate.isChecked()
        arrivalDate = self.edtStoreItemsArrivalDate.date()
        expirationClass = self.cmbStoreItemsExpirationClass.value()
        expiryDays = ExpirationClass.getExpiryDays(expirationClass) if expirationClass is not None else None
        page = self.pageBarStoreItems.page()
        pageSize = self.pageBarStoreItems.pageSize()

        if storeId:
            try:
                itemList = self._srv.getStoreStockItems(
                    storeId=storeId,
                    catalogId=catalogId,
                    pageSize=pageSize,
                    page=page,
                    name=name,
                    fields=fields,
                    arrivalDate=arrivalDate if byArrivalDate else None,
                    expiryDays=expiryDays,
                    detailed=detailed
                )
            except CPharmacyServiceException as e:
                self.showWarningMessage(e.errorMessage)
            else:
                self.tblStoreItems.model().setItems(itemList)
                self.pageBarStoreItems.setPageCount(itemList.pageCount)
                self.pageBarStoreItems.setItemsCount(itemList.count)
        else:
            self.tblStoreItems.model().clearItems()
            self.pageBarStoreItems.setPageCount(1)

    def openStoreItem(self, index):
        storeItem = self.tblStoreItems.model().getItem(index.row())
        catalogItemId = storeItem.catalogItemId
        storeId = storeItem.store
        try:
            shippingInfoList = self._srv.getCatalogItemShippingDocuments(catalogItemId, storeId) if catalogItemId and storeId else None
        except CPharmacyServiceException:
            shippingInfoList = None

        dlg = CStoreItemDialog(self)
        dlg.setItem(storeItem, shippingInfoList)
        dlg.exec_()

    @QtCore.pyqtSlot(int)
    def on_btnStoreItemsPrint_printByTemplate(self, templateId):
        storeId = self.cmbStoreItemsStore.itemId()
        detailed = self.chkStoreItemsDetailed.isChecked()

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            catalog = self._srv.getCatalogItems(flat=True)
            items = self._srv.getFlatStoreItems(storeId, detailed=detailed)
        except:
            catalog = []
            items = []
        finally:
            QtGui.qApp.restoreOverrideCursor()

        ctx = CInfoContext()
        data = {
            'catalog': [CCatalogItemInfo(ctx, item=catalogItem) for catalogItem in catalog],
            'items'  : [CStoreStockItemInfo(ctx, item=storeItem) for storeItem in items]
        }
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot()
    def onStoreStockReport(self):
        storeId = self.cmbStoreItemsStore.itemId()
        catalogId = self.cmbStoreItemsCatalog.itemId()

        try:
            CStoreStockReport(self, storeId, catalogId).exec_()
        except CPharmacyServiceException as e:
            self.showWarningMessage(unicode(e))

    # 2
    def clearShippingDocumentFilter(self):
        self.cmbShippingStore.setCurrentIndex(0)
        self.cmbShippingSupplier.setCurrentIndex(0)
        self.cmbShippingFinalizeUser.setCurrentIndex(0)
        self.chkShippingDocumentDate.setChecked(False)
        self.edtShippingDocumentDate.setDate(QtCore.QDate.currentDate())
        self.cmbShippingFundSource.setCurrentIndex(0)

    @withWaitCursor
    @QtCore.pyqtSlot()
    def reloadShippingDocuments(self):
        if not self._srv: return

        storeId = self.cmbShippingStore.itemId()
        supplierId = self.cmbShippingSupplier.itemId()
        finalizeUserId = self.cmbShippingFinalizeUser.itemId()
        byDate = self.chkShippingDocumentDate.isChecked()
        date = self.edtShippingDocumentDate.date()
        fundSource = self.cmbShippingFundSource.itemId()
        pageSize = self.pageBarShippingDocuments.pageSize()
        page = self.pageBarShippingDocuments.page()

        try:
            docs = self._srv.getShippingDocuments(
                pageSize=pageSize,
                page=page,
                store=storeId,
                supplier=supplierId,
                user=finalizeUserId,
                date=date if byDate else None,
                fundSource=fundSource
            )
        except CPharmacyServiceException as e:
            self.showWarningMessage(e.errorMessage)
        else:
            self.tblShippingDocuments.model().setItems(docs)
            self.pageBarShippingDocuments.setPageCount(docs.pageCount)
            self.pageBarShippingDocuments.setItemsCount(docs.count)

    def createShippingDocument(self):
        dlg = CShippingDocumentDialog(self)
        dlg.setEditable(True)
        dlg.exec_()

        self.reloadShippingDocuments()

    def openShippingDocument(self, index):
        document = self.tblShippingDocuments.model().getItem(index.row())  # type: ShippingDocument
        try:
            positions = self._srv.getFlatShippingDocumentPositions(document.id)
        except CPharmacyServiceException as e:
            positions = None

        dlg = CShippingDocumentDialog(self)
        dlg.setDocument(document, positions, editable=not document.finalized)
        dlg.exec_()

    # 3
    @QtCore.pyqtSlot(int)
    def on_tabWidgetRequestDocuments_currentChanged(self, index):
        self.reloadRequestDocuments()

    def clearRequestDocumentFilter(self):
        self.cmbRequestDocumentType.setValue(None)
        self.cmbRequestDocumentStatus.setValue(None)
        self.cmbRequestDocumentStoreFrom.setValue(None)
        self.cmbRequestDocumentStoreTo.setValue(None)
        self.chkRequestDocumentDate.setChecked(False)
        self.edtRequestDocumentDate.setDate(QtCore.QDate.currentDate())

    @withWaitCursor
    @QtCore.pyqtSlot()
    def reloadRequestDocuments(self):
        u"""
        Семантика "отправитель"/"получатель" для документов типа "Требование":
        В сервисе: отправитель/получатель товара
        В интерфейсе: отправитель/получатель документа
        """
        if not self._srv: return

        isIncoming, tbl, pageBar = self.currentRequestDocumentTable()
        storeFromId = self.cmbRequestDocumentStoreFrom.itemId()
        storeToId = self.cmbRequestDocumentStoreTo.itemId()
        docType = self.cmbRequestDocumentType.value()
        docStatus = self.cmbRequestDocumentStatus.value()
        byDate = self.chkRequestDocumentDate.isChecked()
        date = self.edtRequestDocumentDate.date()
        pageSize = pageBar.pageSize()
        page = pageBar.page()

        try:
            docs = self._srv.getRequestDocuments(
                pageSize=pageSize,
                page=page,
                storeFrom=storeToId,
                storeTo=storeFromId,
                docType=docType,
                transferFinished=docStatus,
                date=date if byDate and date else None
            )
        except CPharmacyServiceException as e:
            self.showWarningMessage(e.errorMessage)
        else:
            tbl.model().setItems(docs)
            pageBar.setPageCount(docs.pageCount)
            pageBar.setItemsCount(docs.count)

    def createRequestDocument(self):
        dlg = CRequestDocumentDialog(self)
        dlg.setEditable(True)
        dlg.exec_()

        self.reloadRequestDocuments()

    def openIncomingRequestDocument(self, index):
        document = self.tblIncomingRequestDocuments.model().getItem(index.row())  # type: RequestDocument
        dlg = CM11DocumentDialog(self)
        dlg.setRequestDocument(document, editable=not document.transferFinished)
        dlg.exec_()

        self.reloadRequestDocuments()

    def openOutcomingRequestDocument(self, index):
        document = self.tblOutcomingRequestDocuments.model().getItem(index.row())  # type: RequestDocument
        dlg = CRequestDocumentDialog(self)
        dlg.setDocument(document, editable=False)
        dlg.exec_()

    def currentRequestDocumentTable(self):
        if self.tabWidgetRequestDocuments.currentWidget() == self.tabIncomingRequestDocuments:
            return True, self.tblIncomingRequestDocuments, self.pageBarIncomingRequestDocuments
        else:
            return False, self.tblOutcomingRequestDocuments, self.pageBarOutcomingRequestDocuments

    @QtCore.pyqtSlot(int)
    def on_btnRequestDocumentPrint_printByTemplate(self, templateId):
        storeFromId = self.cmbRequestDocumentStoreFrom.itemId()
        storeToId = self.cmbRequestDocumentStoreTo.itemId()
        date = self.edtRequestDocumentDate.date() if self.chkRequestDocumentDate.isChecked() else None

        catalog = []
        docs = []

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            catalog = self._srv.getCatalogItems(flat=True)
            docs = self._srv.getFlatRequestDocuments(storeFrom=storeToId, storeTo=storeFromId, date=date, positions=True)

        except CPharmacyServiceException as e:
            import logging
            logger = logging.getLogger('requests.packages.urllib3')
            logger.exception(e)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        ctx = CInfoContext()
        data = {
            'catalog': [
                CCatalogItemInfo(ctx, item=catalogItem) for catalogItem in catalog
            ],
            'docs'   : [
                CRequestDocumentInfo(ctx, doc=doc, positions=doc.items) for doc in docs
            ]
        }
        applyTemplate(self, templateId, data)

    # 4
    def clearInventoryDocumentFilter(self):
        self.cmbInventoryDocumentStore.setValue(None)

    @withWaitCursor
    @QtCore.pyqtSlot()
    def reloadInventoryDocuments(self):
        if not self._srv: return

        pageSize = self.pageBarInventoryDocuments.pageSize()
        page = self.pageBarInventoryDocuments.page()
        storeId = self.cmbInventoryDocumentStore.itemId()

        try:
            docs = self._srv.getInventoryDocuments(
                store=storeId,
                pageSize=pageSize,
                page=page
            )
        except CPharmacyServiceException as e:
            self.showWarningMessage(e.errorMessage)
        else:
            self.tblInventoryDocuments.model().setItems(docs)
            self.pageBarInventoryDocuments.setPageCount(docs.pageCount)
            self.pageBarInventoryDocuments.setPageCount(docs.count)

    def createInventoryDocument(self):
        dlg = CInventoryDocumentDialog(self)
        dlg.setEditable(True)
        dlg.exec_()

        self.reloadInventoryDocuments()

    def openInventoryDocument(self, index):
        inventoryDocument = self.tblInventoryDocuments.model().getItem(index.row())
        dlg = CInventoryDocumentDialog(self)
        dlg.setDocument(inventoryDocument, editable=False)
        dlg.exec_()

        self.reloadInventoryDocuments()


if __name__ == '__main__':
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName('utf8'))
    QtGui.qApp.applyDecorPreferences()
    # QtGui.qApp.db = CDatabase()
    QtGui.qApp.db = connectDataBaseByInfo({
        'driverName'      : 'mysql',
        'host'            : '192.168.0.3',
        'port'            : 3306,
        'database'        : 'ant_p17',
        'user'            : 'dbuser',
        'password'        : 'dbpassword',
        'connectionName'  : 'vista-med',
        'compressData'    : True,
        'afterConnectFunc': None
    })  # for print templates

    dlg = CPharmacyStoreDialog(None)
    dlg.loadSettings = lambda *a: None
    dlg._settings = {
        # 'URL'     : 'http://ptd5int:8000',  # ПТД5
        # 'URL'     : 'http://pnd5vm:8000',  # ПНД5
        # 'URL'     : 'http://192.168.0.207:8000',  # test
        'URL'     : 'http://localhost:8000',  # test
        'User'    : 'user',
        'Password': '123'
    }
    dlg.exec_()
