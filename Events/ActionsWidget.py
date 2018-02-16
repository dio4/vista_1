# coding=utf-8
from PyQt4 import QtCore, QtGui

from Events.Action import CAction, CActionType
from Events.ActionInfo import CCookedActionInfo
from Events.ActionPropertiesTable import CExActionPropertiesTableModel
from Events.ActionTemplateSaveDialog import CActionTemplateSaveDialog
from Events.ActionsSelector import selectActionTypes
from Events.Utils import CFinanceType, CActionTemplateCache, getEventContextData, setActionPropertiesColumnVisible
from Events.ActionsTreeModel import CActionsTreeModel, CActionItem
from Orgs.Utils import getRealOrgStructureId
from Ui_ActionsWidget import Ui_ActionsWidget
from Users.Rights import urLoadActionTemplate, urSaveActionTemplate, urCopyPrevAction
from library.PrintTemplates import customizePrintButton, applyTemplate
from library.Utils import forceDate, forceInt, forceRef, forceBool, forceDouble, forceString
from library.interchange import setDatetimeEditValue


class CActionsWidget(Ui_ActionsWidget, QtGui.QWidget):
    """
    Использование:
    вставить виджет в ui;
    для инициализации вызвать setEventEditor(form_instance),
    для загрузки действий события вызвать loadEvent(event_id),
    для сохранения: saveActions(event_id)
    """

    def __init__(self, parent=None):
        super(CActionsWidget, self).__init__(parent)
        self.eventEditor = parent
        self.actionTemplateCache = CActionTemplateCache(parent)

        self.setupUi(self)

        self.shcCreateAction = QtGui.QShortcut(QtCore.Qt.Key_F9, self)
        self.shcCreateAction.activated.connect(self.createActions)

        self.modelAPActions = CActionsTreeModel(self.tblAPActions)
        self.modelAPProps = CExActionPropertiesTableModel(self.tblAPProps)
        self.tblAPActions.setModel(self.modelAPActions)
        self.tblAPProps.setModel(self.modelAPProps)

        self.tblAPActions.initHeader()
        self.cmbAPStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.btnAPLoadTemplate.setModelCallback(self.getTemplatesModel)
        # self.btnAPLoadPrevAction.setMenu(self.mnuAPLoadPrevAction)

        # setup signals
        self.tblAPActions.actionSelected.connect(self.actionSelected)
        self.tblAPActions.actionDeselected.connect(self.actionDeselected)
        self.connect(self.edtAPBegDate, QtCore.SIGNAL('dateChanged(const QDate &)'), self.begDateChanged)
        self.edtAPBegTime.timeChanged.connect(self.begTimeChanged)
        self.connect(self.edtAPEndDate, QtCore.SIGNAL('dateChanged(const QDate &)'), self.endDateChanged)
        self.edtAPEndTime.timeChanged.connect(self.endTimeChanged)
        self.cmbAPPerson.currentIndexChanged.connect(self.personChanged)
        self.cmbAPSetPerson.currentIndexChanged.connect(self.setPersonChanged)
        self.cmbAPStatus.currentIndexChanged.connect(self.statusChanged)
        self.cmbMKB.editTextChanged.connect(self.mkbChanged)
        self.connect(self.btnAPLoadTemplate, QtCore.SIGNAL('templateSelected(int)'), self.loadTemplate)
        self.btnAPSaveAsTemplate.clicked.connect(self.saveTemplate)
        self.connect(self.btnAPPrint, QtCore.SIGNAL('printByTemplate(int)'), self.printByTemplate)
        self.modelAPActions.dataChanged.connect(self.actionsChanged)

    def actionsChanged(self, lt, br):
        if lt.internalPointer():
            self.actionSelected(lt.internalPointer().action())

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
        currentAction = self.currentAction()
        if currentAction:
            data = getEventContextData(self.eventEditor)
            eventInfo = data['event']
            action = CCookedActionInfo(eventInfo.context, currentAction.getRecord(), currentAction)
            action.setCurrentPropertyIndex(self.tblAPProps.currentIndex().row())
            data['action'] = action
            data['actions'] = self.tblAPActions.actions()
            data['currentActionIndex'] = 0
            applyTemplate(self.eventEditor, templateId, data)

    def loadTemplate(self, tpl_id):
        action = self.currentAction()
        if QtGui.qApp.userHasRight(urLoadActionTemplate) and action:
            action.updateByTemplate(tpl_id)
            self.tblAPProps.model().reset()
            self.tblAPProps.init()
            self.tblAPProps.resizeRowsToContents()
            # model.updateActionAmount(row)

    def saveTemplate(self):
        action = self.currentAction()
        if QtGui.qApp.userHasRight(urSaveActionTemplate) and action:
            actionRecord = action.getRecord()
            dlg = CActionTemplateSaveDialog(self, actionRecord, action, self.eventEditor.clientSex,
                                            self.eventEditor.clientAge, self.eventEditor.personId,
                                            self.eventEditor.personSpecialityId)
            dlg.exec_()
            self.actionTemplateCache.reset(action.getType().id)
            # personId = forceRef(action.getRecord().value('person_id'))
            # actionTemplateTreeModel = self.actionTemplateCache.getModel(action.getType().id,
            #                             personId if personId else forceRef(action.getRecord().value('setPerson_id')))
            # self.btnAPLoadTemplate.setModel(actionTemplateTreeModel)

    def getTemplatesModel(self):
        action = self.currentAction()
        personId = forceRef(action.getRecord().value('person_id'))
        return self.actionTemplateCache.getModel(action.getType().id,
                                                 personId if personId
                                                          else forceRef(action.getRecord().value('setPerson_id')))

    def currentAction(self):  # type: CAction
        idx = self.tblAPActions.currentIndex()
        if not idx.isValid():
            return None
        item = idx.internalPointer()
        if not isinstance(item, CActionItem):
            return None
        return item.action()

    def begDateChanged(self, date):
        time = self.edtAPBegTime.time()
        self.currentAction().getRecord().setValue('begDate', QtCore.QDateTime(date, time))
        self.eventEditor.setIsDirty()

    def begTimeChanged(self, time):
        date = self.edtAPBegDate.date()
        self.currentAction().getRecord().setValue('begDate', QtCore.QDateTime(date, time))
        self.eventEditor.setIsDirty()

    def endDateChanged(self, date):
        time = self.edtAPEndTime.time()
        self.currentAction().getRecord().setValue('endDate', QtCore.QDateTime(date, time))
        self.eventEditor.setIsDirty()

    def endTimeChanged(self, time):
        date = self.edtAPEndDate.date()
        self.currentAction().getRecord().setValue('endDate', QtCore.QDateTime(date, time))
        self.eventEditor.setIsDirty()

    def personChanged(self, idx):
        self.currentAction().getRecord().setValue('person_id', self.cmbAPPerson.value())
        self.eventEditor.setIsDirty()

    def setPersonChanged(self, idx):
        self.currentAction().getRecord().setValue('setPerson_id', self.cmbAPSetPerson.value())
        self.eventEditor.setIsDirty()

    def statusChanged(self, idx):
        self.currentAction().getRecord().setValue('status', idx)
        if idx in [2, 4, 7, 8, 9, 10, 11]:
            if not self.edtAPEndDate.date():
                now = QtCore.QDateTime().currentDateTime()
                self.edtAPEndDate.setDate(now.date())
                if self.edtAPEndTime.isVisible():
                    self.edtAPEndTime.setTime(now.time())
        elif idx in [3]:
            eventPurposeId = self.eventEditor.getEventPurposeId()
            if not forceBool(QtGui.qApp.db.translate('rbEventTypePurpose', 'id', eventPurposeId, 'federalCode = 8')):
                if QtGui.qApp.userId and QtGui.qApp.userSpecialityId:
                    self.cmbAPPerson.setValue(QtGui.qApp.userId)
                else:
                    self.cmbAPPerson.setValue(self.cmbAPSetPerson.value())
        elif idx in [1, 5, 6]:
            pass
        else:
            self.edtAPEndDate.setDate(QtCore.QDate())
        self.eventEditor.setIsDirty()

    def mkbChanged(self, val):
        self.currentAction().getRecord().setValue('MKB', self.cmbMKB.text())
        self.eventEditor.setIsDirty()

    def actionSelected(self, action):
        # toggle widgets enabled state
        self.attrsAP.setEnabled(True)
        self.tblAPProps.setEnabled(True)

        # set action to props model
        self.modelAPProps.setAction(
            action,
            self.eventEditor.clientId,
            self.eventEditor.clientSex,
            self.eventEditor.clientAge
        )
        self.tblAPProps.init()
        self.tblAPProps.resizeRowsToContents()
        setActionPropertiesColumnVisible(action.getType(), self.tblAPProps)

        # set values to top widgets
        setDatetimeEditValue(self.edtAPBegDate, self.edtAPBegTime, action.getRecord(), 'begDate')
        setDatetimeEditValue(self.edtAPEndDate, self.edtAPEndTime, action.getRecord(), 'endDate')
        if not forceDate(action.getRecord().value('endDate')).isNull() and \
                not (forceInt(action.getRecord().value('status')) in CActionType.retranslateClass(False).ignoreStatus) and \
                forceRef(action.getRecord().value('status')) is not None:
            self.cmbAPStatus.setCurrentIndex(2)
        else:
            self.cmbAPStatus.setCurrentIndex(forceInt(action.getRecord().value('status')))
        setPerson = forceRef(action.getRecord().value('setPerson_id'))
        if not setPerson:
            if u'moving' in action.getType().flatCode.lower() and self.eventEditor.prevEventId:
                setPerson = self.presetPerson
            else:
                setPerson = None
        self.cmbAPSetPerson.setValue(setPerson)
        personId = forceRef(action.getRecord().value('person_id'))
        if not personId:
            if u'moving' in action.getType().flatCode.lower() and self.eventEditor.prevEventId:
                personId = self.presetPerson
            else:
                personId = None
        self.cmbAPPerson.setValue(personId)
        self.cmbMKB.setText(forceString(action.getRecord().value('MKB')))
        self.recalculateUET()

        # setup template buttons
        if QtGui.qApp.userHasRight(urLoadActionTemplate) and action:
            self.btnAPLoadTemplate.setEnabled(True)
        else:
            self.btnAPLoadTemplate.setEnabled(False)
        self.btnAPSaveAsTemplate.setEnabled(QtGui.qApp.userHasRight(urSaveActionTemplate))
        self.btnAPLoadPrevAction.setEnabled(QtGui.qApp.userHasRight(urCopyPrevAction) and bool(action))
        self.updatePrintButton(action.getType())

    def updatePrintButton(self, actionType):
        context = actionType.context if actionType else ''
        customizePrintButton(self.btnAPPrint, context, self.eventEditor.isDirty() or not self.eventEditor.itemId())

    def actionDeselected(self):
        self.attrsAP.setEnabled(False)
        self.tblAPProps.setEnabled(False)
        self.recalculateUET()

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor
        self.modelAPActions.eventEditor = eventEditor
        self.actionTemplateCache.eventEditor = eventEditor
        self.modelAPProps.dataChanged.connect(lambda x: eventEditor.setIsDirty())

    def createActions(self):
        eventFinanceId = self.eventEditor.eventFinanceId
        financeCode = CFinanceType.getCode(eventFinanceId)
        existsActionTypesList = list(set(action.getType().id for action in self.modelAPActions.actions()))

        actionTypes = selectActionTypes(
            self.eventEditor,
            [0, 1, 2, 3],  # все классы
            self.eventEditor.clientSex, self.eventEditor.clientAge,
            getRealOrgStructureId(),
            self.eventEditor.getEventTypeId(),
            self.eventEditor.getContractId(),
            self.eventEditor.getMesId(),
            financeCode in [CFinanceType.VMI, CFinanceType.cash],
            self.eventEditor._id,
            existsActionTypesList,
            contractTariffCache=self.eventEditor.contractTariffCache,
            eventBegDate=self.eventEditor.begDate(),
            eventEndDate=self.eventEditor.endDate(),
            paymentScheme=self.eventEditor.getPaymentScheme()
        )
        self.tblAPActions.model().addItems(actionTypes)
        if actionTypes:
            self.eventEditor.setIsDirty(True)
        self.recalculateUET()

    def getActionUET(self, action):
        personId = forceRef(action.getRecord().value('person_id'))
        financeId = self.eventEditor.eventFinanceId
        contractId = self.eventEditor.getContractId()
        return forceDouble(action.getRecord().value('amount')) * self.eventEditor.getUet(action.getType().id, personId, financeId, contractId)

    def recalculateUET(self):
        total = 0
        for action in self.modelAPActions.actions():
            total += self.getActionUET(action)
        self.lblEventUET.setText(unicode(total))
        if self.currentAction():
            self.lblActionUET.setText(unicode(self.getActionUET(self.currentAction())))
        else:
            self.lblActionUET.setText(u'0.0')

    def showEvent(self, evt):
        super(CActionsWidget, self).showEvent(evt)
        self.tblAPActions.setCurrentIndex(self.tblAPActions.model().index(0, 0, self.tblAPActions.rootIndex()))

    def saveActions(self, eventId):
        self.modelAPActions.save(eventId)

    def loadEvent(self, eventId):
        self.modelAPActions.loadEvent(eventId)
        self.tblAPActions.expandAll()
        self.recalculateUET()
