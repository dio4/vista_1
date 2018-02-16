# -*- coding: utf-8 -*-

u"""Расчёты: журнал кассовых операций"""
from CashDialog                 import CashDialogEditor, printCashOrder
from Events.EditDispatcher      import getEventFormClass
from Events.EventInfo           import CEventInfo
from Events.Utils               import EventIsPrimary, EventOrder, getEventContext, getEventName, getEventTypeForm, getWorkEventTypeFilter
from Orgs.Utils                 import getOrgStructureDescendants, getOrgStructureFullName
from Registry.ClientEditDialog  import CClientEditDialog
from Registry.Utils             import getClientBanner
from Reports.Report             import convertFilterToString
from Ui_CashBookDialog          import Ui_CashBookDialog
from Users.Rights               import *
from library.DialogBase         import CDialogBase
from library.PrintInfo          import CInfoContext
from library.PrintTemplates     import CPrintButton, applyTemplate, customizePrintButton, getPrintAction
from library.TableModel         import *


class CCashBookDialog(CDialogBase, Ui_CashBookDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.addModels('CashItems', CCashItemsModel(self))
        self.mnuCashItems = QtGui.QMenu(self)
        self.mnuCashItems.setObjectName('mnuCashItems')
        self.actOpenClient = QtGui.QAction(u'Открыть регистрационную карточку', self)
        self.actOpenClient.setObjectName('actOpenClient')
        self.actOpenEvent = QtGui.QAction(u'Открыть первичный документ', self)
        self.actOpenEvent.setObjectName('actOpenEvent')
        self.actShowAccount = QtGui.QAction(u'Показать расчёт', self)
        self.actShowAccount.setObjectName('actShowAccount')

        self.mnuCashItems.addAction(self.actOpenClient)
        self.mnuCashItems.addAction(self.actOpenEvent)
        self.mnuCashItems.addAction(self.actShowAccount)
        self.actPrintBook = QtGui.QAction(u'Печать журнала кассовых операций', self)
        self.actPrintBook.setObjectName('actPrintBook')
        self.actPrintCash = getPrintAction(self, 'cashOrder', u'Печать ордера')
        self.actPrintCash.setObjectName('actPrintCash')
        self.mnuPrintCash = QtGui.QMenu(self)
        self.mnuPrintCash.setObjectName('mnuPrintCash')
        self.mnuPrintCash.addAction(self.actPrintBook)
        self.mnuPrintCash.addAction(self.actPrintCash)
        self.mnuCashItems.addSeparator()
        self.mnuCashItems.addAction(self.actPrintBook)
        self.mnuCashItems.addAction(self.actPrintCash)

        self.addModels('Clients', CClientsModel(self))
        self.addModels('Events', CEventsModel(self))
        self.actOpenClient2 = QtGui.QAction(u'Открыть регистрационную карточку', self)
        self.actOpenClient2.setObjectName('actOpenClient2')
        self.mnuClients = QtGui.QMenu(self)
        self.mnuClients.setObjectName('mnuClients')
        self.mnuClients.addAction(self.actOpenClient2)

        self.actOpenEvent2 = QtGui.QAction(u'Открыть первичный документ', self)

        self.actOpenEvent2.setObjectName('actOpenEvent2')
        self.actCash = QtGui.QAction(u'Принять оплату', self)
        self.actCash.setObjectName('actCash')
        self.mnuEvents = QtGui.QMenu(self)
        self.mnuEvents.setObjectName('mnuEvents')
        self.mnuEvents.addAction(self.actOpenEvent2)
        self.mnuEvents.addAction(self.actCash)
        self.btnPrintCash =  QtGui.QPushButton(u'Печать', self)
        self.btnPrintCash.setObjectName('btnPrintCash')
        self.btnPrintEvent = CPrintButton(self, u'Печать')
        self.btnPrintEvent.setObjectName('btnPrintEvent')
        self.btnCash =       QtGui.QPushButton(u'Оплата', self)
        self.btnCash.setObjectName('btnCash')

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.bbxFilter.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        self.bbxPaymentFilter.button(QtGui.QDialogButtonBox.Apply).setDefault(True)

        self.buttonBox.addButton(self.btnPrintCash,  QtGui.QDialogButtonBox.ActionRole)
        self.btnPrintCash.setMenu(self.mnuPrintCash)
        self.buttonBox.addButton(self.btnPrintEvent, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnCash, QtGui.QDialogButtonBox.ActionRole)
        self.btnPrintCash.setShortcut('F6')
        self.btnPrintEvent.setShortcut('F6')
        self.btnCash.setShortcut('F9')

        self.btnPrintEvent.setVisible(False)
        self.btnCash.setEnabled(False)

        self.cmbFilterCashOperation.setTable('rbCashOperation', True)
        self.cmbFilterEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbFilterEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbFilterPerson.setSpecialityPresent(True)

        self.tblCashItems.setModel(self.modelCashItems)
        self.tblCashItems.setSelectionModel(self.selectionModelCashItems)
        self.tblCashItems.setPopupMenu(self.mnuCashItems)

        self.cmbPaymentFilterAccountingSystem.setTable('rbAccountingSystem', True)
        self.txtClientInfoBrowser.actions.append(self.actOpenClient2)
        self.tblClients.setModel(self.modelClients)
        self.tblClients.setSelectionModel(self.selectionModelClients)
        self.tblClients.setPopupMenu(self.mnuClients)

        self.tblEvents.setModel(self.modelEvents)
        self.tblEvents.setSelectionModel(self.selectionModelEvents)
        self.tblEvents.setPopupMenu(self.mnuEvents)

        self.filter = smartDict()
        self.paymentFilter = smartDict()
        self.reapplyFilterRequired = False
        self.lastAddedCashItemId = None

        self.cmbFilterCashKeeper.setSpecialityIndependents()

    def exec_(self):
        self.resetFilter()
        self.applyFilter()
        self.resetPaymentFilter()
        self.applyPaymentFilter()
        self.tabWidget.setCurrentIndex(0)
        CDialogBase.exec_(self)

    def resetFilter(self):
        self.edtFilterBegDate.setDate(QDate.currentDate())
        self.edtFilterEndDate.setDate(QDate.currentDate())
        self.edtFilterCashBox.setText(QtGui.qApp.cashBox())
        self.cmbFilterCashKeeper.setValue(None)
        self.cmbFilterCashOperation.setValue(None)
        self.cmbFilterEventPurpose.setValue(None)
        self.cmbFilterEventType.setValue(None)
        self.cmbFilterOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbFilterPerson.setValue(None)

    def applyFilter(self, currentId=None):
        self.filter.begDate = self.edtFilterBegDate.date()
        self.filter.endDate = self.edtFilterEndDate.date()
        self.filter.cashBox = forceStringEx(self.edtFilterCashBox.text())
        self.filter.cashKeeperId = self.cmbFilterCashKeeper.value()
        self.filter.cashOperationId = self.cmbFilterCashOperation.value()
        self.filter.eventPurposeId = self.cmbFilterEventPurpose.value()
        self.filter.eventTypeId = self.cmbFilterEventType.value()
        self.filter.orgStructureId = self.cmbFilterOrgStructure.value()
        self.filter.personId = self.cmbFilterPerson.value()
        self.updateCashItemList(currentId)

    def getFilterAsText(self):
        db = QtGui.qApp.db
        return convertFilterToString(self.filter, [
            ('begDate',         u'Дата оплаты с', forceString),
            ('endDate',         u'Дата оплаты по', forceString),
            ('cashBox',         u'Касса',  forceString),
            ('cashKeeperId',    u'Кассир',
                                lambda id: forceString(db.translate('vrbPerson', 'id', id, 'name'))),
            ('cashOperationId', u'Кассовая операция',
                                lambda id: forceString(db.translate('rbCashOperation', 'id', id, 'name'))),
            ('eventPurposeId',  u'Назначение обращения',
                                lambda id: forceString(db.translate('rbEventTypePurpose', 'id', id, 'name'))),
            ('eventTypeId',     u'Тип обращения', lambda id: getEventName(id)),
            ('orgStructureId',  u'Подразделение врача',
                                lambda id: getOrgStructureFullName(id)),
            ('personId',        u'Врач',
                                lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
                   ])

    def getAmountAsText(self):
        return u'Позиций: %s\nПриход: %s\nРасход:%s' % (
                        self.edtCashItemsCount.text(),
                        self.edtIncome.text(),
                        self.edtOutcome.text(),
                        )

    def updateCashItemList(self, currentId=None):
        filter = self.filter
        db = QtGui.qApp.db
        table = db.table('Event_Payment')
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tablePerson = db.table('Person')
        tableEx = table.leftJoin(tableEvent, tableEvent['id'].eq(table['master_id']))
        tableEx = tableEx.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        tableEx = tableEx.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))

        cond = [tableEvent['deleted'].eq(0),
                table['deleted'].eq(0),
                table['date'].ge(self.edtFilterBegDate.date()),
                table['date'].le(self.edtFilterEndDate.date()),
               ]
        if filter.cashBox:
            cond.append(table['cashBox'].eq(filter.cashBox))
        if filter.cashKeeperId:
            cond.append(table['createPerson_id'].eq(filter.cashKeeperId))
        if filter.cashOperationId:
            cond.append(table['cashOperation_id'].eq(filter.cashOperationId))
        if filter.eventTypeId:
            cond.append(tableEvent['eventType_id'].eq(filter.eventTypeId))
        elif filter.eventPurposeId:
            cond.append(tableEventType['purpose_id'].eq(filter.eventPurposeId))
        if filter.personId:
            cond.append(tableEvent['execPerson_id'].eq(filter.personId))
        elif filter.orgStructureId:
            cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(filter.orgStructureId)))

        income = 0
        outcome = 0
        itemCount = 0
        try:
            db.transaction()
            idList = db.getIdList(tableEx, idCol=table['id'], where=cond, order='Event_Payment.date, Event_Payment.id')
            record = db.getRecordEx(tableEx, 'COUNT(*), SUM(IF(`sum`>0, `sum`,0)) AS `income`, SUM(IF(`sum`<0,`sum`,0)) AS `outcome`', where=cond)
            if record:
                itemCount = forceInt(record.value(0))
                income = forceDecimal(record.value(1))
                outcome = -forceDecimal(record.value(2))
        finally:
            db.commit()

        self.tblCashItems.setIdList(idList, currentId)
        self.edtCashItemsCount.setText(forceString(itemCount))
        self.edtIncome.setText(forceString(income))
        self.edtOutcome.setText(forceString(outcome))

    def getCurrentClientIdByCashItem(self):
        eventId = self.getCurrentEventIdByCashItem()
        if eventId:
            eventRecord = self.modelCashItems.eventCache.get(eventId)
            if eventRecord:
                return forceRef(eventRecord.value('client_id'))
        return None

    def getCurrentEventIdByCashItem(self):
        itemId = self.tblCashItems.currentItemId()
        if itemId:
            itemRecord = self.modelCashItems.recordCache().get(itemId)
            if itemRecord:
                return forceRef(itemRecord.value('master_id'))
        return None

    def resetPaymentFilter(self):
        self.cmbPaymentFilterAccountingSystem.setValue(None)
        self.edtPaymentFilterClientCode.setText('')
        self.edtPaymentFilterLastName.setText('')
        self.edtPaymentFilterFirstName.setText('')
        self.edtPaymentFilterPatrName.setText('')
        self.edtPaymentFilterBirthDay.setDate(QDate())
        self.cmbPaymentFilterSex.setCurrentIndex(0)
        self.edtPaymentFilterEventId.setText('')
        self.edtPaymentFilterExternalEventId.setText('')

    def applyPaymentFilter(self, currentClientId=None, currentEventId=None):
        self.paymentFilter.accountingSystemId = self.cmbPaymentFilterAccountingSystem.value()
        self.paymentFilter.clientCode = forceStringEx(self.edtPaymentFilterClientCode.text())
        self.paymentFilter.lastName   = forceStringEx(self.edtPaymentFilterLastName.text())
        self.paymentFilter.firstName  = forceStringEx(self.edtPaymentFilterFirstName.text())
        self.paymentFilter.patrName   = forceStringEx(self.edtPaymentFilterPatrName.text())
        self.paymentFilter.birthDay   = self.edtPaymentFilterBirthDay.date()
        self.paymentFilter.sex        = self.cmbPaymentFilterSex.currentIndex()
        self.paymentFilter.eventId    = forceStringEx(self.edtPaymentFilterEventId.text())
        self.paymentFilter.externalEventId = forceStringEx(self.edtPaymentFilterExternalEventId.text())
        self.updateClientList(currentClientId)
        self.updateEventList(currentEventId)

    def updateClientList(self, currentClientId=None):
        filter = self.paymentFilter
        db = QtGui.qApp.db
        table = db.table('Client')
        tableEx = table

        cond = []
        if filter.clientCode:
            if filter.accountingSystemId:
                tableCI = db.table('ClientIdentification')
                tableEx = tableEx.leftJoin(tableCI, [tableCI['client_id'].eq(table['id']),
                                                     tableCI['deleted'].eq(0),
                                                     tableCI['accountingSystem_id'].eq(filter.accountingSystemId),
                                                    ])
                cond.append(tableCI['identifier'].eq(filter.clientCode))
            else:
                cond.append(table['id'].eq(filter.clientCode))

        if filter.lastName:
            cond.append(table['lastName'].like(filter.lastName))
        if filter.firstName:
            cond.append(table['firstName'].like(filter.firstName))
        if filter.patrName:
            cond.append(table['patrName'].like(filter.patrName))
        if filter.birthDay:
            cond.append(table['birthDate'].eq(filter.birthDay))
        if filter.sex:
            cond.append(table['sex'].eq(filter.sex))
        if filter.eventId or filter.externalEventId:
            tableEvent = db.table('Event')
            tableEx = tableEx.leftJoin(tableEvent, [tableEvent['client_id'].eq(table['id']),
                                                    tableEvent['deleted'].eq(0),
                                                ])
            if filter.eventId:
                cond.append(tableEvent['id'].eq(filter.eventId))
            if filter.externalEventId:
                cond.append(tableEvent['externalId'].eq(filter.externalEventId))
        if cond:
            idList = db.getIdList(tableEx, idCol=table['id'], where=cond, order='Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.id', limit=10000)
        else:
            idList = []
        self.tblClients.setIdList(idList, currentClientId)
        self.showClientInfo(self.getCurrentClientId())

    def updateEventList(self, currentEventId=None):
        filter = self.paymentFilter
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        table = tableEvent
        clientId = self.getCurrentClientId()
        if clientId:
            tableEventType = db.table('EventType')
            table = table.leftJoin(tableEventType,  tableEventType['id'].eq(tableEvent['eventType_id']))
            cond = [tableEvent['client_id'].eq(clientId),
                    tableEvent['deleted'].eq(0)
                   ]
            table = getWorkEventTypeFilter(table, cond)
            if filter.eventId:
                cond.append(tableEvent['id'].eq(filter.eventId))
            if filter.externalEventId:
                cond.append(tableEvent['externalId'].eq(filter.externalEventId))
            idList = db.getIdList(table, idCol=tableEvent['id'], where=cond, order='setDate DESC', limit=100)
        else:
            idList = []
        self.tblEvents.setIdList(idList, currentEventId)
        self.btnCash.setEnabled(self.tabWidget.currentIndex()==1 and bool(idList))

    def getCurrentClientId(self):
        return self.tblClients.currentItemId()

    def getCurrentEventId(self):
        return self.tblEvents.currentItemId()

    def openClient(self, clientId):
        if clientId and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            dialog.load(clientId)
            self.reapplyFilterRequired = True
            return dialog.exec_()
    def openEvent(self, eventId):
        if eventId and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents]):
            formClass = getEventFormClass(eventId)
            dialog = formClass(self)
            self.reapplyFilterRequired = True
            dialog.load(eventId)
            if dialog.restrictToPayment():
                dialog.exec_()

    def showClientInfo(self, id):
        self.txtClientInfoBrowser.setHtml(getClientBanner(id) if id else '')
        self.actOpenClient2.setEnabled(bool(id))
        # QtGui.qApp.setCurrentClientId(id)

    def cashEvent(self, eventId):
        if eventId:
            dialog = CashDialogEditor(self)
            dialog.setEventId(eventId)
            dialog.setCashBox(QtGui.qApp.cashBox())
            cashItemId = dialog.exec_()
            if cashItemId:
                self.reapplyFilterRequired = True
                self.lastAddedCashItemId = cashItemId

    @pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        if index == 0:
            self.btnPrintCash.setVisible(True)
            self.btnPrintEvent.setVisible(False)
            self.btnCash.setEnabled(False)
            self.splitterBook.setSizes(self.splitterPayment.sizes())
            if self.reapplyFilterRequired:
                self.applyFilter(self.lastAddedCashItemId)
                self.reapplyFilterRequired = False
                self.lastAddedCashItemId = None
        elif index == 1:
            self.btnPrintCash.setVisible(False)
            self.btnPrintEvent.setVisible(True)
            self.btnCash.setEnabled(bool(self.modelEvents.idList()))
            self.splitterPayment.setSizes(self.splitterBook.sizes())
            if self.reapplyFilterRequired:
                self.applyPaymentFilter()
                self.reapplyFilterRequired = False

    @pyqtSlot(int)
    def on_cmbFilterEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbFilterEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbFilterEventType.setFilter(filter)

    @pyqtSlot(int)
    def on_cmbFilterOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbFilterOrgStructure.value()
        self.cmbFilterPerson.setOrgStructureId(orgStructureId)

    @pyqtSlot(QtGui.QAbstractButton)
    def on_bbxFilter_clicked(self, button):
        buttonCode = self.bbxFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyFilter()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilter()
            self.applyFilter()

    @pyqtSlot()
    def on_mnuCashItems_aboutToShow(self):
        currentRow = self.tblCashItems.currentIndex().row()
        itemPresent = currentRow>=0
        self.actOpenClient.setEnabled(itemPresent and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.actOpenEvent.setEnabled(itemPresent and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents]))
        self.actShowAccount.setEnabled(itemPresent)
        self.actPrintCash.setEnabled(itemPresent)

    @pyqtSlot()
    def on_actOpenClient_triggered(self):
        self.openClient(self.getCurrentClientIdByCashItem())
        self.modelCashItems.invalidateRecordsCache()

    @pyqtSlot()
    def on_actOpenEvent_triggered(self):
        self.openEvent(self.getCurrentEventIdByCashItem())
        self.modelCashItems.invalidateRecordsCache()

    @pyqtSlot()
    def on_actShowAccount_triggered(self):
        eventId = self.getCurrentEventIdByCashItem()
        self.resetPaymentFilter()
        self.edtPaymentFilterEventId.setText(str(eventId) if eventId else '')
        self.applyPaymentFilter()
        self.tabWidget.setCurrentIndex(1)

    @pyqtSlot()
    def on_mnuPrintCash_aboutToShow(self):
        itemId = self.tblCashItems.currentItemId()
        self.actPrintCash.setEnabled(bool(itemId))

    @pyqtSlot()
    def on_actPrintBook_triggered(self):
        self.tblCashItems.setReportHeader(u'Журнал кассовых операций')
        self.tblCashItems.setReportDescription(self.getFilterAsText()+'\n'+self.getAmountAsText())
        self.tblCashItems.printContent()

    @pyqtSlot(int)
    def on_actPrintCash_printByTemplate(self, templateId):
        itemId = self.tblCashItems.currentItemId()
        record = self.modelCashItems.recordCache().get(itemId)
        printCashOrder(self,
                       templateId,
                       forceRef(record.value('master_id')),
                       forceDate(record.value('date')),
                       forceRef(record.value('cashOperation_id')),
                       forceDecimal(record.value('sum')),
                       forceString(record.value('cashBox')))

    @pyqtSlot(QtGui.QAbstractButton)
    def on_bbxPaymentFilter_clicked(self, button):
        buttonCode = self.bbxPaymentFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyPaymentFilter()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetPaymentFilter()
            self.applyPaymentFilter()

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelClients_currentRowChanged(self, current, previous):
        self.showClientInfo(self.getCurrentClientId())
        self.updateEventList(self.getCurrentEventId())

    @pyqtSlot()
    def on_mnuClients_aboutToShow(self):
        itemPresent = bool(self.getCurrentClientId())
        self.actOpenClient2.setEnabled(itemPresent and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))

    @pyqtSlot()
    def on_actOpenClient2_triggered(self):
        self.openClient(self.getCurrentClientId())
        self.modelClients.invalidateRecordsCache()
        self.applyPaymentFilter()

    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelEvents_currentRowChanged(self, current, previous):
        eventId = self.getCurrentEventId()
        if eventId:
            eventRecord = self.modelEvents.recordCache().get(eventId)
            eventTypeId = forceRef(eventRecord.value('eventType_id'))
            context = getEventContext(eventTypeId)
            if not context:
                context = 'f'+getEventTypeForm(eventTypeId)
        else:
            context = ''
        if context:
            customizePrintButton(self.btnPrintEvent, context)
            self.btnPrintEvent.setEnabled(True)
        else:
            self.btnPrintEvent.setEnabled(False)

    @pyqtSlot()
    def on_mnuEvents_aboutToShow(self):
        itemPresent = bool(self.getCurrentEventId())
        self.actOpenEvent2.setEnabled(itemPresent and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents]))
        self.actCash.setEnabled(itemPresent)

    @pyqtSlot()
    def on_actOpenEvent2_triggered(self):
        self.openEvent(self.getCurrentEventId())
        self.modelEvents.invalidateRecordsCache()
        self.applyPaymentFilter()

    @pyqtSlot()
    def on_actCash_triggered(self):
        self.cashEvent(self.getCurrentEventId())

    @pyqtSlot()
    def on_btnCash_clicked(self):
        self.cashEvent(self.getCurrentEventId())

    @pyqtSlot(int)
    def on_btnPrintEvent_printByTemplate(self, templateId):
        context = CInfoContext()
        eventId = self.getCurrentEventId()
        eventInfo = context.getInstance(CEventInfo, eventId)
        tempInvalidInfo = None # self.getTempInvalidInfo(context)

        data = { 'event' : eventInfo,
                 'client': eventInfo.client,
                 'tempInvalid': tempInvalidInfo
               }
        applyTemplate(self, templateId, data)


