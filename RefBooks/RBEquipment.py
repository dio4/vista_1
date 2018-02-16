# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4                   import QtGui, QtCore

from library.InDocTable      import CInDocTableModel, CInDocTableCol, CDateInDocTableCol, CRBInDocTableCol
from library.interchange     import getComboBoxValue, getDateEditValue, getLineEditValue, getRBComboBoxValue, \
                                    getSpinBoxValue, setComboBoxValue, setDateEditValue, setLineEditValue, \
                                    setRBComboBoxValue, setSpinBoxValue
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel      import CTableModel, CDateCol, CEnumCol, CNumCol, CRefBookCol, CTextCol
from library.Utils           import forceDate, forceInt, forceRef, forceStringEx

from RefBooks.Tables         import rbCode, rbName, rbEquipment, rbEquipmentType

from Ui_EquipmentsListDialog import Ui_EquipmentsListDialog
from Ui_RBEquipmentEditor    import Ui_RBEquipmentEditorDialog


class CRBEquipmentList(CItemsListDialog, Ui_EquipmentsListDialog):
    setupUi       = Ui_EquipmentsListDialog.setupUi
    retranslateUi = Ui_EquipmentsListDialog.retranslateUi
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CRefBookCol(u'Тип оборудования', ['equipmentType_id'], rbEquipmentType, 10, 2),
            CTextCol(u'Инвентаризационный номер',          ['inventoryNumber'], 10),
            CTextCol(u'Модель',          ['model'], 10),
            CDateCol(u'Дата выпуска', ['releaseDate'], 8),
            CDateCol(u'Дата ввода в эксплуатацию', ['startupDate'], 8),
            CWorkEnumCol(u'Статус', ['status'], [u'Не работает', u'работает'], 5),
            CNumCol(u'Срок службы(лет)', ['employmentTerm'], 7),
            CNumCol(u'Срок гарантии(месяцев)', ['warrantyTerm'], 7),
            CNumCol(u'Период ТО (целое число месяцев)', ['maintenancePeriod'], 12),
            CEnumCol(u'Период ТО(раз в)', ['maintenanceSingleInPeriod'], [u'Нет',
                                                                          u'Неделя',
                                                                          u'Месяц',
                                                                          u'Квартал',
                                                                          u'Полугодие',
                                                                          u'Год'], 12),
            CTextCol(u'Производитель', ['manufacturer'], 10),
            ], rbEquipment, [rbCode, rbName])
        self.cmbEquipmentType.setTable('rbEquipmentType')
        self.setWindowTitleEx(u'Список оборудования')
        self.tblItems.addPopupDelRow()


    def exec_(self):
        result = CItemsListDialog.exec_(self)
        self.saveCurrentItemJournal()
        return result


    def saveCurrentItemJournal(self):
        equipmentId = self.tblItems.currentItemId()
        if bool(equipmentId):
            self.modelMaintenanceJournal.saveItems(equipmentId)


    def setEditableJournal(self, val):
        self.modelMaintenanceJournal.setEditable(val)


    def setup(self, cols, tableName, order, forSelect=False, filterClass=None, allowColumnsHiding=False):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.forSelect = forSelect
        self.filterClass = filterClass
        self.props = {}
        self.order = order

        self.modelMaintenanceJournal = CMaintenanceJournalModel(self)
        self.tblMaintenanceJournal.setModel(self.modelMaintenanceJournal)

        self.model = CEquipmentTableModel(self, cols, self.modelMaintenanceJournal)
        self.selectionModel = QtGui.QItemSelectionModel(self.model, self)
        self.model.idFieldName = self.idFieldName
        self.model.setTable(tableName)
        self.tblItems.setModel(self.model)
        self.tblItems.setSelectionModel(self.selectionModel)
        self.btnSelect.setEnabled(self.forSelect)
        self.btnSelect.setVisible(self.forSelect)
        self.btnSelect.setDefault(self.forSelect)
        self.btnFilter.setEnabled(self.forSelect and bool(self.filterClass))
        self.btnFilter.setEnabled(bool(self.filterClass))
        self.btnFilter.setVisible(bool(self.filterClass))
        self.btnEdit.setDefault(not self.forSelect)
        self.tblItems.setFocus(QtCore.Qt.OtherFocusReason)

        self.btnNew.setShortcut(QtCore.Qt.Key_F9)
        self.btnEdit.setShortcut(QtCore.Qt.Key_F4)
        self.btnPrint.setShortcut(QtCore.Qt.Key_F6)

        self.tblMaintenanceJournal.addPopupDelRow()
        self.tblMaintenanceJournal.addPopupSelectAllRow()
        self.tblMaintenanceJournal.addPopupClearSelectionRow()

        QtCore.QObject.connect(
            self.tblItems.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)
        QtCore.QObject.connect(
            self.selectionModel, QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'), self.on_selectionModel_currentChanged)
        QtCore.QObject.connect(
            self.modelMaintenanceJournal, QtCore.SIGNAL('maintenanceDateChanged(int)'), self.model.maintenanceDateChanged)
        QtCore.QObject.connect(
            self.modelMaintenanceJournal, QtCore.SIGNAL('rowsRemoved(QModelIndex, int, int)'), self.maintenanceRemoved)


    def renewListAndSetTo(self, itemId=None):
        CItemsListDialog.renewListAndSetTo(self, itemId)
        if bool(itemId):
            self.reloadBackGround(itemId)


    def reloadBackGround(self, itemId):
        self.model.maintenanceDateChanged(itemId)


    def maintenanceRemoved(self, index, start, end):
        equipmentId = self.tblItems.currentItemId()
        self.modelMaintenanceJournal.setNeedSave(True)
        if equipmentId:
            self.reloadBackGround(equipmentId)


    def getItemEditor(self):
        return CRBEquipmentEditor(self)


    def getEquipmentIdList(self, props=None):
        if not props:
            props = {}
        db = QtGui.qApp.db
        tableEquipment = db.table('rbEquipment')
        cond = []
        if self.chkOrgStructure.isChecked():
            orgStructureId = self.cmbOrgStructure.value()
            if bool(orgStructureId):
                tableOrgStructureEquipment = db.table('OrgStructure_Equipment')
                condTmp = db.joinAnd([tableOrgStructureEquipment['master_id'].eq(orgStructureId),
                                      tableOrgStructureEquipment['equipment_id'].eq(tableEquipment['id'])])
                cond.append('EXISTS (SELECT OrgStructure_Equipment.`id` FROM OrgStructure_Equipment WHERE %s)'%condTmp)
        if self.chkReleaseDate.isChecked():
            cond.append(tableEquipment['releaseDate'].dateLe(self.edtReleaseDateTo.date()))
            cond.append(tableEquipment['releaseDate'].dateGe(self.edtReleaseDateFrom.date()))
        if self.chkEquipmentType.isChecked():
            equipmentTypeId = self.cmbEquipmentType.value()
            if equipmentTypeId:
                cond.append(tableEquipment['equipmentType_id'].eq(equipmentTypeId))
        if self.chkModel.isChecked():
            model = forceStringEx(self.edtModel.text())
            if model:
                cond.append(tableEquipment['model'].like('%'+model+'%'))
        if self.chkInventoryNumber.isChecked():
            inventoryNumber = forceStringEx(self.edtInventoryNumber.text())
            if inventoryNumber:
                cond.append(tableEquipment['inventoryNumber'].like('%'+inventoryNumber+'%'))
        if self.chkStatus.isChecked():
            cond.append(tableEquipment['status'].eq(self.cmbStatus.currentIndex()))
        if self.chkMaintenance.isChecked():
            tableMaintenance = db.table('EquipmentMaintenanceJournal')
            condValue = self.cmbMaintenance.currentIndex()
            if condValue == 0: # не определено ТО
                cond.append(db.existsStmt(tableMaintenance,
                                          'NOT '+tableMaintenance['master_id'].eq(tableEquipment['id'])))
            elif condValue == 1:# ТО просрочено
                idList = self.model.getIdListByMaintenance()
                cond.append(tableEquipment['id'].inlist(idList))
            elif condValue == 2: # Осталось до окончания ТО
                idList = self.model.getIdListByMaintenance(self.edtMaintenanceTerm.value(),
                                                           self.cmbMaintenanceTermType.currentIndex())
                cond.append(tableEquipment['id'].inlist(idList))
        if self.chkWarranty.isChecked():
            condValue = self.cmbWarranty.currentIndex()
            if condValue == 0: # Гарантия не определена
                cond.append(db.joinOr([tableEquipment['warrantyTerm'].isNull(),
                                      tableEquipment['warrantyTerm'].eq(0)]))
            elif condValue == 1: # На гарантии
                condText = 'DATE(DATE_ADD(%s , INTERVAL %s MONTH)) >= DATE(%s)' %  (tableEquipment['releaseDate'].name(), tableEquipment['warrantyTerm'].name(), db.formatQVariant(QtCore.QVariant.Date, QtCore.QVariant(QtCore.QDate.currentDate())))
                cond.append(condText)
            elif condValue == 2: # Гарантии нет (истекла или не было)
                condText = 'DATE(DATE_ADD(%s , INTERVAL %s MONTH)) < DATE(%s)' %  (tableEquipment['releaseDate'].name(), tableEquipment['warrantyTerm'].name(), db.formatQVariant(QtCore.QVariant.Date, QtCore.QVariant(QtCore.QDate.currentDate())))
                cond.append(db.joinOr([condText,
                             tableEquipment['warrantyTerm'].isNull(),
                             tableEquipment['warrantyTerm'].eq(0)]))
            elif condValue == 3: # До истечения гарантии осталось
                termValue = self.edtWarrantyTerm.value()
                termType  = self.cmbWarrantyTermType.currentIndex()
                if termType == 0:
                    strTermType = 'DAY'
                elif termType == 1:
                    strTermType = 'MONTH'
                elif termType == 2:
                    strTermType = 'YEAR'
                condText = 'DATE(DATE_ADD(%s , INTERVAL %d %s)) = DATE(%s)' %  (tableEquipment['releaseDate'].name(), termValue, strTermType, db.formatQVariant(QtCore.QVariant.Date, QtCore.QVariant(QtCore.QDate.currentDate())))
                cond.append(condText)
        if self.chkEmploymentTerm.isChecked():
            employmentTermValue = self.edtEmploymentTerm.value()
            cond.append(tableEquipment['employmentTerm'].eq(employmentTermValue))
        idList = db.getIdList(tableEquipment, 'id', cond)
        return idList


    def on_filterButtonBox_apply(self, id = None):
#        idList = self.getEquipmentIdList()
        self.renewListAndSetTo(id)


    def on_filterButtonBox_reset(self):
        self.chkOrgStructure.setChecked(False)
        self.cmbOrgStructure.setEnabled(False)

        self.chkReleaseDate.setChecked(False)
        self.edtReleaseDateFrom.setEnabled(False)
        self.edtReleaseDateTo.setEnabled(False)

        self.chkEquipmentType.setChecked(False)
        self.cmbEquipmentType.setEnabled(False)

        self.chkModel.setChecked(False)
        self.edtModel.setEnabled(False)

        self.chkInventoryNumber.setChecked(False)
        self.edtInventoryNumber.setEnabled(False)

        self.chkStatus.setChecked(False)
        self.cmbStatus.setEnabled(False)


    def select(self, props):
        table = self.model.table()
        return self.getEquipmentIdList(props)


#    @pyqtSlot(QtGui.QAbstractButton)
    def on_filterButtonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.saveCurrentItemJournal()
            self.on_filterButtonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_filterButtonBox_reset()
            self.on_filterButtonBox_apply()
        elif unicode(button.text()) == u'Применить':
            self.saveCurrentItemJournal()
            self.on_filterButtonBox_apply()
        elif unicode(button.text()) == u'Сбросить':
            self.on_filterButtonBox_reset()
            self.on_filterButtonBox_apply()


#    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModel_currentChanged(self, currentIndex, previousIndex):
        if previousIndex.isValid():
            previousEquipmentId = self.tblItems.itemId(previousIndex)
            self.modelMaintenanceJournal.saveItems(previousEquipmentId)
        equipmentId = self.tblItems.currentItemId()
        if bool(equipmentId):
            self.modelMaintenanceJournal.loadItems(equipmentId)
        else:
            self.modelMaintenanceJournal.loadItems(0)



class CRBEquipmentEditor(CItemEditorBaseDialog, Ui_RBEquipmentEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbEquipment)
        self.setupUi(self)

        self.addModels('Tests', CEquipmentTestModel(self))
        self.setModels(self.tblTests, self.modelTests, self.selectionModelTests)

        self.tblTests.addPopupSelectAllRow()
        self.tblTests.addPopupClearSelectionRow()
        self.tblTests.addPopupSeparator()
        self.tblTests.addPopupDelRow()

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Оборудование')
        self.cmbEquipmentType.setTable(rbEquipmentType)
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(  self.edtCode,                      record, rbCode)
        setLineEditValue(  self.edtName,                      record, rbName)
        setRBComboBoxValue(self.cmbEquipmentType,             record, 'equipmentType_id')
        setSpinBoxValue(   self.edtTripod,                    record, 'tripod')
        setSpinBoxValue(   self.edtTripodCapacity,            record, 'tripodCapacity')
        setLineEditValue(  self.edtInventoryNumber,           record, 'inventoryNumber')
        setLineEditValue(  self.edtModel,                     record, 'model')
        setDateEditValue(  self.edtReleaseDate,               record, 'releaseDate')
        setDateEditValue(  self.edtStartupDate,               record, 'startupDate')
        setComboBoxValue(  self.cmbStatus,                    record, 'status')
        setSpinBoxValue(   self.edtEmploymentTerm,            record, 'employmentTerm')
        setSpinBoxValue(   self.edtWarrantyTerm,              record, 'warrantyTerm')
        setSpinBoxValue(   self.edtMaintenancePeriod,         record, 'maintenancePeriod')
        setComboBoxValue(  self.cmbMaintenanceSingleInPeriod, record, 'maintenanceSingleInPeriod')
        setLineEditValue(  self.edtManufacturer,              record, 'manufacturer')
        setComboBoxValue(  self.cmbProtocol,                  record, 'protocol')
        setLineEditValue(  self.edtAddress,                   record, 'address')
        setLineEditValue(  self.edtOwnName,                   record, 'ownName')
        setLineEditValue(  self.edtLabName,                   record, 'labName')

        self.modelTests.loadItems(forceRef(record.value('id')))



    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(  self.edtCode,                      record, rbCode)
        getLineEditValue(  self.edtName,                      record, rbName)
        getRBComboBoxValue(self.cmbEquipmentType,             record, 'equipmentType_id')
        getSpinBoxValue(   self.edtTripod,                    record, 'tripod')
        getSpinBoxValue(   self.edtTripodCapacity,            record, 'tripodCapacity')
        getLineEditValue(  self.edtInventoryNumber,           record, 'inventoryNumber')
        getLineEditValue(  self.edtModel,                     record, 'model')
        getDateEditValue(  self.edtReleaseDate,               record, 'releaseDate')
        getDateEditValue(  self.edtStartupDate,               record, 'startupDate')
        getComboBoxValue(  self.cmbStatus,                    record, 'status')
        getSpinBoxValue(   self.edtEmploymentTerm,            record, 'employmentTerm')
        getSpinBoxValue(   self.edtWarrantyTerm,              record, 'warrantyTerm')
        getSpinBoxValue(   self.edtMaintenancePeriod,         record, 'maintenancePeriod')
        getComboBoxValue(  self.cmbMaintenanceSingleInPeriod, record, 'maintenanceSingleInPeriod')
        getLineEditValue(  self.edtManufacturer,              record, 'manufacturer')
        getComboBoxValue(  self.cmbProtocol,                  record, 'protocol')
        getLineEditValue(  self.edtAddress,                   record, 'address')
        getLineEditValue(  self.edtOwnName,                   record, 'ownName')
        getLineEditValue(  self.edtLabName,                   record, 'labName')
        return record


    def saveInternals(self, id):
        self.modelTests.saveItems(id)

    def checkDataEntered(self):
        result = True
        result = result and self.checkModelTests()
        return result

    def checkModelTests(self):
        for row, item in enumerate(self.modelTests.items()):
            if not forceRef(item.value('test_id')):
                return self.checkValueMessage(u'Необходимо указать тест!',
                                              False, self.tblTests, row=row, column=0)
        return True

    @QtCore.pyqtSlot(int)
    def on_cmbMaintenanceSingleInPeriod_currentIndexChanged(self, index):
        if bool(index) and bool(self.edtMaintenancePeriod.value()):
            self.edtMaintenancePeriod.setValue(0)


    @QtCore.pyqtSlot(int)
    def on_edtMaintenancePeriod_valueChanged(self, value):
        if bool(value) and bool(self.cmbMaintenanceSingleInPeriod.currentIndex()):
            self.cmbMaintenanceSingleInPeriod.setCurrentIndex(0)

# #################################################

class CWorkEnumCol(CEnumCol):
    def getForegroundColor(self, values):
        value = forceInt(values[0])
        if not value:
            return QtCore.QVariant(QtGui.QColor(255, 0, 0))
        return QtCore.QVariant()


class CEquipmentTableModel(CTableModel):
    def __init__(self, parent, cols, journalModel=None):
        CTableModel.__init__(self, parent, cols)
        self.mapBackGroundToId = {}
        self.journalModel = journalModel


    def getIdListByMaintenance(self, value=None, valueType=None):
        def checkByValueAndValueType(data, value, valueType):
            backGround, endDate = data
            if (value is None) and (valueType is None):
                return backGround.isValid() # значит просрочено
            else:
                if not backGround.isValid(): # не просрочено, мы же ищем "которым осталось до просрочености"
                    currentDate = QtCore.QDate.currentDate()
                    if valueType == 0: # дней
                        return currentDate.addDays(value) == endDate
                    elif valueType == 1: # месяцев
                        currentDays      = currentDate.daysInMonth()
                        endDays          = endDate.daysInMonth()
                        checkCurrentDate = QtCore.QDate(currentDate.year(), currentDate.month(), currentDays)
                        checkEndDate     = QtCore.QDate(endDate.year(), endDate.month(), endDays)
                        return checkCurrentDate.addMonths(value) == checkEndDate
                    elif valueType == 2: # лет
                        checkCurrentDate = QtCore.QDate(currentDate.year(), 12, 31)
                        checkEndDate     = QtCore.QDate(endDate.year(), 12, 31)
                        return checkCurrentDate.addYears(value) == checkEndDate
            return False

        recordList = QtGui.qApp.db.getRecordList('rbEquipment')
        if recordList:
            localMapBackGroundToId = {}
            for record in recordList:
                backGround, endDate = self.getBackGroundByMaintenancePeriod(record)
                localMapBackGroundToId[forceRef(record.value('id'))] = (backGround, endDate)
            return [id for id in localMapBackGroundToId.keys() if checkByValueAndValueType(localMapBackGroundToId[id],
                                                                                               value, valueType)]
        return []


    def getLastEquipmentMaintenanceDateFromModel(self, startupDate):
        date = startupDate
        for item in self.journalModel.items():
            modelDate = forceDate(item.value('date'))
            if modelDate > date:
                date = modelDate
        return date


    def getLastEquipmentMaintenanceDate(self, equipmentId, startupDate):
        db = QtGui.qApp.db
        tableJournal = db.table('EquipmentMaintenanceJournal')
        cond = [tableJournal['master_id'].eq(equipmentId)]
        record = db.getRecordEx(tableJournal, 'MAX('+tableJournal['date'].name()+') AS maxDate', cond)
        if record:
            date = forceDate(record.value('maxDate'))
            if date.isValid():
                return date
        return startupDate


    def maintenanceDateChanged(self, equipmentId):
        if bool(equipmentId):
            self.mapBackGroundToId[equipmentId] = (None, QtCore.QDate())
            record = self._recordsCache.get(equipmentId)
            valid = self.isValidMaintenancePeriod(record)
            if not valid:
                self.mapBackGroundToId[equipmentId] = (QtCore.QVariant(), QtCore.QDate())
            else:
                startupDate = forceDate(record.value('startupDate'))
                date = self.getLastEquipmentMaintenanceDateFromModel(startupDate)
                backGround, endDate = self.makeBackGround(date, record)
                self.mapBackGroundToId[equipmentId] = (backGround, endDate)

            self.emitDataChanged()


    def getBackGround(self, id):
        return self.mapBackGroundToId.get(id, (None, QtCore.QDate()))


    def getBackGroundByMaintenancePeriod(self, record):
        equipmentId = forceRef(record.value('id'))
        backGround, endDate = self.getBackGround(equipmentId)
        if not backGround:
            valid = self.isValidMaintenancePeriod(record)
            if not valid:
                return (QtCore.QVariant(), endDate)
            startupDate = forceDate(record.value('startupDate'))
            date = self.getLastEquipmentMaintenanceDate(equipmentId, startupDate)
            backGround, endDate = self.makeBackGround(date, record)
            self.mapBackGroundToId[equipmentId] = (backGround, endDate)
        return backGround, endDate


    def makeBackGround(self, date, record):
        backGround = QtCore.QVariant()
        maintenancePeriod = forceInt(record.value('maintenancePeriod'))
        maintenanceSingleInPeriod = forceInt(record.value('maintenanceSingleInPeriod'))
        currentDate = QtCore.QDate.currentDate()
        if bool(maintenancePeriod) and date.isValid():
            endDate = date.addMonths(maintenancePeriod)
            if endDate < currentDate:
                backGround = QtCore.QVariant(QtGui.QColor(125, 125, 125))
        elif bool(maintenanceSingleInPeriod) and date.isValid():
            checker = self.getCheckerMaintenanceSingleInPeriod(maintenanceSingleInPeriod)
            valid, endDate = checker(date, currentDate)
            if not valid:
                backGround = QtCore.QVariant(QtGui.QColor(125, 125, 125))
        return backGround, endDate


    def isValidMaintenancePeriod(self, record):
        maintenancePeriod = forceInt(record.value('maintenancePeriod'))
        maintenanceSingleInPeriod = forceInt(record.value('maintenanceSingleInPeriod'))
        bothEmpty = not (bool(maintenancePeriod) or bool(maintenanceSingleInPeriod))
        bothFull  = bool(maintenancePeriod) and bool(maintenanceSingleInPeriod)
        valid =  not (bothEmpty or bothFull)
        return valid


    def getCheckerMaintenanceSingleInPeriod(self, value):
        def checkWeek(date, currentDate):
            iWeekDay = currentDate.dayOfWeek()
            mondey   = currentDate.addDays(QtCore.Qt.Monday-iWeekDay)
            sunday   = currentDate.addDays(QtCore.Qt.Sunday-iWeekDay)
            return (date >= mondey and date <= sunday), sunday

        def checkMonth(date, currentDate):
            monthDays = currentDate.daysInMonth()
            iDay      = currentDate.day()
            firstDay  = currentDate.addDays(1-iDay)
            lastDay   = currentDate.addDays(monthDays-iDay)
            return (date >= firstDay and date <= lastDay), lastDay

        def checkQuarter(date, currentDate):
            iMonth     = currentDate.month()
            iQuarter   = ((iMonth-1)/3)+1
            iInQuarter = iMonth-((iQuarter-1)*3)
            firstMonth = currentDate.addMonths(1-iInQuarter)
            lastMonth  = currentDate.addMonths(3-iInQuarter)
            firstDate  = QtCore.QDate(firstMonth.year(), firstMonth.month(), 1)
            lastDate   = QtCore.QDate(lastMonth.year(), lastMonth.month(), lastMonth.daysInMonth())
            return (date >= firstDate and date <= lastDate), lastDate

        def checkHalfYear(date, currentDate):
            iMonth     = currentDate.month()
            iHalf      = ((iMonth-1)/6)+1
            iInHalf    = iMonth-((iHalf-1)*6)
            firstMonth = currentDate.addMonths(1-iInHalf)
            lastMonth  = currentDate.addMonths(6-iInHalf)
            firstDate  = QtCore.QDate(firstMonth.year(), firstMonth.month(), 1)
            lastDate   = QtCore.QDate(lastMonth.year(), lastMonth.month(), lastMonth.daysInMonth())
            return (date >= firstDate and date <= lastDate), lastDate

        def checkYear(date, currentDate):
            firstDate = QtCore.QDate(currentDate.year(), 1, 1)
            lastDate  = QtCore.QDate(currentDate.year(), 12, 31)
            return (date >= firstDate and date <= lastDate), lastDate

        def default(date, currentDate):
            return True, QtCore.QDate()

        funcs = {1:checkWeek,
                 2:checkMonth,
                 3:checkQuarter,
                 4:checkHalfYear,
                 5:checkYear}

        return funcs.get(value, default)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.BackgroundRole:
            column = index.column()
            row    = index.row()
            (col, values) = self.getRecordValues(column, row)
            backGround, endDate = self.getBackGroundByMaintenancePeriod(values[1])
            return backGround
        else:
            return CTableModel.data(self, index, role)
        return QtCore.QVariant()

# #########################################################

class CMaintenanceJournalModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'EquipmentMaintenanceJournal', 'id', 'master_id', parent)
        self.addCol(CInDocTableCol(u'ФИО мастера', 'fullName', 30))
        self.addCol(CDateInDocTableCol(u'Дата ТО', 'date', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Планируемая дата ТО', 'plannedDate', 15, canBeEmpty=True))
        self.addCol(CInDocTableCol(u'Примечание', 'note', 30))
        self.currentMasterId = None
        self.needSave = False
        self.isEditable = False

    def setEditable(self, val):
        self.isEditable = val

    def cellReadOnly(self, index):
        return not self.isEditable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CInDocTableModel.setData(self, index, value, role)
        if result:
            self.needSave = True
            if index.column() == 1 and bool(self.currentMasterId):
                self.emit(QtCore.SIGNAL('maintenanceDateChanged(int)'), self.currentMasterId)
        return result

    def setNeedSave(self, val):
        self.needSave = val

    def loadItems(self, masterId):
        self.currentMasterId = masterId
        CInDocTableModel.loadItems(self, masterId)

    def saveItems(self, masterId):
        if self.needSave:
            CInDocTableModel.saveItems(self, masterId)
            self.needSave = False


class CEquipmentTestModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbEquipment_Test', 'id', 'equipment_id', parent)
        self.addCol(CRBInDocTableCol(u'Тест', u'test_id', 10, u'rbTest', showFields=2))
        self.addCol(CInDocTableCol(u'Код теста', 'hardwareTestCode', 15))
        self.addCol(CInDocTableCol(u'Наименование теста', 'hardwareTestName', 15))
        self.addCol(CInDocTableCol(u'Код образца', 'hardwareSpecimenCode', 15))
        self.addCol(CInDocTableCol(u'Наименование образца', 'hardwareSpecimenName', 15))
