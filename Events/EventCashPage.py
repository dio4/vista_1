# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Events.Action import CActionTypeCache, CActionType
from Events.ActionsSummaryModel import CAccActionsSummary
from Events.EventInfo import CEventLocalContractInfo
from library.DialogBase import CConstructHelperMixin
from library.InDocTable import CInDocTableView, CInDocTableModel, CInDocTableCol, CDateInDocTableCol, \
    CEnumInDocTableCol, CFloatInDocTableCol, CRBInDocTableCol
from library.interchange import setDateEditValue, setDatetimeEditValue, setLineEditValue, setRBComboBoxValue, \
    setTextEditValue, getDateEditValue, getLineEditValue, getRBComboBoxValue, \
    getTextEditValue
from library.Utils import forceDouble, forceInt, forceRef, forceString, toVariant, splitDocSerial
from Orgs.Orgs import CBankInDocTableCol, selectOrganisation
from RefBooks.Tables import rbCashOperation, rbDocumentType

from Ui_EventCashPage import Ui_EventCashPageWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class CFastEventCashPage(QtGui.QWidget, Ui_EventCashPageWidget, CConstructHelperMixin):
    localContractTableName = 'Event_LocalContract'
    isControlsCreate = False
    accSum = 0.0
    paymentsSum = 0.0
    sumLimit = ''

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.localContractRecord = QtGui.qApp.db.dummyRecord()
        self._isEditable = True

    def setEditable(self, editable):
        self._isEditable = editable
        self._updateEditable()

    def _updateEditable(self):
        if hasattr(self, 'modelAccActions') and hasattr(self, 'modelPayments'):
            self.modelAccActions.setEditable(self._isEditable)
            self.modelPayments.setEditable(self._isEditable)
        if hasattr(self, 'tabCoordination'):
            self.tabCoordination.setEnabled(self._isEditable)
        if hasattr(self, 'grpActionsDetail'):
            self.grpActionsDetail.setEnabled(self._isEditable)

    def setupUiMini(self, Dialog):
        self.tblAccActions = CInDocTableView(Dialog)
        self.tblPayments = CInDocTableView(Dialog)

    def clearBeforeSetupUi(self):
        self.tblAccActions.setModel(None)
        self.tblPayments.setModel(None)
        self.tblAccActions.deleteLater()
        self.tblAccActions = None
        self.tblPayments.deleteLater()
        self.tblPayments = None
        del self.tblAccActions
        del self.tblPayments

    def preSetupUiMini(self):
        self.addModels('AccActions', CAccActionsSummary(self, True))
        self.addModels('Payments', CPaymentsModel(self))
        self.eventEditor = None
        self.localContractRecord = None

    def preSetupUi(self):
        pass

    def postSetupUiMini(self):
        self.setupModels()
        self._updateEditable()

    def postSetupUi(self):
        self.cmbAPStatus.clear()
        self.cmbAPStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.cmbDocType.setTable(rbDocumentType, True,
                                 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')')
        self.setupModels()
        self.tabCoordination.setFocusProxy(self.grpLocalContract)
        self.tabActionsAndCash.setFocusProxy(self.tblAccActions)
        self.windowTitle = u''
        self._updateEditable()
        self.connect(self.modelAccActions, QtCore.SIGNAL('sumChanged()'), self.setUpdatePaymentsSum)
        self.connect(self.modelPayments, QtCore.SIGNAL('sumChanged()'), self.setUpdatePaymentsSum)

    def setupModels(self):
        self.setModels(self.tblAccActions, self.modelAccActions, self.selectionModelAccActions)
        self.setModels(self.tblPayments, self.modelPayments, self.selectionModelPayments)

        self.tblAccActions.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblAccActions.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        self.tblPayments.addPopupDelRow()
        self.tblAccActionsPrepareColumns()

    def tblAccActionsPrepareColumns(self):
        horizontalHeader = self.tblAccActions.horizontalHeader()
        model = self.tblAccActions.model()
        # 0: тип
        horizontalHeader.hideSection(model.getColIndex('MKB'))  # МКБ
        horizontalHeader.hideSection(model.getColIndex('MES_id'))  # Стандарт
        horizontalHeader.hideSection(model.getColIndex('isUrgent'))  # Срочный
        horizontalHeader.hideSection(model.getColIndex('directionDate'))  # Назначено
        horizontalHeader.hideSection(model.getColIndex('begDate'))  # Начато
        horizontalHeader.hideSection(model.getColIndex('endDate'))  # Окончено
        horizontalHeader.hideSection(model.getColIndex('status'))  # Состояние
        horizontalHeader.hideSection(model.getColIndex('setPerson_id'))  # Назначил
        horizontalHeader.hideSection(model.getColIndex('person_id'))  # Выполнил
        horizontalHeader.hideSection(model.getColIndex('assistant_id'))  # Ассистент
        horizontalHeader.hideSection(model.getColIndex('office'))  # Каб
        # 11: количество
        if not QtGui.qApp.isPNDDiagnosisMode():
            horizontalHeader.hideSection(model.colUetIdx)  # УЕТ
        # 13: примечание
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('account')), 0)  # считать
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('actionType_id')), 1)  # тип
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('finance_id')),
                                     2)  # тип финансирования
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('contract_id')), 3)  # договор
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.colAmountIdx), 4)  # количество
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('price')), 5)  # цена
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('sum')), 6)  # сумма
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('customSum')),
                                     7)  # редактируемая сумма
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('payStatus')),
                                     8)  # отметки финансирования
        horizontalHeader.moveSection(horizontalHeader.visualIndex(model.getColIndex('note')), 9)  # примечание

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor
        self.modelAccActions.setEventEditor(eventEditor)

    def addActionModel(self, model):
        self.modelAccActions.addModel(model)

    def load(self, eventId):
        self.loadLocalContract(eventId)
        self.modelPayments.loadItems(eventId)

    def loadLocalContract(self, eventId):
        db = QtGui.qApp.db
        table = db.table(self.localContractTableName)
        record = db.getRecordEx(table, '*', table['master_id'].eq(eventId))
        if record:
            self.setLocalContractRecord(record)

    def setLocalContractRecord(self, record):
        self.localContractRecord = record
        if self.isControlsCreate:
            self.grpLocalContract.setChecked(forceInt(record.value('deleted')) == 0)
            setDateEditValue(self.edtCoordDate, record, 'coordDate')
            setLineEditValue(self.edtCoordAgent, record, 'coordAgent')
            setLineEditValue(self.edtCoordInspector, record, 'coordInspector')
            setTextEditValue(self.edtCoordText, record, 'coordText')
            setDateEditValue(self.edtContractDate, record, 'dateContract')
            setLineEditValue(self.edtContractNumber, record, 'numberContract')
            setLineEditValue(self.edtSumLimit, record, 'sumLimit')
            setLineEditValue(self.edtLastName, record, 'lastName')
            setLineEditValue(self.edtFirstName, record, 'firstName')
            setLineEditValue(self.edtPatrName, record, 'patrName')
            setDateEditValue(self.edtBirthDate, record, 'birthDate')
            setRBComboBoxValue(self.cmbDocType, record, 'documentType_id')
            setLineEditValue(self.edtDocSerialLeft, record, 'serialLeft')
            setLineEditValue(self.edtDocSerialRight, record, 'serialRight')
            setLineEditValue(self.edtDocNumber, record, 'number')
            setLineEditValue(self.edtRegAddress, record, 'regAddress')
            setRBComboBoxValue(self.cmbOrganisation, record, 'org_id')

    def save(self, eventId):
        self.saveLocalContract(eventId)
        self.modelPayments.saveItems(eventId)

    def saveLocalContract(self, eventId):
        record = self.getLocalContractRecord(eventId)
        if record:
            QtGui.qApp.db.insertOrUpdate(self.localContractTableName, record)

    def getLocalContractRecord(self, eventId):
        record = self.localContractRecord
        if self.isControlsCreate and self.grpLocalContract.isChecked():
            record = self.localContractRecord if self.localContractRecord else QtGui.qApp.db.record(
                self.localContractTableName)
            record.setValue('master_id', toVariant(eventId))

            record.setValue('deleted', QtCore.QVariant(0 if self.grpLocalContract.isChecked() else 1))

            getDateEditValue(self.edtCoordDate, record, 'coordDate')
            getLineEditValue(self.edtCoordAgent, record, 'coordAgent')
            getLineEditValue(self.edtCoordInspector, record, 'coordInspector')
            getTextEditValue(self.edtCoordText, record, 'coordText')

            getDateEditValue(self.edtContractDate, record, 'dateContract')
            getLineEditValue(self.edtContractNumber, record, 'numberContract')
            getLineEditValue(self.edtSumLimit, record, 'sumLimit')
            getLineEditValue(self.edtLastName, record, 'lastName')
            getLineEditValue(self.edtFirstName, record, 'firstName')
            getLineEditValue(self.edtPatrName, record, 'patrName')
            getDateEditValue(self.edtBirthDate, record, 'birthDate')
            getRBComboBoxValue(self.cmbDocType, record, 'documentType_id')
            getLineEditValue(self.edtDocSerialLeft, record, 'serialLeft')
            getLineEditValue(self.edtDocSerialRight, record, 'serialRight')
            getLineEditValue(self.edtDocNumber, record, 'number')
            getLineEditValue(self.edtRegAddress, record, 'regAddress')
            getRBComboBoxValue(self.cmbOrganisation, record, 'org_id')
        return record

    def setCashEx(self, externalId, assistantId, curatorId):
        pass

    def enableEditors(self, eventTypeId):
        pass

    def getCash(self, record, eventTypeId):
        pass

    @QtCore.pyqtSlot(bool)
    def on_grpLocalContract_clicked(self, checked):
        if checked:
            if not self.edtCoordAgent.text():
                self.edtCoordAgent.setText(getCurrentUserName())
            if not self.edtContractNumber.text():
                self.on_btnGetExternalId_clicked()

    def checkDataLocalContract(self):
        result = True
        if self.grpLocalContract.isChecked():
            eventEditor = self.eventEditor
            dateContract = self.edtContractDate.date()
            birthDate = self.edtBirthDate.date()
            result = result and (dateContract or eventEditor.checkInputMessage(u'дату договора', True, self.edtContractDate))
            result = result and (len(self.edtContractNumber.text()) > 0 or eventEditor.checkInputMessage(u'номер договора', True, self.edtContractNumber))
            result = result and (len(self.edtSumLimit.text()) > 0 or eventEditor.checkInputMessage(u'ограничение суммы', True, self.edtSumLimit))
            result = result and (len(self.edtLastName.text()) > 0 or eventEditor.checkInputMessage(u'фамилию', False, self.edtLastName))
            result = result and (len(self.edtFirstName.text()) > 0 or eventEditor.checkInputMessage(u'имя', False, self.edtFirstName))
            result = result and (len(self.edtPatrName.text()) > 0 or eventEditor.checkInputMessage(u'отчество', False, self.edtPatrName))
            result = result and (birthDate or eventEditor.checkInputMessage(u'дату рождения', False, self.edtBirthDate))
            result = result and (self.cmbDocType.value() or eventEditor.checkInputMessage(u'тип документа', True, self.cmbDocType))
            if self.cmbDocType.value():
                result = result and (len(self.edtDocNumber.text()) > 0 or eventEditor.checkInputMessage(u'номер', True, self.edtDocNumber))
                result = result and (len(self.edtDocSerialLeft.text()) > 0 or eventEditor.checkInputMessage(u'левую часть серии', True, self.edtDocSerialLeft))
                result = result and (len(self.edtDocSerialRight.text()) > 0 or eventEditor.checkInputMessage(u'правую часть серии', True, self.edtDocSerialRight))
            result = result and (len(self.edtRegAddress.text()) > 0 or eventEditor.checkInputMessage(u'адрес', True, self.edtRegAddress))
        return result

    def checkAgeClient(self, birthDate, date):
        age = date.year() - birthDate.year()
        if QtCore.QDate(0, birthDate.month(), birthDate.day()) > QtCore.QDate(0, date.month(), date.day()):
            age -= 1
        if age < 18:
            res = QtGui.QMessageBox.question(self,
                                             u'Внимание!',
                                             u'Пациент не достиг возраста 18 лет. Он является плательщиком?',
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                             QtGui.QMessageBox.No)
            if res == QtGui.QMessageBox.No:
                return False
        return True

    def getLocalContractInfo(self, context, eventId):
        result = context.getInstance(CEventLocalContractInfo, eventId)
        if self.grpLocalContract.isChecked():
            result.initByRecord(self.getLocalContractRecord(eventId))
            result.setOkLoaded()
        else:
            result.initByRecord(QtGui.qApp.db.dummyRecord())
            result.setOkLoaded(False)
        return result

    def updatePaymentsSum(self):
        self.accSum = self.modelAccActions.sum()
        self.paymentsSum = self.modelPayments.sum()
        if self.localContractRecord:
            self.sumLimit = self.localContractRecord.value('sumLimit').toString()
        if self.sumLimit:
            sumLimitInt = self.sumLimit.toInt()
            if sumLimitInt[1] and sumLimitInt[0] > 0:
                self.eventEditor.setWindowTitle(
                    u'(' + self.sumLimit + u'/' + forceString(self.accSum) + u') ' + self.windowTitle)

    def setUpdatePaymentsSum(self):
        self.updatePaymentsSum()  # atronah: добавил для решения проблемы с нулевыми суммами, но в целом реализация кривая (то, что обновление сумм и их вывод разделен на две функции)
        self.lblPaymentAccValue.setText('%.2f' % self.accSum)
        self.lblPaymentPayedSumValue.setText('%.2f' % self.paymentsSum)
        self.lblPaymentTotalValue.setText('%.2f' % (self.accSum - self.paymentsSum))
        palette = QtGui.QPalette()
        if self.accSum > self.paymentsSum:
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 0, 0))
        self.lblPaymentTotalValue.setPalette(palette)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtSumLimit_textChanged(self, text):
        paymentAccValue = self.lblPaymentAccValue.text()
        sumLimit = self.edtSumLimit.text()
        if sumLimit:
            sumLimitInt = sumLimit.toInt()
            if sumLimitInt[1] and sumLimitInt[0] > 0:
                self.eventEditor.setWindowTitle(u'(' + sumLimit + u'/' + paymentAccValue + u') ' + self.windowTitle)

    def onActionDataChanged(self, name, value):
        model = self.tblAccActions.model()
        items = model.items()
        row = self.tblAccActions.currentIndex().row()
        if 0 <= row < len(items):
            record = items[row]
            record.setValue(name, toVariant(value))

    def onCurrentActionChanged(self):
        model = self.modelAccActions
        items = model.items()
        row = self.tblAccActions.currentIndex().row()
        editWidgets = [self.edtAPCoordDate, self.edtAPCoordTime,
                       self.edtAPCoordAgent,
                       self.edtAPCoordInspector,
                       self.edtAPCoordText
                       ]

        if 0 <= row < len(items):
            record = items[row]
            canEdit = True
            for widget in editWidgets:
                widget.setEnabled(canEdit)
            try:
                for widget in editWidgets:
                    widget.blockSignals(True)
                actionTypeId = forceRef(record.value('actionType_id')) if record else None
                actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
                showTime = actionType.showTime if actionType else False
                self.edtAPDirectionTime.setVisible(showTime)
                self.edtAPPlannedEndTime.setVisible(showTime)
                self.edtAPCoordTime.setVisible(showTime)
                self.edtAPBegTime.setVisible(showTime)
                self.edtAPEndTime.setVisible(showTime)
                setDatetimeEditValue(self.edtAPDirectionDate, self.edtAPDirectionTime, record, 'directionDate')
                setDatetimeEditValue(self.edtAPPlannedEndDate, self.edtAPPlannedEndTime, record, 'plannedEndDate')
                setDatetimeEditValue(self.edtAPCoordDate, self.edtAPCoordTime, record, 'coordDate')
                self.edtAPCoordAgent.setText(forceString(record.value('coordAgent')))
                self.edtAPCoordInspector.setText(forceString(record.value('coordInspector')))
                self.edtAPCoordText.setText(forceString(record.value('coordText')))
                setDatetimeEditValue(self.edtAPBegDate, self.edtAPBegTime, record, 'begDate')
                setDatetimeEditValue(self.edtAPEndDate, self.edtAPEndTime, record, 'endDate')
                self.cmbAPSetPerson.setValue(forceRef(record.value('setPerson_id')))
                self.cmbAPStatus.setCurrentIndex(forceInt(record.value('status')))
                self.edtAPOffice.setText(forceString(record.value('office')))
                self.cmbAPPerson.setValue(forceRef(record.value('person_id')))
                self.edtAPNote.setText(forceString(record.value('note')))
            finally:
                for widget in editWidgets:
                    widget.blockSignals(False)
        else:
            for widget in editWidgets:
                widget.setEnabled(False)
            self.edtAPDirectionTime.setVisible(False)
            self.edtAPPlannedEndTime.setVisible(False)
            self.edtAPCoordTime.setVisible(False)
            self.edtAPBegTime.setVisible(False)
            self.edtAPEndTime.setVisible(False)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtCoordDate_dateChanged(self, date):
        if not self.edtCoordAgent.text():
            self.edtCoordAgent.setText(getCurrentUserName())

    @QtCore.pyqtSlot()
    def on_btnGetExternalId_clicked(self):
        self.edtContractNumber.setText(self.eventEditor.getExternalId())

    @QtCore.pyqtSlot()
    def on_btnGetClientInfo_clicked(self):
        info = self.eventEditor.clientInfo
        if info and self.checkAgeClient(info['birthDate'], QtCore.QDate.currentDate()):
            self.edtLastName.setText(info['lastName'])
            self.edtFirstName.setText(info['firstName'])
            self.edtPatrName.setText(info['patrName'])
            regAddress = info['regAddress']
            if regAddress:
                self.edtRegAddress.setText(regAddress)
            self.edtBirthDate.setDate(info['birthDate'])
            record = info['documentRecord']
            if record:
                setRBComboBoxValue(self.cmbDocType, record, 'documentType_id')
                serialLeft, serialRight = splitDocSerial(forceString(record.value('serial')))
                self.edtDocSerialLeft.setText(serialLeft)
                self.edtDocSerialRight.setText(serialRight)
                setLineEditValue(self.edtDocNumber, record, 'number')

    @QtCore.pyqtSlot()
    def on_btnSelectOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbOrganisation.value(), False)
        self.cmbOrganisation.update()
        if orgId:
            self.cmbOrganisation.setValue(orgId)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAccActions_currentChanged(self, current, previous):
        self.onCurrentActionChanged()

    @QtCore.pyqtSlot()
    def on_modelAccActions_modelReset(self):
        if self.modelAccActions.rowCount():
            self.tblAccActions.setCurrentIndex(self.modelAccActions.index(0, 0))
        else:
            self.onCurrentActionChanged()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtAPCoordDate_dateChanged(self, date):
        self.edtAPCoordTime.setEnabled(bool(date))
        time = self.edtAPDirectionTime.time() if date and self.edtAPDirectionTime.isVisible() else QtCore.QTime()
        self.onActionDataChanged('coordDate', QtCore.QDateTime(date, time))
        if not self.edtAPCoordAgent.text():
            self.edtAPCoordAgent.setText(getCurrentUserName())

    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtAPCoordTime_timeChanged(self, time):
        date = self.edtAPCoordDate.date()
        self.onActionDataChanged('coordDate', QtCore.QDateTime(date, time if date else QtCore.QTime()))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtAPCoordAgent_textChanged(self, text):
        self.onActionDataChanged('coordAgent', text)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtAPCoordInspector_textChanged(self, text):
        self.onActionDataChanged('coordInspector', text)

    @QtCore.pyqtSlot()
    def on_edtAPCoordText_textChanged(self):
        text = self.edtAPCoordText.toPlainText()
        self.onActionDataChanged('coordText', text)

    @QtCore.pyqtSlot()
    def on_modelAPActions_amountChanged(self):
        self.updatePaymentsSum()

    @QtCore.pyqtSlot()
    def on_modelPayments_sumChanged(self):
        self.updatePaymentsSum()


