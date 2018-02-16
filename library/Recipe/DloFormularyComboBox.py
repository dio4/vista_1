# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox    import CRBComboBox
from library.TableModel     import CTableModel, CTextCol, CRefBookCol, CIntCol
from library.Utils          import forceRef, forceStringEx, toVariant

from library.Ui_FormularyComboBoxPopup import Ui_FormularyComboBoxPopup


class CDloFormularyComboBox(CRBComboBox):
    def __init__(self, parent, filter = None):
        CRBComboBox.__init__(self, parent)
        self.setTable('DloDrugFormulary_Item', filter='isSprPC = 1')
        self._filter = filter
        self._popup = None

    def setQValue(self, var):
        self.setValue(forceRef(var))

    def setFilter(self, filter='', order=None):
        CRBComboBox.setFilter(self, filter, order)
        if self._popup is not None:
            self._popup.setFilter(filter)

    def showPopup(self):
        if not self._popup:
            self._popup = CDloFormularyComboBoxPopup(self, self._filter)
            self.connect(self._popup,QtCore.SIGNAL('itemSelected(QVariant)'), self.setQValue)
        #self._popup.setDefaults(self.defaultClass, self.defaultType)
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        size.setHeight(400)
        width= max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()

class CDloFormularyComboBoxPopup(QtGui.QFrame, Ui_FormularyComboBoxPopup):
    __pyqtSignals__ = ('itemSelected(int)',
                      )

    def __init__(self, parent=None, filter=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self._parent = parent
        self._filter = filter
        self.setupUi(self)
        self.model  = CDloFormularyModel(self)
        self.tblFormulary.setModel(self.model)
        self.tblFormulary.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblFormulary.setColumnWidth(0, 60)
        self.tblFormulary.setColumnWidth(1, 400)
        self.tblFormulary.setColumnWidth(2, 200)
        self.tblFormulary.setColumnWidth(3, 70)
        self.tblFormulary.setColumnWidth(4, 80)

        self.initSearch()

    def setFilter(self, filter):
        self._filter = filter

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
        tableFormulary = db.table('DloDrugFormulary_Item')
        tableTradeNames = db.table('dlo_rbTradeName')
        table = tableFormulary

        if self._code:
            cond.append(tableFormulary['code'].like(self._code))
        if self._name:
            cond.append(tableFormulary['name'].like('%' + self._name + '%'))
        if self._tradeName:
            subCond = [ tableTradeNames['name'].like('%' + self._tradeName + '%') ]
            cond.append(db.joinAnd(subCond))
        if self._mnn:
            cond.append(tableFormulary['mnn'].like('%' + self._mnn + '%'))
        if self._filter and len(self._filter) > 0:
            cond.append(self._filter)
        cond.append(table['isSprPC'].eq(1))
        tableTarget = tableFormulary.leftJoin(tableTradeNames, tableFormulary['tradeName_id'].eq(tableTradeNames['id']))
        idList = db.getIdList(tableTarget, table['id'].name(), cond, [table['name'].name(), table['code'].name()])
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

class CDloFormularyModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CIntCol(     u'Код',                       ['code'],            60),
            CTextCol(     u'Формулярное наименование', ['name'],            400),
            CTextCol(u'Производитель', ['producer'], 200),
            CRefBookCol(  u'Торговое наименование',    ['tradeName_id'],    'dlo_rbTradeName', 200),
            CIntCol(     u'Кол-во',                    ['dosageQnt'],             70),
            CRefBookCol(  u'Дозировка',                ['dosage_id'],       'dlo_rbDosage', 80),
            ], 'DloDrugFormulary_Item')
