# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Accounting.AccountingDialog import CAccountingDialog
from Events.Action import CAction, CActionTypeCache
from Events.ActionEditDialog import CActionEditDialog
from Events.CreateEvent import editEvent, requestNewEvent
from Events.TempInvalidDuplicateEditDialog import CTempInvalidDuplicateEditDialog
from Events.TempInvalidEditDialog import CTempInvalidEditDialog, CTempInvalidCreateDialog
from Events.Utils import getActionTypeDescendants, getEventName, getEventPurposeId, getEventType, \
    getPayStatusMaskByCode, getPayStatusValueByCode, getWorkEventTypeFilter, \
    payStatusText
from Orgs.Orgs import selectOrganisation
from Orgs.Utils import getOrganisationShortName, getOrgStructureAddressIdList, \
    getOrgStructureDescendants, getOrgStructures, getPersonInfo
from Registry.BeforeRecordClient import printOrder
from Registry.CPropertysComboBox import CFilterPropertyOptionsItem
from Registry.ClientEditDialog import CClientEditDialog
from Registry.ComplaintsEditDialog import CComplaintsEditDialog
from Registry.RegistryTable import CClientsTableModel
from Registry.Utils import formatDocument, formatPolicy, getClientBanner, getClientInfo2, getClientInfoEx, \
    getClientMiniInfo, CCheckNetMixin
from Reports.ReportBase import CReportBase
from Reports.ReportView import CReportViewDialog
from Timeline.TimeTable import formatTimeRange
from Ui_RegisterOfficeRegistry import Ui_Form
from Users.Rights import urAdmin, urRegControlDoubles, urRegTabReadRegistry, urRegTabWriteEvents, \
    urRegTabWriteRegistry
from library import database
from library.DateEdit import CDateEdit
from library.DialogBase import CConstructHelperMixin
from library.PreferencesMixin import CDialogPreferencesMixin
from library.PrintTemplates import applyTemplate, directPrintTemplate, getPrintAction, getPrintTemplates
from library.TableModel import CBoolCol, CDateTimeFixedCol, CRefBookCol, CTextCol
from library.Utils import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    forceStringEx, toVariant, getVal, addDots, formatRecordsCount, \
    formatRecordsCount2, formatSex, formatSNILS, quote
from library.constants import atcAmbulance
from library.crbcombobox import CRBModel


class CRegistryWindow(QtGui.QWidget, CConstructHelperMixin, Ui_Form, CDialogPreferencesMixin, CCheckNetMixin):

    def __init__(self, parent):
        super(CRegistryWindow, self).__init__(parent)
        CCheckNetMixin.__init__(self)
        self.updateClientsListRequest = False
        self.addModels('Clients', CClientsTableModel(self))
        self.addModels('Queue', CQueueModel(self))
        self.addModels('VisitByQueue', CVisitByQueueModel(self))

        # self.internal = QtGui.QWidget(self)
        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEditClient.setObjectName('actEditClient')
        self.actPrintClient = getPrintAction(self, 'token', u'Напечатать талон')
        self.actPrintClient.setObjectName('actPrintClient')
        self.actPrintClientLabel = QtGui.QAction(u'Напечатать визитку пациента', self)
        self.actPrintClientLabel.setObjectName('actPrintClientLabel')
        self.actPrintClientLabel.setShortcut(QtGui.QKeySequence(QtCore.Qt.SHIFT+QtCore.Qt.Key_F6))
        templates = getPrintTemplates('clientLabel')
        self.clientLabelTemplate = templates[0] if templates else None
        self.actPrintClientList =   QtGui.QAction(u'Напечатать список пациентов', self)
        self.actPrintClientList.setObjectName('actPrintClientList')
        self.actEventEditClient =   QtGui.QAction(u'Изменить описание клиента', self)
        self.actEventEditClient.setObjectName('actEventEditClient')
        self.actAmbCardEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actAmbCardEditClient.setObjectName('actAmbCardEditClient')
        self.actActionEditClient =  QtGui.QAction(u'Изменить описание клиента', self)
        self.actActionEditClient.setObjectName('actActionEditClient')
        self.actEditActionEvent =  QtGui.QAction(u'Редактировать обращение', self)
        self.actEditActionEvent.setObjectName('actEditActionEvent')
        self.actExpertEditClient =  QtGui.QAction(u'Изменить описание клиента', self)
        self.actExpertEditClient.setObjectName('actExpertEditClient')
        self.actExpertTempInvalidDuplicate =  QtGui.QAction(u'Учесть дубликат документа', self)
        self.actExpertTempInvalidDuplicate.setObjectName('actExpertTempInvalidDuplicate')
        self.actExpertTempInvalidNext =       QtGui.QAction(u'Следующий документ', self)
        self.actExpertTempInvalidNext.setObjectName('actExpertTempInvalidNext')
        self.actExpertTempInvalidPrev =       QtGui.QAction(u'Предыдущий документ', self)
        self.actExpertTempInvalidPrev.setObjectName('actExpertTempInvalidPrev')
        self.actListVisitByQueue = QtGui.QAction(u'Протокол обращений пациента по предварительной записи', self)
        self.actListVisitByQueue.setObjectName('actListVisitByQueue')
        self.actControlDoublesRecordClient = QtGui.QAction(u'Логический контроль двойников', self)
        self.actControlDoublesRecordClient.setObjectName('actControlDoublesRecordClient')
        self.actReservedOrderQueueClient = QtGui.QAction(u'Использовать бронь в очереди', self)
        self.actReservedOrderQueueClient.setObjectName('actReservedOrderQueueClient')
        self.actAmbCreateEvent = QtGui.QAction(u'Новое обращение', self)
        self.actAmbCreateEvent.setObjectName('actAmbCreateEvent')
        self.actAmbDeleteOrder = QtGui.QAction(u'Удалить из очереди', self)
        self.actAmbDeleteOrder.setObjectName('actAmbDeleteOrder')
        self.actAmbChangeNotes =  QtGui.QAction(u'Изменить жалобы/примечания', self)
        self.actAmbChangeNotes.setObjectName('actAmbChangeNotes')
        self.actAmbPrintOrder =  QtGui.QAction(u'Напечатать направление', self)
        self.actAmbPrintOrder.setObjectName('actAmbPrintOrder')
        self.actJumpQueuePosition =  QtGui.QAction(u'Перейти в график', self)
        self.actJumpQueuePosition.setObjectName('actJumpQueuePosition')
        self.actPrintBeforeRecords =  QtGui.QAction(u'Печать предварительной записи', self)
        self.actPrintBeforeRecords.setObjectName('actPrintBeforeRecords')
        self.actShowPreRecordInfo = QtGui.QAction(u'Свойства записи', self)
        self.actShowPreRecordInfo.setObjectName('actShowPreRecordInfo')
        self.actOpenAccountingByEvent =  QtGui.QAction(u'Перейти к счетам', self)
        self.actOpenAccountingByEvent.setObjectName('actOpenAccountingByEvent')
        self.actOpenAccountingByAction = QtGui.QAction(u'Перейти к счетам', self)
        self.actOpenAccountingByAction.setObjectName('actOpenAccountingByAction')
        self.actOpenAccountingByVisit =  QtGui.QAction(u'Перейти к счетам', self)
        self.actOpenAccountingByVisit.setObjectName('actOpenAccountingByVisit')
        self.mnuPrint = QtGui.QMenu(self)
        self.mnuPrint.setObjectName('mnuPrint')
        self.mnuPrint.addAction(self.actPrintClient)
        self.mnuPrint.addAction(self.actPrintClientLabel)
        self.mnuPrint.addAction(self.actPrintClientList)

        # self.setWidget(self.internal)
        self.setupUi(self)
        # self.setWidgetResizable(True)
        self.setObjectName('RegistryWindow')

        self.btnPrint.setMenu(self.mnuPrint)
        self.btnPrint.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT+QtCore.Qt.Key_F6))


        if forceBool(getVal(
            QtGui.qApp.preferences.appPrefs, 'SocCard_SupportEnabled', False)):
            self.enableCardReaderSupport()

        self.setModels(self.tblClients, self.modelClients, self.selectionModelClients)
        self.setModels(self.tblQueue, self.modelQueue, self.selectionModelQueue)
        self.setModels(self.tblVisitByQueue, self.modelVisitByQueue, self.selectionModelVisitByQueue)


        self.cmbFilterDocumentType.setTable('rbDocumentType', True, 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')')
        self.cmbFilterPolicyType.setTable('rbPolicyType', True)

        self.idValidator = CIdValidator(self)
        self.edtFilterId.setValidator(self.idValidator)
        self.edtFilterBirthDay.setHighlightRedDate(False)
        self.chkListOnClientsPage = [
            (self.chkFilterId,        [self.edtFilterId,  self.cmbFilterAccountingSystem]),
            (self.chkFilterLastName,  [self.edtFilterLastName]),
            (self.chkFilterFirstName, [self.edtFilterFirstName]),
            (self.chkFilterPatrName,  [self.edtFilterPatrName]),
            (self.chkFilterBirthDay,  [self.edtFilterBirthDay]),
            (self.chkFilterSex,       [self.cmbFilterSex]),
            (self.chkFilterContact,   [self.edtFilterContact]),
            (self.chkFilterSNILS,     [self.edtFilterSNILS]),
            (self.chkFilterDocument,  [self.cmbFilterDocumentType,  self.edtFilterDocumentSerial, self.edtFilterDocumentNumber]),
            (self.chkFilterPolicy,    [self.cmbFilterPolicyType, self.cmbFilterPolicyInsurer, self.edtFilterPolicySerial, self.edtFilterPolicyNumber]),
            (self.chkFilterWorkOrganisation, [self.cmbWorkOrganisation, self.btnSelectWorkOrganisation]),
            (self.chkFilterCreatePerson, [self.cmbFilterCreatePerson]),
            (self.chkFilterCreateDate, [self.edtFilterBegCreateDate, self.edtFilterEndCreateDate]),
            (self.chkFilterModifyPerson, [self.cmbFilterModifyPerson]),
            (self.chkFilterModifyDate, [self.edtFilterBegModifyDate, self.edtFilterEndModifyDate]),
            (self.chkFilterAge,       [self.edtFilterBegAge, self.cmbFilterBegAge, self.edtFilterEndAge, self.cmbFilterEndAge]),
            (self.chkFilterAddress,   [self.cmbFilterAddressType,
                                       self.cmbFilterAddressCity,
                                       self.cmbFilterAddressStreet,
                                       self.lblFilterAddressHouse, self.edtFilterAddressHouse,
                                       self.lblFilterAddressCorpus, self.edtFilterAddressCorpus,
                                       self.lblFilterAddressFlat, self.edtFilterAddressFlat,
                                       ]),
            (self.chkFilterAddressOrgStructure, [self.cmbFilterAddressOrgStructureType, self.cmbFilterAddressOrgStructure]),
            (self.chkFilterBeds, [self.cmbFilterStatusBeds, self.cmbFilterOrgStructureBeds]),
            (self.chkFilterAddressIsEmpty, []),
            (self.chkFilterAttachType, [self.cmbFilterAttachTypeProperty, self.cmbFilterAttachType]),
            (self.chkFilterAttach,    [self.cmbFilterAttachOrganisation]),
            (self.chkFilterAttachNonBase, []),
            (self.chkFilterTempInvalid, [self.edtFilterBegTempInvalid, self.edtFilterEndTempInvalid]),
            (self.chkFilterRPFUnconfirmed, []),
            (self.chkFilterRPFConfirmed, [self.edtFilterBegRPFConfirmed, self.edtFilterEndRPFConfirmed]),
            ]


        self.cmbFilterAccountingSystem.setTable('rbAccountingSystem',  True)
        self.cmbFilterAccountingSystem.setValue(forceRef(getVal(
            QtGui.qApp.preferences.appPrefs, 'FilterAccountingSystem', 0)))

#        self.chkListOnEventsPage = [...


#        self.chkListOnActionsPage = [...
        self.__actionTypeIdListByClassPage = [None] * 4


#        self.chkListOnExpertPage = [...
        self.__tempInvalidDocTypeIdListByTypePage = [None] * 3

        QtCore.QMetaObject.connectSlotsByName(self) # т.к. в setupUi параметр не self
        for i in range(6):
            self.tblClients.setColumnHidden(6+i, True)


        self.RPFAccountingSystemId = forceRef(QtGui.qApp.db.translate('rbAccountingSystem', 'code', '1', 'id')) #FIXME: record code in code
        if not self.RPFAccountingSystemId:
            self.chkFilterRPFUnconfirmed.setEnabled(False)
            self.chkFilterRPFConfirmed.setEnabled(False)

        self.__filter = {}
        self.bufferRecordsOptionProperty = []

        self.txtClientInfoBrowser.actions.append(self.actEditClient)

        self.tblClients.createPopupMenu([self.actListVisitByQueue, self.actControlDoublesRecordClient, self.actReservedOrderQueueClient])
        self.tblClients.addPopupRecordProperies()
        self.tblQueue.createPopupMenu([self.actAmbCreateEvent, self.actAmbDeleteOrder, self.actAmbChangeNotes, self.actAmbPrintOrder, self.actJumpQueuePosition, self.actPrintBeforeRecords, self.actShowPreRecordInfo])

