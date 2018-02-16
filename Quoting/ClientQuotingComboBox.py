# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase import CConstructHelperMixin
from library.TableModel import CTableModel, CEnumCol, CRefBookCol, CTextCol
from library.Utils      import forceInt, forceRef

from RefBooks.QuotaType import getQuotaTypeClassItemsByExists

from Ui_ClientQuotingComboBoxPopup import Ui_Form


class CClientQuotingComboBoxPopup(QtGui.QFrame, CConstructHelperMixin, Ui_Form):
    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self._mapClassName2Class = {}
        self._clientId = None
        self._dBegDate = QtCore.QDate.currentDate()
        self._dEndDate = QtCore.QDate.currentDate()

        self.setupUi(self)

        self._applyQuotaTypeClassCombobox()
        self.connect(self.buttonBox, QtCore.SIGNAL('clicked(QAbstractButton*)'), self.buttonBoxClicked)
        self.connect(self.tblClientQuoting, QtCore.SIGNAL('clicked(QModelIndex)'), self.itemSelected)

    def _applyQuotaTypeClassCombobox(self):
        for name, _class in getQuotaTypeClassItemsByExists():
            self._mapClassName2Class[name] = _class
            self.cmbClass.addItem(name)

    def view(self):
        return self.tblClientQuoting

    def setBegDate(self, date):
        self._dBegDate = date
        self.edtBegDate.setDate(date)

    def setEndDate(self, date):
        self._dEndDate = date
        self.edtEndDate.setDate(date)

    def itemSelected(self, index):
        itemId = self.tblClientQuoting.itemId(index)
        self.emit(QtCore.SIGNAL('clientQuotingClicked(int)'), itemId)

    def setModel(self, model):
        self._model = model
        self._selectionModel = QtGui.QItemSelectionModel(self._model, self)
        self.setModels(self.tblClientQuoting, self._model, self._selectionModel)

    def buttonBoxClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QtGui.QDialogButtonBox.AcceptRole:
            self.updateClientQuoting()
        elif role == QtGui.QDialogButtonBox.ResetRole:
            self.chkClass.setChecked(True)
            self.chkClass.emit(QtCore.SIGNAL('clicked(bool)'), True)
            self.chkBegDate.setChecked(False)
            self.chkBegDate.emit(QtCore.SIGNAL('clicked(bool)'), False)
            self.chkStatus.setChecked(False)
            self.chkStatus.emit(QtCore.SIGNAL('clicked(bool)'), False)
            self.edtBegDate.setDate(self._dBegDate)
            self.edtEndDate.setDate(self._dEndDate)
            self.updateClientQuoting()

    def setClientId(self, clientId):
        self._clientId = clientId
        self.updateClientQuoting()

    def setTabByTableUpdating(self, smthIsFound):
        if smthIsFound:
            self.tabWidget.setCurrentIndex(0)
        else:
            self.tabWidget.setCurrentIndex(1)

    def updateClientQuoting(self):
        db = QtGui.qApp.db

        tableClientQuoting = db.table('Client_Quoting')
        tableQuotaType     = db.table('QuotaType')

        queryTable = tableClientQuoting.innerJoin(tableQuotaType, tableQuotaType['id'].eq(tableClientQuoting['quotaType_id']))

        cond = [tableQuotaType['deleted'].eq(0),
                    tableQuotaType['isObsolete'].eq(0)]
        if self._clientId:
            cond.append(tableClientQuoting['master_id'].eq(self._clientId))

        cols = ['Client_Quoting.id']
        cond.append(tableClientQuoting['deleted'].eq(0))
        if self.chkBegDate.isChecked():
            begDate = self.edtBegDate.date()
            endDate = self.edtEndDate.date()
            if endDate.isValid():
                cond.append(tableClientQuoting['dateRegistration'].dateLe(endDate))
            if begDate.isValid():
                cond.append(db.joinOr([
                                       tableClientQuoting['dateEnd'].dateGe(begDate),
                                       tableClientQuoting['dateEnd'].dateGe(begDate),
                                       'DATE('+tableClientQuoting['dateEnd'].name()+')='+'DATE(0000-00-00)'
                                      ])
                           )
        if self.chkStatus.isChecked():
            cond.append(tableClientQuoting['status'].eq(self.cmbStatus.currentIndex()))

        if self.chkClass.isChecked():
            className = unicode(self.cmbClass.currentText())
            _class = self._mapClassName2Class[className]
            cond.append(tableQuotaType['class'].eq(_class))

        idList = db.getIdList(queryTable, cols, cond)
        self._model.setIdList([0]+idList)
        self._model.reset()
        self.setTabByTableUpdating(len(idList)>0)

    def setValue(self, value):
        self.tblClientQuoting.setCurrentItemId(value)

    def value(self):
        return self.tblClientQuoting.currentItemId()

    def getItemRowIndex(self, itemId):
        idList = self._model.idList()
        if itemId in idList:
            rowIndex = idList.index(itemId)
        else:
            rowIndex = -1
        return rowIndex

