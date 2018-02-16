# -*- coding: utf-8 -*-

# Просмотр списка типов событий и редактор типа событий

from PyQt4 import QtCore, QtGui

from Events.ActionTypeComboBox import CActionTypeTableCol
from Events.EditDispatcher import getEventFormList
from Events.Utils import CEventTypeDescription, getExpiredDate, EventOrder
from Orgs.OrgComboBox import CPolyclinicExtendedInDocTableCol
from RefBooks.SelectService import selectService
from RefBooks.ServiceModifier import createModifier, parseModifier
from RefBooks.Tables import rbCode, rbName, rbId, rbService
from Ui_EventTypeEditor import Ui_ItemEditorDialog
from library.AgeSelector import checkAgeSelectorSyntax
from library.AmountToWords import amountToWords
from library.InDocTable import CInDocTableModel, CInDocTableCol, CBoolInDocTableCol, CDateInDocTableCol, \
    CEnumInDocTableCol, CIntInDocTableCol, CRBInDocTableCol
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel import CBoolCol, CEnumCol, CNumCol, CRefBookCol, CTextCol
from library.Utils import forceDate, forceInt, forceRef, forceString, forceStringEx, forceTime, toVariant
from library.crbcombobox import CRBComboBox, CRBPopupView, CRBModelDataCache
from library.interchange import getCheckBoxValue, getComboBoxValue, getLineEditValue, getRBComboBoxValue, \
    getSpinBoxValue, setCheckBoxValue, setComboBoxValue, setLineEditValue, \
    setRBComboBoxValue, setSpinBoxValue

SexList = ('', u'М', u'Ж')


class CEventTypeList(CItemsListDialog):
    mimeTypeEventTypeActionsIdList = 'application/x-s11/eventtypeactionsidlist'
    mimeTypeEventTypeDiagnosticsIdList = 'application/x-s11/eventtypediagnosticsidlist'

    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CRefBookCol(u'Назначение', ['purpose_id'], 'rbEventTypePurpose', 10),
            CRefBookCol(u'Профиль', ['eventProfile_id'], 'rbEventProfile', 10),
            CRefBookCol(u'Вид помощи', ['medicalAidKind_id'], 'rbMedicalAidKind', 10),
            CRefBookCol(u'Тип помощи', ['medicalAidType_id'], 'rbMedicalAidType', 10),
            CEnumCol(u'Пол', ['sex'], SexList, 10),
            CTextCol(u'Возраст', ['age'], 10),
            CNumCol(u'Период', ['period'], 10),
            CEnumCol(u'Раз в', ['singleInPeriod'], ['', u'неделю', u'месяц', u'квартал', u'полугодие', u'год'], 10),
            CBoolCol(u'Продолжительное', ['isLong'], 10),
            CNumCol(u'Мин.длительность', ['minDuration'], 10),
            CNumCol(u'Макс.длительность', ['maxDuration'], 10),
            CRefBookCol(u'Сервис ОМС', ['service_id'], 'rbService', 10),
            CRefBookCol(u'Вид события', ['eventKind_id'], 'rbEventKind', 10),
        ], 'EventType', [rbCode, rbName, rbId])
        self.setWindowTitleEx(u'Типы событий')
        self.mimeData = QtCore.QMimeData()
        self.tblItems.setSortingEnabled(True)
        self.setupMenu()

    def setupMenu(self):
        self.actRemoveItem = QtGui.QAction(u'Удалить', self)
        self.actRemoveItem.setObjectName('actRemoveItem')
        self.actDuplicateItem = QtGui.QAction(u'Дублировать', self)
        self.actDuplicateItem.setObjectName('actDuplicateItem')
        self.actCopyPreCreateProperties = QtGui.QAction(u'Копировать определения планировщика в буфер обмена', self)
        self.actCopyPreCreateProperties.setObjectName('actCopyPreCreateProperties')
        self.actPastPreCreateProperties = QtGui.QAction(u'Вставить определения планировщика из буфера обмена', self)
        self.actPastPreCreateProperties.setObjectName('actPastPreCreateProperties')

        self.tblItems.addPopupAction(self.actDuplicateItem)
        self.tblItems.addPopupSeparator()
        self.tblItems.addPopupAction(self.actRemoveItem)
        self.tblItems.addPopupSeparator()
        self.tblItems.addPopupAction(self.actCopyPreCreateProperties)
        self.tblItems.addPopupAction(self.actPastPreCreateProperties)

        self.connect(self.tblItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.on_mnuItems_aboutToShow)

        self.connect(self.actRemoveItem,
                     QtCore.SIGNAL('triggered()'),
                     self.on_actRemoveItem_triggered)

        self.connect(self.actDuplicateItem,
                     QtCore.SIGNAL('triggered()'),
                     self.on_actDuplicateItem_triggered)

        self.connect(self.actCopyPreCreateProperties,
                     QtCore.SIGNAL('triggered()'),
                     self.on_actCopyPreCreateProperties_triggered)

        self.connect(self.actPastPreCreateProperties,
                     QtCore.SIGNAL('triggered()'),
                     self.on_actPastPreCreateProperties_triggered)

    def getItemEditor(self):
        return CEventTypeEditor(self)

    def exec_(self):
        QtGui.qApp.clipboard().mimeData().removeFormat(CEventTypeList.mimeTypeEventTypeActionsIdList)
        QtGui.qApp.clipboard().mimeData().removeFormat(CEventTypeList.mimeTypeEventTypeDiagnosticsIdList)
        return CItemsListDialog.exec_(self)

    @QtCore.pyqtSlot()
    def on_gbMesRequired_toggled(self, on):
        if not on:
            self.chkShowAmountFromMes.setChecked(QtCore.Qt.Unchecked)
            self.chkMesNecessityEqOne.setChecked(QtCore.Qt.Unchecked)
            self.chkShowMedicaments.setChecked(QtCore.Qt.Unchecked)
            self.chkDefaultMesSpecification.setChecked(QtCore.Qt.Unchecked)

        #    @QtCore.pyqtSlot()

    def on_mnuItems_aboutToShow(self):
        itemPresent = self.tblItems.currentIndex().row() >= 0
        mimeData = QtGui.qApp.clipboard().mimeData()
        fullMimeData = bool(mimeData.hasFormat(CEventTypeList.mimeTypeEventTypeActionsIdList))
        fullMimeData = fullMimeData or bool(mimeData.hasFormat(CEventTypeList.mimeTypeEventTypeDiagnosticsIdList))
        self.actDuplicateItem.setEnabled(itemPresent)
        self.actRemoveItem.setEnabled(itemPresent)
        self.actCopyPreCreateProperties.setEnabled(itemPresent)
        self.actPastPreCreateProperties.setEnabled(itemPresent and fullMimeData)

    #    @QtCore.pyqtSlot()
    def on_actDuplicateItem_triggered(self):
        eventTypeId = self.tblItems.currentItemId()
        db = QtGui.qApp.db
        table = db.table('EventType')
        db.transaction()
        try:
            record = db.getRecord(table, '*', eventTypeId)
            record.setNull('id')
            record.setValue('code', toVariant(forceString(record.value('code')) + u'-копия'))
            record.setValue('name', toVariant(forceString(record.value('name')) + u'-копия'))
            newId = db.insertRecord(table, record)
            db.copyDepended(db.table('EventTypeForm'), 'eventType_id', eventTypeId, newId)
            db.copyDepended(db.table('EventType_Action'), 'eventType_id', eventTypeId, newId)
            db.copyDepended(db.table('EventType_Diagnostic'), 'eventType_id', eventTypeId, newId)
            db.commit()
        except:
            db.rollback()
            raise
        self.renewListAndSetTo(newId)

    #    @QtCore.pyqtSlot()
    def on_actRemoveItem_triggered(self):
        eventTypeId = self.tblItems.currentItemId()
        db = QtGui.qApp.db
        table = db.table('EventType')
        db.transaction()
        try:
            eventTable = db.table('Event')
            if (db.getCount(eventTable, where='eventType_id=' + str(eventTypeId)) > 0):
                QtGui.QMessageBox.warning(self, u'Внимание!',
                                          u'Нельзя удалить тип, записи с которым есть в базе. Сначала удалите записи')
            else:
                db.markRecordsDeleted(table, table['id'].eq(eventTypeId))
                self.model.setIdList(self.select({}))
                db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise

    def on_actCopyPreCreateProperties_triggered(self):
        try:
            eventTypeId = self.tblItems.currentItemId()
            if eventTypeId:
                actionsCount = self.copyPreCreateProperties(
                    eventTypeId,
                    'EventType_Action',
                    CEventTypeList.mimeTypeEventTypeActionsIdList
                )
                diagnosticsCount = self.copyPreCreateProperties(
                    eventTypeId,
                    'EventType_Diagnostic',
                    CEventTypeList.mimeTypeEventTypeDiagnosticsIdList
                )
                txtActionsCount = amountToWords(actionsCount, ((u'действие', u'действия', u'действий', 'n'), None))
                txtDiagnosticsCount = amountToWords(diagnosticsCount, ((u'осмотр', u'осмотра', u'осмотров', 'm'), None))
                message = u'Скопировано: %s, %s' % (txtActionsCount, txtDiagnosticsCount)
                self.statusBar.showMessage(message, 5000)
        except:
            QtGui.QMessageBox.warning(self,
                                      u'Внимание!',
                                      u'Не удалось скопировать определения планировщика в буфер обмена')

    def copyPreCreateProperties(self, eventTypeId, tableName, mimeTypeName):
        db = QtGui.qApp.db
        eventTypeActionsIdList = db.getIdList(tableName, 'id', 'eventType_id=%d' % eventTypeId)
        if bool(eventTypeActionsIdList):
            strList = ','.join([str(id) for id in eventTypeActionsIdList])
            self.mimeData.setData(mimeTypeName, QtCore.QByteArray(strList))
            QtGui.qApp.clipboard().setMimeData(self.mimeData)
            return len(eventTypeActionsIdList)
        QtGui.qApp.clipboard().mimeData().removeFormat(mimeTypeName)
        return 0

    def on_actPastPreCreateProperties_triggered(self):
        dlg = CCheckPreCreatePropertiesTypes(self)
        if not dlg.exec_():
            return
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        selectedIdList = self.tblItems.selectedItemIdList()
        if bool(selectedIdList):
            db = QtGui.qApp.db
            mimeData = QtGui.qApp.clipboard().mimeData()
            actionsRecordList = []
            diagnosticsRecordList = []
            if bool(dlg.actionClasses()) and bool(mimeData.hasFormat(CEventTypeList.mimeTypeEventTypeActionsIdList)):
                strIdList = unicode(mimeData.data(CEventTypeList.mimeTypeEventTypeActionsIdList)).split(',')
                actionsIdList = [int(id) for id in strIdList]
                table = db.table('EventType_Action')
                tableActionType = db.table('ActionType')
                cond = [
                    table['id'].inlist(actionsIdList),
                    'EXISTS (SELECT ActionType.`id` FROM ActionType '
                    'WHERE %s AND EventType_Action.`actionType_id`=ActionType.`id`)' %
                    tableActionType['class'].inlist(dlg.actionClasses())
                ]
                actionsRecordList = db.getRecordList(table, '*', cond)
            if dlg.diagnostics() and bool(mimeData.hasFormat(CEventTypeList.mimeTypeEventTypeDiagnosticsIdList)):
                strIdList = unicode(mimeData.data(CEventTypeList.mimeTypeEventTypeDiagnosticsIdList)).split(',')
                diagnosticsIdList = [int(id) for id in strIdList]
                table = db.table('EventType_Diagnostic')
                diagnosticsRecordList = db.getRecordList(table, '*', table['id'].inlist(diagnosticsIdList))
            for selectedId in selectedIdList:
                actualActionsRecordList = self.checkSameRecords(selectedId, actionsRecordList, 'EventType_Action')
                actualDiagnosticsRecordList = self.checkSameRecords(selectedId, diagnosticsRecordList,
                                                                    'EventType_Diagnostic')
                for record in actualActionsRecordList:
                    db.insertRecord('EventType_Action', record)
                for record in actualDiagnosticsRecordList:
                    db.insertRecord('EventType_Diagnostic', record)
                actionsCount = len(actualActionsRecordList)
                diagnosticsCount = len(actualDiagnosticsRecordList)
                txtActionsCount = amountToWords(actionsCount, ((u'действие', u'действия', u'действий', 'n'), None))
                txtDiagnosticsCount = amountToWords(diagnosticsCount, ((u'осмотр', u'осмотра', u'осмотров', 'm'), None))
                message = u'Добавлено: %s, %s' % (txtActionsCount, txtDiagnosticsCount)
                self.statusBar.showMessage(message, 5000)
        QtGui.qApp.restoreOverrideCursor()

    def checkSameRecords(self, id, pastedRecordList, tableName):
        db = QtGui.qApp.db
        table = db.table(tableName)
        existsRecordList = db.getRecordList(table, '*', table['eventType_id'].eq(id))
        actualPastedRecordList = []
        for pastedRecord in pastedRecordList:
            pastedRecord.setNull('id')
            pastedRecord.setNull('eventType_id')
            pastedFieldsCount = pastedRecord.count()
            difRecords = True
            for existsRecord in existsRecordList:
                allIsSame = True
                existsRecord.setNull('id')
                existsRecord.setNull('eventType_id')
                existsFieldsCount = existsRecord.count()
                if existsFieldsCount == pastedFieldsCount:
                    for i in range(pastedFieldsCount):
                        if unicode(existsRecord.fieldName(i)) not in [u'id', u'eventType_id']:
                            if existsRecord.value(i) != pastedRecord.value(i):
                                allIsSame = False
                                break
                if allIsSame:
                    difRecords = False
                    break
            if difRecords:
                pastedRecord.setValue('eventType_id', QtCore.QVariant(id))
                actualPastedRecordList.append(pastedRecord)
        return actualPastedRecordList