#        self.connect(self.tblClients, SIGNAL('requestNewEvent'), self.requestNewEvent)
        self.connect(self.tblClients.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.onListBeforeRecordClientPopupMenuAboutToShow)
        self.connect(self.tblQueue.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.onQueuePopupMenuAboutToShow)

        self.setFocusProxy(self.tabMain)
        # self.internal.setFocusProxy(self.tabMain)
        self.tabMain.setFocusProxy(self.tblClients) # на первый взгляд не нужно, но строка ниже не справляется...
        self.tabRegistry.setFocusProxy(self.tblClients)
        self.tabMainCurrentPage = 0
        self.currentClientFromEvent = False
        self.currentClientFromAction = False
        self.currentClientFromExpert = False
        self.controlSplitter = self.splitterRegistry
        self.tabMain.setCurrentIndex(self.tabMainCurrentPage)
        self.loadDialogPreferences()
        self.cmbFilterAddressCity.setCode(QtGui.qApp.defaultKLADR())
        self.personInfo = CRBModel(self)
        self.personInfo.setTable('vrbPersonWithSpeciality')
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentClientInfoChanged()'), self.updateQueue)

        # Права доступа ко вкладкам
        app = QtGui.qApp
        isAdmin = app.userHasRight(urAdmin)
        # чтение
        self.tabRegistry.setEnabled(isAdmin or app.userHasRight(urRegTabReadRegistry))
        # Запись\изменение
        # Вкладка Картотека: кнопки Редактировать и Регистрация
        self.btnEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteRegistry))
        self.btnNew.setEnabled(isAdmin or app.userHasRight(urRegTabWriteRegistry))
        # Вкладка  СМП
        #   зарезервировано право urRegTabWriteAmbulance
        # заполнение combobox-ов тип прикрепления
        self.fillCmbFilterAttachTypeProperty()
        self.fillCmbFilterAttachType()
        # перенести в exec_
        self.updateClientsList(self.__filter)


    def showAccountingDialog(self, eventId=None, actionId=None, visitId=None):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        dlg = CAccountingDialog(self)
        dlg.setWatchingFields(eventId, actionId, visitId)
        QtGui.qApp.restoreOverrideCursor()
        dlg.exec_()

    def fillCmbFilterAttachTypeProperty(self):
        self.cmbFilterAttachTypeProperty.addItem(u'', QtCore.QVariant())
        self.cmbFilterAttachTypeProperty.addItem(u'Постоянное', QtCore.QVariant('const'))
        self.cmbFilterAttachTypeProperty.addItem(u'Временное', QtCore.QVariant('tmp'))
        self.cmbFilterAttachTypeProperty.addItem(u'Выбыл', QtCore.QVariant('out'))

    def fillCmbFilterAttachType(self, index=0):
        self.cmbFilterAttachType.clear()
        attachTypeProperty = self.cmbFilterAttachTypeProperty.itemData(index)
        where = ''
        if not attachTypeProperty.isNull():
            attachTypeProperty = attachTypeProperty.toString()
            if attachTypeProperty == 'const':
                where = 'rbAttachType.`temporary` = 0'
            elif attachTypeProperty == 'tmp':
                where = 'rbAttachType.`temporary` = 1'
            elif attachTypeProperty == 'out':
                where = 'rbAttachType.`outcome` = 1'
        db = QtGui.qApp.db
        recordList = db.getRecordList('rbAttachType', '*', where)
        self.cmbFilterAttachType.addItem(u'', QtCore.QVariant())
        for record in recordList:
            self.cmbFilterAttachType.addItem(forceString(record.value('name')),
                                                         record.value('id'))


    def closeEvent(self, event):
        self.saveDialogPreferences()
        QtGui.qApp.preferences.appPrefs['FilterAccountingSystem'] = toVariant(
            self.cmbFilterAccountingSystem.value())
        super(CRegistryWindow, self).closeEvent(event)
        QtGui.qApp.mainWindow.registry = None
        if forceBool(getVal(
            QtGui.qApp.preferences.appPrefs, 'SocCard_SupportEnabled', False)):
            self.cardReader.finalize()


    def syncSplitters(self, nextSplitter):
        if nextSplitter != self.controlSplitter:
            nextSplitter.setSizes(self.controlSplitter.sizes())
            self.controlSplitter = nextSplitter


    def focusClients(self):
        self.tblClients.setFocus(QtCore.Qt.TabFocusReason)


    def focusEvents(self):
        self.tblEvents.setFocus(QtCore.Qt.TabFocusReason)


    def getLeavedHospitalBeds(self, orgStructureIdList):
        currentDate = QtCore.QDate.currentDate()
        db = QtGui.qApp.db
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')
        tableClient = db.table('Client')
        orgStructureBedsIdList = db.getDistinctIdList(tableOSHB, [tableOSHB['master_id']], [tableOSHB['master_id'].inlist(orgStructureIdList)])
        clientIdList = []
        if orgStructureBedsIdList:
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            cond = [ tableActionType['flatCode'].like('leaved%'),
                     tableAction['deleted'].eq(0),
                     tableEvent['deleted'].eq(0),
                     tableActionType['deleted'].eq(0),
                     tableClient['deleted'].eq(0),
                     tableEvent['setDate'].le(currentDate),
                     tableAction['begDate'].le(currentDate),
                     tableAction['endDate'].isNull()
                   ]
            stmt = db.selectStmt(queryTable, [tableEvent['id'].alias('eventId'), tableAction['id'].alias('actionId')], cond)
            query = db.query(stmt)
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            while query.next():
                record = query.record()
                eventId = forceRef(record.value('eventId'))
                actionId = forceRef(record.value('actionId'))
                cond = [ tableActionType['flatCode'].like('moving%'),
                         tableAction['deleted'].eq(0),
                         tableEvent['deleted'].eq(0),
                         tableEvent['id'].eq(eventId),
                         tableAP['deleted'].eq(0),
                         tableActionType['deleted'].eq(0),
                         tableAPT['deleted'].eq(0),
                         tableOS['deleted'].eq(0),
                         tableClient['deleted'].eq(0),
                         tableEvent['setDate'].le(currentDate),
                         tableAction['begDate'].le(currentDate),
                         tableAPT['typeName'].like('HospitalBed'),
                         tableAP['action_id'].eq(tableAction['id'])
                       ]
                order = u'Action.begDate DESC'
                cols = [tableClient['id']]
                strListId = ' IN ('+(','.join(str(orgId) for orgId in orgStructureBedsIdList))+')'
                cols.append(u'IF(OrgStructure.id%s, 1, 0) AS boolOrgStructure'%(strListId))
                firstRecord = db.getRecordEx(queryTable, cols, cond, order)
                if firstRecord:
                    if forceBool(firstRecord.value('boolOrgStructure')):
                        clientIdList.append(forceInt(firstRecord.value('id')))
        return clientIdList


    def getHospitalBeds(self, orgStructureIdList, indexFlatCode = 0):
        flatCode = [u'', u'moving', u'leaved', u'planning']
        currentDate = QtCore.QDate.currentDate()
        db = QtGui.qApp.db
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')
        tableClient = db.table('Client')
        orgStructureBedsIdList = db.getDistinctIdList(tableOSHB, [tableOSHB['master_id']], [tableOSHB['master_id'].inlist(orgStructureIdList)])
        if orgStructureBedsIdList:
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            cond = [ tableClient['deleted'].eq(0),
                     tableEvent['deleted'].eq(0),
                     tableAction['deleted'].eq(0),
                     tableAP['deleted'].eq(0),
                     tableActionType['deleted'].eq(0),
                     tableOS['deleted'].eq(0),
                     tableOS['id'].inlist(orgStructureBedsIdList),
                     tableEvent['setDate'].le(currentDate),
                     tableAction['begDate'].le(currentDate),
                     tableAPT['typeName'].like('HospitalBed'),
                     tableAP['action_id'].eq(tableAction['id'])
                   ]
            cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].ge(currentDate)]))
            cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(currentDate)]))
            if indexFlatCode == 1 or indexFlatCode == 3:
                cond.append(tableActionType['flatCode'].like(flatCode[indexFlatCode]))
            else:
                cond.append(db.joinOr([tableActionType['flatCode'].like('moving'), tableActionType['flatCode'].like('planning')]))
            return db.getDistinctIdList(queryTable, [tableClient['id']], cond)
        else:
            return None


    def updateClientsList(self, filter, posToId=None):
        """
            в соответствии с фильтром обновляет список пациентов.
        """
        db = QtGui.qApp.db

        def calcBirthDate(cnt, unit):
            result = QtCore.QDate.currentDate()
            if unit == 3: # дни
                result = result.addDays(-cnt)
            elif unit == 2: # недели
                result = result.addDays(-cnt*7)
            elif unit == 1: # месяцы
                result = result.addMonths(-cnt)
            else: # года
                result = result.addYears(-cnt)
            return result

        def addAddressCond(cond, addrType, addrIdList):
            tableClientAddress = db.table('ClientAddress')
            subcond = [tableClientAddress['client_id'].eqEx('`Client`.`id`'),
                       tableClientAddress['id'].eqEx('(SELECT MAX(`id`) FROM `ClientAddress` AS `CA` WHERE `CA`.`client_id` = `Client`.`id` AND `CA`.`type`=%d)' % addrType)
                      ]
            if addrIdList == None:
                subcond.append(tableClientAddress['address_id'].isNull())
            else:
                subcond.append(tableClientAddress['address_id'].inlist(addrIdList))
            cond.append(db.existsStmt(tableClientAddress, subcond))

        def addAttachCond(cond, subcond, attachTypeId=QtCore.QVariant(), attachTypeProperty=''):
            notOutcome = ''
            notTemporary = ''
            if attachTypeId.isNull() and not attachTypeProperty: #получается изначальный вариант
                notOutcome = 'AND NOT rbAttachType.outcome'
                notTemporary = 'AND NOT rbAttachType.temporary'
                subcond = 'AND '+subcond
            if not attachTypeId.isNull():
                if subcond:
                    subcond = 'AND '+subcond
                else:
                    subcond = ''
                notTemporary = 'AND CA2.attachType_id=%d'%forceInt(attachTypeId)
            attachTypeProperty2 = attachTypeProperty
            if attachTypeProperty:
                if subcond:
                    subcond = 'AND '+subcond
                else:
                    subcond = ''
                if attachTypeProperty == 'const':
                    attachTypeProperty = ' AND rbAttachType2.temporary=0 '
                elif attachTypeProperty == 'tmp':
                    attachTypeProperty = ' AND rbAttachType2.temporary=1 '
                elif attachTypeProperty == 'out':
                    attachTypeProperty = ' AND rbAttachType2.outcome=1 '
            stmt = '''EXISTS (SELECT ClientAttach.id
               FROM ClientAttach
               LEFT JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id
               WHERE ClientAttach.client_id = Client.id
               %s
               %s
               AND ClientAttach.id = (SELECT MAX(CA2.id)
                           FROM ClientAttach AS CA2
                           LEFT JOIN rbAttachType AS rbAttachType2 ON rbAttachType2.id = CA2.attachType_id
                           WHERE CA2.client_id = Client.id
                            %s %s))'''
            cond.append(stmt % (notOutcome,
                                subcond,
                                notTemporary,
                                attachTypeProperty))

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.__filter = filter
            cond = []
            tableClient = db.table('Client')
            if 'id' in filter:
                accountingSystemId = filter.get('accountingSystemId',  None)
                if accountingSystemId:
                    tableIdentification = db.table('ClientIdentification')
                    cond.append(db.existsStmt(tableIdentification,
                        [tableIdentification['client_id'].eq(tableClient['id']),
                         tableIdentification['accountingSystem_id'].eq(accountingSystemId),
                         tableIdentification['identifier'].eq(filter['id'])]))
                else:
                    cond.append(tableClient['id'].eq(filter['id']))
            database.addCondLike(cond, tableClient['lastName'],  addDots(filter.get('lastName', '')))
            database.addCondLike(cond, tableClient['firstName'], addDots(filter.get('firstName', '')))
            database.addCondLike(cond, tableClient['patrName'],  addDots(filter.get('patrName', '')))
            if 'birthDate' in filter:
                birthDate = filter['birthDate']
                if birthDate and birthDate.isNull():
                    birthDate = None
                cond.append(tableClient['birthDate'].eq(birthDate))
            if 'createPersonIdEx' in filter:
                self.addEqCond(cond, tableClient, 'createPerson_id', filter, 'createPersonIdEx')
            if 'begCreateDateEx' in filter:
                self.addDateCond(cond, tableClient, 'createDatetime', filter, 'begCreateDateEx', 'endCreateDateEx')
            if 'modifyPersonIdEx' in filter:
                self.addEqCond(cond, tableClient, 'modifyPerson_id', filter, 'modifyPersonIdEx')
            if 'begModifyDateEx' in filter:
                self.addDateCond(cond, tableClient, 'modifyDatetime', filter, 'begModifyDateEx', 'endModifyDateEx')
            if 'age' in filter:
                lowAge, highAge = filter['age']
                cond.append(tableClient['birthDate'].le(calcBirthDate(*lowAge)))
                cond.append(tableClient['birthDate'].ge(calcBirthDate(*highAge)))
            if filter.has_key('sex'):
                cond.append(tableClient['sex'].eq(filter.get('sex', 0)))
    #        database.addCondLike(cond, tableClient['SNILS'],     addDots(filter.get('SNILS', '')))
            if filter.has_key('SNILS'):
                cond.append(tableClient['SNILS'].eq(filter.get('SNILS', '')))
            table = tableClient
            if filter.has_key('contact'):
                tableContact = db.table('ClientContact')
                condContact = [tableContact['client_id'].eq(tableClient['id']),
                               tableContact['deleted'].eq(0),
                               tableContact['contact'].like(contactToLikeMask(filter['contact']))
                              ]
                cond.append(db.existsStmt(tableContact, condContact))
            doc = filter.get('doc', None)
            if doc:
                tableDoc = db.table('ClientDocument')
                condDoc = [tableDoc['client_id'].eq(tableClient['id']),
                           tableDoc['deleted'].eq(0)
                          ]
                typeId, serial, number = doc
                if typeId or serial or number:
                    if typeId:
                        condDoc.append(tableDoc['documentType_id'].eq(typeId))
                    if serial:
                        condDoc.append(tableDoc['serial'].eq(serial))
                    if number:
                        condDoc.append(tableDoc['number'].eq(number))
                    cond.append(db.existsStmt(tableDoc, condDoc))
                else:
                    cond.append('NOT '+db.existsStmt(tableDoc, condDoc))
            policy = filter.get('policy', None)
            if policy:
                tablePolicy = db.table('ClientPolicy')
                condPolicy = [tablePolicy['client_id'].eq(tableClient['id']),
                              tablePolicy['deleted'].eq(0)
                             ]
                policyType, insurerId, serial, number = policy
                if policyType or insurerId or serial or number:
                    if policyType:
                        condPolicy.append(tablePolicy['policyType_id'].eq(policyType))
                    if insurerId:
                        condPolicy.append(tablePolicy['insurer_id'].eq(insurerId))
                    if serial:
                        condPolicy.append(tablePolicy['serial'].eq(serial))
                    if number:
                        condPolicy.append(tablePolicy['number'].eq(number))
                    cond.append(db.existsStmt(tablePolicy, condPolicy))
                else:
                    cond.append('NOT '+db.existsStmt(tablePolicy, condPolicy))

            orgId = filter.get('orgId', None)
            if orgId:
                tableWork = db.table('ClientWork')
                joinCond = [ tableClient['id'].eq(tableWork['client_id']),
                             'ClientWork.id = (select max(CW.id) from ClientWork as CW where CW.client_id=Client.id)'
                           ]
                table = table.join(tableWork, joinCond)
                cond.append(tableWork['org_id'].eq(orgId))

            address = filter.get('address', None)
            if address:
                addrType, KLADRCode, KLADRStreetCode, house, corpus, flat = address
                tableAddressHouse = db.table('AddressHouse')
                tableAddress = db.table('Address')
                condAddr = [ tableAddressHouse['KLADRCode'].eq(KLADRCode),
                         tableAddressHouse['KLADRStreetCode'].eq(KLADRStreetCode),
                       ]
                if house:
                    condAddr.append( tableAddressHouse['number'].eq(house) )
                    condAddr.append( tableAddressHouse['corpus'].eq(corpus) )
                if flat:
                    condAddr.append( tableAddress['flat'].eq(flat) )
                addrIdList = db.getIdList(tableAddress.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id'])),
                                          tableAddress['id'].name(), condAddr)
                addAddressCond(cond, addrType, addrIdList)
            elif 'addressOrgStructure' in filter:
                addrType, orgStructureId = filter['addressOrgStructure']
                addrIdList = None
                cond2 = []
                if (addrType+1) & 1:
                    addrIdList = getOrgStructureAddressIdList(orgStructureId)
                    addAddressCond(cond2, 0, addrIdList)
                if (addrType+1) & 2:
                    if addrIdList is None:
                        addrIdList = getOrgStructureAddressIdList(orgStructureId)
                    addAddressCond(cond2, 1, addrIdList)
                if ((addrType+1) & 4):
                    if orgStructureId:
                        addAttachCond(cond2, 'orgStructure_id=%d'%orgStructureId)
                    else:
                        addAttachCond(cond2, 'LPU_id=%d'%QtGui.qApp.currentOrgId())
                if cond2:
                    cond.append(db.joinOr(cond2))
            elif 'addressIsEmpty' in filter:
                addAddressCond(cond, 0, None)
            if 'beds' in filter:
                indexFlatCode, orgStructureId = filter['beds']
                if orgStructureId:
                    bedsIdList = getOrgStructureDescendants(orgStructureId)
                else:
                    bedsIdList = getOrgStructures(QtGui.qApp.currentOrgId())
                if indexFlatCode == 2:
                    clientBedsIdList = self.getLeavedHospitalBeds(bedsIdList)
                else:
                    clientBedsIdList = self.getHospitalBeds(bedsIdList, indexFlatCode)
                cond.append(tableClient['id'].inlist(clientBedsIdList))
            if 'attachTo' in filter:
                attachOrgId = filter['attachTo']
                if attachOrgId:
                    if 'attachType' in filter:
                        attachType = filter['attachType'][0]
                        attachTypeProperty = filter['attachType'][1]
                    else:
                        attachType = QtCore.QVariant()
                        attachTypeProperty = ''
                    addAttachCond(cond, 'LPU_id=%d'%attachOrgId, attachType, attachTypeProperty)
                else:
                    pass # добавить - не имеет пост. прикрепления
            elif 'attachToNonBase' in filter:
                addAttachCond(cond, 'LPU_id!=%d'%QtGui.qApp.currentOrgId())
            if 'attachType' in filter:
                attachType = filter['attachType'][0]
                attachTypeProperty = filter['attachType'][1]
                if not attachType.isNull() or attachTypeProperty:
                    if 'attachTo' in filter:
                        if not filter['attachTo']:
                            addAttachCond(cond, None, attachType, attachTypeProperty)
                    else:
                        addAttachCond(cond, None, attachType, attachTypeProperty)
            if 'tempInvalid' in filter:
                begDate, endDate = filter['tempInvalid']
                tableTempInvalid = db.table('TempInvalid')
                condTempInvalid = [ tableTempInvalid['client_id'].eq(tableClient['id']) ]
                if begDate and begDate.isValid():
                    condTempInvalid.append(tableTempInvalid['endDate'].ge(begDate))
                if endDate and endDate.isValid():
                    condTempInvalid.append(tableTempInvalid['begDate'].le(endDate))
                cond.append(db.existsStmt(tableTempInvalid, condTempInvalid))
            if self.RPFAccountingSystemId:
                if filter.get('RPFUnconfirmed', False):
                    tableClientIdentification = db.table('ClientIdentification')
                    condClientIdentification  = [ tableClientIdentification['client_id'].eq(tableClient['id']),
                                                  tableClientIdentification['accountingSystem_id'].eq(self.RPFAccountingSystemId),
                                                ]
                    cond.append('NOT '+db.existsStmt(tableClientIdentification, condClientIdentification))
                elif 'RPFConfirmed' in filter:
                    begDate, endDate = filter['RPFConfirmed']
                    tableClientIdentification = db.table('ClientIdentification')
                    condClientIdentification  = [ tableClientIdentification['client_id'].eq(tableClient['id']),
                                                  tableClientIdentification['accountingSystem_id'].eq(self.RPFAccountingSystemId),
                                                ]
                    if begDate and begDate.isValid():
                        condClientIdentification.append(tableClientIdentification['checkDate'].ge(begDate))
                    if endDate and endDate.isValid():
                        condClientIdentification.append(tableClientIdentification['checkDate'].le(endDate))
                    cond.append(db.existsStmt(tableClientIdentification, condClientIdentification))

            clientsLimit = 10000
            idList = db.getIdList(table,
                                  tableClient['id'].name(),
                                  cond,
                                  [tableClient['lastName'].name(), tableClient['firstName'].name(), tableClient['patrName'].name(), tableClient['birthDate'].name(), tableClient['id'].name()],
                                  limit=clientsLimit)
            if len(idList) < clientsLimit:
                clientCount = len(idList)
            else:
                clientCount = db.getCount(table, tableClient['id'].name(), cond)
            self.tblClients.setIdList(idList, posToId, clientCount)
#            self.tabMain.setTabEnabled(1, bool(idList))
        finally:
            QtGui.QApplication.restoreOverrideCursor()
        self.focusClients()
        self.updateClientsListRequest = False
        if not idList:
            res = QtGui.QMessageBox.warning(self,
                            u'Внимание',
                            u'Пациент не обнаружен.\nХотите зарегистрировать пациента?',
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                            QtGui.QMessageBox.Ok)
            if res == QtGui.QMessageBox.Ok:
                self.editNewClient()
                self.focusClients()


    def getClientFilterAsText(self):
        filter  = self.__filter
        resList = []
        convertFilterToTextItem(resList, filter, 'id',        u'Код пациента',  unicode)
        convertFilterToTextItem(resList, filter, 'lastName',  u'Фамилия')
        convertFilterToTextItem(resList, filter, 'firstName', u'Имя')
        convertFilterToTextItem(resList, filter, 'patrName',  u'Отчество')
        convertFilterToTextItem(resList, filter, 'birthDate', u'Дата рождения', forceString)
        convertFilterToTextItem(resList, filter, 'sex',       u'Пол',           formatSex)
        convertFilterToTextItem(resList, filter, 'SNILS',     u'СНИЛС',         formatSNILS)
        convertFilterToTextItem(resList, filter, 'doc',       u'документ',      lambda doc: formatDocument(doc[0], doc[1], doc[2]))
        convertFilterToTextItem(resList, filter, 'policy',    u'полис',         lambda policy: formatPolicy(policy[0], policy[1], policy[2]))
        convertFilterToTextItem(resList, filter, 'orgId',     u'занятость',     getOrganisationShortName)
        convertFilterToTextItem(resList, filter, 'addressIsEmpty', u'адрес',    lambda dummy: u'пуст')
        return '\n'.join([item[0]+u': '+item[1] for item in resList])


    def showClientInfo(self, id):
        """
            показ информации о пациенте в панели наверху
        """
        if id:
            self.txtClientInfoBrowser.setHtml(getClientBanner(id))
        else :
            self.txtClientInfoBrowser.setText('')
        self.actEditClient.setEnabled(bool(id))
        QtGui.qApp.setCurrentClientId(id)


    def clientId(self, index):
        return self.tblClients.itemId(index)


    def selectedClientId(self):
        return self.tblClients.currentItemId()


    def currentClientId(self):
        return QtGui.qApp.currentClientId()


    def editClient(self, clientId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            if clientId:
                dialog.load(clientId)
            if dialog.exec_() :
                clientId = dialog.itemId()
                self.updateClientsList(self.__filter, clientId)


    def editCurrentClient(self):
        clientId = self.currentClientId()
        self.editClient(clientId)


    def findClient(self, clientId, clientRecord=None):
        self.tabMain.setCurrentIndex(0)
        if not clientRecord:
            db = QtGui.qApp.db
            clientRecord = db.getRecord('Client', 'lastName, firstName, patrName, sex, birthDate, SNILS', clientId)
        if clientRecord:
            filter = {}
            filter['id'] = clientId
            filter['accountingSystemId'] = None
            filter['lastName'] = forceString(clientRecord.value('lastName'))
            filter['firstName'] = forceString(clientRecord.value('firstName'))
            filter['patrName'] = forceString(clientRecord.value('patrName'))
            filter['sex'] = forceInt(clientRecord.value('sex'))
            filter['birthDate'] = forceDate(clientRecord.value('birthDate'))
            filter['SNILS'] = forceString(clientRecord.value('SNILS'))
            self.__filter = self.updateFilterWidgets(filter)
            if not self.__filter:
                self.__filter = self.updateFilterWidgets({'id': clientId, 'accountingSystemId':None}, True)
            self.updateClientsList(self.__filter, clientId)
            self.tabMain.setTabEnabled(1, True)


    def getParamsDialogFilter(self):
        dialogInfo = {}
        if self.chkFilterLastName.isChecked():
            dialogInfo['lastName'] = forceString(self.edtFilterLastName.text())
        if self.chkFilterFirstName.isChecked():
            dialogInfo['firstName'] = forceString(self.edtFilterFirstName.text())
        if self.chkFilterPatrName.isChecked():
            dialogInfo['patrName'] = forceString(self.edtFilterPatrName.text())
        if self.chkFilterBirthDay.isChecked():
            dialogInfo['birthDate'] = forceDate(self.edtFilterBirthDay.date())
        if self.chkFilterSex.isChecked():
            dialogInfo['sex'] = self.cmbFilterSex.currentIndex()
        if self.chkFilterSNILS.isChecked():
            dialogInfo['SNILS'] = self.edtFilterSNILS.text()
        if self.chkFilterDocument.isChecked():
            dialogInfo['docType'] = self.cmbFilterDocumentType.value()
            serial = self.edtFilterDocumentSerial.text()
            for c in '-=/_|':
                serial = serial.replace('c',' ')
            serial = forceStringEx(serial).split()
            dialogInfo['serialLeft'] = serial[0] if len(serial)>=1 else ''
            dialogInfo['serialRight'] = serial[1] if len(serial)>=2 else ''
            dialogInfo['docNumber'] = self.edtFilterDocumentNumber.text()
        if self.chkFilterContact.isChecked():
            dialogInfo['contact'] = forceString(self.edtFilterContact.text())
        if self.chkFilterPolicy.isChecked():
            dialogInfo['polisSerial'] = forceString(self.edtFilterPolicySerial.text())
            dialogInfo['polisNumber'] = forceString(self.edtFilterPolicyNumber.text())
            dialogInfo['polisCompany'] = self.cmbFilterPolicyInsurer.value()
            dialogInfo['polisType'] = self.cmbFilterPolicyType.value()
            dialogInfo['polisTypeName'] = self.cmbFilterPolicyType.model().getName(self.cmbFilterPolicyType.currentIndex())
        if self.chkFilterAddress.isChecked():
            dialogInfo['addressType'] = self.cmbFilterAddressType.currentIndex()
            dialogInfo['regCity'] = self.cmbFilterAddressCity.code()
            dialogInfo['regStreet'] = self.cmbFilterAddressStreet.code()
            dialogInfo['regHouse'] = self.edtFilterAddressHouse.text()
            dialogInfo['regCorpus'] = self.edtFilterAddressCorpus.text()
            dialogInfo['regFlat'] = self.edtFilterAddressFlat.text()
        return dialogInfo


    def editNewClient(self):
        dialog = CClientEditDialog(self)
        dialogInfo = self.getParamsDialogFilter()
        if dialogInfo:
            dialog.setClientDialogInfo(dialogInfo)
        if dialog.exec_():
            clientId = dialog.itemId()
            clientRecord = dialog.getRecord()
            self.findClient(clientId, clientRecord)


    def findControlledByChk(self, chk):
        for s in self.chkListOnClientsPage:
            if s[0] == chk:
                return s[1]
        return None


    def activateFilterWdgets(self, alist):
        if alist:
            for s in alist:
                s.setEnabled(True)
                if isinstance(s, (QtGui.QLineEdit, CDateEdit)):
                    s.selectAll()
            alist[0].setFocus(QtCore.Qt.ShortcutFocusReason)
            alist[0].update()


    def deactivateFilterWdgets(self, alist):
        for s in alist:
            s.setEnabled(False)


    def updateFilterWidgets(self, filter, force=False):
        def intUpdateClientFilterLineEdit(chk, widget, inFilter, name, outFilter):
            val = inFilter.get(name, None)
            if val and (chk.isChecked() or force):
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setText(unicode(val))
                outFilter[name] = val

        def intUpdateClientFilterComboBox(chk, widget, inFilter, name, outFilter):
            if name in inFilter and (chk.isChecked() or force):
                val = inFilter[name]
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setCurrentIndex(val)
                outFilter[name] = val

        def intUpdateClientFilterRBComboBox(chk, widget, inFilter, name, outFilter):
            if name in inFilter and (chk.isChecked() or force):
                val = inFilter[name]
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setValue(val)
                outFilter[name] = val

        def intUpdateClientFilterDateEdit(chk, widget, inFilter, name, outFilter):
            val = inFilter.get(name, None)
            if val and (chk.isChecked() or force):
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setDate(val)
                outFilter[name] = val

        outFilter = {}
        for s in self.chkListOnClientsPage:
            chk = s[0]
            if chk == self.chkFilterId:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'id', outFilter)
                intUpdateClientFilterRBComboBox(chk, s[1][1], filter, 'accountingSystemId', outFilter)
            elif chk == self.chkFilterLastName:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'lastName', outFilter)
            elif chk == self.chkFilterFirstName:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'firstName', outFilter)
            elif chk == self.chkFilterPatrName:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'patrName', outFilter)
            elif chk == self.chkFilterSex:
                value = intUpdateClientFilterComboBox(chk, s[1][0], filter, 'sex', outFilter)
            elif chk == self.chkFilterBirthDay:
                value = intUpdateClientFilterDateEdit(chk, s[1][0], filter, 'birthDate', outFilter)
            elif chk == self.chkFilterContact:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'contact', outFilter)
            elif chk == self.chkFilterSNILS:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'SNILS', outFilter)
            else:
                chk.setChecked(False)
                self.deactivateFilterWdgets(s[1])
        return outFilter


    def setChkFilterChecked(self, chk, checked):
        chk.setChecked(checked)
        self.onChkFilterClicked(chk, checked)


    def onChkFilterClicked(self, chk, checked):
        controlled = self.findControlledByChk(chk)
        if checked:
            self.activateFilterWdgets(controlled)
        else:
            self.deactivateFilterWdgets(controlled)


    def findEvent(self, eventId):
        self.tabMain.setCurrentIndex(1)
        if eventId in self.modelEvents.idList():
            self.tblEvents.setCurrentItemId(eventId)
        else:
            filter = {}
            self.updateEventsList(filter, eventId)


    def setEventList(self, eventIdList):
        self.tabMain.setCurrentIndex(1)
        self.tblEvents.setIdList(eventIdList)
