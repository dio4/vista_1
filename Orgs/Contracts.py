# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Accounting.FormProgressDialog  import CFormProgressDialog, CContractFormProgressDialog
from Accounting.Utils               import getContractInfo, packExposeDiscipline, unpackExposeDiscipline

from Events.ActionsSelector         import CEnableCol
from Events.EventInfo               import CContractInfo

from Exchange.ImportTariffs         import ImportTariffs
from Exchange.ImportTariffsINFIS    import ImportTariffsINFIS
from Exchange.ImportTariffsR67      import ImportTariffsR67
from Exchange.ImportTariffsR77      import ImportTariffsR77
from Exchange.ImportTariffsUniversal import ImportTariffsR23, ImportTariffsR61, ImportTariffsR51, ImportTariffsR85
from Exchange.ExportTariffsXML      import ExportTariffsXML
from Exchange.ExportTariffsR23      import ExportTariffsR23
from Exchange.ImportTariffsXML      import ImportTariffsXML
from ServiceSelectedDialog          import CServiceSelectedDialog

from library.Counter                import getContractDocumentNumber
from library.crbcombobox            import CRBComboBox
from library.DateEdit               import CDateEdit
from library.DialogBase             import CDialogBase, CConstructHelperMixin
from library.InDocTable             import CInDocTableModel, CInDocTableCol, CEnumInDocTableCol, CFloatInDocTableCol, \
                                           CRBInDocTableCol, CInDocTableSortFilterProxyModel
from library.interchange            import getCheckBoxValue, getComboBoxValue, getDateEditValue, getDoubleBoxValue, \
                                           getLineEditValue, getRBComboBoxValue, setCheckBoxValue, setComboBoxValue, \
                                           setDateEditValue, setDoubleBoxValue, setLineEditValue, setRBComboBoxValue, \
                                           getSpinBoxValue, setSpinBoxValue
from library.ItemsListDialog        import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel             import CTableModel, CBackRelationCol, CDateCol, CDesignationCol, CEnumCol, CNumCol, CRefBookCol, CSumCol, CTextCol, \
    CCol, CBoolCol
from library.PrintInfo              import CInfoContext
from library.PrintTemplates         import getPrintAction, applyTemplate
from library.Utils                  import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, \
                                           forceStringEx, toVariant, copyFields, formatNum, formatSex, getVal, \
    CIncremetalFilterHelper, forceDecimal

from IntroducePercentDialog    import CIntroducePercentDialog
from OrgComboBox               import COrgInDocTableCol, CInsurerInDocTableCol
from Orgs                      import selectOrganisation
from PaymentSchemeEditor       import CPaymentSchemeEditor
from TariffModel               import CTariffModel
from Utils                     import getAccountInfo, getOrganisationInfo

from RefBooks.Tables                import rbAccountExportFormat, rbFinance
from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase

from Users.Rights                   import urAccessPriceCalculate

from DublicateTariff import CDuplicateTariff

from Ui_ContractEditor              import Ui_ContractEditorDialog
from Ui_ContractItemsListDialog     import Ui_ContractItemsListDialog
from Ui_PriceCoefficientEditor      import Ui_PriceCoefficientDialog
from Ui_PriceListDialog             import Ui_PriceListDialog
from Ui_ParamsContractDialog        import Ui_ParamsContractDialog
from Ui_PaymentSchemeItemEditor     import Ui_PaymentSchemeItemEditor
from Ui_PaymentSchemeItemEditDialog import Ui_PaymentSchemeItemEditDialog


class CDoubleSpinBoxEdit(QtGui.QDoubleSpinBox):
    def __init__(self, parent=None):
        QtGui.QDoubleSpinBox.__init__(self, parent)


class CCoefficientItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)


    def createEditor(self, parent, option, index):
        editor = CDoubleSpinBoxEdit(parent)
        return editor


    def setEditorData(self, editor, index):
        model  = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setValue(forceDouble(data))


    def setModelData(self, editor, model, index):
        model.setData(index, QtCore.QVariant(editor.value()))


class CDateItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)


    def createEditor(self, parent, option, index):
        editor = CDateEdit(parent)
        return editor


    def setEditorData(self, editor, index):
        model  = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setDate(data.toDate())


    def setModelData(self, editor, model, index):
        model.setData(index, QtCore.QVariant(editor.date()))


class CStringEdit(QtGui.QLineEdit):
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)


class CStringItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)


    def createEditor(self, parent, option, index):
        editor = CStringEdit(parent)
        return editor


    def setEditorData(self, editor, index):
        model  = index.model()
        data = model.data(index, QtCore.Qt.EditRole)
        editor.setText(forceString(data))


    def setModelData(self, editor, model, index):
        model.setData(index, QtCore.QVariant(editor.text()))

class CPaymentSchemeClinicalTestModel(CTableModel):
    def __init__(self, parent=None):
        CTableModel.__init__(self, parent, [
            CDesignationCol(u'Подразделение', ['orgStructure_id'], ('OrgStructure', 'code'), 25),
            CDesignationCol(u'Главный исследователь', ['person_id'], ('vrbPerson', 'name'), 30),
            CTextCol(u'№ договора', ['number'], 20),
            CDateCol(u'Дата заключения', ['begDate'], 20),
            CDateCol(u'Дата окончания', ['endDate'], 20),
            CDesignationCol(u'Контрагент', ['org_id'], ('Organisation', 'shortName'), 35),
            CTextCol(u'Наименование', ['nameProtocol'], 35),
            CTextCol(u'№ протокола', ['numberProtocol'], 15),
            CBoolCol(u'Набор пациентов', ['enrollment'], 15)
        ], 'PaymentScheme')

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            record = self.getRecordByRow(row)
            if record:
                if not forceInt(self.getRecordByRow(row).value('enrollment')):
                    return toVariant(QtGui.QColor(QtCore.Qt.green))
                if forceDate(self.getRecordByRow(row).value('endDate')) < QtCore.QDate.currentDate():
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
        return CTableModel.data(self, index, role)

class CPaymentSchemeClearingModel(CTableModel):
    def __init__(self, parent=None):
        CTableModel.__init__(self, parent, [
            CTextCol(u'№ договора', ['number'], 20),
            CDateCol(u'Дата заключения', ['begDate'], 20),
            CDateCol(u'Дата окончания', ['endDate'], 20),
            CDesignationCol(u'Контрагент', ['org_id'], ('Organisation', 'shortName'), 35)
        ], 'PaymentScheme')

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        columnFieldNames = column.fields()
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            record = self.getRecordByRow(row)
            if record:
                if forceDate(self.getRecordByRow(row).value('endDate')) < QtCore.QDate.currentDate():
                    return toVariant(QtGui.QColor(QtCore.Qt.red))
        return CTableModel.data(self, index, role)

class CContractItemsListDialog(CItemsListDialog, Ui_ContractItemsListDialog,):
    setupUi = Ui_ContractItemsListDialog.setupUi
    retranslateUi = Ui_ContractItemsListDialog.retranslateUi

    def __init__(self, parent):
        cols = [
            CBackRelationCol(interfaceCol = CNumCol(u'Номер этапа', ['idx'], 15),
                             primaryKey = 'id',
                             subTableName = 'PaymentSchemeItem',
                             subTableForeignKey = 'contract_id',
                             subTableCond = 'idx > 0 AND deleted = 0'),
            CBackRelationCol(interfaceCol = CTextCol(u'Наименование этапа', ['name'], 20),
                             primaryKey = 'id',
                             subTableName = 'PaymentSchemeItem',
                             subTableForeignKey = 'contract_id',
                             subTableCond = 'deleted = 0'),
            CBackRelationCol(interfaceCol = CEnumCol(u'Тип этапа', ['type'], [u'обычный', u'по показаниям'], 10, 'c'),
                             primaryKey = 'id',
                             subTableName = 'PaymentSchemeItem',
                             subTableForeignKey = 'contract_id',
                             subTableCond = 'deleted = 0'),
            CRefBookCol(u'Источник финансирования', ['finance_id'], 'rbFinance', 30),
            CTextCol(u'Группа',                  ['grouping'],    30),
            CTextCol(u'Основание',               ['resolution'],  20),
            CTextCol(u'Номер',                   ['number'],      15),
            CTextCol(u'Счетчик',                 ['counterValue'],10),
            # CSumPricesCol(u'Стоимость визита',   ['id'],          10),
            CDateCol(u'Дата',                    ['date'],        10),
            CDateCol(u'Нач.дата',                ['begDate'],     10),
            CDateCol(u'Кон.дата',                ['endDate'],     10),
        ]
        sumPricesCol = CSumPricesCol(u'Стоимость визита', ['id'], 10)

        if not forceBool(QtGui.qApp.preferences.appPrefs.get('DisableSumPricesCol', True)):
            cols.insert(-3, sumPricesCol)

        CItemsListDialog.__init__(
            self,
            parent,
            cols,
            'Contract',
            [
                'Contract.finance_id',
                'Contract.grouping',
                'Contract.resolution',
                'Contract.number',
                'Contract.date'
            ]
        )
        self.setWindowTitleEx(u'Договоры')

class CSumPricesCol(CCol):
    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CCol.__init__(self, title, fields, defaultWidth, alignment)
        self.db = QtGui.qApp.db

    def getSumByContract(self, contractId):
        tblContractTariff = self.db.table('Contract_Tariff')
        records = self.db.getRecordList(tblContractTariff, '*', tblContractTariff['master_id'].eq(contractId))
        sumPrices = forceDecimal(0)
        for record in records:
            sumPrices += (forceDecimal(record.value('price')) * forceDecimal(record.value('amount')))
        return sumPrices

    def load(self, contractId):
        # contractId = forceInt(values[0])
        # sumPrices = self.getSumByContract(contractId)
        # return toVariant(sumPrices)
        sumPrices = self.getSumByContract(contractId)
        self.putIntoCache(contractId, sumPrices)

    def formatNative(self, values):
        contractId = forceInt(values[0])
        sumPrices = self.getSumByContract(contractId)
        return toVariant(sumPrices)