class CCheckPreCreatePropertiesTypes(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.vLayout = QtGui.QVBoxLayout(self)
        self.__chkDiagnostics = QtGui.QCheckBox(u'Осмотры', self)
        self.__chkDiagnostics.setChecked(True)
        self.__chkStatusActions = QtGui.QCheckBox(u'Статус', self)
        self.__chkStatusActions.setChecked(True)
        self.__chkDiagnosticActions = QtGui.QCheckBox(u'Диагностика', self)
        self.__chkDiagnosticActions.setChecked(True)
        self.__chkCureActions = QtGui.QCheckBox(u'Лечение', self)
        self.__chkCureActions.setChecked(True)
        self.__chkMiscActions = QtGui.QCheckBox(u'Прочие мероприятия', self)
        self.__chkMiscActions.setChecked(True)
        self.__chkAnalysesActions = QtGui.QCheckBox(u'Анализы', self)
        self.__chkAnalysesActions.setChecked(True)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)

        self.vLayout.addWidget(self.__chkDiagnostics)
        self.vLayout.addWidget(self.__chkStatusActions)
        self.vLayout.addWidget(self.__chkDiagnosticActions)
        self.vLayout.addWidget(self.__chkCureActions)
        self.vLayout.addWidget(self.__chkMiscActions)
        self.vLayout.addWidget(self.__chkAnalysesActions)
        self.vLayout.addWidget(self.buttonBox)
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)

    def diagnostics(self):
        return self.__chkDiagnostics.isChecked()

    def actionClasses(self):
        classes = []
        if self.__chkStatusActions.isChecked():
            classes.append(0)
        if self.__chkDiagnosticActions.isChecked():
            classes.append(1)
        if self.__chkCureActions.isChecked():
            classes.append(2)
        if self.__chkMiscActions.isChecked():
            classes.append(3)
        if self.__chkAnalysesActions.isChecked():
            classes.append(4)
        return classes


class CEventTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    setFiltersStandard = [u'Набор фильтров для МЭС',
                          u'Набор фильтров для КСГ']

    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'EventType')

        self.addModels('Diagnostics', CDiagnosticsModel(self))
        self.addModels('StatusActions', CActionsModel(self, 0))
        self.addModels('DiagnosticActions', CActionsModel(self, 1))
        self.addModels('CureActions', CActionsModel(self, 2))
        self.addModels('MiscActions', CActionsModel(self, 3))
        self.addModels('AnalysesActions', CActionsModel(self, 4))
        self.addModels('AutoPrint', CAutoPrintSettingsModel(self))
        self.addModels('Associations', CAssociationsModel(self))

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип события')
        self.cmbPurpose.setTable('rbEventTypePurpose')
        self.cmbFinance.setTable('rbFinance')
        self.cmbCaseCast.setTable('rbCaseCast')
        self.cmbEventProfile.setTable('rbEventProfile', True)
        self.cmbMedicalAidKind.setTable('rbMedicalAidKind', True)
        self.cmbMedicalAidType.setTable('rbMedicalAidType', True)
        self.cmbDefaultMesSpecification.setTable('rbMesSpecification', True)

        self.cmbForm.addItem(u'не задано', toVariant(''))
        for formCode, formDescr in getEventFormList():
            self.cmbForm.addItem(formDescr, toVariant(formCode))

        EventOrder.fillCmb(self.cmbDefaultOrder)

        self.cmbScene.setTable('rbScene', True)
        self.cmbTypeCode.setTable('rbEventKind')

        self.setModels(self.tblDiagnostics, self.modelDiagnostics, self.selectionModelDiagnostics)
        self.setModels(self.tblStatusActions, self.modelStatusActions, self.selectionModelStatusActions)
        self.setModels(self.tblDiagnosticActions, self.modelDiagnosticActions, self.selectionModelDiagnosticActions)
        self.setModels(self.tblCureActions, self.modelCureActions, self.selectionModelCureActions)
        self.setModels(self.tblMiscActions, self.modelMiscActions, self.selectionModelMiscActions)
        self.setModels(self.tblAnalysesActions, self.modelAnalysesActions, self.selectionModelAnalysesActions)
        self.setModels(self.tblAutoPrint, self.modelAutoPrint, self.selectionModelAutoPrint)
        self.setModels(self.tblAssociations, self.modelAssociations, self.selectionModelAssociations)
        self.modelAssociations.cols()[0].setFilter(self.itemId())

        for tbl in [self.tblDiagnostics, self.tblStatusActions, self.tblDiagnosticActions, self.tblCureActions,
                    self.tblMiscActions, self.tblAnalysesActions, self.tblAutoPrint]:
            tbl.addMoveRow()
            tbl.addPopupDelRow()
            tbl.addPopupDuplicateCurrentRow()

        self.cmbService.setTable(rbService, True)
        self.cmbCounter.setTable('rbCounter', False)
        self.cmbService.setCurrentIndex(0)
        self.setupDirtyCather()
        self.setIsDirty(False)
        self.regExpTestStr = ''
        self.visitServiceFilterTestStr = ''

        self.popupMenu = QtGui.QMenu(self)
        self.popupMenu.setObjectName('popupMenu')
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')
        self.connect(self.actDelete, QtCore.SIGNAL('triggered()'), self.on_actDelete_triggered)
        self.popupMenu.addAction(self.actDelete)
        self.tblAssociations.setPopupMenu(self.popupMenu)
        self.cmbSetFilters.addItems(self.setFiltersStandard)

        self.chkDefaultMesSpecification.clicked.connect(self.on_chkDefaultMesSpecification_clicked)
        self.chkNoModifyService.stateChanged.connect(self.on_chkNoModifyService_changed)
        self.chkReplaceService.stateChanged.connect(self.on_chkReplaceService_changed)
        self.chkModifyHeadService.stateChanged.connect(self.on_chkModifyHeadService_changed)
        self.chkModifyTailService.stateChanged.connect(self.on_chkModifyTailService_changed)
        self.chkDispByMobileTeam.setVisible(QtGui.qApp.region() == '23')

        self.tblPostsFilter.setTable('rbPost')
        self.tblPostsFilter.setDisabled(True)
        self.tblSpecialitiesFilter.setTable('rbSpeciality')
        self.tblSpecialitiesFilter.setDisabled(True)

    def on_chkDefaultMesSpecification_clicked(self):
        self.cmbDefaultMesSpecification.setEnabled(self.chkDefaultMesSpecification.isChecked())

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setRBComboBoxValue(self.cmbPurpose, record, 'purpose_id')
        setRBComboBoxValue(self.cmbEventProfile, record, 'eventProfile_id')
        setRBComboBoxValue(self.cmbMedicalAidKind, record, 'medicalAidKind_id')
        setRBComboBoxValue(self.cmbMedicalAidType, record, 'medicalAidType_id')
        setComboBoxValue(self.cmbSex, record, 'sex')
        setComboBoxValue(self.cmbCheckKSG, record, 'isCheck_KSG')
        self.edtAgeSelector.setText(forceString(record.value('age')))
        setRBComboBoxValue(self.cmbCounter, record, 'counter_id')
        # setComboBoxValue(   self.cmbDefaultOrder, record, 'defaultOrder')
        self.cmbDefaultOrder.setCode(forceString(record.value('defaultOrder')))
        self.edtDefaultEndTime.setTime(forceTime(record.value('defaultEndTime')))
        setLineEditValue(self.edtPrefix, record, 'prefix')
        setCheckBoxValue(self.chkRequiredCoordination, record, 'isRequiredCoordination')
        setRBComboBoxValue(self.cmbFinance, record, 'finance_id')
        setRBComboBoxValue(self.cmbCaseCast, record, 'caseCast_id')
        weekdays = forceInt(record.value('weekdays')) - 5
        self.cmbWeekdays.setCurrentIndex(weekdays if weekdays in (0, 1, 2) else 0)
        setCheckBoxValue(self.chkCanHavePayableActions, record, 'canHavePayableActions')
        setRBComboBoxValue(self.cmbScene, record, 'scene_id')
        setComboBoxValue(self.cmbVisitFinance, record, 'visitFinance')
        setComboBoxValue(self.cmbActionFinance, record, 'actionFinance')
        setComboBoxValue(self.cmbActionContract, record, 'actionContract')
        setSpinBoxValue(self.edtPeriod, record, 'period')
        setComboBoxValue(self.cmbSingleInPeriod, record, 'singleInPeriod')
        setComboBoxValue(self.cmbDateInput, record, 'dateInput')
        setCheckBoxValue(self.chkIsLong, record, 'isLong')
        setCheckBoxValue(self.chkOrgStructurePriorityForAddActions, record, 'isOrgStructurePriority')
        setSpinBoxValue(self.edtMinDuration, record, 'minDuration')
        setSpinBoxValue(self.edtMaxDuration, record, 'maxDuration')
        setRBComboBoxValue(self.cmbService, record, 'service_id')
        self.cmbForm.setCurrentIndex(max(0, self.cmbForm.findData(record.value('form'))))
        setCheckBoxValue(self.chkShowTime, record, 'showTime')
        setLineEditValue(self.edtContext, record, 'context')
        setCheckBoxValue(self.chkExternalId, record, 'isExternal')
        self.chkExternalIdRequired.setChecked(forceInt(record.value('isExternal')) == 2)
        setCheckBoxValue(self.chkUniqueExternalId, record, 'uniqueExternalId')
        setCheckBoxValue(self.chkExternalIdAsAccountNumber, record, 'externalIdAsAccountNumber')
        setComboBoxValue(self.cmbCounterType, record, 'counterType')
        setCheckBoxValue(self.gbMesRequired, record, 'mesRequired')
        setCheckBoxValue(self.chkIsTakenTissue, record, 'isTakenTissue')
        setLineEditValue(self.edtMesCodeMask, record, 'mesCodeMask')
        setLineEditValue(self.edtMesNameMask, record, 'mesNameMask')
        setCheckBoxValue(self.chkHasAssistant, record, 'hasAssistant')
        setCheckBoxValue(self.chkHasCurator, record, 'hasCurator')
        setCheckBoxValue(self.chkHasVisitAssistant, record, 'hasVisitAssistant')
        setCheckBoxValue(self.chkPermitAnyDate, record, 'permitAnyActionDate')
        setSpinBoxValue(self.edtExposeGrouped, record, 'exposeGrouped')
        setCheckBoxValue(self.chkLittleStranger, record, 'showLittleStranger')
        setCheckBoxValue(self.chkInheritDiagnosis, record, 'inheritDiagnosis')
        setComboBoxValue(self.cmbSetFilters, record, 'setFilterStandard')
        setCheckBoxValue(self.chkInheritResult, record, 'inheritResult')
        setCheckBoxValue(self.chkInheritCheckupResult, record, 'inheritCheckupResult')
        setCheckBoxValue(self.chkInheritGoal, record, 'inheritGoal')
        setRBComboBoxValue(self.cmbTypeCode, record, 'eventKind_id')
        if QtGui.qApp.region() == '23':
            setCheckBoxValue(self.chkDispByMobileTeam, record, 'dispByMobileTeam')
        # Переменная mesRequired является маской, определяющей необходимость применения МЭС (0 бит),
        # возможность вывода количества из МЭС (1 бит) м количества медикаментов (2 бит).
        if forceInt(record.value('mesRequired')) & 2:
            self.chkShowAmountFromMes.setChecked(True)
        if forceInt(record.value('mesRequired')) & 4:
            self.chkShowMedicaments.setChecked(True)
        if forceInt(record.value('mesRequired')) & 8:
            self.chkMesNecessityEqOne.setChecked(True)
        if forceInt(record.value('mesRequired')) & 16:
            self.chkDefaultMesSpecification.setChecked(True)
            setRBComboBoxValue(self.cmbDefaultMesSpecification, record, 'defaultMesSpecification_id')
        self.cmbCounterType.setEnabled(self.chkExternalId.isChecked())
        self.lblCounterType.setEnabled(self.chkExternalId.isChecked())
        self.cmbCounter.setEnabled(self.chkExternalId.isChecked() and self.cmbCounterType.currentIndex() in (1, 2))
        self.lblCounter.setEnabled(self.chkExternalId.isChecked() and self.cmbCounterType.currentIndex() in (1, 2))
        self.edtPrefix.setEnabled(self.chkExternalId.isChecked())
        self.lblPrefix.setEnabled(self.chkExternalId.isChecked())
        self.chkExternalIdRequired.setEnabled(self.chkExternalId.isChecked())

        setLineEditValue(self.edtVisitServiceFilter, record, 'visitServiceFilter')
        modifiers = parseModifier(forceStringEx(record.value('visitServiceModifier')))
        for action, text, n in modifiers:
            if action == 0:
                self.chkNoModifyService.setChecked(True)
            elif action == 1:
                self.chkReplaceService.setChecked(True)
                self.edtReplaceService.setText(text)
            elif action == 2:
                self.chkModifyHeadService.setChecked(True)
                self.edtModifyHeadService.setText(text)
                self.edtModifyHeadService_N.setText(unicode(n))
            elif action == 3:
                self.chkModifyTailService.setChecked(True)
                self.edtModifyTailService.setText(text)
                self.edtModifyTailService_N.setText(unicode(n))

        setCheckBoxValue(self.chkStatusShowOptionalInPlanner, record, 'showStatusActionsInPlanner')
        setCheckBoxValue(self.chkDiagnosticShowOptionalInPlanner, record, 'showDiagnosticActionsInPlanner')
        setCheckBoxValue(self.chkCureShowOptionalInPlanner, record, 'showCureActionsInPlanner')
        setCheckBoxValue(self.chkMiscShowOptionalInPlanner, record, 'showMiscActionsInPlanner')
        setCheckBoxValue(self.chkAnalysesShowOptionalInPlanner, record, 'showAnalysesActionsInPlanner')
        setCheckBoxValue(self.chkStatusLimitInput, record, 'limitStatusActionsInput')
        setCheckBoxValue(self.chkDiagnosticLimitInput, record, 'limitDiagnosticActionsInput')
        setCheckBoxValue(self.chkCureLimitInput, record, 'limitCureActionsInput')
        setCheckBoxValue(self.chkMiscLimitInput, record, 'limitMiscActionsInput')
        setCheckBoxValue(self.chkAnalysesLimitInput, record, 'limitAnalysesActionsInput')
        setCheckBoxValue(self.chkDiagnosisSetDate, record, 'diagnosisSetDateVisible')
        self.on_chkIsTakenTissue_clicked(self.chkIsTakenTissue.isChecked())

        itemId = self.itemId()
        self.modelDiagnostics.loadItems(itemId)
        self.modelStatusActions.loadItems(itemId)
        self.modelDiagnosticActions.loadItems(itemId)
        self.modelCureActions.loadItems(itemId)
        self.modelMiscActions.loadItems(itemId)
        self.modelAnalysesActions.loadItems(itemId)
        self.modelAutoPrint.loadItems(itemId)
        self.modelAssociations.loadItems(itemId)
        self.setIsDirty(False)

        setCheckBoxValue(self.chkOnJobPayedFilter, record, 'isOnJobPayedFilter')  # atronah for issue 317
        setCheckBoxValue(self.chkResetSetDate, record, 'isResetSetDate')
        setCheckBoxValue(self.chkAvailInFastCreateMode, record, 'isAvailInFastCreateMode')
        setCheckBoxValue(self.chkExposeConfirmation, record, 'exposeConfirmation')
        setSpinBoxValue(self.edtMesPerfPercent, record, 'needMesPerformPercent')
        setCheckBoxValue(self.chkShowZNO, record, 'showZNO')
        setCheckBoxValue(self.chkGoalFilter, record, 'goalFilter')

        setCheckBoxValue(self.chkPostsFilter, record, 'filterPosts')
        self.tblPostsFilter.setValues(QtGui.qApp.db.getIdList('EventType_Post', 'post_id',
                                                              'eventType_id = %d' % self.itemId()))
        setCheckBoxValue(self.chkSpecialitiesFilter, record, 'filterSpecialities')
        self.tblSpecialitiesFilter.setValues(QtGui.qApp.db.getIdList('EventType_Speciality', 'speciality_id',
                                                                     'eventType_id = %d' % self.itemId()))
        setCheckBoxValue(self.chkCompulsoryServiceStopIgnore, record, 'compulsoryServiceStopIgnore')
        setCheckBoxValue(self.chkVoluntaryServiceStopIgnore, record, 'voluntaryServiceStopIgnore')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getRBComboBoxValue(self.cmbPurpose, record, 'purpose_id')
        getRBComboBoxValue(self.cmbEventProfile, record, 'eventProfile_id')
        getRBComboBoxValue(self.cmbMedicalAidKind, record, 'medicalAidKind_id')
        getRBComboBoxValue(self.cmbMedicalAidType, record, 'medicalAidType_id')
        getComboBoxValue(self.cmbSex, record, 'sex')
        getComboBoxValue(self.cmbCheckKSG, record, 'isCheck_KSG')
        getLineEditValue(self.edtAgeSelector, record, 'age')
        getComboBoxValue(self.cmbCounterType, record, 'counterType')
        if self.cmbCounter.isEnabled():
            getRBComboBoxValue(self.cmbCounter, record, 'counter_id')
        else:
            record.setNull('counter_id')
        # getComboBoxValue(   self.cmbDefaultOrder, record, 'defaultOrder')
        record.setValue('defaultOrder', toVariant(self.cmbDefaultOrder.code()))
        record.setValue('defaultEndTime', toVariant(self.edtDefaultEndTime.time()))
        getLineEditValue(self.edtPrefix, record, 'prefix')
        getCheckBoxValue(self.chkRequiredCoordination, record, 'isRequiredCoordination')
        getRBComboBoxValue(self.cmbFinance, record, 'finance_id')
        getRBComboBoxValue(self.cmbCaseCast, record, 'caseCast_id')
        weekdays = self.cmbWeekdays.currentIndex()
        record.setValue('weekdays', toVariant(weekdays + 5))
        getCheckBoxValue(self.chkCanHavePayableActions, record, 'canHavePayableActions')
        getRBComboBoxValue(self.cmbScene, record, 'scene_id')
        getComboBoxValue(self.cmbVisitFinance, record, 'visitFinance')
        getComboBoxValue(self.cmbActionFinance, record, 'actionFinance')
        getComboBoxValue(self.cmbActionContract, record, 'actionContract')
        getSpinBoxValue(self.edtPeriod, record, 'period')
        getComboBoxValue(self.cmbSingleInPeriod, record, 'singleInPeriod')
        getComboBoxValue(self.cmbDateInput, record, 'dateInput')
        getCheckBoxValue(self.chkIsLong, record, 'isLong')
        getCheckBoxValue(self.chkOrgStructurePriorityForAddActions, record, 'isOrgStructurePriority')
        getSpinBoxValue(self.edtMinDuration, record, 'minDuration')
        getSpinBoxValue(self.edtMaxDuration, record, 'maxDuration')
        getRBComboBoxValue(self.cmbService, record, 'service_id')
        record.setValue('form', self.cmbForm.itemData(self.cmbForm.currentIndex()))
        getCheckBoxValue(self.chkShowTime, record, 'showTime')
        getLineEditValue(self.edtContext, record, 'context')
        self.getExternalCheckBoxValue(record)
        getCheckBoxValue(self.chkUniqueExternalId, record, 'uniqueExternalId')
        getCheckBoxValue(self.chkExternalIdAsAccountNumber, record, 'externalIdAsAccountNumber')
        getCheckBoxValue(self.chkInheritDiagnosis, record, 'inheritDiagnosis')
        getComboBoxValue(self.cmbSetFilters, record, 'setFilterStandard')
        getCheckBoxValue(self.chkInheritResult, record, 'inheritResult')
        getCheckBoxValue(self.chkInheritCheckupResult, record, 'inheritCheckupResult')
        getCheckBoxValue(self.chkInheritGoal, record, 'inheritGoal')
        getRBComboBoxValue(self.cmbTypeCode, record, 'eventKind_id')
        mesRequiredValue = 0
        if self.gbMesRequired.isChecked():
            mesRequiredValue += 1 << 0  # atronah: Странно, что += вместо |= для битовых операций
            if self.chkShowAmountFromMes.isChecked():
                mesRequiredValue += 1 << 1
            if self.chkShowMedicaments.isChecked():
                mesRequiredValue += 1 << 2
            if self.chkMesNecessityEqOne.isChecked():
                mesRequiredValue |= 8  # atronah: равносильно "+= 1 << 3"
            if self.chkDefaultMesSpecification.isChecked():
                mesRequiredValue |= 16
                getRBComboBoxValue(self.cmbDefaultMesSpecification, record, 'defaultMesSpecification_id')
        record.setValue('mesRequired', toVariant(mesRequiredValue))
        getCheckBoxValue(self.chkIsTakenTissue, record, 'isTakenTissue')
        getLineEditValue(self.edtMesCodeMask, record, 'mesCodeMask')
        getLineEditValue(self.edtMesNameMask, record, 'mesNameMask')
        getCheckBoxValue(self.chkHasAssistant, record, 'hasAssistant')
        getCheckBoxValue(self.chkHasCurator, record, 'hasCurator')
        getCheckBoxValue(self.chkHasVisitAssistant, record, 'hasVisitAssistant')
        getCheckBoxValue(self.chkPermitAnyDate, record, 'permitAnyActionDate')
        getCheckBoxValue(self.chkLittleStranger, record, 'showLittleStranger')
        getSpinBoxValue(self.edtExposeGrouped, record, 'exposeGrouped')
        if QtGui.qApp.region() == '23':
            getCheckBoxValue(self.chkDispByMobileTeam, record, 'dispByMobileTeam')
        modifier = u''
        if self.chkReplaceService.isChecked():
            action = 1
            text = forceStringEx(self.edtReplaceService.text())
            modifier = createModifier(action, text)
        # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyTailService
        if self.chkModifyHeadService.isChecked():
            action = 2
            text = forceStringEx(self.edtModifyHeadService.text())
            n = forceInt(self.edtModifyHeadService_N.text())
            modifier = createModifier(action, text, n)
        # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyHeadService
        if self.chkModifyTailService.isChecked():
            action = 3
            text = forceStringEx(self.edtModifyTailService.text())
            n = forceInt(self.edtModifyTailService_N.text())
            if modifier:
                modifier = modifier + u'/' + createModifier(action, text, n)
            else:
                modifier = createModifier(action, text, n)
        # Если было кликнуто ничего или chkNoModifyService, то modifier должен быть равен u''
        record.setValue('visitServiceModifier', toVariant(modifier))

        getLineEditValue(self.edtVisitServiceFilter, record, 'visitServiceFilter')
        getCheckBoxValue(self.chkStatusShowOptionalInPlanner, record, 'showStatusActionsInPlanner')
        getCheckBoxValue(self.chkDiagnosticShowOptionalInPlanner, record, 'showDiagnosticActionsInPlanner')
        getCheckBoxValue(self.chkCureShowOptionalInPlanner, record, 'showCureActionsInPlanner')
        getCheckBoxValue(self.chkMiscShowOptionalInPlanner, record, 'showMiscActionsInPlanner')
        getCheckBoxValue(self.chkAnalysesShowOptionalInPlanner, record, 'showAnalysesActionsInPlanner')
        getCheckBoxValue(self.chkStatusLimitInput, record, 'limitStatusActionsInput')
        getCheckBoxValue(self.chkDiagnosticLimitInput, record, 'limitDiagnosticActionsInput')
        getCheckBoxValue(self.chkCureLimitInput, record, 'limitCureActionsInput')
        getCheckBoxValue(self.chkMiscLimitInput, record, 'limitMiscActionsInput')
        getCheckBoxValue(self.chkAnalysesLimitInput, record, 'limitAnalysesActionsInput')
        getCheckBoxValue(self.chkOnJobPayedFilter, record, 'isOnJobPayedFilter')  # atronah for issue 317
        getCheckBoxValue(self.chkDiagnosisSetDate, record, 'diagnosisSetDateVisible')
        getCheckBoxValue(self.chkResetSetDate, record, 'isResetSetDate')
        getCheckBoxValue(self.chkAvailInFastCreateMode, record, 'isAvailInFastCreateMode')
        getCheckBoxValue(self.chkExposeConfirmation, record, 'exposeConfirmation')

        getSpinBoxValue(self.edtMesPerfPercent, record, 'needMesPerformPercent')
        getCheckBoxValue(self.chkShowZNO, record, 'showZNO')
        getCheckBoxValue(self.chkGoalFilter, record, 'goalFilter')
        getCheckBoxValue(self.chkPostsFilter, record, 'filterPosts')
        getCheckBoxValue(self.chkSpecialitiesFilter, record, 'filterSpecialities')

        getCheckBoxValue(self.chkCompulsoryServiceStopIgnore, record, 'compulsoryServiceStopIgnore')
        getCheckBoxValue(self.chkVoluntaryServiceStopIgnore, record, 'voluntaryServiceStopIgnore')

        CEventTypeDescription.purge()
        return record

    def getExternalCheckBoxValue(self, record):
        if not self.chkExternalId.isChecked():
            val = 0
        elif not self.chkExternalIdRequired.isChecked():
            val = 1
        else:
            val = 2
        record.setValue('isExternal', QtCore.QVariant(val))

    def saveInternals(self, id):
        self.modelDiagnostics.saveItems(id)
        self.modelStatusActions.saveItems(id)
        self.modelDiagnosticActions.saveItems(id)
        self.modelCureActions.saveItems(id)
        self.modelMiscActions.saveItems(id)
        self.modelAnalysesActions.saveItems(id)
        self.modelAutoPrint.saveItems(id)
        self.modelAssociations.saveItems(id)

        if self.itemId():
            QtGui.qApp.db.deleteRecord('EventType_Post', 'eventType_id = %d' % self.itemId())
            QtGui.qApp.db.insertMultipleFromDict(
                'EventType_Post',
                [{
                     'eventType_id': self.itemId(),
                     'post_id': pid
                 } for pid in self.tblPostsFilter.values()]
            )
            QtGui.qApp.db.deleteRecord('EventType_Speciality', 'eventType_id = %d' % self.itemId())
            QtGui.qApp.db.insertMultipleFromDict(
                'EventType_Speciality',
                [{
                     'eventType_id': self.itemId(),
                     'speciality_id': sid
                 } for sid in self.tblSpecialitiesFilter.values()]
            )

    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        result = result and (self.cmbPurpose.value() or self.checkInputMessage(u'назначение', False, self.cmbPurpose))
        result = result and self.checkAgeSelector()
        return result

    def checkAgeSelector(self):
        result = True
        ageSelector = forceString(self.edtAgeSelector.text())
        if not checkAgeSelectorSyntax(ageSelector):
            message = u'''
            Недопустимый синтаксис селектора возраста.
            Используйте следующий синтаксис:
            "{N{д|н|м|г}-{M{д|н|м|г}}{/S{+}{-}}, {...}, {...}, ..."
            '''
            msg = '\n'.join(filter(None, map(lambda line: line.strip(), message.split('\n'))))
            result = self.checkValueMessage(msg, skipable=False, widget=self.edtAgeSelector)
        return result

    @QtCore.pyqtSlot()
    def on_actDelete_triggered(self):
        index = self.tblAssociations.currentIndex()
        self.modelAssociations.removeRows(index.row(), 1)
        self.modelAssociations.reset()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtVisitServiceFilter_textChanged(self, txt):
        self.btnVisitServiceFilterTest.setEnabled(bool(forceStringEx(txt)))

    @QtCore.pyqtSlot()
    def on_btnSelectService_clicked(self):
        serviceId = selectService(self, self.cmbService)
        self.cmbService.update()
        if serviceId:
            self.cmbService.setValue(serviceId)

    @QtCore.pyqtSlot(bool)
    def on_chkIsTakenTissue_clicked(self, checked):
        self.modelStatusActions.cols()[2].setReadOnly(not checked)
        self.modelDiagnosticActions.cols()[2].setReadOnly(not checked)
        self.modelCureActions.cols()[2].setReadOnly(not checked)
        self.modelMiscActions.cols()[2].setReadOnly(not checked)
        self.modelAnalysesActions.cols()[2].setReadOnly(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkExternalId_clicked(self, checked):
        self.lblPrefix.setEnabled(checked)
        self.edtPrefix.setEnabled(checked)
        self.lblCounterType.setEnabled(checked)
        self.cmbCounterType.setEnabled(checked)
        self.lblCounter.setEnabled(checked and self.cmbCounterType.currentIndex() in (1, 2))
        self.cmbCounter.setEnabled(checked and self.cmbCounterType.currentIndex() in (1, 2))
        self.chkUniqueExternalId.setEnabled(checked)
        self.chkExternalIdAsAccountNumber.setEnabled(checked)
        self.chkExternalIdRequired.setEnabled(checked)

    @QtCore.pyqtSlot(int)
    def on_cmbCounterType_currentIndexChanged(self, value):
        enabled = value in (1, 2)
        self.lblCounter.setEnabled(enabled)
        self.cmbCounter.setEnabled(enabled)

    @QtCore.pyqtSlot(int)
    def on_cmbFinance_currentIndexChanged(self, index):
        self.chkCanHavePayableActions.setEnabled(self.cmbFinance.code() != '4')

    @QtCore.pyqtSlot(int)
    def on_cmbPurpose_currentIndexChanged(self, index):
        self.modelDiagnostics.setPurposeId(self.cmbPurpose.value())
        needWarning = False
        for item in self.modelDiagnostics.items():
            if forceRef(item.value('defaultGoal_id')):
                needWarning = True
                item.setValue('defaultGoal_id', QtCore.QVariant())
        if needWarning:
            QtGui.QMessageBox.warning(
                self,
                u'Внимание!',
                u'Цели обращения для диагнозов на вкладке "Осмотры" были сброшены.',
                buttons=QtGui.QMessageBox.Ok,
                defaultButton=QtGui.QMessageBox.Ok
            )

    @QtCore.pyqtSlot()
    def on_btnVisitRegExpTest_pressed(self):
        self.regExpTestStr = testRegExpServiceModifier(self, self.edtVisitRegExp.text(), self.regExpTestStr)

    def on_chkNoModifyService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.chkReplaceService.setChecked(False)
            self.chkModifyHeadService.setChecked(False)
            self.chkModifyTailService.setChecked(False)

    def on_chkReplaceService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.edtReplaceService.setEnabled(True)

            self.chkNoModifyService.setChecked(False)
            self.chkModifyHeadService.setChecked(False)
            self.chkModifyTailService.setChecked(False)

        if state == QtCore.Qt.Unchecked:
            self.edtReplaceService.setEnabled(False)

    # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyTailService
    def on_chkModifyHeadService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.edtModifyHeadService.setEnabled(True)
            self.edtModifyHeadService_N.setEnabled(True)

            self.chkNoModifyService.setChecked(False)
            self.chkReplaceService.setChecked(False)

        if state == QtCore.Qt.Unchecked:
            self.edtModifyHeadService.setEnabled(False)
            self.edtModifyHeadService_N.setEnabled(False)

    # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyHeadService
    def on_chkModifyTailService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.edtModifyTailService.setEnabled(True)
            self.edtModifyTailService_N.setEnabled(True)

            self.chkNoModifyService.setChecked(False)
            self.chkReplaceService.setChecked(False)

        if state == QtCore.Qt.Unchecked:
            self.edtModifyTailService.setEnabled(False)
            self.edtModifyTailService_N.setEnabled(False)


class CHurtEditorModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, fieldType):
        QtCore.QAbstractTableModel.__init__(self, parent)
        assert fieldType in [0, 1]
        self._tableName = None
        self._fieldType = fieldType
        self._items = []
        self._existsList = []
        self._row2Item = {}
        self._data = None

    def setExistsList(self, existsList):
        self._existsList = existsList
        data = self.getData(self._tableName)
        row = 0
        for item in data.getBuff():
            if not unicode(item[self._fieldType]) in self._existsList:
                id, code, name = item[:3]
                self._row2Item[row] = item
                self._items.append((QtCore.QVariant(code), QtCore.QVariant(name)))
                row += 1
        self.reset()

    def getData(self, tableName):
        if self._data is None:
            self._data = CRBModelDataCache.getData(tableName, addNone=False)
            if not self._data.isLoaded():
                self._data.load()
        return self._data

    def setTable(self, tableName):
        self._tableName = tableName

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items)

    def columnCount(self, index=QtCore.QModelIndex()):
        return 2

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return QtCore.QVariant(u'Код')
                elif section == 1:
                    return QtCore.QVariant(u'Наименование')
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return self._items[index.row()][index.column()]
        return QtCore.QVariant()

    def getValue(self, row):
        return self._row2Item[row][self._fieldType]


