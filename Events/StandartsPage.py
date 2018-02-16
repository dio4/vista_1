# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QTreeWidgetItem

from Events.Action import CAction
from Events.ActionInfo import CCookedActionInfo
from Events.ActionsTemplatePrintDialog import CActionTemplatePrintWidget
from Events.Utils import setActionPropertiesColumnVisible, getEventContextData
from library.DialogBase import CConstructHelperMixin
from Ui_StandartsPage import Ui_QStandartPageWidget
from library.PrintTemplates import customizePrintButton, getPrintTemplates, getVal, applyTemplate
from library.TableModel import CCol, CBoolCol
from library.Utils import forceInt, forceString, forceBool, toVariant, forceDate, setPref, getPref, getPrefInt
from Events.ActionPropertiesTable import CActionPropertiesTableModel


class CFastStandartsPage(QtGui.QDialog, CConstructHelperMixin, Ui_QStandartPageWidget):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.eventEditor = None
        self.eventId = None
        self.relatedEventsTableActive = QtGui.qApp.isNextEventCreationFromAction()
        self.db = QtGui.qApp.db
        self.MKB = None
        self.addModels('APActionProperties', CActionPropertiesTableModel(self))
        self.addModels('BaseTableModel', CBaseServiceModel(self))
        self.mesItems = {}
        self.oldMesServices = []
        self.actPrintSelected = QtGui.QAction(u'Напечатать выделенное', self)
        self.actPrintSelected.setObjectName('actPrintSelected')
        self.connect(self.actPrintSelected, QtCore.SIGNAL('triggered()'), self.on_printSelected_triggered)

    def setupUiMini(self, Dialog):
        pass

    def preSetupUiMini(self):
        pass

    def preSetupUi(self):
        pass

    def postSetupUiMini(self):
        pass

    def postSetupUi(self):
        self.setupModels()
        self.setFocusProxy(self.cmbMes)
        self.cmbMes.setDefaultValue()
        self.cmbMes._popup.setCheckBoxes('f030s')
        self.setTablePrefs('treeStandart')
        if self.mesItems:
            self.btnAdd.setText(u'Заменить')
        self.treeStandartList.addAction(self.actPrintSelected)
        self.connect(self.btnAPPrint, QtCore.SIGNAL('printByTemplate(int)'), self.printByTemplate)

    def setRecord(self, record):
        self.setEventId(forceInt(record.value('id')))
        tableAction = self.db.table('Action')
        actionList = self.db.getDistinctIdList(tableAction, tableAction['id'], [tableAction['event_id'].eq(forceInt(record.value('id'))),
                                                                       tableAction['deleted'].eq(0),
                                                                       tableAction['MES_id'].isNotNull()])
        if actionList:
            mesList = []
            for v in actionList:
                recAction = self.db.getRecordEx(tableAction, '*', tableAction['id'].eq(v))
                if not forceInt(recAction.value('MES_id')) in mesList:
                    mesList.append(forceInt(recAction.value('MES_id')))
                    mesActionList = self.db.getDistinctIdList(tableAction, tableAction['id'], [tableAction['event_id'].eq(forceInt(record.value('id'))),
                                                                                       tableAction['MES_id'].eq(forceInt(recAction.value('MES_id')))])
                    actionsList = []
                    for k in mesActionList:
                        actionRecord = self.db.getRecordEx(tableAction, '*', tableAction['id'].eq(k))
                        if forceInt(actionRecord.value('id')):
                            action = CAction(record=actionRecord)
                            actionsList.append(action)
                    self.mesItems[forceInt(recAction.value('MES_id'))] = actionsList
            self.updateMesTree()

    def getRecord(self, record):
        pass

    def save(self, eventId):
        self.getTablePrefs()
        for k in self.mesItems.keys():
            for v in self.mesItems[k]:
                if forceString(v.getRecord().value('MES_id')):
                    v.save(eventId)
        if self.oldMesServices:
            for v in self.oldMesServices:
                v.save(eventId)

    def printByTemplate(self, templateId):
        if self.eventEditor.isDirty() and forceInt(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'banUnkeptDate')) == 2:
            if QtGui.QMessageBox.question(self,
                                       u'Внимание!',
                                       u'Для печати данного шаблона необходимо сохранить обращение.\nСохранить сейчас?',
                                       QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return
            if not self.eventEditor.saveData():
                return
        if not self.treeStandartList.selectedItems():
            value = None
        else:
            value = self.treeStandartList.selectedItems()[0]
        currentAction = self.getActionByItem(value, value.parent())
        if currentAction:
            data = getEventContextData(self.eventEditor)
            eventInfo = data['event']
            action = CCookedActionInfo(eventInfo.context, currentAction.getRecord(), currentAction)
            action.setCurrentPropertyIndex(self.tblAPProps.currentIndex().row())
            data['action'] = action
            data['actions'] = self.getActionByItem(value, value.parent())
            data['currentActionIndex'] = 0
            applyTemplate(self.eventEditor, templateId, data)


    def updateMesTree(self):
        tableMes = self.db.table('mes.MES')
        tableAction = self.db.table('Action')
        tableMesServices = self.db.table('mes.mrbServiceGroup')
        for k in self.mesItems.keys():
            servicesList = self.mesItems[k]
            recMes = self.db.getRecordEx(tableMes, '*', tableMes['id'].eq(k))
            rootItem = QTreeWidgetItem()
            rootItem.setText(0, forceString(recMes.value('name')))
            rootItem.setText(3, forceString(0))
            self.treeStandartList.addTopLevelItem(rootItem)
            groupsList = self.getMesGroups(k)
            for v in groupsList:
                if v:
                    serviceItem = QTreeWidgetItem(rootItem)
                    serviceItem.setText(0, forceString(self.db.translate(tableMesServices, tableMesServices['id'], forceInt(v), tableMesServices['name'])))
                    for i in servicesList:
                        if self.getNecessityByAction(i.getType().id, k) == u'1' and not forceString(i.getType().code) == u'medicament':
                            recAction = self.db.getRecordEx(tableAction, '*',
                                                            tableAction['id'].eq(i.getRecord().value('id')))
                            if forceString(serviceItem.text(0)) == forceString(self.getServiceGroup(i)):
                                childItem = QTreeWidgetItem(serviceItem)
                                childItem.setText(0, forceString(i.getType().name))
                                childItem.setFlags(childItem.flags() | QtCore.Qt.ItemIsUserCheckable)
                                if recAction:
                                    if forceString(recAction.value('begDate')):
                                        childItem.setBackground(0, QtGui.QBrush(QtGui.QColor(255, 128, 0)))
                                        childItem.setCheckState(1, QtCore.Qt.Checked)
                                    else:
                                        childItem.setCheckState(1, QtCore.Qt.Unchecked)
                                    if forceString(recAction.value('endDate')):
                                        childItem.setBackground(0, QtGui.QBrush(QtCore.Qt.green))
                                        childItem.setCheckState(2, QtCore.Qt.Checked)
                                    else:
                                        childItem.setCheckState(2, QtCore.Qt.Unchecked)
                                else:
                                    childItem.setCheckState(1, QtCore.Qt.Unchecked)
                                    childItem.setCheckState(2, QtCore.Qt.Unchecked)
                else:
                    serviceItem = QTreeWidgetItem(rootItem)
                    serviceItem.setText(0, u'Услуги без группы')
                    for i in servicesList:
                        if self.getNecessityByAction(i.getType().id, k) == u'1' and not forceString(i.getType().code) == u'medicament':
                            recAction = self.db.getRecordEx(tableAction, '*',
                                                            tableAction['id'].eq(i.getRecord().value('id')))
                            if not forceString(self.getServiceGroup(i)):
                                childItem = QTreeWidgetItem(serviceItem)
                                childItem.setText(0, forceString(i.getType().name))
                                childItem.setFlags(childItem.flags() | QtCore.Qt.ItemIsUserCheckable)
                                if recAction:
                                    if forceString(recAction.value('begDate')):
                                        childItem.setBackground(0, QtGui.QBrush(QtGui.QColor(255, 128, 0)))
                                        childItem.setCheckState(1, QtCore.Qt.Checked)
                                    else:
                                        childItem.setCheckState(1, QtCore.Qt.Unchecked)
                                    if forceString(recAction.value('endDate')):
                                        childItem.setBackground(0, QtGui.QBrush(QtCore.Qt.green))
                                        childItem.setCheckState(2, QtCore.Qt.Checked)
                                    else:
                                        childItem.setCheckState(2, QtCore.Qt.Unchecked)
                                else:
                                    childItem.setCheckState(1, QtCore.Qt.Unchecked)
                                    childItem.setCheckState(2, QtCore.Qt.Unchecked)


            medicalItem = QTreeWidgetItem(rootItem)
            medicalItem.setText(0, u'Медикаменты')
            for i in servicesList:
                if self.getMedicamentNecessity(i.getType().id, k) == u'1' and forceString(
                        i.getType().code) == u'medicament':
                    recAction = self.db.getRecordEx(tableAction, '*',
                                                    tableAction['id'].eq(i.getRecord().value('id')))
                    childItem = QTreeWidgetItem(medicalItem)
                    childItem.setText(0, forceString(i.getType().name))
                    childItem.setFlags(childItem.flags() | QtCore.Qt.ItemIsUserCheckable)
                    if recAction:
                        if forceString(recAction.value('begDate')):
                            childItem.setBackground(0, QtGui.QBrush(QtGui.QColor(255, 128, 0)))
                            childItem.setCheckState(1, QtCore.Qt.Checked)
                        else:
                            childItem.setCheckState(1, QtCore.Qt.Unchecked)
                        if forceString(recAction.value('endDate')):
                            childItem.setBackground(0, QtGui.QBrush(QtCore.Qt.green))
                            childItem.setCheckState(2, QtCore.Qt.Checked)
                        else:
                            childItem.setCheckState(2, QtCore.Qt.Unchecked)
                    else:
                        childItem.setCheckState(1, QtCore.Qt.Unchecked)
                        childItem.setCheckState(2, QtCore.Qt.Unchecked)
            self.treeStandartList.expandAll()
            self.calcDone()

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor

    def setClientInfo(self, clientSex, clientAge, clientId=None):
        self.cmbMes.setClientSex(clientSex)
        self.cmbMes.setClientAge(clientAge)
        self.cmbMes.setClientId(clientId)

    def setSpeciality(self, specialityId):
        self.cmbMes.setSpeciality(specialityId)

    def setContract(self, contractId):
        self.cmbMes.setContract(contractId)

    def setEndDateForTariff(self, endDate):
        self.cmbMes.setEndDateForTariff(endDate)

    def setBegDate(self, date):
        self.cmbMes.setBegDate(date)

    def setEndDate(self, date):
        self.cmbMes.setEndDate(date)

    def setMKB(self, MKB):
        self.MKB = MKB
        self.cmbMes.setMKB(MKB)

    def setMKB2(self, MKB2List):
        self.cmbMes.setMKB2(MKB2List)

    def setEventTypeId(self, eventTypeId):
        pass

    def setActionModel(self, model):
        self.actionsModel = model

    def setupModels(self):
        self.setModels(self.tblStandart, self.modelBaseTableModel, self.selectionModelBaseTableModel)
        self.setModels(self.tblAPProps, self.modelAPActionProperties, self.selectionModelAPActionProperties)


    def setEventId(self, value):
        self.eventId = value

    def updateActionEditor(self):
        model = self.tblStandart.model()
        if QtGui.qApp.isCheckMKB():
            self.cmbAPMKB.setMKBFilter({'begDate': self.eventEditor.edtBegDate.date(), 'clientId': self.eventEditor.clientId})
        if model.rowCount() > 0:
            self.tblAPActions.setCurrentIndex(model.index(0, 0))
        else:
            for widget in [self.edtPerson, self.edtSetDate,
                           self.edtExecDate, self.tblAPProps
                           ]:
                widget.setEnabled(False)

    def updatePrintButton(self, actionType):
        context = actionType.context if actionType else ''
        customizePrintButton(self.btnAPPrint, context, self.eventEditor.isDirty() or not self.eventEditor.itemId())

    # Получение частоты использования услуги в стандарте
    def getNecessityByAction(self, actionType, mesId):
        stmt = u'''
        SELECT DISTINCT
            ms.necessity AS necessity
        FROM
            ActionType_Service ats
            INNER JOIN rbService rbS ON rbS.id = ats.service_id
            INNER JOIN mes.mrbService mrbS ON mrbS.name = rbS.name
            INNER JOIN mes.MES_service ms ON ms.service_id = mrbS.id
        WHERE
            ats.master_id = %s AND ms.master_id = %s
        '''
        query = self.db.query(stmt % (actionType, mesId))

        nes = 0
        while query.next():
            record = query.record()
            nes = forceString(record.value('necessity'))
        return nes

    #Получения обязательных медикаментов в стандарте
    def getMedicamentNecessity(self, actionType, mesId):
        stmt = u'''
        SELECT DISTINCT
            mm.necessity AS necessity
        FROM
            ActionType_Medicament atm
            INNER JOIN rbMedicaments rbM ON rbM.id = atm.medicament_id
            INNER JOIN mes.mrbMedicament mrbM ON mrbM.name = rbM.name
            INNER JOIN mes.MES_medicament mm ON mm.medicamentCode = mrbM.code
        WHERE
            atm.master_id = %s AND mm.master_id = %s
        '''
        query = self.db.query(stmt % (actionType, mesId))

        nes = 0
        while query.next():
            record = query.record()
            nes = forceString(record.value('necessity'))
        return nes

    # Обновление таблицы пропертей
    def updatePropTable(self, action):
        pass
        # if self.eventId:
        #     tableEvent = self.db.table('Event')
        #     tableClient = self.db.table('Client')
        #     recEvent = self.db.getRecordEx(tableEvent, tableEvent['client_id'], tableEvent['id'].eq(self.eventId))
        #     if recEvent:
        #         clientId = forceInt(recEvent.value('client_id'))
        #         recClient = self.db.getRecordEx(tableClient, '*', tableClient['id'].eq(clientId))
        #         if recClient:
        #             self.tblAPProps.model().setAction(action, forceInt(recClient.value('id')), forceInt(recClient.value('sex')), None)
        #             self.tblAPProps.resizeRowsToContents()

    # Получение названия и группы услуги
    def getServiceGroup(self, action):
        if action:
            tableMrbService = self.db.table('mes.mrbService')
            tableMesServiceGroup = self.db.table('mes.mrbServiceGroup')

            tableGroup = tableMrbService.innerJoin(tableMesServiceGroup, tableMesServiceGroup['id'].eq(tableMrbService['group_id']))
            recGroup = self.db.getRecordEx(tableGroup, [tableMesServiceGroup['id'], tableMesServiceGroup['name']], tableMrbService['name'].eq(forceString(action.getType().name)))
            if recGroup:
                return forceString(recGroup.value('name'))
            else:
                return u''

    # Получение групп для стандарта
    def getMesGroups(self, mesId):
        tableMes = self.db.table('mes.MES')
        tableMesService = self.db.table('mes.MES_service')
        tableMrbService = self.db.table('mes.mrbService')

        tableServices = tableMes.innerJoin(tableMesService, tableMesService['master_id'].eq(tableMes['id']))
        tableServices = tableServices.innerJoin(tableMrbService, tableMrbService['id'].eq(tableMesService['service_id']))
        result = self.db.getDistinctIdList(tableServices, tableMrbService['group_id'], tableMes['id'].eq(mesId))
        return result

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtServiceFilter_textEdited(self, text):
        if self.mesItems:
            root = self.treeStandartList.invisibleRootItem()
            child_count = root.childCount()
            for i in range(child_count):
                itemRoot = root.child(i)
                child_count = itemRoot.childCount()
                for k in range(child_count):
                    items = itemRoot.child(k)
                    childs = items.childCount()
                    for r in range(childs):
                        item = items.child(r)
                        item.setHidden(not forceString(item.text(0)).upper()[:len(text)] == forceString(text).upper())

            model = self.tblStandart.model()
            if model.items:
                for v in model.items:
                    v.setVisible(not forceString(v[0]).upper()[:len(text)] == forceString(text).upper())

    @QtCore.pyqtSlot()
    def on_treeStandartList_itemSelectionChanged(self):
        selectedItems = self.treeStandartList.selectedItems()
        tableMes = self.db.table('mes.MES')


        if not selectedItems:
            self.treeStandartList.setItemSelected(self.currentSelection, True)
        if not self.treeStandartList.selectedItems():
            value = None
        else:
            value = self.treeStandartList.selectedItems()[0]
        self.currentSelection = value
        if value and value.parent():
            action = self.getActionByItem(value, value.parent())
            if action:
                if forceString(value.parent().text(0)) == self.getServiceGroup(action):
                    recMes = self.db.getRecordEx(tableMes, tableMes['id'], tableMes['name'].eq(value.parent().parent().text(0)))
                    if recMes:
                        for v in self.mesItems[forceInt(recMes.value('id'))]:
                            if forceString(v.getType().name) == forceString(value.text(0)):
                                setActionPropertiesColumnVisible(v.getType(), self.tblAPProps)
                                self.updatePrintButton(v.getType())
                                recClient = self.db.getRecordEx('Client', 'id, sex', 'id = %s' % QtGui.qApp.currentClientId())
                                if recClient:
                                    self.tblAPProps.model().setAction(action, forceInt(recClient.value('id')),
                                                                      forceInt(recClient.value('sex')), None)
                                self.tblAPProps.resizeRowsToContents()
                                self.updatePropTable(v)
                                if forceInt(v.getRecord().value('person_id')):
                                    self.cmbPerson.setValue(forceInt(v.getRecord().value('person_id')))
                                else:
                                    self.cmbPerson.setCurrentIndex(0)
                                if forceString(v.getRecord().value('begDate')):
                                    self.edtSetDate.setDate(forceDate(v.getRecord().value('begDate')))
                                else:
                                    self.edtSetDate.setDate(QtCore.QDate())
                                if forceString(v.getRecord().value('endDate')):
                                    self.edtExecDate.setDate(forceDate(v.getRecord().value('endDate')))
                                else:
                                    self.edtExecDate.setDate(QtCore.QDate())
        else:
            recMes = self.db.getRecordEx(tableMes, tableMes['id'], tableMes['name'].eq(value.text(0)))
            if recMes:
                self.modelBaseTableModel.items = []
                self.modelBaseTableModel.reset()
                servList = []
                for v in self.mesItems[forceInt(recMes.value('id'))]:
                    if not self.getNecessityByAction(v.getType().id, forceInt(recMes.value('id'))) == u'1':
                        servList.append(v)
                if servList:
                    self.modelBaseTableModel.loadData(servList)

    def getActionByItem(self, item, parent):
        for k in self.mesItems.keys():
            for v in self.mesItems[k]:
                if forceString(v.getType().name) == forceString(item.text(0)):
                    if parent:
                        idx = 0
                        tmpActList = []
                        index = parent.indexOfChild(item) - idx
                        if index >= 0:
                            while forceString(parent.child(index).text(0)) == forceString(forceString(item.text(0))) and parent.indexOfChild(item) - idx >= 0:
                                idx += 1
                                index = parent.indexOfChild(item) - idx
                                if index < 0:
                                    break

                            for i in self.mesItems[k]:
                                if forceString(i.getType().name) == forceString(item.text(0)):
                                    tmpActList.append(i)

                            if tmpActList:
                                return tmpActList[idx - 1]
                            else:
                                return v
                        else:
                            return v
                    else:
                        return v

    # Процент выполнения
    def calcDone(self):
        root = self.treeStandartList.invisibleRootItem()
        for v in range(root.childCount()):
            items = 0.0
            countDone = 0.0
            itemRoot = root.child(v)
            for i in range(itemRoot.childCount()):
                groupItems = 0.0
                doneGroupItems = 0.0
                itemService = itemRoot.child(i)
                for k in range(itemService.childCount()):
                    groupItems += 1
                    items += 1
                    item = itemService.child(k)
                    if item.checkState(2) and not forceString(item.parent().text(0)) == u'Медикаменты':
                        doneGroupItems += 1
                        countDone += 1
                    if doneGroupItems:
                        groupProcent = (doneGroupItems / groupItems) * 100
                        itemService.setText(3, forceString(round(groupProcent)))
                    else:
                        itemService.setText(3, u'0')
            if countDone:
                procent = (countDone / items) * 100
                itemRoot.setText(3, forceString(round(procent)))
            else:
                itemRoot.setText(3, u'0')

    def changeMes(self):
        if not self.cmbMes.value() in self.mesItems.keys():
            self.treeStandartList.setEnabled(False)
            newMes = MesItem(forceInt(self.cmbMes.value()), self.actionsModel)
            newServicesList = newMes.getActionsRecords()
            tmpMesItems = {}
            for k in self.mesItems.keys():
                for v in self.mesItems[k]:
                    for i in newServicesList:
                        if i.getType().id == v.getType().id and not forceString(i.getRecord().value('MES_id')) == forceString(v.getRecord().value('MES_id')):
                            v.getRecord().setValue('MES_id', toVariant(forceInt(self.cmbMes.value())))
                            newServicesList[newServicesList.index(i)] = v
            tmpMesItems[forceInt(self.cmbMes.value())] = newServicesList
            for k in self.mesItems.keys():
                for v in self.mesItems[k]:
                    if not v in tmpMesItems[forceInt(self.cmbMes.value())]:
                        v.getRecord().setValue('MES_id', toVariant(None))
                        self.oldMesServices.append(v)
            self.mesItems.clear()
            self.mesItems = tmpMesItems
            self.treeStandartList.clear()
            self.updateMesTree()
            self.treeStandartList.setEnabled(True)


    @QtCore.pyqtSlot(QTreeWidgetItem, int)
    def on_treeStandartList_itemChanged(self, item, index):
        action = self.getActionByItem(item, item.parent())
        if action:
            if index == 1:
                if item.checkState(1):
                    if not forceString(action.getRecord().value('begDate')):
                        action.getRecord().setValue('begDate', toVariant(QtCore.QDate.currentDate()))
                        action.getRecord().setValue('person_id', toVariant(QtGui.qApp.userId))
                        self.cmbPerson.setValue(QtGui.qApp.userId)
                        self.edtSetDate.setDate(QtCore.QDate.currentDate())
                        item.setBackground(0, QtGui.QBrush(QtGui.QColor(255, 128, 0)))
                        if not action in self.actionsModel.items():
                            self.actionsModel.addAction(action)
                else:
                    action.getRecord().setValue('begDate', toVariant(None))
                    item.setBackground(0, QtGui.QBrush(QtCore.Qt.white))
                    if item.checkState(2):
                        action.getRecord().setValue('endDate', toVariant(None))
                        item.setCheckState(2, QtCore.Qt.Unchecked)
            if index == 2:
                if item.checkState(2):
                    if not forceString(action.getRecord().value('endDate')):
                        action.getRecord().setValue('endDate', toVariant(QtCore.QDate.currentDate()))
                        action.getRecord().setValue('person_id', toVariant(QtGui.qApp.userId))
                        self.cmbPerson.setValue(QtGui.qApp.userId)
                        self.edtExecDate.setDate(QtCore.QDate.currentDate())
                        item.setBackground(0, QtGui.QBrush(QtCore.Qt.green))
                        if not item.checkState(1):
                            if not forceString(action.getRecord().value('begDate')):
                                action.getRecord().setValue('begDate', toVariant(QtCore.QDate.currentDate()))
                                action.getRecord().setValue('person_id', toVariant(QtGui.qApp.userId))
                                self.cmbPerson.setValue(QtGui.qApp.userId)
                                self.edtSetDate.setDate(QtCore.QDate.currentDate())
                                if not action in self.actionsModel.items():
                                    self.actionsModel.addAction(action)
                            item.setCheckState(1, QtCore.Qt.Checked)
                        self.calcDone()
                elif item.checkState(1):
                    action.getRecord().setValue('endDate', toVariant(None))
                    item.setBackground(0, QtGui.QBrush(QtGui.QColor(255, 128, 0)))
                else:
                    action.getRecord().setValue('endDate', toVariant(None))
                    item.setBackground(0, QtGui.QBrush(QtCore.Qt.white))

    @QtCore.pyqtSlot()
    def on_btnAdd_clicked(self):
        tableMes = self.db.table('mes.MES')
        tableMesServices = self.db.table('mes.mrbServiceGroup')
        mesId = self.cmbMes.value()
        if forceBool(mesId):
            if self.mesItems:
                if QtGui.QMessageBox.warning(self,
                                          u'Внимание!',
                                          u'Заменить стандарт?\n',
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    self.changeMes()
            else:
                if forceBool(mesId):
                    rootItem = QTreeWidgetItem()
                    rootItem.setText(0, forceString(self.db.translate(tableMes, tableMes['id'], forceInt(mesId), 'name')))
                    rootItem.setText(3, forceString(0))

                    self.treeStandartList.addTopLevelItem(rootItem)
                    recMes = self.db.getRecordEx(tableMes, '*', tableMes['id'].eq(self.cmbMes.value()))
                    if recMes:
                        mes = MesItem(forceInt(recMes.value('id')), self.actionsModel)
                        self.mesItems[forceInt(recMes.value('id'))] = mes.getActionsRecords()

                        for k in self.mesItems.keys():
                            servicesList = self.mesItems[k]
                            groupsList = self.getMesGroups(k)
                            for i in groupsList:
                                if i:
                                    serviceItem = QTreeWidgetItem(rootItem)
                                    serviceItem.setText(0, forceString(
                                        self.db.translate(tableMesServices, tableMesServices['id'], forceInt(i),
                                                          tableMesServices['name'])))
                                    for v in servicesList:
                                        if self.getNecessityByAction(v.getType().id, k) == u'1' and not forceString(v.getType().name) == u'medicament':
                                            if forceString(serviceItem.text(0)) == forceString(self.getServiceGroup(v)):
                                                childItem = QTreeWidgetItem(serviceItem)
                                                childItem.setText(0, forceString(v.getType().name))
                                                childItem.setFlags(childItem.flags() | QtCore.Qt.ItemIsUserCheckable)
                                                childItem.setCheckState(1, QtCore.Qt.Unchecked)
                                                childItem.setCheckState(2, QtCore.Qt.Unchecked)
                                else:
                                    serviceItem = QTreeWidgetItem(rootItem)
                                    serviceItem.setText(0, u'Услуги без группы')
                                    for v in servicesList:
                                        if self.getNecessityByAction(v.getType().id, k) == u'1' and not forceString(v.getType().name) == u'medicament':
                                            if not forceString(self.getServiceGroup(v)):
                                                childItem = QTreeWidgetItem(serviceItem)
                                                childItem.setText(0, forceString(v.getType().name))
                                                childItem.setFlags(childItem.flags() | QtCore.Qt.ItemIsUserCheckable)
                                                childItem.setCheckState(1, QtCore.Qt.Unchecked)
                                                childItem.setCheckState(2, QtCore.Qt.Unchecked)

                        medicalItem = QTreeWidgetItem(rootItem)
                        medicalItem.setText(0, u'Медикаменты')
                        for k in self.mesItems.keys():
                            servicesList = self.mesItems[k]
                            for v in servicesList:
                                if self.getMedicamentNecessity(v.getType().id, k) == u'1' and forceString(v.getType().code) == u'medicament':
                                    childItem = QTreeWidgetItem(medicalItem)
                                    childItem.setText(0, forceString(v.getType().name))
                                    childItem.setFlags(childItem.flags() | QtCore.Qt.ItemIsUserCheckable)
                                    childItem.setCheckState(1, QtCore.Qt.Unchecked)
                                    childItem.setCheckState(2, QtCore.Qt.Unchecked)
                        self.treeStandartList.expandAll()
                        self.btnAdd.setText(u'Заменить')
                self.calcDone()

    # Сохранение размера таблиц
    def getTablePrefs(self):
        if hasattr(self, '_dicTag') and self._dicTag:
            checkList = {}
            setPref(checkList, 'treeCol1', self.treeStandartList.columnWidth(0))
            setPref(checkList, 'treeCol2', self.treeStandartList.columnWidth(1))
            setPref(checkList, 'treeCol3', self.treeStandartList.columnWidth(2))
            preferences = {}
            setPref(preferences, forceString(self._dicTag), checkList)
            setPref(QtGui.qApp.preferences.windowPrefs, 'PageStandarts', preferences)

    def setTablePrefs(self, dicTag):
        self._dicTag = dicTag
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'PageStandarts', {})
        checkList = getPref(preferences, forceString(self._dicTag), {})
        if checkList:
            self.treeStandartList.setColumnWidth(0, getPrefInt(checkList, 'treeCol1', 0))
            self.treeStandartList.setColumnWidth(1, getPrefInt(checkList, 'treeCol2', 0))
            self.treeStandartList.setColumnWidth(2, getPrefInt(checkList, 'treeCol3', 0))

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_tblStandart_currentChanged(self, index, index2):
        pass

    @QtCore.pyqtSlot()
    def on_printSelected_triggered(self):
        items = self.treeStandartList.selectedItems()
        actionsDict = {}
        for item in items:
            if item.parent():
                action = self.getActionByItem(item, item.parent())
                if action:
                    actionsDict[action.getType().id] = {'name': action.getType().name,
                                           'actionData': [(action.getType().id, forceDate(action.getRecord().value('directionDate')))],
                                           'templates': getPrintTemplates(action.getType().context)
                                           }
        dlg = CActionTemplatePrintWidget()
        self.connect(dlg, QtCore.SIGNAL('printActionTemplateList'), self.on_printActionTemplateList)
        dlg.setItems(actionsDict, False, forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'groupPrintWithoutDialog', QtCore.QVariant())))
        if dlg.model._items:
            dlg.exec_()
        else:
            dlg.printOnly()

    def on_printActionTemplateList(self, list):
        self.emit(QtCore.SIGNAL('printActionTemplateList'), list)