class CContractsList(CContractItemsListDialog, CConstructHelperMixin):
    contractTypeCode = {0: ['clearing', 'clinicalTest'],
                        1: 'clinicalTest',
                        2: 'clearing'}

    def __init__(self, parent):
        CContractItemsListDialog.__init__(self, parent)
        self.contractType = None
        self.currentPaymentSchemeId = None
        self.item = {'name': None, 'type': None, 'contractTypeCode': None, 'new': False}
        self.tblItems.setPopupMenu(self.mnuItems)
        self.btnSynchronize.setEnabled(False)
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(QtCore.QDate(currentDate.year(), 1, 1))
        self.edtEndDate.setDate(QtCore.QDate(currentDate.year(), 12, 31))
        self.cmbFinanceSource.setTable('rbFinance', addNone=True)
        self.getGroupingText()
        self.getResolutionText()
        self.filterParams = {}
        self.resetFilterContract()
        self.tabBar.addTab(u'Основные договоры')
        self.tabBar.addTab(u'Клинические испытания')
        self.tabBar.addTab(u'Безналичный расчет')
        self.setModels(self.tblClinicalTest, self.modelClinicalTest, self.selectionModelClinicalTest)
        self.setModels(self.tblClearing, self.modelClearing, self.selectionModelClearing)
        self.updateFilterPaymentScheme()
        self.cmbPerson.setIsInvestigator(True)

    def setupUi(self, widget):
        self.setupPopupMenu()
        self.addModels('ClinicalTest', CPaymentSchemeClinicalTestModel(self))
        self.addModels('Clearing', CPaymentSchemeClearingModel(self))
        self.btnSynchronize =  QtGui.QPushButton(u'Синхронизация', self)
        self.btnSynchronize.setObjectName('btnSynchronize')
        self.btnCreatePaymentScheme = QtGui.QPushButton(u'Создать протокол', self)
        self.btnCreatePaymentScheme.setObjectName('btnCreatePaymentScheme')
        self.btnEditPaymentSchemeItem = QtGui.QPushButton(u'Редактировать порядок этапов', self)
        self.btnEditPaymentSchemeItem.setObjectName('btnEditPaymentSchemeItem')
        CContractItemsListDialog.setupUi(self, widget)
        self.buttonBox.addButton(self.btnSynchronize, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnCreatePaymentScheme, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnEditPaymentSchemeItem, QtGui.QDialogButtonBox.ActionRole)

    def setupPopupMenu(self):
        self.mnuItems = QtGui.QMenu(self)
        self.mnuItems.setObjectName('mnuItems')
        self.actRemoveContract = QtGui.QAction(u'Удалить', self)
        self.actRemoveContract.setObjectName('actRemoveContract')
        self.actDuplicateContract = QtGui.QAction(u'Дублировать', self)
        self.actDuplicateContract.setObjectName('actDuplicateContract')
        self.actDuplicateContractNoExpense = QtGui.QAction(u'Дублировать с тарифами без статей затрат', self)
        self.actDuplicateContractNoExpense.setObjectName('actDuplicateContractNoExpense')
        self.actDuplicateContractNoTariff = QtGui.QAction(u'Дублировать без тарифов', self)
        self.actDuplicateContractNoTariff.setObjectName('actDuplicateContractNoTariff')
        self.actSynchronizeContract = QtGui.QAction(u'Синхронизация', self)
        self.actSynchronizeContract.setObjectName('actSynchronizeContract')

        self.mnuItems.addAction(self.actDuplicateContract)
        self.mnuItems.addSeparator()
        self.mnuItems.addAction(self.actDuplicateContractNoExpense)
        self.mnuItems.addSeparator()
        self.mnuItems.addAction(self.actDuplicateContractNoTariff)
        self.mnuItems.addSeparator()
        self.mnuItems.addAction(self.actRemoveContract)
        self.mnuItems.addSeparator()
        self.mnuItems.addAction(self.actSynchronizeContract)


    def getItemEditor(self):
        return CContractEditor(self, self.currentPaymentSchemeId)


    @QtCore.pyqtSlot()
    def on_mnuItems_aboutToShow(self):
        itemPresent = self.tblItems.currentIndex().row()>=0
        self.actDuplicateContract.setEnabled(itemPresent)
        self.actDuplicateContractNoTariff.setEnabled(itemPresent)
        self.actRemoveContract.setEnabled(itemPresent)
        self.actSynchronizeContract.setEnabled(itemPresent and bool(self.getPriceListId()))


    def getPriceListId(self):
        contractId = self.tblItems.currentItemId()
        priceListId = None
        if contractId:
            db = QtGui.qApp.db
            table = db.table('Contract')
            record = db.getRecordEx(table, [table['priceList_id']], [table['deleted'].eq(0), table['priceList_id'].eq(contractId)])
            priceListId = forceRef(record.value('priceList_id')) if record else None
        return priceListId


    @QtCore.pyqtSlot()
    def on_actDuplicateContract_triggered(self):
        self.duplicateContract()


    @QtCore.pyqtSlot()
    def on_actDuplicateContractNoExpense_triggered(self):
        self.duplicateContract(dupTariff=True, dupExpense=False)


    @QtCore.pyqtSlot()
    def on_actSynchronizeContract_triggered(self):
        self.on_btnSynchronize_clicked()


    @QtCore.pyqtSlot()
    def on_actDuplicateContractNoTariff_triggered(self):
        self.duplicateContract(dupTariff=False, dupExpense=False)


    def duplicateContract(self, dupTariff=True, dupExpense=True):
        contractId = self.tblItems.currentItemId()
        db = QtGui.qApp.db
        table = db.table('Contract')
        tableContractTariff = db.table('Contract_Tariff')
        tableContractExpense = db.table('Contract_CompositionExpense')
        db.transaction()
        try:
            record = db.getRecord(table, '*', contractId)
            record.setNull('id')
            record.setValue('number', toVariant(forceString(record.value('number'))+u'-копия'))
            useCounter = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'useCounterInContracts', QtCore.QVariant()))
            # Для договоров и для счетов используется единый счетчик
            if useCounter:
                counterId = forceRef(db.translate('rbCounter', 'code', 'contract', 'id'))
                counterValue = getContractDocumentNumber(counterId)
                record.setValue('counterValue', toVariant(counterValue))
            else:
                record.setValue('counterValue', QtCore.QVariant())
            newId = db.insertRecord(table, record)
            db.copyDepended(db.table('Contract_Contingent'), 'master_id', contractId, newId)
            db.copyDepended(db.table('Contract_Contragent'), 'master_id', contractId, newId)
            db.copyDepended(db.table('Contract_Specification'), 'master_id', contractId, newId)
            if dupTariff:
                stmt = db.selectStmt(tableContractTariff, '*', [tableContractTariff['master_id'].eq(contractId), tableContractTariff['deleted'].eq(0)], order = 'id')
                qquery = db.query(stmt)
                while qquery.next():
                    recordTariff = qquery.record()
                    tariffId = forceRef(recordTariff.value('id'))
                    recordTariff.setNull('id')
                    recordTariff.setValue('master_id', toVariant(newId))
                    newTariffId = db.insertRecord(tableContractTariff, recordTariff)
                    if dupExpense and tariffId and newTariffId:
                        recordExpenses = db.getRecordList(tableContractExpense, '*', [tableContractExpense['master_id'].eq(tariffId)])
                        for recordExpense in recordExpenses:
                            recordExpense.setNull('id')
                            recordExpense.setValue('master_id', toVariant(newTariffId))
                            db.insertRecord(tableContractExpense, recordExpense)
            db.commit()
        except:
            db.rollback()
            raise
        self.renewListAndSetTo(newId)


    @QtCore.pyqtSlot()
    def on_actRemoveContract_triggered(self):
        contractId = self.tblItems.currentItemId()
        db = QtGui.qApp.db
        table = db.table('Contract')
        tableAccount = db.table('Account')
        tableQuery = table
        tableQuery = table.leftJoin(tableAccount, tableAccount['contract_id'].eq(table['id']))
        cond = [table['id'].eq(contractId)]
        accounts = db.getCount(tableQuery, tableAccount['id'], cond)
        if accounts:
            QtGui.QMessageBox.warning(self,
                                            u'Внимание',
                                            u'Удаление невозможно, по данному договору имеются сформированные реестры счетов.',
                                            QtGui.QMessageBox.Ok,
                                            QtGui.QMessageBox.Ok)
            return 0
        db.transaction()
        try:
            if self.currentPaymentSchemeId:
                tablePaymentScheme = db.table('PaymentScheme')
                tablePaymentSchemeItem = db.table('PaymentSchemeItem')
                db.deleteRecord(tableAccount, tableAccount['contract_id'].eq(tablePaymentScheme))
                db.deleteRecord(tablePaymentSchemeItem, tablePaymentSchemeItem['contract_id'].eq(contractId))

            db.deleteRecord(table, table['id'].eq(contractId))
            db.commit()
            self.tblItems.removeCurrentRow()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblItems_clicked(self, index):
        self.btnSynchronize.setEnabled(bool(self.getPriceListId()))


    @QtCore.pyqtSlot()
    def on_btnSynchronize_clicked(self):
        contractId = self.tblItems.currentItemId()
        if contractId:
            CPriceListDialog(self, contractId).exec_()
        self.renewListAndSetTo(contractId)
        self.applyFilterContract(self.order, contractId)


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxFilterContract_clicked(self, button):
        buttonCode = self.buttonBoxFilterContract.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyFilterContract(self.order, self.tblItems.currentItemId())
            self.updateFilterPaymentScheme()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilterContract()
            self.setFilterParams()
            self.getTblItemsIdList()
        self.btnSynchronize.setEnabled(bool(self.getPriceListId()))

    def exec_(self):
        self.applyFilterContract(self.order)
        return CDialogBase.exec_(self)

    def renewListAndSetTo(self, itemId=None):
        self.applyFilterContract(self.order, itemId)

    def applyFilterContract(self, order = None, itemId=None):
        self.setFilterParams()
        self.getTblItemsIdList(order, itemId)

    def setFilterParams(self):
        self.filterParams = {}
        self.filterParams['financeId'] = self.cmbFinanceSource.value()
        self.filterParams['groupingIndex'] = self.cmbGrouping.currentIndex()
        self.filterParams['grouping'] = self.cmbGrouping.text()
        self.filterParams['resolutionIndex'] = self.cmbResolution.currentIndex()
        self.filterParams['resolution'] = self.cmbResolution.text()
        self.filterParams['priceList'] = self.cmbPriceList.currentIndex()
        self.filterParams['edtBegDate'] = self.edtBegDate.date()
        self.filterParams['edtEndDate'] = self.edtEndDate.date()
        self.filterParams['orgId']  = self.cmbOrgId.value()
        self.filterParams['personId'] = self.cmbPerson.value()
        self.filterParams['number'] = self.edtNumber.text()
        self.filterParams['status'] = self.cmbStatus.currentIndex()
        self.filterParams['orgStrucutreId'] = self.cmbOrgStructure.value()
        self.updateFilterPaymentScheme()


    def getGroupingText(self):
        domain = u'\'не определено\','
        domain = self.getTextStrComboBox(domain, u'grouping')
        self.cmbGrouping.setDomain(domain)


    def getResolutionText(self):
        domain = u'\'не определено\','
        domain = self.getTextStrComboBox(domain, u'resolution')
        self.cmbResolution.setDomain(domain)


    def getTextStrComboBox(self, domain, field):
        query = QtGui.qApp.db.query(u'''SELECT DISTINCT Contract.%s FROM Contract WHERE Contract.deleted = 0'''%(field))
        while query.next():
            record = query.record()
            grouping = forceString(record.value(field))
            if grouping:
               domain +=  u'\'' + grouping + u'\','
        return domain


    def resetFilterContract(self):
        self.cmbFinanceSource.setCurrentIndex(0)
        self.cmbGrouping.setCurrentIndex(0)
        self.cmbResolution.setCurrentIndex(0)
        self.cmbPriceList.setCurrentIndex(0)
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(QtCore.QDate(currentDate.year(), 1, 1))
        self.edtEndDate.setDate(QtCore.QDate(currentDate.year(), 12, 31))

    def updateFilterPaymentScheme(self, newPaymentSchemeId = None):
        db = QtGui.qApp.db

        begDate = self.filterParams.get('edtBegDate', None)
        endDate = self.filterParams.get('edtEndDate', None)
        personId = self.filterParams.get('personId', None)
        orgId = self.filterParams.get('orgId', None)
        number = self.filterParams.get('number', None)
        status = self.filterParams.get('status', None)
        orgStructureId = self.filterParams.get('orgStructureId', None)

        tablePaymentScheme = db.table('PaymentScheme')

        cond = []
        condClinicalTest = []
        condClearing = []

        if begDate and endDate:
            cond.append(db.joinOr([db.joinAnd([tablePaymentScheme['begDate'].dateGe(begDate),
                                               tablePaymentScheme['begDate'].dateLt(endDate)]),
                                   db.joinAnd([tablePaymentScheme['begDate'].dateLe(begDate),
                                               tablePaymentScheme['endDate'].dateGt(begDate)])]))
        elif begDate:
            cond.append(tablePaymentScheme['begDate'].isNotNull())
            cond.append(db.joinOr([tablePaymentScheme['begDate'].dateGe(begDate),
                                   db.joinAnd([tablePaymentScheme['begDate'].dateLe(begDate),
                                               tablePaymentScheme['endDate'].dateGe(begDate)])]))
        elif endDate:
            cond.append(db.joinAnd([tablePaymentScheme['begDate'].isNotNull(),
                                    tablePaymentScheme['begDate'].dateLe(endDate)]))

        if orgId:
            cond.append(tablePaymentScheme['org_id'].eq(orgId))

        order = [tablePaymentScheme['number'],
                 tablePaymentScheme['begDate'],
                 tablePaymentScheme['endDate']]
        if (newPaymentSchemeId and self.contractType == 1) or not newPaymentSchemeId:
            condClinicalTest.extend(cond)
            if personId:
                condClinicalTest.append(tablePaymentScheme['person_id'].eq(personId))
            if number:
                condClinicalTest.append(tablePaymentScheme['numberProtocol'].eq(number))
            if orgStructureId:
                condClinicalTest.append(tablePaymentScheme['orgStructure_id'])
            condClinicalTest.append(tablePaymentScheme['type'].eq(0))
            self.tblClinicalTest.setIdList(db.getDistinctIdList(tablePaymentScheme, where=condClinicalTest, order=order), newPaymentSchemeId if newPaymentSchemeId else self.tblClinicalTest.currentItemId())
        if (newPaymentSchemeId and self.contractType == 2) or not newPaymentSchemeId:
            condClearing.extend(cond)
            if status > 0:
                condClearing.append(tablePaymentScheme['status'].eq(status))
            condClearing.append(tablePaymentScheme['type'].eq(1))
            self.tblClearing.setIdList(db.getDistinctIdList(tablePaymentScheme, where=condClearing, order=order), newPaymentSchemeId if newPaymentSchemeId else self.tblClearing.currentItemId())
            self.currentPaymentSchemeId = self.tabBar.currentIndex()

    def updateOrderPaymentScheme(self):
        pass

    def getTblItemsIdList(self, order = None, itemId=None):
        financeId = self.filterParams.get('financeId', None)
        groupingIndex = self.filterParams.get('groupingIndex', 0)
        grouping = self.filterParams.get('grouping', u'')
        resolutionIndex = self.filterParams.get('resolutionIndex', 0)
        resolution = self.filterParams.get('resolution', u'')
        priceList = self.filterParams.get('priceList', 0)
        edtBegDate = self.filterParams.get('edtBegDate', None)
        edtEndDate = self.filterParams.get('edtEndDate', None)
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        tableContractType = db.table('rbContractType')
        tablePaymentSchemeItem = db.table('PaymentSchemeItem')
        tablePaymentScheme = db.table('PaymentScheme')

        queryTable = tableContract.leftJoin(tableContractType, tableContractType['id'].eq(tableContract['typeId']))
        cond = [tableContract['deleted'].eq(0)]
        order = [tableContract[item] if len(item.split('.')) == 1 else item  for item in order] if isinstance(order, list) else [tableContract[order]]
        if self.contractType:
            queryTable = queryTable.innerJoin(tablePaymentSchemeItem, tablePaymentSchemeItem['contract_id'].eq(tableContract['id']))
            queryTable = queryTable.innerJoin(tablePaymentScheme, tablePaymentScheme['id'].eq(tablePaymentSchemeItem['paymentScheme_id']))
            cond.extend([tablePaymentScheme['id'].eq(self.currentPaymentSchemeId), tableContractType['code'].eq(self.contractTypeCode[self.contractType])])
            order.append(tablePaymentSchemeItem['idx'])
        else:
            cond.extend([db.joinOr([tableContractType['code'].notInlist(['clearing', 'clinicalTest']), tableContractType['code'].isNull()])])
        if financeId:
            cond.append(tableContract['finance_id'].eq(financeId))
        if groupingIndex and grouping:
            cond.append(tableContract['grouping'].like(grouping))
        if resolutionIndex and resolution:
            cond.append(tableContract['resolution'].like(resolution))
        if priceList:
            priceListId = db.getDistinctIdList(tableContract, u'priceList_id', [tableContract['deleted'].eq(0), tableContract['priceList_id'].isNotNull()])
            if priceList == 1:
                cond.append(tableContract['id'].inlist(priceListId))
            elif priceList == 2:
                cond.append(tableContract['id'].notInlist(priceListId))
        if edtBegDate and edtEndDate:
            cond.append(u'''(Contract.begDate >= %s AND Contract.begDate < %s )
OR (Contract.begDate <= %s AND Contract.endDate > %s )'''%(db.formatDate(edtBegDate), db.formatDate(edtEndDate), db.formatDate(edtBegDate), db.formatDate(edtBegDate)))
        elif edtBegDate:
            cond.append(tableContract['begDate'].isNotNull())
            cond.append(db.joinOr([tableContract['begDate'].dateGe(edtBegDate), db.joinAnd([tableContract['begDate'].dateLe(edtBegDate), tableContract['endDate'].dateGe(edtBegDate)])]))
        elif edtEndDate:
            cond.append(tableContract['begDate'].isNotNull())
            cond.append(tableContract['begDate'].dateLe(edtEndDate))
        idList = db.getDistinctIdList(queryTable, tableContract['id'], cond, order)
        self.tblItems.setIdList(idList, itemId)

        self.btnEditPaymentSchemeItem.setEnabled(bool(idList))
        self.label.setText(u'всего: %d' % len(idList))

    def setVisibleInvestFilters(self, bool):
        self.lblStructureCode.setVisible(bool)
        self.cmbOrgStructure.setVisible(bool)
        self.lblPerson.setVisible(bool)
        self.cmbPerson.setVisible(bool)
        self.lblNumber.setVisible(bool)
        self.edtNumber.setVisible(bool)

    def setVisibleNoncashFilters(self, bool):
        self.lblStatus.setVisible(bool)
        self.cmbStatus.setVisible(bool)

    def editPaymentScheme(self):
        itemId = self.tblClinicalTest.currentItemId()
        if itemId:
            dialog = CPaymentSchemeEditor(self)
            dialog.load(itemId)
            if dialog.exec_ ():
                self.setFilterParams()
                self.updateFilterPaymentScheme(itemId)

    @QtCore.pyqtSlot(int)
    def on_tabBar_currentChanged(self, index):
        self.currentPaymentSchemeId = None
        self.contractType = index
        self.item['contractTypeCode'] = self.contractTypeCode[self.contractType]
        if index == 1:
            self.currentPaymentSchemeId = self.tblClinicalTest.currentItemId()
        elif index == 2:
            self.currentPaymentSchemeId = self.tblClearing.currentItemId()
        self.tblClearing.setVisible(index == 2)
        self.tblClinicalTest.setVisible(index == 1)
        self.lblOrgName.setVisible(index)
        self.cmbOrgId.setVisible(index)
        self.btnSelectOrgName.setVisible(index)
        self.setVisibleInvestFilters(True if index == 1 else False)
        self.setVisibleNoncashFilters(True if index == 2 else False)
        self.getTblItemsIdList(self.order, self.tblItems.currentItemId())
        self.btnNew.setEnabled(bool(self.currentPaymentSchemeId) if self.contractType else True)
        self.btnCreatePaymentScheme.setVisible(index)
        self.btnEditPaymentSchemeItem.setVisible(index)
        self.btnEditPaymentSchemeItem.setVisible(index)
        self.tblItems.setColumnHidden(0, not index)
        self.tblItems.setColumnHidden(1, not index)
        self.tblItems.setColumnHidden(2, not index)

    @QtCore.pyqtSlot()
    def on_btnSelectOrgName_clicked(self):
        orgId = selectOrganisation(self, self.cmbOrgId.value(), False)
        self.cmbOrgId.update()
        if orgId:
            self.cmbOrgId.setValue(orgId)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelClinicalTest_currentRowChanged(self, current, previous):
        self.currentPaymentSchemeId = self.tblClinicalTest.itemId(current)
        if self.contractType:
            self.getTblItemsIdList(self.order, self.tblItems.currentItemId())

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelClearing_currentRowChanged(self, current, previous):
        self.currentPaymentSchemeId = self.tblClearing.itemId(current)
        if self.contractType:
            self.getTblItemsIdList(self.order, self.tblItems.currentItemId())

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblClinicalTest_doubleClicked(self, index):
        self.editPaymentScheme()
        self.modelClinicalTest.data(self.tblClinicalTest.currentIndex())

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblClearing_doubleClicked(self, index):
        self.editPaymentScheme()
        self.modelClearing.data(self.tblClearing.currentIndex())


    @QtCore.pyqtSlot()
    def on_btnCreatePaymentScheme_clicked(self):
        dialog = CPaymentSchemeEditor(self)
        if dialog.exec_():
            itemId = dialog.itemId()
            self.setFilterParams()
            self.updateFilterPaymentScheme(itemId)
            if self.btnNew.isVisible():
                self.btnNew.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnEditPaymentSchemeItem_clicked(self):
        dialog = CPaymentSchemeItemEditDialog(self, self.currentPaymentSchemeId)
        if dialog.exec_():
            dialog.save()
            self.getTblItemsIdList(self.order, self.tblItems.currentItemId())

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        if self.contractType:
            self.item['contractTypeCode'] = self.contractTypeCode[self.contractType]
            self.item['new'] = True
            dialog = CPaymentSchemeItemEditor(self)
            if not dialog.exec_():
                return
        CItemsListDialog.on_btnNew_clicked(self)
        self.item['new'] = False