class CHurtColEditor(QtGui.QWidget):
    __pyqtSignals__ = (
        'editingFinished()',
        'commit()',
    )
    typeSign = {0: '%d', 1: '%s'}

    def __init__(self, parent, fieldType):
        QtGui.QWidget.__init__(self, parent)
        self._fieldType = fieldType
        self.edtItems = QtGui.QLineEdit(self)
        self.tblItems = CRBPopupView(self)
        self.layout = QtGui.QGridLayout(self)
        self.layout.setMargin(0)
        self.layout.setSpacing(0)

        self.layout.addWidget(self.edtItems, 0, 0)
        self.layout.addWidget(self.tblItems, 1, 0)

        self.modelItems = CHurtEditorModel(self, fieldType)
        self.tblItems.setModel(self.modelItems)

        self.connect(self.tblItems, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.tblItemsDoubleClicked)

        self.edtItems.installEventFilter(self)
        self.tblItems.installEventFilter(self)

    def eventFilter(self, widget, event):
        et = event.type()
        if et == QtCore.QEvent.FocusOut:
            fw = QtGui.qApp.focusWidget()
            if not (fw and self.isAncestorOf(fw)):
                self.emit(QtCore.SIGNAL('editingFinished()'))
        elif et == QtCore.QEvent.Hide and widget == self.edtItems:
            self.emit(QtCore.SIGNAL('commit()'))
        return QtGui.QWidget.eventFilter(self, widget, event)

    def tblItemsDoubleClicked(self, index):
        if index.isValid():
            value = self.modelItems.getValue(index.row())
            currentText = forceStringEx(self.text())
            if currentText and currentText[-1] != ';':
                currentText += ';%s'
            else:
                currentText += '%s'
            text = (currentText % CHurtColEditor.typeSign[self._fieldType]) % value
            self.edtItems.setText(text)

    def text(self):
        return self.edtItems.text()

    def setText(self, value):
        self.edtItems.setText(value)
        existsList = self.parseValue(value)
        self.modelItems.setExistsList(existsList)

    def setTable(self, tableName):
        self.modelItems.setTable(tableName)

    def parseValue(self, value):
        result = []
        for item in value.split(';'):
            result.append(forceStringEx(item))
        return result