class CStandartsPage(CFastStandartsPage):
    def __init__(self, parent=None):
        CFastStandartsPage.__init__(self, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        self.setupUiMini(self)
        self.setupUi(self)
        self.postSetupUiMini()
        self.postSetupUi()

class CBaseServiceModel(QtCore.QAbstractTableModel):
    headerText = [u'Наименование', u'Назначено', u'Выполнено']

    def __init__(self,  parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._cols = []
        self.items = []
        self.actions = []

    def cols(self):
        self._cols = [CCol(u'Наименование', ['name'], 15, 'l'),
                      CBoolCol(u'Назначено', ['begDate'], 15),
                      CBoolCol(u'Выполнено', ['endDate'], 15)
                      ]
        return self._cols

    def columnCount(self, index=QtCore.QModelIndex()):
        return 3

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items)

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        actionItem = self.actions[row]
        if index.column() == 0 and role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column])
        if index.column() == 1 and role == QtCore.Qt.CheckStateRole:
            if actionItem and forceString(actionItem.getRecord().value('begDate')):
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.Unchecked
        if index.column() == 2 and role == QtCore.Qt.CheckStateRole:
            if actionItem and forceString(actionItem.getRecord().value('endDate')):
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.Unchecked
        return QtCore.QVariant()

    def loadData(self, actionList):
        self.actions = []
        self.actions = actionList
        for v in actionList:
            serviceName = forceString(v.getType().name)
            if serviceName:
                item = [serviceName
                        ]
                self.items.append(item)
        self.reset()

    def setData(self,index,value,role=QtCore.Qt.EditRole):
        if index.isValid():
            actionItem = self.actions[index.row()]
            if index.column() == 1 and role == QtCore.Qt.CheckStateRole:
                if value == QtCore.Qt.Checked:
                    actionItem.getRecord().setValue('begDate', toVariant(QtCore.QDate.currentDate()))
                    return True
                elif value == QtCore.Qt.Unchecked:
                    actionItem.getRecord().setValue('begDate', toVariant(None))
                    return True
            elif index.column() == 2 and role == QtCore.Qt.CheckStateRole:
                if value == QtCore.Qt.Checked:
                    actionItem.getRecord().setValue('endDate', toVariant(QtCore.QDate.currentDate()))
                    return True
                elif value == QtCore.Qt.Unchecked:
                    actionItem.getRecord().setValue('endDate', toVariant(None))
                    return True