#            filter = {}
#            self.updateEventsList(filter, eventId)


    def requestNewEvent(self):
        clientId = self.currentClientId()
        dockFreeQueue = QtGui.qApp.mainWindow.dockFreeQueue
        if dockFreeQueue and dockFreeQueue.content and dockFreeQueue.content._appLockId:
            dockFreeQueue.content.on_actAmbCreateOrder_triggered()
        elif clientId:
            return requestNewEvent(self, clientId)
        return None


    #########################################################################


    def keyPressEvent(self, event):
        """
            перехват нажатия на кнопку Enter с целью завершить заполнение поля фильтра
            и применения фильтра. возможно, что необходимо переделать на QShortcut
            NB! кнопка Enter называется Qt.Key_Return
        """
        if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
            focused = self.focusWidget()
            for s in self.chkListOnClientsPage:
                if s[0] == focused or focused in s[1]:
                    event.setAccepted(True)
                    self.on_buttonBox_apply()
                    return
            if focused == self.cmbFilterEventByClient:
                event.setAccepted(True)
                self.on_buttonBoxEvent_apply()
                return

        super(CRegistryWindow, self).keyPressEvent(event)

    #########################################################################
    def setCmbFilterEventTypeFilter(self, eventPurposeId):
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbFilterEventType.setFilter(filter)


    def addEqCond(self, cond, table, fieldName, filter, name):
        if name in filter:
            cond.append(table[fieldName].eq(filter[name]))


    def addLikeCond(self, cond, table, fieldName, filter, name):
        if name in filter:
            cond.append(table[fieldName].like(filter[name]))


    def addDateCond(self, cond, table, fieldName, filter, begDateName, endDateName):
        begDate = filter.get(begDateName, None)
        if begDate and not begDate.isNull():
            cond.append(table[fieldName].ge(begDate))
        endDate = filter.get(endDateName, None)
        if endDate and not endDate.isNull():
            cond.append(table[fieldName].lt(endDate.addDays(1)))


    def addRangeCond(self, cond, table, fieldName, filter, begName, endName):
        if begName in filter:
            cond.append(table[fieldName].ge(filter[begName]))
        if endName in filter:
            cond.append(table[fieldName].le(filter[endName]))


    def updateEventListAfterEdit(self, eventId):
        if self.tabMain.currentIndex() == 1:
            self.updateEventsList(self.__eventFilter, eventId)
        QtGui.qApp.emitCurrentClientInfoChanged()


    def updateEventsList(self, filter, posToId=None):
        # в соответствии с фильтром обновляет список событий.
        self.__eventFilter = filter
        db = QtGui.qApp.db
        table = db.table('Event')
        queryTable = table
        cond = [table['deleted'].eq(0)]
        self.addEqCond(cond, table, 'id', filter, 'id')
        self.addEqCond(cond, table, 'createPerson_id', filter, 'createPersonId')
        self.addDateCond(cond, table, 'createDatetime', filter, 'begCreateDate', 'endCreateDate')
        self.addEqCond(cond, table, 'modifyPerson_id', filter, 'modifyPersonId')
        self.addDateCond(cond, table, 'modifyDatetime', filter, 'begModifyDate', 'endModifyDate')
        if 'clientIds' in filter:
            clientIds = filter['clientIds']
            cond.append(table['client_id'].inlist(clientIds))
        if 'externalId' in filter:
            cond.append(table['externalId'].eq(filter['externalId']))
        if 'accountSumLimit' in filter:
            accountSumLimit = filter.get('accountSumLimit', 0)
            sumLimitFrom = filter.get('sumLimitFrom', 0)
            sumLimitTo = filter.get('sumLimitTo', 0)
            sumLimitDelta = filter.get('sumLimitDelta', 0)
            tableEventLocalContract = db.table('Event_LocalContract')
            queryTable = queryTable.innerJoin(tableEventLocalContract, tableEventLocalContract['master_id'].eq(table['id']))
            cond.append(tableEventLocalContract['deleted'].eq(0))
            cond.append(tableEventLocalContract['sumLimit'].gt(0))
            if sumLimitFrom or sumLimitTo and sumLimitFrom <= sumLimitTo:
                cond.append(tableEventLocalContract['sumLimit'].ge(sumLimitFrom))
                cond.append(tableEventLocalContract['sumLimit'].le(sumLimitTo))
            if accountSumLimit == 1:
                cond.append(table['totalCost'].gt(tableEventLocalContract['sumLimit']))
                if sumLimitDelta > 0:
                    cond.append(u'Event.totalCost >= (Event_LocalContract.sumLimit + %d)'%(sumLimitDelta))
            elif accountSumLimit == 2:
                cond.append(table['totalCost'].lt(tableEventLocalContract['sumLimit']))
                if sumLimitDelta > 0:
                    cond.append(u'Event.totalCost <= (Event_LocalContract.sumLimit + %d)'%(sumLimitDelta))
        self.addDateCond(cond, table, 'setDate', filter, 'begSetDate', 'endSetDate')
        if filter.get('emptyExecDate', False):
            cond.append(table['execDate'].isNull())
        self.addDateCond(cond, table, 'execDate', filter, 'begExecDate', 'endExecDate')
        self.addDateCond(cond, table, 'nextEventDate', filter, 'begNextDate', 'endNextDate')
        eventPurposeId = filter.get('eventPurposeId', None)
        if eventPurposeId:
            cond.append(table['eventType_id'].name()+' IN (SELECT id FROM EventType WHERE EventType.purpose_id=%d)' % eventPurposeId)
        if 'eventTypeId' in filter:
            cond.append(table['eventType_id'].eq(filter['eventTypeId']))
        elif not eventPurposeId:
            queryTable = getWorkEventTypeFilter(queryTable, cond)
        if 'personId' in filter:
            cond.append(table['execPerson_id'].eq(filter['personId']))
        else:
            if 'specialityId' in filter or 'orgStructureId' in filter:
                tablePerson = db.table('Person')
                queryTable = queryTable.join(tablePerson, tablePerson['id'].eq(table['execPerson_id']))
            if 'specialityId' in filter:
                cond.append(tablePerson['speciality_id'].eq(filter['specialityId']))
            if 'orgStructureId' in filter:
                orgStructureId = filter.get('orgStructureId', None)
                if orgStructureId:
                    orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
                    if orgStructureIdList:
                        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
        if 'relegateOrgId' in filter:
            cond.append(table['relegateOrg_id'].eq(filter['relegateOrgId']))
        if filter.get('dispanserObserved', False):
            condDispanserObserved  = 'EXISTS (SELECT * FROM Diagnostic LEFT JOIN rbDispanser ON rbDispanser.id = Diagnostic.dispanser_id WHERE Diagnostic.event_id = Event.id AND rbDispanser.observed)'
            cond.append(condDispanserObserved)
#            cond.append(table['execDate'].isNull())
        self.addEqCond(cond, table, 'org_id', filter, 'LPUId')
        if filter.get('nonBase', False):
            cond.append(table['org_id'].ne(QtGui.qApp.currentOrgId()))
        mesCode = filter.get('mesCode', None)
        if mesCode is not None:
            if mesCode:
                condMes  = 'MES_id IN (SELECT id FROM mes.MES WHERE code LIKE %s)' % quote(database.undotLikeMask(mesCode))
                cond.append(condMes)
            else:
                cond.append(table['eventType_id'].name()+' IN (SELECT id FROM EventType WHERE EventType.mesRequired)')
                cond.append(table['MES_id'].isNull())

        self.addEqCond(cond, table, 'result_id', filter, 'eventResultId')
        if filter.get('errorInDiagnostic', False):
            condErrInFinish = '(SELECT COUNT(*) FROM Diagnostic WHERE Diagnostic.event_id = Event.id AND diagnosisType_id=(SELECT id FROM rbDiagnosisType WHERE code=\'1\')) != 1'
            condErrInGroup  = 'EXISTS (SELECT * FROM Diagnostic WHERE Diagnostic.event_id = Event.id AND healthGroup_id IS NULL)'
            cond.append(db.joinOr([condErrInFinish, condErrInGroup]))

        payStatusFinanceCode = filter.get('payStatusFinanceCode', None)
        if payStatusFinanceCode:
            payStatusCode = filter.get('payStatusCode', 0)
            mask  = getPayStatusMaskByCode(payStatusFinanceCode)
            value = getPayStatusValueByCode(payStatusCode, payStatusFinanceCode)
            cond.append('((%s & %d) = %d)' % (table['payStatus'].name(), mask, value))

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            idList = db.getIdList(queryTable,
                           table['id'].name(),
                           cond,
                           ['setDate DESC', 'id'])
