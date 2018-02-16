# -*- coding: utf-8 -*-

import re
from PyQt4 import QtCore, QtGui

from Events.ActionTypeComboBox import CActionTypeTableCol
from KLADR.KLADRModel import getCityName, getStreetName
from KLADR.kladrComboxes import CKLADRComboBox, CStreetComboBox
from Orgs.EquipmentComboBox import CEquipmentComboBox
from Orgs.Orgs import selectOrganisation
from Orgs.Utils import COrgStructureAreaInfo
from RefBooks.InvoluteBedsModel import CHospitalBedsModel, CInvoluteBedsModel
from RefBooks.Tables import rbNet
from Registry.Utils import getHouseId
from Resources.JobTypeComboBox import CJobTypeInDocTableCol
from Stock.NomenclatureComboBox import CNomenclatureInDocTableCol
from Ui_OrgStructureEditor import Ui_ItemEditorDialog
from Ui_OrgStructureEditor_AddAddressesDialog import Ui_AddAddressesDialog
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.InDocTable import CBoolInDocTableCol, CDateInDocTableCol, CEnumInDocTableCol, CFloatInDocTableCol, CInDocTableModel, CIntInDocTableCol, CRBInDocTableCol, CTimeInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog, CItemEditorDialog
from library.TableModel import CDesignationCol, CTableModel, CTextCol
from library.TreeModel import CDragDropDBTreeModel
from library.Utils import forceDouble, forceInt, forceRef, forceString, forceStringEx, naturalStringCompare, toVariant, variantEq
from library.crbcombobox import CRBComboBox
from library.interchange import getCheckBoxValue, getComboBoxValue, getLineEditValue, getRBComboBoxValue, getSpinBoxValue, setCheckBoxValue, setComboBoxValue, setLineEditValue, setRBComboBoxValue, setWidgetValue, getWidgetValue
from library.Enum import CEnum


class OrgStructureType(CEnum):
    u""" Тип подразделения (OrgStructure.type) """
    Ambulatory = 0
    Stationary = 1
    Emergency = 2
    Mobile = 3
    AdmissionDepartment = 4
    Reanimation = 5
    Pharmacy = 6
    DayStationary = 7
    DaytimeHospital = 8
    Stock = 99

    nameMap = {
        Ambulatory         : u'Амбулатория',
        Stationary         : u'Стационар',
        Emergency          : u'Скорая помощь',
        Mobile             : u'Мобильная станция',
        AdmissionDepartment: u'Приемное отделение стационара',
        Reanimation        : u'Реанимация',
        Pharmacy           : u'Аптека',
        DayStationary      : u'Дневной стационар',
        DaytimeHospital    : u'Стационар дневного пребывания',
        Stock              : u'Склад'
    }


class COrgStructureList(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CDesignationCol(u'ЛПУ', ['organisation_id'], ('Organisation', 'infisCode'), 5),
            CTextCol(u'Код', ['code'], 40),
            CTextCol(u'Наименование', ['name'], 40),
        ], 'OrgStructure', ['organisation_id', 'parent_id', 'code', 'name'])
        self.setWindowTitleEx(u'Структура ЛПУ')
        self.expandedItemsState = {}

    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('Tree', CDragDropDBTreeModel(self, self.tableName, 'id', 'parent_id', 'code', self.order))
        self.addModels('Table', CTableModel(self, self.cols, self.tableName))
        self.modelTree.setLeavesVisible(True)
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')

    def postSetupUi(self):
        self.setModels(self.treeItems, self.modelTree, self.selectionModelTree)
        self.setModels(self.tblItems, self.modelTable, self.selectionModelTable)
        self.treeItems.header().hide()
        idList = self.select(self.props)
        self.modelTable.setIdList(idList)
        self.tblItems.selectRow(0)
        self.btnSelect.setEnabled(self.forSelect)
        self.btnSelect.setVisible(self.forSelect)
        self.btnSelect.setDefault(self.forSelect)
        self.btnFilter.setEnabled(bool(self.filterClass))
        self.btnFilter.setVisible(bool(self.filterClass))
        self.btnFind.setEnabled(bool(self.findClass))
        self.btnFind.setVisible(bool(self.findClass))
        self.btnEdit.setDefault(not self.forSelect)
        self.tblItems.addPopupDelRow()
        self.tblItems.setFocus(QtCore.Qt.OtherFocusReason)

        self.treeItems.dragEnabled()
        self.treeItems.acceptDrops()
        self.treeItems.showDropIndicator()
        self.treeItems.setDragDropMode(QtGui.QAbstractItemView.InternalMove)

        self.treeItems.createPopupMenu([self.actDelete])
        self.connect(self.treeItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        self.connect(self.modelTree, QtCore.SIGNAL('saveExpandedState()'), self.saveExpandedState)
        self.connect(self.modelTree, QtCore.SIGNAL('restoreExpandedState()'), self.restoreExpandedState)

    def popupMenuAboutToShow(self):
        currentItemId = self.currentTreeItemId()
        self.actDelete.setEnabled(bool(currentItemId))

    def currentTreeItemId(self):
        idx = self.treeItems.currentIndex()
        if idx.isValid():
            return self.modelTree.itemId(idx)

        return None

    def select(self, props):
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        return QtGui.qApp.db.getIdList(table.name(), 'id', table['parent_id'].eq(groupId), self.order)

    def currentGroupId(self):
        return self.modelTree.itemId(self.treeItems.currentIndex())

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        dialog.setGroupId(self.currentGroupId())
        if dialog.exec_():
            itemId = dialog.itemId()
            self.modelTree.update()
            self.renewListAndSetTo(itemId)\

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dialog = self.getItemEditor()
            dialog.load(itemId)
            if dialog.exec_():
                itemId = dialog.itemId()
                self.modelTree.update()
                self.renewListAndSetTo(itemId)
        else:
            self.on_btnNew_clicked()

    def getItemEditor(self):
        return COrgStructureEditor(self)

    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        def deleteCurrentInternal(item):
            if item:
                children = item.items()
                if children:
                    for x in children:
                        deleteCurrentInternal(x)

                db = QtGui.qApp.db
                table = db.table('OrgStructure')
                db.deleteRecord(table, table['id'].eq(item.id()))

        if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                    u'Удалить элемент и все его дочерние элементы?',
                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No
                                    ) == QtGui.QMessageBox.Yes:
            currentIndex = self.treeItems.currentIndex()
            idx = self.modelTree.parent(currentIndex)
            self.saveExpandedState()
            rc = QtGui.qApp.call(self, deleteCurrentInternal,
                (currentIndex.internalPointer(), ))[0]
            if rc:
                self.modelTree.reset()
                self.modelTree.update()
                self.renewListAndSetTo()
                self.restoreExpandedState()
                self.treeItems.setCurrentIndex(idx)


