# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.CreateEvent import editEvent
from Ui_OrderListDialog import Ui_OrderListDialog
from library.DialogBase import CDialogBase
from library.Enum import CEnum
from library.LoggingModule.Logger import getLoggerDbName
from library.TableModel import CDateTimeCol, CEnumCol, CTableModel, CTextCol
from library.Utils import forceRef, forceString, getPref, setPref
from library.database import CTableRecordCache


class OrderStatus(CEnum):
    NotSent = 0
    AwaitingResult = 1
    Finished = 2
    Outdated = 3
    HasError = 4

    nameMap = {
        NotSent       : u'Не отправлено',
        AwaitingResult: u'Отправлено',
        Finished      : u'Закончено',
        Outdated      : u'Устаревшая',
        HasError      : u'Ошибка отправки'
    }


class OrderSyncStatus(CEnum):
    OrderSent = 0
    ResultReceived = 1
    NoBundleData = 2
    ResultNotReceived = 3
    IncorrectPersonIdentifier = 4
    RequestError = 5
    TerminologyServiceError = 6
    PartialResultReceived = 7
    NoSpecimenType = 8
    NoDiagnosticOrderItems = 9
    Outdated = 90
    Exception = 99

    nameMap = {
        OrderSent                : u'Отправлен',
        ResultReceived           : u'Получен результат',
        NoBundleData             : u'Заявка изменена/удалена',
        ResultNotReceived        : u'Результат не готов',
        IncorrectPersonIdentifier: u'Некорректный идентификатор исполнителя',
        RequestError             : u'Ошибка запроса к ОДЛИ',
        TerminologyServiceError  : u'Не валидировано сервисом Терминологии',
        PartialResultReceived    : u'Получен неполный результат',
        NoSpecimenType           : u'Не указан тип биоматериала',
        NoDiagnosticOrderItems   : u'Не указаны коды заявок',
        Outdated                 : u'Устаревшая',
        Exception                : u'Внтуренняя ошибка'
    }


class OrderResponseStatus(CEnum):
    Created = 0
    NotSent = 1
    Finished = 2
    Outdated = 3
    HasError = 4

    nameMap = {
        Created : u'Создан',
        NotSent : u'Не отправлен',
        Finished: u'Отправлен',
        Outdated: u'Устаревший',
        HasError: u'Ошибка отправки'
    }


class OrderResponseSyncStatus(CEnum):
    OrderReceived = 0
    ResultSent = 1
    NoBundleData = 2
    PersonNotSet = 3
    IncorrectPersonIdentifier = 4
    RequestError = 5
    OrderNotReceived = 6
    NoObservations = 7
    NoDiagnosticReports = 8
    IncorrectOrderIdentifier = 9
    NoSpecimenType = 10
    InternalOrderNotFound = 11
    TerminologyServiceError = 12
    Outdated = 90
    Exception = 99

    nameMap = {
        OrderReceived            : u'Получена заявка',
        ResultSent               : u'Результат отправлен',

        NoBundleData             : u'Результат изменен/удален',
        PersonNotSet             : u'Не указан исполнитель',
        IncorrectPersonIdentifier: u'Некорректный идентификатор исполнителя',
        RequestError             : u'Ошибка запроса к ОДЛИ',
        OrderNotReceived         : u'Заявка не получена',
        NoObservations           : u'Не указаны результаты тестов',
        NoDiagnosticReports      : u'Не заполнены результаты исследования',
        # IncorrectOrderIdentifier : 'INCORRECT ORDER IDENTIFIER',
        NoSpecimenType           : u'Не указан тип биоматериала',
        InternalOrderNotFound    : u'Не найдена внутренняя заявка',
        TerminologyServiceError  : u'Не валидировано сервисом Терминологии',
        Outdated                 : u'Устаревший',

        Exception                : u'Внутренняя ошибка'
    }