#                           ['execDate DESC', 'id'])
            self.tblEvents.setIdList(idList, posToId)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        hideClientInfo = 'clientIds' in filter and len(filter['clientIds']) == 1
        for i in xrange(3):
            self.tblEvents.setColumnHidden(i, hideClientInfo)


    def getEventFilterAsText(self):
        db = QtGui.qApp.db
        filter  = self.__eventFilter
        resList = []

        clientIds = filter.get('clientIds', None)
        if clientIds and len(clientIds) == 1:
            resList.append((u'пациент', getClientMiniInfo(clientIds[0])))
        elif clientIds is None:
            resList.append((u'список пациентов', u'полный'))
        else:
            resList.append((u'список пациентов', u'из вкладки'))

        tmpList = [
            ('begSetDate', u'Дата назначения с', forceString),
            ('endSetDate', u'Дата назначения по', forceString),
            ('emptyExecDate', u'Пустая дата выполнения', lambda dummy: ''),
            ('begExecDate', u'Дата выполнения с', forceString),
            ('endExecDate', u'Дата выполнения по', forceString),
            ('begNextDate', u'Дата следующей явки с', forceString),
            ('endNextDate', u'Дата следующей явки по', forceString),
            ('eventTypeId', u'Тип обращения',
                lambda id: getEventName(id)),
            ('specialityId', u'Специальность',
                lambda id: forceString(db.translate('rbSpeciality', 'id', id, 'name'))),
            ('personId', u'Выполнил',
                lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('dispanserObserved', u'Дисп.наблюдение', lambda dummy: ''),
            ('LPUId', u'ЛПУ', getOrganisationShortName),
            ('nonBase', u'Не базовое ЛПУ', lambda dummy: ''),
            ('eventResultId', u'Результат обращения',
                lambda id: forceString(db.translate('rbResult', 'id', id, 'name'))),
            ('errorInDiagnostic', u'Ошибки', lambda dummy: ''),
            ]
        for (key, title, ftm) in tmpList:
            convertFilterToTextItem(resList, filter, key, title, ftm)
        return '\n'.join([ ': '.join(item) for item in resList])


    def eventId(self, index):
        return self.tblEvents.itemId(index)


    def currentEventId(self):
        return self.tblEvents.currentItemId()


    def updateEventInfo(self, eventId):
        db = QtGui.qApp.db
        record = db.getRecord('Event', ['createDatetime','createPerson_id', 'modifyDatetime', 'modifyPerson_id', 'externalId', 'client_id', 'payStatus', 'note'], eventId)
        if record:
            createDatetime = dateTimeToString(record.value('createDatetime').toDateTime())
            createPersonId = forceRef(record.value('createPerson_id'))
            modifyDatetime = dateTimeToString(record.value('modifyDatetime').toDateTime())
            modifyPersonId = forceRef(record.value('modifyPerson_id'))
            externalId     = forceString(record.value('externalId'))
            clientId       = forceRef(record.value('client_id'))
            note           = forceString(record.value('note'))
            payStatus      = forceInt(record.value('payStatus'))
        else:
            createDatetime = ''
            createPersonId = None
            modifyDatetime = ''
            modifyPersonId = None
            externalId     = ''
            clientId       = None
            note           = ''
            payStatus      = 0

        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.txtClientInfoBrowserEvents.setHtml(getClientBanner(clientId))
        else:
            self.txtClientInfoBrowserEvents.setText('')
        self.actEventEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

        if eventId:
            table = db.table('Diagnostic')
            idList = db.getIdList(table, 'id', [table['event_id'].eq(eventId),table['deleted'].eq(0)],  ['id'])
            self.tblEventDiagnostics.setIdList(idList)

            table = db.table('Action')
            idList = db.getIdList(table, 'id', [table['event_id'].eq(eventId),table['deleted'].eq(0)], ['id'])
            self.tblEventActions.setIdList(idList)

            table = db.table('Visit')
            idList = db.getIdList(table, 'id', [table['event_id'].eq(eventId),table['deleted'].eq(0)], ['id'])
            self.tblEventVisits.setIdList(idList)
        else:
            self.tblEventDiagnostics.setIdList([])
            self.tblEventActions.setIdList([])
            self.tblEventVisits.setIdList([])


        self.lblEventIdValue.setText(str(eventId) if eventId else '')
        self.lblEventExternalIdValue.setText(externalId)
        self.lblEventCreateDateTimeValue.setText(createDatetime)
        self.lblEventCreatePersonValue.setText(self.getPersonText(createPersonId))
        self.lblEventModifyDateTimeValue.setText(modifyDatetime)
        self.lblEventModifyPersonValue.setText(self.getPersonText(modifyPersonId))
        self.lblEventNoteValue.setText(note)
        self.lblEventPayStatusValue.setText(payStatusText(payStatus))


    def getPersonText(self, personId):
        if personId:
            index = self.personInfo.searchId(personId)
            if index:
                return self.personInfo.getCode(index)+' | '+self.personInfo.getName(index)
            else:
                return '{'+str(personId)+'}'
        else:
            return ''

    def updateFilterEventResultTable(self):
        if self.chkFilterEventPurpose.isChecked():
            purposeId = self.cmbFilterEventPurpose.value()
        else:
            purposeId = None
        if purposeId is None:
            if self.chkFilterEventType.isChecked():
                eventTypeId = self.cmbFilterEventType.value()
            else:
                eventTypeId = None
            if eventTypeId:
                purposeId = getEventPurposeId(eventTypeId)
        filter = ('eventPurpose_id=\'%d\'' % purposeId) if purposeId else ''
        self.cmbFilterEventResult.setTable('rbResult', False, filter)


    #########################################################################

    def updateAmbCardInfo(self):
        clientId = self.currentClientId()
        if clientId:
            self.txtClientInfoBrowserAmbCard.setHtml(getClientBanner(clientId))
        else:
            self.txtClientInfoBrowserAmbCard.setText('')
        self.actAmbCardEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

    #########################################################################

    def editAction(self, actionId):
        dialog = CActionEditDialog(self)
        dialog.load(actionId)
        if dialog.exec_():
            self.updateActionsList(self.__actionFilter, dialog.itemId())
            QtGui.qApp.emitCurrentClientInfoChanged()
            return dialog.itemId()
        else:
            self.updateActionInfo(actionId)
            self.updateClientsListRequest = True
        return None


    def updateActionsList(self, filter, posToId=None):
        """
            в соответствии с фильтром обновляет список действий (мероприятий).
        """
        self.__actionFilter = filter
        optionPropertyIdList = []
        db = QtGui.qApp.db
        table = db.table('Action')
        tableEvent = db.table('Event')
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyType = db.table('ActionPropertyType')
        queryTable = table.leftJoin(tableEvent, tableEvent['id'].eq(table['event_id']) )
        cond = [table['deleted'].eq(0), tableEvent['deleted'].eq(0)]
        self.addEqCond(cond, table, 'id', filter, 'id')
        self.addEqCond(cond, table, 'createPerson_id', filter, 'createPersonId')
        self.addDateCond(cond, table, 'createDatetime', filter, 'begCreateDate', 'endCreateDate')
        self.addEqCond(cond, table, 'modifyPerson_id', filter, 'modifyPersonId')
        self.addDateCond(cond, table, 'modifyDatetime', filter, 'begModifyDate', 'endModifyDate')
        if 'clientIds' in filter:
            clientIds = filter.get('clientIds')
            cond.append(tableEvent['client_id'].inlist(clientIds))
        if 'eventIds' in filter:
            eventIds = filter.get('eventIds')
            cond.append(table['event_id'].inlist(eventIds))
        if 'isUrgent' in filter:
#            isUrgent = filter.get('isUrgent')
            cond.append(table['isUrgent'].ne(0))
        self.addDateCond(cond, table, 'directionDate', filter, 'begSetDate', 'endSetDate')
        self.addDateCond(cond, table, 'plannedEndDate', filter, 'begPlannedEndDate', 'endPlannedEndDate')
        self.addDateCond(cond, table, 'endDate', filter, 'begExecDate', 'endExecDate')

        actionClass = self.tabWidgetActionsClasses.currentIndex()
        if 'actionTypeId' in filter:
            actionTypeIdList = getActionTypeDescendants(filter['actionTypeId'], actionClass)
            cond.append(table['actionType_id'].inlist(actionTypeIdList))
        else:
            cond.append(table['actionType_id'].name()+' IN (SELECT ActionType.id FROM ActionType WHERE ActionType.class=%d)' % actionClass)
# сделано без учета значений value в таблицах ActionProperty_Double, ActionProperty_Action и т.п., учитывается наличие записи в ActionProperty, т.к. считается, что при не заполнении не создается запись в ActionProperty.
        if self.chkTakeIntoAccountProperty.isChecked():
            if self.chkListProperty.isChecked() and not self.chkThresholdPenaltyGrade.isChecked():
                if not ('booleanFilledProperty' in filter):
                    queryTable = queryTable.leftJoin(tableActionPropertyType, tableActionPropertyType['actionType_id'].eq(table['actionType_id']))
                optionPropertyIdList = self.getDataOptionPropertyChecked()
                if optionPropertyIdList != []:
                    cond.append(tableActionPropertyType['id'].inlist(optionPropertyIdList))
            if 'booleanFilledProperty' in filter:
                if filter.get('booleanFilledProperty') == True:
                    queryTable = queryTable.leftJoin(tableActionProperty, tableActionProperty['action_id'].eq(table['id']))
                    queryTable = queryTable.leftJoin(tableActionPropertyType, tableActionPropertyType['id'].eq(tableActionProperty['type_id']))
                    cond.append(tableActionProperty['deleted'].eq(0))
                elif not self.chkThresholdPenaltyGrade.isChecked():
                    queryTable = queryTable.leftJoin(tableActionPropertyType, tableActionPropertyType['actionType_id'].eq(table['actionType_id']))
                    cond.append(u'Action.id NOT IN (SELECT DISTINCT AP.action_id FROM ActionProperty AS AP WHERE AP.deleted = 0)')
            if self.chkThresholdPenaltyGrade.isChecked() and ('thresholdPenaltyGrade' in filter):
                filterPenaltyGrade = filter.get('thresholdPenaltyGrade')
                if filterPenaltyGrade:
                    whereOptionPropertyId = u''
                    if self.chkListProperty.isChecked():
                        optionPropertyIdList = self.getDataOptionPropertyChecked()
                        if optionPropertyIdList != []:
                            strPropertyIdList = u''
                            col =len(optionPropertyIdList) - 1
                            for propertyId in optionPropertyIdList:
                                strPropertyIdList += forceString(propertyId)
                                col -= 1
                                if col > 0:
                                    strPropertyIdList +=  u', '
                            whereOptionPropertyId = u'(APT.id IN (%s)) AND ' % (strPropertyIdList)
                    cond.append(u'SELECT SUM(APT.penalty) >= %s FROM ActionPropertyType AS APT WHERE %s(APT.id NOT IN (SELECT AP.type_id FROM ActionProperty AS AP WHERE AP.action_id = Action.id AND AP.deleted = 0 GROUP BY AP.type_id) AND (APT.actionType_id = Action.actionType_id))' % (filterPenaltyGrade, whereOptionPropertyId))
        if 'setPersonId' in filter:
            cond.append(table['setPerson_id'].eq(filter['setPersonId']))
        elif 'setSpecialityId' in filter:
            tablePerson = db.table('Person')
            queryTable = queryTable.join(tablePerson, tablePerson['id'].eq(table['setPerson_id']))
            cond.append(tablePerson['speciality_id'].eq(filter['setSpecialityId']))
        if 'execPersonId' in filter:
            cond.append(table['person_id'].eq(filter['execPersonId']))
        if 'assistantId' in filter:
            cond.append(u"EXISTS(SELECT A_A.id "
                                u"       FROM Action_Assistant AS A_A"
                                u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                                u"       WHERE A_A.action_id = %s "
                                u"              AND rbAAT.code like 'assistant'"
                                u"              AND A_A.person_id = %s)"  % (table['id'].name(),
                                                                             filter['assistantId']))
        elif 'execSpecialityId' in filter:
            tablePersonExec = db.table('Person').alias('PersonExec')
            queryTable = queryTable.join(tablePersonExec, tablePersonExec['id'].eq(table['person_id']))
            cond.append(tablePersonExec['speciality_id'].eq(filter['execSpecialityId']))
        self.addEqCond(cond, table, 'status', filter, 'status')

        payStatusFinanceCode = filter.get('payStatusFinanceCode', None)
        if payStatusFinanceCode:
            payStatusCode = filter.get('payStatusCode', 0)
            mask  = getPayStatusMaskByCode(payStatusFinanceCode)
            value = getPayStatusValueByCode(payStatusCode, payStatusFinanceCode)
            cond.append('((%s & %d) = %d)' % (table['payStatus'].name(), mask, value))

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            idList = db.getDistinctIdList(queryTable,
                           table['id'].name(),
                           cond,
                           ['execDate DESC', 'id'])
            self.setActionsIdList(idList, posToId)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        actionsFilterType = filter['actionsFilterType']
        if actionsFilterType in [0, 2]:
            hideClientInfo = True
        elif actionsFilterType == 1:
            hideClientInfo = len(filter['clientIds']) == 1
        elif actionsFilterType == 3:
            hideClientInfo = len(filter['eventIds']) == 1 or \
            len(self.__eventFilter.get('clientIds', [])) == 1
        else:
            hideClientInfo = False
        table = self.getCurrentActionsTable()
        for i in range(3):
            table.setColumnHidden(i, hideClientInfo)


    def getActionFilterAsText(self):
        db = QtGui.qApp.db
        filter  = self.__actionFilter
        resList = []

        actionsFilterType = filter['actionsFilterType']
        if actionsFilterType in [0, 1]:
            clientIds = filter.get('clientIds', None)
            if clientIds and len(clientIds) == 1:
                resList.append((u'пациент', getClientMiniInfo(clientIds[0])))
            elif clientIds and len(clientIds) > 1:
                resList.append((u'список пациентов', u'из вкладки'))
        elif actionsFilterType in [2, 3]:
            clientIds = self.__eventFilter.get('clientIds', None)
            if clientIds and len(clientIds) == 1:
                resList.append((u'пациент', getClientMiniInfo(clientIds[0])))
            elif clientIds and len(clientIds) > 1:
                resList.append((u'список пациентов', u'по списку осмотров'))
        else:
            resList.append((u'список пациентов', u'полный'))

        tmpList = [
            ('begSetDate', u'Дат�� назначения с', forceString),
            ('endSetDate', u'Дата назначения по', forceString),
            ('actionTypeId', u'Тип мероприятия',
                lambda id: forceString(db.translate('ActionType', 'id', id, 'name'))),
            ('setSpecialityId', u'Специальность назначившего',
                lambda id: forceString(db.translate('rbSpeciality', 'id', id, 'name'))),
            ('personId', u'Назначил',
                lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('isUrgent',   u'Срочно', lambda dummy: u'+'),
            ('begPlannedEndDate', u'Плановая дата выполнения с', forceString),
            ('endPlannedEndDate', u'Плановая дата окончания по', forceString),
            ('begExecDate', u'Дата выполнения с', forceString),
            ('endExecDate', u'Дата выполнения по', forceString),
            ]
        for (x, y, z) in tmpList:
            convertFilterToTextItem(resList, filter, x, y, z)
        return '\n'.join([ ': '.join(item) for item in resList])


    def getCurrentActionsTable(self):
        index = self.tabWidgetActionsClasses.currentIndex()
        return [self.tblActionsStatus, self.tblActionsDiagnostic, self.tblActionsCure, self.tblActionsMisc][index]


    def currentActionId(self):
        return self.getCurrentActionsTable().currentItemId()


    def setActionsIdList(self, idList, posToId):
        self.getCurrentActionsTable().setIdList(idList, posToId)


    def focusActions(self):
        self.getCurrentActionsTable().setFocus(QtCore.Qt.TabFocusReason)


    def updateActionInfo(self, actionId):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        table = tableAction.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        record = db.getRecord(table,
                              ['Action.createDatetime','Action.createPerson_id', 'Action.modifyDatetime', 'Action.modifyPerson_id', 'Event.client_id', 'Action.payStatus', 'Action.note'], actionId)
        if record:
            createDatetime = dateTimeToString(record.value('createDatetime').toDateTime())
            createPersonId = forceRef(record.value('createPerson_id'))
            modifyDatetime = dateTimeToString(record.value('modifyDatetime').toDateTime())
            modifyPersonId = forceRef(record.value('modifyPerson_id'))
            clientId       = forceRef(record.value('client_id'))
            note           = forceString(record.value('note'))
            payStatus      = forceInt(record.value('payStatus'))
        else:
            createDatetime = ''
            createPersonId = None
            modifyDatetime = ''
            modifyPersonId = None
            clientId       = None
            note           = ''
            payStatus      = 0

        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.txtClientInfoBrowserActions.setHtml(getClientBanner(clientId))
        else:
            self.txtClientInfoBrowserActions.setText('')
        self.actActionEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

#        table = db.table('Action')
#        idList = db.getIdList(table, 'id', table['event_id'].eq(eventId), ['id'])
#        self.tblEventActions.setIdList(idList)


#        self.lblEventIdValue.setText(str(eventId) if eventId else '')
#        self.lblEventExternalIdValue.setText(externalId)
#        self.lblEventCreateDateTimeValue.setText(createDatetime)
#        self.lblEventCreatePersonValue.setText(self.getPersonText(createPersonId))
#        self.lblEventModifyDateTimeValue.setText(modifyDatetime)
#        self.lblEventModifyPersonValue.setText(self.getPersonText(modifyPersonId))
#        self.lblEventNoteValue.setText(note)
#        self.lblEventPayStatusValue.setText(payStatusText(payStatus))

    def updateTempInvalidList(self, filter, posToId=None):
        # в соответствии с фильтром обновляет список документов вр. нетрудоспособности.
        self.__expertFilter = filter
        db = QtGui.qApp.db
        if filter.get('linked', False):
            table = db.table('TempInvalid').alias('ti')
            mainTable = db.table('TempInvalid')
            queryTable = mainTable.join(table,
                                        db.joinAnd([mainTable['client_id'].eq(table['client_id']),
                                                    mainTable['caseBegDate'].eq(table['caseBegDate'])
                                                   ]))
        else:
            table = db.table('TempInvalid')
            mainTable = table
            queryTable = table

        tableDiagnosis = db.table('Diagnosis')
        queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(table['diagnosis_id']))
        tempInvalidType = self.tabWidgetTempInvalidTypes.currentIndex()
        cond = [ mainTable['deleted'].eq(0),
                 mainTable['type'].eq(tempInvalidType)
               ]
        self.addEqCond(cond, table, 'id', filter, 'id')
        self.addEqCond(cond, table, 'doctype_id', filter, 'docTypeId')
        self.addLikeCond(cond, table, 'serial', filter, 'serial')
        self.addLikeCond(cond, table, 'number', filter, 'number')
        self.addEqCond(cond, table, 'tempInvalidReason_id', filter, 'reasonId')
        self.addDateCond(cond, table, 'begDate', filter, 'begBegDate', 'endBegDate')
        self.addDateCond(cond, table, 'endDate', filter, 'begEndDate', 'endEndDate')
        self.addEqCond(cond, table, 'person_id', filter, 'personId')
        self.addRangeCond(cond, tableDiagnosis, 'MKB', filter, 'begMKB', 'endMKB')
        self.addEqCond(cond, table, 'closed', filter, 'closed')
        if 'begDuration' in filter:
            cond.append(table['duration'].ge(filter['begDuration']))
        if 'endDuration' in filter:
            endDuration = filter['endDuration']
            if endDuration:
                cond.append(table['duration'].le(endDuration))
        self.addEqCond(cond, table, 'insuranceOfficeMark', filter, 'insuranceOfficeMark')
        self.addEqCond(cond, table, 'createPerson_id', filter, 'createPersonId')
        self.addDateCond(cond, table, 'createDatetime', filter, 'begCreateDate', 'endCreateDate')
        self.addEqCond(cond, table, 'modifyPerson_id', filter, 'modifyPersonId')
        self.addDateCond(cond, table, 'modifyDatetime', filter, 'begModifyDate', 'endModifyDate')

        if 'clientIds' in filter:
            clientIds = filter['clientIds']
            cond.append(mainTable['client_id'].inlist(clientIds))

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            if table == mainTable:
                getIdList = db.getIdList
            else:
                getIdList = db.getDistinctIdList
            idList = getIdList(queryTable,
                           mainTable['id'].name(),
                           cond,
                           [mainTable['endDate'].name()+' DESC', mainTable['id'].name()])
            self.setExpertIdList(idList, posToId)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        expertFilterType = filter['expertFilterType']
        hideClientInfo = expertFilterType == 0 or expertFilterType == 1 and len(filter['clientIds']) == 1
        table = self.getCurrentExpertTable()
        for i in range(3):
            table.setColumnHidden(i, hideClientInfo)


    def updateTempInvalidInfo(self, tempInvalidId):
        db = QtGui.qApp.db
        tableTempInvalid = db.table('TempInvalid')
        record = db.getRecord(tableTempInvalid,
                              ['client_id'], tempInvalidId)
#                              ['createDatetime','createPerson_id', 'modifyDatetime', 'modifyPerson_id', 'client_id', 'notes'], tempInvalidId)
        if record:
#            createDatetime = dateTimeToString(record.value('createDatetime').toDateTime())
#            createPersonId = forceRef(record.value('createPerson_id'))
#            modifyDatetime = dateTimeToString(record.value('modifyDatetime').toDateTime())
#            modifyPersonId = forceRef(record.value('modifyPerson_id'))
            clientId       = forceRef(record.value('client_id'))
#            notes          = forceString(record.value('notes'))
        else:
#            createDatetime = ''
#            createPersonId = None
#            modifyDatetime = ''
#            modifyPersonId = None
            clientId       = None
#            notes          = ''
#            payStatus      = 0

        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.txtClientInfoBrowserExpert.setHtml(getClientBanner(clientId))
        else:
            self.txtClientInfoBrowserExpert.setText('')
        self.actExpertEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

        if tempInvalidId:
            table = db.table('TempInvalid_Period')
            idList = db.getIdList(table, 'id', table['master_id'].eq(tempInvalidId), ['id'])
        else:
            idList = []
        tblPeriods = self.getCurrentTempPeriodsTable()
        tblPeriods.setIdList(idList)

        if self.tabWidgetTempInvalidTypes.currentIndex() == 0:
            if tempInvalidId:
                table = db.table('TempInvalidDuplicate')
                idList = db.getIdList(
                    table,
                    'id',
                    [table['tempInvalid_id'].eq(tempInvalidId), table['deleted'].eq(0)],
                    ['id']
                )
            else:
                idList = []
            self.tblExpertTempInvalidDuplicates.setIdList(idList)


    def getExpertFilterAsText(self):
        db = QtGui.qApp.db
        filter  = self.__expertFilter
        resList = []

        expertFilterType = filter['expertFilterType']
        if expertFilterType in [0, 1]:
            clientIds = filter.get('clientIds', None)
            if clientIds and len(clientIds) == 1:
                resList.append((u'Пациент', getClientMiniInfo(clientIds[0])))
            elif clientIds and len(clientIds) > 1:
                resList.append((u'Список пациентов', u'из вкладки'))
        else:
            resList.append((u'Список пациентов', u'полный'))

        tmpList = [
            ('id',         u'Идентифиатор записи', lambda id: '%d'%id),
            ('docTypeId',  u'Тип документа',       lambda id: forceString(db.translate('rbTempInvalidDocument', 'id', id, 'name'))),
            ('serial',     u'Серия',               forceString),
            ('number',     u'Номер',               forceString),
            ('reasonId',   u'Причина нетрудоспособности', lambda id: forceString(db.translate('rbTempInvalidReason', 'id', id, 'name'))),
            ('begBegDate', u'Дата начала с',       forceString),
            ('endBegDate', u'Дата начала по',      forceString),
            ('begEndDate', u'Дата окончания с',    forceString),
            ('endEndDate', u'Дата окончания по',   forceString),
            ('personId',   u'Врач',                lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('begMKB',     u'Код МКБ с',           forceString),
            ('endMKB',     u'Код МКБ по',          forceString),
            ('closed',     u'состояние',           lambda closed: [u'открыт', u'закрыт', u'продлён', u'передан'][closed]),
            ('begDuration',u'длительность с',      lambda v: '%d'%v),
            ('endDuration',u'длительность по',     lambda v: '%d'%v),
            ('insuranceOfficeMark', u'отметка страхового стола', lambda i: [u'без отметки', u'с отметкой']),
            ('createPerson_id', u'Автор записи',   lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('begCreateDate', u'Дата создания с',  forceString),
            ('endCreateDate', u'Дата создания по', forceString),
            ('modifyPerson_id', u'Запись изменил', lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('begModifyDate', u'Дата изменения с', forceString),
            ('endModifyDate', u'Дата изменения по',forceString),
            ]
        for (x, y, z) in tmpList:
            convertFilterToTextItem(resList, filter, x, y, z)
        return '\n'.join([ ': '.join(item) for item in resList])


    def getCurrentExpertTable(self):
        index = self.tabWidgetTempInvalidTypes.currentIndex()
        return [self.tblExpertTempInvalid, self.tblExpertDisability, self.tblExpertVitalRestriction][index]


    def getCurrentTempPeriodsTable(self):
        index = self.tabWidgetTempInvalidTypes.currentIndex()
        return [self.tblExpertTempInvalidPeriods, self.tblExpertDisabilityPeriods, self.tblExpertVitalRestrictionPeriods][index]


    def currentTempInvalidId(self):
        return self.getCurrentExpertTable().currentItemId()


    def setExpertIdList(self, idList, posToId):
        self.getCurrentExpertTable().setIdList(idList, posToId)


    def focusExpert(self):
        self.getCurrentExpertTable().setFocus(QtCore.Qt.TabFocusReason)


    def editTempInvalid(self, tempInvalidId):
        widgetIndex = self.tabWidgetTempInvalidTypes.currentIndex()
        dialog = CTempInvalidEditDialog(self)
        dialog.setWindowTitle(self.tabWidgetTempInvalidTypes.tabText(widgetIndex))
        dialog.load(tempInvalidId)
        if dialog.exec_():
            tempInvalidNewId = dialog.itemId()
            self.updateTempInvalidList(self.__expertFilter, tempInvalidNewId if tempInvalidNewId else tempInvalidId)


    def editTempInvalidExpert(self):
        widgetIndex = self.tabWidgetTempInvalidTypes.currentIndex()
        clientId = self.currentClientId()
        if clientId:
            dialog = CTempInvalidCreateDialog(self, clientId)
            dialog.setType(widgetIndex)
            dialog.setWindowTitle(self.tabWidgetTempInvalidTypes.tabText(widgetIndex))
            if dialog.exec_():
                self.updateTempInvalidList(self.__expertFilter, dialog.itemId())


    def getExpertPrevDocId(self, table):
        tempInvalidId = table.currentItemId()
        if tempInvalidId:
            model = table.model()
            currentItem = model.recordCache().get(tempInvalidId)
            return forceRef(currentItem.value('prev_id'))
        return None


    def getExpertNextDocId(self, table):
        tempInvalidId = table.currentItemId()
        if tempInvalidId:
            return forceRef(QtGui.qApp.db.translate('TempInvalid', 'prev_id', tempInvalidId, 'id'))
        return None


    def enableCardReaderSupport(self):
        QtGui.qApp.startProgressBar(1, u'Поддержка соц. карт...')

        prefs = QtGui.qApp.preferences.appPrefs
        if forceBool(getVal(prefs, 'SocCard_Emulation',  False)):
            from Registry.CardReader import CCardReaderEmulator
            self.cardReader = CCardReaderEmulator()
        else:
            from Registry.CardReader import CCardReader
            self.cardReader = CCardReader()

        self.mapDocumentCodeToSocialCardCode = {}
        self.mapBenefitCodeToSocialCardCode = {}
        self.rbSocialCardDocumentType = None
        self.rbSocialCardBenefitType = None

        nPortNo = forceInt(getVal(prefs, 'SocCard_PortNumber', 0))
        diDevId = forceInt(getVal(prefs,  'SocCard_DevId',  0))
        listIssBSC = []

        for i in range(0, 6):
            listIssBSC.append(forceInt(getVal(prefs, 'SocCard_IssBSC%d' % i,  0)))

        szOperatorId = forceString(getVal(prefs,  'SocCard_OperatorId',  ''))

        if self.cardReader.init(nPortNo, diDevId, listIssBSC, szOperatorId):
            QtGui.qApp.stepProgressBar()
            self.actFilterSocCard =  QtGui.QAction(u'Социальная карта',  self)
            self.actFilterSocCard.setObjectName('actFilterSocCard')
            self.actFilter =  QtGui.QAction(u'Фильтр',  self)
            self.actFilter.setObjectName('actFilter')
            self.mnuFilter =  QtGui.QMenu(self)
            self.mnuFilter.setObjectName('mnuFilter')
            self.mnuFilter.addAction(self.actFilterSocCard)
            self.mnuFilter.addAction(self.actFilter)
            self.btnFilter.setMenu(self.mnuFilter)
            self.btnFilter.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT+QtCore.Qt.Key_F7))

            if forceBool(getVal(prefs,  'SocCard_SetAsDefaultSearch',  False)):
                self.actFilterSocCard.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F7))
                self.actFilter.setShortcut(QtGui.QKeySequence(QtCore.Qt.SHIFT+QtCore.Qt.Key_F7))
                self.mnuFilter.setDefaultAction(self.actFilterSocCard)
            else:
                self.actFilterSocCard.setShortcut(QtGui.QKeySequence(QtCore.Qt.SHIFT+QtCore.Qt.Key_F7))
                self.actFilter.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F7))
                self.mnuFilter.setDefaultAction(self.actFilter)

        else:
            rc = self.cardReader.rc()
            message = u'<h4>Ошибка инициализации считывателя карт.</h4>\n' \
                u'Проверьте правильность подключения устройства и его '\
                u'настроек в меню Настойки.Умолчания.<br><br>' \
                u'Параметры соединения:<table>' \
                u'<tr><td>Номер порта:</td><td><b>%d</b></td></tr>' \
                u'<tr><td>Идентификатор устройства:</td><td><b>%d</b></td></tr>'\
                u'<tr><td>Код банка:</td><td><b>%.2d%.2d%.2d%.2d%.2d%.2d</b></td></tr>' \
                u'<tr><td>Идентификатор оператора:</td><td><b>%s</b></td></tr>'\
                u'<tr><td>Ошибка:</td><td><b>%s (код %d)</b></td></tr></table>' % \
                (nPortNo, diDevId, listIssBSC[0], listIssBSC[1], listIssBSC[2], listIssBSC[3],
                listIssBSC[4], listIssBSC[5], szOperatorId,  self.cardReader.errorText(rc),  rc)

            QtGui.QMessageBox.critical(self, u'Внимание!',
                                    message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        QtGui.qApp.stopProgressBar()


    def findClientBySocCardInfo(self,  clientInfo):
        table = QtGui.qApp.db.table('Client')
        cond = []
        cond.append(table['deleted'].eq(0))

        for x in ('lastName', 'firstName', 'patrName',  'sex',  'birthDate'):
            if clientInfo.has_key(x):
                cond.append(table[x].eq(clientInfo[x]))

        QtGui.qApp.startProgressBar(2, u'Поиск пациента в БД...')
        record = QtGui.qApp.db.getRecordEx(table, 'id',  cond, 'id')
        QtGui.qApp.stepProgressBar()
        SNILS = clientInfo.get('SNILS')

        if not record and SNILS:
            record = QtGui.qApp.db.getRecordEx(table, 'id',  [table['deleted'].eq(0),
                                                      table['SNILS'].eq(SNILS),
                                                     ], 'id')
            QtGui.qApp.stepProgressBar()

        return record


    def processSocCard(self):
        if self.cardReader.checkCardType():
            QtGui.qApp.stepProgressBar()
            clientInfo = self.cardReader.socialInfo()
            QtGui.qApp.stepProgressBar()
            benefitInfo = self.cardReader.benefitInfo()
            QtGui.qApp.stepProgressBar()
            vitalInfo = self.cardReader.vitalInfo()
            QtGui.qApp.stepProgressBar()
            record = self.findClientBySocCardInfo(clientInfo) if clientInfo else None

            if record:
                return self.findClient(forceRef(record.value(0)),  record)
            elif clientInfo:
                message = u'Пациент: %s %s %s, пол: %s, дата рождения:' \
                    u' %s, СНИЛС: %s, не найден в БД. Добавить новую '\
                    u'регистрационную карту?' % (clientInfo.get('lastName', ''),
                    clientInfo.get('firstName', ''), clientInfo.get('patrName', ''),
                    formatSex(clientInfo.get('sex', 0)),
                    clientInfo.get('birthDate', QtCore.QDate()).toString('dd.MM.yyyy'),
                    formatSNILS(clientInfo.get('SNILS')))

                if QtGui.QMessageBox.question(self,
                        u'Добавление нового пациента', message,
                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                        QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    self.createNewClientDialogWithInfoFromSocCard(clientInfo,  benefitInfo,  vitalInfo)
            else:
                message = u'Социальная карта не содержит информации о паиценте'
                QtGui.QMessageBox.critical(self, u'Поиск пациента', message,
                        QtGui.QMessageBox.Ok,  QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.warning(self, u'Внимание!',
                u'Социальная карта не вставлена в считыватель,'\
                u' или имеет неверный формат.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)


    def createNewClientDialogWithInfoFromSocCard(self,  socialInfo,  benefitInfo,  vitalInfo):
        dialog = CClientEditDialog(self)
        self.loadSocialInfo(dialog, socialInfo)
        self.loadBenefitInfo(dialog, benefitInfo)
        self.loadVitalInfo(dialog, vitalInfo)
        if dialog.exec_() :
            clientId = dialog.itemId()
            clientRecord = dialog.getRecord()
            self.findClient(clientId, clientRecord)


    def loadSocialInfo(self, dialog, socialInfo):
        dialog.edtFirstName.setText(socialInfo.get('firstName', ''))
        dialog.edtLastName.setText(socialInfo.get('lastName', ''))
        dialog.edtPatrName.setText(socialInfo.get('patrName', ''))
        dialog.edtBirthDate.setDate(socialInfo.get('birthDate', QtCore.QDate()))
        dialog.cmbSex.setCurrentIndex(socialInfo.get('sex', 0))
        dialog.edtSNILS.setText(socialInfo.get('SNILS', ''))
        serial = socialInfo.get('docSerial')
        for c in '-=/_|':
            serial = serial.replace('c',' ')
        serial = forceStringEx(serial).split()
        serialLeft = serial[0] if len(serial)>=1 else ''
        serialRight = serial[1] if len(serial)>=2 else ''
        dialog.edtDocSerialLeft.setText(serialLeft)
        dialog.edtDocSerialRight.setText(serialRight)
        dialog.edtDocNumber.setText(socialInfo.get('docNumber'))
        docTypeId = self.getSocialCardDocumentTypeId(socialInfo.get('docType'))
        if docTypeId:
            dialog.cmbDocType.setValue(docTypeId)
        notes = u'Социальная карта: серия %s, номер %s. Идентификационный '\
            u'номер социального регистра %s.' % (socialInfo.get('cardNumber','-'),
                socialInfo.get('cardSerial',  '-'),  socialInfo.get('numberSocial','-'))
        dialog.edtNotes.setText(notes)
        dialog.edtCompulsoryPolisSerial.setText(socialInfo.get('policySerial', ''))
        dialog.edtCompulsoryPolisNumber.setText(socialInfo.get('policyNumber', ''))
        notes = socialInfo.get('orgCode',  '')
        policyDate = socialInfo.get('policyDate', None)
        if policyDate:
            notes += u' Дата действия полиса %s.' % policyDate
        dialog.edtCompulsoryPolisNote.setText(notes)


    def getSocialCardDocumentTypeId(self,  code):
        id = self.lookupDocumentTypeId(code)

        if not id:
            if self.rbSocialCardDocumentType == None:
                fileName = forceString(getVal(QtGui.qApp.preferences.appPrefs,
                    'SocCard_rbDocumentTypeRbFileName', ''))
                from Registry.CardReader import loadDocumentTypeRb
                self.rbSocialCardDocumentType = loadDocumentTypeRb(self,  fileName)

            name = self.rbSocialCardDocumentType.get(code)

            if name:
                from Registry.CardReader import askUserForDocumentTypeId
                id = askUserForDocumentTypeId(self,  code, name)
            else:
                message = u'Неизвестный код типа документа "%s".' % code
                QtGui.QMessageBox.critical(self, u'Импорт документа с социальной карты',
                        message,  QtGui.QMessageBox.Ok,  QtGui.QMessageBox.Ok)

        return id


    def loadBenefitInfo(self,  dialog,  benefitInfo):
        if benefitInfo != []:

            for (code,  begDate,  endDate) in benefitInfo:
                id = self.lookupBenefitId(code)
                if not id:
                    if self.rbSocialCardBenefitType == None:
                        fileName = forceString(getVal(QtGui.qApp.preferences.appPrefs,
                            'SocCard_rbClientBenefitRbFileName', ''))
                        from Registry.CardReader import loadBenefitTypeRb
                        self.rbSocialCardBenefitType = loadBenefitTypeRb(self,  fileName)

                    name = self.rbSocialCardBenefitType.get(code)

                    if name:
                        from Registry.CardReader import askUserForBenefitId
                        id = askUserForBenefitId(self,  code,  name)

                if id:
                    self.addBenefit(dialog, id,  begDate,  endDate)
                else:
                    message = u'Неизвестный код льготы "%s".' % code
                    QtGui.QMessageBox.critical(self, u'Импорт льгот с социальной карты',
                        message,  QtGui.QMessageBox.Ok,  QtGui.QMessageBox.Ok)


    def addBenefit(self, dialog,  id,  begDate,  endDate):
        record = dialog.modelSocStatuses.getEmptyRecord()
        record.setValue('socStatusType_id', toVariant(id))
        record.setValue('begDate',  toVariant(begDate))
        record.setValue('endDate', toVariant(endDate))
        dialog.modelSocStatuses.insertRecord(0, record)


    def loadVitalInfo(self,  dialog,  vitalInfo):
        if vitalInfo != 0:
            (allergy,  intolerance,  notes) = self.cardReader.decodeVitalInfo(vitalInfo)

            for x in allergy:
                record = dialog.modelAllergy.getEmptyRecord()
                record.setValue('nameSubstance', toVariant(x))
                record.setValue('createDate',  toVariant(QtCore.QDate.currentDate()))
                dialog.modelAllergy.insertRecord(0, record)

            for x in intolerance:
                record = dialog.modelIntoleranceMedicament.getEmptyRecord()
                record.setValue('nameMedicament', toVariant(x))
                record.setValue('createDate',  toVariant(QtCore.QDate.currentDate()))
                dialog.modelIntoleranceMedicament.insertRecord(0, record)

            if notes != []:
                strNotes = forceString(dialog.edtNotes.toPlainText()) + \
                    u' '+ u', '.join([str(et) for et in notes])
                dialog.edtNotes.setText(strNotes)


    def lookupBenefitId(self,  code):
        id = self.mapBenefitCodeToSocialCardCode.get(code)

        if not id:
            db = QtGui.qApp.db
            table = db.table('rbSocStatusType')
            record = db.getRecordEx(table, 'id',
                                [table['socCode'].eq(code)], 'id')

            if record:
                id = forceInt(record.value(0))
                self.mapBenefitCodeToSocialCardCode[code] = id

        return id


    def lookupDocumentTypeId(self,  code):
        id = self.mapDocumentCodeToSocialCardCode.get(code)

        if not id:
            db = QtGui.qApp.db
            table = db.table('rbDocumentType')
            record = db.getRecordEx(table, 'id',
                                [table['socCode'].eq(code)], 'id')

            if record:
                id = forceInt(record.value(0))
                self.mapDocumentCodeToSocialCardCode[code] = id

        return id

    #########################################################################


    @QtCore.pyqtSlot(int)
    def on_tabMain_currentChanged(self, index):
        keyboardModifiers = QtGui.qApp.keyboardModifiers()
        if index == 0: # реестр
            self.syncSplitters(self.splitterRegistry)
#            self.focusClients()
            if self.tabMainCurrentPage == 1:
                if keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                    db = QtGui.qApp.db
                    eventId = self.currentEventId()
                    clientId = forceRef(db.translate('Event', 'id', eventId, 'client_id'))
                    self.tblClients.setCurrentItemId(clientId)
                if self.updateClientsListRequest:
                    self.updateClientsList(self.__filter)
            self.currentClientFromEvent = False
            self.currentClientFromAction = False
            self.currentClientFromExpert = False
        elif index == 1: # осмотры
            self.syncSplitters(self.splitterEvents)
            if keyboardModifiers & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier:
                clientsFilterType = 2
            elif keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                clientsFilterType = 1
            elif keyboardModifiers & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier:
                clientsFilterType = -1
            else:
                clientsFilterType = 0
            if clientsFilterType == 0 and self.currentClientFromEvent and not self.currentClientFromAction and not self.currentClientFromExpert:
                # возврат из мед. карты или подобного, на одного пациента
                self.updateEventInfo(self.currentEventId())
            else:
                self.updateEventInfo(None)
                if clientsFilterType != -1:
                    self.on_buttonBoxEvent_reset()
                    self.cmbFilterEventByClient.setCurrentIndex(clientsFilterType)
                self.on_buttonBoxEvent_apply()
            self.currentClientFromEvent = True
            self.currentClientFromAction = False
            self.currentClientFromExpert = False
        elif index == 2: # мед.карта
            self.syncSplitters(self.splitterAmbCard)
            self.updateAmbCardInfo()
            self.on_cmdAmbCardDiagnosticsButtonBox_reset()
            self.on_cmdAmbCardStatusButtonBox_reset()
            self.on_cmdAmbCardDiagnosticButtonBox_reset()
            self.on_cmdAmbCardCureButtonBox_reset()
            self.on_cmdAmbCardMiscButtonBox_reset()

            self.on_cmdAmbCardDiagnosticsButtonBox_apply()
            self.on_cmdAmbCardStatusButtonBox_apply()
            self.on_cmdAmbCardDiagnosticButtonBox_apply()
            self.on_cmdAmbCardCureButtonBox_apply()
            self.on_cmdAmbCardMiscButtonBox_apply()
        elif index == 3: # Обслуживание
            self.syncSplitters(self.splitterActions)
            self.updateActionInfo(None)
            if self.currentClientFromEvent: # переход сквозь осмотры
                cmbFilterActionFlags = QtCore.QVariant(int(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable))
                cmbFilterActionDefault = 2
            else:
                cmbFilterActionFlags = QtCore.QVariant(0)
                cmbFilterActionDefault = 0
            self.cmbFilterAction.setItemData(2, cmbFilterActionFlags, QtCore.Qt.UserRole-1)
            self.cmbFilterAction.setItemData(3, cmbFilterActionFlags, QtCore.Qt.UserRole-1)

            if keyboardModifiers & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier:
                clientsFilterType = 5
            elif keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                clientsFilterType = cmbFilterActionDefault+1
            elif keyboardModifiers & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier:
                clientsFilterType = -1
            else:
                clientsFilterType = cmbFilterActionDefault
            if clientsFilterType != -1:
                self.on_buttonBoxAction_reset()
                self.cmbFilterAction.setCurrentIndex(clientsFilterType)
            self.on_buttonBoxAction_apply()
            self.currentClientFromEvent = False
            self.currentClientFromAction = True
            self.currentClientFromExpert = False
        elif index == 4: # КЭР
            self.syncSplitters(self.splitterExpert)
            self.updateTempInvalidInfo(None)
            if keyboardModifiers & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier:
                clientsFilterType = 2
            elif keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                clientsFilterType = 1
            elif keyboardModifiers & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier:
                clientsFilterType = -1
            else:
                clientsFilterType = 0
            if clientsFilterType != -1:
                self.on_buttonBoxExpert_reset()
                self.cmbFilterExpert.setCurrentIndex(clientsFilterType)
            self.on_tabWidgetTempInvalidTypes_currentChanged(self.tabWidgetTempInvalidTypes.currentIndex())
#            self.on_buttonBoxExpert_apply()
            self.currentClientFromEvent = False
            self.currentClientFromAction = False
            self.currentClientFromExpert = True
        self.tabMainCurrentPage = index


    def getFilterInfoBed(self):
        def getNameOrgStructure(orgStructureId):
            db = QtGui.qApp.db
            if orgStructureId:
                tableOS = db.table('OrgStructure')
                record = db.getRecordEx(tableOS, [tableOS['name']], [tableOS['deleted'].eq(0), tableOS['id'].eq(orgStructureId)])
                if record:
                    nameOrgStructure = forceString(record.value(0))
                else:
                    nameOrgStructure = forceString(None)
            else:
                tableO = db.table('Organisation')
                recordOrg = db.getRecordEx(tableO, [tableO['shortName']], [tableO['deleted'].eq(0), tableO['id'].eq(QtGui.qApp.currentOrgId())])
                if recordOrg:
                    nameOrgStructure = forceString(recordOrg.value(0))
                else:
                    nameOrgStructure = forceString(None)
            return nameOrgStructure
        infoBeds = u''
        if self.chkFilterBeds.isChecked():
            statusBeds = self.cmbFilterStatusBeds.currentText()
            orgStructureId = self.cmbFilterOrgStructureBeds.value()
            infoBeds = u'; по койкам: статус %s подразделение %s'%(statusBeds, getNameOrgStructure(orgStructureId))
        infoAddressOrgStructure = u''
        if self.chkFilterAddressOrgStructure.isChecked():
            orgStructureType = self.cmbFilterAddressOrgStructureType.currentText()
            orgStructureId = self.cmbFilterAddressOrgStructure.value()
            infoAddressOrgStructure = u'; по участкам: тип %s подразделение %s'%(orgStructureType, getNameOrgStructure(orgStructureId))
        return [infoBeds, infoAddressOrgStructure]


    @QtCore.pyqtSlot(int)
    def on_modelClients_itemsCountChanged(self, count):
        realItemCount = self.sender().getRealItemCount()
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblClientsCount.setText(formatRecordsCount2(count, realItemCount)+infoBeds+infoAddressOrgStructure)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelClients_currentRowChanged(self, current, previous):
        clientId = self.clientId(current)
        self.showClientInfo(clientId)
        self.tabMain.setTabEnabled(1, current.isValid())
        self.updateQueue()


    def updateQueue(self):
        clientId = self.currentClientId()
        self.modelQueue.loadData(clientId)
        self.modelVisitByQueue.loadData(clientId)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblClients_doubleClicked(self, index):
        self.editCurrentClient()
        self.focusClients()


    def showQueuePosition(self, actionId, VisitBefore = False):
        if actionId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tablePerson = db.table('Person')
            cols = [tableAction['directionDate'],
                    tableAction['person_id'],
                    tablePerson['orgStructure_id'],
                    tablePerson['speciality_id']]
            cond = [tableAction['id'].eq(actionId),
                    tableAction['deleted'].eq(0),
                    tablePerson['deleted'].eq(0)]
            table = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
            record = db.getRecordEx(table, cols, cond)
            if record:
                date = forceDate(record.value('directionDate'))
                personId = forceRef(record.value('person_id'))
                orgStructureId = forceRef(record.value('orgStructure_id'))
                specialityId = forceRef(record.value('speciality_id'))
                try:
                    if QtGui.qApp.mainWindow.dockResources and personId and date and orgStructureId and specialityId and actionId:
                        QtGui.qApp.mainWindow.dockResources.content.showQueueItem(orgStructureId, specialityId, personId, date, actionId)
                except:
                    pass


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblQueue_doubleClicked(self, index):
        if QtGui.qApp.doubleClickQueueClient() == 1:
            self.on_actAmbCreateEvent_triggered()
        elif QtGui.qApp.doubleClickQueueClient() == 2:
                self.on_actAmbChangeNotes_triggered()
        elif QtGui.qApp.doubleClickQueueClient() == 3:
               self.on_actAmbPrintOrder_triggered()
        elif QtGui.qApp.doubleClickQueueClient() == 4:
                self.on_actJumpQueuePosition_triggered()


    @QtCore.pyqtSlot()
    def on_actJumpQueuePosition_triggered(self):
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            actionId = self.modelQueue.items[row][6]
            if actionId:
                QtGui.qApp.callWithWaitCursor(self, self.showQueuePosition, actionId)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblVisitByQueue_doubleClicked(self, index):
        index = self.tblVisitByQueue.currentIndex()
        if index.isValid():
            row = index.row()
            if self.modelVisitByQueue.items[row][0]:
                eventId = self.modelVisitByQueue.items[row][7]
                if eventId:
                    editEvent(self, eventId)
                    self.focusEvents()


    @QtCore.pyqtSlot()
    def on_actEditClient_triggered(self):
        self.editCurrentClient()
        self.focusClients()


    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        self.editCurrentClient()
        self.focusClients()


    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        self.editNewClient()
        self.focusClients()


    @QtCore.pyqtSlot()
    def on_mnuPrint_aboutToShow(self):
        clientId = self.selectedClientId()
        if clientId:
            self.mnuPrint.setDefaultAction(self.actPrintClient)
            self.actPrintClient.setEnabled(True)
            printer = QtGui.qApp.labelPrinter()
            self.actPrintClientLabel.setEnabled(self.clientLabelTemplate is not None and bool(printer))
        else:
            self.actPrintClient.setEnabled(False)
            self.actPrintClientLabel.setEnabled(False)


    @QtCore.pyqtSlot(int)
    def on_actPrintClient_printByTemplate(self, templateId):
        from Events.TempInvalidInfo import CTempInvalidInfoList
        clientId = self.selectedClientId()
        if clientId:
            clientInfo = getClientInfo2(clientId)
            getTempInvalidList = lambda begDate=None, endDate=None, types=None: CTempInvalidInfoList._get(clientInfo.context, clientId, begDate, endDate, types)
            data = {'client':clientInfo,
                    'getTempInvalidList': getTempInvalidList,
                    'tempInvalids':getTempInvalidList()}
            QtGui.qApp.call(self, applyTemplate, (self, templateId, data))


    @QtCore.pyqtSlot()
    def on_actPrintClientLabel_triggered(self):
        clientId = self.selectedClientId()
        printer = QtGui.qApp.labelPrinter()
        if clientId and self.clientLabelTemplate and printer:
            clientInfo = getClientInfo2(clientId)
            QtGui.qApp.call(self, directPrintTemplate, (self.clientLabelTemplate[1], {'client':clientInfo}, printer))


    @QtCore.pyqtSlot()
    def on_actPrintClientList_triggered(self):
        self.tblClients.setReportHeader(u'Список пациентов')
        self.tblClients.setReportDescription(self.getClientFilterAsText())
        dataRoles = [QtCore.Qt.DisplayRole]*(self.modelClients.columnCount())
        self.tblClients.printContent(dataRoles)
        self.focusClients()


    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        pass
#        self.tblClients.setReportHeader(u'Список пациентов')
#        self.tblClients.setReportDescription(self.getClientFilterAsText())
#        self.tblClients.printContent()
#        self.focusClients()


    @QtCore.pyqtSlot()
    def on_actFilterSocCard_triggered(self):
        QtGui.qApp.startProgressBar(4, u'Чтение карты...')
        self.processSocCard()
        QtGui.qApp.stopProgressBar()


    @QtCore.pyqtSlot()
    def on_actFilter_triggered(self):
        self.on_btnFilter_clicked()


    @QtCore.pyqtSlot()
    def on_btnFilter_clicked(self):
        for s in self.chkListOnClientsPage:
            chk = s[0]
            if chk.isChecked():
                self.activateFilterWdgets(s[1])
                return
        dfltChk = self.chkFilterBirthDay
        self.setChkFilterChecked(dfltChk, True)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterId_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if self.chkFilterLastName.isChecked():
            self.setChkFilterChecked(self.chkFilterLastName, False)
        if self.chkFilterFirstName.isChecked():
            self.setChkFilterChecked(self.chkFilterFirstName, False)
        if self.chkFilterPatrName.isChecked():
            self.setChkFilterChecked(self.chkFilterPatrName, False)
        if self.chkFilterBirthDay.isChecked():
            self.setChkFilterChecked(self.chkFilterBirthDay, False)
        if self.chkFilterSex.isChecked():
            self.setChkFilterChecked(self.chkFilterSex, False)
        if self.chkFilterContact.isChecked():
            self.setChkFilterChecked(self.chkFilterContact, False)
        if self.chkFilterSNILS.isChecked():
            self.setChkFilterChecked(self.chkFilterSNILS, False)
        if self.chkFilterDocument.isChecked():
            self.setChkFilterChecked(self.chkFilterDocument, False)
        if self.chkFilterPolicy.isChecked():
            self.setChkFilterChecked(self.chkFilterPolicy, False)
        if self.chkFilterAddress.isChecked():
            self.setChkFilterChecked(self.chkFilterAddress, False)
        if self.chkFilterWorkOrganisation.isChecked():
            self.setChkFilterChecked(self.chkFilterWorkOrganisation, False)
        if self.chkFilterCreatePerson.isChecked():
            self.setChkFilterChecked(self.chkFilterCreatePerson, False)
        if self.chkFilterCreateDate.isChecked():
            self.setChkFilterChecked(self.chkFilterCreateDate, False)
        if self.chkFilterModifyPerson.isChecked():
            self.setChkFilterChecked(self.chkFilterModifyPerson, False)
        if self.chkFilterModifyDate.isChecked():
            self.setChkFilterChecked(self.chkFilterModifyDate, False)
        if self.chkFilterAge.isChecked():
            self.setChkFilterChecked(self.chkFilterAge, False)
        if self.chkFilterAddressOrgStructure.isChecked():
            self.setChkFilterChecked(self.chkFilterAddressOrgStructure, False)
        if self.chkFilterBeds.isChecked():
            self.setChkFilterChecked(self.chkFilterBeds, False)
        if self.chkFilterAddressIsEmpty.isChecked():
            self.setChkFilterChecked(self.chkFilterAddressIsEmpty, False)
        if self.chkFilterAttach.isChecked():
            self.setChkFilterChecked(self.chkFilterAttach, False)
        if self.chkFilterAttachType.isChecked():
            self.setChkFilterChecked(self.chkFilterAttach, False)
        if self.chkFilterAttachNonBase.isChecked():
            self.setChkFilterChecked(self.chkFilterAttachNonBase, False)
        if self.chkFilterTempInvalid.isChecked():
            self.setChkFilterChecked(self.chkFilterTempInvalid, False)
        if self.chkFilterRPFUnconfirmed.isChecked():
            self.setChkFilterChecked(self.chkFilterRPFUnconfirmed, False)
        if self.chkFilterRPFConfirmed.isChecked():
            self.setChkFilterChecked(self.chkFilterRPFConfirmed, False)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterAccountingSystem_currentIndexChanged(self, index):
        self.edtFilterId.setValidator(None)
        if self.cmbFilterAccountingSystem.value():
            self.edtFilterId.setValidator(None)
        else:
            self.edtFilterId.setValidator(self.idValidator)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterLastName_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterFirstName_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterPatrName_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterBirthDay_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAge, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterSex_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterContact_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterSNILS_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterDocument_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterPolicy_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFilterPolicySerial_textEdited(self, text):
        self.cmbFilterPolicyInsurer.setSerialFilter(text)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterWorkOrganisation_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterCreatePerson_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterCreateDate_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterModifyPerson_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterModifyDate_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAge_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterBirthDay, False)


    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAddress_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAddressOrgStructure, False)
            self.setChkFilterChecked(self.chkFilterAddressIsEmpty, False)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterAddressCity_currentIndexChanged(self, index):
        code = self.cmbFilterAddressCity.code()
        self.cmbFilterAddressStreet.setCity(code)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAddressOrgStructure_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAddress, False)
            self.setChkFilterChecked(self.chkFilterAddressIsEmpty, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterBeds_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAddressIsEmpty_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAddress, False)
            self.setChkFilterChecked(self.chkFilterAddressOrgStructure, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAttach_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAttachNonBase, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAttachType_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAttachNonBase_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAttach, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterTempInvalid_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterRPFUnconfirmed_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterRPFConfirmed, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterRPFConfirmed_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterRPFUnconfirmed, False)


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()


#    @pyqtSlot()
    def on_buttonBox_apply(self):
        filter = {}
        if self.chkFilterId.isChecked():
            accountingSystemId = self.cmbFilterAccountingSystem.value()
            clientId = forceStringEx(self.edtFilterId.text())
            if not accountingSystemId:
                clientId = parseClientId(clientId)
            if clientId:
                filter['id'] = clientId
                filter['accountingSystemId'] = accountingSystemId

        if self.chkFilterLastName.isChecked():
            tmp = forceStringEx(self.edtFilterLastName.text())
            if tmp:
                filter['lastName'] = tmp
        if self.chkFilterFirstName.isChecked():
            tmp = forceStringEx(self.edtFilterFirstName.text())
            if tmp:
                filter['firstName'] = tmp
        if self.chkFilterPatrName.isChecked():
            tmp = forceStringEx(self.edtFilterPatrName.text())
            if tmp:
                filter['patrName'] = tmp
        if self.chkFilterBirthDay.isChecked():
            filter['birthDate'] = self.edtFilterBirthDay.date()
        if self.chkFilterSex.isChecked():
            filter['sex'] = self.cmbFilterSex.currentIndex()
        if self.chkFilterContact.isChecked():
            contact = forceStringEx(self.edtFilterContact.text())
            if contact:
                filter['contact'] = contact
        if self.chkFilterSNILS.isChecked():
            tmp = forceStringEx(forceString(self.edtFilterSNILS.text()).replace('-','').replace(' ',''))
            filter['SNILS'] = tmp
        if self.chkFilterDocument.isChecked():
            typeId = self.cmbFilterDocumentType.value()
            serial = forceStringEx(self.edtFilterDocumentSerial.text())
            number = forceStringEx(self.edtFilterDocumentNumber.text())
            filter['doc'] = (typeId, serial, number)
        if self.chkFilterPolicy.isChecked():
            policyType = self.cmbFilterPolicyType.value()
            insurerId = self.cmbFilterPolicyInsurer.value()
            serial = forceStringEx(self.edtFilterPolicySerial.text())
            number = forceStringEx(self.edtFilterPolicyNumber.text())
            filter['policy'] = (policyType, insurerId, serial, number)
        if self.chkFilterWorkOrganisation.isChecked():
            filter['orgId'] = self.cmbWorkOrganisation.value()
        if self.chkFilterCreatePerson.isChecked():
            filter['createPersonIdEx'] = self.cmbFilterCreatePerson.value()
        if self.chkFilterCreateDate.isChecked():
            filter['begCreateDateEx'] = self.edtFilterBegCreateDate.date()
            filter['endCreateDateEx'] = self.edtFilterEndCreateDate.date()
        if self.chkFilterModifyPerson.isChecked():
            filter['modifyPersonIdEx'] = self.cmbFilterModifyPerson.value()
        if self.chkFilterModifyDate.isChecked():
            filter['begModifyDateEx'] = self.edtFilterBegModifyDate.date()
            filter['endModifyDateEx'] = self.edtFilterEndModifyDate.date()
        if self.chkFilterAge.isChecked():
            filter['age'] = ((self.edtFilterBegAge.value(), self.cmbFilterBegAge.currentIndex()),
                             (self.edtFilterEndAge.value()+1, self.cmbFilterEndAge.currentIndex())
                            )
        if self.chkFilterAddress.isChecked():
            filter['address'] = (self.cmbFilterAddressType.currentIndex(),
                                 self.cmbFilterAddressCity.code(),
                                 self.cmbFilterAddressStreet.code(),
                                 self.edtFilterAddressHouse.text(),
                                 self.edtFilterAddressCorpus.text(),
                                 self.edtFilterAddressFlat.text()
                                )
        elif self.chkFilterAddressOrgStructure.isChecked():
            filter['addressOrgStructure'] = (self.cmbFilterAddressOrgStructureType.currentIndex(),
                                             self.cmbFilterAddressOrgStructure.value()
                                            )
        elif self.chkFilterAddressIsEmpty.isChecked():
            filter['addressIsEmpty'] = True
        if self.chkFilterBeds.isChecked():
            filter['beds'] = (self.cmbFilterStatusBeds.currentIndex(),
                              self.cmbFilterOrgStructureBeds.value()
                              )
        if self.chkFilterAttach.isChecked():
            filter['attachTo'] = self.cmbFilterAttachOrganisation.value()
        elif self.chkFilterAttachNonBase.isChecked():
            filter['attachToNonBase'] = True
        if self.chkFilterAttachType.isChecked():
            filter['attachType'] = (self.cmbFilterAttachType.itemData(
                                        self.cmbFilterAttachType.currentIndex()),
                                    forceString(self.cmbFilterAttachTypeProperty.itemData(
                                        self.cmbFilterAttachTypeProperty.currentIndex())))
        if self.chkFilterTempInvalid.isChecked():
            filter['tempInvalid'] = (self.edtFilterBegTempInvalid.date(),
                                     self.edtFilterEndTempInvalid.date()
                                    )
        if self.chkFilterRPFUnconfirmed.isChecked():
            filter['RPFUnconfirmed'] = True
        elif self.chkFilterRPFConfirmed.isChecked():
            filter['RPFConfirmed'] = (self.edtFilterBegRPFConfirmed.date(),
                                      self.edtFilterEndRPFConfirmed.date()
                                     )
        self.updateClientsList(filter)
        self.focusClients()

    @QtCore.pyqtSlot(int)
    def on_cmbFilterAttachTypeProperty_currentIndexChanged(self, index):
        self.fillCmbFilterAttachType(index)

#    @pyqtSlot()
    def on_buttonBox_reset(self):
        for s in self.chkListOnClientsPage:
            chk = s[0]
            if chk.isChecked():
                self.deactivateFilterWdgets(s[1])
                chk.setChecked(False)

#### Events page #################################

    @QtCore.pyqtSlot()
    def on_actEventEditClient_triggered(self):
        db = QtGui.qApp.db
        eventId = self.currentEventId()
#        clientId = forceRef(db.translate('Event', 'id', eventId, 'client_id'))
        clientId = self.currentClientId()
        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.editClient(clientId)
            self.updateEventInfo(self.currentEventId())
            self.updateClientsListRequest = True


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelEvents_currentRowChanged(self, current, previous):
        eventId = self.eventId(current)
        self.updateEventInfo(eventId)


    @QtCore.pyqtSlot(int)
    def on_modelEvents_itemsCountChanged(self, count):
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblEventsCount.setText(formatRecordsCount(count)+infoBeds+infoAddressOrgStructure)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblEvents_doubleClicked(self, index):
        self.on_btnEventEdit_clicked()


    @QtCore.pyqtSlot()
    def on_btnEventEdit_clicked(self):
        eventId = self.currentEventId()
        if eventId:
            editEvent(self, eventId)
        else:
            self.requestNewEvent()
        self.focusEvents()


    @QtCore.pyqtSlot()
    def on_btnEventNew_clicked(self):
        self.requestNewEvent()
        self.focusEvents()


    @QtCore.pyqtSlot()
    def on_btnEventPrint_clicked(self):
        self.tblEvents.setReportHeader(u'Список обращений')
        self.tblEvents.setReportDescription(self.getEventFilterAsText())
#        if self.cmbFilterEventByClient.currentIndex() == 0:
#            dataRoles = [None]*3 + [Qt.DisplayRole]*(self.modelEvents.columnCount()-3)
#        else:
#            dataRoles = [Qt.DisplayRole]*(self.modelEvents.columnCount())
#        self.tblEvents.printContent(dataRoles)
        self.tblEvents.printContent()
        self.focusEvents()





    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventSetDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventNextDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventEmptyExecDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        if checked:
            self.setChkFilterChecked(self.chkFilterEventExecDate, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventExecDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterEventEmptyExecDate, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventPurpose_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.updateFilterEventResultTable()
            self.setCmbFilterEventTypeFilter(self.cmbFilterEventPurpose.value())
        else:
            self.setCmbFilterEventTypeFilter(None)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventPurpose_currentIndexChanged(self, index):
        self.setCmbFilterEventTypeFilter(self.cmbFilterEventPurpose.value())
        self.updateFilterEventResultTable()


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventType_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.updateFilterEventResultTable()


    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventType_currentIndexChanged(self, index):
        self.updateFilterEventResultTable()


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventSpeciality_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterEventPerson.setSpecialityId(self.cmbFilterEventSpeciality.value())
        else:
            self.cmbFilterEventPerson.setSpecialityId(None)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventOrgStructure_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterEventPerson.setOrgStructureId(self.cmbFilterEventOrgStructure.value())
        else:
            self.cmbFilterEventPerson.setOrgStructureId(None)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventSpeciality_currentIndexChanged(self, index):
        self.cmbFilterEventPerson.setSpecialityId(self.cmbFilterEventSpeciality.value())


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventPerson_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkRelegateOrg_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventDispanserObserved_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventLPU_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            db = QtGui.qApp.db
            orgId = forceRef(db.translate('Event', 'id', self.currentEventId(), 'org_id'))
            self.cmbFilterEventLPU.setValue(orgId)
            self.cmbFilterEventPerson.setOrgId(orgId)
            self.setChkFilterChecked(self.chkFilterEventNonBase, False)
        else:
            self.cmbFilterEventLPU.setValue(None)
            self.cmbFilterEventPerson.setOrgId(None)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventLPU_currentIndexChanged(self, index):
        self.cmbFilterEventPerson.setOrgId(self.cmbFilterEventLPU.value())


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventNonBase_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        if checked:
            self.setChkFilterChecked(self.chkFilterEventLPU, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventMes_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventResult_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.updateFilterEventResultTable()


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventCreatePerson_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventCreateDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventModifyPerson_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventModifyDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventPayStatus_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkErrorInDiagnostic_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventId_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if self.chkFilterEventCreatePerson.isChecked():
            self.setChkFilterChecked(self.chkFilterEventCreatePerson, False)
        if self.chkFilterEventCreateDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventCreateDate, False)
        if self.chkFilterEventModifyPerson.isChecked():
            self.setChkFilterChecked(self.chkFilterEventModifyPerson, False)
        if self.chkFilterEventModifyDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventModifyDate, False)
        if self.chkErrorInDiagnostic.isChecked():
            self.setChkFilterChecked(self.chkErrorInDiagnostic, False)
        if self.chkFilterEventPayStatus.isChecked():
            self.setChkFilterChecked(self.chkFilterEventPayStatus, False)
        if self.chkFilterEventSetDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventSetDate, False)
        if self.chkFilterEventEmptyExecDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventEmptyExecDate, False)
        if self.chkFilterEventExecDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventExecDate, False)
        if self.chkFilterEventNextDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventNextDate, False)
        if self.chkFilterEventOrgStructure.isChecked():
            self.setChkFilterChecked(self.chkFilterEventOrgStructure, False)
        if self.chkFilterEventSpeciality.isChecked():
            self.setChkFilterChecked(self.chkFilterEventSpeciality, False)
        if self.chkFilterEventPerson.isChecked():
            self.setChkFilterChecked(self.chkFilterEventPerson, False)
        if self.chkRelegateOrg.isChecked():
            self.setChkFilterChecked(self.chkRelegateOrg, False)
        if self.chkFilterEventDispanserObserved.isChecked():
            self.setChkFilterChecked(self.chkFilterEventDispanserObserved, False)
        if self.chkFilterEventLPU.isChecked():
            self.setChkFilterChecked(self.chkFilterEventLPU, False)
        if self.chkFilterEventNonBase.isChecked():
            self.setChkFilterChecked(self.chkFilterEventNonBase, False)
        if self.chkFilterEventMes.isChecked():
            self.setChkFilterChecked(self.chkFilterEventMes, False)
        if self.chkFilterEventResult.isChecked():
            self.setChkFilterChecked(self.chkFilterEventResult, False)
        if self.chkFilterExternalId.isChecked():
            self.setChkFilterChecked(self.chkFilterExternalId, False)
        if self.chkFilterAccountSumLimit.isChecked():
            self.setChkFilterChecked(self.chkFilterAccountSumLimit, False)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExternalId_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAccountSumLimit_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if self.cmbFilterAccountSumLimit.currentIndex() == 0:
            self.edtFilterSumLimitDelta.setValue(0)
            self.edtFilterSumLimitDelta.setEnabled(False)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterAccountSumLimit_currentIndexChanged(self, index):
        if index == 0:
            self.edtFilterSumLimitDelta.setValue(0)
            self.edtFilterSumLimitDelta.setEnabled(False)
        else:
            self.edtFilterSumLimitDelta.setEnabled(True)