#
# ##########################################################################
#

class CPaymentSchemeItemEditor(CDialogBase, Ui_PaymentSchemeItemEditor):
    def __init__(self,  parent):
        CDialogBase.__init__(self, parent)
        self.parent = parent
        self.btnNewContract = QtGui.QPushButton(u'Добавить договор', self)
        self.btnNewContract.setObjectName('btnNewContract')
        self.setupUi(self)
        self.buttonBox.addButton(self.btnNewContract, QtGui.QDialogButtonBox.ActionRole)

    @QtCore.pyqtSlot()
    def on_btnNewContract_clicked(self):
        self.parent.item['name'] = self.edtName.text()
        self.parent.item['type'] = self.cmbType.currentIndex()
        self.accept()

class CPaymentSchemeModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'PaymentSchemeItem', 'id', 'paymentScheme_id', parent)
        self.addCol(CInDocTableCol(u'Номер этапа',   'idx',   30).setReadOnly(True))
        self.addCol(CInDocTableCol(u'Наименование этапа', 'name',   30))
        self.addCol(CInDocTableCol(u'Контракт', 'contract_id',   30))
        self.setFilter('idx > 0')
        self._enableAppendLine = False
        self.parentWidget = parent

    def saveItems(self, masterId, ):
        if self._items is not None:
            db = QtGui.qApp.db
            for idx, record in enumerate(self._items):
                record = self.removeExtCols(record)
                record.setValue('idx', toVariant(idx + 1))
                db.insertOrUpdate(self._table, record)


class CPaymentSchemeItemEditDialog(CDialogBase, Ui_PaymentSchemeItemEditDialog):
    def __init__(self,  parent, paymentSchemeId = None):
        CDialogBase.__init__(self, parent)
        self.paymentSchemeId = paymentSchemeId
        self.addModels('PaymentSchemeItems', CPaymentSchemeModel(self))
        self.setupUi(self)
        self.setModels(self.tblPaymentSchemeItems, self.modelPaymentSchemeItems, self.selectionModelPaymentSchemeItems)
        self.modelPaymentSchemeItems.loadItems(paymentSchemeId)
        self.tblPaymentSchemeItems.setColumnHidden(2, True)

    def save(self):
        self.modelPaymentSchemeItems.saveItems(self.paymentSchemeId)

    @QtCore.pyqtSlot()
    def on_btnUp_clicked(self):
        oldRow = self.tblPaymentSchemeItems.currentIndex().row()
        column = self.tblPaymentSchemeItems.currentIndex().column()
        index = self.modelPaymentSchemeItems.index(oldRow, 0)
        newIndex = self.modelPaymentSchemeItems.index(oldRow - 1, 0)
        self.modelPaymentSchemeItems.upRow(oldRow)
        self.tblPaymentSchemeItems.setCurrentIndex(self.modelPaymentSchemeItems.index(oldRow - 1, column))
        self.modelPaymentSchemeItems.setData(index, (index.row() + 1), QtCore.Qt.EditRole)
        self.modelPaymentSchemeItems.setData(newIndex, (newIndex.row() + 1), QtCore.Qt.EditRole)


    @QtCore.pyqtSlot()
    def on_btnDown_clicked(self):
        oldRow = self.tblPaymentSchemeItems.currentIndex().row()
        column = self.tblPaymentSchemeItems.currentIndex().column()
        index = self.modelPaymentSchemeItems.index(oldRow, 0)
        newIndex = self.modelPaymentSchemeItems.index(oldRow + 1, 0)
        self.modelPaymentSchemeItems.downRow(oldRow)
        self.tblPaymentSchemeItems.setCurrentIndex(self.modelPaymentSchemeItems.index(oldRow + 1, column))
        self.modelPaymentSchemeItems.setData(index, (index.row() + 1), QtCore.Qt.EditRole)
        self.modelPaymentSchemeItems.setData(newIndex, (newIndex.row() + 1), QtCore.Qt.EditRole)


class CContractEditor(CItemEditorBaseDialog, Ui_ContractEditorDialog):
    def __init__(self,  parent, paymentSchemeId = None):
        CItemEditorBaseDialog.__init__(self, parent, 'Contract')
        self.parentWidget = parent
        self.paymentSchemeId = paymentSchemeId
        self.setupBtnPrintMenu()
        self.setupUi(self)
        self.btnPrint.setMenu(self.mnuBtnPrint)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Договор')
        self.contractId = None
        self.cmbBegDateReload = True
        self.cmbEndDateReload = True
        self.switchDateFilter(False)

        self.cmbRecipient.setAddNone(True, u'не задано')
        self.cmbPayer.setAddNone(True, u'не задано')

        self.modelSpecification = CSpecificationModel(self)
        self.modelSpecification.setObjectName('modelSpecification')
        self.modelTariff = CTariffModel(self)
        self.modelTariff.setObjectName('modelTariff')
        self.proxyModelTariff = CInDocTableSortFilterProxyModel(self) #QtGui.QSortFilterProxyModel(self)
        self.proxyModelTariff.setSourceModel(self.modelTariff)
        self.proxyModelTariff.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxyModelTariff.setFiterDateIntervalKeyColumns((self.modelTariff.getColIndex('begDate'),
                                                              self.modelTariff.getColIndex('endDate')))
        self.proxyModelTariff.setSortingBySourceModel(True)

        self.modelTariffExpense = CTariffExpenseModel(self)
        self.modelTariffExpense.setObjectName('modelTariffExpense')
        self.modelContingent = CContingentModel(self)
        self.modelContingent.setObjectName('modelContingent')

        self.tblSpecification.setModel(self.modelSpecification)
        self.tblTariff.setModel(self.proxyModelTariff)
#        self.tblTariff.setSelectionModel(self.selectionModelTariff)
        self.tblTariffExpense.setModel(self.modelTariffExpense)
        self.tblContingent.setModel(self.modelContingent)

        self.cmbFinance.setTable(rbFinance, True)
        self.cmbDefaultExportFormat.setTable(rbAccountExportFormat, True)
        self.cmbDefaultExportFormat.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContentsOnFirstShow)
        self.tblSpecification.addPopupDelRow()

        self.actRecalcPrice = QtGui.QAction(u'Пересчитать цену с учётом УЕТ', self)

        self.actRecalcPrice.setObjectName('actRecalcPrice')
        self.connect(self.actRecalcPrice, QtCore.SIGNAL('triggered()'), self.on_actRecalcPrice_triggered)
        self.actCheckDuplicateTariff = QtGui.QAction(u'Проверить дубликаты тарифов', self)
        self.actCheckDuplicateTariff.setObjectName('actCheckDuplicateTariff')
        self.connect(self.actCheckDuplicateTariff, QtCore.SIGNAL('triggered()'), self.on_actCheckDuplicateTariff_triggered)
        self.tblTariff.createPopupMenu([self.actRecalcPrice, self.actCheckDuplicateTariff,  '-'])
        self.tblTariff.addPopupDelRow()
        self.tblTariff.addPopupSelectAllRow()
        self.tblTariff.addPopupClearSelectionRow()
        self.tblTariff.addPopupDuplicateCurrentRow()
        self.tblTariffExpense.addPopupRowFromReport(u'rbExpenseServiceItem', u'Статьи затрат услуг')

        self.tblContingent.addPopupDelRow()
        self.btnPriceCalculator.setEnabled(False)
        self.btnIntroduceExpense.setEnabled(False)
        self.lblTableTariffRowCount.hide()
        self.cmbRecipient.setValue(QtGui.qApp.currentOrgId())

        priceValidator = QtGui.QDoubleValidator(self)
        priceValidator.setBottom(0.0)
        priceValidator.setDecimals(2)
        self.edtDeposit.setValidator(priceValidator)
        maxClientsValidator = QtGui.QIntValidator(self)
        maxClientsValidator.setBottom(0)
        self.edtMaxClients.setValidator(maxClientsValidator)

        self.setupDirtyCather()
        self.tabWidget.setCurrentIndex(0)
        self.cmbFinance.setFocus(QtCore.Qt.OtherFocusReason)

        self.tariffFilterHelper = CIncremetalFilterHelper()
        self.edtFindTariffByService.textChanged.connect(self.tariffFilterHelper.filteredStringChanged)
        # self.modelTariff.data
        self.modelTariff.dataChanged.connect(self.cmbBegDateLoad)
        self.modelTariff.dataChanged.connect(self.cmbEndDateLoad)
        self.modelTariff.rowsInserted.connect(self.cmbBegDateLoad)
        self.modelTariff.rowsInserted.connect(self.cmbEndDateLoad)
        self.modelTariff.rowsRemoved.connect(self.cmbBegDateLoad)
        self.modelTariff.rowsRemoved.connect(self.cmbEndDateLoad)
        self.cmbBegDate.currentIndexChanged.connect(self.tariffFilterHelper.filteredStringChanged)
        self.cmbEndDate.currentIndexChanged.connect(self.tariffFilterHelper.filteredStringChanged)
        self.edtOperateDate.editTextChanged.connect(self.tariffFilterHelper.filteredStringChanged)
        self.chkBegDate.toggled.connect(self.tariffFilterHelper.filteredStringChanged)
        self.chkEndDate.toggled.connect(self.tariffFilterHelper.filteredStringChanged)
        self.chkOperateDate.toggled.connect(self.tariffFilterHelper.filteredStringChanged)
        self.tariffFilterHelper.filterApplied.connect(self.applyTariffFilter)
        self.connect(self.chkBegDate, QtCore.SIGNAL('toggled(bool)'), self.on_cmbBegDate_Setup)
        self.connect(self.chkEndDate, QtCore.SIGNAL('toggled(bool)'), self.on_cmbEndDate_Setup)
        self.btnSwitchDateFilter.toggled.connect(self.switchDateFilter)
        if self.paymentSchemeId:
            lastItemRecord = QtGui.qApp.db.getRecordEx('Contract',
                                                       '*',
                                                       'Contract.id = (SELECT contract_id FROM PaymentSchemeItem WHERE paymentScheme_id = %s AND deleted = 0 ORDER BY id DESC LIMIT 1) AND deleted = 0' % self.paymentSchemeId)
            if lastItemRecord:
                self.setRecord(lastItemRecord, self.parentWidget.item['new'])
            else:
                self.cmbPayer.setValue(forceRef(QtGui.qApp.db.translate('PaymentScheme', 'id', self.paymentSchemeId, 'org_id')))
            self.contractType = forceRef(QtGui.qApp.db.translate('rbContractType', 'code', self.parentWidget.item['contractTypeCode'], 'id'))
            # self.modelTariff.setFilter('(SELECT eisLegacy FROM rbService WHERE rbService.id = service_id) = 0')
            self.modelTariff.cols()[2].setFilter('eisLegacy = 0')
        if len(self.modelSpecification.items()) == 0:
            tSpecific_Contract = QtGui.qApp.db.table('Contract_Specification')
            tableSpecification = QtGui.qApp.db.table('EventType')
            nRec = tSpecific_Contract.newRecord()
            rec = QtGui.qApp.db.getRecordEx(tableSpecification, 'id', tableSpecification['code'].eq('protocol'))
            if rec:
                nRec.setValue('eventType_id', toVariant(rec.value('id')))
                self.modelSpecification.addRecord(nRec)

        # i3166 item 6 (coz Alex want this)
        if not self.edtNumber.text():
            self.edtNumber.setText('0')

        if not self.cmbFinance.value():
            self.cmbFinance.setValue(4)



    def setupBtnPrintMenu(self):
        self.actPrintTariffInfo = QtGui.QAction(u'Сведения о тарифах для договора', self)
        self.actPrintTariffInfo.setObjectName('actPrintTariffInfo')
        self.actPrintContractByTemplate = getPrintAction(self, 'contract', u'Ещё печать')
        self.actPrintContractByTemplate.setObjectName('actPrintContractByTemplate')
        self.mnuBtnPrint = QtGui.QMenu(self)
        self.mnuBtnPrint.setObjectName('mnuBtnPrint')
        self.mnuBtnPrint.addAction(self.actPrintTariffInfo)
        self.mnuBtnPrint.addAction(self.actPrintContractByTemplate)

    def freezeHeadFields(self):
        self.cmbFinance.setDisabled(True)
        self.edtNumber.setDisabled(True)
        self.edtGrouping.setDisabled(True)
        self.edtDate.setDisabled(True)
        self.edtResolution.setDisabled(True)
        self.edtBegDate.setDisabled(True)
        self.edtEndDate.setDisabled(True)
        self.cmbRecipient.setDisabled(True)
        self.btnSelectRecipient.setDisabled(True)
        self.tabWidget.setCurrentIndex(1)


    def setRecord(self, record, synhr = False):
        if not synhr:
            CItemEditorBaseDialog.setRecord(self, record)
            contractId = self.itemId()
        else:
            contractId = forceRef(record.value('id'))
        self.contractId = contractId
        setLineEditValue(self.edtNumber,            record, 'number')

        setDateEditValue(self.edtDate,              record, 'date')

        setRBComboBoxValue(self.cmbRecipient,       record, 'recipient_id')
