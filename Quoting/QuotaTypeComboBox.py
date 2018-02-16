# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from RefBooks.QuotaType import getQuotaTypeClassItemsByExists
from Ui_RBQuotaTypeComboBoxPopup import Ui_RBQuotaTypeComboBoxPopup
from library.Utils import forceString
from library.crbcombobox import CRBComboBox, CRBModel, CRBSelectionModel


class CQuotaTypeComboBoxPopup(QtGui.QFrame, Ui_RBQuotaTypeComboBoxPopup):
    __pyqtSignals__ = ('quotaTypeSelected(int)',
                      )
    quotaTypeClassList = None
    def __init__(self, parent, tableName = ''):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self._mapClassName2Class = {}
        self._clientId = None
        self.clientBegDate = None
        self.clientEegDate = None
        self._addNone   = True
        self._tableName = tableName
        self._filier    = ''
        self._order     = ''
        self.id         = None
        self.table = QtGui.qApp.db.table('QuotaType')
        
        self.setupUi(self)
        
        self._applyQuotaTypeClassCombobox()
        self._model = parent._model
        self._selectionModel = CRBSelectionModel(self._model)
        self.tblQuotaType.setModel(self._model)
        self.tblQuotaType.setSelectionModel(self._selectionModel)
        self.edtDate.setDate(QtCore.QDate().currentDate())
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setShortcut(QtCore.Qt.Key_Return)
    
    def _applyQuotaTypeClassCombobox(self):
        for name, _class in getQuotaTypeClassItemsByExists():
            self._mapClassName2Class[name] = _class
            self.cmbVTMPClass.addItem(name)


    def setBegDate(self, date):
        self.clientBegDate = date

    def setEndDate(self, date):
        self.clientEndDate = date

    def setClientId(self, clientId):
        self._clientId = clientId
        self.setTable(self._tableName)

    def hideColumn(self, index):
        self.tblQuotaType.hideColumn(index)

    def rowCount(self, index):
        return self._model.rowCount()

    def searchCodeEx(self, searchString):
        return self._model.searchCodeEx(self._searchString)

    def setCurrentIndex(self, rowIndex):
        index = self._model.index(rowIndex, 1)
        self.tblQuotaType.setCurrentIndex(index)

    def currentIndex(self):
        return self.tblQuotaType.currentIndex()

    def setSelectionCurrentIndex(self, index, selectionFlags):
        self._selectionModel.setCurrentIndex(index, selectionFlags)

    def model(self):
        return self.tblQuotaType.model()

    def setViewFocus(self):
        self.tblQuotaType.setFocus()

    def view(self):
        return self.tblQuotaType

    def setTable(self, tableName, addNone=True, filter='', order=None):
        self._tableName = tableName
        self._addNone   = addNone
        self._filier    = filter
        self._order     = order
        cond = [self.table['isObsolete'].eq(0)]
        db = QtGui.qApp.db
        if self._clientId:
            condClient = []
            tableClientQuoting = db.table('Client_Quoting')
            tableQuotaType     = db.table('QuotaType')
            queryTable = tableClientQuoting.innerJoin(tableQuotaType, tableQuotaType['id'].eq(tableClientQuoting['quotaType_id']))
            condClient = [tableClientQuoting['deleted'].eq(0)]
            condClient.append(tableClientQuoting['master_id'].eq(self._clientId))
            if self.clientEndDate.isValid():
                condClient.append(tableClientQuoting['dateRegistration'].dateLe(self.clientEndDate))
            if self.clientBegDate.isValid():
                condClient.append(db.joinOr([
                                       tableClientQuoting['dateEnd'].dateGe(self.clientBegDate),
                                       tableClientQuoting['dateEnd'].dateGe(self.clientBegDate),
                                       'DATE('+tableClientQuoting['dateEnd'].name()+')='+'DATE(0000-00-00)'
                                      ])
                           )
            idList = db.getIdList(queryTable, 'QuotaType.id', condClient)
            idList += self.getChildrenIdList(idList)
            cond.append(self.table['id'].inlist(idList))
        if self.chkVTMPClass.isChecked():
            className = unicode(self.cmbVTMPClass.currentText())
            if className:
                _class = self._mapClassName2Class[className]
                cond.append(self.table['class'].eq(_class))
        if self.chkLimits.isChecked():
            tableQuoting = db.table('Quoting')
            checkedDate = self.edtDate.date()
            c = [tableQuoting['beginDate'].le(checkedDate)]
            c.append(tableQuoting['endDate'].ge(checkedDate))
            idList = db.getIdList(tableQuoting, 'quotaType_id', c)
            idList += self.getChildrenIdList(idList)
            index = self.cmbLimits.currentIndex()
            if index == 0:
                cond.append(self.table['id'].inlist(idList))
            elif index == 1:
                cond.append(self.table['id'].notInlist(idList))
        filter = db.joinAnd(cond)
        self._model.setTable(tableName, addNone, filter, order)

    def getChildrenIdList(self, idList):
        db = QtGui.qApp.db
        resume = []
        for id in idList:
            code = forceString(db.translate(self.table, 'id', id, 'code'))
            cond = [self.table['group_code'].eq(code)]
            resume += db.getIdList(self.table, 'id', cond)
        if resume:
            resume += self.getChildrenIdList(resume)
        return resume

    def setFilter(self, filter='', order=None):
        self._filier    = filter
        self._order     = order
        self.setTable(self._tableName, self._addNone, filter, order)

    def reloadData(self):
        self._model.setTable(self._tableName, self._addNone, self._filier, self._order)

    def setModel(self, model):
        self._model = model
        self.tblQuotaType.setModel(model)

    def selectItemByIndex(self, index):
        row = index.row()
        self.emit(QtCore.SIGNAL('quotaTypeSelected(int)'), row)
        self.hide()

    def _resize(self):
        parent = self.parent()
        pos = parent.rect().bottomLeft()
        pos2 = parent.rect().topLeft()
        pos = parent.mapToGlobal(pos)
        pos2 = parent.mapToGlobal(pos2)
        size = self.sizeHint()
        hHeaderSize = 0
        for column in [0, 1]:
            hHeaderSize += self.view().columnWidth(column)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        width = max(size.width(), parent.width(), hHeaderSize)
        size.setWidth(width)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self.move(pos)
        self.resize(size)
        self.view().resizeColumnToContents(0)
        scrollBar = self.view().horizontalScrollBar()
        scrollBar.setValue(0)

    def on_buttonBox_apply(self):
        self.setTable(self._tableName, self._addNone, self._filier, self._order)
        if self._model.rowCount() > 1:
            self.view().resizeColumnToContents(0)
            self.tabWidget.setCurrentIndex(0)

    def on_buttonBox_reset(self):
        self.chkVTMPClass.setChecked(True)
        self.chkLimits.setChecked(True)
        self.edtDate.setDate(QtCore.QDate().currentDate())
        self.cmbVTMPClass.setCurrentIndex(0)
        self.cmbLimits.setCurrentIndex(0)
        self.cmbVTMPClass.setEnabled(True)
        self.cmbLimits.setEnabled(True)
        self.setTable(self._tableName, self._addNone, self._filier, self._order)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply or button == 'enter':
            self.on_buttonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblQuotaType_clicked(self, index):
        self.selectItemByIndex(index)