#### AmbCard page #################################

    @QtCore.pyqtSlot()
    def on_actAmbCardEditClient_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            self.editClient(clientId)
            self.updateAmbCardInfo()
            self.updateClientsListRequest = True

### Actions page ##################################

    @QtCore.pyqtSlot()
    def on_actActionEditClients_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            self.editClient(clientId)
            self.updateActionInfo()
            self.updateClientsListRequest = True


    @QtCore.pyqtSlot(int)
    def on_tabWidgetActionsClasses_currentChanged(self, index):
        self.cmbFilterActionType.setClass(index)
        self.cmbFilterActionType.setValue(self.__actionTypeIdListByClassPage[index])
        self.on_buttonBoxAction_apply()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsStatus_currentRowChanged(self, current, previous):
        actionId = self.tblActionsStatus.currentItemId()
        self.updateActionInfo(actionId)
        self.updateAmbCardPropertiesTable(current, self.tblActionsStatusProperties)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsDiagnostic_currentRowChanged(self, current, previous):
        actionId = self.tblActionsDiagnostic.currentItemId()
        self.updateActionInfo(actionId)
        self.updateAmbCardPropertiesTable(current, self.tblActionsDiagnosticProperties)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsCure_currentRowChanged(self, current, previous):
        actionId = self.tblActionsCure.currentItemId()
        self.updateActionInfo(actionId)
        self.updateAmbCardPropertiesTable(current, self.tblActionsCureProperties)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsMisc_currentRowChanged(self, current, previous):
        actionId = self.tblActionsMisc.currentItemId()
        self.updateActionInfo(actionId)
        self.updateAmbCardPropertiesTable(current, self.tblActionsMiscProperties)


    @QtCore.pyqtSlot(int)
    def on_modelActionsStatus_itemsCountChanged(self, count):
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblActionsStatusCount.setText(formatRecordsCount(count)+infoBeds+infoAddressOrgStructure)


    @QtCore.pyqtSlot(int)
    def on_modelActionsDiagnostic_itemsCountChanged(self, count):
        self.lblActionsDiagnosticCount.setText(formatRecordsCount(count))


    @QtCore.pyqtSlot(int)
    def on_modelActionsCure_itemsCountChanged(self, count):
        self.lblActionsCureCount.setText(formatRecordsCount(count))


    @QtCore.pyqtSlot(int)
    def on_modelActionsMisc_itemsCountChanged(self, count):
        self.lblActionsMiscCount.setText(formatRecordsCount(count))


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsStatus_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsDiagnostic_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsCure_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsMisc_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()


    @QtCore.pyqtSlot()
    def on_actOpenAccountingByEvent_triggered(self):
        eventId = self.tblEvents.currentItemId()
        self.showAccountingDialog(eventId)


    @QtCore.pyqtSlot()
    def on_actOpenAccountingByAction_triggered(self):
        actionId = self.tblEventActions.currentItemId()
        self.showAccountingDialog(None, actionId)


    @QtCore.pyqtSlot()
    def on_actOpenAccountingByVisit_triggered(self):
        visitId = self.tblEventVisits.currentItemId()
        self.showAccountingDialog(None, None, visitId)


    @QtCore.pyqtSlot()
    def on_actEditActionEvent_triggered(self):
        self.on_btnActionEventEdit_clicked()


    @QtCore.pyqtSlot()
    def on_btnActionEventEdit_clicked(self):
        actionId = self.currentActionId()
        if actionId:
            eventId = forceRef(QtGui.qApp.db.translate('Action', 'id', actionId, 'event_id'))
            if eventId:
                if editEvent(self, eventId):
                   self.on_buttonBoxAction_apply()
        self.focusActions()


    @QtCore.pyqtSlot()
    def on_btnActionEdit_clicked(self):
        actionId = self.currentActionId()
        if actionId:
            self.editAction(actionId)
        self.focusActions()


    @QtCore.pyqtSlot()
    def on_btnActionPrint_clicked(self):
        tblActions = self.getCurrentActionsTable()
        tblActions.setReportHeader(u'Список мероприятий')
        tblActions.setReportDescription(self.getActionFilterAsText())