#        self.UpdateRecipientInfo()
        setRBComboBoxValue(self.cmbRecipientAccount,record, 'recipientAccount_id')
        setLineEditValue(self.edtRecipientKBK,      record, 'recipientKBK')
        setRBComboBoxValue(self.cmbPayer,           record, 'payer_id')
#        self.UpdatePayerInfo()
        setRBComboBoxValue(self.cmbPayerAccount,    record, 'payerAccount_id')
        setLineEditValue(self.edtPayerKBK,          record, 'payerKBK')
        setDateEditValue(self.edtBegDate,           record, 'begDate')
        setDateEditValue(self.edtEndDate,           record, 'endDate')
        setRBComboBoxValue(self.cmbFinance,         record, 'finance_id')
        setLineEditValue(self.edtGrouping,          record, 'grouping')
        setLineEditValue(self.edtResolution,        record, 'resolution')
#        self.modelOrganisationAccounts.loadItems(self.itemId())
        setRBComboBoxValue(self.cmbDefaultExportFormat, record, 'format_id')
        setCheckBoxValue(self.chkExposeUnfinishedEventVisits, record, 'exposeUnfinishedEventVisits')
        setCheckBoxValue(self.chkExposeUnfinishedEventActions, record, 'exposeUnfinishedEventActions')
        setComboBoxValue(self.cmbVisitExposition,  record, 'visitExposition')
        setComboBoxValue(self.cmbActionExposition, record, 'actionExposition')
        exposeDiscipline = forceInt(record.value('exposeDiscipline'))
        exposeByEvent, exposeByEventType, exposeByMonth, exposeByClient, exposeByInsurer, exposeByServiceArea = unpackExposeDiscipline(exposeDiscipline)
        self.chkExposeDisciplineAllInOne.setChecked(not(exposeByEvent or exposeByEventType or exposeByClient or exposeByMonth or exposeByInsurer or exposeByServiceArea))
        setCheckBoxValue(self.chkExposeByMESMaxDuration, record, 'exposeByMESMaxDuration')
        self.chkExposeDisciplineByEvent.setChecked(exposeByEvent)
        self.chkExposeDisciplineByMonth.setChecked(exposeByMonth)
        self.chkExposeDisciplineByClient.setChecked(exposeByClient)
        self.chkExposeDisciplineByEventType.setChecked(exposeByEventType)
        self.chkExposeDisciplineByServiceArea.setChecked(exposeByServiceArea)
        setSpinBoxValue(self.edtLimitationPeriod, record, 'limitationPeriod')
        setCheckBoxValue(self.chkIgnorePayStatusForJobs, record, 'ignorePayStatusForJobs')
        setCheckBoxValue(self.chkIsConsiderFederalPrice, record, 'isConsiderFederalPrice')
        self.cmbExposeDisciplineByInsurer.setCurrentIndex(exposeByInsurer)
        priceListId = forceRef(record.value('priceList_id'))
        if priceListId:
            self.cmbPriceList.setValue(priceListId)
        else:
            if contractId:
                db = QtGui.qApp.db
                tableContract = db.table('Contract')
                priceListRecord = db.getRecordEx(tableContract, [tableContract['id']], [tableContract['deleted'].eq(0), tableContract['priceList_id'].eq(contractId)])
                dependantId = forceRef(priceListRecord.value('id')) if priceListRecord else None
                if dependantId:
                    self.cmbPriceList.setValue(contractId)
        setDoubleBoxValue(self.edtCoefficient, record, 'coefficient')
        setDoubleBoxValue(self.edtCoefficientEx, record, 'coefficientEx')
        setDoubleBoxValue(self.edtCoefficientEx2, record, 'coefficientEx2')
        setLineEditValue(self.edtOrgCategory,  record,  'orgCategory')
        setDoubleBoxValue(self.edtRegionalTariffRegulationFactor, record,  'regionalTariffRegulationFactor')
        setLineEditValue(self.edtDeposit, record, 'deposit')
        setLineEditValue(self.edtMaxClients, record, 'maxClients')

        self.modelSpecification.loadItems(contractId)
        self.modelContingent.loadItems(contractId)
        if not synhr:
            self.modelTariff.loadItems(contractId)
            self.lblTableTariffRowCount.setText(u'Количество записей: %s' % self.proxyModelTariff.rowCount())


    def getRecord(self, record = None):
        if record is None:
            record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtNumber,            record, 'number')
        getDateEditValue(self.edtDate,              record, 'date')
        getRBComboBoxValue(self.cmbRecipient,       record, 'recipient_id')
        getRBComboBoxValue(self.cmbRecipientAccount,record, 'recipientAccount_id')
        getLineEditValue(self.edtRecipientKBK,      record, 'recipientKBK')
        getRBComboBoxValue(self.cmbPayer,           record, 'payer_id')
        getRBComboBoxValue(self.cmbPayerAccount,    record, 'payerAccount_id')
        getLineEditValue(self.edtPayerKBK,          record, 'payerKBK')
        getDateEditValue(self.edtBegDate,           record, 'begDate')
        getDateEditValue(self.edtEndDate,           record, 'endDate')
        getRBComboBoxValue(self.cmbFinance,         record, 'finance_id')
        getLineEditValue(self.edtGrouping,          record, 'grouping')
        getLineEditValue(self.edtResolution,        record, 'resolution')
        getRBComboBoxValue(self.cmbDefaultExportFormat, record, 'format_id')
        getCheckBoxValue(self.chkExposeUnfinishedEventVisits, record, 'exposeUnfinishedEventVisits')
        getCheckBoxValue(self.chkExposeUnfinishedEventActions, record, 'exposeUnfinishedEventActions')
        getCheckBoxValue(self.chkIgnorePayStatusForJobs, record, 'ignorePayStatusForJobs')
        getCheckBoxValue(self.chkIsConsiderFederalPrice, record, 'isConsiderFederalPrice')
        getComboBoxValue(self.cmbVisitExposition,   record, 'visitExposition')
        getComboBoxValue(self.cmbActionExposition,  record, 'actionExposition')
        if self.chkExposeDisciplineAllInOne.isChecked():
            exposeDiscipline = 0
        else:
            exposeDiscipline = packExposeDiscipline(
                self.chkExposeDisciplineByEvent.isChecked(),
                self.chkExposeDisciplineByEventType.isChecked(),
                self.chkExposeDisciplineByMonth.isChecked(),
                self.chkExposeDisciplineByClient.isChecked(),
                self.cmbExposeDisciplineByInsurer.currentIndex(),
                self.chkExposeDisciplineByServiceArea.isChecked()
            )
        record.setValue('exposeDiscipline', toVariant(exposeDiscipline))
        getCheckBoxValue(self.chkExposeByMESMaxDuration, record, 'exposeByMESMaxDuration')
        getSpinBoxValue(self.edtLimitationPeriod, record, 'limitationPeriod')
        getRBComboBoxValue(self.cmbPriceList, record, 'priceList_id')
