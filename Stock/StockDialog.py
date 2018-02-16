# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""Работа: складской учёт"""

from PyQt4 import QtGui, QtCore

from library.crbcombobox              import CRBComboBox
from library.DialogBase               import CDialogBase
from library.InDocTable               import CRecordListModel, CInDocTableCol, CRBInDocTableCol, CFloatInDocTableCol, \
                                             CDateInDocTableCol
from library.TableModel               import CTableModel, CDateCol, CDateTimeCol, CEnumCol, CRefBookCol, CTextCol
from library.Utils                    import forceDouble, forceString, forceStringEx, toVariant, formatRecordsCount, \
                                             smartDict

from Orgs.Utils                       import getOrgStructureDescendants, getOrgStructureFullName

from Stock.FinTransferEditDialog      import CFinTransferEditDialog
from Stock.InventoryEditDialog        import CInventoryEditDialog
from Stock.InvoiceEditDialog          import CInvoiceEditDialog
from Stock.NomenclatureComboBox       import CNomenclatureInDocTableCol
from Stock.ProductionEditDialog       import CProductionEditDialog
from Stock.StockMotion                import editStockMotion
from Stock.StockRequisitionEditDialog import CStockRequisitionEditDialog

from Ui_StockDialog import Ui_Dialog


class CStockDialog(CDialogBase, Ui_Dialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.addModels('Motions',   CMyMotionsModel(self))
        self.mnuMotions =        QtGui.QMenu(self)
        self.mnuMotions.setObjectName('mnuMotions')
        self.actAddInvoice =     QtGui.QAction(u'Создать накладную', self)
        self.actAddInvoice.setObjectName('actAddInvoice')
        self.actAddInventory =   QtGui.QAction(u'Создать инвентаризацию', self)
        self.actAddInventory.setObjectName('actAddInventory')
        self.actAddFinTransfer = QtGui.QAction(u'Создать фин.перенос', self)
        self.actAddFinTransfer.setObjectName('actAddFinTransfer')
        self.actAddProduction =  QtGui.QAction(u'Создать производство', self)
        self.actAddProduction.setObjectName('actAddProduction')
        self.actEditMotion =     QtGui.QAction(u'Редактировать движение', self)
        self.actEditMotion.setObjectName('actEditMotion')

        self.mnuMotions.addAction(self.actAddInvoice)
        self.mnuMotions.addAction(self.actAddInventory)
        self.mnuMotions.addAction(self.actAddFinTransfer)
        self.mnuMotions.addAction(self.actAddProduction)
        self.mnuMotions.addSeparator()
        self.mnuMotions.addAction(self.actEditMotion)

        self.addModels('Remainings', CRemainingsModel(self))

        self.addModels('MRs',       CMyRequisitionsModel(self))
        self.mnuMRs =    QtGui.QMenu(self)
        self.mnuMRs.setObjectName('mnuMRs')
        self.actAddRequisition = QtGui.QAction(u'Создать требование', self)
        self.actAddRequisition.setObjectName('actAddRequisition')
        self.actEditRequisition = QtGui.QAction(u'Редактировать требование', self)
        self.actEditRequisition.setObjectName('actEditRequisition')
        self.actRevokeRequisition = QtGui.QAction(u'Отменить требование', self)
        self.actRevokeRequisition.setObjectName('actRevokeRequisition')
        self.mnuMRs.addAction(self.actAddRequisition)
        self.mnuMRs.addAction(self.actEditRequisition)
        self.mnuMRs.addAction(self.actRevokeRequisition)
        self.addModels('MRContent', CRequisitionContentModel(self))

        self.addModels('RTMs',       CRequisitionsToMeModel(self))
        self.mnuRTMs = QtGui.QMenu(self)
        self.mnuRTMs.setObjectName('mnuRTMs')
#        self.addObject('actOpenClient', QtGui.QAction(u'Открыть регистрационную карточку', self))
        self.actCreateMotionByRequisition = QtGui.QAction(u'Создать движение по требованию', self)
        self.actCreateMotionByRequisition.setObjectName('actCreateMotionByRequisition')
#        self.addObject('actRejectRequisition', QtGui.QAction(u'Отказать в требование', self))
        self.mnuRTMs.addAction(self.actCreateMotionByRequisition)
#        self.mnuRTMs.addAction(self.actRejectRequisition)
        self.addModels('RTMContent', CRequisitionContentModel(self))

        self.btnPrint = QtGui.QPushButton(u'Печать', self)

        self.btnPrint.setObjectName('btnPrint')
        self.btnPrint.setShortcut('F6')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        if QtGui.qApp.currentOrgStructureId():
            self.setWindowTitle(u'Склад ЛСиИМН: %s' % getOrgStructureFullName(QtGui.qApp.currentOrgStructureId()))

        self.bbxMotionsFilter.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        self.bbxRemainingsFilter.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        self.bbxMRsFilter.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        self.bbxRTMsFilter.button(QtGui.QDialogButtonBox.Apply).setDefault(True)

        self.cmbMotionsFilterNomenclature.setTable('rbNomenclature', order='name')
        self.cmbMotionsFilterFinance.setTable('rbFinance', True)

        self.cmbRemainingsFilterNomenclature.setTable('rbNomenclature', order='name')
        self.cmbRemainingsFilterFinance.setTable('rbFinance', True)

        self.cmbMRsFilterNomenclature.setTable('rbNomenclature', order='name')
        self.cmbRTMsFilterNomenclature.setTable('rbNomenclature', order='name')

        self.tblMotions.setModel(self.modelMotions)
        self.tblMotions.setSelectionModel(self.selectionModelMotions)
        self.tblMotions.setPopupMenu(self.mnuMotions)

        self.tblRemainings.setModel(self.modelRemainings)
        self.tblRemainings.setSelectionModel(self.selectionModelRemainings)

        self.tblMRs.setModel(self.modelMRs)
        self.tblMRs.setSelectionModel(self.selectionModelMRs)
        self.tblMRs.setPopupMenu(self.mnuMRs)
        self.tblMRContent.setModel(self.modelMRContent)
        self.tblMRContent.setSelectionModel(self.selectionModelMRContent)

        self.tblRTMs.setModel(self.modelRTMs)
        self.tblRTMs.setSelectionModel(self.selectionModelRTMs)
        self.tblRTMs.setPopupMenu(self.mnuRTMs)

        self.tblRTMContent.setModel(self.modelRTMContent)
        self.tblRTMContent.setSelectionModel(self.selectionModelRTMContent)

        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)

        self.motionsFilter = smartDict()
        self.remainingsFilter = smartDict()
        self.MRsFilter = smartDict()
        self.RTMsFilter = smartDict()

        self.controlSplitter = None