#        model = tblActions.model()
#        if self.cmbFilterAction.currentIndex() == 0:
#            dataRoles = [None]*3 + [Qt.DisplayRole]*(model.columnCount()-3)
#        else:
#            dataRoles = [Qt.DisplayRole]*(model.columnCount())
#        tblActions.printContent(dataRoles)
        tblActions.printContent()
        self.focusActions()


    @QtCore.pyqtSlot()
    def on_btnActionFilter_clicked(self):
        for s in self.chkListOnActionsPage:
            chk = s[0]
            if chk.isChecked():
                self.activateFilterWdgets(s[1])
                return
        dfltChk = self.chkFilterActionType
        self.setChkFilterChecked(dfltChk, True)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionType_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if not checked or not self.chkTakeIntoAccountProperty.isChecked():
            self.enabledOptionProperty(checked)
            self.setChkFilterChecked(self.chkListProperty, False)
            self.chkListProperty.setEnabled(False)
            self.tblListOptionProperty.setEnabled(False)


    @QtCore.pyqtSlot(bool)
    def on_chkThresholdPenaltyGrade_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkListProperty_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        actionTypeId = forceRef(self.cmbFilterActionType.value())
        self.enabledOptionProperty(checked, actionTypeId)


    def enabledOptionProperty(self, checked, actionTypeId = None):
        if actionTypeId and checked:
            self.bufferRecordsOptionProperty = []
            self.tblListOptionProperty.setEnabled(True)
            QtGui.qApp.callWithWaitCursor(self, self.printDataOptiontPropertys, actionTypeId)
        else:
            self.bufferRecordsOptionProperty = []
            self.tblListOptionProperty.selectAll()
            self.tblListOptionProperty.clear()
            self.tblListOptionProperty.setEnabled(False)


    def printDataOptiontPropertys(self, typeActionId = None):
        self.bufferRecordsOptionProperty = []
        self.rows = 0
        if typeActionId:
            db = QtGui.qApp.db
            table = db.table('ActionPropertyType')
            cols = [table['id'], table['name']]
            cond = [table['actionType_id'].eq(typeActionId)]
            records = db.getRecordList(table, cols, cond, u'name')
            for record in records:
                nameProperty = u''
                self.bufferRecordsOptionProperty.append(record)
                nameProperty = forceString(record.value('name'))
                self.tblListOptionProperty.addItem(CFilterPropertyOptionsItem(nameProperty, self.tblListOptionProperty))
                item = self.tblListOptionProperty.item(self.rows)
                self.tblListOptionProperty.scrollToItem(item)
                self.rows += 1


    def getDataOptionPropertyChecked(self):
        optionPropertyIdList = []
        rowCount = 0
        rowCount = self.tblListOptionProperty.count() - 1
        while rowCount >= 0:
            optionPropertyItem = self.tblListOptionProperty.item(rowCount)
            if optionPropertyItem:
                if optionPropertyItem.checkState() == QtCore.Qt.Checked:
                    record = self.bufferRecordsOptionProperty[rowCount]
                    optionPropertyIdList.append(forceRef(record.value('id')))
            rowCount -= 1
        return optionPropertyIdList


    @QtCore.pyqtSlot(bool)
    def on_chkFilledProperty_clicked(self, checked):
        if checked:
            self.setChkFilterChecked(self.chkThresholdPenaltyGrade, False)
            self.chkThresholdPenaltyGrade.setEnabled(False)
            self.edtThresholdPenaltyGrade.setEnabled(False)
        elif self.chkTakeIntoAccountProperty.isChecked():
             self.chkThresholdPenaltyGrade.setEnabled(True)


    @QtCore.pyqtSlot(bool)
    def on_chkTakeIntoAccountProperty_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if not checked or not self.chkFilterActionType.isChecked():
            self.enabledOptionProperty(checked)
            self.setChkFilterChecked(self.chkListProperty, False)
            self.chkListProperty.setEnabled(False)
            self.tblListOptionProperty.setEnabled(False)
        elif checked and self.chkFilterActionType.isChecked():
              self.chkListProperty.setEnabled(True)
        if not self.chkThresholdPenaltyGrade.isChecked():
            self.edtThresholdPenaltyGrade.setEnabled(False)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterActionType_currentIndexChanged(self, index):
        index = self.tabWidgetActionsClasses.currentIndex()
        self.__actionTypeIdListByClassPage[index] = self.cmbFilterActionType.value()
        actionTypeId = forceRef(self.cmbFilterActionType.value())
        self.enabledOptionProperty(self.chkListProperty.isChecked(), actionTypeId)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionSetDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionSetSpeciality_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterActionSetPerson.setSpecialityId(self.cmbFilterActionSetSpeciality.value())
        else:
            self.cmbFilterActionSetPerson.setSpecialityId(None)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExecSetSpeciality_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterExecSetPerson.setSpecialityId(self.cmbFilterExecSetSpeciality.value())
        else:
            self.cmbFilterExecSetPerson.setSpecialityId(None)


    @QtCore.pyqtSlot(int)
    def on_cmbFilterActionSetSpeciality_currentIndexChanged(self, index):
        self.cmbFilterActionSetPerson.setSpecialityId(self.cmbFilterActionSetSpeciality.value())


    @QtCore.pyqtSlot(int)
    def on_cmbFilterExecSetSpeciality_currentIndexChanged(self, index):
        self.cmbFilterExecSetPerson.setSpecialityId(self.cmbFilterExecSetSpeciality.value())


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionSetPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExecSetPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAssistant_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionPlannedEndDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionStatus_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionExecDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionCreatePerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionCreateDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionModifyPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionModifyDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionPayStatus_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionId_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)