class CHurtCol(CInDocTableCol):
    idField = 0
    codeField = 1

    def __init__(self, name, fieldName, tableName, fieldType=codeField):
        CInDocTableCol.__init__(self, name, fieldName, 12)
        self._fieldType = fieldType
        self._tableName = tableName

    def createEditor(self, parent):
        editor = CHurtColEditor(parent, self._fieldType)
        editor.setTable(self._tableName)
        return editor


class CDiagnosticsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'EventType_Diagnostic', 'id', 'eventType_id', parent)
        self.addCol(CRBInDocTableCol(u'Специальность', 'speciality_id', 20, 'rbSpeciality')).setSortable(True)
        self.addCol(CEnumInDocTableCol(u'Пол', 'sex', 5, ['', u'М', u'Ж'])).setSortable(True)
        self.addCol(CInDocTableCol(u'Возраст', 'age', 12)).setSortable(True)
        self.addCol(CRBInDocTableCol(u'Услуга', 'service_id', 10, 'rbService', prefferedWidth=300,
                                     showFields=CRBComboBox.showCodeAndName)).setSortable(True)
        self.addCol(CInDocTableCol(u'Код МКБ по умолчанию', 'defaultMKB', 5)).setSortable(True)
        self.addCol(CRBInDocTableCol(u'ДН по умолчанию', 'defaultDispanser_id', 10, 'rbDispanser')).setToolTip(
            u'Диспансерное наблюдение').setSortable(True)
        self.addCol(CRBInDocTableCol(u'ГЗ по умолчанию', 'defaultHealthGroup_id', 10, 'rbHealthGroup')).setToolTip(
            u'Группа здоровья').setSortable(True)
        self.addCol(CRBInDocTableCol(u'Тип визита', 'visitType_id', 20, 'rbVisitType')).setSortable(True)
        self.addCol(CIntInDocTableCol(u'Действителен', 'actuality', 5)).setSortable(True)
        self.addCol(CIntInDocTableCol(u'Группа выбора', 'selectionGroup', 15, low=-100, high=100)).setSortable(True)
        self.addCol(CHurtCol(u'Типы вредности', 'hurtType', 'rbHurtType')).setSortable(True)
        self.addCol(CHurtCol(u'Факторы вредности', 'hurtFactorType', 'rbHurtFactorType')).setSortable(True)
        self.goalCol = CRBInDocTableCol(u'Цель обращения', 'defaultGoal_id', 10, 'rbEventGoal')
        self.addCol(self.goalCol)

    def afterUpdateEditorGeometry(self, editor, index):
        if index.column() in [self.getColIndex('hurtType'), self.getColIndex('hurtFactorType')]:
            editor.resize(editor.width(), 12 * editor.height())

    def setPurposeId(self, eventPurposeId):
        self.goalCol.setFilter('eventTypePurpose_id=\'%d\'' % eventPurposeId)
        self.reset()