class COrderModel(CTableModel):
    u""" МИС-часть: заявки на лабораторные исследования """
    fetchSize = 100

    def __init__(self, parent):
        super(COrderModel, self).__init__(parent, cols=[
            CTextCol(u'Идентификатор МИС', ['orderMisId'], 10),
            CTextCol(u'Идентификатор ЛИС', ['orderUUID'], 10),
            CTextCol(u'Штрих-код', ['externalId'], 10),
            CTextCol(u'ФИО пациента', ['clientName'], 25),
            CTextCol(u'Биоматериал', ['tissueTypeName'], 15),
            CDateTimeCol(u'Создано', ['datetime'], 20),
            CDateTimeCol(u'Отправлено', ['sentDatetime'], 20),
            CDateTimeCol(u'Получено', ['receivedDatetime'], 20),
            CEnumCol(u'Статус', ['status'], OrderStatus, 20),
            CEnumCol(u'Текущее состояние', ['lastSyncStatus'], OrderSyncStatus, 20, notPresentValue='-'),
            CTextCol(u'Текст ошибки', ['error'], 20, toolTipValue=True)
        ])
        self.setTable('')

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableEvent = db.table('Event')
        tableOrder = db.table('{0}.N3LabOrderLog'.format(getLoggerDbName()))
        tableOrderSync = db.table('{0}.N3LabOrderSyncLog'.format(getLoggerDbName()))
        tableOrderSent = tableOrderSync.alias('OrderSent')
        tableOrderRecv = tableOrderSync.alias('OrderRecv')
        tableOrderCurrent = tableOrderSync.alias('OrderCurrent')
        tableTissueType = db.table('rbTissueType')
        tableTTJ = db.table('TakenTissueJournal')

        table = tableOrder
        table = table.leftJoin(tableOrderSent,
                               tableOrderSent['id'].eqStmt(
                                   db.selectMin(tableOrderSync,
                                                tableOrderSync['id'],
                                                [tableOrderSync['order_id'].eq(tableOrder['id']),
                                                 tableOrderSync['status'].eq(OrderSyncStatus.OrderSent)])
                               ))
        table = table.leftJoin(tableOrderRecv,
                               tableOrderRecv['id'].eqStmt(
                                   db.selectMax(tableOrderSync,
                                                tableOrderSync['id'],
                                                [tableOrderSync['order_id'].eq(tableOrder['id']),
                                                 tableOrderSync['status'].eq(OrderSyncStatus.ResultReceived)])
                               ))
        table = table.leftJoin(tableOrderCurrent,
                               tableOrderCurrent['id'].eqStmt(
                                   db.selectMax(tableOrderSync,
                                                tableOrderSync['id'],
                                                tableOrderSync['order_id'].eq(tableOrder['id']))
                               ))
        table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableOrder['event_id']))
        table = table.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        table = table.leftJoin(tableTTJ, tableTTJ['id'].eq(tableOrder['takenTissueJournal_id']))
        table = table.leftJoin(tableTissueType, tableTissueType['id'].eq(tableTTJ['tissueType_id']))

        cols = [
            tableOrder['orderMisId'],
            tableOrder['orderUUID'],
            tableOrder['datetime'],
            tableOrder['status'],
            tableOrder['event_id'],
            tableOrderCurrent['error'],
            db.concat_ws(' ', tableClient['lastName'], tableClient['firstName'], tableClient['patrName']).alias('clientName'),
            tableTTJ['externalId'],
            tableTissueType['name'].alias('tissueTypeName'),
            tableOrderCurrent['status'].alias('lastSyncStatus'),
            tableOrderSent['datetime'].alias('sentDatetime'),
            tableOrderRecv['datetime'].alias('receivedDatetime')
        ]

        self._table = table
        self._recordsCache = CTableRecordCache(db, self._table, cols, recordCacheCapacity)

    def isEditable(self):
        return True