### Expert page ##################################

    @QtCore.pyqtSlot()
    def on_actExpertEditClient_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            self.editClient(clientId)
            self.updateTempInvalidInfo()
            self.updateClientsListRequest = True


    @QtCore.pyqtSlot(int)
    def on_tabWidgetTempInvalidTypes_currentChanged(self, index):
        filter = 'type=%d'%index
        self.cmbFilterExpertDocType.setTable('rbTempInvalidDocument', False, filter)
        self.cmbFilterExpertReason.setTable('rbTempInvalidReason', False, filter)

        self.cmbFilterExpertDocType.setValue(self.__tempInvalidDocTypeIdListByTypePage[index])
        self.on_buttonBoxExpert_apply()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelExpertTempInvalid_currentRowChanged(self, current, previous):
        tempInvalidId = self.tblExpertTempInvalid.currentItemId()
        self.updateTempInvalidInfo(tempInvalidId)


    def onExpertTempInvalidPopupMenuAboutToShow(self):
        tempInvalidId = self.tblExpertTempInvalid.currentItemId()
        prevId = self.getExpertPrevDocId(self.tblExpertTempInvalid)
        nextId = self.getExpertNextDocId(self.tblExpertTempInvalid)
        self.actExpertTempInvalidNext.setEnabled(bool(nextId))
        self.actExpertTempInvalidPrev.setEnabled(bool(prevId))
        self.actExpertTempInvalidDuplicate.setEnabled(bool(tempInvalidId))


    @QtCore.pyqtSlot()
    def on_actExpertTempInvalidNext_triggered(self):
        nextId = self.getExpertNextDocId(self.tblExpertTempInvalid)
        if nextId:
            row = self.tblExpertTempInvalid.model().findItemIdIndex(nextId)
            if row>=0:
                self.tblExpertTempInvalid.setCurrentRow(row)
            else:
                QtGui.QMessageBox.information(self, u'Переход к следующему документу', u'Переход невозможен - необходимо изменить фильтр')


    def onListBeforeRecordClientPopupMenuAboutToShow(self):
         clientId = self.currentClientId()
         self.actListVisitByQueue.setEnabled(bool(clientId))
         self.actControlDoublesRecordClient.setEnabled(bool(clientId) and QtGui.qApp.userHasRight(urRegControlDoubles))
         self.actReservedOrderQueueClient.setEnabled(bool(QtGui.qApp.mainWindow.dockFreeQueue and QtGui.qApp.mainWindow.dockFreeQueue.content and QtGui.qApp.mainWindow.dockFreeQueue.content._appLockId))


    def onQueuePopupMenuAboutToShow(self):
        self.actAmbCreateEvent.setEnabled(self.modelQueue.rowCount() > 0 and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents]))
        self.actAmbDeleteOrder.setEnabled(self.modelQueue.rowCount() > 0)
        self.actAmbChangeNotes.setEnabled(self.modelQueue.rowCount() > 0)
        self.actAmbPrintOrder.setEnabled(self.modelQueue.rowCount() > 0)
        self.actPrintBeforeRecords.setEnabled(self.modelQueue.rowCount() > 0)
        self.actShowPreRecordInfo.setEnabled(self.modelQueue.rowCount() > 0)


    def checkTblEventsPopupMenu(self):
        self.actOpenAccountingByEvent.setEnabled(self.modelEvents.rowCount()>0)

    def checkTblEventActionsPopupMenu(self):
        self.actOpenAccountingByAction.setEnabled(self.modelEventActions.rowCount()>0)

    def checkTblEventVisitsPopupMenu(self):
        self.actOpenAccountingByVisit.setEnabled(self.modelEventVisits.rowCount()>0)

    @QtCore.pyqtSlot()
    def on_actAmbCreateEvent_triggered(self):
        clientId = self.currentClientId()
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            requestNewEvent(self, clientId, False, None, [], None, self.modelQueue.items[row][1], self.modelQueue.items[row][7])


    @QtCore.pyqtSlot()
    def on_actAmbDeleteOrder_triggered(self):
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            actionId = self.modelQueue.items[row][6]
            if actionId:
                confirmation = QtGui.QMessageBox.warning( self,
                    u'Внимание!',
                    u'Подтвердите удаление записи к врачу',
                    QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
                    QtGui.QMessageBox.Cancel)
                if confirmation != QtGui.QMessageBox.Ok:
                    return
                db = QtGui.qApp.db
                propertiesTable = db.table('ActionProperty_Action')
                tableAction = db.table('Action')
                db.transaction()
                try:
                    db.updateRecords(tableAction, 'deleted=1', [tableAction['id'].eq(actionId)])
                    db.updateRecords(propertiesTable, 'value=NULL', [propertiesTable['value'].eq(actionId)])
                    db.commit()
                except:
                    db.rollback()
                    raise
            QtGui.qApp.emitCurrentClientInfoChanged()
            self.updateQueue()
            if QtGui.qApp.mainWindow.dockResources:
                QtGui.qApp.mainWindow.dockResources.content.updateTimeTable()


    @QtCore.pyqtSlot()
    def on_actAmbChangeNotes_triggered(self):
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            actionId = self.modelQueue.items[row][6]
            if actionId:
                db = QtGui.qApp.db
                table = db.table('Action')
                record = db.getRecord(table, 'id, note', actionId)
                dlg = CComplaintsEditDialog(self)
                dlg.setComplaints(forceString(record.value('note')))
                if dlg.exec_():
                    record.setValue('note', QtCore.QVariant(dlg.getComplaints()))
                    db.updateRecord(table, record)


    @QtCore.pyqtSlot()
    def on_actAmbPrintOrder_triggered(self):
        eventId = None
        timeRange = None, None
        timeRange1 = None, None
        timeRange2 = None, None
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            actionId = self.modelQueue.items[row][6]
            if actionId:
                db = QtGui.qApp.db
                table = db.table('ActionProperty_Action')
                num = forceInt(db.translate(table, table['value'], actionId, table['index']))
                personId = self.modelQueue.items[row][7]
                dateTime = self.modelQueue.items[row][1]
                date = dateTime.date()
                time = dateTime.time()
                clientId = self.currentClientId()
                if clientId:
                    records = forceRef(db.query('''SELECT A.event_id FROM Action AS A WHERE A.id = (SELECT ActionProperty.action_id
FROM Action
INNER JOIN ActionProperty_Action ON ActionProperty_Action.value = Action.id
INNER JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
INNER JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
WHERE Action.id = %d AND ActionPropertyType.name LIKE \'%s\' LIMIT 0, 1)''' % (actionId, 'queue')))
                    if records.first():
                        record = records.record()
                        eventId = forceRef(record.value('event_id'))
                    if eventId:
                        action = CAction.getAction(eventId, atcAmbulance)
                        begTime = action['begTime']
                        endTime = action['endTime']
                        begTime1 = action['begTime1']
                        endTime1 = action['endTime1']
                        begTime2 = action['begTime2']
                        endTime2 = action['endTime2']
                        if begTime and endTime:
                            timeRange = (begTime, endTime)
                        if begTime1 and endTime1:
                            timeRange1 = (begTime1, endTime1)
                        if begTime2 and endTime2:
                            timeRange2 = (begTime2, endTime2)
                        if timeRange1 and timeRange2:
                            start1, finish1 = timeRange1
                            if time >= start1 and time < finish1:
                                timeRange = timeRange1
                            start2, finish2 = timeRange2
                            if time >= start2 and time < finish2:
                                timeRange = timeRange2
                        printOrder(self, clientId, 0, date, self.modelQueue.items[row][2], personId, num+1, time, unicode(formatTimeRange(timeRange)))


    @QtCore.pyqtSlot()
    def on_actPrintBeforeRecords_triggered(self):
        if self.modelQueue.rowCount():
            self.tblQueue.setReportHeader(u'Протокол предварительной записи пациента')
            self.tblQueue.setReportDescription(self.txtClientInfoBrowser.toHtml())
            dataRoles = [None]
            for _ in xrange(1, self.tblQueue.model().columnCount()): dataRoles.append(QtCore.Qt.DisplayRole)
            self.tblQueue.printContent(dataRoles)


    @QtCore.pyqtSlot()
    def on_actShowPreRecordInfo_triggered(self):
        row = self.tblQueue.currentRow()
        item = self.modelQueue.items[row]
        self.showPreRecordInfo(item)


    @QtCore.pyqtSlot()
    def on_actControlDoublesRecordClient_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            CRegistryControlDoubles(self, clientId).exec_()
            self.on_buttonBox_apply()


    @QtCore.pyqtSlot()
    def on_actReservedOrderQueueClient_triggered(self):
        dockFreeQueue = QtGui.qApp.mainWindow.dockFreeQueue
        if dockFreeQueue and dockFreeQueue.content and dockFreeQueue.content._appLockId:
            dockFreeQueue.content.on_actAmbCreateOrder_triggered()


    @QtCore.pyqtSlot()
    def on_actListVisitByQueue_triggered(self):
        try:
            clientId = self.currentClientId()
            if QtGui.qApp.mainWindow.dockResources.content and clientId:
                QtGui.qApp.mainWindow.dockResources.content.createVisitBeforeRecordClient(clientId)
        except:
            pass


    @QtCore.pyqtSlot()
    def on_actExpertTempInvalidPrev_triggered(self):
        prevId = self.getExpertPrevDocId(self.tblExpertTempInvalid)
        if prevId:
            row = self.tblExpertTempInvalid.model().findItemIdIndex(prevId)
            if row>=0:
                self.tblExpertTempInvalid.setCurrentRow(row)
            else:
                QtGui.QMessageBox.information(self, u'Переход к предыдущему документу', u'Переход невозможен - необходимо изменить фильтр')


    @QtCore.pyqtSlot()
    def on_actExpertTempInvalidDuplicate_triggered(self):
        tempInvalidId = self.tblExpertTempInvalid.currentItemId()
        if tempInvalidId:
            dialog = CTempInvalidDuplicateEditDialog(self)
            dialog.setTempInvalid(tempInvalidId)
            if dialog.exec_():
                self.updateTempInvalidInfo(tempInvalidId)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertTempInvalidDuplicates_doubleClicked(self, index):
        itemId = self.tblExpertTempInvalidDuplicates.currentItemId()
        if itemId:
            dialog = CTempInvalidDuplicateEditDialog(self)
            dialog.load(itemId)
            if dialog.exec_():
                self.tblExpertTempInvalidDuplicates.model().invalidateRecordsCache()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelExpertDisability_currentRowChanged(self, current, previous):
        tempInvalidId = self.tblExpertDisability.currentItemId()
        self.updateTempInvalidInfo(tempInvalidId)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelExpertVitalRestriction_currentRowChanged(self, current, previous):
        tempInvalidId = self.tblExpertVitalRestriction.currentItemId()
        self.updateTempInvalidInfo(tempInvalidId)


    @QtCore.pyqtSlot(int)
    def on_modelExpertTempInvalid_itemsCountChanged(self, count):
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblExpertTempInvalidCount.setText(formatRecordsCount(count)+infoBeds+infoAddressOrgStructure)


    @QtCore.pyqtSlot(int)
    def on_modelExpertDisability_itemsCountChanged(self, count):
        self.lblExpertDisabilityCount.setText(formatRecordsCount(count))


    @QtCore.pyqtSlot(int)
    def on_modelExpertVitalRestriction_itemsCountChanged(self, count):
        self.lblExpertVitalRestrictionCount.setText(formatRecordsCount(count))


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertTempInvalid_doubleClicked(self, index):
        self.on_btnExpertEdit_clicked()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertDisability_doubleClicked(self, index):
        self.on_btnExpertEdit_clicked()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertVitalRestriction_doubleClicked(self, index):
        self.on_btnExpertEdit_clicked()


    @QtCore.pyqtSlot()
    def on_btnExpertEdit_clicked(self):
        tempInvalidId = self.currentTempInvalidId()
        if tempInvalidId:
            self.editTempInvalid(tempInvalidId)
        self.focusExpert()
        QtGui.qApp.emitCurrentClientInfoChanged()


    @QtCore.pyqtSlot()
    def on_btnExpertPrint_clicked(self):
        tblExpert = self.getCurrentExpertTable()
        tempInvalidType = self.tabWidgetTempInvalidTypes.currentIndex()
        tblExpert.setReportHeader(unicode(self.tabWidgetTempInvalidTypes.tabText(tempInvalidType)))
        tblExpert.setReportDescription(self.getExpertFilterAsText())
        model = tblExpert.model()
        tblExpert.printContent()
        self.focusExpert()


    @QtCore.pyqtSlot()
    def on_btnExpertFilter_clicked(self):
        for s in self.chkListOnExpertPage:
            chk = s[0]
            if chk.isChecked():
                self.activateFilterWdgets(s[1])
                return
        dfltChk = self.chkFilterExpertDocType
        self.setChkFilterChecked(dfltChk, True)


    @QtCore.pyqtSlot()
    def on_btnExpertNew_clicked(self):
        self.editTempInvalidExpert()
        self.focusExpert()
        QtGui.qApp.emitCurrentClientInfoChanged()


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertDocType_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertSerial_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertNumber_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertReason_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertBegDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertEndDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertMKB_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertClosed_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertDuration_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertInsuranceOfficeMark_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertCreatePerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertModifyPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertCreateDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)


    def checkAmbOrHome(self, APAction_id):
        stmt = 'SELECT ActionType.code FROM ActionProperty_Action LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id LEFT JOIN Action ON Action.id = ActionProperty.action_id LEFT JOIN ActionType ON ActionType.id = Action.actionType_id WHERE ActionProperty_Action.id = %d' % APAction_id
        query = QtGui.qApp.db.query(stmt)
        if query.first():
            return forceString(query.value(0))
        return None

    def showPreRecordInfo(self, preRecordItem):
        actionId = preRecordItem[6]
        dateTime = preRecordItem[1].toString('dd.MM.yyyy hh:mm')
        office = preRecordItem[2]
        APAction_id = preRecordItem[8]
        ambOrHome = self.checkAmbOrHome(APAction_id)
        db = QtGui.qApp.db
        actionRecord = db.getRecord('Action', '*', actionId)
        createDatetime = forceString(actionRecord.value('createDatetime'))
        createPerson = forceString(db.translate('vrbPersonWithSpeciality',
                                              'id', forceRef(actionRecord.value('createPerson_id')),
                                              'name'))
        modifyDatetime = forceString(actionRecord.value('modifyDatetime'))
        modifyPerson = forceString(db.translate('vrbPersonWithSpeciality',
                                              'id', forceRef(actionRecord.value('modifyPerson_id')),
                                              'name'))
        clientId = forceRef(db.translate('Event', 'id',
                                         forceRef(actionRecord.value('event_id')), 'client_id'))
        personInfo = getPersonInfo(forceRef(actionRecord.value('person_id')))
        clientInfo = getClientInfoEx(clientId)

        report = CReportBase()
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Свойства записи')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)

        cursor.insertText(u'Создатель записи: %s\n' % createPerson)
        cursor.insertText(u'Дата создания записи: %s\n' % createDatetime)
        cursor.insertText(u'Редактор записи: %s\n' % modifyPerson)
        cursor.insertText(u'Дата редактирования записи: %s\n\n' % modifyDatetime)

        cursor.insertText(u'дата записи: %s\n' % forceString(forceDate(actionRecord.value('createDatetime'))))
        if personInfo:
            specialityName = personInfo['specialityName']
            orgStructure_id = forceInt(db.translate('Person', 'id', personInfo['id'], 'orgStructure_id'))
            orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
            cursor.insertText(u'врач: %s, %s\n' % (personInfo['fullName'], personInfo['specialityName']))
            cursor.insertText(u'подразделение: %s, %s\n' % (orgStructureName, personInfo['postName']))
        if clientInfo:
            cursor.insertText(u'пациент: %s\n' % clientInfo['fullName'])
            cursor.insertText(u'д/р: %s\n' % clientInfo['birthDate'])
            cursor.insertText(u'возраст: %s\n' % clientInfo['age'])
            cursor.insertText(u'пол: %s\n' % clientInfo['sex'])
            cursor.insertText(u'адрес: %s\n' % clientInfo['regAddress'])
            cursor.insertText(u'полис: %s\n' % clientInfo['policy'])
            cursor.insertText(u'паспорт: %s\n' % clientInfo['document'])
            cursor.insertText(u'СНИЛС: %s\n' % clientInfo['SNILS'])
        note = forceString(actionRecord.value('note'))
        cursor.insertText(u'жалобы/примечания: %s\n' % note)

        if ambOrHome:
            if ambOrHome == 'amb':
                cursor.insertText(u'запись на амбулаторный приём ')
                if bool(office):
                    office = u' к. '+office
                else:
                    office = ''
                cursor.insertText(unicode(dateTime) +office)
            elif ambOrHome == 'home':
                cursor.insertText(u'вызов на дом ')
                cursor.insertText(unicode(dateTime))

        cursor.insertBlock()
        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Свойства записи')
        reportView.setText(doc)
        reportView.exec_()