class COrgStructureEditor(CItemEditorDialog, Ui_ItemEditorDialog):
    setupUi = Ui_ItemEditorDialog.setupUi
    retranslateUi = Ui_ItemEditorDialog.retranslateUi

    def __init__(self, parent):
        CItemEditorDialog.__init__(self, parent, 'OrgStructure')
        self.setWindowTitleEx(u'Подразделение')
        self.on_cmbIsArea_currentIndexChanged(0)
        self.on_chkHasHospitalBeds_toggled(False)
        self.on_chkHasStocks_toggled(False)
        self.cmbParent.setNameField('name')
        self.cmbParent.setAddNone(True)
        self.cmbParent.setFilter('False')
        self.cmbParent.setTable('OrgStructure')
        self.cmbOrganisation.setValue(QtGui.qApp.currentOrgId())
        self.cmbNet.setTable(rbNet, True)
        self.cmbChief.setSpecialityPresent(True)
        self.cmbHeadNurse.setSpecialityPresent(None)
        self.KLADRDelegate = CKLADRItemDelegate(self)
        self.StreetDelegate = CStreetItemDelegate(self)
        self.tblAddress.setItemDelegateForColumn(0, self.KLADRDelegate)
        self.tblAddress.setItemDelegateForColumn(1, self.StreetDelegate)
        self.tblAddress.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.addModels('Address', CAddressModel(self))
        self.addModels('HospitalBeds', CHospitalBedsModel(self))
        self.addModels('InvoluteBeds', CInvoluteBedsModel(self))
        self.modelHospitalBeds.setInvoluteBedsModel(self.modelInvoluteBeds)
        self.addModels('Jobs', CJobsModel(self))
        self.addModels('Gaps', CGapsModel(self))
        self.addModels('EventTypes', CEventTypesModel(self))
        self.addModels('ActionTypes', CActionTypesModel(self))
        self.addModels('DisabledAttendance', CDisabledAttendanceModel(self))
        self.addModels('Stocks', CStocksModel(self))
        self.addModels('Equipments', CEquipmentsModel(self))
        self.setModels(self.tblAddress, self.modelAddress, self.selectionModelAddress)
        self.setModels(self.tblHospitalBeds, self.modelHospitalBeds, self.selectionModelHospitalBeds)
        self.setModels(self.tblInvoluteBeds, self.modelInvoluteBeds, self.selectionModelInvoluteBeds)
        self.setModels(self.tblJobs, self.modelJobs, self.selectionModelJobs)
        self.setModels(self.tblGaps, self.modelGaps, self.selectionModelGaps)
        self.setModels(self.tblEventTypes, self.modelEventTypes, self.selectionModelEventTypes)
        self.setModels(self.tblActionTypes, self.modelActionTypes, self.selectionModelActionTypes)
        self.setModels(self.tblDisabledAttendance, self.modelDisabledAttendance, self.selectionModelDisabledAttendance)
        self.setModels(self.tblStocks, self.modelStocks, self.selectionModelStocks)
        self.setModels(self.tblEquipments, self.modelEquipments, self.selectionModelEquipments)

        self.actAddEmpty = QtGui.QAction(u'Вставить пустую запись', self)

        self.actAddEmpty.setObjectName('actAddEmpty')
        self.actDuplicate = QtGui.QAction(u'Дублировать', self)
        self.actDuplicate.setObjectName('actDuplicate')
        self.actUp = QtGui.QAction(u'Поднять строку', self)
        self.actUp.setObjectName('actUp')
        self.actDown = QtGui.QAction(u'Опустить строку', self)
        self.actDown.setObjectName('actDown')
        self.actGetParentDisabledAttendance = QtGui.QAction(u'Копировать ограничения из вышестоящего подразделения', self)
        self.actGetParentDisabledAttendance.setObjectName('actGetParentDisabledAttendance')
        self.actDelRows = QtGui.QAction(u'Удалить выделенные строки', self)
        self.actDelRows.setObjectName('actDelRows')
        self.tblAddress.createPopupMenu([self.actAddEmpty, self.actDuplicate, '-', self.actUp, self.actDown, '-', self.actDelRows])
        self.tblDisabledAttendance.createPopupMenu([self.actGetParentDisabledAttendance, '-'])

        for tbl in [self.tblHospitalBeds, self.tblInvoluteBeds, self.tblJobs,
                    self.tblGaps, self.tblEventTypes,
                    self.tblActionTypes, self.tblDisabledAttendance,
                    self.tblStocks, self.tblEquipments]:
            tbl.addMoveRow()
            tbl.addPopupSeparator()
            tbl.addPopupDuplicateCurrentRow()
            tbl.addPopupSeparator()
            tbl.addPopupDelRow()

        self.cmbType.setEnum(OrgStructureType)
        self.cmbIsArea.setEnum(COrgStructureAreaInfo)

        self.cmbParent.setNameField('name')
        self.cmbParent.setAddNone(True)
        self.cmbParent.setTable('OrgStructure')
        self.cmbOrganisation.setValue(QtGui.qApp.currentOrgId())
        self.cmbNet.setTable(rbNet, True)
        self.cmbChief.setSpecialityPresent(True)
        self.cmbHeadNurse.setSpecialityPresent(None)
        self.KLADRDelegate = CKLADRItemDelegate(self)
        self.StreetDelegate = CStreetItemDelegate(self)
        self.tblAddress.setItemDelegateForColumn(0, self.KLADRDelegate)
        self.tblAddress.setItemDelegateForColumn(1, self.StreetDelegate)
        self.on_cmbIsArea_currentIndexChanged(0)
        self.on_chkHasHospitalBeds_toggled(False)
        self.on_chkHasStocks_toggled(False)
        self.cmbFilterAddressStreet.setCity(QtGui.qApp.defaultKLADR())
        self.connect(self.tblAddress.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAddressAboutToShow)
        self.connect(self.actAddEmpty, QtCore.SIGNAL('triggered()'), self.addEmptyAddress)
        self.connect(self.actDuplicate, QtCore.SIGNAL('triggered()'), self.duplicateAddress)
        self.connect(self.actUp, QtCore.SIGNAL('triggered()'), self.upAddress)
        self.connect(self.actDown, QtCore.SIGNAL('triggered()'), self.downAddress)
        self.connect(self.actGetParentDisabledAttendance, QtCore.SIGNAL('triggered()'), self.getParentDisabledAttendance)
        self.connect(self.actDelRows, QtCore.SIGNAL('triggered()'), self.tblAddress.removeSelectedRows)
        self.connect(self.selectionModelHospitalBeds, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex)'), self.changedInvoluteBeds)

        # self.edtSalaryPercentage.textChanged.connect(self.on_edtSalaryPercentage_textChanged)
        self._salaryPercentageRegExp = '^\d+(\.\d+)?$'  # '^\-$|\d+(\.\d+)?$'

        self.cmbMiacHead.setVisible(QtGui.qApp.checkGlobalPreference('53', u'да'))
        self.lblMiacHead.setVisible(QtGui.qApp.checkGlobalPreference('53', u'да'))
        self.lblMiacCode.setVisible(QtGui.qApp.region() == '78')
        self.edtMiacCode.setVisible(QtGui.qApp.region() == '78')

    def on_edtSalaryPercentage_textChanged(self, text):
        result = re.search(self._salaryPercentageRegExp, self.edtSalaryPercentage.text())
        if result:
            if forceDouble(result.group(0)) > 100.0:
                self.edtSalaryPercentage.setText('100')
        if len(self.edtSalaryPercentage.text()) == 0:
            self.edtSalaryPercentage.setText('0')

    def checkSalaryPercentage(self):
        result = re.search(self._salaryPercentageRegExp, self.edtSalaryPercentage.text())
        if result:
            return True
        else:
            QtGui.QMessageBox.warning(
                self,
                u'Внимание!',
                u'%s введен некорректно' % self.lblSalaryPercentage.text(),
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )
            return False

    def changedInvoluteBeds(self, current, previous):
        row = current.row()
        involuteBeds = self.modelHospitalBeds.involuteBeds(row)
        self.modelInvoluteBeds.setItems(involuteBeds)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setRBComboBoxValue(self.cmbOrganisation, record, 'organisation_id')
        setRBComboBoxValue(self.cmbParent, record, 'parent_id')
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtAddress, record, 'address')
        setWidgetValue(self.cmbType, record, 'type', forceInt)
        setRBComboBoxValue(self.cmbNet, record, 'net_id')
        setRBComboBoxValue(self.cmbChief, record, 'chief_id')
        setRBComboBoxValue(self.cmbHeadNurse, record, 'headNurse_id')
        setLineEditValue(self.edtInfisCode, record, 'infisCode')
        setLineEditValue(self.edtAttachCode, record, 'attachCode')
        setLineEditValue(self.edtBookkeeperCode, record, 'bookkeeperCode')
        setLineEditValue(self.edtInfisInternalCode, record, 'infisInternalCode')
        setLineEditValue(self.edtInfisDepTypeCode, record, 'infisDepTypeCode')
        setLineEditValue(self.edtInfisTariffCode, record, 'infisTariffCode')
        setLineEditValue(self.edtStorageCode, record, 'storageCode')
        setLineEditValue(self.edtDayLimit, record, 'dayLimit')
        setLineEditValue(self.edtSyncGUID, record, 'syncGUID')
        setLineEditValue(self.edtMiacCode, record, 'miacCode')

        self.edtSalaryPercentage.setValue(forceDouble(record.value('salaryPercentage')))
        self.edtQuota.setValue(forceInt(record.value('quota')))
        # if len(self.edtSalaryPercentage.value()) == 0:
        #    self.edtSalaryPercentage.setText('0')

        setComboBoxValue(self.cmbIsArea, record, 'isArea')
        setRBComboBoxValue(self.cmbMiacHead, record, 'miacHead_id')
        setCheckBoxValue(self.chkHasHospitalBeds, record, 'hasHospitalBeds')
        setCheckBoxValue(self.chkHasStocks, record, 'hasStocks')
        setCheckBoxValue(self.chkHasDS, record, 'hasDayStationary')
        setCheckBoxValue(self.chkAvailableForExternal, record, 'availableForExternal')
        setCheckBoxValue(self.chkInheritEventTypes, record, 'inheritEventTypes')
        setCheckBoxValue(self.chkInheritGaps, record, 'inheritGaps')
        setCheckBoxValue(self.chkInheritActionTypes, record, 'inheritActionTypes')
        setCheckBoxValue(self.chkVisibleInDR, record, 'isVisibleInDR')
        self.modelAddress.loadData(self.itemId())
        self.modelHospitalBeds.loadItems(self.itemId())
        self.modelJobs.loadItems(self.itemId())
        self.modelGaps.loadItems(self.itemId())
        self.modelEventTypes.loadItems(self.itemId())
        self.modelActionTypes.loadItems(self.itemId())
        self.modelDisabledAttendance.loadItems(self.itemId())
        self.modelStocks.loadItems(self.itemId())
        self.modelEquipments.loadItems(self.itemId())
        self.cmbChief.setOrgStructureId(self.itemId())
        self.cmbHeadNurse.setOrgStructureId(self.itemId())

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getRBComboBoxValue(self.cmbOrganisation, record, 'organisation_id')
        getRBComboBoxValue(self.cmbParent, record, 'parent_id')
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getLineEditValue(self.edtAddress, record, 'address')
        getWidgetValue(self.cmbType, record, 'type')
        getRBComboBoxValue(self.cmbNet, record, 'net_id')
        getRBComboBoxValue(self.cmbChief, record, 'chief_id')
        getRBComboBoxValue(self.cmbHeadNurse, record, 'headNurse_id')
        getLineEditValue(self.edtInfisCode, record, 'infisCode')
        getLineEditValue(self.edtAttachCode, record, 'attachCode')
        getLineEditValue(self.edtBookkeeperCode, record, 'bookkeeperCode')
        getLineEditValue(self.edtInfisInternalCode, record, 'infisInternalCode')
        getLineEditValue(self.edtInfisDepTypeCode, record, 'infisDepTypeCode')
        getLineEditValue(self.edtInfisTariffCode, record, 'infisTariffCode')
        getLineEditValue(self.edtDayLimit, record, 'dayLimit')
        getLineEditValue(self.edtStorageCode, record, 'storageCode')
        getLineEditValue(self.edtSyncGUID, record, 'syncGUID')
        getLineEditValue(self.edtMiacCode, record, 'miacCode')

        getSpinBoxValue(self.edtSalaryPercentage, record, 'salaryPercentage')
        getSpinBoxValue(self.edtQuota, record, 'quota')

        getComboBoxValue(self.cmbIsArea, record, 'isArea')
        if self.cmbMiacHead.isEnabled():
            getRBComboBoxValue(self.cmbMiacHead, record, 'miacHead_id')
        else:
            record.setValue('miacHead_id', toVariant(None))
        getCheckBoxValue(self.chkHasHospitalBeds, record, 'hasHospitalBeds')
        getCheckBoxValue(self.chkHasStocks, record, 'hasStocks')
        getCheckBoxValue(self.chkHasDS, record, 'hasDayStationary')
        getCheckBoxValue(self.chkAvailableForExternal, record, 'availableForExternal')
        getCheckBoxValue(self.chkInheritEventTypes, record, 'inheritEventTypes')
        getCheckBoxValue(self.chkInheritGaps, record, 'inheritGaps')
        getCheckBoxValue(self.chkInheritActionTypes, record, 'inheritActionTypes')
        getCheckBoxValue(self.chkVisibleInDR, record, 'isVisibleInDR')
        return record

    def saveInternals(self, id):
        self.modelAddress.saveData(id)
        self.modelHospitalBeds.saveItems(id)
        self.modelJobs.saveItems(id)
        self.modelGaps.saveItems(id)
        self.modelEventTypes.saveItems(id)
        self.modelActionTypes.saveItems(id)
        self.modelDisabledAttendance.saveItems(id)
        self.modelStocks.saveItems(id)
        self.modelEquipments.saveItems(id)

    def checkDataEntered(self):
        return self.checkDisabledAttendance() & self.checkMiacHead()  # & self.checkSalaryPercentage()

    def checkMiacHead(self):
        if not QtGui.qApp.checkGlobalPreference('53', u'да'):
            return True
        if not self.cmbMiacHead.isEnabled():
            return True
        db = QtGui.qApp.db
        if (not self.cmbMiacHead.value()) or db.getRecordEx('OrgStructure', 'id', where="id = '%s' and bookkeeperCode" % forceString(self.cmbMiacHead.value())):
            return True
        QtGui.QMessageBox.warning(self,
                                  u'Внимание!',
                                  u'В поле "Участок относится к" указано недопустимое значение',
                                  QtGui.QMessageBox.Ok,
                                  QtGui.QMessageBox.Ok)
        self.setFocusToWidget(self.cmbMiacHead)
        return False

    def checkDisabledAttendance(self):
        attachTypeIdList = []
        for row, record in enumerate(self.modelDisabledAttendance.items()):
            attachTypeId = forceRef(record.value('attachType_id'))
            if attachTypeId not in attachTypeIdList:
                attachTypeIdList.append(attachTypeId)
            else:
                QtGui.QMessageBox.warning(self,
                                          u'Внимание!',
                                          u'Тип прикрепления повторяется!',
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.Ok)
                self.setFocusToWidget(self.tblDisabledAttendance, row, record.indexOf('attachType_id'))
                return False
        return True

    def setGroupId(self, id):
        if id:
            orgId = forceRef(QtGui.qApp.db.translate('OrgStructure', 'id', id, 'organisation_id'))
            self.groupId = id
            self.cmbOrganisation.setValue(orgId)
            self.cmbParent.setValue(forceRef(id))

    @QtCore.pyqtSlot()
    def on_btnFilterApply_clicked(self):
        if not self.cmbFilterAddressStreet.code():
            QtGui.QMessageBox.information(None, u"Улица", u"Не выбрана улица")
            return
        houses = self.edtFilterAdressHouse.text().split('-')
        housesList = []
        if len(houses) > 1:
            housesList = range(forceInt(houses[0]), forceInt(houses[1]) + 1)
        else:
            housesList.append(forceInt(houses[0]))
        self.modelAddress.filterApply(forceInt(self.cmbFilterAddressStreet.code()), housesList,
                                      forceInt(self.edtFilterCorp.text()), forceInt(self.edtFilterFirstKv.text()),
                                      forceInt(self.edtFilterLastKv.text()))

    @QtCore.pyqtSlot(int)
    def on_cmbOrganisation_currentIndexChanged(self, index):
        orgId = self.cmbOrganisation.value()
        if orgId:
            self.cmbParent.setEnabled(False)
            self.cmbParent.setFilter('organisation_id=%d' % orgId)
        else:
            self.cmbParent.setEnabled(False)
            self.cmbParent.setFilter('organisation_id IS NULL')

    @QtCore.pyqtSlot()
    def on_btnSelectOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbOrganisation.value(), False)
        self.cmbOrganisation.update()
        if orgId:
            self.cmbOrganisation.setValue(orgId)

    @QtCore.pyqtSlot(int)
    def on_cmbIsArea_currentIndexChanged(self, index):
        self.tabWidget.setTabEnabled(1, bool(index > 0))
        self.tblAddress.setEnabled(bool(index > 0))
        miacHeadEnabled = bool(index in [COrgStructureAreaInfo.GeneralPractice, COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic])
        self.cmbMiacHead.setEnabled(miacHeadEnabled)
        self.lblMiacHead.setEnabled(miacHeadEnabled)

    @QtCore.pyqtSlot(bool)
    def on_chkHasHospitalBeds_toggled(self, checked):
        self.tabWidget.setTabEnabled(2, checked)
        self.tblHospitalBeds.setEnabled(checked)
        self.tblInvoluteBeds.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkHasStocks_toggled(self, checked):
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tabStocks), checked)
        self.tblStocks.setEnabled(checked)

    def popupMenuAddressAboutToShow(self):
        row = self.tblAddress.currentIndex().row()
        rows = len(self.modelAddress.items)

        self.actAddEmpty.setEnabled(rows > 0 and row >= 0)
        self.actDuplicate.setEnabled(rows > 0 and row >= 0)
        self.actUp.setEnabled(rows > 0 and row > 0)
        self.actDown.setEnabled(rows > 0 and row >= 0 and row < rows - 1)

    def addEmptyAddress(self):
        row = self.tblAddress.currentIndex().row()
        if row >= 0:
            self.modelAddress.addEmptyRow(row)

    def duplicateAddress(self):
        currentIndex = self.tblAddress.currentIndex()
        row = currentIndex.row()
        if row >= 0:
            self.modelAddress.duplicateRow(row)
            self.tblAddress.setCurrentIndex(currentIndex.sibling(row + 1, currentIndex.column()))

    def upAddress(self):
        currentIndex = self.tblAddress.currentIndex()
        row = currentIndex.row()
        if row >= 1:
            self.modelAddress.upRow(row)
            self.tblAddress.setCurrentIndex(currentIndex.sibling(row - 1, currentIndex.column()))

    def downAddress(self):
        currentIndex = self.tblAddress.currentIndex()
        row = currentIndex.row()
        if row >= 0:
            self.modelAddress.downRow(row)
            self.tblAddress.setCurrentIndex(currentIndex.sibling(row + 1, currentIndex.column()))

    def getParentDisabledAttendance(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            orgStructureId = self.itemId()
            if orgStructureId:
                db = QtGui.qApp.db
                tableOrgStructure = db.table('OrgStructure')
                tableOSDA = db.table('OrgStructure_DisabledAttendance')
                recordParentId = db.getRecordEx(tableOrgStructure, [tableOrgStructure['parent_id']], [tableOrgStructure['deleted'].eq(0), tableOrgStructure['id'].eq(orgStructureId)])
                if recordParentId:
                    parentId = forceRef(recordParentId.value('parent_id'))
                    if parentId:
                        attachTypeIdList = []
                        for row, recordItem in enumerate(self.modelDisabledAttendance.items()):
                            attachTypeId = forceRef(recordItem.value('attachType_id'))
                            if attachTypeId not in attachTypeIdList:
                                attachTypeIdList.append(attachTypeId)
                        records = db.getRecordList(tableOSDA, '*', [tableOSDA['master_id'].eq(parentId)])
                        for record in records:
                            attachTypeId = forceRef(record.value('attachType_id'))
                            if attachTypeId and (attachTypeId not in attachTypeIdList):
                                orgStructureId = forceRef(record.value('master_id'))
                                disabledType = forceInt(record.value('disabledType'))
                                self.addRowDisabledAttendance(orgStructureId, attachTypeId, disabledType)
        finally:
            QtGui.qApp.restoreOverrideCursor()

    def addRowDisabledAttendance(self, orgStructureId, attachTypeId, disabledType):
        newRecord = QtGui.qApp.db.table('OrgStructure_DisabledAttendance').newRecord()
        newRecord.setValue('master_id', QtCore.QVariant(orgStructureId))
        newRecord.setValue('attachType_id', QtCore.QVariant(attachTypeId))
        newRecord.setValue('disabledType', QtCore.QVariant(disabledType))
        self.modelDisabledAttendance.items().append(newRecord)
        index = QtCore.QModelIndex()
        cnt = len(self.modelDisabledAttendance.items())
        self.modelDisabledAttendance.beginInsertRows(index, cnt, cnt)
        self.modelDisabledAttendance.insertRows(cnt, 1, index)
        self.modelDisabledAttendance.endInsertRows()

    @QtCore.pyqtSlot()
    def on_btnAddAddresses_clicked(self):
        dlg = CAddAddressesDialog(self)
        if dlg.exec_():
            numbersType = dlg.cmbNumbers.currentIndex()
            newAddresses = []
            for houseNumber in range(dlg.edtHouseFrom.value(), dlg.edtHouseTo.value() + 1):
                if numbersType == 0 or numbersType == 1 and houseNumber % 2 == 1 or numbersType == 2 and houseNumber % 2 == 0:
                    newAddresses.append([
                        dlg.cmbCity.code(),
                        dlg.cmbStreet.code(),
                        str(houseNumber),
                        '',
                        dlg.edtFlatFrom.value(),
                        dlg.edtFlatTo.value()
                    ])
            if newAddresses:
                rows = len(self.modelAddress.items)
                self.modelAddress.beginInsertRows(QtCore.QModelIndex(), rows, rows + len(newAddresses) - 1)
                self.modelAddress.items.extend(newAddresses)
                self.modelAddress.endInsertRows()


class CAddAddressesDialog(QtGui.QDialog, Ui_AddAddressesDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbCity.setCode(QtGui.qApp.defaultKLADR())

    @QtCore.pyqtSlot(int)
    def on_cmbCity_currentIndexChanged(self, index):
        code = self.cmbCity.code()
        self.cmbStreet.setCity(code)

    def accept(self):
        if not self.cmbCity.code():
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Не выбран населенный пункт.',
                QtGui.QMessageBox.Ok
            )
            return
        if not self.cmbStreet.code():
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Не выбрана улица.',
                QtGui.QMessageBox.Ok
            )
            return
        QtGui.QDialog.accept(self)