class COrderResponseModel(CTableModel):
    u""" ЛИС-часть: результаты лабораторных исследований """
    fetchSize = 100

    def __init__(self, parent):
        super(COrderResponseModel, self).__init__(parent, cols=[
            CTextCol(u'Идентификатор заявки в ЛИС', ['orderUUID'], 10),
            CTextCol(u'Идентификатор ЛИС', ['orderResponseUUID'], 10),
            CTextCol(u'ФИО пациента', ['clientName'], 25),
            CDateTimeCol(u'Дата создания', ['datetime'], 20),
            CDateTimeCol(u'Дата отправки', ['sentDatetime'], 20),
            CEnumCol(u'Статус', ['status'], OrderResponseStatus, 20),
            CEnumCol(u'Текущее состояние', ['lastSyncStatus'], OrderResponseSyncStatus, 20, notPresentValue='-'),
            CTextCol(u'Текст ошибки', ['error'], 20)
        ])
        self.setTable('')

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableEvent = db.table('Event')
        tableOrderResponse = db.table('{0}.N3LabOrderResponseLog'.format(getLoggerDbName()))
        tableOrderResponseSync = db.table('{0}.N3LabOrderResponseSyncLog'.format(getLoggerDbName()))
        tableOrderResponseSent = tableOrderResponseSync.alias('OrderResponseSent')
        tableOrderResponseCurrent = tableOrderResponseSync.alias('OrderResponseCurrent')

        table = tableOrderResponse
        table = table.leftJoin(tableOrderResponseSent,
                               tableOrderResponseSent['id'].eqStmt(
                                   db.selectMin(tableOrderResponseSync,
                                                tableOrderResponseSync['id'],
                                                [tableOrderResponseSync['orderResponse_id'].eq(tableOrderResponse['id']),
                                                 tableOrderResponseSync['status'].eq(OrderResponseSyncStatus.ResultSent)])
                               ))
        table = table.leftJoin(tableOrderResponseCurrent,
                               tableOrderResponseCurrent['id'].eqStmt(
                                   db.selectMax(tableOrderResponseSync,
                                                tableOrderResponseSync['id'],
                                                tableOrderResponseSync['orderResponse_id'].eq(tableOrderResponse['id']))
                               ))
        table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableOrderResponse['event_id']))
        table = table.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

        cols = [
            tableOrderResponse['orderUUID'],
            tableOrderResponse['orderResponseUUID'],
            tableOrderResponse['datetime'],
            tableOrderResponse['status'],
            tableOrderResponse['event_id'],
            tableOrderResponseCurrent['error'],
            db.concat_ws(' ', tableClient['lastName'], tableClient['firstName'], tableClient['patrName']).alias('clientName'),
            tableOrderResponseCurrent['status'].alias('lastSyncStatus'),
            tableOrderResponseSent['datetime'].alias('sentDatetime')
        ]

        self._table = table
        self._recordsCache = CTableRecordCache(db, self._table, cols, recordCacheCapacity)

    def isEditable(self):
        return True


