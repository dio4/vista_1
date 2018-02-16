# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox    import CRBComboBox
from library.InDocTable     import CRBInDocTableCol
from library.TableModel     import CTableModel, CTextCol
from library.Utils          import forceRef, forceStringEx, toVariant

from Ui_FormularyItemComboBoxPopup import Ui_FormularyItemComboBoxPopup

class CFormularyItemComboBox(CRBComboBox):
    def __init__(self, parent):
        CRBComboBox.__init__(self, parent)
        self.setTable('rbMedicines')
        self._popup = None

    def setQValue(self, var):
        self.setValue(forceRef(var))

    def showPopup(self):
        if not self._popup:
            self._popup = CFormularyItemComboBoxPopup(self)
            self.connect(self._popup,QtCore.SIGNAL('itemSelected(QVariant)'), self.setQValue)
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


class CFormularyItemInDocTableCol(CRBInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, 'rbMedicines', **params)

    def createEditor(self, parent):
        editor = CFormularyItemComboBox(parent)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor

class CFormularyItemComboBoxPopup(QtGui.QFrame, Ui_FormularyItemComboBoxPopup):
    __pyqtSignals__ = ('itemSelected(int)',
                      )

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self._parent = parent
        self.setupUi(self)
        self.model  = CFormularyItemModel(self)
        self.tblFormularyItem.setModel(self.model)
        self.tblFormularyItem.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.initSearch()

    def show(self):
        self.resetSearch()
        self.applySearch()
        self.tblFormularyItem.setFocus()
        id = self._parent.value()
        if id:
            self.tblFormularyItem.setCurrentItemId(self._parent.value())
        else:
            self.tblFormularyItem.setCurrentRow(0)
        QtGui.QFrame.show(self)


    def selectCurrentItem(self):
        id = self.tblFormularyItem.currentItemId()
        self.emit(QtCore.SIGNAL('itemSelected(QVariant)'), toVariant(id))
        self.hide()


    def initSearch(self):
        self._code = ''
        self._name = ''

    def resetSearch(self):
        self.initSearch()
        self.edtCode.setText(self._code)
        self.edtName.setText(self._name)

    def applySearch(self):
        self._code = forceStringEx(self.edtCode.text())
        self._name = forceStringEx(self.edtName.text())

        db = QtGui.qApp.db
        cond = []
        tableFormularyItem = db.table('rbMedicines')
        table = tableFormularyItem

        if self._code:
            cond.append(tableFormularyItem['code'].like('%' + self._code + '%'))
        if self._name:
            cond.append(tableFormularyItem['name'].like('%' + self._name + '%'))

        tableTarget = tableFormularyItem
        idList = db.getIdList(table, tableTarget['id'].name(), cond, [tableTarget['name'].name(), tableTarget['code'].name()] )
        self.tblFormularyItem.setIdList(idList)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblFormularyItem_clicked(self, index):
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
                if self.tblFormularyItem.currentItemId():
                    self.selectCurrentItem()
#        if (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C):
#            self.tabWidget.setCurrentIndex(0)
#        if (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_G):
#            self.tabWidget.setCurrentIndex(1)
        QtGui.QFrame.keyPressEvent(self, event)


class CFormularyItemModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(     u'Код',            ['code'],  20),
            CTextCol(     u'Наименование',   ['name'],  60),
            ], 'rbMedicines' )
