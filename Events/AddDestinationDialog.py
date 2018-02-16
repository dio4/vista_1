# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4  import QtCore, QtGui, QtSql
from Ui_AddDestinationDialog                import Ui_AddDestinationDialog
from library.DialogBase                     import CDialogBase, CConstructHelperMixin
from library.TableModel                     import CTableModel, CTextCol
from library.InDocTable                     import CInDocTableCol, CRecordListModel
from library.Utils                          import forceInt, forceString
from Orgs.Utils                             import getOrgStructures, getOrgStructureDescendants

class CMNNTableModel(CRecordListModel):

    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CInDocTableCol(u'МНН', 'mnn', 70))

    def flags(self, index):
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return flags

    def addItems(self, mnnList):
        self.removeRows(0, len(self._items))
        for mnn in mnnList:
            newRecord = super(CMNNTableModel, self).getEmptyRecord()
            for col in self._cols:
                newRecord.append(QtSql.QSqlField(col.fieldName()))
                if col.fieldName() == 'mnn':
                    newRecord.setValue(col.fieldName(), mnn)
            self.addRecord(newRecord)


class CIssueFormTableModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CInDocTableCol(u'Форма выпуска', 'issueForm', 70))

    def flags(self, index):
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return flags

    def addItems(self, issueFormList):
        self.removeRows(0, len(self._items))
        for issueForm in issueFormList:
            newRecord = super(CIssueFormTableModel, self).getEmptyRecord()
            for col in self._cols:
                newRecord.append(QtSql.QSqlField(col.fieldName()))
                if col.fieldName() == 'issueForm':
                    newRecord.setValue(col.fieldName(), issueForm)
            self.addRecord(newRecord)


class CListTableModel(CTableModel):
    def __init__(self, parent = None):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Выбранные препараты', ['name'], 50))
        self.setTable('rbMedicines')


class CTradeNamesTableModel(CTableModel):
    def __init__(self, parent = None):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Торговые наименования', ['name'], 50))
        self.setTable('rbStockNomenclature')


class COrgStructureStock(CTableModel):
    def __init__(self, parent = None):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Подразделения', ['name'], 50))
        self.setTable('OrgStructure')


