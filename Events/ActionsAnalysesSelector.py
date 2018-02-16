# -*- coding: utf -*-

from PyQt4 import QtCore, QtGui

from Events.ActionsSelector import CActionTypesSelectionDialog, CActionTypesSelectionManager
from Events.Ui_ActionsAnalysesSelectorDialog import Ui_ActionTypesSelectorDialog as Ui_SelectorDialogAnalyses
from library.MES.Utils import getMesServiceInfo
from library.Utils import forceDouble, forceInt, forceStringEx


class CActionTypesAnalysesSelectionDialog(CActionTypesSelectionDialog, Ui_SelectorDialogAnalyses):
    def __init__(self, parent):
        CActionTypesSelectionDialog.__init__(self, parent)
        self.disabledActionTypeIdList = None

        self.connect(self.treeActionTypeGroups, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_treeActionTypeGroups_doubleClicked)
        self.connect(self.selectionModelSelectedActionTypes, QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'), self.on_selectionModelSelectedActionTypes_currentChanged)

    def setSelected(self, actionTypeId, value, resetMainModel=False):
        if not actionTypeId: assert u'В ActionAnalysesSelector.CActionTypesAnalysesSelectionDialog.setSelected actionTypeId не пришел :('

        selected = self.isSelected(actionTypeId)
        if value:
            if not selected:
                self.addSelectionAnalyses(actionTypeId, resetMainModel)
                return True
        else:
            if selected:
                self.removeSelectionAnalyses(actionTypeId, resetMainModel)
                return True
        return False

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionTypeGroups_currentChanged(self, current, previous):
        if current.isValid() and current.internalPointer():
            treeItem = current.internalPointer()
            actionTypeId = treeItem.id()
            _class = treeItem.class_()
            if not treeItem.items():  # node is a leaf
                _id = treeItem.id()
                if _id and _id in self.mesActionTypes:
                    record = getMesServiceInfo(treeItem.code(), self.mesId, self.getNecessityFilter())
                    if record:
                        averageQnt = forceInt(record.value('averageQnt'))
                        necessity = forceDouble(record.value('necessity'))
                        doctorWTU = forceDouble(record.value('doctorWTU'))
                        paramedicalWTU = forceDouble(record.value('paramedicalWTU'))
                        text = u'СК: %d; ЧП: %.1f; УЕТвр: %.1f; УЕТср: %.1f' % (averageQnt, necessity, doctorWTU, paramedicalWTU)
                        self.lblMesInfo.setText(text)
                        return
            self.lblMesInfo.clear()
        else:
            actionTypeId = None
            _class = None
        self.setGroupId(actionTypeId, _class)
        text = forceStringEx(self.edtFindByCode.text())
        if text:
            self.on_edtFindByCode_textChanged(text)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelSelectedActionTypes_currentChanged(self, current, previous):
        pass

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_treeActionTypeGroups_doubleClicked(self, index):
        item = index.internalPointer()
        itemId = item.id()
        self.setSelected(itemId, True)


def selectActionTypesAnalyses(parent, actionTypeClasses=None, clientSex=None, clientAge=None, orgStructureId=None, eventTypeId=None,
                              contractId=None, mesId=None, chkContractByFinanceId=None, eventId=None, existsActionTypesList=None,
                              contractTariffCache=None, eventEditorOwner=None, notFilteredActionTypesClasses=None,
                              defaultFinanceId=None, defaultContractFilterPart=None, showAmountFromMes=None, eventBegDate=None,
                              eventEndDate=QtCore.QDate(), showMedicaments=False, isQuietAddingByMes=False, paymentScheme=None,
                              MKB=None, chosenActionTypes=None, returnDirtyRows=False):
    if not actionTypeClasses:
        actionTypeClasses = []
    if not existsActionTypesList:
        existsActionTypesList = []
    if not notFilteredActionTypesClasses:
        notFilteredActionTypesClasses = []
    if not chosenActionTypes:
        chosenActionTypes = {}
    QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    dlg = CActionTypesAnalysesSelectionDialog(parent)
    dlg.setPreviousActionTypeIds(chosenActionTypes)
    dlg.setBlockSignals(True)
    dlg.setExistsActionTypes(existsActionTypesList)
    dlg.setOrgStructurePriority(eventTypeId)
    if hasattr(parent, 'cmbPerson'):
        dlg.setExecPerson(parent.cmbPerson.value())
    dlg.setMesId(mesId)
    dlg.setShowAmount(showAmountFromMes)
    dlg.setShowMedicaments(showMedicaments)
    dlg.setActionTypeClasses(actionTypeClasses)
    dlg.setSexAndAge(clientSex, clientAge)
    dlg.setEventId(eventId)
    dlg.setSpecialityId()
    dlg.setEventTypeId(eventTypeId)
    dlg.setDefaultFinanceId(defaultFinanceId)
    dlg.setDefaultContractFilterPart(defaultContractFilterPart)
    dlg.setOrgStructureId(orgStructureId)
    dlg.setContractId(contractId, chkContractByFinanceId)
    dlg.updateSelectedCount()
    dlg.setContractTariffCache(contractTariffCache)
    dlg.setBegDate(eventBegDate)
    dlg.setEndDate(eventEndDate)
    dlg.setClientId()
    dlg.setNotFilteredClasses(notFilteredActionTypesClasses)
    dlg.setMKB(MKB)
    dlg.setBlockSignals(False)
    dlg.setEventEditorOwner(eventEditorOwner)
    dlg.setPaymentScheme(paymentScheme)
    QtGui.qApp.restoreOverrideCursor()

    if isQuietAddingByMes:
        dlg.updateTreeData()
        dlg.chkNecessity.setChecked(True)
        dlg.edtNecessity.setValue(1.00)
        dlg.on_bntSelectAll_pressed()

    if isQuietAddingByMes or dlg.exec_():
        result = dlg.getSelectedList(returnDirtyRows)
    else:
        result = []

    return result
