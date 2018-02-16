# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getEventAcceptablePolicyList, getClientRepresentativePolicyList
from library.database import CTableRecordCache
from library.DialogBase import CConstructHelperMixin
from library.TableModel import CTableModel, CTextCol, CDateCol
from library.Utils import forceDate, forceString

from Ui_ClientPolicyComboBoxPopup import Ui_ClientPolicyComboBoxPopup


class CClientPolicyModel(CTableModel):

    def __init__(self, parent):
        CTableModel.__init__(self, parent, cols=[
            CTextCol(u'Серия', ['serial'], 16),
            CTextCol(u'Номер', ['number'], 35),
            CTextCol(u'Тип', ['policyType'], 40),
            CTextCol(u'Вид', ['policyKind'], 40),
            CDateCol(u'Дата выдачи', ['begDate'], 14),
            CDateCol(u'Дата окончания', ['endDate'], 14),
            CDateCol(u'Дата погашения', ['dischargeDate'], 14),
            CTextCol(u'Территория страхования', ['insuranceArea'], 25),
            CTextCol(u'Страховая компания', ['insurerName'], 50),
            CTextCol(u'ОГРН', ['insurerOGRN'], 15),
            CTextCol(u'ОКАТО', ['insurerOKATO'], 15),
            CTextCol(u'Примечание', ['note'], 25)
        ])
        self.setTable('ClientPolicy')

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        ClientPolicy = db.table('ClientPolicy')
        PolicyKind = db.table('rbPolicyKind')
        PolicyType = db.table('rbPolicyType')
        Insurer = db.table('Organisation')
        cols = [
            ClientPolicy['serial'].alias('serial'),
            ClientPolicy['number'].alias('number'),
            ClientPolicy['begDate'].alias('begDate'),
            ClientPolicy['endDate'].alias('endDate'),
            ClientPolicy['dischargeDate'].alias('dischargeDate'),
            ClientPolicy['insuranceArea'].alias('insuranceArea'),
            ClientPolicy['note'].alias('note'),
            PolicyType['name'].alias('policyType'),
            PolicyKind['name'].alias('policyKind'),
            Insurer['fullName'].alias('insurerName'),
            Insurer['OGRN'].alias('insurerOGRN'),
            Insurer['OKATO'].alias('insurerOKATO')
        ]
        queryTable = ClientPolicy.leftJoin(PolicyKind, PolicyKind['id'].eq(ClientPolicy['policyKind_id']))
        queryTable = queryTable.leftJoin(PolicyType, PolicyType['id'].eq(ClientPolicy['policyType_id']))
        queryTable = queryTable.leftJoin(Insurer, Insurer['id'].eq(ClientPolicy['insurer_id']))
        self._table = queryTable
        self._recordsCache = CTableRecordCache(db, self._table, cols, recordCacheCapacity)


