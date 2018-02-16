# -*- coding: utf-8 -*-
import itertools
from PyQt4 import QtCore, QtGui
from collections import defaultdict

from Pharmacy.Service import CPharmacyService
from Pharmacy.Types import BaseDocument, Catalog, Store, StoreItem, StoreStockItem
from Pharmacy.ui.Ui_StoreStockReportSetupDialog import Ui_StoreStockReportSetupDialog
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from library.DialogBase import CDialogBase


class CStoreStockReportSetupDialog(CDialogBase, Ui_StoreStockReportSetupDialog):
    def __init__(self, parent):
        super(CStoreStockReportSetupDialog, self).__init__(parent)
        self.setupUi(self)
        self.edtBegDate.setDate(QtCore.QDate.currentDate())
        self.edtEndDate.setDate(QtCore.QDate.currentDate())
        self.setWindowTitle(u'Отчет за период')

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CStoreStockReport(CReport):
    u""" Отчет по складу за период """

    def __init__(self, parent, storeId, catalogId=None):
        super(CStoreStockReport, self).__init__(parent)
        self.setTitle(u'Отчет за период')
        self.storeId = storeId
        self.catalogId = catalogId
        self.srv = CPharmacyService.getInstance()

    def getSetupDialog(self, parent):
        dlg = CStoreStockReportSetupDialog(parent)
        dlg.setWindowTitle(self.title())
        return dlg

    def getDescription(self, params):
        store = self.srv.getItem(Store, self.storeId)
        rows = [
            u'Склад: {0}'.format(store.name)
        ]
        if self.catalogId:
            catalog = self.srv.getItem(Catalog, self.catalogId)
            rows.append(u'Каталог: {0}'.format(catalog.name))
        return rows

    def getDefaultParams(self):
        return {}

    def build(self, params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')

        before = defaultdict(int)
        delta = defaultdict(int)
        income = defaultdict(int)
        outcome = defaultdict(int)
        after = defaultdict(int)

        units = dict((unit.id, unit.name) for unit in self.srv.getMeasurementUnits())
        storeItems = dict((storeItem.id, storeItem) for storeItem in self.srv.getStoreItems())
        currentStoreStock = self.srv.getFlatStoreItems(storeId=self.storeId, catalogId=self.catalogId, detailed=True)
        shipping = self.srv.getFlatShippingDocuments(storeId=self.storeId, finalized=True, items=True)
        inventory = self.srv.getFlatInventoryDocuments(storeId=self.storeId, finalized=True, items=True)
        m11From = self.srv.getFlatM11Documents(storeFrom=self.storeId, finalized=True, items=True)
        m11To = self.srv.getFlatM11Documents(storeTo=self.storeId, finalized=True, items=True)

        docs = sorted(itertools.chain.from_iterable((shipping, inventory, m11From, m11To)), key=lambda doc: doc.date)

        for doc in docs:  # type: BaseDocument
            storeDelta = doc.getStoreItemDelta(storeId=self.storeId)

            if doc.finalizeDate.date() < begDate:
                target = before
            elif doc.finalizeDate.date() > endDate:
                target = after
            else:
                target = delta
                for itemId, deltaAmount in storeDelta.items():
                    if deltaAmount > 0:
                        income[itemId] += deltaAmount
                    else:
                        outcome[itemId] += abs(deltaAmount)

            for itemId, deltaAmount in storeDelta.items():
                target[itemId] += deltaAmount

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        self.dumpParams(cursor, params)

        table = createTable(cursor, [
            ('10?', [u'Торговое наименование'], CReportBase.AlignLeft),
            ('10?', [u'Дозировка'], CReportBase.AlignLeft),
            ('10?', [u'МНН'], CReportBase.AlignLeft),
            ('10?', [u'Ед. изм.'], CReportBase.AlignLeft),
            ('10?', [u'Серия'], CReportBase.AlignLeft),
            ('10?', [u'Срок годности'], CReportBase.AlignLeft),
            ('10?', [u'Остаток на начало периода'], CReportBase.AlignRight),
            ('10?', [u'Приход'], CReportBase.AlignRight),
            ('10?', [u'Расход'], CReportBase.AlignRight),
            ('10?', [u'Остаток на конец периода'], CReportBase.AlignRight),
        ])

        for storeStockItem in sorted(currentStoreStock, key=lambda it: it.tradeName):  # type: StoreStockItem
            item = storeItems.get(storeStockItem.itemId, StoreItem())  # type: StoreItem
            table.addRowWithContent(item.tradeName,
                                    item.dosage,
                                    item.INN,
                                    units.get(item.unit, ''),
                                    item.serial,
                                    item.expiryDate.toString('dd.MM.yyyy'),
                                    before[item.id],
                                    income[item.id],
                                    outcome[item.id],
                                    before[item.id] + delta[item.id])

        return doc