class CActionsModel(CInDocTableModel):
    def __init__(self, parent, actionTypeClass):
        CInDocTableModel.__init__(self, 'EventType_Action', 'id', 'eventType_id', parent)
        self.addCol(CActionTypeTableCol(u'Наименование', 'actionType_id', 20, actionTypeClass, descendants=True, model=self)).setSortable(True)
        self.addCol(CRBInDocTableCol(u'Специальность', 'speciality_id', 20, 'rbSpeciality')).setSortable(True)
        self.addCol(CRBInDocTableCol(u'Тип ткани', 'tissueType_id', 20, 'rbTissueType')).setReadOnly(True).setSortable(
            True)
        self.addCol(CEnumInDocTableCol(u'Пол', 'sex', 5, ['', u'М', u'Ж'])).setSortable(True)
        self.addCol(CInDocTableCol(u'Возраст', 'age', 12)).setSortable(True)
        self.addCol(CIntInDocTableCol(u'Действителен', 'actuality', 10)).setSortable(True)
        self.addCol(CIntInDocTableCol(u'Группа выбора', 'selectionGroup', 15, low=-100, high=100)).setSortable(True)
        self.addCol(CBoolInDocTableCol(u'Обязательная услуга', 'isCompulsory', 15, low=-100, high=100)).setSortable(
            True)
        # deprecated by i3097
        # self.addCol(CBoolInDocTableCol( u'Выставлять',  'expose', 5)).setSortable(True)
        self.addCol(
            CEnumInDocTableCol(u'Платно', 'payable', 5, [u'по событию', u'по выбору', u'обязательно'])).setSortable(
            True)
        self.addCol(CHurtCol(u'Типы вредности', 'hurtType', 'rbHurtType')).setSortable(True)
        self.addCol(CHurtCol(u'Факторы вредности', 'hurtFactorType', 'rbHurtFactorType')).setSortable(True)
        self.addCol(CPolyclinicExtendedInDocTableCol(u'Место проведения', 'defaultOrg_id', 20))

        self.actionTypeClass = actionTypeClass
        self.actionTypeIdList = self.getActionTypeIdList(actionTypeClass)

        db = QtGui.qApp.db
        table = db.table('EventType_Action')
        self.setFilter(table['actionType_id'].inlist(self.actionTypeIdList))

    def afterUpdateEditorGeometry(self, editor, index):
        if index.column() in [self.getColIndex('hurtType'), self.getColIndex('hurtFactorType')]:
            editor.resize(editor.width(), 12 * editor.height())

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        # deprecated by i3097
        # result.setValue('expose', toVariant(True))
        return result

    def getActionTypeIdList(self, actionTypeClass):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        return db.getIdList(tableActionType, 'id',
                            [tableActionType['deleted'].eq(0), tableActionType['class'].eq(actionTypeClass)])


