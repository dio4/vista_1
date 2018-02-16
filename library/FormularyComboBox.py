# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox    import CRBComboBox
from library.TableModel     import CTableModel, CTextCol, CRefBookCol
from library.Utils          import forceRef, forceStringEx, toVariant

from Ui_FormularyComboBoxPopup import Ui_FormularyComboBoxPopup


class CFormularyComboBox(CRBComboBox):
    def __init__(self, parent, filter = None):
        CRBComboBox.__init__(self, parent)
        self.setTable('vrbDrugFormulary_Item')
        self._filter = filter
        self._popup = None

    def setQValue(self, var):
        self.setValue(forceRef(var))

    def showPopup(self):
        if not self._popup:
            self._popup = CFormularyComboBoxPopup(self, self._filter)
            self.connect(self._popup,QtCore.SIGNAL('itemSelected(QVariant)'), self.setQValue)
        #self._popup.setDefaults(self.defaultClass, self.defaultType)
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        width= max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()

class CFormularyComboBoxPopup(QtGui.QFrame, Ui_FormularyComboBoxPopup):
    __pyqtSignals__ = ('itemSelected(int)',
                      )

    def __init__(self, parent=None, filter=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self._parent = parent
        self._filter = filter
        self.setupUi(self)
        self.model  = CFormularyModel(self)
        self.tblFormulary.setModel(self.model)
        self.tblFormulary.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.initSearch()

    def show(self):
        self.resetSearch()
        self.applySearch()
        self.tblFormulary.setFocus()
        id = self._parent.value()
        if id:
            self.tblFormulary.setCurrentItemId(self._parent.value())
        else:
            self.tblFormulary.setCurrentRow(0)
        QtGui.QFrame.show(self)

    def selectCurrentItem(self):
        id = self.tblFormulary.currentItemId()
        self.emit(QtCore.SIGNAL('itemSelected(QVariant)'), toVariant(id))
        self.hide()

    def initSearch(self):
        self._code = ''
        self._name = ''
        self._tradeName = ''
        self._mnn = ''

    def resetSearch(self):
        self.initSearch()
        self.edtCode.setText(self._code)
        self.edtName.setText(self._name)
        self.edtTradeName.setText(self._tradeName)
        self.edtMnn.setText(self._mnn)

    def applySearch(self):
        self._code = forceStringEx(self.edtCode.text())
        self._name = forceStringEx(self.edtName.text())
        self._tradeName = forceStringEx(self.edtTradeName.text())
        self._mnn = forceStringEx(self.edtMnn.text())

        db = QtGui.qApp.db
        cond = []
        tableFormulary = db.table('vrbDrugFormulary_Item')
        table = tableFormulary

        if self._code:
            cond.append(tableFormulary['code'].like(self._code))
        if self._name:
            cond.append(tableFormulary['name'].like('%' + self._name + '%'))
        if self._tradeName:
            cond.append(tableFormulary['tradeName'].like('%' + self._tradeName + '%'))
        if self._mnn:
            cond.append(tableFormulary['mnn'].like('%' + self._mnn + '%'))
        if self._filter and len(self._filter) > 0:
            cond.append(self._filter)
        tableTarget = tableFormulary
        idList = db.getIdList(table, tableTarget['id'].name(), cond, [tableTarget['name'].name(), tableTarget['code'].name()] )
        self.tblFormulary.setIdList(idList)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblFormulary_clicked(self, index):
        self.selectCurrentItem()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applySearch()
            self.tabWidget.setCurrentIndex(0)
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetSearch()

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            if self.tabWidget.currentIndex():
                self.applySearch()
                self.tabWidget.setCurrentIndex(0)
            else:
                if self.tblFormulary.currentItemId():
                    self.selectCurrentItem()
        QtGui.QFrame.keyPressEvent(self, event)


class CFormularyModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(     u'Код',                      ['code'],            20),
            CTextCol(     u'Формулярное наименование', ['name'],            60),
            CRefBookCol(  u'Торговое наименование',    ['tradeName_id'],    'dlo_rbTradeName', 60)
            ], 'vrbDrugFormulary_Item' )
