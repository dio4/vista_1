# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Action import CAction, CActionType
from Events.ActionInfo import CCookedActionInfo
from Events.ActionPropertiesTable import CExActionPropertiesTableModel
from Events.ActionTemplateChoose import CActionTemplateChooseButton
from Events.ActionTemplateSaveDialog import CActionTemplateSaveDialog
from Events.EventInfo import CEventInfo
from Events.ExecTimeNextActionDialog import CExecTimeNextActionDialog
from Events.ExecutionPlanDialog import CGetExecutionPlan
from Events.Utils import CActionTemplateCache, checkTissueJournalStatusByActions, getEventLengthDays, \
    setActionPropertiesColumnVisible, validCalculatorSettings
from Orgs.Orgs import selectOrganisation
from Registry.ClientEditDialog import CClientEditDialog
from Registry.Utils import formatClientBanner, getClientInfo
from Resources.JobTicketReserveMixin import CJobTicketReserveMixin
from Ui_ActionEditDialog import Ui_ActionDialog
from Users.Rights import urAdmin, urCopyPrevAction, urLoadActionTemplate, urRegTabWriteRegistry, urSaveActionTemplate
from library.ItemsListDialog import CItemEditorBaseDialog
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, customizePrintButton, getPrintButton
from library.Utils import calcAgeTuple, forceDate, forceDateTime, forceInt, forceRef, forceString, formatName, pyDate, \
    toVariant
from library.interchange import getComboBoxValue, getDatetimeEditValue, getDoubleBoxValue, getLineEditValue, \
    getRBComboBoxValue, setCheckBoxValue, setComboBoxValue, setDatetimeEditValue, \
    setDoubleBoxValue, setLabelText, setLineEditValue, setRBComboBoxValue