#        self.visitedMotions = False
        self.visitedMRs = False
        self.visitedRTMs = False

#        self.connect(self.tblMRs.horizontalHeader(), SIGNAL('sectionClicked(int)'), self.setMRsSort)
#        self.connect(self.tblRTMs.horizontalHeader(), SIGNAL('sectionClicked(int)'), self.setRTMsSort)



    def exec_(self):
        self.tabWidget.setCurrentIndex(0)
        self.resetMotionsFilter()
        self.applyMotionsFilter()
        CDialogBase.exec_(self)


    def syncSplitters(self, nextSplitter):
        if self.controlSplitter and nextSplitter != self.controlSplitter:
            nextSplitter.setSizes(self.controlSplitter.sizes())
            self.controlSplitter = nextSplitter
        else:
            self.controlSplitter = nextSplitter


    def composeDateTime(self, date, time):
        if date:
            return QtCore.QDateTime(date, time)
        else:
            return QtCore.QDateTime()


    def getRequisitionItemIdList(self, requisitionId):
        if requisitionId:
            db = QtGui.qApp.db
            table = db.table('StockRequisition_Item')
            cond = table['master_id'].eq(requisitionId)
            return db.getIdList(table, 'id', where=cond, order='idx, id')
        else:
            return []


    # MR ##(my requests)########################################################

    def resetMRsFilter(self):
        self.chkMRsFilterOnlyActive.setChecked(True)
        self.edtMRsFilterBegDate.setDate(QtCore.QDate())
        self.edtMRsFilterEndDate.setDate(QtCore.QDate())
        self.edtMRsFilterBegDeadlineDate.setDate(QtCore.QDate())
        self.edtMRsFilterEndDeadlineDate.setDate(QtCore.QDate())
        self.edtMRsFilterBegDeadlineTime.setTime(QtCore.QTime())
        self.edtMRsFilterEndDeadlineTime.setTime(QtCore.QTime())
        self.cmbMRsFilterOrgStructure.setValue(None)
        self.cmbMRsFilterNomenclature.setValue(None)


    def applyMRsFilter(self):
        self.MRsFilter.onlyActive = self.chkMRsFilterOnlyActive.isChecked()
        self.MRsFilter.begDate = self.edtMRsFilterBegDate.date()
        self.MRsFilter.endDate = self.edtMRsFilterEndDate.date()
        self.MRsFilter.begDeadline = self.composeDateTime(self.edtMRsFilterBegDeadlineDate.date(), self.edtMRsFilterBegDeadlineTime.time())
        self.MRsFilter.endDeadline = self.composeDateTime(self.edtMRsFilterEndDeadlineDate.date(), self.edtMRsFilterEndDeadlineTime.time())
        self.MRsFilter.orgStructureId = self.cmbMRsFilterOrgStructure.value()
        self.MRsFilter.nomenclatureId = self.cmbMRsFilterNomenclature.value()
        self.updateMRsList()


