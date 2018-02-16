# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Events import FormularyModels
from Events.Ui_FormularyItemSelectionDialog import Ui_FormularyItemSelectionDialog
from library.InDocTable import CInDocTableCol
from library.Utils import *



class CFormularyInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)

    def toString(self, val, record):
        itemId = forceInt(val)

        db = QtGui.qApp.db

        stmt = u'''
            SELECT d.name
            FROM DrugFormulary_Item AS i
            INNER JOIN rbMedicines AS d ON d.id = i.drug_id
            WHERE i.id = %(id)s
            LIMIT 1
        ''' % {
            'id' : itemId
            }
        query = db.query(stmt)
        if query.next():
            record = query.record()
            return forceString(record.value('name'))
        
    def createEditor(self, parent):
        editor = CFormularyItemSelectionDialog(parent=parent)
        return editor

class CFormularyItemSelectionDialog(QtGui.QDialog, Ui_FormularyItemSelectionDialog):
    __pyqtSignals__ = ('itemSelected(int)',
                      )

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self._parent = parent
        self.setupUi(self)
        self.modelMNNs  = FormularyModels.CFormularyMNNsModel(self)
        self.modelForms  = FormularyModels.CFormularyFormsModel(self)
        self.modelFullNames  = FormularyModels.CFormularyFullNamesModel(self)
        self.lstMNNs.setModel(self.modelMNNs)
        self.lstMNNs.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.lstDrugForms.setModel(self.modelForms)
        self.lstDrugForms.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.lstFullNames.setModel(self.modelFullNames)
        self.lstFullNames.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.initSearch()

    def show(self):
        self.resetSearch()
        self.applySearch()
        self.tblFormularyItems.setFocus()
        id = self._parent.value()
        if id:
            self.tblFormularyItems.setCurrentItemId(self._parent.value())
        else:
            self.tblFormularyItems.setCurrentRow(0)
        self.show(self)

    def selectCurrentItem(self):
        id = self.tblFormularyItems.currentItemId()
        self.emit(QtCore.SIGNAL('itemSelected(QVariant)'), toVariant(id))
        self.hide()


    def initSearch(self):
        self._code = ''
        self._name = ''
        self._mnn = ''


    def resetSearch(self):
        self.initSearch()
        self.edtCode.setText(self._code)
        self.edtName.setText(self._name)
        self.edtMnn.setText(self._mnn)

    def applySearch(self):
        self._code = forceStringEx(self.edtCode.text())
        self._name = forceStringEx(self.edtName.text())
        self._mnn = forceStringEx(self.edtMnn.text())

        db = QtGui.qApp.db
        cond = []
        tableNomenclature = db.table('rbStockNomenclature')
        table = tableNomenclature

        if self._code:
            cond.append(tableNomenclature['code'].like(self._code))
        if self._name:
            cond.append(tableNomenclature['name'].like(self._name))
        if self._mnn:
            cond.append(tableNomenclature['mnn'].like(self._mnn))

        tableTarget = tableNomenclature
        idList = db.getIdList(table, tableTarget['id'].name(), cond, [tableTarget['name'].name(), tableTarget['code'].name()] )
        self.tblNomenclature.setIdList(idList)


    @pyqtSlot(QModelIndex)
    def on_tblFormularyItems_clicked(self, index):
        self.selectCurrentItem()

    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applySearch()
            self.tabWidget.setCurrentIndex(0)
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetSearch()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.tabWidget.currentIndex():
                self.applySearch()
                self.tabWidget.setCurrentIndex(0)
            else:
                if self.tblNomenclature.currentItemId():
                    self.selectCurrentItem()
#        if (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C):
#            self.tabWidget.setCurrentIndex(0)
#        if (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_G):
#            self.tabWidget.setCurrentIndex(1)
        QtGui.QFrame.keyPressEvent(self, event)