class CActionEditDialog(CItemEditorBaseDialog, Ui_ActionDialog, CJobTicketReserveMixin):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Action')
        CJobTicketReserveMixin.__init__(self)
        self.eventId = None
        self.eventTypeId = None
        self.clientId = None
        self.forceClientId = None
        self.clientSex = None
        self.clientAge = None
        self.personId = None
        self.personSpecialityId = None
        self.newActionId = None
        self.clientInfo = None
        self._mainWindowState = QtGui.qApp.mainWindow.windowState()

        self.addModels('ActionProperties', CExActionPropertiesTableModel(self))

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)

        self.actEditClient.setObjectName('actEditClient')
        self.btnPrint = getPrintButton(self, '')
        self.btnPrint.setObjectName('btnPrint')
        self.btnLoadTemplate = CActionTemplateChooseButton(self)
        self.btnLoadTemplate.setObjectName('btnLoadTemplate')
        self.btnLoadTemplate.setText(u'Загрузить шаблон')
        self.btnSaveAsTemplate = QtGui.QPushButton(u'Сохранить шаблон', self)
        self.btnSaveAsTemplate.setObjectName('btnSaveAsTemplate')
        self.setupUi(self)
        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbStatus.clear()
        self.cmbStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Мероприятие')
        self.edtDirectionDate.canBeEmpty(True)
        self.edtEndDate.canBeEmpty(True)
        self.edtBegDate.canBeEmpty(True)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnLoadTemplate, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnSaveAsTemplate, QtGui.QDialogButtonBox.ActionRole)
        self.setModelsEx(self.tblProps, self.modelActionProperties, self.selectionModelActionProperties)
        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.actEditClient.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))

        self.setupDirtyCather()
        self.setIsDirty(False)

        self.actionTemplateCache = CActionTemplateCache(self)

        action = QtGui.QAction(self)
        self.actSetLaboratoryCalculatorInfo = action
        self.actSetLaboratoryCalculatorInfo.setObjectName('actSetLaboratoryCalculatorInfo')
        action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F3))
        self.addAction(action)
        self.connect(self.actSetLaboratoryCalculatorInfo, QtCore.SIGNAL('triggered()'),
                     self.on_actSetLaboratoryCalculatorInfo)
        self.connect(self.btnCloseWidgets, QtCore.SIGNAL('arrowTypeChanged(bool)'), self.on_arrowTypeChanged)
        self.setVisibleBtnCloseWidgets(False)
        self._canUseLaboratoryCalculatorPropertyTypeList = None

    def on_arrowTypeChanged(self, value):
        self.frmWidgets.setVisible(value)

    def setVisibleBtnCloseWidgets(self, value):
        self.btnCloseWidgets.setVisible(value)
        if value:
            self.btnCloseWidgets.applayArrow()

    def setReduced(self, value):
        self.txtClientInfoBrowser.setVisible(not value)
        if self.clientInfo is None:
            self.clientInfo = getClientInfo(self.clientId)
        name = formatName(self.clientInfo.lastName, self.clientInfo.firstName, self.clientInfo.patrName)
        self.setWindowTitle(self.windowTitle() + ' : ' + name)
        self.setVisibleBtnCloseWidgets(value)

    def exec_(self):
        QtGui.qApp.setJTR(self)
        result = CItemEditorBaseDialog.exec_(self)
        try:
            if not result:
                self.delAllJobTicketReservations()
        except:
            QtGui.qApp.logCurrentException()
        QtGui.qApp.setJTR(None)
        QtGui.qApp.disconnectClipboard()
        return result

    def setForceClientId(self, clientId):
        self.forceClientId = clientId

    def checkNeedLaboratoryCalculator(self, propertyTypeList, clipboardSlot):
        actualPropertyTypeList = [
            propType for propType in propertyTypeList if validCalculatorSettings(propType.laboratoryCalculator)
        ]
        if actualPropertyTypeList:
            QtGui.qApp.connectClipboard(clipboardSlot)
        else:
            QtGui.qApp.disconnectClipboard()
        return actualPropertyTypeList

    @QtCore.pyqtSlot()
    def on_btnPlanNextAction_clicked(self):
        record = self.getRecord()
        if record:
            dialog = CGetExecutionPlan(self, record, self.action.getExecutionPlan())
            dialog.exec_()
            self.action.setExecutionPlan(dialog.model.executionPlan)

    @QtCore.pyqtSlot()
    def on_btnNextAction_clicked(self):
        if self.cmbStatus.currentIndex() == 3:
            currentDateTime = QtCore.QDateTime.currentDateTime()
            db = QtGui.qApp.db
            table = db.table('vrbPersonWithSpeciality')
            personId = QtGui.qApp.userId if (
            QtGui.qApp.userId and QtGui.qApp.userSpecialityId) else self.cmbSetPerson.value()
            record = db.getRecordEx(table, [table['name']], [table['id'].eq(personId)]) if personId else None
            personName = forceString(record.value('name')) if record else ''
            self.edtNote.setText('Отменить: %s %s' % (currentDateTime.toString('dd-MM-yyyy hh:mm'), personName))
        else:
            self.newActionId = None
            prevRecord = self.getRecord()
            if prevRecord:
                actionTypeId = forceRef(prevRecord.value('actionType_id')) if prevRecord else None
                duration = self.edtDuration.value()
                aliquoticity = self.edtAliquoticity.value()
                if duration >= 1 or aliquoticity > 1:
                    recordList = {}
                    periodicity = self.edtPeriodicity.value()
                    if aliquoticity and actionTypeId:
                        db = QtGui.qApp.db
                        tableAction = db.table('Action')
                        eventId = forceRef(prevRecord.value('event_id'))
                        actionId = forceRef(prevRecord.value('id'))
                        directionDate = forceDateTime(prevRecord.value('directionDate'))
                        setPersonId = forceRef(prevRecord.value('setPerson_id'))
                        if eventId:
                            cond = [
                                tableAction['deleted'].eq(0),
                                tableAction['actionType_id'].eq(actionTypeId),
                                tableAction['event_id'].eq(eventId),
                                tableAction['directionDate'].eq(directionDate),
                                tableAction['setPerson_id'].eq(setPersonId)
                            ]
                            for recordOld in db.iterRecordList(
                                    tableAction, tableAction['*'], cond, tableAction['begDate']
                            ):
                                id = forceRef(recordOld.value('id'))
                                begDateOld = forceDateTime(recordOld.value('begDate'))
                                recordList[(id, begDateOld)] = recordOld
                            keysList = recordList.keys()
                            keysList.sort()
                            keyList = keysList[-1]
                            quoticity = 0
                            if aliquoticity > 1:
                                for key in recordList.keys():
                                    if key[1].date() == keyList[1].date():
                                        quoticity += 1
                            if duration >= 1 or (aliquoticity > 1 and aliquoticity > quoticity):
                                lastRecord = recordList.get(keyList, None)
                                newRecordAction = False
                                if lastRecord:
                                    prevActionId = forceRef(lastRecord.value('id'))
                                    if actionId == prevActionId:
                                        begDate = forceDateTime(prevRecord.value('begDate'))
                                        if QtGui.qApp.userId and QtGui.qApp.userSpecialityId:
                                            execPersonId = QtGui.qApp.userId
                                        else:
                                            execPersonId = self.cmbSetPerson.value()
                                        dialog = CExecTimeNextActionDialog(self, begDate, execPersonId)
                                        if dialog.exec_():
                                            execTime = dialog.getExecTime()
                                            execPersonId = dialog.getExecPersonId()
                                            specifiedName = forceString(prevRecord.value('specifiedName'))
                                            prevRecord.setValue('person_id', toVariant(execPersonId))
                                            executionPlan = self.action.getExecutionPlan()
                                            executionPlanKeys = executionPlan.keys()
                                            executionPlanKeys.sort()
                                            executionPlanBegDate = executionPlan.get(pyDate(begDate.date()), {})
                                            if not executionPlanBegDate:
                                                for keyDate in executionPlanKeys:
                                                    executionPlanTimes = executionPlan.get(keyDate, {})
                                                    aliquoticityNew = len(executionPlanTimes)
                                                    if aliquoticityNew:
                                                        executionPlanTimeKeys = executionPlanTimes.keys()
                                                        executionPlanTimeKeys.sort()
                                                        aliquoticity = aliquoticityNew
                                                        begDateDate = begDate.date()
                                                        durationNew = duration - begDateDate.daysTo(
                                                            QtCore.QDate(keyDate))
                                                        duration = durationNew
                                                        begDate = QtCore.QDateTime(QtCore.QDate(keyDate),
                                                                                   executionPlanTimeKeys[0])
                                                        break
                                            else:
                                                executionPlanBegDateKeys = executionPlanBegDate.keys()
                                                executionPlanBegDateKeys.sort()
                                                begTime = executionPlanBegDateKeys[0]
                                                executionPlanKeys = executionPlan.keys()
                                                executionPlanKeys.sort()
                                                if QtCore.QDate(executionPlanKeys[0]) == begDate.date():
                                                    aliquoticity = len(executionPlanBegDateKeys)
                                                    newBegDate = begDate.date().addDays(1)
                                                    maxBegDate = executionPlanKeys[len(executionPlanKeys) - 1]
                                                    while newBegDate <= maxBegDate:
                                                        periodicityPlanTimes = executionPlan.get(pyDate(newBegDate), {})
                                                        if len(periodicityPlanTimes):
                                                            periodicity = begDate.date().daysTo(newBegDate) - 1
                                                            break
                                                        else:
                                                            newBegDate = newBegDate.addDays(1)
                                                    if periodicity < 0:
                                                        periodicity = 0
                                                begDate = QtCore.QDateTime(begDate.date(), begTime)
                                            prevRecord.setValue('aliquoticity', toVariant(aliquoticity))
                                            prevRecord.setValue('begDate', toVariant(begDate))
                                            prevRecord.setValue('endDate',
                                                                toVariant(QtCore.QDateTime(begDate.date(), execTime)))
                                            prevRecord.setValue('status', toVariant(2))
                                            prevRecord.setValue('plannedEndDate',
                                                                toVariant(begDate.addDays(duration - 1)))
                                            prevRecord.setValue('duration', toVariant(duration))
                                            endDate = forceDateTime(prevRecord.value('endDate'))
                                            newExecutionPlan = {}
                                            tableActionExecutionPlan = db.table('Action_ExecutionPlan')
                                            for execDate, timeList in executionPlan.items():
                                                timeListDict = {}
                                                for execTime, record in timeList.items():
                                                    if QtCore.QDateTime(QtCore.QDate(execDate), execTime) > begDate:
                                                        newExecPlanRecord = tableActionExecutionPlan.newRecord()
                                                        newExecPlanRecord.setValue('execDate',
                                                                                   toVariant(record.value('execDate')))
                                                        newExecPlanRecord.setValue('master_id', toVariant(None))
                                                        newExecPlanRecord.setValue('id', toVariant(None))
                                                        timeListDict[execTime] = newExecPlanRecord
                                                if timeListDict or QtCore.QDate(execDate) > begDate.date():
                                                    newExecutionPlan[execDate] = timeListDict
                                            begDateNew = None
                                            periodicityNew = -1
                                            if newExecutionPlan:
                                                newExecutionPlanKeys = newExecutionPlan.keys()
                                                newExecutionPlanKeys.sort()
                                                newExecTimeList = {}
                                                newExecDate = None
                                                for planKey in newExecutionPlanKeys:
                                                    newExecTimeList = newExecutionPlan.get(planKey, {})
                                                    if newExecTimeList:
                                                        newExecDate = planKey
                                                        break
                                                if newExecTimeList and newExecDate:
                                                    newExecTimeListKeys = newExecTimeList.keys()
                                                    if len(newExecTimeListKeys) > 0:
                                                        newExecTimeListKeys.sort()
                                                        newExecTime = newExecTimeListKeys[0]
                                                        begDateNew = QtCore.QDateTime(QtCore.QDate(newExecDate),
                                                                                      newExecTime)
                                                        aliquoticity = len(newExecTimeListKeys)
                                                        begDateDate = begDate.date()
                                                        periodicity = begDateDate.daysTo(begDateNew.date()) - 1
                                                        if periodicity < 0:
                                                            periodicity = 0
                                                        if begDateDate == begDateNew.date():
                                                            durationNew = duration
                                                        else:
                                                            durationNew = duration - 1 - periodicity
                                                        periodicityNew = 0
                                                        begDateNewDate = begDateNew.date()
                                                        for newExecutionKey in newExecutionPlanKeys:
                                                            newExecutionDate = QtCore.QDate(newExecutionKey)
                                                            if newExecutionDate > begDateNewDate:
                                                                periodicityNew = begDateNewDate.daysTo(
                                                                    newExecutionDate) - 1
                                                                if periodicityNew < 0:
                                                                    periodicityNew = 0
                                                                break
                                            elif aliquoticity > 1 and aliquoticity > quoticity:
                                                begDateNew = QtCore.QDateTime(endDate.date(),
                                                                              execTime if execTime else self.getCurrentTimeAction(
                                                                                  endDate))
                                                durationNew = duration
                                            else:
                                                endDateNew = endDate.addDays(periodicity + 1)
                                                begDateNew = QtCore.QDateTime(endDateNew.date(),
                                                                              execTime if execTime else  self.getCurrentTimeAction(
                                                                                  endDate))
                                                durationNew = duration - 1 - periodicity
                                            prevRecord.setValue('periodicity', toVariant(periodicity))
                                            if begDateNew and durationNew:
                                                if periodicityNew > -1:
                                                    periodicity = periodicityNew
                                                newRecord = tableAction.newRecord()
                                                newRecord.setValue('event_id', toVariant(prevRecord.value('event_id')))
                                                newRecord.setValue('begDate', toVariant(begDateNew))
                                                newRecord.setValue('status', toVariant(0))
                                                newRecord.setValue('idx', toVariant(9999))
                                                newRecord.setValue('specifiedName', toVariant(specifiedName))
                                                newRecord.setValue('duration', toVariant(durationNew))
                                                newRecord.setValue('periodicity', toVariant(periodicity))
                                                newRecord.setValue('aliquoticity', toVariant(aliquoticity))
                                                newRecord.setValue('plannedEndDate',
                                                                   toVariant(begDateNew.addDays(durationNew - 1)))
                                                newRecord.setValue('actionType_id', toVariant(actionTypeId))
                                                newRecord.setValue('directionDate',
                                                                   toVariant(prevRecord.value('directionDate')))
                                                newRecord.setValue('setPerson_id',
                                                                   toVariant(prevRecord.value('setPerson_id')))
                                                newRecord.setValue('person_id', toVariant(QtGui.qApp.userId if (
                                                QtGui.qApp.userId and QtGui.qApp.userSpecialityId) else self.cmbSetPerson.value()))
                                                newRecord.setValue('org_id', toVariant(prevRecord.value('org_id')))
                                                newRecord.setValue('amount', toVariant(prevRecord.value('amount')))
                                                newAction = CAction(record=newRecord)
                                                if newExecutionPlan:
                                                    newAction.setExecutionPlan(newExecutionPlan)
                                                if newAction:
                                                    for properties in self.action._properties:
                                                        type = properties._type
                                                        name = type.name
                                                        if (type.canChangeOnlyOwner > 0
                                                            or type.inActionsSelectionTable == 1
                                                            or type.isActionNameSpecifier
                                                            ) and name:
                                                            newAction[name] = self.action[name]
                                                    self.newActionId = newAction.save(idx=9999)
                                                newRecordAction = True
                                                self.setRecordByNext(prevRecord)
                                                self.saveData()
                                                self.close()
                                if duration == 1 and not newRecordAction:
                                    begDate = forceDateTime(prevRecord.value('begDate'))
                                    prevRecord.setValue('status', toVariant(2))
                                    endDate = forceDateTime(prevRecord.value('endDate'))
                                    if not endDate:
                                        prevRecord.setValue('endDate', toVariant(begDate))
                                    prevRecord.setValue('person_id', toVariant(QtGui.qApp.userId if (
                                    QtGui.qApp.userId and QtGui.qApp.userSpecialityId) else self.cmbSetPerson.value()))
                                    prevRecord.setValue('plannedEndDate', toVariant(begDate.addDays(duration - 1)))
                                    self.setRecordByNext(prevRecord)
                                    self.saveData()
                                    self.close()

    def getCurrentTimeAction(self, actionDate):
        currentDateTime = QtCore.QDateTime.currentDateTime()
        if currentDateTime == actionDate:
            currentTime = currentDateTime.time()
            return currentTime.addSecs(60)
        else:
            return currentDateTime.time()

    def setRecordByNext(self, record):
        oldAction = self.action
        newAction = CAction(record=record)
        CAction.copyAction(oldAction, newAction, isCopyRecordData=False)
        self.setAction(newAction)

    @QtCore.pyqtSlot(int)
    def on_edtDuration_valueChanged(self, value):
        if value > 0 and not self.edtEndDate.date():
            self.btnNextAction.setEnabled(True)
        else:
            self.btnNextAction.setEnabled(False)
        if value > 0:
            self.btnPlanNextAction.setEnabled(True)
        else:
            self.btnPlanNextAction.setEnabled(False)
        canEdit = not self.action.isLocked() if self.action else True
        self.edtDirectionDate.setEnabled(bool(not value > 0) and canEdit)
        self.edtDirectionTime.setEnabled(bool(not value > 0) and canEdit)
        self.cmbSetPerson.setEnabled(bool(not value > 0) and canEdit)
        self.edtPlannedEndDate.setEnabled(bool(not value > 0) and canEdit)
        self.edtPlannedEndTime.setEnabled(bool(not value > 0) and canEdit)
        self.edtBegDate.setEnabled(bool(not value > 0) and canEdit)
        self.edtBegTime.setEnabled(bool(not value > 0) and canEdit)
        self.edtEndDate.setEnabled(bool(not value > 0) and canEdit)
        self.edtEndTime.setEnabled(bool(not value > 0) and canEdit)
        actionType = self.action.getType()
        if actionType.defaultPlannedEndDate == CActionType.dpedBegDatePlusDuration:
            begDate = self.edtBegDate.date()
            date = begDate.addDays(value - 1) if begDate.isValid() and not value == 0 else QtCore.QDate()
            self.edtPlannedEndDate.setDate(date)

    def on_actSetLaboratoryCalculatorInfo(self):
        result = self.checkNeedLaboratoryCalculator(self.modelActionProperties.propertyTypeList,
                                                    self.on_laboratoryCalculatorClipboard)
        self._canUseLaboratoryCalculatorPropertyTypeList = result
        self.setInfoToLaboratoryCalculatorClipboard()

    def setInfoToLaboratoryCalculatorClipboard(self):
        if self._canUseLaboratoryCalculatorPropertyTypeList:
            propertyTypeList = self._canUseLaboratoryCalculatorPropertyTypeList
            actual = unicode(
                '; '.join('(' + ','.join([forceString(propType.id), propType.laboratoryCalculator, propType.name]) + ')'
                          for propType in propertyTypeList))
            mimeData = QtCore.QMimeData()
            mimeData.setData(QtGui.qApp.inputCalculatorMimeDataType,
                             QtCore.QString(actual).toUtf8())
            QtGui.qApp.clipboard().setMimeData(mimeData)
            self._mainWindowState = QtGui.qApp.mainWindow.windowState()
            QtGui.qApp.mainWindow.showMinimized()

    def on_laboratoryCalculatorClipboard(self):
        mimeData = QtGui.qApp.clipboard().mimeData()
        baData = mimeData.data(QtGui.qApp.outputCalculatorMimeDataType)
        if baData:
            QtGui.qApp.mainWindow.setWindowState(self._mainWindowState)
            data = forceString(QtCore.QString.fromUtf8(baData))
            self.modelActionProperties.setLaboratoryCalculatorData(data)

    def getClientId(self, eventId):
        if self.forceClientId:
            return self.forceClientId
        return forceRef(QtGui.qApp.db.translate('Event', 'id', eventId, 'client_id'))

    def setAction(self, action):
        self._initByAction(action)

    def _initByAction(self, action):
        self.action = action

        record = action.getRecord()
        CItemEditorBaseDialog.setRecord(self, record)
        self.eventId = forceRef(record.value('event_id'))
        self.eventTypeId = forceRef(QtGui.qApp.db.translate('Event', 'id', self.eventId, 'eventType_id'))
        self.idx = forceInt(record.value('idx'))
        self.clientId = self.getClientId(self.eventId)
        actionType = self.action.getType()
        setActionPropertiesColumnVisible(actionType, self.tblProps)
        showTime = actionType.showTime
        self.edtDirectionTime.setVisible(showTime)
        self.edtPlannedEndTime.setVisible(showTime)
        self.edtCoordTime.setVisible(showTime)
        self.edtBegTime.setVisible(showTime)
        self.edtEndTime.setVisible(showTime)
        self.lblAssistant.setVisible(actionType.hasAssistant)
        self.cmbAssistant.setVisible(actionType.hasAssistant)
        self.setWindowTitle(actionType.code + '|' + actionType.name)
        setCheckBoxValue(self.chkIsUrgent, record, 'isUrgent')
        setDatetimeEditValue(self.edtDirectionDate, self.edtDirectionTime, record, 'directionDate')
        setDatetimeEditValue(self.edtPlannedEndDate, self.edtPlannedEndTime, record, 'plannedEndDate')
        setDatetimeEditValue(self.edtCoordDate, self.edtCoordTime, record, 'coordDate')
        setLabelText(self.lblCoordText, record, 'coordText')
        setDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDate')
        setDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDate')
        setComboBoxValue(self.cmbStatus, record, 'status')
        setDoubleBoxValue(self.edtAmount, record, 'amount')
        setDoubleBoxValue(self.edtUet, record, 'uet')
        setRBComboBoxValue(self.cmbPerson, record, 'person_id')
        setRBComboBoxValue(self.cmbSetPerson, record, 'setPerson_id')
        setLineEditValue(self.edtOffice, record, 'office')
        self.cmbAssistant.setValue(self.action.getAssistantId('assistant'))
        setLineEditValue(self.edtNote, record, 'note')
        self.edtDuration.setValue(forceInt(record.value('duration')))
        self.edtPeriodicity.setValue(forceInt(record.value('periodicity')))
        self.edtAliquoticity.setValue(forceInt(record.value('aliquoticity')))

        mkbVisible = bool(actionType.defaultMKB)
        mkbEnabled = actionType.defaultMKB in [1, 2, 5]
        self.cmbMKB.setVisible(mkbVisible)
        self.lblMKB.setVisible(mkbVisible)
        self.cmbMKB.setEnabled(mkbEnabled)
        self.cmbMKB.setText(forceString(record.value('MKB')))

        morphologyMKBVisible = bool(actionType.defaultMorphology) and QtGui.qApp.defaultMorphologyMKBIsVisible()
        morphologyEnabled = actionType.defaultMorphology in [1, 2, 5]
        self.cmbMorphologyMKB.setVisible(morphologyMKBVisible)
        self.lblMorphologyMKB.setVisible(morphologyMKBVisible)
        self.cmbMorphologyMKB.setEnabled(morphologyEnabled)
        self.cmbMorphologyMKB.setText(forceString(record.value('morphologyMKB')))

        self.cmbOrg.setValue(forceRef(record.value('org_id')))
        if (self.cmbPerson.value() is None
            and actionType.defaultPersonInEditor in (CActionType.dpUndefined, CActionType.dpCurrentUser)
            and QtGui.qApp.userSpecialityId):
            self.cmbPerson.setValue(QtGui.qApp.userId)

        self.setPersonId(self.cmbPerson.value())
        self.updateClientInfo()
        self.edtAmount.setEnabled(actionType.amountEvaluation == 0)

        self.modelActionProperties.setAction(self.action, self.clientId, self.clientSex, self.clientAge)
        self.modelActionProperties.reset()
        self.tblProps.init()
        self.tblProps.resizeRowsToContents()

        context = actionType.context if actionType else ''
        customizePrintButton(self.btnPrint, context)

        if QtGui.qApp.userHasRight(urLoadActionTemplate):
            personId = forceRef(record.value('person_id'))
            actionTemplateTreeModel = self.actionTemplateCache.getModel(actionType.id,
                                                                        personId if personId else forceRef(
                                                                            record.value('setPerson_id')))
            self.btnLoadTemplate.setModel(actionTemplateTreeModel)
        else:
            self.btnLoadTemplate.setEnabled(False)
        self.btnSaveAsTemplate.setEnabled(QtGui.qApp.userHasRight(urSaveActionTemplate))
        self.edtDuration.setEnabled(
            QtGui.qApp.userHasRight(urCopyPrevAction) and bool(QtGui.qApp.userId == self.cmbSetPerson.value()) and bool(
                not self.action.getExecutionPlan()) and bool(self.cmbStatus.currentIndex() in [0, 5]) and bool(
                not self.edtEndDate.date()))
        self.edtPeriodicity.setEnabled(
            QtGui.qApp.userHasRight(urCopyPrevAction) and bool(QtGui.qApp.userId == self.cmbSetPerson.value()) and bool(
                not self.action.getExecutionPlan()) and bool(self.cmbStatus.currentIndex() in [0, 5]) and bool(
                not self.edtEndDate.date()))
        self.edtAliquoticity.setEnabled(
            QtGui.qApp.userHasRight(urCopyPrevAction) and bool(QtGui.qApp.userId == self.cmbSetPerson.value()) and bool(
                not self.action.getExecutionPlan()) and bool(self.cmbStatus.currentIndex() in [0, 5]) and bool(
                not self.edtEndDate.date()))

        canEdit = not self.action.isLocked() if self.action else True
        for widget in [self.edtPlannedEndDate, self.edtPlannedEndTime,
                       self.cmbStatus, self.edtBegDate, self.edtBegTime,
                       self.edtEndDate, self.edtEndTime,
                       self.cmbPerson, self.edtOffice,
                       self.cmbAssistant,
                       self.edtAmount, self.edtUet,
                       self.edtNote, self.cmbOrg,
                       self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
                       ]:
            widget.setEnabled(canEdit)
        if not canEdit:
            self.btnLoadTemplate.setEnabled(False)

        canEditPlannedEndDate = canEdit and actionType.defaultPlannedEndDate not in [CActionType.dpedBegDatePlusAmount,
                                                                                     CActionType.dpedBegDatePlusDuration]
        self.edtPlannedEndDate.setEnabled(canEditPlannedEndDate)
        self.edtPlannedEndTime.setEnabled(canEditPlannedEndDate)
        if self.edtDuration.value() > 0 and not self.edtEndDate.date():
            self.btnNextAction.setEnabled(True)
        else:
            self.btnNextAction.setEnabled(False)
        if self.edtDuration.value() > 0:
            self.btnPlanNextAction.setEnabled(True)
        else:
            self.btnPlanNextAction.setEnabled(False)
        self.on_edtDuration_valueChanged(forceInt(record.value('duration')))

    def setRecord(self, record):
        action = CAction(record=record)
        self._initByAction(action)

    def getRecord(self):
        record = self.record()
        showTime = self.action.getType().showTime

        getDatetimeEditValue(self.edtPlannedEndDate, self.edtPlannedEndTime, record, 'plannedEndDate', showTime)
        getDatetimeEditValue(self.edtBegDate, self.edtBegTime, record, 'begDate', showTime)
        getDatetimeEditValue(self.edtEndDate, self.edtEndTime, record, 'endDate', showTime)
        getComboBoxValue(self.cmbStatus, record, 'status')
        getDoubleBoxValue(self.edtAmount, record, 'amount')
        getDoubleBoxValue(self.edtUet, record, 'uet')
        getRBComboBoxValue(self.cmbPerson, record, 'person_id')
        getRBComboBoxValue(self.cmbSetPerson, record, 'setPerson_id')
        getLineEditValue(self.edtOffice, record, 'office')
        getLineEditValue(self.edtNote, record, 'note')
        record.setValue('MKB', QtCore.QVariant(self.cmbMKB.text()))
        record.setValue('morphologyMKB', QtCore.QVariant(self.cmbMorphologyMKB.validText()))
        record.setValue('org_id', QtCore.QVariant(self.cmbOrg.value()))
        record.setValue('duration', toVariant(self.edtDuration.value()))
        record.setValue('periodicity', toVariant(self.edtPeriodicity.value()))
        record.setValue('aliquoticity', toVariant(self.edtAliquoticity.value()))
        return record

    def on_cmbAssistant_currentIndexChanged(self, index):
        self.action.setAssistant('assistant', self.cmbAssistant.value())

    def saveInternals(self, id):
        self.action.save(self.eventId, self.idx)
        checkTissueJournalStatusByActions([(self.action.getRecord(), self.action)])

    def updateClientInfo(self):
        self.clientInfo = getClientInfo(self.clientId)
        self.txtClientInfoBrowser.setHtml(formatClientBanner(self.clientInfo))
        self.clientSex = self.clientInfo.sexCode
        self.clientBirthDate = self.clientInfo.birthDate
        self.clientAge = calcAgeTuple(self.clientBirthDate, self.edtDirectionDate.date())

    def updateAmount(self):
        def getActionLength(countRedDays):
            startDate = self.edtBegDate.date()
            stopDate = self.edtEndDate.date()
            if startDate and stopDate:
                return getEventLengthDays(startDate, stopDate, countRedDays, self.eventTypeId)
            else:
                return 0

        def setAmount(amount):
            self.edtAmount.setValue(amount)

        actionType = self.action.getType()
        if actionType.amountEvaluation == CActionType.actionLength:
            setAmount(actionType.amount * getActionLength(True))
        elif actionType.amountEvaluation == CActionType.actionLengthWithoutRedDays:
            setAmount(actionType.amount * getActionLength(False))
        elif actionType.amountEvaluation == CActionType.actionFilledProps:
            setAmount(actionType.amount * self.action.getFilledPropertiesCount())

        if actionType.defaultPlannedEndDate == CActionType.dpedBegDatePlusAmount:
            begDate = self.edtBegDate.date()
            amountValue = int(self.edtAmount.value())
            date = begDate.addDays(amountValue - 1) if (amountValue and begDate.isValid()) else QtCore.QDate()
            self.edtPlannedEndDate.setDate(date)
        elif actionType.defaultPlannedEndDate == CActionType.dpedBegDatePlusDuration:
            begDate = self.edtBegDate.date()
            durationValue = self.edtDuration.value()
            date = begDate.addDays(durationValue) if begDate.isValid() else QtCore.QDate()
            self.edtPlannedEndDate.setDate(date)

    def checkDataEntered(self):
        result = True
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        if begDate and endDate:
            result = result and (
                endDate >= begDate or self.checkValueMessage(
                    u'Дата выполнения действия %s не должна быть раньше даты начала действия % s' % (
                    forceString(endDate), forceString(begDate)), False,
                    self.edtEndDate))
        if self.eventId:
            record = QtGui.qApp.db.getRecord('Event', 'setDate, execDate', self.eventId)
            if record:
                setDate = forceDate(record.value('setDate'))
                execDate = forceDate(record.value('execDate'))
                if setDate and endDate:
                    result = result and (
                        endDate >= setDate or self.checkValueMessage(
                            u'Дата выполнения действия %s не должна быть раньше даты начала события % s' % (
                            forceString(endDate), forceString(setDate)), True,
                            self.edtEndDate))
                if execDate and endDate:
                    result = result and (
                        execDate >= endDate or self.checkValueMessage(
                            u'Дата выполнения действия %s не должна быть позже даты выполнения события % s' % (
                            forceString(endDate), forceString(execDate)), True,
                            self.edtEndDate))
                elif setDate and endDate:
                    currentDate = QtCore.QDate.currentDate()
                    if currentDate:
                        result = result and (
                            currentDate >= endDate or self.checkValueMessage(
                                u'Дата выполнения действия %s не должна быть позже текущей даты % s' % (
                                forceString(endDate), forceString(currentDate)), True,
                                self.edtEndDate))
        if not self.checkActionMorphology():
            return False
        return result

    def checkActionMorphology(self):
        if QtGui.qApp.defaultMorphologyMKBIsVisible() and (self.cmbStatus.currentIndex() in [2, 4]):
            action = self.action
            actionType = action.getType()
            defaultMorphology = actionType.defaultMorphology
            isMorphologyRequired = actionType.isMorphologyRequired
            morphologyMKB = self.cmbMorphologyMKB.text()
            if not self.cmbMorphologyMKB.isValid(morphologyMKB) and defaultMorphology > 0 and isMorphologyRequired > 0:
                if self.cmbStatus.currentIndex() == 4 and isMorphologyRequired == 2:
                    return True
                skippable = True if isMorphologyRequired == 1 else False
                message = u'Необходимо ввести корректную морфологию диагноза действия `%s`' % actionType.name
                return self.checkValueMessage(message, skippable, self.cmbMorphologyMKB)
        return True

    def setPersonId(self, personId):
        self.personId = personId
        record = QtGui.qApp.db.getRecord('Person', 'speciality_id, tariffCategory_id', self.personId)
        if record:
            self.personSpecialityId = forceRef(record.value('speciality_id'))
            self.personTariffCategoryId = forceRef(record.value('tariffCategory_id'))
        self.actionTemplateCache.reset()

    def getEventInfo(self, context):
        return None

    def setCurrentProperty(self, row, column=1):
        index = self.modelActionProperties.index(row, column)
        self.tblProps.setCurrentIndex(index)

    @QtCore.pyqtSlot()
    def on_actEditClient_triggered(self):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            dialog.load(self.clientId)
            if dialog.exec_():
                self.updateClientInfo()

    @QtCore.pyqtSlot(float)
    def on_edtAmount_valueChanged(self, value):
        actionType = self.action.getType()
        if actionType.defaultPlannedEndDate == CActionType.dpedBegDatePlusAmount:
            begDate = self.edtBegDate.date()
            amountValue = int(value)
            date = begDate.addDays(amountValue - 1) if (amountValue and begDate.isValid()) else QtCore.QDate()
            self.edtPlannedEndDate.setDate(date)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbMKB_textChanged(self, value):
        if value[-1:] == '.':
            value = value[:-1]
        diagName = forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', value, 'DiagName'))
        if diagName:
            self.lblMKBText.setText(diagName)
        else:
            self.lblMKBText.clear()
        self.cmbMorphologyMKB.setMKBFilter(self.cmbMorphologyMKB.getMKBFilter(unicode(value)))

    @QtCore.pyqtSlot()
    def on_btnSelectOrg_clicked(self):
        orgId = selectOrganisation(self, self.cmbOrg.value(), False, self.cmbOrg.filter())
        self.cmbOrg.update()
        if orgId:
            self.cmbOrg.setValue(orgId)

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self):
        self.setPersonId(self.cmbPerson.value())

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.updateAmount()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.updateAmount()
        if date:
            if self.cmbStatus.currentIndex() != 2:
                self.cmbStatus.setCurrentIndex(2)
        else:
            if self.cmbStatus.currentIndex() == 2:
                self.cmbStatus.setCurrentIndex(3)
        if self.edtDuration.value() > 0 and not self.edtEndDate.date():
            self.btnNextAction.setEnabled(True)
        else:
            self.btnNextAction.setEnabled(False)
        if self.edtDuration.value() > 0:
            self.btnPlanNextAction.setEnabled(True)
        else:
            self.btnPlanNextAction.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_cmbStatus_currentIndexChanged(self, index):
        if index in [2, 4]:
            if not self.edtEndDate.date():
                self.edtEndDate.setDate(QtCore.QDate.currentDate())
        elif index in [3]:
            self.edtEndDate.setDate(QtCore.QDate())
            if QtGui.qApp.userId and QtGui.qApp.userSpecialityId:
                self.cmbPerson.setValue(QtGui.qApp.userId)
            else:
                self.cmbPerson.setValue(self.cmbSetPerson.value())
        else:
            self.edtEndDate.setDate(QtCore.QDate())

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelActionProperties_dataChanged(self, topLeft, bottomRight):
        self.updateAmount()

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        context = CInfoContext()
        eventInfo = context.getInstance(CEventInfo, self.eventId)

        eventActions = eventInfo.actions
        eventActions._idList = [self.itemId()]
        eventActions._items = [CCookedActionInfo(context, self.getRecord(), self.action)]
        eventActions._loaded = True

        action = eventInfo.actions[0]
        action.setCurrentPropertyIndex(self.tblProps.currentIndex().row())
        data = {
            'event': eventInfo,
            'action': action,
            'client': eventInfo.client,
            'actions': eventActions,
            'currentActionIndex': 0,
            'tempInvalid': None
        }
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_btnLoadTemplate_templateSelected(self, templateId):
        if QtGui.qApp.userHasRight(urLoadActionTemplate):
            self.action.updateByTemplate(templateId)
            self.tblProps.model().reset()
            self.tblProps.resizeRowsToContents()
            self.updateAmount()

    @QtCore.pyqtSlot()
    def on_btnSaveAsTemplate_clicked(self):
        if QtGui.qApp.userHasRight(urSaveActionTemplate):
            dlg = CActionTemplateSaveDialog(self, self.getRecord(), self.action, self.clientSex, self.clientAge,
                                            self.personId, self.personSpecialityId)
            dlg.exec_()
            actionType = self.action.getType()
            self.actionTemplateCache.reset(actionType.id)
            actionTemplateTreeModel = self.actionTemplateCache.getModel(actionType.id)
            self.btnLoadTemplate.setModel(actionTemplateTreeModel)