#    def setMRsSort(self, col):
#        self.order = col
#        header=self.tblItems.horizontalHeader()
#        header.setSortIndicatorShown(True)
#        header.setSortIndicator(col, Qt.AscendingOrder)
#        self.updateMRsList()

    def updateMRsList(self, currentId=None):
        filter = self.MRsFilter
        db = QtGui.qApp.db
        table = db.table('StockRequisition')
        tableItems = db.table('StockRequisition_Item')
        cond = [table['deleted'].eq(0),
                table['recipient_id'].eq(QtGui.qApp.currentOrgStructureId()),
               ]
        if filter.orgStructureId:
            cond.append(table['supplier_id'].inlist(getOrgStructureDescendants(filter.orgStructureId)))
        if filter.onlyActive:
            cond.append(table['revoked'].eq(0))
        if filter.begDate:
            cond.append(table['date'].ge(filter.begDate))
        if filter.endDate:
            cond.append(table['date'].le(filter.endDate))
        if filter.begDeadline:
            cond.append(table['deadline'].ge(filter.begDeadline))
        if filter.endDeadline:
            cond.append(table['deadline'].le(filter.endDeadline))
        if filter.nomenclatureId:
            subcond = [tableItems['master_id'].eq(table['id']),
                       tableItems['nomenclature_id'].eq(filter.nomenclatureId),
                      ]
            if filter.onlyActive:
                subcond.append(tableItems['qnt'].ge(tableItems['satisfiedQnt']))
            cond.append(db.existsStmt(tableItems, subcond))
        idList = db.getIdList(table, idCol=table['id'], where=cond, order='date, deadline')
        self.tblMRs.setIdList(idList, currentId)
        self.lblMRs.setText(formatRecordsCount(len(idList)))


    def addRequisition(self):
        dialog = CStockRequisitionEditDialog(self)
        dialog.setDefaults()
        id = dialog.exec_()
        if id:
            self.updateMRsList(id)


    def editRequisition(self, id):
        dialog = CStockRequisitionEditDialog(self)
        dialog.load(id)
        id = dialog.exec_()
        if id:
            self.updateMRsList(id)



    def updateMRContent(self, requisitionId):
        self.tblMRContent.setIdList(self.getRequisitionItemIdList(requisitionId))

    # Motions ########################################################

    def resetMotionsFilter(self):
        self.edtMotionsFilterBegDate.setDate(QtCore.QDate.currentDate().addDays(-7))
        self.edtMotionsFilterEndDate.setDate(QtCore.QDate())
        self.cmbMotionsFilterSupplier.setValue(None)
        self.cmbMotionsFilterReceiver.setValue(None)
        self.cmbMotionsFilterNomenclature.setValue(None)
        self.cmbMotionsFilterFinance.setValue(None)
        self.edtMotionsFilterNote.setText('')


    def applyMotionsFilter(self):
        filter = self.motionsFilter
        filter.begDate = self.edtMotionsFilterBegDate.date()
        filter.endDate = self.edtMotionsFilterEndDate.date()
        filter.supplierId = self.cmbMotionsFilterSupplier.value()
        filter.receiverId = self.cmbMotionsFilterReceiver.value()
        filter.note = forceString(self.edtMotionsFilterNote.text())
        filter.nomenclatureId = self.cmbMotionsFilterNomenclature.value()
        filter.financeId = self.cmbMotionsFilterFinance.value()
        self.updateMotionsList()


    def updateMotionsList(self, currentId=None):
        filter = self.motionsFilter
        db = QtGui.qApp.db
        table = db.table('StockMotion')
        tableItems = db.table('StockMotion_Item')
        cond = [table['deleted'].eq(0),
                db.joinOr([ table['supplier_id'].eq(QtGui.qApp.currentOrgStructureId()),
                            table['receiver_id'].eq(QtGui.qApp.currentOrgStructureId())])
               ]
        if filter.supplierId:
