#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""
Коечный фонд
"""

from PyQt4 import QtGui, QtCore

from Events.Action                 import CAction, CActionType
from Events.ActionEditDialog       import CActionEditDialog
from Events.ActionInfo             import CActionInfo
from Events.ActionPropertiesTable  import CActionPropertiesTableModel
from Events.ActionTypeCol          import CActionTypeCol
from Events.ActionTypeDialog       import CActionTypeDialogTableModel
from Events.CreateEvent            import requestNewEvent
from Events.EditDispatcher         import getEventFormClass
from Events.EventEditDialog        import CEventEditDialog
from Events.EventFeedPage          import CFeedPageDialog
from Events.EventFeedModel         import CFeedModel
from Events.Utils                  import getActionTypeDescendants

from HospitalBeds.HospitalBedsEvent            import CHospitalBedsEventDialog
from HospitalBeds.HospitalBedsLocationCardTypeEditor import CHospitalBedsLocationCardTypeEditor
from HospitalBeds.HospitalBedsReport           import CHospitalBedsReport, CFeedReport
from HospitalBeds.HospitalizationEventDialog   import CHospitalizationEventDialog, CFindClientInfoDialog
from HospitalBeds.HospitalBedInfo              import CHospitalEventInfo
from HospitalBeds.HospitalBedEditorDialog      import CHospitalBedEditorDialog
from HospitalBeds.ProcessingReferralWindow import CProcessingReferralWindow
from HospitalBeds.RelatedEventListDialog       import CRelatedEventListDialog
from HospitalBeds.RadialSheetDialog            import CRadialSheetSetupDialog
from HospitalBeds.Utils import getActionTypeIdListByFlatCode, getOrgStructureIdList, getAgeRangeCond
from HospitalBeds.models.DeathModel import CDeathModel
from HospitalBeds.models.LeavedModel import CLeavedModel
from HospitalBeds.models.LobbyModel import CLobbyModel
from HospitalBeds.models.PresenceModel import CPresenceModel
from HospitalBeds.models.QueueModel import CQueueModel
from HospitalBeds.models.ReadyToLeaveModel import CReadyToLeaveModel
from HospitalBeds.models.ReanimationModel import CReanimationModel
from HospitalBeds.models.ReceivedModel import CReceivedModel
from HospitalBeds.models.RenunciationModel import CRenunciationModel
from HospitalBeds.models.TransferModel import CTransferModel
from HospitalBeds.models.MaternitywardModel import CMaternitywardModel
from library.RecordListLock import CRecordListLockMixin

from library.crbcombobox           import CRBComboBox
from library.database              import addCondLike, CRecordCache, CTableRecordCache
from library.DialogBase            import CDialogBase
from library.InDocTable            import CInDocTableView, CInDocTableModel, CDateInDocTableCol, CEnumInDocTableCol, \
                                          CRBInDocTableCol
from library.PreferencesMixin      import CPreferencesMixin
from library.PrintInfo             import CInfoContext
from library.PrintTemplates        import applyTemplateInt, htmlTemplate
from library.TableModel            import CTableModel, CCol, CBoolCol, CDateCol, CDateTimeFixedCol, CDesignationCol, \
                                          CEnumCol, CIntCol, CNumCol, CRefBookCol, CTextCol
from library.DateEdit              import CDateEdit
from library.TemperatureListEditor import CTemperatureListEditorDialog
from library.Utils                 import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
                                          forceStringEx, forceTime, toVariant, getPref, getVal, setPref, calcAge, \
                                          formatRecordsCount

from Orgs.OrgStructComboBoxes      import COrgStructureModel
from Orgs.Utils                    import COrgStructureInfo

from RefBooks.RBMenu               import CGetRBMenu

from Registry.AmbCardMixin         import CAmbCardMixin
from Registry.StatusObservationClientEditor import CStatusObservationClientEditor
from Registry.Utils                import getClientInfoEx, \
                                          CCheckNetMixin

from Reports.ReportBase            import CReportBase, createTable
from Reports.ReportView            import CReportViewDialog, CReportViewOrientation, CReportViewOrientationMargins
from Reports.ReportArchiveHistory  import CReportArchiveHistory
from Reports.ReportArchiveList     import CReportArchiveList

from Users.Rights                  import urAdmin, urHospitalTabPlanning, urHospitalTabReceived, urLeavedTabPresence, \
                                          urRegTabWriteRegistry, urEditHospitalBedLocationCard

from Ui_HospitalBeds                        import Ui_HospitalBedsDialog
from Ui_ReportF001Setup                     import Ui_ReportF001SetupDialog
from Ui_ReportLogbookHospitalizationSetup   import Ui_ReportLogbookHospitalizationSetupDialog
from Ui_HospitalBedsBriefSettingSetup import Ui_HospitalBedsBriefSettingSetupDialog

import temperatureList_html

from GUIHider.VisibleControlMixin import CVisibleControlMixin
from library.CheckableModel import CCheckableModel


class CPhysicalActivityModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Event_PhysicalActivity', 'id', 'event_id', parent)
        self.addCol(CDateInDocTableCol(u'Дата режима', 'date', 20, low = 0, high = 100))
        self.addCol(CRBInDocTableCol(u'Режим', 'physicalActivityMode_id', 20, 'rbPhysicalActivityMode', showFields = CRBComboBox.showName, addNone = False))


class CSettingSetupDialog(CDialogBase, Ui_HospitalBedsBriefSettingSetupDialog):
    def __init__(self, parent=None, model=None, tableName='', additionalColumn=None):
        if not additionalColumn:
            additionalColumn = []
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.lstColumn.setColumnWidth(0, 130)
        self.tableModel = CTableColumnModel(None, model, additionalColumn)
        if model:
            self.lstColumn.setModel(self.tableModel)

        self.tableNameFontSize = ''
        self.tableName = tableName

        self.tableNameFontSize = self.tableName + 'FontSize'
        self.edtFontSize.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, self.tableNameFontSize, None)))
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, self.tableName, {})
        self.tableModel.loadPreferences(preferences)

    def params(self):
        result = {}
        result['columnName'] = self.lstColumn.nameValues()
        result['fontSize'] = self.edtFontSize.Text()
        return result

    @QtCore.pyqtSlot()
    def on_chkAll_clicked(self):
        if self.chkNothing.isChecked():
            self.chkNothing.setChecked(False)
        if self.chkAll.isChecked():
            itemsCheckeds = [True] * self.tableModel.rowCount(None)
            self.lstColumn.model().setModelData(itemsCheckeds)
            self.lstColumn.model().emitDataChanged()

    @QtCore.pyqtSlot()
    def on_chkNothing_clicked(self):
        if self.chkAll.isChecked():
            self.chkAll.setChecked(False)
        if self.chkNothing.isChecked():
            itemsCheckeds = [False] * self.tableModel.rowCount(None)
            self.lstColumn.model().setModelData(itemsCheckeds)
            self.lstColumn.model().emitDataChanged()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            preferences = self.tableModel.savePreferences()
            setPref(QtGui.qApp.preferences.windowPrefs, self.tableName, preferences)
            QtGui.qApp.preferences.appPrefs[self.tableNameFontSize] = toVariant(self.edtFontSize.text())


class CTableColumnModel(QtCore.QAbstractTableModel, CPreferencesMixin):
    def __init__(self, parent=None, tableModel=None, additionalColumn=None):
        if not additionalColumn:
            additionalColumn = []
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.tableModel = tableModel
        self.itemsNames = []
        self.itemsCheckeds = [True] * (tableModel.columnCount() + len(additionalColumn))
        self.additionalColumn = additionalColumn

    def rowCount(self, parent):
        return self.tableModel.columnCount() + len(self.additionalColumn)

    def columnCount(self, parent):
        return 2

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col == 0:
                return QtCore.QVariant(QtCore.QString(u"Название столбцов"))
            else:
                return QtCore.QVariant(QtCore.QString(u"Выводить столбцы"))
        return QtCore.QVariant()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if index.column() == 0 and role == QtCore.Qt.DisplayRole:
            if index.row() < self.tableModel.columnCount():
                self.itemsNames.append(self.tableModel.headerData(index.row(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole))
                return self.tableModel.headerData(index.row(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            else:
                self.itemsNames.append(self.additionalColumn[index.row() - self.tableModel.columnCount()])
                return self.additionalColumn[index.row() - self.tableModel.columnCount()]
        if index.column() == 1 and role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked if self.itemsCheckeds[index.row()] else QtCore.Qt.Unchecked
        return QtCore.QVariant()

    def flags(self, QModelIndex):
        return QtCore.QAbstractTableModel.flags(self, QModelIndex) | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable

    def setData(self, index, value, role):
        if role == QtCore.Qt.CheckStateRole:
            row = index.row()
            self.itemsCheckeds[row] = forceBool(value)
        return True

    def getModelData(self):
        return self.itemsCheckeds

    def setModelData(self, itemsCheckeds):
        self.itemsCheckeds = itemsCheckeds

    def emitDataChanged(self):
        index1 = self.index(0, 1)
        index2 = self.index(self.tableModel.columnCount(), 1)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index1, index2)

    def loadPreferences(self, preferences):
        model = self.tableModel
        if model:
            for i in xrange(model.columnCount() + len(self.additionalColumn)):
                checkeds = forceBool(getPref(preferences, 'col_'+str(i), None))
                self.itemsCheckeds[i] = checkeds

    def savePreferences(self):
        preferences = {}
        model = self.tableModel
        if model:
            for i in xrange(model.columnCount() + len(self.additionalColumn)):
                checkeds = self.itemsCheckeds[i]
                setPref(preferences, 'col_'+str(i), QtCore.QVariant(checkeds))
        return preferences


class CHospitalBedsDialog(CDialogBase, CAmbCardMixin, CCheckNetMixin, CVisibleControlMixin, CRecordListLockMixin, Ui_HospitalBedsDialog):

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        CCheckNetMixin.__init__(self)
        CRecordListLockMixin.__init__(self)

        self.filterByExactTime = QtGui.qApp.filterByExactTime()

        # Словарь, содержащий для каждой вкладки (доступ по индексу) список действий (QAction) дополнительной печати
        self._additionalPrintActions = {}

        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId()))
        self.addModels('HospitalBeds', CHospitalBedsModel(self))
        self.addModels('InvoluteBeds',  CInvoluteBedsModel(self))
        self.addModels('Presence', CPresenceModel(self))
        self.addModels('ActionList', CHospitalActionsTableModel(self))
        self.addModels('ActionsStatus', CAttendanceActionsTableModel(self))
        self.addModels('ActionsStatusProperties', CActionPropertiesTableModel(self))
        self.addModels('ActionsDiagnostic', CAttendanceActionsTableModel(self))
        self.addModels('ActionsDiagnosticProperties', CActionPropertiesTableModel(self))
        self.addModels('ActionsCure', CAttendanceActionsTableModel(self))
        self.addModels('ActionsCureProperties', CActionPropertiesTableModel(self))
        self.addModels('ActionsMisc', CAttendanceActionsTableModel(self))
        self.addModels('ActionsMiscProperties', CActionPropertiesTableModel(self))
        self.addModels('Received', CReceivedModel(self))
        self.addModels('Transfer', CTransferModel(self))
        self.addModels('Leaved', CLeavedModel(self))
        self.addModels('ReabyToLeave', CReadyToLeaveModel(self))
        self.addModels('Queue', CQueueModel(self))
        self.addModels('Renunciation', CRenunciationModel(self))
        self.addModels('Death', CDeathModel(self))
        self.addModels('Reanimation', CReanimationModel(self))
        self.addModels('Lobby', CLobbyModel(self))
        self.addModels('Maternityward', CMaternitywardModel(self))
        self.btnPrint = QtGui.QPushButton(u'Печать', self)
        self.btnPrint.setObjectName('btnPrint')
        self.btnTemperatureList = QtGui.QPushButton(u'Температурный лист (F8)', self)
        self.btnTemperatureList.setObjectName('btnTemperatureList')
        self.btnFeed = QtGui.QPushButton(u'Питание', self)
        self.btnFeed.setObjectName('btnFeed')
        self.btnRadialSheet = QtGui.QPushButton(u'Листок облучения', self)
        self.btnRadialSheet.setObjectName('btnRadialSheet')

        self.setupHospitalBedsMenu()
        self.setupEditActionEventMenu()
        self.setupBtnPrintMenu()
        self.setupBtnFeedMenu()
        self.setupUi(self)
        self.cmbFilterActionList.clear()
        self.cmbFilterActionList.addItems([u'Не учитывать'] + CActionType.retranslateClass(False).statusNames)
        self.cmbFilterActionStatus.clear()
        self.cmbFilterActionStatus.addItems([u'Не учитывать'] + CActionType.retranslateClass(False).statusNames)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        self.setModels(self.tblHospitalBeds,  self.modelHospitalBeds, self.selectionModelHospitalBeds)
        self.setModels(self.tblInvoluteBeds, self.modelInvoluteBeds, self.selectionModelInvoluteBeds)
        self.setModels(self.tblPresence,  self.modelPresence, self.selectionModelPresence)
        self.setModels(self.tblActionList,  self.modelActionList, self.selectionModelActionList)
        self.setModels(self.tblActionsStatus, self.modelActionsStatus, self.selectionModelActionsStatus)
        self.setModels(self.tblActionsStatusProperties, self.modelActionsStatusProperties, self.selectionModelActionsStatusProperties)
        self.setModels(self.tblActionsDiagnostic, self.modelActionsDiagnostic, self.selectionModelActionsDiagnostic)
        self.setModels(self.tblActionsDiagnosticProperties, self.modelActionsDiagnosticProperties, self.selectionModelActionsDiagnosticProperties)
        self.setModels(self.tblActionsCure, self.modelActionsCure, self.selectionModelActionsCure)
        self.setModels(self.tblActionsCureProperties, self.modelActionsCureProperties, self.selectionModelActionsCureProperties)
        self.setModels(self.tblActionsMisc, self.modelActionsMisc, self.selectionModelActionsMisc)
        self.setModels(self.tblActionsMiscProperties, self.modelActionsMiscProperties, self.selectionModelActionsMiscProperties)
        self.setModels(self.tblReceived,  self.modelReceived, self.selectionModelReceived)
        self.setModels(self.tblTransfer,  self.modelTransfer, self.selectionModelTransfer)
        self.setModels(self.tblLeaved,  self.modelLeaved, self.selectionModelLeaved)
        self.setModels(self.tblReabyToLeave,  self.modelReabyToLeave, self.selectionModelReabyToLeave)
        self.setModels(self.tblQueue,  self.modelQueue, self.selectionModelQueue)
        self.setModels(self.tblRenunciation,  self.modelRenunciation, self.selectionModelRenunciation)
        self.setModels(self.tblDeath,  self.modelDeath, self.selectionModelDeath)
        self.setModels(self.tblReanimation,  self.modelReanimation, self.selectionModelReanimation)
        self.setModels(self.tblLobby, self.modelLobby, self.selectionModelLobby)
        self.setModels(self.tblMaternityward,  self.modelMaternityward, self.selectionModelMaternityward)

        self.cmbFilterType.setTable('rbHospitalBedType', addNone=True)
        self.cmbFilterProfile.setTable('rbHospitalBedProfile', addNone=True)
        self.cmbFilterSchedule.setTable('rbHospitalBedShedule', addNone=True)
        self.cmbFilterAccountingSystem.setTable('rbAccountingSystem',  True)
        self.cmbFilterAccountingSystem.setValue(forceRef(getVal(
            QtGui.qApp.preferences.appPrefs, 'FilterAccountingSystem', 0)))
        self.cmbStatusObservation.setTable('rbStatusObservationClientType',  True)
        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbAttachType.setTable('rbAttachType', addNone=True)
        self.cmbLocationCard.setTable('rbHospitalBedsLocationCardType', addNone=True)
        self.edtFilterBegDate.canBeEmpty()
        self.edtFilterEndDate.canBeEmpty()
        self.buttonBox.addButton(self.btnFeed, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnTemperatureList, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnRadialSheet, QtGui.QDialogButtonBox.ActionRole)
        self.btnTemperatureList.setShortcut(QtCore.Qt.Key_F8)
        self.btnPrint.setMenu(self.mnuBtnPrint)
        self.btnFeed.setMenu(self.mnuBtnFeed)
        self.tblHospitalBeds.setPopupMenu(self.mnuHospitalBeds)
        self.tblPresence.setPopupMenu(self.mnuHospitalBeds)
        self.tblActionsStatus.setPopupMenu(self.mnuEditActionEvent)
        self.tblActionsDiagnostic.setPopupMenu(self.mnuEditActionEvent)
        self.tblActionsCure.setPopupMenu(self.mnuEditActionEvent)
        self.tblActionsMisc.setPopupMenu(self.mnuEditActionEvent)
        self.tblActionsStatusProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblActionsDiagnosticProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblActionsCureProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblActionsMiscProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblReceived.setPopupMenu(self.mnuHospitalBeds)
        self.tblTransfer.setPopupMenu(self.mnuHospitalBeds)
        self.tblLeaved.setPopupMenu(self.mnuHospitalBeds)
        self.tblReabyToLeave.setPopupMenu(self.mnuHospitalBeds)
        self.tblQueue.setPopupMenu(self.mnuHospitalBeds)
        self.tblRenunciation.setPopupMenu(self.mnuHospitalBeds)
        self.tblDeath.setPopupMenu(self.mnuHospitalBeds)
        self.tblReanimation.setPopupMenu(self.mnuHospitalBeds)
        self.tblLobby.setPopupMenu(self.mnuHospitalBeds)
        self.tblMaternityward.setPopupMenu(self.mnuEditActionEvent)
        self.reasonRenunciation()
        self.reasonRenunciateDeath()
        self.cmbInvolute.setEnabled(False)
        self.resetFilter()
        orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
        self.filterAsText = ''
        self.btnLeavedEvent = False
        self.notSelectedRows = True

        self.__actionTypeIdListByClassPage = [None] * 4
        self.grbActionFilter.setVisible(False)
        self.cmbFilterActionList.setCurrentIndex(1)
        self.cmbFilterActionStatus.setCurrentIndex(1)
        self.tblActionsStatus.setClientInfoHidden(False)
        self.tblActionsDiagnostic.setClientInfoHidden(False)
        self.tblActionsCure.setClientInfoHidden(False)
        self.tblActionsMisc.setClientInfoHidden(False)
        self.cmbPerson.setOnlyDoctorsIfUnknowPost(True)
        self.cmbPerson.setSpecialityId(None)
        self.tblPresence.horizontalHeader().setClickable(True)
        self.tblReceived.horizontalHeader().setClickable(True)
        self.tblTransfer.horizontalHeader().setClickable(True)
        self.tblLeaved.horizontalHeader().setClickable(True)
        self.tblRenunciation.horizontalHeader().setClickable(True)
        self.tblQueue.horizontalHeader().setClickable(True)

        tableViewList = [self.tblPresence,
                         self.tblReceived,
                         self.tblTransfer,
                         self.tblLeaved,
                         self.tblReabyToLeave,
                         self.tblQueue,
                         self.tblRenunciation,
                         self.tblDeath,
                         self.tblReanimation,
                         self.tblLobby,
                         self.tblMaternityward]
        for tableView in tableViewList:
            tableView.setSortingEnabled(True)

        self.initAdditionalPrintActions()

        self._invisibleObjectsNameList = self.reduceNames(QtGui.qApp.userInfo.hiddenObjectsNameList([self.moduleName()])) \
                                         if QtGui.qApp.userInfo else []
        self.updateVisibleState(self, self._invisibleObjectsNameList)
        self.tabWidget.currentChanged.connect(self.currentTabChanged)

        if orgStructureIndex and orgStructureIndex.isValid():
            self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
            self.treeOrgStructure.setExpanded(orgStructureIndex, True)
        else:
            self.updateHospitalBeds()

        tabIndex = self.tabWidget.indexOf(self.tabPresence)
        if tabIndex == -1:
            tabIndex = 0
        if self.tabWidget.currentIndex() == tabIndex:
            self.currentTabChanged(tabIndex)
        else:
            self.tabWidget.setCurrentIndex(tabIndex)

        self.cmbFeed.setVisible(False)
        self.edtDateFeed.setVisible(False)
        self.lblFeed.setVisible(False)
        self.lblDateFeed.setVisible(False)







    @staticmethod
    def moduleName():
        return u'HospitalBedsDialog'


    @staticmethod
    def moduleTitle():
        return u'Стационарный монитор'


    @classmethod
    def hiddableChildren(cls):
        #TODO: atronah: решить проблему с игнором смены имен в файле интерфейса
        # один из вариантов решения: парсить ui-файл
        nameList = []
        nameList.append((u'tabFund', u'Коечный фонд')) #0
        table = u'tabFund.tblHospitalBeds:'
        nameList.extend([
                        (table + u'code', u'Колонка \'Код\''),
                        (table + u'isPermanent', u'Колонка \'Штат\''),
                        (table + u'type_id', u'Колонка \'Тип\''),
                        (table + u'profile_id', u'Колонка \'Профиль\''),
                        (table + u'relief', u'Колонка \'Смены\''),
                        (table + u'schedule_id', u'Колонка \'Режим\''),
                        (table + u'begDate', u'Колонка \'Начало\''),
                        (table + u'endDate', u'Колонка \'Окончание\''),
                        (table + u'master_id', u'Колонка \'Подразделение\''),
                        (table + u'name', u'Колонка \'Наименование\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'sex', u'Колонка \'Пол\'')
                        ])

        nameList.append((u'tabPresence', u'Присутствуют')) #1
        table = u'tabPresence.tblPresence:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'feed', u'Колонка \'П\''),
                        (table + u'physicalActivityName', u'Колонка \'Р\''),
                        (table + u'comfortableDate', u'Колонка \'К\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'isUnconscious', u'Колонка \'БС\''),
                        # (table + u'isVIP', u'Колонка \'VIP\''),
                        (table + u'begDateString', u'Колонка \'Поступил\''),
                        (table + u'plannedEndDate', u'Колонка \'Плановая дата выбытия\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'provisionalDiagnosis', u'Колонка \'Предварительный диагноз\''),
                        (table + u'admissionDiagnosis', u'Колонка \'Диагноз приёмного отделения\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'profileBed', u'Колонка \'Профиль койки\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\''),
                        (table + u'patronage', u'Колонка \'Уход\''),
                        (table + u'quota', u'Колонка \'Квота\''),
                        (table + u'snils', u'Колонка \'СНИЛС\'')
                         ])

        nameList.append((u'tabReceived', u'Поступили')) #2
        table = u'tabReceived.tblReceived:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'feed', u'Колонка \'П\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'begDateReceived', u'Колонка \'Госпитализирован\''),
                        (table + u'begDateString', u'Колонка \'Поступил\''),
                        (table + u'endDate', u'Колонка \'Выбыл\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'provisionalDiagnosis', u'Колонка \'Предварительный диагноз\''),
                        (table + u'admissionDiagnosis', u'Колонка \'Диагноз приёмного отделения\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'profileBed', u'Колонка \'Профиль койки\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\''),
                        (table + u'patronage', u'Колонка \'Уход\''),
                        (table + u'quota', u'Колонка \'Квота\''),
                        (table + u'snils', u'Колонка \'СНИЛС\'')
                         ])

        nameList.append((u'tabTransfer', u'Переведены')) #3
        table = u'tabTransfer.tblTransfer:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'feed', u'Колонка \'П\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'begDateReceived', u'Колонка \'Госпитализирован\''),
                        (table + u'begDateString', u'Колонка \'Поступил\''),
                        (table + u'endDate', u'Колонка \'Выбыл\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'profileBed', u'Колонка \'Профиль койки\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'nameFromOS', u'Колонка \'Переведен из\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\''),
                        (table + u'patronage', u'Колонка \'Уход\'')
                         ])

        nameList.append((u'tabLeaved', u'Выбыли')) #4
        table = u'tabLeaved.tblLeaved:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'locationCardName', u'Колонка \'И/Б\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'feed', u'Колонка \'П\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'begDateReceived', u'Колонка \'Госпитализирован\''),
                        (table + u'begDateString', u'Колонка \'Поступил\''),
                        (table + u'endDate', u'Колонка \'Выбыл\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'profileBed', u'Колонка \'Профиль койки\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\''),
                        (table + u'quota', u'Колонка \'Квота\''),
                        (table + u'snils', u'Колонка \'СНИЛС\'')
                         ])

        nameList.append((u'tabReabyToLeave', u'Готовы к выбытию')) #5
        table = u'tabReabyToLeave.tblReabyToLeave:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'feed', u'Колонка \'П\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'begDateReceived', u'Колонка \'Госпитализирован\''),
                        (table + u'begDateString', u'Колонка \'Поступил\''),
                        (table + u'plannedEndDate', u'Колонка \'Плановая дата выбытия\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\''),
                        (table + u'quota', u'Колонка \'Квота\'')
                         ])

        nameList.append((u'tabQueue', u'В очереди')) #6
        table = u'tabQueue.tblQueue:'
        nameList.extend([
                        (table + u'begDate', u'Колонка \'Дата назначения\''),
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'directionDate', u'Колонка \'Поставлен\''),
                        (table + u'plannedEndDate', u'Колонка \'Плановая дата госпитализации\''),
                        (table + u'waitingDays', u'Колонка \'Ожидание\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\'')
                         ])

        nameList.append((u'tabRenunciation', u'Отказ от госпитализации')) #7
        table = u'tabRenunciation.tblRenunciation:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'begDateString', u'Колонка \'Поступил\''),
                        (table + u'endDate', u'Колонка \'Выбыл\''),
                        (table + u'nameRenunciate', u'Колонка \'Причина отказа\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\'')
                         ])

        nameList.append((u'tabDeath', u'Умерло')) #8
        table = u'tabDeath.tblDeath:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'begDateReceived', u'Колонка \'Госпитализирован\''),
                        (table + u'endDate', u'Колонка \'Выбыл\''),
                        (table + u'MKB', u'Колонка \'МКБ\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'namePerson', u'Колонка \'Ответственный\'')
                         ])
        nameList.append((u'tabReanimation', u'Реанимация')) #9
        table = u'tabReanimation.tblReanimation:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'feed', u'Колонка \'П\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'reanimationBegDate', u'Колонка \'Реанимирован\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'nameFromOS', u'Колонка \'Переведен из\''),
                        (table + u'currentCommonOSName', u'Колонка \'Числится за\'')
                         ])
        nameList.append((u'tabLobby', u'Приёмное отделение')) #10
        table = u'tabLobby.tblLobby:'
        nameList.extend([
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'namePerson', u'Колонка \'Врач\''),
                        (table + u'actionName', u'Колонка \'Действие\''),
                        (table + u'result', u'Колонка \'Результат\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'codeBed', u'Колонка \'Койка\''),
                        (table + u'begDate', u'Колонка \'Начало\''),
                        (table + u'endDate', u'Колонка \'Окончание\'')
                        ])
        nameList.append((u'tabMaternityward', u'Родовое отделение')) #11
        table = u'tabMaternityward.tblMaternityward:'
        nameList.extend([
                        (table + u'statusObservationCode', u'Колонка \'С\''),
                        (table + u'codeFinance', u'Колонка \'И\''),
                        (table + u'contractInfo', u'Колонка \'Д\''),
                        (table + u'feed', u'Колонка \'П\''),
                        (table + u'clientId', u'Колонка \'Номер\''),
                        (table + u'externalId', u'Колонка \'Карта\''),
                        (table + u'clientName', u'Колонка \'ФИО\''),
                        (table + u'sex', u'Колонка \'Пол\''),
                        (table + u'birthDate', u'Колонка \'Дата рождения\''),
                        (table + u'age', u'Колонка \'Возраст\''),
                        (table + u'employable', u'Колонка \'Трудоспособный возраст\''),
                        (table + u'reanimationBegDate', u'Колонка \'Реанимирован\''),
                        (table + u'nameOS', u'Колонка \'Подразделение\''),
                        (table + u'nameFromOS', u'Колонка \'Переведен из\''),
                        (table + u'currentCommonOSName', u'Колонка \'Числится за\'')
                         ])

        return cls.normalizeHiddableChildren(nameList)

    def fastEventFeedEdit(self, model, row):
        eventId = model.items[row].get('eventId', 0)
        clientId = model.items[row].get('clientId', 0)
        if self.lockList('Event', [eventId]):
            try:
                feedDialog = CFeedPageDialog(self)
                feedDialog.setClientId(clientId)
                feedDialog.loadData(eventId)
                if feedDialog.exec_():
                    model.loadData(self.getFilter())
            finally:
                self.releaseLockList()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblPresence_doubleClicked(self, index):
        if index.isValid():
            model = self.tblPresence.model()
            row = index.row()
            column = model.cols()[index.column()]
            columnFieldNames = column.fields()
            if 'codeBed' in columnFieldNames:
                actionId         = model.items[row].get('actionId', 0)
                actionTypeId     = model.items[row].get('actionTypeId', 0)
                clientId         = model.items[row].get('clientId', 0)
                actionTypeIdList = getActionTypeIdListByFlatCode(u'moving%')
                if actionId and (actionTypeId and actionTypeId in actionTypeIdList) and clientId:
                    db = QtGui.qApp.db
                    templateRecord = db.getRecord('Action', '*', actionId)
                    action = CAction(record=templateRecord)
                    if action:
                        dialog = CHospitalBedEditorDialog(self)
                        dialog.cmbHospitalBed.setPlannedEndDate(forceDate(action._record.value('plannedEndDate')))
                        bedId = forceRef(action[u'койка'])
                        if bedId:
                            orgStructureId = forceRef(QtGui.qApp.db.translate('OrgStructure_HospitalBed', 'id', bedId, 'master_id'))
                        else:
                            orgStructureId = action[u'Отделение пребывания'] if (u'moving' in action._actionType.flatCode.lower()) else None
                        sex = forceInt(QtGui.qApp.db.translate('Client', 'id', clientId, 'sex'))
                        dialog.cmbHospitalBed.setOrgStructureId(orgStructureId)
                        dialog.cmbHospitalBed.setBedId(bedId)
                        dialog.cmbHospitalBed.setSex(sex)
                        dialog.cmbHospitalBed.setDomain('')
                        dialog.cmbHospitalBed.setValue(bedId)
                        if dialog.exec_():
                            bedId = dialog.values()
                            if bedId:
                                eventId = forceRef(action._record.value('event_id'))
                                if CEventEditDialog(self).checkMovingBeds(clientId, eventId, actionId, forceDateTime(action._record.value('begDate')), forceDateTime(action._record.value('endDate')), None, 0, 0, None):
                                    action[u'койка'] = bedId
                                    action.save()
                                    self.loadDataPresence()
                else:
                    self.on_actOpenEvent_triggered()
            elif 'feed' in columnFieldNames:
                self.fastEventFeedEdit(model, row)
            elif 'physicalActivityName' in columnFieldNames:
                eventId = model.items[row].get('eventId', 0)

                physicalActivityDialog = CDialogBase(self)
                physicalActivityModel = CPhysicalActivityModel(physicalActivityDialog)
                if eventId:
                    physicalActivityModel.loadItems(eventId)

                #setup UI
                mainLayout = QtGui.QVBoxLayout(physicalActivityDialog)

                tblPhysicalActivity = CInDocTableView(physicalActivityDialog)
                tblPhysicalActivity.setModel(physicalActivityModel)
                tblPhysicalActivity.addPopupDelRow()
                tblPhysicalActivity.addPopupRecordProperies()
                mainLayout.addWidget(tblPhysicalActivity)

                buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                                   QtCore.Qt.Horizontal,
                                                   physicalActivityDialog)
                physicalActivityDialog.connect(buttonBox, QtCore.SIGNAL('accepted()'), physicalActivityDialog, QtCore.SLOT('accept()'))
                physicalActivityDialog.connect(buttonBox, QtCore.SIGNAL('rejected()'), physicalActivityDialog, QtCore.SLOT('reject()'))
                mainLayout.addWidget(buttonBox)

                physicalActivityDialog.setLayout(mainLayout)
                #end setup UI

                if physicalActivityDialog.exec_():
                    physicalActivityModel.saveItems(eventId)
                    self.loadDataPresence()
            else:
                self.on_actOpenEvent_triggered()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblReceived_doubleClicked(self, index):
        if index.isValid():
            model = self.tblReceived.model()
            row = index.row()
            column = model.cols()[index.column()]
            columnFieldNames = column.fields()
            if 'feed' in columnFieldNames:
                self.fastEventFeedEdit(model, row)
            else:
                self.on_actOpenEvent_triggered()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblTransfer_doubleClicked(self, index):
        self.on_actOpenEvent_triggered()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblLeaved_doubleClicked(self, index):
        if index.isValid():
            model = self.tblLeaved.model()
            row = index.row()
            column = model.cols()[index.column()]
            columnFieldNames = column.fields()
            if 'feed' in columnFieldNames:
                self.fastEventFeedEdit(model, row)
            else:
                self.tabLeaved.enabledChange(True)
                if index.column() == 1:
                    self.changeHBLocation([self.tblLeaved.model().items[row].get('eventId', 0)])
                else:
                    self.on_actOpenEvent_triggered()


    def changeHBLocation(self, eventIdList):
        model = self.tblLeaved.model()
        if eventIdList:
            if QtGui.qApp.userHasAnyRight([urAdmin, urEditHospitalBedLocationCard]):
                dialog = CHospitalBedsLocationCardTypeEditor(self, eventIdList)
                if dialog.exec_():
                    model.loadData(self.getFilter()) #если вариант будет работать медленно, нужно реализовать вариант явного изменения ячейки, без перезагрузки всей таблицы

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblReabyToLeave_doubleClicked(self, index):
        self.on_actOpenEvent_triggered()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblQueue_doubleClicked(self, index):
        self.on_actOpenEvent_triggered()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblRenunciation_doubleClicked(self, index):
        self.on_actOpenEvent_triggered()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblDeath_doubleClicked(self, index):
        self.on_actOpenEvent_triggered()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblReanimation_doubleClicked(self, index):
        if index.isValid():
            model = self.tblReanimation.model()
            row = index.row()
            column = model.cols()[index.column()]
            columnFieldNames = column.fields()
            if 'feed' in columnFieldNames:
                self.fastEventFeedEdit(model, row)
            else:
                self.on_actOpenEvent_triggered()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblLobby_doubleClicked(self, index):
        self.on_actOpenEvent_triggered()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblMaternityward_doubleClicked(self, index):
        if index.isValid():
            model = self.tblMaternityward.model()
            row = index.row()
            column = model.cols()[index.column()]
            columnFieldNames = column.fields()
            if 'feed' in columnFieldNames:
                self.fastEventFeedEdit(model, row)
            else:
                self.on_actOpenEvent_triggered()

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            numericKeys = [QtCore.Qt.Key_1, QtCore.Qt.Key_2, QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5,
                           QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8, QtCore.Qt.Key_9]
            if key == QtCore.Qt.Key_Tab:
                index = self.tabWidget.currentIndex()
                lastIndex = self.tabWidget.count() - 1
                nextIndexFound = False
                nextIndex = index
                while not nextIndexFound:
                    if nextIndex == lastIndex:
                        nextIndex = 0
                    else:
                        nextIndex += 1
                    if self.tabWidget.isTabEnabled(nextIndex) or nextIndex == index:
                        nextIndexFound = True
                self.tabWidget.setCurrentIndex(nextIndex)
                self.setFocus(QtCore.Qt.TabFocusReason)
            elif key in numericKeys:
                nextIndex = int(event.text()) - 1
                if nextIndex <= self.tabWidget.count() and self.tabWidget.isTabEnabled(nextIndex):
                    self.tabWidget.setCurrentIndex(nextIndex)
                    self.setFocus(QtCore.Qt.OtherFocusReason)
            elif key == QtCore.Qt.Key_0:
                self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
                self.setFocus(QtCore.Qt.OtherFocusReason)

    def setupHospitalBedsMenu(self):
        self.mnuHospitalBeds = QtGui.QMenu(self)
        self.mnuHospitalBeds.setObjectName('mnuHospitalBeds')
        self.actOpenEvent = QtGui.QAction(u'Открыть обращение', self)
        self.actOpenEvent.setObjectName('actOpenEvent')
        self.actRecreateEventWithAnotherType = QtGui.QAction(u'Сменить тип события', self)
        self.actRecreateEventWithAnotherType.setObjectName('actRecreateEventWithAnotherType')
        self.actEditClientInfoBeds = QtGui.QAction(u'Редактировать карту пациента', self)
        self.actEditClientInfoBeds.setObjectName('actEditClientInfoBeds')
        self.actGetFeedFromMenu = QtGui.QAction(u'Назначить питание по шаблону', self)
        self.actGetFeedFromMenu.setObjectName('actGetFeedFromMenu')
        self.actTemperatureListEditor = QtGui.QAction(u'Редактор температурного листа', self)
        self.actTemperatureListEditor.setObjectName('actTemperatureListEditor')
        self.actStatusObservationClient = QtGui.QAction(u'Изменить статус наблюдения пациента', self)
        self.actStatusObservationClient.setObjectName('actStatusObservationClient')
        self.actRelatedEventClient = QtGui.QAction(u'Показать стандарты и диагнозы других отделений', self)
        self.actRelatedEventClient.setObjectName('actRelatedEventClient')
        self.actMultipleHBLocationCardChange = QtGui.QAction(u'Изменить место нахождения истории болезни', self)
        self.actMultipleHBLocationCardChange.setObjectName('actMultipleHBLocationCardChange')
        self.mnuHospitalBeds.addAction(self.actOpenEvent)
        self.mnuHospitalBeds.addAction(self.actRecreateEventWithAnotherType)
        self.mnuHospitalBeds.addAction(self.actEditClientInfoBeds)
        self.mnuHospitalBeds.addAction(self.actGetFeedFromMenu)
        self.mnuHospitalBeds.addAction(self.actTemperatureListEditor)
        self.mnuHospitalBeds.addAction(self.actStatusObservationClient)
        self.mnuHospitalBeds.addAction(self.actRelatedEventClient)
        self.mnuHospitalBeds.addAction(self.actMultipleHBLocationCardChange)


    def setupEditActionEventMenu(self):
        self.mnuEditActionEvent = QtGui.QMenu(self)
        self.mnuEditActionEvent.setObjectName('mnuEditActionEvent')
        self.actEditActionEvent = QtGui.QAction(u'Открыть обращение', self)
        self.actEditActionEvent.setObjectName('actEditActionEvent')
        self.actEditClientInfo = QtGui.QAction(u'Редактировать карту пациента', self)
        self.actEditClientInfo.setObjectName('actEditClientInfo')
        self.actEditStatusObservationClient = QtGui.QAction(u'Изменить статус наблюдения пациента', self)
        self.actEditStatusObservationClient.setObjectName('actEditStatusObservationClient')
        self.actGetFeedFromMenu = QtGui.QAction(u'Назначить питание по шаблону', self)
        self.actGetFeedFromMenu.setObjectName('actGetFeedFromMenu')
        self.mnuEditActionEvent.addAction(self.actEditClientInfo)
        self.mnuEditActionEvent.addAction(self.actEditActionEvent)
        self.mnuEditActionEvent.addAction(self.actEditStatusObservationClient)
        self.mnuEditActionEvent.addAction(self.actGetFeedFromMenu)


    def setupBtnPrintMenu(self):
        self.mnuBtnPrint = QtGui.QMenu(self)
        self.mnuBtnPrint.setObjectName('mnuBtnPrint')
        self.actPrintReport = QtGui.QAction(u'Сводка', self)
        self.actPrintReport.setObjectName('actPrintReport')
        self.actReportLeaved = QtGui.QAction(u'Сводка по выписке', self)
        self.actReportLeaved.setObjectName('actReportLeaved')
        self.actPrintJournal = QtGui.QAction(u'Журнал', self)
        self.actPrintJournal.setObjectName('actPrintJournal')
        self.actPrintFeedReport = QtGui.QAction(u'Порционник', self)
        self.actPrintFeedReport.setObjectName('actPrintFeedReport')
        self.actPrintThermalSheet = QtGui.QAction(u'Температурный лист (список)', self)
        self.actPrintThermalSheet.setObjectName('actPrintThermalSheet')
        self.actPrintLogbookHospitalization = QtGui.QAction(u'Журнал учёта госпитализации', self)
        self.actPrintLogbookHospitalization.setObjectName('actPrintLogbookHospitalization')
        self.menuAdditionalPrint =  QtGui.QMenu(u'Дополнительно', self)
        self.menuAdditionalPrint.setObjectName('menuAdditionalPrint')

        self.mnuBtnPrint.addAction(self.actPrintReport)
        self.mnuBtnPrint.addAction(self.actReportLeaved)
        self.mnuBtnPrint.addAction(self.actPrintJournal)
        self.mnuBtnPrint.addAction(self.actPrintFeedReport)
        self.mnuBtnPrint.addAction(self.actPrintThermalSheet)
        self.mnuBtnPrint.addAction(self.actPrintLogbookHospitalization)
        self.mnuBtnPrint.addMenu(self.menuAdditionalPrint)



    def initAdditionalPrintActions(self):
        self._additionalPrintActions.clear()

        # инициализация отчетов для вкладки "Отказы от госпитализации"
        actionList = self._additionalPrintActions.setdefault(self.tabRenunciation, [])
        actionList.append(QtGui.QAction(u'Отказы от госпитализации', self, triggered=self.printRenunciationsReport))
        actionList.append(QtGui.QAction(u'Отказы от госпитализации (расширенный отчет)', self, triggered=self.printRenunciationsVerboseReport))


        # инициализация отчётов для вкладки "Выбыли"
        actionList = self._additionalPrintActions.setdefault(self.tabLeaved, [])
        actionList.append(QtGui.QAction(u'Архив историй болезни', self, triggered=self.printReportArchiveHistory))
        actionList.append(QtGui.QAction(u'Архивный список', self, triggered=self.printReportArchiveList))

        # инициализация отчетов для вкладки "Отказы от госпитализации"
        actionList = self._additionalPrintActions.setdefault(self.tabReceived, [])
        actionList.append(QtGui.QAction(u'Список поступивших больных', self, triggered=self.printReceivedReport))
        actionList.append(QtGui.QAction(u'Список поступивших больных (для онко)', self, triggered=self.printReceivedOnkoReport))



    def updatePrintMenu(self):
        reportActions = self._additionalPrintActions.get(self.tabWidget.currentWidget(), [])
        self.menuAdditionalPrint.clear()
        for action in reportActions:
            self.menuAdditionalPrint.addAction(action)
        self.menuAdditionalPrint.menuAction().setEnabled(bool(reportActions))



    def setupBtnFeedMenu(self):
        self.mnuBtnFeed = QtGui.QMenu(self)
        self.mnuBtnFeed.setObjectName('mnuBtnFeed')
        self.actSelectAllFeed = QtGui.QAction(u'Выделить всех с питанием', self)
        self.actSelectAllFeed.setObjectName('actSelectAllFeed')
        self.actSelectAllNoFeed = QtGui.QAction(u'Выделить всех без питания', self)
        self.actSelectAllNoFeed.setObjectName('actSelectAllNoFeed')
        self.actSelectionAllRow = QtGui.QAction(u'Выделить всех', self)
        self.actSelectionAllRow.setObjectName('actSelectionAllRow')
        self.actClearSelectionRow = QtGui.QAction(u'Снять выделение', self)
        self.actClearSelectionRow.setObjectName('actClearSelectionRow')
        self.actProlongationFeed = QtGui.QAction(u'Пролонгация питания', self)
        self.actProlongationFeed.setObjectName('actProlongationFeed')
        self.actGetFeedFromMenuAll = QtGui.QAction(u'Назначить питание по шаблону', self)
        self.actGetFeedFromMenuAll.setObjectName('actGetFeedFromMenuAll')
        self.mnuBtnFeed.addAction(self.actSelectAllFeed)
        self.mnuBtnFeed.addAction(self.actSelectAllNoFeed)
        self.mnuBtnFeed.addAction(self.actSelectionAllRow)
        self.mnuBtnFeed.addAction(self.actClearSelectionRow)
        self.mnuBtnFeed.addAction(self.actProlongationFeed)
        self.mnuBtnFeed.addAction(self.actGetFeedFromMenuAll)


    def reasonRenunciation(self):
        domain = u'\'не определено\','
        recordReceived = self.reasonRenunciationDomain(u'received%')
        recordPlanning = self.reasonRenunciationDomain(u'planning%')
        if recordReceived:
            domainR = QtCore.QString(forceString(recordReceived))
            if u'*' in domainR:
                index = domainR.indexOf(u'*', 0, QtCore.Qt.CaseInsensitive)
                if domainR[index - 1] != u',':
                    domainR.replace(QtCore.QString('*'), QtCore.QString(','))
                else:
                    domainR.remove(QtCore.QChar('*'), QtCore.Qt.CaseInsensitive)
            domain += domainR
        if recordPlanning:
            domain += forceString(recordPlanning)
        if domain != u'':
            self.cmbRenunciation.setDomain(domain)


    def reasonRenunciationDomain(self, flatCode = u'received%'):
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        cond =[tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(flatCode)),
               tableAPT['name'].like(u'Причина отказа%'),
               tableAPT['typeName'].like(u'String')
        ]
        queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableAPT, tableActionType['id'].eq(tableAPT['actionType_id']))
        record = db.getRecordEx(queryTable, [tableAPT['valueDomain']], cond)
        if record:
            return record.value(0)
        return None


    def reasonRenunciateDeath(self, death = False):
        domain = u'\'не определено\''
        recordReceived = self.reasonRenunciateDeathDomain()
        if recordReceived:
            domainR = QtCore.QString(forceString(recordReceived))
            if u'*' in domainR:
                index = domainR.indexOf(u'*', 0, QtCore.Qt.CaseInsensitive)
                if domainR[index - 1] != u',':
                    domainR.replace(QtCore.QString('*'), QtCore.QString(','))
                else:
                    domainR.remove(QtCore.QChar('*'), QtCore.Qt.CaseInsensitive)
            if death:
                domainS = u''
                domainList = domainR.split(",")
                for domainI in domainList:
                    if domainI.contains(u'умер', QtCore.Qt.CaseInsensitive) or domainI.contains(u'смерть', QtCore.Qt.CaseInsensitive):
                        domainS += ',' + domainI
                domain += domainS
            else:
                domain += u',' + domainR
        if domain != u'':
            self.cmbHospitalizingOutcome.setDomain(domain)
        self.lblHospitalizingOutcome.setText(u'Смерть' if death else u'Исход госпитализации')


    def reasonRenunciateDeathDomain(self):
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        cond =[ tableAction['deleted'].eq(0),
                tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('leaved%')),
                tableAPT['name'].like(u'Исход госпитализации'),
                tableAPT['typeName'].like(u'String')
        ]
        #        cond.append(db.joinOr([tableAPT['valueDomain'].like(u'%умер%'), tableAPT['valueDomain'].like(u'%смерть%')]))
        queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableAPT, tableActionType['id'].eq(tableAPT['actionType_id']))
        record = db.getRecordEx(queryTable, [tableAPT['valueDomain']], cond)
        if record:
            return record.value(0)
        return None


    def resetFilter(self):
        personId = QtGui.qApp.userId if QtGui.qApp.userSpecialityId else None
        isDefaultInHB = QtGui.qApp.db.translate('Person', 'id', personId, 'isDefaultInHB')
        isDefaultInHB = forceBool(isDefaultInHB)
        personId = personId if isDefaultInHB else None
        self.cmbPerson.setValue(personId)
        self.cmbFilterAccountingSystem.setValue(None)
        self.cmbStatusObservation.setValue(None)
        self.edtFilterClientId.setText('')
        self.edtFilterEventId.setText('')
        self.edtFilterCode.setText('')
        self.cmbSexBed.setCurrentIndex(0)
        self.cmbFilterIsPermanent.setCurrentIndex(0)
        self.cmbFilterType.setValue(None)
        self.chkAssistant.setChecked(False)
        self.cmbAssistant.setValue(None)
        self.cmbFilterProfile.setValue(None)
        self.cmbFinance.setValue(None)
        self.cmbQuotingType.setValue(None)
        self.cmbAttachType.setValue(None)
        self.spbBedAgeFrom.setValue(0)
        self.spbBedAgeTo.setValue(self.spbBedAgeTo.maximum())
        self.cmbFilterSchedule.setValue(None)
        self.edtFilterBegDate.setDate(QtCore.QDate.currentDate())
        self.edtFilterEndDate.setDate(QtCore.QDate())
        self.edtPresenceDayValue.setValue(0)
        self.cmbFilterBusy.setCurrentIndex(0)
        self.chkInvolution.setChecked(False)
        self.cmbInvolute.setCurrentIndex(0)
        self.cmbInvolute.setEnabled(False)
        self.chkAttachType.setChecked(False)
        self.cmbAttachType.setCurrentIndex(0)
        self.cmbAttachType.setEnabled(False)
        self.cmbLocationClient.setCurrentIndex(0)
        self.cmbFeed.setCurrentIndex(0)
        self.edtDateFeed.setDate(QtCore.QDate.currentDate())
        self.cmbReceived.setCurrentIndex(0)
        self.cmbTransfer.setCurrentIndex(0)
        self.chkStayOrgStructure.setChecked(True)
        self.cmbLeaved.setCurrentIndex(0)
        self.cmbRenunciation.setCurrentIndex(0)
        self.cmbRenunciationAction.setCurrentIndex(0)
        self.cmbHospitalizingOutcome.setCurrentIndex(0)
        self.cmbSex.setCurrentIndex(0)
        self.spbAgeFrom.setValue(0)
        self.spbAgeTo.setValue(self.spbAgeTo.maximum())
        self.cmbFilterActionType.setValue(0)
        self.cmbFilterActionStatus.setCurrentIndex(1)
        self.chkFilterIsUrgent.setChecked(False)
        self.edtFilterBegDatePlan.setDate(QtCore.QDate())
        self.edtFilterEndDatePlan.setDate(QtCore.QDate())
        if self.filterByExactTime:
            self.edtFilterBegTime.setTime(QtCore.QTime(0, 0))
            self.edtFilterEndTime.setTime(QtCore.QTime(0, 0))
        else:
            self.edtFilterEndTime.setTime(QtGui.qApp.changingDayTime())
        self.cmbLocationCard.setValue(None)


    #TODO: atronah: вписать все гуи фильтры и использовать во всех загрузчиках контента вместо тонны аргументов у функции loadData()
    def getFilter(self, directives=None):
        params = {'orgStructureIndex': self.treeOrgStructure.currentIndex()}
        if self.spbAgeFrom.isEnabled():
            params['ageFrom'] = self.spbAgeFrom.value()
        if self.spbAgeTo.isEnabled():
            params['ageTo'] = self.spbAgeTo.value()
        # Если стоит глобальная настройка filterByExactTime, то используется точное время начала и конца (отдельно), оно
        # берется из edtFilterBegTime и edtFilterEndTime, иначе используется время смены суток (одно и то же для начала
        # и конца), берется из edtFilterEndTime. Какой кошмар.
        if not self.filterByExactTime:
            params['changingDayTime'] = self.edtFilterEndTime.time()
        if self.edtFilterBegDate.isEnabled():
            params['begDate'] = self.edtFilterBegDate.date()
            addTime = self.edtFilterBegTime.time() if self.filterByExactTime else params['changingDayTime']
            params['begDateTime'] = QtCore.QDateTime(params['begDate'], addTime) if params['begDate'] else QtCore.QDateTime()
        if self.edtFilterEndDate.isEnabled():
            params['endDate'] = self.edtFilterEndDate.date()
            addTime = self.edtFilterEndTime.time() if self.filterByExactTime else params['changingDayTime']
            params['endDateTime'] = QtCore.QDateTime(params['endDate'], addTime) if params['endDate'] else QtCore.QDateTime()
        if self.edtFilterEventId.isEnabled():
            params['eventId'] = forceStringEx(self.edtFilterEventId.text())
        if self.edtFilterCode.isEnabled():
            params['codeBeds'] = self.edtFilterCode.text()
        if self.cmbAttachType.isVisible():
            params['clientAttachTypeCode'] = self.cmbAttachType.code() if (self.chkAttachType.isChecked() and self.cmbAttachType.isEnabled()) else 0
        if self.edtFilterClientId.isEnabled():
            params['clientId'] = forceStringEx(self.edtFilterClientId.text())
        if self.cmbLocationClient.isEnabled():
            params['clientLocation'] = self.cmbLocationClient.currentIndex()
        if self.cmbFinance.isEnabled():
            params['financeId'] = self.cmbFinance.value()
        if self.cmbFilterIsPermanent.isEnabled():
            params['permanent'] = self.cmbFilterIsPermanent.currentIndex()
        if self.cmbPerson.isEnabled():
            params['personId'] = self.cmbPerson.value()
        if self.cmbFilterProfile.isEnabled():
            params['profileId'] = self.cmbFilterProfile.value()
        if self.cmbQuotingType.isEnabled():
            params['quotingType'] = (self.cmbQuotingType.currentClass(), self.cmbQuotingType.value())
        if self.cmbStatusObservation.isEnabled():
            params['statusObservation'] = self.cmbStatusObservation.value()
        if self.cmbSex.isEnabled():
            params['sex'] = self.cmbSex.currentIndex()
        if self.cmbFilterType.isEnabled():
            params['typeId'] = self.cmbFilterType.value()
        if self.cmbFeed.isEnabled():
            params['feed'] = self.cmbFeed.currentIndex()
        if self.edtDateFeed.isEnabled():
            params['dateFeed'] = self.edtDateFeed.date() if self.cmbFeed.currentIndex() > 0 else None
        if self.cmbFilterAccountingSystem.isEnabled():
            params['accountingSystemId'] = self.cmbFilterAccountingSystem.value()
        if self.chkStayOrgStructure.isEnabled():
            params['stayOrgStructureId'] = self.chkStayOrgStructure.isChecked()
        if self.edtPresenceDayValue.isEnabled():
            params['presenceDay'] = self.edtPresenceDayValue.value()
        if self.cmbReceived.isEnabled():
            params['received'] = self.cmbReceived.currentIndex()
        if self.cmbTransfer.isEnabled():
            params['transfer'] = self.cmbTransfer.currentIndex()
        if self.chkStayOrgStructure.isEnabled():
            params['stayOrgStructure'] = self.chkStayOrgStructure.isChecked()
        if self.cmbLeaved.isEnabled():
            params['leaved'] = self.cmbLeaved.currentIndex()
        if self.cmbHospitalizingOutcome.isEnabled():
            params['death'] = self.cmbHospitalizingOutcome.currentText()
        if self.cmbRenunciationAction.isEnabled():
            params['renunciation'] = self.cmbRenunciationAction.currentIndex()
        if self.cmbRenunciation.isEnabled():
            params['renunciationReason'] = self.cmbRenunciation.text()
        if self.cmbAssistant.isEnabled():
            params['assistant'] = self.cmbAssistant.value()
        if self.chkAssistant.isEnabled():
            params['chkAssistant'] = self.chkAssistant.isChecked()
        if self.chkShowFinished.isEnabled():
            params['showFinished'] = self.chkShowFinished.isChecked()
        if self.cmbLobbyAction.isEnabled():
            params['lobbyAction'] = self.cmbLobbyAction.currentIndex()
        if self.cmbLobbyResult.isEnabled():
            params['lobbyResult'] = self.cmbLobbyResult.currentIndex()
        if self.cmbLocationCard.isEnabled():
            params['locationCard'] = self.cmbLocationCard.code()

        if directives is not None:
            for param in directives:
                params[param] = directives[param]

        return params



    def updateHospitalBeds(self):
        code = forceStringEx(self.edtFilterCode.text())
        sexIndexBed = self.cmbSexBed.currentIndex()
        ageForBed = self.spbBedAgeFrom.value()
        ageToBed = self.spbBedAgeTo.value()
        permanent = self.cmbFilterIsPermanent.currentIndex()
        typeId = self.cmbFilterType.value()
        profile = self.cmbFilterProfile.value()
        schedule = self.cmbFilterSchedule.value()
        begDate = self.edtFilterBegDate.date()
        endDate = self.edtFilterEndDate.date()
        begTime = self.edtFilterBegTime.time()
        endTime = self.edtFilterBegTime.time()
        busy = self.cmbFilterBusy.currentIndex()
        now = QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)
        involution = self.cmbInvolute.currentIndex()
        changingDayTime = self.edtFilterEndTime.time()

        db = QtGui.qApp.db
        table = db.table('OrgStructure_HospitalBed')
        tableOrgStructure = db.table('OrgStructure')
        tableEx = table.join(tableOrgStructure, tableOrgStructure['id'].eq(table['master_id']))
        orgStructureIdList = getOrgStructureIdList(self.treeOrgStructure.currentIndex())
        cond = [ table['master_id'].inlist(orgStructureIdList) ]
        addCondLike(cond, table['code'], code)
        if sexIndexBed:
            cond.append(table['sex'].eq(sexIndexBed))
        if ageForBed <= ageToBed:
            ageForBedCount = ageForBed
            if ageForBed == 0:
                ageList = [u'']
            else:
                ageList = []
            while ageForBedCount <= ageToBed:
                ageList.append(str(ageForBedCount))
                ageForBedCount += 1
            cond.append(table['age'].inlist(ageList))
        if permanent != 0:
            cond.append(table['isPermanent'].eq(permanent-1))
        if typeId:
            cond.append(table['type_id'].eq(typeId))
        if profile:
            cond.append(table['profile_id'].eq(profile))
        if schedule:
            cond.append(table['schedule_id'].eq(schedule))

        if not begDate.isNull():
            begDateTime = QtCore.QDateTime(begDate, begTime if self.filterByExactTime else changingDayTime)
            cond.append(db.joinOr([table['begDate'].datetimeLe(begDateTime),
                                   table['begDate'].isNull()]))
        if not endDate.isNull():
            endDateTime = QtCore.QDateTime(endDate, endTime if self.filterByExactTime else changingDayTime)
            cond.append(db.joinOr([table['endDate'].datetimeGe(endDateTime),
                                   table['endDate'].isNull()]))
        if busy == 1:
            cond.append('NOT isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\')' % now)
        elif busy == 2:
            cond.append('isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\')' % now)
        if self.chkInvolution.isChecked():
            cond.append(table['involution'].eq(involution + 1))
            if not begDate.isNull():
                cond.append(db.joinOr([table['begDateInvolute'].le(begDate), table['begDateInvolute'].isNull()]))
                cond.append(db.joinOr([table['endDateInvolute'].le(begDate), table['endDateInvolute'].isNull()]))

        idList = db.getIdList(tableEx, idCol=table['id'].name(),  where=cond, order='OrgStructure.name, OrgStructure_HospitalBed.idx')
        self.tblHospitalBeds.setIdList(idList)

        cnt = len(idList)
        if busy == 1:
            cntBusy = 0
        elif busy == 2:
            cntBusy = cnt
        else:
            cond = [ table['id'].inlist(idList),
                     table['involution'].eq(0),
                     'isHospitalBedBusy(OrgStructure_HospitalBed.id, \'%s\')' % now
            ]
            cntBusy = db.getCount(table, countCol='id', where=cond)

        cond = [table['id'].inlist(idList)
        ]
        if self.chkInvolution.isChecked():
            cond.append(table['involution'].eq(involution + 1))
        else:
            cond.append(table['involution'].gt(0))
        if not begDate.isNull():
            cond.append(db.joinOr([table['begDateInvolute'].le(begDate), table['begDateInvolute'].isNull()]))
            cond.append(db.joinOr([table['endDateInvolute'].le(begDate), table['endDateInvolute'].isNull()]))
        cntInvolute = db.getCount(table, countCol='id', where=cond)

        self.lblInvoluteValue.setText(str(cntInvolute))
        self.lblTotalValue.setText(str(cnt))
        self.lblFreeValue.setText(str(cnt - cntBusy - cntInvolute))
        self.lblBusyValue.setText(str(cntBusy))

        filterAsText = []
        if code: filterAsText.append(u'код : '+code)
        if permanent: filterAsText.append(u'штат : ' + unicode(self.cmbFilterIsPermanent.currentText()))
        if typeId:      filterAsText.append(u'тип : ' + unicode(self.cmbFilterType.currentText()))
        if profile:   filterAsText.append(u'профиль : ' + unicode(self.cmbFilterProfile.currentText()))
        if schedule:  filterAsText.append(u'график : ' + unicode(self.cmbFilterSchedule.currentText()))
        if sexIndexBed: filterAsText.append(u'пол койки : '+unicode(['', u'М', u'Ж'][sexIndexBed]))
        if ageForBed: filterAsText.append(u'возраст койки от : '+unicode(ageForBed))
        if ageToBed: filterAsText.append(u'возраст койки до : '+unicode(ageToBed))
        if begDate.isValid(): filterAsText.append(u'начало : ' + forceString(begDate))
        if endDate.isValid(): filterAsText.append(u'окончание : ' + forceString(endDate))
        if busy:      filterAsText.append(unicode(self.cmbFilterBusy.currentText()))
        filterAsText.append(u'отчёт составлен : ' + forceString(QtCore.QDateTime.currentDateTime()))
        self.filterAsText = '\n'.join(filterAsText)


    def getCurrentEventId(self, indexWidget = 0):
        hospitalBedId = None
        if indexWidget == self.tabWidget.indexOf(self.tabFund):
            hospitalBedId = self.tblHospitalBeds.currentItemId()
        elif indexWidget == self.tabWidget.indexOf(self.tabPresence):
            index = self.tblPresence.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelPresence.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabReceived):
            index = self.tblReceived.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelReceived.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabTransfer):
            index = self.tblTransfer.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelTransfer.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabLeaved):
            index = self.tblLeaved.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelLeaved.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabReabyToLeave):
            index = self.tblReabyToLeave.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelReabyToLeave.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabQueue):
            index = self.tblQueue.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelQueue.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabRenunciation):
            index = self.tblRenunciation.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelRenunciation.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabDeath):
            index = self.tblDeath.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelDeath.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabReanimation):
            index = self.tblReanimation.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelReanimation.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabLobby):
            index = self.tblLobby.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelLobby.items[row].get('eventId', 0)
        elif indexWidget == self.tabWidget.indexOf(self.tabMaternityward):
            index = self.tblMaternityward.currentIndex()
            row = index.row()
            if row >= 0:
                return self.modelMaternityward.items[row].get('eventId', 0)

        if hospitalBedId:
            CHospitalBedsEventDialog(self, hospitalBedId).exec_()
            self.on_selectionModelOrgStructure_currentChanged(None, None)
        return None


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelOrgStructure_currentChanged(self, current, previous):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == self.tabWidget.indexOf(self.tabFund):
            self.updateHospitalBeds()
        elif widgetIndex == self.tabWidget.indexOf(self.tabPresence):
            orgStructureIndex = self.treeOrgStructure.currentIndex()
            if orgStructureIndex:
                treeItem = orgStructureIndex.internalPointer() if orgStructureIndex.isValid() else None
                orgStructureIdList = getOrgStructureIdList(orgStructureIndex) if treeItem and treeItem._id else []
                self.cmbFilterActionList.setCurrentIndex(1)
                self.chkListStatus.setChecked(False)
                self.chkListDiagnostic.setChecked(True)
                self.chkListCure.setChecked(True)
                self.chkListMisc.setChecked(False)
                if orgStructureIdList:
                    db = QtGui.qApp.db
                    tableOS = db.table('OrgStructure')
                    movingOSIdList = db.getIdList(tableOS, tableOS['id'], [tableOS['id'].inlist(orgStructureIdList), tableOS['type'].ne(4), tableOS['deleted'].eq(0)])
                    receivedOSIdList = db.getIdList(tableOS, tableOS['id'], [tableOS['id'].inlist(orgStructureIdList), tableOS['type'].eq(4), tableOS['deleted'].eq(0)])
                    if receivedOSIdList and not movingOSIdList:
                        self.chkListStatus.setChecked(True)
                        self.chkListMisc.setChecked(True)
            self.loadDataPresence()
            self.tblPresence.setFocus(QtCore.Qt.TabFocusReason)
            rowCount = self.modelPresence.rowCount()
            if rowCount > 0:
                self.tblPresence.setCurrentRow(0)
            self.updateActionsList({}, [self.getCurrentEventId(1)])
        elif widgetIndex == self.tabWidget.indexOf(self.tabReceived):
            self.loadDataReceived()
        elif widgetIndex == self.tabWidget.indexOf(self.tabTransfer):
            self.loadDataTransfer()
        elif widgetIndex == self.tabWidget.indexOf(self.tabLeaved):
            self.loadDataLeaved()
        elif widgetIndex == self.tabWidget.indexOf(self.tabReabyToLeave):
            self.loadDataReadyToLeave()
        elif widgetIndex == self.tabWidget.indexOf(self.tabQueue):
            self.loadDataQueue()
        elif widgetIndex == self.tabWidget.indexOf(self.tabRenunciation):
            self.loadDataRenunciation()
        elif widgetIndex == self.tabWidget.indexOf(self.tabDeath):
            self.loadDataDeath()
        elif widgetIndex == self.tabWidget.indexOf(self.tabReanimation):
            self.loadDataReanimation()
        elif widgetIndex == self.tabWidget.indexOf(self.tabLobby):
            self.loadDataLobby()
        elif widgetIndex == self.tabWidget.indexOf(self.tabMaternityward):
            self.loadDataMaternityward()
        self.lblCountRecordList.setText(formatRecordsCount(self.getCurrentWidgetRowCount(self.tabWidget.currentIndex())))


    def loadDataLeaved(self, directives=None):
        self.modelLeaved.loadData(self.getFilter(directives=directives))

    def loadDataQueue(self, directives=None):
        self.modelQueue.loadData(self.getFilter(directives=directives))

    def loadDataRenunciation(self, directives=None):
        self.modelRenunciation.loadData(self.getFilter(directives=directives))

    def loadDataDeath(self, directives=None):
        self.modelDeath.loadData(self.getFilter(directives=directives))

    def loadDataPresence(self, directives=None):
        self.modelPresence.loadData(self.getFilter(directives=directives))

    def loadDataReceived(self, directives=None):
        self.modelReceived.loadData(self.getFilter(directives=directives))

    def loadDataTransfer(self, directives=None):
        self.modelTransfer.loadData(self.getFilter(directives=directives))

    def loadDataReadyToLeave(self, directives=None):
        self.modelReabyToLeave.loadData(params=self.getFilter(directives=directives))

    def loadDataReanimation(self, directives=None):
        self.modelReanimation.loadData(params=self.getFilter(directives=directives))

    def loadDataLobby(self, directives=None):
        self.modelLobby.loadData(params=self.getFilter())

    def loadDataMaternityward(self, directives=None):
        self.modelMaternityward.loadData(params=self.getFilter())

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxFilter_clicked(self, button):
        buttonCode = self.buttonBoxFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_selectionModelOrgStructure_currentChanged(None, None)
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilter()
            self.on_selectionModelOrgStructure_currentChanged(None, None)


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Close:
            self.reject()


    @QtCore.pyqtSlot()
    def on_actPrintFeedReport_triggered(self):
        widgetIndex = self.tabWidget.currentIndex()
        items = []
        if widgetIndex == self.tabWidget.indexOf(self.tabPresence):
            # self.loadDataLeaved()
            # self.loadDataReanimation(directives={'orgStructureIndex': self.treeOrgStructure.rootIndex()})
            CFeedReport(self, self.modelPresence, [self.modelReanimation, self.modelMaternityward], self.modelLeaved).exec_()
        elif widgetIndex == self.tabWidget.indexOf(self.tabReanimation):
            CFeedReport(self, self.modelReanimation, forReanimation=True).exec_()
        elif widgetIndex == self.tabWidget.indexOf(self.tabMaternityward):
            CFeedReport(self, self.modelMaternityward, forReanimation=True).exec_()

    @QtCore.pyqtSlot(bool)
    def on_chkAssistant_toggled(self, checked):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == self.tabWidget.indexOf(self.tabLeaved):
            self.cmbAssistant.setEnabled(self.chkAssistant.isChecked())


    @QtCore.pyqtSlot()
    def on_btnFindClientInfo_clicked(self):
        self.cmbFilterAccountingSystem.setValue(None)
        self.edtFilterClientId.setText('')
        HospitalizationEvent = CFindClientInfoDialog(self)
        if HospitalizationEvent:
            HospitalizationEvent.setWindowTitle(u'''Поиск пациента''')
            HospitalizationEvent.exec_()
            self.edtFilterClientId.setText(forceString(HospitalizationEvent.filterClientId))


    def getConditionFilter(self):
        sexList = [u'не определено', u'мужской', u'женский']
        rows = []
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result

        titleDescription = u''
        begDate = self.edtFilterBegDate.date()
        endDate = self.edtFilterEndDate.date()
        if self.filterByExactTime:
            begDate = QtCore.QDateTime(begDate, self.edtFilterBegTime.time())
            endDate = QtCore.QDateTime(endDate, self.edtFilterEndTime.time())
        sexIndex = self.cmbSex.currentIndex()
        ageFor = self.spbAgeFrom.value()
        ageTo = self.spbAgeTo.value()
        sexIndexBed = self.cmbSexBed.currentIndex()
        ageForBed = self.spbBedAgeFrom.value()
        ageToBed = self.spbBedAgeTo.value()

        if begDate or endDate:
            titleDescription = u'за период' + dateRangeAsStr(begDate, endDate)
        currentIndexOS = self.treeOrgStructure.currentIndex()
        if currentIndexOS:
            orgStructureId = self.getOrgStructureId(currentIndexOS)
            if orgStructureId:
                titleDescription += u'\n' + u'подразделение ' + forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
            else:
                titleDescription += u'\n' + u'ЛПУ'
        accountingSystemId = self.cmbFilterAccountingSystem.value()
        if accountingSystemId:
            accountingSystemName = forceString(QtGui.qApp.db.translate('rbAccountingSystem', 'id', accountingSystemId, 'name'))
            titleDescription += u'\n' + u'внешняя учётная система ' + accountingSystemName
            rows.append(u'Внешняя учётная система ' + accountingSystemName)
        filterClientId = forceStringEx(self.edtFilterClientId.text())
        if filterClientId:
            titleDescription += u'\n' + u'идентификатор пациента %s'%(str(filterClientId))
            rows.append(u'идентификатор пациента %s'%(str(filterClientId)))
        edtFilterEventId = forceStringEx(self.edtFilterEventId.text())
        if edtFilterEventId:
            titleDescription += u'\n' + u'внешний идентификатор События (Карта) %s'%(str(edtFilterEventId))
            rows.append(u'Внешний идентификатор События (Карта) %s'%(str(edtFilterEventId)))
        statusObservationId = self.cmbStatusObservation.value()
        if statusObservationId:
            statusObservationName = forceString(QtGui.qApp.db.translate('rbStatusObservationClientType', 'id', statusObservationId, 'name'))
            titleDescription += u'\n' + u'статус наблюдения пациента: ' + statusObservationName
            rows.append(u'Статус наблюдения пациента: ' + statusObservationName)
        personId = self.cmbPerson.value()
        if personId:
            personName = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            titleDescription += u'\n' + u'врач ' + personName
            rows.append(u'Врач ' + personName)
        if self.cmbAssistant.isEnabled() and self.chkAssistant.isChecked():
            assistantId = self.cmbAssistant.value()
            if assistantId:
                assistantName = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', assistantId, 'name'))
                titleDescription += u'\n' + u'ассистент ' + assistantName
                rows.append(u'Ассистент ' + assistantName)
            else:
                rows.append(u'Ассистент ' + u'не указан')
        if sexIndex:
            titleDescription += u'\n' + u'пол ' + sexList[sexIndex]
            rows.append(u'Пол ' + sexList[sexIndex])
        if ageFor or ageTo:
            titleDescription += u'\n' + u'возраст' + u' с '+forceString(ageFor) + u' по '+forceString(ageTo)
            rows.append(u'Возраст' + u' с '+forceString(ageFor) + u' по '+forceString(ageTo))
        if self.chkInvolution.isChecked():
            titleDescription += u'\n' + u'сворачивание койки ' + forceString(self.cmbInvolute.currentText())
        if self.cmbFilterIsPermanent.currentIndex():
            permanent = self.cmbFilterIsPermanent.currentText()
            titleDescription += u'\n' + u'штат ' + forceString(permanent)
            rows.append(u'Штат койки ' + forceString(permanent))
        typeId = self.cmbFilterType.value()
        if typeId:
            typeId = self.cmbFilterType.currentText()
            titleDescription += u'\n' + u'тип ' + forceString(typeId)
            rows.append(u'Тип койки ' + forceString(typeId))
        profile = self.cmbFilterProfile.value()
        if profile:
            profile = self.cmbFilterProfile.currentText()
            titleDescription += u'\n' + u'профиль ' + forceString(profile)
            rows.append(u'Профиль койки ' + forceString(profile))
        if sexIndexBed:
            titleDescription += u'\n' + u'пол койки ' + sexList[sexIndexBed]
            rows.append(u'Пол койки ' + sexList[sexIndexBed])
        if ageForBed or ageToBed:
            rows.append(u'Возраст койки' + u' с '+forceString(ageForBed) + u' по '+forceString(ageToBed))
        codeFinance = self.cmbFinance.value()
        if codeFinance:
            codeFinance = self.cmbFinance.currentText()
            titleDescription += u'\n' + u'источник финансирования ' + forceString(codeFinance)
            rows.append(u'Источник финансирования ' + forceString(codeFinance))
        currentClass = self.cmbQuotingType.currentClass()
        quotingTypeId = self.cmbQuotingType.value()
        if quotingTypeId or currentClass != None:
            if not quotingTypeId:
                titleDescription += u'\n' + u'квотирование: класс ' + [u'ВТМП', u'СМП'][currentClass]
                rows.append(u'Квотирование: класс - ' + [u'ВТМП', u'СМП'][currentClass])
            else:
                nameQuotaType = forceString(QtGui.qApp.db.translate('QuotaType', 'id', quotingTypeId, 'name'))
                titleDescription += u'\n' + u'квотирование: ' + nameQuotaType
                rows.append(u'Квотирование: ' + nameQuotaType)
        if self.cmbFeed.isEnabled():
            titleDescription += u'\n' + u'питание: ' + forceString(self.cmbFeed.currentText())
            if self.edtDateFeed.isEnabled():
                titleDescription += u' на дату: ' + forceString(self.edtDateFeed.date())
        if self.edtPresenceDayValue.isEnabled():
            presenceDayValue = self.edtPresenceDayValue.value()
            if presenceDayValue:
                titleDescription += u'\n' + self.lblPresenceDay.text() + u': ' + forceString(presenceDayValue)
        if self.cmbReceived.isEnabled():
            received = self.cmbReceived.currentIndex()
            titleDescription += u'\n' + self.lblReceived.text() + u': ' + [u'в ЛПУ', u'в отделение', u'в приемное отделение'][received]
            rows.append(self.lblReceived.text() + u': ' + [u'в ЛПУ', u'в отделение', u'в приемное отделение'][received])
        if self.cmbTransfer.isEnabled():
            transfer = self.cmbTransfer.currentIndex()
            titleDescription += u'\n' + self.lblTransfer.text() + u': ' + [u'из отделения', u'в отделение'][transfer]
            rows.append(self.lblTransfer.text() + u': ' + [u'из отделения', u'в отделение'][transfer])
        if self.chkStayOrgStructure.isEnabled():
            titleDescription += u'\n' + u'с учетом "Отделения пребывания"'
            rows.append(u'с учетом "Отделения пребывания"')
        if self.cmbLeaved.isEnabled():
            leaved = self.cmbLeaved.currentIndex()
            titleDescription += u'\n' + self.lblLeaved.text() + u': ' + [u'из ЛПУ', u'без выписки', u'из отделений'][leaved]
            rows.append(self.lblLeaved.text() + u': ' + [u'из ЛПУ', u'без выписки', u'из отделений'][leaved])
        if self.cmbRenunciation.isEnabled():
            titleDescription += u'\n' + self.lblRenunciation.text() + u': ' + self.cmbRenunciation.text()
            rows.append(self.lblRenunciation.text() + u': ' + self.cmbRenunciation.text())
        if self.cmbHospitalizingOutcome.isEnabled():
            titleDescription += u'\n' + self.lblHospitalizingOutcome.text() + u': ' + self.cmbHospitalizingOutcome.text()
            rows.append(self.lblHospitalizingOutcome.text() + u': ' + self.cmbHospitalizingOutcome.text())
        if self.cmbRenunciationAction.isEnabled():
            renunciationAction = self.cmbRenunciationAction.currentIndex()
            titleDescription += u'\n' + self.lblRenunciationAction.text() + u': ' + [u'Госпитализации', u'Планировании'][renunciationAction]
            rows.append(self.lblRenunciationAction.text() + u': ' + [u'Госпитализации', u'Планировании'][renunciationAction])
        titleBed = u''
        scheduleBed = self.cmbFilterSchedule.currentText()
        if scheduleBed:
            titleBed += u'\n' + u'режим ' + forceString(scheduleBed)
        busyBed = self.cmbFilterBusy.currentText()
        if busyBed:
            titleBed += u'\n' + u'занятость ' + forceString(busyBed)
        codeBed = self.edtFilterCode.text()
        if codeBed:
            titleBed += u'\n' + u'код койки ' + forceString(codeBed)
        if self.chkAttachType.isChecked() and self.cmbAttachType.isEnabled():
            titleDescription += u'\n' + u'прикрепление пациента: ' + forceString(self.cmbAttachType.currentText())
            rows.append(u'Прикрепление пациента: ' + forceString(self.cmbAttachType.currentText()))
        if self.cmbLocationClient.isEnabled():
            titleDescription += u'\n' + u'размещение пациента: ' + forceString(self.cmbLocationClient.currentText())
            rows.append(u'Размещение пациента: ' + forceString(self.cmbLocationClient.currentText()))
        if self.cmbLocationCard.isEnabled():
            locationCard = self.cmbLocationCard.currentText()
            titleDescription += u'\n' + u'архив истории болезни ' + forceString(locationCard)
            rows.append(u'Архив истории болезни ' + forceString(locationCard))
        titlePresenceDay = titleDescription
        titleDescription += u'\n' + u'отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime())

        return titleDescription, titlePresenceDay, rows


    def addReportColumn(self, items, roleList):
        db = QtGui.qApp.db

        additionalCol = {}
        tempAdditionalColList = []
        for role in roleList:
            tempAdditionalColList.append({})
        if not tempAdditionalColList:
            return {}

        if not items or not items[0].get('eventId'):
            return {}

        eventIdList = '('
        for item in items:
            eventIdList += forceString(item.get('eventId')) + ', '
        eventIdList = eventIdList[:len(eventIdList) - 2] + ')'

        select = ['Event.id']
        join = u' LEFT JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0'

        if roleList[0] or roleList[1]:
            if roleList[0]:
                select.append(u'CONCAT_WS(\' \', rbDocumentType.name, ClientDocument.serial, ClientDocument.number, ClientDocument.origin) AS clientPassport')
                join += u'''
                    LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND ClientDocument.deleted = 0
                    LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
                '''
            if roleList[1]:
                select.append(u'CONCAT_WS(\' \', InsurerOrg.shortName, rbPolicyType.name, rbPolicyKind.name, ClientPolicy.serial, ClientPolicy.number, ClientPolicy.name) AS clientPolicy')
                join += u'''
                    LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.deleted = 0
                    LEFT JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
                    LEFT JOIN rbPolicyKind ON rbPolicyKind.id = ClientPolicy.policyKind_id
                    LEFT JOIN Organisation AS InsurerOrg ON InsurerOrg.id = ClientPolicy.insurer_id AND InsurerOrg.deleted = 0 AND InsurerOrg.isInsurer = 1
                '''
        if roleList[2] or roleList[3]:
            join += u'''
                LEFT JOIN ActionType AS ActType ON ActType.flatCode LIKE 'received%%'
                    AND ActType.deleted = 0
            '''
        if roleList[2]:
            select.append(u'ReferralOrg.shortName AS referralOrg')
            join += u'''
                LEFT JOIN Action AS ActOrg ON ActOrg.event_id = Event.id
                    AND ActOrg.deleted = 0
                LEFT JOIN ActionPropertyType AS ActPropTypeOrg ON ActPropTypeOrg.actionType_id = ActType.id
                    AND ActPropTypeOrg.typeName LIKE 'Organisation%%'
                    AND ActPropTypeOrg.descr LIKE 'направлен%%'
                    AND ActPropTypeOrg.deleted = 0
                LEFT JOIN ActionProperty AS ActPropOrg ON ActPropOrg.action_id = ActOrg.id
                    AND ActPropOrg.type_id = ActPropTypeOrg.id
                    AND ActPropOrg.deleted = 0
                LEFT JOIN ActionProperty_Organisation ON ActionProperty_Organisation.id = ActPropOrg.id
                LEFT JOIN Organisation AS ReferralOrg ON ReferralOrg.id = ActionProperty_Organisation.value
                    AND ReferralOrg.deleted = 0
            ''' % {'eventIdList' : eventIdList}
        if roleList[3]:
            select.append(u'ActionProperty_String.value AS diagReferralOrg')
            join += u'''
                LEFT JOIN Action AS ActDiag ON ActDiag.event_id = Event.id
                    AND ActDiag.deleted = 0
                LEFT JOIN ActionPropertyType AS ActPropTypeDiag ON ActPropTypeDiag.actionType_id = ActType.id
                    AND ActPropTypeDiag.typeName LIKE 'String%%'
                    AND ActPropTypeDiag.descr LIKE 'Диагноз направившего учреждения%%'
                    AND ActPropTypeDiag.deleted = 0
                LEFT JOIN ActionProperty AS ActPropDiag ON ActPropDiag.action_id = ActDiag.id
                    AND ActPropDiag.type_id = ActPropTypeDiag.id
                    AND ActPropDiag.deleted = 0
                LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActPropDiag.id
            ''' % {'eventIdList' : eventIdList}
        if roleList[4]:
            select.append(u'getClientLocAddress(Event.client_id) AS clientLocAddress')
        if roleList[5]:
            select.append(u'getClientRegAddress(Event.client_id) AS clientRegAddress')
        if roleList[6] or roleList[7]:
            join += ' LEFT JOIN ClientWork ON ClientWork.client_id = Client.id AND ClientWork.id = getClientWorkId(Client.id) AND ClientWork.deleted = 0'
        if roleList[6]:
            select.append('if(ClientWork.org_id IS NOT NULL, WorkOrg.shortName, ClientWork.freeInput) AS clientWork')
            join += ' LEFT JOIN Organisation WorkOrg ON WorkOrg.id = ClientWork.org_id'
        if roleList[7]:
            select.append('ClientWork.post')

        stmt = u'''
            SELECT %(select)s
            FROM Event
            %(join)s
            WHERE Event.deleted = 0
                AND Event.id IN %(eventIdList)s
        ''' % {'select' : ', '.join(select),
               'join' : join,
               'eventIdList' : eventIdList}
        query = db.query(stmt)
        while query.next():
            record = query.record()
            eventId = forceInt(record.value('id'))
            i = 0
            if roleList[0]\
                    and forceString(record.value('clientPassport'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId : forceString(record.value('clientPassport'))})
            if roleList[0]:
                i += 1
            if roleList[1]\
                    and forceString(record.value('clientPolicy'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId : forceString(record.value('clientPolicy'))})
            if roleList[1]:
                i += 1
            if roleList[2]\
                    and forceString(record.value('referralOrg'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId : forceString(record.value('referralOrg'))})
            if roleList[2]:
                i += 1
            if roleList[3]\
                    and forceString(record.value('diagReferralOrg'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId : forceString(record.value('diagReferralOrg'))})
            if roleList[3]:
                i += 1
            if roleList[4]\
                    and forceString(record.value('clientLocAddress'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId : forceString(record.value('clientLocAddress'))})
            if roleList[4]:
                i += 1
            if roleList[5]\
                    and forceString(record.value('clientRegAddress'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId : forceString(record.value('clientRegAddress'))})
            if roleList[5]:
                i += 1
            if roleList[6]\
                    and forceString(record.value('clientWork'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId: forceString(record.value('clientWork'))})
            if roleList[6]:
                i += 1
            if roleList[7]\
                    and forceString(record.value('post'))\
                    and not tempAdditionalColList[i].has_key(eventId):
                tempAdditionalColList[i].update({eventId: forceString(record.value('post'))})

        i = 0
        for role in roleList:
            if role:
                additionalCol.update({role : tempAdditionalColList[i]})
                i += 1

        return additionalCol

    def __getOrderStatistic(self, items):
        from collections import defaultdict
        # 1 — плановый
        # 2 — экстренный
        sum1 = 0
        sum2 = 0
        sums2 = defaultdict(int)
        for i in items:
            if i['ordType'] == 1:
                sum1 += 1
            elif i['ordType'] == 2:
                sum2 += 1
                sums2[i['ordChannel']] += 1

        str = u''
        str += u'Количество плановых: ' + unicode(sum1) + u'\n'
        str += u'Количество экстренных: ' + unicode(sum2) + u'\n'
        str += u'Из них:\n'
        for key, value in sums2.iteritems():
            str += unicode(key) + u': ' + unicode(value) + u'\n'

        return str

    #TODO: mdldml: вынести в HospitalBedsReport
    @QtCore.pyqtSlot()
    def on_actPrintReport_triggered(self):
        widgetIndex = self.tabWidget.currentIndex()
        titleDescription, titlePresenceDay = self.getConditionFilter()[:2]
        addColTitle = [
            u'Паспорт пациент',
            u'Полис пациента',
            u'Направившее учреждение',
            u'Диагноз направившего учреждения',
            u'Адрес прописки пациента',
            u'Адрес проживания пациента',
            u'Место работы',
            u'Должность',
            u'Ф-027',
            u'Стат. талон',
            u'Архив'
        ]
        if widgetIndex == self.tabWidget.indexOf(self.tabFund):
            report = CHospitalBedsReport(self)
            view = CReportViewDialog(self)
            view.setText(report.build(self.filterAsText, self.modelHospitalBeds.idList()))
            view.exec_()
        elif widgetIndex == self.tabWidget.indexOf(self.tabPresence):
            result = CSettingSetupDialog(None, self.tblPresence.model(), 'PrintTblPresence', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblPresence.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblPresence.setReportHeader(u'Присутствуют в стационаре')
                presenceDay = self.edtPresenceDayValue.value()
                if presenceDay:
                    titlePresenceDay += u'\n' + u'присутсвуют дней ' + forceString(presenceDay)
                titlePresenceDay += u'\n' + u'отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime())
                self.tblPresence.setReportDescription(titlePresenceDay)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = self.addReportColumn(self.tblPresence.model().items, roleList)
                self.tblPresence.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabReceived):
            result = CSettingSetupDialog(None, self.tblReceived.model(), 'PrintTblReceived', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()

                # roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                # i3290. Зачем эта строчка? Из-за нее не все столбцы были видны. Смотри задачу
                # itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblReceived.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblReceived.setReportHeader(u'Поступили %s' % (self.cmbReceived.currentText()))

                self.tblReceived.setReportDescription(titleDescription + '\n' + self.__getOrderStatistic(self.tblReceived.model().items))
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                #additionalCol = {}
                #if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                additionalCol = self.addReportColumn(self.tblReceived.model().items, roleList)
                self.tblReceived.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabTransfer):
            result = CSettingSetupDialog(None, self.tblTransfer.model(), 'PrintTblTransfer', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblTransfer.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblTransfer.setReportHeader(u'Переведены %s'%(self.cmbTransfer.currentText()))
                self.tblTransfer.setReportDescription(titleDescription)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = {}
                if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                    additionalCol = self.addReportColumn(self.tblTransfer.model().items, roleList)
                self.tblTransfer.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabLeaved):
            result = CSettingSetupDialog(None, self.tblLeaved.model(), 'PrintTblLeaved', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds#[len(itemsCheckeds) - len(addColTitle):]
                # i3290. Зачем эта строчка? Из-за нее не все столбцы были видны. Смотри задачу
                # itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblLeaved.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblLeaved.setReportHeader(u'Выбыло %s' % (self.cmbLeaved.currentText()))
                self.tblLeaved.setReportDescription(titleDescription)
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                #additionalCol = {}
                #if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                additionalCol = self.addReportColumn(self.tblLeaved.model().items, roleList)
                self.tblLeaved.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabReabyToLeave):
            result = CSettingSetupDialog(None, self.tblReabyToLeave.model(), 'PrintTblReabyToLeave', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblReabyToLeave.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblReabyToLeave.setReportHeader(u'Готовятся к выбытию %s' % (self.cmbLeaved.currentText()))
                self.tblReabyToLeave.setReportDescription(titleDescription)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = {}
                if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                    additionalCol = self.addReportColumn(self.tblReabyToLeave.model().items, roleList)
                self.tblReabyToLeave.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabQueue):
            result = CSettingSetupDialog(None, self.tblQueue.model(), 'PrintTblQueue', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblQueue.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblQueue.setReportHeader(u'Планирование')
                self.tblQueue.setReportDescription(titleDescription)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = {}
                if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                    additionalCol = self.addReportColumn(self.tblQueue.model().items, roleList)
                self.tblQueue.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabRenunciation):
            result = CSettingSetupDialog(None, self.tblRenunciation.model(), 'PrintTblRenunciation', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblRenunciation.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                if self.cmbRenunciation.text()!= u'не определено':
                    reason = u'. Причина: %s' % (self.cmbRenunciation.text())
                else:
                    reason = u''
                reason += u' Отказ при %s' % (self.cmbRenunciationAction.currentText())
                self.tblRenunciation.setReportHeader(u'Отказы от госпитализации%s' % (reason))
                self.tblRenunciation.setReportDescription(titleDescription)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = {}
                if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                    additionalCol = self.addReportColumn(self.tblRenunciation.model().items, roleList)
                self.tblRenunciation.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabDeath):
            result = CSettingSetupDialog(None, self.tblDeath.model(), 'PrintTblDeath', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblDeath.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblDeath.setReportHeader(u'Умерло %s' % (self.cmbHospitalizingOutcome.currentText()))
                self.tblDeath.setReportDescription(titleDescription)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = {}
                if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                    additionalCol = self.addReportColumn(self.tblDeath.model().items, roleList)
                self.tblDeath.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabReanimation):
            result = CSettingSetupDialog(None, self.tblReanimation.model(), 'PrintTblReanimation', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblReanimation.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblReanimation.setReportHeader(u'Реанимированы')
                self.tblReanimation.setReportDescription(titleDescription)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = {}
                if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                    additionalCol = self.addReportColumn(self.tblReanimation.model().items, roleList)
                self.tblReanimation.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)
        elif widgetIndex == self.tabWidget.indexOf(self.tabLobby):
            result = CSettingSetupDialog(None, self.tblLobby.model(), 'PrintTblLobby', addColTitle)
            if result.exec_():
                i = 0
                itemsDisplay = []
                itemsCheckeds = result.lstColumn.model().getModelData()
                roleList = itemsCheckeds[len(itemsCheckeds) - len(addColTitle):]
                itemsCheckeds = itemsCheckeds[:len(itemsCheckeds) - len(addColTitle)]
                fontSize = forceInt(result.edtFontSize.text()) if result.edtFontSize.text() else 8
                while i < self.tblLobby.model().columnCount():
                    if itemsCheckeds[i]:
                        itemsDisplay.append(QtCore.Qt.DisplayRole)
                    else:
                        itemsDisplay.append(None)
                    i += 1
                self.tblLobby.setReportHeader(u'Приёмное отделение')
                self.tblLobby.setReportDescription(titleDescription)
                roleList = [addColTitle[i] if roleList[i] else '' for i in xrange(len(roleList))]
                additionalCol = {}
                if roleList[0] or roleList[1] or roleList[2] or roleList[3]:
                    additionalCol = self.addReportColumn(self.tblLobby.model().items, roleList)
                self.tblLobby.printContent(itemsDisplay, None, fontSize, additionalCol, addColTitle)

    #TODO: mdldml: вынести в HospitalBedsReport
    @QtCore.pyqtSlot()
    def printRenunciationsReport(self):
        columnRoleList = [None] * self.tblRenunciation.model().columnCount()

        titles = [None] * self.tblRenunciation.model().columnCount()

        showedColumnFieldNames = [u'externalId',
                                  u'clientName',
                                  u'sex',
                                  u'birthDate',
                                  u'nameOS']

        for idx, column in enumerate(self.tblRenunciation.model().cols()):
            columnFields = column.fields()
            if 'birthDate' in columnFields:
                columnRoleList[idx] = QtCore.Qt.UserRole
                titles[idx] = u'Возраст'
            elif columnFields[0] in showedColumnFieldNames:
                columnRoleList[idx] = QtCore.Qt.DisplayRole


        reportDescription = self.getConditionFilter()[0]
        self.tblRenunciation.setReportHeader(u'Отказы от госпитализации')
        self.tblRenunciation.setReportDescription(reportDescription)
        self.tblRenunciation.printContent(columnRoleList, titles)

    def printRenunciationsVerboseReport(self):
        items = self.tblRenunciation.model().items
        db = QtGui.qApp.db

        try:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            cursor.setCharFormat(CReportBase.ReportTitle)
            header = u'Список отказов от госпитализации'
            if QtCore.Qt.mightBeRichText(header):
                cursor.insertHtml(header)
            else:
                cursor.insertText(header)
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportBody)
            description = self.getConditionFilter()[0]
            if QtCore.Qt.mightBeRichText(description):
                cursor.insertHtml(description)
            else:
                cursor.insertText(description)
            cursor.insertBlock()

            tableColumns =  [('9?', [u'№ п/п'], CReportBase.AlignLeft),
                             ('9?', [u'Вид оплаты'], CReportBase.AlignLeft),
                             ('9?', [u'№ ИБ'], CReportBase.AlignLeft),
                             ('9?', [u'код отделения'], CReportBase.AlignLeft),
                             ('9?', [u'Дата и время поступления\nТип госпитализации.'], CReportBase.AlignLeft),
                             ('9?', [u'Фамилия Имя Отчество'], CReportBase.AlignLeft),
                             ('9?', [u'Возраст и дата рождения'], CReportBase.AlignLeft),
                             ('9?', [u'Пол'], CReportBase.AlignLeft),
                             ('9?', [u'Домашний адрес (адрес регистрации), Место работы, должность'], CReportBase.AlignLeft),
                             ('9?', [u'Кем направлен, Кем доставлен, "номер машины", "номер наряда"'], CReportBase.AlignLeft),
                             ('9?', [u'Диагноз направившего учреждения'], CReportBase.AlignLeft),
                             ('9?', [u'Диагноз'], CReportBase.AlignLeft)
            ]

            table = createTable(cursor, tableColumns)

            dlg = QtGui.QDialog()
            dlg.setWindowTitle(u'Выберите категорию')

            # Задача 2711. Город и область в списке согласно настройкам по умолчанию
            tableKladr = db.table('kladr.KLADR').alias('k')
            tableSocr = db.table('kladr.SOCRBASE').alias('s')
            tableQueryKladr = tableKladr
            tableQueryKladr = tableQueryKladr.innerJoin(tableSocr, tableSocr['SCNAME'].eq(tableKladr['SOCR']))

            kladrDict = {'default' : {'shortCode': forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR'])[:2],
                                      'fullCode' : forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR']),
                                      'name'     : forceString(QtGui.qApp.db.translate(tableQueryKladr, tableKladr['CODE'], forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR']), "concat(s.SOCRNAME, ' ', k.NAME)"))
                                     },
                         'province': {'shortCode': forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR'])[:2],
                                      'fullCode' : forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR']),
                                      'name'     : forceString(QtGui.qApp.db.translate(tableQueryKladr, tableKladr['CODE'], forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR']), "concat(k.NAME, ' ', s.SOCRNAME)"))
                                      }
                         }

            filterModel = CCheckableModel([kladrDict['province']['name'],    # 0
                                           u'Иногородние',                   # 1
                                           u'Иностранцы',                    # 2
                                           kladrDict['default']['name'],     # 3
                                           u'Без адреса регистрации',        # 4
                                           u'Без документа'])                # 5

            filterModel.setEnabled(0, forceBool(kladrDict['province']['fullCode']))

            listView = QtGui.QListView()
            listView.setModel(filterModel)
            btnApply = QtGui.QPushButton(u'Применить')
            btnApply.setDefault(True)
            btnApply.clicked.connect(dlg.accept)
            layout = QtGui.QVBoxLayout()
            layout.addWidget(listView)
            layout.addWidget(btnApply)
            dlg.setLayout(layout)

            dlg.exec_()

            filterList = filterModel.checkStateList()

            # Формирование кэша данных о пациентах модели
            clientIdList = []
            eventIdList = []
            actionIdList = []
            for item in items:
                clientId = item.get('clientId', None)
                eventId = item.get('eventId', None)
                actionId = item.get('actionId', None)
                if clientId and clientId not in clientIdList:
                    clientIdList.append(clientId)
                if eventId and eventId not in eventIdList:
                    eventIdList.append(eventId)
                if actionId and actionId not in actionIdList:
                    actionIdList.append(actionId)

            tableClient = db.table('Client')
            tableEvent = db.table('Event')
            tableClientDocument = db.table('ClientDocument')
            tableClientDocumentType = db.table('rbDocumentType')
            tableRegClientAddress = db.table('ClientAddress').alias('RegClientAddress')
            tableRegAddress = db.table('Address').alias('RegAddress')
            tableRegAddressHouse = db.table('AddressHouse').alias('RegAddressHouse')
            tableDiagnostic = db.table('Diagnostic')
            tableDiagnosis = db.table('Diagnosis')
            tableDiagnosisType = db.table('rbDiagnosisType')
            tableMKB = db.table('MKB_Tree')

            queryTable = tableClient.leftJoin(tableEvent, tableEvent['client_id'].eq(tableClient['id']))

            queryTable = queryTable.leftJoin(tableClientDocument, '%s = getClientDocumentId(%s)' % (tableClientDocument['id'].name(), tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableClientDocumentType, tableClientDocumentType['id'].eq(tableClientDocument['documentType_id']))

            queryTable = queryTable.leftJoin(tableRegClientAddress, '%s = getClientRegAddressId(%s)' % (tableRegClientAddress['id'].name(), tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableRegAddress, tableRegAddress['id'].eq(tableRegClientAddress['address_id']))
            queryTable = queryTable.leftJoin(tableRegAddressHouse, tableRegAddressHouse['id'].eq(tableRegAddress['house_id']))

            queryTable = queryTable.leftJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                                               tableDiagnostic['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableDiagnosisType, [tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']),
                                                                  tableDiagnosisType['code'].inlist(['7', '11'])]) # Основной предварительный и Сопутствующий предварительный
            queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
            queryTable = queryTable.leftJoin(tableMKB, tableMKB['DiagID'].eq(tableDiagnosis['MKB']))

            cols = [tableClient['id'].alias('clientId'),
                    '%s AS isExistsRegAddress' % tableRegClientAddress['id'].isNotNull(),
                    '%s AS isExistsDocument' % tableClientDocument['id'].isNotNull(),
                    u'''%s AND EXISTS(SELECT SS.id
                                     FROM ClientSocStatus AS SS
                                            INNER JOIN rbSocStatusClass AS SSC ON SSC.id = SS.socStatusClass_id
                                            INNER JOIN rbSocStatusType AS SST ON SST.id = SS.socStatusType_id
                                     WHERE
                                            SS.client_id = %s
                                            AND SS.deleted = 0
                                            AND SSC.flatCode LIKE 'citizenship'
                                            -- исключение типа "Россия" для соц. статуса "Гражданство" (код 643 согласно ISO 4217)
                                            AND SST.code NOT LIKE '%%643'
                    ) AS isForeigner''' % (tableClientDocumentType['isForeigner'].name(), tableClient['id'].name()),
                    # tableClientDocumentType['isForeigner'],
                    tableRegAddressHouse['KLADRCode'],
                    tableDiagnosis['MKB'],
                    tableMKB['DiagName'],
                    'formatClientAddress(%s) AS regAddress' % tableRegClientAddress['id'].name(),
                    'getClientLocAddress(%s) AS locAddress' % tableClient['id'].name(),
                    'getClientWork(%s) AS work' % tableClient['id'].name(),
                    'getClientPolicyId(%s, 1) IS NOT NULL AS isExistsCompulsoryPolicy' % tableClient['id'].name(),
                    'getClientPolicyId(%s, 0) IS NOT NULL AS isExistsVoluntaryPolicy' % tableClient['id'].name()
            ]

            cond = [tableClient['id'].inlist(clientIdList),
                    tableEvent['id'].inlist(eventIdList)]

            order = [tableClient['id'],
                     tableDiagnosisType['code']]

            clientInfoCache = {}
            for record in db.getRecordList(queryTable, cols, cond, order):
                clientId = forceRef(record.value('clientId'))
                if not clientInfoCache.has_key(clientId):
                    clientInfo = {'isExistsRegAddress' : forceBool(record.value('isExistsRegAddress')),
                                  'isExistsDocument' : forceBool(record.value('isExistsDocument')),
                                  'isForeigner' : forceBool(record.value('isForeigner')),
                                  'isExistsCompulsoryPolicy' : forceBool(record.value('isExistsCompulsoryPolicy')),
                                  'isExistsVoluntaryPolicy' : forceBool(record.value('isExistsVoluntaryPolicy')),
                                  'KLADRCode' : forceString(record.value('KLADRCode')),
                                  'regAddress' : forceString(record.value('regAddress')),
                                  'locAddress' : forceString(record.value('locAddress')),
                                  'work' : forceString(record.value('work')),
                                  'diagnosisList' : []}
                    clientInfoCache[clientId] = clientInfo
                else:
                    clientInfoCache[clientId]['diagnosisList'].append(u'%s (%s)' % (forceString(record.value('MKB')),
                                                                                    forceString(record.value('DiagName'))))


            actionInfo = {}
            #atronah: подгрузка данных о действиях:
            tableAction = db.table('Action')
            for record in db.getRecordList(tableAction, cols = '*', where = tableAction['id'].inlist(actionIdList)):
                actionInfo[forceRef(record.value('id'))] = CAction(record = record)

            for item in items:
                action = actionInfo[item.get('actionId', None)]
                eventId = item.get('eventId', None)
                clientInfo = clientInfoCache[item['clientId']]
                if True in filterList: # Если включен хотя бы один фильтр
                    # загрузка данных по документу, если включен один из фильтров, связанных с документами
                    if filterList[2] or filterList[5] or filterList[1]:
                        isForeigner = clientInfo['isForeigner']

                    # Если хотя бы одно из условий не верно, то пропускаем пациента
                    if not (
                            # включен фильтр "Область по умолчанию" и пациент из области по умолчанию
                            (filterList[0] and (clientInfo['isExistsRegAddress']
                                                and clientInfo['KLADRCode'][:2] == kladrDict['province']['shortCode']))

                            # включен фильтр "Иногородние" и пациент иногородний (т.е. не из области по умолчанию и не из населённого пункта по умолчанию)
                            or (filterList[1] and (clientInfo['isExistsRegAddress']
                                                   and clientInfo['KLADRCode'][:2] not in [kladrDict['province']['shortCode'], kladrDict['default']['shortCode']])
                                and not isForeigner)

                            # включен фильтр "Иностранцы" и пациент иностранец (т.е. тип документа соотв. ИНПАСПОРТ, в соц.статусе "гражданстово" не РФ)
                            or (filterList[2] and isForeigner)

                            # включен фильтр "Населённый пункт по умолчанию" и пациент из населённого пункта по умолчанию
                            or (filterList[3] and (clientInfo['isExistsRegAddress']
                                                   and clientInfo['KLADRCode'][:2] == kladrDict['default']['shortCode']))

                            # включен фильтр "Без адреса регистрации" и пациент без адреса регистрации
                            or (filterList[4] and not (clientInfo['isExistsRegAddress']
                                                       and clientInfo['KLADRCode']))

                            # включен фильтр "Без документа" и пациент без документа
                            or (filterList[5] and not clientInfo['isExistsDocument'])
                    ):
                        continue


                row = table.addRow()
                table.setText(row, 0, row)

                if clientInfo['isExistsCompulsoryPolicy']:
                    if clientInfo['isExistsVoluntaryPolicy']:
                        table.setText(row, 1, u'ОМС/ДМС')
                    else:
                        table.setText(row, 1, u'ОМС')
                else:
                    if clientInfo['isExistsVoluntaryPolicy']:
                        table.setText(row, 1, u'ДМС')
                    elif clientInfo['isForeigner']:
                        table.setText(row, 1, u'платно')

                table.setText(row, 2, item.get('externalId', u'')) # № ИБ
                table.setText(row, 3, forceString(db.translate('OrgStructure', 'id', action[u'Направлен в отделение'], 'code'))) # код отделения
                # Дата и время поступления\nТип госпитализации.
                table.setText(row, 4, u'%s, %s' % (forceString(item.get('begDate', u'')),
                                                       forceString(db.translate('rbResult',
                                                                                'id',
                                                                                item.get('eventResultId', None),
                                                                                'name')))
                )
                table.setText(row, 5, item.get('clientName', u'')) # Фамилия Имя Отчество
                table.setText(row, 6, item.get('birthDate', u'')) # Возраст и дата рождения
                table.setText(row, 7, item.get('sex', u'')) # Пол
                # Домашний адрес (адрес регистрации), Место работы, должность
                table.setText(row, 8, u'%s (%s) %s' % (clientInfo['locAddress'],
                                                       clientInfo['regAddress'] or u'---',
                                                       clientInfo['work']))
                sourceOrgId = action[u'Кем направлен']
                sourceOrgText = forceString(db.translate('Organisation', 'id', sourceOrgId, 'infisCode')) \
                    if sourceOrgId \
                    else forceString(action[u'Прочие направители']) or u'---'
                # Кем направлен, Кем доставлен, "номер машины", "номер наряда"
                deliveryman = forceString(action[u'Кем доставлен']) or u'---'
                transportNumber = forceString(action[u'№ Машины']) or u'---'
                orderNumber = forceString(action[u'№ Наряда']) or u'---'
                table.setText(row, 9, u'%s, %s, %s, %s' % (sourceOrgText,
                                                           deliveryman,
                                                           transportNumber,
                                                           orderNumber))
                # Диагноз направившего учреждения
                table.setText(row, 10, forceString(action[u'Диагноз направителя']))
                # Диагноз
                table.setText(row, 11, u', '.join([forceString(action[u'Диагноз приемного отделения'])] + clientInfo['diagnosisList']))


            view = CReportViewDialog(self)
            view.setText(doc)
            view.exec_()
        except:
            QtGui.qApp.logCurrentException()

    @QtCore.pyqtSlot()
    def printReportArchiveHistory(self):
        CReportArchiveHistory(self).exec_()

    @QtCore.pyqtSlot()
    def printReportArchiveList(self):
        CReportArchiveList(self).exec_()

    #TODO: mdldml: вынести в HospitalBedsReport
    ## Вывод отчета "Список поступивших больных" (описание отчета в i1168)
    @QtCore.pyqtSlot()
    def printReceivedReport(self):

        params = self.getFilter()
        receivedFilterIdx = params.get('received', None)
        if receivedFilterIdx != 0: # Поступили: в ЛПУ
            QtGui.QMessageBox.information(self,
                                          u'Некорректные условия формирования отчета',
                                          u'Данный отчет может быть сформирован\n'
                                          u'только при значении фильтра "Поступили" = "в ЛПУ"',
                                          buttons = QtGui.QMessageBox.Ok,
                                          defaultButton = QtGui.QMessageBox.Ok)
            return

        # Получение списка поступивших
        items = self.tblReceived.model().items
        db = QtGui.qApp.db
        # Загрузка действий "Движение", следующих сразу за поступлением
        #(аналогично выбору фильтра "Поуступили: в отделение")
        # для тех же настроек фильтра
        params['received'] = 1
        movingRecordList = self.tblReceived.model().getRecordList(params)

        movingBegDatetimeByEvent = {}
        for movingRecord in movingRecordList:
            eventId = forceRef(movingRecord.value('eventId'))
            movingBegDatetimeByEvent[eventId] = forceString(movingRecord.value('begDate'))


        try:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            cursor.setCharFormat(CReportBase.ReportTitle)
            header = u'Список поступивших больных'
            if QtCore.Qt.mightBeRichText(header):
                cursor.insertHtml(header)
            else:
                cursor.insertText(header)
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportBody)
            description = self.getConditionFilter()[0]
            if QtCore.Qt.mightBeRichText(description):
                cursor.insertHtml(description)
            else:
                cursor.insertText(description)
            cursor.insertBlock()

            tableColumns =  [('9?', [u'№ п/п'], CReportBase.AlignLeft),
                             ('9?', [u'Вид оплаты'], CReportBase.AlignLeft),
                             ('9?', [u'№ ИБ'], CReportBase.AlignLeft),
                             ('9?', [u'код отделения'], CReportBase.AlignLeft),
                             ('9?', [u'Дата и время поступления\nи отправки пациента.\nТип госпитализации.'], CReportBase.AlignLeft),
                             ('9?', [u'Фамилия Имя Отчество'], CReportBase.AlignLeft),
                             ('9?', [u'Возраст и дата рождения'], CReportBase.AlignLeft),
                             ('9?', [u'Пол'], CReportBase.AlignLeft),
                             ('9?', [u'Домашний адрес (адрес регистрации), Место работы, должность'], CReportBase.AlignLeft),
                             ('9?', [u'Кем направлен, Кем доставлен, "номер машины", "номер наряда"'], CReportBase.AlignLeft),
                             ('9?', [u'Диагноз направившего учреждения'], CReportBase.AlignLeft),
                             ('9?', [u'Диагноз'], CReportBase.AlignLeft)
            ]

            table = createTable(cursor, tableColumns)

            dlg = QtGui.QDialog()
            dlg.setWindowTitle(u'Выберите категорию')

            # Задача 2711. Город и область в списке согласно настройкам по умолчанию
            tableKladr = db.table('kladr.KLADR').alias('k')
            tableSocr = db.table('kladr.SOCRBASE').alias('s')
            tableQueryKladr = tableKladr
            tableQueryKladr = tableQueryKladr.innerJoin(tableSocr, tableSocr['SCNAME'].eq(tableKladr['SOCR']))

            kladrDict = {'default' : {'shortCode': forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR'])[:2],
                                      'fullCode' : forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR']),
                                      'name'     : forceString(QtGui.qApp.db.translate(tableQueryKladr, tableKladr['CODE'], forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR']), "concat(s.SOCRNAME, ' ', k.NAME)"))
                                     },
                         'province': {'shortCode': forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR'])[:2],
                                      'fullCode' : forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR']),
                                      'name'     : forceString(QtGui.qApp.db.translate(tableQueryKladr, tableKladr['CODE'], forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR']), "concat(k.NAME, ' ', s.SOCRNAME)"))
                                      }
                         }

            filterModel = CCheckableModel([kladrDict['province']['name'],    # 0
                                           u'Иногородние',                   # 1
                                           u'Иностранцы',                    # 2
                                           kladrDict['default']['name'],     # 3
                                           u'Без адреса регистрации',        # 4
                                           u'Без документа'])                # 5

            filterModel.setEnabled(0, forceBool(kladrDict['province']['fullCode']))

            listView = QtGui.QListView()
            listView.setModel(filterModel)
            btnApply = QtGui.QPushButton(u'Применить')
            btnApply.setDefault(True)
            btnApply.clicked.connect(dlg.accept)
            layout = QtGui.QVBoxLayout()
            layout.addWidget(listView)
            layout.addWidget(btnApply)
            dlg.setLayout(layout)

            dlg.exec_()

            filterList = filterModel.checkStateList()

            # Формирование кэша данных о пациентах модели
            clientIdList = []
            eventIdList = []
            actionIdList = []
            for item in items:
                clientId = item.get('clientId', None)
                eventId = item.get('eventId', None)
                actionId = item.get('actionId', None)
                if clientId and clientId not in clientIdList:
                    clientIdList.append(clientId)
                if eventId and eventId not in eventIdList:
                    eventIdList.append(eventId)
                if actionId and actionId not in actionIdList:
                    actionIdList.append(actionId)

            tableClient = db.table('Client')
            tableEvent = db.table('Event')
            tableClientDocument = db.table('ClientDocument')
            tableClientDocumentType = db.table('rbDocumentType')
            tableRegClientAddress = db.table('ClientAddress').alias('RegClientAddress')
            tableRegAddress = db.table('Address').alias('RegAddress')
            tableRegAddressHouse = db.table('AddressHouse').alias('RegAddressHouse')
            tableDiagnostic = db.table('Diagnostic')
            tableDiagnosis = db.table('Diagnosis')
            tableDiagnosisType = db.table('rbDiagnosisType')
            tableMKB = db.table('MKB_Tree')

            queryTable = tableClient.leftJoin(tableEvent, tableEvent['client_id'].eq(tableClient['id']))

            queryTable = queryTable.leftJoin(tableClientDocument, '%s = getClientDocumentId(%s)' % (tableClientDocument['id'].name(), tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableClientDocumentType, tableClientDocumentType['id'].eq(tableClientDocument['documentType_id']))

            queryTable = queryTable.leftJoin(tableRegClientAddress, '%s = getClientRegAddressId(%s)' % (tableRegClientAddress['id'].name(), tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableRegAddress, tableRegAddress['id'].eq(tableRegClientAddress['address_id']))
            queryTable = queryTable.leftJoin(tableRegAddressHouse, tableRegAddressHouse['id'].eq(tableRegAddress['house_id']))

            queryTable = queryTable.leftJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                                               tableDiagnostic['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableDiagnosisType, [tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']),
                                                                  tableDiagnosisType['code'].inlist(['7', '11'])]) # Основной предварительный и Сопутствующий предварительный
            queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
            queryTable = queryTable.leftJoin(tableMKB, tableMKB['DiagID'].eq(tableDiagnosis['MKB']))

            cols = [tableClient['id'].alias('clientId'),
                    '%s AS isExistsRegAddress' % tableRegClientAddress['id'].isNotNull(),
                    '%s AS isExistsDocument' % tableClientDocument['id'].isNotNull(),
                    u'''%s AND EXISTS(SELECT SS.id
                                     FROM ClientSocStatus AS SS
                                            INNER JOIN rbSocStatusClass AS SSC ON SSC.id = SS.socStatusClass_id
                                            INNER JOIN rbSocStatusType AS SST ON SST.id = SS.socStatusType_id
                                     WHERE
                                            SS.client_id = %s
                                            AND SS.deleted = 0
                                            AND SSC.flatCode LIKE 'citizenship'
                                            -- исключение типа "Россия" для соц. статуса "Гражданство" (код 643 согласно ISO 4217)
                                            AND SST.code NOT LIKE '%%643'
                    ) AS isForeigner''' % (tableClientDocumentType['isForeigner'].name(), tableClient['id'].name()),
                    # tableClientDocumentType['isForeigner'],
                    tableRegAddressHouse['KLADRCode'],
                    tableDiagnosis['MKB'],
                    tableMKB['DiagName'],
                    'formatClientAddress(%s) AS regAddress' % tableRegClientAddress['id'].name(),
                    'getClientLocAddress(%s) AS locAddress' % tableClient['id'].name(),
                    'getClientWork(%s) AS work' % tableClient['id'].name(),
                    'getClientPolicyId(%s, 1) IS NOT NULL AS isExistsCompulsoryPolicy' % tableClient['id'].name(),
                    'getClientPolicyId(%s, 0) IS NOT NULL AS isExistsVoluntaryPolicy' % tableClient['id'].name()
            ]

            cond = [tableClient['id'].inlist(clientIdList),
                    tableEvent['id'].inlist(eventIdList)]

            order = [tableClient['id'],
                     tableDiagnosisType['code']]

            clientInfoCache = {}
            for record in db.getRecordList(queryTable, cols, cond, order):
                clientId = forceRef(record.value('clientId'))
                if not clientInfoCache.has_key(clientId):
                    clientInfo = {'isExistsRegAddress' : forceBool(record.value('isExistsRegAddress')),
                                  'isExistsDocument' : forceBool(record.value('isExistsDocument')),
                                  'isForeigner' : forceBool(record.value('isForeigner')),
                                  'isExistsCompulsoryPolicy' : forceBool(record.value('isExistsCompulsoryPolicy')),
                                  'isExistsVoluntaryPolicy' : forceBool(record.value('isExistsVoluntaryPolicy')),
                                  'KLADRCode' : forceString(record.value('KLADRCode')),
                                  'regAddress' : forceString(record.value('regAddress')),
                                  'locAddress' : forceString(record.value('locAddress')),
                                  'work' : forceString(record.value('work')),
                                  'diagnosisList' : []}
                    clientInfoCache[clientId] = clientInfo
                else:
                    clientInfoCache[clientId]['diagnosisList'].append(u'%s (%s)' % (forceString(record.value('MKB')),
                                                                                    forceString(record.value('DiagName'))))


            actionInfo = {}
            #atronah: подгрузка данных о действиях:
            tableAction = db.table('Action')
            for record in db.getRecordList(tableAction, cols = '*', where = tableAction['id'].inlist(actionIdList)):
                actionInfo[forceRef(record.value('id'))] = CAction(record = record)

            for item in items:
                action = actionInfo[item.get('actionId', None)]
                eventId = item.get('eventId', None)
                clientInfo = clientInfoCache[item['clientId']]
                if True in filterList: # Если включен хотя бы один фильтр
                    # загрузка данных по документу, если включен один из фильтров, связанных с документами
                    if filterList[2] or filterList[5] or filterList[1]:
                        isForeigner = clientInfo['isForeigner']

                    # Если хотя бы одно из условий не верно, то пропускаем пациента
                    if not (
                            # включен фильтр "Область по умолчанию" и пациент из области по умолчанию
                            (filterList[0] and (clientInfo['isExistsRegAddress']
                                                and clientInfo['KLADRCode'][:2] == kladrDict['province']['shortCode']))

                            # включен фильтр "Иногородние" и пациент иногородний (т.е. не из области по умолчанию и не из населённого пункта по умолчанию)
                            or (filterList[1] and (clientInfo['isExistsRegAddress']
                                                   and clientInfo['KLADRCode'][:2] not in [kladrDict['province']['shortCode'], kladrDict['default']['shortCode']])
                                and not isForeigner)

                            # включен фильтр "Иностранцы" и пациент иностранец (т.е. тип документа соотв. ИНПАСПОРТ, в соц.статусе "гражданстово" не РФ)
                            or (filterList[2] and isForeigner)

                            # включен фильтр "Населённый пункт по умолчанию" и пациент из населённого пункта по умолчанию
                            or (filterList[3] and (clientInfo['isExistsRegAddress']
                                                   and clientInfo['KLADRCode'][:2] == kladrDict['default']['shortCode']))

                            # включен фильтр "Без адреса регистрации" и пациент без адреса регистрации
                            or (filterList[4] and not (clientInfo['isExistsRegAddress']
                                                       and clientInfo['KLADRCode']))

                            # включен фильтр "Без документа" и пациент без документа
                            or (filterList[5] and not clientInfo['isExistsDocument'])
                    ):
                        continue


                row = table.addRow()
                table.setText(row, 0, row)

                if clientInfo['isExistsCompulsoryPolicy']:
                    if clientInfo['isExistsVoluntaryPolicy']:
                        table.setText(row, 1, u'ОМС/ДМС')
                    else:
                        table.setText(row, 1, u'ОМС')
                else:
                    if clientInfo['isExistsVoluntaryPolicy']:
                        table.setText(row, 1, u'ДМС')
                    elif clientInfo['isForeigner']:
                        table.setText(row, 1, u'платно')

                table.setText(row, 2, item.get('externalId', u'')) # № ИБ
                table.setText(row, 3, forceString(db.translate('OrgStructure', 'id', action[u'Направлен в отделение'], 'code'))) # код отделения
                # Дата и время поступления\nи отправки пациента.\nТип госпитализации.
                table.setText(row, 4, u'%s, %s, %s' % (forceString(item.get('begDate', u'')),
                                                       movingBegDatetimeByEvent.get(eventId, u''),
                                                       forceString(db.translate('rbResult',
                                                                                'id',
                                                                                item.get('eventResultId', None),
                                                                                'name')))
                )
                table.setText(row, 5, item.get('clientName', u'')) # Фамилия Имя Отчество
                table.setText(row, 6, item.get('birthDate', u'')) # Возраст и дата рождения
                table.setText(row, 7, item.get('sex', u'')) # Пол
                # Домашний адрес (адрес регистрации), Место работы, должность
                table.setText(row, 8, u'%s (%s) %s' % (clientInfo['locAddress'],
                                                       clientInfo['regAddress'] or u'---',
                                                       clientInfo['work']))
                sourceOrgId = action[u'Кем направлен']
                sourceOrgText = forceString(db.translate('Organisation', 'id', sourceOrgId, 'infisCode')) \
                    if sourceOrgId \
                    else forceString(action[u'Прочие направители']) or u'---'
                # Кем направлен, Кем доставлен, "номер машины", "номер наряда"
                deliveryman = forceString(action[u'Кем доставлен']) or u'---'
                transportNumber = forceString(action[u'№ Машины']) or u'---'
                orderNumber = forceString(action[u'№ Наряда']) or u'---'
                table.setText(row, 9, u'%s, %s, %s, %s' % (sourceOrgText,
                                                           deliveryman,
                                                           transportNumber,
                                                           orderNumber))
                # Диагноз направившего учреждения
                table.setText(row, 10, forceString(action[u'Диагноз направителя']))
                # Диагноз
                table.setText(row, 11, u', '.join([forceString(action[u'Диагноз приемного отделения'])] + clientInfo['diagnosisList']))


            view = CReportViewDialog(self)
            view.setText(doc)
            view.exec_()
        except:
            QtGui.qApp.logCurrentException()

    #TODO: mdldml: вынести в HospitalBedsReport
    ## Вывод отчета "Список поступивших больных (для онко)"
    @QtCore.pyqtSlot()
    def printReceivedOnkoReport(self):

        params = self.getFilter()
        receivedFilterIdx = params.get('received', None)
        if receivedFilterIdx != 0: # Поступили: в ЛПУ
            QtGui.QMessageBox.information(self,
                                          u'Некорректные условия формирования отчета',
                                          u'Данный отчет может быть сформирован\n'
                                          u'только при значении фильтра "Поступили" = "в ЛПУ"',
                                          buttons = QtGui.QMessageBox.Ok,
                                          defaultButton = QtGui.QMessageBox.Ok)
            return

        # Получение списка поступивших
        items =  self.tblReceived.model().items
        db = QtGui.qApp.db
        # Загрузка действий "Движение", следующих сразу за поступлением
        #(аналогично выбору фильтра "Поуступили: в отделение")
        # для тех же настроек фильтра
        params['received'] = 1
        movingRecordList = self.tblReceived.model().getRecordList(params)

        movingBegDatetimeByEvent = {}
        for movingRecord in movingRecordList:
            eventId = forceRef(movingRecord.value('eventId'))
            movingBegDatetimeByEvent[eventId] = forceString(movingRecord.value('begDate'))


        try:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            cursor.setCharFormat(CReportBase.ReportTitle)
            header = u'Список поступивших больных (для онко)'
            if QtCore.Qt.mightBeRichText(header):
                cursor.insertHtml(header)
            else:
                cursor.insertText(header)
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportBody)
            description = self.getConditionFilter()[0]
            if QtCore.Qt.mightBeRichText(description):
                cursor.insertHtml(description)
            else:
                cursor.insertText(description)
            cursor.insertBlock()

            tableColumns =  [('10?', [u'№ п/п'], CReportBase.AlignLeft),
                             ('10?', [u'№ ИБ'], CReportBase.AlignLeft),
                             ('10?', [u'код отделения'], CReportBase.AlignLeft),
                             ('10?', [u'Дата и время поступления\nи отправки пациента.'], CReportBase.AlignLeft),
                             ('10?', [u'Фамилия Имя Отчество'], CReportBase.AlignLeft),
                             ('10?', [u'Возраст'], CReportBase.AlignLeft),
                             ('10?', [u'Дата рождения'], CReportBase.AlignLeft),
                             ('10?', [u'Пол'], CReportBase.AlignLeft),
                             ('10?', [u'Домашний адрес (адрес регистрации), Место работы, должность'], CReportBase.AlignLeft),
                             ('10?', [u'Гражданство'], CReportBase.AlignLeft),
                             ('10?', [u'Диагноз направившего учреждения'], CReportBase.AlignLeft),
                             ('10?', [u'Дата выписки'], CReportBase.AlignLeft)
            ]

            table = createTable(cursor, tableColumns)

            dlg = QtGui.QDialog()
            dlg.setWindowTitle(u'Выберите категорию')

            # Задача 2711. Город и область в списке согласно настройкам по умолчанию
            tableKladr = db.table('kladr.KLADR').alias('k')
            tableSocr = db.table('kladr.SOCRBASE').alias('s')
            tableQueryKladr = tableKladr
            tableQueryKladr = tableQueryKladr.innerJoin(tableSocr, tableSocr['SCNAME'].eq(tableKladr['SOCR']))

            kladrDict = {'default' : {'shortCode': forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR'])[:2],
                                      'fullCode' : forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR']),
                                      'name'     : forceString(QtGui.qApp.db.translate(tableQueryKladr, tableKladr['CODE'], forceString(QtGui.qApp.preferences.appPrefs['defaultKLADR']), "concat(s.SOCRNAME, ' ', k.NAME)"))
                                     },
                         'province': {'shortCode': forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR'])[:2],
                                      'fullCode' : forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR']),
                                      'name'     : forceString(QtGui.qApp.db.translate(tableQueryKladr, tableKladr['CODE'], forceString(QtGui.qApp.preferences.appPrefs['provinceKLADR']), "concat(k.NAME, ' ', s.SOCRNAME)"))
                                      }
                         }

            filterModel = CCheckableModel([kladrDict['province']['name'],    # 0
                                           u'Иногородние',                   # 1
                                           u'Иностранцы',                    # 2
                                           kladrDict['default']['name'],     # 3
                                           u'Без адреса регистрации',        # 4
                                           u'Без документа',                 # 5
                                           u'Граждане Белоруссии',           # 6
                                           u'Граждане Украины'])             # 7

            filterModel.setEnabled(0, forceBool(kladrDict['province']['fullCode']))

            listView = QtGui.QListView()
            listView.setModel(filterModel)
            btnApply = QtGui.QPushButton(u'Применить')
            btnApply.setDefault(True)
            btnApply.clicked.connect(dlg.accept)
            layout = QtGui.QVBoxLayout()
            layout.addWidget(listView)
            layout.addWidget(btnApply)
            dlg.setLayout(layout)

            dlg.exec_()

            filterList = filterModel.checkStateList()

            # Формирование кэша данных о пациентах модели
            clientIdList = []
            eventIdList = []
            actionIdList = []
            for item in items:
                clientId = item.get('clientId', None)
                eventId = item.get('eventId', None)
                actionId = item.get('actionId', None)
                if clientId and clientId not in clientIdList:
                    clientIdList.append(clientId)
                if eventId and eventId not in eventIdList:
                    eventIdList.append(eventId)
                if actionId and actionId not in actionIdList:
                    actionIdList.append(actionId)

            tableClient = db.table('Client')
            tableEvent = db.table('Event')
            tableClientDocument = db.table('ClientDocument')
            tableClientDocumentType = db.table('rbDocumentType')
            tableRegClientAddress = db.table('ClientAddress').alias('RegClientAddress')
            tableRegAddress = db.table('Address').alias('RegAddress')
            tableRegAddressHouse = db.table('AddressHouse').alias('RegAddressHouse')
            tableDiagnostic = db.table('Diagnostic')
            tableDiagnosis = db.table('Diagnosis')
            tableDiagnosisType = db.table('rbDiagnosisType')
            tableMKB = db.table('MKB_Tree')

            queryTable = tableClient.leftJoin(tableEvent, tableEvent['client_id'].eq(tableClient['id']))

            queryTable = queryTable.leftJoin(tableClientDocument, '%s = getClientDocumentId(%s)' % (tableClientDocument['id'].name(), tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableClientDocumentType, tableClientDocumentType['id'].eq(tableClientDocument['documentType_id']))

            queryTable = queryTable.leftJoin(tableRegClientAddress, '%s = getClientRegAddressId(%s)' % (tableRegClientAddress['id'].name(), tableClient['id'].name()))
            queryTable = queryTable.leftJoin(tableRegAddress, tableRegAddress['id'].eq(tableRegClientAddress['address_id']))
            queryTable = queryTable.leftJoin(tableRegAddressHouse, tableRegAddressHouse['id'].eq(tableRegAddress['house_id']))

            queryTable = queryTable.leftJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                                               tableDiagnostic['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableDiagnosisType, [tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']),
                                                                  tableDiagnosisType['code'].inlist(['7', '11'])]) # Основной предварительный и Сопутствующий предварительный
            queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
            queryTable = queryTable.leftJoin(tableMKB, tableMKB['DiagID'].eq(tableDiagnosis['MKB']))

            cols = [tableClient['id'].alias('clientId'),
                    '%s AS isExistsRegAddress' % tableRegClientAddress['id'].isNotNull(),
                    '%s AS isExistsDocument' % tableClientDocument['id'].isNotNull(),
                    u'''%s AND EXISTS(SELECT SS.id
                                     FROM ClientSocStatus AS SS
                                            INNER JOIN rbSocStatusClass AS SSC ON SSC.id = SS.socStatusClass_id
                                            INNER JOIN rbSocStatusType AS SST ON SST.id = SS.socStatusType_id
                                     WHERE
                                            SS.client_id = %s
                                            AND SS.deleted = 0
                                            AND SSC.flatCode LIKE 'citizenship'
                                            -- исключение типа "Россия" для соц. статуса "Гражданство" (код 643 согласно ISO 4217)
                                            AND SST.code NOT LIKE '%%643'
                    ) AS isForeigner''' % (tableClientDocumentType['isForeigner'].name(), tableClient['id'].name()),
                    tableClientDocumentType['isForeigner'],
                    tableRegAddressHouse['KLADRCode'],
                    tableDiagnosis['MKB'],
                    tableMKB['DiagName'],
                    'formatClientAddress(%s) AS regAddress' % tableRegClientAddress['id'].name(),
                    'getClientLocAddress(%s) AS locAddress' % tableClient['id'].name(),
                    'getClientWork(%s) AS work' % tableClient['id'].name(),
                    'getClientPolicyId(%s, 1) IS NOT NULL AS isExistsCompulsoryPolicy' % tableClient['id'].name(),
                    '''(SELECT SST.code
                        FROM ClientSocStatus AS SS
                        INNER JOIN rbSocStatusClass AS SSC ON SSC.id = SS.socStatusClass_id
                        INNER JOIN rbSocStatusType AS SST ON SST.id = SS.socStatusType_id
                        WHERE SS.client_id = %(clientId)s
                              AND SS.deleted = 0
                              AND SSC.flatCode LIKE 'citizenship') AS countryCitizenshipCode
                    ''' % {'clientId' : tableClient['id'].name()}
            ]

            cond = [tableClient['id'].inlist(clientIdList),
                    tableEvent['id'].inlist(eventIdList)]

            order = [tableClient['id'],
                     tableDiagnosisType['code']]

            clientInfoCache = {}
            for record in db.getRecordList(queryTable, cols, cond, order):
                clientId = forceRef(record.value('clientId'))
                if not clientInfoCache.has_key(clientId):
                    clientInfo = {'isExistsRegAddress' : forceBool(record.value('isExistsRegAddress')),
                                  'isExistsDocument' : forceBool(record.value('isExistsDocument')),
                                  'isForeigner' : forceBool(record.value('isForeigner')),
                                  'isExistsCompulsoryPolicy' : forceBool(record.value('isExistsCompulsoryPolicy')),
                                  'KLADRCode' : forceString(record.value('KLADRCode')),
                                  'regAddress' : forceString(record.value('regAddress')),
                                  'locAddress' : forceString(record.value('locAddress')),
                                  'work' : forceString(record.value('work')),
                                  'diagnosisList' : [],
                                  'countryCitizenshipCode' : forceString(record.value('countryCitizenshipCode'))}
                    clientInfoCache[clientId] = clientInfo
                else:
                    clientInfoCache[clientId]['diagnosisList'].append(u'%s (%s)' % (forceString(record.value('MKB')),
                                                                                    forceString(record.value('DiagName'))))


            actionInfo = {}
            #atronah: подгрузка данных о действиях:
            tableAction = db.table('Action')
            for record in db.getRecordList(tableAction, cols = '*', where = tableAction['id'].inlist(actionIdList)):
                actionInfo[forceRef(record.value('id'))] = CAction(record = record)

            for item in items:
                action = actionInfo[item.get('actionId', None)]
                eventId = item.get('eventId', None)
                clientInfo = clientInfoCache[item['clientId']]
                if True in filterList: # Если включен хотя бы один фильтр
                    # загрузка данных по документу, если включен один из фильтров, связанных с документами
                    if filterList[2] or filterList[5] or filterList[1]:
                        isForeigner = clientInfo['isForeigner']

                    # Если хотя бы одно из условий не верно, то пропускаем пациента
                    if not (
                            # включен фильтр "Область по умолчанию" и пациент из области по умолчанию
                            (filterList[0] and (clientInfo['isExistsRegAddress']
                                                and clientInfo['KLADRCode'][:2] == kladrDict['province']['shortCode']))

                            # включен фильтр "Иногородние" и пациент иногородний (т.е. не из области по умолчанию и не из населённого пункта по умолчанию)
                            or (filterList[1] and (clientInfo['isExistsRegAddress']
                                                   and clientInfo['KLADRCode'][:2] not in [kladrDict['province']['shortCode'], kladrDict['default']['shortCode']])
                                and not isForeigner)

                            # включен фильтр "Иностранцы" и пациент иностранец (т.е. тип документа соотв. ИНПАСПОРТ)
                            or (filterList[2] and isForeigner and not clientInfo['isExistsCompulsoryPolicy'])

                            # включен фильтр "Населённый пункт по умолчанию" и пациент из населённого пункта по умолчанию
                            or (filterList[3] and (clientInfo['isExistsRegAddress']
                                                   and clientInfo['KLADRCode'][:2] == kladrDict['default']['shortCode']))

                            # включен фильтр "Без адреса регистрации" и пациент без адреса регистрации
                            or (filterList[4] and not (clientInfo['isExistsRegAddress']
                                                       and clientInfo['KLADRCode']))

                            # включен фильтр "Без документа" и пациент без документа
                            or (filterList[5] and not clientInfo['isExistsDocument'])

                            # включён фильтр "Граждане Белоруссии" (код Белоруссии 112, согласно ISO 4217, на 25.09.2014)
                            or (filterList[6] and not filterList[7] and clientInfo['countryCitizenshipCode'] == u'м112')

                            # включён фильтр "Граждане Украины" (код Украины 804, согласно ISO 4217, на 25.09.2014)
                            or (filterList[7] and not filterList[6] and clientInfo['countryCitizenshipCode'] == u'м804')

                            # включёны оба фильтра "Граждане Белоруссии" и "Граждане Украины"
                            or (filterList[6] and filterList[7] and clientInfo['countryCitizenshipCode'] in [u'м112', u'м804'])
                    ):
                        continue


                row = table.addRow()
                table.setText(row, 0, row)
                table.setText(row, 1, item.get('externalId', u'')) # № ИБ
                table.setText(row, 2, forceString(db.translate('OrgStructure', 'id', action[u'Направлен в отделение'], 'code'))) # код отделения
                # Дата и время поступления\nи отправки пациента.\nТип госпитализации.
                table.setText(row, 3, forceString(item.get('begDate', u'')))

                table.setText(row, 4, item.get('clientName', u'')) # Фамилия Имя Отчество
                table.setText(row, 5, forceString(item.get('birthDateRaw', u''))) # Возраст
                table.setText(row, 6, forceString(item.get('age', u''))) # Дата рождения
                table.setText(row, 7, item.get('sex', u'')) # Пол
                # Домашний адрес (адрес регистрации), Место работы, должность
                table.setText(row, 8, u'%s (%s) %s' % (clientInfo['locAddress'],
                                                       clientInfo['regAddress'] or u'---',
                                                       clientInfo['work']))
                # Гражданство
                if clientInfo['countryCitizenshipCode']:
                    table.setText(row, 9, forceString(db.translate('rbSocStatusType', 'code', clientInfo['countryCitizenshipCode'], 'name')))
                # Диагноз направившего учреждения
                table.setText(row, 10, forceString(action[u'Диагноз направителя']))
                # Дата выписки
                table.setText(row, 11, forceString(item.get('endDate', u'')))


            view = CReportViewDialog(self)
            view.setText(doc)
            view.exec_()
        except:
            QtGui.qApp.logCurrentException()

    def getContextData(self):
        context = CInfoContext()
        orgStructureId = self.modelOrgStructure.itemId(self.treeOrgStructure.currentIndex())
        events = []
        for item in self.modelPresence.items:
            event = context.getInstance(CHospitalEventInfo, item.get('eventId', 0))
            event._action = context.getInstance(CActionInfo, item.get('actionId', 0))
            event._finance = item.get('nameFinance', '')
            event._hasFeed = item.get('feed', False)
            event._feed = forceString(item['feedTextValueItem'])
            event._bedCode = item.get('codeBed', '')
            events = events + [event, ]
        data = { 'events' : events,
                 'orgStructure': context.getInstance(COrgStructureInfo, orgStructureId)
        }
        return data



    @QtCore.pyqtSlot()
    def on_actPrintThermalSheet_triggered(self):
        # widgetIndex == 1
        data = self.getContextData()
        applyTemplateInt(self, u"Присутствующие на отделении", temperatureList_html.CONTENT, data, templateType=htmlTemplate)


    @QtCore.pyqtSlot()
    def on_actPrintJournal_triggered(self):
        self.getStationaryReportF001()

    @QtCore.pyqtSlot()
    def on_actPrintLogbookHospitalization_triggered(self):
        self.getLogbookHospitalization()


    @QtCore.pyqtSlot()
    def on_actReportLeaved_triggered(self):
        self.getReportLeaved()


    @QtCore.pyqtSlot()
    def on_btnLeaved_clicked(self):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == self.tabWidget.indexOf(self.tabPresence):
            self.btnLeavedEvent = True
            self.on_actOpenEvent_triggered()

    @QtCore.pyqtSlot()
    def on_btnRadialSheet_clicked(self):
        personId = self.cmbPerson.value()
        personName = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
        dialog = CRadialSheetSetupDialog(self,  personName)
        dialog.exec_()

    # Логика как у `on_btnHospitalization_clicked`
    @QtCore.pyqtSlot()
    def on_btnCreateEvent_clicked(self):
        widgetIndex = self.tabWidget.currentIndex()
        eventId = self.getCurrentEventId(widgetIndex)
        clientId=forceRef(QtGui.qApp.db.translateEx('Event', 'id', eventId, 'client_id'))
        if clientId:
            actionId = None
            begDate = None
            endDate = None
            execDate = None
            if eventId:
                if widgetIndex == self.tabWidget.indexOf(self.tabQueue):
                    actionId, orgStructureId, bedId, begDate, endDate, execDate, personId, form = self.getDataQueueEvent(eventId)
            if clientId:
                newEventId = requestNewEvent(self, clientId)
                # if newEventId:
                #     if widgetIndex == self.tabWidget.indexOf(self.tabQueue) and actionId:
                #         self.editReceivedQueueEvent(actionId, begDate, endDate, execDate)
        else:
            HospitalizationEvent = CHospitalizationEventDialog(
                self,
                widgetIndex == self.tabWidget.indexOf(self.tabQueue),
                clientId,
                eventId,
                otherType=True
            )
            HospitalizationEvent.btnCommit.setText(u'Создать обращение (Пробел)')
            HospitalizationEvent.setWindowTitle(u'Новое обращение')
            HospitalizationEvent.exec_()

    @QtCore.pyqtSlot()
    def on_btnHospitalization_clicked(self):
        clientId = None
        eventId = None
        personId = None
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex in (self.tabWidget.indexOf(self.tabQueue), self.tabWidget.indexOf(self.tabLobby)):
            model = self.modelQueue if widgetIndex == self.tabWidget.indexOf(self.tabQueue) else self.modelLobby
            index = self.tblQueue.currentIndex() if widgetIndex == self.tabWidget.indexOf(self.tabQueue) else self.tblLobby.currentIndex()
            row = index.row()
            if row >= 0:
                clientId = model.items[row].get('clientId', 0)
                eventId = model.items[row].get('eventId', 0)
                personId = model.items[row].get('personId', 0)
        if clientId:
            # newEventId = None
            actionId = None
            bedId = None
            orgStructureId = None
            begDate = None
            endDate = None
            execDate = None
            actionTypeIdValue = None
            flagHospitalization = True
            financeId = None
            protocolQuoteId = None
            planningHospitalEventId = None
            if eventId:
                if widgetIndex == self.tabWidget.indexOf(self.tabQueue):
                    actionId, orgStructureId, bedId, begDate, endDate, execDate, personId, form = self.getDataQueueEvent(eventId)
                    planningHospitalEventId = eventId
                    financeId = self.getPlanningFinanceId(eventId)
                    # if form == '027':
                    #     protocolQuoteId = self.getProtocolQuote(eventId)
            if clientId:
                # self.selectHospitalizationEventCode(clientId)
                eventTypeFilterHospitalization = '(EventType.medicalAidType_id IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'1\', \'2\', \'3\', \'7\', \'10\')))'
                diagnos = self.getDiagnosString(eventId)
                newEventId = requestNewEvent(self, clientId, flagHospitalization, actionTypeIdValue, [orgStructureId, bedId], eventTypeFilterHospitalization, None, personId, planningHospitalEventId, diagnos, financeId, protocolQuoteId)
                if newEventId:
                    # Раньше использовалось только на вкладке "В очереди", сейчас - пока не решено, как должно быть.
                    # if self.flagPlanningHospital and actionId:
                    if widgetIndex == self.tabWidget.indexOf(self.tabQueue) and actionId:
                        self.editReceivedQueueEvent(actionId, begDate, endDate, execDate)
                        self.on_selectionModelOrgStructure_currentChanged(None, None)
        else:
            HospitalizationEvent = CHospitalizationEventDialog(self, widgetIndex == self.tabWidget.indexOf(self.tabQueue), clientId, eventId)
            HospitalizationEvent.exec_()
            newEventId = HospitalizationEvent.newEventId
            if newEventId and widgetIndex == self.tabWidget.indexOf(self.tabQueue):
                self.on_selectionModelOrgStructure_currentChanged(None, None)

        # i4151
        # if newEventId:
        #     self.on_selectionModelOrgStructure_currentChanged(None, None)
        #     self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabReceived))
        #     self.tblReceived.setFocus(QtCore.Qt.OtherFocusReason)
        #     countRow = self.modelReceived.rowCount()
        #     row = -1
        #     while row != (countRow - 1):
        #         row += 1
        #         if newEventId == self.modelReceived.items[row].get('eventId', 0):
        #             self.tblReceived.setCurrentRow(row)
        #             break


    # Следующие функции полностью дублируют аналоги в HospitalizationEventDialog.py
    # Если требования к задаче не изменятся, нужно сделать их независимыми от класса.
    @staticmethod
    def editReceivedQueueEvent(actionId, begDate, endDate, execDate):
        if actionId:
            currentDateTime = QtCore.QDateTime.currentDateTime()
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            if not endDate:
                db.updateRecords(tableAction.name(), tableAction['endDate'].eq(currentDateTime), [tableAction['id'].eq(actionId), tableAction['deleted'].eq(0)])
                if not begDate:
                    db.updateRecords(tableAction.name(), tableAction['begDate'].eq(currentDateTime), [tableAction['id'].eq(actionId), tableAction['deleted'].eq(0)])
            db.updateRecords(tableAction.name(), tableAction['status'].eq(2), [tableAction['id'].eq(actionId), tableAction['deleted'].eq(0)])

    def getPlanningFinanceId(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableActionPRBF = db.table('ActionProperty_rbFinance')
            tableActionProperty = db.table('ActionProperty')
            tableAPT = db.table('ActionPropertyType')
            table = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            table = table.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableActionProperty, tableActionProperty['type_id'].eq(tableAPT['id']))
            table = table.innerJoin(tableActionPRBF, tableActionPRBF['id'].eq(tableActionProperty['id']))
            cols = [tableActionPRBF['value']]
            cond = [tableEvent['id'].eq(eventId),
                    tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(u'planning%')),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableAction['id'].isNotNull(),
                    tableActionType['deleted'].eq(0),
                    tableAPT['deleted'].eq(0),
                    tableAPT['deleted'].like(u'источник финансирования'),
                    tableActionProperty['deleted'].eq(0),
                    tableActionProperty['action_id'].eq(tableAction['id'])
            ]
            record = db.getRecordEx(table, cols, cond, 'Action.id DESC')
            return forceRef(record.value('value')) if record else None
        return None

    def getDiagnosString(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            table = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            cols = [tableActionType['flatCode']]
            cols.append('''(SELECT APS.value
                            FROM ActionPropertyType AS APT
                            INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
                            INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
                            WHERE  Action.id IS NOT NULL AND APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND APT.name LIKE '%s') AS diagnos'''%(u'Диагноз'))
            cond = [tableEvent['id'].eq(eventId),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableActionType['deleted'].eq(0)
            ]
            records = db.getRecordList(table, cols, cond, 'Action.endDate DESC')
            for record in records:
                diagnos = forceString(record.value('diagnos'))
                flatCode = forceString(record.value('flatCode'))
                if u'protocol' in flatCode.lower():
                    return diagnos
            for record in records:
                diagnos = forceString(record.value('diagnos'))
                if diagnos:
                    return diagnos
        return None

    def getDataQueueEvent(self, eventId = None):
        if eventId:
            currentDateTime = QtCore.QDateTime.currentDateTime()
            db = QtGui.qApp.db
            tableAPHB = db.table('ActionProperty_HospitalBed')
            tableAPT = db.table('ActionPropertyType')
            tableAP = db.table('ActionProperty')
            tableActionType = db.table('ActionType')
            tableAction = db.table('Action')
            tableOSHB = db.table('OrgStructure_HospitalBed')
            tableOS = db.table('OrgStructure')
            tableEvent = db.table('Event')
            tableEventType = db.table('EventType')
            tableAPOS = db.table('ActionProperty_OrgStructure')
            cols = [tableAction['id'],
                    tableAction['begDate'],
                    tableAction['endDate'],
                    tableAction['person_id'],
                    tableEvent['execDate'],
                    tableEventType['form'],
                    tableOSHB['id'].alias('bedId')
            ]
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            cond = [tableActionType['flatCode'].like('planning'),
                    tableAction['deleted'].eq(0),
                    tableAP['deleted'].eq(0),
                    tableActionType['deleted'].eq(0),
                    tableOS['deleted'].eq(0),
                    tableEvent['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableAction['event_id'].eq(eventId),
                    tableAPT['typeName'].like('HospitalBed'),
                    tableAP['action_id'].eq(tableAction['id'])
            ]
            records = db.getRecordList(queryTable, cols, cond)
            orgStructureId = None
            begDate = None
            endDate = None
            actionId = None
            bedId = None
            execDate = None
            personId = None
            form = ''
            for record in records:
                actionId = forceRef(record.value('id'))
                bedId = forceRef(record.value('bedId'))
                begDate = forceDate(record.value('begDate'))
                endDate = forceDate(record.value('endDate'))
                execDate = forceDate(record.value('execDate'))
                personId = forceRef(record.value('person_id'))
                form     = forceString(record.value('form'))

            cols = [tableAction['id'],
                    tableAction['begDate'],
                    tableAction['endDate'],
                    tableAction['person_id'],
                    tableEvent['execDate'],
                    tableEventType['form'],
                    tableOS['id'].alias('orgStructureId')
            ]
            cond = [tableActionType['flatCode'].like(u'planning%'),
                    tableAction['deleted'].eq(0),
                    tableEvent['deleted'].eq(0),
                    tableAction['event_id'].eq(eventId),
                    tableActionType['deleted'].eq(0),
                    tableAPT['deleted'].eq(0),
                    tableOS['deleted'].eq(0),
                    tableAP['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableAP['action_id'].eq(tableAction['id']),
                    tableAPT['typeName'].like('OrgStructure')
            ]
            queryNoBed = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryNoBed = queryNoBed.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryNoBed = queryNoBed.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
            queryNoBed = queryNoBed.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryNoBed = queryNoBed.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryNoBed = queryNoBed.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
            queryNoBed = queryNoBed.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
            recordsNoBed = db.getRecordList(queryNoBed, cols, cond)
            for recordNoBed in recordsNoBed:
                actionId = forceRef(recordNoBed.value('id'))
                orgStructureId = forceRef(recordNoBed.value('orgStructureId'))
                begDate = forceDate(recordNoBed.value('begDate'))
                endDate = forceDate(recordNoBed.value('endDate'))
                execDate = forceDate(recordNoBed.value('execDate'))
                personId = forceRef(recordNoBed.value('person_id'))
                form     = forceString(recordNoBed.value('form'))
        return actionId, orgStructureId, bedId, begDate, endDate, execDate, personId, form

    def getProtocolQuote(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableActionCQ = db.table('ActionProperty_Client_Quoting')
            tableActionProperty = db.table('ActionProperty')
            tableAPT = db.table('ActionPropertyType')
            table = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            table = table.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableActionProperty, tableActionProperty['type_id'].eq(tableAPT['id']))
            table = table.innerJoin(tableActionCQ, tableActionCQ['id'].eq(tableActionProperty['id']))
            cols = [tableActionCQ['value']]
            cond = [tableEvent['id'].eq(eventId),
                    tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(u'protocol%')),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableAction['id'].isNotNull(),
                    tableActionType['deleted'].eq(0),
                    tableAPT['deleted'].eq(0),
                    tableAPT['name'].like(u'Квота'),
                    tableActionProperty['deleted'].eq(0),
                    tableActionProperty['action_id'].eq(tableAction['id'])
            ]
            record = db.getRecordEx(table, cols, cond, 'Action.id DESC')
            return forceRef(record.value('value')) if record else None
        return None
    ### Конец дублирующихся функций

    @QtCore.pyqtSlot()
    def on_actTemperatureListEditor_triggered(self):
        index = self.tblPresence.currentIndex()
        if index.isValid():
            row = index.row()
            eventId = self.modelPresence.items[row].get('eventId', 0) if row >= 0 else None
            actionTypeIdList = getActionTypeIdListByFlatCode(u'temperatureSheet%')
            clientId = self.modelPresence.items[row].get('clientId', 0)
            if eventId and actionTypeIdList and clientId:
                db = QtGui.qApp.db
                tableClient = db.table('Client')
                tableEvent = db.table('Event')
                clientRecord = db.getRecordEx(tableClient, [tableClient['sex'], tableClient['birthDate']], [tableClient['id'].eq(clientId), tableClient['deleted'].eq(0)])
                clientSex = forceInt(clientRecord.value('sex'))
                clientAge = calcAge(forceDate(clientRecord.value('birthDate')), QtCore.QDate.currentDate())
                setDateRecord = db.getRecordEx(tableEvent, [tableEvent['setDate']], [tableEvent['id'].eq(eventId), tableEvent['deleted'].eq(0)])
                setDate = forceDateTime(setDateRecord.value('setDate')) if setDateRecord else None
                dialog = CTemperatureListEditorDialog(self, clientId, eventId, actionTypeIdList, clientSex, clientAge, setDate)
                if dialog.exec_():
                    if dialog.action:
                        dialog.action.save()


    @QtCore.pyqtSlot()
    def on_actGetFeedFromMenu_triggered(self):
        index = self.tblPresence.currentIndex()
        row = index.row()
        eventId = self.modelPresence.items[row].get('eventId', 0) if row >= 0 else None
        if eventId and self.lockList('Event', [eventId]):
            try:
                eventIdList = []
                eventIdList.append([eventId, self.modelPresence.items[row].get('begDate', None) if row >= 0 else None, self.modelPresence.items[row].get('plannedEndDate', None) if row >= 0 else None, self.modelPresence.items[row].get('ebdDate', 0) if row >= 0 else None])
                self.getFeedFromMenu(eventIdList)
            finally:
                self.releaseLockList()

    def getFeedFromMenu(self, eventIdList):
        if eventIdList:
            dialog = CGetRBMenu(self)
            menuId = dialog.exec_()
            if menuId:
                for eventData in eventIdList:
                    eventId = eventData[0] if eventData else None
                    if eventId:
                        db = QtGui.qApp.db
                        tableEvent = db.table('Event')
                        tableEventType = db.table('EventType')
                        table = tableEvent.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
                        eventTypeRecord = db.getRecordEx(table, tableEventType['id'], [tableEvent['id'].eq(eventId), tableEventType['form'].like('003')])
                        if eventTypeRecord and forceRef(eventTypeRecord.value('id')):
                            begDatePresence = eventData[1] if len(eventData) >= 2 else None
                            plannedEndDatePresence = eventData[2] if len(eventData) >= 3 else None
                            endDatePresence = eventData[3] if len(eventData) >= 4 else None
                            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                            try:
                                begDate = dialog.edtBegDate.date()
                                endDate = dialog.edtEndDate.date()
                                if begDate and endDate and begDate <= endDate:
                                    if begDatePresence and begDate < begDatePresence.date():
                                        begDate = begDatePresence.date()
                                    if endDatePresence and endDate > endDatePresence.date():
                                        endDate = endDatePresence.date()
                                    if (not plannedEndDatePresence or begDate < plannedEndDatePresence) and (not begDatePresence or begDate >= begDatePresence.date()) and (not endDatePresence or endDate <= endDatePresence.date()):
                                        modelFeed = CFeedModel(self)
                                        modelFeed.loadHeader()
                                        modelFeed.loadData(eventId)
                                        modelFeed.insertFromMenu(menuId, begDate, endDate, dialog.chkUpdate.isChecked())
                                        modelFeed.saveData(eventId)
                                        self.modelPresence.reset()
                                        self.on_selectionModelOrgStructure_currentChanged(None, None)
                            finally:
                                QtGui.QApplication.restoreOverrideCursor()


    def saveFeedFromMenu(self, masterId, records):
        # TODO и тут
        if (records is not None) and masterId:
            db = QtGui.qApp.db
            table = db.table('Event_Feed')
            masterId = toVariant(masterId)
            idList = []
            for record in records:
                if forceDate(record.value('date')) and forceRef(record.value('diet_id')):
                    record.setValue('event_id', masterId)
                    eventFeedId = db.insertOrUpdate(table, record)
                    record.setValue('id', toVariant(eventFeedId))
                    idList.append(eventFeedId)
            filters = [table['event_id'].eq(masterId),
                       'NOT ('+table['id'].inlist(idList)+')']
            db.deleteRecord(table, filters)


    def getOrgStructureId(self, treeIndex):
        #        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        #        return treeItem._id if treeItem else None
        if treeIndex:
            return treeIndex.model().itemId(treeIndex)
        return None


    def dumpParams(self, cursor):
        sexList = [u'не определено', u'мужской', u'женский']
        db = QtGui.qApp.db
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result
        description = []
        begDate = self.edtFilterBegDate.date()
        endDate = self.edtFilterEndDate.date()
        if self.filterByExactTime:
            begDate = QtCore.QDateTime(begDate, self.edtFilterBegTime.time())
            endDate = QtCore.QDateTime(endDate, self.edtFilterEndTime.time())
        currentIndexOS = self.treeOrgStructure.currentIndex()
        sexIndex = self.cmbSex.currentIndex()
        ageFor = self.spbAgeFrom.value()
        ageTo = self.spbAgeTo.value()
        if begDate or endDate:
            description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if currentIndexOS:
            orgStructureId = self.getOrgStructureId(currentIndexOS)
            if orgStructureId:
                description.append(u'подразделение ' + forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name')))
            else:
                description.append(u'ЛПУ')
        if sexIndex:
            description.append(u'пол ' + sexList[sexIndex])
        if ageFor or ageTo:
            description.append(u'возраст' + u' с '+forceString(ageFor) + u' по '+forceString(ageTo))
        personId = self.cmbPerson.value()
        if personId:
            personName = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            description.append(u'Врач ' + personName)
        if self.cmbAssistant.isEnabled() and self.chkAssistant.isChecked():
            assistantId = self.cmbAssistant.value()
            if assistantId:
                assistantName = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', assistantId, 'name'))
                description.append(u'Ассистент ' + assistantName)
            else:
                description.append(u'Ассистент ' + u'не указан')
        typeId = self.cmbFilterType.value()
        if typeId:
            typeId = self.cmbFilterType.currentText()
            description.append(u'Тип койки ' + forceString(typeId))
        profile = self.cmbFilterProfile.value()
        if profile:
            profile = self.cmbFilterProfile.currentText()
            description.append(u'Профиль койки ' + forceString(profile))
        sexIndexBed = self.cmbSexBed.currentIndex()
        if sexIndexBed:
            description.append(u'Пол койки ' + sexList[sexIndexBed])
        codeFinance = self.cmbFinance.value()
        if codeFinance:
            codeFinance = self.cmbFinance.currentText()
            description.append(u'Источник финансирования ' + forceString(codeFinance))
        currentClass = self.cmbQuotingType.currentClass()
        quotingTypeId = self.cmbQuotingType.value()
        if quotingTypeId or currentClass != None:
            if not quotingTypeId:
                description.append(u'Квотирование: класс - ' + [u'ВТМП', u'СМП'][currentClass])
            else:
                nameQuotaType = forceString(QtGui.qApp.db.translate('QuotaType', 'id', quotingTypeId, 'name'))
                description.append(u'Квотирование: ' + nameQuotaType)
        if self.cmbFeed.isEnabled():
            feed = self.cmbFeed.currentIndex()
            if feed:
                dateFeed = self.edtDateFeed.date()
                description.append(u'Питание: ' + [u'не учитывать', u'не назначено', u'назначено'][feed] + u' на дату ' + dateFeed.toString('dd.MM.yyyy'))
        if self.chkAttachType.isChecked() and self.cmbAttachType.isEnabled():
            description.append(u'Прикрепление пациента: ' + forceString(self.cmbAttachType.currentText()))
        if self.cmbLocationClient.isEnabled():
            description.append(u'Размещение пациента: ' + forceString(self.cmbLocationClient.currentText()))
        if self.edtPresenceDayValue.isEnabled():
            presenceDayValue = self.edtPresenceDayValue.value()
            if presenceDayValue:
                description.append(self.lblPresenceDay.text() + u': ' + forceString(presenceDayValue))
        if self.cmbReceived.isEnabled():
            received = self.cmbReceived.currentIndex()
            description.append(self.lblReceived.text() + u': ' + [u'в ЛПУ', u'в отделение', u'в приемное отделение'][received])
        if self.cmbTransfer.isEnabled():
            transfer = self.cmbTransfer.currentIndex()
            description.append(self.lblTransfer.text() + u': ' + [u'из отделения', u'в отделение'][transfer])
        if self.chkStayOrgStructure.isEnabled():
            description.append(u'с учетом "Отделения пребывания"')
        if self.cmbLeaved.isEnabled():
            leaved = self.cmbLeaved.currentIndex()
            description.append(self.lblLeaved.text() + u': ' + [u'из ЛПУ', u'без выписки', u'из отделений'][leaved])
        if self.cmbRenunciation.isEnabled():
            description.append(self.lblRenunciation.text() + u': ' + self.cmbRenunciation.text())
        if self.cmbHospitalizingOutcome.isEnabled():
            description.append(self.lblHospitalizingOutcome.text() + u': ' + self.cmbHospitalizingOutcome.text())
        if self.cmbRenunciationAction.isEnabled():
            renunciationAction = self.cmbRenunciationAction.currentIndex()
            description.append(self.lblRenunciationAction.text() + u': ' + [u'Госпитализации', u'Планировании'][renunciationAction])
        if self.cmbLocationCard.isEnabled():
            description.append(self.lblLocationCard.text() + u': ' + self.cmbLocationCard.currentText())

        description.append(u'отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    #TODO: mdldml: вынести в HospitalBedsReport
    def getReportLeaved(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сводка по выписке')
        cursor.insertBlock()
        self.dumpParams(cursor)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('5%',[u'№'], CReportBase.AlignRight),
                ('10%', [u'№ истории болезни'], CReportBase.AlignLeft),
                ('20%', [u'ФИО пациента'], CReportBase.AlignLeft),
                ('15%', [u'Отделение'], CReportBase.AlignLeft),
                ('15%', [u'Дата госпитализации'], CReportBase.AlignLeft),
                ('10%', [u'Дата выписки'], CReportBase.AlignLeft),
                ('10%' , [u'Диагноз'], CReportBase.AlignLeft),
                ('15%', [u'Ответственный'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, cols)
        cnt = 0
        items = self.modelLeaved.items
        for item in items:
            i = table.addRow()
            cnt += 1
            table.setText(i, 0, cnt)
            table.setText(i, 1, item.get('externalId', ''))
            table.setText(i, 2, item.get('clientName', ''))
            table.setText(i, 3, ((item.get('codeBed', '') + u' - ') if item.get('codeBed', '') else u'') + item.get('nameOS', ''))
            table.setText(i, 4, item.get('begDateReceived', ''))
            table.setText(i, 5, forceString(item.get('endDate', '')))
            table.setText(i, 6, forceString(item.get('MKB', '')))
            table.setText(i, 7, item.get('namePerson', ''))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)
        reportView = CReportViewOrientation(self, QtGui.QPrinter.Landscape)
        reportView.setWindowTitle(u'Сводка по выписке')
        reportView.setText(doc)
        reportView.exec_()

    #TODO: mdldml: вынести в HospitalBedsReport
    def getStationaryReportF001(self):
        orgStructureIndex = self.treeOrgStructure.currentIndex()
        begDate = self.edtFilterBegDate.date()
        endDate = self.edtFilterEndDate.date()
        begTime = self.edtFilterBegTime.time()
        endTime = self.edtFilterEndTime.time()
        changingDayTime = self.edtFilterEndTime.time()
        sexIndex = self.cmbSex.currentIndex()
        ageFor = self.spbAgeFrom.value()
        ageTo = self.spbAgeTo.value()

        report = CReportBase()
        params = report.getDefaultParams()
        setupDialog = CReportF001SetupDialog(self)
        setupDialog.setParams(params)
        if not setupDialog.exec_():
            return
        params = setupDialog.params()
        report.saveDefaultParams(params)
        chkClientId = params.get('chkClientId', False)
        chkEventId = params.get('chkEventId', False)
        chkExternalEventId = params.get('chkExternalEventId', False)
        chkPrintTypeEvent = params.get('chkPrintTypeEvent', False)
        condSort = params.get('condSort', 0)
        condOrgStructure = params.get('condOrgStructure', 0)
        printTypeMKB = params.get('printTypeMKB', 0)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Учет приема больных и отказов в госпитализации')
        cursor.insertBlock()
        self.dumpParams(cursor)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('2%',[u'№'], CReportBase.AlignRight),
                ('5%', [u'Поступление', u'дата'], CReportBase.AlignLeft),
                ('5%', [u'', u'час'], CReportBase.AlignLeft),
                ('7%', [u'Фамилия, И., О.'], CReportBase.AlignLeft),
                ('5%', [u'Дата рождения'], CReportBase.AlignLeft),
                ('12%', [u'Постоянное место жительства или адрес  родственников, близких и № телефона'], CReportBase.AlignLeft),
                ('7%', [u'Каким учреждением был направлен или доставлен'], CReportBase.AlignLeft),
                ('7%', [u'Отделение, в которое помещен больной'], CReportBase.AlignLeft),
                ('7%', [u'№ карты стационарного больного'], CReportBase.AlignLeft),
                ('7%', [u'Предварительный диагноз МКБ'], CReportBase.AlignLeft),
                ('5%', [u'Выписан, переведен в другой  стационар, умер'], CReportBase.AlignLeft),
                ('7%', [u'Отметка о сообщении родственникам или учреждению'], CReportBase.AlignLeft),
                ('7%', [u'Если не был госпитализирован', u'причина и принятые меры'], CReportBase.AlignLeft),
                ('7%', [u'', u'отказ в приеме первичный, повторный'], CReportBase.AlignLeft),
                ('5%', [u'Место работы'], CReportBase.AlignLeft),
                ('5%', [u'Примечание'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1) # №
        table.mergeCells(0, 1, 1, 2) # Поступление
        table.mergeCells(0, 3, 2, 1) # ФИО
        table.mergeCells(0, 4, 2, 1) # Дата рождения
        table.mergeCells(0, 5, 2, 1) # Адрес
        table.mergeCells(0, 6, 2, 1) # Учреждение кем доставлен
        table.mergeCells(0, 7, 2, 1) # Отделение
        table.mergeCells(0, 8, 2, 1) # Диагноз
        table.mergeCells(0, 9, 2, 1) # № карты
        table.mergeCells(0, 10, 2, 1) # Выписан
        table.mergeCells(0, 11, 2, 1) # Отметка о сообщении
        table.mergeCells(0, 12, 1, 2) # не был госпитализирован
        table.mergeCells(0, 13, 2, 1) # Примечание


        def queryProperty(flatCode, colsVal = u'', condVal = u'', flag = None, actionIdLeaved = None):
            colsClientId = []
            condClientId = [ tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(flatCode)),
                             tableAction['deleted'].eq(0),
                             tableEvent['deleted'].eq(0),
                             tableAP['deleted'].eq(0),
                             tableAPT['deleted'].eq(0),
                             tableClient['deleted'].eq(0),
                             tableAP['action_id'].eq(tableAction['id'])
            ]
            condClientId.append(tableAction['event_id'].eq(forceRef(records.value('eventId'))))
            condClientId.append(tableEvent['client_id'].eq(clientId))
            if flag != 3:
                if actionIdLeaved != None:
                    condClientId.append(tableAction['id'].eq(actionIdLeaved))
                else:
                    condClientId.append(tableAction['id'].eq(forceRef(records.value('id'))))
                condClientId.append(tableAPT['name'].like(condVal))
            queryTableClientId = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTableClientId = queryTableClientId.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTableClientId = queryTableClientId.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            queryTableClientId = queryTableClientId.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTableClientId = queryTableClientId.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            if flag == 0:
                queryTableClientId = queryTableClientId.innerJoin(tableAPO, tableAPO['id'].eq(tableAP['id']))
                queryTableClientId = queryTableClientId.innerJoin(tableOrg, tableOrg['id'].eq(tableAPO['value']))
                colsClientId.append(tableOrg['shortName'].alias(colsVal))
                condClientId.append(tableOrg['deleted'].eq(0))
            elif flag == 1:
                queryTableClientId = queryTableClientId.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
                queryTableClientId = queryTableClientId.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
                colsClientId.append(tableOS['code'].alias(colsVal) if condOrgStructure else tableOS['name'].alias(colsVal))
            elif flag == 3:
                colsClientId.append(tableAction['id'].alias('actionIdLeaved'))
                colsClientId.append(tableAction['begDate'].alias('begDateLeaved'))
                colsClientId.append(tableAction['note'].alias('noteLeaved'))
            else:
                queryTableClientId = queryTableClientId.innerJoin(tableAPS, tableAPS['id'].eq(tableAP['id']))
                colsClientId.append(tableAPS['value'].alias(colsVal))
            stmt = db.selectStmt(queryTableClientId, colsClientId, condClientId, isDistinct = True)
            return db.query(stmt)

        cnt = 0
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableAPS = db.table('ActionProperty_String')
        tableAPO = db.table('ActionProperty_Organisation')
        tableOrg = db.table('Organisation')
        tableAPOS = db.table('ActionProperty_OrgStructure')
        tableOS = db.table('OrgStructure')
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnostic = db.table('Diagnostic')
        tableRBDiagnosisType = db.table('rbDiagnosisType')
        cols = [tableAction['id'],
                tableEvent['id'].alias('eventId'),
                tableEvent['eventType_id'],
                tableEvent['client_id'],
                tableEvent['externalId'],
                tableClient['lastName'],
                tableClient['firstName'],
                tableClient['patrName'],
                tableClient['sex'],
                tableClient['birthDate'],
                tableAction['begDate'],
                tableAction['note'],
                tableAction['finance_id'],
                tableEvent['contract_id']
        ]
        queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
        cond = [ tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(u'received%')),
                 tableAction['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableAP['deleted'].eq(0),
                 tableAPT['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 tableAP['action_id'].eq(tableAction['id'])
        ]
        if begDate:
            begDateTime = QtCore.QDateTime(begDate, begTime if self.filterByExactTime else changingDayTime)
            cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].datetimeGe(begDateTime)]))
        if endDate:
            endDateTime = QtCore.QDateTime(endDate, endTime if self.filterByExactTime else changingDayTime)
            cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].datetimeLe(endDateTime)]))
        if sexIndex > 0:
            cond.append(tableClient['sex'].eq(sexIndex))
        if ageFor <= ageTo:
            cond.append(getAgeRangeCond(ageFor, ageTo))
        if orgStructureIndex:
            if self.getOrgStructureId(orgStructureIndex):
                orgStructureIdList = getOrgStructureIdList(orgStructureIndex)
                queryTable = queryTable.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
                queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
                cond.append(tableOS['id'].inlist(orgStructureIdList))
        stmt = db.selectStmt(queryTable,
                             cols,
                             cond,
                             order = [u'Client.lastName, Client.firstName, Client.patrName', u'Action.begDate', u'Client.id', u'Event.id', u'CAST(Event.externalId AS SIGNED)'][condSort],
                             isDistinct = True)
        query = db.query(stmt)
        while query.next():
            records = query.record()
            clientId = forceRef(records.value('client_id'))
            eventId = forceRef(records.value('eventId'))
            begDate = forceDate(records.value('begDate'))
            begTime = forceTime(records.value('begDate'))
            note = forceString(records.value('note'))
            contractId = forceRef(records.value('contract_id'))
            financeId = forceRef(records.value('finance_id'))
            noteText = u''
            if note != u'':
                noteText = note + u'. '
            if clientId:
                clientInfo = getClientInfoEx(clientId)
                adress = u''
                if clientInfo['regAddress']:
                    adress = u'регистрация: ' + clientInfo['regAddress']
                if clientInfo['locAddress']:
                    adress += u', проживание: ' + clientInfo['locAddress']
                if clientInfo['phones']:
                    adress += u', телефон: ' + clientInfo['phones']
                i = table.addRow()
                cnt += 1
                table.setText(i, 0, cnt)
                table.setText(i, 1, begDate.toString('dd.MM.yyyy'))
                table.setText(i, 2, begTime.toString('hh:mm:ss'))
                table.setText(i, 3, clientInfo['fullName'])
                table.setText(i, 4, clientInfo['birthDate'] + u'(' + clientInfo['age'] + u')')
                table.setText(i, 5, adress)
                table.setText(i, 14, clientInfo['work'])
                numberCardStr = u''
                numberCardList = []
                if chkClientId:
                    numberCardList.append(clientId)
                if chkEventId:
                    numberCardList.append(forceRef(records.value('eventId')))
                if chkExternalEventId:
                    numberCardList.append(forceString(records.value('externalId')))
                #numberCardList.sort()
                numberCardStr = u','.join(forceString(numberCard) for numberCard in numberCardList if numberCard)
                table.setText(i, 8, numberCardStr)
                whoDirecting = u''
                queryClientId = queryProperty(u'received%', u'whoDirecting', u'Кем направлен%', 0)
                if queryClientId.first():
                    record = queryClientId.record()
                    whoDirecting = u'Направлен: ' + forceString(record.value('whoDirecting')) + u' '
                queryClientId = queryProperty(u'received%', u'whoDelivered', u'Кем доставлен%')
                if queryClientId.first():
                    record = queryClientId.record()
                    whoDirecting += u'Доставлен: ' + forceString(record.value('whoDelivered'))
                table.setText(i, 6, whoDirecting)
                nameOSTypeEventList = []
                queryClientId = queryProperty(u'received%', u'orgStructure', u'Направлен в отделение%', 1)
                if queryClientId.first():
                    record = queryClientId.record()
                    nameOSTypeEventList.append(forceString(record.value('orgStructure')))
                if chkPrintTypeEvent:
                    tableRBFinance = db.table('rbFinance')
                    if financeId:
                        recordFinance = db.getRecordEx(tableRBFinance, [tableRBFinance['name']], [tableRBFinance['id'].eq(financeId)])
                        nameOSTypeEventList.append(u'\n' + forceString(recordFinance.value('name')) if recordFinance else '')
                    else:
                        if contractId:
                            tableContract = db.table('Contract')
                            tableFinanceQuery = tableContract.innerJoin(tableRBFinance, tableContract['finance_id'].eq(tableRBFinance['id']))
                            recordFinance = db.getRecordEx(tableFinanceQuery, [tableRBFinance['name']], [tableContract['id'].eq(contractId), tableContract['deleted'].eq(0)])
                            nameOSTypeEventList.append(u'\n' + forceString(recordFinance.value('name')) if recordFinance else '')
                table.setText(i, 7, u'; '.join(nameOSTypeEvent for nameOSTypeEvent in nameOSTypeEventList if nameOSTypeEvent))
                diagnosisList = []
                if printTypeMKB == 1 or printTypeMKB == 2:
                    queryTableMKB = tableEvent.innerJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
                    queryTableMKB = queryTableMKB.innerJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
                    queryTableMKB = queryTableMKB.innerJoin(tableRBDiagnosisType, tableDiagnostic['diagnosisType_id'].eq(tableRBDiagnosisType['id']))
                    condMKB = [tableEvent['deleted'].eq(0),
                               tableEvent['id'].eq(eventId),
                               tableDiagnosis['deleted'].eq(0),
                               tableDiagnostic['deleted'].eq(0),
                               tableRBDiagnosisType['code'].eq(7)
                    ]
                    stmt = db.selectStmt(queryTableMKB, u'Diagnosis.MKB', condMKB, isDistinct = True)
                    queryClientId = db.query(stmt)
                    while queryClientId.next():
                        record = queryClientId.record()
                        diagnosisList.append(forceString(record.value('MKB')))
                if printTypeMKB == 0 or printTypeMKB == 2:
                    queryClientId = queryProperty(u'received%', u'diagnosis', u'Диагноз направителя%')
                    while queryClientId.next():
                        record = queryClientId.record()
                        diagnosisList.append(forceString(record.value('diagnosis')))
                table.setText(i, 9, u', '.join(diagnos for diagnos in diagnosisList if diagnos))
                queryClientId = queryProperty(u'received%', u'nameRenuncReason', u'Причина отказа%')
                nameRenunciate = u''
                if queryClientId.first():
                    record = queryClientId.record()
                    nameRenunciate = u'Причина: ' + forceString(record.value('nameRenuncReason')) + u' '
                queryClientId = queryProperty(u'received%', u'nameRenuncMeasure', u'Принятые меры при отказе%')
                if queryClientId.first():
                    record = queryClientId.record()
                    nameRenunciate += u'Меры: ' + forceString(record.value('nameRenuncMeasure'))
                table.setText(i, 12, nameRenunciate)
                queryClientId = queryProperty(u'received%', u'refusal', u'Отказ в приеме%')
                if queryClientId.first():
                    record = queryClientId.record()
                    table.setText(i, 13, forceString(record.value('refusal')))
                queryClientId = queryProperty(u'leaved%', u'', u'', 3)
                if queryClientId.first():
                    record = queryClientId.record()
                    actionIdLeaved = forceRef(record.value('actionIdLeaved'))
                    noteText += forceString(record.value('noteLeaved'))
                    if actionIdLeaved:
                        result = u''
                        queryClientId = queryProperty(u'leaved%', u'resultHaspital', u'Исход госпитализации%', None, actionIdLeaved)
                        if queryClientId.first():
                            record = queryClientId.record()
                            resultHaspital = forceString(record.value('resultHaspital'))
                            result = resultHaspital + u' '
                            begDateLeaved = forceDate(record.value('begDateLeaved'))
                            if begDateLeaved:
                                result += begDateLeaved.toString('dd.MM.yyyy') + u' '
                        queryClientId = queryProperty(u'leaved%', u'transferOrganisation', u'Переведен в стационар%', None, actionIdLeaved)
                        if queryClientId.first():
                            record = queryClientId.record()
                            transferOrganisation = forceString(record.value('transferOrganisation'))
                            result += u'Перевод: ' + transferOrganisation
                        table.setText(i, 10, result)
                        queryClientId = queryProperty(u'leaved%', u'messageRelative', u'Сообщение родственникам%', None, actionIdLeaved)
                        if queryClientId.first():
                            record = queryClientId.record()
                            table.setText(i, 11, forceString(record.value('messageRelative')))
                table.setText(i, 15, noteText)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)
        reportView = CReportViewOrientation(self, QtGui.QPrinter.Landscape)
        reportView.setWindowTitle(u'Журнал')
        reportView.setText(doc)
        reportView.exec_()

    #TODO: mdldml: вынести в HospitalBedsReport
    def getLogbookHospitalization(self):
        orgStructureIndex = self.treeOrgStructure.currentIndex()
        begDate = self.edtFilterBegDate.date()
        endDate = self.edtFilterEndDate.date()
        changingDayTime = self.edtFilterEndTime.time()
        sexIndex = self.cmbSex.currentIndex()
        ageFor = self.spbAgeFrom.value()
        ageTo = self.spbAgeTo.value()

        report = CReportBase()
        params = report.getDefaultParams()
        setupDialog = CReportLogbookHospitalizationSetupDialog(self)
        setupDialog.setParams(params)
        if not setupDialog.exec_():
            return
        params = setupDialog.params()
        report.saveDefaultParams(params)
        diapFrom = forceString(params.get('edtDiapFrom', ''))
        diapTo = forceString(params.get('edtDiapTo', ''))
        prefix = forceString(params.get('edtPrefix', ''))
        contractIdList = params.get('contractIdList', None)
        resultId = params.get('cmbResult', None)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Журнал учёта госпитализации')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        if diapFrom or diapTo:
            cursor.insertText(u'Диапазон номеров истории болезни:')
            cursor.insertBlock()
            if diapFrom:
                cursor.insertText(u'от ' + diapFrom + ' ')
            if diapTo:
                cursor.insertText(u'до ' + diapTo)
            cursor.insertBlock()
        cursor.insertBlock()
        cols = [('5%', [u'№ записи'], CReportBase.AlignCenter),
                ('5%', [u'№ истории болезни'], CReportBase.AlignRight),
                ('5%', [u'Результат'], CReportBase.AlignLeft),
                ('5%', [u'Договор'], CReportBase.AlignLeft),
                ('8%', [u'Дата, время поступления'], CReportBase.AlignLeft),
                ('13%', [u'Фамилия Имя Отчество'], CReportBase.AlignLeft),
                ('8%', [u'Дата рождения, возраст'], CReportBase.AlignLeft),
                ('23%', [u'Домашний адрес проживания, место работы, должность'], CReportBase.AlignLeft),
                ('5%', [u'Кем направлен, доставлен'], CReportBase.AlignLeft),
                ('5%', [u'Отделение'], CReportBase.AlignLeft),
                ('10%', [u'Диагноз направившего учреждения'], CReportBase.AlignLeft),
                ('10%', [u'Диагноз приёмного отделения'], CReportBase.AlignLeft),
                ('8%', [u'Профиль'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, cols)

        def queryProperty(flatCode, colsVal = u'', condVal = u'', flag = None, actionIdLeaved = None):
            colsClientId = []
            condClientId = [ tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(flatCode)),
                             tableAction['deleted'].eq(0),
                             tableEvent['deleted'].eq(0),
                             tableAP['deleted'].eq(0),
                             tableAPT['deleted'].eq(0),
                             tableClient['deleted'].eq(0),
                             tableAP['action_id'].eq(tableAction['id'])
            ]
            condClientId.append(tableAction['event_id'].eq(forceRef(records.value('eventId'))))
            condClientId.append(tableEvent['client_id'].eq(clientId))
            if flag != 3:
                if actionIdLeaved != None:
                    condClientId.append(tableAction['id'].eq(actionIdLeaved))
                else:
                    condClientId.append(tableAction['id'].eq(forceRef(records.value('id'))))
                condClientId.append(tableAPT['name'].like(condVal))
            queryTableClientId = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTableClientId = queryTableClientId.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTableClientId = queryTableClientId.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            queryTableClientId = queryTableClientId.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTableClientId = queryTableClientId.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            if flag == 0:
                queryTableClientId = queryTableClientId.innerJoin(tableAPO, tableAPO['id'].eq(tableAP['id']))
                queryTableClientId = queryTableClientId.innerJoin(tableOrg, tableOrg['id'].eq(tableAPO['value']))
                colsClientId.append(tableOrg['infisCode'].alias(colsVal))
                condClientId.append(tableOrg['deleted'].eq(0))
            elif flag == 1:
                queryTableClientId = queryTableClientId.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
                queryTableClientId = queryTableClientId.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
                colsClientId.append(tableOS['code'].alias(colsVal))
            elif flag == 3:
                colsClientId.append(tableAction['id'].alias('actionIdLeaved'))
                colsClientId.append(tableAction['begDate'].alias('begDateLeaved'))
                colsClientId.append(tableAction['note'].alias('noteLeaved'))
            else:
                queryTableClientId = queryTableClientId.innerJoin(tableAPS, tableAPS['id'].eq(tableAP['id']))
                colsClientId.append(tableAPS['value'].alias(colsVal))
            stmt = db.selectStmt(queryTableClientId, colsClientId, condClientId, isDistinct = True)
            return db.query(stmt)

        def queryPropertyString(actionId, actionPropertyName):
            queryTable = tableAP
            queryTable = queryTable.innerJoin(tableAPS, tableAP['id'].eq(tableAPS['id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAP['type_id'].eq(tableAPT['id']))
            stmt = db.selectStmt(queryTable, tableAPS['value'], '''ActionProperty.`action_id` = %s AND ActionPropertyType.`name` LIKE '%s' ''' % (actionId, actionPropertyName))
            return db.query(stmt)

        def queryReceivedTime(eventId):
            queryTable = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            stmt = db.selectStmt(queryTable, tableAction['endDate'], '''ActionType.`flatCode` LIKE 'received' AND Action.`event_id` = %s''' %eventId)
            return db.query(stmt)

        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableAPS = db.table('ActionProperty_String')
        tableAPO = db.table('ActionProperty_Organisation')
        tableOrg = db.table('Organisation')
        tableAPOS = db.table('ActionProperty_OrgStructure')
        tableOS = db.table('OrgStructure')
        tableContract = db.table('Contract')
        tableResult = db.table('rbResult')

        tableDiagnostic = db.table('Diagnostic')
        subTableDiagnostic = tableDiagnostic.alias('subqueryDiagnostic')
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnosisType = db.table('rbDiagnosisType')
        tableMKB = db.table('MKB_Tree')
        diagnosisCond = [tableDiagnostic['deleted'].eq(0),
                         tableDiagnosisType['code'].inlist(['7', '11']), # Основной предварительный и Сопутствующий предварительный
                         subTableDiagnostic['event_id'].eq(tableEvent['id'])
        ]
        subQueryTable = subTableDiagnostic.innerJoin(tableDiagnosisType, tableDiagnosisType['id'].eq(subTableDiagnostic['diagnosisType_id']))
        subQeuryStmt = db.selectStmt(subQueryTable,
                                     subTableDiagnostic['id'],
                                     where = diagnosisCond,
                                     order = [tableDiagnosisType['code'],
                                              u'%s DESC' % subTableDiagnostic['id'].name()],
                                     limit = 1)

        cols = [tableAction['id'],
                tableEvent['id'].alias('eventId'),
                tableEvent['eventType_id'],
                tableEvent['client_id'],
                tableEvent['externalId'],
                tableContract['number'].alias('contractNumber'),
                tableContract['date'].alias('contractDate'),
                tableContract['resolution'].alias('contractResolution'),
                tableResult['name'].alias('resultName'),
                tableClient['lastName'],
                tableClient['firstName'],
                tableClient['patrName'],
                tableClient['sex'],
                tableClient['birthDate'],
                tableAction['begDate'],
                tableAction['note'],
                tableAction['finance_id'],
                tableEvent['contract_id'],
                tableEvent['externalId'],
                tableEvent['order'],
                tableDiagnosis['MKB'],
                tableMKB['DiagName']
        ]
        queryTable = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableContract, tableEvent['contract_id'].eq(tableContract['id']))
        queryTable = queryTable.innerJoin(tableResult, tableEvent['result_id'].eq(tableResult['id']))
        queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
        queryTable = queryTable.leftJoin(tableDiagnostic, tableDiagnostic['id'].signEx('=', u'(%s)' % subQeuryStmt))
        queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
        queryTable = queryTable.leftJoin(tableMKB, tableMKB['DiagID'].eq(tableDiagnosis['MKB']))
        cond = [ tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(u'received%')),
                 tableAction['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableAP['deleted'].eq(0),
                 tableAPT['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 tableAP['action_id'].eq(tableAction['id'])
        ]
        # if begDate:
        #     cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].datetimeGe(QDateTime(begDate, changingDayTime))]))
        # if endDate:
        #     cond.append(db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].datetimeLe(QDateTime(endDate, changingDayTime))]))
        cond.append(tableAction['begDate'].yearEq(QtCore.QDate.currentDate()))
        flagPrefix = False
        if prefix:
            cond.append(tableEvent['externalId'].like(prefix + '%'))
            flagPrefix = True
            if diapFrom:
                cond.append('CAST(RIGHT(Event.`externalId`, CHAR_LENGTH(Event.`externalId`) - %s) AS DECIMAL) >= %s' % (len(prefix), forceInt(diapFrom)))
            if diapTo:
                cond.append('CAST(RIGHT(Event.`externalId`, CHAR_LENGTH(Event.`externalId`) - %s) AS DECIMAL) <= %s' % (len(prefix), forceInt(diapTo)))
        else:
            if diapFrom:
                cond.append('CAST(Event.`externalId` AS DECIMAL) >= %s' % forceInt(diapFrom))
            if diapTo:
                cond.append('CAST(Event.`externalId` AS DECIMAL) <= %s' % forceInt(diapTo))
        if contractIdList:
            cond.append(tableEvent['contract_id'].inlist(contractIdList))
        if resultId:
            cond.append(tableEvent['result_id'].eq(resultId))

        # if sexIndex > 0:
        #     cond.append(tableClient['sex'].eq(sexIndex))
        # if ageFor <= ageTo:
        #     cond.append(getAgeRangeCond(ageFor, ageTo))
        # if orgStructureIndex:
        #     if self.getOrgStructureId(orgStructureIndex):
        #         orgStructureIdList = getOrgStructureIdList(orgStructureIndex)
        #         queryTable = queryTable.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
        #         queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
        #         cond.append(tableOS['id'].inlist(orgStructureIdList))
        stmt = db.selectStmt(queryTable,
                             cols,
                             cond,
                             order = 'CAST(RIGHT(Event.`externalId`, CHAR_LENGTH(Event.`externalId`) - %s) AS DECIMAL)' % len(prefix),
                             isDistinct = True)
        query = db.query(stmt)
        number = 1
        while query.next():
            records = query.record()
            clientId = forceRef(records.value('client_id'))
            eventId = forceRef(records.value('eventId'))
            begDate = forceDate(records.value('begDate'))
            begTime = forceTime(records.value('begDate'))
            externalId = forceString(records.value('externalId'))
            actionId = forceInt(records.value('id'))
            contractName = u' '.join([forceString(records.value('contractNumber')), forceString(records.value('contractName')), forceString(records.value('contractResolution'))])
            resultName = forceString(records.value('resultName'))

            flagNum = True
            if flagPrefix:
                lenPrefix = len(prefix)
                num = externalId[lenPrefix:]
                if diapFrom:
                    if forceInt(num) < forceInt(diapFrom): # externalId < diapFrom
                        flagNum = False
                if diapTo:
                    if forceInt(num) > forceInt(diapTo): # externalId > diapTo
                        flagNum = False
                if not num.isdigit() and len(num) != len(diapFrom) and len(num) != len(diapTo):
                    flagNum = False
            else:
                if diapFrom:
                    if forceInt(externalId) < forceInt(diapFrom):
                        flagNum = False
                if diapTo:
                    if forceInt(externalId) > forceInt(diapTo):
                        flagNum = False
                if not externalId.isdigit():
                    flagNum = False
            if clientId and flagNum:
                clientInfo = getClientInfoEx(clientId)
                address = u''
                if clientInfo['regAddress']:
                    address = u'регистрация: ' + clientInfo['regAddress']
                # if clientInfo['locAddress']:
                #     address += u', проживание: ' + clientInfo['locAddress']
                if clientInfo['phones']:
                    address += u', телефон: ' + clientInfo['phones']
                if clientInfo['work']:
                    address += u', место работы: ' + clientInfo['work']
                i = table.addRow()
                table.setText(i, 0, number)
                number += 1
                table.setText(i, 1, externalId)
                table.setText(i, 2, resultName)
                table.setText(i, 3, contractName)

                queryMovingTm = queryReceivedTime(eventId)
                movingBegTime = QtCore.QTime(00, 00, 00)
                if queryMovingTm.first():
                    recordMovingTime = queryMovingTm.record()
                    movingBegTime = forceTime(recordMovingTime.value('endDate'))
                    movingBegDate = forceDate(recordMovingTime.value('endDate'))
                    if movingBegDate == begDate:
                        differenceBegTime = movingBegTime.addSecs( -(begTime.hour()*3600 + begTime.minute()*60 + begTime.second()))
                    elif movingBegDate > begDate:
                        differenceBegTime = movingBegTime.addSecs( 86400 - (begTime.hour()*3600 + begTime.minute()*60 + begTime.second()) + (movingBegTime.hour()*3600 + movingBegTime.minute()*60 + movingBegTime.second()))
                else:
                    differenceBegTime = QtCore.QTime(00, 00, 00)
                table.setText(i, 4, begDate.toString('dd.MM.yyyy') + ' ' + begTime.toString('hh:mm:ss') + '/' + movingBegTime.toString('hh:mm:ss') + ' (' + differenceBegTime.toString('hh:mm:ss') + ')')
                table.setText(i, 5, clientInfo['fullName'])
                table.setText(i, 6, clientInfo['birthDate'] + u' (' + clientInfo['age'] + u')')
                table.setText(i, 7, address)

                whoDirecting = u''
                queryClientId = queryProperty(u'received%', u'whoDirecting', u'Кем направлен%', 0)
                if queryClientId.first():
                    record = queryClientId.record()
                    whoDirecting = u'Направлен: ' + forceString(record.value('whoDirecting')) + u' '
                queryClientId = queryProperty(u'received%', u'whoDelivered', u'Кем доставлен%')
                if queryClientId.first():
                    record = queryClientId.record()
                    whoDirecting += u'Доставлен: ' + forceString(record.value('whoDelivered'))
                table.setText(i, 8, whoDirecting)
                nameOSPartList = []
                queryClientId = queryProperty(u'received%', u'orgStructure', u'Направлен в отделение%', 1)
                if queryClientId.first():
                    record = queryClientId.record()
                    nameOSPartList.append(forceString(record.value('orgStructure')))
                eventOrder = forceInt(records.value('order'))
                nameOSPartList.append({1 : u'Плановый',
                                       2 : u'Экстренный',
                                       #3 : u'Самотеком',
                                       #4 : u'Принудительный',
                                       #6 : u'Неотложный'
                                      }.get(eventOrder, u''))
                table.setText(i, 9, u'; '.join(nameOS for nameOS in nameOSPartList if nameOS))
                queryPropertyStr1 = queryPropertyString(actionId, u'Диагноз направителя')
                diag1 = ''
                if queryPropertyStr1.first():
                    recordsPropertyString1 = queryPropertyStr1.record()
                    diag1 = forceString(recordsPropertyString1.value('value'))
                table.setText(i, 10, diag1)
                queryPropertyStr2 = queryPropertyString(actionId, u'Диагноз приёмного отделения')
                mkb = forceString(records.value('MKB'))
                mkbDescr = forceString(records.value('DiagName'))
                diagnosisList = []
                if mkb:
                    diagnosisList.append(mkb + (u' (%s)' % mkbDescr if mkbDescr else u''))
                if queryPropertyStr2.first():
                    recordsPropertyString2 = queryPropertyStr2.record()
                    diagnosisList.append(forceString(recordsPropertyString2.value('value')))
                table.setText(i, 11, '\n'.join(diagnosisList))
                queryPropertyStr3 = queryPropertyString(actionId, u'Профиль')
                prof = ''
                if queryPropertyStr3.first():
                    recordsPropertyString3 = queryPropertyStr3.record()
                    prof = forceString(recordsPropertyString3.value('value'))
                table.setText(i, 12, prof)



        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)
        reportView = CReportViewOrientationMargins(self, QtGui.QPrinter.Landscape, (50, 50, 50, 50, QtGui.QPrinter.Millimeter))
        reportView.setWindowTitle(u'Журнал')
        reportView.setText(doc)
        reportView.exec_()


    @QtCore.pyqtSlot()
    def on_mnuBtnPrint_aboutToShow(self):
        self.on_mnuHospitalBeds_aboutToShow()


    @QtCore.pyqtSlot()
    def on_btnTemperatureList_clicked(self):
        self.on_actTemperatureListEditor_triggered()


    @QtCore.pyqtSlot()
    def on_mnuBtnFeed_aboutToShow(self):
        self.on_mnuFeed_aboutToShow()


    @QtCore.pyqtSlot()
    def on_mnuFeed_aboutToShow(self):
        self.tblPresence.setFocus(QtCore.Qt.OtherFocusReason)
        currentIndex = self.tblPresence.currentIndex()
        isBusy = currentIndex.row() >= 0
        tabPresenceIndex = self.tabWidget.indexOf(self.tabPresence)
        currentTabIndex = self.tabWidget.currentIndex()
        self.actSelectAllFeed.setEnabled(isBusy and (currentTabIndex == tabPresenceIndex))
        self.actSelectAllNoFeed.setEnabled(isBusy and (currentTabIndex == tabPresenceIndex))
        self.actSelectionAllRow.setEnabled(isBusy and (currentTabIndex == tabPresenceIndex))
        rows = self.getSelectedRows(self.tblPresence)
        self.actClearSelectionRow.setEnabled(isBusy and (currentTabIndex == tabPresenceIndex) and bool(rows))
        self.actProlongationFeed.setEnabled(isBusy and (currentTabIndex == tabPresenceIndex) and bool(rows))
        self.actGetFeedFromMenuAll.setEnabled(isBusy and (currentTabIndex == tabPresenceIndex) and bool(rows))


    def getSelectedRows(self, table):
        rowCount = table.model().rowCount()
        rowSet = set([index.row() for index in table.selectedIndexes() if index.row()<rowCount])
        result = list(rowSet)
        result.sort()
        return result


    @QtCore.pyqtSlot()
    def on_actSelectAllFeed_triggered(self):
        self.notSelectedRows = False
        self.tblPresence.clearSelection()
        self.tblPresence.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        items = self.tblPresence.model().items
        selectRowList = []
        for row, item in enumerate(items):
            if item.get('clientId', 0) and (row not in selectRowList):
                self.tblPresence.selectRow(row)
                selectRowList.append(row)
        self.tblPresence.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setActionsIdList([], None)


    @QtCore.pyqtSlot()
    def on_actSelectAllNoFeed_triggered(self):
        self.notSelectedRows = False
        self.tblPresence.clearSelection()
        self.tblPresence.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        items = self.tblPresence.model().items
        selectRowList = []
        for row, item in enumerate(items):
            if (not item.get('clientId', 0)) and (row not in selectRowList):
                self.tblPresence.selectRow(row)
                selectRowList.append(row)
        self.tblPresence.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setActionsIdList([], None)


    @QtCore.pyqtSlot()
    def on_actSelectionAllRow_triggered(self):
        self.notSelectedRows = False
        self.tblPresence.clearSelection()
        self.tblPresence.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblPresence.selectAll()
        self.tblPresence.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setActionsIdList([], None)


    @QtCore.pyqtSlot()
    def on_actClearSelectionRow_triggered(self):
        self.notSelectedRows = True
        self.tblPresence.clearSelection()
        rowCount = self.modelPresence.rowCount()
        if rowCount > 0:
            self.tblPresence.setCurrentRow(0)

    @QtCore.pyqtSlot()
    def on_actProlongationFeed_triggered(self):
        eventIdList = self.getEventIdList()
        if self.lockList('Event', [eventData[0] for eventData in eventIdList]):
            try:
                self.notSelectedRows = True
                self.prolongationFeed(eventIdList)
                rowCount = self.modelPresence.rowCount()
                if rowCount > 0:
                    self.tblPresence.setCurrentRow(0)
            finally:
                self.releaseLockList()

    @QtCore.pyqtSlot()
    def on_actGetFeedFromMenuAll_triggered(self):
        eventIdList = self.getEventIdList()
        if self.lockList('Event', [eventData[0] for eventData in eventIdList]):
            try:
                self.notSelectedRows = True
                self.getFeedFromMenu(eventIdList)
                rowCount = self.modelPresence.rowCount()
                if rowCount > 0:
                    self.tblPresence.setCurrentRow(0)
            finally:
                self.releaseLockList()

    def getEventIdList(self):
        items = self.tblPresence.model().items
        selectIndexes = self.tblPresence.selectedIndexes()
        selectRowList = []
        eventIdList = []
        for selectIndex in selectIndexes:
            selectRow = selectIndex.row()
            if selectRow not in selectRowList:
                selectRowList.append(selectRow)
        for row, item in enumerate(items):
            if row in selectRowList:
                eventId = item.get('eventId', 0)
                if eventId and (eventId not in eventIdList):
                    eventData = [eventId, item.get('begDate', None), item.get('plannedEndDate', None), item.get('endDate', None)]
                    eventIdList.append(eventData)
        return eventIdList


    def prolongationFeed(self, eventIdList):
        #TODO и тут тоже
        for eventData in eventIdList:
            eventId = eventData[0] if eventData else None
            if eventId:
                db = QtGui.qApp.db
                tableEvent = db.table('Event')
                tableEventType = db.table('EventType')
                tableRBMealTime = db.table('rbMealTime')
                table = tableEvent.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
                eventTypeRecord = db.getRecordEx(table, tableEventType['id'], [tableEvent['id'].eq(eventId), tableEventType['form'].like('003')])
                if eventTypeRecord and forceRef(eventTypeRecord.value('id')):
                    begDatePresence = eventData[1] if len(eventData) >= 2 else None
                    plannedEndDatePresence = eventData[2] if len(eventData) >= 3 else None
                    endDatePresence = eventData[3] if len(eventData) >= 4 else None
                    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                    try:
                        currentDate = QtCore.QDate.currentDate()
                        nextDateFeed = QtCore.QDateTime(currentDate.addDays(1), QtCore.QTime()) if currentDate else None
                        if currentDate and nextDateFeed:
                            tableEventFeed = db.table('Event_Feed')
                            cond = [tableEventFeed['deleted'].eq(0),
                                    tableEventFeed['event_id'].eq(eventId)
                            ]
                            recordsAll = db.getRecordList(tableEventFeed, '*', cond, 'Event_Feed.date ASC')
                            prevEventIdList = {}
                            if not recordsAll:
                                prevEventId = None
                                prevEventRecord = db.getRecordEx(tableEvent, [tableEvent['id'], tableEvent['prevEvent_id']], [tableEvent['id'].eq(eventId), tableEvent['deleted'].eq(0)])
                                if prevEventRecord:
                                    prevId = forceRef(prevEventRecord.value('id'))
                                    prevEventId = forceRef(prevEventRecord.value('prevEvent_id'))
                                    prevEventIdList[prevId] = prevEventId
                                while prevEventId:
                                    prevEventRecord = db.getRecordEx(tableEvent, [tableEvent['id'], tableEvent['prevEvent_id']], [tableEvent['id'].eq(prevEventId), tableEvent['deleted'].eq(0)])
                                    if prevEventRecord:
                                        prevEventId = forceRef(prevEventRecord.value('prevEvent_id'))
                                        prevId = forceRef(prevEventRecord.value('id'))
                                        prevEventIdList[prevId] = prevEventId
                                    else:
                                        prevEventId = None
                            newRecords = []
                            records = []
                            prevEventIdList = []
                            if not recordsAll and prevEventIdList:
                                for prevId, prevEventId in prevEventIdList.items():
                                    if not records:
                                        cond = [tableEventFeed['deleted'].eq(0),
                                                tableEventFeed['date'].dateEq(currentDate),
                                                tableEventFeed['event_id'].eq(prevEventId)
                                        ]
                                        records = db.getRecordList(tableEventFeed, '*', cond, 'Event_Feed.date ASC')
                            else:
                                cond = [tableEventFeed['deleted'].eq(0),
                                        tableEventFeed['date'].dateEq(currentDate),
                                        tableEventFeed['event_id'].eq(eventId)
                                ]
                                records = db.getRecordList(tableEventFeed, '*', cond, 'Event_Feed.date ASC')
                            cond = [tableEventFeed['deleted'].eq(0),
                                    tableEventFeed['date'].dateEq(nextDateFeed.date()),
                                    tableEventFeed['event_id'].eq(eventId)
                            ]
                            recordsNextDate = db.getRecordList(tableEventFeed, '*', cond, 'Event_Feed.date ASC')
                            if not recordsNextDate:
                                dateTimeList = [begDatePresence if begDatePresence else QtCore.QDateTime(),
                                                endDatePresence if endDatePresence else (plannedEndDatePresence if plannedEndDatePresence else QtCore.QDateTime())
                                ]
                                if (not dateTimeList[0] or nextDateFeed >= dateTimeList[0]) and (not dateTimeList[1] or nextDateFeed <= dateTimeList[1]):
                                    for record in records:
                                        recordMealTime = db.getRecordEx(tableRBMealTime, '*', [tableRBMealTime['id'].eq(forceRef(record.value('mealTime_id')))])
                                        if recordMealTime:
                                            begTime = forceTime(recordMealTime.value('begTime'))
                                            endTime = forceTime(recordMealTime.value('endTime'))
                                            nextBegDateTime = nextDateFeed.setTime(begTime)
                                            nextBegDateTime = nextDateFeed
                                            nextEndDateTime = nextDateFeed.setTime(endTime)
                                            nextEndDateTime = nextDateFeed
                                            if ((not dateTimeList[0] or not nextBegDateTime or nextBegDateTime >= dateTimeList[0]) and (not dateTimeList[1] or not nextEndDateTime or nextEndDateTime <= dateTimeList[1])) or ((not dateTimeList[0] or not nextBegDateTime or nextBegDateTime <= dateTimeList[0]) and (not dateTimeList[0] or not nextEndDateTime or nextEndDateTime > dateTimeList[0])) or ((not dateTimeList[1] or not nextBegDateTime or nextBegDateTime < dateTimeList[1]) and (not dateTimeList[1] or not nextEndDateTime or nextEndDateTime >= dateTimeList[1])):
                                                newRecord = tableEventFeed.newRecord()
                                                newRecord.setValue('date', toVariant(nextDateFeed))
                                                newRecord.setValue('mealTime_id', record.value('mealTime_id'))
                                                newRecord.setValue('diet_id', record.value('diet_id'))
                                                newRecords.append(newRecord)
                                    for newRecord in newRecords:
                                        recordsAll.append(newRecord)
                                    if recordsAll:
                                        self.saveFeedFromMenu(eventId, recordsAll)
                                    self.modelPresence.reset()
                                    self.on_selectionModelOrgStructure_currentChanged(None, None)
                    finally:
                        QtGui.QApplication.restoreOverrideCursor()


    @QtCore.pyqtSlot()
    def on_mnuHospitalBeds_aboutToShow(self):
        widgetIndex = self.tabWidget.currentIndex()
        isBusy = False
        self.actReportLeaved.setEnabled(False)
        tabPresenceIndex = self.tabWidget.indexOf(self.tabPresence)
        tabReceivedIndex = self.tabWidget.indexOf(self.tabReceived)
        tabLeavedIndex = self.tabWidget.indexOf(self.tabLeaved)
        tabReanimationIndex = self.tabWidget.indexOf(self.tabReanimation)

        if widgetIndex == self.tabWidget.indexOf(self.tabFund):
            self.tblHospitalBeds.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblHospitalBeds.currentIndex()
            isBusy = currentIndex.row() >= 0 and self.modelHospitalBeds.isBusy(currentIndex)
        elif widgetIndex == tabPresenceIndex:
            self.tblPresence.setFocus(QtCore.Qt.TabFocusReason)
            currentIndex = self.tblPresence.currentIndex()
            isBusy = currentIndex.row() >= 0
            self.actPrintFeedReport.setEnabled(True)
            self.actPrintThermalSheet.setEnabled(isBusy)
        elif widgetIndex == tabReceivedIndex:
            self.tblReceived.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblReceived.currentIndex()
            isBusy = currentIndex.row() >= 0
        elif widgetIndex == self.tabWidget.indexOf(self.tabTransfer):
            self.tblTransfer.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblTransfer.currentIndex()
            isBusy = currentIndex.row() >= 0
        elif widgetIndex == tabLeavedIndex:
            self.tblLeaved.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblLeaved.currentIndex()
            isBusy = currentIndex.row() >= 0
            self.actReportLeaved.setEnabled(isBusy)
        elif widgetIndex == self.tabWidget.indexOf(self.tabReabyToLeave):
            self.tblReabyToLeave.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblReabyToLeave.currentIndex()
            isBusy = currentIndex.row() >= 0
        elif widgetIndex == self.tabWidget.indexOf(self.tabQueue):
            self.tblQueue.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblQueue.currentIndex()
            isBusy = currentIndex.row() >= 0
        elif widgetIndex == self.tabWidget.indexOf(self.tabRenunciation):
            self.tblRenunciation.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblRenunciation.currentIndex()
            isBusy = currentIndex.row() >= 0
        elif widgetIndex == self.tabWidget.indexOf(self.tabDeath):
            self.tblDeath.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblDeath.currentIndex()
            isBusy = currentIndex.row() >= 0
        elif widgetIndex == tabReanimationIndex:
            self.tblReanimation.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblReanimation.currentIndex()
            isBusy = currentIndex.row() >= 0
            self.actPrintFeedReport.setEnabled(True)
        elif widgetIndex == self.tabWidget.indexOf(self.tabLobby):
            self.tblLobby.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblLobby.currentIndex()
            isBusy = currentIndex.row() >= 0
        elif widgetIndex == self.tabWidget.indexOf(self.tabMaternityward):
            self.tblMaternityward.setFocus(QtCore.Qt.OtherFocusReason)
            currentIndex = self.tblMaternityward.currentIndex()
            isBusy = currentIndex.row() >= 0
            self.actPrintFeedReport.setEnabled(True)

        showGetFeedFromMenu = widgetIndex in [tabPresenceIndex, tabReceivedIndex, tabLeavedIndex, tabReanimationIndex]
        self.actGetFeedFromMenu.setVisible(showGetFeedFromMenu)
        self.actGetFeedFromMenu.setEnabled(showGetFeedFromMenu and isBusy)
        self.actTemperatureListEditor.setVisible(forceBool(widgetIndex == tabPresenceIndex))
        self.actTemperatureListEditor.setEnabled(forceBool(widgetIndex == tabPresenceIndex) and isBusy)

        self.actOpenEvent.setEnabled(isBusy)
        self.actEditClientInfoBeds.setEnabled(isBusy and widgetIndex)
        self.actStatusObservationClient.setEnabled(isBusy)
        self.actRelatedEventClient.setEnabled(isBusy)

        rows = self.getSelectedRows(self.getCurrentTable())
        showLocationCardContextMenu = widgetIndex == tabLeavedIndex and len(rows) > 1
        self.actOpenEvent.setVisible(not showLocationCardContextMenu)
        self.actEditClientInfoBeds.setVisible(not showLocationCardContextMenu)
        self.actStatusObservationClient.setVisible(not showLocationCardContextMenu)
        self.actRelatedEventClient.setVisible(not showLocationCardContextMenu)
        self.actMultipleHBLocationCardChange.setVisible(showLocationCardContextMenu)

        self.actPrintReport.setEnabled(isBusy)
        if widgetIndex not in [tabPresenceIndex, self.tabWidget.indexOf(self.tabReanimation), self.tabWidget.indexOf(self.tabMaternityward)]:
            self.actPrintFeedReport.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_mnuEditActionEvent_aboutToShow(self):
        currentIndex = self.getCurrentActionsTable().currentIndex()
        self.actEditActionEvent.setEnabled(currentIndex.row() >= 0)
        self.actEditClientInfo.setEnabled(currentIndex.row() >= 0)
        self.actEditStatusObservationClient.setEnabled(currentIndex.row() >= 0)


    @QtCore.pyqtSlot()
    def on_actEditClientInfoBeds_triggered(self):
        self.editClient()


    @QtCore.pyqtSlot()
    def on_actEditClientInfo_triggered(self):
        self.editClient()

    def editClient(self):
        table = self.getCurrentTable()
        if table:
            tableIndex = table.currentIndex()
            row = tableIndex.row()
            if row > -1:
                clientId = table.model().items[row].get('clientId', 0)
                if clientId:
                    from Registry.ClientEditDialog  import CClientEditDialog
                    dialog = CClientEditDialog(self)
                    if clientId:
                        dialog.load(clientId)
                    dialog.exec_()


    def getCurrentTable(self):
        index = self.tabWidget.currentIndex()
        if index == self.tabWidget.indexOf(self.tabFund):
            return None
        if index == self.tabWidget.indexOf(self.tabPresence):
            return self.tblPresence
        elif index == self.tabWidget.indexOf(self.tabReceived):
            return self.tblReceived
        elif index == self.tabWidget.indexOf(self.tabTransfer):
            return self.tblTransfer
        elif index == self.tabWidget.indexOf(self.tabLeaved):
            return self.tblLeaved
        elif index == self.tabWidget.indexOf(self.tabReabyToLeave):
            return self.tblReabyToLeave
        elif index == self.tabWidget.indexOf(self.tabQueue):
            return self.tblQueue
        elif index == self.tabWidget.indexOf(self.tabRenunciation):
            return self.tblRenunciation
        elif index == self.tabWidget.indexOf(self.tabDeath):
            return self.tblDeath
        elif index == self.tabWidget.indexOf(self.tabReanimation):
            return self.tblReanimation
        elif index == self.tabWidget.indexOf(self.tabLobby):
            return self.tblLobby
        else:
            return self.tblMaternityward


    @QtCore.pyqtSlot()
    def on_actStatusObservationClient_triggered(self):
        self.updateStatusObservationClient()


    @QtCore.pyqtSlot()
    def on_actRelatedEventClient_triggered(self):
        eventId = self.getCurrentEventId(self.tabWidget.currentIndex())
        if eventId:
            CRelatedEventListDialog(self, eventId).exec_()

    @QtCore.pyqtSlot()
    def on_actMultipleHBLocationCardChange_triggered(self):
        model = self.tblLeaved.model()
        eventIdList = [model.items[index].get('eventId', 0) for index in self.getSelectedRows(self.tblLeaved)]
        self.changeHBLocation(eventIdList)

    @QtCore.pyqtSlot()
    def on_actEditStatusObservationClient_triggered(self):
        self.updateStatusObservationClient()


    def updateStatusObservationClient(self):
        try:
            table = self.getCurrentTable()
            if table:
                tableIndex = table.currentIndex()
                row = tableIndex.row()
                if row > -1:
                    clientId = table.model().items[row].get('clientId', 0)
                    if clientId:
                        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
                            dialog = CStatusObservationClientEditor(self, clientId)
                            if dialog.exec_():
                                self.on_selectionModelOrgStructure_currentChanged(None, None)
        except:
            pass


    @QtCore.pyqtSlot()
    def on_actEditActionEvent_triggered(self):
        currentActionsTable = self.getCurrentActionsTable()
        actionId = currentActionsTable.currentItemId()
        if actionId:
            eventId = forceRef(QtGui.qApp.db.translate('Action', 'id', actionId, 'event_id'))
            if eventId:
                formClass = getEventFormClass(eventId)
                dialog = formClass(self)
                dialog.load(eventId)
                if dialog.exec_():
                    filters = {}
                    actionType = self.cmbFilterActionType.value()
                    if actionType:
                        filters['actionTypeId'] = actionType
                    filters['status'] = self.cmbFilterActionStatus.currentIndex()
                    filters['isUrgent'] = self.chkFilterIsUrgent.isChecked()
                    filters['begDatePlan'] = self.edtFilterBegDatePlan.date()
                    filters['endDatePlan'] = self.edtFilterEndDatePlan.date()
                    self.updateActionsList(filters, self.modelPresence.eventIdList if self.tabWidgetActionsClasses.currentIndex() > 0 else [self.getCurrentEventId(1)])
        if not actionId:
            currentActionsTable.setFocus(QtCore.Qt.TabFocusReason)
        elif actionId:
            currentActionsTable.setCurrentItemId(actionId)


    def requestNewEvent(self, isAmb=True, moveEventId=None, personId=None, begDate=None, endDate=None, externalId=None, referralId=None, clientId = None):
        if not clientId:
            clientId = self.currentClientId()
        dockFreeQueue = QtGui.qApp.mainWindow.dockFreeQueue
        if dockFreeQueue and dockFreeQueue.content and dockFreeQueue.content._appLockId:
            dockFreeQueue.content.on_actAmbCreateOrder_triggered()
        elif clientId:
            result = requestNewEvent(self, clientId, isAmb=isAmb, moveEventId=moveEventId,
                                     personId=personId, begDate=begDate, endDate=endDate, externalId=externalId, referralId=referralId)
            return result
        return None

    @QtCore.pyqtSlot()
    def on_actRecreateEventWithAnotherType_triggered(self):
        # currentTable = self.getCurrentTable()
        # currentRow = currentTable.currentRow()
        widgetIndex = self.tabWidget.currentIndex()
        eventId = self.getCurrentEventId(widgetIndex)
        if not eventId:
            return
        db = QtGui.qApp.db
        tblEvent = db.table('Event')

        record = db.getRecordEx(tblEvent,
                       'execPerson_id, externalId, setDate, execDate, client_id',
                       'id = %i' % eventId)
        clientId = forceInt(record.value('client_id'))
        personId = forceRef(record.value('execPerson_id'))
        externalId = forceStringEx(record.value('externalId'))
        begDate = forceDateTime(record.value('setDate'))
        endDate = forceDateTime(record.value('execDate'))

        tblAccountItem = db.table('Account_Item')
        if forceRef(db.translateEx(tblAccountItem, 'event_id', eventId, 'id')) is not None:
            QtGui.QMessageBox.warning(self, u'Ошибка!', u'Невозможно пересоздать выставленное в счёт обращение',
                                      QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return
        self.requestNewEvent(clientId=clientId, moveEventId=eventId, personId=personId,
                             externalId=externalId, begDate=begDate, endDate=endDate)

    @QtCore.pyqtSlot()
    def on_actOpenEvent_triggered(self):
        currentTable = self.getCurrentTable()
        currentRow = currentTable.currentRow()
        widgetIndex = self.tabWidget.currentIndex()
        eventId = self.getCurrentEventId(widgetIndex)
        if eventId:
            formClass = getEventFormClass(eventId)
            dialog = formClass(self)
            try:
                dialog.load(eventId)
                if self.btnLeavedEvent:
                    flatCode = u'leaved%'
                    db = QtGui.qApp.db
                    tableActionType = db.table('ActionType')
                    idListActionType = db.getIdList(tableActionType, [tableActionType['id']], [tableActionType['flatCode'].like(flatCode), tableActionType['deleted'].eq(0)])
                    actionTypeIdValue = None
                    if len(idListActionType) > 1:
                        dialogActionType = CActionTypeDialogTableModel(self, idListActionType)
                        if dialogActionType.exec_():
                            actionTypeIdValue = dialogActionType.currentItemId()
                    else:
                        actionTypeIdValue = idListActionType[0] if idListActionType else None
                    if actionTypeIdValue:
                        dialog.setLeavedAction(actionTypeIdValue)
                if dialog.exec_():
                    self.on_selectionModelOrgStructure_currentChanged(None, None)
                    if self.btnLeavedEvent:
                        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabLeaved))
                        self.tblLeaved.setFocus(QtCore.Qt.OtherFocusReason)
                        countRow = self.modelLeaved.rowCount()
                        row = -1
                        while row != (countRow - 1):
                            if eventId == self.modelLeaved.items[row].get('eventId', 0):
                                self.tblLeaved.setCurrentRow(row)
                                break
                            row += 1
                        self.btnLeavedEvent = False
            finally:
                self.btnLeavedEvent = False
        self.btnLeavedEvent = False
        if widgetIndex == 1:
            currentTable.setCurrentRow(currentRow)
            self.updateActionsList({}, [self.getCurrentEventId(1)])
        else:
            currentTable.setCurrentRow(currentRow)
            self.on_selectionModelOrgStructure_currentChanged(None, None)


    @QtCore.pyqtSlot(bool)
    def on_chkInvolution_toggled(self, checked):
        self.cmbInvolute.setEnabled(checked)
        self.cmbInvolute.setCurrentIndex(0)


    @QtCore.pyqtSlot(bool)
    def on_chkAttachType_toggled(self, checked):
        isTabFund = self.tabWidget.currentIndex() == self.tabWidget.indexOf(self.tabFund)
        self.cmbAttachType.setEnabled(not isTabFund and checked)
        self.cmbAttachType.setCurrentIndex(0)


    @QtCore.pyqtSlot(int)
    def on_cmbReceived_currentIndexChanged(self, index):
        if index == 1:
            self.cmbLocationClient.setEnabled(True)
        else:
            self.cmbLocationClient.setEnabled(False)
        self.cmbFilterIsPermanent.setEnabled(index == 1)
        self.cmbFilterType.setEnabled(index == 1)
        self.cmbFilterProfile.setEnabled(index == 1)


    @QtCore.pyqtSlot(int)
    def on_cmbLeaved_currentIndexChanged(self, index):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == self.tabWidget.indexOf(self.tabLeaved):
            self.cmbFilterIsPermanent.setEnabled(index != 0)
            self.cmbFilterType.setEnabled(index != 0)
            self.cmbFilterProfile.setEnabled(index != 0)
        elif widgetIndex == self.tabWidget.indexOf(self.tabReabyToLeave):
            self.cmbFilterIsPermanent.setEnabled(True)
            self.cmbFilterType.setEnabled(True)
            self.cmbFilterProfile.setEnabled(True)


    @QtCore.pyqtSlot(int)
    def on_cmbRenunciationAction_currentIndexChanged(self, index):
        self.cmbFilterIsPermanent.setEnabled(index == 1)
        self.cmbFilterType.setEnabled(index == 1)
        self.cmbFilterProfile.setEnabled(index == 1)


    @QtCore.pyqtSlot(int)
    def on_cmbFeed_currentIndexChanged(self, index):
        if index == 0:
            self.edtDateFeed.setDate(QtCore.QDate.currentDate())
        self.edtDateFeed.setEnabled(forceBool(index) and self.cmbFeed.isEnabled())

    @classmethod
    def setFilterWidgetValue(cls, widget, value):
        """Устанавливает значение value для указанного виджета (почти универсально)

        @param widget: виджет
        @param value: значение
        """
        if isinstance(widget, CRBComboBox):
            widget.setValue(value)
        elif isinstance(widget, CDateEdit):
            widget.setDate(forceDate(value))
        elif isinstance(widget, QtGui.QComboBox):
            widget.setCurrentIndex(forceInt(value))
        elif isinstance(widget, QtGui.QLineEdit):
            widget.setText(forceStringEx(value))
        elif isinstance(widget, QtGui.QCheckBox):
            widget.setChecked(forceBool(value))
        elif isinstance(widget, QtGui.QSpinBox):
            widget.setValue(forceInt(value))


    @classmethod
    def setFilterWidgetEnabled(cls, widget, enabled, defaultValue=None):
        """Настройка отображения фильтров. Отвечает за видимость (чтоб не мешалось на экране) и за "включенность"
        (enabled проверяется при применении фильтров)

        @param widget: виджет фильтра. Если фильтр состоит из одного виджета, передается этот виджет. Если из лэйбла и соответствующего виджета - передается лэйбл, а сам фильтр получается автоматически (нужно указать связь в gui)
        @param enabled: включен/выключен
        @param defaultValue: значение по умолчанию. Подразумевается, что метод вызывается только при переключении между вкладками, и значения всех фильтров сбрасываются.
        @return: None
        """
        if not isinstance(widget, QtGui.QWidget):
            return
        if isinstance(widget, QtGui.QLabel):
            buddyWidget = widget.buddy()
            cls.setFilterWidgetEnabled(buddyWidget, enabled, defaultValue)
        else:
            cls.setFilterWidgetValue(widget, defaultValue)
        widget.setVisible(enabled)
        widget.setEnabled(enabled)


    @QtCore.pyqtSlot(int)
    def currentTabChanged(self, index):
        #TODO: age, ageTo и sex - можно ли избавиться от двух наборов одинаковых виджетов??

        def isTab(tab):
            return index == self.tabWidget.indexOf(tab)

        app = QtGui.qApp

        isTabFund = isTab(self.tabFund)
        isTabPresence = isTab(self.tabPresence)
        isTabReceived = isTab(self.tabReceived)
        isTabTransfer = isTab(self.tabTransfer)
        isTabLeaved = isTab(self.tabLeaved)
        isTabReadyToLeave = isTab(self.tabReabyToLeave)
        isTabQueue = isTab(self.tabQueue)
        isTabRenunciation = isTab(self.tabRenunciation)
        isTabDeath = isTab(self.tabDeath)
        isTabReanimation = isTab(self.tabReanimation)
        isTabLobby = isTab(self.tabLobby)
        isTabMaternityward = isTab(self.tabMaternityward)


        self.setFilterWidgetEnabled(self.grpPatient, True)
        self.setFilterWidgetEnabled(self.lblStatusObservation, True)

        self.setFilterWidgetEnabled(self.cmbFilterAccountingSystem, not isTabFund)
        self.setFilterWidgetEnabled(self.edtFilterClientId,         not isTabFund)
        self.setFilterWidgetEnabled(self.btnFindClientInfo,         not isTabFund)
        self.setFilterWidgetEnabled(self.lblFilterEventId,          not isTabFund)
        self.setFilterWidgetEnabled(self.lblSexBed,                 isTabFund)
        self.setFilterWidgetEnabled(self.lblBedAge,                 isTabFund)
        self.setFilterWidgetEnabled(self.lblBedAgeTo,               isTabFund, 150)
        self.setFilterWidgetEnabled(self.lblFilterSchedule,         isTabFund)
        self.setFilterWidgetEnabled(self.lblFilterBusy,             isTabFund)
        self.setFilterWidgetEnabled(self.chkInvolution,             isTabFund)
        self.setFilterWidgetEnabled(self.cmbInvolute,               isTabFund)
        self.setFilterWidgetEnabled(self.lblFilterCode,             any([isTabFund, isTabPresence]))
        self.setFilterWidgetEnabled(self.chkAttachType,             not any([isTabFund, isTabLobby]))
        self.setFilterWidgetEnabled(self.cmbAttachType,             not any([isTabFund, isTabLobby]))
        self.cmbAttachType.setEnabled(False)
        self.setFilterWidgetEnabled(self.lblFinance,                not any([isTabFund, isTabLobby]))
        self.setFilterWidgetEnabled(self.lblFilterPermanent,        not isTabDeath)
        self.setFilterWidgetEnabled(self.lblFilterType,             not isTabDeath)
        self.setFilterWidgetEnabled(self.lblProfile,                not isTabDeath)
        self.setFilterWidgetEnabled(self.chkAssistant,              isTabLeaved) #TODO: atronah: фильтр используется только на вкладке "Выбыли", но доступен всегда
        self.setFilterWidgetEnabled(self.cmbAssistant,              isTabLeaved)
        self.setFilterWidgetEnabled(self.lblHospitalizingOutcome,   any([isTabLeaved, isTabDeath]))
        self.cmbInvolute.setEnabled(False)

        self.setFilterWidgetEnabled(self.lblReceived,               isTabReceived)
        self.setFilterWidgetEnabled(self.lblTransfer,               isTabTransfer)
        self.setFilterWidgetEnabled(self.chkStayOrgStructure,       isTabTransfer)
        self.setFilterWidgetEnabled(self.lblQuotingType,            not any([isTabFund, isTabReanimation, isTabLobby, isTabMaternityward]))
        self.setFilterWidgetEnabled(self.lblDateFeed,       any([isTabPresence, isTabReceived, isTabTransfer, isTabReadyToLeave]), QtCore.QDate().currentDate())
        self.setFilterWidgetEnabled(self.lblFeed,           any([isTabPresence, isTabReceived, isTabTransfer, isTabReadyToLeave]))
        self.setFilterWidgetEnabled(self.lblLocationClient, any([isTabFund, isTabPresence, isTabTransfer, isTabLeaved, isTabQueue, isTabReanimation, isTabMaternityward]))
        self.setFilterWidgetEnabled(self.lblLeaved,         any([isTabLeaved, isTabReadyToLeave]))
        self.setFilterWidgetEnabled(self.lblLocationCard,       isTabLeaved)
        self.setFilterWidgetEnabled(self.cmbLocationCard,       isTabLeaved)

        self.setFilterWidgetEnabled(self.lblRenunciation,       isTabRenunciation)
        self.setFilterWidgetEnabled(self.lblRenunciationAction, isTabRenunciation)
        self.setFilterWidgetEnabled(self.lblPresenceDay,        any([isTabPresence, isTabQueue]))
        self.setFilterWidgetEnabled(self.lblPresenceDay_2,      any([isTabPresence, isTabQueue]))
        self.setFilterWidgetEnabled(self.lblFilterBegDate,      not isTabPresence, QtCore.QDate.currentDate())
        self.setFilterWidgetEnabled(self.edtFilterBegTime,      not isTabPresence and self.filterByExactTime, QtCore.QDate.currentDate())
        self.setFilterWidgetEnabled(self.lblChangingDayTime,    not isTabPresence and not self.filterByExactTime, QtCore.QTime())
        self.setFilterWidgetEnabled(self.lblFilterEndDate,      not isTabPresence)
        self.setFilterWidgetEnabled(self.edtFilterEndTime,      not isTabPresence, QtCore.QDate.currentDate())
        self.setFilterWidgetEnabled(self.lblSexPresence,        not any([isTabFund, isTabReanimation, isTabLobby, isTabMaternityward]))
        self.setFilterWidgetEnabled(self.lblAgePresence,        not any([isTabFund, isTabReanimation, isTabLobby, isTabMaternityward]))
        self.setFilterWidgetEnabled(self.lblAgePresenceTo,      not any([isTabFund, isTabReanimation, isTabLobby, isTabMaternityward]), 150)
        self.setFilterWidgetEnabled(self.lblLobbyAction,        isTabLobby)
        self.setFilterWidgetEnabled(self.lblLobbyResult,        isTabLobby)
        self.setFilterWidgetEnabled(self.chkShowFinished,       isTabLobby)

        self.setFilterWidgetEnabled(self.btnFeed,               isTabPresence)
        self.setFilterWidgetEnabled(self.btnTemperatureList,    isTabPresence)

        self.cmbLeaved.clear()

        self.btnHospitalization.setEnabled(any([isTabReceived and app.userHasAnyRight([urAdmin, urHospitalTabReceived]),
                                                (isTabQueue or isTabLobby) and app.userHasAnyRight([urAdmin, urHospitalTabPlanning])]))
        self.btnLeaved.setEnabled(isTabPresence and app.userHasAnyRight([urAdmin, urLeavedTabPresence]))



        if isTabFund:           self.updateHospitalBeds()
        elif isTabReceived:     self.loadDataReceived()
        elif isTabTransfer:     self.loadDataTransfer()
        elif isTabQueue:        self.loadDataQueue()
        elif isTabRenunciation: self.loadDataRenunciation()
        elif isTabReanimation:  self.loadDataReanimation()
        elif isTabLobby:        self.loadDataLobby()
        elif isTabMaternityward:  self.loadDataMaternityward()

        elif isTabPresence:
            self.loadDataPresence()
            self.tblPresence.setFocus(QtCore.Qt.TabFocusReason)
            if self.modelPresence.rowCount():
                self.tblPresence.setCurrentRow(0)
            self.updateActionsList({}, [self.getCurrentEventId(1)])

        elif isTabLeaved:
            self.cmbLeaved.addItems([u'из ЛПУ', u'без выписки', u'из отделений'])
            self.reasonRenunciateDeath()
            self.loadDataLeaved()

        elif isTabReadyToLeave:
            self.cmbLeaved.addItems([u'из ЛПУ', u'перевод в отделение'])
            self.loadDataReadyToLeave()

        elif isTabDeath:
            self.reasonRenunciateDeath(True)
            self.loadDataDeath()

        self.lblCountRecordList.setText(formatRecordsCount(self.getCurrentWidgetRowCount(index)))
        self.updatePrintMenu()


    @QtCore.pyqtSlot(int)
    def on_cmbLobbyAction_currentIndexChanged(self, index):
        self.cmbLobbyResult.setEnabled(index == 1)


    @QtCore.pyqtSlot(int)
    def on_tabWidgetActionsClasses_currentChanged(self, index):
        self.grbActionFilter.setVisible(not index == 0)
        if index > 0:
            if not self.notSelectedRows:
                self.on_actClearSelectionRow_triggered()
            self.cmbFilterActionType.setClass(index-1)
            self.cmbFilterActionType.setValue(self.__actionTypeIdListByClassPage[index-1])
            self.on_buttonBoxAction_apply()
        else:
            self.tblPresence.setFocus(QtCore.Qt.TabFocusReason)
            if self.notSelectedRows:
                self.updateActionsList({}, [self.getCurrentEventId(1)])
            else:
                self.setActionsIdList([], None)


    def getCurrentActionsTable(self):
        index = self.tabWidgetActionsClasses.currentIndex()
        return [self.tblActionList, self.tblActionsStatus, self.tblActionsDiagnostic, self.tblActionsCure, self.tblActionsMisc][index]


    def setActionsIdList(self, idList, posToId):
        self.getCurrentActionsTable().setIdList(idList, posToId)


    def updateActionsList(self, filters, eventIdList=None, posToId=None):
        if not eventIdList:
            eventIdList = []
        actionClass = self.tabWidgetActionsClasses.currentIndex()-1
        if eventIdList and self.notSelectedRows:
            db = QtGui.qApp.db
            table = db.table('Action')
            tableEvent = db.table('Event')
            queryTable = table.leftJoin(tableEvent, tableEvent['id'].eq(table['event_id']) )
            cond = [table['deleted'].eq(0), tableEvent['deleted'].eq(0)]
            cond.append(table['event_id'].inlist(eventIdList))
            actionTypeTSIdList = getActionTypeIdListByFlatCode(u'temperatureSheet%')
            if actionClass > -1:
                if 'actionTypeId' in filters:
                    actionTypeIdList = getActionTypeDescendants(filters['actionTypeId'], actionClass)
                    cond.append(table['actionType_id'].inlist(actionTypeIdList))
                else:
                    cond.append(table['actionType_id'].name()+' IN (SELECT ActionType.id FROM ActionType WHERE ActionType.class=%d)' % actionClass)
                if actionTypeTSIdList:
                    cond.append(table['actionType_id'].notInlist(actionTypeTSIdList))
                begDatePlan = filters.get('begDatePlan', None)
                isUrgent = filters.get('isUrgent', 0)
                endDatePlan = filters.get('endDatePlan', None)
                if isUrgent:
                    cond.append(table['isUrgent'].eq(1))
                if begDatePlan or endDatePlan:
                    cond.append('DATE(Action.`plannedEndDate`) != 0')
                if begDatePlan:
                    cond.append(table['plannedEndDate'].dateGe(begDatePlan))
                if endDatePlan:
                    cond.append(table['plannedEndDate'].dateLe(endDatePlan))
                if filters.get('status', 0) == 1:
                    cond.append(db.joinOr([table['status'].eq(5), table['status'].eq(0)]))
                else:
                    status = filters.get('status', 0) - 2
                    if status > -1:
                        cond.append(table['status'].eq(status))
            elif actionClass == -1:
                if self.cmbFilterActionList.currentIndex() == 1:
                    cond.append(db.joinOr([table['status'].eq(5), table['status'].eq(0)]))
                else:
                    status = self.cmbFilterActionList.currentIndex() - 2
                    if status > -1:
                        cond.append(table['status'].eq(status))
                classActions = []
                if self.chkListStatus.isChecked():
                    classActions.append(u'0')
                if self.chkListDiagnostic.isChecked():
                    classActions.append(u'1')
                if self.chkListCure.isChecked():
                    classActions.append(u'2')
                if self.chkListMisc.isChecked():
                    classActions.append(u'3')
                if classActions:
                    cond.append(table['actionType_id'].name()+' IN (SELECT ActionType.id FROM ActionType WHERE ActionType.class IN ('+', '.join([classAction for classAction in classActions])+'))')
                if actionTypeTSIdList:
                    cond.append(table['actionType_id'].notInlist(actionTypeTSIdList))
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                idList = db.getDistinctIdList(queryTable,
                                              table['id'].name(),
                                              cond,
                                              ['Event.execDate DESC', 'Action.id'])
                self.setActionsIdList(idList, posToId)
            finally:
                QtGui.QApplication.restoreOverrideCursor()
        else:
            self.setActionsIdList([], None)


    def getActionTypeDescendants2(self, actionTypeId):
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        result = set([actionTypeId])
        parents = [actionTypeId]
        classCond = db.joinOr([tableActionType['class'].eq(1), tableActionType['class'].eq(2)])
        while parents:
            cond = tableActionType['group_id'].inlist(parents)
            if classCond:
                cond = [cond, classCond]
                children = set(db.getIdList(tableActionType, where=cond))
                newChildren = children-result
                result |= newChildren
                parents = newChildren
        return list(result)


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxActionList_clicked(self, button):
        buttonCode = self.buttonBoxActionList.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.updateActionsList({}, [self.getCurrentEventId(1)])
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.cmbFilterActionList.setCurrentIndex(1)
            self.chkListStatus.setChecked(False)
            self.chkListDiagnostic.setChecked(True)
            self.chkListCure.setChecked(True)
            self.chkListMisc.setChecked(False)
            self.updateActionsList({}, [self.getCurrentEventId(1)])


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxAction_clicked(self, button):
        buttonCode = self.buttonBoxAction.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBoxAction_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBoxAction_reset()


    def on_buttonBoxAction_reset(self):
        self.cmbFilterActionType.setValue(0)
        self.cmbFilterActionStatus.setCurrentIndex(1)
        self.chkFilterIsUrgent.setChecked(False)
        self.edtFilterBegDatePlan.setDate(QtCore.QDate())
        self.edtFilterEndDatePlan.setDate(QtCore.QDate())
        filters = {}
        filters['status'] = self.cmbFilterActionStatus.currentIndex()
        filters['isUrgent'] = self.chkFilterIsUrgent.isChecked()
        filters['begDatePlan'] = self.edtFilterBegDatePlan.date()
        filters['endDatePlan'] = self.edtFilterEndDatePlan.date()
        self.updateActionsList(filters, self.modelPresence.eventIdList if self.tabWidgetActionsClasses.currentIndex()!= 0 else [self.getCurrentEventId(1)])


    def on_buttonBoxAction_apply(self):
        filters = {}
        actionType = self.cmbFilterActionType.value()
        if actionType:
            filters['actionTypeId'] = actionType
        filters['status'] = self.cmbFilterActionStatus.currentIndex()
        filters['isUrgent'] = self.chkFilterIsUrgent.isChecked()
        filters['begDatePlan'] = self.edtFilterBegDatePlan.date()
        filters['endDatePlan'] = self.edtFilterEndDatePlan.date()
        self.updateActionsList(filters, self.modelPresence.eventIdList if self.tabWidgetActionsClasses.currentIndex()!= 0 else [self.getCurrentEventId(1)])


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelHospitalBeds_currentRowChanged(self, current, previous):
        eventId = self.tblHospitalBeds.currentItemId()
        self.modelInvoluteBeds.loadItems(eventId)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelPresence_currentRowChanged(self, current, previous):
        if self.notSelectedRows:
            self.updateActionsList({}, [self.getCurrentEventId(1)])
        else:
            self.setActionsIdList([], None)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionList_currentRowChanged(self, current, previous):
        actionTypeName = ''
        actionCountStr = ''
        actionId = self.tblActionList.currentItemId()
        if actionId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            record = db.getRecordEx(tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id'])), [tableActionType['name'], tableAction['specifiedName'], tableAction['aliquoticity'], tableAction['event_id'], tableAction['begDate'], tableAction['actionType_id']], [tableAction['id'].eq(actionId), tableAction['deleted'].eq(0), tableActionType['deleted'].eq(0)])
            if record:
                eventId = forceRef(record.value('event_id'))
                begDate = forceDate(record.value('begDate'))
                actionTypeId = forceRef(record.value('actionType_id'))
                name = forceString(record.value('name'))
                specifiedName = forceString(record.value('specifiedName'))
                actionTypeName = name + (' ' + specifiedName if specifiedName else '')
                if eventId:
                    actionCount = db.getDistinctCount(tableAction, 'Action.id', [tableAction['event_id'].eq(eventId), tableAction['actionType_id'].eq(actionTypeId), tableAction['deleted'].eq(0), tableAction['begDate'].dateEq(begDate)])
                    actionCountStr = '<b>[%s]</b> '%(forceString(actionCount))
        self.lblActionTypeName.setText(actionCountStr + actionTypeName)


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblPresence_clicked(self, index):
        selectedRows = []
        rowCount = self.tblPresence.model().rowCount()
        for index in self.tblPresence.selectedIndexes():
            if index.row() < rowCount:
                row = index.row()
                if row not in selectedRows:
                    selectedRows.append(row)
        if len(selectedRows) > 1:
            self.notSelectedRows = False
            self.setActionsIdList([], None)
        else:
            self.notSelectedRows = True
            self.updateActionsList({}, [self.getCurrentEventId(1)])


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
        self.lblActionsStatusCount.setText(formatRecordsCount(count))


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
    def on_tblActionList_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsStatus_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()
        self.on_buttonBoxAction_apply()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsDiagnostic_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()
        self.on_buttonBoxAction_apply()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsCure_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()
        self.on_buttonBoxAction_apply()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsMisc_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()
        self.on_buttonBoxAction_apply()


    @QtCore.pyqtSlot(int)
    def on_cmbFilterActionType_currentIndexChanged(self, index):
        index = self.tabWidgetActionsClasses.currentIndex()-1
        if index > -1:
            self.__actionTypeIdListByClassPage[index] = self.cmbFilterActionType.value()

    @QtCore.pyqtSlot()
    def on_btnProcessingReferral_clicked(self):
        row = self.tblQueue.currentRow()
        if row:
            dialog = CProcessingReferralWindow(self)
            if dialog.exec_():
                if len(dialog.edtStatus.text()):
                    if self.tblQueue.model().items[row]['recid']:
                        try:
                            #TODO: i3014. Отправка данных об обработанном направлении
                            from Exchange.TFOMSExchange.DCExchangeSrv_client import DCExchangeSrvLocator, SendTryAssertReservedBed
                            from Exchange.TFOMSExchange.DCExchangeSrv_types import ns1
                            from Events.ReferralPage import getPackageInformation
                            from Exchange.TFOMSExchange.config import userName, password, senderCode
                            loc = DCExchangeSrvLocator()
                            port = loc.getDCExchangeSrvPort()
                            msg = SendTryAssertReservedBed()
                            msg._username = userName
                            msg._password = password
                            msg._sendercode = senderCode
                            msg._yearcode = QtCore.QDate.year(QtCore.QDate.currentDate())
                            msg._monthcode = QtCore.QDate.month(QtCore.QDate.currentDate())

                            msg._orderpack = ns1.cAssertReservedBedPackage_Def("_orderpack")
                            msg._orderpack._p10_packinf = getPackageInformation('_p10_packinf')
                            msg._orderpack._p11_abl = ns1.cAssertReservedBedList_Def("_p11_abl")
                            msg._orderpack._p11_abl._r10_abr = ns1.cAssertReservedBed_Def("_r10_abr")
                            msg._orderpack._p11_abl._r10_abr._p10_recid = self.tblQueue.model().items[row]['recid']
                            msg._orderpack._p11_abl._r10_abr._p11_brdt = ns1.cBedAssertDetail_Def("_p11_brdt")
                            msg._orderpack._p11_abl._r10_abr._p12_nzap = 0 # ???
                            msg._orderpack._p11_abl._r10_abr._p11_brdt._a10_stcd = int(dialog.edtStatus.text())

                            msg._orderpack._p11_abl._r10_abr._p11_brdt._a11_hsdt = dialog.edtDate.text()#.toString('yyyy-MM-dd')

                            response = port.SendTryAssertReservedBed(msg)
                            if response:
                                QtGui.QMessageBox.information(self, u'Ошибка',
                                                              response._orderpack._r11_rsinf._responceMessage.decode(
                                                                  u'UTF-8'), QtGui.QMessageBox.Ok)
                                for v in response._orderpack._r12_orerl._f10_orflker:
                                    errStr = ''
                                    for k in v._f11_flkerrorList._f10_flkerror:
                                        errStr += k._e11_ems + '\n'
                                    if errStr:
                                        QtGui.QMessageBox.information(self, u'Ошибка', errStr.decode(u'UTF-8'),
                                                                      QtGui.QMessageBox.Ok)
                        except Exception as error:
                            QtGui.QMessageBox.information(
                                self,
                                u"Обработка направления",
                                u"Ошибка: %s" % error.str,
                                QtGui.QMessageBox.Ok,
                                QtGui.QMessageBox.Ok
                            )

        else:
            QtGui.QMessageBox.information(
                self,
                u"Обработка направления",
                u"Для того чтобы обработать направления сперва выберете нужную строку в таблице.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )
        pass

    def focusActions(self, actionId=None, newActionId=None):
        currentActionsTable = self.getCurrentActionsTable()
        if not actionId and not newActionId:
            currentActionsTable.setFocus(QtCore.Qt.TabFocusReason)
        elif newActionId:
            currentActionsTable.setCurrentItemId(newActionId)
        elif actionId:
            currentActionsTable.setCurrentItemId(actionId)


    def on_btnActionEdit_clicked(self):
        actionId = self.getCurrentActionsTable().currentItemId()
        if actionId:
            newActionId = self.editAction(actionId)[1]
            self.updateActionsList({}, [self.getCurrentEventId(1)])
        self.focusActions(actionId, newActionId)


    def editAction(self, actionId):
        dialog = CActionEditDialog(self)
        dialog.load(actionId)
        if dialog.exec_():
            filters = {}
            actionType = self.cmbFilterActionType.value()
            if actionType:
                filters['actionTypeId'] = actionType
            filters['status'] = self.cmbFilterActionStatus.currentIndex()
            filters['isUrgent'] = self.chkFilterIsUrgent.isChecked()
            filters['begDatePlan'] = self.edtFilterBegDatePlan.date()
            filters['endDatePlan'] = self.edtFilterEndDatePlan.date()
            self.updateActionsList(filters, self.modelPresence.eventIdList if self.tabWidgetActionsClasses.currentIndex()!= 0 else [self.getCurrentEventId(1)])
            return (dialog.itemId(), dialog.newActionId)
        else:
            self.updateActionInfo(actionId)
            self.updateClientsListRequest = True
        return (None, dialog.newActionId)


    def updateActionInfo(self, actionId):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        table = tableAction.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        record = db.getRecord(table,
                              ['Action.createDatetime','Action.createPerson_id', 'Action.modifyDatetime', 'Action.modifyPerson_id', 'Event.client_id', 'Action.payStatus', 'Action.note'], actionId)
        clientId       = forceRef(record.value('client_id')) if record else None

        if not clientId:
            clientId = self.currentClientId()
        QtGui.qApp.setCurrentClientId(clientId)


    def dateTimeToString(self, value):
        return  value.toString('dd.MM.yyyy hh:mm:ss')


    def currentClientId(self):
        return QtGui.qApp.currentClientId()


    def addEqCond(self, cond, table, fieldName, filters, name):
        if name in filters:
            cond.append(table[fieldName].eq(filters[name]))


    def getCurrentWidgetRowCount(self, widgetIndex):
        if widgetIndex == self.tabWidget.indexOf(self.tabLobby):
            return self.modelHospitalBeds.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabPresence):
            return self.modelPresence.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabReceived):
            return self.modelReceived.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabTransfer):
            return self.modelTransfer.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabLeaved):
            return self.modelLeaved.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabReabyToLeave):
            return self.modelReabyToLeave.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabQueue):
            return self.modelQueue.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabRenunciation):
            return self.modelRenunciation.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabDeath):
            return self.modelDeath.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabReanimation):
            return self.modelReanimation.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabLobby):
            return self.modelLobby.rowCount()
        elif widgetIndex == self.tabWidget.indexOf(self.tabMaternityward):
            return self.modelMaternityward.rowCount()
        return 0


class CHospitalBedsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent,  [
            CTextCol(u'Код',            ['code'], 10),
            CBoolCol(u'Штат',           ['isPermanent'], 10),
            CRefBookCol(u'Тип',         ['type_id'], 'rbHospitalBedType', 10),
            CRefBookCol(u'Профиль',     ['profile_id'], 'rbHospitalBedProfile', 10),
            CNumCol(u'Смены',           ['relief'], 6),
            CRefBookCol(u'Режим',       ['schedule_id'], 'rbHospitalBedShedule', 15),
            CDateCol(u'Начало',         ['begDate'], 20),
            CDateCol(u'Окончание',      ['endDate'], 20),
#            CEnumCol(u'Причина сворачивания', ['involution'], [u'нет сворачивания', u'ремонт', u'карантин'], 16),
#            CDateCol(u'Начало сворачивания', ['begDateInvolute'], 20),
#            CDateCol(u'Окончание сворачивания', ['endDateInvolute'], 20),
            CDesignationCol(u'Подразделение', ['master_id', 'isBusy'], ('OrgStructure', 'name'), 8),
            CTextCol(u'Наименование',   ['name'], 20),
            CTextCol(u'Возраст',        ['age'], 10),
            CEnumCol(u'Пол',            ['sex'], ['', u'М', u'Ж'], 10),
            ], 'vHospitalBed' )


    def isBusy(self, index):
        record = self.getRecordByRow(index.row())
        return forceBool(record.value('isBusy'))


    def data(self, index, role):
        if role == QtCore.Qt.BackgroundColorRole:
            record = self.getRecordByRow(index.row())
            if forceBool(record.value('isBusy')):
                return toVariant(QtGui.QColor(200, 230, 240))
            else:
                return QtCore.QVariant()
        else:
            return CTableModel.data(self, index, role)


class CInvoluteBedsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'HospitalBed_Involute', 'id', 'master_id', parent)
        self.addCol(CEnumInDocTableCol(u'Причина сворачивания', 'involuteType', 16, [u'нет сворачивания', u'ремонт', u'карантин'])).setReadOnly()
        self.addCol(CDateInDocTableCol(u'Начало сворачивания', 'begDateInvolute', 20, canBeEmpty=True)).setReadOnly()
        self.addCol(CDateInDocTableCol(u'Окончание сворачивания', 'endDateInvolute', 20, canBeEmpty=True)).setReadOnly()


# Присутствуют - Статус/Диагностика/Лечение/Мероприятия - 1
class CAttendanceActionsTableModel(CTableModel):

    class CLocClientColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')

        def formatShortNameInt(self, lastName, firstName, patrName):
            return forceStringEx(lastName + ' ' +((firstName[:1]) if firstName else '') + ((patrName[:1]) if patrName else ''))

        def format(self, values):
            val = values[0]
            eventId  = forceRef(val)
            if eventId:
                db = QtGui.qApp.db
                tableEvent = db.table('Event')
                tableClient = db.table('Client')
                table = tableEvent.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))

                clientRecord = db.getRecordEx(table, [tableClient['lastName'], tableClient['firstName'], tableClient['patrName']], [tableEvent['deleted'].eq(0), tableClient['deleted'].eq(0), tableEvent['id'].eq(eventId)])
                if clientRecord:
                    name  = self.formatShortNameInt(forceString(clientRecord.value('lastName')),
                                                    forceString(clientRecord.value('firstName')),
                                                    forceString(clientRecord.value('patrName')))
                    return toVariant(name)
                return CCol.invalid
            return CCol.invalid

    class CLocClientIdentifierColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            self.identifiersCache = CRecordCache()


        def getClientIdentifier(self, clientId):
            identifier = self.identifiersCache.get(clientId)
            if identifier is None:
                accountingSystemId = QtGui.qApp.defaultAccountingSystemId()
                if accountingSystemId is None:
                    identifier = clientId
                else:
                    db = QtGui.qApp.db
                    tableClientIdentification = db.table('ClientIdentification')
                    cond = [tableClientIdentification['client_id'].eq(clientId),
                            tableClientIdentification['accountingSystem_id'].eq(accountingSystemId)]
                    record = db.getRecordEx(tableClientIdentification, tableClientIdentification['identifier'], cond)
                    identifier = forceString(record.value(0)) if record else ''
                self.identifiersCache.put(clientId, identifier)
            return identifier


        def format(self, values):
            val = values[0]
            eventId = forceRef(val)
            if eventId:
                db = QtGui.qApp.db
                table = db.table('Event')
                clientRecord = db.getRecordEx(table, [table['client_id'], table['externalId']], [table['deleted'].eq(0), table['id'].eq(eventId)])
                if clientRecord:
                    clientId = forceRef(clientRecord.value('client_id'))
                    externalId = forceString(clientRecord.value('externalId'))
                    return toVariant(forceString(self.getClientIdentifier(clientId)) + (u', карта %s'%(externalId) if externalId else u''))
            return CCol.invalid


    class CLocClientBirthDateColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')


        def format(self, values):
            val = values[0]
            eventId  = forceRef(val)
            if eventId:
                db = QtGui.qApp.db
                tableEvent = db.table('Event')
                tableClient = db.table('Client')
                table = tableEvent.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                clientRecord = db.getRecordEx(table, [tableClient['birthDate']], [tableEvent['deleted'].eq(0), tableClient['deleted'].eq(0), tableEvent['id'].eq(eventId)])
                if clientRecord:
                    return toVariant(forceString(clientRecord.value('birthDate')))
            return CCol.invalid


    class CLocClientSexColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')


        def format(self, values):
            val = values[0]
            eventId  = forceRef(val)
            if eventId:
                db = QtGui.qApp.db
                tableEvent = db.table('Event')
                tableClient = db.table('Client')
                table = tableEvent.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                clientRecord = db.getRecordEx(table, [tableClient['sex']], [tableEvent['deleted'].eq(0), tableClient['deleted'].eq(0), tableEvent['id'].eq(eventId)])
                if clientRecord:
                    return toVariant([u'', u'М', u'Ж'][forceInt(clientRecord.value('sex'))])
            return CCol.invalid


    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.clientCol   = CAttendanceActionsTableModel.CLocClientColumn( u'Ф.И.О.', ['event_id'], 60)
        self.clientIdentifierCol = CAttendanceActionsTableModel.CLocClientIdentifierColumn(u'Идентификатор', ['event_id'], 30)
        self.clientBirthDateCol = CAttendanceActionsTableModel.CLocClientBirthDateColumn(u'Дата рожд.', ['event_id'], 20)
        self.clientSexCol = CAttendanceActionsTableModel.CLocClientSexColumn(u'Пол', ['event_id'], 5)
        self.addColumn(CDateCol(u'Назначено',      ['directionDate'], 15))
        self.addColumn(CActionTypeCol(u'Действие', 15))
        self.addColumn(CBoolCol(u'Срочно',         ['isUrgent'],      15))
        self.addColumn(CIntCol(u'Д',               ['duration'],      15))
        self.addColumn(CIntCol(u'И',               ['periodicity'],   15))
        self.addColumn(CIntCol(u'К',               ['aliquoticity'],  15))
        self.addColumn(CEnumCol(u'Состояние',      ['status'], CActionType.retranslateClass(False).statusNames, 4))
        self.addColumn(CDateTimeFixedCol(u'Начато',     ['begDate'],       15))
        self.addColumn(CDateTimeFixedCol(u'Окончено',   ['endDate'],       15))
        self.addColumn(CDateCol(u'План',           ['plannedEndDate'],15))
        self.addColumn(CRefBookCol(u'Назначил',    ['setPerson_id'], 'vrbPersonWithSpeciality', 20))
        self.addColumn(CRefBookCol(u'Выполнил',    ['person_id'],    'vrbPersonWithSpeciality', 20))
        self.addColumn(CTextCol(u'Каб',            ['office'],                                6))
        self.addColumn(CTextCol(u'Примечания',     ['note'],                                  6))
        self.setTable('Action')


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                actionId = self._idList[section]
                self._recordsCache.weakFetch(actionId, self._idList[max(0, section-self.fetchSize):(section+self.fetchSize)])
                record = self._recordsCache.get(actionId)
                clientValues   = self.clientCol.extractValuesFromRecord(record)
                clientValue = forceString(self.clientCol.format(clientValues))
                clientIdentifier = ''
                clientIdentifierValues = self.clientIdentifierCol.extractValuesFromRecord(record)
                clientIdentifier = forceString(self.clientIdentifierCol.format(clientIdentifierValues))
                clientBirthDateValues = self.clientBirthDateCol.extractValuesFromRecord(record)
                clientBirthDate = forceString(self.clientBirthDateCol.format(clientBirthDateValues))
                clientSexValues = self.clientSexCol.extractValuesFromRecord(record)
                clientSex = forceString(self.clientSexCol.format(clientSexValues))
                clientFIOSex = u', '.join([clientValue, clientSex])
                birthDateSex = u', '.join([clientIdentifier, clientBirthDate])
                result =  u'\n'.join([clientFIOSex, birthDateSex])
                return QtCore.QVariant(result)
        return CTableModel.headerData(self, section, orientation, role)


    def flags(self, index):
        enabled = True
        if enabled:
            return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsSelectable


    def setTable(self, tableName):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        loadFields = []
        loadFields.append(u'''Client.id AS clientId, CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS FIO, Client.birthDate, Client.sex, Action.id, Action.event_id, Action.directionDate, Action.isUrgent, Action.plannedEndDate, Action.begDate, Action.endDate, Action.actionType_id, Action.status, Action.setPerson_id, Action.person_id, Action.office, Action.note, Action.specifiedName, Action.duration, Action.periodicity, Action.aliquoticity''')
        queryTable = tableAction.leftJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        self._table = queryTable
        self._recordsCache = CTableRecordCache(db, self._table, loadFields)

# Присутствуют - Список - 2
class CHospitalActionsTableModel(CAttendanceActionsTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CDateCol(u'Назначено',      ['directionDate'], 15))
        self.addColumn(CActionTypeCol(u'Действие', 15))
        self.addColumn(CBoolCol(u'Срочно',         ['isUrgent'],      15))
        self.addColumn(CIntCol(u'Д',               ['duration'],      15))
        self.addColumn(CIntCol(u'И',               ['periodicity'],   15))
        self.addColumn(CIntCol(u'К',               ['aliquoticity'],  15))
        self.addColumn(CEnumCol(u'Состояние',      ['status'], CActionType.retranslateClass(False).statusNames, 4))
        self.addColumn(CDateTimeFixedCol(u'Начато',     ['begDate'],       15))
        self.addColumn(CDateTimeFixedCol(u'Окончено',   ['endDate'],       15))
        self.addColumn(CDateCol(u'План',           ['plannedEndDate'],15))
        self.addColumn(CRefBookCol(u'Назначил',    ['setPerson_id'], 'vrbPersonWithSpeciality', 20))
        self.addColumn(CRefBookCol(u'Выполнил',    ['person_id'],    'vrbPersonWithSpeciality', 20))
        self.addColumn(CTextCol(u'Каб',            ['office'],                                6))
        self.addColumn(CTextCol(u'Примечания',     ['note'],                                  6))
        self.addColumn(CTextCol(u'Ф.И.О.', ['FIO'], 60))
        self.addColumn(CDateCol(u'Дата рожд.', ['birthDate'], 20, highlightRedDate=False))
        self.addColumn(CEnumCol(u'Пол', ['sex'], ['', u'М', u'Ж'], 5))
        self.setTable('Action')


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.ToolTipRole:
                if section == 3:
                    return QtCore.QVariant(u'Длительность курса лечения в днях.')
                elif section == 4:
                    return QtCore.QVariant(u'''Интервал: 0 - каждый день,
                                        1 - через 1 день,
                                        2 - через 2 дня,
                                        3 - через 3 дня,
                                        и т.д.''')
                elif section == 5:
                    return QtCore.QVariant(u'Сколько раз в сутки.')
        return CAttendanceActionsTableModel.headerData(self, section, orientation, role)

    #def data(self, index, role=QtCore.Qt.DisplayRole):
    #    if not index.isValid():
    #        return QtCore.QVariant()
    #    column = index.column()
    #    row = index.row()
    #    color = self.unconsciousPatientRowColor
    #    if role == QtCore.Qt.DisplayRole:  ### or role == Qt.EditRole:
    #        (col, values) = self.getRecordValues(column, row)
    #        col.color = color if self.getUnconsciousStatusByEvent(forceRef(self.getRecordByRow(row).value('event_id'))) else None
    #        return col.format(values)
    #    elif role == QtCore.Qt.TextAlignmentRole:
    #        col = self._cols[column]
    #        return col.alignment()
    #    elif role == QtCore.Qt.CheckStateRole:
    #        (col, values) = self.getRecordValues(column, row)
    #        col.color = color if self.getUnconsciousStatusByEvent(forceRef(self.getRecordByRow(row).value('event_id'))) else None
    #        return col.checked(values)
    #    elif role == QtCore.Qt.ForegroundRole:
    #        (col, values) = self.getRecordValues(column, row)
    #        col.color = color if self.getUnconsciousStatusByEvent(forceRef(self.getRecordByRow(row).value('event_id'))) else None
    #        return col.getForegroundColor(values)
    #    elif role == QtCore.Qt.BackgroundRole:
    #        (col, values) = self.getRecordValues(column, row)
    #        col.color = color if self.getUnconsciousStatusByEvent(forceRef(self.getRecordByRow(row).value('event_id'))) else None
    #        return col.getBackgroundColor(values)
    #    elif role == QtCore.Qt.ToolTipRole:
    #        if column == 11 or column == 12:
    #            (col, values) = self.getRecordValues(column, row)
    #            col.color = color if self.getUnconsciousStatusByEvent(forceRef(self.getRecordByRow(row).value('event_id'))) else None
    #            return col.getCodeNameToolTip(values)
    #    return QtCore.QVariant()

class CReportF001SetupDialog(QtGui.QDialog, Ui_ReportF001SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)


    def setParams(self, params):
        self.chkClientId.setChecked(params.get('chkClientId', True))
        self.chkEventId.setChecked(params.get('chkEventId', False))
        self.chkExternalEventId.setChecked(params.get('chkExternalEventId', False))
        self.chkPrintTypeEvent.setChecked(params.get('chkPrintTypeEvent', False))
        self.cmbCondSort.setCurrentIndex(params.get('condSort', 0))
        self.cmbCondOrgStructure.setCurrentIndex(params.get('condOrgStructure', 0))
        self.cmbPrintTypeMKB.setCurrentIndex(params.get('printTypeMKB', 0))


    def params(self):
        result = {}
        result['chkClientId'] = self.chkClientId.isChecked()
        result['chkEventId'] = self.chkEventId.isChecked()
        result['chkExternalEventId'] = self.chkExternalEventId.isChecked()
        result['chkPrintTypeEvent'] = self.chkPrintTypeEvent.isChecked()
        result['condSort'] = self.cmbCondSort.currentIndex()
        result['condOrgStructure'] = self.cmbCondOrgStructure.currentIndex()
        result['printTypeMKB'] = self.cmbPrintTypeMKB.currentIndex()
        return result

class CReportLogbookHospitalizationSetupDialog(QtGui.QDialog, Ui_ReportLogbookHospitalizationSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbResult.setTable('rbResult', True)

    def setParams(self, params):
        self.edtDiapFrom.setText(params.get('edtDiapFrom', ''))
        self.edtDiapTo.setText(params.get('edtDiapTo', ''))
        self.edtPrefix.setText(params.get('edtPrefix', ''))
        self.cmbContract.setPath(params.get('contractPath', u''))
        self.cmbResult.setValue(params.get('cmbResult', 0))

    def params(self):
        result = {}
        result['edtDiapFrom'] = self.edtDiapFrom.text()
        result['edtDiapTo'] = self.edtDiapTo.text()
        result['edtPrefix'] = self.edtPrefix.text()
        result['contractIdList'] = self.cmbContract.getIdList()
        result['contractPath'] = self.cmbContract.getPath()
        result['cmbResult'] = self.cmbResult.value()
        return result