# Стандарт
class MesItem():
    def __init__(self, mesId=None, actionsModel = None):
        self.db = QtGui.qApp.db
        self.actionsList = []
        self.mesId = mesId
        self.actionModel = actionsModel

    # Получение списка всех услуг для стандарта
    def getActionsRecords(self):
        stmt = u'''
        SELECT DISTINCT
            ms.master_id AS mesId,
            ms.averageQnt AS qnt,
            rbS.id AS serviceId,
            rbS.name AS name,
            rbS.code AS code,
            ms.necessity AS necessity,
            at.id AS actionTypeId
        FROM
            mes.MES_service ms
            INNER JOIN mes.mrbService mrbS ON mrbS.id = ms.service_id
            INNER JOIN rbService rbS ON rbS.name = mrbS.name
            INNER JOIN ActionType_Service ats ON ats.service_id = rbS.id
            INNER JOIN ActionType at ON at.id = ats.master_id AND at.deleted = 0
        WHERE ms.master_id = %s GROUP BY ats.service_id
        '''
        query = self.db.query(stmt % self.mesId)

        while query.next():
            record = query.record()
            for v in xrange(forceInt(record.value('qnt'))):
                tableAction = self.db.table('Action')
                action = CAction.createByTypeId(forceInt(record.value('actionTypeId')))
                recAction = tableAction.newRecord()
                recAction.setValue('status', toVariant(2))
                recAction.setValue('actionType_id', toVariant(action.getType().id))
                recAction.setValue('deleted', toVariant(0))
                recAction.setValue('MES_id', toVariant(self.mesId))
                recAction.setValue('directionDate', toVariant(QtCore.QDateTime.currentDateTime()))
                action.setRecord(recAction)
                self.actionsList.append(action)

        #Получение списка медикаментов
        stmt = u'''
        SELECT DISTINCT
            mm.master_id AS mesId,
            mm.averageQnt AS qnt,
            rbM.id AS serviceId,
            rbM.name AS name,
            rbM.code AS code,
            mm.necessity AS necessity,
            atm.master_id AS actionTypeId
        FROM
            mes.MES_medicament mm
            INNER JOIN mes.mrbMedicament mrbM ON mrbM.code = mm.medicamentCode
            INNER JOIN rbMedicaments rbM ON rbM.name = mrbM.name
            INNER JOIN ActionType_Medicament atm ON atm.medicament_id = rbM.id
            INNER JOIN ActionType at ON at.name = rbM.name AND at.deleted =0
        WHERE mm.master_id = %s
        '''
        query = self.db.query(stmt % self.mesId)

        while query.next():
            record = query.record()
            for v in range(forceInt(record.value('qnt'))):
                tableAction = self.db.table('Action')
                action = CAction.createByTypeId(forceInt(record.value('actionTypeId')))
                recAction = tableAction.newRecord()
                recAction.setValue('status', toVariant(2))
                recAction.setValue('actionType_id', toVariant(action.getType().id))
                recAction.setValue('deleted', toVariant(0))
                recAction.setValue('MES_id', toVariant(self.mesId))
                recAction.setValue('directionDate', toVariant(QtCore.QDateTime.currentDateTime()))
                action.setRecord(recAction)
                self.actionsList.append(action)

        return self.actionsList


    def getActionsList(self):
        return self.actionsList