class CAddDestinationSetupDialog(CDialogBase, Ui_AddDestinationDialog, CConstructHelperMixin):

    def __init__(self, parent = None, filter = ''):
        CDialogBase.__init__(self, parent)

        self.curDrugsId = []
        self.tradeNameCodesList = []
        self.filter = filter
        self.drugFormularyItemIdList = []
        self.orgStructureIdList = []
        self.orgStructureIdWhere = ''

        self.mnn = '%'
        self.issueForm = '%'
        self.tradeName = '%'
        self.searchMNN ='%'
        self.searchIssueForm = '%'
        self.searchTradeName = '%'

        self.addModels('MNN', CMNNTableModel(self))
        self.addModels('IssueForm', CIssueFormTableModel(self))
        self.addModels('TradeName', CTradeNamesTableModel(self))
        self.addModels('List', CListTableModel(self))
        self.addModels('OrgStructureStock', COrgStructureStock(self))
        self.setupUi(self)
        self.setModels(self.tblMNN, self.modelMNN, self.selectionModelMNN)
        self.tblMNN.horizontalHeader().setStretchLastSection(True)
        self.tblMNN.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setModels(self.tblIssueForm, self.modelIssueForm, self.selectionModelIssueForm)
        self.tblIssueForm.horizontalHeader().setStretchLastSection(True)
        self.tblIssueForm.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblIssueForm.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.setModels(self.tblTradeName, self.modelTradeName, self.selectionModelTradeName)
        self.tblTradeName.horizontalHeader().setStretchLastSection(True)
        self.tblTradeName.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblSelectedDrugs.setModel(self.modelList)
        self.tblSelectedDrugs.horizontalHeader().setStretchLastSection(True)
        self.chkCurrentFormulary.setChecked(True)
        self.prbLoad.setVisible(False)

        if QtGui.qApp.currentOrgStructureId():
            self.orgStructureIdList = getOrgStructureDescendants(QtGui.qApp.currentOrgStructureId())
        else:
            self.orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
        if len(self.orgStructureIdList) > 0:
            self.orgStructureIdWhere = u'''AND DrugFormulary.orgStructure_id IN (%(orgStructures)s) ''' % {'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in self.orgStructureIdList)}

        self.tableMNNRebuild()

    def tableMNNRebuild(self):
        db = QtGui.qApp.db
        stmt = '''
            SELECT rbMedicines.mnn
            FROM rbMedicines
            WHERE rbMedicines.id IN (SELECT DrugFormulary_Item.drug_id
                             FROM DrugFormulary_Item
                             INNER JOIN DrugFormulary ON DrugFormulary.id = DrugFormulary_Item.master_id
                                                         AND DATE(DrugFormulary.begDate) <= DATE('%(curDate)s')
                                                         AND DATE(DrugFormulary.endDate) >= DATE('%(curDate)s')
                                                         %(orgStructureIdWhere)s)
               AND rbMedicines.mnn LIKE '%(searchMNN)s'
               %(filter)s
            ORDER BY rbMedicines.mnn''' % {'curDate' : QtCore.QDate.currentDate().toString('yyyy-MM-dd'),
                                                       'orgStructureIdWhere' : self.orgStructureIdWhere,
                                                       'filter' : self.filter,
                                                       'searchMNN' : self.searchMNN}

        query = db.query(stmt)
        mnnList = []
        while query.next():
            record = query.record()
            if not mnnList.count(forceString(record.value('mnn'))):
                mnnList.append(forceString(record.value('mnn')))
        self.tblMNN.model().addItems(mnnList)

    def tableIssueFormRebuild(self):
        db = QtGui.qApp.db

        brandNameList = []
        stmt = '''
            SELECT name
            FROM rbStockNomenclature
            WHERE mnn LIKE '%(mnnName)s'
                  AND mnn LIKE '%(searchMNN)s'
            ORDER BY name
            ''' % {'mnnName' : self.mnn,
                   'searchMNN' : self.searchMNN}
        query = db.query(stmt)
        oldName = ''
        while query.next():
            record = query.record()
            if oldName != forceString(record.value('name')):
                oldName = forceString(record.value('name'))
                brandNameList.append(forceString(record.value('name')))

        if len(brandNameList) > 1:
            nameList = 'AND ('
            i = 0
            while i < len(brandNameList) - 1:
                if i < len(brandNameList) - 2:
                    nameList += "rbMedicines.name LIKE '%" + brandNameList[i] + "%' OR "
                else:
                    nameList += "rbMedicines.name LIKE '%" + brandNameList[i] + "%')"
                i += 1
        else:
            nameList = ''

        stmt = '''
                SELECT rbMedicines.issueForm
                FROM rbMedicines
                WHERE rbMedicines.id IN (SELECT DrugFormulary_Item.drug_id
                                 FROM DrugFormulary_Item
                                 INNER JOIN DrugFormulary ON DrugFormulary.id = DrugFormulary_Item.master_id
                                                             AND DATE(DrugFormulary.begDate) <= DATE('%(curDate)s')
                                                             AND DATE(DrugFormulary.endDate) >= DATE('%(curDate)s')
                                                             %(orgStructureIdWhere)s)
                   %(nameList)s
                   AND rbMedicines.mnn LIKE '%(mnn)s'
                   AND rbMedicines.mnn LIKE '%(searchMNN)s'
                   AND rbMedicines.issueForm LIKE '%(searchIssueForm)s'
                   %(filter)s
                ORDER BY rbMedicines.issueForm ''' % {'curDate' : QtCore.QDate.currentDate().toString('yyyy-MM-dd'),
                                              'nameList' : nameList,
                                              'orgStructureIdWhere' : self.orgStructureIdWhere,
                                              'mnn' : self.mnn,
                                              'searchMNN' : self.searchMNN,
                                              'searchIssueForm' : self.searchIssueForm,
                                              'filter' : self.filter}
        query = db.query(stmt)
        issueFormList = []
        while query.next():
            record = query.record()
            if not issueFormList.count(forceString(record.value('issueForm'))):
                issueFormList.append(forceString(record.value('issueForm')))
        self.tblIssueForm.model().addItems(issueFormList)

    def tableTradeNameRebuild(self):
        db = QtGui.qApp.db
        idList = []
        stmt = '''
            SELECT id, code, name
            FROM rbStockNomenclature
            WHERE mnn LIKE '%(mnn)s'
                  AND mnn LIKE '%(searchMNN)s'
                  AND issueForm LIKE '%(issueForm)s'
                  AND issueForm LIKE '%(searchIssueForm)s'
                  AND name LIKE '%(searchTradeName)s'
            ORDER BY name
            ''' % {'mnn' : '%' + self.mnn + '%',
                   'searchMNN' : self.searchMNN,
                   'issueForm' : '%' + self.issueForm + '%',
                   'searchIssueForm' : self.searchIssueForm,
                   'searchTradeName' : self.searchTradeName}
        query = db.query(stmt)
        oldName = ''
        while query.next():
            record = query.record()
            if oldName != forceString(record.value('name')):
                oldName = forceString(record.value('name'))
                idList.append(forceInt(record.value('id')))
        self.tblTradeName.model().setIdList(idList)

    def tableOrgStructureStockRebuild(self):
        db = QtGui.qApp.db
        idListOrgStructure = []
        idListNomenclature = []

        stmt = '''
            SELECT rbStockNomenclature.id
            FROM rbStockNomenclature
            WHERE rbStockNomenclature.mnn LIKE '%(mnn)s'
                  AND rbStockNomenclature.mnn LIKE '%(searchMNN)s'
                  AND rbStockNomenclature.issueForm LIKE '%(issueForm)s'
                  AND rbStockNomenclature.issueForm LIKE '%(searchIssueForm)s'
            ''' % {'mnn' : '%' + self.mnn + '%',
                   'searchMNN' : self.searchMNN,
                   'issueForm' : '%' + self.issueForm + '%',
                   'searchIssueForm' : self.searchIssueForm}
        query = db.query(stmt)
        while query.next():
            record = query.record()
            id = forceInt(record.value('id'))
            idListNomenclature.append(id)

        stmt = '''
            SELECT OrgStructure.id
            FROM OrgStructure
            WHERE OrgStructure.deleted = 0
                AND OrgStructure.hasStocks = 1
                AND OrgStructure.name LIKE '%(searchOrgStructure)s'
            ORDER BY OrgStructure.name
        ''' % {'searchOrgStructure' : self.searchTradeName}
        query = db.query(stmt)
        while query.next():
            record = query.record()
            id = forceInt(record.value('id'))
            #for idNomenclature in idListNomenclature:
            #    if CStockModelMixin.getRemainings(QtCore.QDate.currentDate(), 0, id, 0, idNomenclature):
            #        idListOrgStructure.append(id)

    def getDrugFormularyItemIdList(self):
        return self.drugFormularyItemIdList, self.tradeNameCodesList

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.chkCurrentFormulary.setChecked(params.get('currentFormular', True))

    def params(self):
        result = {}
        result['currentFormular'] = self.chkCurrentFormulary.isChecked()
        return result

    def accept(self):
        if not self.drugFormularyItemIdList:
            QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Необходимо выбрать хотя бы одно лекарственное средство.',
                                       QtGui.QMessageBox.Ok)
            return
        super(CAddDestinationSetupDialog, self).accept()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelMNN_currentRowChanged(self, current, previous):
        self.curTradeName = ''
        mnn = forceString(self.tblMNN.model().data(current))
        if mnn != '':
            self.mnn = mnn
            self.tableIssueFormRebuild()
            if self.chkOrgStructureStock.isChecked():
                self.tableOrgStructureStockRebuild()
            else:
                self.tableTradeNameRebuild()
            self.tblIssueForm.selectRow(1)
            if self.tblIssueForm.model().rowCount():
                self.tblIssueForm.selectRow(0)
        else:
            self.mnn = '%'

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelIssueForm_currentRowChanged(self, current, previous):
        issueForm = forceString(self.tblIssueForm.model().data(current))
        if issueForm != '':
            self.issueForm = issueForm
            if self.chkOrgStructureStock.isChecked():
                self.tableOrgStructureStockRebuild()
            else:
                self.tableTradeNameRebuild()
        else:
            self.issueForm = '%'

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTradeName_currentRowChanged(self, current, previous):
        if not self.chkOrgStructureStock.isChecked():
            tradeName = forceString(self.tblTradeName.model().data(current))
            if tradeName != '':
                self.tradeName = tradeName
            else:
                self.tradeName = '%'

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblIssueForm_doubleClicked(self, index):
        self.on_btnAdd_clicked()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblTradeName_doubleClicked(self, index):
        self.on_btnAdd_clicked()

    @QtCore.pyqtSlot()
    def on_btnAdd_clicked(self):
        #FIXME: Зачем подзапросы? (везде)
        stmt = u'''
                SELECT rbMedicines.id AS drugId,
                DrugFormulary_Item.id AS drugFormularyItemId
                FROM rbMedicines
                INNER JOIN DrugFormulary_Item ON DrugFormulary_Item.drug_id = rbMedicines.id
                WHERE rbMedicines.id IN (SELECT DrugFormulary_Item.drug_id
                                    FROM DrugFormulary_Item
                                    INNER JOIN DrugFormulary ON DrugFormulary.id = DrugFormulary_Item.master_id
                                                                AND DATE(DrugFormulary.begDate) <= DATE('%(curDate)s')
                                                                AND DATE(DrugFormulary.endDate) >= DATE('%(curDate)s')
                                                                %(orgStructureIdWhere)s)
                      AND rbMedicines.mnn LIKE '%(mnn)s'
                      AND rbMedicines.mnn LIKE '%(searchMNN)s'
                      AND rbMedicines.issueForm LIKE '%(issueForm)s'
                      AND rbMedicines.issueForm LIKE '%(searchIssueForm)s'
                      %(filter)s
                GROUP BY DrugFormulary_Item.drug_id
                ''' % {'curDate' : QtCore.QDate.currentDate().toString('yyyy-MM-dd'),
                       'orgStructureIdWhere' : self.orgStructureIdWhere,
                       'mnn' : self.mnn,
                       'searchMNN' : self.searchMNN,
                       'issueForm' : self.issueForm,
                       'searchIssueForm' : self.searchIssueForm,
                       'filter' : self.filter}
        query = QtGui.qApp.db.query(stmt)
        while query.next():
            record = query.record()
            drugId = forceInt(record.value('drugId'))
            if drugId not in self.curDrugsId:
                self.curDrugsId.append(drugId)
                self.drugFormularyItemIdList.append(forceInt(record.value('drugFormularyItemId')))
                if self.curDrugsId and not self.chkOrgStructureStock.isChecked():
                    tradeNameCode = 0
                    if self.tradeName != '%':
                        where = '''
                            name = (SELECT MAX(id)
                                     FROM rbStockNomenclature
                                     WHERE name LIKE '%(tradeName)s'
                                           AND name LIKE '%(searchTradeName)s')
                        ''' % {'tradeName' : self.tradeName,
                               'searchTradeName' : self.searchTradeName}
                        tradeNameCodeRecord = QtGui.qApp.db.getRecordEx('rbStockNomenclature', 'code', where)
                        tradeNameCode = forceInt(tradeNameCodeRecord.value('code'))
                    if tradeNameCode:
                        self.tradeNameCodesList.append(tradeNameCode)
                    else:
                        self.tradeNameCodesList.append(0)
                else:
                    self.tradeNameCodesList.append(0)
        if len(self.curDrugsId) > 0:
            self.tblSelectedDrugs.model().setIdList(self.curDrugsId)

    @QtCore.pyqtSlot()
    def on_btnDelete_clicked(self):
        rowList = []
        for row in self.tblSelectedDrugs.selectionModel().selectedRows():
            rowList.append(row.row())
        for index in rowList:
            self.curDrugsId.remove(self.curDrugsId[index])
            self.drugFormularyItemIdList.remove(self.drugFormularyItemIdList[index])
        rowList.reverse()
        for index in rowList:
            del self.tradeNameCodesList[index]
        self.tblSelectedDrugs.model().setIdList(self.curDrugsId)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtMNN_textChanged(self, text):
        text = forceString(text)
        if text != '':
            self.searchMNN = '%' + text + '%'
        else:
            self.searchMNN = '%'
        self.tableMNNRebuild()
        self.tblIssueForm.model().clearItems()
        self.tblTradeName.model().setIdList([])

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtIssueForm_textChanged(self, text):
        text = forceString(text)
        if text != '':
            self.searchIssueForm = '%' + text + '%'
        else:
            self.searchIssueForm = '%'
        self.tableIssueFormRebuild()
        self.tblTradeName.model().setIdList([])

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtTradeName_textChanged(self, text):
        text = forceString(text)
        if text != '':
            self.searchTradeName = '%' + text + '%'
        else:
            self.searchTradeName = '%'
        if self.chkOrgStructureStock.isChecked():
            self.tableOrgStructureStockRebuild()
        else:
            self.tableTradeNameRebuild()

    @QtCore.pyqtSlot(bool)
    def on_chkCurrentFormulary_clicked(self, checked):
        if checked and len(self.orgStructureIdList) > 0:
            self.orgStructureIdWhere = u'''AND DrugFormulary.orgStructure_id IN (%(orgStructures)s) ''' % {'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in self.orgStructureIdList)}
        else:
            self.orgStructureIdWhere = ''
        self.tableMNNRebuild()

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructureStock_clicked(self, checked):
        self.edtDrugs.clear()
        if checked:
            self.lblDrugs.setText(u'Подразделения с остатками')
            self.setModels(self.tblTradeName, self.modelOrgStructureStock, self.selectionModelOrgStructureStock)
            self.tableOrgStructureStockRebuild()

        else:
            self.lblDrugs.setText(u'Торговые наименования')
            self.setModels(self.tblTradeName, self.modelTradeName, self.selectionModelTradeName)
            self.tableTradeNameRebuild()