#        record.setValue('priceList_id', toVariant(self.cmbPriceList.value()))
        getDoubleBoxValue(self.edtCoefficient, record, 'coefficient')
        getDoubleBoxValue(self.edtCoefficientEx, record, 'coefficientEx')
        getDoubleBoxValue(self.edtCoefficientEx2, record, 'coefficientEx2')
        getLineEditValue(self.edtOrgCategory,  record,  'orgCategory')
        getDoubleBoxValue(self.edtRegionalTariffRegulationFactor, record,  'regionalTariffRegulationFactor')
        getLineEditValue(self.edtDeposit, record, 'deposit')
        getLineEditValue(self.edtMaxClients, record, 'maxClients')
        if self.paymentSchemeId:
            record.setValue('typeId', toVariant(self.contractType))
        self.lblCounterValue.setText(forceString(record.value('counterValue')))
        return record


    def save(self):
        try:
            prevId = self.itemId()
            db = QtGui.qApp.db
            recordList = [self.getRecord()] if not self._record or not self.paymentSchemeId else []
            currentId = forceRef(self._record.value('id'))
            if self.isDirty() and self.paymentSchemeId:
                recordList.extend(db.getRecordList('PaymentSchemeItem AS p INNER JOIN Contract AS c ON c.id = p.contract_id', 'c.*', 'p.paymentScheme_id = %s AND c.deleted = 0 AND p.deleted = 0' % (self.paymentSchemeId)))
            db.transaction()
            try:
                for index, record in enumerate(recordList):
                    newRecord = not forceRef(record.value('id'))
                    if index:
                        self.getRecord(record)
                    else:
                        useCounter = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'useCounterInContracts', QtCore.QVariant()))
                        # Для договоров и для счетов используется единый счетчик
                        if newRecord and useCounter:
                                counterId = forceRef(db.translate('rbCounter', 'code', 'contract', 'id'))
                                counterValue = getContractDocumentNumber(counterId)
                                record.setValue('counterValue', toVariant(counterValue))
                    id = db.insertOrUpdate(db.table(self._tableName), record)
                    if newRecord:
                        currentId = id
                    if self.paymentSchemeId:
                        if newRecord:
                            self.savePaymentSchemeItem(id)
                        # paymentSchemeRecord = db.getRecordEx('PaymentScheme', '*', 'PaymentScheme.id = %s' % self.paymentSchemeId)
                        # paymentSchemeRecord.setValue('total', toVariant(forceDouble(paymentSchemeRecord.value('total')) - forceDouble(record.value('deposit'))))
                        # db.insertOrUpdate(db.table('PaymentScheme'), paymentSchemeRecord)
                    self.saveInternals(id, not id == currentId)
                db.commit()
            except:
                db.rollback()
                self.setItemId(prevId)
                raise
            self.setItemId(currentId)
            self.afterSave()
            return currentId
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical( self,
                                        u'',
                                        unicode(e),
                                        QtGui.QMessageBox.Close)
            return None

    def saveInternals(self, id, synchr = False):
        self.saveItemsModel(self.modelSpecification, id)
        self.modelTariffExpense.saveItems()
        self.saveItemsModel(self.modelContingent, id)
        if not synchr:
            self.modelTariff.saveItems(id)

    def saveItemsModel(self, model, id):
        for record in model._items:
            record.setValue('id', toVariant(None))
        model.saveItems(id)

    def savePaymentSchemeItem(self, id):
        db = QtGui.qApp.db
        table = db.table('PaymentSchemeItem')
        lastIdx= forceInt(db.translate(table, 'paymentScheme_id', self.paymentSchemeId, 'MIN(idx)' if self.parentWidget.item['type'] else 'MAX(idx)'))
        record = db.record('PaymentSchemeItem')
        record.setValue('idx', toVariant((lastIdx - 1) if lastIdx < 0 else -1if self.parentWidget.item['type'] else (lastIdx + 1)))
        record.setValue('name', toVariant(self.parentWidget.item['name']))
        record.setValue('type', toVariant(self.parentWidget.item['type']))
        record.setValue('paymentScheme_id', toVariant(self.paymentSchemeId))
        record.setValue('contract_id', toVariant(id))
        db.insertOrUpdate(table, record)


    def checkDataEntered(self):
        result = True
        if self.paymentSchemeId:
            record = QtGui.qApp.db.getRecordEx('PaymentScheme', ['begDate', 'endDate'], 'id = %s' % self.paymentSchemeId)
            result = result and ((forceDate(record.value('begDate')) <= forceDate(self.edtBegDate.date()) and forceDate(record.value('endDate')) >= forceDate(self.edtEndDate.date())) or self.checkInputMessage(u'корректный срок действия договора', True, self.edtBegDate))
        result = result and (forceStringEx(self.edtNumber.text()) or  self.checkInputMessage(u'номер', False, self.edtNumber))
        result = result and (self.edtDate.date().isValid()    or self.checkInputMessage(u'дату', False, self.edtDate))
        result = result and (self.cmbRecipient.value()        or self.checkInputMessage(u'получателя', False, self.cmbRecipient))
        result = result and (self.cmbRecipientAccount.value() or self.checkInputMessage(u'рассчетный счет получателя', False, self.cmbRecipientAccount))
        result = result and (self.cmbPayer.value()            or self.checkInputMessage(u'плательщика', False, self.cmbPayer))
        result = result and ((self.cmbPayerAccount.value() or self.paymentSchemeId)     or  self.checkInputMessage(u'рассчетный счет плательщика', False, self.cmbPayerAccount))
        result = result and (forceStringEx(self.edtGrouping.text())   or self.checkInputMessage(u'группу договоров', True, self.edtGrouping))
        result = result and (forceStringEx(self.edtResolution.text()) or self.checkInputMessage(u'основание', True, self.edtResolution))
        return result


    def UpdateRecipientInfo(self):
        id = self.cmbRecipient.value()
        orgInfo = getOrganisationInfo(id)
        self.edtRecipientINN.setText(orgInfo.get('INN', ''))
        self.edtRecipientOGRN.setText(orgInfo.get('OGRN', ''))
        self.cmbRecipientAccount.setOrgId(id)


    def UpdateRecipientAccountInfo(self):
        id = self.cmbRecipientAccount.value()
        accountInfo = getAccountInfo(id)
        self.edtRecipientBank.setText(accountInfo.get('shortBankName', ''))


    def UpdatePayerInfo(self):
        id = self.cmbPayer.value()
        orgInfo = getOrganisationInfo(id)
        self.edtPayerINN.setText(orgInfo.get('INN', ''))
        self.edtPayerOGRN.setText(orgInfo.get('OGRN', ''))
        self.cmbPayerAccount.setOrgId(id)


    def UpdatePayerAccountInfo(self):
        id = self.cmbPayerAccount.value()
        accountInfo = getAccountInfo(id)
        self.edtPayerBank.setText(accountInfo.get('shortBankName', ''))

    def addTariff(self):
        # model = self.tblTariff.model()
        dialog = CServiceSelectedDialog(self, self.contractId)
        dialog.setContractId(self.contractId)
        if dialog.exec_():
            self.modelTariff._extColsPresent = True
            for serviceId, record in dialog.getSelectedServiceList():
                self.modelTariff.addRecord(record)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_F9 and self.tabWidget.indexOf(self.tabTariff) == self.tabWidget.currentIndex():
            self.addTariff()


    @QtCore.pyqtSlot(int)
    def on_cmbRecipient_currentIndexChanged(self, index):
        self.UpdateRecipientInfo()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblTariff_clicked(self, index):
        self.modelTariffExpense.saveItems()
        self.loadTariffExpense(index)


    def loadTariffExpense(self, currentIndex):
        currentIndex = self.proxyModelTariff.mapToSource(currentIndex)
        if currentIndex.isValid():
            row = currentIndex.row()
            if row in xrange(len(self.modelTariff.items())):
                record = self.modelTariff.items()[row]
                tariffId = forceRef(record.value('id'))
                if tariffId:
                    self.modelTariffExpense.loadItems(tariffId, record)


    @QtCore.pyqtSlot()
    def on_btnSelectRecipient_clicked(self):
        orgId = selectOrganisation(self, self.cmbRecipient.value(), False)
        self.cmbRecipient.update()
        self.cmbRecipientAccount.update()
        if orgId:
            self.setIsDirty()
            self.cmbRecipient.setValue(orgId)


    @QtCore.pyqtSlot(int)
    def on_cmbRecipientAccount_currentIndexChanged(self, index):
        self.UpdateRecipientAccountInfo()


    @QtCore.pyqtSlot(int)
    def on_cmbPayer_currentIndexChanged(self, index):
        self.UpdatePayerInfo()


    @QtCore.pyqtSlot()
    def on_btnSelectPayer_clicked(self):
        orgId = selectOrganisation(self, self.cmbPayer.value(), False)
        self.cmbPayer.update()
        self.cmbPayerAccount.update()
        if orgId:
            self.setIsDirty()
            self.cmbPayer.setValue(orgId)


    @QtCore.pyqtSlot(int)
    def on_cmbPayerAccount_currentIndexChanged(self, index):
        self.UpdatePayerAccountInfo()


    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        # мотивация изменения импорта тарифов:
        # импорт через изменение БД обладает
        # двумя дефектами:
        # 1) нарушается логика работы редактора (после Cancel данные оказываются изменёнными)
        # 2) в случае каких-либо проблем с импортом данные оказываются частично изменёнными.
        dbImport = False
        regionCode = QtGui.qApp.defaultKLADR()[:2]
        if regionCode == '51':
            importProc = ImportTariffsR51
        elif regionCode in ('50', '77'):
            dbImport = True
            importProc = ImportTariffsR77
        elif regionCode == '67':
            importProc = ImportTariffsR67
        elif regionCode == '61':
            importProc = ImportTariffsR61
        elif regionCode == '23':
            importProc = ImportTariffsR23
        elif regionCode == '91': # Крым
            importProc = ImportTariffsR85
        elif self.cmbDefaultExportFormat.code() == '6':
            importProc = ImportTariffsINFIS
        else:
            importProc = ImportTariffs

        if dbImport:
            importProc(self, self.itemId())
            self.modelTariff.loadItems(self.itemId())
        else:
            ok, tariffList = importProc(self, self.itemId(), self.edtBegDate.date(), self.edtEndDate.date(), self.modelTariff.items())
            if ok:
                self.modelTariff.setItems(tariffList)
                self.modelTariff.reset()


    @QtCore.pyqtSlot()
    def on_btnImportXML_clicked(self):
        items = ImportTariffsXML(self, self.modelTariff.items())
        self.modelTariff.setItems(items)


    @QtCore.pyqtSlot()
    def on_btnExportXML_clicked(self):
        ExportTariffsXML(self, self.modelTariff.items())

    @QtCore.pyqtSlot()
    def on_btnExportDBF_clicked(self):
        ExportTariffsR23(self, self.modelTariff.items(), self.cmbRecipient.value())

    @QtCore.pyqtSlot()
    def on_actPrintTariffInfo_triggered(self):
        CTariffsReport(self, self.itemId()).oneShot({})

    @QtCore.pyqtSlot(int)
    def on_actPrintContractByTemplate_printByTemplate(self, templateId):
        context = CInfoContext()
        contract = context.getInstance(CContractInfo, self.itemId())
        data = {'contract': contract,
               }
        applyTemplate(self, templateId, data)


    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        if index == 1:
            self.btnPriceCalculator.setEnabled(QtGui.qApp.userHasRight(urAccessPriceCalculate))
            self.btnIntroduceExpense.setEnabled(QtGui.qApp.userHasRight(urAccessPriceCalculate))
            self.lblTableTariffRowCount.show()
        else:
            self.btnPriceCalculator.setEnabled(False)
            self.btnIntroduceExpense.setEnabled(False)
            self.lblTableTariffRowCount.hide()


    @QtCore.pyqtSlot()
    def on_btnPriceCalculator_clicked(self):
        rows = []
        indexList = self.tblTariff.selectedIndexes()
        for index in indexList:
            sourceIndex = self.proxyModelTariff.mapToSource(index)
            row = sourceIndex.row()
            if (row not in rows) and row in xrange(self.modelTariff.rowCount()):
                rows.append(row)
        setupDialog = CPriceCoefficientEditor(self)
        setupDialog.lblSelectionRows.setText(u'Выделено строк: %d'%(len(rows)))
        if setupDialog.exec_():
            coefficients = setupDialog.params()
            for coefficient, edt in zip(coefficients, (self.edtCoefficient, self.edtCoefficientEx, self.edtCoefficientEx2)):
                if coefficient is not None:
                    edt.setValue(coefficient)
            if any(coefficient is not None for coefficient in coefficients) and rows:
                QtGui.qApp.callWithWaitCursor(self, self.updatePricesInSelectedRecords, coefficients, rows)
        else:
            self.tblTariff.clearSelection()


    def getPriceListId(self, contractId):
        if contractId:
            db = QtGui.qApp.db
            table = db.table('Contract')
            record = db.getRecordEx(table, [table['priceList_id']], [table['deleted'].eq(0), table['priceList_id'].eq(contractId)])
            return forceRef(record.value('priceList_id')) if record else None
        return None


    @QtCore.pyqtSlot()
    def on_btnIntroduceExpense_clicked(self):
        rows = []
        indexList = self.tblTariff.selectedIndexes()
        for index in indexList:
            sourceIndex = self.proxyModelTariff.mapToSource(index)
            row = sourceIndex.row()
            if (row not in rows) and row in xrange(self.modelTariff.rowCount()):
                rows.append(row)
        if rows:
            setupDialog = CIntroducePercentDialog(self)
            setupDialog.modelIntroducePercent.loadData()
            setupDialog.lblSelectionRows.setText(u'Выделено строк: %d'%(len(rows)))
            if setupDialog.exec_():
                records = setupDialog.modelIntroducePercent.items
                sumPercent = 0
                for record in records:
                    sumPercent += forceDouble(record[1])
                isCorrect = sumPercent < 100.5 or self.checkValueMessage(u'Сумма по процентам превышает 100!', True, self)
                if isCorrect:
                    QtGui.qApp.callWithWaitCursor(self, self.updateTariffExpense, rows, records)
                    self.loadTariffExpense(self.tblTariff.currentIndex())
            else:
                self.tblTariff.clearSelection()


    def updateTariffExpense(self, rows, records):
        db = QtGui.qApp.db
        db.transaction()
        try:
            tableExpense = db.table('Contract_CompositionExpense')
            for row in rows:
                item = self.modelTariff.items()[row]
                if item:
                    tariffId = forceRef(item.value('id'))
                    if tariffId:
                        db.deleteRecord(tableExpense, [tableExpense['master_id'].eq(tariffId)])
                        for record in records:
                            rbTableId = record[2]
                            percent = record[1]
                            newRecord = tableExpense.newRecord()
                            newRecord.setValue('master_id', toVariant(tariffId))
                            newRecord.setValue('rbTable_id', toVariant(rbTableId))
                            newRecord.setValue('percent', toVariant(percent))
                            db.insertRecord(tableExpense, newRecord)
            db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise
        self.tblTariff.clearSelection()

    def fixCheckboxes(self, widget, newValue):
        def uncheck(widget):
            if isinstance(widget, QtGui.QComboBox):
                widget.setCurrentIndex(0)
            else:
                widget.setChecked(False)

        def checked(widget):
            return widget.currentIndex() if isinstance(widget, QtGui.QComboBox) else widget.isChecked()

        widgets = [
            self.chkExposeDisciplineAllInOne,
            self.chkExposeDisciplineByEvent,
            self.chkExposeDisciplineByEventType,
            self.chkExposeDisciplineByMonth,
            self.chkExposeDisciplineByClient,
            self.chkExposeDisciplineByServiceArea,
            self.cmbExposeDisciplineByInsurer
        ]
        allowedGroups = [
            [self.chkExposeDisciplineByServiceArea, self.chkExposeDisciplineByEventType, self.cmbExposeDisciplineByInsurer],
            [self.chkExposeDisciplineByMonth, self.chkExposeDisciplineByClient]
        ]

        if newValue:
            if widget in widgets:
                widgets.remove(widget)
            for group in allowedGroups:
                if widget in group:
                    for otherWidget in group:
                        if otherWidget in widgets:
                            widgets.remove(otherWidget)

            for otherWidget in widgets:
                uncheck(otherWidget)
        elif all(map(lambda w: not checked(w), widgets)):
            self.chkExposeDisciplineAllInOne.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkExposeDisciplineAllInOne_clicked(self, checked):
        self.fixCheckboxes(self.chkExposeDisciplineAllInOne, checked)

    @QtCore.pyqtSlot(bool)
    def on_chkExposeDisciplineByEvent_clicked(self, checked):
        self.fixCheckboxes(self.chkExposeDisciplineByEvent, checked)

    @QtCore.pyqtSlot(bool)
    def on_chkExposeDisciplineByEventType_clicked(self, checked):
        self.fixCheckboxes(self.chkExposeDisciplineByEventType, checked)

    @QtCore.pyqtSlot(bool)
    def on_chkExposeDisciplineByMonth_clicked(self, checked):
        self.fixCheckboxes(self.chkExposeDisciplineByMonth, checked)

    @QtCore.pyqtSlot(bool)
    def on_chkExposeDisciplineByClient_clicked(self, checked):
        self.fixCheckboxes(self.chkExposeDisciplineByClient, checked)

    @QtCore.pyqtSlot(int)
    def on_cmbExposeDisciplineByInsurer_currentIndexChanged(self, index):
        self.fixCheckboxes(self.cmbExposeDisciplineByInsurer, (index != 0))

    @QtCore.pyqtSlot(bool)
    def on_chkExposeDisciplineByServiceArea_clicked(self, checked):
        self.fixCheckboxes(self.chkExposeDisciplineByServiceArea, checked)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbPriceList_editTextChanged(self, index):
        contractId = self.itemId()
        priceListId = self.cmbPriceList.value()
        if not priceListId:
            priceListId = self.getPriceListId(contractId)
            if priceListId and priceListId == contractId:
                self.cmbPriceList.setValue(priceListId)


    @QtCore.pyqtSlot()
    def on_actRecalcPrice_triggered(self):
        isDirty = False
        rows = []
        indexList = self.tblTariff.selectedIndexes()
        for index in indexList:
            sourceIndex = self.proxyModelTariff.mapToSource(index)
            row = sourceIndex.row()
            if (row not in rows) and row in xrange(self.modelTariff.rowCount()):
                rows.append(row)

        for r in rows:
            record = self.modelTariff.items()[r]
            uet = forceDouble(record.value('uet'))

            if uet > 0.0:
                isDirty = True
                price = forceDouble(record.value('price'))
                record.setValue('price', toVariant(price*uet))

        if isDirty:
            self.modelTariff.emitDataChanged()
            self.tblTariff.clearSelection()

    @QtCore.pyqtSlot()
    def on_actCheckDuplicateTariff_triggered(self):
        dialog = CDuplicateTariff(self, self.modelTariff._items)
        if dialog.exec_():
            newTariffList = dialog.getTariffList()
            if newTariffList:
                self.modelTariff.setItems(dialog.getTariffList())
                self.setIsDirty(True)

    @QtCore.pyqtSlot()
    def applyTariffFilter(self):
        self.proxyModelTariff.clearFilterFixedString()
        self.proxyModelTariff.addFilterStartsWithString(self.modelTariff.getColIndex('service_id'), self.edtFindTariffByService.text())
        if self.cmbBegDate.isEnabled() and self.cmbBegDate.currentIndex():
            self.proxyModelTariff.addFilterFixedString(self.modelTariff.getColIndex('begDate'), self.cmbBegDate.currentText()
                                                       if not self.cmbBegDate.currentIndex() == 1 else u'')
        if self.cmbEndDate.isEnabled()and self.cmbEndDate.currentIndex():
            self.proxyModelTariff.addFilterFixedString(self.modelTariff.getColIndex('endDate'), self.cmbEndDate.currentText()
                                                       if not self.cmbEndDate.currentIndex() == 1 else u'')

        self.proxyModelTariff.addFilterDateInInterval(self.edtOperateDate.currentText()
                                                      if self.edtOperateDate.isEnabled() else u'')
        self.proxyModelTariff.invalidate()
        self.lblTableTariffRowCount.setText(u'Количество записей: %s' % self.proxyModelTariff.rowCount())

    def cmbDateSetup(self, field):
        dateDict = {}
        for item in self.modelTariff.items():
            value = item.value(field)
            name = forceDate(value)
            if not name in dateDict.keys() and name:
                dateDict[name] = value
        list = [((0, u'Все даты', QtCore.QVariant())),
                ((1, u'Не указано', QtCore.QVariant()))]
        for i, name in enumerate(sorted(dateDict.keys())):
            list.append((i + 2, forceString(name), dateDict[name]))
        return list

    def cmbBegDateLoad(self):
        if self.contractId:
            self.cmbBegDate.setEnabled(True)
            currentText = self.cmbBegDate.currentText()
            currentIndex = 0
            self.cmbBegDate.clear()
            list = self.cmbDateSetup('begDate')
            for it, name, value in list:
                self.cmbBegDate.insertItem(it, name, value)
                if currentText == name:
                    currentIndex = it
            self.cmbBegDateReload = False
            self.cmbBegDate.setCurrentIndex(currentIndex)

    def cmbEndDateLoad(self):
        if self.contractId:
            self.cmbEndDate.setEnabled(True)
            currentText = self.cmbBegDate.currentText()
            currentIndex = 0
            self.cmbEndDate.clear()
            list = self.cmbDateSetup('endDate')
            for it, name, value in list:
                self.cmbEndDate.insertItem(it, name, value)
                if currentText == name:
                    currentIndex = it
            self.cmbEndDateReload = False
            self.cmbEndDate.setCurrentIndex(currentIndex)

    @QtCore.pyqtSlot(bool)
    def on_cmbBegDate_Setup(self, enable):
        if enable and self.cmbBegDateReload:
            self.cmbBegDateLoad()
        else:
            self.cmbBegDate.clear()
            self.cmbBegDateReload = True
            self.cmbBegDate.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def on_cmbEndDate_Setup(self, enable):
        if enable and self.cmbEndDateReload:
            self.cmbEndDateLoad()
        else:
            self.cmbEndDate.clear()
            self.cmbEndDateReload = True
            self.cmbEndDate.setDisabled(True)

    @QtCore.pyqtSlot(bool)
    def switchDateFilter(self, value):
        if not value:
            self.chkOperateDate.setChecked(False)
            self.switchDateFilter
            self.stkwDateFilter.setCurrentIndex(0)
            self.btnSwitchDateFilter.setText(u'Режим "Период"')
        else:
            self.chkBegDate.setChecked(False)
            self.chkEndDate.setChecked(False)
            self.stkwDateFilter.setCurrentIndex(1)
            self.btnSwitchDateFilter.setText(u'Режим "Дата"')

    @QtCore.pyqtSlot(bool)
    def on_chkOperateDate_clicked(self, checked):
        self.edtOperateDate.setEnabled(checked)


    def updatePricesInSelectedRecords(self, coefficients, rows):
        for row in rows:
            record = self.modelTariff.items()[row]
            CPriceListDialog.updateTariffToCoefficient(record, coefficients)
        self.modelTariff.emitDataChanged()
        self.tblTariff.clearSelection()