#            cond.append(table['supplier_id'].inlist(getOrgStructureDescendants(filter.orgStructureId)))
            cond.append(table['supplier_id'].eq(filter.supplierId))
        if filter.receiverId:
#            cond.append(table['supplier_id'].inlist(getOrgStructureDescendants(filter.orgStructureId)))
            cond.append(table['receiver_id'].eq(filter.receiverId))
        if filter.begDate:
            cond.append(table['date'].ge(filter.begDate))
        if filter.endDate:
            cond.append(table['date'].lt(filter.endDate.addDays(1)))
        if filter.note:
            cond.append(table['note'].like(filter.note))
        if filter.nomenclatureId or filter.financeId:
            subcond = [tableItems['master_id'].eq(table['id'])]
            if filter.nomenclatureId:
                subcond.append(tableItems['nomenclature_id'].eq(filter.nomenclatureId))
            if filter.financeId:
                subcond.append(tableItems['finance_id'].eq(filter.financeId))
            cond.append(db.existsStmt(tableItems, subcond))
        idList = db.getIdList(table, idCol=table['id'], where=cond, order='date DESC, id DESC')
        self.tblMotions.setIdList(idList, currentId)
        self.lblMotions.setText(formatRecordsCount(len(idList)))


    def addMotion(self, dialogClass, requisitionIdList = None):
        dialog = dialogClass(self)
        dialog.setDefaults()
        if requisitionIdList:
            dialog.setRequsitions(requisitionIdList)
        id = dialog.exec_()
        if id:
            self.updateMotionsList(id)


    def addInvoice(self, requisitionIdList = None):
        self.addMotion(CInvoiceEditDialog, requisitionIdList)


    def addInventory(self):
        self.addMotion(CInventoryEditDialog)


    def addFinTransfer(self):
        self.addMotion(CFinTransferEditDialog)


    def addProduction(self):
        self.addMotion(CProductionEditDialog)

    # Remainings #####################################################

    def resetRemainingsFilter(self):
        self.edtRemainingsFilterDate.setDate(QtCore.QDate())
        self.cmbRemainingsFilterStorage.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbRemainingsFilterNomenclature.setValue(None)
        self.chkRemainingsFilterGroupByBatch.setChecked(False)
        self.edtRemainingsFilterBatch.setText('')
        self.edtRemainingsFilterBegShelfTime.setDate(QtCore.QDate())
        self.edtRemainingsFilterEndShelfTime.setDate(QtCore.QDate())
        self.cmbRemainingsFilterFinance.setValue(None)
        self.chkRemainingsFilterConstrainedQnt.setChecked(False)
        self.chkRemainingsFilterOrderQnt.setChecked(False)
        self.edtMotionsFilterNote.setText('')


    def applyRemainingsFilter(self):
        filter = self.remainingsFilter
        filter.date = self.edtRemainingsFilterDate.date()
        filter.storageId = self.cmbRemainingsFilterStorage.value()
        filter.nomenclatureId = self.cmbRemainingsFilterNomenclature.value()
        filter.groupByBatch = self.chkRemainingsFilterGroupByBatch.isChecked()
        filter.batch = forceStringEx(self.edtRemainingsFilterBatch.text())
        filter.begShelfTime = self.edtRemainingsFilterBegShelfTime.date()
        filter.endShelfTime = self.edtRemainingsFilterEndShelfTime.date()
        filter.financeId = self.cmbRemainingsFilterFinance.value()
        filter.constrainedQnt = self.chkRemainingsFilterConstrainedQnt.isChecked()
        filter.orderQnt = self.chkRemainingsFilterOrderQnt.isChecked()
        self.updateRemainingsList()


    def updateRemainingsList(self, currentId=None):
        filter = self.remainingsFilter
        self.modelRemainings.loadData(filter.date,
                                      filter.storageId,
                                      filter.nomenclatureId,
                                      filter.groupByBatch,
                                      filter.batch,
                                      filter.begShelfTime,
                                      filter.endShelfTime,
                                      filter.financeId,
                                      filter.constrainedQnt,
                                      filter.orderQnt
                                      )

    # RTMs ##(requests to me)####################################################

    def resetRTMsFilter(self):
        self.chkRTMsFilterOnlyActive.setChecked(True)
        self.edtRTMsFilterBegDate.setDate(QtCore.QDate())
        self.edtRTMsFilterEndDate.setDate(QtCore.QDate())
        self.edtRTMsFilterBegDeadlineDate.setDate(QtCore.QDate())
        self.edtRTMsFilterEndDeadlineDate.setDate(QtCore.QDate())
        self.edtRTMsFilterBegDeadlineTime.setTime(QtCore.QTime())
        self.edtRTMsFilterEndDeadlineTime.setTime(QtCore.QTime())
        self.cmbRTMsFilterOrgStructure.setValue(None)
        self.cmbRTMsFilterNomenclature.setValue(None)


    def applyRTMsFilter(self):
        self.RTMsFilter.onlyActive = self.chkRTMsFilterOnlyActive.isChecked()
        self.RTMsFilter.begDate = self.edtRTMsFilterBegDate.date()
        self.RTMsFilter.endDate = self.edtRTMsFilterEndDate.date()
        self.RTMsFilter.begDeadline = self.composeDateTime(self.edtRTMsFilterBegDeadlineDate.date(), self.edtRTMsFilterBegDeadlineTime.time())
        self.RTMsFilter.endDeadline = self.composeDateTime(self.edtRTMsFilterEndDeadlineDate.date(), self.edtRTMsFilterEndDeadlineTime.time())
        self.RTMsFilter.orgStructureId = self.cmbRTMsFilterOrgStructure.value()
        self.RTMsFilter.nomenclatureId = self.cmbRTMsFilterNomenclature.value()
        self.updateRTMsList()


    def updateRTMsList(self, currentId=None):
        filter = self.RTMsFilter
        db = QtGui.qApp.db
        table = db.table('StockRequisition')
        tableItems = db.table('StockRequisition_Item')
        cond = [table['deleted'].eq(0),
                table['supplier_id'].eq(QtGui.qApp.currentOrgStructureId()),
               ]
        if filter.orgStructureId:
            cond.append(table['recipient_id'].inlist(getOrgStructureDescendants(filter.orgStructureId)))
        if filter.onlyActive:
            cond.append(table['revoked'].eq(0))
        if filter.begDate:
            cond.append(table['date'].ge(filter.begDate))
        if filter.endDate:
            cond.append(table['date'].le(filter.endDate))
        if filter.begDeadline:
            cond.append(table['deadline'].ge(filter.begDeadline))
        if filter.endDeadline:
            cond.append(table['deadline'].le(filter.endDeadline))
        if filter.nomenclatureId:
            subcond = [tableItems['master_id'].eq(table['id']),
                       tableItems['nomenclature_id'].eq(filter.nomenclatureId),
                      ]
            if filter.onlyActive:
                subcond.append(tableItems['qnt'].ge(tableItems['satisfiedQnt']))
            cond.append(db.existsStmt(tableItems, subcond))
        idList = db.getIdList(table, idCol=table['id'], where=cond, order='date, deadline')
        self.tblRTMs.setIdList(idList, currentId)
        self.lblRTMs.setText(formatRecordsCount(len(idList)))


    def updateRTMContent(self, requisitionId):
        self.tblRTMContent.setIdList(self.getRequisitionItemIdList(requisitionId))


    # slots ####################################################################

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        if index == 0:
            self.syncSplitters(self.splitterMotions)