class CClientQuotingComboBox(QtGui.QComboBox):
    def __init__(self, parent, clientId=None, begDate=QtCore.QDate(), endDate=QtCore.QDate()):
        QtGui.QComboBox.__init__(self, parent)
        # self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        # self.preferedWidth = 500
        self._clientId = clientId
        self._popup = CClientQuotingComboBoxPopup(self)
        self._model = CClientQuotingModel(self)
        self.setModel(self._model)
        self.setBegDate(begDate)
        self.setEndDate(endDate)
        self._popup.setClientId(self._clientId)
        self.connect(self._popup, QtCore.SIGNAL('clientQuotingClicked(int)'), self.on_clientQuotingClicked)

    def setBegDate(self, date):
        self._popup.setBegDate(date)

    def setEndDate(self, date):
        self._popup.setEndDate(date)

    def setClientId(self, clientId):
        self._clientId = clientId
        self._popup.setClientId(self._clientId)

    def on_clientQuotingClicked(self, itemId):
        self.setValue(itemId)
        self._popup.hide()

    def setModel(self, model):
        QtGui.QComboBox.setModel(self, model)
        self.setModelColumn(1)
        self._popup.setModel(model)

    def showPopup(self):
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self.sizeHint()
        hHeaderSize = 0
        size = self._popup.sizeHint()
        width= max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
#        width= max(self.width(), self.preferedWidth)
#        size.setWidth(width)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.updateClientQuoting()

    def value(self):
        value = self._popup.value()
        return value

    def setValue(self, value):
        self._popup.setValue(value)
        rowIndex = self._popup.getItemRowIndex(value)
        self.setCurrentIndex(rowIndex)

# ####################################################
class CClassCol(CEnumCol):
    def format(self, values):
        quotaTypeId = forceRef(values[0])
        if quotaTypeId:
            i = forceInt(QtGui.qApp.db.translate('QuotaType', 'id', quotaTypeId, 'class'))
            if 0 <= i <len(self._vallist):
                return QtCore.QVariant(self._vallist[i])
            else:
                return QtCore.QVariant('{%d}' % i)
        return QtCore.QVariant()

class CStatusEnumCol(CEnumCol):
    def format(self, values):
        val = values[0]
        if val.isValid():
            return CEnumCol.format(self, values)
        return QtCore.QVariant()

class CClientQuotingModel(CTableModel):
    def __init__(self, parent):
        self._nullRecord = None
        CTableModel.__init__(self, parent, cols=[
            CClassCol(u'Класс', ['quotaType_id'], [u'ВТМП', u'СМП', u'Родовой сертификат', u'Платные', u'ОМС', u'ВМП из ОМС', u'ВМП сверх базового', u'АКИ'], 10),
            CRefBookCol(u'Тип', ['quotaType_id'], 'QuotaType', 16, 2),
            CTextCol(u'Номер', ['quotaTicket'], 6),
            CTextCol(u'МКБ', ['MKB'], 6),
            CStatusEnumCol(u'Статус', ['status'], [u'Отменено',
                                                   u'Ожидание',
                                                   u'Активный талон',
                                                   u'Талон для заполнения',
                                                   u'Заблокированный талон',
                                                   u'Отказано',
                                                   u'Необходимо согласовать дату обслуживания',
                                                   u'Дата обслуживания на согласовании',
                                                   u'Дата обслуживания согласована',
                                                   u'Пролечен',
                                                   u'Обслуживание отложено',
                                                   u'Отказ пациента',
                                                   u'Импортировано из ВТМП'], 10)],
            tableName='Client_Quoting')

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        row    = index.row()
        id     = self._idList[row]
        if id == 0 and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant('-')
        else:
            return CTableModel.data(self, index, role)