class CQuotaTypeComboBox(CRBComboBox):
    __pyqtSignals__ = ('quotaTypeSelected(int)',
                      )

    def __init__(self, parent):
        super(CQuotaTypeComboBox, self).__init__(parent)
        self._model = CRBModel(self)
        self._searchString = ''
        self._selectionModel = CRBSelectionModel(self._model)
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.prefferedWidth = None
        self.popupView = CQuotaTypeComboBoxPopup(self)
        self.connect(self.popupView.tblQuotaType, QtCore.SIGNAL('hide()'), self.hidePopup)
        self.setModel(self._model)
        self.connect(self.popupView,QtCore.SIGNAL('quotaTypeSelected(int)'), self.setValueByRow)

    def model(self):
        return self._model

    def setTable(self, tableName, addNone=True, filter='', order=None):
        self.popupView.setTable(tableName, addNone, filter, order)

    def setFilter(self, filter='', order=None):
        self.popupView.setFilter(filter, order)

    def reloadData(self):
        self.popupView.reloadData()

    def setModel(self, model):
        self.popupView.setModel(model)
        CRBComboBox.setModel(self, model)

    def showPopup(self):
        self.popupView.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Reset)
        self.popupView._resize()
        self.popupView.show()
        self.popupView.tblQuotaType.setFocus()

    def currentIndex(self):
        return self.popupView.currentIndex()

    def lookup(self):
        i, self._searchString = self.popupView.searchCodeEx(self._searchString)
        if i>=0 and i!=self.currentIndex() :
            self.popupView.setCurrentIndex(i)

    def setValue(self, itemId):
        rowIndex = self._model.searchId(itemId)
        self.setIndex(rowIndex if rowIndex is not None else 0)

    def setValueByRow(self, rowIndex):
        itemId = self._model.getId(rowIndex)
        self.setValue(itemId)
        self.emit(QtCore.SIGNAL('quotaTypeSelected(int)'), itemId)

    def value(self):
        rowIndex = self.currentIndex().row()
        return self._model.getId(rowIndex)

    def setCode(self, code):
        rowIndex = self._model.searchCode(code)
        self.setCurrentIndex(rowIndex)

    def setIndex(self, rowIndex):
        self.popupView.setCurrentIndex(rowIndex)
        self.setCurrentIndex(rowIndex)

    def code(self):
        rowIndex = self.currentIndex()
        return self.model().getCode(rowIndex)

    def setShowFields(self, showFields):
        pass

    def setPrefferedWidth(self, prefferedWidth):
        pass

class CClientQuotingModelPatientComboBox(CQuotaTypeComboBox):
    def __init__(self, parent):
        CQuotaTypeComboBox.__init__(self, parent)
        self._model = CRBModel(self)
        self._searchString = ''
        self._selectionModel = CRBSelectionModel(self._model)
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.prefferedWidth = None
        self.popupView = CQuotaTypeComboBoxPopup(self, 'QuotaType')
        self.setModel(self._model)
        self._clientId = None
        self.connect(self.popupView,QtCore.SIGNAL('quotaTypeSelected(int)'), self.setValueByRow)

    def setClientId(self, clientId):
        self._clientId = clientId
        self.popupView.setClientId(self._clientId)

    def setBegDate(self, date):
        self.popupView.setBegDate(date)

    def setEndDate(self, date):
        self.popupView.setEndDate(date)

    def setShowFields(self, showFields):
        CRBComboBox.setShowFields(self, CRBComboBox.showCodeAndName)