#
# ###################################################################
#



class CSpecificationModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Contract_Specification', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Событие',  'eventType_id',  30, 'EventType', filter='deleted = 0', addNone=False))


#
# ###################################################################
#




class CTariffExpenseModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Contract_CompositionExpense', 'id', 'master_id', parent)
        self.parent=parent
        self.addCol(CRBInDocTableCol(u'Затрата', 'rbTable_id',  30, 'rbExpenseServiceItem', showFields=CRBComboBox.showCodeAndName)).setReadOnly(True)
        self.addCol(CFloatInDocTableCol(u'Процент', 'percent', 2, precision=2))
        self.addExtCol(CFloatInDocTableCol(u'Сумма', 'sum', 8, precision=2), QtCore.QVariant.Double)
        self.masterId = None
        self.parent = parent
        self.parentItems = []


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if 0 <= row < len(self.items()):
                if value.isNull():
                    return False
                if column == 1:
                    record = self.items()[row]
                    record.setValue('percent', toVariant(forceDouble(value)))
                    sum = 0
                    if self.parentItems:
                        percent = forceDouble(record.value('percent'))
                        parentSum = forceDouble(self.parentItems.value('price'))
                        sum = self.getSum(percent, parentSum)
                        record.setValue('sum', toVariant(sum))
                        self.emitCellChanged(row, column)
                        return True
                elif column == 2:
                    record = self.items()[row]
                    record.setValue('sum', toVariant(forceDouble(value)))
                    percent = 0
                    if self.parentItems:
                        sum = forceDouble(record.value('sum'))
                        parentSum = forceDouble(self.parentItems.value('price'))
                        percent = self.getPercent(sum, parentSum)
                        record.setValue('percent', toVariant(percent))
                        self.emitCellChanged(row, column)
                        return True
        return False


    def flags(self, index):
        result = CInDocTableModel.flags(self, index)
        column = index.column()
        row = index.row()
        expenseTypeId = None
        if 0 <= row < len(self.items()):
            record = self.items()[row]
            expenseTypeId = forceRef(record.value('rbTable_id'))
        if expenseTypeId and column != 0:
            result |= QtCore.Qt.ItemIsEditable
        return result



    def getEmptyRecord(self):
        record = CInDocTableModel.getEmptyRecord(self)
        record.setValue('master_id', toVariant(self.masterId))
        return record


    def loadItems(self, masterId, parentItems):
        self.parentItems = parentItems
        self.masterId = masterId
        if self.masterId:
            CInDocTableModel.loadItems(self, self.masterId)
            for row, item in enumerate(self.items()):
                newRecord = self.getEmptyRecord()
                copyFields(newRecord, item)
                sum = 0
                if self.parentItems:
                    percent = forceDouble(newRecord.value('percent'))
                    parentSum = forceDouble(self.parentItems.value('price'))
                    sum = self.getSum(percent, parentSum)
                newRecord.setValue('sum', toVariant(sum))
                self.items()[row] = newRecord
        else:
            self.setItems([])
        self.reset()


    def saveItems(self):
        if self.masterId:
            sumPercent = 0
            for item in self.items():
                sumPercent += forceDouble(item.value('percent'))
            isCorrect = sumPercent < 100.5 or self.parent.checkValueMessage(u'Сумма по процентам превышает 100!', True, self.parent)
            if isCorrect:
                CInDocTableModel.saveItems(self, self.masterId)


    def getSum(self, percent, parentSum):
        sum = 0
        if parentSum:
            if percent:
                sum = (parentSum * percent)/100.0
        return sum


    def getPercent(self, sum, parentSum):
        percent = 0
        if parentSum:
            percent = (sum*100)/parentSum
        return percent

#
# ###################################################################
#

class CContingentModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Contract_Contingent', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип прикрепления', 'attachType_id', 30, 'rbAttachType'))
        self.addCol(COrgInDocTableCol(u'Занятость', 'org_id', 30))
        self.addCol(CRBInDocTableCol(u'Соц.статус', 'socStatusType_id', 30, 'rbSocStatusType'))
        self.addCol(CInsurerInDocTableCol(u'СМО', 'insurer_id', 50))
        self.addCol(CRBInDocTableCol(u'Тип страхования', 'policyType_id', 30, 'rbPolicyType'))
        self.addCol(CEnumInDocTableCol(u'Зона обслуживания', 'serviceArea', 10, [u'Любая',
        u'Нас.пункт', u'Нас.пункт+область', u'Область', u'Область+Другие', u'Другие']))
        self.addCol(CEnumInDocTableCol(u'Пол', 'sex', 3, [u'', u'М', u'Ж']))
        self.addCol(CInDocTableCol(u'Возраст', 'age', 8))


#
# ###################################################################
#

class CTariffsReport(CReport):
    def __init__(self, parent,  contractId):
        CReport.__init__(self, parent)
        self.contractInfo = getContractInfo(contractId)
        self.contractId = contractId
        contractNumber = self.contractInfo.number if self.contractInfo.number else '-'
        contractDate = self.contractInfo.date.toString('dd.MM.yyyy')
        self.setTitle(u'Сведения о тарифах для договора №%s от %s' % (contractNumber, contractDate))


    def getSetupDialog(self, parent):
        return None


    def build(self, params):
        query = self.createQuery()
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('5%', [u'№ строки',                        '1' ], CReportBase.AlignRight),
                        ('5%', [u'Событие',                         '2' ], CReportBase.AlignLeft),
                        ('10%',[u'Тарифицируется',                  '3' ], CReportBase.AlignLeft),
                        ('10%',[u'Услуга',                          '4' ], CReportBase.AlignLeft),
                        ('10%',[u'Дата начала',                     '5' ], CReportBase.AlignCenter),
                        ('10%',[u'Дата окончания',                  '6' ], CReportBase.AlignCenter),
                        ('5%', [u'Пол',                             '7' ], CReportBase.AlignCenter),
                        ('10%',[u'Возраст',                         '8' ], CReportBase.AlignCenter),
                        ('5%', [u'Ед.уч.',                          '9' ], CReportBase.AlignLeft),
                        ('5%', [u'Количество',                      '10'], CReportBase.AlignRight),
                        ('5%', [u'УЕТ',                             '11'], CReportBase.AlignRight),
                        ('5%', [u'Цена',                            '12'], CReportBase.AlignRight),
                        ('10%',[u'Начало второго тарифа',           '13'], CReportBase.AlignRight),
                        ('10%',[u'Сумма второго тарифа',            '14'], CReportBase.AlignRight),
                        ('10%',[u'Цена второго тарифа',             '15'], CReportBase.AlignRight),

                        ('10%',[u'Начало третьего тарифа',          '16'], CReportBase.AlignRight),
                        ('10%',[u'Сумма третьего тарифа',           '17'], CReportBase.AlignRight),
                        ('10%',[u'Цена третьего тарифа',            '18'], CReportBase.AlignRight),
                       ]

        table = createTable(cursor, tableColumns)
        rowNum = 0

        while query.next():
            record = query.record()
            i = table.addRow()
            rowNum += 1
            eventTypeCode = forceString(record.value('eventType_code'))
            eventTypeName = forceString(record.value('eventType_name'))
            eventTypeStr = u'%s|%s' % (eventTypeCode,  eventTypeName) if eventTypeCode or eventTypeName else  u'не задано'
            serviceCode = forceString(record.value('service_code'))
            serviceName = forceString(record.value('service_name'))
            serviceStr = u'%s|%s' % (serviceCode,  serviceName) if serviceCode or serviceName else  u'не задано'

            table.setText(i, 0, rowNum)
            table.setText(i, 1, eventTypeStr)
            table.setText(i, 2, CTariffModel.tariffTypeNames[forceInt(record.value('tariffType'))])
            table.setText(i, 3, serviceStr)
            table.setText(i, 4, forceString(record.value('begDate')))
            table.setText(i, 5, forceString(record.value('endDate')))
            table.setText(i, 6, formatSex(forceInt(record.value('sex'))))
            table.setText(i, 7, forceString(record.value('age')))
            table.setText(i, 8, forceString(record.value('unit_name')))
            table.setText(i, 9, forceString(record.value('amount')))
            table.setText(i, 10, forceString(record.value('uet')))
            table.setText(i, 11, forceString(record.value('price')))
            table.setText(i, 12, forceString(record.value('frag1Start')))
            table.setText(i, 13, forceString(record.value('frag1Sum')))
            table.setText(i, 14, forceString(record.value('frag1Price')))
            table.setText(i, 15, forceString(record.value('frag2Start')))
            table.setText(i, 16, forceString(record.value('frag2Sum')))
            table.setText(i, 17, forceString(record.value('frag2Price')))
        return doc


    def createQuery(self):
        db = QtGui.qApp.db
        stmt = """
        SELECT  Contract_Tariff.tariffType, Contract_Tariff.begDate, Contract_Tariff.endDate,
                Contract_Tariff.sex, Contract_Tariff.age, Contract_Tariff.amount, Contract_Tariff.uet, Contract_Tariff.price,
                Contract_Tariff.frag1Start, Contract_Tariff.frag1Sum, Contract_Tariff.frag1Price,
                Contract_Tariff.frag2Start, Contract_Tariff.frag2Sum, Contract_Tariff.frag2Price,
                EventType.code AS eventType_code,
                EventType.name AS eventType_name,
                rbService.code AS service_code,
                rbService.name AS service_name,
                rbMedicalAidUnit.code AS unit_code,
                rbMedicalAidUnit.name AS unit_name
        FROM Contract_Tariff
        LEFT JOIN EventType ON eventType_id=EventType.id AND EventType.deleted=0
        LEFT JOIN rbService ON rbService.id=Contract_Tariff.service_id
        LEFT JOIN rbMedicalAidUnit ON rbMedicalAidUnit.id=unit_id
        WHERE Contract_Tariff.master_id=%d AND Contract_Tariff.deleted=0
        """  % self.contractId
        query = db.query(stmt)
        return query


class CPriceCoefficientEditor(QtGui.QDialog, Ui_PriceCoefficientDialog):
        def __init__(self, parent=None):
            QtGui.QDialog.__init__(self, parent)
            self.setupUi(self)
            for edt in self.edtPriceCoefficient, self.edtPriceExCoefficient, self.edtPriceEx2Coefficient:
                edt.setMinimum(-9999.9999)
                edt.setMaximum(9999.9999)
                edt.setSingleStep(0.0001)


        def params(self):
            return (self.edtPriceCoefficient.value() if self.chkPriceCoefficient.isChecked() else None,
                    self.edtPriceExCoefficient.value() if self.chkPriceExCoefficient.isChecked() else None,
                    self.edtPriceEx2Coefficient.value() if self.chkPriceEx2Coefficient.isChecked() else None
                   )


class CParamsContractDialog(QtGui.QDialog, Ui_ParamsContractDialog):
        def __init__(self, parent=None):
            QtGui.QDialog.__init__(self, parent)
            self.setupUi(self)

        def params(self):
            result = {}
            if self.chkContractGroup.isChecked():
                result['grouping'] = self.edtContractGroup.text()
            if self.chkBase.isChecked():
                result['resolution'] = self.edtBase.text()
            if self.chkNumber.isChecked():
                result['number'] = self.edtNumber.text()
            if self.chkDate.isChecked():
                result['date'] = self.edtDate.date()
            if self.chkBegDate.isChecked():
                result['begDate'] = self.edtBegDate.date()
            if self.chkEndDate.isChecked():
                result['endDate'] = self.edtEndDate.date()
            if self.chkCoefficient.isChecked():
                result['coefficient'] = self.edtCoefficient.value()
            if self.chkCoefficientEx.isChecked():
                result['coefficientEx'] = self.edtCoefficientEx.value()
            if self.chkCoefficientEx2.isChecked():
                result['coefficientEx2'] = self.edtCoefficientEx2.value()
            return result


        def setParams(self, record):
            if record:
                self.edtContractGroup.setText(forceString(record.value('grouping')))
                self.edtBase.setText(forceString(record.value('resolution')))
                self.edtNumber.setText(forceString(record.value('number')))
                self.edtDate.setDate(forceDate(record.value('date')))
                self.edtBegDate.setDate(forceDate(record.value('begDate')))
                self.edtEndDate.setDate(forceDate(record.value('endDate')))
                self.edtCoefficient.setValue(forceDouble(record.value('coefficient')))
                self.edtCoefficientEx.setValue(forceDouble(record.value('coefficientEx')))
                self.edtCoefficientEx2.setValue(forceDouble(record.value('coefficientEx2')))


class CContractsSelectionManager(object):
    def updateSelectedCount(self):
        n = len(self.selectedContractsIdList)
        if n:
            msg = u'выбрано '+formatNum(n, (u'контракт', u'контракта', u'контрактов'))
        else:
            msg = u'ничего не выбрано'
        self.lblSelectedCount.setText(msg)


    def setSelected(self, contractId, value):
        present = self.isSelected(contractId)
        if value:
            if not present:
                self.selectedContractsIdList.append(contractId)
                self.updateSelectedCount()
        else:
            if present:
                self.selectedContractsIdList.remove(contractId)
                self.updateSelectedCount()


    def isSelected(self, contractId):
        return contractId in self.selectedContractsIdList