class CAddressModel(QtCore.QAbstractTableModel):
    headers = [u'город', u'улица', u'дом', u'корпус', u'первая кв.', u'последняя кв.']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.itemsWithoutFilter = []
        self.isFilter = False

    def columnCount(self, index=QtCore.QModelIndex()):
        return 6

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items) + 1

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def confirmRemoveRow(self, view, row, multiple=False):
        return True

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(CAddressModel.headers[section])
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if row < len(self.items):
            if role == QtCore.Qt.EditRole:
                return toVariant(self.items[row][column])

            if role == QtCore.Qt.DisplayRole:
                if column == 0:
                    code = self.items[row][column]
                    return toVariant(getCityName(code) if code else None)
                if column == 1:
                    code = self.items[row][column]
                    return toVariant(getStreetName(code) if code else None)
                else:
                    return toVariant(self.items[row][column])
        elif row == len(self.items):
            if role == QtCore.Qt.EditRole:
                if column == 0:
                    return toVariant('7800000000000')
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if row == len(self.items):
                if value.isNull():
                    return False
                self.items.append(self.getEmptyItem())
                itemsCnt = len(self.items)
                index = QtCore.QModelIndex()
                self.beginInsertRows(index, itemsCnt, itemsCnt)
                self.insertRows(itemsCnt, 1, index)
                self.endInsertRows()
            item = self.items[row]
            if column in [0, 1, 3]:
                itemValue = forceStringEx(value)
            elif column == 2:
                itemValue = forceStringEx(value)
                ranges = re.findall(r'^(\d+)-(\d+)$', forceStringEx(itemValue))
                if ranges:
                    startHouse = int(ranges[0][0])
                    endHouse = int(ranges[0][1])
                    if 0 < endHouse - startHouse < 100:
                        for house in xrange(startHouse, endHouse):
                            item[column] = forceStringEx(house)
                            self.duplicateRow(row + house - startHouse)
                        item[column] = forceStringEx(endHouse)
                        self.emitCellChanged(row, column)
                        return True
            else:
                itemValue = forceInt(value)
            if item[column] != itemValue:
                item[column] = itemValue
                self.emitCellChanged(row, column)
                if column == 0:
                    item[1] = ''
                    self.emitCellChanged(row, 1)
                return True
        return False

    def getEmptyItem(self):
        return ['', '', '', '', 0, 0]

    def filterApply(self, street, houseNum, houseCorp, firstFlat, lastFlat):
        i = 0
        houses = []
        filterResult = {}

        if houseNum[0] == 0:
            for k in self.getItemsList():
                if forceInt(street) == forceInt(k[1]):
                    filterResult[i] = k
                    i += 1
        elif len(houseNum) == 1:
            for k in self.getItemsList():
                c = 0
                filterList = [street, houseNum, houseCorp, firstFlat, lastFlat]
                for f in filterList:
                    c += 1
                    if f == 0 or None:
                        filterList[c - 1] = k[c]

                if forceInt(filterList[0]) == forceInt(k[1]) and forceInt(houseNum[0]) == forceInt(k[2]) and \
                                forceInt(filterList[2]) == forceInt(k[3]) and forceInt(filterList[3]) == forceInt(k[4]) and \
                                forceInt(filterList[4]) == forceInt(k[5]):
                    filterResult[i] = k
                    i += 1
        elif len(houseNum) > 1:
            for k in self.getItemsList():
                for h in houseNum:
                    if street == forceInt(k[1]) and h == forceInt(k[2]):
                        houses.append(k)
            for k in houses:
                c = 0
                filterList = [houseCorp, firstFlat, lastFlat]
                for f in filterList:
                    c += 1
                    if f == 0 or None:
                        filterList[c - 1] = k[c + 2]
                if forceInt(filterList[0]) == forceInt(k[3]) and forceInt(filterList[1]) == forceInt(k[4]) and forceInt(filterList[2] == forceInt(k[5])):
                    filterResult[i] = k
                    i += 1

        if filterResult:
            if not self.isFilter:
                self.itemsWithoutFilter = self.items
            self.isFilter = True
            self.items = []
            for k in filterResult.values():
                self.items.append(k)
            self.reset()
        else:
            QtGui.QMessageBox.information(None, u'Запись не найдена', u'По данному запросу запись не найдена.')

    def getItemsList(self):
        if self.isFilter:
            return self.itemsWithoutFilter
        else:
            return self.items

    def saveData(self, masterId):
        db = QtGui.qApp.db
        tableAddress = db.table('OrgStructure_Address')
        idList = []
        for item in self.getItemsList():
            houseInfo = {'KLADRCode'      : item[0],
                         'KLADRStreetCode': item[1],
                         'number'         : item[2],
                         'corpus'         : item[3]}
            houseId = getHouseId(houseInfo)
            record = tableAddress.newRecord()
            record.setValue('master_id', toVariant(masterId))
            record.setValue('house_id', toVariant(houseId))
            record.setValue('firstFlat', toVariant(item[4]))
            record.setValue('lastFlat', toVariant(item[5]))
            idList.append(db.insertRecord(tableAddress, record))
        db.deleteRecord(tableAddress, [tableAddress['master_id'].eq(masterId),
                                       tableAddress['id'].notInlist(idList)])

    def loadData(self, masterId):
        if not masterId:
            return
        db = QtGui.qApp.db
        tableAddress = db.table('OrgStructure_Address')
        tableHouse = db.table('AddressHouse')
        table = tableAddress.leftJoin(tableHouse, tableAddress['house_id'].eq(tableHouse['id']))
        records = db.getRecordList(table, [tableHouse['KLADRCode'],
                                           tableHouse['KLADRStreetCode'],
                                           tableHouse['number'],
                                           tableHouse['corpus'],
                                           tableAddress['firstFlat'],
                                           tableAddress['lastFlat']
                                           ], tableAddress['master_id'].eq(masterId), tableAddress['id'].name())
        for record in records:
            item = [forceString(record.value('KLADRCode')),
                    forceString(record.value('KLADRStreetCode')),
                    forceString(record.value('number')),
                    forceString(record.value('corpus')),
                    forceInt(record.value('firstFlat')),
                    forceInt(record.value('lastFlat')),
                    ]
            self.items.append(item)
        self.reset()

    def addEmptyRow(self, row):
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.insert(row, self.getEmptyItem())
        self.endInsertRows()

    def duplicateRow(self, row):
        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.items.insert(row, [x for x in self.items[row]])
        self.endInsertRows()

    def upRow(self, row):
        item = self.items[row]
        del self.items[row]
        self.items.insert(row - 1, item)
        indexLT = self.index(row - 1, 0)
        indexRB = self.index(row, self.columnCount() - 1)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), indexLT, indexRB)

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        self.items.sort(
            cmp=naturalStringCompare,
            key=lambda (item): forceString(item[column]),
            reverse=(order == QtCore.Qt.DescendingOrder)
        )
        indexLT = self.index(0, 0)
        indexRB = self.index(len(self.items) - 1, self.columnCount() - 1)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), indexLT, indexRB)

    def downRow(self, row):
        item = self.items[row]
        del self.items[row]
        self.items.insert(row + 1, item)
        indexLT = self.index(row, 0)
        indexRB = self.index(row + 1, self.columnCount() - 1)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), indexLT, indexRB)

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex()):
        if 0 <= row and row + count <= len(self.items):
            self.beginRemoveRows(parentIndex, row, row + count - 1)
            del self.items[row:row + count]
            self.endRemoveRows()
            return True
        else:
            return False

    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)


class CKLADRItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CKLADRComboBox(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        KLADRCode = model.data(index, QtCore.Qt.EditRole)
        editor.setCode(forceString(KLADRCode))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.code()))


class CStreetItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = CStreetComboBox(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        code = model.data(index.sibling(index.row(), index.column() - 1), QtCore.Qt.EditRole)
        streetCode = model.data(index, QtCore.Qt.EditRole)
        editor.setCity(forceString(code))
        editor.setCode(forceString(streetCode))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.code()))


class CJobsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_Job', 'id', 'master_id', parent)
        self.addCol(CJobTypeInDocTableCol(u'Тип', 'jobType_id', 20))
        self.addCol(CTimeInDocTableCol(u'Начало', 'begTime', 15, canBeEmpty=True))
        self.addCol(CTimeInDocTableCol(u'Окончание', 'endTime', 15, canBeEmpty=True))
        self.addCol(CIntInDocTableCol(u'Количество', 'quantity', 20, low=0, high=999999))
        self.addCol(CDateInDocTableCol(u'Расписание видимо до', 'lastAccessibleDate', 15))
        self.addCol(CBoolInDocTableCol(u'Видимость в DR', 'isVisibleInDR', 5))


class CRBGapsInDocTableCol(CRBInDocTableCol):
    def setFilter(self, filter):
        self.filter = filter


class CGapsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_Gap', 'id', 'master_id', parent)
        self.addCol(CTimeInDocTableCol(u'Начало', 'begTime', 15))
        self.addCol(CTimeInDocTableCol(u'Окончание', 'endTime', 15))
        self.addCol(CRBGapsInDocTableCol(u'Специальность', 'speciality_id', 10, 'rbSpeciality', prefferedWidth=150))
        self.addCol(CRBGapsInDocTableCol(u'Сотрудник', 'person_id', 20, 'vrbPersonWithSpeciality', order='name', prefferedWidth=150))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if not variantEq(self.data(index, role), value):
            if column == 2:  # специальность
                specialityId = forceRef(value)
                if not specialityId:
                    self.cols()[3].setFilter(u'')
                else:
                    self.cols()[3].setFilter(u'speciality_id = %s' % (specialityId))
                result = CInDocTableModel.setData(self, index, value, role)
                return result
            if column == 3:  # сотрудник
                personId = forceRef(value)
                if not personId:
                    self.cols()[2].setFilter(u'')
                else:
                    self.cols()[2].setFilter(u'id IN (SELECT DISTINCT speciality_id FROM vrbPersonWithSpeciality WHERE id = %s)' % (personId))
                result = CInDocTableModel.setData(self, index, value, role)
                return result
            return CInDocTableModel.setData(self, index, value, role)
        else:
            return True


class CEventTypesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_EventType', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип', 'eventType_id', 20, 'EventType', filter='deleted = 0'))


class CActionTypesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_ActionType', 'id', 'master_id', parent)
        self.addCol(CActionTypeTableCol(u'Тип', 'actionType_id', 20, None, classesVisible=True, descendants=True, model=self))


class CDisabledAttendanceModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_DisabledAttendance', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип прикрепления', 'attachType_id', 20, 'rbAttachType', filter='temporary != 0', showFields=CRBComboBox.showCodeAndName))
        self.addCol(CEnumInDocTableCol(u'Способ ограничения', 'disabledType', 3, [u'мягко', u'строго', u'запрет']))


class CStocksModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_Stock', 'id', 'master_id', parent)
        self.addCol(CNomenclatureInDocTableCol(u'ЛСиИМН', 'nomenclature_id', 50, showFields=CRBComboBox.showName))
        self.addCol(CRBInDocTableCol(u'Тип финансирования', 'finance_id', 20, 'rbFinance'))
        self.addCol(CFloatInDocTableCol(u'Гарантийный запас', 'constrainedQnt', 20))
        self.addCol(CFloatInDocTableCol(u'Точка заказа', 'orderQnt', 20))


class CRBEquipmentCol(CRBInDocTableCol):
    def createEditor(self, parent):
        editor = CEquipmentComboBox(parent)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order=self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor


class CEquipmentsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_Equipment', 'id', 'master_id', parent)
        self.addCol(CRBEquipmentCol(u'Оборудование', 'equipment_id', 15, 'rbEquipment'))