class CCashItemsModel(CTableModel):
    def __init__(self, parent):
        eventTypeCol = CLocEventTypeColumn(  u'Обращение', ['master_id'], 20)
        eventSetDateCol = CLocEventSetDateColumn(  u'Назначено', ['master_id'], 20, eventTypeCol.eventCache)
        eventExecDateCol = CLocEventExecDateColumn(  u'Окончено', ['master_id'], 20, eventTypeCol.eventCache)
        eventPersonCol = CLocEventPersonColumn(  u'Врач', ['master_id'], 20, eventTypeCol.eventCache)
        clientCol = CLocClientColumn( u'Ф.И.О.', ['master_id'], 20, eventTypeCol.eventCache)
        clientBirthDateCol = CLocClientBirthDateColumn( u'Дата рожд.', ['master_id'], 10, eventTypeCol.eventCache, clientCol.clientCache)
        clientSexCol = CLocClientSexColumn(             u'Пол', ['master_id'], 3, eventTypeCol.eventCache, clientCol.clientCache)
        CTableModel.__init__(self, parent, [
            CDateCol(u'Дата',        ['date'],    10),
            CTextCol(u'Касса',       ['cashBox'], 20),
            CRefBookCol(u'Кассир',   ['createPerson_id'], 'vrbPerson', 20),
            CRefBookCol(u'Операция', ['cashOperation_id'], 'rbCashOperation', 20),
            CSumCol(u'Сумма',        ['sum'],    10, 'r'),
            clientCol,
            clientBirthDateCol,
            clientSexCol,
            eventTypeCol,
            eventSetDateCol,
            eventExecDateCol,
            eventPersonCol,
            ], 'Event_Payment' )
        self.eventCache = eventTypeCol.eventCache