class CLabOrderListDialog(CDialogBase, Ui_OrderListDialog):
    def __init__(self, parent):
        super(CLabOrderListDialog, self).__init__(parent)
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()

    def preSetupUi(self):
        self.actOpenOrderEvent = QtGui.QAction(u'Перейти к обращению', self)
        self.actOpenOrderEvent.setObjectName('actOpenOrderEvent')
        self.actOpenOrderResponseEvent = QtGui.QAction(u'Перейти к обращению', self)
        self.actOpenOrderResponseEvent.setObjectName('actOpenOrderResponseEvent')
        self.actResendOrder = QtGui.QAction(u'Отправить заново', self)
        self.actResendOrder.setObjectName('actResendOrder')
        self.actResendOrderResponse = QtGui.QAction(u'Отправить заново', self)
        self.actResendOrderResponse.setObjectName('actResendOrderResponse')

        self.addModels('Order', COrderModel(self))
        self.addModels('OrderResponse', COrderResponseModel(self))

    def postSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.setModels(self.tblOrder, self.modelOrder, self.selectionModelOrder)
        self.tblOrder.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblOrder.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblOrder.createPopupMenu([self.actOpenOrderEvent,
                                       self.actResendOrder])
        self.connect(self.tblOrder.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.onOrderPopupMenuAboutToShow)

        self.cmbOrderStatus.setEnum(OrderStatus, addNone=True)
        self.cmbOrderSyncStatus.setEnum(OrderSyncStatus, addNone=True)
        self.edtOrderDateFrom.setDate(QtCore.QDate.currentDate())
        self.edtOrderDateTo.setDate(QtCore.QDate.currentDate())

        self.setModels(self.tblOrderResponse, self.modelOrderResponse, self.selectionModelOrderResponse)
        self.tblOrderResponse.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblOrderResponse.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblOrderResponse.createPopupMenu([self.actOpenOrderResponseEvent,
                                               self.actResendOrderResponse])
        self.connect(self.tblOrderResponse.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.onOrderResponsePopupMenuAboutToShow)

        self.cmbOrderResponseStatus.setEnum(OrderResponseStatus, addNone=True)
        self.cmbOrderResponseSyncStatus.setEnum(OrderResponseSyncStatus, addNone=True)
        self.edtOrderResponseDate.setDate(QtCore.QDate.currentDate())

        self.btnClose.clicked.connect(self.close)

    def loadPreferences(self, preferences):
        self.tblOrder.loadPreferences(getPref(preferences, 'tblOrder)', {}))
        self.tblOrderResponse.loadPreferences(getPref(preferences, 'tblOrderResponse', {}))
        return CDialogBase.loadPreferences(self, preferences)

    def savePreferences(self):
        result = CDialogBase.savePreferences(self)
        setPref(result, 'tblOrder', self.tblOrder.savePreferences())
        setPref(result, 'tblOrderResponse', self.tblOrderResponse.savePreferences())
        return result

    @QtCore.pyqtSlot()
    def onOrderPopupMenuAboutToShow(self):
        row = self.tblOrder.currentIndex().row()
        record = self.tblOrder.model().getRecordByRow(row)
        status = forceRef(record.value('status'))
        self.actResendOrder.setVisible(status in (OrderStatus.Outdated,
                                                  OrderStatus.HasError))

    @QtCore.pyqtSlot()
    def onOrderResponsePopupMenuAboutToShow(self):
        row = self.tblOrderResponse.currentIndex().row()
        record = self.tblOrderResponse.model().getRecordByRow(row)
        status = forceRef(record.value('status'))
        self.actResendOrderResponse.setVisible(status in (OrderResponseStatus.Outdated,
                                                          OrderResponseStatus.HasError))

    @QtCore.pyqtSlot()
    def on_actOpenOrderEvent_triggered(self):
        row = self.tblOrder.currentIndex().row()
        record = self.tblOrder.model().getRecordByRow(row)
        evenId = forceRef(record.value('event_id'))
        editEvent(self, evenId)

    @QtCore.pyqtSlot()
    def on_actOpenOrderResponseEvent_triggered(self):
        row = self.tblOrderResponse.currentIndex().row()
        record = self.tblOrderResponse.model().getRecordByRow(row)
        eventId = forceRef(record.value('event_id'))
        editEvent(self, eventId)

    @QtCore.pyqtSlot()
    def on_actResendOrder_triggered(self):
        idList = self.tblOrder.model().idList()
        orderIdList = [idList[index.row()] for index in self.tblOrder.selectionModel().selectedRows() if index.isValid()]

        db = QtGui.qApp.db
        tableOrder = db.table('{0}.N3LabOrderLog'.format(getLoggerDbName()))
        cond = [
            tableOrder['id'].inlist(orderIdList),
            tableOrder['status'].inlist([OrderStatus.Outdated,
                                         OrderStatus.HasError])
        ]
        expr = [
            tableOrder['status'].eq(OrderStatus.NotSent)
        ]
        db.updateRecords(tableOrder, expr, cond)
        self.tblOrder.model().recordCache().invalidate(orderIdList)

    @QtCore.pyqtSlot()
    def on_actResendOrderResponse_triggered(self):
        idList = self.tblOrderResponse.model().idList()
        orderResponseIdList = [idList[index.row()] for index in self.tblOrderResponse.selectionModel().selectedRows() if index.isValid()]

        db = QtGui.qApp.db
        tableOrderResponse = db.table('{0}.N3LabOrderResponseLog'.format(getLoggerDbName()))
        cond = [
            tableOrderResponse['id'].inlist(orderResponseIdList),
            tableOrderResponse['status'].inlist([OrderResponseStatus.Outdated,
                                                 OrderResponseStatus.HasError])
        ]
        expr = [
            tableOrderResponse['status'].eq(OrderResponseStatus.NotSent)
        ]
        db.updateRecords(tableOrderResponse, expr, cond)
        self.tblOrder.model().recordCache().invalidate(orderResponseIdList)

    @QtCore.pyqtSlot()
    def on_btnOrderApply_clicked(self):
        self.reloadOrderList()

    @QtCore.pyqtSlot()
    def on_btnOrderResponseApply_clicked(self):
        self.reloadOrderResponseList()

    def reloadOrderList(self, order=None, reverse=False):
        status = self.cmbOrderStatus.value()
        syncStatus = self.cmbOrderSyncStatus.value()
        hasError = self.chkOrderError.isChecked()
        errorText = forceString(self.edtOrderError.text())
        dateFrom = self.edtOrderDateFrom.date() if self.chkOrderDateFrom.isChecked() else None
        dateTo = self.edtOrderDateTo.date() if self.chkOrderDateTo.isChecked() else None

        db = QtGui.qApp.db
        tableOrder = db.table('{0}.N3LabOrderLog'.format(getLoggerDbName()))
        tableOrderSync = db.table('{0}.N3LabOrderSyncLog'.format(getLoggerDbName()))
        tableOrderCurrent = tableOrderSync.alias('OrderCurrent')

        table = tableOrder

        cond = []
        if status is not None:
            cond.append(tableOrder['status'].eq(status))

        if (syncStatus is not None or hasError):
            table = table.leftJoin(tableOrderCurrent,
                                   tableOrderCurrent['id'].eqStmt(
                                       db.selectMax(tableOrderSync,
                                                    tableOrderSync['id'],
                                                    tableOrderSync['order_id'].eq(tableOrder['id']))
                                   ))

            if syncStatus is not None:
                cond.append(tableOrderCurrent['status'].eq(syncStatus))

            if errorText:
                cond.append(tableOrderCurrent['error'].like(u'%{0}%'.format(errorText)))
            elif hasError:
                cond.append(tableOrderCurrent['error'].ne(''))

        if dateFrom:
            cond.append(tableOrder['datetime'].dateGe(dateFrom))

        if dateTo:
            cond.append(tableOrder['datetime'].dateLe(dateTo))

        if order is None:
            order = [
                tableOrder['id'].desc()
            ]
        idList = db.getDistinctIdList(table, tableOrder['id'], cond, order=order)
        if reverse:
            idList = idList[::-1]
        self.tblOrder.model().setIdList(idList)
        self.lblOrderCount.setText(u'Записей в таблице: {0}'.format(len(idList)))

    def reloadOrderResponseList(self, order=None, reverse=False):
        status = self.cmbOrderResponseStatus.value()
        syncStatus = self.cmbOrderResponseSyncStatus.value()
        hasError = self.chkOrderResponseError.isChecked()
        errorText = forceString(self.edtOrderResponseError.text())

        db = QtGui.qApp.db
        tableOrderResponse = db.table('{0}.N3LabOrderResponseLog'.format(getLoggerDbName()))
        tableOrderResponseSync = db.table('{0}.N3LabOrderResponseSyncLog'.format(getLoggerDbName()))
        tableOrderResponseCurrent = tableOrderResponseSync.alias('OrderResponseCurrent')

        table = tableOrderResponse

        cond = []
        if status is not None:
            cond.append(tableOrderResponse['status'].eq(status))

        if (syncStatus is not None or hasError):
            table = table.leftJoin(tableOrderResponseCurrent,
                                   tableOrderResponseCurrent['id'].eqStmt(
                                       db.selectMax(tableOrderResponseSync,
                                                    tableOrderResponseSync['id'],
                                                    tableOrderResponseSync['orderResponse_id'].eq(tableOrderResponse['id']))
                                   ))

            if syncStatus is not None:
                cond.append(tableOrderResponseCurrent['status'].eq(syncStatus))

            if errorText:
                cond.append(tableOrderResponseCurrent['error'].like(u'%{0}%'.format(errorText)))
            elif hasError:
                cond.append(tableOrderResponseCurrent['error'].ne(''))

        if self.chkOrderResponseDate.isChecked():
            date = self.edtOrderResponseDate.date()
            cond.append(tableOrderResponse['datetime'].dateEq(date))

        if order is None:
            order = [
                tableOrderResponse['id'].desc()
            ]
        idList = db.getDistinctIdList(table, tableOrderResponse['id'], cond, order=order)
        if reverse:
            idList = idList[::-1]
        self.tblOrderResponse.model().setIdList(idList)
        self.lblOrderResponseCount.setText(u'Записей в таблице: {0}'.format(len(idList)))

    def setOrderIdList(self, idList):
        self.tblOrder.model().setIdList(idList)
        self.lblOrderCount.setText(u'Записей в таблице: {0}'.format(len(idList)))

    def setOrderResponseIdList(self, idList):
        self.tblOrderResponse.model().setIdList(idList)
        self.lblOrderResponseCount.setText(u'Записей в таблице: {0}'.format(len(idList)))


# def main():
#     import sys
#     from library.database import connectDataBaseByInfo
#     from s11main import CS11mainApp
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     app.applyDecorPreferences()
#
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#     db = connectDataBaseByInfo({'driverName'      : 'mysql',
#                                 'host'            : 'p104',
#                                 'port'            : 3306,
#                                 'database'        : 's11',
#                                 'user'            : 'dbuser',
#                                 'password'        : 'dbpassword',
#                                 'connectionName'  : 'vista-med',
#                                 'compressData'    : True,
#                                 'afterConnectFunc': None})
#     QtGui.qApp = app
#     QtGui.qApp.db = db
#     orgId = (db.getDistinctIdList('OrgStructure', 'organisation_id', 'deleted=0') or [None])[0]
#     QtGui.qApp.currentOrgId = lambda: orgId
#     QtGui.qApp.currentOrgStructureId = lambda: None
#     dlg = CLabOrderListDialog(None)
#     dlg.exec_()
#
#
# if __name__ == '__main__':
#     main()
