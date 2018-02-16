# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox    import CRBComboBox
from library.InDocTable     import CRBInDocTableCol
from library.TableModel     import CTableModel, CTextCol
from library.Utils          import forceRef, forceStringEx, toVariant

from Ui_NomenclatureComboBoxPopup import Ui_NomenclatureComboBoxPopup


class CNomenclatureComboBox(CRBComboBox):
    def __init__(self, parent):
        CRBComboBox.__init__(self, parent)
        self.setTable('rbNomenclature')
        self.defaultClassId = None
        self.defaultKindId = None
        self.defaultTypeId = None
        self._popup = None


    def setDefaultIds(self, classId, kindId, typeId):
        self.defaultClassId = classId
        self.defaultKindId = kindId
        self.defaultTypeId = typeId


    def setQValue(self, var):
        self.setValue(forceRef(var))


    def showPopup(self):
#        self.__searchString = ''
        if not self._popup:
            self._popup = CNomenclatureComboBoxPopup(self)
            self.connect(self._popup,QtCore.SIGNAL('itemSelected(QVariant)'), self.setQValue)
        self._popup.setDefaultIds(self.defaultClassId, self.defaultKindId, self.defaultTypeId)
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


class CNomenclatureInDocTableCol(CRBInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, 'rbNomenclature', **params)
        self.defaultClassId = None
        self.defaultKindId = None
        self.defaultTypeId = None


    def setDefaultClassId(self, classId):
        self.defaultClassId = classId


    def setDefaultKindId(self, kindId):
        self.defaultKindId = kindId


    def setDefaultTypeId(self, typeId):
        self.defaultTypeId = typeId


    def createEditor(self, parent):
        editor = CNomenclatureComboBox(parent)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        editor.setDefaultIds(self.defaultClassId, self.defaultKindId, self.defaultTypeId)
        return editor



class CNomenclatureComboBoxPopup(QtGui.QFrame, Ui_NomenclatureComboBoxPopup):
    __pyqtSignals__ = ('itemSelected(int)',
                      )

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self._parent = parent
        self.setupUi(self)
        self.model  = CNomenclatureModel(self)
        self.tblNomenclature.setModel(self.model)
        self.tblNomenclature.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.cmbClass.setTable('rbNomenclatureClass', True)
        self.cmbKind.setTable('rbNomenclatureKind', True)
        self.cmbType.setTable('rbNomenclatureType', True)

        self._defaultClassId = None
        self._defaultKindId = None
        self._defaultTypeId = None
        self.initSearch()
#        self.cmbClass.installEventFilter(self)


    def setDefaultIds(self, classId, kindId, typeId):
        self._defaultClassId = classId
        self._defaultKindId = kindId
        self._defaultTypeId = typeId


    def show(self):
        self.resetSearch()
        self.applySearch()
        self.tblNomenclature.setFocus()
        id = self._parent.value()
        if id:
            self.tblNomenclature.setCurrentItemId(self._parent.value())
        else:
            self.tblNomenclature.setCurrentRow(0)
        QtGui.QFrame.show(self)


    def selectCurrentItem(self):
        id = self.tblNomenclature.currentItemId()
        self.emit(QtCore.SIGNAL('itemSelected(QVariant)'), toVariant(id))
        self.hide()


    def initSearch(self):
        self._classId = self._defaultClassId
        self._kindId = self._defaultKindId
        self._typeId = self._defaultTypeId
        self._code = ''
        self._name = ''
        self._producer = ''
        self._ATC = ''
        self._includeAnalogies = False


    def resetSearch(self):
        self.initSearch()
        self.cmbClass.setValue(self._classId)
        self.cmbKind.setValue(self._kindId)
        self.cmbType.setValue(self._typeId)
        self.edtCode.setText(self._code)
        self.edtName.setText(self._name)
        self.edtProducer.setText(self._producer)
        self.edtATC.setText(self._ATC)
        self.chkIncludeAnalogies.setChecked(self._includeAnalogies)


    def applySearch(self):
        self._classId = self.cmbClass.value()
        self._kindId = self.cmbKind.value()
        self._typeId = self.cmbType.value()
        self._code = forceStringEx(self.edtCode.text())
        self._name = forceStringEx(self.edtName.text())
        self._producer = forceStringEx(self.edtProducer.text())
        self._ATC = forceStringEx(self.edtATC.text())
        self._includeAnalogies = self.chkIncludeAnalogies.isChecked()

        db = QtGui.qApp.db
        cond = []
        tableNomenclature = db.table('rbNomenclature')
        table = tableNomenclature

        if self._typeId:
            cond.append(tableNomenclature['type_id'].eq(self._typeId))
        elif self._kindId or self._classId:
            tableType = db.table('rbNomenclatureType')
            table = table.leftJoin(tableType, tableType['id'].eq(tableNomenclature['type_id']))
            if self._kindId:
                cond.append(tableType['kind_id'].eq(self._kindId))
            else:
                tableKind = db.table('rbNomenclatureKind')
                table = table.leftJoin(tableKind, tableKind['id'].eq(tableType['kind_id']))
                cond.append(tableKind['class_id'].eq(self._classId))
        if self._code:
            cond.append(tableNomenclature['code'].like(self._code))
        if self._name:
            cond.append(tableNomenclature['name'].like(self._name))
        if self._producer:
            cond.append(tableNomenclature['producer'].like(self._producer))
        if self._ATC:
            cond.append(tableNomenclature['ATC'].like(self._ATC))
        if self._includeAnalogies and cond:
            tableTarget = db.table('rbNomenclature').alias('A')
            table = table.leftJoin(tableTarget,
                                   db.joinOr([
                                       db.joinAnd( [tableTarget['analog_id'].isNotNull(),
                                                    tableTarget['analog_id'].eq(tableNomenclature['analog_id'])] ),
                                       db.joinAnd( [tableTarget['analog_id'].isNull(),
                                                    tableTarget['id'].eq(tableNomenclature['id'])] )
                                              ]))
        else:
            tableTarget = tableNomenclature
        idList = db.getIdList(table, tableTarget['id'].name(), cond, [tableTarget['name'].name(), tableTarget['code'].name()] )
        self.tblNomenclature.setIdList(idList)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblNomenclature_clicked(self, index):
        self.selectCurrentItem()


    @QtCore.pyqtSlot(int)
    def on_cmbClass_currentIndexChanged(self, index):
        classId = self.cmbClass.value()
        if classId:
            table = QtGui.qApp.db.table('rbNomenclatureKind')
            self.cmbKind.setFilter(table['class_id'].eq(classId))
        else:
            self.cmbKind.setFilter('')


    @QtCore.pyqtSlot(int)
    def on_cmbKind_currentIndexChanged(self, index):
        kindId = self.cmbKind.value()
        if kindId:
            table = QtGui.qApp.db.table('rbNomenclatureType')
            self.cmbType.setFilter(table['kind_id'].eq(kindId))
        else:
            self.cmbType.setFilter('')


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applySearch()
            self.tabWidget.setCurrentIndex(0)
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetSearch()

#    def eventFilter(self, obj, event):
#        if event.type() == QEvent.KeyPress:
#            key = event.key()
#            if key in (Qt.Key_C, Qt.Key_G):
#                if key == Qt.Key_C:
#                    obj.keyPressEvent(event)
#                self.keyPressEvent(event)
#                return False
#            if  key == Qt.Key_Tab:
#                self.focusNextPrevChild(True)
#                return True
#        return False


    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
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


class CNomenclatureModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(     u'Код',            ['code'],  20),
            CTextCol(     u'Наименование',   ['name'],  60),
            ], 'rbNomenclature' )