# ===== :)


def convertFilterToTextItem(resList, filter, prop, propTitle, format=None):
    val = filter.get(prop, None)
    if val:
        if format:
            resList.append((propTitle, format(val)))
        else:
            resList.append((propTitle, val))


class CIdValidator(QtGui.QRegExpValidator):
    def __init__(self, parent):
        QtGui.QRegExpValidator.__init__(self, QtCore.QRegExp(r'(\d*)(\.\d*)?'), parent)


def dateTimeToString(value):
#   return value.toString(Qt.DefaultLocaleLongDate)
    return  value.toString('dd.MM.yyyy hh:mm:ss')


def parseClientId(clientIdEx):
    if '.' in clientIdEx:
        miacCode, clientId = clientIdEx.split('.')
    else:
        miacCode, clientId = '', clientIdEx
    if miacCode:
        if forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode')) != miacCode.strip():
            return -1
    return int(clientId)


class CQueueModel(QtCore.QAbstractTableModel):
    headerText = [u'Отметка', u'Дата и время приема', u'Каб', u'Специалист', u'Записал', u'Примечания']

    def __init__(self,  parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.clientId = None
        self._cols = []
        self.items = []


    def cols(self):
        self._cols = [CBoolCol(u'Отметка', ['status'], 6),
                      CDateTimeFixedCol(u'Дата и время приема', ['directionDate'], 20),
                      CTextCol(u'Каб',           ['office'], 6),
                      CRefBookCol(u'Специалист', ['person_id'], 'vrbPersonWithSpeciality', 20),
                      CRefBookCol(u'Записал',    ['setPerson_id'], 'vrbPersonWithSpeciality', 20),
                      CTextCol(u'Примечания',    ['note'], 6),
                     ]
        return self._cols


    def columnCount(self, index = QtCore.QModelIndex()):
        return 6


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
        column = index.column()
        if column == 0:
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if column > 0:
                item = self.items[row]
                return toVariant(item[column])
        elif role == QtCore.Qt.CheckStateRole and QtGui.qApp.ambulanceUserCheckable():
            if column == 0:
                item = self.items[row]
                return toVariant(QtCore.Qt.Checked if item[0]==0 else QtCore.Qt.Unchecked)
        return QtCore.QVariant()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.CheckStateRole and QtGui.qApp.ambulanceUserCheckable():
            if column == 0:
                db = QtGui.qApp.db
                table = db.table('Action')
                actionId = forceRef(self.items[row][6])
                status = forceInt(self.items[row][0])
                if actionId and status in (0, 1) and self.clientId:
                    newStatus = 1-status
                    record = db.getRecord(table, ['id', 'status'], actionId)
                    record.setValue('status', QtCore.QVariant(newStatus))
                    try:
                        db.updateRecord(table, record)
                        self.items[row][column] = newStatus
                        self.emitCellChanged(row, column)
                        dockResources = QtGui.qApp.mainWindow.dockResources
                        if dockResources and dockResources.content:
                            dockResources.content.modelAmbQueue.setStatus(self.clientId, actionId, newStatus)
                            dockResources.content.tblAmbQueue.setFocus(QtCore.Qt.OtherFocusReason)
                        return True
                    except:
                        pass
            return True
        return False


    def loadData(self, clientId = None):
        self.items = []
        etcQueue = 'queue'
        atcQueue = 'queue'
        recordBufferEventId = []
        if clientId:
            self.clientId = clientId
            currentDate = forceDateTime(QtCore.QDate.currentDate())
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableEvent = db.table('Event')
            tableActionProperty_Action = db.table('ActionProperty_Action')
            cols = [tableAction['id'],
                    tableAction['setPerson_id'],
                    tableAction['person_id'],
                    tableAction['status'],
                    tableAction['office'],
                    tableAction['directionDate'],
                    tableAction['note'],
                    tableActionProperty_Action['id'].alias('APAction_id')]
            actionType = CActionTypeCache.getByCode(atcQueue)
            actionTypeId = actionType.id
            eventType = getEventType(etcQueue)
            eventTypeId = eventType.eventTypeId
            cond = [tableEvent['client_id'].eq(self.clientId),
                    tableEvent['setDate'].ge(currentDate),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableEvent['eventType_id'].eq(eventTypeId),
                    tableAction['actionType_id'].eq(actionTypeId)]
            tableQuery = tableAction
            tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
            records = db.getRecordList(tableQuery, cols, cond, 'Action.directionDate')
            for record in records:
                actionId = forceRef(record.value('id'))
                personId = forceRef(record.value('person_id'))
                setPersonId = forceRef(record.value('setPerson_id'))
                APAction_id = forceRef(record.value('APAction_id'))
                item = [forceInt(record.value('status')),
                        forceDateTime(record.value('directionDate')),
                        forceString(record.value('office')),
                        forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')) if personId else u'',
                        forceString(db.translate('vrbPersonWithSpeciality', 'id', setPersonId, 'name')) if setPersonId else u'',
                        forceString(record.value('note')),
                        actionId,
                        personId,
                        APAction_id
                        ]
                self.items.append(item)
        self.reset()


    def emitCellChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)


class CVisitByQueueModel(QtCore.QAbstractTableModel):
    headerText = [u'Выполнено', u'Дата и время приема', u'Каб', u'Специалист', u'Записал', u'Примечания']

    def __init__(self,  parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._cols = []
        self.items = []


    def cols(self):
        self._cols = [CDateTimeFixedCol(u'Дата и время приема', ['directionDate'], 20),
                      CTextCol(u'Каб',            ['office'], 6),
                      CRefBookCol(u'Специалист',  ['person_id'], 'vrbPersonWithSpeciality', 20),
                      CRefBookCol(u'Записал',    ['setPerson_id'], 'vrbPersonWithSpeciality', 20),
                      CTextCol(u'Примечания',     ['note'], 6),
                     ]
        return self._cols


    def columnCount(self, index = QtCore.QModelIndex()):
        return 6


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if column != 0:
                item = self.items[row]
                return toVariant(item[column])
        elif role == QtCore.Qt.CheckStateRole:
            if column == 0:
                item = self.items[row]
                return toVariant(QtCore.Qt.Checked if item[column] else QtCore.Qt.Unchecked)
        return QtCore.QVariant()


    def loadData(self, clientId = None):
        self.items = []
        if clientId:
            currentDateTime = forceDateTime(QtCore.QDateTime.currentDateTime())
            etcQueue = 'queue'
            atcQueue = 'queue'
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableVisit = db.table('Visit')
            tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
            tableActionProperty_Action = db.table('ActionProperty_Action')
            tableOrgStructure = db.table('OrgStructure')
            cols = [tableAction['id'],
                    tableAction['directionDate'],
                    tableAction['setPerson_id'],
                    tableAction['person_id'],
                    tableAction['office'],
                    tableAction['note'],
                    tablePersonWithSpeciality['speciality_id']
                    ]
            actionType = CActionTypeCache.getByCode(atcQueue)
            actionTypeId = actionType.id
            eventType = getEventType(etcQueue)
            eventTypeId = eventType.eventTypeId
            tableQuery = tableAction
            tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
            tableQuery = tableQuery.innerJoin(tablePersonWithSpeciality, tablePersonWithSpeciality['id'].eq(tableAction['person_id']))
            cond = [tableEvent['client_id'].eq(clientId),
                    tableAction['directionDate'].lt(currentDateTime),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableEvent['eventType_id'].eq(eventTypeId),
                    tableAction['actionType_id'].eq(actionTypeId)
                    ]
            recordBufferAction = db.getRecordList(tableQuery, cols, cond, 'Action.directionDate')
            listDirectionDateAction = []
            specialityIdList = []
            personIdList = []
            for recordDirectionDateAction in recordBufferAction:
                directionDate = forceDate(recordDirectionDateAction.value('directionDate'))
                if directionDate and directionDate not in listDirectionDateAction:
                    listDirectionDateAction.append(directionDate)
                specialityId = forceRef(recordDirectionDateAction.value('speciality_id'))
                if specialityId and specialityId not in specialityIdList:
                    specialityIdList.append(specialityId)
                personId = forceRef(recordDirectionDateAction.value('person_id'))
                if personId and personId not in personIdList:
                    personIdList.append(personId)
            if listDirectionDateAction:
                cols = [tableVisit['date'],
                        tableVisit['person_id'],
                        tableVisit['event_id'].alias('eventId'),
                        tablePersonWithSpeciality['speciality_id'],
                        tablePersonWithSpeciality['name'].alias('personName')
                        ]
                condVisit = [tableVisit['date'].inlist(listDirectionDateAction),
                             tableEvent['client_id'].eq(clientId),
                             tableEvent['deleted'].eq(0),
                             tableVisit['deleted'].eq(0)
                             ]
                condVisit.append(db.joinOr([tablePersonWithSpeciality['speciality_id'].inlist(specialityIdList), tableVisit['person_id'].inlist(personIdList)]))
                tableQueryVisit = tableVisit
                tableQueryVisit = tableQueryVisit.innerJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
                tableQueryVisit = tableQueryVisit.innerJoin(tablePersonWithSpeciality, tablePersonWithSpeciality['id'].eq(tableVisit['person_id']))
                recordVisit = db.getRecordList(tableQueryVisit, cols, condVisit, 'Visit.date')
            for record in recordBufferAction:
                directionDate = forceDate(record.value('directionDate'))
                setPersonId = forceRef(record.value('setPerson_id'))
                personId = forceRef(record.value('person_id'))
                specialityId = forceRef(record.value('speciality_id'))
                actionId = forceRef(record.value('id'))
                visit, eventId = self.getVisit(directionDate, personId, specialityId, recordVisit)
                item = [visit,
                        forceDateTime(record.value('directionDate')),
                        forceString(record.value('office')),
                        forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')) if personId else u'',
                        forceString(db.translate('vrbPersonWithSpeciality', 'id', setPersonId, 'name')) if setPersonId else u'',
                        forceString(record.value('note')),
                        actionId,
                        eventId
                        ]
                self.items.append(item)
        self.reset()


    def getVisit(self, directionDate=None, personId=None, specialityId=None, recordVisit=None):
        if not recordVisit:
            recordVisit = []
        for recordVisitData in recordVisit:
            if directionDate and (personId or specialityId):
                if directionDate == forceDate(recordVisitData.value('date')):
                    if personId == forceRef(recordVisitData.value('person_id')):
                        eventId = forceRef(recordVisitData.value('eventId'))
                        return True, eventId
                    elif specialityId == forceRef(recordVisitData.value('speciality_id')):
                        eventId = forceRef(recordVisitData.value('eventId'))
                        return True, eventId
        return False, None



#    @QtCore.pyqtSlot()
#    def on_actAmbCreateEvent_triggered(self):
#        clientId = self.getCurrentQueuedClientId(self.tblAmbQueue)
#        QtGui.qApp.requestNewEvent(clientId)

def contactToLikeMask(contact):
    m = '...'
    result = m+m.join(contact.replace('-','').replace(' ','').replace('.',''))+m
    return result