#            self.btnPrint.setEnabled(True)
#            self.btnCash.setEnabled(False)
            self.applyMotionsFilter()
        elif index == 1:
            self.syncSplitters(self.splitterRemainings)
            self.applyRemainingsFilter() # обновляем всегда
        elif index == 2:
            self.syncSplitters(self.splitterMRs)
            if not self.visitedMRs:
                self.resetMRsFilter()
                self.visitedMRs = True
            self.applyMRsFilter()

        elif index == 3:
            self.syncSplitters(self.splitterRTMs)
            if not self.visitedRTMs:
                self.resetRTMsFilter()
                self.visitedRTMs = True
            self.applyRTMsFilter()

    # Motions ########################################################

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_bbxMotionsFilter_clicked(self, button):
        buttonCode = self.bbxMotionsFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyMotionsFilter()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetMotionsFilter()
            self.applyMotionsFilter()


    @QtCore.pyqtSlot()
    def on_actAddInvoice_triggered(self):
        self.addInvoice()


    @QtCore.pyqtSlot()
    def on_actAddInventory_triggered(self):
        self.addInventory()


    @QtCore.pyqtSlot()
    def on_actAddFinTransfer_triggered(self):
        self.addFinTransfer()


    @QtCore.pyqtSlot()
    def on_actAddProduction_triggered(self):
        self.addProduction()


    @QtCore.pyqtSlot()
    def on_actEditMotion_triggered(self):
        id = self.tblMotions.currentItemId()
        if id:
            editStockMotion(self, id)

    # Remainings #####################################################


    @QtCore.pyqtSlot(bool)
    def on_chkRemainingsFilterGroupByBatch_toggled(self, val):
        self.lblRemainingsFilterBatch.setEnabled(val)
        self.edtRemainingsFilterBatch.setEnabled(val)
        self.lblRemainingsFilterBegShelfTime.setEnabled(val)
        self.edtRemainingsFilterBegShelfTime.setEnabled(val)
        self.lblRemainingsFilterEndShelfTime.setEnabled(val)
        self.edtRemainingsFilterEndShelfTime.setEnabled(val)


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_bbxRemainingsFilter_clicked(self, button):
        buttonCode = self.bbxRemainingsFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyRemainingsFilter()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetRemainingsFilter()
            self.applyRemainingsFilter()

    # MR ##(my requests)########################################################

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtMRsFilterBegDeadlineDate_dateChanged(self, date):
        self.edtMRsFilterBegDeadlineTime.setEnabled(bool(date))


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtMRsFilterEndDeadlineDate_dateChanged(self, date):
        self.edtMRsFilterEndDeadlineTime.setEnabled(bool(date))


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_bbxMRsFilter_clicked(self, button):
        buttonCode = self.bbxMRsFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyMRsFilter()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetMRsFilter()
            self.applyMRsFilter()


    @QtCore.pyqtSlot()
    def on_actAddRequisition_triggered(self):
        self.addRequisition()

    @QtCore.pyqtSlot()
    def on_actEditRequisition_triggered(self):
        id = self.tblMRs.currentItemId()
        if id:
            self.editRequisition(id)
            self.updateMRContent(id)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelMRs_currentRowChanged(self, current, previous):
        id = self.tblMRs.itemId(current)
        self.updateMRContent(id)


    # RTMs ##(requests to me)####################################################

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtRTMsFilterBegDeadlineDate_dateChanged(self, date):
        self.edtRTMsFilterBegDeadlineTime.setEnabled(bool(date))


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtRTMsFilterEndDeadlineDate_dateChanged(self, date):
        self.edtRTMsFilterEndDeadlineTime.setEnabled(bool(date))


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_bbxRTMsFilter_clicked(self, button):
        buttonCode = self.bbxRTMsFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyRTMsFilter()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetRTMsFilter()
            self.applyRTMsFilter()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelRTMs_currentRowChanged(self, current, previous):
        id = self.tblRTMs.itemId(current)
        self.updateRTMContent(id)


    @QtCore.pyqtSlot()
    def on_actCreateMotionByRequisition_triggered(self):
        id = self.tblRTMs.currentItemId()
        if id:
            self.addInvoice([id])
            self.updateRTMContent(id)