class CClientPolicyComboBoxPopup(QtGui.QFrame, CConstructHelperMixin, Ui_ClientPolicyComboBoxPopup):

    def __init__(self, parent, clientId=None, date=QtCore.QDate.currentDate()):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)

        self._clientId = clientId
        self._date = date
        self._policyTypeId = None
        self._policyFromRepresentative = False
        self._eventIsClosed = False

        self.setupUi(self)

        self.cmbPolicyType.setTable('rbPolicyType', True)
        self.cmbPolicyType.setCurrentIndex(0)

        self.cmbPolicyKind.setTable('rbPolicyKind', True)
        self.cmbPolicyKind.setCurrentIndex(0)

        self.connect(self.buttonBox, QtCore.SIGNAL('clicked(QAbstractButton*)'), self.buttonBoxClicked)
        self.connect(self.tblClientPolicy, QtCore.SIGNAL('clicked(QModelIndex)'), self.itemSelected)

    def view(self):
        return self.tblClientPolicy

    def itemSelected(self, index):
        itemId = self.tblClientPolicy.itemId(index)
        self.emit(QtCore.SIGNAL('clientPolicyClicked(int)'), itemId)

    def model(self):
        return self._model

    def setModel(self, model):
        self._model = model
        self._selectionModel = QtGui.QItemSelectionModel(self._model, self)
        self.setModels(self.tblClientPolicy, self._model, self._selectionModel)

    def buttonBoxClicked(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QtGui.QDialogButtonBox.ApplyRole:
            self.updateClientPolicy()
        elif role == QtGui.QDialogButtonBox.ResetRole:
            self.cmbPolicyType.setCurrentIndex(0)
            self.cmbPolicyKind.setCurrentIndex(0)
            self.updateClientPolicy()

    def setClientId(self, clientId):
        self._clientId = clientId

    def setDate(self, date):
        self._date = date

    def setPolicyTypeId(self, policyTypeId):
        self._policyTypeId = policyTypeId

    def setPolicyFromRepresentative(self, value):
        self._policyFromRepresentative = value

    def setEventIsClosed(self, closed):
        self._eventIsClosed = closed

    def setTabByTableUpdating(self, policyIsFound):
        if policyIsFound:
            self.tabWidget.setCurrentIndex(0)
        else:
            self.tabWidget.setCurrentIndex(1)

    def getAcceptablePolicyList(self):
        policyTypeId = self.cmbPolicyType.value() or self._policyTypeId
        policyKindId = self.cmbPolicyKind.value()
        return getEventAcceptablePolicyList(self._clientId, policyTypeId, policyKindId, self._date, self._eventIsClosed)

    def getRepresentativePolicyList(self):
        policyTypeId = self.cmbPolicyType.value() or self._policyTypeId
        policyKindId = self.cmbPolicyKind.value()
        return getClientRepresentativePolicyList(self._clientId, policyTypeId, policyKindId, self._date)

    def updateClientPolicy(self):
        idList = self.getRepresentativePolicyList() if self._policyFromRepresentative else self.getAcceptablePolicyList()
        self._model.setIdList(idList)
        self._model.reset()
        self.setTabByTableUpdating(len(idList) > 0)

    def setValue(self, value):
        self.tblClientPolicy.setCurrentItemId(value)

    def value(self):
        itemId = self.tblClientPolicy.currentItemId()
        return itemId if itemId != 0 else None


class CClientPolicyComboBox(QtGui.QComboBox):
    pyqtSignals = ('clientPolicyChanged(int)',
                   )

    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self._model = CClientPolicyModel(self)
        self._popup = CClientPolicyComboBoxPopup(self)
        self._popup.setModel(self._model)
        self.setModel(self._model)

        self._policyId = None

        self.connect(self._popup, QtCore.SIGNAL('clientPolicyClicked(int)'), self.setValue)
        self.connect(self._popup.model(), QtCore.SIGNAL('modelReset()'), self.setLastActual)

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

    def setClientId(self, clientId):
        self._popup.setClientId(clientId)

    def setDate(self, date):
        self._popup.setDate(date)

    def setPolicyTypeId(self, policyTypeId):
        self._popup.setPolicyTypeId(policyTypeId)

    def setPolicyFromRepresentative(self, value):
        self._popup.setPolicyFromRepresentative(value)

    def setEventIsClosed(self, closed=True):
        self._popup.setEventIsClosed(closed)

    def updatePolicy(self, date=None):
        if not date is None:
            self.setDate(date)
        self._popup.updateClientPolicy()
        self.setLastActual()

    def showPopup(self):
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()

    def setValue(self, id):
        if not id is None:
            self.emit(QtCore.SIGNAL('clientPolicyChanged(int)'), id)
        self._policyId = id if id else None
        self.updateText()
        self._popup.hide()

    @QtCore.pyqtSlot()
    def setLastActual(self):
        idList = self._model.idList()
        self.setValue(idList[-1] if idList else None)

    def value(self):
        return self._policyId

    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        QtGui.QComboBox.setCurrentIndex(self, index.row())

    def updateText(self):
        text = u'не выбран'
        record = self._popup.model().getRecordById(self._policyId)
        isRepresentative = self._popup._policyFromRepresentative
        if not record is None:
            begDateStr = forceDate(record.value('begDate')).toString('dd.MM.yyyy')
            endDateStr = forceDate(record.value('endDate')).toString('dd.MM.yyyy')
            text = u'{isRepr}{policyType} {policyKind}, серия {serial} номер {number}, дата выдачи {begDate}, дата окончания {endDate}, СМО: {insurer}, примечание: {note}'.format(
                isRepr=(u'(Полис представителя) ' if isRepresentative else u''),
                policyType=forceString(record.value('policyType')),
                policyKind=forceString(record.value('policyKind')),
                serial=forceString(record.value('serial')),
                number=forceString(record.value('number')),
                begDate=begDateStr if begDateStr else u'не указана',
                endDate=endDateStr if endDateStr else u'не указана',
                insurer=forceString(record.value('insurerName')),
                note=forceString(record.value('note'))
            )

        self.setEditText(text)