# Класс для поиска евентов (фильтр в картотеке)
class CFindMesEventsInfo():
    def __init__(self):
        self.db = QtGui.qApp.db
        self.tableMes = self.db.table('mes.MES')
        self.tableMesService = self.db.table('mes.MES_service')
        self.tableEvents = self.db.table('Event')
        self.tableAction = self.db.table('Action')
        self.doneEvents = []
        self.inProgressEvents = []

    def getMesEvents(self):
        tableStmt = self.tableEvents.innerJoin(self.tableAction, [self.tableAction['event_id'].eq(self.tableEvents['id']), self.tableAction['MES_id'].isNotNull(), self.tableAction['endDate'].isNotNull()])
        tableStmt = tableStmt.innerJoin(self.tableMes, self.tableMes['id'].eq(self.tableAction['MES_id']))
        tableStmt = tableStmt.innerJoin(self.tableMesService, [self.tableMesService['master_id'].eq(self.tableMes['id']), self.tableMesService['necessity'].eq(1)])
        eventsList = self.db.getDistinctIdList(tableStmt, self.tableEvents['id'], self.tableEvents['deleted'].eq(0))
        return eventsList

    def getEvents(self):
        events = self.getMesEvents()
        for v in events:
            mesList = []
            recMesList = self.db.getIdList(self.tableAction, self.tableAction['MES_id'], [self.tableAction['event_id'].eq(v),
                                                                                self.tableAction['deleted'].eq(0),
                                                                                self.tableAction['MES_id'].isNotNull()])
            if recMesList:
                for k in recMesList:
                    if not k in mesList:
                        mesList.append(k)

            for k in mesList:
                tableServices = self.tableAction.innerJoin(self.tableMes, self.tableMes['id'].eq(self.tableAction['MES_id']))
                tableServices = tableServices.innerJoin(self.tableMesService, [self.tableMesService['master_id'].eq(self.tableMes['id']), self.tableMesService['necessity'].eq(1)])
                actions = 0
                doneAction = 0
                recActions = self.db.getDistinctIdList(tableServices, self.tableAction['id'], [self.tableAction['event_id'].eq(v),
                                                                                self.tableAction['deleted'].eq(0),
                                                                                self.tableAction['MES_id'].eq(k)])
                recDoneActions = self.db.getDistinctIdList(tableServices, self.tableAction['id'], [self.tableAction['event_id'].eq(v),
                                                                                    self.tableAction['deleted'].eq(0),
                                                                                    self.tableAction['MES_id'].eq(k),
                                                                                    self.tableAction['endDate'].isNotNull()])

                actions += len(recActions)
                doneAction += len(recDoneActions) + 1
                if actions == doneAction:
                    self.doneEvents.append(v)
                else:
                    self.inProgressEvents.append(v)

    def getDoneEvents(self):
        return self.doneEvents

    def getInProgessEvents(self):
        return self.inProgressEvents