class CPriceListDialog(CDialogBase, CContractsSelectionManager, Ui_PriceListDialog):
    def __init__(self,  parent, priceListId):
        CDialogBase.__init__(self, parent)
        self.setupPopupMenu()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.modelContracts = CPriceListTableModel(self)
        self.modelContracts.setObjectName('modelContracts')
        self.tblContracts.setModel(self.modelContracts)
        self.parentPriceListId = priceListId
        self.priceListId = priceListId
        self.selectedContractsIdList = []
        self.cmbPriceList.setPriceListOnly(True)
        self.setRecord()
        self.stringItemDelegate = CStringItemDelegate()
        self.dateItemDelegate = CDateItemDelegate(self)
        self.coefficientItemDelegate = CCoefficientItemDelegate(self)
        self.tblContracts.setItemDelegateForColumn(2, self.stringItemDelegate)
        self.tblContracts.setItemDelegateForColumn(3, self.stringItemDelegate)
        self.tblContracts.setItemDelegateForColumn(4, self.stringItemDelegate)
        self.tblContracts.setItemDelegateForColumn(5, self.dateItemDelegate)
        self.tblContracts.setItemDelegateForColumn(6, self.dateItemDelegate)
        self.tblContracts.setItemDelegateForColumn(7, self.dateItemDelegate)
        self.tblContracts.setItemDelegateForColumn(8, self.coefficientItemDelegate)
        self.tblContracts.setItemDelegateForColumn(9, self.coefficientItemDelegate)
        if self.priceListId:
            self.btnSynchronization.setEnabled(True)
            self.btnRegistration.setEnabled(True)
            self.btnPeriodOnPriceList.setEnabled(True)
        self.tblContracts.setPopupMenu(self.mnuItems)


    def setupPopupMenu(self):
        self.mnuItems = QtGui.QMenu(self)
        self.mnuItems.setObjectName('mnuItems')
        self.actUpdateParamsContract = QtGui.QAction(u'Изменить параметры', self)
        self.actUpdateParamsContract.setObjectName('actUpdateParamsContract')
        self.mnuItems.addAction(self.actUpdateParamsContract)


    @QtCore.pyqtSlot()
    def on_mnuItems_aboutToShow(self):
        itemPresent = self.tblContracts.currentIndex().row() >= 0
        self.actUpdateParamsContract.setEnabled(itemPresent)


    @QtCore.pyqtSlot()
    def on_actUpdateParamsContract_triggered(self):
        self.getParamsContract()


    def setRecord(self):
        if self.priceListId:
            db = QtGui.qApp.db
            table = db.table('Contract')
            record = db.getRecordEx(table, [table['priceList_id']], [table['deleted'].eq(0), table['priceList_id'].eq(self.priceListId)])
            if record:
                self.priceListId = forceRef(record.value('priceList_id'))
                if self.priceListId:
                    self.cmbPriceList.setValue(self.priceListId)
                    self.setPriceListCode(self.priceListId)
                else:
                    self.tblContracts.setIdList([], None)
            else:
                self.priceListId = None
                self.tblContracts.setIdList([], None)
        else:
            self.tblContracts.setIdList([], None)
        self.setWindowTitleEx(u'Синхронизация договоров с прайс-листом: %s'%(self.cmbPriceList.currentText()))


    def getPriceListIdList(self, id):
        idList = []
        if id:
            db = QtGui.qApp.db
            tableContract = db.table('Contract')
            idList = db.getDistinctIdList(tableContract, tableContract['id'].name(), [tableContract['deleted'].eq(0), tableContract['priceList_id'].eq(id), tableContract['id'].ne(id)], u'finance_id, grouping, resolution, number, date')
        return idList


    def setPriceListIdList(self, idList, posToId):
        if idList:
            self.tblContracts.setIdList(idList, posToId)
            self.tblContracts.setFocus(QtCore.Qt.OtherFocusReason)


    def setPriceListCode(self, id):
        crIdList = self.getPriceListIdList(id)
        self.setPriceListIdList(crIdList, None)


    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbPriceList_editTextChanged(self, index):
        self.on_btnClearAll_clicked()
        priceListId = self.cmbPriceList.value()
        if priceListId:
            self.priceListId = priceListId
            self.btnEstablish.setEnabled(True)
            self.btnSynchronization.setEnabled(True)
            self.btnRegistration.setEnabled(True)
            self.btnPeriodOnPriceList.setEnabled(True)
            self.setRecord()
        else:
            self.priceListId = None
            self.tblContracts.setIdList([], None)
            self.btnEstablish.setEnabled(False)
            self.btnSynchronization.setEnabled(False)
            self.btnRegistration.setEnabled(False)
            self.btnPeriodOnPriceList.setEnabled(False)
        self.modelContracts.emitDataChanged()


    @QtCore.pyqtSlot()
    def on_btnSelectedAll_clicked(self):
        self.selectedContractsIdList = self.modelContracts.idList()
        self.modelContracts.emitDataChanged()
        self.updateSelectedCount()


    @QtCore.pyqtSlot()
    def on_btnClearAll_clicked(self):
        self.selectedContractsIdList = []
        self.modelContracts.emitDataChanged()
        self.updateSelectedCount()


    @QtCore.pyqtSlot()
    def on_btnEstablish_clicked(self):
        if self.checkDataEntered():
            if self.messageQuestion(u'Прайс-листы выделенных договоров будут заменены на текущий прайс-лист. Вы уверены, что хотите этого?'):
                QtGui.qApp.callWithWaitCursor(self, self.getEstablish)
                self.on_btnClearAll_clicked()
        else:
            self.on_btnClearAll_clicked()


    def getEstablish(self):
        if self.priceListId and self.parentPriceListId:
            db = QtGui.qApp.db
            db.transaction()
            try:
                tableContract = db.table('Contract')
                for selectedContractsId in self.selectedContractsIdList:
                    recordCache = self.modelContracts._recordsCache.map.get(selectedContractsId, None)
                    if recordCache:
                        grouping = forceString(recordCache.value('grouping'))
                        number = forceString(recordCache.value('number'))
                        resolution = forceString(recordCache.value('resolution'))
                        date = forceDate(recordCache.value('date'))
                        begDate = forceDate(recordCache.value('begDate'))
                        endDate = forceDate(recordCache.value('endDate'))
                        coefficientPrice = forceDouble(recordCache.value('coefficient'))
                        coefficientPriceEx = forceDouble(recordCache.value('coefficientEx'))
                        coefficientPriceEx2 = forceDouble(recordCache.value('coefficientEx2'))
                        record = db.getRecordEx(tableContract, '*', [tableContract['id'].eq(selectedContractsId), tableContract['deleted'].eq(0)])
                        if number:
                            record.setValue('number', toVariant(number))
                        if grouping:
                            record.setValue('grouping', toVariant(grouping))
                        if resolution:
                            record.setValue('resolution', toVariant(resolution))
                        if date:
                            record.setValue('date', toVariant(date))
                        if begDate:
                            record.setValue('begDate', toVariant(begDate))
                        if endDate:
                            record.setValue('endDate', toVariant(endDate))
                        record.setValue('priceList_id', toVariant(self.parentPriceListId))
                        record.setValue('coefficient', toVariant(coefficientPrice))
                        record.setValue('coefficientEx', toVariant(coefficientPriceEx))
                        record.setValue('coefficientEx2', toVariant(coefficientPriceEx2))
                        db.updateRecord(tableContract, record)
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise
            self.priceListId = self.parentPriceListId
            self.setRecord()
            self.modelContracts.emitDataChanged()

    @staticmethod
    def updateTariffToCoefficient(record, coefficients):
        assert len(coefficients) == 3
        recordChanged = False
        if record:
            for coefficient, fieldName in zip(coefficients, ('price', 'priceEx', 'priceEx2')):
                if coefficient is not None:
                    value = forceDouble(record.value(fieldName))
                    newValue = value*coefficient if coefficient >= 0 else -value/coefficient
                    record.setValue(fieldName, newValue)
                    recordChanged = True
        return recordChanged


    @QtCore.pyqtSlot()
    def on_btnSynchronization_clicked(self):
        if self.checkDataEntered():
            if self.synchronizeContracts():
                if self.messageQuestion(u'Будет проведена синхронизация выделенных договоров в соответствии с текущим прайс-листом. Вы уверены, что хотите этого?'):
                    self.getSynchronizationTariff()
                    self.setRecord()
                    self.modelContracts.emitDataChanged()
        else:
            self.on_btnClearAll_clicked()

    def synchronizeContracts(self):
        if self.priceListId != self.parentPriceListId:
            res = QtGui.QMessageBox.question( self,
                                 u'Внимание!',
                                 u'Выбранный прайс-лист не соответствует текущему договору.\nХотите продолжить?',
                                 QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                 QtGui.QMessageBox.No)
            if res == QtGui.QMessageBox.No:
                return False
        return True

    def getSynchronizationTariff(self, registration = False):
        if self.priceListId and self.selectedContractsIdList and self.parentPriceListId:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            db = QtGui.qApp.db
            db.transaction()
            progressDialog = None
            try:
                progressDialog = CContractFormProgressDialog(self)
                progressDialog.lblByContracts.setText(u'Тарифы')
                progressDialog.setWindowTitle(u'Синхронизация договоров')
                progressDialog.show()
                tableContract = db.table('Contract')
                tableContractTariff = db.table('Contract_Tariff')
                table = tableContract.innerJoin(tableContractTariff, tableContract['id'].eq(tableContractTariff['master_id']))
                records = db.getRecordListGroupBy(table, 'Contract_Tariff.*', [tableContractTariff['deleted'].eq(0), tableContract['deleted'].eq(0), tableContractTariff['master_id'].eq(self.parentPriceListId)], 'Contract_Tariff.id')
                updateTariffIdList = []
                progressDialog.setNumContracts(len(records))
                for record in records:
                    progressDialog.prbContracts.setValue(progressDialog.prbContracts.value()+1)
                    tariffId = forceRef(record.value('id'))
                    eventTypeId = forceRef(record.value('eventType_id'))
                    tariffType = forceInt(record.value('tariffType'))
                    serviceId = forceRef(record.value('service_id'))
                    tariffCategoryId = forceRef(record.value('tariffCategory_id'))
                    sex = forceInt(record.value('sex'))
                    age = forceString(record.value('age'))
                    MKB = forceString(record.value('MKB'))
                    cond = [tableContract['priceList_id'].eq(self.parentPriceListId),
                            tableContractTariff['master_id'].inlist(self.selectedContractsIdList),
                            tableContractTariff['master_id'].ne(self.parentPriceListId),
                            tableContract['deleted'].eq(0),
                            tableContractTariff['deleted'].eq(0),
                            tableContractTariff['eventType_id'].eq(eventTypeId),
                            tableContractTariff['tariffType'].eq(tariffType),
                            tableContractTariff['service_id'].eq(serviceId),
                            tableContractTariff['tariffCategory_id'].eq(tariffCategoryId),
                            tableContractTariff['MKB'].eq(MKB),
                            tableContractTariff['sex'].eq(sex),
                            tableContractTariff['age'].eq(age)
                            ]
                    if updateTariffIdList:
                        cond.append(tableContractTariff['id'].notInlist(updateTariffIdList))
                    oldRecords = db.getRecordListGroupBy(table, [tableContractTariff['id'].alias('contractTariffId'), tableContractTariff['master_id'], tableContract['id'].alias('contractId')], cond, 'Contract_Tariff.id')
                    updateTariffId = None
                    contractNameList = {}
                    if self.chkUpdate.isChecked():
                        progressDialog.setNumContractSteps(len(oldRecords))
                        for oldRecord in oldRecords:
                            progressDialog.step()
                            contractId = forceRef(oldRecord.value('contractId'))
                            recordCache = self.modelContracts._recordsCache.map.get(contractId, None)
                            if recordCache:
                                coefficientPrice = forceDouble(recordCache.value('coefficient'))
                                coefficientPriceEx = forceDouble(recordCache.value('coefficientEx'))
                                coefficientPriceEx2 = forceDouble(recordCache.value('coefficientEx2'))
                                coefficients = coefficientPrice, coefficientPriceEx2, coefficientPriceEx2
                                oldTariffId = forceRef(oldRecord.value('contractTariffId'))
                                masterId = forceRef(oldRecord.value('master_id'))
                                self.updateTariffToCoefficient(record, coefficients)
                                record.setValue('master_id', toVariant(masterId))
                                record.setValue('id', toVariant(oldTariffId))
                                updateTariffId = db.updateRecord(tableContractTariff, record)
                                if updateTariffId and updateTariffId not in updateTariffIdList:
                                    updateTariffIdList.append(updateTariffId)
                                if not contractNameList.get(masterId, None):
                                    contractName = forceString(recordCache.value('number')) + ' ' + forceString(forceDate(recordCache.value('date')))
                                    contractNameList[masterId] = contractName
                                    progressDialog.setContractName(contractName)
                    if not oldRecords and self.chkInsert.isChecked():
                        progressDialog.setNumContractSteps(len(self.selectedContractsIdList))
                        for selectedContractsId in self.selectedContractsIdList:
                            progressDialog.step()
                            recordCache = self.modelContracts._recordsCache.map.get(selectedContractsId, None)
                            if recordCache:
                                coefficientPrice = forceDouble(recordCache.value('coefficient'))
                                coefficientPriceEx = forceDouble(recordCache.value('coefficientEx'))
                                coefficientPriceEx2 = forceDouble(recordCache.value('coefficientEx2'))
                                coefficients = coefficientPrice, coefficientPriceEx2, coefficientPriceEx2
                                self.updateTariffToCoefficient(record, coefficients)
                                record.setValue('master_id', toVariant(selectedContractsId))
                                record.setValue('id', toVariant(None))
                                updateTariffId = db.insertRecord(tableContractTariff, record)
                                if updateTariffId and updateTariffId not in updateTariffIdList:
                                    updateTariffIdList.append(updateTariffId)
                                if not contractNameList.get(selectedContractsId, None):
                                    contractName = forceString(recordCache.value('number')) + ' ' + forceString(forceDate(recordCache.value('date')))
                                    contractNameList[selectedContractsId] = contractName
                                    progressDialog.setContractName(contractName)
                for selectedContractsId in self.selectedContractsIdList:
                    recordContract = self.modelContracts._recordsCache.map.get(selectedContractsId, None)
                    if recordContract:
                        recordContract.setValue('priceList_id', toVariant(self.parentPriceListId))
                        db.updateRecord(tableContract, recordContract)
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise
            finally:
                QtGui.qApp.restoreOverrideCursor()
                if progressDialog:
                    progressDialog.close()


    @QtCore.pyqtSlot()
    def on_btnRegistration_clicked(self):
        if self.checkDataEntered() and self.checkDataEnteredRegistration():
            if self.selectedContractsIdList and self.synchronizeContracts():
                if self.messageQuestion(u'Будет проведена регистрация выбранных договоров. Вы уверены, что хотите этого?'):
                    self.getRegistration()
                    if self.messageQuestion(u'Будет проведена синхронизация вновь созданных договоров  по текущему прайс-листу. Вы уверены, что хотите этого?'):
                        self.getSynchronizationTariff(True)
                    self.setRecord()
                    self.modelContracts.emitDataChanged()
        else:
            self.on_btnClearAll_clicked()


    @QtCore.pyqtSlot()
    def on_btnPeriodOnPriceList_clicked(self):
        if self.selectedContractsIdList and self.synchronizeContracts():
            if self.messageQuestion(u'Дата и период выбранных договоров будут установлены по текущему прайс-листу. Вы уверены, что хотите этого?'):
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                try:
                    db = QtGui.qApp.db
                    db.transaction()
                    try:
                        tableContract = db.table('Contract')
                        if self.parentPriceListId:
                            for selectedContractsId in self.selectedContractsIdList:
                                record = db.getRecordEx(tableContract, [tableContract['date'], tableContract['begDate'], tableContract['endDate']], [tableContract['deleted'].eq(0), tableContract['id'].eq(self.parentPriceListId)])
                                if record and selectedContractsId:
                                    date = forceDate(record.value('date'))
                                    begDate = forceDate(record.value('begDate'))
                                    endDate = forceDate(record.value('endDate'))
                                    db.updateRecords(tableContract, [tableContract['endDate'].eq(endDate), tableContract['begDate'].eq(begDate), tableContract['date'].eq(date)], [tableContract['id'].eq(selectedContractsId), tableContract['deleted'].eq(0)])
                        db.commit()
                    except:
                        db.rollback()
                        QtGui.qApp.logCurrentException()
                        raise
                finally:
                    QtGui.qApp.restoreOverrideCursor()
                    self.setRecord()
                    self.modelContracts.emitDataChanged()


    def getParamsContract(self):
        if self.selectedContractsIdList:
            selectedContractsId = self.selectedContractsIdList[0]
            if selectedContractsId:
                db = QtGui.qApp.db
                tableContract = db.table('Contract')
                record = db.getRecordEx(tableContract, '*', [tableContract['id'].eq(selectedContractsId), tableContract['deleted'].eq(0)])
            setupDialog = CParamsContractDialog(self)
            setupDialog.setParams(record)
            if setupDialog.exec_():
                params = setupDialog.params()
                for selectedContractsId in self.selectedContractsIdList:
                    recordCache = self.modelContracts._recordsCache.map.get(selectedContractsId, None)
                    if recordCache:
                        for fieldName in ('grouping', 'resolution', 'number', 'date', 'begDate', 'endDate', 'coefficient', 'coefficientEx', 'coefficientEx2'):
                            value = params.get(fieldName, None)
                            if value is not None:
                                recordCache.setValue(fieldName, toVariant(value))


    def duplicateContract(self, contractId, recordCache, progressDialog):
        newId = None
        db = QtGui.qApp.db
        table = db.table('Contract')
        tableContractTariff = db.table('Contract_Tariff')
        tableContractExpense = db.table('Contract_CompositionExpense')
        db.transaction()
        try:
            grouping = forceString(recordCache.value('grouping'))
            number = forceString(recordCache.value('number'))
            resolution = forceString(recordCache.value('resolution'))
            date = forceDate(recordCache.value('date'))
            begDate = forceDate(recordCache.value('begDate'))
            endDate = forceDate(recordCache.value('endDate'))
            coefficientPrice = forceDouble(recordCache.value('coefficient'))
            coefficientPriceEx = forceDouble(recordCache.value('coefficientEx'))
            coefficientPriceEx2 = forceDouble(recordCache.value('coefficientEx2'))
            coefficients = coefficientPrice, coefficientPriceEx, coefficientPriceEx2
            record = db.getRecordEx(table, '*', [table['id'].eq(contractId), table['deleted'].eq(0)])
            record.setNull('id')
            numberRecord = forceString(record.value('number'))
            if number.lower() == numberRecord.lower():
                record.setValue('number', toVariant(numberRecord + u'-копия'))
            else:
                record.setValue('number', toVariant(number))
            if grouping:
                record.setValue('grouping', toVariant(grouping))
            if resolution:
                record.setValue('resolution', toVariant(resolution))
            if date:
                record.setValue('date', toVariant(date))
            if begDate:
                record.setValue('begDate', toVariant(begDate))
            if endDate:
                record.setValue('endDate', toVariant(endDate))
            record.setValue('priceList_id', toVariant(self.parentPriceListId))
            record.setValue('coefficient', toVariant(coefficientPrice))
            record.setValue('coefficientEx', toVariant(coefficientPriceEx))
            record.setValue('coefficientEx2', toVariant(coefficientPriceEx2))
            newId = db.insertRecord(table, record)
            db.copyDepended(db.table('Contract_Contingent'), 'master_id', contractId, newId)
            db.copyDepended(db.table('Contract_Contragent'), 'master_id', contractId, newId)
            db.copyDepended(db.table('Contract_Specification'), 'master_id', contractId, newId)
            stmt = db.selectStmt(tableContractTariff, '*', [tableContractTariff['master_id'].eq(contractId), tableContractTariff['deleted'].eq(0)],  order = 'id')
            qquery = db.query(stmt)
            progressDialog.setContractName(number + ' ' + forceString(date))
            progressDialog.setNumContractSteps(qquery.size())
            while qquery.next():
                progressDialog.step()
                recordTariff = qquery.record()
                tariffId = forceRef(recordTariff.value('id'))
                recordTariff.setNull('id')
                recordTariff.setValue('master_id', toVariant(newId))
                self.updateTariffToCoefficient(recordTariff, coefficients)
                newTariffId = db.insertRecord(tableContractTariff, recordTariff)
                if self.chkInsertExpense.isChecked() and tariffId and newTariffId:
                    recordExpenses = db.getRecordList(tableContractExpense, '*', [tableContractExpense['master_id'].eq(tariffId)])
                    for recordExpense in recordExpenses:
                        recordExpense.setNull('id')
                        recordExpense.setValue('master_id', toVariant(newTariffId))
                        db.insertRecord(tableContractExpense, recordExpense)
            db.commit()
        except:
            db.rollback()
            raise
        return newId


    def getRegistration(self):
        if self.priceListId and self.selectedContractsIdList and self.parentPriceListId:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            db = QtGui.qApp.db
            db.transaction()
            progressDialog = None
            try:
                progressDialog = CFormProgressDialog(self)
                progressDialog.setWindowTitle(u'Регистрация договоров')
                progressDialog.setNumContracts(len(self.selectedContractsIdList))
                progressDialog.show()
                tableContract = db.table('Contract')
                duplicateContractIdList = []
                for selectedContractsId in self.selectedContractsIdList:
                    recordCache = self.modelContracts._recordsCache.map.get(selectedContractsId, None)
                    if recordCache:
                        date = forceDate(recordCache.value('date'))
                        coefficientPrice = forceDouble(recordCache.value('coefficient'))
                        coefficientPriceEx = forceDouble(recordCache.value('coefficientEx'))
                        coefficientPriceEx2 = forceDouble(recordCache.value('coefficientEx2'))
                        record = db.getRecordEx(tableContract, '*', [tableContract['id'].eq(selectedContractsId), tableContract['deleted'].eq(0)])
                        if record:
                            record.setValue('endDate', toVariant(date))
                            closedContractId = db.updateRecord(tableContract, record)
                            duplicateContractId = self.duplicateContract(selectedContractsId, recordCache, progressDialog)
                            if duplicateContractId and (duplicateContractId not in duplicateContractIdList):
                                duplicateContractIdList.append(duplicateContractId)
                db.commit()
                self.selectedContractsIdList = duplicateContractIdList
                self.setRecord()
                self.modelContracts.emitDataChanged()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise
            finally:
                QtGui.qApp.restoreOverrideCursor()
                if progressDialog:
                    progressDialog.close()


    def messageQuestion(self, message):
        res = QtGui.QMessageBox.question( self,
                     u'Внимание!',
                     message,
                     QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                     QtGui.QMessageBox.No)
        if res == QtGui.QMessageBox.No:
            return False
        elif res == QtGui.QMessageBox.Yes:
            return True


    def checkDataEnteredRegistration(self):
        result = True
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        for selectedContractsId in self.selectedContractsIdList:
            recordCache = self.modelContracts._recordsCache.map.get(selectedContractsId, None)
            if recordCache:
                endDate = forceDate(recordCache.value('date'))
                record = db.getRecordEx(tableContract, '*', [tableContract['id'].eq(selectedContractsId), tableContract['deleted'].eq(0)])
                if record:
                    dateContract = forceDate(record.value('date'))
                    begDateContract = forceDate(record.value('begDate'))
                    result = result and ((dateContract <= endDate and begDateContract <= endDate) or self.checkValueMessage(u'Дата окончания периода %s должна быть больше или равна дате начала периода %s'% (forceString(endDate), forceString(begDateContract)), False, self.tblContracts, self.modelContracts.findItemIdIndex(selectedContractsId), 5))
        return result


    def checkDataEntered(self):
        result = True
        for key in self.selectedContractsIdList:
            recordCache = self.modelContracts._recordsCache.map.get(key, None)
            if recordCache:
                row = self.modelContracts.findItemIdIndex(key)
                date = forceDate(recordCache.value('date'))
                begDate = forceDate(recordCache.value('begDate'))
                endDate = forceDate(recordCache.value('endDate'))
                result = result and (not date.isNull() or self.checkInputMessage(u'дату', False, self.tblContracts, row, 5))
                result = result and (not begDate.isNull() or self.checkInputMessage(u'начальную дату', False, self.tblContracts, row, 6))
                result = result and (not endDate.isNull() or self.checkInputMessage(u'конечную дату', False, self.tblContracts, row, 7))
                result = result and ((date <= begDate and date < endDate) or self.checkValueMessage(u'Период %s-%s не может начаться раньше даты %s'% (forceString(begDate), forceString(endDate), forceString(date)), False, self.tblContracts, row, 5))
                result = result and ((begDate <= endDate) or self.checkValueMessage(u'Дата начала периода %s должна быть меньше или равна дате окончания периода %s' % (forceString(begDate), forceString(endDate)), False, self.tblContracts, row, 6))
        return result


class CPriceListTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CEnableCol(u'Выбрать',               ['id'], 5,  parent),
            CRefBookCol(u'Источник финансирования', ['finance_id'], 'rbFinance', 20),
            CTextCol(u'Группа',                  ['grouping'],  20),
            CTextCol(u'Основание',               ['resolution'],10),
            CTextCol(u'Номер',                   ['number'],    5),
            CDateCol(u'Дата',                    ['date'],      10),
            CDateCol(u'Нач.дата',                ['begDate'],   10),
            CDateCol(u'Кон.дата',                ['endDate'],   10),
            CSumCol(u'Коэффициент тарифа',              ['coefficient'], 5),
            CSumCol(u'Коэффициент расширенного тарифа', ['coefficientEx'], 5),
            CSumCol(u'Второй коэффициент расширенного тарифа', ['coefficientEx2'], 5)
            ], 'Contract' )
        self.parent = parent


    def flags(self, index):
        result = CTableModel.flags(self, index)
        if index.column() == 0:
            result |= QtCore.Qt.ItemIsUserCheckable
        elif index.column() != 1:
            result |= QtCore.Qt.ItemIsEditable
        return result


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.BackgroundColorRole:
            row = index.row()
            column = index.column()
            contractId = self._idList[row]
            record = self._recordsCache.map.get(contractId, None)
            if record and (    (column == 10 and not forceDouble(record.value('coefficientEx2')))
                            or (column == 9 and not forceDouble(record.value('coefficientEx')))
                            or (column == 8 and not forceDouble(record.value('coefficient')))
                            or (column == 7 and not forceDate(record.value('endDate')))
                            or (column == 6 and not forceDate(record.value('begDate')))
                            or (column == 5 and not forceDate(record.value('date')))
                            or (column == 4 and not forceString(record.value('number')))
                            or (column == 3 and not forceString(record.value('resolution')))
                            or (column == 2 and not forceString(record.value('grouping')))
                          ):
                   return toVariant(QtGui.QColor(255, 0, 0))
            return QtCore.QVariant()
        elif role == QtCore.Qt.FontRole:
            row = index.row()
            column = index.column()
            contractId = self._idList[row]
            record = self._recordsCache.map.get(contractId, None)
            font = QtGui.QFont()
            if record and (   (column == 8  and not forceDouble(record.value('coefficient')))
                           or (column == 9  and not forceDouble(record.value('coefficientEx')))
                           or (column == 10 and not forceDouble(record.value('coefficientEx2')))
                          ):
                        font.setBold(True)
                        font.setItalic(True)
            return QtCore.QVariant(font)
        elif role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            contractId = self._idList[row]
            record = self._recordsCache.map.get(contractId, None)
            if record:
                if column == 2:
                    return toVariant(forceString(record.value('grouping')))
                elif column == 3:
                    return toVariant(forceString(record.value('resolution')))
                elif column == 4:
                    return toVariant(forceString(record.value('number')))
                elif column == 5:
                    return toVariant(forceDate(record.value('date')))
                elif column == 6:
                    return toVariant(forceDate(record.value('begDate')))
                elif column == 7:
                    return toVariant(forceDate(record.value('endDate')))
                elif column == 8:
                    return toVariant(forceDouble(record.value('coefficient')))
                elif column == 9:
                    return toVariant(forceDouble(record.value('coefficientEx')))
                elif column == 10:
                    return toVariant(forceDouble(record.value('coefficientEx2')))
            return QtCore.QVariant()
        return CTableModel.data(self, index, role)


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        column = index.column()
        contractId = self._idList[row]
        if role == QtCore.Qt.EditRole:
            if contractId:
                record = self._recordsCache.map.get(contractId, None)
                if record:
                    if column == 2:
                        record.setValue('grouping', toVariant(value))
                    elif column == 3:
                        record.setValue('resolution', toVariant(value))
                    elif column == 4:
                        record.setValue('number', toVariant(value))
                    elif column == 5:
                        record.setValue('date', toVariant(value))
                    elif column == 6:
                        record.setValue('begDate', toVariant(value))
                    elif column == 7:
                        record.setValue('endDate', toVariant(value))
                    elif column == 8:
                        record.setValue('coefficient', toVariant(value))
                    elif column == 9:
                        record.setValue('coefficientEx', toVariant(value))
                    elif column == 10:
                        record.setValue('coefficientEx2', toVariant(value))
                    self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
            return True
        if role == QtCore.Qt.CheckStateRole:
            if contractId and column == 0:
                self.parent.setSelected(contractId, forceInt(value) == QtCore.Qt.Checked)
                self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
            return True
        return False