class CAutoPrintSettingsModel(CInDocTableModel):
    class UpdateType:
        clearAll = 0
        updateExpiredDate = 1
        clearAllExpired = 2

    def __init__(self, parent=None):
        super(CAutoPrintSettingsModel, self).__init__(tableName='EventType_AutoPrint',
                                                      idFieldName='id',
                                                      masterIdFieldName='eventType_id',
                                                      parent=parent)
        tableRbPrintTemplate = QtGui.qApp.db.table('rbPrintTemplate')
        self.addCol(CRBInDocTableCol(u'Шаблон', 'printTemplate_id', 20, 'rbPrintTemplate',
                                     showFields=CRBComboBox.showCodeAndName, codeFieldName='context',
                                     filter=tableRbPrintTemplate['deleted'].eq(0))).setSortable(True)
        self.addCol(CEnumInDocTableCol(u'Триггер', 'triggerType', 5,
                                       [u'При открытии события', u'При сохранении события'])).setSortable(True)
        self.addCol(CEnumInDocTableCol(u'Повтор', 'repeatType', 5,
                                       [u'Каждый раз', u'Один раз', u'Один раз на пациента'])).setSortable(True)
        self.addCol(CEnumInDocTableCol(u'Сбрасывать повторы', 'repeatResetType', 5, [u'Не сбрасывать',
                                                                                     u'В указанную дату',
                                                                                     u'В конце месяца',
                                                                                     u'В конце года',
                                                                                     ])
                    ).setSortable(True)
        self.addCol(CDateInDocTableCol(u'Дата сброса', 'repeatResetDate', 5, canBeEmpty=True))

        self._clearRepeatsIdList = []
        self._changedRepeatResetDateIdList = []

    ## Обновляет имеющиеся Счетчики повторов
    @staticmethod
    def updateRepeatStatus(item, updateType=UpdateType.clearAll):
        masterId = forceRef(item.value('id'))
        if not masterId:
            return

        table = QtGui.qApp.db.table('EventType_AutoPrint_Repeat')
        if updateType == CAutoPrintSettingsModel.UpdateType.clearAll:
            QtGui.qApp.db.deleteRecord(table=table,
                                       where=table['master_id'].eq(masterId))
        elif updateType == CAutoPrintSettingsModel.UpdateType.updateExpiredDate:
            expiredDate = getExpiredDate(forceInt(item.value('repeatResetType')),
                                         forceDate(item.value('repeatResetDate')))
            # Установка новой даты окончания для всех счетчиков с пустой датой
            # Необходимо, если тип сброса повторов изменился с "не сбрасывать" на любой другой
            QtGui.qApp.db.updateRecords(table=table,
                                        expr=u'%s = %s' % (table['expiredDate'].name(),
                                                           table['expiredDate'].formatValue(expiredDate)),
                                        where=[table['master_id'].eq(masterId),
                                               table['expiredDate'].isNull()])
        elif updateType == CAutoPrintSettingsModel.UpdateType.clearAllExpired:
            # Удаление для указанной настройки всех счетчиков повтора с датой окончания меньше или равной сегодняшней 
            QtGui.qApp.db.deleteRecord(table=table,
                                       where=[table['master_id'].eq(masterId),
                                              table['expiredDate'].le(QtCore.QDate.currentDate())])

    def loadItems(self, masterId):
        self._clearRepeatsIdList = []
        self._changedRepeatResetDateIdList = []
        CInDocTableModel.loadItems(self, masterId)

    def saveItems(self, masterId):
        for item in self.items():
            # Обнулять дату окончания действия для всех настроек,
            # сброс повторов у которых не настроен на режим "в указанную дату" (=1)
            if forceInt(item.value('repeatResetType')) != 1:
                item.setValue('repeatResetDate', QtCore.QVariant())

            itemId = forceRef(item.value('id'))
            if itemId in self._clearRepeatsIdList:
                self.updateRepeatStatus(item, updateType=CAutoPrintSettingsModel.UpdateType.clearAll)

            # Обновлять даты окончания у всех счетчиков повторов, если задана новая
            if itemId in self._changedRepeatResetDateIdList:
                if not forceDate(item.value('repeatResetDate')).isNull():
                    self.updateRepeatStatus(item, updateType=CAutoPrintSettingsModel.UpdateType.updateExpiredDate)

            self.updateRepeatStatus(item, updateType=CAutoPrintSettingsModel.UpdateType.clearAllExpired)
        self._clearRepeatsIdList = []
        self._changedRepeatResetDateIdList = []
        CInDocTableModel.saveItems(self, masterId)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if index.column() == self.getColIndex('repeatType'):
                if QtGui.QMessageBox.Yes == QtGui.QMessageBox.warning(
                        QtGui.qApp.activeWindow(),
                        u'Подвердите смену настройки',
                        u'При смене типа повторения\n'
                        u'из базы будут удалены все метки\n'
                        u'для прошлой настройки типа\n'
                        u'\n'
                        u'Вы уверены, что хотите поменять тип повтора для шаблона?',
                        buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel,
                        defaultButton=QtGui.QMessageBox.Cancel
                ):
                    # Добавить id настройки в список тех, для которых будут стерты все прошлые счетчики повторов
                    self._clearRepeatsIdList.append(forceRef(self.value(index.row, 'id')))
                else:
                    return False
            elif index.column() == self.getColIndex('repeatResetType'):
                resetDateColIdx = self.getColIndex('repeatResetDate')
                if forceInt(value) != 1:  # Не стоит опция "сбрасывать в указанную дату
                    # Обнуление даты, если ее ввод запрещен
                    super(CAutoPrintSettingsModel, self).setData(self.index(index.row(), resetDateColIdx),
                                                                 QtCore.QVariant(),
                                                                 role=role)
            elif index.column() == self.getColIndex('repeatResetDate'):
                if self.value(index.row(), 'repeatResetDate') != forceDate(value):
                    # Добавить id настройки в список тех, для которых будут обновлены даты окончания
                    self._changedRepeatResetDateIdList.append(forceRef(self.value(index.row(), 'id')))
                    repeatResetTypeIdx = self.getColIndex('repeatResetType')
                    if value.isNull():
                        # Если дата окончания установленна в пустую, то перевести тип сброса в режим "не сбрасывать"
                        super(CAutoPrintSettingsModel, self).setData(self.index(index.row(), repeatResetTypeIdx),
                                                                     QtCore.QVariant(0),
                                                                     role=role)
                    else:
                        # Обновить дату на "день, следующий за текущим", если она меньше или равна сегодняшней
                        if forceDate(value) <= QtCore.QDate.currentDate():
                            value = QtCore.QVariant(QtCore.QDate.currentDate().addDays(1))
                        # Если дата окончания установленна не пустой, то перевести тип сброса в режим "в указанную дату"
                        super(CAutoPrintSettingsModel, self).setData(self.index(index.row(), repeatResetTypeIdx),
                                                                     QtCore.QVariant(1),
                                                                     role=role)

        return super(CAutoPrintSettingsModel, self).setData(index, value, role=role)


class CAssociationsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'EventTypeAssociations', 'id', 'master_id', parent)
        self.addCol(
            CRBInDocTableCol(u'Тип события', 'eventType_id', 2, 'EventType', showFields=CRBComboBox.showCodeAndName))
        self.addCol(CEnumInDocTableCol(
            u'Применение',
            'type',
            5,
            [
                u'запрет на создание при наличии открытого обращения',
                u'запрет на создание при отсутствии обращения',
                u'запрет на создание при отсутствии обращения за текущий год',
                u'запрет на создание при отсутсвии "Выписки"'
            ])
        )


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': '192.168.0.3',
        'port': 3306,
        'database': 'p120',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CEventTypeList(None)
    w.exec_()


if __name__ == '__main__':
    main()