class CLocEventTypeColumn(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.eventCache     = CTableRecordCache(db, db.table('Event'), 'eventType_id, client_id, setDate, execDate, execPerson_id')
        self.eventTypeCache = CTableRecordCache(db, db.table('EventType'), 'name')

    def format(self, values):
        eventId = forceRef(values[0])
        if eventId:
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                eventTypeId = forceRef(eventRecord.value('eventType_id'))
                eventTypeRecord = self.eventTypeCache.get(eventTypeId)
                if eventTypeRecord:
                    return eventTypeRecord.value('name')
        return CCol.invalid

    def invalidateRecordsCache(self):
        self.eventCache.invalidate()
        self.eventTypeCache.invalidate()


class CLocEventSetDateColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.eventCache  = eventCache

    def format(self, values):
        eventId = forceRef(values[0])
        if eventId:
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                return toVariant(forceString(forceDate(eventRecord.value('setDate'))))
        return CCol.invalid


class CLocEventExecDateColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.eventCache  = eventCache

    def format(self, values):
        eventId = forceRef(values[0])
        if eventId:
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                return toVariant(forceString(forceDate(eventRecord.value('execDate'))))
        return CCol.invalid


class CLocEventPersonColumn(CRefBookCol):
    def __init__(self, title, fields, defaultWidth, eventCache):
        CRefBookCol.__init__(self, title, fields, 'vrbPersonWithSpeciality', defaultWidth)
        db = QtGui.qApp.db
        self.eventCache  = eventCache

    def format(self, values):
        eventId = forceRef(values[0])
        if eventId:
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                return CRefBookCol.format(self, [eventRecord.value('execPerson_id')])
        return CCol.invalid


class CLocClientColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.eventCache  = eventCache
        self.clientCache = CTableRecordCache(db, db.table('Client'), 'lastName, firstName, patrName, birthDate, sex, SNILS')

    def format(self, values):
        val = values[0]
        eventId  = forceRef(val)
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            clientId = forceRef(eventRecord.value('client_id'))
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                name  = formatName(clientRecord.value('lastName'),
                                   clientRecord.value('firstName'),
                                   clientRecord.value('patrName'))
                return toVariant(name)
        return CCol.invalid

    def invalidateRecordsCache(self):
        self.clientCache.invalidate()


class CLocClientBirthDateColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache, clientCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.eventCache  = eventCache
        self.clientCache = clientCache

    def format(self, values):
        val = values[0]
        eventId  = forceRef(val)
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            clientId = forceRef(eventRecord.value('client_id'))
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                return toVariant(forceString(clientRecord.value('birthDate')))
        return CCol.invalid


class CLocClientSexColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache, clientCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.eventCache  = eventCache
        self.clientCache = clientCache

    def format(self, values):
        val = values[0]
        eventId  = forceRef(val)
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            clientId = forceRef(eventRecord.value('client_id'))
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                return toVariant(formatSex(clientRecord.value('sex')))
        return CCol.invalid


class CClientsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CTextCol(u'Фамилия',       ['lastName'],  20),
            CTextCol(u'Имя',           ['firstName'], 20),
            CTextCol(u'Отчество',      ['patrName'],  20),
            CDateCol(u'Дата рожд.', ['birthDate'], 12, highlightRedDate=False),
            CEnumCol(u'Пол',        ['sex'], [u'-', u'М', u'Ж'], 4, 'c'),
            ], 'Client' )


class CEventsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CDateCol(u'Назначен', ['setDate'],  10),
            CDateCol(u'Выполнен', ['execDate'], 10),
            CRefBookCol(u'Тип',  ['eventType_id'], 'EventType', 15),
            CRefBookCol(u'МЭС',  ['MES_id'], 'mes.MES', 15, CRBComboBox.showCode),
            CRefBookCol(u'Врач', ['execPerson_id'], 'vrbPersonWithSpeciality', 15),
            CEnumCol(u'Первичный', ['isPrimary'], EventIsPrimary.nameList, 8),
            CEnumCol(u'Порядок', ['order'], EventOrder().orderNameList, 8),
            CRefBookCol(u'Результат', ['result_id'], 'rbResult', 40),
            CTextCol(u'Внешний идентификатор', ['externalId'], 30),
            ], 'Event' )