#
# ##############################################################################
#

class CMyMotionsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CEnumCol(     u'Тип',           ['type'],  [u'Накладная',
                                                        u'Инвентаризация',
                                                        u'Фин.переброска',
                                                        u'Производство',
                                                        u'Списание',
                                                       ],  20),

            CDateTimeCol( u'Дата и время',  ['date'],  20),
            CRefBookCol(  u'Поставщик',     ['supplier_id'], 'OrgStructure', 15),
            CRefBookCol(  u'Получатель',    ['receiver_id'], 'OrgStructure', 15),
            CTextCol(     u'Примечание',    ['note'],  20),
            ], 'StockMotion' )

#
# ##############################################################################
#

class CRemainingsModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CRBInDocTableCol(u'Подразделение', 'orgStructure_id', 50, 'OrgStructure', showFields = CRBComboBox.showCode))
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields = CRBComboBox.showName))
        self.addCol(CInDocTableCol( u'Партия', 'batch', 16))
        self.addCol(CDateInDocTableCol( u'Годен до', 'shelfTime', 12, canBeEmpty=True))
        self.addCol(CRBInDocTableCol(    u'Тип финансирования', 'finance_id', 15, 'rbFinance'))
        self.addCol(CFloatInDocTableCol( u'Кол-во', 'qnt', 12))
        self.addCol(CFloatInDocTableCol( u'Сумма', 'sum', 12))
        self.addCol(CFloatInDocTableCol( u'Гантированный запас', 'constrainedQnt', 12))
        self.addCol(CFloatInDocTableCol( u'Точка заказа', 'orderQnt', 12))
        self._cachedRow = None
        self._cachedRowColor = None


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def getRowColor(self, row):
        if self._cachedRow != row:
            self._cachedRow = row
            record = self._items[row]
            varQnt = record.value('qnt')
            varConstrainedQnt = record.value('constrainedQnt')
            varOrderQnt = record.value('orderQnt')
            self._cachedRowColor = None
            if not (varConstrainedQnt.isNull() or varOrderQnt.isNull()):
                qnt = forceDouble(varQnt)
                constrainedQnt = forceDouble(varConstrainedQnt)
                orderQnt = forceDouble(varOrderQnt)
                if qnt<constrainedQnt:
                    self._cachedRowColor = QtGui.QColor(QtCore.Qt.darkRed)
                elif qnt<orderQnt:
                    self._cachedRowColor = QtGui.QColor(QtCore.Qt.darkGreen)
        return self._cachedRowColor


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.ForegroundRole:
            row = index.row()
            return toVariant(self.getRowColor(row))
        else:
            return CRecordListModel.data(self, index, role)


    def loadData(self, date, orgStructureId, nomenclatureId,
                 groupByBatch, batch, begShelfTime, endShelfTime,
                 financeId, constrainedQnt, orderQnt):
        self._items = []
        db = QtGui.qApp.db
        table = db.table('StockTrans')
        tableOSS = db.table('OrgStructure_Stock')
        debCond = []
        creCond = []
        ossCond = []
        if date:
            debCond.append(table['date'].lt(date))
            creCond.append(table['date'].lt(date))
        if orgStructureId:
            debCond.append(table['debOrgStructure_id'].eq(orgStructureId))
            creCond.append(table['creOrgStructure_id'].eq(orgStructureId))
            ossCond.append(tableOSS['master_id'].eq(orgStructureId))
        else:
            debCond.append(table['debOrgStructure_id'].isNotNull())
            creCond.append(table['creOrgStructure_id'].isNotNull())
        if nomenclatureId:
            debCond.append(table['debNomenclature_id'].eq(nomenclatureId))
            creCond.append(table['creNomenclature_id'].eq(nomenclatureId))
            ossCond.append(tableOSS['nomenclature_id'].eq(nomenclatureId))

        if groupByBatch:
            batchFields = 'batch, shelfTime,'
            sqlGroupByBatch = 'batch, shelfTime, '
            if batch:
                t = table['batch'].eq(batch)
                debCond.append(t)
                creCond.append(t)
            if begShelfTime:
                t = table['shelfTime'].ge(begShelfTime)
                debCond.append(t)
                creCond.append(t)
            if endShelfTime:
                t = table['shelfTime'].le(endShelfTime)
                debCond.append(t)
                creCond.append(t)
        else:
            batchFields = '\'\' AS batch, NULL AS shelfTime,'
            sqlGroupByBatch = ''
        if financeId:
            debCond.append(table['debFinance_id'].eq(financeId))
            creCond.append(table['creFinance_id'].eq(financeId))
            ossCond.append(tableOSS['finance_id'].eq(financeId))
        havCond = ['(`qnt` != 0 OR `sum` != 0 OR `constrainedQnt` IS NOT NULL)']
        if constrainedQnt:
            havCond.append('`qnt`<`constrainedQnt`')
        if orderQnt:
            havCond.append('`qnt`<`orderQnt`')

        stmt = u'''
SELECT T.orgStructure_id,
       T.nomenclature_id,
       T.batch,
       T.shelfTime,
       T.finance_id,
       sum(T.qnt) AS `qnt`,
       sum(T.`sum`) AS `sum`,
       OrgStructure_Stock.constrainedQnt AS constrainedQnt,
       OrgStructure_Stock.orderQnt AS orderQnt
FROM
    (
    SELECT debOrgStructure_id AS orgStructure_id,
           debNomenclature_id AS nomenclature_id,
           %(batchFields)s
           debFinance_id      AS finance_id,
           sum(qnt)           AS `qnt`,
           sum(`sum`)         AS `sum`
    FROM StockTrans
    WHERE %(debCond)s
    GROUP BY debOrgStructure_id, debNomenclature_id, %(groupByBatch)s debFinance_id
    UNION
    SELECT creOrgStructure_id AS orgStructure_id,
           creNomenclature_id AS nomenclature_id,
           %(batchFields)s
           creFinance_id      AS finance_id,
           -sum(qnt)          AS `qnt`,
           -sum(`sum`)        AS `sum`
    FROM StockTrans
    WHERE %(creCond)s
    GROUP BY creOrgStructure_id, creNomenclature_id, %(groupByBatch)s creFinance_id
    UNION
    SELECT master_id          AS orgStructure_id,
           nomenclature_id    AS nomenclature_id,
           ''                 AS batch,
           NULL               AS shelfTime,
           finance_id         AS finance_id,
           0                  AS `qnt`,
           0                  AS `sum`
    FROM OrgStructure_Stock
    WHERE %(ossCond)s
    GROUP BY master_id, nomenclature_id, finance_id
    ) AS T
    LEFT JOIN OrgStructure ON OrgStructure.id = T.orgStructure_id
    LEFT JOIN rbNomenclature ON rbNomenclature.id = T.nomenclature_id
    LEFT JOIN rbFinance ON rbFinance.id = T.finance_id
    LEFT JOIN OrgStructure_Stock ON OrgStructure_Stock.master_id = T.orgStructure_id
          AND OrgStructure_Stock.nomenclature_id = T.nomenclature_id
          AND OrgStructure_Stock.finance_id = T.finance_id
GROUP BY orgStructure_id, nomenclature_id, %(groupByBatch)s finance_id
HAVING (%(havCond)s)
ORDER BY OrgStructure.code, rbNomenclature.code, rbNomenclature.name, %(groupByBatch)s rbFinance.code
''' % {
        'debCond' : db.joinAnd(debCond) if debCond else '1',
        'creCond' : db.joinAnd(creCond) if creCond else '1',
        'ossCond' : db.joinAnd(ossCond) if ossCond else '1',
        'havCond' : db.joinAnd(havCond),
        'groupByBatch' : sqlGroupByBatch,
        'batchFields'  : batchFields,
      }
        query = db.query(stmt)
        while query.next():
            self._items.append(query.record())
        self.reset()
#
# ##############################################################################
#

class CMyRequisitionsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CDateCol(     u'Дата',          ['date'],  20),
            CDateTimeCol( u'Срок',          ['deadline'], 20),
            CRefBookCol(  u'Поставщик',     ['supplier_id'], 'OrgStructure', 15),
            CTextCol(     u'Примечание',    ['note'],  20),
            ], 'StockRequisition' )


#
# ##############################################################################
#

class CRequisitionsToMeModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CDateCol(     u'Дата',          ['date'],  20),
            CDateTimeCol( u'Срок',          ['deadline'], 20),
            CRefBookCol(  u'Заказчик',      ['recipient_id'], 'OrgStructure', 15),
            CTextCol(     u'Примечание',    ['note'],  20),
            ], 'StockRequisition' )


#
# ##############################################################################
#

class CRequisitionContentModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CRefBookCol(  u'ЛСиИМН',             ['nomenclature_id'], 'rbNomenclature', 50),
            CRefBookCol(  u'Тип финансирования', ['finance_id'],      'rbFinance', 15),
            CTextCol(     u'Кол-во',             ['qnt'],  12),
            CTextCol(     u'Отпущено',           ['satisfiedQnt'],  12),
            ], 'StockRequisition_Item' )
