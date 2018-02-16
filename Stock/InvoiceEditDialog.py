# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils               import forceRef, forceDouble, toVariant
from library.crbcombobox         import CRBComboBox
from library.InDocTable          import CInDocTableModel, CInDocTableCol, CDateInDocTableCol, CFloatInDocTableCol, \
                                        CRBInDocTableCol
from library.interchange         import getRBComboBoxValue, setRBComboBoxValue

from Stock.NomenclatureComboBox  import CNomenclatureInDocTableCol
from Stock.StockMotionBaseDialog import CStockMotionBaseDialog

from Ui_Invoice import Ui_InvoiceDialog


class CInvoiceEditDialog(CStockMotionBaseDialog, Ui_InvoiceDialog):
    def __init__(self,  parent):
        CStockMotionBaseDialog.__init__(self, parent)

        self.addModels('Items', CItemsModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setupDirtyCather()
        self.tblItems.setModel(self.modelItems)
        self.prepareItemsPopupMenu(self.tblItems)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.requisitionIdList = None


    def setDefaults(self):
        CStockMotionBaseDialog.setDefaults(self)


    def setRequsitions(self, requisitionIdList):
        if requisitionIdList:
            requisitionId = requisitionIdList[0]
            self.cmbReceiver.setValue(forceRef(QtGui.qApp.db.translate('StockRequisition', 'id', requisitionId, 'recipient_id')))
            self.modelItems.setRequsitions(requisitionIdList)
            self.requisitionIdList = requisitionIdList


    def setRecord(self, record):
        CStockMotionBaseDialog.setRecord(self, record)
        setRBComboBoxValue( self.cmbReceiver, record, 'receiver_id')
        setRBComboBoxValue( self.cmbReceiverPerson, record, 'receiverPerson_id')
        self.modelItems.loadItems(self.itemId())
        self.setIsDirty(False)


    def getRecord(self):
        record = CStockMotionBaseDialog.getRecord(self)
        getRBComboBoxValue( self.cmbReceiver, record, 'receiver_id')
        getRBComboBoxValue( self.cmbReceiverPerson, record, 'receiverPerson_id')
        record.setValue('type', 0)
        return record


    def saveInternals(self, id):
        self.modelItems.saveItems(id)
        if self.requisitionIdList:
            self.updateRequisition()


    def updateRequisition(self):
        db = QtGui.qApp.db
        tableSR = db.table('StockRequisition')
        tableSRI = db.table('StockRequisition_Item')
        table = tableSRI.leftJoin(tableSR, tableSR['id'].eq(tableSRI['master_id']))
        requisitionItems = db.getRecordList(table,
                           'StockRequisition_Item.*',
                           [tableSRI['master_id'].inlist(self.requisitionIdList),
                            tableSR['recipient_id'].eq(self.cmbReceiver.value())
                           ],
                           'master_id, idx')

        fndict = self.modelItems.getDataAsFNDict()
        preciseGroupDict = {}
        for item in requisitionItems:
            nomenclatureId = forceRef(item.value('nomenclature_id'))
            financeId = forceRef(item.value('finance_id'))
            qnt = forceDouble(item.value('qnt'))
            satisfiedQnt = forceDouble(item.value('satisfiedQnt'))
            oldSatisfiedQnt = satisfiedQnt
            ndict = fndict.get(financeId, None)
            if ndict:
                if nomenclatureId in ndict:
                    nomenclatureIdList = [nomenclatureId]
                else:
                    nomenclatureIdList = preciseGroupDict.get(nomenclatureId, None)
                    if nomenclatureIdList is None:
                        nomenclatureIdList = getNomenclatureAnalogies(nomenclatureId)
                        preciseGroupDict[nomenclatureId] = nomenclatureIdList
                for nomenclatureId in nomenclatureIdList:
                    if nomenclatureId in ndict:
                        outQnt = ndict[nomenclatureId]
                        delta = min(max(0, qnt-satisfiedQnt), outQnt)
                        if delta>0:
                            ndict[nomenclatureId] -= delta
                            satisfiedQnt += delta
            if oldSatisfiedQnt != satisfiedQnt:
                item.setValue('satisfiedQnt', toVariant(satisfiedQnt))
                db.updateRecord('StockRequisition_Item', item)


    def checkDataEntered(self):
        result = True
#        result = result and (self.cmbPurpose.value() or self.checkInputMessage(u'назначение', False, self.cmbPurpose))
#        result = result and self.checkItemsDataEntered()
        return result


#    def checkItemsDataEntered(self):
#        for row, item in enumerate(self.modelItems.items()):
#            if not self.checkItemDataEntered(row, item):
#                return False
#        return True
#
#
#    def checkItemDataEntered(self, row, item):
#        nomenclatureId = forceString(item.value('nomenclature_id'))
#        qnt            = forceDouble(item.value('qnt'))
#        result = nomenclatureId or self.checkInputMessage(u'лекарственное средство или изделие медицинского назначения', False, self.tblProperties, row, 0)
#        result = result and (qnt or self.checkInputMessage(u'количество', False, self.tblProperties, row, 2))
#        return result

    @QtCore.pyqtSlot(int)
    def on_cmbReceiver_currentIndexChanged(self, val):
        orgStructureId = self.cmbReceiver.value()
#        if orgStructureId:
        self.cmbReceiverPerson.setOrgStructureId(orgStructureId)



class CItemsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'StockMotion_Item', 'id', 'master_id', parent)
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields = CRBComboBox.showName))
        self.addCol(CInDocTableCol( u'Партия', 'batch', 16))
        self.addCol(CDateInDocTableCol( u'Годен до', 'shelfTime', 12, canBeEmpty=True))
        self.addCol(CRBInDocTableCol(    u'Тип финансирования', 'finance_id', 15, 'rbFinance'))
        self.addCol(CFloatInDocTableCol( u'Кол-во', 'qnt', 12))
        self.addCol(CFloatInDocTableCol( u'Сумма', 'sum', 12))
        self.priceCache = parent


    def calcSum(self, item):
        nomenclatureId = forceRef(item.value('nomenclature_id'))
        financeId = forceRef(item.value('finance_id'))
        price = self.priceCache.getPrice(nomenclatureId, financeId)
        return forceDouble(item.value('qnt'))*price


    def setRequsitions(self, requisitionIdList):
        db = QtGui.qApp.db
        table = db.table('StockRequisition_Item')
        requisitionItems = db.getRecordList(table,
                           '*',
                           table['master_id'].inlist(requisitionIdList),
                           'master_id, idx')
        for item in requisitionItems:
            qnt = forceDouble(item.value('qnt'))-forceDouble(item.value('satisfiedQnt'))
            if qnt>0:
                myItem = self.getEmptyRecord()
                myItem.setValue('nomenclature_id', item.value('nomenclature_id'))
                myItem.setValue('finance_id',      item.value('finance_id'))
                myItem.setValue('qnt',             toVariant(qnt))
                myItem.setValue('sum',             toVariant(self.calcSum(myItem)))
                self.items().append(myItem)
        self.reset()


    def getDataAsFNDict(self):
        result = {}
        for item in self.items():
            financeId = forceRef(item.value('finance_id'))
            nomenclatureId = forceRef(item.value('nomenclature_id'))
            if financeId and nomenclatureId:
                ndict = result.setdefault(financeId, {})
                ndict[nomenclatureId]=ndict.get(nomenclatureId, 0) + forceDouble(item.value('qnt'))
        return result


def getNomenclatureAnalogies(nomenclatureId):
    db = QtGui.qApp.db
    tableNomenclature = db.table('rbNomenclature')
    tableNomenclature2 = db.table('rbNomenclature').alias('RBN2')
    table = tableNomenclature.leftJoin(tableNomenclature2,
                                       tableNomenclature2['analog_id'].eq(tableNomenclature['analog_id']))
    return db.getIdList(table,
                        tableNomenclature['id'],
                        db.joinAnd([
                                    tableNomenclature2['id'].eq(nomenclatureId),
                                    tableNomenclature['analog_id'].isNotNull(),
                                   ]
                                  )
                       )