class CEventCashPage(CFastEventCashPage):
    def __init__(self, parent=None):
        CFastEventCashPage.__init__(self, parent)
        self.setupUi(self)
        self.preSetupUiMini()
        self.preSetupUi()
        self.postSetupUi()


class CPaymentsModel(CInDocTableModel):
    __pyqtSignals__ = ('sumChanged()',
                       )

    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Event_Payment', 'id', 'master_id', parent)
        self._parent = parent
        self.addCol(CInDocTableCol(     u'Касса',                   'cashBox',          15)).setToolTip(u'').setReadOnly()
        self.addCol(CDateInDocTableCol( u'Дата',                    'date',             15, canBeEmpty=True)).setToolTip(u'Дата платежа')
        self.addCol(CRBInDocTableCol(   u'Операция',                'cashOperation_id', 10, rbCashOperation, addNone=True, prefferedWidth=150))
        self.addCol(CInDocTableCol(     u'№ чека',                 'cheque',           20))
        self.addCol(CFloatInDocTableCol(u'Сумма',                   'sum',              15)).setToolTip(u'Сумма платежа')
        self.addCol(CEnumInDocTableCol( u'Тип оплаты',              'typePayment',      12,  [u'наличный', u'безналичный']))
        self.addCol(CInDocTableCol(     u'Расчетный счет',          'settlementAccount',22))
        self.addCol(CBankInDocTableCol( u'Реквизиты банка',         'bank_id',          22))
        self.addCol(CInDocTableCol(     u'Номер кредитной карты',   'numberCreditCard', 22))

    def loadItems(self, eventId):
        CInDocTableModel.loadItems(self, eventId)
        self.emitSumChanged()

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('cashBox', toVariant(QtGui.qApp.cashBox()))
        result.setValue('date', toVariant(QtCore.QDate.currentDate()))
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CInDocTableModel.setData(self, index, value, role)
        if result and index.column() == 3:
            self.emitSumChanged()
        return result

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex()):
        result = CInDocTableModel.removeRows(self, row, count, parentIndex)
        self.emitSumChanged()
        return result

    def sum(self):
        result = 0.0
        for item in self.items():
            result += forceDouble(item.value('sum'))
        return result

    def emitSumChanged(self):
        self.emit(QtCore.SIGNAL('sumChanged()'))


def getCurrentUserName():
    if QtGui.qApp.userInfo:
        return QtGui.qApp.userInfo.name()
    else:
        return ''
